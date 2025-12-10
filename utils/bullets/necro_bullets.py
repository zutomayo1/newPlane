# -*- coding: utf-8 -*-
"""
Necro 战机子弹涂装效果渲染模块

包含以下子弹效果：
- soul_reaper/death_scythe: 灵魂收割
- blood_curse/vampire_drain: 鲜血诅咒
- bone_spike/skeletal_weapon: 白骨尖刺
- plague_cloud/pestilence_mist: 瘟疫之云
- death_mark/doom_sigil: 死亡印记
- ghost_chain/spectral_shackle: 幽灵锁链
- necrotic_burst/undead_explosion: 死灵爆发
"""
import pygame
import math
import random


def render_necro_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Necro战机的子弹效果
    
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
    
    if "soul_reaper" in effects or "death_scythe" in effects:
        # 灵魂收割：死神镰刀
        # 镰刀刃
        scythe_blade = [
            (center_x - size//6, center_y - size//3),
            (center_x + size//3, center_y - size//6),
            (center_x + size//4, center_y + size//8),
            (center_x - size//4, center_y)
        ]
        pygame.draw.polygon(surface, (200, 200, 220), scythe_blade)
        pygame.draw.polygon(surface, color, scythe_blade, 3)
        # 镰刀柄
        pygame.draw.line(surface, (100, 50, 80), (center_x, center_y), (center_x - size//4, center_y + size//2), 4)
        # 灵魂漩涡
        for i in range(6):
            angle = (i * 60 + pygame.time.get_ticks() / 40) * 3.14159 / 180
            spiral_r = size//4 + int(size//8 * (i / 6))
            sx = center_x + int(spiral_r * math.cos(angle))
            sy = center_y + int(spiral_r * math.sin(angle))
            alpha = 200 - i * 30
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (sx - x + size, sy - y + size), size//20)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "blood_curse" in effects or "vampire_drain" in effects:
        # 鲜血诅咒：吸血魔法
        # 血滴核心
        pygame.draw.circle(surface, (180, 0, 80), (center_x, center_y), size//4)
        pygame.draw.circle(surface, color, (center_x, center_y), size//5)
        # 血滴形状（水滴）
        drop_points = []
        for i in range(16):
            angle = (i * 22.5 - 90) * 3.14159 / 180
            if i < 8:
                radius = size//3
            else:
                radius = size//4 + int(size//8 * math.sin((i - 8) * 0.785))
            px = center_x + int(radius * math.cos(angle))
            py = center_y + int(radius * math.sin(angle))
            drop_points.append((px, py))
        if len(drop_points) > 2:
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            adjusted_points = [(px - x + size, py - y + size) for px, py in drop_points]
            pygame.draw.polygon(temp_surf, (200, 0, 100, 180), adjusted_points)
            surface.blit(temp_surf, (x - size, y - size))
            pygame.draw.lines(surface, color, True, drop_points, 2)
        # 吸血触手
        for i in range(4):
            angle = (i * 90 + pygame.time.get_ticks() / 50) * 3.14159 / 180
            tendril_points = []
            for j in range(6):
                radius = size//5 + j * size//15
                wave = int(size//15 * math.sin(j * 0.8 + pygame.time.get_ticks() / 100))
                tx = center_x + int(radius * math.cos(angle)) + wave
                ty = center_y + int(radius * math.sin(angle))
                tendril_points.append((tx, ty))
            if len(tendril_points) > 1:
                pygame.draw.lines(surface, (150, 0, 70), False, tendril_points, 2)
        return True
    
    elif "bone_spike" in effects or "skeletal_weapon" in effects:
        # 白骨尖刺：骸骨武器
        # 骨刺主体（长三角）
        spike_points = [
            (center_x, center_y - size//2),
            (center_x + size//8, center_y + size//2),
            (center_x - size//8, center_y + size//2)
        ]
        pygame.draw.polygon(surface, (220, 220, 220), spike_points)
        pygame.draw.polygon(surface, color, spike_points, 3)
        # 骨节（横纹）
        for i in range(5):
            node_y = center_y - size//3 + i * size//6
            node_width = size//6 - i * size//40
            pygame.draw.line(surface, (180, 180, 180), 
                           (center_x - node_width, node_y),
                           (center_x + node_width, node_y), 2)
        # 骨刺尖端
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y - size//2), size//12)
        # 周围骨片
        for i in range(4):
            angle = (i * 90 + 45) * 3.14159 / 180
            bx = center_x + int(size//3 * math.cos(angle))
            by = center_y + int(size//3 * math.sin(angle))
            bone_shard = [
                (bx, by - size//10),
                (bx + size//15, by + size//15),
                (bx - size//15, by + size//15)
            ]
            pygame.draw.polygon(surface, (200, 200, 200), bone_shard)
            pygame.draw.polygon(surface, color, bone_shard, 2)
        return True
    
    elif "plague_cloud" in effects or "pestilence_mist" in effects:
        # 瘟疫之云：病毒毒雾
        # 毒雾核心
        pygame.draw.circle(surface, (100, 150, 50), (center_x, center_y), size//5)
        pygame.draw.circle(surface, color, (center_x, center_y), size//6)
        # 毒雾扩散（多层云）
        random.seed(234)
        for i in range(12):
            angle = (i * 30 + random.randint(-15, 15)) * 3.14159 / 180
            cloud_r = size//4 + random.randint(0, size//8)
            cx = center_x + int(cloud_r * math.cos(angle))
            cy = center_y + int(cloud_r * math.sin(angle))
            cloud_size = size//10 + random.randint(0, size//15)
            alpha = 150 - i * 10
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (120, 180, 60, alpha), (cx - x + size, cy - y + size), cloud_size)
            surface.blit(temp_surf, (x - size, y - size))
        # 病毒粒子
        for i in range(8):
            angle = (i * 45 + pygame.time.get_ticks() / 60) * 3.14159 / 180
            px = center_x + int(size//3 * math.cos(angle))
            py = center_y + int(size//3 * math.sin(angle))
            # 病毒形状（十字）
            pygame.draw.line(surface, (80, 120, 40), (px - size//25, py), (px + size//25, py), 2)
            pygame.draw.line(surface, (80, 120, 40), (px, py - size//25), (px, py + size//25), 2)
        return True
    
    elif "death_mark" in effects or "doom_sigil" in effects:
        # 死亡印记：终结符文
        # 符文圆环
        pygame.draw.circle(surface, color, (center_x, center_y), size//3, 3)
        pygame.draw.circle(surface, (150, 0, 100), (center_x, center_y), size//4, 2)
        # 死亡标记（五角星）
        star_points = []
        for i in range(5):
            angle = (i * 72 - 90) * 3.14159 / 180
            px = center_x + int(size//4 * math.cos(angle))
            py = center_y + int(size//4 * math.sin(angle))
            star_points.append((px, py))
        # 绘制五角星（连接间隔点）
        if len(star_points) == 5:
            pygame.draw.line(surface, color, star_points[0], star_points[2], 3)
            pygame.draw.line(surface, color, star_points[2], star_points[4], 3)
            pygame.draw.line(surface, color, star_points[4], star_points[1], 3)
            pygame.draw.line(surface, color, star_points[1], star_points[3], 3)
            pygame.draw.line(surface, color, star_points[3], star_points[0], 3)
        # 符文文字（简化为线条）
        rune_symbols = [
            [(center_x - size//8, center_y - size//2), (center_x + size//8, center_y - size//2)],
            [(center_x - size//2, center_y), (center_x - size//4, center_y)],
            [(center_x + size//4, center_y), (center_x + size//2, center_y)],
            [(center_x, center_y + size//3), (center_x, center_y + size//2)]
        ]
        for line_start, line_end in rune_symbols:
            pygame.draw.line(surface, (180, 50, 120), line_start, line_end, 2)
        return True
    
    elif "ghost_chain" in effects or "spectral_shackle" in effects:
        # 幽灵锁链：灵魂枷锁
        # 锁链中心
        pygame.draw.circle(surface, (120, 80, 150), (center_x, center_y), size//6)
        pygame.draw.circle(surface, color, (center_x, center_y), size//8)
        # 锁链（4条）
        for i in range(4):
            angle = (i * 90) * 3.14159 / 180
            chain_points = []
            for j in range(6):
                radius = size//8 + j * size//15
                # 锁链弧度
                arc_offset = int(size//12 * math.sin(j * 0.6 + pygame.time.get_ticks() / 80))
                cx = center_x + int(radius * math.cos(angle)) + arc_offset * (1 if i % 2 == 0 else -1)
                cy = center_y + int(radius * math.sin(angle))
                chain_points.append((cx, cy))
            if len(chain_points) > 1:
                pygame.draw.lines(surface, (100, 70, 130), False, chain_points, 3)
                # 锁链节点
                for cx, cy in chain_points[::2]:
                    pygame.draw.circle(surface, (150, 100, 180), (cx, cy), size//25)
        # 枷锁环（4个）
        for i in range(4):
            angle = (i * 90 + 45) * 3.14159 / 180
            ring_x = center_x + int(size//2.5 * math.cos(angle))
            ring_y = center_y + int(size//2.5 * math.sin(angle))
            pygame.draw.circle(surface, (140, 90, 160), (ring_x, ring_y), size//15, 2)
        return True
    
    elif "necrotic_burst" in effects or "undead_explosion" in effects:
        # 死灵爆发：腐朽爆炸
        # 死灵核心
        pygame.draw.circle(surface, (180, 50, 120), (center_x, center_y), size//5)
        pygame.draw.circle(surface, color, (center_x, center_y), size//6)
        # 爆发波（3层）
        burst_phase = (pygame.time.get_ticks() / 50) % 100 / 100
        for i in range(3):
            burst_r = int((size//4 + i * size//6) * (1 + burst_phase * 0.6))
            alpha = int((200 - i * 50) * (1 - burst_phase * 0.7))
            burst_colors = [(150, 0, 100), (180, 50, 120), (200, 80, 140)]
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*burst_colors[i], alpha), (size, size), burst_r, 3)
            surface.blit(temp_surf, (x - size, y - size))
        # 死灵能量（8个骷髅头简化形状）
        for i in range(8):
            angle = (i * 45 + burst_phase * 360) * 3.14159 / 180
            skull_r = size//3 + int(burst_phase * size//3)
            sx = center_x + int(skull_r * math.cos(angle))
            sy = center_y + int(skull_r * math.sin(angle))
            skull_size = int(size//15 * (1 - burst_phase * 0.5))
            if skull_size > 0:
                # 简化骷髅（圆形+眼睛）
                pygame.draw.circle(surface, (200, 200, 200), (sx, sy), skull_size)
                pygame.draw.circle(surface, (0, 0, 0), (sx - skull_size//3, sy - skull_size//4), skull_size//5)
                pygame.draw.circle(surface, (0, 0, 0), (sx + skull_size//3, sy - skull_size//4), skull_size//5)
        return True
    
    return False
