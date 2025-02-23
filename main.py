from PyQt6.QtWidgets import QApplication

from gui import Window


def main():
    app = QApplication([])
    window = Window()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
