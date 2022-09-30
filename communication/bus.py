from .base import BaseComm
from threading import Thread
import can
import struct
import time


class CanBusComm(BaseComm):
    def __init__(self) -> None:
        self.can_bus = can.interface.Bus(bustype="socketcan", channel="can0", bitrate=1000000)
        super().__init__()
        self.receiver_thread = Thread(target=self._receive_loop)
        self.receiver_thread.start()

    def _receive_loop(self):
        while self._running:
            msg = self.can_bus.recv(timeout=0.1)
            if not self._running:
                break
            if msg.arbitration_id == 0x1FFA2000:
                track = msg.data[0]
                (ms,) = struct.unpack(">i", msg.data[1:])
                self.received_time(track, ms / 1000)
        print("finished receive_loop")

    def _send_msg(self, id, data, wait):
        msg = can.Message(arbitration_id=id, data=data, is_extended_id=True)
        self.can_bus.send(msg)
        time.sleep(wait)

    def stop(self):
        super().stop()
