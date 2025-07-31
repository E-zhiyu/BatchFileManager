"""主窗口模块"""
from PyQt6.QtCore import QSize, QEventLoop, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from AppConfig.config import cfg
from Interfaces.HomeInterface import HomeInterface
from Interfaces.SettingInterface import SettingInterface
from Interfaces.InfoInterface import InfoInterface

from qfluentwidgets import FluentWindow, NavigationItemPosition, SplashScreen
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

    def initSubInterfaces(self):
        """初始化子窗口"""
        self.homeInterface = HomeInterface(self)
        self.settingInterface = SettingInterface(self)
        self.infoInterface = InfoInterface(self)

    def initNavigation(self):
        """初始化导航栏"""
        self.navigationInterface.setExpandWidth(200)  # 设置导航栏展开宽度

        # 创建导航栏选项
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页')

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
        fileTableWidth = [self.homeInterface.fileTableView.columnWidth(i) for i in range(5)]
        cfg.set(cfg.tableColumnWidth, fileTableWidth)
        super().closeEvent(event)
