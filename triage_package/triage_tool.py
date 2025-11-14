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
#                       -Elijah Anakalea-Buckley

import os
import tarfile
import psutil
import shutil
import configparser
import smtplib
import argparse
from email.mime.text import MIMEText
from email.message import EmailMessage
import re
from datetime import datetime, timezone, timedelta
import pyscreenshot as ImageGrab #For Wayland Primarily
from PIL import Image
from vncdotool import api
import glob

class Triage_Tools(object):

    def __init__(self, config: str, message:str):
        self.config_file = config
        # Get UTC date for log grab and report naming
        self.utc_date = datetime.now(timezone.utc)
        # Extract the date part
        self.current_utc_date = str(self.utc_date.date())
        self.utc_time = str(self.utc_date.time())
        self.cutoff = datetime.now().replace(tzinfo=None) - timedelta(hours=24)
        self.message = message

        self.time_pattern = r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"

        # Load config file
        self.load_config()

    def load_config(self):
        ''' Load the configuration file '''
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file {self.config_file} not found")
        
        # Create a ConfigParser object
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

        # Read the .ini file TODO: Change to config.ini later
        #Report Section
        if self.config["Report"]["email_alerts"].lower().strip() == "true":
            self.email_alerts = True
        else:
            self.email_alerts = False

        self.target_email = self.config["Report"]["instrument_master_email"]
        self.reports_path = self.config["Report"]["report_path"]
        #Machine Section
        self.cpu_threshold = self.config["Machine"]["cpu_threshold"]
        self.memory_threshold = self.config["Machine"]["memory_threshold"]
        #System
        self.os = self.config["System"]["os"]
        self.os_version = self.config["System"]["os_version"]
        #Logs Section of ini file
        #self.system_log = self.config["Logs"]["system"]

        #VNC information
        self.host = self.config["VNC"]["host"]
        self.password = self.config["VNC"]["password"]
        temp_sessions = self.config["VNC"]["vnc_sessions"]
        self.vnc_sessions = [int(num.strip()) for num in temp_sessions.split(',')]
        #Make report file name and current UTCdate folder
        if not os.path.exists(f"{self.reports_path}/{self.current_utc_date}"):
            os.mkdir(f"{self.reports_path}/{self.current_utc_date}")
        self.report_name = f"{self.reports_path}/{self.current_utc_date}/gecko_report_{self.utc_time}.txt"
        self.regex_pattern = r"^.*error.*$|^.*warning.*$"

        #Put main message into the file
        with open(self.report_name, 'w') as report_file:
            report_file.write("=========Reported Error From User==========\n")
            report_file.write(f"{self.message}\n\n")

        print("Configuration loaded successfully.")

    def gather_system_info(self):
        ''' Gather system information such as CPU, memory, disk usage '''
        # All CPU data from psutil
        #Interval, usage over that period in sec; perself.cpu = separates
        #TODO: Thread so other things can execute over the interval
        self.cpu_detailed_usage = psutil.cpu_times_percent(interval=5, percpu=True) #List
        self.cpu_count_logical = psutil.cpu_count(logical=True) #Int
        self.cpu_count_physical = psutil.cpu_count(logical=False) #Int
        #Parse and separate frq "per cpu" to be readable
        self.cpu_freq = psutil.cpu_freq(percpu=True) #List
        self.cpu_stats = psutil.cpu_stats() #<class 'psutil._common.scpustats'>
        self.cpu_times = psutil.cpu_times() #<class 'psutil._common.scpustats'>
        #Parse and separate usage "per cpu" to be readable
        #Interval, usage over that period in sec; perself.cpu = separates

        # Temperature
        self.temps = psutil.sensors_temperatures() #Dict
        # Memory
        self.virtual_memory = psutil.virtual_memory() #<class 'psutil._pslinux.svmem'>

        with open(self.report_name, 'a') as file:
            file.write("\n\n=====System Information=====\n")
            file.write(f'Logical CPUs: {self.cpu_count_logical}\n')
            file.write(f'Physical CPUs: {self.cpu_count_physical}\n')
            file.write(f'Detailed CPU Usage:\n')
            for cpu in self.cpu_detailed_usage:
                file.write(str(cpu) + '\n')
            file.write(f'Detailed CPU freq stat:\n')
            for freq in self.cpu_freq:
                file.write(str(freq) + '\n')
            file.write(f'CPU Stats:\n')
            file.write(str( self.cpu_stats) + '\n')
            file.write(f'CPU Times:\n')
            file.write(str(self.cpu_times) + '\n')
            file.write(f'CPU Temps:\n')
            for key, value in self.temps.items():
                file.write(f'Key: {key}\n    Value: {value}\n')
            file.write(str(self.virtual_memory) + '\n')

    def __gather_instrument_info(self):
        ''' Gather information from connected instruments '''
        #TODO:: Not required but a later feature for possibly gathering Info from Daemons

    def _take_screenshots(self):
        ''' Take screenshots of the system state on all possible monitors '''
        # Use acync to go into vnc session and take screenshots
        #TODO: Needs Testing! may switch to something else,  2 other easy implementable methods
        
        # Ensure report path ends with slash
        if not self.reports_path.endswith("/"):
            self.reports_path += "/" 

        for session in self.vnc_sessions:
            # Format session number (e.g., '1' → '01')
            session_str = f"{int(session):02d}"

            screenshot_name = f"gecko_screenshot_{session_str}_{self.utc_time}.png"
            screenshot_path = os.path.join(self.reports_path, screenshot_name)

            try:
                # Connect to host and capture screen
                with api.connect(f"{self.host}:59{session_str}", password=self.password) as vnc_client:
                    vnc_client.captureScreen(screenshot_path)
                print(f"[INFO] Saved screenshot: {screenshot_path}")

            except Exception as e:
                print(f"[ERROR] Failed to capture screenshot for session {session_str}: {e}")


    
    def gather_logs(self):
        ''' Gathers Logs from all paths to dump into tar comp. '''
        #Iterate through log paths in config file
        for log in self.config["Logs"]:
            log_path = self.config["Logs"][log]
            
            #Check that a log path exist
            if os.path.exists(log_path):
                #Copy over to logs folder
                try:
                    shutil.copy2(log_path,f"{self.reports_path}/{self.current_utc_date}")
                
                except FileNotFoundError:
                    print(f"Error: The file at {log_path} was not found.")
                except PermissionError:
                    print(f"Error: Permission denied to access the file at {log_path}.")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
            else:
                print(f"Log path {log_path} does not exist.")


    def _comb_logs(self):
        ''' Comb logs for errors and warnings '''

        #Iterate through log paths in config file
        for log in self.config["Logs"]:
            log_path = self.config["Logs"][log]
            #TODO: Put log_path into report file
            with open(self.report_name, 'a') as file:
                file.write(f"\n\n====={log_path}=====\n")
            if os.path.exists(log_path):
                print(f"Gathering log from {log_path}")
                try:
                    with open(log_path, 'r') as log_file:
                        #Search for occurances of warnings and errors sequentially
                        full_log = log_file.read()

                    #Use Regex
                    matches = (re.findall(self.regex_pattern, full_log, 
                                                        re.IGNORECASE | re.MULTILINE))
                    timeframe_matches = [
                            match for match in matches
                            if (m := re.match(self.time_pattern, match))
                            and datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S") >= self.cutoff
                        ]

                    with open(self.report_name, 'a') as report_file:
                        for match in timeframe_matches:
                            report_file.write(f"{match}\n")
                        
                        #TODO:: Populate Template
                
                except FileNotFoundError:
                    print(f"Error: The file at {log_path} was not found.")
                except PermissionError:
                    print(f"Error: Permission denied to access the file at {log_path}.")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
            else:
                print(f"Log path {log_path} does not exist.")

    def __generate_report(self):
        ''' Generate a report based on gathered data using template engine'''
        #Jinjaa template engine or cheetah template engine or something similar

    def send_report(self):
        ''' Send the generated report to specified recipients '''
        #send message using smtplib
        #format message
        msg = EmailMessage()
        msg ['Subject'] = f''
        msg['From'] = ''
        msg['To'] = self.target_email

        image_files = glob.glob(os.path.join(self.reports_path,'**', '*.png'), recursive=True)

        # TODO: test add attatchment.
        msg.add_attachment()
        #for file in image_files:
        #    with open(file,'rb') as fp:
        #         img_data = fp.read()
        #    msg.add_attachment(img_data, maintype='image', subtype='png')
        
        sender = smtplib.SMTP('localhost')
        sender.quit()
    
    def compress_report(self):

        #Tar file and add it to message
        with tarfile.open(f"{self.reports_path}/gecko_{self.utc_date}.tar.gz", "w:gz") as tar:
            tar.add(f"{self.reports_path}/{self.current_utc_date}", arcname=os.path.basename(f"{self.reports_path}/{self.current_utc_date}"))

        return

