"""连接.jar文件的模块"""
import json
import subprocess

from AppConfig.config import cfg
from Logs.log_recorder import logging


class JarConnector:
    """
    连接.jar文件的类
    :param target：需要运行的.jar文件
    """

    def __init__(self, target: str):
        self.target = target  # 目标.jar文件路径
        self.custom_java_path = cfg.get(cfg.customJavaPath)

        # 启动Java进程
        self.java_process = subprocess.Popen(
            [self.custom_java_path if cfg.get(cfg.useCustomJavaPath) else "java", '-jar', self.target],
            creationflags=subprocess.CREATE_NO_WINDOW,  # 关键参数，不显示窗口
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logging.info(f'JarConnector成功创建子进程，目标："{self.target}"')

    def sendData(self, *data):
        """
        通过标准输入向Java子进程发送数据
        :param data: 待发送的数据列表（不需要换行符）
        """
        # 将列表转换为JSON字符串并发送
        for d in data:
            json_data = json.dumps(d)
            self.java_process.stdin.write(json_data + '\n')  # 添加换行符作为结束标记
            self.java_process.stdin.flush()  # 确保数据被发送
        self.java_process.stdin.close()
        logging.info('JarConnector成功发送数据')

    def receiveData(self):
        """从Java子进程读取标准输出中的数据"""
        logging.info('JarConnector尝试接收数据……')
        json_data = self.java_process.stdout.readline()
        try:
            data = json.loads(json_data)
            logging.info('JarConnector成功接收数据')
            return data
        except json.decoder.JSONDecodeError:
            logging.warning('JarConnector接收数据失败')
            return None
