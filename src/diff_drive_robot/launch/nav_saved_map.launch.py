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
    map_file = os.path.join(pkg_path, 'maps', 'my_map.yaml')

    # Map server (loads the saved map instead of SLAM)
    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        parameters=[{
            'use_sim_time': True,
            'yaml_filename': map_file,
        }],
        output='screen'
    )

    # AMCL for localization on the saved map
    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        parameters=[{
            'use_sim_time': True,
            'base_frame_id': 'base_footprint',
            'odom_frame_id': 'odom',
            'global_frame_id': 'map',
            'scan_topic': '/scan',
            'set_initial_pose': True,
            'initial_pose.x': 0.0,
            'initial_pose.y': -2.0,
            'initial_pose.z': 0.0,
            'initial_pose.yaw': 0.0,
        }],
        output='screen'
    )

    # Lifecycle manager for map_server and amcl
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['map_server', 'amcl'],
        }],
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

    # RViz
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
        map_server,
        amcl,
        lifecycle_manager,
        nav2_bringup,
        rviz,
    ])
