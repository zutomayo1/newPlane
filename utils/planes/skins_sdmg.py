# -*- coding: utf-8 -*-
"""
S.D.M.G. (Bio-System "STAR-DOLPHIN") - 涂装模块
Project Code: MEGA_SHARK_MK4

泰拉瑞亚致敬：S.D.M.G. (Space Dolphin Machine Gun)
生物机械海豚 + 镀铬美学 + 重火力加特林
"""
import pygame
import math
import random

# ==================== 涂装主题定义 ====================
SDMG_THEMES = {
    "default": {
        "name": "星际海豚",
        "armor": (192, 192, 192),       # 银色镜面装甲 #C0C0C0
        "energy": (0, 255, 255),         # 青色能量辉光 #00FFFF
        "shell": (255, 215, 0),          # 金色弹壳 #FFD700
        "accent": (100, 180, 255),       # 蓝色点缀
        "glow": (150, 255, 255),         # 发光色
        "tube": (0, 200, 200),           # 能量管
        "muzzle": (255, 200, 100),       # 枪口火焰
    },
    "neon": {
        "name": "霓虹鲨潮",
        "armor": (40, 40, 60),
        "energy": (255, 0, 255),
        "shell": (255, 100, 200),
        "accent": (200, 0, 255),
        "glow": (255, 150, 255),
        "tube": (255, 50, 200),
        "muzzle": (255, 100, 255),
    },
    "abyss": {
        "name": "深渊猎手",
        "armor": (20, 30, 60),
        "energy": (100, 200, 255),
        "shell": (150, 200, 255),
        "accent": (80, 150, 220),
        "glow": (120, 180, 255),
        "tube": (60, 120, 200),
        "muzzle": (100, 200, 255),
    },
    "golden": {
        "name": "黄金暴君",
        "armor": (255, 215, 0),
        "energy": (255, 255, 200),
        "shell": (255, 180, 50),
        "accent": (255, 240, 150),
        "glow": (255, 255, 180),
        "tube": (255, 200, 100),
        "muzzle": (255, 220, 100),
    },
    "void": {
        "name": "虚空噬星",
        "armor": (30, 20, 50),
        "energy": (150, 100, 255),
        "shell": (200, 150, 255),
        "accent": (120, 80, 200),
        "glow": (180, 130, 255),
        "tube": (100, 60, 180),
        "muzzle": (150, 100, 255),
    },
    "lunar": {
        "name": "月球领主",
        "armor": (80, 100, 120),
        "energy": (100, 255, 200),
        "shell": (200, 255, 220),
        "accent": (80, 200, 180),
        "glow": (150, 255, 220),
        "tube": (60, 180, 150),
        "muzzle": (100, 255, 180),
    },
}

# 涂装样式列表
SDMG_STYLES = [f"sdmg_{key}" for key in SDMG_THEMES.keys()]

SDMG_STYLE_VARIANTS = {
    "default": {
        "shadow_color": (0, 0, 0),
        "shadow_alpha": 115,
        "aura_mode": "standard",
        "trail_mode": "none",
    },
    "neon": {
        "shadow_color": (30, 0, 60),
        "shadow_alpha": 150,
        "aura_mode": "neon_ring",
        "trail_mode": "neon_scan",
    },
    "abyss": {
        "shadow_color": (0, 10, 35),
        "shadow_alpha": 140,
        "aura_mode": "abyss_mist",
        "trail_mode": "bubble",
    },
    "golden": {
        "shadow_color": (40, 25, 0),
        "shadow_alpha": 130,
        "aura_mode": "golden_flare",
        "trail_mode": "solar_rune",
    },
    "void": {
        "shadow_color": (5, 0, 20),
        "shadow_alpha": 170,
        "aura_mode": "void_singularity",
        "trail_mode": "void_rift",
    },
    "lunar": {
        "shadow_color": (10, 20, 25),
        "shadow_alpha": 135,
        "aura_mode": "lunar_prism",
        "trail_mode": "lunar_shard",
    },
}


def is_sdmg_style(style):
    """检查是否为SDMG涂装"""
    return style in SDMG_STYLES or style.startswith("sdmg_")


def get_sdmg_theme(style):
    """获取SDMG涂装主题"""
    if style.startswith("sdmg_"):
        key = style[5:]
    else:
        key = style
    return SDMG_THEMES.get(key, SDMG_THEMES["default"])


def get_sdmg_variant(style):
    if style.startswith("sdmg_"):
        key = style[5:]
    else:
        key = style
    return SDMG_STYLE_VARIANTS.get(key, SDMG_STYLE_VARIANTS["default"])


def get_all_sdmg_styles():
    """获取所有SDMG涂装列表"""
    return SDMG_STYLES


# =============================================================================
#   核心辅助函数 - S.D.M.G.专属元素
# =============================================================================

def _draw_gatling_barrel(s, cx, cy, length, t, theme, heat=0.0):
    """六管旋转加特林机枪"""
    energy = theme["energy"]
    armor = theme["armor"]
    muzzle = theme["muzzle"]
    
    rotation = t * 8  # 高速旋转
    barrel_count = 6
    barrel_radius = int(length * 0.25)
    
    # 枪管外壳
    pygame.draw.circle(s, armor, (cx, cy), barrel_radius + 4)
    pygame.draw.circle(s, (max(0, armor[0]-30), max(0, armor[1]-30), max(0, armor[2]-30)), 
                      (cx, cy), barrel_radius + 4, 2)
    
    # 六根枪管
    for i in range(barrel_count):
        angle = rotation + i * (math.pi * 2 / barrel_count)
        bx = cx + math.cos(angle) * barrel_radius
        by = cy + math.sin(angle) * barrel_radius
        
        # 枪管本体
        barrel_len = length * 0.6
        end_x = bx + math.cos(angle) * 0  # 指向前方
        end_y = by - barrel_len
        
        # 枪管圆柱
        pygame.draw.line(s, armor, (int(bx), int(by)), (int(bx), int(by - barrel_len)), 4)
        
        # 枪口火焰（根据热量）
        if heat > 0.3:
            flame_intensity = heat * abs(math.sin(t * 20 + i))
            flame_len = int(10 * flame_intensity)
            flame_color = (
                min(255, int(muzzle[0] * flame_intensity)),
                min(255, int(muzzle[1] * flame_intensity * 0.6)),
                min(255, int(muzzle[2] * flame_intensity * 0.3))
            )
            pygame.draw.circle(s, flame_color, (int(bx), int(by - barrel_len - flame_len//2)), 
                             int(3 + flame_intensity * 2))
    
    # 中心能量核心
    core_pulse = 0.7 + 0.3 * math.sin(t * 5)
    pygame.draw.circle(s, energy, (cx, cy), int(6 * core_pulse))
    pygame.draw.circle(s, (255, 255, 255), (cx, cy), int(3 * core_pulse))


def _draw_shell_cascade(s, cx, cy, w, h, t, theme, firing=True):
    """弹壳瀑布效果"""
    if not firing:
        return
    
    shell_color = theme["shell"]
    
    # 生成多个下落的弹壳
    shell_count = 8
    for i in range(shell_count):
        # 随机化位置和旋转
        seed = int(t * 10 + i * 7) % 100
        random.seed(seed)
        
        shell_x = cx + random.randint(-int(w*0.15), int(w*0.15))
        fall_progress = ((t * 3 + i * 0.3) % 1.0)
        shell_y = cy + h * 0.1 + fall_progress * h * 0.4
        
        shell_rot = t * 5 + i * 0.8
        shell_len = 6
        shell_w = 3
        
        # 弹壳形状（简化矩形+半圆）
        alpha = int(255 * (1 - fall_progress))
        if alpha > 50:
            # 弹壳主体
            pygame.draw.ellipse(s, shell_color, 
                              (int(shell_x - shell_w), int(shell_y - shell_len//2), 
                               shell_w * 2, shell_len))
            # 弹壳底部
            pygame.draw.circle(s, (min(255, shell_color[0]+30), 
                                  min(255, shell_color[1]+30), 
                                  min(255, shell_color[2]+30)), 
                             (int(shell_x), int(shell_y + shell_len//2 - 1)), shell_w - 1)


def _draw_energy_tubes(s, points, t, theme):
    """发光能量液管"""
    tube_color = theme["tube"]
    glow = theme["glow"]
    
    if len(points) < 2:
        return
    
    # 能量流动效果
    flow = (t * 3) % 1.0
    
    # 绘制管道
    pygame.draw.lines(s, tube_color, False, points, 3)
    
    # 能量脉冲
    for i, (px, py) in enumerate(points):
        pulse_phase = (flow + i * 0.2) % 1.0
        pulse_size = int(4 * (0.5 + 0.5 * math.sin(pulse_phase * math.pi * 2)))
        pygame.draw.circle(s, glow, (int(px), int(py)), pulse_size)


def _draw_torpedo_pod(s, cx, cy, size, t, theme, side=1):
    """微型鱼雷发射巢"""
    armor = theme["armor"]
    energy = theme["energy"]
    
    pod_w = int(size * 0.8)
    pod_h = int(size * 0.5)
    
    # 发射巢外壳
    pygame.draw.ellipse(s, armor, (cx - pod_w//2, cy - pod_h//2, pod_w, pod_h))
    pygame.draw.ellipse(s, (max(0, armor[0]-40), max(0, armor[1]-40), max(0, armor[2]-40)),
                       (cx - pod_w//2, cy - pod_h//2, pod_w, pod_h), 2)
    
    # 鱼雷发射口
    for i in range(3):
        tube_x = cx - pod_w//3 + i * (pod_w//3)
        tube_y = cy
        pygame.draw.circle(s, (30, 30, 40), (tube_x, tube_y), 3)
        # 鱼雷头部微光
        pulse = 0.5 + 0.5 * math.sin(t * 4 + i)
        pygame.draw.circle(s, (*energy, int(150 * pulse)), (tube_x, tube_y - 2), 2)


def _draw_radar_fin(s, cx, cy, size, t, theme):
    """雷达背鳍"""
    armor = theme["armor"]
    energy = theme["energy"]
    
    # 背鳍形状
    fin_pts = [
        (cx, cy),
        (cx - size * 0.3, cy - size * 0.2),
        (cx, cy - size),
        (cx + size * 0.3, cy - size * 0.2),
    ]
    pygame.draw.polygon(s, armor, fin_pts)
    pygame.draw.polygon(s, (min(255, armor[0]+30), min(255, armor[1]+30), min(255, armor[2]+30)),
                       fin_pts, 2)
    
    # 雷达尖端红光
    blink = abs(math.sin(t * 3))
    pygame.draw.circle(s, (255, int(50 * blink), int(50 * blink)), 
                      (cx, int(cy - size + 3)), 3)


def _draw_transparent_hull(s, cx, cy, w, h, t, theme):
    """透明装甲板 - 可见内部弹链"""
    armor = theme["armor"]
    energy = theme["energy"]
    
    # 透明玻璃区域
    glass_w = int(w * 0.3)
    glass_h = int(h * 0.4)
    glass_x = cx - glass_w // 2
    glass_y = cy - glass_h // 2
    
    # 玻璃边框
    pygame.draw.rect(s, (min(255, armor[0]+50), min(255, armor[1]+50), min(255, armor[2]+50)), 
                    (glass_x, glass_y, glass_w, glass_h), 2)
    
    # 内部弹链动画
    chain_speed = t * 8
    for i in range(5):
        chain_y = glass_y + 5 + ((chain_speed + i * 8) % glass_h)
        if chain_y < glass_y + glass_h - 3:
            # 弹链节
            pygame.draw.circle(s, theme["shell"], (glass_x + 5, int(chain_y)), 2)
            pygame.draw.circle(s, theme["shell"], (glass_x + glass_w - 5, int(chain_y)), 2)
            # 连接线
            pygame.draw.line(s, (100, 100, 100), 
                           (glass_x + 5, int(chain_y)), 
                           (glass_x + glass_w - 5, int(chain_y)), 1)


def _lerp_color(color_a, color_b, t):
    """线性插值颜色"""
    return tuple(int(color_a[i] + (color_b[i] - color_a[i]) * t) for i in range(3))


def _draw_plasma_spine(s, cx, cy, w, h, t, theme):
    """沿机背的能量脊柱"""
    glow = theme["glow"]
    accent = theme["accent"]
    segment_count = 6
    length = w * 0.5
    start_x = cx - length / 2
    spine_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    plane_left = cx - w / 2
    plane_top = cy - h / 2
    for i in range(segment_count):
        progress = i / max(1, segment_count - 1)
        px = int(start_x + progress * length)
        wave = math.sin(t * 3 + progress * math.pi * 2)
        py = int(cy - h * 0.2 + wave * 4)
        radius = int(5 + 2 * (1 - abs(wave)))
        color = (*glow, 130)
        local = (int(px - plane_left), int(py - plane_top))
        pygame.draw.circle(spine_surf, color, local, radius)
        pygame.draw.circle(spine_surf, (*accent, 200), local, max(1, radius // 3))
    s.blit(spine_surf, (int(plane_left), int(plane_top)), special_flags=pygame.BLEND_ADD)


def _draw_rear_thrusters(s, cx, cy, w, h, t, theme, heat):
    """尾部矢量喷口与尾焰"""
    armor = theme["armor"]
    muzzle = theme["muzzle"]
    thruster_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    plane_left = cx - w / 2
    plane_top = cy - h / 2
    offsets = [-w * 0.12, w * 0.12]
    for i, offset in enumerate(offsets):
        nozzle_rect = pygame.Rect(0, 0, int(w * 0.12), int(h * 0.18))
        nozzle_rect.center = (
            int((cx + offset) - plane_left),
            int((cy + h * 0.28) - plane_top),
        )
        pygame.draw.ellipse(thruster_surf, armor, nozzle_rect)
        pygame.draw.ellipse(thruster_surf,
                            (max(0, armor[0] - 40), max(0, armor[1] - 40), max(0, armor[2] - 40)),
                            nozzle_rect, 2)
        plasma = pygame.Surface((nozzle_rect.width, nozzle_rect.height * 2), pygame.SRCALPHA)
        intensity = max(0.2, heat) * (1 + 0.2 * math.sin(t * 6 + i))
        flame_color = (*muzzle, int(160 * intensity))
        pygame.draw.polygon(
            plasma,
            flame_color,
            [
                (nozzle_rect.width // 2, 0),
                (nozzle_rect.width, int(nozzle_rect.height * 1.6)),
                (0, int(nozzle_rect.height * 1.6)),
            ],
        )
        thruster_surf.blit(plasma, (nozzle_rect.left, nozzle_rect.bottom - nozzle_rect.height // 3),
                   special_flags=pygame.BLEND_ADD)
    s.blit(thruster_surf, (int(plane_left), int(plane_top)))


def _draw_sensor_array(s, cx, cy, radius, t, theme):
    """头部量子感测阵列"""
    glow = theme["glow"]
    energy = theme["energy"]
    sensor_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    center = (radius * 2, radius * 2)
    for i in range(3):
        angle = t * 2 + i * (math.pi * 2 / 3)
        orbit_r = radius * 0.9
        px = int(center[0] + math.cos(angle) * orbit_r)
        py = int(center[1] + math.sin(angle) * orbit_r)
        pygame.draw.circle(sensor_surf, (*glow, 160), (px, py), 4)
        pygame.draw.circle(sensor_surf, (*energy, 220), (px, py), 2)
    pygame.draw.circle(sensor_surf, (*glow, 200), center, int(radius * 0.7), 1)
    s.blit(sensor_surf, (cx - radius * 2, cy - radius * 2), special_flags=pygame.BLEND_ADD)


def _draw_body_panel_lines(s, x, y, w, h, swim, theme, heat):
    """机体面板与能量线路"""
    panel_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    accent = theme["accent"]
    glow = theme["glow"]
    for i in range(4):
        offset_y = int(h * (0.25 + i * 0.12) + swim)
        rect = pygame.Rect(int(w * 0.2), offset_y, int(w * 0.6), int(h * 0.15))
        pygame.draw.arc(panel_surf, (*accent, 120), rect, 0, math.pi, 1)
    for i in range(3):
        progress = i / 2
        path = [
            (int(w * (0.28 + progress * 0.25)), int(h * 0.25 + swim)),
            (int(w * (0.3 + progress * 0.25)), int(h * 0.4 + swim)),
            (int(w * (0.32 + progress * 0.2)), int(h * 0.55 + swim)),
        ]
        pygame.draw.lines(panel_surf, (*glow, 110), False, path, 1)
    if heat > 0.55:
        thermal = pygame.Surface((w, h), pygame.SRCALPHA)
        alpha = int((heat - 0.55) * 220)
        pygame.draw.ellipse(thermal, (255, 120, 80, alpha),
                            (int(w * 0.15), int(h * 0.25), int(w * 0.7), int(h * 0.35)))
        panel_surf.blit(thermal, (0, 0), special_flags=pygame.BLEND_ADD)
    s.blit(panel_surf, (x, y), special_flags=pygame.BLEND_ADD)


def _draw_silhouette_shadow(s, x, y, w, h, t, variant):
    """巨大的投影增强压迫感"""
    shadow = pygame.Surface((int(w * 1.4), int(h * 0.8)), pygame.SRCALPHA)
    offset = int(10 + math.sin(t * 1.2) * 3)
    color = variant.get("shadow_color", (0, 0, 0))
    alpha = variant.get("shadow_alpha", 120)
    pygame.draw.ellipse(
        shadow,
        (*color, alpha),
        (0, offset, shadow.get_width(), shadow.get_height() - offset // 2),
    )
    s.blit(shadow, (int(x - w * 0.2), int(y + h * 0.35)))


def _draw_heavy_armor_overlay(s, x, y, w, h, swim, theme):
    """多层厚重装甲板"""
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    armor = theme["armor"]
    dark = (max(0, armor[0] - 60), max(0, armor[1] - 60), max(0, armor[2] - 60))
    highlight = (min(255, armor[0] + 30), min(255, armor[1] + 30), min(255, armor[2] + 30))
    plates = [
        [
            (int(w * 0.18), int(h * 0.38 + swim)),
            (int(w * 0.5), int(h * 0.26 + swim)),
            (int(w * 0.82), int(h * 0.33 + swim)),
            (int(w * 0.75), int(h * 0.45 + swim)),
            (int(w * 0.25), int(h * 0.5 + swim)),
        ],
        [
            (int(w * 0.22), int(h * 0.55 + swim)),
            (int(w * 0.78), int(h * 0.55 + swim)),
            (int(w * 0.7), int(h * 0.68 + swim)),
            (int(w * 0.3), int(h * 0.7 + swim)),
        ],
    ]
    for plate in plates:
        pygame.draw.polygon(overlay, dark, plate)
        pygame.draw.polygon(overlay, highlight, plate, 2)
    gradient = pygame.Surface((w, h), pygame.SRCALPHA)
    for row in range(h):
        alpha = max(0, min(150, int((row / h) * 180)))
        pygame.draw.line(gradient, (0, 0, 0, alpha), (0, row), (w, row))
    overlay.blit(gradient, (0, 0))
    s.blit(overlay, (x, y), special_flags=pygame.BLEND_SUB)


def _draw_predator_lances(s, cx, head_y, w, h, t, theme):
    """突出的捕食者式前臂"""
    lance_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    armor = theme["armor"]
    accent = theme["accent"]
    sweep = math.sin(t * 2) * h * 0.02
    for direction in (-1, 1):
        base_x = w // 2 + int(direction * w * 0.08)
        base_y = int(h * 0.15 + head_y - (h // 2))
        tip_x = w // 2 + int(direction * w * 0.38)
        tip_y = base_y - int(h * 0.12 + sweep * direction)
        mid_x = w // 2 + int(direction * w * 0.2)
        mid_y = base_y + int(h * 0.05)
        points = [
            (base_x, base_y),
            (mid_x, mid_y),
            (tip_x, tip_y),
            (base_x - int(direction * w * 0.05), base_y - int(h * 0.02)),
        ]
        pygame.draw.polygon(lance_surf, armor, points)
        pygame.draw.polygon(lance_surf, accent, points, 2)
    s.blit(lance_surf, (int(cx - w // 2), int(head_y - h // 2)))


def _draw_variant_trails(s, x, y, w, h, t, theme, variant):
    mode = variant.get("trail_mode", "none")
    if mode == "none" or not mode:
        return
    trail = pygame.Surface((w, h), pygame.SRCALPHA)
    energy = theme["energy"]
    glow = theme["glow"]
    if mode == "neon_scan":
        color = (*energy, 150)
        for i in range(4):
            offset = (t * 40 + i * 30) % (w + 40)
            start = (int(offset) - 40, h)
            end = (int(offset - h * 0.4), 0)
            pygame.draw.line(trail, color, start, end, 3)
    elif mode == "bubble":
        for i in range(5):
            progress = (t * 0.35 + i * 0.22) % 1.0
            px = int(w * 0.22 + math.sin(i * 1.3) * w * 0.05)
            py = int(h * (0.7 - progress * 0.5))
            radius = max(2, int(4 + 3 * (1 - progress)))
            alpha = max(20, int(80 * (1 - progress)))
            pygame.draw.circle(trail, (*glow, alpha), (px, py), radius, 1)
    elif mode == "solar_rune":
        color = (*theme["shell"], 180)
        center_y = int(h * 0.65)
        for i in range(3):
            width = int(w * 0.18)
            rect = pygame.Rect(int(w * 0.3) - i * 6, center_y - i * 8, width, width // 3)
            pygame.draw.ellipse(trail, color, rect, 2)
    elif mode == "void_rift":
        color = (*energy, 140)
        for lane in range(2):
            points = []
            for y_pos in range(0, h, 8):
                wave = math.sin(t * 2 + y_pos * 0.15 + lane)
                px = int(w * (0.25 + lane * 0.35) + wave * w * 0.08)
                points.append((px, y_pos))
            if len(points) >= 2:
                pygame.draw.lines(trail, color, False, points, 2)
    elif mode == "lunar_shard":
        color = (*glow, 150)
        for i in range(4):
            progress = (t * 0.4 + i * 0.25) % 1.0
            base_x = int(w * 0.4 + i * 10)
            base_y = int(h * (0.4 + math.sin(i + t) * 0.05))
            height = int(18 * (1 - progress))
            points = [
                (base_x, base_y - height),
                (base_x + 6, base_y),
                (base_x - 6, base_y),
            ]
            pygame.draw.polygon(trail, color, points, 1)
    s.blit(trail, (int(x), int(y)), special_flags=pygame.BLEND_ADD)


def _draw_variant_aura(s, cx, cy, w, h, t, theme, variant):
    mode = variant.get("aura_mode", "standard")
    aura = pygame.Surface((w + 80, h + 80), pygame.SRCALPHA)
    center = ((w + 80) // 2, (h + 80) // 2)
    base_rect = (20, 20, w + 40, h + 40)
    if mode == "neon_ring":
        for i in range(3):
            radius = int(min(w, h) * (0.35 + i * 0.08))
            alpha = 160 - i * 35
            pygame.draw.circle(aura, (*theme["energy"], alpha), center, radius, 2)
            angle = t * 4 + i
            marker = (
                int(center[0] + math.cos(angle) * radius),
                int(center[1] + math.sin(angle) * radius),
            )
            pygame.draw.circle(aura, (255, 255, 255, alpha), marker, 3)
    elif mode == "abyss_mist":
        for i in range(5):
            alpha = int(70 - i * 10)
            rect = (
                10 - i * 5,
                40 + i * 12,
                w + 60 + i * 10,
                h + 20,
            )
            pygame.draw.ellipse(aura, (*theme["glow"], alpha), rect)
    elif mode == "golden_flare":
        for i in range(8):
            angle = math.radians(i * 45 + t * 60)
            length = min(w, h) * 0.6
            end = (
                int(center[0] + math.cos(angle) * length),
                int(center[1] + math.sin(angle) * length),
            )
            pygame.draw.line(aura, (*theme["shell"], 160), center, end, 3)
        pygame.draw.circle(aura, (*theme["glow"], 120), center, int(min(w, h) * 0.45), 3)
    elif mode == "void_singularity":
        radius = int(min(w, h) * 0.4)
        pygame.draw.circle(aura, (10, 0, 20, 160), center, radius)
        for i in range(3):
            start = t * 1.4 + i * 1.1
            pygame.draw.arc(
                aura,
                (*theme["energy"], 140),
                (
                    center[0] - radius - i * 6,
                    center[1] - radius - i * 6,
                    (radius + i * 6) * 2,
                    (radius + i * 6) * 2,
                ),
                start,
                start + math.pi * 1.4,
                3,
            )
    elif mode == "lunar_prism":
        polygon = []
        r = min(w, h) * 0.45
        for i in range(6):
            angle = math.radians(i * 60 + t * 20)
            polygon.append((center[0] + math.cos(angle) * r, center[1] + math.sin(angle) * r))
        pygame.draw.polygon(aura, (*theme["glow"], 140), polygon, 2)
        for i in range(3):
            angle = math.radians(i * 120 + t * 50)
            inner = int(r * 0.6)
            end = (
                int(center[0] + math.cos(angle) * inner),
                int(center[1] + math.sin(angle) * inner),
            )
            pygame.draw.line(aura, (255, 255, 255, 150), center, end, 2)
    else:
        pulse = 0.6 + 0.4 * math.sin(t * 4)
        pygame.draw.ellipse(
            aura,
            (*theme["energy"], int(30 * pulse + 20)),
            base_rect,
        )
    s.blit(aura, (int(cx - (w + 80) // 2), int(cy - (h + 80) // 2)), special_flags=pygame.BLEND_ADD)


# =============================================================================
#   主绘制函数
# =============================================================================

def draw_sdmg(surface, color, x, y, w, h, frame, style="sdmg_default"):
    """绘制S.D.M.G.机体"""
    theme = get_sdmg_theme(style)
    variant = get_sdmg_variant(style)
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.02
    
    armor = theme["armor"]
    energy = theme["energy"]
    shell = theme["shell"]
    accent = theme["accent"]
    glow = theme["glow"]
    
    # 游动动画
    swim = math.sin(t * 2) * 3
    
    # 热量模拟（0-1）
    heat = 0.5 + 0.3 * math.sin(t * 0.5)
    
    _draw_silhouette_shadow(surface, x, y, w, h, t, variant)
    _draw_variant_trails(surface, x, y, w, h, t, theme, variant)

    # ========== 弹壳瀑布（最底层）==========
    _draw_shell_cascade(surface, cx, cy + h * 0.15, w, h, t, theme, firing=True)
    
    # ========== 尾鳍 ==========
    tail_wave = math.sin(t * 3) * 8
    tail_pts = [
        (cx, cy + h * 0.25 + swim),
        (cx - w * 0.12, cy + h * 0.32 + swim),
        (cx - w * 0.2 + tail_wave, cy + h * 0.42 + swim),
        (cx, cy + h * 0.35 + swim),
        (cx + w * 0.2 - tail_wave, cy + h * 0.42 + swim),
        (cx + w * 0.12, cy + h * 0.32 + swim),
    ]
    pygame.draw.polygon(surface, armor, tail_pts)
    pygame.draw.polygon(surface, accent, tail_pts, 2)
    _draw_rear_thrusters(surface, cx, cy, w, h, t, theme, heat)
    
    # ========== 胸鳍（带鱼雷巢）==========
    fin_flap = math.sin(t * 2.5) * 10
    
    # 左胸鳍
    left_fin_pts = [
        (cx - w * 0.22, cy + swim),
        (cx - w * 0.45, cy - h * 0.05 + fin_flap + swim),
        (cx - w * 0.42, cy + h * 0.1 + fin_flap + swim),
        (cx - w * 0.28, cy + h * 0.12 + swim),
    ]
    pygame.draw.polygon(surface, armor, left_fin_pts)
    pygame.draw.polygon(surface, accent, left_fin_pts, 2)
    _draw_torpedo_pod(surface, cx - int(w * 0.35), cy + int(h * 0.05 + fin_flap + swim), 18, t, theme, -1)
    
    # 右胸鳍
    right_fin_pts = [
        (cx + w * 0.22, cy + swim),
        (cx + w * 0.45, cy - h * 0.05 - fin_flap + swim),
        (cx + w * 0.42, cy + h * 0.1 - fin_flap + swim),
        (cx + w * 0.28, cy + h * 0.12 + swim),
    ]
    pygame.draw.polygon(surface, armor, right_fin_pts)
    pygame.draw.polygon(surface, accent, right_fin_pts, 2)
    _draw_torpedo_pod(surface, cx + int(w * 0.35), cy + int(h * 0.05 - fin_flap + swim), 18, t, theme, 1)
    
    # ========== 背鳍（雷达）==========
    _draw_radar_fin(surface, cx, cy - h * 0.15 + swim, h * 0.25, t, theme)
    _draw_plasma_spine(surface, cx, cy, w, h, t, theme)
    
    # ========== 主体 - 流线型海豚身躯 ==========
    body_w, body_h = int(w * 0.55), int(h * 0.45)
    body_rect = (cx - body_w // 2, int(cy - body_h // 2 + swim), body_w, body_h)
    pygame.draw.ellipse(surface, armor, body_rect)
    
    # 镜面高光
    highlight_w, highlight_h = int(body_w * 0.6), int(body_h * 0.3)
    pygame.draw.ellipse(surface, (min(255, armor[0]+40), min(255, armor[1]+40), min(255, armor[2]+40)),
                       (cx - highlight_w // 2, int(cy - body_h // 3 + swim), highlight_w, highlight_h))
    _draw_body_panel_lines(surface, x, y, w, h, swim, theme, heat)
    _draw_heavy_armor_overlay(surface, x, y, w, h, swim, theme)
    
    # ========== 透明装甲板（两侧）==========
    _draw_transparent_hull(surface, cx - int(w * 0.12), cy + swim, w * 0.2, h * 0.25, t, theme)
    _draw_transparent_hull(surface, cx + int(w * 0.12), cy + swim, w * 0.2, h * 0.25, t, theme)
    
    # ========== 能量液管 ==========
    tube_pts_left = [
        (cx - w * 0.2, cy - h * 0.1 + swim),
        (cx - w * 0.25, cy + swim),
        (cx - w * 0.22, cy + h * 0.1 + swim),
    ]
    tube_pts_right = [
        (cx + w * 0.2, cy - h * 0.1 + swim),
        (cx + w * 0.25, cy + swim),
        (cx + w * 0.22, cy + h * 0.1 + swim),
    ]
    _draw_energy_tubes(surface, [(int(p[0]), int(p[1])) for p in tube_pts_left], t, theme)
    _draw_energy_tubes(surface, [(int(p[0]), int(p[1])) for p in tube_pts_right], t, theme)
    
    # ========== 头部 ==========
    head_r = int(w * 0.22)
    head_y = cy - h * 0.18 + swim
    pygame.draw.circle(surface, armor, (cx, int(head_y)), head_r)
    
    # 头部高光
    pygame.draw.circle(surface, (min(255, armor[0]+50), min(255, armor[1]+50), min(255, armor[2]+50)),
                      (cx - head_r // 3, int(head_y - head_r // 3)), head_r // 3)
    _draw_sensor_array(surface, cx, int(head_y - head_r * 0.1), int(head_r * 0.8), t, theme)
    _draw_predator_lances(surface, cx, head_y, w, h, t, theme)
    
    # ========== 眼睛 ==========
    eye_r = 7
    for ex in [-12, 12]:
        eye_x = cx + ex
        eye_y = int(head_y + 2)
        # 眼白
        pygame.draw.circle(surface, (240, 240, 250), (eye_x, eye_y), eye_r)
        # 虹膜
        pygame.draw.circle(surface, energy, (eye_x, eye_y), eye_r - 2)
        # 瞳孔
        pygame.draw.circle(surface, (20, 20, 30), (eye_x, eye_y), 3)
        # 高光
        pygame.draw.circle(surface, (255, 255, 255), (eye_x - 2, eye_y - 2), 2)
    
    # ========== 嘴部 - 张开的加特林 ==========
    mouth_y = head_y + head_r * 0.7
    mouth_open = int(head_r * 0.8)  # 90度张开
    
    # 上下颚
    jaw_color = (max(0, armor[0]-20), max(0, armor[1]-20), max(0, armor[2]-20))
    # 上颚
    pygame.draw.arc(surface, jaw_color, 
                   (cx - mouth_open // 2, int(mouth_y - mouth_open // 2), mouth_open, mouth_open),
                   0, math.pi, 3)
    # 下颚
    pygame.draw.arc(surface, jaw_color,
                   (cx - mouth_open // 2, int(mouth_y), mouth_open, mouth_open // 2),
                   math.pi, 2 * math.pi, 3)
    
    # 加特林机枪从嘴里伸出
    gatling_y = int(mouth_y - h * 0.15)
    _draw_gatling_barrel(surface, cx, gatling_y, h * 0.3, t, theme, heat)
    
    # ========== 抛壳口标记 ==========
    eject_x = cx
    eject_y = cy + int(h * 0.08) + swim
    pygame.draw.rect(surface, (50, 50, 60), (eject_x - 8, eject_y - 3, 16, 6))
    pygame.draw.rect(surface, shell, (eject_x - 6, eject_y - 2, 12, 4))
    
    # ========== 热量视觉效果 ==========
    if heat > 0.6:
        # 机身变红
        heat_overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        heat_alpha = int((heat - 0.6) * 200)
        pygame.draw.ellipse(heat_overlay, (255, 100, 50, heat_alpha), 
                           (w // 2 - body_w // 2, h // 2 - body_h // 2, body_w, body_h))
        surface.blit(heat_overlay, (x, y))
    
    # ========== 机型特效差异化光晕 ==========
    _draw_variant_aura(surface, cx, cy, w, h, t, theme, variant)


def render_sdmg_skin(surface, color, x, y, w, h, frame, style):
    """渲染SDMG涂装"""
    draw_sdmg(surface, color, x, y, w, h, frame, style)


def _render_sdmg_base(s, t, pulse):
    """渲染基础SDMG机体（无涂装）"""
    frame = int(t * 60)
    draw_sdmg(s, (0, 255, 255), 10, 10, 100, 100, frame, "sdmg_default")
