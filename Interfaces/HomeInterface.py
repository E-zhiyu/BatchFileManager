"""主页模块"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QTableWidgetItem

from qfluentwidgets import PushButton, TableWidget
from qfluentwidgets import FluentIcon as FIF

from AppConfig.config import cfg


class HomeInterface(QWidget):
    """主页类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parentWindow = parent  # 保存主窗口的引用
        self.setObjectName("HomeInterface")

        # 初始化布局管理器
        self.widgetLayout = QVBoxLayout(self)
        self.totalWidget = QWidget(self)
        self.widgetLayout.addWidget(self.totalWidget)
        self.mainLayout = QVBoxLayout(self.totalWidget)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.mainLayout.setContentsMargins(5, 5, 5, 5)
        self.mainLayout.setSpacing(10)

        # 初始化控件
        self.initControls()

    def initControls(self):
        """初始化控件"""

        # 添加操作按钮
        self.btnLayout = QHBoxLayout(self)
        self.btnLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.mainLayout.addLayout(self.btnLayout)

        self.runButton = PushButton(FIF.PLAY.icon(color='green'), '运行文件')
        self.btnLayout.addWidget(self.runButton)

        self.addButton = PushButton(FIF.ADD, "添加文件")
        self.btnLayout.addWidget(self.addButton)

        self.removeButton = PushButton(FIF.DELETE.icon(color='red'), '删除文件')
        self.btnLayout.addWidget(self.removeButton)

        # 文件列表视图
        self.fileTableView = TableWidget(self)
        self.mainLayout.addWidget(self.fileTableView)

        self.fileTableView.setBorderVisible(True)  # 设置边界可见性
        self.fileTableView.setBorderRadius(5)  # 设置边界圆角弧度
        self.fileTableView.setColumnCount(5)  # 设置列数
        # self.fileTableView.setRowCount(0)  # 设置行数
        self.fileTableView.verticalHeader().hide()  # 隐藏行序号
        self.fileTableView.setHorizontalHeaderLabels(['文件名', '备注', '文件类型', '修改日期', '大小'])
        self.fileTableView.setSortingEnabled(True)  # 启用表头排序

        # 恢复软件关闭前的列宽
        columnWidthList = cfg.get(cfg.tableColumnWidth)
        if columnWidthList is not None:
            for i, width in enumerate(columnWidthList):
                if width:
                    self.fileTableView.setColumnWidth(i, width)
        else:
            self.fileTableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 备注列拉伸以适应窗口

        """以下代码仅用于测试"""
        """files = [
            ['run.bat', '启动MC服务器', '.bat', '2025-7-29', '2KB'],
            ['start.bat', '启动泰拉瑞亚服务器', '.bat', '2025-7-29', '2KB']
        ]
        self.fileTableView.setRowCount(len(files))
        for index, file in enumerate(files):
            for i in range(5):
                self.fileTableView.setItem(index, i, QTableWidgetItem(file[i]))"""
