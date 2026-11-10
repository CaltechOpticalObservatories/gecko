# Gecko Triage Tool

[![CI](https://github.com/CaltechOpticalObservatories/gecko/actions/workflows/ci.yml/badge.svg)](https://github.com/CaltechOpticalObservatories/gecko/actions/workflows/ci.yml)
[![Docs](https://github.com/CaltechOpticalObservatories/gecko/actions/workflows/docs.yml/badge.svg)](https://caltechopticalobservatories.github.io/gecko/)

## What is Gecko?

Gecko is a command-line triage and diagnostics tool designed to help operators and engineers quickly collect useful debugging information when an instrument or system encounters a problem.

Instead of manually gathering logs, screenshots, and science images, Gecko automates the process and produces a single packaged report that can be reviewed or shared with the development and operations teams.

Gecko is especially useful during:

- Instrument failures or unexpected behavior  
- Software crashes or lockups  
- Data acquisition issues  
- Hardware communication problems  
- On-sky observing anomalies  

---

### What Gecko Can Collect

When run in triage mode, Gecko can automatically gather:

- System information (CPU, memory, temperatures)  
- System and application log files, with recent errors and warnings summarized  
- Screenshots of the current system state  
- Science images or recent exposure data (if configured)  
- A compressed report bundle for archiving or emailing  

---

### Why Use Gecko?

Gecko provides a consistent and repeatable way to capture critical debugging context at the moment an issue occurs. This reduces downtime and helps teams diagnose problems faster, without requiring users to manually locate and send multiple files.

## Quick start

Gecko runs on Linux with Python 3.8 or newer.

```bash
pip install "git+https://github.com/CaltechOpticalObservatories/gecko.git"
gecko -init                                   # once per machine/account
gecko -u "your.name" -m "Description of the issue"
```

From a source checkout, `./gecko` works the same way.

> **Upgrading a checkout from before 0.2?** Copy `triage_package/triage.ini` to
> `~/.config/gecko/gecko.ini` **before** `git pull`. See the
> [upgrade notes](https://caltechopticalobservatories.github.io/gecko/installation.html#migrating).

## Documentation

**https://caltechopticalobservatories.github.io/gecko/**

- [Operator guide](docs/operator-guide.md): filing a report
- [Installation](docs/installation.md) and [configuration](docs/configuration.md): setting up a machine
- [What's in a report](docs/report-contents.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Development](docs/development.md): tests, tox, docs, releasing

## License

MIT. See [LICENSE](LICENSE).
