#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/5/17 8:02
# @Author  : tom hanks
# @File    : ComControl.py
# @Description : 文档说明


import time
import serial
import ch9329Comm
import random

from res.data.GameInfo import GAMEINFO
from res.utils.WindowsApi import winapi

class ComControl():

    def __init__(self):
        super(ComControl, self).__init__()  # 重构run函数必须要写
        self.currentKey = ""  # 当前或者上一个按下的按键
        self.down_state = ""

    def initCom(self,comport,rate):
        """

        :param comport: com端口
        :param rate: 频率
        :return:
        """
        print("initCom 初始化串口")
        serial.ser = serial.Serial(comport, rate)  # 开启串口
        self.keyboard = ch9329Comm.keyboard.DataComm()

        # screen_w,screen_h = winapi.getScreenRect()

        self.mouse = ch9329Comm.mouse.DataComm(GAMEINFO.GAME_RESOLUTION['w'], GAMEINFO.GAME_RESOLUTION['h'])


    def mouseClickL(self,sleep_= 0.2):
        """
        鼠标左键
        :param sleep_: 操作后等待毫秒
        :return:
        """
        self.mouse.click()  # 单击左键
        time.sleep(sleep_)

    def mouseClickR(self,sleep_= 0.2):
        """
        鼠标右键
        :param sleep_: 操作后等待毫秒
        :return:
        """
        self.mouse.clickRight()  # 单击左键
        time.sleep(sleep_)

    def downKeyLonger(self,key):
        # if winapi.Foreground() == False:
        #     return
        if self.currentKey == key:
            return
        self.currentKey = key
        self.down_state = "longer"
        self.keyboard.send_data(key)  # 按下

    def downDouble(self,x_key = "",y_key = "",x_time = 0,y_time = 0):

        # if winapi.Foreground() == False:
        #     return

        self.keyboard.release()  # 松开

        if x_time >= y_time:
            #   第二个方向键按下前需要等待时长
            interval_time = x_time - y_time
            self.keyboard.send_data(x_key)  # 按下
            self.keyboard.release()  # 松开
            self.keyboard.send_data(x_key)  # 按下
            #   等待过后按下第二个方向键
            time.sleep(interval_time)
            print("按键：",x_key + y_key)
            self.keyboard.send_data(x_key + y_key)  # 按下
            #   等待按键结束
            time.sleep(y_time)
        else:
            #   第二个方向键按下前需要等待时长
            interval_time = y_time - x_time
            self.keyboard.send_data(y_key)  # 按下
            #   等待过后按下第二个方向键
            time.sleep(interval_time)
            self.keyboard.send_data(x_key)  # 按下
            self.keyboard.release()  # 松开
            self.keyboard.send_data(x_key)  # 按下
            self.keyboard.send_data(x_key + y_key)  # 按下
            #   等待按键结束
            time.sleep(x_time)

        self.keyboard.release()  # 松开

    # 按下按键
    def downKey(self,key,t = True):
        # if winapi.Foreground() == False:
        #     return
        self.currentKey = key
        self.down_state = "down"
        self.keyboard.send_data(key)  # 按下
        if t:
            # time.sleep(random.randrange(10,25) * 0.01)
            time.sleep(t)
        self.upKey(key)
    #   三连击
    def tripleHit(self):
        if winapi.Foreground() == False:
            return
        for i in range(3):
            self.keyboard.send_data("XX")  # 按下
            time.sleep(0.5)

    def upKey(self,key = "",t = 0):
        # if winapi.Foreground() == False:
        #     return

        # time.sleep(t)
        if self.currentKey == key:
            self.keyboard.release()  # 松开
            self.currentKey = ''
            self.down_state = ""
        if key == "":
            self.keyboard.release()  # 松开
            self.currentKey = ''
            self.down_state = ""

    def setKeyboard(self, keyboard):
        self.keyboard = keyboard  # serial的实例引用

    def getDownState(self):
        return self.down_state

    def release(self):
        self.keyboard.release()  # 松开


comControl = ComControl()