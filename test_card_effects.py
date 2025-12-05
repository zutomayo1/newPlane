"""测试卡牌效果是否正确应用"""
import sys
from roguelite import BASE_CARDS, MODIFIER_CARDS, SYNERGY_RULES, Card, UpgradeManager

# 模拟一个简单的玩家对象
class MockPlayer:
    def __init__(self):
        self.level = 1
        self.damage = 10
        self.bullet_count = 1
        self.piercing = 0
        self.shield = 0
        self.max_hp = 100
        self.dodge_chance = 0
        self.damage_reduction = 0
        self.has_regen = False
        self.has_gravity_field = False
        self.has_chain_lightning = False
        self.has_frost = False
        self.has_turrets = False
        self.pickup_range = 200
        self.xp_multiplier = 1.0
        self.has_chaos = False
        self.crit_chance = 0
        
def check_card_effect_mapping():
    """检查卡牌效果属性是否都能被应用"""
    print("=" * 60)
    print("检查卡牌效果映射")
    print("=" * 60)
    
    # 收集所有卡牌中使用的效果属性
    all_effects = set()
    
    # 基础卡牌
    for card_id, card_data in BASE_CARDS.items():
        if "base_effect" in card_data:
            all_effects.update(card_data["base_effect"].keys())
        for upgrade in card_data.get("upgrades", []):
            if "effect" in upgrade:
                all_effects.update(upgrade["effect"].keys())
    
    # 参数卡牌
    for card_id, card_data in MODIFIER_CARDS.items():
        if "effect" in card_data:
            if isinstance(card_data["effect"], dict):
                all_effects.update(card_data["effect"].keys())
    
    # 协同效果
    for synergy_id, synergy_data in SYNERGY_RULES.items():
        if "effect" in synergy_data:
            all_effects.update(synergy_data["effect"].keys())
    
    print(f"\n发现 {len(all_effects)} 种效果属性:")
    for effect in sorted(all_effects):
        print(f"  - {effect}")
    
    # 检查 _apply_card_to_player 方法中处理的属性
    handled_effects = {
        "bullet_count", "damage_mult", "pierce", "split_count", "split_damage",
        "shield_amount", "dodge_chance", "damage_reduction", "max_hp_bonus", 
        "regen_rate", "regen_interval", "slow_mult", "radius", "chain_count",
        "chain_damage", "freeze_duration", "drone_count", "turret_count",
        "turret_damage", "magnet_range", "xp_mult", "chaos_chance", "chaos_mult"
    }
    
    print(f"\n_apply_card_to_player 中处理 {len(handled_effects)} 种属性:")
    for effect in sorted(handled_effects):
        print(f"  - {effect}")
    
    # 找出未处理的效果
    unhandled = all_effects - handled_effects
    if unhandled:
        print(f"\n⚠️ 警告: 以下 {len(unhandled)} 个效果未被处理:")
        for effect in sorted(unhandled):
            print(f"  ❌ {effect}")
            # 找出哪些卡牌使用了这个效果
            cards_using = []
            for card_id, card_data in BASE_CARDS.items():
                if "base_effect" in card_data and effect in card_data["base_effect"]:
                    cards_using.append(f"基础:{card_data['name']}")
                for upgrade in card_data.get("upgrades", []):
                    if "effect" in upgrade and effect in upgrade["effect"]:
                        cards_using.append(f"基础:{card_data['name']}(升级)")
            for card_id, card_data in MODIFIER_CARDS.items():
                if "effect" in card_data and isinstance(card_data["effect"], dict) and effect in card_data["effect"]:
                    cards_using.append(f"参数:{card_data['name']}")
            for synergy_id, synergy_data in SYNERGY_RULES.items():
                if "effect" in synergy_data and effect in synergy_data["effect"]:
                    cards_using.append(f"协同:{synergy_data['name']}")
            print(f"     使用此效果的卡牌: {', '.join(cards_using)}")
    else:
        print("\n✓ 所有效果都已正确处理!")
    
    # 检查多余处理的效果
    extra_handled = handled_effects - all_effects
    if extra_handled:
        print(f"\n⚠️ 注意: 以下 {len(extra_handled)} 个效果被处理但没有卡牌使用:")
        for effect in sorted(extra_handled):
            print(f"  ? {effect}")
    
    return len(unhandled) == 0

def test_card_application():
    """测试卡牌是否能正确应用"""
    print("\n" + "=" * 60)
    print("测试卡牌应用")
    print("=" * 60)
    
    player = MockPlayer()
    manager = UpgradeManager()
    manager.set_player_ref(player)
    
    # 测试几张关键卡牌
    test_cards = [
        ("linear_trajectory", "base", "线性弹道"),
        ("energy_shield", "base", "能量护盾"),
        ("gravity_field", "base", "引力场"),
        ("power_boost", "modifier", "强度增幅"),
    ]
    
    print("\n测试卡牌应用:")
    for card_id, card_type, card_name in test_cards:
        print(f"\n测试 [{card_name}] (ID: {card_id})...")
        old_damage = player.damage
        old_bullet = player.bullet_count
        old_shield = player.shield
        
        success = manager.add_card(card_id, card_type)
        
        if success:
            print(f"  ✓ 卡牌添加成功")
            print(f"    伤害: {old_damage} → {player.damage}")
            print(f"    子弹: {old_bullet} → {player.bullet_count}")
            print(f"    护盾: {old_shield} → {player.shield}")
            if hasattr(player, 'has_gravity_field'):
                print(f"    引力场: {player.has_gravity_field}")
        else:
            print(f"  ❌ 卡牌添加失败")
    
    print(f"\n当前拥有 {len(manager.owned_cards)} 张卡牌")
    print(f"流派统计: {manager.archetype_counts}")
    print(f"激活协同: {len(manager.active_synergies)} 个")

if __name__ == "__main__":
    all_good = check_card_effect_mapping()
    test_card_application()
    
    if all_good:
        print("\n" + "=" * 60)
        print("✓ 所有检查通过!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("⚠️ 发现问题,需要修复!")
        print("=" * 60)
        sys.exit(1)
