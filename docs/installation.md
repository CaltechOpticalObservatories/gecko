# Installation

Gecko runs on **Linux** with **Python 3.8 or newer**. These steps are for the person
setting up an instrument machine. Operators only need the
[operator guide](operator-guide.md).

## System requirements

| Needed for | Requirement |
|---|---|
| Everything | Python ≥ 3.8 and `pip` (or `pipx`) |
| Everything | Read access to the instrument's log and science directories |
| Screenshots | `xwd` and ImageMagick `convert` on `PATH`, plus access to the X11 displays |
| Email alerts | A working `sendmail` at `/usr/sbin/sendmail` (Postfix and Sendmail both provide one) |

Screenshots and email are optional. Without them, Gecko still builds the report and
prints a message about the step that couldn't run.

Install the screenshot tools with your distribution's package manager. Package names
vary by release. `xwd` usually comes from `x11-apps` on Debian/Ubuntu, and from
`xorg-x11-apps` or `xwd` on RHEL, Rocky and Alma. ImageMagick is `imagemagick` on
Debian/Ubuntu and `ImageMagick` on RHEL-family systems (from EPEL on some releases).
Check that they're available:

```console
$ command -v xwd convert
```

## Install Gecko

Pick one of these. Each one gives you a `gecko` command.

### Option A: shared virtual environment (recommended for instrument machines)

```console
$ sudo python3 -m venv /opt/gecko
$ sudo /opt/gecko/bin/pip install "git+https://github.com/CaltechOpticalObservatories/gecko.git"
$ sudo ln -s /opt/gecko/bin/gecko /usr/local/bin/gecko
```

To upgrade later, rerun the `pip install` line with `--upgrade`.

### Option B: per-user install with pipx

```console
$ pipx install "git+https://github.com/CaltechOpticalObservatories/gecko.git"
```

### Option C: source checkout

Use this if you want to run straight from a clone, as with releases before 0.2:

```console
$ git clone https://github.com/CaltechOpticalObservatories/gecko.git
$ cd gecko
$ python3 -m pip install --user psutil
$ ./gecko --version
```

On Debian 12, Ubuntu 23.04 and newer, `pip install --user` is blocked for the system
Python. Install `psutil` with `sudo apt install python3-psutil` instead.

`./gecko` can be symlinked onto the `PATH`
(`sudo ln -s "$PWD/gecko" /usr/local/bin/gecko`). Unlike before 0.2, it now works
from any directory.

## Configure

Run the interactive setup once. It explains each section and asks for the values:

```console
$ gecko -init
```

Press **Enter** at a prompt to keep the value shown in parentheses. See
[configuration](configuration.md) for what each setting does.

### Where the configuration lives

Gecko uses the first file that exists from this list:

1. The path given with `-c` / `--config`
2. The path in the `GECKO_CONFIG` environment variable
3. `~/.config/gecko/gecko.ini` (or `$XDG_CONFIG_HOME/gecko/gecko.ini`)
4. `/etc/gecko/gecko.ini`

`gecko -init` writes to the path from `--config` or `GECKO_CONFIG` if one is given,
and otherwise to `~/.config/gecko/gecko.ini`.

**One config shared by all accounts on a machine:** create it in `/etc` and every
user picks it up automatically:

```console
$ sudo /opt/gecko/bin/gecko -init --config /etc/gecko/gecko.ini
```

Make sure the account operators use can write to the configured `report_path`.

## Check the setup

File a test report:

```console
$ gecko -u "$USER" -m "Test report after installing Gecko"
```

Open the bundle it prints and check it against
[what's in a report](report-contents.md). If screenshots or logs are missing, see
[troubleshooting](troubleshooting.md).

(migrating)=
## Upgrading from a source checkout older than 0.2

Before 0.2, `gecko -init` saved settings **inside the repository**, in
`triage_package/triage.ini`. Version 0.2 moves that file, so `git pull` will refuse
to run while it has local changes. Save your settings first:

```console
$ cd /path/to/gecko
$ mkdir -p ~/.config/gecko
$ cp triage_package/triage.ini ~/.config/gecko/gecko.ini
$ git checkout -- triage_package/triage.ini
$ git pull
```

Then run `gecko -u "$USER" -m "test"` to confirm the settings were picked up.

If you run a newer Gecko while an initialized `triage_package/triage.ini` is still
present, Gecko uses it and prints a warning asking you to move it. `gecko -init` also
copies its values into the new location automatically.
