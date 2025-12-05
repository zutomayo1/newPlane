#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试强度增幅参数卡效果"""

# 模拟卡牌效果计算
class MockCard:
    def __init__(self, base_effect):
        self.base_effect = base_effect.copy()
        self.modifiers = []
    
    def add_modifier(self, mod_effect):
        """模拟添加参数卡"""
        effect = self.base_effect.copy()
        
        for key, value in mod_effect.items():
            if key == "damage_mult" and key in effect:
                # damage_mult特殊处理
                effect[key] *= value
            elif key.endswith("_mult") and key in effect:
                effect[key] *= value
            else:
                effect[key] = effect.get(key, 0) + value
        
        return effect

print("=== 强度增幅参数卡测试 ===\n")

# 测试1: 线性弹道(damage_mult=0) + 强度增幅
print("【测试1】线性弹道Lv1 + 强度增幅")
card1 = MockCard({"bullet_count": 1, "damage_mult": 0.0})
print(f"基础效果: {card1.base_effect}")
result1 = card1.add_modifier({"damage_mult": 1.25})
print(f"加强度增幅后: {result1}")
print(f"问题: damage_mult = 0 * 1.25 = 0，完全没用！❌\n")

# 测试2: 线性弹道Lv3(damage_mult=0.3) + 强度增幅
print("【测试2】线性弹道Lv3 + 强度增幅")
card2 = MockCard({"bullet_count": 2, "damage_mult": 0.3})
print(f"基础效果: {card2.base_effect}")
result2 = card2.add_modifier({"damage_mult": 1.25})
print(f"加强度增幅后: {result2}")
print(f"damage_mult = 0.3 * 1.25 = 0.375 (+37.5%伤害) ✅\n")

# 测试3: 精准光束(damage_mult=2.5) + 强度增幅
print("【测试3】精准光束Lv1 + 强度增幅")
card3 = MockCard({"damage_mult": 2.5, "pierce": 3})
print(f"基础效果: {card3.base_effect}")
result3 = card3.add_modifier({"damage_mult": 1.25})
print(f"加强度增幅后: {result3}")
print(f"damage_mult = 2.5 * 1.25 = 3.125 ✅\n")

# 测试4: 应用到玩家的最终伤害
print("=== 应用到玩家后的实际伤害 ===")
print("假设玩家基础伤害 = 10")
print()

# 线性弹道Lv1 + 强度增幅
final_damage1 = 10 * (1.0 + 0.0)
print(f"线性Lv1+强度增幅: 10 * (1.0 + 0.0) = {final_damage1} ❌ 没加成!")

# 线性弹道Lv3 + 强度增幅
final_damage2 = 10 * (1.0 + 0.375)
print(f"线性Lv3+强度增幅: 10 * (1.0 + 0.375) = {final_damage2} ✅")

# 精准光束 + 强度增幅
final_damage3 = 10 * (1.0 + 3.125)
print(f"精准Lv1+强度增幅: 10 * (1.0 + 3.125) = {final_damage3} ✅")
