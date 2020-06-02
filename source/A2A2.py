import os
import sys
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl,QEvent,Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
import webbrowser
import platform
from TR_Utils.wordtopdf import createPdf
from TR_Utils.closetip import NewWidget
from TR_Utils.controller import con
from TR_Utils.watch_clip import WatchClip
from TR_Utils.text_filter import TextFilter
from TR_Utils.history_file import History_file
from TR_Utils.configure import config,config_path


sysstr = platform.system()
is_win = is_linux = is_mac = False

if sysstr == "Windows":
    is_win = True
elif sysstr == "Linux":
    is_linux = True
elif sysstr == "Mac":
    is_mac = True
## print('System: %s' % sysstr)


MAX_CHARACTERS = 5000     # 最大翻译数

class WebView(QWebEngineView):

    def __init__(self):
        ###print('init webView')
        super(WebView, self).__init__()
        self._glwidget = None
        self.pdf_js_path = "file:///" + os.path.join(os.getcwd(), "pdfjs", "web", "viewer.html")
        pdf_path = "file:///" + os.path.join(os.getcwd(), "sample", "induction.pdf")
        if sys.platform == "win32":
            self.pdf_js_path = self.pdf_js_path.replace("\\", "/")
            pdf_path = pdf_path.replace('\\', '/')
        self.changePDF(pdf_path)
        self.setAcceptDrops(True)
        self.installEventFilter(self)

    def dragEnterEvent(self,e):

        if is_linux or is_mac:
            if e.mimeData().hasFormat('text/plain') and e.mimeData().text()[-6:-2] == ".pdf":
                e.accept()
            else:
                e.ignore()
        elif is_win:
            if e.mimeData().text()[-4:] == ".pdf":
                e.accept()
            else:
                e.ignore()



    def dropEvent(self,e):

        self.changePDF(e.mimeData().text())

    def event(self, e):
        """
        Detect child add event, as QWebEngineView do not capture mouse event directly,
        the child layer _glwidget is implicitly added to QWebEngineView and we track mouse event through the glwidget
        :param e: QEvent
        :return: super().event(e)
        """
        if self._glwidget is None:
            if e.type() == QEvent.ChildAdded and e.child().isWidgetType():
                    ###print('child add')
                    self._glwidget = e.child()
                    self._glwidget.installEventFilter(self)
        return super().event(e)

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonRelease and source is self._glwidget:
            con.pdfViewMouseRelease.emit()
        return super().eventFilter(source, event)

    def changePDF(self, pdf_path):


        self.load(QUrl.fromUserInput('%s?file=%s' % (self.pdf_js_path, pdf_path)))
        if sys.platform == 'win32' and 'sample' not in pdf_path:
            if "/" in pdf_path:

                with open(config_path, "w",encoding='GB2312') as f:
                    config.set("history_pdf", pdf_path.split('/')[-1], pdf_path)
                    config.write(f)
            else:

                config.set("history_pdf",  pdf_path.split('\\')[-1].split('.')[0], pdf_path)
                with open("config.txt", "w", encoding='GB2312') as f:
                    config.write(f)






class MainWindow(QMainWindow,):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("翻译")
        self.setWindowIcon(QIcon("./sample/logo.ico"))

        self.thread_my = WatchClip()
        self.thread_my.start()



        '''    *****************************  create translation area  ******************************     '''


        TAB=QTabWidget()
        TAB.setMinimumWidth(2)

        tab1 = QWidget()
        tab2 = QWidget()
        TAB.addTab(tab1, "译文")
        TAB.addTab(tab2, "原文")


        self.translate_ori = QPlainTextEdit()
        self.translate_ori.setStyleSheet("font: 12pt Roboto")

        self.translate_res = QPlainTextEdit()
        self.translate_res.setStyleSheet("font: 12pt Roboto")

        res_con = QVBoxLayout()
        res_con.addWidget(self.translate_res)
        res_con.setContentsMargins(0, 0, 0, 0)  # 设置距离左上右下的距离
        tab1.setLayout(res_con)

        ori_con = QVBoxLayout()
        ori_con.addWidget(self.translate_ori)
        ori_con.setContentsMargins(0, 0, 0, 0)  # 设置距离左上右下的距离
        tab2.setLayout(ori_con)


        # 字体大小
        self.selectable_text_size = ['8','9','10','11','12','13','14','15',]
        self.text_size_combobox = QComboBox()
        self.text_size_combobox.addItems(self.selectable_text_size)
        self.text_size_combobox.setCurrentIndex(4)

        label1 = QLabel('字号:')
        label1.setAlignment(Qt.AlignVCenter)
        label2 = QLabel('链接:')
        label2.setAlignment(Qt.AlignVCenter)



        ''' -----------快速访问--------------'''

        # 百度翻译
        def open_url_bf():
            try:
                webbrowser.open("https://sci-hub.org.cn/", new=0)
            except:
                pass
        bf_btn= QPushButton("SCI-HUB")
        bf_btn.adjustSize()
        bf_btn.setStyleSheet("QPushButton:pressed {background-color:yellow}")
        bf_btn.pressed.connect(open_url_bf)

        # 知网
        def open_url_cn():
            try:
                webbrowser.open("https://dict.cnki.net/", new=0)
            except:
                pass
        cn_btn= QPushButton("CNKI")
        cn_btn.adjustSize()
        cn_btn.setStyleSheet("QPushButton:pressed {background-color:yellow}")
        cn_btn.pressed.connect(open_url_cn)





        resHboxLayout = QHBoxLayout()
        resHboxLayout.addWidget(label2)
        resHboxLayout.addStretch()
        resHboxLayout.addWidget(bf_btn)
        resHboxLayout.addStretch()
        resHboxLayout.addWidget(cn_btn)
        resHboxLayout.addStretch()
        resHboxLayout.addWidget(label1)
        resHboxLayout.addWidget(self.text_size_combobox)
        resHboxLayout.setContentsMargins(0, 0, 0, 0)


        resWidget = QWidget()
        resWidget.setLayout(resHboxLayout)


        # toolbar
        self.tool=QToolBar()
        self.addToolBar(self.tool)

        self.filter = TextFilter()
        vbox = QVBoxLayout()
        vbox.addWidget(TAB)
        vbox.addWidget(resWidget)
        vbox.addWidget(self.tool)

        gbox = QGroupBox()
        gbox.setStyleSheet("font: 12pt Roboto")
        gbox.setLayout(vbox)

        self.pdfWrapper = WebView()
        self.pdfWrapper.setContentsMargins(0, 0, 0, 0)
        gbox.setContentsMargins(0, 0, 0, 0)

        hBoxLayout = QHBoxLayout()
        # 左右窗口可动态变化
        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(self.pdfWrapper)
        splitter1.addWidget(gbox)
        hBoxLayout.addWidget(splitter1)

        widget = QWidget()
        widget.setLayout(hBoxLayout)

        self.setCentralWidget(widget)
        self.recent_text = ""
        self.showMaximized()






        '''    *****************************  create the  toolbar and menu bar  ******************************     '''


        #添加间隔00
        self.t_s00 = QAction( '                            ', self)
        self.t_s00.setEnabled(False)
        self.tool.addAction(self.t_s00)

        #添加间隔0
        self.t_s0 = QAction( '                            ', self)
        self.t_s0.setEnabled(False)
        self.tool.addAction(self.t_s0)
        # self.tool.insertSeparator(self.t_s0)

        # 打开PDF
        self.t_folder_open = QAction(QIcon("./sample/folder_open.ico"),'打开PDF',self)
        self.t_folder_open.setShortcut('Ctrl+O')
        self.tool.addAction(self.t_folder_open)

        #添加间隔1
        self.t_s1 = QAction( '                        ', self)
        self.t_s1.setEnabled(False)
        self.tool.addAction(self.t_s1)
        self.tool.insertSeparator(self.t_s1)

        # 最近打开的
        self.t_history_look = QAction(QIcon("./sample/osave.ico"),'最近打开的文件',self)

        self.tool.insertSeparator(self.t_history_look)
        self.tool.addAction(self.t_history_look)

        #添加间隔1
        self.t_s2 = QAction( '                      ', self)
        self.t_s2.setEnabled(False)
        self.tool.addAction(self.t_s2)
        self.tool.insertSeparator(self.t_s2)

        # 帮助
        self.t_help = QAction(QIcon("./sample/help.ico"),'更多知识',self)
        self.t_help.setShortcut('Alt+F')
        self.tool.insertSeparator(self.t_help)
        self.tool.addAction(self.t_help)

        #添加间隔2
        self.t_s3 = QAction( '                      ', self)
        self.t_s3.setEnabled(False)
        self.tool.addAction(self.t_s3)
        self.tool.insertSeparator(self.t_s3)

        # 退出
        self.t_hid = QAction(QIcon("./sample/close.ico"),'隐藏',self)
        self.t_hid.setShortcut('Alt+F4')
        self.tool.insertSeparator(self.t_hid)
        self.tool.addAction(self.t_hid)

        self.tool.actionTriggered[QAction].connect(self.openDir)




    def openDir(self, qaction):

        if qaction.text() == '打开文件':
            try:
                fd = QFileDialog.getOpenFileName(self, '打开文件', './', 'All(*.*);;PDF(*.pdf)', 'All(*.*)')
                if  fd[0].split('/')[-1].split(".")[-1] == "pdf":
                    self.pdfWrapper.changePDF(fd[0])

                elif  fd[0].split('/')[-1].split(".")[-1] == "docx" or fd[0].split('/')[-1].split(".")[-1] == "doc":
                      ss = fd[0].split(".")[:-1]
                      self.sss = str(ss[0]) + ".pdf"
                      createPdf(fd[0],self.sss)
                      self.pdfWrapper.changePDF(self.sss)
            except:
                  pass


        elif qaction.text() == '最近打开的文件':
            try :
                self.window = History_file(self.pdfWrapper)
                self.window.show()
            except:
                pass

        elif  qaction.text() == '更多知识':
            try:
                webbrowser.open("https://search.chongbuluo.com/", new=0)
            except:
                pass

        elif qaction.text() == '隐藏':

            self.pdfWrapper.resize(self.width(),self.height())

    def getHistoryPDF(self):
        tp = config.items('history_pdf')
        name_list = []
        path_list = []
        for item in tp:
            name_list.append(item[0])
            path_list.append(item[1])
        return path_list, name_list

    def updateTranslation(self, cur_text):
        self.translate_res.clear()
        self.translate_res.setPlainText(cur_text)

    def updateByMouseRelease(self):
        # print('no seletion to translate')
        if self.pdfWrapper.hasSelection():

            to_translate_text = self.pdfWrapper.selectedText()
            if len(to_translate_text) > MAX_CHARACTERS:
                hint_str = '请选择少于%d个英文字符' % MAX_CHARACTERS
                # print(hint_str)
                self.translate_ori.setText(hint_str)

                return
            else:
                if self.recent_text == to_translate_text:
                    # print('same as before, not new translate')
                    return
                else:
                    hint_str = '正在翻译...'
                    filtered = self.filter.removeDashLine(to_translate_text)
                    # print(filtered)
                    self.recent_text = to_translate_text
                    self.translate_ori.setPlainText(filtered)
                    self.translate_res.setPlainText(hint_str)
                    # self.thread_my.setTranslateText(filtered)

    def updateByTextEdit(self):
        # print('TextEdited')
        self.thread_my.setTranslateText(self.translate_ori.toPlainText())

    def updateOriTextSizeByIndexChanged(self, index):
        self.translate_ori.setStyleSheet("font: {0}pt Roboto".format(self.selectable_text_size[index]))

    def updateResTextSizeByIndexChanged(self, index):
        self.translate_res.setStyleSheet("font: {0}pt Roboto".format(self.selectable_text_size[index]))

    def closeEvent(self, event):
        self.thread_my.expired()
        result = QMessageBox.question(self, "警告", "Do you want to exit?", QMessageBox.Yes | QMessageBox.No)
        if (result == QMessageBox.Yes):
            event.accept()
            try:
                os.remove(self.sss)
            except:
                pass
        else:
            event.ignore()




if __name__ == '__main__':

    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()


    con.translationChanged.connect(mainWindow.updateTranslation)
    con.pdfViewMouseRelease.connect(mainWindow.updateByMouseRelease)
    mainWindow.translate_ori.textChanged.connect(mainWindow.updateByTextEdit)
    mainWindow.text_size_combobox.currentIndexChanged.connect(mainWindow.updateOriTextSizeByIndexChanged)
    mainWindow.text_size_combobox.currentIndexChanged.connect(mainWindow.updateResTextSizeByIndexChanged)

    sys.exit(app.exec_())
    
