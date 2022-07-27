from PySide6.QtSvgWidgets import QSvgWidget
import PySide6.QtSvg
from PySide6.QtWidgets import QApplication
from WelcomeWindow import WelcomeWindow


app = QApplication()

welcomeWindow = WelcomeWindow()
welcomeWindow.show()

app.exec()
