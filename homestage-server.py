import logging
import config
from homestage.controller import AudioState, HomeStage


def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s (%(levelname)s) [%(name)s] %(message)s",
                        datefmt="%H:%M:%S")
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    listener = AudioState(config.RECORDING_DEVICE)
    stage = HomeStage(config.DEVICES, listener)

    listener.start()
    stage.start()


if __name__ == '__main__':
    main()
