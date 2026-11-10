# Operator guide

Run Gecko **as soon as you notice a problem**, before restarting software or
power-cycling hardware. It records what the machine looked like at that moment.

## File a report

Open a terminal on the instrument machine and run:

```console
$ gecko -u "your.name" -m "what happened"
```

Both parts are required:

`-u`, `--user`
: Your name, so engineers know who to follow up with.

`-m`, `--message`
: A description of the problem. Put it in quotes.

A run takes a few seconds, most of it spent sampling CPU usage. When it finishes,
Gecko prints where the bundle was saved:

```text
Triage workflow complete! Report: /home/obs/gecko_reports/2026-11-06/gecko_2026-11-06_071305_1234560000.tar.gz
```

If email alerts are configured, the bundle is also sent to the engineering team.
Nothing else is required of you.

## Writing a useful message

Engineers read your message long after the event. A good one answers:

- **What did you see?** The exact error text, or what looked wrong.
- **When?** The UT time, or which exposure or observation it was during.
- **What were you doing?** The last command, script or GUI action before the problem.
- **What have you tried?** For example, "retried twice, same result".

```console
$ gecko -u "Steven.B" -m "Slicecam frames all zeros since ~02:10 UT. Started after \
  changing the exposure to 30 s. Retried twice. ACAM looks normal."
```

## If Gecko itself reports an error

| Message | What to do |
|---|---|
| `No configuration file found ... Run: gecko -init` | Gecko hasn't been set up for your account. Ask your instrument administrator, or see [installation](installation.md). |
| `... has not been initialized` | Same as above. |
| `you need to include a user and a message` | Add both `-u` and `-m`. |
| `gecko: command not found` | Gecko isn't on your `PATH`. Ask your administrator. |

Anything else: see [troubleshooting](troubleshooting.md). Include the full error text
when you report the problem.
