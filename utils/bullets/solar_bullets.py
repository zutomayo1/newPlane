# -*- coding: utf-8 -*-
"""
Solar 战机子弹涂装效果渲染模块

包含以下子弹效果：
- solar_flare/light_burst: 太阳耀斑（耀斑）
- corona_ring/plasma_loop: 日冕光环（日冕）
- prominence_jet/flame_tongue: 日珥喷发（日珥）
- sunspot_vortex/magnetic_storm: 太阳黑子（黑子）
- fusion_core/nuclear_pulse: 核聚变核（聚变）
- photon_stream/light_particle: 光子流束（光子）
- supernova_burst/stellar_explosion: 超新星爆发（超新星）
"""
import pygame
import math


def render_solar_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Solar战机的子弹效果
    
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
    
    if "solar_flare" in effects or "light_burst" in effects:
        # 太阳耀斑：光芒爆发
        # 太阳核心
        pygame.draw.circle(surface, (255, 255, 100), (center_x, center_y), size//5)
        pygame.draw.circle(surface, color, (center_x, center_y), size//6)
        # 耀斑射线（16条）
        for i in range(16):
            angle = (i * 22.5) * 3.14159 / 180
            # 交替长度
            length = size//2 if i % 2 == 0 else size//1.5
            x1 = center_x + int(size//6 * math.cos(angle))
            y1 = center_y + int(size//6 * math.sin(angle))
            x2 = center_x + int(length * math.cos(angle))
            y2 = center_y + int(length * math.sin(angle))
            # 渐变光芒
            pygame.draw.line(surface, (255, 220, 0), (x1, y1), (x2, y2), 3)
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), 1)
        # 光晕
        for i in range(3):
            halo_r = size//4 + i * size//8
            alpha = 180 - i * 50
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (size, size), halo_r)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "corona_ring" in effects or "plasma_loop" in effects:
        # 日冕光环：等离子环
        # 中心
        pygame.draw.circle(surface, (255, 200, 0), (center_x, center_y), size//6)
        # 日冕环（3层）
        for i in range(3):
            ring_r = size//3 + i * size//8
            ring_color = (255, 180 - i * 30, 0)
            alpha = 200 - i * 40
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*ring_color, alpha), (size, size), ring_r, 4)
            surface.blit(temp_surf, (x - size, y - size))
        # 等离子弧（4个）
        for i in range(4):
            angle = (i * 90 + pygame.time.get_ticks() / 50) * 3.14159 / 180
            arc_start = angle - 0.5
            arc_end = angle + 0.5
            arc_points = []
            for a in range(10):
                arc_angle = arc_start + (arc_end - arc_start) * a / 10
                px = center_x + int(size//2 * math.cos(arc_angle))
                py = center_y + int(size//2 * math.sin(arc_angle))
                arc_points.append((px, py))
            if len(arc_points) > 1:
                pygame.draw.lines(surface, (255, 150, 0), False, arc_points, 3)
        return True
    
    elif "prominence_jet" in effects or "flame_tongue" in effects:
        # 日珥喷发：火焰喷射
        # 太阳主体
        pygame.draw.circle(surface, (255, 120, 0), (center_x, center_y), size//4)
        # 火焰喷射（6条）
        for i in range(6):
            angle = (i * 60) * 3.14159 / 180
            # 火焰轨迹
            flame_points = []
            for j in range(8):
                radius = size//4 + j * size//15
                wave_offset = int(size//12 * math.sin(pygame.time.get_ticks() / 100 + i + j))
                fx = center_x + int(radius * math.cos(angle)) + wave_offset
                fy = center_y + int(radius * math.sin(angle))
                flame_points.append((fx, fy))
            if len(flame_points) > 1:
                # 多层火焰颜色
                pygame.draw.lines(surface, (255, 200, 0), False, flame_points, 5)
                pygame.draw.lines(surface, (255, 100, 0), False, flame_points, 3)
                pygame.draw.lines(surface, color, False, flame_points, 1)
        return True
    
    elif "sunspot_vortex" in effects or "magnetic_storm" in effects:
        # 太阳黑子：磁场漩涡
        # 黑子核心
        pygame.draw.circle(surface, (100, 50, 0), (center_x, center_y), size//5)
        pygame.draw.circle(surface, color, (center_x, center_y), size//6)
        # 磁力线漩涡（3条螺旋）
        for arm in range(3):
            spiral_points = []
            arm_offset = arm * 120
            for i in range(15):
                angle = (i * 24 + arm_offset + pygame.time.get_ticks() / 30) * 3.14159 / 180
                radius = size//8 + i * size//30
                sx = center_x + int(radius * math.cos(angle))
                sy = center_y + int(radius * math.sin(angle))
                spiral_points.append((sx, sy))
            if len(spiral_points) > 1:
                pygame.draw.lines(surface, (255, 150, 0), False, spiral_points, 3)
                pygame.draw.lines(surface, (200, 80, 0), False, spiral_points, 1)
        # 磁暴环
        for i in range(2):
            storm_r = size//3 + i * size//6
            alpha = 160 - i * 60
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (255, 100, 0, alpha), (size, size), storm_r, 3)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "fusion_core" in effects or "nuclear_pulse" in effects:
        # 核聚变核：聚变反应
        # 聚变核心（亮白）
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//8)
        pygame.draw.circle(surface, (255, 255, 200), (center_x, center_y), size//6)
        pygame.draw.circle(surface, color, (center_x, center_y), size//5)
        # 能量环（脉冲扩散）
        pulse_phase = (pygame.time.get_ticks() / 50) % 100 / 100
        for i in range(4):
            pulse_r = int((size//4 + i * size//6) * (1 + pulse_phase * 0.5))
            alpha = int((200 - i * 40) * (1 - pulse_phase))
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (255, 255, 100, alpha), (size, size), pulse_r, 3)
            surface.blit(temp_surf, (x - size, y - size))
        # 聚变粒子
        for i in range(8):
            angle = (i * 45 + pygame.time.get_ticks() / 20) * 3.14159 / 180
            particle_r = size//3
            px = center_x + int(particle_r * math.cos(angle))
            py = center_y + int(particle_r * math.sin(angle))
            pygame.draw.circle(surface, (255, 255, 150), (px, py), size//20)
        return True
    
    elif "photon_stream" in effects or "light_particle" in effects:
        # 光子流束：光粒子流
        # 光源核心
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//8)
        pygame.draw.circle(surface, color, (center_x, center_y), size//10)
        # 光子粒子流（螺旋）
        for stream in range(4):
            stream_offset = stream * 90
            for i in range(12):
                angle = (i * 30 + stream_offset + pygame.time.get_ticks() / 30) * 3.14159 / 180
                radius = size//6 + i * size//30
                px = center_x + int(radius * math.cos(angle))
                py = center_y + int(radius * math.sin(angle))
                particle_size = size//15 - i // 4
                if particle_size > 0:
                    pygame.draw.circle(surface, (255, 255, 220), (px, py), particle_size)
                    temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                    pygame.draw.circle(temp_surf, (*color, 200), (px - x + size, py - y + size), particle_size + 2)
                    surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "supernova_burst" in effects or "stellar_explosion" in effects:
        # 超新星爆发：毁灭爆炸
        # 超新星核心
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//10)
        pygame.draw.circle(surface, (255, 100, 0), (center_x, center_y), size//8)
        pygame.draw.circle(surface, color, (center_x, center_y), size//6)
        # 爆炸波（3层）
        explosion_phase = (pygame.time.get_ticks() / 40) % 100 / 100
        for i in range(3):
            blast_r = int((size//3 + i * size//5) * (1 + explosion_phase * 0.8))
            alpha = int((220 - i * 60) * (1 - explosion_phase * 0.8))
            blast_color = [(255, 0, 0), (255, 100, 0), (255, 200, 0)][i]
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*blast_color, alpha), (size, size), blast_r, 4)
            surface.blit(temp_surf, (x - size, y - size))
        # 爆炸碎片（12个）
        for i in range(12):
            angle = (i * 30 + explosion_phase * 360) * 3.14159 / 180
            debris_r = size//2 + int(explosion_phase * size//2)
            dx = center_x + int(debris_r * math.cos(angle))
            dy = center_y + int(debris_r * math.sin(angle))
            debris_size = int(size//12 * (1 - explosion_phase * 0.5))
            if debris_size > 0:
                pygame.draw.circle(surface, (255, 150, 0), (dx, dy), debris_size)
        return True
    
    return False
