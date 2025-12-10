# -*- coding: utf-8 -*-
"""
终极机体涂装 - Genesis（创世之翼·起源）

宇宙原初之力的化身，拥有创造与毁灭并存的宇宙美学
"""
import pygame
import math

# Genesis 涂装样式列表
GENESIS_STYLES = [
    "genesis_cosmic",      # 宇宙起源 - 星空深蓝
    "genesis_solar",       # 太阳诞生 - 金红炽焰
    "genesis_nebula",      # 星云孕育 - 紫粉梦幻
    "genesis_void",        # 虚无创生 - 黑白对立
    "genesis_life",        # 生命之源 - 翠绿金辉
    "genesis_crystal",     # 水晶世界 - 冰蓝透明
    "genesis_chaos",       # 混沌原初 - 多彩混乱
    "genesis_ex",          # EX改装涂装
    "genesis_ex2",         # EX2改装涂装
    "genesis_ex3",         # EX3改装涂装
    "genesis_ex4",         # EX4改装涂装
    "genesis_ex5",         # EX5改装涂装
]


def is_genesis_style(model_style):
    """检查是否为 Genesis 涂装样式"""
    return model_style in GENESIS_STYLES


def render_genesis_skin(s, c, model_style, t, pid, static):
    """渲染 Genesis 专属涂装"""
    if not is_genesis_style(model_style):
        return None
    
    pulse = 0 if static else abs(math.sin(t * 3))
    
    if model_style == "genesis_cosmic":
        _render_genesis_cosmic(s, t, pulse)
    elif model_style == "genesis_solar":
        _render_genesis_solar(s, t, pulse)
    elif model_style == "genesis_nebula":
        _render_genesis_nebula(s, t, pulse)
    elif model_style == "genesis_void":
        _render_genesis_void(s, t, pulse)
    elif model_style == "genesis_life":
        _render_genesis_life(s, t, pulse)
    elif model_style == "genesis_crystal":
        _render_genesis_crystal(s, t, pulse)
    elif model_style == "genesis_chaos":
        _render_genesis_chaos(s, t, pulse)
    elif model_style.startswith("genesis_ex"):
        _render_genesis_ex(s, t, pulse, model_style)
    else:
        _render_genesis_base(s, t, pulse)
    
    return s


def _render_genesis_base(s, t, pulse):
    """Genesis 基础渲染 - 创世之翼的宇宙形态"""
    # 宇宙色系
    cosmic_gold = (255, 200, 100)
    star_white = (255, 255, 255)
    void_black = (10, 10, 30)
    nebula_pink = (255, 150, 200)
    
    # 宇宙大爆炸扩散环
    for ring in range(5):
        ring_r = 15 + ring * 10 + int(5 * math.sin(t * 3 - ring * 0.5))
        ring_alpha = 200 - ring * 35
        ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 渐变色环
        ring_color = (
            int(255 - ring * 20),
            int(200 - ring * 30),
            int(100 + ring * 20)
        )
        pygame.draw.circle(ring_surf, (*ring_color, ring_alpha), (60, 60), ring_r, 3)
        s.blit(ring_surf, (0, 0))
    
    # 创世之翼（双翼展开）
    for side in [-1, 1]:
        wing_base_x = 60 + side * 15
        
        # 主翼羽
        for feather in range(6):
            f_angle = (side * (20 + feather * 12) + math.sin(t * 2 + feather * 0.3) * 8)
            f_len = 25 + feather * 6
            fx = wing_base_x + side * math.cos(f_angle * 0.01745) * f_len
            fy = 50 - math.sin(f_angle * 0.01745) * f_len * 0.5
            
            # 羽毛渐变
            f_alpha = 255 - feather * 30
            f_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(f_surf, (*cosmic_gold, f_alpha), (wing_base_x, 50), (int(fx), int(fy)), 3)
            
            # 羽尖光点
            pygame.draw.circle(f_surf, (*star_white, f_alpha), (int(fx), int(fy)), 3)
            s.blit(f_surf, (0, 0))
    
    # 中心创世核心
    # 外层能量场
    core_glow_r = int(22 + 4 * pulse)
    pygame.draw.circle(s, cosmic_gold, (60, 55), core_glow_r)
    pygame.draw.circle(s, (255, 220, 150), (60, 55), core_glow_r - 4)
    
    # 内核
    pygame.draw.circle(s, star_white, (60, 55), 12)
    pygame.draw.circle(s, cosmic_gold, (60, 55), 8)
    
    # 轨道粒子（行星形成）
    for planet in range(8):
        p_angle = (planet * 45 + t * 40) * 0.01745
        p_r = 38 + int(3 * math.sin(t * 5 + planet))
        px = 60 + math.cos(p_angle) * p_r
        py = 55 + math.sin(p_angle) * p_r * 0.6  # 椭圆轨道
        
        # 行星颜色变化
        planet_colors = [
            (255, 100, 100), (255, 200, 100), (200, 255, 100), (100, 255, 200),
            (100, 200, 255), (150, 100, 255), (255, 100, 200), (255, 255, 100)
        ]
        pygame.draw.circle(s, planet_colors[planet], (int(px), int(py)), 4)
    
    # 尾部能量流
    for trail in range(5):
        trail_y = 75 + trail * 8
        trail_width = 20 - trail * 3
        trail_alpha = 200 - trail * 35
        trail_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.ellipse(trail_surf, (*cosmic_gold, trail_alpha), 
                          (60 - trail_width, trail_y, trail_width * 2, 6))
        s.blit(trail_surf, (0, 0))


def _render_genesis_cosmic(s, t, pulse):
    """宇宙起源 - 星空深蓝主题"""
    deep_blue = (20, 40, 100)
    star_blue = (100, 150, 255)
    white = (255, 255, 255)
    
    # 深空背景
    bg_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.circle(bg_surf, (*deep_blue, 200), (60, 60), 55)
    s.blit(bg_surf, (0, 0))
    
    # 星星散布
    import random
    random.seed(42)  # 固定种子保持一致
    for star in range(30):
        sx = random.randint(10, 110)
        sy = random.randint(10, 110)
        
        # 检查是否在圆内
        dist = math.sqrt((sx - 60) ** 2 + (sy - 60) ** 2)
        if dist < 52:
            star_brightness = int(150 + 100 * math.sin(t * 4 + star))
            star_size = 1 if random.random() > 0.3 else 2
            pygame.draw.circle(s, (star_brightness, star_brightness, 255), (sx, sy), star_size)
    
    # 星云带
    nebula_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for band in range(3):
        band_y = 40 + band * 15 + int(5 * math.sin(t * 2 + band))
        pygame.draw.ellipse(nebula_surf, (100, 80, 200, 60), (20, band_y, 80, 20))
    s.blit(nebula_surf, (0, 0))
    
    # 中心星系核心
    pygame.draw.circle(s, star_blue, (60, 60), 18)
    pygame.draw.circle(s, white, (60, 60), 12)
    
    # 旋臂
    for arm in range(4):
        arm_angle = (arm * 90 + t * 20) * 0.01745
        for seg in range(8):
            seg_r = 15 + seg * 5
            seg_angle = arm_angle + seg * 0.15
            sx = 60 + math.cos(seg_angle) * seg_r
            sy = 60 + math.sin(seg_angle) * seg_r
            seg_alpha = 255 - seg * 25
            seg_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(seg_surf, (*star_blue, seg_alpha), (int(sx), int(sy)), 3)
            s.blit(seg_surf, (0, 0))


def _render_genesis_solar(s, t, pulse):
    """太阳诞生 - 金红炽焰主题"""
    solar_gold = (255, 200, 50)
    solar_orange = (255, 150, 0)
    solar_red = (255, 80, 0)
    white = (255, 255, 255)
    
    # 日冕层
    for corona in range(4):
        corona_r = 45 - corona * 8
        corona_alpha = 100 - corona * 20
        corona_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(corona_surf, (*solar_orange, corona_alpha), (60, 60), corona_r)
        s.blit(corona_surf, (0, 0))
    
    # 太阳耀斑
    for flare in range(12):
        flare_angle = (flare * 30 + t * 25) * 0.01745
        flare_len = 35 + int(15 * abs(math.sin(t * 5 + flare)))
        
        fx = 60 + math.cos(flare_angle) * flare_len
        fy = 60 + math.sin(flare_angle) * flare_len
        
        # 耀斑三角
        flare_width = 8
        perp_angle = flare_angle + math.pi / 2
        base1_x = 60 + math.cos(perp_angle) * flare_width / 2
        base1_y = 60 + math.sin(perp_angle) * flare_width / 2
        base2_x = 60 - math.cos(perp_angle) * flare_width / 2
        base2_y = 60 - math.sin(perp_angle) * flare_width / 2
        
        flare_color = solar_gold if flare % 2 == 0 else solar_red
        pygame.draw.polygon(s, flare_color, [
            (int(base1_x), int(base1_y)),
            (int(base2_x), int(base2_y)),
            (int(fx), int(fy))
        ])
    
    # 太阳核心
    pygame.draw.circle(s, solar_gold, (60, 60), 20)
    pygame.draw.circle(s, white, (60, 60), 14)
    
    # 核心脉动
    pulse_r = int(10 + 4 * pulse)
    pygame.draw.circle(s, solar_orange, (60, 60), pulse_r)


def _render_genesis_nebula(s, t, pulse):
    """星云孕育 - 紫粉梦幻主题"""
    nebula_purple = (180, 100, 255)
    nebula_pink = (255, 150, 200)
    nebula_blue = (150, 180, 255)
    white = (255, 255, 255)
    
    # 多层星云
    for layer in range(5):
        layer_offset = t * 10 * (1 if layer % 2 == 0 else -1)
        
        nebula_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 不规则形状（用多个椭圆叠加）
        for blob in range(4):
            blob_x = 60 + math.cos((layer + blob) * 1.5 + layer_offset * 0.01) * 20
            blob_y = 60 + math.sin((layer + blob) * 1.5 + layer_offset * 0.01) * 15
            blob_w = 40 + layer * 5
            blob_h = 30 + layer * 3
            
            colors = [nebula_purple, nebula_pink, nebula_blue]
            blob_color = colors[(layer + blob) % 3]
            blob_alpha = 60 - layer * 10
            
            pygame.draw.ellipse(nebula_surf, (*blob_color, blob_alpha),
                              (int(blob_x - blob_w/2), int(blob_y - blob_h/2), blob_w, blob_h))
        
        s.blit(nebula_surf, (0, 0))
    
    # 新星诞生点
    for star_birth in range(6):
        sb_angle = (star_birth * 60 + t * 15) * 0.01745
        sb_r = 30 + int(10 * math.sin(t * 3 + star_birth))
        sbx = 60 + math.cos(sb_angle) * sb_r
        sby = 60 + math.sin(sb_angle) * sb_r
        
        # 新星光芒
        pygame.draw.circle(s, nebula_pink, (int(sbx), int(sby)), 6)
        pygame.draw.circle(s, white, (int(sbx), int(sby)), 3)
    
    # 中心原恒星
    pygame.draw.circle(s, nebula_purple, (60, 60), 15)
    pygame.draw.circle(s, nebula_pink, (60, 60), 10)
    pygame.draw.circle(s, white, (60, 60), 5)


def _render_genesis_void(s, t, pulse):
    """虚无创生 - 黑白对立主题"""
    pure_white = (255, 255, 255)
    pure_black = (0, 0, 0)
    gray = (128, 128, 128)
    
    # 太极阴阳结构
    # 外圆
    pygame.draw.circle(s, gray, (60, 60), 45, 2)
    
    # 阴阳分割
    rotation = t * 30
    rot_rad = rotation * 0.01745
    
    # 白色半圆
    white_points = [(60, 60)]
    for i in range(181):
        angle = (i + rotation) * 0.01745
        x = 60 + math.cos(angle) * 42
        y = 60 + math.sin(angle) * 42
        white_points.append((int(x), int(y)))
    if len(white_points) > 2:
        pygame.draw.polygon(s, pure_white, white_points)
    
    # 黑色半圆
    black_points = [(60, 60)]
    for i in range(181):
        angle = (i + 180 + rotation) * 0.01745
        x = 60 + math.cos(angle) * 42
        y = 60 + math.sin(angle) * 42
        black_points.append((int(x), int(y)))
    if len(black_points) > 2:
        pygame.draw.polygon(s, pure_black, black_points)
    
    # 小圆（鱼眼）
    white_eye_angle = (90 + rotation) * 0.01745
    black_eye_angle = (270 + rotation) * 0.01745
    
    white_eye_x = 60 + math.cos(white_eye_angle) * 21
    white_eye_y = 60 + math.sin(white_eye_angle) * 21
    black_eye_x = 60 + math.cos(black_eye_angle) * 21
    black_eye_y = 60 + math.sin(black_eye_angle) * 21
    
    # 白中黑点
    pygame.draw.circle(s, pure_white, (int(white_eye_x), int(white_eye_y)), 12)
    pygame.draw.circle(s, pure_black, (int(white_eye_x), int(white_eye_y)), 5)
    
    # 黑中白点
    pygame.draw.circle(s, pure_black, (int(black_eye_x), int(black_eye_y)), 12)
    pygame.draw.circle(s, pure_white, (int(black_eye_x), int(black_eye_y)), 5)
    
    # 边界光环
    pygame.draw.circle(s, gray, (60, 60), 45, 3)
    
    # 平衡粒子
    for p in range(8):
        p_angle = (p * 45 + t * 20) * 0.01745
        p_r = 50
        px = 60 + math.cos(p_angle) * p_r
        py = 60 + math.sin(p_angle) * p_r
        p_color = pure_white if p % 2 == 0 else pure_black
        pygame.draw.circle(s, p_color, (int(px), int(py)), 3)
        pygame.draw.circle(s, gray, (int(px), int(py)), 3, 1)


def _render_genesis_life(s, t, pulse):
    """生命之源 - 翠绿金辉主题"""
    life_green = (50, 200, 100)
    gold = (255, 215, 100)
    white = (255, 255, 255)
    
    # DNA 双螺旋
    for helix in range(2):
        helix_offset = helix * math.pi
        
        for i in range(20):
            progress = i / 20
            angle = progress * math.pi * 4 + t * 3 + helix_offset
            x = 60 + math.cos(angle) * 15
            y = 20 + progress * 80
            
            # 螺旋点
            helix_color = life_green if helix == 0 else gold
            pygame.draw.circle(s, helix_color, (int(x), int(y)), 3)
            
            # 碱基对连接（每隔几个点）
            if i % 3 == 0 and helix == 0:
                other_x = 60 + math.cos(angle + math.pi) * 15
                pygame.draw.line(s, white, (int(x), int(y)), (int(other_x), int(y)), 1)
    
    # 生命能量球
    for orb in range(6):
        orb_angle = (orb * 60 + t * 25) * 0.01745
        orb_r = 45
        ox = 60 + math.cos(orb_angle) * orb_r
        oy = 60 + math.sin(orb_angle) * orb_r
        
        orb_color = life_green if orb % 2 == 0 else gold
        pygame.draw.circle(s, orb_color, (int(ox), int(oy)), 5)
        pygame.draw.circle(s, white, (int(ox), int(oy)), 3)
    
    # 中心生命核心
    core_pulse = int(15 + 5 * pulse)
    pygame.draw.circle(s, life_green, (60, 60), core_pulse)
    pygame.draw.circle(s, gold, (60, 60), core_pulse - 5)
    pygame.draw.circle(s, white, (60, 60), 6)


def _render_genesis_crystal(s, t, pulse):
    """水晶世界 - 冰蓝透明主题"""
    crystal_blue = (150, 220, 255)
    ice_white = (220, 240, 255)
    deep_blue = (80, 150, 220)
    
    # 水晶结构
    # 主晶体（六边形）
    hex_points = []
    for i in range(6):
        angle = (i * 60 + 30) * 0.01745
        r = 35
        hx = 60 + math.cos(angle) * r
        hy = 60 + math.sin(angle) * r
        hex_points.append((int(hx), int(hy)))
    
    # 晶体填充（半透明）
    hex_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.polygon(hex_surf, (*crystal_blue, 150), hex_points)
    s.blit(hex_surf, (0, 0))
    
    # 晶体边缘
    pygame.draw.polygon(s, ice_white, hex_points, 2)
    
    # 内部折射线
    for i in range(6):
        pygame.draw.line(s, (*ice_white, 100), (60, 60), hex_points[i], 1)
    
    # 小晶体碎片
    for frag in range(8):
        frag_angle = (frag * 45 + t * 15) * 0.01745
        frag_r = 45 + int(5 * math.sin(t * 4 + frag))
        fx = 60 + math.cos(frag_angle) * frag_r
        fy = 60 + math.sin(frag_angle) * frag_r
        
        # 小六边形
        small_hex = []
        for i in range(6):
            sh_angle = (i * 60 + t * 30) * 0.01745
            sh_r = 6
            shx = fx + math.cos(sh_angle) * sh_r
            shy = fy + math.sin(sh_angle) * sh_r
            small_hex.append((int(shx), int(shy)))
        
        frag_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(frag_surf, (*crystal_blue, 180), small_hex)
        pygame.draw.polygon(frag_surf, ice_white, small_hex, 1)
        s.blit(frag_surf, (0, 0))
    
    # 中心晶核
    pygame.draw.circle(s, deep_blue, (60, 60), 12)
    pygame.draw.circle(s, crystal_blue, (60, 60), 8)
    pygame.draw.circle(s, ice_white, (60, 60), 4)


def _render_genesis_chaos(s, t, pulse):
    """混沌原初 - 多彩混乱主题"""
    # 混沌色彩
    chaos_colors = [
        (255, 50, 50),
        (255, 150, 50),
        (255, 255, 50),
        (50, 255, 50),
        (50, 255, 255),
        (50, 50, 255),
        (255, 50, 255),
    ]
    
    # 混沌漩涡
    for ring in range(7):
        ring_r = 50 - ring * 6
        ring_rot = t * (40 + ring * 10) * (1 if ring % 2 == 0 else -1)
        
        ring_color = chaos_colors[ring]
        
        # 不规则环
        chaos_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        for seg in range(36):
            seg_angle = (seg * 10 + ring_rot) * 0.01745
            seg_r = ring_r + int(5 * math.sin(t * 8 + seg + ring))
            sx = 60 + math.cos(seg_angle) * seg_r
            sy = 60 + math.sin(seg_angle) * seg_r
            pygame.draw.circle(chaos_surf, (*ring_color, 150), (int(sx), int(sy)), 3)
        s.blit(chaos_surf, (0, 0))
    
    # 混沌能量爆发
    for burst in range(12):
        burst_angle = (burst * 30 + t * 50) * 0.01745
        burst_len = 30 + int(20 * abs(math.sin(t * 6 + burst)))
        bx = 60 + math.cos(burst_angle) * burst_len
        by = 60 + math.sin(burst_angle) * burst_len
        
        burst_color = chaos_colors[burst % 7]
        pygame.draw.line(s, burst_color, (60, 60), (int(bx), int(by)), 2)
    
    # 混沌核心
    core_color_idx = int(t * 5) % 7
    pygame.draw.circle(s, chaos_colors[core_color_idx], (60, 60), 15)
    pygame.draw.circle(s, chaos_colors[(core_color_idx + 3) % 7], (60, 60), 10)
    pygame.draw.circle(s, (255, 255, 255), (60, 60), 5)


def _render_genesis_ex(s, t, pulse, style):
    """EX 改装系列"""
    # 根据 EX 等级确定颜色
    ex_colors = {
        "genesis_ex": ((255, 220, 180), (255, 180, 120)),    # 铜金
        "genesis_ex2": ((220, 220, 240), (180, 180, 220)),   # 银辉
        "genesis_ex3": ((255, 240, 150), (255, 200, 80)),    # 金耀
        "genesis_ex4": ((255, 150, 220), (220, 100, 180)),   # 玫瑰
        "genesis_ex5": ((255, 255, 255), (255, 240, 220)),   # 神圣
    }
    
    main_color, accent = ex_colors.get(style, ((255, 255, 255), (200, 200, 200)))
    
    # EX 创世框架
    # 八芒星
    for i in range(8):
        angle = (i * 45 + t * 12) * 0.01745
        outer_r = 48
        inner_r = 25
        
        # 外点
        ox = 60 + math.cos(angle) * outer_r
        oy = 60 + math.sin(angle) * outer_r
        
        # 内点（偏移）
        inner_angle = ((i + 0.5) * 45 + t * 12) * 0.01745
        ix = 60 + math.cos(inner_angle) * inner_r
        iy = 60 + math.sin(inner_angle) * inner_r
        
        pygame.draw.line(s, main_color, (int(ox), int(oy)), (int(ix), int(iy)), 2)
        pygame.draw.circle(s, accent, (int(ox), int(oy)), 4)
    
    # 内部旋转环
    for ring in range(2):
        ring_r = 20 + ring * 10
        ring_rot = t * (25 + ring * 15) * (1 if ring % 2 == 0 else -1)
        pygame.draw.circle(s, main_color, (60, 60), ring_r, 2)
        
        # 环上粒子
        for p in range(4):
            p_angle = (p * 90 + ring_rot) * 0.01745
            px = 60 + math.cos(p_angle) * ring_r
            py = 60 + math.sin(p_angle) * ring_r
            pygame.draw.circle(s, accent, (int(px), int(py)), 3)
    
    # 中心 EX 核心
    pygame.draw.circle(s, main_color, (60, 60), 14)
    pygame.draw.circle(s, accent, (60, 60), 9)
    pygame.draw.circle(s, (255, 255, 255), (60, 60), 4)
    
    # EX 等级能量
    ex_level = style.replace("genesis_ex", "")
    level_num = int(ex_level) if ex_level.isdigit() else 1
    
    # 外围能量环（等级越高环越多）
    for ring in range(level_num):
        ring_r = 52 + ring * 4
        ring_alpha = 200 - ring * 30
        ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (*main_color, ring_alpha), (60, 60), ring_r, 1)
        s.blit(ring_surf, (0, 0))


__all__ = ['render_genesis_skin', 'is_genesis_style', 'GENESIS_STYLES']
