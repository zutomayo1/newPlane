# -*- coding: utf-8 -*-
"""
晶簇射流·晶瀑 (Crystalfall) - 专属涂装渲染模块
水晶紫岩青的晶簇战机，以晶体构建护盾与屏障

涂装列表 (12种完全不同形态):
1. crystalfall_default - 晶瀑原型（水晶紫+岩青基底）
2. crystalfall_amethyst - 紫水晶簇（深紫矿脉）
3. crystalfall_diamond - 钻石切割（璀璨折射）
4. crystalfall_emerald - 翡翠晶洞（东方绿玉）
5. crystalfall_ruby - 红宝石核（炽热血晶）
6. crystalfall_sapphire - 蓝宝石海（深海结晶）
7. crystalfall_obsidian - 黑曜石刃（火山玻璃）
8. crystalfall_opal - 蛋白石幻（彩虹折射）
9. crystalfall_quartz - 白水晶簇（纯净透明）
10. crystalfall_geode - 晶洞奇观（紫晶洞穴）
11. crystalfall_frost - 霜晶凝结（冰封晶体）
12. crystalfall_void - 虚空晶核（暗物质结晶）
"""
import pygame
import math
import random

# Crystalfall涂装样式列表
CRYSTALFALL_STYLES = [
    "crystalfall_default",
    "crystalfall_amethyst",
    "crystalfall_diamond",
    "crystalfall_emerald",
    "crystalfall_ruby",
    "crystalfall_sapphire",
    "crystalfall_obsidian",
    "crystalfall_opal",
    "crystalfall_quartz",
    "crystalfall_geode",
    "crystalfall_frost",
    "crystalfall_void"
]


def is_crystalfall_style(model_style):
    """检查是否为 Crystalfall 涂装样式"""
    return model_style in CRYSTALFALL_STYLES


def render_crystalfall_skin(surface, c, model_style, t, pid, static):
    """渲染 Crystalfall 专属涂装"""
    if model_style not in CRYSTALFALL_STYLES:
        return None
    
    skin_id = model_style.replace("crystalfall_", "")
    frame = 0 if static else int(t * 60) % 360
    draw_crystalfall(surface, c, 60, 60, scale=1.8, skin_id=skin_id, frame=frame)
    return surface


def _render_crystalfall_base(surface, t, pulse):
    """基础机体渲染（用于base.py调用）"""
    frame = int(t * 60) % 360
    draw_crystalfall(surface, (150, 200, 220), 60, 60, scale=1.8, skin_id="default", frame=frame)


def draw_crystalfall(surface, color, x, y, scale=1.0, skin_id="default", frame=0):
    """绘制晶瀑 - 12种独特形态"""
    cx, cy = x, y
    s = scale
    pulse = math.sin(frame * 0.1) * 3
    
    if skin_id == "default":
        _draw_default(surface, cx, cy, s, frame, pulse)
    elif skin_id == "amethyst":
        _draw_amethyst(surface, cx, cy, s, frame, pulse)
    elif skin_id == "diamond":
        _draw_diamond(surface, cx, cy, s, frame, pulse)
    elif skin_id == "emerald":
        _draw_emerald(surface, cx, cy, s, frame, pulse)
    elif skin_id == "ruby":
        _draw_ruby(surface, cx, cy, s, frame, pulse)
    elif skin_id == "sapphire":
        _draw_sapphire(surface, cx, cy, s, frame, pulse)
    elif skin_id == "obsidian":
        _draw_obsidian(surface, cx, cy, s, frame, pulse)
    elif skin_id == "opal":
        _draw_opal(surface, cx, cy, s, frame, pulse)
    elif skin_id == "quartz":
        _draw_quartz(surface, cx, cy, s, frame, pulse)
    elif skin_id == "geode":
        _draw_geode(surface, cx, cy, s, frame, pulse)
    elif skin_id == "frost":
        _draw_frost(surface, cx, cy, s, frame, pulse)
    elif skin_id == "void":
        _draw_void(surface, cx, cy, s, frame, pulse)
    else:
        _draw_default(surface, cx, cy, s, frame, pulse)


def _draw_crystal_spike(surface, cx, cy, s, angle, length, color1, color2, width=8):
    """绘制单个晶体尖刺"""
    rad = math.radians(angle)
    tip_x = cx + math.cos(rad) * length * s
    tip_y = cy + math.sin(rad) * length * s
    
    # 晶体形状（菱形）
    side_rad1 = math.radians(angle + 90)
    side_rad2 = math.radians(angle - 90)
    
    points = [
        (tip_x, tip_y),  # 尖端
        (cx + math.cos(side_rad1) * width * 0.5 * s, cy + math.sin(side_rad1) * width * 0.5 * s),
        (cx, cy),  # 基部
        (cx + math.cos(side_rad2) * width * 0.5 * s, cy + math.sin(side_rad2) * width * 0.5 * s),
    ]
    pygame.draw.polygon(surface, color1, points)
    pygame.draw.polygon(surface, color2, points, 1)
    
    # 高光面
    highlight_points = [
        (tip_x, tip_y),
        ((tip_x + cx) / 2 + math.cos(side_rad1) * 2 * s, (tip_y + cy) / 2 + math.sin(side_rad1) * 2 * s),
        (cx, cy),
    ]
    highlight_color = tuple(min(255, c + 40) for c in color1[:3])
    pygame.draw.polygon(surface, highlight_color, highlight_points)


def _draw_default(surface, cx, cy, s, frame, pulse):
    """晶瀑原型 - 水晶紫+岩青基底"""
    crystal_purple = (180, 120, 220)
    rock_cyan = (100, 150, 180)
    glow_purple = (200, 150, 255)
    core_white = (240, 230, 255)
    
    # 晶体光晕
    for layer in range(4):
        r = int((30 - layer * 5) * s + pulse)
        alpha = 60 - layer * 12
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*crystal_purple[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 岩石基底
    base_points = []
    for i in range(8):
        angle = i * 45
        rad = math.radians(angle)
        r = 16 * s + random.Random(i).random() * 3 * s
        base_points.append((cx + math.cos(rad) * r, cy + math.sin(rad) * r))
    pygame.draw.polygon(surface, rock_cyan, base_points)
    
    # 晶簇尖刺
    for i in range(8):
        angle = i * 45 + 22.5
        length = 22 + math.sin(frame * 0.1 + i) * 3
        _draw_crystal_spike(surface, cx, cy, s, angle, length, crystal_purple, glow_purple)
    
    # 核心晶体
    pygame.draw.circle(surface, crystal_purple, (int(cx), int(cy)), int(10 * s))
    pygame.draw.circle(surface, core_white, (int(cx), int(cy)), int(6 * s))
    
    # 闪烁高光
    sparkle_angle = frame * 2
    sparkle_r = 8 * s
    sx = cx + math.cos(math.radians(sparkle_angle)) * sparkle_r
    sy = cy + math.sin(math.radians(sparkle_angle)) * sparkle_r
    pygame.draw.circle(surface, core_white, (int(sx), int(sy)), int(2 * s))


def _draw_amethyst(surface, cx, cy, s, frame, pulse):
    """紫水晶簇 - 深紫矿脉"""
    deep_purple = (100, 40, 140)
    amethyst = (150, 80, 180)
    light_purple = (200, 150, 220)
    vein_dark = (60, 30, 80)
    
    # 矿脉基底
    pygame.draw.circle(surface, vein_dark, (int(cx), int(cy)), int(22 * s))
    
    # 矿脉纹理
    for i in range(6):
        vein_angle = i * 60 + random.Random(i).random() * 30
        rad = math.radians(vein_angle)
        v_len = 18 * s
        vx = cx + math.cos(rad) * v_len
        vy = cy + math.sin(rad) * v_len
        pygame.draw.line(surface, deep_purple, (cx, cy), (vx, vy), int(2 * s))
    
    # 紫水晶簇
    for i in range(10):
        angle = i * 36 + frame * 0.2
        length = 18 + random.Random(i + 100).random() * 10
        _draw_crystal_spike(surface, cx, cy, s, angle, length, amethyst, light_purple, width=6)
    
    # 核心
    pygame.draw.circle(surface, deep_purple, (int(cx), int(cy)), int(8 * s))
    pygame.draw.circle(surface, amethyst, (int(cx), int(cy)), int(5 * s))
    
    # 闪光
    for i in range(4):
        sparkle_angle = frame * 1.5 + i * 90
        sparkle_r = 15 * s
        sx = cx + math.cos(math.radians(sparkle_angle)) * sparkle_r
        sy = cy + math.sin(math.radians(sparkle_angle)) * sparkle_r
        pygame.draw.circle(surface, light_purple, (int(sx), int(sy)), int(2 * s))


def _draw_diamond(surface, cx, cy, s, frame, pulse):
    """钻石切割 - 璀璨折射"""
    diamond_clear = (240, 250, 255)
    diamond_blue = (200, 220, 255)
    rainbow = [(255, 200, 200), (255, 255, 200), (200, 255, 200), (200, 200, 255)]
    
    # 折射光芒
    for i in range(8):
        ray_angle = frame * 2 + i * 45
        rad = math.radians(ray_angle)
        ray_len = 35 * s
        color = rainbow[i % 4]
        alpha = int(80 + 40 * math.sin(frame * 0.2 + i))
        ray_surf = pygame.Surface((int(ray_len), int(6 * s)), pygame.SRCALPHA)
        pygame.draw.rect(ray_surf, (*color[:3], alpha), (0, 0, int(ray_len), int(6 * s)))
        rotated = pygame.transform.rotate(ray_surf, -ray_angle)
        surface.blit(rotated, (cx - rotated.get_width() // 2, cy - rotated.get_height() // 2))
    
    # 钻石切面
    for i in range(6):
        angle = i * 60
        rad = math.radians(angle)
        facet_r = 18 * s
        fx = cx + math.cos(rad) * facet_r * 0.5
        fy = cy + math.sin(rad) * facet_r * 0.5
        
        facet_points = [
            (cx, cy),
            (fx + math.cos(rad - 0.5) * 12 * s, fy + math.sin(rad - 0.5) * 12 * s),
            (cx + math.cos(rad) * 20 * s, cy + math.sin(rad) * 20 * s),
            (fx + math.cos(rad + 0.5) * 12 * s, fy + math.sin(rad + 0.5) * 12 * s),
        ]
        color_var = 220 + int(20 * math.sin(i + frame * 0.1))
        pygame.draw.polygon(surface, (color_var, color_var + 5, 255), facet_points)
        pygame.draw.polygon(surface, diamond_blue, facet_points, 1)
    
    # 核心
    pygame.draw.circle(surface, diamond_clear, (int(cx), int(cy)), int(8 * s))
    
    # 璀璨高光
    pygame.draw.circle(surface, (255, 255, 255), (int(cx - 2 * s), int(cy - 2 * s)), int(4 * s))


def _draw_emerald(surface, cx, cy, s, frame, pulse):
    """翡翠晶洞 - 东方绿玉"""
    jade_green = (80, 180, 100)
    emerald = (50, 150, 80)
    pale_jade = (150, 220, 170)
    gold_trim = (220, 180, 80)
    
    # 玉石光晕
    for layer in range(3):
        r = int((28 - layer * 6) * s)
        alpha = 60 - layer * 15
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*jade_green[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 翡翠主体
    pygame.draw.circle(surface, emerald, (int(cx), int(cy)), int(18 * s))
    
    # 玉纹
    for i in range(4):
        vein_angle = i * 90 + 45
        rad = math.radians(vein_angle)
        v_start = 5 * s
        v_end = 16 * s
        pygame.draw.line(surface, pale_jade,
                        (cx + math.cos(rad) * v_start, cy + math.sin(rad) * v_start),
                        (cx + math.cos(rad) * v_end, cy + math.sin(rad) * v_end), int(2 * s))
    
    # 晶体尖端
    for i in range(6):
        angle = i * 60 + frame * 0.3
        length = 25 + math.sin(frame * 0.1 + i) * 3
        _draw_crystal_spike(surface, cx, cy, s, angle, length, jade_green, pale_jade, width=7)
    
    # 金边
    pygame.draw.circle(surface, gold_trim, (int(cx), int(cy)), int(10 * s), int(2 * s))
    
    # 核心
    pygame.draw.circle(surface, pale_jade, (int(cx), int(cy)), int(6 * s))


def _draw_ruby(surface, cx, cy, s, frame, pulse):
    """红宝石核 - 炽热血晶"""
    ruby_red = (200, 30, 60)
    blood_red = (150, 20, 40)
    fire_orange = (255, 100, 50)
    pink_glow = (255, 150, 180)
    
    # 炽热光晕
    for layer in range(4):
        r = int((32 - layer * 5) * s + pulse)
        alpha = 80 - layer * 15
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*ruby_red[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 红宝石主体
    pygame.draw.circle(surface, blood_red, (int(cx), int(cy)), int(16 * s))
    
    # 内部火焰纹
    for i in range(4):
        flame_angle = frame * 0.5 + i * 90
        rad = math.radians(flame_angle)
        flame_r = 10 * s
        fx = cx + math.cos(rad) * flame_r
        fy = cy + math.sin(rad) * flame_r
        pygame.draw.circle(surface, fire_orange, (int(fx), int(fy)), int(4 * s))
    
    # 红宝石尖刺
    for i in range(8):
        angle = i * 45 + frame * 0.2
        length = 22 + math.sin(frame * 0.15 + i) * 4
        _draw_crystal_spike(surface, cx, cy, s, angle, length, ruby_red, pink_glow)
    
    # 核心
    pygame.draw.circle(surface, ruby_red, (int(cx), int(cy)), int(8 * s))
    pygame.draw.circle(surface, pink_glow, (int(cx), int(cy)), int(4 * s))


def _draw_sapphire(surface, cx, cy, s, frame, pulse):
    """蓝宝石海 - 深海结晶"""
    sapphire_blue = (30, 80, 180)
    deep_blue = (20, 50, 120)
    light_blue = (100, 150, 220)
    white_glow = (200, 220, 255)
    
    # 深海光晕
    for layer in range(4):
        r = int((30 - layer * 5) * s + pulse)
        alpha = 60 - layer * 12
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*sapphire_blue[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 蓝宝石主体
    pygame.draw.circle(surface, deep_blue, (int(cx), int(cy)), int(18 * s))
    
    # 水波纹
    for i in range(3):
        wave_r = ((frame + i * 30) % 60) * s * 0.3 + 8 * s
        wave_alpha = int(100 * (1 - ((frame + i * 30) % 60) / 60))
        if wave_alpha > 0:
            wave_surf = pygame.Surface((int(wave_r * 2 + 4), int(wave_r * 2 + 4)), pygame.SRCALPHA)
            pygame.draw.circle(wave_surf, (*light_blue[:3], wave_alpha), 
                             (int(wave_r + 2), int(wave_r + 2)), int(wave_r), 2)
            surface.blit(wave_surf, (cx - wave_r - 2, cy - wave_r - 2))
    
    # 蓝宝石尖刺
    for i in range(6):
        angle = i * 60 + frame * 0.25
        length = 24 + math.sin(frame * 0.1 + i) * 3
        _draw_crystal_spike(surface, cx, cy, s, angle, length, sapphire_blue, light_blue, width=8)
    
    # 核心
    pygame.draw.circle(surface, sapphire_blue, (int(cx), int(cy)), int(8 * s))
    pygame.draw.circle(surface, white_glow, (int(cx), int(cy)), int(4 * s))


def _draw_obsidian(surface, cx, cy, s, frame, pulse):
    """黑曜石刃 - 火山玻璃"""
    obsidian_black = (20, 20, 25)
    glass_gray = (60, 60, 70)
    magma_orange = (255, 100, 30)
    reflect_white = (150, 150, 160)
    
    # 熔岩裂隙光
    for i in range(4):
        crack_angle = i * 90 + 45
        rad = math.radians(crack_angle)
        crack_len = 28 * s
        # 裂隙发光
        for j in range(5):
            cx_j = cx + math.cos(rad) * j * 5 * s
            cy_j = cy + math.sin(rad) * j * 5 * s
            glow_r = (6 - j) * s
            alpha = int(150 - j * 25)
            glow_surf = pygame.Surface((int(glow_r * 2 + 4), int(glow_r * 2 + 4)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*magma_orange[:3], alpha), 
                             (int(glow_r + 2), int(glow_r + 2)), int(glow_r))
            surface.blit(glow_surf, (cx_j - glow_r - 2, cy_j - glow_r - 2))
    
    # 黑曜石主体
    obsidian_points = []
    for i in range(8):
        angle = i * 45
        rad = math.radians(angle)
        r = 18 * s if i % 2 == 0 else 22 * s
        obsidian_points.append((cx + math.cos(rad) * r, cy + math.sin(rad) * r))
    pygame.draw.polygon(surface, obsidian_black, obsidian_points)
    pygame.draw.polygon(surface, glass_gray, obsidian_points, 2)
    
    # 锋利刃尖
    for i in range(6):
        angle = i * 60 + 30
        length = 28 + math.sin(frame * 0.1 + i) * 2
        _draw_crystal_spike(surface, cx, cy, s, angle, length, obsidian_black, glass_gray, width=5)
    
    # 反光
    pygame.draw.line(surface, reflect_white, 
                    (cx - 8 * s, cy - 8 * s), (cx + 5 * s, cy - 5 * s), int(2 * s))
    
    # 核心熔岩
    pygame.draw.circle(surface, magma_orange, (int(cx), int(cy)), int(5 * s))


def _draw_opal(surface, cx, cy, s, frame, pulse):
    """蛋白石幻 - 彩虹折射"""
    opal_white = (240, 240, 250)
    rainbow_colors = [
        (255, 150, 150),  # 红
        (255, 200, 150),  # 橙
        (255, 255, 150),  # 黄
        (150, 255, 150),  # 绿
        (150, 200, 255),  # 蓝
        (200, 150, 255),  # 紫
    ]
    
    # 彩虹光晕
    for i, color in enumerate(rainbow_colors):
        angle = frame * 1.5 + i * 60
        rad = math.radians(angle)
        r = 25 * s
        glow_x = cx + math.cos(rad) * 10 * s
        glow_y = cy + math.sin(rad) * 10 * s
        glow_surf = pygame.Surface((int(r * 2), int(r * 2)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color[:3], 60), (int(r), int(r)), int(r * 0.8))
        surface.blit(glow_surf, (glow_x - r, glow_y - r))
    
    # 蛋白石主体
    pygame.draw.circle(surface, opal_white, (int(cx), int(cy)), int(18 * s))
    
    # 流动彩斑
    for i in range(6):
        spot_angle = frame * 0.8 + i * 60
        rad = math.radians(spot_angle)
        spot_r = 12 * s
        sx = cx + math.cos(rad) * spot_r
        sy = cy + math.sin(rad) * spot_r
        color = rainbow_colors[(i + int(frame / 20)) % 6]
        pygame.draw.circle(surface, color, (int(sx), int(sy)), int(5 * s))
    
    # 晶簇
    for i in range(6):
        angle = i * 60 + frame * 0.3
        length = 20 + math.sin(frame * 0.15 + i) * 4
        color = rainbow_colors[i]
        _draw_crystal_spike(surface, cx, cy, s, angle, length, opal_white, color, width=6)
    
    # 核心
    pygame.draw.circle(surface, opal_white, (int(cx), int(cy)), int(8 * s))
    # 彩虹核
    core_color = rainbow_colors[int(frame / 10) % 6]
    pygame.draw.circle(surface, core_color, (int(cx), int(cy)), int(4 * s))


def _draw_quartz(surface, cx, cy, s, frame, pulse):
    """白水晶簇 - 纯净透明"""
    quartz_clear = (245, 250, 255)
    quartz_white = (255, 255, 255)
    quartz_gray = (200, 210, 220)
    sparkle = (255, 255, 255)
    
    # 纯净光晕
    for layer in range(3):
        r = int((28 - layer * 6) * s)
        alpha = 40 - layer * 10
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*quartz_white[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 透明晶体簇
    for i in range(12):
        angle = i * 30 + frame * 0.2
        length = 15 + random.Random(i).random() * 12
        # 半透明效果
        crystal_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        _draw_crystal_spike(crystal_surf, 30, 30, s * 0.8, angle, length, 
                           (*quartz_clear[:3],), quartz_gray, width=5)
        surface.blit(crystal_surf, (cx - 30, cy - 30))
    
    # 核心
    pygame.draw.circle(surface, quartz_gray, (int(cx), int(cy)), int(10 * s))
    pygame.draw.circle(surface, quartz_clear, (int(cx), int(cy)), int(6 * s))
    
    # 闪烁光点
    for i in range(6):
        sparkle_angle = frame * 3 + i * 60
        sparkle_r = 15 * s + math.sin(frame * 0.2 + i) * 5 * s
        sx = cx + math.cos(math.radians(sparkle_angle)) * sparkle_r
        sy = cy + math.sin(math.radians(sparkle_angle)) * sparkle_r
        pygame.draw.circle(surface, sparkle, (int(sx), int(sy)), int(2 * s))


def _draw_geode(surface, cx, cy, s, frame, pulse):
    """晶洞奇观 - 紫晶洞穴"""
    cave_brown = (100, 80, 60)
    geode_purple = (140, 80, 180)
    crystal_violet = (180, 120, 220)
    inner_glow = (200, 150, 255)
    
    # 岩石外壳
    shell_points = []
    for i in range(10):
        angle = i * 36
        rad = math.radians(angle)
        r = 24 * s + random.Random(i).random() * 4 * s
        shell_points.append((cx + math.cos(rad) * r, cy + math.sin(rad) * r))
    pygame.draw.polygon(surface, cave_brown, shell_points)
    
    # 晶洞内部（深色）
    inner_points = []
    for i in range(10):
        angle = i * 36
        rad = math.radians(angle)
        r = 16 * s + random.Random(i + 50).random() * 3 * s
        inner_points.append((cx + math.cos(rad) * r, cy + math.sin(rad) * r))
    pygame.draw.polygon(surface, (40, 30, 50), inner_points)
    
    # 内壁紫晶
    for i in range(12):
        angle = i * 30 + 15
        rad = math.radians(angle)
        base_r = 14 * s
        bx = cx + math.cos(rad) * base_r
        by = cy + math.sin(rad) * base_r
        # 向内生长
        inner_angle = angle + 180
        length = 8 + random.Random(i + 200).random() * 6
        _draw_crystal_spike(surface, bx, by, s * 0.6, inner_angle, length, 
                           geode_purple, crystal_violet, width=4)
    
    # 核心发光
    for layer in range(3):
        r = int((8 - layer * 2) * s)
        alpha = 150 - layer * 40
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*inner_glow[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))


def _draw_frost(surface, cx, cy, s, frame, pulse):
    """霜晶凝结 - 冰封晶体"""
    ice_blue = (180, 220, 255)
    frost_white = (240, 250, 255)
    deep_ice = (100, 160, 220)
    snow = (255, 255, 255)
    
    # 冰霜光晕
    for layer in range(4):
        r = int((30 - layer * 5) * s + pulse)
        alpha = 50 - layer * 10
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*ice_blue[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 冰晶主体
    pygame.draw.circle(surface, deep_ice, (int(cx), int(cy)), int(16 * s))
    pygame.draw.circle(surface, ice_blue, (int(cx), int(cy)), int(12 * s))
    
    # 六角冰晶分支
    for i in range(6):
        angle = i * 60 + frame * 0.2
        rad = math.radians(angle)
        branch_len = 25 * s
        
        # 主干
        pygame.draw.line(surface, frost_white,
                        (cx, cy),
                        (cx + math.cos(rad) * branch_len, cy + math.sin(rad) * branch_len), int(3 * s))
        
        # 分叉
        for j in range(3):
            fork_start = 8 + j * 6
            for side in [-1, 1]:
                fork_angle = angle + side * 60
                fork_rad = math.radians(fork_angle)
                fork_len = (8 - j * 2) * s
                start_x = cx + math.cos(rad) * fork_start * s
                start_y = cy + math.sin(rad) * fork_start * s
                pygame.draw.line(surface, frost_white,
                                (start_x, start_y),
                                (start_x + math.cos(fork_rad) * fork_len,
                                 start_y + math.sin(fork_rad) * fork_len), int(2 * s))
    
    # 核心
    pygame.draw.circle(surface, frost_white, (int(cx), int(cy)), int(6 * s))
    
    # 雪花粒子
    for i in range(8):
        snow_angle = frame * 1.5 + i * 45
        snow_r = 22 * s + math.sin(frame * 0.15 + i) * 6 * s
        sx = cx + math.cos(math.radians(snow_angle)) * snow_r
        sy = cy + math.sin(math.radians(snow_angle)) * snow_r
        pygame.draw.circle(surface, snow, (int(sx), int(sy)), int(2 * s))


def _draw_void(surface, cx, cy, s, frame, pulse):
    """虚空晶核 - 暗物质结晶"""
    void_purple = (40, 20, 80)
    void_black = (10, 5, 20)
    rift_cyan = (0, 200, 220)
    dark_crystal = (60, 30, 100)
    
    # 虚空漩涡
    for layer in range(5):
        r = int((35 - layer * 5) * s)
        alpha = 40 - layer * 6
        angle_offset = frame * (0.3 + layer * 0.1)
        
        for i in range(6):
            swirl_angle = angle_offset + i * 60
            rad = math.radians(swirl_angle)
            swirl_r = r * 0.8
            sx = cx + math.cos(rad) * swirl_r
            sy = cy + math.sin(rad) * swirl_r
            
            swirl_surf = pygame.Surface((int(8 * s), int(8 * s)), pygame.SRCALPHA)
            pygame.draw.circle(swirl_surf, (*void_purple[:3], alpha), (int(4 * s), int(4 * s)), int(3 * s))
            surface.blit(swirl_surf, (sx - 4 * s, sy - 4 * s))
    
    # 虚空晶体
    pygame.draw.circle(surface, void_black, (int(cx), int(cy)), int(18 * s))
    
    # 暗晶尖刺
    for i in range(8):
        angle = i * 45 + frame * 0.3
        length = 24 + math.sin(frame * 0.1 + i) * 3
        _draw_crystal_spike(surface, cx, cy, s, angle, length, dark_crystal, void_purple, width=6)
    
    # 裂隙能量
    for i in range(4):
        rift_angle = i * 90 + frame
        rad = math.radians(rift_angle)
        rift_len = 15 * s
        pygame.draw.line(surface, rift_cyan,
                        (cx, cy),
                        (cx + math.cos(rad) * rift_len, cy + math.sin(rad) * rift_len), int(2 * s))
    
    # 核心
    pygame.draw.circle(surface, void_purple, (int(cx), int(cy)), int(8 * s))
    pygame.draw.circle(surface, rift_cyan, (int(cx), int(cy)), int(4 * s))
    
    # 暗物质粒子
    for i in range(10):
        particle_angle = frame * 2 + i * 36
        particle_r = 20 * s + math.sin(frame * 0.2 + i * 0.5) * 8 * s
        px = cx + math.cos(math.radians(particle_angle)) * particle_r
        py = cy + math.sin(math.radians(particle_angle)) * particle_r
        pygame.draw.circle(surface, rift_cyan, (int(px), int(py)), int(1.5 * s))
