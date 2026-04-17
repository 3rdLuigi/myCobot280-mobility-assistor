import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    #Locate packages
    pkg_workspace = get_package_share_directory('assistive_workspace_sim')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    urdf_file = os.path.join(pkg_workspace,'urdf','workspace.urdf.xacro')
    world_file = os.path.join(pkg_workspace,'worlds','workspace.sdf')
    
    robot_state_publisher_node = Node(
        package = 'robot_state_publisher',
        executable = 'robot_state_publisher',
        parameters = [{'robot_description' : Command(['xacro ', urdf_file])}],
        output = 'screen'
    )
    #Launch Gazebo Harmonic in custom world
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments = {'gz_args': f'-r {world_file}'}.items(),
    )

    #Spawn workspace into Gazebo
    spawn_entity = Node(
        package = 'ros_gz_sim',
        executable = 'create',
        arguments = ['-name', 'assistive_workspace','-topic', 'robot_description','-z','0.0'],
        output = 'screen',
    )

    #Bridge between Gazebo Camera and ROS2
    bridge = Node(
        package = 'ros_gz_image',
        executable = 'image_bridge',
        arguments = ['/camera/image_raw'],
        output = 'screen'
    )

    return LaunchDescription([
        AppendEnvironmentVariable(
            name = 'GZ_SIM_RESOURCE_PATH',
            value = os.path.join(get_package_share_directory('mycobot_description'), '..')
        ),
        robot_state_publisher_node,
        gazebo,
        spawn_entity,
        bridge
    ])