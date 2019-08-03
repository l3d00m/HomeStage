import logging
import threading
from typing import Optional
from homestage import mqtt

import aubio

from homestage.model import Media, Section
from homestage.patterns import *

logger = logging.getLogger(__name__)


class AudioState:
    media = Media()
    current_tempo = 0

    def __init__(self, mic, sample_rate=44100, fft_size=1024):
        self.mic = mic
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.hop_size = self.fft_size // 2
        self.tempo = aubio.tempo("default", self.fft_size, self.hop_size, self.sample_rate)
        self.current_tempo = 0
        self.beat = False
        self.enabled = False
        self.index = False

    def start(self):
        threading.Thread(target=self._run).start()

    def _run(self):
        with self.mic.recorder(samplerate=self.sample_rate, channels=1) as mic:
            while True:
                signal = mic.record(numframes=self.hop_size)
                if self.enabled:
                    signal = signal.flatten().astype('float32', casting='same_kind')
                    self.beat = self.tempo(signal)[0] > 0
                    self.current_tempo = self.tempo.get_bpm()
                    if self.beat:
                        self.index ^= True


class PatternController:
    media: Media
    section: Optional[Section]

    def __init__(self, state: AudioState):
        self.state = state
        self.pattern = RainbowSweep(state)
        self.media = Media()
        self.section = None
        self.bank = [
            lambda: DualToneResponseFastSweep(self.state),
            lambda: RainbowSweep(self.state),
            lambda: MellowSweep(self.state),
            lambda: BrightnessSweep(self.state),
        ]

    def get_pattern(self, media) -> Pattern:
        position = media.position
        change = False

        if self.media != media:
            self.media = media
            change = True

        if position:
            section = media.analysis.sections.at(position)
            if self.section != section:
                self.section = section
                change = True
        else:
            self.section = None

        if change:
            self.pattern = random.choice(self.bank)()
            logger.info("Change of pattern triggered")

        return self.pattern


class HomeStage:
    def __init__(self, devices, state: AudioState):
        self.devices = devices
        self.state = state
        self.controller = PatternController(state)
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
                logger.info("Output disableds")
                self._enabled = False
                self.state.enabled = self._enabled

    def run(self):
        while True:
            if self.enabled:
                if self.last_index is not self.state.index:
                    self.last_index = self.state.index
                    print("beat recognize")
                    pattern = self.controller.get_pattern(self.state.media)
                    pattern.update(self.devices)
                    for device in self.devices:
                        mqtt.update(device)
                time.sleep(0.001)
            else:
                time.sleep(1)
