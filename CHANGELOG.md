# Changelog

All notable changes to Gecko are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.2.0]

### Upgrade note

If you run Gecko from a source checkout, **copy your settings out of
`triage_package/triage.ini` before pulling**. That file has moved, and `git pull` will
refuse to update while it has local changes. See
[Upgrading from a source checkout older than 0.2](https://caltechopticalobservatories.github.io/gecko/installation.html#migrating).

### Added

- Gecko is now an installable package (`pip install`, `pipx install`) that provides a
  `gecko` command. `python -m gecko` works too.
- Configuration is looked up in `--config`, `$GECKO_CONFIG`,
  `~/.config/gecko/gecko.ini` and `/etc/gecko/gecko.ini`, in that order.
- `-c`/`--config` and `-V`/`--version` options.
- Documentation site (Sphinx, Shibuya theme), published to GitHub Pages.
- Test suite, tox environments, and GitHub Actions for tests (Python 3.8–3.12), lint
  and docs.

### Changed

- `gecko -init` writes to the user's configuration file instead of overwriting the
  template in the repository. It copies settings from an old
  `triage_package/triage.ini` if it finds one.
- `./gecko` and symlinks to it now work from any directory.
- Errors are printed as `gecko: error: ...` with a non-zero exit status, instead of a
  traceback or a silent exit.
- The "Triage workflow complete" message, with the bundle path, is now printed
  whether or not email is enabled.
- The dated report folder is created automatically. `report_path` itself must exist.

### Fixed

- Science images were copied but left out of the `.tar.gz` bundle and the email.
- Running before `gecko -init`, or with `email_alerts` left blank, crashed with
  `ValueError: Not a boolean`.
- A `report_path` containing `.`, `:` or spaces broke bundle creation.
- The "Science Directory does not Exist" message printed `<built-in function dir>`
  instead of the folder name.
- System information no longer crashes on platforms without temperature sensors.

### Removed

- The unused `vncdotool` and `pillow` dependencies. The only runtime dependency is now
  `psutil`.
