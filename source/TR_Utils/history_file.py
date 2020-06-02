from PyQt5.QtWidgets import QWidget,QLabel,QListWidget,QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from TR_Utils.configure import config
class History_file(QWidget):

    def __init__(self, pdfWrapper):
        super().__init__()
        self.pdfWrapper = pdfWrapper


        self.setWindowTitle("最近打开的文件")
        self.setWindowIcon(QIcon("./sample/osave.ico"))
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setMaximumSize(500,500)

        self.resize(500,300)

        label=QLabel("文件名")

        label.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
        label.setStyleSheet("font-size:12pt;color:red")
        label.setFixedHeight(25)


        self.history_pdf_path_list, self.history_pdf_name_list = self.getHistoryPDF()
        layout=QVBoxLayout()
        self.setLayout(layout)
        self.list_widget_of_history_pdf = QListWidget()

        self.list_widget_of_history_pdf.addItems(self.history_pdf_name_list)
        layout.addWidget(label)
        layout.addWidget(self.list_widget_of_history_pdf)
        layout.setContentsMargins(0, 0, 0, 0)

        self.list_widget_of_history_pdf.itemDoubleClicked.connect(self.historyListWidgetDBClicked)


    def getHistoryPDF(self):
        tp = config.items('history_pdf')
        name_list = []
        path_list = []
        for item in tp:
            name_list.append(item[0])
            path_list.append(item[1])

        return path_list, name_list

    def historyListWidgetDBClicked(self, item):
        for path in self.history_pdf_path_list:
            if item.text() in path.lower():
                try:
                    self.pdfWrapper.changePDF(path)
                    self.close()
                except:
                    self.close()

# if __name__ == '__main__':
#     import sys
#     app = QApplication(sys.argv)
#
#     mainWindow = History_file()
#     mainWindow.show()
#
#     sys.exit(app.exec_())