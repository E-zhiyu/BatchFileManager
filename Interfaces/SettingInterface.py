"""设置界面模块"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from qfluentwidgets import (ScrollArea, SettingCardGroup, OptionsSettingCard, QConfig, FluentIcon,
                            CustomColorSettingCard, ExpandLayout)


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
