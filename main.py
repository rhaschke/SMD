from PyQt5 import QtWidgets, QtCore
from gui import RaceControlWindow
import sys


app = QtWidgets.QApplication(sys.argv)
main = RaceControlWindow()
main.show()
app.exec_()
