"""Filesystem locations used by the application.

Keeping these paths relative to this module makes the installer work when it is
started from a shortcut, a terminal in another directory, or a packaged build.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def resolve_project_path(path: str | Path) -> Path:
    """Return an absolute path, relative paths being anchored at the project."""
    candidate = Path(path).expanduser()
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate
