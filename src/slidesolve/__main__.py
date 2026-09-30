"""Allow ``python -m slidesolve`` to run the command-line interface."""

from .cli import main


raise SystemExit(main())
