from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys, utils, shutil, filecmp, time, logging

logger = logging.getLogger(__name__)


class DupCheckUI(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.setWindowTitle('Sort Movies')
        self.mainLayout = QVBoxLayout(self)
        self.goButton = QPushButton('Sort movies')
        self.goButton.clicked.connect(self._sortMovies)
        self.mainLayout.addWidget(self.goButton)

        self.resize(400, 100)

    def _sortMovies(self, rootFolder=None):
        print(rootFolder)


def main():
    app = QApplication(sys.argv)
    w = DupCheckUI()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()