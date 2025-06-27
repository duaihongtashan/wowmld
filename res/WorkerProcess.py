"""
**************************************
*  @Author  ：   肥鹅
*  @Time    ：   2025/2/23 15:56
*  @Project :   自动采矿完成版
*  @FileName:   WorkerProcess.py
**************************************
"""

import sys
import time
import multiprocessing  # 导入多进程模块
from res.ActionLoop import main, mining
from res.com.ComControl import comControl
from res.game.Interface import gameInterface
from res.utils.WindowsApi import winapi
from res.data.GameInfo import GAMEINFO

# WorkerProcess 代码示例
class WorkerProcess(multiprocessing.Process):
    def __init__(self, stop_event, button_index,COM):
        super().__init__()
        self.running = False  # 任务是否正在运行的标志
        self.stop_event = stop_event
        self.button_index = button_index
        self.ready_event = multiprocessing.Event()  # 用于同步，确保任务启动

        self.COM = COM

    def run(self):
        print(f"进程 {self.button_index} 启动，")
        self.start_task()
        # 等待start_task触发
        self.ready_event.wait()  # 等待ready_event信号，确保start_task已经准备好
        print(f"当前连接端口号：{self.COM} button_index: {self.button_index}")
        comControl.initCom(self.COM, 115200)  # 初始化串口通信
        gameInterface.init()  # 初始化游戏接口
        winapi.setVideoCapture(self.button_index)

        # 这里只是做一些后台任务，不能直接创建界面
        while not self.stop_event.is_set():
            # print("aaa",self.running)
            if self.running:
                print("bbb")
                main()

        print(f"脚本 {self.button_index} 号停止.")
        comControl.release()

    def start_task(self):
        # 设置任务正在运行的状态
        self.running = True
        self.ready_event.set()  # 发出信号，表示进程可以开始工作
        print(f"进程 {self.button_index} 的任务已开始")
        GAMEINFO.ACTION_LOOP = True

    def stop_task(self):
        # 设置任务停止运行的状态
        self.running = False
        print("任务已停止")
        GAMEINFO.ACTION_LOOP = False
