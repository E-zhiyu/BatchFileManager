"""程序入口"""
import sys

from PyQt6.QtWidgets import QApplication

from AppConfig.config import cfg
from Interfaces.MainWindow import MainWindow

from Logs.log_recorder import *
from qfluentwidgets import FluentTranslator, Theme, setTheme, setThemeColor, isDarkTheme

# 启用DPI比例
"""
if cfg.get(cfg.dpiScale) != "Auto":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))
"""


def themeInit(theme: Theme = None):
    """应用主题初始化"""
    dark_style = """
        QWidget {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        """
    light_style = """
        QWidget {
            background-color: #f0f0f0;
            color: #000000;
        }
        """

    if theme is None:
        theme = cfg.get(cfg.themeMode)

    if theme == Theme.LIGHT:
        app.setStyleSheet(light_style)
    elif theme == Theme.DARK:
        app.setStyleSheet(dark_style)
    elif theme == Theme.AUTO:
        if isDarkTheme():
            app.setStyleSheet(dark_style)
        else:
            app.setStyleSheet(light_style)



# 将主题和主题色改变的信号连接至对应函数
cfg.themeColorChanged.connect(setThemeColor)
cfg.themeChanged.connect(setTheme)
cfg.themeChanged.connect(themeInit)

if __name__ == '__main__':
    logging.info('程序启动')
    # 创建应用程序
    app = QApplication(sys.argv)

    # 设置翻译器
    translator = FluentTranslator()
    app.installTranslator(translator)

    # 初始化主题
    themeInit()

    # 创建主窗口
    w = MainWindow()
    w.show()

    app.exec()
    logging.info('程序结束运行\n')
