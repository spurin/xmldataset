# API reference

Everything below is importable from the `xmldataset` package.

```{eval-rst}
.. module:: xmldataset

Parsing
-------

.. autofunction:: parse_using_profile

.. autofunction:: iter_records

Profiles
--------

.. autofunction:: compile_profile

.. autofunction:: load_profile

.. autofunction:: json_schema

.. autoclass:: Profile
   :members:
   :exclude-members: roots

The profile model
~~~~~~~~~~~~~~~~~

Profiles compile to these immutable classes. You rarely need them directly, but
they are useful for building or inspecting profiles in code.

.. autoclass:: Node
   :members: child

.. autoclass:: Field

.. autoclass:: ExternalValue

.. autoclass:: ExternalReset

.. autoclass:: DatasetProcess

Errors
------

.. autoexception:: XMLDatasetError

.. autoexception:: ProfileError

.. autoexception:: MissingProcessError

.. autoexception:: ConfigurationError

Types
-----

.. py:data:: XMLSource

   XML to read: ``str`` or ``bytes`` content, an :class:`os.PathLike` path, a
   file object, or an :class:`xml.etree.ElementTree.Element` or
   ``ElementTree``.

.. py:data:: Record

   One record of a dataset: a ``dict`` mapping field names to values.
```
