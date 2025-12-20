# -*- coding: utf-8 -*-
"""
分形天顶·ZENITH 涂装系统
原型：Terraria - Zenith (The Ultimate Sword)
风格：像素碎片 + RGB光效 + 剑阵回旋镖母舰
设计理念：终极武器 - 集合所有传奇剑刃的分形母舰
"""
import pygame
import math
import colorsys

# ==================== 6种涂装主题 ====================
ZENITH_THEMES = {
    "zenith_default": {
        "name": "分形天顶",
        "core": (75, 0, 130),        # 靛青核心
        "blade": (255, 255, 255),    # 纯白剑刃
        "glow": (255, 0, 255),       # 品红光效
        "pixel": (255, 255, 255),    # 像素碎片
        "trail": (147, 112, 219),    # 紫罗兰拖尾
        "accent": (200, 100, 255),   # 强调色
        "energy": (180, 80, 255),    # 能量色
    },
    "zenith_terra": {
        "name": "泰拉圣剑",
        "core": (0, 200, 100),       # 泰拉绿
        "blade": (100, 255, 150),    # 翠绿刃
        "glow": (50, 255, 100),      # 绿光
        "pixel": (200, 255, 200),    # 绿碎片
        "trail": (0, 180, 80),       # 暗绿尾
        "accent": (150, 255, 180),   # 强调色
        "energy": (80, 220, 120),    # 能量色
    },
    "zenith_meowmere": {
        "name": "喵喵彩虹",
        "core": (255, 150, 200),     # 粉色核心
        "blade": (255, 200, 220),    # 粉刃
        "glow": (255, 100, 180),     # 粉光
        "pixel": (255, 255, 255),    # 白碎片
        "trail": (255, 180, 220),    # 粉尾
        "accent": (255, 220, 240),   # 强调色
        "energy": (255, 130, 200),   # 能量色
    },
    "zenith_stardust": {
        "name": "星尘龙骸",
        "core": (0, 150, 255),       # 星蓝
        "blade": (100, 200, 255),    # 浅蓝刃
        "glow": (50, 180, 255),      # 蓝光
        "pixel": (200, 230, 255),    # 星碎片
        "trail": (0, 120, 200),      # 深蓝尾
        "accent": (150, 220, 255),   # 强调色
        "energy": (80, 180, 255),    # 能量色
    },
    "zenith_solar": {
        "name": "日耀烈焰",
        "core": (255, 100, 0),       # 烈焰橙
        "blade": (255, 180, 50),     # 金刃
        "glow": (255, 150, 0),       # 橙光
        "pixel": (255, 220, 100),    # 火碎片
        "trail": (200, 80, 0),       # 深橙尾
        "accent": (255, 200, 100),   # 强调色
        "energy": (255, 120, 30),    # 能量色
    },
    "zenith_void": {
        "name": "虚空终末",
        "core": (30, 0, 50),         # 虚空紫
        "blade": (80, 20, 120),      # 暗紫刃
        "glow": (100, 0, 150),       # 虚空光
        "pixel": (50, 0, 80),        # 暗碎片
        "trail": (60, 0, 100),       # 深紫尾
        "accent": (120, 40, 180),    # 强调色
        "energy": (80, 0, 130),      # 能量色
    },
}

ZENITH_STYLES = list(ZENITH_THEMES.keys())


def is_zenith_style(style):
    """检查是否为天顶涂装"""
    return style in ZENITH_STYLES


def get_zenith_theme(style):
    """获取天顶涂装主题"""
    return ZENITH_THEMES.get(style, ZENITH_THEMES["zenith_default"])


# ==================== 名剑数据 ====================
LEGENDARY_SWORDS = [
    {"name": "泰拉刃", "color": (0, 255, 100), "length": 18},
    {"name": "喵喵刃", "color": (255, 150, 200), "length": 16},
    {"name": "星尘龙剑", "color": (0, 180, 255), "length": 20},
    {"name": "日耀剑", "color": (255, 150, 0), "length": 17},
    {"name": "星旋剑", "color": (0, 220, 200), "length": 15},
    {"name": "星云剑", "color": (200, 80, 255), "length": 16},
    {"name": "流星剑", "color": (150, 200, 230), "length": 14},
    {"name": "种子剑", "color": (100, 200, 80), "length": 13},
    {"name": "无头骑士剑", "color": (255, 120, 0), "length": 19},
    {"name": "彩虹猫之刃", "color": (255, 100, 180), "length": 15},
    {"name": "铜短剑", "color": (200, 150, 100), "length": 8},
    {"name": "断钢剑", "color": (180, 180, 200), "length": 14},
]


def _get_rainbow_color(frame, offset=0):
    """获取彩虹循环颜色"""
    hue = ((frame * 3 + offset) % 360) / 360.0
    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    return (int(r * 255), int(g * 255), int(b * 255))


def _blend_color(c1, c2, ratio):
    """混合两个颜色"""
    return tuple(int(c1[i] * (1 - ratio) + c2[i] * ratio) for i in range(3))


def _draw_detailed_sword(surface, cx, cy, angle, length, color, frame, glow_intensity=1.0):
    """绘制高精度剑刃 - 多层结构"""
    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    perp_cos, perp_sin = math.cos(rad + math.pi/2), math.sin(rad + math.pi/2)
    
    # 剑尖位置
    tip_x = cx + cos_a * length
    tip_y = cy + sin_a * length
    # 剑柄位置
    hilt_x = cx - cos_a * 5
    hilt_y = cy - sin_a * 5
    
    # 剑身宽度
    blade_width = max(2, length * 0.15)
    
    # === 第1层：外发光（最大范围）===
    for i in range(3):
        glow_w = blade_width + 4 - i
        glow_alpha = int((40 - i * 12) * glow_intensity)
        if glow_alpha > 0:
            # 计算剑身多边形
            pts = [
                (tip_x, tip_y),
                (cx + perp_cos * glow_w, cy + perp_sin * glow_w),
                (hilt_x + perp_cos * glow_w * 0.6, hilt_y + perp_sin * glow_w * 0.6),
                (hilt_x - perp_cos * glow_w * 0.6, hilt_y - perp_sin * glow_w * 0.6),
                (cx - perp_cos * glow_w, cy - perp_sin * glow_w),
            ]
            pts = [(int(p[0]), int(p[1])) for p in pts]
            glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            offset_pts = [(p[0] - int(cx) + 60, p[1] - int(cy) + 60) for p in pts]
            pygame.draw.polygon(glow_surf, (*color, glow_alpha), offset_pts)
            surface.blit(glow_surf, (int(cx) - 60, int(cy) - 60))
    
    # === 第2层：剑身主体 ===
    blade_pts = [
        (tip_x, tip_y),
        (cx + perp_cos * blade_width, cy + perp_sin * blade_width),
        (hilt_x + perp_cos * blade_width * 0.4, hilt_y + perp_sin * blade_width * 0.4),
        (hilt_x - perp_cos * blade_width * 0.4, hilt_y - perp_sin * blade_width * 0.4),
        (cx - perp_cos * blade_width, cy - perp_sin * blade_width),
    ]
    blade_pts = [(int(p[0]), int(p[1])) for p in blade_pts]
    pygame.draw.polygon(surface, color, blade_pts)
    
    # === 第3层：剑身高光（沿中线）===
    highlight_color = (min(255, color[0] + 80), min(255, color[1] + 80), min(255, color[2] + 80))
    mid_x = (tip_x + hilt_x) / 2
    mid_y = (tip_y + hilt_y) / 2
    pygame.draw.line(surface, highlight_color, 
                    (int(hilt_x), int(hilt_y)), (int(tip_x), int(tip_y)), 2)
    
    # === 第4层：剑尖闪光 ===
    pygame.draw.circle(surface, (255, 255, 255), (int(tip_x), int(tip_y)), 3)
    pygame.draw.circle(surface, color, (int(tip_x), int(tip_y)), 2)
    
    # === 第5层：剑柄装饰 ===
    pygame.draw.circle(surface, (80, 60, 40), (int(hilt_x), int(hilt_y)), 4)
    pygame.draw.circle(surface, (180, 150, 100), (int(hilt_x), int(hilt_y)), 2)


def _draw_legendary_blade(surface, cx, cy, angle, sword_data, frame, scale=1.0, alpha=255):
    """绘制传奇剑刃 - 带名剑特效"""
    color = sword_data["color"]
    length = sword_data["length"] * scale
    
    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    perp_cos, perp_sin = math.cos(rad + math.pi/2), math.sin(rad + math.pi/2)
    
    tip_x = cx + cos_a * length
    tip_y = cy + sin_a * length
    hilt_x = cx - cos_a * 4
    hilt_y = cy - sin_a * 4
    
    blade_width = max(2, length * 0.12)
    
    # 光晕
    glow_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
    for i in range(2):
        glow_alpha = int((50 - i * 20) * alpha / 255)
        if glow_alpha > 0:
            pygame.draw.line(glow_surf, (*color, glow_alpha),
                           (40 - cos_a * 4, 40 - sin_a * 4),
                           (40 + cos_a * length, 40 + sin_a * length), int(6 - i * 2))
    surface.blit(glow_surf, (int(cx) - 40, int(cy) - 40))
    
    # 剑身
    blade_pts = [
        (tip_x, tip_y),
        (cx + perp_cos * blade_width, cy + perp_sin * blade_width),
        (hilt_x, hilt_y),
        (cx - perp_cos * blade_width, cy - perp_sin * blade_width),
    ]
    blade_pts = [(int(p[0]), int(p[1])) for p in blade_pts]
    
    blade_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
    offset_pts = [(p[0] - int(cx) + 40, p[1] - int(cy) + 40) for p in blade_pts]
    pygame.draw.polygon(blade_surf, (*color, alpha), offset_pts)
    surface.blit(blade_surf, (int(cx) - 40, int(cy) - 40))
    
    # 剑尖
    if alpha > 200:
        pygame.draw.circle(surface, (255, 255, 255), (int(tip_x), int(tip_y)), 2)


def _draw_pixel_field(surface, cx, cy, frame, theme, count=12, radius=40):
    """绘制像素碎片场 - 增强版"""
    import random
    random.seed(int(frame * 0.3))
    
    pixel_color = theme.get("pixel", (255, 255, 255))
    glow_color = theme.get("glow", (255, 0, 255))
    
    for i in range(count):
        # 双螺旋分布
        spiral_angle = frame * 2 + i * (360 / count)
        wave = 8 * math.sin(frame * 0.1 + i * 0.5)
        dist = radius + wave
        
        angle_rad = math.radians(spiral_angle)
        px = cx + math.cos(angle_rad) * dist
        py = cy + math.sin(angle_rad) * dist
        
        # 像素大小脉动
        base_size = 3 + int(2 * math.sin(frame * 0.15 + i * 0.3))
        
        # 交替使用主题色和彩虹色
        if i % 3 == 0:
            color = _get_rainbow_color(frame, i * 30)
        else:
            color = pixel_color
        
        alpha = int(150 + 80 * math.sin(frame * 0.2 + i * 0.4))
        
        # 像素块 + 光晕
        pixel_surf = pygame.Surface((base_size * 3, base_size * 3), pygame.SRCALPHA)
        # 外光晕
        pygame.draw.rect(pixel_surf, (*glow_color, alpha // 4), 
                        (0, 0, base_size * 3, base_size * 3))
        # 内核
        pygame.draw.rect(pixel_surf, (*color, alpha), 
                        (base_size, base_size, base_size, base_size))
        # 高光点
        pygame.draw.rect(pixel_surf, (255, 255, 255, alpha // 2), 
                        (base_size, base_size, 1, 1))
        
        surface.blit(pixel_surf, (int(px - base_size * 1.5), int(py - base_size * 1.5)))


# ==================== 新版核心绘制组件 ====================

def _draw_hilt_core(surface, cx, cy, frame, theme):
    """
    A. 核心：棱镜剑柄 (The Hilt Core) - 高精度版
    - 机械护手 + 黑曜石剑柄 + 多层金属质感
    - 中心镶嵌RGB循环变色的泰拉棱镜
    """
    core_color = theme.get("core", (75, 0, 130))
    glow_color = theme.get("glow", (255, 0, 255))
    accent_color = theme.get("accent", (200, 100, 255))
    
    # === 黑曜石剑柄（垂直向上）- 多层结构 ===
    # 最外层：金属边框
    pygame.draw.rect(surface, (50, 50, 55), (cx - 5, cy - 10, 10, 20))
    # 内层：黑曜石本体
    pygame.draw.rect(surface, (26, 26, 30), (cx - 4, cy - 9, 8, 18))
    # 高光条
    pygame.draw.line(surface, (60, 60, 70), (cx - 2, cy - 8), (cx - 2, cy + 7), 1)
    # 暗影条
    pygame.draw.line(surface, (15, 15, 18), (cx + 2, cy - 8), (cx + 2, cy + 7), 1)
    
    # === 机械护手（横向）- 精细结构 ===
    guard_color = (65, 55, 75)
    guard_highlight = (90, 80, 100)
    guard_shadow = (40, 35, 50)
    
    # 护手主体
    pygame.draw.rect(surface, guard_color, (cx - 16, cy - 3, 32, 8))
    # 上边缘高光
    pygame.draw.line(surface, guard_highlight, (cx - 15, cy - 2), (cx + 15, cy - 2), 1)
    # 下边缘阴影
    pygame.draw.line(surface, guard_shadow, (cx - 15, cy + 4), (cx + 15, cy + 4), 1)
    
    # 护手两端装饰 - 宝石镶嵌
    for side in [-1, 1]:
        gem_x = cx + side * 13
        # 底座
        pygame.draw.circle(surface, (50, 40, 60), (gem_x, cy + 1), 4)
        pygame.draw.circle(surface, (70, 60, 80), (gem_x, cy + 1), 3)
        # 小宝石 - 随主题变色
        gem_color = _get_rainbow_color(frame, side * 90)
        pygame.draw.circle(surface, gem_color, (gem_x, cy + 1), 2)
        pygame.draw.circle(surface, (255, 255, 255, 180), (gem_x - 1, cy), 1)
    
    # 护手中央装饰线
    pygame.draw.line(surface, accent_color, (cx - 8, cy + 1), (cx - 4, cy + 1), 1)
    pygame.draw.line(surface, accent_color, (cx + 4, cy + 1), (cx + 8, cy + 1), 1)
    
    # === 泰拉棱镜（RGB循环变色水晶）- 高精度版 ===
    rgb_color = _get_rainbow_color(frame, 0)
    
    # 棱镜外发光 - 多层渐变
    for i in range(5):
        r = 14 - i * 2
        alpha = 50 - i * 8
        if r > 0 and alpha > 0:
            glow_surf = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*rgb_color, alpha), (r + 4, r + 4), r)
            surface.blit(glow_surf, (cx - r - 4, cy - r - 4))
    
    # 棱镜主体（多层钻石形）
    # 外层 - 稍暗
    prism_outer = [
        (cx, cy - 9), (cx + 7, cy), (cx, cy + 9), (cx - 7, cy)
    ]
    pygame.draw.polygon(surface, _blend_color(rgb_color, (0, 0, 0), 0.3), prism_outer)
    
    # 中层 - 主色
    prism_mid = [
        (cx, cy - 7), (cx + 5, cy), (cx, cy + 7), (cx - 5, cy)
    ]
    pygame.draw.polygon(surface, rgb_color, prism_mid)
    
    # 内层 - 高光区
    prism_inner = [
        (cx - 2, cy - 4), (cx + 1, cy - 1), (cx - 2, cy + 2), (cx - 4, cy - 1)
    ]
    highlight_color = (min(255, rgb_color[0] + 100), 
                       min(255, rgb_color[1] + 100), 
                       min(255, rgb_color[2] + 100))
    pygame.draw.polygon(surface, highlight_color, prism_inner)
    
    # 棱镜边框
    pygame.draw.polygon(surface, (255, 255, 255), prism_outer, 1)
    
    # 中心闪光点
    flash_alpha = int(200 + 55 * math.sin(frame * 0.3))
    flash_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
    pygame.draw.circle(flash_surf, (255, 255, 255, flash_alpha), (3, 3), 2)
    surface.blit(flash_surf, (cx - 3, cy - 3))


def _draw_fractal_rings(surface, cx, cy, frame, theme):
    """
    B. 机身：分形剑刃三环结构 (Fractal Blades) - 高精度版
    - 内环：绿色泰拉刃碎片，顺时针慢转
    - 中环：粉/彩虹碎片，逆时针中速转
    - 外环：半透明全息剑影，高速转形成光轮
    """
    blade_color = theme.get("blade", (255, 255, 255))
    glow_color = theme.get("glow", (255, 0, 255))
    energy_color = theme.get("energy", (180, 80, 255))
    
    # === 外环：全息剑影光轮（最底层）===
    outer_count = 12
    outer_radius = 44
    outer_speed = frame * 6
    
    # 光轮残影底层
    for i in range(3):
        r = outer_radius + 2 - i * 2
        ring_color = _get_rainbow_color(frame, i * 40)
        alpha = 35 - i * 10
        ring_surf = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (*ring_color, alpha), (r + 5, r + 5), r, 3)
        surface.blit(ring_surf, (cx - r - 5, cy - r - 5))
    
    # 外环剑刃
    for i in range(outer_count):
        angle = outer_speed + (360 / outer_count) * i
        rad = math.radians(angle)
        fx = cx + math.cos(rad) * outer_radius
        fy = cy + math.sin(rad) * outer_radius
        
        holo_color = _get_rainbow_color(frame, i * 30)
        sword_data = {"color": holo_color, "length": 10}
        _draw_legendary_blade(surface, fx, fy, angle + 90, sword_data, frame, 0.8, 100)
    
    # === 中环：星怒/喵刃碎片 ===
    mid_count = 8
    mid_radius = 30
    mid_speed = -frame * 3.5
    
    for i in range(mid_count):
        angle = mid_speed + (360 / mid_count) * i
        rad = math.radians(angle)
        fx = cx + math.cos(rad) * mid_radius
        fy = cy + math.sin(rad) * mid_radius
        
        # 交替粉色和彩虹
        if i % 2 == 0:
            frag_color = (255, 150, 200)
        else:
            frag_color = _get_rainbow_color(frame, i * 45)
        
        sword_data = {"color": frag_color, "length": 12}
        _draw_legendary_blade(surface, fx, fy, angle + 90, sword_data, frame, 0.9, 220)
    
    # === 内环：泰拉刃碎片 ===
    inner_count = 6
    inner_radius = 18
    inner_speed = frame * 2
    terra_green = (80, 220, 130)
    
    for i in range(inner_count):
        angle = inner_speed + (360 / inner_count) * i
        rad = math.radians(angle)
        fx = cx + math.cos(rad) * inner_radius
        fy = cy + math.sin(rad) * inner_radius
        
        sword_data = {"color": terra_green, "length": 10}
        _draw_legendary_blade(surface, fx, fy, angle + 90, sword_data, frame, 0.85, 255)
    
    # === 环间能量连接 ===
    arc_count = 6
    for i in range(arc_count):
        arc_angle = frame * 4 + (360 / arc_count) * i
        rad = math.radians(arc_angle)
        
        # 从内环到中环
        inner_x = cx + math.cos(rad) * inner_radius
        inner_y = cy + math.sin(rad) * inner_radius
        mid_x = cx + math.cos(rad + 0.2) * mid_radius
        mid_y = cy + math.sin(rad + 0.2) * mid_radius
        
        arc_color = _get_rainbow_color(frame, i * 60)
        arc_alpha = int(80 + 40 * math.sin(frame * 0.15 + i))
        
        arc_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.line(arc_surf, (*arc_color, arc_alpha),
                        (inner_x - cx + 50, inner_y - cy + 50),
                        (mid_x - cx + 50, mid_y - cy + 50), 2)
        surface.blit(arc_surf, (cx - 50, cy - 50))


def _draw_glitch_exhaust(surface, cx, cy, frame, theme):
    """
    C. 推进器：像素拖尾/故障效果 (Afterimage Exhaust) - 高精度版
    - 双引擎像素拉丝拖尾
    - 彩虹渐变 + 故障闪烁
    """
    import random
    random.seed(int(frame * 0.25))
    
    trail_color = theme.get("trail", (147, 112, 219))
    glow_color = theme.get("glow", (255, 0, 255))
    
    # 双引擎
    for side in [-1, 1]:
        base_x = cx + side * 10
        base_y = cy + 12
        
        # 引擎核心发光
        for i in range(3):
            r = 6 - i * 2
            alpha = 60 - i * 15
            engine_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(engine_surf, (*glow_color, alpha), (r + 2, r + 2), r)
            surface.blit(engine_surf, (int(base_x - r - 2), int(base_y - r - 2)))
        
        # 像素拖尾 - 多层
        for layer in range(3):
            layer_offset = layer * 2
            
            for i in range(15):
                # 故障偏移
                glitch_x = random.uniform(-4, 4) if (frame + i) % 4 == 0 else 0
                
                trail_y = base_y + i * 5 + layer_offset
                trail_x = base_x + glitch_x + side * (i * 0.4) + layer * side * 0.5
                
                # 渐变色
                progress = i / 15
                rgb = _get_rainbow_color(frame, i * 20 + side * 60 + layer * 30)
                
                # 透明度衰减
                alpha = max(0, int(180 * (1 - progress) - layer * 30))
                
                # 大小衰减
                size = max(1, int((5 - layer) * (1 - progress * 0.6)))
                
                if alpha > 0 and size > 0:
                    pixel_surf = pygame.Surface((size + 4, size + 4), pygame.SRCALPHA)
                    # 光晕
                    pygame.draw.rect(pixel_surf, (*rgb, alpha // 3), (0, 0, size + 4, size + 4))
                    # 核心
                    pygame.draw.rect(pixel_surf, (*rgb, alpha), (2, 2, size, size))
                    surface.blit(pixel_surf, (int(trail_x - size // 2 - 2), int(trail_y)))


def _draw_enchanted_wings(surface, cx, cy, frame, theme):
    """
    D. 侧翼：附魔剑刃 (Enchanted Wings) - 高精度版
    - 两把悬浮的附魔剑，带能量场
    - 动态悬浮 + 附魔光环
    """
    blade_color = theme.get("blade", (255, 255, 255))
    energy_color = theme.get("energy", (180, 80, 255))
    glow_color = theme.get("glow", (255, 0, 255))
    
    for side in [-1, 1]:
        # 悬浮动画
        float_offset = 4 * math.sin(frame * 0.08 + side * 0.5)
        wing_x = cx + side * 38
        wing_y = cy + 5 + float_offset
        
        # 剑的角度 - 稍微向外倾斜
        sword_angle = -90 + side * 18 + 3 * math.sin(frame * 0.1)
        sword_length = 26
        
        rad = math.radians(sword_angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        
        tip_x = wing_x + cos_a * sword_length
        tip_y = wing_y + sin_a * sword_length
        hilt_x = wing_x - cos_a * 8
        hilt_y = wing_y - sin_a * 8
        
        # === 附魔光环 ===
        enchant_rgb = _get_rainbow_color(frame, side * 90 + 180)
        for i in range(3):
            r = 12 - i * 3
            alpha = 40 - i * 10
            aura_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (*enchant_rgb, alpha), (r + 2, r + 2), r)
            surface.blit(aura_surf, (int(wing_x - r - 2), int(wing_y - r - 2)))
        
        # === 剑身光晕 ===
        glow_surf = pygame.Surface((60, 70), pygame.SRCALPHA)
        pygame.draw.line(glow_surf, (*enchant_rgb, 40),
                        (30 - cos_a * 8, 35 - sin_a * 8),
                        (30 + cos_a * sword_length, 35 + sin_a * sword_length), 10)
        pygame.draw.line(glow_surf, (*energy_color, 60),
                        (30 - cos_a * 8, 35 - sin_a * 8),
                        (30 + cos_a * sword_length, 35 + sin_a * sword_length), 6)
        surface.blit(glow_surf, (int(wing_x - 30), int(wing_y - 35)))
        
        # === 剑身主体 ===
        # 使用高精度剑刃绘制
        sword_data = {"color": blade_color, "length": sword_length}
        _draw_detailed_sword(surface, wing_x, wing_y, sword_angle, sword_length, 
                            blade_color, frame, 1.2)
        
        # === 剑柄宝石 ===
        pygame.draw.circle(surface, (80, 60, 40), (int(hilt_x), int(hilt_y)), 5)
        pygame.draw.circle(surface, (180, 150, 100), (int(hilt_x), int(hilt_y)), 3)
        gem_color = _get_rainbow_color(frame + side * 30, 0)
        pygame.draw.circle(surface, gem_color, (int(hilt_x), int(hilt_y)), 2)


def _draw_rgb_core(surface, cx, cy, frame, base_color):
    """绘制RGB棱镜核心（旧版保留兼容）"""
    # 多层光晕
    for i in range(4):
        r = 12 - i * 2 + 2 * math.sin(frame * 0.15 + i)
        rgb_color = _get_rainbow_color(frame, i * 30)
        alpha = 80 - i * 15
        if r > 0:
            glow_surf = pygame.Surface((int(r * 2 + 4), int(r * 2 + 4)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*rgb_color, alpha), (int(r + 2), int(r + 2)), int(r))
            surface.blit(glow_surf, (int(cx - r - 2), int(cy - r - 2)))
    
    # 核心棱镜（六边形）
    prism_pts = []
    for i in range(6):
        angle = math.radians(i * 60 + frame * 2)
        px = cx + math.cos(angle) * 8
        py = cy + math.sin(angle) * 8
        prism_pts.append((int(px), int(py)))
    pygame.draw.polygon(surface, base_color, prism_pts)
    pygame.draw.polygon(surface, (255, 255, 255), prism_pts, 1)


def _draw_sword_array(surface, cx, cy, frame, theme):
    """绘制环绕剑阵（旧版保留兼容）"""
    sword_count = len(LEGENDARY_SWORDS)
    base_angle = frame * 3  # 旋转速度
    
    for i, sword in enumerate(LEGENDARY_SWORDS):
        # 每把剑的角度
        angle = base_angle + (360 / sword_count) * i
        # 螺旋轨道
        orbit_r = 28 + 8 * math.sin(frame * 0.08 + i * 0.5)
        sword_x = cx + math.cos(math.radians(angle)) * orbit_r
        sword_y = cy + math.sin(math.radians(angle)) * orbit_r
        
        # 剑指向切线方向（旋转感）
        sword_angle = angle + 90 + 15 * math.sin(frame * 0.1 + i)
        
        # 根据涂装调整颜色
        if theme.get("name") == "喵喵彩虹":
            color = _get_rainbow_color(frame, i * 30)
        else:
            color = sword["color"]
        
        _draw_legendary_blade(surface, sword_x, sword_y, sword_angle, sword, frame)


# ==================== 涂装绘制调度 ====================
def draw_zenith(surface, color, x, y, w, h, frame, style="zenith_default"):
    """绘制天顶机体 - 根据涂装调用专属绘制"""
    drawers = {
        "zenith_default": _draw_default_zenith,
        "zenith_terra": _draw_terra_zenith,
        "zenith_meowmere": _draw_meowmere_zenith,
        "zenith_stardust": _draw_stardust_zenith,
        "zenith_solar": _draw_solar_zenith,
        "zenith_void": _draw_void_zenith,
    }
    drawer = drawers.get(style, _draw_default_zenith)
    drawer(surface, x, y, w, h, frame, style)


def render_zenith_skin(surface, color, model_style, t, pid, static):
    """渲染天顶涂装入口"""
    frame = int(t * 60) if not static else 0
    draw_zenith(surface, color, 10, 10, 100, 100, frame, model_style)
    return surface


# ==================== 默认涂装：分形天顶（回旋镖母舰） ====================
def _draw_default_zenith(surface, x, y, w, h, frame, style):
    """
    默认分形天顶 - 回旋镖母舰 (Boomerang Mothership) - 高精度版
    
    结构：
    A. 核心：棱镜剑柄 - RGB循环变色的泰拉棱镜
    B. 机身：三层环状分形剑刃
    C. 推进器：像素故障拖尾
    D. 侧翼：悬浮附魔剑
    E. 装饰：像素碎片场
    """
    theme = get_zenith_theme(style)
    cx, cy = x + w // 2, y + h // 2
    
    # E. 像素碎片场（最底层）
    _draw_pixel_field(surface, cx, cy, frame, theme, 16, 48)
    
    # C. 像素故障拖尾
    _draw_glitch_exhaust(surface, cx, cy, frame, theme)
    
    # D. 侧翼附魔剑
    _draw_enchanted_wings(surface, cx, cy, frame, theme)
    
    # B. 三层分形剑刃环
    _draw_fractal_rings(surface, cx, cy, frame, theme)
    
    # A. 棱镜剑柄核心（最顶层）
    _draw_hilt_core(surface, cx, cy, frame, theme)


# ==================== 泰拉圣剑 - 高精度版 ====================
def _draw_terra_zenith(surface, x, y, w, h, frame, style):
    """泰拉圣剑 - 翠绿圣光剑阵 - 高精度版"""
    theme = get_zenith_theme(style)
    cx, cy = x + w // 2, y + h // 2
    
    terra_green = theme["blade"]
    terra_glow = theme["glow"]
    terra_core = theme["core"]
    
    # === 自然能量场 ===
    for layer in range(4):
        wave = 3 * math.sin(frame * 0.08 + layer * 0.5)
        r = 46 - layer * 8 + wave
        alpha = 35 - layer * 8
        if r > 0 and alpha > 0:
            field_surf = pygame.Surface((int(r * 2 + 8), int(r * 2 + 8)), pygame.SRCALPHA)
            pygame.draw.circle(field_surf, (*terra_glow, alpha), (int(r + 4), int(r + 4)), int(r))
            surface.blit(field_surf, (int(cx - r - 4), int(cy - r - 4)))
    
    # === 藤蔓能量线 ===
    vine_count = 6
    for i in range(vine_count):
        vine_angle = frame * 1.5 + i * (360 / vine_count)
        vine_pts = []
        for j in range(12):
            seg_angle = vine_angle + j * 8
            seg_r = 15 + j * 2.5 + 3 * math.sin(frame * 0.1 + j * 0.3)
            vx = cx + math.cos(math.radians(seg_angle)) * seg_r
            vy = cy + math.sin(math.radians(seg_angle)) * seg_r
            vine_pts.append((int(vx), int(vy)))
        if len(vine_pts) > 1:
            vine_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
            offset_pts = [(p[0] - cx + 50, p[1] - cy + 50) for p in vine_pts]
            pygame.draw.lines(vine_surf, (*terra_glow, 120), False, offset_pts, 2)
            surface.blit(vine_surf, (cx - 50, cy - 50))
    
    # === 泰拉刃专属剑阵 ===
    sword_count = 10
    for i in range(sword_count):
        angle = frame * 3 + (360 / sword_count) * i
        orbit_r = 32 + 6 * math.sin(frame * 0.12 + i * 0.4)
        sx = cx + math.cos(math.radians(angle)) * orbit_r
        sy = cy + math.sin(math.radians(angle)) * orbit_r
        
        # 剑指向切线
        sword_angle = angle + 90 + 10 * math.sin(frame * 0.08 + i)
        
        sword_data = {"color": terra_green, "length": 16}
        _draw_legendary_blade(surface, sx, sy, sword_angle, sword_data, frame, 1.0, 230)
        
        # 叶片粒子
        if i % 3 == 0:
            leaf_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            leaf_alpha = int(150 + 50 * math.sin(frame * 0.2 + i))
            pygame.draw.ellipse(leaf_surf, (*terra_glow, leaf_alpha), (0, 2, 8, 4))
            surface.blit(leaf_surf, (int(sx - 4), int(sy - 4)))
    
    # === 泰拉核心 ===
    # 外圈光晕
    for i in range(4):
        r = 14 - i * 3
        alpha = 80 - i * 18
        core_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(core_surf, (*terra_glow, alpha), (r + 2, r + 2), r)
        surface.blit(core_surf, (cx - r - 2, cy - r - 2))
    
    # 核心主体
    pygame.draw.circle(surface, terra_core, (cx, cy), 11)
    pygame.draw.circle(surface, terra_green, (cx, cy), 8)
    pygame.draw.circle(surface, (200, 255, 220), (cx, cy), 5)
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 2)
    
    # 核心边框
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 11, 1)


# ==================== 喵喵彩虹 - 高精度版 ====================
def _draw_meowmere_zenith(surface, x, y, w, h, frame, style):
    """喵喵彩虹 - 彩虹猫头弹幕 - 高精度版"""
    theme = get_zenith_theme(style)
    cx, cy = x + w // 2, y + h // 2
    
    pink_core = theme["core"]
    pink_glow = theme["glow"]
    
    # === 彩虹拖尾环 ===
    rainbow_layers = 7
    for layer in range(rainbow_layers):
        trail_r = 42 - layer * 3
        trail_angle = frame * 4 + layer * 15
        
        trail_pts = []
        for i in range(20):
            seg_angle = trail_angle + i * 8
            wave = 5 * math.sin(frame * 0.15 + i * 0.3 + layer * 0.2)
            seg_r = trail_r + wave
            tx = cx + math.cos(math.radians(seg_angle)) * seg_r
            ty = cy + math.sin(math.radians(seg_angle)) * seg_r
            trail_pts.append((int(tx), int(ty)))
        
        if len(trail_pts) > 1:
            rgb = _get_rainbow_color(frame, layer * 50)
            alpha = 100 - layer * 12
            trail_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
            offset_pts = [(p[0] - cx + 50, p[1] - cy + 50) for p in trail_pts]
            pygame.draw.lines(trail_surf, (*rgb, alpha), False, offset_pts, 3)
            surface.blit(trail_surf, (cx - 50, cy - 50))
    
    # === 彩虹猫头环绕 ===
    cat_count = 8
    for i in range(cat_count):
        angle = frame * 5 + (360 / cat_count) * i
        orbit_r = 34
        float_y = 3 * math.sin(frame * 0.12 + i * 0.5)
        cat_x = cx + math.cos(math.radians(angle)) * orbit_r
        cat_y = cy + math.sin(math.radians(angle)) * orbit_r + float_y
        
        rgb = _get_rainbow_color(frame, i * 45)
        
        # 猫头光晕
        glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*rgb, 60), (10, 10), 8)
        surface.blit(glow_surf, (int(cat_x - 10), int(cat_y - 10)))
        
        # 猫脸
        pygame.draw.circle(surface, rgb, (int(cat_x), int(cat_y)), 7)
        
        # 耳朵
        ear_pts_l = [(int(cat_x - 5), int(cat_y - 4)), 
                     (int(cat_x - 3), int(cat_y - 10)), 
                     (int(cat_x - 1), int(cat_y - 4))]
        ear_pts_r = [(int(cat_x + 5), int(cat_y - 4)), 
                     (int(cat_x + 3), int(cat_y - 10)), 
                     (int(cat_x + 1), int(cat_y - 4))]
        pygame.draw.polygon(surface, rgb, ear_pts_l)
        pygame.draw.polygon(surface, rgb, ear_pts_r)
        
        # 内耳
        pygame.draw.polygon(surface, (255, 200, 220), 
                           [(int(cat_x - 4), int(cat_y - 5)), 
                            (int(cat_x - 3), int(cat_y - 8)), 
                            (int(cat_x - 2), int(cat_y - 5))])
        pygame.draw.polygon(surface, (255, 200, 220), 
                           [(int(cat_x + 4), int(cat_y - 5)), 
                            (int(cat_x + 3), int(cat_y - 8)), 
                            (int(cat_x + 2), int(cat_y - 5))])
        
        # 眼睛
        pygame.draw.circle(surface, (0, 0, 0), (int(cat_x - 2), int(cat_y - 1)), 2)
        pygame.draw.circle(surface, (0, 0, 0), (int(cat_x + 2), int(cat_y - 1)), 2)
        pygame.draw.circle(surface, (255, 255, 255), (int(cat_x - 2), int(cat_y - 2)), 1)
        pygame.draw.circle(surface, (255, 255, 255), (int(cat_x + 2), int(cat_y - 2)), 1)
        
        # 鼻子
        pygame.draw.circle(surface, (255, 150, 180), (int(cat_x), int(cat_y + 1)), 1)
        
        # 胡须
        whisker_alpha = int(150 + 50 * math.sin(frame * 0.2 + i))
        whisker_surf = pygame.Surface((20, 10), pygame.SRCALPHA)
        pygame.draw.line(whisker_surf, (*rgb, whisker_alpha), (0, 3), (7, 2), 1)
        pygame.draw.line(whisker_surf, (*rgb, whisker_alpha), (0, 5), (7, 5), 1)
        pygame.draw.line(whisker_surf, (*rgb, whisker_alpha), (0, 7), (7, 8), 1)
        pygame.draw.line(whisker_surf, (*rgb, whisker_alpha), (20, 3), (13, 2), 1)
        pygame.draw.line(whisker_surf, (*rgb, whisker_alpha), (20, 5), (13, 5), 1)
        pygame.draw.line(whisker_surf, (*rgb, whisker_alpha), (20, 7), (13, 8), 1)
        surface.blit(whisker_surf, (int(cat_x - 10), int(cat_y)))
    
    # === 粉色核心 ===
    for i in range(4):
        r = 16 - i * 3
        alpha = 70 - i * 15
        core_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(core_surf, (*pink_glow, alpha), (r + 2, r + 2), r)
        surface.blit(core_surf, (cx - r - 2, cy - r - 2))
    
    pygame.draw.circle(surface, pink_core, (cx, cy), 13)
    pygame.draw.circle(surface, (255, 200, 220), (cx, cy), 9)
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 5)
    
    # 爱心装饰
    heart_x, heart_y = cx, cy
    heart_pts = [
        (heart_x, heart_y + 3),
        (heart_x - 3, heart_y - 1),
        (heart_x - 2, heart_y - 3),
        (heart_x, heart_y - 1),
        (heart_x + 2, heart_y - 3),
        (heart_x + 3, heart_y - 1),
    ]
    pygame.draw.polygon(surface, (255, 100, 150), heart_pts)


# ==================== 星尘龙骸 - 高精度版 ====================
def _draw_stardust_zenith(surface, x, y, w, h, frame, style):
    """星尘龙骸 - 星蓝龙形剑阵 - 高精度版"""
    theme = get_zenith_theme(style)
    cx, cy = x + w // 2, y + h // 2
    
    star_blue = theme["blade"]
    star_glow = theme["glow"]
    star_core = theme["core"]
    
    # === 星尘粒子场 ===
    import random
    random.seed(int(frame * 0.2))
    for i in range(20):
        angle = random.uniform(0, 360)
        dist = random.uniform(15, 50)
        px = cx + math.cos(math.radians(angle)) * dist
        py = cy + math.sin(math.radians(angle)) * dist
        
        # 闪烁效果
        twinkle = math.sin(frame * 0.3 + i * 0.7)
        if twinkle > 0.3:
            alpha = int(100 + 100 * twinkle)
            size = 2 + int(2 * twinkle)
            
            star_surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
            # 十字星芒
            pygame.draw.line(star_surf, (*star_glow, alpha), 
                           (size * 1.5, 0), (size * 1.5, size * 3), 1)
            pygame.draw.line(star_surf, (*star_glow, alpha), 
                           (0, size * 1.5), (size * 3, size * 1.5), 1)
            # 核心
            pygame.draw.circle(star_surf, (*star_blue, alpha), 
                             (int(size * 1.5), int(size * 1.5)), size)
            surface.blit(star_surf, (int(px - size * 1.5), int(py - size * 1.5)))
    
    # === 龙形剑阵 - 蛇形身躯 ===
    seg_count = 14
    dragon_pts = []
    for i in range(seg_count):
        wave = 18 * math.sin(frame * 0.12 + i * 0.5)
        seg_y = cy - 35 + i * 5
        seg_x = cx + wave
        dragon_pts.append((seg_x, seg_y))
        
        # 龙身剑刃
        sword_angle = -90 + wave * 1.5
        seg_size = 1.2 - i * 0.06 if i < 10 else 0.6 + (i - 10) * 0.1
        
        sword_data = {"color": star_blue, "length": 12}
        _draw_legendary_blade(surface, seg_x, seg_y, sword_angle, sword_data, frame, seg_size, 220)
    
    # 龙脊连接线
    if len(dragon_pts) > 1:
        spine_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        offset_pts = [(int(p[0] - cx + 50), int(p[1] - cy + 50)) for p in dragon_pts]
        pygame.draw.lines(spine_surf, (*star_glow, 80), False, offset_pts, 3)
        surface.blit(spine_surf, (cx - 50, cy - 50))
    
    # === 龙头 ===
    head_x, head_y = dragon_pts[0]
    head_wave = 18 * math.sin(frame * 0.12)
    
    # 头部光晕
    for i in range(3):
        r = 10 - i * 2
        alpha = 60 - i * 15
        head_glow = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(head_glow, (*star_glow, alpha), (r + 2, r + 2), r)
        surface.blit(head_glow, (int(head_x - r - 2), int(head_y - r - 2)))
    
    # 龙头主体
    head_pts = [
        (int(head_x), int(head_y - 10)),
        (int(head_x + 6), int(head_y)),
        (int(head_x + 4), int(head_y + 5)),
        (int(head_x - 4), int(head_y + 5)),
        (int(head_x - 6), int(head_y)),
    ]
    pygame.draw.polygon(surface, star_blue, head_pts)
    pygame.draw.polygon(surface, (255, 255, 255), head_pts, 1)
    
    # 龙眼
    pygame.draw.circle(surface, (255, 255, 255), (int(head_x - 2), int(head_y - 3)), 2)
    pygame.draw.circle(surface, (255, 255, 255), (int(head_x + 2), int(head_y - 3)), 2)
    pygame.draw.circle(surface, star_core, (int(head_x - 2), int(head_y - 3)), 1)
    pygame.draw.circle(surface, star_core, (int(head_x + 2), int(head_y - 3)), 1)
    
    # === 蓝色核心 ===
    pygame.draw.circle(surface, star_core, (cx, cy), 10)
    pygame.draw.circle(surface, star_blue, (cx, cy), 6)
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 3)


# ==================== 日耀烈焰 - 高精度版 ====================
def _draw_solar_zenith(surface, x, y, w, h, frame, style):
    """日耀烈焰 - 火焰剑阵 - 高精度版"""
    theme = get_zenith_theme(style)
    cx, cy = x + w // 2, y + h // 2
    
    solar_orange = theme["blade"]
    solar_glow = theme["glow"]
    solar_core = theme["core"]
    
    # === 烈焰光环 - 多层脉动 ===
    for layer in range(5):
        pulse = 4 * math.sin(frame * 0.15 + layer * 0.4)
        r = 48 - layer * 7 + pulse
        alpha = 45 - layer * 8
        if r > 0 and alpha > 0:
            fire_surf = pygame.Surface((int(r * 2 + 8), int(r * 2 + 8)), pygame.SRCALPHA)
            # 火焰渐变 - 从橙到红
            fire_color = _blend_color(solar_glow, (255, 50, 0), layer * 0.15)
            pygame.draw.circle(fire_surf, (*fire_color, alpha), (int(r + 4), int(r + 4)), int(r))
            surface.blit(fire_surf, (int(cx - r - 4), int(cy - r - 4)))
    
    # === 日耀射线 ===
    ray_count = 12
    for i in range(ray_count):
        ray_angle = frame * 2 + i * (360 / ray_count)
        ray_length = 42 + 8 * math.sin(frame * 0.2 + i * 0.5)
        ray_rad = math.radians(ray_angle)
        
        end_x = cx + math.cos(ray_rad) * ray_length
        end_y = cy + math.sin(ray_rad) * ray_length
        
        # 多层射线
        for j in range(3):
            ray_alpha = 100 - j * 30
            ray_width = 4 - j
            ray_color = _blend_color(solar_orange, (255, 255, 200), j * 0.3)
            
            ray_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.line(ray_surf, (*ray_color, ray_alpha),
                           (50, 50), (end_x - cx + 50, end_y - cy + 50), ray_width)
            surface.blit(ray_surf, (cx - 50, cy - 50))
    
    # === 日耀剑阵 - 放射状 ===
    sword_count = 8
    for i in range(sword_count):
        angle = frame * 2.5 + (360 / sword_count) * i
        orbit_r = 32 + 4 * math.sin(frame * 0.1 + i * 0.4)
        sx = cx + math.cos(math.radians(angle)) * orbit_r
        sy = cy + math.sin(math.radians(angle)) * orbit_r
        
        # 剑指向外（放射状）
        sword_angle = angle + 8 * math.sin(frame * 0.15 + i)
        
        sword_data = {"color": solar_orange, "length": 18}
        _draw_legendary_blade(surface, sx, sy, sword_angle, sword_data, frame, 1.0, 240)
        
        # 火焰粒子尾迹
        flame_count = 3
        for f in range(flame_count):
            flame_dist = orbit_r - 6 - f * 4
            fx = cx + math.cos(math.radians(angle)) * flame_dist
            fy = cy + math.sin(math.radians(angle)) * flame_dist
            
            flame_alpha = int(120 - f * 35)
            flame_size = 4 - f
            
            if flame_alpha > 0 and flame_size > 0:
                flame_surf = pygame.Surface((flame_size * 3, flame_size * 3), pygame.SRCALPHA)
                flame_color = _blend_color(solar_glow, (255, 255, 100), f * 0.3)
                pygame.draw.circle(flame_surf, (*flame_color, flame_alpha), 
                                 (flame_size * 1.5, flame_size * 1.5), flame_size)
                surface.blit(flame_surf, (int(fx - flame_size * 1.5), int(fy - flame_size * 1.5)))
    
    # === 烈焰核心 ===
    # 外圈火焰
    for i in range(4):
        r = 16 - i * 3
        alpha = 90 - i * 20
        core_color = _blend_color(solar_core, (255, 200, 50), i * 0.25)
        core_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(core_surf, (*core_color, alpha), (r + 2, r + 2), r)
        surface.blit(core_surf, (cx - r - 2, cy - r - 2))
    
    # 核心主体
    pygame.draw.circle(surface, solar_core, (cx, cy), 13)
    pygame.draw.circle(surface, solar_orange, (cx, cy), 9)
    pygame.draw.circle(surface, (255, 230, 150), (cx, cy), 5)
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 2)
    
    # 核心边框
    pygame.draw.circle(surface, (255, 255, 200), (cx, cy), 13, 1)
    
    # 日耀剑阵 - 放射状
    sword_count = 6
    for i in range(sword_count):
        angle = frame * 3 + (360 / sword_count) * i
        orbit_r = 28
        sx = cx + math.cos(math.radians(angle)) * orbit_r
        sy = cy + math.sin(math.radians(angle)) * orbit_r
        # 剑指向外
        _draw_detailed_sword(surface, sx, sy, angle, 16, theme["blade"], frame, 1.0)
    
    # 烈焰核心
    pygame.draw.circle(surface, theme["core"], (cx, cy), 12)
    pygame.draw.circle(surface, (255, 255, 200), (cx, cy), 6)


# ==================== 虚空终末 - 高精度版 ====================
def _draw_void_zenith(surface, x, y, w, h, frame, style):
    """虚空终末 - 暗黑虚空剑阵 - 高精度版"""
    theme = get_zenith_theme(style)
    cx, cy = x + w // 2, y + h // 2
    
    void_purple = theme["blade"]
    void_glow = theme["glow"]
    void_core = theme["core"]
    
    # === 虚空漩涡 - 吸收效果 ===
    vortex_layers = 6
    for layer in range(vortex_layers):
        vortex_angle = -frame * (3 - layer * 0.3) + layer * 30
        r = 50 - layer * 6 + 3 * math.sin(frame * 0.08 + layer)
        alpha = 50 - layer * 7
        
        if r > 0 and alpha > 0:
            vortex_surf = pygame.Surface((int(r * 2 + 10), int(r * 2 + 10)), pygame.SRCALPHA)
            
            # 漩涡线
            vortex_pts = []
            for i in range(30):
                seg_angle = vortex_angle + i * 12
                seg_r = r * (1 - i * 0.02)
                if seg_r > 0:
                    vx = r + 5 + math.cos(math.radians(seg_angle)) * seg_r
                    vy = r + 5 + math.sin(math.radians(seg_angle)) * seg_r
                    vortex_pts.append((int(vx), int(vy)))
            
            if len(vortex_pts) > 1:
                # 渐变紫色
                vortex_color = _blend_color(void_glow, (0, 0, 0), layer * 0.1)
                pygame.draw.lines(vortex_surf, (*vortex_color, alpha), False, vortex_pts, 2)
            
            surface.blit(vortex_surf, (int(cx - r - 5), int(cy - r - 5)))
    
    # === 虚空裂隙 ===
    rift_count = 5
    for i in range(rift_count):
        rift_angle = frame * 1.5 + i * (360 / rift_count)
        rift_length = 35 + 10 * math.sin(frame * 0.12 + i * 0.6)
        rift_rad = math.radians(rift_angle)
        
        start_r = 12
        sx = cx + math.cos(rift_rad) * start_r
        sy = cy + math.sin(rift_rad) * start_r
        ex = cx + math.cos(rift_rad) * rift_length
        ey = cy + math.sin(rift_rad) * rift_length
        
        # 多层裂隙
        for j in range(3):
            rift_alpha = 80 - j * 25
            rift_width = 5 - j
            rift_color = _blend_color(void_purple, (0, 0, 0), j * 0.3)
            
            rift_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.line(rift_surf, (*rift_color, rift_alpha),
                           (sx - cx + 50, sy - cy + 50), (ex - cx + 50, ey - cy + 50), rift_width)
            surface.blit(rift_surf, (cx - 50, cy - 50))
    
    # === 暗影剑阵 ===
    sword_count = 10
    for i in range(sword_count):
        angle = -frame * 1.8 + i * (360 / sword_count)
        orbit_wave = 6 * math.sin(frame * 0.08 + i * 0.5)
        orbit_r = 34 + orbit_wave
        sx = cx + math.cos(math.radians(angle)) * orbit_r
        sy = cy + math.sin(math.radians(angle)) * orbit_r
        
        # 剑指向中心（被吸入感）
        sword_angle = angle + 180 + 15 * math.sin(frame * 0.1 + i)
        
        # 暗淡的剑 - 带虚空效果
        sword_data = {"color": void_purple, "length": 15}
        _draw_legendary_blade(surface, sx, sy, sword_angle, sword_data, frame, 0.9, 200)
        
        # 暗影残留
        shadow_x = sx - math.cos(math.radians(angle)) * 5
        shadow_y = sy - math.sin(math.radians(angle)) * 5
        shadow_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (*void_core, 80), (5, 5), 4)
        surface.blit(shadow_surf, (int(shadow_x - 5), int(shadow_y - 5)))
    
    # === 虚空粒子 ===
    import random
    random.seed(int(frame * 0.25))
    for i in range(15):
        # 向内移动的粒子
        base_dist = random.uniform(25, 55)
        inward_progress = (frame * 0.02 + i * 0.1) % 1
        actual_dist = base_dist * (1 - inward_progress * 0.5)
        
        p_angle = random.uniform(0, 360)
        px = cx + math.cos(math.radians(p_angle)) * actual_dist
        py = cy + math.sin(math.radians(p_angle)) * actual_dist
        
        p_alpha = int(100 + 80 * inward_progress)
        p_size = 2 + int(3 * (1 - inward_progress))
        
        if p_alpha > 0 and p_size > 0:
            p_surf = pygame.Surface((p_size * 2 + 2, p_size * 2 + 2), pygame.SRCALPHA)
            p_color = _blend_color(void_glow, (0, 0, 0), inward_progress * 0.5)
            pygame.draw.circle(p_surf, (*p_color, p_alpha), (p_size + 1, p_size + 1), p_size)
            surface.blit(p_surf, (int(px - p_size - 1), int(py - p_size - 1)))
    
    # === 虚空核心 - 黑洞效果 ===
    # 事件视界
    for i in range(5):
        r = 18 - i * 3
        alpha = 60 - i * 10
        horizon_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        horizon_color = _blend_color(void_glow, (0, 0, 0), i * 0.2)
        pygame.draw.circle(horizon_surf, (*horizon_color, alpha), (r + 2, r + 2), r)
        surface.blit(horizon_surf, (cx - r - 2, cy - r - 2))
    
    # 黑洞核心
    pygame.draw.circle(surface, (0, 0, 0), (cx, cy), 14)
    pygame.draw.circle(surface, void_core, (cx, cy), 10)
    pygame.draw.circle(surface, void_purple, (cx, cy), 6)
    
    # 奇点闪烁
    singularity_alpha = int(180 + 75 * math.sin(frame * 0.25))
    singularity_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
    pygame.draw.circle(singularity_surf, (void_glow[0], void_glow[1], void_glow[2], singularity_alpha), (3, 3), 2)
    surface.blit(singularity_surf, (cx - 3, cy - 3))
    
    # 核心边框
    pygame.draw.circle(surface, void_glow, (cx, cy), 14, 1)
