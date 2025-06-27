#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/12/11 17:10
# @Author  : 肥鹅
# @file: GameInfo.py

class GameInfo():

    def __init__(self):
        # 人物等级
        self.LEVEL = 0
        # 人物血量
        self.HP = 0
        # 人物蓝量
        self.MP = 0
        # 跟随队长 false不跟随队长，true跟随队长
        self.FOLLOW = False
        # 跟随队长攻击  false不跟随队长攻击
        self.FOLLOW_ASK = False
        # 拾取 1为不拾取
        self.PICKUP_STATE = 1
        # 剥皮 1为不剥皮，0为剥皮
        self.PEEL_STATE = 1
        # 鼠标选怪还是tab  False为tab
        self.SELECT_STATE = False
        # 截取方式  false为正方形截图，true为窗口截图
        self.SCREEN_STATE = False
        # 跟随攻击
        self.CHECK_GENSUI = False
        # 宏选怪
        self.CHECK_HONGXUANGUAI = False
        # 升级路线文件
        self.LEVEL_PATH = ""
        # 串口设备状态
        self.COM_STATE = False
        # 游戏窗口信息
        self.GAME_INFO = {"left":0,"top":0,"right":0,"bottom":0}
        # 游戏窗口句柄
        self.GAME_HWDN = 0
        # 游戏窗口分辨率
        self.GAME_RESOLUTION = {"w":1920,"h":1080}
        # 游戏窗口中心点
        self.GAME_CENTER = [960, 540]
        # 圆点，半径攻击记录位置
        self.YUANDIAN = [
            (3534.0000000000005, 7975.0),
            (3452.0000000000005, 7822.0),
            (3439.0, 7620.0),
            (3578.0, 7270.999999999999),
            (3688.0000000000005, 7117.0),
            (3761.9999999999995, 7005.0),
            (3839.0, 6948.0),
            (3902.0000000000005, 6992.0),
            (4067.0, 7039.0),
            (4223.0, 7211.0),
            (4056.0, 7331.999999999999),
            (3943.0, 7387.0),
            (3815.0, 7497.0),
            (3722.9999999999995, 7656.999999999999),
            (3632.0, 7905.0),

        ]
        # 圆点序列表
        self.YDIndex = 0
        # 攻击半径
        self.BANJING = 0
        # 目标检测WEB地址
        # 判断位置
        self.WEB_PREDICT = {"arrow":"","monsters":""}
        # 使用技能颜色判断人物是否可以使用远程技能
        self.REMOTE_STATE = False
        # 游戏循环
        self.ACTION_LOOP = True

GAMEINFO = GameInfo()