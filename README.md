# myCobot 280 Mobility Assistor
A robotics and computer vision project using the myCobot 280 Pi and ROS 2 Jazzy. This project aims to create an automated assistive sorting and grasping pipeline.

## Features
* **Custom Vision Pipeline:** Uses OpenCV and ArUco markers to create a flattened, top-down digital workspace.
* **Color Detection:** HSV-based masking to accurately locate and generate X/Y coordinates for target objects.
* **Digital Twin:** Full ROS 2/Gazebo simulation for safe testing of MoveIt 2 grasping logic before physical deployment.

## Tech Stack
* **OS:** Ubuntu 24.04
* **Middleware:** ROS 2 Jazzy
* **Language:** Python 3.12
* **Libraries:** OpenCV, NumPy

## Installation & Setup for myCobot
## Installation

### 1.1 Pre-Requriements

For using this package, the [Python api](https://github.com/elephantrobotics/pymycobot) library should be installed first.

```bash
pip install pymycobot --user
```

### 1.2 Package Download and Install

Install ros package in your src folder of your Colcon workspace.

```bash
$ cd ~/colcon_ws/src
# For the humble branch
$ git clone -b humble --depth 1 https://github.com/elephantrobotics/mycobot_ros2.git
# For the foxy branch
$ git clone -b foxy --depth 1 https://github.com/elephantrobotics/mycobot_ros2.git
# For the galactic branch
$ git clone -b galactic --depth 1 https://github.com/elephantrobotics/mycobot_ros2.git
$ cd ~/colcon_ws
$ vcs import src < src/warehouse_ros_mongo.repos
$ sudo apt-get update && rosdep install --from-paths src --ignore-src -y
$ colcon build
$ source ~/colcon_ws/install/setup.bash
$ sudo echo 'source ~/colcon_ws/install/setup.bash' >> ~/.bashrc
```

## Troubleshooting

1. On ROS2 Humble if slider_control does not show GUI properly, update file
   `/opt/ros/humble/lib/python3.10/site-packages/joint_state_publisher_gui/joint_state_publisher_gui.py`
   from here: https://github.com/ros/joint_state_publisher/blob/ros2/joint_state_publisher_gui/joint_state_publisher_gui/joint_state_publisher_gui.py

