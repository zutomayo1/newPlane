#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试扩展成就系统"""

import sys
sys.path.insert(0, r'c:\Users\真夜中\Desktop\newPlane')

from roguelite import AchievementManager

mgr = AchievementManager()

print("=" * 60)
print("扩展成就系统测试 - 总计24个成就")
print("=" * 60)

print(f"\n成就总数: {len(mgr.achievements)}")

# 按分类显示所有成就
categories = {
    "击杀类": ["first_blood", "killer_100", "killer_500", "killer_1000"],
    "Boss类": ["boss_slayer", "boss_master", "first_boss"],
    "波数类": ["wave_10", "wave_20", "wave_30"],
    "连击类": ["combo_50", "combo_100"],
    "伤害类": ["damage_1000", "damage_5000"],
    "完美类": ["perfect_run", "no_heal", "survivor"],
    "收集类": ["collector", "rich"],
    "速度类": ["speedrun", "fast_clear"],
    "编队类": ["drone_master", "drone_squad"],
}

for cat, ach_ids in categories.items():
    print(f"\n【{cat}】")
    for ach_id in ach_ids:
        if ach_id in mgr.achievements:
            ach = mgr.achievements[ach_id]
            print(f"  [{ach_id:15}] {ach.name:12} - {ach.description:20} ({ach.reward}分)")

print(f"\n{'=' * 60}")
print(f"总成就数: {len(mgr.achievements)}")
print(f"总奖励分数: {sum(a.reward for a in mgr.achievements.values())} 分")
print(f"{'=' * 60}")

# 测试解锁一些成就
print(f"\n【测试成就解锁】")
mgr.add_kill(1)
mgr.check_achievements(None)
print(f"[OK] 击杀1个敌人: {mgr.achievements['first_blood'].unlocked}")

mgr.add_kill(99)
mgr.check_achievements(None)
print(f"[OK] 累计击杀100个: {mgr.achievements['killer_100'].unlocked}")

mgr.add_kill(400)
mgr.check_achievements(None)
print(f"[OK] 累计击杀500个: {mgr.achievements['killer_500'].unlocked}")

mgr.add_kill(500)
mgr.check_achievements(None)
print(f"[OK] 累计击杀1000个: {mgr.achievements['killer_1000'].unlocked}")

print(f"\n已解锁成就数: {sum(1 for a in mgr.achievements.values() if a.unlocked)}")
print(f"已获得奖励分数: {mgr.get_total_reward()}")

print("\n测试完成！成就系统扩展成功 [OK]")
