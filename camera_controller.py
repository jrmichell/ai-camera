import cv2
import depthai as dai
import numpy as np
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel, QMainWindow, QRadioButton, QVBoxLayout, QWidget


class Camera(QThread):
    frameCaptured = pyqtSignal(np.ndarray)

    def __init__(self) -> None:
        super().__init__()

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

        # Connect to device and start pipeline
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
