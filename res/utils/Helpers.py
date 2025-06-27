#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/10/14 18:04
# @Author  : 肥鹅
# @file: Helpers.py
import math
import os
import cv2
import numpy as np
from ocr.TextOCR import textOCR

"""
Helpers         工具类
find_xml_files: 遍历指定文件夹下指定文件
screenShot:     截取指定位置大小图像
imgIsText:      提取指定区域图像中文字，并对比是否包含参数文字
matchTemplate:  opencv模板匹配
"""
class Helpers():

    def find_xml_files(self,directory,filetype = ".xml"):
        """
        遍历指定文件夹下指定文件
        :param directory:文件夹目录
        :param filetype:文件类型
        :return: 返回指定后缀文件列表，不好含后缀名
        """
        xml_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(filetype):
                    # 获取文件名（不包含文件后缀）并保存在列表中
                    filename = os.path.splitext(file)[0]
                    xml_files.append(filename)
        return xml_files

    def screenShot(self,screen,loc):
        """
        截取指定位置大小图像
        :param screen:原始图像
        :param loc:截取位置
        :return:
        """
        if len(loc) == 2:
            x1 = loc[0][0]
            y1 = loc[0][1]
            x2 = loc[1][0]
            y2 = loc[1][1]
            img = screen[y1:y2,x1:x2]
        return img

    def extractText(self,screen,dict_obj = None,lst_b = False):
        """
        提取图像中文字
        :param screen: 原始图像
        :param dict_obj: 文字区域坐标和文字，类型dict
        :return:识别结果
        """
        if dict_obj:
            loc = (dict_obj['left_top'],dict_obj['right_down'])
            img = self.screenShot(screen, loc)
        else:
            img = screen
        res = textOCR.bytesToText(img)
        if not lst_b:
            text = res[0]['text']
        else:
            text = res
        # print("识别文字：", text,res)
        return text

    def imgIsText(self,screen,dict_obj) -> bool:
        """
        提取指定区域图像中文字，并对比是否包含参数文字
        :param screen: 原始图像
        :param dict_obj: 文字区域坐标和文字，类型dict
        :return:识别结果
        """
        name = dict_obj['text']
        text = self.extractText(screen,dict_obj)
        if text.find(name) >= 0:
            return True
        return False


    def matchTemplate(self,img_path,im_opencv,acc = 0.75):
        """
        opencv模板匹配
        :param img_path:匹配图像路径
        :param im_opencv:被匹配图像
        :param acc:正确率
        :return: 匹配结果和匹配图像的宽高
        """
        # 查找裂缝图标
        template = cv2.imread(img_path)
        cols,rows = template.shape[:2]  # rows->w, cols->h
        # 使用模板匹配功能，在原始图像中找到要匹配的图像
        res = cv2.matchTemplate(im_opencv, template, cv2.TM_CCOEFF_NORMED)
        # 获取匹配结果中的最大值和最小值
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > acc:
            return max_val,max_loc,rows, cols

        return None,None,None,None

    def distanceTo(self,p1,p2):
        """
        计算两点之间的距离
        :param p1: 目标坐标
        :param p2: 目的地坐标
        :return:距离
        """
        # print("distanceTo: ",p1,p2)
        try:
            d = math.sqrt(pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2))
        except Exception as e:
            return 0
        return d


    def calculate_angle(self,A, B):
        """
        计算平面坐标系中点B相对于点A的角度（0到360度之间）。
        参数:
        A -- 点A的坐标，格式为(x1, y1)
        B -- 点B的坐标，格式为(x2, y2)

        返回:点B相对于点A的角度（度数）
        """
        x1, y1 = A
        x2, y2 = B

        # 计算两点之间的dx和dy
        dx = x2 - x1
        dy = y2 - y1

        # 使用atan2计算角度（返回的是弧度值）   图片坐标零点为左上角，所以这里需要处理y值为负数
        angle_rad = math.atan2(-dy, dx)

        # 将弧度转换为度数
        angle_deg = math.degrees(angle_rad)

        # 将角度转换为0到360度之间
        if angle_deg < 0:
            angle_deg += 360

        return angle_deg


    def rotation_direction(self,start_angle, end_angle):
        """
        计算当前角度到指定角度 顺时针或者逆时针 哪个方向更近
        :param start_angle: 人物当前角度值
        :param end_angle: 目标角度值
        :return: 最优解的转向和需要转动的角度
        """

        clockwise = (end_angle - start_angle) % 360
        counterclockwise = (start_angle - end_angle) % 360

        # 确定最小旋转方向
        if clockwise <= counterclockwise:
            return '逆时针', clockwise
        else:
            return '顺时针', counterclockwise


    def find_closest_point_and_index(self,coordinates, target):
        """
        从未经过的坐标数组中找出与指定坐标最接近的未经过的点
        参数:
        coordinates -- 坐标数组，格式为[(x1, y1), (x2, y2), ...]
        target -- 指定坐标，格式为(xt, yt)

        返回:
        一个元组，包含最接近的点的坐标、对应的距离和在列表中的位置
        """
        # 初始化最小距离、最接近的点及其在列表中的位置
        min_distance = float('inf')
        closest_point = None
        closest_index = -1

        # 遍历坐标数组，计算每个点与指定坐标的距离
        for index, point in enumerate(coordinates):
            # v:是否已经经过此坐标，只寻找没有走过的坐标。 1：已经过 0：未经过
            x, y, s_str, _,_,v = point
            if v == 1:
                continue
            distance = math.sqrt((x - target[0]) ** 2 + (y - target[1]) ** 2)

            # 如果当前距离小于最小距离，则更新最小距离、最接近的点及其在列表中的位置
            min_distance = distance
            closest_point = point
            closest_index = index
            break

        return closest_point, min_distance, closest_index

    def find_nearest_point_and_index(self,coordinates, target):
        """
        从坐标数组中找出与指定坐标最接近的点的坐标。 不分是否已经经过的点
        参数:
        coordinates -- 坐标数组，格式为[(x1, y1), (x2, y2), ...]
        target -- 矿的坐标，格式为(xt, yt)

        返回:
        一个元组，包含最接近的点的坐标、对应的距离和在列表中的位置
        """
        # 初始化最小距离、最接近的点及其在列表中的位置
        min_distance = float('inf')
        closest_point = None
        closest_index = -1

        # 遍历坐标数组，计算每个点与指定坐标的距离
        for index, point in enumerate(coordinates):
            # v:是否已经经过此坐标，只寻找没有走过的坐标。 1：已经过 0：未经过
            x, y, s_str, _,_,v = point

            distance = math.sqrt((x - target[0]) ** 2 + (y - target[1]) ** 2)

            # 如果当前距离小于最小距离，则更新最小距离、最接近的点及其在列表中的位置
            if distance < min_distance:
                min_distance = distance
                closest_point = point
                closest_index = index


        return closest_point, min_distance, closest_index

    def get_color_proportion(self,image):

        # 转换到HSV颜色空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # cv2.imshow("aaa", hsv)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # 定义颜色范围（HSV）
        black_lower = np.array([0, 0, 0])
        black_upper = np.array([180, 255, 50])

        gray_lower = np.array([0, 0, 0])
        gray_upper = np.array([180, 255, 255])  # 需要根据具体情况调整范围

        white_lower = np.array([0, 0, 200])
        white_upper = np.array([180, 255, 255])

        red_lower = np.array([0, 120, 70])
        red_upper = np.array([10, 255, 255])

        orange_lower = np.array([10, 120, 70])
        orange_upper = np.array([25, 255, 255])

        yellow_lower = np.array([25, 120, 70])
        yellow_upper = np.array([35, 255, 255])

        green_lower = np.array([35, 40, 40])
        green_upper = np.array([85, 255, 255])

        cyan_lower = np.array([85, 40, 40])
        cyan_upper = np.array([140, 255, 255])

        blue_lower = np.array([140, 40, 40])
        blue_upper = np.array([180, 255, 255])

        purple_lower = np.array([120, 150, 70])
        purple_upper = np.array([140, 255, 255])

        # 初始化颜色掩码 黑、灰、白、红、橙、黄、绿、青、蓝、紫
        masks = {
            "black": cv2.inRange(hsv, black_lower, black_upper),
            "gray": cv2.inRange(hsv, gray_lower, gray_upper),
            "white": cv2.inRange(hsv, white_lower, white_upper),
            "red": cv2.inRange(hsv, red_lower, red_upper),
            "orange": cv2.inRange(hsv, orange_lower, orange_upper),
            "yellow": cv2.inRange(hsv, yellow_lower, yellow_upper),
            "green": cv2.inRange(hsv, green_lower, green_upper),
            "cyan": cv2.inRange(hsv, cyan_lower, cyan_upper),
            "blue": cv2.inRange(hsv, blue_lower, blue_upper),
            "purple": cv2.inRange(hsv, purple_lower, purple_upper)
        }

        # 计算每种颜色的像素比例
        total_pixels = image.shape[0] * image.shape[1]
        color_proportions = {}
        for color, mask in masks.items():
            color_pixels = cv2.countNonZero(mask)
            color_proportions[color] = color_pixels / total_pixels

        return color_proportions


    def check_substring_char_count(self,main_string, sub_string):
        """
        判断主字符串中包含子字符串的字符数是否超过主字符串长度的一半。

        参数:
        main_string (str): 主字符串
        sub_string (str): 子字符串

        返回:
        bool: 如果包含子字符串的字符数超过主字符串长度的一半，则返回True；否则返回False。
        """
        # 计算主字符串和子字符串的长度
        main_len = len(main_string)
        sub_len = len(sub_string)

        # 如果子字符串为空，则直接返回False（因为空字符串不包含任何字符）
        if sub_len == 0:
            return False

        # 初始化计数器
        count = 0

        # 遍历主字符串，统计包含子字符串中字符的数量
        for char in main_string:
            if char in sub_string:
                count += 1

        # 判断是否超过一半
        return count

helpers = Helpers()