# Camera Calibration - Intrinsics Parameters for Kinect v2

To carry out camera calibration with Kinect v2 using ROS-Noetic in a Docker environment, follow the detailed steps provided below:

## Obtain the ROS-Noetic Docker Image

You have two options to get the Docker image for Noetic-ROS:

### Build the image from the Dockerfile:
```bash
docker build -t noetic-ros-kinect2 .
```

### Download the image from Docker Hub:
```bash
docker pull joaonunovalente/noetic-ros-kinect2
```

### Run the Docker Container
Run the container with the following command:

```bash
docker run  -it \
            --env DISPLAY=$DISPLAY \
            -v /tmp/.X11-unix:/tmp/.X11-unix \
            -v /dev:/dev \
            --device=/dev/dri:/dev/dri \
            --ulimit nofile=1024:524288 \
            --ipc=host \
            --network host \
            --privileged \
            --name noetic-ros-kinect2-container \
            noetic-ros-kinect2
```
## Inside the Docker Container

### Update and Prepare the Environment
First, update the package list:
```bash
apt-get update
apt-get upgrade
```

### Open Terminator Terminal
Run the terminator terminal:

```bash
terminator
```
###  Prepare the ROS Script
Make the ROS script executable:
```bash
chmod +x /realsense_ros.py
```
## Run ROS Core and the Required Nodes


**Terminal 1: Start roscore**

```bash
roscore
```

**Terminal 2: Run the RealSense ROS script**

```bash
./realsense_ros.py
```

**Terminal 3: Echo the raw image topic**
```bash
rostopic echo /usb_cam/image_raw 
```

**Terminal 4: Run the camera calibration tool**
```bash
rosrun camera_calibration cameracalibrator.py --size 8x6 --square 0.1054 image:=/usb_cam/image_raw camera:=/usb_cam  --no-service-check
```
