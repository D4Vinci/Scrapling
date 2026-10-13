import pytest

from scrapling.engines._browsers._validators import PlaywrightConfig, StealthConfig


@pytest.mark.parametrize("config_type", [PlaywrightConfig, StealthConfig])
@pytest.mark.parametrize("field", ["init_script", "executable_path"])
def test_newly_created_file_is_validated_again(tmp_path, config_type, field):
    path = tmp_path / "generated-file"
    kwargs = {field: str(path)}
    with pytest.raises(ValueError, match="not found"):
        config_type(**kwargs)
    path.write_text("generated", encoding="utf-8")
    assert getattr(config_type(**kwargs), field) == str(path)


@pytest.mark.parametrize("config_type", [PlaywrightConfig, StealthConfig])
@pytest.mark.parametrize("field", ["init_script", "executable_path"])
def test_deleted_file_is_not_accepted_from_cache(tmp_path, config_type, field):
    path = tmp_path / "removed-file"
    path.write_text("generated", encoding="utf-8")
    kwargs = {field: str(path)}
    config_type(**kwargs)
    path.unlink()
    with pytest.raises(ValueError, match="not found"):
        config_type(**kwargs)


def test_file_replaced_with_directory_is_rejected(tmp_path):
    path = tmp_path / "replaced-file"
    path.write_text("generated", encoding="utf-8")
    PlaywrightConfig(init_script=str(path))
    path.unlink()
    path.mkdir()
    with pytest.raises(ValueError, match="not a file"):
        PlaywrightConfig(init_script=str(path))
