import tomllib


from rcdesign.set_version import get_ver, bump


with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)
    release = data["project"]["version"]


class TestSetVer:
    def test_get_ver(self):
        ver = get_ver("pyproject.toml")
        assert isinstance(ver, str)
        assert ver.count(".") == 2  # Should be in major.minor.patch format
        assert ver == release

    def test_bump(self):
        assert bump("patch") == "0.4.19"
        assert bump("minor") == "0.5.0"
        assert bump("major") == "1.0.0"
        assert bump("0.1.2") == "0.1.2"  # Should return the same version
        assert bump("invalid") == "0.0.0"  # Invalid input should return default
