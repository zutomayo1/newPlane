# -*- coding: utf-8 -*-
"""
Prism 战机子弹涂装效果渲染模块

包含以下子弹效果：
- rainbow_ray/spectrum_split: 彩虹射线
- crystal_shard/prism_fragment: 水晶碎片
- refraction_beam/light_bend: 折射光束
- laser_prism/triangular_prism: 激光棱镜
- aurora_split/northern_light: 极光分裂
- hologram/3d_projection: 全息投影
- lens_flare/optical_burst: 镜头光晕
"""
import pygame
import math


def render_prism_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Prism战机的子弹效果
    
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
    
    if "rainbow_ray" in effects or "spectrum_split" in effects:
        # 彩虹射线：七色光芒
        # 彩虹核心
        rainbow_colors = [
            (255, 0, 0), (255, 127, 0), (255, 255, 0),
            (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)
        ]
        # 彩虹射线（7条）
        for i, ray_color in enumerate(rainbow_colors):
            angle = (i * 51.4 + pygame.time.get_ticks() / 50) * 3.14159 / 180
            x1 = center_x + int(size//8 * math.cos(angle))
            y1 = center_y + int(size//8 * math.sin(angle))
            x2 = center_x + int(size//2 * math.cos(angle))
            y2 = center_y + int(size//2 * math.sin(angle))
            pygame.draw.line(surface, ray_color, (x1, y1), (x2, y2), 3)
        # 中心白光
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//8)
        pygame.draw.circle(surface, color, (center_x, center_y), size//10)
        # 光谱环
        for i in range(7):
            ring_color = rainbow_colors[i]
            ring_r = size//4 + i * size//35
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*ring_color, 150), (size, size), ring_r, 2)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "crystal_shard" in effects or "prism_fragment" in effects:
        # 水晶碎片：晶体折射
        # 中心水晶
        crystal_points = [
            (center_x, center_y - size//2),
            (center_x + size//3, center_y),
            (center_x, center_y + size//2),
            (center_x - size//3, center_y)
        ]
        pygame.draw.polygon(surface, (200, 240, 255), crystal_points)
        pygame.draw.polygon(surface, color, crystal_points, 3)
        # 碎片（周围小晶体）
        for i in range(6):
            angle = (i * 60 + pygame.time.get_ticks() / 60) * 3.14159 / 180
            sx = center_x + int(size//2.5 * math.cos(angle))
            sy = center_y + int(size//2.5 * math.sin(angle))
            shard_points = [
                (sx, sy - size//8),
                (sx + size//12, sy + size//12),
                (sx - size//12, sy + size//12)
            ]
            pygame.draw.polygon(surface, (150, 220, 255), shard_points)
            pygame.draw.polygon(surface, color, shard_points, 2)
        # 光线折射效果
        for i in range(4):
            angle = (i * 90) * 3.14159 / 180
            x1 = center_x + int(size//4 * math.cos(angle))
            y1 = center_y + int(size//4 * math.sin(angle))
            x2 = center_x + int(size//2 * math.cos(angle + 0.5))
            y2 = center_y + int(size//2 * math.sin(angle + 0.5))
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.line(temp_surf, (*color, 180), (x1 - x + size, y1 - y + size), (x2 - x + size, y2 - y + size), 2)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "refraction_beam" in effects or "light_bend" in effects:
        # 折射光束：曲线光束
        # 光源
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//8)
        pygame.draw.circle(surface, color, (center_x, center_y), size//10)
        # 折射光束（3条弯曲路径）
        for i in range(3):
            beam_angle = (i * 120) * 3.14159 / 180
            beam_points = []
            for j in range(8):
                radius = size//8 + j * size//16
                curve_offset = int(size//12 * math.sin(j * 0.5 + pygame.time.get_ticks() / 100))
                bx = center_x + int(radius * math.cos(beam_angle)) + curve_offset
                by = center_y + int(radius * math.sin(beam_angle))
                beam_points.append((bx, by))
            if len(beam_points) > 1:
                # 多层光束颜色
                pygame.draw.lines(surface, (200, 230, 255), False, beam_points, 4)
                pygame.draw.lines(surface, color, False, beam_points, 2)
        # 折射粒子
        for i in range(6):
            angle = (i * 60) * 3.14159 / 180
            px = center_x + int(size//3 * math.cos(angle))
            py = center_y + int(size//3 * math.sin(angle))
            pygame.draw.circle(surface, (150, 200, 255), (px, py), size//25)
        return True
    
    elif "laser_prism" in effects or "triangular_prism" in effects:
        # 激光棱镜：三棱镜
        # 棱镜主体（三角形）
        prism_triangle = [
            (center_x, center_y - size//3),
            (center_x + size//3, center_y + size//3),
            (center_x - size//3, center_y + size//3)
        ]
        pygame.draw.polygon(surface, (180, 230, 255), prism_triangle)
        pygame.draw.polygon(surface, color, prism_triangle, 3)
        # 入射光（白光）
        pygame.draw.line(surface, (255, 255, 255), (center_x - size//2, center_y - size//4), (center_x - size//6, center_y), 3)
        # 分光（彩虹射线）
        spectrum_colors = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (148, 0, 211)]
        for i, spec_color in enumerate(spectrum_colors):
            angle = -20 + i * 10
            rad = angle * 3.14159 / 180
            x1 = center_x + size//6
            y1 = center_y
            x2 = center_x + int(size//2 * math.cos(rad))
            y2 = center_y + int(size//2 * math.sin(rad))
            pygame.draw.line(surface, spec_color, (x1, y1), (x2, y2), 2)
        return True
    
    elif "aurora_split" in effects or "northern_light" in effects:
        # 极光分裂：北极光
        # 极光波纹
        aurora_colors = [(0, 255, 200), (100, 255, 150), (150, 255, 200)]
        wave_phase = (pygame.time.get_ticks() / 60) % 100 / 100
        for i in range(3):
            wave_y = center_y - size//2 + i * size//3 + int(wave_phase * size//4)
            # 波浪曲线
            wave_points = []
            for j in range(10):
                wx = center_x - size//2 + j * size//9
                wy = wave_y + int(size//10 * math.sin(j * 0.8 + wave_phase * 6.28))
                wave_points.append((wx, wy))
            if len(wave_points) > 1:
                alpha = 200 - i * 50
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                adjusted_points = [(px - x + size, py - y + size) for px, py in wave_points]
                pygame.draw.lines(temp_surf, (*aurora_colors[i], alpha), False, adjusted_points, 3)
                surface.blit(temp_surf, (x - size, y - size))
        # 中心光球
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//8)
        pygame.draw.circle(surface, color, (center_x, center_y), size//10)
        # 极光粒子
        for i in range(8):
            angle = (i * 45 + pygame.time.get_ticks() / 50) * 3.14159 / 180
            px = center_x + int(size//3 * math.cos(angle))
            py = center_y + int(size//3 * math.sin(angle))
            pygame.draw.circle(surface, (120, 255, 200), (px, py), size//20)
        return True
    
    elif "hologram" in effects or "3d_projection" in effects:
        # 全息投影：3D影像
        # 全息网格
        grid_lines = 8
        for i in range(grid_lines):
            # 横线
            y_pos = center_y - size//2 + i * size//(grid_lines-1)
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.line(temp_surf, (*color, 120), 
                           (center_x - size//2 - x + size, y_pos - y + size),
                           (center_x + size//2 - x + size, y_pos - y + size), 1)
            surface.blit(temp_surf, (x - size, y - size))
            # 竖线
            x_pos = center_x - size//2 + i * size//(grid_lines-1)
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.line(temp_surf, (*color, 120),
                           (x_pos - x + size, center_y - size//2 - y + size),
                           (x_pos - x + size, center_y + size//2 - y + size), 1)
            surface.blit(temp_surf, (x - size, y - size))
        # 3D立方体（旋转）
        rotation = (pygame.time.get_ticks() / 50) % 360 * 3.14159 / 180
        cube_size = size//4
        cube_points_3d = [
            (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
        ]
        cube_points_2d = []
        for px, py, pz in cube_points_3d:
            # 简单旋转投影
            rx = px * math.cos(rotation) - pz * math.sin(rotation)
            rz = px * math.sin(rotation) + pz * math.cos(rotation)
            x2d = center_x + int(rx * cube_size)
            y2d = center_y + int(py * cube_size)
            cube_points_2d.append((x2d, y2d))
        # 绘制立方体边
        cube_edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
        for i, j in cube_edges:
            pygame.draw.line(surface, color, cube_points_2d[i], cube_points_2d[j], 2)
        return True
    
    elif "lens_flare" in effects or "optical_burst" in effects:
        # 镜头光晕：光学耀斑
        # 主光源（超亮）
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//6)
        pygame.draw.circle(surface, color, (center_x, center_y), size//8)
        # 光晕环（多层）
        for i in range(4):
            flare_r = size//5 + i * size//10
            alpha = 200 - i * 40
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (255, 255, 255, alpha), (size, size), flare_r)
            surface.blit(temp_surf, (x - size, y - size))
        # 光斑（6个）
        flare_spots = [0.3, 0.5, 0.7, 0.9, 1.1, 1.3]
        for i, dist in enumerate(flare_spots):
            spot_x = center_x + int(size//2 * dist * math.cos(i * 0.8))
            spot_y = center_y + int(size//2 * dist * math.sin(i * 0.8))
            spot_size = int(size//15 * (1.5 - dist * 0.5))
            if spot_size > 0:
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, 180), (spot_x - x + size, spot_y - y + size), spot_size)
                surface.blit(temp_surf, (x - size, y - size))
        # 十字光芒
        for i in range(4):
            angle = (i * 90) * 3.14159 / 180
            x1 = center_x + int(size//8 * math.cos(angle))
            y1 = center_y + int(size//8 * math.sin(angle))
            x2 = center_x + int(size//1.5 * math.cos(angle))
            y2 = center_y + int(size//1.5 * math.sin(angle))
            pygame.draw.line(surface, (255, 255, 200), (x1, y1), (x2, y2), 3)
        return True
    
    return False
