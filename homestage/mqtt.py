import paho.mqtt.client as mqtt


# noinspection PyUnusedLocal
def on_connect(client, userdata, flags, rc):
    if rc > 0:
        raise ConnectionError('Wrong result code from mqtt server {}'.format(rc))
    print("Connected with result code {}".format(rc))


client = mqtt.Client()
client.on_connect = on_connect
client.connect("192.168.0.40",
               1883,
               10)


def update(device):
    print('r{},g{},b{} and br{}'.format(device.r, device.g, device.b, device.brightness))
    value = '{},{},{}'.format(device.r, device.g, device.b)
    client.publish("led-kueche/rgb/set", value)
    client.publish("led-kueche/brightness/set", device.brightness)
