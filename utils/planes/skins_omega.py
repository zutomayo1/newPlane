# -*- coding: utf-8 -*-
"""
终极机体涂装 - Omega（终末神兵·奥米茄）

融合所有机体精华的终极形态，拥有七彩流光的神圣机械美学
"""
import pygame
import math

# Omega 涂装样式列表
OMEGA_STYLES = [
    "omega_divine",      # 神圣审判 - 金白圣光
    "omega_void",        # 虚空终末 - 深紫黑暗
    "omega_aurora",      # 极光流转 - 七彩极光
    "omega_celestial",   # 天界机神 - 蓝金神圣
    "omega_infernal",    # 地狱烈焰 - 红黑炼狱
    "omega_quantum",     # 量子形态 - 青蓝科技
    "omega_primal",      # 原始神力 - 翠绿自然
    "omega_clockwork",   # 永恒钟表 - 齿轮时钟机械
    "omega_dragon",      # 神龙之魂 - 东方龙鳞
    "omega_galactic",    # 银河霸主 - 星系漩涡
    "omega_runic",       # 符文铭刻 - 古代符文
    "omega_tempest",     # 风暴君王 - 雷电风暴
]


def is_omega_style(model_style):
    """检查是否为 Omega 涂装样式"""
    return model_style in OMEGA_STYLES


def render_omega_skin(s, c, model_style, t, pid, static):
    """渲染 Omega 专属涂装"""
    if not is_omega_style(model_style):
        return None
    
    pulse = 0 if static else abs(math.sin(t * 3))
    
    if model_style == "omega_divine":
        _render_omega_divine(s, t, pulse)
    elif model_style == "omega_void":
        _render_omega_void(s, t, pulse)
    elif model_style == "omega_aurora":
        _render_omega_aurora(s, t, pulse)
    elif model_style == "omega_celestial":
        _render_omega_celestial(s, t, pulse)
    elif model_style == "omega_infernal":
        _render_omega_infernal(s, t, pulse)
    elif model_style == "omega_quantum":
        _render_omega_quantum(s, t, pulse)
    elif model_style == "omega_primal":
        _render_omega_primal(s, t, pulse)
    elif model_style == "omega_clockwork":
        _render_omega_clockwork(s, t, pulse)
    elif model_style == "omega_dragon":
        _render_omega_dragon(s, t, pulse)
    elif model_style == "omega_galactic":
        _render_omega_galactic(s, t, pulse)
    elif model_style == "omega_runic":
        _render_omega_runic(s, t, pulse)
    elif model_style == "omega_tempest":
        _render_omega_tempest(s, t, pulse)
    else:
        _render_omega_base(s, t, pulse)
    
    return s


def _render_omega_base(s, t, pulse):
    """Omega 基础渲染 - 机械圣殿，七属性折射棱面"""
    colors = [
        (255, 112, 112),   # 红-火
        (255, 186, 96),    # 橙-雷
        (255, 231, 120),   # 黄-光
        (96, 214, 132),    # 绿-风
        (96, 214, 214),    # 青-冰
        (96, 132, 214),    # 蓝-水
        (186, 112, 255),   # 紫-暗
    ]

    # 外环：折线七芒棱框
    frame_points = []
    for i in range(7):
        ang = (i * 360 / 7 + t * 25) * 0.01745
        r = 50 + 4 * math.sin(t * 3 + i)
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r * 0.92
        frame_points.append((int(x), int(y)))
    pygame.draw.polygon(s, (80, 80, 90), frame_points, 3)

    # 七条能量折线（非圆形）
    for i in range(7):
        ang = (i * 360 / 7 + t * 40) * 0.01745
        mid_ang = ang + 0.25
        inner = 18
        mid = 34 + 6 * math.sin(t * 5 + i)
        outer = 52
        ix = 60 + math.cos(ang) * inner
        iy = 60 + math.sin(ang) * inner
        mx = 60 + math.cos(mid_ang) * mid
        my = 60 + math.sin(mid_ang) * mid
        ox = 60 + math.cos(ang) * outer
        oy = 60 + math.sin(ang) * outer
        pygame.draw.lines(s, colors[i], False, [(int(ix), int(iy)), (int(mx), int(my)), (int(ox), int(oy))], 3)

    # 中层：旋转菱格网
    grid = pygame.Surface((120, 120), pygame.SRCALPHA)
    rot = t * 18
    for offset in range(-3, 4):
        y0 = 60 + offset * 10
        pygame.draw.aaline(grid, (200, 200, 220, 120), (0, y0), (120, y0))
        pygame.draw.aaline(grid, (200, 200, 220, 120), (y0, 0), (120 - y0, 120))
    grid = pygame.transform.rotozoom(grid, rot, 1)
    s.blit(grid, (-20, -20))

    # 内层：旋转六边核
    hex_points = []
    for i in range(6):
        ang = (i * 60 + t * 35) * 0.01745
        r = 20 + 2 * math.sin(t * 4 + i)
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        hex_points.append((int(x), int(y)))
    pygame.draw.polygon(s, colors[int(t) % 7], hex_points)
    pygame.draw.polygon(s, (255, 255, 255), hex_points, 2)

    # Ω字形（线段组合，避免圆形）
    omega = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.arc(omega, (150, 150, 200), (4, 6, 32, 22), 0, math.pi, 3)
    pygame.draw.line(omega, (150, 150, 200), (4, 18), (4, 30), 3)
    pygame.draw.line(omega, (150, 150, 200), (36, 18), (36, 30), 3)
    pygame.draw.line(omega, (150, 150, 200), (10, 28), (30, 28), 3)
    s.blit(omega, (40, 40))

    # 碎片化粒子（多边形片）
    shard_count = 12
    for i in range(shard_count):
        ang = (i * (360 / shard_count) - t * 55) * 0.01745
        r = 38 + 5 * math.sin(t * 6 + i)
        cx = 60 + math.cos(ang) * r
        cy = 60 + math.sin(ang) * r
        shard = [
            (cx + 4, cy - 2),
            (cx + 8, cy + 2),
            (cx - 2, cy + 6),
            (cx - 6, cy + 1),
        ]
        pygame.draw.polygon(s, (*colors[i % 7], 200), shard)


def _render_omega_divine(s, t, pulse):
    """神圣审判 - 金白圣光主题，十字光剑与羽刃"""
    gold = (255, 215, 64)
    white = (255, 255, 255)
    ivory = (255, 235, 210)

    # 双层斜十字光剑
    cross_len = int(48 + 6 * pulse)
    cross_thickness = 4
    for rot in [0, 45]:
        rot_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(rot_surf, gold, [
            (60 - cross_thickness, 60 - cross_len),
            (60 + cross_thickness, 60 - cross_len),
            (60 + cross_thickness, 60 + cross_len),
            (60 - cross_thickness, 60 + cross_len),
        ])
        pygame.draw.polygon(rot_surf, gold, [
            (60 - cross_len, 60 - cross_thickness),
            (60 + cross_len, 60 - cross_thickness),
            (60 + cross_len, 60 + cross_thickness),
            (60 - cross_len, 60 + cross_thickness),
        ])
        rot_surf = pygame.transform.rotozoom(rot_surf, rot + t * 6, 1)
        s.blit(rot_surf, (-20, -20))

    # 六翼羽刃（长三角）
    for i in range(6):
        ang = (i * 60 + 30 + math.sin(t * 2 + i) * 8) * 0.01745
        base = 18
        tip = 46 + 6 * pulse
        px = 60 + math.cos(ang) * tip
        py = 60 + math.sin(ang) * tip
        left = (60 + math.cos(ang + 0.45) * base, 60 + math.sin(ang + 0.45) * base)
        right = (60 + math.cos(ang - 0.45) * base, 60 + math.sin(ang - 0.45) * base)
        pygame.draw.polygon(s, ivory, [(px, py), left, right])
        pygame.draw.polygon(s, gold, [(px, py), left, right], 2)

    # 中心圣核（分层方钻）
    core = [
        (60, 40), (78, 60), (60, 80), (42, 60)
    ]
    pygame.draw.polygon(s, white, core)
    inner = [(60, 46), (74, 60), (60, 74), (46, 60)]
    pygame.draw.polygon(s, gold, inner)
    pygame.draw.line(s, gold, inner[0], inner[2], 2)
    pygame.draw.line(s, gold, inner[1], inner[3], 2)


def _render_omega_void(s, t, pulse):
    """虚空终末 - 深紫黑暗主题，裂隙棱带与折线眼"""
    void_purple = (70, 10, 120)
    abyss = (20, 5, 40)
    glow = (190, 120, 255)

    # 扭曲菱环
    for ring in range(5):
        r = 50 - ring * 9
        rot = t * (28 + ring * 8) * (1 if ring % 2 == 0 else -1)
        band = []
        for seg in range(10):
            ang = (seg * 36 + rot) * 0.01745
            off = 6 * math.sin(t * 4 + seg + ring)
            x = 60 + math.cos(ang) * (r + off)
            y = 60 + math.sin(ang) * (r - off * 0.4)
            band.append((int(x), int(y)))
        pygame.draw.polygon(s, (*void_purple, 140 - ring * 15), band, 2)

    # 裂隙棱带（锯齿线）
    for i in range(8):
        ang = (i * 45 + t * 22) * 0.01745
        len1 = 28 + 10 * math.sin(t * 5 + i)
        len2 = 52
        base = (60, 60)
        mid = (60 + math.cos(ang) * len1, 60 + math.sin(ang) * len1)
        tip = (60 + math.cos(ang + 0.15) * len2, 60 + math.sin(ang + 0.15) * len2)
        pygame.draw.polygon(s, glow, [base, mid, tip])

    # 中心多边眼
    hex_eye = []
    for i in range(6):
        ang = (i * 60 + t * 30) * 0.01745
        r = 16 + 2 * math.sin(t * 3 + i)
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        hex_eye.append((int(x), int(y)))
    pygame.draw.polygon(s, abyss, hex_eye)
    pygame.draw.polygon(s, glow, hex_eye, 2)

    # 瞳孔裂隙（折线）
    slit = [
        (60 - 10, 60 - 2),
        (60 - 3, 60 - 6),
        (60 + 4, 60 + 6),
        (60 + 11, 60 + 2),
    ]
    pygame.draw.polygon(s, glow, slit)


def _render_omega_aurora(s, t, pulse):
    """极光流转 - 七彩极光主题，棱镜碎片与波纹多边形"""
    aurora_colors = [
        (255, 90, 140),
        (255, 180, 80),
        (180, 255, 90),
        (80, 255, 180),
        (80, 180, 255),
        (140, 90, 255),
        (255, 90, 200),
    ]

    # 极光波纹带（多边形条带）
    for band in range(7):
        wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pts_top = []
        pts_bot = []
        for x in range(0, 121, 8):
            phase = (x * 0.06 + t * 2 + band * 0.8)
            y_mid = 60 + math.sin(phase) * (18 + band * 2.5)
            pts_top.append((x, int(y_mid - 4)))
            pts_bot.append((x, int(y_mid + 4)))
        ribbon = pts_top + pts_bot[::-1]
        pygame.draw.polygon(wave_surf, (*aurora_colors[band], 70), ribbon)
        s.blit(wave_surf, (0, 0))

    # 旋转棱镜碎片环
    for i in range(12):
        ang = (i * 30 + t * 35) * 0.01745
        r = 42 + 6 * math.sin(t * 4 + i)
        cx = 60 + math.cos(ang) * r
        cy = 60 + math.sin(ang) * r
        shard = [
            (cx, cy - 7),
            (cx + 5, cy + 2),
            (cx - 5, cy + 5),
        ]
        pygame.draw.polygon(s, aurora_colors[i % 7], shard)
        pygame.draw.polygon(s, (255, 255, 255), shard, 1)

    # 中心八边棱镜
    prism = []
    for i in range(8):
        ang = (i * 45 + t * 18) * 0.01745
        r = 22 + 3 * math.sin(t * 5 + i)
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        prism.append((int(x), int(y)))
    pygame.draw.polygon(s, (255, 255, 255, 180), prism)
    for i in range(8):
        pygame.draw.line(s, aurora_colors[i % 7], prism[i], prism[(i + 1) % 8], 2)

    # 核心菱形
    diamond = [(60, 50), (70, 60), (60, 70), (50, 60)]
    pygame.draw.polygon(s, aurora_colors[int(t * 3) % 7], diamond)
    pygame.draw.polygon(s, (255, 255, 255), diamond, 2)


def _render_omega_celestial(s, t, pulse):
    """天界机神 - 蓝金神圣主题，齿轮光轮与刃翼"""
    blue = (70, 140, 255)
    gold = (255, 210, 80)
    white = (255, 255, 255)

    # 三层齿轮光轮
    for ring in range(3):
        r = 48 - ring * 14
        teeth = 12 - ring * 2
        rot = t * (22 + ring * 8) * (1 if ring % 2 == 0 else -1)
        gear = []
        for i in range(teeth * 2):
            ang = (i * 180 / teeth + rot) * 0.01745
            rad = r if i % 2 == 0 else r - 6
            x = 60 + math.cos(ang) * rad
            y = 60 + math.sin(ang) * rad
            gear.append((int(x), int(y)))
        color = gold if ring == 1 else blue
        pygame.draw.polygon(s, color, gear, 2)

    # 八刃翼（梯形刀刃）
    for i in range(8):
        ang = (i * 45 + 22.5 + math.sin(t * 2.5 + i) * 6) * 0.01745
        base_in = 20
        base_out = 28
        tip = 52 + 5 * pulse
        b1 = (60 + math.cos(ang - 0.12) * base_in, 60 + math.sin(ang - 0.12) * base_in)
        b2 = (60 + math.cos(ang + 0.12) * base_in, 60 + math.sin(ang + 0.12) * base_in)
        m1 = (60 + math.cos(ang - 0.08) * base_out, 60 + math.sin(ang - 0.08) * base_out)
        m2 = (60 + math.cos(ang + 0.08) * base_out, 60 + math.sin(ang + 0.08) * base_out)
        tp = (60 + math.cos(ang) * tip, 60 + math.sin(ang) * tip)
        blade = [b1, m1, tp, m2, b2]
        color = gold if i % 2 == 0 else blue
        pygame.draw.polygon(s, color, blade)
        pygame.draw.polygon(s, white, blade, 1)

    # 中心十二边神核
    core = []
    for i in range(12):
        ang = (i * 30 + t * 25) * 0.01745
        r = 14 + 2 * math.sin(t * 4 + i)
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        core.append((int(x), int(y)))
    pygame.draw.polygon(s, white, core)
    pygame.draw.polygon(s, gold, core, 2)
    # 内六边
    inner = []
    for i in range(6):
        ang = (i * 60 + t * 30) * 0.01745
        x = 60 + math.cos(ang) * 8
        y = 60 + math.sin(ang) * 8
        inner.append((int(x), int(y)))
    pygame.draw.polygon(s, blue, inner)


def _render_omega_infernal(s, t, pulse):
    """地狱烈焰 - 红黑炼狱主题，锯齿火焰与魔角"""
    crimson = (255, 40, 20)
    blood = (140, 10, 0)
    black = (25, 5, 5)
    ember = (255, 190, 60)

    # 外层锯齿火环（不规则多边形）
    fire_ring = []
    for i in range(24):
        ang = (i * 15 + t * 45) * 0.01745
        r = 48 + (12 if i % 2 == 0 else 0) + 5 * math.sin(t * 6 + i)
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        fire_ring.append((int(x), int(y)))
    pygame.draw.polygon(s, (*crimson, 180), fire_ring)
    pygame.draw.polygon(s, ember, fire_ring, 2)

    # 内层地狱熔岩纹
    lava_band = []
    for i in range(16):
        ang = (i * 22.5 - t * 30) * 0.01745
        r = 28 + 8 * math.sin(t * 5 + i * 0.7)
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        lava_band.append((int(x), int(y)))
    pygame.draw.polygon(s, blood, lava_band)
    pygame.draw.polygon(s, crimson, lava_band, 2)

    # 双魔角（曲线三角）
    for side in [-1, 1]:
        base = (60 + side * 12, 58)
        mid = (60 + side * 28, 42 + 4 * math.sin(t * 3))
        tip = (60 + side * 38, 22 + 6 * math.sin(t * 2.5))
        horn = [base, mid, tip, (60 + side * 22, 50)]
        pygame.draw.polygon(s, blood, horn)
        pygame.draw.polygon(s, ember, horn, 2)

    # 中心熔岩六边核
    core = []
    for i in range(6):
        ang = (i * 60 + t * 20) * 0.01745
        r = 14 + 3 * pulse
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        core.append((int(x), int(y)))
    pygame.draw.polygon(s, black, core)
    pygame.draw.polygon(s, crimson, core, 2)
    # 内菱形
    inner = [(60, 54), (66, 60), (60, 66), (54, 60)]
    pygame.draw.polygon(s, ember, inner)


def _render_omega_quantum(s, t, pulse):
    """量子形态 - 青蓝科技主题，六边网格与电子轨迹"""
    cyan = (0, 240, 255)
    blue = (20, 120, 255)
    white = (255, 255, 255)

    # 六边蜂窝网格
    grid = pygame.Surface((120, 120), pygame.SRCALPHA)
    hex_r = 12
    for row in range(-2, 5):
        for col in range(-2, 6):
            cx = col * hex_r * 1.73 + (row % 2) * hex_r * 0.866 + t * 8 % (hex_r * 1.73)
            cy = row * hex_r * 1.5 + 10
            if 0 < cx < 120 and 0 < cy < 120:
                hex_pts = []
                for i in range(6):
                    ang = (i * 60 + 30) * 0.01745
                    hx = cx + math.cos(ang) * hex_r * 0.8
                    hy = cy + math.sin(ang) * hex_r * 0.8
                    hex_pts.append((int(hx), int(hy)))
                pygame.draw.polygon(grid, (*cyan, 40), hex_pts, 1)
    s.blit(grid, (0, 0))

    # 三层椭圆轨道（多边形近似）
    for orbit in range(3):
        r = 22 + orbit * 14
        rot = t * (35 - orbit * 8)
        pts = []
        for i in range(20):
            ang = (i * 18 + rot) * 0.01745
            x = 60 + math.cos(ang) * r
            y = 60 + math.sin(ang) * (r * 0.65)
            pts.append((int(x), int(y)))
        pygame.draw.polygon(s, blue, pts, 1)
        # 电子菱形
        for e in range(2):
            e_ang = (rot + e * 180) * 0.01745
            ex = 60 + math.cos(e_ang) * r
            ey = 60 + math.sin(e_ang) * (r * 0.65)
            electron = [(ex, ey - 5), (ex + 4, ey), (ex, ey + 5), (ex - 4, ey)]
            pygame.draw.polygon(s, cyan, electron)
            pygame.draw.polygon(s, white, electron, 1)

    # 中心八边量子核
    core = []
    for i in range(8):
        ang = (i * 45 + t * 40) * 0.01745
        r = 12 + 3 * math.sin(t * 6 + i)
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        core.append((int(x), int(y)))
    pygame.draw.polygon(s, blue, core)
    pygame.draw.polygon(s, cyan, core, 2)
    # 内方块
    inner = [(60, 55), (65, 60), (60, 65), (55, 60)]
    pygame.draw.polygon(s, white, inner)


def _render_omega_primal(s, t, pulse):
    """原始神力 - 翠绿自然主题，生命之树与蔓藤"""
    emerald = (40, 200, 90)
    forest = (25, 140, 55)
    gold = (255, 210, 60)
    bark = (120, 75, 35)
    root_c = (90, 60, 30)

    # 树干（梯形）
    trunk = [(55, 58), (65, 58), (68, 98), (52, 98)]
    pygame.draw.polygon(s, bark, trunk)
    pygame.draw.polygon(s, root_c, trunk, 2)

    # 分支树枝（折线）
    branches = [
        [(60, 58), (48, 48), (38, 38 + 4 * math.sin(t * 2))],
        [(60, 58), (72, 48), (82, 38 + 4 * math.sin(t * 2 + 1))],
        [(60, 58), (55, 42), (45, 28 + 3 * math.sin(t * 2.5))],
        [(60, 58), (65, 42), (75, 28 + 3 * math.sin(t * 2.5 + 1))],
    ]
    for br in branches:
        pygame.draw.lines(s, bark, False, [(int(x), int(y)) for x, y in br], 3)

    # 树叶（多边形簇）
    leaf_centers = [(38, 32), (82, 32), (45, 22), (75, 22), (60, 12)]
    for i, (lx, ly) in enumerate(leaf_centers):
        offset = 3 * math.sin(t * 3 + i)
        leaf = [
            (lx, ly - 10 + offset),
            (lx + 9, ly + 2),
            (lx, ly + 8),
            (lx - 9, ly + 2),
        ]
        color = emerald if i % 2 == 0 else forest
        pygame.draw.polygon(s, color, leaf)
        pygame.draw.polygon(s, gold, leaf, 1)

    # 根系（折线三角）
    roots = [
        [(55, 98), (42, 105), (30, 112)],
        [(60, 98), (60, 108), (60, 118)],
        [(65, 98), (78, 105), (90, 112)],
    ]
    for rt in roots:
        pygame.draw.lines(s, root_c, False, rt, 2)

    # 环绕生命能量碎片
    for i in range(10):
        ang = (i * 36 + t * 28) * 0.01745
        r = 50 + 5 * math.sin(t * 4 + i)
        cx = 60 + math.cos(ang) * r
        cy = 60 + math.sin(ang) * r
        shard = [
            (cx, cy - 5),
            (cx + 4, cy),
            (cx, cy + 5),
            (cx - 4, cy),
        ]
        color = emerald if i % 2 == 0 else gold
        pygame.draw.polygon(s, color, shard)

    # 中心花蕾（五边形）
    bud = []
    for i in range(5):
        ang = (i * 72 - 90 + t * 12) * 0.01745
        r = 8 + 2 * pulse
        x = 60 + math.cos(ang) * r
        y = 30 + math.sin(ang) * r
        bud.append((int(x), int(y)))
    pygame.draw.polygon(s, gold, bud)
    pygame.draw.polygon(s, emerald, bud, 2)


def _render_omega_clockwork(s, t, pulse):
    """永恒钟表 - 精密齿轮与时钟机械"""
    bronze = (180, 130, 70)
    gold = (220, 180, 80)
    dark = (60, 45, 30)
    white = (255, 250, 240)

    # 三层同心齿轮（不同转速）
    for gear_idx, (r, teeth, speed) in enumerate([(48, 24, 1), (32, 16, -1.5), (18, 10, 2.2)]):
        rot = t * 20 * speed
        pts = []
        for i in range(teeth * 2):
            ang = (i * 180 / teeth + rot) * 0.01745
            rad = r if i % 2 == 0 else r - 5
            x = 60 + math.cos(ang) * rad
            y = 60 + math.sin(ang) * rad
            pts.append((int(x), int(y)))
        color = bronze if gear_idx == 0 else (gold if gear_idx == 1 else dark)
        pygame.draw.polygon(s, color, pts)
        pygame.draw.polygon(s, gold if gear_idx != 1 else bronze, pts, 2)

    # 时钟指针（时/分/秒）
    for length, width, speed, color in [(35, 3, 0.5, gold), (28, 4, 6, bronze), (22, 2, 72, white)]:
        ang = (t * speed - 90) * 0.01745
        tip = (60 + math.cos(ang) * length, 60 + math.sin(ang) * length)
        pygame.draw.line(s, color, (60, 60), (int(tip[0]), int(tip[1])), width)

    # 罗马数字刻度位置（12点钟方向等）
    for i in range(12):
        ang = (i * 30 - 90) * 0.01745
        r = 44
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        mark = [(x, y - 3), (x + 2, y), (x, y + 3), (x - 2, y)]
        pygame.draw.polygon(s, white, mark)

    # 中心轴（八边形）
    axle = []
    for i in range(8):
        ang = (i * 45 + t * 30) * 0.01745
        x = 60 + math.cos(ang) * 6
        y = 60 + math.sin(ang) * 6
        axle.append((int(x), int(y)))
    pygame.draw.polygon(s, gold, axle)


def _render_omega_dragon(s, t, pulse):
    """神龙之魂 - 东方龙鳞与龙须"""
    jade = (60, 180, 120)
    gold = (255, 200, 60)
    red = (220, 50, 50)
    dark = (30, 60, 45)

    # 龙身S曲线（鳞片链）
    for row in range(3):
        offset = row * 8
        for i in range(12):
            progress = i / 11
            wave = math.sin(progress * math.pi * 2 + t * 3 + row * 0.5) * 15
            x = 20 + progress * 80
            y = 55 + wave + (row - 1) * 12
            # 菱形鳞片
            scale = [
                (x, y - 6), (x + 5, y), (x, y + 6), (x - 5, y)
            ]
            color = jade if (i + row) % 3 != 0 else gold
            pygame.draw.polygon(s, color, scale)
            pygame.draw.polygon(s, dark, scale, 1)

    # 龙首（三角+角）
    head = [(95, 50), (110, 60), (95, 70), (85, 60)]
    pygame.draw.polygon(s, jade, head)
    pygame.draw.polygon(s, gold, head, 2)
    # 龙角
    horn1 = [(98, 48), (105, 35 + 3 * math.sin(t * 2)), (100, 50)]
    horn2 = [(98, 72), (105, 85 - 3 * math.sin(t * 2)), (100, 70)]
    pygame.draw.polygon(s, gold, horn1)
    pygame.draw.polygon(s, gold, horn2)
    # 龙眼
    pygame.draw.polygon(s, red, [(100, 58), (104, 60), (100, 62), (96, 60)])

    # 龙须（飘动折线）
    for side in [-1, 1]:
        whisker = [(108, 60 + side * 5)]
        for seg in range(4):
            wx = 112 + seg * 6
            wy = 60 + side * (8 + seg * 3 + 4 * math.sin(t * 4 + seg))
            whisker.append((wx, wy))
        pygame.draw.lines(s, gold, False, whisker, 2)

    # 龙珠（中心六边形）
    pearl = []
    for i in range(6):
        ang = (i * 60 + t * 25) * 0.01745
        x = 35 + math.cos(ang) * 12
        y = 60 + math.sin(ang) * 12
        pearl.append((int(x), int(y)))
    pygame.draw.polygon(s, gold, pearl)
    pygame.draw.polygon(s, red, pearl, 2)
    inner = [(35, 54), (41, 60), (35, 66), (29, 60)]
    pygame.draw.polygon(s, red, inner)


def _render_omega_galactic(s, t, pulse):
    """银河霸主 - 星系漩涡与星云"""
    purple = (100, 60, 180)
    blue = (60, 100, 200)
    pink = (200, 100, 180)
    white = (255, 255, 255)
    dark = (20, 15, 40)

    # 背景星云（不规则多边形）
    nebula = pygame.Surface((120, 120), pygame.SRCALPHA)
    for layer in range(3):
        pts = []
        sides = 12 + layer * 4
        for i in range(sides):
            ang = (i * 360 / sides + t * (5 - layer * 2)) * 0.01745
            r = 55 - layer * 12 + 8 * math.sin(t * 2 + i + layer)
            x = 60 + math.cos(ang) * r
            y = 60 + math.sin(ang) * r
            pts.append((int(x), int(y)))
        colors = [purple, blue, pink]
        pygame.draw.polygon(nebula, (*colors[layer], 60), pts)
    s.blit(nebula, (0, 0))

    # 四条旋臂（弧形多边形）
    for arm in range(4):
        arm_pts = []
        base = arm * 90 + t * 15
        for seg in range(15):
            progress = seg / 14
            ang = (base + progress * 180) * 0.01745
            r = 10 + progress * 45
            x = 60 + math.cos(ang) * r
            y = 60 + math.sin(ang) * r
            arm_pts.append((int(x), int(y)))
        for seg in range(14, -1, -1):
            progress = seg / 14
            ang = (base + progress * 180 + 12) * 0.01745
            r = 8 + progress * 40
            x = 60 + math.cos(ang) * r
            y = 60 + math.sin(ang) * r
            arm_pts.append((int(x), int(y)))
        color = purple if arm % 2 == 0 else blue
        pygame.draw.polygon(s, color, arm_pts)

    # 散布星点（小菱形）
    import random
    random.seed(77)
    for _ in range(20):
        sx = random.randint(15, 105)
        sy = random.randint(15, 105)
        dist = math.sqrt((sx - 60) ** 2 + (sy - 60) ** 2)
        if dist < 52:
            star = [(sx, sy - 2), (sx + 2, sy), (sx, sy + 2), (sx - 2, sy)]
            pygame.draw.polygon(s, white, star)

    # 中心黑洞（多层六边形）
    for layer in range(3):
        r = 14 - layer * 4
        pts = []
        for i in range(6):
            ang = (i * 60 + t * 35 * (1 if layer % 2 == 0 else -1)) * 0.01745
            x = 60 + math.cos(ang) * r
            y = 60 + math.sin(ang) * r
            pts.append((int(x), int(y)))
        color = dark if layer == 0 else (purple if layer == 1 else white)
        pygame.draw.polygon(s, color, pts)


def _render_omega_runic(s, t, pulse):
    """符文铭刻 - 古代神秘符文"""
    stone = (80, 75, 70)
    glow = (120, 200, 255)
    gold = (255, 200, 100)
    dark = (30, 28, 25)

    # 石板底座（八边形）
    tablet = []
    for i in range(8):
        ang = (i * 45 + 22.5) * 0.01745
        r = 52
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        tablet.append((int(x), int(y)))
    pygame.draw.polygon(s, stone, tablet)
    pygame.draw.polygon(s, dark, tablet, 3)

    # 内层符文环
    inner_ring = []
    for i in range(12):
        ang = (i * 30 + t * 8) * 0.01745
        r = 38
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        inner_ring.append((int(x), int(y)))
    pygame.draw.polygon(s, dark, inner_ring, 2)

    # 八个符文字符（各种几何图案）
    rune_patterns = [
        [(0, -8), (5, 0), (0, 8), (-5, 0)],  # 菱形
        [(0, -8), (6, 8), (-6, 8)],           # 三角
        [(-5, -6), (5, -6), (5, 6), (-5, 6)], # 方形
        [(0, -8), (0, 8), (-6, 0)],           # 箭头
        [(0, -8), (6, -2), (4, 8), (-4, 8), (-6, -2)],  # 五边
        [(-6, -4), (6, -4), (0, 8)],          # 倒三角
        [(0, -6), (6, 0), (0, 6), (-6, 0), (0, -6), (0, 6)],  # X
        [(-5, -5), (5, -5), (0, 0), (5, 5), (-5, 5), (0, 0)], # 沙漏
    ]
    glow_alpha = int(150 + 100 * math.sin(t * 3))
    for i in range(8):
        ang = (i * 45 + t * 8) * 0.01745
        r = 38
        cx = 60 + math.cos(ang) * r
        cy = 60 + math.sin(ang) * r
        pattern = rune_patterns[i]
        pts = [(cx + dx, cy + dy) for dx, dy in pattern]
        rune_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(rune_surf, (*glow, glow_alpha), pts)
        pygame.draw.polygon(rune_surf, gold, pts, 1)
        s.blit(rune_surf, (0, 0))

    # 中心大符文（旋转五芒星）
    star = []
    for i in range(10):
        ang = (i * 36 - 90 + t * 12) * 0.01745
        r = 18 if i % 2 == 0 else 8
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        star.append((int(x), int(y)))
    pygame.draw.polygon(s, glow, star)
    pygame.draw.polygon(s, gold, star, 2)


def _render_omega_tempest(s, t, pulse):
    """风暴君王 - 雷电风暴与旋风"""
    dark_blue = (20, 30, 60)
    lightning = (200, 220, 255)
    yellow = (255, 255, 150)
    purple = (150, 100, 200)

    # 风暴云层（多层不规则形）
    for layer in range(4):
        cloud = []
        sides = 16 - layer * 2
        rot = t * (10 + layer * 5) * (1 if layer % 2 == 0 else -1)
        for i in range(sides):
            ang = (i * 360 / sides + rot) * 0.01745
            r = 52 - layer * 10 + 6 * math.sin(t * 4 + i * 2 + layer)
            x = 60 + math.cos(ang) * r
            y = 60 + math.sin(ang) * r
            cloud.append((int(x), int(y)))
        alpha = 180 - layer * 40
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (*dark_blue, alpha), cloud)
        s.blit(surf, (0, 0))

    # 闪电（锯齿折线）
    for bolt in range(6):
        ang_base = (bolt * 60 + t * 30) * 0.01745
        bolt_pts = [(60, 60)]
        pos = [60, 60]
        for seg in range(5):
            length = 8 + seg * 2
            ang = ang_base + (0.3 if seg % 2 == 0 else -0.3)
            pos = [pos[0] + math.cos(ang) * length, pos[1] + math.sin(ang) * length]
            bolt_pts.append((int(pos[0]), int(pos[1])))
        flash = int(200 + 55 * math.sin(t * 15 + bolt * 2))
        pygame.draw.lines(s, (flash, flash, 255), False, bolt_pts, 3)
        # 闪电末端光点
        end = bolt_pts[-1]
        spark = [(end[0], end[1] - 4), (end[0] + 3, end[1]), (end[0], end[1] + 4), (end[0] - 3, end[1])]
        pygame.draw.polygon(s, yellow, spark)

    # 旋风中心（螺旋线）
    spiral_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for arm in range(3):
        pts = []
        for seg in range(20):
            progress = seg / 19
            ang = (arm * 120 + progress * 360 + t * 60) * 0.01745
            r = 5 + progress * 18
            x = 60 + math.cos(ang) * r
            y = 60 + math.sin(ang) * r
            pts.append((int(x), int(y)))
        pygame.draw.lines(spiral_surf, (*purple, 200), False, pts, 2)
    s.blit(spiral_surf, (0, 0))

    # 风暴之眼（中心六边形）
    eye = []
    for i in range(6):
        ang = (i * 60 + t * 40) * 0.01745
        r = 10 + 3 * math.sin(t * 5 + i)
        x = 60 + math.cos(ang) * r
        y = 60 + math.sin(ang) * r
        eye.append((int(x), int(y)))
    pygame.draw.polygon(s, lightning, eye)
    pygame.draw.polygon(s, yellow, eye, 2)


__all__ = ['render_omega_skin', 'is_omega_style', 'OMEGA_STYLES']
