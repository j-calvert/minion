# minion

## setting up
- Install Pi OS
- Set up networking ref: https://www.raspberrypi.com/documentation/computers/configuration.html
- Enable services: VNC, SSH, I2C
- Install updates
- git clone https://<new_token>@github.com/j-calvert/minion.git
- pip, etc: https://learn.adafruit.com/adafruit-crickit-hat-for-raspberry-pi-linux-computers/python-installation

## Running
- export DISPLAY=:0 # if remote


## Diagnosing
- i2cdetect -y 1
