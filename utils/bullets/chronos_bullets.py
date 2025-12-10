# -*- coding: utf-8 -*-
"""
Chronos 战机子弹涂装效果渲染模块

包含以下子弹效果：
- time_ripple/chrono_freeze: 时钟表盘
- reverse_trail/time_rewind: 逆转螺旋
- season_cycle/day_night_shift: 纪元日历
- sand_flow/hourglass_flip: 沙漏
- space_crack/causality_break: 悖论漩涡
- echo_trail/resonance: 回声波纹
- infinite_loop/holy_glow: 永恒莫比乌斯环
"""
import pygame
import math


def render_chronos_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Chronos战机的子弹效果
    
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
    
    if "time_ripple" in effects or "chrono_freeze" in effects:
        # 时钟表盘
        # 时钟圆盘
        pygame.draw.circle(surface, (200, 200, 230), (center_x, center_y), size//3)
        pygame.draw.circle(surface, color, (center_x, center_y), size//3, 2)
        # 时钟刻度（12个）
        for i in range(12):
            angle = (i * 30 - 90) * 3.14159 / 180
            r1 = size//4 if i % 3 == 0 else int(size//3.5)
            r2 = size//3
            x1 = center_x + int(r1 * math.cos(angle))
            y1 = center_y + int(r1 * math.sin(angle))
            x2 = center_x + int(r2 * math.cos(angle))
            y2 = center_y + int(r2 * math.sin(angle))
            width = 2 if i % 3 == 0 else 1
            pygame.draw.line(surface, (100, 100, 160), (x1, y1), (x2, y2), width)
        # 时针（向上指12点）
        pygame.draw.line(surface, (60, 60, 120), (center_x, center_y), 
                       (center_x, center_y - size//4), 3)
        # 时间波纹
        pulse = (pygame.time.get_ticks() / 300) % 100 / 100
        ripple_r = int(size//3 + pulse * size//6)
        alpha = int(150 * (1 - pulse))
        temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surf, (*color, alpha), (size, size), ripple_r, 2)
        surface.blit(temp_surf, (x - size//2, y - size//2))
        return True
    
    elif "reverse_trail" in effects or "time_rewind" in effects:
        # 逆转螺旋
        # 逆时针螺旋
        rotation = -pygame.time.get_ticks() / 300  # 负值表示逆时针
        for arm in range(2):
            spiral_points = []
            arm_offset = arm * 180
            for i in range(8):
                angle = (rotation * 50 + i * 30 + arm_offset) * 3.14159 / 180
                radius = size//8 + i * size//40
                sx = center_x + int(radius * math.cos(angle))
                sy = center_y + int(radius * math.sin(angle))
                spiral_points.append((sx, sy))
            if len(spiral_points) > 1:
                pygame.draw.lines(surface, (180, 150, 255), False, spiral_points, 3)
        # 中心倒带标记（⏪）
        pygame.draw.circle(surface, color, (center_x, center_y), size//6)
        # 双箭头
        for offset in [-size//12, size//20]:
            arrow = [
                (center_x + offset, center_y),
                (center_x - size//8 + offset, center_y - size//15),
                (center_x - size//8 + offset, center_y + size//15)
            ]
            pygame.draw.polygon(surface, (100, 70, 150), arrow)
        return True
    
    elif "season_cycle" in effects or "day_night_shift" in effects:
        # 纪元日历
        # 日历页面
        page_rect = (center_x - size//3, int(center_y - size//2.5), size*2//3, size)
        pygame.draw.rect(surface, (240, 240, 250), page_rect, border_radius=5)
        pygame.draw.rect(surface, color, page_rect, 2, border_radius=5)
        # 四季色块（4象限）
        season_colors = [(120, 220, 120), (255, 200, 80), (200, 120, 80), (220, 220, 255)]
        for i, season_color in enumerate(season_colors):
            angle = (i * 90 + 45) * 3.14159 / 180
            sx = center_x + int(size//5 * math.cos(angle))
            sy = center_y + int(size//5 * math.sin(angle))
            pygame.draw.circle(surface, season_color, (sx, sy), size//12)
        # 太阳（左上）
        sun_x, sun_y = center_x - size//4, center_y - size//4
        pygame.draw.circle(surface, (255, 255, 100), (sun_x, sun_y), size//15)
        for j in range(6):
            ray_angle = (j * 60) * 3.14159 / 180
            ray_x = sun_x + int(size//10 * math.cos(ray_angle))
            ray_y = sun_y + int(size//10 * math.sin(ray_angle))
            pygame.draw.line(surface, (255, 255, 100), (sun_x, sun_y), (ray_x, ray_y), 1)
        # 月亮（右下）
        moon_x, moon_y = center_x + size//4, center_y + size//4
        pygame.draw.circle(surface, (200, 200, 240), (moon_x, moon_y), size//15)
        return True
    
    elif "sand_flow" in effects or "hourglass_flip" in effects:
        # 沙漏
        # 沙漏外框（上三角）
        hourglass_top = [
            (center_x - size//3, int(center_y - size//2.5)),
            (center_x + size//3, int(center_y - size//2.5)),
            (center_x, center_y)
        ]
        pygame.draw.polygon(surface, (200, 180, 140), hourglass_top)
        pygame.draw.polygon(surface, color, hourglass_top, 2)
        # 下三角
        hourglass_bottom = [
            (center_x, center_y),
            (center_x - size//3, int(center_y + size//2.5)),
            (center_x + size//3, int(center_y + size//2.5))
        ]
        pygame.draw.polygon(surface, (200, 180, 140), hourglass_bottom)
        pygame.draw.polygon(surface, color, hourglass_bottom, 2)
        # 流动沙子
        sand_phase = (pygame.time.get_ticks() / 100) % 100 / 100
        # 上半部少量沙粒
        for i in range(3):
            sand_x = center_x + (i - 1) * size//10
            sand_y = center_y - size//3 + int(sand_phase * size//6)
            pygame.draw.circle(surface, (220, 200, 120), (sand_x, sand_y), 2)
        # 下半部较多沙粒
        for i in range(8):
            sand_x = center_x + ((i % 3) - 1) * size//12
            sand_y = center_y + size//6 + (i // 3) * size//12
            pygame.draw.circle(surface, (220, 200, 120), (sand_x, sand_y), 2)
        return True
    
    elif "space_crack" in effects or "causality_break" in effects:
        # 悖论漩涡（无限符号∞）
        # 左环
        left_center = (center_x - size//4, center_y)
        pygame.draw.circle(surface, color, left_center, size//5, 3)
        # 右环
        right_center = (center_x + size//4, center_y)
        pygame.draw.circle(surface, color, right_center, size//5, 3)
        # 中心连接点
        pygame.draw.circle(surface, color, (center_x, center_y), size//8)
        # 时空裂痕（放射）
        for i in range(8):
            angle = (i * 45 + pygame.time.get_ticks() / 100) * 3.14159 / 180
            x1 = center_x + int(size//3 * math.cos(angle))
            y1 = center_y + int(size//3 * math.sin(angle))
            x2 = center_x + int(size//2 * math.cos(angle))
            y2 = center_y + int(size//2 * math.sin(angle))
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.line(temp_surf, (200, 150, 255, 180), 
                           (x1 - x + size, y1 - y + size), 
                           (x2 - x + size, y2 - y + size), 1)
            surface.blit(temp_surf, (x - size, y - size))
        # 因果破碎闪电
        for i in range(4):
            angle = (i * 90) * 3.14159 / 180
            bolt_points = [(center_x, center_y)]
            for j in range(2):
                radius = (j + 1) * size//6
                bx = center_x + int(radius * math.cos(angle))
                by = center_y + int(radius * math.sin(angle))
                bolt_points.append((bx, by))
            if len(bolt_points) > 1:
                pygame.draw.lines(surface, (255, 200, 255), False, bolt_points, 1)
        return True
    
    elif "echo_trail" in effects or "resonance" in effects:
        # 回声波纹
        # 主波形核心
        pygame.draw.circle(surface, (180, 200, 255), (center_x, center_y), size//6)
        pygame.draw.circle(surface, color, (center_x, center_y), size//8)
        # 波纹（虚线效果）
        for i in range(3):
            wave_r = size//4 + i * size//10
            alpha = 200 - i * 50
            # 虚线波纹
            for angle_deg in range(0, 360, 30):
                angle = angle_deg * 3.14159 / 180
                x1 = center_x + int(wave_r * math.cos(angle))
                y1 = center_y + int(wave_r * math.sin(angle))
                x2 = center_x + int((wave_r + size//20) * math.cos(angle))
                y2 = center_y + int((wave_r + size//20) * math.sin(angle))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.line(temp_surf, (*color, alpha), 
                               (x1 - x + size, y1 - y + size), 
                               (x2 - x + size, y2 - y + size), 1)
                surface.blit(temp_surf, (x - size, y - size))
        # 音叉共振
        fork_y = center_y - size//3
        # 音叉柄
        pygame.draw.rect(surface, (160, 180, 220), (center_x - 2, fork_y, 4, size//5))
        # 音叉两臂
        pygame.draw.line(surface, (160, 180, 220), 
                       (center_x - size//10, fork_y - size//12), (center_x - size//10, fork_y), 2)
        pygame.draw.line(surface, (160, 180, 220), 
                       (center_x + size//10, fork_y - size//12), (center_x + size//10, fork_y), 2)
        return True
    
    elif "infinite_loop" in effects or "holy_glow" in effects:
        # 永恒莫比乌斯环
        # 两个相交的圆（8字形）
        left_loop = (center_x - size//4, center_y)
        right_loop = (center_x + size//4, center_y)
        pygame.draw.circle(surface, color, left_loop, size//4, 4)
        pygame.draw.circle(surface, color, right_loop, size//4, 4)
        # 中心交点
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//10)
        pygame.draw.circle(surface, color, (center_x, center_y), size//12)
        # 环上运动点
        for i in range(4):
            angle = (i * 90 + pygame.time.get_ticks() / 20) * 3.14159 / 180
            loop_x = center_x + (size//4 if i % 2 == 0 else -size//4)
            px = loop_x + int(size//4 * math.cos(angle))
            py = center_y + int(size//4 * math.sin(angle))
            pygame.draw.circle(surface, (200, 200, 255), (px, py), 3)
        # 神圣光辉（外发光）
        glow_pulse = abs(math.sin(pygame.time.get_ticks() / 300))
        for i in range(2):
            glow_r = size//2 + i * size//8 + int(glow_pulse * size//10)
            alpha = int((100 - i * 40) * glow_pulse)
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (255, 255, 255, alpha), (size, size), glow_r, 2)
            surface.blit(temp_surf, (x - size//2, y - size//2))
        return True
    
    return False
