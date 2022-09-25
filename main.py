from multiprocessing.sharedctypes import Value
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from typing import List
import os
import sys
import random


class DataWidget(QtWidgets.QWidget):
    doubleClicked = QtCore.pyqtSignal()
    teamChanged = QtCore.pyqtSignal(int, str)  # pass column and new team
    resultChanged = QtCore.pyqtSignal(str)  # pass team

    def __init__(self, column: int, teams: QtCore.QStringListModel) -> None:
        super().__init__()
        uic.loadUi("data.ui", self)
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

    def setTime(self, time: float):
        self.time.setValue(time)
        self.resultChanged.emit(self.name.currentText())

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


class RunRow(QtCore.QObject):
    doubleClicked = QtCore.pyqtSignal()
    resultChanged = QtCore.pyqtSignal(str)  # pass column

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
            w.resultChanged.connect(self.resultChanged)

    def anyTeamChanged(self, col: int, team: str):
        for w in self.widgets:
            if w.column != col and team != "" and w.name.currentText() == team:
                w.name.setCurrentIndex(-1)

    def setEnabled(self, enable: bool):
        for w in self.widgets:
            w.setEnabled(enable)

    def result(self, team: str):
        sortedResults = sorted(
            [(w.name.currentText(), w.result()) for w in self.widgets if w.result() > 0],
            key=lambda x: x[1],
        )
        print(sortedResults)
        order, _ = zip(*sortedResults)
        if team not in order or team == "":
            return 0
        return 3 - order.index(team)


class Race:
    def __init__(self, grid: QtWidgets.QGridLayout) -> None:
        self.teams = QtCore.QStringListModel()
        self.runs = [RunRow(i, self.teams, grid, 5 + i) for i in range(3)]
        for r in self.runs:
            r.resultChanged.connect(self.updateResult)

        self.points = [QtWidgets.QSpinBox() for i in range(3)]
        for col, p in enumerate(self.points):
            font = QtGui.QFont()
            font.setPointSize(16)
            p.setFont(font)
            p.setButtonSymbols(QtWidgets.QSpinBox.ButtonSymbols.NoButtons)
            p.setReadOnly(True)
            grid.addWidget(p, 3, 1 + col)

        for r in self.runs:
            for w in r.widgets:
                w.setTime(random.randint(500, 2000) / 100)

    def setTeamNames(self, names: List[str]):
        self.teams.setStringList(names)

    def setCurrentRun(self, run: int):
        for i, r in enumerate(self.runs):
            r.setEnabled(i == run)

    def updateResult(self, team: str):
        result = sum(w.result(team) for w in self.runs)
        try:
            idx = self.teams.stringList().index(team)
            self.points[idx].setValue(result)
        except ValueError:
            pass


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

        self.lineEdit().editingFinished.connect(self._onChange)

    def _onChange(self):
        text = self.currentText()
        if text not in self.model.stringList():
            proposed_completion = self.completer().currentCompletion()
            self.setCurrentText(proposed_completion)
        self.teamChanged.emit(self.col, self.currentText())


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("main.ui", self)  # load .ui file

        # Load logos
        mydir = os.path.dirname(os.path.realpath(__file__))
        self.smd.setPixmap(QtGui.QPixmap(os.path.join(mydir, "smd.png")))
        self.vde.setPixmap(QtGui.QPixmap(os.path.join(mydir, "vde.png")))

        self.race = Race(self.gridLayout)
        self.race.setCurrentRun(0)

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
            self.gridLayout.addWidget(t, 1, 1 + t.col, 1, 1)

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
