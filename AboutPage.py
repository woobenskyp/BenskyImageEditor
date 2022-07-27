from PySide6.QtGui import QFont, QIcon
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDialogButtonBox
import PySide6.QtSvg


class AboutPage(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About Bensky Image Editor")
        self.setWindowIcon(QIcon('icon/logo.svg'))

        mainLayout = QVBoxLayout()
        mainContentLayout = QHBoxLayout()

        infoContentLayout = QVBoxLayout()

        logo = QSvgWidget()
        logo.load("icon/logo.svg")
        logo.setFixedSize(96, 96)

        appName = QLabel("Bensky Image Editor")
        appNameFont = QFont()
        appNameFont.setPointSize(16)
        appNameFont.setWeight(QFont.Bold)
        appName.setFont(appNameFont)

        appVersion = QLabel("Version 1.0.0")
        appVersion.setStyleSheet("color: grey; margin-bottom: 24px")

        infoContentLayout.addWidget(appName)
        infoContentLayout.addWidget(appVersion)
        infoContentLayout.addWidget(QLabel("Built on June 25, 2022"))
        infoContentLayout.addWidget(QLabel("\n+1 809 866 7424\nfnethaiti@gmail.com\n"))
        infoContentLayout.addWidget(QLabel("Copyright © 2022 Woobensky Pierre"))

        logoLayout = QVBoxLayout()
        logoLayout.addWidget(logo)
        logoLayout.addStretch()

        mainContentLayout.addLayout(logoLayout)
        mainContentLayout.addStretch()

        mainContentLayout.addLayout(infoContentLayout)

        okButton = QDialogButtonBox(QDialogButtonBox.Ok)
        okButton.accepted.connect(self.accept)
        mainLayout.addLayout(mainContentLayout)
        mainLayout.addWidget(okButton)

        self.setLayout(mainLayout)


