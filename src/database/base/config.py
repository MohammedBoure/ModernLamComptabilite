import sys
import os

def get_external_path(filename):
    """
    Returns the absolute path to a file, accounting for PyInstaller's _MEIPASS.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(os.path.dirname(sys.executable), filename)
    return os.path.join(os.path.abspath("."), filename)

def _coerce_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)

    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default

def get_env_bool(env_name, default=False):
    """
    Reads a boolean value from an environment variable.
    """
    env_value = os.getenv(env_name)
    if env_value is not None:
        return _coerce_bool(env_value, default)
    return default
