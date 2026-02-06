Gecko Initialization Guide (`-init`)
====================================

Gecko requires a configuration file before it can generate full triage reports.  
The initialization process (`-init`) walks the user through this configuration step-by-step by asking questions and saving responses into an `.ini` file.

This guide explains what happens during initialization, what information is required, and what each section of the config file controls.

Overview: What Does `-init` Do?
-------------------------------

Running::

    ./gecko -init

will prompt you with questions that need to be answered in order to create an accurate config/ini file for your reporting.

Example Inputs
--------------

Each section will include a block of text with example inputs to simplify the configuration process.

Important Sections
------------------

Primary Section
^^^^^^^^^^^^^^^

Boolean Options::

    email_alerts: false

Who will receive the report email::

    recipient_email: eng@observatory.edu

Required Directories (must exist)::

    report_path: /home/user/dir/reports
    logs_dir: /data/latest/logs/
    science_dir: /data/latest/

Notes
-----

- All paths listed in the configuration must already exist on the system. Gecko will not create them automatically.
- Ensure the email address is valid if email alerts are enabled.
- Boolean options accept only ``true`` or ``false``.
- After initialization, you can manually edit the `.ini` file if needed.

Summary
-------

The ``-init`` process is designed to simplify setup by guiding the user through necessary configurations.  
Once completed, Gecko can generate triage reports accurately using the saved configuration.
