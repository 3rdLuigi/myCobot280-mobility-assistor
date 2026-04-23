from launch import LaunchDescription
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder

def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("firefighter", package_name="mycobot_280_moveit2").to_moveit_configs()
    
    config_dict = moveit_config.to_dict()
    
    config_dict.update({"use_sim_time": True})

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[config_dict],
    )

    return LaunchDescription([move_group_node])