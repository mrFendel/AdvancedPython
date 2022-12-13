import logging
from dataclasses import dataclass
from datetime import datetime

from PySide2.QtCore import QObject, Signal, QTimer

from .database import Point
from .device import Thermometer


@dataclass
class ControllerConfig:
    period: int = 1000


class ThermometerController(QObject):
    measurement = Signal(float)

    def __init__(self, device: Thermometer, config: ControllerConfig):
        super().__init__()
        self.device = device
        self.cfg = config
        self.timer = QTimer()
        temp = self.device.get()
        self.measurement.send(temp)
        logging.info(temp)

    def start(self):
        self.timer.start(self.config.period)

    def stop(self):
        self.timer.stop()

