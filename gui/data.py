from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtCore import Qt, QSize, QObject
import utils


class DataWidget(QtWidgets.QWidget):
    doubleClicked = QtCore.pyqtSignal()
    teamChanged = QtCore.pyqtSignal(int, str)  # pass column and new team
    resultChanged = QtCore.pyqtSignal(str)  # pass team

    def __init__(self, column: int, teams: QtCore.QStringListModel) -> None:
        super().__init__()
        uic.loadUi(utils.path(__file__, "data.ui"), self)
        self.column = column
        self.name.setModel(teams)

        self.name.currentTextChanged.connect(
            lambda: self.teamChanged.emit(self.column, self.name.currentText())
        )

        self.invalid.stateChanged.connect(
            lambda: self.resultChanged.emit(self.name.currentText())
        )
        self.name.currentTextChanged.connect(
            lambda: self.resultChanged.emit(self.name.currentText())
        )
        self.resultChanged.connect(lambda: self.points.setValue(0))  # TODO: setPoints

    def setTime(self, time: float):
        self.time.setValue(time)
        self.resultChanged.emit(self.name.currentText())

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
        self.name.setCurrentIndex(-1)
        self.time.setValue(0)
        self.invalid.setChecked(False)

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
