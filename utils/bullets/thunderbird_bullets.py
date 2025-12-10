# -*- coding: utf-8 -*-
"""
Thunderbird 战机子弹涂装效果渲染模块

包含以下子弹效果：
- lightning_bolt: 闪电箭矢（风暴）
- tesla_coil: 特斯拉线圈（电磁）
- feather_shape: 等离子羽毛（等离子）
- aurora_blade: 极光羽刃（极光）
- holy_spear: 女武神之矛（女武神）
- phoenix_plume: 凤凰火羽（凤凰）
- nebula_feather: 星云羽毛（星空）
"""
import pygame
import math
import random


def render_thunderbird_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Thunderbird战机的子弹效果
    
    Args:
        surface: pygame绘图表面
        effects: 效果列表
        color: 主题颜色
        center_x, center_y: 中心坐标
        size: 子弹大小
        x, y: 左上角坐标
    
    Returns:
        bool: 如果渲染了效果返回True，否则False
    """
    
    if "lightning_bolt" in effects:
        # 闪电箭矢：之字形闪电
        segments = [
            (center_x, center_y - size//2),
            (center_x + size//8, center_y - size//4),
            (center_x - size//12, center_y),
            (center_x + size//10, center_y + size//4),
            (center_x, center_y + size//2)
        ]
        pygame.draw.lines(surface, (255, 255, 255), False, segments, 6)
        pygame.draw.lines(surface, color, False, segments, 3)
        # 电弧光晕
        for i in range(3):
            offset = i * 3
            offset_segments = [(px + offset, py) for px, py in segments]
            alpha = 100 - i * 30
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            if len(offset_segments) > 1:
                pygame.draw.lines(temp_surf, (*color, alpha), False, 
                                [(px - center_x + size, py - center_y + size) for px, py in offset_segments], 2)
                surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "tesla_coil" in effects:
        # 特斯拉线圈：螺旋线圈+电弧环
        # 中心核心
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//6)
        pygame.draw.circle(surface, color, (center_x, center_y), size//8)
        # 螺旋线圈
        coil_points = []
        for i in range(20):
            angle = i * 18 * 3.14159 / 180
            radius = size//6 + (i / 20) * size//3
            phase = pygame.time.get_ticks() / 200
            px = center_x + int(radius * math.cos(angle + phase))
            py = center_y + int(radius * math.sin(angle + phase))
            coil_points.append((px, py))
        if len(coil_points) > 1:
            pygame.draw.lines(surface, color, False, coil_points, 3)
        # 电弧环
        for i in range(3):
            arc_radius = size//4 + i * size//8
            pygame.draw.circle(surface, color, (center_x, center_y), arc_radius, 2)
        return True
    
    elif "feather_shape" in effects:
        # 等离子羽毛：羽毛形状
        # 羽轴（中央线）
        pygame.draw.line(surface, (200, 200, 200), 
                       (center_x, center_y - size//2), 
                       (center_x, center_y + size//2), 4)
        # 羽丝（两侧）
        for i in range(8):
            py = center_y - size//2 + i * size//8
            width = int(size//3 * (1 - abs(i - 4) / 4))
            # 左侧羽丝
            pygame.draw.line(surface, color, 
                           (center_x, py), 
                           (center_x - width, py + size//16), 2)
            # 右侧羽丝
            pygame.draw.line(surface, color, 
                           (center_x, py), 
                           (center_x + width, py + size//16), 2)
        # 半透明羽毛轮廓
        temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        feather_outline = [
            (size, size//2),
            (size - size//3, size),
            (size, size*3//2),
            (size + size//3, size)
        ]
        pygame.draw.polygon(temp_surf, (*color, 100), feather_outline)
        surface.blit(temp_surf, (x - size//2, y - size//2))
        return True
    
    elif "aurora_blade" in effects:
        # 极光羽刃：彩虹刀刃
        # 刀刃形状（菱形刀）
        blade = [
            (center_x, center_y - size//2),
            (center_x + size//6, center_y),
            (center_x, center_y + size//2),
            (center_x - size//6, center_y)
        ]
        # 彩虹渐变填充
        colors_gradient = [
            (255, 0, 0), (255, 127, 0), (255, 255, 0),
            (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)
        ]
        for i, grad_color in enumerate(colors_gradient):
            offset = i * 2
            temp_blade = [(px + offset, py) for px, py in blade]
            alpha = 150 - i * 15
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.polygon(temp_surf, (*grad_color, alpha), 
                              [(px - center_x + size, py - center_y + size) for px, py in temp_blade])
            surface.blit(temp_surf, (x - size, y - size))
        pygame.draw.polygon(surface, (255, 255, 255), blade, 2)
        return True
    
    elif "holy_spear" in effects:
        # 女武神之矛：长矛形状
        # 矛杆
        shaft_width = size // 12
        pygame.draw.rect(surface, (180, 160, 140), 
                       (center_x - shaft_width//2, center_y, shaft_width, size//2))
        # 矛尖（三角锥）
        spear_tip = [
            (center_x, center_y - size//2),
            (center_x - size//6, center_y),
            (center_x + size//6, center_y)
        ]
        pygame.draw.polygon(surface, (220, 220, 240), spear_tip)
        pygame.draw.polygon(surface, color, spear_tip, 2)
        # 圣光环绕
        for i in range(3):
            angle = (pygame.time.get_ticks() / 300 + i * 120) * 3.14159 / 180
            glow_x = center_x + int(size//3 * math.cos(angle))
            glow_y = center_y + int(size//3 * math.sin(angle))
            pygame.draw.circle(surface, (255, 255, 200), (glow_x, glow_y), size//15)
        return True
    
    elif "phoenix_plume" in effects:
        # 凤凰火羽：火焰羽毛
        # 羽轴
        pygame.draw.line(surface, (255, 200, 0), 
                       (center_x, center_y - size//2), 
                       (center_x, center_y + size//2), 5)
        # 火焰羽丝
        for i in range(6):
            py = center_y - size//2 + i * size//6
            flame_width = int(size//2.5 * (1 - abs(i - 3) / 3))
            # 左侧火焰
            flame_points_l = [
                (center_x, py),
                (center_x - flame_width//2, py + size//12),
                (center_x - flame_width, py + size//8),
                (center_x - flame_width//2, py + size//10)
            ]
            pygame.draw.polygon(surface, (255, 100, 0), flame_points_l)
            pygame.draw.polygon(surface, (255, 200, 0), flame_points_l, 2)
            # 右侧火焰
            flame_points_r = [
                (center_x, py),
                (center_x + flame_width//2, py + size//12),
                (center_x + flame_width, py + size//8),
                (center_x + flame_width//2, py + size//10)
            ]
            pygame.draw.polygon(surface, (255, 100, 0), flame_points_r)
            pygame.draw.polygon(surface, (255, 200, 0), flame_points_r, 2)
        return True
    
    elif "nebula_feather" in effects:
        # 星云羽毛：星点羽毛
        # 羽轴
        pygame.draw.line(surface, (200, 150, 255), 
                       (center_x, center_y - size//2), 
                       (center_x, center_y + size//2), 3)
        # 羽丝
        for i in range(8):
            py = center_y - size//2 + i * size//8
            width = int(size//3 * (1 - abs(i - 4) / 4))
            pygame.draw.line(surface, color, 
                           (center_x, py), 
                           (center_x - width, py + size//16), 2)
            pygame.draw.line(surface, color, 
                           (center_x, py), 
                           (center_x + width, py + size//16), 2)
        # 星点装饰
        random.seed(123)
        for _ in range(12):
            star_x = center_x + random.randint(-size//3, size//3)
            star_y = center_y + random.randint(-size//2, size//2)
            star_size = random.randint(1, 3)
            pygame.draw.circle(surface, (255, 255, 255), (star_x, star_y), star_size)
        return True
    
    return False
