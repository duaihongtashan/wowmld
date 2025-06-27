#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/11/19 21:53
# @Author  : 肥鹅
# @file: PredictHealth.py

import cv2
import time
import requests
from res.data.GameInfo import GAMEINFO
from ultralytics import YOLO

model = None
def initMonstersPt():
    """
    初始化怪物目标检测模型  模型为 血条 标记 矿
    :return:
    """
    global model
    model = YOLO("ultralytics/weights/monsters/best.pt")

def predictHealth(img):

    lst = ['health','sign','kuang','maradon']

    # 进行目标检测
    results = model(img)

    # 提取检测结果
    detections = []
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            detections.append({
                "class": lst[int(box.cls)],
                "confidence": float(box.conf),#相似度
                "x1": float(x1),
                "y1": float(y1),
                "x2": float(x2),
                "y2": float(y2),
            })

    return detections

def predictWebHealth(img):
    # 将OpenCV图像编码为JPEG
    _, img_encoded = cv2.imencode('.jpg', img)
    image_bytes = img_encoded.tobytes()

    # 发送POST请求
    url = GAMEINFO.WEB_PREDICT['monsters']
    files = {'image': ('image.jpg', image_bytes, 'image/jpeg')}
    response = requests.post(url, files=files)
    # print("用时：", time.time() - t)

    # 打印检测结果
    if response.status_code == 200:
        detections = response.json()['detections']
        # print(f"Detections: {detections}")
        return detections

initMonstersPt()