#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/12/12 11:19
# @Author  : 肥鹅
# @file: Player.py

import cv2
import numpy as np
import time
import logging
from res.YoloResult.PlayerAngle import getPlayerAngle,getWebPlayerAngle
from res.data.GameInfo import GAMEINFO
from res.utils.Helpers import helpers
from res.game.Interface import gameInterface
from res.game.Map import map

class Player(object):

    def __init__(self):

        # 2、创建SIFT算法
        self.sift = cv2.SIFT_create()
        # 4、创建特征匹配器
        self.flann = cv2.FlannBasedMatcher()

        self.action_completion = {
            "target": 0,  # 是否存在目标
            "pickup": GAMEINFO.PICKUP_STATE,
            "peel": GAMEINFO.PEEL_STATE,
            "time": 0,                # 当前选中目标的时间戳
            "sleep": 30,                        # 间隔为30秒
            "first": 2,                         # 是否为新目标，此值为目标monster_health_value，可以附加状态技能
            "remote_state":False,               # 是否进入攻击状态  False 不在攻击状态
            "back_state":False,                 # 是否需要去下一个坐标点 4次宏选择怪物后会变为True
            "GG":0,                             # 按下 G 键次数，（上一个敌人） 防止没有上一个敌人死循环
            "ask_state":"77",                   #状态攻击键
            "pet":2,                            # 1,2,3 宠物的3中攻击状态
        }

    def targetHp(self):
        """
        获取目标 0 死亡 1有目标 2空或其他情况
        :return:
        """
        health = gameInterface.getMonsterHpImg()
        t = helpers.extractText(health)
        logging.info(f"当前目标血量：{t}")
        if t == "死亡" or t.find("死") == 0:
            return 0

        if t == "":
            return 2

        # 怪物当前血量
        t_index = t.find("/")
        # 当前血量中第一个字符
        first_char = t[0]

        # 怪物当前血量大于0
        if first_char != "0" and t_index > 0:
            # 有血量数值
            return 1
        else:
            # 不为空 不为死亡 也不是正常数值情况
            return 2


    def Angle(self):
        """
        获取当前小地图中人物的角度
        :return:
        """
        min_map = gameInterface.getMinMapImg()
        if min_map is None:
            return None
        # 应用遮罩
        image_min = map.extractCircle(min_map)
        # 4通道转换为3通道RGB
        image_min = cv2.cvtColor(image_min,cv2.COLOR_BGRA2RGB)
        # yolo_obb模型预测 本地或者web
        if GAMEINFO.WEB_PREDICT['arrow'] == "":
            detections = getPlayerAngle(image_min)
        else:
            detections = getWebPlayerAngle(image_min)
            return detections[0]['angle_360']

        return detections['angle_360']


    def outdoorsAngle(self):
        """
        在野外 获取 人物角度 outdoors [ˌaʊtˈdɔːz]
        :return:
        """
        try:
            img = gameInterface.getAngleBox()
            name_txt = helpers.extractText(img)
            name_txt = float(name_txt)
        except Exception as e:
            return None
        return name_txt

    def LocText(self):
        """
        获取人物当前坐标
        :return:
        """
        p_img = gameInterface.getMapPointImg()
        try:
            # ocr文字识别
            t = helpers.extractText(p_img)
            # 以冒号分割字符串
            x,y = t.split(":")
            x = float(x) * 100
            y = float(y) * 100

        except Exception as e:
            logging.info(f"识别出现错误：{e}")
            return None
        return (x,y)

    def Loc(self,image_max_path = "res/map/maxmap_01.jpg"):
        try:
            image_min = gameInterface.getMinMapImg()
        except Exception as e:
            return None

        if image_min is None:
            return None
        try:
            # 1、加载图像
            image_max = cv2.imread(image_max_path)
            # 创建掩码
            image_min = map.extractCircle(image_min)
            # 图像增强
            image_max = map.preprocess_image(image_max)
            image_min = map.preprocess_image(image_min)

            # 3、检测图像中的关键点和描述子
            keypoint1, descriptors1 = self.sift.detectAndCompute(image_max, None)
            keypoint2, descriptors2 = self.sift.detectAndCompute(image_min, None)



            k = 2
            # 4、为每个描述符找到k个最佳匹配值
            matches = self.flann.knnMatch(descriptors1, descriptors2, k)

            # 5、遍历列表筛选最佳匹配结果
            good_matches = []
            for m, n in matches:
                if m.distance < 0.75 * n.distance:
                    good_matches.append(m)

            # 6、获取对应匹配点的位置
            points_lst1 = []
            points_lst2 = []
            for m in good_matches:
                query_idx = m.queryIdx
                keypoint = keypoint1[query_idx]
                point = keypoint.pt
                points_lst1.append(point)

                train_idx = m.trainIdx
                keypoint = keypoint2[train_idx]
                point = keypoint.pt
                points_lst2.append(point)

            np_points_lst1 = np.float32(points_lst1)

            point1 = np_points_lst1.reshape(-1, 1, 2)

            np_points_lst2 = np.float32(points_lst2)
            point2 = np_points_lst2.reshape(-1, 1, 2)

            # 计算变换矩阵
            M, mask = cv2.findHomography(point2, point1, cv2.RANSAC, 5)
            # height, width = image_max.shape[:2]
            # aligned_image = cv2.warpPerspective(image_min, M, (width, height))
            # result = cv2.addWeighted(image_max, 0.5, aligned_image, 0.5, 0)

            x = M[0, 2] + 120
            y = M[1, 2] + 118
            # print("人物在当前副本地图中的坐标：",x,y)
            return int(x), int(y)
        except Exception as e:
            logging.debug("获取人物位置遇到错误返回None ！---- Player class")
            return None

    def hpmp(self):
        """
        人物的hp和mp当前值
        :return:
        """
        hp_img = gameInterface.getPlayerHpImg()
        mp_img = gameInterface.getPlayerMpImg()
        hp = helpers.extractText(hp_img)
        mp = helpers.extractText(mp_img)

        #魔法值
        mp_percentage_value = 1
        hp_percentage_value = 1
        # 血量
        try:
            hps = hp[:-1]
            hp_percentage_value = float(hps) / 100

            mps = mp[:-1]
            mp_percentage_value = float(mps) / 100
        except Exception as e:
            logging.info(f"人物血量和魔法值获取错误：{e}")

        return hp_percentage_value,mp_percentage_value

    def drinkDrag(self):
        """
        喝药
        :return:
        """
        pass

    def isBuff(self):
        """
        匹配buff图标是否存在
        :param buff_path:buff图标图像路径
        :return:
        """
        im_opencv = gameInterface.getBuffRect()
        template = cv2.imread("res/img/buff_01.jpg")
        res = cv2.matchTemplate(im_opencv, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val > 0.75:
            logging.info(f"有buff图标，{max_val}")
            return True
        return False

    def askState(self):
        """
        头像位置战斗状态
        :return:
        """
        game_img = gameInterface.getGameBoxImg()
        if game_img is None:
            return None
        im_opencv = game_img[0:125, 0:125]  # 英[helθ] 健康++

        max_val, max_loc, rows, cols = helpers.matchTemplate("res/img/ask_state.jpg", im_opencv, 0.85)
        if max_val is not None:
            return True
        return False


player = Player()