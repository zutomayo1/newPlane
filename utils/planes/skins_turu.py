# -*- coding: utf-8 -*-
"""
巨石核拳·图鲁 (Stone-Core TURU) 机体涂装渲染模块

设计理念：
- 核心元素：远古岩石巨人、熔岩核心、重型石拳
- 机体形态：厚重岩石躯体，巨大石拳，发光核心眼
- 视觉效果：粗犷岩石质感，裂纹发光，蓄力指示器
- 特殊机制：岩石装甲模式切换，4段蓄力攻击
"""
import pygame
import math

# =============================================================================
#   图鲁涂装样式列表 (12款)
# =============================================================================

TURU_STYLES = [
    "turu_default",    # 岩核原型 - 橙色熔岩核心
    "turu_magma",      # 熔岩之心 - 深红熔岩
    "turu_obsidian",   # 黑曜石王 - 紫黑虚空
    "turu_crystal",    # 水晶巨像 - 冰蓝棱镜
    "turu_jade",       # 翡翠神兽 - 翠绿古玉
    "turu_diamond",    # 钻石核心 - 纯白璀璨
    "turu_meteor",     # 陨铁巨人 - 太空陨石
    "turu_sandstone",  # 砂岩遗迹 - 沙漠古物
    "turu_ice",        # 冰川巨人 - 极地冰霜
    "turu_volcanic",   # 火山领主 - 炽烈火山
    "turu_rusty",      # 锈蚀古物 - 苔藓铁锈
    "turu_golden",     # 黄金图鲁 - 传说黄金
]

# 主题配色方案
TURU_THEMES = {
    "turu_default": {
        "name": "岩核原型",
        "rock_main": (110, 100, 90),       # 主岩石色
        "rock_dark": (60, 55, 50),         # 深岩石
        "rock_light": (140, 130, 120),     # 浅岩石
        "core": (255, 120, 40),            # 核心色
        "core_bright": (255, 200, 100),    # 核心高光
        "crack": (255, 160, 80),           # 裂纹色
        "glow": (255, 180, 100),           # 光晕色
        "accent": (180, 120, 60),          # 装饰色
    },
    "turu_magma": {
        "name": "熔岩之心",
        "rock_main": (45, 30, 25),
        "rock_dark": (25, 15, 12),
        "rock_light": (70, 50, 40),
        "core": (255, 60, 20),
        "core_bright": (255, 150, 80),
        "crack": (255, 100, 40),
        "glow": (255, 80, 30),
        "accent": (200, 60, 30),
    },
    "turu_obsidian": {
        "name": "黑曜石王",
        "rock_main": (30, 25, 40),
        "rock_dark": (15, 12, 25),
        "rock_light": (50, 45, 70),
        "core": (180, 80, 255),
        "core_bright": (220, 150, 255),
        "crack": (200, 120, 255),
        "glow": (150, 100, 220),
        "accent": (120, 80, 180),
    },
    "turu_crystal": {
        "name": "水晶巨像",
        "rock_main": (160, 190, 220),
        "rock_dark": (100, 130, 170),
        "rock_light": (200, 220, 240),
        "core": (80, 180, 255),
        "core_bright": (180, 230, 255),
        "crack": (150, 210, 255),
        "glow": (120, 200, 255),
        "accent": (100, 160, 200),
    },
    "turu_jade": {
        "name": "翡翠神兽",
        "rock_main": (60, 130, 80),
        "rock_dark": (30, 80, 50),
        "rock_light": (100, 170, 110),
        "core": (150, 255, 150),
        "core_bright": (200, 255, 200),
        "crack": (120, 220, 140),
        "glow": (100, 255, 130),
        "accent": (80, 150, 90),
    },
    "turu_diamond": {
        "name": "钻石核心",
        "rock_main": (210, 220, 235),
        "rock_dark": (170, 180, 200),
        "rock_light": (240, 245, 255),
        "core": (255, 255, 255),
        "core_bright": (255, 255, 255),
        "crack": (255, 230, 255),
        "glow": (255, 240, 255),
        "accent": (220, 210, 240),
    },
    "turu_meteor": {
        "name": "陨铁巨人",
        "rock_main": (55, 50, 65),
        "rock_dark": (30, 28, 40),
        "rock_light": (80, 75, 95),
        "core": (255, 180, 80),
        "core_bright": (255, 220, 150),
        "crack": (255, 200, 120),
        "glow": (255, 190, 100),
        "accent": (100, 90, 110),
    },
    "turu_sandstone": {
        "name": "砂岩遗迹",
        "rock_main": (170, 140, 100),
        "rock_dark": (130, 100, 65),
        "rock_light": (200, 175, 140),
        "core": (255, 200, 80),
        "core_bright": (255, 230, 150),
        "crack": (220, 180, 120),
        "glow": (255, 210, 130),
        "accent": (180, 150, 100),
    },
    "turu_ice": {
        "name": "冰川巨人",
        "rock_main": (180, 210, 240),
        "rock_dark": (130, 170, 210),
        "rock_light": (220, 240, 255),
        "core": (160, 230, 255),
        "core_bright": (220, 250, 255),
        "crack": (200, 240, 255),
        "glow": (180, 240, 255),
        "accent": (150, 200, 230),
    },
    "turu_volcanic": {
        "name": "火山领主",
        "rock_main": (35, 25, 20),
        "rock_dark": (20, 12, 10),
        "rock_light": (55, 40, 32),
        "core": (255, 50, 10),
        "core_bright": (255, 120, 60),
        "crack": (255, 80, 20),
        "glow": (255, 60, 15),
        "accent": (180, 40, 20),
    },
    "turu_rusty": {
        "name": "锈蚀古物",
        "rock_main": (110, 85, 65),
        "rock_dark": (70, 55, 40),
        "rock_light": (140, 115, 90),
        "core": (130, 160, 90),
        "core_bright": (170, 200, 130),
        "crack": (100, 140, 80),
        "glow": (120, 150, 85),
        "accent": (150, 110, 70),
    },
    "turu_golden": {
        "name": "黄金图鲁",
        "rock_main": (255, 200, 80),
        "rock_dark": (200, 150, 50),
        "rock_light": (255, 230, 150),
        "core": (255, 255, 220),
        "core_bright": (255, 255, 255),
        "crack": (255, 240, 180),
        "glow": (255, 250, 200),
        "accent": (230, 180, 60),
    },
}


def is_turu_style(model_style):
    """检查是否为图鲁涂装样式"""
    return model_style in TURU_STYLES


def get_turu_theme(style):
    """获取主题配色"""
    return TURU_THEMES.get(style, TURU_THEMES["turu_default"])


# =============================================================================
#   蓄力条渲染
# =============================================================================

def _draw_charge_bar(surface, cx, cy, theme, t):
    """绘制图鲁专属4段蓄力条"""
    max_charge = 4
    bar_y = int(cy + 38)
    bar_width = 48
    segment_width = 10
    gap = 2
    
    # 获取当前蓄力值和装甲状态
    actual_charge = 0
    is_unarmored = False
    try:
        from sprites import player
        if player and hasattr(player, 'rock_charge'):
            actual_charge = int(player.rock_charge)
        if player and hasattr(player, 'armor_mode'):
            is_unarmored = not player.armor_mode
    except:
        actual_charge = 0
    
    # 蓄力条背景框
    bg_color = theme["crack"] if is_unarmored else (30, 28, 25)
    pygame.draw.rect(surface, bg_color, 
                     (cx - bar_width//2 - 3, bar_y - 3, bar_width + 6, 14),
                     border_radius=3)
    pygame.draw.rect(surface, (50, 48, 45), 
                     (cx - bar_width//2 - 3, bar_y - 3, bar_width + 6, 14),
                     1, border_radius=3)
    
    # 各段蓄力格子
    for i in range(max_charge):
        seg_x = cx - bar_width//2 + i * (segment_width + gap)
        filled = i < actual_charge
        
        if filled:
            # 已充能 - 发光效果
            pulse = abs(math.sin(t * 6 + i * 0.5))
            base_col = theme["core"]
            bright_col = tuple(min(255, c + int(50 * pulse)) for c in base_col)
            
            # 格子主体
            pygame.draw.rect(surface, base_col, 
                           (seg_x, bar_y, segment_width, 8), border_radius=2)
            # 高光
            pygame.draw.rect(surface, bright_col, 
                           (seg_x + 1, bar_y + 1, segment_width - 2, 3), border_radius=1)
        elif is_unarmored:
            # 卸甲模式 - 脉动空格
            pulse = abs(math.sin(t * 8 + i * 0.3))
            glow_alpha = int(80 + pulse * 60)
            glow_surf = pygame.Surface((segment_width, 8), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*theme["glow"], glow_alpha), 
                           (0, 0, segment_width, 8), border_radius=2)
            surface.blit(glow_surf, (seg_x, bar_y))
        else:
            # 未充能 - 暗色
            pygame.draw.rect(surface, (45, 42, 38), 
                           (seg_x, bar_y, segment_width, 8), border_radius=2)
            pygame.draw.rect(surface, (60, 55, 50), 
                           (seg_x, bar_y, segment_width, 8), 1, border_radius=2)
    
    # 满蓄力闪烁
    if actual_charge >= max_charge:
        if abs(math.sin(t * 10)) > 0.5:
            flash_surf = pygame.Surface((bar_width + 6, 14), pygame.SRCALPHA)
            pygame.draw.rect(flash_surf, (255, 255, 255, 120), 
                           (0, 0, bar_width + 6, 14), border_radius=3)
            surface.blit(flash_surf, (cx - bar_width//2 - 3, bar_y - 3))


# =============================================================================
#   通用绘制辅助函数
# =============================================================================

def _draw_rock_body(surface, cx, cy, theme, t, pulse):
    """绘制图鲁的岩石主躯体"""
    rock_main = theme["rock_main"]
    rock_dark = theme["rock_dark"]
    rock_light = theme["rock_light"]
    crack = theme["crack"]
    
    # 外层岩石轮廓（粗犷不规则）
    body_outer = [
        (cx - 28, cy + 22),
        (cx - 35, cy + 5),
        (cx - 32, cy - 15),
        (cx - 18, cy - 28),
        (cx, cy - 32),
        (cx + 18, cy - 28),
        (cx + 32, cy - 15),
        (cx + 35, cy + 5),
        (cx + 28, cy + 22),
    ]
    pygame.draw.polygon(surface, rock_dark, body_outer)
    
    # 主岩层
    body_main = [
        (cx - 24, cy + 18),
        (cx - 30, cy + 3),
        (cx - 27, cy - 12),
        (cx - 15, cy - 24),
        (cx, cy - 27),
        (cx + 15, cy - 24),
        (cx + 27, cy - 12),
        (cx + 30, cy + 3),
        (cx + 24, cy + 18),
    ]
    pygame.draw.polygon(surface, rock_main, body_main)
    
    # 高光岩层
    body_highlight = [
        (cx - 18, cy + 12),
        (cx - 22, cy),
        (cx - 18, cy - 10),
        (cx - 10, cy - 18),
        (cx, cy - 20),
        (cx + 10, cy - 18),
        (cx + 18, cy - 10),
        (cx + 22, cy),
        (cx + 18, cy + 12),
    ]
    pygame.draw.polygon(surface, rock_light, body_highlight)
    
    # 岩石纹理裂痕
    crack_alpha = int(120 + pulse * 80)
    crack_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    
    # 主裂痕（从核心向外辐射）
    pygame.draw.line(crack_surf, (*crack, crack_alpha), 
                    (60, 55), (60 - 18, 75), 2)
    pygame.draw.line(crack_surf, (*crack, crack_alpha), 
                    (60, 55), (60 + 16, 78), 2)
    pygame.draw.line(crack_surf, (*crack, crack_alpha), 
                    (60, 55), (60 - 22, 45), 2)
    pygame.draw.line(crack_surf, (*crack, crack_alpha), 
                    (60, 55), (60 + 20, 42), 2)
    
    # 次级裂痕
    pygame.draw.line(crack_surf, (*crack, crack_alpha - 40), 
                    (60 - 15, 70), (60 - 25, 80), 1)
    pygame.draw.line(crack_surf, (*crack, crack_alpha - 40), 
                    (60 + 12, 72), (60 + 22, 82), 1)
    
    surface.blit(crack_surf, (0, 0))


def _draw_stone_fist(surface, cx, cy, side, theme, t, pulse):
    """绘制巨石拳头 (side: -1左, 1右)"""
    rock_main = theme["rock_main"]
    rock_dark = theme["rock_dark"]
    rock_light = theme["rock_light"]
    accent = theme["accent"]
    
    # 拳头中心位置
    fist_x = cx + side * 42
    fist_y = cy + 5
    
    # 拳头外轮廓（粗犷岩石）
    fist_outer = [
        (fist_x + side * 8, fist_y + 12),
        (fist_x + side * 14, fist_y + 5),
        (fist_x + side * 15, fist_y - 8),
        (fist_x + side * 10, fist_y - 16),
        (fist_x - side * 2, fist_y - 14),
        (fist_x - side * 8, fist_y - 6),
        (fist_x - side * 6, fist_y + 8),
    ]
    pygame.draw.polygon(surface, rock_dark, fist_outer)
    
    # 拳头主体
    fist_main = [
        (fist_x + side * 6, fist_y + 9),
        (fist_x + side * 11, fist_y + 3),
        (fist_x + side * 12, fist_y - 6),
        (fist_x + side * 8, fist_y - 12),
        (fist_x - side * 1, fist_y - 11),
        (fist_x - side * 5, fist_y - 4),
        (fist_x - side * 4, fist_y + 6),
    ]
    pygame.draw.polygon(surface, rock_main, fist_main)
    
    # 拳头高光
    fist_hl = [
        (fist_x + side * 4, fist_y + 5),
        (fist_x + side * 8, fist_y),
        (fist_x + side * 8, fist_y - 6),
        (fist_x + side * 5, fist_y - 8),
        (fist_x, fist_y - 6),
        (fist_x - side * 2, fist_y),
    ]
    pygame.draw.polygon(surface, rock_light, fist_hl)
    
    # 指节凸起
    for i in range(3):
        knuckle_y = fist_y - 12 + i * 6
        knuckle_x = fist_x + side * (10 - i * 2)
        pygame.draw.circle(surface, rock_dark, (knuckle_x, knuckle_y), 4)
        pygame.draw.circle(surface, rock_light, (knuckle_x - side, knuckle_y - 1), 2)
    
    # 拳头装甲纹
    pygame.draw.arc(surface, accent, 
                   (fist_x - 8, fist_y - 10, 16, 12), 
                   0 if side > 0 else math.pi, math.pi if side > 0 else 2*math.pi, 2)


def _draw_core_eye(surface, cx, cy, theme, t, pulse):
    """绘制核心发光眼"""
    core = theme["core"]
    core_bright = theme["core_bright"]
    glow = theme["glow"]
    
    # 多层光晕
    glow_radius = int(18 + pulse * 8)
    for r in range(glow_radius, 0, -3):
        alpha = int(100 - r * 4)
        if alpha > 0:
            glow_surf = pygame.Surface((r*2 + 4, r*2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*glow, alpha), (r + 2, r + 2), r)
            surface.blit(glow_surf, (cx - r - 2, cy - 5 - r - 2))
    
    # 核心外环
    pygame.draw.circle(surface, core, (cx, cy - 5), 11)
    
    # 核心内环
    pygame.draw.circle(surface, core_bright, (cx, cy - 5), 7)
    
    # 核心高光点
    pygame.draw.circle(surface, (255, 255, 255), (cx - 3, cy - 8), 3)
    pygame.draw.circle(surface, (255, 255, 255), (cx + 2, cy - 4), 2)
    
    # 瞳孔
    pygame.draw.circle(surface, theme["rock_dark"], (cx, cy - 5), 3)


# =============================================================================
#   系列一：岩核战神系列 (default, magma, obsidian)
# =============================================================================

def _render_turu_default(surface, t, pulse, visual=None):
    """岩核原型 - 远古花岗岩巨人，经典重型石甲"""
    cx, cy = 60, 60
    theme = TURU_THEMES["turu_default"]
    
    # === 独特特效：重力岩石轨道 ===
    # 三层轨道环
    for orbit in range(3):
        orbit_r = 42 + orbit * 6
        orbit_alpha = int(50 - orbit * 12)
        orbit_surf = pygame.Surface((orbit_r*2+4, orbit_r*2+4), pygame.SRCALPHA)
        pygame.draw.circle(orbit_surf, (*theme["accent"], orbit_alpha), 
                          (orbit_r+2, orbit_r+2), orbit_r, 1)
        surface.blit(orbit_surf, (cx - orbit_r - 2, cy - orbit_r - 2))
    
    # 轨道上的浮游岩块
    for i in range(8):
        orbit_idx = i % 3
        angle = t * (1.2 - orbit_idx * 0.3) + i * 0.78
        dist = 42 + orbit_idx * 6
        rx = cx + math.cos(angle) * dist
        ry = cy + math.sin(angle) * dist * 0.65
        # 不规则岩块（每个形状不同）
        size = 4 + (i % 3)
        rock_pts = [
            (rx, ry - size),
            (rx - size * 0.8, ry + size * 0.3),
            (rx + size * 0.6, ry + size * 0.5),
        ]
        pygame.draw.polygon(surface, theme["rock_dark"], rock_pts)
        pygame.draw.polygon(surface, theme["rock_main"], rock_pts, 1)
    
    # === 独特躯体：层叠花岗岩装甲 ===
    # 底层装甲（最大）
    body_base = [
        (cx - 30, cy + 24), (cx - 36, cy + 8), (cx - 32, cy - 12),
        (cx - 20, cy - 26), (cx, cy - 30), (cx + 20, cy - 26),
        (cx + 32, cy - 12), (cx + 36, cy + 8), (cx + 30, cy + 24),
    ]
    pygame.draw.polygon(surface, theme["rock_dark"], body_base)
    
    # 中层装甲
    body_mid = [
        (cx - 25, cy + 20), (cx - 30, cy + 5), (cx - 26, cy - 10),
        (cx - 16, cy - 22), (cx, cy - 25), (cx + 16, cy - 22),
        (cx + 26, cy - 10), (cx + 30, cy + 5), (cx + 25, cy + 20),
    ]
    pygame.draw.polygon(surface, theme["rock_main"], body_mid)
    
    # 顶层高光装甲
    body_top = [
        (cx - 18, cy + 14), (cx - 22, cy + 2), (cx - 18, cy - 8),
        (cx - 10, cy - 16), (cx, cy - 18), (cx + 10, cy - 16),
        (cx + 18, cy - 8), (cx + 22, cy + 2), (cx + 18, cy + 14),
    ]
    pygame.draw.polygon(surface, theme["rock_light"], body_top)
    
    # 装甲分割线
    pygame.draw.line(surface, theme["rock_dark"], (cx - 15, cy - 15), (cx - 20, cy + 18), 2)
    pygame.draw.line(surface, theme["rock_dark"], (cx + 15, cy - 15), (cx + 20, cy + 18), 2)
    pygame.draw.line(surface, theme["rock_dark"], (cx - 8, cy - 20), (cx - 5, cy + 15), 1)
    pygame.draw.line(surface, theme["rock_dark"], (cx + 8, cy - 20), (cx + 5, cy + 15), 1)
    
    # === 独特裂纹：辐射状能量裂痕 ===
    crack_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    crack_pulse = abs(math.sin(t * 3))
    crack_alpha = int(140 + crack_pulse * 80)
    
    # 主裂纹（8方向辐射）
    for i in range(8):
        angle = i * 0.785 + 0.4
        length = 18 + (i % 3) * 4
        end_x = cx + math.cos(angle) * length
        end_y = cy - 5 + math.sin(angle) * length * 0.8
        pygame.draw.line(crack_surf, (*theme["crack"], crack_alpha),
                        (cx, cy - 5), (end_x, end_y), 2)
        # 分支裂纹
        if i % 2 == 0:
            branch_angle = angle + 0.4
            branch_len = length * 0.5
            bx = end_x + math.cos(branch_angle) * branch_len
            by = end_y + math.sin(branch_angle) * branch_len * 0.8
            pygame.draw.line(crack_surf, (*theme["crack"], crack_alpha - 40),
                            (end_x, end_y), (bx, by), 1)
    surface.blit(crack_surf, (0, 0))
    
    # === 独特肩甲：层叠式岩板肩甲 ===
    for side in [-1, 1]:
        sx = cx + side * 28
        sy = cy - 5
        # 三层肩甲板
        for layer in range(3):
            offset = layer * 3
            plate_pts = [
                (sx - side * (2 + offset), sy + 8 - offset),
                (sx + side * (8 - offset), sy - 6 - offset),
                (sx + side * (14 - offset), sy - 10 - offset * 2),
                (sx + side * (12 - offset), sy + 4 - offset),
            ]
            col = [theme["rock_dark"], theme["rock_main"], theme["rock_light"]][layer]
            pygame.draw.polygon(surface, col, plate_pts)
        # 肩甲铆钉
        pygame.draw.circle(surface, theme["accent"], (sx + side * 6, sy - 4), 3)
        pygame.draw.circle(surface, theme["crack"], (sx + side * 6, sy - 4), 2)
    
    # === 独特石拳：棱角分明的方形巨拳 ===
    for side in [-1, 1]:
        fx = cx + side * 44
        fy = cy + 6
        # 拳头主体（棱角方形）
        fist_pts = [
            (fx - side * 8, fy + 10),
            (fx + side * 10, fy + 8),
            (fx + side * 14, fy - 2),
            (fx + side * 12, fy - 12),
            (fx + side * 2, fy - 14),
            (fx - side * 6, fy - 8),
            (fx - side * 8, fy + 2),
        ]
        pygame.draw.polygon(surface, theme["rock_dark"], fist_pts)
        # 拳面高光
        fist_face = [
            (fx + side * 2, fy + 6),
            (fx + side * 10, fy + 4),
            (fx + side * 12, fy - 4),
            (fx + side * 8, fy - 10),
            (fx + side * 2, fy - 8),
        ]
        pygame.draw.polygon(surface, theme["rock_main"], fist_face)
        pygame.draw.polygon(surface, theme["rock_light"], fist_face, 2)
        # 指节棱线
        for k in range(3):
            ky = fy - 10 + k * 6
            pygame.draw.line(surface, theme["rock_dark"],
                           (fx + side * 4, ky), (fx + side * 10, ky), 2)
    
    # === 独特核心：层环式发光核心 ===
    # 外环脉动
    for ring in range(4):
        r = 14 - ring * 3 + int(pulse * 3)
        ring_alpha = int(60 + ring * 30 + pulse * 40)
        ring_surf = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (*theme["glow"], ring_alpha), (r+2, r+2), r, 2)
        surface.blit(ring_surf, (cx - r - 2, cy - 5 - r - 2))
    
    # 核心主体
    pygame.draw.circle(surface, theme["core"], (cx, cy - 5), 10)
    pygame.draw.circle(surface, theme["core_bright"], (cx, cy - 5), 6)
    pygame.draw.circle(surface, (255, 255, 255), (cx - 2, cy - 8), 3)
    pygame.draw.circle(surface, theme["rock_dark"], (cx, cy - 5), 3)
    
    # === 独特头冠：三塔式岩冠 ===
    # 中央主塔
    main_crown = [
        (cx - 6, cy - 26), (cx - 4, cy - 40), (cx, cy - 44),
        (cx + 4, cy - 40), (cx + 6, cy - 26),
    ]
    pygame.draw.polygon(surface, theme["rock_dark"], main_crown)
    pygame.draw.polygon(surface, theme["rock_light"], main_crown, 2)
    # 侧塔
    for side in [-1, 1]:
        side_crown = [
            (cx + side * 10, cy - 24),
            (cx + side * 8, cy - 34),
            (cx + side * 12, cy - 32),
            (cx + side * 14, cy - 24),
        ]
        pygame.draw.polygon(surface, theme["rock_main"], side_crown)
        pygame.draw.polygon(surface, theme["rock_light"], side_crown, 1)
    
    _draw_charge_bar(surface, cx, cy, theme, t)


def _render_turu_magma(surface, t, pulse, visual=None):
    """熔岩之心 - 深渊火山巨人，躯体熔岩流动"""
    cx, cy = 60, 60
    theme = TURU_THEMES["turu_magma"]
    
    # === 独特特效：火山热浪扭曲 ===
    heat_wave = abs(math.sin(t * 4))
    # 热浪扭曲环
    for wave in range(5):
        wave_r = 28 + wave * 8 + int(heat_wave * 4)
        wave_offset = math.sin(t * 3 + wave * 0.8) * 3
        wave_alpha = int(80 - wave * 12)
        wave_surf = pygame.Surface((wave_r*2+10, wave_r*2+10), pygame.SRCALPHA)
        # 扭曲的不规则环
        for seg in range(12):
            seg_angle = seg * 0.523
            seg_r = wave_r + math.sin(t * 5 + seg) * 3
            x1 = wave_r + 5 + math.cos(seg_angle) * seg_r
            y1 = wave_r + 5 + math.sin(seg_angle) * seg_r
            x2 = wave_r + 5 + math.cos(seg_angle + 0.523) * seg_r
            y2 = wave_r + 5 + math.sin(seg_angle + 0.523) * seg_r
            pygame.draw.line(wave_surf, (*theme["glow"], wave_alpha), 
                           (x1, y1), (x2, y2), 2)
        surface.blit(wave_surf, (cx - wave_r - 5 + wave_offset, cy - wave_r - 5))
    
    # 火山灰粒子（向上飘散）
    for i in range(12):
        ash_x = cx - 30 + (i * 7) + math.sin(t * 2 + i) * 5
        ash_y = cy + 40 - ((t * 30 + i * 15) % 80)
        ash_alpha = int(60 + math.sin(t + i) * 30)
        ash_size = 2 + (i % 2)
        ash_surf = pygame.Surface((ash_size*2+2, ash_size*2+2), pygame.SRCALPHA)
        pygame.draw.circle(ash_surf, (*theme["rock_light"], ash_alpha), 
                          (ash_size+1, ash_size+1), ash_size)
        surface.blit(ash_surf, (ash_x - ash_size - 1, ash_y - ash_size - 1))
    
    # === 独特躯体：龟裂熔岩外壳 ===
    # 黑色硬壳外层
    shell_outer = [
        (cx - 32, cy + 26), (cx - 40, cy + 5), (cx - 35, cy - 18),
        (cx - 18, cy - 32), (cx, cy - 36), (cx + 18, cy - 32),
        (cx + 35, cy - 18), (cx + 40, cy + 5), (cx + 32, cy + 26),
    ]
    pygame.draw.polygon(surface, theme["rock_dark"], shell_outer)
    
    # 熔岩裂缝系统（复杂网络）
    lava_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    lava_pulse = abs(math.sin(t * 5))
    lava_alpha = int(200 + lava_pulse * 55)
    
    # 主裂缝网（Y形结构）
    pygame.draw.line(lava_surf, (*theme["crack"], lava_alpha),
                    (cx, cy - 5), (cx, cy + 22), 6)
    pygame.draw.line(lava_surf, (*theme["crack"], lava_alpha),
                    (cx, cy - 5), (cx - 25, cy + 20), 5)
    pygame.draw.line(lava_surf, (*theme["crack"], lava_alpha),
                    (cx, cy - 5), (cx + 25, cy + 20), 5)
    pygame.draw.line(lava_surf, (*theme["crack"], lava_alpha),
                    (cx, cy - 5), (cx - 18, cy - 25), 4)
    pygame.draw.line(lava_surf, (*theme["crack"], lava_alpha),
                    (cx, cy - 5), (cx + 18, cy - 25), 4)
    
    # 次级裂缝
    pygame.draw.line(lava_surf, (*theme["core"], lava_alpha - 30),
                    (cx - 15, cy + 12), (cx - 32, cy + 8), 3)
    pygame.draw.line(lava_surf, (*theme["core"], lava_alpha - 30),
                    (cx + 15, cy + 12), (cx + 32, cy + 8), 3)
    pygame.draw.line(lava_surf, (*theme["core"], lava_alpha - 30),
                    (cx - 12, cy - 18), (cx - 28, cy - 22), 2)
    pygame.draw.line(lava_surf, (*theme["core"], lava_alpha - 30),
                    (cx + 12, cy - 18), (cx + 28, cy - 22), 2)
    
    # 毛细裂缝（蛛网状）
    for i in range(16):
        angle = i * 0.393
        length = 15 + (i % 4) * 5
        mid_x = cx + math.cos(angle) * 12
        mid_y = cy - 5 + math.sin(angle) * 10
        end_x = cx + math.cos(angle) * length
        end_y = cy - 5 + math.sin(angle) * length * 0.8
        pygame.draw.line(lava_surf, (*theme["core"], lava_alpha - 60),
                        (mid_x, mid_y), (end_x, end_y), 1)
    
    surface.blit(lava_surf, (0, 0))
    
    # 表层岩块（漂浮在熔岩上）
    for i in range(6):
        angle = t * 0.5 + i * 1.05
        dist = 15 + (i % 3) * 5
        bx = cx + math.cos(angle) * dist
        by = cy - 5 + math.sin(angle) * dist * 0.6 + math.sin(t * 2 + i) * 2
        block_pts = [
            (bx, by - 4), (bx - 5, by + 2), (bx + 4, by + 3),
        ]
        pygame.draw.polygon(surface, theme["rock_dark"], block_pts)
    
    # === 独特肩甲：火山口形肩甲 ===
    for side in [-1, 1]:
        sx = cx + side * 32
        sy = cy - 2
        # 火山口主体
        crater_outer = [
            (sx - side * 6, sy + 14),
            (sx + side * 4, sy + 10),
            (sx + side * 14, sy - 5),
            (sx + side * 10, sy - 18),
            (sx - side * 2, sy - 12),
            (sx - side * 8, sy + 2),
        ]
        pygame.draw.polygon(surface, theme["rock_dark"], crater_outer)
        # 火山口内熔岩
        crater_lava = pygame.Surface((30, 30), pygame.SRCALPHA)
        lava_glow = int(180 + lava_pulse * 75)
        pygame.draw.ellipse(crater_lava, (*theme["core"], lava_glow), (5, 8, 18, 12))
        pygame.draw.ellipse(crater_lava, (*theme["core_bright"], lava_glow), (9, 11, 10, 6))
        surface.blit(crater_lava, (sx - 15, sy - 8))
        # 熔岩喷溅
        for j in range(3):
            splash_y = sy - 15 - int(abs(math.sin(t * 6 + j + side)) * 8)
            splash_x = sx + side * (2 + j * 3)
            pygame.draw.circle(surface, theme["core"], (splash_x, splash_y), 2)
    
    # === 独特石拳：熔岩覆盖的锤拳 ===
    for side in [-1, 1]:
        fx = cx + side * 46
        fy = cy + 8
        # 拳头主体（锤形）
        hammer_pts = [
            (fx - side * 8, fy + 12),
            (fx + side * 6, fy + 14),
            (fx + side * 16, fy + 5),
            (fx + side * 18, fy - 8),
            (fx + side * 12, fy - 16),
            (fx - side * 2, fy - 14),
            (fx - side * 8, fy - 4),
        ]
        pygame.draw.polygon(surface, theme["rock_dark"], hammer_pts)
        # 熔岩覆层
        lava_layer = pygame.Surface((40, 35), pygame.SRCALPHA)
        lava_layer_alpha = int(120 + lava_pulse * 80)
        pygame.draw.polygon(lava_layer, (*theme["crack"], lava_layer_alpha), [
            (20 - side * 2, 18), (20 + side * 10, 16),
            (20 + side * 14, 8), (20 + side * 8, 4),
            (20, 6), (20 - side * 4, 12),
        ])
        surface.blit(lava_layer, (fx - 20, fy - 15))
        # 熔岩滴落
        for d in range(2):
            drip_y = fy + 14 + int(((t * 40 + d * 20) % 20))
            drip_alpha = int(200 - ((t * 40 + d * 20) % 20) * 8)
            if drip_alpha > 0:
                drip_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
                pygame.draw.circle(drip_surf, (*theme["core"], drip_alpha), (4, 4), 3)
                surface.blit(drip_surf, (fx + side * (4 + d * 6) - 4, drip_y - 4))
    
    # === 独特核心：熔岩心脏（脉动收缩） ===
    heart_beat = abs(math.sin(t * 4))
    heart_r = int(12 + heart_beat * 4)
    # 熔岩光晕
    for g in range(5):
        gr = heart_r + 6 + g * 4
        g_alpha = int(100 - g * 18 + heart_beat * 30)
        g_surf = pygame.Surface((gr*2+4, gr*2+4), pygame.SRCALPHA)
        pygame.draw.circle(g_surf, (*theme["glow"], g_alpha), (gr+2, gr+2), gr)
        surface.blit(g_surf, (cx - gr - 2, cy - 5 - gr - 2))
    # 心脏核心
    pygame.draw.circle(surface, theme["core"], (cx, cy - 5), heart_r)
    pygame.draw.circle(surface, theme["core_bright"], (cx, cy - 5), int(heart_r * 0.6))
    pygame.draw.circle(surface, (255, 255, 200), (cx, cy - 5), int(heart_r * 0.3))
    # 脉动波纹
    if heart_beat > 0.7:
        wave_r = int((heart_beat - 0.7) * 50 + heart_r)
        wave_surf = pygame.Surface((wave_r*2+4, wave_r*2+4), pygame.SRCALPHA)
        wave_alpha = int((1 - (heart_beat - 0.7) / 0.3) * 150)
        pygame.draw.circle(wave_surf, (*theme["core"], wave_alpha), (wave_r+2, wave_r+2), wave_r, 3)
        surface.blit(wave_surf, (cx - wave_r - 2, cy - 5 - wave_r - 2))
    
    # === 独特头冠：火焰喷发冠 ===
    # 基座
    crown_base = [(cx - 14, cy - 28), (cx - 10, cy - 32), (cx + 10, cy - 32), (cx + 14, cy - 28)]
    pygame.draw.polygon(surface, theme["rock_dark"], crown_base)
    # 火焰喷射
    for i in range(7):
        flame_x = cx - 10 + i * 3.3
        flame_phase = t * 8 + i * 0.7
        flame_h = 12 + int(abs(math.sin(flame_phase)) * 10)
        flame_sway = math.sin(flame_phase * 0.5) * 3
        # 外焰
        outer_flame = [
            (flame_x, cy - 32),
            (flame_x - 4 + flame_sway, cy - 32 - flame_h),
            (flame_x + 4 + flame_sway, cy - 32 - flame_h),
        ]
        pygame.draw.polygon(surface, theme["core"], outer_flame)
        # 内焰
        inner_h = flame_h * 0.6
        inner_flame = [
            (flame_x, cy - 32),
            (flame_x - 2 + flame_sway * 0.5, cy - 32 - inner_h),
            (flame_x + 2 + flame_sway * 0.5, cy - 32 - inner_h),
        ]
        pygame.draw.polygon(surface, theme["core_bright"], inner_flame)
    
    _draw_charge_bar(surface, cx, cy, theme, t)


def _render_turu_obsidian(surface, t, pulse, visual=None):
    """黑曜石王 - 虚空裂隙巨人，次元切割形态"""
    cx, cy = 60, 60
    theme = TURU_THEMES["turu_obsidian"]
    
    # === 独特特效：虚空裂隙传送门 ===
    void_pulse = abs(math.sin(t * 1.8))
    # 虚空漩涡
    for swirl in range(6):
        swirl_angle = t * (0.8 - swirl * 0.1) + swirl * 1.05
        swirl_r = 35 + swirl * 4
        swirl_alpha = int(60 - swirl * 8)
        # 扭曲的螺旋线
        swirl_surf = pygame.Surface((swirl_r*2+10, swirl_r*2+10), pygame.SRCALPHA)
        prev_x, prev_y = None, None
        for seg in range(24):
            seg_angle = swirl_angle + seg * 0.26
            seg_r = swirl_r - seg * 0.8
            if seg_r > 5:
                sx = swirl_r + 5 + math.cos(seg_angle) * seg_r
                sy = swirl_r + 5 + math.sin(seg_angle) * seg_r * 0.7
                if prev_x is not None:
                    pygame.draw.line(swirl_surf, (*theme["glow"], swirl_alpha),
                                   (prev_x, prev_y), (sx, sy), 2)
                prev_x, prev_y = sx, sy
        surface.blit(swirl_surf, (cx - swirl_r - 5, cy - swirl_r - 5))
    
    # 虚空裂隙粒子（从中心向外消散）
    for i in range(10):
        particle_age = (t * 0.8 + i * 0.3) % 1
        particle_angle = i * 0.63 + t * 0.5
        particle_dist = 10 + particle_age * 40
        px = cx + math.cos(particle_angle) * particle_dist
        py = cy + math.sin(particle_angle) * particle_dist * 0.6
        p_alpha = int((1 - particle_age) * 180)
        p_size = int((1 - particle_age) * 4) + 1
        # 拖尾效果
        for trail in range(3):
            trail_dist = particle_dist - trail * 5
            if trail_dist > 10:
                tx = cx + math.cos(particle_angle) * trail_dist
                ty = cy + math.sin(particle_angle) * trail_dist * 0.6
                t_alpha = int(p_alpha * (1 - trail * 0.3))
                t_surf = pygame.Surface((p_size*2+2, p_size*2+2), pygame.SRCALPHA)
                pygame.draw.circle(t_surf, (*theme["core"], t_alpha), 
                                 (p_size+1, p_size+1), p_size - trail//2)
                surface.blit(t_surf, (tx - p_size - 1, ty - p_size - 1))
    
    # === 独特躯体：锋利切割黑曜石体 ===
    # 尖锐棱角外形
    body_sharp = [
        (cx - 28, cy + 22), (cx - 38, cy + 2), (cx - 34, cy - 18),
        (cx - 22, cy - 32), (cx, cy - 38), (cx + 22, cy - 32),
        (cx + 34, cy - 18), (cx + 38, cy + 2), (cx + 28, cy + 22),
    ]
    pygame.draw.polygon(surface, theme["rock_dark"], body_sharp)
    
    # 玻璃质棱面（反光效果）
    facet_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    facet_pulse = abs(math.sin(t * 2.5 + 0.5))
    
    # 左侧棱面组
    left_facets = [
        [(cx - 25, cy + 18), (cx - 34, cy), (cx - 28, cy - 15), (cx - 15, cy + 5)],
        [(cx - 28, cy - 15), (cx - 20, cy - 28), (cx - 8, cy - 15), (cx - 15, cy + 5)],
        [(cx - 34, cy), (cx - 36, cy - 12), (cx - 28, cy - 15), (cx - 30, cy - 5)],
    ]
    for i, facet in enumerate(left_facets):
        f_alpha = int(40 + facet_pulse * 30 + i * 10)
        pygame.draw.polygon(facet_surf, (*theme["rock_light"], f_alpha), facet)
        pygame.draw.polygon(facet_surf, (*theme["accent"], f_alpha + 20), facet, 1)
    
    # 右侧棱面组
    right_facets = [
        [(cx + 25, cy + 18), (cx + 34, cy), (cx + 28, cy - 15), (cx + 15, cy + 5)],
        [(cx + 28, cy - 15), (cx + 20, cy - 28), (cx + 8, cy - 15), (cx + 15, cy + 5)],
        [(cx + 34, cy), (cx + 36, cy - 12), (cx + 28, cy - 15), (cx + 30, cy - 5)],
    ]
    for i, facet in enumerate(right_facets):
        f_alpha = int(30 + facet_pulse * 25 + i * 8)
        pygame.draw.polygon(facet_surf, (*theme["rock_light"], f_alpha), facet)
        pygame.draw.polygon(facet_surf, (*theme["accent"], f_alpha + 15), facet, 1)
    
    surface.blit(facet_surf, (0, 0))
    
    # 虚空能量脉络
    void_vein = pygame.Surface((120, 120), pygame.SRCALPHA)
    vein_alpha = int(150 + void_pulse * 100)
    # 脉络网络
    pygame.draw.line(void_vein, (*theme["crack"], vein_alpha),
                    (cx, cy - 5), (cx - 25, cy + 18), 3)
    pygame.draw.line(void_vein, (*theme["crack"], vein_alpha),
                    (cx, cy - 5), (cx + 25, cy + 18), 3)
    pygame.draw.line(void_vein, (*theme["crack"], vein_alpha),
                    (cx, cy - 5), (cx, cy - 30), 3)
    pygame.draw.line(void_vein, (*theme["crack"], vein_alpha - 30),
                    (cx - 15, cy + 8), (cx - 32, cy + 5), 2)
    pygame.draw.line(void_vein, (*theme["crack"], vein_alpha - 30),
                    (cx + 15, cy + 8), (cx + 32, cy + 5), 2)
    surface.blit(void_vein, (0, 0))
    
    # === 独特肩甲：次元刃肩甲 ===
    for side in [-1, 1]:
        sx = cx + side * 30
        sy = cy - 8
        # 多层刃片
        for blade in range(4):
            blade_offset = blade * 4
            blade_pts = [
                (sx - side * (4 - blade), sy + 10 - blade_offset),
                (sx + side * (6 + blade * 2), sy - 5 - blade_offset),
                (sx + side * (20 + blade * 3), sy - 20 - blade_offset * 2),
                (sx + side * (12 + blade), sy - 2 - blade_offset),
            ]
            blade_col = theme["rock_dark"] if blade % 2 == 0 else theme["rock_main"]
            pygame.draw.polygon(surface, blade_col, blade_pts)
            pygame.draw.polygon(surface, theme["crack"], blade_pts, 1)
        # 虚空能量点
        pygame.draw.circle(surface, theme["core"], (sx + side * 8, sy - 8), 4)
        pygame.draw.circle(surface, theme["core_bright"], (sx + side * 8, sy - 8), 2)
    
    # === 独特石拳：虚空切割爪 ===
    for side in [-1, 1]:
        fx = cx + side * 45
        fy = cy + 5
        # 爪形拳头
        claw_base = [
            (fx - side * 8, fy + 10),
            (fx + side * 5, fy + 8),
            (fx + side * 10, fy - 2),
            (fx + side * 6, fy - 12),
            (fx - side * 4, fy - 10),
            (fx - side * 8, fy),
        ]
        pygame.draw.polygon(surface, theme["rock_dark"], claw_base)
        pygame.draw.polygon(surface, theme["rock_main"], claw_base, 2)
        
        # 虚空利爪（3根）
        for claw in range(3):
            claw_y = fy - 8 + claw * 6
            claw_pts = [
                (fx + side * 10, claw_y),
                (fx + side * 22, claw_y - 4 + claw),
                (fx + side * 20, claw_y + 2),
            ]
            pygame.draw.polygon(surface, theme["rock_light"], claw_pts)
            pygame.draw.polygon(surface, theme["crack"], claw_pts, 1)
        
        # 虚空能量覆层
        claw_glow = pygame.Surface((35, 30), pygame.SRCALPHA)
        glow_alpha = int(60 + void_pulse * 50)
        pygame.draw.ellipse(claw_glow, (*theme["glow"], glow_alpha), (5, 5, 25, 20))
        surface.blit(claw_glow, (fx - 5 + side * 5, fy - 15))
    
    # === 独特核心：虚空之眼（瞳孔旋转） ===
    # 外层虚空能量
    for ring in range(5):
        r = 16 - ring * 2 + int(void_pulse * 3)
        ring_angle = t * (2 - ring * 0.3)
        ring_alpha = int(80 + ring * 25 + void_pulse * 40)
        ring_surf = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
        # 旋转的断环
        for arc in range(4):
            arc_start = ring_angle + arc * 1.57
            arc_end = arc_start + 1.2
            pygame.draw.arc(ring_surf, (*theme["glow"], ring_alpha),
                          (2, 2, r*2, r*2), arc_start, arc_end, 2)
        surface.blit(ring_surf, (cx - r - 2, cy - 5 - r - 2))
    
    # 核心主体
    pygame.draw.circle(surface, theme["core"], (cx, cy - 5), 11)
    pygame.draw.circle(surface, theme["core_bright"], (cx, cy - 5), 7)
    # 旋转瞳孔
    pupil_angle = t * 3
    pupil_x = cx + math.cos(pupil_angle) * 2
    pupil_y = cy - 5 + math.sin(pupil_angle) * 2
    pygame.draw.circle(surface, theme["rock_dark"], (int(pupil_x), int(pupil_y)), 3)
    pygame.draw.circle(surface, (255, 255, 255), (cx - 3, cy - 8), 2)
    
    # === 独特头冠：虚空王之冠 ===
    # 锯齿王冠
    crown_pts = []
    for i in range(9):
        crown_x = cx - 16 + i * 4
        if i % 2 == 0:
            crown_pts.append((crown_x, cy - 28))
        else:
            crown_pts.append((crown_x, cy - 40 - (i % 3) * 5))
    pygame.draw.polygon(surface, theme["rock_dark"], crown_pts)
    pygame.draw.polygon(surface, theme["crack"], crown_pts, 2)
    
    # 中央虚空宝石
    pygame.draw.circle(surface, theme["core"], (cx, cy - 38), 6)
    pygame.draw.circle(surface, theme["core_bright"], (cx, cy - 38), 4)
    pygame.draw.circle(surface, (255, 255, 255), (cx - 2, cy - 40), 2)
    
    # 侧面小宝石
    for side in [-1, 1]:
        pygame.draw.circle(surface, theme["core"], (cx + side * 10, cy - 34), 3)
        pygame.draw.circle(surface, theme["core_bright"], (cx + side * 10, cy - 34), 2)
    
    _draw_charge_bar(surface, cx, cy, theme, t)


# =============================================================================
#   系列二：矿物珍宝系列 (crystal, jade, diamond)
# =============================================================================

def _render_turu_crystal(surface, t, pulse, visual=None):
    """水晶巨像 - 六边形棱镜体，彩虹光线折射分解"""
    cx, cy = 60, 60
    theme = TURU_THEMES["turu_crystal"]
    
    # === 独特特效：棱镜彩虹分解 ===
    shimmer = abs(math.sin(t * 3))
    rainbow_colors = [
        (255, 80, 80), (255, 160, 80), (255, 255, 80),
        (80, 255, 80), (80, 200, 255), (160, 80, 255), (255, 80, 200)
    ]
    # 光线从核心向外发散分解为彩虹
    for i, col in enumerate(rainbow_colors):
        angle = t * 1.5 + i * 0.9
        # 每条光线由多个点组成
        for seg in range(4):
            dist = 25 + seg * 8 + shimmer * 4
            spread = seg * 0.12  # 逐渐分散
            seg_angle = angle + spread * (-1 if i < 3 else 1)
            rx = cx + math.cos(seg_angle) * dist
            ry = cy + math.sin(seg_angle) * dist * 0.65
            ray_alpha = int(150 - seg * 30 + shimmer * 40)
            ray_size = 4 - seg // 2
            if ray_alpha > 0 and ray_size > 0:
                ray_surf = pygame.Surface((ray_size*2+2, ray_size*2+2), pygame.SRCALPHA)
                pygame.draw.circle(ray_surf, (*col, ray_alpha), (ray_size+1, ray_size+1), ray_size)
                surface.blit(ray_surf, (rx - ray_size - 1, ry - ray_size - 1))
    
    # 棱镜折射光带
    prism_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for band in range(5):
        band_y = cy - 20 + band * 10
        band_alpha = int(30 + shimmer * 25)
        band_col = rainbow_colors[band % 7]
        pygame.draw.line(prism_surf, (*band_col, band_alpha),
                        (cx - 35 + band * 3, band_y), (cx + 35 - band * 3, band_y), 2)
    surface.blit(prism_surf, (0, 0))
    
    # === 独特躯体：六边形棱柱晶体 ===
    # 六边形主体（水晶特有形态）
    hex_outer = []
    for i in range(6):
        angle = i * 1.047 - 0.52  # 60度间隔
        hx = cx + math.cos(angle) * 32
        hy = cy + math.sin(angle) * 26
        hex_outer.append((hx, hy))
    pygame.draw.polygon(surface, theme["rock_dark"], hex_outer)
    
    # 中层六边形
    hex_mid = []
    for i in range(6):
        angle = i * 1.047 - 0.52
        hx = cx + math.cos(angle) * 26
        hy = cy + math.sin(angle) * 21
        hex_mid.append((hx, hy))
    pygame.draw.polygon(surface, theme["rock_main"], hex_mid)
    
    # 内层发光六边形
    hex_inner = []
    for i in range(6):
        angle = i * 1.047 - 0.52
        hx = cx + math.cos(angle) * 18
        hy = cy + math.sin(angle) * 14
        hex_inner.append((hx, hy))
    pygame.draw.polygon(surface, theme["rock_light"], hex_inner)
    
    # 六边形棱线
    for i in range(6):
        angle = i * 1.047 - 0.52
        ex = cx + math.cos(angle) * 32
        ey = cy + math.sin(angle) * 26
        pygame.draw.line(surface, (255, 255, 255), (cx, cy), (ex, ey), 1)
    
    # === 独特棱面：透明折射面 ===
    facet_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    facet_phase = abs(math.sin(t * 2.5))
    
    # 三个主棱面（交替闪烁）
    for f in range(3):
        f_angle = f * 2.09 + t * 0.5
        f_alpha = int(60 + facet_phase * 50 + math.sin(t * 4 + f) * 30)
        f_pts = [
            (cx, cy),
            (cx + math.cos(f_angle) * 28, cy + math.sin(f_angle) * 22),
            (cx + math.cos(f_angle + 1.05) * 28, cy + math.sin(f_angle + 1.05) * 22),
        ]
        pygame.draw.polygon(facet_surf, (255, 255, 255, f_alpha), f_pts)
    surface.blit(facet_surf, (0, 0))
    
    # === 独特肩甲：立方晶系肩垫 ===
    for side in [-1, 1]:
        sx = cx + side * 30
        sy = cy - 5
        # 三层递进水晶块
        for layer in range(3):
            offset = layer * 5
            crystal_pts = [
                (sx - side * (2 + offset//2), sy + 12 - offset),
                (sx + side * (4 - layer), sy - 4 - offset),
                (sx + side * (14 - offset), sy - 12 - offset),
                (sx + side * (18 - offset), sy - 4 - offset),
                (sx + side * (12 - offset//2), sy + 8 - offset),
            ]
            c_alpha = 200 - layer * 40
            c_col = theme["rock_main"] if layer == 0 else theme["rock_light"]
            pygame.draw.polygon(surface, c_col, crystal_pts)
            pygame.draw.polygon(surface, (255, 255, 255), crystal_pts, 1)
        # 肩部宝石
        pygame.draw.circle(surface, theme["core"], (sx + side * 8, sy - 8), 4)
        pygame.draw.circle(surface, (255, 255, 255), (sx + side * 7, sy - 9), 2)
    
    # === 独特石拳：水晶尖锥拳 ===
    for side in [-1, 1]:
        fx = cx + side * 45
        fy = cy + 6
        # 尖锥主体
        prism_fist = [
            (fx - side * 6, fy + 10),
            (fx + side * 8, fy + 12),
            (fx + side * 18, fy),
            (fx + side * 20, fy - 10),  # 尖端
            (fx + side * 12, fy - 14),
            (fx, fy - 10),
            (fx - side * 6, fy),
        ]
        pygame.draw.polygon(surface, theme["rock_main"], prism_fist)
        pygame.draw.polygon(surface, theme["rock_light"], prism_fist, 2)
        
        # 棱面高光
        for ridge in range(3):
            r_start = (fx + side * (4 + ridge * 5), fy - 10 + ridge * 6)
            r_end = (fx + side * (16 - ridge * 2), fy - 8 + ridge * 5)
            pygame.draw.line(surface, (255, 255, 255), r_start, r_end, 1)
        
        # 指节晶簇
        for k in range(2):
            kx = fx + side * (8 + k * 6)
            ky = fy - 12 + k * 4
            pygame.draw.polygon(surface, theme["rock_light"], [
                (kx, ky - 6), (kx - 3, ky + 2), (kx + 3, ky + 2)
            ])
    
    # === 独特核心：旋转棱镜核心 ===
    prism_angle = t * 2
    # 外层旋转六边形
    for ring in range(4):
        r = 14 - ring * 2 + int(pulse * 3)
        ring_a = prism_angle + ring * 0.3
        ring_alpha = int(100 + ring * 30 + shimmer * 40)
        ring_surf = pygame.Surface((r*2+8, r*2+8), pygame.SRCALPHA)
        hex_pts = []
        for i in range(6):
            ha = ring_a + i * 1.047
            hx = r + 4 + math.cos(ha) * r
            hy = r + 4 + math.sin(ha) * r
            hex_pts.append((hx, hy))
        pygame.draw.polygon(ring_surf, (*theme["glow"], ring_alpha), hex_pts, 2)
        surface.blit(ring_surf, (cx - r - 4, cy - 5 - r - 4))
    
    # 核心本体
    pygame.draw.circle(surface, theme["core"], (cx, cy - 5), 10)
    pygame.draw.circle(surface, theme["core_bright"], (cx, cy - 5), 6)
    pygame.draw.circle(surface, (255, 255, 255), (cx - 2, cy - 7), 3)
    
    # === 独特头冠：多尖水晶簇 ===
    # 中央主晶
    main_crystal = [
        (cx - 5, cy - 28), (cx - 3, cy - 46), (cx + 3, cy - 46), (cx + 5, cy - 28)
    ]
    pygame.draw.polygon(surface, theme["rock_light"], main_crystal)
    pygame.draw.polygon(surface, (255, 255, 255), main_crystal, 1)
    
    # 侧面晶簇（左右各2根，不同高度）
    crystal_heights = [(-12, 36), (-7, 40), (7, 38), (12, 34)]
    for cx_off, ch in crystal_heights:
        crystal_pts = [
            (cx + cx_off - 2, cy - 28),
            (cx + cx_off, cy - ch),
            (cx + cx_off + 2, cy - 28),
        ]
        pygame.draw.polygon(surface, theme["rock_main"], crystal_pts)
        pygame.draw.polygon(surface, (255, 255, 255), crystal_pts, 1)
    
    _draw_charge_bar(surface, cx, cy, theme, t)


def _render_turu_jade(surface, t, pulse, visual=None):
    """翡翠神兽 - 东方神兽玉雕，圆润古朴形态"""
    cx, cy = 60, 60
    theme = TURU_THEMES["turu_jade"]
    
    # === 独特特效：祥云萦绕 ===
    jade_glow = abs(math.sin(t * 1.8))
    # 祥云（东方风格的卷云）
    for cloud in range(5):
        cloud_angle = t * 0.5 + cloud * 1.26
        cloud_dist = 38 + math.sin(t * 0.8 + cloud) * 6
        cx_cloud = cx + math.cos(cloud_angle) * cloud_dist
        cy_cloud = cy + math.sin(cloud_angle) * cloud_dist * 0.5
        cloud_alpha = int(50 + jade_glow * 35)
        cloud_surf = pygame.Surface((24, 16), pygame.SRCALPHA)
        # 祥云形状（三个重叠圆）
        pygame.draw.circle(cloud_surf, (*theme["glow"], cloud_alpha), (6, 10), 5)
        pygame.draw.circle(cloud_surf, (*theme["glow"], cloud_alpha), (12, 8), 6)
        pygame.draw.circle(cloud_surf, (*theme["glow"], cloud_alpha), (18, 10), 5)
        surface.blit(cloud_surf, (cx_cloud - 12, cy_cloud - 8))
    
    # 玉粉尘（缓慢飘落）
    for i in range(8):
        dust_x = cx - 25 + (i * 8) + math.sin(t + i) * 5
        dust_y = ((t * 15 + i * 20) % 60) + cy - 30
        dust_alpha = int(60 + math.sin(t * 2 + i) * 30)
        dust_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(dust_surf, (*theme["core"], dust_alpha), (3, 3), 2)
        surface.blit(dust_surf, (dust_x - 3, dust_y - 3))
    
    # === 独特躯体：圆润玉雕形态 ===
    # 最外层（深色边缘）
    pygame.draw.ellipse(surface, theme["rock_dark"], (cx - 34, cy - 28, 68, 52))
    # 中层（主体玉色）
    pygame.draw.ellipse(surface, theme["rock_main"], (cx - 30, cy - 24, 60, 44))
    # 内层（高光区）
    pygame.draw.ellipse(surface, theme["rock_light"], (cx - 22, cy - 18, 44, 32))
    
    # 玉纹理（飘逸丝状）
    vein_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    vein_alpha = int(70 + jade_glow * 40)
    # S形玉纹
    for v in range(3):
        v_offset = v * 8 - 8
        pts = []
        for seg in range(8):
            sx = cx - 20 + seg * 5 + v_offset
            sy = cy - 10 + math.sin(seg * 0.8 + v) * 8
            pts.append((sx, sy))
        if len(pts) >= 2:
            pygame.draw.lines(vein_surf, (*theme["crack"], vein_alpha), False, pts, 2)
    surface.blit(vein_surf, (0, 0))
    
    # 古纹装饰
    # 中央如意纹
    pygame.draw.arc(surface, theme["crack"], (cx - 12, cy - 8, 24, 16), 0.5, 2.6, 2)
    pygame.draw.arc(surface, theme["crack"], (cx - 8, cy - 4, 16, 12), 0.5, 2.6, 2)
    
    # === 独特肩甲：螭龙纹玉环 ===
    for side in [-1, 1]:
        sx = cx + side * 28
        sy = cy - 5
        # 玉环主体
        pygame.draw.circle(surface, theme["rock_dark"], (sx, sy), 14)
        pygame.draw.circle(surface, theme["rock_main"], (sx, sy), 11)
        pygame.draw.circle(surface, theme["rock_dark"], (sx, sy), 6)
        pygame.draw.circle(surface, theme["rock_light"], (sx, sy), 4)
        # 螭龙纹（简化卷曲）
        dragon_pts = [
            (sx - side * 8, sy - 8),
            (sx - side * 12, sy - 4),
            (sx - side * 10, sy + 4),
            (sx - side * 6, sy + 8),
        ]
        pygame.draw.lines(surface, theme["crack"], False, dragon_pts, 2)
    
    # === 独特石拳：璧玉圆拳 ===
    for side in [-1, 1]:
        fx = cx + side * 44
        fy = cy + 5
        # 圆润拳头主体
        pygame.draw.ellipse(surface, theme["rock_dark"], (fx - 12, fy - 12, 24, 24))
        pygame.draw.ellipse(surface, theme["rock_main"], (fx - 10, fy - 10, 20, 20))
        pygame.draw.ellipse(surface, theme["rock_light"], (fx - 6, fy - 6, 12, 12))
        
        # 拳面雕纹（同心圆）
        pygame.draw.circle(surface, theme["crack"], (fx, fy), 8, 1)
        pygame.draw.circle(surface, theme["crack"], (fx, fy), 5, 1)
        
        # 边缘回纹装饰
        for r in range(3):
            r_angle = t * 0.5 + r * 2.09 + side
            rx = fx + math.cos(r_angle) * 10
            ry = fy + math.sin(r_angle) * 10
            pygame.draw.rect(surface, theme["crack"], (rx - 2, ry - 2, 4, 4), 1)
    
    # === 独特核心：太极玉眼 ===
    # 外层玉环
    for ring in range(4):
        r = 14 - ring * 2 + int(pulse * 2)
        ring_alpha = int(80 + ring * 25 + jade_glow * 35)
        ring_surf = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (*theme["glow"], ring_alpha), (r+2, r+2), r, 2)
        surface.blit(ring_surf, (cx - r - 2, cy - 5 - r - 2))
    
    # 太极核心
    pygame.draw.circle(surface, theme["core"], (cx, cy - 5), 10)
    # 阴阳分界
    pygame.draw.arc(surface, theme["core_bright"], (cx - 10, cy - 15, 20, 20), 1.57, 4.71, 10)
    # 阴阳鱼眼
    pygame.draw.circle(surface, theme["rock_dark"], (cx - 3, cy - 8), 3)
    pygame.draw.circle(surface, theme["core_bright"], (cx + 3, cy - 2), 3)
    pygame.draw.circle(surface, (255, 255, 255), (cx - 4, cy - 9), 1)
    
    # === 独特头冠：如意祥云冠 ===
    # 如意头（三层叠）
    for layer in range(3):
        l_offset = layer * 4
        l_width = 24 - layer * 6
        l_height = 12 - layer * 3
        l_y = cy - 32 - l_offset
        pygame.draw.ellipse(surface, theme["rock_main"] if layer == 0 else theme["rock_light"],
                           (cx - l_width//2, l_y, l_width, l_height))
        if layer < 2:
            pygame.draw.ellipse(surface, theme["crack"],
                               (cx - l_width//2, l_y, l_width, l_height), 1)
    
    # 垂珠装饰
    for side in [-1, 1]:
        pygame.draw.circle(surface, theme["core"], (cx + side * 10, cy - 30), 3)
        pygame.draw.circle(surface, theme["core_bright"], (cx + side * 10, cy - 30), 2)
    
    _draw_charge_bar(surface, cx, cy, theme, t)


def _render_turu_diamond(surface, t, pulse, visual=None):
    """钻石核心 - 完美切割明亮式，极致璀璨闪耀"""
    cx, cy = 60, 60
    theme = TURU_THEMES["turu_diamond"]
    
    # === 独特特效：火彩闪烁场 ===
    brilliance = abs(math.sin(t * 4))
    
    # 随机位置的火彩闪光（十字星芒）
    for i in range(10):
        spark_phase = (t * 3 + i * 0.8) % 6.28
        spark_angle = i * 0.63 + spark_phase * 0.2
        spark_dist = 30 + math.sin(spark_phase) * 15
        sx = cx + math.cos(spark_angle) * spark_dist
        sy = cy + math.sin(spark_angle) * spark_dist * 0.6
        spark_life = abs(math.sin(spark_phase * 2))
        if spark_life > 0.3:
            spark_alpha = int(spark_life * 200)
            spark_len = int(3 + spark_life * 5)
            spark_surf = pygame.Surface((spark_len*2+4, spark_len*2+4), pygame.SRCALPHA)
            # 四芒星
            pygame.draw.line(spark_surf, (255, 255, 255, min(255, spark_alpha)),
                           (spark_len+2, 2), (spark_len+2, spark_len*2+2), 2)
            pygame.draw.line(spark_surf, (255, 255, 255, min(255, spark_alpha)),
                           (2, spark_len+2), (spark_len*2+2, spark_len+2), 2)
            # 对角短芒
            pygame.draw.line(spark_surf, (255, 255, 255, min(255, spark_alpha - 50)),
                           (4, 4), (spark_len*2, spark_len*2), 1)
            pygame.draw.line(spark_surf, (255, 255, 255, min(255, spark_alpha - 50)),
                           (spark_len*2, 4), (4, spark_len*2), 1)
            surface.blit(spark_surf, (sx - spark_len - 2, sy - spark_len - 2))
    
    # 彩虹火彩散射
    fire_colors = [(255, 200, 200), (255, 255, 200), (200, 255, 255), (220, 200, 255)]
    for i, col in enumerate(fire_colors):
        fire_angle = t * 2.5 + i * 1.57
        fire_dist = 42 + brilliance * 6
        for seg in range(3):
            seg_dist = fire_dist - seg * 6
            fx = cx + math.cos(fire_angle) * seg_dist
            fy = cy + math.sin(fire_angle) * seg_dist * 0.5
            f_alpha = int(100 - seg * 25 + brilliance * 40)
            f_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(f_surf, (*col, f_alpha), (5, 5), 4 - seg)
            surface.blit(f_surf, (fx - 5, fy - 5))
    
    # === 独特躯体：明亮式切割钻石形 ===
    # 冠部（上半，八角形）
    crown = []
    for i in range(8):
        angle = i * 0.785 - 0.39
        cr = 28 if i % 2 == 0 else 32
        crown.append((cx + math.cos(angle) * cr, cy - 8 + math.sin(angle) * cr * 0.7))
    pygame.draw.polygon(surface, theme["rock_main"], crown)
    
    # 亭部（下半，收尖）
    pavilion = [
        (cx - 28, cy + 2), (cx - 20, cy + 18), (cx, cy + 26),
        (cx + 20, cy + 18), (cx + 28, cy + 2),
    ]
    pygame.draw.polygon(surface, theme["rock_dark"], pavilion)
    
    # 台面（顶部平面）
    table = []
    for i in range(8):
        angle = i * 0.785 - 0.39
        table.append((cx + math.cos(angle) * 16, cy - 12 + math.sin(angle) * 10))
    pygame.draw.polygon(surface, theme["rock_light"], table)
    
    # 星形刻面（冠部到台面）
    facet_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(8):
        angle = i * 0.785 - 0.39
        outer_x = cx + math.cos(angle) * 30
        outer_y = cy - 8 + math.sin(angle) * 21
        inner_x = cx + math.cos(angle) * 16
        inner_y = cy - 12 + math.sin(angle) * 10
        f_alpha = int(80 + brilliance * 60 + math.sin(t * 5 + i) * 40)
        pygame.draw.polygon(facet_surf, (255, 255, 255, f_alpha),
                           [(cx, cy - 12), (inner_x, inner_y), (outer_x, outer_y)])
    
    # 亭部刻面（向尖端收）
    for i in range(8):
        angle = i * 0.785 - 0.39
        top_x = cx + math.cos(angle) * 28
        top_y = cy + 2 + math.sin(angle) * 8
        f_alpha = int(50 + brilliance * 40)
        pygame.draw.polygon(facet_surf, (200, 200, 255, f_alpha),
                           [(top_x, top_y), (cx, cy + 26),
                            (cx + math.cos(angle + 0.39) * 28, cy + 2 + math.sin(angle + 0.39) * 8)])
    surface.blit(facet_surf, (0, 0))
    
    # === 独特肩甲：小钻簇肩饰 ===
    for side in [-1, 1]:
        sx = cx + side * 30
        sy = cy - 6
        # 主钻
        main_pts = [
            (sx, sy - 14), (sx + side * 10, sy - 5),
            (sx + side * 8, sy + 8), (sx - side * 4, sy + 6), (sx - side * 6, sy - 6),
        ]
        pygame.draw.polygon(surface, theme["rock_main"], main_pts)
        pygame.draw.polygon(surface, (255, 255, 255), main_pts, 1)
        
        # 副钻（3颗小钻）
        for d in range(3):
            d_x = sx + side * (12 + d * 4)
            d_y = sy - 8 + d * 6
            d_pts = [(d_x, d_y - 5), (d_x + side * 4, d_y), (d_x, d_y + 4), (d_x - side * 3, d_y)]
            pygame.draw.polygon(surface, theme["rock_light"], d_pts)
            pygame.draw.polygon(surface, (255, 255, 255), d_pts, 1)
    
    # === 独特石拳：多面宝石拳 ===
    for side in [-1, 1]:
        fx = cx + side * 46
        fy = cy + 5
        # 主体（八面体形）
        fist_pts = [
            (fx - side * 6, fy), (fx, fy - 14),
            (fx + side * 14, fy - 10), (fx + side * 18, fy),
            (fx + side * 14, fy + 10), (fx, fy + 12), (fx - side * 6, fy + 6),
        ]
        pygame.draw.polygon(surface, theme["rock_main"], fist_pts)
        
        # 刻面分割线
        pygame.draw.line(surface, (255, 255, 255), (fx, fy), (fx, fy - 14), 1)
        pygame.draw.line(surface, (255, 255, 255), (fx, fy), (fx + side * 18, fy), 1)
        pygame.draw.line(surface, (255, 255, 255), (fx, fy), (fx, fy + 12), 1)
        
        # 表面高光
        pygame.draw.polygon(surface, theme["rock_light"], [
            (fx, fy), (fx + side * 8, fy - 8), (fx + side * 14, fy - 4), (fx + side * 10, fy + 2)
        ])
        
        # 火彩点
        for spark in range(2):
            sp_x = fx + side * (6 + spark * 6)
            sp_y = fy - 6 + spark * 4
            pygame.draw.circle(surface, (255, 255, 255), (sp_x, sp_y), 2)
    
    # === 独特核心：心形切割核心 ===
    # 旋转火彩环
    for ring in range(5):
        r = 16 - ring * 2 + int(pulse * 3)
        ring_angle = t * (3 - ring * 0.5)
        ring_alpha = int(100 + ring * 30 + brilliance * 50)
        ring_surf = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
        # 八芒星形环
        for ray in range(8):
            ray_angle = ring_angle + ray * 0.785
            ray_len = r if ray % 2 == 0 else r * 0.7
            rx = r + 2 + math.cos(ray_angle) * ray_len
            ry = r + 2 + math.sin(ray_angle) * ray_len
            pygame.draw.line(ring_surf, (255, 255, 255, min(255, ring_alpha)),
                           (r + 2, r + 2), (rx, ry), 2)
        surface.blit(ring_surf, (cx - r - 2, cy - 5 - r - 2))
    
    # 纯白核心
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy - 5), 11)
    pygame.draw.circle(surface, theme["core_bright"], (cx, cy - 5), 8)
    pygame.draw.circle(surface, (255, 255, 255), (cx - 2, cy - 8), 3)
    
    # === 独特头冠：帝王钻冠 ===
    # 主钻（大）
    main_crown = [
        (cx - 8, cy - 28), (cx - 4, cy - 44), (cx + 4, cy - 44), (cx + 8, cy - 28)
    ]
    pygame.draw.polygon(surface, theme["rock_light"], main_crown)
    pygame.draw.polygon(surface, (255, 255, 255), main_crown, 2)
    
    # 侧翼钻（各2颗）
    wing_data = [(-14, -32, 6), (-10, -36, 5), (10, -36, 5), (14, -32, 6)]
    for wx, wy, ws in wing_data:
        wing_pts = [(cx + wx, cy + wy + ws), (cx + wx - ws//2, cy + wy),
                    (cx + wx, cy + wy - ws), (cx + wx + ws//2, cy + wy)]
        pygame.draw.polygon(surface, theme["rock_main"], wing_pts)
        pygame.draw.polygon(surface, (255, 255, 255), wing_pts, 1)
    
    # 顶部超大火彩
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy - 42), 4)
    # 十字星芒
    pygame.draw.line(surface, (255, 255, 255), (cx, cy - 50), (cx, cy - 34), 2)
    pygame.draw.line(surface, (255, 255, 255), (cx - 8, cy - 42), (cx + 8, cy - 42), 2)
    
    _draw_charge_bar(surface, cx, cy, theme, t)


# =============================================================================
#   系列三：自然元素系列 (meteor, sandstone, ice)
# =============================================================================

def _render_turu_meteor(surface, t, pulse, visual=None):
    """陨铁巨人 - 坠落陨石，大气燃烧与宇宙金属交织"""
    cx, cy = 60, 60
    theme = TURU_THEMES["turu_meteor"]
    
    # === 独特特效：陨石坠落轨迹 ===
    heat = abs(math.sin(t * 2.5))
    
    # 燃烧轨迹（向上的火焰尾巴）
    for tail in range(6):
        tail_y = cy + 25 + tail * 8
        tail_width = 24 - tail * 3
        tail_alpha = int(120 - tail * 18)
        if tail_alpha > 0:
            tail_surf = pygame.Surface((tail_width + 10, 12), pygame.SRCALPHA)
            # 火焰锯齿
            flame_pts = []
            for i in range(tail_width // 3 + 1):
                fx = 5 + i * 3
                fy = 2 if i % 2 == 0 else 8 + math.sin(t * 8 + i) * 2
                flame_pts.append((fx, fy))
            if len(flame_pts) >= 3:
                pygame.draw.polygon(tail_surf, (*theme["crack"], tail_alpha), flame_pts)
            surface.blit(tail_surf, (cx - tail_width // 2 - 5, tail_y))
    
    # 大气燃烧粒子（四散）
    for i in range(10):
        p_age = (t * 1.5 + i * 0.4) % 1
        p_angle = i * 0.63 + 2.5  # 主要向上和侧面
        p_dist = 15 + p_age * 35
        px = cx + math.cos(p_angle) * p_dist * 0.6
        py = cy + 10 + p_age * 30  # 向下飘
        p_alpha = int((1 - p_age) * 200)
        p_size = int((1 - p_age) * 4) + 1
        if p_alpha > 30:
            p_surf = pygame.Surface((p_size*2+2, p_size*2+2), pygame.SRCALPHA)
            p_col = theme["core"] if i % 2 == 0 else theme["crack"]
            pygame.draw.circle(p_surf, (*p_col, p_alpha), (p_size+1, p_size+1), p_size)
            surface.blit(p_surf, (px - p_size - 1, py - p_size - 1))
    
    # === 独特躯体：不规则陨石块形态 ===
    # 高度不规则的陨石外形
    meteor_body = [
        (cx - 28, cy + 20), (cx - 38, cy + 5), (cx - 35, cy - 10),
        (cx - 28, cy - 24), (cx - 12, cy - 32), (cx + 8, cy - 30),
        (cx + 25, cy - 28), (cx + 36, cy - 12), (cx + 40, cy + 8),
        (cx + 32, cy + 22), (cx + 15, cy + 26), (cx - 10, cy + 24),
    ]
    pygame.draw.polygon(surface, theme["rock_dark"], meteor_body)
    
    # 陨石表面纹理层
    meteor_inner = [
        (cx - 22, cy + 16), (cx - 30, cy + 2), (cx - 26, cy - 12),
        (cx - 18, cy - 22), (cx - 5, cy - 26), (cx + 12, cy - 24),
        (cx + 22, cy - 20), (cx + 30, cy - 8), (cx + 32, cy + 6),
        (cx + 26, cy + 18), (cx + 10, cy + 20), (cx - 8, cy + 18),
    ]
    pygame.draw.polygon(surface, theme["rock_main"], meteor_inner)
    
    # 高光区域（高温熔融面）
    hot_spot = pygame.Surface((120, 120), pygame.SRCALPHA)
    hot_alpha = int(80 + heat * 60)
    pygame.draw.polygon(hot_spot, (*theme["rock_light"], hot_alpha), [
        (cx - 15, cy - 15), (cx - 5, cy - 22), (cx + 8, cy - 18),
        (cx + 5, cy - 5), (cx - 10, cy - 8),
    ])
    surface.blit(hot_spot, (0, 0))
    
    # === 独特撞击坑：多种大小的陨石坑 ===
    crater_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    craters = [(cx - 15, cy + 8, 9), (cx + 18, cy - 8, 7), 
               (cx - 5, cy - 18, 5), (cx + 8, cy + 12, 6),
               (cx - 22, cy - 5, 4), (cx + 25, cy + 5, 5)]
    for crx, cry, cr_size in craters:
        # 坑边缘
        pygame.draw.circle(crater_surf, (*theme["rock_dark"], 180), (crx, cry), cr_size)
        # 坑内阴影
        pygame.draw.circle(crater_surf, (*theme["rock_main"], 120), (crx, cry), int(cr_size * 0.7))
        # 中心高光
        pygame.draw.circle(crater_surf, (*theme["rock_light"], 80), (crx - 1, cry - 1), int(cr_size * 0.3))
    surface.blit(crater_surf, (0, 0))
    
    # === 独特热裂纹：熔融金属脉络 ===
    heat_vein = pygame.Surface((120, 120), pygame.SRCALPHA)
    vein_alpha = int(180 + heat * 75)
    # 不规则的热裂纹网络
    pygame.draw.line(heat_vein, (*theme["crack"], vein_alpha),
                    (cx + 5, cy - 5), (cx - 18, cy + 18), 4)
    pygame.draw.line(heat_vein, (*theme["crack"], vein_alpha),
                    (cx + 5, cy - 5), (cx + 25, cy + 15), 4)
    pygame.draw.line(heat_vein, (*theme["crack"], vein_alpha),
                    (cx + 5, cy - 5), (cx - 10, cy - 22), 3)
    pygame.draw.line(heat_vein, (*theme["crack"], vein_alpha),
                    (cx + 5, cy - 5), (cx + 20, cy - 18), 3)
    # 分支
    pygame.draw.line(heat_vein, (*theme["core"], vein_alpha - 40),
                    (cx - 12, cy + 10), (cx - 28, cy + 15), 2)
    pygame.draw.line(heat_vein, (*theme["core"], vein_alpha - 40),
                    (cx + 18, cy + 8), (cx + 32, cy + 12), 2)
    surface.blit(heat_vein, (0, 0))
    
    # === 独特肩甲：陨石碎片簇 ===
    for side in [-1, 1]:
        sx = cx + side * 32
        sy = cy - 5
        # 主碎片
        main_shard = [
            (sx - side * 4, sy + 12), (sx + side * 3, sy - 8),
            (sx + side * 16, sy - 18), (sx + side * 20, sy - 8),
            (sx + side * 18, sy + 8), (sx + side * 8, sy + 14),
        ]
        pygame.draw.polygon(surface, theme["rock_dark"], main_shard)
        pygame.draw.polygon(surface, theme["accent"], main_shard, 2)
        
        # 小碎片群
        for frag in range(3):
            f_offset = frag * 6
            frag_pts = [
                (sx + side * (10 + f_offset), sy - 20 - frag * 3),
                (sx + side * (14 + f_offset), sy - 25 - frag * 2),
                (sx + side * (16 + f_offset), sy - 18 - frag * 3),
            ]
            pygame.draw.polygon(surface, theme["rock_main"], frag_pts)
        
        # 热点发光
        glow_surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        glow_alpha = int(80 + heat * 60)
        pygame.draw.circle(glow_surf, (*theme["glow"], glow_alpha), (8, 8), 6)
        surface.blit(glow_surf, (sx + side * 8 - 8, sy - 10))
    
    # === 独特石拳：熔融金属覆盖的拳头 ===
    for side in [-1, 1]:
        fx = cx + side * 46
        fy = cy + 6
        # 不规则陨铁拳
        fist_pts = [
            (fx - side * 8, fy + 10), (fx + side * 4, fy + 14),
            (fx + side * 16, fy + 6), (fx + side * 20, fy - 4),
            (fx + side * 16, fy - 14), (fx + side * 4, fy - 16),
            (fx - side * 6, fy - 8), (fx - side * 8, fy + 2),
        ]
        pygame.draw.polygon(surface, theme["rock_dark"], fist_pts)
        
        # 金属高光层
        metal_pts = [
            (fx, fy + 8), (fx + side * 12, fy + 4),
            (fx + side * 16, fy - 2), (fx + side * 10, fy - 10),
            (fx + side * 2, fy - 8), (fx - side * 2, fy),
        ]
        pygame.draw.polygon(surface, theme["rock_main"], metal_pts)
        
        # 熔融覆层
        melt_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        melt_alpha = int(100 + heat * 80)
        pygame.draw.ellipse(melt_surf, (*theme["crack"], melt_alpha), (5, 8, 20, 14))
        surface.blit(melt_surf, (fx - 10 + side * 5, fy - 12))
    
    # === 独特核心：燃烧陨核 ===
    # 燃烧光晕
    for ring in range(5):
        r = 16 - ring * 2 + int(heat * 4)
        ring_alpha = int(100 + ring * 25 + heat * 50)
        ring_surf = pygame.Surface((r*2+6, r*2+6), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (*theme["glow"], ring_alpha), (r+3, r+3), r, 3)
        surface.blit(ring_surf, (cx - r - 3, cy - 5 - r - 3))
    
    # 陨核
    pygame.draw.circle(surface, theme["core"], (cx, cy - 5), 12)
    pygame.draw.circle(surface, theme["core_bright"], (cx, cy - 5), 8)
    # 金属质感内核
    pygame.draw.circle(surface, theme["accent"], (cx, cy - 5), 5)
    pygame.draw.circle(surface, (255, 255, 255), (cx - 3, cy - 8), 2)
    
    # === 独特头冠：陨石碎片冠 ===
    # 主碎片（参差不齐）
    crown_shards = [
        [(cx - 10, cy - 28), (cx - 12, cy - 42), (cx - 6, cy - 38), (cx - 4, cy - 28)],
        [(cx - 3, cy - 28), (cx, cy - 48), (cx + 5, cy - 44), (cx + 3, cy - 28)],
        [(cx + 8, cy - 28), (cx + 14, cy - 40), (cx + 18, cy - 36), (cx + 12, cy - 28)],
    ]
    for shard in crown_shards:
        pygame.draw.polygon(surface, theme["rock_dark"], shard)
        pygame.draw.polygon(surface, theme["accent"], shard, 1)
    
    # 燃烧边缘
    for i in range(3):
        edge_x = cx - 8 + i * 8
        edge_y = cy - 40 - (i % 2) * 5
        pygame.draw.circle(surface, theme["core"], (edge_x, edge_y), 3)
    
    _draw_charge_bar(surface, cx, cy, theme, t)


def _render_turu_sandstone(surface, t, pulse, visual=None):
    """砂岩遗迹 - 沙漠法老守护者，埃及神殿风格"""
    cx, cy = 60, 60
    theme = TURU_THEMES["turu_sandstone"]
    
    # === 独特特效：沙尘风暴环绕 ===
    sand_drift = abs(math.sin(t * 1.2))
    
    # 多层沙尘漩涡
    for swirl in range(3):
        swirl_angle = t * (0.8 + swirl * 0.2) * (-1 if swirl % 2 else 1)
        swirl_r = 40 + swirl * 6
        swirl_alpha = int(40 - swirl * 10)
        swirl_surf = pygame.Surface((swirl_r*2+10, swirl_r*2+10), pygame.SRCALPHA)
        # 沙尘弧线
        for arc in range(6):
            arc_start = swirl_angle + arc * 1.05
            arc_len = 0.8
            pygame.draw.arc(swirl_surf, (*theme["accent"], swirl_alpha),
                          (5, 5, swirl_r*2, swirl_r*2), arc_start, arc_start + arc_len, 3)
        surface.blit(swirl_surf, (cx - swirl_r - 5, cy - swirl_r - 5))
    
    # 飘落的沙粒
    for i in range(15):
        sand_x = cx - 35 + (i * 5) + math.sin(t * 2 + i) * 8
        sand_y = ((t * 25 + i * 12) % 70) + cy - 35
        sand_alpha = int(50 + math.sin(t * 3 + i) * 25)
        sand_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(sand_surf, (*theme["accent"], sand_alpha), (2, 2), 1)
        surface.blit(sand_surf, (sand_x - 2, sand_y - 2))
    
    # === 独特躯体：埃及方尖碑形态 ===
    # 梯形躯干（金字塔式）
    body_outer = [
        (cx - 30, cy + 24), (cx - 38, cy + 8), (cx - 32, cy - 12),
        (cx - 22, cy - 28), (cx, cy - 34), (cx + 22, cy - 28),
        (cx + 32, cy - 12), (cx + 38, cy + 8), (cx + 30, cy + 24),
    ]
    pygame.draw.polygon(surface, theme["rock_dark"], body_outer)
    
    # 中层（砂岩本体）
    body_mid = [
        (cx - 24, cy + 18), (cx - 30, cy + 4), (cx - 26, cy - 10),
        (cx - 18, cy - 22), (cx, cy - 28), (cx + 18, cy - 22),
        (cx + 26, cy - 10), (cx + 30, cy + 4), (cx + 24, cy + 18),
    ]
    pygame.draw.polygon(surface, theme["rock_main"], body_mid)
    
    # 风化层纹（水平线条）
    layer_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    layer_alpha = int(80 + sand_drift * 40)
    for i in range(6):
        ly = cy - 18 + i * 8
        lw = 48 - abs(i - 2.5) * 6
        pygame.draw.line(layer_surf, (*theme["accent"], layer_alpha - i * 8),
                        (cx - lw//2, ly), (cx + lw//2, ly), 2)
    surface.blit(layer_surf, (0, 0))
    
    # === 独特符文：象形文字装饰 ===
    rune_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    rune_alpha = int(120 + sand_drift * 80)
    
    # 中央圣甲虫符号
    pygame.draw.ellipse(rune_surf, (*theme["core"], rune_alpha), (cx - 10, cy - 12, 20, 14))
    pygame.draw.ellipse(rune_surf, (*theme["core_bright"], rune_alpha), (cx - 6, cy - 8, 12, 8))
    # 翅膀
    pygame.draw.arc(rune_surf, (*theme["crack"], rune_alpha),
                   (cx - 25, cy - 15, 20, 20), 0.5, 2.5, 2)
    pygame.draw.arc(rune_surf, (*theme["crack"], rune_alpha),
                   (cx + 5, cy - 15, 20, 20), 0.6, 2.6, 2)
    
    # 象形文字列（两侧）
    for side in [-1, 1]:
        for h in range(4):
            hx = cx + side * 18
            hy = cy - 5 + h * 8
            # 简化象形符号
            symbol = h % 4
            if symbol == 0:  # 眼睛
                pygame.draw.ellipse(rune_surf, (*theme["crack"], rune_alpha - 30),
                                  (hx - 4, hy - 2, 8, 4))
            elif symbol == 1:  # 波浪
                pygame.draw.arc(rune_surf, (*theme["crack"], rune_alpha - 30),
                               (hx - 5, hy - 3, 10, 6), 0, 3.14, 2)
            elif symbol == 2:  # 三角
                pygame.draw.polygon(rune_surf, (*theme["crack"], rune_alpha - 30),
                                   [(hx, hy - 4), (hx - 4, hy + 2), (hx + 4, hy + 2)])
            else:  # 圆点
                pygame.draw.circle(rune_surf, (*theme["crack"], rune_alpha - 30), (hx, hy), 3)
    
    surface.blit(rune_surf, (0, 0))
    
    # === 独特肩甲：狮身人面像肩垫 ===
    for side in [-1, 1]:
        sx = cx + side * 30
        sy = cy - 5
        # 狮爪形肩甲
        claw_pts = [
            (sx - side * 4, sy + 14),
            (sx + side * 4, sy - 6),
            (sx + side * 10, sy - 14),
            (sx + side * 18, sy - 10),
            (sx + side * 16, sy + 2),
            (sx + side * 12, sy + 12),
        ]
        pygame.draw.polygon(surface, theme["rock_dark"], claw_pts)
        pygame.draw.polygon(surface, theme["rock_main"], [
            (sx, sy + 8), (sx + side * 6, sy - 4),
            (sx + side * 14, sy - 6), (sx + side * 12, sy + 6),
        ])
        # 装饰纹
        pygame.draw.line(surface, theme["crack"], (sx + side * 6, sy - 8), (sx + side * 14, sy - 4), 2)
        pygame.draw.line(surface, theme["crack"], (sx + side * 4, sy), (sx + side * 12, sy + 4), 2)
    
    # === 独特石拳：权杖握拳 ===
    for side in [-1, 1]:
        fx = cx + side * 44
        fy = cy + 5
        # 方形握拳
        fist_pts = [
            (fx - side * 6, fy + 12), (fx + side * 8, fy + 14),
            (fx + side * 16, fy + 6), (fx + side * 18, fy - 6),
            (fx + side * 14, fy - 14), (fx + side * 2, fy - 12),
            (fx - side * 6, fy - 4),
        ]
        pygame.draw.polygon(surface, theme["rock_dark"], fist_pts)
        pygame.draw.polygon(surface, theme["rock_main"], [
            (fx, fy + 8), (fx + side * 12, fy + 8),
            (fx + side * 14, fy - 4), (fx + side * 8, fy - 10),
            (fx, fy - 6),
        ])
        
        # 权杖（从拳中伸出）
        staff_x = fx + side * 10
        pygame.draw.line(surface, theme["accent"], (staff_x, fy - 14), (staff_x, fy - 28), 3)
        # 权杖顶部安卡符
        pygame.draw.circle(surface, theme["core"], (staff_x, fy - 30), 4)
        pygame.draw.line(surface, theme["core"], (staff_x, fy - 26), (staff_x, fy - 20), 2)
        pygame.draw.line(surface, theme["core"], (staff_x - 3, fy - 24), (staff_x + 3, fy - 24), 2)
    
    # === 独特核心：太阳神之眼 ===
    # 太阳光芒
    sun_rays = pygame.Surface((120, 120), pygame.SRCALPHA)
    ray_alpha = int(100 + sand_drift * 60)
    for ray in range(12):
        ray_angle = t * 0.5 + ray * 0.523
        ray_len = 18 + (ray % 2) * 6
        rx1 = cx + math.cos(ray_angle) * 10
        ry1 = cy - 5 + math.sin(ray_angle) * 8
        rx2 = cx + math.cos(ray_angle) * ray_len
        ry2 = cy - 5 + math.sin(ray_angle) * ray_len * 0.8
        pygame.draw.line(sun_rays, (*theme["glow"], ray_alpha), (rx1, ry1), (rx2, ry2), 2)
    surface.blit(sun_rays, (0, 0))
    
    # 核心眼睛（荷鲁斯之眼）
    pygame.draw.ellipse(surface, theme["core"], (cx - 12, cy - 10, 24, 12))
    pygame.draw.ellipse(surface, theme["core_bright"], (cx - 8, cy - 8, 16, 8))
    pygame.draw.circle(surface, theme["rock_dark"], (cx, cy - 5), 4)
    pygame.draw.circle(surface, (255, 255, 255), (cx - 2, cy - 6), 2)
    # 眼线装饰
    pygame.draw.line(surface, theme["crack"], (cx + 12, cy - 5), (cx + 20, cy + 5), 2)
    pygame.draw.arc(surface, theme["crack"], (cx - 18, cy - 12, 12, 14), 1.5, 3.5, 2)
    
    # === 独特头冠：法老双冠 ===
    # 下埃及红冠（向后延伸）
    red_crown = [
        (cx - 18, cy - 28), (cx - 22, cy - 35), (cx - 15, cy - 42),
        (cx + 5, cy - 45), (cx + 18, cy - 40), (cx + 22, cy - 35),
        (cx + 15, cy - 28),
    ]
    pygame.draw.polygon(surface, theme["rock_main"], red_crown)
    pygame.draw.polygon(surface, theme["crack"], red_crown, 2)
    
    # 上埃及白冠（中央高耸）
    white_crown = [
        (cx - 6, cy - 35), (cx - 4, cy - 55), (cx + 4, cy - 55), (cx + 6, cy - 35),
    ]
    pygame.draw.polygon(surface, theme["rock_light"], white_crown)
    pygame.draw.polygon(surface, theme["crack"], white_crown, 1)
    
    # 眼镜蛇装饰
    pygame.draw.ellipse(surface, theme["core"], (cx - 4, cy - 58, 8, 6))
    pygame.draw.circle(surface, theme["core_bright"], (cx, cy - 56), 2)
    
    _draw_charge_bar(surface, cx, cy, theme, t)


def _render_turu_ice(surface, t, pulse, visual=None):
    """冰川巨人 - 极地冰霜泰坦，永恒冰封形态"""
    cx, cy = 60, 60
    theme = TURU_THEMES["turu_ice"]
    
    # === 独特特效：暴风雪漩涡 ===
    frost = abs(math.sin(t * 2))
    
    # 冰霜漩涡环
    for blizzard in range(4):
        b_angle = t * (1.2 - blizzard * 0.2) * (-1 if blizzard % 2 else 1)
        b_r = 38 + blizzard * 5
        b_alpha = int(50 - blizzard * 10)
        b_surf = pygame.Surface((b_r*2+10, b_r*2+10), pygame.SRCALPHA)
        # 断续风环
        for seg in range(8):
            seg_start = b_angle + seg * 0.785
            seg_len = 0.5 + math.sin(t * 3 + seg) * 0.2
            pygame.draw.arc(b_surf, (*theme["glow"], b_alpha),
                          (5, 5, b_r*2, b_r*2), seg_start, seg_start + seg_len, 2)
        surface.blit(b_surf, (cx - b_r - 5, cy - b_r - 5))
    
    # 飘落雪花（大型六角形）
    for i in range(8):
        snow_x = cx - 30 + (i * 9) + math.sin(t * 1.5 + i) * 10
        snow_y = ((t * 20 + i * 15) % 70) + cy - 35
        snow_rot = t * 2 + i
        snow_alpha = int(120 + frost * 60)
        snow_surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        # 六角雪花
        for arm in range(6):
            arm_angle = snow_rot + arm * 1.047
            # 主臂
            ax1 = 8 + math.cos(arm_angle) * 2
            ay1 = 8 + math.sin(arm_angle) * 2
            ax2 = 8 + math.cos(arm_angle) * 7
            ay2 = 8 + math.sin(arm_angle) * 7
            pygame.draw.line(snow_surf, (255, 255, 255, snow_alpha), (ax1, ay1), (ax2, ay2), 1)
            # 侧枝
            mid_x = 8 + math.cos(arm_angle) * 4
            mid_y = 8 + math.sin(arm_angle) * 4
            for branch in [-0.5, 0.5]:
                bx = mid_x + math.cos(arm_angle + branch) * 2
                by = mid_y + math.sin(arm_angle + branch) * 2
                pygame.draw.line(snow_surf, (255, 255, 255, snow_alpha - 30), 
                               (mid_x, mid_y), (bx, by), 1)
        surface.blit(snow_surf, (snow_x - 8, snow_y - 8))
    
    # === 独特躯体：冰晶几何体 ===
    # 多边形冰体
    ice_body = [
        (cx - 30, cy + 20), (cx - 38, cy + 2), (cx - 34, cy - 16),
        (cx - 20, cy - 30), (cx, cy - 36), (cx + 20, cy - 30),
        (cx + 34, cy - 16), (cx + 38, cy + 2), (cx + 30, cy + 20),
    ]
    pygame.draw.polygon(surface, theme["rock_dark"], ice_body)
    
    # 透明冰层
    ice_layer = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.polygon(ice_layer, (*theme["rock_main"], 180), [
        (cx - 26, cy + 16), (cx - 32, cy), (cx - 28, cy - 14),
        (cx - 16, cy - 26), (cx, cy - 30), (cx + 16, cy - 26),
        (cx + 28, cy - 14), (cx + 32, cy), (cx + 26, cy + 16),
    ])
    surface.blit(ice_layer, (0, 0))
    
    # 冰晶棱面（高对比度反光）
    facet_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    facet_alpha = int(100 + frost * 80)
    # 大棱面
    pygame.draw.polygon(facet_surf, (255, 255, 255, facet_alpha), [
        (cx - 22, cy + 12), (cx - 30, cy - 8), (cx - 18, cy - 22), (cx - 8, cy)
    ])
    pygame.draw.polygon(facet_surf, (255, 255, 255, facet_alpha - 20), [
        (cx + 22, cy + 12), (cx + 30, cy - 8), (cx + 18, cy - 22), (cx + 8, cy)
    ])
    # 小棱面
    pygame.draw.polygon(facet_surf, (255, 255, 255, facet_alpha - 30), [
        (cx - 8, cy - 15), (cx, cy - 28), (cx + 8, cy - 15), (cx, cy - 5)
    ])
    surface.blit(facet_surf, (0, 0))
    
    # 冰霜裂纹（锋利线条）
    frost_crack = pygame.Surface((120, 120), pygame.SRCALPHA)
    crack_alpha = int(150 + frost * 80)
    pygame.draw.line(frost_crack, (255, 255, 255, crack_alpha),
                    (cx - 18, cy - 20), (cx - 25, cy + 15), 2)
    pygame.draw.line(frost_crack, (255, 255, 255, crack_alpha),
                    (cx + 15, cy - 22), (cx + 22, cy + 12), 2)
    pygame.draw.line(frost_crack, (255, 255, 255, crack_alpha - 30),
                    (cx - 12, cy - 5), (cx + 10, cy - 8), 1)
    pygame.draw.line(frost_crack, (255, 255, 255, crack_alpha - 30),
                    (cx - 5, cy + 8), (cx + 8, cy + 5), 1)
    surface.blit(frost_crack, (0, 0))
    
    # === 独特肩甲：冰刺簇肩甲 ===
    for side in [-1, 1]:
        sx = cx + side * 30
        sy = cy - 6
        # 主冰刺
        main_spike = [
            (sx - side * 4, sy + 10),
            (sx + side * 6, sy - 8),
            (sx + side * 12, sy - 26),
            (sx + side * 10, sy - 10),
            (sx + side * 8, sy + 8),
        ]
        pygame.draw.polygon(surface, theme["rock_main"], main_spike)
        pygame.draw.polygon(surface, (255, 255, 255), main_spike, 2)
        
        # 副冰刺（3根小刺）
        for spike in range(3):
            s_offset = spike * 5 - 5
            spike_pts = [
                (sx + side * (8 + s_offset), sy + 4 - spike * 4),
                (sx + side * (14 + s_offset), sy - 18 - spike * 3),
                (sx + side * (12 + s_offset), sy - 6 - spike * 3),
            ]
            pygame.draw.polygon(surface, theme["rock_light"], spike_pts)
            pygame.draw.polygon(surface, (255, 255, 255), spike_pts, 1)
        
        # 冰霜光晕
        glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        glow_alpha = int(40 + frost * 30)
        pygame.draw.circle(glow_surf, (*theme["glow"], glow_alpha), (10, 10), 8)
        surface.blit(glow_surf, (sx + side * 6 - 10, sy - 15))
    
    # === 独特石拳：冰拳 ===
    for side in [-1, 1]:
        fx = cx + side * 45
        fy = cy + 5
        # 棱角分明的冰拳
        ice_fist = [
            (fx - side * 8, fy + 10), (fx + side * 6, fy + 12),
            (fx + side * 16, fy + 4), (fx + side * 20, fy - 6),
            (fx + side * 14, fy - 16), (fx + side * 2, fy - 14),
            (fx - side * 6, fy - 6),
        ]
        pygame.draw.polygon(surface, theme["rock_main"], ice_fist)
        pygame.draw.polygon(surface, (255, 255, 255), ice_fist, 2)
        
        # 冰晶纹理
        pygame.draw.line(surface, (255, 255, 255), 
                        (fx + side * 4, fy - 10), (fx + side * 14, fy - 4), 1)
        pygame.draw.line(surface, (255, 255, 255), 
                        (fx + side * 2, fy), (fx + side * 12, fy + 4), 1)
        
        # 冰锥指节
        for k in range(3):
            kx = fx + side * (8 + k * 4)
            ky = fy - 14 + k * 5
            ice_knuckle = [(kx, ky - 8), (kx - 2, ky), (kx + 2, ky)]
            pygame.draw.polygon(surface, (255, 255, 255), ice_knuckle)
    
    # === 独特核心：冰封之心 ===
    # 冰霜光环
    for ring in range(5):
        r = 15 - ring * 2 + int(frost * 3)
        ring_alpha = int(80 + ring * 30 + frost * 50)
        ring_surf = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (*theme["glow"], ring_alpha), (r+2, r+2), r, 2)
        surface.blit(ring_surf, (cx - r - 2, cy - 5 - r - 2))
    
    # 核心冰晶
    pygame.draw.circle(surface, theme["core"], (cx, cy - 5), 11)
    pygame.draw.circle(surface, theme["core_bright"], (cx, cy - 5), 7)
    # 雪花内核
    for arm in range(6):
        arm_angle = t * 0.5 + arm * 1.047
        ax = cx + math.cos(arm_angle) * 5
        ay = cy - 5 + math.sin(arm_angle) * 5
        pygame.draw.line(surface, (255, 255, 255), (cx, cy - 5), (ax, ay), 1)
    pygame.draw.circle(surface, (255, 255, 255), (cx - 2, cy - 8), 2)
    
    # === 独特头冠：冰王之冠 ===
    # 中央大冰柱
    main_ice = [
        (cx - 5, cy - 28), (cx - 3, cy - 52), (cx + 3, cy - 52), (cx + 5, cy - 28)
    ]
    pygame.draw.polygon(surface, theme["rock_light"], main_ice)
    pygame.draw.polygon(surface, (255, 255, 255), main_ice, 2)
    
    # 侧面冰柱群（递减高度）
    ice_heights = [(-12, 40), (-8, 46), (-4, 44), (4, 42), (8, 44), (12, 38)]
    for ix, ih in ice_heights:
        ice_pts = [
            (cx + ix - 2, cy - 28),
            (cx + ix, cy - ih),
            (cx + ix + 2, cy - 28),
        ]
        pygame.draw.polygon(surface, theme["rock_main"], ice_pts)
        pygame.draw.polygon(surface, (255, 255, 255), ice_pts, 1)
    
    # 冰霜光芒
    for ray in range(5):
        ray_x = cx - 8 + ray * 4
        ray_y = cy - 48 + abs(ray - 2) * 4
        pygame.draw.circle(surface, (255, 255, 255), (ray_x, ray_y), 2)
    
    _draw_charge_bar(surface, cx, cy, theme, t)


# =============================================================================
#   系列四：终极形态系列 (volcanic, rusty, golden)
# =============================================================================

def _render_turu_volcanic(surface, t, pulse, visual=None):
    """火山领主 - 末日火山喷发形态，岩浆瀑布与火山灰"""
    cx, cy = 60, 60
    theme = TURU_THEMES["turu_volcanic"]
    
    # === 独特特效：火山喷发冲击波 ===
    eruption = abs(math.sin(t * 3))
    
    # 喷发冲击波（向外扩散）
    for wave in range(4):
        wave_age = (t * 0.8 + wave * 0.5) % 2
        if wave_age < 1.5:
            wave_r = int(20 + wave_age * 35)
            wave_alpha = int((1.5 - wave_age) * 80)
            wave_surf = pygame.Surface((wave_r*2+6, wave_r*2+6), pygame.SRCALPHA)
            pygame.draw.circle(wave_surf, (*theme["glow"], wave_alpha), 
                             (wave_r+3, wave_r+3), wave_r, 4)
            surface.blit(wave_surf, (cx - wave_r - 3, cy - wave_r - 3))
    
    # 火山灰柱（向上喷射）
    ash_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for ash in range(15):
        ash_age = (t * 2 + ash * 0.3) % 1.5
        ash_x = cx - 15 + (ash % 5) * 8 + math.sin(t * 4 + ash) * 5
        ash_y = cy - 30 - ash_age * 40
        ash_alpha = int((1.5 - ash_age) * 100)
        ash_size = int(3 - ash_age * 1.5)
        if ash_size > 0 and ash_alpha > 0:
            pygame.draw.circle(ash_surf, (*theme["rock_light"], ash_alpha), 
                             (int(ash_x), int(ash_y)), ash_size)
    surface.blit(ash_surf, (0, 0))
    
    # 岩浆飞溅粒子
    for i in range(12):
        p_age = (t * 1.5 + i * 0.35) % 1.2
        p_angle = -1.57 + (i - 6) * 0.25 + math.sin(t + i) * 0.2
        p_speed = 30 + (i % 4) * 8
        px = cx + math.cos(p_angle) * p_age * p_speed
        py = cy - 20 + math.sin(p_angle) * p_age * p_speed + p_age * p_age * 25
        p_alpha = max(0, min(255, int((1.2 - p_age) * 220)))
        if p_alpha > 0 and py < cy + 40:
            p_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (*theme["core"], p_alpha), (5, 5), 4)
            pygame.draw.circle(p_surf, (*theme["core_bright"], p_alpha), (5, 5), 2)
            surface.blit(p_surf, (px - 5, py - 5))
    
    # === 独特躯体：火山口形态躯体 ===
    # 外层熔岩壳
    body_outer = [
        (cx - 32, cy + 24), (cx - 42, cy + 5), (cx - 38, cy - 15),
        (cx - 25, cy - 30), (cx, cy - 36), (cx + 25, cy - 30),
        (cx + 38, cy - 15), (cx + 42, cy + 5), (cx + 32, cy + 24),
    ]
    pygame.draw.polygon(surface, theme["rock_dark"], body_outer)
    
    # 火山口凹陷（顶部）
    crater_body = [
        (cx - 18, cy - 25), (cx - 22, cy - 32), (cx, cy - 36),
        (cx + 22, cy - 32), (cx + 18, cy - 25), (cx, cy - 20),
    ]
    pygame.draw.polygon(surface, theme["rock_main"], crater_body)
    
    # 熔岩流（从裂缝涌出）
    lava_flow = pygame.Surface((120, 120), pygame.SRCALPHA)
    lava_pulse = abs(math.sin(t * 4))
    lava_alpha = int(220 + lava_pulse * 35)
    
    # 主熔岩河（4条）
    rivers = [
        [(cx, cy - 5), (cx - 15, cy + 8), (cx - 25, cy + 22), (cx - 30, cy + 35)],
        [(cx, cy - 5), (cx + 12, cy + 10), (cx + 22, cy + 24), (cx + 28, cy + 38)],
        [(cx - 8, cy - 15), (cx - 22, cy - 8), (cx - 35, cy + 5)],
        [(cx + 8, cy - 15), (cx + 22, cy - 8), (cx + 35, cy + 5)],
    ]
    for river in rivers:
        for i in range(len(river) - 1):
            width = 5 - i
            pygame.draw.line(lava_flow, (*theme["crack"], lava_alpha),
                           river[i], river[i+1], max(2, width))
    
    # 熔岩池（底部积聚）
    pygame.draw.ellipse(lava_flow, (*theme["core"], lava_alpha - 30), 
                       (cx - 25, cy + 18, 50, 16))
    pygame.draw.ellipse(lava_flow, (*theme["core_bright"], lava_alpha - 50), 
                       (cx - 18, cy + 21, 36, 10))
    surface.blit(lava_flow, (0, 0))
    
    # === 独特肩甲：熔岩瀑布肩甲 ===
    for side in [-1, 1]:
        sx = cx + side * 32
        sy = cy - 5
        # 肩甲岩体
        shoulder_pts = [
            (sx - side * 6, sy + 14), (sx + side * 4, sy - 10),
            (sx + side * 18, sy - 16), (sx + side * 22, sy - 4),
            (sx + side * 18, sy + 12), (sx + side * 6, sy + 16),
        ]
        pygame.draw.polygon(surface, theme["rock_dark"], shoulder_pts)
        
        # 熔岩瀑布（从肩甲流下）
        for fall in range(4):
            fall_x = sx + side * (8 + fall * 3)
            fall_phase = (t * 3 + fall * 0.4) % 1
            for drip in range(5):
                drip_y = sy + 12 + drip * 6 + fall_phase * 6
                drip_alpha = int(200 - drip * 35)
                if drip_alpha > 0:
                    pygame.draw.circle(surface, (*theme["core"], drip_alpha), 
                                     (fall_x, int(drip_y)), 3 - drip // 2)
        
        # 肩甲顶部熔岩池
        pygame.draw.ellipse(surface, theme["core"], 
                           (sx + side * 6 - 8, sy - 14, 16, 8))
    
    # === 独特石拳：岩浆覆盖的毁灭拳 ===
    for side in [-1, 1]:
        fx = cx + side * 46
        fy = cy + 6
        # 岩石拳体
        fist_pts = [
            (fx - side * 8, fy + 12), (fx + side * 6, fy + 14),
            (fx + side * 18, fy + 4), (fx + side * 22, fy - 8),
            (fx + side * 16, fy - 18), (fx + side * 2, fy - 16),
            (fx - side * 6, fy - 6),
        ]
        pygame.draw.polygon(surface, theme["rock_dark"], fist_pts)
        
        # 熔岩覆层（流动效果）
        lava_fist = pygame.Surface((40, 40), pygame.SRCALPHA)
        lf_alpha = int(150 + lava_pulse * 80)
        pygame.draw.polygon(lava_fist, (*theme["crack"], lf_alpha), [
            (20, 22), (20 + side * 14, 20), (20 + side * 18, 12),
            (20 + side * 12, 6), (20 + side * 4, 8), (20, 15),
        ])
        surface.blit(lava_fist, (fx - 20, fy - 18))
        
        # 火焰环绕
        for flame in range(5):
            f_angle = t * 5 + flame * 1.26 + side
            f_dist = 14 + math.sin(t * 8 + flame) * 3
            flame_x = fx + math.cos(f_angle) * f_dist
            flame_y = fy + math.sin(f_angle) * f_dist * 0.7
            pygame.draw.circle(surface, theme["core_bright"], 
                             (int(flame_x), int(flame_y)), 3)
    
    # === 独特核心：熔岩心室 ===
    # 熔岩脉动光晕
    for ring in range(5):
        r = 16 - ring * 2 + int(eruption * 5)
        ring_alpha = min(255, int(120 + ring * 20 + eruption * 40))
        ring_surf = pygame.Surface((r*2+6, r*2+6), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (*theme["glow"], ring_alpha), (r+3, r+3), r, 3)
        surface.blit(ring_surf, (cx - r - 3, cy - 5 - r - 3))
    
    # 熔岩核心（剧烈脉动）
    core_r = int(12 + eruption * 4)
    pygame.draw.circle(surface, theme["core"], (cx, cy - 5), core_r)
    pygame.draw.circle(surface, theme["core_bright"], (cx, cy - 5), int(core_r * 0.7))
    pygame.draw.circle(surface, (255, 255, 200), (cx, cy - 5), int(core_r * 0.4))
    # 熔岩气泡
    for bubble in range(3):
        b_angle = t * 3 + bubble * 2.09
        bx = cx + math.cos(b_angle) * 6
        by = cy - 5 + math.sin(b_angle) * 4
        pygame.draw.circle(surface, (255, 200, 100), (int(bx), int(by)), 2)
    
    # === 独特头冠：火山喷发冠 ===
    # 火山口边缘
    crater_crown = [
        (cx - 20, cy - 28), (cx - 16, cy - 35), (cx - 8, cy - 32),
        (cx, cy - 38), (cx + 8, cy - 32), (cx + 16, cy - 35), (cx + 20, cy - 28),
    ]
    pygame.draw.polygon(surface, theme["rock_dark"], crater_crown)
    
    # 喷发火柱
    for i in range(9):
        col_x = cx - 16 + i * 4
        col_phase = t * 10 + i * 0.8
        col_h = 15 + int(abs(math.sin(col_phase)) * 18)
        col_sway = math.sin(col_phase * 0.5) * 4
        # 外焰
        outer = [(col_x, cy - 35), (col_x - 4 + col_sway, cy - 35 - col_h),
                 (col_x + 4 + col_sway, cy - 35 - col_h)]
        pygame.draw.polygon(surface, theme["core"], outer)
        # 内焰
        inner_h = col_h * 0.6
        inner = [(col_x, cy - 35), (col_x - 2 + col_sway * 0.5, cy - 35 - inner_h),
                 (col_x + 2 + col_sway * 0.5, cy - 35 - inner_h)]
        pygame.draw.polygon(surface, theme["core_bright"], inner)
    
    _draw_charge_bar(surface, cx, cy, theme, t)


def _render_turu_rusty(surface, t, pulse, visual=None):
    """锈蚀古物 - 千年废墟遗迹，苔藓与铁锈交织"""
    cx, cy = 60, 60
    theme = TURU_THEMES["turu_rusty"]
    
    # === 独特特效：衰败尘埃与孢子 ===
    decay = abs(math.sin(t * 0.6))
    
    # 锈粉飘落
    rust_dust = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(12):
        dust_x = cx - 35 + (i * 6) + math.sin(t * 0.8 + i) * 8
        dust_y = ((t * 12 + i * 10) % 70) + cy - 35
        dust_alpha = int(40 + math.sin(t + i) * 20)
        dust_size = 1 + (i % 2)
        pygame.draw.circle(rust_dust, (*theme["accent"], dust_alpha), 
                          (int(dust_x), int(dust_y)), dust_size)
    surface.blit(rust_dust, (0, 0))
    
    # 苔藓孢子（缓慢上升）
    for i in range(8):
        spore_x = cx - 25 + (i * 7) + math.sin(t * 0.5 + i) * 6
        spore_y = cy + 30 - ((t * 8 + i * 12) % 60)
        spore_alpha = int(50 + math.sin(t * 1.5 + i) * 30)
        spore_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(spore_surf, (*theme["core"], spore_alpha), (4, 4), 2)
        # 孢子尾迹
        pygame.draw.line(spore_surf, (*theme["core"], spore_alpha - 20),
                        (4, 4), (4, 7), 1)
        surface.blit(spore_surf, (spore_x - 4, spore_y - 4))
    
    # 衰败光环（微弱闪烁）
    for ring in range(2):
        r = 40 + ring * 8 + int(decay * 3)
        ring_alpha = int(25 - ring * 8)
        ring_surf = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
        # 断续的破碎环
        for seg in range(6):
            seg_start = t * 0.2 + seg * 1.05
            seg_len = 0.6 + math.sin(t + seg) * 0.2
            pygame.draw.arc(ring_surf, (*theme["glow"], ring_alpha),
                          (2, 2, r*2, r*2), seg_start, seg_start + seg_len, 2)
        surface.blit(ring_surf, (cx - r - 2, cy - r - 2))
    
    # === 独特躯体：破损锈蚀石体 ===
    # 不规则破损外形
    body_rusted = [
        (cx - 30, cy + 22), (cx - 38, cy + 4), (cx - 34, cy - 14),
        (cx - 22, cy - 28), (cx - 5, cy - 32), (cx + 10, cy - 30),
        (cx + 28, cy - 24), (cx + 36, cy - 10), (cx + 38, cy + 6),
        (cx + 30, cy + 20), (cx + 12, cy + 26), (cx - 8, cy + 24),
    ]
    pygame.draw.polygon(surface, theme["rock_dark"], body_rusted)
    
    # 破损缺口
    holes = [(cx - 18, cy + 8, 7), (cx + 22, cy - 5, 6), 
             (cx - 8, cy - 20, 5), (cx + 10, cy + 15, 4)]
    for hx, hy, hr in holes:
        pygame.draw.circle(surface, (40, 35, 30), (hx, hy), hr)
        pygame.draw.circle(surface, theme["rock_dark"], (hx, hy), hr, 2)
    
    # 锈斑层（多层叠加）
    rust_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    rust_alpha = int(100 + decay * 40)
    # 大锈斑
    rust_spots = [(cx - 15, cy - 5, 12), (cx + 12, cy + 8, 10),
                  (cx - 5, cy + 18, 8), (cx + 18, cy - 15, 9),
                  (cx - 22, cy + 12, 7)]
    for rx, ry, rr in rust_spots:
        pygame.draw.circle(rust_surf, (*theme["accent"], rust_alpha), (rx, ry), rr)
        pygame.draw.circle(rust_surf, (*theme["accent"], rust_alpha - 30), 
                          (rx - 2, ry - 2), int(rr * 0.6))
    # 锈斑纹理线
    for i in range(8):
        angle = i * 0.785 + 0.3
        length = 15 + (i % 3) * 5
        rx1 = cx + math.cos(angle) * 8
        ry1 = cy + math.sin(angle) * 6
        rx2 = cx + math.cos(angle) * length
        ry2 = cy + math.sin(angle) * length * 0.8
        pygame.draw.line(rust_surf, (*theme["accent"], rust_alpha - 40),
                        (rx1, ry1), (rx2, ry2), 2)
    surface.blit(rust_surf, (0, 0))
    
    # 苔藓覆盖区
    moss_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    moss_alpha = int(90 + decay * 40)
    moss_areas = [
        (cx - 25, cy - 2, 18, 14), (cx + 10, cy - 20, 14, 10),
        (cx - 12, cy + 12, 20, 12), (cx + 15, cy + 5, 12, 10),
    ]
    for mx, my, mw, mh in moss_areas:
        pygame.draw.ellipse(moss_surf, (*theme["core"], moss_alpha), (mx, my, mw, mh))
        # 苔藓纹理点
        for j in range(4):
            jx = mx + 4 + j * 4
            jy = my + 3 + (j % 2) * 4
            pygame.draw.circle(moss_surf, (*theme["core_bright"], moss_alpha - 20), 
                             (jx, jy), 2)
    surface.blit(moss_surf, (0, 0))
    
    # === 独特肩甲：残破锈蚀肩甲 ===
    for side in [-1, 1]:
        sx = cx + side * 28
        sy = cy - 5
        # 破损肩甲主体
        shoulder_pts = [
            (sx - side * 4, sy + 10), (sx + side * 5, sy - 8),
            (sx + side * 14, sy - 14), (sx + side * 16, sy - 2),
            (sx + side * 12, sy + 12), (sx + side * 4, sy + 14),
        ]
        pygame.draw.polygon(surface, theme["rock_dark"], shoulder_pts)
        
        # 破损缺口
        pygame.draw.circle(surface, (40, 35, 30), (sx + side * 10, sy - 6), 5)
        pygame.draw.circle(surface, (40, 35, 30), (sx + side * 6, sy + 6), 4)
        
        # 锈蚀边缘
        pygame.draw.polygon(surface, theme["accent"], shoulder_pts, 2)
        
        # 苔藓簇
        pygame.draw.ellipse(surface, theme["core"], 
                           (sx + side * 2 - 5, sy - 10, 10, 6))
    
    # === 独特石拳：风化破损拳 ===
    for side in [-1, 1]:
        fx = cx + side * 44
        fy = cy + 5
        # 破损拳头轮廓
        fist_pts = [
            (fx - side * 6, fy + 10), (fx + side * 5, fy + 12),
            (fx + side * 14, fy + 4), (fx + side * 16, fy - 6),
            (fx + side * 12, fy - 14), (fx + side * 2, fy - 12),
            (fx - side * 5, fy - 4),
        ]
        pygame.draw.polygon(surface, theme["rock_dark"], fist_pts)
        
        # 风化纹理
        pygame.draw.line(surface, theme["accent"], 
                        (fx + side * 4, fy - 8), (fx + side * 12, fy + 2), 2)
        pygame.draw.line(surface, theme["accent"], 
                        (fx + side * 2, fy + 4), (fx + side * 10, fy + 8), 2)
        
        # 缺失的指节
        pygame.draw.circle(surface, (40, 35, 30), (fx + side * 10, fy - 8), 4)
        
        # 苔藓附着
        pygame.draw.ellipse(surface, theme["core"],
                           (fx - 4, fy - 2, 8, 5))
    
    # === 独特核心：衰弱暗淡核心 ===
    # 微弱脉动（不稳定）
    weak_pulse = abs(math.sin(t * 1.5))
    flicker = 1 if (int(t * 10) % 7 > 1) else 0.6  # 闪烁效果
    
    # 暗淡光环
    for ring in range(3):
        r = 12 - ring * 2 + int(weak_pulse * 2)
        ring_alpha = int((40 + ring * 20) * flicker)
        ring_surf = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (*theme["glow"], ring_alpha), (r+2, r+2), r, 2)
        surface.blit(ring_surf, (cx - r - 2, cy - 5 - r - 2))
    
    # 衰弱核心
    core_alpha = int(180 * flicker)
    pygame.draw.circle(surface, (*theme["core"][:3], core_alpha), (cx, cy - 5), 9)
    pygame.draw.circle(surface, (*theme["core_bright"][:3], core_alpha), (cx, cy - 5), 5)
    # 裂纹
    for crack in range(4):
        c_angle = crack * 1.57 + 0.4
        cx1 = cx + math.cos(c_angle) * 3
        cy1 = cy - 5 + math.sin(c_angle) * 3
        cx2 = cx + math.cos(c_angle) * 8
        cy2 = cy - 5 + math.sin(c_angle) * 6
        pygame.draw.line(surface, theme["rock_dark"], (cx1, cy1), (cx2, cy2), 1)
    
    # === 独特头冠：断裂残冠 ===
    # 残破的冠基
    crown_base = [
        (cx - 14, cy - 28), (cx - 10, cy - 32), (cx + 8, cy - 30), (cx + 14, cy - 28)
    ]
    pygame.draw.polygon(surface, theme["rock_dark"], crown_base)
    
    # 断裂的冠尖（只剩两根）
    left_spike = [(cx - 10, cy - 32), (cx - 12, cy - 42), (cx - 6, cy - 38), (cx - 4, cy - 32)]
    pygame.draw.polygon(surface, theme["rock_main"], left_spike)
    
    right_spike = [(cx + 6, cy - 30), (cx + 10, cy - 44), (cx + 14, cy - 36), (cx + 10, cy - 30)]
    pygame.draw.polygon(surface, theme["rock_main"], right_spike)
    
    # 中央断裂痕迹
    pygame.draw.line(surface, theme["accent"], (cx - 2, cy - 32), (cx + 2, cy - 34), 3)
    
    # 苔藓覆盖冠部
    pygame.draw.ellipse(surface, theme["core"], (cx - 8, cy - 34, 12, 6))
    
    _draw_charge_bar(surface, cx, cy, theme, t)


def _render_turu_golden(surface, t, pulse, visual=None):
    """黄金神帝 - 至尊皇帝形态，神圣辉煌的终极黄金巨像"""
    cx, cy = 60, 60
    theme = TURU_THEMES["turu_golden"]
    
    # === 独特特效：神圣辉光与宝石尘埃 ===
    radiance = abs(math.sin(t * 1.5))
    sparkle = abs(math.sin(t * 4))
    
    # 神圣十字光芒
    cross_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    cross_alpha = int(50 + radiance * 40)
    cross_len = 50 + int(radiance * 10)
    pygame.draw.line(cross_surf, (*theme["glow"], cross_alpha),
                    (cx, cy - cross_len), (cx, cy + cross_len - 10), 4)
    pygame.draw.line(cross_surf, (*theme["glow"], cross_alpha),
                    (cx - cross_len + 10, cy), (cx + cross_len - 10, cy), 4)
    # 斜十字
    diag_len = int(cross_len * 0.6)
    pygame.draw.line(cross_surf, (*theme["glow"], cross_alpha - 20),
                    (cx - diag_len, cy - diag_len + 8), (cx + diag_len, cy + diag_len - 12), 3)
    pygame.draw.line(cross_surf, (*theme["glow"], cross_alpha - 20),
                    (cx + diag_len, cy - diag_len + 8), (cx - diag_len, cy + diag_len - 12), 3)
    surface.blit(cross_surf, (0, 0))
    
    # 多层同心神圣环
    for ring in range(4):
        r = 35 + ring * 10 + int(radiance * 5)
        ring_alpha = int(80 - ring * 15)
        ring_surf = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
        # 金色实心环
        pygame.draw.circle(ring_surf, (*theme["glow"], ring_alpha), (r+2, r+2), r, 3)
        # 白色内边
        if ring < 2:
            pygame.draw.circle(ring_surf, (255, 255, 255, ring_alpha - 20), (r+2, r+2), r - 1, 1)
        surface.blit(ring_surf, (cx - r - 2, cy - r - 2))
    
    # 宝石尘埃（上升的金色星辰）
    for i in range(15):
        dust_x = cx - 40 + (i * 6) + math.sin(t * 0.8 + i * 0.5) * 10
        dust_y = cy + 35 - ((t * 15 + i * 8) % 75)
        dust_alpha = int(150 + sparkle * 100)
        dust_size = 2 + (i % 3)
        dust_surf = pygame.Surface((dust_size*2+4, dust_size*2+4), pygame.SRCALPHA)
        # 星形尘埃
        pygame.draw.circle(dust_surf, (*theme["core"], dust_alpha), (dust_size+2, dust_size+2), dust_size)
        pygame.draw.circle(dust_surf, (255, 255, 255, dust_alpha), (dust_size+2, dust_size+2), dust_size//2+1)
        surface.blit(dust_surf, (dust_x - dust_size - 2, dust_y - dust_size - 2))
    
    # 光芒射线（从核心向外）
    ray_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for ray in range(8):
        ray_angle = t * 0.3 + ray * 0.785
        ray_alpha = int(40 + sparkle * 40)
        ray_len = 45 + math.sin(t * 2 + ray) * 8
        rx1 = cx + math.cos(ray_angle) * 12
        ry1 = cy + math.sin(ray_angle) * 10
        rx2 = cx + math.cos(ray_angle) * ray_len
        ry2 = cy + math.sin(ray_angle) * ray_len * 0.7
        pygame.draw.line(ray_surf, (*theme["glow"], ray_alpha), (rx1, ry1), (rx2, ry2), 2)
    surface.blit(ray_surf, (0, 0))
    
    # === 独特躯体：黄金神像雕塑 ===
    # 精雕细琢的躯体轮廓
    body_golden = [
        (cx - 28, cy + 20), (cx - 36, cy + 2), (cx - 32, cy - 16),
        (cx - 18, cy - 30), (cx, cy - 34), (cx + 18, cy - 30),
        (cx + 32, cy - 16), (cx + 36, cy + 2), (cx + 28, cy + 20),
        (cx + 10, cy + 24), (cx - 10, cy + 24),
    ]
    pygame.draw.polygon(surface, theme["rock_main"], body_golden)
    
    # 金色渐变层
    inner_body = [
        (cx - 22, cy + 15), (cx - 28, cy + 2), (cx - 24, cy - 12),
        (cx - 12, cy - 24), (cx, cy - 27), (cx + 12, cy - 24),
        (cx + 24, cy - 12), (cx + 28, cy + 2), (cx + 22, cy + 15),
        (cx + 6, cy + 18), (cx - 6, cy + 18),
    ]
    pygame.draw.polygon(surface, theme["rock_light"], inner_body)
    
    # 黄金浮雕纹饰
    engrave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    engrave_alpha = int(200 + sparkle * 55)
    
    # 胸部皇家徽章（盾形）
    badge_pts = [
        (cx, cy - 18), (cx - 12, cy - 8), (cx - 10, cy + 8),
        (cx, cy + 14), (cx + 10, cy + 8), (cx + 12, cy - 8),
    ]
    pygame.draw.polygon(engrave_surf, (*theme["crack"], engrave_alpha), badge_pts, 2)
    
    # 徽章内饰（皇冠图案）
    pygame.draw.polygon(engrave_surf, (*theme["crack"], engrave_alpha - 30),
                       [(cx - 6, cy - 6), (cx - 4, cy - 12), (cx, cy - 8), 
                        (cx + 4, cy - 12), (cx + 6, cy - 6)], 1)
    
    # 卷草纹饰（两侧）
    for side in [-1, 1]:
        for i in range(3):
            scroll_x = cx + side * (18 + i * 4)
            scroll_y = cy - 5 + i * 6
            pygame.draw.circle(engrave_surf, (*theme["crack"], engrave_alpha - 40),
                             (scroll_x, scroll_y), 3, 1)
    
    surface.blit(engrave_surf, (0, 0))
    
    # === 独特肩甲：皇帝龙肩甲 ===
    for side in [-1, 1]:
        sx = cx + side * 32
        sy = cy - 6
        # 多层华丽肩甲
        outer_shoulder = [
            (sx - side * 6, sy + 12), (sx + side * 4, sy - 12),
            (sx + side * 18, sy - 18), (sx + side * 22, sy - 4),
            (sx + side * 18, sy + 8), (sx + side * 8, sy + 14),
        ]
        pygame.draw.polygon(surface, theme["rock_dark"], outer_shoulder)
        
        inner_shoulder = [
            (sx - side * 2, sy + 6), (sx + side * 6, sy - 8),
            (sx + side * 14, sy - 12), (sx + side * 16, sy - 2),
            (sx + side * 12, sy + 6),
        ]
        pygame.draw.polygon(surface, theme["rock_main"], inner_shoulder)
        
        # 金边
        pygame.draw.polygon(surface, theme["crack"], outer_shoulder, 2)
        
        # 龙头装饰
        dragon_x = sx + side * 18
        dragon_y = sy - 14
        pygame.draw.circle(surface, theme["rock_light"], (dragon_x, dragon_y), 6)
        pygame.draw.circle(surface, theme["crack"], (dragon_x, dragon_y), 6, 2)
        # 龙眼
        pygame.draw.circle(surface, (255, 80, 80), (dragon_x + side * 2, dragon_y - 1), 2)
        
        # 肩甲主宝石
        pygame.draw.circle(surface, theme["core"], (sx + side * 10, sy - 4), 5)
        pygame.draw.circle(surface, (255, 255, 255), (sx + side * 10, sy - 4), 3)
        # 高光
        pygame.draw.circle(surface, (255, 255, 255), (sx + side * 9, sy - 5), 1)
    
    # === 独特石拳：黄金神力拳 ===
    for side in [-1, 1]:
        fx = cx + side * 46
        fy = cy + 4
        
        # 拳头神圣光晕
        fist_glow = pygame.Surface((45, 45), pygame.SRCALPHA)
        fist_alpha = int(70 + radiance * 70)
        for gr in range(3):
            pygame.draw.circle(fist_glow, (*theme["glow"], fist_alpha - gr * 20), 
                             (22, 22), 18 - gr * 3)
        surface.blit(fist_glow, (fx - 22, fy - 22))
        
        # 精雕黄金拳
        fist_pts = [
            (fx - side * 8, fy + 12), (fx + side * 4, fy + 14),
            (fx + side * 16, fy + 6), (fx + side * 20, fy - 6),
            (fx + side * 16, fy - 16), (fx + side * 4, fy - 14),
            (fx - side * 6, fy - 6),
        ]
        pygame.draw.polygon(surface, theme["rock_main"], fist_pts)
        pygame.draw.polygon(surface, theme["crack"], fist_pts, 2)
        
        # 指关节宝石
        for knuckle in range(3):
            kx = fx + side * (8 + knuckle * 4)
            ky = fy - 10 + knuckle * 3
            pygame.draw.circle(surface, theme["core"], (kx, ky), 3)
            pygame.draw.circle(surface, (255, 255, 255), (kx, ky), 1)
        
        # 神圣符文
        rune_alpha = int(150 + sparkle * 100)
        pygame.draw.circle(surface, (*theme["core"], rune_alpha), 
                          (fx + side * 10, fy), 5, 2)
    
    # === 独特核心：太阳神心 ===
    # 多层放射光芒
    sun_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
    sun_cx, sun_cy = 30, 30
    sun_pulse = abs(math.sin(t * 2.5))
    
    # 外层光芒（三角形射线）
    for ray in range(12):
        ray_angle = t * 0.4 + ray * 0.524
        inner_r = 10 + sun_pulse * 2
        outer_r = 18 + sun_pulse * 4
        r1x = sun_cx + math.cos(ray_angle) * inner_r
        r1y = sun_cy + math.sin(ray_angle) * inner_r
        r2x = sun_cx + math.cos(ray_angle) * outer_r
        r2y = sun_cy + math.sin(ray_angle) * outer_r
        r3x = sun_cx + math.cos(ray_angle + 0.15) * (inner_r + 3)
        r3y = sun_cy + math.sin(ray_angle + 0.15) * (inner_r + 3)
        ray_pts = [(r1x, r1y), (r2x, r2y), (r3x, r3y)]
        ray_alpha = int(180 + sparkle * 75)
        pygame.draw.polygon(sun_surf, (*theme["core"], ray_alpha), ray_pts)
    
    # 核心光环
    for ring in range(4):
        r = 10 - ring * 2 + int(sun_pulse * 2)
        if r > 0:
            ring_alpha = min(255, int(180 + ring * 15))
            pygame.draw.circle(sun_surf, (*theme["core"], ring_alpha), (sun_cx, sun_cy), r)
    
    # 白色核心
    pygame.draw.circle(sun_surf, (255, 255, 255), (sun_cx, sun_cy), 5)
    pygame.draw.circle(sun_surf, (255, 255, 200), (sun_cx, sun_cy), 3)
    
    surface.blit(sun_surf, (cx - 30, cy - 35))
    
    # === 独特头冠：皇帝神冠 ===
    # 冠基（弧形）
    crown_base = [
        (cx - 20, cy - 28), (cx - 18, cy - 32), (cx, cy - 34), 
        (cx + 18, cy - 32), (cx + 20, cy - 28)
    ]
    pygame.draw.polygon(surface, theme["rock_dark"], crown_base)
    
    # 五峰神冠
    peaks = [
        (-14, -38, -10, -50), (-7, -35, -4, -44), (0, -34, 0, -55),
        (7, -35, 4, -44), (14, -38, 10, -50)
    ]
    for bx, by, tx, ty in peaks:
        peak_pts = [
            (cx + bx - 3, cy + by), (cx + tx, cy + ty), (cx + bx + 3, cy + by)
        ]
        pygame.draw.polygon(surface, theme["rock_main"], peak_pts)
        pygame.draw.polygon(surface, theme["crack"], peak_pts, 1)
    
    # 中央神冠宝石（最大最亮）
    main_gem_y = cy - 48
    gem_pulse = abs(math.sin(t * 3))
    # 宝石光晕
    gem_glow = pygame.Surface((24, 24), pygame.SRCALPHA)
    gem_alpha = int(150 + gem_pulse * 100)
    pygame.draw.circle(gem_glow, (*theme["core"], gem_alpha - 80), (12, 12), 10)
    pygame.draw.circle(gem_glow, (*theme["core"], gem_alpha - 40), (12, 12), 7)
    surface.blit(gem_glow, (cx - 12, main_gem_y - 12))
    
    # 宝石本体（切割钻石形）
    gem_pts = [
        (cx, main_gem_y - 8), (cx + 6, main_gem_y - 2), (cx + 4, main_gem_y + 5),
        (cx, main_gem_y + 7), (cx - 4, main_gem_y + 5), (cx - 6, main_gem_y - 2),
    ]
    pygame.draw.polygon(surface, theme["core"], gem_pts)
    pygame.draw.polygon(surface, (255, 255, 255), gem_pts, 1)
    # 切面反光
    pygame.draw.polygon(surface, (255, 255, 255, 180),
                       [(cx, main_gem_y - 6), (cx + 4, main_gem_y - 1), (cx, main_gem_y + 2)])
    
    # 侧峰宝石
    side_gems = [(-10, -44), (-4, -40), (4, -40), (10, -44)]
    for gx, gy in side_gems:
        pygame.draw.circle(surface, theme["core"], (cx + gx, cy + gy), 3)
        pygame.draw.circle(surface, (255, 255, 255), (cx + gx, cy + gy), 1)
    
    _draw_charge_bar(surface, cx, cy, theme, t)


# =============================================================================
#   渲染调度器和接口函数
# =============================================================================

# 涂装渲染器映射表
_TURU_RENDERERS = {
    "turu_default": _render_turu_default,
    "turu_magma": _render_turu_magma,
    "turu_obsidian": _render_turu_obsidian,
    "turu_crystal": _render_turu_crystal,
    "turu_jade": _render_turu_jade,
    "turu_diamond": _render_turu_diamond,
    "turu_meteor": _render_turu_meteor,
    "turu_sandstone": _render_turu_sandstone,
    "turu_ice": _render_turu_ice,
    "turu_volcanic": _render_turu_volcanic,
    "turu_rusty": _render_turu_rusty,
    "turu_golden": _render_turu_golden,
}


def render_turu_skin(surface, color, model_style, t, pid, static=False):
    """渲染图鲁专属涂装
    
    Args:
        surface: pygame Surface对象
        color: 基础颜色（未使用，保持接口兼容）
        model_style: 涂装样式名称
        t: 时间参数（用于动画）
        pid: 玩家ID
        static: 是否静态渲染
    
    Returns:
        渲染后的surface
    """
    if not is_turu_style(model_style):
        return None
    
    pulse = 0 if static else abs(math.sin(t * 3))
    
    renderer = _TURU_RENDERERS.get(model_style, _render_turu_default)
    renderer(surface, t, pulse)
    
    return surface


def _render_turu_base(surface, t, pulse, visual=None):
    """基础渲染器 - 由base.py调用"""
    _render_turu_default(surface, t, pulse, visual)
