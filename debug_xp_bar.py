"""调试经验条显示问题"""
import sys
sys.path.insert(0, '.')

# 模拟游戏环境
import pygame
pygame.init()

from sprites import Player
from config import *

print("=" * 60)
print("调试经验条显示")
print("=" * 60)

# 创建玩家
player = Player("striker")
print(f"\n1. 创建Player后:")
print(f"   player.xp = {player.xp}")
print(f"   player.next_level_xp = {player.next_level_xp}")
print(f"   player.level = {player.level}")
print(f"   player.exp_system = {player.exp_system}")

# 初始化肉鸽系统
print(f"\n2. 调用 init_roguelite_systems()...")
try:
    player.init_roguelite_systems()
except Exception as e:
    print(f"   错误: {e}")
    import traceback
    traceback.print_exc()

print(f"\n3. 初始化后:")
print(f"   player.xp = {player.xp}")
print(f"   player.next_level_xp = {player.next_level_xp}")
print(f"   player.level = {player.level}")
print(f"   player.exp_system = {player.exp_system}")
if player.exp_system:
    print(f"   player.exp_system.xp_collected = {player.exp_system.xp_collected}")
    print(f"   player.exp_system.next_level_xp = {player.exp_system.next_level_xp}")
    print(f"   player.exp_system.level = {player.exp_system.level}")

# 测试增加经验
print(f"\n4. 增加50点经验...")
player.add_xp(50)

print(f"\n5. 增加经验后:")
print(f"   player.xp = {player.xp}")
print(f"   player.next_level_xp = {player.next_level_xp}")
print(f"   player.level = {player.level}")
if player.exp_system:
    print(f"   player.exp_system.xp_collected = {player.exp_system.xp_collected}")
    print(f"   player.exp_system.next_level_xp = {player.exp_system.next_level_xp}")

# 计算经验条百分比
exp_val = player.xp if hasattr(player, 'xp') else 0
exp_max = player.next_level_xp if hasattr(player, 'next_level_xp') else 100
exp_pct = (exp_val / exp_max * 100) if exp_max > 0 else 0

print(f"\n6. 经验条显示计算:")
print(f"   exp_val = {exp_val}")
print(f"   exp_max = {exp_max}")
print(f"   exp_pct = {exp_pct:.1f}%")

# 再增加经验测试升级
print(f"\n7. 再增加60点经验(触发升级)...")
player.add_xp(60)

print(f"\n8. 升级后:")
print(f"   player.xp = {player.xp}")
print(f"   player.next_level_xp = {player.next_level_xp}")
print(f"   player.level = {player.level}")
if player.exp_system:
    print(f"   player.exp_system.xp_collected = {player.exp_system.xp_collected}")
    print(f"   player.exp_system.next_level_xp = {player.exp_system.next_level_xp}")
    print(f"   player.exp_system.level = {player.exp_system.level}")

exp_val = player.xp
exp_max = player.next_level_xp
exp_pct = (exp_val / exp_max * 100) if exp_max > 0 else 0

print(f"\n9. 升级后经验条:")
print(f"   exp_val = {exp_val}")
print(f"   exp_max = {exp_max}")
print(f"   exp_pct = {exp_pct:.1f}%")

print("\n" + "=" * 60)
if player.xp > 0 and player.level > 1:
    print("✅ 经验系统同步正常!")
else:
    print("⚠️ 经验系统同步有问题!")
print("=" * 60)
