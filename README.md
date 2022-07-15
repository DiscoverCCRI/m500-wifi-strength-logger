# m500-wifi-strength-logger
ROS package "signal strength" that is used to log RSSI wifi signal strength at different GPS coordinates (works best with an RTK enabled GPS).
Designed for use on a m500 with the ROS noetic docker image and helper scripts provided in the repo DiscoverCCRI/m500-docker.

## Install
clone the repo into the VOXL's home directory, which will be mounted into the noetic docker container when following DiscoverCCRI/m500-docker.
Once inside the noetic docker, run:
```
root@apq8096:~/yoctohome# catkin make
```
After making the package, source the package with:
```
root@apq8096:~/yoctohome# source noetic_catkin_ws/devel/setup.bash
```
Note that the above step can be replaced with sourcing the noetic_env.sh script from DiscoverCCRI/m500-docker if the noetic_catkin_ws is located in the yoctohome directory.

## Run
After the environment has been properly sourced, add a second terminal to the noetic docker container, source its environment, and then run roscore - as described in DiscoverCCRI/m500-docker.

With roscore running, you can then start the wifi-logger node:
```
root@apq8096:~/yoctohome/sdcard/logs# rosrun signal_strength wifi-logger
```
Once started, the wifi-logger node will publish RSSI wifi strength and GPS data to the rostopic wifi-logger/wifi-logs. The node will also start saving csv files containing more detailed information to whichever directory you invoke the rosrun command from. For more information on how the code works, see the comments in the wifi-logger.py file, located at m500-wifi-strength-logger/noetic_catkin_ws/src/signal_strength/scripts/wifi-logger.py

