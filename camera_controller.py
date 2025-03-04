import sys

import depthai as dai
import numpy as np
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QLabel,
    QMainWindow,
    QRadioButton,
    QVBoxLayout,
)


class Camera(QThread):
    frameCaptured = pyqtSignal(np.ndarray)

    def __init__(self) -> None:
        self.pipeline = dai.Pipeline()
        super().__init__()

    def rgb_init(self) -> None:
        # Define source and output
        camRgb = self.pipeline.create(dai.node.ColorCamera)
        xoutRgb = self.pipeline.create(dai.node.XLinkOut)

        """Color Orders"""
        self.color_orders = ["RGB", "BGR"]
        if self.color_orders[0]:  # RGB
            camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
            xoutRgb.setStreamName(self.color_orders[0].lower())

        if self.color_orders[1]:  # BGR
            camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
            xoutRgb.setStreamName(self.color_orders[1].lower())

        """Options"""
        self.options = ["preview", "video"]
        if self.options[0]:  # Preview
            # Linking
            camRgb.preview.link(xoutRgb.input)

            # Properties
            camRgb.setInterleaved(False)

        if self.options[1]:  # Video
            # Properties
            camRgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
            camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)

            xoutRgb.input.setBlocking(False)
            xoutRgb.input.setQueueSize(1)

    def rgb_preview(self) -> None:
        self.rgb_init()

        # Connect to device and start pipeline
        with dai.Device(self.pipeline) as device:

            print("device", device)

            # Output queue will be used to get the rgb frames from the output defined above
            qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

            while True:
                inRgb = qRgb.get()
                frame = inRgb.getCvFrame()

                if frame is not None:
                    self.frameCaptured.emit(frame)  # Emit frame signal

                # Prevent high CPU usage
                if not self.isInterruptionRequested():
                    self.msleep(10)
                else:
                    break

    # TODO: Redo rgb_video() method
    def rgb_video(self) -> None:
        self.rgb_init()
        # Connect to device and start pipeline
        with dai.Device(self.pipeline) as device:

            # Output queue will be used to get the encoded data from the output defined above
            q = device.getOutputQueue(name="h265", maxSize=30, blocking=True)

            # The .h265 file is a raw stream file (not playable yet)
            with open("video.h265", "wb") as videoFile:
                print("Press Ctrl+C to stop encoding...")
                try:
                    while True:
                        h265Packet = (
                            q.get()
                        )  # Blocking call, will wait until a new data has arrived
                        h265Packet.getData().tofile(
                            videoFile
                        )  # Appends the packet data to the opened file
                except KeyboardInterrupt:
                    # Keyboard interrupt (Ctrl + C) detected
                    pass

        print(
            "To view the encoded data, convert the stream file (.h265) into a video file (.mp4) using a command below:"
        )
        print("ffmpeg -framerate 30 -i video.h265 -c copy video.mp4")


class Window(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Camera")
        self.setStyleSheet(
            "font-family: garamond; \
             color: #000; \
             font-size: 32px; \
             background-color: #fff;"
        )
        self.resize(800, 600)

        # Start DepthAI Thread
        try:
            self.camera_thread = Camera()
            self.camera_thread.frameCaptured.connect(self.update_frame)
            self.camera_thread.start()
        except Exception as e:
            raise e

    def create_window(self) -> None:

        # Layouts
        main_layout = QGridLayout()
        options_layout = QVBoxLayout()

        """Color Orders"""
        # Widgets
        color_orders = ["RGB", "BGR"]
        color_order_selector = QComboBox()
        color_order_selector.addItems(color_orders)
        main_layout.addWidget(
            color_order_selector, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft
        )
        """Camera Options"""
        camera_option_video = QRadioButton("Video", self)
        camera_options_preview = QRadioButton("Preview", self)
        main_layout.addLayout(
            options_layout, 1, 1, alignment=Qt.AlignmentFlag.AlignRight
        )
        # Set preview to be checked by default
        camera_options_preview.setChecked(
            True
        )  # NOTE: Crashes program if camera is not connected

        # Add everything needed for the options layout
        options_layout.addWidget(camera_options_preview)
        options_layout.addWidget(camera_option_video)

        """Video Display"""
        self.video_label = QLabel(self)
        self.setCentralWidget(self.video_label)
        main_layout.addWidget(
            self.video_label, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter
        )

        # Add everything needed for the main layout

        # Set layouts
        self.setLayout(main_layout)

        # FIX: Wait until selection is executed
        # if camera_options_preview.isChecked():
        #     self.option = "preview"
        #     self.rgb_preview()
        # if camera_option_video.isChecked():
        #     self.option = "video"
        #     self.rgb_video(pipeline)

    def update_frame(self, frame):
        """Update QLabel with the latest frame."""
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        qimg = QImage(
            frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
        )
        pixmap = QPixmap.fromImage(qimg)

        # Scale pixmap to fit label while keeping aspect ratio
        self.video_label.setPixmap(
            pixmap.scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
        )

    def close_event(self, event):
        """Handle window close event to stop camera thread."""
        self.camera_thread.requestInterruption()
        self.camera_thread.quit()
        self.camera_thread.wait()
        event.accept()
