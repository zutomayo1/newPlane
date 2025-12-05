#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试线性弹道卡牌效果"""

class MockPlayer:
    def __init__(self):
        self.bullet_count = 1
        self.damage = 10

def apply_effect(player, effect):
    """模拟卡牌效果应用"""
    if "bullet_count" in effect:
        player.bullet_count = getattr(player, "bullet_count", 1) + effect["bullet_count"]
    if "damage_mult" in effect:
        player.damage *= (1.0 + effect["damage_mult"])

# 测试1: 初始1发子弹的机体
print("=== 初始1发子弹机体 ===")
player1 = MockPlayer()
print(f"初始: 子弹={player1.bullet_count}, 伤害={player1.damage}")

effect_lv1 = {'bullet_count': 1, 'damage_mult': 0.0, 'speed_mult': 0.0}
apply_effect(player1, effect_lv1)
print(f"Level 1线性弹道: 子弹={player1.bullet_count}, 伤害={player1.damage}")

# 测试2: Level 2
player2 = MockPlayer()
effect_lv2 = {'bullet_count': 2, 'damage_mult': 0.0, 'speed_mult': 0.0}
apply_effect(player2, effect_lv2)
print(f"Level 2线性弹道: 子弹={player2.bullet_count}, 伤害={player2.damage}")

# 测试3: Level 3
player3 = MockPlayer()
effect_lv3 = {'bullet_count': 2, 'damage_mult': 0.3, 'speed_mult': 0.0}
apply_effect(player3, effect_lv3)
print(f"Level 3线性弹道: 子弹={player3.bullet_count}, 伤害={player3.damage}")

# 测试4: 初始3发子弹的机体
print("\n=== 初始3发子弹机体 ===")
class MockPlayer3:
    def __init__(self):
        self.bullet_count = 3
        self.damage = 10

player4 = MockPlayer3()
print(f"初始: 子弹={player4.bullet_count}, 伤害={player4.damage}")
apply_effect(player4, effect_lv1)
print(f"Level 1线性弹道: 子弹={player4.bullet_count}, 伤害={player4.damage}")

player5 = MockPlayer3()
apply_effect(player5, effect_lv3)
print(f"Level 3线性弹道: 子弹={player5.bullet_count}, 伤害={player5.damage}")
