"""
**************************************
*  @Author  ：   肥鹅
*  @Time    ：   2025/2/24 1:55
*  @Project :   自动采矿完成版
*  @FileName:   ActionLoop.py
**************************************
"""

import numpy as np
import time
import random
import threading
import logging
import pyautogui
from res.data.GameInfo import GAMEINFO
from res.game.Interface import gameInterface
from res.com.ComControl import comControl
from res.utils.Helpers import helpers
from res.data.LoadFile import loadFile
from res.game.Player import player
from res.game.Control import control
from res.game.Map import map
from res.YoloResult.PredictHealth import predictHealth
from res.com.WindMouse import moveMouse
from res.game.Monsters import monsters
from res.map.WalkInstance import walkinstance

# 配置基本的日志记录器
logging.basicConfig(level=logging.DEBUG,  # 设置日志级别
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 设置日志格式
                    datefmt='%Y-%m-%d %H:%M:%S')  # 设置日期格式



# 全局变量
COORDINATES = []  # 存储自动副本路径坐标
NEAREST_LST = []  # 与矿匹配的路径中最近的点
CURRENT_INDEX = None
CLOSE_LST = []      #已经经过的矿物
BACK_HOME = False   # False 未使用回城


class Mining:
    def __init__(self):
        """初始化采矿类，加载路径和矿物信息"""


        self.init()
        self.original_kuang_lst = loadFile.readKuangTxt()  # 读取原始矿物列表位置
        logging.info(f"加载路径完毕：{COORDINATES}")

    def init(self):
        global COORDINATES
        self.kuang_obj = loadFile.readPathFile()  # 读取副本路径坐标
        self.coordinates = loadFile.readFile()
        COORDINATES = self.coordinates


    def backHome(self):
        global BACK_HOME
        for i in range(5):
            comControl.keyboard.send_data("++", "L_SHIFT")
            logging.info("按下自动出副本宏！！！")
            time.sleep(random.uniform(0.3, 0.6))
            comControl.release()
            time.sleep(random.uniform(0.3, 0.6))
        BACK_HOME = True

        comControl.release()

    def restoreMagic(self):
        """
        回复魔法值，使用神圣恳求，（这里应该先判断蓝量，到达阈值才使用）
        :return:
        """
        im_opencv = gameInterface.getGameBoxImg()
        if im_opencv is None:
            return None

        max_val, max_loc, rows, cols = helpers.matchTemplate("res/img/skill_sskq.jpg", im_opencv, 0.9)
        if max_val is not None:
            comControl.downKey("QQ")
            comControl.release()


    def piPeiKuang(self, target):
        """
        匹配原始数组中的矿物位置
        :param target: 当前人物位置
        :return: 寻路路径
        """
        global NEAREST_LST,CLOSE_LST
        # 获取小地图左上角坐标
        left_top = [int(target[0] - 122), int(target[1] - 118)]
        # 获取小地图图像
        min_map_img = gameInterface.getMinMapImg()
        # 加载矿物匹配图像，返回矿物坐标列表
        k_lst = map.matchKuang(min_map_img, left_top, "res/img/kuang.png")

        for k_target in k_lst:
            # 找到最接近的矿坐标
            closest_point, min_distance, closest_index = helpers.find_nearest_point_and_index(self.original_kuang_lst, k_target)
            # 水里的矿特殊处理
            if closest_index == 10:
                print(f"当前矿坐标：{k_target} 在水里，所以跳出此次矿匹配")
                return

            logging.info(f"找到可挖掘矿石,序列：{closest_index},距离差：{min_distance},固定坐标值：{closest_point},当前矿坐标：{k_target}")

            for i in range(len(self.kuang_obj)):
                if self.kuang_obj[i]['id'] == closest_index:
                    if self.kuang_obj[i]['id'] not in CLOSE_LST:
                        print(f"当前矿物路径：{self.kuang_obj[i]['points']}")
                        self.kuang_obj[i]['bool'] = False
                        NEAREST_LST.append(self.kuang_obj[i])
                        CLOSE_LST.append(self.kuang_obj[i]['id'])
                        break


    def predictK(self):
        """预测矿物位置"""
        # comControl.downKey("PS") # 保存图像丰富目标检测
        img = gameInterface.getGameBoxImg()
        detections = predictHealth(img)

        if detections is None:
            time.sleep(0.2)
            return None

        for box in detections:
            # 有选中标记
            if box['class'] == "kuang":

                logging.info(f"识别到的矿物图像信息：{box}")
                x1, y1, x2, y2 = box['x1'], box['y1'], box['x2'], box['y2']
                x, y = x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2
                return [x, y]
        return None

    def switchPath(self,closest_point):
        """
        奇幻矿物路径
        :param closest_point: 矿物坐标
        :return:
        """
        global COORDINATES,CURRENT_INDEX,NEAREST_LST
        # 切换矿物路径
        for point in NEAREST_LST:
            # 矿物路线开头坐标与当前坐标
            # print(point['points'][0] , closest_point,COORDINATES)
            if point['points'][0][:2] == closest_point[:2] and point['bool'] == False:
                COORDINATES = point['points']
                CURRENT_INDEX = point['id']
                point['bool'] = True
                # COORDINATES[0][5] = 1
                return True
        return False

    def askMonster(self):
        # 延时判断屏幕内是否还有怪物血条
        const = 0

        while True:
            # 接口返回怪物数据
            detections = monsters.getAllMonster()
            if detections is None:
                time.sleep(0.2)
                continue
            # 屏幕中是否有标记符号
            sign_v = False
            # 屏幕中是否有血条
            health_v = False
            for item in detections:
                # 有选中标记
                if item['class'] == "sign":
                    sign_v = True
                    c_x = 1920 / 2
                    c_y = 1080 / 2
                    m_x = (item['x1'] + item['x2']) / 2
                    m_y = (item['y1'] + item['y2']) / 2
                    angle_biaoji = helpers.calculate_angle((c_x, c_y), (m_x, m_y))
                    direction, angle = helpers.rotation_direction(angle_biaoji, 90)
                    # print("当前标记所在角度：", angle_biaoji, "需要旋转的角度：", angle)
                    if angle >= 65:
                        t = 2 / 360 * angle
                        t = round(t, 2)
                        if direction == "顺时针":
                            comControl.downKey("AA", t)
                        else:
                            comControl.downKey("DD", t)
                    break

            if sign_v == False:
                correct_angle = False
                for item in detections:
                    if item['class'] == "health":
                        health_v = True
                        c_x = 1920 / 2
                        c_y = 1080 / 2
                        m_x = (item['x1'] + item['x2']) / 2
                        m_y = (item['y1'] + item['y2']) / 2
                        angle_deg = helpers.calculate_angle((c_x, c_y), (m_x, m_y))
                        if angle_deg < 150 and angle_deg > 30:
                            correct_angle = True
                # 人物前方没有一个怪物
                if correct_angle == False:
                    for item in detections:
                        if item['class'] == "health":
                            c_x = 1920 / 2
                            c_y = 1080 / 2
                            m_x = (item['x1'] + item['x2']) / 2
                            m_y = (item['y1'] + item['y2']) / 2
                            angle_deg = helpers.calculate_angle((c_x, c_y), (m_x, m_y))

                            direction, angle = helpers.rotation_direction(angle_deg, 90)
                            t = 2 / 360 * angle
                            t = round(t, 2)
                            if direction == "顺时针":
                                comControl.downKey("AA", t)
                            else:
                                comControl.downKey("DD", t)
                            break
                else:
                    print("按下TAB键")
                    # 前方有怪物，但是没有标记。则按下tab
                    comControl.downKey("TA")
                    time.sleep(random.uniform(0.3, 0.6))

            if health_v or sign_v:
                const = 0
                comControl.downKey("11")
                time.sleep(random.uniform(0.2, 0.4))
                continue
            else:
                const += 1
                if const > 3:
                    return
                else:
                    time.sleep(0.3)
                    continue

    def run(self):
        """主运行函数，控制采矿流程"""
        global COORDINATES,NEAREST_LST,CURRENT_INDEX,BACK_HOME

        logging.info(f"已到达副本内，开始自动副本 {gameInterface.getMapName().strip()}")
        while GAMEINFO.ACTION_LOOP:
            target = player.Loc()
            if not target:
                time.sleep(1)
                continue

            # 参数1：x   参数2：y  参数3：怪物类型    参数4：0无,1战斗,2嘲讽 3采矿  参数5：1旋转半周  参数6： 1已经经过此点,2已战斗过 3已采矿
            closest_point, distance, index = helpers.find_closest_point_and_index(COORDINATES, target)

            if index != -1:
                # 与战斗点距离小于8 开始战斗 直到屏幕内没有血条
                if COORDINATES[index - 1][3] == 1 and COORDINATES[index - 1][5] == 1:
                    comControl.release()
                    print("触发战斗：", "距离人物最近坐标点：", closest_point, " 人物坐标点：", target)
                    # 怪物的序列号，1 卫兵 2、控制者 3 预言者
                    m_index = COORDINATES[index - 1][2]
                    if m_index == 1:
                        # 按下选择对应怪物按键w
                        comControl.downKey("F4CC")

                    if COORDINATES[index - 1][4] == 1:
                        print("转身攻击身后目标")
                        comControl.downKey("DD", 1)
                        COORDINATES[index - 1][4] = 0

                    # 持续战斗 直到没有血条在屏幕内
                    self.askMonster()

                    COORDINATES[index - 1][3] = 0
                    COORDINATES[index - 1][5] = 2

                    continue



            # # 自动出副本
            if CURRENT_INDEX is None and BACK_HOME == False:
                if index >= 34:
                    self.backHome()

            if BACK_HOME == True:
                map_name = gameInterface.getMapName().strip()
                num = helpers.check_substring_char_count("萨瑟里斯海岸", map_name)
                if num >= 4:
                    logging.info("已经出副本，所以退出当前run函数")
                    return False

            if index == -1:
                if CURRENT_INDEX is None:
                    comControl.release()
                    logging.info("结束路径")
                    self.backHome()
                    break
                else:
                    # 只有一个坐标点的矿物处理
                    if COORDINATES[index][3] != 3:
                        pre_point = COORDINATES[-1]

                        COORDINATES = self.coordinates
                        # 遍历到指定索引之前的所有子列表
                        for i in range(len(COORDINATES)):
                            if COORDINATES[i][:2] == pre_point[:2]:
                                print("找到了当前再列表中的位置：",i,pre_point)
                                # COORDINATES[i][5] = 1

                                for i in range(i + 1):
                                    # 修改当前子列表中第五个元素的值
                                    COORDINATES[i][5] = 1


                        print("切换回默认路径：",COORDINATES)
                        CURRENT_INDEX = None
                        #这里需要遍历改变前面路径的已经过值：

                        continue





            if index > 0:
                l_index = index - 1


                # 与战斗点距离小于8 开始战斗 直到屏幕内没有血条
                if COORDINATES[l_index][3] == 1 and COORDINATES[l_index][5] == 1:
                    comControl.release()
                    print("触发战斗：", "距离人物最近坐标点：", closest_point, " 人物坐标点：", target)
                    # # 怪物的序列号，1 卫兵 2、控制者 3 预言者

                    # 持续战斗 直到没有血条在屏幕内
                    self.askMonster()
                    # # 拾取
                    # pickUp()
                    # 恢复状态
                    # restorePlayer()

                    COORDINATES[l_index][3] = 0
                    COORDINATES[l_index][5] = 2

            # 是否是采矿点：
            if COORDINATES[index - 1][3] == 3:
                comControl.release()

                # 记录开始时间
                start_time = time.time()
                # 等待怪物
                while True:

                    # 获取当前时间
                    current_time = time.time()
                    # 计算时间差
                    elapsed_time = current_time - start_time
                    # 检查是否达到了 30 秒
                    if elapsed_time >= 30:
                        break

                    v = player.askState()
                    if v:
                        self.askMonster()
                    else:
                        break

                # 目标检测矿
                const = 0
                while const < 5:
                    box = self.predictK()
                    if box:
                        moveMouse(box)
                        time.sleep(random.uniform(1.5, 1.7))
                        const += 1
                        continue
                    else:
                        if const == 1:
                            comControl.downKey("N8")  # 切换视角
                            time.sleep(random.uniform(1, 1.2))
                            const += 1
                            continue
                        comControl.downKey("DD", 0.6)
                        time.sleep(random.uniform(0.4, 0.6))

                    const += 1
                # 恢复顶部视角
                comControl.downKey("N7")

                comControl.release()

                COORDINATES[index - 1][3] = 0
                continue

            v = self.switchPath(COORDINATES[index - 1])
            if v:
                print("switchPath 函数返回 TRUE 这里continue")
                continue

            target_next = COORDINATES[index][:2]
            next_angle = helpers.calculate_angle(target, target_next)
            player_angle = player.Angle()

            if not player_angle:
                logging.debug(f"角度坐标获取失败 player_angle ：{player_angle}")
                continue

            logging.debug(f"人物坐标：{target}, 下一个坐标：{target_next}, 路径序列：{index}, 当前角度：{player_angle}, 目标角度：{next_angle}")
            control.moveAndRotate(player_angle, next_angle)


            self.piPeiKuang(target)

            self.restoreMagic()

    def xigou(self):
        global COORDINATES, NEAREST_LST, CURRENT_INDEX, BACK_HOME,CLOSE_LST
        COORDINATES = []  # 存储自动副本路径坐标
        NEAREST_LST = []  # 与矿匹配的路径中最近的点
        CURRENT_INDEX = None
        CLOSE_LST = []      #已经经过的矿物
        BACK_HOME = False   # False 未使用回城


def playerLocThread():
    """线程函数，监控玩家位置并更新路径状态"""
    global COORDINATES,CURRENT_INDEX

    while True:
        target = player.Loc()
        if not target:
            continue

        closest_point, min_distance, index = helpers.find_closest_point_and_index(COORDINATES, target)

        if index == -1:
            if CURRENT_INDEX is None:
                logging.info("playerLocThread 线程结束")
                break
            else:
                continue

        if min_distance < 4:
            logging.debug(f"更改index：{index}")
            COORDINATES[index][5] = 1


def main():

    walkinstance.run()

    # 进入副本
    img = gameInterface.getGameBoxImg()
    detections = predictHealth(img)

    time.sleep(random.uniform(0.4, 0.6))
    comControl.downKey("N8")

    for box in detections:
        # 有选中标记
        if box['class'] == "maradon":
            x1, y1, x2, y2 = box['x1'], box['y1'], box['x2'], box['y2']
            x, y = x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2
            moveMouse((x,y))

    const = 0
    while GAMEINFO.ACTION_LOOP :
        map_name = gameInterface.getMapName().strip()
        num = helpers.check_substring_char_count("地歌瀑布", map_name)
        if num <= 2:
            if const >= 15:
                logging.info("没有进入地歌瀑布,退出脚本")
                exit()
        else:
            break
        if gameInterface.getMapName().strip() == "地歌瀑布":
            break

        time.sleep(1)
        const += 1

    comControl.keyboard.send_data("11","L_CTRL")
    time.sleep(random.uniform(1.3, 1.5))
    comControl.keyboard.send_data("++", "L_CTRL")

    time.sleep(random.uniform(1.3, 1.5))
    comControl.downKey("QQ")

    time.sleep(random.uniform(1.3, 1.5))
    comControl.downKey("N7")

    # 启动线程
    thread = threading.Thread(target=playerLocThread)

    thread.start()

    mining.run()

    mining.xigou()

    walkinstance.xigou()

    time.sleep(2)
    while GAMEINFO.ACTION_LOOP:
        map_name = gameInterface.getMapName().strip()
        num = helpers.check_substring_char_count("萨瑟里斯海岸", map_name)
        if num >= 4:
            logging.info("开始新一轮采矿")
            break

    comControl.keyboard.send_data("99", "L_CTRL")

    mining.init()

mining = Mining()
# if __name__ == '__main__':
#
#     # 启动采矿主程序
#     mining = Mining()
#     main()


