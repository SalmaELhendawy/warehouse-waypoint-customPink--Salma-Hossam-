import os
import xacro
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, AppendEnvironmentVariable,
                            IncludeLaunchDescription, TimerAction)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    x_pose = LaunchConfiguration('x_pose')
    y_pose = LaunchConfiguration('y_pose')
    yaw = LaunchConfiguration('yaw')
    gz_extra = LaunchConfiguration('gz_extra')

    robot_dir = get_package_share_directory('my_robot_description')
    ros_gz_sim_dir = get_package_share_directory('ros_gz_sim')

    world = os.path.join(robot_dir, 'worlds', 'warehouse_storage.sdf')
    xacro_file = os.path.join(robot_dir, 'urdf', 'robot_description.urdf.xacro')
    bridge_yaml = os.path.join(robot_dir, 'config', 'gz_bridge.yaml')

    # Process the xacro into a plain URDF string
    robot_desc = xacro.process_file(xacro_file).toxml()

    # 1) Environment: world, models (logo, Depot) and package:// meshes
    gz_env = [
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH',
                                  os.path.join(robot_dir, 'worlds')),
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH',
                                  os.path.join(robot_dir, 'models')),
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH',
                                  str(Path(robot_dir).parent.resolve())),
    ]

    # 2) Gazebo server + world
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_dir, 'launch', 'gz_sim.launch.py')),
        launch_arguments={
            'gz_args': ['-r -s -v2 ', gz_extra, ' ', world],
            'on_exit_shutdown': 'true',
        }.items())

    # 3) robot_state_publisher
    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_desc,
        }])

    # 4) Spawn the robot (the position is set here)
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description',
                   '-name', 'custom_robot',
                   '-x', x_pose, '-y', y_pose, '-z', '0.05',
                   '-Y', yaw],
        output='screen')

    # 5) Robot bridge (clock, tf, odom, scan, joint_states, cmd_vel)
    robot_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='robot_bridge',
        parameters=[{'config_file': bridge_yaml,
                     'use_sim_time': use_sim_time}],
        output='screen')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('x_pose', default_value='-2.0'),
        DeclareLaunchArgument('y_pose', default_value='0.5'),
        DeclareLaunchArgument('yaw', default_value='0.0'),
        DeclareLaunchArgument('gz_extra', default_value=''),

        *gz_env,
        gz_sim,
        rsp,
        robot_bridge,
        # wait for the world to load before spawning
        TimerAction(period=5.0, actions=[spawn_robot]),
    ])