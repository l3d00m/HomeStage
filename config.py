import soundcard as sc
from homestage.devices import MqttLight

device = MqttLight("led-kueche/rgb/set", "led-kueche/brightness/set")
DEVICES = [device]

MQTT_BROKER_HOSTNAME = "192.168.0.40"
MQTT_BROKER_PORT = 1883

RECORDING_DEVICE = None
mics = sc.all_microphones(include_loopback=True)
for mic in mics:
    if 'Analog' in str(mic):
        RECORDING_DEVICE = mic
        break

if RECORDING_DEVICE is None:
    raise Exception("couldn't find microphone")
