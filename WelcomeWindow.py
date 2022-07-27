import os
from pathlib import Path

from PySide6.QtGui import QIcon, QFont, Qt, QPixmap, QImageReader
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QHBoxLayout
from MainWindow import MainWindow


class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bensky Image Editor")
        self.setWindowIcon(QIcon("icon/logo.svg"))

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.setupUi()


    def setupUi(self):
        self.setStyleSheet("QPushButton{ padding: 12px 128px; margin-left: 8px; margin-right: 8px;}")

        logo = QSvgWidget()
        logo.load("icon/logo.svg")
        logo.setFixedSize(156, 156)

        logoLayout = QHBoxLayout()
        logoLayout.addStretch()
        logoLayout.addWidget(logo)
        logoLayout.addStretch()

        appName = QLabel("Bensky Image Editor")
        appNameFont = QFont()
        appNameFont.setPointSize(24)
        appName.setFont(appNameFont)
        appName.setAlignment(Qt.AlignCenter)

        appVersion = QLabel("Version 1.0.0")
        appVersion.setStyleSheet("color: grey; margin-bottom: 24px")
        appVersion.setAlignment(Qt.AlignCenter)

        appInfoLayout = QVBoxLayout()
        appInfoLayout.setAlignment(Qt.AlignCenter)
        appInfoLayout.addLayout(logoLayout)
        appInfoLayout.addWidget(appName)
        appInfoLayout.addWidget(appVersion)

        openImageButton = QPushButton("Open Image")
        openImageButton.setIcon(QPixmap("icon/openproject.svg"))
        openImageButton.setStyleSheet("margin-bottom: 12px")
        openImageButton.clicked.connect(self.openImage)

        self.mainLayout.addLayout(appInfoLayout)
        self.mainLayout.addWidget(openImageButton)
        self.mainLayout.setAlignment(Qt.AlignHCenter)


    def openImage(self):
        formats = ["*." + extension.data().decode() for extension in QImageReader.supportedImageFormats()]
        fileFilter = "Images (" + " ".join(formats) + ")"
        print(fileFilter)
        imagePath = QFileDialog.getOpenFileName(self, "Open Image", "\home", fileFilter)
        if imagePath[0]:
            self.project = MainWindow(imagePath[0])
            self.project.show()
            self.hide()