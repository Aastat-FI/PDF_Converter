from PyQt5.QtWidgets import QApplication
from gui import MainWindow
import settings


def main():
    settings.init()
    app = QApplication([])
    mw = MainWindow()
    app.exec_()


if __name__ == "__main__":
    main()
