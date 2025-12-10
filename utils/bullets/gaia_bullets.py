# -*- coding: utf-8 -*-
"""
Gaia 战机子弹涂装效果渲染模块

包含以下子弹效果：
- seed_spiral/leaf_swirl: 森林之种（森林）
- crystal_facet/gem_sparkle: 水晶宝石（水晶）
- vine_coil/thorn_barb: 荆棘藤蔓（藤蔓）
- petal_storm/bloom_burst: 花瓣风暴（鲜花）
- rock_boulder/earth_crack: 大地之石（大地）
- mushroom_cap/spore_cloud: 魔法蘑菇（蘑菇）
- tree_rings/ancient_runes: 古树之心（远古）
"""
import pygame
import math
import random


def render_gaia_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Gaia战机的子弹效果
    
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
    
    if "seed_spiral" in effects or "leaf_swirl" in effects:
        # 森林之种：种子螺旋+叶片
        # 种子核心
        pygame.draw.circle(surface, (100, 200, 100), (center_x, center_y), size//6)
        pygame.draw.circle(surface, color, (center_x, center_y), size//8)
        # 螺旋叶片（8片）
        for i in range(8):
            angle = (i * 45 + pygame.time.get_ticks() / 30) * 3.14159 / 180
            leaf_x = center_x + int(size//3 * math.cos(angle))
            leaf_y = center_y + int(size//3 * math.sin(angle))
            # 叶片形状（椭圆）
            leaf_rect = pygame.Rect(leaf_x - size//10, leaf_y - size//6, size//5, size//3)
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.ellipse(temp_surf, (*color, 200), 
                              (leaf_rect.x - x + size, leaf_rect.y - y + size, leaf_rect.width, leaf_rect.height))
            surface.blit(temp_surf, (x - size, y - size))
            pygame.draw.ellipse(surface, (100, 220, 100), leaf_rect, 1)
        return True
    
    elif "crystal_facet" in effects or "gem_sparkle" in effects:
        # 水晶宝石：多面晶体
        # 主晶体（六边形）
        crystal_points = []
        for i in range(6):
            angle = (i * 60) * 3.14159 / 180
            px = center_x + int(size//2 * math.cos(angle))
            py = center_y + int(size//2 * math.sin(angle))
            crystal_points.append((px, py))
        temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.polygon(temp_surf, (*color, 200), 
                          [(px - center_x + size, py - center_y + size) for px, py in crystal_points])
        surface.blit(temp_surf, (x - size, y - size))
        pygame.draw.polygon(surface, (0, 255, 220), crystal_points, 2)
        # 内部切面
        for i in range(6):
            angle = (i * 60) * 3.14159 / 180
            x1 = center_x
            y1 = center_y
            x2 = center_x + int(size//2 * math.cos(angle))
            y2 = center_y + int(size//2 * math.sin(angle))
            pygame.draw.line(surface, (0, 220, 200), (x1, y1), (x2, y2), 1)
        # 宝石闪光
        for i in range(4):
            angle = (i * 90 + pygame.time.get_ticks() / 50) * 3.14159 / 180
            sparkle_x = center_x + int(size//3 * math.cos(angle))
            sparkle_y = center_y + int(size//3 * math.sin(angle))
            pygame.draw.circle(surface, (255, 255, 255), (sparkle_x, sparkle_y), size//20)
        return True
    
    elif "vine_coil" in effects or "thorn_barb" in effects:
        # 荆棘藤蔓：盘绕藤蔓+尖刺
        # 藤蔓主体（螺旋）
        vine_points = []
        for i in range(20):
            angle = (i * 18) * 3.14159 / 180
            radius = size//6 + (i / 20) * size//3
            vx = center_x + int(radius * math.cos(angle))
            vy = center_y + int(radius * math.sin(angle))
            vine_points.append((vx, vy))
        if len(vine_points) > 1:
            pygame.draw.lines(surface, (120, 160, 60), False, vine_points, 4)
            pygame.draw.lines(surface, color, False, vine_points, 2)
        # 荆棘刺（沿藤蔓）
        for i in range(0, len(vine_points), 4):
            if i < len(vine_points):
                vx, vy = vine_points[i]
                # 计算刺的方向
                if i < len(vine_points) - 1:
                    next_x, next_y = vine_points[i + 1]
                    perp_angle = math.atan2(next_y - vy, next_x - vx) + 1.5708
                else:
                    perp_angle = 0
                thorn_x = vx + int(size//8 * math.cos(perp_angle))
                thorn_y = vy + int(size//8 * math.sin(perp_angle))
                # 刺（三角形）
                thorn = [
                    (thorn_x, thorn_y),
                    (vx + int(size//15 * math.cos(perp_angle + 0.5)), vy + int(size//15 * math.sin(perp_angle + 0.5))),
                    (vx + int(size//15 * math.cos(perp_angle - 0.5)), vy + int(size//15 * math.sin(perp_angle - 0.5)))
                ]
                pygame.draw.polygon(surface, (140, 180, 70), thorn)
        return True
    
    elif "petal_storm" in effects or "bloom_burst" in effects:
        # 花瓣风暴：飞舞花瓣
        # 花心
        pygame.draw.circle(surface, (255, 200, 0), (center_x, center_y), size//8)
        # 飞舞花瓣（12片）
        for i in range(12):
            angle = (i * 30 + pygame.time.get_ticks() / 40) * 3.14159 / 180
            radius = size//4 + int(size//6 * math.sin(pygame.time.get_ticks() / 80 + i))
            petal_x = center_x + int(radius * math.cos(angle))
            petal_y = center_y + int(radius * math.sin(angle))
            # 花瓣（椭圆）
            petal_rect = pygame.Rect(petal_x - size//12, petal_y - size//8, size//6, size//4)
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.ellipse(temp_surf, (*color, 220), 
                              (petal_rect.x - x + size, petal_rect.y - y + size, petal_rect.width, petal_rect.height))
            surface.blit(temp_surf, (x - size, y - size))
            pygame.draw.ellipse(surface, (255, 180, 220), petal_rect, 1)
        return True
    
    elif "rock_boulder" in effects or "earth_crack" in effects:
        # 大地之石：岩石形状
        # 岩石（不规则多边形）
        rock_points = [
            (center_x, center_y - size//2),
            (center_x + size//3, center_y - size//4),
            (center_x + size//2, center_y + size//6),
            (center_x + size//4, center_y + size//2),
            (center_x - size//4, center_y + size//2),
            (center_x - size//2, center_y + size//6),
            (center_x - size//3, center_y - size//4)
        ]
        pygame.draw.polygon(surface, (140, 120, 80), rock_points)
        pygame.draw.polygon(surface, color, rock_points, 3)
        # 岩石裂纹
        crack_lines = [
            [(center_x - size//6, center_y - size//4), (center_x + size//8, center_y)],
            [(center_x + size//10, center_y - size//6), (center_x - size//12, center_y + size//6)],
            [(center_x - size//8, center_y + size//8), (center_x + size//6, center_y + size//4)]
        ]
        for crack in crack_lines:
            pygame.draw.line(surface, (80, 60, 40), crack[0], crack[1], 2)
        return True
    
    elif "mushroom_cap" in effects or "spore_cloud" in effects:
        # 魔法蘑菇：蘑菇形状+孢子云
        # 蘑菇伞盖（半圆）
        cap_rect = pygame.Rect(center_x - size//2, center_y - size//2, size, size//1.5)
        temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.ellipse(temp_surf, (*color, 220), 
                          (cap_rect.x - x + size, cap_rect.y - y + size, cap_rect.width, cap_rect.height))
        surface.blit(temp_surf, (x - size, y - size))
        pygame.draw.arc(surface, (220, 120, 255), cap_rect, 0, 3.14159, 3)
        # 蘑菇柄
        stalk_rect = (center_x - size//8, center_y, size//4, size//2)
        pygame.draw.rect(surface, (180, 150, 200), stalk_rect)
        # 蘑菇斑点
        random.seed(456)
        for _ in range(6):
            spot_x = center_x + random.randint(-size//3, size//3)
            spot_y = center_y - size//2 + random.randint(0, size//4)
            spot_size = random.randint(size//20, size//12)
            pygame.draw.circle(surface, (255, 200, 255), (spot_x, spot_y), spot_size)
        # 孢子云
        for i in range(8):
            angle = (i * 45) * 3.14159 / 180
            cloud_x = center_x + int(size//1.5 * math.cos(angle))
            cloud_y = center_y + int(size//1.5 * math.sin(angle))
            cloud_size = size // 15
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, 150), (cloud_x - x + size, cloud_y - y + size), cloud_size)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "tree_rings" in effects or "ancient_runes" in effects:
        # 古树之心：年轮+符文
        # 树心（同心圆年轮）
        for i in range(5):
            ring_radius = size//6 + i * size//12
            pygame.draw.circle(surface, (130 - i * 10, 90 - i * 8, 40), (center_x, center_y), ring_radius, 2)
        # 中心
        pygame.draw.circle(surface, (180, 120, 60), (center_x, center_y), size//8)
        # 古代符文（8个符号）
        for i in range(8):
            angle = (i * 45) * 3.14159 / 180
            rune_x = center_x + int(size//2.5 * math.cos(angle))
            rune_y = center_y + int(size//2.5 * math.sin(angle))
            # 简单符文形状（竖线+横线）
            pygame.draw.line(surface, (200, 150, 80), 
                           (rune_x, rune_y - size//15), 
                           (rune_x, rune_y + size//15), 2)
            pygame.draw.line(surface, (200, 150, 80), 
                           (rune_x - size//20, rune_y - size//20), 
                           (rune_x + size//20, rune_y - size//20), 2)
        return True
    
    return False
