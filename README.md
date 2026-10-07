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
Start at the Charging Station (Home)
Navigate to the Loading Station
Wait exactly 30 seconds
Navigate to the Storage Area
Navigate to the Shipping Station
Return to the Charging Station (Home)

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
```
ros2 run nav2_map_server map_saver_cli -f ~/warehouse_world_map
```

This produces both files, which are kept in slam_toolbox_demo/map/:

warehouse_world_map.yaml (resolution 0.05, origin [-5.955, -7.089, 0])
<img width="636" height="292" alt="Screenshot 2026-10-07 210351" src="https://github.com/user-attachments/assets/92a3c3eb-9a6e-4914-af5b-d8ab3d418f55" />

-----------------------------------------------------------------------------------------------------------------------------
7. How to launch and test AMCL localization
 
AMCL and the map server are started by amcl.launch.py . SLAM Toolbox must be closed, otherwise both publish map -> odom.

in terminal :
```
ros2 launch robot_navigation amcl.launch.py
```

check:
ros2 lifecycle get /map_server         # active
ros2 lifecycle get /amcl               # active
ros2 topic echo /amcl_pose --once      # close to the real robot pose
ros2 run tf2_ros tf2_echo map base_footprint
ros2 run tf2_tools view_frames         # map -> odom -> base_footprint


In RViz (Fixed Frame = map) the following displays are used: Map, TF, RobotModel, LaserScan and ParticleCloud.
1.Set the correct initial pose (initial_pose: 0, 0, 0 in amcl.yaml, valid because the robot is spawned at the map origin, or 2D Pose Estimate).
2.Confirm the LiDAR scan aligns with the map walls.
3.Confirm the particle cloud converges around the robot.
4.Move the robot and verify localization remains stable.
5.Confirm /amcl_pose updates while the robot moves.
6.Localization recovery is demonstrated by displacing the pose estimate and correcting it with 2D Pose Estimate.

-------------------------------------------------------------------------------------------------------------------------------------------------

8. How to launch the complete Nav2 system

in terminal:
```
ros2 launch robot_navigation nav2_bringup.launch.py

```
check :
```
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 lifecycle get /planner_server
ros2 lifecycle get /controller_server
ros2 lifecycle get /behavior_server
ros2 lifecycle get /bt_navigator
```
All cycles must be Active.

Test before automation:

Display the global costmap and local costmap, the global plan and local plan, the robot, the laser scan, the map and the particles.
Set one manual 2D Goal Pose in RViz and confirm the robot plans and reaches the goal safely.
then send autonomous goal by send_goal python script

------------------------------------------------------------------------------

Main Nav2 configuration for the custom robot:

Navigation Parameters:

| Parameter        | Value                                                                 |
|------------------|-----------------------------------------------------------------------|
| Footprint (costmaps) | rectangle [[0.20, 0.18], [0.20, -0.18], [-0.20, -0.18], [-0.20, 0.18]] (chassis 0.40 x 0.28 plus the wheels at y = +/-0.18) |
| Local planner    | DWB, max_vel_x: 0.22, max_vel_theta: 1.0                              |
| Global planner   | NavFn                                                                 |
| Inflation        | radius 0.30 m, cost scaling 3.0                                       |
| Local costmap    | 6 x 6 m rolling window, LiDAR range 3.5 / 3.0 m                       |
| Global costmap   | LiDAR range 10.0 / 8.0 m                                              |
| AMCL             | laser_min_range: 0.15, laser_max_range: 10.0                          |



Waypoints:

| ID   | Name                   | x (m) | y (m) | yaw (rad) | Role                                |
|------|------------------------|-------|-------|-----------|-------------------------------------|
| HOME | Charging Station (Home)| 0.00  | 0.00  | 0.00      | Mission start and final destination |
| 01   | Loading Station        | 2.50  | -0.50 | 0.00      | Wait here for 30 seconds            |
| 02   | Storage Area           | 11.00 | 1.60  | 0.00      | Second navigation goal              |
| 03   | Shipping Station       | 8.00  | -2.00 | 0.00      | Third navigation goal               |


----------------------------------------------------------------------------------------------------------------------------

10. Mission route:

Charging Station (Home) -> Loading Station -> wait 30 s -> Storage Area -> Shipping Station -> Charging Station (Home)

---------------------------------------
The mission starts only after Nav2 and AMCL are active and the robot is localized at the Charging Station (the node publishes the Home initial pose and waits with waitUntilNav2Active). It then sends one NavigateToPose goal at a time and waits for each Nav2 result before sending the next goal. If a goal fails, the node stops the mission and reports the failed location.

 Terminal 1: Nav2 + AMCL + RViz
ros2 launch robot_navigation nav2_bringup.launch.py

 Terminal 2: mission
ros2 run warehouse_waypoints waypoint_mission 

-------------------------------------------
11. RViz waypoint-marker behavior

The mission node publishes all waypoints as a visualization_msgs/msg/MarkerArray on the /waypoint_markers topic.

.Each waypoint is drawn as a pin (floor ring, stem and head) with a heading arrow, placed at its stored pose in the map frame.
.The station name is displayed above every marker.
.Blue means an inactive waypoint.
.Green means the active navigation goal. Only the active goal is green, and it also gets a soft glow halo.
.The MarkerArray is republished every time the active goal changes.

| Moment                          | Home | Loading | Storage | Shipping |
|---------------------------------|------|---------|---------|----------|
| Mission start (waiting for Nav2)| 🟩   | 🟦      | 🟦      | 🟦       |
| Heading to Loading Station      | 🟦   | 🟩      | 🟦      | 🟦       |
| Heading to Storage Area         | 🟦   | 🟦      | 🟩      | 🟦       |
| Heading to Shipping Station     | 🟦   | 🟦      | 🟦      | 🟩       |
| Returning to Home (last goal)   | 🟩   | 🟦      | 🟦      | 🟦       |
| Mission complete (arrived Home) | 🟦   | 🟦      | 🟦      | 🟦       |


-----------------------------------------------------------------------------------------

12. Required terminal output

Output of the mission node (ros2 run warehouse_waypoints waypoint_mission:
Example - real results 
<img width="683" height="197" alt="Screenshot 2026-10-07 174838" src="https://github.com/user-attachments/assets/048cafb7-2931-497d-a125-f1928000bef3" />

If a goal fails, the node stops the mission and prints:
[ERROR] [basic_navigator]: [FAILED] Goal  at (x=<x>, y=<y>) ended with result: FAILED. Mission stopped.

-------------------------------------------------------------------------------------------------------
13. Problems encountered and their solutions

| # | Problem                                                   | Cause                                                                 | Solution                                                                 |
|---|-----------------------------------------------------------|------------------------------------------------------------------------|--------------------------------------------------------------------------|
| 1 | The warehouse logo did not appear when the world was started from the UI | Gazebo started by the UI does not have the models folder in `GZ_SIM_RESOURCE_PATH`, so `model://etgah_logo` could not be resolved | The world, models and robot meshes now live in `my_robot_description`, and `gazebo.launch.py` starts Gazebo itself with the correct resource paths |
| 2 | LiDAR mesh appeared late or not at all                    | `package://my_robot_description/meshes/...` was not resolvable by Gazebo | The parent folder of the package share directory is added to `GZ_SIM_RESOURCE_PATH` in the launch file |
| 3 | `robot_state_publisher` and the spawn failed with the original launch file | The xacro was read as plain text, the executable name and package were wrong, and the file name was misspelled | The launch file expands the xacro with `xacro.process_file(...)`, uses the `robot_state_publisher` package, and spawns from the `robot_description` topic |
| 4 | Odometry drift and jerky turning with the first design    | Four wheels driven as skid steer slip while turning                    | The robot was redesigned as a differential drive with two drive wheels and two passive casters, with higher wheel friction and lower acceleration limits |
| 5 | Scan frame did not match the Nav2 configuration           | The LiDAR link was named `lidar_link`                                  | Renamed to `base_scan` (also `gz_frame_id`) to follow the same frame contract as TurtleBot3 |
| 6 | AMCL started with the scan shifted from the walls         | The map was built with the robot spawned at a different point than the launch default, so (0, 0) in the map did not match the spawn | The spawn point was set to the point used while mapping (`x_pose:=-2.0 y_pose:=0.5`), so `initial_pose: 0, 0, 0` is correct |
| 7 | Costmap footprint did not match the robot                 | The footprint was copied from an earlier, larger robot design          | Footprint recalculated from the xacro: chassis 0.40 x 0.28 plus the wheels at y = +/-0.18 |
| 8 | Message Filter dropping message and jumping TF            | Duplicate `/clock` publisher, `use_sim_time` missing on some nodes, stale Gazebo processes | One `/clock` bridge, `use_sim_time: true` on every node, kill old processes before a restart |
| 9 | Timed out while waiting for action server to acknowledge goal request | The BT server timeout was too small under CPU load                     | `default_server_timeout` raised to 100 and `debug_trajectory_details` set to False |

------------------------------------------------------------------------------------------------------------------------------------------------------------------

14. Screenshots

Custom robot in the warehouse world (Gazebo):

<img width="959" height="491" alt="Screenshot 2026-10-05 200344" src="https://github.com/user-attachments/assets/6be2469e-253d-4fa7-ad1a-7a25284bd2c3" />

Mapping (SLAM Toolbox):

<img width="710" height="251" alt="Screenshot 2026-10-08 005636" src="https://github.com/user-attachments/assets/29ddf3de-61c5-4c36-b079-8edb522d4f98" />

Saved warehouse map:
<img width="476" height="236" alt="Screenshot 2026-10-07 210359" src="https://github.com/user-attachments/assets/ebf401f9-846f-49d3-a0b4-9e9f1751bf02" />

<img width="263" height="145" alt="Screenshot 2026-10-05 204546" src="https://github.com/user-attachments/assets/30a11939-4f6c-4329-9fb5-f8c0c22f88fe" />

AMCL localization (scan aligned with the walls, particle cloud converged):

<img width="368" height="212" alt="Screenshot 2026-10-06 233526" src="https://github.com/user-attachments/assets/793e3d41-2206-416e-98f1-b241fe89588e" />

Navigation: global and local costmaps:

<img width="291" height="206" alt="Screenshot 2026-10-08 010139" src="https://github.com/user-attachments/assets/0ae8675e-714f-442c-8069-61091c8a174b" />
<img width="340" height="197" alt="global" src="https://github.com/user-attachments/assets/99e6c6df-720b-488f-9a65-ee59b87a1553" />


Navigation: global plan and local plan
<img width="313" height="218" alt="Screenshot 2026-10-07 030927" src="https://github.com/user-attachments/assets/8c7b14ca-f202-4779-8fbb-d90323450bc5" />
<img width="356" height="260" alt="Screenshot 2026-10-08 010443" src="https://github.com/user-attachments/assets/be404fe7-d42f-4f27-ad7a-74ee8a63b5f2" />

All named waypoint markers:

<img width="364" height="264" alt="Screenshot 2026-10-08 010618" src="https://github.com/user-attachments/assets/2e6eeaf7-dd9f-4cd4-bc37-fe3c89bf3eb2" />
<img width="304" height="193" alt="Screenshot 2026-10-08 010634" src="https://github.com/user-attachments/assets/a4a90416-3bc0-44d5-95e4-52e12eaa525a" />


Active goal in green
<img width="323" height="217" alt="Screenshot 2026-10-08 010753" src="https://github.com/user-attachments/assets/faf0ab5f-d0c4-403c-8a26-23f27f78756e" />

Other waypoints in blue
<img width="347" height="210" alt="Screenshot 2026-10-08 010831" src="https://github.com/user-attachments/assets/719adc12-566f-4fb5-8459-e1955a44d6b0" />

/waypoint_markers topic in RViz
didn't record the topic but it has been showed inrviz.
<img width="470" height="289" alt="Screenshot 2026-10-07 173914" src="https://github.com/user-attachments/assets/d45a4f0d-69d4-4222-81ec-a96d429b7298" />


------------------------------------------------------------------------------------------------------------------------------------

15. Demonstration video
    
Narrated video of the complete project (custom robot spawn in the warehouse, SLAM Toolbox mapping, AMCL, Nav2, the complete autonomous mission and the RViz waypoint markers






