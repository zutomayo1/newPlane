"""测试经验拾取是否正常工作"""
import sys
sys.path.insert(0, '.')

from roguelite import ItemManager, ExperienceSystem

class TestPlayer:
    def __init__(self):
        self.hp = 100
        self.max_hp = 100
        self.score = 0
        self.level = 1
        self.xp = 0
        self.next_level_xp = 100
        self.exp_system = ExperienceSystem(self)
        
    def add_xp(self, amount):
        """增加经验值"""
        old_level = self.level
        new_level = self.exp_system.add_xp(amount)
        
        # 同步属性
        self.xp = self.exp_system.xp_collected
        self.next_level_xp = self.exp_system.next_level_xp
        self.level = self.exp_system.level
        
        if new_level > old_level:
            print(f"  🎉 升级! {old_level} → {new_level}")
        
        return new_level

# 创建测试对象
player = TestPlayer()
item_mgr = ItemManager()

print("=" * 60)
print("测试经验拾取系统")
print("=" * 60)

# 生成经验物品
print("\n生成5个经验球...")
for i in range(5):
    item = item_mgr.spawn_item("gold", 100 + i*50, 100, rarity=1)
    print(f"  经验球 {i+1}: 价值={item.value}")

print(f"\n初始状态:")
print(f"  等级: {player.level}")
print(f"  经验: {player.xp}/{player.next_level_xp}")
print(f"  分数: {player.score}")

# 模拟拾取
print("\n开始拾取经验球...")
for i, item in enumerate(item_mgr.items):
    print(f"\n拾取第 {i+1} 个经验球 (价值 {item.value}):")
    old_xp = player.xp
    old_level = player.level
    
    item_mgr.pickup_item(item, player)
    
    print(f"  等级: {old_level} → {player.level}")
    print(f"  经验: {old_xp}/{player.next_level_xp} → {player.xp}/{player.next_level_xp}")
    print(f"  经验条: {player.exp_system.get_progress_percent()}%")

print("\n" + "=" * 60)
print(f"最终状态:")
print(f"  等级: {player.level}")
print(f"  经验: {player.xp}/{player.next_level_xp}")
print(f"  经验条进度: {player.exp_system.get_progress_percent()}%")
print("=" * 60)

if player.level > 1:
    print("\n✅ 经验系统正常工作! 成功升级!")
else:
    print("\n⚠️ 经验系统可能有问题,未能升级")
