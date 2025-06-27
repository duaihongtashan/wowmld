#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/23 2:08
# @Author  : 肥鹅
# @file: WindMouse.py

import time,random,logging
import pyautogui
import numpy as np
from res.data.GameInfo import GAMEINFO
from res.com.ComControl import comControl



RECORD_POINT = []
sqrt3 = np.sqrt(3)
sqrt5 = np.sqrt(5)

def wind_mouse(start_x, start_y, dest_x, dest_y, G_0=9, W_0=3, M_0=15, D_0=12, move_mouse=lambda x,y: None):
    '''
    WindMouse algorithm. Calls the move_mouse kwarg with each new step.
    Released under the terms of the GPLv3 license.
    G_0 - magnitude of the gravitational fornce
    W_0 - magnitude of the wind force fluctuations
    M_0 - maximum step size (velocity clip threshold)
    D_0 - distance where wind behavior changes from random to damped
    '''
    current_x,current_y = start_x,start_y
    v_x = v_y = W_x = W_y = 0
    while (dist:=np.hypot(dest_x-start_x,dest_y-start_y)) >= 1:
        W_mag = min(W_0, dist)
        if dist >= D_0:
            W_x = W_x/sqrt3 + (2*np.random.random()-1)*W_mag/sqrt5
            W_y = W_y/sqrt3 + (2*np.random.random()-1)*W_mag/sqrt5
        else:
            W_x /= sqrt3
            W_y /= sqrt3
            if M_0 < 3:
                M_0 = np.random.random()*3 + 3
            else:
                M_0 /= sqrt5
        v_x += W_x + G_0*(dest_x-start_x)/dist
        v_y += W_y + G_0*(dest_y-start_y)/dist
        v_mag = np.hypot(v_x, v_y)
        if v_mag > M_0:
            v_clip = M_0/2 + np.random.random()*M_0/2
            v_x = (v_x/v_mag) * v_clip
            v_y = (v_y/v_mag) * v_clip
        start_x += v_x
        start_y += v_y
        move_x = int(np.round(start_x))
        move_y = int(np.round(start_y))
        if current_x != move_x or current_y != move_y:
            #This should wait for the mouse polling interval
            move_mouse(current_x:=move_x,current_y:=move_y)
    return current_x,current_y


def moveMouse(k):
    """
    鼠标移动到游戏内指定坐标位置
    :param k: 目的地坐标
    """
    global RECORD_POINT
    cur_x, cur_y = 0,0
    if len(RECORD_POINT) == 0:
        cur_x, cur_y = GAMEINFO.GAME_CENTER
        comControl.mouse.send_data_absolute(cur_x, cur_y)
        RECORD_POINT = GAMEINFO.GAME_CENTER
        logging.info(f"当前没有鼠标位置，将其移动到屏幕中间并记录：{cur_x}, {cur_y}")
    else:
        cur_x, cur_y = RECORD_POINT
    points = []

    left = k[0]
    top = k[1]
    wind_mouse(cur_x, cur_y, left, top, move_mouse=lambda x, y: points.append([x, y]))
    points = np.asarray(points)

    for p in points:
        time.sleep(random.uniform(0.005, 0.015))
        comControl.mouse.send_data_absolute(int(p[0]), int(p[1]))
    # comControl.mouse.send_data_absolute(int(k[0]), int(k[1]))
    logging.info(f"鼠标已经移动到屏幕绝对坐标：{int(left)}, {int(top)}")
    time.sleep(random.uniform(0.02, 0.04))
    comControl.downKey(";;")
    RECORD_POINT = [int(left), int(top)]