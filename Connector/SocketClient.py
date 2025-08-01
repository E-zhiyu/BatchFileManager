import socket
import threading
import queue

from qfluentwidgets import TextBrowser, LineEdit


class SocketClient:
    def __init__(self, userCommandControl: LineEdit = None, outputControl: TextBrowser = None, host='localhost',
                 port=8080):
        """
        连接至Java子进程控制台的构造方法
        :param userCommandControl:用户输入命令的控件
        :param outputControl:待更新的GUI控件
        :param host:目标IP地址
        :param port:目标端口
        """
        self.userCommandControl = userCommandControl
        self.outputControl = outputControl
        self.host = host
        self.port = port
        self.command_queue = queue.Queue()
        self.running = True

    def setup_socket(self):
        """创建套接字并启动通信线程"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))

            # 启动接收线程
            self.receive_thread = threading.Thread(
                target=self.receive_messages,
                daemon=True
            )
            self.receive_thread.start()

            # 启动发送线程
            self.send_thread = threading.Thread(
                target=self.process_command_queue,
                daemon=True
            )
            self.send_thread.start()

            if self.outputControl:
                self.outputControl.append("【BFM】已连接到Java进程服务器")
            else:
                print("【BFM】已连接到Java进程服务器")
        except ConnectionRefusedError:
            if self.outputControl:
                self.outputControl.append("【BFM】错误: 无法连接到服务器")
            else:
                print("【BFM】错误: 无法连接到服务器")

    def send_command(self):
        """将命令放入队列(由发送线程处理)"""
        if self.userCommandControl:
            cmd = self.userCommandControl.text()
            self.outputControl.append(f">{cmd}")
            if cmd:
                self.command_queue.put(cmd)
                self.userCommandControl.setText('')  # 清空输入框的命令
        else:  # 仅用于调试
            cmd = input()
            self.command_queue.put(cmd)

    def process_command_queue(self):
        """发送线程: 处理命令队列"""
        while self.running:
            try:
                cmd = self.command_queue.get(timeout=0.1)
                self.sock.sendall((cmd + '\n').encode('utf-8'))
            except queue.Empty:
                continue
            except Exception as e:
                if self.outputControl:
                    self.outputControl.append(f"【BFM】发送错误: {str(e)}")
                else:
                    print(f"【BFM】发送错误: {str(e)}")
                break

    def receive_messages(self):
        """接收线程: 处理服务器消息"""
        while self.running:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if not data:
                    break
                # 更新GUI
                if self.outputControl:
                    self.outputControl.append(data.replace('\n', ''))
                else:
                    print(data)
            except ConnectionResetError:
                if self.outputControl:
                    self.outputControl.append('【BFM】服务器已关闭')
                else:
                    print("【BFM】服务器已关闭")
                break
            except Exception as e:
                if self.outputControl:
                    self.outputControl.append(f'【BFM】接收错误：{str(e)}')
                else:
                    print(f'【BFM】接收错误：{str(e)}')
                break

    def on_close(self):
        """关闭应用时的清理工作"""
        self.running = False
        if hasattr(self, 'sock'):
            self.sock.close()
