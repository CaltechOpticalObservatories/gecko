# Gecko

**Gecko** captures the state of an instrument machine at the moment something
goes wrong, so engineers can diagnose the problem later without asking the
operator to dig up files in the middle of the night.

One command records system information, copies the logs and summarizes their
recent errors and warnings, screenshots every X11 display, grabs the newest
science images, and packages it all into a single bundle that can be emailed to
the team.

```sh
gecko -init
gecko -u "your.name" -m "Slicecam frames all zeros since 02:10 UT"
```

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} {octicon}`download` Install
:link: installation
:link-type: doc

Get Gecko onto a Linux instrument machine, including the optional screenshot
and email tools.
:::

:::{grid-item-card} {octicon}`rocket` Operator guide
:link: operator-guide
:link-type: doc

File a report when something breaks, and write a message engineers can use.
:::

:::{grid-item-card} {octicon}`gear` Configuration
:link: configuration
:link-type: doc

Every setting: log and science folders, report output, timestamps, and email.
:::

:::{grid-item-card} {octicon}`file-zip` What's in a report
:link: report-contents
:link-type: doc

The report folder, the `.tar.gz` bundle, and each section of the text report.
:::

:::{grid-item-card} {octicon}`tools` Troubleshooting
:link: troubleshooting
:link-type: doc

Error messages, missing screenshots, and errors that don't show up in the summary.
:::

:::{grid-item-card} {octicon}`terminal` Command line
:link: cli
:link-type: doc

All `gecko` options, exit codes, and environment variables.
:::

::::

## Where to go next

If you're an operator, the [operator guide](operator-guide.md) is the only page you need. If
you're setting Gecko up on a machine, start with [installation](installation.md) and then
[configuration](configuration.md). If you're upgrading a checkout from before 0.2, read
[the upgrade notes](installation.md#upgrading-from-a-source-checkout-older-than-02)
before you pull.

```{toctree}
:hidden:
:caption: Getting started

installation
operator-guide
```

```{toctree}
:hidden:
:caption: User guide

report-contents
troubleshooting
```

```{toctree}
:hidden:
:caption: Reference

cli
configuration
api
```

```{toctree}
:hidden:
:caption: Development

development
changelog
```
