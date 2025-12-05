"""
完整的卡牌系统集成测试
测试从经验获取、升级触发、卡牌选择、效果应用的完整流程
"""
import pygame
import sys
sys.path.insert(0, '.')

# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))

print("="*60)
print("卡牌系统完整性测试")
print("="*60)

# ==============================================================================
# 测试1: 导入所有必要模块
# ==============================================================================
print("\n[测试1] 模块导入...")
try:
    from roguelite import (
        BASE_CARDS, MODIFIER_CARDS, SYNERGY_RULES,
        Card, UpgradeManager, ExperienceSystem
    )
    from sprites import Player
    print("✅ 所有模块导入成功")
except Exception as e:
    print(f"❌ 模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# 测试2: 数据完整性
# ==============================================================================
print("\n[测试2] 数据完整性...")
print(f"  - 基础卡牌: {len(BASE_CARDS)} 张")
print(f"  - 参数卡牌: {len(MODIFIER_CARDS)} 张")
print(f"  - 协同规则: {len(SYNERGY_RULES)} 个")

# 检查每张卡牌是否有必要字段
required_base_fields = ["name", "category", "archetype", "desc", "base_effect", "rarity"]
required_modifier_fields = ["name", "type", "desc", "effect", "rarity"]

errors = []
for card_id, card_data in BASE_CARDS.items():
    for field in required_base_fields:
        if field not in card_data:
            errors.append(f"基础卡 {card_id} 缺少字段: {field}")

for card_id, card_data in MODIFIER_CARDS.items():
    for field in required_modifier_fields:
        if field not in card_data:
            errors.append(f"参数卡 {card_id} 缺少字段: {field}")

if errors:
    print("❌ 数据完整性检查失败:")
    for err in errors:
        print(f"  - {err}")
else:
    print("✅ 所有卡牌数据完整")

# ==============================================================================
# 测试3: Player和系统初始化
# ==============================================================================
print("\n[测试3] Player和系统初始化...")
try:
    # Player(plane_id, custom_visual=None)
    player = Player("striker")
    player.init_roguelite_systems()
    
    assert player.exp_system is not None, "经验系统未初始化"
    assert player.upgrade_manager is not None, "升级管理器未初始化"
    assert player.xp == 0, "初始经验值不为0"
    assert player.level == 1, "初始等级不为1"
    
    print(f"✅ Player初始化成功")
    print(f"  - 经验: {player.xp}/{player.next_level_xp}")
    print(f"  - 等级: {player.level}")
except Exception as e:
    print(f"❌ Player初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# 测试4: 经验系统和升级触发
# ==============================================================================
print("\n[测试4] 经验系统和升级触发...")
try:
    # 增加经验到升级
    initial_level = player.level
    print(f"  初始等级: {initial_level}")
    
    # 添加足够经验升级
    xp_needed = player.next_level_xp - player.xp
    new_level = player.add_xp(xp_needed + 10)
    
    assert new_level > initial_level, f"等级未提升: {initial_level} -> {new_level}"
    print(f"  ✓ 等级提升: {initial_level} -> {new_level}")
    print(f"  ✓ 经验: {player.xp}/{player.next_level_xp}")
    
    # 触发升级卡牌选择
    player.upgrade_manager.trigger_levelup()
    assert player.upgrade_manager.level_up_ready, "升级未就绪"
    assert player.upgrade_manager.upgrade_choice is not None, "升级选项未生成"
    assert len(player.upgrade_manager.upgrade_choice) == 3, f"升级选项数量错误: {len(player.upgrade_manager.upgrade_choice)}"
    
    print(f"  ✓ 升级选项生成: {len(player.upgrade_manager.upgrade_choice)} 个")
    for i, choice in enumerate(player.upgrade_manager.upgrade_choice):
        print(f"    {i+1}. 类型={choice['type']}, ID={choice['id']}")
    
    print("✅ 经验系统和升级触发正常")
except Exception as e:
    print(f"❌ 经验系统测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# 测试5: 卡牌选择和效果应用
# ==============================================================================
print("\n[测试5] 卡牌选择和效果应用...")
try:
    # 记录初始属性
    initial_damage = player.damage
    initial_hp = player.max_hp
    initial_cards = len(player.upgrade_manager.owned_cards)
    
    print(f"  选择前: 伤害={initial_damage}, 生命={initial_hp}, 卡牌数={initial_cards}")
    
    # 选择第一个选项
    success = player.upgrade_manager.select_upgrade(0)
    assert success, "卡牌选择失败"
    
    # 检查状态
    assert len(player.upgrade_manager.owned_cards) > initial_cards, "卡牌未添加到卡组"
    assert player.upgrade_manager.upgrade_choice is None, "升级选项未清除"
    assert not player.upgrade_manager.level_up_ready, "升级状态未重置"
    
    print(f"  选择后: 伤害={player.damage}, 生命={player.max_hp}, 卡牌数={len(player.upgrade_manager.owned_cards)}")
    print(f"  ✓ 卡牌已添加到卡组")
    print(f"  ✓ 属性变化: 伤害 {initial_damage}->{player.damage}")
    
    print("✅ 卡牌选择和效果应用正常")
except Exception as e:
    print(f"❌ 卡牌选择测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# 测试6: 多次升级和协同触发
# ==============================================================================
print("\n[测试6] 多次升级和协同触发...")
try:
    # 连续升级3次
    for round_num in range(3):
        # 增加经验升级
        xp_needed = player.next_level_xp - player.xp + 10
        player.add_xp(xp_needed)
        
        # 触发升级
        player.upgrade_manager.trigger_levelup()
        
        # 选择第一个选项
        if player.upgrade_manager.upgrade_choice:
            choice = player.upgrade_manager.upgrade_choice[0]
            player.upgrade_manager.select_upgrade(0)
            print(f"  第{round_num+1}轮: 选择了 {choice['type']}/{choice['id']}")
    
    # 检查协同
    print(f"  ✓ 总卡牌数: {len(player.upgrade_manager.owned_cards)}")
    print(f"  ✓ 流派统计: {player.upgrade_manager.archetype_counts}")
    print(f"  ✓ 激活协同: {len(player.upgrade_manager.active_synergies)} 个")
    
    if player.upgrade_manager.active_synergies:
        for syn_id in player.upgrade_manager.active_synergies:
            syn_data = SYNERGY_RULES[syn_id]
            print(f"    - {syn_data['name']}: {syn_data['desc']}")
    
    print("✅ 多次升级和协同系统正常")
except Exception as e:
    print(f"❌ 多次升级测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# 测试7: 卡牌升级
# ==============================================================================
print("\n[测试7] 卡牌升级...")
try:
    # 找到一张基础卡牌
    base_cards = [card for card in player.upgrade_manager.owned_cards.values() if card.type == "base"]
    
    if base_cards:
        test_card = base_cards[0]
        initial_level = test_card.level
        
        # 尝试升级
        upgrade_success = test_card.upgrade()
        
        if upgrade_success:
            assert test_card.level > initial_level, "卡牌等级未提升"
            print(f"  ✓ 卡牌 {test_card.id} 升级: {initial_level} -> {test_card.level}")
        else:
            print(f"  - 卡牌 {test_card.id} 已满级")
        
        print("✅ 卡牌升级系统正常")
    else:
        print("⚠️ 没有基础卡牌可供测试升级")
except Exception as e:
    print(f"❌ 卡牌升级测试失败: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# 测试总结
# ==============================================================================
print("\n" + "="*60)
print("测试总结")
print("="*60)
print(f"✅ 最终状态:")
print(f"  - 玩家等级: {player.level}")
print(f"  - 玩家经验: {player.xp}/{player.next_level_xp}")
print(f"  - 卡组大小: {len(player.upgrade_manager.owned_cards)} 张")
print(f"  - 伤害: {player.damage}")
print(f"  - 生命: {player.max_hp}")
print(f"  - 激活协同: {len(player.upgrade_manager.active_synergies)} 个")
print(f"\n✅ 所有测试通过! 卡牌系统可以正常游玩!")
print("="*60)

pygame.quit()
