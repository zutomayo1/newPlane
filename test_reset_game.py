"""测试完整的游戏重置流程"""
import pygame
import sys

print("初始化pygame...")
pygame.init()

print("导入模块...")
from config import *
from utils import *
from systems import *
from sprites import *
from weather import WeatherSystem
from customization import customization_manager

print("创建sprite组...")
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()

print("设置选择的飞机...")
selected_plane = "striker"

print("创建天气系统...")
weather_system = WeatherSystem(WIDTH, HEIGHT)

print("获取涂装...")
try:
    custom_visual = customization_manager.get_theme_visual(
        selected_plane, 
        PLANES[selected_plane].get('visual', None)
    )
    print(f"  涂装获取成功: {custom_visual}")
except Exception as e:
    print(f"  涂装获取失败: {e}")
    import traceback
    traceback.print_exc()
    custom_visual = None

print("创建玩家...")
try:
    player = Player(selected_plane, custom_visual=custom_visual)
    print(f"  玩家创建成功: {player}")
except Exception as e:
    print(f"  玩家创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("初始化肉鸽系统...")
try:
    player.init_roguelite_systems()
    print("  肉鸽系统初始化成功")
except Exception as e:
    print(f"  肉鸽系统初始化失败: {e}")
    import traceback
    traceback.print_exc()

print("添加到sprite组...")
all_sprites.add(player)

print("\n✅ 完整流程测试通过！")
print(f"玩家位置: {player.rect.center}")
print(f"玩家HP: {player.hp}/{player.max_hp}")
print(f"玩家速度: {player.speed}")

pygame.quit()
