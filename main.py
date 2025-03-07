import sys

from PyQt6.QtWidgets import QApplication

from camera_controller import Window


def main():
    app = QApplication(sys.argv)
    window = Window()
    window.__init__()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
