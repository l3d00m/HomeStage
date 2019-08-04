import paho.mqtt.client as mqtt
import logging

logger = logging.getLogger(__name__)


# noinspection PyUnusedLocal
class MqttController:
    def __init__(self):
        self.enabled = True
        self.client = mqtt.Client()

    def start(self, mqtt_host, mqtt_port, mqtt_enable_topic="led/music_synchro"):
        self.client.on_connect = self.on_connect
        self.client.connect(mqtt_host, mqtt_port, 10)
        self.client.subscribe(mqtt_enable_topic)
        self.client.on_message = self.on_message
        self.client.loop_start()

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        if rc > 0:
            raise ConnectionError('Wrong result code from mqtt server {}'.format(rc))
        logger.info("Connected with result code {}".format(rc))

    def on_message(self, client, userdata, msg):
        print('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))
        # Decode JSON request
        data = msg.payload.decode("utf-8")
        # Check request method
        if data == 'ON':
            self.enabled = True
            logger.info("Stage is On via MQTT")
        if data == 'OFF':
            self.enabled = False
            logger.info("Stage is Off via MQTT")

    def update(self, device):
        logger.debug('r{},g{},b{} and br{}'.format(device.r, device.g, device.b, device.brightness))
        value = '{},{},{}'.format(device.r, device.g, device.b)
        if device.r >= 0:
            self.client.publish(device.rgb_topic, value)
        if device.brightness >= 0:
            self.client.publish(device.brightness_topic, device.brightness)
