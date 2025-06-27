"""自动寻路到副本门口
**************************************
*  @Author  ：   肥鹅
*  @Time    ：   2025/2/6 17:02
*  @Project :   自动采矿完成版
*  @FileName:   WalkInstance.py
**************************************
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/12/14 2:04
# @Author  : 肥鹅

#导入需要的库
import time,random
import logging
from operator import index

from res.com.ComControl import comControl
from res.data.GameInfo import GAMEINFO
from res.game.Player import player
from res.utils.Helpers import helpers
from res.game.Interface import gameInterface
from res.game.Control import control
from res.com.WindMouse import moveMouse



# 配置基本的日志记录器
logging.basicConfig(level=logging.INFO,  # 设置日志级别
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 设置日志格式
                    datefmt='%Y-%m-%d %H:%M:%S')  # 设置日期格式


class WalkInstance(object):

    def __init__(self):

        self.COORDINATES = []
        self.path_file = [{"path":"res/map/maladun/coords_01.txt","speed":28},{"path":"res/map/maladun/coords_02.txt","speed":2},{"path":"res/map/maladun/coords_03.txt","speed":2}]
        self.file_index = 0
        self.move_time = {
            "time":0.0,
            "point":0,
            "state":0,      # 0 为正序，1为倒序
        }
        self.open_door_time = 0.0
        self.door_num = 0


    def readPath(self):
        # 打开文件 'a.txt' 并按行读取

        path_file = self.path_file[self.file_index]
        with open(path_file['path'], 'r') as file:
            # 逐行读取文件内容
            for line in file:
                # 去除每行末尾的换行符，并将字符串转换为整数
                line_str = line.strip()
                if line_str == "":
                    continue
                line_lst = line_str.split(",")
                x = int(float(line_lst[0]))
                y = int(float(line_lst[1]))
                # 打印转换后的整数（或进行其他操作）
                self.COORDINATES.append([x,y,0,0,0,0])


    def chengQiBuff(self):
        """
        乘骑buff
        :return:
        """
        const = 0
        while const < 5:
            im_opencv = gameInterface.getBuffRect()
            max_val, max_loc, rows, cols = helpers.matchTemplate("res/img/qicheng_01.jpg", im_opencv, 0.8)
            if max_val is None:
                comControl.keyboard.send_data("88","L_CTRL")
                time.sleep(random.uniform(0.3, 0.5))
                comControl.release()
                time.sleep(2)
            else:
                return

    def aesToDes(self,original_list):
        """
        正序倒序转换
        :return:
        """

        # 步骤1: 倒序列表
        reversed_list = original_list[::-1]
        # 步骤2: 遍历倒序后的列表，修改第三位元素
        for sublist in reversed_list:
            # 使用三元运算符进行0和1的互换
            sublist[5] = 1 if sublist[5] == 0 else 0
        # 打印结果
        # print(reversed_list)
        return reversed_list


    def run(self):
        map_name = gameInterface.getMapName().strip()
        num = helpers.check_substring_char_count("萨瑟里斯海岸",map_name)
        if num < 4:
            print("没有在萨瑟里斯海岸，无法启动寻路到副本")
            return False

        comControl.downKey("N8")
        time.sleep(random.uniform(0.6, 0.9))
        comControl.keyboard.send_data("--","L_SHIFT")

        #移动鼠标
        self.mouseToDoor()

        self.readPath()
        self.chengQiBuff()
        while GAMEINFO.ACTION_LOOP:
            v = self.inSituAsk()
            if v >= 3:
                break

        return True

    def mouseToDoor(self):
        comControl.release()
        # 移动鼠标到门上
        time.sleep(random.uniform(0.3, 0.5))
        _x, _y = GAMEINFO.GAME_CENTER
        moveMouse((_x, _y - 150))
        time.sleep(random.uniform(0.3, 0.5))

        comControl.release()

    def inSituAsk(self):
        """

        :return:
        """
        # 当前人物位置
        target = player.LocText()
        # print("当前人物位置：",target)
        if target is None:
            logging.info("没有获取到当前人物位置，等待一秒钟 return")
            time.sleep(1)
            return 0

        # 获取人物距离最近的战斗点    ！！！！！注意  这里使用了读取的坐标列表，如果没有多余点，就可以。如果多余点比较多，就会造成有时会略过我们的战斗点
        closest_point, distance, index = helpers.find_closest_point_and_index(self.COORDINATES, target)

        if index != -1 and index != 0:
            if self.move_time['time'] == 0:
                self.move_time['time'] = time.time()
                self.move_time['point'] = target
            else:

                if time.time() - self.move_time['time'] > 5 and self.move_time['state'] == 0:
                    d = helpers.distanceTo(target, self.move_time['point'])
                    player_speed = self.path_file[self.file_index]['speed']
                    print(d, player_speed)
                    if d < player_speed:
                        print("人物移动卡住了！！！~~~~\n", "倒序路径\n", "记录时间后退3秒")
                        self.COORDINATES = self.aesToDes(self.COORDINATES)
                        self.move_time['state'] = 1

                    self.move_time['time'] = time.time()
                    self.move_time['point'] = target

                if time.time() - self.move_time['time'] > 3 and self.move_time['state'] == 1:
                    print("路径直接转为正序，继续行进。。！")
                    self.COORDINATES = self.aesToDes(self.COORDINATES)
                    self.move_time['time'] = time.time()
                    self.move_time['point'] = target
                    self.move_time['state'] = 0

        # 门口开门


        if ((self.file_index == 1 and self.move_time['state'] == 0 and index == -1) or
                (self.file_index == 2 and self.move_time['state'] == 0 and index == 155)):
            if self.door_num == 0:
                comControl.downKey(";;")
                self.open_door_time = time.time()
                self.door_num += 1
            elif time.time() - self.open_door_time > 3:
                comControl.downKey(";;")
                self.open_door_time = time.time()
                self.door_num += 1

            print("开门次数：",self.door_num)

        # print(f"与指定坐标({target})最接近的点是: {closest_point}，距离为: {distance}，在列表中的位置为: {index}")
        if index == -1:
            logging.info(f"寻路已经结束，当前人物坐标：{target}")
            comControl.release()
            if self.file_index == 0:
                player_angle = player.outdoorsAngle()
                control.rotateInPlace(player_angle,165)
                comControl.downKeyLonger("WW")
                while True:
                    map_name = gameInterface.getMapName()
                    if map_name == "玛拉顿":
                        comControl.release()
                        comControl.keyboard.send_data("88","L_CTRL")
                        self.file_index += 1
                        self.readPath()

                        return 0
            if self.file_index == 1:

                time.sleep(0.5)
                comControl.downKey(";;")
                time.sleep(0.5)
                self.file_index += 1
                self.readPath()
                return 0

            if self.file_index == 2:
                comControl.release()
                time.sleep(0.5)
                self.file_index += 1

                return self.file_index


        else:
            # 下一个路径点
            target_next = self.COORDINATES[index][:2]
            # 计算下一个坐标点在当前人物位置的哪个角度
            next_angle = helpers.calculate_angle(target, target_next)

            # 当前人物角度
            player_angle = player.outdoorsAngle()
            if player_angle == None:
                return 0

            # logging.info(f"下一个路径点：{target_next}, 人物当前坐标：{target} ,人物当前角度：{round(player_angle,2)} 需要转动角度：{round(next_angle,2)}")

            if player_angle is None:
                return 0
            else:
                # 前进中调整角度
                control.moveAndRotate(player_angle, next_angle)

            test_loc = self.COORDINATES[index]
           # 判断是否已经经过
            if test_loc[5] == 0:
                # 判断与最近的点的距离是否小于 阈值
                distance = helpers.distanceTo(target_next,target)
                v = self.path_file[self.file_index]['speed']
                if distance < v:
                    self.COORDINATES[index][5] = 1

                    # logging.info(f"达到停止移动，旋转角度")
                    # comControl.release()
                    # time.sleep(2)
        return 1


    def xigou(self):
        self.COORDINATES = []
        self.path_file = [{"path":"res/map/maladun/coords_01.txt","speed":28},{"path":"res/map/maladun/coords_02.txt","speed":2},{"path":"res/map/maladun/coords_03.txt","speed":2}]
        self.file_index = 0


walkinstance = WalkInstance()



# if __name__ == '__main__':
#     cap = Captain()
#     time.sleep(2)
#     logging.info("开始")
#
#     cap.readPath()
#     for i in range(800):
#
#         cap.inSituAsk()
#     comControl.release()