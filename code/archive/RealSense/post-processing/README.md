# Identifying Objects with an RGBD Camera and CAD Model

Using an RGBD camera and a CAD model allows to accurately identify and track objects in 3D by combining color, depth, and geometric information.

## Prerequisites

- Python 3.10 installed on your system. You can check if you have Python installed by running:
  ```bash
  python3 --version
  ```

**Note:** Some libraries required for this project may not support Python 3.11 or higher. It's recommended to use Python 3.10 for compatibility.

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