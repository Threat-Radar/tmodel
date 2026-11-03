"""Entry point for the standalone engine executable (bin/build-engine, #124).

Same as the `tmodel` command; the desktop app runs it as `tmodel-engine serve`.
"""

import sys

from engine.cli import main

if __name__ == "__main__":
    sys.exit(main())
