# -*- coding: utf-8 -*-
"""
Arbiter 战机子弹涂装效果渲染模块

包含以下子弹效果：
- quant_cube/quantum_matrix: 量子立方（量子）
- fractal_shard/split_multiply: 分形碎片（分形）
- tesseract/hypercube_projection: 四维超立方（超立方）
- matrix_rain/code_cascade: 矩阵代码雨（矩阵）
- geometric_wave/angular_ripple: 几何波纹（几何）
- quantum_entangle/spooky_action: 量子纠缠网（纠缠）
- collapse_star/wavefunction_collapse: 波函数坍缩（坍缩）
"""
import pygame
import math
import random


def render_arbiter_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Arbiter战机的子弹效果
    
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
    
    if "quant_cube" in effects or "quantum_matrix" in effects:
        # 量子立方：几何量子态
        cube_size = size//2
        pygame.draw.rect(surface, color, (center_x - cube_size//2, center_y - cube_size//2, cube_size, cube_size), 3)
        # 透视立方
        offset = size//6
        back_rect = (center_x - cube_size//2 + offset, center_y - cube_size//2 - offset, cube_size, cube_size)
        pygame.draw.rect(surface, (150, 80, 200), back_rect, 2)
        # 连接线
        corners = [
            (center_x - cube_size//2, center_y - cube_size//2),
            (center_x + cube_size//2, center_y - cube_size//2),
            (center_x + cube_size//2, center_y + cube_size//2),
            (center_x - cube_size//2, center_y + cube_size//2)
        ]
        back_corners = [
            (center_x - cube_size//2 + offset, center_y - cube_size//2 - offset),
            (center_x + cube_size//2 + offset, center_y - cube_size//2 - offset),
            (center_x + cube_size//2 + offset, center_y + cube_size//2 - offset),
            (center_x - cube_size//2 + offset, center_y + cube_size//2 - offset)
        ]
        for i in range(4):
            pygame.draw.line(surface, (120, 60, 180), corners[i], back_corners[i], 1)
        # 量子态粒子
        for i in range(8):
            angle = (i * 45 + pygame.time.get_ticks() / 40) * 3.14159 / 180
            px = center_x + int(size//3 * math.cos(angle))
            py = center_y + int(size//3 * math.sin(angle))
            pygame.draw.circle(surface, (200, 150, 255), (px, py), size//25)
        return True
    
    elif "fractal_shard" in effects or "split_multiply" in effects:
        # 分形碎片：自相似分裂
        main_triangle = [
            (center_x, center_y - size//2),
            (center_x - size//2, center_y + size//2),
            (center_x + size//2, center_y + size//2)
        ]
        pygame.draw.polygon(surface, color, main_triangle, 3)
        # 分形子碎片
        for i in range(3):
            angle = (i * 120 + pygame.time.get_ticks() / 50) * 3.14159 / 180
            fx = center_x + int(size//3 * math.cos(angle))
            fy = center_y + int(size//3 * math.sin(angle))
            sub_triangle = [
                (fx, fy - size//6),
                (fx - size//6, fy + size//6),
                (fx + size//6, fy + size//6)
            ]
            pygame.draw.polygon(surface, (180, 100, 230), sub_triangle, 2)
        return True
    
    elif "tesseract" in effects or "hypercube_projection" in effects:
        # 四维超立方：高维投影
        inner_size = size//3
        inner_rect = (center_x - inner_size//2, center_y - inner_size//2, inner_size, inner_size)
        pygame.draw.rect(surface, (150, 100, 220), inner_rect, 3)
        outer_size = int(size//1.5)
        outer_rect = (center_x - outer_size//2, center_y - outer_size//2, outer_size, outer_size)
        pygame.draw.rect(surface, color, outer_rect, 3)
        # 连接线
        inner_corners = [
            (center_x - inner_size//2, center_y - inner_size//2),
            (center_x + inner_size//2, center_y - inner_size//2),
            (center_x + inner_size//2, center_y + inner_size//2),
            (center_x - inner_size//2, center_y + inner_size//2)
        ]
        outer_corners = [
            (center_x - outer_size//2, center_y - outer_size//2),
            (center_x + outer_size//2, center_y - outer_size//2),
            (center_x + outer_size//2, center_y + outer_size//2),
            (center_x - outer_size//2, center_y + outer_size//2)
        ]
        for i in range(4):
            pygame.draw.line(surface, (180, 120, 240), inner_corners[i], outer_corners[i], 2)
        return True
    
    elif "matrix_rain" in effects or "code_cascade" in effects:
        # 矩阵代码雨：数字瀑布
        temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.rect(temp_surf, (0, 50, 20, 180), (0, 0, size*2, size*2))
        surface.blit(temp_surf, (x - size, y - size))
        random.seed(123)
        for i in range(8):
            line_x = center_x - size//2 + i * size//4
            for j in range(6):
                code_y = center_y - size//2 + j * size//6
                brightness = 100 + (j * 25)
                char_color = (0, brightness, 50)
                char_size = size//20
                pygame.draw.rect(surface, char_color, (line_x - char_size//2, code_y - char_size//2, char_size, char_size))
        return True
    
    elif "geometric_wave" in effects or "angular_ripple" in effects:
        # 几何波纹：棱角扩散
        hex_points = []
        for i in range(6):
            angle = (i * 60) * 3.14159 / 180
            px = center_x + int(size//4 * math.cos(angle))
            py = center_y + int(size//4 * math.sin(angle))
            hex_points.append((px, py))
        pygame.draw.polygon(surface, color, hex_points, 3)
        # 波纹环
        wave_phase = (pygame.time.get_ticks() / 60) % 100 / 100
        for i in range(3):
            wave_r = size//3 + i * size//8 + int(wave_phase * size//6)
            alpha = int((200 - i * 50) * (1 - wave_phase))
            wave_hex = []
            for j in range(6):
                angle = (j * 60) * 3.14159 / 180
                px = center_x + int(wave_r * math.cos(angle))
                py = center_y + int(wave_r * math.sin(angle))
                wave_hex.append((px, py))
            if len(wave_hex) > 1:
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                adjusted_points = [(px - x + size, py - y + size) for px, py in wave_hex]
                pygame.draw.lines(temp_surf, (*color, alpha), True, adjusted_points, 2)
                surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "quantum_entangle" in effects or "spooky_action" in effects:
        # 量子纠缠网：超距连接
        pygame.draw.circle(surface, (255, 150, 255), (center_x, center_y), size//8)
        pygame.draw.circle(surface, color, (center_x, center_y), size//10)
        particles = []
        for i in range(8):
            angle = (i * 45 + pygame.time.get_ticks() / 40) * 3.14159 / 180
            px = center_x + int(size//2.5 * math.cos(angle))
            py = center_y + int(size//2.5 * math.sin(angle))
            particles.append((px, py))
            pygame.draw.circle(surface, (200, 100, 220), (px, py), size//15)
        temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        for i in range(len(particles)):
            opposite = (i + 4) % len(particles)
            p1 = (particles[i][0] - x + size, particles[i][1] - y + size)
            p2 = (particles[opposite][0] - x + size, particles[opposite][1] - y + size)
            pygame.draw.line(temp_surf, (*color, 150), p1, p2, 2)
        surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "collapse_star" in effects or "wavefunction_collapse" in effects:
        # 波函数坍缩：量子态收束
        collapse_phase = (math.sin(pygame.time.get_ticks() / 100) + 1) / 2
        for i in range(8):
            angle = (i * 45) * 3.14159 / 180
            spread = int(size//3 * (1 - collapse_phase))
            sx = center_x + int(spread * math.cos(angle))
            sy = center_y + int(spread * math.sin(angle))
            alpha = int(150 * (1 - collapse_phase))
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (sx - x + size, sy - y + size), size//10)
            surface.blit(temp_surf, (x - size, y - size))
        final_size = int(size//5 * collapse_phase)
        pygame.draw.circle(surface, (220, 180, 255), (center_x, center_y), final_size + 5)
        pygame.draw.circle(surface, color, (center_x, center_y), final_size)
        return True
    
    return False
