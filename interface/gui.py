"""GUI-заглушка на PyQt5 — отображает результаты (минимальная реализация)"""
from PyQt5 import QtWidgets
import sys

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartSec Audit GUI")
        self.resize(800, 600)
        self.text = QtWidgets.QTextEdit(self)
        self.setCentralWidget(self.text)

    def display(self, text: str):
        self.text.append(text)


def run_app():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_app()
