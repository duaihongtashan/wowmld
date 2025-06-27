#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/12/12 11:20
# @Author  : 肥鹅
# @file: Map.py

import cv2
import numpy as np
from res.data.LoadFile import loadFile
from res.utils.Helpers import helpers

class Map(object):

    def __init__(self):
        pass

    def matchKuang(self,map_min,left_top,template_path):
        """
        模板匹配小地图中矿物位置
        :param map_min:小地图
        :param left_top:当前小地图左上角位置
        :param template_path:矿物图标图片路径
        :return:矿物列表
        """
        k_lst = []
        template = cv2.imread(template_path)
        h, w = template.shape[:2]  # rows->h, cols->w
        # print('高：', h, "宽：", w)
        # 相关系数匹配方法：cv2.TM_CCOEFF
        if map_min is None or template is None:
            return k_lst
        res = cv2.matchTemplate(map_min, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.7  # 自定义阈值
        loc = np.where(res >= threshold)  # 匹配程度大于%80的坐标y,x
        for pt in zip(*loc[::-1]):  # *号表示可选参数
            right_bottom = (pt[0] + w, pt[1] + h)
            cv2.rectangle(map_min, pt, right_bottom, (0, 0, 255), 2)
            k_point_x = pt[0] + w / 2 + left_top[0]
            k_point_y = pt[1] + w / 2 + left_top[1]
            k_lst.append([k_point_x, k_point_y])

        return k_lst



    def preprocess_image(self,img):
        """
        图像增强
        :return:
        """
        if len(img.shape) == 3:  # 检查图像是否为三通道
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转换为灰度图像
        # 增强图像对比度
        enahanced_image = cv2.equalizeHist(img)
        # 对图像进行模糊
        blurred_image = cv2.GaussianBlur(enahanced_image, (5, 5), 0)
        # 对图像进行锐化
        sharpened_image = cv2.addWeighted(enahanced_image, 1.5, blurred_image, -0.5, 0)

        # cv2.imshow("aaa",sharpened_image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return sharpened_image

    def createMask(self,shape,center,radius,fill_color=255,line_type = -1):
        """
        创建圆形掩码
        :param shape: 图像形状
        :param center: 中心点
        :param radius: 半径
        :param fill_color:填充颜色
        :param line_type: 线条类型
        :return:numpy类型遮罩
        """
        mask = np.zeros(shape[:2], dtype=np.uint8)
        cv2.circle(mask,center,radius,fill_color,line_type)
        # cv2.imshow("bbb",mask)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return mask

    def extractCircle(self,image):
        """
        应用掩码遮罩，保留圆形地图
        :param image: 小地图图像
        :return:圆形地图图像
        """

        if len(image.shape) == 3:
            image = cv2.cvtColor(image,cv2.COLOR_BGR2BGRA)
        else:
            image = cv2.cvtColor(image,cv2.COLOR_GRAY2BGR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

        mask = self.createMask(image.shape[:2], (120, 117), 56)
        # 应用掩码到图像
        _, alpha = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)  # 将掩码转换为二值图像作为Alpha通道
        result = image.copy()
        result[:, :, :3] = cv2.bitwise_and(result[:, :, :3], result[:, :, :3], mask=mask)
        result[:, :, 3] = alpha  # 设置Alpha通道

        return result

map = Map()