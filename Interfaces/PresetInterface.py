"""文件预设界面模块"""
from enum import Enum

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QFrame, QVBoxLayout

from Connector.JarConnector import JarConnector
from qfluentwidgets import CardWidget, BodyLabel, CaptionLabel, SwitchButton, PushButton, InfoBar, InfoBarPosition

from Logs.log_recorder import logging
from AppConfig.config import cfg


class PresetStyle(Enum):
    """预设卡片种类"""

    SWITCH = 'switch'
    QUEUE = 'queue'


class PresetCard(CardWidget):
    """预设卡片类"""

    def __init__(self, title, content, style: PresetStyle, parent=None):
        """
        预设卡片构造方法
        :param title: 卡片标题
        :param content: 卡片描述内容
        :param style: 卡片样式（种类为PresetStyle枚举值）
        :param parent: 卡片父容器（默认为None）
        """
        super().__init__(parent)
        self.title = title
        self.content = content
        self.style = style
        self.parentInterface = parent
        self.setFixedHeight(73)

        # 根据样式设置成员属性
        if self.style == PresetStyle.SWITCH:
            self.openFile = None
            self.closeFile = None
        elif self.style == PresetStyle.QUEUE:
            self.fileTuple = None

        # 基本布局设置
        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.setSpacing(15)

        self.initControls()

        self.clicked.connect(self.setCurrentCard)

    def setFile(self, *files):
        """
        设置卡片对应的文件
        :param files: 传入的文件路径
        """
        if self.style == PresetStyle.SWITCH:
            self.openFile = files[0]
            self.closeFile = files[1]
        elif self.style == PresetStyle.QUEUE:
            self.fileTuple = files

    def initControls(self):
        """初始化控件"""

        # 指示是否为当前卡片的纯色色块
        self.__currentFrame = QFrame(self)
        self.__currentFrame.setFixedHeight(20)
        self.__currentFrame.setFixedWidth(3)
        self.mainLayout.addWidget(self.__currentFrame)

        # 标题和内容
        self.titleContentLayout = QVBoxLayout()
        self.titleContentLayout.setSpacing(0)
        self.titleLabel = BodyLabel(self.title, self)
        self.contentLabel = CaptionLabel(self.content, self)
        self.contentLabel.setTextColor("#606060", "#d2d2d2")
        self.titleContentLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.titleContentLayout.addWidget(self.contentLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addLayout(self.titleContentLayout)

        self.mainLayout.addStretch(1)

        # 根据种类增加控件
        if self.style == PresetStyle.SWITCH:
            self.switchButton = SwitchButton()
            self.mainLayout.addWidget(self.switchButton, 0, Qt.AlignmentFlag.AlignRight)
            self.switchButton.checkedChanged.connect(self.__onButtonClicked)
        elif self.style == PresetStyle.QUEUE:
            self.runButton = PushButton('运行文件')
            self.mainLayout.addWidget(self.runButton, 0, Qt.AlignmentFlag.AlignRight)
            self.runButton.clicked.connect(self.__onButtonClicked)

    def runFile(self, filePath: str):
        """
        运行文件方法
        :param filePath: 文件路径
        :return: Java后端应答情况（文件是否正确运行）
        """
        cmdInterface = self.parentInterface.parentWindow.cmdInterface
        running_cnt = JarConnector('./backend/fileRunner.jar', [filePath])
        ack = running_cnt.receiveData()

        if ack:
            logging.info('文件成功运行')
            cmdInterface.startCommunication()
            return True
        else:
            return False

    def __onButtonClicked(self, *args):
        """用户点击按钮后执行的方法"""
        cmdInterface = self.parentInterface.parentWindow.cmdInterface
        runningFlag = cmdInterface.socketClient.running

        if self.style == PresetStyle.SWITCH:
            if not args[0]:  # 判断开关状态
                if runningFlag:
                    InfoBar.error(
                        "错误",
                        '已有正在运行的文件',
                        duration=1500,
                        position=InfoBarPosition.TOP,
                        parent=self.parentInterface.parentWindow
                    )
                    self.switchButton.blockSignals(True)
                    self.switchButton.setChecked(False)
                    self.switchButton.blockSignals(False)
                else:
                    logging.info('开关类预设：开')
                    flag = self.runFile(self.openFile)
                    if flag:
                        InfoBar.success(
                            '成功',
                            '文件已成功运行',
                            duration=1500,
                            position=InfoBarPosition.TOP,
                            parent=self.parentInterface.parentWindow
                        )
                    else:
                        InfoBar.error(
                            "运行失败",
                            "Java后端运行异常，请检查Java版本",
                            position=InfoBarPosition.TOP,
                            duration=1500,
                            parent=self.parentWindow
                        )
                        logging.error('运行失败：Java后端运行异常')
            else:
                if runningFlag:
                    InfoBar.error(
                        "错误",
                        '已有正在运行的文件',
                        duration=1500,
                        position=InfoBarPosition.TOP,
                        parent=self.parentInterface.parentWindow
                    )
                    self.switchButton.blockSignals(True)
                    self.switchButton.setChecked(True)
                    self.switchButton.blockSignals(False)
                else:
                    flag = self.runFile(self.closeFile)
                    if flag:
                        InfoBar.success(
                            '成功',
                            '文件已成功运行',
                            duration=1500,
                            position=InfoBarPosition.TOP,
                            parent=self.parentInterface.parentWindow
                        )
                    else:
                        InfoBar.error(
                            "运行失败",
                            "Java后端运行异常，请检查Java版本",
                            position=InfoBarPosition.TOP,
                            duration=1500,
                            parent=self.parentWindow
                        )
                        logging.error('运行失败：Java后端运行异常')
        elif self.style == PresetStyle.QUEUE:
            if runningFlag:  # 开始执行队列中的文件前检查是否有正在运行的文件
                InfoBar.error(
                    "错误",
                    '已有正在运行的文件',
                    duration=1500,
                    position=InfoBarPosition.TOP,
                    parent=self.parentInterface.parentWindow
                )
            else:
                for i, file in enumerate(self.fileTuple):
                    if runningFlag: continue
                    flag = self.runFile(file)
                    if not flag:
                        InfoBar.error(
                            '错误',
                            f'运行至第{i}个文件时出错，已终止文件运行',
                            duration=1500,
                            position=InfoBarPosition.TOP,
                            parent=self.parentInterface.parentWindow
                        )
                        break
                else:  # 循环正常结束时触发
                    InfoBar.success(
                        '完成',
                        '队列中的文件已全部执行',
                        duration=1500,
                        position=InfoBarPosition.TOP,
                        parent=self.parentInterface.parentWindow
                    )

    def getStyle(self):
        """获取卡片样式"""
        return self.style

    def setCurrentCard(self, flag: bool = True):
        """
        设置为选中的卡片
        :param flag: 选中或取消选中
        """
        themeColor = cfg.get(cfg.themeColor)

        if flag:
            qss = '{background-color: %s; border: 1px}' % themeColor
        else:
            qss = '{background-color: transparent; border: 1px}'

        self.__currentFrame.setStyleSheet(qss)


class PresetInterface(QWidget):
    """文件预设界面类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parentWindow = parent
        self.setObjectName("PresetInterface")

        self.presetCardList = []

    def loadPreset(self):
        """加载保存到文件的预设"""
        pass

    def savePreset(self):
        """将预设保存至文件"""
        pass
