from launch import LaunchDescription
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder

def generate_launch_description():
    # This pulls in the URDF, SRDF, and kinematics from your config package
    moveit_config = (
        MoveItConfigsBuilder("firefighter", package_name="mycobot_280_moveit2")
        .to_moveit_configs()
    )

    pick_and_place_node = Node(
        package="arm_controller",
        executable="pick_and_place",
        output="screen",
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            {"use_sim_time": True} # Since you are using Gazebo
        ],
    )

    return LaunchDescription([pick_and_place_node])