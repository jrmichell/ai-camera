from PyQt6.QtWidgets import QApplication, QWidget
from camera import Camera
from gui import FrameViewer


def main():
    app = QApplication([])
    camera = Camera("RGB", "video")
    camera.show()
    camera.run(app)


if __name__ == "__main__":
    main()
