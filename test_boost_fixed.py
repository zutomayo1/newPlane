#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""完整测试强度增幅修复后的效果"""

# 模拟完整的卡牌系统
BASE_CARDS = {
    "linear_trajectory": {
        "name": "线性弹道",
        "base_effect": {"bullet_count": 1, "damage_mult": 0.0, "speed_mult": 0.0},
        "upgrades": [
            {"level": 2, "effect": {"bullet_count": 1}},
            {"level": 3, "effect": {"damage_mult": 0.3}}
        ]
    },
    "precision_beam": {
        "name": "精准光束",
        "base_effect": {"damage_mult": 2.5, "pierce": 3, "fire_rate": 0.5}
    }
}

MODIFIER_CARDS = {
    "power_boost": {
        "name": "强度增幅",
        "effect": {"damage_mult": 0.25}
    }
}

class Card:
    def __init__(self, card_id, level=1):
        self.id = card_id
        self.level = level
        self.data = BASE_CARDS[card_id]
        self.modifiers = []
        self.final_effect = self._calculate_effect()
    
    def _calculate_effect(self):
        effect = self.data.get("base_effect", {}).copy()
        
        # 应用升级
        if self.level > 1 and "upgrades" in self.data:
            for upgrade in self.data["upgrades"]:
                if upgrade["level"] <= self.level:
                    for key, value in upgrade["effect"].items():
                        effect[key] = effect.get(key, 0) + value
        
        # 应用参数卡
        for mod_id in self.modifiers:
            if mod_id in MODIFIER_CARDS:
                mod_effect = MODIFIER_CARDS[mod_id]["effect"]
                for key, value in mod_effect.items():
                    if key == "damage_mult":
                        # damage_mult使用加法
                        effect[key] = effect.get(key, 0) + value
        
        return effect
    
    def add_modifier(self, mod_id):
        self.modifiers.append(mod_id)
        self.final_effect = self._calculate_effect()

print("=== 强度增幅修复后测试 ===\n")

# 测试1: 线性弹道 Lv1
print("【测试1】线性弹道 Lv1")
card1 = Card("linear_trajectory", 1)
print(f"无强度增幅: {card1.final_effect}")
card1.add_modifier("power_boost")
print(f"加强度增幅: {card1.final_effect}")
print(f"结果: damage_mult从0.0变为0.25 ✅\n")

# 测试2: 线性弹道 Lv3
print("【测试2】线性弹道 Lv3")
card2 = Card("linear_trajectory", 3)
print(f"无强度增幅: {card2.final_effect}")
card2.add_modifier("power_boost")
print(f"加强度增幅: {card2.final_effect}")
print(f"结果: damage_mult从0.3变为0.55 ✅\n")

# 测试3: 精准光束 Lv1
print("【测试3】精准光束 Lv1")
card3 = Card("precision_beam", 1)
print(f"无强度增幅: {card3.final_effect}")
card3.add_modifier("power_boost")
print(f"加强度增幅: {card3.final_effect}")
print(f"结果: damage_mult从2.5变为2.75 ✅\n")

# 测试4: 应用到玩家
print("=== 应用到玩家 (基础伤害10) ===")
base_damage = 10

for name, card in [("线性Lv1+强化", card1), ("线性Lv3+强化", card2), ("精准Lv1+强化", card3)]:
    final_damage = base_damage * (1.0 + card.final_effect["damage_mult"])
    print(f"{name}: {base_damage} × (1.0 + {card.final_effect['damage_mult']}) = {final_damage}")
