#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException

from std_msgs.msg import Int32
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion


class OdomNode(Node):

    def __init__(self):
        super().__init__('odom_node')

        # Robot physical parameters
        self.wheel_radius = 0.065       # meters
        self.wheel_base = 0.21         # meters
        self.ticks_per_revolution = 512

        # Robot pose (x, y, theta)
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

        # Latest received ticks
        self.left_ticks = None
        self.right_ticks = None

        # Previous tick counts for delta computation
        self.prev_left_ticks = None
        self.prev_right_ticks = None

        # Velocities
        self.linear_velocity = 0.0
        self.angular_velocity = 0.0

        # Subscriptions
        self.left_sub = self.create_subscription(
            Int32,
            '/left_wheel_ticks',
            self.left_ticks_callback,
            10
        )

        self.right_sub = self.create_subscription(
            Int32,
            '/right_wheel_ticks',
            self.right_ticks_callback,
            10
        )

        # Odometry publisher
        self.odom_pub = self.create_publisher(
            Odometry,
            '/odom',
            10
        )

        # 10 Hz timer (dt = 0.1s)
        self.dt = 0.1
        self.timer = self.create_timer(
            self.dt,
            self.publish_odometry
        )

        self.get_logger().info('Odometry computation node initialized')

    def left_ticks_callback(self, msg):
        self.left_ticks = msg.data

    def right_ticks_callback(self, msg):
        self.right_ticks = msg.data

    def publish_odometry(self):
        # Calculate kinematics only if tick messages have been received
        if self.left_ticks is not None and self.right_ticks is not None:
            if self.prev_left_ticks is None:
                # First reading: store baseline to avoid sudden jump
                self.prev_left_ticks = self.left_ticks
                self.prev_right_ticks = self.right_ticks
            else:
                # Encoder tick difference
                delta_left = self.left_ticks - self.prev_left_ticks
                delta_right = self.right_ticks - self.prev_right_ticks

                self.prev_left_ticks = self.left_ticks
                self.prev_right_ticks = self.right_ticks

                # Distance travelled by each wheel (arc length)
                wheel_circumference = 2.0 * math.pi * self.wheel_radius
                left_dist = (delta_left / self.ticks_per_revolution) * wheel_circumference
                right_dist = (delta_right / self.ticks_per_revolution) * wheel_circumference

                # Differential drive motion model
                delta_dist = (left_dist + right_dist) / 2.0
                delta_theta = (right_dist - left_dist) / self.wheel_base

                # Midpoint integration for pose update
                avg_theta = self.theta + (delta_theta / 2.0)
                self.x += delta_dist * math.cos(avg_theta)
                self.y += delta_dist * math.sin(avg_theta)
                self.theta += delta_theta

                # Normalize heading to [-pi, pi]
                self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))

                # Linear and angular velocity
                self.linear_velocity = delta_dist / self.dt
                self.angular_velocity = delta_theta / self.dt

        # Prepare Odometry message
        odom = Odometry()
        odom.header.stamp = self.get_clock().now().to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'

        # Position
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0

        # Orientation: heading (theta) converted to quaternion
        odom.pose.pose.orientation.x = 0.0
        odom.pose.pose.orientation.y = 0.0
        odom.pose.pose.orientation.z = math.sin(self.theta / 2.0)
        odom.pose.pose.orientation.w = math.cos(self.theta / 2.0)

        # Velocities
        odom.twist.twist.linear.x = self.linear_velocity
        odom.twist.twist.linear.y = 0.0
        odom.twist.twist.linear.z = 0.0
        odom.twist.twist.angular.x = 0.0
        odom.twist.twist.angular.y = 0.0
        odom.twist.twist.angular.z = self.angular_velocity

        self.odom_pub.publish(odom)


def main(args=None):
    rclpy.init(args=args)
    node = OdomNode()

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
