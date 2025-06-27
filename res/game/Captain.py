#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/12/14 2:04
# @Author  : 肥鹅
# @file: Captain.py

#导入需要的库
import cv2
import random
import time
import logging
from res.data.GameInfo import GAMEINFO
from res.com.ComControl import comControl
from res.game.Player import player
from res.utils.Helpers import helpers
from res.game.Control import control
from res.game.Monsters import monsters
from res.game.Interface import gameInterface

# 配置基本的日志记录器
logging.basicConfig(level=logging.DEBUG,  # 设置日志级别
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 设置日志格式
                    datefmt='%Y-%m-%d %H:%M:%S')  # 设置日期格式


class Captain(object):

    def __init__(self):
        self.pre_target_state = 2
        # 宏选怪按键排序记录
        self.hong_const = -1
        # 返回中心点状态 True为正在返回
        self.back_center = False


    def run(self):
        # 当前人物位置
        target = player.Loc()
        if target is None:
            time.sleep(1)
            return

        # 获取人物距离最近的路径点
        closest_point, distance, index = helpers.find_closest_point_and_index(GAMEINFO.LEVEL_PATH, target)
        if distance <= 18:
            closest_point[2] = 1
        # 列表已经到最后，结束线程
        if index == -1:
            comControl.release()
            time.sleep(1)
            for index, point in enumerate(GAMEINFO.LEVEL_PATH):
                GAMEINFO.LEVEL_PATH[index][2] = 0
            logging.info("结束路径")

        # 下一个路径点
        target_next = GAMEINFO.LEVEL_PATH[index][:2]
        # 计算下一个坐标点在当前人物位置的哪个角度
        next_angle = helpers.calculate_angle(target, target_next)
        # 当前人物角度
        player_angle = player.Angle()

        monster_health_value = player.targetHp()
        logging.info(" 怪物血量情况：", monster_health_value, " 0为死亡，2为无对象，1为有对象"," player.action_completion:", player.action_completion," 上一个目标状态：",self.pre_target_state)
        if monster_health_value == 1:

            if self.pre_target_state == 2:
                img = gameInterface.getMonsterHpImg(True)

                proportions = helpers.get_color_proportion(img)
                if proportions["red"] < 0.8 and proportions["yellow"] < 0.8:
                    player.action_completion['target'] = 0
                    self.pre_target_state == 2
                    comControl.downKey('ES')
                    time.sleep(random.uniform(1,2))
                    return

            # 有目标对象，选择攻击按键或方式
            closest_point, distance, index = monsters.recentMst()
            if distance is not None:
                if distance <= 180:
                    comControl.downKey("EE")
                    time.sleep(random.uniform(0.4, 1))
                else:
                    comControl.downKey("66")
                    time.sleep(random.uniform(0.4, 1))
            else:
                comControl.downKey("66")
                time.sleep(random.uniform(0.4, 1))
            # 找到目标更新状态
            player.action_completion['target'] = 1
            self.pre_target_state = monster_health_value
            return
        elif monster_health_value == 0:
            # 怪物为死亡状态
            if player.action_completion["pickup"] == 0:
                comControl.downKey("EE")
                time.sleep(random.uniform(1.5, 2.5))
                player.action_completion["pickup"] = 1
                return

            if player.action_completion["peel"] == 0:
                comControl.downKey("EE")
                time.sleep(random.uniform(1.8, 2.2))
                player.action_completion["peel"] = 1
                return

            if player.action_completion['target'] == 1 and player.action_completion["pickup"] == 1 and \
                    player.action_completion["peel"] == 1:
                comControl.downKey("ES")
                time.sleep(random.uniform(0.3, 0.5))
                return
        else:

            if player.action_completion['target'] == 0:

                # 目标检测屏幕内所有怪物
                health_lst = monsters.getAllMonster()

                if len(health_lst) == 0:
                    # 当前屏幕没有怪物，进行寻路
                    # 自动寻路
                    control.moveAndRotate(player_angle, next_angle)
                    return

                center = GAMEINFO.GAME_CENTER
                # 从怪物列表中找到离屏幕中心最近的怪物
                closest_point, distance, index = helpers.find_closest_point_and_index(health_lst, center)
                # 鼠标选择怪物
                if GAMEINFO.SELECT_STATE:
                    comControl.release()
                    control.moveMouse(health_lst[index][0], health_lst[index][1])
                    time.sleep(0.2)
                # 需要旋转的角度
                angle_v = helpers.calculate_angle(center, health_lst[index][:2])
                if abs(90 - angle_v) > 45:
                    # 计算当前人物角度到下一个坐标点需要旋转的角度和方向
                    direction, angle = helpers.rotation_direction(90, angle_v)
                    t = 2 / 360 * angle
                    t = round(t, 2)

                    if direction == "顺时针":
                        comControl.downKeyLonger("DD")
                        time.sleep(t)
                        comControl.release()
                        # comControl.downKey("TA")
                    else:
                        comControl.downKeyLonger("AA")
                        time.sleep(t)
                        comControl.release()
                        # comControl.downKey("TA")

                    # TAB 选择怪物  这里tab要旋转后才能进行选怪，而鼠标需要再旋转前选怪
                    if not GAMEINFO.SELECT_STATE:
                        comControl.release()
                        comControl.downKey("TA")
                        time.sleep(0.2)
                return

            else:
                if player.action_completion["pickup"] == 0:
                    comControl.downKey("GG")
                    time.sleep(random.uniform(0.4, 0.8))
                    return
                if player.action_completion["peel"] == 0:
                    comControl.downKey("GG")
                    time.sleep(random.uniform(0.4, 0.8))
                    return
                player.action_completion["pickup"] = GAMEINFO.PICKUP_STATE
                player.action_completion["peel"] = GAMEINFO.PEEL_STATE
                player.action_completion['target'] = 0
                self.pre_target_state = monster_health_value

    def inSituAsk(self):
        """
        原地定点半径刷怪
        :return:
        """
        # 当前人物位置
        target = player.Loc()
        if target is None:
            logging.info("没有获取到当前人物位置，等待一秒钟 return")
            time.sleep(1)
            return

        monster_health_value = player.targetHp()
        logging.info(f" 怪物血量情况：{monster_health_value} 0为死亡，2为无对象，1为有对象,player.action_completion:{player.action_completion} 上一个目标状态：{self.pre_target_state}")

        if monster_health_value != 2:
            if time.time() - player.action_completion['time'] > 40 and player.action_completion['time'] != 0:
                logging.info(f"当前时间超时,按下esc：{time.time()},{player.action_completion['time']}")
                comControl.downKey("ES")
                time.sleep(random.uniform(0.5,1))
                player.action_completion["pickup"] = 1
                player.action_completion["peel"] = 1
                player.action_completion['target'] = 0
                player.action_completion['time'] = time.time()
                self.hong_const += 1
                return

        # 当前已有目标
        if monster_health_value == 1:

            # 第一次选中怪物
            first = player.action_completion['first']
            if first == 2:
                player.action_completion['time'] = time.time()
                # 血条颜色
                img = gameInterface.getMonsterHpImg(True)
                # cv2.imshow("aa",img)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()
                # 非可战斗对象 按下ESC 并等待
                proportions = helpers.get_color_proportion(img)
                if proportions["red"] < 0.6 and proportions["yellow"] < 0.6:
                    player.action_completion['target'] = 0
                    time.sleep(random.uniform(0.1,0.2))
                    comControl.downKey('ES')
                    time.sleep(random.uniform(1, 2))
                    logging.info("当前选择对象不是可战斗对象，或已经被其他人选择。",proportions)
                    return

            # 快捷键技能状态颜色
            remote_v = gameInterface.getRemote()
            # 是否在攻击状态
            remote_state = player.action_completion['remote_state']
            logging.info(f"选中怪物，判断是否为可攻击,颜色差：{GAMEINFO.REMOTE_STATE - remote_v},可攻击状态：{remote_state}")
            if abs(GAMEINFO.REMOTE_STATE - remote_v) > 35 and remote_state == False:
                comControl.downKey("EE")
                time.sleep(random.uniform(0.4, 1))
                logging.info("按下E 交互键，去寻找怪物")
            else:
                # 停止E的交互，并更改攻击状态为可攻击
                if not remote_state:
                    comControl.downKey("EE")
                    comControl.downKey("SS", 0.1)
                    # comControl.downKey("SS",0.05)
                    player.action_completion['remote_state'] = True
                    ask_state = player.action_completion['ask_state']
                    comControl.downKey(ask_state)

                if random.randrange(0,15) == 9:
                    comControl.downKey("EE")
                    comControl.downKey("SS", 0.1)
                comControl.downKey("66")
                time.sleep(random.uniform(0.4, 1))

            # 找到目标更新状态
            player.action_completion['target'] = 1
            player.action_completion['first'] = monster_health_value
            return

        elif monster_health_value == 0:
            # 选中上一个敌人记录状态
            player.action_completion['GG'] = 0
            # 怪物为死亡状态
            if player.action_completion["pickup"] == 0:
                comControl.downKey("EE")
                time.sleep(random.uniform(1.5, 2.2))
                player.action_completion["pickup"] = 1
                return

            if player.action_completion["peel"] == 0:
                comControl.downKey("EE")
                time.sleep(random.uniform(3.5, 3.8))
                player.action_completion["peel"] = 1
                return

            if player.action_completion['target'] == 1 and player.action_completion["pickup"] == 1 and \
                    player.action_completion["peel"] == 1:
                comControl.downKey("ES")
                logging.info(" 拾取 剥皮完成 初始化player.action_completion ，并按下ESC键")
                time.sleep(random.uniform(0.3, 0.5))
                return

        else:
            logging.info(f"当前无目标：{player.action_completion}")
            # 没有上一个敌人 无限循环的处理
            if player.action_completion['GG'] > 4:
                player.action_completion["pickup"] = 1
                player.action_completion["peel"] = 1
                player.action_completion['GG'] = 0

            if player.action_completion['target'] == 0:

                # 目标检测屏幕内所有怪物
                health_lst = monsters.getAllMonster()

                # 人物持续返回中心点。到达后停止状态
                next_target = GAMEINFO.YUANDIAN[GAMEINFO.YDIndex]
                if self.back_center:
                    if helpers.distanceTo(target, next_target) < 20:
                        self.back_center = False
                        # 判断是否已经按过4个选怪宏，圆点index加1 移动到下一个挂机处
                        back_state = player.action_completion['back_state']

                        # 宠物攻击状态切换为 跟随攻击
                        if player.action_completion['pet'] == 3:
                            time.sleep(random.uniform(0.03, 0.06))
                            comControl.keyboard.send_data("99", "L_CTRL")
                            time.sleep(random.uniform(0.1, 0.2))
                            comControl.release()
                            time.sleep(random.uniform(0.8, 1.2))
                            player.action_completion['pet'] = 2

                        if back_state:
                            if player.action_completion['pet'] == 2:
                                time.sleep(random.uniform(0.03, 0.06))
                                comControl.keyboard.send_data("00","L_CTRL")
                                time.sleep(random.uniform(0.1, 0.2))
                                comControl.release()
                                time.sleep(random.uniform(0.8, 1.2))
                                player.action_completion['pet'] = 3

                            control.detectionIndex()
                            while True:
                                b = control.backCenter()
                                if b:
                                    player.action_completion['back_state'] = False

                                    # 宠物攻击状态切换为 跟随攻击
                                    if player.action_completion['pet'] == 3:
                                        time.sleep(random.uniform(0.03, 0.06))
                                        comControl.keyboard.send_data("99", "L_CTRL")
                                        time.sleep(random.uniform(0.1, 0.2))
                                        comControl.release()
                                        time.sleep(random.uniform(0.03, 0.06))
                                        player.action_completion['pet'] = 2

                                    break

                    else:
                        if player.action_completion['pet'] == 2:
                            time.sleep(random.uniform(0.03, 0.06))
                            comControl.keyboard.send_data("00","L_CTRL")
                            time.sleep(random.uniform(0.1, 0.2))
                            comControl.release()
                            time.sleep(random.uniform(0.03,0.06))
                            player.action_completion['pet'] = 3
                        # 计算下一个坐标点在当前人物位置的哪个角度
                        next_angle = helpers.calculate_angle(target, next_target)
                        # 当前人物角度
                        player_angle = player.Angle()
                        control.moveAndRotate(player_angle, next_angle)
                    return

                if len(health_lst) == 0:
                    # 当前屏幕内没有怪物，判断与圆点距离
                    distance = helpers.distanceTo(target, next_target)
                    if distance >= GAMEINFO.BANJING:
                        # 计算下一个坐标点在当前人物位置的哪个角度
                        next_angle = helpers.calculate_angle(target, next_target)
                        # 当前人物角度
                        player_angle = player.Angle()
                        control.moveAndRotate(player_angle, next_angle)
                        self.back_center = True
                        return
                    else:
                        # 宏选怪
                        if self.hong_const == 1:
                            comControl.keyboard.send_data("11", "L_SHIFT")
                            time.sleep(0.1)

                        if self.hong_const == 2:
                            comControl.keyboard.send_data("22", "L_SHIFT")
                            time.sleep(0.1)

                        if self.hong_const == 3:
                            comControl.keyboard.send_data("33", "L_SHIFT")
                            time.sleep(0.1)

                        if self.hong_const == 4:
                            comControl.keyboard.send_data("44", "L_SHIFT")
                            time.sleep(0.1)
                            player.action_completion['back_state'] = True

                        # 按下宏选怪没有找到怪物，则换下一个。
                        monster_health_value = player.targetHp()
                        if monster_health_value != 1:
                            self.hong_const += 1

                        if self.hong_const > 4:
                            self.hong_const = 1
                            # 回到当前圆点
                            logging.info("当前地点怪物已经刷完，返回定点位置。")
                            self.back_center = True
                        return


                center = GAMEINFO.GAME_CENTER
                # 从怪物列表中找到离屏幕中心最近的怪物
                closest_point, distance, index = helpers.find_closest_point_and_index(health_lst, center)
                # 鼠标选择怪物
                if GAMEINFO.SELECT_STATE:
                    comControl.release()
                    control.moveMouse(health_lst[index][0], health_lst[index][1])
                    # 没有选择到怪物，则不旋转，直接返回
                    v = player.targetHp()
                    if v != 1:
                        return

                return

            else:
                if player.action_completion["pickup"] == 0:
                    comControl.downKey("GG")
                    time.sleep(random.uniform(0.4, 0.8))
                    player.action_completion['GG'] += 1
                    return
                if player.action_completion["peel"] == 0:
                    comControl.downKey("GG")
                    time.sleep(random.uniform(0.4, 0.8))
                    player.action_completion['GG'] += 1
                    return
                player.action_completion["pickup"] = GAMEINFO.PICKUP_STATE
                player.action_completion["peel"] = GAMEINFO.PEEL_STATE
                player.action_completion['target'] = 0
                player.action_completion['first'] = monster_health_value
                player.action_completion['remote_state'] = False
                player.action_completion['GG'] = 0
                # player.action_completion['time'] = 0
                logging.info("当前怪物操作完毕，初始化数据")

                comControl.downKey("++")
                time.sleep(random.uniform(0.4, 0.8))

                # 判断当前血量和魔法值。是否需要休息
                hp,mp = player.hpmp()

                if mp < 0.35:
                    comControl.downKey("--")
                    t = time.time()
                    while True:
                        hp, mp = player.hpmp()
                        if mp > 0.9:
                            break
                        # 喝水不能大于15秒 以防其他情况造成人物死亡
                        if time.time() - t > 15:
                            break

                if hp <= 0.4:
                    comControl.downKey("22")
                    t = time.time()
                    while True:
                        hp, mp = player.hpmp()
                        if hp > 0.9:
                            break
                        # 喝水不能大于15秒 以防其他情况造成人物死亡
                        if time.time() - t > 15:
                            break

                if hp <= 0.4 and mp < 0.35:
                    comControl.downKey("++--")
                    t = time.time()
                    while True:
                        hp, mp = player.hpmp()
                        if hp > 0.9 and mp > 0.9:
                            break
                        # 喝水不能大于15秒 以防其他情况造成人物死亡
                        if time.time() - t > 15:
                            break

                #判断buff状态，是否重新添加
                b = player.isBuff()
                if not b:
                    comControl.release()
                    time.sleep(random.uniform(0.4, 0.8))
                    comControl.downKey("33")
                    time.sleep(random.uniform(0.4, 0.8))

captain = Captain()