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
#                       -Elijah Anakalea-Buckley

import pathlib
import os
import pyautogui
import subprocess
import psutil
import configparser
import smtplib
import re
from datetime import datetime, timezone
import pyscreenshot as ImageGrab

class Triage_Tools(object):

    def __init__(self, config: str):
        self.config = config
        # Get UTC date for log grab and report naming
        self.UTC_date = str(datetime.utcnow().date())

        # Load config file
        self.load_config()

    def load_config(self):
        ''' Load the configuration file '''

    def gather_logs(self):
        ''' Gather logs from specified sources '''

    def gather_system_info(self):
        ''' Gather system information such as CPU, memory, disk usage '''

    def gather_instrument_info(self):
        ''' Gather information from connected instruments '''

    def take_screenshots(self):
        ''' Take screenshots of the system state on all possible monitors '''

    def comb_logs(self):
        ''' Comb logs for errors and warnings '''

    def generate_report(self):
        ''' Generate a report based on gathered data using template engine'''
        #Jinjaa template engine or cheetah template engine or something similar

    def send_report(self):
        ''' Send the generated report to specified recipients '''


def main():