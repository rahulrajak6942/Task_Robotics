from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='odom_computation',
            executable='odom_node',
            name='odom_node',
            output='screen'
        ),
        Node(
            package='odom_computation',
            executable='imu_publisher',
            name='imu_publisher',
            output='screen'
        )
    ])
