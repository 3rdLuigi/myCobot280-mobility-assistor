import os
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # 1. Locate the package and URDF
    pkg_workspace = get_package_share_directory('assistive_workspace_sim')
    urdf_file = os.path.join(pkg_workspace, 'urdf', 'workspace.urdf.xacro')

    # 2. Start the Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', urdf_file])}],
        output='screen'
    )

    # 3. Start the Joint State Publisher GUI (Useful later for the robot arm)
    joint_state_publisher = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen'
    )

    # 4. Launch RViz 2
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher,
        rviz
    ])