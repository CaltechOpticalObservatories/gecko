"""Command-line interface for Gecko."""
import argparse
import sys

from . import __version__
from .config import ensure_config_file, init_target_path, resolve_config_path
from .triage import GeckoConfigError, Triagetools

DESCRIPTION = """\
Gecko Triage Tool

Collect system information and logs, take screenshots, grab the latest science
images, and package them into a compressed report (optionally emailed).

  1) Configure Gecko once per machine:   gecko -init
  2) File a report when something breaks: gecko -u "your.name" -m "what happened"
"""


def build_parser():
    """Build the ``gecko`` argument parser."""
    parser = argparse.ArgumentParser(
        prog="gecko",
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-init",
        "--initialize",
        action="store_true",
        help="Create or update the configuration file by answering prompts.",
    )
    parser.add_argument(
        "-m",
        "--message",
        help="Description of the issue, e.g. 'Lost connection to the slicecam at 02:13 UT'.",
    )
    parser.add_argument(
        "-u",
        "--user",
        help="Your name, so the report can be followed up.",
    )
    parser.add_argument(
        "-c",
        "--config",
        metavar="PATH",
        help="Configuration file to use. Defaults to $GECKO_CONFIG, "
        "~/.config/gecko/gecko.ini, or /etc/gecko/gecko.ini (first that exists).",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def run_initialize(config):
    """Run the interactive configuration prompts."""
    target = ensure_config_file(init_target_path(config))
    Triagetools(config=str(target), init=True)
    print(f"\nInitialization complete! Settings saved to {target}")
    print('You can now file a report with:\n  gecko -u "your.name" -m "your issue message"\n')
    return 0


def run_report(config, user, message):
    """Run the full triage workflow and return an exit code."""
    config_path = resolve_config_path(config)
    if not config_path.is_file():
        raise GeckoConfigError(
            f"No configuration file found at {config_path}. Run: gecko -init"
        )
    user_message = f"USER: {user}\nMESSAGE: {message}"
    gecko = Triagetools(config=str(config_path), message=user_message)
    print(f"Running triage workflow for user: {user}\nwith the message: {message}\n")
    gecko.gather_system_info()
    gecko.gather_logs()
    gecko.comb_logs()
    gecko.take_screenshots()
    gecko.grab_science_image()
    gecko.compress_report()
    if gecko.email_alerts:
        gecko.send_report()
    print(f"\nTriage workflow complete! Report: {gecko.tar_filename}")
    return 0


def main(argv=None):
    """Entry point for the ``gecko`` command. Returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.initialize and (args.message or args.user):
        parser.error("-init cannot be combined with --message/--user")

    try:
        if args.initialize:
            return run_initialize(args.config)
        if args.message and args.user:
            return run_report(args.config, args.user, args.message)
    except (GeckoConfigError, FileNotFoundError) as exc:
        print(f"gecko: error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\ngecko: cancelled", file=sys.stderr)
        return 130

    print(
        "gecko: error: you need to include a user and a message in your report.\n"
        "example:\n"
        "  gecko -u 'Steven.B' -m 'One of the channels looked weird and I was "
        "unable to get any more data'",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
