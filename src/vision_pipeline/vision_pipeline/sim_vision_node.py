import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class SimVisionNode(Node):
    def __init__(self):
        super().__init__('sim_vision_node')

        # Subscribe to the camera topic in Gazebo
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Convert ROS2 video to OpenCV
        self.cv_bridge = CvBridge()
        self.get_logger().info('Simulation Vision Node Started')

    def image_callback(self, msg):
        try:

            frame = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding = 'bgr8')

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            lower_red1 = np.array([0, 150, 150])
            upper_red1 = np.array([10, 255, 255])

            lower_red2 = np.array([170, 150, 150])
            upper_red2 = np.array([180, 255, 255])

            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            red_mask = mask1 + mask2

            contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                if cv2.contourArea(contour) > 50:
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

                        self.get_logger().info(f"Target found at X: {cx}, Y: {cy}")
            cv2.imshow("Simulated Vision Camera", frame)
            cv2.waitKey(1)


        except Exception as e:
            self.get_logger().error(f"ERROR: Failed to process image: {e}")

def main(args = None):
    rclpy.init(args = args)
    node = SimVisionNode()
    rclpy.spin(node)
    node.destroy_node()
    cv2.destroyAllWindows()
    rclpy.shutdown()

if __name__ == '__main__':
    main() 