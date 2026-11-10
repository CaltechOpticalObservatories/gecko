# Troubleshooting

Gecko prints `gecko: error: ...` on standard error and exits with a non-zero status
when it can't produce a report. Problems with individual steps (a screenshot, an
unreadable log, email) are printed but don't stop the run.

## Setup errors

`No configuration file found at ~/.config/gecko/gecko.ini. Run: gecko -init`
: No config exists for this account. Run `gecko -init`, point `GECKO_CONFIG` at an
  existing file, or create `/etc/gecko/gecko.ini` for the whole machine. See
  [installation](installation.md#configure).

`Configuration file ... has not been initialized`
: The file is still the blank template. Run `gecko -init --config <that file>`, or set
  `initialized = true` under `[System]` once you've filled it in by hand.

`Logs.logs_dir must be set in ...` (or `Report.report_path`, `Report.recipient_email`, ...)
: A required value is blank. Edit the file or rerun `gecko -init`.

`Report.report_path does not exist: ...`
: Create the directory, and make sure the operator account can write to it.

`Invalid regex in Report.time_pattern: ...`
: Fix the regular expression. Test it against a real log line with Python's `re`
  module before saving it.

`gecko: warning: using legacy config .../triage_package/triage.ini`
: A config from a pre-0.2 checkout is being used. Move it as the warning says. See
  [upgrading](installation.md#upgrading-from-a-source-checkout-older-than-02).

`you need to include a user and a message in your report`
: Both `-u` and `-m` are required.

## During a run

`No X11 displays found`
: No sockets were found in `/tmp/.X11-unix/`. This is expected on headless machines.
  Wayland sessions aren't supported.

`Failed to capture -> :0: [Errno 2] No such file or directory: 'xwd'`
: Install the screenshot tools (see [installation](installation.md#system-requirements)).

A screenshot is reported as captured but the PNG is missing or empty
: `xwd` couldn't connect to the display, usually because the account running Gecko
  isn't allowed to. Run Gecko as the user logged into that display, or grant access
  (for example with `xhost` or by sharing the `XAUTHORITY` file).

`Error: Permission denied to access the file at ...`
: The account running Gecko can't read that log. The rest of the run continues.

`Failed to send report: ...`
: `sendmail` failed. The report and bundle are still saved locally. Check that
  `/usr/sbin/sendmail` exists, that the machine can relay mail, and that the bundle
  isn't larger than your mail server's attachment limit (often 10–25 MB).

(errors-missing-from-the-summary)=
## Errors missing from the summary

If a log clearly has recent errors but its section in the text report is empty:

1. **The line doesn't start with a timestamp** matched by `time_pattern`. Only lines
   whose timestamp is at the very start are considered.
2. **The timestamp format isn't accepted.** The captured text must be parseable by
   `datetime.fromisoformat`. On Python 3.8–3.10 that means fractional seconds of
   exactly 3 or 6 digits, and no trailing `Z`.
3. **The timestamp has a UTC offset** (`+00:00`). Gecko compares it with a local time
   without an offset, prints `An unexpected error occurred: can't compare offset-naive
   and offset-aware datetimes`, and skips that file's summary.
4. **Clock differences.** Timestamps are compared with the machine's local clock. If
   the logs are in UTC and the machine isn't, the 24-hour window is shifted by the
   difference.
5. **The file doesn't end in `.log`.** Other files are copied but not scanned.

## The bundle is very large

Everything under `logs_dir` is copied on every run. Point `logs_dir` at the current
night's logs rather than the whole archive, and check whether the newest file in the
science folders is a very large image.

## Getting help

Open an issue at
<https://github.com/CaltechOpticalObservatories/gecko/issues>. Include the output of
`gecko --version`, the full error text, and (with paths and addresses removed if
necessary) your configuration file.
