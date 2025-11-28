#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试僚机是否能射击"""

import sys
sys.path.insert(0, r'c:\Users\真夜中\Desktop\newPlane')

from sprites import Player
from wingman import WingmanSquadron
from roguelite import create_wingman_weapon
from config import WIDTH, HEIGHT

# 创建玩家
print("创建玩家...")
player = Player("striker")

# 创建编队
print("创建编队...")
player.wingman_squadron = WingmanSquadron(player, max_wingmen=4)

# 创建武器并添加僚机
print("创建武器和僚机...")
for i in range(4):
    weapon = create_wingman_weapon(player)
    print(f"  武器{i}: {weapon}")
    print(f"    type: {weapon.type if hasattr(weapon, 'type') else 'N/A'}")
    print(f"    can_shoot: {weapon.can_shoot() if hasattr(weapon, 'can_shoot') else 'N/A'}")
    result = player.wingman_squadron.add_wingman(weapon)
    print(f"  添加结果: {result}")

# 显示编队信息
print(f"\n编队状态:")
print(f"  僚机数量: {len(player.wingman_squadron.wingmen)}")

# 显示每个僚机的信息
for i, wm in enumerate(player.wingman_squadron.wingmen):
    print(f"\n僚机{i}:")
    print(f"  weapon: {wm.weapon}")
    print(f"  weapon.type: {wm.weapon.type if wm.weapon else 'None'}")
    print(f"  weapon.can_shoot(): {wm.weapon.can_shoot() if wm.weapon else 'None'}")

print("\n测试完成！")
