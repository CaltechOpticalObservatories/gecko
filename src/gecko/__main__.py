"""Allow ``python -m gecko``."""
import sys

from .cli import main

sys.exit(main())
