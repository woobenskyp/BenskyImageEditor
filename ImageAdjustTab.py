from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QPixmap, Qt, QImage, QResizeEvent
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea, QFormLayout, QSlider, QPushButton
import numpy as np
from PIL import Image


class ImageAdjustTab(QWidget):
    def __init__(self, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow
        self.mainWindow.imageChanged.connect(self.changeImage)
        self.mainWindow.stackedWidget.currentChanged.connect(self.updateImage)
        self.mainWindow.zoomInAction.triggered.connect(lambda: self.zoomImage(0.15))
        self.mainWindow.zoomOutAction.triggered.connect(lambda: self.zoomImage(-0.15))

        self.mainLayout = QHBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setupImageView()
        self.setupAdjustmentPanel()
        self.xDifference = None

        self.setLayout(self.mainLayout)

    def setupAdjustmentPanel(self):
        self.setStyleSheet("font-size: 14px")
        lightAdjustmentLayout = QFormLayout()
        lightAdjustmentLayout.setRowWrapPolicy(QFormLayout.WrapAllRows)

        lightLabel = QLabel("Light")
        lightLabel.setStyleSheet("font-size: 18px; margin: 16px 0 16px 0")

        colorLabel = QLabel("Color")
        colorLabel.setStyleSheet("font-size: 18px; margin: 16px 0 16px 0")

        textureLabel = QLabel("Texture")
        textureLabel.setStyleSheet("font-size: 18px; margin: 16px 0 16px 0")

        brightnessLabel = QPushButton(" Brightness")
        brightnessLabel.setIconSize(QSize(20, 20))
        brightnessLabel.setIcon(QPixmap("icon/brightness.svg"))
        brightnessLabel.setFlat(True)
        self.brightnessSlider = Slider(self.mainWindow)
        self.brightnessSlider.setOrientation(Qt.Horizontal)
        self.brightnessSlider.setRange(-100, 100)
        self.brightnessSlider.setSingleStep(5)
        self.brightnessSlider.setSliderPosition(0)
        self.brightnessSlider.valueChanged.connect(lambda value: self.setBrightness(value - self.brightnessSlider.previousValue))
        brightnessLabel.clicked.connect(lambda : self.brightnessSlider.setValue(0))

        contrastLabel = QPushButton(" Contrast")
        contrastLabel.setIconSize(QSize(20, 20))
        contrastLabel.setIcon(QPixmap("icon/contrast.svg"))
        contrastLabel.setFlat(True)
        self.contrastSlider = Slider(self.mainWindow)
        self.contrastSlider.setOrientation(Qt.Horizontal)
        self.contrastSlider.setRange(-100, 100)
        self.contrastSlider.setSingleStep(1)
        self.contrastSlider.setSliderPosition(0)
        self.contrastSlider.valueChanged.connect(lambda value: self.setContrast(value - self.contrastSlider.previousValue))
        contrastLabel.clicked.connect(lambda : self.contrastSlider.setValue(0))


        highlightLabel = QPushButton(" Highlight")
        highlightLabel.setIconSize(QSize(20, 20))
        highlightLabel.setIcon(QPixmap("icon/hightlight.svg"))
        highlightLabel.setFlat(True)
        self.highlightSlider = Slider(self.mainWindow)
        self.highlightSlider.setOrientation(Qt.Horizontal)
        self.highlightSlider.setRange(-100, 100)
        self.highlightSlider.setSingleStep(5)
        self.highlightSlider.setSliderPosition(0)
        self.highlightSlider.valueChanged.connect(lambda value: self.setHighlight(value - self.highlightSlider.previousValue))
        highlightLabel.clicked.connect(lambda: self.highlightSlider.setValue(0))

        shadowsLabel = QPushButton(" Shadows")
        shadowsLabel.setIconSize(QSize(20, 20))
        shadowsLabel.setIcon(QPixmap("icon/shadows.svg"))
        shadowsLabel.setFlat(True)
        self.shadowsSlider = Slider(self.mainWindow)
        self.shadowsSlider.setOrientation(Qt.Horizontal)
        self.shadowsSlider.setRange(-100, 100)
        self.shadowsSlider.setSingleStep(5)
        self.shadowsSlider.setSliderPosition(0)
        self.shadowsSlider.valueChanged.connect(lambda value: self.setShadows(value - self.shadowsSlider.previousValue))
        shadowsLabel.clicked.connect(lambda: self.shadowsSlider.setValue(0))

        lightAdjustmentLayout.addRow(brightnessLabel, self.brightnessSlider)
        lightAdjustmentLayout.addRow(contrastLabel, self.contrastSlider)
        lightAdjustmentLayout.addRow(highlightLabel, self.highlightSlider)
        lightAdjustmentLayout.addRow(shadowsLabel, self.shadowsSlider)

        colorAdjustmentLayout = QFormLayout()
        colorAdjustmentLayout.setRowWrapPolicy(QFormLayout.WrapAllRows)

        saturationLabel = QPushButton(" Saturation")
        saturationLabel.setIconSize(QSize(20, 20))
        saturationLabel.setIcon(QPixmap("icon/saturation.svg"))
        saturationLabel.setFlat(True)
        self.saturationSlider = Slider(self.mainWindow)
        self.saturationSlider.setOrientation(Qt.Horizontal)
        self.saturationSlider.setRange(-100, 100)
        self.saturationSlider.setSingleStep(5)
        self.saturationSlider.setSliderPosition(0)
        self.saturationSlider.valueChanged.connect(lambda value: self.setSaturation(value - self.saturationSlider.previousValue))
        saturationLabel.clicked.connect(lambda: self.saturationSlider.setValue(0))

        warmthLabel = QPushButton(" Warmth")
        warmthLabel.setIconSize(QSize(20, 20))
        warmthLabel.setIcon(QPixmap("icon/warmth.svg"))
        warmthLabel.setFlat(True)
        self.warmthSlider = Slider(self.mainWindow)
        self.warmthSlider.setOrientation(Qt.Horizontal)
        self.warmthSlider.setRange(-100, 100)
        self.warmthSlider.setSingleStep(5)
        self.warmthSlider.setSliderPosition(0)
        self.warmthSlider.valueChanged.connect(lambda value: self.setWarmth(value - self.warmthSlider.previousValue))
        warmthLabel.clicked.connect(lambda: self.warmthSlider.setValue(0))

        colorAdjustmentLayout.addRow(saturationLabel, self.saturationSlider)
        colorAdjustmentLayout.addRow(warmthLabel, self.warmthSlider)

        textureAdjustmentLayout = QFormLayout()
        textureAdjustmentLayout.setRowWrapPolicy(QFormLayout.WrapAllRows)

        sharpnessLabel = QPushButton(" Sharpness ")
        sharpnessLabel.setIconSize(QSize(20, 20))
        sharpnessLabel.setIcon(QPixmap("icon/sharpness.svg"))
        sharpnessLabel.setFlat(True)
        self.sharpnessSlider = Slider(self.mainWindow)
        self.sharpnessSlider.setOrientation(Qt.Horizontal)
        self.sharpnessSlider.setRange(0, 100)
        self.sharpnessSlider.setSingleStep(5)
        self.sharpnessSlider.setSliderPosition(0)
        self.sharpnessSlider.valueChanged.connect(lambda value: self.setSharpness(value - self.sharpnessSlider.previousValue))
        sharpnessLabel.clicked.connect(lambda: self.sharpnessSlider.setValue(0))

        textureAdjustmentLayout.addRow(sharpnessLabel, self.sharpnessSlider)

        adjustmentPanelLayout = QVBoxLayout()
        adjustmentPanelLayout.setContentsMargins(8, 4, 16, 16)
        adjustmentPanelLayout.setAlignment(Qt.AlignTop)
        adjustmentPanelLayout.addWidget(lightLabel)
        adjustmentPanelLayout.addLayout(lightAdjustmentLayout)
        adjustmentPanelLayout.addWidget(colorLabel)
        adjustmentPanelLayout.addLayout(colorAdjustmentLayout)
        adjustmentPanelLayout.addWidget(textureLabel)
        adjustmentPanelLayout.addLayout(textureAdjustmentLayout)

        self.adjustmentPanel = QWidget()
        self.adjustmentPanel.setLayout(adjustmentPanelLayout)
        adjustmentPanelScrollArea = QScrollArea()
        adjustmentPanelScrollArea.setMinimumWidth(260)
        adjustmentPanelScrollArea.setWidgetResizable(True)
        adjustmentPanelScrollArea.setStyleSheet("border: 0px; margin: 0; padding: 0;")

        adjustmentPanelScrollArea.setWidget(self.adjustmentPanel)

        self.mainLayout.addWidget(adjustmentPanelScrollArea)
        self.updateImage()


    def setupImageView(self):
        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.modifiedImageData = np.array(Image.open(self.mainWindow.imageFile), dtype=np.float16)

        self.imageScale = 1

        self.prevVScrollPos = 0
        self.prevVScrollMax = 0
        self.prevHScrollPos = 0
        self.prevHScrollMax = 0

        self.imageScrollArea = ScrollArea()
        self.imageScrollArea.setWidgetResizable(True)
        self.imageScrollArea.setStyleSheet("border: 0px; margin: 0; padding: 0; background: white;")
        self.imageScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.imageScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.imageScrollArea.verticalScrollBar().rangeChanged.connect(self.adaptCurrentScrollToPrev)
        self.imageScrollArea.horizontalScrollBar().rangeChanged.connect(self.adaptCurrentScrollToPrev)
        self.imageScrollArea.resized.connect(self.updateImage)

        self.imageScrollArea.setWidget(self.imageLabel)
        self.mainLayout.addWidget(self.imageScrollArea, 2)

    def changeImage(self):
        self.modifiedImageData = np.array(Image.open(self.mainWindow.imageFile), dtype=np.float16)
        self.brightnessSlider.setSliderPosition(0)
        self.contrastSlider.setValue(0)
        self.highlightSlider.setValue(0)
        self.shadowsSlider.setValue(0)
        self.saturationSlider.setValue(0)
        self.warmthSlider.setValue(0)
        self.sharpnessSlider.setValue(0)
        self.xDifference = None
        self.updateImage()

    def updateImage(self):
        try:
            self.image = self.mainWindow.imageCropWidget.cropedImage()
            print('updated image')
        except:
            self.image = self.mainWindow.modifiedImage
            print('error')
        if self.image.width() > self.imageScrollArea.width() or self.image.height() > self.imageScrollArea.height():
            image = self.image.scaled(self.imageScrollArea.width(), self.imageScrollArea.height(), Qt.KeepAspectRatio,
                                              Qt.SmoothTransformation)
        else:
            image = self.image
        image = image.scaledToHeight(image.height()*self.imageScale)
        self.imageLabel.setPixmap(QPixmap.fromImage(image))


    def zoomImage(self, scaleAdded):
        if self.isVisible():
            self.imageScale += scaleAdded
            self.prevVScrollPos = self.imageScrollArea.verticalScrollBar().value()
            self.prevVScrollMax = self.imageScrollArea.verticalScrollBar().maximum()

            self.prevHScrollPos = self.imageScrollArea.horizontalScrollBar().value()
            self.prevHScrollMax = self.imageScrollArea.horizontalScrollBar().maximum()

            self.updateImage()

            if self.imageScale + scaleAdded >= 2.5:
                self.mainWindow.zoomInAction.setDisabled(True)
                return
            else:
                self.mainWindow.zoomInAction.setDisabled(False)
            if self.imageScale + scaleAdded <= 0.75:
                self.mainWindow.zoomOutAction.setDisabled(True)
                return
            else:
                self.mainWindow.zoomOutAction.setDisabled(False)

    def adaptCurrentScrollToPrev(self):
        vScrollMax = self.imageScrollArea.verticalScrollBar().maximum()
        hScrollMax = self.imageScrollArea.horizontalScrollBar().maximum()

        if self.prevVScrollPos == 0 and self.prevVScrollMax == 0:
            self.prevVScrollPos = 1
            self.prevVScrollMax = 2
        if self.prevHScrollPos == 0 and self.prevHScrollMax == 0:
            self.prevHScrollPos = 1
            self.prevHScrollMax = 2

        self.imageScrollArea.verticalScrollBar().setSliderPosition(vScrollMax * self.prevVScrollPos / self.prevVScrollMax)
        self.imageScrollArea.horizontalScrollBar().setSliderPosition(hScrollMax * self.prevHScrollPos / self.prevHScrollMax)


    def setBrightness(self, value):
        self.modifiedImageData[:, :, :] += value
        cappedData = np.array(self.modifiedImageData, copy=True)
        cappedData[:, :, :] = np.where(cappedData[:, :, :] > 255, 255, np.where(cappedData[:, :, :] < 0, 0, cappedData[:, :, :]))

        self.mainWindow.modifiedImage = Image.fromarray(cappedData.astype(np.uint8), "RGB").toqimage()
        self.updateImage()

    def setContrast(self, value):
        mean = 128
        factor = (259*(value + 255))/(255*(259-value))
        self.modifiedImageData[:, :, :] = factor * (self.modifiedImageData[:, :, :] - mean) + mean


        cappedData = np.array(self.modifiedImageData, copy=True)
        cappedData[:, :, :] = np.where(cappedData[:, :, :] > 255, 255, np.where(cappedData[:, :, :] < 0, 0, cappedData[:, :, :]))

        self.mainWindow.modifiedImage = Image.fromarray(cappedData.astype(np.uint8), "RGB").toqimage()
        self.updateImage()

    def setHighlight(self, value):
        factor = (259 * (value + 255)) / (255 * (259 - value))
        self.modifiedImageData[:, :, :] = np.where(self.modifiedImageData[:, :, :] > 140,
                                                   factor * (self.modifiedImageData[:, :, :] - 140) + 140,
                                                   self.modifiedImageData[:, :, :])

        cappedData = np.array(self.modifiedImageData, copy=True)
        cappedData[:, :, :] = np.where(cappedData[:, :, :] > 255, 255,
                                       np.where(cappedData[:, :, :] < 0, 0, cappedData[:, :, :]))

        self.mainWindow.modifiedImage = Image.fromarray(cappedData.astype(np.uint8), "RGB").toqimage()
        self.updateImage()

    def setShadows(self, value):
        value /= 3
        self.modifiedImageData[:, :, :] = np.where(self.modifiedImageData[:, :, :] < 140,
                                                    self.modifiedImageData[:, :, :] + value,
                                                   self.modifiedImageData[:, :, :])

        cappedData = np.array(self.modifiedImageData, copy=True)
        cappedData[:, :, :] = np.where(cappedData[:, :, :] > 255, 255,
                                       np.where(cappedData[:, :, :] < 0, 0, cappedData[:, :, :]))

        self.mainWindow.modifiedImage = Image.fromarray(cappedData.astype(np.uint8), "RGB").toqimage()
        self.updateImage()

    def setWarmth(self, value):
        self.modifiedImageData[:, :, 0] += value
        self.modifiedImageData[:, :, 1] += (value*0.65)


        cappedData = np.array(self.modifiedImageData, copy=True)
        cappedData[:, :, :] = np.where(cappedData[:, :, :] > 255, 255,
                                       np.where(cappedData[:, :, :] < 0, 0, cappedData[:, :, :]))

        self.mainWindow.modifiedImage = Image.fromarray(cappedData.astype(np.uint8), "RGB").toqimage()
        self.updateImage()

    def setSaturation(self, value):
        meanByPixel = self.modifiedImageData.mean(2)
        factor = (259 * (value + 255)) / (255 * (259 - value))

        self.modifiedImageData[:, :, 0] = factor * (self.modifiedImageData[:, :, 0] - meanByPixel) + meanByPixel
        self.modifiedImageData[:, :, 1] = factor * (self.modifiedImageData[:, :, 1] - meanByPixel) + meanByPixel
        self.modifiedImageData[:, :, 2] = factor * (self.modifiedImageData[:, :, 2] - meanByPixel) + meanByPixel

        cappedData = np.array(self.modifiedImageData, copy=True)
        cappedData[:, :, :] = np.where(cappedData[:, :, :] > 255, 255,
                                       np.where(cappedData[:, :, :] < 0, 0, cappedData[:, :, :]))

        self.mainWindow.modifiedImage = Image.fromarray(cappedData.astype(np.uint8), "RGB").toqimage()
        self.updateImage()

    def setSharpness(self, value):
        if not type(self.xDifference) == np.ndarray:
            self.xDifference = np.diff(self.modifiedImageData, axis=0)
            self.xDifference = np.concatenate((np.array([[[0, 0, 0]]*self.xDifference.shape[1]]), self.xDifference), axis=0)

        #value *= 2
        self.modifiedImageData = self.modifiedImageData + (self.xDifference*(value/10))

        cappedData = np.array(self.modifiedImageData, copy=True)
        cappedData[:, :, :] = np.where(cappedData[:, :, :] > 255, 255,
                                       np.where(cappedData[:, :, :] < 0, 0, cappedData[:, :, :]))

        self.mainWindow.modifiedImage = Image.fromarray(cappedData.astype(np.uint8), "RGB").toqimage()
        self.updateImage()

    def getImage(self):
        cappedData = np.array(self.modifiedImageData, copy=True)
        cappedData[:, :, :] = np.where(cappedData[:, :, :] > 255, 255,
                                       np.where(cappedData[:, :, :] < 0, 0, cappedData[:, :, :]))

        return Image.fromarray(cappedData.astype(np.uint8), "RGB").toqimage()

class Slider(QSlider):
    def __init__(self, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow
        self.previousValue = 0
        self.currentValue = self.value()
        self.valueChanged.connect(self.setPreviousValue)

    def setPreviousValue(self):
        self.mainWindow.changesSaved = False
        self.previousValue = self.currentValue
        self.currentValue = self.value()

class ScrollArea(QScrollArea):
    resized = Signal()

    def resizeEvent(self, e:QResizeEvent):
        super().resizeEvent(e)
        if not e.oldSize() == e.size():
            self.resized.emit()




