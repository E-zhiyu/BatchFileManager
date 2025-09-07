"""主页模块"""
import os

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QTableWidgetItem, QFileDialog, QTableWidget

from qfluentwidgets import PushButton, TableWidget, InfoBar, InfoBarPosition, Dialog, ToolTipFilter, ToolTipPosition, \
    RoundMenu, Action
from qfluentwidgets import FluentIcon as FIF

from AppConfig.config import cfg
from Connector.JarConnector import JarConnector
from Logs.log_recorder import logging


class FileTabel(TableWidget):
    """文件列表类"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setEditTriggers(
            QTableWidget.EditTrigger.DoubleClicked |  # 双击
            QTableWidget.EditTrigger.EditKeyPressed  # 按F2键
        )

    def setItem(self, row, column, item):
        if column != 1:
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # 如果列下标不为1则不可编辑

        super().setItem(row, column, item)


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

        self.__initControls()  # 初始化控件
        self.__initShortcuts()  # 初始化快捷键

        # 加载已保存的文件内容
        self.loadContents()

        cfg.fileDataChanged.connect(self.refreshFileTable)  # 将文件数据改变信号连接至刷新布局方法

    def __initControls(self):
        """初始化控件"""

        # 添加操作按钮
        self.btnLayout = QHBoxLayout(self)
        self.btnLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.mainLayout.addLayout(self.btnLayout)

        self.runButton = PushButton(FIF.PLAY.icon(color='green'), '运行文件')
        self.runButton.setToolTip('运行单个选中的文件\n             (F5)')
        self.runButton.installEventFilter(ToolTipFilter(self.runButton, position=ToolTipPosition.BOTTOM))
        self.btnLayout.addWidget(self.runButton)
        self.runButton.clicked.connect(lambda: self.runFileAction())

        self.addButton = PushButton(FIF.ADD, "添加文件")
        self.addButton.setToolTip('将文件添加至表格中')
        self.addButton.installEventFilter(ToolTipFilter(self.addButton, position=ToolTipPosition.BOTTOM))
        self.btnLayout.addWidget(self.addButton)
        self.addButton.clicked.connect(self.addFileAction)

        self.removeButton = PushButton(FIF.DELETE.icon(color='red'), '删除文件')
        self.removeButton.setToolTip('将选中的文件移出表格\n            (Delete)')
        self.removeButton.installEventFilter(ToolTipFilter(self.removeButton, position=ToolTipPosition.BOTTOM))
        self.btnLayout.addWidget(self.removeButton)
        self.removeButton.clicked.connect(lambda: self.removeFileAction())

        self.openFolderButton = PushButton(FIF.FOLDER.icon(color='orange'), '打开所在文件夹')
        self.openFolderButton.setToolTip('打开选中文件的文件夹')
        self.openFolderButton.installEventFilter(ToolTipFilter(self.openFolderButton, position=ToolTipPosition.BOTTOM))
        self.btnLayout.addWidget(self.openFolderButton)
        self.openFolderButton.clicked.connect(lambda: self.openFolderAction())

        # 文件表格视图
        self.fileTableView = FileTabel(self)
        self.mainLayout.addWidget(self.fileTableView)

        self.fileTableView.setBorderVisible(True)  # 设置边界可见性
        self.fileTableView.setBorderRadius(5)  # 设置边界圆角弧度
        self.fileTableView.setColumnCount(6)  # 设置列数
        self.fileTableView.verticalHeader().hide()  # 隐藏行序号
        self.fileTableView.setHorizontalHeaderLabels(['文件名', '备注', '文件路径', '修改日期', '文件类型', '大小'])
        self.fileTableView.setSortingEnabled(True)  # 启用表头排序

        self.fileTableView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)  # 将表格的上下文菜单策略设置为 自定义模式
        self.fileTableView.customContextMenuRequested.connect(self.showContextMenu)  # 绑定显示右键菜单的方法
        self.fileTableView.itemChanged.connect(self.saveContents)  # 编辑内容后执行保存方法

        # 恢复软件关闭前的列宽
        columnWidthList = cfg.get(cfg.tableColumnWidth)
        if columnWidthList is not None:
            for i, width in enumerate(columnWidthList):
                if width:
                    self.fileTableView.setColumnWidth(i, width)
        else:
            self.fileTableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 备注列拉伸以适应窗口
            self.fileTableView.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # 文件路径拉伸

    def __initShortcuts(self):
        """初始化快捷键"""
        self.runButton.setShortcut('F5')
        self.removeButton.setShortcut('delete')

    def showContextMenu(self, pos: QPoint):
        """
        呼出右键上下文菜单
        :param pos: 光标位置
        """

        # 获取全局坐标
        global_pos = self.fileTableView.viewport().mapToGlobal(pos)

        # 判断点击的行
        row = self.fileTableView.rowAt(pos.y())
        if row < 0:  # 若没有选中有效行则直接结束
            return

        # 为菜单添加动作
        menu = RoundMenu()
        fileEdit_actions = [
            Action(FIF.PLAY.icon(color='green'), '运行文件', triggered=lambda: self.runFileAction(row)),
            Action(FIF.EDIT, '编辑备注', triggered=lambda: self.editRemarkAction(row)),
            Action(FIF.SYNC, '重定向文件', triggered=lambda: self.redirectFile(row)),
        ]
        menu.addActions(fileEdit_actions)
        menu.addSeparator()  # 添加一个分割线
        fileOperation_actions = [
            Action(FIF.DELETE.icon(color='red'), '删除文件', triggered=lambda: self.removeFileAction(row)),
            Action(FIF.FOLDER.icon(color='orange'), '打开文件夹', triggered=lambda: self.openFolderAction(row)),
        ]
        menu.addActions(fileOperation_actions)

        # 计算菜单尺寸
        menu_rect = menu.actionGeometry(menu.actions()[0])  # 获取第一个动作的尺寸
        menu_height = menu_rect.height() * len(menu.actions())
        menu_width = menu_rect.width()

        # 获取窗口可用区域
        window_rect = self.fileTableView.window().geometry()

        # 检查是否会超出右边界
        if global_pos.x() + menu_width > window_rect.right():
            global_pos.setX(window_rect.right() - menu_width)

        # 检查是否会超出下边界
        if global_pos.y() + menu_height > window_rect.bottom():
            global_pos.setY(global_pos.y() - menu_height)

        # 显示菜单
        menu.exec(global_pos)

    def runFileAction(self, row: int = None):
        """
        运行文件行为
        :param row:选中的单个行下标（默认为空）
        """

        # 获取文件路径
        if row is None:
            selectedRanges = self.fileTableView.selectedRanges()
            if selectedRanges:

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
                    return  # 多选时不运行文件
                else:
                    item = self.fileTableView.item(self.fileTableView.currentRow(), 2)  # 获取保存文件路径的元素
            else:
                InfoBar.warning(
                    '提示',
                    '请先选择一个文件',
                    position=InfoBarPosition.TOP,
                    duration=1500,
                    parent=self.parentWindow
                )
                return  # 未选择文件时结束方法调用
        else:
            item = self.fileTableView.item(row, 2)

        # 运行文件
        if self.parentWindow.cmdInterface.socketClient.running:
            InfoBar.error(
                '运行失败',
                '已有正在运行的文件',
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self.parentWindow
            )
            logging.info('运行失败，已有正在运行的文件')
            return

        # 弹出确认对话框
        w = Dialog('运行文件', '是否确认运行选中的文件')
        if not w.exec():
            return  # 对话框选择取消不运行文件

        logging.info('运行文件中……')
        filePath = item.text()

        # 判断文件是否存在
        if not os.path.isfile(filePath):
            # 在备注中标记“（已失效）”
            remark = self.fileTableView.item(self.fileTableView.currentRow(), 1).text()
            if not remark.startswith('（已失效）'):
                remark = f'（已失效）{remark}'
                self.fileTableView.setItem(self.fileTableView.currentRow(), 1, QTableWidgetItem(remark))

            self.fileTableView.clearSelection()  # 取消所有选择

            InfoBar.error(
                '失败',
                '所选的文件不存在',
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self.parentWindow
            )
            logging.error('运行失败：文件不存在')
            return

        # 在备注中删除“（已失效）”字样
        remark = self.fileTableView.item(self.fileTableView.currentRow(), 1).text()
        if remark.startswith('（已失效）'):
            remark = remark.lstrip('（已失效）')
            self.fileTableView.setItem(self.fileTableView.currentRow(), 1, QTableWidgetItem(remark))

        running_cnt = JarConnector('./backend/fileRunner.jar')
        running_cnt.sendData([filePath])
        ack = running_cnt.receiveData()
        if not ack:
            InfoBar.error(
                "运行失败",
                "Java后端运行异常，请检查Java版本",
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self.parentWindow
            )
            logging.error('运行失败：Java后端运行异常')
            return  # 应答值为假不运行文件

        InfoBar.success(
            '开始运行',
            '请前往控制台界面查看运行详情',
            position=InfoBarPosition.TOP,
            duration=1500,
            parent=self.parentWindow
        )
        logging.info('文件已开始运行')
        self.parentWindow.cmdInterface.startCommunication()  # 开始与子进程通信

    def editRemarkAction(self, row: int):
        """
        编辑文件备注
        :param row:选中的单个行下标
        """
        logging.info('编辑备注')
        self.fileTableView.editItem(self.fileTableView.item(row, 1))

    def redirectFile(self, row: int):
        """
        重定向文件
        :param row:需要重定向的文件条目所在的行下标
        """
        old_path = self.fileTableView.item(row, 2).text()
        filePath = QFileDialog.getOpenFileName(
            None,
            '添加文件',
            os.path.dirname(old_path),
            '批处理和命令脚本 (*.bat *.cmd);;批处理文件 (*.bat);;命令脚本 (*.cmd)'
        )[0]
        if not filePath:
            return

        redirect_cnt = JarConnector('./backend/fileAdder.jar')
        redirect_cnt.sendData([filePath])
        fileInfos = redirect_cnt.receiveData()[0]

        self.fileTableView.blockSignals(True)
        self.fileTableView.setItem(row, 0, QTableWidgetItem(fileInfos[0]))  # 文件名
        self.fileTableView.setItem(row, 2, QTableWidgetItem(filePath))  # 路径
        self.fileTableView.setItem(row, 3, QTableWidgetItem(fileInfos[1]))  # 修改日期
        self.fileTableView.setItem(row, 4, QTableWidgetItem(fileInfos[2]))  # 文件类型
        self.fileTableView.setItem(row, 5, QTableWidgetItem(fileInfos[3]))  # 文件大小

        # 去除“已失效”标记
        remark = self.fileTableView.item(row, 1).text()
        if remark.startswith('（已失效）'):
            remark = remark.lstrip('（已失效）')
            self.fileTableView.setItem(row, 1, QTableWidgetItem(remark))

        self.fileTableView.blockSignals(False)

        InfoBar.success(
            '成功',
            '已更新文件信息',
            position=InfoBarPosition.TOP,
            duration=1500,
            parent=self.parentWindow
        )

        self.saveContents()

    def addFileAction(self):
        """添加文件行为"""

        files = QFileDialog.getOpenFileNames(
            None,
            '添加文件',
            '',
            '批处理和命令脚本 (*.bat *.cmd);;批处理文件 (*.bat);;命令脚本 (*.cmd)'
        )[0]
        if not files:
            return

        logging.info('开始添加文件……')
        fileAdd_cnt = JarConnector('./backend/fileAdder.jar')
        fileAdd_cnt.sendData(files)
        file_infos = fileAdd_cnt.receiveData()  # [[文件名,修改日期,后缀名,文件大小],...]
        if file_infos is None or file_infos[0] is None:  # 判断是否接受None或者第一个元素是否为空
            InfoBar.error(
                '失败',
                '无法添加文件',
                duration=1500,
                position=InfoBarPosition.TOP,
                parent=self.parentWindow
            )
            logging.error('无法添加文件')
            return

        currentRowCount = self.fileTableView.rowCount()

        self.fileTableView.setSortingEnabled(False)  # 暂时禁用排序防止插入的数据错位
        self.fileTableView.blockSignals(True)
        self.fileTableView.setRowCount(len(files) + currentRowCount)
        for index, oneInfo in enumerate(file_infos):
            self.fileTableView.setItem(currentRowCount + index, 0, QTableWidgetItem(oneInfo[0]))
            self.fileTableView.setItem(currentRowCount + index, 1,
                                       QTableWidgetItem(None))  # 即使没有获取信息也要填充防止获取内容时类型错误
            self.fileTableView.setItem(currentRowCount + index, 2, QTableWidgetItem(files[index]))
            self.fileTableView.setItem(currentRowCount + index, 3, QTableWidgetItem(oneInfo[1]))
            self.fileTableView.setItem(currentRowCount + index, 4, QTableWidgetItem(oneInfo[2]))
            self.fileTableView.setItem(currentRowCount + index, 5, QTableWidgetItem(oneInfo[3]))
        self.fileTableView.setSortingEnabled(True)
        self.fileTableView.blockSignals(False)

        InfoBar.success(
            '成功',
            f'已添加{len(file_infos)}个文件',
            duration=1500,
            position=InfoBarPosition.TOP,
            parent=self.parentWindow
        )
        logging.info(f'成功添加{len(files)}个文件')

        self.saveContents()

    def removeFileAction(self, row: int = None):
        """
        删除文件行为
        :param row:选中的单个行下标（默认为空）
        """

        # 获取删除前的行数
        currentRowCount = self.fileTableView.rowCount()

        if row is None:
            selectedRanges = self.fileTableView.selectedRanges()
            if not selectedRanges:
                InfoBar.warning(
                    '提示',
                    '请选择至少一个文件',
                    position=InfoBarPosition.TOP,
                    duration=1500,
                    parent=self.parentWindow
                )
                return

            w = Dialog('删除文件', '确认从列表中删除选中的文件吗？（此操作不会删除硬盘上的文件）', self.parentWindow)
            if not w.exec():
                return

            # 收集所有要删除的行索引（从大到小排序）
            rowsToDelete = set()
            for range_obj in selectedRanges:
                rowsToDelete.update(range(range_obj.topRow(), range_obj.bottomRow() + 1))

            # 从大到小删除（避免索引变化问题）
            i = 0
            for row in sorted(rowsToDelete, reverse=True):
                self.fileTableView.removeRow(row)
                i += 1

            self.fileTableView.setRowCount(currentRowCount - i)  # 减少行数
            self.fileTableView.clearSelection()  # 取消所有选择

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
            w = Dialog('删除文件', '确认从列表中删除选中的文件吗？（此操作不会删除硬盘上的文件）', self.parentWindow)
            if not w.exec():
                return

            self.fileTableView.removeRow(row)
            self.fileTableView.setRowCount(currentRowCount - 1)  # 减少行数
            self.fileTableView.clearSelection()  # 取消所有选择

            InfoBar.success(
                '成功',
                '已删除选中的文件',
                duration=1500,
                position=InfoBarPosition.TOP,
                parent=self.parentWindow
            )

            logging.info('已删除1个文件')
            self.saveContents()

    def openFolderAction(self, row: int = None):
        """
        打开文件夹行为
        :param row:选中的单个行下标（默认为空）
        """

        if row is None:
            selectedRanges = self.fileTableView.selectedRanges()

            if not selectedRanges:  # 排除没有选择的情况
                InfoBar.warning(
                    '提示',
                    '请选择至少一个文件',
                    position=InfoBarPosition.TOP,
                    duration=1500,
                    parent=self.parentWindow
                )
                return

            # 收集所有要删除的行索引（从大到小排序）
            selectedRowsIndex = set()
            for range_obj in selectedRanges:
                selectedRowsIndex.update(range(range_obj.topRow(), range_obj.bottomRow() + 1))

            dirToOpen = []
            for i in selectedRowsIndex:
                item = self.fileTableView.item(i, 2)
                filePath = item.text()
                directory = os.path.dirname(filePath).replace('/', '\\')
                if os.path.isdir(directory):
                    dirToOpen.append(directory)

            dirToOpen = set(dirToOpen)
            if len(dirToOpen) > 3:
                w = Dialog('打开文件夹', '一次性打开过多文件夹可能导致桌面混乱，确认继续吗？', self.parentWindow)
                if w.exec():
                    for directory in dirToOpen:
                        os.startfile(directory)
            elif len(dirToOpen) == 0:
                InfoBar.error(
                    '失败',
                    '所选文件的目录均不存在',
                    position=InfoBarPosition.TOP,
                    duration=1500,
                    parent=self.parentWindow
                )
            else:
                for directory in dirToOpen:
                    os.startfile(directory)
                logging.info('用户打开文件所在目录')
        else:
            # 获取目录路径
            item = self.fileTableView.item(row, 2)
            filePath = item.text()
            directory = os.path.dirname(filePath).replace('/', '\\')

            if not os.path.isdir(directory):
                InfoBar.error(
                    '失败',
                    '所选文件的目录不存在',
                    position=InfoBarPosition.TOP,
                    duration=1500,
                    parent=self.parentWindow
                )
                return

            os.startfile(directory)
            logging.info('用户打开文件所在目录')

    def refreshFileTable(self):
        """刷新文件列表"""
        self.fileTableView.blockSignals(True)
        self.fileTableView.clear()
        self.fileTableView.setHorizontalHeaderLabels(['文件名', '备注', '文件路径', '修改日期', '文件类型', '大小'])
        self.fileTableView.blockSignals(False)

        self.loadContents()

    def saveContents(self):
        """将表格的内容保存至文件"""
        logging.info('开始保存文件数据……')

        if not cfg.get(cfg.isOpeningJavaPathCorrect):
            logging.warning('由于程序启动时Java路径有误，故不保存文件信息')
            return

        # 获取表格内容
        allRows = []
        for row in range(self.fileTableView.rowCount()):
            oneRow = []
            for column in range(self.fileTableView.columnCount()):
                if column >= 3: continue  # 不记录修改日期、文件类型和文件大小
                item = self.fileTableView.item(row, column)
                try:
                    oneRow.append(item.text())
                except AttributeError:
                    oneRow.append(None)
            allRows.append(oneRow)

        # 保存至文件
        if not os.path.isdir('./config'):
            os.mkdir('./config')

        jsonWriter_cnt = JarConnector('./backend/jsonWriter.jar')
        jsonWriter_cnt.sendData(['./config/fileTableContents.json'], allRows)
        flag = jsonWriter_cnt.receiveData()

        if flag:
            logging.info('文件数据保存成功')
        else:
            logging.error('文件数据保存失败')

    def loadContents(self):
        """加载已保存的文件内容"""
        logging.info('开始读取已保存的文件信息……')

        jsonReader_cnt = JarConnector('./backend/jsonReader.jar')
        jsonReader_cnt.sendData(['./config/fileTableContents.json'])
        allRows = jsonReader_cnt.receiveData()
        if not allRows:
            InfoBar.error(
                '错误',
                '文件信息读取出错，请检查Java版本',
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self.parentWindow
            )
            cfg.set(cfg.isOpeningJavaPathCorrect, False)
            logging.error('文件信息读取失败')
            return

        logging.info('文件信息读取成功')
        # 检测文件是否存在
        for rowIndex, fileInfo in enumerate(allRows):
            if not os.path.isfile(fileInfo[2]) and not allRows[rowIndex][1].startswith('（已失效）'):
                allRows[rowIndex][1] = f'（已失效）{fileInfo[1]}'  # 如果文件不存在则在备注中标记

        # 设置表格行数
        self.fileTableView.setRowCount(len(allRows))

        # 依次添加文件信息
        self.fileTableView.blockSignals(True)  # 阻断信号防止加载过程中保存表格信息

        if self.versionCompare(cfg.get(cfg.appVersion).lstrip('v'), '1.1.0') < 0:  # 若上一次启动的版本号低于1.1.0，则升级数据结构
            allFilePath = []
            for i, row in enumerate(allRows):
                for j, column in enumerate(row):
                    if j == 3 or j == 5: continue  # 不加载修改日期和文件大小
                    if j == 2: allFilePath.append(column)  # 获取文件路径
                    self.fileTableView.setItem(i, j, QTableWidgetItem(column))
        else:  # 若以上判断均为否，则正常读取数据
            allFilePath = []
            for i, row in enumerate(allRows):
                self.fileTableView.setItem(i, 0, QTableWidgetItem(row[0]))  # 文件名
                self.fileTableView.setItem(i, 1, QTableWidgetItem(row[1]))  # 备注
                self.fileTableView.setItem(i, 2, QTableWidgetItem(row[2]))  # 路径
                allFilePath.append(row[2])

        logging.info('开始刷新文件修改日期和大小……')
        getInfo_cnt = JarConnector('./backend/fileInfoGetter.jar')
        getInfo_cnt.sendData(allFilePath)
        allInfos = getInfo_cnt.receiveData()
        if allInfos:
            logging.info('文件修改日期和大小刷新成功')
            for rowIndex, fileInfo in enumerate(allInfos):
                self.fileTableView.setItem(rowIndex, 3, QTableWidgetItem(fileInfo[0]))
                self.fileTableView.setItem(rowIndex, 4, QTableWidgetItem(fileInfo[1]))
                self.fileTableView.setItem(rowIndex, 5, QTableWidgetItem(fileInfo[2]))
        else:
            logging.warning('文件修改日期和大小刷新失败')
            for i in range(self.fileTableView.rowCount()):
                self.fileTableView.setItem(i, 3, QTableWidgetItem('未知'))
                self.fileTableView.setItem(i, 5, QTableWidgetItem('未知'))
            InfoBar.warning(
                '警告',
                '软件的Java路径有误，无法获取修改日期和文件大小',
                duration=-1,
                position=InfoBarPosition.TOP,
                parent=self.parentWindow
            )

        self.fileTableView.blockSignals(False)

    @staticmethod
    def versionCompare(dataVersion, targetVersion):
        """
        版本比较方法
        :param dataVersion: JSON数据版本号
        :param targetVersion: 需要比较的版本号
        :return: 0-相同，1-前者大于后者，-1-前者小于后者
        """

        jh, jm, jl = map(int, dataVersion.split('.'))
        th, tm, tl = map(int, targetVersion.split('.'))

        if jh > th:
            return 1
        elif jh < th:
            return -1
        else:
            if jm > tm:
                return 1
            elif jm < tm:
                return -1
            else:
                if jl > tl:
                    return 1
                elif jl < tl:
                    return -1
                else:
                    return 0
