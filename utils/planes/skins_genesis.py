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
    "genesis_phoenix",     # 涅槃凤凰 - 浴火重生
    "genesis_ocean",       # 深渊海神 - 海洋漩涡
    "genesis_sakura",      # 樱吹雪 - 日式樱花
    "genesis_mecha",       # 机神降临 - 机甲变形
    "genesis_constellation",  # 星座守护 - 十二星座
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
    elif model_style == "genesis_phoenix":
        _render_genesis_phoenix(s, t, pulse)
    elif model_style == "genesis_ocean":
        _render_genesis_ocean(s, t, pulse)
    elif model_style == "genesis_sakura":
        _render_genesis_sakura(s, t, pulse)
    elif model_style == "genesis_mecha":
        _render_genesis_mecha(s, t, pulse)
    elif model_style == "genesis_constellation":
        _render_genesis_constellation(s, t, pulse)
    else:
        _render_genesis_base(s, t, pulse)
    
    return s


def _render_genesis_base(s, t, pulse):
    """创世之翼基础渲染 - 多边形翼与星云核心"""
    gold = (255, 195, 90)
    star_white = (255, 255, 255)
    nebula = (180, 120, 220)

    # 宇宙扩散环（多边形）
    for ring in range(5):
        sides = 8 + ring * 2
        r = 18 + ring * 9 + 4 * math.sin(t * 3 - ring * 0.6)
        pts = []
        rot = t * (15 - ring * 3)
        for i in range(sides):
            ang = (i * 360 / sides + rot) * 0.01745
            x = 60 + math.cos(ang) * r
            y = 55 + math.sin(ang) * r * 0.85
            pts.append((int(x), int(y)))
        color_r = 255 - ring * 18
        color_g = 195 - ring * 25
        color_b = 90 + ring * 20
        pygame.draw.polygon(s, (color_r, color_g, color_b, 180 - ring * 30), pts, 2)

    # 双翼（多层梯形羽片）
    for side in [-1, 1]:
        base_x = 60 + side * 14
        for f in range(5):
            f_ang = side * (25 + f * 14 + math.sin(t * 2.5 + f) * 6) * 0.01745
            length = 28 + f * 8
            tip_x = base_x + math.cos(f_ang) * length * side
            tip_y = 50 - math.sin(abs(f_ang)) * length * 0.45
            w = 6 - f * 0.8
            feather = [
                (base_x, 50 - w),
                (base_x, 50 + w),
                (tip_x, tip_y + w * 0.3),
                (tip_x, tip_y - w * 0.3),
            ]
            alpha = 220 - f * 35
            f_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(f_surf, (*gold, alpha), feather)
            pygame.draw.polygon(f_surf, (*star_white, alpha), feather, 1)
            s.blit(f_surf, (0, 0))

    # 中心八边核心
    core = []
    for i in range(8):
        ang = (i * 45 + t * 22) * 0.01745
        r = 18 + 3 * math.sin(t * 4 + i)
        x = 60 + math.cos(ang) * r
        y = 55 + math.sin(ang) * r
        core.append((int(x), int(y)))
    pygame.draw.polygon(s, gold, core)
    pygame.draw.polygon(s, star_white, core, 2)

    # 内层菱形
    inner = [(60, 45), (70, 55), (60, 65), (50, 55)]
    pygame.draw.polygon(s, star_white, inner)
    pygame.draw.polygon(s, nebula, inner, 2)

    # 轨道碎片（菱形行星）
    planet_colors = [
        (255, 110, 110), (255, 190, 100), (190, 255, 110), (110, 255, 190),
        (110, 190, 255), (160, 110, 255), (255, 110, 190), (255, 255, 110)
    ]
    for i in range(8):
        ang = (i * 45 + t * 38) * 0.01745
        r = 40 + 4 * math.sin(t * 5 + i)
        cx = 60 + math.cos(ang) * r
        cy = 55 + math.sin(ang) * r * 0.6
        shard = [(cx, cy - 5), (cx + 4, cy), (cx, cy + 5), (cx - 4, cy)]
        pygame.draw.polygon(s, planet_colors[i], shard)

    # 尾部能量条（梯形）
    for trail in range(4):
        ty = 72 + trail * 10
        w = 18 - trail * 4
        h = 5
        ribbon = [(60 - w, ty), (60 + w, ty), (60 + w - 2, ty + h), (60 - w + 2, ty + h)]
        alpha = 180 - trail * 40
        t_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(t_surf, (*gold, alpha), ribbon)
        s.blit(t_surf, (0, 0))


def _render_genesis_cosmic(s, t, pulse):
    """宇宙起源 - 星空深蓝主题，旋臂星系与星团"""
    deep_blue = (15, 35, 90)
    star_blue = (90, 140, 255)
    white = (255, 255, 255)
    purple = (120, 80, 200)

    # 深空背景（十二边形）
    bg = []
    for i in range(12):
        ang = (i * 30) * 0.01745
        r = 54
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        bg.append((int(x), int(y)))
    bg_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.polygon(bg_surf, (*deep_blue, 200), bg)
    s.blit(bg_surf, (0, 0))

    # 四条旋臂（曲线多边形）
    for arm in range(4):
        arm_pts = []
        base_ang = arm * 90 + t * 18
        for seg in range(12):
            progress = seg / 11
            ang = (base_ang + progress * 120) * 0.01745
            r = 12 + progress * 42
            x = 60 + math.cos(ang) * r
            y = 60 + math.sin(ang) * r
            arm_pts.append((int(x), int(y)))
        # 另一侧
        for seg in range(11, -1, -1):
            progress = seg / 11
            ang = (base_ang + progress * 120 + 8) * 0.01745
            r = 10 + progress * 38
            x = 60 + math.cos(ang) * r
            y = 60 + math.sin(ang) * r
            arm_pts.append((int(x), int(y)))
        color = star_blue if arm % 2 == 0 else purple
        arm_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(arm_surf, (*color, 100), arm_pts)
        s.blit(arm_surf, (0, 0))

    # 星团碎片（小三角/菱形）
    import random
    random.seed(42)
    for star in range(25):
        sx = random.randint(15, 105)
        sy = random.randint(15, 105)
        dist = math.sqrt((sx - 60) ** 2 + (sy - 60) ** 2)
        if dist < 50:
            brightness = int(150 + 100 * math.sin(t * 4 + star))
            size = 2 + (star % 3)
            shard = [(sx, sy - size), (sx + size, sy), (sx, sy + size), (sx - size, sy)]
            pygame.draw.polygon(s, (brightness, brightness, 255), shard)

    # 中心星系核（十边形）
    core = []
    for i in range(10):
        ang = (i * 36 + t * 25) * 0.01745
        r = 16 + 3 * math.sin(t * 5 + i)
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        core.append((int(x), int(y)))
    pygame.draw.polygon(s, star_blue, core)
    pygame.draw.polygon(s, white, core, 2)
    # 内菱
    inner = [(60, 52), (68, 60), (60, 68), (52, 60)]
    pygame.draw.polygon(s, white, inner)


def _render_genesis_solar(s, t, pulse):
    """太阳诞生 - 金红炽焰主题，火焰刃与多边形日冕"""
    gold = (255, 195, 50)
    orange = (255, 140, 20)
    crimson = (255, 70, 20)
    white = (255, 255, 255)

    # 多层日冕（不规则多边形）
    for corona in range(4):
        pts = []
        sides = 16 - corona * 2
        r = 50 - corona * 10
        rot = t * (12 + corona * 5) * (1 if corona % 2 == 0 else -1)
        for i in range(sides):
            ang = (i * 360 / sides + rot) * 0.01745
            rad = r + 6 * math.sin(t * 5 + i + corona)
            x = 60 + math.cos(ang) * rad
            y = 60 + math.sin(ang) * rad
            pts.append((int(x), int(y)))
        alpha = 120 - corona * 25
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (*orange, alpha), pts)
        s.blit(surf, (0, 0))

    # 十二条耀斑刃（梯形三角）
    for i in range(12):
        ang = (i * 30 + t * 28) * 0.01745
        length = 38 + 14 * abs(math.sin(t * 5 + i))
        w = 7
        tip = (60 + math.cos(ang) * length, 60 + math.sin(ang) * length)
        left = (60 + math.cos(ang + 0.25) * 18, 60 + math.sin(ang + 0.25) * 18)
        right = (60 + math.cos(ang - 0.25) * 18, 60 + math.sin(ang - 0.25) * 18)
        mid_l = (60 + math.cos(ang + 0.12) * (length * 0.6), 60 + math.sin(ang + 0.12) * (length * 0.6))
        mid_r = (60 + math.cos(ang - 0.12) * (length * 0.6), 60 + math.sin(ang - 0.12) * (length * 0.6))
        blade = [left, mid_l, tip, mid_r, right]
        color = gold if i % 2 == 0 else crimson
        pygame.draw.polygon(s, color, blade)
        pygame.draw.polygon(s, orange, blade, 1)

    # 中心太阳核（十边形）
    core = []
    for i in range(10):
        ang = (i * 36 + t * 20) * 0.01745
        r = 18 + 3 * math.sin(t * 4 + i)
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        core.append((int(x), int(y)))
    pygame.draw.polygon(s, gold, core)
    pygame.draw.polygon(s, white, core, 2)
    # 内六边
    inner = []
    for i in range(6):
        ang = (i * 60 + t * 25) * 0.01745
        x = 60 + math.cos(ang) * 10
        y = 60 + math.sin(ang) * 10
        inner.append((int(x), int(y)))
    pygame.draw.polygon(s, white, inner)
    # 核心菱形
    diamond = [(60, 54), (66, 60), (60, 66), (54, 60)]
    pygame.draw.polygon(s, orange, diamond)


def _render_genesis_nebula(s, t, pulse):
    """星云孕育 - 紫粉梦幻主题，多边形云层与星光碎片"""
    purple = (170, 90, 255)
    pink = (255, 140, 200)
    blue = (140, 170, 255)
    white = (255, 255, 255)

    # 多层星云（不规则多边形）
    for layer in range(5):
        offset = t * 8 * (1 if layer % 2 == 0 else -1)
        pts = []
        sides = 10 + layer * 2
        for i in range(sides):
            ang = (i * 360 / sides + offset + layer * 20) * 0.01745
            r = 25 + layer * 8 + 10 * math.sin(t * 2.5 + i * 0.5 + layer)
            x = 60 + math.cos(ang) * r
            y = 60 + math.sin(ang) * r * 0.8
            pts.append((int(x), int(y)))
        colors = [purple, pink, blue]
        color = colors[layer % 3]
        alpha = 70 - layer * 12
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (*color, alpha), pts)
        s.blit(surf, (0, 0))

    # 新星诞生点（菱形星光）
    for i in range(8):
        ang = (i * 45 + t * 18) * 0.01745
        r = 35 + 12 * math.sin(t * 3.5 + i)
        cx = 60 + math.cos(ang) * r
        cy = 60 + math.sin(ang) * r
        # 四角星形
        star = [
            (cx, cy - 8),
            (cx + 3, cy - 3),
            (cx + 8, cy),
            (cx + 3, cy + 3),
            (cx, cy + 8),
            (cx - 3, cy + 3),
            (cx - 8, cy),
            (cx - 3, cy - 3),
        ]
        color = pink if i % 2 == 0 else purple
        pygame.draw.polygon(s, color, star)
        pygame.draw.polygon(s, white, star, 1)

    # 中心原恒星（十二边形）
    core = []
    for i in range(12):
        ang = (i * 30 + t * 22) * 0.01745
        r = 14 + 3 * math.sin(t * 4 + i)
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        core.append((int(x), int(y)))
    pygame.draw.polygon(s, purple, core)
    pygame.draw.polygon(s, pink, core, 2)
    # 内六边
    inner = []
    for i in range(6):
        ang = (i * 60 + t * 28) * 0.01745
        x = 60 + math.cos(ang) * 8
        y = 60 + math.sin(ang) * 8
        inner.append((int(x), int(y)))
    pygame.draw.polygon(s, white, inner)


def _render_genesis_void(s, t, pulse):
    """虚无创生 - 黑白对立主题，多边形太极与平衡碎片"""
    white = (255, 255, 255)
    black = (10, 10, 10)
    gray = (128, 128, 128)

    # 外层十二边形边框
    outer = []
    for i in range(12):
        ang = (i * 30 + t * 15) * 0.01745
        r = 48
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        outer.append((int(x), int(y)))
    pygame.draw.polygon(s, gray, outer, 2)

    # 旋转太极（用多边形构建半圆）
    rot = t * 25
    # 白色半圆多边形
    white_half = [(60, 60)]
    for i in range(19):
        ang = (i * 10 + rot) * 0.01745
        x = 60 + math.cos(ang) * 42
        y = 60 + math.sin(ang) * 42
        white_half.append((int(x), int(y)))
    pygame.draw.polygon(s, white, white_half)
    # 黑色半圆多边形
    black_half = [(60, 60)]
    for i in range(19):
        ang = (i * 10 + 180 + rot) * 0.01745
        x = 60 + math.cos(ang) * 42
        y = 60 + math.sin(ang) * 42
        black_half.append((int(x), int(y)))
    pygame.draw.polygon(s, black, black_half)

    # 鱼眼（六边形）
    white_eye_ang = (90 + rot) * 0.01745
    black_eye_ang = (270 + rot) * 0.01745
    wx = 60 + math.cos(white_eye_ang) * 21
    wy = 60 + math.sin(white_eye_ang) * 21
    bx = 60 + math.cos(black_eye_ang) * 21
    by = 60 + math.sin(black_eye_ang) * 21
    # 白中黑点
    w_hex = []
    for i in range(6):
        ang = (i * 60) * 0.01745
        w_hex.append((int(wx + math.cos(ang) * 10), int(wy + math.sin(ang) * 10)))
    pygame.draw.polygon(s, white, w_hex)
    w_inner = [(wx, wy - 4), (wx + 4, wy), (wx, wy + 4), (wx - 4, wy)]
    pygame.draw.polygon(s, black, w_inner)
    # 黑中白点
    b_hex = []
    for i in range(6):
        ang = (i * 60) * 0.01745
        b_hex.append((int(bx + math.cos(ang) * 10), int(by + math.sin(ang) * 10)))
    pygame.draw.polygon(s, black, b_hex)
    b_inner = [(bx, by - 4), (bx + 4, by), (bx, by + 4), (bx - 4, by)]
    pygame.draw.polygon(s, white, b_inner)

    # 平衡碎片（菱形）
    for i in range(8):
        ang = (i * 45 + t * 22) * 0.01745
        r = 52
        cx = 60 + math.cos(ang) * r
        cy = 60 + math.sin(ang) * r
        color = white if i % 2 == 0 else black
        shard = [(cx, cy - 5), (cx + 4, cy), (cx, cy + 5), (cx - 4, cy)]
        pygame.draw.polygon(s, color, shard)
        pygame.draw.polygon(s, gray, shard, 1)


def _render_genesis_life(s, t, pulse):
    """生命之源 - 翠绿金辉主题，DNA螺旋与生命能量碎片"""
    green = (50, 195, 100)
    gold = (255, 210, 90)
    white = (255, 255, 255)

    # DNA 双螺旋（多边形节点）
    for helix in range(2):
        offset = helix * math.pi
        prev_pt = None
        for i in range(18):
            progress = i / 17
            ang = progress * math.pi * 3.5 + t * 2.8 + offset
            x = 60 + math.cos(ang) * 16
            y = 18 + progress * 84
            # 螺旋节点（菱形）
            node = [(x, y - 4), (x + 3, y), (x, y + 4), (x - 3, y)]
            color = green if helix == 0 else gold
            pygame.draw.polygon(s, color, node)
            # 连接线
            if prev_pt:
                pygame.draw.line(s, color, prev_pt, (x, y), 2)
            prev_pt = (x, y)
            # 碱基对连接（折线）
            if i % 3 == 0 and helix == 0:
                other_x = 60 + math.cos(ang + math.pi) * 16
                mid_x = 60
                pygame.draw.lines(s, white, False, [(x, y), (mid_x, y), (other_x, y)], 1)

    # 生命能量环（菱形碎片）
    for i in range(10):
        ang = (i * 36 + t * 28) * 0.01745
        r = 48 + 5 * math.sin(t * 4 + i)
        cx = 60 + math.cos(ang) * r
        cy = 60 + math.sin(ang) * r
        shard = [(cx, cy - 6), (cx + 5, cy), (cx, cy + 6), (cx - 5, cy)]
        color = green if i % 2 == 0 else gold
        pygame.draw.polygon(s, color, shard)
        pygame.draw.polygon(s, white, shard, 1)

    # 中心生命核（十边形）
    core = []
    for i in range(10):
        ang = (i * 36 + t * 20) * 0.01745
        r = 14 + 4 * pulse
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        core.append((int(x), int(y)))
    pygame.draw.polygon(s, green, core)
    pygame.draw.polygon(s, gold, core, 2)
    # 内菱
    inner = [(60, 52), (68, 60), (60, 68), (52, 60)]
    pygame.draw.polygon(s, white, inner)


def _render_genesis_crystal(s, t, pulse):
    """水晶世界 - 冰蓝透明主题，多层水晶棱面"""
    ice = (140, 215, 255)
    frost = (215, 235, 255)
    deep = (70, 145, 220)

    # 主晶体（十二边形）
    main_crystal = []
    for i in range(12):
        ang = (i * 30 + 15 + t * 8) * 0.01745
        r = 38 + 4 * math.sin(t * 3 + i)
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        main_crystal.append((int(x), int(y)))
    surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (*ice, 160), main_crystal)
    s.blit(surf, (0, 0))
    pygame.draw.polygon(s, frost, main_crystal, 2)

    # 内部折射线（三角分割）
    for i in range(6):
        pygame.draw.line(s, (*frost, 120), (60, 60), main_crystal[i * 2], 1)

    # 外围水晶碎片（六边形）
    for i in range(8):
        ang = (i * 45 + t * 15) * 0.01745
        r = 50 + 6 * math.sin(t * 4 + i)
        cx = 60 + math.cos(ang) * r
        cy = 60 + math.sin(ang) * r
        shard = []
        for j in range(6):
            s_ang = (j * 60 + t * 25) * 0.01745
            s_r = 7
            sx = cx + math.cos(s_ang) * s_r
            sy = cy + math.sin(s_ang) * s_r
            shard.append((int(sx), int(sy)))
        shard_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(shard_surf, (*ice, 180), shard)
        pygame.draw.polygon(shard_surf, frost, shard, 1)
        s.blit(shard_surf, (0, 0))

    # 中心晶核（八边形）
    core = []
    for i in range(8):
        ang = (i * 45 + t * 18) * 0.01745
        r = 12 + 2 * math.sin(t * 5 + i)
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        core.append((int(x), int(y)))
    pygame.draw.polygon(s, deep, core)
    pygame.draw.polygon(s, frost, core, 2)
    # 内菱
    inner = [(60, 54), (66, 60), (60, 66), (54, 60)]
    pygame.draw.polygon(s, frost, inner)


def _render_genesis_chaos(s, t, pulse):
    """混沌原初 - 多彩混乱主题，多边形漩涡与爆裂线"""
    chaos_colors = [
        (255, 55, 55),
        (255, 145, 55),
        (255, 245, 55),
        (55, 255, 55),
        (55, 255, 255),
        (55, 55, 255),
        (255, 55, 255),
    ]

    # 多层混沌漩涡（不规则多边形）
    for ring in range(7):
        r = 50 - ring * 6
        rot = t * (35 + ring * 8) * (1 if ring % 2 == 0 else -1)
        pts = []
        sides = 12 + ring
        for i in range(sides):
            ang = (i * 360 / sides + rot) * 0.01745
            rad = r + 6 * math.sin(t * 7 + i + ring * 2)
            x = 60 + math.cos(ang) * rad
            y = 60 + math.sin(ang) * rad
            pts.append((int(x), int(y)))
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (*chaos_colors[ring], 120), pts, 2)
        s.blit(surf, (0, 0))

    # 混沌爆裂线（三角尖刺）
    for i in range(14):
        ang = (i * (360 / 14) + t * 45) * 0.01745
        length = 32 + 22 * abs(math.sin(t * 6 + i))
        tip = (60 + math.cos(ang) * length, 60 + math.sin(ang) * length)
        left = (60 + math.cos(ang + 0.35) * 14, 60 + math.sin(ang + 0.35) * 14)
        right = (60 + math.cos(ang - 0.35) * 14, 60 + math.sin(ang - 0.35) * 14)
        pygame.draw.polygon(s, chaos_colors[i % 7], [left, tip, right])

    # 混沌核心（七边形）
    core = []
    color_idx = int(t * 4) % 7
    for i in range(7):
        ang = (i * (360 / 7) + t * 30) * 0.01745
        r = 14 + 3 * math.sin(t * 5 + i)
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        core.append((int(x), int(y)))
    pygame.draw.polygon(s, chaos_colors[color_idx], core)
    pygame.draw.polygon(s, chaos_colors[(color_idx + 3) % 7], core, 2)
    # 内菱
    inner = [(60, 52), (68, 60), (60, 68), (52, 60)]
    pygame.draw.polygon(s, (255, 255, 255), inner)


def _render_genesis_phoenix(s, t, pulse):
    """涅槃凤凰 - 浴火重生的火鸟"""
    flame_red = (255, 80, 30)
    flame_orange = (255, 160, 40)
    flame_yellow = (255, 230, 100)
    ash = (60, 40, 35)

    # 凤凰身体（中心椭圆形火焰）
    body = []
    for i in range(12):
        ang = (i * 30 + t * 15) * 0.01745
        rx = 18 + 4 * math.sin(t * 4 + i)
        ry = 12
        x = 60 + math.cos(ang) * rx
        y = 55 + math.sin(ang) * ry
        body.append((int(x), int(y)))
    pygame.draw.polygon(s, flame_orange, body)
    pygame.draw.polygon(s, flame_yellow, body, 2)

    # 双翼（火焰羽毛扇形展开）
    for side in [-1, 1]:
        for feather in range(7):
            ang = side * (25 + feather * 12 + 5 * math.sin(t * 3 + feather)) * 0.01745
            length = 20 + feather * 7
            tip_x = 60 + math.cos(ang) * length * side * 0.8
            tip_y = 50 - math.sin(abs(ang)) * length * 0.5
            base_l = (60 + side * 10, 52)
            base_r = (60 + side * 12, 58)
            colors = [flame_red, flame_orange, flame_yellow]
            pygame.draw.polygon(s, colors[feather % 3], [base_l, (tip_x, tip_y), base_r])

    # 凤凰尾羽（向下飘动的火焰）
    for tail in range(5):
        tail_x = 55 + tail * 3 + 4 * math.sin(t * 4 + tail)
        tail_pts = [
            (tail_x, 65),
            (tail_x + 4, 75 + tail * 6),
            (tail_x - 2, 85 + tail * 8 + 5 * math.sin(t * 3 + tail)),
            (tail_x - 5, 72 + tail * 5),
        ]
        color = flame_yellow if tail % 2 == 0 else flame_orange
        pygame.draw.polygon(s, color, tail_pts)

    # 凤首（三角头+冠羽）
    head = [(60, 35), (68, 45), (60, 48), (52, 45)]
    pygame.draw.polygon(s, flame_orange, head)
    # 冠羽
    for crown in range(3):
        cx = 58 + crown * 2
        crown_pts = [(cx, 35), (cx + 2, 22 + 4 * math.sin(t * 5 + crown)), (cx - 1, 32)]
        pygame.draw.polygon(s, flame_yellow, crown_pts)
    # 眼睛
    pygame.draw.polygon(s, ash, [(58, 40), (62, 42), (58, 44), (54, 42)])

    # 环绕火星
    for spark in range(10):
        ang = (spark * 36 + t * 45) * 0.01745
        r = 48 + 6 * math.sin(t * 5 + spark)
        sx = 60 + math.cos(ang) * r
        sy = 55 + math.sin(ang) * r
        spark_shape = [(sx, sy - 3), (sx + 2, sy), (sx, sy + 3), (sx - 2, sy)]
        pygame.draw.polygon(s, flame_yellow, spark_shape)


def _render_genesis_ocean(s, t, pulse):
    """深渊海神 - 海洋漩涡与波浪"""
    deep_blue = (20, 50, 120)
    sea_blue = (40, 120, 180)
    foam = (200, 230, 255)
    gold = (255, 200, 100)

    # 多层波浪环
    for wave_ring in range(4):
        pts = []
        sides = 24
        r_base = 50 - wave_ring * 10
        rot = t * (15 + wave_ring * 5) * (1 if wave_ring % 2 == 0 else -1)
        for i in range(sides):
            ang = (i * 360 / sides + rot) * 0.01745
            wave_h = 5 * math.sin(i * 3 + t * 6 + wave_ring)
            r = r_base + wave_h
            x = 60 + math.cos(ang) * r
            y = 60 + math.sin(ang) * r
            pts.append((int(x), int(y)))
        colors = [deep_blue, sea_blue, foam, sea_blue]
        alpha = 200 - wave_ring * 40
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (*colors[wave_ring], alpha), pts)
        s.blit(surf, (0, 0))

    # 海洋漩涡（螺旋臂）
    for arm in range(3):
        spiral_pts = []
        for seg in range(20):
            progress = seg / 19
            ang = (arm * 120 + progress * 540 + t * 40) * 0.01745
            r = 8 + progress * 35
            x = 60 + math.cos(ang) * r
            y = 60 + math.sin(ang) * r
            spiral_pts.append((int(x), int(y)))
        pygame.draw.lines(s, foam, False, spiral_pts, 2)

    # 海神三叉戟（中心）
    trident_base = (60, 70)
    trident_top = (60, 35)
    pygame.draw.line(s, gold, trident_base, trident_top, 3)
    # 三叉
    for prong in [-1, 0, 1]:
        px = 60 + prong * 10
        py = 30 + abs(prong) * 5
        tip = (px, py - 8 + 3 * math.sin(t * 3))
        pygame.draw.line(s, gold, (60, 38), tip, 2)
        # 叉尖
        prong_tip = [(px, py - 12), (px + 3, py - 5), (px - 3, py - 5)]
        pygame.draw.polygon(s, gold, prong_tip)

    # 水泡（小六边形）
    import random
    random.seed(88)
    for bubble in range(12):
        bx = random.randint(20, 100)
        by = random.randint(20, 100)
        br = 4 + (bubble % 3)
        bubble_pts = []
        for i in range(6):
            ang = (i * 60) * 0.01745
            x = bx + math.cos(ang) * br
            y = by + math.sin(ang) * br
            bubble_pts.append((int(x), int(y)))
        pygame.draw.polygon(s, foam, bubble_pts, 1)


def _render_genesis_sakura(s, t, pulse):
    """樱吹雪 - 飘散的樱花花瓣"""
    pink = (255, 180, 200)
    light_pink = (255, 220, 230)
    brown = (120, 80, 60)
    white = (255, 255, 255)

    # 樱花树枝（从左下向右上）
    branches = [
        [(20, 100), (40, 75), (55, 55)],
        [(40, 75), (60, 65), (80, 55)],
        [(55, 55), (65, 40), (70, 25)],
        [(55, 55), (45, 38), (35, 25)],
    ]
    for branch in branches:
        pygame.draw.lines(s, brown, False, branch, 3)

    # 樱花花朵（五瓣花）
    flower_positions = [(70, 25), (35, 25), (80, 55), (65, 40), (45, 38), (55, 55)]
    for idx, (fx, fy) in enumerate(flower_positions):
        # 五片花瓣
        for petal in range(5):
            petal_ang = (petal * 72 - 90 + t * 8 + idx * 30) * 0.01745
            petal_len = 8 + 2 * math.sin(t * 3 + idx + petal)
            px = fx + math.cos(petal_ang) * petal_len
            py = fy + math.sin(petal_ang) * petal_len
            petal_pts = [
                (fx, fy),
                (fx + math.cos(petal_ang + 0.4) * petal_len * 0.5, fy + math.sin(petal_ang + 0.4) * petal_len * 0.5),
                (px, py),
                (fx + math.cos(petal_ang - 0.4) * petal_len * 0.5, fy + math.sin(petal_ang - 0.4) * petal_len * 0.5),
            ]
            pygame.draw.polygon(s, pink if idx % 2 == 0 else light_pink, petal_pts)
        # 花心
        pygame.draw.polygon(s, (255, 230, 150), [(fx - 2, fy - 2), (fx + 2, fy - 2), (fx + 2, fy + 2), (fx - 2, fy + 2)])

    # 飘落的花瓣（散布）
    import random
    random.seed(99)
    for petal in range(15):
        base_x = random.randint(10, 110)
        base_y = random.randint(10, 110)
        # 花瓣位置随时间飘动
        px = (base_x + t * 15 + petal * 7) % 120
        py = (base_y + t * 20 + petal * 11) % 120
        rot = t * 100 + petal * 45
        # 椭圆形花瓣（用菱形近似）
        petal_pts = [
            (px, py - 4),
            (px + 3, py),
            (px, py + 4),
            (px - 3, py),
        ]
        # 旋转花瓣
        cos_r = math.cos(rot * 0.01745)
        sin_r = math.sin(rot * 0.01745)
        rotated = []
        for (x, y) in petal_pts:
            dx, dy = x - px, y - py
            nx = px + dx * cos_r - dy * sin_r
            ny = py + dx * sin_r + dy * cos_r
            rotated.append((nx, ny))
        color = pink if petal % 3 == 0 else (light_pink if petal % 3 == 1 else white)
        pygame.draw.polygon(s, color, rotated)


def _render_genesis_mecha(s, t, pulse):
    """机神降临 - 变形机甲"""
    steel = (150, 160, 170)
    dark_steel = (80, 85, 95)
    red = (220, 50, 50)
    gold = (255, 200, 80)
    white = (255, 255, 255)

    # 机甲躯干（六边形核心）
    torso = []
    for i in range(6):
        ang = (i * 60 + 30 + t * 5) * 0.01745
        r = 18
        x = 60 + math.cos(ang) * r
        y = 55 + math.sin(ang) * r
        torso.append((int(x), int(y)))
    pygame.draw.polygon(s, steel, torso)
    pygame.draw.polygon(s, dark_steel, torso, 2)

    # 机甲头部（三角）
    head = [(60, 28), (70, 40), (50, 40)]
    pygame.draw.polygon(s, steel, head)
    pygame.draw.polygon(s, dark_steel, head, 2)
    # 眼睛（长条）
    pygame.draw.polygon(s, red, [(54, 34), (66, 34), (65, 37), (55, 37)])
    # 天线
    pygame.draw.line(s, gold, (60, 28), (60, 18 + 3 * math.sin(t * 4)), 2)

    # 双臂（可动关节）
    for side in [-1, 1]:
        # 肩甲
        shoulder_x = 60 + side * 28
        shoulder = [(shoulder_x - 8, 48), (shoulder_x + 8, 48), (shoulder_x + 6, 58), (shoulder_x - 6, 58)]
        pygame.draw.polygon(s, dark_steel, shoulder)
        pygame.draw.polygon(s, gold, shoulder, 1)
        
        # 手臂
        arm_ang = side * (30 + 15 * math.sin(t * 2)) * 0.01745
        elbow_x = shoulder_x + math.cos(arm_ang) * 15 * side
        elbow_y = 58 + abs(math.sin(arm_ang)) * 10
        pygame.draw.line(s, steel, (shoulder_x, 55), (elbow_x, elbow_y), 4)
        
        # 前臂
        hand_x = elbow_x + side * 12
        hand_y = elbow_y + 10
        pygame.draw.line(s, steel, (elbow_x, elbow_y), (hand_x, hand_y), 3)
        # 手部武器
        weapon = [(hand_x - 3, hand_y), (hand_x + 3, hand_y), (hand_x, hand_y + 8)]
        pygame.draw.polygon(s, red, weapon)

    # 双腿
    for side in [-1, 1]:
        leg_x = 60 + side * 10
        # 大腿
        pygame.draw.line(s, dark_steel, (leg_x, 70), (leg_x + side * 5, 85), 4)
        # 小腿
        pygame.draw.line(s, steel, (leg_x + side * 5, 85), (leg_x, 100), 3)
        # 脚部
        foot = [(leg_x - 5, 98), (leg_x + 5, 98), (leg_x + 8, 105), (leg_x - 8, 105)]
        pygame.draw.polygon(s, dark_steel, foot)

    # 背部推进器
    for side in [-1, 1]:
        thruster_x = 60 + side * 22
        thruster = [(thruster_x - 4, 45), (thruster_x + 4, 45), (thruster_x + 3, 65), (thruster_x - 3, 65)]
        pygame.draw.polygon(s, dark_steel, thruster)
        # 火焰
        flame_len = 10 + 6 * abs(math.sin(t * 8))
        flame = [(thruster_x, 65), (thruster_x - 4, 65 + flame_len), (thruster_x + 4, 65 + flame_len)]
        pygame.draw.polygon(s, gold, flame)

    # 胸口能量核心
    core = [(60, 50), (66, 55), (60, 62), (54, 55)]
    pygame.draw.polygon(s, red, core)
    pygame.draw.polygon(s, white, core, 1)


def _render_genesis_constellation(s, t, pulse):
    """星座守护 - 十二星座连线图"""
    night = (15, 20, 45)
    star_color = (255, 255, 220)
    line_color = (100, 150, 255)
    gold = (255, 200, 100)

    # 夜空背景（十二边形）
    bg = []
    for i in range(12):
        ang = (i * 30) * 0.01745
        x = 60 + math.cos(ang) * 55
        y = 60 + math.sin(ang) * 55
        bg.append((int(x), int(y)))
    pygame.draw.polygon(s, night, bg)

    # 十二星座符号位置（围成一圈）
    constellation_patterns = [
        # 白羊 - V形角
        [(-3, -5), (0, 0), (3, -5)],
        # 金牛 - 圆+角
        [(0, 3), (-4, -2), (4, -2), (0, 3)],
        # 双子 - II形
        [(-3, -4), (-3, 4), (3, -4), (3, 4)],
        # 巨蟹 - 69形
        [(-4, 0), (0, -4), (4, 0), (0, 4)],
        # 狮子 - 弧形
        [(-4, 4), (-4, -2), (0, -4), (4, -2)],
        # 处女 - M形
        [(-4, 4), (-2, -4), (0, 2), (2, -4), (4, 4)],
        # 天秤 - 秤形
        [(-5, 0), (5, 0), (0, -5), (0, 5)],
        # 天蝎 - M尾
        [(-4, -3), (-2, 3), (0, -3), (2, 3), (4, 0)],
        # 射手 - 箭形
        [(-4, 4), (4, -4), (0, 0), (4, 0), (0, -4)],
        # 摩羯 - V形
        [(-3, -4), (0, 4), (3, -4), (5, 0)],
        # 水瓶 - 波浪
        [(-4, -2), (-2, 2), (0, -2), (2, 2), (4, -2)],
        # 双鱼 - )(形
        [(-3, -4), (-5, 0), (-3, 4), (3, -4), (5, 0), (3, 4)],
    ]

    # 绘制十二星座
    for idx in range(12):
        ang = (idx * 30 - 90 + t * 5) * 0.01745
        cx = 60 + math.cos(ang) * 40
        cy = 60 + math.sin(ang) * 40
        
        pattern = constellation_patterns[idx]
        # 星点
        star_pts = [(cx + dx * 1.2, cy + dy * 1.2) for dx, dy in pattern]
        
        # 连线
        if len(star_pts) > 1:
            pygame.draw.lines(s, line_color, False, star_pts, 1)
        
        # 星点（小菱形）
        brightness = int(200 + 55 * math.sin(t * 3 + idx))
        for (sx, sy) in star_pts:
            star_shape = [(sx, sy - 2), (sx + 2, sy), (sx, sy + 2), (sx - 2, sy)]
            pygame.draw.polygon(s, (brightness, brightness, 220), star_shape)

    # 中心太阳/月亮交替
    phase = math.sin(t * 0.5)
    if phase > 0:
        # 太阳（八角星）
        sun = []
        for i in range(8):
            ang = (i * 45 + t * 20) * 0.01745
            r = 12 if i % 2 == 0 else 7
            x = 60 + math.cos(ang) * r
            y = 60 + math.sin(ang) * r
            sun.append((int(x), int(y)))
        pygame.draw.polygon(s, gold, sun)
    else:
        # 月亮（弯月多边形）
        moon = []
        for i in range(12):
            ang = (i * 30 - 90) * 0.01745
            r = 10
            x = 60 + math.cos(ang) * r
            y = 60 + math.sin(ang) * r
            moon.append((int(x), int(y)))
        pygame.draw.polygon(s, (220, 220, 200), moon)
        # 月亮阴影
        shadow = []
        for i in range(8):
            ang = (i * 45 + 45) * 0.01745
            r = 8
            x = 63 + math.cos(ang) * r
            y = 60 + math.sin(ang) * r
            shadow.append((int(x), int(y)))
        pygame.draw.polygon(s, night, shadow)

    # 外环星座边界
    pygame.draw.polygon(s, line_color, bg, 1)


__all__ = ['render_genesis_skin', 'is_genesis_style', 'GENESIS_STYLES']
