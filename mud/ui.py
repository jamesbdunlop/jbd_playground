from PyQt5 import QtGui, QtWidgets, QtCore
import sys

class AdventureUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(AdventureUI, self).__init__(parent)

        self.setWindowTitle('Sams Game')

        self.tempWidget = QtWidgets.QWidget()
        self.tempWidgetLayout = QtWidgets.QVBoxLayout(self.tempWidget)
        self.goButton = QtWidgets.QPushButton("RUN THE GAME!")

        self.tempWidgetLayout.addWidget(self.goButton)

        self.setCentralWidget(self.tempWidget)


if __name__ == '__main__':
    qtapp = QtWidgets.QApplication(sys.argv)
    myUI = AdventureUI()
    myUI.show()
    sys.exit(qtapp.exec_())
