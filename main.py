from PyQt5 import QtWidgets, uic, QtCore
from typing import List
from communication import CanBusComm, DummyComm
import sys


class DataWidget(QtWidgets.QWidget):
    doubleClicked = QtCore.pyqtSignal()

    def __init__(self, column: int, teams: QtCore.QStringListModel) -> None:
        super().__init__()
        uic.loadUi("data.ui", self)
        self.column = column
        self.name.setModel(teams)

    def setTime(self, time: float):
        self.doubleSpinBox_time.setValue(time)

    def reset(self):
        self.name.setCurrentText("")
        self.time.setValue(0)
        self.invalid.setChecked(False)

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()


class RunRow(QtCore.QObject):
    doubleClicked = QtCore.pyqtSignal()

    def __init__(
        self,
        num: int,
        teams: QtCore.QStringListModel,
        grid: QtWidgets.QGridLayout,
        row: int,
        col: int = 1,
    ) -> None:
        super().__init__()
        self.num = num
        self.widgets = [DataWidget(i, teams) for i in range(3)]
        for c, w in enumerate(self.widgets):
            grid.addWidget(w, row, col + c)
            w.doubleClicked.connect(self.doubleClicked)


class Race:
    def __init__(self, grid: QtWidgets.QGridLayout) -> None:
        self.teams = QtCore.QStringListModel()
        self.runs = [RunRow(i, self.teams, grid, 5 + i) for i in range(3)]
        for w in self.runs:
            w.doubleClicked.connect(lambda: print("doubleClicked"))

    def setTeamNames(self, names: List[str]):
        names.append("")
        self.teams.setStringList(names)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("main.ui", self)  # load .ui file

        try:
            self.track = CanBusComm()
        except Exception as e:
            print("Failed to initialize can bus: ", e)
            self.track = DummyComm()

        self.race = Race(self.gridLayout)
        self.race.setTeamNames(["1", "2", "3"])


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    app.exec_()
