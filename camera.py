from camera_controller import CameraController
from PyQt6.QtWidgets import QApplication, QWidget


class Camera(CameraController):

    def __init__(self, color_order: str, option: str) -> None:
        self.color_order = color_order
        self.option = option
        super().__init__(color_order, option)

    def run(self, app: QApplication) -> None:
        app.exec()
