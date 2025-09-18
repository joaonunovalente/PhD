
# Camera Calibration - Intrinsics Parameters for RealSense

To carry out camera calibration with Intel RealSense using ROS-Noetic in a Docker environment, follow the detailed steps provided below:

## Obtain the ROS-Noetic Docker Image

You have two options to get the Docker image for ROS-Noetic:

### Build the image from the Dockerfile:
```bash
docker build -t <image_name> .
```

### Download the image from Docker Hub:
```bash
docker pull joaonunovalente/ros-noetic
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
            --name <name-container> \
            <image_name>
```
## Inside the Docker Container

### Update and Prepare the Environment
First, update the package list:
```bash
apt-get update
```

### Open Terminator Terminal
Run the terminator terminal:

```bash
terminator
```
###  Prepare the ROS Script
Create and make the ROS script executable:
```bash
nano realsense_ros.py
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
## Upload Image to Docker Hub
If you want to upload or update your Docker image on Docker Hub, use the following commands:

**Log in to Docker Hub:**
```bash
docker login
```
**Tag your Docker image:**
```bash
docker tag ros-noetic joaonunovalente/ros-noetic
```
**Push your Docker image:**
```bash
docker push joaonunovalente/ros-noetic
```