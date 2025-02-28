from camera_controller import CameraController


def main():
    camera = CameraController("RGB")
    camera.rgb_preview()


if __name__ == "__main__":
    main()
