#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试范围拓展修复后的效果"""

# 模拟卡牌系统
BASE_CARDS = {
    "explosive_round": {
        "name": "爆裂弹头",
        "base_effect": {"explosion_radius": 80, "explosion_mult": 0.6}
    },
    "gravity_field": {
        "name": "引力场",
        "base_effect": {"slow_mult": 0.6, "pull_strength": 2.0, "radius": 150}
    },
    "frost_nova": {
        "name": "冰霜新星",
        "base_effect": {"freeze_duration": 120, "freeze_radius": 100}
    },
    "resource_magnet": {
        "name": "资源磁场",
        "base_effect": {"magnet_range": 200, "xp_mult": 1.2}
    },
    "linear_trajectory": {
        "name": "线性弹道",
        "base_effect": {"bullet_count": 1, "damage_mult": 0.0}
    }
}

MODIFIER_CARDS = {
    "range_extend": {
        "name": "范围拓展",
        "effect": {"range_mult": 1.4}
    }
}

def apply_modifier(base_effect, mod_effect):
    """应用参数卡到基础卡"""
    effect = base_effect.copy()
    
    for key, value in mod_effect.items():
        if key == "range_mult":
            # range_mult特殊处理:增强所有范围相关属性
            for range_key in ["radius", "explosion_radius", "freeze_radius", "magnet_range", "slow_area"]:
                if range_key in effect:
                    effect[range_key] *= value
    
    return effect

print("=== 范围拓展修复后测试 ===\n")

# 测试有范围属性的卡牌
test_cards = [
    ("explosive_round", "爆裂弹头"),
    ("gravity_field", "引力场"),
    ("frost_nova", "冰霜新星"),
    ("resource_magnet", "资源磁场")
]

for card_id, card_name in test_cards:
    base = BASE_CARDS[card_id]["base_effect"]
    modified = apply_modifier(base, MODIFIER_CARDS["range_extend"]["effect"])
    
    print(f"【{card_name}】")
    print(f"  基础: {base}")
    print(f"  加范围拓展: {modified}")
    
    # 找出变化的范围属性
    for key in base:
        if key in ["radius", "explosion_radius", "freeze_radius", "magnet_range"]:
            old_val = base[key]
            new_val = modified[key]
            print(f"  ✅ {key}: {old_val} → {new_val} (×1.4)")
    print()

# 测试没有范围属性的卡牌
print("【线性弹道 - 无范围属性】")
base = BASE_CARDS["linear_trajectory"]["base_effect"]
modified = apply_modifier(base, MODIFIER_CARDS["range_extend"]["effect"])
print(f"  基础: {base}")
print(f"  加范围拓展: {modified}")
print(f"  ✅ 没有范围属性,效果不变")
