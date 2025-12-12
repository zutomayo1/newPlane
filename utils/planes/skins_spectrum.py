# -*- coding: utf-8 -*-
"""
天幕虹裂·光谱 (Spectrum) - 专属涂装渲染模块
分解一切颜色的棱镜使者

涂装列表 (12种完全不同形态) - 与customization.py同步:
1. spectrum_default - 棱镜原型
2. spectrum_full_spectrum - 虹龙天翔
3. spectrum_aurora - 极光织者
4. spectrum_neon_city - 霓虹都市
5. spectrum_opal_dream - 油膜虹彩
6. spectrum_sunset_prism - 玫瑰花窗
7. spectrum_deep_ocean - 蝶翼效应
8. spectrum_crystal_rainbow - 迪斯科炼狱
9. spectrum_infrared - 通感幻觉
10. spectrum_ultraviolet - 骄傲风暴
11. spectrum_monochrome - 色差畸变
12. spectrum_chaos_spectrum - 虚空棱镜
"""
import pygame
import math
import random

SPECTRUM_STYLES = [
    "spectrum_default",
    "spectrum_full_spectrum",
    "spectrum_aurora",
    "spectrum_neon_city",
    "spectrum_opal_dream",
    "spectrum_sunset_prism",
    "spectrum_deep_ocean",
    "spectrum_crystal_rainbow",
    "spectrum_infrared",
    "spectrum_ultraviolet",
    "spectrum_monochrome",
    "spectrum_chaos_spectrum"
]


def is_spectrum_style(model_style):
    return model_style in SPECTRUM_STYLES


def render_spectrum_skin(surface, c, model_style, t, pid, static):
    if model_style not in SPECTRUM_STYLES:
        return None
    skin_id = model_style.replace("spectrum_", "")
    frame = 0 if static else int(t * 60) % 360
    draw_spectrum(surface, c, 60, 60, scale=1.8, skin_id=skin_id, frame=frame)
    return surface


def _render_spectrum_base(surface, t, pulse):
    frame = int(t * 60) % 360
    draw_spectrum(surface, (200, 200, 200), 60, 60, scale=1.8, skin_id="default", frame=frame)
    return surface


# 彩虹色谱
RAINBOW = [
    (255, 0, 0),      # 红
    (255, 127, 0),    # 橙
    (255, 255, 0),    # 黄
    (0, 255, 0),      # 绿
    (0, 127, 255),    # 青
    (0, 0, 255),      # 蓝
    (148, 0, 211),    # 紫
]


def draw_spectrum(surface, color, x, y, scale=1.0, skin_id="default", frame=0):
    cx, cy = x, y
    s = scale
    pulse = math.sin(frame * 0.1) * 3
    
    if skin_id == "default":
        _draw_default(surface, cx, cy, s, frame, pulse)
    elif skin_id == "full_spectrum":
        _draw_rainbow_dragon(surface, cx, cy, s, frame, pulse)
    elif skin_id == "aurora":
        _draw_aurora_weaver(surface, cx, cy, s, frame, pulse)
    elif skin_id == "neon_city":
        _draw_neon_metropolis(surface, cx, cy, s, frame, pulse)
    elif skin_id == "opal_dream":
        _draw_oil_slick(surface, cx, cy, s, frame, pulse)
    elif skin_id == "sunset_prism":
        _draw_stained_glass(surface, cx, cy, s, frame, pulse)
    elif skin_id == "deep_ocean":
        _draw_butterfly_effect(surface, cx, cy, s, frame, pulse)
    elif skin_id == "crystal_rainbow":
        _draw_disco_inferno(surface, cx, cy, s, frame, pulse)
    elif skin_id == "infrared":
        _draw_synesthesia(surface, cx, cy, s, frame, pulse)
    elif skin_id == "ultraviolet":
        _draw_pride_storm(surface, cx, cy, s, frame, pulse)
    elif skin_id == "monochrome":
        _draw_chromatic_aberration(surface, cx, cy, s, frame, pulse)
    elif skin_id == "chaos_spectrum":
        _draw_void_prism(surface, cx, cy, s, frame, pulse)
    else:
        _draw_default(surface, cx, cy, s, frame, pulse)


def _draw_default(surface, cx, cy, s, frame, pulse):
    """棱镜形态 - 三角棱镜分解白光成七色光谱"""
    prism_silver = (220, 225, 235)
    
    # 入射白光
    white_beam_end = cx - 18 * s
    pygame.draw.line(surface, (255, 255, 255), (cx - 50 * s, cy), (white_beam_end, cy), 4)
    # 光束发光效果
    for i in range(3):
        surf = pygame.Surface((120, 20), pygame.SRCALPHA)
        pygame.draw.line(surf, (255, 255, 255, 80 - i * 25), (10, 10), (int(50 * s), 10), 6 + i * 2)
        surface.blit(surf, (cx - 55 * s, cy - 10))
    
    # 三角棱镜
    prism_points = [
        (cx, cy - 22 * s),
        (cx - 18 * s, cy + 15 * s),
        (cx + 18 * s, cy + 15 * s),
    ]
    pygame.draw.polygon(surface, prism_silver, prism_points)
    pygame.draw.polygon(surface, (180, 185, 200), prism_points, 2)
    # 棱镜内部折射效果
    pygame.draw.line(surface, (200, 210, 230), (cx, cy - 18 * s), (cx - 5 * s, cy + 10 * s), 1)
    pygame.draw.line(surface, (200, 210, 230), (cx, cy - 18 * s), (cx + 8 * s, cy + 10 * s), 1)
    
    # 七色散射光束
    spread_start_x = cx + 15 * s
    for i, color in enumerate(RAINBOW):
        angle = -30 + i * 10 + math.sin(frame * 0.05) * 2
        rad = math.radians(angle)
        beam_len = 40 * s
        end_x = spread_start_x + math.cos(rad) * beam_len
        end_y = cy + math.sin(rad) * beam_len
        
        # 主光束
        pygame.draw.line(surface, color, (spread_start_x, cy), (int(end_x), int(end_y)), 3)
        # 发光效果
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(surf, (*color, 100), (spread_start_x, cy), (int(end_x), int(end_y)), 6)
        surface.blit(surf, (0, 0))
    
    # 棱镜高光
    pygame.draw.line(surface, (255, 255, 255), (cx - 5 * s, cy - 15 * s), (cx - 10 * s, cy), 2)


def _draw_rainbow_dragon(surface, cx, cy, s, frame, pulse):
    """虹龙天翔 - 七彩神龙的流光形态"""
    # 龙身蜿蜒（彩虹渐变）
    body_segments = 20
    for i in range(body_segments):
        seg_angle = frame * 2 + i * 15
        seg_offset = math.sin(math.radians(seg_angle)) * 10 * s
        seg_x = cx - 30 * s + i * 3.5 * s + seg_offset * 0.3
        seg_y = cy + seg_offset
        seg_size = 8 * s - abs(i - 10) * 0.4 * s
        
        color_idx = int((i + frame * 0.1) % len(RAINBOW))
        color = RAINBOW[color_idx]
        pygame.draw.circle(surface, color, (int(seg_x), int(seg_y)), int(seg_size))
    
    # 龙头
    head_x = cx + 25 * s
    head_y = cy + math.sin(frame * 0.1) * 5 * s
    head_points = [
        (head_x + 15 * s, head_y),
        (head_x, head_y - 10 * s),
        (head_x - 8 * s, head_y - 5 * s),
        (head_x - 8 * s, head_y + 5 * s),
        (head_x, head_y + 10 * s),
    ]
    # 渐变龙头
    pygame.draw.polygon(surface, (255, 100, 100), head_points)
    pygame.draw.polygon(surface, (255, 200, 100), head_points, 2)
    # 龙眼
    pygame.draw.circle(surface, (255, 255, 255), (int(head_x + 5 * s), int(head_y - 3 * s)), int(3 * s))
    pygame.draw.circle(surface, (0, 0, 0), (int(head_x + 6 * s), int(head_y - 3 * s)), int(1.5 * s))
    # 龙须
    for j in range(2):
        whisker_y = head_y + (j * 2 - 1) * 5 * s
        whisker_wave = math.sin(frame * 0.15 + j) * 5 * s
        pygame.draw.line(surface, (255, 200, 100), 
                        (head_x + 12 * s, whisker_y),
                        (head_x + 25 * s + whisker_wave, whisker_y + whisker_wave), 2)
    
    # 彩虹鳞片光效
    for i in range(12):
        scale_angle = frame * 3 + i * 30
        scale_r = 20 * s + math.sin(frame * 0.1 + i) * 5 * s
        sx = cx + math.cos(math.radians(scale_angle)) * scale_r
        sy = cy + math.sin(math.radians(scale_angle)) * scale_r
        color = RAINBOW[i % len(RAINBOW)]
        surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color, 150), (6, 6), 4)
        surface.blit(surf, (sx - 6, sy - 6))


def _draw_aurora_weaver(surface, cx, cy, s, frame, pulse):
    """极光织者 - 编织极光的神秘存在"""
    aurora_colors = [(100, 255, 150), (100, 200, 255), (180, 100, 255), (255, 100, 200)]
    
    # 织布机框架
    loom_color = (60, 50, 80)
    pygame.draw.rect(surface, loom_color, (cx - 35 * s, cy - 30 * s, 70 * s, 5 * s))
    pygame.draw.rect(surface, loom_color, (cx - 35 * s, cy + 25 * s, 70 * s, 5 * s))
    pygame.draw.rect(surface, loom_color, (cx - 38 * s, cy - 30 * s, 5 * s, 60 * s))
    pygame.draw.rect(surface, loom_color, (cx + 33 * s, cy - 30 * s, 5 * s, 60 * s))
    
    # 编织中的极光丝线
    for i in range(12):
        thread_x = cx - 30 * s + i * 5.5 * s
        wave_offset = math.sin(frame * 0.08 + i * 0.4) * 10 * s
        thread_points = []
        for j in range(10):
            ty = cy - 25 * s + j * 5.5 * s
            tx = thread_x + math.sin(frame * 0.05 + j * 0.3 + i * 0.2) * 3 * s
            thread_points.append((tx, ty))
        if len(thread_points) > 1:
            color = aurora_colors[i % len(aurora_colors)]
            pygame.draw.lines(surface, color, False, thread_points, 2)
    
    # 横向纬线
    for j in range(8):
        weft_y = cy - 20 * s + j * 6 * s
        weft_progress = (frame * 2 + j * 20) % 70
        weft_x = cx - 30 * s + weft_progress * s
        color = aurora_colors[(j + int(frame * 0.1)) % len(aurora_colors)]
        pygame.draw.circle(surface, color, (int(weft_x), int(weft_y)), int(2 * s))
        # 编织轨迹
        pygame.draw.line(surface, (*color, 150), (cx - 30 * s, weft_y), (weft_x, weft_y), 1)
    
    # 织者之手（抽象光点）
    hand_x = cx + math.sin(frame * 0.1) * 20 * s
    hand_y = cy + math.cos(frame * 0.15) * 15 * s
    for i in range(5):
        finger_angle = -60 + i * 30 + frame
        finger_len = 8 * s
        fx = hand_x + math.cos(math.radians(finger_angle)) * finger_len
        fy = hand_y + math.sin(math.radians(finger_angle)) * finger_len
        pygame.draw.line(surface, (255, 255, 200), (hand_x, hand_y), (int(fx), int(fy)), 2)
    pygame.draw.circle(surface, (255, 255, 220), (int(hand_x), int(hand_y)), int(4 * s))


def _draw_neon_metropolis(surface, cx, cy, s, frame, pulse):
    """霓虹都市 - 赛博朋克的光污染形态"""
    neon_pink = (255, 50, 150)
    neon_cyan = (50, 255, 255)
    neon_yellow = (255, 255, 50)
    dark_bg = (20, 15, 35)
    
    # 城市天际线剪影
    buildings = [
        (cx - 40 * s, 15 * s), (cx - 30 * s, 25 * s), (cx - 20 * s, 20 * s),
        (cx - 10 * s, 35 * s), (cx, 28 * s), (cx + 10 * s, 32 * s),
        (cx + 20 * s, 22 * s), (cx + 30 * s, 30 * s), (cx + 40 * s, 18 * s),
    ]
    for i, (bx, height) in enumerate(buildings):
        pygame.draw.rect(surface, dark_bg, (bx - 4 * s, cy + 20 * s - height, 8 * s, height))
        # 霓虹窗户
        for wy in range(int(height // (5 * s))):
            if random.random() > 0.3:
                window_color = random.choice([neon_pink, neon_cyan, neon_yellow])
                glow_alpha = int(150 + math.sin(frame * 0.2 + i + wy) * 100)
                wy_pos = cy + 18 * s - height + wy * 5 * s
                surf = pygame.Surface((8, 6), pygame.SRCALPHA)
                pygame.draw.rect(surf, (*window_color, min(255, glow_alpha)), (1, 1, 6, 4))
                surface.blit(surf, (bx - 3 * s, wy_pos))
    
    # 霓虹招牌
    sign_texts = [(cx - 25 * s, cy - 25 * s, neon_pink), (cx + 15 * s, cy - 15 * s, neon_cyan)]
    for sx, sy, color in sign_texts:
        # 招牌框
        pygame.draw.rect(surface, color, (sx - 8 * s, sy - 4 * s, 16 * s, 8 * s), 2)
        # 发光效果
        glow_surf = pygame.Surface((int(20 * s), int(12 * s)), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*color, 80), (0, 0, int(20 * s), int(12 * s)))
        surface.blit(glow_surf, (sx - 10 * s, sy - 6 * s))
        # 闪烁
        if frame % 20 < 15:
            pygame.draw.line(surface, color, (sx - 5 * s, sy), (sx + 5 * s, sy), 2)
    
    # 雨中霓虹反射
    for i in range(15):
        rain_x = cx - 40 * s + random.random() * 80 * s
        rain_y = (cy + 40 * s + frame * 3 + i * 20) % 80 * s - 20 * s + cy - 20 * s
        rain_color = random.choice([neon_pink, neon_cyan, neon_yellow])
        pygame.draw.line(surface, rain_color, (rain_x, rain_y), (rain_x, rain_y + 5 * s), 1)


def _draw_oil_slick(surface, cx, cy, s, frame, pulse):
    """油膜虹彩 - 薄膜干涉的迷幻色彩"""
    # 油膜基底
    pygame.draw.ellipse(surface, (30, 30, 40), (cx - 35 * s, cy - 25 * s, 70 * s, 50 * s))
    
    # 干涉条纹
    for ring in range(15):
        ring_r = 5 * s + ring * 2.5 * s
        # 颜色随角度和时间变化
        ring_hue = (frame * 2 + ring * 25) % 360
        color = pygame.Color(0)
        color.hsva = (ring_hue, 80, 100, 100)
        
        ring_surf = pygame.Surface((int(ring_r * 2 + 10), int(ring_r * 1.5 + 10)), pygame.SRCALPHA)
        pygame.draw.ellipse(ring_surf, (color.r, color.g, color.b, 100), 
                           (5, 5, int(ring_r * 2), int(ring_r * 1.4)), 2)
        surface.blit(ring_surf, (cx - ring_r - 5, cy - ring_r * 0.7 - 5))
    
    # 流动效果
    for i in range(8):
        flow_angle = frame * 1.5 + i * 45
        flow_r = 20 * s + math.sin(frame * 0.1 + i) * 10 * s
        fx = cx + math.cos(math.radians(flow_angle)) * flow_r
        fy = cy + math.sin(math.radians(flow_angle)) * flow_r * 0.6
        
        flow_hue = (frame * 3 + i * 45) % 360
        color = pygame.Color(0)
        color.hsva = (flow_hue, 90, 100, 100)
        
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(surf, (color.r, color.g, color.b, 150), (8, 8), 6)
        surface.blit(surf, (fx - 8, fy - 8))
    
    # 高光
    pygame.draw.ellipse(surface, (255, 255, 255, 100), 
                       (cx - 15 * s, cy - 15 * s, 12 * s, 8 * s))


def _draw_stained_glass(surface, cx, cy, s, frame, pulse):
    """玫瑰花窗 - 哥特教堂的神圣彩窗形态"""
    lead_color = (40, 40, 50)
    glass_colors = [(200, 50, 50), (50, 100, 200), (200, 180, 50), 
                   (50, 180, 100), (180, 50, 180), (200, 100, 50)]
    
    # 圆形主框
    pygame.draw.circle(surface, lead_color, (int(cx), int(cy)), int(38 * s), int(4 * s))
    
    # 玫瑰花瓣分割
    for i in range(8):
        petal_angle = i * 45
        rad = math.radians(petal_angle)
        # 放射线
        pygame.draw.line(surface, lead_color, (cx, cy), 
                        (cx + math.cos(rad) * 35 * s, cy + math.sin(rad) * 35 * s), int(2 * s))
        
        # 花瓣玻璃
        petal_points = []
        for j in range(5):
            p_angle = petal_angle - 20 + j * 10
            p_rad = math.radians(p_angle)
            p_r = 30 * s if j == 2 else 20 * s
            petal_points.append((
                cx + math.cos(p_rad) * p_r,
                cy + math.sin(p_rad) * p_r
            ))
        
        glass_color = glass_colors[i % len(glass_colors)]
        # 光透过效果
        glow = int(abs(math.sin(frame * 0.05 + i)) * 50)
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (*glass_color, 180 + glow), petal_points)
        surface.blit(surf, (0, 0))
    
    # 中心花蕊
    pygame.draw.circle(surface, (255, 220, 100), (int(cx), int(cy)), int(10 * s))
    pygame.draw.circle(surface, lead_color, (int(cx), int(cy)), int(10 * s), int(2 * s))
    # 内部细节
    for i in range(6):
        inner_angle = i * 60 + frame * 0.5
        inner_rad = math.radians(inner_angle)
        pygame.draw.line(surface, lead_color, (cx, cy),
                        (cx + math.cos(inner_rad) * 8 * s, cy + math.sin(inner_rad) * 8 * s), 1)
    
    # 光芒照射
    if frame % 60 < 30:
        light_alpha = int(50 + (30 - abs(frame % 60 - 15)) * 3)
        light_surf = pygame.Surface((int(80 * s), int(80 * s)), pygame.SRCALPHA)
        pygame.draw.circle(light_surf, (255, 255, 200, light_alpha), (int(40 * s), int(40 * s)), int(35 * s))
        surface.blit(light_surf, (cx - 40 * s, cy - 40 * s))


def _draw_butterfly_effect(surface, cx, cy, s, frame, pulse):
    """蝶翼效应 - 混沌理论的彩蝶形态"""
    # 蝴蝶翅膀 - 对称但复杂的图案
    for side in [-1, 1]:
        # 上翼
        upper_wing = []
        for i in range(12):
            angle = -80 + i * 15
            r = 30 * s * (1 + math.sin(math.radians(angle * 2)) * 0.3)
            r = r + math.sin(frame * 0.05 + i * 0.2) * 3 * s
            wx = cx + side * math.cos(math.radians(angle * side + 90)) * r * 0.6
            wy = cy - 10 * s + math.sin(math.radians(angle * side + 90)) * r
            upper_wing.append((wx, wy))
        
        # 翅膀颜色渐变
        wing_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        if len(upper_wing) > 2:
            # 基础色
            pygame.draw.polygon(wing_surf, (50, 50, 80, 200), upper_wing)
            surface.blit(wing_surf, (0, 0))
        
        # 翅膀花纹 - 眼斑
        for i in range(3):
            spot_dist = 12 * s + i * 8 * s
            spot_x = cx + side * spot_dist
            spot_y = cy - 15 * s + i * 5 * s
            spot_colors = [RAINBOW[i * 2 % 7], RAINBOW[(i * 2 + 1) % 7]]
            pygame.draw.circle(surface, spot_colors[0], (int(spot_x), int(spot_y)), int(5 * s - i))
            pygame.draw.circle(surface, spot_colors[1], (int(spot_x), int(spot_y)), int(3 * s - i * 0.5))
            pygame.draw.circle(surface, (255, 255, 255), (int(spot_x), int(spot_y)), int(1.5 * s))
        
        # 下翼
        lower_wing = [
            (cx, cy + 5 * s),
            (cx + side * 20 * s, cy + 25 * s),
            (cx + side * 10 * s, cy + 30 * s),
            (cx, cy + 15 * s),
        ]
        color_idx = int(frame * 0.1) % len(RAINBOW)
        pygame.draw.polygon(surface, RAINBOW[color_idx], lower_wing)
    
    # 身体
    pygame.draw.ellipse(surface, (40, 35, 50), (cx - 3 * s, cy - 20 * s, 6 * s, 40 * s))
    # 触角
    for side in [-1, 1]:
        ant_wave = math.sin(frame * 0.15) * 3 * s
        pygame.draw.line(surface, (60, 55, 70), 
                        (cx + side * 2 * s, cy - 20 * s),
                        (cx + side * 10 * s + ant_wave, cy - 32 * s), 2)
        pygame.draw.circle(surface, (80, 75, 90), 
                          (int(cx + side * 10 * s + ant_wave), int(cy - 32 * s)), int(2 * s))


def _draw_disco_inferno(surface, cx, cy, s, frame, pulse):
    """迪斯科炼狱 - 70年代的舞池狂欢"""
    # 迪斯科球
    ball_r = 20 * s
    pygame.draw.circle(surface, (180, 180, 180), (int(cx), int(cy)), int(ball_r))
    
    # 镜面瓦片
    for i in range(8):
        for j in range(6):
            tile_angle = i * 45 + frame * 2
            tile_lat = -60 + j * 24
            
            tile_x = cx + math.cos(math.radians(tile_angle)) * math.cos(math.radians(tile_lat)) * ball_r * 0.85
            tile_y = cy + math.sin(math.radians(tile_lat)) * ball_r * 0.85
            
            # 反射闪光
            brightness = int(100 + abs(math.sin(frame * 0.15 + i + j)) * 155)
            tile_color = (brightness, brightness, brightness)
            pygame.draw.rect(surface, tile_color, (tile_x - 2 * s, tile_y - 2 * s, 4 * s, 4 * s))
    
    # 旋转光束
    for i in range(6):
        beam_angle = frame * 4 + i * 60
        beam_color = RAINBOW[i % len(RAINBOW)]
        beam_len = 45 * s
        
        beam_end_x = cx + math.cos(math.radians(beam_angle)) * beam_len
        beam_end_y = cy + math.sin(math.radians(beam_angle)) * beam_len
        
        # 光束锥形
        beam_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        beam_points = [
            (cx, cy),
            (cx + math.cos(math.radians(beam_angle - 8)) * beam_len,
             cy + math.sin(math.radians(beam_angle - 8)) * beam_len),
            (cx + math.cos(math.radians(beam_angle + 8)) * beam_len,
             cy + math.sin(math.radians(beam_angle + 8)) * beam_len),
        ]
        pygame.draw.polygon(beam_surf, (*beam_color, 80), beam_points)
        surface.blit(beam_surf, (0, 0))
    
    # 地板方格
    floor_y = cy + 25 * s
    for i in range(8):
        for j in range(2):
            fx = cx - 35 * s + i * 10 * s
            fy = floor_y + j * 8 * s
            floor_color = RAINBOW[(i + j + int(frame * 0.2)) % len(RAINBOW)] if (i + j) % 2 == 0 else (30, 30, 40)
            pygame.draw.rect(surface, floor_color, (fx, fy, 9 * s, 7 * s))


def _draw_synesthesia(surface, cx, cy, s, frame, pulse):
    """通感幻觉 - 听见颜色的神经异象"""
    # 声波可视化
    for wave in range(5):
        wave_points = []
        wave_amp = 15 * s * (1 + wave * 0.3)
        wave_freq = 0.1 + wave * 0.02
        
        for i in range(40):
            wx = cx - 40 * s + i * 2 * s
            wy = cy + math.sin(frame * wave_freq + i * 0.3) * wave_amp * math.sin(i * 0.08)
            wave_points.append((wx, wy - wave * 8 * s))
        
        if len(wave_points) > 1:
            color = RAINBOW[wave % len(RAINBOW)]
            pygame.draw.lines(surface, color, False, wave_points, 2)
    
    # 神经突触闪烁
    random.seed(42)
    for i in range(15):
        neuron_x = cx + random.uniform(-35, 35) * s
        neuron_y = cy + random.uniform(-30, 30) * s
        
        # 突触活跃度
        activity = abs(math.sin(frame * 0.1 + i * 0.5))
        if activity > 0.5:
            neuron_color = RAINBOW[int(activity * len(RAINBOW)) % len(RAINBOW)]
            pygame.draw.circle(surface, neuron_color, (int(neuron_x), int(neuron_y)), int(3 * s * activity))
            
            # 连接线
            for j in range(i + 1, min(i + 3, 15)):
                n2_x = cx + random.uniform(-35, 35) * s
                n2_y = cy + random.uniform(-30, 30) * s
                if random.random() > 0.5:
                    surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(surf, (*neuron_color, 100), 
                                   (int(neuron_x), int(neuron_y)), (int(n2_x), int(n2_y)), 1)
                    surface.blit(surf, (0, 0))
    
    # 颜色音符
    notes = [(cx - 20 * s, cy - 20 * s), (cx + 15 * s, cy - 10 * s), (cx, cy + 20 * s)]
    for i, (nx, ny) in enumerate(notes):
        note_phase = (frame * 0.15 + i) % 1
        note_y = ny - note_phase * 20 * s
        color = RAINBOW[(i + int(frame * 0.1)) % len(RAINBOW)]
        # 音符形状
        pygame.draw.ellipse(surface, color, (nx - 4 * s, note_y - 3 * s, 8 * s, 6 * s))
        pygame.draw.line(surface, color, (nx + 3.5 * s, note_y), (nx + 3.5 * s, note_y - 12 * s), 2)


def _draw_pride_storm(surface, cx, cy, s, frame, pulse):
    """骄傲风暴 - 彩虹旗的力量宣言"""
    pride_colors = [(228, 3, 3), (255, 140, 0), (255, 237, 0), 
                   (0, 128, 38), (0, 77, 255), (117, 7, 135)]
    
    # 飘扬的旗帜
    flag_width = 60 * s
    flag_height = 36 * s
    stripe_height = flag_height / 6
    
    for i, color in enumerate(pride_colors):
        stripe_points = []
        for j in range(15):
            sx = cx - 30 * s + j * flag_width / 14
            wave = math.sin(frame * 0.1 + j * 0.3) * 5 * s
            sy_top = cy - 18 * s + i * stripe_height + wave
            sy_bottom = cy - 18 * s + (i + 1) * stripe_height + wave
            stripe_points.append((sx, sy_top))
        
        for j in range(14, -1, -1):
            sx = cx - 30 * s + j * flag_width / 14
            wave = math.sin(frame * 0.1 + j * 0.3) * 5 * s
            sy_bottom = cy - 18 * s + (i + 1) * stripe_height + wave
            stripe_points.append((sx, sy_bottom))
        
        if len(stripe_points) > 2:
            pygame.draw.polygon(surface, color, stripe_points)
    
    # 旗杆
    pygame.draw.rect(surface, (100, 80, 60), (cx - 33 * s, cy - 25 * s, 3 * s, 55 * s))
    
    # 力量光环
    for ring in range(len(pride_colors)):
        ring_r = 35 * s + ring * 3 * s + math.sin(frame * 0.08 + ring) * 2 * s
        ring_alpha = 100 - ring * 12
        surf = pygame.Surface((int(ring_r * 2 + 10), int(ring_r * 2 + 10)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*pride_colors[ring], ring_alpha), 
                          (int(ring_r + 5), int(ring_r + 5)), int(ring_r), 2)
        surface.blit(surf, (cx - ring_r - 5, cy - ring_r - 5))
    
    # 星星装饰
    for i in range(6):
        star_angle = frame * 2 + i * 60
        star_r = 42 * s
        star_x = cx + math.cos(math.radians(star_angle)) * star_r
        star_y = cy + math.sin(math.radians(star_angle)) * star_r
        pygame.draw.circle(surface, (255, 255, 255), (int(star_x), int(star_y)), int(2 * s))


def _draw_chromatic_aberration(surface, cx, cy, s, frame, pulse):
    """色差畸变 - 镜头边缘的光学瑕疵"""
    base_shape = [
        (cx, cy - 25 * s),
        (cx - 15 * s, cy - 10 * s),
        (cx - 20 * s, cy + 10 * s),
        (cx, cy + 20 * s),
        (cx + 20 * s, cy + 10 * s),
        (cx + 15 * s, cy - 10 * s),
    ]
    
    # RGB分离效果
    offsets = [
        (-4 * s, -2 * s, (255, 0, 0)),    # 红色偏移
        (0, 0, (0, 255, 0)),               # 绿色居中
        (4 * s, 2 * s, (0, 0, 255)),      # 蓝色偏移
    ]
    
    aberration = math.sin(frame * 0.05) * 2 * s  # 动态色差
    
    for ox, oy, color in offsets:
        offset_shape = [(p[0] + ox + aberration, p[1] + oy) for p in base_shape]
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (*color, 120), offset_shape)
        surface.blit(surf, (0, 0))
    
    # 镜头光晕
    for i in range(3):
        flare_x = cx + (i - 1) * 15 * s
        flare_y = cy - 15 * s
        flare_r = 8 * s + math.sin(frame * 0.1 + i) * 3 * s
        
        # 六边形光斑
        flare_points = []
        for j in range(6):
            angle = j * 60 + frame * 0.5
            fx = flare_x + math.cos(math.radians(angle)) * flare_r
            fy = flare_y + math.sin(math.radians(angle)) * flare_r
            flare_points.append((fx, fy))
        
        color = RAINBOW[(i * 2) % len(RAINBOW)]
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (*color, 80), flare_points)
        surface.blit(surf, (0, 0))
    
    # 边缘模糊/暗角
    vignette_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for ring in range(10):
        ring_r = 50 * s - ring * 5 * s
        alpha = ring * 8
        pygame.draw.circle(vignette_surf, (0, 0, 0, alpha), (60, 60), int(ring_r), int(5 * s))
    surface.blit(vignette_surf, (0, 0))


def _draw_void_prism(surface, cx, cy, s, frame, pulse):
    """虚空棱镜 - 吞噬并折射暗物质的形态"""
    void_black = (5, 0, 15)
    void_purple = (80, 20, 120)
    antimatter_colors = [(255, 50, 255), (50, 255, 255), (255, 255, 50)]
    
    # 虚空核心
    void_r = 15 * s
    pygame.draw.circle(surface, void_black, (int(cx), int(cy)), int(void_r))
    # 事件视界
    for ring in range(3):
        r = void_r + ring * 3 * s
        surf = pygame.Surface((int(r * 2 + 10), int(r * 2 + 10)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*void_purple, 150 - ring * 40), (int(r + 5), int(r + 5)), int(r), 2)
        surface.blit(surf, (cx - r - 5, cy - r - 5))
    
    # 暗物质棱镜结构
    prism_points = [
        (cx, cy - 30 * s),
        (cx - 25 * s, cy + 20 * s),
        (cx + 25 * s, cy + 20 * s),
    ]
    prism_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.polygon(prism_surf, (*void_purple, 100), prism_points)
    pygame.draw.polygon(prism_surf, (150, 50, 200), prism_points, 2)
    surface.blit(prism_surf, (0, 0))
    
    # 吸入的光线
    for i in range(8):
        in_angle = frame * 2 + i * 45
        in_r = 45 * s
        in_x = cx + math.cos(math.radians(in_angle)) * in_r
        in_y = cy + math.sin(math.radians(in_angle)) * in_r
        
        # 弯曲的吸入轨迹
        curve_points = []
        for t in range(10):
            t_val = t / 9
            # 螺旋吸入
            spiral_angle = in_angle + t_val * 90
            spiral_r = in_r * (1 - t_val * 0.7)
            px = cx + math.cos(math.radians(spiral_angle)) * spiral_r
            py = cy + math.sin(math.radians(spiral_angle)) * spiral_r
            curve_points.append((int(px), int(py)))
        
        if len(curve_points) > 1:
            color = antimatter_colors[i % len(antimatter_colors)]
            pygame.draw.lines(surface, color, False, curve_points, 2)
    
    # 折射出的反物质光
    for i in range(3):
        out_angle = -30 + i * 30 + math.sin(frame * 0.05) * 10
        out_r = 35 * s
        out_x = cx + math.cos(math.radians(out_angle)) * out_r
        out_y = cy - 10 * s + math.sin(math.radians(out_angle)) * out_r
        
        # 反相颜色光束
        anti_color = antimatter_colors[i]
        pygame.draw.line(surface, anti_color, (cx, cy - 5 * s), (int(out_x), int(out_y)), 3)
        # 反光粒子
        particle_x = out_x + math.cos(math.radians(out_angle)) * (frame % 20)
        particle_y = out_y + math.sin(math.radians(out_angle)) * (frame % 20)
        pygame.draw.circle(surface, anti_color, (int(particle_x), int(particle_y)), 2)
