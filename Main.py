"""程序入口"""
import sys

from PyQt6.QtWidgets import QApplication

from AppConfig.config import cfg
from Interfaces.MainWindow import MainWindow

from Logs.log_recorder import *

# 启用DPI比例
"""
if cfg.get(cfg.dpiScale) != "Auto":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))
"""

def run_with_gui():
    logging.info('程序启动')
    # 创建应用程序
    app = QApplication(sys.argv)

    # 创建主窗口
    w = MainWindow()
    w.show()

    app.exec()
    logging.info('程序结束运行\n')
