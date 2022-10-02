from PyQt5 import QtWidgets, uic, QtCore, QtGui
from .widgets import RunWidget, DataWidget, TeamGroup, TeamComboBox
from communication import CanBusComm, DummyComm
from typing import List
import utils
import numpy as np
from collections import OrderedDict


class RunRow(TeamGroup):
    pointsChanged = QtCore.pyqtSignal()

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
            w.invalidChanged.connect(self.updatePoints)
            w.points.valueChanged.connect(self.pointsChanged)
        self.setGroup([w.team for w in self.widgets])  # configure TeamGroup

    def reset(self):
        for w in self.widgets:
            w.reset()

    def setEnabled(self, enable: bool):
        for w in self.widgets:
            w.setEnabled(enable and w.team.currentText() != utils.no_team_str)

    def updatePoints(self):
        """recalculate points"""
        sorted_times = sorted(enumerate([w.resultTime() for w in self.widgets]),
                              key=lambda x: x[1] if x[1] > 0 else 888)
        order, _ = zip(*sorted_times)
        for i, w in enumerate(self.widgets):
            w.points.setValue(3 - order.index(i) if w.resultTime() > 0 else 0)


class Race:
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        self.teamsModel = QtCore.QStringListModel()
        self.expected_runs = 0
        self.current_run = -1

        # Create top row's team comboboxes
        self.teams = TeamGroup([parent.findChild(TeamComboBox, f"team_combobox_{i+1}") for i in range(3)])
        for i, team in enumerate(self.teams):
            team.col = i
            team.setModel(self.teamsModel)
            team.teamChanged.connect(lambda: self.configureRuns([t.currentText() for t in self.teams]))
            team.teamChanged.connect(lambda col: self.setTrackEnabled(
                col, self.teams[col].currentText() != utils.no_team_str))

        # Create widgets row-wise for each run
        self.run_rows = [RunRow(self.teamsModel, parent.gridLayout, 5 + i) for i in range(3)]
        for r in self.run_rows:
            r.pointsChanged.connect(self.updatePoints)

        # "Lauf x" widgets in first column
        self.run_widgets = [RunWidget(i) for i in range(3)]
        for i, w in enumerate(self.run_widgets):
            parent.gridLayout.addWidget(w, 5 + i, 0)
            w.activate.connect(self.setRun)
            w.cancelled.connect(self.resetRun)

        # access to widgets: points, best_times, track labels
        self.points = [parent.findChild(QtWidgets.QSpinBox, f"points_{i+1}") for i in range(3)]
        self.best_times = [parent.findChild(QtWidgets.QDoubleSpinBox, f"best_time_{i+1}") for i in range(3)]
        self.track_labels = [parent.findChild(QtWidgets.QLabel, f"label_track{i+1}") for i in range(3)]

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

    def configureRuns(self, names):
        """configure run rows based on team names"""
        assert len(names) == 3
        names = np.array(names)
        valid = names != utils.no_team_str
        self.expected_runs = num_valid = np.count_nonzero(valid)

        for run in range(3):
            if run >= num_valid:
                for col in range(3):
                    self.run_rows[run][col].setCurrentIndex(-1)
                continue

            tracks = np.arange(3)  # initialize to 0 1 2
            # rotate valid tracks only, use +run to rotate in opposite direction
            rotate = np.mod(np.arange(num_valid) - run, num_valid)
            tracks[valid] = tracks[valid][rotate]  # assign new ordering
            for col in range(3):
                self.run_rows[run][col].setCurrentText(names[tracks[col]])

        self.setRun(-1)  # disable all runs
        self.run_widgets[0].setEnabled(True)

    def setTrackEnabled(self, col: int, enabled: bool):
        print("setTrackEnabled", col, enabled)
        self.best_times[col].setEnabled(enabled)
        self.points[col].setEnabled(enabled)
        self.track_labels[col].setEnabled(enabled)

    def resetRun(self, run):
        self.run_rows[run].reset()

    def updatePoints(self):
        for c in range(3):
            team = self.teams[c].currentText()
            points = [row.widgets[row.index(team)].points.value() for row in self.run_rows[:self.expected_runs]]
            self.points[c].setValue(sum(points))

    def updateBestTime(self, team: str):
        times = [row.widgets[row.index(team)].resultTime() for row in self.run_rows[:self.expected_runs]]
        self.best_times[self.teams.index(team)].setValue(min([t for t in times if t > 0]))

    def setRun(self, run: int):
        # Enable/disable widgets
        for i in range(3):
            self.run_rows[i].setEnabled(i <= run)
            self.run_widgets[i].setEnabled(i <= run)
        self.current_run = run

        if run < 0:  # reset
            for w in self.run_widgets:
                w.on_cancelButton_clicked()
        else:  # Prepare run
            # Block clock on unused tracks
            for i, team in enumerate(self.run_rows[run].teams):
                self.comm.blockClock(i, team.currentText() == utils.no_team_str)
            # Send team names to display
            self.comm.setTextTracks([self.run_rows[run].teams[col].currentText() for col in range(3)])

    def onReceivedTime(self, track: int, seconds: float):
        try:
            row = self.run_rows[self.current_run]
            w = row.widgets[track-1]
        except IndexError:
            return  # invalid current_run
        if w.team.currentText() == utils.no_team_str or w.invalid.isChecked():
            return  # invalid team / track

        print(f"Bahn {track} ({w.team.currentText()}): {seconds:.2f}s")
        w.setTime(seconds)
        row.updatePoints()
        self.updateBestTime(w.team.currentText())

        # Did we finish all expected runs?
        if len([w for w in row.widgets if w.resultTime() > 0]) == self.expected_runs:
           self.onRunFinished()

    def onRunFinished(self):
        if self.current_run+1 < self.expected_runs:
            self.run_widgets[self.current_run+1].setEnabled(True)
        else:  # all runs finished
            pass

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
