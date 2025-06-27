"""
**************************************
*  @Author  ：   肥鹅
*  @Time    ：   2025/2/23 15:10
*  @Project :   自动采矿完成版
*  @FileName:   Main.py
**************************************
"""


import sys
import serial.tools.list_ports
import multiprocessing  # 导入多进程模块
from res.WorkerProcess import WorkerProcess
from res.ui.main.mainwindow import Ui_Widget
from PyQt5.QtWidgets import QApplication, QMainWindow


class mywindow(QMainWindow, Ui_Widget):
    def  __init__ (self):
        super(mywindow, self).__init__()
        self.setupUi(self)

        # 按钮数量
        button_num = 3
        # 初始化多进程相关事件和列表
        self.processes = [None, None, None]  # 用来存储每个按钮的进程对象
        self.stop_events = [multiprocessing.Event() for _ in range(button_num)]  # 为每个按钮创建一个事件，用来控制进程停止

        # 开始脚本按钮
        self.start_buts = [self.startButton_0,self.startButton_1,self.startButton_2]
        self.startButton_0.clicked.connect(lambda: self.toggle_process(0))
        self.startButton_1.clicked.connect(lambda: self.toggle_process(1))
        self.startButton_2.clicked.connect(lambda: self.toggle_process(2))

        # 结束脚本按钮endButton_0
        self.end_buts = [self.endButton_0,self.endButton_1,self.endButton_2]
        self.endButton_0.clicked.connect(lambda: self.end_bt(0))
        self.endButton_1.clicked.connect(lambda: self.end_bt(1))
        self.endButton_2.clicked.connect(lambda: self.end_bt(2))

        # COM端口下拉列表
        options = self.get_com_ports()
        self.comboBoxs = [self.comboBox_0, self.comboBox_1, self.comboBox_2]
        for combo in self.comboBoxs:
            for option in options:
                combo.addItem(option.device)                                       # 添加相同的选项到每个组合框

        for combo in self.comboBoxs:
            combo.currentIndexChanged.connect(self.on_combobox_changed)     # 连接信号到槽函数


    def toggle_process(self, button_index):

        """ 切换进程的状态：启动或停止 """
        if self.processes[button_index] is None or not self.processes[button_index].is_alive():
            self.start_buts[button_index].setText("进行中")
            current_combo = self.comboBoxs[button_index]
            selected_text = current_combo.currentText()

            # 如果进程没有启动或已经停止，则启动新进程
            self.stop_events[button_index].clear()  # 清除停止事件，允许进程继续运行
            self.processes[button_index] = WorkerProcess(self.stop_events[button_index], button_index,selected_text)  # 创建新进程
            self.processes[button_index].start()  # 启动进程
            # 启动任务
            # self.processes[button_index].start_task()
            # self.labels[button_index].setText(f"Button {button_index+1} is running...")  # 更新标签显示
        # else:
        #     self.processes[button_index].stop_task()  # 停止任务
        #     # 如果进程正在运行，设置停止事件，停止进程
        #     self.stop_events[button_index].set()  # 设置事件，通知进程停止
        #     self.processes[button_index].join(timeout=1)  # 等待进程正常结束，最多等待1秒
        #     if self.processes[button_index].is_alive():
        #         self.processes[button_index].terminate()  # 如果进程未正常退出，强制终止
        #     self.processes[button_index] = None  # 清除进程对象
        #     self.start_buts[button_index].setText("进行中")
        #     # self.labels[button_index].setText(f"Button {button_index+1}")  # 更新标签显示


    def end_bt(self, button_index):
        self.processes[button_index].stop_task()  # 停止任务
        # 如果进程正在运行，设置停止事件，停止进程
        self.stop_events[button_index].set()  # 设置事件，通知进程停止
        self.processes[button_index].join(timeout=1)  # 等待进程正常结束，最多等待1秒
        if self.processes[button_index].is_alive():
            self.processes[button_index].terminate()  # 如果进程未正常退出，强制终止
        self.processes[button_index] = None  # 清除进程对象
        self.start_buts[button_index].setText("开始进行")

    def on_combobox_changed(self, index):
        # 这里我们需要确定是哪个combobox组合框触发了信号
        # 但是由于我们连接了相同的槽到多个组合框，我们需要另一种方法来识别它
        # 一种方法是在 lambda 表达式中传递额外的信息，但这里我们使用了 sender() 方法
        sender_combo = self.sender()
        selected_text = sender_combo.currentText()
        print(
            f"Selected in {sender_combo.objectName() if sender_combo.objectName() else 'unknown combo'}: {selected_text}")

    def get_com_ports(self):
        """
        获取系统中所有可用的COM端口。
        """
        com_ports = serial.tools.list_ports.comports()  # 获取所有COM端口
        return com_ports

if __name__ == '__main__':

    # 启动窗口
    app = QApplication(sys.argv)
    MainWindow = mywindow()
    MainWindow.show()
    sys.exit(app.exec_())


