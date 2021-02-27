import logging
import threading
from typing import Optional

import aubio

from homestage.model import Media, Section
from homestage.patterns import *

logger = logging.getLogger(__name__)


class AudioState:
    media = Media()
    current_tempo = 0

    def __init__(self, mic, sample_rate=44100, fft_size=512):
        self.mic = mic
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.hop_size = self.fft_size // 2
        # initialize aubio, default for fft size is 512 and hop_size 256
        self.tempo = aubio.tempo("default", self.fft_size, self.hop_size, self.sample_rate)
        self.current_tempo = 0
        self.beat = False
        self.enabled = False
        self.index = False

    def start(self):
        threading.Thread(target=self._run).start()

    def _run(self):
        # The music analysis has to be done asynchronous to not leave out single parts
        with self.mic.recorder(samplerate=self.sample_rate, channels=1) as mic:
            while True:
                signal = mic.record(numframes=self.hop_size)
                if self.enabled:
                    signal = signal.flatten().astype('float32', casting='same_kind')
                    # tempo(signal) returns an array with a single value indicating if there just was a beat
                    self.beat = self.tempo(signal)[0] > 0
                    self.current_tempo = self.tempo.get_bpm()
                    if self.beat:
                        # this variable will be polled further down
                        self.index ^= True
                        print("beat")


class PatternController:
    media: Media
    section: Optional[Section]

    def __init__(self, state: AudioState):
        self.state = state
        self.pattern = RainbowSweep()
        self.media = Media()
        self.section = None
        self.bank = [
            lambda: DualToneResponseFastSweep(),
            lambda: RainbowSweep(),
            lambda: MellowSweep(),
            lambda: Blink(),
        ]

    def get_pattern(self, media) -> Pattern:
        # make the pattern random when the song changes
        # position = media.position
        # change = False
        #
        # if self.media != media:
        #     self.media = media
        #     change = True
        #
        # if position:
        #     section = media.analysis.sections.at(position)
        #     if self.section != section:
        #         self.section = section
        #         change = True
        # else:
        #     self.section = None
        #
        # if change:
        #     self.pattern = random.choice(self.bank)()
        #     logger.info("Change of pattern triggered")

        return self.pattern


# noinspection PyAttributeOutsideInit
class HomeStage:
    def __init__(self, devices, mqtt_controller, state: AudioState):
        self.devices = devices
        self.state = state
        self.controller = PatternController(state)
        self.mqtt_controller = mqtt_controller
        self.lock = threading.RLock()
        self._enabled = False
        self.last_index = False

    def start(self):
        self.enabled = True
        threading.Thread(target=self.run).start()

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        with self.lock:
            if enabled and not self._enabled:
                logger.info("Output enabled")
                self._enabled = True
                self.state.enabled = self._enabled

            if not enabled and self._enabled:
                logger.info("Output disabled")
                self._enabled = False
                self.state.enabled = self._enabled
                # reset brightness level
                # for device in self.devices:
                #     device.brightness = 255
                #     self.mqtt_controller.update(device)

    def run(self):
        while True:
            # Set enabled state based on MQTT
            self.enabled = self.mqtt_controller.enabled
            # only do logic if a new part was analyzed by aubio (and a new beat was detected)
            if self.last_index is not self.state.index:
                self.last_index = self.state.index
                # get current pattern (changes on song change)
                pattern = self.controller.get_pattern(self.state.media)
                # use the pattern to update the device state
                pattern.update(self.devices)
                # only update when enabled so the beat detection works as soon as it is enabled because it still analyzes in bg
                if self.enabled:
                    # update the devices depending on their type
                    for device in self.devices:
                        self.mqtt_controller.update(device)
            # sleep for a short amount to allow the other thread being executed
            time.sleep(0.001)
