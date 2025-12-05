#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试生命再生卡牌效果"""

import sys
sys.path.insert(0, '.')
from roguelite import Card

# 测试生命再生
print("=== 生命再生卡牌效果 ===")
c1 = Card('regeneration', 'base')
print(f"Level 1: {c1.final_effect}")

c1.level = 2
c1.final_effect = c1._calculate_effect()
print(f"Level 2: {c1.final_effect}")

c1.level = 3
c1.final_effect = c1._calculate_effect()
print(f"Level 3: {c1.final_effect}")

# 计算每秒回复
FPS = 120
print("\n=== 每秒回复计算 (FPS=120) ===")
for level, effect in [(1, {'regen_rate': 5, 'regen_interval': 300}),
                      (2, {'regen_rate': 8, 'regen_interval': 300}),
                      (3, {'regen_rate': 8, 'regen_interval': 200})]:
    rate = effect['regen_rate']
    interval = effect['regen_interval']
    per_second = rate * (FPS / interval)
    print(f"Level {level}: {rate}点 / {interval}帧 = {per_second:.2f}点/秒")
