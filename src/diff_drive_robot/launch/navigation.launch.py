import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg_path = get_package_share_directory('diff_drive_robot')
    nav2_bringup_path = get_package_share_directory('nav2_bringup')

    nav2_params_file = os.path.join(pkg_path, 'config', 'nav2_params.yaml')
    slam_params_file = os.path.join(pkg_path, 'config', 'slam_params.yaml')

    # SLAM Toolbox (online async mode - builds map while navigating)
    slam_toolbox = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        parameters=[slam_params_file],
        output='screen'
    )

    # Nav2 navigation stack
    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_path, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'params_file': nav2_params_file,
            'use_sim_time': 'True',
        }.items()
    )

    # RViz with nav2 default view
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
        nav2_bringup,
        rviz,
    ])
