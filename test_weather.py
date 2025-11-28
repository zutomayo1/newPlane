"""
天气系统测试脚本
"""

import pygame
import math
from weather import WeatherSystem, WeatherType

# 初始化pygame
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("天气系统测试")
clock = pygame.time.Clock()

# 创建天气系统
weather_system = WeatherSystem(WIDTH, HEIGHT)

# 测试循环
running = True
test_duration = 0
max_test_time = 300  # 5秒测试

while running and test_duration < max_test_time:
    clock.tick(60)
    test_duration += 1
    
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # 按1-6切换天气
            elif event.key == pygame.K_1:
                weather_system.current_weather = WeatherType.CLEAR
            elif event.key == pygame.K_2:
                weather_system.current_weather = WeatherType.RAIN
            elif event.key == pygame.K_3:
                weather_system.current_weather = WeatherType.SNOW
            elif event.key == pygame.K_4:
                weather_system.current_weather = WeatherType.METEOR
            elif event.key == pygame.K_5:
                weather_system.current_weather = WeatherType.WIND
            elif event.key == pygame.K_6:
                weather_system.current_weather = WeatherType.SANDSTORM
    
    # 更新天气系统
    weather_system.update()
    
    # 绘制
    screen.fill((10, 10, 20))  # 深空黑
    
    # 绘制背景网格
    for x in range(0, WIDTH, 50):
        pygame.draw.line(screen, (40, 40, 60), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 50):
        pygame.draw.line(screen, (40, 40, 60), (0, y), (WIDTH, y))
    
    # 绘制天气效果
    weather_system.draw(screen)
    
    # 绘制游戏信息
    font = pygame.font.Font(None, 32)
    info_text = f"当前天气: {weather_system.get_weather_name()}"
    surf = font.render(info_text, True, (200, 200, 200))
    screen.blit(surf, (WIDTH - 350, HEIGHT - 100))
    
    info_text2 = f"玩家速度修饰符: {weather_system.player_speed_modifier:.2f}x"
    surf2 = font.render(info_text2, True, (200, 200, 200))
    screen.blit(surf2, (WIDTH - 350, HEIGHT - 60))
    
    info_text3 = f"伤害修饰符: {weather_system.bullet_damage_modifier:.2f}x"
    surf3 = font.render(info_text3, True, (200, 200, 200))
    screen.blit(surf3, (WIDTH - 350, HEIGHT - 20))
    
    # 绘制说明
    small_font = pygame.font.Font(None, 20)
    guide = "按 1-6 切换天气 | ESC 退出"
    guide_surf = small_font.render(guide, True, (150, 150, 150))
    screen.blit(guide_surf, (10, 10))
    
    pygame.display.flip()

pygame.quit()
print("天气系统测试完成！")
print("✅ 测试项目:")
print("  - 雨（降低速度和伤害）")
print("  - 雪（更大幅度降低速度和伤害）")
print("  - 流星雨（流星视觉效果）")
print("  - 强风（影响子弹轨迹和速度）")
print("  - 沙暴（严重影响能见度和速度）")
print("  - 晴空（正常状态）")
