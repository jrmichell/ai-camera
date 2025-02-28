import cv2
import depthai as dai
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QLabel,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


class CameraController(QWidget):
    def __init__(self, color_order: str) -> None:
        self.color_order = color_order
        self.pipeline = dai.Pipeline()
        super().__init__()

    def rgb_init(self) -> None:
        # pipeline = dai.Pipeline()

        # Define source and output
        camRgb = self.pipeline.create(dai.node.ColorCamera)
        xoutRgb = self.pipeline.create(dai.node.XLinkOut)

        xoutRgb.setStreamName(self.color_order.lower())

        option = ["preview", "video"]

        if self.color_order == "RGB":
            camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)

        if self.color_order == "BGR":
            camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

        if option[0]:  # Preview
            # Linking
            camRgb.preview.link(xoutRgb.input)

            # Properties
            camRgb.setInterleaved(False)

        if option[1]:  # Video
            # Properties
            camRgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
            camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)

            xoutRgb.input.setBlocking(False)
            xoutRgb.input.setQueueSize(1)

    def rgb_preview(self) -> None:
        self.rgb_init()

        print("pipeline", self.pipeline)

        # Connect to device and start pipeline
        with dai.Device(self.pipeline) as device:

            print("device", device)

            # Output queue will be used to get the rgb frames from the output defined above
            qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

            while True:
                inRgb = (
                    qRgb.get()
                )  # blocking call, will wait until a new data has arrived

                # Retrieve 'bgr' (opencv format) frame
                cv2.imshow(self.color_order.lower(), inRgb.getCvFrame())

                if cv2.waitKey(1) == ord("q"):
                    break

                # FIX: Display preview in GUI
                # frame = inRgb.getCvFrame()
                # height, width, channels = frame.shape
                # img = QImage(
                #     frame, width, height, channels, QImage.Format.Format_RGB888
                # )
                # pixmap = QPixmap(img)
                # self.frame.setPixmap(pixmap)

    # TODO: Redo the rgb_video() method to use opencv2
    def rgb_video(self, pipeline: dai.Pipeline) -> None:
        self.rgb_init()
        # Connect to device and start pipeline
        with dai.Device(pipeline) as device:

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

    def create_window(self) -> None:
        self.setWindowTitle("Camera")

        # Layouts
        main_layout = QGridLayout()
        options_layout = QVBoxLayout()

        self.setStyleSheet(
            "font-family: garamond; \
             color: #000; \
             font-size: 32px; \
             background-color: #fff;"
        )
        self.resize(800, 600)

        # Widgets
        color_orders = ["RGB", "BGR"]
        color_order_selector = QComboBox()
        color_order_selector.addItems(color_orders)

        camera_option_video = QRadioButton("Video", self)
        camera_options_preview = QRadioButton("Preview", self)

        self.frame = QLabel()

        # Set preview to be checked by default
        camera_options_preview.setChecked(
            True
        )  # NOTE: Crashes program if camera is not connected

        # Add everything needed for the options layout
        options_layout.addWidget(camera_options_preview)
        options_layout.addWidget(camera_option_video)

        # Add everything needed for the main layout
        main_layout.addWidget(
            color_order_selector, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft
        )
        main_layout.addWidget(self.frame, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set layouts
        main_layout.addLayout(
            options_layout, 1, 1, alignment=Qt.AlignmentFlag.AlignRight
        )
        self.setLayout(main_layout)

        # TODO: Wait until selection is executed
        if camera_options_preview.isChecked():
            self.option = "preview"
            self.rgb_preview()
        if camera_option_video.isChecked():
            self.option = "video"
            # self.rgb_video(pipeline)
