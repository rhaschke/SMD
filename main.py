from PyQt5 import QtWidgets, QtCore
from gui import MainWindow
import sys


app = QtWidgets.QApplication(sys.argv)

main = MainWindow()
main.nextRace()

main.show()
app.exec_()
