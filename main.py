from PyQt5.QtWidgets import QApplication
from gui import MainWindow


def main():
    app = QApplication([])
    mw = MainWindow()
    app.exec_()


if __name__ == "__main__":
    main()
