"""File-based logging for the QRE MCP server.

The server runs over stdio (MCP protocol), so stdout/stderr are not available
for human-readable logs. This module writes structured log lines to a file
that can be tailed in a separate terminal.

Log file path (in order of precedence):
  1. QRE_MCP_LOG environment variable
  2. ~/.local/share/qre-mcp/qre-mcp.log

Usage:
    tail -F ~/.local/share/qre-mcp/qre-mcp.log
"""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

_DEFAULT_LOG_DIR = Path.home() / ".local" / "share" / "qre-mcp"
_DEFAULT_LOG_FILE = _DEFAULT_LOG_DIR / "qre-mcp.log"

_LOG_FORMAT = "%(asctime)s %(levelname)-5s [%(name)s] %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger("qre_mcp")


def setup_logging() -> Path:
    """Configure file logging. Call once at server startup. Returns the log file path."""
    if logger.handlers:
        # Already configured (e.g. during tests)
        return _log_path()

    path = _log_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        path,
        maxBytes=5 * 1024 * 1024,  # 5 MB per file
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    handler.setLevel(logging.DEBUG)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.propagate = False

    logger.info("=== QRE MCP server started — log: %s ===", path)
    return path


def _log_path() -> Path:
    env = os.environ.get("QRE_MCP_LOG")
    return Path(env) if env else _DEFAULT_LOG_FILE
