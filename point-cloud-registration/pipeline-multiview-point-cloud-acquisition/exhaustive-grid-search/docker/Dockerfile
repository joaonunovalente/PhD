FROM nvidia/cuda:11.2.2-cudnn8-devel-ubuntu20.04

ENV TZ=Europe/Lisbon
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# INSTALL PYTHON 3.8 + PACKAGES
RUN apt-get update && \
    apt-get install -y wget software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.8 python3.8-dev python3-distutils python3-apt && \
    ln -s /usr/bin/python3.8 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

# INSTALL SYSTEM UTILITIES & DEPENDENCIES
RUN apt-get update && \
    apt-get install -y libx11-6 libgl1 nano unzip tmux git-all curl && \
    rm -rf /var/lib/apt/lists/*

# INSTALL PIP
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.8 get-pip.py && \
    rm get-pip.py && \
    python3.8 -m pip install --upgrade pip

# INSTALL PYTORCH
RUN wget https://github.com/isl-org/open3d_downloads/releases/download/torch1.8.1/torch-1.8.1-cp38-cp38-linux_x86_64.whl && \
    python3.8 -m pip install torch-1.8.1-cp38-cp38-linux_x86_64.whl && \
    rm torch-1.8.1-cp38-cp38-linux_x86_64.whl

# INSTALL PYTHON REQUIREMENTS
RUN python3.8 -m pip install \
    open3d==0.15.2 \
    ninja==1.11.1 \
    notebook==6.5.2 \
    plotly==5.11.0 \
    termcolor==1.1.0 \
    seaborn==0.13.0 \
    kaleido==0.2.1

# MAKE BASH PROMPT PRETTIER
ENV PS1="🐳 \[\e[0;34m\]EGS\[\e[0m\] \w # "

