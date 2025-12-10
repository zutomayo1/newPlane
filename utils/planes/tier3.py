"""
T3 高级机体渲染

包含 4 种 T3 机体的渲染函数:
- eclipse: 日食幽灵型
- prism: 棱镜分光型
- necro: 死灵骑士型
- wormhole: 虫洞型（基础渲染，涂装在model_styles中）
"""
import pygame
import math

from config import BLACK


def render_tier3(s, pid, c, edge_color, t, pulse, visual):
    """渲染 T3 机体"""
    
    if pid == "eclipse":
        _render_eclipse(s, c, edge_color, t, pulse)
    elif pid == "prism":
        _render_prism(s, c, edge_color, t, pulse)
    elif pid == "necro":
        _render_necro(s, c, edge_color, t, pulse)
    elif pid == "wormhole":
        _render_wormhole(s, c, edge_color, t, pulse, visual)


def _render_eclipse(s, c, edge_color, t, pulse):
    """Eclipse - 日食幽灵型：双核心 + 吸收光芒"""
    pygame.draw.circle(s, (30, 20, 50), (40, 60), 28)
    pygame.draw.circle(s, (150, 50, 200), (40, 60), 26)
    pygame.draw.circle(s, (30, 20, 50), (80, 60), 28)
    pygame.draw.circle(s, (150, 50, 200), (80, 60), 26)
    pygame.draw.line(s, (100, 50, 180), (40, 60), (80, 60), 3)
    # 中间连接体
    pygame.draw.rect(s, (100, 50, 180), (52, 54, 16, 12))
    # 动态：吸收光晕脉动
    aura_r = int(32 + 8 * pulse)
    pygame.draw.circle(s, (200, 100, 255), (40, 60), aura_r, 1)
    pygame.draw.circle(s, (200, 100, 255), (80, 60), aura_r, 1)
    # 能量流
    for i in range(3):
        offset = i * 8 - 8
        pygame.draw.line(s, (150 + int(100 * pulse), 50 + int(150 * pulse), 200), 
                        (40, 60 + offset), (80, 60 + offset), 1)


def _render_prism(s, c, edge_color, t, pulse):
    """Prism - 棱镜分光型：三棱柱 + 光谱分解"""
    pygame.draw.polygon(s, (50, 100, 150), [(60, 5), (40, 90), (80, 90)])
    pygame.draw.polygon(s, (0, 255, 200), [(60, 8), (42, 88), (78, 88)])
    pygame.draw.polygon(s, edge_color, [(60, 8), (42, 88), (78, 88)], 2)
    # 三条能量射线
    for angle, color in [(0, (255, 100, 100)), (120, (100, 255, 100)), (240, (100, 100, 255))]:
        rad = math.radians(angle)
        start_x, start_y = 60, 45
        end_x = start_x + math.cos(rad) * 35
        end_y = start_y + math.sin(rad) * 35
        pygame.draw.line(s, color, (int(start_x), int(start_y)), (int(end_x), int(end_y)), 2)
        # 脉动的光点
        pulsing_r = int(3 + 2 * abs(math.sin(t * 4 + angle)))
        pygame.draw.circle(s, color, (int(end_x), int(end_y)), pulsing_r)
    # 中心棱镜
    pygame.draw.circle(s, (150, 200, 255), (60, 45), 8)


def _render_necro(s, c, edge_color, t, pulse):
    """Necro - 死灵骑士型：骷髅头 + 吸血能量"""
    # 头骨主体
    pygame.draw.circle(s, (80, 80, 100), (60, 45), 22)
    pygame.draw.circle(s, (150, 50, 150), (60, 45), 20)
    pygame.draw.rect(s, (80, 80, 100), (45, 55, 30, 30))
    pygame.draw.rect(s, (150, 50, 150), (47, 57, 26, 26))
    # 眼窝
    pygame.draw.circle(s, BLACK, (52, 40), 5)
    pygame.draw.circle(s, BLACK, (68, 40), 5)
    pygame.draw.circle(s, (255, 100, 150), (52, 40), 2)
    pygame.draw.circle(s, (255, 100, 150), (68, 40), 2)
    # 骨架肋部（下半身）
    for i, x in enumerate([45, 60, 75]):
        pygame.draw.line(s, (150, 50, 150), (x, 80), (x - 5, 105), 3)
    # 动态：吸血能量脉冲
    vampire_pulse = int(100 + 155 * pulse)
    pygame.draw.circle(s, (vampire_pulse, 50, 150), (60, 45), 24, 2)
    # 能量流向
    for offset in range(-10, 15, 5):
        pygame.draw.line(s, (200, 50, 150), (40, 60 + offset), (50, 70 + offset), 1)


def _render_wormhole(s, c, edge_color, t, pulse, visual):
    """Wormhole - 虫洞型：基础渲染"""
    # 注意：wormhole有大量涂装在 model_styles 中处理
    # 这里只是基础渲染
    
    # 虫洞漩涡效果
    for i in range(5):
        radius = 45 - i * 8
        alpha = 150 - i * 25
        color = (100 + i * 20, 50 + i * 30, 200 - i * 20)
        pygame.draw.circle(s, color, (60, 60), radius, 2)
    
    # 中心奇点
    core_size = int(8 + 4 * pulse)
    pygame.draw.circle(s, (200, 100, 255), (60, 60), core_size)
    pygame.draw.circle(s, (255, 200, 255), (60, 60), core_size - 3)
    
    # 旋转粒子
    for i in range(6):
        angle = t * 3 + i * math.pi / 3
        dist = 30 + 5 * math.sin(t * 5 + i)
        px = 60 + math.cos(angle) * dist
        py = 60 + math.sin(angle) * dist
        pygame.draw.circle(s, (180, 100, 220), (int(px), int(py)), 3)


__all__ = ['render_tier3']
