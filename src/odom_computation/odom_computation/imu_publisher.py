#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from sensor_msgs.msg import Imu


class ImuPublisher(Node):

    def __init__(self):
        super().__init__('imu_publisher')

        # Publisher for IMU data
        self.imu_pub = self.create_publisher(
            Imu,
            '/imu/data',
            10
        )

        # Publish at 20 Hz (0.05s timer)
        self.timer_period = 0.05
        self.timer = self.create_timer(
            self.timer_period,
            self.publish_imu
        )

        self.get_logger().info('IMU publisher node started')

    def publish_imu(self):
        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'imu_link'

        # Orientation (stationary or level heading: identity quaternion)
        msg.orientation.x = 0.0
        msg.orientation.y = 0.0
        msg.orientation.z = 0.0
        msg.orientation.w = 1.0

        # Angular velocity (rad/s) - zero when moving straight or stationary
        msg.angular_velocity.x = 0.0
        msg.angular_velocity.y = 0.0
        msg.angular_velocity.z = 0.0

        # Linear acceleration (m/s^2)
        # z-axis measures gravity (~9.81 m/s^2), x and y are zero at constant velocity
        msg.linear_acceleration.x = 0.0
        msg.linear_acceleration.y = 0.0
        msg.linear_acceleration.z = 9.81

        # Covariance matrices (set diagonal small values for valid sensor data)
        msg.orientation_covariance[0] = 0.01
        msg.orientation_covariance[4] = 0.01
        msg.orientation_covariance[8] = 0.01

        msg.angular_velocity_covariance[0] = 0.001
        msg.angular_velocity_covariance[4] = 0.001
        msg.angular_velocity_covariance[8] = 0.001

        msg.linear_acceleration_covariance[0] = 0.01
        msg.linear_acceleration_covariance[4] = 0.01
        msg.linear_acceleration_covariance[8] = 0.01

        self.imu_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ImuPublisher()

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
