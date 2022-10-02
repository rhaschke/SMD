from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtCore import Qt, QSize, QObject
import utils


class DataWidget(QtWidgets.QWidget):
    invalidChanged = QtCore.pyqtSignal()

    def __init__(self, column: int, teams: QtCore.QStringListModel) -> None:
        super().__init__()
        uic.loadUi(utils.path(__file__, "data.ui"), self)
        self.column = column
        self.team.col = column
        self.team.setModel(teams)

        self.invalid.stateChanged.connect(self.invalidChanged)

    def setTime(self, time: float):
        self.time.setValue(time)

    def setTeam(self, team: str):
        self.team.setCurrentText(team)

    def resultTime(self):
        if self.invalid.isChecked() or self.team.currentText() == utils.no_team_str:
            return 0.0
        return self.time.value()

    def reset(self):
        self.time.setValue(0)
        self.invalid.setChecked(False)
        self.points.setValue(0)
