# Intel RealSense Camera with Python on Linux

This repository contains a guide and example code to help you set up and use an Intel RealSense camera with Python on a Linux system.

### Step 1: Install the Python Wrapper

Ensure you have `pip` installed and install the **pyrealsense2** package.
```sh
pip install pyrealsense2
```

**Note:** It works with Python 3.6-3.11

### What about Python 3.12?

Good luck!

## Create a virtual environment

To create a virtual environment using Python's venv module, run the following command:

```bash
python3 -m venv .venv
```

## Activate the virtual environment

Activate the virtual environment by running:

```bash
source .venv/bin/activate
```

##  Install the required packages

Once the virtual environment is activated, install the necessary dependencies listed in the requirements.txt file:

```bash
pip install -r requirements.txt
```