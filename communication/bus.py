from .base import BaseComm
import can
import time


class CanBusComm(BaseComm):
    def __init__(self) -> None:
        super().__init__()
        self.can_bus = can.interface.Bus(bustype="socketcan", channel="can0", bitrate=1000000)

    def _send_msg(self, id, data, wait):
        msg = can.Message(arbitration_id=id, data=data, is_extended_id=True)
        self.can_bus.send(msg)
        time.sleep(wait)
