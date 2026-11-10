# Command-line reference

```text
gecko -u USER -m MESSAGE [-c PATH]   # file a report
gecko -init [-c PATH]                # create or update the configuration
gecko --version
```

Exit status: `0` on success, `1` when the configuration is missing or invalid, `2`
for incorrect usage, `130` if interrupted with Ctrl-C.

Environment:

`GECKO_CONFIG`
: Configuration file to use when `--config` is not given.

`XDG_CONFIG_HOME`
: Base directory for the per-user configuration (default `~/.config`).

You can also run Gecko as `python -m gecko`, or as `./gecko` from a source checkout.

## Options

```{argparse}
:module: gecko.cli
:func: build_parser
:prog: gecko
:nodescription:
```
