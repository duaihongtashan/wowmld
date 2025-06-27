#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/12/12 16:51
# @Author  : 肥鹅
# @file: Control.py

import pyautogui
import numpy as np
import time,random
import logging
from res.utils.Helpers import helpers
from res.data.GameInfo import GAMEINFO
from res.com.WindMouse import wind_mouse
from res.com.ComControl import comControl
from res.game.Player import player

class Control(object):

    def init(self):
        self.left, self.top, self.right, self.bottom = (GAMEINFO.GAME_INFO[key] for key in ['left', 'top', 'right', 'bottom'])

    def moveMouse(self,absolute_x, absolute_y):
        """
        鼠标移动
        :param absolute_x: 鼠标目的地x坐标
        :param absolute_y: 鼠标目的地y坐标
        :return:
        """
        cur_x, cur_y = pyautogui.position()
        logging.info(f"获取鼠标位置：{cur_x}, {cur_y},{absolute_x + self.left}, {absolute_y + self.top}")
        points = []
        wind_mouse(cur_x, cur_y, absolute_x + self.left, absolute_y + self.top,
                   move_mouse=lambda x, y: points.append([x, y]))
        points = np.asarray(points)

        for p in points:
            comControl.mouse.send_data_absolute(int(p[0]), int(p[1]))
        comControl.mouse.click()
        time.sleep(random.uniform(0.02, 0.04))

        return True

    def rotateInPlace(self,player_angle, next_angle):
        """
        原地旋转到对应角度
        :param player_angle: 人物当前角度值
        :param next_angle: 下一个坐标点在当前人物位置的方向
        :return:
        """
        # 计算当前人物角度到下一个坐标点需要旋转的角度和方向
        direction, angle = helpers.rotation_direction(player_angle, next_angle)
        # print(f"小地图人物角度：{angle_360},角度差值：{angle}, 下一个位置坐标：{target_next}")
        t = 2 / 360 * angle
        t = round(t, 2)
        # print("需要间隔的时间", t)
        if direction == "顺时针":
            comControl.downKey("DD", t)
        else:
            comControl.downKey("AA", t)

        time.sleep(random.uniform(0.01, 0.1))


    def moveAndRotate(self,player_angle,next_angle):
        """
        前进中调整角度
        :param player_angle: 人物当前角度值
        :param next_angle: 下一个坐标点在当前人物位置的方向
        :return:
        """

        if abs(player_angle - next_angle) > 15:
            # 计算当前人物角度到下一个坐标点需要旋转的角度和方向
            direction, angle = helpers.rotation_direction(player_angle, next_angle)
            t = 2 / 360 * angle
            t = round(t, 2)
            # 原地旋转
            # logging.info(f"角度旋转：{player_angle, next_angle} 需要旋转角度：{angle} 按下时间：{t}")
            if angle > 50:
                if direction == "顺时针":
                    comControl.downKey("DD", t)
                else:
                    comControl.downKey("AA", t)

                time.sleep(random.uniform(0.01, 0.1))
            else:
                # 前进中旋转
                if direction == "顺时针":
                    comControl.downKeyLonger("WWDD")
                    time.sleep(t)
                    comControl.downKeyLonger("WW")
                else:
                    comControl.downKeyLonger("WWAA")
                    time.sleep(t)
                    comControl.downKeyLonger("WW")
        else:
            # 添加随机跳跃
            # if random.randint(0, 20) == 9:
            #     comControl.downKeyLonger("WWSP")
            #     time.sleep(random.uniform(0.1, 0.2))
            comControl.downKeyLonger("WW")


    def detectionIndex(self):
        """
        定点打怪序列的增加和维护
        :return:
        """
        if len(GAMEINFO.YUANDIAN) == 0:
            return
        # 防止圆点index超出索引
        if GAMEINFO.YDIndex >= len(GAMEINFO.YUANDIAN) - 1:
            GAMEINFO.YDIndex = 0
        else:
            GAMEINFO.YDIndex += 1

    def backCenter(self):
        """
        返回中心点
        :return: False 没有到达位置  True到达目的地
        """
        # 当前人物位置
        target = player.Loc()
        # 当前圆点坐标
        next_target = GAMEINFO.YUANDIAN[GAMEINFO.YDIndex]

        if helpers.distanceTo(target, next_target) < 20:
            return True

        # 计算下一个坐标点在当前人物位置的哪个角度
        next_angle = helpers.calculate_angle(target, next_target)
        # 当前人物角度
        player_angle = player.Angle()
        self.moveAndRotate(player_angle, next_angle)

        return False


control = Control()