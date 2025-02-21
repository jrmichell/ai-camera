import cv2
import depthai as dai
from gui import FrameViewer
from PyQt6.QtWidgets import QApplication, QWidget


class CameraController(FrameViewer):

    def __init__(self, color_order: str, option: str) -> None:
        self.color_order = color_order
        self.option = option
        super().__init__()

    def rgb_init(self, pipeline: dai.Pipeline) -> None:

        # Define source and output
        camRgb = pipeline.create(dai.node.ColorCamera)
        xoutRgb = pipeline.create(dai.node.XLinkOut)

        xoutRgb.setStreamName(self.option)

        if self.color_order == "RGB":
            camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)

        if self.color_order == "BGR":
            camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

        if self.option == "preview":
            # Linking
            camRgb.preview.link(xoutRgb.input)

            # Properties
            camRgb.setInterleaved(False)

        if self.option == "video":
            # Properties
            camRgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
            camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)

            xoutRgb.input.setBlocking(False)
            xoutRgb.input.setQueueSize(1)

    def rgb_preview(self) -> None:
        self.rgb_init(dai.Pipeline)

        # Connect to device and start pipeline
        with dai.Device(dai.Pipeline) as device:

            # Output queue will be used to get the rgb frames from the output defined above
            qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

            while True:
                inRgb = (
                    qRgb.get()
                )  # blocking call, will wait until a new data has arrived

                # Retrieve 'bgr' (opencv format) frame
                cv2.imshow(self.option, inRgb.getCvFrame())

                if cv2.waitKey(1) == ord("q"):
                    break

    # TODO: Redo the rgb_video() method to use opencv2
    def rgb_video(self) -> None:
        self.rgb_init(dai.Pipeline)

        # Connect to device and start pipeline
        with dai.Device(dai.Pipeline) as device:

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
