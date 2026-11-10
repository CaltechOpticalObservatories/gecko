"""Shared fixtures: an isolated, initialized Gecko site with fake logs and science data."""
import configparser
import os
from datetime import datetime, timedelta

import psutil
import pytest

from gecko import triage
from gecko.config import TEMPLATE_PATH


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    """Keep tests away from the real ~/.config, $GECKO_CONFIG and current directory."""
    monkeypatch.delenv("GECKO_CONFIG", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    monkeypatch.setattr("gecko.config.SYSTEM_CONFIG_PATH", tmp_path / "etc" / "gecko.ini")
    monkeypatch.setattr("gecko.config.legacy_config_paths", lambda: [])
    monkeypatch.chdir(tmp_path)


@pytest.fixture(autouse=True)
def fast_system_info(monkeypatch):
    """Skip the 3-second CPU sampling and avoid capturing real displays."""
    real = psutil.cpu_times_percent
    monkeypatch.setattr(
        triage.psutil, "cpu_times_percent", lambda interval=None, percpu=False: real(percpu=percpu)
    )
    monkeypatch.setattr(triage.Triagetools, "find_displays", lambda self: [])


def write_config(path, **sections):
    """Write a config file based on the packaged template with overrides applied."""
    parser = configparser.ConfigParser()
    parser.read(TEMPLATE_PATH)
    for section, values in sections.items():
        for key, value in values.items():
            parser[section][key] = str(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        parser.write(handle)
    return path


@pytest.fixture
def site(tmp_path):
    """An initialized config pointing at fake log, science and report folders."""
    logs = tmp_path / "data" / "logs"
    science = tmp_path / "data" / "science"
    reports = tmp_path / "reports"
    for folder in (logs / "subsystem", science / "acam", reports):
        folder.mkdir(parents=True)

    now = datetime.now()
    recent = (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    old = (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
    (logs / "camera.log").write_text(
        f"{recent} INFO all good\n"
        f"{recent} ERROR shutter timeout\n"
        f"{old} ERROR stale error from days ago\n",
        encoding="utf-8",
    )
    (logs / "subsystem" / "motor.log").write_text(f"{recent} WARNING drift\n", encoding="utf-8")

    older = science / "acam" / "acam_0001.fits"
    newest = science / "acam" / "acam_0002.fits"
    older.write_bytes(b"old")
    newest.write_bytes(b"new")
    os.utime(older, (1, 1))

    config = write_config(
        tmp_path / "gecko.ini",
        System={"initialized": "true", "os": "rocky", "os_version": "9"},
        Logs={"logs_dir": logs, "science_dir": science},
        Report={"report_path": reports, "email_alerts": "false"},
    )
    return {"config": config, "reports": reports, "logs": logs, "science": science}
