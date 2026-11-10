# Development

## Setup

```console
$ git clone https://github.com/CaltechOpticalObservatories/gecko.git
$ cd gecko
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -e ".[dev]"
```

The `dev` extra installs pytest, ruff and tox.

## Layout

```text
src/gecko/
├── cli.py        # argument parsing and the report / -init flows
├── config.py     # finding, creating and migrating configuration files
├── triage.py     # the Triagetools class that collects everything
└── triage.ini    # template copied by `gecko -init`
gecko             # launcher for running from a source checkout
tests/            # pytest suite
docs/             # this documentation (Sphinx + MyST Markdown)
```

## Checks

All checks run through [tox](https://tox.wiki/):

| Command | What it does |
|---|---|
| `tox -e py312` | Run the tests on one Python version (`py38` to `py312`) |
| `tox -e lint` | `ruff check` |
| `tox -e docs` | Build the HTML docs into `docs/_build/html`. Warnings are errors |
| `tox -e linkcheck` | Check external links in the docs (not run in CI) |
| `tox` | Tests on every installed Python version, plus lint and docs |

During development, `pytest` and `ruff check src tests` work directly in the
virtual environment.

The tests never touch your real configuration. They point `XDG_CONFIG_HOME` and
`/etc/gecko` at temporary directories, skip the 3-second CPU sample and disable
screenshots.

## Continuous integration

`.github/workflows/ci.yml`
: Tests on Python 3.8–3.12 and ruff, for every push to `main` and every pull request.

`.github/workflows/docs.yml`
: Builds the docs for every pull request. On `main` it also publishes them to
  GitHub Pages at <https://caltechopticalobservatories.github.io/gecko/>.

## Writing docs

Pages are Markdown, parsed by [MyST](https://myst-parser.readthedocs.io/), with the
[Shibuya](https://shibuya.lepture.com/) theme. The CLI reference is generated from
`gecko.cli.build_parser()` and the API page from docstrings (Google style). Update
those at the source rather than in the page.

Preview locally:

```console
$ tox -e docs
$ python -m http.server -d docs/_build/html
```

## Releasing

1. Update `__version__` in `src/gecko/__init__.py`.
2. Move the "Unreleased" notes in `CHANGELOG.md` under the new version.
3. Merge to `main`, then tag: `git tag v0.2.0 && git push origin v0.2.0`.

## Compatibility promises

- **Python 3.8** is the minimum supported version. Don't use newer syntax or
  standard-library APIs; CI catches most of this.
- **The legacy command line keeps working**: `gecko -u NAME -m MESSAGE` and
  `gecko -init`/`--initialize`. New features can add options or subcommands, but
  must not break these.
- **Linux** is the deployment target.

## Roadmap

These changes are planned for later releases:

Core cleanup
: Run each step independently so one failure can't stop the bundle. Bundle exactly
  the files from this run, keeping the log folder structure. Handle timezone-aware
  timestamps. Add size and age limits for copied logs and science files. Make the
  science sub-folders configurable.

Command line
: Subcommands (`gecko report`, `gecko init`, `gecko config show|validate`) plus
  `--no-email` and `--dry-run`, with the legacy flags kept as aliases.

Desktop GUI
: A PySide6 application with a simple operator view (name, message, run, progress,
  open folder) and a separate settings page.
