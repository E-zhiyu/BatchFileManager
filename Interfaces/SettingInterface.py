"""设置界面模块"""
import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QHBoxLayout, QButtonGroup

from qfluentwidgets import (ScrollArea, SettingCardGroup, OptionsSettingCard, QConfig, FluentIcon, RadioButton,
                            CustomColorSettingCard, ExpandLayout, PushSettingCard, ExpandGroupSettingCard, LineEdit,
                            ToolButton)

from AppConfig.config import cfg


class JavaPathCard(ExpandGroupSettingCard):
    """Java路径设置卡"""

    def __init__(self, parent=None):
        javaPath = cfg.get(cfg.customJavaPath)
        super().__init__(FluentIcon.CAFE, 'Java路径', javaPath if javaPath else '由环境变量决定', parent)

        # 创建单选按钮实例
        sysRadioBtn = RadioButton('由环境变量决定')
        customRadioBtn = RadioButton('自定义')

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
        customLayout.addWidget(self.pathBtn)

        # 将各组合添加至设置卡片
        self.add(sysRadioBtn)
        self.add(customRadioBtn, customWidget)

        self.__loadStatus()  # 加载配置并设置控件状态

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

    def __onIdClicked(self, btn_id):
        """
        单选按钮按下后的响应方法
        :param btn_id: 被按下的单选按钮编号
        """

        if btn_id == 0:
            cfg.set(cfg.useCustomJavaPath,False)
            self.card.setContent('由环境变量决定')

            self.pathLineEdit.setEnabled(False)
            self.pathBtn.setEnabled(False)
        elif btn_id == 1:
            self.pathLineEdit.setEnabled(True)
            self.pathBtn.setEnabled(True)

            customJavaPath = self.pathLineEdit.text().strip('\"')
            if os.path.isfile(customJavaPath):
                cfg.set(cfg.useCustomJavaPath, True)
                cfg.set(cfg.customJavaPath, customJavaPath)
                self.card.setContent(customJavaPath)
            else:
                cfg.set(cfg.useCustomJavaPath, False)
                self.card.setContent('Java路径错误')

    def __onPathBtnClicked(self):
        """路径按钮按下后的响应方法"""
        java_path = QFileDialog.getOpenFileName(
            None,
            '选择Java',
            "",
            "Java应用程序 (java.exe)"
        )[0]
        self.pathLineEdit.setText(java_path)
        self.pathLineEdit.setCursorPosition(0)  # 设置光标位置以从头部显示路径

        if java_path and os.path.isfile(java_path):
            cfg.set(cfg.customJavaPath, java_path)
            self.card.setContent(java_path)
        else:
            self.card.setContent('Java路径错误')

    def __onTextChanged(self):
        """路径输入框文本改变的响应方法"""
        java_path = self.pathLineEdit.text().strip('\"')
        if os.path.isfile(java_path):
            cfg.set(cfg.customJavaPath, java_path)
            self.card.setContent(java_path)
        else:
            self.card.setContent('Java路径错误')

    def __loadStatus(self):
        """加载配置文件内容并设置控件状态"""
        self.buttonGroup.blockSignals(True)
        self.pathLineEdit.blockSignals(True)
        self.pathLineEdit.setText(cfg.get(cfg.customJavaPath))
        self.pathLineEdit.setCursorPosition(0)  # 设置光标位置以从头部显示路径

        if cfg.get(cfg.useCustomJavaPath):
            btn = self.buttonGroup.button(1)
            btn.setChecked(True)
            self.pathLineEdit.setEnabled(True)
            self.pathBtn.setEnabled(True)
        else:
            btn = self.buttonGroup.button(0)
            btn.setChecked(True)
            self.pathLineEdit.setEnabled(False)
            self.pathBtn.setEnabled(False)

        self.buttonGroup.blockSignals(False)
        self.pathLineEdit.blockSignals(False)


class SettingInterface(QWidget):
    """设置界面类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingInterface")

        # 基本布局设置
        self.widgetLayout = QVBoxLayout(self)
        self.scrollArea = ScrollArea(self)
        self.widgetLayout.addWidget(self.scrollArea)

        self.scrollWidget = QWidget(self.scrollArea)
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

        """个性化设置项"""
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

        """运行环境项"""
        self.environmentGroup = SettingCardGroup("运行环境", self.scrollWidget)
        self.viewLayout.addWidget(self.environmentGroup)

        # 修改Java路径
        self.javaPathCard = JavaPathCard(parent=self)
        self.environmentGroup.addSettingCard(self.javaPathCard)
