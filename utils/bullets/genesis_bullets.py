# -*- coding: utf-8 -*-
"""
Genesis 战机子弹涂装效果渲染模块

包含以下子弹效果：
- genesis_star: 创世之星（基础）
- cosmic_origin: 宇宙起源
- solar_birth: 太阳诞生
- nebula_seed: 星云种子
- void_creation: 虚无创生
- life_spark: 生命火花
- crystal_shard: 水晶碎片
- chaos_burst: 混沌爆发
"""
import pygame
import math


def render_genesis_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Genesis战机的子弹效果
    
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
    t = pygame.time.get_ticks() / 1000.0
    
    if "genesis_star" in effects or "cosmic_origin" in effects:
        # 创世之星 - 宇宙大爆炸扩散
        cosmic_gold = (255, 200, 100)
        star_white = (255, 255, 255)
        
        # 扩散环
        for ring in range(4):
            ring_r = size // 6 + ring * (size // 10) + int(3 * math.sin(t * 5 - ring * 0.5))
            ring_alpha = 200 - ring * 40
            
            ring_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            ring_color = (
                int(255 - ring * 15),
                int(200 - ring * 25),
                int(100 + ring * 20)
            )
            pygame.draw.circle(ring_surf, (*ring_color, ring_alpha), (size, size), ring_r, 2)
            surface.blit(ring_surf, (x - size // 2, y - size // 2))
        
        # 轨道粒子
        for planet in range(6):
            p_angle = (planet * 60 + t * 120) * math.pi / 180
            p_r = size // 3
            px = center_x + int(math.cos(p_angle) * p_r)
            py = center_y + int(math.sin(p_angle) * p_r * 0.6)
            
            planet_colors = [
                (255, 100, 100), (255, 200, 100), (100, 255, 100),
                (100, 200, 255), (150, 100, 255), (255, 100, 200)
            ]
            pygame.draw.circle(surface, planet_colors[planet], (px, py), 2)
        
        # 中心核心
        pygame.draw.circle(surface, cosmic_gold, (center_x, center_y), size // 5)
        pygame.draw.circle(surface, star_white, (center_x, center_y), size // 8)
        return True
    
    elif "solar_birth" in effects:
        # 太阳诞生 - 金红炽焰
        solar_gold = (255, 200, 50)
        solar_orange = (255, 150, 0)
        
        # 耀斑
        for flare in range(8):
            flare_angle = (flare * 45 + t * 80) * math.pi / 180
            flare_len = size // 3 + int(abs(math.sin(t * 10 + flare)) * (size // 6))
            fx = center_x + int(math.cos(flare_angle) * flare_len)
            fy = center_y + int(math.sin(flare_angle) * flare_len)
            
            pygame.draw.line(surface, solar_gold, (center_x, center_y), (fx, fy), 2)
            pygame.draw.circle(surface, solar_orange, (fx, fy), 2)
        
        # 日冕
        pygame.draw.circle(surface, solar_orange, (center_x, center_y), size // 4)
        pygame.draw.circle(surface, solar_gold, (center_x, center_y), size // 6)
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size // 10)
        return True
    
    elif "nebula_seed" in effects:
        # 星云种子 - 紫粉梦幻
        nebula_purple = (180, 100, 255)
        nebula_pink = (255, 150, 200)
        
        # 星云层
        for layer in range(3):
            layer_offset = t * 30 * (1 if layer % 2 == 0 else -1)
            
            nebula_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            for blob in range(4):
                blob_angle = (blob * 90 + layer_offset) * math.pi / 180
                blob_r = size // 4 + layer * (size // 12)
                bx = size + int(math.cos(blob_angle) * blob_r)
                by = size + int(math.sin(blob_angle) * blob_r)
                
                colors = [nebula_purple, nebula_pink, (150, 180, 255)]
                blob_alpha = 100 - layer * 25
                pygame.draw.circle(nebula_surf, (*colors[(layer + blob) % 3], blob_alpha), (bx, by), size // 8)
            surface.blit(nebula_surf, (x - size // 2, y - size // 2))
        
        # 中心原恒星
        pygame.draw.circle(surface, nebula_purple, (center_x, center_y), size // 6)
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size // 12)
        return True
    
    elif "void_creation" in effects:
        # 虚无创生 - 黑白太极
        pure_white = (255, 255, 255)
        pure_black = (0, 0, 0)
        gray = (128, 128, 128)
        
        rotation = t * 100
        
        # 太极圆
        pygame.draw.circle(surface, gray, (center_x, center_y), size // 3, 2)
        
        # 白半圆
        white_points = [(center_x, center_y)]
        for i in range(181):
            angle = (i + rotation) * math.pi / 180
            white_points.append((
                center_x + int(math.cos(angle) * (size // 3 - 2)),
                center_y + int(math.sin(angle) * (size // 3 - 2))
            ))
        if len(white_points) > 2:
            pygame.draw.polygon(surface, pure_white, white_points)
        
        # 黑半圆
        black_points = [(center_x, center_y)]
        for i in range(181):
            angle = (i + 180 + rotation) * math.pi / 180
            black_points.append((
                center_x + int(math.cos(angle) * (size // 3 - 2)),
                center_y + int(math.sin(angle) * (size // 3 - 2))
            ))
        if len(black_points) > 2:
            pygame.draw.polygon(surface, pure_black, black_points)
        
        # 鱼眼
        white_eye_angle = (90 + rotation) * math.pi / 180
        black_eye_angle = (270 + rotation) * math.pi / 180
        eye_r = size // 6
        
        white_ex = center_x + int(math.cos(white_eye_angle) * eye_r)
        white_ey = center_y + int(math.sin(white_eye_angle) * eye_r)
        black_ex = center_x + int(math.cos(black_eye_angle) * eye_r)
        black_ey = center_y + int(math.sin(black_eye_angle) * eye_r)
        
        pygame.draw.circle(surface, pure_white, (white_ex, white_ey), size // 12)
        pygame.draw.circle(surface, pure_black, (white_ex, white_ey), size // 24)
        pygame.draw.circle(surface, pure_black, (black_ex, black_ey), size // 12)
        pygame.draw.circle(surface, pure_white, (black_ex, black_ey), size // 24)
        return True
    
    elif "life_spark" in effects:
        # 生命火花 - DNA螺旋
        life_green = (50, 200, 100)
        gold = (255, 215, 100)
        
        # DNA 螺旋
        for helix in range(2):
            helix_offset = helix * math.pi
            
            for i in range(10):
                progress = i / 10
                angle = progress * math.pi * 2 + t * 8 + helix_offset
                hx = center_x + int(math.cos(angle) * (size // 8))
                hy = center_y - size // 3 + int(progress * (size * 2 // 3))
                
                helix_color = life_green if helix == 0 else gold
                pygame.draw.circle(surface, helix_color, (hx, hy), 2)
        
        # 中心
        pygame.draw.circle(surface, gold, (center_x, center_y), size // 6)
        pygame.draw.circle(surface, life_green, (center_x, center_y), size // 10)
        return True
    
    elif "crystal_shard" in effects:
        # 水晶碎片 - 六边形
        crystal_blue = (150, 220, 255)
        ice_white = (220, 240, 255)
        
        # 主晶体
        hex_points = []
        for i in range(6):
            angle = (i * 60 + 30) * math.pi / 180
            r = size // 3
            hx = center_x + int(math.cos(angle) * r)
            hy = center_y + int(math.sin(angle) * r)
            hex_points.append((hx, hy))
        
        hex_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        offset_points = [(p[0] - x + size // 2, p[1] - y + size // 2) for p in hex_points]
        pygame.draw.polygon(hex_surf, (*crystal_blue, 180), offset_points)
        pygame.draw.polygon(hex_surf, ice_white, offset_points, 2)
        surface.blit(hex_surf, (x - size // 2, y - size // 2))
        
        # 折射线
        for i in range(6):
            pygame.draw.line(surface, (*ice_white, 150), (center_x, center_y), hex_points[i], 1)
        
        # 中心
        pygame.draw.circle(surface, ice_white, (center_x, center_y), size // 8)
        return True
    
    elif "chaos_burst" in effects:
        # 混沌爆发 - 多彩混乱
        chaos_colors = [
            (255, 50, 50), (255, 150, 50), (255, 255, 50),
            (50, 255, 50), (50, 255, 255), (50, 50, 255), (255, 50, 255)
        ]
        
        # 混沌能量
        for burst in range(10):
            burst_angle = (burst * 36 + t * 150) * math.pi / 180
            burst_len = size // 4 + int(abs(math.sin(t * 12 + burst)) * (size // 6))
            bx = center_x + int(math.cos(burst_angle) * burst_len)
            by = center_y + int(math.sin(burst_angle) * burst_len)
            
            burst_color = chaos_colors[burst % 7]
            pygame.draw.line(surface, burst_color, (center_x, center_y), (bx, by), 2)
        
        # 混沌核心
        core_color_idx = int(t * 10) % 7
        pygame.draw.circle(surface, chaos_colors[core_color_idx], (center_x, center_y), size // 5)
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size // 10)
        return True
    
    return False


__all__ = ['render_genesis_bullet']
