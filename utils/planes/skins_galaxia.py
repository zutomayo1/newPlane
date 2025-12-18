"""
宇宙之弧·Galaxia 专属涂装系统
泰拉瑞亚武器改造机体系列 - 第一架
基于 Ark of the Cosmos 的剪刀变形机甲
"""
import pygame
import math
import random

# ==================== 涂装主题定义 ====================
GALAXIA_THEMES = {
    "default": {
        "name": "午夜星河",
        "primary": (80, 100, 200),       # 午夜蓝
        "secondary": (120, 80, 200),     # 紫罗兰
        "accent": (200, 150, 255),       # 淡紫
        "glow": (150, 200, 255),         # 星光蓝
        "trail": (100, 120, 255),        # 星云尾迹
        "blade_upper": (60, 80, 180),    # 上刃深蓝
        "blade_lower": (40, 20, 80),     # 下刃虚空黑
        "nebula": (140, 100, 220),       # 星云紫
        "constellation": (255, 255, 200), # 星座金
        "stardust": (200, 220, 255),     # 星尘白
        "cosmic_vein": (100, 180, 255),  # 宇宙纹理
    },
    "solar": {
        "name": "太阳风暴",
        "primary": (255, 180, 50),
        "secondary": (255, 100, 0),
        "accent": (255, 220, 100),
        "glow": (255, 200, 80),
        "trail": (255, 150, 0),
        "blade_upper": (255, 160, 30),
        "blade_lower": (200, 80, 0),
        "nebula": (255, 140, 50),
        "constellation": (255, 255, 150),
        "stardust": (255, 230, 180),
        "cosmic_vein": (255, 200, 100),
    },
    "nebula": {
        "name": "星云柱",
        "primary": (255, 100, 200),
        "secondary": (200, 50, 150),
        "accent": (255, 150, 255),
        "glow": (255, 180, 255),
        "trail": (200, 80, 160),
        "blade_upper": (220, 80, 180),
        "blade_lower": (150, 40, 120),
        "nebula": (230, 100, 200),
        "constellation": (255, 200, 255),
        "stardust": (255, 220, 255),
        "cosmic_vein": (200, 120, 200),
    },
    "vortex": {
        "name": "旋涡柱",
        "primary": (0, 255, 200),
        "secondary": (0, 180, 150),
        "accent": (100, 255, 255),
        "glow": (150, 255, 255),
        "trail": (0, 200, 150),
        "blade_upper": (0, 220, 180),
        "blade_lower": (0, 120, 100),
        "nebula": (50, 200, 180),
        "constellation": (200, 255, 255),
        "stardust": (220, 255, 255),
        "cosmic_vein": (100, 220, 200),
    },
    "stardust": {
        "name": "星尘柱",
        "primary": (100, 180, 255),
        "secondary": (50, 140, 220),
        "accent": (200, 220, 255),
        "glow": (180, 210, 255),
        "trail": (80, 160, 240),
        "blade_upper": (80, 160, 240),
        "blade_lower": (40, 100, 180),
        "nebula": (100, 170, 240),
        "constellation": (220, 240, 255),
        "stardust": (240, 250, 255),
        "cosmic_vein": (150, 200, 255),
    },
    "crimson": {
        "name": "猩红噩梦",
        "primary": (200, 30, 60),
        "secondary": (150, 20, 40),
        "accent": (255, 60, 90),
        "glow": (255, 100, 120),
        "trail": (180, 30, 50),
        "blade_upper": (180, 30, 60),
        "blade_lower": (120, 15, 30),
        "nebula": (160, 30, 60),
        "constellation": (255, 150, 150),
        "stardust": (255, 200, 200),
        "cosmic_vein": (200, 80, 100),
        "flesh": (180, 30, 50),
        "bone": (220, 200, 180),
        "blood": (200, 30, 60),
    },
    "corruption": {
        "name": "腐化深渊",
        "primary": (150, 80, 200),
        "secondary": (100, 50, 150),
        "accent": (180, 120, 255),
        "glow": (200, 150, 255),
        "trail": (120, 60, 180),
        "blade_upper": (130, 70, 190),
        "blade_lower": (80, 40, 120),
        "nebula": (140, 80, 200),
        "constellation": (220, 200, 255),
        "stardust": (240, 230, 255),
        "cosmic_vein": (160, 120, 220),
    },
    "hallowed": {
        "name": "神圣之辉",
        "primary": (255, 255, 255),
        "secondary": (220, 220, 255),
        "accent": (255, 255, 200),
        "glow": (255, 255, 255),
        "trail": (230, 230, 255),
        "blade_upper": (240, 240, 255),
        "blade_lower": (200, 200, 230),
        "nebula": (230, 230, 255),
        "constellation": (255, 255, 180),
        "stardust": (255, 255, 240),
        "cosmic_vein": (220, 220, 255),
    },
    "lunar": {
        "name": "月耀天体",
        "primary": (150, 180, 255),
        "secondary": (100, 140, 220),
        "accent": (200, 220, 255),
        "glow": (220, 230, 255),
        "trail": (120, 160, 240),
        "blade_upper": (140, 170, 250),
        "blade_lower": (80, 110, 180),
        "nebula": (130, 160, 230),
        "constellation": (240, 245, 255),
        "stardust": (250, 252, 255),
        "cosmic_vein": (180, 200, 255),
    },
    "zenith": {
        "name": "天顶之刃",
        "primary": (255, 255, 150),
        "secondary": (255, 220, 100),
        "accent": (255, 255, 200),
        "glow": (255, 255, 220),
        "trail": (240, 240, 120),
        "blade_upper": (250, 250, 140),
        "blade_lower": (220, 200, 80),
        "nebula": (240, 230, 130),
        "constellation": (255, 255, 180),
        "stardust": (255, 255, 230),
        "cosmic_vein": (240, 240, 160),
    },
    "rainbow": {
        "name": "彩虹水晶",
        "primary": (255, 100, 200),
        "secondary": (200, 150, 255),
        "accent": (150, 200, 255),
        "glow": (255, 200, 255),
        "trail": (200, 100, 255),
        "blade_upper": (255, 150, 200),
        "blade_lower": (150, 100, 255),
        "nebula": (200, 150, 255),
        "constellation": (255, 255, 200),
        "stardust": (255, 230, 255),
        "cosmic_vein": (220, 180, 255),
    },
    "void": {
        "name": "虚空撕裂",
        "primary": (100, 50, 150),
        "secondary": (60, 30, 100),
        "accent": (150, 100, 200),
        "glow": (180, 130, 255),
        "trail": (80, 40, 120),
        "blade_upper": (90, 50, 140),
        "blade_lower": (40, 20, 70),
        "nebula": (100, 60, 160),
        "constellation": (200, 180, 255),
        "stardust": (220, 210, 255),
        "cosmic_vein": (130, 90, 190),
    },
}

# ==================== 辅助函数 ====================
def get_galaxia_theme(style_name):
    """获取GALAXIA涂装主题"""
    return GALAXIA_THEMES.get(style_name, GALAXIA_THEMES["default"])

def is_galaxia_style(style_name):
    """判断是否为GALAXIA涂装"""
    return style_name in GALAXIA_THEMES or style_name.startswith("galaxia_")

def get_all_galaxia_styles():
    """获取所有GALAXIA涂装列表"""
    return list(GALAXIA_THEMES.keys())

# ==================== 机体渲染函数 ====================
def render_galaxia_plane(surface, color, x, y, w, h, frame, style="galaxia_default"):
    """
    渲染GALAXIA机体 - 宇宙之弧剪刀变形机甲
    超精细版本 - 包含多层视觉系统
    """
    if style.startswith("galaxia_"):
        theme_name = style[8:]
    else:
        theme_name = style if style in GALAXIA_THEMES else "default"
    
    theme = get_galaxia_theme(theme_name)
    cx = x + w // 2
    cy = y + h // 2
    scale = min(w, h) / 100 * 2.0  # 放大到2.0倍，强烈压迫感
    t = frame * 0.05
    
    # ============================================================
    #   第一层：远景星云背景 - 螺旋星云尾迹
    # ============================================================
    for spiral_arm in range(3):  # 3个螺旋臂
        arm_offset = spiral_arm * 2.09  # 120度分布
        for trail in range(25):
            trail_progress = (t * 1.5 + trail * 0.12 + arm_offset) % 6.28
            trail_dist = 25 + trail * 2.5
            trail_x = cx + int(math.cos(trail_progress) * trail_dist * scale)
            trail_y = cy + int(math.sin(trail_progress) * trail_dist * scale * 0.5)
            trail_size = max(1, int((25 - trail) / 5))
            trail_alpha = max(0, 120 - trail * 5)
            if trail_alpha > 0:
                pygame.draw.circle(surface, (*theme["nebula"], trail_alpha), 
                                 (trail_x, trail_y), trail_size)
                # 星云内核
                if trail < 10:
                    pygame.draw.circle(surface, (*theme["glow"], trail_alpha // 2), 
                                     (trail_x, trail_y), trail_size // 2)
    
    # ============================================================
    #   第二层：环绕星尘粒子云 - 双层轨道
    # ============================================================
    for orbit in range(2):  # 内外两层轨道
        orbit_radius = 35 + orbit * 15
        particle_count = 25 + orbit * 10
        for star in range(particle_count):
            star_angle = t * (1.8 - orbit * 0.3) + star * (6.28 / particle_count)
            star_dist = orbit_radius + 8 * math.sin(t * 4 + star * 0.4)
            star_x = cx + int(math.cos(star_angle) * star_dist * scale)
            star_y = cy + int(math.sin(star_angle) * star_dist * scale * 0.45)
            star_pulse = 0.6 + 0.4 * math.sin(t * 7 + star * 1.2)
            star_size = max(1, int((2 + orbit) * star_pulse))
            star_alpha = int((160 - orbit * 30) * star_pulse)
            # 星尘粒子
            pygame.draw.circle(surface, (*theme["stardust"], star_alpha), 
                             (star_x, star_y), star_size)
            # 亮点闪烁
            if star % 5 == 0:
                pygame.draw.circle(surface, (*theme["glow"], star_alpha), 
                                 (star_x, star_y), 1)
    
    # ============================================================
    #   第三层：星座投影 - 五芒星阵
    # ============================================================
    constellation_points = []
    for point in range(5):
        point_angle = t * 0.3 + point * (6.28 / 5)
        point_dist = 50 * scale
        point_x = cx + int(math.cos(point_angle) * point_dist)
        point_y = cy + int(math.sin(point_angle) * point_dist * 0.4)
        constellation_points.append((point_x, point_y))
        # 星座节点
        node_pulse = 0.7 + 0.3 * math.sin(t * 5 + point)
        node_size = int(4 * node_pulse)
        pygame.draw.circle(surface, (*theme["constellation"], 200), 
                         (point_x, point_y), node_size)
        pygame.draw.circle(surface, (*theme["constellation"], 100), 
                         (point_x, point_y), node_size + 3)
    
    # 连接星座线（五芒星）
    for i in range(5):
        start_pt = constellation_points[i]
        end_pt = constellation_points[(i + 2) % 5]
        line_alpha = int(150 * (0.8 + 0.2 * math.sin(t * 3 + i)))
        pygame.draw.line(surface, (*theme["constellation"], line_alpha), 
                       start_pt, end_pt, 1)
    
    # ============================================================
    #   主题差异化特效层 - 每个涂装独特的视觉系统
    # ============================================================
    if theme_name == "solar":
        # ====== 太阳风暴：日冕环+耀斑爆发+太阳黑子+日珥+光球层 ======
        # 光球层（底层脉动）
        photosphere_pulse = 0.9 + 0.1 * math.sin(t * 3)
        photosphere_r = int(35 * scale * photosphere_pulse)
        for layer in range(5):
            layer_r = photosphere_r - layer * int(3 * scale)
            layer_alpha = 60 + layer * 10
            pygame.draw.circle(surface, (*theme["primary"], layer_alpha), (cx, cy), layer_r)
        
        # 日冕环（多层旋转）
        for ring_set in range(3):
            ring_offset = ring_set * 2.09
            for ring in range(3):
                ring_r = int((45 + ring * 15 + ring_set * 5) * scale)
                ring_w = int((8 - ring * 2) * scale)
                for arc in range(12):
                    arc_start = arc * (math.pi / 6) + t * (0.5 + ring_set * 0.2) + ring_offset
                    arc_end = arc_start + math.pi / 8
                    arc_alpha = 100 - ring * 25 - ring_set * 10
                    if arc_alpha > 0:
                        pygame.draw.arc(surface, (*theme["primary"], arc_alpha),
                                      (cx - ring_r, cy - ring_r // 2, ring_r * 2, ring_r),
                                      arc_start, arc_end, ring_w)
        
        # 耀斑爆发（八向+分叉）
        for flare_dir in range(8):
            flare_angle = t * 2 + flare_dir * (math.pi / 4)
            flare_intensity = 0.8 + 0.2 * math.sin(t * 4 + flare_dir)
            flare_base_len = int((30 + 20 * math.sin(t * 4 + flare_dir)) * scale * flare_intensity)
            
            # 主耀斑
            for f in range(8):
                f_progress = f / 8
                fx = cx + int(math.cos(flare_angle) * (flare_base_len * f_progress))
                fy = cy + int(math.sin(flare_angle) * (flare_base_len * f_progress) * 0.4)
                f_size = int((8 - f) * scale * flare_intensity)
                f_alpha = int((220 - f * 25) * flare_intensity)
                if f_alpha > 0:
                    pygame.draw.circle(surface, (*theme["accent"], f_alpha), (fx, fy), f_size)
                    # 内核
                    if f < 5:
                        pygame.draw.circle(surface, (*theme["glow"], f_alpha + 30), (fx, fy), f_size // 2)
            
            # 耀斑分叉
            if flare_dir % 2 == 0:
                for branch in [-1, 1]:
                    branch_angle = flare_angle + branch * (math.pi / 8)
                    branch_len = flare_base_len * 0.6
                    for b in range(5):
                        b_progress = b / 5
                        bx = cx + int(math.cos(branch_angle) * (branch_len * b_progress))
                        by = cy + int(math.sin(branch_angle) * (branch_len * b_progress) * 0.4)
                        b_alpha = int((180 - b * 35) * flare_intensity)
                        if b_alpha > 0:
                            pygame.draw.circle(surface, (*theme["accent"], b_alpha), (bx, by), max(1, int((5 - b) * scale)))
        
        # 太阳黑子（旋转+脉动）
        for spot_ring in range(2):
            spot_count = 6 + spot_ring * 3
            spot_dist = (20 + spot_ring * 12) * scale
            for spot in range(spot_count):
                spot_angle = t * (1.5 - spot_ring * 0.5) + spot * (6.28 / spot_count)
                spot_pulse = 0.8 + 0.2 * math.sin(t * 5 + spot)
                spot_x = cx + int(math.cos(spot_angle) * spot_dist)
                spot_y = cy + int(math.sin(spot_angle) * spot_dist * 0.4)
                spot_size = int((4 + spot_ring) * scale * spot_pulse)
                # 黑子核心
                pygame.draw.circle(surface, (50, 30, 0, 200), (spot_x, spot_y), spot_size)
                # 黑子边缘（橙色）
                pygame.draw.circle(surface, (*theme["secondary"], 180), (spot_x, spot_y), spot_size, 1)
                # 半影
                pygame.draw.circle(surface, (*theme["primary"], 80), (spot_x, spot_y), int(spot_size * 1.5))
        
        # 日珥（边缘喷发）
        for prominence in range(6):
            prom_angle = prominence * (math.pi / 3) + t * 0.3
            prom_base_x = cx + int(math.cos(prom_angle) * 40 * scale)
            prom_base_y = cy + int(math.sin(prom_angle) * 40 * scale * 0.4)
            # 日珥弧线
            prom_points = []
            for seg in range(8):
                seg_progress = seg / 8
                arc_height = math.sin(seg_progress * math.pi) * 15 * scale
                seg_angle = prom_angle + math.pi / 2
                px = prom_base_x + int(math.cos(seg_angle) * seg_progress * 20 * scale)
                py = prom_base_y + int(math.sin(seg_angle) * seg_progress * 20 * scale * 0.4) - int(arc_height)
                prom_points.append((px, py))
            if len(prom_points) > 1:
                prom_alpha = int(150 + 100 * math.sin(t * 3 + prominence))
                pygame.draw.lines(surface, (*theme["accent"], prom_alpha), False, prom_points, int(3 * scale))
                # 日珥粒子
                for i, pt in enumerate(prom_points):
                    if i % 2 == 0:
                        pygame.draw.circle(surface, (*theme["glow"], prom_alpha), pt, int(2 * scale))
        
        # 太阳风粒子流
        for wind in range(20):
            wind_angle = t * 3 + wind * 0.3
            wind_dist = int((40 + ((t * 40 + wind * 5) % 40)) * scale)
            wind_x = cx + int(math.cos(wind_angle) * wind_dist)
            wind_y = cy + int(math.sin(wind_angle) * wind_dist * 0.35)
            wind_alpha = 200 - int(((t * 40 + wind * 5) % 40) * 4)
            if wind_alpha > 0:
                pygame.draw.circle(surface, (*theme["stardust"], wind_alpha), (wind_x, wind_y), max(1, int(2 * scale)))
                # 拖尾
                trail_x = cx + int(math.cos(wind_angle) * (wind_dist - 5 * scale))
                trail_y = cy + int(math.sin(wind_angle) * (wind_dist - 5 * scale) * 0.35)
                pygame.draw.line(surface, (*theme["stardust"], wind_alpha // 2), (trail_x, trail_y), (wind_x, wind_y), 1)
        
        # 色球层爆发（底部火舌）
        for tongue in range(12):
            tongue_angle = tongue * (math.pi / 6) + t * 2
            tongue_base_r = 30 * scale
            tongue_height = (8 + 5 * math.sin(t * 6 + tongue)) * scale
            tongue_x_base = cx + int(math.cos(tongue_angle) * tongue_base_r)
            tongue_y_base = cy + int(math.sin(tongue_angle) * tongue_base_r * 0.35)
            tongue_x_tip = cx + int(math.cos(tongue_angle) * (tongue_base_r + tongue_height))
            tongue_y_tip = cy + int(math.sin(tongue_angle) * (tongue_base_r + tongue_height) * 0.35)
            tongue_alpha = int(180 + 70 * math.sin(t * 8 + tongue))
            pygame.draw.line(surface, (*theme["secondary"], tongue_alpha), 
                           (tongue_x_base, tongue_y_base), (tongue_x_tip, tongue_y_tip), int(2 * scale))
        
        # 磁场线（弧形连接）
        magnetic_nodes = []
        for node in range(8):
            node_angle = node * (math.pi / 4)
            node_x = cx + int(math.cos(node_angle) * 35 * scale)
            node_y = cy + int(math.sin(node_angle) * 35 * scale * 0.35)
            magnetic_nodes.append((node_x, node_y))
        for i in range(len(magnetic_nodes)):
            for j in range(i + 2, min(i + 4, len(magnetic_nodes))):
                if (int(t * 10) + i + j) % 3 == 0:
                    mid_x = (magnetic_nodes[i][0] + magnetic_nodes[j][0]) // 2
                    mid_y = (magnetic_nodes[i][1] + magnetic_nodes[j][1]) // 2 - int(10 * scale)
                    mag_alpha = int(100 + 80 * math.sin(t * 4 + i + j))
                    # 绘制弧线（用3段直线近似）
                    pygame.draw.line(surface, (*theme["primary"], mag_alpha), magnetic_nodes[i], (mid_x, mid_y), 1)
                    pygame.draw.line(surface, (*theme["primary"], mag_alpha), (mid_x, mid_y), magnetic_nodes[j], 1)
    
    elif theme_name == "nebula":
        # ====== 星云柱：灵能波纹+粉紫云团+能量脉冲+星云涡旋+灵能闪电 ======
        # 灵能波纹（多层扩散）
        for wave_set in range(3):
            wave_phase = (t * (3 - wave_set * 0.5) + wave_set * 0.33) % 1.0
            for wave in range(5):
                wave_r = int((15 + (wave_phase + wave * 0.2) * 70) * scale)
                wave_alpha = int(180 * (1 - (wave_phase + wave * 0.2) % 1.0) * (1 - wave_set * 0.2))
                if wave_alpha > 20:
                    # 波纹圆环
                    pygame.draw.circle(surface, (*theme["nebula"], wave_alpha), (cx, cy), wave_r, int((3 - wave_set) * scale))
                    # 波纹光点
                    for dot in range(12):
                        dot_angle = dot * (math.pi / 6) + wave_phase * 6.28
                        dot_x = cx + int(math.cos(dot_angle) * wave_r)
                        dot_y = cy + int(math.sin(dot_angle) * wave_r * 0.35)
                        pygame.draw.circle(surface, (*theme["accent"], wave_alpha), (dot_x, dot_y), int(2 * scale))
        
        # 粉紫云团（多层浮动）
        for cloud_layer in range(3):
            cloud_count = 8 + cloud_layer * 4
            cloud_dist_base = (25 + cloud_layer * 15) * scale
            for cloud in range(cloud_count):
                cloud_angle = t * (0.8 - cloud_layer * 0.2) + cloud * (6.28 / cloud_count)
                cloud_dist = cloud_dist_base + 10 * math.sin(t * 2 + cloud) * scale
                cloud_x = cx + int(math.cos(cloud_angle) * cloud_dist)
                cloud_y = cy + int(math.sin(cloud_angle) * cloud_dist * 0.35)
                cloud_pulse = 0.7 + 0.3 * math.sin(t * 3 + cloud)
                cloud_size = int((10 - cloud_layer * 2 + 4 * math.sin(t * 3 + cloud)) * scale * cloud_pulse)
                
                # 云团主体（多层）
                for c_layer in range(3):
                    c_size = cloud_size - c_layer * int(2 * scale)
                    c_alpha = (120 - cloud_layer * 20) - c_layer * 20
                    if c_size > 0 and c_alpha > 0:
                        pygame.draw.circle(surface, (*theme["nebula"], c_alpha), (cloud_x, cloud_y), c_size)
                
                # 云团核心
                core_size = cloud_size // 2
                core_alpha = 100 - cloud_layer * 15
                pygame.draw.circle(surface, (*theme["accent"], core_alpha), (cloud_x, cloud_y), core_size)
                
                # 云团粒子
                for particle in range(5):
                    p_angle = particle * (6.28 / 5) + t * 4
                    p_dist = cloud_size * 0.8
                    p_x = cloud_x + int(math.cos(p_angle) * p_dist)
                    p_y = cloud_y + int(math.sin(p_angle) * p_dist * 0.5)
                    pygame.draw.circle(surface, (*theme["stardust"], 150), (p_x, p_y), max(1, int(1 * scale)))
        
        # 能量脉冲线（交叉网格）
        for pulse_h in range(5):
            p_y = cy - int(40 * scale) + pulse_h * int(20 * scale)
            pulse_progress = (t * 5 + pulse_h * 0.3) % 1.0
            p_x = cx - int(50 * scale) + int(pulse_progress * 100 * scale)
            pulse_alpha = int(220 * (1 - abs(pulse_progress - 0.5) * 2))
            if pulse_alpha > 0:
                pygame.draw.circle(surface, (*theme["glow"], pulse_alpha), (p_x, p_y), int(4 * scale))
                # 拖尾
                for trail in range(5):
                    trail_x = p_x - trail * int(4 * scale)
                    trail_alpha = int(pulse_alpha * (1 - trail * 0.2))
                    pygame.draw.circle(surface, (*theme["accent"], trail_alpha), (trail_x, p_y), max(1, int((4 - trail) * scale)))
        
        # 垂直脉冲
        for pulse_v in range(4):
            p_x = cx - int(30 * scale) + pulse_v * int(20 * scale)
            pulse_progress = (t * 4 + pulse_v * 0.4) % 1.0
            p_y = cy - int(40 * scale) + int(pulse_progress * 80 * scale)
            pulse_alpha = int(200 * (1 - abs(pulse_progress - 0.5) * 2))
            if pulse_alpha > 0:
                pygame.draw.circle(surface, (*theme["glow"], pulse_alpha), (p_x, p_y), int(3 * scale))
        
        # 星云涡旋（螺旋臂）
        for arm in range(4):
            arm_offset = arm * (math.pi / 2)
            for seg in range(20):
                seg_progress = seg / 20
                spiral_angle = arm_offset + seg_progress * math.pi * 2 + t * 1.5
                spiral_dist = int(seg_progress * 45 * scale)
                spiral_x = cx + int(math.cos(spiral_angle) * spiral_dist)
                spiral_y = cy + int(math.sin(spiral_angle) * spiral_dist * 0.35)
                spiral_alpha = int(180 * (1 - seg_progress))
                if spiral_alpha > 0:
                    spiral_size = int((5 - seg_progress * 3) * scale)
                    pygame.draw.circle(surface, (*theme["nebula"], spiral_alpha), (spiral_x, spiral_y), spiral_size)
        
        # 灵能闪电（节点连接）
        psi_nodes = []
        for node in range(10):
            node_angle = t * 1.2 + node * (6.28 / 10)
            node_dist = int((25 + 15 * math.sin(t * 2 + node)) * scale)
            node_x = cx + int(math.cos(node_angle) * node_dist)
            node_y = cy + int(math.sin(node_angle) * node_dist * 0.35)
            psi_nodes.append((node_x, node_y))
            # 节点光球
            node_pulse = 0.7 + 0.3 * math.sin(t * 6 + node)
            pygame.draw.circle(surface, (*theme["accent"], int(220 * node_pulse)), (node_x, node_y), int(4 * scale * node_pulse))
            pygame.draw.circle(surface, (*theme["glow"], 250), (node_x, node_y), int(2 * scale))
        
        # 闪电连接
        for i in range(len(psi_nodes)):
            for j in range(i + 1, len(psi_nodes)):
                if abs(i - j) <= 3 and (int(t * 15) + i + j) % 4 == 0:
                    # 锯齿闪电
                    lightning_segs = 6
                    last_pt = psi_nodes[i]
                    for ls in range(lightning_segs):
                        ls_progress = (ls + 1) / lightning_segs
                        base_x = int(psi_nodes[i][0] + (psi_nodes[j][0] - psi_nodes[i][0]) * ls_progress)
                        base_y = int(psi_nodes[i][1] + (psi_nodes[j][1] - psi_nodes[i][1]) * ls_progress)
                        zigzag = int(math.sin(ls * 2 + t * 20) * 6 * scale)
                        pt = (base_x + zigzag, base_y)
                        lightning_alpha = int(200 + 50 * math.sin(t * 12 + i + j))
                        pygame.draw.line(surface, (*theme["glow"], lightning_alpha), last_pt, pt, int(2 * scale))
                        last_pt = pt
        
        # 灵能符文（旋转）
        for rune in range(8):
            rune_angle = t * -1.5 + rune * (math.pi / 4)
            rune_dist = 40 * scale
            rune_x = cx + int(math.cos(rune_angle) * rune_dist)
            rune_y = cy + int(math.sin(rune_angle) * rune_dist * 0.35)
            rune_alpha = int(180 + 70 * math.sin(t * 4 + rune))
            # 符文形状（三角）
            rune_points = []
            for p in range(3):
                p_angle = rune_angle + p * (6.28 / 3)
                p_dist = 5 * scale
                px = rune_x + int(math.cos(p_angle) * p_dist)
                py = rune_y + int(math.sin(p_angle) * p_dist * 0.5)
                rune_points.append((px, py))
            if len(rune_points) > 2:
                pygame.draw.polygon(surface, (*theme["accent"], rune_alpha), rune_points, int(2 * scale))
                pygame.draw.circle(surface, (*theme["glow"], rune_alpha), (rune_x, rune_y), int(3 * scale))
    
    elif theme_name == "vortex":
        # ====== 旋涡柱：时空漩涡+扭曲场+虫洞+引力波+时间裂痕 ======
        # 时空漩涡（三层螺旋）
        for spiral_layer in range(3):
            spiral_density = 35 - spiral_layer * 5
            spiral_speed = 3 - spiral_layer * 0.8
            for spiral in range(spiral_density):
                s_progress = spiral / spiral_density
                s_angle = t * spiral_speed + spiral * (6.28 / spiral_density * 3) + spiral_layer * 2.09
                s_dist = int((5 + s_progress * (55 - spiral_layer * 10)) * scale)
                sx = cx + int(math.cos(s_angle) * s_dist)
                sy = cy + int(math.sin(s_angle) * s_dist * 0.35)
                s_alpha = int((220 - spiral_layer * 40) * (1 - s_progress))
                if s_alpha > 0:
                    s_size = max(1, int((4 - s_progress * 2 - spiral_layer) * scale))
                    pygame.draw.circle(surface, (*theme["primary"], s_alpha), (sx, sy), s_size)
                    # 轨迹连接
                    if spiral > 0:
                        prev_angle = s_angle - (6.28 / spiral_density * 3)
                        prev_dist = int((5 + (spiral - 1) / spiral_density * (55 - spiral_layer * 10)) * scale)
                        prev_x = cx + int(math.cos(prev_angle) * prev_dist)
                        prev_y = cy + int(math.sin(prev_angle) * prev_dist * 0.35)
                        pygame.draw.line(surface, (*theme["primary"], s_alpha // 2), (prev_x, prev_y), (sx, sy), 1)
        
        # 扭曲场（波动圆环）
        for wave_ring in range(8):
            wave_points = []
            wave_r = int((20 + wave_ring * 6) * scale)
            for seg in range(32):
                seg_angle = seg * (math.pi / 16)
                distort_freq = 5 + wave_ring
                distort_amp = (5 - wave_ring * 0.5) * scale
                distort = math.sin(seg_angle * distort_freq + t * (8 + wave_ring)) * distort_amp
                wx = cx + int(math.cos(seg_angle) * (wave_r + distort))
                wy = cy + int(math.sin(seg_angle) * (wave_r + distort) * 0.35)
                wave_points.append((wx, wy))
            if len(wave_points) > 2:
                wave_alpha = 170 - wave_ring * 20
                pygame.draw.lines(surface, (*theme["accent"], wave_alpha), True, wave_points, 1)
        
        # 虫洞核心（黑洞效果）
        for hole_ring in range(8):
            hole_r = int((18 - hole_ring * 2.2) * scale)
            if hole_r > 0:
                hole_alpha = 80 + hole_ring * 20
                hole_color_factor = hole_ring / 8
                hole_color = tuple(int(c * (1 - hole_color_factor * 0.8)) for c in theme["secondary"])
                pygame.draw.circle(surface, (*hole_color, hole_alpha), (cx, cy), hole_r)
        # 虫洞事件视界
        event_horizon_r = int(15 * scale)
        pygame.draw.circle(surface, (0, 0, 0, 250), (cx, cy), event_horizon_r)
        pygame.draw.circle(surface, (*theme["glow"], 200), (cx, cy), event_horizon_r, int(2 * scale))
        
        # 引力波（脉冲环）
        gravity_wave_phase = (t * 2) % 1.0
        for gw in range(4):
            gw_r = int((event_horizon_r + (gravity_wave_phase + gw * 0.25) * 50) * scale)
            gw_alpha = int(200 * (1 - (gravity_wave_phase + gw * 0.25) % 1.0))
            if gw_alpha > 20:
                pygame.draw.circle(surface, (*theme["accent"], gw_alpha), (cx, cy), gw_r, int(3 * scale))
        
        # 时间裂痕（扭曲线条）
        for crack in range(6):
            crack_angle = crack * (math.pi / 3) + t * 0.3
            crack_points = [(cx, cy)]
            for seg in range(12):
                seg_progress = (seg + 1) / 12
                seg_dist = int(seg_progress * 45 * scale)
                time_distort = math.sin(t * 8 + seg * 2 + crack) * 8 * scale
                crack_x = cx + int(math.cos(crack_angle) * seg_dist + time_distort)
                crack_y = cy + int(math.sin(crack_angle) * seg_dist * 0.35)
                crack_points.append((crack_x, crack_y))
            if len(crack_points) > 1:
                crack_alpha = int(190 + 60 * math.sin(t * 3 + crack))
                pygame.draw.lines(surface, (*theme["glow"], crack_alpha), False, crack_points, int(2 * scale))
                # 裂痕发光
                for i, pt in enumerate(crack_points):
                    if i % 2 == 0:
                        glow_pulse = 0.6 + 0.4 * math.sin(t * 10 + i + crack)
                        pygame.draw.circle(surface, (*theme["accent"], int(200 * glow_pulse)), pt, int(3 * scale))
        
        # 被吸入的碎片（螺旋向内）
        for debris in range(20):
            debris_life = ((t * 20 + debris * 3) % 60) / 60
            debris_angle = debris * 0.9 + t * 4
            debris_dist = int((50 - debris_life * 50) * scale)
            if debris_dist > event_horizon_r:
                debris_x = cx + int(math.cos(debris_angle) * debris_dist)
                debris_y = cy + int(math.sin(debris_angle) * debris_dist * 0.35)
                debris_alpha = int(200 * debris_life)
                debris_size = int((3 - debris_life * 2) * scale)
                if debris_alpha > 0 and debris_size > 0:
                    pygame.draw.circle(surface, (*theme["stardust"], debris_alpha), (debris_x, debris_y), debris_size)
                    # 拉伸效果
                    stretch_x = debris_x + int(math.cos(debris_angle) * 5 * scale * debris_life)
                    stretch_y = debris_y + int(math.sin(debris_angle) * 5 * scale * 0.35 * debris_life)
                    pygame.draw.line(surface, (*theme["stardust"], debris_alpha // 2), (debris_x, debris_y), (stretch_x, stretch_y), 1)
        
        # 奇点光环（最内层）
        singularity_glow = 0.8 + 0.2 * math.sin(t * 15)
        for sg in range(5):
            sg_r = int((8 + sg * 2) * scale * singularity_glow)
            sg_alpha = 220 - sg * 40
            pygame.draw.circle(surface, (*theme["glow"], sg_alpha), (cx, cy), sg_r, 1)
    
    elif theme_name == "stardust":
        # ====== 星尘柱：星龙环绕+龙鳞+星尘流+龙息+龙珠+星辰之眼 ======
        # 星龙环绕（双龙盘绕）
        for dragon_id in range(2):
            dragon_offset = dragon_id * math.pi
            dragon_speed = 1.2 + dragon_id * 0.3
            # 龙身节点
            dragon_nodes = []
            for seg in range(25):
                seg_progress = seg / 25
                coil_angle = dragon_offset + t * dragon_speed + seg_progress * math.pi * 4
                coil_r = int((15 + seg_progress * 40 - seg_progress * seg_progress * 15) * scale)
                coil_height = math.sin(seg_progress * math.pi) * 15 * scale
                dx = cx + int(math.cos(coil_angle) * coil_r)
                dy = cy + int(math.sin(coil_angle) * coil_r * 0.35) - int(coil_height)
                dragon_nodes.append((dx, dy))
            
            # 绘制龙身连接
            if len(dragon_nodes) > 1:
                dragon_alpha = 200 - dragon_id * 30
                for i in range(len(dragon_nodes) - 1):
                    body_thickness = int((6 - i / 5) * scale)
                    if body_thickness > 0:
                        pygame.draw.line(surface, (*theme["secondary"], dragon_alpha), 
                                       dragon_nodes[i], dragon_nodes[i + 1], body_thickness)
            
            # 龙鳞
            for i, node in enumerate(dragon_nodes):
                if i % 2 == 0:
                    scale_size = int((5 - i / 10) * scale)
                    scale_angle = t * 5 + i
                    scale_alpha = dragon_alpha - 40
                    # 鳞片形状（菱形）
                    scale_points = []
                    for p in range(4):
                        p_angle = p * (math.pi / 2) + scale_angle
                        p_dist = scale_size * (1.5 if p % 2 == 0 else 1.0)
                        px = node[0] + int(math.cos(p_angle) * p_dist)
                        py = node[1] + int(math.sin(p_angle) * p_dist * 0.5)
                        scale_points.append((px, py))
                    if len(scale_points) == 4:
                        pygame.draw.polygon(surface, (*theme["accent"], scale_alpha), scale_points)
                        pygame.draw.polygon(surface, (*theme["glow"], scale_alpha + 50), scale_points, 1)
            
            # 龙头（最前端）
            if len(dragon_nodes) > 0:
                head_pos = dragon_nodes[-1]
                head_angle = math.atan2(dragon_nodes[-1][1] - dragon_nodes[-2][1],
                                       dragon_nodes[-1][0] - dragon_nodes[-2][0])
                # 龙眼
                for eye in [-1, 1]:
                    eye_offset = 4 * scale * eye
                    eye_x = head_pos[0] + int(math.sin(head_angle) * eye_offset)
                    eye_y = head_pos[1] - int(math.cos(head_angle) * eye_offset * 0.5)
                    pygame.draw.circle(surface, (*theme["glow"], 255), (eye_x, eye_y), int(3 * scale))
                    pygame.draw.circle(surface, (255, 255, 255, 255), (eye_x, eye_y), int(1.5 * scale))
                # 龙角
                for horn in [-1, 1]:
                    horn_angle = head_angle + horn * (math.pi / 4)
                    horn_len = 10 * scale
                    horn_tip_x = head_pos[0] + int(math.cos(horn_angle) * horn_len)
                    horn_tip_y = head_pos[1] + int(math.sin(horn_angle) * horn_len * 0.5)
                    pygame.draw.line(surface, (*theme["accent"], 220), head_pos, (horn_tip_x, horn_tip_y), int(2 * scale))
        
        # 星尘流（螺旋上升）
        for dust in range(25):
            dust_life = ((t * 30 + dust * 2) % 80) / 80
            dust_angle = dust * 0.8 + t * 2
            dust_dist = int(dust_life * 50 * scale)
            dust_height = dust_life * 30 * scale
            dust_x = cx + int(math.cos(dust_angle) * dust_dist)
            dust_y = cy + int(math.sin(dust_angle) * dust_dist * 0.35) - int(dust_height)
            dust_alpha = int(220 * (1 - dust_life))
            if dust_alpha > 0:
                dust_size = max(1, int((4 - dust_life * 3) * scale))
                pygame.draw.circle(surface, (*theme["stardust"], dust_alpha), (dust_x, dust_y), dust_size)
                # 星尘轨迹
                if dust > 0:
                    prev_life = ((t * 30 + (dust - 1) * 2) % 80) / 80
                    prev_angle = (dust - 1) * 0.8 + t * 2
                    prev_dist = int(prev_life * 50 * scale)
                    prev_height = prev_life * 30 * scale
                    prev_x = cx + int(math.cos(prev_angle) * prev_dist)
                    prev_y = cy + int(math.sin(prev_angle) * prev_dist * 0.35) - int(prev_height)
                    pygame.draw.line(surface, (*theme["stardust"], dust_alpha // 2), (prev_x, prev_y), (dust_x, dust_y), 1)
        
        # 龙息（粒子喷射）
        breath_base_angle = t * 1.5
        for breath in range(15):
            breath_angle = breath_base_angle + (breath - 7) * 0.15
            breath_progress = ((t * 25 + breath * 3) % 50) / 50
            breath_dist = int(breath_progress * 55 * scale)
            breath_x = cx + int(math.cos(breath_angle) * breath_dist)
            breath_y = cy + int(math.sin(breath_angle) * breath_dist * 0.35)
            breath_alpha = int(200 * (1 - breath_progress))
            if breath_alpha > 0:
                breath_size = int((5 - breath_progress * 4) * scale)
                if breath_size > 0:
                    # 龙息核心
                    pygame.draw.circle(surface, (*theme["accent"], breath_alpha), (breath_x, breath_y), breath_size)
                    # 龙息光晕
                    pygame.draw.circle(surface, (*theme["glow"], breath_alpha // 2), (breath_x, breath_y), breath_size * 2)
        
        # 龙珠（核心能量球）
        dragonball_pulse = 0.85 + 0.15 * math.sin(t * 8)
        for db_layer in range(6):
            db_r = int((18 - db_layer * 2.5) * scale * dragonball_pulse)
            db_alpha = 100 + db_layer * 25
            db_color_mix = db_layer / 6
            db_color = tuple(int(theme["accent"][i] * (1 - db_color_mix) + theme["glow"][i] * db_color_mix) for i in range(3))
            if db_r > 0:
                pygame.draw.circle(surface, (*db_color, db_alpha), (cx, cy), db_r)
        # 龙珠光环
        for ring in range(4):
            ring_angle = t * 3 + ring * (math.pi / 2)
            ring_dist = 12 * scale
            ring_x = cx + int(math.cos(ring_angle) * ring_dist)
            ring_y = cy + int(math.sin(ring_angle) * ring_dist * 0.4)
            pygame.draw.circle(surface, (*theme["glow"], 220), (ring_x, ring_y), int(3 * scale))
        
        # 星辰之眼（观察者）
        for eye_ring in range(3):
            eye_angle = t * (2 - eye_ring * 0.4) + eye_ring * 2.09
            eye_dist = int((35 + eye_ring * 10) * scale)
            eye_x = cx + int(math.cos(eye_angle) * eye_dist)
            eye_y = cy + int(math.sin(eye_angle) * eye_dist * 0.35)
            eye_alpha = 180 - eye_ring * 40
            # 眼睛外轮廓
            pygame.draw.circle(surface, (*theme["secondary"], eye_alpha), (eye_x, eye_y), int(6 * scale))
            # 眼珠
            pupil_pulse = 0.7 + 0.3 * math.sin(t * 6 + eye_ring)
            pygame.draw.circle(surface, (*theme["accent"], eye_alpha + 50), (eye_x, eye_y), int(4 * scale * pupil_pulse))
            # 瞳孔
            pygame.draw.circle(surface, (0, 0, 0, 250), (eye_x, eye_y), int(2 * scale))
            # 眼光
            for ray in range(4):
                ray_angle = ray * (math.pi / 2) + t * 4
                ray_len = 5 * scale
                ray_end_x = eye_x + int(math.cos(ray_angle) * ray_len)
                ray_end_y = eye_y + int(math.sin(ray_angle) * ray_len * 0.5)
                pygame.draw.line(surface, (*theme["glow"], eye_alpha), (eye_x, eye_y), (ray_end_x, ray_end_y), 1)
    
    elif theme_name == "crimson":
        # ====== 血腥：血肉藤蔓+脊椎+血管网+心脏+血液飞溅+腐肉块 ======
        # 血肉藤蔓（有机触手）
        for vine_id in range(6):
            vine_base_angle = vine_id * (math.pi / 3)
            vine_points = [(cx, cy)]
            for seg in range(15):
                seg_progress = (seg + 1) / 15
                wave_offset = math.sin(t * 3 + seg * 0.5 + vine_id) * 8 * scale
                seg_angle = vine_base_angle + seg_progress * 0.5
                seg_dist = int(seg_progress * 45 * scale)
                seg_x = cx + int(math.cos(seg_angle) * seg_dist + wave_offset)
                seg_y = cy + int(math.sin(seg_angle) * seg_dist * 0.35)
                vine_points.append((seg_x, seg_y))
            
            # 绘制藤蔓主体
            if len(vine_points) > 1:
                vine_alpha = 200
                for i in range(len(vine_points) - 1):
                    vine_thickness = int((6 - i / 3) * scale)
                    if vine_thickness > 0:
                        pygame.draw.line(surface, (*theme["flesh"], vine_alpha), 
                                       vine_points[i], vine_points[i + 1], vine_thickness)
            
            # 藤蔓上的刺（每隔2节）
            for i, pt in enumerate(vine_points):
                if i % 2 == 0 and i > 0:
                    for thorn_side in [-1, 1]:
                        thorn_angle = math.atan2(pt[1] - vine_points[i - 1][1],
                                                pt[0] - vine_points[i - 1][0]) + thorn_side * (math.pi / 2)
                        thorn_len = (5 - i / 5) * scale
                        thorn_tip_x = pt[0] + int(math.cos(thorn_angle) * thorn_len)
                        thorn_tip_y = pt[1] + int(math.sin(thorn_angle) * thorn_len * 0.5)
                        pygame.draw.line(surface, (*theme["accent"], 220), pt, (thorn_tip_x, thorn_tip_y), int(2 * scale))
                        # 刺尖
                        pygame.draw.circle(surface, (*theme["glow"], 255), (thorn_tip_x, thorn_tip_y), max(1, int(1.5 * scale)))
        
        # 脊椎骨（中轴骨架）
        vertebrae_count = 12
        for v in range(vertebrae_count):
            v_angle = t * 1.5 + v * 0.3
            v_dist = int((10 + v * 3) * scale)
            v_x = cx
            v_y = cy - int(v_dist) + int(40 * scale)
            v_pulse = 0.9 + 0.1 * math.sin(t * 8 + v)
            # 椎骨主体（椭圆）
            v_w = int(8 * scale * v_pulse)
            v_h = int(6 * scale * v_pulse)
            pygame.draw.ellipse(surface, (*theme["bone"], 220), (v_x - v_w // 2, v_y - v_h // 2, v_w, v_h))
            pygame.draw.ellipse(surface, (*theme["flesh"], 180), (v_x - v_w // 2, v_y - v_h // 2, v_w, v_h), 1)
            # 横突（左右伸出）
            for side in [-1, 1]:
                process_len = 6 * scale
                process_end_x = v_x + int(side * process_len)
                pygame.draw.line(surface, (*theme["bone"], 200), (v_x, v_y), (process_end_x, v_y), int(2 * scale))
        
        # 血管网络（脉动网格）
        blood_nodes = []
        for node_ring in range(3):
            node_count = 6 + node_ring * 2
            node_dist = (20 + node_ring * 12) * scale
            for node in range(node_count):
                node_angle = node * (6.28 / node_count) + t * (0.5 - node_ring * 0.1)
                node_x = cx + int(math.cos(node_angle) * node_dist)
                node_y = cy + int(math.sin(node_angle) * node_dist * 0.35)
                blood_nodes.append((node_x, node_y))
                # 血管节点（脉冲）
                node_pulse = 0.7 + 0.3 * math.sin(t * 6 + node_ring + node)
                pygame.draw.circle(surface, (*theme["blood"], int(220 * node_pulse)), (node_x, node_y), int(3 * scale * node_pulse))
        
        # 连接血管
        for i in range(len(blood_nodes)):
            for j in range(i + 1, min(i + 4, len(blood_nodes))):
                if (i + j) % 3 == 0:
                    vessel_alpha = int(150 + 80 * math.sin(t * 4 + i + j))
                    vessel_pulse = 1.0 + 0.2 * math.sin(t * 8 + i)
                    vessel_thickness = max(1, int(2 * scale * vessel_pulse))
                    pygame.draw.line(surface, (*theme["blood"], vessel_alpha), 
                                   blood_nodes[i], blood_nodes[j], vessel_thickness)
        
        # 心脏（核心跳动）
        heartbeat_phase = (t * 4) % 1.0
        if heartbeat_phase < 0.3:
            heartbeat_scale = 1.0 + (heartbeat_phase / 0.3) * 0.3
        elif heartbeat_phase < 0.5:
            heartbeat_scale = 1.3 - ((heartbeat_phase - 0.3) / 0.2) * 0.3
        else:
            heartbeat_scale = 1.0
        
        heart_size = int(15 * scale * heartbeat_scale)
        # 心脏主体（双瓣）
        for lobe in [-1, 1]:
            lobe_x = cx + int(lobe * 5 * scale * heartbeat_scale)
            pygame.draw.circle(surface, (*theme["flesh"], 240), (lobe_x, cy - int(3 * scale)), heart_size)
        # 心尖
        heart_tip_y = cy + int(heart_size * 1.2)
        pygame.draw.polygon(surface, (*theme["flesh"], 240), [
            (cx - heart_size, cy),
            (cx + heart_size, cy),
            (cx, heart_tip_y)
        ])
        # 心脏血管
        for artery in range(4):
            artery_angle = artery * (math.pi / 2) + t * 2
            artery_len = (heart_size + 8 * scale) * heartbeat_scale
            artery_end_x = cx + int(math.cos(artery_angle) * artery_len)
            artery_end_y = cy + int(math.sin(artery_angle) * artery_len * 0.4)
            pygame.draw.line(surface, (*theme["blood"], 220), (cx, cy), (artery_end_x, artery_end_y), int(3 * scale))
        
        # 血液飞溅（喷射粒子）
        for splatter in range(30):
            splatter_life = ((t * 50 + splatter * 3) % 100) / 100
            splatter_angle = splatter * 0.7 + math.sin(t * 3 + splatter) * 0.5
            splatter_dist = int(splatter_life * 60 * scale)
            splatter_x = cx + int(math.cos(splatter_angle) * splatter_dist)
            splatter_y = cy + int(math.sin(splatter_angle) * splatter_dist * 0.35) - int(splatter_life * splatter_life * 20 * scale)
            splatter_alpha = int(220 * (1 - splatter_life))
            if splatter_alpha > 0:
                splatter_size = max(1, int((3 - splatter_life * 2) * scale))
                pygame.draw.circle(surface, (*theme["blood"], splatter_alpha), (splatter_x, splatter_y), splatter_size)
                # 血滴拖尾
                for trail in range(3):
                    trail_progress = (trail + 1) / 3
                    trail_dist = splatter_dist - trail * 3 * scale
                    trail_x = cx + int(math.cos(splatter_angle) * trail_dist)
                    trail_y = cy + int(math.sin(splatter_angle) * trail_dist * 0.35) - int((splatter_life - trail_progress * 0.1) ** 2 * 20 * scale)
                    trail_alpha = splatter_alpha // (trail + 2)
                    if trail_alpha > 0:
                        pygame.draw.circle(surface, (*theme["blood"], trail_alpha), (trail_x, trail_y), max(1, int(1 * scale)))
        
        # 腐肉块（漂浮碎片）
        for chunk in range(15):
            chunk_angle = t * 0.8 + chunk * 0.6
            chunk_dist = int((25 + 12 * math.sin(t * 2 + chunk)) * scale)
            chunk_x = cx + int(math.cos(chunk_angle) * chunk_dist)
            chunk_y = cy + int(math.sin(chunk_angle) * chunk_dist * 0.35)
            chunk_rot = t * 3 + chunk
            chunk_pulse = 0.8 + 0.2 * math.sin(t * 5 + chunk)
            # 肉块形状（不规则四边形）
            chunk_points = []
            for p in range(4):
                p_angle = p * (math.pi / 2) + chunk_rot
                p_dist = (4 + (p % 2) * 2) * scale * chunk_pulse
                px = chunk_x + int(math.cos(p_angle) * p_dist)
                py = chunk_y + int(math.sin(p_angle) * p_dist * 0.5)
                chunk_points.append((px, py))
            if len(chunk_points) == 4:
                pygame.draw.polygon(surface, (*theme["flesh"], 200), chunk_points)
                pygame.draw.polygon(surface, (*theme["accent"], 180), chunk_points, 1)
                # 肉块光泽
                pygame.draw.circle(surface, (*theme["glow"], 120), (chunk_x, chunk_y), int(2 * scale))
    
    elif theme_name == "corruption":
        # ====== 腐化：真菌蔓延+诅咒符文+腐化孢子+蠕虫隧道+腐化之眼+毒液池 ======
        # 真菌蔓延（地毯式增长）
        for creep_layer in range(4):
            creep_count = 12 + creep_layer * 6
            creep_dist_base = (18 + creep_layer * 10) * scale
            for creep in range(creep_count):
                creep_angle = t * (0.4 - creep_layer * 0.08) + creep * (6.28 / creep_count)
                creep_dist = creep_dist_base + 8 * math.sin(t * 2.5 + creep) * scale
                creep_x = cx + int(math.cos(creep_angle) * creep_dist)
                creep_y = cy + int(math.sin(creep_angle) * creep_dist * 0.35)
                creep_pulse = 0.75 + 0.25 * math.sin(t * 4 + creep + creep_layer)
                creep_size = int((7 - creep_layer + 3 * math.sin(t * 2 + creep)) * scale * creep_pulse)
                
                # 菌块主体（多层紫黑）
                for c_layer in range(3):
                    c_size = creep_size - c_layer * int(2 * scale)
                    c_alpha = (140 - creep_layer * 15) - c_layer * 20
                    if c_size > 0 and c_alpha > 0:
                        c_color_factor = c_layer / 3
                        c_color = tuple(int(theme["secondary"][i] * (1 - c_color_factor) + theme["nebula"][i] * c_color_factor) for i in range(3))
                        pygame.draw.circle(surface, (*c_color, c_alpha), (creep_x, creep_y), c_size)
                
                # 菌丝（连接到中心）
                if creep % 3 == 0 and creep_layer > 0:
                    mycelium_alpha = 80 - creep_layer * 10
                    pygame.draw.line(surface, (*theme["nebula"], mycelium_alpha), (cx, cy), (creep_x, creep_y), 1)
                    # 菌丝节点
                    for node in range(3):
                        node_progress = (node + 1) / 4
                        node_x = int(cx + (creep_x - cx) * node_progress)
                        node_y = int(cy + (creep_y - cy) * node_progress)
                        pygame.draw.circle(surface, (*theme["secondary"], mycelium_alpha), (node_x, node_y), max(1, int(1.5 * scale)))
        
        # 诅咒符文（双层逆向旋转）
        for rune_ring in range(2):
            rune_count = 6 + rune_ring * 2
            rune_dist = (38 + rune_ring * 8) * scale
            rune_speed = -1.8 + rune_ring * 1.0
            for rune in range(rune_count):
                rune_angle = t * rune_speed + rune * (6.28 / rune_count)
                rune_x = cx + int(math.cos(rune_angle) * rune_dist)
                rune_y = cy + int(math.sin(rune_angle) * rune_dist * 0.35)
                rune_pulse = 0.8 + 0.2 * math.sin(t * 5 + rune + rune_ring)
                rune_alpha = int((200 - rune_ring * 30) * rune_pulse)
                
                # 符文十字架
                cross_size = (6 - rune_ring) * scale * rune_pulse
                pygame.draw.line(surface, (*theme["accent"], rune_alpha),
                               (rune_x - int(cross_size), rune_y), 
                               (rune_x + int(cross_size), rune_y), int(3 * scale))
                pygame.draw.line(surface, (*theme["accent"], rune_alpha),
                               (rune_x, rune_y - int(cross_size)), 
                               (rune_x, rune_y + int(cross_size)), int(3 * scale))
                
                # 符文外圈
                outer_r = int(cross_size * 1.2)
                pygame.draw.circle(surface, (*theme["accent"], rune_alpha), (rune_x, rune_y), outer_r, int(2 * scale))
                
                # 符文光点
                for dot in range(4):
                    dot_angle = dot * (math.pi / 2) + t * 6
                    dot_dist = outer_r * 1.3
                    dot_x = rune_x + int(math.cos(dot_angle) * dot_dist)
                    dot_y = rune_y + int(math.sin(dot_angle) * dot_dist * 0.5)
                    pygame.draw.circle(surface, (*theme["glow"], rune_alpha), (dot_x, dot_y), max(1, int(2 * scale)))
        
        # 腐化孢子（螺旋上升+扩散）
        for spore_layer in range(3):
            spore_count = 12 - spore_layer * 2
            for spore in range(spore_count):
                spore_life = ((t * (35 - spore_layer * 5) + spore * (70 / spore_count)) % 70) / 70
                spore_angle = spore * (6.28 / spore_count) + t * (1.5 + spore_layer * 0.5)
                spore_dist = int(spore_life * 45 * scale)
                spore_height = spore_life * 35 * scale
                spore_x = cx + int(math.cos(spore_angle) * spore_dist + math.sin(t * 8 + spore) * 8 * scale)
                spore_y = cy + int(math.sin(spore_angle) * spore_dist * 0.35) - int(spore_height)
                spore_alpha = int((220 - spore_layer * 30) * (1 - spore_life))
                
                if spore_alpha > 20:
                    spore_size = max(1, int((4 - spore_life * 2.5) * scale))
                    # 孢子主体
                    pygame.draw.circle(surface, (*theme["nebula"], spore_alpha), (spore_x, spore_y), spore_size)
                    # 孢子核心
                    pygame.draw.circle(surface, (*theme["glow"], spore_alpha), (spore_x, spore_y), max(1, spore_size // 2))
                    
                    # 孢子拖尾
                    for trail in range(4):
                        trail_life = spore_life - trail * 0.05
                        if trail_life > 0:
                            trail_dist = int(trail_life * 45 * scale)
                            trail_height = trail_life * 35 * scale
                            trail_x = cx + int(math.cos(spore_angle) * trail_dist + math.sin(t * 8 + spore) * 8 * scale)
                            trail_y = cy + int(math.sin(spore_angle) * trail_dist * 0.35) - int(trail_height)
                            trail_alpha = spore_alpha // (trail + 2)
                            if trail_alpha > 0:
                                pygame.draw.circle(surface, (*theme["nebula"], trail_alpha), (trail_x, trail_y), max(1, int(1 * scale)))
        
        # 蠕虫隧道（地下通道）
        worm_nodes = []
        for seg in range(20):
            seg_progress = seg / 20
            worm_angle = t * 2 + seg_progress * math.pi * 3
            worm_dist = int((12 + seg_progress * 30 - seg_progress * seg_progress * 10) * scale)
            worm_depth = math.sin(seg_progress * math.pi) * 12 * scale
            worm_x = cx + int(math.cos(worm_angle) * worm_dist)
            worm_y = cy + int(math.sin(worm_angle) * worm_dist * 0.35) + int(worm_depth)
            worm_nodes.append((worm_x, worm_y))
        
        # 绘制隧道
        if len(worm_nodes) > 1:
            for i in range(len(worm_nodes) - 1):
                tunnel_thickness = int((10 - i / 3) * scale)
                tunnel_alpha = 160 - i * 6
                if tunnel_thickness > 0 and tunnel_alpha > 0:
                    pygame.draw.line(surface, (*theme["secondary"], tunnel_alpha), 
                                   worm_nodes[i], worm_nodes[i + 1], tunnel_thickness)
                    # 隧道边缘光
                    if i % 2 == 0:
                        pygame.draw.line(surface, (*theme["nebula"], tunnel_alpha // 2), 
                                       worm_nodes[i], worm_nodes[i + 1], tunnel_thickness // 2)
        
        # 蠕虫段（身体节）
        for i, node in enumerate(worm_nodes):
            if i % 3 == 0:
                segment_pulse = 0.85 + 0.15 * math.sin(t * 10 + i)
                segment_size = int((6 - i / 6) * scale * segment_pulse)
                # 体节
                pygame.draw.circle(surface, (*theme["accent"], 220), node, segment_size)
                # 体节纹理
                pygame.draw.circle(surface, (*theme["secondary"], 180), node, segment_size, 1)
        
        # 腐化之眼（监视者）
        for eye_set in range(2):
            eye_count = 4 + eye_set * 2
            eye_dist = (28 + eye_set * 14) * scale
            for eye in range(eye_count):
                eye_angle = t * (1.0 - eye_set * 0.3) + eye * (6.28 / eye_count)
                eye_x = cx + int(math.cos(eye_angle) * eye_dist)
                eye_y = cy + int(math.sin(eye_angle) * eye_dist * 0.35)
                eye_pulse = 0.75 + 0.25 * math.sin(t * 4 + eye + eye_set)
                eye_alpha = int((210 - eye_set * 30) * eye_pulse)
                
                # 眼白
                eye_size = int((7 - eye_set) * scale * eye_pulse)
                pygame.draw.circle(surface, (*theme["primary"], eye_alpha), (eye_x, eye_y), eye_size)
                
                # 虹膜（紫色）
                iris_size = int(eye_size * 0.7)
                pygame.draw.circle(surface, (*theme["nebula"], eye_alpha), (eye_x, eye_y), iris_size)
                
                # 瞳孔（看向中心）
                look_angle = math.atan2(cy - eye_y, cx - eye_x)
                pupil_offset = iris_size * 0.3
                pupil_x = eye_x + int(math.cos(look_angle) * pupil_offset)
                pupil_y = eye_y + int(math.sin(look_angle) * pupil_offset * 0.5)
                pupil_size = int(eye_size * 0.4)
                pygame.draw.circle(surface, (20, 10, 30, 255), (pupil_x, pupil_y), pupil_size)
                
                # 眼光（发光点）
                highlight_x = pupil_x + int(pupil_size * 0.3)
                highlight_y = pupil_y - int(pupil_size * 0.3)
                pygame.draw.circle(surface, (*theme["glow"], 255), (highlight_x, highlight_y), max(1, int(1.5 * scale)))
        
        # 毒液池（底部积液）
        pool_y_base = cy + int(25 * scale)
        pool_width = 60 * scale
        # 液面波动
        pool_points = []
        for px in range(int(pool_width)):
            wave_height = math.sin(t * 6 + px * 0.2) * 3 * scale
            pool_x = cx - int(pool_width / 2) + px
            pool_y = pool_y_base + int(wave_height)
            pool_points.append((pool_x, pool_y))
        
        # 绘制液池
        if len(pool_points) > 2:
            # 添加底部点形成闭合形状
            pool_bottom_points = pool_points + [(pool_points[-1][0], pool_y_base + int(15 * scale)), 
                                                 (pool_points[0][0], pool_y_base + int(15 * scale))]
            pygame.draw.polygon(surface, (*theme["nebula"], 150), pool_bottom_points)
            # 液面反光
            pygame.draw.lines(surface, (*theme["glow"], 200), False, pool_points, int(2 * scale))
        
        # 毒液气泡
        for bubble in range(8):
            bubble_life = ((t * 20 + bubble * 7) % 50) / 50
            bubble_x = cx - int(25 * scale) + bubble * int(7 * scale) + int(math.sin(t * 3 + bubble) * 4 * scale)
            bubble_y = pool_y_base - int(bubble_life * 20 * scale)
            bubble_alpha = int(180 * (1 - bubble_life))
            if bubble_alpha > 20:
                bubble_size = max(1, int((3 + bubble_life) * scale))
                pygame.draw.circle(surface, (*theme["glow"], bubble_alpha), (bubble_x, bubble_y), bubble_size)
                pygame.draw.circle(surface, (*theme["nebula"], bubble_alpha), (bubble_x, bubble_y), bubble_size, 1)
    
    elif theme_name == "hallowed":
        # ====== 神圣：彩虹光谱+圣光十字+天使光环+圣翼+神圣符文+祝福光线+圣歌粒子 ======
        # 彩虹光谱（多层7色环+脉冲）
        rainbow_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]
        for ring_layer in range(3):
            for i, color in enumerate(rainbow_colors):
                ring_r = int((28 + i * 6 + ring_layer * 3) * scale)
                ring_pulse = 0.7 + 0.3 * math.sin(t * (3 - ring_layer * 0.5) + i * 0.6)
                ring_alpha = int((120 - ring_layer * 20) * ring_pulse)
                ring_thickness = max(1, int((4 - ring_layer) * scale))
                pygame.draw.circle(surface, (*color, ring_alpha), (cx, cy), ring_r, ring_thickness)
                
                # 彩虹光点（环上装饰）
                if ring_layer == 0:
                    for dot in range(12):
                        dot_angle = dot * (math.pi / 6) + t * 2
                        dot_x = cx + int(math.cos(dot_angle) * ring_r)
                        dot_y = cy + int(math.sin(dot_angle) * ring_r * 0.35)
                        dot_pulse = 0.6 + 0.4 * math.sin(t * 6 + dot + i)
                        pygame.draw.circle(surface, (*color, int(220 * dot_pulse)), (dot_x, dot_y), int(3 * scale))
        
        # 圣光十字（多重脉冲+扩散）
        for cross_layer in range(4):
            cross_size = int((24 + 10 * math.sin(t * 3 + cross_layer * 0.5) + cross_layer * 4) * scale)
            cross_alpha = int((220 - cross_layer * 35) * (0.6 + 0.4 * math.sin(t * 4 + cross_layer)))
            cross_thickness = max(1, int((6 - cross_layer) * scale))
            
            # 竖线
            pygame.draw.line(surface, (*theme["glow"], cross_alpha),
                           (cx, cy - cross_size), (cx, cy + cross_size), cross_thickness)
            # 横线
            pygame.draw.line(surface, (*theme["glow"], cross_alpha),
                           (cx - cross_size, cy), (cx + cross_size, cy), cross_thickness)
            
            # 十字端点光芒
            for end_angle in [0, math.pi / 2, math.pi, math.pi * 1.5]:
                end_x = cx + int(math.cos(end_angle) * cross_size)
                end_y = cy + int(math.sin(end_angle) * cross_size * 0.35)
                for ray in range(6):
                    ray_angle = end_angle + (ray - 2.5) * 0.15
                    ray_len = (8 - cross_layer * 2) * scale
                    ray_end_x = end_x + int(math.cos(ray_angle) * ray_len)
                    ray_end_y = end_y + int(math.sin(ray_angle) * ray_len * 0.35)
                    ray_alpha = cross_alpha // (2 + abs(ray - 2.5))
                    if ray_alpha > 0:
                        pygame.draw.line(surface, (*theme["constellation"], ray_alpha), (end_x, end_y), (ray_end_x, ray_end_y), 1)
        
        # 十字中心光球（多层）
        core_pulse = 0.8 + 0.2 * math.sin(t * 8)
        for core_layer in range(6):
            core_r = int((10 - core_layer * 1.5) * scale * core_pulse)
            core_alpha = 180 + core_layer * 12
            if core_r > 0:
                pygame.draw.circle(surface, (*theme["constellation"], core_alpha), (cx, cy), core_r)
        
        # 天使光环（头顶+多层椭圆）
        halo_y = cy - int(40 * scale)
        halo_base_r = 18 * scale
        for halo_ring in range(5):
            halo_r = int(halo_base_r + halo_ring * 4 * scale)
            halo_h = int(halo_r * 0.4)
            halo_pulse = 0.85 + 0.15 * math.sin(t * 5 + halo_ring)
            halo_alpha = int((200 - halo_ring * 30) * halo_pulse)
            halo_thickness = max(1, int((3 - halo_ring * 0.5) * scale))
            
            if halo_alpha > 0:
                pygame.draw.ellipse(surface, (*theme["constellation"], halo_alpha),
                                  (cx - halo_r, halo_y - halo_h, halo_r * 2, halo_h * 2), halo_thickness)
                # 光环光点
                for dot in range(8):
                    dot_angle = dot * (math.pi / 4) + t * 3
                    dot_x = cx + int(math.cos(dot_angle) * halo_r)
                    dot_y = halo_y + int(math.sin(dot_angle) * halo_h)
                    pygame.draw.circle(surface, (*theme["glow"], halo_alpha), (dot_x, dot_y), max(1, int(2 * scale)))
        
        # 圣翼展开（双翼+羽毛）
        for wing_side in [-1, 1]:
            wing_base_x = cx + int(wing_side * 12 * scale)
            wing_base_y = cy
            
            # 主翼骨（3层）
            for layer in range(3):
                wing_angle = wing_side * (math.pi / 6 + layer * math.pi / 12) + math.sin(t * 2 + layer) * 0.1
                wing_len = (25 + layer * 8) * scale
                wing_tip_x = wing_base_x + int(math.cos(wing_angle) * wing_len)
                wing_tip_y = wing_base_y + int(math.sin(wing_angle) * wing_len * 0.3)
                wing_alpha = 200 - layer * 30
                
                # 翼骨
                pygame.draw.line(surface, (*theme["constellation"], wing_alpha), 
                               (wing_base_x, wing_base_y), (wing_tip_x, wing_tip_y), int((4 - layer) * scale))
                
                # 羽毛（沿翼骨分布）
                for feather in range(8):
                    feather_progress = (feather + 1) / 9
                    feather_base_x = int(wing_base_x + (wing_tip_x - wing_base_x) * feather_progress)
                    feather_base_y = int(wing_base_y + (wing_tip_y - wing_base_y) * feather_progress)
                    
                    # 羽毛形状（三点）
                    feather_angle = wing_angle + wing_side * (math.pi / 2)
                    feather_len = (8 - layer * 2) * scale * (1 - feather_progress * 0.3)
                    feather_tip_x = feather_base_x + int(math.cos(feather_angle) * feather_len)
                    feather_tip_y = feather_base_y + int(math.sin(feather_angle) * feather_len * 0.5)
                    
                    feather_alpha = wing_alpha - feather * 15
                    if feather_alpha > 0:
                        # 羽毛主体
                        pygame.draw.line(surface, (*theme["glow"], feather_alpha), 
                                       (feather_base_x, feather_base_y), (feather_tip_x, feather_tip_y), max(1, int(2 * scale)))
                        # 羽毛尖端
                        pygame.draw.circle(surface, (*theme["constellation"], feather_alpha), 
                                         (feather_tip_x, feather_tip_y), max(1, int(1.5 * scale)))
        
        # 神圣符文阵（环形排列+旋转）
        for rune_ring in range(2):
            rune_count = 8 + rune_ring * 4
            rune_dist = (42 + rune_ring * 10) * scale
            rune_speed = 1.5 - rune_ring * 0.8
            for rune in range(rune_count):
                rune_angle = t * rune_speed + rune * (6.28 / rune_count)
                rune_x = cx + int(math.cos(rune_angle) * rune_dist)
                rune_y = cy + int(math.sin(rune_angle) * rune_dist * 0.35)
                rune_pulse = 0.75 + 0.25 * math.sin(t * 6 + rune + rune_ring)
                rune_alpha = int((190 - rune_ring * 30) * rune_pulse)
                rune_size = (5 - rune_ring) * scale
                
                # 符文形状（六芒星）
                star_points = []
                for p in range(6):
                    p_angle = p * (math.pi / 3) + rune_angle
                    p_dist = rune_size * (1.5 if p % 2 == 0 else 0.7)
                    px = rune_x + int(math.cos(p_angle) * p_dist)
                    py = rune_y + int(math.sin(p_angle) * p_dist * 0.5)
                    star_points.append((px, py))
                
                if len(star_points) == 6:
                    # 外轮廓
                    pygame.draw.polygon(surface, (*theme["constellation"], rune_alpha), star_points, int(2 * scale))
                    # 内核
                    pygame.draw.circle(surface, (*theme["glow"], rune_alpha + 50), (rune_x, rune_y), max(1, int(2 * scale)))
        
        # 祝福光线（径向发射）
        for ray_set in range(3):
            ray_count = 12 - ray_set * 2
            ray_offset = ray_set * 0.524
            for ray in range(ray_count):
                ray_angle = t * (2 - ray_set * 0.5) + ray * (6.28 / ray_count) + ray_offset
                ray_progress = ((t * (30 - ray_set * 5) + ray * 3) % 60) / 60
                ray_dist = int(ray_progress * 55 * scale)
                ray_x = cx + int(math.cos(ray_angle) * ray_dist)
                ray_y = cy + int(math.sin(ray_angle) * ray_dist * 0.35)
                ray_alpha = int((220 - ray_set * 30) * (1 - ray_progress))
                
                if ray_alpha > 20:
                    ray_size = max(1, int((5 - ray_progress * 3 - ray_set) * scale))
                    # 光线头部
                    pygame.draw.circle(surface, (*theme["glow"], ray_alpha), (ray_x, ray_y), ray_size)
                    # 光线尾迹
                    for trail in range(5):
                        trail_progress = ray_progress - trail * 0.05
                        if trail_progress > 0:
                            trail_dist = int(trail_progress * 55 * scale)
                            trail_x = cx + int(math.cos(ray_angle) * trail_dist)
                            trail_y = cy + int(math.sin(ray_angle) * trail_dist * 0.35)
                            trail_alpha = ray_alpha // (trail + 2)
                            if trail_alpha > 0:
                                pygame.draw.circle(surface, (*theme["constellation"], trail_alpha), 
                                                 (trail_x, trail_y), max(1, int((5 - ray_progress * 3 - trail) * scale)))
        
        # 圣歌粒子（螺旋上升音符）
        for note in range(20):
            note_life = ((t * 25 + note * 4) % 70) / 70
            note_angle = note * 0.9 + t * 3
            note_dist = int(note_life * 35 * scale)
            note_height = note_life * 40 * scale
            note_x = cx + int(math.cos(note_angle) * note_dist)
            note_y = cy + int(math.sin(note_angle) * note_dist * 0.35) - int(note_height)
            note_alpha = int(200 * (1 - note_life))
            
            if note_alpha > 20:
                # 音符头
                note_size = max(1, int((4 - note_life * 2) * scale))
                pygame.draw.circle(surface, (*theme["constellation"], note_alpha), (note_x, note_y), note_size)
                # 音符尾（竖线）
                note_stem_y = note_y - int(8 * scale)
                pygame.draw.line(surface, (*theme["glow"], note_alpha), 
                               (note_x, note_y), (note_x, note_stem_y), max(1, int(1 * scale)))
                # 音符光晕
                pygame.draw.circle(surface, (*theme["glow"], note_alpha // 2), (note_x, note_y), note_size * 2)
    
    elif theme_name == "lunar":
        # ====== 月耀天体：月相变化+陨石雨+星环+月海+月坑+潮汐波+星云带 ======
        # 月相（完整循环+月海细节）
        moon_phase = (t * 0.6) % 1.0
        moon_base_r = 24 * scale
        
        # 满月底层（多层渲染）
        for layer in range(5):
            moon_layer_r = int((moon_base_r - layer * 2) * scale)
            moon_alpha = 180 + layer * 15
            if moon_layer_r > 0:
                pygame.draw.circle(surface, (*theme["primary"], moon_alpha), (cx, cy), moon_layer_r)
        
        # 月海（阴暗区域）
        maria_positions = [
            (0.3, 0.2), (-0.4, -0.1), (0.1, -0.3), (-0.2, 0.3)
        ]
        for maria_x_ratio, maria_y_ratio in maria_positions:
            maria_x = cx + int(maria_x_ratio * moon_base_r)
            maria_y = cy + int(maria_y_ratio * moon_base_r * 0.4)
            maria_size = int((6 + 3 * math.sin(t * 2 + maria_x_ratio)) * scale)
            pygame.draw.circle(surface, (80, 90, 110, 180), (maria_x, maria_y), maria_size)
            # 月海边缘光
            pygame.draw.circle(surface, (*theme["secondary"], 100), (maria_x, maria_y), maria_size, 1)
        
        # 月相阴影（渐变处理）
        shadow_offset_base = (moon_phase - 0.5) * moon_base_r * 2.5
        for shadow_layer in range(8):
            shadow_offset = shadow_offset_base + shadow_layer * (moon_base_r * 0.15)
            if abs(shadow_offset) < moon_base_r * 2:
                shadow_alpha = 180 - shadow_layer * 20
                if shadow_alpha > 0:
                    shadow_x = cx + int(shadow_offset)
                    pygame.draw.circle(surface, (25, 30, 45, shadow_alpha), (shadow_x, cy), int(moon_base_r * (1 - shadow_layer * 0.08)))
        
        # 月光光晕（多层扩散）
        for glow_ring in range(8):
            glow_r = int(moon_base_r + glow_ring * 6 * scale)
            glow_pulse = 0.6 + 0.4 * math.sin(t * 2.5 - glow_ring * 0.4)
            glow_alpha = int((100 - glow_ring * 12) * glow_pulse)
            if glow_alpha > 20:
                pygame.draw.circle(surface, (*theme["glow"], glow_alpha), (cx, cy), glow_r, max(1, int((3 - glow_ring * 0.3) * scale)))
        
        # 月坑（撞击坑）
        for crater in range(12):
            crater_angle = crater * (math.pi / 6) + t * 0.2
            crater_dist = int((12 + crater % 3 * 5) * scale)
            crater_x = cx + int(math.cos(crater_angle) * crater_dist)
            crater_y = cy + int(math.sin(crater_angle) * crater_dist * 0.4)
            crater_size = int((3 + crater % 4) * scale)
            # 坑底（暗）
            pygame.draw.circle(surface, (60, 70, 85, 200), (crater_x, crater_y), crater_size)
            # 坑缘（亮边）
            crater_rim_offset = -2
            crater_rim_x = crater_x + int(math.cos(crater_angle - math.pi / 4) * crater_rim_offset)
            crater_rim_y = crater_y + int(math.sin(crater_angle - math.pi / 4) * crater_rim_offset * 0.4)
            pygame.draw.circle(surface, (*theme["primary"], 220), (crater_rim_x, crater_rim_y), max(1, int(1 * scale)))
        
        # 陨石雨（多层+碎片效果）
        for meteor_layer in range(3):
            meteor_count = 8 + meteor_layer * 4
            meteor_speed = 18 - meteor_layer * 3
            for meteor in range(meteor_count):
                meteor_life = ((t * meteor_speed + meteor * (80 / meteor_count)) % 80) / 80
                meteor_base_x = cx - int(45 * scale) + (meteor % 5) * int(20 * scale)
                meteor_x = meteor_base_x + int(meteor_life * 90 * scale)
                meteor_y = cy - int(45 * scale) + int(meteor_life * 70 * scale)
                meteor_alpha = int((220 - meteor_layer * 30) * (1 - meteor_life))
                
                if meteor_alpha > 20:
                    meteor_size = max(1, int((4 - meteor_layer - meteor_life * 2) * scale))
                    # 陨石核心
                    pygame.draw.circle(surface, (*theme["accent"], meteor_alpha), (meteor_x, meteor_y), meteor_size)
                    # 内核（高温）
                    pygame.draw.circle(surface, (*theme["glow"], meteor_alpha + 30), (meteor_x, meteor_y), max(1, meteor_size // 2))
                    
                    # 陨石尾迹（多粒子）
                    for trail in range(8):
                        trail_progress = meteor_life - trail * 0.04
                        if trail_progress > 0:
                            trail_x = meteor_base_x + int(trail_progress * 90 * scale)
                            trail_y = cy - int(45 * scale) + int(trail_progress * 70 * scale)
                            trail_alpha = int(meteor_alpha * (1 - trail * 0.12))
                            trail_size = max(1, int((4 - meteor_layer - trail_progress * 2 - trail * 0.3) * scale))
                            if trail_alpha > 0 and trail_size > 0:
                                pygame.draw.circle(surface, (*theme["trail"], trail_alpha), (trail_x, trail_y), trail_size)
                    
                    # 陨石碎片（分离粒子）
                    if meteor_life > 0.3 and meteor % 3 == 0:
                        for fragment in range(3):
                            frag_angle = fragment * (math.pi / 1.5) - math.pi / 2
                            frag_offset = (meteor_life - 0.3) * 8 * scale
                            frag_x = meteor_x + int(math.cos(frag_angle) * frag_offset)
                            frag_y = meteor_y + int(math.sin(frag_angle) * frag_offset * 0.5)
                            frag_alpha = int(meteor_alpha * 0.6)
                            if frag_alpha > 0:
                                pygame.draw.circle(surface, (*theme["accent"], frag_alpha), (frag_x, frag_y), max(1, int(1.5 * scale)))
        
        # 星环（土星环效果+环粒子）
        for ring_layer in range(4):
            ring_w = int((52 + ring_layer * 8) * scale)
            ring_h = int((12 + ring_layer * 2) * scale)
            ring_alpha = 140 - ring_layer * 25
            ring_thickness = max(1, int((4 - ring_layer) * scale))
            pygame.draw.ellipse(surface, (*theme["secondary"], ring_alpha),
                              (cx - ring_w, cy - ring_h // 2, ring_w * 2, ring_h), ring_thickness)
            
            # 环上的粒子（岩石块）
            particle_count = 20 + ring_layer * 5
            for p in range(particle_count):
                p_angle = p * (6.28 / particle_count) + t * (0.5 - ring_layer * 0.1)
                p_ellipse_x = math.cos(p_angle) * ring_w
                p_ellipse_y = math.sin(p_angle) * ring_h * 0.5
                p_x = cx + int(p_ellipse_x)
                p_y = cy + int(p_ellipse_y)
                p_pulse = 0.7 + 0.3 * math.sin(t * 8 + p + ring_layer)
                p_alpha = int((ring_alpha - 20) * p_pulse)
                if p_alpha > 0:
                    pygame.draw.circle(surface, (*theme["stardust"], p_alpha), (p_x, p_y), max(1, int(2 * scale)))
        
        # 潮汐波（月球引力效果）
        tide_wave_count = 6
        for wave in range(tide_wave_count):
            wave_phase = (t * 2.5 + wave * (1 / tide_wave_count)) % 1.0
            wave_r = int((moon_base_r + wave_phase * 45) * scale)
            wave_alpha = int(160 * (1 - wave_phase))
            if wave_alpha > 20:
                # 波纹环
                pygame.draw.circle(surface, (*theme["accent"], wave_alpha), (cx, cy), wave_r, max(1, int(2 * scale)))
                # 波纹粒子
                for dot in range(16):
                    dot_angle = dot * (math.pi / 8) + wave_phase * 6.28
                    dot_x = cx + int(math.cos(dot_angle) * wave_r)
                    dot_y = cy + int(math.sin(dot_angle) * wave_r * 0.35)
                    pygame.draw.circle(surface, (*theme["accent"], wave_alpha), (dot_x, dot_y), max(1, int(2 * scale)))
        
        # 星云带（背景气体云）
        for nebula_band in range(3):
            band_y_offset = (nebula_band - 1) * 20 * scale
            band_count = 10
            for cloud in range(band_count):
                cloud_x = cx - int(40 * scale) + cloud * int(8 * scale) + int(math.sin(t * 2 + cloud + nebula_band) * 6 * scale)
                cloud_y = cy + int(band_y_offset)
                cloud_pulse = 0.5 + 0.5 * math.sin(t * 1.5 + cloud + nebula_band)
                cloud_size = int((5 + cloud % 3) * scale * cloud_pulse)
                cloud_alpha = int((80 - nebula_band * 15) * cloud_pulse)
                if cloud_alpha > 0:
                    pygame.draw.circle(surface, (*theme["nebula"], cloud_alpha), (cloud_x, cloud_y), cloud_size)
    
    elif theme_name == "zenith":
        # ====== 天顶之刃：剑影重叠+终极之力+光剑阵+剑气+剑阵法术+神兵光柱+万剑归宗 ======
        # 剑影重叠（多圈+层次感）
        for sword_ring in range(3):
            sword_count = 9 + sword_ring * 3
            sword_dist_base = (32 + sword_ring * 12) * scale
            sword_rotation_speed = 0.9 - sword_ring * 0.2
            for sword in range(sword_count):
                sword_angle = sword * (6.28 / sword_count) + t * sword_rotation_speed + sword_ring * 1.047
                sword_dist = sword_dist_base + 5 * math.sin(t * 3 + sword) * scale
                sword_x = cx + int(math.cos(sword_angle) * sword_dist)
                sword_y = cy + int(math.sin(sword_angle) * sword_dist * 0.35)
                
                # 剑的方向（指向外）
                sword_len = int((28 - sword_ring * 3) * scale)
                sword_tip_angle = sword_angle
                sword_tip_x = sword_x + int(math.cos(sword_tip_angle) * sword_len)
                sword_tip_y = sword_y + int(math.sin(sword_tip_angle) * sword_len * 0.35)
                
                sword_pulse = 0.7 + 0.3 * math.sin(t * 4 + sword + sword_ring)
                sword_alpha = int((180 - sword_ring * 30) * sword_pulse)
                sword_thickness = max(1, int((5 - sword_ring) * scale))
                
                # 剑刃主体
                pygame.draw.line(surface, (*theme["accent"], sword_alpha), 
                               (sword_x, sword_y), (sword_tip_x, sword_tip_y), sword_thickness)
                
                # 剑刃中线（高光）
                mid_highlight_alpha = min(255, sword_alpha + 60)
                pygame.draw.line(surface, (*theme["glow"], mid_highlight_alpha), 
                               (sword_x, sword_y), (sword_tip_x, sword_tip_y), max(1, sword_thickness // 2))
                
                # 剑尖光芒（爆裂光点）
                tip_glow_size = int((6 - sword_ring) * scale * sword_pulse)
                for glow_layer in range(3):
                    glow_size = tip_glow_size - glow_layer * int(2 * scale)
                    glow_alpha = max(0, min(255, sword_alpha + 70 - glow_layer * 30))
                    if glow_size > 0 and glow_alpha > 0:
                        pygame.draw.circle(surface, (*theme["glow"], glow_alpha), (sword_tip_x, sword_tip_y), glow_size)
                
                # 剑柄（握把）
                handle_len = 6 * scale
                handle_end_x = sword_x - int(math.cos(sword_tip_angle) * handle_len)
                handle_end_y = sword_y - int(math.sin(sword_tip_angle) * handle_len * 0.35)
                pygame.draw.line(surface, (*theme["secondary"], max(0, sword_alpha - 20)), 
                               (sword_x, sword_y), (handle_end_x, handle_end_y), max(1, sword_thickness + int(2 * scale)))
                # 剑柄宝石
                pygame.draw.circle(surface, (*theme["constellation"], min(255, sword_alpha + 50)), 
                                 (handle_end_x, handle_end_y), max(1, int(3 * scale)))
                
                # 剑气（刀光剑影）
                if sword % 2 == 0:
                    for aura in range(4):
                        aura_progress = ((t * 25 + sword * 5 + aura * 2) % 30) / 30
                        aura_offset = aura_progress * 20 * scale
                        aura_x = sword_tip_x + int(math.cos(sword_tip_angle) * aura_offset)
                        aura_y = sword_tip_y + int(math.sin(sword_tip_angle) * aura_offset * 0.35)
                        aura_alpha = max(0, int((sword_alpha - 40) * (1 - aura_progress)))
                        if aura_alpha > 0:
                            aura_size = max(1, int((5 - aura_progress * 3) * scale))
                            pygame.draw.circle(surface, (*theme["accent"], aura_alpha), (aura_x, aura_y), aura_size)
        
        # 终极之力（中心八向爆发+脉冲环）
        power_pulse = 0.5 + 0.5 * math.sin(t * 5)  # 范围 0.0-1.0
        for burst_ring in range(3):
            burst_count = 8 + burst_ring * 4
            for burst in range(burst_count):
                burst_angle = burst * (6.28 / burst_count) + t * (2.5 - burst_ring * 0.5) + burst_ring * 0.524
                burst_base_len = (18 + burst_ring * 8) * scale
                burst_len = int((burst_base_len + 18 * power_pulse) * scale)
                
                # 爆发射线
                for seg in range(6):
                    seg_progress = (seg + 1) / 6
                    seg_dist = burst_len * seg_progress
                    bx = cx + int(math.cos(burst_angle) * seg_dist)
                    by = cy + int(math.sin(burst_angle) * seg_dist * 0.35)
                    seg_alpha = max(0, min(255, int((250 - burst_ring * 40) * power_pulse * (1 - seg_progress * 0.3))))
                    seg_size = int((6 - burst_ring - seg_progress * 3) * scale)
                    if seg_alpha > 0 and seg_size > 0:
                        pygame.draw.circle(surface, (*theme["constellation"], seg_alpha), (bx, by), seg_size)
                
                # 爆发连线
                burst_end_x = cx + int(math.cos(burst_angle) * burst_len)
                burst_end_y = cy + int(math.sin(burst_angle) * burst_len * 0.35)
                burst_line_alpha = max(0, min(255, int((220 - burst_ring * 35) * power_pulse)))
                pygame.draw.line(surface, (*theme["glow"], burst_line_alpha), 
                               (cx, cy), (burst_end_x, burst_end_y), max(1, int((4 - burst_ring) * scale)))
        
        # 光剑阵核心（多层光球）
        for core_layer in range(8):
            core_r = int((16 - core_layer * 1.8) * scale * (0.9 + 0.1 * math.sin(t * 10)))
            core_alpha = min(255, 160 + core_layer * 12)
            core_color_mix = core_layer / 8
            core_color = tuple(int(theme["constellation"][i] * (1 - core_color_mix) + theme["glow"][i] * core_color_mix) for i in range(3))
            if core_r > 0:
                pygame.draw.circle(surface, (*core_color, core_alpha), (cx, cy), core_r)
        
        # 剑阵法术（符文阵）
        for rune_circle in range(2):
            rune_count = 12 - rune_circle * 4
            rune_dist = (45 + rune_circle * 8) * scale
            for rune in range(rune_count):
                rune_angle = t * (-1.8 + rune_circle * 0.8) + rune * (6.28 / rune_count)
                rune_x = cx + int(math.cos(rune_angle) * rune_dist)
                rune_y = cy + int(math.sin(rune_angle) * rune_dist * 0.35)
                rune_pulse = 0.75 + 0.25 * math.sin(t * 6 + rune + rune_circle)
                rune_alpha = int((190 - rune_circle * 35) * rune_pulse)
                
                # 符文形状（剑形）
                rune_sword_len = (7 - rune_circle * 2) * scale
                rune_sword_angle = rune_angle + math.pi / 2
                rune_tip_x = rune_x + int(math.cos(rune_sword_angle) * rune_sword_len)
                rune_tip_y = rune_y + int(math.sin(rune_sword_angle) * rune_sword_len * 0.5)
                rune_base_x = rune_x - int(math.cos(rune_sword_angle) * rune_sword_len * 0.3)
                rune_base_y = rune_y - int(math.sin(rune_sword_angle) * rune_sword_len * 0.3 * 0.5)
                
                pygame.draw.line(surface, (*theme["accent"], rune_alpha), 
                               (rune_base_x, rune_base_y), (rune_tip_x, rune_tip_y), max(1, int(2 * scale)))
                pygame.draw.circle(surface, (*theme["glow"], min(255, rune_alpha + 50)), (rune_tip_x, rune_tip_y), max(1, int(2 * scale)))
                
                # 符文光环
                for ring in range(2):
                    ring_r = int((4 + ring * 2) * scale)
                    pygame.draw.circle(surface, (*theme["constellation"], max(0, rune_alpha - ring * 40)), 
                                     (rune_x, rune_y), ring_r, 1)
        
        # 神兵光柱（天降神剑）
        pillar_phase = (t * 2.5) % 1.0
        if pillar_phase < 0.7:  # 光柱持续时间
            pillar_alpha = min(255, int(220 * (1 - pillar_phase / 0.7)))
            pillar_width = int(25 * scale * (0.8 + 0.2 * math.sin(t * 12)))
            # 光柱主体（渐变）
            for layer in range(10):
                layer_y = cy - int(50 * scale) + layer * int(10 * scale)
                layer_alpha = max(0, min(255, pillar_alpha - layer * 20))
                if layer_alpha > 0:
                    pygame.draw.ellipse(surface, (*theme["glow"], layer_alpha),
                                      (cx - pillar_width // 2, layer_y - int(5 * scale), 
                                       pillar_width, int(10 * scale)))
            
            # 光柱粒子（上升）
            for particle in range(15):
                particle_life = ((t * 40 + particle * 4) % 50) / 50
                particle_x = cx + int(math.sin(t * 5 + particle) * pillar_width * 0.4)
                particle_y = cy + int(15 * scale) - int(particle_life * 65 * scale)
                particle_alpha = int(pillar_alpha * (1 - particle_life))
                if particle_alpha > 0:
                    pygame.draw.circle(surface, (*theme["constellation"], particle_alpha), 
                                     (particle_x, particle_y), max(1, int(3 * scale)))
        
        # 万剑归宗（剑雨效果）
        sword_rain_count = 20
        for rain_sword in range(sword_rain_count):
            rain_life = ((t * 30 + rain_sword * 3) % 60) / 60
            rain_x = cx - int(50 * scale) + (rain_sword % 10) * int(10 * scale) + int(math.sin(t * 2 + rain_sword) * 5 * scale)
            rain_y = cy - int(50 * scale) + int(rain_life * 100 * scale)
            rain_alpha = int(200 * (1 - rain_life))
            
            if rain_alpha > 20:
                # 剑形（小型）
                rain_sword_len = 12 * scale
                rain_sword_angle = math.pi / 2 + math.sin(t * 4 + rain_sword) * 0.3
                rain_tip_x = rain_x + int(math.cos(rain_sword_angle) * rain_sword_len)
                rain_tip_y = rain_y + int(math.sin(rain_sword_angle) * rain_sword_len * 0.5)
                
                pygame.draw.line(surface, (*theme["accent"], rain_alpha), 
                               (rain_x, rain_y), (rain_tip_x, rain_tip_y), max(1, int(2 * scale)))
                pygame.draw.circle(surface, (*theme["glow"], rain_alpha), (rain_tip_x, rain_tip_y), max(1, int(2 * scale)))
    
    elif theme_name == "rainbow":
        # ====== 彩虹水晶：棱镜折射+水晶碎片+光谱循环+光学现象+色散效应+虹彩粒子+光晕干涉 ======
        # 定义完整彩虹色谱
        rainbow_spectrum = [
            (255, 0, 0),      # 红
            (255, 127, 0),    # 橙
            (255, 255, 0),    # 黄
            (0, 255, 0),      # 绿
            (0, 191, 255),    # 青
            (0, 0, 255),      # 蓝
            (148, 0, 211)     # 紫
        ]
        
        # 水晶碎片（多层六边形+色彩循环）
        for crystal_ring in range(3):
            crystal_count = 12 + crystal_ring * 4
            crystal_dist_base = (28 + crystal_ring * 12) * scale
            crystal_rotation_speed = 1.6 - crystal_ring * 0.3
            for crystal in range(crystal_count):
                crystal_angle = t * crystal_rotation_speed + crystal * (6.28 / crystal_count) + crystal_ring * 1.047
                crystal_dist = crystal_dist_base + 8 * math.sin(t * 2.5 + crystal) * scale
                crystal_x = cx + int(math.cos(crystal_angle) * crystal_dist)
                crystal_y = cy + int(math.sin(crystal_angle) * crystal_dist * 0.35)
                
                # 颜色循环（基于时间+位置）
                hue_shift = (t * 3 + crystal * (1 / crystal_count) + crystal_ring * 0.3) % 1.0
                color_index = int(hue_shift * 7) % 7
                color_next = (color_index + 1) % 7
                color_blend = (hue_shift * 7) % 1.0
                crystal_color = tuple(int(rainbow_spectrum[color_index][i] * (1 - color_blend) + rainbow_spectrum[color_next][i] * color_blend) for i in range(3))
                
                crystal_pulse = 0.75 + 0.25 * math.sin(t * 5 + crystal + crystal_ring)
                crystal_alpha = int((210 - crystal_ring * 30) * crystal_pulse)
                
                # 水晶多边形（六边形）
                crystal_size = (8 - crystal_ring * 2) * scale
                crystal_points = []
                for p in range(6):
                    p_angle = crystal_angle + p * (math.pi / 3)
                    p_dist = crystal_size
                    px = crystal_x + int(math.cos(p_angle) * p_dist)
                    py = crystal_y + int(math.sin(p_angle) * p_dist * 0.5)
                    crystal_points.append((px, py))
                
                if len(crystal_points) == 6:
                    # 水晶主体（实心）
                    pygame.draw.polygon(surface, (*crystal_color, crystal_alpha), crystal_points)
                    # 水晶边缘（高光）
                    pygame.draw.polygon(surface, (255, 255, 255, crystal_alpha), crystal_points, max(1, int(2 * scale)))
                    # 水晶核心（明亮点）
                    pygame.draw.circle(surface, (255, 255, 255, crystal_alpha + 40), (crystal_x, crystal_y), max(1, int(2 * scale)))
        
        # 棱镜折射光线（七彩光束+扩散）
        for ray_set in range(2):
            ray_count = 7 + ray_set * 7
            ray_offset = ray_set * 0.5
            for ray in range(ray_count):
                ray_angle = t * (3.5 - ray_set) + ray * (6.28 / ray_count) + ray_offset
                ray_base_len = (22 + ray_set * 10) * scale
                ray_len = int(ray_base_len + 12 * math.sin(t * 4 + ray) * scale)
                
                # 光线颜色（彩虹循环）
                ray_hue = (ray / ray_count + t * 0.5) % 1.0
                ray_color_idx = int(ray_hue * 7) % 7
                ray_color = rainbow_spectrum[ray_color_idx]
                ray_alpha = int((200 - ray_set * 40) * (0.7 + 0.3 * math.sin(t * 5 + ray)))
                
                # 光线分段绘制（渐变效果）
                for seg in range(8):
                    seg_progress = (seg + 1) / 8
                    seg_dist = ray_len * seg_progress
                    ray_x = cx + int(math.cos(ray_angle) * seg_dist)
                    ray_y = cy + int(math.sin(ray_angle) * seg_dist * 0.35)
                    seg_alpha = int(ray_alpha * (1 - seg_progress * 0.4))
                    seg_size = max(1, int((5 - ray_set - seg_progress * 2) * scale))
                    
                    if seg_alpha > 0:
                        pygame.draw.circle(surface, (*ray_color, seg_alpha), (ray_x, ray_y), seg_size)
                
                # 光线末端光晕
                ray_end_x = cx + int(math.cos(ray_angle) * ray_len)
                ray_end_y = cy + int(math.sin(ray_angle) * ray_len * 0.35)
                for glow in range(3):
                    glow_size = int((6 - glow * 2 - ray_set) * scale)
                    glow_alpha = ray_alpha // (glow + 2)
                    if glow_size > 0 and glow_alpha > 0:
                        pygame.draw.circle(surface, (*ray_color, glow_alpha), (ray_end_x, ray_end_y), glow_size)
        
        # 光谱核心（彩虹同心圆）
        for spectrum_ring in range(7):
            s_r = int((20 - spectrum_ring * 2.5) * scale * (0.9 + 0.1 * math.sin(t * 10)))
            s_color = rainbow_spectrum[spectrum_ring]
            s_alpha = 180 - spectrum_ring * 20
            if s_r > 0:
                pygame.draw.circle(surface, (*s_color, s_alpha), (cx, cy), s_r)
        # 核心白光
        pygame.draw.circle(surface, (255, 255, 255, 250), (cx, cy), int(5 * scale))
        
        # 色散效应（光的分解）
        dispersion_count = 14
        for disp in range(dispersion_count):
            disp_life = ((t * 35 + disp * 4) % 70) / 70
            disp_angle = disp * (6.28 / dispersion_count) + t * 2
            disp_dist = int(disp_life * 50 * scale)
            disp_x = cx + int(math.cos(disp_angle) * disp_dist)
            disp_y = cy + int(math.sin(disp_angle) * disp_dist * 0.35)
            
            # 色散粒子颜色（基于位置）
            disp_hue = disp / dispersion_count
            disp_color_idx = int(disp_hue * 7) % 7
            disp_color = rainbow_spectrum[disp_color_idx]
            disp_alpha = int(220 * (1 - disp_life))
            
            if disp_alpha > 20:
                disp_size = max(1, int((4 - disp_life * 2.5) * scale))
                pygame.draw.circle(surface, (*disp_color, disp_alpha), (disp_x, disp_y), disp_size)
                # 拖尾
                for trail in range(4):
                    trail_life = disp_life - trail * 0.06
                    if trail_life > 0:
                        trail_dist = int(trail_life * 50 * scale)
                        trail_x = cx + int(math.cos(disp_angle) * trail_dist)
                        trail_y = cy + int(math.sin(disp_angle) * trail_dist * 0.35)
                        trail_alpha = int((disp_alpha - 20) * (1 - trail * 0.25))
                        if trail_alpha > 0:
                            pygame.draw.circle(surface, (*disp_color, trail_alpha), (trail_x, trail_y), max(1, int((disp_size - trail) * scale)))
        
        # 虹彩粒子云（环绕飘舞）
        for particle in range(30):
            particle_angle = t * 2.2 + particle * 0.4
            particle_orbit_r = (18 + 12 * math.sin(t * 1.5 + particle)) * scale
            particle_height = math.sin(t * 3 + particle * 0.7) * 15 * scale
            particle_x = cx + int(math.cos(particle_angle) * particle_orbit_r)
            particle_y = cy + int(math.sin(particle_angle) * particle_orbit_r * 0.35) - int(particle_height)
            
            # 粒子颜色（彩虹循环）
            particle_hue = ((t * 2 + particle * 0.1) % 1.0)
            particle_color_idx = int(particle_hue * 7) % 7
            particle_color = rainbow_spectrum[particle_color_idx]
            particle_pulse = 0.6 + 0.4 * math.sin(t * 8 + particle)
            particle_alpha = int(180 * particle_pulse)
            particle_size = max(1, int(3 * scale * particle_pulse))
            
            pygame.draw.circle(surface, (*particle_color, particle_alpha), (particle_x, particle_y), particle_size)
            # 粒子光晕
            pygame.draw.circle(surface, (*particle_color, particle_alpha // 2), (particle_x, particle_y), particle_size * 2)
        
        # 光晕干涉（波动环）
        interference_phase = (t * 3) % 1.0
        for wave in range(6):
            wave_r = int((12 + (interference_phase + wave * 0.15) * 45) * scale)
            wave_hue = (interference_phase + wave * 0.15) % 1.0
            wave_color_idx = int(wave_hue * 7) % 7
            wave_color = rainbow_spectrum[wave_color_idx]
            wave_alpha = int(160 * (1 - (interference_phase + wave * 0.15) % 1.0))
            
            if wave_alpha > 20:
                pygame.draw.circle(surface, (*wave_color, wave_alpha), (cx, cy), wave_r, max(1, int(2 * scale)))
        
        # 彩虹光桥（连接水晶）
        if int(t * 5) % 10 < 7:  # 间歇出现
            bridge_count = 8
            for bridge in range(bridge_count // 2):
                bridge_angle_1 = bridge * (6.28 / (bridge_count // 2)) + t * 1.5
                bridge_angle_2 = (bridge + 1) * (6.28 / (bridge_count // 2)) + t * 1.5
                bridge_dist = 35 * scale
                
                bridge_x1 = cx + int(math.cos(bridge_angle_1) * bridge_dist)
                bridge_y1 = cy + int(math.sin(bridge_angle_1) * bridge_dist * 0.35)
                bridge_x2 = cx + int(math.cos(bridge_angle_2) * bridge_dist)
                bridge_y2 = cy + int(math.sin(bridge_angle_2) * bridge_dist * 0.35)
                
                bridge_hue = (bridge / (bridge_count // 2) + t) % 1.0
                bridge_color_idx = int(bridge_hue * 7) % 7
                bridge_color = rainbow_spectrum[bridge_color_idx]
                bridge_alpha = int(150 + 100 * math.sin(t * 4 + bridge))
                
                # 弧形光桥（用多段直线近似）
                bridge_segs = 8
                for seg in range(bridge_segs):
                    seg_progress = seg / bridge_segs
                    seg_x = int(bridge_x1 + (bridge_x2 - bridge_x1) * seg_progress)
                    seg_y = int(bridge_y1 + (bridge_y2 - bridge_y1) * seg_progress)
                    arc_offset = -math.sin(seg_progress * math.pi) * 10 * scale
                    seg_x += int(arc_offset * math.cos(bridge_angle_1 + math.pi / 2))
                    seg_y += int(arc_offset * math.sin(bridge_angle_1 + math.pi / 2) * 0.35)
                    
                    pygame.draw.circle(surface, (*bridge_color, bridge_alpha), (seg_x, seg_y), max(1, int(2 * scale)))
    
    elif theme_name == "void":
        # ====== 虚空撕裂：现实裂缝+虚空触须+时空碎片+虚空之眼+暗物质+次元门+虚空漩涡 ======
        # 现实裂缝（多层+锯齿裂纹）
        for crack_layer in range(3):
            crack_count = 4 + crack_layer * 2
            for crack in range(crack_count):
                crack_angle = crack * (6.28 / crack_count) + t * (0.25 - crack_layer * 0.08) + crack_layer * 0.785
                crack_points = [(cx, cy)]
                crack_segs = 12 - crack_layer * 2
                
                for seg in range(crack_segs):
                    seg_progress = (seg + 1) / crack_segs
                    seg_dist = int(seg_progress * (45 - crack_layer * 8) * scale)
                    # 锯齿抖动
                    seg_zigzag = math.sin(t * 8 + seg * 3 + crack) * (6 - crack_layer * 2) * scale
                    seg_perp_angle = crack_angle + math.pi / 2
                    cx_point = cx + int(math.cos(crack_angle) * seg_dist + math.cos(seg_perp_angle) * seg_zigzag)
                    cy_point = cy + int(math.sin(crack_angle) * seg_dist * 0.35 + math.sin(seg_perp_angle) * seg_zigzag * 0.35)
                    crack_points.append((cx_point, cy_point))
                
                if len(crack_points) > 1:
                    crack_alpha = int((230 - crack_layer * 35) * (0.8 + 0.2 * math.sin(t * 4 + crack)))
                    crack_thickness = max(1, int((4 - crack_layer) * scale))
                    pygame.draw.lines(surface, (*theme["accent"], crack_alpha), False, crack_points, crack_thickness)
                    # 裂缝内部虚空（暗紫色）
                    pygame.draw.lines(surface, (80, 40, 120, crack_alpha - 40), False, crack_points, max(1, crack_thickness // 2))
                    # 裂缝发光边缘
                    for i, pt in enumerate(crack_points):
                        if i % 2 == 0:
                            glow_pulse = 0.6 + 0.4 * math.sin(t * 10 + i + crack)
                            pygame.draw.circle(surface, (*theme["glow"], int(crack_alpha * glow_pulse)), pt, max(1, int(2 * scale)))
        
        # 虚空触须（有机波动+吸盘）
        for tendril_set in range(2):
            tendril_count = 6 + tendril_set * 3
            tendril_speed = -1.3 + tendril_set * 0.4
            for tendril in range(tendril_count):
                tendril_angle = t * tendril_speed + tendril * (6.28 / tendril_count) + tendril_set * 1.047
                tendril_points = []
                tendril_segs = 15 - tendril_set * 3
                
                for seg in range(tendril_segs):
                    seg_progress = seg / tendril_segs
                    seg_base_dist = (12 + seg_progress * (35 - tendril_set * 10)) * scale
                    # 有机波动（双频率）
                    seg_wave_1 = math.sin(t * 6 + seg * 1.2 + tendril) * (10 - tendril_set * 3) * scale
                    seg_wave_2 = math.cos(t * 9 + seg * 0.8 + tendril_set) * 5 * scale
                    seg_dist = seg_base_dist + seg_wave_1
                    seg_perp = seg_wave_2
                    
                    tendril_x = cx + int(math.cos(tendril_angle) * seg_dist + seg_perp * math.cos(tendril_angle + math.pi / 2))
                    tendril_y = cy + int(math.sin(tendril_angle) * seg_dist * 0.35 + seg_perp * math.sin(tendril_angle + math.pi / 2) * 0.35)
                    tendril_points.append((tendril_x, tendril_y))
                
                if len(tendril_points) > 1:
                    tendril_pulse = 0.7 + 0.3 * math.sin(t * 3.5 + tendril + tendril_set)
                    tendril_alpha = int((200 - tendril_set * 40) * tendril_pulse)
                    tendril_thickness = max(1, int((5 - tendril_set * 2) * scale))
                    
                    # 触须主体（渐变粗细）
                    for i in range(len(tendril_points) - 1):
                        seg_thickness = max(1, int(tendril_thickness * (1 - i / len(tendril_points) * 0.6)))
                        pygame.draw.line(surface, (*theme["secondary"], tendril_alpha), 
                                       tendril_points[i], tendril_points[i + 1], seg_thickness)
                    
                    # 吸盘（每隔3节）
                    for i, pt in enumerate(tendril_points):
                        if i % 3 == 0 and i > 0:
                            sucker_pulse = 0.7 + 0.3 * math.sin(t * 8 + i + tendril)
                            sucker_size = int((4 - tendril_set) * scale * sucker_pulse)
                            sucker_alpha = tendril_alpha - 30
                            if sucker_alpha > 0:
                                # 吸盘外圈
                                pygame.draw.circle(surface, (*theme["nebula"], sucker_alpha), pt, sucker_size)
                                # 吸盘中心
                                pygame.draw.circle(surface, (40, 20, 60, sucker_alpha + 50), pt, sucker_size // 2)
        
        # 时空碎片（三维旋转+扭曲）
        for shard_ring in range(3):
            shard_count = 10 + shard_ring * 5
            for shard in range(shard_count):
                shard_orbit_angle = t * (2.5 - shard_ring * 0.6) + shard * (6.28 / shard_count)
                shard_orbit_r = (22 + shard_ring * 10 + 8 * math.sin(t * 2 + shard)) * scale
                shard_x = cx + int(math.cos(shard_orbit_angle) * shard_orbit_r)
                shard_y = cy + int(math.sin(shard_orbit_angle) * shard_orbit_r * 0.35)
                
                # 碎片自转
                shard_rot = t * (5 + shard_ring) + shard * 0.7
                shard_pulse = 0.75 + 0.25 * math.sin(t * 6 + shard + shard_ring)
                shard_alpha = int((170 - shard_ring * 25) * shard_pulse)
                
                # 不规则四边形碎片
                shard_points = []
                for p in range(4):
                    p_angle = shard_rot + p * (math.pi / 2)
                    p_base_dist = (5 + shard_ring + shard % 3) * scale
                    # 扭曲变形
                    p_distort = 1.0 + 0.3 * math.sin(t * 7 + p + shard)
                    p_dist = p_base_dist * p_distort
                    px = shard_x + int(math.cos(p_angle) * p_dist)
                    py = shard_y + int(math.sin(p_angle) * p_dist * 0.5)
                    shard_points.append((px, py))
                
                if len(shard_points) == 4:
                    # 碎片主体
                    pygame.draw.polygon(surface, (*theme["nebula"], shard_alpha), shard_points)
                    # 碎片边缘（虚空光）
                    pygame.draw.polygon(surface, (*theme["accent"], shard_alpha + 60), shard_points, max(1, int(2 * scale)))
                    # 碎片核心光点
                    pygame.draw.circle(surface, (*theme["glow"], shard_alpha + 50), (shard_x, shard_y), max(1, int(1.5 * scale)))
        
        # 虚空之眼（多重凝视）
        for eye_set in range(2):
            eye_count = 5 + eye_set * 3
            eye_dist_base = (32 + eye_set * 14) * scale
            for eye in range(eye_count):
                eye_angle = t * (1.2 - eye_set * 0.4) + eye * (6.28 / eye_count)
                eye_dist = eye_dist_base + 6 * math.sin(t * 2.5 + eye) * scale
                eye_x = cx + int(math.cos(eye_angle) * eye_dist)
                eye_y = cy + int(math.sin(eye_angle) * eye_dist * 0.35)
                eye_pulse = 0.75 + 0.25 * math.sin(t * 5 + eye + eye_set)
                eye_alpha = int((220 - eye_set * 40) * eye_pulse)
                
                # 眼眶（椭圆）
                eye_w = int((9 - eye_set * 2) * scale * eye_pulse)
                eye_h = int((6 - eye_set) * scale * eye_pulse)
                pygame.draw.ellipse(surface, (*theme["secondary"], eye_alpha), 
                                  (eye_x - eye_w, eye_y - eye_h, eye_w * 2, eye_h * 2))
                pygame.draw.ellipse(surface, (*theme["nebula"], eye_alpha), 
                                  (eye_x - eye_w, eye_y - eye_h, eye_w * 2, eye_h * 2), max(1, int(2 * scale)))
                
                # 虚空虹膜（紫黑色）
                iris_w = int(eye_w * 0.7)
                iris_h = int(eye_h * 0.7)
                pygame.draw.ellipse(surface, (100, 50, 130, eye_alpha), 
                                  (eye_x - iris_w, eye_y - iris_h, iris_w * 2, iris_h * 2))
                
                # 瞳孔（凝视中心）
                look_to_center = math.atan2(cy - eye_y, cx - eye_x)
                pupil_offset_x = int(math.cos(look_to_center) * iris_w * 0.3)
                pupil_offset_y = int(math.sin(look_to_center) * iris_h * 0.3)
                pupil_x = eye_x + pupil_offset_x
                pupil_y = eye_y + pupil_offset_y
                pupil_size = max(1, int(3 * scale))
                pygame.draw.circle(surface, (20, 10, 30, 255), (pupil_x, pupil_y), pupil_size)
                
                # 眼光（诡异微光）
                highlight_x = pupil_x - int(pupil_size * 0.4)
                highlight_y = pupil_y - int(pupil_size * 0.4)
                pygame.draw.circle(surface, (*theme["glow"], 220), (highlight_x, highlight_y), max(1, int(1 * scale)))
        
        # 暗物质粒子（漂浮暗点）
        for dark_matter in range(25):
            dm_life = ((t * 20 + dark_matter * 5) % 80) / 80
            dm_angle = dark_matter * 0.6 + math.sin(t * 1.5 + dark_matter) * 2
            dm_dist = int((15 + dm_life * 40) * scale)
            dm_x = cx + int(math.cos(dm_angle) * dm_dist)
            dm_y = cy + int(math.sin(dm_angle) * dm_dist * 0.35)
            dm_alpha = int(180 * (1 - dm_life * 0.7))
            
            if dm_alpha > 20:
                dm_size = max(1, int((3 - dm_life * 1.5) * scale))
                # 暗物质核心（深紫黑）
                pygame.draw.circle(surface, (60, 30, 80, dm_alpha), (dm_x, dm_y), dm_size)
                # 暗物质光环（虚空光）
                pygame.draw.circle(surface, (*theme["nebula"], dm_alpha // 2), (dm_x, dm_y), dm_size * 2)
        
        # 次元门（虚空传送门）
        portal_phase = (t * 2) % 1.0
        if portal_phase < 0.8:  # 门开启周期
            portal_size_factor = 1.0 if portal_phase < 0.6 else (1.0 - (portal_phase - 0.6) / 0.2)
            portal_alpha_factor = min(1.0, portal_phase / 0.2) if portal_phase < 0.2 else portal_size_factor
            
            # 门框（椭圆）
            portal_w = int(20 * scale * portal_size_factor)
            portal_h = int(28 * scale * portal_size_factor)
            portal_alpha = int(200 * portal_alpha_factor)
            
            # 多层门框
            for layer in range(4):
                layer_w = portal_w + layer * int(3 * scale)
                layer_h = portal_h + layer * int(4 * scale)
                layer_alpha = portal_alpha - layer * 40
                if layer_alpha > 0:
                    pygame.draw.ellipse(surface, (*theme["accent"], layer_alpha), 
                                      (cx - layer_w, cy - layer_h, layer_w * 2, layer_h * 2), 
                                      max(1, int((4 - layer) * scale)))
            
            # 门内虚空（暗紫黑洞）
            for void_layer in range(6):
                void_w = int(portal_w * (1 - void_layer * 0.15))
                void_h = int(portal_h * (1 - void_layer * 0.15))
                void_color_factor = void_layer / 6
                void_color = tuple(int(80 * (1 - void_color_factor)) for _ in range(3))
                void_alpha = 150 + void_layer * 15
                if void_w > 0 and void_h > 0:
                    pygame.draw.ellipse(surface, (*void_color, void_alpha), 
                                      (cx - void_w, cy - void_h, void_w * 2, void_h * 2))
            
            # 门内粒子流（进入虚空）
            for particle in range(12):
                particle_angle = particle * (math.pi / 6) + t * 8
                particle_progress = ((t * 40 + particle * 5) % 30) / 30
                particle_start_r = portal_w * 1.2
                particle_end_r = 0
                particle_r = int(particle_start_r * (1 - particle_progress))
                particle_x = cx + int(math.cos(particle_angle) * particle_r)
                particle_y = cy + int(math.sin(particle_angle) * particle_r * (portal_h / portal_w) * 0.35)
                particle_alpha = int(portal_alpha * (1 - particle_progress))
                
                if particle_alpha > 0:
                    pygame.draw.circle(surface, (*theme["glow"], particle_alpha), (particle_x, particle_y), max(1, int(2 * scale)))
        
        # 虚空漩涡（中心吸引）
        vortex_arms = 5
        for arm in range(vortex_arms):
            arm_offset = arm * (6.28 / vortex_arms)
            for seg in range(20):
                seg_progress = seg / 20
                vortex_angle = arm_offset + seg_progress * math.pi * 3 + t * 2.5
                vortex_dist = int((5 + seg_progress * 30) * scale)
                vortex_x = cx + int(math.cos(vortex_angle) * vortex_dist)
                vortex_y = cy + int(math.sin(vortex_angle) * vortex_dist * 0.35)
                vortex_alpha = int(190 * (1 - seg_progress))
                
                if vortex_alpha > 20:
                    vortex_size = max(1, int((4 - seg_progress * 2) * scale))
                    pygame.draw.circle(surface, (*theme["secondary"], vortex_alpha), (vortex_x, vortex_y), vortex_size)
    
    # ============================================================
    #   第四层：剪刀刀刃系统 - 标准剪刀结构
    # ============================================================
    blade_open_angle = 20 + 12 * math.sin(t * 1.0)  # 张合角度（加大让剪刀更明显）
    blade_pulse = 0.85 + 0.15 * math.sin(t * 2.5)
    blade_rotation = t * 0.5  # 整体旋转
    
    # === 上剪刃（午夜蓝刀刃）- 剪刀片形状 ===
    upper_blade_len = int(65 * scale)  # 增加长度：45->65
    upper_blade_width = int(10 * scale)  # 增加宽度：6->10
    upper_handle_len = int(8 * scale)  # 减少手柄长度让刀刃更突出
    
    # 剪刀刀片形状（渐窄的三角形刀刃）
    upper_points = [
        # 刀柄连接处（宽）
        (cx - upper_blade_width // 2, cy - upper_handle_len),
        (cx + upper_blade_width // 2, cy - upper_handle_len),
        # 中部渐窄
        (cx + upper_blade_width // 3, cy - upper_handle_len - upper_blade_len * 0.5),
        # 刀尖（锐利）
        (cx, cy - upper_handle_len - upper_blade_len),
        # 刀背（另一侧）
        (cx - upper_blade_width // 3, cy - upper_handle_len - upper_blade_len * 0.5),
    ]
    
    # 旋转 + 张合
    rotated_upper = []
    for px, py in upper_points:
        # 先绕中心应用张合角度
        angle1 = math.radians(-blade_open_angle)
        rx1 = cx + (px - cx) * math.cos(angle1) - (py - cy) * math.sin(angle1)
        ry1 = cy + (px - cx) * math.sin(angle1) + (py - cy) * math.cos(angle1)
        # 再应用整体旋转
        angle2 = blade_rotation
        rx2 = cx + (rx1 - cx) * math.cos(angle2) - (ry1 - cy) * math.sin(angle2)
        ry2 = cy + (rx1 - cx) * math.sin(angle2) + (ry1 - cy) * math.cos(angle2)
        rotated_upper.append((int(rx2), int(ry2)))
    
    # 刀刃阴影
    shadow_offset = int(3 * scale)
    shadow_upper = [(x + shadow_offset, y + shadow_offset) for x, y in rotated_upper]
    pygame.draw.polygon(surface, (0, 0, 0, 120), shadow_upper)
    
    # 刀刃主体
    pygame.draw.polygon(surface, theme["blade_upper"], rotated_upper)
    
    # 刀刃边缘高光（让刀刃更锋利）
    pygame.draw.line(surface, (*theme["glow"], 200), rotated_upper[0], rotated_upper[2], 2)
    pygame.draw.line(surface, (*theme["glow"], 200), rotated_upper[2], rotated_upper[4], 3)
    
    # 刀刃锯齿边缘（剪刀特征）- 在刀背添加
    serration_count = 8
    for serr in range(serration_count):
        serr_progress = serr / serration_count
        # 从刀柄到刀尖的刀背
        base_x = int(rotated_upper[0][0] + (rotated_upper[4][0] - rotated_upper[0][0]) * serr_progress)
        base_y = int(rotated_upper[0][1] + (rotated_upper[4][1] - rotated_upper[0][1]) * serr_progress)
        # 锯齿向外突出
        serr_angle = math.atan2(rotated_upper[4][1] - rotated_upper[0][1], 
                                rotated_upper[4][0] - rotated_upper[0][0]) + math.pi / 2
        serr_len = int(2 * scale)
        serr_x = base_x + int(math.cos(serr_angle) * serr_len)
        serr_y = base_y + int(math.sin(serr_angle) * serr_len)
        pygame.draw.line(surface, theme["accent"], (base_x, base_y), (serr_x, serr_y), 1)
    
    # 刀刃光晕（4层）
    for glow_layer in range(4):
        glow_alpha = int((140 - glow_layer * 35) * blade_pulse)
        if glow_alpha > 0:
            pygame.draw.polygon(surface, (*theme["accent"], glow_alpha), 
                              rotated_upper, 2 + glow_layer)
    
    # 刀刃能量纹理（8条）
    for vein_idx in range(8):
        vein_progress = vein_idx / 8
        # 从刀柄到刀尖
        base_idx = 0 if vein_idx % 2 == 0 else 1
        tip_idx = 4
        vx = int(rotated_upper[base_idx][0] + (rotated_upper[tip_idx][0] - rotated_upper[base_idx][0]) * vein_progress)
        vy = int(rotated_upper[base_idx][1] + (rotated_upper[tip_idx][1] - rotated_upper[base_idx][1]) * vein_progress)
        vein_size = max(1, int(3 * (1 - vein_progress)))
        vein_alpha = int(120 * (1 - vein_progress) * blade_pulse)
        if vein_alpha > 0:
            pygame.draw.circle(surface, (*theme["cosmic_vein"], vein_alpha), 
                             (vx, vy), vein_size)
    
    # 刀刃星云纹理（横向条纹）
    for stripe in range(4):  # 减少到4条（因为只有5个点）
        stripe_progress = stripe / 4
        idx1 = 0
        idx2 = 1
        sx1 = int(rotated_upper[idx1][0] + (rotated_upper[4][0] - rotated_upper[idx1][0]) * stripe_progress)
        sy1 = int(rotated_upper[idx1][1] + (rotated_upper[4][1] - rotated_upper[idx1][1]) * stripe_progress)
        sx2 = int(rotated_upper[idx2][0] + (rotated_upper[4][0] - rotated_upper[idx2][0]) * stripe_progress)
        sy2 = int(rotated_upper[idx2][1] + (rotated_upper[4][1] - rotated_upper[idx2][1]) * stripe_progress)
        stripe_alpha = int(80 * (1 - stripe_progress))
        if stripe_alpha > 0:
            pygame.draw.line(surface, (*theme["nebula"], stripe_alpha), 
                           (sx1, sy1), (sx2, sy2), 1)
    
    # 刀尖光芒爆发
    tip_pos = rotated_upper[4]
    tip_glow_radius = int((6 + 4 * math.sin(t * 10)) * scale)
    for glow_ring in range(5):
        ring_radius = tip_glow_radius + glow_ring * 4
        ring_alpha = int((240 - glow_ring * 50) * blade_pulse)
        if ring_alpha > 0:
            pygame.draw.circle(surface, (*theme["glow"], ring_alpha), 
                             tip_pos, ring_radius)
    
    # 刀尖能量射线（6条）
    for ray in range(6):
        ray_angle = t * 8 + ray * (6.28 / 6)
        ray_len = int((12 + 6 * math.sin(t * 12 + ray)) * scale)
        ray_end_x = tip_pos[0] + int(math.cos(ray_angle) * ray_len)
        ray_end_y = tip_pos[1] + int(math.sin(ray_angle) * ray_len)
        ray_alpha = int(200 * (0.7 + 0.3 * math.sin(t * 15 + ray)))
        pygame.draw.line(surface, (*theme["glow"], ray_alpha), 
                       tip_pos, (ray_end_x, ray_end_y), 2)
    
    # === 上剪刃刀柄环（手指孔）- 剪刀标志性特征 ===
    upper_handle_ring_center_x = cx
    upper_handle_ring_center_y = cy + int(12 * scale)  # 向下移动：8->12
    upper_ring_radius = int(14 * scale)  # 增大环：10->14
    
    # 先计算旋转后的位置
    angle1 = math.radians(-blade_open_angle)
    angle2 = blade_rotation
    
    # 刀柄环中心点旋转
    rx1 = cx + (upper_handle_ring_center_x - cx) * math.cos(angle1) - (upper_handle_ring_center_y - cy) * math.sin(angle1)
    ry1 = cy + (upper_handle_ring_center_x - cx) * math.sin(angle1) + (upper_handle_ring_center_y - cy) * math.cos(angle1)
    rx2 = cx + (rx1 - cx) * math.cos(angle2) - (ry1 - cy) * math.sin(angle2)
    ry2 = cy + (rx1 - cx) * math.sin(angle2) + (ry1 - cy) * math.cos(angle2)
    upper_ring_pos = (int(rx2), int(ry2))
    
    # 刀柄环外圈
    pygame.draw.circle(surface, theme["blade_upper"], upper_ring_pos, upper_ring_radius, int(4 * scale))
    # 刀柄环光晕
    for ring_glow in range(3):
        glow_r = upper_ring_radius + ring_glow * 3
        glow_alpha = int((180 - ring_glow * 50) * blade_pulse)
        pygame.draw.circle(surface, (*theme["accent"], glow_alpha), upper_ring_pos, glow_r, 2)
    # 刀柄环内部空洞（黑色）
    pygame.draw.circle(surface, (0, 0, 0, 200), upper_ring_pos, upper_ring_radius - int(4 * scale))
    
    # 刀柄与刀环的连接杆
    connection_start = rotated_upper[0] if abs(rotated_upper[0][0] - upper_ring_pos[0]) < abs(rotated_upper[1][0] - upper_ring_pos[0]) else rotated_upper[1]
    pygame.draw.line(surface, theme["blade_upper"], connection_start, upper_ring_pos, int(4 * scale))
    pygame.draw.line(surface, (*theme["accent"], 150), connection_start, upper_ring_pos, int(2 * scale))
    
    # === 下剪刃部分 ===
    lower_blade_len = int(65 * scale)  # 增加长度：45->65
    lower_blade_width = int(10 * scale)  # 增加宽度：6->10
    lower_handle_len = int(8 * scale)  # 减少手柄长度：12->8
    
    # 剪刀刀片形状（对称）
    lower_points = [
        (cx - lower_blade_width // 2, cy - lower_handle_len),
        (cx + lower_blade_width // 2, cy - lower_handle_len),
        (cx + lower_blade_width // 3, cy - lower_handle_len - lower_blade_len * 0.5),
        (cx, cy - lower_handle_len - lower_blade_len),
        (cx - lower_blade_width // 3, cy - lower_handle_len - lower_blade_len * 0.5),
    ]
    
    rotated_lower = []
    for px, py in lower_points:
        angle1 = math.radians(blade_open_angle)
        rx1 = cx + (px - cx) * math.cos(angle1) - (py - cy) * math.sin(angle1)
        ry1 = cy + (px - cx) * math.sin(angle1) + (py - cy) * math.cos(angle1)
        angle2 = blade_rotation
        rx2 = cx + (rx1 - cx) * math.cos(angle2) - (ry1 - cy) * math.sin(angle2)
        ry2 = cy + (rx1 - cx) * math.sin(angle2) + (ry1 - cy) * math.cos(angle2)
        rotated_lower.append((int(rx2), int(ry2)))
    
    shadow_lower = [(x + shadow_offset, y + shadow_offset) for x, y in rotated_lower]
    pygame.draw.polygon(surface, (0, 0, 0, 120), shadow_lower)
    pygame.draw.polygon(surface, theme["blade_lower"], rotated_lower)
    
    # 下刃边缘高光
    pygame.draw.line(surface, (*theme["glow"], 200), rotated_lower[0], rotated_lower[2], 2)
    pygame.draw.line(surface, (*theme["glow"], 200), rotated_lower[2], rotated_lower[4], 3)
    
    # 下刃锯齿边缘
    for serr in range(serration_count):
        serr_progress = serr / serration_count
        base_x = int(rotated_lower[1][0] + (rotated_lower[4][0] - rotated_lower[1][0]) * serr_progress)
        base_y = int(rotated_lower[1][1] + (rotated_lower[4][1] - rotated_lower[1][1]) * serr_progress)
        serr_angle = math.atan2(rotated_lower[4][1] - rotated_lower[1][1], 
                                rotated_lower[4][0] - rotated_lower[1][0]) - math.pi / 2
        serr_len = int(2 * scale)
        serr_x = base_x + int(math.cos(serr_angle) * serr_len)
        serr_y = base_y + int(math.sin(serr_angle) * serr_len)
        pygame.draw.line(surface, theme["primary"], (base_x, base_y), (serr_x, serr_y), 1)
    
    # 下刃光晕
    for glow_layer in range(4):
        glow_alpha = int((140 - glow_layer * 35) * blade_pulse)
        if glow_alpha > 0:
            pygame.draw.polygon(surface, (*theme["primary"], glow_alpha), 
                              rotated_lower, 2 + glow_layer)
    
    # 下刃能量脉冲（流动效果）
    for pulse_idx in range(10):
        pulse_phase = (t * 5 + pulse_idx * 0.3) % 1.0
        if pulse_phase < 0.8:
            base_pt = rotated_lower[0] if pulse_idx % 2 == 0 else rotated_lower[1]
            tip_pt = rotated_lower[4]
            px = int(base_pt[0] + (tip_pt[0] - base_pt[0]) * pulse_phase)
            py = int(base_pt[1] + (tip_pt[1] - base_pt[1]) * pulse_phase)
            pulse_size = int(4 * (1 - pulse_phase))
            pulse_alpha = int(220 * (1 - pulse_phase))
            if pulse_alpha > 0:
                pygame.draw.circle(surface, (*theme["accent"], pulse_alpha), 
                                 (px, py), pulse_size)
    
    # 下刃刀尖光晕
    lower_tip = rotated_lower[4]
    for glow_ring in range(5):
        ring_radius = tip_glow_radius + glow_ring * 4
        ring_alpha = int((240 - glow_ring * 50) * blade_pulse)
        if ring_alpha > 0:
            pygame.draw.circle(surface, (*theme["glow"], ring_alpha), 
                             lower_tip, ring_radius)
    
    # 下刃能量射线
    for ray in range(6):
        ray_angle = -t * 8 + ray * (6.28 / 6)
        ray_len = int((12 + 6 * math.sin(t * 12 + ray)) * scale)
        ray_end_x = lower_tip[0] + int(math.cos(ray_angle) * ray_len)
        ray_end_y = lower_tip[1] + int(math.sin(ray_angle) * ray_len)
        ray_alpha = int(200 * (0.7 + 0.3 * math.sin(t * 15 + ray)))
        pygame.draw.line(surface, (*theme["glow"], ray_alpha), 
                       lower_tip, (ray_end_x, ray_end_y), 2)
    
    # === 下剪刃刀柄环（手指孔）===
    lower_handle_ring_center_x = cx
    lower_handle_ring_center_y = cy + int(12 * scale)  # 向下移动：8->12
    lower_ring_radius = int(14 * scale)  # 增大环：10->14
    
    # 刀柄环中心点旋转
    angle1_lower = math.radians(blade_open_angle)
    rx1_lower = cx + (lower_handle_ring_center_x - cx) * math.cos(angle1_lower) - (lower_handle_ring_center_y - cy) * math.sin(angle1_lower)
    ry1_lower = cy + (lower_handle_ring_center_x - cx) * math.sin(angle1_lower) + (lower_handle_ring_center_y - cy) * math.cos(angle1_lower)
    rx2_lower = cx + (rx1_lower - cx) * math.cos(angle2) - (ry1_lower - cy) * math.sin(angle2)
    ry2_lower = cy + (rx1_lower - cx) * math.sin(angle2) + (ry1_lower - cy) * math.cos(angle2)
    lower_ring_pos = (int(rx2_lower), int(ry2_lower))
    
    # 刀柄环外圈
    pygame.draw.circle(surface, theme["blade_lower"], lower_ring_pos, lower_ring_radius, int(4 * scale))
    # 刀柄环光晕
    for ring_glow in range(3):
        glow_r = lower_ring_radius + ring_glow * 3
        glow_alpha = int((180 - ring_glow * 50) * blade_pulse)
        pygame.draw.circle(surface, (*theme["primary"], glow_alpha), lower_ring_pos, glow_r, 2)
    # 刀柄环内部空洞
    pygame.draw.circle(surface, (0, 0, 0, 200), lower_ring_pos, lower_ring_radius - int(4 * scale))
    
    # 刀柄与刀环的连接杆
    connection_start_lower = rotated_lower[0] if abs(rotated_lower[0][0] - lower_ring_pos[0]) < abs(rotated_lower[1][0] - lower_ring_pos[0]) else rotated_lower[1]
    pygame.draw.line(surface, theme["blade_lower"], connection_start_lower, lower_ring_pos, int(4 * scale))
    pygame.draw.line(surface, (*theme["primary"], 150), connection_start_lower, lower_ring_pos, int(2 * scale))
    
    # ============================================================
    #   第五层：剪刀铰链机构 - 精密齿轮系统
    # ============================================================
    hinge_core_radius = int(7 * scale)
    
    # 外部护环（3层）
    for ring_idx in range(3):
        ring_radius = hinge_core_radius + 3 + ring_idx * 3
        ring_pulse = 0.9 + 0.1 * math.sin(t * 4 + ring_idx)
        ring_alpha = int((220 - ring_idx * 50) * ring_pulse)
        pygame.draw.circle(surface, (*theme["accent"], ring_alpha), 
                         (cx, cy), ring_radius, 2)
        # 环上装饰节点
        for node in range(8):
            node_angle = t * 2 + node * (6.28 / 8) + ring_idx * 0.4
            node_x = cx + int(math.cos(node_angle) * ring_radius)
            node_y = cy + int(math.sin(node_angle) * ring_radius)
            pygame.draw.circle(surface, (*theme["glow"], ring_alpha), 
                             (node_x, node_y), 2)
    
    # 旋转齿轮（12齿）
    gear_teeth = 12
    gear_radius = hinge_core_radius + 1
    gear_tooth_len = int(4 * scale)
    for tooth in range(gear_teeth):
        tooth_angle = -t * 4 + tooth * (6.28 / gear_teeth)
        tooth_base_x = cx + int(math.cos(tooth_angle) * gear_radius)
        tooth_base_y = cy + int(math.sin(tooth_angle) * gear_radius)
        tooth_tip_x = cx + int(math.cos(tooth_angle) * (gear_radius + gear_tooth_len))
        tooth_tip_y = cy + int(math.sin(tooth_angle) * (gear_radius + gear_tooth_len))
        pygame.draw.line(surface, theme["primary"], 
                       (tooth_base_x, tooth_base_y), (tooth_tip_x, tooth_tip_y), 2)
        # 齿尖光点
        pygame.draw.circle(surface, theme["glow"], (tooth_tip_x, tooth_tip_y), 2)
    
    # 铰链核心
    pygame.draw.circle(surface, theme["blade_lower"], (cx, cy), hinge_core_radius)
    pygame.draw.circle(surface, theme["accent"], (cx, cy), hinge_core_radius, 2)
    
    # 核心能量球
    core_pulse = 0.7 + 0.3 * math.sin(t * 6)
    core_size = int(4 * scale * core_pulse)
    for core_layer in range(3):
        layer_radius = core_size + core_layer * 2
        layer_alpha = int((250 - core_layer * 70) * core_pulse)
        pygame.draw.circle(surface, (*theme["glow"], layer_alpha), 
                         (cx, cy), layer_radius)
    
    # ============================================================
    #   第六层：星图仪驾驶舱 - 全息投影球体
    # ============================================================
    cockpit_radius = int(10 * scale)
    cockpit_y_offset = int(5 * scale)
    
    # 护盾脉冲（5层扩散）
    shield_pulse_phase = (t * 2) % 1.0
    for shield_ring in range(5):
        shield_radius = cockpit_radius + int(shield_pulse_phase * 20 * scale) + shield_ring * 3
        shield_alpha = int((180 - shield_pulse_phase * 150) * (1 - shield_ring * 0.15))
        if shield_alpha > 0:
            pygame.draw.circle(surface, (*theme["secondary"], shield_alpha), 
                             (cx, cy + cockpit_y_offset), shield_radius, 1)
    
    # 玻璃罩（透明半球）
    pygame.draw.circle(surface, (*theme["primary"], 80), 
                     (cx, cy + cockpit_y_offset), cockpit_radius)
    pygame.draw.circle(surface, (*theme["accent"], 200), 
                     (cx, cy + cockpit_y_offset), cockpit_radius, 2)
    # 高光
    highlight_offset = int(3 * scale)
    pygame.draw.circle(surface, (*theme["glow"], 150), 
                     (cx - highlight_offset, cy + cockpit_y_offset - highlight_offset), 
                     int(4 * scale))
    
    # 内部星座投影（旋转5芒星）
    projection_radius = int(6 * scale)
    for star_pt in range(5):
        star_angle = t * 2 + star_pt * (6.28 / 5)
        star_x = cx + int(math.cos(star_angle) * projection_radius)
        star_y = cy + cockpit_y_offset + int(math.sin(star_angle) * projection_radius)
        star_brightness = 0.6 + 0.4 * math.sin(t * 8 + star_pt)
        star_size = int(2 * star_brightness)
        star_alpha = int(220 * star_brightness)
        pygame.draw.circle(surface, (*theme["constellation"], star_alpha), 
                         (star_x, star_y), star_size)
    
    # 中心指示器
    pygame.draw.circle(surface, theme["glow"], 
                     (cx, cy + cockpit_y_offset), int(2 * scale))
    
    # ============================================================
    #   第七层：全息光翼系统 - 4对能量翼
    # ============================================================
    wing_pairs = 4
    for wing_pair in range(wing_pairs):
        wing_base_y = cy + int((10 + wing_pair * 8) * scale)
        wing_length = int((25 - wing_pair * 3) * scale)
        wing_segments = 6
        
        for side in [-1, 1]:  # 左右对称
            wing_points = [(cx, wing_base_y)]
            for seg in range(wing_segments):
                seg_ratio = (seg + 1) / wing_segments
                seg_x = cx + side * int(wing_length * seg_ratio)
                seg_y = wing_base_y + int(8 * scale * math.sin(seg_ratio * 3.14) * 
                                          (1 + 0.2 * math.sin(t * 3 + wing_pair + seg)))
                wing_points.append((seg_x, seg_y))
            
            # 翼膜渐变
            for seg in range(len(wing_points) - 1):
                seg_progress = seg / (len(wing_points) - 1)
                seg_alpha = int(150 * (1 - seg_progress) * (1 - wing_pair * 0.15))
                if seg_alpha > 0:
                    pygame.draw.line(surface, (*theme["accent"], seg_alpha), 
                                   wing_points[seg], wing_points[seg + 1], 
                                   max(1, int(3 * (1 - seg_progress))))
            
            # 翼尖光点
            wing_tip = wing_points[-1]
            tip_pulse = 0.6 + 0.4 * math.sin(t * 6 + wing_pair)
            tip_size = int(3 * tip_pulse)
            tip_alpha = int(220 * tip_pulse)
            pygame.draw.circle(surface, (*theme["glow"], tip_alpha), 
                             wing_tip, tip_size)
            
            # 翼尖轨迹
            for trail_pt in range(5):
                trail_progress = trail_pt / 5
                trail_x = wing_tip[0] - side * int(trail_progress * 10 * scale)
                trail_y = wing_tip[1] + int(trail_progress * 5 * scale)
                trail_alpha = int(120 * (1 - trail_progress))
                if trail_alpha > 0:
                    pygame.draw.circle(surface, (*theme["trail"], trail_alpha), 
                                     (trail_x, trail_y), max(1, 3 - trail_pt))
            
            # 翼骨结构
            for bone in range(wing_segments):
                bone_ratio = bone / wing_segments
                bone_x = cx + side * int(wing_length * bone_ratio)
                bone_y = wing_base_y + int(8 * scale * math.sin(bone_ratio * 3.14))
                pygame.draw.circle(surface, theme["primary"], (bone_x, bone_y), 2)
    
    # ============================================================
    #   第八层：星辰粒子发射器 - 双推进器
    # ============================================================
    thruster_y = cy + int(25 * scale)
    thruster_spacing = int(8 * scale)
    
    for thruster_side in [-1, 1]:
        thruster_x = cx + thruster_side * thruster_spacing
        
        # 喷口外壳
        thruster_width = int(6 * scale)
        thruster_height = int(10 * scale)
        pygame.draw.ellipse(surface, theme["primary"], 
                          (thruster_x - thruster_width // 2, thruster_y, 
                           thruster_width, thruster_height))
        pygame.draw.ellipse(surface, theme["accent"], 
                          (thruster_x - thruster_width // 2, thruster_y, 
                           thruster_width, thruster_height), 2)
        
        # 粒子喷射（12个粒子）
        for particle in range(12):
            particle_phase = (t * 8 + particle * 0.3) % 1.0
            particle_x = thruster_x + int(thruster_side * 2 * math.sin(t * 10 + particle))
            particle_y = thruster_y + thruster_height + int(particle_phase * 30 * scale)
            particle_size = max(1, int(4 * (1 - particle_phase)))
            particle_alpha = int(200 * (1 - particle_phase))
            if particle_alpha > 0:
                pygame.draw.circle(surface, (*theme["trail"], particle_alpha), 
                                 (particle_x, particle_y), particle_size)
                # 粒子尾迹
                if particle % 2 == 0:
                    trail_y = particle_y - int(5 * scale * particle_phase)
                    pygame.draw.line(surface, (*theme["trail"], particle_alpha // 2), 
                                   (particle_x, particle_y), (particle_x, trail_y), 1)
        
        # 喷口核心光
        core_glow_size = int((3 + 2 * math.sin(t * 12 + thruster_side)) * scale)
        pygame.draw.circle(surface, (*theme["glow"], 250), 
                         (thruster_x, thruster_y + thruster_height // 2), 
                         core_glow_size)
    
    # ============================================================
    #   第九层：中轴装甲板 - 3段连接装甲
    # ============================================================
    armor_segments = 3
    armor_start_y = cy - int(5 * scale)
    
    for seg in range(armor_segments):
        armor_y = armor_start_y + seg * int(10 * scale)
        armor_width = int((14 - seg * 2) * scale)
        armor_height = int(8 * scale)
        
        # 装甲板主体
        pygame.draw.rect(surface, theme["primary"], 
                       (cx - armor_width // 2, armor_y, armor_width, armor_height))
        pygame.draw.rect(surface, theme["accent"], 
                       (cx - armor_width // 2, armor_y, armor_width, armor_height), 1)
        
        # 装甲能量槽
        energy_bar_width = armor_width - 4
        energy_fill = 0.6 + 0.4 * math.sin(t * 3 + seg)
        energy_fill_width = int(energy_bar_width * energy_fill)
        pygame.draw.rect(surface, (*theme["glow"], 180), 
                       (cx - energy_fill_width // 2, armor_y + 2, 
                        energy_fill_width, armor_height - 4))
        
        # 装甲铆钉
        for rivet in range(3):
            rivet_x = cx - armor_width // 2 + 2 + rivet * (armor_width - 4) // 2
            pygame.draw.circle(surface, theme["secondary"], 
                             (rivet_x, armor_y + 2), 2)
            pygame.draw.circle(surface, theme["secondary"], 
                             (rivet_x, armor_y + armor_height - 2), 2)
    
    # ============================================================
    #   第十层：环境粒子效果 - 浮游星尘
    # ============================================================
    for floating_dust in range(20):
        dust_x = cx + int(60 * scale * math.sin(t * 0.8 + floating_dust * 1.5))
        dust_y = cy + int(50 * scale * math.cos(t * 0.6 + floating_dust * 1.2))
        dust_size = max(1, int(2 + math.sin(t * 5 + floating_dust)))
        dust_alpha = int(100 + 50 * math.sin(t * 4 + floating_dust))
        pygame.draw.circle(surface, (*theme["stardust"], dust_alpha), 
                         (dust_x, dust_y), dust_size)
    
    # 渲染完成 - 所有元素已直接绘制到surface上
