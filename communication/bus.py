from .base import BaseComm
from threading import Thread
import can
import struct
import time


class CanBusComm(BaseComm):
    def __init__(self) -> None:
        super().__init__()
        self.can_bus = can.interface.Bus(bustype="socketcan", channel="can0", bitrate=1000000)
        self.receiver_thread = Thread(target=self._receive)
        self.receiver_thread.start()

    def _receive(self):
        while True:
            msg = self.can_bus.recv()
            if msg.arbitration_id == 0x1FFA2000:
                track = msg.data[0]
                (ms,) = struct.unpack(">i", msg.data[1:])
                self.received_time(track, ms / 1000)

    def _send_msg(self, id, data, wait):
        msg = can.Message(arbitration_id=id, data=data, is_extended_id=True)
        self.can_bus.send(msg)
        time.sleep(wait)
