# -*- coding: utf-8 -*-
"""
棘刺藤骨·荆穹 (Thornvine) - 专属涂装渲染模块
骨白深红的藤蔓生物兵器，以荆棘缠绕吞噬敌人

涂装列表 (12种完全不同形态):
1. thornvine_default - 骨蔓原型（骨白藤蔓+深红棘刺）
2. thornvine_bloodthorn - 血棘荆冠（血染的荆棘王冠）
3. thornvine_fossil - 远古化石（石化藤骨）
4. thornvine_venom - 毒蔓猎手（剧毒浸染的猎杀者）
5. thornvine_winter - 霜骨寒蔓（冰封的枯骨藤蔓）
6. thornvine_infernal - 炼狱棘藤（燃烧的地狱荆棘）
7. thornvine_jade - 翡翠骨莲（玉化的骨骼莲花）
8. thornvine_nightmare - 噩梦缠绕（暗紫恐惧编织）
9. thornvine_golden - 黄金荆冠（帝王的荆棘之冕）
10. thornvine_spectral - 幽魂藤骨（魂火缠绕的骨蔓）
11. thornvine_coral - 深海珊瑚（海底珊瑚骨架）
12. thornvine_void - 虚空棘刺（次元裂隙中的荆棘）
"""
import pygame
import math
import random

# Thornvine涂装样式列表
THORNVINE_STYLES = [
    "thornvine_default",
    "thornvine_bloodthorn",
    "thornvine_fossil",
    "thornvine_venom",
    "thornvine_winter",
    "thornvine_infernal",
    "thornvine_jade",
    "thornvine_nightmare",
    "thornvine_golden",
    "thornvine_spectral",
    "thornvine_coral",
    "thornvine_void"
]


def is_thornvine_style(model_style):
    """检查是否为 Thornvine 涂装样式"""
    return model_style in THORNVINE_STYLES


def render_thornvine_skin(surface, c, model_style, t, pid, static):
    """渲染 Thornvine 专属涂装"""
    if model_style not in THORNVINE_STYLES:
        return None
    
    skin_id = model_style.replace("thornvine_", "")
    frame = 0 if static else int(t * 60) % 360
    draw_thornvine(surface, c, 60, 60, scale=1.8, skin_id=skin_id, frame=frame)
    return surface


def _render_thornvine_base(surface, t, pulse):
    """基础机体渲染（用于base.py调用）"""
    frame = int(t * 60) % 360
    draw_thornvine(surface, (200, 180, 150), 60, 60, scale=1.8, skin_id="default", frame=frame)


def draw_thornvine(surface, color, x, y, scale=1.0, skin_id="default", frame=0):

    """绘制荆穹 - 12种独特形态"""
    cx, cy = x, y
    s = scale
    pulse = math.sin(frame * 0.1) * 3
    
    if skin_id == "default":
        _draw_default(surface, cx, cy, s, frame, pulse)
    elif skin_id == "bloodthorn":
        _draw_bloodthorn(surface, cx, cy, s, frame, pulse)
    elif skin_id == "fossil":
        _draw_fossil(surface, cx, cy, s, frame, pulse)
    elif skin_id == "venom":
        _draw_venom(surface, cx, cy, s, frame, pulse)
    elif skin_id == "winter":
        _draw_winter(surface, cx, cy, s, frame, pulse)
    elif skin_id == "infernal":
        _draw_infernal(surface, cx, cy, s, frame, pulse)
    elif skin_id == "jade":
        _draw_jade(surface, cx, cy, s, frame, pulse)
    elif skin_id == "nightmare":
        _draw_nightmare(surface, cx, cy, s, frame, pulse)
    elif skin_id == "golden":
        _draw_golden(surface, cx, cy, s, frame, pulse)
    elif skin_id == "spectral":
        _draw_spectral(surface, cx, cy, s, frame, pulse)
    elif skin_id == "coral":
        _draw_coral(surface, cx, cy, s, frame, pulse)
    elif skin_id == "void":
        _draw_void(surface, cx, cy, s, frame, pulse)
    else:
        _draw_default(surface, cx, cy, s, frame, pulse)


def _draw_bone_vine(surface, cx, cy, s, angle, length, bone_color, thorn_color, segments=5, frame=0):
    """绘制通用骨蔓（带棘刺）"""
    rad = math.radians(angle)
    wave_offset = math.sin(frame * 0.08 + angle * 0.05) * 4 * s
    
    # 分段骨节
    prev_x, prev_y = cx, cy
    for i in range(segments):
        seg_length = length / segments
        seg_angle = angle + math.sin(frame * 0.05 + i * 0.8) * 15
        seg_rad = math.radians(seg_angle)
        
        next_x = prev_x + math.cos(seg_rad) * seg_length * s
        next_y = prev_y + math.sin(seg_rad) * seg_length * s
        
        # 骨节
        thickness = int((4 - i * 0.5) * s)
        pygame.draw.line(surface, bone_color, (prev_x, prev_y), (next_x, next_y), max(1, thickness))
        
        # 关节
        joint_r = int((3 - i * 0.3) * s)
        pygame.draw.circle(surface, bone_color, (int(next_x), int(next_y)), joint_r)
        
        # 棘刺（每节两侧）
        if i < segments - 1:
            thorn_len = (8 - i) * s
            for side in [-1, 1]:
                thorn_angle = seg_angle + side * 70
                thorn_rad = math.radians(thorn_angle)
                thorn_x = (prev_x + next_x) / 2 + math.cos(thorn_rad) * thorn_len
                thorn_y = (prev_y + next_y) / 2 + math.sin(thorn_rad) * thorn_len
                mid_x, mid_y = (prev_x + next_x) / 2, (prev_y + next_y) / 2
                pygame.draw.line(surface, thorn_color, (mid_x, mid_y), (thorn_x, thorn_y), max(1, int(2 * s)))
        
        prev_x, prev_y = next_x, next_y
    
    return prev_x, prev_y


def _draw_default(surface, cx, cy, s, frame, pulse):
    """骨蔓原型 - 骨白藤蔓主体，深红棘刺点缀"""
    bone_white = (240, 235, 220)
    thorn_red = (180, 50, 50)
    core_dark = (60, 40, 40)
    
    # 放射状骨蔓
    for i in range(6):
        angle = i * 60 + frame * 0.3
        _draw_bone_vine(surface, cx, cy, s, angle, 35, bone_white, thorn_red, segments=4, frame=frame)
    
    # 中央核心 - 脊椎骨构造
    for layer in range(3):
        r = int((15 - layer * 3) * s)
        color = (240 - layer * 30, 235 - layer * 30, 220 - layer * 25)
        pygame.draw.circle(surface, color, (int(cx), int(cy)), r)
    
    # 核心棘刺环
    for i in range(8):
        angle = i * 45 + frame * 0.5
        rad = math.radians(angle)
        thorn_r = 8 * s
        start_r = 12 * s
        tx = cx + math.cos(rad) * (start_r + thorn_r)
        ty = cy + math.sin(rad) * (start_r + thorn_r)
        pygame.draw.line(surface, thorn_red, 
                        (cx + math.cos(rad) * start_r, cy + math.sin(rad) * start_r),
                        (tx, ty), int(3 * s))
        pygame.draw.circle(surface, thorn_red, (int(tx), int(ty)), int(2 * s))
    
    # 核心深色圆点
    pygame.draw.circle(surface, core_dark, (int(cx), int(cy)), int(5 * s))


def _draw_bloodthorn(surface, cx, cy, s, frame, pulse):
    """血棘荆冠 - 血染的荆棘王冠，滴血效果"""
    blood_red = (150, 20, 30)
    dark_blood = (80, 10, 15)
    thorn_black = (40, 20, 25)
    
    # 血液滴落效果
    for i in range(5):
        drop_y = (frame * 2 + i * 40) % 60
        drop_x = cx + math.sin(i * 1.5) * 20 * s
        drop_alpha = int(200 * (1 - drop_y / 60))
        drop_surf = pygame.Surface((10, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(drop_surf, (*blood_red[:3], drop_alpha), (2, 0, 6, int(8 + drop_y * 0.2)))
        surface.blit(drop_surf, (drop_x - 5, cy + drop_y * s - 30 * s))
    
    # 荆棘冠主体
    crown_points = []
    for i in range(12):
        angle = i * 30 - 90
        rad = math.radians(angle)
        outer_r = 28 * s if i % 2 == 0 else 22 * s
        inner_variation = math.sin(frame * 0.1 + i) * 3 * s
        r = outer_r + inner_variation
        crown_points.append((cx + math.cos(rad) * r, cy + math.sin(rad) * r))
    pygame.draw.polygon(surface, dark_blood, crown_points)
    pygame.draw.polygon(surface, blood_red, crown_points, int(3 * s))
    
    # 尖锐棘刺
    for i in range(8):
        angle = i * 45 + 22.5
        rad = math.radians(angle)
        base_r = 25 * s
        tip_r = 40 * s + math.sin(frame * 0.15 + i) * 5 * s
        pygame.draw.line(surface, thorn_black,
                        (cx + math.cos(rad) * base_r, cy + math.sin(rad) * base_r),
                        (cx + math.cos(rad) * tip_r, cy + math.sin(rad) * tip_r), int(3 * s))
    
    # 中心血珠
    for layer in range(3):
        r = int((12 - layer * 3) * s + pulse * 0.3)
        pygame.draw.circle(surface, (blood_red[0] + layer * 20, blood_red[1], blood_red[2]), 
                          (int(cx), int(cy)), r)
    # 高光
    pygame.draw.circle(surface, (220, 80, 80), (int(cx - 3 * s), int(cy - 3 * s)), int(3 * s))


def _draw_fossil(surface, cx, cy, s, frame, pulse):
    """远古化石 - 石化的藤蔓骨骼"""
    stone_gray = (140, 135, 125)
    fossil_brown = (100, 90, 70)
    crack_dark = (60, 55, 45)
    amber = (180, 140, 60)
    
    # 石化藤蔓
    for i in range(5):
        angle = i * 72 + 36
        _draw_bone_vine(surface, cx, cy, s, angle, 32, stone_gray, fossil_brown, segments=4, frame=0)  # 静止
    
    # 石化主体
    body_points = []
    for i in range(8):
        angle = i * 45
        rad = math.radians(angle)
        r = (18 + random.Random(i).random() * 5) * s
        body_points.append((cx + math.cos(rad) * r, cy + math.sin(rad) * r))
    pygame.draw.polygon(surface, stone_gray, body_points)
    pygame.draw.polygon(surface, fossil_brown, body_points, 2)
    
    # 裂纹
    for i in range(6):
        seed = random.Random(i + 100)
        crack_start = (cx + seed.randint(-10, 10) * s, cy + seed.randint(-10, 10) * s)
        crack_end = (crack_start[0] + seed.randint(-15, 15) * s, crack_start[1] + seed.randint(-15, 15) * s)
        pygame.draw.line(surface, crack_dark, crack_start, crack_end, 1)
    
    # 琥珀包裹的小虫（点缀）
    amber_x = cx + 8 * s
    amber_y = cy - 5 * s
    pygame.draw.ellipse(surface, amber, (amber_x - 5 * s, amber_y - 3 * s, 10 * s, 6 * s))
    pygame.draw.ellipse(surface, (200, 160, 80), (amber_x - 3 * s, amber_y - 2 * s, 6 * s, 4 * s))
    
    # 化石纹理中心
    pygame.draw.circle(surface, fossil_brown, (int(cx), int(cy)), int(8 * s))
    pygame.draw.circle(surface, stone_gray, (int(cx), int(cy)), int(5 * s))


def _draw_venom(surface, cx, cy, s, frame, pulse):
    """毒蔓猎手 - 剧毒浸染，毒液滴落"""
    venom_green = (80, 200, 50)
    dark_green = (30, 80, 20)
    poison_purple = (120, 50, 150)
    
    # 毒气粒子
    for i in range(8):
        particle_angle = frame * 2 + i * 45
        particle_r = 30 * s + math.sin(frame * 0.1 + i) * 10 * s
        px = cx + math.cos(math.radians(particle_angle)) * particle_r
        py = cy + math.sin(math.radians(particle_angle)) * particle_r
        alpha = int(100 + 50 * math.sin(frame * 0.15 + i))
        particle_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, (*venom_green[:3], alpha), (6, 6), int(4 * s))
        surface.blit(particle_surf, (px - 6, py - 6))
    
    # 毒蔓
    for i in range(5):
        angle = i * 72 + frame * 0.2
        _draw_bone_vine(surface, cx, cy, s, angle, 30, dark_green, venom_green, segments=4, frame=frame)
    
    # 毒囊核心
    for layer in range(4):
        r = int((16 - layer * 3) * s + pulse * 0.4)
        color_blend = (
            venom_green[0] - layer * 15,
            venom_green[1] - layer * 30,
            venom_green[2] + layer * 10
        )
        pygame.draw.circle(surface, color_blend, (int(cx), int(cy)), r)
    
    # 毒液气泡
    for i in range(4):
        bubble_offset = (frame * 3 + i * 20) % 40
        bubble_x = cx + math.sin(i * 2) * 8 * s
        bubble_y = cy - bubble_offset * s * 0.5 - 5 * s
        bubble_r = int((3 - bubble_offset / 20) * s)
        if bubble_r > 0:
            pygame.draw.circle(surface, venom_green, (int(bubble_x), int(bubble_y)), bubble_r)
    
    # 紫色毒刺尖端
    for i in range(6):
        angle = i * 60 + 30
        rad = math.radians(angle)
        tip_x = cx + math.cos(rad) * 25 * s
        tip_y = cy + math.sin(rad) * 25 * s
        pygame.draw.circle(surface, poison_purple, (int(tip_x), int(tip_y)), int(3 * s))


def _draw_winter(surface, cx, cy, s, frame, pulse):
    """霜骨寒蔓 - 冰封的枯骨藤蔓"""
    ice_white = (220, 240, 255)
    frost_blue = (150, 200, 240)
    bone_pale = (200, 210, 220)
    deep_ice = (80, 120, 180)
    
    # 冰霜粒子飘落
    for i in range(10):
        snow_x = cx + math.sin(frame * 0.05 + i * 0.8) * 35 * s
        snow_y = cy + ((frame + i * 15) % 50 - 25) * s
        snow_alpha = int(150 + 50 * math.sin(i))
        snow_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(snow_surf, (*ice_white[:3], snow_alpha), (3, 3), int(2 * s))
        surface.blit(snow_surf, (snow_x - 3, snow_y - 3))
    
    # 冰封藤蔓
    for i in range(5):
        angle = i * 72
        _draw_bone_vine(surface, cx, cy, s, angle, 30, bone_pale, frost_blue, segments=4, frame=0)
    
    # 冰晶棘刺
    for i in range(8):
        angle = i * 45 + 22.5
        rad = math.radians(angle)
        base_r = 20 * s
        tip_r = 32 * s
        # 六边形冰晶
        tip_x = cx + math.cos(rad) * tip_r
        tip_y = cy + math.sin(rad) * tip_r
        crystal_points = []
        for j in range(6):
            c_angle = angle + j * 60
            c_rad = math.radians(c_angle)
            c_r = 4 * s
            crystal_points.append((tip_x + math.cos(c_rad) * c_r, tip_y + math.sin(c_rad) * c_r))
        pygame.draw.polygon(surface, frost_blue, crystal_points)
        pygame.draw.line(surface, ice_white, 
                        (cx + math.cos(rad) * base_r, cy + math.sin(rad) * base_r),
                        (tip_x, tip_y), int(2 * s))
    
    # 冰冻核心
    pygame.draw.circle(surface, frost_blue, (int(cx), int(cy)), int(14 * s))
    pygame.draw.circle(surface, ice_white, (int(cx), int(cy)), int(10 * s))
    pygame.draw.circle(surface, deep_ice, (int(cx), int(cy)), int(5 * s))


def _draw_infernal(surface, cx, cy, s, frame, pulse):
    """炼狱棘藤 - 燃烧的地狱荆棘"""
    flame_orange = (255, 120, 30)
    fire_red = (255, 60, 20)
    ember_yellow = (255, 200, 50)
    char_black = (40, 20, 10)
    
    # 火焰光晕
    for layer in range(4):
        r = int((35 - layer * 5) * s + pulse)
        alpha = 60 - layer * 12
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*flame_orange[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 燃烧藤蔓
    for i in range(5):
        angle = i * 72 + frame * 0.5
        # 炭化骨节
        _draw_bone_vine(surface, cx, cy, s, angle, 28, char_black, fire_red, segments=4, frame=frame)
        # 火焰附着
        for j in range(3):
            flame_angle = angle + (j - 1) * 20
            flame_r = (15 + j * 5) * s
            fx = cx + math.cos(math.radians(flame_angle)) * flame_r
            fy = cy + math.sin(math.radians(flame_angle)) * flame_r
            flame_h = 10 * s + math.sin(frame * 0.2 + j) * 4 * s
            # 火焰三角
            flame_points = [
                (fx, fy - flame_h),
                (fx - 4 * s, fy + 2 * s),
                (fx + 4 * s, fy + 2 * s)
            ]
            pygame.draw.polygon(surface, ember_yellow, flame_points)
    
    # 熔岩核心
    for layer in range(3):
        r = int((12 - layer * 3) * s + pulse * 0.5)
        color = (
            255,
            120 + layer * 40,
            30 + layer * 20
        )
        pygame.draw.circle(surface, color, (int(cx), int(cy)), r)
    
    # 火星
    for i in range(6):
        spark_angle = frame * 4 + i * 60
        spark_r = 20 * s + math.sin(frame * 0.3 + i) * 8 * s
        sx = cx + math.cos(math.radians(spark_angle)) * spark_r
        sy = cy + math.sin(math.radians(spark_angle)) * spark_r
        pygame.draw.circle(surface, ember_yellow, (int(sx), int(sy)), int(2 * s))


def _draw_jade(surface, cx, cy, s, frame, pulse):
    """翡翠骨莲 - 玉化的骨骼莲花"""
    jade_green = (100, 200, 130)
    pale_jade = (180, 230, 200)
    deep_jade = (40, 120, 80)
    gold_accent = (220, 180, 80)
    
    # 莲花花瓣
    for i in range(8):
        angle = i * 45 + frame * 0.2
        rad = math.radians(angle)
        petal_r = 25 * s
        
        # 花瓣形状
        petal_cx = cx + math.cos(rad) * 12 * s
        petal_cy = cy + math.sin(rad) * 12 * s
        petal_points = [
            (petal_cx, petal_cy),
            (cx + math.cos(rad - 0.3) * petal_r, cy + math.sin(rad - 0.3) * petal_r),
            (cx + math.cos(rad) * (petal_r + 8 * s), cy + math.sin(rad) * (petal_r + 8 * s)),
            (cx + math.cos(rad + 0.3) * petal_r, cy + math.sin(rad + 0.3) * petal_r),
        ]
        pygame.draw.polygon(surface, jade_green if i % 2 == 0 else pale_jade, petal_points)
        pygame.draw.polygon(surface, deep_jade, petal_points, 1)
    
    # 玉骨藤蔓
    for i in range(4):
        angle = i * 90 + 45
        _draw_bone_vine(surface, cx, cy, s, angle, 20, pale_jade, jade_green, segments=3, frame=frame)
    
    # 莲心
    pygame.draw.circle(surface, jade_green, (int(cx), int(cy)), int(12 * s))
    pygame.draw.circle(surface, pale_jade, (int(cx), int(cy)), int(8 * s))
    
    # 金色花蕊
    for i in range(6):
        angle = i * 60 + frame * 0.5
        rad = math.radians(angle)
        stamen_r = 6 * s
        sx = cx + math.cos(rad) * stamen_r
        sy = cy + math.sin(rad) * stamen_r
        pygame.draw.circle(surface, gold_accent, (int(sx), int(sy)), int(2 * s))
    
    # 中心宝石
    pygame.draw.circle(surface, deep_jade, (int(cx), int(cy)), int(4 * s))
    pygame.draw.circle(surface, (220, 255, 230), (int(cx - 1 * s), int(cy - 1 * s)), int(1.5 * s))


def _draw_nightmare(surface, cx, cy, s, frame, pulse):
    """噩梦缠绕 - 暗紫恐惧编织"""
    nightmare_purple = (80, 30, 120)
    shadow_black = (20, 10, 30)
    fear_magenta = (150, 50, 130)
    eye_yellow = (255, 220, 50)
    
    # 阴影触手
    for i in range(6):
        angle = i * 60 + math.sin(frame * 0.08 + i) * 20
        _draw_bone_vine(surface, cx, cy, s, angle, 35, shadow_black, nightmare_purple, segments=5, frame=frame)
    
    # 恐惧之眼
    for i in range(3):
        eye_angle = i * 120 + frame * 0.3
        rad = math.radians(eye_angle)
        eye_r = 18 * s
        ex = cx + math.cos(rad) * eye_r
        ey = cy + math.sin(rad) * eye_r
        
        # 眼白
        pygame.draw.ellipse(surface, fear_magenta, (ex - 6 * s, ey - 4 * s, 12 * s, 8 * s))
        # 瞳孔（跟踪）
        pupil_offset_x = math.sin(frame * 0.1) * 2 * s
        pupil_offset_y = math.cos(frame * 0.1) * 1 * s
        pygame.draw.circle(surface, eye_yellow, (int(ex + pupil_offset_x), int(ey + pupil_offset_y)), int(3 * s))
        pygame.draw.circle(surface, shadow_black, (int(ex + pupil_offset_x), int(ey + pupil_offset_y)), int(1.5 * s))
    
    # 核心暗影
    for layer in range(4):
        r = int((15 - layer * 3) * s + pulse * 0.3)
        alpha = 200 - layer * 40
        core_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(core_surf, (*nightmare_purple[:3], alpha), (r + 2, r + 2), r)
        surface.blit(core_surf, (cx - r - 2, cy - r - 2))
    
    # 中心虚空
    pygame.draw.circle(surface, shadow_black, (int(cx), int(cy)), int(6 * s))


def _draw_golden(surface, cx, cy, s, frame, pulse):
    """黄金荆冠 - 帝王的荆棘之冕"""
    gold = (255, 215, 0)
    dark_gold = (180, 140, 20)
    royal_red = (180, 30, 50)
    shine_white = (255, 250, 220)
    
    # 金色光芒
    for i in range(12):
        angle = i * 30 + frame * 0.3
        rad = math.radians(angle)
        ray_length = (25 + math.sin(frame * 0.15 + i) * 8) * s
        pygame.draw.line(surface, dark_gold,
                        (cx + math.cos(rad) * 15 * s, cy + math.sin(rad) * 15 * s),
                        (cx + math.cos(rad) * ray_length, cy + math.sin(rad) * ray_length), int(2 * s))
    
    # 荆冠
    crown_points = []
    for i in range(10):
        angle = i * 36 - 90
        rad = math.radians(angle)
        r = 22 * s if i % 2 == 0 else 28 * s
        crown_points.append((cx + math.cos(rad) * r, cy + math.sin(rad) * r))
    pygame.draw.polygon(surface, gold, crown_points)
    pygame.draw.polygon(surface, dark_gold, crown_points, 2)
    
    # 皇冠尖端
    for i in range(5):
        angle = i * 72 - 90
        rad = math.radians(angle)
        tip_r = 32 * s
        tx = cx + math.cos(rad) * tip_r
        ty = cy + math.sin(rad) * tip_r
        pygame.draw.circle(surface, royal_red, (int(tx), int(ty)), int(4 * s))
        pygame.draw.circle(surface, (255, 100, 120), (int(tx - 1 * s), int(ty - 1 * s)), int(1.5 * s))
    
    # 中心王冠
    pygame.draw.circle(surface, gold, (int(cx), int(cy)), int(12 * s))
    pygame.draw.circle(surface, dark_gold, (int(cx), int(cy)), int(8 * s))
    pygame.draw.circle(surface, royal_red, (int(cx), int(cy)), int(4 * s))
    
    # 闪光
    shine_angle = frame * 2
    shine_x = cx + math.cos(math.radians(shine_angle)) * 5 * s
    shine_y = cy + math.sin(math.radians(shine_angle)) * 5 * s
    pygame.draw.circle(surface, shine_white, (int(shine_x), int(shine_y)), int(2 * s))


def _draw_spectral(surface, cx, cy, s, frame, pulse):
    """幽魂藤骨 - 魂火缠绕的骨蔓"""
    soul_blue = (100, 200, 255)
    ghost_white = (220, 240, 255)
    bone_gray = (180, 180, 190)
    void_purple = (80, 50, 150)
    
    # 魂火粒子
    for i in range(10):
        flame_angle = frame * 2 + i * 36
        flame_r = 25 * s + math.sin(frame * 0.1 + i) * 10 * s
        fx = cx + math.cos(math.radians(flame_angle)) * flame_r
        fy = cy + math.sin(math.radians(flame_angle)) * flame_r - 5 * s
        alpha = int(150 + 50 * math.sin(frame * 0.2 + i))
        flame_surf = pygame.Surface((14, 20), pygame.SRCALPHA)
        # 魂火形状
        pygame.draw.ellipse(flame_surf, (*soul_blue[:3], alpha), (3, 6, 8, 12))
        pygame.draw.ellipse(flame_surf, (*ghost_white[:3], alpha // 2), (4, 2, 6, 8))
        surface.blit(flame_surf, (fx - 7, fy - 10))
    
    # 幽灵藤蔓
    for i in range(5):
        angle = i * 72 + frame * 0.4
        _draw_bone_vine(surface, cx, cy, s, angle, 28, bone_gray, soul_blue, segments=4, frame=frame)
    
    # 核心魂火
    for layer in range(4):
        r = int((14 - layer * 3) * s + pulse * 0.5)
        alpha = 200 - layer * 40
        core_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(core_surf, (*soul_blue[:3], alpha), (r + 2, r + 2), r)
        surface.blit(core_surf, (cx - r - 2, cy - r - 2))
    
    # 虚空核心
    pygame.draw.circle(surface, void_purple, (int(cx), int(cy)), int(5 * s))
    pygame.draw.circle(surface, ghost_white, (int(cx - 1 * s), int(cy - 1 * s)), int(2 * s))


def _draw_coral(surface, cx, cy, s, frame, pulse):
    """深海珊瑚 - 海底珊瑚骨架"""
    coral_pink = (255, 130, 150)
    coral_orange = (255, 160, 100)
    deep_blue = (30, 60, 120)
    seafoam = (150, 220, 200)
    
    # 水泡
    for i in range(8):
        bubble_y = cy - ((frame + i * 20) % 50) * s
        bubble_x = cx + math.sin(frame * 0.1 + i) * 20 * s
        bubble_r = int((3 + (i % 3)) * s)
        alpha = int(150 - ((frame + i * 20) % 50) * 2)
        if alpha > 0:
            bubble_surf = pygame.Surface((bubble_r * 2 + 4, bubble_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(bubble_surf, (*seafoam[:3], alpha), (bubble_r + 2, bubble_r + 2), bubble_r)
            pygame.draw.circle(bubble_surf, (*coral_pink[:3], alpha // 2), (bubble_r, bubble_r), bubble_r // 2)
            surface.blit(bubble_surf, (bubble_x - bubble_r - 2, bubble_y - bubble_r - 2))
    
    # 珊瑚分支
    for i in range(6):
        angle = i * 60 + frame * 0.1
        branch_color = coral_pink if i % 2 == 0 else coral_orange
        _draw_coral_branch(surface, cx, cy, s, angle, 25, branch_color)
    
    # 珊瑚核心
    pygame.draw.circle(surface, coral_orange, (int(cx), int(cy)), int(12 * s))
    pygame.draw.circle(surface, coral_pink, (int(cx), int(cy)), int(8 * s))
    
    # 珊瑚孔洞
    for i in range(5):
        hole_angle = i * 72 + 36
        rad = math.radians(hole_angle)
        hx = cx + math.cos(rad) * 5 * s
        hy = cy + math.sin(rad) * 5 * s
        pygame.draw.circle(surface, deep_blue, (int(hx), int(hy)), int(2 * s))


def _draw_coral_branch(surface, cx, cy, s, angle, length, color):
    """绘制珊瑚分支"""
    rad = math.radians(angle)
    segments = 3
    prev_x, prev_y = cx, cy
    
    for i in range(segments):
        seg_length = length / segments * (1 - i * 0.2)
        next_x = prev_x + math.cos(rad) * seg_length * s
        next_y = prev_y + math.sin(rad) * seg_length * s
        
        thickness = int((5 - i * 1.5) * s)
        pygame.draw.line(surface, color, (prev_x, prev_y), (next_x, next_y), max(1, thickness))
        
        # 分叉
        if i < segments - 1:
            for side in [-1, 1]:
                fork_angle = angle + side * 40
                fork_rad = math.radians(fork_angle)
                fork_len = 8 * s
                fork_x = next_x + math.cos(fork_rad) * fork_len
                fork_y = next_y + math.sin(fork_rad) * fork_len
                pygame.draw.line(surface, color, (next_x, next_y), (fork_x, fork_y), max(1, thickness - 1))
        
        prev_x, prev_y = next_x, next_y


def _draw_void(surface, cx, cy, s, frame, pulse):
    """虚空棘刺 - 次元裂隙中的荆棘"""
    void_purple = (60, 20, 100)
    rift_cyan = (0, 200, 220)
    dark_void = (20, 5, 40)
    star_white = (220, 220, 255)
    
    # 次元裂隙
    for i in range(4):
        rift_angle = i * 90 + frame * 0.5
        rad = math.radians(rift_angle)
        rift_len = 30 * s
        # 裂隙线
        rift_points = [
            (cx + math.cos(rad) * 10 * s, cy + math.sin(rad) * 10 * s),
            (cx + math.cos(rad - 0.1) * rift_len, cy + math.sin(rad - 0.1) * rift_len),
            (cx + math.cos(rad) * (rift_len + 5 * s), cy + math.sin(rad) * (rift_len + 5 * s)),
            (cx + math.cos(rad + 0.1) * rift_len, cy + math.sin(rad + 0.1) * rift_len),
        ]
        pygame.draw.polygon(surface, rift_cyan, rift_points)
        pygame.draw.polygon(surface, dark_void, rift_points, 1)
    
    # 虚空藤蔓
    for i in range(5):
        angle = i * 72 + 36 + frame * 0.3
        _draw_bone_vine(surface, cx, cy, s, angle, 25, void_purple, rift_cyan, segments=4, frame=frame)
    
    # 次元核心
    for layer in range(4):
        r = int((14 - layer * 3) * s + pulse * 0.4)
        alpha = 180 - layer * 35
        core_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(core_surf, (*void_purple[:3], alpha), (r + 2, r + 2), r)
        surface.blit(core_surf, (cx - r - 2, cy - r - 2))
    
    # 虚空之眼
    pygame.draw.circle(surface, rift_cyan, (int(cx), int(cy)), int(6 * s))
    pygame.draw.circle(surface, dark_void, (int(cx), int(cy)), int(3 * s))
    
    # 星尘点缀
    for i in range(8):
        star_angle = frame * 1.5 + i * 45
        star_r = 20 * s + math.sin(frame * 0.2 + i * 0.5) * 8 * s
        sx = cx + math.cos(math.radians(star_angle)) * star_r
        sy = cy + math.sin(math.radians(star_angle)) * star_r
        pygame.draw.circle(surface, star_white, (int(sx), int(sy)), int(1.5 * s))
