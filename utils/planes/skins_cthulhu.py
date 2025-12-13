# -*- coding: utf-8 -*-
"""
至尊机体涂装 - Cthulhu（月蚀星骸·克苏鲁）

真正的克苏鲁美学：不可名状的恐惧、扭曲的触手、无数的眼睛、深渊的凝视
"""
import pygame
import math
import random

# Cthulhu 涂装样式列表
CTHULHU_STYLES = [
    "cthulhu_default",      # 深渊之主 - 经典克苏鲁绿+章鱼头
    "cthulhu_abyss",        # 海沟巨兽 - 深海压强扭曲+生物发光
    "cthulhu_bloodmoon",    # 血祭狂潮 - 鲜血祭祀+邪教符文
    "cthulhu_void",         # 虚空之眼 - 纯黑裂隙+无数眼球
    "cthulhu_starfall",     # 星之眷属 - 陨星碎片+外星几何
    "cthulhu_cosmos",       # 宇宙蠕虫 - 星云血肉+无限延伸
    "cthulhu_nightmare",    # 梦魇造物 - 扭曲肉块+恐惧之眼
    "cthulhu_aurora",       # 极光异象 - 诡异光谱+形态不稳
    "cthulhu_eldritch",     # 远古遗骸 - 骨骼暴露+腐朽符文
    "cthulhu_eclipse",      # 黑日降临 - 吞噬之日+日冕触手
    "cthulhu_dreamland",    # 梦境彼岸 - 迷幻扭曲+不稳定
    "cthulhu_primordial",   # 原初混沌 - 不定形+原始汤
]


def is_cthulhu_style(model_style):
    return model_style in CTHULHU_STYLES


def render_cthulhu_skin(s, c, model_style, t, pid, static):
    if not is_cthulhu_style(model_style):
        return None
    pulse = 0 if static else abs(math.sin(t * 2))
    
    renderers = {
        "cthulhu_default": _render_cthulhu_default,
        "cthulhu_abyss": _render_cthulhu_abyss,
        "cthulhu_bloodmoon": _render_cthulhu_bloodmoon,
        "cthulhu_void": _render_cthulhu_void,
        "cthulhu_starfall": _render_cthulhu_starfall,
        "cthulhu_cosmos": _render_cthulhu_cosmos,
        "cthulhu_nightmare": _render_cthulhu_nightmare,
        "cthulhu_aurora": _render_cthulhu_aurora,
        "cthulhu_eldritch": _render_cthulhu_eldritch,
        "cthulhu_eclipse": _render_cthulhu_eclipse,
        "cthulhu_dreamland": _render_cthulhu_dreamland,
        "cthulhu_primordial": _render_cthulhu_primordial,
    }
    renderer = renderers.get(model_style, _render_cthulhu_default)
    renderer(s, t, pulse)
    return s


# =============================================================================
#   通用绘制函数
# =============================================================================

def _draw_eldritch_eye(s, cx, cy, size, t, iris_col, pupil_col, sclera_col=None, vertical=True):
    """邪神之眼 - 竖瞳/横瞳，带血丝"""
    sclera = sclera_col or (200, 180, 160)
    pygame.draw.ellipse(s, sclera, (cx - size, cy - size * 0.6, size * 2, size * 1.2))
    
    # 血丝
    for i in range(5):
        angle = (i * 72 + t * 20) * 0.01745
        bx = cx + math.cos(angle) * size * 0.7
        by = cy + math.sin(angle) * size * 0.4
        pygame.draw.line(s, (180, 50, 50), (cx, cy), (int(bx), int(by)), 1)
    
    # 虹膜
    iris_r = int(size * 0.55)
    wobble_x = math.sin(t * 1.5) * 2
    wobble_y = math.cos(t * 1.2) * 1
    pygame.draw.circle(s, iris_col, (int(cx + wobble_x), int(cy + wobble_y)), iris_r)
    
    # 瞳孔
    if vertical:
        pw, ph = max(2, int(size * 0.15 + abs(math.sin(t * 3)) * 3)), int(size * 0.8)
    else:
        pw, ph = int(size * 0.8), max(2, int(size * 0.15 + abs(math.sin(t * 3)) * 3))
    pygame.draw.ellipse(s, pupil_col, (int(cx - pw//2 + wobble_x), int(cy - ph//2 + wobble_y), pw, ph))
    pygame.draw.circle(s, (255, 255, 255), (int(cx - size * 0.3), int(cy - size * 0.2)), max(1, int(size * 0.12)))


def _draw_tentacle_organic(s, ox, oy, length, base_angle, t, color, thickness=5, suckers=True):
    """有机触手 - 带吸盘、蜿蜒、渐细"""
    segments = 12
    points = []
    for i in range(segments + 1):
        prog = i / segments
        wave1 = math.sin(t * 2.5 + prog * 5) * (8 + prog * 12)
        wave2 = math.cos(t * 1.8 + prog * 3) * 4
        dist = length * prog
        angle_rad = math.radians(base_angle)
        perp = angle_rad + math.pi / 2
        px = ox + math.cos(angle_rad) * dist + math.cos(perp) * (wave1 + wave2)
        py = oy + math.sin(angle_rad) * dist + math.sin(perp) * (wave1 + wave2)
        points.append((int(px), int(py)))
    
    if len(points) >= 2:
        for i in range(len(points) - 1):
            prog = i / len(points)
            seg_thick = max(1, int(thickness * (1 - prog * 0.8)))
            fade = 1 - prog * 0.4
            seg_col = (int(color[0] * fade), int(color[1] * fade), int(color[2] * fade))
            pygame.draw.line(s, seg_col, points[i], points[i + 1], seg_thick)
        
        if suckers and len(points) > 3:
            for i in range(2, len(points) - 1, 2):
                sucker_size = max(1, int(3 * (1 - i / len(points))))
                pygame.draw.circle(s, (color[0]//2, color[1]//2, color[2]//2), points[i], sucker_size)


def _draw_writhing_mass(s, cx, cy, base_r, t, color, variation=0.3):
    """蠕动的肉块"""
    points = []
    for i in range(16):
        angle = i * (2 * math.pi / 16)
        r = base_r * (1 + math.sin(t * 2 + i * 0.8) * variation + math.cos(t * 3 + i * 1.2) * variation * 0.5)
        points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
    if len(points) >= 3:
        pygame.draw.polygon(s, color, points)


# =============================================================================
#   1. 深渊之主 - 经典克苏鲁：章鱼头+面部触手
# =============================================================================

def _render_cthulhu_default(s, t, pulse):
    deep_green = (30, 80, 60)
    slime_green = (50, 120, 80)
    pale_flesh = (140, 160, 130)
    eye_yellow = (180, 200, 80)
    void_black = (10, 15, 12)
    
    # 深渊涟漪背景
    for i in range(3):
        ripple_r = 50 - i * 12 + int(pulse * 5)
        ripple_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(ripple_surf, (*deep_green, 50 - i * 15), (60, 60), ripple_r)
        s.blit(ripple_surf, (0, 0))
    
    # 章鱼形态头颅
    head_points = []
    for i in range(20):
        angle = i * 18 * 0.01745
        r = 32 + math.sin(t + i * 0.3) * 3 if i < 10 else 28 - (i - 10) * 1.5 + math.sin(t + i * 0.3) * 2
        head_points.append((int(60 + math.cos(angle) * r), int(50 + math.sin(angle) * r * 0.9)))
    pygame.draw.polygon(s, deep_green, head_points)
    pygame.draw.polygon(s, slime_green, head_points, 2)
    
    # 头顶隆起
    pygame.draw.ellipse(s, slime_green, (42, 25, 36, 25))
    pygame.draw.ellipse(s, deep_green, (45, 28, 30, 20))
    
    # 巨眼
    _draw_eldritch_eye(s, 60, 48, 14, t, eye_yellow, void_black, pale_flesh)
    
    # 面部触须
    for ox, oy, length, angle in [(45, 62, 40, 160), (52, 65, 35, 175), (60, 68, 38, 180), (68, 65, 35, 185), (75, 62, 40, 200)]:
        _draw_tentacle_organic(s, ox, oy, length + pulse * 5, angle, t + angle * 0.01, slime_green, 4, True)
    
    # 鳞片纹理
    for i in range(8):
        sx = 45 + (i % 4) * 10 + math.sin(t + i) * 2
        sy = 35 + (i // 4) * 12
        pygame.draw.arc(s, pale_flesh, (sx - 4, sy - 3, 8, 6), 0, math.pi, 1)


# =============================================================================
#   2. 海沟巨兽 - 深海压强扭曲，生物发光
# =============================================================================

def _render_cthulhu_abyss(s, t, pulse):
    abyss_black = (5, 12, 20)
    pressure_blue = (20, 50, 80)
    biolum_cyan = (100, 255, 220)
    biolum_purple = (180, 100, 255)
    
    pygame.draw.circle(s, abyss_black, (60, 60), 50)
    
    # 扭曲身体
    body_points = []
    for i in range(24):
        angle = i * 15 * 0.01745
        r = 35 + math.sin(i * 0.7) * 8 + math.cos(i * 1.3 + t) * 5
        body_points.append((int(60 + math.cos(angle) * r), int(58 + math.sin(angle) * r * 0.85)))
    pygame.draw.polygon(s, pressure_blue, body_points)
    
    # 生物发光点
    for i, (lx, ly) in enumerate([(40, 45), (80, 45), (35, 60), (85, 60), (45, 75), (75, 75), (55, 35), (65, 35)]):
        flicker = abs(math.sin(t * 3 + i * 1.5))
        if flicker > 0.3:
            col = biolum_cyan if i % 2 == 0 else biolum_purple
            glow_surf = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*col, int(100 * flicker)), (8, 8), 6)
            pygame.draw.circle(glow_surf, col, (8, 8), 2)
            s.blit(glow_surf, (lx - 8, ly - 8))
    
    # 多眼
    for ex, ey, size in [(48, 50, 8), (72, 50, 8), (60, 42, 6), (38, 58, 5), (82, 58, 5)]:
        _draw_eldritch_eye(s, ex, ey, size, t, biolum_cyan, abyss_black, (80, 90, 100))
    
    # 细长触角
    for i in range(6):
        _draw_tentacle_organic(s, 60, 65, 30 + i * 3, 30 + i * 20 + 90, t + i * 0.5, pressure_blue, 2, False)


# =============================================================================
#   3. 血祭狂潮 - 鲜血祭祀，邪教符文
# =============================================================================

def _render_cthulhu_bloodmoon(s, t, pulse):
    blood_red = (150, 20, 30)
    dark_crimson = (80, 10, 20)
    flesh_pink = (180, 100, 100)
    bone_white = (220, 210, 200)
    
    # 血雾
    for i in range(4):
        blood_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(blood_surf, (*blood_red, 40 - i * 8), (60, 60), 55 - i * 10)
        s.blit(blood_surf, (0, 0))
    
    _draw_writhing_mass(s, 60, 55, 30, t, dark_crimson, 0.2)
    _draw_writhing_mass(s, 60, 55, 25, t * 0.8, blood_red, 0.15)
    
    # 邪教符文圆环
    rune_r = 38 + int(pulse * 3)
    pygame.draw.circle(s, bone_white, (60, 55), rune_r, 1)
    pygame.draw.circle(s, bone_white, (60, 55), rune_r - 5, 1)
    
    # 符文三角
    for i in range(6):
        angle = (i * 60 + t * 15) * 0.01745
        rx, ry = 60 + math.cos(angle) * rune_r, 55 + math.sin(angle) * rune_r
        pygame.draw.polygon(s, bone_white, [(rx, ry - 4), (rx - 3, ry + 3), (rx + 3, ry + 3)])
    
    _draw_eldritch_eye(s, 60, 52, 12, t, blood_red, (20, 5, 5), flesh_pink)
    
    # 血泪
    tear_y = 60 + int((t * 30) % 30)
    pygame.draw.ellipse(s, blood_red, (57, tear_y, 6, 10))
    
    for i in range(4):
        _draw_tentacle_organic(s, 60, 70, 35, 45 + i * 90 + 45, t + i, blood_red, 4, False)


# =============================================================================
#   4. 虚空之眼 - 纯黑裂隙，无数眼球
# =============================================================================

def _render_cthulhu_void(s, t, pulse):
    void_black = (5, 5, 8)
    rift_purple = (80, 40, 120)
    eye_glow = (200, 180, 255)
    
    pygame.draw.circle(s, void_black, (60, 60), 52)
    
    # 裂隙
    for i in range(8):
        angle = i * 45 * 0.01745 + t * 0.1
        points = [(60, 55)]
        for j in range(6):
            dist = 10 + j * 8
            offset = math.sin(j * 2 + t) * 5
            points.append((int(60 + math.cos(angle) * dist + math.cos(angle + 1.57) * offset),
                          int(55 + math.sin(angle) * dist + math.sin(angle + 1.57) * offset)))
        pygame.draw.lines(s, rift_purple, False, points, 2)
    
    # 无数眼球
    for i, (ex, ey, size) in enumerate([(60, 50, 10), (42, 45, 6), (78, 45, 6), (35, 58, 5), (85, 58, 5),
                                         (48, 68, 5), (72, 68, 5), (55, 38, 4), (65, 38, 4), (40, 72, 4), (80, 72, 4)]):
        _draw_eldritch_eye(s, ex, ey, size, t + i * 0.7, rift_purple, (0, 0, 0), eye_glow, i % 2 == 0)


# =============================================================================
#   5. 星之眷属 - 外星几何，非欧几里得
# =============================================================================

def _render_cthulhu_starfall(s, t, pulse):
    star_purple = (100, 60, 150)
    cosmic_blue = (60, 80, 180)
    meteor_gold = (255, 200, 100)
    void_dark = (20, 15, 40)
    
    # 星空
    for i in range(15):
        sx, sy = 20 + (i * 37) % 80, 15 + (i * 23) % 90
        if abs(math.sin(t * 3 + i)) > 0.5:
            pygame.draw.circle(s, meteor_gold, (sx, sy), 1)
    
    # 不可能三角
    pygame.draw.polygon(s, void_dark, [(60, 20), (90, 70), (30, 70)])
    pygame.draw.polygon(s, star_purple, [(60, 20), (90, 70), (30, 70)], 2)
    pygame.draw.polygon(s, cosmic_blue, [(60, 75), (40, 40), (80, 40)], 2)
    pygame.draw.line(s, star_purple, (60, 20), (60, 75), 1)
    pygame.draw.line(s, star_purple, (30, 70), (80, 40), 1)
    pygame.draw.line(s, star_purple, (90, 70), (40, 40), 1)
    
    # 星云眼
    pygame.draw.circle(s, (180, 170, 200), (60, 50), 12)
    for i in range(20):
        angle = i * 18 * 0.01745 + t
        r = 6 + math.sin(i + t * 2) * 2
        pygame.draw.circle(s, star_purple, (int(60 + math.cos(angle) * r), int(50 + math.sin(angle) * r)), 1)
    pygame.draw.ellipse(s, void_dark, (58, 44, 4, 12))
    
    # 陨石碎片
    for i in range(5):
        angle_rad = math.radians(i * 72 + 36)
        ex, ey = 60 + math.cos(angle_rad) * (25 + pulse * 5), 55 + math.sin(angle_rad) * (25 + pulse * 5)
        pygame.draw.polygon(s, meteor_gold, [(ex, ey - 5), (ex + 4, ey), (ex + 2, ey + 6), (ex - 3, ey + 4), (ex - 4, ey - 2)])


# =============================================================================
#   6. 宇宙蠕虫 - 无限延伸的虫体
# =============================================================================

def _render_cthulhu_cosmos(s, t, pulse):
    nebula_pink = (200, 100, 150)
    nebula_blue = (80, 120, 200)
    flesh_cosmic = (180, 140, 160)
    core_white = (255, 240, 250)
    void_purple = (40, 20, 60)
    
    # 星云背景
    for i in range(3):
        nebula_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.ellipse(nebula_surf, (*nebula_pink, 30), (10 + i * 20, 20 + i * 15, 60, 40))
        pygame.draw.ellipse(nebula_surf, (*nebula_blue, 25), (20 + i * 20, 15 + i * 15, 50, 50))
        s.blit(nebula_surf, (0, 0))
    
    # 蠕虫体节
    seg_points = []
    for i in range(8):
        prog = i / 7
        sx = 30 + prog * 60 + math.sin(t * 2 + prog * 4) * 15
        sy = 40 + math.sin(prog * 3.14) * 25 + math.cos(t * 1.5 + prog * 3) * 8
        sr = 12 - i + int(pulse * 2)
        seg_points.append((int(sx), int(sy), sr))
    
    for sx, sy, sr in seg_points:
        pygame.draw.circle(s, flesh_cosmic, (sx, sy), sr)
        pygame.draw.circle(s, nebula_pink, (sx, sy), sr, 1)
    
    # 头部巨口
    head_x, head_y = seg_points[0][0], seg_points[0][1]
    pygame.draw.circle(s, flesh_cosmic, (head_x, head_y), 15)
    mouth_open = abs(math.sin(t * 2)) * 8 + 4
    pygame.draw.ellipse(s, void_purple, (head_x - 8, head_y - int(mouth_open)//2, 16, int(mouth_open)))
    for i in range(5):
        pygame.draw.polygon(s, core_white, [(head_x - 6 + i * 3, head_y - 2), 
                                            (head_x - 5 + i * 3, head_y + 3), 
                                            (head_x - 4 + i * 3, head_y - 2)])
    
    _draw_eldritch_eye(s, head_x, head_y - 10, 6, t, nebula_blue, void_purple, core_white)


# =============================================================================
#   7. 梦魇造物 - 扭曲的肉块，恐惧之眼
# =============================================================================

def _render_cthulhu_nightmare(s, t, pulse):
    nightmare_black = (15, 10, 20)
    fear_red = (180, 40, 60)
    flesh_gray = (100, 80, 90)
    scream_white = (240, 230, 250)
    
    # 恐惧雾气
    for i in range(5):
        fog_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        fx = 30 + i * 15 + math.sin(t + i) * 10
        fy = 30 + i * 12 + math.cos(t * 0.7 + i) * 8
        pygame.draw.ellipse(fog_surf, (*nightmare_black, 60 - i * 10), (fx - 20, fy - 15, 40, 30))
        s.blit(fog_surf, (0, 0))
    
    _draw_writhing_mass(s, 60, 55, 32, t, flesh_gray, 0.35)
    _draw_writhing_mass(s, 60, 55, 25, t * 1.3, nightmare_black, 0.25)
    
    # 扭曲肢体
    for lx, ly, length, angle in [(35, 50, 25, -150), (85, 50, 25, -30), (40, 75, 20, 150), (80, 75, 20, 30)]:
        points = [(lx, ly)]
        for j in range(5):
            dist = length * (j + 1) / 5
            twist = math.sin(t * 3 + j) * 8
            points.append((int(lx + math.cos(math.radians(angle)) * dist + twist),
                          int(ly + math.sin(math.radians(angle)) * dist)))
        pygame.draw.lines(s, flesh_gray, False, points, 3)
        pygame.draw.circle(s, fear_red, points[-1], 3)
    
    # 多个恐惧之眼
    for i, (ex, ey, size) in enumerate([(50, 45, 8), (70, 45, 8), (60, 55, 10), (42, 60, 5), (78, 60, 5)]):
        if math.sin(t * 2 + i * 1.3) > -0.3:
            _draw_eldritch_eye(s, ex, ey, size, t + i, fear_red, nightmare_black, scream_white)
    
    # 尖叫的嘴
    pygame.draw.ellipse(s, nightmare_black, (52, 78 + int(math.sin(t * 4) * 3), 16, 8 + int(pulse * 4)))


# =============================================================================
#   8. 极光异象 - 诡异的光谱变换
# =============================================================================

def _render_cthulhu_aurora(s, t, pulse):
    def get_aurora_color(offset):
        h = (t * 0.5 + offset) % 3
        if h < 1: return (int(255 * (1 - h)), int(255 * h), 100)
        elif h < 2: return (100, int(255 * (2 - h)), int(255 * (h - 1)))
        else: return (int(255 * (h - 2)), 100, int(255 * (3 - h)))
    
    # 极光波浪
    for wave in range(5):
        wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        points = [(i * 5, int(30 + wave * 15 + math.sin(t * 2 + i * 0.3 + wave) * 10)) for i in range(25)]
        pygame.draw.lines(wave_surf, (*get_aurora_color(wave * 0.5), 100), False, points, 3)
        s.blit(wave_surf, (0, 0))
    
    # 不稳定形态
    body_points = [(int(60 + math.cos(i * 22.5 * 0.01745) * (28 + math.sin(t * 4 + i * 0.5) * 8)),
                   int(55 + math.sin(i * 22.5 * 0.01745) * (28 + math.sin(t * 4 + i * 0.5) * 8))) for i in range(16)]
    pygame.draw.polygon(s, get_aurora_color(0), body_points)
    pygame.draw.polygon(s, get_aurora_color(1), body_points, 2)
    
    _draw_eldritch_eye(s, 60, 50, 12, t, get_aurora_color(2), (20, 20, 30), get_aurora_color(0))
    
    for i in range(6):
        _draw_tentacle_organic(s, 60, 60, 30 + pulse * 5, i * 60 + t * 20, t + i, get_aurora_color(i * 0.3), 3, False)


# =============================================================================
#   9. 远古遗骸 - 骨骼暴露，腐朽符文
# =============================================================================

def _render_cthulhu_eldritch(s, t, pulse):
    bone_white = (220, 210, 190)
    bone_shadow = (160, 145, 120)
    decay_green = (80, 100, 60)
    rune_gold = (180, 150, 80)
    void_black = (20, 18, 15)
    
    # 腐朽雾气
    for i in range(3):
        decay_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.ellipse(decay_surf, (*decay_green, 40), 
                           (15 + i * 20 + math.sin(t * 0.5 + i) * 10, 30 + math.cos(t * 0.3 + i) * 8, 50, 40))
        s.blit(decay_surf, (0, 0))
    
    # 骷髅
    skull_points = [(60, 25), (80, 35), (88, 55), (82, 75), (60, 85), (38, 75), (32, 55), (40, 35)]
    pygame.draw.polygon(s, bone_white, skull_points)
    pygame.draw.polygon(s, bone_shadow, skull_points, 2)
    
    # 眼眶
    pygame.draw.ellipse(s, void_black, (42, 42, 16, 20))
    pygame.draw.ellipse(s, void_black, (62, 42, 16, 20))
    glow_phase = abs(math.sin(t * 1.5))
    if glow_phase > 0.3:
        pygame.draw.circle(s, (*rune_gold, int(150 * glow_phase)), (50, 52), 4)
        pygame.draw.circle(s, (*rune_gold, int(150 * glow_phase)), (70, 52), 4)
    
    pygame.draw.polygon(s, void_black, [(57, 60), (60, 55), (63, 60), (60, 68)])
    
    # 牙齿
    for i in range(6):
        pygame.draw.rect(s, bone_shadow, (46 + i * 5, 73, 4, 8))
    
    # 符文
    for i, (rx, ry) in enumerate([(35, 40), (85, 40), (30, 70), (90, 70)]):
        if i % 2 == 0:
            pygame.draw.polygon(s, rune_gold, [(rx, ry - 4), (rx - 4, ry + 3), (rx + 4, ry + 3)])
        else:
            pygame.draw.circle(s, rune_gold, (rx, ry), 4, 1)


# =============================================================================
#   10. 黑日降临 - 吞噬之日，日冕触手
# =============================================================================

def _render_cthulhu_eclipse(s, t, pulse):
    corona_orange = (255, 150, 50)
    corona_red = (255, 80, 30)
    eclipse_black = (10, 8, 5)
    flare_yellow = (255, 220, 100)
    
    # 日冕背景
    for i in range(5):
        corona_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(corona_surf, (*corona_orange, 60 - i * 10), (60, 55), 55 - i * 5)
        s.blit(corona_surf, (0, 0))
    
    # 日冕触手
    for i in range(12):
        angle = i * 30 + t * 10
        flare_length = 35 + math.sin(t * 3 + i) * 10 + pulse * 8
        points = [(60, 55)]
        for j in range(6):
            dist = 20 + flare_length * (j / 5)
            wave = math.sin(t * 4 + j * 0.5 + i) * 5
            points.append((int(60 + math.cos(math.radians(angle)) * dist + wave),
                          int(55 + math.sin(math.radians(angle)) * dist)))
        for j in range(len(points) - 1):
            col = flare_yellow if j < 2 else (corona_orange if j < 4 else corona_red)
            pygame.draw.line(s, col, points[j], points[j + 1], max(1, 4 - j))
    
    # 黑日核心
    pygame.draw.circle(s, eclipse_black, (60, 55), 25)
    pygame.draw.circle(s, corona_orange, (60, 55), 27, 2)
    
    eye_glow = int(pulse * 150 + 50)
    _draw_eldritch_eye(s, 60, 52, 10, t, corona_orange, eclipse_black, (80, 60, 40))


# =============================================================================
#   11. 梦境彼岸 - 迷幻扭曲，不稳定
# =============================================================================

def _render_cthulhu_dreamland(s, t, pulse):
    dream_pink = (220, 150, 200)
    mist_blue = (150, 180, 220)
    dream_purple = (180, 120, 200)
    ethereal = (240, 235, 255)
    shadow = (60, 50, 80)
    
    # 迷雾
    for i in range(6):
        mist_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        mx = 30 + i * 15 + math.sin(t * 0.5 + i * 0.7) * 15
        my = 40 + math.cos(t * 0.3 + i) * 20
        pygame.draw.ellipse(mist_surf, (*mist_blue, 40), (mx - 20, my - 15, 40, 30))
        pygame.draw.ellipse(mist_surf, (*dream_pink, 30), (mx - 15, my - 10, 35, 25))
        s.blit(mist_surf, (0, 0))
    
    # 虚影
    for ghost in range(3):
        offset_x = math.sin(t * 2 + ghost * 2) * 5
        offset_y = math.cos(t * 1.5 + ghost * 2) * 3
        ghost_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        _draw_writhing_mass(ghost_surf, 60 + int(offset_x), 55 + int(offset_y), 25 - ghost * 3, 
                           t + ghost, (*dream_purple, 180 - ghost * 50), 0.2)
        s.blit(ghost_surf, (0, 0))
    
    # 闪烁眼睛
    for i, (ex, ey, size) in enumerate([(48, 48, 8), (72, 48, 8), (60, 60, 6)]):
        visibility = math.sin(t * 2 + i * 1.5)
        if visibility > 0:
            _draw_eldritch_eye(s, ex, ey, size, t, dream_purple, shadow, ethereal)
    
    # 漂浮符号
    for i in range(4):
        sx = 35 + i * 20 + math.sin(t + i) * 5
        sy = 30 + math.cos(t * 0.7 + i) * 15
        rot = t + i
        tri_points = [(int(sx + math.cos(rot + j * 2.09) * 4), int(sy + math.sin(rot + j * 2.09) * 4)) for j in range(3)]
        pygame.draw.polygon(s, ethereal, tri_points, 1)


# =============================================================================
#   12. 原初混沌 - 不定形，原始汤
# =============================================================================

def _render_cthulhu_primordial(s, t, pulse):
    chaos_gray = (80, 75, 85)
    primordial = (60, 55, 70)
    creation_light = (255, 250, 220)
    void_deep = (20, 18, 25)
    proto_green = (100, 120, 80)
    
    # 混沌团块
    for blob in range(5):
        blob_points = []
        blob_cx = 60 + math.sin(t * 0.3 + blob) * 10
        blob_cy = 55 + math.cos(t * 0.4 + blob * 0.7) * 8
        blob_r = 35 - blob * 5
        for i in range(12):
            angle = i * (2 * math.pi / 12)
            r_var = blob_r * (0.6 + math.sin(t + i * 0.5 + blob) * 0.4 + math.cos(t * 1.5 + i * 0.8 + blob) * 0.3)
            blob_points.append((int(blob_cx + math.cos(angle) * r_var), int(blob_cy + math.sin(angle) * r_var)))
        col = primordial if blob % 2 == 0 else chaos_gray
        pygame.draw.polygon(s, col, blob_points)
    
    # 创世火花
    for i in range(8):
        if math.sin(t * 2 + i * 0.8) > 0.5:
            pygame.draw.circle(s, creation_light, (30 + (i * 13) % 60, 25 + (i * 17) % 70), 2 + int(math.sin(t * 2 + i) * 2))
    
    # 分裂眼睛
    num_eyes = 3 + int(abs(math.sin(t * 0.5)) * 3)
    for i in range(num_eyes):
        eye_angle = t * 0.3 + i * (2 * math.pi / num_eyes)
        eye_dist = 15 + abs(math.sin(t + i)) * 10
        ex = 60 + math.cos(eye_angle) * eye_dist
        ey = 55 + math.sin(eye_angle) * eye_dist * 0.7
        eye_size = 5 + int(abs(math.cos(t + i * 0.7)) * 4)
        pygame.draw.ellipse(s, creation_light, (ex - eye_size, ey - eye_size * 0.6, eye_size * 2, eye_size * 1.2))
        pygame.draw.ellipse(s, void_deep, (ex - 1, ey - eye_size * 0.4, 2, int(eye_size * 0.8)))
    
    # 伪足
    for i in range(6):
        base_angle = i * 60 + t * 15
        extend = 0.5 + abs(math.sin(t * 2 + i * 0.9)) * 0.5
        length = 30 * extend
        points = [(60, 55)]
        for j in range(5):
            dist = length * (j + 1) / 5
            wave = math.sin(t * 3 + j * 0.7 + i) * 8
            points.append((int(60 + math.cos(math.radians(base_angle)) * dist + wave),
                          int(55 + math.sin(math.radians(base_angle)) * dist)))
        for j in range(len(points) - 1):
            pygame.draw.line(s, proto_green, points[j], points[j + 1], max(1, 4 - j))
    
    # 气泡
    for i in range(5):
        bubble_x = 40 + i * 10 + math.sin(t * 0.5 + i) * 5
        bubble_y = 80 - int((t * 20 + i * 15) % 60)
        pygame.draw.circle(s, creation_light, (int(bubble_x), bubble_y), 2 + i % 3, 1)


def _render_cthulhu_base(s, t, pulse):
    _render_cthulhu_default(s, t, pulse)
