#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证僚机冷却时间已减半"""

import sys
sys.path.insert(0, r'c:\Users\真夜中\Desktop\newPlane')

from sprites import Player
from roguelite import create_wingman_weapon

# 创建玩家
player = Player("striker")
player.weapon_slots[player.current_slot] = {
    'type': 'cannon',
    'stars': 3,
    'name': '炮'
}

# 从系统导入 WeaponSystem 来初始化玩家武器
from systems import WeaponSystem
player.weapon_slots[player.current_slot] = WeaponSystem(player.weapon_slots[player.current_slot])

print("Player weapon info:")
pw = player.weapon_slots[player.current_slot]
print(f"  Type: {pw.type}")
print(f"  Max cooldown: {pw.cooldown_max}")

# 创建僚机武器
wingman_weapon = create_wingman_weapon(player)

print(f"\nWingman weapon info:")
print(f"  Type: {wingman_weapon.type}")
print(f"  Max cooldown: {wingman_weapon.cooldown_max}")

# 检查是否减半
if pw.cooldown_max > 0:
    expected_cooldown = max(1, pw.cooldown_max // 2)
    if wingman_weapon.cooldown_max == expected_cooldown:
        print(f"\nOK: Cooldown correctly halved: {pw.cooldown_max} -> {wingman_weapon.cooldown_max}")
    else:
        print(f"\nERROR: Cooldown not halved: {pw.cooldown_max} -> {wingman_weapon.cooldown_max} (expected: {expected_cooldown})")
else:
    print("\nCooldown is 0 or 1, cannot test halving")
