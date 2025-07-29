"""连接.jar文件的模块"""
import json
import subprocess


class JarConnector:
    """
    连接.jar文件的类
    参数 target：需要运行的.jar文件
    参数 sent_data：需要发送的参数
    """

    def __init__(self, target: str, sent_data):
        self.target = target  # 目标.jar文件路径
        self.sent_data = sent_data  # 需要发送的数据
        self.received_data = None  # 接收到的数据

        # 启动Java进程
        self.java_process = subprocess.Popen(
            ["java", '-jar', self.target],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )

        self.sendData()
        self.receiveData()

    def sendData(self):
        """发送数据"""

        # 将列表转换为JSON字符串并发送
        json_data = json.dumps(self.sent_data)
        self.java_process.stdin.write(json_data + "\n")  # 添加换行符作为结束标记
        self.java_process.stdin.flush()  # 确保数据被发送

    def receiveData(self):
        """接收数据并保存"""
        json_data = self.java_process.stdout.readline()
        self.received_data = json.loads(json_data)
