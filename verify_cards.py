"""快速验证卡牌效果是否生效"""
import sys
sys.path.insert(0, '.')

from roguelite import BASE_CARDS, UpgradeManager

class SimplePlayer:
    def __init__(self):
        self.damage = 10
        self.bullet_count = 1
        self.piercing = 0
        self.shield = 0
        self.max_hp = 100
        self.delay = 200
        self.wingmen = []
        
manager = UpgradeManager()
player = SimplePlayer()
manager.set_player_ref(player)

print("测试关键卡牌效果:")
print("=" * 60)

# 测试1: 线性弹道 (bullet_count + damage_mult + speed_mult)
print("\n1. 线性弹道 (弹幕+1, 伤害×1.0, 速度×1.0)")
print(f"   添加前: 子弹={player.bullet_count}, 伤害={player.damage}")
manager.add_card("linear_trajectory", "base")
print(f"   添加后: 子弹={player.bullet_count}, 伤害={player.damage}")
print(f"   效果属性: {BASE_CARDS['linear_trajectory']['base_effect']}")

# 测试2: 精准光束 (damage_mult + pierce + fire_rate)
print("\n2. 精准光束 (伤害×2.5, 穿透+3, 射速×0.5)")
old_dmg = player.damage
old_pierce = player.piercing
old_delay = player.delay
manager.add_card("precision_beam", "base")
print(f"   伤害: {old_dmg} → {player.damage} (×{player.damage/old_dmg:.1f})")
print(f"   穿透: {old_pierce} → {player.piercing}")
print(f"   射速延迟: {old_delay} → {player.delay}")

# 测试3: 能量护盾 (shield_amount + shield_regen)
print("\n3. 能量护盾 (护盾+30, 回复+1)")
old_shield = player.shield
manager.add_card("energy_shield", "base")
print(f"   护盾: {old_shield} → {player.shield}")
print(f"   护盾回复: {hasattr(player, 'shield_regen')} -> {getattr(player, 'shield_regen', 0)}")

# 测试4: 无人机群 (drone_count + drone_damage)
print("\n4. 无人机群 (僚机+2, 僚机伤害×1.0)")
old_wingmen = len(player.wingmen)
manager.add_card("drone_swarm", "base")
print(f"   僚机数量: {old_wingmen} → {len(player.wingmen)}")
print(f"   僚机伤害倍率: {getattr(player, 'drone_damage_mult', 1.0)}")

print("\n" + "=" * 60)
print(f"总计卡牌: {len(manager.owned_cards)}")
print(f"流派统计: {manager.archetype_counts}")
print("\n✓ 关键效果测试完成!")
