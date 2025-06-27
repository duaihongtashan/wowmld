#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/12/12 11:19
# @Author  : 肥鹅
# @file: Interface.py

import cv2
import numpy as np
from res.data.GameInfo import GAMEINFO
from res.utils.WindowsApi import winapi
from res.utils.Helpers import helpers


class Interface(object):

    def __init__(self):
        pass

    def init(self):
        # 查找魔兽世界标题的窗口
        hwnd = winapi.getTitleHwnd("魔兽世界")

        # 获取指定句柄窗口位置信息
        wow_rect = winapi.getWinRect(hwnd)

        self.left = wow_rect['left']       # + 10
        self.top = wow_rect['top']         # + 31
        self.right = wow_rect['right']
        self.bot = wow_rect['bot']

        GAMEINFO.GAME_INFO = {
            "left": self.left,
            "top": self.top,
            "right": self.right,
            "bottom": self.bot
        }

        GAMEINFO.GAME_HWDN = hwnd

    def getGameBoxImg(self):
        """
        获取游戏窗口图像
        :return:
        """
        im_opencv = winapi.getScreen()
        if im_opencv is None:
            return None
        game_img = im_opencv[self.top:self.bot,self.left:self.right]
        return game_img

    def getMonsterHpImg(self,v=False):
        """
        获取怪物血量图像
        :param v: 如果为True 则只截取前段颜色
        :return:
        """
        game_img = self.getGameBoxImg()
        if not v:
            health = game_img[39:65, 332:455]  # 英[helθ] 健康++
            # health = game_img[56:81, 454:523]  # 英[helθ] 健康++
        else:
            #血条颜色
            health = game_img[39:65, 332:345]  # 英[helθ] 健康++
            # health = game_img[56:81, 453:465]  # 英[helθ] 健康++

        return health

    def getMapPointImg(self):
        """
        获取界面中坐标图像
        :return:
        """
        game_img = self.getGameBoxImg()
        # 截取坐标插件的显示内容（根据移动位置需要调整）
        map_point = game_img[1040:1080, 0:200]
        return map_point

    def getPlayerHpImg(self):
        """
        获取 人物HP值图像
        :return:
        """
        game_img = self.getGameBoxImg()
        hp = game_img[40 :66, 123:  249]
        #同时显示状态下 百分比数值
        # hp = game_img[40:66, 115:  145]
        # hp = game_img[60:80, 156:  193]
        return hp


    def getPlayerMpImg(self):
        """
        获取 人物MP值图像
        :return:
        """
        game_img = self.getGameBoxImg()
        mp = game_img[68:84,  126: 246]
        #同时显示状态下 百分比数值
        # mp = game_img[68:87, 115:  145]
        # mp = game_img[86:102, 155:  190]
        return mp


    def getbackpackEmptyImg(self):
        """
        获取 背包剩余格数图像
        :return:
        """
        game_img = self.getGameBoxImg()
        empty = game_img[ 1035: 1080, 1555:  1595]
        return empty

    def getMinMapImg(self):
        """
        获取 小地图 图像
        :return:
        """
        game_img = self.getGameBoxImg()
        if game_img is None:
            return None
        minMap = game_img[ 0:226, 1689: 1920]
        return minMap

    def getRemote(self):
        """
        技能判断目标是否在射程内 判断快捷键6 技能状态颜色
        :return:
        """
        image = self.getGameBoxImg()[1032:1070, 592:630]

        # 确保图像是RGB格式（如果不是，则转换）
        if len(image.shape) == 2:  # 灰度图像
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:  # 包含透明度的RGBA图像
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

        # 计算每个颜色通道的平均值
        mean = np.mean(image[:, :, :])
        return mean

    def getBuffRect(self):
        """
        获取buff区域图像
        :return:
        """
        game_img = self.getGameBoxImg()
        buff_img = game_img[ 0:204, 1043: 1694]
        return buff_img


    def getMapName(self):
        """
        获取插件中地图名称
        :return:
        """
        game_img = self.getGameBoxImg()
        # map_name = game_img[ 6:27, 1713: 1903]
        # map_name = game_img[955:1015, 3: 174]
        map_name = game_img[878:938, 3: 174]

        name_lst = helpers.extractText(map_name,lst_b=True)
        # print(name_lst)
        if len(name_lst) > 1:
            name_txt = name_lst[1]['text']
        else:
            name_txt = name_lst[0]['text']
        return name_txt

    def getAngleBox(self):
        """
        获取插件中人物角度
        :return:
        """
        game_img = self.getGameBoxImg()
        if game_img is None:
            return None
        angle_img = game_img[955:1015, 3: 174]

        return angle_img


gameInterface = Interface()