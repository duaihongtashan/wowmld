#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/11/19 22:12
# @Author  : 肥鹅
# @file: PlayerAngle.py



import cv2
import numpy as np
import math
import pickle
import requests
from ultralytics import YOLO
from res.data.GameInfo import GAMEINFO

model = None
def initArrowPt():
    """
    初始化检测模型
    :return:
    """
    global model
    # 加载YOLOv8模型
    model = YOLO('ultralytics/weights/arrow/best.pt')  # 替换为你的模型路径


def determine_position_and_angle(xA, yA, xB, yB):
    # 判断位置
    if xB < xA and yB < yA:
        position = "左上"
    elif xB > xA and yB < yA:
        position = "右上"
    elif xB < xA and yB > yA:
        position = "左下"
    elif xB > xA and yB > yA:
        position = "右下"
    else:
        position = "点B在点A的垂直或水平线上"

    # 计算角度（以度为单位）
    dx = xB - xA
    dy = yB - yA
    angle = math.degrees(math.atan2(dy, dx))  # atan2返回的是弧度，需要转换为度

    # 调整角度到0-360度范围内（如果需要的话）
    if angle < 0:
        angle += 360

    return position, angle

def getPlayerAngle(img):
    # 进行目标检测
    results = model(img)

    # 提取检测结果
    detections = []
    # 遍历每个检测结果
    x_center1 = 0
    x_center2 = 0
    y_center1 = 0
    y_center2 = 0
    angle_deg = 0
    angle_360 = 0
    direction = ""
    for r in results:

        obb_results = r.obb.xywhr.cpu().numpy()

        for i in range(len(obb_results)):
            obb_box_name = r.names[r.obb.cls.cpu().tolist()[i]]

            result = obb_results[i]
            x_center, y_center, width, height, angle_rad = result

            if obb_box_name == "arrow":
                x_center1 = x_center
                y_center1 = y_center
                # 弧度转角度
                angle_deg = np.degrees(angle_rad.item())

            if obb_box_name == "head":
                x_center2 = x_center
                y_center2 = y_center

        position, angle = determine_position_and_angle(x_center1, y_center1, x_center2, y_center2)

        angle_360 = abs(angle - 360)
        # print(f"点B在点A的{position}，角度为{angle}度, {angle_360}")

    # detections.append({'angle_deg': angle_deg, "direction":direction,"angle_360":angle_360})
    return {'angle_deg': angle_deg,"angle_360":angle_360}



def getWebPlayerAngle(img):
    """
     向服务器发送图像，并接收目标检测结果
     :param img: cv2图像
     :return:
     """
    detections = {'angle_deg': 0,"angle_360":0}
    # 将OpenCV图像编码为JPEG
    _, img_encoded = cv2.imencode('.jpg', img)
    image_bytes = img_encoded.tobytes()

    # 发送POST请求
    url = GAMEINFO.WEB_PREDICT['arrow']
    files = {'image': ('image.jpg', image_bytes, 'image/jpeg')}
    response = requests.post(url, files=files)
    # print("用时：", time.time() - t)

    # 打印检测结果

    if response.status_code == 200:
        detections = response.json()['detections']
        # print(f"Detections: {detections}")
        if len(detections) > 0:
            for item in detections:
                # print("item:",item)
                item['angle_360'] = item['angle_360']

    return detections


initArrowPt()
