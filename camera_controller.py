import cv2
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
    QWidget,
)


class Camera(QThread):
    frameCaptured = pyqtSignal(np.ndarray)

    def __init__(self) -> None:
        # self.pipeline = dai.Pipeline()
        super().__init__()

    # def rgb_init(self) -> dai.Pipeline:
    #     pipeline = dai.Pipeline()
    #
    #     # Define source and output
    #     camRgb = pipeline.create(dai.node.ColorCamera)
    #     xoutRgb = pipeline.create(dai.node.XLinkOut)
    #
    #     """Color Orders"""
    #     # self.color_orders = ["RGB", "BGR"]
    #     # if self.color_orders[0]:  # RGB
    #     #     camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
    #     #     xoutRgb.setStreamName(self.color_orders[0].lower())
    #     #
    #     # if self.color_orders[1]:  # BGR
    #     #     camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    #     #     xoutRgb.setStreamName(self.color_orders[1].lower())
    #
    #     xoutRgb.setStreamName("rgb")
    #
    #     """Options"""
    #     self.options = ["preview", "video"]
    #     if self.options[0]:  # Preview
    #         # Linking
    #         camRgb.preview.link(xoutRgb.input)
    #
    #         # Properties
    #         camRgb.setInterleaved(False)
    #
    #     if self.options[1]:  # Video
    #         # Properties
    #         camRgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    #         camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    #
    #         xoutRgb.input.setBlocking(False)
    #         xoutRgb.input.setQueueSize(1)
    #
    #     return pipeline

    # def rgb_preview(self) -> None:
    #     pipeline = self.rgb_init()
    #
    #     # Connect to device and start pipeline
    #     with dai.Device(pipeline) as device:
    #
    #         print("device", device)
    #
    #         # Output queue will be used to get the rgb frames from the output defined above
    #         qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    #
    #         while True:
    #             inRgb = qRgb.get()
    #             frame = inRgb.getCvFrame()
    #
    #             if frame is not None:
    #                 print(f"Frame received: {frame.shape}")  # Debugging
    #                 self.frameCaptured.emit(frame)  # Emit frame signal
    #                 print("Signal emitted")  # Debugging
    #
    #             # Prevent high CPU usage
    #             if not self.isInterruptionRequested():
    #                 self.msleep(10)
    #             else:
    #                 break

    def run(self) -> None:
        """Runs the camera processing loop in a separate thread."""
        print("Starting DepthAI Camera Thread...")

        # Create the DepthAI pipeline inside run() to avoid blocking the main thread
        pipeline = dai.Pipeline()

        # Define source and output
        camRgb = pipeline.create(dai.node.ColorCamera)
        xoutRgb = pipeline.create(dai.node.XLinkOut)
        xoutRgb.setStreamName("rgb")

        # Set up preview
        camRgb.preview.link(xoutRgb.input)
        camRgb.setInterleaved(False)

        # Connect to the device and start the pipeline
        with dai.Device(pipeline) as device:
            print("Device connected:", device)

            # Output queue will be used to get the rgb frames
            qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

            while not self.isInterruptionRequested():
                inRgb = qRgb.get()
                frame = inRgb.getCvFrame()

                if frame is not None:
                    print(f"Frame received: {frame.shape}")  # Debugging
                    self.frameCaptured.emit(frame)  # Emit frame signal
                    print("Signal emitted")  # Debugging

                self.msleep(10)  # Prevent high CPU usage

    # TODO: Redo rgb_video() method
    # def rgb_video(self) -> None:
    #     pipeline = self.rgb_init()
    #
    #     # Connect to device and start pipeline
    #     with dai.Device(pipeline) as device:
    #
    #         # Output queue will be used to get the encoded data from the output defined above
    #         q = device.getOutputQueue(name="h265", maxSize=30, blocking=True)
    #
    #         # The .h265 file is a raw stream file (not playable yet)
    #         with open("video.h265", "wb") as videoFile:
    #             print("Press Ctrl+C to stop encoding...")
    #             try:
    #                 while True:
    #                     h265Packet = (
    #                         q.get()
    #                     )  # Blocking call, will wait until a new data has arrived
    #                     h265Packet.getData().tofile(
    #                         videoFile
    #                     )  # Appends the packet data to the opened file
    #             except KeyboardInterrupt:
    #                 # Keyboard interrupt (Ctrl + C) detected
    #                 pass
    #
    #     print(
    #         "To view the encoded data, convert the stream file (.h265) into a video file (.mp4) using a command below:"
    #     )
    #     print("ffmpeg -framerate 30 -i video.h265 -c copy video.mp4")


class Window(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Camera")
        self.setStyleSheet(
            "font-family: garamond; \
             color: #fff; \
             font-size: 32px; \
             background-color: #000;"
        )
        self.resize(800, 600)

        # Main widget
        self.main_layout = QVBoxLayout()
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # QLabel to display the video
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")  # Ensure visibility
        self.video_label.setPixmap(QPixmap(640, 480))  # Placeholder
        self.main_layout.addWidget(self.video_label)

        self.options_layout = QVBoxLayout()

        # Camera Options
        self.camera_option_video = QRadioButton("Video", self)
        self.camera_option_preview = QRadioButton("Preview", self)
        self.options_layout.addWidget(self.camera_option_preview)
        self.options_layout.addWidget(self.camera_option_video)
        self.main_layout.addLayout(self.options_layout)

        # Set preview to be checked by default
        self.camera_option_preview.setChecked(True)

        # Start DepthAI Thread
        self.camera_thread = Camera()
        print("Signal connected")  # Debugging
        self.camera_thread.frameCaptured.connect(self.update_frame)
        self.camera_thread.start()  # Start the camera thread

        # if self.camera_option_preview.isChecked():
        #     self.camera_thread.rgb_preview()

    def update_frame(self, frame: np.ndarray):
        """Update QLabel with the latest frame."""
        print(f"Updating frame: {frame.shape}")  # Debugging

        # Convert OpenCV image (BGR) to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        height, width, channel = frame_rgb.shape
        bytes_per_line = 3 * width
        qimg = QImage(
            frame_rgb.data.tobytes(),
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888,
        )
        pixmap = QPixmap.fromImage(qimg)

        # Scale pixmap to fit label while keeping aspect ratio
        self.video_label.setPixmap(
            pixmap.scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
        )
        self.video_label.repaint()  # Ensure UI refresh

    def close_event(self, event):
        """Handle window close event to stop camera thread."""
        self.camera_thread.requestInterruption()
        self.camera_thread.quit()
        self.camera_thread.wait()
        event.accept()

    def create_window(self) -> None:

        # Layouts
        # main_layout = QGridLayout()
        # options_layout = QVBoxLayout()

        """Color Orders"""
        # Widgets
        # color_orders = ["RGB", "BGR"]
        # color_order_selector = QComboBox()
        # color_order_selector.addItems(color_orders)
        # self.main_layout.addWidget(color_order_selector)
        """Camera Options"""
        # camera_option_video = QRadioButton("Video", self)
        # camera_options_preview = QRadioButton("Preview", self)
        # self.main_layout.addLayout(
        #     options_layout, 1, 1, alignment=Qt.AlignmentFlag.AlignRight
        # )
        # Set preview to be checked by default
        # camera_options_preview.setChecked(
        #     True
        # )  # NOTE: Crashes program if camera is not connected

        # Add everything needed for the options layout
        # options_layout.addWidget(camera_options_preview)
        # options_layout.addWidget(camera_option_video)

        """Video Display"""
        # self.video_label = QLabel(self)
        # self.setCentralWidget(self.video_label)
        # main_layout.addWidget(
        #     self.video_label, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter
        # )

        # Add everything needed for the main layout

        # Set layouts
        # self.setLayout(main_layout)

        # FIX: Wait until selection is executed
        # if camera_options_preview.isChecked():
        #     self.option = "preview"
        #     self.rgb_preview()
        # if camera_option_video.isChecked():
        #     self.option = "video"
        #     self.rgb_video(pipeline)
