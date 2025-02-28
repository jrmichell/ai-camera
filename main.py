from camera_controller import CameraController


def main():
    camera = CameraController("RGB", "preview")
    camera.rgb_preview()


if __name__ == "__main__":
    main()
