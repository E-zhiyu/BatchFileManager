"""设置界面模块"""
import datetime
import json
import os
import shutil

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QHBoxLayout, QButtonGroup, QFrame, QDialog

from qfluentwidgets import (ScrollArea, SettingCardGroup, OptionsSettingCard, QConfig, FluentIcon, RadioButton,
                            CustomColorSettingCard, ExpandLayout, LineEdit,
                            ToolButton, InfoBar, InfoBarPosition, ToolTipFilter, ToolTipPosition,
                            SimpleExpandGroupSettingCard, BodyLabel, PushButton)

from AppConfig.config import cfg
from Logs.log_recorder import logging


class JavaPathCard(SimpleExpandGroupSettingCard):
    """Java路径设置卡"""

    def __init__(self, parent=None):
        self.parentWindow = parent
        javaPath = cfg.get(cfg.customJavaPath)
        super().__init__(FluentIcon.CAFE, 'Java路径', javaPath if javaPath else '由环境变量决定', parent)

        # 创建单选按钮实例
        sysRadioBtn = RadioButton('由环境变量决定')
        sysRadioBtn.setToolTip('使用环境变量中的Java路径')
        sysRadioBtn.installEventFilter(ToolTipFilter(sysRadioBtn, position=ToolTipPosition.TOP))

        customRadioBtn = RadioButton('自定义')
        customRadioBtn.setToolTip('使用自定义的Java路径')
        customRadioBtn.installEventFilter(ToolTipFilter(customRadioBtn, position=ToolTipPosition.TOP))

        self.buttonGroup = QButtonGroup()
        self.buttonGroup.addButton(sysRadioBtn, 0)
        self.buttonGroup.addButton(customRadioBtn, 1)
        self.buttonGroup.idClicked.connect(self.__onIdClicked)

        # 创建自定义路径的控件组合
        customWidget = QWidget()
        customWidget.setFixedHeight(50)
        customLayout = QHBoxLayout(customWidget)
        customLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        customLayout.setSpacing(3)

        self.pathLineEdit = LineEdit()
        self.pathLineEdit.setPlaceholderText('请输入Java路径')
        self.pathLineEdit.setClearButtonEnabled(True)
        self.pathLineEdit.setFixedWidth(200)
        self.pathLineEdit.setFixedHeight(35)
        self.pathLineEdit.textChanged.connect(self.__onTextChanged)
        customLayout.addWidget(self.pathLineEdit)

        self.pathBtn = ToolButton(FluentIcon.FOLDER)
        self.pathBtn.setFixedHeight(35)
        self.pathBtn.clicked.connect(self.__onPathBtnClicked)
        self.pathBtn.setToolTip('选择Java.exe的路径')
        self.pathBtn.installEventFilter(ToolTipFilter(self.pathBtn, position=ToolTipPosition.TOP))
        customLayout.addWidget(self.pathBtn)

        # 将各组合添加至设置卡片
        self.add(sysRadioBtn)
        self.add(customRadioBtn, customWidget)

        # 加载配置并设置控件状态
        self.__loadStatus()

    def add(self, lControl, rWidget=None):
        """
        添加一行新的设置选项
        :param lControl: 新选项左侧的控件
        :param rWidget: 新选项右侧容纳一个或多个控件的容器
        """

        w = QWidget()
        w.setFixedHeight(60)

        layout = QHBoxLayout(w)
        layout.setContentsMargins(48, 0, 48, 12)

        layout.addWidget(lControl, 0, Qt.AlignmentFlag.AlignLeft)
        if rWidget is not None:
            layout.addStretch(1)
            layout.addWidget(rWidget)

        self.addGroupWidget(w)  # 将组合后的容器添加到卡片布局中

    def verifyJavaPath(self, path: str):
        """
        验证自定义Java路径并修改配置项
        :param path: 需要验证的Java路径
        :return:通过-True，不通过-False
        """

        path = path.strip('\"')

        if os.path.isfile(path):
            cfg.set(cfg.customJavaPath, path)
            cfg.set(cfg.useCustomJavaPath, True)
            self.card.setContent(path)
            InfoBar.success(
                '成功',
                '成功设置Java路径',
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self.parentWindow
            )
            return True
        else:
            cfg.set(cfg.useCustomJavaPath, False)
            self.card.setContent('Java路径错误')
            InfoBar.error(
                '错误',
                'Java路径错误',
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self.parentWindow
            )
            return False

    def __onIdClicked(self, btn_id):
        """
        单选按钮按下后的响应方法
        :param btn_id: 被按下的单选按钮编号
        """

        if btn_id == 0:
            cfg.set(cfg.useCustomJavaPath, False)
            self.card.setContent('由环境变量决定')

            self.pathLineEdit.setEnabled(False)
            self.pathBtn.setEnabled(False)
            InfoBar.success(
                '成功',
                'Java路径遵从环境变量',
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self.parentWindow
            )
        elif btn_id == 1:
            self.pathLineEdit.setEnabled(True)
            self.pathBtn.setEnabled(True)

            customJavaPath = self.pathLineEdit.text().strip('\"')
            self.verifyJavaPath(customJavaPath)

    def __onPathBtnClicked(self):
        """路径按钮按下后的响应方法"""
        currentPath = self.pathLineEdit.text().strip('\"')
        if os.path.isfile(currentPath):
            path = currentPath
        else:
            path = ''

        java_path = QFileDialog.getOpenFileName(
            None,
            '选择Java',
            path,
            "Java应用程序 (java.exe)"
        )[0]

        if java_path:
            self.pathLineEdit.blockSignals(True)
            self.pathLineEdit.setText(java_path)
            self.pathLineEdit.setCursorPosition(0)  # 设置光标位置以从头部显示路径
            self.pathLineEdit.blockSignals(False)

            self.verifyJavaPath(java_path)

    def __onTextChanged(self):
        """路径输入框文本改变的响应方法"""
        java_path = self.pathLineEdit.text().strip('\"')
        self.verifyJavaPath(java_path)

    def __loadStatus(self):
        """加载配置文件内容并设置控件状态"""
        self.buttonGroup.blockSignals(True)
        self.pathLineEdit.blockSignals(True)
        self.pathLineEdit.setText(cfg.get(cfg.customJavaPath))
        self.pathLineEdit.setCursorPosition(0)  # 设置光标位置以从头部显示路径

        if cfg.get(cfg.useCustomJavaPath):
            self.card.setContent(cfg.get(cfg.customJavaPath))
            btn = self.buttonGroup.button(1)
            btn.setChecked(True)
            self.pathLineEdit.setEnabled(True)
            self.pathBtn.setEnabled(True)
        else:
            self.card.setContent('由环境变量决定')
            btn = self.buttonGroup.button(0)
            btn.setChecked(True)
            self.pathLineEdit.setEnabled(False)
            self.pathBtn.setEnabled(False)

        self.buttonGroup.blockSignals(False)
        self.pathLineEdit.blockSignals(False)


class BackupRecoveryCard(SimpleExpandGroupSettingCard):
    """
    数据备份和恢复卡片

    构造方法参数
    ------------
    * icon: 卡片图标
    * title: 卡片标题
    * content: 卡片描述
    * source: 被操作的文件路径
    * defaultName: 导出的默认文件名
    * importSignal: 导入数据时触发的信号
    * parentWindow: 所属的父界面
    """

    def __init__(self, icon: FluentIcon, title, content, source, defaultName, importSignal: pyqtSignal, parentWindow):
        super().__init__(icon, title, content, parentWindow)
        self.source = source
        self.defaultName = defaultName
        self.importSignal = importSignal
        self.parentWindow = parentWindow

        # 创建控件实例
        exportLabel = BodyLabel('导出数据')
        exportBtn = PushButton('选择位置')
        exportBtn.clicked.connect(self.exportData)
        importLabel = BodyLabel('导入数据')
        importBtn = PushButton('选择文件')
        importBtn.clicked.connect(self.importData)

        # 将控件实例添加至布局
        self.add(exportLabel, exportBtn)
        self.add(importLabel, importBtn)

    def add(self, label, control):
        """
        添加配置项到折叠区域
        :param label: 左侧标题标签
        :param control: 右侧功能控件
        """
        w = QWidget()
        w.setFixedHeight(60)

        layout = QHBoxLayout(w)
        layout.setContentsMargins(48, 0, 48, 12)

        layout.addWidget(label, 0, Qt.AlignmentFlag.AlignLeft)
        if control is not None:
            layout.addStretch(1)
            layout.addWidget(control)

        self.addGroupWidget(w)  # 将组合后的容器添加到卡片布局中

    def exportData(self):
        """导出数据方法"""
        w = QFileDialog(
            self,
            '数据导出',
            '',
            'JSON文件 (*.json)'
        )
        w.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)  # 对话框设置为保存文件模式
        default_name = datetime.datetime.now().strftime('%Y-%m-%d-') + self.defaultName
        w.selectFile(default_name)

        if w.exec() != QDialog.DialogCode.Accepted:
            return

        logging.info(f'源"{self.source}"开始导出数据……')
        target_path = w.selectedFiles()[0]
        try:
            shutil.copyfile(self.source, target_path)
            InfoBar.success(
                '成功',
                '数据已成功导出',
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self.parentWindow
            )
            logging.info('数据导出成功')
        except FileNotFoundError:
            InfoBar.error(
                '失败',
                '数据文件不存在',
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self.parentWindow
            )
            logging.error('数据导出失败')

    def importData(self):
        """恢复数据方法"""
        file_path = QFileDialog.getOpenFileName(
            self,
            '数据导入',
            '',
            'JSON文件 (*.json)'
        )[0]
        if not file_path:
            return

        logging.info(f'源"{self.source}"开始导入数据……')
        # 判断文件是否存在（避免用户移除文件）
        if not os.path.isfile(file_path):
            InfoBar.error(
                '失败',
                '待导入的文件不存在',
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self.parentWindow
            )
            logging.error('导入失败：待导入的文件不存在')
            return

        # 判断文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
            if not self.dataValidator(content):
                InfoBar.error(
                    '失败',
                    '文件内容格式错误',
                    position=InfoBarPosition.TOP,
                    duration=1500,
                    parent=self.parentWindow
                )
                logging.error('导入失败：文件格式错误')
                return

        # 复制文件内容
        shutil.copyfile(file_path, self.source)
        self.importSignal.emit()
        InfoBar.success(
            '成功',
            '数据已成功导入',
            position=InfoBarPosition.TOP,
            duration=1500,
            parent=self.parentWindow
        )
        logging.info('数据导入成功')

    @staticmethod
    def dataValidator(data_content) -> bool:
        """
        数据验证抽象方法
        :param data_content: 需要验证的数据内容
        :return 验证结果
        """
        return True


class FileBakRecCard(BackupRecoveryCard):
    """
    文件表格备份和恢复设置卡片

    构造方法参数
    ------------
    * icon: 卡片图标
    * title: 卡片标题
    * content: 卡片描述
    * source: 被操作的文件路径
    * defaultName: 导出的默认文件名
    * importSignal: 导入数据时触发的信号
    * parentWindow: 所属的父界面
    """

    @staticmethod
    def dataValidator(data_content) -> bool:
        """
        重写数据验证方法
        :param data_content: 需要验证的数据内容
        :return: 数据验证结果
        """

        for file in data_content:
            for fileInfo in file:
                if not isinstance(fileInfo, str):
                    return False
        return True


class PresetBakRecCard(BackupRecoveryCard):
    """
    预设备份和恢复卡片

    构造方法参数
    ------------
    * icon: 卡片图标
    * title: 卡片标题
    * content: 卡片描述
    * source: 被操作的文件路径
    * defaultName: 导出的默认文件名
    * importSignal: 导入数据时触发的信号
    * parentWindow: 所属的父界面
    """

    @staticmethod
    def dataValidator(data_content) -> bool:
        """
        重写导入数据的验证方法
        :param data_content: 待验证的数据内容
        :return: 验证结果
        """

        for preset in data_content:
            for i, presetInfo in enumerate(preset):
                if i < 3:
                    if not isinstance(presetInfo, str):
                        return False
                else:
                    if not isinstance(presetInfo, list):
                        return False
        return True


class SettingInterface(QWidget):
    """设置界面类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingInterface")

        # 基本布局设置
        self.widgetLayout = QVBoxLayout(self)
        self.scrollArea = ScrollArea(self)
        self.widgetLayout.addWidget(self.scrollArea)

        self.scrollWidget = QFrame(self.scrollArea)
        self.scrollArea.enableTransparentBackground()
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setWidgetResizable(True)

        self.viewLayout = ExpandLayout(self.scrollWidget)
        self.viewLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.viewLayout.setSpacing(5)

        # 添加控件
        self.initControls()

    def initControls(self):
        """初始化控件"""

        """个性化设置组"""
        self.personalizationGroup = SettingCardGroup('个性化', self.scrollWidget)
        self.viewLayout.addWidget(self.personalizationGroup)

        # 修改应用主题
        self.themeCard = OptionsSettingCard(
            QConfig.themeMode,
            FluentIcon.BRUSH,
            '应用主题',
            '修改你的应用主题',
            texts=[
                '浅色', '深色',
                '跟随系统'
            ],
            parent=self.personalizationGroup
        )
        self.personalizationGroup.addSettingCard(self.themeCard)

        # 修改主题颜色
        self.themeColorCard = CustomColorSettingCard(
            QConfig.themeColor,
            FluentIcon.PALETTE,
            '主题颜色',
            '调整应用的主题颜色',
            parent=self.personalizationGroup
        )
        self.personalizationGroup.addSettingCard(self.themeColorCard)

        """运行环境组"""
        self.environmentGroup = SettingCardGroup("运行环境", self.scrollWidget)
        self.viewLayout.addWidget(self.environmentGroup)

        # 修改Java路径
        self.javaPathCard = JavaPathCard(parent=self)
        self.environmentGroup.addSettingCard(self.javaPathCard)

        """软件数据组"""
        self.softwareDataGroup = SettingCardGroup('软件数据', self.scrollWidget)
        self.viewLayout.addWidget(self.softwareDataGroup)

        self.fileDataCard = FileBakRecCard(FluentIcon.FOLDER, '文件数据', '备份或恢复保存的文件信息',
                                           './config/fileTableContents.json', 'fileContents.json',
                                           cfg.fileDataChanged, self)
        self.softwareDataGroup.addSettingCard(self.fileDataCard)

        self.presetDataCard = PresetBakRecCard(FluentIcon.EMOJI_TAB_SYMBOLS, '预设数据', '备份或恢复文件预设',
                                               './config/presets.json', 'presets.json', cfg.presetDataChanged, self)
        self.softwareDataGroup.addSettingCard(self.presetDataCard)
