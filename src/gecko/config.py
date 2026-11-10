"""Locate and create Gecko configuration files.

Lookup order used by :func:`resolve_config_path`:

1. An explicit path (``--config``).
2. The ``GECKO_CONFIG`` environment variable.
3. The per-user file ``$XDG_CONFIG_HOME/gecko/gecko.ini`` (default ``~/.config/gecko/gecko.ini``).
4. The system-wide file ``/etc/gecko/gecko.ini``.
5. A legacy ``triage_package/triage.ini`` from a pre-0.2 source checkout, if it was initialized.
"""
import configparser
import os
import shutil
import sys
from pathlib import Path

ENV_VAR = "GECKO_CONFIG"
SYSTEM_CONFIG_PATH = Path("/etc/gecko/gecko.ini")
TEMPLATE_PATH = Path(__file__).with_name("triage.ini")
_LEGACY_RELATIVE = Path("triage_package") / "triage.ini"


def user_config_path():
    """Return the per-user config path, honoring ``XDG_CONFIG_HOME``."""
    base = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / "gecko" / "gecko.ini"


def legacy_config_paths():
    """Return candidate locations of a pre-0.2 ``triage_package/triage.ini``."""
    candidates = [Path.cwd() / _LEGACY_RELATIVE]
    # src/gecko/config.py -> repository root when running from a source checkout
    repo_root = Path(__file__).resolve().parents[2]
    candidates.append(repo_root / _LEGACY_RELATIVE)
    unique = []
    for path in candidates:
        if path not in unique:
            unique.append(path)
    return unique


def is_initialized(path):
    """Return True if ``path`` is a readable config with ``System.initialized = true``."""
    parser = configparser.ConfigParser()
    try:
        if not parser.read(path):
            return False
    except configparser.Error:
        return False
    value = parser.get("System", "initialized", fallback="").strip().lower()
    return value in {"1", "true", "yes", "on"}


def find_legacy_config():
    """Return an initialized legacy config path, or None."""
    for path in legacy_config_paths():
        if path.is_file() and is_initialized(path):
            return path
    return None


def _warn_legacy(path):
    print(
        f"gecko: warning: using legacy config {path}.\n"
        f"       Move it to {user_config_path()} (or set {ENV_VAR}); "
        "support for the old location will be removed in a future release.",
        file=sys.stderr,
    )


def resolve_config_path(explicit=None):
    """Return the config file Gecko should read.

    If no existing file is found, the per-user path is returned so that error
    messages point the operator at the location ``gecko -init`` will create.
    """
    if explicit:
        return Path(explicit).expanduser()
    env_value = os.environ.get(ENV_VAR)
    if env_value:
        return Path(env_value).expanduser()
    for path in (user_config_path(), SYSTEM_CONFIG_PATH):
        if path.is_file():
            return path
    legacy = find_legacy_config()
    if legacy is not None:
        _warn_legacy(legacy)
        return legacy
    return user_config_path()


def init_target_path(explicit=None):
    """Return the config file ``gecko -init`` should write."""
    if explicit:
        return Path(explicit).expanduser()
    env_value = os.environ.get(ENV_VAR)
    if env_value:
        return Path(env_value).expanduser()
    return user_config_path()


def ensure_config_file(target):
    """Create ``target`` if needed and return its path.

    A new file is seeded from an initialized legacy config when one exists (so
    ``gecko -init`` migrates old settings), otherwise from the packaged template.
    """
    target = Path(target)
    if target.exists():
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    source = find_legacy_config() or TEMPLATE_PATH
    shutil.copyfile(source, target)
    if source != TEMPLATE_PATH:
        print(f"Copied existing settings from {source}")
    return target
