#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/12/12 11:18
# @Author  : 肥鹅
# @file: Monsters.py

from res.utils.Helpers import helpers
from res.data.GameInfo import GAMEINFO
from res.YoloResult.PredictHealth import predictHealth,predictWebHealth
from res.game.Interface import gameInterface

class Monsters(object):

    def getAllMonster(self):
        """
        目标检测屏幕内所有怪物
        :return: 目标检测结果 包含 【x,y,离屏幕中心距离】
        """
        game_img = gameInterface.getGameBoxImg()
        if GAMEINFO.WEB_PREDICT['monsters'] == "":
            healths = predictHealth(game_img)
        else:
            healths = predictWebHealth(game_img)
        # print("目标检测结果：", healths)
        # if healths is None:
        #     return None
        # resolution_w = GAMEINFO.GAME_RESOLUTION['w']
        # resolution_h = GAMEINFO.GAME_RESOLUTION['h']
        # screen_target = [resolution_w / 2, resolution_h / 2]
        # health_lst = []
        # for index, v in enumerate(healths):
        #     if v['class'] == "health":
        #         x = (v['x1'] + v['x2']) / 2
        #         y = (v['y1'] + v['y2']) / 2
        #         distance = helpers.distanceTo(screen_target, [x, y])
        #         health_lst.append([x, y, distance])

        return healths

    def recentMst(self):
        """
        距离最近的怪物
        :return:
        """

        # 目标检测屏幕内所有怪物
        health_lst = self.getAllMonster()

        if len(health_lst) == 0:
            return None,None,None

        center = GAMEINFO.GAME_CENTER
        # 从怪物列表中找到离屏幕中心最近的怪物
        closest_point, distance, index = helpers.find_closest_point_and_index(health_lst, center)

        return closest_point, distance, index

monsters = Monsters()