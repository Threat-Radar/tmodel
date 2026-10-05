"""Engine operations, independent of transport.

The local API and the CLI both call these functions, so the GUI and the CLI
always run the same engine code (APP-0001 A-030 boundary, A-060 CLI parity).
"""

from __future__ import annotations

import platform
from typing import Any

from engine import __version__

ENGINE_NAME = "tmodel-engine"


def version() -> dict[str, Any]:
    """Engine and runtime version."""
    return {
        "engine": ENGINE_NAME,
        "version": __version__,
        "python": platform.python_version(),
    }


def health() -> dict[str, Any]:
    """Liveness check. Grows real checks (store reachable, library loaded) later."""
    return {"status": "ok", **version()}
