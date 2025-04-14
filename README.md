# ROS 2 Drone Mission

This project demonstrates autonomous waypoint-based drone navigation using ROS 2, MAVROS, PX4, and Gazebo.

## Folder Structure

- `Main Codes/`: Contains ROS 2 nodes for the mission
  - `waypoint_publisher.py`
  - `drone_mission.py`

## Setup Instructions

1. Launch PX4 SITL:
   ```bash
   ./path_to_px4/Tools/simulation/gazebo-classic/sitl_multiple_run.sh -n 1


2. Launch MAVROS:
   ```bash
   ros2 launch mavros px4.launch fcu_url:="udp://:14540@127.0.0.1:14557"

3. Launch ROS2 Nodes:
    ```bash
    ros2 run your_package_name waypoint_publisher
    ros2 run your_package_name drone_mission

Current Working:

![Screenshot from 2025-04-14 10-20-54](https://github.com/user-attachments/assets/a230a74e-4f3b-472d-8f06-e2e49cde6ee7)

Future Works

In the future, this project can be expanded and improved in several ways:

    Multi-Drone Swarm Coordination:

        Extend the current system to handle multiple drones, allowing for swarm behavior.

        Implement leader-follower and coordinated waypoint navigation strategies.

    Autonomous Obstacle Avoidance:

        Integrate sensors (e.g., LiDAR, cameras) to enable real-time obstacle detection and avoidance during flight.

        Use advanced algorithms like SLAM (Simultaneous Localization and Mapping) for better navigation in unknown environments.

    Improved Flight Path Planning:

        Implement more advanced flight planning algorithms to handle dynamic environments, such as A* or RRT (Rapidly-exploring Random Trees).

        Allow for real-time rerouting based on sensor data.

    Integration with Ground Control Station:

        Add a GUI-based ground control station (GCS) to visualize drone status, flight paths, and live video feeds.

        Support mission uploads, real-time control, and telemetry monitoring via GCS.

Contributing

Contributions are welcome! Feel free to open issues or submit pull requests for new features or bug fixes.
