from PyQt5 import QtWidgets, uic, QtCore, QtGui
from .widgets import DataWidget
from typing import List
import utils
import random


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
        if sortedResults == []:
            return 0
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

        self.run_buttons = [QtWidgets.QPushButton(f"Lauf {run+1}:") for run in range(3)]
        for i, b in enumerate(self.run_buttons):
            grid.addWidget(b, 5 + i, 0)
        self.run_buttons[0].clicked.connect(lambda: self.setRun(0))
        self.run_buttons[1].clicked.connect(lambda: self.setRun(1))
        self.run_buttons[2].clicked.connect(lambda: self.setRun(2))

        self.points = [QtWidgets.QSpinBox() for i in range(3)]

        for col, p in enumerate(self.points):
            font = QtGui.QFont()
            font.setPointSize(16)
            p.setFont(font)
            p.setButtonSymbols(QtWidgets.QSpinBox.ButtonSymbols.NoButtons)
            p.setReadOnly(True)
            grid.addWidget(p, 3, 1 + col)

        # TEMP: set random times
        for r in self.runs:
            for w in r.widgets:
                w.setTime(random.randint(500, 2000) / 100)

    def setTeamNames(self, names: List[str]):
        self.teams.setStringList(names)
        # automatically populate runs:
        valid_names = [name for name in names if name != ""]
        l = len(valid_names)
        if l == 3:
            for r in self.runs:
                for i, w in enumerate(r.widgets):
                    w.setTeam(valid_names[i])
                valid_names.append(valid_names.pop(0))
        elif l == 2:
            for row, r in enumerate(self.runs):
                for col, w in enumerate(r.widgets):
                    if row == 2 or col == 1:
                        w.setTeam("")
            self.runs[0].widgets[0].setTeam(valid_names[0])
            self.runs[0].widgets[2].setTeam(valid_names[1])
            self.runs[1].widgets[0].setTeam(valid_names[1])
            self.runs[1].widgets[2].setTeam(valid_names[0])

    def updateResult(self, team: str):
        print("team: ", team)
        indexes = [i for i, t in enumerate(self.teams.stringList()) if t == team]
        result = sum(w.result(team) for w in self.runs)
        for idx in indexes:
            self.points[idx].setValue(result)

    def setRun(self, run: int):
        for i in range(3):
            self.runs[i].setEnabled(i == run)
            self.run_buttons[i].setEnabled(i == run + 1)

    def reset(self):
        self.setRun(-1)


class RaceControlWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi(utils.path(__file__, "ctrl.ui"), self)  # load .ui file

        # Load logos
        self.smd.setPixmap(QtGui.QPixmap(utils.path(__file__, "smd.png")))
        self.vde.setPixmap(QtGui.QPixmap(utils.path(__file__, "vde.png")))

        self.race = Race(self.gridLayout)
        self.race.reset()

        # racing_class (TODO: From Database)
        self.race_class.addItems(["UA", "UB", "AZ", "SE"])
        self.race_class.currentTextChanged.connect(self.onRaceClassChanged)

        # teammodel
        self.teamModel = QtCore.QStringListModel()

        self.onRaceClassChanged("UA")
        self.teams = [getattr(self, f"team_combobox_{i+1}") for i in range(3)]
        for i, team in enumerate(self.teams):
            team.col = i
            team.setModel(self.teamModel)
            team.teamChanged.connect(self.anyTeamChanged)

        # ensure that one team can only be in one slot at the time

    def anyTeamChanged(self, col: int, team: str):
        for i, t in enumerate(self.teams):
            if i != col and team != "" and t.currentText() == team:
                t.setCurrentText("")
        self.race.setTeamNames([t.currentText() for t in self.teams])

    def onRaceClassChanged(self, race_class: str):
        tmp_participants = [race_class + " " + str(i) for i in range(25)]
        tmp_participants.append("")
        self.teamModel.setStringList(tmp_participants)
