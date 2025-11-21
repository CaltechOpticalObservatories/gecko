# python-package-template
This is a template on how to package a simple Python project

## Table of Contents

1. Installation
2. Setting Up Your Package
3. Installing Dependencies
4. Building Your Package
5. Publishing to PyPI

## Installation

To install the package in editable mode (ideal for development), follow these steps:

### Requirements

- Python 3.7 or higher
- `pip` (ensure it's the latest version)
- `setuptools` 42 or higher (for building the package)

### 1. Clone the repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/CaltechOpticalObservatories/gecko.git
cd gecko
```

### 2. Set Up Your Python Environment

Create a virtual environment for your package:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Build Dependencies

Make sure setuptools and pip are up to date:

```bash
pip install --upgrade pip setuptools wheel
```

## Installing Dependencies

To install your package in editable mode for development, use the following command:

```bash
pip install -e .
```

This will install the package, allowing you to edit it directly and have changes take effect immediately without reinstalling.

To install any optional dependencies, such as development dependencies, use:

```bash
pip install -e .[dev]
```

### Filling Out Config File

## Logs
Logs will have the path to any and all logs you would like to comb upon execution. This includes the system logs on more . This tool with comb the last 24 hours for ERRORS or WARNINGS assuming the log timestamps are formatted as 
```bash
time_pattern = r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
```

You can change this format the the source code if you are familiar with python.
Example Log Path:
```bash
FAM_Logs = ~/LOGS/data/devices/FAM/FAM.log
```

## System
This holds the information for your Linux system and version.
-TODO: Implent cross platform utility legacy system compatability

## VNC
Your VNC credentials and all of the sessions the engineers may want screenshots of.
```bash
host = "hostname.outlook.com"
password = "Hello_Sky"
vnc_sessions = 1,2,3,4
```

## Report
Fill out contact information and path to report storage

## Executing from anywhere
Make sure your global python enviornment has all dependices and move executable into bin

