from depthai import Pipeline
from PyQt6.QtWidgets import QApplication

from camera_controller import CameraController


def main():
    app = QApplication([])
    window = CameraController("RGB", "preview")
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
