import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
import xacro


def generate_launch_description():
    # Paket dizini
    pkg_dir = get_package_share_directory('drone_sim')
    
    # URDF dosyasının yolunu belirle
    urdf_file = os.path.join(pkg_dir, 'urdf', 'drone.urdf.xacro')
    world_file = os.path.join(pkg_dir, 'worlds', 'drone_world.world')
    
    # XACRO'yu URDF'ye dönüştür
    doc = xacro.parse(open(urdf_file))
    xacro.process_doc(doc)
    urdf_xml = xacro.utils.process_file(urdf_file)
    
    # Launch argümanları
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    
    ld = LaunchDescription()
    
    # Gazebo'yu başlat
    gazebo_server = ExecuteProcess(
        cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_init.so', '-s', 'libgazebo_ros_factory.so', world_file],
        output='screen',
        name='gazebo_server'
    )
    
    gazebo_client = ExecuteProcess(
        cmd=['gzclient'],
        output='screen',
        name='gazebo_client',
        condition=IfCondition(LaunchConfiguration('gui', default='true'))
    )
    
    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': urdf_xml
        }]
    )
    
    # Spawn drone modeli
    spawn_drone = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'drone', '-topic', 'robot_description', '-x', '0', '-y', '0', '-z', '1'],
        output='screen'
    )
    
    ld.add_action(gazebo_server)
    ld.add_action(gazebo_client)
    ld.add_action(robot_state_publisher)
    ld.add_action(spawn_drone)
    
    return ld
