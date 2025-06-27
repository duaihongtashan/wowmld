#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/12/14 2:10
# @Author  : 肥鹅
# @file: TeamMember.py

# team member  英[tiːm ˈmembə(r)] 团队成员;小组成员;队员;组员;
#导入需要的库
import random
import time
from res.data.GameInfo import GAMEINFO
from res.com.ComControl import comControl
from res.game.Player import player
from res.utils.Helpers import helpers
from res.game.Control import control
from res.game.Monsters import monsters

class TeamMember(object):

    def run(self):

        # # 目标检测屏幕内所有怪物
        # health_lst = monsters.getAllMonster()
        #
        # if len(health_lst) == 0:
        #     # 当前屏幕没有怪物，无动作
        #     pass
        # else:
        #     # 屏幕内有怪物，进行攻击
        #     closest_point, distance, index = monsters.recentMst()
        #     if distance is not None:
        #         if distance <= 220:
        #             comControl.downKey("88")
        #             time.sleep(random.uniform(0.4, 1))
        #         else:
        #             comControl.downKey("99")
        #             time.sleep(random.uniform(0.4, 1))
        print("99")
        comControl.downKey("99")
        time.sleep(random.uniform(0.5,1.5))


teamMember = TeamMember()
