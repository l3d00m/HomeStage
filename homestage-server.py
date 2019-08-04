import logging
import config
from homestage.controller import AudioState, HomeStage
from homestage.mqtt import MqttController


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s.%(msecs)03d (%(levelname)s) [%(name)s] %(message)s",
                        datefmt="%H:%M:%S")
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    listener = AudioState(config.RECORDING_DEVICE)
    mqtt_controller = MqttController()
    stage = HomeStage(config.DEVICES, mqtt_controller, listener)

    listener.start()
    mqtt_controller.start(config.MQTT_BROKER_HOSTNAME, config.MQTT_BROKER_PORT)
    stage.start()


if __name__ == '__main__':
    main()
