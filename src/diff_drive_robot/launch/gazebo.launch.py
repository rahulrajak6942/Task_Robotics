import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro


def generate_launch_description():

    pkg_path = get_package_share_directory('diff_drive_robot')
    gazebo_ros_path = get_package_share_directory('gazebo_ros')

    # Process xacro to get robot description
    xacro_file = os.path.join(pkg_path, 'urdf', 'robot.urdf.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()

    # World file
    world_file = os.path.join(pkg_path, 'worlds', 'obstacles.world')

    # Robot state publisher (publishes TF from URDF)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True
        }],
        output='screen'
    )

    # Launch Gazebo with custom world
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_path, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': world_file,
        }.items()
    )

    # Spawn the robot in Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'diff_drive_robot',
            '-x', '0.0',
            '-y', '-2.0',
            '-z', '0.05',
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
    ])
