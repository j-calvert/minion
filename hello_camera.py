from pprint import *
from picamera2 import Picamera2, Preview
from libcamera import Transform
import math
import time
import pantilthat
from screeninfo import get_monitors

monitor = get_monitors()[0]
width = monitor.width
height = monitor.height
picam2 = Picamera2()
pprint(picam2.sensor_modes)
capture_scaledown = 4 # Don't needlessly try to capture at full resolution of the screen
camera_config = picam2.create_preview_configuration({"size": (int(width / capture_scaledown), int(height / capture_scaledown))})
picam2.configure(camera_config)
picam2.start_preview(Preview.QT, x=0, y=0, width=width, height=height,transform=Transform(vflip=1, hflip=1))
picam2.start()

try:
    while True:  # This will keep the preview open indefinitely
        # Get the time in seconds
        t = time.time()

        a = math.sin(2 * t) * 10 + 20
        b = math.cos(3 * t) * 10 
        
        pantilthat.pan(a)
        pantilthat.tilt(b)

        # Sleep for a bit so we're not hammering the HAT with updates
        time.sleep(0.05)
        pass
except KeyboardInterrupt:
    # Exit by pressing 'Ctrl + C'
    print("Interrupted, closing...")
finally:
    picam2.stop()  # Always ensure to stop the camera


