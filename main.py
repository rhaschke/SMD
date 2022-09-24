from PyQt5 import QtWidgets, uic, QtCore, QtGui
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
        self.name.setCurrentIndex(-1)
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
                w.name.setCurrentIndex(-1)


class TeamCompleter(QtWidgets.QCompleter):
    def __init__(self, teams: QtCore.QStringListModel):
        self.teams = teams

    def update(self, word: str):
        pass


class Race:
    def __init__(self, grid: QtWidgets.QGridLayout) -> None:
        self.teams = QtCore.QStringListModel()
        self.runs = [RunRow(i, self.teams, grid, 5 + i) for i in range(3)]
        for w in self.runs:
            w.doubleClicked.connect(lambda: print("doubleClicked"))

    def setTeamNames(self, names: List[str]):
        self.teams.setStringList(names)


class TeamBox(QtWidgets.QComboBox):
    teamChanged = QtCore.pyqtSignal(int, str)

    def __init__(self, col: int, model: QtCore.QStringListModel):
        super().__init__()
        self.col = col
        self.model = model
        self.setModel(model)
        self.setEditable(True)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.setFont(font)
        self.setCurrentIndex(-1)
        completer = self.completer()
        completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        completer.setFilterMode(QtCore.Qt.MatchContains)
        completer.setModel(model)

        self.currentTextChanged.connect(self._onChange)

    def _onChange(self, text: str):

        # TODO: validate
        self.teamChanged.emit(self.col, self.currentText())


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("main.ui", self)  # load .ui file

        self.race = Race(self.gridLayout)
        self.race.setTeamNames(["1", "2", "3"])

        # racing_class (TODO: From Database)
        self.race_class.addItems(["UA", "UB", "AZ", "SE"])
        self.race_class.currentTextChanged.connect(self.onRaceClassChanged)

        # teammodel
        self.teamModel = QtCore.QStringListModel()

        self.onRaceClassChanged("UA")
        # self
        self.teams = [TeamBox(i, self.teamModel) for i in range(3)]
        for t in self.teams:
            t.teamChanged.connect(self.anyTeamChanged)
            self.gridLayout.addWidget(t, 4, 1 + t.col, 1, 1)

        # ensure that one team can only be in one slot at the time

    def anyTeamChanged(self, col: int, team: str):
        for i, t in enumerate(self.teams):
            if i != col and team != "" and t.currentText() == team:
                t.setCurrentText("")
        self.race.setTeamNames(list(set([t.currentText() for t in self.teams])))

    def onRaceClassChanged(self, race_class: str):
        tmp_participants = [race_class + " " + str(i) for i in range(25)]
        tmp_participants.append("")
        self.teamModel.setStringList(tmp_participants)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    app.exec_()
