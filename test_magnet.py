#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试资源磁场卡牌效果"""

# 模拟升级计算
base_effect = {"magnet_range": 200, "xp_mult": 1.2}
upgrades = [
    {"level": 2, "effect": {"magnet_range": 100}, "desc": "范围 +100"},
    {"level": 3, "effect": {"xp_mult": 0.3}, "desc": "经验 +30%"}
]

print("=== 资源磁场升级效果计算 ===")
for level in [1, 2, 3]:
    effect = base_effect.copy()
    
    if level > 1:
        for upgrade in upgrades:
            if upgrade["level"] <= level:
                for key, value in upgrade["effect"].items():
                    if key in effect:
                        effect[key] += value  # 加法
                    else:
                        effect[key] = value
    
    print(f"Level {level}: {effect}")

# 模拟应用到玩家
print("\n=== 应用到玩家 ===")

class Player:
    def __init__(self):
        self.pickup_range = 100
        self.xp_multiplier = 1.0

# 测试1: 单张Level 1
p1 = Player()
effect1 = {"magnet_range": 200, "xp_mult": 1.2}
p1.pickup_range = max(p1.pickup_range, effect1["magnet_range"])
added_mult = effect1["xp_mult"] - 1.0 if effect1["xp_mult"] >= 1.0 else effect1["xp_mult"]
p1.xp_multiplier = p1.xp_multiplier + added_mult
print(f"1张Lv1: range={p1.pickup_range}, xp={p1.xp_multiplier}x")

# 测试2: 单张Level 3
p2 = Player()
effect3 = {"magnet_range": 300, "xp_mult": 1.5}
p2.pickup_range = max(p2.pickup_range, effect3["magnet_range"])
added_mult = effect3["xp_mult"] - 1.0 if effect3["xp_mult"] >= 1.0 else effect3["xp_mult"]
p2.xp_multiplier = p2.xp_multiplier + added_mult
print(f"1张Lv3: range={p2.pickup_range}, xp={p2.xp_multiplier}x")

# 测试3: 2张Level 3
p3 = Player()
for i in range(2):
    p3.pickup_range = max(p3.pickup_range, effect3["magnet_range"])
    added_mult = effect3["xp_mult"] - 1.0 if effect3["xp_mult"] >= 1.0 else effect3["xp_mult"]
    p3.xp_multiplier = p3.xp_multiplier + added_mult
print(f"2张Lv3: range={p3.pickup_range}, xp={p3.xp_multiplier}x")
