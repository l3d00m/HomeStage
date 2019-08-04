import random
import time
from colorsys import hsv_to_rgb

import math


class Pattern:
    def update(self, devices):
        return False


class DualToneResponseFastSweep(Pattern):
    def __init__(self):
        self.color = hsv_to_rgb(math.sin(time.time() * 5) * 0.5 + 0.5, 1, 1)
        self.colors = [hsv_to_rgb(random.random(), 1, 1), hsv_to_rgb(random.random(), 1, 1)]
        self.color_index = 0

    def update(self, devices):
        self.color = self.colors[self.color_index]
        self.color_index += 1
        if self.color_index >= len(self.colors):
            self.color_index = 0

        for device in devices:
            device.r = int(255 * self.color[0])
            device.g = int(255 * self.color[1])
            device.b = int(255 * self.color[2])
            device.brightness = -1
        return False


class RainbowSweep(Pattern):
    def __init__(self):
        self.last_pulse = 0
        self.index = 0
        self.incrementor = 0.08

    def update(self, devices):
        self.index += self.incrementor
        if self.index > 1:
            self.index -= 1

        color = hsv_to_rgb(self.index, 1, 1)

        for device in devices:
            device.r = int(255 * color[0])
            device.g = int(255 * color[1])
            device.b = int(255 * color[2])
            device.brightness = -1
        return False


class MellowSweep(Pattern):
    def __init__(self, ):
        self.color = hsv_to_rgb(math.sin(time.time() * 5) * 0.5 + 0.5, 1, 1)
        self.colors = [hsv_to_rgb(random.random(), 1, 1), hsv_to_rgb(random.random(), 1, 1)]
        self.color_index = 0

    def update(self, devices):
        self.color = self.colors[self.color_index]
        self.color_index += 1
        if self.color_index >= len(self.colors):
            self.color_index = 0

        for device in devices:
            device.r = int(255 * self.color[0])
            device.g = int(255 * self.color[1])
            device.b = int(255 * self.color[2])
            device.brightness = -1
        return False


class Blink(Pattern):
    def __init__(self):
        self.brightness = False

    def update(self, devices):
        self.brightness ^= True

        for device in devices:
            device.brightness = int(255 * self.brightness)
            device.r = -1

        return False
