import time
import math
from adafruit_crickit import crickit
import signal
import threading
import sys

motor = crickit.dc_motor_1

def signal_handler(sig, frame):
    motor.throttle = 0
    sys.exit()


# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

motor.throttle = -1
def main_loop():
    while not stop_event.is_set():
        print("Working...")
        # Use wait instead of sleep to allow for interrupting with Ctrl+C
        stop_event.wait(10)

# Create the stop event
stop_event = threading.Event()

# Start the main loop
main_loop()

motor.throttle = 0