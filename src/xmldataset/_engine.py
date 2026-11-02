"""The streaming extraction engine.

The XML is read as a stream of start/end events in document order. Each element
is discarded once it ends, and each record is released as soon as nothing can
change it any more, so memory stays bounded by the depth of the document and the
number of records that are still waiting for a value.

Record rules (documented for users in docs/profiles.md):

1. A value belongs to the element its field is written under; an attribute
   belongs to its element.
2. A record never combines values from two occurrences of the same element.
   A value from a new occurrence, or for a field the record already has, starts
   a new record.
3. Values from enclosing elements are copied into every record beneath them,
   including values that appear after those records in the document.
4. ``__NEW_DATASET__`` makes an element the record boundary for a dataset;
   elements below it no longer split records.
5. Records are created only when a value is written, so there are no empty rows.
"""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from collections import deque
from collections.abc import Callable, Iterator, Mapping
from functools import lru_cache
from typing import Any

from ._errors import ConfigurationError, MissingProcessError, ProfileError
from ._model import ExternalValue, Field, Node, Profile

__all__ = ["Engine", "check_references", "compile_runtime", "iter_events"]

XML_NAMESPACE = "http://www.w3.org/XML/1998/namespace"
CHUNK_SIZE = 1 << 16
DOCUMENT = 0  # occurrence id for scopes that span the whole document
RECORD_ELEMENT = -1  # pseudo node id: the __NEW_DATASET__ element a record belongs to

OccPath = tuple[tuple[int, int], ...]  # ((profile node id, occurrence id), ...)
ExternalKey = tuple[str, str]  # (external dataset, field name)
ContextValue = tuple[Any, "OccPath", bool, "tuple[ExternalKey, int] | None"]


class RNode:
    """A profile node prepared for matching."""

    __slots__ = (
        "always_follow",
        "block",
        "children",
        "default_children",
        "depth",
        "exact",
        "external_values",
        "fields",
        "has_default",
        "hold_datasets",
        "id",
        "ignore",
        "key",
        "local",
        "name",
        "outputs",
        "parent",
        "processing",
        "resets",
        "scope_keys",
    )

    def __init__(self, node: Node | None, node_id: int, parent: RNode | None) -> None:
        self.id = node_id
        self.name = node.name if node else ""
        self.parent = parent
        self.depth: int = parent.depth + 1 if parent else 0
        self.ignore = node.ignore if node else False
        # An element with its own block in the profile (attributes or children
        # listed under it) owns its text, just as it owns its attributes.
        self.block = bool(node.children) if node else True
        self.fields: tuple[Field, ...] = node.fields if node else ()
        self.has_default = any(f.default is not None for f in self.fields)
        self.external_values = node.external_values if node else ()
        self.resets = node.reset_external_values if node else ()
        self.processing = node.dataset_processing if node else ()
        self.key = self.name  # resolved below for prefixed names
        self.outputs = [
            (f, (f.prefix or "") + (f.name or self.name)) for f in self.fields
        ]
        self.children: list[RNode] = []  # not ignored, in profile order
        self.exact: dict[str, RNode] = {}  # includes ignored children
        self.local: dict[str, RNode] = {}
        self.always_follow: set[int] = set()
        self.default_children: list[RNode] = []
        self.hold_datasets: tuple[str, ...] = ()
        self.scope_keys: tuple[ExternalKey, ...] = ()

    def lookup(self, tag: str) -> RNode | None:
        """The child matching an element or attribute name, preferring exact
        names to unprefixed names that match the local name in any namespace."""
        node = self.exact.get(tag)
        if node is None and tag[:1] == "{":
            node = self.local.get(tag[tag.find("}") + 1 :])
        return node

    def text_owner(self) -> RNode:
        """The element a value of this node's own text belongs to (rule 1)."""
        if self.block or self.parent is None:
            return self
        return self.parent


def _location(node: RNode) -> str:
    names = []
    cur: RNode | None = node
    while cur is not None and cur.parent is not None:
        names.append(cur.name)
        cur = cur.parent
    return " > ".join(reversed(names))


def check_references(profile: Profile) -> None:
    """Directives must refer to datasets and external values the profile produces.

    Raises:
        ProfileError: A directive names something nothing produces, which is
            almost always a typo.
    """
    datasets: set[str] = set()
    externals: set[ExternalKey] = set()
    pending: list[tuple[list[str], Node]] = [([n.name], n) for n in profile.roots]
    nodes: list[tuple[list[str], Node]] = []
    while pending:
        names, node = pending.pop()
        if node.ignore:
            continue
        nodes.append((names, node))
        for spec in node.fields:
            out = (spec.prefix or "") + (spec.name or node.name)
            if spec.dataset is not None:
                datasets.add(spec.dataset)
            if spec.external_dataset is not None:
                externals.add((spec.external_dataset, out))
        datasets.update(ext.dataset for ext in node.external_values)
        pending.extend(([*names, child.name], child) for child in node.children)
    for names, node in nodes:
        where = " > ".join(names)
        for dataset in node.new_dataset:
            if dataset not in datasets:
                raise ProfileError(
                    f"__NEW_DATASET__ names {dataset!r},"
                    " which no field sends values to",
                    location=where,
                )
        for proc in node.dataset_processing:
            if proc.dataset not in datasets:
                raise ProfileError(
                    f"__DATASET_PROCESSING__ names dataset {proc.dataset!r},"
                    " which no field sends values to",
                    location=where,
                )
        for directive, items in (
            ("__EXTERNAL_VALUE__", node.external_values),
            ("__NEW_EXTERNAL_VALUE_HOLDER__", node.reset_external_values),
        ):
            for item in items:
                if (item.external_dataset, item.field) not in externals:
                    raise ProfileError(
                        f"{directive}: nothing captures {item.field!r} into external"
                        f" dataset {item.external_dataset!r}",
                        location=where,
                    )


class Runtime:
    """A profile compiled for the engine (cached per profile and namespaces)."""

    def __init__(self, profile: Profile, namespaces: Mapping[str, str]) -> None:
        check_references(profile)
        self.nodes: list[RNode] = []
        self.root = self._add(None, None)
        # Build iteratively: profiles may be deeper than the recursion limit.
        pending: list[tuple[Node, RNode]] = [
            (node, self.root) for node in profile.roots
        ]
        built: list[tuple[Node, RNode]] = []
        while pending:
            node, parent = pending.pop(0)
            rnode = self._add(node, parent)
            if node.ignore:
                # Indexed only so it shadows local-name matches. A prefix with no
                # URI cannot match anything, so it needs no namespace either.
                prefix = node.name.split(":", 1)[0] if ":" in node.name else None
                if (
                    prefix is None
                    or node.name.startswith("{")
                    or prefix in namespaces
                    or prefix == "xml"
                ):
                    self._index(parent, rnode, namespaces)
                continue
            self._index(parent, rnode, namespaces)
            built.append((node, rnode))
            parent.children.append(rnode)
            pending[:0] = [(child, rnode) for child in node.children]

        self.explicit: dict[str, set[int]] = {}
        # dataset -> enclosing node id -> fields it may still supply (holds)
        self.owner_fields: dict[str, dict[int, set[str]]] = {}
        self.owner_lists: dict[str, dict[int, set[str]]] = {}
        sources: dict[ExternalKey, list[RNode]] = {}
        consumers: dict[ExternalKey, list[RNode]] = {}
        self.processes: set[str] = set()
        for node, rnode in built:
            for dataset in node.new_dataset:
                self.explicit.setdefault(dataset, set()).add(rnode.id)
            for name in node.always_follow:
                child = next((c for c in rnode.children if c.name == name), None)
                if child is not None:
                    rnode.always_follow.add(child.id)
            owner = rnode.text_owner()
            for spec, out_name in rnode.outputs:
                if spec.process is not None:
                    self.processes.add(spec.process)
                if spec.dataset is not None:
                    self._own(spec.dataset, owner.id, out_name, spec.as_list)
                if spec.external_dataset is not None:
                    key = (spec.external_dataset, out_name)
                    sources.setdefault(key, []).append(owner)
            for ext in node.external_values:
                self._own(ext.dataset, rnode.id, ext.name or ext.field, False)
                key = (ext.external_dataset, ext.field)
                consumers.setdefault(key, []).append(rnode)
            for proc in node.dataset_processing:
                self.processes.add(proc.process)
        # dataset -> elements that can enclose its records (strict ancestors of
        # any element its values belong to); only these need rule 4 bookkeeping
        self.enclosing: dict[str, set[int]] = {}
        for dataset, owners in self.owner_fields.items():
            ancestors = self.enclosing.setdefault(dataset, set())
            for owner_id in owners:
                cur = self.nodes[owner_id].parent
                while cur is not None and cur.id not in ancestors:
                    ancestors.add(cur.id)
                    cur = cur.parent
        for rnode in self.nodes:
            rnode.default_children = [
                c
                for c in rnode.children
                if c.has_default or (c.id in rnode.always_follow and c.children)
            ]
            rnode.hold_datasets = tuple(
                ds for ds, owners in self.owner_fields.items() if rnode.id in owners
            )

        # An external value lives as long as the element enclosing both the
        # elements that capture it and the elements that use it.
        self.scope: dict[ExternalKey, int] = {}
        scope_keys: dict[int, list[ExternalKey]] = {}
        for key in sources.keys() | consumers.keys():
            ends = sources.get(key, []) + consumers.get(key, [])
            scope = _common_ancestor(ends)
            self.scope[key] = scope.id
            scope_keys.setdefault(scope.id, []).append(key)
        for node_id, keys in scope_keys.items():
            self.nodes[node_id].scope_keys = tuple(keys)

    def _add(self, node: Node | None, parent: RNode | None) -> RNode:
        rnode = RNode(node, len(self.nodes), parent)
        self.nodes.append(rnode)
        return rnode

    def _own(self, dataset: str, owner_id: int, name: str, as_list: bool) -> None:
        self.owner_fields.setdefault(dataset, {}).setdefault(owner_id, set()).add(name)
        if as_list:
            self.owner_lists.setdefault(dataset, {}).setdefault(owner_id, set()).add(
                name
            )

    @staticmethod
    def _index(parent: RNode, rnode: RNode, namespaces: Mapping[str, str]) -> None:
        name = rnode.name
        if name.startswith("{"):
            rnode.key = name
        elif ":" in name:
            prefix, local = name.split(":", 1)
            uri = namespaces.get(prefix, XML_NAMESPACE if prefix == "xml" else None)
            if uri is None:
                raise ConfigurationError(
                    f"the profile uses the namespace prefix {prefix!r} ({name!r})"
                    " but no URI was given for it;"
                    f" pass namespaces={{{prefix!r}: '...'}}"
                )
            rnode.key = f"{{{uri}}}{local}"
        else:
            parent.local.setdefault(name, rnode)
        parent.exact.setdefault(rnode.key, rnode)


def _common_ancestor(nodes: list[RNode]) -> RNode:
    chains = []
    for node in nodes:
        chain: list[RNode] = []
        cur: RNode | None = node
        while cur is not None:
            chain.append(cur)
            cur = cur.parent
        chains.append(chain[::-1])
    common = chains[0][0]
    for depth in range(min(len(c) for c in chains)):
        if all(c[depth] is chains[0][depth] for c in chains):
            common = chains[0][depth]
        else:
            break
    return common


@lru_cache(maxsize=32)
def _runtime(profile: Profile, namespaces: tuple[tuple[str, str], ...]) -> Runtime:
    return Runtime(profile, dict(namespaces))


def compile_runtime(profile: Profile, namespaces: Mapping[str, str] | None) -> Runtime:
    if namespaces is None:
        return _runtime(profile, ())
    if not isinstance(namespaces, Mapping) or not all(
        isinstance(k, str) and isinstance(v, str) for k, v in namespaces.items()
    ):
        raise ConfigurationError("namespaces must map prefixes (str) to URIs (str)")
    return _runtime(profile, tuple(sorted(namespaces.items())))


class Record:
    __slots__ = (
        "data",
        "dataset",
        "emitted",
        "inside",
        "occ",
        "paths",
        "pending",
        "real",
        "seen",
        "seq",
    )

    def __init__(self, dataset: str, data: dict[str, Any]) -> None:
        self.dataset = dataset
        self.data = data
        self.occ: dict[int, int] = {}  # node id -> occurrence id, for boundaries
        self.paths: dict[str, OccPath] = {}  # field -> the element its value is from
        self.pending: dict[str, tuple[ExternalKey, int]] = {}
        self.real = 0  # values written from the document (not inherited)
        # Element occurrences its own values came from or from inside (seen), and
        # those strictly enclosing them (inside), whose values it shares (rule 4).
        self.seen: dict[int, int] = {}
        self.inside: dict[int, int] = {}
        self.seq = 0  # when it was last written
        self.emitted = False


class Frame:
    __slots__ = ("base", "elem", "flushed", "matched", "node", "occ", "path", "seq")

    def __init__(self, node: RNode | None, elem: Any, base: OccPath, occ: int) -> None:
        self.seq = 0  # the engine's write counter when the element started
        self.node = node
        self.elem = elem
        self.base = base  # path of the parent element
        self.path: OccPath = (*base, (node.id, occ)) if node is not None else ()
        self.occ = occ
        self.flushed = False
        # Children seen as attributes or elements; only tracked for defaults.
        self.matched: set[int] | None = (
            set() if node and node.default_children else None
        )


class Engine:
    """Turns start/end events into finished ``(dataset, record)`` pairs."""

    def __init__(
        self,
        runtime: Runtime,
        process: Mapping[str, Callable[[Any], Any]] | None,
        global_values: Mapping[str, Any] | None,
    ) -> None:
        if process is not None and not isinstance(process, Mapping):
            raise ConfigurationError("process must map names to functions")
        if runtime.processes:
            if process is None:
                raise MissingProcessError("process definition not supplied as argument")
            for name in sorted(runtime.processes):
                if name not in process:
                    raise MissingProcessError(f"process coderef {name} missing")
                if not callable(process[name]):
                    raise ConfigurationError(f"process {name!r} is not callable")
        if global_values is not None and not isinstance(global_values, Mapping):
            raise ConfigurationError("global_values must be a mapping")
        self.rt = runtime
        self.depth = [node.depth for node in runtime.nodes]
        self.process = dict(process or {})
        self.global_values = dict(global_values or {})
        self.stack: list[Frame] = []
        self.next_occ = DOCUMENT
        self.open_occ: set[int] = set()
        self.queues: dict[str, deque[Record]] = {}
        self.latest: dict[str, Record] = {}
        self.order: dict[str, None] = {}  # datasets in order of their first record
        self.externals: dict[ExternalKey, tuple[int, Any]] = {}
        self.waiting: dict[ExternalKey, list[tuple[Record, str, int]]] = {}
        # occurrence -> dataset -> field -> (value, path, as_list, pending): the
        # latest values belonging to each open element, shared by records inside it
        self.context: dict[int, dict[str, dict[str, ContextValue]]] = {}
        self.seq = 0
        self.out: deque[tuple[str, dict[str, Any]]] = deque()

    # --- events -------------------------------------------------------------

    def start(self, elem: Any) -> None:
        stack = self.stack
        if stack:
            parent = stack[-1]
            pnode = parent.node
            if pnode is None:
                stack.append(Frame(None, elem, (), -1))
                return
            if not parent.flushed:
                self._flush(parent)
            tag = elem.tag
            node = pnode.exact.get(tag)
            if node is None and tag[:1] == "{":
                node = pnode.local.get(tag[tag.find("}") + 1 :])
            if node is None or node.ignore:
                stack.append(Frame(None, elem, (), -1))
                return
            if parent.matched is not None:
                parent.matched.add(node.id)
            base = parent.path
        else:
            node = self.rt.root.lookup(elem.tag)
            if node is None or node.ignore:
                stack.append(Frame(None, elem, (), -1))
                return
            base = ()
        self.next_occ += 1
        occ = self.next_occ
        self.open_occ.add(occ)
        frame = Frame(node, elem, base, occ)
        frame.seq = self.seq
        stack.append(frame)
        for reset in node.resets:
            self._reset_external((reset.external_dataset, reset.field))

    def end(self, elem: Any) -> None:
        frame = self.stack.pop()
        node = frame.node
        if node is None:
            return
        if not frame.flushed:
            self._flush(frame)
        if frame.matched is not None:
            for child in node.default_children:
                if child.id not in frame.matched:
                    self._defaults(child, frame.path, node)
        for ext in node.external_values:
            self._forward(ext, frame.path)
        for proc in node.processing:
            current = self.latest.get(proc.dataset)
            # Only a record written to while this element was open is "its" record.
            if current is not None and current.seq > frame.seq:
                self.process[proc.process](current.data)
        self._close(frame.occ, node)

    def finish(self) -> None:
        for key in list(self.waiting):
            self._resolve_missing(key, None)
        self.latest.clear()
        for dataset in list(self.queues):
            self._drain(dataset)

    # --- capturing ----------------------------------------------------------

    def _flush(self, frame: Frame) -> None:
        """Capture an element's own text and attributes (before its children)."""
        frame.flushed = True
        node = frame.node
        assert node is not None
        elem = frame.elem
        if node.fields:
            path = frame.path if node.block else frame.base
            for spec, name in node.outputs:
                self._capture(spec, name, elem.text, path)
        attrib = elem.attrib
        if attrib and node.children:
            for key, value in attrib.items():
                child = node.lookup(key)
                if child is None or child.ignore:
                    continue
                if frame.matched is not None:
                    frame.matched.add(child.id)
                for spec, name in child.outputs:
                    self._capture(spec, name, value, frame.path)

    def _defaults(self, child: RNode, path: OccPath, parent: RNode) -> None:
        """Apply defaults for ``child``, which is missing from its parent."""
        stand_in: OccPath | None = None
        if child.block or child.id in parent.always_follow:
            self.next_occ += 1  # a stand-in occurrence for the missing element
            stand_in = (*path, (child.id, self.next_occ))
        if child.has_default:
            own = stand_in if child.block and stand_in is not None else path
            for spec, name in child.outputs:
                if spec.default is not None:
                    self._capture(spec, name, spec.default, own)
        if child.id in parent.always_follow and stand_in is not None:
            for grandchild in child.children:
                if grandchild.has_default or (
                    grandchild.id in child.always_follow and grandchild.children
                ):
                    self._defaults(grandchild, stand_in, child)

    def _capture(self, spec: Field, name: str, value: Any, path: OccPath) -> None:
        if spec.process is not None:
            value = self.process[spec.process](value)
        if spec.dataset is not None:
            self._write(spec.dataset, name, value, path, as_list=spec.as_list)
        if spec.external_dataset is not None:
            self._store_external((spec.external_dataset, name), value, path)

    # --- external values ----------------------------------------------------

    def _scope_occ(self, key: ExternalKey, path: OccPath) -> int:
        scope = self.rt.scope.get(key, 0)
        for node_id, occ in path:
            if node_id == scope:
                return occ
        return DOCUMENT

    def _store_external(self, key: ExternalKey, value: Any, path: OccPath) -> None:
        scope = self._scope_occ(key, path)
        self.externals[key] = (scope, value)
        waiters = self.waiting.get(key)
        if not waiters:
            return
        keep, touched = [], set()
        for record, name, waiter_scope in waiters:
            if waiter_scope != scope or name not in record.pending:
                keep.append((record, name, waiter_scope))
                continue
            assert not record.emitted, "a released record received a value"
            del record.pending[name]
            record.data[name] = value
            touched.add(record.dataset)
        self.waiting[key] = keep
        for dataset in touched:
            self._drain(dataset)

    def _forward(self, ext: ExternalValue, path: OccPath) -> None:
        key = (ext.external_dataset, ext.field)
        name = ext.name or ext.field
        scope = self._scope_occ(key, path)
        stored = self.externals.get(key)
        if stored is not None and stored[0] == scope:
            self._write(ext.dataset, name, stored[1], path)
        else:  # not seen yet: hold the record until it appears or the scope ends
            self._write(ext.dataset, name, None, path, pending=(key, scope))

    def _reset_external(self, key: ExternalKey) -> None:
        self.externals.pop(key, None)
        self._resolve_missing(key, None)

    def _resolve_missing(self, key: ExternalKey, scope: int | None) -> None:
        waiters = self.waiting.get(key)
        if not waiters:
            return
        keep, touched = [], set()
        for record, name, waiter_scope in waiters:
            if scope is not None and waiter_scope != scope:
                keep.append((record, name, waiter_scope))
                continue
            if record.pending.pop(name, None) is not None:
                record.paths.pop(name, None)
                record.real -= 1
                touched.add(record.dataset)
        if keep:
            self.waiting[key] = keep
        else:
            del self.waiting[key]
        for dataset in touched:
            self._drain(dataset)

    def _close(self, occ: int, node: RNode) -> None:
        self.open_occ.discard(occ)
        self.context.pop(occ, None)
        for key in node.scope_keys:
            stored = self.externals.get(key)
            if stored is not None and stored[0] == occ:
                del self.externals[key]
            self._resolve_missing(key, occ)
        for dataset in node.hold_datasets:
            self._drain(dataset)

    # --- records ------------------------------------------------------------

    def _boundary(self, dataset: str, path: OccPath) -> OccPath:
        """The part of ``path`` that decides record boundaries for ``dataset``.

        Below an element with ``__NEW_DATASET__`` for the dataset, deeper
        elements no longer split records, so the path is cut at that element.
        """
        explicit = self.rt.explicit.get(dataset)
        if explicit:
            for i in range(len(path) - 1, -1, -1):
                if path[i][0] in explicit:
                    # The leading marker records which record element this is,
                    # so entering any other one (book, then magazine) splits too.
                    return ((RECORD_ELEMENT, path[i][1]), *path[: i + 1])
        return path

    def _reachable(self, record: Record, node_id: int, occ: int) -> bool:
        """Can a value still arriving from occurrence ``occ`` of element
        ``node_id`` reach ``record``? (Rule 4.)

        True when the record holds values from strictly inside that occurrence
        and the element is still open. Holding records back (``_ready``) and
        sharing late values with them (``_write``) both use this.
        """
        return record.inside.get(node_id) == occ and occ in self.open_occ

    def _write(
        self,
        dataset: str,
        name: str,
        value: Any,
        path: OccPath,
        *,
        as_list: bool = False,
        pending: tuple[ExternalKey, int] | None = None,
    ) -> None:
        record = self.latest.get(dataset)
        if path and path[-1][0] in self.rt.enclosing.get(dataset, ()):
            # Rule 4: this value belongs to an element that can enclose records.
            # Remember it for records that enter the element later, and share it
            # with the held records already inside it.
            node_id, occ = path[-1]
            shared = self.context.setdefault(occ, {}).setdefault(dataset, {})
            if as_list and name in shared and shared[name][1] == path:
                shared[name][0].append(value)
            else:
                shared[name] = ([value] if as_list else value, path, as_list, pending)
            reached_latest = False
            for held in reversed(self.queues[dataset]) if record is not None else ():
                if held.seen.get(node_id) != occ:
                    break  # records touching this occurrence are the queue's tail
                if self._reachable(held, node_id, occ) and (
                    name not in held.paths or (as_list and held.paths[name] == path)
                ):
                    self._set(held, name, value, path, None, pending, as_list)
                    reached_latest = reached_latest or held is record
            if reached_latest:
                return
        bpath = self._boundary(dataset, path) if dataset in self.rt.explicit else path
        # Occurrence ids are unique per element, so a record that already holds
        # the deepest occurrence of this path also holds all of its ancestors.
        same = (
            bool(bpath)
            and record is not None
            and record.occ.get(bpath[-1][0]) == bpath[-1][1]
        )
        if record is None or (name in record.paths and not as_list):
            record = self._new_record(dataset)
            same = False
        elif not same:
            occ_map = record.occ
            for node_id, occ in bpath:
                if occ_map.get(node_id, occ) != occ:
                    record = self._new_record(dataset)
                    break
        self._set(record, name, value, path, None if same else bpath, pending, as_list)

    def _set(
        self,
        record: Record,
        name: str,
        value: Any,
        path: OccPath,
        bpath: OccPath | None,
        pending: tuple[ExternalKey, int] | None,
        as_list: bool,
    ) -> None:
        """Store a value; ``bpath`` is None when the record already holds it."""
        assert not record.emitted, "a released record received a value"
        if bpath:
            occ_map = record.occ
            for node_id, occ in bpath:
                occ_map[node_id] = occ
        if path and record.seen.get(path[-1][0]) != path[-1][1]:
            enclosing = self.rt.enclosing.get(record.dataset, ())
            for node_id, occ in path:
                record.seen[node_id] = occ
            for node_id, occ in path[:-1]:
                if record.inside.get(node_id) != occ and node_id in enclosing:
                    record.inside[node_id] = occ
                    self._inherit(record, occ)
        had = name in record.paths
        record.paths[name] = path
        record.real += 1
        self.seq += 1
        record.seq = self.seq
        if pending is not None:
            record.pending[name] = pending
            self.waiting.setdefault(pending[0], []).append((record, name, pending[1]))
        elif as_list:
            current = record.data.get(name)
            if had and isinstance(current, list):
                current.append(value)
            else:  # never append to a list that came from global_values
                record.data[name] = [value]
        else:
            record.data[name] = value

    def _inherit(self, record: Record, occ: int) -> None:
        """Give ``record`` the values of enclosing occurrence ``occ`` it lacks."""
        shared = self.context.get(occ, {}).get(record.dataset)
        if not shared:
            return
        for field, (value, source, as_list, pending) in shared.items():
            if field in record.paths:
                continue
            record.paths[field] = source
            if pending is not None:
                stored = self.externals.get(pending[0])
                if stored is not None and stored[0] == pending[1]:
                    record.data[field] = stored[1]
                else:
                    record.pending[field] = pending
                    self.waiting.setdefault(pending[0], []).append(
                        (record, field, pending[1])
                    )
            else:
                record.data[field] = list(value) if as_list else value

    def _new_record(self, dataset: str) -> Record:
        record = Record(dataset, dict(self.global_values))
        self.queues.setdefault(dataset, deque()).append(record)
        self.latest[dataset] = record
        self.order.setdefault(dataset)
        self._drain(dataset)
        return record

    def _ready(self, record: Record) -> bool:
        if record.pending or self.latest.get(record.dataset) is record:
            return False
        owners = self.rt.owner_fields.get(record.dataset)
        if owners:
            lists = self.rt.owner_lists.get(record.dataset, {})
            for node_id, occ in record.inside.items():
                names = owners.get(node_id)
                if names is None or not self._reachable(record, node_id, occ):
                    continue
                if not names <= record.paths.keys() or node_id in lists:
                    return False  # an enclosing element may still supply a value
        return True

    def _drain(self, dataset: str) -> None:
        queue = self.queues.get(dataset)
        while queue and self._ready(queue[0]):
            record = queue.popleft()
            record.emitted = True
            if record.real > 0:
                self.out.append((dataset, record.data))


# --- input -------------------------------------------------------------------


def _is_element(source: Any) -> bool:
    return isinstance(source, ET.Element) or (
        not isinstance(source, (str, bytes, bytearray, memoryview, os.PathLike))
        and hasattr(source, "tag")
        and hasattr(source, "attrib")
        and hasattr(source, "iter")
    )


def _chunks(source: Any) -> Iterator[str | bytes]:
    if isinstance(source, str):
        if "<" not in source and len(source) < 4096 and os.path.exists(source):
            raise ConfigurationError(
                f"xml looks like a file path ({source!r}); a str is read as XML"
                " content, so pass pathlib.Path(...) to read a file"
            )
        for i in range(0, len(source), CHUNK_SIZE):
            yield source[i : i + CHUNK_SIZE]
    elif isinstance(source, (bytes, bytearray, memoryview)):
        view = memoryview(source).cast("B")
        for i in range(0, len(view), CHUNK_SIZE):
            yield bytes(view[i : i + CHUNK_SIZE])
    elif isinstance(source, os.PathLike):
        with open(source, "rb") as fh:
            while chunk := fh.read(CHUNK_SIZE):
                yield chunk
    elif hasattr(source, "read"):
        while chunk := source.read(CHUNK_SIZE):
            yield chunk
    else:
        raise TypeError(
            "xml must be XML content (str or bytes), an os.PathLike, a file object,"
            f" or an Element, not {type(source).__name__}"
        )


def iter_events(engine: Engine, source: Any) -> Iterator[tuple[str, dict[str, Any]]]:
    """Feed ``source`` through ``engine``, yielding records as they finish."""
    out = engine.out
    if isinstance(source, ET.ElementTree):
        source = source.getroot()
    if _is_element(source):
        engine.start(source)
        walk = [(source, iter(source))]
        while walk:
            child = next(walk[-1][1], None)
            if child is None:
                engine.end(walk.pop()[0])
            elif isinstance(
                child.tag, str
            ):  # skip comments and processing instructions
                engine.start(child)
                walk.append((child, iter(child)))
            while out:
                yield out.popleft()
    else:
        parser: ET.XMLPullParser[ET.Element] = ET.XMLPullParser(events=("start", "end"))
        open_elements: list[ET.Element] = []

        def handle() -> Iterator[tuple[str, dict[str, Any]]]:
            start, end = engine.start, engine.end
            # typeshed's read_events() also covers namespace events, which are
            # not requested here: every event is ("start" | "end", Element).
            events: Iterator[tuple[str, ET.Element]] = parser.read_events()  # type: ignore[assignment]
            for event, elem in events:
                if event == "start":
                    open_elements.append(elem)
                    start(elem)
                else:
                    end(elem)
                    open_elements.pop()
                    if open_elements:
                        # Free finished elements as we go. Earlier siblings are
                        # already gone, so this one is always the first child.
                        del open_elements[-1][0]
                    elem.clear()
                while out:
                    yield out.popleft()

        for chunk in _chunks(source):
            parser.feed(chunk)
            yield from handle()
        parser.close()
        yield from handle()
    engine.finish()
    while out:
        yield out.popleft()
