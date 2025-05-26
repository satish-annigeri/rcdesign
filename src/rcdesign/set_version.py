import sys
from pathlib import Path
import re
from datetime import datetime
from zoneinfo import ZoneInfo
import tomllib


ROOT_DIR = Path(__file__).resolve().parents[2]


def get_ver(src_ver: str = "pyproject.toml"):
    """Get the current version of the project from the specified source file.
    Args:
        src_ver (str): The source file from which to read the version. Default is "pyproject.toml".
    Returns:
        str: The current version of the project.
    """
    fpath = ROOT_DIR / src_ver
    with open(fpath, "rb") as f:
        data = tomllib.load(f)
    ver = data["project"]["version"]
    return ver


def bump(next_ver: str) -> str:
    """Bump the version number based on the specified type (major, minor, patch) or return the specified version.
    Args:
        next_ver (str): The type of version bump ("major", "minor", "patch") or a specific version string.
    Returns:
        str: The new version number based on the specified type or the specified version string.
    """
    pattern = r"(\d+).(\d+).(\d+)"

    if next_ver.lower() in ["major", "minor", "patch"]:
        current_ver = get_ver()
        m = re.match(pattern, current_ver)
        if m:  # Current version is known to follow "major.minor.patch" format
            major, minor, patch = m.groups()
            match next_ver.lower():
                case "patch":
                    return f"{major}.{minor}.{int(patch) + 1}"
                case "minor":
                    return f"{major}.{int(minor) + 1}.{0}"
                case "major":
                    return f"{int(major) + 1}.{0}.{0}"
                case _:
                    return "0.0.0"
        else:  # Current version does not follow "major.minor.patch" format
            return "0.0.0"
    else:
        m = re.match(pattern, next_ver)
        if m:
            return f"{next_ver}"
        else:
            return "0.0.0"


def set_ver():
    """Get or set the version of the project based on command line arguments.

    If no arguments are provided, it returns the current version.
    If the first argument is "--bump" followed by "patch", "minor", or "major",
    it bumps the version accordingly and writes it to the `__about__.py` file.
    If the third argument is "--dry-run", it simulates the version change without writing to the file.
    Returns:
        str: A message indicating the current or new version, or the change made.
    """
    if len(sys.argv) == 1:
        return f"rcdesign v{get_ver()}"

    fpath = ROOT_DIR / "src" / "rcdesign" / "__about__.py"
    current_ver = get_ver()
    if len(sys.argv) > 2:
        if (sys.argv[1] == "--bump") and (sys.argv[2] in ["patch", "minor", "major"]):
            new_ver = bump(sys.argv[2])
        else:
            print("Invalid command options")
            sys.exit(1)
    dry_run = (len(sys.argv) > 3) and (sys.argv[3] == "--dry-run")

    time_now = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()
    s = f'\nChanging release version from "{current_ver}" to "{new_ver}"\n'
    if not dry_run:
        s = f"# Version set by src/rcdesign/set_version.py {time_now}\n"
        s += f'# Changing release version from "{current_ver}" to "{new_ver}"\n'
        s += f'\n__version__ = "{new_ver}"\n'
        with open(fpath, "w") as f:
            f.write(s)
    return s
