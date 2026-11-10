# Configuration

Gecko reads an INI file. `gecko -init` creates it from a built-in template and walks
you through every value. You can also edit the file by hand afterwards.
[Installation](installation.md#where-the-configuration-lives) explains where Gecko
looks for the file.

## Minimal example

```ini
[System]
os = rocky
os_version = 9.4
initialized = true

[Logs]
logs_dir = /data/latest/logs/
science_dir = /data/latest/

[Report]
report_path = /home/obs/gecko_reports
time_pattern = ^(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?)
email_alerts = false
recipient_email =
machine_name =

[Machine]
cpu_threshold = 85
memory_threshold = 90
```

The `help_text` entries in the template are the explanations `gecko -init` prints.
Gecko ignores them otherwise.

## `[System]`

`os`, `os_version`
: Free text, written at the top of the system-information section of each report,
  for example `rocky` and `9.4`.

`initialized`
: Set to `true` by `gecko -init`. Gecko refuses to file a report until this is `true`,
  so a half-configured template is never used by accident. If you write the file by
  hand, set it yourself.

## `[Logs]`

`logs_dir` (required)
: Directory holding the instrument logs. Gecko searches it **recursively**:
  - every file in it is copied into the report folder, and
  - every file ending in `.log` is scanned for recent errors and warnings (see
    [`time_pattern`](#time-pattern)).

  Point this at the current night's logs (for example a `latest` symlink to today's
  dated folder), not the whole log archive. Everything under it is copied on every run.

`science_dir` (required)
: Directory holding science data. Gecko copies the **newest file** (by modification
  time) from each of these folders, if they exist:
  - `science_dir/acam`
  - `science_dir/slicecam`
  - `science_dir` itself

  These sub-folder names are currently fixed.

## `[Report]`

`report_path` (required)
: Directory where reports are written. It must already exist. Gecko creates a
  sub-folder per UTC date inside it. See [what's in a report](report-contents.md).

(time-pattern)=
`time_pattern`
: Regular expression that finds the timestamp at the **start** of each log line. The
  first capture group must hold the timestamp, in a form Python's
  {py:meth}`datetime.fromisoformat <datetime.datetime.fromisoformat>` accepts. The
  default matches `2026-11-06 07:13:05` and `2026-11-06T07:13:05.123456`.

  A line ends up in the report when **all** of these are true:
  - it contains `error` or `warning` (any capitalization),
  - it starts with a timestamp matching this pattern, and
  - that timestamp is within the last 24 hours, compared with the machine's
    **local** clock.

  Lines without a leading timestamp are left out of the summary, but they are still
  in the copied log files.

  :::{note}
  On Python 3.8–3.10, `fromisoformat` only accepts fractional seconds with exactly 3
  or 6 digits, and no `Z` suffix. Timestamps that include a UTC offset (such as
  `+00:00`) currently cause that log file's summary to be skipped. See
  [troubleshooting](troubleshooting.md#errors-missing-from-the-summary).
  :::

`email_alerts`
: `true` to email each report, `false` (the default) to only save it. A blank value
  counts as `false`.

`recipient_email`
: Address the report is sent to. Required when `email_alerts = true`.

`machine_name`
: Used as the email's **From** address. Required when `email_alerts = true`. Many mail
  servers reject a bare host name, so use a full address such as
  `gecko@venus.observatory.edu`.

Email is sent with `/usr/sbin/sendmail -t -oi`. The text report and the `.tar.gz`
bundle are attached.

## `[Machine]`

`cpu_threshold`, `memory_threshold`
: Percentages, for example `85` and `90`. These are stored for planned
  health-monitoring features and **currently have no effect**.

## Editing by hand

You can edit the file with any text editor. Run `gecko -init` again at any time to
step through the values. It shows the current value for each prompt and keeps it if
you press Enter.
