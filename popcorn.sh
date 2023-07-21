#!/bin/bash

# Set the working directory
cd /home/minion/minion

sudo nice -n -20 python3 ./hello_camera.py >> autorun2.log 2>&1
echo "Done with autostart run"
