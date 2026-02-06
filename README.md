# Gecko Triage tool
## What is Gecko?

Gecko is a command-line triage and diagnostics tool designed to help operators and engineers quickly collect useful debugging information when an instrument or system encounters a problem.

Instead of manually gathering logs, screenshots, and science images, Gecko automates the process and produces a single packaged report that can be reviewed or shared with the development and operations teams.

Gecko is especially useful during:

- Instrument failures or unexpected behavior  
- Software crashes or lockups  
- Data acquisition issues  
- Hardware communication problems  
- On-sky observing anomalies  

---

### What Gecko Can Collect

When run in triage mode, Gecko can automatically gather:

- System and application log files  
- Instrument-specific telemetry or diagnostic outputs  
- Screenshots of the current system state  
- Science images or recent exposure data (if configured)  
- A compressed report bundle for archiving or emailing  

---

### Why Use Gecko?

Gecko provides a consistent and repeatable way to capture critical debugging context at the moment an issue occurs. This reduces downtime and helps teams diagnose problems faster, without requiring users to manually locate and send multiple files.

Once initialized, generating a triage report is as simple as:

```bash
./gecko -u "your.name" -m "Description of the issue"
```

## Table of Contents

1. Installation
2. Setting Up Your Package
3. Installing Dependencies
4. Building Your Package
5. Publishing to PyPI

### Installation

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

## Making the executable(optional)

Run this in your terminal to create the gecko executable:

```bash
cd gecko
chmod +x gecko
```

### Filling Out Config File

You can run the command below and you will be prompted with questions to fill out the config file. Read promps and answer accordingly:

```bash
python3 gecko -init
(or ./gecko -init)
```

[Initialization Guide](INIT_GUIDE.md)

### Make Executable avaiable anywhere in the system

Symlink the executable file to bin:

```bash
sudo ln -s /path/to/repo/Gecko/gecko /usr/local/bin/gecko
```

### Generate a report

You can now generate gecko reports from any terminal on the machine! (assuming python is available globally)

```bash
./gecko -m "<insert description of bug or instrument failure here>"
```