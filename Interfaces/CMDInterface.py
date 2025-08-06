"""图形化控制台界面"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from Connector.SocketClient import SocketClient
from qfluentwidgets import BodyLabel, LineEdit, TextBrowser, PushButton, Dialog, InfoBar, InfoBarPosition, CheckBox, \
    ToolTipFilter, ToolTipPosition
from qfluentwidgets import FluentIcon as FIF


class CMDInterface(QWidget):
    """图形化控制台界面类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parentWindow = parent
        self.commandToBeSent = ""  # 等待发送的命令缓冲区
        self.setObjectName("CMDInterface")

        # 初始化基本布局
        self.totalWidget = QWidget(self)
        self.widgetLayout = QHBoxLayout(self)
        self.widgetLayout.addWidget(self.totalWidget)

        self.mainLayout = QVBoxLayout(self.totalWidget)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.mainLayout.setContentsMargins(5, 5, 5, 5)
        self.mainLayout.setSpacing(10)

        # 加载其他控件
        self.initControls()

        # 实例化连接子进程控制台的套接字客户端
        self.socketClient = SocketClient(self, self.cmdInputLineEdit, self.outputTextBrowser)

        # 设置控件信号连接
        self.sendCommandButton.clicked.connect(self.socketClient.send_command)
        self.cmdInputLineEdit.returnPressed.connect(self.socketClient.send_command)

    def initControls(self):
        """初始化控件"""

        """命令输入和控制台操作"""
        runCommandLabel = BodyLabel("命令输入框")
        self.mainLayout.addWidget(runCommandLabel, 0, Qt.AlignmentFlag.AlignLeft)
        runCommandLayout = QHBoxLayout()
        self.mainLayout.addLayout(runCommandLayout)

        self.cmdInputLineEdit = LineEdit()  # 命令输入框
        self.cmdInputLineEdit.setPlaceholderText('输入待运行的命令')
        runCommandLayout.addWidget(self.cmdInputLineEdit, 1, )

        self.sendCommandButton = PushButton(text='发送命令', icon=FIF.SEND)
        self.sendCommandButton.setToolTip('将命令发送至后台(Enter)')
        self.sendCommandButton.installEventFilter(ToolTipFilter(self.sendCommandButton, position=ToolTipPosition.TOP))
        runCommandLayout.addWidget(self.sendCommandButton, 0, )

        killButton = PushButton(text='结束进程', icon=FIF.CLOSE.icon(color='red'))
        killButton.setToolTip('强制结束进程')
        killButton.installEventFilter(ToolTipFilter(killButton, position=ToolTipPosition.TOP))
        runCommandLayout.addWidget(killButton, 0, Qt.AlignmentFlag.AlignRight)
        killButton.clicked.connect(lambda: self.stopCommunicationAndKill(True))

        """控制台内容输出"""
        outputLayout = QHBoxLayout()
        self.mainLayout.addLayout(outputLayout)
        CMDOutputLabel = BodyLabel('控制台输出')
        outputLayout.addWidget(CMDOutputLabel, 0, Qt.AlignmentFlag.AlignLeft)

        self.autoScrollCheckBox = CheckBox('自动滚动')  # 自动滚动复选框
        self.autoScrollCheckBox.setToolTip('输出内容更新时自动滚动至页面底部')
        self.autoScrollCheckBox.installEventFilter(
            ToolTipFilter(self.autoScrollCheckBox, position=ToolTipPosition.BOTTOM_RIGHT))
        self.autoScrollCheckBox.setChecked(True)
        self.autoScrollCheckBox.checkStateChanged.connect(self.setAutoScroll)
        outputLayout.addWidget(self.autoScrollCheckBox, 0, Qt.AlignmentFlag.AlignRight)

        self.outputTextBrowser = TextBrowser()  # 显示控制台内容的控件
        self.outputTextBrowser.document().setMaximumBlockCount(1000)  # 限制最大行数
        self.mainLayout.addWidget(self.outputTextBrowser, 1)

    def setAutoScroll(self):
        self.socketClient.autoScroll = self.autoScrollCheckBox.isChecked()

    def startCommunication(self):
        """启动与Java子进程的通信"""
        self.clearOutput()
        self.socketClient.setup_socket()

    def stopCommunicationAndKill(self, withMessageBox: bool = False):
        """
        结束与Java子进程的通信并结束进程
        :param withMessageBox:是否弹出确认框
        """
        if not withMessageBox:
            self.socketClient.send_command('#kill#')
        else:
            if self.socketClient.running:
                w = Dialog('结束进程', '确认要结束进程吗？这可能导致进程无法正常关闭', self.parentWindow)
                if w.exec():
                    self.socketClient.send_command('#kill#')
            else:
                InfoBar.error(
                    "错误",
                    '没有正在运行的文件',
                    duration=1500,
                    position=InfoBarPosition.TOP,
                    parent=self.parentWindow
                )

    def clearOutput(self):
        """清空命令输出的内容"""
        self.outputTextBrowser.clear()
