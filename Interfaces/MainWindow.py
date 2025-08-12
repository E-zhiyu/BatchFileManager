"""主窗口模块"""
from PyQt6.QtCore import QSize, QEventLoop, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from AppConfig.config import cfg
from Interfaces.HomeInterface import HomeInterface
from Interfaces.PresetInterface import PresetInterface
from Interfaces.SettingInterface import SettingInterface
from Interfaces.InfoInterface import InfoInterface
from Interfaces.CMDInterface import CMDInterface

from qfluentwidgets import FluentWindow, NavigationItemPosition, SplashScreen, Dialog
from qfluentwidgets import FluentIcon as FIF

from Interfaces import version


class MainWindow(FluentWindow):
    """主窗口类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initWindow()
        self.initSubInterfaces()
        self.initNavigation()

        # 结束启动动画
        self.splashScreen.finish()

        # 文件运行状态改变时修改标题
        self.cmdInterface.socketClient.runningChanged.connect(self.changeTitle)

    def changeTitle(self, isRunning: bool = False):
        """
        根据文件运行状态修改标题
        :param isRunning: 文件是否运行
        """
        if isRunning:
            self.setWindowTitle(f'BatchFileManager-{version}（正在运行）')
        else:
            self.setWindowTitle(f'BatchFileManager-{version}')

    def initSubInterfaces(self):
        """初始化子窗口"""
        self.homeInterface = HomeInterface(self)
        self.settingInterface = SettingInterface(self)
        self.infoInterface = InfoInterface(self)
        self.cmdInterface = CMDInterface(self)
        self.presetInterface = PresetInterface(self)

    def initNavigation(self):
        """初始化导航栏"""
        self.navigationInterface.setExpandWidth(200)  # 设置导航栏展开宽度

        # 创建导航栏选项
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页')
        self.addSubInterface(self.cmdInterface, FIF.COMMAND_PROMPT, '控制台')
        self.addSubInterface(self.presetInterface, FIF.EMOJI_TAB_SYMBOLS, '文件预设')

        # 添加导航栏底部按钮
        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.infoInterface, FIF.INFO, '关于软件', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        """初始化窗口"""
        self.resize(800, 600)
        self.setMinimumWidth(500)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle(f'BatchFileManager-{version}')

        # 创建启动界面
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(102, 102))

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.show()

        loop = QEventLoop(self)
        QTimer.singleShot(500, loop.quit)
        loop.exec()

    def closeEvent(self, event):
        """重写关闭事件"""

        cfg.set(cfg.appVersion, version)  # 更新应用版本号

        # 检测是否有程序正在运行并弹出对话框
        if self.cmdInterface.socketClient.running:
            w = Dialog('文件正在运行', '当前有文件正在运行，关闭应用将强制结束进程，确认继续吗？')
            if not w.exec():
                event.ignore()
                return

        # 关闭时保存表格宽度
        fileTableWidth = [self.homeInterface.fileTableView.columnWidth(i) for i in range(5)]
        cfg.set(cfg.tableColumnWidth, fileTableWidth)

        # 保存表格内容
        self.homeInterface.saveContents()

        # 切断与子进程的连接
        self.cmdInterface.stopCommunicationAndKill()

        super().closeEvent(event)
