import configparser

from gecko import config
from gecko.config import TEMPLATE_PATH, resolve_config_path, user_config_path

from .conftest import write_config


def test_template_is_packaged_and_uninitialized():
    parser = configparser.ConfigParser()
    assert parser.read(TEMPLATE_PATH)
    assert parser.get("System", "initialized") == "false"
    assert parser.get("Report", "email_alerts") == "false"


def test_explicit_path_wins(tmp_path, monkeypatch):
    monkeypatch.setenv("GECKO_CONFIG", str(tmp_path / "env.ini"))
    assert resolve_config_path(str(tmp_path / "cli.ini")) == tmp_path / "cli.ini"


def test_env_var_beats_user_config(tmp_path, monkeypatch):
    write_config(user_config_path())
    monkeypatch.setenv("GECKO_CONFIG", str(tmp_path / "env.ini"))
    assert resolve_config_path() == tmp_path / "env.ini"


def test_user_config_beats_system_config():
    write_config(config.SYSTEM_CONFIG_PATH)
    write_config(user_config_path())
    assert resolve_config_path() == user_config_path()


def test_system_config_used_when_no_user_config():
    write_config(config.SYSTEM_CONFIG_PATH)
    assert resolve_config_path() == config.SYSTEM_CONFIG_PATH


def test_defaults_to_user_path_when_nothing_exists():
    assert resolve_config_path() == user_config_path()


def test_initialized_legacy_config_is_used_with_warning(tmp_path, monkeypatch, capsys):
    legacy = write_config(
        tmp_path / "triage_package" / "triage.ini", System={"initialized": "true"}
    )
    monkeypatch.setattr(config, "legacy_config_paths", lambda: [legacy])
    assert resolve_config_path() == legacy
    assert "legacy config" in capsys.readouterr().err


def test_uninitialized_legacy_template_is_ignored(tmp_path, monkeypatch):
    legacy = write_config(tmp_path / "triage_package" / "triage.ini")
    monkeypatch.setattr(config, "legacy_config_paths", lambda: [legacy])
    assert resolve_config_path() == user_config_path()


def test_init_seeds_from_legacy_config(tmp_path, monkeypatch):
    legacy = write_config(
        tmp_path / "triage_package" / "triage.ini",
        System={"initialized": "true"},
        Logs={"logs_dir": "/data/old/logs"},
    )
    monkeypatch.setattr(config, "legacy_config_paths", lambda: [legacy])
    target = config.ensure_config_file(user_config_path())
    assert "/data/old/logs" in target.read_text()


def test_ensure_config_file_never_overwrites(tmp_path):
    existing = tmp_path / "mine.ini"
    existing.write_text("[System]\ninitialized = true\n")
    config.ensure_config_file(existing)
    assert existing.read_text() == "[System]\ninitialized = true\n"
