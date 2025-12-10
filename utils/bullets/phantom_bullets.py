# -*- coding: utf-8 -*-
"""
Phantom 战机子弹涂装效果渲染模块

包含以下子弹效果：
- void_crack: 虚空裂缝（Mk2）
- ghost_face: 幽灵面孔（隐身）
- crystal_prism: 水晶棱镜（镜像）
- tentacle_crawl: 触手蠕动（噩梦）
- aurora_tail: 极光彗星（极光）
- hourglass_flow: 沙漏流转（时间）
- matrix_rain: 矩阵代码雨（矩阵）
"""
import pygame
import math
import random


def render_phantom_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Phantom战机的子弹效果
    
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
    
    if "void_crack" in effects:
        # 虚空裂缝：不规则裂缝+黑洞漩涡
        # 中心黑洞
        for r in range(size//2, 0, -size//10):
            alpha = int(255 * (1 - r / (size//2)))
            temp_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (size//2, size//2), r)
            surface.blit(temp_surf, (x, y))
        # 裂缝闪电
        for i in range(4):
            angle = (i * 90 + pygame.time.get_ticks() / 100) * 3.14159 / 180
            segments = []
            for j in range(4):
                r = size//5 + j * size//10
                px = center_x + int(r * math.cos(angle) + random.randint(-5, 5))
                py = center_y + int(r * math.sin(angle) + random.randint(-5, 5))
                segments.append((px, py))
            pygame.draw.lines(surface, (150, 0, 200), False, segments, 2)
        return True
    
    elif "ghost_face" in effects:
        # 幽灵面孔：脸型轮廓+眼睛+嘴巴
        # 脸型（椭圆形半透明）
        temp_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(temp_surf, (*color, 150), (size//6, size//8, size*2//3, size*3//4))
        surface.blit(temp_surf, (x, y))
        # 眼睛（发光）
        eye_y = center_y - size//8
        pygame.draw.circle(surface, (255, 255, 255), (center_x - size//6, eye_y), size//10)
        pygame.draw.circle(surface, (255, 255, 255), (center_x + size//6, eye_y), size//10)
        pygame.draw.circle(surface, (100, 100, 255), (center_x - size//6, eye_y), size//15)
        pygame.draw.circle(surface, (100, 100, 255), (center_x + size//6, eye_y), size//15)
        # 嘴巴（哀嚎弧形）
        mouth_rect = pygame.Rect(center_x - size//4, center_y, size//2, size//3)
        pygame.draw.arc(surface, (200, 200, 255), mouth_rect, 0, 3.14159, 3)
        return True
    
    elif "crystal_prism" in effects:
        # 水晶棱镜：多面体+内部光线
        # 外层八面体
        top = (center_x, center_y - size//2.5)
        bottom = (center_x, center_y + size//2.5)
        mid_points = []
        for i in range(4):
            angle = (i * 90) * 3.14159 / 180
            px = center_x + int(size//3.5 * math.cos(angle))
            py = center_y + int(size//3.5 * math.sin(angle))
            mid_points.append((px, py))
        # 绘制上半部分面
        for i in range(4):
            face = [top, mid_points[i], mid_points[(i+1)%4]]
            pygame.draw.polygon(surface, color, face)
            pygame.draw.polygon(surface, (255, 255, 255), face, 2)
        # 绘制下半部分面
        for i in range(4):
            face = [bottom, mid_points[i], mid_points[(i+1)%4]]
            pygame.draw.polygon(surface, color, face)
            pygame.draw.polygon(surface, (255, 255, 255), face, 2)
        # 内部光线
        for i in range(4):
            pygame.draw.line(surface, (255, 255, 255), top, mid_points[i], 1)
        return True
    
    elif "tentacle_crawl" in effects:
        # 触手蠕动：多条触须+恐惧之眼
        # 中心眼球
        pygame.draw.circle(surface, (150, 0, 150), (center_x, center_y), size//4)
        pygame.draw.circle(surface, (255, 0, 255), (center_x, center_y), size//6)
        pygame.draw.circle(surface, (50, 0, 50), (center_x, center_y), size//10)
        # 6条扭曲触手
        for i in range(6):
            angle_base = i * 60 * 3.14159 / 180
            segments = [(center_x, center_y)]
            for j in range(5):
                angle = angle_base + math.sin((pygame.time.get_ticks() / 200 + i + j)) * 0.3
                r = (j + 1) * size // 12
                px = center_x + int(r * math.cos(angle))
                py = center_y + int(r * math.sin(angle))
                segments.append((px, py))
            # 触手宽度递减
            for k in range(len(segments)-1):
                width = max(1, 6 - k)
                pygame.draw.line(surface, color, segments[k], segments[k+1], width)
        return True
    
    elif "aurora_tail" in effects:
        # 极光彗星：流星体+彩虹尾迹
        # 彗星头部（亮白核心）
        pygame.draw.circle(surface, (255, 255, 255), (center_x + size//6, center_y), size//5)
        pygame.draw.circle(surface, color, (center_x + size//6, center_y), size//7)
        # 彩虹尾迹（波浪状）
        colors = [(255, 100, 100), (255, 255, 100), (100, 255, 100), (100, 255, 255), (100, 100, 255)]
        for i, trail_color in enumerate(colors):
            wave_points = []
            for j in range(8):
                offset = math.sin((pygame.time.get_ticks() / 100 + j + i)) * size // 15
                px = center_x + size//6 - j * size // 15
                py = center_y + offset
                wave_points.append((px, py))
            if len(wave_points) > 1:
                pygame.draw.lines(surface, trail_color, False, wave_points, 3)
        return True
    
    elif "hourglass_flow" in effects:
        # 沙漏流转：沙漏形状+流沙粒子
        # 上半部分三角形
        top_tri = [
            (center_x, center_y),
            (center_x - size//3, center_y - size//2.5),
            (center_x + size//3, center_y - size//2.5)
        ]
        pygame.draw.polygon(surface, color, top_tri)
        pygame.draw.polygon(surface, (255, 255, 255), top_tri, 2)
        # 下半部分三角形
        bottom_tri = [
            (center_x, center_y),
            (center_x - size//3, center_y + size//2.5),
            (center_x + size//3, center_y + size//2.5)
        ]
        pygame.draw.polygon(surface, color, bottom_tri)
        pygame.draw.polygon(surface, (255, 255, 255), bottom_tri, 2)
        # 流沙粒子
        for i in range(5):
            offset = (pygame.time.get_ticks() / 30 + i * 10) % (size//2)
            py = center_y - size//2.5 + offset
            if py < center_y + size//2.5:
                pygame.draw.circle(surface, (255, 230, 150), (center_x, int(py)), 2)
        return True
    
    elif "matrix_rain" in effects:
        # 矩阵代码雨：数字方块瀑布
        # 绘制代码列
        for col in range(5):
            x_pos = x + col * size // 5 + size // 10
            blocks = int((pygame.time.get_ticks() / 100 + col * 3) % 8)
            for row in range(blocks):
                y_pos = y + row * size // 8
                block_size = size // 12
                alpha = int(255 * (1 - row / 8))
                temp_surf = pygame.Surface((block_size, block_size), pygame.SRCALPHA)
                temp_surf.fill((*color, alpha))
                surface.blit(temp_surf, (x_pos, y_pos))
                # 边框
                pygame.draw.rect(surface, (0, 200, 0), (x_pos, y_pos, block_size, block_size), 1)
        return True
    
    return False
