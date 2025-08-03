# 批处理文件管理器

这是一款能够便捷管理本地批处理文件的应用

## 主要特性

- 集中管理批处理或命令脚本文件
- 为每个批处理或命令脚本文件添加备注
- 将控制台内容输出到图形化界面
- 通过图形化界面输入命令
- 强制结束正在运行的批处理或命令脚本文件

## 下载与使用

1. 安装OpenJDK 24（软件部分功能依靠.jar文件）
2. 从Release下载最新版软件压缩包并解压到任意位置
3. 运行解压得到的BatchFileManager.exe

## 构建项目

1. 克隆本仓库或直接下载源代码压缩包
2. 依次以Java_Backend\src\InterfaceFunction中的类为主类构建为同名.jar文件
3. 在源码根目录（即Main.py所在目录）新建backend文件夹，将构建好的.jar文件移动至该文件夹
4. 运行Main.py

## 使用到的其他开源项目

GUI界面：[QFluentWidgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)
