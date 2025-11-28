#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试成就通知UI系统"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from roguelite import AchievementManager
from sprites import Player

def test_achievement_notifications():
    """测试成就通知系统集成"""
    print("=" * 60)
    print("Achievement Notification System Test")
    print("=" * 60)
    
    # 创建玩家实例以初始化成就系统
    player = Player()  # 使用默认飞机
    player.init_roguelite_systems()  # 手动初始化肉鸽系统
    
    # 确保玩家有成就管理器
    if not hasattr(player, 'achievement_manager'):
        print("Error: Player has no achievement manager")
        return False
    
    mgr = player.achievement_manager
    
    print(f"\nAchievement System Initialized")
    print(f"  - Total achievements: {len(mgr.achievements)}")
    print(f"  - Unlocked: {sum(1 for a in mgr.achievements.values() if a.unlocked)}")
    print(f"  - Total reward: {mgr.get_total_reward()}")
    
    # 测试成就解锁
    print("\nTesting achievement unlock process...")
    
    # 测试击杀成就
    print("\n  Simulating 100 enemy kills:")
    for i in range(100):
        mgr.add_kill(1)
    
    new_achievements = mgr.check_achievements(player)
    print(f"  - Unlocked {len(new_achievements)} achievements")
    
    if new_achievements:
        for ach_id in new_achievements:
            ach = mgr.achievements[ach_id]
            print(f"    OK {ach.name} (+{ach.reward} pts)")
    
    # 测试波数成就
    print("\n  Simulating 20 waves cleared:")
    for wave in range(1, 21):
        mgr.update_max_wave(wave)
    
    new_achievements = mgr.check_achievements(player)
    print(f"  - Unlocked {len(new_achievements)} achievements")
    
    if new_achievements:
        for ach_id in new_achievements:
            ach = mgr.achievements[ach_id]
            print(f"    OK {ach.name} (+{ach.reward} pts)")
    
    # 测试Boss成就
    print("\n  Simulating 1 boss kill:")
    mgr.stats["bosses_killed"] = 1
    new_achievements = mgr.check_achievements(player)
    print(f"  - Unlocked {len(new_achievements)} achievements")
    
    if new_achievements:
        for ach_id in new_achievements:
            ach = mgr.achievements[ach_id]
            print(f"    OK {ach.name} (+{ach.reward} pts)")
    
    print("\n" + "=" * 60)
    print("Achievement Statistics:")
    print(f"  Total achievements: {len(mgr.achievements)}")
    unlocked = [a for a in mgr.achievements.values() if a.unlocked]
    print(f"  Unlocked: {len(unlocked)}")
    print(f"  Total points: {sum(a.reward for a in unlocked)}")
    print("=" * 60)
    
    return True

def test_save_load():
    """测试成就保存与加载"""
    print("\nTesting save & load...")
    player = Player()
    player.init_roguelite_systems()
    mgr = player.achievement_manager
    # 模拟一个成就解锁状态
    mgr.achievements['first_blood'].unlock()
    mgr.stats['total_kills'] = 100
    # 保存到临时文件
    testfile = 'achievements_test.json'
    if mgr.save_to_file(testfile):
        print(f"  Saved to {testfile}")
    else:
        print("  Failed to save file")
        return False

    # 新建管理器并加载
    mgr2 = AchievementManager()
    if mgr2.load_from_file(testfile):
        print("  Loaded from file")
    else:
        print("  Failed to load file")
        return False

    unlocked_before = [ach.id for ach in mgr.get_unlocked_achievements()]
    unlocked_after = [ach.id for ach in mgr2.get_unlocked_achievements()]
    print(f"  Before: {unlocked_before}")
    print(f"  After:  {unlocked_after}")
    return set(unlocked_before) == set(unlocked_after)

if __name__ == "__main__":
    success1 = test_achievement_notifications()
    success2 = test_save_load()
    success = success1 and success2
    sys.exit(0 if success else 1)
