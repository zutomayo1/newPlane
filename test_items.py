#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试物品系统功能"""

import sys
sys.path.insert(0, r'c:\Users\真夜中\Desktop\newPlane')

from roguelite import ItemManager, Item

print("=" * 50)
print("物品系统测试")
print("=" * 50)

# 创建物品管理器
item_mgr = ItemManager()

print("\n1. 创建物品:")
item1 = item_mgr.spawn_item("health", 100, 100, 1)
print(f"   ✓ 生成医疗包: {item1.name} 价值 {item1.value} HP")

item2 = item_mgr.spawn_item("gold", 200, 200, 2)
print(f"   ✓ 生成经验值: {item2.name} 价值 {item2.value} 分")

item3 = item_mgr.spawn_item("core", 300, 300, 3)
print(f"   ✓ 生成核心片段: {item3.name} 稀有度 {item3.rarity}★")

print(f"\n2. 物品管理器状态:")
print(f"   当前物品数: {len(item_mgr.items)}")
print(f"   存活物品: {sum(1 for i in item_mgr.items if i.alive)}")

print(f"\n3. 物品属性:")
for item in item_mgr.items:
    print(f"   - {item.name}: 位置({item.x}, {item.y}), 价值{item.value}, 颜色{item.color}")

print(f"\n4. 随机掉落:")
for i in range(5):
    item = item_mgr.spawn_random_drop(400 + i*50, 100, rarity=2)
    print(f"   - 掉落 {item.name} (稀有度 {item.rarity}★)")

print(f"\n5. 最终统计:")
print(f"   总物品数: {len(item_mgr.items)}")

print("\n" + "=" * 50)
print("物品系统测试完成 ✓")
print("=" * 50)
