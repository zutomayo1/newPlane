# ==============================================================================
#   新卡牌系统测试脚本
# ==============================================================================
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from roguelite import *

def test_card_system():
    """测试新卡牌系统"""
    print("="*60)
    print("新卡牌系统测试")
    print("="*60)
    
    # 测试1: 基础卡牌数据
    print("\n【测试1】基础卡牌数据")
    print(f"基础卡牌总数: {len(BASE_CARDS)}")
    print(f"参数卡牌总数: {len(MODIFIER_CARDS)}")
    print(f"协同规则总数: {len(SYNERGY_RULES)}")
    
    # 按类别统计
    categories = {}
    for card_id, card_data in BASE_CARDS.items():
        cat = card_data.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n类别分布:")
    for cat, count in categories.items():
        print(f"  {cat}: {count} 张")
    
    # 按流派统计
    archetypes = {}
    for card_id, card_data in BASE_CARDS.items():
        arch = card_data.get("archetype", "unknown")
        archetypes[arch] = archetypes.get(arch, 0) + 1
    
    print("\n流派分布:")
    for arch, count in archetypes.items():
        print(f"  {arch}: {count} 张")
    
    # 测试2: 卡牌实例创建
    print("\n【测试2】卡牌实例创建")
    card1 = Card("linear_trajectory", "base")
    print(f"创建卡牌: {card1.get_display_name()}")
    print(f"流派: {card1.data.get('archetype', 'N/A')}")
    print(f"基础效果: {card1.data.get('base_effect', {})}")
    print(f"数学指纹: {card1.get_formula()}")
    
    # 测试3: 卡牌升级
    print("\n【测试3】卡牌升级")
    print(f"当前等级: Lv.{card1.level}")
    card1.upgrade()
    print(f"升级后: {card1.get_display_name()}")
    print(f"最终效果: {card1.final_effect}")
    
    # 测试4: 添加参数卡
    print("\n【测试4】添加参数卡")
    card1.add_modifier("power_boost")
    card1.add_modifier("homing_addon")
    print(f"附加参数卡: {card1.modifiers}")
    print(f"最终效果: {card1.final_effect}")
    
    # 测试5: 升级管理器
    print("\n【测试5】升级管理器")
    manager = UpgradeManager()
    
    # 模拟添加卡牌
    manager.add_card("linear_trajectory", "base")
    manager.add_card("split_shot", "base")
    manager.add_card("explosive_round", "base")
    
    print(f"当前卡组: {len(manager.owned_cards)} 张卡")
    print(f"流派统计: {manager.archetype_counts}")
    
    # 测试6: 协同触发
    print("\n【测试6】协同触发")
    print(f"激活协同数: {len(manager.active_synergies)}")
    for synergy_id in manager.active_synergies:
        synergy = SYNERGY_RULES[synergy_id]
        print(f"  - {synergy['name']}: {synergy['desc']}")
    
    # 测试7: 构建总结
    print("\n【测试7】构建总结")
    summary = manager.get_build_summary()
    print(f"总卡牌数: {summary['total_cards']}")
    print(f"流派分布: {summary['archetypes']}")
    print(f"协同数: {summary['synergies']}")
    print(f"主流派: {summary['dominant_archetype']}")
    
    # 测试8: 程序化图案生成
    print("\n【测试8】程序化图案生成")
    patterns = ["wave", "spiral", "geometric", "fractal"]
    for i, pattern_type in enumerate(patterns):
        pattern = generate_card_pattern(1000 + i, pattern_type)
        print(f"{pattern_type}: {pattern['formula']}")
    
    # 测试9: 动态难度
    print("\n【测试9】动态难度系统")
    difficulty = DynamicDifficultySystem()
    difficulty.update_difficulty(manager)
    print(f"卡组强度: {difficulty.build_strength_multiplier:.2f}")
    print(f"敌人属性倍率: {difficulty.get_enemy_stat_multiplier():.2f}")
    print(f"刷怪速率倍率: {difficulty.get_spawn_rate_multiplier():.2f}")
    
    print("\n="*60)
    print("测试完成！")
    print("="*60)

def test_all_cards():
    """测试所有卡牌数据完整性"""
    print("\n【完整性测试】检查所有卡牌数据")
    
    errors = []
    
    # 检查基础卡牌
    for card_id, card_data in BASE_CARDS.items():
        if "name" not in card_data:
            errors.append(f"基础卡 {card_id} 缺少 name")
        if "category" not in card_data:
            errors.append(f"基础卡 {card_id} 缺少 category")
        if "archetype" not in card_data:
            errors.append(f"基础卡 {card_id} 缺少 archetype")
        if "base_effect" not in card_data:
            errors.append(f"基础卡 {card_id} 缺少 base_effect")
    
    # 检查参数卡
    for mod_id, mod_data in MODIFIER_CARDS.items():
        if "name" not in mod_data:
            errors.append(f"参数卡 {mod_id} 缺少 name")
        if "effect" not in mod_data:
            errors.append(f"参数卡 {mod_id} 缺少 effect")
    
    # 检查协同规则
    for syn_id, syn_data in SYNERGY_RULES.items():
        if "name" not in syn_data:
            errors.append(f"协同 {syn_id} 缺少 name")
        if "trigger" not in syn_data:
            errors.append(f"协同 {syn_id} 缺少 trigger")
        if "effect" not in syn_data:
            errors.append(f"协同 {syn_id} 缺少 effect")
    
    if errors:
        print(f"发现 {len(errors)} 个错误:")
        for err in errors:
            print(f"  - {err}")
    else:
        print("✓ 所有卡牌数据完整！")

if __name__ == "__main__":
    test_card_system()
    test_all_cards()
    
    print("\n" + "="*60)
    print("卡牌清单")
    print("="*60)
    
    print("\n【基础卡牌 - 攻击类】")
    for card_id, card_data in BASE_CARDS.items():
        if card_data.get("category") == "attack":
            print(f"  • {card_data['name']} ({card_id})")
            print(f"    流派: {card_data.get('archetype', 'N/A')}")
            print(f"    效果: {card_data.get('desc', 'N/A')}")
    
    print("\n【基础卡牌 - 防御类】")
    for card_id, card_data in BASE_CARDS.items():
        if card_data.get("category") == "defense":
            print(f"  • {card_data['name']} ({card_id})")
            print(f"    效果: {card_data.get('desc', 'N/A')}")
    
    print("\n【基础卡牌 - 特殊类】")
    for card_id, card_data in BASE_CARDS.items():
        if card_data.get("category") == "special":
            print(f"  • {card_data['name']} ({card_id})")
            print(f"    效果: {card_data.get('desc', 'N/A')}")
    
    print("\n【基础卡牌 - 系统类】")
    for card_id, card_data in BASE_CARDS.items():
        if card_data.get("category") == "system":
            print(f"  • {card_data['name']} ({card_id})")
            print(f"    效果: {card_data.get('desc', 'N/A')}")
    
    print("\n【参数卡牌】")
    for mod_id, mod_data in MODIFIER_CARDS.items():
        print(f"  • {mod_data['name']} ({mod_id})")
        print(f"    类型: {mod_data.get('type', 'N/A')}")
        print(f"    效果: {mod_data.get('desc', 'N/A')}")
    
    print("\n【协同效果】")
    for syn_id, syn_data in SYNERGY_RULES.items():
        print(f"  • {syn_data['name']} ({syn_id})")
        print(f"    触发: {syn_data.get('trigger', {})}")
        print(f"    效果: {syn_data.get('desc', 'N/A')}")
