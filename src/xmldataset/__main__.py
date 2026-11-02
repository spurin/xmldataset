"""Allow ``python -m xmldataset``; see ``xmldataset --help``."""

from ._cli import main

raise SystemExit(main())
