# What's in a report

Each run writes into a folder named after the **UTC date**, inside the configured
`report_path`:

```text
<report_path>/
└── 2026-11-06/
    ├── gecko_report_07:13:05.123456.txt         # the text report
    ├── gecko_screenshot_:0_07:13:05.123456.png  # one per X11 display
    ├── camera.log                                # copies of every file in logs_dir
    ├── motor.log
    ├── acam_0002.fits                            # newest science file(s)
    └── gecko_2026-11-06_071305_1234560000.tar.gz # the bundle
```

The times in file names are the UTC time of the run. All files are placed flat in
the dated folder, so the folder structure of `logs_dir` is not kept.

## The bundle (`.tar.gz`)

The bundle is what gets emailed and is the file to share. It contains:

- the text report from this run,
- this run's screenshots,
- the newest science file(s) copied by this run,
- every file in the dated folder whose name contains `.log`.

Unpack it with:

```console
$ tar -xzf gecko_2026-11-06_071305_1234560000.tar.gz
```

:::{note}
Because logs are copied flat into the dated folder, a bundle can also contain logs
copied by **earlier runs on the same UTC day**. Two log files with the same name in
different sub-folders of `logs_dir` overwrite each other. Both are known
limitations and are planned to change.
:::

## The text report

`gecko_report_<time>.txt` has these sections, in order:

**Reported Error From User**
: The `USER:` and `MESSAGE:` given on the command line.

**System Information**
: The configured OS and version, CPU counts, per-CPU usage sampled over 3 seconds,
  CPU frequencies, CPU statistics and times, temperature sensors (where the hardware
  reports them) and memory usage. Values are printed as Python's
  [psutil](https://psutil.readthedocs.io/) reports them.

**One section per `.log` file** (headed `=====/path/to/file.log=====`)
: Lines from that log that mention `error` or `warning` and have a timestamp from
  the last 24 hours. See [`time_pattern` in the `[Report]` section](configuration.md#report) for the
  exact rules. An empty section means nothing matched.

**Science directory notes**
: Only present when a science folder was missing or empty.
