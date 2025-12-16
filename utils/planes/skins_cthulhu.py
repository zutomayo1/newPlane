# -*- coding: utf-8 -*-
"""
月蚀星骸·克苏鲁 (Eclipse-Core · CTHULHU)
TYPE-ELDRITCH "深渊凝视者"

设计理念：不可名状的宇宙恐惧 · 触手与眼球的深渊美学
视觉关键词：克苏鲁神话、深渊绿、无数眼睛、扭曲触手、邪神符文

12款异质化涂装 - 每个涂装独立绘制函数
"""
import pygame
import math
import random

# =============================================================================
#   12款皮肤主题配置
# =============================================================================

CTHULHU_THEMES = {
    # ================= [系列一：深渊之主] =================
    "cthulhu_default": {
        "name": "深渊之主·原初",
        "body": (30, 80, 60),           # 深渊绿
        "flesh": (50, 120, 80),         # 黏液绿
        "eye_iris": (180, 200, 80),     # 黄绿虹膜
        "eye_pupil": (10, 15, 12),      # 深渊黑瞳
        "accent": (140, 160, 130),      # 苍白肉色
        "glow": (100, 180, 120),        # 绿光
    },
    "cthulhu_abyss": {
        "name": "海沟巨兽·深渊",
        "body": (5, 12, 20),            # 深海黑
        "flesh": (20, 50, 80),          # 压力蓝
        "eye_iris": (100, 255, 220),    # 生物发光青
        "eye_pupil": (5, 12, 20),       # 深海黑瞳
        "accent": (180, 100, 255),      # 生物发光紫
        "glow": (100, 255, 220),        # 青光
    },
    "cthulhu_bloodmoon": {
        "name": "血祭狂潮·猩红",
        "body": (80, 10, 20),           # 深红
        "flesh": (150, 20, 30),         # 鲜血红
        "eye_iris": (150, 20, 30),      # 血红虹膜
        "eye_pupil": (20, 5, 5),        # 暗红瞳
        "accent": (220, 210, 200),      # 骨白
        "glow": (255, 100, 100),        # 血光
    },

    # ================= [系列二：虚空凝视] =================
    "cthulhu_void": {
        "name": "虚空之眼·裂隙",
        "body": (5, 5, 8),              # 虚空黑
        "flesh": (80, 40, 120),         # 裂隙紫
        "eye_iris": (80, 40, 120),      # 紫色虹膜
        "eye_pupil": (0, 0, 0),         # 纯黑瞳
        "accent": (200, 180, 255),      # 幽光
        "glow": (150, 100, 200),        # 紫光
    },
    "cthulhu_starfall": {
        "name": "星之眷属·陨落",
        "body": (20, 15, 40),           # 宇宙暗
        "flesh": (100, 60, 150),        # 星云紫
        "eye_iris": (60, 80, 180),      # 宇宙蓝
        "eye_pupil": (20, 15, 40),      # 暗紫瞳
        "accent": (255, 200, 100),      # 陨石金
        "glow": (180, 150, 255),        # 星光
    },
    "cthulhu_cosmos": {
        "name": "宇宙蠕虫·星云",
        "body": (40, 20, 60),           # 星云暗
        "flesh": (200, 100, 150),       # 星云粉
        "eye_iris": (80, 120, 200),     # 星云蓝
        "eye_pupil": (40, 20, 60),      # 暗紫瞳
        "accent": (255, 240, 250),      # 星核白
        "glow": (200, 150, 220),        # 粉光
    },

    # ================= [系列三：梦魇造物] =================
    "cthulhu_nightmare": {
        "name": "梦魇造物·恐惧",
        "body": (15, 10, 20),           # 梦魇黑
        "flesh": (100, 80, 90),         # 腐肉灰
        "eye_iris": (180, 40, 60),      # 恐惧红
        "eye_pupil": (15, 10, 20),      # 梦魇瞳
        "accent": (240, 230, 250),      # 尖叫白
        "glow": (200, 80, 100),         # 恐惧光
    },
    "cthulhu_aurora": {
        "name": "极光异象·幻彩",
        "body": (30, 40, 50),           # 极光底
        "flesh": (150, 200, 180),       # 极光绿
        "eye_iris": (200, 150, 255),    # 极光紫
        "eye_pupil": (20, 20, 30),      # 暗瞳
        "accent": (255, 200, 150),      # 极光橙
        "glow": (100, 255, 200),        # 极光
    },
    "cthulhu_eldritch": {
        "name": "远古遗骸·枯骨",
        "body": (20, 18, 15),           # 腐朽黑
        "flesh": (160, 145, 120),       # 骨影
        "eye_iris": (180, 150, 80),     # 符文金
        "eye_pupil": (20, 18, 15),      # 腐朽瞳
        "accent": (220, 210, 190),      # 枯骨白
        "glow": (180, 150, 80),         # 符文光
    },

    # ================= [系列四：终末启示] =================
    "cthulhu_eclipse": {
        "name": "黑日降临·日冕",
        "body": (10, 8, 5),             # 黑日核
        "flesh": (255, 150, 50),        # 日冕橙
        "eye_iris": (255, 150, 50),     # 日冕虹膜
        "eye_pupil": (10, 8, 5),        # 黑日瞳
        "accent": (255, 220, 100),      # 耀斑黄
        "glow": (255, 180, 80),         # 日冕光
    },
    "cthulhu_dreamland": {
        "name": "梦境彼岸·迷幻",
        "body": (60, 50, 80),           # 梦影
        "flesh": (220, 150, 200),       # 梦粉
        "eye_iris": (180, 120, 200),    # 梦紫
        "eye_pupil": (60, 50, 80),      # 梦瞳
        "accent": (240, 235, 255),      # 虚幻白
        "glow": (200, 180, 255),        # 梦光
    },
    "cthulhu_primordial": {
        "name": "原初混沌·创世",
        "body": (60, 55, 70),           # 混沌灰
        "flesh": (80, 75, 85),          # 原初灰
        "eye_iris": (255, 250, 220),    # 创世光
        "eye_pupil": (20, 18, 25),      # 虚无瞳
        "accent": (100, 120, 80),       # 原生绿
        "glow": (255, 250, 220),        # 创世光
    },
}

# 涂装样式列表
CTHULHU_STYLES = list(CTHULHU_THEMES.keys())


def is_cthulhu_style(style):
    """检查是否为克苏鲁涂装"""
    return style in CTHULHU_STYLES


def get_cthulhu_theme(style):
    """获取涂装主题"""
    return CTHULHU_THEMES.get(style, CTHULHU_THEMES["cthulhu_default"])


# =============================================================================
#   通用绘制辅助函数
# =============================================================================

def _draw_eldritch_eye(s, cx, cy, size, t, theme, vertical=True):
    """
    邪神之眼 - 竖瞳/横瞳，带血丝和动态瞳孔
    """
    # 眼白（略带病态）
    sclera = (200, 190, 180)
    pygame.draw.ellipse(s, sclera, (cx - size, cy - size * 0.6, size * 2, size * 1.2))
    
    # 血丝
    for i in range(6):
        angle = (i * 60 + t * 15) * 0.01745
        bx = cx + math.cos(angle) * size * 0.75
        by = cy + math.sin(angle) * size * 0.45
        pygame.draw.line(s, (180, 50, 50), (cx, cy), (int(bx), int(by)), 1)
    
    # 虹膜
    iris_r = int(size * 0.55)
    wobble_x = math.sin(t * 1.5) * 2
    wobble_y = math.cos(t * 1.2) * 1.5
    pygame.draw.circle(s, theme["eye_iris"], (int(cx + wobble_x), int(cy + wobble_y)), iris_r)
    
    # 虹膜纹理
    for i in range(8):
        ring_angle = i * math.pi / 4 + t * 0.1
        rx = cx + wobble_x + math.cos(ring_angle) * iris_r * 0.7
        ry = cy + wobble_y + math.sin(ring_angle) * iris_r * 0.7
        pygame.draw.line(s, (*theme["eye_iris"], 150), 
                        (int(cx + wobble_x), int(cy + wobble_y)), 
                        (int(rx), int(ry)), 1)
    
    # 瞳孔（竖瞳或横瞳）
    pupil_contract = abs(math.sin(t * 3)) * 3
    if vertical:
        pw = max(2, int(size * 0.15 + pupil_contract))
        ph = int(size * 0.8)
    else:
        pw = int(size * 0.8)
        ph = max(2, int(size * 0.15 + pupil_contract))
    
    pygame.draw.ellipse(s, theme["eye_pupil"], 
                       (int(cx - pw//2 + wobble_x), int(cy - ph//2 + wobble_y), pw, ph))
    
    # 高光
    pygame.draw.circle(s, (255, 255, 255), 
                      (int(cx - size * 0.3), int(cy - size * 0.25)), 
                      max(1, int(size * 0.15)))


def _draw_tentacle(s, ox, oy, length, base_angle, t, color, thickness=5, suckers=True):
    """
    有机触手 - 带吸盘、蜿蜒、渐细
    """
    segments = 14
    points = []
    
    for i in range(segments + 1):
        prog = i / segments
        # 多重波动
        wave1 = math.sin(t * 2.5 + prog * 5) * (8 + prog * 15)
        wave2 = math.cos(t * 1.8 + prog * 3.5) * 5
        wave3 = math.sin(t * 3.2 + prog * 2) * 3
        
        dist = length * prog
        angle_rad = math.radians(base_angle)
        perp = angle_rad + math.pi / 2
        
        px = ox + math.cos(angle_rad) * dist + math.cos(perp) * (wave1 + wave2 + wave3)
        py = oy + math.sin(angle_rad) * dist + math.sin(perp) * (wave1 + wave2)
        points.append((int(px), int(py)))
    
    if len(points) >= 2:
        # 绘制触手主体（渐细）
        for i in range(len(points) - 1):
            prog = i / len(points)
            seg_thick = max(1, int(thickness * (1 - prog * 0.85)))
            
            # 颜色渐变
            fade = 1 - prog * 0.35
            seg_col = (int(color[0] * fade), int(color[1] * fade), int(color[2] * fade))
            pygame.draw.line(s, seg_col, points[i], points[i + 1], seg_thick)
        
        # 吸盘
        if suckers and len(points) > 4:
            for i in range(2, len(points) - 1, 2):
                prog = i / len(points)
                sucker_size = max(1, int(4 * (1 - prog)))
                
                # 吸盘位置偏移
                angle_rad = math.radians(base_angle)
                offset_x = math.cos(angle_rad + math.pi / 2) * 3
                offset_y = math.sin(angle_rad + math.pi / 2) * 3
                
                sucker_col = (color[0] // 2, color[1] // 2, color[2] // 2)
                pygame.draw.circle(s, sucker_col, 
                                 (int(points[i][0] + offset_x), int(points[i][1] + offset_y)), 
                                 sucker_size)
                pygame.draw.circle(s, (color[0] // 3, color[1] // 3, color[2] // 3),
                                 (int(points[i][0] + offset_x), int(points[i][1] + offset_y)),
                                 max(1, sucker_size - 1))


def _draw_writhing_mass(s, cx, cy, base_r, t, color, variation=0.3):
    """
    蠕动的肉块 - 不规则形态
    """
    points = []
    num_points = 16
    
    for i in range(num_points):
        angle = i * (2 * math.pi / num_points)
        # 多重扰动
        r = base_r * (1 + 
                     math.sin(t * 2 + i * 0.8) * variation + 
                     math.cos(t * 3 + i * 1.2) * variation * 0.5 +
                     math.sin(t * 1.5 + i * 2) * variation * 0.3)
        
        points.append((int(cx + math.cos(angle) * r), 
                      int(cy + math.sin(angle) * r)))
    
    if len(points) >= 3:
        pygame.draw.polygon(s, color, points)


# =============================================================================
#   [系列一：深渊之主] - 精细化独立绘制函数
# =============================================================================

def draw_cthulhu_default(s, cx, cy, w, h, t):
    """
    深渊之主·原初 - 经典克苏鲁章鱼头
    特点：章鱼形头颅 + 面部触须 + 巨大竖瞳 + 鳞片纹理
    """
    theme = get_cthulhu_theme("cthulhu_default")
    
    # === 深渊涟漪背景 ===
    for i in range(4):
        ripple_r = 48 - i * 10 + int(math.sin(t * 2) * 4)
        ripple_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.circle(ripple_surf, (*theme["body"], 40 - i * 10), (cx, cy), ripple_r)
        s.blit(ripple_surf, (0, 0))
    
    # === 章鱼形态头颅 ===
    head_points = []
    for i in range(24):
        angle = i * 15 * 0.01745
        # 上半部圆润，下半部收窄
        if i < 12:
            r = 32 + math.sin(t + i * 0.3) * 3
        else:
            r = 28 - (i - 12) * 1.2 + math.sin(t + i * 0.3) * 2
        
        head_points.append((int(cx + math.cos(angle) * r), 
                           int(cy - 5 + math.sin(angle) * r * 0.85)))
    
    pygame.draw.polygon(s, theme["body"], head_points)
    pygame.draw.polygon(s, theme["flesh"], head_points, 2)
    
    # === 头顶隆起 ===
    for i in range(3):
        bulge_x = cx - 8 + i * 8
        bulge_y = cy - 28 + abs(i - 1) * 3
        bulge_w = 18 - abs(i - 1) * 4
        bulge_h = 12 - abs(i - 1) * 2
        
        pygame.draw.ellipse(s, theme["flesh"], 
                          (bulge_x - bulge_w//2, bulge_y, bulge_w, bulge_h))
        pygame.draw.ellipse(s, theme["body"],
                          (bulge_x - bulge_w//2 + 2, bulge_y + 2, bulge_w - 4, bulge_h - 4))
    
    # === 巨眼 ===
    _draw_eldritch_eye(s, cx, cy - 5, 14, t, theme, vertical=True)
    
    # === 鳞片纹理 ===
    for row in range(3):
        for col in range(5):
            sx = cx - 20 + col * 10 + (row % 2) * 5 + math.sin(t + row + col) * 1.5
            sy = cy - 18 + row * 10
            
            # 鳞片弧线
            pygame.draw.arc(s, theme["accent"], (sx - 4, sy - 2, 8, 5), 0, math.pi, 1)
    
    # === 面部触须（5条主触须） ===
    tentacle_configs = [
        (cx - 15, cy + 10, 42, 155),
        (cx - 8, cy + 13, 38, 168),
        (cx, cy + 15, 40, 180),
        (cx + 8, cy + 13, 38, 192),
        (cx + 15, cy + 10, 42, 205),
    ]
    
    for ox, oy, length, angle in tentacle_configs:
        pulse_len = length + math.sin(t * 2) * 5
        _draw_tentacle(s, ox, oy, pulse_len, angle, t + angle * 0.01, theme["flesh"], 5, True)
    
    # === 额外小触须 ===
    for i in range(4):
        small_ox = cx - 12 + i * 8
        small_oy = cy + 8
        small_angle = 160 + i * 15
        _draw_tentacle(s, small_ox, small_oy, 20, small_angle, t + i, theme["body"], 2, False)
    
    # === 侧面纹路 ===
    for side in [-1, 1]:
        for i in range(3):
            line_x = cx + side * (20 + i * 4)
            line_y1 = cy - 10 + i * 8
            line_y2 = cy + 5 + i * 6
            pygame.draw.line(s, (*theme["accent"], 100), 
                           (int(line_x), int(line_y1)), 
                           (int(line_x - side * 5), int(line_y2)), 1)


def draw_cthulhu_abyss(s, cx, cy, w, h, t):
    """
    海沟巨兽·深渊 - 深海压强扭曲，生物发光
    特点：扭曲深海体 + 生物发光点 + 多眼 + 细长深海触角
    """
    theme = get_cthulhu_theme("cthulhu_abyss")
    
    # === 深海黑暗背景 ===
    pygame.draw.circle(s, theme["body"], (cx, cy), 50)
    
    # === 扭曲的身体（承受深海压力） ===
    body_points = []
    for i in range(24):
        angle = i * 15 * 0.01745
        # 不规则扭曲
        r = 35 + math.sin(i * 0.7) * 8 + math.cos(i * 1.3 + t) * 5 + math.sin(t * 2 + i * 0.5) * 3
        body_points.append((int(cx + math.cos(angle) * r), 
                           int(cy - 2 + math.sin(angle) * r * 0.85)))
    
    pygame.draw.polygon(s, theme["flesh"], body_points)
    
    # === 压力裂纹 ===
    for i in range(6):
        crack_angle = i * 60 * 0.01745 + t * 0.05
        crack_len = 25 + math.sin(t + i) * 5
        
        crack_points = [(cx, cy)]
        for j in range(5):
            dist = crack_len * (j + 1) / 5
            offset = math.sin(t * 2 + j * 1.5 + i) * 4
            cx_p = cx + math.cos(crack_angle) * dist + offset
            cy_p = cy + math.sin(crack_angle) * dist
            crack_points.append((int(cx_p), int(cy_p)))
        
        pygame.draw.lines(s, (*theme["eye_iris"], 60), False, crack_points, 1)
    
    # === 生物发光点 ===
    biolum_positions = [
        (cx - 20, cy - 10), (cx + 20, cy - 10),
        (cx - 25, cy + 5), (cx + 25, cy + 5),
        (cx - 15, cy + 20), (cx + 15, cy + 20),
        (cx - 5, cy - 25), (cx + 5, cy - 25),
        (cx, cy + 15),
    ]
    
    for i, (lx, ly) in enumerate(biolum_positions):
        flicker = abs(math.sin(t * 3 + i * 1.5))
        if flicker > 0.25:
            col = theme["eye_iris"] if i % 2 == 0 else theme["accent"]
            
            # 光晕
            glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            for g in range(3):
                glow_alpha = max(0, min(255, int(60 * flicker) - g * 15))
                if glow_alpha > 0:
                    pygame.draw.circle(glow_surf, (*col, glow_alpha), (10, 10), 8 - g * 2)
            pygame.draw.circle(glow_surf, col, (10, 10), 3)
            s.blit(glow_surf, (lx - 10, ly - 10))
    
    # === 多眼（深海适应） ===
    eye_configs = [
        (cx - 12, cy - 5, 9),
        (cx + 12, cy - 5, 9),
        (cx, cy - 15, 7),
        (cx - 22, cy + 3, 5),
        (cx + 22, cy + 3, 5),
        (cx - 8, cy + 12, 4),
        (cx + 8, cy + 12, 4),
    ]
    
    for ex, ey, size in eye_configs:
        _draw_eldritch_eye(s, ex, ey, size, t, theme, vertical=True)
    
    # === 细长深海触角 ===
    for i in range(8):
        angle = i * 45 + 22.5
        ox = cx + math.cos(math.radians(angle)) * 20
        oy = cy + math.sin(math.radians(angle)) * 15
        length = 25 + i * 3 + math.sin(t + i) * 5
        
        _draw_tentacle(s, ox, oy, length, angle, t + i * 0.5, theme["flesh"], 2, False)
        
        # 触角尖端发光
        tip_x = ox + math.cos(math.radians(angle)) * length
        tip_y = oy + math.sin(math.radians(angle)) * length
        if math.sin(t * 2 + i) > 0:
            pygame.draw.circle(s, theme["eye_iris"], (int(tip_x), int(tip_y)), 2)
    
    # === 深海气泡 ===
    for i in range(5):
        bubble_x = cx - 20 + i * 10 + math.sin(t * 0.5 + i) * 5
        bubble_y = cy + 35 - int((t * 15 + i * 20) % 50)
        bubble_r = 2 + i % 2
        pygame.draw.circle(s, (*theme["eye_iris"], 80), (int(bubble_x), int(bubble_y)), bubble_r, 1)


def draw_cthulhu_bloodmoon(s, cx, cy, w, h, t):
    """
    血祭狂潮·猩红 - 鲜血祭祀，邪教符文
    特点：血肉蠕动体 + 邪教符文环 + 血泪之眼 + 祭祀触手
    """
    theme = get_cthulhu_theme("cthulhu_bloodmoon")
    
    # === 血雾背景 ===
    for i in range(5):
        blood_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.circle(blood_surf, (*theme["flesh"], 35 - i * 6), (cx, cy), 52 - i * 8)
        s.blit(blood_surf, (0, 0))
    
    # === 蠕动的血肉体 ===
    _draw_writhing_mass(s, cx, cy, 32, t, theme["body"], 0.25)
    _draw_writhing_mass(s, cx, cy, 26, t * 0.8, theme["flesh"], 0.18)
    
    # === 邪教符文圆环 ===
    rune_r = 40 + int(math.sin(t * 2) * 3)
    
    # 双环
    pygame.draw.circle(s, theme["accent"], (cx, cy), rune_r, 2)
    pygame.draw.circle(s, theme["accent"], (cx, cy), rune_r - 6, 1)
    
    # 符文标记
    for i in range(8):
        angle = (i * 45 + t * 12) * 0.01745
        rx = cx + math.cos(angle) * rune_r
        ry = cy + math.sin(angle) * rune_r
        
        # 交替符文形状
        if i % 2 == 0:
            # 三角符文
            tri_pts = [
                (rx, ry - 5),
                (rx - 4, ry + 4),
                (rx + 4, ry + 4)
            ]
            pygame.draw.polygon(s, theme["accent"], tri_pts)
        else:
            # 圆形符文
            pygame.draw.circle(s, theme["accent"], (int(rx), int(ry)), 3)
            pygame.draw.circle(s, theme["body"], (int(rx), int(ry)), 2)
    
    # 内部五芒星
    star_r = rune_r - 15
    star_pts = []
    for i in range(5):
        angle = (i * 72 - 90 + t * 5) * 0.01745
        star_pts.append((int(cx + math.cos(angle) * star_r),
                        int(cy + math.sin(angle) * star_r)))
    
    # 连接五芒星
    for i in range(5):
        pygame.draw.line(s, (*theme["accent"], 150), 
                        star_pts[i], star_pts[(i + 2) % 5], 1)
    
    # === 血泪之眼 ===
    _draw_eldritch_eye(s, cx, cy - 3, 13, t, theme, vertical=True)
    
    # 血泪
    tear_y = cy + 10 + int((t * 25) % 35)
    tear_alpha = 255 - int((t * 25) % 35) * 6
    if tear_alpha > 0:
        pygame.draw.ellipse(s, (*theme["flesh"], tear_alpha), 
                          (cx - 3, tear_y, 6, 10))
    
    # 第二滴血泪（错开）
    tear_y2 = cy + 10 + int((t * 25 + 17) % 35)
    tear_alpha2 = 255 - int((t * 25 + 17) % 35) * 6
    if tear_alpha2 > 0:
        pygame.draw.ellipse(s, (*theme["flesh"], tear_alpha2),
                          (cx - 1, tear_y2, 4, 8))
    
    # === 祭祀触手 ===
    for i in range(4):
        angle = 45 + i * 90
        ox = cx + math.cos(math.radians(angle)) * 15
        oy = cy + math.sin(math.radians(angle)) * 12
        
        _draw_tentacle(s, ox, oy, 35, angle, t + i, theme["flesh"], 4, False)
    
    # === 血滴飞溅 ===
    for i in range(6):
        if math.sin(t * 3 + i * 1.2) > 0.7:
            splat_x = cx + math.cos(t + i * 1.5) * 35
            splat_y = cy + math.sin(t * 0.8 + i) * 30
            pygame.draw.circle(s, theme["flesh"], (int(splat_x), int(splat_y)), 2)


# =============================================================================
#   [系列二：虚空凝视] - 精细化独立绘制函数
# =============================================================================

def draw_cthulhu_void(s, cx, cy, w, h, t):
    """
    虚空之眼·虚无 - 空间裂隙，无数眼球窥视
    特点：纯黑虚空体 + 空间裂隙 + 11只眼球 + 重叠维度
    """
    theme = get_cthulhu_theme("cthulhu_void")
    
    # === 虚空黑洞背景 ===
    pygame.draw.circle(s, theme["body"], (cx, cy), 50)
    
    # 维度扭曲环
    for i in range(3):
        ring_r = 45 - i * 8
        ring_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (*theme["glow"], 40 - i * 12), (cx, cy), ring_r, 2)
        s.blit(ring_surf, (0, 0))
    
    # === 空间裂隙 ===
    for i in range(8):
        rift_angle = i * 45 * 0.01745 + t * 0.15
        rift_points = [(cx, cy)]
        
        for j in range(8):
            dist = 10 + j * 6
            # 裂隙扭曲
            offset = math.sin(j * 2.5 + t * 2) * 6 + math.cos(j * 1.8 + t * 1.5) * 4
            rx = cx + math.cos(rift_angle) * dist + math.cos(rift_angle + 1.57) * offset
            ry = cy + math.sin(rift_angle) * dist + math.sin(rift_angle + 1.57) * offset
            rift_points.append((int(rx), int(ry)))
        
        # 裂隙渐变
        for k in range(len(rift_points) - 1):
            alpha = 200 - k * 20
            pygame.draw.line(s, (*theme["accent"], max(50, alpha)), 
                           rift_points[k], rift_points[k + 1], 
                           max(1, 3 - k // 3))
    
    # === 虚空核心 ===
    _draw_writhing_mass(s, cx, cy, 28, t, theme["flesh"], 0.15)
    
    # 核心脉动
    pulse_r = 20 + int(math.sin(t * 3) * 4)
    pygame.draw.circle(s, theme["body"], (cx, cy), pulse_r)
    pygame.draw.circle(s, theme["accent"], (cx, cy), pulse_r, 1)
    
    # === 无数窥视之眼 ===
    eye_configs = [
        (cx, cy - 3, 11, True),       # 中央主眼
        (cx - 18, cy - 8, 7, True),   # 左上
        (cx + 18, cy - 8, 7, False),  # 右上
        (cx - 25, cy + 5, 5, True),   # 左侧
        (cx + 25, cy + 5, 5, False),  # 右侧
        (cx - 12, cy + 16, 5, True),  # 下左
        (cx + 12, cy + 16, 5, False), # 下右
        (cx - 8, cy - 18, 4, False),  # 顶左
        (cx + 8, cy - 18, 4, True),   # 顶右
        (cx - 20, cy + 18, 4, False), # 底左角
        (cx + 20, cy + 18, 4, True),  # 底右角
    ]
    
    for i, (ex, ey, size, vertical) in enumerate(eye_configs):
        # 眼球浮动
        float_x = math.sin(t * 1.5 + i * 0.8) * 2
        float_y = math.cos(t * 1.2 + i * 0.6) * 1.5
        _draw_eldritch_eye(s, int(ex + float_x), int(ey + float_y), size, t + i * 0.7, theme, vertical)
    
    # === 次元交界光芒 ===
    for i in range(6):
        if math.sin(t * 4 + i * 1.3) > 0.6:
            beam_angle = (i * 60 + t * 25) * 0.01745
            beam_len = 35 + math.sin(t * 2 + i) * 10
            
            beam_x = cx + math.cos(beam_angle) * beam_len
            beam_y = cy + math.sin(beam_angle) * beam_len
            pygame.draw.line(s, (*theme["glow"], 100), (cx, cy), (int(beam_x), int(beam_y)), 1)
            pygame.draw.circle(s, theme["glow"], (int(beam_x), int(beam_y)), 2)


def draw_cthulhu_starfall(s, cx, cy, w, h, t):
    """
    星之眷属·坠落 - 非欧几何，不可能图形
    特点：不可能三角 + 扭曲几何 + 星云眼 + 流星碎片
    """
    theme = get_cthulhu_theme("cthulhu_starfall")
    
    # === 星空背景 ===
    for i in range(20):
        star_x = cx - 40 + (i * 37) % 80
        star_y = cy - 45 + (i * 23) % 90
        
        # 星星闪烁
        if abs(math.sin(t * 3 + i * 1.2)) > 0.4:
            star_size = 1 + (i % 2)
            star_alpha = int(100 + math.sin(t * 2 + i) * 50)
            pygame.draw.circle(s, (*theme["accent"], star_alpha), (int(star_x), int(star_y)), star_size)
    
    # === 不可能三角（彭罗斯三角） ===
    # 外三角
    tri_size = 32
    tri_y_offset = -2
    outer_pts = [
        (cx, cy - tri_size + tri_y_offset),
        (cx + tri_size * 0.866, cy + tri_size * 0.5 + tri_y_offset),
        (cx - tri_size * 0.866, cy + tri_size * 0.5 + tri_y_offset)
    ]
    pygame.draw.polygon(s, theme["body"], outer_pts)
    pygame.draw.polygon(s, theme["accent"], outer_pts, 2)
    
    # 内三角（倒置）
    inner_size = 20
    inner_pts = [
        (cx, cy + inner_size * 0.6 + tri_y_offset),
        (cx - inner_size * 0.5, cy - inner_size * 0.3 + tri_y_offset),
        (cx + inner_size * 0.5, cy - inner_size * 0.3 + tri_y_offset)
    ]
    pygame.draw.polygon(s, theme["eye_iris"], inner_pts, 2)
    
    # 不可能连接线（造成视觉悖论）
    pygame.draw.line(s, theme["accent"], outer_pts[0], inner_pts[0], 1)
    pygame.draw.line(s, theme["accent"], outer_pts[1], inner_pts[1], 1)
    pygame.draw.line(s, theme["accent"], outer_pts[2], inner_pts[2], 1)
    
    # 中心交叉点
    pygame.draw.line(s, theme["accent"], outer_pts[0], (cx, cy + tri_y_offset), 1)
    pygame.draw.line(s, theme["eye_iris"], outer_pts[1], (cx - 5, cy - 5 + tri_y_offset), 1)
    pygame.draw.line(s, theme["eye_iris"], outer_pts[2], (cx + 5, cy - 5 + tri_y_offset), 1)
    
    # === 星云之眼 ===
    # 星云背景
    nebula_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    for ring in range(6):
        ring_angle = ring * 60 + t * 30
        ring_r = 12 - ring
        nebula_col = theme["eye_iris"] if ring % 2 == 0 else theme["accent"]
        rx = 15 + math.cos(math.radians(ring_angle)) * ring
        ry = 15 + math.sin(math.radians(ring_angle)) * ring
        pygame.draw.circle(nebula_surf, (*nebula_col, 100), (int(rx), int(ry)), ring_r)
    s.blit(nebula_surf, (cx - 15, cy - 18))
    
    # 核心眼睛
    pygame.draw.circle(s, (200, 190, 210), (cx, cy - 3), 10)
    
    # 旋转粒子
    for i in range(10):
        p_angle = (i * 36 + t * 50) * 0.01745
        p_r = 6 + math.sin(i + t * 3) * 2
        px = cx + math.cos(p_angle) * p_r
        py = cy - 3 + math.sin(p_angle) * p_r
        pygame.draw.circle(s, theme["eye_iris"], (int(px), int(py)), 1)
    
    # 竖瞳
    pupil_h = 12 + int(math.sin(t * 2) * 3)
    pygame.draw.ellipse(s, theme["eye_pupil"], (cx - 2, cy - 3 - pupil_h // 2, 4, pupil_h))
    pygame.draw.circle(s, (255, 255, 255), (cx - 3, cy - 7), 2)
    
    # === 流星碎片 ===
    for i in range(5):
        meteor_angle = math.radians(i * 72 + 36 + t * 8)
        orbit_r = 38 + math.sin(t * 2 + i) * 5
        
        mx = cx + math.cos(meteor_angle) * orbit_r
        my = cy + math.sin(meteor_angle) * orbit_r * 0.7
        
        # 不规则陨石
        meteor_pts = [
            (mx, my - 5),
            (mx + 4, my - 1),
            (mx + 3, my + 4),
            (mx - 2, my + 5),
            (mx - 4, my + 1),
            (mx - 3, my - 3)
        ]
        pygame.draw.polygon(s, theme["accent"], [(int(p[0]), int(p[1])) for p in meteor_pts])
        
        # 尾焰
        tail_len = 8 + math.sin(t * 3 + i) * 3
        tail_angle = meteor_angle + math.pi
        tx = mx + math.cos(tail_angle) * tail_len
        ty = my + math.sin(tail_angle) * tail_len * 0.7
        pygame.draw.line(s, (*theme["accent"], 150), (int(mx), int(my)), (int(tx), int(ty)), 2)


def draw_cthulhu_cosmos(s, cx, cy, w, h, t):
    """
    星际蠕虫·宇宙 - 星云蠕虫，无尽延伸
    特点：分节蠕虫体 + 星云纹理 + 巨口利齿 + 宇宙背景
    """
    theme = get_cthulhu_theme("cthulhu_cosmos")
    
    # === 星云背景 ===
    for i in range(4):
        nebula_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        nx = cx - 20 + i * 15 + math.sin(t * 0.3 + i) * 8
        ny = cy - 15 + i * 10 + math.cos(t * 0.2 + i) * 6
        
        col = theme["eye_iris"] if i % 2 == 0 else theme["accent"]
        pygame.draw.ellipse(nebula_surf, (*col, 30), (nx - 25, ny - 15, 50, 30))
        s.blit(nebula_surf, (0, 0))
    
    # === 蠕虫体节 ===
    segments = []
    for i in range(9):
        prog = i / 8
        # S形蜿蜒
        seg_x = cx - 30 + prog * 60 + math.sin(t * 2.2 + prog * 5) * 12
        seg_y = cy - 5 + math.sin(prog * math.pi) * 20 + math.cos(t * 1.8 + prog * 4) * 6
        seg_r = 14 - i * 1.2 + int(math.sin(t * 2) * 2)
        segments.append((int(seg_x), int(seg_y), max(4, int(seg_r))))
    
    # 绘制体节
    for i, (sx, sy, sr) in enumerate(segments):
        # 体节主体
        pygame.draw.circle(s, theme["flesh"], (sx, sy), sr)
        
        # 星云纹理环
        pygame.draw.circle(s, theme["eye_iris"], (sx, sy), sr, 1)
        
        # 内部光点
        if i < 6:
            glow_alpha = int(100 + math.sin(t * 3 + i) * 50)
            pygame.draw.circle(s, (*theme["accent"], glow_alpha), (sx, sy), max(1, sr - 4))
    
    # === 头部（第一节） ===
    head_x, head_y, head_r = segments[0]
    head_r = 16
    pygame.draw.circle(s, theme["flesh"], (head_x, head_y), head_r)
    
    # 头部纹理
    for ring in range(3):
        ring_r = head_r - ring * 3
        pygame.draw.circle(s, theme["eye_iris"], (head_x, head_y), ring_r, 1)
    
    # === 巨口 ===
    mouth_open = 10 + int(abs(math.sin(t * 2.5)) * 8)
    mouth_rect = (head_x - 10, head_y - mouth_open // 2, 20, mouth_open)
    pygame.draw.ellipse(s, theme["body"], mouth_rect)
    
    # 利齿
    teeth_count = 6
    for i in range(teeth_count):
        # 上排齿
        tooth_x = head_x - 8 + i * 3
        tooth_y_top = head_y - mouth_open // 2 + 2
        pygame.draw.polygon(s, theme["glow"], [
            (tooth_x, tooth_y_top),
            (tooth_x + 2, tooth_y_top + 5),
            (tooth_x - 1, tooth_y_top)
        ])
        
        # 下排齿
        tooth_y_bot = head_y + mouth_open // 2 - 2
        pygame.draw.polygon(s, theme["glow"], [
            (tooth_x, tooth_y_bot),
            (tooth_x + 2, tooth_y_bot - 5),
            (tooth_x - 1, tooth_y_bot)
        ])
    
    # === 头顶之眼 ===
    _draw_eldritch_eye(s, head_x, head_y - 12, 7, t, theme, vertical=True)
    
    # === 尾部能量 ===
    tail_x, tail_y, _ = segments[-1]
    for i in range(4):
        trail_angle = (i * 90 + t * 40) * 0.01745
        trail_len = 15 + math.sin(t * 2 + i) * 5
        tx = tail_x + math.cos(trail_angle) * trail_len
        ty = tail_y + math.sin(trail_angle) * trail_len
        pygame.draw.line(s, (*theme["accent"], 120), (tail_x, tail_y), (int(tx), int(ty)), 2)
    
    # === 漂浮粒子 ===
    for i in range(8):
        particle_angle = (i * 45 + t * 20) * 0.01745
        particle_dist = 40 + math.sin(t + i) * 8
        px = cx + math.cos(particle_angle) * particle_dist
        py = cy + math.sin(particle_angle) * particle_dist * 0.6
        
        if math.sin(t * 2 + i * 0.7) > 0:
            pygame.draw.circle(s, theme["accent"], (int(px), int(py)), 2)


# =============================================================================
#   [系列三：梦魇造物] - 精细化独立绘制函数
# =============================================================================

def draw_cthulhu_nightmare(s, cx, cy, w, h, t):
    """
    梦魇具现·噩梦 - 恐惧凝聚，扭曲肉块
    特点：蠕动恐惧体 + 扭曲肢体 + 闪烁恐惧眼 + 尖叫之口
    """
    theme = get_cthulhu_theme("cthulhu_nightmare")
    
    # === 恐惧雾气 ===
    for i in range(6):
        fog_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        fx = cx - 20 + i * 12 + math.sin(t + i) * 12
        fy = cy - 15 + i * 8 + math.cos(t * 0.7 + i) * 10
        pygame.draw.ellipse(fog_surf, (*theme["body"], 55 - i * 8), (fx - 22, fy - 16, 44, 32))
        s.blit(fog_surf, (0, 0))
    
    # === 蠕动恐惧体 ===
    _draw_writhing_mass(s, cx, cy - 3, 34, t, theme["flesh"], 0.32)
    _draw_writhing_mass(s, cx, cy - 3, 26, t * 1.3, theme["body"], 0.25)
    _draw_writhing_mass(s, cx, cy - 3, 18, t * 0.8, theme["eye_pupil"], 0.2)
    
    # === 扭曲肢体 ===
    limb_configs = [
        (cx - 25, cy - 8, 28, -145),   # 左上
        (cx + 25, cy - 8, 28, -35),    # 右上
        (cx - 28, cy + 15, 24, 155),   # 左下
        (cx + 28, cy + 15, 24, 25),    # 右下
        (cx - 15, cy - 22, 20, -100),  # 顶左
        (cx + 15, cy - 22, 20, -80),   # 顶右
    ]
    
    for lx, ly, length, angle in limb_configs:
        points = [(lx, ly)]
        for j in range(6):
            dist = length * (j + 1) / 6
            # 多重扭曲
            twist = math.sin(t * 3 + j * 1.2) * 10 + math.cos(t * 2.5 + j) * 5
            px = lx + math.cos(math.radians(angle)) * dist + twist
            py = ly + math.sin(math.radians(angle)) * dist + math.sin(t + j) * 3
            points.append((int(px), int(py)))
        
        # 绘制肢体
        for k in range(len(points) - 1):
            thick = max(1, 4 - k // 2)
            pygame.draw.line(s, theme["flesh"], points[k], points[k + 1], thick)
        
        # 肢端血红爪
        pygame.draw.circle(s, theme["accent"], points[-1], 4)
        pygame.draw.circle(s, theme["eye_pupil"], points[-1], 2)
    
    # === 闪烁恐惧之眼 ===
    eye_configs = [
        (cx - 12, cy - 10, 9, True),   # 左眼
        (cx + 12, cy - 10, 9, False),  # 右眼
        (cx, cy + 5, 11, True),        # 中央大眼
        (cx - 20, cy + 2, 5, True),    # 左侧小眼
        (cx + 20, cy + 2, 5, False),   # 右侧小眼
    ]
    
    for i, (ex, ey, size, vertical) in enumerate(eye_configs):
        # 闪烁效果
        visibility = math.sin(t * 2.2 + i * 1.5)
        if visibility > -0.4:
            alpha_mult = min(1, (visibility + 0.4) * 1.5)
            _draw_eldritch_eye(s, ex, ey, size, t + i * 0.8, theme, vertical)
    
    # === 尖叫之口 ===
    mouth_y = cy + 18
    mouth_open = 8 + int(abs(math.sin(t * 4)) * 6)
    
    # 口腔
    pygame.draw.ellipse(s, theme["eye_pupil"], 
                       (cx - 10, mouth_y - mouth_open // 2, 20, mouth_open))
    
    # 内部深渊
    inner_open = max(2, mouth_open - 4)
    pygame.draw.ellipse(s, (0, 0, 0), 
                       (cx - 6, mouth_y - inner_open // 2, 12, inner_open))
    
    # 尖牙
    for i in range(5):
        tooth_x = cx - 8 + i * 4
        # 上牙
        pygame.draw.polygon(s, theme["glow"], [
            (tooth_x, mouth_y - mouth_open // 2),
            (tooth_x + 2, mouth_y - mouth_open // 2 + 5),
            (tooth_x - 1, mouth_y - mouth_open // 2)
        ])
        # 下牙
        pygame.draw.polygon(s, theme["glow"], [
            (tooth_x, mouth_y + mouth_open // 2),
            (tooth_x + 2, mouth_y + mouth_open // 2 - 4),
            (tooth_x - 1, mouth_y + mouth_open // 2)
        ])
    
    # === 恐惧粒子 ===
    for i in range(8):
        if math.sin(t * 3.5 + i * 1.1) > 0.5:
            px = cx + math.cos(t + i * 0.9) * (30 + i * 3)
            py = cy + math.sin(t * 0.7 + i) * (25 + i * 2)
            pygame.draw.circle(s, theme["accent"], (int(px), int(py)), 2)


def draw_cthulhu_aurora(s, cx, cy, w, h, t):
    """
    极光异象·流光 - 诡异光谱变换，形态不稳定
    特点：色彩流动极光 + 不稳定身体 + 变色之眼 + 光谱触手
    """
    theme = get_cthulhu_theme("cthulhu_aurora")
    
    def get_aurora_color(offset):
        """生成极光渐变色"""
        h = (t * 0.4 + offset) % 3
        if h < 1:
            return (int(255 * (1 - h)), int(255 * h), int(100 + 50 * h))
        elif h < 2:
            return (int(100 + 50 * (2 - h)), int(255 * (2 - h)), int(255 * (h - 1)))
        else:
            return (int(255 * (h - 2)), int(100 + 50 * (3 - h)), int(255 * (3 - h)))
    
    # === 极光波浪背景 ===
    for wave in range(6):
        wave_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        points = []
        for i in range(28):
            px = cx - 50 + i * 4
            py = cy - 30 + wave * 12 + math.sin(t * 2.5 + i * 0.35 + wave * 0.8) * 8
            points.append((px, int(py)))
        
        aurora_col = get_aurora_color(wave * 0.4)
        pygame.draw.lines(wave_surf, (*aurora_col, 90 - wave * 12), False, points, 3)
        s.blit(wave_surf, (0, 0))
    
    # === 不稳定形态身体 ===
    body_points = []
    for i in range(20):
        angle = i * 18 * 0.01745
        # 剧烈波动
        r = 30 + math.sin(t * 4.5 + i * 0.6) * 10 + math.cos(t * 3 + i * 0.8) * 6
        body_points.append((int(cx + math.cos(angle) * r), 
                           int(cy + math.sin(angle) * r * 0.9)))
    
    # 多层渐变填充
    pygame.draw.polygon(s, get_aurora_color(0), body_points)
    pygame.draw.polygon(s, get_aurora_color(1), body_points, 3)
    pygame.draw.polygon(s, get_aurora_color(2), body_points, 1)
    
    # === 内部光核 ===
    for ring in range(4):
        ring_r = 20 - ring * 4 + int(math.sin(t * 3) * 3)
        ring_col = get_aurora_color(ring * 0.3)
        pygame.draw.circle(s, (*ring_col, 150 - ring * 30), (cx, cy), ring_r)
    
    # === 变色之眼 ===
    eye_col = get_aurora_color(t * 0.5)
    
    # 眼白
    pygame.draw.ellipse(s, (220, 215, 230), (cx - 13, cy - 10, 26, 16))
    
    # 虹膜
    iris_wobble_x = math.sin(t * 1.8) * 3
    iris_wobble_y = math.cos(t * 1.5) * 2
    pygame.draw.circle(s, eye_col, (int(cx + iris_wobble_x), int(cy - 2 + iris_wobble_y)), 9)
    
    # 瞳孔
    pupil_size = 3 + int(abs(math.sin(t * 3.5)) * 3)
    pygame.draw.ellipse(s, (20, 20, 30), 
                       (int(cx - pupil_size // 2 + iris_wobble_x), 
                        int(cy - 8 + iris_wobble_y), 
                        pupil_size, 12))
    
    # 高光
    pygame.draw.circle(s, (255, 255, 255), (cx - 4, cy - 5), 2)
    
    # === 光谱触手 ===
    for i in range(6):
        angle = i * 60 + t * 18
        ox = cx + math.cos(math.radians(angle)) * 18
        oy = cy + math.sin(math.radians(angle)) * 14
        
        tentacle_col = get_aurora_color(i * 0.5)
        _draw_tentacle(s, ox, oy, 32 + math.sin(t + i) * 6, angle, t + i * 0.7, tentacle_col, 3, False)
    
    # === 漂浮光点 ===
    for i in range(10):
        float_angle = (i * 36 + t * 25) * 0.01745
        float_dist = 35 + math.sin(t * 2 + i) * 8
        fx = cx + math.cos(float_angle) * float_dist
        fy = cy + math.sin(float_angle) * float_dist * 0.7
        
        point_col = get_aurora_color(i * 0.2)
        pygame.draw.circle(s, point_col, (int(fx), int(fy)), 2 + i % 2)


def draw_cthulhu_eldritch(s, cx, cy, w, h, t):
    """
    远古遗骸·古神 - 骨骼化遗体，符文刻印
    特点：骷髅外壳 + 空洞眼眶发光 + 古老符文 + 腐朽气息
    """
    theme = get_cthulhu_theme("cthulhu_eldritch")
    
    # === 腐朽雾气 ===
    for i in range(4):
        decay_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        dx = cx - 15 + i * 15 + math.sin(t * 0.4 + i) * 10
        dy = cy - 10 + math.cos(t * 0.3 + i) * 8
        pygame.draw.ellipse(decay_surf, (*theme["flesh"], 40 - i * 8), (dx - 25, dy - 18, 50, 36))
        s.blit(decay_surf, (0, 0))
    
    # === 骷髅外壳 ===
    skull_points = [
        (cx, cy - 32),      # 顶
        (cx + 20, cy - 22), # 右上
        (cx + 28, cy - 5),  # 右侧上
        (cx + 25, cy + 15), # 右侧下
        (cx + 12, cy + 28), # 右下
        (cx, cy + 32),      # 底
        (cx - 12, cy + 28), # 左下
        (cx - 25, cy + 15), # 左侧下
        (cx - 28, cy - 5),  # 左侧上
        (cx - 20, cy - 22), # 左上
    ]
    
    pygame.draw.polygon(s, theme["body"], skull_points)
    pygame.draw.polygon(s, theme["flesh"], skull_points, 2)
    
    # 头骨裂纹
    crack_lines = [
        [(cx - 5, cy - 30), (cx - 8, cy - 20), (cx - 12, cy - 12)],
        [(cx + 3, cy - 28), (cx + 10, cy - 18), (cx + 8, cy - 8)],
        [(cx - 20, cy + 5), (cx - 15, cy + 12), (cx - 10, cy + 18)],
        [(cx + 20, cy + 5), (cx + 15, cy + 12), (cx + 10, cy + 18)],
    ]
    
    for crack in crack_lines:
        pygame.draw.lines(s, theme["accent"], False, crack, 1)
    
    # === 空洞眼眶 ===
    eye_positions = [(cx - 12, cy - 8), (cx + 12, cy - 8)]
    
    for ex, ey in eye_positions:
        # 眼眶
        pygame.draw.ellipse(s, theme["eye_pupil"], (ex - 10, ey - 12, 20, 24))
        
        # 内部发光
        glow_phase = abs(math.sin(t * 1.8))
        if glow_phase > 0.25:
            glow_alpha = int(180 * glow_phase)
            glow_surf = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*theme["accent"], glow_alpha), (8, 8), 6)
            pygame.draw.circle(glow_surf, theme["accent"], (8, 8), 3)
            s.blit(glow_surf, (ex - 8, ey - 6))
    
    # === 鼻腔 ===
    nose_pts = [
        (cx - 3, cy + 2),
        (cx, cy - 3),
        (cx + 3, cy + 2),
        (cx, cy + 10)
    ]
    pygame.draw.polygon(s, theme["eye_pupil"], nose_pts)
    
    # === 牙齿 ===
    for i in range(7):
        tooth_x = cx - 12 + i * 4
        tooth_w = 3
        tooth_h = 8 + (i % 2) * 2
        pygame.draw.rect(s, theme["flesh"], (tooth_x, cy + 18, tooth_w, tooth_h))
        pygame.draw.rect(s, theme["accent"], (tooth_x, cy + 18, tooth_w, tooth_h), 1)
    
    # === 古老符文 ===
    rune_positions = [
        (cx - 30, cy - 15, "triangle"),
        (cx + 30, cy - 15, "circle"),
        (cx - 25, cy + 20, "circle"),
        (cx + 25, cy + 20, "triangle"),
        (cx, cy - 38, "star"),
        (cx, cy + 38, "star"),
    ]
    
    for rx, ry, shape in rune_positions:
        glow = abs(math.sin(t * 1.5 + rx * 0.1))
        rune_col = (*theme["accent"], int(100 + 100 * glow))
        
        if shape == "triangle":
            pygame.draw.polygon(s, rune_col, [
                (rx, ry - 5), (rx - 5, ry + 4), (rx + 5, ry + 4)
            ])
        elif shape == "circle":
            pygame.draw.circle(s, theme["accent"], (rx, ry), 5, 1)
            pygame.draw.circle(s, rune_col[:3], (rx, ry), 3)
        else:  # star
            for j in range(5):
                star_angle = j * 72 - 90
                sx = rx + math.cos(math.radians(star_angle)) * 5
                sy = ry + math.sin(math.radians(star_angle)) * 5
                pygame.draw.line(s, theme["accent"], (rx, ry), (int(sx), int(sy)), 1)
    
    # === 符文能量连线 ===
    if math.sin(t * 2) > 0.3:
        for i in range(0, len(rune_positions) - 1, 2):
            pygame.draw.line(s, (*theme["accent"], 80),
                           (rune_positions[i][0], rune_positions[i][1]),
                           (rune_positions[i + 1][0], rune_positions[i + 1][1]), 1)


# =============================================================================
#   [系列四：终末启示] - 精细化独立绘制函数
# =============================================================================

def draw_cthulhu_eclipse(s, cx, cy, w, h, t):
    """
    黑日降临·日蚀 - 日冕包裹的黑洞核心
    特点：日冕火焰 + 黑洞核心 + 日珥触手 + 吞噬之眼
    """
    theme = get_cthulhu_theme("cthulhu_eclipse")
    
    # === 日冕背景 ===
    for i in range(6):
        corona_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        corona_r = 52 - i * 6 + int(math.sin(t * 2) * 3)
        pygame.draw.circle(corona_surf, (*theme["accent"], 65 - i * 10), (cx, cy), corona_r)
        s.blit(corona_surf, (0, 0))
    
    # === 日冕火焰触手 ===
    for i in range(14):
        flame_angle = i * 25.7 + t * 12
        base_length = 38 + (i % 3) * 8
        flare_length = base_length + math.sin(t * 3.5 + i * 0.9) * 12
        
        flame_points = [(cx, cy)]
        for j in range(7):
            dist = 18 + flare_length * (j / 6)
            wave = math.sin(t * 4.5 + j * 0.6 + i) * 6
            fx = cx + math.cos(math.radians(flame_angle)) * dist + wave
            fy = cy + math.sin(math.radians(flame_angle)) * dist
            flame_points.append((int(fx), int(fy)))
        
        # 渐变颜色
        for k in range(len(flame_points) - 1):
            if k < 2:
                col = theme["glow"]
            elif k < 4:
                col = theme["accent"]
            else:
                col = theme["eye_iris"]
            
            thick = max(1, 5 - k)
            pygame.draw.line(s, col, flame_points[k], flame_points[k + 1], thick)
    
    # === 黑洞核心 ===
    pygame.draw.circle(s, theme["body"], (cx, cy), 26)
    
    # 事件视界
    pygame.draw.circle(s, theme["accent"], (cx, cy), 28, 2)
    pygame.draw.circle(s, theme["eye_iris"], (cx, cy), 30, 1)
    
    # 核心旋涡
    for i in range(5):
        spiral_angle = (i * 72 + t * 40) * 0.01745
        spiral_r = 12 + i * 3
        sx = cx + math.cos(spiral_angle) * spiral_r * 0.6
        sy = cy + math.sin(spiral_angle) * spiral_r * 0.5
        pygame.draw.arc(s, theme["flesh"], 
                       (int(sx) - 8, int(sy) - 5, 16, 10),
                       spiral_angle, spiral_angle + 2, 1)
    
    # === 吞噬之眼 ===
    # 眼眶深渊
    pygame.draw.ellipse(s, theme["flesh"], (cx - 12, cy - 9, 24, 18))
    
    # 虹膜（火焰色）
    iris_pulse = abs(math.sin(t * 2)) * 3
    pygame.draw.circle(s, theme["accent"], (cx, cy - 1), int(8 + iris_pulse))
    
    # 瞳孔（黑洞）
    pygame.draw.circle(s, theme["body"], (cx, cy - 1), 4)
    
    # 高光
    pygame.draw.circle(s, theme["glow"], (cx - 4, cy - 4), 2)
    
    # === 日珥爆发 ===
    for i in range(4):
        if math.sin(t * 2.5 + i * 1.5) > 0.4:
            burst_angle = (i * 90 + 45 + t * 8) * 0.01745
            burst_len = 45 + math.sin(t * 3 + i) * 10
            
            bx = cx + math.cos(burst_angle) * burst_len
            by = cy + math.sin(burst_angle) * burst_len
            
            # 弧形日珥
            pygame.draw.arc(s, theme["accent"],
                          (int(cx - burst_len * 0.7), int(cy - burst_len * 0.7),
                           int(burst_len * 1.4), int(burst_len * 1.4)),
                          burst_angle - 0.3, burst_angle + 0.3, 3)


def draw_cthulhu_dreamland(s, cx, cy, w, h, t):
    """
    梦境彼岸·幻梦 - 迷幻空间，虚实交替
    特点：多层迷雾 + 虚影重叠 + 闪烁之眼 + 漂浮符文
    """
    theme = get_cthulhu_theme("cthulhu_dreamland")
    
    # === 梦境迷雾 ===
    for i in range(7):
        mist_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        mx = cx - 25 + i * 12 + math.sin(t * 0.45 + i * 0.8) * 18
        my = cy - 10 + math.cos(t * 0.35 + i) * 22
        
        mist_col = theme["eye_iris"] if i % 2 == 0 else theme["accent"]
        pygame.draw.ellipse(mist_surf, (*mist_col, 45 - i * 5), (mx - 22, my - 16, 44, 32))
        s.blit(mist_surf, (0, 0))
    
    # === 虚影身体（多重叠加） ===
    for ghost in range(4):
        offset_x = math.sin(t * 2.2 + ghost * 2.5) * (5 + ghost * 2)
        offset_y = math.cos(t * 1.7 + ghost * 2) * (4 + ghost * 1.5)
        
        ghost_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        ghost_alpha = 200 - ghost * 45
        
        ghost_points = []
        for i in range(16):
            angle = i * 22.5 * 0.01745
            r = 28 - ghost * 4 + math.sin(t * 2 + i * 0.5 + ghost) * 5
            gx = cx + offset_x + math.cos(angle) * r
            gy = cy + offset_y + math.sin(angle) * r * 0.85
            ghost_points.append((int(gx), int(gy)))
        
        if len(ghost_points) >= 3:
            pygame.draw.polygon(ghost_surf, (*theme["flesh"], ghost_alpha), ghost_points)
        s.blit(ghost_surf, (0, 0))
    
    # === 实体核心 ===
    core_points = []
    for i in range(16):
        angle = i * 22.5 * 0.01745
        r = 22 + math.sin(t * 2.5 + i * 0.6) * 4
        core_points.append((int(cx + math.cos(angle) * r), 
                           int(cy + math.sin(angle) * r * 0.85)))
    
    pygame.draw.polygon(s, theme["body"], core_points)
    pygame.draw.polygon(s, theme["accent"], core_points, 2)
    
    # === 闪烁之眼 ===
    eye_configs = [
        (cx - 10, cy - 5, 8, 0),
        (cx + 10, cy - 5, 8, 1),
        (cx, cy + 8, 6, 2),
    ]
    
    for ex, ey, size, phase in eye_configs:
        visibility = math.sin(t * 2.3 + phase * 1.8)
        
        if visibility > -0.2:
            fade = min(1, (visibility + 0.2) * 1.2)
            
            # 眼白
            sclera_col = (*theme["glow"], int(200 * fade))
            pygame.draw.ellipse(s, sclera_col, 
                              (ex - size, ey - int(size * 0.6), size * 2, int(size * 1.2)))
            
            # 虹膜
            wobble = math.sin(t * 1.5 + phase) * 2
            iris_col = (*theme["accent"], int(255 * fade))
            pygame.draw.circle(s, iris_col, (int(ex + wobble), ey), int(size * 0.5))
            
            # 瞳孔
            pupil_col = (*theme["body"], int(255 * fade))
            pygame.draw.ellipse(s, pupil_col, 
                              (int(ex - 1 + wobble), int(ey - size * 0.35), 2, int(size * 0.7)))
    
    # === 漂浮符文 ===
    for i in range(5):
        rune_angle = (i * 72 + t * 15) * 0.01745
        rune_dist = 35 + math.sin(t * 0.8 + i) * 8
        
        rx = cx + math.cos(rune_angle) * rune_dist
        ry = cy + math.sin(rune_angle) * rune_dist * 0.7
        
        # 旋转三角符文
        rot = t * 2 + i * 1.2
        tri_pts = []
        for j in range(3):
            tri_angle = rot + j * 2.094
            tx = rx + math.cos(tri_angle) * 5
            ty = ry + math.sin(tri_angle) * 5
            tri_pts.append((int(tx), int(ty)))
        
        pygame.draw.polygon(s, theme["glow"], tri_pts, 1)
        
        # 中心点
        if math.sin(t * 3 + i) > 0.3:
            pygame.draw.circle(s, theme["accent"], (int(rx), int(ry)), 2)
    
    # === 梦境粒子 ===
    for i in range(12):
        particle_prog = ((t * 0.5 + i * 0.3) % 1)
        
        # 螺旋上升
        spiral_angle = particle_prog * math.pi * 4 + i * 0.5
        spiral_r = 20 + particle_prog * 25
        
        px = cx + math.cos(spiral_angle) * spiral_r
        py = cy + 30 - particle_prog * 60
        
        if 0.1 < particle_prog < 0.9:
            alpha = int(150 * (1 - abs(particle_prog - 0.5) * 2))
            pygame.draw.circle(s, (*theme["accent"], alpha), (int(px), int(py)), 2)


def draw_cthulhu_primordial(s, cx, cy, w, h, t):
    """
    原初混沌·太初 - 不定形原始生命
    特点：混沌变形体 + 创世火花 + 分裂眼 + 原生伪足
    """
    theme = get_cthulhu_theme("cthulhu_primordial")
    
    # === 混沌团块（多层叠加） ===
    for blob in range(6):
        blob_cx = cx + math.sin(t * 0.35 + blob * 0.9) * 12
        blob_cy = cy + math.cos(t * 0.45 + blob * 0.7) * 10
        blob_r = 38 - blob * 5
        
        blob_points = []
        for i in range(14):
            angle = i * (2 * math.pi / 14)
            # 极度不规则
            r_var = blob_r * (0.55 + 
                             math.sin(t * 1.2 + i * 0.6 + blob) * 0.35 + 
                             math.cos(t * 1.8 + i * 0.9 + blob * 0.5) * 0.28 +
                             math.sin(t * 0.7 + i * 1.2) * 0.15)
            
            blob_points.append((int(blob_cx + math.cos(angle) * r_var), 
                               int(blob_cy + math.sin(angle) * r_var)))
        
        col = theme["body"] if blob % 2 == 0 else theme["flesh"]
        if len(blob_points) >= 3:
            pygame.draw.polygon(s, col, blob_points)
    
    # === 混沌内核 ===
    core_r = 18 + int(math.sin(t * 2.5) * 5)
    _draw_writhing_mass(s, cx, cy, core_r, t * 1.3, theme["eye_pupil"], 0.25)
    
    # === 创世火花 ===
    for i in range(10):
        spark_phase = math.sin(t * 2.5 + i * 0.85)
        if spark_phase > 0.4:
            # 随机分布
            spark_x = cx - 35 + (i * 17 + int(t * 5)) % 70
            spark_y = cy - 35 + (i * 23 + int(t * 3)) % 70
            
            spark_size = 2 + int((spark_phase - 0.4) * 4)
            pygame.draw.circle(s, theme["glow"], (int(spark_x), int(spark_y)), spark_size)
            
            # 火花射线
            for j in range(4):
                ray_angle = j * 90 + t * 30
                ray_len = spark_size * 2
                rx = spark_x + math.cos(math.radians(ray_angle)) * ray_len
                ry = spark_y + math.sin(math.radians(ray_angle)) * ray_len
                pygame.draw.line(s, theme["glow"], 
                               (int(spark_x), int(spark_y)), 
                               (int(rx), int(ry)), 1)
    
    # === 分裂眼睛（数量变化） ===
    num_eyes = 3 + int(abs(math.sin(t * 0.6)) * 4)
    
    for i in range(num_eyes):
        eye_angle = t * 0.35 + i * (2 * math.pi / num_eyes)
        eye_dist = 12 + abs(math.sin(t * 0.8 + i)) * 12
        
        ex = cx + math.cos(eye_angle) * eye_dist
        ey = cy + math.sin(eye_angle) * eye_dist * 0.75
        
        # 眼睛大小变化
        eye_size = 5 + int(abs(math.cos(t * 0.9 + i * 0.8)) * 5)
        
        # 眼白
        pygame.draw.ellipse(s, theme["glow"], 
                          (int(ex - eye_size), int(ey - eye_size * 0.6), 
                           eye_size * 2, int(eye_size * 1.2)))
        
        # 瞳孔（竖瞳）
        pupil_w = max(2, int(eye_size * 0.3))
        pupil_h = int(eye_size * 0.9)
        pygame.draw.ellipse(s, theme["eye_pupil"], 
                          (int(ex - pupil_w // 2), int(ey - pupil_h // 2), 
                           pupil_w, pupil_h))
    
    # === 原生伪足 ===
    for i in range(7):
        foot_base_angle = i * 51.4 + t * 18
        
        # 伸缩动画
        extend = 0.4 + abs(math.sin(t * 2.2 + i * 1.1)) * 0.6
        foot_length = 35 * extend
        
        foot_ox = cx + math.cos(math.radians(foot_base_angle)) * 15
        foot_oy = cy + math.sin(math.radians(foot_base_angle)) * 12
        
        foot_points = [(int(foot_ox), int(foot_oy))]
        for j in range(6):
            dist = foot_length * (j + 1) / 6
            wave = math.sin(t * 3.5 + j * 0.8 + i) * 10
            
            fx = foot_ox + math.cos(math.radians(foot_base_angle)) * dist + wave
            fy = foot_oy + math.sin(math.radians(foot_base_angle)) * dist
            foot_points.append((int(fx), int(fy)))
        
        # 绘制伪足
        for k in range(len(foot_points) - 1):
            thick = max(1, 5 - k)
            pygame.draw.line(s, theme["accent"], foot_points[k], foot_points[k + 1], thick)
        
        # 末端膨大
        if extend > 0.6:
            pygame.draw.circle(s, theme["flesh"], foot_points[-1], 3)
    
    # === 原初气泡 ===
    for i in range(6):
        bubble_prog = ((t * 0.25 + i * 0.18) % 1)
        
        bubble_x = cx - 25 + i * 10 + math.sin(t * 0.6 + i) * 6
        bubble_y = cy + 35 - bubble_prog * 70
        bubble_r = 2 + (i % 3) + int((1 - abs(bubble_prog - 0.5) * 2) * 2)
        
        if 0.05 < bubble_prog < 0.95:
            pygame.draw.circle(s, theme["glow"], (int(bubble_x), int(bubble_y)), bubble_r, 1)


# =============================================================================
#   分发器与公共接口
# =============================================================================

# 渲染函数映射表
_CTHULHU_RENDERERS = {
    "cthulhu_default": draw_cthulhu_default,
    "cthulhu_abyss": draw_cthulhu_abyss,
    "cthulhu_bloodmoon": draw_cthulhu_bloodmoon,
    "cthulhu_void": draw_cthulhu_void,
    "cthulhu_starfall": draw_cthulhu_starfall,
    "cthulhu_cosmos": draw_cthulhu_cosmos,
    "cthulhu_nightmare": draw_cthulhu_nightmare,
    "cthulhu_aurora": draw_cthulhu_aurora,
    "cthulhu_eldritch": draw_cthulhu_eldritch,
    "cthulhu_eclipse": draw_cthulhu_eclipse,
    "cthulhu_dreamland": draw_cthulhu_dreamland,
    "cthulhu_primordial": draw_cthulhu_primordial,
}


def draw_cthulhu(surface, style, cx, cy, w, h, t):
    """
    克苏鲁涂装绘制主入口
    
    参数:
        surface: pygame Surface 绘制目标
        style: 涂装风格名称 (如 "cthulhu_default", "cthulhu_void" 等)
        cx, cy: 中心坐标
        w, h: 绘制区域宽高
        t: 动画时间参数
    """
    renderer = _CTHULHU_RENDERERS.get(style, draw_cthulhu_default)
    renderer(surface, cx, cy, w, h, t)


def render_cthulhu_skin(surface, color, model_style, t, pid, static):
    """
    渲染克苏鲁涂装入口（兼容 base.py 调用）
    
    参数:
        surface: pygame Surface 绘制目标
        color: 颜色参数（未使用，保持接口兼容）
        model_style: 涂装风格名称
        t: 时间参数
        pid: 机体ID（未使用）
        static: 是否静态渲染
        
    返回:
        pygame.Surface 或 None
    """
    if not is_cthulhu_style(model_style):
        return None
    
    frame = int(t * 60) if not static else 0
    draw_cthulhu(surface, model_style, 60, 60, 120, 120, frame * 0.05)
    return surface


def _render_cthulhu_base(s, t, pulse):
    """
    基础克苏鲁机体渲染（兼容 base.py 中 pid=="cthulhu" 调用）
    """
    cx, cy = 60, 60
    theme = get_cthulhu_theme("cthulhu_default")
    
    # === 深渊涟漪背景 ===
    for i in range(4):
        ripple_r = 48 - i * 10 + int(pulse * 8)
        ripple_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(ripple_surf, (*theme["body"], 40 - i * 10), (cx, cy), ripple_r)
        s.blit(ripple_surf, (0, 0))
    
    # === 章鱼形态头颅 ===
    head_points = []
    for i in range(24):
        angle = i * 15 * 0.01745
        if i < 12:
            r = 32 + math.sin(t + i * 0.3) * 3
        else:
            r = 28 - (i - 12) * 1.2 + math.sin(t + i * 0.3) * 2
        head_points.append((int(cx + math.cos(angle) * r), 
                           int(cy - 5 + math.sin(angle) * r * 0.85)))
    
    pygame.draw.polygon(s, theme["body"], head_points)
    pygame.draw.polygon(s, theme["flesh"], head_points, 2)
    
    # === 头顶隆起 ===
    for i in range(3):
        bulge_x = cx - 8 + i * 8
        bulge_y = cy - 28 + abs(i - 1) * 3
        bulge_w = 18 - abs(i - 1) * 4
        bulge_h = 12 - abs(i - 1) * 2
        pygame.draw.ellipse(s, theme["flesh"], 
                          (bulge_x - bulge_w//2, bulge_y, bulge_w, bulge_h))
    
    # === 巨眼 ===
    _draw_eldritch_eye(s, cx, cy - 5, 14, t, theme, vertical=True)
    
    # === 面部触须 ===
    tentacle_configs = [
        (cx - 15, cy + 10, 42, 155),
        (cx - 8, cy + 13, 38, 168),
        (cx, cy + 15, 40, 180),
        (cx + 8, cy + 13, 38, 192),
        (cx + 15, cy + 10, 42, 205),
    ]
    
    for ox, oy, length, angle in tentacle_configs:
        pulse_len = length + pulse * 8
        _draw_tentacle(s, ox, oy, pulse_len, angle, t + angle * 0.01, theme["flesh"], 5, True)
    
    # === 鳞片纹理 ===
    for row in range(3):
        for col in range(5):
            sx = cx - 20 + col * 10 + (row % 2) * 5 + math.sin(t + row + col) * 1.5
            sy = cy - 18 + row * 10
            pygame.draw.arc(s, theme["accent"], (sx - 4, sy - 2, 8, 5), 0, math.pi, 1)

