# -*- coding: utf-8 -*-
"""
孢子幕炮·菌幕 (Sporeveil) - 专属涂装渲染模块
孢子绿云幕白的生物孢子战机，以孢子云幕覆盖战场

涂装列表 (12种完全不同形态):
1. sporeveil_default - 菌幕原型（孢子绿+云幕白）
2. sporeveil_mushroom - 蘑菇王国（可爱蘑菇）
3. sporeveil_toxic - 毒蕈云雾（致命毒菌）
4. sporeveil_biolume - 生物发光（深海荧光）
5. sporeveil_pollen - 花粉风暴（春日花粉）
6. sporeveil_mycelium - 菌丝网络（地下网络）
7. sporeveil_ancient - 远古孢子（史前菌类）
8. sporeveil_frost - 霜冻孢子（冰封菌落）
9. sporeveil_ember - 灰烬孢子（火山灰菌）
10. sporeveil_void - 虚空菌落（异次元孢子）
11. sporeveil_crystal - 水晶孢子（晶化菌体）
12. sporeveil_rainbow - 彩虹菌伞（幻彩孢子）
"""
import pygame
import math
import random

# Sporeveil涂装样式列表
SPOREVEIL_STYLES = [
    "sporeveil_default",
    "sporeveil_mushroom",
    "sporeveil_toxic",
    "sporeveil_biolume",
    "sporeveil_pollen",
    "sporeveil_mycelium",
    "sporeveil_ancient",
    "sporeveil_frost",
    "sporeveil_ember",
    "sporeveil_void",
    "sporeveil_crystal",
    "sporeveil_rainbow"
]


def is_sporeveil_style(model_style):
    """检查是否为 Sporeveil 涂装样式"""
    return model_style in SPOREVEIL_STYLES


def render_sporeveil_skin(surface, c, model_style, t, pid, static):
    """渲染 Sporeveil 专属涂装"""
    if model_style not in SPOREVEIL_STYLES:
        return None
    
    skin_id = model_style.replace("sporeveil_", "")
    frame = 0 if static else int(t * 60) % 360
    draw_sporeveil(surface, c, 60, 60, scale=1.8, skin_id=skin_id, frame=frame)
    return surface


def _render_sporeveil_base(surface, t, pulse):
    """基础机体渲染（用于base.py调用）"""
    frame = int(t * 60) % 360
    draw_sporeveil(surface, (120, 180, 100), 60, 60, scale=1.8, skin_id="default", frame=frame)


def draw_sporeveil(surface, color, x, y, scale=1.0, skin_id="default", frame=0):
    """绘制菌幕 - 12种独特形态"""
    cx, cy = x, y
    s = scale
    pulse = math.sin(frame * 0.1) * 3
    
    if skin_id == "default":
        _draw_default(surface, cx, cy, s, frame, pulse)
    elif skin_id == "mushroom":
        _draw_mushroom(surface, cx, cy, s, frame, pulse)
    elif skin_id == "toxic":
        _draw_toxic(surface, cx, cy, s, frame, pulse)
    elif skin_id == "biolume":
        _draw_biolume(surface, cx, cy, s, frame, pulse)
    elif skin_id == "pollen":
        _draw_pollen(surface, cx, cy, s, frame, pulse)
    elif skin_id == "mycelium":
        _draw_mycelium(surface, cx, cy, s, frame, pulse)
    elif skin_id == "ancient":
        _draw_ancient(surface, cx, cy, s, frame, pulse)
    elif skin_id == "frost":
        _draw_frost(surface, cx, cy, s, frame, pulse)
    elif skin_id == "ember":
        _draw_ember(surface, cx, cy, s, frame, pulse)
    elif skin_id == "void":
        _draw_void(surface, cx, cy, s, frame, pulse)
    elif skin_id == "crystal":
        _draw_crystal(surface, cx, cy, s, frame, pulse)
    elif skin_id == "rainbow":
        _draw_rainbow(surface, cx, cy, s, frame, pulse)
    else:
        _draw_default(surface, cx, cy, s, frame, pulse)


def _draw_spore_particle(surface, x, y, s, color, alpha=200, size=3):
    """绘制孢子粒子"""
    spore_surf = pygame.Surface((int(size * 2 * s + 4), int(size * 2 * s + 4)), pygame.SRCALPHA)
    pygame.draw.circle(spore_surf, (*color[:3], alpha), (int(size * s + 2), int(size * s + 2)), int(size * s))
    surface.blit(spore_surf, (x - size * s - 2, y - size * s - 2))


def _draw_mushroom_cap(surface, cx, cy, s, cap_color, spot_color, stem_color, cap_width=20, cap_height=12):
    """绘制蘑菇帽"""
    # 菌柄
    pygame.draw.rect(surface, stem_color, 
                    (cx - 4 * s, cy, 8 * s, 10 * s))
    
    # 菌伞
    cap_rect = (cx - cap_width * s / 2, cy - cap_height * s, cap_width * s, cap_height * s * 1.5)
    pygame.draw.ellipse(surface, cap_color, cap_rect)
    
    # 斑点
    for i in range(4):
        spot_angle = i * 90 + 45
        rad = math.radians(spot_angle)
        spot_r = cap_width * 0.3 * s
        sx = cx + math.cos(rad) * spot_r
        sy = cy - cap_height * 0.4 * s + math.sin(rad) * spot_r * 0.3
        pygame.draw.circle(surface, spot_color, (int(sx), int(sy)), int(3 * s))


def _draw_default(surface, cx, cy, s, frame, pulse):
    """菌幕原型 - 孢子绿+云幕白"""
    spore_green = (100, 180, 100)
    veil_white = (240, 250, 240)
    glow_green = (150, 220, 150)
    core_dark = (50, 100, 50)
    
    # 孢子云幕光晕
    for layer in range(5):
        r = int((35 - layer * 5) * s + pulse)
        alpha = 50 - layer * 8
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*spore_green[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 漂浮孢子
    for i in range(12):
        spore_angle = frame * 1.2 + i * 30
        spore_r = 22 * s + math.sin(frame * 0.1 + i * 0.5) * 8 * s
        sx = cx + math.cos(math.radians(spore_angle)) * spore_r
        sy = cy + math.sin(math.radians(spore_angle)) * spore_r
        alpha = int(150 + 50 * math.sin(frame * 0.15 + i))
        _draw_spore_particle(surface, sx, sy, s, spore_green, alpha)
    
    # 菌幕主体
    pygame.draw.circle(surface, veil_white, (int(cx), int(cy)), int(18 * s))
    
    # 孢子纹理
    for i in range(6):
        tex_angle = i * 60 + frame * 0.2
        rad = math.radians(tex_angle)
        tex_r = 12 * s
        tx = cx + math.cos(rad) * tex_r
        ty = cy + math.sin(rad) * tex_r
        pygame.draw.circle(surface, spore_green, (int(tx), int(ty)), int(4 * s))
    
    # 核心
    pygame.draw.circle(surface, spore_green, (int(cx), int(cy)), int(10 * s))
    pygame.draw.circle(surface, glow_green, (int(cx), int(cy)), int(6 * s))
    pygame.draw.circle(surface, veil_white, (int(cx), int(cy)), int(3 * s))


def _draw_mushroom(surface, cx, cy, s, frame, pulse):
    """蘑菇王国 - 可爱蘑菇群"""
    cap_red = (220, 80, 80)
    spot_white = (255, 255, 255)
    stem_beige = (240, 220, 200)
    grass_green = (80, 150, 80)
    
    # 小蘑菇群
    mushroom_positions = [
        (cx - 15 * s, cy + 5 * s, 0.6),
        (cx + 18 * s, cy + 3 * s, 0.5),
        (cx - 8 * s, cy + 12 * s, 0.4),
        (cx + 10 * s, cy + 10 * s, 0.45),
    ]
    for mx, my, ms in mushroom_positions:
        _draw_mushroom_cap(surface, mx, my, s * ms, cap_red, spot_white, stem_beige, 16, 10)
    
    # 主蘑菇
    wobble = math.sin(frame * 0.1) * 2 * s
    _draw_mushroom_cap(surface, cx, cy + wobble, s, cap_red, spot_white, stem_beige)
    
    # 可爱表情
    eye_y = cy - 5 * s + wobble
    # 眼睛
    for side in [-1, 1]:
        eye_x = cx + side * 5 * s
        pygame.draw.circle(surface, (0, 0, 0), (int(eye_x), int(eye_y)), int(3 * s))
        pygame.draw.circle(surface, spot_white, (int(eye_x - 1 * s), int(eye_y - 1 * s)), int(1 * s))
    # 腮红
    pygame.draw.circle(surface, (255, 180, 180), (int(cx - 10 * s), int(eye_y + 3 * s)), int(3 * s))
    pygame.draw.circle(surface, (255, 180, 180), (int(cx + 10 * s), int(eye_y + 3 * s)), int(3 * s))
    
    # 小孢子
    for i in range(6):
        spore_y = cy - ((frame + i * 20) % 50) * s * 0.5 - 15 * s
        spore_x = cx + math.sin(frame * 0.1 + i) * 20 * s
        alpha = int(200 * (1 - ((frame + i * 20) % 50) / 50))
        if alpha > 0:
            _draw_spore_particle(surface, spore_x, spore_y, s * 0.5, spot_white, alpha)


def _draw_toxic(surface, cx, cy, s, frame, pulse):
    """毒蕈云雾 - 致命毒菌"""
    toxic_purple = (120, 50, 150)
    poison_green = (150, 255, 50)
    dark_purple = (60, 20, 80)
    skull_white = (240, 240, 240)
    
    # 毒气云
    for layer in range(4):
        r = int((32 - layer * 5) * s + pulse)
        alpha = 60 - layer * 12
        gas_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(gas_surf, (*toxic_purple[:3], alpha), (r + 2, r + 2), r)
        surface.blit(gas_surf, (cx - r - 2, cy - r - 2))
    
    # 毒蕈主体
    cap_points = []
    for i in range(8):
        angle = i * 45 - 90
        rad = math.radians(angle)
        r = 20 * s if i % 2 == 0 else 16 * s
        cap_points.append((cx + math.cos(rad) * r, cy + math.sin(rad) * r * 0.6 - 5 * s))
    pygame.draw.polygon(surface, toxic_purple, cap_points)
    
    # 菌柄
    pygame.draw.rect(surface, dark_purple, (cx - 5 * s, cy - 3 * s, 10 * s, 15 * s))
    
    # 毒液滴
    for i in range(4):
        drip_y = (frame * 2 + i * 25) % 40
        drip_x = cx + (i - 1.5) * 6 * s
        drip_alpha = int(200 * (1 - drip_y / 40))
        if drip_alpha > 0:
            pygame.draw.ellipse(surface, (*poison_green[:3], drip_alpha),
                              (drip_x - 2 * s, cy + drip_y * s * 0.5 + 5 * s, 4 * s, 6 * s))
    
    # 骷髅标记
    pygame.draw.circle(surface, skull_white, (int(cx), int(cy - 8 * s)), int(6 * s))
    pygame.draw.ellipse(surface, skull_white, (cx - 5 * s, cy - 5 * s, 10 * s, 6 * s))
    # 眼洞
    pygame.draw.circle(surface, dark_purple, (int(cx - 3 * s), int(cy - 9 * s)), int(2 * s))
    pygame.draw.circle(surface, dark_purple, (int(cx + 3 * s), int(cy - 9 * s)), int(2 * s))
    
    # 毒孢子
    for i in range(8):
        spore_angle = frame * 2 + i * 45
        spore_r = 25 * s + math.sin(frame * 0.15 + i) * 8 * s
        sx = cx + math.cos(math.radians(spore_angle)) * spore_r
        sy = cy + math.sin(math.radians(spore_angle)) * spore_r
        _draw_spore_particle(surface, sx, sy, s, poison_green, 180)


def _draw_biolume(surface, cx, cy, s, frame, pulse):
    """生物发光 - 深海荧光菌"""
    deep_blue = (10, 30, 60)
    biolume_cyan = (0, 255, 200)
    biolume_blue = (50, 150, 255)
    glow_white = (200, 255, 255)
    
    # 深海背景光
    for layer in range(4):
        r = int((35 - layer * 6) * s)
        alpha = 40 - layer * 8
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*biolume_cyan[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 发光菌体
    pygame.draw.circle(surface, deep_blue, (int(cx), int(cy)), int(18 * s))
    
    # 发光脉络
    for i in range(6):
        vein_angle = i * 60 + frame * 0.3
        rad = math.radians(vein_angle)
        vein_len = 15 * s
        
        # 脉络曲线
        points = [(cx, cy)]
        for j in range(5):
            vx = cx + math.cos(rad) * j * 3 * s + math.sin(frame * 0.2 + j) * 2 * s
            vy = cy + math.sin(rad) * j * 3 * s
            points.append((vx, vy))
        
        if len(points) > 2:
            pygame.draw.lines(surface, biolume_cyan, False, points, int(2 * s))
    
    # 发光点
    for i in range(8):
        glow_angle = frame * 1.5 + i * 45
        glow_r = 12 * s + math.sin(frame * 0.1 + i) * 4 * s
        gx = cx + math.cos(math.radians(glow_angle)) * glow_r
        gy = cy + math.sin(math.radians(glow_angle)) * glow_r
        
        # 脉冲发光
        pulse_alpha = int(150 + 100 * math.sin(frame * 0.2 + i))
        glow_surf = pygame.Surface((int(8 * s), int(8 * s)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*biolume_cyan[:3], pulse_alpha), (int(4 * s), int(4 * s)), int(3 * s))
        surface.blit(glow_surf, (gx - 4 * s, gy - 4 * s))
    
    # 核心
    pygame.draw.circle(surface, biolume_blue, (int(cx), int(cy)), int(8 * s))
    pygame.draw.circle(surface, glow_white, (int(cx), int(cy)), int(4 * s))


def _draw_pollen(surface, cx, cy, s, frame, pulse):
    """花粉风暴 - 春日花粉"""
    pollen_yellow = (255, 230, 100)
    petal_pink = (255, 180, 200)
    leaf_green = (100, 180, 80)
    center_orange = (255, 180, 50)
    
    # 花粉风暴
    for i in range(20):
        pollen_angle = frame * 2 + i * 18
        pollen_r = 15 * s + (i % 4) * 6 * s + math.sin(frame * 0.1 + i) * 5 * s
        px = cx + math.cos(math.radians(pollen_angle)) * pollen_r
        py = cy + math.sin(math.radians(pollen_angle)) * pollen_r
        alpha = int(150 + 50 * math.sin(frame * 0.15 + i))
        _draw_spore_particle(surface, px, py, s * 0.6, pollen_yellow, alpha, size=2)
    
    # 花朵主体
    # 花瓣
    for i in range(5):
        petal_angle = i * 72 + frame * 0.2
        rad = math.radians(petal_angle)
        petal_cx = cx + math.cos(rad) * 10 * s
        petal_cy = cy + math.sin(rad) * 10 * s
        
        pygame.draw.ellipse(surface, petal_pink,
                           (petal_cx - 6 * s, petal_cy - 10 * s, 12 * s, 18 * s))
    
    # 花心
    pygame.draw.circle(surface, center_orange, (int(cx), int(cy)), int(10 * s))
    pygame.draw.circle(surface, pollen_yellow, (int(cx), int(cy)), int(6 * s))
    
    # 花粉粒
    for i in range(6):
        grain_angle = frame * 0.5 + i * 60
        rad = math.radians(grain_angle)
        grain_r = 6 * s
        gx = cx + math.cos(rad) * grain_r
        gy = cy + math.sin(rad) * grain_r
        pygame.draw.circle(surface, pollen_yellow, (int(gx), int(gy)), int(2 * s))
    
    # 叶子装饰
    for side in [-1, 1]:
        leaf_x = cx + side * 20 * s
        leaf_y = cy + 8 * s
        pygame.draw.ellipse(surface, leaf_green,
                           (leaf_x - 8 * s, leaf_y - 4 * s, 16 * s, 8 * s))


def _draw_mycelium(surface, cx, cy, s, frame, pulse):
    """菌丝网络 - 地下网络"""
    mycel_white = (240, 240, 230)
    soil_brown = (80, 60, 40)
    node_purple = (150, 100, 180)
    glow_blue = (100, 150, 255)
    
    # 土壤背景
    pygame.draw.circle(surface, soil_brown, (int(cx), int(cy)), int(25 * s))
    
    # 菌丝网络
    nodes = []
    for i in range(8):
        angle = i * 45 + random.Random(i).random() * 20
        rad = math.radians(angle)
        node_r = 18 * s + random.Random(i + 10).random() * 8 * s
        nx = cx + math.cos(rad) * node_r
        ny = cy + math.sin(rad) * node_r
        nodes.append((nx, ny))
    
    # 菌丝连接
    for i, (nx, ny) in enumerate(nodes):
        # 连接到中心
        _draw_mycelium_thread(surface, cx, cy, nx, ny, s, mycel_white, frame)
        # 连接到相邻节点
        next_node = nodes[(i + 1) % len(nodes)]
        _draw_mycelium_thread(surface, nx, ny, next_node[0], next_node[1], s * 0.7, mycel_white, frame)
    
    # 节点
    for nx, ny in nodes:
        pygame.draw.circle(surface, node_purple, (int(nx), int(ny)), int(4 * s))
        # 发光效果
        glow_alpha = int(100 + 50 * math.sin(frame * 0.15))
        glow_surf = pygame.Surface((int(10 * s), int(10 * s)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*glow_blue[:3], glow_alpha), (int(5 * s), int(5 * s)), int(4 * s))
        surface.blit(glow_surf, (nx - 5 * s, ny - 5 * s))
    
    # 中心核心
    pygame.draw.circle(surface, node_purple, (int(cx), int(cy)), int(10 * s))
    pygame.draw.circle(surface, mycel_white, (int(cx), int(cy)), int(6 * s))


def _draw_mycelium_thread(surface, x1, y1, x2, y2, s, color, frame):
    """绘制菌丝线"""
    # 波动菌丝
    points = []
    segments = 8
    for i in range(segments + 1):
        t = i / segments
        mx = x1 + (x2 - x1) * t
        my = y1 + (y2 - y1) * t
        # 波动
        perp_x = -(y2 - y1)
        perp_y = x2 - x1
        length = math.sqrt(perp_x ** 2 + perp_y ** 2)
        if length > 0:
            perp_x /= length
            perp_y /= length
        wave = math.sin(frame * 0.1 + i * 0.5) * 3 * s * (1 - abs(t - 0.5) * 2)
        mx += perp_x * wave
        my += perp_y * wave
        points.append((mx, my))
    
    if len(points) > 2:
        pygame.draw.lines(surface, color, False, points, max(1, int(1.5 * s)))


def _draw_ancient(surface, cx, cy, s, frame, pulse):
    """远古孢子 - 史前菌类"""
    fossil_gray = (140, 130, 120)
    amber = (200, 150, 50)
    ancient_green = (80, 100, 60)
    stone = (100, 95, 85)
    
    # 石化外壳
    shell_points = []
    for i in range(10):
        angle = i * 36
        rad = math.radians(angle)
        r = 22 * s + random.Random(i).random() * 4 * s
        shell_points.append((cx + math.cos(rad) * r, cy + math.sin(rad) * r))
    pygame.draw.polygon(surface, fossil_gray, shell_points)
    pygame.draw.polygon(surface, stone, shell_points, 2)
    
    # 裂纹
    for i in range(5):
        crack_angle = i * 72 + 20
        rad = math.radians(crack_angle)
        crack_len = 15 * s
        pygame.draw.line(surface, stone,
                        (cx + math.cos(rad) * 5 * s, cy + math.sin(rad) * 5 * s),
                        (cx + math.cos(rad) * crack_len, cy + math.sin(rad) * crack_len), 1)
    
    # 琥珀保存的孢子
    amber_glow = pygame.Surface((int(30 * s), int(30 * s)), pygame.SRCALPHA)
    pygame.draw.circle(amber_glow, (*amber[:3], 150), (int(15 * s), int(15 * s)), int(12 * s))
    surface.blit(amber_glow, (cx - 15 * s, cy - 15 * s))
    
    # 内部远古孢子
    pygame.draw.circle(surface, ancient_green, (int(cx), int(cy)), int(10 * s))
    
    # 远古纹理
    for i in range(4):
        tex_angle = i * 90 + 45
        rad = math.radians(tex_angle)
        pygame.draw.line(surface, stone,
                        (cx, cy),
                        (cx + math.cos(rad) * 8 * s, cy + math.sin(rad) * 8 * s), int(2 * s))
    
    # 核心
    pygame.draw.circle(surface, amber, (int(cx), int(cy)), int(5 * s))


def _draw_frost(surface, cx, cy, s, frame, pulse):
    """霜冻孢子 - 冰封菌落"""
    ice_blue = (180, 220, 255)
    frost_white = (245, 250, 255)
    deep_ice = (100, 150, 200)
    snow = (255, 255, 255)
    
    # 冰霜光晕
    for layer in range(3):
        r = int((28 - layer * 6) * s + pulse)
        alpha = 50 - layer * 12
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*ice_blue[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 冰封菌体
    pygame.draw.circle(surface, deep_ice, (int(cx), int(cy)), int(18 * s))
    pygame.draw.circle(surface, ice_blue, (int(cx), int(cy)), int(14 * s))
    
    # 冰晶孢子
    for i in range(6):
        crystal_angle = i * 60 + frame * 0.3
        rad = math.radians(crystal_angle)
        crystal_r = 20 * s
        crx = cx + math.cos(rad) * crystal_r
        cry = cy + math.sin(rad) * crystal_r
        
        # 六角冰晶
        crystal_points = []
        for j in range(6):
            c_angle = crystal_angle + j * 60
            c_rad = math.radians(c_angle)
            c_r = 6 * s if j % 2 == 0 else 4 * s
            crystal_points.append((crx + math.cos(c_rad) * c_r, cry + math.sin(c_rad) * c_r))
        pygame.draw.polygon(surface, frost_white, crystal_points)
    
    # 核心
    pygame.draw.circle(surface, frost_white, (int(cx), int(cy)), int(8 * s))
    pygame.draw.circle(surface, deep_ice, (int(cx), int(cy)), int(4 * s))
    
    # 雪花粒子
    for i in range(10):
        snow_angle = frame * 1.5 + i * 36
        snow_r = 25 * s + math.sin(frame * 0.1 + i) * 6 * s
        sx = cx + math.cos(math.radians(snow_angle)) * snow_r
        sy = cy + math.sin(math.radians(snow_angle)) * snow_r
        pygame.draw.circle(surface, snow, (int(sx), int(sy)), int(2 * s))


def _draw_ember(surface, cx, cy, s, frame, pulse):
    """灰烬孢子 - 火山灰菌"""
    ash_gray = (100, 95, 90)
    ember_orange = (255, 120, 30)
    fire_red = (255, 60, 20)
    char_black = (40, 35, 30)
    
    # 灰烬光晕
    for layer in range(3):
        r = int((30 - layer * 6) * s + pulse)
        alpha = 50 - layer * 12
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*ember_orange[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 灰烬主体
    pygame.draw.circle(surface, char_black, (int(cx), int(cy)), int(18 * s))
    
    # 裂纹发光
    for i in range(6):
        crack_angle = i * 60 + frame * 0.2
        rad = math.radians(crack_angle)
        crack_len = 15 * s
        # 发光裂纹
        pygame.draw.line(surface, ember_orange,
                        (cx, cy),
                        (cx + math.cos(rad) * crack_len, cy + math.sin(rad) * crack_len), int(3 * s))
        pygame.draw.line(surface, fire_red,
                        (cx, cy),
                        (cx + math.cos(rad) * crack_len * 0.8, cy + math.sin(rad) * crack_len * 0.8), int(2 * s))
    
    # 火星孢子
    for i in range(10):
        spark_y = cy - ((frame * 3 + i * 15) % 50) * s * 0.6 - 10 * s
        spark_x = cx + math.sin(frame * 0.15 + i) * 18 * s
        spark_alpha = int(255 * (1 - ((frame * 3 + i * 15) % 50) / 50))
        if spark_alpha > 0:
            spark_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(spark_surf, (*ember_orange[:3], spark_alpha), (4, 4), int(3 * s))
            surface.blit(spark_surf, (spark_x - 4, spark_y - 4))
    
    # 核心熔岩
    pygame.draw.circle(surface, fire_red, (int(cx), int(cy)), int(8 * s))
    pygame.draw.circle(surface, ember_orange, (int(cx), int(cy)), int(5 * s))


def _draw_void(surface, cx, cy, s, frame, pulse):
    """虚空菌落 - 异次元孢子"""
    void_purple = (60, 20, 100)
    void_black = (15, 5, 25)
    rift_cyan = (0, 200, 220)
    dark_spore = (80, 40, 120)
    
    # 虚空漩涡
    for layer in range(5):
        r = int((35 - layer * 5) * s)
        alpha = 40 - layer * 6
        angle_offset = frame * (0.3 + layer * 0.1)
        
        for i in range(6):
            swirl_angle = angle_offset + i * 60
            rad = math.radians(swirl_angle)
            swirl_r = r * 0.7
            sx = cx + math.cos(rad) * swirl_r
            sy = cy + math.sin(rad) * swirl_r
            
            swirl_surf = pygame.Surface((int(10 * s), int(10 * s)), pygame.SRCALPHA)
            pygame.draw.circle(swirl_surf, (*void_purple[:3], alpha), (int(5 * s), int(5 * s)), int(4 * s))
            surface.blit(swirl_surf, (sx - 5 * s, sy - 5 * s))
    
    # 虚空菌体
    pygame.draw.circle(surface, void_black, (int(cx), int(cy)), int(16 * s))
    
    # 裂隙触手
    for i in range(4):
        tentacle_angle = i * 90 + frame * 0.5
        rad = math.radians(tentacle_angle)
        
        points = [(cx, cy)]
        for j in range(5):
            tx = cx + math.cos(rad + math.sin(frame * 0.1 + j) * 0.3) * (j + 1) * 5 * s
            ty = cy + math.sin(rad + math.sin(frame * 0.1 + j) * 0.3) * (j + 1) * 5 * s
            points.append((tx, ty))
        
        if len(points) > 2:
            pygame.draw.lines(surface, rift_cyan, False, points, int(2 * s))
    
    # 核心
    pygame.draw.circle(surface, dark_spore, (int(cx), int(cy)), int(8 * s))
    pygame.draw.circle(surface, rift_cyan, (int(cx), int(cy)), int(4 * s))
    
    # 虚空孢子
    for i in range(8):
        spore_angle = frame * 2 + i * 45
        spore_r = 22 * s + math.sin(frame * 0.15 + i) * 8 * s
        sx = cx + math.cos(math.radians(spore_angle)) * spore_r
        sy = cy + math.sin(math.radians(spore_angle)) * spore_r
        pygame.draw.circle(surface, rift_cyan, (int(sx), int(sy)), int(2 * s))


def _draw_crystal(surface, cx, cy, s, frame, pulse):
    """水晶孢子 - 晶化菌体"""
    crystal_purple = (180, 140, 220)
    crystal_clear = (230, 220, 250)
    amethyst = (140, 80, 180)
    glow_white = (250, 245, 255)
    
    # 晶体光晕
    for layer in range(3):
        r = int((28 - layer * 6) * s + pulse)
        alpha = 50 - layer * 12
        glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*crystal_purple[:3], alpha), (r + 2, r + 2), r)
        surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # 晶化菌体
    pygame.draw.circle(surface, amethyst, (int(cx), int(cy)), int(16 * s))
    
    # 晶体尖刺
    for i in range(8):
        angle = i * 45 + frame * 0.2
        rad = math.radians(angle)
        spike_len = 22 * s + math.sin(frame * 0.1 + i) * 3 * s
        
        # 晶体形状
        tip_x = cx + math.cos(rad) * spike_len
        tip_y = cy + math.sin(rad) * spike_len
        side_rad1 = math.radians(angle + 90)
        side_rad2 = math.radians(angle - 90)
        
        points = [
            (tip_x, tip_y),
            (cx + math.cos(side_rad1) * 4 * s, cy + math.sin(side_rad1) * 4 * s),
            (cx, cy),
            (cx + math.cos(side_rad2) * 4 * s, cy + math.sin(side_rad2) * 4 * s),
        ]
        pygame.draw.polygon(surface, crystal_clear, points)
        pygame.draw.polygon(surface, crystal_purple, points, 1)
    
    # 核心
    pygame.draw.circle(surface, crystal_purple, (int(cx), int(cy)), int(8 * s))
    pygame.draw.circle(surface, glow_white, (int(cx), int(cy)), int(4 * s))
    
    # 晶尘
    for i in range(6):
        dust_angle = frame * 1.5 + i * 60
        dust_r = 20 * s + math.sin(frame * 0.2 + i) * 6 * s
        dx = cx + math.cos(math.radians(dust_angle)) * dust_r
        dy = cy + math.sin(math.radians(dust_angle)) * dust_r
        pygame.draw.circle(surface, glow_white, (int(dx), int(dy)), int(2 * s))


def _draw_rainbow(surface, cx, cy, s, frame, pulse):
    """彩虹菌伞 - 幻彩孢子"""
    rainbow_colors = [
        (255, 100, 100),  # 红
        (255, 180, 100),  # 橙
        (255, 255, 100),  # 黄
        (100, 255, 100),  # 绿
        (100, 200, 255),  # 蓝
        (180, 100, 255),  # 紫
    ]
    
    # 彩虹光环
    for i, color in enumerate(rainbow_colors):
        r = int((32 - i * 3) * s)
        alpha = 60
        ring_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (*color[:3], alpha), (r + 2, r + 2), r, int(3 * s))
        surface.blit(ring_surf, (cx - r - 2, cy - r - 2))
    
    # 菌伞
    cap_colors = []
    for i in range(8):
        color_idx = (i + int(frame / 20)) % 6
        cap_colors.append(rainbow_colors[color_idx])
    
    for i in range(8):
        angle = i * 45 - 90
        rad = math.radians(angle)
        # 扇形花瓣
        petal_points = [
            (cx, cy),
            (cx + math.cos(rad - 0.35) * 18 * s, cy + math.sin(rad - 0.35) * 12 * s),
            (cx + math.cos(rad) * 20 * s, cy + math.sin(rad) * 14 * s),
            (cx + math.cos(rad + 0.35) * 18 * s, cy + math.sin(rad + 0.35) * 12 * s),
        ]
        pygame.draw.polygon(surface, cap_colors[i], petal_points)
    
    # 核心
    pygame.draw.circle(surface, (255, 255, 255), (int(cx), int(cy)), int(8 * s))
    core_color = rainbow_colors[int(frame / 10) % 6]
    pygame.draw.circle(surface, core_color, (int(cx), int(cy)), int(5 * s))
    
    # 彩虹孢子
    for i in range(12):
        spore_angle = frame * 2 + i * 30
        spore_r = 22 * s + math.sin(frame * 0.15 + i) * 6 * s
        sx = cx + math.cos(math.radians(spore_angle)) * spore_r
        sy = cy + math.sin(math.radians(spore_angle)) * spore_r
        color = rainbow_colors[i % 6]
        pygame.draw.circle(surface, color, (int(sx), int(sy)), int(2 * s))
