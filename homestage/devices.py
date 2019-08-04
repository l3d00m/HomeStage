class MqttLight:
    def __init__(self, rgb_topic, brightness_topic):
        self.rgb_topic = rgb_topic
        self.brightness_topic = brightness_topic
        self.r = -1
        self.g = -1
        self.b = -1
        self.brightness = -1
