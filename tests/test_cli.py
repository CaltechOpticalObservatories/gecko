import tarfile

import pytest

from gecko import __version__, cli


def run(*argv):
    return cli.main(list(argv))


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        run("--version")
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


@pytest.mark.parametrize("flag", ["-init", "--initialize"])
def test_legacy_init_flags_are_accepted(flag):
    args = cli.build_parser().parse_args([flag])
    assert args.initialize is True


def test_legacy_short_report_flags_are_accepted():
    args = cli.build_parser().parse_args(["-u", "Steven.B", "-m", "channel looked weird"])
    assert (args.user, args.message) == ("Steven.B", "channel looked weird")


def test_message_without_user_is_rejected(capsys):
    assert run("-m", "something broke") == 2
    assert "user and a message" in capsys.readouterr().err


def test_init_cannot_be_combined_with_report_flags():
    with pytest.raises(SystemExit) as exc:
        run("-init", "-m", "x")
    assert exc.value.code == 2


def test_report_without_config_gives_friendly_error(capsys):
    assert run("-u", "op", "-m", "broken") == 1
    err = capsys.readouterr().err
    assert "gecko -init" in err
    assert "Traceback" not in err


def test_report_with_uninitialized_template_gives_friendly_error(tmp_path, capsys):
    from gecko.config import TEMPLATE_PATH

    config = tmp_path / "fresh.ini"
    config.write_text(TEMPLATE_PATH.read_text())
    assert run("-c", str(config), "-u", "op", "-m", "broken") == 1
    assert "has not been initialized" in capsys.readouterr().err


def test_full_report_bundle(site, capsys):
    assert run("-c", str(site["config"]), "-u", "op", "-m", "shutter stuck") == 0
    out = capsys.readouterr().out
    assert "Triage workflow complete" in out

    archives = list(site["reports"].glob("*/*.tar.gz"))
    assert len(archives) == 1
    with tarfile.open(archives[0]) as tar:
        names = tar.getnames()

    assert any(name.startswith("gecko_report_") and name.endswith(".txt") for name in names)
    assert "camera.log" in names
    assert "motor.log" in names
    # Regression: science images used to be left out of the tarball.
    assert "acam_0002.fits" in names
    assert "acam_0001.fits" not in names

    report = next(site["reports"].glob("*/gecko_report_*.txt")).read_text()
    assert "USER: op\nMESSAGE: shutter stuck" in report
    assert "ERROR shutter timeout" in report
    assert "WARNING drift" in report
    assert "stale error from days ago" not in report
    assert "rocky :: 9" in report


def test_init_writes_user_config(tmp_path, monkeypatch):
    answers = iter(
        {
            "logs_dir": str(tmp_path),
            "science_dir": str(tmp_path),
            "report_path": str(tmp_path),
        }.get(key, "")
        for key in [
            "os", "os_version",
            "logs_dir", "science_dir",
            "report_path", "time_pattern", "email_alerts", "recipient_email", "machine_name",
            "cpu_threshold", "memory_threshold",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))

    assert run("-init") == 0

    from gecko.config import is_initialized, user_config_path

    target = user_config_path()
    assert target.is_file()
    assert is_initialized(target)
    assert f"logs_dir = {tmp_path}" in target.read_text()


def test_report_path_containing_dots(site, tmp_path):
    # Regression: the tarball name sanitizer used to rewrite '.' in the whole path.
    from .conftest import write_config

    reports = tmp_path / ".gecko" / "reports.d"
    reports.mkdir(parents=True)
    config = write_config(
        tmp_path / "dotted.ini",
        System={"initialized": "true"},
        Logs={"logs_dir": site["logs"], "science_dir": site["science"]},
        Report={"report_path": reports},
    )
    assert run("-c", str(config), "-u", "op", "-m", "x") == 0
    assert len(list(reports.glob("*/*.tar.gz"))) == 1
