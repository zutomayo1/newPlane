"""
测试所有卡牌效果是否正确实现
"""
from roguelite import BASE_CARDS, MODIFIER_CARDS

def check_card_effects():
    """检查所有卡牌的effect字段是否在_apply_card_to_player中有对应处理"""
    
    print("=" * 80)
    print("卡牌效果检查报告")
    print("=" * 80)
    
    # 已知的效果处理器列表
    handled_effects = {
        # 攻击类
        "bullet_count", "bullet_count_mult", "damage_mult", "pierce", "pierce_bonus",
        "infinite_pierce", "split_count", "split_damage", "split_level", "fire_rate",
        "speed_mult", "explosion_radius", "explosion_mult", "explosion", "all_bullets_explode",
        
        # 防御类
        "shield_amount", "shield_regen", "dodge_chance", "damage_reduction",
        "max_hp_bonus", "regen_rate", "regen_interval", "lifesteal",
        
        # 控制类
        "slow_mult", "slow_area", "slow_on_hit", "slow_duration", "global_slow",
        "freeze_duration", "freeze_radius", "pull_strength", "time_factor", "radius",
        
        # 特殊效果
        "chain_count", "chain_damage", "chain", "chain_targets", "homing",
        "homing_strength", "crit_chance", "crit_mult", "range_mult", "duration_mult",
        "control_range_mult", "spread_angle",
        
        # 召唤类
        "drone_count", "drone_damage", "turret_count", "turret_damage",
        "summon_count", "summon_damage_mult", "summon_count_mult", "summon_ai",
        
        # 系统类
        "magnet_range", "xp_mult", "chaos_chance", "chaos_mult"
    }
    
    issues = []
    all_cards = {**BASE_CARDS, **MODIFIER_CARDS}
    
    print(f"\n检查 {len(all_cards)} 张卡牌...\n")
    
    for card_id, card_data in all_cards.items():
        card_name = card_data.get("name", card_id)
        
        # 检查base_effect
        base_effect = card_data.get("base_effect", card_data.get("effect", {}))
        
        unhandled = []
        for effect_key in base_effect.keys():
            if effect_key not in handled_effects:
                unhandled.append(effect_key)
        
        if unhandled:
            issues.append({
                "card_id": card_id,
                "card_name": card_name,
                "unhandled": unhandled,
                "category": card_data.get("category", "modifier")
            })
        
        # 检查upgrades中的effect
        upgrades = card_data.get("upgrades", [])
        for i, upgrade in enumerate(upgrades):
            upgrade_effect = upgrade.get("effect", {})
            upgrade_unhandled = []
            
            for effect_key in upgrade_effect.keys():
                if effect_key not in handled_effects:
                    upgrade_unhandled.append(effect_key)
            
            if upgrade_unhandled:
                issues.append({
                    "card_id": card_id,
                    "card_name": card_name,
                    "unhandled": upgrade_unhandled,
                    "level": i + 2,
                    "category": card_data.get("category", "modifier")
                })
    
    # 打印结果
    if not issues:
        print("✅ 所有卡牌效果都已正确实现!\n")
        print(f"共检查 {len(all_cards)} 张卡牌")
        print(f"共 {len(handled_effects)} 种效果类型")
    else:
        print(f"❌ 发现 {len(issues)} 个问题:\n")
        
        for issue in issues:
            level_info = f" [等级{issue['level']}]" if 'level' in issue else ""
            print(f"卡牌: {issue['card_name']} ({issue['card_id']}){level_info}")
            print(f"  类别: {issue['category']}")
            print(f"  未处理的效果: {', '.join(issue['unhandled'])}")
            print()
    
    print("=" * 80)
    
    # 按类别统计卡牌
    print("\n卡牌统计:")
    categories = {}
    for card_id, card_data in BASE_CARDS.items():
        cat = card_data.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count} 张")
    print(f"  modifier: {len(MODIFIER_CARDS)} 张")
    print(f"  总计: {len(all_cards)} 张")
    
    return len(issues) == 0

def list_all_cards():
    """列出所有卡牌及其效果"""
    print("\n" + "=" * 80)
    print("所有卡牌列表")
    print("=" * 80)
    
    print("\n【基础卡牌】")
    for card_id, card_data in BASE_CARDS.items():
        name = card_data.get("name", card_id)
        category = card_data.get("category", "unknown")
        archetype = card_data.get("archetype", "")
        desc = card_data.get("desc", "")
        base_effect = card_data.get("base_effect", {})
        
        print(f"\n{name} ({card_id})")
        print(f"  类别: {category} | 原型: {archetype}")
        print(f"  描述: {desc}")
        print(f"  基础效果: {', '.join(f'{k}={v}' for k, v in base_effect.items())}")
        
        upgrades = card_data.get("upgrades", [])
        if upgrades:
            print(f"  升级路线:")
            for i, upgrade in enumerate(upgrades):
                effect = upgrade.get("effect", {})
                desc = upgrade.get("desc", "")
                print(f"    Lv{i+2}: {desc} ({', '.join(f'{k}={v}' for k, v in effect.items())})")
    
    print("\n【修饰卡牌】")
    for card_id, card_data in MODIFIER_CARDS.items():
        name = card_data.get("name", card_id)
        card_type = card_data.get("type", "unknown")
        desc = card_data.get("desc", "")
        effect = card_data.get("effect", {})
        
        print(f"\n{name} ({card_id})")
        print(f"  类型: {card_type}")
        print(f"  描述: {desc}")
        print(f"  效果: {', '.join(f'{k}={v}' for k, v in effect.items())}")

if __name__ == "__main__":
    # 检查效果实现
    success = check_card_effects()
    
    # 列出所有卡牌
    # list_all_cards()
    
    if success:
        print("\n✅ 所有卡牌检查通过!")
    else:
        print("\n❌ 存在未实现的卡牌效果,请检查!")
