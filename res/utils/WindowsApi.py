#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/10/25 1:25
# @Author  : 肥鹅
# @file: WindowsApi.py
import logging

#导入需要的库
import win32gui, win32ui, win32con
import cv2
import numpy
import logging

class WindowsApi():

    def __init__(self):
        self.HWND = 0
        # self.cap = cv2.VideoCapture(0)
        #
        # if not self.cap.isOpened():
        #     print("无法打开视频采集卡")
        #     exit()
        #
        # # 尝试设置帧宽度和高度（这些值应该根据你的设备进行调整）
        # frame_width = 1920
        # frame_height = 1080
        #
        # # 设置属性ID和对应的值
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
        #
        # # 可选：尝试设置帧率
        # # 注意：不是所有设备都支持设置帧率
        # fps = 60.0
        # self.cap.set(cv2.CAP_PROP_FPS, fps)

    def setVideoCapture(self, video_index):
        """
        设置获取哪个采集卡的内容
        :param video_index:
        :return:
        """
        self.cap = cv2.VideoCapture(video_index)
        if not self.cap.isOpened():
            print("无法打开视频采集卡")
            exit()
        # 尝试设置帧宽度和高度（这些值应该根据你的设备进行调整）
        frame_width = 1920
        frame_height = 1080
        # 设置属性ID和对应的值
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

        # 可选：尝试设置帧率
        # 注意：不是所有设备都支持设置帧率
        fps = 60.0
        self.cap.set(cv2.CAP_PROP_FPS, fps)

    def getTitleHwnd(self,win_title):
        #  GetDesktopWindow 获得代表整个屏幕的一个窗口（桌面窗口）句柄
        hd = win32gui.GetDesktopWindow()
        # 初始化一个空列表，用于存储桌面窗口的所有子窗口句柄
        hwndChildList = []
        #   EnumChildWindows 为指定的父窗口枚举子窗口
        win32gui.EnumChildWindows(hd, lambda hwnd, param: param.append(hwnd), hwndChildList)

        for hwnd in hwndChildList:
            #   GetWindowText 取得一个窗体的标题（caption）文字，或者一个控件的内容
            # print("句柄：", hwnd, "标题：", win32gui.GetWindowText(hwnd))
            title = win32gui.GetWindowText(hwnd)
            if title.find(win_title) == 0:
                print("句柄：：", hwnd, "标题：", win32gui.GetWindowText(hwnd))
                self.HWND = hwnd
                return hwnd

        print(f"没有找到对应标题的窗口{win_title}")
        return None

    def getWinRect(self,hwnd):
        # rect = win32gui.GetWindowRect(hwnd)
        # left, top, right, bot = rect
        # w = right - left
        # h = bot - top

        # return {
        #     "left":left,
        #     "top":top,
        #     "right":right,
        #     "bot":bot,
        #     "width":w,
        #     "height":h,
        # }

        return {
            "left":0,
            "top":0,
            "right":1920,
            "bot":1080,
            "width":1920,
            "height":1080,
        }

    def getScreen(self):

        ret, im_opencv = self.cap.read()

        return im_opencv


    def Foreground(self):
        """
        当前激活窗口是否为指定的窗口
        :return:
        """
        # 获取当前活动窗口句柄
        hwnd = win32gui.GetForegroundWindow()

        if hwnd != self.HWND:
            return False
        else:
            return True

winapi = WindowsApi()