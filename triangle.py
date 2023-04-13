import math
import numpy as np


def triangle_wave(x, period=2*math.pi, amplitude=1):
    """
    Generate a triangle wave.

    Args:
        x (float): The input value.
        period (float, optional): The period of the triangle wave. Defaults to 2*math.pi.
        amplitude (float, optional): The amplitude of the triangle wave. Defaults to 1.

    Returns:
        float: The triangle wave value at the given input.
    """
    normalized_x = x / period
    sawtooth_value = 2 * (normalized_x - math.floor(0.5 + normalized_x))
    return amplitude * (1 - 2 * abs(sawtooth_value))


# test method
if __name__ == "__main__":
    for x in np.arange(0, 10, 0.1):
        print(f"{x} {triangle_wave(x, 10)}")
              