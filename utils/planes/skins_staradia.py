# -*- coding: utf-8 -*-
"""
至尊机体涂装 - Staradia（辉耀天女·斯塔德）

灵感来源：泰拉瑞亚光之女皇 - 优雅的光之舞者，棱镜翅膀与虹光剑刃
主题配色：女皇虹 (255, 180, 220) + 月耀金 (255, 215, 120)
"""
import pygame
import math
import random

# Staradia 涂装样式列表
STARADIA_STYLES = [
    "default",           # 虹辉原典 - 六翼棱镜光羽+优雅舞姿
    "empress",           # 圣光女皇 - 纯白棱镜+金色光环(白昼形态)
    "prismatic",         # 棱镜幻蝶 - 全彩虹循环+蝶翼折射
    "twilight",          # 暮霽女神 - 薄暮紫+落日金渐变
    "aurora_weaver",     # 极光织女 - 极光绿+星辰蓝幕布
    "sakura",            # 樱花仙子 - 粉色樱花+浮游花瓣
    "dawn",              # 曙光破晓 - 朝霞橙+黎明粉希望
    "moonlight",         # 月华仙子 - 冷月银+柔光蓝樱吹雪
    "rainbow_fury",      # 虹怒天罚 - 暴怒彩虹+秒杀形态
    "ethereal",          # 梦蝶幻影 - 梦幻紫+透明蝶翼
    "solar_flare",       # 烈日凰舞 - 太阳金+凤凰火羽
    "void_empress",      # 虚渊暗皇 - 虚空紫+堕落女皇
]


def is_staradia_style(model_style):
    """检查是否为 Staradia 涂装"""
    return model_style in STARADIA_STYLES


def render_staradia_skin(s, cx, cy, model_style, size, t):
    """
    渲染 Staradia 机体涂装
    
    参数:
        s: Surface 对象
        cx, cy: 中心坐标
        model_style: 涂装样式
        size: 尺寸
        t: 时间参数
    """
    if not is_staradia_style(model_style):
        return None
    
    pulse = abs(math.sin(t * 2))
    
    renderers = {
        "default": _render_staradia_default,
        "empress": _render_staradia_empress,
        "prismatic": _render_staradia_prismatic,
        "twilight": _render_staradia_twilight,
        "aurora_weaver": _render_staradia_aurora,
        "sakura": _render_staradia_sakura,
        "dawn": _render_staradia_dawn,
        "moonlight": _render_staradia_moonlight,
        "rainbow_fury": _render_staradia_rainbow_fury,
        "ethereal": _render_staradia_ethereal,
        "solar_flare": _render_staradia_solar_flare,
        "void_empress": _render_staradia_void_empress,
    }
    
    renderer = renderers.get(model_style, _render_staradia_default)
    renderer(s, t, pulse)
    return s


# =============================================================================
#   通用绘制函数
# =============================================================================

def _draw_empress_body(s, cx, cy, t, base_color, accent_color, size=30):
    """绘制女皇优雅身姿 - 流线型身体+细腰设计"""
    # 优雅的8字形身姿
    # 上半身（胸部）
    chest_points = []
    for i in range(16):
        angle = i * 22.5 * 0.01745
        r = size * 0.5 + math.sin(t + i * 0.3) * 1.5
        if i < 8:  # 上半部分更宽
            r *= 1.1
        chest_points.append((int(cx + math.cos(angle) * r), int(cy - 8 + math.sin(angle) * r * 0.7)))
    pygame.draw.polygon(s, base_color, chest_points)
    pygame.draw.polygon(s, accent_color, chest_points, 1)
    
    # 细腰
    waist_y = cy + 2
    waist_w = int(size * 0.35)
    pygame.draw.ellipse(s, base_color, (cx - waist_w, waist_y - 3, waist_w * 2, 6))
    
    # 下半身（裙摆）
    skirt_points = []
    for i in range(12):
        angle = (i * 30 - 90) * 0.01745
        r = size * 0.6 + math.sin(t * 1.5 + i * 0.5) * 2
        skirt_points.append((int(cx + math.cos(angle) * r), int(cy + 15 + math.sin(angle + 1.57) * r * 0.5)))
    skirt_points.insert(0, (cx - waist_w, waist_y))
    skirt_points.append((cx + waist_w, waist_y))
    pygame.draw.polygon(s, base_color, skirt_points)
    pygame.draw.polygon(s, accent_color, skirt_points, 1)


def _draw_prismatic_wing(s, cx, cy, wing_angle, t, wing_index, colors, size=25):
    """绘制棱镜光羽 - 蝴蝶翅膀般的棱镜效果"""
    angle_rad = math.radians(wing_angle)
    
    # 翅膀基础位置
    base_dist = 12
    wx = cx + math.cos(angle_rad) * base_dist
    wy = cy + math.sin(angle_rad) * base_dist
    
    # 翅膀扇动
    flap = math.sin(t * 3 + wing_index * 0.5) * 0.15
    
    # 棱镜翅膀由多层组成
    for layer in range(3):
        layer_offset = layer * 0.3
        wing_points = []
        for i in range(8):
            seg_angle = angle_rad + (i - 3.5) * (0.4 + flap) - layer_offset
            dist = size * (1.2 - layer * 0.3) * (1 - abs(i - 3.5) / 5)
            wing_points.append((
                int(wx + math.cos(seg_angle) * dist),
                int(wy + math.sin(seg_angle) * dist)
            ))
        
        if len(wing_points) >= 3:
            # 彩虹渐变色
            color_idx = (wing_index + layer + int(t * 2)) % len(colors)
            wing_color = colors[color_idx]
            
            # 半透明绘制
            wing_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(wing_surf, (*wing_color, 120 - layer * 30), wing_points)
            pygame.draw.polygon(wing_surf, (*wing_color, 200), wing_points, 1)
            s.blit(wing_surf, (0, 0))
            
            # 棱镜光线
            if layer == 0:
                for i in range(0, len(wing_points) - 1, 2):
                    light_color = colors[(color_idx + i) % len(colors)]
                    pygame.draw.line(wing_surf, (*light_color, 100), 
                                   (int(wx), int(wy)), wing_points[i], 1)
                s.blit(wing_surf, (0, 0))


def _draw_rainbow_halo(s, cx, cy, radius, t, rainbow=True):
    """绘制彩虹光环 - 环绕女皇的神圣光晕"""
    halo_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    
    if rainbow:
        # 彩虹光环（7色）
        rainbow_colors = [
            (255, 100, 100),  # 红
            (255, 180, 100),  # 橙
            (255, 255, 100),  # 黄
            (100, 255, 100),  # 绿
            (100, 200, 255),  # 青
            (150, 100, 255),  # 蓝
            (255, 100, 255),  # 紫
        ]
        
        for i, color in enumerate(rainbow_colors):
            angle_offset = (t * 2 + i * 0.5) % (2 * math.pi)
            r = radius + i * 2 + abs(math.sin(t * 3 + i)) * 3
            
            # 绘制光环段
            for seg in range(36):
                seg_angle = seg * 10 * 0.01745 + angle_offset
                x = cx + math.cos(seg_angle) * r
                y = cy + math.sin(seg_angle) * r
                alpha = int(100 + 80 * abs(math.sin(t * 2 + seg * 0.1)))
                pygame.draw.circle(halo_surf, (*color, alpha), (int(x), int(y)), 2)
    else:
        # 单色光环
        for i in range(3):
            r = radius + i * 4 + abs(math.sin(t * 2)) * 2
            pygame.draw.circle(halo_surf, (255, 255, 255, 80 - i * 20), (cx, cy), int(r), 2)
    
    s.blit(halo_surf, (0, 0))


def _draw_floating_stars(s, cx, cy, t, count, color, radius_range):
    """绘制漂浮星辰 - 环绕的星光粒子"""
    star_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    
    for i in range(count):
        angle = (i * 360 / count + t * 20) * 0.01745
        orbit = radius_range[0] + (radius_range[1] - radius_range[0]) * (i / count)
        
        # 上下浮动
        float_offset = math.sin(t * 2 + i * 0.7) * 3
        
        sx = cx + math.cos(angle) * orbit
        sy = cy + math.sin(angle) * orbit + float_offset
        
        # 闪烁效果
        twinkle = abs(math.sin(t * 3 + i * 1.3))
        alpha = int(150 + 100 * twinkle)
        star_size = 2 + int(twinkle * 2)
        
        # 绘制星星（十字形）
        pygame.draw.circle(star_surf, (*color, alpha), (int(sx), int(sy)), star_size)
        # 十字光芒
        for dx, dy in [(star_size, 0), (-star_size, 0), (0, star_size), (0, -star_size)]:
            pygame.draw.line(star_surf, (*color, alpha // 2), 
                           (int(sx), int(sy)), 
                           (int(sx + dx), int(sy + dy)), 1)
    
    s.blit(star_surf, (0, 0))


def _draw_light_blade(s, cx, cy, angle, length, t, color):
    """绘制光剑 - 女皇的光之武器"""
    angle_rad = math.radians(angle)
    
    # 剑身光芒
    blade_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    
    # 剑柄
    hilt_x = cx + math.cos(angle_rad) * 8
    hilt_y = cy + math.sin(angle_rad) * 8
    pygame.draw.circle(s, color, (int(hilt_x), int(hilt_y)), 3)
    
    # 剑刃（渐变变细）
    for i in range(int(length)):
        progress = i / length
        blade_x = hilt_x + math.cos(angle_rad) * i
        blade_y = hilt_y + math.sin(angle_rad) * i
        blade_width = int((1 - progress) * 4) + 1
        alpha = int(200 - progress * 100)
        
        pygame.draw.circle(blade_surf, (*color, alpha), (int(blade_x), int(blade_y)), blade_width)
    
    # 剑尖闪光
    tip_x = hilt_x + math.cos(angle_rad) * length
    tip_y = hilt_y + math.sin(angle_rad) * length
    flash = abs(math.sin(t * 8))
    pygame.draw.circle(blade_surf, (*color, int(255 * flash)), (int(tip_x), int(tip_y)), 4)
    
    s.blit(blade_surf, (0, 0))


# =============================================================================
#   涂装渲染函数（12种）
# =============================================================================

def _render_staradia_default(s, t, pulse):
    """1. 虹辉原典 - 六翼棱镜光羽+优雅舞姿"""
    empress_pink = (255, 180, 220)
    moon_gold = (255, 215, 120)
    rainbow_colors = [
        (255, 100, 150), (255, 150, 100), (255, 230, 100),
        (150, 255, 150), (100, 200, 255), (180, 100, 255)
    ]
    
    # 超大彩虹光环背景（3层旋转）
    for layer in range(3):
        _draw_rainbow_halo(s, 60, 60, 48 - layer * 10, t + layer * 0.5, True)
    
    # 彩虹粒子旋涡（环绕身体）
    for i in range(24):
        angle = (i * 15 + t * 100) * 0.01745
        orbit = 32 + abs(math.sin(t * 2 + i * 0.3)) * 10
        px = 60 + math.cos(angle) * orbit
        py = 60 + math.sin(angle) * orbit
        color = rainbow_colors[i % 6]
        particle_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, (*color, 200), (int(px), int(py)), 4)
        s.blit(particle_surf, (0, 0))
    
    # 六翼棱镜光羽（3对，尺寸分级）
    wing_configs = [
        (65, 0, 30), (115, 1, 30),    # 上翼（最大）
        (35, 2, 26), (145, 3, 26),    # 中翼
        (5, 4, 22), (175, 5, 22),     # 下翼（最小）
    ]
    for angle, idx, size in wing_configs:
        _draw_prismatic_wing(s, 60, 60, angle, t, idx, rainbow_colors, size)
    
    # 女皇身姿
    _draw_empress_body(s, 60, 60, t, empress_pink, moon_gold, 28)
    
    # 华丽光冠（旋转光环）
    crown_y = 27
    for i in range(10):
        crown_angle = (i * 36 + t * 40) * 0.01745
        crown_dist = 14 if i % 2 == 0 else 11
        crown_x = 60 + math.cos(crown_angle) * crown_dist
        crown_y_pos = crown_y + math.sin(crown_angle) * 7
        color = rainbow_colors[i % 6]
        pygame.draw.circle(s, color, (int(crown_x), int(crown_y_pos)), 5)
        pygame.draw.circle(s, (255, 255, 255), (int(crown_x), int(crown_y_pos)), 2)
    
    # 超大核心宝石（多层发光）
    core_pulse = abs(math.sin(t * 3))
    for i in range(5):
        color = rainbow_colors[(int(t * 3) + i) % 6]
        pygame.draw.circle(s, color, (60, 60), int(16 - i * 3 + core_pulse * 5))
    pygame.draw.circle(s, (255, 255, 255), (60, 60), 6)
    
    # 多层环绕星辰
    for orbit_idx, orbit in enumerate([(30, 36), (40, 46), (50, 56)]):
        star_count = 8 - orbit_idx * 2
        _draw_floating_stars(s, 60, 60, t + orbit_idx * 0.3, star_count, rainbow_colors[orbit_idx * 2], orbit)


def _render_staradia_empress(s, t, pulse):
    """2. 圣光女皇 - 纯白棱镜+金色光环(白昼形态)"""
    holy_white = (255, 255, 255)
    divine_gold = (255, 230, 180)
    light_gold = (255, 250, 220)
    wing_colors = [(255, 250, 250), (255, 245, 220), (255, 255, 240)]
    
    # 整个屏幕的神圣白光（白昼太阳效果）
    white_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.rect(white_surf, (255, 255, 240, 40), (0, 0, 120, 120))
    s.blit(white_surf, (0, 0))
    
    # 超强神圣光晕（白昼太阳）
    for i in range(10):
        glow_r = 65 - i * 5 + int(pulse * 10)
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        alpha = 90 - i * 7 + int(pulse * 35)
        pygame.draw.circle(glow_surf, (*divine_gold, alpha), (60, 60), glow_r)
        s.blit(glow_surf, (0, 0))
    
    # 神圣十字光芒（白昼形态）+ 对角线 = 8条光线
    cross_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    cross_len = 45 + int(pulse * 15)
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        angle_rad = math.radians(angle + t * 25)
        width = 6 if angle % 90 == 0 else 4
        # 多层光线
        for j in range(4):
            length = cross_len - j * 7
            ex = 60 + math.cos(angle_rad) * length
            ey = 60 + math.sin(angle_rad) * length
            alpha = 220 - j * 45
            pygame.draw.line(cross_surf, (*light_gold, alpha), (60, 60), (int(ex), int(ey)), width - j)
        # 光线末端光球
        pygame.draw.circle(cross_surf, holy_white, (int(ex), int(ey)), 6)
        pygame.draw.circle(cross_surf, divine_gold, (int(ex), int(ey)), 3)
    s.blit(cross_surf, (0, 0))
    
    # 神圣光剑阵（环绕旋转）
    for i in range(16):
        blade_angle = i * 22.5 + t * 50
        blade_dist = 38 + abs(math.sin(t * 2 + i * 0.5)) * 5
        blade_x = 60 + math.cos(math.radians(blade_angle)) * blade_dist
        blade_y = 60 + math.sin(math.radians(blade_angle)) * blade_dist
        _draw_light_blade(s, blade_x, blade_y, blade_angle + 90, 15, t, divine_gold)
    
    # 六翼（纯白棱镜翅膀，更大）
    for angle, idx in [(60, 0), (30, 1), (120, 2), (150, 3), (0, 4), (180, 5)]:
        _draw_prismatic_wing(s, 60, 60, angle, t, idx, wing_colors, 28)
    
    # 女皇身姿（纯白）
    _draw_empress_body(s, 60, 60, t, holy_white, divine_gold, 32)
    
    # 黄金头冠（更华丽，3层）
    for layer in range(3):
        crown_count = 9 - layer * 2
        crown_r = 12 + layer * 3
        for i in range(crown_count):
            crown_angle = (-80 + i * (160 / (crown_count - 1))) * 0.01745
            crown_x = 60 + math.cos(crown_angle) * crown_r
            crown_y = 24 + layer * 2 + math.sin(crown_angle) * (crown_r - 4)
            size = 5 - layer
            pygame.draw.circle(s, divine_gold, (int(crown_x), int(crown_y)), size)
            pygame.draw.circle(s, light_gold, (int(crown_x), int(crown_y)), size - 2)
    pygame.draw.circle(s, light_gold, (60, 24), 6)
    pygame.draw.circle(s, holy_white, (60, 24), 3)
    
    # 神圣核心（超大）
    core_r = int(14 + pulse * 6)
    pygame.draw.circle(s, light_gold, (60, 60), core_r)
    pygame.draw.circle(s, holy_white, (60, 60), core_r - 5)
    pygame.draw.circle(s, divine_gold, (60, 60), 6)
    pygame.draw.circle(s, (255, 255, 255), (60, 60), 3)
    
    # 六翼（纯白棱镜翅膀）
    for angle, idx in [(60, 0), (30, 1), (120, 2), (150, 3), (0, 4), (180, 5)]:
        _draw_prismatic_wing(s, 60, 60, angle, t, idx, wing_colors, 24)
    
    # 女皇身姿（纯白）
    _draw_empress_body(s, 60, 60, t, holy_white, divine_gold, 30)
    
    # 黄金头冠（更华丽）
    crown_points = []
    for i in range(7):
        crown_angle = (-75 + i * 25) * 0.01745
        crown_r = 10 if i % 2 == 0 else 6
        crown_x = 60 + math.cos(crown_angle) * crown_r
        crown_y = 28 + math.sin(crown_angle) * crown_r
        crown_points.append((int(crown_x), int(crown_y)))
    pygame.draw.polygon(s, divine_gold, crown_points)
    pygame.draw.circle(s, light_gold, (60, 26), 4)
    
    # 神圣核心
    pygame.draw.circle(s, light_gold, (60, 60), int(10 + pulse * 4))
    pygame.draw.circle(s, holy_white, (60, 60), 5)


def _render_staradia_prismatic(s, t, pulse):
    """3. 棱镜幻蝶 - 全彩虹循环+蝶翼折射"""
    # 动态彩虹色（HSV循环）
    def get_rainbow_color(offset):
        h = (t * 0.5 + offset) % 3
        if h < 1:
            return (int(255 * (1 - h) + 100 * h), int(255 * h), 150)
        elif h < 2:
            return (100, int(255 * (2 - h) + 100 * (h - 1)), int(255 * (h - 1)))
        else:
            return (int(255 * (h - 2)), 100, int(255 * (3 - h) + 100 * (h - 2)))
    
    # 全屏彩虹光谱背景（水平渐变）
    spectrum_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for y in range(0, 120, 2):
        color = get_rainbow_color(y * 0.025)
        pygame.draw.rect(spectrum_surf, (*color, 50), (0, y, 120, 2))
    s.blit(spectrum_surf, (0, 0))
    
    # 多层彩虹旋涡（3个反向旋转）
    for layer in range(3):
        spiral_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        direction = 1 if layer % 2 == 0 else -1
        for i in range(70):
            angle = (i * 5.14 + t * 80 * direction + layer * 120) * 0.01745
            dist = i * 0.9
            sx = 60 + math.cos(angle) * dist
            sy = 60 + math.sin(angle) * dist
            color = get_rainbow_color(i * 0.06 + layer * 0.4)
            size = 5 - layer
            pygame.draw.circle(spiral_surf, (*color, 140 - layer * 35), (int(sx), int(sy)), size)
        s.blit(spiral_surf, (0, 0))
    
    # 彩虹光环爆发（多层）
    for i in range(10):
        ring_color = get_rainbow_color(i * 0.25)
        ring_r = 22 + i * 4 + int(pulse * 6)
        ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (*ring_color, 120), (60, 60), ring_r, 3)
        s.blit(ring_surf, (0, 0))
    
    # 蝴蝶形翅膀（更大、更华丽）
    butterfly_colors = [get_rainbow_color(i * 0.3) for i in range(6)]
    for angle, idx in [(50, 0), (130, 1), (20, 2), (160, 3), (350, 4), (190, 5)]:
        _draw_prismatic_wing(s, 60, 60, angle, t, idx, butterfly_colors, 32)
    
    # 女皇身姿（彩虹渐变）
    body_color = get_rainbow_color(0)
    accent_color = get_rainbow_color(1)
    _draw_empress_body(s, 60, 60, t, body_color, accent_color, 28)
    
    # 彩虹核心（多层旋转）
    for i in range(5):
        core_color = get_rainbow_color(i * 0.4 + t * 0.5)
        pygame.draw.circle(s, core_color, (60, 60), int(16 - i * 3 + pulse * 3))
    pygame.draw.circle(s, (255, 255, 255), (60, 60), 5)
    
    # 彩虹星尘暴（大量粒子）
    for i in range(20):
        star_color = get_rainbow_color(i * 0.15)
        angle = (i * 18 + t * 120) * 0.01745
        orbit = 35 + abs(math.sin(t * 3 + i * 0.4)) * 12
        sx = 60 + math.cos(angle) * orbit
        sy = 60 + math.sin(angle) * orbit
        pygame.draw.circle(s, star_color, (int(sx), int(sy)), 4)
        pygame.draw.circle(s, (255, 255, 255), (int(sx), int(sy)), 2)
    
    # 蝴蝶形翅膀（更大、更华丽）
    butterfly_colors = [get_rainbow_color(i * 0.3) for i in range(6)]
    for angle, idx in [(50, 0), (130, 1), (20, 2), (160, 3), (350, 4), (190, 5)]:
        _draw_prismatic_wing(s, 60, 60, angle, t, idx, butterfly_colors, 28)
    
    # 女皇身姿（彩虹渐变）
    body_color = get_rainbow_color(0)
    accent_color = get_rainbow_color(1)
    _draw_empress_body(s, 60, 60, t, body_color, accent_color, 26)
    
    # 彩虹核心
    for i in range(3):
        core_color = get_rainbow_color(i * 0.5)
        pygame.draw.circle(s, core_color, (60, 60), int(10 - i * 3 + pulse * 2))
    
    # 彩虹星尘
    for i in range(12):
        star_color = get_rainbow_color(i * 0.2)
        _draw_floating_stars(s, 60, 60, t + i * 0.5, 1, star_color, (30 + i * 2, 32 + i * 2))


def _render_staradia_twilight(s, t, pulse):
    """4. 暮霭女神 - 薄暮紫+落日金渐变"""
    dusk_purple = (180, 100, 220)
    sunset_gold = (255, 200, 100)
    twilight_pink = (255, 150, 180)
    sky_gradient = [(200, 120, 200), (220, 150, 180), (255, 180, 140)]
    
    # 日落渐变背景
    gradient_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(40):
        y = i * 3
        progress = i / 40
        if progress < 0.5:
            col = dusk_purple
        else:
            blend = (progress - 0.5) * 2
            col = (
                int(dusk_purple[0] + (sunset_gold[0] - dusk_purple[0]) * blend),
                int(dusk_purple[1] + (sunset_gold[1] - dusk_purple[1]) * blend),
                int(dusk_purple[2] + (sunset_gold[2] - dusk_purple[2]) * blend)
            )
        pygame.draw.rect(gradient_surf, (*col, 40), (0, y, 120, 3))
    s.blit(gradient_surf, (0, 0))
    
    # 落日光晕
    for i in range(4):
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*sunset_gold, 50 - i * 10), (60, 60), 45 - i * 8)
        s.blit(glow_surf, (0, 0))
    
    # 余晖光羽
    wing_colors = [dusk_purple, twilight_pink, sunset_gold]
    for angle, idx in [(60, 0), (30, 1), (120, 2), (150, 3), (5, 4), (175, 5)]:
        _draw_prismatic_wing(s, 60, 60, angle, t, idx, wing_colors, 23)
    
    # 女皇剪影
    _draw_empress_body(s, 60, 60, t, dusk_purple, sunset_gold, 28)
    
    # 薄暮皇冠
    for i in range(5):
        crown_angle = (-60 + i * 30) * 0.01745
        crown_col = sunset_gold if i % 2 == 0 else twilight_pink
        crown_x = 60 + math.cos(crown_angle) * 9
        crown_y = 29 + math.sin(crown_angle) * 5
        pygame.draw.circle(s, crown_col, (int(crown_x), int(crown_y)), 4)
    
    # 渐变核心
    pygame.draw.circle(s, sunset_gold, (60, 60), int(9 + pulse * 3))
    pygame.draw.circle(s, twilight_pink, (60, 60), 5)
    
    # 黄昏星辰
    _draw_floating_stars(s, 60, 60, t, 6, twilight_pink, (38, 48))


def _render_staradia_aurora(s, t, pulse):
    """5. 极光织女 - 极光绿+星辰蓝幕布"""
    aurora_green = (100, 255, 220)
    aurora_blue = (100, 255, 150)
    star_blue = (120, 230, 200)
    arctic_cyan = (150, 255, 240)
    
    # 极光波浪背景
    aurora_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for wave in range(5):
        points = []
        for i in range(25):
            x = i * 5
            y = 30 + wave * 12 + math.sin(t * 2 + i * 0.3 + wave * 0.5) * 8
            points.append((x, int(y)))
        if len(points) > 1:
            pygame.draw.lines(aurora_surf, (*aurora_green, 80 - wave * 15), False, points, 3)
    s.blit(aurora_surf, (0, 0))
    
    # 极地光晕
    for i in range(3):
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*star_blue, 45 - i * 12), (60, 60), 48 - i * 10)
        s.blit(glow_surf, (0, 0))
    
    # 极光翅膀（流动效果，左右对称布局）
    wing_colors = [aurora_green, aurora_blue, arctic_cyan]
    for angle, idx, size in [(65, 0, 28), (115, 1, 28), (35, 2, 24), (145, 3, 24), (5, 4, 20), (175, 5, 20)]:
        _draw_prismatic_wing(s, 60, 60, angle, t, idx, wing_colors, size)
    
    # 女皇身姿
    _draw_empress_body(s, 60, 60, t, aurora_green, star_blue, 27)
    
    # 冰晶皇冠
    for i in range(6):
        crown_angle = (-65 + i * 26) * 0.01745
        crown_x = 60 + math.cos(crown_angle) * 10
        crown_y = 28 + math.sin(crown_angle) * 6
        # 冰晶形状
        pygame.draw.polygon(s, arctic_cyan, [
            (int(crown_x), int(crown_y - 4)),
            (int(crown_x + 3), int(crown_y)),
            (int(crown_x), int(crown_y + 4)),
            (int(crown_x - 3), int(crown_y))
        ])
    
    # 极光核心
    pygame.draw.circle(s, star_blue, (60, 60), int(10 + pulse * 3))
    pygame.draw.circle(s, arctic_cyan, (60, 60), 5)
    pygame.draw.circle(s, (255, 255, 255), (60, 60), 2)
    
    # 北极星辰
    _draw_floating_stars(s, 60, 60, t, 10, arctic_cyan, (35, 50))


def _render_staradia_sakura(s, t, pulse):
    """樱花仙子 - 粉色樱花飘落+温柔光辉"""
    # 樱花粉系配色
    sakura_pink = (255, 183, 197)
    sakura_deep = (255, 130, 160)
    petal_white = (255, 240, 245)
    branch_brown = (139, 90, 70)
    gold_center = (255, 220, 150)
    
    cx, cy = 60, 60
    
    # === 淡粉背景光晕 ===
    for r in range(50, 15, -10):
        alpha = 25 + (50 - r) // 2
        glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*sakura_pink, alpha), (cx, cy), r)
        s.blit(glow, (0, 0))
    
    # === 飘落的樱花花瓣 ===
    for i in range(12):
        rng = random.Random(i * 31)
        # 花瓣轨迹 - 缓慢飘落+左右摇曳
        base_x = rng.randint(15, 105)
        fall_speed = 0.3 + rng.random() * 0.2
        sway = math.sin(t * 2 + i * 0.8) * 8
        
        petal_y = ((t * 20 * fall_speed + i * 30) % 120)
        petal_x = base_x + sway
        
        # 花瓣旋转角度
        rot = t * 2 + i * 0.5
        
        # 绘制樱花花瓣（5瓣花形）
        petal_size = 4 + rng.random() * 2
        petal_color = sakura_pink if i % 2 else petal_white
        
        # 简化的花瓣形状
        points = []
        for j in range(5):
            angle = rot + j * 72 * 0.01745
            r_size = petal_size if j % 2 == 0 else petal_size * 0.5
            points.append((
                int(petal_x + math.cos(angle) * r_size),
                int(petal_y + math.sin(angle) * r_size)
            ))
        if len(points) >= 3:
            pygame.draw.polygon(s, (*petal_color, 180), points)
    
    # === 樱花树枝装饰 ===
    # 左上角树枝
    pygame.draw.line(s, branch_brown, (10, 10), (35, 35), 2)
    pygame.draw.line(s, branch_brown, (25, 15), (35, 30), 1)
    # 右上角树枝
    pygame.draw.line(s, branch_brown, (110, 10), (85, 35), 2)
    pygame.draw.line(s, branch_brown, (95, 15), (85, 30), 1)
    
    # 树枝上的小花
    for bx, by in [(32, 32), (88, 32), (20, 18), (100, 18)]:
        pygame.draw.circle(s, sakura_pink, (bx, by), 4)
        pygame.draw.circle(s, petal_white, (bx, by), 2)
        pygame.draw.circle(s, gold_center, (bx, by), 1)
    
    # === 主体 - 樱花精灵翼膀（放大+辉光） ===
    wing_surf = pygame.Surface((120, 120), pygame.SRCALPHA)

    # 背景翼光晕，先打底再叠加形状
    for r, alpha in [(42, 55), (32, 70)]:
        pygame.draw.circle(wing_surf, (*sakura_pink, alpha), (cx - 22, cy), r)
        pygame.draw.circle(wing_surf, (*sakura_pink, alpha), (cx + 22, cy), r)

    # 左翼 - 大号花瓣翼
    left_wing = [
        (cx - 12, cy - 8),
        (cx - 45, cy - 25),
        (cx - 65, cy + 0),
        (cx - 48, cy + 24),
        (cx - 20, cy + 14),
    ]
    pygame.draw.polygon(wing_surf, sakura_pink, left_wing)
    pygame.draw.polygon(wing_surf, sakura_deep, left_wing, 2)

    # 右翼 - 对称花瓣翼
    right_wing = [
        (cx + 12, cy - 8),
        (cx + 45, cy - 25),
        (cx + 65, cy + 0),
        (cx + 48, cy + 24),
        (cx + 20, cy + 14),
    ]
    pygame.draw.polygon(wing_surf, sakura_pink, right_wing)
    pygame.draw.polygon(wing_surf, sakura_deep, right_wing, 2)

    # 翼膀亮斑与渐变
    for wx, wy, radius, alpha in [(-45, -10, 8, 130), (-55, 8, 10, 100), (45, -10, 8, 130), (55, 8, 10, 100)]:
        pygame.draw.circle(wing_surf, (*petal_white, alpha), (cx + wx, cy + wy), radius)

    s.blit(wing_surf, (0, 0))
    
    # === 精灵身体 ===
    # 身体椭圆
    body_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.ellipse(body_surf, sakura_deep, (cx - 10, cy - 20, 20, 35))
    pygame.draw.ellipse(body_surf, sakura_pink, (cx - 8, cy - 18, 16, 30))
    s.blit(body_surf, (0, 0))
    
    # 头部
    pygame.draw.circle(s, petal_white, (cx, cy - 22), 8)
    pygame.draw.circle(s, sakura_pink, (cx, cy - 22), 6)
    
    # 樱花发饰
    pygame.draw.circle(s, sakura_deep, (cx - 5, cy - 28), 3)
    pygame.draw.circle(s, sakura_deep, (cx + 5, cy - 28), 3)
    pygame.draw.circle(s, gold_center, (cx - 5, cy - 28), 1)
    pygame.draw.circle(s, gold_center, (cx + 5, cy - 28), 1)
    
    # === 能量核心 - 樱花形状 ===
    core_size = 10 + pulse * 3
    # 绘制5瓣樱花核心
    for i in range(5):
        petal_angle = (i * 72 - 90) * 0.01745 + t * 0.5
        px = cx + math.cos(petal_angle) * core_size * 0.7
        py = cy + math.sin(petal_angle) * core_size * 0.7
        pygame.draw.circle(s, sakura_pink, (int(px), int(py)), int(core_size * 0.4))
    pygame.draw.circle(s, gold_center, (cx, cy), int(core_size * 0.3))
    pygame.draw.circle(s, petal_white, (cx, cy), int(core_size * 0.15))
    
    # === 飘散的光点 ===
    for i in range(6):
        sparkle_angle = (i * 60 + t * 30) * 0.01745
        sparkle_dist = 35 + math.sin(t * 2 + i) * 5
        sx = cx + math.cos(sparkle_angle) * sparkle_dist
        sy = cy + math.sin(sparkle_angle) * sparkle_dist
        sparkle_alpha = int(150 + 50 * math.sin(t * 4 + i * 1.2))
        pygame.draw.circle(s, (*petal_white, sparkle_alpha), (int(sx), int(sy)), 2)


def _render_staradia_dawn(s, t, pulse):
    """7. 曙光破晓 - 朝霞橙+黎明粉希望"""
    dawn_orange = (255, 180, 100)
    dawn_pink = (255, 150, 180)
    hope_yellow = (255, 230, 150)
    sunrise_gold = (255, 190, 140)
    
    # 曙光放射背景
    ray_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(12):
        angle = (i * 30 + t * 15) * 0.01745
        for j in range(3):
            ray_len = 25 + j * 10 + abs(math.sin(t * 2 + i * 0.5)) * 8
            ex = 60 + math.cos(angle) * ray_len
            ey = 60 + math.sin(angle) * ray_len
            alpha = 80 - j * 25
            pygame.draw.line(ray_surf, (*hope_yellow, alpha), (60, 60), (int(ex), int(ey)), 4 - j)
    s.blit(ray_surf, (0, 0))
    
    # 朝霞光晕
    for i in range(4):
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        glow_color = dawn_orange if i % 2 == 0 else dawn_pink
        pygame.draw.circle(glow_surf, (*glow_color, 50 - i * 10), (60, 60), 48 - i * 9)
        s.blit(glow_surf, (0, 0))
    
    # 希望之翼
    wing_colors = [dawn_orange, dawn_pink, hope_yellow]
    for angle, idx in [(58, 0), (122, 1), (28, 2), (152, 3), (358, 4), (182, 5)]:
        _draw_prismatic_wing(s, 60, 60, angle, t, idx, wing_colors, 25)
    
    # 女皇身姿
    _draw_empress_body(s, 60, 60, t, dawn_orange, hope_yellow, 29)
    
    # 黎明之冠（太阳形）
    crown_r = 12
    for i in range(8):
        ray_angle = i * 45 * 0.01745
        # 长短交替的光芒
        ray_length = 8 if i % 2 == 0 else 5
        ray_x = 60 + math.cos(ray_angle) * (crown_r + ray_length)
        ray_y = 27 + math.sin(ray_angle) * (crown_r + ray_length)
        pygame.draw.line(s, sunrise_gold, (60, 27), (int(ray_x), int(ray_y)), 3)
    pygame.draw.circle(s, hope_yellow, (60, 27), 6)
    pygame.draw.circle(s, (255, 255, 240), (60, 27), 3)
    
    # 破晓核心（脉冲光芒）
    core_pulse = abs(math.sin(t * 4))
    pygame.draw.circle(s, hope_yellow, (60, 60), int(11 + core_pulse * 4))
    pygame.draw.circle(s, (255, 255, 200), (60, 60), int(6 + core_pulse * 2))
    pygame.draw.circle(s, (255, 255, 255), (60, 60), 3)
    
    # 希望星光
    _draw_floating_stars(s, 60, 60, t, 8, hope_yellow, (36, 46))
    
    # 驱散黑暗的光粒子
    for i in range(6):
        particle_phase = (t * 1.2 + i * 0.5) % 1.5
        particle_angle = i * 60 * 0.01745
        particle_dist = 25 + particle_phase * 25
        px = 60 + math.cos(particle_angle) * particle_dist
        py = 60 + math.sin(particle_angle) * particle_dist
        particle_alpha = int(200 * (1 - particle_phase / 1.5))
        particle_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, (*sunrise_gold, particle_alpha), (int(px), int(py)), 3)
        s.blit(particle_surf, (0, 0))


def _render_staradia_moonlight(s, t, pulse):
    """8. 月华仙子 - 冷月银+柔光蓝樱吹雪"""
    moon_silver = (230, 240, 255)
    soft_blue = (200, 220, 255)
    sakura_pink = (255, 220, 240)
    moonlight_cyan = (220, 235, 255)
    
    # 月光洒落背景
    moonbeam_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(8):
        beam_x = 20 + i * 12
        beam_alpha = int(40 + 30 * abs(math.sin(t + i * 0.5)))
        pygame.draw.rect(moonbeam_surf, (*soft_blue, beam_alpha), (beam_x, 0, 6, 120))
    s.blit(moonbeam_surf, (0, 0))
    
    # 月华光晕
    for i in range(3):
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*moonlight_cyan, 35 - i * 10), (60, 60), 52 - i * 12)
        s.blit(glow_surf, (0, 0))
    
    # 月光翅膀
    wing_colors = [moon_silver, soft_blue, moonlight_cyan]
    for angle, idx in [(62, 0), (118, 1), (32, 2), (148, 3), (3, 4), (177, 5)]:
        _draw_prismatic_wing(s, 60, 60, angle, t, idx, wing_colors, 23)
    
    # 女皇身姿
    _draw_empress_body(s, 60, 60, t, moon_silver, soft_blue, 27)
    
    # 月牙皇冠
    pygame.draw.arc(s, moon_silver, (50, 20, 20, 16), 0, math.pi, 3)
    pygame.draw.arc(s, soft_blue, (50, 20, 20, 16), 0, math.pi, 1)
    # 月牙上的星星
    for i in range(3):
        star_x = 55 + i * 5
        star_y = 24
        pygame.draw.circle(s, (255, 255, 255), (star_x, star_y), 2)
    
    # 月华核心
    pygame.draw.circle(s, soft_blue, (60, 60), int(9 + pulse * 2))
    pygame.draw.circle(s, moon_silver, (60, 60), 5)
    pygame.draw.circle(s, (255, 255, 255), (60, 60), 2)
    
    # 樱花飘落（月下樱吹雪）
    for i in range(12):
        sakura_phase = (t * 0.5 + i * 0.3) % 2
        sakura_x = 25 + (i * 17) % 70 + math.sin(t * 2 + i) * 8
        sakura_y = -10 + sakura_phase * 70
        sakura_alpha = int(180 * (1 - sakura_phase / 2))
        
        # 樱花瓣（五瓣）
        sakura_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        for petal in range(5):
            petal_angle = petal * 72 * 0.01745 + t + i
            petal_x = sakura_x + math.cos(petal_angle) * 3
            petal_y = sakura_y + math.sin(petal_angle) * 3
            pygame.draw.circle(sakura_surf, (*sakura_pink, sakura_alpha), (int(petal_x), int(petal_y)), 2)
        s.blit(sakura_surf, (0, 0))
    
    # 月光星尘
    _draw_floating_stars(s, 60, 60, t, 6, moonlight_cyan, (38, 48))


def _render_staradia_rainbow_fury(s, t, pulse):
    """9. 虹怒天罚 - 暴怒彩虹+秒杀形态"""
    fury_red = (255, 80, 120)
    burst_gold = (255, 200, 50)
    rage_orange = (255, 150, 100)
    wrath_colors = [
        (255, 50, 80), (255, 120, 60), (255, 200, 80),
        (200, 255, 100), (100, 200, 255), (180, 80, 255)
    ]
    
    # 暴怒能量爆发（剧烈震动）
    shake_x = math.sin(t * 18) * 5
    shake_y = math.cos(t * 15) * 5
    
    # 全屏闪烁红光（愤怒氛围）
    flash = abs(math.sin(t * 10))
    flash_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.rect(flash_surf, (255, 50, 50, int(100 * flash)), (0, 0, 120, 120))
    s.blit(flash_surf, (0, 0))
    
    # 超强愤怒光环（多重爆裂，震荡效果）
    burst_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(10):
        burst_r = 25 + i * 6 + int(pulse * 15)
        burst_alpha = 150 - i * 12
        ring_width = 5 if i % 2 == 0 else 3
        pygame.draw.circle(burst_surf, (*fury_red, burst_alpha), 
                          (int(60 + shake_x), int(60 + shake_y)), burst_r, ring_width)
    s.blit(burst_surf, (0, 0))
    
    # 虹怒光剑阵（双层旋转攻击）
    blade_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for layer in range(2):
        for i in range(12):
            blade_angle = i * 30 + t * (150 if layer == 0 else -120)
            blade_color = wrath_colors[i % len(wrath_colors)]
            blade_length = 28 if layer == 0 else 22
            _draw_light_blade(blade_surf, 60 + shake_x, 60 + shake_y, blade_angle, blade_length, t, blade_color)
    s.blit(blade_surf, (0, 0))
    
    # 能量冲击波（扩散）
    for i in range(3):
        wave_phase = (t * 2 + i * 0.7) % 1.5
        wave_r = int(20 + wave_phase * 40)
        wave_alpha = int(180 * (1 - wave_phase / 1.5))
        wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(wave_surf, (*rage_orange, wave_alpha), 
                          (int(60 + shake_x), int(60 + shake_y)), wave_r, 4)
        s.blit(wave_surf, (0, 0))
    
    # 愤怒之翼（张开威慑）
    wing_colors = [fury_red, rage_orange, burst_gold]
    for angle, idx in [(50, 0), (130, 1), (20, 2), (160, 3), (350, 4), (190, 5)]:
        _draw_prismatic_wing(s, 60 + shake_x, 60 + shake_y, angle, t, idx, wing_colors, 26)
    
    # 女皇身姿（战斗形态）
    _draw_empress_body(s, 60 + shake_x, 60 + shake_y, t, fury_red, burst_gold, 30)
    
    # 怒火之冠
    crown_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(8):
        flame_angle = (-80 + i * 20) * 0.01745
        flame_height = 8 + abs(math.sin(t * 5 + i)) * 6
        flame_x = 60 + math.cos(flame_angle) * 12
        flame_y = 25 - flame_height
        # 火焰形状
        flame_points = [
            (int(flame_x), int(flame_y)),
            (int(flame_x + 3), int(flame_y + flame_height * 0.6)),
            (int(flame_x), int(flame_y + flame_height)),
            (int(flame_x - 3), int(flame_y + flame_height * 0.6))
        ]
        pygame.draw.polygon(crown_surf, (*fury_red, 200), flame_points)
    s.blit(crown_surf, (0, 0))
    
    # 爆裂核心
    core_r = int(12 + pulse * 6)
    pygame.draw.circle(s, burst_gold, (int(60 + shake_x), int(60 + shake_y)), core_r)
    pygame.draw.circle(s, fury_red, (int(60 + shake_x), int(60 + shake_y)), core_r - 4)
    pygame.draw.circle(s, (255, 255, 200), (int(60 + shake_x), int(60 + shake_y)), 4)
    
    # 怒火粒子（快速旋转）
    for i in range(12):
        particle_angle = (i * 30 + t * 200) * 0.01745
        particle_dist = 40
        px = 60 + math.cos(particle_angle) * particle_dist
        py = 60 + math.sin(particle_angle) * particle_dist
        particle_color = wrath_colors[i % len(wrath_colors)]
        pygame.draw.circle(s, particle_color, (int(px), int(py)), 3)


def _render_staradia_ethereal(s, t, pulse):
    """10. 梦蝶幻影 - 梦幻紫+透明蝶翼"""
    dream_purple = (220, 180, 255)
    ethereal_pink = (255, 200, 230)
    fantasy_lavender = (215, 175, 250)
    bubble_colors = [(235, 200, 255), (255, 220, 245), (200, 180, 255)]
    
    # 梦境雾气
    mist_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(8):
        mist_x = 20 + i * 12 + math.sin(t * 0.5 + i) * 15
        mist_y = 30 + math.cos(t * 0.3 + i) * 20
        pygame.draw.ellipse(mist_surf, (*dream_purple, 30), 
                           (int(mist_x - 15), int(mist_y - 10), 30, 20))
    s.blit(mist_surf, (0, 0))
    
    # 梦幻光晕
    for i in range(3):
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*fantasy_lavender, 40 - i * 10), (60, 60), 50 - i * 12)
        s.blit(glow_surf, (0, 0))
    
    # 透明蝶翼（半透明层叠）
    for angle, idx in [(55, 0), (125, 1), (25, 2), (155, 3), (355, 4), (185, 5)]:
        wing_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 绘制蝴蝶翼（更透明）
        wing_color = bubble_colors[idx % 3]
        _draw_prismatic_wing(wing_surf, 60, 60, angle, t, idx, [wing_color], 26)
        # 添加透明度
        wing_surf.set_alpha(150)
        s.blit(wing_surf, (0, 0))
    
    # 女皇身姿（半透明）
    body_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    _draw_empress_body(body_surf, 60, 60, t, dream_purple, ethereal_pink, 27)
    body_surf.set_alpha(200)
    s.blit(body_surf, (0, 0))
    
    # 梦蝶之冠
    for i in range(5):
        crown_angle = (-60 + i * 30) * 0.01745
        crown_x = 60 + math.cos(crown_angle) * 10
        crown_y = 28 + math.sin(crown_angle) * 6 + math.sin(t * 2 + i) * 2
        # 蝴蝶形状
        pygame.draw.circle(s, ethereal_pink, (int(crown_x - 3), int(crown_y)), 3)
        pygame.draw.circle(s, ethereal_pink, (int(crown_x + 3), int(crown_y)), 3)
        pygame.draw.circle(s, dream_purple, (int(crown_x), int(crown_y + 2)), 2)
    
    # 梦幻核心
    pygame.draw.circle(s, fantasy_lavender, (60, 60), int(9 + pulse * 3))
    pygame.draw.circle(s, ethereal_pink, (60, 60), 5)
    
    # 梦境泡沫（漂浮上升）
    bubble_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(10):
        bubble_phase = (t * 0.6 + i * 0.4) % 2
        bubble_x = 35 + (i * 13) % 50 + math.sin(t + i) * 5
        bubble_y = 90 - bubble_phase * 50
        bubble_size = 3 + int(abs(math.sin(t * 2 + i)) * 3)
        bubble_alpha = int(150 * (1 - bubble_phase / 2))
        
        # 泡泡
        pygame.draw.circle(bubble_surf, (*bubble_colors[i % 3], bubble_alpha), 
                          (int(bubble_x), int(bubble_y)), bubble_size)
        # 高光
        pygame.draw.circle(bubble_surf, (255, 255, 255, bubble_alpha // 2), 
                          (int(bubble_x - 1), int(bubble_y - 1)), bubble_size // 2)
    s.blit(bubble_surf, (0, 0))


def _render_staradia_solar_flare(s, t, pulse):
    """11. 烈日凰舞 - 太阳金+凤凰火羽"""
    solar_gold = (255, 200, 50)
    corona_red = (255, 120, 30)
    flare_orange = (255, 180, 60)
    phoenix_yellow = (255, 230, 100)
    
    # 日冕背景
    corona_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(5):
        corona_r = 55 - i * 8 + int(pulse * 6)
        pygame.draw.circle(corona_surf, (*flare_orange, 55 - i * 10), (60, 60), corona_r)
    s.blit(corona_surf, (0, 0))
    
    # 太阳黑子（暗斑）
    for i in range(4):
        spot_angle = (i * 90 + t * 30) * 0.01745
        spot_dist = 25 + abs(math.sin(t + i)) * 5
        spot_x = 60 + math.cos(spot_angle) * spot_dist
        spot_y = 60 + math.sin(spot_angle) * spot_dist
        pygame.draw.circle(s, (200, 100, 20), (int(spot_x), int(spot_y)), 4)
        pygame.draw.circle(s, (150, 70, 10), (int(spot_x), int(spot_y)), 2)
    
    # 凤凰火焰翅膀
    wing_colors = [solar_gold, corona_red, phoenix_yellow]
    for angle, idx in [(55, 0), (125, 1), (25, 2), (155, 3), (355, 4), (185, 5)]:
        # 火焰尾迹
        trail_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        trail_angle_rad = math.radians(angle)
        for j in range(5):
            trail_dist = 15 + j * 5
            trail_x = 60 + math.cos(trail_angle_rad) * trail_dist
            trail_y = 60 + math.sin(trail_angle_rad) * trail_dist
            trail_alpha = 100 - j * 18
            pygame.draw.circle(trail_surf, (*corona_red, trail_alpha), 
                             (int(trail_x), int(trail_y)), 6 - j)
        s.blit(trail_surf, (0, 0))
        
        # 火羽
        _draw_prismatic_wing(s, 60, 60, angle, t, idx, wing_colors, 25)
    
    # 女皇身姿
    _draw_empress_body(s, 60, 60, t, solar_gold, phoenix_yellow, 29)
    
    # 凤凰火冠
    for i in range(7):
        flame_angle = (-75 + i * 25) * 0.01745 + math.sin(t * 4 + i) * 0.1
        flame_length = 10 + abs(math.sin(t * 5 + i)) * 6
        flame_x = 60 + math.cos(flame_angle) * 12
        flame_y = 25
        # 火焰
        flame_points = [
            (int(flame_x), int(flame_y - flame_length)),
            (int(flame_x + 2), int(flame_y - flame_length * 0.5)),
            (int(flame_x), int(flame_y)),
            (int(flame_x - 2), int(flame_y - flame_length * 0.5))
        ]
        pygame.draw.polygon(s, corona_red, flame_points)
        pygame.draw.polygon(s, phoenix_yellow, [flame_points[0], flame_points[2]], 2)
    
    # 太阳核心
    core_r = int(11 + pulse * 5)
    pygame.draw.circle(s, phoenix_yellow, (60, 60), core_r)
    pygame.draw.circle(s, solar_gold, (60, 60), core_r - 3)
    pygame.draw.circle(s, (255, 255, 240), (60, 60), 4)
    
    # 火焰粒子
    for i in range(10):
        ember_phase = (t * 1.5 + i * 0.3) % 1.5
        ember_angle = (i * 36 + t * 40) * 0.01745
        ember_dist = 35 + ember_phase * 20
        ex = 60 + math.cos(ember_angle) * ember_dist
        ey = 60 + math.sin(ember_angle) * ember_dist
        ember_alpha = int(220 * (1 - ember_phase / 1.5))
        ember_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(ember_surf, (*flare_orange, ember_alpha), (int(ex), int(ey)), 3)
        s.blit(ember_surf, (0, 0))


def _render_staradia_void_empress(s, t, pulse):
    """12. 虚渊暗皇 - 虚空紫+堕落女皇"""
    # 提亮颜色，增加可见度
    void_purple = (120, 60, 180)       # 更亮的紫色
    abyss_black = (60, 30, 90)         # 更亮的暗色
    dark_violet = (180, 80, 160)       # 更亮的紫罗兰
    corrupt_pink = (220, 100, 180)     # 更亮的粉色
    rift_colors = [(160, 90, 200), (100, 60, 150), (200, 100, 200)]
    
    # 虚空漩涡背景（多层扭曲）
    for vortex_layer in range(3):
        vortex_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        direction = 1 if vortex_layer % 2 == 0 else -1
        for i in range(30):
            angle = (i * 12 + t * 80 * direction + vortex_layer * 90) * 0.01745
            dist = 20 + i * 1.5 + vortex_layer * 5
            vx = 60 + math.cos(angle) * dist
            vy = 60 + math.sin(angle) * dist
            alpha = 220 - i * 5 - vortex_layer * 30
            size = 5 - vortex_layer
            pygame.draw.circle(vortex_surf, (*void_purple, max(50, alpha)), (int(vx), int(vy)), size)
        s.blit(vortex_surf, (0, 0))
    
    # 虚空裂隙（更醒目）
    rift_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(12):
        rift_angle = (i * 30 + t * 25) * 0.01745
        rift_points = [(60, 60)]
        for j in range(5):
            dist = 18 + j * 10
            offset = math.sin(j * 2.5 + t * 4) * 8
            rift_points.append((
                int(60 + math.cos(rift_angle) * dist + math.cos(rift_angle + 1.57) * offset),
                int(60 + math.sin(rift_angle) * dist + math.sin(rift_angle + 1.57) * offset)
            ))
        pygame.draw.lines(rift_surf, (*corrupt_pink, 255), False, rift_points, 3)
        pygame.draw.lines(rift_surf, (*dark_violet, 180), False, rift_points, 1)
    s.blit(rift_surf, (0, 0))
    
    # 虚空能量球（环绕）- 更大更亮
    for i in range(6):
        orb_angle = (i * 60 + t * 50) * 0.01745
        orb_dist = 38 + abs(math.sin(t * 3 + i)) * 8
        orb_x = 60 + math.cos(orb_angle) * orb_dist
        orb_y = 60 + math.sin(orb_angle) * orb_dist
        orb_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(orb_surf, (*void_purple, 180), (int(orb_x), int(orb_y)), 10)
        pygame.draw.circle(orb_surf, (*corrupt_pink, 255), (int(orb_x), int(orb_y)), 6)
        pygame.draw.circle(orb_surf, (255, 200, 255), (int(orb_x), int(orb_y)), 3)
        s.blit(orb_surf, (0, 0))
    
    # 虚空光晕 - 更亮
    for i in range(3):
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*void_purple, 80 - i * 20), (60, 60), 50 - i * 12)
        s.blit(glow_surf, (0, 0))
    
    # 堕落之翼（扭曲形态，左右对称布局）
    for angle, idx, size in [(65, 0, 28), (115, 1, 28), (35, 2, 24), (145, 3, 24), (5, 4, 20), (175, 5, 20)]:
        # 扭曲效果
        twisted_angle = angle + math.sin(t * 2 + idx) * 12
        _draw_prismatic_wing(s, 60, 60, twisted_angle, t, idx, rift_colors, size)
    
    # 女皇身姿（暗黑形态）
    _draw_empress_body(s, 60, 60, t, void_purple, dark_violet, 28)
    
    # 虚渊之冠（倒刺王冠）
    for i in range(7):
        thorn_angle = (-75 + i * 25) * 0.01745
        thorn_length = 9 + (3 if i % 2 == 0 else 0)
        thorn_x = 60 + math.cos(thorn_angle) * 13
        thorn_y = 26
        # 倒刺
        thorn_points = [
            (int(thorn_x), int(thorn_y - thorn_length)),
            (int(thorn_x + 2), int(thorn_y - 2)),
            (int(thorn_x - 2), int(thorn_y - 2))
        ]
        pygame.draw.polygon(s, dark_violet, thorn_points)
        pygame.draw.polygon(s, corrupt_pink, thorn_points, 1)
    
    # 虚空核心（漩涡）- 更醒目
    vortex_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(15):
        vortex_angle = (i * 24 + t * 80) * 0.01745
        vortex_dist = i * 2
        vortex_x = 60 + math.cos(vortex_angle) * vortex_dist
        vortex_y = 60 + math.sin(vortex_angle) * vortex_dist
        vortex_alpha = 255 - i * 12
        pygame.draw.circle(vortex_surf, (*corrupt_pink, max(80, vortex_alpha)), 
                          (int(vortex_x), int(vortex_y)), max(1, 4 - i // 5))
    s.blit(vortex_surf, (0, 0))
    
    # 中心核心亮点
    pygame.draw.circle(s, corrupt_pink, (60, 60), int(8 + pulse * 2))
    pygame.draw.circle(s, (255, 200, 255), (60, 60), 4)


def _render_staradia_base(s, t, pulse):
    """基础渲染（默认形态）"""
    _render_staradia_default(s, t, pulse)
