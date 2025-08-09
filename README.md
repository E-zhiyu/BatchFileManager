# 批处理文件管理器

这是一款能够便捷管理本地批处理文件的应用

## 效果展示

<img width="1388" height="1037" alt="PixPin_2025-08-05_12-47-27" src="https://github.com/user-attachments/assets/3c7546c0-de30-4dc9-9f61-04cc73704081" />
<img width="1388" height="1037" alt="PixPin_2025-08-05_12-50-22" src="https://github.com/user-attachments/assets/c2c25c4e-bab2-4b37-a453-0fd43176a8a1" />


## 主要特性

- 集中管理批处理或命令脚本文件
- 为每个批处理或命令脚本文件添加备注
- 将控制台内容输出到图形化界面
- 通过图形化界面输入命令
- 强制结束正在运行的批处理或命令脚本文件

## 下载与使用

1. 下载OpenJDK 24
2. 从Release下载最新版软件压缩包
3. （可选）将OpenJDK 24（或更新的版本）的安装路径添加至环境变量
4. 解压下载的软件压缩包，运行解压得到的BatchFileManager.exe
5. 在软件的设置界面将Java路径设置为OpenJDK 24的安装路径（如果没有设置环境变量）

## 构建项目

1. 克隆本仓库或直接下载源代码压缩包
2. 安装OpenJDK 24或更新的版本
3. 依次以Java_Backend\src\InterfaceFunction中的类为主类构建为同名.jar文件
4. 在源码根目录（即Main.py所在目录）新建backend文件夹，将构建好的.jar文件移动至该文件夹
5. 运行Main.py

## 使用到的其他开源项目

GUI界面：[QFluentWidgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)
