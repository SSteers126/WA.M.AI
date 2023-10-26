from PySide6.QtGui import QTextFormat, QPixmap
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget, QPushButton,
                               QGridLayout, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QFileDialog, QGroupBox, QTabWidget, QComboBox, QSpinBox,
                               QCheckBox, QTextEdit, QDialog, QProgressBar)


class VideoProgressWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Converting video...")

        self.resize(300, 200)
        self.progress = QProgressBar()