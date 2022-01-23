import sys
from PyQt5 import QtWidgets, QtCore
from peer import Peer
from ui import Ui_MainWindow

class AppUi(QtWidgets.QMainWindow):
    def __init__(self,peer:Peer):
        self.qt_app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QWidget.__init__(self, None)
        self.ui = Ui_MainWindow(peer)
        self.ui.setupUi(self)

    def itemClicked(self, item):
        print(item.text())

    def comboChanged(self):
        print(self.ui.comboBox.currentData())

    def pushButtonPressed(self):
        self.ui.textBrowser.append(self.ui.lineEdit.text())

    def run(self):
        self.show()
        self.qt_app.exec_()

def main():
    app = AppUi()
    app.run()

if __name__ == '__main__':
    main()
