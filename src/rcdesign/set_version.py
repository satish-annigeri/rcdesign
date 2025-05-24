from pathlib import Path
import re
from datetime import datetime
from zoneinfo import ZoneInfo
import tomllib


ROOT_DIR = Path(__file__).resolve().parents[2]


def get_ver(src_ver: str = "pyproject.toml"):
    fpath = ROOT_DIR / src_ver
    with open(fpath, "rb") as f:
        data = tomllib.load(f)
    ver = data["project"]["version"]
    return ver


def set_ver():
    version = get_ver()
    fpath = ROOT_DIR / "src" / "rcdesign" / "__about__.py"
    with open(fpath, "w") as f:
        time_now = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()
        s = f"#  Version set by src/rcdesign/set_version.py {time_now}\n\n"
        s += f'__version__ = "{version}"\n'
        f.write(s)


def bump(next_ver: str) -> str:
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
