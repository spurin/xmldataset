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

from ._errors import ConfigurationError, MissingProcessError
from ._model import ExternalValue, Field, Node, Profile

__all__ = ["Engine", "compile_runtime", "iter_events"]

XML_NAMESPACE = "http://www.w3.org/XML/1998/namespace"
CHUNK_SIZE = 1 << 16
DOCUMENT = 0  # occurrence id for scopes that span the whole document
RECORD_ELEMENT = -1  # pseudo node id: the __NEW_DATASET__ element a record belongs to

OccPath = tuple[tuple[int, int], ...]  # ((profile node id, occurrence id), ...)
ExternalKey = tuple[str, str]  # (external dataset, field name)


class RNode:
    """A profile node prepared for matching."""

    __slots__ = (
        "always_follow",
        "children",
        "default_children",
        "depth",
        "exact",
        "external_values",
        "fields",
        "hold_datasets",
        "id",
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
        self.fields: tuple[Field, ...] = node.fields if node else ()
        self.external_values = node.external_values if node else ()
        self.resets = node.reset_external_values if node else ()
        self.processing = node.dataset_processing if node else ()
        self.key = self.name  # resolved below for prefixed names
        self.outputs = [
            (f, (f.prefix or "") + (f.name or self.name)) for f in self.fields
        ]
        self.children: list[RNode] = []
        self.exact: dict[str, RNode] = {}
        self.local: dict[str, RNode] = {}
        self.always_follow: set[int] = set()
        self.default_children: list[RNode] = []
        self.hold_datasets: tuple[str, ...] = ()
        self.scope_keys: tuple[ExternalKey, ...] = ()

    def lookup(self, tag: str) -> RNode | None:
        node = self.exact.get(tag)
        if node is None and tag[:1] == "{":
            node = self.local.get(tag[tag.find("}") + 1 :])
        return node


class Runtime:
    """A profile compiled for the engine (cached per profile and namespaces)."""

    def __init__(self, profile: Profile, namespaces: Mapping[str, str]) -> None:
        self.nodes: list[RNode] = []
        self.root = self._add(None, None)
        # Build iteratively: profiles may be deeper than the recursion limit.
        pending: list[tuple[Node, RNode]] = [
            (node, self.root) for node in profile.roots
        ]
        built: list[tuple[Node, RNode]] = []
        while pending:
            node, parent = pending.pop(0)
            if node.ignore:
                continue
            rnode = self._add(node, parent)
            built.append((node, rnode))
            parent.children.append(rnode)
            self._index(parent, rnode, namespaces)
            pending[:0] = [(child, rnode) for child in node.children]

        self.explicit: dict[str, set[int]] = {}
        self.owner_fields: dict[str, dict[int, set[str]]] = {}
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
            owner = rnode.parent
            assert owner is not None
            for spec, out_name in rnode.outputs:
                if spec.process is not None:
                    self.processes.add(spec.process)
                if spec.dataset is not None:
                    self._own(spec.dataset, owner.id, out_name)
                if spec.external_dataset is not None:
                    sources.setdefault((spec.external_dataset, out_name), []).append(
                        owner
                    )
            for ext in node.external_values:
                self._own(ext.dataset, rnode.id, ext.name or ext.field)
                consumers.setdefault((ext.external_dataset, ext.field), []).append(
                    rnode
                )
            for proc in node.dataset_processing:
                self.processes.add(proc.process)
        for rnode in self.nodes:
            rnode.default_children = [
                c
                for c in rnode.children
                if any(f.default is not None for f in c.fields)
                or (not c.fields and c.id in rnode.always_follow)
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

    def _own(self, dataset: str, owner_id: int, name: str) -> None:
        self.owner_fields.setdefault(dataset, {}).setdefault(owner_id, set()).add(name)

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
    __slots__ = ("data", "dataset", "max_depth", "occ", "paths", "pending", "real")

    def __init__(self, dataset: str, data: dict[str, Any]) -> None:
        self.dataset = dataset
        self.data = data
        self.occ: dict[int, int] = {}  # profile node id -> occurrence id
        self.paths: dict[str, OccPath] = {}  # field -> where its value came from
        self.pending: dict[str, tuple[ExternalKey, int]] = {}
        self.real = 0  # values written from the document (not inherited)
        self.max_depth = 0


class Frame:
    __slots__ = ("base", "elem", "flushed", "matched", "node", "occ", "path")

    def __init__(self, node: RNode | None, elem: Any, base: OccPath, occ: int) -> None:
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
            if node is None:
                stack.append(Frame(None, elem, (), -1))
                return
            if parent.matched is not None:
                parent.matched.add(node.id)
            base = parent.path
        else:
            node = self.rt.root.lookup(elem.tag)
            if node is None:
                stack.append(Frame(None, elem, (), -1))
                return
            base = ()
        self.next_occ += 1
        occ = self.next_occ
        self.open_occ.add(occ)
        stack.append(Frame(node, elem, base, occ))
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
            if current is not None:
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
            for spec, name in node.outputs:
                self._capture(spec, name, elem.text, frame.base)
        attrib = elem.attrib
        if attrib and node.children:
            local: dict[str, Any] | None = None
            for child in node.children:
                if child.key in attrib:
                    value = attrib[child.key]
                elif child.key == child.name:  # unprefixed: match any namespace
                    if local is None:
                        local = {
                            k[k.find("}") + 1 :]: v
                            for k, v in attrib.items()
                            if k[:1] == "{"
                        }
                    if child.name not in local:
                        continue
                    value = local[child.name]
                else:
                    continue
                if frame.matched is not None:
                    frame.matched.add(child.id)
                for spec, name in child.outputs:
                    self._capture(spec, name, value, frame.path)

    def _defaults(self, child: RNode, path: OccPath, parent: RNode) -> None:
        if child.fields:
            for spec, name in child.outputs:
                if spec.default is not None:
                    self._capture(spec, name, spec.default, path)
        elif child.id in parent.always_follow:
            self.next_occ += 1  # a stand-in occurrence for the missing element
            inner = (*path, (child.id, self.next_occ))
            for grandchild in child.children:
                if grandchild.fields or grandchild.id in child.always_follow:
                    self._defaults(grandchild, inner, child)

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
        bpath = self._boundary(dataset, path) if dataset in self.rt.explicit else path
        record = self.latest.get(dataset)
        # Occurrence ids are unique per element, so a record that already holds
        # the deepest occurrence of this path also holds all of its ancestors.
        same = False
        if record is not None and bpath:
            node_id, occ = bpath[-1]
            same = record.occ.get(node_id) == occ
            if same and not as_list and record.max_depth > self.depth[node_id]:
                # A value from an enclosing element: share it with every record
                # already started inside that element (which may still be open).
                applied = False
                for held in reversed(self.queues[dataset]):
                    if held.occ.get(node_id) != occ:
                        break
                    if name not in held.paths:
                        self._set(held, name, value, path, None, pending, as_list=False)
                        applied = True
                if applied:
                    return
        if record is None or (name in record.paths and not as_list):
            record = self._new_record(dataset, record, path, name)
            same = False
        elif not same:
            occ_map = record.occ
            for node_id, occ in bpath:
                if occ_map.get(node_id, occ) != occ:
                    record = self._new_record(dataset, record, path, name)
                    break
        self._set(
            record, name, value, path, None if same else bpath, pending, as_list=as_list
        )

    def _set(
        self,
        record: Record,
        name: str,
        value: Any,
        path: OccPath,
        bpath: OccPath | None,
        pending: tuple[ExternalKey, int] | None,
        *,
        as_list: bool,
    ) -> None:
        """Store a value; ``bpath`` is None when the record already holds it."""
        record.paths[name] = path
        if bpath:
            occ_map = record.occ
            for node_id, occ in bpath:
                occ_map[node_id] = occ
            depth = self.depth[bpath[-1][0]]
            if depth > record.max_depth:
                record.max_depth = depth
        record.real += 1
        if pending is not None:
            record.pending[name] = pending
            self.waiting.setdefault(pending[0], []).append((record, name, pending[1]))
        elif as_list:
            record.data.setdefault(name, []).append(value)
        else:
            record.data[name] = value

    def _new_record(
        self, dataset: str, previous: Record | None, path: OccPath, name: str
    ) -> Record:
        record = Record(dataset, dict(self.global_values))
        if previous is not None:
            for field, source in previous.paths.items():
                if (
                    field == name
                    or len(source) >= len(path)
                    or path[: len(source)] != source
                ):
                    continue
                # Inherit values from elements that enclose the new record.
                record.paths[field] = source
                bsource = self._boundary(dataset, source)
                for node_id, occ in bsource:
                    record.occ[node_id] = occ
                if bsource:
                    record.max_depth = max(record.max_depth, self.depth[bsource[-1][0]])
                waiting = previous.pending.get(field)
                if waiting is not None:
                    record.pending[field] = waiting
                    self.waiting[waiting[0]].append((record, field, waiting[1]))
                else:
                    value = previous.data[field]
                    record.data[field] = (
                        list(value) if isinstance(value, list) else value
                    )
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
            open_occ = self.open_occ
            for node_id, occ in record.occ.items():
                if occ in open_occ:
                    names = owners.get(node_id)
                    if names and not names <= record.paths.keys():
                        return False  # an enclosing element may still supply a value
        return True

    def _drain(self, dataset: str) -> None:
        queue = self.queues.get(dataset)
        while queue and self._ready(queue[0]):
            record = queue.popleft()
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
