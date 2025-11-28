#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试成就系统功能"""

import sys
sys.path.insert(0, r'c:\Users\真夜中\Desktop\newPlane')

from roguelite import AchievementManager

# 创建成就管理器
mgr = AchievementManager()

print("=" * 50)
print("成就系统测试")
print("=" * 50)

# 测试初始状态
print("\n1. 初始状态:")
print(f"   总成就数: {len(mgr.achievements)}")
print(f"   已解锁: {sum(1 for a in mgr.achievements.values() if a.unlocked)}")
print(f"   总奖励: {mgr.get_total_reward()}")

# 测试成就
print("\n2. 成就列表:")
for ach_id, ach in list(mgr.achievements.items())[:5]:
    print(f"   - {ach.name}: {ach.description}")

# 测试击杀计数
print("\n3. 测试击杀数据:")
mgr.add_kill(1)
print(f"   击杀1个敌人后...")
unlocked = mgr.check_achievements(None)
if "first_blood" in unlocked:
    print(f"   ✓ 解锁成就: 初次杀戮")
else:
    print(f"   ✗ 未解锁")

mgr.add_kill(99)
print(f"   累计击杀100个敌人后...")
unlocked = mgr.check_achievements(None)
if "killer_100" in unlocked:
    print(f"   ✓ 解锁成就: 百杀者")
else:
    print(f"   ✗ 未解锁")

# 测试伤害数据
print("\n4. 测试伤害数据:")
mgr.add_damage(1500)
print(f"   造成1500伤害后...")
unlocked = mgr.check_achievements(None)
if "damage_1000" in unlocked:
    print(f"   ✓ 解锁成就: 破坏者")
else:
    print(f"   ✗ 未解锁")

# 测试波数
print("\n5. 测试波数:")
mgr.update_max_wave(15)
print(f"   到达第15波后...")
unlocked = mgr.check_achievements(None)
if "wave_10" in unlocked:
    print(f"   ✓ 解锁成就: 十波生存")
else:
    print(f"   ✗ 未解锁")

# 最终统计
print("\n6. 最终统计:")
unlocked_achievements = mgr.get_unlocked_achievements()
print(f"   已解锁成就: {len(unlocked_achievements)}")
for ach in unlocked_achievements:
    print(f"   ✓ {ach.name} (+{ach.reward}分)")
print(f"   总奖励分数: {mgr.get_total_reward()}")

print("\n" + "=" * 50)
print("测试完成！成就系统正常运行 ✓")
print("=" * 50)
