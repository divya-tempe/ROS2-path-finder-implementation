#!/usr/bin/env python3

"""
planner_node.py

Main planner node for ras598_assignment_2.

Responsibilities:
1. Subscribe to robot state topics
2. Call /get_task once at startup
3. Publish velocity commands on /cmd_vel
4. Publish visualization markers on /planner_markers
5. Keep ROS-specific code separate from planning logic where possible
"""

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32
from visualization_msgs.msg import Marker

# -------------------------------------------------------------------
# IMPORTANT:
# Replace this import with the actual service type provided in
# your assignment or simulator package.
#
# Example:
# from my_robot_interfaces.srv import GetTask
# -------------------------------------------------------------------
# from your_interfaces_package.srv import GetTask


class PlannerNode(Node):
    """
    A simple planner node skeleton.

    This node:
    - subscribes to /ground_truth
    - subscribes to /energy_consumed
    - publishes /cmd_vel
    - publishes /planner_markers
    - calls /get_task once at startup
    """

    def __init__(self):
        super().__init__('planner_node')

        # -----------------------------
        # Internal state variables
        # -----------------------------
        self.current_pose = None
        self.energy_consumed = 0.0
        self.task_received = False

        # -----------------------------
        # Publishers
        # -----------------------------
        # Publishes robot velocity commands
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Publishes RViz visualization markers
        self.marker_pub = self.create_publisher(
            Marker,
            '/planner_markers',
            10
        )

        # -----------------------------
        # Subscribers
        # -----------------------------
        # Ground truth robot state
        self.ground_truth_sub = self.create_subscription(
            Odometry,
            '/ground_truth',
            self.ground_truth_callback,
            10
        )

        # Energy consumption feedback
        self.energy_sub = self.create_subscription(
            Float32,
            '/energy_consumed',
            self.energy_callback,
            10
        )

        # -----------------------------
        # Service client
        # -----------------------------
        # Replace GetTask with the actual service type
        self.task_client = None
        # self.task_client = self.create_client(GetTask, '/get_task')

        # -----------------------------
        # Timers
        # -----------------------------
        # One short timer to trigger the startup service call
        self.startup_timer = self.create_timer(1.0, self.startup_step)

        # Main control loop timer
        self.control_timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('Planner node started.')

    def startup_step(self):
        """
        Runs once after startup to call /get_task.

        We use a timer so the node has time to initialize before trying
        to contact the service server.
        """
        if self.task_received:
            return

        # If the actual service client is not connected yet, just warn once.
        if self.task_client is None:
            self.get_logger().warn(
                'Replace the placeholder GetTask service import/client before running.'
            )
            self.task_received = True
            self.startup_timer.cancel()
            return

        if not self.task_client.wait_for_service(timeout_sec=0.5):
            self.get_logger().info('/get_task service not available yet, waiting...')
            return

        # Create and send request once
        req = GetTask.Request()
        future = self.task_client.call_async(req)
        future.add_done_callback(self.handle_task_response)

        self.task_received = True
        self.startup_timer.cancel()
        self.get_logger().info('Called /get_task once at startup.')

    def handle_task_response(self, future):
        """
        Handles the response from /get_task.

        Replace the logging below with actual task parsing once you know
        the response fields in your assignment.
        """
        try:
            response = future.result()
            self.get_logger().info(f'Received task response: {response}')
        except Exception as exc:
            self.get_logger().error(f'Failed to call /get_task: {exc}')

    def ground_truth_callback(self, msg: Odometry):
        """
        Stores the latest robot ground-truth pose/state.

        This callback is intentionally simple so it is easy to explain.
        """
        self.current_pose = msg.pose.pose

    def energy_callback(self, msg: Float32):
        """
        Stores the latest measured energy consumption.
        """
        self.energy_consumed = msg.data

    def control_loop(self):
        """
        Main planner loop.

        For now, this starter version:
        - publishes a zero Twist
        - publishes a simple visualization marker

        Later, you can replace the command generation part with your
        actual planning logic.
        """
        # -------------------------------------------
        # 1. Compute command
        # -------------------------------------------
        cmd = Twist()

        # Starter behavior: stop the robot
        cmd.linear.x = 0.0
        cmd.angular.z = 0.0

        self.cmd_vel_pub.publish(cmd)

        # -------------------------------------------
        # 2. Publish marker
        # -------------------------------------------
        marker = self.create_status_marker()
        self.marker_pub.publish(marker)

    def create_status_marker(self) -> Marker:
        """
        Creates a simple RViz marker showing planner status.

        This is kept as a separate method so visualization code stays
        separate from control logic.
        """
        marker = Marker()
        marker.header.frame_id = 'map'
        marker.header.stamp = self.get_clock().now().to_msg()

        marker.ns = 'planner'
        marker.id = 0
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD

        # Position of marker in the world
        marker.pose.position.x = 0.0
        marker.pose.position.y = 0.0
        marker.pose.position.z = 0.2
        marker.pose.orientation.w = 1.0

        # Marker size
        marker.scale.x = 0.2
        marker.scale.y = 0.2
        marker.scale.z = 0.2

        # Marker color (green)
        marker.color.a = 1.0
        marker.color.r = 0.0
        marker.color.g = 1.0
        marker.color.b = 0.0

        return marker


def main(args=None):
    """
    Standard ROS 2 Python entry point.
    """
    rclpy.init(args=args)
    node = PlannerNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Planner node interrupted by user.')
    finally:
        node.destroy_node()
        rclpy.shutdown()
