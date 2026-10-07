Autonomous Warehouse Waypoint Delivery Robot (Custom Robot-Pink)
---------------------------------------------------------------------
custom differential-drive robot (2 drive wheels + 2 casters, 2D LiDAR) | ROS 2: Jazzy | Simulator: Gazebo Harmonic | Stack: SLAM Toolbox, AMCL, Nav2:


1. Project overview and mission

This project builds an autonomous warehouse delivery robot with a custom robot model (URDF/xacro written from scratch). 
The robot is spawned inside a Gazebo warehouse world, maps the warehouse with SLAM Toolbox, localizes itself on the saved map with AMCL,
and navigates with Nav2 through four named warehouse locations.

---------------------------------------------------------------------
Mission:

the mission begins and ends at the Charging Station (Home).
1- Start at the Charging Station (Home)
2- Navigate to the Loading Station
3- Wait exactly 30 seconds
4- Navigate to the Storage Area
5- Navigate to the Shipping Station
6- Return to the Charging Station (Home)

Each goal is sent only after the previous goal succeeded. 
If any goal fails, the mission stops and reports the location of the failed goal.

--------------------------------------------------------------------------
| Item       | Value                                                                 |
|------------|-----------------------------------------------------------------------|
| Chassis    | 0.40 x 0.28 x 0.12 m box                                              |
| Drive      | 2 powered wheels (radius 0.06 m, separation 0.32 m) + front & rear passive casters |
| Sensor     | 2D LiDAR, 360 samples, 10 Hz, range 0.15 – 10.0 m, frame `base_scan`  |
| Plugins    | DiffDrive (publishes `odom -> base_footprint`), JointStatePublisher, gpu_lidar |
| Max speed  | 0.5 m/s linear, 1.0 rad/s angular (Nav2 limit 0.22 m/s)               |

-----------------------------------------------------------------------------------------------------------------
2. Repository and package structure
warehouse-waypoint-nav-[YOUR-NAME]/
├── my_robot_description/              # custom robot + warehouse world + Gazebo launch
│   ├── urdf/
│   │   ├── robot_description.urdf.xacro
│   │   └── robot_description.gazebo
│   ├── meshes/lidar.STL
│   ├── config/gz_bridge.yaml
│   ├── worlds/warehouse_storage.sdf
│   ├── models/
│   ├── launch/gazebo.launch.py
│   ├── CMakeLists.txt
│   └── package.xml
├── slam_toolbox_demo/
│   ├── config/slam_toolbox.yaml
│   ├── launch/<slam_launch_file>.launch.py
│   ├── CMakeLists.txt
│   └── package.xml
├── robot_navigation/
│   ├── config/
│   │   ├── amcl.yaml
│   │   ├── planner_server.yaml
│   │   ├── controller_server.yaml
│   │   ├── behavior_server.yaml
│   │   └── bt_navigator.yaml
│   ├── launch/
│   │   └── nav2_bringup.launch.py
│   ├── map/
│   │   ├── warehouse_world_map.yaml
│   │   └── warehouse_world_map.pgm
│   ├── rviz/
│   │   └── navigation.rviz
│   ├── CMakeLists.txt
│   └── package.xml
├── warehouse_waypoints/
│   ├── resource/
│   │   └── warehouse_waypoints
│   ├── warehouse_waypoints/
│   │   ├── __init__.py
│   │   └── nodes/
│   │       ├── __init__.py
│   │       └── waypoint_mission.py
│   ├── package.xml
│   ├── setup.cfg
│   └── setup.py
├── images/
└── README.md

-------------------------------------------------------------------------------------------------------------------------

| Package               | Type         | Purpose                                                                                                                        |
|-----------------------|--------------|--------------------------------------------------------------------------------------------------------------------------------|
| my_robot_description  | ament_cmake  | Robot xacro/URDF, Gazebo plugins, ROS-Gazebo bridge, warehouse world and models, and `gazebo.launch.py` (starts Gazebo with the world, robot_state_publisher, the bridge and spawns the robot) |
| slam_toolbox_demo     | ament_cmake  | SLAM Toolbox configuration and launch                                                                                          |
| robot_navigation      | ament_cmake  | Saved map, AMCL and Nav2 configuration, `nav2_bringup.launch.py` (map server, AMCL, planner, controller, behavior server, BT navigator, lifecycle manager, RViz) |
| warehouse_waypoints   | ament_python | Autonomous mission node and RViz waypoint markers                                                                              |


------------------------------------------------------------------------------------------------------------------------------

3. Workspace build instructions

```
mkdir -p ~/warehouse_waypoint_ws/src
cd ~/warehouse_waypoint_ws/src
ros2 pkg create my_robot_description, slam_toolbox_demo, robot_navigation --build-type ament_cmake
ros2 pkg create warehouse_waypoints --build-type ament_python
colcon build --packages-select my_robot_description slam_toolbox_demo robot_navigation warehouse_waypoints
source install/setup.bash
```

------------------------------------------------------------------------------------------------------------------------------

4. How to launch the custom robot inside the warehouse world

One launch file starts everything: Gazebo with the warehouse world, robot_state_publisher, the ROS-Gazebo bridge, and spawns the robot at the Charging Station.
you can launch file from terminal by
```
ros2 launch my_robot_description gazebo.launch.py
```
or from platform UI

The spawn position is set by launch arguments (defaults x_pose:=-2.0 y_pose:=0.5 yaw:=0.0):

Verify the simulation before doing anything else:
```
ros2 topic info /clock -v                              # exactly one publisher
ros2 topic hz /scan                                    # about 10 Hz
ros2 topic echo /scan --once --field header.frame_id   # base_scan
ros2 topic echo /odom --once --field child_frame_id    # base_footprint
ros2 node list | grep robot_state                      # one robot_state_publisher
gz model --list                                        # custom_robot and logo
ros2 run tf2_tools view_frames                         # odom -> base_footprint -> base_link -> base_scan
```
------------------------------------------------------------------------------------------------------------------------
5. How to map the warehouse using SLAM Toolbox

Terminal 1 :
ros2 launch slam_toolbox_demo slam_toolbox.launch.py

Terminal 2 :
rviz2

Terminal 3 :
ros2 run teleop_twist_keyboard teleop_twist_keyboard


SLAM Toolbox configuration highlights: use_sim_time: true, odom_frame: odom, base_frame: base_footprint, map_frame: map, 
scan_topic: /scan, min_laser_range: 0.15, max_laser_range: 10.0, transform_timeout: 0.5.

Drive slowly through every accessible aisle, explore the walls, corners and open areas, 
and avoid duplicated walls and large unexplored gaps. Confirm in RViz (Fixed Frame = map) 
that the robot pose moves correctly on the map and that the TF tree is map -> odom -> base_footprint.

 -----------------------------------------------------------------------------------------------------------------------

 6. How to save the warehouse map
in terminal 
ros2 run nav2_map_server map_saver_cli -f ~/warehouse_world_map

