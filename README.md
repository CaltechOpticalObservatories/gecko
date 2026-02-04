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