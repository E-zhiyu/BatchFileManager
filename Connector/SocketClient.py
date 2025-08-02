import errno
import socket
import threading
import queue

from qfluentwidgets import TextBrowser, LineEdit, InfoBar, InfoBarPosition

from Logs.log_recorder import logging


class SocketClient:
    def __init__(self, parent, userCommandControl: LineEdit, outputControl: TextBrowser, host='localhost',
                 port=8080):
        """
        连接至Java子进程控制台的构造方法
        :param parent:创建实例的界面
        :param userCommandControl:用户输入命令的控件
        :param outputControl:待更新的GUI控件
        :param host:目标IP地址
        :param port:目标端口
        """
        self.parent = parent
        self.userCommandControl = userCommandControl
        self.outputControl = outputControl
        self.host = host
        self.port = port
        self.command_queue = queue.Queue()
        self.running = False

    def setup_socket(self):
        """创建套接字并启动通信线程"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(3.0)
        try:
            self.sock.connect((self.host, self.port))
            self.sock.settimeout(0)  # 成功连接则取消超时
            self.outputControl.append("【BFM】已连接到Java进程服务器")
            logging.info("【BFM】已连接到Java进程服务器")
            self.running = True
        except ConnectionRefusedError:
            self.outputControl.append("【BFM】错误: 无法连接到服务器")
            logging.error('【BFM】错误: 无法连接到服务器')
        except socket.timeout:
            self.outputControl.append('【BFM】错误：连接子进程超时')
            logging.warning('【BFM】错误：连接子进程超时')

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

    def send_command(self):
        """将命令放入队列(由发送线程处理)"""
        cmd = self.userCommandControl.text()
        if cmd and self.running:
            logging.info(f'用户输入命令：{cmd}')
            self.outputControl.append(f">{cmd}")
            self.command_queue.put(cmd)
            self.userCommandControl.setText('')  # 清空输入框的命令
            InfoBar.success(
                "成功",
                '命令已发送',
                duration=1500,
                position=InfoBarPosition.TOP,
                parent=self.parent.parentWindow
            )
        elif not self.running:
            InfoBar.error(
                "错误",
                '没有正在运行的文件',
                duration=1500,
                position=InfoBarPosition.TOP,
                parent=self.parent.parentWindow
            )
        elif not cmd:
            InfoBar.warning(
                "警告",
                '不能发送空命令',
                duration=1500,
                position=InfoBarPosition.TOP,
                parent=self.parent.parentWindow
            )

    def process_command_queue(self):
        """发送线程: 处理命令队列"""
        while self.running:
            try:
                cmd = self.command_queue.get(timeout=0.1)
                self.sock.sendall((cmd + '\n').encode('utf-8'))
            except queue.Empty:
                continue
            except socket.timeout:
                self.outputControl.append('【BFM】发送超时')
            except Exception as e:
                self.outputControl.append(f"【BFM】发送错误: {str(e)}")
                break

    def receive_messages(self):
        """接收线程: 处理服务器消息"""
        while self.running:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                self.outputControl.append(data.replace('\n', ''))
                if not data or data.startswith('#'):
                    self.on_close()
                    break
                # 更新GUI
            except ConnectionResetError:
                self.outputControl.append('【BFM】Java后端服务器已关闭')
                break
            except socket.timeout:
                self.outputControl.append('【BFM】接收超时')
            except socket.error as e:
                if e.errno == 10035:  # 处理非阻塞错误
                    continue
            except Exception as e:
                self.outputControl.append(f'【BFM】接收错误：{str(e)}')
                break

    def on_close(self):
        """关闭应用时的清理工作"""
        self.running = False
        if hasattr(self, 'sock'):
            self.sock.close()
