# Imports
from PyQt6.QtWidgets import QGridLayout, QPushButton, QWidget


class Window(QWidget):
    def __init__(self):
        super().__init__()
        # NOTE: This will no longer be needed when the camera is implemented
        self.setWindowTitle("Camera")

        # Layouts
        main_layout = QGridLayout()

        # Widgets
        self.setStyleSheet(
            "font-family: garamond; \
             color: white; \
             font-size: 32px; \
             background-color: #662d91;"
        )
        self.resize(800, 600)

        # Test Buttons
        yes_button = QPushButton("Yes")
        yes_button.setFixedSize(150, 150)
        no_button = QPushButton("No")
        no_button.setFixedSize(150, 150)

        # Add everything needed for the main layout
        main_layout.addWidget(yes_button, 1, 1)
        main_layout.addWidget(no_button, 1, 2)

        # Set the layout to the main layout configured
        self.setLayout(main_layout)
