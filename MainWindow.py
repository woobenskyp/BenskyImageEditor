from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import Qt, QIcon, QImageReader, QActionGroup, QAction, QResizeEvent, QImage, QPixmap
from PySide6.QtWidgets import QMainWindow, QPushButton, QHBoxLayout, QWidget, QVBoxLayout, QStackedWidget, QFileDialog, \
    QToolBar, QMessageBox

from AboutPage import AboutPage
from ImageCropTab import ImageCropTab
from ImageAdjustTab import ImageAdjustTab

class MainWindow(QMainWindow):
    resized = Signal()
    imageChanged = Signal()

    def __init__(self, imagePath):
        super().__init__()
        self.setWindowTitle("Bensky Image Editor")
        self.setWindowIcon(QIcon("icon/logo.svg"))

        self.imageFile = imagePath
        self.image = QImage(self.imageFile)
        self.modifiedImage = QImage(self.imageFile)
        self.changesSaved = True

        self.setupHeaderLayout()
        self.setupToolbar()

        self.stackedWidget = QStackedWidget()
        self.imageCropWidget = ImageCropTab(self)
        self.imageAdjustWidget = ImageAdjustTab(self)

        self.stackedWidget.addWidget(self.imageCropWidget)
        self.stackedWidget.addWidget(self.imageAdjustWidget)
        self.stackedWidget.setCurrentWidget(self.imageCropWidget)

        self.setCentralWidget(self.stackedWidget)


    def setupHeaderLayout(self):
        self.resetImageButton = QPushButton("Reset")
        self.resetImageButton.setStyleSheet('padding: 4px 8px 4px 8px;')
        self.resetImageButton.setFlat(True)
        self.resetImageButton.clicked.connect(self.resetImage)

        self.newButton = QPushButton(QIcon("icon/newimage.svg"), "Open")
        self.newButton.setStyleSheet("QPushButton:hover{background: #CBE7FE;} QPushButton{background: white; border: 0; padding: 8px 16px; border-bottom: 3px solid #ff5900; color: #E75801;}")
        self.newButton.clicked.connect(self.openNewImage)

        self.saveButton = QPushButton(QIcon("icon/saveimage.svg"), "Save")
        self.saveButton.setStyleSheet("QPushButton:hover{background: #CBE7FE;} QPushButton{background: white; border: 0; padding: 8px 16px; border-bottom: 3px solid #ff5900; color: #E75801;}")
        self.saveButton.clicked.connect(self.saveImage)

        self.helpButton = QPushButton(QIcon("icon/infoimage.svg"), "About")
        self.helpButton.clicked.connect(self.showAboutPage)
        self.helpButton.setFlat(True)

        headerLayout = QHBoxLayout()
        headerLayout.setContentsMargins(0, 0, 0, 0)
        headerLayout.setSpacing(0)
        header = QWidget()
        header.setObjectName('header')
        header.setLayout(headerLayout)
        header.setStyleSheet("#header{background: white;  border-bottom: 1px solid silver}")

        headerLayout.addWidget(self.resetImageButton)
        headerLayout.addStretch()
        headerLayout.addWidget(self.newButton)
        headerLayout.addWidget(self.saveButton)
        headerLayout.addStretch()
        headerLayout.addWidget(self.helpButton)

        self.setMenuWidget(header)

    def setupToolbar(self):
        self.toolbar = QToolBar("Main ToolBar")
        self.toolbar.setIconSize(QSize(20, 20))
        self.toolbar.setStyleSheet("QToolBar{background: white; padding: 4px; padding-top: 8px} QToolButton{padding: 4px}")
        self.toolbar.setMovable(False)
        self.toolbar.visibilityChanged.connect(lambda : self.toolbar.setVisible(True))

        stackWidgetSwitcher = QActionGroup(self)

        imageCropAction = QAction(self)
        imageCropAction.setCheckable(True)
        imageCropAction.setActionGroup(stackWidgetSwitcher)
        imageCropAction.setIcon(QIcon("icon/imagecrop.svg"))
        imageCropAction.setToolTip("Crop")
        imageCropAction.triggered.connect(self.gotoCropPanel)

        imageAdjustAction = QAction(self)
        imageAdjustAction.setCheckable(True)
        imageCropAction.setChecked(True)
        imageAdjustAction.setActionGroup(stackWidgetSwitcher)
        imageAdjustAction.setIcon(QIcon("icon/imageadjust.svg"),)
        imageAdjustAction.setToolTip("Adjust")
        imageAdjustAction.triggered.connect(self.gotoAdjustPanel)

        self.zoomInAction = QAction(self)
        self.zoomInAction.setVisible(False)
        self.zoomInAction.setToolTip("Zoom In")
        self.zoomInAction.setIcon(QIcon('icon/zoomin.svg'))

        self.zoomOutAction = QAction(self)
        self.zoomOutAction.setVisible(False)
        self.zoomOutAction.setToolTip("Zoom Out")
        self.zoomOutAction.setIcon(QIcon('icon/zoomout.svg'))

        self.toolbar.addAction(imageCropAction)
        self.toolbar.addAction(imageAdjustAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.zoomInAction)
        self.toolbar.addAction(self.zoomOutAction)
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)

    def gotoCropPanel(self):
        self.stackedWidget.setCurrentWidget(self.imageCropWidget)
        self.zoomOutAction.setVisible(False)
        self.zoomInAction.setVisible(False)

    def gotoAdjustPanel(self):
        self.stackedWidget.setCurrentWidget(self.imageAdjustWidget)
        self.zoomOutAction.setVisible(True)
        self.zoomInAction.setVisible(True)

    def resetImage(self):
        self.imageChanged.emit()
        self.modifiedImage = self.image
        self.changesSaved = True
        self.imageChanged.emit()



    def openNewImage(self):
        if not self.changesSaved:
            response = QMessageBox.question(self, 'Changes unsaved', 'Do you want to save the current image?')
            if response == QMessageBox.Yes:
                saved = self.saveImage()
                if not saved:
                    return

        formats = ["*." + extension.data().decode() for extension in QImageReader.supportedImageFormats()]
        fileFilter = "Images (" + " ".join(formats) + ")"
        print(fileFilter)
        imagePath = QFileDialog.getOpenFileName(self, "Open Image", "\home", fileFilter)
        if imagePath[0]:
            self.imageChanged.emit()
            self.imageFile = imagePath[0]
            self.image = QImage(self.imageFile)
            self.modifiedImage = QImage(self.imageFile)
            self.changesSaved = True
            self.imageChanged.emit()


    def saveImage(self):
        savePath = QFileDialog.getSaveFileName(self, "Save Image", "\home", "Images (*.{})".format(self.imageFile.split('.')[-1]))
        if savePath[0]:
            self.imageCropWidget.cropedImage().save(savePath[0])
            return True
        else:
            return False

    def resizeEvent(self, e:QResizeEvent):
        super().resizeEvent(e)
        if not e.oldSize() == e.size():
            self.resized.emit()

    def showAboutPage(self):
        aboutPage = AboutPage()
        aboutPage.exec()



