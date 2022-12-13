import logging
from logging import Handler
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Union, Optional

from PySide2.QtCore import QSettings, QSize, QPoint, Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QApplication, QPushButton, QDockWidget, QTextEdit
from appdirs import user_config_dir
from dataclasses import dataclass, field
from .config import resolve_config
from .controller import ControllerConfig, ThermometerController
from .database import SqliteConfig, Database
from .device import VirtualThermometer, USBThermometer
from .oscilloscope import OscilloscopeConfig, Oscilloscope


@dataclass
class Config:
    fake_device: bool = False
    logging_level: Union[str, int] = logging.INFO
    sqlite: SqliteConfig = field(default_factory=SqliteConfig)
    controller: ControllerConfig = field(default_factory=ControllerConfig)
    oscilloscope: OscilloscopeConfig = field(default_factory=OscilloscopeConfig)


class RunButton(QPushButton):
    def __init__(self, parent, control: ThermometerController):
        super().__init__(parent)
        self.run = False
        self.update()
        self.clicked.connect(self.onClick)
        self.control = control

    def click_btn(self):
        self.run = not self.run
        self.control.start() if self.run else self.control.stop()
        self.update()
        logging.info("Button clicked")

    def update(self):
        self.setText("Run" if self.run else "Stop")
        c = "green" if self.run else "red"
        self.setStyleSheet(f"QPushButton {{ color: {c}; }}")


class Central(QWidget):
    def __init__(self, parent, control: ThermometerController, db: Database, cfg: Config):
        super().__init__(parent)
        btn = RunButton(self, control)


class QTextEditor(Handler):
    def __init__(self, parent):
        super().__init__()
        logging.root.addHandler(self)
        self.widget = QTextEdit(parent)
        self.widget.setReadOnly(True)

    def send(self, record):
        message = self.format(record)
        self.widget.setPlainText(message)


class Main(QMainWindow):

    def __init__(self, control: ThermometerController, db: Optional[Database], cfg: Config):
        super().__init__()
        central = Central(self, control, None, cfg)
        self.setCentralWidget(central)
        self.setWindowTitle("Serious Temperature Monitor")
        self.settings = QSettings("User", "stem")
        self.resize(self.settings.value("size", QSize(300, 300)))
        self.move(self.settings.value("pos", QPoint(1024, 512)))

        docs = QDockWidget("Log", self)
        self.addDockWidget(Qt.TopDockWidgetArea, docs)
        logs = QTextEditor(self)
        docs.setWidget(logs.widget)
        toolbar = self.addToolBar('Log')
        toolbar.addAction(docs.toggleViewAction())


def run():
    config = resolve_config(Config, "config.yaml",
                            ""  # TODO(Assignment 14)
                            )
    database = Database.create_or_connect_sqlite(config.sqlite)
    # Create the Qt Application
    application = QApplication([])
    thermometer_factory = VirtualThermometer if config.fake_device else USBThermometer
    with thermometer_factory() as thermometer:
        controller = ThermometerController(thermometer, config.controller)
        # Create and show the main window
        MainWindow = Main(controller, database, config)
        MainWindow.show()
        return application.exec_()
        # Run the main Qt loop
