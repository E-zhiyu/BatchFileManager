"""关于软件界面模块"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from qfluentwidgets import SubtitleLabel, BodyLabel, HyperlinkButton, FluentIcon, setFont
from Interfaces import version


class InfoInterface(QWidget):
    """关于软件界面类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parentWindow = parent
        self.setObjectName("InfoInterface")

        # 初始化布局管理器
        self.totalWidget = QWidget(self)
        self.widgetLayout = QVBoxLayout(self)
        self.widgetLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widgetLayout.addWidget(self.totalWidget)

        self.mainLayout = QVBoxLayout(self.totalWidget)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.setSpacing(5)
        self.mainLayout.setContentsMargins(0, 0, 20, 0)

        # 初始化控件
        self.initControls()

    def initControls(self):
        """初始化控件"""

        # 标题标签
        titleLabel = SubtitleLabel('关于软件', self.totalWidget)
        self.mainLayout.addWidget(titleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        setFont(titleLabel, 25, QFont.Weight.Bold)

        # 版本号标签
        versionLabel = BodyLabel(f'版本：{version}', self.totalWidget)
        self.mainLayout.addWidget(versionLabel, 0, Qt.AlignmentFlag.AlignCenter)

        # 作者标签
        authorLabel = BodyLabel('作者：GitHub@E-zhiyu', self.totalWidget)
        self.mainLayout.addWidget(authorLabel, 0, Qt.AlignmentFlag.AlignCenter)

        # 查看源码按钮
        urlButton = HyperlinkButton(icon=FluentIcon.LINK, url='https://github.com/E-zhiyu/BatchFileManager',
                                    text='查看源代码')
        self.mainLayout.addWidget(urlButton, 0, Qt.AlignmentFlag.AlignCenter)
