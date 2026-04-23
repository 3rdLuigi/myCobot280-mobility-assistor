#include <memory>
#include <thread>
#include <vector>
#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.hpp>

int main(int argc, char * argv[])
{
  // Initialize Node
  rclcpp::init(argc, argv);
  rclcpp::NodeOptions node_options;
  node_options.automatically_declare_parameters_from_overrides(true);
  node_options.append_parameter_override("use_sim_time", true);
  auto move_group_node = rclcpp::Node::make_shared("pick_and_place_node", node_options);

  // Spin up a background thread
  rclcpp::executors::SingleThreadedExecutor executor;
  executor.add_node(move_group_node);
  std::thread([&executor]() { executor.spin(); }).detach();

  // Connect to robotic arm
  static const std::string PLANNING_GROUP = "arm_group";
  moveit::planning_interface::MoveGroupInterface move_group(move_group_node, PLANNING_GROUP);

  RCLCPP_INFO(move_group_node->get_logger(), "Executing Joint Space Bypass...");

  // Define the Target Position (Joint Space)
  // This explicitly tells the 6 motors exactly what angle to go to (in radians)
  std::vector<double> joint_targets = {
    0.0,   // Joint 1: Base center
    -0.5,  // Joint 2: Lean forward slightly
    0.5,   // Joint 3: Bend elbow up
    0.0,   // Joint 4: Wrist straight
    1.57,  // Joint 5: Bend wrist 90 degrees
    0.0    // Joint 6: Flange straight
  };

  // We use setJointValueTarget instead of setPoseTarget!
  move_group.setJointValueTarget(joint_targets);

  // Plan and Execute
  moveit::planning_interface::MoveGroupInterface::Plan my_plan;
  bool success = (move_group.plan(my_plan) == moveit::core::MoveItErrorCode::SUCCESS);

  if (success) {
    RCLCPP_INFO(move_group_node->get_logger(), "Path found! Moving the arm...");
    move_group.execute(my_plan);
  } else {
    RCLCPP_ERROR(move_group_node->get_logger(), "MoveIt failed to find a safe path.");
  }

  rclcpp::shutdown();
  return 0;
}