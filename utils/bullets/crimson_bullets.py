# -*- coding: utf-8 -*-
"""
Crimson 战机子弹涂装效果渲染模块

包含以下子弹效果：
- blood_blade: 血月之刃（血月）
- crimson_mist: 血雾弥漫
- katana_slash: 武士刀气（武士）
- blade_flash: 刀光闪烁
- demon_claw: 恶魔之爪（恶魔）
- blood_scratch: 血色爪痕
- hellfire_burst: 地狱烈焰（炼狱）
- inferno_wave: 炼狱波动
- rose_petal: 血玫瑰刺（玫瑰）
- thorn_spike: 尖刺荆棘
- dragon_breath: 血龙吐息（血龙）（注意与Striker同名不同效果）
- blood_scale: 血色龙鳞
- bat_swarm: 吸血蝠群（吸血鬼）
- vampire_drain: 吸血吸取
"""
import pygame
import math
import random


def render_crimson_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Crimson战机的子弹效果
    
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
    
    if "blood_blade" in effects:
        # 血月之刃：弯刀形状+血雾
        # 弯刀刀身（弧形）
        blade_points = []
        for i in range(15):
            angle = (i * 12 - 90) * 3.14159 / 180
            radius = size // 2
            px = center_x + int(radius * math.cos(angle))
            py = center_y + int(radius * math.sin(angle))
            blade_points.append((px, py))
        if len(blade_points) > 1:
            pygame.draw.lines(surface, color, False, blade_points, 5)
            pygame.draw.lines(surface, (255, 0, 0), False, blade_points, 2)
        # 刀尖
        pygame.draw.circle(surface, (150, 0, 0), (center_x, center_y - size//2), size//10)
        # 血雾粒子
        random.seed(int(pygame.time.get_ticks() / 100))
        for _ in range(5):
            mist_x = center_x + random.randint(-size//3, size//3)
            mist_y = center_y + random.randint(-size//3, size//3)
            mist_size = random.randint(2, 5)
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, 100), 
                             (mist_x - x + size, mist_y - y + size), mist_size)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "crimson_mist" in effects:
        # 血雾弥漫：血色雾气
        # 中心血珠
        pygame.draw.circle(surface, (150, 0, 0), (center_x, center_y), size//6)
        # 血雾扩散
        for i in range(5):
            radius = size//4 + i * size//10
            alpha = 150 - i * 25
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (size, size), radius)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "katana_slash" in effects:
        # 武士刀气：斜斩刀光
        # 刀光轨迹（对角线）
        x1, y1 = center_x - size//2, center_y + size//2
        x2, y2 = center_x + size//2, center_y - size//2
        # 多层刀光
        for i in range(5):
            offset = i * 2
            alpha = 220 - i * 30
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.line(temp_surf, (*color, alpha), 
                           (x1 - center_x + size + offset, y1 - center_y + size - offset),
                           (x2 - center_x + size + offset, y2 - center_y + size - offset), 6 - i)
            surface.blit(temp_surf, (x - size, y - size))
        # 刀光闪烁
        pygame.draw.line(surface, (255, 255, 255), (x1, y1), (x2, y2), 2)
        return True
    
    elif "blade_flash" in effects:
        # 刀光闪烁：闪光效果
        # 主刀光
        pygame.draw.line(surface, color, 
                       (center_x - size//2, center_y), 
                       (center_x + size//2, center_y), 6)
        pygame.draw.line(surface, (255, 255, 255), 
                       (center_x - size//2, center_y), 
                       (center_x + size//2, center_y), 2)
        # 闪光粒子
        for i in range(4):
            flash_x = center_x + (i - 1.5) * size//4
            flash_y = center_y
            pygame.draw.circle(surface, (255, 255, 255), (int(flash_x), flash_y), size//15)
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, 150), 
                             (int(flash_x) - x + size, flash_y - y + size), size//10)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "demon_claw" in effects:
        # 恶魔之爪：三爪撕裂
        # 爪痕（3条）
        for i in range(3):
            offset = (i - 1) * size//6
            x1 = center_x + offset - size//8
            y1 = center_y - size//2
            x2 = center_x + offset + size//8
            y2 = center_y + size//2
            pygame.draw.line(surface, (80, 0, 0), (x1, y1), (x2, y2), 6)
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), 3)
            pygame.draw.line(surface, (200, 0, 0), (x1, y1), (x2, y2), 1)
        return True
    
    elif "blood_scratch" in effects:
        # 血色爪痕：爪痕+血滴
        # 爪痕
        for i in range(4):
            offset = (i - 1.5) * size//8
            x1 = center_x + offset
            y1 = center_y - size//2
            x2 = center_x + offset + size//10
            y2 = center_y + size//2
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), 3)
        # 血滴
        for i in range(3):
            drop_x = center_x + (i - 1) * size//6
            drop_y = center_y + size//3
            pygame.draw.circle(surface, (150, 0, 0), (drop_x, drop_y), size//15)
            # 泪滴尾巴
            tail = [
                (drop_x, drop_y + size//15),
                (drop_x - size//30, drop_y + size//10),
                (drop_x + size//30, drop_y + size//10)
            ]
            pygame.draw.polygon(surface, (150, 0, 0), tail)
        return True
    
    elif "hellfire_burst" in effects:
        # 地狱烈焰：火焰爆发
        # 中心火核
        pygame.draw.circle(surface, (255, 255, 0), (center_x, center_y), size//8)
        pygame.draw.circle(surface, color, (center_x, center_y), size//6)
        # 爆发火焰（8个火舌）
        for i in range(8):
            angle = (i * 45) * 3.14159 / 180
            flame_length = size//2 + int(size//8 * math.sin(pygame.time.get_ticks() / 100 + i))
            x1 = center_x + int(size//8 * math.cos(angle))
            y1 = center_y + int(size//8 * math.sin(angle))
            x2 = center_x + int(flame_length * math.cos(angle))
            y2 = center_y + int(flame_length * math.sin(angle))
            # 火焰渐变
            for j in range(3):
                flame_color = [(255, 200, 0), (255, 100, 0), (200, 0, 0)][j]
                offset = j * 2
                x2_offset = center_x + int((flame_length - offset * 5) * math.cos(angle))
                y2_offset = center_y + int((flame_length - offset * 5) * math.sin(angle))
                pygame.draw.line(surface, flame_color, (x1, y1), (x2_offset, y2_offset), 4 - j)
        return True
    
    elif "inferno_wave" in effects:
        # 炼狱波动：火焰波纹
        # 波纹（4层）
        for i in range(4):
            wave_radius = size//6 + i * size//8
            alpha = 200 - i * 40
            # 火焰色渐变
            wave_color = (255, 120 - i * 20, 0)
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*wave_color, alpha), (size, size), wave_radius, 3)
            surface.blit(temp_surf, (x - size, y - size))
        # 中心
        pygame.draw.circle(surface, (255, 255, 0), (center_x, center_y), size//8)
        return True
    
    elif "rose_petal" in effects:
        # 血玫瑰刺：玫瑰花瓣
        # 花瓣（5瓣）
        for i in range(5):
            angle = (i * 72) * 3.14159 / 180
            petal_x = center_x + int(size//3 * math.cos(angle))
            petal_y = center_y + int(size//3 * math.sin(angle))
            # 心形花瓣
            petal_rect = pygame.Rect(0, 0, size//4, size//3)
            petal_rect.center = (petal_x, petal_y)
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.ellipse(temp_surf, (*color, 200), 
                              (petal_x - x - size//8 + size, petal_y - y - size//6 + size, size//4, size//3))
            surface.blit(temp_surf, (x - size, y - size))
            pygame.draw.ellipse(surface, (180, 30, 60), petal_rect, 1)
        # 花心
        pygame.draw.circle(surface, (150, 0, 40), (center_x, center_y), size//10)
        return True
    
    elif "thorn_spike" in effects:
        # 尖刺荆棘：尖刺放射
        # 中心
        pygame.draw.circle(surface, (150, 30, 60), (center_x, center_y), size//8)
        # 荆棘刺（12根）
        for i in range(12):
            angle = (i * 30) * 3.14159 / 180
            thorn_length = size//2 + (i % 3) * size//12
            x1 = center_x + int(size//8 * math.cos(angle))
            y1 = center_y + int(size//8 * math.sin(angle))
            x2 = center_x + int(thorn_length * math.cos(angle))
            y2 = center_y + int(thorn_length * math.sin(angle))
            # 尖刺（三角形）
            thorn_base = size // 15
            perp_angle = angle + 1.5708
            p1 = (x1 + int(thorn_base * math.cos(perp_angle)), 
                 y1 + int(thorn_base * math.sin(perp_angle)))
            p2 = (x1 - int(thorn_base * math.cos(perp_angle)), 
                 y1 - int(thorn_base * math.sin(perp_angle)))
            thorn = [(x2, y2), p1, p2]
            pygame.draw.polygon(surface, color, thorn)
            pygame.draw.polygon(surface, (200, 50, 80), thorn, 1)
        return True
    
    elif "blood_scale" in effects:
        # 血色龙鳞：龙鳞纹理
        # 鳞片（菱形阵列）
        for row in range(3):
            for col in range(3):
                scale_x = center_x + (col - 1) * size//4
                scale_y = center_y + (row - 1) * size//4
                scale = [
                    (scale_x, scale_y - size//12),
                    (scale_x + size//15, scale_y),
                    (scale_x, scale_y + size//12),
                    (scale_x - size//15, scale_y)
                ]
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.polygon(temp_surf, (*color, 180), 
                                  [(px - center_x + size, py - center_y + size) for px, py in scale])
                surface.blit(temp_surf, (x - size, y - size))
                pygame.draw.polygon(surface, (180, 0, 0), scale, 1)
        return True
    
    elif "bat_swarm" in effects:
        # 吸血蝠群：蝙蝠群飞
        # 蝙蝠（5只）
        for i in range(5):
            angle = (i * 72 + pygame.time.get_ticks() / 50) * 3.14159 / 180
            bat_x = center_x + int(size//3 * math.cos(angle))
            bat_y = center_y + int(size//3 * math.sin(angle))
            # 蝙蝠翅膀（简化V形）
            wing_span = size // 8
            left_wing = [
                (bat_x, bat_y),
                (bat_x - wing_span, bat_y - wing_span//2),
                (bat_x - wing_span//2, bat_y + wing_span//4)
            ]
            right_wing = [
                (bat_x, bat_y),
                (bat_x + wing_span, bat_y - wing_span//2),
                (bat_x + wing_span//2, bat_y + wing_span//4)
            ]
            pygame.draw.polygon(surface, color, left_wing)
            pygame.draw.polygon(surface, color, right_wing)
            # 蝙蝠身体
            pygame.draw.circle(surface, (80, 0, 40), (bat_x, bat_y), size//25)
        return True
    
    elif "vampire_drain" in effects:
        # 吸血吸取：血液流动
        # 中心血核
        pygame.draw.circle(surface, (120, 0, 50), (center_x, center_y), size//6)
        # 血液流（螺旋吸入）
        for i in range(8):
            angle = (i * 45 + pygame.time.get_ticks() / 20) * 3.14159 / 180
            radius_start = size // 2
            radius_end = size // 6
            # 流动轨迹
            flow_points = []
            for j in range(8):
                progress = j / 8
                radius = radius_start + (radius_end - radius_start) * progress
                px = center_x + int(radius * math.cos(angle + progress * 3.14159))
                py = center_y + int(radius * math.sin(angle + progress * 3.14159))
                flow_points.append((px, py))
            if len(flow_points) > 1:
                pygame.draw.lines(surface, color, False, flow_points, 2)
        return True
    
    return False
