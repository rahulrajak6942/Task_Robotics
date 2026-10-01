import os

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg_path = get_package_share_directory('diff_drive_robot')
    nav2_bringup_path = get_package_share_directory('nav2_bringup')
    slam_params_file = os.path.join(pkg_path, 'config', 'slam_params.yaml')

    # SLAM Toolbox node for mapping (with fast real-time update params)
    slam_toolbox = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        parameters=[slam_params_file],
        output='screen'
    )

    # RViz to visualize laser scan, TF, and building map
    rviz_config = os.path.join(nav2_bringup_path, 'rviz', 'nav2_default_view.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([
        slam_toolbox,
        rviz,
    ])
