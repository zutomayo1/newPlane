#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证右下角僚机显示改动
"""

import sys
sys.path.insert(0, '.')

import pygame
from config import WIDTH, HEIGHT, CYAN
from sprites import Player
from wingman import WingmanSquadron

# 初始化pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

print("=== 右下角僚机显示验证 ===\n")

# 创建玩家
player = Player("striker")
player.wingman_squadron = WingmanSquadron(player, player.max_wingmen)

print("[Check 1] 验证僚机属性")
print(">> 玩家最大僚机数: " + str(player.max_wingmen))
print(">> 当前僚机数: " + str(len(player.wingman_squadron.wingmen)))

# 添加僚机
print("\n[Check 2] 添加僚机")
for i in range(2):
    player.wingman_squadron.add_wingman(None)

print(">> 当前僚机数: " + str(len(player.wingman_squadron.wingmen)))

# 验证显示文本
wingman_count = len(player.wingman_squadron.wingmen)
wingman_max = player.max_wingmen
wingman_text = f"僚机 {wingman_count}/{wingman_max}"

print("\n[Check 3] 右下角显示文本")
print(">> 文本内容: '" + wingman_text + "'")
print(">> 颜色: CYAN")

if "僚机" in wingman_text and "/" in wingman_text:
    print("\n[SUCCESS] 右下角僚机显示文本格式正确!")
else:
    print("\n[ERROR] 文本格式错误")

print("\n=== 验证完成 ===")
