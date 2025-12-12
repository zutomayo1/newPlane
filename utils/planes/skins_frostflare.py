# -*- coding: utf-8 -*-
"""
极昼寒界·霜曜 (Frostflare) - 专属涂装渲染模块
极地寒霜与永昼之光的交织

涂装列表 (12种完全不同形态) - 与customization.py同步:
1. frostflare_default - 极光原型
2. frostflare_absolute_zero - 绝对零度
3. frostflare_blizzard - 暴风雪怒
4. frostflare_glacier - 冰川巨灵
5. frostflare_aurora_borealis - 极光之冠
6. frostflare_ice_queen - 冰凰涅槃
7. frostflare_permafrost - 永冻之心
8. frostflare_diamond_dust - 钻石星尘
9. frostflare_polar_night - 极地哨兵
10. frostflare_frost_fire - 雪花曼陀罗
11. frostflare_crystal_palace - 水晶宫殿
12. frostflare_winter_solstice - 北极蜃景
"""
import pygame
import math
import random

FROSTFLARE_STYLES = [
    "frostflare_default",
    "frostflare_absolute_zero",
    "frostflare_blizzard",
    "frostflare_glacier",
    "frostflare_aurora_borealis",
    "frostflare_ice_queen",
    "frostflare_permafrost",
    "frostflare_diamond_dust",
    "frostflare_polar_night",
    "frostflare_frost_fire",
    "frostflare_crystal_palace",
    "frostflare_winter_solstice"
]


def is_frostflare_style(model_style):
    return model_style in FROSTFLARE_STYLES


def render_frostflare_skin(surface, c, model_style, t, pid, static):
    if model_style not in FROSTFLARE_STYLES:
        return None
    skin_id = model_style.replace("frostflare_", "")
    frame = 0 if static else int(t * 60) % 360
    draw_frostflare(surface, c, 60, 60, scale=1.8, skin_id=skin_id, frame=frame)
    return surface


def _render_frostflare_base(surface, t, pulse):
    frame = int(t * 60) % 360
    draw_frostflare(surface, (100, 180, 255), 60, 60, scale=1.8, skin_id="default", frame=frame)
    return surface


def draw_frostflare(surface, color, x, y, scale=1.0, skin_id="default", frame=0):
    cx, cy = x, y
    s = scale
    pulse = math.sin(frame * 0.1) * 3
    
    if skin_id == "default":
        _draw_default(surface, cx, cy, s, frame, pulse)
    elif skin_id == "absolute_zero":
        _draw_absolute_zero(surface, cx, cy, s, frame, pulse)
    elif skin_id == "blizzard":
        _draw_blizzard_fury(surface, cx, cy, s, frame, pulse)
    elif skin_id == "glacier":
        _draw_glacier_titan(surface, cx, cy, s, frame, pulse)
    elif skin_id == "aurora_borealis":
        _draw_aurora_crown(surface, cx, cy, s, frame, pulse)
    elif skin_id == "ice_queen":
        _draw_ice_phoenix(surface, cx, cy, s, frame, pulse)
    elif skin_id == "permafrost":
        _draw_permafrost_heart(surface, cx, cy, s, frame, pulse)
    elif skin_id == "diamond_dust":
        _draw_diamond_dust(surface, cx, cy, s, frame, pulse)
    elif skin_id == "polar_night":
        _draw_polar_sentinel(surface, cx, cy, s, frame, pulse)
    elif skin_id == "frost_fire":
        _draw_snowflake_mandala(surface, cx, cy, s, frame, pulse)
    elif skin_id == "crystal_palace":
        _draw_crystal_palace(surface, cx, cy, s, frame, pulse)
    elif skin_id == "winter_solstice":
        _draw_arctic_mirage(surface, cx, cy, s, frame, pulse)
    else:
        _draw_default(surface, cx, cy, s, frame, pulse)


def _draw_default(surface, cx, cy, s, frame, pulse):
    """极昼形态 - 冰蓝结晶机体+流动极光"""
    ice_blue = (100, 180, 255)
    frost_white = (230, 245, 255)
    aurora_green = (100, 255, 180)
    
    # 极光背景层
    for i in range(5):
        aurora_y = cy - 20 * s + i * 10 * s
        wave_offset = math.sin(frame * 0.05 + i * 0.8) * 15 * s
        aurora_points = []
        for j in range(12):
            ax = cx - 40 * s + j * 8 * s
            ay = aurora_y + math.sin(frame * 0.03 + j * 0.5 + i) * 8 * s
            aurora_points.append((ax + wave_offset * 0.3, ay))
        if len(aurora_points) > 1:
            colors = [aurora_green, (100, 200, 255), (150, 100, 255)]
            surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.lines(surf, (*colors[i % 3], 80 - i * 12), False, aurora_points, 3)
            surface.blit(surf, (0, 0))
    
    # 冰晶机翼
    for side in [-1, 1]:
        wing_points = [
            (cx + side * 8 * s, cy - 5 * s),
            (cx + side * 35 * s, cy - 15 * s),
            (cx + side * 40 * s, cy + 5 * s),
            (cx + side * 30 * s, cy + 15 * s),
            (cx + side * 12 * s, cy + 10 * s),
        ]
        pygame.draw.polygon(surface, ice_blue, wing_points)
        pygame.draw.polygon(surface, frost_white, wing_points, 2)
        # 冰晶纹理
        for i in range(3):
            fx = cx + side * (15 + i * 8) * s
            pygame.draw.line(surface, frost_white, (fx, cy - 10 * s + i * 5 * s), 
                           (fx + side * 8 * s, cy + 5 * s + i * 3 * s), 1)
    
    # 主体结晶
    body_points = [
        (cx, cy - 28 * s),
        (cx - 12 * s, cy - 8 * s),
        (cx - 10 * s, cy + 18 * s),
        (cx, cy + 22 * s),
        (cx + 10 * s, cy + 18 * s),
        (cx + 12 * s, cy - 8 * s),
    ]
    pygame.draw.polygon(surface, ice_blue, body_points)
    pygame.draw.polygon(surface, frost_white, body_points, 2)
    
    # 六角冰晶核心
    for i in range(6):
        angle = i * 60 + frame * 0.5
        r = 8 * s + pulse / 2
        hx = cx + math.cos(math.radians(angle)) * r
        hy = cy + math.sin(math.radians(angle)) * r
        pygame.draw.line(surface, frost_white, (cx, cy), (int(hx), int(hy)), 2)
    pygame.draw.circle(surface, frost_white, (int(cx), int(cy)), int(5 * s))
    pygame.draw.circle(surface, (200, 230, 255), (int(cx), int(cy)), int(3 * s))


def _draw_aurora_crown(surface, cx, cy, s, frame, pulse):
    """极光之冠 - 北极光编织的王冠形态"""
    aurora_colors = [(100, 255, 150), (100, 200, 255), (180, 100, 255), (255, 100, 200)]
    
    # 流动极光幕布
    for layer in range(6):
        curtain_points = []
        base_y = cy - 35 * s + layer * 8 * s
        for i in range(20):
            cx_offset = (i - 10) * 5 * s
            wave1 = math.sin(frame * 0.04 + i * 0.3 + layer * 0.5) * 12 * s
            wave2 = math.sin(frame * 0.06 + i * 0.5) * 5 * s
            curtain_points.append((cx + cx_offset, base_y + wave1 + wave2))
        if len(curtain_points) > 1:
            color = aurora_colors[layer % len(aurora_colors)]
            alpha = 120 - layer * 15
            surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.lines(surf, (*color, alpha), False, curtain_points, 4 - layer // 2)
            surface.blit(surf, (0, 0))
    
    # 王冠主体
    crown_points = [
        (cx - 20 * s, cy + 5 * s),
        (cx - 25 * s, cy - 10 * s),
        (cx - 15 * s, cy - 25 * s),
        (cx - 8 * s, cy - 15 * s),
        (cx, cy - 30 * s),
        (cx + 8 * s, cy - 15 * s),
        (cx + 15 * s, cy - 25 * s),
        (cx + 25 * s, cy - 10 * s),
        (cx + 20 * s, cy + 5 * s),
    ]
    pygame.draw.polygon(surface, (200, 230, 255), crown_points)
    pygame.draw.polygon(surface, (150, 200, 255), crown_points, 2)
    
    # 王冠宝石
    gem_positions = [(cx, cy - 28 * s), (cx - 15 * s, cy - 22 * s), (cx + 15 * s, cy - 22 * s)]
    for i, (gx, gy) in enumerate(gem_positions):
        color = aurora_colors[i]
        glow = int(abs(math.sin(frame * 0.1 + i)) * 50 + 200)
        pygame.draw.circle(surface, color, (int(gx), int(gy)), int(4 * s))
        pygame.draw.circle(surface, (glow, glow, glow), (int(gx), int(gy)), int(2 * s))
    
    # 底座
    base_points = [(cx - 22 * s, cy + 5 * s), (cx - 18 * s, cy + 18 * s),
                  (cx + 18 * s, cy + 18 * s), (cx + 22 * s, cy + 5 * s)]
    pygame.draw.polygon(surface, (180, 210, 240), base_points)


def _draw_glacier_titan(surface, cx, cy, s, frame, pulse):
    """冰川巨灵 - 远古冰川觉醒的巨人形态"""
    glacier_blue = (80, 140, 200)
    ancient_ice = (150, 200, 230)
    deep_ice = (40, 80, 140)
    
    # 巨人躯体
    body_points = [
        (cx, cy - 30 * s),
        (cx - 18 * s, cy - 15 * s),
        (cx - 25 * s, cy + 5 * s),
        (cx - 20 * s, cy + 25 * s),
        (cx + 20 * s, cy + 25 * s),
        (cx + 25 * s, cy + 5 * s),
        (cx + 18 * s, cy - 15 * s),
    ]
    pygame.draw.polygon(surface, glacier_blue, body_points)
    pygame.draw.polygon(surface, ancient_ice, body_points, 3)
    
    # 冰川纹理裂痕
    cracks = [
        [(cx - 15 * s, cy - 20 * s), (cx - 10 * s, cy - 5 * s), (cx - 18 * s, cy + 10 * s)],
        [(cx + 8 * s, cy - 15 * s), (cx + 15 * s, cy + 5 * s)],
        [(cx - 5 * s, cy + 5 * s), (cx + 5 * s, cy + 20 * s)],
    ]
    for crack in cracks:
        pygame.draw.lines(surface, deep_ice, False, crack, 2)
        # 裂痕发光
        glow_alpha = int(80 + math.sin(frame * 0.1) * 40)
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.lines(surf, (*ancient_ice, glow_alpha), False, crack, 4)
        surface.blit(surf, (0, 0))
    
    # 冰晶眼睛
    for side in [-1, 1]:
        eye_x = cx + side * 8 * s
        eye_y = cy - 18 * s
        pygame.draw.ellipse(surface, (200, 240, 255), 
                           (eye_x - 5 * s, eye_y - 3 * s, 10 * s, 6 * s))
        # 瞳孔光芒
        pupil_glow = int(150 + math.sin(frame * 0.15 + side) * 100)
        pygame.draw.circle(surface, (pupil_glow, 220, 255), (int(eye_x), int(eye_y)), int(2 * s))
    
    # 肩部冰刺
    for side in [-1, 1]:
        for i in range(3):
            spike_base_x = cx + side * 20 * s
            spike_base_y = cy - 10 * s + i * 8 * s
            spike_len = 15 * s - i * 3 * s
            spike_angle = side * (60 - i * 15)
            spike_tip_x = spike_base_x + math.cos(math.radians(spike_angle)) * spike_len
            spike_tip_y = spike_base_y - math.sin(math.radians(spike_angle)) * spike_len
            spike_points = [
                (spike_base_x, spike_base_y - 3 * s),
                (spike_tip_x, spike_tip_y),
                (spike_base_x, spike_base_y + 3 * s),
            ]
            pygame.draw.polygon(surface, ancient_ice, spike_points)
    
    # 寒气散发
    for i in range(8):
        mist_angle = frame * 0.5 + i * 45
        mist_r = 35 * s + math.sin(frame * 0.08 + i) * 5 * s
        mist_x = cx + math.cos(math.radians(mist_angle)) * mist_r
        mist_y = cy + math.sin(math.radians(mist_angle)) * mist_r
        mist_alpha = int(60 + math.sin(frame * 0.1 + i) * 30)
        surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(surf, (200, 230, 255, mist_alpha), (10, 10), int(5 * s))
        surface.blit(surf, (mist_x - 10, mist_y - 10))


def _draw_diamond_dust(surface, cx, cy, s, frame, pulse):
    """钻石星尘 - 无数微小冰晶的闪耀形态"""
    # 星尘粒子云
    random.seed(42)
    for i in range(50):
        dust_angle = random.random() * 360 + frame * 0.3
        dust_r = random.uniform(8, 40) * s
        dust_x = cx + math.cos(math.radians(dust_angle)) * dust_r
        dust_y = cy + math.sin(math.radians(dust_angle)) * dust_r
        # 闪烁效果
        twinkle = abs(math.sin(frame * 0.15 + i * 0.5))
        if twinkle > 0.5:
            size = int(1 + twinkle * 2)
            brightness = int(155 + twinkle * 100)
            pygame.draw.circle(surface, (brightness, brightness, 255), (int(dust_x), int(dust_y)), size)
            # 十字闪光
            if twinkle > 0.8:
                for j in range(4):
                    ray_angle = j * 90
                    ray_len = 3 * s * twinkle
                    rx = dust_x + math.cos(math.radians(ray_angle)) * ray_len
                    ry = dust_y + math.sin(math.radians(ray_angle)) * ray_len
                    pygame.draw.line(surface, (255, 255, 255), (int(dust_x), int(dust_y)), (int(rx), int(ry)), 1)
    
    # 中央钻石
    diamond_points = [
        (cx, cy - 20 * s),
        (cx - 15 * s, cy - 5 * s),
        (cx - 10 * s, cy + 15 * s),
        (cx + 10 * s, cy + 15 * s),
        (cx + 15 * s, cy - 5 * s),
    ]
    pygame.draw.polygon(surface, (200, 230, 255), diamond_points)
    pygame.draw.polygon(surface, (255, 255, 255), diamond_points, 2)
    
    # 钻石切面
    pygame.draw.line(surface, (180, 210, 240), (cx, cy - 20 * s), (cx - 8 * s, cy + 5 * s), 1)
    pygame.draw.line(surface, (180, 210, 240), (cx, cy - 20 * s), (cx + 8 * s, cy + 5 * s), 1)
    pygame.draw.line(surface, (180, 210, 240), (cx - 8 * s, cy + 5 * s), (cx + 8 * s, cy + 5 * s), 1)
    
    # 彩虹折射光
    for i in range(6):
        refract_angle = frame * 2 + i * 60
        refract_len = 25 * s
        rx = cx + math.cos(math.radians(refract_angle)) * refract_len
        ry = cy + math.sin(math.radians(refract_angle)) * refract_len
        rainbow = [(255, 100, 100), (255, 200, 100), (255, 255, 100), 
                   (100, 255, 100), (100, 200, 255), (200, 100, 255)]
        pygame.draw.line(surface, rainbow[i], (int(cx), int(cy)), (int(rx), int(ry)), 2)


def _draw_polar_sentinel(surface, cx, cy, s, frame, pulse):
    """极地哨兵 - 守护永冻的机械体形态"""
    metal_blue = (100, 130, 180)
    ice_white = (220, 235, 250)
    energy_cyan = (80, 220, 255)
    
    # 机械主体
    body_rect = (cx - 15 * s, cy - 20 * s, 30 * s, 40 * s)
    pygame.draw.rect(surface, metal_blue, body_rect)
    pygame.draw.rect(surface, ice_white, body_rect, 2)
    
    # 头部传感器
    head_points = [
        (cx - 12 * s, cy - 20 * s),
        (cx, cy - 32 * s),
        (cx + 12 * s, cy - 20 * s),
    ]
    pygame.draw.polygon(surface, metal_blue, head_points)
    pygame.draw.polygon(surface, ice_white, head_points, 2)
    # 传感器眼
    pygame.draw.circle(surface, energy_cyan, (int(cx), int(cy - 25 * s)), int(4 * s))
    scan_line = (frame % 60) / 60 * math.pi
    scan_x = cx + math.cos(scan_line) * 3 * s
    pygame.draw.circle(surface, (255, 255, 255), (int(scan_x), int(cy - 25 * s)), int(2 * s))
    
    # 肩部护甲
    for side in [-1, 1]:
        shoulder = [
            (cx + side * 15 * s, cy - 15 * s),
            (cx + side * 28 * s, cy - 10 * s),
            (cx + side * 30 * s, cy + 5 * s),
            (cx + side * 20 * s, cy + 10 * s),
        ]
        pygame.draw.polygon(surface, (80, 110, 160), shoulder)
        pygame.draw.polygon(surface, ice_white, shoulder, 2)
    
    # 冰冻射线发射器
    for side in [-1, 1]:
        emitter_x = cx + side * 25 * s
        emitter_y = cy
        pygame.draw.circle(surface, metal_blue, (int(emitter_x), int(emitter_y)), int(6 * s))
        pygame.draw.circle(surface, energy_cyan, (int(emitter_x), int(emitter_y)), int(4 * s))
        # 充能效果
        charge = (frame % 40) / 40
        if charge > 0.7:
            ring_r = (charge - 0.7) / 0.3 * 10 * s
            surf = pygame.Surface((int(ring_r * 2 + 10), int(ring_r * 2 + 10)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*energy_cyan, 150), (int(ring_r + 5), int(ring_r + 5)), int(ring_r), 2)
            surface.blit(surf, (emitter_x - ring_r - 5, emitter_y - ring_r - 5))
    
    # 能量管线
    for i in range(4):
        pipe_y = cy - 10 * s + i * 8 * s
        pygame.draw.line(surface, (60, 90, 140), (cx - 13 * s, pipe_y), (cx + 13 * s, pipe_y), 2)
        # 流动能量
        flow_x = cx - 13 * s + (frame * 2 + i * 20) % (26 * s)
        pygame.draw.circle(surface, energy_cyan, (int(flow_x), int(pipe_y)), 2)
    
    # 稳定器脚部
    for side in [-1, 1]:
        foot_points = [
            (cx + side * 10 * s, cy + 20 * s),
            (cx + side * 18 * s, cy + 30 * s),
            (cx + side * 5 * s, cy + 30 * s),
        ]
        pygame.draw.polygon(surface, metal_blue, foot_points)


def _draw_ice_phoenix(surface, cx, cy, s, frame, pulse):
    """冰凰涅槃 - 寒霜中重生的神鸟形态"""
    ice_blue = (100, 200, 255)
    crystal_white = (230, 245, 255)
    aurora_teal = (80, 255, 220)
    
    # 冰晶羽翼
    for side in [-1, 1]:
        for layer in range(3):
            wing_points = []
            wing_spread = 35 * s - layer * 5 * s
            for i in range(6):
                angle = (i * 20 - 50) * side + math.sin(frame * 0.08 + i) * 5
                dist = wing_spread - i * 3 * s
                wx = cx + side * 8 * s + math.cos(math.radians(90 + angle)) * dist
                wy = cy - 5 * s + math.sin(math.radians(90 + angle)) * dist
                wing_points.append((wx, wy))
            wing_points.append((cx + side * 8 * s, cy + 10 * s))
            alpha = 200 - layer * 50
            surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            colors = [ice_blue, (150, 220, 255), crystal_white]
            pygame.draw.polygon(surf, (*colors[layer], alpha), wing_points)
            surface.blit(surf, (0, 0))
    
    # 凤凰身体
    body = [
        (cx, cy - 25 * s),
        (cx - 10 * s, cy - 10 * s),
        (cx - 8 * s, cy + 12 * s),
        (cx, cy + 18 * s),
        (cx + 8 * s, cy + 12 * s),
        (cx + 10 * s, cy - 10 * s),
    ]
    pygame.draw.polygon(surface, ice_blue, body)
    pygame.draw.polygon(surface, crystal_white, body, 2)
    
    # 冰晶冠羽
    for i in range(5):
        crest_x = cx - 6 * s + i * 3 * s
        crest_h = 12 * s + math.sin(frame * 0.1 + i) * 3 * s
        crest_points = [
            (crest_x, cy - 25 * s),
            (crest_x - 2 * s, cy - 25 * s - crest_h * 0.6),
            (crest_x, cy - 25 * s - crest_h),
            (crest_x + 2 * s, cy - 25 * s - crest_h * 0.6),
        ]
        pygame.draw.polygon(surface, aurora_teal, crest_points)
    
    # 眼睛
    for side in [-1, 1]:
        pygame.draw.circle(surface, crystal_white, (int(cx + side * 4 * s), int(cy - 15 * s)), int(3 * s))
        pygame.draw.circle(surface, aurora_teal, (int(cx + side * 4 * s), int(cy - 15 * s)), int(1.5 * s))
    
    # 冰晶尾羽
    for i in range(7):
        tail_x = cx - 9 * s + i * 3 * s
        tail_len = 18 * s + math.sin(frame * 0.1 + i) * 5 * s
        tail_points = [
            (tail_x, cy + 18 * s),
            (tail_x - 2 * s, cy + 18 * s + tail_len * 0.7),
            (tail_x, cy + 18 * s + tail_len),
            (tail_x + 2 * s, cy + 18 * s + tail_len * 0.7),
        ]
        colors = [aurora_teal, crystal_white, ice_blue]
        pygame.draw.polygon(surface, colors[i % 3], tail_points)
    
    # 寒气粒子
    for i in range(10):
        p_angle = frame * 0.5 + i * 36
        p_r = 30 * s + math.sin(frame * 0.1 + i) * 8 * s
        px = cx + math.cos(math.radians(p_angle)) * p_r
        py = cy + math.sin(math.radians(p_angle)) * p_r
        alpha = int(100 + math.sin(frame * 0.1 + i) * 50)
        surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*aurora_teal, alpha), (5, 5), 3)
        surface.blit(surf, (px - 5, py - 5))


def _draw_crystal_palace(surface, cx, cy, s, frame, pulse):
    """水晶宫殿 - 冰雪女王的居所形态"""
    palace_blue = (120, 180, 230)
    crystal = (220, 240, 255)
    royal_purple = (150, 130, 200)
    
    # 宫殿主塔
    tower_points = [
        (cx, cy - 38 * s),
        (cx - 8 * s, cy - 25 * s),
        (cx - 12 * s, cy + 10 * s),
        (cx + 12 * s, cy + 10 * s),
        (cx + 8 * s, cy - 25 * s),
    ]
    pygame.draw.polygon(surface, palace_blue, tower_points)
    pygame.draw.polygon(surface, crystal, tower_points, 2)
    
    # 塔顶尖刺
    pygame.draw.polygon(surface, crystal, [
        (cx, cy - 45 * s), (cx - 4 * s, cy - 38 * s), (cx + 4 * s, cy - 38 * s)])
    
    # 侧翼塔楼
    for side in [-1, 1]:
        side_tower = [
            (cx + side * 20 * s, cy - 20 * s),
            (cx + side * 15 * s, cy - 10 * s),
            (cx + side * 18 * s, cy + 15 * s),
            (cx + side * 30 * s, cy + 15 * s),
            (cx + side * 32 * s, cy - 5 * s),
        ]
        pygame.draw.polygon(surface, (100, 160, 210), side_tower)
        pygame.draw.polygon(surface, crystal, side_tower, 2)
        # 小塔尖
        pygame.draw.polygon(surface, crystal, [
            (cx + side * 20 * s, cy - 28 * s),
            (cx + side * 17 * s, cy - 20 * s),
            (cx + side * 23 * s, cy - 20 * s),
        ])
    
    # 窗户发光
    windows = [(cx, cy - 18 * s), (cx, cy - 5 * s), (cx - 20 * s, cy), (cx + 20 * s, cy)]
    for wx, wy in windows:
        glow = int(150 + math.sin(frame * 0.1 + wx) * 50)
        pygame.draw.ellipse(surface, (glow, glow, 255), (wx - 3 * s, wy - 4 * s, 6 * s, 8 * s))
        pygame.draw.ellipse(surface, royal_purple, (wx - 3 * s, wy - 4 * s, 6 * s, 8 * s), 1)
    
    # 基座
    base = [(cx - 35 * s, cy + 15 * s), (cx - 30 * s, cy + 25 * s),
            (cx + 30 * s, cy + 25 * s), (cx + 35 * s, cy + 15 * s)]
    pygame.draw.polygon(surface, (90, 140, 190), base)
    pygame.draw.polygon(surface, crystal, base, 2)
    
    # 魔法光环
    for i in range(3):
        ring_r = 38 * s + i * 5 * s + math.sin(frame * 0.05 + i) * 3 * s
        ring_alpha = 80 - i * 20
        surf = pygame.Surface((int(ring_r * 2 + 10), int(ring_r * 2 + 10)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*royal_purple, ring_alpha), (int(ring_r + 5), int(ring_r + 5)), int(ring_r), 2)
        surface.blit(surf, (cx - ring_r - 5, cy - ring_r - 5))


def _draw_blizzard_fury(surface, cx, cy, s, frame, pulse):
    """暴风雪怒 - 狂暴寒流的化身形态"""
    storm_white = (240, 248, 255)
    wind_blue = (150, 200, 255)
    fury_dark = (60, 100, 160)
    
    # 漩涡风暴
    for ring in range(8):
        ring_r = 10 * s + ring * 5 * s
        ring_points = []
        for i in range(24):
            angle = i * 15 + frame * 3 - ring * 10
            wave = math.sin(math.radians(angle * 3)) * 3 * s
            px = cx + math.cos(math.radians(angle)) * (ring_r + wave)
            py = cy + math.sin(math.radians(angle)) * (ring_r + wave)
            ring_points.append((int(px), int(py)))
        alpha = 200 - ring * 20
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        if len(ring_points) > 2:
            pygame.draw.polygon(surf, (*wind_blue, alpha // 3), ring_points)
            pygame.draw.lines(surf, (*storm_white, alpha), True, ring_points, 2)
        surface.blit(surf, (0, 0))
    
    # 冰晶碎片飞旋
    random.seed(42)
    for i in range(20):
        shard_angle = frame * 4 + i * 18
        shard_r = 25 * s + random.uniform(-10, 10) * s
        sx = cx + math.cos(math.radians(shard_angle)) * shard_r
        sy = cy + math.sin(math.radians(shard_angle)) * shard_r
        shard_size = random.uniform(2, 5) * s
        # 菱形冰晶
        shard_points = [
            (sx, sy - shard_size),
            (sx - shard_size * 0.5, sy),
            (sx, sy + shard_size),
            (sx + shard_size * 0.5, sy),
        ]
        pygame.draw.polygon(surface, storm_white, shard_points)
    
    # 风暴眼核心
    pygame.draw.circle(surface, fury_dark, (int(cx), int(cy)), int(12 * s))
    pygame.draw.circle(surface, wind_blue, (int(cx), int(cy)), int(8 * s))
    # 怒目
    for side in [-1, 1]:
        pygame.draw.ellipse(surface, storm_white, 
                           (cx + side * 3 * s - 2 * s, cy - 2 * s, 4 * s, 3 * s))


def _draw_permafrost_heart(surface, cx, cy, s, frame, pulse):
    """永冻之心 - 万年寒冰的核心形态"""
    permafrost = (80, 130, 180)
    ancient_blue = (40, 80, 140)
    heart_glow = (150, 220, 255)
    
    # 外层冻土
    for layer in range(3):
        r = (35 - layer * 8) * s
        irregularity = []
        for i in range(12):
            angle = i * 30
            var = math.sin(frame * 0.02 + i + layer) * 3 * s
            irregularity.append((
                cx + math.cos(math.radians(angle)) * (r + var),
                cy + math.sin(math.radians(angle)) * (r + var)
            ))
        colors = [(100, 150, 200), permafrost, ancient_blue]
        pygame.draw.polygon(surface, colors[layer], irregularity)
    
    # 冰层断面纹理
    for i in range(5):
        line_y = cy - 20 * s + i * 10 * s
        line_wave = math.sin(frame * 0.03 + i) * 5 * s
        pygame.draw.line(surface, (60, 110, 170), 
                        (cx - 25 * s + line_wave, line_y),
                        (cx + 25 * s - line_wave, line_y), 1)
    
    # 核心心脏
    heart_beat = abs(math.sin(frame * 0.08)) * 3 * s
    heart_r = 10 * s + heart_beat
    # 心形近似
    heart_surf = pygame.Surface((int(heart_r * 3), int(heart_r * 3)), pygame.SRCALPHA)
    hcx, hcy = int(heart_r * 1.5), int(heart_r * 1.5)
    pygame.draw.circle(heart_surf, heart_glow, (hcx - int(heart_r * 0.35), hcy - int(heart_r * 0.2)), int(heart_r * 0.6))
    pygame.draw.circle(heart_surf, heart_glow, (hcx + int(heart_r * 0.35), hcy - int(heart_r * 0.2)), int(heart_r * 0.6))
    pygame.draw.polygon(heart_surf, heart_glow, [
        (hcx - int(heart_r * 0.8), hcy),
        (hcx, hcy + int(heart_r)),
        (hcx + int(heart_r * 0.8), hcy),
    ])
    surface.blit(heart_surf, (cx - heart_r * 1.5, cy - heart_r * 1.2))
    
    # 心跳脉冲波
    pulse_phase = (frame % 60) / 60
    if pulse_phase < 0.3:
        pulse_r = pulse_phase / 0.3 * 40 * s
        pulse_alpha = int(150 * (1 - pulse_phase / 0.3))
        surf = pygame.Surface((int(pulse_r * 2 + 10), int(pulse_r * 2 + 10)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*heart_glow, pulse_alpha), (int(pulse_r + 5), int(pulse_r + 5)), int(pulse_r), 2)
        surface.blit(surf, (cx - pulse_r - 5, cy - pulse_r - 5))


def _draw_snowflake_mandala(surface, cx, cy, s, frame, pulse):
    """雪花曼陀罗 - 完美对称的冰晶阵形态"""
    mandala_white = (240, 248, 255)
    mandala_blue = (130, 180, 230)
    center_cyan = (180, 240, 255)
    
    # 六重对称雪花
    for branch in range(6):
        branch_angle = branch * 60 + frame * 0.3
        rad = math.radians(branch_angle)
        
        # 主枝
        branch_len = 35 * s
        bx = cx + math.cos(rad) * branch_len
        by = cy + math.sin(rad) * branch_len
        pygame.draw.line(surface, mandala_white, (cx, cy), (int(bx), int(by)), 3)
        
        # 侧枝（3对）
        for i in range(3):
            side_dist = 10 * s + i * 8 * s
            side_len = 12 * s - i * 3 * s
            side_x = cx + math.cos(rad) * side_dist
            side_y = cy + math.sin(rad) * side_dist
            for side in [-1, 1]:
                side_angle = branch_angle + side * 60
                side_rad = math.radians(side_angle)
                sex = side_x + math.cos(side_rad) * side_len
                sey = side_y + math.sin(side_rad) * side_len
                pygame.draw.line(surface, mandala_blue, (int(side_x), int(side_y)), (int(sex), int(sey)), 2)
        
        # 末端装饰
        pygame.draw.circle(surface, center_cyan, (int(bx), int(by)), int(3 * s))
    
    # 内环装饰
    for ring in range(3):
        ring_r = 8 * s + ring * 6 * s
        for i in range(12):
            dot_angle = i * 30 + ring * 15 + frame * 0.5
            dx = cx + math.cos(math.radians(dot_angle)) * ring_r
            dy = cy + math.sin(math.radians(dot_angle)) * ring_r
            pygame.draw.circle(surface, mandala_white if ring % 2 == 0 else mandala_blue, (int(dx), int(dy)), int(2 * s))
    
    # 中心
    pygame.draw.circle(surface, center_cyan, (int(cx), int(cy)), int(6 * s))
    pygame.draw.circle(surface, mandala_white, (int(cx), int(cy)), int(3 * s))
    
    # 外围光环
    aura_r = 40 * s + math.sin(frame * 0.05) * 3 * s
    aura_surf = pygame.Surface((int(aura_r * 2 + 10), int(aura_r * 2 + 10)), pygame.SRCALPHA)
    pygame.draw.circle(aura_surf, (*mandala_blue, 60), (int(aura_r + 5), int(aura_r + 5)), int(aura_r), 2)
    surface.blit(aura_surf, (cx - aura_r - 5, cy - aura_r - 5))


def _draw_arctic_mirage(surface, cx, cy, s, frame, pulse):
    """北极蜃景 - 寒光折射的幻象形态"""
    mirage_colors = [(200, 230, 255), (180, 210, 250), (160, 190, 245)]
    
    # 多重幻影层
    for ghost in range(4):
        ghost_offset_x = math.sin(frame * 0.05 + ghost * 0.8) * 8 * s
        ghost_offset_y = math.cos(frame * 0.07 + ghost) * 5 * s
        ghost_alpha = 150 - ghost * 35
        
        ghost_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 幻影机体
        body = [
            (cx + ghost_offset_x, cy - 25 * s + ghost_offset_y),
            (cx - 12 * s + ghost_offset_x, cy - 5 * s + ghost_offset_y),
            (cx - 10 * s + ghost_offset_x, cy + 15 * s + ghost_offset_y),
            (cx + 10 * s + ghost_offset_x, cy + 15 * s + ghost_offset_y),
            (cx + 12 * s + ghost_offset_x, cy - 5 * s + ghost_offset_y),
        ]
        color = mirage_colors[ghost % 3]
        pygame.draw.polygon(ghost_surf, (*color, ghost_alpha), body)
        # 翼幻影
        for side in [-1, 1]:
            wing = [
                (cx + side * 10 * s + ghost_offset_x, cy + ghost_offset_y),
                (cx + side * 35 * s + ghost_offset_x, cy - 10 * s + ghost_offset_y),
                (cx + side * 30 * s + ghost_offset_x, cy + 10 * s + ghost_offset_y),
            ]
            pygame.draw.polygon(ghost_surf, (*color, ghost_alpha), wing)
        surface.blit(ghost_surf, (0, 0))
    
    # 折射光线
    for i in range(8):
        ray_angle = frame * 1.5 + i * 45
        ray_start_r = 15 * s
        ray_end_r = 40 * s
        ray_bend = math.sin(frame * 0.1 + i) * 15
        
        rx1 = cx + math.cos(math.radians(ray_angle)) * ray_start_r
        ry1 = cy + math.sin(math.radians(ray_angle)) * ray_start_r
        rx2 = cx + math.cos(math.radians(ray_angle + ray_bend)) * ray_end_r
        ry2 = cy + math.sin(math.radians(ray_angle + ray_bend)) * ray_end_r
        
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(surf, (200, 230, 255, 100), (int(rx1), int(ry1)), (int(rx2), int(ry2)), 2)
        surface.blit(surf, (0, 0))


def _draw_absolute_zero(surface, cx, cy, s, frame, pulse):
    """绝对零度 - 热寂前的最终形态"""
    void_black = (5, 5, 15)
    zero_blue = (80, 120, 180)
    entropy_white = (200, 210, 230)
    
    # 热寂虚空
    void_surf = pygame.Surface((int(80 * s), int(80 * s)), pygame.SRCALPHA)
    pygame.draw.circle(void_surf, void_black, (int(40 * s), int(40 * s)), int(38 * s))
    surface.blit(void_surf, (cx - 40 * s, cy - 40 * s))
    
    # 最后的能量涟漪
    for ring in range(5):
        ring_phase = (frame * 0.5 + ring * 15) % 60
        ring_r = ring_phase * 0.7 * s
        ring_alpha = max(0, int(150 - ring_phase * 2.5))
        if ring_alpha > 0:
            surf = pygame.Surface((int(ring_r * 2 + 10), int(ring_r * 2 + 10)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*zero_blue, ring_alpha), (int(ring_r + 5), int(ring_r + 5)), int(ring_r), 1)
            surface.blit(surf, (cx - ring_r - 5, cy - ring_r - 5))
    
    # 冻结的时间晶格
    for i in range(6):
        for j in range(6):
            gx = cx - 25 * s + i * 10 * s
            gy = cy - 25 * s + j * 10 * s
            dist = math.hypot(gx - cx, gy - cy)
            if dist < 35 * s:
                # 时间越靠近中心越冻结
                freeze = 1 - dist / (35 * s)
                brightness = int(40 + freeze * 80)
                pygame.draw.circle(surface, (brightness, brightness + 20, brightness + 40), (int(gx), int(gy)), 1)
    
    # 零点核心
    core_r = 12 * s
    # 分子运动停止的视觉
    for layer in range(4):
        r = core_r - layer * 2 * s
        colors = [entropy_white, zero_blue, (40, 60, 100), void_black]
        pygame.draw.circle(surface, colors[layer], (int(cx), int(cy)), int(r))
    
    # 量子涨落
    random.seed(frame // 30)
    if frame % 30 < 5:
        for i in range(3):
            qx = cx + random.uniform(-20, 20) * s
            qy = cy + random.uniform(-20, 20) * s
            pygame.draw.circle(surface, entropy_white, (int(qx), int(qy)), 2)
    
    # 0K标识
    font_surf = pygame.Surface((30, 20), pygame.SRCALPHA)
    pygame.draw.circle(font_surf, zero_blue, (8, 10), 6, 1)  # 0
    pygame.draw.line(font_surf, zero_blue, (18, 5), (18, 15), 2)  # K的竖
    pygame.draw.line(font_surf, zero_blue, (18, 10), (25, 5), 2)
    pygame.draw.line(font_surf, zero_blue, (18, 10), (25, 15), 2)
    surface.blit(font_surf, (cx - 15, cy + 18 * s))
