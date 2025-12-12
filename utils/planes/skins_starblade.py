# -*- coding: utf-8 -*-
"""
浮游刃环·星镰 (Starblade) - 专属涂装渲染模块
钛银星尘的环刃战机，以回旋镰刃收割敌人

涂装列表 (12种完全不同形态):
1. starblade_default - 星尘原型（钛银机身+星尘蓝环刃）
2. starblade_chrome - 镀铬利刃（纯镜面反射）
3. starblade_nebula - 星云漩涡（紫蓝星云纹理）
4. starblade_golden - 黄金收割者（金色麦穗镰刀）
5. starblade_blood - 血月镰刀（深红血染）
6. starblade_crystal - 水晶切割（透明棱镜折射）
7. starblade_shadow - 暗影刺客（隐匿黑刃）
8. starblade_electric - 电弧切割（高压电流）
9. starblade_jade - 翡翠玉环（东方玉石）
10. starblade_phoenix - 凤凰羽刃（火焰羽翼）
11. starblade_frost - 霜寒刃环（冰霜附魔）
12. starblade_void - 虚空裂隙（次元切割）
"""
import pygame
import math
import random

# Starblade涂装样式列表
STARBLADE_STYLES = [
    "starblade_default",
    "starblade_chrome",
    "starblade_nebula",
    "starblade_golden",
    "starblade_blood",
    "starblade_crystal",
    "starblade_shadow",
    "starblade_electric",
    "starblade_jade",
    "starblade_phoenix",
    "starblade_frost",
    "starblade_void"
]


def is_starblade_style(model_style):
    """检查是否为 Starblade 涂装样式"""
    return model_style in STARBLADE_STYLES


def render_starblade_skin(surface, c, model_style, t, pid, static):
    """渲染 Starblade 专属涂装"""
    if model_style not in STARBLADE_STYLES:
        return None
    
    skin_id = model_style.replace("starblade_", "")
    frame = 0 if static else int(t * 60) % 360
    draw_starblade(surface, c, 60, 60, scale=1.8, skin_id=skin_id, frame=frame)
    return surface


def _render_starblade_base(surface, t, pulse):
    """基础机体渲染（用于base.py调用）"""
    frame = int(t * 60) % 360
    draw_starblade(surface, (180, 200, 220), 60, 60, scale=1.8, skin_id="default", frame=frame)


def draw_starblade(surface, color, x, y, scale=1.0, skin_id="default", frame=0):
    """绘制星镰 - 12种独特形态"""
    cx, cy = x, y
    s = scale
    pulse = math.sin(frame * 0.1) * 3
    
    if skin_id == "default":
        _draw_default(surface, cx, cy, s, frame, pulse)
    elif skin_id == "chrome":
        _draw_chrome(surface, cx, cy, s, frame, pulse)
    elif skin_id == "nebula":
        _draw_nebula(surface, cx, cy, s, frame, pulse)
    elif skin_id == "golden":
        _draw_golden(surface, cx, cy, s, frame, pulse)
    elif skin_id == "blood":
        _draw_blood(surface, cx, cy, s, frame, pulse)
    elif skin_id == "crystal":
        _draw_crystal(surface, cx, cy, s, frame, pulse)
    elif skin_id == "shadow":
        _draw_shadow(surface, cx, cy, s, frame, pulse)
    elif skin_id == "electric":
        _draw_electric(surface, cx, cy, s, frame, pulse)
    elif skin_id == "jade":
        _draw_jade(surface, cx, cy, s, frame, pulse)
    elif skin_id == "phoenix":
        _draw_phoenix(surface, cx, cy, s, frame, pulse)
    elif skin_id == "frost":
        _draw_frost(surface, cx, cy, s, frame, pulse)
    elif skin_id == "void":
        _draw_void(surface, cx, cy, s, frame, pulse)
    else:
        _draw_default(surface, cx, cy, s, frame, pulse)


def _draw_ring_blade(surface, cx, cy, s, radius, blade_count, ring_color, blade_color, rotation, thickness=3):
    """绘制通用环刃"""
    # 环体
    pygame.draw.circle(surface, ring_color, (int(cx), int(cy)), int(radius * s), int(thickness * s))
    
    # 刀刃
    for i in range(blade_count):
        angle = rotation + i * (360 / blade_count)
        rad = math.radians(angle)
        
        # 刃尖向外
        blade_inner = radius - 2
        blade_outer = radius + 10
        blade_width = 15
        
        # 刀刃形状（弧形）
        blade_points = [
            (cx + math.cos(rad) * blade_inner * s, cy + math.sin(rad) * blade_inner * s),
            (cx + math.cos(rad - 0.2) * (blade_inner + 3) * s, cy + math.sin(rad - 0.2) * (blade_inner + 3) * s),
            (cx + math.cos(rad) * blade_outer * s, cy + math.sin(rad) * blade_outer * s),
            (cx + math.cos(rad + 0.2) * (blade_inner + 3) * s, cy + math.sin(rad + 0.2) * (blade_inner + 3) * s),
        ]
        pygame.draw.polygon(surface, blade_color, blade_points)


def _draw_default(surface, cx, cy, s, frame, pulse):
    """星尘原型 - 钛银机身+星尘蓝环刃"""
    titanium = (200, 210, 220)
    stardust_blue = (100, 180, 255)
    core_white = (240, 245, 255)
    accent_cyan = (0, 200, 255)
    
    # 外层环刃
    rotation = frame * 2
    _draw_ring_blade(surface, cx, cy, s, 25, 6, titanium, stardust_blue, rotation)
    
    # 内层逆转环
    inner_rotation = -frame * 1.5
    pygame.draw.circle(surface, titanium, (int(cx), int(cy)), int(16 * s), int(2 * s))
    for i in range(4):
        angle = inner_rotation + i * 90
        rad = math.radians(angle)
        blade_x = cx + math.cos(rad) * 16 * s
        blade_y = cy + math.sin(rad) * 16 * s
        pygame.draw.circle(surface, stardust_blue, (int(blade_x), int(blade_y)), int(4 * s))
    
    # 核心
    pygame.draw.circle(surface, stardust_blue, (int(cx), int(cy)), int(10 * s))
    pygame.draw.circle(surface, core_white, (int(cx), int(cy)), int(6 * s))
    
    # 星尘粒子
    for i in range(8):
        particle_angle = frame * 3 + i * 45
        particle_r = 20 * s + math.sin(frame * 0.15 + i) * 5 * s
        px = cx + math.cos(math.radians(particle_angle)) * particle_r
        py = cy + math.sin(math.radians(particle_angle)) * particle_r
        pygame.draw.circle(surface, accent_cyan, (int(px), int(py)), int(2 * s))


def _draw_chrome(surface, cx, cy, s, frame, pulse):
    """镀铬利刃 - 纯镜面反射效果"""
    chrome_light = (240, 245, 250)
    chrome_mid = (180, 190, 200)
    chrome_dark = (100, 110, 120)
    reflect_white = (255, 255, 255)
    
    # 镜面环刃
    rotation = frame * 1.8
    _draw_ring_blade(surface, cx, cy, s, 26, 6, chrome_mid, chrome_light, rotation)
    
    # 反光条纹
    for i in range(3):
        reflect_angle = frame * 0.5 + i * 120
        rad = math.radians(reflect_angle)
        start_r = 18 * s
        end_r = 32 * s
        pygame.draw.line(surface, reflect_white,
                        (cx + math.cos(rad) * start_r, cy + math.sin(rad) * start_r),
                        (cx + math.cos(rad) * end_r, cy + math.sin(rad) * end_r), int(2 * s))
    
    # 内环
    pygame.draw.circle(surface, chrome_dark, (int(cx), int(cy)), int(15 * s), int(3 * s))
    
    # 核心镜面球
    pygame.draw.circle(surface, chrome_mid, (int(cx), int(cy)), int(10 * s))
    pygame.draw.circle(surface, chrome_light, (int(cx), int(cy)), int(6 * s))
    # 高光
    pygame.draw.circle(surface, reflect_white, (int(cx - 2 * s), int(cy - 2 * s)), int(3 * s))


def _draw_nebula(surface, cx, cy, s, frame, pulse):
    """星云漩涡 - 紫蓝星云纹理"""
    nebula_purple = (120, 60, 180)
    nebula_blue = (60, 100, 200)
    nebula_pink = (200, 100, 180)
    star_white = (255, 255, 255)
    
    # 星云光晕
    for layer in range(4):
        r = int((32 - layer * 5) * s)
        alpha = 80 - layer * 15
        color = nebula_purple if layer % 2 == 0 else nebula_blue
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 漩涡环刃
    rotation = frame * 1.5
    for i in range(6):
        angle = rotation + i * 60
        rad = math.radians(angle)
        blade_r = 24 * s
        bx = cx + math.cos(rad) * blade_r
        by = cy + math.sin(rad) * blade_r
        # 漩涡刃
        swirl_points = [
            (bx, by),
            (bx + math.cos(rad - 0.5) * 8 * s, by + math.sin(rad - 0.5) * 8 * s),
            (bx + math.cos(rad) * 12 * s, by + math.sin(rad) * 12 * s),
            (bx + math.cos(rad + 0.5) * 8 * s, by + math.sin(rad + 0.5) * 8 * s),
        ]
        pygame.draw.polygon(surface, nebula_pink, swirl_points)
    
    # 核心
    pygame.draw.circle(surface, nebula_blue, (int(cx), int(cy)), int(12 * s))
    pygame.draw.circle(surface, nebula_purple, (int(cx), int(cy)), int(8 * s))
    
    # 星点
    for i in range(12):
        star_angle = frame * 2 + i * 30
        star_r = 20 * s + math.sin(frame * 0.1 + i * 0.5) * 8 * s
        sx = cx + math.cos(math.radians(star_angle)) * star_r
        sy = cy + math.sin(math.radians(star_angle)) * star_r
        pygame.draw.circle(surface, star_white, (int(sx), int(sy)), int(1.5 * s))


def _draw_golden(surface, cx, cy, s, frame, pulse):
    """黄金收割者 - 金色麦穗镰刀"""
    gold = (255, 215, 0)
    dark_gold = (180, 140, 20)
    bronze = (200, 150, 80)
    wheat = (240, 220, 150)
    
    # 麦穗装饰
    for i in range(6):
        angle = i * 60 + 30
        rad = math.radians(angle)
        wheat_r = 30 * s
        wx = cx + math.cos(rad) * wheat_r
        wy = cy + math.sin(rad) * wheat_r
        # 麦穗
        for j in range(4):
            kernel_y = wy - j * 3 * s
            pygame.draw.ellipse(surface, wheat, (wx - 2 * s, kernel_y - 2 * s, 4 * s, 4 * s))
    
    # 金色镰刀环刃
    rotation = frame * 1.2
    _draw_ring_blade(surface, cx, cy, s, 24, 4, dark_gold, gold, rotation, thickness=4)
    
    # 内环
    pygame.draw.circle(surface, bronze, (int(cx), int(cy)), int(14 * s), int(3 * s))
    
    # 核心
    pygame.draw.circle(surface, gold, (int(cx), int(cy)), int(10 * s))
    pygame.draw.circle(surface, dark_gold, (int(cx), int(cy)), int(6 * s))
    
    # 金光闪烁
    sparkle_angle = frame * 3
    sparkle_r = 8 * s
    sx = cx + math.cos(math.radians(sparkle_angle)) * sparkle_r
    sy = cy + math.sin(math.radians(sparkle_angle)) * sparkle_r
    pygame.draw.circle(surface, (255, 255, 200), (int(sx), int(sy)), int(3 * s))


def _draw_blood(surface, cx, cy, s, frame, pulse):
    """血月镰刀 - 深红血染"""
    blood_red = (150, 20, 30)
    dark_blood = (80, 10, 20)
    crimson = (200, 40, 50)
    black = (30, 10, 15)
    
    # 血滴效果
    for i in range(5):
        drop_angle = i * 72 + frame * 0.5
        rad = math.radians(drop_angle)
        drop_r = 28 * s
        dx = cx + math.cos(rad) * drop_r
        dy = cy + math.sin(rad) * drop_r
        drop_len = 8 * s + math.sin(frame * 0.2 + i) * 3 * s
        pygame.draw.ellipse(surface, blood_red, (dx - 2 * s, dy, 4 * s, drop_len))
    
    # 血色环刃
    rotation = frame * 2
    _draw_ring_blade(surface, cx, cy, s, 24, 6, dark_blood, crimson, rotation)
    
    # 内环（锯齿）
    for i in range(12):
        angle = frame + i * 30
        rad = math.radians(angle)
        inner_r = 14 * s
        outer_r = 17 * s if i % 2 == 0 else 14 * s
        pygame.draw.line(surface, blood_red,
                        (cx + math.cos(rad) * inner_r, cy + math.sin(rad) * inner_r),
                        (cx + math.cos(rad) * outer_r, cy + math.sin(rad) * outer_r), int(2 * s))
    
    # 核心
    pygame.draw.circle(surface, dark_blood, (int(cx), int(cy)), int(10 * s))
    pygame.draw.circle(surface, crimson, (int(cx), int(cy)), int(6 * s))
    pygame.draw.circle(surface, black, (int(cx), int(cy)), int(3 * s))


def _draw_crystal(surface, cx, cy, s, frame, pulse):
    """水晶切割 - 透明棱镜折射"""
    crystal_clear = (220, 240, 255)
    prism_blue = (150, 200, 255)
    prism_pink = (255, 180, 220)
    prism_green = (180, 255, 200)
    
    # 棱镜折射光
    for i in range(6):
        angle = frame * 0.8 + i * 60
        rad = math.radians(angle)
        ray_r = 35 * s
        colors = [prism_blue, prism_pink, prism_green]
        color = colors[i % 3]
        alpha = int(100 + 50 * math.sin(frame * 0.15 + i))
        ray_surf = pygame.Surface((int(ray_r), int(8 * s)), pygame.SRCALPHA)
        pygame.draw.rect(ray_surf, (*color[:3], alpha), (0, 0, int(ray_r), int(8 * s)))
        rotated = pygame.transform.rotate(ray_surf, -angle)
        surface.blit(rotated, (cx - rotated.get_width() // 2, cy - rotated.get_height() // 2))
    
    # 水晶环刃
    rotation = frame * 1.5
    for i in range(6):
        angle = rotation + i * 60
        rad = math.radians(angle)
        blade_r = 25 * s
        bx = cx + math.cos(rad) * blade_r
        by = cy + math.sin(rad) * blade_r
        # 水晶刃（多边形）
        crystal_points = [
            (bx + math.cos(rad) * 10 * s, by + math.sin(rad) * 10 * s),
            (bx + math.cos(rad - 0.4) * 5 * s, by + math.sin(rad - 0.4) * 5 * s),
            (bx + math.cos(rad + 0.4) * 5 * s, by + math.sin(rad + 0.4) * 5 * s),
        ]
        pygame.draw.polygon(surface, crystal_clear, crystal_points)
        pygame.draw.polygon(surface, prism_blue, crystal_points, 1)
    
    # 核心棱镜
    pygame.draw.circle(surface, prism_blue, (int(cx), int(cy)), int(12 * s))
    pygame.draw.circle(surface, crystal_clear, (int(cx), int(cy)), int(8 * s))
    
    # 高光
    pygame.draw.circle(surface, (255, 255, 255), (int(cx - 2 * s), int(cy - 2 * s)), int(3 * s))


def _draw_shadow(surface, cx, cy, s, frame, pulse):
    """暗影刺客 - 隐匿黑刃"""
    shadow_black = (20, 20, 30)
    dark_purple = (60, 30, 80)
    stealth_gray = (80, 80, 100)
    eye_red = (200, 50, 50)
    
    # 阴影扩散
    for layer in range(4):
        r = int((30 - layer * 4) * s + pulse * 0.5)
        alpha = 60 - layer * 12
        shadow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (*shadow_black[:3], alpha), (r + 2, r + 2), r)
        surface.blit(shadow_surf, (cx - r - 2, cy - r - 2))
    
    # 暗影环刃（时隐时现）
    rotation = frame * 2.5
    visibility = 0.5 + 0.5 * math.sin(frame * 0.1)
    for i in range(6):
        if (i + int(frame / 10)) % 3 == 0:  # 部分刃隐形
            continue
        angle = rotation + i * 60
        rad = math.radians(angle)
        blade_r = 24 * s
        bx = cx + math.cos(rad) * blade_r
        by = cy + math.sin(rad) * blade_r
        blade_points = [
            (bx, by),
            (bx + math.cos(rad - 0.3) * 6 * s, by + math.sin(rad - 0.3) * 6 * s),
            (bx + math.cos(rad) * 12 * s, by + math.sin(rad) * 12 * s),
            (bx + math.cos(rad + 0.3) * 6 * s, by + math.sin(rad + 0.3) * 6 * s),
        ]
        pygame.draw.polygon(surface, stealth_gray, blade_points)
    
    # 内环
    pygame.draw.circle(surface, dark_purple, (int(cx), int(cy)), int(14 * s), int(2 * s))
    
    # 核心
    pygame.draw.circle(surface, shadow_black, (int(cx), int(cy)), int(10 * s))
    
    # 刺客之眼
    eye_pulse = math.sin(frame * 0.15) * 2 * s
    pygame.draw.circle(surface, eye_red, (int(cx), int(cy)), int(4 * s + eye_pulse))
    pygame.draw.circle(surface, (255, 100, 100), (int(cx), int(cy)), int(2 * s))


def _draw_electric(surface, cx, cy, s, frame, pulse):
    """电弧切割 - 高压电流"""
    electric_blue = (0, 150, 255)
    lightning_white = (220, 240, 255)
    arc_cyan = (0, 255, 255)
    core_yellow = (255, 255, 150)
    
    # 电弧放射
    for i in range(8):
        arc_angle = frame * 5 + i * 45
        rad = math.radians(arc_angle)
        # 锯齿形电弧
        points = [(cx, cy)]
        current_x, current_y = cx, cy
        for j in range(5):
            seg_angle = arc_angle + random.Random(frame // 5 + i * 100 + j).randint(-30, 30)
            seg_rad = math.radians(seg_angle)
            seg_len = (5 + j * 3) * s
            current_x += math.cos(seg_rad) * seg_len
            current_y += math.sin(seg_rad) * seg_len
            points.append((current_x, current_y))
        
        if len(points) > 2:
            pygame.draw.lines(surface, electric_blue, False, points, int(2 * s))
            pygame.draw.lines(surface, lightning_white, False, points, int(1 * s))
    
    # 电弧环刃
    rotation = frame * 3
    _draw_ring_blade(surface, cx, cy, s, 22, 6, electric_blue, arc_cyan, rotation)
    
    # 电流核心
    for layer in range(3):
        r = int((12 - layer * 3) * s + pulse * 0.6)
        pygame.draw.circle(surface, electric_blue, (int(cx), int(cy)), r)
    pygame.draw.circle(surface, core_yellow, (int(cx), int(cy)), int(5 * s))


def _draw_jade(surface, cx, cy, s, frame, pulse):
    """翡翠玉环 - 东方玉石"""
    jade_green = (100, 200, 130)
    pale_jade = (180, 230, 200)
    deep_jade = (50, 120, 80)
    gold_trim = (220, 180, 80)
    
    # 玉环
    pygame.draw.circle(surface, jade_green, (int(cx), int(cy)), int(26 * s), int(6 * s))
    pygame.draw.circle(surface, pale_jade, (int(cx), int(cy)), int(24 * s), int(2 * s))
    
    # 金边装饰
    for i in range(8):
        angle = i * 45
        rad = math.radians(angle)
        gold_r = 26 * s
        gx = cx + math.cos(rad) * gold_r
        gy = cy + math.sin(rad) * gold_r
        pygame.draw.circle(surface, gold_trim, (int(gx), int(gy)), int(3 * s))
    
    # 旋转玉片
    rotation = frame * 0.8
    for i in range(4):
        angle = rotation + i * 90
        rad = math.radians(angle)
        piece_r = 18 * s
        px = cx + math.cos(rad) * piece_r
        py = cy + math.sin(rad) * piece_r
        # 玉片
        jade_points = [
            (px + math.cos(rad) * 8 * s, py + math.sin(rad) * 8 * s),
            (px + math.cos(rad - 0.5) * 4 * s, py + math.sin(rad - 0.5) * 4 * s),
            (px + math.cos(rad + 0.5) * 4 * s, py + math.sin(rad + 0.5) * 4 * s),
        ]
        pygame.draw.polygon(surface, pale_jade, jade_points)
        pygame.draw.polygon(surface, deep_jade, jade_points, 1)
    
    # 核心
    pygame.draw.circle(surface, jade_green, (int(cx), int(cy)), int(10 * s))
    pygame.draw.circle(surface, pale_jade, (int(cx), int(cy)), int(6 * s))


def _draw_phoenix(surface, cx, cy, s, frame, pulse):
    """凤凰羽刃 - 火焰羽翼"""
    phoenix_orange = (255, 150, 50)
    flame_red = (255, 80, 30)
    flame_yellow = (255, 220, 100)
    ember = (255, 100, 50)
    
    # 火焰光晕
    for layer in range(3):
        r = int((32 - layer * 6) * s + pulse)
        alpha = 80 - layer * 20
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*phoenix_orange[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 羽刃
    rotation = frame * 1.5
    for i in range(6):
        angle = rotation + i * 60
        rad = math.radians(angle)
        feather_r = 25 * s
        fx = cx + math.cos(rad) * feather_r
        fy = cy + math.sin(rad) * feather_r
        # 羽毛形状
        feather_points = [
            (fx + math.cos(rad) * 12 * s, fy + math.sin(rad) * 12 * s),
            (fx + math.cos(rad - 0.4) * 4 * s, fy + math.sin(rad - 0.4) * 4 * s),
            (fx, fy),
            (fx + math.cos(rad + 0.4) * 4 * s, fy + math.sin(rad + 0.4) * 4 * s),
        ]
        pygame.draw.polygon(surface, phoenix_orange, feather_points)
        pygame.draw.polygon(surface, flame_red, feather_points, 1)
    
    # 核心火焰
    for layer in range(3):
        r = int((12 - layer * 3) * s + pulse * 0.5)
        color = [flame_yellow, phoenix_orange, flame_red][layer]
        pygame.draw.circle(surface, color, (int(cx), int(cy)), r)
    
    # 火星
    for i in range(6):
        spark_angle = frame * 4 + i * 60
        spark_r = 18 * s + math.sin(frame * 0.2 + i) * 6 * s
        sx = cx + math.cos(math.radians(spark_angle)) * spark_r
        sy = cy + math.sin(math.radians(spark_angle)) * spark_r
        pygame.draw.circle(surface, ember, (int(sx), int(sy)), int(2 * s))


def _draw_frost(surface, cx, cy, s, frame, pulse):
    """霜寒刃环 - 冰霜附魔"""
    ice_blue = (150, 220, 255)
    frost_white = (230, 245, 255)
    deep_ice = (80, 150, 200)
    snow = (255, 255, 255)
    
    # 冰霜粒子
    for i in range(10):
        snow_angle = frame * 1.5 + i * 36
        snow_r = 28 * s + math.sin(frame * 0.1 + i) * 8 * s
        sx = cx + math.cos(math.radians(snow_angle)) * snow_r
        sy = cy + math.sin(math.radians(snow_angle)) * snow_r
        alpha = int(150 + 50 * math.sin(frame * 0.2 + i))
        snow_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(snow_surf, (*snow[:3], alpha), (4, 4), int(2 * s))
        surface.blit(snow_surf, (sx - 4, sy - 4))
    
    # 冰晶环刃
    rotation = frame * 1.2
    for i in range(6):
        angle = rotation + i * 60
        rad = math.radians(angle)
        blade_r = 24 * s
        bx = cx + math.cos(rad) * blade_r
        by = cy + math.sin(rad) * blade_r
        # 六边形冰晶
        crystal_points = []
        for j in range(6):
            c_angle = angle + j * 60
            c_rad = math.radians(c_angle)
            cr = 8 * s if j % 2 == 0 else 5 * s
            crystal_points.append((bx + math.cos(c_rad) * cr, by + math.sin(c_rad) * cr))
        pygame.draw.polygon(surface, frost_white, crystal_points)
        pygame.draw.polygon(surface, ice_blue, crystal_points, 1)
    
    # 冰环
    pygame.draw.circle(surface, ice_blue, (int(cx), int(cy)), int(16 * s), int(2 * s))
    
    # 核心
    pygame.draw.circle(surface, deep_ice, (int(cx), int(cy)), int(10 * s))
    pygame.draw.circle(surface, frost_white, (int(cx), int(cy)), int(6 * s))


def _draw_void(surface, cx, cy, s, frame, pulse):
    """虚空裂隙 - 次元切割"""
    void_purple = (60, 20, 100)
    rift_cyan = (0, 200, 220)
    dark_void = (20, 5, 40)
    star_white = (220, 220, 255)
    
    # 次元裂隙
    for i in range(4):
        rift_angle = i * 90 + frame * 0.8
        rad = math.radians(rift_angle)
        rift_len = 35 * s
        # 裂隙
        rift_points = [
            (cx, cy),
            (cx + math.cos(rad - 0.15) * rift_len, cy + math.sin(rad - 0.15) * rift_len),
            (cx + math.cos(rad) * (rift_len + 5 * s), cy + math.sin(rad) * (rift_len + 5 * s)),
            (cx + math.cos(rad + 0.15) * rift_len, cy + math.sin(rad + 0.15) * rift_len),
        ]
        pygame.draw.polygon(surface, rift_cyan, rift_points)
    
    # 虚空环刃
    rotation = frame * 2
    for i in range(6):
        angle = rotation + i * 60
        rad = math.radians(angle)
        blade_r = 22 * s
        bx = cx + math.cos(rad) * blade_r
        by = cy + math.sin(rad) * blade_r
        # 虚空刃
        blade_points = [
            (bx + math.cos(rad) * 10 * s, by + math.sin(rad) * 10 * s),
            (bx + math.cos(rad - 0.3) * 4 * s, by + math.sin(rad - 0.3) * 4 * s),
            (bx, by),
            (bx + math.cos(rad + 0.3) * 4 * s, by + math.sin(rad + 0.3) * 4 * s),
        ]
        pygame.draw.polygon(surface, void_purple, blade_points)
        pygame.draw.polygon(surface, rift_cyan, blade_points, 1)
    
    # 核心
    for layer in range(3):
        r = int((12 - layer * 3) * s + pulse * 0.4)
        pygame.draw.circle(surface, void_purple, (int(cx), int(cy)), r)
    pygame.draw.circle(surface, rift_cyan, (int(cx), int(cy)), int(5 * s))
    
    # 星尘
    for i in range(8):
        star_angle = frame * 2 + i * 45
        star_r = 18 * s + math.sin(frame * 0.15 + i) * 6 * s
        sx = cx + math.cos(math.radians(star_angle)) * star_r
        sy = cy + math.sin(math.radians(star_angle)) * star_r
        pygame.draw.circle(surface, star_white, (int(sx), int(sy)), int(1.5 * s))
