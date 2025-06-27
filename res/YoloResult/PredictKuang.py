"""
**************************************
*  @Author  ：   肥鹅
*  @Time    ：   2025/1/31 22:42
*  @Project :   自动采矿完成版
*  @FileName:   PredictKuang.py
**************************************
"""



import cv2
import numpy as np
from ultralytics import YOLO



class PredictKuang:

    def __init__(self):

        # 加载YOLOv8模型
        self.model = YOLO('res/data/weights/best.pt')  # 替换为你的模型路径

# 定义类别标签（根据模型训练时使用的标签进行更新）
# CLASS_LABELS = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light']

    def predict(self,img):

        # 进行目标检测
        results = self.model(img)

        # 提取检测结果
        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                detections.append({
                    "class": int(box.cls),
                    "confidence": float(box.conf),
                    "x1": float(x1),
                    "y1": float(y1),
                    "x2": float(x2),
                    "y2": float(y2)
                })

        return  detections

predictKuang = PredictKuang()