"""连接.jar文件的模块"""
import json
import subprocess


class JarConnector:
    """连接.jar文件的类"""

    def __init__(self, target: str, data):
        self.target = target  # 目标.jar文件路径
        self.data = data  # 需要发送的数据

        self.sendData()

    def sendData(self):
        # 启动Java进程
        java_process = subprocess.Popen(
            ["java", '-jar', self.target],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )

        # 将列表转换为JSON字符串并发送
        json_data = json.dumps(self.data)
        java_process.stdin.write(json_data + "\n")  # 添加换行符作为结束标记
        java_process.stdin.flush()  # 确保数据被发送
