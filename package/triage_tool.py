#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: triage_tool/triage_tool.py
# Author: Elijah Anakalea-Buckley
# Purpose: Triage aspects of any observatory system or instrument to provide
#          a quick overview of the system health and status at any point.
#          Specifically designed for execution at a crash or issue during
#          observation and potencially adapts to monitoring of system health
#          over time. 

#NOTE:: pip install the items below;not included in python standard packages
#       pip install pyscreenshot
#       pip install psutil
#       pip install vncdotool
#       pip install pillow
#       pip install asyncvnc
#                       -Elijah Anakalea-Buckley

import os
import psutil
import configparser
import smtplib
import re
from datetime import datetime, timezone
import pyscreenshot as ImageGrab #For Wayland Primarily
import asyncio, asyncvnc
from PIL import Image
from vncdotool import api

class Triage_Tools(object):

    def __init__(self, config: str):
        self.config = config
        # Get UTC date for log grab and report naming
        self.UTC_date = datetime.now(timezone.utc)
        # Extract the date part
        self.current_utc_date = str(self.UTC_date.date())

        # Load config file
        self.load_config()

    def load_config(self):
        ''' Load the configuration file '''
        config_path = os.path.join(self.script_dir, self.config)
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file {self.config} not found in {self.script_dir}")
        
        # Create a ConfigParser object
        self.config = configparser.ConfigParser()
        self.config.read(self.config)

        # Read the .ini file TODO: Change to config.ini later
        #Report Section
        self.log_lookback_hour = self.config["Report"]["LogLookbackHours"]
        self.EmailAlerts = self.config["Report"]["EmailAlerts"]
        self.Instrument_Master_Email = self.config["Report"]["Instrument_Master_Email"]
        self.Reports_Path = self.config["Report"]["ReportPath"]
        #Machine Section
        self.CPUThreshold = self.config["Machine"]["CPUThreshold"]
        self.MemoryThreshold = self.config["Machine"]["MemoryThreshold"]
        #System
        self.OS = self.config["System"]["OS"]
        self.OS_Version = self.config["System"]["Version"]
        #Logs Section of ini file
        self.system_log = self.config["Logs"]["system"]

        #VNC information
        self.host = self.config["VNC"]["host"]
        self.user = self.config["VNC"]["user"]
        self.password = self.config["VNC"]["password"]
        self.vnc_sessions = self.config["VNC"]["vnc_sessions"]
        #Make report file name
        self.report_name = f"{self.report_path}/gecko_report_{self.current_utc_date}.txt"

        print("Configuration loaded successfully.")

    def gather_system_info(self):
        ''' Gather system information such as CPU, memory, disk usage '''
        # All CPU data from psutil
        #Interval, usage over that period in sec; perself.cpu = separates
        #TODO: Thread so other things can execute over the interval
        self.cpu_detailed_usage = psutil.cpu_times_percent(interval=5, percpu=True)
        self.cpu_count_logical = psutil.cpu_count(logical=True)
        self.cpu_count_physical = psutil.cpu_count(logical=False)
        #Parse and separate frq "per cpu" to be readable
        self.cpu_freq = psutil.cpu_freq(percpu=True)
        self.cpu_stats = psutil.cpu_stats()
        self.cpu_times = psutil.cpu_times()
        #Parse and separate usage "per cpu" to be readable
        #Interval, usage over that period in sec; perself.cpu = separates
        self.cpu_detailed_usage = psutil.cpu_times_percent(interval=5, percpu=True)

        # Temperature
        self.temps = psutil.sensors_temperatures()
        # Memory
        self.virtual_memory = psutil.virtual_memory()

    def gather_instrument_info(self):
        ''' Gather information from connected instruments '''
        #TODO:: Not required but a later feature for possibly gathering Info from Daemons

    async def take_screenshots(self):
        ''' Take screenshots of the system state on all possible monitors '''
        # Use acync to go into vnc session and take screenshots
        #TODO: Needs Testing! may switch to something else,  2 other easy implementable methods
        for session in self.vnc_sessions:
            screenshot_name = f"gecko_screenshot_{session}_{self.current_utc_date}.png"
            async with asyncvnc.connect(self.host, session, self.user, self.password) as vnc_client:
                #Take screenshot
                raw_image = await vnc_client.screenshot()

                image = Image.fromarray(raw_image)
                image.save(self.Reports_Path+ screenshot_name)
            ######vncdotool implementation
            # connect to host and session
            with api.connect(f'{self.host}::{session}', password=f"{self.password}") as vnc_client:
                vnc_client.captureScreen(self.Reports_Path+screenshot_name)


    def comb_logs(self):
        ''' Comb logs for errors and warnings '''

        #Iterate through log paths in config file
        for log in self.config["Logs"]:
            log_path = self.config["Logs"][log]
            #TODO: Put log_path into report file
            with open(self.report_name, 'w') as file:
                file.write(f"\n\n====={log_path}=====")
            if os.path.exists(log_path):
                print(f"Gathering log from {log_path}")
                try:
                    with open(log_path, 'r') as log_file:
                        #Search for occurances of warnings and errors sequentially
                        #TODO::test regex quicker find
                        full_log = log_file.read()
                        matches = (re.findeall("^.*error.*$|^.*warning.*$",
                                                        full_log, re.IGNORECASE))
                        with open(self.report_name, 'w') as report_file:
                            for match in matches:
                                report_file.write(match)
                        #########TODO:: Decide: above or bottom
                        for line in log_file:
                            #Process each line as needed using regex
                            #TODO: Process lines and add to report file
                            if(re.search("warning", line, re.IGNORECASE) or 
                                        re.search("error", line, re.IGNORECASE)):
                                with open(self.report_name, 'w') as report_file:
                                    report_file.write(line.strip())
                        
                        #TODO:: Populate Template
                
                except FileNotFoundError:
                    print(f"Error: The file at {log_path} was not found.")
                except PermissionError:
                    print(f"Error: Permission denied to access the file at {log_path}.")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
            else:
                print(f"Log path {log_path} does not exist.")

        #Parse system logs differently
        #TODO: Implement System Comb Maybe

    def generate_report(self):
        ''' Generate a report based on gathered data using template engine'''
        #Jinjaa template engine or cheetah template engine or something similar

    def send_report(self):
        ''' Send the generated report to specified recipients '''
