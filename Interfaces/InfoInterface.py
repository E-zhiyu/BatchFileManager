"""关于软件界面模块"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from qfluentwidgets import SubtitleLabel, BodyLabel, HyperlinkButton, setFont, PushButton, MessageBoxBase, TextBrowser
from qfluentwidgets import FluentIcon as FIF
from Interfaces import version

help_md = """\
### 文件操作

- 使用主页的“添加文件”按钮将你想要的文件添加至表格中（若出现“未知”字样，请检查Java版本）
- 文件表格支持多选，多选的按键逻辑与Windows文件资源管理器一致
- 点击“删除文件”按钮即可将选中文件从表格中移除，支持多选
- 点击“打开文件夹”按钮可以打开文件所在位置，支持同时打开多个文件夹
- 单选状态下点击“运行文件”按钮可以运行选中的文件，此时文件的运行细节将会输出到“控制台”界面，用户也可通过该界面输入命令

### 编辑单元格

- 目前只有备注栏支持用户修改，其他栏目内容由程序自动生成
- 用户可以通过双击单元格以及选中单元格后按下F2的方法进入编辑状态
- 编辑完成后点击表格其他位置或者按下回车键，编辑的内容将自动保存

### 文件失效

- 软件启动时将逐一判断已添加的文件是否存在，若文件被删除或移动至其他位置则会在“备注”栏提示用户文件已失效
- 尝试运行失效文件时将会再次检测文件是否存在，若文件存在则能够成功运行并消除失效标记
- 失效的文件仍能尝试打开所在目录，除非该文件的目录也不存在
- 软件不会自动移除失效的文件，便于用户排查文件失效的原因

### 文件运行

- 一次只能同时运行一个文件，且文件运行时会占用端口号1918，请确保该端口号没有被其他应用占用
- 在主页选中文件并点击“运行文件”按钮后，“控制台”界面将监听文件运行的输出内容
- 用户可以在“控制台”界面上方的输入框中输入命令，按下回车或者旁边的发送按钮发送命令
- 如果想要强制结束运行中的文件，可以按下输入框旁的“结束进程”按钮，或者发送“#kill#”命令（除非迫不得已，否则不推荐使用这种方法）
- 文件运行结束或者进程被杀死将会显示退出代码，0为正常退出
- 文件运行时的输出内容最多保存1000行，且在下次运行文件时自动清空
"""

updateLog_md = """\
# v1.1.0

## 新增内容

- 右键菜单增加重定向选项，能够在不删除原有文件条目的情况下替换为新的文件条目
- 主页运行文件和删除文件添加快捷键，可在对应按钮的工具提示中查看（鼠标悬停在上方1.5s后会弹出）
- 现在可以点击主页表头进行排序

## 优化内容

- 软件启动后会自动更新文件修改日期和文件大小

## 修复BUG

= 修复Java版本不对时添加文件导致崩溃的BUG


# v1.0.2

## 新增内容

- 设置界面新增配置Java路径选项，以便在没有设置环境变量的情况下使用软件

## 更改内容

- 文件表格右键编辑备注由弹出对话框改为启用单元格编辑功能
- 将运行文件的通信端口由8080修改为1918


# v1.0.1

## 更改内容

- 运行文件之前会弹出对话框确认操作
- 现在只有备注栏可以双击鼠标或按下F2编辑其中内容

## 优化内容

- 现在端口号被占用会终止文件的运行
- 文件运行时退出会弹出对话框进行确认
- 文件运行时会在窗口标题提示文件正在运行
- 将控制台输出控件由富文本输入框更换为普通文本输入框以优化性能
- 通过增加接收缓冲队列，即使需要高频输出控制台内容也不会导致程序崩溃


# v1.0.0

## 基本功能

- 集中管理批处理或命令脚本文件
- 为每个批处理或命令脚本文件添加备注
- 将控制台内容输出到图形化界面
- 通过图形化界面输入命令
- 强制结束正在运行的批处理或命令脚本文件
"""


class TextMessageBox(MessageBoxBase):
    """显示MarkDown文本的对话框类"""

    def __init__(self, title: str, md: str, parent=None):
        """
        :param md: 需要显示的文本
        :param parent: 需要遮罩的窗口（推荐设置为主窗口）
        """
        super().__init__(parent)
        self.widget.setMinimumWidth(550)  # 设置最小窗口宽度
        self.widget.setFixedHeight(500)  # 设置固定窗口高度
        self.cancelButton.hide()  # 隐藏取消按钮
        self.yesButton.setText('确定')

        titleLabel = SubtitleLabel(title)
        self.viewLayout.addWidget(titleLabel)

        txtBrowser = TextBrowser(self)
        txtBrowser.setMarkdown(md)
        self.viewLayout.addWidget(txtBrowser)


class InfoInterface(QWidget):
    """关于软件界面类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parentWindow = parent
        self.setObjectName("InfoInterface")

        # 初始化布局管理器
        self.totalWidget = QWidget()
        self.widgetLayout = QVBoxLayout(self)
        self.widgetLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widgetLayout.setContentsMargins(0, 0, 20, 0)
        self.widgetLayout.addWidget(self.totalWidget)

        self.mainLayout = QVBoxLayout(self.totalWidget)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.setSpacing(5)

        # 初始化控件
        self.initControls()

    def initControls(self):
        """初始化控件"""

        # 标题标签
        titleLabel = SubtitleLabel('关于软件', self.totalWidget)
        self.mainLayout.addWidget(titleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        setFont(titleLabel, 25, QFont.Weight.Bold)

        # 版本号标签
        versionLabel = BodyLabel(f'版本：{version}', self.totalWidget)
        self.mainLayout.addWidget(versionLabel, 0, Qt.AlignmentFlag.AlignCenter)

        # 作者标签
        authorLabel = BodyLabel('作者：GitHub@E-zhiyu', self.totalWidget)
        self.mainLayout.addWidget(authorLabel, 0, Qt.AlignmentFlag.AlignCenter)

        # 查看源码按钮
        urlButton = HyperlinkButton(icon=FIF.LINK, url='https://github.com/E-zhiyu/BatchFileManager',
                                    text='查看源代码')
        self.mainLayout.addWidget(urlButton, 0, Qt.AlignmentFlag.AlignCenter)

        # 使用说明按钮
        helpButton = PushButton(icon=FIF.HELP, text="使用说明", parent=self)
        self.mainLayout.addWidget(helpButton, 0, Qt.AlignmentFlag.AlignCenter)
        helpButton.clicked.connect(self.showHelp)

        # 更新日志按钮
        logButton = PushButton(icon=FIF.UPDATE, text='更新日志', parent=self)
        self.mainLayout.addWidget(logButton, 0, Qt.AlignmentFlag.AlignCenter)
        logButton.clicked.connect(self.showUpdateLog)

    def showHelp(self):
        """弹出使用说明消息框"""
        w = TextMessageBox("使用说明", help_md, self.parentWindow)
        w.show()

    def showUpdateLog(self):
        """弹出更新日志消息框"""
        w = TextMessageBox("更新日志", updateLog_md, self.parentWindow)
        w.show()
