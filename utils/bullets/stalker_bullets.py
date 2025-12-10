# -*- coding: utf-8 -*-
"""
Stalker 战机子弹涂装效果渲染模块

包含以下子弹效果：
- plasma_disc/heat_trail: 铁血飞盘（捕食者）
- acid_drop/corrosive: 异形酸液（异形）（注意检查顺序）
- color_shift/stealth_flicker: 变色迷彩（变色龙）
- spore_burst/swarm_split: 虫群孢子（虫群）
- drone_tracking/scanner_lock: 追踪无人机（无人机）
- void_phase/dimension_shift: 虚空潜行（虚空）
- xenomorph_egg/hive_spawn: 异形卵巢（异形母体）
"""
import pygame
import math
import random


def render_stalker_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Stalker战机的子弹效果
    
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
    
    if "plasma_disc" in effects or "heat_trail" in effects:
        # 铁血飞盘：旋转飞盘+等离子
        # 飞盘主体（圆形+锯齿边）
        pygame.draw.circle(surface, (180, 0, 220), (center_x, center_y), size//3)
        # 锯齿边缘（8个三角）
        for i in range(8):
            angle = (i * 45 + pygame.time.get_ticks() / 20) * 3.14159 / 180
            x1 = center_x + int(size//3 * math.cos(angle))
            y1 = center_y + int(size//3 * math.sin(angle))
            x2 = center_x + int(size//2 * math.cos(angle))
            y2 = center_y + int(size//2 * math.sin(angle))
            # 三角锯齿
            angle_left = angle - 0.3
            angle_right = angle + 0.3
            p1 = (x1 + int(size//8 * math.cos(angle_left)), y1 + int(size//8 * math.sin(angle_left)))
            p2 = (x1 + int(size//8 * math.cos(angle_right)), y1 + int(size//8 * math.sin(angle_right)))
            pygame.draw.polygon(surface, color, [(x2, y2), p1, p2])
        # 中心等离子核
        pygame.draw.circle(surface, (255, 0, 255), (center_x, center_y), size//6)
        # 热能轨迹
        for i in range(3):
            trail_radius = size//3 + i * size//8
            alpha = 180 - i * 50
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (size, size), trail_radius, 2)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "color_shift" in effects or "stealth_flicker" in effects:
        # 变色迷彩：色彩变换效果
        # 主体（渐变色圆形）
        shift_colors = [(120, 180, 120), (80, 140, 180), (140, 120, 160), (100, 160, 100)]
        time_index = int(pygame.time.get_ticks() / 200) % len(shift_colors)
        current_color = shift_colors[time_index]
        # 多层渐变
        for i in range(4):
            radius = size//2 - i * size//10
            alpha = 220 - i * 40
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            blend_color = tuple(int(c * (1 - i * 0.2)) for c in current_color)
            pygame.draw.circle(temp_surf, (*blend_color, alpha), (size, size), radius)
            surface.blit(temp_surf, (x - size, y - size))
        # 隐形闪烁边缘
        for i in range(6):
            angle = (i * 60 + pygame.time.get_ticks() / 50) * 3.14159 / 180
            px = center_x + int(size//2.5 * math.cos(angle))
            py = center_y + int(size//2.5 * math.sin(angle))
            alpha = int(200 * abs(math.sin(pygame.time.get_ticks() / 100 + i)))
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*current_color, alpha), (px - x + size, py - y + size), size//15)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "spore_burst" in effects or "swarm_split" in effects:
        # 虫群孢子：孢子扩散
        # 主孢子囊
        pygame.draw.circle(surface, (100, 140, 60), (center_x, center_y), size//4)
        pygame.draw.circle(surface, color, (center_x, center_y), size//4, 2)
        # 裂变纹理
        for i in range(6):
            angle = (i * 60) * 3.14159 / 180
            x1 = center_x
            y1 = center_y
            x2 = center_x + int(size//4 * math.cos(angle))
            y2 = center_y + int(size//4 * math.sin(angle))
            pygame.draw.line(surface, (60, 100, 30), (x1, y1), (x2, y2), 2)
        # 扩散孢子（12个小孢子）
        for i in range(12):
            angle = (i * 30 + pygame.time.get_ticks() / 50) * 3.14159 / 180
            radius = size//2 + int(size//8 * math.sin(pygame.time.get_ticks() / 100 + i))
            spore_x = center_x + int(radius * math.cos(angle))
            spore_y = center_y + int(radius * math.sin(angle))
            spore_size = size // 20
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, 180), (spore_x - x + size, spore_y - y + size), spore_size)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "drone_tracking" in effects or "scanner_lock" in effects:
        # 追踪无人机：机械无人机形状
        # 无人机主体（十字形）
        # 横臂
        pygame.draw.rect(surface, (220, 170, 0), 
                       (center_x - size//2, center_y - size//12, size, size//6))
        # 竖臂
        pygame.draw.rect(surface, (220, 170, 0), 
                       (center_x - size//12, center_y - size//2, size//6, size))
        # 中心核心
        pygame.draw.circle(surface, (255, 200, 0), (center_x, center_y), size//6)
        pygame.draw.circle(surface, (200, 150, 0), (center_x, center_y), size//8)
        # 四个旋翼（圆圈）
        for i in range(4):
            angle = (i * 90) * 3.14159 / 180
            rotor_x = center_x + int(size//2.5 * math.cos(angle))
            rotor_y = center_y + int(size//2.5 * math.sin(angle))
            pygame.draw.circle(surface, (180, 140, 0), (rotor_x, rotor_y), size//10, 2)
        # 扫描锁定线
        scan_angle = (pygame.time.get_ticks() / 20) * 3.14159 / 180
        x1 = center_x + int(size//6 * math.cos(scan_angle))
        y1 = center_y + int(size//6 * math.sin(scan_angle))
        x2 = center_x + int(size//1.8 * math.cos(scan_angle))
        y2 = center_y + int(size//1.8 * math.sin(scan_angle))
        pygame.draw.line(surface, (255, 0, 0), (x1, y1), (x2, y2), 2)
        return True
    
    elif "void_phase" in effects or "dimension_shift" in effects:
        # 虚空潜行：次元裂隙
        # 虚空裂隙（不规则裂痕）
        rift_points = [
            (center_x, center_y - size//2),
            (center_x - size//8, center_y - size//4),
            (center_x + size//10, center_y),
            (center_x - size//12, center_y + size//4),
            (center_x, center_y + size//2)
        ]
        pygame.draw.lines(surface, (150, 0, 200), False, rift_points, 4)
        pygame.draw.lines(surface, (200, 100, 255), False, rift_points, 2)
        # 虚空漩涡
        for i in range(4):
            radius = size//4 + i * size//10
            alpha = 180 - i * 40
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (size, size), radius, 2)
            surface.blit(temp_surf, (x - size, y - size))
        # 次元碎片
        for i in range(6):
            angle = (i * 60) * 3.14159 / 180
            shard_x = center_x + int(size//3 * math.cos(angle))
            shard_y = center_y + int(size//3 * math.sin(angle))
            shard = [
                (shard_x, shard_y - size//15),
                (shard_x + size//20, shard_y + size//15),
                (shard_x - size//20, shard_y + size//15)
            ]
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.polygon(temp_surf, (*color, 200), 
                              [(px - center_x + size, py - center_y + size) for px, py in shard])
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "xenomorph_egg" in effects or "hive_spawn" in effects:
        # 异形卵巢：卵形+触手
        # 卵体（椭圆）
        egg_rect = pygame.Rect(center_x - size//3, center_y - size//2, size*2//3, size)
        temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.ellipse(temp_surf, (*color, 220), 
                          (egg_rect.x - x + size, egg_rect.y - y + size, egg_rect.width, egg_rect.height))
        surface.blit(temp_surf, (x - size, y - size))
        pygame.draw.ellipse(surface, (60, 140, 60), egg_rect, 3)
        # 卵纹理（竖线）
        for i in range(5):
            line_x = center_x - size//4 + i * size//8
            pygame.draw.line(surface, (40, 100, 40), 
                           (line_x, center_y - size//2), 
                           (line_x, center_y + size//2), 1)
        # 顶部裂口（张开）
        opening = [
            (center_x - size//6, center_y - size//2),
            (center_x - size//4, center_y - size//1.5),
            (center_x, center_y - size//1.8),
            (center_x + size//4, center_y - size//1.5),
            (center_x + size//6, center_y - size//2)
        ]
        pygame.draw.lines(surface, (80, 180, 80), False, opening, 2)
        # 触手（4条）
        for i in range(4):
            angle = (i * 90 + 45) * 3.14159 / 180
            tentacle = []
            for j in range(5):
                radius = size//3 + j * size//15
                wave_offset = int(size//20 * math.sin(pygame.time.get_ticks() / 100 + i + j))
                tx = center_x + int(radius * math.cos(angle)) + wave_offset
                ty = center_y + int(radius * math.sin(angle))
                tentacle.append((tx, ty))
            if len(tentacle) > 1:
                pygame.draw.lines(surface, (60, 120, 60), False, tentacle, 2)
        return True
    
    return False
