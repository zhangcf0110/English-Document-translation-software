from PyQt5.QtWidgets import *
import  sys
# NewWidget是随便起的名字，QWidget是要重写的，继承给NewWidget
class NewWidget(QWidget):
    def closeEvent(self, event):
        result = QMessageBox.question(self, "Xpath Robot", "Do you want to exit?", QMessageBox.Yes | QMessageBox.No)
        if(result == QMessageBox.Yes):
            event.accept()
            print(1)
        else:
            event.ignore()
