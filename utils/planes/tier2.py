"""
T2 进阶机体渲染

包含 4 种 T2 机体的渲染函数:
- gaia: 盖亚型
- weaver: 织网者型
- solar: 太阳型
- arbiter: 仲裁者型
"""
import pygame
import math

from config import CYBER_LIME, CYBER_AMBER, WHITE


def render_tier2(s, pid, c, edge_color, t, pulse, visual):
    """渲染 T2 机体"""
    
    if pid == "gaia":
        _render_gaia(s, c, edge_color, t, pulse)
    elif pid == "weaver":
        _render_weaver(s, c, edge_color, t, pulse)
    elif pid == "solar":
        _render_solar(s, c, edge_color, t, pulse)
    elif pid == "arbiter":
        _render_arbiter(s, c, edge_color, t, pulse)


def _render_gaia(s, c, edge_color, t, pulse):
    """Gaia - 盖亚型：中心生长脉动 + 能量流动"""
    main_color = (100, 200, 100)
    pygame.draw.polygon(s, (50, 100, 50), [(30, 20), (70, 20), (90, 60), (70, 90), (30, 90), (10, 60)])
    pygame.draw.polygon(s, main_color, [(32, 22), (68, 22), (88, 60), (68, 88), (32, 88), (12, 60)])
    pygame.draw.polygon(s, edge_color, [(32, 22), (68, 22), (88, 60), (68, 88), (32, 88), (12, 60)], 2)
    # 动态：中心圆脉动生长
    core_r = int(22 + 5 * pulse)
    pygame.draw.circle(s, CYBER_LIME, (50, 50), core_r)
    pygame.draw.circle(s, (200, 255, 100), (50, 50), int(18 + 3 * pulse))
    pygame.draw.circle(s, (100, 150, 100), (50, 50), 8)


def _render_weaver(s, c, edge_color, t, pulse):
    """Weaver - 织网者型：蜘蛛网旋转 + 中心脉动"""
    pygame.draw.circle(s, (80, 80, 100), (60, 60), 26)
    pygame.draw.circle(s, (200, 200, 220), (60, 60), 25)
    pygame.draw.circle(s, edge_color, (60, 60), 25, 2)
    pygame.draw.circle(s, WHITE, (60, 60), 15)
    pygame.draw.circle(s, (100, 150, 200), (60, 60), 10)
    # 动态：蜘蛛网旋转
    for angle in range(0, 360, 45):
        rad = math.radians(angle + t * 50)
        x = 60 + math.cos(rad) * 30
        y = 60 + math.sin(rad) * 30
        web_color = (int(150 + 100 * pulse), 180, 200)
        pygame.draw.line(s, web_color, (60, 60), (x, y), 1)


def _render_solar(s, c, edge_color, t, pulse):
    """Solar - 太阳型：放射线旋转 + 脉冲能量"""
    pygame.draw.circle(s, (100, 50, 0), (60, 60), 32)
    pygame.draw.circle(s, CYBER_AMBER, (60, 60), 30)
    pygame.draw.circle(s, (255, 200, 0), (60, 60), 30, 2)
    # 动态：8条放射线旋转
    for i in range(8):
        angle = (t * 2 + i * 45) * math.pi / 180
        x1 = 60 + math.cos(angle) * (25 + int(10 * pulse))
        y1 = 60 + math.sin(angle) * (25 + int(10 * pulse))
        x2 = 60 + math.cos(angle) * (45 + int(10 * pulse))
        y2 = 60 + math.sin(angle) * (45 + int(10 * pulse))
        pygame.draw.line(s, (255, 255, int(100 * pulse)), (int(x1), int(y1)), (int(x2), int(y2)), 2)
    pygame.draw.circle(s, (255, 255, int(100 + 155 * pulse)), (60, 60), 12)


def _render_arbiter(s, c, edge_color, t, pulse):
    """Arbiter - 仲裁者型：内部正方形旋转 + 能量脉冲"""
    main_color = (100, 150, 200)
    pygame.draw.polygon(s, (50, 75, 100), [(60, 10), (110, 60), (60, 110), (10, 60)])
    pygame.draw.polygon(s, main_color, [(60, 12), (108, 60), (60, 108), (12, 60)])
    pygame.draw.polygon(s, edge_color, [(60, 12), (108, 60), (60, 108), (12, 60)], 2)
    # 动态：内部正方形旋转
    angle = t * 2
    size = 15 + int(8 * pulse)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    corners = [
        (60 + cos_a * size - sin_a * size, 60 + sin_a * size + cos_a * size),
        (60 + cos_a * size + sin_a * size, 60 + sin_a * size - cos_a * size),
        (60 - cos_a * size + sin_a * size, 60 - sin_a * size - cos_a * size),
        (60 - cos_a * size - sin_a * size, 60 - sin_a * size + cos_a * size),
    ]
    pygame.draw.polygon(s, (100 + int(155 * pulse), 200, 255), corners)
    pygame.draw.circle(s, (200, 255, 255), (60, 60), 6)


__all__ = ['render_tier2']
