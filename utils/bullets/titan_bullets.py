# -*- coding: utf-8 -*-
"""
Titan 战机子弹涂装效果渲染模块

包含以下子弹效果：
- shell_massive: 巨型炮弹（要塞）
- nuclear_glow: 核辐射（核武）
- magma_boulder: 熔岩巨石（火山）
- rocket_thruster: 机械火箭（机甲）
- ice_spike: 冰晶巨刺（水晶）
- demon_skull: 恶魔骷髅（恶魔）
- plasma_beam: 轨道激光柱（轨道）
"""
import pygame
import math
import random


def render_titan_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Titan战机的子弹效果
    
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
    
    if "shell_massive" in effects:
        # 巨型炮弹：圆柱形弹体+尖锐弹头
        # 弹体（圆柱）
        body_width = size // 2
        body_height = size
        body_rect = (center_x - body_width//2, center_y - size//3, body_width, body_height)
        pygame.draw.rect(surface, color, body_rect, border_radius=5)
        pygame.draw.rect(surface, (180, 180, 180), body_rect, 3, border_radius=5)
        # 弹头（三角锥）
        tip = [
            (center_x, center_y - size//1.8),
            (center_x - body_width//2, center_y - size//3),
            (center_x + body_width//2, center_y - size//3)
        ]
        pygame.draw.polygon(surface, (100, 100, 100), tip)
        pygame.draw.polygon(surface, (200, 200, 200), tip, 2)
        # 底部推进器纹路
        for i in range(3):
            y_line = center_y + size//3 + i * size//8
            pygame.draw.line(surface, (80, 80, 80), 
                           (center_x - body_width//2, y_line),
                           (center_x + body_width//2, y_line), 2)
        return True
    
    elif "nuclear_glow" in effects:
        # 核辐射：多层发光球体+辐射符号
        # 外层脉冲光环
        pulse = abs(math.sin(pygame.time.get_ticks() / 200))
        for i in range(3):
            radius = size//2 + int(i * size//6 * pulse)
            alpha = int(100 * (1 - i/3))
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (size, size), radius)
            surface.blit(temp_surf, (x-size//2, y-size//2))
        # 中心核心球
        pygame.draw.circle(surface, (255, 255, 0), (center_x, center_y), size//4)
        pygame.draw.circle(surface, color, (center_x, center_y), size//5)
        # 辐射标志（三叶符号）
        for i in range(3):
            angle = (i * 120) * 3.14159 / 180
            segment_start = (
                center_x + int(size//6 * math.cos(angle)),
                center_y + int(size//6 * math.sin(angle))
            )
            segment_end = (
                center_x + int(size//2.2 * math.cos(angle)),
                center_y + int(size//2.2 * math.sin(angle))
            )
            pygame.draw.line(surface, (0, 0, 0), segment_start, segment_end, 5)
            pygame.draw.circle(surface, (0, 0, 0), segment_end, size//10)
        return True
    
    elif "magma_boulder" in effects:
        # 熔岩巨石：不规则岩石+裂缝发光
        # 主体不规则多边形
        random.seed(42)  # 固定随机种子保证稳定显示
        points = []
        for i in range(8):
            angle = (i * 45) * 3.14159 / 180
            radius = size//2.5 + random.randint(-size//8, size//8)
            px = center_x + int(radius * math.cos(angle))
            py = center_y + int(radius * math.sin(angle))
            points.append((px, py))
        pygame.draw.polygon(surface, (80, 40, 0), points)
        pygame.draw.polygon(surface, color, points, 3)
        # 岩浆裂缝（发光）
        for i in range(4):
            x1 = center_x + random.randint(-size//4, size//4)
            y1 = center_y + random.randint(-size//4, size//4)
            x2 = x1 + random.randint(-size//6, size//6)
            y2 = y1 + random.randint(-size//6, size//6)
            pygame.draw.line(surface, (255, 255, 0), (x1, y1), (x2, y2), 3)
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), 1)
        return True
    
    elif "rocket_thruster" in effects:
        # 机械火箭：圆柱体+尾部推进器
        # 火箭头部（圆锥）
        nose = [
            (center_x, center_y - size//2),
            (center_x - size//5, center_y - size//4),
            (center_x + size//5, center_y - size//4)
        ]
        pygame.draw.polygon(surface, (200, 200, 200), nose)
        # 火箭身（圆柱+窗口）
        body_rect = (center_x - size//5, center_y - size//4, size*2//5, size*3//4)
        pygame.draw.rect(surface, color, body_rect)
        pygame.draw.rect(surface, (255, 255, 255), body_rect, 2)
        # 窗口
        pygame.draw.circle(surface, (100, 200, 255), (center_x, center_y), size//8)
        # 尾部推进器火焰
        flame_height = int(size//4 * (1 + 0.3 * math.sin(pygame.time.get_ticks() / 100)))
        flame = [
            (center_x - size//5, center_y + size//2),
            (center_x, center_y + size//2 + flame_height),
            (center_x + size//5, center_y + size//2)
        ]
        pygame.draw.polygon(surface, (255, 200, 0), flame)
        pygame.draw.polygon(surface, (255, 100, 0), [
            (center_x - size//8, center_y + size//2),
            (center_x, center_y + size//2 + flame_height//2),
            (center_x + size//8, center_y + size//2)
        ])
        return True
    
    elif "ice_spike" in effects:
        # 冰晶巨刺：多棱锥形+透明质感
        # 主尖刺（四棱锥）
        tip = (center_x, center_y - size//2)
        base_points = [
            (center_x - size//4, center_y + size//4),
            (center_x + size//4, center_y + size//4),
            (center_x + size//3, center_y),
            (center_x - size//3, center_y)
        ]
        # 绘制四个侧面
        temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        for i in range(4):
            face = [tip, base_points[i], base_points[(i+1)%4]]
            pygame.draw.polygon(temp_surf, (*color, 180), face)
            pygame.draw.polygon(temp_surf, (255, 255, 255), face, 2)
        surface.blit(temp_surf, (x-size//2, y-size//2))
        # 冰晶闪光
        for i in range(3):
            angle = (i * 120) * 3.14159 / 180
            px = center_x + int(size//3 * math.cos(angle))
            py = center_y + int(size//3 * math.sin(angle))
            pygame.draw.circle(surface, (255, 255, 255), (px, py), 3)
        return True
    
    elif "demon_skull" in effects:
        # 恶魔骷髅：骷髅头+角+火焰
        # 头骨轮廓
        pygame.draw.ellipse(surface, (120, 0, 0), 
                          (center_x - size//3, center_y - size//3, size*2//3, size*2//3))
        pygame.draw.ellipse(surface, color, 
                          (center_x - size//3, center_y - size//3, size*2//3, size*2//3), 3)
        # 眼睛（空洞）
        pygame.draw.circle(surface, (0, 0, 0), (center_x - size//6, center_y - size//10), size//10)
        pygame.draw.circle(surface, (255, 0, 0), (center_x - size//6, center_y - size//10), size//10, 2)
        pygame.draw.circle(surface, (0, 0, 0), (center_x + size//6, center_y - size//10), size//10)
        pygame.draw.circle(surface, (255, 0, 0), (center_x + size//6, center_y - size//10), size//10, 2)
        # 鼻子（三角洞）
        nose = [
            (center_x, center_y + size//12),
            (center_x - size//15, center_y + size//6),
            (center_x + size//15, center_y + size//6)
        ]
        pygame.draw.polygon(surface, (0, 0, 0), nose)
        # 恶魔角
        for dx in [-size//3, size//3]:
            horn = [
                (center_x + dx, center_y - size//4),
                (center_x + dx + (size//8 if dx < 0 else -size//8), center_y - size//2),
                (center_x + dx + (size//6 if dx < 0 else -size//6), center_y - size//4)
            ]
            pygame.draw.polygon(surface, (80, 0, 0), horn)
            pygame.draw.polygon(surface, color, horn, 2)
        return True
    
    elif "plasma_beam" in effects:
        # 轨道激光柱：十字光柱+瞄准圈
        # 中心发光核心
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//5)
        pygame.draw.circle(surface, color, (center_x, center_y), size//6)
        # 垂直光束
        beam_width = size // 10
        pygame.draw.rect(surface, (*color, 200), 
                       (center_x - beam_width//2, center_y - size//2, beam_width, size))
        # 水平光束
        pygame.draw.rect(surface, (*color, 200), 
                       (center_x - size//2, center_y - beam_width//2, size, beam_width))
        # 瞄准圈
        for radius in [size//2.5, size//2]:
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), int(radius), 2)
        # 十字准星角标
        marker_len = size // 8
        for angle in [45, 135, 225, 315]:
            rad = angle * 3.14159 / 180
            x1 = center_x + int(size//2.2 * math.cos(rad))
            y1 = center_y + int(size//2.2 * math.sin(rad))
            x2 = x1 + int(marker_len * math.cos(rad))
            y2 = y1 + int(marker_len * math.sin(rad))
            pygame.draw.line(surface, (255, 255, 255), (x1, y1), (x2, y2), 2)
        return True
    
    return False
