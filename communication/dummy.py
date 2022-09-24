from .base import BaseComm
from time import time
from PyQt5.QtCore import QTimer
import random


class DummyComm(BaseComm):
    def __init__(self) -> None:
        super().__init__()
        self.start_time = 0
        self.track_order = None
        self.timer: QTimer = None

    def _send(self, id, *args, **kwargs):
        super()._send(id, *args, **kwargs)
        if id == 0x1FFBEA10:  # setBackText used as signal to start new race
            self.track_order = [1, 2, 3]
            random.shuffle(self.track_order)
            self.start_time = time()
            self.startTrackTimer()

    def startTrackTimer(self):
        track = self.track_order.pop()
        wait = random.randint(100, 500)  # ms
        self.timer = QTimer.singleShot(wait, lambda: self.onTrackTimer(track))

    def onTrackTimer(self, track: int):
        self.received_time.emit(track, time() - self.start_time)
        if self.track_order:
            self.startTrackTimer()  # start for next track
