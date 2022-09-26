from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QSize, QObject
from .data import DataWidget


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
    teamChanged = QtCore.pyqtSignal(int, str)

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self.col = None
        self.setEditable(True)
        completer = self.completer()
        completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        completer.setFilterMode(QtCore.Qt.MatchContains)

        self.lineEdit().editingFinished.connect(self._onChange)

    def setModel(self, model: QtCore.QAbstractItemModel) -> None:
        self.completer().setModel(model)
        super().setModel(model)

    def _onChange(self):
        text = self.currentText()
        if text not in self.model().stringList():
            proposed_completion = self.completer().currentCompletion()
            self.setCurrentText(proposed_completion)
        self.teamChanged.emit(self.col, self.currentText())
