# FilenameChanger/log/log_recorder.py
"""
日志记录模块
"""
import logging
import os
from datetime import datetime

log_dir = './logs'


class DailyFileHandler(logging.FileHandler):
    def __init__(self):
        """
        功能：每天动态生成YYYY-MM-DD.log
        """
        os.makedirs(log_dir, exist_ok=True)
        filename = self.get_today_filename()
        super().__init__(filename, encoding='utf-8')

    @staticmethod
    def get_today_filename():
        """
        功能：生成当前日期对应的文件名
        """
        today = datetime.now().strftime('%Y-%m-%d')
        return os.path.join(log_dir, f'{today}.log')


def setup_logger():
    formatter = logging.Formatter('%(asctime)s - [%(filename)s-%(lineno)d/%(levelname)s] : %(message)s',
                                  datefmt='%H:%M:%S')
    handler = DailyFileHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


setup_logger()
