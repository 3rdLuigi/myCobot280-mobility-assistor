import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder

def generate_launch_description():
    # Load your specific myCobot MoveIt config
    moveit_config = (
        MoveItConfigsBuilder("firefighter", package_name="mycobot_280_moveit2")
        .to_moveit_configs()
    )

    # Start your existing Gazebo Simulation (which handles RSP and spawning)
    gazebo_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("assistive_workspace_sim"), "launch", "sim_world.launch.py")
        )
    )

    # The Clock Bridge (The magic fix for the timing error)
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )

    # Start MoveGroup with use_sim_time explicitly enforced
    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            {"use_sim_time": True}, 
        ],
    )

    # Spawn the Joint State Broadcaster
    jsb_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    # Spawn the Arm Controller
    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_group_controller"], 
    )

    return LaunchDescription([
        gazebo_sim,
        clock_bridge,
        # Start controllers 3 seconds after Gazebo
        TimerAction(period=3.0, actions=[jsb_spawner, arm_controller_spawner]),
        
        # Start MoveIt 6 seconds after Gazebo (gives controllers time to load)
        TimerAction(period=6.0, actions=[move_group_node])
    ])