# LiDAR + Nav2 Roadmap for SYNCHROFLEET_AMR

This roadmap is tailored to the current repository layout and current gaps.

## 1) What exists already

- Differential-drive base model and ros2_control integration (`my_bot_description`, `my_bot_controller`).
- Basic Nav2 package scaffold (`my_bot_nav2`) with minimal parameters.
- Gazebo launch and spawn flow.

## 2) What is missing for autonomous LiDAR navigation

1. A LiDAR sensor link/joint + Gazebo sensor plugin in URDF/Xacro.
2. Laser data pipeline (`/scan`) and TF chain (`map -> odom -> base_footprint -> base_link -> lidar_link`).
3. SLAM package integration (e.g., `slam_toolbox`) for online map creation.
4. Correct Nav2 bringup launch usage (include the Nav2 launch file, do not execute it as a node).
5. Full Nav2 parameterization for:
   - local/global costmaps
   - controller/planner/recovery behaviors
   - AMCL for localization on saved map
6. Operational launch stack for two modes:
   - Mapping mode (SLAM + teleop)
   - Navigation mode (localization + planner/controller)

## 3) Recommended package additions

Install runtime dependencies:

```bash
sudo apt install \
  ros-$ROS_DISTRO-nav2-bringup \
  ros-$ROS_DISTRO-navigation2 \
  ros-$ROS_DISTRO-slam-toolbox \
  ros-$ROS_DISTRO-twist-mux \
  ros-$ROS_DISTRO-teleop-twist-keyboard
```

Update `package.xml` dependencies so the repo is self-describing.

## 4) URDF/Xacro: add LiDAR

Add a `lidar_link` and fixed joint from `base_link` in `my_bot.urdf.xacro`, then add Gazebo ray sensor config in `my_bot_gazebo.xacro`.

Minimum concept:

- `lidar_link` around 0.15–0.25 m above base.
- 360 deg scan, range ~0.12–12.0 m.
- ROS topic `/scan`, frame `lidar_link`.

For Gazebo (classic/ignition variants), ensure plugin publishes `sensor_msgs/msg/LaserScan` and that ROS bridge/plugin is configured if needed by your simulator variant.

## 5) TF and odometry requirements

Nav2/SLAM need stable transforms:

- `odom -> base_footprint` from diff drive controller.
- `base_footprint -> base_link` fixed joint (already present).
- `base_link -> lidar_link` fixed joint (to add).
- During mapping: `slam_toolbox` publishes `map -> odom`.
- During localization: `amcl` publishes `map -> odom`.

Do **not** let both SLAM and AMCL publish `map -> odom` simultaneously.

## 6) Mapping mode launch

Create `my_bot_nav2/launch/mapping.launch.py` that composes:

1. robot description + simulation launch
2. controller launch
3. `slam_toolbox` online async launch
4. RViz preconfigured with map, scan, TF
5. Optional teleop node

Typical mapping workflow:

```bash
ros2 launch my_bot_nav2 mapping.launch.py
# drive robot around
ros2 run nav2_map_server map_saver_cli -f ~/maps/warehouse_a
```

## 7) Navigation mode launch

Create `my_bot_nav2/launch/navigation.launch.py`:

1. robot + controller launch
2. map_server loading saved YAML map
3. AMCL localization
4. Nav2 planner/controller/behavior tree stack

Use `IncludeLaunchDescription` to include `nav2_bringup/bringup_launch.py` with launch arguments:

- `map:=/path/to/map.yaml`
- `params_file:=.../config/nav2_params.yaml`
- `use_sim_time:=true`
- `autostart:=true`

## 8) Nav2 params baseline

Expand `nav2_params.yaml` significantly:

- `local_costmap` plugins:
  - obstacle_layer (LaserScan `/scan`)
  - inflation_layer
- `global_costmap` plugins:
  - static_layer
  - obstacle_layer
  - inflation_layer
- `controller_server`:
  - DWB or RPP controller tuned for your wheelbase
- `planner_server`:
  - Smac2D or NavFn
- `bt_navigator`: default behavior tree XML
- `behavior_server` recovery behaviors

Costmap starting points:

- resolution: 0.05
- inflation_radius: 0.35–0.55
- robot_radius: slightly larger than real chassis footprint

## 9) Critical fix in current Nav2 launch

Current `my_bot_nav2/launch/nav2.launch.py` executes `bringup_launch.py` as a `Node`. This is incorrect and should be replaced with `IncludeLaunchDescription` targeting Nav2's launch file.

## 10) Validation checklist

Use these checks after wiring everything:

```bash
ros2 topic list | rg 'scan|cmd_vel|odom|map'
ros2 topic echo /scan --once
ros2 run tf2_tools view_frames
ros2 lifecycle get /amcl
ros2 lifecycle get /controller_server
```

In RViz2 verify:

- Scan aligns with robot geometry.
- Costmaps are populating from obstacles.
- `2D Pose Estimate` localizes robot on map.
- `2D Goal Pose` executes fully and reaches goal.

## 11) Multi-world portability ("any exported world")

To make navigation portable across worlds:

1. Keep robot frame conventions and sensor frames constant.
2. Save one map per world/environment.
3. Use per-world Nav2 parameter overlays only for:
   - inflation radius
   - obstacle persistence
   - planner tolerances
4. Launch with arguments:
   - `world:=...`
   - `map:=...`
   - `params:=base + world overlay`

This gives predictable behavior while letting you tune for tight or open spaces.
