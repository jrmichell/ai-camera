# Imports
import os
import sys
import cv2
import string
import numpy as np
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QApplication,
    QComboBox,
)
from PyQt6.QtCore import Qt
from PyQt6 import QtCore


class FrameViewer(QMainWindow):

    def __init__(self):
        super().__init__()

        # Initialize Main Window
        self.setStyleSheet(
            "font-family: garamond; \
             color: white; \
             font-size: 32px; \
             background-color: grey;"
        )
        self.setFixedSize(800, 600)

        # Test Button
        button = QPushButton("Yes")
        self.setCentralWidget(button)
