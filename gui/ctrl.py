from inspect import trace
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from .widgets import RunWidget, DataWidget, TeamGroup, TeamComboBox
from communication import CanBusComm, DummyComm
from typing import List
import utils
import numpy as np
from collections import OrderedDict
from utils.debug import traced


class RunRow(TeamGroup):
    resultChanged = QtCore.pyqtSignal()

    def __init__(
        self,
        teams: QtCore.QStringListModel,
        grid: QtWidgets.QGridLayout,
        row: int,
        col: int = 1,
    ) -> None:
        super().__init__()
        self.widgets = [DataWidget(i, teams) for i in range(3)]
        for c, w in enumerate(self.widgets):
            grid.addWidget(w, row, col + c)
            w.invalidChanged.connect(self.resultChanged)
        self.setGroup([w.team for w in self.widgets])

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
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        self.teamsModel = QtCore.QStringListModel()
        self.current_run = -1

        # Create top row's team comboboxes
        self.teams = TeamGroup([parent.findChild(TeamComboBox, f"team_combobox_{i+1}") for i in range(3)])
        for i, team in enumerate(self.teams):
            team.col = i
            team.setModel(self.teamsModel)
            team.teamChanged.connect(lambda: self.configureRuns([t.currentText() for t in self.teams]))

        # Create widgets row-wise for each run
        self.run_rows = [RunRow(self.teamsModel, parent.gridLayout, 5 + i) for i in range(3)]
        for r in self.run_rows:
            r.resultChanged.connect(self.updateResult)

        # "Lauf x" widgets in first column
        self.run_widgets = [RunWidget(i) for i in range(3)]
        for i, w in enumerate(self.run_widgets):
            parent.gridLayout.addWidget(w, 5 + i, 0)
            w.activate.connect(self.setRun)

        # total points widgets
        self.points = [parent.findChild(QtWidgets.QSpinBox, f"points_{i+1}") for i in range(3)]

        try:
            self.comm = CanBusComm()
        except Exception as e:
            print("Failed to initialize can bus: ", e)
            self.comm = DummyComm()

        self.comm.received_time.connect(self.onReceivedTime)

    def setTeamNames(self, names: List[str]):
        assert len(names) in [2, 3]
        # store 3 team names + no_team_str in teamsModel
        names = list(OrderedDict.fromkeys(names + [f"{utils.no_team_str}"]))
        self.teamsModel.setStringList(names)
        for i, team_combo in enumerate(self.teams):
            team_combo.setCurrentText(names[i])

        self.configureRuns(names[:3])  # configure all RunRows
        self.setRun(-1)  # disable all runs
        self.run_widgets[0].setEnabled(True)

    def configureRuns(self, names):
        """configure run rows based on team names"""
        assert len(names) == 3
        names = np.array(names)
        valid = names != utils.no_team_str
        num_valid = np.count_nonzero(valid)

        for run in range(3):
            if run >= num_valid:
                for i in range(3):
                    self.run_rows[run][i].setCurrentIndex(-1)
                continue

            tracks = np.arange(3)  # initialize to 0 1 2
            # rotate valid tracks only, use +run to rotate in opposite direction
            rotate = np.mod(np.arange(num_valid) - run, num_valid)
            tracks[valid] = tracks[valid][rotate]  # assign new ordering
            for i in range(3):
                self.run_rows[run][i].setCurrentText(names[tracks[i]])

    def updateResult(self, team: str):
        indexes = [i for i, t in enumerate(self.teams.stringList()) if t == team]
        result = sum(w.result(team) for w in self.run_rows)
        for idx in indexes:
            self.points[idx].setValue(result)

    def setRun(self, run: int):
        # Enable/disable widgets
        for i in range(3):
            self.run_rows[i].setEnabled(i <= run)
            self.run_widgets[i].setEnabled(i <= run)
        self.current_run = run
        if run >= 0:  # Prepare run
            # Block clock on unused tracks
            for i, team in enumerate(self.run_rows[run].teams):
                self.comm.blockClock(i, team.currentText() == utils.no_team_str)
            # Send team names to display
            self.comm.setTextTracks([self.run_rows[run].teams[col].currentText() for col in range(3)])

    def onReceivedTime(self, track: int, seconds: float):
        if self.current_run < 0 or self.run_rows[self.current_run].teams[track-1].currentText() == utils.no_team_str:
            return
        print(f"Bahn {track} ({self.run_rows[self.current_run].teams[track-1].currentText()}): {seconds:.2f}s")
        self.run_rows[self.current_run].widgets[track-1].setTime(seconds)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi(utils.path(__file__, "ctrl.ui"), self)  # load .ui file
        self.next_race_button.clicked.connect(self.nextRace)

        # Load logos
        self.smd.setPixmap(QtGui.QPixmap(utils.path(__file__, "smd.png")))
        self.vde.setPixmap(QtGui.QPixmap(utils.path(__file__, "vde.png")))

        self.race_class_combo: QtWidgets.QComboBox
        self.race_class_combo.setModel(QtCore.QStringListModel())
        self.race_class_combo.model().setStringList(["UA", "UB"])
        self.race_class_combo.setCurrentIndex(0)
        self.race_class_combo.currentTextChanged.connect(self.nextRace)

        self.race = Race(self)

    # Fetch next race (TODO: from database)

    def nextRace(self):
        import random
        self.race.setTeamNames([f"{self.race_class_combo.currentText()}{i+1:02d}"
                                for i in random.sample(range(25), random.randint(2, 3))])
