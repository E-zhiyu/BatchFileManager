"""主页模块"""
import json
import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QTableWidgetItem, QFileDialog

from qfluentwidgets import PushButton, TableWidget, InfoBar, InfoBarPosition, Dialog, ToolTipFilter, ToolTipPosition
from qfluentwidgets import FluentIcon as FIF

from AppConfig.config import cfg
from Connector.JarConnector import JarConnector
from Logs.log_recorder import logging


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
        self.runButton.setToolTip('运行单个选中的文件')
        self.runButton.installEventFilter(ToolTipFilter(self.runButton,position=ToolTipPosition.BOTTOM))
        self.btnLayout.addWidget(self.runButton)
        self.runButton.clicked.connect(self.runFileAction)

        self.addButton = PushButton(FIF.ADD, "添加文件")
        self.addButton.setToolTip('将文件添加至表格中')
        self.addButton.installEventFilter(ToolTipFilter(self.addButton,position=ToolTipPosition.BOTTOM))
        self.btnLayout.addWidget(self.addButton)
        self.addButton.clicked.connect(self.addFileAction)

        self.removeButton = PushButton(FIF.DELETE.icon(color='red'), '删除文件')
        self.removeButton.setToolTip('将选中的文件移出表格')
        self.removeButton.installEventFilter(ToolTipFilter(self.removeButton,position=ToolTipPosition.BOTTOM))
        self.btnLayout.addWidget(self.removeButton)
        self.removeButton.clicked.connect(self.removeFileAction)

        self.openFolderButton = PushButton(FIF.FOLDER, '打开所在文件夹')
        self.openFolderButton.setToolTip('打开选中文件的文件夹')
        self.openFolderButton.installEventFilter(ToolTipFilter(self.openFolderButton,position=ToolTipPosition.BOTTOM))
        self.btnLayout.addWidget(self.openFolderButton)
        self.openFolderButton.clicked.connect(self.openFolderAction)

        # 文件列表视图
        self.fileTableView = TableWidget(self)
        self.mainLayout.addWidget(self.fileTableView)

        self.fileTableView.setBorderVisible(True)  # 设置边界可见性
        self.fileTableView.setBorderRadius(5)  # 设置边界圆角弧度
        self.fileTableView.setColumnCount(6)  # 设置列数
        self.fileTableView.verticalHeader().hide()  # 隐藏行序号
        self.fileTableView.setHorizontalHeaderLabels(['文件名', '备注', '文件路径', '修改日期', '文件类型', '大小'])
        # self.fileTableView.setSortingEnabled(True)  # 启用表头排序

        # 恢复软件关闭前的列宽
        columnWidthList = cfg.get(cfg.tableColumnWidth)
        if columnWidthList is not None:
            for i, width in enumerate(columnWidthList):
                if width:
                    self.fileTableView.setColumnWidth(i, width)
        else:
            self.fileTableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 备注列拉伸以适应窗口
            self.fileTableView.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # 文件路径拉伸

    def runFileAction(self):
        """运行文件行为"""

        selectedRanges = self.fileTableView.selectedRanges()
        if selectedRanges:
            logging.info('运行文件中……')

            # 收集选中的行索引（从大到小排序）
            selectedRowsIndex = []
            for range_obj in selectedRanges:
                selectedRowsIndex.append(range(range_obj.bottomRow(), range_obj.topRow() + 1))

            # 判断是否多选
            if len(selectedRowsIndex) > 1:
                InfoBar.warning(
                    "提示",
                    "只能同时运行一个文件",
                    duration=1500,
                    position=InfoBarPosition.TOP,
                    parent=self.parentWindow
                )
            else:
                if not self.parentWindow.cmdInterface.sktClient.running:
                    item = self.fileTableView.item(self.fileTableView.currentRow(), 2)  # 获取保存文件路径的元素
                    filePath = item.text()
                    JarConnector('./backend/fileRunner.jar', [filePath])
                    self.parentWindow.cmdInterface.startCommunication()  # 开始与子进程通信

                    InfoBar.success(
                        '开始运行',
                        '请前往控制台界面查看运行详情',
                        position=InfoBarPosition.TOP,
                        duration=1500,
                        parent=self.parentWindow
                    )
                    logging.info('文件成功运行')
                else:
                    InfoBar.error(
                        '运行失败',
                        '已有正在运行的文件',
                        position=InfoBarPosition.TOP,
                        duration=1500,
                        parent=self.parentWindow
                    )
                    logging.info('运行失败，已有正在运行的文件')
        else:
            InfoBar.warning(
                '提示',
                '请选择至少一个文件',
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self.parentWindow
            )

    def addFileAction(self):
        """添加文件行为"""

        files = QFileDialog.getOpenFileNames(
            None,
            '添加文件',
            '',
            '批处理和命令脚本 (*.bat *.cmd);;批处理文件 (*.bat);;命令脚本 (*.cmd)'
        )[0]

        if files:
            logging.info('开始添加文件……')

            fileAdd_cnt = JarConnector('./backend/fileAdder.jar', files)
            file_infos = fileAdd_cnt.receiveData()  # [[文件名,修改日期,后缀名,文件大小],...]
            if file_infos is not None:
                currentRowCount = self.fileTableView.rowCount()

                self.fileTableView.setRowCount(len(files) + currentRowCount)
                for index, oneInfo in enumerate(file_infos):
                    self.fileTableView.setItem(currentRowCount + index, 0, QTableWidgetItem(oneInfo[0]))
                    self.fileTableView.setItem(currentRowCount + index, 2, QTableWidgetItem(files[index]))
                    self.fileTableView.setItem(currentRowCount + index, 3, QTableWidgetItem(oneInfo[1]))
                    self.fileTableView.setItem(currentRowCount + index, 4, QTableWidgetItem(oneInfo[2]))
                    self.fileTableView.setItem(currentRowCount + index, 5, QTableWidgetItem(oneInfo[3]))

                InfoBar.success(
                    '成功',
                    f'已添加{len(file_infos)}个文件',
                    duration=1500,
                    position=InfoBarPosition.TOP,
                    parent=self.parentWindow
                )
                logging.info(f'成功添加{len(files)}个文件')

            else:
                InfoBar.error(
                    '失败',
                    '无法添加文件',
                    duration=1500,
                    position=InfoBarPosition.TOP,
                    parent=self.parentWindow
                )
                logging.error('无法添加文件')

            self.saveContents()

    def removeFileAction(self):
        """删除文件行为"""

        selectedRanges = self.fileTableView.selectedRanges()
        if selectedRanges:
            w = Dialog('删除文件', '确认从列表中删除选中的文件吗？（此操作不会删除硬盘上的文件）', self.parentWindow)
            if w.exec():
                logging.info('开始删除文件……')

                # 收集所有要删除的行索引（从大到小排序）
                rowsToDelete = set()
                for range_obj in selectedRanges:
                    rowsToDelete.update(range(range_obj.topRow(), range_obj.bottomRow() + 1))

                # 从大到小删除（避免索引变化问题）
                i = 0
                for row in sorted(rowsToDelete, reverse=True):
                    self.fileTableView.removeRow(row)
                    i += 1

                InfoBar.success(
                    '成功',
                    '已删除选中的文件',
                    duration=1500,
                    position=InfoBarPosition.TOP,
                    parent=self.parentWindow
                )

                logging.info(f'已删除{i}个文件')
                self.saveContents()
        else:
            InfoBar.warning(
                '提示',
                '请选择至少一个文件',
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self.parentWindow
            )

    def openFolderAction(self):
        """打开文件夹行为"""

        selectedRanges = self.fileTableView.selectedRanges()

        if selectedRanges:
            # 收集所有要删除的行索引（从大到小排序）
            selectedRowsIndex = set()
            for range_obj in selectedRanges:
                selectedRowsIndex.update(range(range_obj.topRow(), range_obj.bottomRow() + 1))

            dirToOpen = []
            for i in selectedRowsIndex:
                item = self.fileTableView.item(i, 2)
                filePath = item.text()
                directory = os.path.dirname(filePath).replace('/', '\\')
                dirToOpen.append(directory)

            dirToOpen = set(dirToOpen)
            if len(dirToOpen) > 3:
                w = Dialog('打开文件夹', '一次性打开过多文件夹可能导致卡顿，确认继续吗？', self.parentWindow)
                if w.exec():
                    for dir in dirToOpen:
                        os.system(f'explorer "{dir}"')
            else:
                for dir in dirToOpen:
                    os.system(f'explorer "{dir}"')
        else:
            InfoBar.warning(
                '提示',
                '请选择至少一个文件',
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self.parentWindow
            )

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
        if not os.path.isdir('./config'):
            os.mkdir('./config')

        with open('./config/fileTableContents.json', 'w', encoding='utf-8') as f:
            json.dump(allRows, f, ensure_ascii=False, indent=4)

    def loadContents(self):
        """加载已保存的文件内容"""

        try:
            with open('./config/fileTableContents.json', 'r', encoding='utf-8') as f:
                allRows = json.load(f)

                # 设置表格行数
                self.fileTableView.setRowCount(len(allRows))

                # 依次添加文件信息
                for i, row in enumerate(allRows):
                    for j, column in enumerate(row):
                        self.fileTableView.setItem(i, j, QTableWidgetItem(column))
        except FileNotFoundError:
            pass
