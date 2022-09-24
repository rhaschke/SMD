from PyQt5 import QtWidgets, uic, QtCore
from typing import List
import sys


class DataWidget(QtWidgets.QWidget):
    doubleClicked = QtCore.pyqtSignal()
    teamChanged = QtCore.pyqtSignal(int, str)  # pass column and new team

    def __init__(self, column: int, teams: QtCore.QStringListModel) -> None:
        super().__init__()
        uic.loadUi("data.ui", self)
        self.column = column
        self.name.setModel(teams)

        self.name.currentTextChanged.connect(
            lambda: self.teamChanged.emit(self.column, self.name.currentText())
        )

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
            w.teamChanged.connect(self.anyTeamChanged)

    def anyTeamChanged(self, col: int, team: str):
        for w in self.widgets:
            if w.column != col and team != "" and w.name.currentText() == team:
                w.name.setCurrentText("")


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

        self.race = Race(self.gridLayout)
        self.race.setTeamNames(["1", "2", "3"])

        # teammodel
        tmp_participants = ["UA " + str(i) for i in range(25)]
        tmp_participants.append("")
        self.teamModel = QtCore.QStringListModel(tmp_participants)

        self.teams = [self.team1, self.team2, self.team3]
        for i, team in enumerate(self.teams):
            team.setModel(self.teamModel)
            team.setCurrentText("")

        # do not put in loop! lambda can't work with changing i...
        self.teams[0].currentTextChanged.connect(lambda text: self.anyTeamChanged(0, text))
        self.teams[1].currentTextChanged.connect(lambda text: self.anyTeamChanged(1, text))
        self.teams[2].currentTextChanged.connect(lambda text: self.anyTeamChanged(2, text))

    def anyTeamChanged(self, col: int, team: str):
        for i, t in enumerate(self.teams):
            if i != col and team != "" and t.currentText() == team:
                t.setCurrentText("")
                print("change ", i, col, team)
        self.race.setTeamNames(list(set([t.currentText() for t in self.teams])))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    app.exec_()
