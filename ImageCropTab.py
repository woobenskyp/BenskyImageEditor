import math

from PySide6.QtCore import QRect, QSize, QPoint, QPointF
from PySide6.QtGui import QPixmap, Qt, QImage, QPaintEvent, QPainter, QPen, QColor, QMouseEvent, QCursor, QBrush, QIcon, \
    QTransform, QPolygon, QKeyEvent
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication, QPushButton, QHBoxLayout, QComboBox, QSlider
import numpy as np
from PIL import Image


class ImageCropTab(QWidget):
    def __init__(self, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow
        self.mainWindow.imageChanged.connect(self.updateImage)
        self.mainWindow.stackedWidget.currentChanged.connect(self.loadChanges)
        self.imageCrop = ImageCrop(self.mainWindow.modifiedImage)

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 8)

        mainLayout.addWidget(self.imageCrop)

        transformLayout = QHBoxLayout()
        transformLayout.setContentsMargins(8, 8, 8, 8)
        self.rotateLeftButton = QPushButton()
        self.rotateLeftButton.setIcon(QPixmap("icon/rotateleft.svg"))
        self.rotateLeftButton.setIconSize(QSize(24, 24))
        self.rotateLeftButton.clicked.connect(self.rotateLeft)

        self.rotateRightButton = QPushButton()
        self.rotateRightButton.setIcon(QPixmap("icon/rotateright.svg"))
        self.rotateRightButton.setIconSize(QSize(24, 24))
        self.rotateRightButton.clicked.connect(self.rotateRight)

        self.cropRatio = QComboBox()
        self.cropRatio.setIconSize(QSize(24, 24))
        self.cropRatio.addItem(QIcon('icon/freecrop.svg'), 'Free')
        self.cropRatio.addItem(QIcon('icon/1x1crop.svg'), '1:1')
        self.cropRatio.addItem(QIcon('icon/3x2crop.svg'), '3:2')
        self.cropRatio.addItem(QIcon('icon/5x4crop.svg'), '5:4')
        self.cropRatio.addItem(QIcon('icon/7x5crop.svg'), '7:5')
        self.cropRatio.addItem(QIcon('icon/16x9crop.svg'), '16:9')
        self.cropRatio.currentTextChanged.connect(self.imageCrop.changeCropRatio)

        self.flipVerButton = QPushButton()
        self.flipVerButton.setIcon(QPixmap("icon/flipver.svg"))
        self.flipVerButton.setIconSize(QSize(24, 24))
        self.flipVerButton.clicked.connect(self.flipVer)

        self.flipHorButton = QPushButton()
        self.flipHorButton.setIcon(QPixmap("icon/fliphor.svg"))
        self.flipHorButton.setIconSize(QSize(24, 24))
        self.flipHorButton.clicked.connect(self.flipHor)

        transformLayout.addStretch()
        transformLayout.addStretch()
        transformLayout.addWidget(self.rotateLeftButton)
        transformLayout.addWidget(self.rotateRightButton)
        transformLayout.addStretch()
        transformLayout.addWidget(self.cropRatio)
        transformLayout.addStretch()
        transformLayout.addWidget(self.flipVerButton)
        transformLayout.addWidget(self.flipHorButton)
        transformLayout.addStretch()
        transformLayout.addStretch()

        mainLayout.addLayout(transformLayout)
        self.setLayout(mainLayout)

    def cropedImage(self):
        self.imageCrop.image = self.mainWindow.modifiedImage
        return self.imageCrop.cropedImage()

    def rotateLeft(self):
        self.mainWindow.imageAdjustWidget.modifiedImageData = np.rot90(self.mainWindow.imageAdjustWidget.modifiedImageData)
        self.imageCrop.cropRect.pivotLeft(self.mainWindow.modifiedImage.width())
        self.mainWindow.modifiedImage = self.mainWindow.imageAdjustWidget.getImage()
        self.loadChanges()
        self.imageCrop.update()

    def rotateRight(self):
        self.mainWindow.imageAdjustWidget.modifiedImageData = np.rot90(self.mainWindow.imageAdjustWidget.modifiedImageData, -1)
        self.imageCrop.cropRect.pivotRight(self.mainWindow.modifiedImage.height())
        self.mainWindow.modifiedImage = self.mainWindow.imageAdjustWidget.getImage()
        self.loadChanges()
        self.imageCrop.update()


    def flipHor(self):
        self.mainWindow.imageAdjustWidget.modifiedImageData = np.flip(
            self.mainWindow.imageAdjustWidget.modifiedImageData, axis=1)
        self.mainWindow.modifiedImage = self.mainWindow.imageAdjustWidget.getImage()
        self.updateImage()

    def flipVer(self):
        self.mainWindow.imageAdjustWidget.modifiedImageData = np.flip(
            self.mainWindow.imageAdjustWidget.modifiedImageData, axis=0)
        self.mainWindow.modifiedImage = self.mainWindow.imageAdjustWidget.getImage()
        self.updateImage()

    def loadChanges(self):
        if self.isVisible():
            self.imageCrop.image = self.mainWindow.modifiedImage

    def updateImage(self):
        self.rotationSlider.setSliderPosition(0)
        self.imageCrop.setImage(self.mainWindow.modifiedImage)


class ImageCrop(QWidget):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.cropRect = CropRectangle(0, 0, image.width(), image.height())
        self.padding = 56
        self.cropHandleRects = []
        self.cropHandleNames = ["TopLeft", "TopMiddle", "TopRight",
                                "LeftMiddle", "RightMiddle",
                                "BottomLeft", "BottomMiddle", "BottomRight"]
        self.cropHandleCursors = [Qt.SizeFDiagCursor, Qt.SizeVerCursor, Qt.SizeBDiagCursor,
                                  Qt.SizeHorCursor, Qt.SizeHorCursor,
                                  Qt.SizeBDiagCursor, Qt.SizeVerCursor, Qt.SizeFDiagCursor]
        self.dragHandle = QRect()

        self.setMouseTracking(True)
        self.mousePressed = False
        self.shiftHeld = False
        self.selectedhandle = ""

    def setImage(self, image):
        self.image = image
        self.cropRect = CropRectangle(0, 0, image.width(), image.height())
        self.update()

    def rotateCrop(self, value):
        self.cropRect.rotate(value)

        self.fixCropOverflow()
        self.update()

    def fixCropOverflow(self):
        while True:
            cropDistanceFromEdge = {self.cropRect.moveBoundingLeftSide: 0 - self.cropRect.boundingRect().x(),
                                    self.cropRect.moveBoundingTopSide: 0 - self.cropRect.boundingRect().y(),
                                    self.cropRect.moveBoundingRightSide: self.cropRect.boundingRect().x() + self.cropRect.boundingRect().width() - self.image.width(),
                                    self.cropRect.moveBoundingBottomSide: self.cropRect.boundingRect().y() + self.cropRect.boundingRect().height() - self.image.height()}
            if max(cropDistanceFromEdge.values()) > 0:
                max(cropDistanceFromEdge, key=cropDistanceFromEdge.get)(cropDistanceFromEdge[max(cropDistanceFromEdge, key=cropDistanceFromEdge.get)])
            else:
                break

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        scaledImageWidth = self.image.width() / self.cropRect.width() * self.scaledCropRect().width()
        scaledImageHeight = self.image.height() / self.cropRect.height() * self.scaledCropRect().height()
        image = self.image.scaled(scaledImageWidth, scaledImageHeight)
        self.scaledImgSize = image.size()

        cropCenter = QPoint((scaledImageWidth * self.cropRect.center().x() / self.image.width()),
                            (scaledImageHeight * self.cropRect.center().y() / self.image.height()))
        pen = QPen()
        pen.setWidth(0)
        painter.setPen(pen)
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        brush.setColor("white")
        painter.fillRect(self.rect(), brush)

        brush.setStyle(Qt.NoBrush)
        painter.setBrush(brush)

        painter.translate(self.size().width() / 2, self.size().height() / 2)
        painter.rotate(-self.cropRect.rotation)

        painter.drawImage(-cropCenter.x(), -cropCenter.y(), image)

        painter.rotate(self.cropRect.rotation)
        painter.translate(-(self.size().width() / 2), -(self.size().height() / 2))

        self.drawCropFrame(painter)

    def scaledCropRect(self):
        cropSizeRatio = self.cropRect.height() / self.cropRect.width()
        if (self.size().width() - self.padding * 2) * cropSizeRatio < self.size().height() - self.padding * 2:
            scaledWidth = self.size().width() - self.padding * 2
            scaledHeight = scaledWidth * cropSizeRatio
        else:
            scaledHeight = self.size().height() - self.padding * 2
            scaledWidth = scaledHeight / cropSizeRatio

        x = self.size().width() / 2 - scaledWidth / 2
        y = self.size().height() / 2 - scaledHeight / 2
        scaledCropRect = QRect(x, y, scaledWidth, scaledHeight)

        return scaledCropRect

    def changeCropRatio(self, comboText):
        if comboText == 'Free':
            return
        else:
            size = comboText.split(':')
            cropSizeRatio = int(size[1]) / int(size[0])
        if self.cropRect.width() * cropSizeRatio < self.cropRect.height():
            cropWidth = self.cropRect.width()
            cropHeight = cropWidth * cropSizeRatio

            pointF = self.cropRect.verMovementVector*(self.cropRect.height()/2 - cropHeight/2)
            startingPoint = self.cropRect.polygon[0] + pointF.toPoint()
        else:
            cropHeight = self.cropRect.height()
            cropWidth = cropHeight / cropSizeRatio

            pointF = self.cropRect.horMovementVector * (self.cropRect.width()/2 - cropWidth/2)
            startingPoint = self.cropRect.polygon[0] + pointF.toPoint()


        self.cropRect = CropRectangle(startingPoint.x(), startingPoint.y(), cropWidth, cropHeight, self.cropRect.rotation)
        self.update()

    def drawCropFrame(self, painter):
        scaledCropRect = self.scaledCropRect()
        x = scaledCropRect.x()
        y = scaledCropRect.y()

        pen = QPen()
        pen.setColor(QColor('black'))

        if self.mousePressed:
            pen.setWidth(1)
            pen.setColor('grey')
            painter.setPen(pen)
            painter.drawLine(x + scaledCropRect.width() / 3, y, x + scaledCropRect.width() / 3,
                             y + scaledCropRect.height())
            painter.drawLine(x + scaledCropRect.width() / 3 * 2, y, x + scaledCropRect.width() / 3 * 2,
                             y + scaledCropRect.height())
            painter.drawLine(x, y + scaledCropRect.height() / 3, x + scaledCropRect.width(),
                             y + scaledCropRect.height() / 3)
            painter.drawLine(x, y + scaledCropRect.height() / 3 * 2, x + scaledCropRect.width(),
                             y + scaledCropRect.height() / 3 * 2)
            pen.setColor('black')

        pen.setWidth(4)
        painter.setPen(pen)

        painter.drawRect(x, y, scaledCropRect.width() + 1, scaledCropRect.height() + 1)

        self.cropHandleRects = []
        if scaledCropRect.width() < 28 * 3 + 10:
            xHandleLength = scaledCropRect.width() / 4
        else:
            xHandleLength = 28

        if scaledCropRect.height() < 28 * 3 + 10:
            yHandleLength = scaledCropRect.height() / 4
        else:
            yHandleLength = 28
        self.xHandlesLength = xHandleLength
        self.yHandleLength = yHandleLength

        x -= 3
        y -= 3
        painter.drawLine(x, y, x + xHandleLength, y)
        painter.drawLine(x, y, x, y + yHandleLength)
        self.cropHandleRects.append(QRect(x - xHandleLength, y - yHandleLength, xHandleLength * 2, yHandleLength * 2))

        x += 4
        painter.drawLine(x + scaledCropRect.width() / 2 - xHandleLength / 2, y,
                         x + scaledCropRect.width() / 2 + xHandleLength / 2, y)
        self.cropHandleRects.append(
            QRect(x + xHandleLength + 1, y - yHandleLength, scaledCropRect.width() - xHandleLength * 2 - 1,
                  yHandleLength * 2))

        x += 3
        painter.drawLine(x + scaledCropRect.width() - xHandleLength, y, x + scaledCropRect.width(), y)
        painter.drawLine(x + scaledCropRect.width(), y, x + scaledCropRect.width(), y + yHandleLength)
        self.cropHandleRects.append(
            QRect(x + scaledCropRect.width() - xHandleLength, y - yHandleLength, xHandleLength * 2, yHandleLength * 2))

        # ---
        x -= 7
        y += 4
        painter.drawLine(x, y + scaledCropRect.height() / 2 - yHandleLength / 2, x,
                         y + scaledCropRect.height() / 2 + yHandleLength / 2)
        self.cropHandleRects.append(QRect(x - xHandleLength, y + yHandleLength + 1, xHandleLength * 2,
                                          scaledCropRect.height() - yHandleLength * 2 - 1))

        x += 7
        painter.drawLine(x + scaledCropRect.width(), y + scaledCropRect.height() / 2 - yHandleLength / 2,
                         x + scaledCropRect.width(), y + scaledCropRect.height() / 2 + yHandleLength / 2)
        self.cropHandleRects.append(
            QRect(x + scaledCropRect.width() - xHandleLength, y + yHandleLength + 1, xHandleLength * 2,
                  scaledCropRect.height() - yHandleLength * 2 - 1))

        # ---
        y += 3
        x -= 6
        painter.drawLine(x, y + scaledCropRect.height() - yHandleLength, x, y + scaledCropRect.height())
        painter.drawLine(x, y + scaledCropRect.height(), x + xHandleLength, y + scaledCropRect.height())
        self.cropHandleRects.append(
            QRect(x - xHandleLength, y + scaledCropRect.height() - yHandleLength, xHandleLength * 2, yHandleLength * 2))

        x += 3
        painter.drawLine(x + scaledCropRect.width() / 2 - xHandleLength / 2, y + scaledCropRect.height(),
                         x + scaledCropRect.width() / 2 + xHandleLength / 2, y + scaledCropRect.height())
        self.cropHandleRects.append(QRect(x + xHandleLength + 1, y + scaledCropRect.height() - yHandleLength,
                                          scaledCropRect.width() - xHandleLength * 2 - 1, yHandleLength * 2))

        x += 3
        painter.drawLine(x + scaledCropRect.width(), y + scaledCropRect.height() - yHandleLength,
                         x + scaledCropRect.width(), y + scaledCropRect.height())
        painter.drawLine(x + scaledCropRect.width() - xHandleLength, y + scaledCropRect.height(),
                         x + scaledCropRect.width(), y + scaledCropRect.height())
        self.cropHandleRects.append(
            QRect(x + scaledCropRect.width() - xHandleLength, y + scaledCropRect.height() - yHandleLength,
                  xHandleLength * 2, yHandleLength * 2))

        self.dragHandle = QRect(scaledCropRect.x() + xHandleLength, scaledCropRect.y() + yHandleLength,
                                scaledCropRect.width() - 2 * xHandleLength, scaledCropRect.height() - 2 * yHandleLength)

    def mouseMoveEvent(self, event: QMouseEvent):
        super().mouseMoveEvent(event)
        inHandle = False
        for i, rect in enumerate(self.cropHandleRects):
            if rect.contains(event.pos()):
                inHandle = True
                cursor = self.cursor()
                cursor.setShape(self.cropHandleCursors[i])
                self.setCursor(cursor)
                break
        if not inHandle and self.dragHandle.contains(event.pos()):
            inHandle = True
            cursor = self.cursor()
            cursor.setShape(Qt.OpenHandCursor)
            self.setCursor(cursor)

        if not inHandle:
            cursor = self.cursor()
            cursor.setShape(Qt.ArrowCursor)
            self.setCursor(cursor)

        if self.mousePressed:
            xScale = self.image.width() / self.scaledImgSize.width()
            yScale = self.image.height() / self.scaledImgSize.height()

            xMovement = (event.x() - self.prevX) * xScale
            yMovement = (event.y() - self.prevY) * yScale

            minimumSize = 70
            if self.selectedhandle == "DragHandle":
                translatedRect = self.cropRect.polygon.translated(xMovement, yMovement)
                if xMovement < 0 <= translatedRect.boundingRect().x():
                    self.cropRect.polygon.translate(xMovement, 0)
                if xMovement > 0 and translatedRect.boundingRect().x() + translatedRect.boundingRect().width() < self.image.width():
                    self.cropRect.polygon.translate(xMovement, 0)
                if yMovement < 0 < translatedRect.boundingRect().y():
                    self.cropRect.polygon.translate(0, yMovement)
                if yMovement > 0 and translatedRect.boundingRect().y() + translatedRect.boundingRect().height()  < self.image.height():
                    self.cropRect.polygon.translate(0, yMovement)

            leftBounding = self.cropRect.boundingRect().x() + 5
            topBounding = self.cropRect.boundingRect().y() + 5
            rightBounding = self.cropRect.boundingRect().x() + self.cropRect.boundingRect().width() - 10
            bottomBounding = self.cropRect.boundingRect().y() + self.cropRect.boundingRect().height() - 10


            xHorBoundingMov = abs(self.cropRect.horMovementVector.x() / 1) * xMovement
            yHorBoundingMov = abs(self.cropRect.horMovementVector.y() / 1) * xMovement
            y2HorBoundingMov = abs(self.cropRect.horMovementVector.y() / 1) * xMovement

            yVerBoundingMov = abs(self.cropRect.verMovementVector.y() / 1) * yMovement
            xVerBoundingMov = abs(self.cropRect.verMovementVector.x() / 1) * yMovement
            x2VerBoundingMov = abs(self.cropRect.verMovementVector.x() / 1) * yMovement


            diagonalMove = False
            if "Left" in self.selectedhandle:
                if self.scaledCropRect().width() - (event.x() - self.prevX) > self.xHandlesLength and self.cropRect.width() - xMovement > minimumSize:
                    if (leftBounding + xHorBoundingMov >= 0 and topBounding + yHorBoundingMov >= 0 and bottomBounding - y2HorBoundingMov <= self.image.height()) or xMovement > 0:
                        if not "Middle" in self.selectedhandle and self.shiftHeld:
                            movement = math.sqrt(xMovement**2 + yMovement**2) * (1 if xMovement+yMovement > 0 else -1)
                            self.cropRect.moveLeftSide(movement)
                            diagonalMove = True
                        else:
                            self.cropRect.moveLeftSide(xMovement, keepAspectRatio=self.shiftHeld)


            if "Right" in self.selectedhandle:
                if self.scaledCropRect().width() + (event.x() - self.prevX) > self.xHandlesLength and self.cropRect.width() + xMovement > minimumSize:
                    if (rightBounding + xHorBoundingMov <= self.image.width() and topBounding - yHorBoundingMov >= 0 and bottomBounding + y2HorBoundingMov <= self.image.height()) or xMovement < 0:
                        if not "Middle" in self.selectedhandle and self.shiftHeld:
                            movement = math.sqrt(xMovement ** 2 + yMovement ** 2) * (1 if xMovement+yMovement > 0 else -1)
                            self.cropRect.moveRightSide(movement)
                            diagonalMove = True
                        else:
                            self.cropRect.moveRightSide(xMovement, keepAspectRatio=self.shiftHeld)

            if "Bottom" in self.selectedhandle:
                if self.scaledCropRect().height() + (event.y() - self.prevY) > self.yHandleLength and self.cropRect.height() + yMovement > minimumSize:
                    if (bottomBounding + yVerBoundingMov <= self.image.height() and leftBounding - xVerBoundingMov >= 0 and rightBounding + x2VerBoundingMov <= self.image.width()) or yMovement < 0:
                        if not "Middle" in self.selectedhandle and self.shiftHeld and diagonalMove:
                            movement = math.sqrt(xMovement**2 + yMovement**2) * self.cropRect.height()/self.cropRect.width() * (1 if xMovement+yMovement > 0 else -1)
                            self.cropRect.moveBottomSide(movement)
                        else:
                            self.cropRect.moveBottomSide(yMovement, keepAspectRatio=self.shiftHeld)

            if "Top" in self.selectedhandle:
                if self.scaledCropRect().height() - (event.y() - self.prevY) > self.yHandleLength and self.cropRect.height() - yMovement > minimumSize:
                    if (topBounding + yVerBoundingMov >= 0 and leftBounding + xVerBoundingMov >= 0 and rightBounding - x2VerBoundingMov <= self.image.width()) or yMovement > 0:
                        if not "Middle" in self.selectedhandle and self.shiftHeld and diagonalMove:
                            movement = math.sqrt(xMovement ** 2 + yMovement ** 2) * self.cropRect.height() / self.cropRect.width() * (1 if xMovement+yMovement > 0 else -1)
                            self.cropRect.moveTopSide(movement)
                        else:
                            self.cropRect.moveTopSide(yMovement, keepAspectRatio=self.shiftHeld)
            self.update()

        self.prevX = event.x()
        self.prevY = event.y()
        if self.mousePressed:
            if self.selectedhandle == "DragHandle":
                cursorShape = Qt.ClosedHandCursor
            else:
                cursorShape = self.cropHandleCursors[self.cropHandleNames.index(self.selectedhandle)]
            cursor = self.cursor()
            cursor.setShape(cursorShape)
            self.setCursor(cursor)

    def mousePressEvent(self, event: QMouseEvent):
        self.setFocus()
        if event.button() == Qt.LeftButton:
            inHandle = False
            for i, rect in enumerate(self.cropHandleRects):
                if rect.contains(event.pos()):
                    self.selectedhandle = self.cropHandleNames[i]
                    self.mousePressed = True
                    self.prevX = event.x()
                    self.prevY = event.y()
                    inHandle = True
                    break
            if not inHandle and self.dragHandle.contains(event.pos()):
                self.selectedhandle = "DragHandle"
                self.mousePressed = True
                self.prevX = event.x()
                self.prevY = event.y()

                cursor = self.cursor()
                cursor.setShape(Qt.ClosedHandCursor)
                self.setCursor(cursor)
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.mousePressed = False
        self.selectedhandle = ""
        self.update()

    def keyPressEvent(self, event:QKeyEvent):
        print(event.key())
        if event.key() == Qt.Key_Shift:
            self.shiftHeld = True

    def keyReleaseEvent(self, event:QKeyEvent):
        if event.key() == Qt.Key_Shift:
            self.shiftHeld = False

    def cropedImage(self):
        canvas = QPixmap(int(self.cropRect.width()), int(self.cropRect.height()))
        canvas.fill(Qt.white)
        painter = QPainter(canvas)

        painter.translate(self.cropRect.width() / 2, self.cropRect.height() / 2)
        painter.rotate(-self.cropRect.rotation)
        painter.drawImage(-self.cropRect.center().x(), -self.cropRect.center().y(), self.image)
        painter.end()
        return canvas.toImage()


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


class CropRectangle:
    def __init__(self, x, y, width, height, rotation=None):
        if rotation == None:
            self.polygon = QPolygon([QPoint(x, y), QPoint(width, y),
                                     QPoint(x, height), QPoint(width, height)])
            self.horMovementVector = QPointF(1, 0)
            self.verMovementVector = QPointF(0, 1)
            self.rotation = 0
        else:
            self.rotation = rotation
            transform = QTransform()
            transform.rotate(self.rotation)

            self.horMovementVector = transform.map(QPointF(1, 0))
            self.verMovementVector = transform.map(QPointF(0, 1))

            self.polygon = QPolygon([QPoint(x, y), QPoint(x, y)+(self.horMovementVector*width).toPoint(),
                                     QPoint(x, y)+(self.verMovementVector*height).toPoint(), QPoint(x, y)+(self.horMovementVector*width).toPoint() + (self.verMovementVector*height).toPoint()])

    def width(self):
        width = math.sqrt((self.polygon.at(0).x() - self.polygon.at(1).x()) ** 2 +
                          (self.polygon.at(0).y() - self.polygon.at(1).y()) ** 2)
        return width

    def height(self):
        height = math.sqrt((self.polygon.at(0).x() - self.polygon.at(2).x()) ** 2 +
                           (self.polygon.at(0).y() - self.polygon.at(2).y()) ** 2)
        return height

    def pivotLeft(self, width):
        point0 = QPoint(self.polygon[1].y(), width-self.polygon[1].x())
        point1 = QPoint(self.polygon[3].y(), width-self.polygon[3].x())
        point2 = QPoint(self.polygon[0].y(), width-self.polygon[0].x())
        point3 = QPoint(self.polygon[2].y(), width-self.polygon[2].x())
        self.polygon = QPolygon([point0, point1, point2, point3])

    def pivotRight(self, height):
        point0 = QPoint(height-self.polygon[2].y(), self.polygon[2].x())
        point1 = QPoint(height-self.polygon[0].y(), self.polygon[0].x())
        point2 = QPoint(height-self.polygon[3].y(), self.polygon[3].x())
        point3 = QPoint(height-self.polygon[1].y(), self.polygon[1].x())
        print(self.polygon,"\n", QPolygon([point0, point1, point2, point3]))
        self.polygon = QPolygon([point0, point1, point2, point3])

    def moveLeftSide(self, pixel, keepAspectRatio=False):
        if not keepAspectRatio:
            movement = self.horMovementVector * pixel
            self.polygon[0] += movement.toPoint()
            self.polygon[2] += movement.toPoint()
        else:
            widthUnit = 1
            heightUnit = self.height() / self.width()
            widthPixelMove = pixel * widthUnit
            heightPixelMove = pixel / 2 * heightUnit

            self.moveLeftSide(widthPixelMove)
            self.moveTopSide(heightPixelMove)
            self.moveBottomSide(-heightPixelMove)

    def moveRightSide(self, pixel, keepAspectRatio=False):
        if not keepAspectRatio:
            movement = self.horMovementVector * pixel
            self.polygon[1] += movement.toPoint()
            self.polygon[3] += movement.toPoint()
        else:
            widthUnit = 1
            heightUnit = self.height() / self.width()
            widthPixelMove = pixel * widthUnit
            heightPixelMove = pixel / 2 * heightUnit

            self.moveRightSide(widthPixelMove)
            self.moveTopSide(-heightPixelMove)
            self.moveBottomSide(heightPixelMove)

    def moveTopSide(self, pixel, keepAspectRatio=False):
        if not keepAspectRatio:
            movement = self.verMovementVector * pixel
            self.polygon[0] += movement.toPoint()
            self.polygon[1] += movement.toPoint()
        else:
            heightUnit = 1
            widthUnit = self.width() / self.height()
            heightPixelMove = pixel * heightUnit
            widthPixelMove = pixel / 2 * widthUnit

            self.moveTopSide(heightPixelMove)
            self.moveLeftSide(widthPixelMove)
            self.moveRightSide(-widthPixelMove)

    def moveBottomSide(self, pixel, keepAspectRatio=False):
        if not keepAspectRatio:
            movement = self.verMovementVector * pixel
            self.polygon[2] += movement.toPoint()
            self.polygon[3] += movement.toPoint()
        else:
            heightUnit = 1
            widthUnit = self.width() / self.height()
            heightPixelMove = pixel * heightUnit
            widthPixelMove = pixel / 2 * widthUnit

            self.moveBottomSide(heightPixelMove)
            self.moveLeftSide(-widthPixelMove)
            self.moveRightSide(widthPixelMove)

    def _setBoundingRect(self, newRect):
        newRectAspectRatio = newRect.width() / newRect.height()
        currentBoundingAspectRatio = self.boundingRect().width() / self.boundingRect().height()
        if int(newRectAspectRatio) == int(currentBoundingAspectRatio):
            newPolygon = QPolygon()
            for point in self.polygon.toList():
                newX = newRect.width() * (
                            point.x() - self.boundingRect().x()) / self.boundingRect().width() + newRect.x()
                newY = newRect.height() * (
                            point.y() - self.boundingRect().y()) / self.boundingRect().height() + newRect.y()
                newPolygon.append(QPoint(newX, newY))
            self.polygon = newPolygon
        else:
            raise Exception("Aspect Ratio not kept")

    def moveBoundingLeftSide(self, pixel):
        resizedRect = self.polygon.boundingRect()
        widthUnit = 1
        heightUnit = resizedRect.height() / resizedRect.width()
        widthPixelMove = pixel * widthUnit
        heightPixelMove = pixel / 2 * heightUnit

        resizedRect.setX(resizedRect.x() + widthPixelMove)
        resizedRect.setY(resizedRect.y() + heightPixelMove)
        resizedRect.setHeight(resizedRect.height() - heightPixelMove)

        self._setBoundingRect(resizedRect)

    def moveBoundingTopSide(self, pixel):
        resizedRect = self.polygon.boundingRect()
        heightUnit = 1
        widthUnit = resizedRect.width() / resizedRect.height()
        heightPixelMove = pixel * heightUnit
        widthPixelMove = pixel / 2 * widthUnit

        resizedRect.setY(resizedRect.y() + heightPixelMove)
        resizedRect.setX(resizedRect.x() + widthPixelMove)
        resizedRect.setWidth(resizedRect.width() - widthPixelMove)

        self._setBoundingRect(resizedRect)

    def moveBoundingBottomSide(self, pixel):
        resizedRect = self.polygon.boundingRect()
        heightUnit = 1
        widthUnit = resizedRect.width() / resizedRect.height()
        heightPixelMove = pixel * heightUnit
        widthPixelMove = pixel / 2 * widthUnit

        resizedRect.setHeight(resizedRect.height() - heightPixelMove)
        resizedRect.setX(resizedRect.x() + widthPixelMove)
        resizedRect.setWidth(resizedRect.width() - widthPixelMove)

        self._setBoundingRect(resizedRect)

    def moveBoundingRightSide(self, pixel):
        resizedRect = self.polygon.boundingRect()
        widthUnit = 1
        heightUnit = resizedRect.height() / resizedRect.width()
        widthPixelMove = pixel * widthUnit
        heightPixelMove = pixel / 2 * heightUnit

        resizedRect.setWidth(resizedRect.width() - widthPixelMove)
        resizedRect.setY(resizedRect.y() + heightPixelMove)
        resizedRect.setHeight(resizedRect.height() - heightPixelMove)

        self._setBoundingRect(resizedRect)

    def rotate(self, degree):
        self.rotation += degree
        centerPoint = self.center()
        originCenteredPolygon = self.polygon.translated(-centerPoint.x(), -centerPoint.y())
        transform = QTransform()
        transform.rotate(degree)
        rotatedPolygon = transform.map(originCenteredPolygon)
        rotatedPolygon.translate(centerPoint.x(), centerPoint.y())
        self.horMovementVector = transform.map(self.horMovementVector)
        self.verMovementVector = transform.map(self.verMovementVector)
        self.polygon = rotatedPolygon

    def center(self):
        centerPoint = QPoint(
            (self.polygon.at(0).x() + self.polygon.at(1).x() + self.polygon.at(2).x() + self.polygon.at(3).x()) / 4,
            (self.polygon.at(0).y() + self.polygon.at(1).y() + self.polygon.at(2).y() + self.polygon.at(3).y()) / 4)
        return centerPoint

    def boundingRect(self):
        return self.polygon.boundingRect()
