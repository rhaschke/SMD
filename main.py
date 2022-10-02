from PyQt5 import QtWidgets, QtCore
from gui import MainWindow
import sys
import signal


def sigint_handler(*args):
    print(" Quitting")
    QtWidgets.QApplication.quit()

app = QtWidgets.QApplication(sys.argv)

main = MainWindow()
main.nextRace()

# Run the python interpreter every 100ms to catch Ctrl-C
timer = QtCore.QTimer()
timer.start(100)
timer.timeout.connect(lambda: None)
# Call our custom signal handler on Ctrl-C
signal.signal(signal.SIGINT, sigint_handler)

main.show()
app.exec_()

# stop communication threads
main.race.comm.stop()
