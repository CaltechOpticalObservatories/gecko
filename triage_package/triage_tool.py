#!/usr/bin/env python3
'''
 -*- coding: utf-8 -*-
 File: triage_tool/triage_tool.py
 Author: Elijah Anakalea-Buckley
 Purpose: Triage aspects of any observatory system or instrument to provide
          a quick overview of the system health and status at any point.
          Specifically designed for execution at a crash or issue during
          observation and potencially adapts to monitoring of system health
          over time. 

NOTE:: pip install the items below;not included in python standard packages
       pip install pyscreenshot
       pip install psutil
       pip install vncdotool
       pip install pillow
                       -Elijah Anakalea-Buckley
'''
import os
import sys
import subprocess
import tarfile
import shutil
import configparser
#import smtplib
from email.message import EmailMessage
import re
from datetime import datetime, timezone, timedelta
import glob
import threading #pylint: disable=W0611
import socket #pylint: disable=W0611
import psutil
from vncdotool import api #pylint: disable=W0611

class Triagetools(object):
    """Triage tool for bug catching and error reporting"""

    def __init__(self, config: str, message:str = "", init = False):
        # Grab UTC, and load config file
        self.config_file = config
        self.utc_date = datetime.now(timezone.utc)
        self.current_utc_date = str(self.utc_date.date())
        self.utc_time = str(self.utc_date.time())
        self.cutoff = datetime.now().replace(tzinfo=None) - timedelta(hours=24)
        self.message = message
        self.time_pattern = r"^(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?)"

        # Create a ConfigParser object
        self.config = configparser.ConfigParser()

        # Load config file if called
        if init is True:
            self.initialize(self.config_file)
        else:
            self.load_config(self.config_file)

    def initialize(self, config):
        ''' Initialize and configure the application '''
        if not os.path.exists(config):
            raise FileNotFoundError(f"Configuration file {config} not found")
        self.config.read(config)

        #Iterate through prompts and populate ini file
        for section in self.config.sections():
            print(f"\n\n======  Initializing Section: {section}  ======")
            for key, value in self.config[section].items():
                if key == "initialized":
                    continue
                if key == "help_text":
                    print(value.rstrip())
                    print()  # extra blank line
                    continue
                # Remove inline comments (anything after '#')
                clean_value = value.split('#')[0].strip()
                # Prompt user; show current value if it exists
                prompt = f"Enter value for '{key}'"
                if clean_value:
                    prompt += f" (current: {clean_value})"
                prompt += ": "
                user_input = input(prompt).strip()

                # If user presses enter, keep existing value
                if user_input == "":
                    user_input = clean_value

                # Save updated value
                self.config[section][key] = user_input

        #set initialized to true for later execution and write
        self.config["System"]["initialized"] = "true"
        with open(self.config_file, "w", encoding="utf-8") as config_file:
            self.config.write(config_file)

    def load_config(self, config):
        ''' Load the configuration file '''
        if not os.path.exists(config):
            raise FileNotFoundError(f"Configuration file {config} not found")
        self.config.read(config)

        initialized = self.config.getboolean("System", "initialized")

        if not initialized:
            print("\nYou have not Initialized this application! Please run: 'gecko -init'\n")
            sys.exit(0)

        #Report Section(report file name and current UTCdate folder)
        self.email_alerts = self.config.getboolean("Report", "email_alerts")
        if self.email_alerts:
            self.target_email = self.config["Report"]["recipient_email"]
            #self.sender_email = self.config["Report"]["sender_email"]
            #self.sender_password = self.config["Report"]["sender_password"]
        self.r_path = self.config["Report"]["report_path"]
        self.log_dir = self.config["Logs"]["logs_dir"]
        self.science_dir = self.config["Logs"]["science_dir"]
        self.reports_path = f"{self.r_path}/{self.current_utc_date}"
        if not os.path.exists(f"{self.reports_path}"):
            os.mkdir(f"{self.reports_path}")
        self.report_name = f"{self.reports_path}/gecko_report_{self.utc_time}.txt"
        self.regex_pattern = r"^.*error.*$|^.*warning.*$"
        log_time_pattern = self.config["Report"]["time_pattern"]
        try:
            # document the regex
            self.time_pattern = re.compile(log_time_pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex in config: {e}")#pylint: disable=W0707

        #Machine Section
        self.cpu_threshold = self.config["Machine"]["cpu_threshold"]
        self.memory_threshold = self.config["Machine"]["memory_threshold"]

        #System
        self.os = self.config["System"]["os"]
        self.os_version = self.config["System"]["os_version"]

        #VNC information
        #self.host = self.config["VNC"]["host"]
        #self.password = self.config["VNC"]["password"]
        #temp_sessions = self.config["VNC"]["vnc_sessions"]
        #self.vnc_sessions = [int(num.strip()) for num in temp_sessions.split(',')]

        #Put main message into the file
        with open(self.report_name, 'w', encoding='utf-8') as report_file:
            report_file.write("=========Reported Error From User==========\n")
            report_file.write(f"{self.message}\n\n")

        print("Configuration loaded successfully.")

    def gather_system_info(self):
        ''' Gather system information such as CPU, memory, disk usage '''
        # All CPU data from psutil
        #Interval, usage over that period in sec; perself.cpu = separates
        cpu_detailed_usage = psutil.cpu_times_percent(interval=3, percpu=True) #List
        cpu_count_logical = psutil.cpu_count(logical=True) #Int
        cpu_count_physical = psutil.cpu_count(logical=False) #Int
        #Parse and separate frq "per cpu" to be readable
        cpu_freq = psutil.cpu_freq(percpu=True) #List
        cpu_stats = psutil.cpu_stats() #<class 'psutil._common.scpustats'>
        cpu_times = psutil.cpu_times() #<class 'psutil._common.scpustats'>
        #Parse and separate usage "per cpu" to be readable
        #Interval, usage over that period in sec; perself.cpu = separates

        # Temperature
        temps = psutil.sensors_temperatures() #Dict
        # Memory
        virtual_memory = psutil.virtual_memory() #<class 'psutil._pslinux.svmem'>
        system_str = f"{self.os} :: {self.os_version}"

        with open(self.report_name, 'a', encoding='utf-8') as file:
            file.write("\n\n=====System Information=====\n")
            file.write(f'{system_str}\n')
            file.write(f'Logical CPUs: {cpu_count_logical}\n')
            file.write(f'Physical CPUs: {cpu_count_physical}\n')
            file.write('Detailed CPU Usage:\n')
            for cpu in cpu_detailed_usage:
                file.write(str(cpu) + '\n')
            file.write('Detailed CPU freq stat:\n')
            for freq in cpu_freq:
                file.write(str(freq) + '\n')
            file.write('CPU Stats:\n')
            file.write(str( cpu_stats) + '\n')
            file.write('CPU Times:\n')
            file.write(str(cpu_times) + '\n')
            file.write('CPU Temps:\n')
            for key, value in temps.items():
                file.write(f'Key: {key}\n    Value: {value}\n')
            file.write(str(virtual_memory) + '\n')

    def take_screenshots(self):
        ''' Take screenshots of the system state on all possible monitors '''
        sessions = self.find_displays()

        if not sessions:
            print("no X11 diaplays found")
            return

        print(f"Found Sessions: {', '.join(sessions)}")

        for s in sessions:
            try:
                out = self.capture_session(s)
                print(f"Captured Session: {s} -> {out}")
            except Exception as e: #pylint: disable=W0718
                print(f"Failed to capture -> {s}: {e}")

    def capture_session(self, session):
        '''Captures a specific session through x11'''

        screenshot_name = f"gecko_screenshot_{session}_{self.utc_time}.png"
        screenshot_path = os.path.join(f"{self.reports_path}", screenshot_name)

        xwd = subprocess.Popen(
            ["xwd", "-root", "-silent", "-display", session],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            )

        convert = subprocess.Popen(
            ["convert", "xwd:-", str(screenshot_path)],
            stdin=xwd.stdout,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            )

        xwd.stdout.close()
        convert.wait()

        return screenshot_path

    def find_displays(self):
        """
         Find active X11 displays by checking /tmp/.X11-unix/X*
        """
        displays = []
        for path in glob.glob("/tmp/.X11-unix/X*"):
            display = ":" + os.path.basename(path)[1:]
            displays.append(display)
        return sorted(displays, key=lambda d: int(d[1:]))

    def gather_logs(self):
        ''' Gathers Logs from all paths to dump into tar comp. '''
        #Iterate through log paths in config file
        for subdir, dirs, files in os.walk(self.log_dir): # pylint: disable = W0612
            for file in files:
                log_file = os.path.join(subdir, file)
                #Copy over to logs folder
                try:
                    shutil.copy2(log_file,f"{self.reports_path}")
                except FileNotFoundError:
                    print(f"Error: The file at {log_file} was not found.")
                except PermissionError:
                    print(f"Error: Permission denied to access the file at {log_file}.")
                except Exception as e: # pylint: disable = W0718
                    print(f"An unexpected error occurred: {e}")

    def comb_logs(self):
        ''' Comb logs for errors and warnings '''
        #Iterate through log paths in config file
        for subdir, dirs, files in os.walk(self.log_dir): # pylint: disable = W0612
            for file in files:
                if file.lower().endswith(".log"):
                    log_path = os.path.join(subdir, file)
                    with open(self.report_name, 'a', encoding='utf-8') as file:
                        file.write(f"\n\n====={log_path}=====\n")
                    print(f"Gathering log from: {log_path}")
                    try:
                        with open(log_path, 'r', encoding='utf-8') as log_file:
                            #Search for occurances of warnings and errors sequentially
                            full_log = log_file.read()

                        #Use Regex
                        matches = (re.findall(self.regex_pattern, full_log,
                                                            re.IGNORECASE | re.MULTILINE))
                        #timeframe_matches = [
                        #        match for match in matches
                        #        if (m := re.match(self.time_pattern, match))
                        #        and datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S") >=
                        #                                                        self.cutoff]
                        timeframe_matches = [
                                match for match in matches
                                if (m := re.match(self.time_pattern, match))
                                and datetime.fromisoformat(m.group(1)) >= self.cutoff]

                        with open(self.report_name, 'a', encoding='utf-8') as report_file:
                            for match in timeframe_matches:
                                report_file.write(f"{match}\n")
                    except FileNotFoundError:
                        print(f"Error: The file at {log_path} was not found.")
                    except PermissionError:
                        print(f"Error: Permission denied to access the file at {log_path}.")
                    except Exception as e: # pylint: disable = W0718
                        print(f"An unexpected error occurred: {e}")

    def compress_report(self):
        '''Compresses report file into a tar.gz format to be emailed'''
        #Tar file and add it to message
        with tarfile.open(f"{self.reports_path}/gecko_{self.utc_date}.tar.gz", "w:gz") as tar:
            tar.add(f"{self.reports_path}", arcname=os.path.basename(f"{self.reports_path}"))

    def grab_science_image(self):
        '''Grabs most recent science image(s) to include in triage'''
        #Edit this section to fit instrument data schema
        image_dirs = [
            f"{self.science_dir}/acam",
            f"{self.science_dir}/slicecam",
            self.science_dir,
        ]
        #Iterate through dirs and grab most recent modified file,
        # which should be the most recent image taken
        for i_dir in image_dirs:
            try:
                if not os.path.exists(i_dir):
                    with open(self.report_name, 'a', encoding='utf-8') as file:
                        file.write(f"\nScience Directory does not Exist: {dir}\n")
                else:
                    files = [
                    os.path.join(i_dir, f)
                    for f in os.listdir(i_dir)
                    if os.path.isfile(os.path.join(i_dir, f))
                    ]

                    if not files:
                        raise FileNotFoundError("No files found in source directory.")

                    # Pick newest by modification time
                    newest_file = max(files, key=os.path.getmtime)

                    # Copy to destination
                    shutil.copy(newest_file, self.reports_path)
            except FileNotFoundError  as e:
                with open(self.report_name, 'a', encoding='utf-8') as file:
                    file.write(f"\nSource Directory: {i_dir}\n--{e}\n")

    def send_report(self):
        """Send the generated report to specified recipients."""

        # Create email
        msg = EmailMessage()
        msg['Subject'] = f'Gecko Report {self.utc_date}'
        msg['From'] = self.sender_email   # replace with actual sender
        msg['To'] = self.target_email     # can be comma-separated string or list

        # Email body
        msg.set_content("Please see attached report images.")

        #.txt file first
        with open(self.report_name, 'rb') as f:
            msg.add_attachment(
                f.read(),
                maintype='text',
                subtype='plain',
                filename=os.path.basename(self.report_name)
                )

        #tar.gz file next
        tar_file = f"{self.reports_path}/gecko_{self.utc_date}.tar.gz"
        with open(tar_file, 'rb') as f:
            msg.add_attachment(
                f.read(),
                maintype='application',
                subtype='gzip',
                filename=os.path.basename(tar_file)
            )

        # Attach PNG images recursively from the reports_path
        image_files = glob.glob(os.path.join(self.reports_path, '**', '*.png'), recursive=True)
        #for file in image_files:
        #    with open(file, 'rb') as fp:
        #        img_data = fp.read()
        #        filename = os.path.basename(file)
        #        msg.add_attachment(img_data, maintype='image', subtype='png', filename=filename)

        ## Send email using local SMTP server
        #with smtplib.SMTP('localhost') as sender:
        #    sender.send_message(msg)

        # Connect to Gmail SMTP server
        #with smtplib.SMTP_SSL('smtp.outlook.com', 465) as smtp:
        #    smtp.login(self.sender_email, self.sender_password)  # use an App Password
        #    smtp.send_message(msg)
        #print(f"Report sent to {self.target_email}")

        for file in image_files:
            with open(file, "rb") as fp:
                msg.add_attachment(
                    fp.read(),
                    maintype="image",
                    subtype="png",
                    filename=os.path.basename(file)
                )

        # Send using local sendmail instead of SMTP
        try:
            subprocess.run(
                ["/usr/sbin/sendmail", "-t", "-oi"],
                input=msg.as_bytes(),
                check=True
            )
            print(f"Report sent to {self.target_email}")

        except Exception as e: #pylint: disable=W0718
            print("Failed to send report:", e)
