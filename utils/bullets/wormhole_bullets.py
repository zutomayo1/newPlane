# -*- coding: utf-8 -*-
"""
Wormhole 战机子弹涂装效果渲染模块

包含以下子弹效果：
- water_vortex/spiral_ascend: 季风暴雨·水龙卷
- heat_shimmer/distortion_wave: 沙漠幻影·蜃景
- growing_branches/leaf_orbit: 盆栽之心·微观树
- warm_glow/candle_flicker: 纸灯笼·温光
- faceted_crystal/inner_glow_pulse: 晶洞爆裂·紫晶
- carved_runes/tribal_aura: 图腾柱·古灵
- ancient_text/time_echo: 遗迹石碑·古文
"""
import pygame
import math


def render_wormhole_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Wormhole战机的子弹效果
    
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
    
    if "water_vortex" in effects or "spiral_ascend" in effects:
        # 季风暴雨·水龙卷
        rotation = pygame.time.get_ticks() / 100
        # 螺旋水流（3层）
        for layer in range(3):
            spiral_points = []
            for i in range(8):
                angle = (i * 45 + layer * 30 + rotation) * 3.14159 / 180
                radius = size//6 + layer * size//12
                px = center_x + int(radius * math.cos(angle))
                py = center_y + int(radius * math.sin(angle))
                spiral_points.append((px, py))
            if len(spiral_points) > 1:
                pygame.draw.lines(surface, (100 + layer*30, 180 + layer*20, 240), False, spiral_points, 3)
        # 水滴飞溅
        for i in range(6):
            angle = (i * 60 + rotation * 2) * 3.14159 / 180
            splash_r = size//3
            sx = center_x + int(splash_r * math.cos(angle))
            sy = center_y + int(splash_r * math.sin(angle))
            pygame.draw.circle(surface, (100, 200, 255), (sx, sy), size//20)
        pygame.draw.circle(surface, color, (center_x, center_y), size//6)
        return True
    
    elif "heat_shimmer" in effects or "distortion_wave" in effects:
        # 沙漠幻影·蜃景
        time_val = pygame.time.get_ticks() / 200
        # 波浪扭曲线（4条）
        for i in range(4):
            wave_points = []
            for j in range(10):
                wx = x + j * size // 10
                wy = center_y + int(size//8 * math.sin((j + i + time_val) * 0.8))
                wave_points.append((wx, wy))
            if len(wave_points) > 1:
                alpha = 180 - i * 40
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.lines(temp_surf, (*color, alpha), False, 
                                [(px - x + size//2, py - y + size//2) for px, py in wave_points], 2)
                surface.blit(temp_surf, (x - size//4, y - size//4))
        # 幻影核心
        for i in range(3):
            offset = (i - 1) * size//8
            alpha = 150 - i * 40
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (size + offset, size), size//5)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "growing_branches" in effects or "leaf_orbit" in effects:
        # 盆栽之心·微观树
        # 树根基座
        pygame.draw.rect(surface, (100, 80, 60), (center_x - size//8, center_y + size//4, size//4, size//12))
        # 主树干（蜷曲）
        trunk_points = []
        for i in range(6):
            ty = center_y + size//4 - i * size//12
            tx = center_x + int(size//12 * math.sin(i * 0.6))
            trunk_points.append((tx, ty))
        if len(trunk_points) > 1:
            pygame.draw.lines(surface, (80, 60, 40), False, trunk_points, size//20)
        # 枝干（4条）
        for i in range(4):
            angle = (i * 90 + 45) * 3.14159 / 180
            bx = center_x + int(size//4 * math.cos(angle))
            by = center_y + int(size//4 * math.sin(angle))
            pygame.draw.line(surface, (100, 80, 60), (center_x, center_y), (bx, by), 2)
        # 绿叶环绕
        leaf_rotation = pygame.time.get_ticks() / 500
        for i in range(8):
            leaf_angle = (i * 45 + leaf_rotation * 50) * 3.14159 / 180
            lx = center_x + int(size//3 * math.cos(leaf_angle))
            ly = center_y + int(size//3 * math.sin(leaf_angle))
            pygame.draw.circle(surface, (60 + i*10, 120, 80), (lx, ly), size//15)
        return True
    
    elif "warm_glow" in effects or "candle_flicker" in effects:
        # 纸灯笼·温光
        # 六边形灯笼
        hex_points = []
        for i in range(6):
            angle = (i * 60) * 3.14159 / 180
            hx = center_x + int(size//3 * math.cos(angle))
            hy = center_y + int(size//3 * math.sin(angle))
            hex_points.append((hx, hy))
        # 绘制半透明灯笼
        temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        adjusted_hex = [(px - x + size, py - y + size) for px, py in hex_points]
        pygame.draw.polygon(temp_surf, (255, 220, 150, 200), adjusted_hex)
        surface.blit(temp_surf, (x - size, y - size))
        pygame.draw.polygon(surface, color, hex_points, 2)
        # 连接中心线
        for i in range(6):
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.line(temp_surf, (240, 200, 130, 150), 
                           (center_x - x + size, center_y - y + size), 
                           (hex_points[i][0] - x + size, hex_points[i][1] - y + size), 1)
            surface.blit(temp_surf, (x - size, y - size))
        # 温暖光晕
        flicker = int(abs(math.sin(pygame.time.get_ticks() / 100)) * 20)
        for i in range(2):
            glow_r = size//5 + i * size//8 + flicker
            alpha = 100 - i * 30
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (255, 220, 100, alpha), (size, size), glow_r)
            surface.blit(temp_surf, (x - size, y - size))
        # 烛火核心
        pygame.draw.circle(surface, (255, 200, 80), (center_x, center_y), size//8)
        pygame.draw.circle(surface, (255, 255, 200), (center_x, center_y - flicker//3), size//12)
        return True
    
    elif "faceted_crystal" in effects or "inner_glow_pulse" in effects:
        # 晶洞爆裂·紫晶
        # 多面晶体（8面）
        crystal_points = []
        for i in range(8):
            angle = (i * 45) * 3.14159 / 180
            radius = size//3 if i % 2 == 0 else size//4
            cx = center_x + int(radius * math.cos(angle))
            cy = center_y + int(radius * math.sin(angle))
            crystal_points.append((cx, cy))
        # 绘制半透明晶体
        temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        adjusted_crystal = [(px - x + size, py - y + size) for px, py in crystal_points]
        pygame.draw.polygon(temp_surf, (180, 100, 240, 200), adjusted_crystal)
        surface.blit(temp_surf, (x - size, y - size))
        pygame.draw.polygon(surface, color, crystal_points, 2)
        # 内部晶面
        for i in range(0, 8, 2):
            triangle = [(center_x, center_y), crystal_points[i], crystal_points[(i+2) % 8]]
            pygame.draw.polygon(surface, (140 + i*10, 60 + i*5, 200), triangle)
        # 紫光脉动
        pulse = int(abs(math.sin(pygame.time.get_ticks() / 150)) * size//8)
        for i in range(2):
            pulse_r = size//10 + i * size//12 + pulse
            alpha = 180 - i * 60
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (180, 100, 240, alpha), (size, size), pulse_r)
            surface.blit(temp_surf, (x - size, y - size))
        # 裂纹闪光
        for i in range(6):
            angle = (i * 60) * 3.14159 / 180
            ray_x = center_x + int(size//2.5 * math.cos(angle))
            ray_y = center_y + int(size//2.5 * math.sin(angle))
            pygame.draw.line(surface, (200, 120, 255), (center_x, center_y), (ray_x, ray_y), 2)
        return True
    
    elif "carved_runes" in effects or "tribal_aura" in effects:
        # 图腾柱·古灵
        # 图腾柱主体（2段）
        for i in range(2):
            seg_y = center_y - size//4 + i * size//3
            pygame.draw.rect(surface, (180 - i*20, 120 - i*15, 60), 
                           (center_x - size//8, seg_y, size//4, size//3 - size//12))
            pygame.draw.rect(surface, color, 
                           (center_x - size//8, seg_y, size//4, size//3 - size//12), 2)
            # 横纹
            for j in range(3):
                carve_y = seg_y + j * size//12
                pygame.draw.line(surface, (120, 80, 40), 
                               (center_x - size//10, carve_y), (center_x + size//10, carve_y), 1)
            # 图腾眼睛
            eye_y = seg_y + size//8
            pygame.draw.circle(surface, (255, 220, 150), (center_x - size//16, eye_y), size//20)
            pygame.draw.circle(surface, (255, 220, 150), (center_x + size//16, eye_y), size//20)
        # 符文发光（旋转）
        rune_rotation = pygame.time.get_ticks() / 400
        for i in range(6):
            angle = (i * 60 + rune_rotation * 50) * 3.14159 / 180
            rx = center_x + int(size//3 * math.cos(angle))
            ry = center_y + int(size//3 * math.sin(angle))
            pygame.draw.circle(surface, (255, 220, 100), (rx, ry), size//25)
        return True
    
    elif "ancient_text" in effects or "time_echo" in effects:
        # 遗迹石碑·古文
        # 破碎石板（六边形不规则）
        tablet_points = [
            (center_x - size//3, center_y - size//3),
            (center_x + size//4, center_y - size//3),
            (center_x + size//3, center_y),
            (center_x + size//4, center_y + size//3),
            (center_x - size//4, center_y + size//3),
            (center_x - size//3, center_y)
        ]
        pygame.draw.polygon(surface, (100, 110, 140), tablet_points)
        pygame.draw.polygon(surface, color, tablet_points, 2)
        # 古文字符号（简化）
        for i in range(4):
            text_x = center_x + (i % 2 - 0.5) * size//4
            text_y = center_y + (i // 2 - 0.5) * size//4
            # 竖线
            pygame.draw.line(surface, (200, 180, 150), 
                           (int(text_x), int(text_y - size//20)), (int(text_x), int(text_y + size//20)), 2)
            # 横线
            if i % 2 == 0:
                pygame.draw.line(surface, (200, 180, 150), 
                               (int(text_x - size//25), int(text_y)), (int(text_x + size//25), int(text_y)), 2)
        # 历史回响波纹
        echo_phase = (pygame.time.get_ticks() / 100) % 100 / 100
        for i in range(2):
            echo_r = int((size//4 + i * size//8) * (1 + echo_phase * 0.5))
            alpha = int((120 - i * 40) * (1 - echo_phase))
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (150, 160, 190, alpha), (size, size), echo_r, 2)
            surface.blit(temp_surf, (x - size, y - size))
        # 裂痕发光
        for i in range(3):
            angle = (i * 120 + echo_phase * 360) * 3.14159 / 180
            crack_len = size//6
            ex = center_x + int(crack_len * math.cos(angle))
            ey = center_y + int(crack_len * math.sin(angle))
            pygame.draw.line(surface, (180, 200, 230), (center_x, center_y), (ex, ey), 2)
        return True
    
    return False
