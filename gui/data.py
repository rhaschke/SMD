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

        self.invalid.stateChanged.connect(
            lambda: self.invalidChanged.emit(self.column)
        )

    def setTime(self, time: float):
        self.time.setValue(time)

    def setTeam(self, team: str):
        self.name.setCurrentText(team)

    def result(self):
        if (
            self.invalid.isChecked()
            or self.time.value() <= 0
            and self.name.currentText() != ""
        ):
            return 0
        return self.time.value()

    def reset(self):
        self.team.setCurrentText(utils.no_team_str)
        self.time.setValue(0)
        self.invalid.setChecked(False)
