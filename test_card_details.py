"""
详细检查每张卡牌的实际效果应用
"""
from roguelite import BASE_CARDS, MODIFIER_CARDS

def detailed_card_check():
    """详细检查每张卡牌的效果说明"""
    
    print("=" * 80)
    print("卡牌详细效果检查")
    print("=" * 80)
    
    # 定义效果类型和说明
    effect_descriptions = {
        # 攻击类
        "bullet_count": "子弹数量增加",
        "bullet_count_mult": "子弹数量倍率",
        "damage_mult": "伤害倍率",
        "pierce": "穿透次数",
        "pierce_bonus": "额外穿透",
        "infinite_pierce": "无限穿透",
        "split_count": "分裂数量",
        "split_damage": "分裂伤害倍率",
        "split_level": "分裂等级",
        "fire_rate": "射速倍率",
        "speed_mult": "弹速倍率",
        "explosion_radius": "爆炸半径",
        "explosion_mult": "爆炸伤害倍率",
        "explosion": "爆炸效果",
        "all_bullets_explode": "所有子弹爆炸",
        
        # 防御类
        "shield_amount": "护盾值",
        "shield_regen": "护盾回复速度",
        "dodge_chance": "闪避率",
        "damage_reduction": "伤害减免",
        "max_hp_bonus": "最大生命加成",
        "regen_rate": "生命回复量",
        "regen_interval": "回复间隔",
        "lifesteal": "生命偷取",
        
        # 控制类
        "slow_mult": "减速倍率",
        "slow_area": "减速范围",
        "slow_on_hit": "击中减速",
        "slow_duration": "减速持续时间",
        "global_slow": "全局减速",
        "freeze_duration": "冻结时长",
        "freeze_radius": "冻结范围",
        "pull_strength": "拉力强度",
        "time_factor": "时间因子",
        "radius": "作用半径",
        
        # 特殊效果
        "chain_count": "连锁次数",
        "chain_damage": "连锁伤害倍率",
        "chain": "连锁效果",
        "chain_targets": "连锁目标数",
        "homing": "追踪效果",
        "homing_strength": "追踪强度",
        "crit_chance": "暴击率",
        "crit_mult": "暴击倍率",
        "range_mult": "射程倍率",
        "duration_mult": "持续时间倍率",
        "control_range_mult": "控制范围倍率",
        "spread_angle": "散射角度",
        
        # 召唤类
        "drone_count": "无人机数量",
        "drone_damage": "无人机伤害",
        "turret_count": "炮塔数量",
        "turret_damage": "炮塔伤害",
        "summon_count": "召唤物数量",
        "summon_damage_mult": "召唤物伤害倍率",
        "summon_count_mult": "召唤物数量倍率",
        "summon_ai": "召唤物AI模式",
        
        # 系统类
        "magnet_range": "吸引范围",
        "xp_mult": "经验倍率",
        "chaos_chance": "混沌触发率",
        "chaos_mult": "混沌效果倍率"
    }
    
    print("\n【基础卡牌 - 16张】")
    print("-" * 80)
    
    for i, (card_id, card_data) in enumerate(BASE_CARDS.items(), 1):
        name = card_data.get("name", card_id)
        category = card_data.get("category", "unknown")
        archetype = card_data.get("archetype", "")
        desc = card_data.get("desc", "")
        base_effect = card_data.get("base_effect", {})
        rarity = card_data.get("rarity", 1)
        
        print(f"\n{i}. {name} ({card_id})")
        print(f"   类别: {category} | 原型: {archetype} | 稀有度: {rarity}★")
        print(f"   描述: {desc}")
        print(f"   基础效果:")
        for key, value in base_effect.items():
            desc_text = effect_descriptions.get(key, "未知效果")
            print(f"      • {desc_text}: {value}")
        
        upgrades = card_data.get("upgrades", [])
        if upgrades:
            print(f"   升级路线:")
            for level, upgrade in enumerate(upgrades, 2):
                effect = upgrade.get("effect", {})
                upgrade_desc = upgrade.get("desc", "")
                print(f"      Lv{level}: {upgrade_desc}")
                for key, value in effect.items():
                    desc_text = effect_descriptions.get(key, "未知效果")
                    print(f"         → {desc_text}: {value}")
    
    print("\n" + "=" * 80)
    print("【修饰卡牌 - 10张】")
    print("-" * 80)
    
    for i, (card_id, card_data) in enumerate(MODIFIER_CARDS.items(), 1):
        name = card_data.get("name", card_id)
        card_type = card_data.get("type", "unknown")
        desc = card_data.get("desc", "")
        effect = card_data.get("effect", {})
        rarity = card_data.get("rarity", 1)
        
        print(f"\n{i}. {name} ({card_id})")
        print(f"   类型: {card_type} | 稀有度: {rarity}★")
        print(f"   描述: {desc}")
        print(f"   效果:")
        for key, value in effect.items():
            desc_text = effect_descriptions.get(key, "未知效果")
            print(f"      • {desc_text}: {value}")
    
    print("\n" + "=" * 80)
    print("\n统计信息:")
    print(f"  基础卡牌: 16 张")
    print(f"  修饰卡牌: 10 张")
    print(f"  总计: 26 张")
    print(f"  效果类型: {len(effect_descriptions)} 种")
    
    # 按类别统计
    print("\n基础卡牌分类:")
    categories = {}
    for card_data in BASE_CARDS.values():
        cat = card_data.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items()):
        cat_name = {
            "attack": "攻击类",
            "defense": "防御类", 
            "special": "特殊类",
            "system": "系统类"
        }.get(cat, cat)
        print(f"  {cat_name}: {count} 张")
    
    # 修饰卡牌分类
    print("\n修饰卡牌分类:")
    mod_types = {}
    for card_data in MODIFIER_CARDS.values():
        mod_type = card_data.get("type", "unknown")
        mod_types[mod_type] = mod_types.get(mod_type, 0) + 1
    
    for mod_type, count in sorted(mod_types.items()):
        type_name = {
            "numeric": "数值类",
            "trait": "特性类"
        }.get(mod_type, mod_type)
        print(f"  {type_name}: {count} 张")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    detailed_card_check()
