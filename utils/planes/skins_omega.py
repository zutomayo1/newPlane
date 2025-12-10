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
    "omega_ex",          # EX改装涂装
    "omega_ex2",         # EX2改装涂装
    "omega_ex3",         # EX3改装涂装
    "omega_ex4",         # EX4改装涂装
    "omega_ex5",         # EX5改装涂装
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
    elif model_style.startswith("omega_ex"):
        _render_omega_ex(s, t, pulse, model_style)
    else:
        _render_omega_base(s, t, pulse)
    
    return s


def _render_omega_base(s, t, pulse):
    """Omega 基础渲染 - 融合七属性的机械神殿"""
    # 七彩流光色系
    colors = [
        (255, 100, 100),   # 红-火
        (255, 200, 100),   # 橙-雷
        (255, 255, 100),   # 黄-光
        (100, 255, 100),   # 绿-风
        (100, 200, 255),   # 青-冰
        (100, 100, 255),   # 蓝-水
        (200, 100, 255),   # 紫-暗
    ]
    
    # 外围神圣光环（七芒星）
    for i in range(7):
        angle = (i * 360 / 7 + t * 30) * 0.01745
        color = colors[i]
        outer_r = 52 + int(3 * math.sin(t * 4 + i))
        ox = 60 + math.cos(angle) * outer_r
        oy = 60 + math.sin(angle) * outer_r
        
        # 光芒线
        inner_r = 25
        ix = 60 + math.cos(angle) * inner_r
        iy = 60 + math.sin(angle) * inner_r
        pygame.draw.line(s, color, (int(ix), int(iy)), (int(ox), int(oy)), 3)
        
        # 顶点光球
        glow_size = int(6 + 2 * math.sin(t * 5 + i))
        pygame.draw.circle(s, color, (int(ox), int(oy)), glow_size)
        pygame.draw.circle(s, (255, 255, 255), (int(ox), int(oy)), glow_size - 2)
    
    # 七芒星连线
    for i in range(7):
        angle1 = (i * 360 / 7 + t * 30) * 0.01745
        angle2 = ((i + 2) * 360 / 7 + t * 30) * 0.01745  # 跳两个点连线
        r = 52
        x1 = 60 + math.cos(angle1) * r
        y1 = 60 + math.sin(angle1) * r
        x2 = 60 + math.cos(angle2) * r
        y2 = 60 + math.sin(angle2) * r
        
        line_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(line_surf, (*colors[i], 150), (int(x1), int(y1)), (int(x2), int(y2)), 2)
        s.blit(line_surf, (0, 0))
    
    # 中心核心 - 多层结构
    # 外壳
    pygame.draw.circle(s, (200, 200, 220), (60, 60), 28)
    pygame.draw.circle(s, (255, 255, 255), (60, 60), 26)
    pygame.draw.circle(s, (220, 220, 240), (60, 60), 28, 2)
    
    # 内部旋转核心
    core_color_idx = int(t * 2) % 7
    core_color = colors[core_color_idx]
    pygame.draw.circle(s, core_color, (60, 60), 18)
    pygame.draw.circle(s, (255, 255, 255), (60, 60), 12)
    
    # 中心Ω符号
    omega_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    # 简化的Ω形状
    pygame.draw.arc(omega_surf, (100, 100, 150), (3, 3, 24, 20), 0, math.pi, 3)
    pygame.draw.line(omega_surf, (100, 100, 150), (3, 13), (3, 20), 3)
    pygame.draw.line(omega_surf, (100, 100, 150), (27, 13), (27, 20), 3)
    s.blit(omega_surf, (45, 50))
    
    # 环绕能量粒子
    for i in range(14):
        p_angle = (i * 360 / 14 - t * 60) * 0.01745
        p_r = 38 + int(3 * math.sin(t * 6 + i))
        px = 60 + math.cos(p_angle) * p_r
        py = 60 + math.sin(p_angle) * p_r
        p_color = colors[i % 7]
        pygame.draw.circle(s, p_color, (int(px), int(py)), 3)


def _render_omega_divine(s, t, pulse):
    """神圣审判 - 金白圣光主题"""
    gold = (255, 215, 0)
    white = (255, 255, 255)
    light_gold = (255, 240, 200)
    
    # 神圣光环
    for ring in range(3):
        ring_r = 48 - ring * 8
        ring_alpha = 200 - ring * 50
        ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (*gold, ring_alpha), (60, 60), ring_r, 2)
        s.blit(ring_surf, (0, 0))
    
    # 十字圣光
    cross_len = int(45 + 5 * pulse)
    pygame.draw.line(s, light_gold, (60, 60 - cross_len), (60, 60 + cross_len), 4)
    pygame.draw.line(s, light_gold, (60 - cross_len, 60), (60 + cross_len, 60), 4)
    
    # 对角光芒
    for i in range(4):
        angle = (45 + i * 90 + t * 20) * 0.01745
        ray_len = 35 + int(5 * math.sin(t * 4 + i))
        rx = 60 + math.cos(angle) * ray_len
        ry = 60 + math.sin(angle) * ray_len
        pygame.draw.line(s, gold, (60, 60), (int(rx), int(ry)), 2)
    
    # 中心神圣核心
    pygame.draw.circle(s, white, (60, 60), 20)
    pygame.draw.circle(s, gold, (60, 60), 16)
    pygame.draw.circle(s, light_gold, (60, 60), 10)
    
    # 天使羽翼效果
    for side in [-1, 1]:
        for feather in range(5):
            f_angle = (side * (30 + feather * 15) + math.sin(t * 3 + feather) * 5) * 0.01745
            f_len = 30 + feather * 5
            fx = 60 + math.cos(f_angle) * f_len
            fy = 60 + math.sin(f_angle) * f_len
            f_alpha = 200 - feather * 30
            f_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(f_surf, (*gold, f_alpha), (60, 60), (int(fx), int(fy)), 3)
            s.blit(f_surf, (0, 0))


def _render_omega_void(s, t, pulse):
    """虚空终末 - 深紫黑暗主题"""
    void_purple = (80, 0, 120)
    dark_purple = (40, 0, 60)
    bright_purple = (180, 80, 255)
    
    # 虚空漩涡背景
    for ring in range(6):
        ring_r = 50 - ring * 7
        rotation = t * (30 + ring * 10) * (1 if ring % 2 == 0 else -1)
        ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        for seg in range(8):
            seg_angle = (seg * 45 + rotation) * 0.01745
            seg_len = ring_r
            sx = 60 + math.cos(seg_angle) * seg_len
            sy = 60 + math.sin(seg_angle) * seg_len
            seg_alpha = 150 - ring * 20
            pygame.draw.line(ring_surf, (*void_purple, seg_alpha), (60, 60), (int(sx), int(sy)), 2)
        
        s.blit(ring_surf, (0, 0))
    
    # 虚空裂隙
    for crack in range(6):
        crack_angle = (crack * 60 + t * 15) * 0.01745
        crack_len = 45 + int(5 * math.sin(t * 5 + crack))
        cx = 60 + math.cos(crack_angle) * crack_len
        cy = 60 + math.sin(crack_angle) * crack_len
        
        # 裂隙光芒
        pygame.draw.line(s, bright_purple, (60, 60), (int(cx), int(cy)), 2)
        pygame.draw.circle(s, bright_purple, (int(cx), int(cy)), 4)
    
    # 中心虚空核心
    pygame.draw.circle(s, dark_purple, (60, 60), 22)
    pygame.draw.circle(s, void_purple, (60, 60), 18)
    
    # 脉动的虚空之眼
    eye_size = int(10 + 4 * pulse)
    pygame.draw.circle(s, (0, 0, 0), (60, 60), eye_size)
    pygame.draw.circle(s, bright_purple, (60, 60), eye_size, 2)
    
    # 中心瞳孔
    pygame.draw.circle(s, bright_purple, (60, 60), 4)


def _render_omega_aurora(s, t, pulse):
    """极光流转 - 七彩极光主题"""
    # 极光色带
    aurora_colors = [
        (255, 100, 150),
        (255, 200, 100),
        (200, 255, 100),
        (100, 255, 200),
        (100, 200, 255),
        (150, 100, 255),
        (255, 100, 200),
    ]
    
    # 流动的极光带
    for band in range(7):
        band_offset = (t * 50 + band * 30) % 360
        band_color = aurora_colors[band]
        
        wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        points = []
        for x in range(0, 121, 10):
            y = 60 + math.sin((x + band_offset) * 0.05 + band) * (20 + band * 3)
            points.append((x, int(y)))
        
        if len(points) > 1:
            pygame.draw.lines(wave_surf, (*band_color, 100), False, points, 3)
        s.blit(wave_surf, (0, 0))
    
    # 中心棱镜核心
    prism_points = []
    for i in range(6):
        angle = (i * 60 + t * 20) * 0.01745
        r = 25
        px = 60 + math.cos(angle) * r
        py = 60 + math.sin(angle) * r
        prism_points.append((int(px), int(py)))
    
    # 棱镜填充（半透明彩虹）
    prism_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.polygon(prism_surf, (255, 255, 255, 150), prism_points)
    s.blit(prism_surf, (0, 0))
    
    # 棱镜边框
    for i in range(6):
        color = aurora_colors[i]
        pygame.draw.line(s, color, prism_points[i], prism_points[(i+1)%6], 2)
    
    # 中心光核
    core_color_idx = int(t * 3) % 7
    pygame.draw.circle(s, aurora_colors[core_color_idx], (60, 60), 12)
    pygame.draw.circle(s, (255, 255, 255), (60, 60), 8)


def _render_omega_celestial(s, t, pulse):
    """天界机神 - 蓝金神圣主题"""
    celestial_blue = (80, 150, 255)
    celestial_gold = (255, 215, 100)
    white = (255, 255, 255)
    
    # 天界光轮
    for ring in range(4):
        ring_r = 50 - ring * 10
        ring_rot = t * (20 + ring * 5) * (1 if ring % 2 == 0 else -1)
        
        for spoke in range(12):
            spoke_angle = (spoke * 30 + ring_rot) * 0.01745
            inner_r = ring_r - 5
            outer_r = ring_r
            
            ix = 60 + math.cos(spoke_angle) * inner_r
            iy = 60 + math.sin(spoke_angle) * inner_r
            ox = 60 + math.cos(spoke_angle) * outer_r
            oy = 60 + math.sin(spoke_angle) * outer_r
            
            color = celestial_gold if spoke % 3 == 0 else celestial_blue
            pygame.draw.line(s, color, (int(ix), int(iy)), (int(ox), int(oy)), 2)
    
    # 六翼
    for wing in range(6):
        wing_angle = (wing * 60 + 30) * 0.01745
        wing_len = 45 + int(5 * math.sin(t * 3 + wing))
        wx = 60 + math.cos(wing_angle) * wing_len
        wy = 60 + math.sin(wing_angle) * wing_len
        
        # 翼尖
        pygame.draw.line(s, celestial_gold, (60, 60), (int(wx), int(wy)), 3)
        pygame.draw.circle(s, celestial_blue, (int(wx), int(wy)), 5)
        pygame.draw.circle(s, white, (int(wx), int(wy)), 3)
    
    # 中心神核
    pygame.draw.circle(s, celestial_blue, (60, 60), 20)
    pygame.draw.circle(s, celestial_gold, (60, 60), 15)
    pygame.draw.circle(s, white, (60, 60), 10)


def _render_omega_infernal(s, t, pulse):
    """地狱烈焰 - 红黑炼狱主题"""
    infernal_red = (255, 50, 0)
    dark_red = (150, 0, 0)
    black = (30, 0, 0)
    ember = (255, 200, 50)
    
    # 炼狱火焰
    for flame in range(12):
        flame_angle = (flame * 30 + t * 40) * 0.01745
        flame_len = 35 + int(15 * math.sin(t * 6 + flame))
        
        fx = 60 + math.cos(flame_angle) * flame_len
        fy = 60 + math.sin(flame_angle) * flame_len
        
        # 火焰渐变
        mid_x = 60 + math.cos(flame_angle) * (flame_len * 0.6)
        mid_y = 60 + math.sin(flame_angle) * (flame_len * 0.6)
        
        pygame.draw.line(s, dark_red, (60, 60), (int(mid_x), int(mid_y)), 4)
        pygame.draw.line(s, infernal_red, (int(mid_x), int(mid_y)), (int(fx), int(fy)), 3)
        pygame.draw.circle(s, ember, (int(fx), int(fy)), 4)
    
    # 魔王之角
    for horn in [-1, 1]:
        horn_base_x = 60 + horn * 15
        horn_tip_x = 60 + horn * 35
        horn_tip_y = 30 + int(5 * math.sin(t * 2))
        
        pygame.draw.line(s, dark_red, (horn_base_x, 50), (horn_tip_x, horn_tip_y), 5)
        pygame.draw.circle(s, infernal_red, (horn_tip_x, horn_tip_y), 4)
    
    # 中心熔岩核心
    pygame.draw.circle(s, black, (60, 60), 22)
    pygame.draw.circle(s, dark_red, (60, 60), 18)
    
    # 脉动的熔岩
    lava_size = int(12 + 4 * pulse)
    pygame.draw.circle(s, infernal_red, (60, 60), lava_size)
    pygame.draw.circle(s, ember, (60, 60), lava_size - 4)


def _render_omega_quantum(s, t, pulse):
    """量子形态 - 青蓝科技主题"""
    quantum_cyan = (0, 255, 255)
    quantum_blue = (0, 150, 255)
    white = (255, 255, 255)
    
    # 量子网格
    grid_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(6):
        offset = (t * 20 + i * 20) % 120
        pygame.draw.line(grid_surf, (*quantum_cyan, 50), (0, int(offset)), (120, int(offset)), 1)
        pygame.draw.line(grid_surf, (*quantum_cyan, 50), (int(offset), 0), (int(offset), 120), 1)
    s.blit(grid_surf, (0, 0))
    
    # 量子轨道
    for orbit in range(3):
        orbit_r = 25 + orbit * 12
        orbit_rot = t * (40 - orbit * 10)
        
        # 轨道线
        pygame.draw.circle(s, quantum_blue, (60, 60), orbit_r, 1)
        
        # 轨道电子
        for electron in range(2):
            e_angle = (orbit_rot + electron * 180) * 0.01745
            ex = 60 + math.cos(e_angle) * orbit_r
            ey = 60 + math.sin(e_angle) * orbit_r
            pygame.draw.circle(s, quantum_cyan, (int(ex), int(ey)), 4)
            pygame.draw.circle(s, white, (int(ex), int(ey)), 2)
    
    # 中心量子核
    pygame.draw.circle(s, quantum_blue, (60, 60), 15)
    pygame.draw.circle(s, quantum_cyan, (60, 60), 10)
    
    # 不确定性波动
    wave_size = int(8 + 4 * math.sin(t * 8))
    pygame.draw.circle(s, white, (60, 60), wave_size)


def _render_omega_primal(s, t, pulse):
    """原始神力 - 翠绿自然主题"""
    primal_green = (50, 200, 80)
    forest_green = (30, 150, 50)
    gold = (255, 215, 0)
    brown = (139, 90, 43)
    
    # 生命之树
    # 树干
    pygame.draw.rect(s, brown, (55, 60, 10, 35))
    
    # 树冠（多层叶子）
    for layer in range(4):
        layer_y = 55 - layer * 12
        layer_width = 40 - layer * 8
        leaf_color = primal_green if layer % 2 == 0 else forest_green
        
        pygame.draw.polygon(s, leaf_color, [
            (60, layer_y - 15),
            (60 - layer_width // 2, layer_y + 5),
            (60 + layer_width // 2, layer_y + 5)
        ])
    
    # 根系
    for root in range(5):
        root_angle = (root * 36 + 162) * 0.01745
        root_len = 20 + int(5 * math.sin(t * 2 + root))
        rx = 60 + math.cos(root_angle) * root_len
        ry = 95 + math.sin(root_angle) * (root_len * 0.3)
        pygame.draw.line(s, brown, (60, 95), (int(rx), int(ry)), 2)
    
    # 生命能量粒子
    for particle in range(12):
        p_angle = (particle * 30 + t * 25) * 0.01745
        p_r = 45 + int(5 * math.sin(t * 4 + particle))
        px = 60 + math.cos(p_angle) * p_r
        py = 60 + math.sin(p_angle) * p_r
        
        p_color = primal_green if particle % 2 == 0 else gold
        p_size = int(3 + 2 * math.sin(t * 5 + particle))
        pygame.draw.circle(s, p_color, (int(px), int(py)), p_size)
    
    # 中心生命核心（花蕾）
    pygame.draw.circle(s, gold, (60, 30), 8)
    for petal in range(5):
        petal_angle = (petal * 72 + t * 10) * 0.01745
        px = 60 + math.cos(petal_angle) * 12
        py = 30 + math.sin(petal_angle) * 12
        pygame.draw.circle(s, primal_green, (int(px), int(py)), 5)


def _render_omega_ex(s, t, pulse, style):
    """EX 改装系列"""
    # 根据 EX 等级确定颜色
    ex_colors = {
        "omega_ex": ((255, 200, 150), (255, 150, 100)),    # 铜色
        "omega_ex2": ((200, 200, 220), (150, 150, 200)),   # 银色
        "omega_ex3": ((255, 220, 100), (255, 180, 50)),    # 金色
        "omega_ex4": ((200, 100, 255), (150, 50, 200)),    # 紫晶
        "omega_ex5": ((255, 255, 255), (200, 220, 255)),   # 圣白
    }
    
    main_color, accent = ex_colors.get(style, ((255, 255, 255), (200, 200, 200)))
    
    # EX 机甲框架
    # 六边形装甲板
    for i in range(6):
        angle = (i * 60 + t * 15) * 0.01745
        r = 42
        x = 60 + math.cos(angle) * r
        y = 60 + math.sin(angle) * r
        
        # 装甲连接线
        next_angle = ((i + 1) * 60 + t * 15) * 0.01745
        nx = 60 + math.cos(next_angle) * r
        ny = 60 + math.sin(next_angle) * r
        pygame.draw.line(s, main_color, (int(x), int(y)), (int(nx), int(ny)), 3)
        
        # 节点
        pygame.draw.circle(s, accent, (int(x), int(y)), 5)
    
    # 内部三角结构
    for tri in range(2):
        tri_offset = tri * 60
        tri_points = []
        for i in range(3):
            angle = (i * 120 + tri_offset + t * 20) * 0.01745
            r = 28
            tx = 60 + math.cos(angle) * r
            ty = 60 + math.sin(angle) * r
            tri_points.append((int(tx), int(ty)))
        pygame.draw.polygon(s, accent, tri_points, 2)
    
    # 中心 EX 核心
    pygame.draw.circle(s, main_color, (60, 60), 18)
    pygame.draw.circle(s, accent, (60, 60), 12)
    
    # EX 等级标记
    ex_level = style.replace("omega_ex", "")
    level_num = int(ex_level) if ex_level.isdigit() else 1
    
    # 环绕的 EX 粒子数量基于等级
    for p in range(level_num * 3 + 3):
        p_angle = (p * (360 / (level_num * 3 + 3)) - t * 50) * 0.01745
        p_r = 35
        px = 60 + math.cos(p_angle) * p_r
        py = 60 + math.sin(p_angle) * p_r
        pygame.draw.circle(s, main_color, (int(px), int(py)), 3)


__all__ = ['render_omega_skin', 'is_omega_style', 'OMEGA_STYLES']
