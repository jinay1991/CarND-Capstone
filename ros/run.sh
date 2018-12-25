sudo apt-get update 
sudo apt-get install ros-kinetic-dbw-mkz-msgs
catkin_make
source devel/setup.bash
roslaunch launch/styx.launch
