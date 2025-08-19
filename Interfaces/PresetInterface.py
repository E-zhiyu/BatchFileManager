"""文件预设界面模块"""
import json
import os
from enum import Enum

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QFrame, QVBoxLayout, QListWidgetItem, QFileDialog

from qfluentwidgets import CardWidget, BodyLabel, CaptionLabel, SwitchButton, PushButton, InfoBar, InfoBarPosition, \
    CommandBar, Action, SmoothScrollArea, Theme, isDarkTheme, MessageBoxBase, ListWidget, ComboBox, LineEdit, \
    ToolButton, ToolTipFilter, ToolTipPosition, SubtitleLabel, TextBrowser
from qfluentwidgets import FluentIcon as FIF

from Connector.JarConnector import JarConnector
from Logs.log_recorder import logging
from AppConfig.config import cfg

style_introduction = """\
## 开关

- 功能：用户点击开关按钮后分别运行开启文件和关闭文件
- 文件说明：需要设置一个开启文件和一个关闭文件，用于在切换开关状态时执行相应的操作

## 队列

- 功能：按照新建预设时从上到下的顺序依次运行文件
- 文件说明：需要一个或多个文件，运行该队列时将会按照顺序依次执行文件
"""


class PresetStyle(Enum):
    """预设卡片种类"""

    SWITCH = 'Switch'
    QUEUE = 'Queue'


class TextMessageBox(MessageBoxBase):
    """
    显示MarkDown文本的对话框类

    构造方法参数
    ------------
    * title: 对话框标题
    * md: 需要显示的Markdown文本
    * parent: 需要遮罩的窗体（建议设置为主窗体）
    """

    def __init__(self, title: str, md: str, parent=None):
        super().__init__(parent)
        self.widget.setMinimumWidth(550)  # 设置最小窗口宽度
        self.widget.setFixedHeight(500)  # 设置固定窗口高度
        self.cancelButton.hide()  # 隐藏取消按钮
        self.yesButton.setText('确定')

        titleLabel = SubtitleLabel(title)
        self.viewLayout.addWidget(titleLabel)

        txtBrowser = TextBrowser(self)
        txtBrowser.setMarkdown(md)
        self.viewLayout.addWidget(txtBrowser)


class PresetCard(CardWidget):
    """
    文件预设卡片

    构造方法参数
    ------------
    * title: 卡片标题
    * content: 卡片描述
    * style: 卡片样式
    * index: 卡片位置下标
    * parent: 卡片所属的界面
    """

    clicked = pyqtSignal(int)

    def __init__(self, title, content, style: PresetStyle, index, parent=None):
        super().__init__(parent)
        self.title = title
        self.content = content
        self.style = style
        self.index = index
        self.parentInterface = parent
        self.isCurrentCard = None
        self.setFixedHeight(73)

        if not isinstance(style, PresetStyle): raise TypeError  # 样式种类错误则抛出异常

        # 根据样式设置成员属性
        if self.style == PresetStyle.SWITCH:
            self.openFile = None
            self.closeFile = None
        elif self.style == PresetStyle.QUEUE:
            self.fileList = None

        # 基本布局设置
        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.setSpacing(15)
        self.mainLayout.setContentsMargins(5, 5, 25, 5)

        self.initControls()  # 初始化控件
        self.setCurrent(False)  # 设置为非当前卡片

        cfg.themeChanged.connect(self.refreshStyleSheet)
        cfg.themeColorChanged.connect(self.refreshStyleSheet)

    def mouseReleaseEvent(self, e):
        """重写鼠标释放功能以发送卡片下标"""
        super(CardWidget, self).mouseReleaseEvent(e)
        self.clicked.emit(self.index)

    def setFile(self, files: list):
        """
        设置卡片对应的文件
        :param files: 传入的文件路径列表
        """
        if self.style == PresetStyle.SWITCH:
            self.openFile = files[0]
            self.closeFile = files[1]
        elif self.style == PresetStyle.QUEUE:
            self.fileList = files

    def initControls(self):
        """初始化控件"""

        # 指示是否为当前卡片的纯色色块
        self.__currentFrame = QFrame(self)  # 标记是否为当前卡片的色块
        self.__currentFrame.setFixedHeight(20)
        self.__currentFrame.setFixedWidth(3)
        self.mainLayout.addWidget(self.__currentFrame)

        self.mainLayout.addSpacing(10)

        # 标题和内容
        self.titleContentLayout = QVBoxLayout()
        self.titleContentLayout.setSpacing(0)
        self.titleLabel = BodyLabel(self.title, self)
        self.contentLabel = CaptionLabel(self.content if self.content else '<无描述>', self)
        self.contentLabel.setTextColor("#606060", "#d2d2d2")
        self.titleContentLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.titleContentLayout.addWidget(self.contentLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.mainLayout.addLayout(self.titleContentLayout)

        qss = 'QLabel{background-color: transparent;}'
        self.titleLabel.setStyleSheet(qss)
        self.contentLabel.setStyleSheet(qss)

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
            if args[0]:  # 判断开关状态
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
                            "请检查Java版本和预设文件",
                            position=InfoBarPosition.TOP,
                            duration=1500,
                            parent=self.parentInterface.parentWindow
                        )
                        logging.error('运行失败：Java后端或预设文件异常')
                        self.switchButton.blockSignals(True)
                        self.switchButton.setChecked(False)
                        self.switchButton.blockSignals(False)
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
                            "请检查Java版本和预设文件",
                            position=InfoBarPosition.TOP,
                            duration=1500,
                            parent=self.parentInterface.parentWindow
                        )
                        logging.error('运行失败：Java后端或预设文件异常')
                        self.switchButton.blockSignals(True)
                        self.switchButton.setChecked(True)
                        self.switchButton.blockSignals(False)
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
                for i, file in enumerate(self.fileList):
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

    def getPresetData(self) -> list:
        """
        获取预设信息
        :return: 存放预设信息的列表
        """
        presetData = []

        if self.style == PresetStyle.SWITCH:
            btn_stat = self.switchButton.isChecked()
            open_file = self.openFile
            close_file = self.closeFile
            presetData = [btn_stat, open_file, close_file]
        elif self.style == PresetStyle.QUEUE:
            presetData = self.fileList

        return presetData

    def getStyle(self) -> PresetStyle:
        """获取卡片样式"""
        return self.style

    def setCurrent(self, flag: bool = True):
        """
        设置卡片是否为当前卡片
        :param flag: 选中或取消选中
        """
        if flag == self.isCurrentCard:
            return

        self.isCurrentCard = flag
        themeColor = cfg.get(cfg.themeColor)
        theme = cfg.get(cfg.themeMode)

        if flag:
            qss = 'QFrame{background-color: %s; border-radius: 1px}' % themeColor.name()
        else:
            if theme == Theme.AUTO:
                if isDarkTheme():
                    theme = Theme.DARK
                else:
                    theme = Theme.LIGHT

            if theme == Theme.LIGHT:
                qss = 'QFrame{background-color: #d2d2d2; border-radius: 1px}'
            else:
                qss = 'QFrame{background-color: #606060; border-radius: 1px}'

        self.__currentFrame.setStyleSheet(qss)

    def refreshStyleSheet(self, arg: (Theme, QColor)):
        """
        主题模式或主题色改变时刷新样式表
        :param arg: 修改后的主题模式或者主题色
        """

        label_qss = 'QLabel{background-color: transparent;}'
        self.titleLabel.setStyleSheet(label_qss)
        self.contentLabel.setStyleSheet(label_qss)

        if isinstance(arg, QColor):
            if self.isCurrentCard:
                qss = 'QFrame{background-color: %s; border-radius: 1px}' % arg.name()
            else:
                qss = 'QFrame{background-color: #d2d2d2; border-radius: 1px}'
            self.__currentFrame.setStyleSheet(qss)
        elif isinstance(arg, Theme):
            light_qss = 'QFrame{background-color: #d2d2d2; border-radius: 1px}'
            dark_qss = 'QFrame{background-color: #606060; border-radius: 1px}'

            if self.isCurrentCard:
                return  # 如果是当前卡片则不需要改变颜色

            if arg == Theme.AUTO:
                if isDarkTheme():
                    arg = Theme.DARK
                else:
                    arg = Theme.LIGHT

            if arg == Theme.LIGHT:
                self.__currentFrame.setStyleSheet(light_qss)
            else:
                self.__currentFrame.setStyleSheet(dark_qss)


class RecordableLineEdit(LineEdit):
    """能够通知父容器自身焦点改变的文本框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        if self.parent:
            self.parent.setInputControl(self)


class PresetDataInputDialog(MessageBoxBase):
    """
    预设信息输入对话框

    构造方法参数
    ------------
    * styleSelectable: 是否可选择卡片样式
    * style: 输入框样式
    * parent: 待遮罩的对象（建议设置为主窗口）
    * presetData: 待填充的预设信息列表    [title,content,[presetDatas...]]
    """

    def __init__(self, styleSelectable: bool = True, style: PresetStyle = PresetStyle.SWITCH, parent=None, *presetData):
        super().__init__(parent)
        self.styleSelectable = styleSelectable
        self.style = style
        self.parentWindow = parent
        self.presetData = presetData
        self.allFilePaths = []
        self.inputControl = None  # 待填充已添加文件信息的控件

        self.widget.setFixedSize(650, 550)
        self.yesButton.setText('确定')
        self.cancelButton.setText('取消')

        # 基本布局设置
        self.layout = QHBoxLayout(self.widget)
        self.viewLayout.addLayout(self.layout)
        controlWidget = QFrame()
        controlWidget.setFixedWidth(350)
        self.layout.addWidget(controlWidget, 0, Qt.AlignmentFlag.AlignLeft)
        listWidget = QFrame()
        listWidget.setFixedWidth(240)
        self.layout.addWidget(listWidget, 0, Qt.AlignmentFlag.AlignRight)

        # 右侧文件列表布局设置
        listLayout = QVBoxLayout(listWidget)
        listLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        listTitle = BodyLabel('已保存的文件')
        listLayout.addWidget(listTitle)
        listLayout.addSpacing(10)
        self.fileListControl = ListWidget()
        listLayout.addWidget(self.fileListControl)
        self.fileListControl.itemClicked.connect(self.__inputCollectedFile)

        # 左侧功能控件布局设置
        controlWidgetLayout = QVBoxLayout(controlWidget)
        controlWidgetLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        styleLayout = QHBoxLayout()
        controlWidgetLayout.addLayout(styleLayout)
        changeStyleLabel = BodyLabel('预设样式')
        styleLayout.addWidget(changeStyleLabel)
        styleSelectComboBox = ComboBox()
        styleLayout.addWidget(styleSelectComboBox)
        styleSelectComboBox.setFixedWidth(100)
        items = ['开关', '队列']
        styleSelectComboBox.addItems(items)
        styleSelectComboBox.currentIndexChanged.connect(self.__initMainControls)

        titleLayout = QHBoxLayout()
        controlWidgetLayout.addLayout(titleLayout)
        titleLabel = BodyLabel('预设名称')
        titleLayout.addWidget(titleLabel)
        titleLayout.addSpacing(30)
        self.titleLineEdit = LineEdit()
        titleLayout.addWidget(self.titleLineEdit)

        contentLayout = QHBoxLayout()
        controlWidgetLayout.addLayout(contentLayout)
        contentLabel = BodyLabel('预设描述')
        contentLayout.addWidget(contentLabel)
        contentLayout.addSpacing(30)
        self.contentLineEdit = LineEdit()
        contentLayout.addWidget(self.contentLineEdit)

        # 初始化下拉框的内容
        styleSelectComboBox.blockSignals(True)
        styleTuple = tuple(PresetStyle)
        index = styleTuple.index(self.style)
        styleSelectComboBox.setCurrentIndex(index)
        styleSelectComboBox.blockSignals(False)

        # 判断下拉框是否可用
        if not self.styleSelectable:
            styleSelectComboBox.setEnabled(False)

        # 添加mainLayout布局管理器
        controlWidgetLayout.addSpacing(20)
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        controlWidgetLayout.addLayout(self.mainLayout)

        self.__initMainControls(styleSelectComboBox.currentIndex())  # 初始化主要的控件
        self.__showCollectedFiles()  # 将文件添加至列表视图
        self.__setPresetData()  # 初始化预设信息

    def __initMainControls(self, styleIndex: int = 0):
        # 先删除旧控件
        while self.mainLayout.count():
            item = self.mainLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    subItem = item.layout().takeAt(0)
                    if subItem.widget():
                        subItem.widget().deleteLater()
                item.layout().deleteLater()

        styleTuple = tuple(PresetStyle)
        style = styleTuple[styleIndex]
        self.style = style

        # 动态添加左侧容器的内容
        if style == PresetStyle.SWITCH:
            # 开启文件标签
            openFileLabel = BodyLabel('开启文件')
            self.mainLayout.addWidget(openFileLabel)

            # 开启文件路径输入控件
            openFileInputLayout = QHBoxLayout()
            openFileInputLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.mainLayout.addLayout(openFileInputLayout)

            self.openFilePathLineEdit = RecordableLineEdit(self)
            openFileInputLayout.addWidget(self.openFilePathLineEdit)
            self.openFilePathLineEdit.setClearButtonEnabled(True)
            self.openFilePathLineEdit.setPlaceholderText('请输入开启文件的路径')

            openFileSelectButton = ToolButton(FIF.FOLDER)
            openFileInputLayout.addWidget(openFileSelectButton)
            openFileSelectButton.setToolTip('选择开启文件的路径')
            openFileSelectButton.installEventFilter(ToolTipFilter(openFileSelectButton, position=ToolTipPosition.TOP))
            openFileSelectButton.clicked.connect(lambda: self.__addFile(self.openFilePathLineEdit))

            self.mainLayout.addSpacing(10)

            # 关闭文件标签
            closeFileLabel = BodyLabel('关闭文件')
            self.mainLayout.addWidget(closeFileLabel)

            # 关闭文件路径输入控件
            closeFileInputLayout = QHBoxLayout()
            closeFileInputLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.mainLayout.addLayout(closeFileInputLayout)

            self.closeFilePathLineEdit = RecordableLineEdit(self)
            closeFileInputLayout.addWidget(self.closeFilePathLineEdit)
            self.closeFilePathLineEdit.setClearButtonEnabled(True)
            self.closeFilePathLineEdit.setPlaceholderText('请输入关闭文件的路径')

            closeFileSelectButton = ToolButton(FIF.FOLDER)
            closeFileInputLayout.addWidget(closeFileSelectButton)
            closeFileSelectButton.setToolTip('选择关闭文件的路径')
            closeFileSelectButton.installEventFilter(ToolTipFilter(closeFileSelectButton, position=ToolTipPosition.TOP))
            closeFileSelectButton.clicked.connect(lambda: self.__addFile(self.closeFilePathLineEdit))

        elif style == PresetStyle.QUEUE:
            headerLayout = QHBoxLayout()
            self.mainLayout.addLayout(headerLayout)

            fileQueueLabel = BodyLabel('文件队列')
            headerLayout.addWidget(fileQueueLabel, 0, Qt.AlignmentFlag.AlignLeft)
            addBtn = ToolButton(FIF.ADD)
            headerLayout.addWidget(addBtn)
            addBtn.setToolTip('添加文件')
            addBtn.installEventFilter(ToolTipFilter(addBtn, position=ToolTipPosition.TOP))

            delBtn = ToolButton(FIF.DELETE.icon(color='red'))
            headerLayout.addWidget(delBtn)
            delBtn.setToolTip('移除文件')
            delBtn.installEventFilter(ToolTipFilter(delBtn, position=ToolTipPosition.TOP))

            fileQueueList = ListWidget()
            self.mainLayout.addWidget(fileQueueList)

            addBtn.clicked.connect(lambda: self.__addFile(fileQueueList))
            delBtn.clicked.connect(lambda: self.__delFile(fileQueueList))
            self.setInputControl(fileQueueList)

    def __showCollectedFiles(self):
        """右侧列表视图显示已保存的文件"""

        # 读取JSON文件中的路径
        try:
            with open('./config/fileTableContents.json', 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                self.allFilePaths = [fileInfo[2] for fileInfo in json_data]
        except FileNotFoundError:
            self.allFilePaths = []

        # 将路径中的文件名显示在列表视图中
        for file in self.allFilePaths:
            item = QListWidgetItem(os.path.basename(file))
            self.fileListControl.addItem(item)

    def __inputCollectedFile(self):
        """点击右侧文件列表后添加相应的文件路径"""
        index = self.fileListControl.currentRow()
        filePath = self.allFilePaths[index]

        if self.style == PresetStyle.SWITCH:
            if isinstance(self.inputControl, LineEdit):
                self.inputControl.setText(filePath)
                self.inputControl.setCursorPosition(0)
                self.inputControl.setFocus()
        elif self.style == PresetStyle.QUEUE:
            if isinstance(self.inputControl, ListWidget):
                item = QListWidgetItem(filePath)
                self.inputControl.addItem(item)

    def __setPresetData(self):
        """填充外部传递的预设信息"""
        if not self.presetData:
            return

        title = self.presetData[0]
        content = self.presetData[1]
        self.titleLineEdit.setText(title)
        self.titleLineEdit.setCursorPosition(0)
        self.contentLineEdit.setText(content)
        self.contentLineEdit.setCursorPosition(0)

        if self.style == PresetStyle.SWITCH:
            btn_stat, openFile, closeFile = self.presetData[2]
            self.openFilePathLineEdit.setText(openFile)
            self.openFilePathLineEdit.setCursorPosition(0)
            self.closeFilePathLineEdit.setText(closeFile)
            self.closeFilePathLineEdit.setCursorPosition(0)
        elif self.style == PresetStyle.QUEUE:
            fileList = self.presetData[2]
            for file in fileList:
                item = QListWidgetItem(file)
                self.fileListControl.addItem(item)

    def getPresetData(self) -> list:
        """
        获取输入的预设信息
        :return: 包含预设标题、描述、样式和文件信息列表的列表
        """

        title = self.titleLineEdit.text()
        content = self.contentLineEdit.text()
        style = self.style

        if style == PresetStyle.SWITCH:
            openFile = self.openFilePathLineEdit.text()
            closeFile = self.closeFilePathLineEdit.text()
            fileData = [openFile, closeFile]
        elif style == PresetStyle.QUEUE:
            fileData = []
            for i in range(self.fileListControl.count()):
                item = self.fileListControl.item(i)
                filePath = item.text()
                fileData.append(filePath)
        else:
            fileData = []

        return [title, content, style, fileData]

    def setInputControl(self, control):
        """设置填充已有文件的控件"""
        self.inputControl = control

    @staticmethod
    def __addFile(control):
        """
        向指定控件添加文件路径
        :param control: 待填充文件路径的控件
        """

        if isinstance(control, LineEdit):
            path = control.text()
        else:
            path = ''

        filePath = QFileDialog.getOpenFileName(
            None,
            '添加文件',
            path,
            '批处理和命令脚本 (*.bat *.cmd);;批处理文件 (*.bat);;命令脚本 (*.cmd)'
        )[0]
        if not filePath:
            return

        if isinstance(control, LineEdit):
            control.setText(filePath)
            control.setCursorPosition(0)
        elif isinstance(control, ListWidget):
            filename = os.path.basename(filePath)
            item = QListWidgetItem(f'{filename}({filePath})')
            control.addItem(item)

    @staticmethod
    def __delFile(control):
        """
        将指定控件中指定的文件移除
        :param control: 需要移除文件的控件
        """
        if isinstance(control, ListWidget):
            control.takeItem(control.currentRow())

    def validate(self) -> bool:
        """重写验证方法"""
        flag = True
        warning_content = ''

        if not self.titleLineEdit.text():
            flag = False
            warning_content = '请输入标题'
        elif self.style == PresetStyle.SWITCH:
            openFile = self.openFilePathLineEdit.text()
            closeFile = self.closeFilePathLineEdit.text()
            if not os.path.isfile(openFile):
                flag = False
                warning_content = '请输入正确的开启文件的路径'
            elif not os.path.isfile(closeFile):
                flag = False
                warning_content = '请输入正确的关闭文件的路径'
        elif self.style == PresetStyle.QUEUE:
            if not self.fileListControl.count():
                flag = False
                warning_content = '请添加至少一个文件'

        if not flag:
            InfoBar.error(
                '错误',
                warning_content,
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self
            )
        return flag


class PresetInterface(QWidget):
    """文件预设界面类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parentWindow = parent
        self.setObjectName("PresetInterface")

        self.cardList = []
        self.currentCardIndex = -1

        # 基本布局设置
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.mainLayout.setContentsMargins(5, 5, 5, 5)
        self.mainLayout.setSpacing(10)

        self.initControls()  # 初始化控件
        self.loadPreset()  # 加载预设卡片

        cfg.presetDataChanged.connect(self.refreshPresetView)  # 将预设数据改变信号连接至刷新布局方法

    def initControls(self):
        """初始化控件"""

        btnLayout = QHBoxLayout()
        btnLayout.setContentsMargins(5, 5, 5, 5)
        self.mainLayout.addLayout(btnLayout)

        # 命令栏
        self.commandBar = CommandBar()
        self.commandBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)  # 图标右侧显示文字
        btnLayout.addWidget(self.commandBar)

        self.commandBar.addActions([
            Action(FIF.ADD, '新建预设', triggered=self.addPreset),
            Action(FIF.DELETE.icon(color='red'), '删除预设', triggered=self.deletePreset),
            Action(FIF.EDIT, '编辑预设', triggered=self.editPreset)
        ])

        # 预设说明按钮
        helpBtn = ToolButton(FIF.HELP)
        btnLayout.addWidget(helpBtn, 0, Qt.AlignmentFlag.AlignRight)
        helpBtn.setToolTip('预设说明')
        helpBtn.installEventFilter(ToolTipFilter(helpBtn, position=ToolTipPosition.TOP_RIGHT))
        helpBtn.clicked.connect(self.showHelp)

        # 卡片滚动区域
        self.cardScrollArea = SmoothScrollArea(self)
        self.mainLayout.addWidget(self.cardScrollArea)
        self.cardWidget = QFrame(self)
        self.cardScrollArea.setWidget(self.cardWidget)
        self.cardScrollArea.setWidgetResizable(True)

        self.cardLayout = QVBoxLayout(self.cardWidget)  # 卡片滚动区域的垂直布局管理器
        self.cardLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.cardLayout.setContentsMargins(5, 5, 5, 5)
        self.cardLayout.setSpacing(5)

    def changeCurrentCard(self, cardIndex: int):
        """
        将当前卡片切换为指定下标的卡片
        :param cardIndex: 指定的卡片下标（-1为取消选中）
        """
        if self.currentCardIndex == cardIndex:  # 点击当前卡片则取消选中
            self.changeCurrentCard(-1)
            return

        if self.currentCardIndex != -1:
            last = self.currentCardIndex
            self.cardList[last].setCurrent(False)

        now = self.currentCardIndex = cardIndex

        if self.currentCardIndex != -1:
            self.cardList[now].setCurrent(True)

    def addPreset(self):
        """添加新预设"""
        w = PresetDataInputDialog(True, parent=self.parentWindow)
        if w.exec():
            title, content, style, fileData = w.getPresetData()
            if not fileData:
                InfoBar.error(
                    '错误',
                    '无法获取预设文件信息',
                    position=InfoBarPosition.TOP,
                    duration=1500,
                    parent=self.parentWindow
                )
                return

            new_card = PresetCard(title, content, style, len(self.cardList), self)
            new_card.setFile(fileData)
            self.addNewCard(new_card)

    def deletePreset(self):
        """删除预设"""
        card_index = self.currentCardIndex
        if card_index == -1:
            InfoBar.warning(
                '提示',
                '请选择一个预设卡片',
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self.parentWindow
            )
            return
        self.changeCurrentCard(-1)  # 重置当前卡片的下标

        # 先将后面的卡片下标减一
        for card in self.cardList[card_index + 1:]:
            card.index -= 1

        card = self.cardLayout.takeAt(card_index).widget()
        card.deleteLater()
        self.cardList.pop(card_index)

        self.savePreset()  # 操作结束即保存预设

    def editPreset(self):
        """编辑预设"""
        if self.currentCardIndex == -1:
            InfoBar.warning(
                '提示',
                '请选择一个预设卡片',
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self.parentWindow
            )
            return

        cardStyle = self.cardList[self.currentCardIndex].getStyle()
        title = self.cardList[self.currentCardIndex].title
        content = self.cardList[self.currentCardIndex].content
        presetData = self.cardList[self.currentCardIndex].getPresetData()

        w = PresetDataInputDialog(False, cardStyle, self.parentWindow, title, content, presetData)
        if not w.exec():
            return

        title, content, style, fileData = w.getPresetData()
        if not fileData:
            InfoBar.error(
                '错误',
                '无法获取预设文件信息',
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self.parentWindow
            )
            return

        # 实例化新卡片
        new_card = PresetCard(title, content, style, self.currentCardIndex, self)
        new_card.setFile(fileData)
        new_card.clicked.connect(self.changeCurrentCard)

        # 删除旧卡片
        old_card = self.cardLayout.takeAt(self.currentCardIndex).widget()
        old_card.deleteLater()

        # 添加新卡片
        self.cardLayout.insertWidget(self.currentCardIndex, new_card)
        self.cardList[self.currentCardIndex] = new_card

        self.savePreset()  # 保存预设变更
        self.changeCurrentCard(-1)  # 将当前卡片下标复位

    def addNewCard(self, card: PresetCard):
        """
        添加新卡片到布局中
        :param card: 待添加的卡片
        """
        card.clicked.connect(self.changeCurrentCard)
        self.cardLayout.addWidget(card)
        self.cardList.append(card)
        self.savePreset()  # 操作结束即保存预设

    def showHelp(self):
        """显示帮助信息窗口"""
        w = TextMessageBox('预设说明', style_introduction, self.parentWindow)
        w.exec()

    def refreshPresetView(self):
        """刷新文件预设"""
        while self.cardLayout.count():
            item = self.cardLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.cardList.clear()

        self.loadPreset()

    def loadPreset(self):
        """加载保存到文件的预设"""
        try:
            with open('./config/presets.json', 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        except FileNotFoundError:
            return

        for index, preset in enumerate(json_data):
            title = preset[0]
            content = preset[1]
            try:
                style = PresetStyle(preset[2])
            except ValueError:
                style = None
            presetData = preset[3]
            new_card = PresetCard(title, content, style, index, self)

            if style == PresetStyle.SWITCH:
                btn_stat = presetData[0]
                openFile = presetData[1]
                closeFile = presetData[2]

                new_card.switchButton.blockSignals(True)
                new_card.switchButton.setChecked(btn_stat)
                new_card.switchButton.blockSignals(False)
                new_card.setFile([openFile, closeFile])
            elif style == PresetStyle.QUEUE:
                fileList = presetData
                new_card.setFile(fileList)

            self.addNewCard(new_card)

    def savePreset(self):
        """将预设保存至文件"""
        allPresets = []

        for presetCard in self.cardList:
            title = presetCard.title
            content = presetCard.content
            style = presetCard.getStyle().value
            presetData = presetCard.getPresetData()

            onePresetCardInfo = [title, content, style, presetData]
            allPresets.append(onePresetCardInfo)

        with open('./config/presets.json', 'w', encoding='utf-8') as f:
            json.dump(allPresets, f, ensure_ascii=False, indent=4)
