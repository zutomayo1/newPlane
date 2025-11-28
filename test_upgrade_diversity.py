#!/usr/bin/env python3
"""
升级卡牌多样性测试脚本
验证每次升级时选出的卡牌都不相同
"""

import sys
sys.path.insert(0, '.')

from roguelite import ExperienceSystem, UpgradeManager, BUFF_LIBRARY
import random

class MockPlayer:
    def __init__(self):
        self.level = 1
        self.hp = 100
        self.max_hp = 100
        self.damage = 30
        self.xp = 0
        self.upgrade_manager = None

def test_upgrade_diversity():
    """测试多次升级的卡牌是否每次都不同"""
    print("=" * 60)
    print("升级卡牌多样性测试")
    print("=" * 60)
    
    player = MockPlayer()
    upgrade_manager = UpgradeManager()
    upgrade_manager.set_player_ref(player)
    player.upgrade_manager = upgrade_manager
    
    upgrade_results = []
    
    for upgrade_num in range(1, 6):
        print(f"\n【第 {upgrade_num} 次升级】")
        
        # 触发升级
        upgrade_manager.trigger_levelup()
        
        if upgrade_manager.upgrade_choice:
            choices = upgrade_manager.upgrade_choice
            buff_names = [BUFF_LIBRARY[buff_id]['name'] for buff_id in choices]
            print(f"  选项1: {buff_names[0]}")
            print(f"  选项2: {buff_names[1]}")
            print(f"  选项3: {buff_names[2]}")
            
            upgrade_results.append(set(choices))
        
        # 模拟玩家选择第一个
        if upgrade_manager.upgrade_choice:
            upgrade_manager.select_upgrade(0)
    
    # 验证多样性
    print("\n" + "=" * 60)
    print("多样性分析：")
    print("=" * 60)
    
    all_unique = True
    for i in range(len(upgrade_results)):
        for j in range(i + 1, len(upgrade_results)):
            if upgrade_results[i] == upgrade_results[j]:
                print(f"⚠️  警告: 第 {i+1} 和第 {j+1} 次升级的卡牌完全相同！")
                all_unique = False
                
    if all_unique:
        print(f"✅ 通过: 所有 {len(upgrade_results)} 次升级都生成了不同的卡牌组合")
    else:
        print(f"❌ 失败: 存在重复的卡牌组合")
    
    # 统计选项
    print(f"\n共生成 {len(upgrade_results)} 次升级选择，每次3张卡牌")
    print(f"总计 {len(upgrade_results) * 3} 张卡牌，其中：")
    
    all_choices = []
    for result in upgrade_results:
        all_choices.extend(result)
    
    from collections import Counter
    choice_counts = Counter(all_choices)
    for buff_id, count in sorted(choice_counts.items(), key=lambda x: -x[1])[:5]:
        buff_name = BUFF_LIBRARY[buff_id]['name']
        print(f"  {buff_name}: 出现 {count} 次")
    
    return all_unique

if __name__ == "__main__":
    result = test_upgrade_diversity()
    sys.exit(0 if result else 1)
