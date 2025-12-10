"""
T1 基础机体渲染

包含 9 种 T1 机体的渲染函数:
- striker: 攻击型
- phantom: 幽灵型
- titan: 巨人型
- thunderbird: 雷鸟型
- viper: 毒蛇型
- specter: 幽灵型
- aurora: 极光型
- crimson: 猩红型
- stalker: 潜行者型
"""
import pygame
import math

from config import (
    CYBER_CYAN, CYBER_CYAN_BRIGHT, CYBER_AMBER, CYBER_RED_ALERT, CYBER_LIME,
    WHITE, BLACK
)


def render_tier1(s, pid, c, edge_color, t, pulse, visual):
    """渲染 T1 机体"""
    
    if pid == "striker":
        _render_striker(s, c, edge_color, t, pulse)
    elif pid == "phantom":
        _render_phantom(s, c, edge_color, t, pulse)
    elif pid == "titan":
        _render_titan(s, c, edge_color, t, pulse)
    elif pid == "thunderbird":
        _render_thunderbird(s, c, edge_color, t, pulse)
    elif pid == "viper":
        _render_viper(s, c, edge_color, t, pulse)
    elif pid == "specter":
        _render_specter(s, c, edge_color, t, pulse)
    elif pid == "aurora":
        _render_aurora(s, c, edge_color, t, pulse)
    elif pid == "crimson":
        _render_crimson(s, c, edge_color, t, pulse)
    elif pid == "stalker":
        _render_stalker(s, c, edge_color, t, pulse)


def _render_striker(s, c, edge_color, t, pulse):
    """Striker - 攻击型：脉动菱形 + 闪烁能量核心"""
    pygame.draw.polygon(s, (50, 100, 150), [(60, 10), (110, 90), (60, 110), (10, 90)])
    pygame.draw.polygon(s, c, [(60, 15), (105, 90), (60, 105), (15, 90)])
    pygame.draw.polygon(s, edge_color, [(60, 15), (105, 90), (60, 105), (15, 90)], 3)
    pygame.draw.polygon(s, (255, 200, 0), [(60, 35), (90, 90), (60, 100), (30, 90)], 1)
    # 动态：能量核心脉动大小
    core_size = int(5 + 3 * pulse)
    pygame.draw.circle(s, (255, 100 + int(155 * pulse), 100), (60, 50), core_size)


def _render_phantom(s, c, edge_color, t, pulse):
    """Phantom - 幽灵型：六边形 + 旋转能量点"""
    main_color = (200, 100, 255)
    pygame.draw.polygon(s, (100, 50, 150), [(60, 10), (90, 50), (120, 110), (60, 90), (0, 110), (30, 50)])
    pygame.draw.polygon(s, main_color, [(60, 15), (88, 52), (115, 105), (60, 88), (5, 105), (32, 52)])
    pygame.draw.polygon(s, edge_color, [(60, 15), (88, 52), (115, 105), (60, 88), (5, 105), (32, 52)], 2)
    # 动态：能量点旋转
    for i in range(3):
        angle = t * 2 + (i * 2 * math.pi / 3)
        x = 60 + math.cos(angle) * 15
        y = 70 + math.sin(angle) * 10
        pygame.draw.circle(s, (150 + int(100 * pulse), 200, 255), (int(x), int(y)), 4)


def _render_titan(s, c, edge_color, t, pulse):
    """Titan - 巨人型：厚重感 + 闪烁炮塔"""
    pygame.draw.rect(s, (80, 50, 20), (18, 18, 84, 84))
    pygame.draw.rect(s, CYBER_AMBER, (20, 20, 80, 80))
    pygame.draw.rect(s, (255, 200, 0), (20, 20, 80, 80), 3)
    tower_brightness = int(100 + 155 * pulse)
    pygame.draw.rect(s, (tower_brightness, tower_brightness // 2, 0), (40, 5, 40, 35))
    pygame.draw.rect(s, (200, 150, 50), (35, 35, 50, 50), 2)
    pygame.draw.circle(s, (255, 255, int(100 * pulse)), (60, 60), 12)


def _render_thunderbird(s, c, edge_color, t, pulse):
    """Thunderbird - 雷鸟型：眼睛闪烁 + 翅膀脉动"""
    main_color = (255, 200, 0)
    pygame.draw.polygon(s, (100, 80, 0), [(60, 0), (20, 60), (0, 40), (20, 100), (60, 80), (100, 100), (120, 40), (100, 60)])
    pygame.draw.polygon(s, main_color, [(60, 5), (25, 60), (5, 40), (25, 95), (60, 75), (95, 95), (115, 40), (95, 60)])
    pygame.draw.polygon(s, edge_color, [(60, 5), (25, 60), (5, 40), (25, 95), (60, 75), (95, 95), (115, 40), (95, 60)], 2)
    # 动态：眼睛闪烁
    eye_bright = int(100 + 155 * pulse)
    pygame.draw.circle(s, (eye_bright, 200, 255), (60, 40), 8)


def _render_viper(s, c, edge_color, t, pulse):
    """Viper - 毒蛇型：毒囊呼吸 + 眼睛跟踪"""
    main_color = (100, 200, 50)
    pygame.draw.polygon(s, (50, 100, 30), [(60, 0), (100, 40), (80, 100), (40, 100), (20, 40)])
    pygame.draw.polygon(s, main_color, [(60, 5), (95, 42), (78, 95), (42, 95), (25, 42)])
    pygame.draw.polygon(s, edge_color, [(60, 5), (95, 42), (78, 95), (42, 95), (25, 42)], 2)
    # 动态：毒囊呼吸
    toxin_points = [(60, int(20 + 5 * pulse)), (int(70 + 5 * pulse), 60), (60, int(50 - 5 * pulse)), (int(50 - 5 * pulse), 60)]
    pygame.draw.polygon(s, (255, int(100 * pulse), 0), toxin_points, 1)
    pygame.draw.circle(s, (255, 100 + int(155 * pulse), 0), (60, 30), 4)


def _render_specter(s, c, edge_color, t, pulse):
    """Specter - 幽灵型：透明度脉动 + 能量波纹"""
    pygame.draw.polygon(s, (30, 40, 80), [(60, 0), (80, 80), (60, 100), (40, 80)])
    pygame.draw.polygon(s, (150, 180, 255), [(60, 5), (78, 78), (60, 95), (42, 78)])
    pygame.draw.polygon(s, edge_color, [(60, 5), (78, 78), (60, 95), (42, 78)], 3)
    pygame.draw.circle(s, WHITE, (60, 50), 8)
    pygame.draw.circle(s, (100, 150, 255), (60, 50), 5)
    # 动态：能量波纹
    ripple_r = int(15 + 5 * pulse)
    pygame.draw.circle(s, (100 + int(155 * pulse), 200, 255), (60, 50), ripple_r, 1)


def _render_aurora(s, c, edge_color, t, pulse):
    """Aurora - 极光型：彩虹色旋转 + 多环脉动"""
    pygame.draw.circle(s, (80, 50, 100), (60, 60), 52)
    pygame.draw.circle(s, (150, 100, 200), (60, 60), 50)
    pygame.draw.circle(s, edge_color, (60, 60), 50, 2)
    # 动态：彩虹色环旋转
    r = int(35 + 5 * pulse)
    color_val = int(200 + 55 * pulse)
    pygame.draw.circle(s, (color_val, 100, 200), (60, 60), r, 1)
    pygame.draw.circle(s, WHITE, (60, 60), 20)
    pygame.draw.circle(s, (255 - int(100 * pulse), 100, 200), (60, 60), 10)


def _render_crimson(s, c, edge_color, t, pulse):
    """Crimson - 猩红型：能量条闪烁 + 边框脉动"""
    pygame.draw.polygon(s, (100, 20, 20), [(50, 80), (20, 20), (50, 40), (80, 20)])
    pygame.draw.polygon(s, CYBER_RED_ALERT, [(50, 78), (22, 22), (50, 42), (78, 22)])
    pygame.draw.polygon(s, (255, 100, 100), [(50, 78), (22, 22), (50, 42), (78, 22)], 3)
    # 动态：能量条颜色脉动
    energy_color_r = int(255 * pulse)
    pygame.draw.line(s, (energy_color_r, int(200 * pulse), 0), (50, 80), (50, 10), 4)
    pygame.draw.line(s, WHITE, (50, 80), (50, 10), 2)


def _render_stalker(s, c, edge_color, t, pulse):
    """Stalker - 潜行者型：眼睛扫描 + 隐身脉动"""
    main_color = (100, 120, 150)
    pygame.draw.polygon(s, (50, 60, 80), [(50, 10), (30, 50), (10, 40), (30, 70), (50, 90), (70, 70), (90, 40), (70, 50)])
    pygame.draw.polygon(s, main_color, [(50, 12), (32, 50), (12, 40), (32, 68), (50, 88), (68, 68), (88, 40), (68, 50)])
    pygame.draw.polygon(s, edge_color, [(50, 12), (32, 50), (12, 40), (32, 68), (50, 88), (68, 68), (88, 40), (68, 50)], 2)
    # 动态：三个眼睛扫描
    for idx, x in enumerate([30, 50, 70]):
        eye_bright = int(255 * abs(math.sin(t * 3 + idx)))
        pygame.draw.circle(s, (eye_bright, 100, 0), (x, 30), 5)
        pygame.draw.circle(s, BLACK, (x, 30), 3)


__all__ = ['render_tier1']
