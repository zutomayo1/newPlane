# -*- coding: utf-8 -*-
"""
Weaver 战机子弹涂装效果渲染模块

包含以下子弹效果：
- web_net/spider_silk: 蛛网陷阱（蜘蛛）
- phase_shift/dimension_warp: 相位穿梭（相位）
- void_cocoon/space_lock: 虚空之茧（虚空）
- time_thread/slow_field: 时间丝线（时间）
- quantum_tangle/entangle_web: 量子纠缠（量子）
- shadow_weave/dark_web: 暗影编织（暗影）
- cosmic_thread/star_web: 宇宙之网（宇宙）
"""
import pygame
import math
import random


def render_weaver_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Weaver战机的子弹效果
    
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
    
    if "web_net" in effects or "spider_silk" in effects:
        # 蛛网陷阱：蛛网形状
        # 中心蛛网节点
        pygame.draw.circle(surface, (220, 220, 220), (center_x, center_y), size//8)
        pygame.draw.circle(surface, color, (center_x, center_y), size//10)
        # 蛛网放射线（8条）
        for i in range(8):
            angle = (i * 45) * 3.14159 / 180
            x1 = center_x + int(size//8 * math.cos(angle))
            y1 = center_y + int(size//8 * math.sin(angle))
            x2 = center_x + int(size//2 * math.cos(angle))
            y2 = center_y + int(size//2 * math.sin(angle))
            pygame.draw.line(surface, (200, 200, 200), (x1, y1), (x2, y2), 2)
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), 1)
        # 蛛网环圈（3层）
        for i in range(3):
            ring_radius = size//4 + i * size//8
            # 绘制八边形环
            web_points = []
            for j in range(8):
                angle = (j * 45) * 3.14159 / 180
                px = center_x + int(ring_radius * math.cos(angle))
                py = center_y + int(ring_radius * math.sin(angle))
                web_points.append((px, py))
            if len(web_points) > 1:
                pygame.draw.lines(surface, (180, 180, 180), True, web_points, 1)
        return True
    
    elif "phase_shift" in effects or "dimension_warp" in effects:
        # 相位穿梭：重影效果
        # 主体（多层重影）
        shift_offsets = [(0, 0), (3, -2), (6, -4), (-3, -2)]
        for i, (dx, dy) in enumerate(shift_offsets):
            alpha = 220 - i * 40
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            # 菱形
            diamond = [
                (size + dx, size//2 + dy),
                (size*3//2 + dx, size + dy),
                (size + dx, size*3//2 + dy),
                (size//2 + dx, size + dy)
            ]
            pygame.draw.polygon(temp_surf, (*color, alpha), diamond)
            surface.blit(temp_surf, (x - size, y - size))
            if i == 0:
                pygame.draw.polygon(surface, (200, 200, 220), 
                                  [(px + x - size, py + y - size) for px, py in diamond], 2)
        # 相位粒子
        for i in range(6):
            angle = (i * 60 + pygame.time.get_ticks() / 50) * 3.14159 / 180
            px = center_x + int(size//3 * math.cos(angle))
            py = center_y + int(size//3 * math.sin(angle))
            pygame.draw.circle(surface, (180, 180, 220), (px, py), size//20)
        return True
    
    elif "void_cocoon" in effects or "space_lock" in effects:
        # 虚空之茧：茧形封锁
        # 茧外壳（椭圆）
        cocoon_rect = pygame.Rect(center_x - size//3, center_y - size//2, size*2//3, size)
        temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.ellipse(temp_surf, (*color, 200), 
                          (cocoon_rect.x - x + size, cocoon_rect.y - y + size, cocoon_rect.width, cocoon_rect.height))
        surface.blit(temp_surf, (x - size, y - size))
        pygame.draw.ellipse(surface, (120, 120, 180), cocoon_rect, 3)
        # 束缚线条（竖线）
        for i in range(6):
            line_x = center_x - size//4 + i * size//10
            pygame.draw.line(surface, (80, 80, 130), 
                           (line_x, center_y - size//2), 
                           (line_x, center_y + size//2), 2)
        # 虚空核心
        pygame.draw.circle(surface, (50, 50, 100), (center_x, center_y), size//8)
        # 空间扭曲环
        for i in range(3):
            wave_radius = size//6 + i * size//10
            alpha = 180 - i * 50
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (size, size), wave_radius, 2)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "time_thread" in effects or "slow_field" in effects:
        # 时间丝线：螺旋时钟
        # 时钟圆盘
        pygame.draw.circle(surface, (200, 200, 240), (center_x, center_y), size//3, 3)
        pygame.draw.circle(surface, color, (center_x, center_y), size//3, 1)
        # 时钟刻度（12个）
        for i in range(12):
            angle = (i * 30 - 90) * 3.14159 / 180
            x1 = center_x + int(size//4 * math.cos(angle))
            y1 = center_y + int(size//4 * math.sin(angle))
            x2 = center_x + int(size//3 * math.cos(angle))
            y2 = center_y + int(size//3 * math.sin(angle))
            width = 3 if i % 3 == 0 else 1
            pygame.draw.line(surface, (160, 160, 200), (x1, y1), (x2, y2), width)
        # 时针（减速效果）
        time_angle = (pygame.time.get_ticks() / 100) * 3.14159 / 180
        needle_x = center_x + int(size//4 * math.cos(time_angle))
        needle_y = center_y + int(size//4 * math.sin(time_angle))
        pygame.draw.line(surface, (100, 100, 150), (center_x, center_y), (needle_x, needle_y), 3)
        # 时间波纹
        for i in range(2):
            wave_r = size//2 + i * size//6 + int(size//10 * math.sin(pygame.time.get_ticks() / 100))
            alpha = 150 - i * 50
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (size, size), wave_r, 2)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "quantum_tangle" in effects or "entangle_web" in effects:
        # 量子纠缠：量子粒子连接
        # 中心量子核
        pygame.draw.circle(surface, (150, 220, 255), (center_x, center_y), size//6)
        pygame.draw.circle(surface, color, (center_x, center_y), size//8)
        # 量子粒子（6个）
        particles = []
        for i in range(6):
            angle = (i * 60 + pygame.time.get_ticks() / 40) * 3.14159 / 180
            px = center_x + int(size//2.5 * math.cos(angle))
            py = center_y + int(size//2.5 * math.sin(angle))
            particles.append((px, py))
            # 粒子球
            pygame.draw.circle(surface, (100, 180, 255), (px, py), size//12)
            pygame.draw.circle(surface, color, (px, py), size//15)
        # 纠缠连线（连接所有粒子）
        for i in range(len(particles)):
            for j in range(i + 1, len(particles)):
                alpha = 150
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                p1 = (particles[i][0] - x + size, particles[i][1] - y + size)
                p2 = (particles[j][0] - x + size, particles[j][1] - y + size)
                pygame.draw.line(temp_surf, (*color, alpha), p1, p2, 1)
                surface.blit(temp_surf, (x - size, y - size))
        # 纠缠波动
        for px, py in particles:
            pulse_size = int(size//15 * (1 + 0.3 * math.sin(pygame.time.get_ticks() / 80)))
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, 100), (px - x + size, py - y + size), pulse_size)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "shadow_weave" in effects or "dark_web" in effects:
        # 暗影编织：黑暗蛛网
        # 暗影中心
        pygame.draw.circle(surface, (30, 30, 60), (center_x, center_y), size//5)
        pygame.draw.circle(surface, color, (center_x, center_y), size//6)
        # 暗影射线（12条）
        for i in range(12):
            angle = (i * 30) * 3.14159 / 180
            # 不规则长度
            length = size//2 + (i % 3) * size//8
            x1 = center_x + int(size//6 * math.cos(angle))
            y1 = center_y + int(size//6 * math.sin(angle))
            x2 = center_x + int(length * math.cos(angle))
            y2 = center_y + int(length * math.sin(angle))
            # 渐变黑影
            for j in range(3):
                alpha = 180 - j * 50
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                offset = j * 2
                pygame.draw.line(temp_surf, (*color, alpha), 
                               (x1 - x + size + offset, y1 - y + size + offset),
                               (x2 - x + size + offset, y2 - y + size + offset), 2)
                surface.blit(temp_surf, (x - size, y - size))
        # 暗影粒子
        random.seed(789)
        for _ in range(8):
            px = center_x + random.randint(-size//2, size//2)
            py = center_y + random.randint(-size//2, size//2)
            psize = random.randint(2, 4)
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, 120), (px - x + size, py - y + size), psize)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "cosmic_thread" in effects or "star_web" in effects:
        # 宇宙之网：星空蛛网
        # 中心星云
        pygame.draw.circle(surface, (200, 180, 255), (center_x, center_y), size//6)
        pygame.draw.circle(surface, color, (center_x, center_y), size//8)
        # 星际连线（12条）
        for i in range(12):
            angle = (i * 30) * 3.14159 / 180
            x1 = center_x + int(size//8 * math.cos(angle))
            y1 = center_y + int(size//8 * math.sin(angle))
            x2 = center_x + int(size//2 * math.cos(angle))
            y2 = center_y + int(size//2 * math.sin(angle))
            # 星光线
            pygame.draw.line(surface, (180, 160, 220), (x1, y1), (x2, y2), 2)
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), 1)
        # 星点（8个）
        for i in range(8):
            angle = (i * 45) * 3.14159 / 180
            star_x = center_x + int(size//2.5 * math.cos(angle))
            star_y = center_y + int(size//2.5 * math.sin(angle))
            # 星芒
            for j in range(4):
                star_angle = (j * 45) * 3.14159 / 180
                sx1 = star_x
                sy1 = star_y
                sx2 = star_x + int(size//15 * math.cos(star_angle))
                sy2 = star_y + int(size//15 * math.sin(star_angle))
                pygame.draw.line(surface, (255, 255, 255), (sx1, sy1), (sx2, sy2), 1)
            pygame.draw.circle(surface, (255, 255, 255), (star_x, star_y), size//25)
        return True
    
    return False
