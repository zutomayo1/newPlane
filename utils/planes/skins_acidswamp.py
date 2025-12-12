# -*- coding: utf-8 -*-
"""
酸蚀喷溅·腐沼 (Acidswamp) - 专属涂装渲染模块
荧光绿腐黑的酸液生化兵器，以腐蚀溶解一切

涂装列表 (12种完全不同形态):
1. acidswamp_default - 酸沼原型（荧光绿+腐黑基底）
2. acidswamp_toxic - 剧毒废液（工业污染绿）
3. acidswamp_biohazard - 生化危机（警告标识）
4. acidswamp_slime - 史莱姆王（半透明果冻）
5. acidswamp_nuclear - 核辐射（放射性黄绿）
6. acidswamp_plague - 瘟疫之源（腐烂紫绿）
7. acidswamp_venom - 蛇毒喷射（剧毒紫黑）
8. acidswamp_swamp - 沼泽怪物（泥浆棕绿）
9. acidswamp_neon - 霓虹酸雨（赛博朋克）
10. acidswamp_crystal - 酸性晶体（结晶酸盐）
11. acidswamp_lava - 熔岩酸池（橙红酸流）
12. acidswamp_void - 虚空腐蚀（暗紫酸雾）
"""
import pygame
import math
import random

# Acidswamp涂装样式列表
ACIDSWAMP_STYLES = [
    "acidswamp_default",
    "acidswamp_toxic",
    "acidswamp_biohazard",
    "acidswamp_slime",
    "acidswamp_nuclear",
    "acidswamp_plague",
    "acidswamp_venom",
    "acidswamp_swamp",
    "acidswamp_neon",
    "acidswamp_crystal",
    "acidswamp_lava",
    "acidswamp_void"
]


def is_acidswamp_style(model_style):
    """检查是否为 Acidswamp 涂装样式"""
    return model_style in ACIDSWAMP_STYLES


def render_acidswamp_skin(surface, c, model_style, t, pid, static):
    """渲染 Acidswamp 专属涂装"""
    if model_style not in ACIDSWAMP_STYLES:
        return None
    
    skin_id = model_style.replace("acidswamp_", "")
    frame = 0 if static else int(t * 60) % 360
    draw_acidswamp(surface, c, 60, 60, scale=1.8, skin_id=skin_id, frame=frame)
    return surface


def _render_acidswamp_base(surface, t, pulse):
    """基础机体渲染（用于base.py调用）"""
    frame = int(t * 60) % 360
    draw_acidswamp(surface, (100, 180, 80), 60, 60, scale=1.8, skin_id="default", frame=frame)


def draw_acidswamp(surface, color, x, y, scale=1.0, skin_id="default", frame=0):
    """绘制腐沼 - 12种独特形态"""
    cx, cy = x, y
    s = scale
    pulse = math.sin(frame * 0.1) * 3
    
    if skin_id == "default":
        _draw_default(surface, cx, cy, s, frame, pulse)
    elif skin_id == "toxic":
        _draw_toxic(surface, cx, cy, s, frame, pulse)
    elif skin_id == "biohazard":
        _draw_biohazard(surface, cx, cy, s, frame, pulse)
    elif skin_id == "slime":
        _draw_slime(surface, cx, cy, s, frame, pulse)
    elif skin_id == "nuclear":
        _draw_nuclear(surface, cx, cy, s, frame, pulse)
    elif skin_id == "plague":
        _draw_plague(surface, cx, cy, s, frame, pulse)
    elif skin_id == "venom":
        _draw_venom(surface, cx, cy, s, frame, pulse)
    elif skin_id == "swamp":
        _draw_swamp(surface, cx, cy, s, frame, pulse)
    elif skin_id == "neon":
        _draw_neon(surface, cx, cy, s, frame, pulse)
    elif skin_id == "crystal":
        _draw_crystal(surface, cx, cy, s, frame, pulse)
    elif skin_id == "lava":
        _draw_lava(surface, cx, cy, s, frame, pulse)
    elif skin_id == "void":
        _draw_void(surface, cx, cy, s, frame, pulse)
    else:
        _draw_default(surface, cx, cy, s, frame, pulse)


def _draw_acid_bubble(surface, x, y, s, color, alpha=200):
    """绘制酸液气泡"""
    bubble_surf = pygame.Surface((int(10 * s), int(10 * s)), pygame.SRCALPHA)
    pygame.draw.circle(bubble_surf, (*color[:3], alpha), (int(5 * s), int(5 * s)), int(4 * s))
    pygame.draw.circle(bubble_surf, (*color[:3], alpha // 2), (int(4 * s), int(4 * s)), int(2 * s))
    surface.blit(bubble_surf, (x - 5 * s, y - 5 * s))


def _draw_drip(surface, cx, cy, s, frame, color, drip_count=5):
    """绘制滴落效果"""
    for i in range(drip_count):
        drip_progress = (frame * 2 + i * 30) % 60
        drip_x = cx + math.sin(i * 1.5) * 15 * s
        drip_y = cy + drip_progress * s * 0.8
        drip_alpha = int(200 * (1 - drip_progress / 60))
        drip_len = 5 + drip_progress * 0.2
        if drip_alpha > 0:
            drip_surf = pygame.Surface((8, int(drip_len * s)), pygame.SRCALPHA)
            pygame.draw.ellipse(drip_surf, (*color[:3], drip_alpha), (0, 0, 8, int(drip_len * s)))
            surface.blit(drip_surf, (drip_x - 4, drip_y))


def _draw_default(surface, cx, cy, s, frame, pulse):
    """酸沼原型 - 荧光绿+腐黑基底"""
    acid_green = (150, 255, 80)
    dark_green = (50, 80, 30)
    glow_green = (180, 255, 120)
    black_base = (30, 40, 20)
    
    # 酸液光晕
    for layer in range(4):
        r = int((30 - layer * 5) * s + pulse)
        alpha = 80 - layer * 15
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*acid_green[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 腐黑基底
    pygame.draw.circle(surface, black_base, (int(cx), int(cy)), int(22 * s))
    
    # 酸液流动纹理
    for i in range(6):
        angle = frame * 0.5 + i * 60
        rad = math.radians(angle)
        stream_r = 15 * s
        sx = cx + math.cos(rad) * stream_r
        sy = cy + math.sin(rad) * stream_r
        pygame.draw.circle(surface, dark_green, (int(sx), int(sy)), int(6 * s))
        pygame.draw.circle(surface, acid_green, (int(sx), int(sy)), int(4 * s))
    
    # 核心酸池
    pygame.draw.circle(surface, dark_green, (int(cx), int(cy)), int(12 * s))
    pygame.draw.circle(surface, acid_green, (int(cx), int(cy)), int(8 * s))
    pygame.draw.circle(surface, glow_green, (int(cx), int(cy)), int(4 * s))
    
    # 气泡
    for i in range(5):
        bubble_angle = frame * 2 + i * 72
        bubble_r = 18 * s + math.sin(frame * 0.2 + i) * 5 * s
        bx = cx + math.cos(math.radians(bubble_angle)) * bubble_r
        by = cy + math.sin(math.radians(bubble_angle)) * bubble_r
        _draw_acid_bubble(surface, bx, by, s * 0.6, acid_green)
    
    # 滴落
    _draw_drip(surface, cx, cy, s, frame, acid_green)


def _draw_toxic(surface, cx, cy, s, frame, pulse):
    """剧毒废液 - 工业污染绿"""
    toxic_green = (100, 180, 50)
    sludge_brown = (80, 70, 40)
    warning_yellow = (255, 200, 0)
    rust_orange = (180, 100, 50)
    
    # 工业废液池
    pygame.draw.circle(surface, sludge_brown, (int(cx), int(cy)), int(25 * s))
    
    # 浮油层
    for i in range(4):
        oil_angle = frame * 0.3 + i * 90
        rad = math.radians(oil_angle)
        oil_r = 18 * s
        ox = cx + math.cos(rad) * oil_r * 0.5
        oy = cy + math.sin(rad) * oil_r * 0.5
        pygame.draw.ellipse(surface, rust_orange, 
                           (ox - 8 * s, oy - 4 * s, 16 * s, 8 * s))
    
    # 剧毒核心
    pygame.draw.circle(surface, toxic_green, (int(cx), int(cy)), int(14 * s))
    pygame.draw.circle(surface, warning_yellow, (int(cx), int(cy)), int(8 * s))
    
    # 警告符号
    pygame.draw.polygon(surface, sludge_brown, [
        (cx, cy - 6 * s),
        (cx - 5 * s, cy + 4 * s),
        (cx + 5 * s, cy + 4 * s)
    ])
    pygame.draw.circle(surface, warning_yellow, (int(cx), int(cy + 1 * s)), int(2 * s))
    
    # 冒泡
    for i in range(6):
        bubble_y = cy - ((frame * 2 + i * 20) % 40) * s * 0.5
        bubble_x = cx + math.sin(i * 2) * 12 * s
        bubble_r = int((3 - ((frame * 2 + i * 20) % 40) / 20) * s)
        if bubble_r > 0:
            pygame.draw.circle(surface, toxic_green, (int(bubble_x), int(bubble_y)), bubble_r)


def _draw_biohazard(surface, cx, cy, s, frame, pulse):
    """生化危机 - 警告标识"""
    bio_yellow = (255, 220, 0)
    bio_black = (30, 30, 30)
    warning_red = (220, 50, 50)
    toxic_green = (100, 200, 50)
    
    # 警告圆环
    pygame.draw.circle(surface, bio_yellow, (int(cx), int(cy)), int(26 * s), int(4 * s))
    pygame.draw.circle(surface, bio_black, (int(cx), int(cy)), int(22 * s), int(2 * s))
    
    # 生化标志
    for i in range(3):
        angle = i * 120 - 90 + frame * 0.3
        rad = math.radians(angle)
        # 三个扇形
        arc_r = 16 * s
        arc_cx = cx + math.cos(rad) * 8 * s
        arc_cy = cy + math.sin(rad) * 8 * s
        pygame.draw.circle(surface, bio_yellow, (int(arc_cx), int(arc_cy)), int(8 * s))
        pygame.draw.circle(surface, bio_black, (int(arc_cx), int(arc_cy)), int(5 * s))
    
    # 中心
    pygame.draw.circle(surface, bio_yellow, (int(cx), int(cy)), int(6 * s))
    pygame.draw.circle(surface, bio_black, (int(cx), int(cy)), int(4 * s))
    
    # 闪烁警告
    if (frame // 15) % 2 == 0:
        warning_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(warning_surf, (*warning_red[:3], 100), (30, 30), int(30 * s))
        surface.blit(warning_surf, (cx - 30, cy - 30))
    
    # 毒气粒子
    for i in range(6):
        gas_angle = frame * 1.5 + i * 60
        gas_r = 28 * s + math.sin(frame * 0.1 + i) * 8 * s
        gx = cx + math.cos(math.radians(gas_angle)) * gas_r
        gy = cy + math.sin(math.radians(gas_angle)) * gas_r
        alpha = int(100 + 50 * math.sin(frame * 0.2 + i))
        gas_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(gas_surf, (*toxic_green[:3], alpha), (5, 5), int(4 * s))
        surface.blit(gas_surf, (gx - 5, gy - 5))


def _draw_slime(surface, cx, cy, s, frame, pulse):
    """史莱姆王 - 半透明果冻"""
    slime_green = (100, 220, 100)
    slime_light = (150, 255, 150)
    slime_dark = (50, 150, 50)
    eye_white = (255, 255, 255)
    
    # 果冻主体（波动）
    wobble = math.sin(frame * 0.15) * 3 * s
    body_points = []
    for i in range(12):
        angle = i * 30
        rad = math.radians(angle)
        r = 22 * s + math.sin(frame * 0.1 + i * 0.5) * 4 * s
        body_points.append((cx + math.cos(rad) * r, cy + math.sin(rad) * r))
    
    # 半透明效果
    slime_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
    offset_points = [(p[0] - cx + 40, p[1] - cy + 40) for p in body_points]
    pygame.draw.polygon(slime_surf, (*slime_green[:3], 180), offset_points)
    surface.blit(slime_surf, (cx - 40, cy - 40))
    
    # 内层
    inner_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.circle(inner_surf, (*slime_light[:3], 150), (30, 30), int(14 * s))
    surface.blit(inner_surf, (cx - 30, cy - 30))
    
    # 可爱眼睛
    eye_offset_x = 5 * s
    eye_y = cy - 3 * s
    # 左眼
    pygame.draw.ellipse(surface, eye_white, (cx - eye_offset_x - 5 * s, eye_y - 4 * s, 8 * s, 10 * s))
    pygame.draw.circle(surface, (0, 0, 0), (int(cx - eye_offset_x), int(eye_y + 1 * s)), int(3 * s))
    # 右眼
    pygame.draw.ellipse(surface, eye_white, (cx + eye_offset_x - 3 * s, eye_y - 4 * s, 8 * s, 10 * s))
    pygame.draw.circle(surface, (0, 0, 0), (int(cx + eye_offset_x), int(eye_y + 1 * s)), int(3 * s))
    
    # 高光
    pygame.draw.circle(surface, slime_light, (int(cx - 8 * s), int(cy - 8 * s)), int(4 * s))
    
    # 小史莱姆
    for i in range(3):
        mini_angle = frame * 0.5 + i * 120
        rad = math.radians(mini_angle)
        mini_r = 28 * s
        mx = cx + math.cos(rad) * mini_r
        my = cy + math.sin(rad) * mini_r
        pygame.draw.circle(surface, slime_green, (int(mx), int(my)), int(5 * s))
        pygame.draw.circle(surface, eye_white, (int(mx), int(my - 1 * s)), int(2 * s))


def _draw_nuclear(surface, cx, cy, s, frame, pulse):
    """核辐射 - 放射性黄绿"""
    nuclear_yellow = (255, 255, 50)
    radiation_green = (150, 255, 50)
    hazard_black = (30, 30, 30)
    glow_green = (200, 255, 100)
    
    # 辐射光晕
    for layer in range(5):
        r = int((35 - layer * 5) * s + pulse)
        alpha = 60 - layer * 10
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*radiation_green[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 辐射符号
    pygame.draw.circle(surface, nuclear_yellow, (int(cx), int(cy)), int(22 * s))
    
    # 三叶草辐射标志
    for i in range(3):
        angle = i * 120 - 90 + frame * 0.2
        rad = math.radians(angle)
        blade_cx = cx + math.cos(rad) * 10 * s
        blade_cy = cy + math.sin(rad) * 10 * s
        pygame.draw.circle(surface, hazard_black, (int(blade_cx), int(blade_cy)), int(8 * s))
    
    # 中心
    pygame.draw.circle(surface, hazard_black, (int(cx), int(cy)), int(5 * s))
    pygame.draw.circle(surface, nuclear_yellow, (int(cx), int(cy)), int(3 * s))
    
    # 放射性粒子
    for i in range(8):
        particle_angle = frame * 3 + i * 45
        particle_r = 25 * s + math.sin(frame * 0.2 + i) * 8 * s
        px = cx + math.cos(math.radians(particle_angle)) * particle_r
        py = cy + math.sin(math.radians(particle_angle)) * particle_r
        pygame.draw.circle(surface, glow_green, (int(px), int(py)), int(2 * s))


def _draw_plague(surface, cx, cy, s, frame, pulse):
    """瘟疫之源 - 腐烂紫绿"""
    plague_purple = (120, 60, 120)
    rot_green = (80, 120, 50)
    decay_brown = (80, 60, 40)
    pus_yellow = (200, 180, 80)
    
    # 腐烂光晕
    for layer in range(3):
        r = int((28 - layer * 6) * s)
        alpha = 80 - layer * 20
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*plague_purple[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 腐肉主体
    body_points = []
    for i in range(10):
        angle = i * 36
        rad = math.radians(angle)
        r = 20 * s + random.Random(i).random() * 5 * s
        body_points.append((cx + math.cos(rad) * r, cy + math.sin(rad) * r))
    pygame.draw.polygon(surface, decay_brown, body_points)
    
    # 腐烂斑块
    for i in range(5):
        spot_angle = i * 72 + 36
        rad = math.radians(spot_angle)
        spot_r = 12 * s
        sx = cx + math.cos(rad) * spot_r
        sy = cy + math.sin(rad) * spot_r
        pygame.draw.circle(surface, rot_green, (int(sx), int(sy)), int(5 * s))
        pygame.draw.circle(surface, plague_purple, (int(sx), int(sy)), int(3 * s))
    
    # 脓液滴落
    for i in range(4):
        pus_y = (frame * 2 + i * 25) % 50
        pus_x = cx + math.sin(i * 2) * 10 * s
        pus_alpha = int(200 * (1 - pus_y / 50))
        if pus_alpha > 0:
            pus_surf = pygame.Surface((8, 12), pygame.SRCALPHA)
            pygame.draw.ellipse(pus_surf, (*pus_yellow[:3], pus_alpha), (0, 0, 8, 12))
            surface.blit(pus_surf, (pus_x - 4, cy + pus_y * s * 0.6))
    
    # 核心
    pygame.draw.circle(surface, plague_purple, (int(cx), int(cy)), int(8 * s))
    pygame.draw.circle(surface, pus_yellow, (int(cx), int(cy)), int(4 * s))


def _draw_venom(surface, cx, cy, s, frame, pulse):
    """蛇毒喷射 - 剧毒紫黑"""
    venom_purple = (100, 30, 120)
    poison_green = (80, 200, 80)
    fang_white = (240, 240, 240)
    dark_black = (20, 10, 25)
    
    # 毒气扩散
    for layer in range(4):
        r = int((32 - layer * 6) * s + pulse)
        alpha = 60 - layer * 12
        gas_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(gas_surf, (*venom_purple[:3], alpha), (r + 2, r + 2), r)
        surface.blit(gas_surf, (cx - r - 2, cy - r - 2))
    
    # 蛇形主体
    pygame.draw.ellipse(surface, dark_black, (cx - 18 * s, cy - 12 * s, 36 * s, 24 * s))
    
    # 蛇鳞
    for i in range(6):
        scale_angle = i * 60
        rad = math.radians(scale_angle)
        scale_r = 10 * s
        scx = cx + math.cos(rad) * scale_r
        scy = cy + math.sin(rad) * scale_r
        pygame.draw.ellipse(surface, venom_purple, (scx - 4 * s, scy - 3 * s, 8 * s, 6 * s))
    
    # 毒牙
    for side in [-1, 1]:
        fang_x = cx + side * 8 * s
        fang_y = cy + 5 * s
        fang_points = [
            (fang_x, fang_y),
            (fang_x - 2 * s, fang_y + 10 * s),
            (fang_x + 2 * s, fang_y + 10 * s)
        ]
        pygame.draw.polygon(surface, fang_white, fang_points)
        # 毒液滴
        drip_y = (frame * 3) % 20
        pygame.draw.circle(surface, poison_green, 
                          (int(fang_x), int(fang_y + 10 * s + drip_y * s * 0.3)), int(2 * s))
    
    # 蛇眼
    for side in [-1, 1]:
        eye_x = cx + side * 6 * s
        eye_y = cy - 3 * s
        pygame.draw.ellipse(surface, (255, 220, 50), (eye_x - 3 * s, eye_y - 4 * s, 6 * s, 8 * s))
        pygame.draw.ellipse(surface, (0, 0, 0), (eye_x - 1 * s, eye_y - 3 * s, 2 * s, 6 * s))


def _draw_swamp(surface, cx, cy, s, frame, pulse):
    """沼泽怪物 - 泥浆棕绿"""
    mud_brown = (100, 80, 50)
    swamp_green = (80, 120, 60)
    moss_green = (60, 100, 40)
    water_dark = (40, 60, 50)
    
    # 沼泽水面
    pygame.draw.circle(surface, water_dark, (int(cx), int(cy)), int(28 * s))
    
    # 泥浆涟漪
    for i in range(3):
        ripple_r = ((frame + i * 30) % 60) * s * 0.4 + 10 * s
        ripple_alpha = int(150 * (1 - ((frame + i * 30) % 60) / 60))
        if ripple_alpha > 0:
            ripple_surf = pygame.Surface((int(ripple_r * 2 + 4), int(ripple_r * 2 + 4)), pygame.SRCALPHA)
            pygame.draw.circle(ripple_surf, (*mud_brown[:3], ripple_alpha), 
                             (int(ripple_r + 2), int(ripple_r + 2)), int(ripple_r), 2)
            surface.blit(ripple_surf, (cx - ripple_r - 2, cy - ripple_r - 2))
    
    # 泥浆怪物
    monster_wobble = math.sin(frame * 0.1) * 3 * s
    monster_points = []
    for i in range(8):
        angle = i * 45
        rad = math.radians(angle)
        r = 18 * s + math.sin(frame * 0.15 + i) * 4 * s
        monster_points.append((cx + math.cos(rad) * r, cy + math.sin(rad) * r + monster_wobble))
    pygame.draw.polygon(surface, mud_brown, monster_points)
    
    # 苔藓斑块
    for i in range(5):
        moss_angle = i * 72 + 20
        rad = math.radians(moss_angle)
        moss_r = 12 * s
        mx = cx + math.cos(rad) * moss_r
        my = cy + math.sin(rad) * moss_r
        pygame.draw.circle(surface, moss_green, (int(mx), int(my)), int(4 * s))
    
    # 眼睛
    eye_y = cy - 5 * s + monster_wobble
    for side in [-1, 1]:
        eye_x = cx + side * 6 * s
        pygame.draw.circle(surface, swamp_green, (int(eye_x), int(eye_y)), int(4 * s))
        pygame.draw.circle(surface, (0, 0, 0), (int(eye_x), int(eye_y)), int(2 * s))
    
    # 气泡
    for i in range(4):
        bubble_y = cy - ((frame + i * 20) % 40) * s * 0.5 - 10 * s
        bubble_x = cx + math.sin(i * 1.5) * 15 * s
        bubble_r = int(3 * s - ((frame + i * 20) % 40) * 0.05 * s)
        if bubble_r > 0:
            pygame.draw.circle(surface, swamp_green, (int(bubble_x), int(bubble_y)), bubble_r)


def _draw_neon(surface, cx, cy, s, frame, pulse):
    """霓虹酸雨 - 赛博朋克"""
    neon_green = (0, 255, 100)
    neon_pink = (255, 0, 150)
    neon_blue = (0, 200, 255)
    dark_bg = (20, 20, 30)
    
    # 霓虹光晕
    for layer, color in enumerate([neon_green, neon_pink, neon_blue]):
        r = int((30 - layer * 4) * s + pulse)
        alpha = 80 - layer * 15
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 深色基底
    pygame.draw.circle(surface, dark_bg, (int(cx), int(cy)), int(20 * s))
    
    # 霓虹环
    pygame.draw.circle(surface, neon_green, (int(cx), int(cy)), int(18 * s), int(2 * s))
    pygame.draw.circle(surface, neon_pink, (int(cx), int(cy)), int(14 * s), int(2 * s))
    pygame.draw.circle(surface, neon_blue, (int(cx), int(cy)), int(10 * s), int(2 * s))
    
    # 闪烁霓虹条
    for i in range(6):
        angle = frame * 2 + i * 60
        rad = math.radians(angle)
        strip_color = [neon_green, neon_pink, neon_blue][i % 3]
        start_r = 20 * s
        end_r = 28 * s
        pygame.draw.line(surface, strip_color,
                        (cx + math.cos(rad) * start_r, cy + math.sin(rad) * start_r),
                        (cx + math.cos(rad) * end_r, cy + math.sin(rad) * end_r), int(3 * s))
    
    # 核心
    pygame.draw.circle(surface, neon_green, (int(cx), int(cy)), int(5 * s))


def _draw_crystal(surface, cx, cy, s, frame, pulse):
    """酸性晶体 - 结晶酸盐"""
    crystal_green = (150, 255, 150)
    crystal_clear = (220, 255, 220)
    acid_yellow = (200, 255, 100)
    dark_green = (50, 100, 50)
    
    # 晶体光晕
    for layer in range(3):
        r = int((28 - layer * 5) * s)
        alpha = 60 - layer * 15
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*crystal_green[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 晶体簇
    for i in range(6):
        angle = i * 60 + frame * 0.3
        rad = math.radians(angle)
        crystal_r = 20 * s
        cr_x = cx + math.cos(rad) * crystal_r * 0.5
        cr_y = cy + math.sin(rad) * crystal_r * 0.5
        
        # 六边形晶体
        crystal_points = []
        for j in range(6):
            c_angle = angle + j * 60
            c_rad = math.radians(c_angle)
            c_r = 10 * s if j % 2 == 0 else 6 * s
            crystal_points.append((cr_x + math.cos(c_rad) * c_r, cr_y + math.sin(c_rad) * c_r))
        pygame.draw.polygon(surface, crystal_clear, crystal_points)
        pygame.draw.polygon(surface, crystal_green, crystal_points, 1)
    
    # 核心晶体
    core_points = []
    for i in range(6):
        angle = i * 60
        rad = math.radians(angle)
        r = 8 * s if i % 2 == 0 else 5 * s
        core_points.append((cx + math.cos(rad) * r, cy + math.sin(rad) * r))
    pygame.draw.polygon(surface, acid_yellow, core_points)
    pygame.draw.polygon(surface, dark_green, core_points, 1)
    
    # 高光
    pygame.draw.circle(surface, crystal_clear, (int(cx - 2 * s), int(cy - 2 * s)), int(3 * s))


def _draw_lava(surface, cx, cy, s, frame, pulse):
    """熔岩酸池 - 橙红酸流"""
    lava_orange = (255, 120, 30)
    lava_red = (255, 60, 20)
    magma_yellow = (255, 200, 50)
    crust_black = (40, 20, 10)
    
    # 熔岩光晕
    for layer in range(4):
        r = int((32 - layer * 5) * s + pulse)
        alpha = 80 - layer * 15
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*lava_orange[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 熔岩池
    pygame.draw.circle(surface, lava_red, (int(cx), int(cy)), int(22 * s))
    
    # 岩壳
    for i in range(5):
        crust_angle = i * 72 + frame * 0.2
        rad = math.radians(crust_angle)
        crust_r = 18 * s
        crust_x = cx + math.cos(rad) * crust_r * 0.7
        crust_y = cy + math.sin(rad) * crust_r * 0.7
        crust_size = 6 * s + random.Random(i).random() * 4 * s
        pygame.draw.circle(surface, crust_black, (int(crust_x), int(crust_y)), int(crust_size))
    
    # 熔岩流动
    for i in range(4):
        flow_angle = frame * 0.5 + i * 90
        rad = math.radians(flow_angle)
        flow_r = 10 * s
        fx = cx + math.cos(rad) * flow_r
        fy = cy + math.sin(rad) * flow_r
        pygame.draw.circle(surface, magma_yellow, (int(fx), int(fy)), int(5 * s))
    
    # 核心
    pygame.draw.circle(surface, lava_orange, (int(cx), int(cy)), int(8 * s))
    pygame.draw.circle(surface, magma_yellow, (int(cx), int(cy)), int(4 * s))
    
    # 火星
    for i in range(6):
        spark_y = cy - ((frame * 3 + i * 15) % 40) * s * 0.5 - 5 * s
        spark_x = cx + math.sin(frame * 0.2 + i) * 15 * s
        spark_alpha = int(255 * (1 - ((frame * 3 + i * 15) % 40) / 40))
        if spark_alpha > 0:
            spark_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(spark_surf, (*magma_yellow[:3], spark_alpha), (3, 3), int(2 * s))
            surface.blit(spark_surf, (spark_x - 3, spark_y - 3))


def _draw_void(surface, cx, cy, s, frame, pulse):
    """虚空腐蚀 - 暗紫酸雾"""
    void_purple = (80, 30, 120)
    void_black = (20, 10, 30)
    rift_cyan = (0, 180, 200)
    acid_glow = (150, 100, 200)
    
    # 虚空漩涡
    for layer in range(5):
        r = int((35 - layer * 5) * s + pulse)
        alpha = 60 - layer * 10
        angle_offset = frame * (0.5 + layer * 0.2)
        
        vortex_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        # 螺旋臂
        for i in range(4):
            arm_angle = angle_offset + i * 90
            rad = math.radians(arm_angle)
            for j in range(10):
                arm_r = r * j / 10
                arm_x = r + 2 + math.cos(rad + j * 0.3) * arm_r
                arm_y = r + 2 + math.sin(rad + j * 0.3) * arm_r
                pygame.draw.circle(vortex_surf, (*void_purple[:3], alpha), (int(arm_x), int(arm_y)), int(3 * s))
        surface.blit(vortex_surf, (cx - r - 2, cy - r - 2))
    
    # 虚空核心
    pygame.draw.circle(surface, void_black, (int(cx), int(cy)), int(15 * s))
    
    # 裂隙能量
    for i in range(4):
        rift_angle = i * 90 + frame
        rad = math.radians(rift_angle)
        rift_len = 20 * s
        pygame.draw.line(surface, rift_cyan,
                        (cx, cy),
                        (cx + math.cos(rad) * rift_len, cy + math.sin(rad) * rift_len), int(2 * s))
    
    # 核心之眼
    pygame.draw.circle(surface, void_purple, (int(cx), int(cy)), int(8 * s))
    pygame.draw.circle(surface, rift_cyan, (int(cx), int(cy)), int(4 * s))
    pygame.draw.circle(surface, acid_glow, (int(cx), int(cy)), int(2 * s))
    
    # 虚空粒子
    for i in range(8):
        particle_angle = frame * 2 + i * 45
        particle_r = 22 * s + math.sin(frame * 0.15 + i) * 8 * s
        px = cx + math.cos(math.radians(particle_angle)) * particle_r
        py = cy + math.sin(math.radians(particle_angle)) * particle_r
        pygame.draw.circle(surface, acid_glow, (int(px), int(py)), int(2 * s))
