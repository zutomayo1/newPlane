# -*- coding: utf-8 -*-
"""
Eclipse 战机子弹涂装效果渲染模块

包含以下子弹效果：
- dual_core/sync_resonance: 双核心共振
- shadow_eclipse/lunar_devour: 影蚀之月
- corona_burst/eclipse_ring: 日冕爆发
- void_mirror/shadow_clone: 虚空镜像
- twilight_zone/dusk_dawn_edge: 黄昏地带
- dark_matter/invisible_mass: 暗物质弹
- black_sun/anti_radiance: 黑日降临
"""
import pygame
import math


def render_eclipse_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Eclipse战机的子弹效果
    
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
    
    if "dual_core" in effects or "sync_resonance" in effects:
        # 双核心共振：双星系统
        core_offset = size//4
        # 左核心
        left_x = center_x - core_offset
        pygame.draw.circle(surface, (100, 50, 180), (left_x, center_y), size//6)
        pygame.draw.circle(surface, color, (left_x, center_y), size//8)
        # 右核心
        right_x = center_x + core_offset
        pygame.draw.circle(surface, (150, 80, 220), (right_x, center_y), size//6)
        pygame.draw.circle(surface, color, (right_x, center_y), size//8)
        # 共振波（连接线）
        resonance_width = int(3 + 2 * math.sin(pygame.time.get_ticks() / 80))
        pygame.draw.line(surface, (200, 100, 255), (left_x, center_y), (right_x, center_y), resonance_width)
        # 能量环
        for i in range(2):
            ring_r = size//3 + i * size//8
            alpha = 180 - i * 60
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (size, size), ring_r, 2)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "shadow_eclipse" in effects or "lunar_devour" in effects:
        # 影蚀之月：月影吞噬
        # 月盘
        pygame.draw.circle(surface, (180, 180, 200), (center_x, center_y), size//3)
        # 影子侵蚀（半圆）
        eclipse_phase = (math.sin(pygame.time.get_ticks() / 100) + 1) / 2
        shadow_offset = int(size//3 * eclipse_phase)
        shadow_x = center_x - shadow_offset
        pygame.draw.circle(surface, (30, 20, 50), (shadow_x, center_y), size//3)
        # 边缘光晕
        pygame.draw.circle(surface, color, (center_x, center_y), size//3, 3)
        # 日冕效果
        for i in range(8):
            angle = (i * 45) * 3.14159 / 180
            x1 = center_x + int(size//3 * math.cos(angle))
            y1 = center_y + int(size//3 * math.sin(angle))
            x2 = center_x + int(size//2 * math.cos(angle))
            y2 = center_y + int(size//2 * math.sin(angle))
            pygame.draw.line(surface, (120, 80, 160), (x1, y1), (x2, y2), 2)
        return True
    
    elif "corona_burst" in effects or "eclipse_ring" in effects:
        # 日冕爆发：日食边缘
        # 日食主体
        pygame.draw.circle(surface, (50, 30, 80), (center_x, center_y), size//4)
        # 日冕环（3层）
        for i in range(3):
            ring_r = size//3 + i * size//8
            ring_color = (100 + i * 30, 50 + i * 20, 180 + i * 20)
            alpha = 200 - i * 50
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*ring_color, alpha), (size, size), ring_r, 3)
            surface.blit(temp_surf, (x - size, y - size))
        # 爆发射线（12条）
        for i in range(12):
            angle = (i * 30 + pygame.time.get_ticks() / 50) * 3.14159 / 180
            length = size//3 if i % 2 == 0 else size//2
            x1 = center_x + int(size//4 * math.cos(angle))
            y1 = center_y + int(size//4 * math.sin(angle))
            x2 = center_x + int(length * math.cos(angle))
            y2 = center_y + int(length * math.sin(angle))
            pygame.draw.line(surface, (200, 100, 255), (x1, y1), (x2, y2), 2)
        return True
    
    elif "void_mirror" in effects or "shadow_clone" in effects:
        # 虚空镜像：影子复制
        # 主体
        pygame.draw.circle(surface, color, (center_x, center_y), size//5)
        pygame.draw.circle(surface, (150, 100, 200), (center_x, center_y), size//6)
        # 镜像（4个方向）
        mirror_offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        for i, (dx, dy) in enumerate(mirror_offsets):
            mirror_x = center_x + dx * size//3
            mirror_y = center_y + dy * size//3
            alpha = 150 - i * 20
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (mirror_x - x + size, mirror_y - y + size), size//8)
            surface.blit(temp_surf, (x - size, y - size))
        # 连接线
        for dx, dy in mirror_offsets:
            mirror_x = center_x + dx * size//3
            mirror_y = center_y + dy * size//3
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.line(temp_surf, (*color, 100), 
                           (center_x - x + size, center_y - y + size),
                           (mirror_x - x + size, mirror_y - y + size), 1)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "twilight_zone" in effects or "dusk_dawn_edge" in effects:
        # 黄昏地带：光暗边缘
        # 渐变背景（从亮到暗）
        for i in range(20):
            gradient_y = center_y - size//2 + i * size//10
            brightness = 200 - i * 10
            gradient_color = (brightness, brightness//2, brightness + 55)
            pygame.draw.line(surface, gradient_color, 
                           (center_x - size//2, gradient_y),
                           (center_x + size//2, gradient_y), size//10)
        # 边界线
        pygame.draw.line(surface, color, (center_x - size//2, center_y), (center_x + size//2, center_y), 4)
        # 光暗粒子
        for i in range(6):
            angle = (i * 60) * 3.14159 / 180
            px = center_x + int(size//3 * math.cos(angle))
            py = center_y + int(size//3 * math.sin(angle))
            particle_color = (200, 150, 250) if py < center_y else (50, 30, 100)
            pygame.draw.circle(surface, particle_color, (px, py), size//18)
        return True
    
    elif "dark_matter" in effects or "invisible_mass" in effects:
        # 暗物质弹：不可见质量
        # 扭曲空间（波纹）
        for i in range(4):
            wave_r = size//6 + i * size//10
            alpha = 150 - i * 30
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (size, size), wave_r, 2)
            surface.blit(temp_surf, (x - size, y - size))
        # 暗物质核心（几乎不可见）
        pygame.draw.circle(surface, (50, 20, 100), (center_x, center_y), size//8)
        temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surf, (*color, 100), (size, size), size//6)
        surface.blit(temp_surf, (x - size, y - size))
        # 引力扭曲线
        for i in range(8):
            angle = (i * 45 + pygame.time.get_ticks() / 60) * 3.14159 / 180
            x1 = center_x + int(size//4 * math.cos(angle))
            y1 = center_y + int(size//4 * math.sin(angle))
            x2 = center_x + int(size//2 * math.cos(angle + 0.3))
            y2 = center_y + int(size//2 * math.sin(angle + 0.3))
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.line(temp_surf, (*color, 120), 
                           (x1 - x + size, y1 - y + size),
                           (x2 - x + size, y2 - y + size), 1)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "black_sun" in effects or "anti_radiance" in effects:
        # 黑日降临：黑色太阳
        # 黑色核心
        pygame.draw.circle(surface, (20, 10, 30), (center_x, center_y), size//4)
        pygame.draw.circle(surface, color, (center_x, center_y), size//5)
        # 反光环（黑色光晕）
        for i in range(3):
            halo_r = size//3 + i * size//8
            alpha = 180 - i * 50
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (50, 20, 80, alpha), (size, size), halo_r, 4)
            surface.blit(temp_surf, (x - size, y - size))
        # 反向射线（吸收光线）
        for i in range(16):
            angle = (i * 22.5) * 3.14159 / 180
            x1 = center_x + int(size//2 * math.cos(angle))
            y1 = center_y + int(size//2 * math.sin(angle))
            x2 = center_x + int(size//4 * math.cos(angle))
            y2 = center_y + int(size//4 * math.sin(angle))
            # 从外向内绘制
            pygame.draw.line(surface, (80, 30, 120), (x1, y1), (x2, y2), 2)
        # 暗能量粒子
        for i in range(8):
            angle = (i * 45 + pygame.time.get_ticks() / 40) * 3.14159 / 180
            px = center_x + int(size//2.5 * math.cos(angle))
            py = center_y + int(size//2.5 * math.sin(angle))
            pygame.draw.circle(surface, (100, 30, 150), (px, py), size//20)
        return True
    
    return False
