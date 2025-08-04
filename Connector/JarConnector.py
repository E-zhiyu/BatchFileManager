"""连接.jar文件的模块"""
import json
import subprocess


class JarConnector:
    """
    连接.jar文件的类
    :param target：需要运行的.jar文件
    :param sent_data：需要发送的参数（要能被JSON格式化）
    """

    def __init__(self, target: str, sent_data: (list, dict, set)):
        self.target = target  # 目标.jar文件路径
        self.sent_data = sent_data  # 需要发送的数据

        # 启动Java进程
        self.java_process = subprocess.Popen(
            ["java", '-jar', self.target],
            creationflags=subprocess.CREATE_NO_WINDOW,  # 关键参数，不显示窗口
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        self.__sendData()

    def __sendData(self):
        """通过标准输入向Java子进程发送数据"""
        # 将列表转换为JSON字符串并发送
        json_data = json.dumps(self.sent_data)
        self.java_process.stdin.write(json_data + '\n')  # 添加换行符作为结束标记
        self.java_process.stdin.flush()  # 确保数据被发送
        self.java_process.stdin.close()

    def receiveData(self):
        """从Java子进程读取标准输出中的数据"""
        json_data = self.java_process.stdout.readline()
        try:
            return json.loads(json_data)
        except json.decoder.JSONDecodeError:
            return None
