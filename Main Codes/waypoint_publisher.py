import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import time

class WaypointPublisher(Node):
    def __init__(self):
        super().__init__('waypoint_publisher')
        self.publisher = self.create_publisher(PoseStamped, '/waypoint_cmd', 10)
        
        # Define waypoints (x, y, z) with floating-point values
        self.waypoints = [
            (0.0, 0.0, 5.0),   # Takeoff position
            (10.0, 0.0, 5.0),  # Move forward
            (10.0, 10.0, 5.0), # Move right
            (0.0, 10.0, 5.0),  # Move backward
            (0.0,15.0,1000),
            (0.0, 0.0, 5.0)    # Return to start
        ]
        
        self.index = 0  # Start from first waypoint
        self.timer = self.create_timer(0.1, self.publish_waypoint)  # 10 Hz loop

        self.start_time = time.time()
        self.waypoint_duration = 7  # Hold each waypoint for 7 seconds

    def publish_waypoint(self):
        """ Publish the current waypoint at 10 Hz for 7 seconds, then switch to next. """
        elapsed_time = time.time() - self.start_time

        if elapsed_time >= self.waypoint_duration:
            # Move to the next waypoint and reset timer
            self.index = (self.index + 1) % len(self.waypoints)
            self.start_time = time.time()
            self.get_logger().info(f'Switching to next waypoint: {self.waypoints[self.index]}')

        # Publish current waypoint
        x, y, z = self.waypoints[self.index]
        waypoint = PoseStamped()
        waypoint.pose.position.x = float(x)
        waypoint.pose.position.y = float(y)
        waypoint.pose.position.z = float(z)
        
        self.publisher.publish(waypoint)
        self.get_logger().info(f'Published waypoint: x={x}, y={y}, z={z}')

def main(args=None):
    rclpy.init(args=args)
    node = WaypointPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
