"""主页模块"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QTableWidgetItem, QFileDialog

from qfluentwidgets import PushButton, TableWidget
from qfluentwidgets import FluentIcon as FIF

from AppConfig.config import cfg

from Connector.JarConnector import JarConnector

import json


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

        # 加载已保存的文件内容
        self.loadContents()

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
        self.addButton.clicked.connect(self.addFileAction)

        self.removeButton = PushButton(FIF.DELETE.icon(color='red'), '删除文件')
        self.btnLayout.addWidget(self.removeButton)
        self.removeButton.clicked.connect(self.removeFileAction)

        # 文件列表视图
        self.fileTableView = TableWidget(self)
        self.mainLayout.addWidget(self.fileTableView)

        self.fileTableView.setBorderVisible(True)  # 设置边界可见性
        self.fileTableView.setBorderRadius(5)  # 设置边界圆角弧度
        self.fileTableView.setColumnCount(6)  # 设置列数
        # self.fileTableView.setRowCount(0)  # 设置行数
        self.fileTableView.verticalHeader().hide()  # 隐藏行序号
        self.fileTableView.setHorizontalHeaderLabels(['文件名', '备注', '文件路径', '修改日期', '文件类型', '大小'])
        self.fileTableView.setSortingEnabled(True)  # 启用表头排序
        self.fileTableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 备注列拉伸以适应窗口
        self.fileTableView.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # 文件路径拉伸

        # 恢复软件关闭前的列宽
        columnWidthList = cfg.get(cfg.tableColumnWidth)
        if columnWidthList is not None:
            for i, width in enumerate(columnWidthList):
                if width:
                    self.fileTableView.setColumnWidth(i, width)

        """以下代码仅用于测试"""
        """files = [
            ['run.bat', '启动MC服务器', 'D:/MyFolder', '2025-7-29', '.bat', '2KB'],
            ['start.bat', '启动泰拉瑞亚服务器', 'D:/MyFolder', '2025-7-29', '.bat', '2KB']
        ]
        self.fileTableView.setRowCount(len(files))
        for index, file in enumerate(files):
            for i in range(6):
                self.fileTableView.setItem(index, i, QTableWidgetItem(file[i]))"""

    def addFileAction(self):
        """添加文件行为"""
        files = QFileDialog.getOpenFileNames(
            None,
            '添加文件',
            '',
            '批处理和命令脚本 (*.bat *.cmd);;批处理文件 (*.bat);;命令脚本 (*.cmd)'
        )[0]

        if files:
            cnt = JarConnector('./backend/fileAdder.jar', files)
            file_infos = cnt.received_data  # [[文件名,修改日期,后缀名,文件大小],...]
            if file_infos is not None:
                currentRowCount = self.fileTableView.rowCount()

                self.fileTableView.setRowCount(len(files) + currentRowCount)
                for index, oneInfo in enumerate(file_infos):
                    self.fileTableView.setItem(currentRowCount + index, 0, QTableWidgetItem(oneInfo[0]))
                    self.fileTableView.setItem(currentRowCount + index, 2, QTableWidgetItem(files[index]))
                    self.fileTableView.setItem(currentRowCount + index, 3, QTableWidgetItem(oneInfo[1]))
                    self.fileTableView.setItem(currentRowCount + index, 4, QTableWidgetItem(oneInfo[2]))
                    self.fileTableView.setItem(currentRowCount + index, 5, QTableWidgetItem(oneInfo[3]))

            self.saveContents()

    def removeFileAction(self):
        """删除文件行为"""
        selectedRanges = self.fileTableView.selectedRanges()
        if selectedRanges:
            # 收集所有要删除的行索引（从大到小排序）
            rows_to_delete = set()
            for range_obj in selectedRanges:
                rows_to_delete.update(range(range_obj.topRow(), range_obj.bottomRow() + 1))

            # 从大到小删除（避免索引变化问题）
            for row in sorted(rows_to_delete, reverse=True):
                self.fileTableView.removeRow(row)

            self.saveContents()
            return True
        else:
            return False

    def saveContents(self):
        """将表格的内容保存至文件"""

        # 获取表格内容
        allRows = []
        for row in range(self.fileTableView.rowCount()):
            oneRow = []
            for column in range(self.fileTableView.columnCount()):
                item = self.fileTableView.item(row, column)
                try:
                    oneRow.append(item.text())
                except AttributeError:
                    oneRow.append(None)
            allRows.append(oneRow)

        # 保存至文件
        with open('./config/fileTableContents.json', 'w', encoding='utf-8') as f:
            json.dump(allRows, f, ensure_ascii=False, indent=4)

    def loadContents(self):
        """加载已保存的文件内容"""
        with open('./config/fileTableContents.json', 'r', encoding='utf-8') as f:
            allRows = json.load(f)

            # 设置表格行数
            self.fileTableView.setRowCount(len(allRows))

            # 依次添加文件信息
            for i, row in enumerate(allRows):
                for j, column in enumerate(row):
                    self.fileTableView.setItem(i, j, QTableWidgetItem(column))
