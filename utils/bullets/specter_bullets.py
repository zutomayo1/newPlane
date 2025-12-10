# -*- coding: utf-8 -*-
"""
Specter 战机子弹涂装效果渲染模块

包含以下子弹效果：
- scythe_blade: 死神镰刀（死神）
- shadow_dagger: 暗影匕首（刺客）
- wraith_chain: 怨灵锁链（怨灵）
- sniper_round: 狙击弹（狙击）
- poltergeist_cube: 灵异魔方（灵异）
- fallen_wing: 堕落天使（天使）
- void_rift: 虚空裂缝（虚空猎手）
"""
import pygame
import math


def render_specter_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Specter战机的子弹效果
    
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
    
    if "scythe_blade" in effects:
        # 死神镰刀：弯月形刀刃
        # 镰刀柄
        handle_start = (center_x, center_y + size//3)
        handle_end = (center_x, center_y + size//2)
        pygame.draw.line(surface, (80, 80, 80), handle_start, handle_end, 5)
        # 弯月刀刃（弧形）
        blade_rect = pygame.Rect(center_x - size//2, center_y - size//2, size, size)
        pygame.draw.arc(surface, color, blade_rect, 0, 3.14159, 5)
        pygame.draw.arc(surface, (200, 100, 255), blade_rect, 0, 3.14159, 2)
        # 刀尖
        tip_points = [
            (center_x - size//2, center_y),
            (center_x - size//2 - size//8, center_y - size//12),
            (center_x - size//2, center_y - size//6)
        ]
        pygame.draw.polygon(surface, color, tip_points)
        return True
    
    elif "shadow_dagger" in effects:
        # 暗影匕首：尖锐短刃
        # 刀刃（菱形）
        blade = [
            (center_x, center_y - size//2),
            (center_x + size//8, center_y),
            (center_x, center_y + size//4),
            (center_x - size//8, center_y)
        ]
        pygame.draw.polygon(surface, (100, 100, 150), blade)
        pygame.draw.polygon(surface, color, blade, 2)
        # 刀柄
        handle_rect = (center_x - size//12, center_y + size//4, size//6, size//4)
        pygame.draw.rect(surface, (50, 50, 80), handle_rect)
        # 暗影效果
        temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        for i in range(3):
            offset = i * 3
            shadow_blade = [(px + offset, py) for px, py in blade]
            pygame.draw.polygon(temp_surf, (*color, 80 - i*20), 
                              [(px - center_x + size, py - center_y + size) for px, py in shadow_blade])
        surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "wraith_chain" in effects:
        # 怨灵锁链：波浪形锁链
        # 锁链链节
        chain_segments = 6
        for i in range(chain_segments):
            y_pos = center_y - size//2 + i * size//6
            wave = int(size//8 * math.sin(pygame.time.get_ticks() / 200 + i))
            # 链环
            link_rect = (center_x - size//10 + wave, y_pos, size//5, size//8)
            pygame.draw.ellipse(surface, color, link_rect, 3)
            # 连接线
            if i < chain_segments - 1:
                next_wave = int(size//8 * math.sin(pygame.time.get_ticks() / 200 + i + 1))
                pygame.draw.line(surface, color, 
                               (center_x + wave, y_pos + size//16),
                               (center_x + next_wave, y_pos + size//6), 2)
        return True
    
    elif "sniper_round" in effects:
        # 狙击弹：流线型子弹
        # 弹头（尖锥）
        tip = [
            (center_x, center_y - size//2),
            (center_x - size//6, center_y - size//4),
            (center_x + size//6, center_y - size//4)
        ]
        pygame.draw.polygon(surface, (200, 200, 220), tip)
        pygame.draw.polygon(surface, color, tip, 2)
        # 弹体（圆柱）
        body_rect = (center_x - size//6, center_y - size//4, size//3, size*2//3)
        pygame.draw.rect(surface, (180, 180, 200), body_rect)
        pygame.draw.rect(surface, color, body_rect, 2)
        # 弹壳纹路
        for i in range(3):
            y_line = center_y - size//8 + i * size//8
            pygame.draw.line(surface, color, 
                           (center_x - size//6, y_line),
                           (center_x + size//6, y_line), 1)
        return True
    
    elif "poltergeist_cube" in effects:
        # 灵异魔方：旋转方块
        # 3D方块效果
        rotation = pygame.time.get_ticks() / 500
        cube_size = size // 3
        # 正面
        front_points = [
            (center_x - cube_size, center_y - cube_size),
            (center_x + cube_size, center_y - cube_size),
            (center_x + cube_size, center_y + cube_size),
            (center_x - cube_size, center_y + cube_size)
        ]
        pygame.draw.polygon(surface, color, front_points)
        pygame.draw.polygon(surface, (255, 255, 255), front_points, 2)
        # 上面（透视）
        top_points = [
            (center_x - cube_size, center_y - cube_size),
            (center_x + cube_size, center_y - cube_size),
            (center_x + cube_size + cube_size//3, center_y - cube_size - cube_size//3),
            (center_x - cube_size + cube_size//3, center_y - cube_size - cube_size//3)
        ]
        pygame.draw.polygon(surface, (*color, 150), top_points)
        pygame.draw.polygon(surface, (200, 150, 255), top_points, 2)
        # 右侧
        side_points = [
            (center_x + cube_size, center_y - cube_size),
            (center_x + cube_size + cube_size//3, center_y - cube_size - cube_size//3),
            (center_x + cube_size + cube_size//3, center_y + cube_size - cube_size//3),
            (center_x + cube_size, center_y + cube_size)
        ]
        pygame.draw.polygon(surface, (*color, 180), side_points)
        pygame.draw.polygon(surface, (220, 180, 255), side_points, 2)
        return True
    
    elif "fallen_wing" in effects:
        # 堕落天使：黑色羽翼
        # 左翼
        for i in range(5):
            feather_x = center_x - size//6 - i * size//8
            feather_y = center_y - size//4 + i * size//10
            feather = [
                (feather_x, feather_y),
                (feather_x - size//10, feather_y + size//6),
                (feather_x + size//15, feather_y + size//8)
            ]
            pygame.draw.polygon(surface, (50, 50, 80), feather)
            pygame.draw.polygon(surface, color, feather, 1)
        # 右翼
        for i in range(5):
            feather_x = center_x + size//6 + i * size//8
            feather_y = center_y - size//4 + i * size//10
            feather = [
                (feather_x, feather_y),
                (feather_x + size//10, feather_y + size//6),
                (feather_x - size//15, feather_y + size//8)
            ]
            pygame.draw.polygon(surface, (50, 50, 80), feather)
            pygame.draw.polygon(surface, color, feather, 1)
        # 中心光晕
        pygame.draw.circle(surface, (150, 150, 200), (center_x, center_y), size//8)
        return True
    
    elif "void_rift" in effects:
        # 虚空裂缝：空间裂痕
        # 主裂缝
        rift_segments = [
            (center_x, center_y - size//2),
            (center_x - size//8, center_y - size//6),
            (center_x + size//10, center_y + size//8),
            (center_x - size//12, center_y + size//3),
            (center_x, center_y + size//2)
        ]
        pygame.draw.lines(surface, (150, 0, 200), False, rift_segments, 4)
        pygame.draw.lines(surface, (200, 100, 255), False, rift_segments, 2)
        # 虚空漩涡
        for r in range(size//2, 0, -size//10):
            alpha = int(150 * (1 - r / (size//2)))
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (size, size), r)
            surface.blit(temp_surf, (x - size, y - size))
        # 空间碎片
        for i in range(4):
            angle = (i * 90) * 3.14159 / 180
            shard_x = center_x + int(size//3 * math.cos(angle))
            shard_y = center_y + int(size//3 * math.sin(angle))
            pygame.draw.polygon(surface, color, [
                (shard_x, shard_y - size//15),
                (shard_x + size//20, shard_y),
                (shard_x, shard_y + size//15),
                (shard_x - size//20, shard_y)
            ])
        return True
    
    return False
