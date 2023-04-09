import time
import math
from adafruit_crickit import crickit
import signal

motor = crickit.dc_motor_1

def signal_handler(sig, frame):
    motor.throttle = 0

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)


def sine_oscillation_motor(motor, period, duration):
    start_time = time.time()

    while time.time() - start_time < duration:
        current_time = time.time() - start_time
        sine_wave = math.sin(2 * math.pi * current_time / period)
        motor.throttle = sine_wave
        time.sleep(0.01)  # Adjust this value for smoother or faster motor response

# Usage example
sine_oscillation_motor(motor, period=15, duration=30)