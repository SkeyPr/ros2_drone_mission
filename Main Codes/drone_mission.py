import rclpy
from rclpy.node import Node
from mavros_msgs.srv import CommandTOL, SetMode, CommandBool
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float64
import time

class DroneMission(Node):
    def __init__(self):
        super().__init__('drone_mission')

        self.arming_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.mode_client = self.create_client(SetMode, '/mavros/set_mode')

        self.pos_pub = self.create_publisher(PoseStamped, '/mavros/setpoint_position/local', 10)

        self.waypoint_sub = self.create_subscription(PoseStamped, '/waypoint_cmd', self.waypoint_callback, 10)

        # Altitude Subscriber
        self.altitude_sub = self.create_subscription(Float64, '/mavros/global_position/rel_alt', self.altitude_callback, 10)

        self.current_altitude = 0.0
        self.received_waypoint = None
        self.last_waypoint_time = time.time()
        self.offboard_active = False
        self.mission_start_time = None  # To track mission duration

        # Timer to continuously send waypoints (20 Hz for smoother updates)
        self.timer = self.create_timer(0.05, self.publish_waypoints)

        # Store the current position for smooth interpolation
        self.current_position = PoseStamped()
        self.current_position.pose.position.x = 0.0
        self.current_position.pose.position.y = 0.0
        self.current_position.pose.position.z = 5.0

    def altitude_callback(self, msg):
        self.current_altitude = msg.data

    def waypoint_callback(self, msg):
        """ Continuously update the target waypoint """
        self.received_waypoint = msg
        self.last_waypoint_time = time.time()
        self.get_logger().info(f'Received new waypoint: {msg.pose.position}')

    def wait_for_service(self, client):
        while not client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(f'Waiting for {client.srv_name} service...')

    def set_mode(self, mode):
        """ Ensure mode switch and wait for confirmation """
        self.wait_for_service(self.mode_client)
        req = SetMode.Request()
        req.custom_mode = mode
        future = self.mode_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        self.get_logger().info(f'Switched to mode: {mode}')

    def arm_drone(self):
        """ Ensure arming and wait for confirmation """
        self.wait_for_service(self.arming_client)
        req = CommandBool.Request()
        req.value = True
        future = self.arming_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        self.get_logger().info('Drone armed')

    def send_dummy_setpoints(self, duration=5):
        """ Send dummy setpoints for a given duration to prepare for OFFBOARD """
        self.get_logger().info(f'Sending dummy setpoints for {duration} seconds...')
        start_time = time.time()
        while time.time() - start_time < duration:
            self.pos_pub.publish(self.current_position)
            time.sleep(0.05)  # 20 Hz for smoother transitions

    def lerp(self, start, end, alpha):
        """ Linear interpolation between start and end """
        return start + (end - start) * alpha

    def smooth_move(self, current, target, alpha=0.02):
        """ Smoothly interpolate between current and target positions """
        current.pose.position.x = self.lerp(current.pose.position.x, target.pose.position.x, alpha)
        current.pose.position.y = self.lerp(current.pose.position.y, target.pose.position.y, alpha)
        current.pose.position.z = self.lerp(current.pose.position.z, target.pose.position.z, alpha)

    def publish_waypoints(self):
        """ Continuously publish the latest waypoint to maintain OFFBOARD mode """
        if not self.offboard_active:
            return  # Only send waypoints after OFFBOARD mode is active

        # Check if 60 seconds have passed
        if self.mission_start_time and (time.time() - self.mission_start_time > 60):
            self.get_logger().info("Mission time exceeded 60 seconds. Initiating landing...")
            self.land_drone()
            return

        if self.received_waypoint:
            # Smoothly interpolate towards the waypoint
            self.smooth_move(self.current_position, self.received_waypoint)

            # Publish the interpolated waypoint
            self.pos_pub.publish(self.current_position)
            self.get_logger().info(f'Smoothly moving to: {self.current_position.pose.position}')
        else:
            self.get_logger().warn('No waypoint received, holding position...')

    def land_drone(self):
        """ Switch to AUTO.LAND and stop mission """
        self.set_mode('AUTO.LAND')
        self.get_logger().info('Landing...')
        self.timer.cancel()
        rclpy.shutdown()

    def run_mission(self):
        """ Execute the mission """
        self.set_mode('AUTO.TAKEOFF')
        time.sleep(5)
        self.arm_drone()

        self.get_logger().info('Waiting before switching to OFFBOARD...')
        time.sleep(10)  # Allow time for takeoff

        # Send dummy setpoints before switching to OFFBOARD
        self.send_dummy_setpoints(duration=5)

        # Now switch to OFFBOARD mode and start sending waypoints continuously
        self.set_mode('OFFBOARD')
        self.offboard_active = True
        self.mission_start_time = time.time()  # Start mission timer
        self.get_logger().info('OFFBOARD mode activated. Mission started.')

        rclpy.spin(self)

def main(args=None):
    rclpy.init(args=args)
    node = DroneMission()
    node.run_mission()

if __name__ == '__main__':
    main()
