#!/bin/bash

# Set the working directory
cd /home/minion/minion

# Run the script with high priority in a loop
# while true; do
    sudo nice -n -20 python3 ./pan_image_with_motors.py >> autorun.log 2>&1
    sleep 1
# done
echo "Done with autostart run"
