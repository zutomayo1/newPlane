# -*- coding: utf-8 -*-
"""
星渊火陨·赫利俄斯 (Helios) - 专属涂装渲染模块
太阳神的化身，以炽热的星焰焚尽一切

涂装列表 (12种完全不同形态) - 与customization.py同步:
1. helios_default - 日冕原型（金红日冕+太阳黑子核心）
2. helios_solar_flare - 太阳耀斑（日珥环绕的耀眼光芒）
3. helios_magma_core - 熔岩之心（岩浆流动的火山裂纹）
4. helios_sunset_god - 黄昏神使（橙紫渐变暮光）
5. helios_white_dwarf - 白矮星核（致密引力透镜）
6. helios_red_giant - 红巨星（膨胀的星云光晕）
7. helios_supernova - 超新星（恒星爆发的璀璨）
8. helios_obsidian_sun - 黑曜太阳（暗焰蚀光）
9. helios_plasma_storm - 等离子风暴（电浆磁场线）
10. helios_ancient_flame - 远古圣焰（青铜符文永恒之火）
11. helios_celestial_forge - 天炉熔铸（神匠锻造之地）
12. helios_frozen_sun - 冰封太阳（霜火悖论）
"""
import pygame
import math
import random

# Helios涂装样式列表 - 与customization.py保持一致
HELIOS_STYLES = [
    "helios_default",
    "helios_solar_flare",
    "helios_magma_core",
    "helios_sunset_god",
    "helios_white_dwarf",
    "helios_red_giant",
    "helios_supernova",
    "helios_obsidian_sun",
    "helios_plasma_storm",
    "helios_ancient_flame",
    "helios_celestial_forge",
    "helios_frozen_sun"
]


def is_helios_style(model_style):
    """检查是否为 Helios 涂装样式"""
    return model_style in HELIOS_STYLES


def render_helios_skin(surface, c, model_style, t, pid, static):
    """渲染 Helios 专属涂装"""
    if model_style not in HELIOS_STYLES:
        return None
    
    skin_id = model_style.replace("helios_", "")
    frame = 0 if static else int(t * 60) % 360
    draw_helios(surface, c, 60, 60, scale=1.8, skin_id=skin_id, frame=frame)
    return surface


def _render_helios_base(surface, t, pulse):
    """渲染 Helios 基础外形"""
    frame = int(t * 60) % 360
    draw_helios(surface, (255, 150, 50), 60, 60, scale=1.8, skin_id="default", frame=frame)
    return surface


def draw_helios(surface, color, x, y, scale=1.0, skin_id="default", frame=0):
    """绘制赫利俄斯 - 12种独特形态"""
    cx, cy = x, y
    s = scale
    pulse = math.sin(frame * 0.1) * 3
    
    if skin_id == "default":
        _draw_default(surface, cx, cy, s, frame, pulse)
    elif skin_id == "solar_flare":
        _draw_solar_deity(surface, cx, cy, s, frame, pulse)
    elif skin_id == "magma_core":
        _draw_magma_titan(surface, cx, cy, s, frame, pulse)
    elif skin_id == "sunset_god":
        _draw_phoenix_rebirth(surface, cx, cy, s, frame, pulse)
    elif skin_id == "white_dwarf":
        _draw_plasma_core(surface, cx, cy, s, frame, pulse)
    elif skin_id == "red_giant":
        _draw_infernal_emperor(surface, cx, cy, s, frame, pulse)
    elif skin_id == "supernova":
        _draw_supernova(surface, cx, cy, s, frame, pulse)
    elif skin_id == "obsidian_sun":
        _draw_binary_star(surface, cx, cy, s, frame, pulse)
    elif skin_id == "plasma_storm":
        _draw_solar_eclipse(surface, cx, cy, s, frame, pulse)
    elif skin_id == "ancient_flame":
        _draw_forge_god(surface, cx, cy, s, frame, pulse)
    elif skin_id == "celestial_forge":
        _draw_cosmic_furnace(surface, cx, cy, s, frame, pulse)
    elif skin_id == "frozen_sun":
        _draw_neutron_star(surface, cx, cy, s, frame, pulse)
    else:
        _draw_default(surface, cx, cy, s, frame, pulse)


def _draw_default(surface, cx, cy, s, frame, pulse):
    """太阳神形态 - 金红日冕环绕，中央太阳黑子漩涡"""
    # 外层日冕 - 放射状火焰
    for i in range(16):
        angle = i * 22.5 + frame * 0.5
        rad = math.radians(angle)
        inner_r = 25 * s
        outer_r = 38 * s + math.sin(frame * 0.15 + i) * 8 * s
        x1 = cx + math.cos(rad) * inner_r
        y1 = cy + math.sin(rad) * inner_r
        x2 = cx + math.cos(rad) * outer_r
        y2 = cy + math.sin(rad) * outer_r
        # 火焰渐变
        for j in range(5):
            t_val = j / 5
            px = x1 + (x2 - x1) * t_val
            py = y1 + (y2 - y1) * t_val
            color_r = int(255 - t_val * 55)
            color_g = int(200 - t_val * 130)
            color_b = int(50 - t_val * 30)
            pygame.draw.circle(surface, (color_r, color_g, max(0, color_b)), (int(px), int(py)), int(4 * s - j * 0.5))
    
    # 日珥喷发 - 弧形等离子体
    for i in range(3):
        arc_angle = frame * 0.8 + i * 120
        arc_rad = math.radians(arc_angle)
        arc_x = cx + math.cos(arc_rad) * 20 * s
        arc_y = cy + math.sin(arc_rad) * 20 * s
        arc_height = 15 * s + math.sin(frame * 0.2 + i) * 5 * s
        arc_surf = pygame.Surface((int(30 * s), int(arc_height * 2)), pygame.SRCALPHA)
        pygame.draw.arc(arc_surf, (255, 180, 80, 180), (0, 0, int(30 * s), int(arc_height * 2)), 
                       0, math.pi, int(3 * s))
        rotated = pygame.transform.rotate(arc_surf, -arc_angle)
        surface.blit(rotated, (arc_x - rotated.get_width() // 2, arc_y - rotated.get_height() // 2))
    
    # 太阳主体 - 多层渐变
    for layer in range(5):
        r = int((22 - layer * 3) * s + pulse / 2)
        alpha = 255 - layer * 30
        color = (255, 200 - layer * 25, 100 - layer * 15, alpha)
        surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (r + 2, r + 2), r)
        surface.blit(surf, (cx - r - 2, cy - r - 2))
    
    # 太阳黑子漩涡
    for i in range(3):
        spot_angle = frame * 0.3 + i * 120
        spot_dist = 8 * s
        spot_x = cx + math.cos(math.radians(spot_angle)) * spot_dist
        spot_y = cy + math.sin(math.radians(spot_angle)) * spot_dist
        pygame.draw.circle(surface, (80, 40, 20), (int(spot_x), int(spot_y)), int(3 * s))
        # 黑子周围的磁场线
        for j in range(4):
            mag_angle = j * 90 + frame
            mag_x = spot_x + math.cos(math.radians(mag_angle)) * 5 * s
            mag_y = spot_y + math.sin(math.radians(mag_angle)) * 5 * s
            pygame.draw.line(surface, (150, 80, 40), (int(spot_x), int(spot_y)), (int(mag_x), int(mag_y)), 1)


def _draw_solar_deity(surface, cx, cy, s, frame, pulse):
    """日轮圣驾 - 埃及太阳神Ra的金色战车形态"""
    gold = (255, 215, 0)
    royal_blue = (30, 50, 120)
    turquoise = (64, 224, 208)
    
    # 圣甲虫翼展 - 埃及风格翅膀
    for side in [-1, 1]:
        wing_points = []
        for i in range(7):
            wing_x = cx + side * (12 + i * 6) * s
            wing_y = cy + math.sin(i * 0.5 + frame * 0.08) * 5 * s - 5 * s + i * 2 * s
            wing_points.append((wing_x, wing_y))
        wing_points.append((cx + side * 48 * s, cy + 10 * s))
        wing_points.append((cx + side * 10 * s, cy + 5 * s))
        pygame.draw.polygon(surface, gold, wing_points)
        pygame.draw.polygon(surface, (180, 150, 0), wing_points, 2)
        # 翼上的羽毛纹理
        for i in range(5):
            fx = cx + side * (18 + i * 7) * s
            fy = cy - 2 * s + i * 2 * s
            pygame.draw.line(surface, royal_blue, (fx, fy), (fx + side * 5 * s, fy + 8 * s), 2)
    
    # 日轮盘 - 大型太阳圆盘
    pygame.draw.circle(surface, (255, 180, 50), (int(cx), int(cy - 8 * s)), int(18 * s))
    pygame.draw.circle(surface, gold, (int(cx), int(cy - 8 * s)), int(14 * s))
    # 眼纹（荷鲁斯之眼简化）
    pygame.draw.ellipse(surface, royal_blue, (cx - 8 * s, cy - 14 * s, 16 * s, 10 * s))
    pygame.draw.circle(surface, turquoise, (int(cx), int(cy - 10 * s)), int(4 * s))
    pygame.draw.circle(surface, (0, 0, 0), (int(cx), int(cy - 10 * s)), int(2 * s))
    
    # 眼镜蛇冠（圣蛇）
    snake_wave = math.sin(frame * 0.15) * 3 * s
    snake_points = [
        (cx, cy - 26 * s),
        (cx - 3 * s + snake_wave, cy - 32 * s),
        (cx, cy - 38 * s),
        (cx + 3 * s - snake_wave, cy - 32 * s),
    ]
    pygame.draw.polygon(surface, gold, snake_points)
    pygame.draw.circle(surface, (255, 50, 50), (int(cx), int(cy - 36 * s)), int(2 * s))
    
    # 法老胸甲
    chest_points = [(cx, cy + 2 * s), (cx - 12 * s, cy + 15 * s), 
                   (cx, cy + 25 * s), (cx + 12 * s, cy + 15 * s)]
    pygame.draw.polygon(surface, royal_blue, chest_points)
    pygame.draw.polygon(surface, gold, chest_points, 2)
    # 圣甲虫图案
    pygame.draw.ellipse(surface, turquoise, (cx - 5 * s, cy + 8 * s, 10 * s, 12 * s))
    
    # 放射光芒
    for i in range(12):
        ray_angle = i * 30 + frame
        ray_len = 45 * s + math.sin(frame * 0.1 + i) * 5 * s
        rx = cx + math.cos(math.radians(ray_angle)) * ray_len
        ry = cy - 8 * s + math.sin(math.radians(ray_angle)) * ray_len
        pygame.draw.line(surface, (255, 220, 100, 150), (cx, cy - 8 * s), (int(rx), int(ry)), 2)


def _draw_supernova(surface, cx, cy, s, frame, pulse):
    """超新星爆发 - 恒星死亡时的壮丽爆炸"""
    # 冲击波环
    for ring in range(4):
        ring_phase = (frame * 2 + ring * 20) % 100
        ring_r = ring_phase * 0.5 * s
        ring_alpha = max(0, 200 - ring_phase * 2)
        if ring_alpha > 0:
            surf = pygame.Surface((int(ring_r * 2 + 10), int(ring_r * 2 + 10)), pygame.SRCALPHA)
            colors = [(255, 100, 50), (255, 200, 100), (200, 150, 255), (100, 200, 255)]
            pygame.draw.circle(surf, (*colors[ring], ring_alpha), (int(ring_r + 5), int(ring_r + 5)), int(ring_r), 3)
            surface.blit(surf, (cx - ring_r - 5, cy - ring_r - 5))
    
    # 物质喷射 - 对称射流
    for side in [-1, 1]:
        jet_length = 35 * s + pulse * 2
        jet_points = [
            (cx, cy),
            (cx + side * 8 * s, cy - side * 15 * s),
            (cx + side * 5 * s, cy - side * jet_length),
            (cx, cy - side * (jet_length - 10 * s))
        ]
        jet_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(jet_surf, (255, 180, 100, 200), jet_points)
        surface.blit(jet_surf, (0, 0))
    
    # 碎片云
    random.seed(42)
    for i in range(25):
        debris_angle = random.random() * 360 + frame * 0.5
        debris_dist = random.uniform(15, 40) * s
        debris_x = cx + math.cos(math.radians(debris_angle)) * debris_dist
        debris_y = cy + math.sin(math.radians(debris_angle)) * debris_dist
        debris_size = random.uniform(1, 4) * s
        debris_color = random.choice([(255, 200, 100), (200, 100, 50), (255, 255, 200)])
        pygame.draw.circle(surface, debris_color, (int(debris_x), int(debris_y)), int(debris_size))
    
    # 中央残骸 - 脉动核心
    core_pulse = 8 * s + math.sin(frame * 0.2) * 4 * s
    pygame.draw.circle(surface, (255, 255, 255), (int(cx), int(cy)), int(core_pulse))
    pygame.draw.circle(surface, (200, 220, 255), (int(cx), int(cy)), int(core_pulse * 0.7))
    pygame.draw.circle(surface, (150, 180, 255), (int(cx), int(cy)), int(core_pulse * 0.4))


def _draw_magma_titan(surface, cx, cy, s, frame, pulse):
    """熔岩泰坦 - 由熔融岩浆构成的巨人形态"""
    rock_dark = (50, 30, 25)
    rock_light = (80, 50, 40)
    magma_orange = (255, 140, 50)
    magma_yellow = (255, 220, 100)
    
    # 巨人轮廓 - 厚重岩石躯体
    body_points = [
        (cx, cy - 28 * s),  # 头顶
        (cx - 15 * s, cy - 15 * s),  # 左肩
        (cx - 22 * s, cy + 5 * s),  # 左臂
        (cx - 18 * s, cy + 20 * s),  # 左下
        (cx + 18 * s, cy + 20 * s),  # 右下
        (cx + 22 * s, cy + 5 * s),  # 右臂
        (cx + 15 * s, cy - 15 * s),  # 右肩
    ]
    pygame.draw.polygon(surface, rock_dark, body_points)
    pygame.draw.polygon(surface, rock_light, body_points, 3)
    
    # 裂缝中的岩浆光芒
    crack_points = [
        [(cx - 12 * s, cy - 20 * s), (cx - 8 * s, cy - 5 * s), (cx - 15 * s, cy + 10 * s)],
        [(cx + 5 * s, cy - 15 * s), (cx + 10 * s, cy + 5 * s), (cx + 8 * s, cy + 18 * s)],
        [(cx - 5 * s, cy + 5 * s), (cx + 2 * s, cy + 15 * s)],
    ]
    for crack in crack_points:
        glow_intensity = int(180 + math.sin(frame * 0.15) * 75)
        pygame.draw.lines(surface, (glow_intensity, int(glow_intensity * 0.5), 50), False, crack, 3)
        pygame.draw.lines(surface, magma_yellow, False, crack, 1)
    
    # 熔岩眼睛
    for side in [-1, 1]:
        eye_x = cx + side * 6 * s
        eye_y = cy - 18 * s
        eye_glow = int(200 + math.sin(frame * 0.2 + side) * 55)
        pygame.draw.ellipse(surface, (eye_glow, int(eye_glow * 0.4), 0), 
                           (eye_x - 4 * s, eye_y - 2 * s, 8 * s, 5 * s))
    
    # 熔岩滴落效果
    for i in range(5):
        drip_y = (cy + 20 * s + (frame * 1.5 + i * 30) % 40 * s) 
        drip_x = cx - 15 * s + i * 8 * s + math.sin(frame * 0.1 + i) * 3 * s
        drip_alpha = max(0, 255 - int((drip_y - cy - 20 * s) * 6))
        if drip_alpha > 0 and drip_y < cy + 45 * s:
            surf = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*magma_orange, drip_alpha), (5, 5), int(3 * s))
            surface.blit(surf, (drip_x - 5, drip_y - 5))
    
    # 头顶熔岩喷发
    for i in range(6):
        erupt_angle = -60 + i * 24 + math.sin(frame * 0.1) * 10
        erupt_len = 12 * s + random.uniform(-3, 3) * s
        ex = cx + math.cos(math.radians(erupt_angle)) * erupt_len
        ey = cy - 28 * s + math.sin(math.radians(erupt_angle)) * erupt_len
        pygame.draw.line(surface, magma_orange, (cx, cy - 28 * s), (int(ex), int(ey)), 2)


def _draw_phoenix_rebirth(surface, cx, cy, s, frame, pulse):
    """凤凰涅槃 - 浴火重生的神鸟形态"""
    flame_red = (255, 80, 30)
    flame_orange = (255, 160, 50)
    flame_yellow = (255, 240, 100)
    ash_gray = (60, 55, 65)
    
    # 灰烬羽毛（底层）
    for side in [-1, 1]:
        for i in range(6):
            feather_x = cx + side * (8 + i * 7) * s
            feather_y = cy + 5 * s - i * 2 * s
            feather_len = 15 * s - i * 1.5 * s
            feather_angle = side * (20 - i * 5) + math.sin(frame * 0.05 + i) * 5
            fx = feather_x + math.cos(math.radians(90 + feather_angle)) * feather_len
            fy = feather_y + math.sin(math.radians(90 + feather_angle)) * feather_len
            # 灰烬到火焰的渐变
            for j in range(5):
                t_val = j / 5
                px = feather_x + (fx - feather_x) * t_val
                py = feather_y + (fy - feather_y) * t_val
                if t_val < 0.4:
                    color = ash_gray
                elif t_val < 0.7:
                    color = flame_red
                else:
                    color = flame_orange
                pygame.draw.circle(surface, color, (int(px), int(py)), int(3 * s - j * 0.4))
    
    # 凤凰身体轮廓
    body_points = [
        (cx, cy - 25 * s),  # 头
        (cx - 10 * s, cy - 10 * s),
        (cx - 8 * s, cy + 15 * s),
        (cx, cy + 20 * s),
        (cx + 8 * s, cy + 15 * s),
        (cx + 10 * s, cy - 10 * s),
    ]
    pygame.draw.polygon(surface, flame_orange, body_points)
    
    # 燃烧头冠
    for i in range(5):
        crown_x = cx - 8 * s + i * 4 * s
        crown_height = 12 * s + math.sin(frame * 0.2 + i) * 5 * s
        flame_points = [
            (crown_x, cy - 25 * s),
            (crown_x - 3 * s, cy - 25 * s - crown_height * 0.5),
            (crown_x, cy - 25 * s - crown_height),
            (crown_x + 3 * s, cy - 25 * s - crown_height * 0.5),
        ]
        pygame.draw.polygon(surface, flame_yellow, flame_points)
    
    # 重生光环
    rebirth_phase = (frame % 120) / 120
    if rebirth_phase < 0.5:
        ring_r = rebirth_phase * 80 * s
        ring_alpha = int(200 * (0.5 - rebirth_phase) * 2)
        surf = pygame.Surface((int(ring_r * 2 + 10), int(ring_r * 2 + 10)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*flame_yellow, ring_alpha), (int(ring_r + 5), int(ring_r + 5)), int(ring_r), 2)
        surface.blit(surf, (cx - ring_r - 5, cy - ring_r - 5))
    
    # 火焰眼睛
    for side in [-1, 1]:
        eye_x = cx + side * 4 * s
        eye_y = cy - 18 * s
        pygame.draw.circle(surface, flame_yellow, (int(eye_x), int(eye_y)), int(3 * s))
        pygame.draw.circle(surface, (255, 255, 255), (int(eye_x), int(eye_y)), int(1.5 * s))
    
    # 尾羽火焰
    for i in range(7):
        tail_x = cx - 12 * s + i * 4 * s
        tail_len = 20 * s + math.sin(frame * 0.15 + i) * 8 * s
        tail_points = [
            (tail_x, cy + 20 * s),
            (tail_x - 2 * s, cy + 20 * s + tail_len * 0.6),
            (tail_x, cy + 20 * s + tail_len),
            (tail_x + 2 * s, cy + 20 * s + tail_len * 0.6),
        ]
        tail_color = flame_yellow if i % 2 == 0 else flame_orange
        pygame.draw.polygon(surface, tail_color, tail_points)


def _draw_plasma_core(surface, cx, cy, s, frame, pulse):
    """等离子核心 - 托卡马克聚变反应堆形态"""
    plasma_blue = (100, 180, 255)
    plasma_white = (220, 240, 255)
    metal_gray = (120, 125, 135)
    energy_cyan = (80, 255, 255)
    
    # 外层约束环（托卡马克环）
    for i in range(3):
        ring_angle = frame * 2 + i * 120
        ring_r = 32 * s - i * 5 * s
        ring_rect = (cx - ring_r, cy - ring_r * 0.6, ring_r * 2, ring_r * 1.2)
        ring_surf = pygame.Surface((int(ring_r * 2 + 10), int(ring_r * 1.2 + 10)), pygame.SRCALPHA)
        pygame.draw.ellipse(ring_surf, (*metal_gray, 200), (5, 5, int(ring_r * 2), int(ring_r * 1.2)), 4)
        rotated = pygame.transform.rotate(ring_surf, ring_angle)
        surface.blit(rotated, (cx - rotated.get_width() // 2, cy - rotated.get_height() // 2))
    
    # 磁场线可视化
    for i in range(12):
        field_angle = i * 30 + frame * 1.5
        field_r = 22 * s
        fx = cx + math.cos(math.radians(field_angle)) * field_r
        fy = cy + math.sin(math.radians(field_angle)) * field_r * 0.5
        pygame.draw.circle(surface, plasma_blue, (int(fx), int(fy)), int(2 * s))
        # 场线弧
        if i % 3 == 0:
            arc_surf = pygame.Surface((int(20 * s), int(20 * s)), pygame.SRCALPHA)
            pygame.draw.arc(arc_surf, (*energy_cyan, 150), (0, 0, int(20 * s), int(20 * s)), 
                          math.radians(field_angle), math.radians(field_angle + 60), 2)
            surface.blit(arc_surf, (fx - 10 * s, fy - 10 * s))
    
    # 等离子体核心
    core_r = 15 * s + pulse
    for layer in range(4):
        layer_r = core_r - layer * 3 * s
        alpha = 255 - layer * 40
        colors = [plasma_white, plasma_blue, energy_cyan, (255, 255, 255)]
        surf = pygame.Surface((int(layer_r * 2 + 4), int(layer_r * 2 + 4)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*colors[layer], alpha), (int(layer_r + 2), int(layer_r + 2)), int(layer_r))
        surface.blit(surf, (cx - layer_r - 2, cy - layer_r - 2))
    
    # 能量注入点
    for i in range(4):
        inject_angle = i * 90 + 45
        inject_x = cx + math.cos(math.radians(inject_angle)) * 35 * s
        inject_y = cy + math.sin(math.radians(inject_angle)) * 35 * s
        # 注入束
        beam_progress = (frame * 3 + i * 20) % 40
        beam_x = cx + (inject_x - cx) * (beam_progress / 40)
        beam_y = cy + (inject_y - cy) * (beam_progress / 40)
        pygame.draw.line(surface, energy_cyan, (int(inject_x), int(inject_y)), (int(beam_x), int(beam_y)), 2)
        pygame.draw.circle(surface, plasma_white, (int(inject_x), int(inject_y)), int(3 * s))


def _draw_infernal_emperor(surface, cx, cy, s, frame, pulse):
    """炎帝天威 - 东方火神的龙焰战甲形态"""
    imperial_red = (200, 50, 50)
    dragon_gold = (255, 200, 80)
    dark_red = (120, 30, 30)
    
    # 龙鳞甲胄
    for row in range(5):
        for col in range(4):
            scale_x = cx - 10 * s + col * 7 * s
            scale_y = cy - 10 * s + row * 8 * s
            scale_offset = (row % 2) * 3.5 * s
            scale_points = [
                (scale_x + scale_offset, scale_y),
                (scale_x + scale_offset - 3 * s, scale_y + 6 * s),
                (scale_x + scale_offset + 3 * s, scale_y + 6 * s),
            ]
            pygame.draw.polygon(surface, imperial_red, scale_points)
            pygame.draw.polygon(surface, dragon_gold, scale_points, 1)
    
    # 龙首头盔
    helmet_points = [
        (cx, cy - 35 * s),  # 角尖
        (cx - 8 * s, cy - 25 * s),  # 左角根
        (cx - 12 * s, cy - 18 * s),  # 左颊
        (cx, cy - 15 * s),  # 下巴
        (cx + 12 * s, cy - 18 * s),
        (cx + 8 * s, cy - 25 * s),
    ]
    pygame.draw.polygon(surface, dark_red, helmet_points)
    pygame.draw.polygon(surface, dragon_gold, helmet_points, 2)
    # 龙眼
    for side in [-1, 1]:
        pygame.draw.ellipse(surface, dragon_gold, (cx + side * 4 * s - 3 * s, cy - 23 * s, 6 * s, 4 * s))
        pygame.draw.circle(surface, (255, 50, 0), (int(cx + side * 4 * s), int(cy - 21 * s)), int(1.5 * s))
    
    # 龙须火焰
    for i in range(4):
        whisker_side = 1 if i < 2 else -1
        whisker_num = i % 2
        whisker_base_x = cx + whisker_side * 10 * s
        whisker_base_y = cy - 18 * s + whisker_num * 5 * s
        whisker_len = 15 * s + math.sin(frame * 0.2 + i) * 5 * s
        whisker_angle = whisker_side * (30 + whisker_num * 15) + math.sin(frame * 0.1) * 10
        wx = whisker_base_x + math.cos(math.radians(whisker_angle)) * whisker_len
        wy = whisker_base_y + math.sin(math.radians(whisker_angle)) * whisker_len
        for t in range(5):
            t_val = t / 5
            px = whisker_base_x + (wx - whisker_base_x) * t_val
            py = whisker_base_y + (wy - whisker_base_y) * t_val
            pygame.draw.circle(surface, dragon_gold, (int(px), int(py)), int(2 * s - t * 0.3))
    
    # 火焰斗篷
    for i in range(8):
        cape_x = cx - 14 * s + i * 4 * s
        cape_wave = math.sin(frame * 0.08 + i * 0.5) * 5 * s
        cape_points = [
            (cape_x, cy + 15 * s),
            (cape_x - 3 * s + cape_wave, cy + 30 * s),
            (cape_x + cape_wave, cy + 38 * s + abs(cape_wave)),
            (cape_x + 3 * s + cape_wave, cy + 30 * s),
        ]
        pygame.draw.polygon(surface, (255, 100 + i * 15, 50), cape_points)
    
    # 帝王纹章
    emblem_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
    pygame.draw.circle(emblem_surf, dragon_gold, (12, 12), 10)
    pygame.draw.circle(emblem_surf, imperial_red, (12, 12), 7)
    # 龙纹简化
    pygame.draw.arc(emblem_surf, dragon_gold, (6, 6, 12, 12), 0, math.pi, 2)
    surface.blit(emblem_surf, (cx - 12, cy - 5))


def _draw_binary_star(surface, cx, cy, s, frame, pulse):
    """双星系统 - 相互缠绕的恒星双子"""
    star_blue = (100, 150, 255)
    star_red = (255, 120, 80)
    
    # 公转轨道计算
    orbit_angle = frame * 1.5
    orbit_r = 18 * s
    star1_x = cx + math.cos(math.radians(orbit_angle)) * orbit_r
    star1_y = cy + math.sin(math.radians(orbit_angle)) * orbit_r * 0.4
    star2_x = cx - math.cos(math.radians(orbit_angle)) * orbit_r
    star2_y = cy - math.sin(math.radians(orbit_angle)) * orbit_r * 0.4
    
    # 引力桥 - 物质交换
    bridge_points = []
    for i in range(10):
        t = i / 9
        bx = star1_x + (star2_x - star1_x) * t
        by = star1_y + (star2_y - star1_y) * t - math.sin(t * math.pi) * 8 * s
        bridge_points.append((int(bx), int(by)))
    if len(bridge_points) > 1:
        pygame.draw.lines(surface, (255, 200, 150, 180), False, bridge_points, 3)
    
    # 蓝星（主星）
    for layer in range(4):
        r = int((12 - layer * 2) * s + pulse / 3)
        alpha = 255 - layer * 50
        surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        color = (100 + layer * 30, 150 + layer * 20, 255, alpha)
        pygame.draw.circle(surf, color, (r + 2, r + 2), r)
        surface.blit(surf, (star1_x - r - 2, star1_y - r - 2))
    
    # 红星（伴星）
    for layer in range(4):
        r = int((10 - layer * 1.5) * s + pulse / 3)
        alpha = 255 - layer * 50
        surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        color = (255, 120 - layer * 20, 80 - layer * 15, alpha)
        pygame.draw.circle(surf, color, (r + 2, r + 2), r)
        surface.blit(surf, (star2_x - r - 2, star2_y - r - 2))
    
    # 轨道轨迹
    orbit_surf = pygame.Surface((int(orbit_r * 2 + 20), int(orbit_r * 0.8 + 20)), pygame.SRCALPHA)
    pygame.draw.ellipse(orbit_surf, (150, 150, 200, 80), (10, 10, int(orbit_r * 2), int(orbit_r * 0.8)), 1)
    surface.blit(orbit_surf, (cx - orbit_r - 10, cy - orbit_r * 0.4 - 10))
    
    # 恒星风粒子
    for i in range(12):
        wind_angle = i * 30 + frame * 2
        wind_r = 30 * s + math.sin(frame * 0.1 + i) * 5 * s
        wx = cx + math.cos(math.radians(wind_angle)) * wind_r
        wy = cy + math.sin(math.radians(wind_angle)) * wind_r * 0.5
        color = star_blue if i % 2 == 0 else star_red
        pygame.draw.circle(surface, color, (int(wx), int(wy)), 2)


def _draw_solar_eclipse(surface, cx, cy, s, frame, pulse):
    """日蚀冕流 - 日全食时的太阳冕环"""
    corona_red = (255, 100, 80)
    corona_orange = (255, 180, 100)
    moon_dark = (15, 12, 20)
    
    # 冕环放射
    for i in range(24):
        corona_angle = i * 15 + frame * 0.3
        rad = math.radians(corona_angle)
        inner_r = 22 * s
        outer_r = 40 * s + math.sin(frame * 0.1 + i * 0.5) * 10 * s
        
        # 冕流曲线
        corona_points = []
        for t in range(8):
            t_val = t / 7
            dist = inner_r + (outer_r - inner_r) * t_val
            wave = math.sin(t_val * math.pi * 2 + frame * 0.05) * 5 * s * t_val
            px = cx + math.cos(rad + wave * 0.02) * dist
            py = cy + math.sin(rad + wave * 0.02) * dist
            corona_points.append((int(px), int(py)))
        
        if len(corona_points) > 1:
            color = corona_red if i % 2 == 0 else corona_orange
            pygame.draw.lines(surface, color, False, corona_points, 2)
    
    # 太阳本体（被遮挡部分的边缘光）
    edge_glow = pygame.Surface((int(50 * s), int(50 * s)), pygame.SRCALPHA)
    for ring in range(5):
        r = int(20 * s + ring * 2 * s)
        alpha = 150 - ring * 30
        pygame.draw.circle(edge_glow, (*corona_orange, alpha), (int(25 * s), int(25 * s)), r, 2)
    surface.blit(edge_glow, (cx - 25 * s, cy - 25 * s))
    
    # 月球遮挡（中央黑暗）
    pygame.draw.circle(surface, moon_dark, (int(cx), int(cy)), int(18 * s))
    # 月球表面细节
    for i in range(5):
        crater_angle = i * 72 + 30
        crater_dist = random.uniform(5, 15) * s
        crater_x = cx + math.cos(math.radians(crater_angle)) * crater_dist * 0.7
        crater_y = cy + math.sin(math.radians(crater_angle)) * crater_dist * 0.7
        pygame.draw.circle(surface, (25, 22, 30), (int(crater_x), int(crater_y)), int(3 * s))
    
    # 钻石环效果（周期性闪光）
    diamond_phase = (frame % 120) / 120
    if diamond_phase < 0.15:
        diamond_brightness = int(255 * (diamond_phase / 0.15))
        diamond_angle = 45  # 固定位置
        diamond_x = cx + math.cos(math.radians(diamond_angle)) * 20 * s
        diamond_y = cy + math.sin(math.radians(diamond_angle)) * 20 * s
        for burst in range(6):
            burst_angle = burst * 60
            burst_len = 15 * s * (diamond_phase / 0.15)
            bx = diamond_x + math.cos(math.radians(burst_angle)) * burst_len
            by = diamond_y + math.sin(math.radians(burst_angle)) * burst_len
            pygame.draw.line(surface, (255, 255, diamond_brightness), (int(diamond_x), int(diamond_y)), (int(bx), int(by)), 2)


def _draw_forge_god(surface, cx, cy, s, frame, pulse):
    """锻造之神 - 赫菲斯托斯的神火熔炉形态"""
    forge_orange = (255, 140, 50)
    metal_dark = (60, 55, 70)
    metal_hot = (255, 200, 150)
    ember = (255, 100, 30)
    
    # 熔炉主体
    furnace_points = [
        (cx - 20 * s, cy - 15 * s),
        (cx - 25 * s, cy + 20 * s),
        (cx + 25 * s, cy + 20 * s),
        (cx + 20 * s, cy - 15 * s),
    ]
    pygame.draw.polygon(surface, metal_dark, furnace_points)
    pygame.draw.polygon(surface, (80, 75, 90), furnace_points, 2)
    
    # 炉膛开口
    opening_rect = (cx - 12 * s, cy - 5 * s, 24 * s, 18 * s)
    pygame.draw.rect(surface, (20, 15, 25), opening_rect)
    # 炉火
    fire_intensity = int(150 + math.sin(frame * 0.2) * 100)
    for i in range(6):
        fire_x = cx - 8 * s + i * 3.5 * s
        fire_h = 10 * s + math.sin(frame * 0.3 + i) * 5 * s
        fire_points = [
            (fire_x, cy + 10 * s),
            (fire_x - 2 * s, cy + 10 * s - fire_h * 0.6),
            (fire_x, cy + 10 * s - fire_h),
            (fire_x + 2 * s, cy + 10 * s - fire_h * 0.6),
        ]
        pygame.draw.polygon(surface, (fire_intensity, int(fire_intensity * 0.5), 50), fire_points)
    
    # 铁砧
    anvil_points = [
        (cx - 30 * s, cy + 22 * s),
        (cx - 35 * s, cy + 28 * s),
        (cx - 25 * s, cy + 32 * s),
        (cx + 25 * s, cy + 32 * s),
        (cx + 35 * s, cy + 28 * s),
        (cx + 30 * s, cy + 22 * s),
    ]
    pygame.draw.polygon(surface, (50, 50, 55), anvil_points)
    pygame.draw.polygon(surface, metal_dark, anvil_points, 2)
    
    # 锻造的热铁
    hot_metal = pygame.Surface((int(20 * s), int(8 * s)), pygame.SRCALPHA)
    pygame.draw.rect(hot_metal, metal_hot, (0, 0, int(20 * s), int(8 * s)))
    # 热量辉光
    glow_alpha = int(100 + math.sin(frame * 0.15) * 50)
    glow_surf = pygame.Surface((int(30 * s), int(18 * s)), pygame.SRCALPHA)
    pygame.draw.ellipse(glow_surf, (*forge_orange, glow_alpha), (0, 0, int(30 * s), int(18 * s)))
    surface.blit(glow_surf, (cx - 15 * s, cy + 18 * s))
    surface.blit(hot_metal, (cx - 10 * s, cy + 23 * s))
    
    # 锤击火星
    if frame % 30 < 5:
        random.seed(frame // 30)
        for i in range(8):
            spark_angle = random.uniform(0, 360)
            spark_dist = random.uniform(5, 25) * s
            spark_x = cx + math.cos(math.radians(spark_angle)) * spark_dist
            spark_y = cy + 25 * s + math.sin(math.radians(spark_angle)) * spark_dist * 0.3 - 10 * s
            pygame.draw.circle(surface, ember, (int(spark_x), int(spark_y)), int(random.uniform(1, 3) * s))
    
    # 烟囱
    chimney_points = [(cx - 5 * s, cy - 15 * s), (cx - 8 * s, cy - 35 * s),
                     (cx + 8 * s, cy - 35 * s), (cx + 5 * s, cy - 15 * s)]
    pygame.draw.polygon(surface, metal_dark, chimney_points)
    # 烟雾
    for i in range(4):
        smoke_y = cy - 35 * s - (frame * 0.8 + i * 15) % 40 * s
        smoke_x = cx + math.sin(frame * 0.05 + i) * 5 * s
        smoke_alpha = max(0, 120 - int((cy - 35 * s - smoke_y) * 3))
        if smoke_alpha > 0:
            surf = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(surf, (80, 80, 90, smoke_alpha), (8, 8), int(5 * s))
            surface.blit(surf, (smoke_x - 8, smoke_y - 8))


def _draw_cosmic_furnace(surface, cx, cy, s, frame, pulse):
    """宇宙熔炉 - 创世之焰的原初形态"""
    primordial_gold = (255, 220, 150)
    void_black = (10, 5, 15)
    creation_white = (255, 255, 240)
    nebula_purple = (150, 100, 200)
    
    # 虚空背景
    void_surf = pygame.Surface((int(80 * s), int(80 * s)), pygame.SRCALPHA)
    pygame.draw.circle(void_surf, void_black, (int(40 * s), int(40 * s)), int(38 * s))
    surface.blit(void_surf, (cx - 40 * s, cy - 40 * s))
    
    # 原初星云旋转
    for i in range(20):
        nebula_angle = frame * 0.5 + i * 18
        nebula_dist = 20 * s + i * 1.2 * s
        nebula_x = cx + math.cos(math.radians(nebula_angle)) * nebula_dist
        nebula_y = cy + math.sin(math.radians(nebula_angle)) * nebula_dist
        nebula_size = 3 * s + math.sin(frame * 0.1 + i) * 1.5 * s
        colors = [nebula_purple, primordial_gold, (255, 150, 100)]
        surf = pygame.Surface((int(nebula_size * 2 + 4), int(nebula_size * 2 + 4)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*colors[i % 3], 150), (int(nebula_size + 2), int(nebula_size + 2)), int(nebula_size))
        surface.blit(surf, (nebula_x - nebula_size - 2, nebula_y - nebula_size - 2))
    
    # 创世火球
    for layer in range(5):
        r = int((15 - layer * 2) * s + pulse)
        alpha = 255 - layer * 40
        if layer == 0:
            color = (*creation_white, alpha)
        elif layer < 3:
            color = (*primordial_gold, alpha)
        else:
            color = (255, 150, 100, alpha)
        surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (r + 2, r + 2), r)
        surface.blit(surf, (cx - r - 2, cy - r - 2))
    
    # 新生恒星
    random.seed(42)
    for i in range(6):
        star_angle = frame * 0.3 + i * 60
        star_dist = 28 * s
        star_x = cx + math.cos(math.radians(star_angle)) * star_dist
        star_y = cy + math.sin(math.radians(star_angle)) * star_dist
        twinkle = int(abs(math.sin(frame * 0.1 + i)) * 100 + 155)
        pygame.draw.circle(surface, (twinkle, twinkle, int(twinkle * 0.9)), (int(star_x), int(star_y)), int(2 * s))
        # 十字光芒
        for j in range(4):
            ray_angle = j * 90
            ray_len = 4 * s
            rx = star_x + math.cos(math.radians(ray_angle)) * ray_len
            ry = star_y + math.sin(math.radians(ray_angle)) * ray_len
            pygame.draw.line(surface, (twinkle, twinkle, int(twinkle * 0.9)), (int(star_x), int(star_y)), (int(rx), int(ry)), 1)
    
    # 能量射流
    for beam in range(4):
        beam_angle = beam * 90 + 45
        beam_end_x = cx + math.cos(math.radians(beam_angle)) * 45 * s
        beam_end_y = cy + math.sin(math.radians(beam_angle)) * 45 * s
        beam_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(beam_surf, (*primordial_gold, 100), (int(cx), int(cy)), (int(beam_end_x), int(beam_end_y)), 3)
        surface.blit(beam_surf, (0, 0))


def _draw_neutron_star(surface, cx, cy, s, frame, pulse):
    """中子星核 - 极致压缩的恒星残骸"""
    neutron_blue = (150, 180, 255)
    neutron_white = (240, 245, 255)
    pulse_cyan = (100, 255, 255)
    magnetic_purple = (180, 100, 255)
    
    # 磁场极光
    for pole in [-1, 1]:
        for i in range(8):
            aurora_angle = frame * 2 + i * 12
            aurora_height = (25 + i * 3) * s
            aurora_x = cx + math.cos(math.radians(aurora_angle)) * 8 * s
            aurora_y = cy + pole * aurora_height
            aurora_alpha = 150 - i * 15
            surf = pygame.Surface((int(10 * s), int(aurora_height)), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (*magnetic_purple, aurora_alpha), (0, 0, int(10 * s), int(aurora_height)))
            surface.blit(surf, (aurora_x - 5 * s, min(aurora_y, cy) - 5 if pole == -1 else cy))
    
    # 脉冲射线束
    pulsar_phase = frame % 60
    if pulsar_phase < 30:
        beam_angle = frame * 6
        for side in [-1, 1]:
            beam_dir = beam_angle + side * 90
            beam_len = 50 * s
            bx = cx + math.cos(math.radians(beam_dir)) * beam_len
            by = cy + math.sin(math.radians(beam_dir)) * beam_len
            # 射线锥
            cone_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            cone_points = [
                (cx, cy),
                (cx + math.cos(math.radians(beam_dir - 10)) * beam_len, 
                 cy + math.sin(math.radians(beam_dir - 10)) * beam_len),
                (cx + math.cos(math.radians(beam_dir + 10)) * beam_len,
                 cy + math.sin(math.radians(beam_dir + 10)) * beam_len),
            ]
            pygame.draw.polygon(cone_surf, (*pulse_cyan, 80), cone_points)
            surface.blit(cone_surf, (0, 0))
    
    # 中子星核心 - 极致密度
    for layer in range(4):
        r = int((12 - layer * 2) * s)
        alpha = 255 - layer * 30
        if layer == 0:
            color = (*neutron_white, alpha)
        else:
            color = (*neutron_blue, alpha)
        surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (r + 2, r + 2), r)
        surface.blit(surf, (cx - r - 2, cy - r - 2))
    
    # 表面磁极热点
    for i in range(2):
        spot_y = cy + (i * 2 - 1) * 8 * s
        spot_pulse = int(200 + math.sin(frame * 0.3 + i * math.pi) * 55)
        pygame.draw.circle(surface, (spot_pulse, spot_pulse, 255), (int(cx), int(spot_y)), int(3 * s))
    
    # X射线环
    xray_r = 20 * s + math.sin(frame * 0.15) * 3 * s
    xray_surf = pygame.Surface((int(xray_r * 2 + 10), int(xray_r * 0.5 + 10)), pygame.SRCALPHA)
    pygame.draw.ellipse(xray_surf, (*pulse_cyan, 100), (5, 5, int(xray_r * 2), int(xray_r * 0.5)), 2)
    surface.blit(xray_surf, (cx - xray_r - 5, cy - xray_r * 0.25 - 5))
