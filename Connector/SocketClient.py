import socket
import threading
import queue

from PyQt6.QtCore import pyqtSignal, QObject

from qfluentwidgets import TextBrowser, LineEdit, InfoBar, InfoBarPosition

from Logs.log_recorder import logging


class SocketClient(QObject):
    runningChanged = pyqtSignal(bool)

    def __init__(self, parent, userCommandControl: LineEdit, outputControl: TextBrowser, host='localhost', port=8080,
                 *args, **kwargs):
        """
        连接至Java子进程控制台的构造方法
        :param parent:创建实例的界面
        :param userCommandControl:用户输入命令的控件
        :param outputControl:控制台内容输出控件
        :param host:目标IP地址
        :param port:目标端口
        """
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.userCommandControl = userCommandControl
        self.outputTextBrowser = outputControl
        self.host = host
        self.port = port
        self.command_queue = queue.Queue()
        self.running = False
        self.autoScroll = True
        self.rcvTimeoutCount = 0  # 接收超时计数器

    def setup_socket(self):
        """创建套接字并启动通信线程"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(3.0)
        try:
            self.sock.connect((self.host, self.port))
            self.outputTextBrowser.insertPlainText("【BFM】已连接到Java文件运行进程\n")
            logging.info("【BFM】已连接到Java文件运行进程")
            self.running = True
            self.runningChanged.emit(True)
        except ConnectionRefusedError:
            self.outputTextBrowser.insertPlainText("【BFM】错误: 端口8080被占用，无法连接至服务器\n")
            logging.error('【BFM】错误: 端口8080被占用，无法连接至服务器')
            self.on_close()
        except socket.timeout:
            self.outputTextBrowser.insertPlainText('【BFM】错误：连接子进程超时\n')
            logging.warning('【BFM】错误：连接子进程超时')
            self.on_close()
        else:
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

    def send_command(self, custom_cmd: str = ''):
        """将命令放入队列(由发送线程处理)"""
        if not custom_cmd:
            cmd = self.userCommandControl.text()
            logging.info(f'用户输入命令：{cmd}')
        else:
            cmd = custom_cmd
            logging.info(f'尝试结束进程')

        if cmd and self.running:
            self.outputTextBrowser.insertPlainText(f">{cmd}\n")
            self.command_queue.put(cmd)
            self.userCommandControl.setText('')  # 清空输入框的命令

            if not custom_cmd:  # 只有获取的是命令输入框的内容才会显示消息条
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
                self.outputTextBrowser.insertPlainText('【BFM】发送超时\n')
                logging.warning('【BFM】发送超时')
            except Exception as e:
                self.outputTextBrowser.insertPlainText(f"【BFM】发送错误: {str(e)}\n")
                logging.error(f"【BFM】发送错误: {str(e)}")
                self.on_close()
                break

    def receive_messages(self):
        """接收线程: 处理服务器消息"""
        while self.running:
            try:
                data = self.sock.recv(1024).decode('utf-8')

                self.outputTextBrowser.insertPlainText(data)  # 更新GUI
                self.rcvTimeoutCount = 0  # 清空接收超时计数器

                # 滚动到底部
                if self.autoScroll:
                    cursor = self.outputTextBrowser.textCursor()
                    cursor.movePosition(cursor.MoveOperation.End)  # PyQt6 的枚举值
                    self.outputTextBrowser.setTextCursor(cursor)
                    self.outputTextBrowser.ensureCursorVisible()

                # 自动检测并关闭进程
                if not data:
                    self.on_close()
                    break
                elif data.startswith('#'):
                    logging.info(data.rstrip('\n'))
                    self.on_close()
                    break

                self.sock.settimeout(0)  # 成功接收则取消超时
            except ConnectionResetError:
                self.outputTextBrowser.insertPlainText('【BFM】Java文件运行服务已关闭\n')
                logging.info('【BFM】Java文件运行服务已关闭')
                self.on_close()
                break
            except socket.timeout:
                if self.rcvTimeoutCount <= 3:
                    self.rcvTimeoutCount += 1
                    self.outputTextBrowser.insertPlainText('【BFM】接收超时\n')
                    logging.warning('【BFM】接收超时')
                else:
                    self.outputTextBrowser.insertPlainText('【BFM】超时次数过多，文件运行进程已终止\n')
                    self.outputTextBrowser.insertPlainText(
                        '【BFM】提示：使用netstat -ano | findstr \"8080\"以查询端口占用情况\n')
                    logging.error('【BFM】超时次数过多，文件运行进程已终止，请检查8080端口占用情况')
                    self.on_close()
                    break
            except socket.error as e:
                if e.errno == 10035:  # 处理非阻塞错误
                    continue
            except Exception as e:
                self.outputTextBrowser.insertPlainText(f'【BFM】接收错误：{str(e)}\n')
                logging.error(f'【BFM】接收错误：{str(e)}')
                self.on_close()
                break

    def on_close(self):
        """关闭应用时的清理工作"""
        self.rcvTimeoutCount = 0  # 超时计数器归零
        self.running = False
        self.runningChanged.emit(self.running)
        if hasattr(self, 'sock'):
            self.sock.close()
