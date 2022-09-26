from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtCore import Qt, QSize, QObject
from typing import List

from .data import DataWidget
import utils
from utils.debug import traced


def computeMaxSize(aspect: float, max_size: QSize) -> QSize:
    max_width, max_height = max_size.width(), max_size.height()
    h = int(aspect * max_width)
    if h > max_height:
        return QSize(int(max_height / aspect + 0.5), max_height)
    else:
        return QSize(max_width, h)


# This Widget class is used in .ui files
# https://www.pythonguis.com/tutorials/embed-pyqtgraph-custom-widgets-qt-app
class ScaledImageLabel(QtWidgets.QLabel):
    """Auto scaling QLabel's pixmap keeping its initial aspect ratio"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pixmap: QtGui.QPixmap = None
        self.aspect: float = None
        self.max_size = super().maximumSize()

    def setPixmap(self, pixmap: QtGui.QPixmap) -> None:
        self.pixmap = pixmap
        if self.pixmap is None or self.pixmap.isNull():
            self.aspect = None
            self.max_size = super().maximumSize()
        else:
            self.aspect = self.pixmap.height() / self.pixmap.width()
            self.max_size = computeMaxSize(self.aspect, super().maximumSize())

        return super().setPixmap(pixmap)

    def minimumSizeHint(self) -> QSize:
        return QSize(10, 10)

    def maximumSize(self) -> QSize:
        return self.max_size

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        if self.aspect is None:
            return self.height()
        else:
            return int(self.aspect * width + 0.5)

    def sizeHint(self) -> QSize:
        return self.max_size

    def scaledPixmap(self):
        return self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        if self.aspect is not None:
            super().setPixmap(self.scaledPixmap())


class TeamComboBox(QtWidgets.QComboBox):
    none = "---"
    teamChanged = QtCore.pyqtSignal(int, int)  # col, index

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self.col = None
        self.currentIndexChanged.connect(self.__emitTeamChanged)
        self.setInsertPolicy(self.NoInsert)

    def __emitTeamChanged(self, index):
        self.teamChanged.emit(self.col, index)

    def setModel(self, model: QtCore.QAbstractItemModel) -> None:
        self.completer().setModel(model)
        super().setModel(model)

    def setEditable(self, editable: bool) -> None:
        super().setEditable(editable)
        if editable:
            completer = self.completer()
            completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
            completer.setFilterMode(QtCore.Qt.MatchContains)
            self.lineEdit().editingFinished.connect(self._onEdited)

    def setCurrentText(self, text: str) -> None:
        idx = self.findText(text)
        if idx < 0:  # not found
            super().setCurrentText(text)
        else:
            self.setCurrentIndex(idx)

    def _onEdited(self):
        if self.currentIndex() < 0:  # no item selected
            proposed_completion = self.completer().currentCompletion()
            self.setCurrentText(proposed_completion)


class TeamGroup(QObject):
    """Helper class to ensure that team names in this group are unique"""

    def __init__(self, teams=None, parent=None) -> None:
        super().__init__(parent)
        self.teams: List[TeamComboBox] = []
        self.setGroup(teams)

    def setGroup(self, teams: List[TeamComboBox]):
        for team in self.teams:
            team.teamChanged.disconnect(self.makeUnique)
        self.teams = teams if teams else []
        for team in self.teams:
            team.teamChanged.connect(self.makeUnique)

    # provide iterator methods
    def __iter__(self):
        return self.teams.__iter__()

    def __len__(self):
        return self.teams.__len__()

    def __getitem__(self, key):
        return self.teams.__getitem__(key)

    def makeUnique(self, col: int, idx: int):
        if idx == -1:
            return
        for c, team in enumerate(self.teams):
            if c != col and team.currentIndex() == idx:
                team.setCurrentText(utils.no_team_str)


class RunWidget(QtWidgets.QWidget):
    activate = QtCore.pyqtSignal(int)
    cancelled = QtCore.pyqtSignal(int)

    def __init__(self, id: int, *args) -> None:
        super().__init__(*args)
        uic.loadUi(utils.path(__file__, "run.ui"), self)
        self.id = id
        self.num.setValue(id+1)
        self._setButtonsActivated(False)

    def _setButtonsActivated(self, activate):
        self.activateButton.setDisabled(activate)
        self.cancelButton.setEnabled(activate)

    def mouseDoubleClickEvent(self, event):
        self.activate.emit(int(self.num.value())-1)

    @QtCore.pyqtSlot()
    def on_activateButton_clicked(self):
        self._setButtonsActivated(True)
        self.activate.emit(self.id)

    @QtCore.pyqtSlot()
    def on_cancelButton_clicked(self):
        self._setButtonsActivated(False)
        self.cancelled.emit(self.id)
