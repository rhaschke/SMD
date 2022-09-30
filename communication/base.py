from PyQt5 import QtCore
import struct
from threading import Thread
import queue


class BaseComm(QtCore.QObject):
    """Base class for communication with Track Controller"""

    received_time = QtCore.pyqtSignal(int, float)  # signal on received time
    reset = QtCore.pyqtSignal()  # signal on reset
    __len_id = {
        0x1FFBEB00: 0x1FFBE900,  # long text
        0x1FFBEC00: 0x1FFBEA00,  # track-wise front text
        0x1FFBEC10: 0x1FFBEA10,  # track-wise back text
    }

    def __init__(self) -> None:
        super().__init__()
        self._queue = queue.SimpleQueue()
        self._running = True
        self._sender_thread = Thread(target=self._send_loop)
        self._sender_thread.start()

    def stop(self):
        self._running = False
        self._queue.put((0, 0, 0))
        self._sender_thread.join()

    def _send_loop(self):
        while self._running:
            task = self._queue.get(block=True)
            if self._running:
                self._send_msg(*task)
        print("finished send_loop")

    def _send_msg(self, id, data, wait):
        pass

    def _send(self, id, *args, fmt="<h", wait=0.005):
        data = struct.pack(fmt, *args)
        self._queue.put((id, data, wait))

    def _sendText(self, id, txt):
        print(txt)
        self._send(self.__len_id[id], len(txt), wait=0.05)
        for ch in txt:
            self._send(id, ord(ch.encode("cp437")), wait=0.003)

    def setText(self, txt):
        self._sendText(0x1FFBEB00, txt)

    def setTextTracks(self, txts, padding="^"):
        padded = [f"{padding}{txt}{padding}" for txt in txts]
        self._sendText(0x1FFBEC00, "|".join(padded))
        self._sendText(0x1FFBEC10, "|".join(reversed(padded)))

    def softReset(self):
        self._send(0x1FFB1000, 1)

    def setRounds(self, count: int):
        self._send(0x1FFB2000, count)

    def setBrightness(self, brightness: int):
        self._send(0x1FFB3000, brightness)

    def showTime(self, show: bool):
        self._send(0x1FFB3300, int(show))

    def setCountDown(self, show: bool):
        self._send(0x1FFB3400, int(show))

    def setSensorSensitivity(self, sensitivity: int):
        self._send(0x1FFB4000, sensitivity)

    def setBlockSensorTime(self, ms: int):
        self._send(0x1FFB5000, ms)

    def blockClock(self, id: int, block: bool):
        self._send(0x1FFB6100 + id * 0x100, int(block))

    def requestStatus(self):
        self._send(0x1FFBF000, 1)
