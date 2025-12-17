# -*- coding: utf-8 -*-
"""
亵渎天神·普罗维登斯 (Providence) 涂装系统
原型：Terraria Calamity Mod - Providence, the Profaned Goddess
风格：神圣几何 + 晶体矿物 + 重装堡垒 - 圣甲虫/神圣盾牌形态
"""
import pygame
import math

# ==================== 12种涂装主题 ====================
PROVIDENCE_THEMES = {
    # 默认涂装 - 亵渎天神原型
    "providence_default": {
        "name": "亵渎天神",
        "armor": (255, 215, 0),      # 圣金 Holy Gold
        "crystal": (255, 105, 180),  # 水晶粉 Crystal Pink
        "core": (255, 165, 0),       # 岩浆橙 Magma Orange
        "flame": (100, 100, 255),    # 亵渎蓝焰
        "glow": (255, 200, 100),     # 神圣光晕
        "border": (255, 180, 50),    # 金边
    },
    
    # 【昼夜循环系列】
    "providence_night": {
        "name": "夜殿守护",
        "armor": (80, 60, 120),      # 暗紫
        "crystal": (150, 100, 200),  # 月光紫
        "core": (200, 150, 255),     # 星辉紫
        "flame": (100, 80, 180),     # 暗焰
        "glow": (180, 150, 220),     # 月光晕
        "border": (120, 100, 180),   # 紫边
    },
    
    "providence_abyss": {
        "name": "深渊圣殿",
        "armor": (30, 50, 80),       # 深海蓝
        "crystal": (60, 120, 180),   # 海晶蓝
        "core": (80, 200, 220),      # 深渊青
        "flame": (40, 100, 150),     # 深焰
        "glow": (100, 180, 200),     # 深海光
        "border": (50, 80, 120),     # 深边
    },
    
    # 【矿物晶体系列】
    "providence_crystal": {
        "name": "棱镜女皇",
        "armor": (220, 220, 240),    # 钻石白
        "crystal": (180, 200, 255),  # 棱镜蓝
        "core": (255, 255, 255),     # 纯白核心
        "flame": (200, 220, 255),    # 冰蓝焰
        "glow": (230, 240, 255),     # 钻石光
        "border": (180, 200, 230),   # 冰边
    },
    
    "providence_magma": {
        "name": "熔岩神使",
        "armor": (180, 80, 30),      # 熔岩红
        "crystal": (255, 120, 50),   # 岩浆橙
        "core": (255, 200, 80),      # 熔核黄
        "flame": (255, 80, 30),      # 烈焰红
        "glow": (255, 150, 80),      # 熔光
        "border": (200, 100, 40),    # 岩边
    },
    
    "providence_frost": {
        "name": "永冻圣典",
        "armor": (180, 220, 255),    # 冰蓝
        "crystal": (200, 240, 255),  # 霜晶
        "core": (150, 200, 255),     # 冰核
        "flame": (100, 180, 255),    # 冰焰
        "glow": (220, 240, 255),     # 霜光
        "border": (150, 200, 240),   # 冰边
    },
    
    # 【宇宙异象系列】
    "providence_void": {
        "name": "虚空审判",
        "armor": (40, 20, 60),       # 虚空紫
        "crystal": (100, 50, 150),   # 暗晶紫
        "core": (150, 80, 200),      # 虚空核
        "flame": (80, 40, 120),      # 虚焰
        "glow": (120, 80, 180),      # 虚光
        "border": (80, 50, 120),     # 虚边
    },
    
    "providence_nature": {
        "name": "丛林神殿",
        "armor": (80, 140, 60),      # 丛林绿
        "crystal": (120, 200, 80),   # 翠晶绿
        "core": (180, 255, 100),     # 生命绿
        "flame": (100, 180, 60),     # 绿焰
        "glow": (150, 220, 100),     # 自然光
        "border": (100, 160, 80),    # 藤边
    },
    
    "providence_storm": {
        "name": "雷霆圣裁",
        "armor": (100, 100, 150),    # 雷云灰
        "crystal": (180, 180, 255),  # 电光紫
        "core": (255, 255, 150),     # 雷核黄
        "flame": (200, 200, 255),    # 电焰
        "glow": (220, 220, 255),     # 雷光
        "border": (150, 150, 200),   # 雷边
    },
    
    # 【神圣变体系列】
    "providence_blood": {
        "name": "血月祭司",
        "armor": (150, 30, 50),      # 血红
        "crystal": (200, 60, 80),    # 血晶
        "core": (255, 100, 120),     # 血核
        "flame": (180, 40, 60),      # 血焰
        "glow": (220, 80, 100),      # 血光
        "border": (180, 50, 70),     # 血边
    },
    
    "providence_gold": {
        "name": "皇金审判",
        "armor": (255, 200, 50),     # 皇金
        "crystal": (255, 230, 150),  # 金晶
        "core": (255, 255, 200),     # 金核
        "flame": (255, 220, 100),    # 金焰
        "glow": (255, 240, 180),     # 金光
        "border": (255, 210, 80),    # 金边
    },
    
    "providence_aurora": {
        "name": "极光圣典",
        "armor": (100, 200, 180),    # 极光青
        "crystal": (150, 255, 200),  # 极光绿
        "core": (200, 255, 230),     # 极光核
        "flame": (100, 220, 180),    # 极光焰
        "glow": (180, 255, 220),     # 极光
        "border": (120, 220, 200),   # 极光边
    },
}


def get_providence_theme(style):
    """获取普罗维登斯涂装主题"""
    if style in PROVIDENCE_THEMES:
        return PROVIDENCE_THEMES[style]
    return PROVIDENCE_THEMES["providence_default"]


def get_providence_skin_list():
    """获取所有涂装列表"""
    return list(PROVIDENCE_THEMES.keys())


def get_providence_skin_info(style):
    """获取涂装详细信息"""
    theme = get_providence_theme(style)
    return {
        "id": style,
        "name": theme["name"],
        "colors": {
            "armor": theme["armor"],
            "crystal": theme["crystal"],
            "core": theme["core"]
        }
    }


PROVIDENCE_STYLES = list(PROVIDENCE_THEMES.keys())


def is_providence_style(style):
    """检查是否为普罗维登斯涂装"""
    return style in PROVIDENCE_STYLES


# ==================== 涂装绘制调度 ====================
def draw_providence(surface, color, x, y, w, h, frame, style="providence_default"):
    """绘制普罗维登斯机体 - 根据涂装调用专属绘制"""
    drawers = {
        "providence_default": draw_default_providence,
        "providence_night": draw_night_providence,
        "providence_abyss": draw_abyss_providence,
        "providence_crystal": draw_crystal_providence,
        "providence_magma": draw_magma_providence,
        "providence_frost": draw_frost_providence,
        "providence_void": draw_void_providence,
        "providence_nature": draw_nature_providence,
        "providence_storm": draw_storm_providence,
        "providence_blood": draw_blood_providence,
        "providence_gold": draw_gold_providence,
        "providence_aurora": draw_aurora_providence,
    }
    drawer = drawers.get(style, draw_default_providence)
    drawer(surface, x, y, w, h, frame, style)


def render_providence_skin(surface, color, x, y, w, h, frame, style):
    """渲染普罗维登斯涂装"""
    draw_providence(surface, color, x, y, w, h, frame, style)


# ==================== 默认涂装：亵渎天神 ====================
def draw_default_providence(surface, x, y, w, h, frame, style):
    """
    默认亵渎天神 - 圣甲虫神殿堡垒形态
    特色：金字塔神殿主体 + 六片圣火羽翼 + 亵渎之眼核心 + 4个祭坛浮游炮
    """
    theme = get_providence_theme(style)
    
    armor = theme["armor"]        # 圣金
    crystal = theme["crystal"]    # 水晶粉
    core_color = theme["core"]    # 岩浆橙
    flame = theme["flame"]        # 亵渎蓝焰
    glow = theme["glow"]          # 神圣光晕
    border = theme["border"]      # 金边
    
    # 颜色变体
    armor_light = tuple(min(255, c + 60) for c in armor)
    armor_dark = tuple(max(0, c - 50) for c in armor)
    armor_shadow = tuple(max(0, c - 80) for c in armor)
    crystal_light = tuple(min(255, c + 50) for c in crystal)
    crystal_dark = tuple(max(0, c - 30) for c in crystal)
    flame_bright = tuple(min(255, c + 80) for c in flame)
    
    t = frame * 0.05
    cx, cy = x + w // 2, y + h // 2
    
    # ========== 【第一层】神圣几何光阵背景 ==========
    # 六芒星光阵
    hex_radius = 48 + 5 * math.sin(t * 1.2)
    hex_alpha = int(25 + 10 * math.sin(t * 2))
    for ring in range(3):
        ring_r = hex_radius - ring * 12
        if ring_r > 0:
            hex_pts = []
            for i in range(6):
                angle = math.radians(i * 60 + 30 + t * 5)
                hx = cx + math.cos(angle) * ring_r
                hy = cy + math.sin(angle) * ring_r
                hex_pts.append((int(hx), int(hy)))
            pygame.draw.polygon(surface, (*glow, max(5, hex_alpha - ring * 8)), hex_pts, 1)
    
    # 神圣光晕（多层渐变）
    for i in range(6):
        r = int(52 - i * 7 + 4 * math.sin(t * 1.5 + i * 0.5))
        alpha = max(0, 30 - i * 5)
        if r > 0:
            glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*glow, alpha), (r + 2, r + 2), r)
            surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # ========== 【第二层】六片圣火羽翼 ==========
    wing_hover = 3 * math.sin(t * 2.5)
    
    for wing_idx in range(6):
        # 每片翼的角度：上方两片、中间两片、下方两片
        if wing_idx < 2:
            base_angle = -60 + wing_idx * 120  # -60°, 60°
            wing_len = 38
            wing_offset_y = -12
        elif wing_idx < 4:
            base_angle = -45 + (wing_idx - 2) * 90  # -45°, 45°
            wing_len = 32
            wing_offset_y = 5
        else:
            base_angle = -30 + (wing_idx - 4) * 60  # -30°, 30°
            wing_len = 26
            wing_offset_y = 18
        
        side = 1 if wing_idx % 2 == 1 else -1
        wing_angle = math.radians(base_angle)
        
        # 羽翼根部位置
        root_x = cx + side * 18
        root_y = cy + wing_offset_y + wing_hover
        
        # 羽翼尖端位置（随动画摆动）
        swing = 8 * math.sin(t * 3 + wing_idx * 0.8)
        tip_x = root_x + side * wing_len + swing * side
        tip_y = root_y + math.sin(wing_angle) * wing_len * 0.5
        
        # 羽翼形状 - 火焰羽毛
        feather_pts = []
        segments = 10
        for seg in range(segments + 1):
            progress = seg / segments
            # 羽毛轮廓：中间宽两端窄
            width = 12 * math.sin(progress * math.pi) * (1 - progress * 0.3)
            width = max(2, width)
            
            px = root_x + (tip_x - root_x) * progress
            py = root_y + (tip_y - root_y) * progress
            
            # 上边缘
            feather_pts.append((int(px), int(py - width)))
        
        for seg in range(segments, -1, -1):
            progress = seg / segments
            width = 12 * math.sin(progress * math.pi) * (1 - progress * 0.3)
            width = max(2, width)
            
            px = root_x + (tip_x - root_x) * progress
            py = root_y + (tip_y - root_y) * progress
            
            # 下边缘
            feather_pts.append((int(px), int(py + width)))
        
        if len(feather_pts) >= 3:
            # 羽翼主体 - 渐变色
            pygame.draw.polygon(surface, (*crystal, 160), feather_pts)
            # 羽翼边缘发光
            pygame.draw.polygon(surface, crystal_light, feather_pts, 2)
            
            # 羽翼内部火焰纹理
            for fline in range(3):
                fl_progress = 0.2 + fline * 0.25
                fl_x = root_x + (tip_x - root_x) * fl_progress
                fl_y = root_y + (tip_y - root_y) * fl_progress
                fl_len = 8 - fline * 2
                pygame.draw.line(surface, (*flame, 150),
                    (int(fl_x), int(fl_y)),
                    (int(fl_x + side * fl_len), int(fl_y - 3)), 1)
        
        # 羽翼尖端火焰
        flame_size = 4 + int(2 * math.sin(t * 5 + wing_idx))
        pygame.draw.circle(surface, (*flame, 200), (int(tip_x), int(tip_y)), flame_size)
        pygame.draw.circle(surface, (*flame_bright, 150), (int(tip_x), int(tip_y)), max(2, flame_size - 2))
    
    # ========== 【第三层】4个祭坛浮游炮 ==========
    drone_orbit = 35 + 5 * math.sin(t * 1.5)
    
    for drone_idx in range(4):
        drone_angle = t * 1.2 + drone_idx * (math.pi / 2)  # 均匀分布，缓慢旋转
        
        dx = cx + math.cos(drone_angle) * drone_orbit
        dy = cy + math.sin(drone_angle) * drone_orbit * 0.7
        
        # 祭坛基座 - 小金字塔形
        altar_size = 8
        altar_pts = [
            (int(dx), int(dy - altar_size)),           # 顶点
            (int(dx + altar_size), int(dy + altar_size * 0.6)),  # 右下
            (int(dx - altar_size), int(dy + altar_size * 0.6)),  # 左下
        ]
        pygame.draw.polygon(surface, armor, altar_pts)
        pygame.draw.polygon(surface, armor_light, altar_pts, 1)
        
        # 祭坛装饰线
        pygame.draw.line(surface, armor_dark,
            (int(dx), int(dy - altar_size + 2)),
            (int(dx), int(dy + altar_size * 0.4)), 1)
        
        # 祭坛顶部圣火
        fire_size = 3 + int(2 * math.sin(t * 6 + drone_idx * 1.5))
        pygame.draw.circle(surface, flame, (int(dx), int(dy - altar_size - 3)), fire_size)
        pygame.draw.circle(surface, flame_bright, (int(dx), int(dy - altar_size - 3)), max(1, fire_size - 2))
        
        # 祭坛与主体的连接光线
        pygame.draw.line(surface, (*glow, 60),
            (int(dx), int(dy)), (cx, cy), 1)
    
    # ========== 【第四层】神殿主体（金字塔堡垒） ==========
    # 外层装甲 - 埃及神殿形状
    body_pts = [
        (cx, y + 3),              # 金字塔顶
        (cx + 8, y + 8),          # 右上斜面
        (cx + 20, y + 18),        # 右肩
        (cx + 24, cy - 5),        # 右上腰
        (cx + 22, cy + 8),        # 右下腰
        (cx + 18, cy + 18),       # 右臀
        (cx + 10, y + h - 6),     # 右底
        (cx, y + h - 2),          # 底尖
        (cx - 10, y + h - 6),     # 左底
        (cx - 18, cy + 18),       # 左臀
        (cx - 22, cy + 8),        # 左下腰
        (cx - 24, cy - 5),        # 左上腰
        (cx - 20, y + 18),        # 左肩
        (cx - 8, y + 8),          # 左上斜面
    ]
    pygame.draw.polygon(surface, armor, body_pts)
    pygame.draw.polygon(surface, border, body_pts, 2)
    
    # 神殿内层（高光面）
    inner_pts = [
        (cx, y + 10),
        (cx + 14, y + 22),
        (cx + 16, cy - 3),
        (cx + 14, cy + 10),
        (cx + 8, y + h - 14),
        (cx, y + h - 10),
        (cx - 8, y + h - 14),
        (cx - 14, cy + 10),
        (cx - 16, cy - 3),
        (cx - 14, y + 22),
    ]
    pygame.draw.polygon(surface, armor_light, inner_pts)
    pygame.draw.polygon(surface, (*armor_dark, 150), inner_pts, 1)
    
    # 神殿纹饰 - 水平分隔线和圣甲虫图腾
    for i in range(5):
        ly = y + 16 + i * 12
        lw = 14 - i * 1.5
        lw = max(4, int(lw))
        pygame.draw.line(surface, armor_shadow, (cx - lw, ly), (cx + lw, ly), 1)
        # 小装饰点
        if i < 4:
            pygame.draw.circle(surface, crystal, (cx - lw - 2, ly), 1)
            pygame.draw.circle(surface, crystal, (cx + lw + 2, ly), 1)
    
    # 侧面装甲板
    for side in [-1, 1]:
        plate_pts = [
            (cx + side * 20, y + 20),
            (cx + side * 26, cy - 8),
            (cx + side * 24, cy + 5),
            (cx + side * 18, cy + 12),
        ]
        pygame.draw.polygon(surface, armor_dark, plate_pts)
        pygame.draw.polygon(surface, (*armor_shadow, 150), plate_pts, 1)
    
    # ========== 【第五层】亵渎之眼（核心） ==========
    eye_y = cy - 5
    eye_pulse = 1 + 0.3 * math.sin(t * 3)
    
    # 眼眶 - 菱形
    eye_w = int(14 * eye_pulse)
    eye_h = int(10 * eye_pulse)
    eye_pts = [
        (cx, eye_y - eye_h),      # 上
        (cx + eye_w, eye_y),      # 右
        (cx, eye_y + eye_h),      # 下
        (cx - eye_w, eye_y),      # 左
    ]
    pygame.draw.polygon(surface, (*flame, 100), eye_pts)
    pygame.draw.polygon(surface, flame_bright, eye_pts, 2)
    
    # 核心火焰光晕
    for ring in range(4):
        ring_r = int(12 - ring * 2.5 + 2 * math.sin(t * 4 + ring))
        ring_alpha = max(0, 120 - ring * 25)
        if ring_r > 0:
            pygame.draw.circle(surface, (*core_color, ring_alpha), (cx, eye_y), ring_r)
    
    # 核心内焰
    inner_r = int(5 + 2 * math.sin(t * 5))
    pygame.draw.circle(surface, core_color, (cx, eye_y), inner_r)
    pygame.draw.circle(surface, armor_light, (cx, eye_y), max(2, inner_r - 3))
    
    # 瞳孔（会动的眼球效果）
    pupil_offset_x = int(2 * math.sin(t * 1.5))
    pupil_offset_y = int(1 * math.cos(t * 2))
    pygame.draw.circle(surface, armor_shadow, (cx + pupil_offset_x, eye_y + pupil_offset_y), 3)
    pygame.draw.circle(surface, (255, 255, 255), (cx + pupil_offset_x - 1, eye_y + pupil_offset_y - 1), 1)
    
    # 核心周围火焰粒子
    for i in range(8):
        p_angle = t * 3.5 + i * (math.pi / 4)
        p_dist = 15 + 5 * math.sin(t * 4 + i * 0.7)
        px = cx + math.cos(p_angle) * p_dist
        py = eye_y + math.sin(p_angle) * p_dist * 0.6
        p_size = 2 + int(1.5 * math.sin(t * 6 + i))
        pygame.draw.circle(surface, (*flame, 180), (int(px), int(py)), p_size)
    
    # ========== 【第六层】圣甲虫头冠 ==========
    head_y = y + 5
    
    # 头冠基座
    crown_base = [
        (cx - 12, head_y + 10),
        (cx - 6, head_y + 4),
        (cx, head_y - 2),
        (cx + 6, head_y + 4),
        (cx + 12, head_y + 10),
    ]
    pygame.draw.polygon(surface, armor, crown_base)
    pygame.draw.polygon(surface, armor_light, crown_base, 1)
    
    # 中央高塔
    pygame.draw.polygon(surface, armor_light, [
        (cx - 4, head_y + 5),
        (cx, head_y - 5),
        (cx + 4, head_y + 5),
    ])
    
    # 侧面装饰角
    for side in [-1, 1]:
        horn_pts = [
            (cx + side * 10, head_y + 8),
            (cx + side * 14, head_y + 2),
            (cx + side * 12, head_y + 10),
        ]
        pygame.draw.polygon(surface, armor_dark, horn_pts)
    
    # 头冠宝石
    gem_pulse = 3 + int(1.5 * math.sin(t * 4.5))
    pygame.draw.circle(surface, crystal, (cx, head_y + 2), gem_pulse + 2)
    pygame.draw.circle(surface, crystal_light, (cx, head_y + 2), gem_pulse)
    # 宝石高光
    pygame.draw.circle(surface, (255, 255, 255), (cx - 1, head_y), 1)
    
    # ========== 【第七层】推进系统 ==========
    thrust_pulse = 12 + int(6 * math.sin(t * 5))
    
    # 主推进火焰（三角形渐变）
    for layer in range(3):
        layer_len = thrust_pulse - layer * 3
        layer_width = 8 - layer * 2
        layer_alpha = 255 - layer * 50
        thrust_pts = [
            (cx - layer_width, y + h - 4),
            (cx, y + h + layer_len),
            (cx + layer_width, y + h - 4),
        ]
        if layer == 0:
            pygame.draw.polygon(surface, glow, thrust_pts)
        elif layer == 1:
            pygame.draw.polygon(surface, core_color, thrust_pts)
        else:
            pygame.draw.polygon(surface, armor_light, thrust_pts)
    
    # 侧推进器
    for side in [-1, 1]:
        sx = cx + side * 14
        side_thrust = thrust_pulse * 0.6
        pygame.draw.polygon(surface, (*glow, 180), [
            (sx - 3, y + h - 8),
            (sx, y + h + int(side_thrust)),
            (sx + 3, y + h - 8),
        ])
        pygame.draw.polygon(surface, (*core_color, 150), [
            (sx - 1, y + h - 8),
            (sx, y + h + int(side_thrust) - 4),
            (sx + 1, y + h - 8),
        ])
    
    # 推进器喷口装饰
    pygame.draw.ellipse(surface, armor_dark, (cx - 10, y + h - 6, 20, 5))
    pygame.draw.ellipse(surface, armor_shadow, (cx - 8, y + h - 5, 16, 3))


# ==================== 夜殿守护涂装 ====================
def draw_night_providence(surface, x, y, w, h, frame, style):
    """
    夜殿守护 - 月神殿形态
    特色：新月塔主体 + 星云羽翼 + 满月核心 + 4个星尘浮游炮
    """
    theme = get_providence_theme(style)
    armor = theme["armor"]        # 暗紫
    crystal = theme["crystal"]    # 月光紫
    core = theme["core"]          # 星辉紫
    flame = theme["flame"]        # 暗焰
    glow = theme["glow"]          # 月光晕
    border = theme["border"]
    
    armor_light = tuple(min(255, c + 50) for c in armor)
    armor_dark = tuple(max(0, c - 40) for c in armor)
    armor_shadow = tuple(max(0, c - 70) for c in armor)
    crystal_light = tuple(min(255, c + 60) for c in crystal)
    crystal_dark = tuple(max(0, c - 30) for c in crystal)
    star_white = (240, 240, 255)
    
    t = frame * 0.05
    cx, cy = x + w // 2, y + h // 2
    
    # ========== 【第一层】星空背景 ==========
    # 散落的小星星
    for i in range(12):
        star_seed = (i * 127 + 53) % 360
        star_angle = math.radians(star_seed) + t * 0.3
        star_dist = 35 + (i % 5) * 8
        sx = cx + math.cos(star_angle) * star_dist
        sy = cy + math.sin(star_angle) * star_dist * 0.8
        star_size = 1 + int((math.sin(t * 3 + i * 0.7) + 1) * 0.8)
        star_alpha = int(80 + 50 * math.sin(t * 4 + i))
        pygame.draw.circle(surface, (*star_white, star_alpha), (int(sx), int(sy)), star_size)
    
    # 月光光晕（柔和的紫色）
    for ring in range(5):
        r = int(50 - ring * 8 + 4 * math.sin(t * 1.5 + ring * 0.5))
        alpha = max(0, 30 - ring * 5)
        if r > 0:
            glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*glow, alpha), (r + 2, r + 2), r)
            surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # ========== 【第二层】六片星云羽翼 ==========
    wing_float = 4 * math.sin(t * 2)
    
    for wing_idx in range(6):
        # 翅膀分布：上2、中2、下2
        if wing_idx < 2:
            angle_base = -55 + wing_idx * 110
            wing_length = 42
            wing_y_offset = -10
        elif wing_idx < 4:
            angle_base = -40 + (wing_idx - 2) * 80
            wing_length = 36
            wing_y_offset = 8
        else:
            angle_base = -25 + (wing_idx - 4) * 50
            wing_length = 28
            wing_y_offset = 22
        
        side = 1 if wing_idx % 2 == 1 else -1
        swing = 6 * math.sin(t * 2.5 + wing_idx * 0.6) * side
        
        # 翼根和翼尖
        root_x = cx + side * 16
        root_y = cy + wing_y_offset + wing_float
        tip_x = root_x + side * wing_length + swing
        tip_y = root_y - 8 + wing_idx * 3
        
        # 星云翼形状 - 飘逸的弧线
        nebula_pts = []
        segments = 12
        for seg in range(segments + 1):
            prog = seg / segments
            # 宽度：中间宽两端窄，带波浪
            wave = 2 * math.sin(prog * math.pi * 3 + t * 3)
            width = 10 * math.sin(prog * math.pi) + wave
            width = max(2, width)
            
            px = root_x + (tip_x - root_x) * prog
            py = root_y + (tip_y - root_y) * prog
            nebula_pts.append((int(px), int(py - width)))
        
        for seg in range(segments, -1, -1):
            prog = seg / segments
            wave = 2 * math.sin(prog * math.pi * 3 + t * 3)
            width = 10 * math.sin(prog * math.pi) + wave
            width = max(2, width)
            
            px = root_x + (tip_x - root_x) * prog
            py = root_y + (tip_y - root_y) * prog
            nebula_pts.append((int(px), int(py + width)))
        
        if len(nebula_pts) >= 3:
            # 星云主体 - 半透明紫色
            pygame.draw.polygon(surface, (*crystal, 140), nebula_pts)
            # 星云边缘 - 发光
            pygame.draw.polygon(surface, (*crystal_light, 180), nebula_pts, 1)
            
            # 星云内的小星星
            for star in range(3):
                s_prog = 0.25 + star * 0.25
                s_x = root_x + (tip_x - root_x) * s_prog
                s_y = root_y + (tip_y - root_y) * s_prog
                s_size = 2 if star == 1 else 1
                s_alpha = int(150 + 50 * math.sin(t * 5 + wing_idx + star))
                pygame.draw.circle(surface, (*star_white, s_alpha), (int(s_x), int(s_y)), s_size)
        
        # 翼尖星光
        tip_glow = 3 + int(2 * math.sin(t * 4 + wing_idx))
        pygame.draw.circle(surface, (*core, 180), (int(tip_x), int(tip_y)), tip_glow)
        pygame.draw.circle(surface, star_white, (int(tip_x), int(tip_y)), max(1, tip_glow - 2))
    
    # ========== 【第三层】4个星尘浮游炮 ==========
    drone_orbit = 38 + 4 * math.sin(t * 1.8)
    
    for drone_idx in range(4):
        # 椭圆轨道，相位错开
        drone_angle = t * 1.5 + drone_idx * (math.pi / 2)
        dx = cx + math.cos(drone_angle) * drone_orbit
        dy = cy + math.sin(drone_angle) * drone_orbit * 0.65
        
        # 星尘核心 - 小月亮形状
        moon_size = 7
        # 画新月：外圆减内圆
        pygame.draw.circle(surface, crystal, (int(dx), int(dy)), moon_size)
        # 内部阴影形成月牙
        shadow_offset = 3
        pygame.draw.circle(surface, armor_shadow, (int(dx + shadow_offset), int(dy - 1)), moon_size - 2)
        
        # 月亮周围的星尘粒子
        for particle in range(5):
            p_angle = t * 4 + drone_idx * 2 + particle * 1.26
            p_dist = 10 + 3 * math.sin(t * 5 + particle)
            px = dx + math.cos(p_angle) * p_dist
            py = dy + math.sin(p_angle) * p_dist * 0.7
            p_size = 1 if particle % 2 == 0 else 2
            pygame.draw.circle(surface, (*glow, 150), (int(px), int(py)), p_size)
        
        # 与主体的连接 - 星光线
        pygame.draw.line(surface, (*crystal_light, 50), (int(dx), int(dy)), (cx, cy), 1)
    
    # ========== 【第四层】月神殿主体 ==========
    # 外形：新月塔形状，优雅的曲线
    body_pts = [
        (cx, y + 2),               # 塔尖
        (cx + 6, y + 8),           # 右上收
        (cx + 18, y + 20),         # 右肩展开
        (cx + 22, cy - 8),         # 右上腰
        (cx + 24, cy + 5),         # 右腰最宽
        (cx + 20, cy + 18),        # 右下收
        (cx + 12, y + h - 8),      # 右底
        (cx, y + h - 2),           # 底尖
        (cx - 12, y + h - 8),      # 左底
        (cx - 20, cy + 18),        # 左下收
        (cx - 24, cy + 5),         # 左腰最宽
        (cx - 22, cy - 8),         # 左上腰
        (cx - 18, y + 20),         # 左肩
        (cx - 6, y + 8),           # 左上收
    ]
    pygame.draw.polygon(surface, armor, body_pts)
    pygame.draw.polygon(surface, armor_light, body_pts, 2)
    
    # 内层高光
    inner_pts = [
        (cx, y + 10),
        (cx + 12, y + 24),
        (cx + 16, cy - 5),
        (cx + 14, cy + 12),
        (cx + 8, y + h - 16),
        (cx, y + h - 10),
        (cx - 8, y + h - 16),
        (cx - 14, cy + 12),
        (cx - 16, cy - 5),
        (cx - 12, y + 24),
    ]
    pygame.draw.polygon(surface, armor_light, inner_pts)
    
    # 月相装饰纹路
    for i in range(4):
        ly = y + 20 + i * 14
        # 新月弧线
        arc_w = 12 - i * 2
        arc_h = 6
        pygame.draw.arc(surface, armor_dark, 
            (cx - arc_w, ly - arc_h // 2, arc_w * 2, arc_h),
            0, math.pi, 1)
    
    # 侧面月纹装甲
    for side in [-1, 1]:
        plate_pts = [
            (cx + side * 18, y + 22),
            (cx + side * 25, cy - 5),
            (cx + side * 23, cy + 8),
            (cx + side * 16, cy + 15),
        ]
        pygame.draw.polygon(surface, armor_dark, plate_pts)
        # 月牙装饰
        moon_x = cx + side * 21
        moon_y = cy
        pygame.draw.arc(surface, crystal_dark, 
            (int(moon_x) - 5, int(moon_y) - 5, 10, 10),
            math.pi * 0.3 if side > 0 else math.pi * 1.2,
            math.pi * 1.2 if side > 0 else math.pi * 2.1, 2)
    
    # ========== 【第五层】满月核心 ==========
    moon_y = cy - 3
    moon_pulse = 1 + 0.15 * math.sin(t * 2.5)
    moon_radius = int(12 * moon_pulse)
    
    # 满月外圈光晕
    for halo in range(4):
        halo_r = moon_radius + 6 - halo * 2
        halo_alpha = max(0, 60 - halo * 12)
        pygame.draw.circle(surface, (*core, halo_alpha), (cx, moon_y), halo_r)
    
    # 满月本体
    pygame.draw.circle(surface, crystal, (cx, moon_y), moon_radius)
    
    # 月球表面陨石坑
    crater_positions = [(2, -2, 3), (-3, 1, 2), (1, 3, 2)]
    for cr_x, cr_y, cr_r in crater_positions:
        pygame.draw.circle(surface, crystal_dark, 
            (cx + cr_x, moon_y + cr_y), cr_r)
    
    # 月球高光
    pygame.draw.circle(surface, crystal_light, (cx - 3, moon_y - 3), 4)
    pygame.draw.circle(surface, star_white, (cx - 4, moon_y - 4), 2)
    
    # 月球周围星光粒子
    for i in range(10):
        p_angle = t * 2.8 + i * 0.628
        p_dist = moon_radius + 8 + 4 * math.sin(t * 3.5 + i)
        px = cx + math.cos(p_angle) * p_dist
        py = moon_y + math.sin(p_angle) * p_dist * 0.8
        p_size = 1 + int(math.sin(t * 5 + i) > 0.5)
        pygame.draw.circle(surface, (*glow, 160), (int(px), int(py)), p_size)
    
    # ========== 【第六层】星冠头饰 ==========
    head_y = y + 5
    
    # 星冠基座
    crown_pts = [
        (cx - 14, head_y + 12),
        (cx - 10, head_y + 4),
        (cx - 5, head_y + 8),
        (cx, head_y - 4),
        (cx + 5, head_y + 8),
        (cx + 10, head_y + 4),
        (cx + 14, head_y + 12),
    ]
    pygame.draw.polygon(surface, armor, crown_pts)
    pygame.draw.polygon(surface, armor_light, crown_pts, 1)
    
    # 中央星尖
    pygame.draw.polygon(surface, crystal, [
        (cx - 3, head_y + 6),
        (cx, head_y - 6),
        (cx + 3, head_y + 6),
    ])
    
    # 侧面星角
    for side in [-1, 1]:
        pygame.draw.polygon(surface, armor_light, [
            (cx + side * 8, head_y + 6),
            (cx + side * 12, head_y - 1),
            (cx + side * 10, head_y + 10),
        ])
    
    # 星冠宝石
    gem_size = 3 + int(1.5 * math.sin(t * 4))
    pygame.draw.circle(surface, core, (cx, head_y + 3), gem_size + 2)
    pygame.draw.circle(surface, crystal_light, (cx, head_y + 3), gem_size)
    pygame.draw.circle(surface, star_white, (cx - 1, head_y + 1), 1)
    
    # ========== 【第七层】星光推进 ==========
    thrust_len = 14 + int(7 * math.sin(t * 4.5))
    
    # 主推进 - 紫色星光
    for layer in range(3):
        l_len = thrust_len - layer * 4
        l_width = 7 - layer * 2
        thrust_pts = [
            (cx - l_width, y + h - 5),
            (cx, y + h + l_len),
            (cx + l_width, y + h - 5),
        ]
        if layer == 0:
            pygame.draw.polygon(surface, glow, thrust_pts)
        elif layer == 1:
            pygame.draw.polygon(surface, core, thrust_pts)
        else:
            pygame.draw.polygon(surface, crystal_light, thrust_pts)
    
    # 尾焰星光粒子
    for i in range(5):
        p_y = y + h + 3 + i * 3
        p_x = cx + int(3 * math.sin(t * 6 + i * 1.5))
        p_alpha = int(180 - i * 30)
        pygame.draw.circle(surface, (*glow, p_alpha), (p_x, p_y), 2 - i // 3)
    
    # 侧推进
    for side in [-1, 1]:
        sx = cx + side * 14
        s_len = int(thrust_len * 0.5)
        pygame.draw.polygon(surface, (*glow, 160), [
            (sx - 2, y + h - 8),
            (sx, y + h + s_len),
            (sx + 2, y + h - 8),
        ])
    
    # 推进器喷口
    pygame.draw.ellipse(surface, armor_dark, (cx - 9, y + h - 7, 18, 5))
    pygame.draw.ellipse(surface, armor_shadow, (cx - 6, y + h - 6, 12, 3))


# ==================== 深渊圣殿涂装 ====================
def draw_abyss_providence(surface, x, y, w, h, frame, style):
    """
    深渊圣殿 - 深海神殿形态
    特色：珊瑚礁神殿主体 + 波浪鳍翼 + 漩涡核心 + 4个气泡浮游炮
    """
    theme = get_providence_theme(style)
    armor = theme["armor"]        # 深海蓝
    crystal = theme["crystal"]    # 海晶蓝
    core = theme["core"]          # 深渊青
    flame = theme["flame"]        # 深焰
    glow = theme["glow"]          # 深海光
    border = theme["border"]
    
    armor_light = tuple(min(255, c + 55) for c in armor)
    armor_dark = tuple(max(0, c - 35) for c in armor)
    armor_shadow = tuple(max(0, c - 60) for c in armor)
    crystal_light = tuple(min(255, c + 65) for c in crystal)
    crystal_dark = tuple(max(0, c - 25) for c in crystal)
    water_white = (200, 230, 255)
    
    t = frame * 0.05
    cx, cy = x + w // 2, y + h // 2
    
    # ========== 【第一层】深海水纹背景 ==========
    # 同心圆波纹
    for ring in range(5):
        ring_r = 45 - ring * 8 + 6 * math.sin(t * 1.8 + ring * 0.8)
        ring_alpha = max(0, 25 - ring * 4)
        if ring_r > 5:
            pygame.draw.circle(surface, (*glow, ring_alpha), (cx, cy), int(ring_r), 1)
    
    # 深海光晕
    for i in range(6):
        r = int(48 - i * 7 + 3 * math.sin(t * 1.3 + i * 0.4))
        alpha = max(0, 28 - i * 4)
        if r > 0:
            glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*glow, alpha), (r + 2, r + 2), r)
            surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # ========== 【第二层】六片波浪鳍翼 ==========
    wave_flow = 5 * math.sin(t * 2.2)
    
    for wing_idx in range(6):
        # 翼的分布：上2、中2、下2
        if wing_idx < 2:
            angle_base = -65 + wing_idx * 130
            wing_length = 40
            wing_y_offset = -8
        elif wing_idx < 4:
            angle_base = -45 + (wing_idx - 2) * 90
            wing_length = 34
            wing_y_offset = 10
        else:
            angle_base = -28 + (wing_idx - 4) * 56
            wing_length = 26
            wing_y_offset = 24
        
        side = 1 if wing_idx % 2 == 1 else -1
        
        # 水流摆动
        flow = 7 * math.sin(t * 2.5 + wing_idx * 0.7) * side
        
        root_x = cx + side * 15
        root_y = cy + wing_y_offset + wave_flow
        tip_x = root_x + side * wing_length + flow
        tip_y = root_y - 5 + wing_idx * 2
        
        # 波浪形鳍翼 - 水滴+波浪边缘
        fin_pts = []
        segments = 14
        for seg in range(segments + 1):
            prog = seg / segments
            # 宽度随进度变化，带波浪
            wave_detail = 1.5 * math.sin(prog * math.pi * 4 + t * 4)
            width = 11 * math.sin(prog * math.pi) * (1 - prog * 0.2) + wave_detail
            width = max(2, width)
            
            px = root_x + (tip_x - root_x) * prog
            py = root_y + (tip_y - root_y) * prog
            fin_pts.append((int(px), int(py - width)))
        
        for seg in range(segments, -1, -1):
            prog = seg / segments
            wave_detail = 1.5 * math.sin(prog * math.pi * 4 + t * 4)
            width = 11 * math.sin(prog * math.pi) * (1 - prog * 0.2) + wave_detail
            width = max(2, width)
            
            px = root_x + (tip_x - root_x) * prog
            py = root_y + (tip_y - root_y) * prog
            fin_pts.append((int(px), int(py + width)))
        
        if len(fin_pts) >= 3:
            # 鳍翼主体 - 半透明海蓝
            pygame.draw.polygon(surface, (*crystal, 150), fin_pts)
            # 鳍翼边缘 - 发光
            pygame.draw.polygon(surface, (*crystal_light, 190), fin_pts, 1)
            
            # 鳍翼内的水波纹理
            for wave_line in range(3):
                w_prog = 0.3 + wave_line * 0.2
                w_x = root_x + (tip_x - root_x) * w_prog
                w_y = root_y + (tip_y - root_y) * w_prog
                w_offset = 3 * math.sin(t * 3 + wave_line)
                pygame.draw.line(surface, (*glow, 120),
                    (int(w_x - 5), int(w_y + w_offset)),
                    (int(w_x + 5), int(w_y - w_offset)), 1)
        
        # 鳍尖水珠
        drop_size = 3 + int(2 * math.sin(t * 5 + wing_idx))
        pygame.draw.circle(surface, (*water_white, 200), (int(tip_x), int(tip_y)), drop_size)
        pygame.draw.circle(surface, crystal_light, (int(tip_x), int(tip_y)), max(1, drop_size - 2))
    
    # ========== 【第三层】4个气泡浮游炮 ==========
    bubble_orbit = 36 + 5 * math.sin(t * 1.6)
    
    for bubble_idx in range(4):
        # 上下浮动的椭圆轨道
        bubble_angle = t * 1.4 + bubble_idx * (math.pi / 2)
        bubble_bob = 3 * math.sin(t * 2.5 + bubble_idx * 1.2)
        
        bx = cx + math.cos(bubble_angle) * bubble_orbit
        by = cy + math.sin(bubble_angle) * bubble_orbit * 0.7 + bubble_bob
        
        # 大气泡外壳
        bubble_size = 9 + int(2 * math.sin(t * 3 + bubble_idx))
        
        # 气泡外圈 - 半透明
        pygame.draw.circle(surface, (*crystal, 120), (int(bx), int(by)), bubble_size)
        # 气泡高光边缘
        pygame.draw.circle(surface, crystal_light, (int(bx), int(by)), bubble_size, 2)
        
        # 气泡内的小气泡核
        inner_size = bubble_size - 4
        pygame.draw.circle(surface, (*glow, 160), (int(bx), int(by)), inner_size)
        
        # 气泡高光点
        highlight_x = bx - bubble_size * 0.3
        highlight_y = by - bubble_size * 0.4
        pygame.draw.circle(surface, water_white, (int(highlight_x), int(highlight_y)), 3)
        pygame.draw.circle(surface, (255, 255, 255), (int(highlight_x - 1), int(highlight_y - 1)), 1)
        
        # 小气泡环绕
        for mini in range(3):
            mini_angle = t * 4 + bubble_idx * 2 + mini * 2.1
            mini_dist = bubble_size + 5
            mini_x = bx + math.cos(mini_angle) * mini_dist
            mini_y = by + math.sin(mini_angle) * mini_dist * 0.8
            mini_size = 2 + int(math.sin(t * 5 + mini) > 0)
            pygame.draw.circle(surface, (*crystal_light, 150), (int(mini_x), int(mini_y)), mini_size)
        
        # 连接线 - 水流
        pygame.draw.line(surface, (*glow, 40), (int(bx), int(by)), (cx, cy), 1)
    
    # ========== 【第四层】珊瑚礁神殿主体 ==========
    # 外形：深海神殿，带珊瑚装饰
    body_pts = [
        (cx, y + 2),               # 尖顶
        (cx + 7, y + 10),          # 右上收窄
        (cx + 19, y + 22),         # 右肩
        (cx + 23, cy - 6),         # 右上腰
        (cx + 25, cy + 6),         # 右腰最宽
        (cx + 21, cy + 20),        # 右下腰
        (cx + 14, y + h - 7),      # 右底
        (cx, y + h - 1),           # 底尖
        (cx - 14, y + h - 7),      # 左底
        (cx - 21, cy + 20),        # 左下腰
        (cx - 25, cy + 6),         # 左腰最宽
        (cx - 23, cy - 6),         # 左上腰
        (cx - 19, y + 22),         # 左肩
        (cx - 7, y + 10),          # 左上收窄
    ]
    pygame.draw.polygon(surface, armor, body_pts)
    pygame.draw.polygon(surface, armor_light, body_pts, 2)
    
    # 内层高光
    inner_pts = [
        (cx, y + 12),
        (cx + 13, y + 26),
        (cx + 17, cy - 3),
        (cx + 15, cy + 14),
        (cx + 10, y + h - 15),
        (cx, y + h - 9),
        (cx - 10, y + h - 15),
        (cx - 15, cy + 14),
        (cx - 17, cy - 3),
        (cx - 13, y + 26),
    ]
    pygame.draw.polygon(surface, armor_light, inner_pts)
    
    # 水波纹装饰
    for i in range(5):
        ly = y + 18 + i * 13
        arc_w = 13 - i * 1.5
        arc_w = max(4, int(arc_w))
        wave_offset = int(3 * math.sin(t * 2.5 + i))
        # 波浪弧线
        pygame.draw.arc(surface, armor_dark,
            (cx - arc_w + wave_offset, ly - 4, arc_w * 2, 8),
            0, math.pi, 1)
    
    # 侧面珊瑚装甲
    for side in [-1, 1]:
        plate_pts = [
            (cx + side * 19, y + 24),
            (cx + side * 26, cy - 4),
            (cx + side * 24, cy + 10),
            (cx + side * 17, cy + 18),
        ]
        pygame.draw.polygon(surface, armor_dark, plate_pts)
        
        # 珊瑚枝装饰
        coral_x = cx + side * 22
        coral_y = cy + 2
        for branch in range(3):
            branch_angle = math.radians(-30 + branch * 30) * side
            branch_len = 8 - branch * 2
            branch_ex = coral_x + math.cos(branch_angle) * branch_len * side
            branch_ey = coral_y - math.sin(branch_angle) * branch_len
            pygame.draw.line(surface, crystal_dark,
                (int(coral_x), int(coral_y)),
                (int(branch_ex), int(branch_ey)), 2)
            pygame.draw.circle(surface, glow, (int(branch_ex), int(branch_ey)), 2)
    
    # ========== 【第五层】漩涡核心 ==========
    vortex_y = cy - 4
    vortex_pulse = 1 + 0.25 * math.sin(t * 2.8)
    
    # 漩涡外圈
    for ring in range(5):
        ring_r = int((14 - ring * 2.5) * vortex_pulse)
        ring_alpha = max(0, 100 - ring * 18)
        if ring_r > 0:
            pygame.draw.circle(surface, (*core, ring_alpha), (cx, vortex_y), ring_r)
    
    # 漩涡主体
    vortex_r = int(8 * vortex_pulse)
    pygame.draw.circle(surface, crystal, (cx, vortex_y), vortex_r)
    
    # 漩涡旋转条纹
    for spiral in range(8):
        spiral_angle = t * 4 + spiral * (math.pi / 4)
        spiral_start_r = 3
        spiral_end_r = vortex_r + 2
        
        s_start_x = cx + math.cos(spiral_angle) * spiral_start_r
        s_start_y = vortex_y + math.sin(spiral_angle) * spiral_start_r
        s_end_x = cx + math.cos(spiral_angle) * spiral_end_r
        s_end_y = vortex_y + math.sin(spiral_angle) * spiral_end_r
        
        spiral_alpha = int(120 - (spiral % 2) * 40)
        pygame.draw.line(surface, (*core, spiral_alpha),
            (int(s_start_x), int(s_start_y)),
            (int(s_end_x), int(s_end_y)), 1)
    
    # 漩涡中心
    pygame.draw.circle(surface, armor_light, (cx, vortex_y), 4)
    pygame.draw.circle(surface, water_white, (cx, vortex_y), 2)
    
    # 漩涡周围水流粒子
    for i in range(10):
        p_angle = t * 3.5 + i * 0.628
        p_dist = vortex_r + 6 + 4 * math.sin(t * 4 + i * 0.8)
        px = cx + math.cos(p_angle) * p_dist
        py = vortex_y + math.sin(p_angle) * p_dist * 0.7
        p_size = 1 + int(math.sin(t * 5 + i) > 0.3)
        pygame.draw.circle(surface, (*glow, 170), (int(px), int(py)), p_size)
    
    # ========== 【第六层】珊瑚头冠 ==========
    head_y = y + 5
    
    # 头冠基座 - 贝壳形
    crown_pts = [
        (cx - 13, head_y + 11),
        (cx - 9, head_y + 5),
        (cx - 4, head_y + 9),
        (cx, head_y - 3),
        (cx + 4, head_y + 9),
        (cx + 9, head_y + 5),
        (cx + 13, head_y + 11),
    ]
    pygame.draw.polygon(surface, armor, crown_pts)
    pygame.draw.polygon(surface, armor_light, crown_pts, 1)
    
    # 贝壳纹理
    for i in range(3):
        shell_y = head_y + 2 + i * 3
        shell_w = 8 - i * 2
        pygame.draw.line(surface, armor_dark, (cx - shell_w, shell_y), (cx + shell_w, shell_y), 1)
    
    # 中央珊瑚尖
    pygame.draw.polygon(surface, crystal, [
        (cx - 3, head_y + 5),
        (cx, head_y - 5),
        (cx + 3, head_y + 5),
    ])
    
    # 侧面珊瑚角
    for side in [-1, 1]:
        pygame.draw.polygon(surface, armor_light, [
            (cx + side * 7, head_y + 7),
            (cx + side * 11, head_y + 1),
            (cx + side * 9, head_y + 10),
        ])
        # 小珊瑚球
        pygame.draw.circle(surface, glow, (cx + side * 11, head_y + 1), 2)
    
    # 头冠宝石
    gem_size = 3 + int(1.5 * math.sin(t * 4.2))
    pygame.draw.circle(surface, core, (cx, head_y + 2), gem_size + 2)
    pygame.draw.circle(surface, crystal_light, (cx, head_y + 2), gem_size)
    pygame.draw.circle(surface, water_white, (cx - 1, head_y), 1)
    
    # ========== 【第七层】水流推进 ==========
    thrust_len = 13 + int(7 * math.sin(t * 4.8))
    
    # 主推进 - 多层水流
    for layer in range(3):
        l_len = thrust_len - layer * 4
        l_width = 7 - layer * 2
        thrust_pts = [
            (cx - l_width, y + h - 4),
            (cx, y + h + l_len),
            (cx + l_width, y + h - 4),
        ]
        if layer == 0:
            pygame.draw.polygon(surface, glow, thrust_pts)
        elif layer == 1:
            pygame.draw.polygon(surface, core, thrust_pts)
        else:
            pygame.draw.polygon(surface, crystal_light, thrust_pts)
    
    # 上升气泡
    for i in range(6):
        bubble_phase = (t * 35 + i * 15) % 25
        bub_x = cx - 6 + (i % 3) * 6
        bub_y = y + h + 4 - bubble_phase
        bub_r = max(1, 3 - int(bubble_phase / 10))
        if bub_y > y + h - 8 and bub_r > 0:
            bub_alpha = int(150 - bubble_phase * 4)
            pygame.draw.circle(surface, (*water_white, bub_alpha), (int(bub_x), int(bub_y)), bub_r)
    
    # 侧推进 - 水流
    for side in [-1, 1]:
        sx = cx + side * 15
        s_len = int(thrust_len * 0.6)
        pygame.draw.polygon(surface, (*glow, 170), [
            (sx - 2, y + h - 9),
            (sx, y + h + s_len),
            (sx + 2, y + h - 9),
        ])
    
    # 推进器喷口
    pygame.draw.ellipse(surface, armor_dark, (cx - 10, y + h - 7, 20, 5))
    pygame.draw.ellipse(surface, armor_shadow, (cx - 7, y + h - 6, 14, 3))


# ==================== 棱镜女皇涂装 ====================
def draw_crystal_providence(surface, x, y, w, h, frame, style):
    """
    棱镜女皇 - 钻石神殿形态
    特色：多面体钻石主体 + 光谱棱镜翼 + 折射核心 + 4个旋转碎片浮游炮
    """
    theme = get_providence_theme(style)
    armor = theme["armor"]        # 钻石白
    crystal = theme["crystal"]    # 棱镜蓝
    core = theme["core"]          # 纯白核心
    flame = theme["flame"]        # 冰蓝焰
    glow = theme["glow"]          # 钻石光
    border = theme["border"]
    
    armor_light = tuple(min(255, c + 35) for c in armor)
    armor_dark = tuple(max(0, c - 30) for c in armor)
    armor_shadow = tuple(max(0, c - 60) for c in armor)
    crystal_light = tuple(min(255, c + 45) for c in crystal)
    pure_white = (255, 255, 255)
    
    # 彩虹光谱色
    spectrum = [
        (255, 80, 80),    # 红
        (255, 180, 80),   # 橙
        (255, 255, 100),  # 黄
        (100, 255, 100),  # 绿
        (80, 180, 255),   # 青
        (180, 100, 255),  # 紫
    ]
    
    t = frame * 0.05
    cx, cy = x + w // 2, y + h // 2
    
    # ========== 【第一层】光谱折射背景 ==========
    # 旋转光谱环
    for i, spec_color in enumerate(spectrum):
        ring_angle = t * 1.5 + i * (math.pi / 3)
        ring_dist = 42 + 6 * math.sin(t * 2 + i * 0.5)
        ring_x = cx + math.cos(ring_angle) * ring_dist * 0.4
        ring_y = cy + math.sin(ring_angle) * ring_dist * 0.3
        ring_alpha = int(30 + 15 * math.sin(t * 2.5 + i))
        
        glow_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*spec_color, ring_alpha), (12, 12), 10)
        surface.blit(glow_surf, (int(ring_x) - 12, int(ring_y) - 12))
    
    # 钻石光晕
    for i in range(5):
        r = int(46 - i * 8 + 4 * math.sin(t * 1.8 + i * 0.6))
        alpha = max(0, 28 - i * 5)
        if r > 0:
            glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*glow, alpha), (r + 2, r + 2), r)
            surface.blit(glow_surf, (cx - r - 2, cy - r - 2))
    
    # ========== 【第二层】六片光谱棱镜翼 ==========
    prism_float = 4 * math.sin(t * 2.3)
    
    for wing_idx in range(6):
        # 翼分布
        if wing_idx < 2:
            angle_base = -60 + wing_idx * 120
            wing_len = 44
            wing_y_offset = -10
        elif wing_idx < 4:
            angle_base = -42 + (wing_idx - 2) * 84
            wing_len = 36
            wing_y_offset = 8
        else:
            angle_base = -26 + (wing_idx - 4) * 52
            wing_len = 28
            wing_y_offset = 22
        
        side = 1 if wing_idx % 2 == 1 else -1
        refract = 5 * math.sin(t * 3 + wing_idx * 0.9) * side
        
        root_x = cx + side * 17
        root_y = cy + wing_y_offset + prism_float
        tip_x = root_x + side * wing_len + refract
        tip_y = root_y - 6 + wing_idx * 2.5
        
        # 棱镜形状 - 多面切割
        facet_pts = []
        facets = 10
        for seg in range(facets + 1):
            prog = seg / facets
            # 钻石切面形状
            width = 13 * math.sin(prog * math.pi)
            # 添加棱镜切面效果
            if prog < 0.3 or prog > 0.7:
                width *= 0.7
            width = max(2, width)
            
            px = root_x + (tip_x - root_x) * prog
            py = root_y + (tip_y - root_y) * prog
            facet_pts.append((int(px), int(py - width)))
        
        for seg in range(facets, -1, -1):
            prog = seg / facets
            width = 13 * math.sin(prog * math.pi)
            if prog < 0.3 or prog > 0.7:
                width *= 0.7
            width = max(2, width)
            
            px = root_x + (tip_x - root_x) * prog
            py = root_y + (tip_y - root_y) * prog
            facet_pts.append((int(px), int(py + width)))
        
        if len(facet_pts) >= 3:
            # 主体 - 高透明水晶
            pygame.draw.polygon(surface, (*crystal, 140), facet_pts)
            
            # 边缘 - 光谱色
            spec_idx = wing_idx % len(spectrum)
            pygame.draw.polygon(surface, spectrum[spec_idx], facet_pts, 2)
            
            # 内部折射线 - 多条
            for refr_line in range(4):
                r_prog = 0.2 + refr_line * 0.2
                r_x = root_x + (tip_x - root_x) * r_prog
                r_y = root_y + (tip_y - root_y) * r_prog
                r_angle = math.radians(wing_idx * 30 + refr_line * 15)
                r_ex = r_x + math.cos(r_angle) * 6 * side
                r_ey = r_y + math.sin(r_angle) * 4
                r_alpha = int(120 - refr_line * 20)
                pygame.draw.line(surface, (*pure_white, r_alpha),
                    (int(r_x), int(r_y)), (int(r_ex), int(r_ey)), 1)
        
        # 翼尖光点
        tip_pulse = 4 + int(2 * math.sin(t * 5 + wing_idx))
        tip_spec = spectrum[wing_idx % len(spectrum)]
        pygame.draw.circle(surface, (*tip_spec, 200), (int(tip_x), int(tip_y)), tip_pulse)
        pygame.draw.circle(surface, pure_white, (int(tip_x), int(tip_y)), max(1, tip_pulse - 3))
    
    # ========== 【第三层】4个旋转晶体碎片浮游炮 ==========
    shard_orbit = 37 + 4 * math.sin(t * 1.7)
    
    for shard_idx in range(4):
        shard_angle = t * 2 + shard_idx * (math.pi / 2)
        shard_spin = t * 6 + shard_idx * math.pi
        
        sx = cx + math.cos(shard_angle) * shard_orbit
        sy = cy + math.sin(shard_angle) * shard_orbit * 0.7
        
        # 晶体碎片 - 菱形
        shard_size = 9
        shard_pts = []
        for pt in range(4):
            pt_angle = shard_spin + pt * (math.pi / 2)
            pt_dist = shard_size if pt % 2 == 0 else shard_size * 0.6
            pt_x = sx + math.cos(pt_angle) * pt_dist
            pt_y = sy + math.sin(pt_angle) * pt_dist * 0.7
            shard_pts.append((int(pt_x), int(pt_y)))
        
        if len(shard_pts) >= 3:
            # 碎片主体
            shard_color = spectrum[shard_idx % len(spectrum)]
            pygame.draw.polygon(surface, (*shard_color, 180), shard_pts)
            pygame.draw.polygon(surface, (*shard_color, 255), shard_pts, 2)
            
            # 内部高光
            pygame.draw.polygon(surface, (*pure_white, 150), [
                (int(sx - 3), int(sy)),
                (int(sx), int(sy - 3)),
                (int(sx + 3), int(sy)),
            ])
        
        # 碎片周围小光点
        for sparkle in range(3):
            sp_angle = t * 5 + shard_idx * 2 + sparkle * 2.1
            sp_dist = shard_size + 6
            sp_x = sx + math.cos(sp_angle) * sp_dist
            sp_y = sy + math.sin(sp_angle) * sp_dist * 0.8
            pygame.draw.circle(surface, pure_white, (int(sp_x), int(sp_y)), 1)
        
        # 连接光线
        line_alpha = int(50 + 30 * math.sin(t * 3 + shard_idx))
        pygame.draw.line(surface, (*glow, line_alpha), (int(sx), int(sy)), (cx, cy), 1)
    
    # ========== 【第四层】钻石神殿主体 ==========
    # 外形：多面钻石切割
    body_pts = [
        (cx, y + 1),              # 顶尖
        (cx + 5, y + 6),          # 右上小切面
        (cx + 18, y + 18),        # 右肩大切面
        (cx + 22, cy - 7),        # 右上腰
        (cx + 25, cy + 4),        # 右腰最宽
        (cx + 21, cy + 17),       # 右下腰
        (cx + 13, y + h - 8),     # 右底切面
        (cx, y + h - 1),          # 底尖
        (cx - 13, y + h - 8),     # 左底切面
        (cx - 21, cy + 17),       # 左下腰
        (cx - 25, cy + 4),        # 左腰最宽
        (cx - 22, cy - 7),        # 左上腰
        (cx - 18, y + 18),        # 左肩大切面
        (cx - 5, y + 6),          # 左上小切面
    ]
    pygame.draw.polygon(surface, armor, body_pts)
    pygame.draw.polygon(surface, armor_light, body_pts, 2)
    
    # 内层高光面
    inner_pts = [
        (cx, y + 9),
        (cx + 12, y + 23),
        (cx + 16, cy - 4),
        (cx + 14, cy + 11),
        (cx + 9, y + h - 16),
        (cx, y + h - 10),
        (cx - 9, y + h - 16),
        (cx - 14, cy + 11),
        (cx - 16, cy - 4),
        (cx - 12, y + 23),
    ]
    pygame.draw.polygon(surface, armor_light, inner_pts)
    
    # 钻石切面线 - 精密网格
    cut_lines = [
        ((cx - 14, y + 20), (cx + 14, y + 20)),
        ((cx - 18, cy - 2), (cx + 18, cy - 2)),
        ((cx - 16, cy + 10), (cx + 16, cy + 10)),
        ((cx - 11, cy + 20), (cx + 11, cy + 20)),
        ((cx, y + 12), (cx, cy + 18)),
        ((cx - 8, y + 16), (cx - 12, cy + 12)),
        ((cx + 8, y + 16), (cx + 12, cy + 12)),
    ]
    for line_start, line_end in cut_lines:
        pygame.draw.line(surface, armor_shadow, line_start, line_end, 1)
    
    # 侧面棱镜装甲
    for side in [-1, 1]:
        plate_pts = [
            (cx + side * 18, y + 20),
            (cx + side * 26, cy - 6),
            (cx + side * 24, cy + 8),
            (cx + side * 17, cy + 15),
        ]
        pygame.draw.polygon(surface, armor_dark, plate_pts)
        # 切面线
        pygame.draw.line(surface, armor_shadow,
            (cx + side * 20, y + 24), (cx + side * 22, cy + 10), 1)
    
    # ========== 【第五层】折射核心 ==========
    prism_y = cy - 4
    prism_pulse = 1 + 0.2 * math.sin(t * 3.2)
    prism_r = int(11 * prism_pulse)
    
    # 外圈光谱环
    for i, spec_c in enumerate(spectrum):
        ring_r = prism_r + 6 - i
        ring_alpha = max(0, 80 - i * 12)
        if ring_r > 0:
            pygame.draw.circle(surface, (*spec_c, ring_alpha), (cx, prism_y), ring_r, 1)
    
    # 核心主体
    pygame.draw.circle(surface, crystal, (cx, prism_y), prism_r)
    
    # 内部折射图案
    for ray in range(8):
        ray_angle = t * 4 + ray * (math.pi / 4)
        ray_len = prism_r - 2
        ray_x = cx + math.cos(ray_angle) * ray_len
        ray_y = prism_y + math.sin(ray_angle) * ray_len
        pygame.draw.line(surface, (*pure_white, 180), (cx, prism_y), (int(ray_x), int(ray_y)), 1)
    
    # 核心中央
    pygame.draw.circle(surface, core, (cx, prism_y), 5)
    pygame.draw.circle(surface, pure_white, (cx, prism_y), 3)
    
    # 高光
    pygame.draw.circle(surface, (255, 255, 255), (cx - 2, prism_y - 2), 2)
    
    # ========== 【第六层】水晶王冠 ==========
    head_y = y + 4
    
    # 王冠基座
    crown_pts = [
        (cx - 15, head_y + 12),
        (cx - 11, head_y + 5),
        (cx - 6, head_y + 9),
        (cx, head_y - 5),
        (cx + 6, head_y + 9),
        (cx + 11, head_y + 5),
        (cx + 15, head_y + 12),
    ]
    pygame.draw.polygon(surface, armor, crown_pts)
    pygame.draw.polygon(surface, armor_light, crown_pts, 1)
    
    # 中央钻石尖
    pygame.draw.polygon(surface, crystal_light, [
        (cx - 4, head_y + 6),
        (cx, head_y - 7),
        (cx + 4, head_y + 6),
    ])
    
    # 侧面钻石角
    for side in [-1, 1]:
        pygame.draw.polygon(surface, armor_light, [
            (cx + side * 9, head_y + 7),
            (cx + side * 13, head_y),
            (cx + side * 11, head_y + 10),
        ])
        # 钻石顶
        pygame.draw.circle(surface, pure_white, (cx + side * 13, head_y), 2)
    
    # 王冠宝石
    gem_size = 4 + int(1.5 * math.sin(t * 4.5))
    gem_spec = spectrum[int(t * 2) % len(spectrum)]
    pygame.draw.circle(surface, gem_spec, (cx, head_y + 3), gem_size + 2)
    pygame.draw.circle(surface, pure_white, (cx, head_y + 3), gem_size)
    pygame.draw.circle(surface, (255, 255, 255), (cx - 1, head_y + 1), 1)
    
    # ========== 【第七层】光谱推进 ==========
    thrust_len = 13 + int(7 * math.sin(t * 5))
    
    # 主推进 - 彩虹渐变
    for layer in range(3):
        l_len = thrust_len - layer * 4
        l_width = 7 - layer * 2
        thrust_pts = [
            (cx - l_width, y + h - 5),
            (cx, y + h + l_len),
            (cx + l_width, y + h - 5),
        ]
        if layer == 0:
            pygame.draw.polygon(surface, glow, thrust_pts)
        elif layer == 1:
            layer_spec = spectrum[(int(t * 3)) % len(spectrum)]
            pygame.draw.polygon(surface, layer_spec, thrust_pts)
        else:
            pygame.draw.polygon(surface, pure_white, thrust_pts)
    
    # 光谱粒子
    for i in range(5):
        p_y = y + h + 2 + i * 3
        p_x = cx + int(4 * math.sin(t * 6 + i * 1.5))
        p_spec = spectrum[(i + int(t * 5)) % len(spectrum)]
        p_alpha = int(200 - i * 35)
        pygame.draw.circle(surface, (*p_spec, p_alpha), (p_x, p_y), 2)
    
    # 侧推进
    for side in [-1, 1]:
        sx = cx + side * 15
        s_len = int(thrust_len * 0.6)
        s_spec = spectrum[(1 if side > 0 else 4) % len(spectrum)]
        pygame.draw.polygon(surface, (*s_spec, 180), [
            (sx - 2, y + h - 9),
            (sx, y + h + s_len),
            (sx + 2, y + h - 9),
        ])
    
    # 推进器喷口
    pygame.draw.ellipse(surface, armor_dark, (cx - 10, y + h - 7, 20, 5))
    pygame.draw.ellipse(surface, armor_shadow, (cx - 7, y + h - 6, 14, 3))

# ==================== 熔岩神使涂装 ====================
def draw_magma_providence(surface, x, y, w, h, frame, style):
    """
    熔岩神使 - 火山堡垒形态
    特色：熔岩火山主体 + 岩浆流动翼 + 熔核 + 4个熔岩滴浮游炮
    """
    theme = get_providence_theme(style)
    armor = theme["armor"]        # 熔岩红
    crystal = theme["crystal"]    # 岩浆橙
    core = theme["core"]          # 熔核黄
    flame = theme["flame"]        # 烈焰红
    glow = theme["glow"]          # 熔光
    border = theme["border"]
    
    armor_light = tuple(min(255, c + 60) for c in armor)
    armor_dark = tuple(max(0, c - 45) for c in armor)
    armor_shadow = tuple(max(0, c - 75) for c in armor)
    crystal_light = tuple(min(255, c + 70) for c in crystal)
    lava_bright = (255, 240, 100)
    
    t = frame * 0.06
    cx, cy = x + w // 2, y + h // 2
    
    # 热浪光晕 + 六片岩浆翼 + 4个熔岩滴浮游炮 + 火山主体 + 熔核 + 火山头冠 + 岩浆推进
    # （简化版本保持兼容性，详细实现见前4个涂装参考）
    
    # 热浪光晕
    for ring in range(6):
        ring_r = 50 - ring * 7 + 5 * math.sin(t * 2.5 + ring * 0.6)
        ring_alpha = max(0, 40 - ring * 6)
        if ring_r > 0:
            heat_surf = pygame.Surface((int(ring_r) * 2 + 4, int(ring_r) * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(heat_surf, (*flame, ring_alpha), (int(ring_r) + 2, int(ring_r) + 2), int(ring_r))
            surface.blit(heat_surf, (cx - int(ring_r) - 2, cy - int(ring_r) - 2))
    
    # 六片岩浆流翼
    lava_flow = 5 * math.sin(t * 2)
    for wing_idx in range(6):
        if wing_idx < 2:
            wing_len, wing_y = 42, -8
        elif wing_idx < 4:
            wing_len, wing_y = 35, 10
        else:
            wing_len, wing_y = 27, 23
        
        side = 1 if wing_idx % 2 == 1 else -1
        root_x, root_y = cx + side * 16, cy + wing_y + lava_flow
        tip_x = root_x + side * wing_len + 6 * math.sin(t * 2.8 + wing_idx * 0.8) * side
        tip_y = root_y + 2 + wing_idx * 2.5
        
        # 岩浆流形状
        pts = []
        for seg in range(13):
            prog = seg / 12
            width = 12 * math.sin(prog * math.pi) * (1 - prog * 0.3) + 2 * math.sin(prog * math.pi * 5 + t * 3)
            px, py = root_x + (tip_x - root_x) * prog, root_y + (tip_y - root_y) * prog
            pts.append((int(px), int(py - max(2, width))))
        for seg in range(12, -1, -1):
            prog = seg / 12
            width = 12 * math.sin(prog * math.pi) * (1 - prog * 0.3) + 2 * math.sin(prog * math.pi * 5 + t * 3)
            px, py = root_x + (tip_x - root_x) * prog, root_y + (tip_y - root_y) * prog
            pts.append((int(px), int(py + max(2, width))))
        
        if len(pts) >= 3:
            pygame.draw.polygon(surface, armor_dark, pts)
            pygame.draw.polygon(surface, armor, pts, 2)
            # 裂缝发光
            for c in range(3):
                cx_crack = root_x + (tip_x - root_x) * (0.25 + c * 0.25)
                cy_crack = root_y + (tip_y - root_y) * (0.25 + c * 0.25)
                glow_val = int(150 + 100 * math.sin(t * 4 + wing_idx + c))
                pygame.draw.line(surface, (*crystal, glow_val), (int(cx_crack - 4), int(cy_crack)), (int(cx_crack + 4), int(cy_crack)), 2)
        
        # 翼尖熔岩滴
        drip_size = 4 + int(2 * math.sin(t * 5 + wing_idx))
        pygame.draw.circle(surface, crystal, (int(tip_x), int(tip_y)), drip_size)
        pygame.draw.circle(surface, lava_bright, (int(tip_x), int(tip_y)), max(1, drip_size - 2))
    
    # 4个熔岩滴浮游炮
    for lava_idx in range(4):
        lava_angle = t * 1.6 + lava_idx * (math.pi / 2)
        lx = cx + math.cos(lava_angle) * (38 + 4 * math.sin(t * 1.8))
        ly = cy + math.sin(lava_angle) * 26 + 4 * math.sin(t * 2.5 + lava_idx * 1.3)
        
        # 水滴形熔岩
        drop_pts = [(int(lx), int(ly - 10)), (int(lx + 8), int(ly)), (int(lx), int(ly + 13)), (int(lx - 8), int(ly))]
        pygame.draw.polygon(surface, armor_dark, drop_pts)
        inner_pts = [(int(lx + (p[0] - lx) * 0.7), int(ly + (p[1] - ly) * 0.7)) for p in drop_pts]
        pygame.draw.polygon(surface, crystal, inner_pts)
        pygame.draw.circle(surface, lava_bright, (int(lx), int(ly - 2)), 4)
        pygame.draw.circle(surface, (255, 255, 255), (int(lx), int(ly - 2)), 2)
        
        # 火花
        for sp in range(3):
            sp_angle = t * 6 + lava_idx * 2 + sp * 2.1
            sp_x = lx + math.cos(sp_angle) * 15
            sp_y = ly + math.sin(sp_angle) * 12
            pygame.draw.circle(surface, (*flame, int(180 + 70 * math.sin(t * 7 + sp))), (int(sp_x), int(sp_y)), 1)
        pygame.draw.line(surface, (*crystal, 60), (int(lx), int(ly)), (cx, cy), 1)
    
    # 火山主体
    body_pts = [(cx, y + 2), (cx + 20, y + 22), (cx + 26, cy + 7), (cx + 22, cy + 20), (cx + 15, y + h - 7), (cx, y + h),
                (cx - 15, y + h - 7), (cx - 22, cy + 20), (cx - 26, cy + 7), (cx - 20, y + 22)]
    pygame.draw.polygon(surface, armor, body_pts)
    pygame.draw.polygon(surface, armor_light, body_pts, 2)
    
    inner_pts = [(cx, y + 11), (cx + 14, y + 26), (cx + 17, cy - 2), (cx + 15, cy + 13), (cx + 10, y + h - 15), (cx, y + h - 9),
                 (cx - 10, y + h - 15), (cx - 15, cy + 13), (cx - 17, cy - 2), (cx - 14, y + 26)]
    pygame.draw.polygon(surface, armor_light, inner_pts)
    
    # 裂缝纹路
    for i in range(5):
        crack_y = y + 18 + i * 13
        pulse = max(0, min(255, int(120 + 130 * math.sin(t * 3.5 + i * 0.9))))
        pygame.draw.line(surface, (*crystal, pulse), (cx - 12 + i * 1.5, crack_y), (cx + 12 - i * 1.5, crack_y + 2), 2)
    
    # 熔核
    magma_pulse = 1 + 0.3 * math.sin(t * 3.5)
    magma_r = int(12 * magma_pulse)
    for ring in range(5):
        r_val = magma_r + 8 - ring * 2
        if r_val > 0:
            pygame.draw.circle(surface, (*flame, max(0, 120 - ring * 22)), (cx, cy - 3), r_val)
    pygame.draw.circle(surface, core, (cx, cy - 3), magma_r)
    pygame.draw.circle(surface, crystal_light, (cx, cy - 3), max(2, magma_r - 4))
    pygame.draw.circle(surface, lava_bright, (cx, cy - 3), max(1, magma_r - 7))
    
    # 喷发粒子
    for i in range(10):
        p_angle = t * 4.5 + i * 0.628
        p_dist = magma_r + 6 + 5 * abs(math.sin(t * 5 + i))
        px = cx + math.cos(p_angle) * p_dist
        py = cy - 3 + math.sin(p_angle) * p_dist * 0.7
        pygame.draw.circle(surface, (*crystal, int(200 + 50 * math.sin(t * 7 + i))), (int(px), int(py)), 2)
    
    # 火山口头冠
    pygame.draw.polygon(surface, armor, [(cx - 14, y + 11), (cx, y - 4), (cx + 14, y + 11)])
    pygame.draw.polygon(surface, armor_light, [(cx - 14, y + 11), (cx, y - 4), (cx + 14, y + 11)], 1)
    gem_size = 4 + int(2 * math.sin(t * 4.5))
    pygame.draw.circle(surface, (*crystal, int(150 + 100 * math.sin(t * 5))), (cx, y + 3), gem_size + 2)
    pygame.draw.circle(surface, lava_bright, (cx, y + 3), gem_size)
    
    # 岩浆推进
    thrust_len = 16 + int(9 * math.sin(t * 5.5))
    for layer in range(3):
        l_len, l_width = thrust_len - layer * 5, 8 - layer * 2
        pts = [(cx - l_width, y + h - 4), (cx, y + h + l_len), (cx + l_width, y + h - 4)]
        pygame.draw.polygon(surface, [flame, core, lava_bright][layer], pts)
    
    for i in range(6):
        p_y = y + h + 3 + i * 4
        p_alpha = int(220 - i * 35)
        if 2 - i // 4 > 0:
            pygame.draw.circle(surface, (*crystal, p_alpha), (cx + int(5 * math.sin(t * 7 + i * 1.8)), p_y), 2 - i // 4)
    
    for side in [-1, 1]:
        s_len = int(thrust_len * 0.65)
        pygame.draw.polygon(surface, (*flame, 200), [(cx + side * 16 - 3, y + h - 9), (cx + side * 16, y + h + s_len), (cx + side * 16 + 3, y + h - 9)])
    
    pygame.draw.ellipse(surface, armor_dark, (cx - 11, y + h - 7, 22, 5))
    pygame.draw.ellipse(surface, armor_shadow, (cx - 8, y + h - 6, 16, 3))

# ==================== 寒霜圣裔涂装 ====================
def draw_frost_providence(surface, x, y, w, h, frame, style):
    """寒霜圣裔 - 冰蓝寒霜+雪花结晶主题"""
    theme = get_providence_theme(style)
    armor = theme["armor"]
    crystal = theme["crystal"]
    core = theme["core"]
    flame = theme["flame"]
    glow = theme["glow"]
    
    armor_light = tuple(min(255, c + 60) for c in armor)
    armor_dark = tuple(max(0, c - 40) for c in armor)
    armor_shadow = tuple(max(0, c - 70) for c in armor)
    crystal_light = tuple(min(255, c + 80) for c in crystal)
    frost_pale = (230, 250, 255)
    frost_deep = (100, 150, 210)
    
    t = frame * 0.05
    cx, cy = x + w // 2, y + h // 2
    
    # 雪花飘落 + 六片冰晶翼 + 4个冰锥浮游炮 + 冰晶圣殿 + 冰核 + 冰冠 + 寒霜推进
    
    # 雪花飘落背景
    for snow_idx in range(18):
        snow_x = cx + int(45 * math.sin(t * 0.8 + snow_idx * 0.628))
        snow_y = y + (snow_idx * 11 + int(t * 30 + snow_idx * 50)) % (h + 40) - 15
        snow_size = 1 + (snow_idx % 3)
        if y - 15 <= snow_y <= y + h + 20:
            snow_alpha = 100 + int(80 * math.sin(t * 2.5 + snow_idx))
            pygame.draw.circle(surface, (*frost_pale, min(255, snow_alpha)), (snow_x, snow_y), snow_size)
            if snow_size >= 2:
                for dir in range(6):
                    dir_angle = dir * math.pi / 3
                    dx = snow_x + math.cos(dir_angle) * snow_size * 1.5
                    dy = snow_y + math.sin(dir_angle) * snow_size * 1.5
                    pygame.draw.line(surface, (*frost_pale, min(255, snow_alpha // 2)), (snow_x, snow_y), (int(dx), int(dy)), 1)
    
    for ring in range(5):
        ring_r = 45 - ring * 7 + 4 * math.sin(t * 2 + ring * 0.5)
        ring_alpha = max(0, 35 - ring * 6)
        if ring_r > 0:
            frost_surf = pygame.Surface((int(ring_r) * 2 + 4, int(ring_r) * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(frost_surf, (*glow, ring_alpha), (int(ring_r) + 2, int(ring_r) + 2), int(ring_r))
            surface.blit(frost_surf, (cx - int(ring_r) - 2, cy - int(ring_r) - 2))
    
    # 六片冰晶翼（六角雪花结晶）
    ice_pulse = 3.5 * math.sin(t * 1.7)
    for wing_idx in range(6):
        if wing_idx < 2:
            wing_len, wing_y = 40, -7
        elif wing_idx < 4:
            wing_len, wing_y = 33, 11
        else:
            wing_len, wing_y = 26, 24
        
        side = 1 if wing_idx % 2 == 1 else -1
        root_x, root_y = cx + side * 15, cy + wing_y + ice_pulse
        tip_x = root_x + side * wing_len + 5 * math.sin(t * 2.5 + wing_idx * 0.7) * side
        tip_y = root_y + 3 + wing_idx * 2
        
        for branch in range(6):
            branch_angle = wing_idx * 0.523 + branch * math.pi / 3 + t * 0.3
            branch_len = wing_len * 0.5
            bx = root_x + side * (tip_x - root_x) * 0.5 + math.cos(branch_angle) * branch_len * 0.6
            by = root_y + (tip_y - root_y) * 0.5 + math.sin(branch_angle) * branch_len * 0.4
            pygame.draw.line(surface, crystal, (int(root_x + side * (tip_x - root_x) * 0.5), int(root_y + (tip_y - root_y) * 0.5)), (int(bx), int(by)), 2)
            
            for sub in [-0.4, 0.4]:
                sub_angle = branch_angle + sub
                sub_len = 7
                sbx = bx + math.cos(sub_angle) * sub_len
                sby = by + math.sin(sub_angle) * sub_len * 0.6
                pygame.draw.line(surface, armor_light, (int(bx), int(by)), (int(sbx), int(sby)), 1)
        
        wing_pts = []
        for seg in range(10):
            prog = seg / 9
            width = 10 * math.sin(prog * math.pi) + 2 * math.sin(prog * math.pi * 4 + t * 2.5)
            px, py = root_x + (tip_x - root_x) * prog, root_y + (tip_y - root_y) * prog
            wing_pts.append((int(px), int(py - max(1, width))))
        for seg in range(8, -1, -1):
            prog = seg / 9
            width = 10 * math.sin(prog * math.pi) + 2 * math.sin(prog * math.pi * 4 + t * 2.5)
            px, py = root_x + (tip_x - root_x) * prog, root_y + (tip_y - root_y) * prog
            wing_pts.append((int(px), int(py + max(1, width))))
        
        if len(wing_pts) >= 3:
            pygame.draw.polygon(surface, armor_dark, wing_pts)
            pygame.draw.polygon(surface, crystal, wing_pts, 1)
        
        wing_center_x = root_x + side * (tip_x - root_x) * 0.5
        wing_center_y = root_y + (tip_y - root_y) * 0.5
        pygame.draw.circle(surface, armor, (int(wing_center_x), int(wing_center_y)), 7)
        pygame.draw.circle(surface, frost_pale, (int(wing_center_x), int(wing_center_y)), 4)
        pygame.draw.circle(surface, crystal_light, (int(wing_center_x), int(wing_center_y)), 2)
        
        icicle_len = 6 + int(2 * math.sin(t * 4 + wing_idx))
        pygame.draw.polygon(surface, crystal, [(int(tip_x), int(tip_y - icicle_len)), (int(tip_x - 3), int(tip_y)), (int(tip_x + 3), int(tip_y))])
        pygame.draw.polygon(surface, frost_pale, [(int(tip_x), int(tip_y - icicle_len)), (int(tip_x - 2), int(tip_y)), (int(tip_x + 2), int(tip_y))], 1)
    
    # 4个冰锥浮游炮
    for ice_idx in range(4):
        ice_angle = t * 1.5 + ice_idx * (math.pi / 2)
        ix = cx + math.cos(ice_angle) * (36 + 5 * math.sin(t * 2))
        iy = cy + math.sin(ice_angle) * 25 + 5 * math.sin(t * 2.3 + ice_idx * 1.2)
        
        spike_h = 14 + int(3 * math.sin(t * 3.5 + ice_idx))
        spike_pts = [(int(ix), int(iy - spike_h)), (int(ix + 6), int(iy - 2)), (int(ix), int(iy + spike_h)), (int(ix - 6), int(iy - 2))]
        pygame.draw.polygon(surface, frost_deep, spike_pts)
        pygame.draw.polygon(surface, crystal, spike_pts, 2)
        
        inner_pts = [(int(ix + (p[0] - ix) * 0.6), int(iy + (p[1] - iy) * 0.6)) for p in spike_pts]
        pygame.draw.polygon(surface, frost_pale, inner_pts)
        
        pygame.draw.circle(surface, armor, (int(ix), int(iy)), 5)
        pygame.draw.circle(surface, frost_pale, (int(ix), int(iy)), 3)
        pygame.draw.circle(surface, crystal_light, (int(ix), int(iy)), 1)
        
        for p in range(4):
            p_angle = t * 5 + ice_idx * 2 + p * 1.57
            p_x = ix + math.cos(p_angle) * 13
            p_y = iy + math.sin(p_angle) * 10
            pygame.draw.circle(surface, (*frost_pale, int(150 + 100 * math.sin(t * 6 + p))), (int(p_x), int(p_y)), 1)
        pygame.draw.line(surface, (*crystal, 50), (int(ix), int(iy)), (cx, cy), 1)
    
    # 冰晶圣殿主体
    body_pts = [(cx, y + 1), (cx + 21, y + 20), (cx + 25, cy + 6), (cx + 20, cy + 18), (cx + 14, y + h - 8), (cx, y + h - 1),
                (cx - 14, y + h - 8), (cx - 20, cy + 18), (cx - 25, cy + 6), (cx - 21, y + 20)]
    pygame.draw.polygon(surface, armor, body_pts)
    pygame.draw.polygon(surface, armor_light, body_pts, 2)
    
    inner_pts = [(cx, y + 10), (cx + 15, y + 25), (cx + 18, cy - 1), (cx + 14, cy + 12), (cx + 9, y + h - 16), (cx, y + h - 10),
                 (cx - 9, y + h - 16), (cx - 14, cy + 12), (cx - 18, cy - 1), (cx - 15, y + 25)]
    pygame.draw.polygon(surface, armor_light, inner_pts)
    
    for i in range(5):
        frost_y = y + 16 + i * 12
        frost_glow = max(0, min(255, int(100 + 120 * math.sin(t * 2.8 + i * 0.8))))
        pygame.draw.line(surface, (*crystal, frost_glow), (cx - 11 + i, frost_y), (cx + 11 - i, frost_y + 1), 1)
        pygame.draw.line(surface, (*frost_pale, frost_glow // 2), (cx - 10 + i, frost_y - 1), (cx + 10 - i, frost_y), 1)
    
    # 冰核
    ice_pulse = 1 + 0.25 * math.sin(t * 3)
    ice_r = int(11 * ice_pulse)
    for ring in range(4):
        r_val = ice_r + 6 - ring * 2
        if r_val > 0:
            pygame.draw.circle(surface, (*glow, max(0, 100 - ring * 20)), (cx, cy - 2), r_val)
    pygame.draw.circle(surface, core, (cx, cy - 2), ice_r)
    pygame.draw.circle(surface, crystal_light, (cx, cy - 2), max(2, ice_r - 4))
    pygame.draw.circle(surface, frost_pale, (cx, cy - 2), max(1, ice_r - 7))
    
    for i in range(8):
        shard_angle = t * 2.5 + i * 0.785
        shard_dist = ice_r + 8 + 4 * abs(math.sin(t * 4 + i))
        sx = cx + math.cos(shard_angle) * shard_dist
        sy = cy - 2 + math.sin(shard_angle) * shard_dist * 0.6
        shard_pts = [(int(sx), int(sy - 3)), (int(sx + 2), int(sy)), (int(sx), int(sy + 3)), (int(sx - 2), int(sy))]
        pygame.draw.polygon(surface, (*crystal, int(180 + 70 * math.sin(t * 6 + i))), shard_pts)
    
    # 冰冠
    pygame.draw.polygon(surface, armor, [(cx - 13, y + 10), (cx, y - 3), (cx + 13, y + 10)])
    pygame.draw.polygon(surface, armor_light, [(cx - 13, y + 10), (cx, y - 3), (cx + 13, y + 10)], 1)
    
    for tip_side in [-1, 0, 1]:
        tip_x = cx + tip_side * 8
        pygame.draw.polygon(surface, crystal, [(tip_x - 3, y + 5), (tip_x, y - 1), (tip_x + 3, y + 5)])
        pygame.draw.polygon(surface, frost_pale, [(tip_x - 2, y + 5), (tip_x, y), (tip_x + 2, y + 5)], 1)
    
    gem_size = 4 + int(2 * math.sin(t * 3.5))
    pygame.draw.circle(surface, (*crystal, int(140 + 110 * math.sin(t * 4.5))), (cx, y + 4), gem_size + 2)
    pygame.draw.circle(surface, frost_pale, (cx, y + 4), gem_size)
    
    # 寒霜推进
    thrust_len = 15 + int(8 * math.sin(t * 4.5))
    for layer in range(3):
        l_len, l_width = thrust_len - layer * 4, 7 - layer * 2
        pts = [(cx - l_width, y + h - 4), (cx, y + h + l_len), (cx + l_width, y + h - 4)]
        pygame.draw.polygon(surface, [glow, crystal, frost_pale][layer], pts)
    
    for i in range(7):
        p_y = y + h + 2 + i * 3
        p_alpha = int(200 - i * 28)
        if 2 - i // 5 > 0:
            pygame.draw.circle(surface, (*frost_pale, p_alpha), (cx + int(4 * math.sin(t * 6 + i * 1.5)), p_y), 2 - i // 5)
    
    for side in [-1, 1]:
        s_len = int(thrust_len * 0.6)
        pygame.draw.polygon(surface, (*glow, 180), [(cx + side * 15 - 2, y + h - 8), (cx + side * 15, y + h + s_len), (cx + side * 15 + 2, y + h - 8)])
    
    pygame.draw.ellipse(surface, armor_dark, (cx - 10, y + h - 6, 20, 5))
    pygame.draw.ellipse(surface, armor_shadow, (cx - 7, y + h - 5, 14, 3))

# ==================== 虚空神裔涂装 ====================
def draw_void_providence(surface, x, y, w, h, frame, style):
    """虚空神裔 - 暗紫虚空+扭曲空间主题"""
    theme = get_providence_theme(style)
    armor = theme["armor"]
    crystal = theme["crystal"]
    core = theme["core"]
    flame = theme["flame"]
    glow = theme["glow"]
    
    armor_light = tuple(min(255, c + 50) for c in armor)
    armor_dark = tuple(max(0, c - 45) for c in armor)
    armor_shadow = tuple(max(0, c - 75) for c in armor)
    crystal_light = tuple(min(255, c + 70) for c in crystal)
    void_deep = (20, 0, 35)
    void_pale = (180, 140, 220)
    
    t = frame * 0.055
    cx, cy = x + w // 2, y + h // 2
    
    # 空间裂隙背景 + 六片扭曲翼 + 4个虚空眼浮游炮 + 虚空神殿 + 奇点核 + 虚空冠 + 虚空推进
    
    # 空间裂隙背景
    for rift_idx in range(12):
        rift_angle = t * 0.6 + rift_idx * 0.523
        rift_dist = 35 + 10 * math.sin(t * 2 + rift_idx)
        rx = cx + math.cos(rift_angle) * rift_dist
        ry = cy + math.sin(rift_angle) * rift_dist * 0.7
        rift_len = 8 + int(5 * math.sin(t * 3.5 + rift_idx))
        rift_alpha = int(80 + 80 * math.sin(t * 4 + rift_idx * 0.8))
        rift_end_angle = rift_angle + 0.3 + 0.2 * math.sin(t * 5 + rift_idx)
        rx2 = rx + math.cos(rift_end_angle) * rift_len
        ry2 = ry + math.sin(rift_end_angle) * rift_len
        pygame.draw.line(surface, (*crystal, rift_alpha), (int(rx), int(ry)), (int(rx2), int(ry2)), 2)
        pygame.draw.line(surface, (*void_pale, rift_alpha // 2), (int(rx - 1), int(ry)), (int(rx2 - 1), int(ry2)), 1)
    
    # 虚空漩涡光晕
    for ring in range(6):
        ring_r = 48 - ring * 7 + 4 * math.sin(t * 2.2 + ring * 0.6)
        ring_alpha = max(0, 35 - ring * 5)
        if ring_r > 0:
            void_surf = pygame.Surface((int(ring_r) * 2 + 4, int(ring_r) * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(void_surf, (*glow, ring_alpha), (int(ring_r) + 2, int(ring_r) + 2), int(ring_r))
            surface.blit(void_surf, (cx - int(ring_r) - 2, cy - int(ring_r) - 2))
    
    # 六片扭曲空间翼
    warp_pulse = 4 * math.sin(t * 1.8)
    for wing_idx in range(6):
        if wing_idx < 2:
            wing_len, wing_y = 42, -8
        elif wing_idx < 4:
            wing_len, wing_y = 35, 10
        else:
            wing_len, wing_y = 28, 23
        
        side = 1 if wing_idx % 2 == 1 else -1
        warp_x = 3 * math.sin(t * 3.2 + wing_idx * 0.9)
        warp_y = 2 * math.cos(t * 2.8 + wing_idx * 0.7)
        root_x, root_y = cx + side * 16 + warp_x, cy + wing_y + warp_pulse + warp_y
        tip_x = root_x + side * wing_len + 6 * math.sin(t * 2.6 + wing_idx * 0.8) * side
        tip_y = root_y + 2 + wing_idx * 2.2
        
        # 扭曲空间形状
        pts = []
        for seg in range(12):
            prog = seg / 11
            distort = 3 * math.sin(prog * math.pi * 3 + t * 4 + wing_idx)
            width = 11 * math.sin(prog * math.pi) * (1 - prog * 0.25) + distort
            px, py = root_x + (tip_x - root_x) * prog, root_y + (tip_y - root_y) * prog
            pts.append((int(px), int(py - max(2, width))))
        for seg in range(11, -1, -1):
            prog = seg / 11
            distort = 3 * math.sin(prog * math.pi * 3 + t * 4 + wing_idx)
            width = 11 * math.sin(prog * math.pi) * (1 - prog * 0.25) + distort
            px, py = root_x + (tip_x - root_x) * prog, root_y + (tip_y - root_y) * prog
            pts.append((int(px), int(py + max(2, width))))
        
        if len(pts) >= 3:
            pygame.draw.polygon(surface, armor_dark, pts)
            pygame.draw.polygon(surface, crystal, pts, 1)
            # 空间裂缝发光
            for c in range(4):
                cx_crack = root_x + (tip_x - root_x) * (0.2 + c * 0.2)
                cy_crack = root_y + (tip_y - root_y) * (0.2 + c * 0.2)
                glow_val = max(0, min(255, int(120 + 130 * math.sin(t * 5 + wing_idx + c))))
                pygame.draw.line(surface, (*core, glow_val), (int(cx_crack - 3), int(cy_crack - 1)), (int(cx_crack + 3), int(cy_crack + 1)), 2)
        
        # 翼尖虚空点
        void_size = 4 + int(2 * math.sin(t * 4.5 + wing_idx))
        pygame.draw.circle(surface, void_deep, (int(tip_x), int(tip_y)), void_size + 2)
        pygame.draw.circle(surface, crystal, (int(tip_x), int(tip_y)), void_size)
        pygame.draw.circle(surface, void_pale, (int(tip_x), int(tip_y)), max(1, void_size - 2))
    
    # 4个虚空眼浮游炮
    for eye_idx in range(4):
        eye_angle = t * 1.4 + eye_idx * (math.pi / 2)
        ex = cx + math.cos(eye_angle) * (38 + 5 * math.sin(t * 2.2))
        ey = cy + math.sin(eye_angle) * 26 + 5 * math.sin(t * 2.6 + eye_idx * 1.3)
        
        # 眼球形状
        eye_r = 10 + int(2 * math.sin(t * 3 + eye_idx))
        pygame.draw.ellipse(surface, armor_dark, (int(ex - eye_r), int(ey - eye_r * 0.7), eye_r * 2, int(eye_r * 1.4)))
        pygame.draw.ellipse(surface, crystal, (int(ex - eye_r), int(ey - eye_r * 0.7), eye_r * 2, int(eye_r * 1.4)), 2)
        
        # 眼白和瞳孔
        pygame.draw.ellipse(surface, void_pale, (int(ex - eye_r * 0.6), int(ey - eye_r * 0.4), int(eye_r * 1.2), int(eye_r * 0.8)))
        pupil_offset_x = int(3 * math.sin(t * 2 + eye_idx))
        pupil_offset_y = int(2 * math.cos(t * 2.5 + eye_idx))
        pygame.draw.circle(surface, void_deep, (int(ex + pupil_offset_x), int(ey + pupil_offset_y)), 4)
        pygame.draw.circle(surface, core, (int(ex + pupil_offset_x), int(ey + pupil_offset_y)), 2)
        pygame.draw.circle(surface, crystal_light, (int(ex + pupil_offset_x - 1), int(ey + pupil_offset_y - 1)), 1)
        
        # 眼部能量线
        for l in range(3):
            l_angle = t * 4 + eye_idx * 2 + l * 2.1
            l_x = ex + math.cos(l_angle) * 16
            l_y = ey + math.sin(l_angle) * 12
            pygame.draw.line(surface, (*crystal, int(100 + 100 * math.sin(t * 6 + l))), (int(ex), int(ey)), (int(l_x), int(l_y)), 1)
        pygame.draw.line(surface, (*glow, 45), (int(ex), int(ey)), (cx, cy), 1)
    
    # 虚空神殿主体
    body_pts = [(cx, y + 2), (cx + 22, y + 21), (cx + 26, cy + 7), (cx + 21, cy + 19), (cx + 14, y + h - 8), (cx, y + h - 1),
                (cx - 14, y + h - 8), (cx - 21, cy + 19), (cx - 26, cy + 7), (cx - 22, y + 21)]
    pygame.draw.polygon(surface, armor, body_pts)
    pygame.draw.polygon(surface, armor_light, body_pts, 2)
    
    inner_pts = [(cx, y + 11), (cx + 15, y + 26), (cx + 18, cy - 1), (cx + 14, cy + 12), (cx + 9, y + h - 16), (cx, y + h - 9),
                 (cx - 9, y + h - 16), (cx - 14, cy + 12), (cx - 18, cy - 1), (cx - 15, y + 26)]
    pygame.draw.polygon(surface, armor_light, inner_pts)
    
    # 空间扭曲纹路
    for i in range(6):
        warp_y = y + 16 + i * 11
        warp_offset = 4 * math.sin(t * 3.5 + i * 0.8)
        warp_alpha = max(0, min(255, int(90 + 130 * math.sin(t * 3 + i * 0.9))))
        pygame.draw.line(surface, (*crystal, warp_alpha), (cx - 12 + warp_offset, warp_y), (cx + 12 - warp_offset, warp_y + 2), 1)
        pygame.draw.line(surface, (*void_pale, warp_alpha // 2), (cx - 11 + warp_offset, warp_y - 1), (cx + 11 - warp_offset, warp_y + 1), 1)
    
    # 奇点核心
    singularity_pulse = 1 + 0.3 * math.sin(t * 3.5)
    singularity_r = int(12 * singularity_pulse)
    for ring in range(5):
        r_val = singularity_r + 8 - ring * 2
        if r_val > 0:
            pygame.draw.circle(surface, (*glow, max(0, 110 - ring * 20)), (cx, cy - 2), r_val)
    pygame.draw.circle(surface, void_deep, (cx, cy - 2), singularity_r + 2)
    pygame.draw.circle(surface, core, (cx, cy - 2), singularity_r)
    pygame.draw.circle(surface, crystal_light, (cx, cy - 2), max(2, singularity_r - 4))
    pygame.draw.circle(surface, void_pale, (cx, cy - 2), max(1, singularity_r - 7))
    
    # 吸收粒子
    for i in range(10):
        p_angle = -t * 3 + i * 0.628
        p_dist = singularity_r + 12 - 6 * ((t * 2 + i) % 1)
        px = cx + math.cos(p_angle) * p_dist
        py = cy - 2 + math.sin(p_angle) * p_dist * 0.7
        pygame.draw.circle(surface, (*crystal, int(150 + 100 * math.sin(t * 6 + i))), (int(px), int(py)), 2)
    
    # 虚空冠
    pygame.draw.polygon(surface, armor, [(cx - 14, y + 11), (cx, y - 4), (cx + 14, y + 11)])
    pygame.draw.polygon(surface, armor_light, [(cx - 14, y + 11), (cx, y - 4), (cx + 14, y + 11)], 1)
    
    # 三眼装饰
    for eye_pos in [-1, 0, 1]:
        eye_x = cx + eye_pos * 7
        eye_y = y + 4 + abs(eye_pos) * 2
        pygame.draw.ellipse(surface, void_deep, (eye_x - 4, eye_y - 2, 8, 4))
        pygame.draw.ellipse(surface, crystal, (eye_x - 4, eye_y - 2, 8, 4), 1)
        pygame.draw.circle(surface, core, (eye_x, eye_y), 2)
    
    gem_size = 4 + int(2 * math.sin(t * 4))
    pygame.draw.circle(surface, (*crystal, int(130 + 120 * math.sin(t * 4.5))), (cx, y + 3), gem_size + 2)
    pygame.draw.circle(surface, void_pale, (cx, y + 3), gem_size)
    
    # 虚空推进
    thrust_len = 16 + int(9 * math.sin(t * 4.8))
    for layer in range(3):
        l_len, l_width = thrust_len - layer * 5, 8 - layer * 2
        warp = int(3 * math.sin(t * 6 + layer))
        pts = [(cx - l_width + warp, y + h - 4), (cx + warp // 2, y + h + l_len), (cx + l_width + warp, y + h - 4)]
        pygame.draw.polygon(surface, [glow, crystal, void_pale][layer], pts)
    
    for i in range(7):
        p_y = y + h + 2 + i * 3
        p_alpha = int(200 - i * 28)
        warp = int(5 * math.sin(t * 7 + i * 1.5))
        if 2 - i // 5 > 0:
            pygame.draw.circle(surface, (*crystal, p_alpha), (cx + warp, p_y), 2 - i // 5)
    
    for side in [-1, 1]:
        s_len = int(thrust_len * 0.55)
        pygame.draw.polygon(surface, (*glow, 170), [(cx + side * 16 - 2, y + h - 9), (cx + side * 16, y + h + s_len), (cx + side * 16 + 2, y + h - 9)])
    
    pygame.draw.ellipse(surface, armor_dark, (cx - 11, y + h - 7, 22, 5))
    pygame.draw.ellipse(surface, armor_shadow, (cx - 8, y + h - 6, 16, 3))

# ==================== 丛林神殿涂装 ====================
def draw_nature_providence(surface, x, y, w, h, frame, style):
    """丛林神殿 - 翠绿藤蔓+生命之叶主题"""
    theme = get_providence_theme(style)
    armor = theme["armor"]
    crystal = theme["crystal"]
    core = theme["core"]
    flame = theme["flame"]
    glow = theme["glow"]
    
    armor_light = tuple(min(255, c + 55) for c in armor)
    armor_dark = tuple(max(0, c - 40) for c in armor)
    armor_shadow = tuple(max(0, c - 70) for c in armor)
    crystal_light = tuple(min(255, c + 75) for c in crystal)
    leaf_bright = (180, 255, 150)
    leaf_deep = (40, 100, 30)
    
    t = frame * 0.05
    cx, cy = x + w // 2, y + h // 2
    
    # 花瓣飘落 + 六片藤蔓叶翼 + 4个花苞浮游炮 + 树根神殿 + 生命核 + 花冠 + 生命推进
    
    # 花瓣飘落背景
    for petal_idx in range(15):
        petal_x = cx + int(40 * math.sin(t * 0.7 + petal_idx * 0.628))
        petal_y = y + (petal_idx * 12 + int(t * 25 + petal_idx * 45)) % (h + 35) - 12
        petal_rot = t * 2 + petal_idx * 0.8
        if y - 12 <= petal_y <= y + h + 18:
            petal_alpha = int(100 + 80 * math.sin(t * 2.5 + petal_idx))
            # 花瓣形状
            petal_pts = []
            for seg in range(6):
                angle = petal_rot + seg * math.pi / 3
                r = 3 + 2 * math.sin(seg * math.pi / 3)
                px = petal_x + math.cos(angle) * r
                py = petal_y + math.sin(angle) * r * 0.6
                petal_pts.append((int(px), int(py)))
            pygame.draw.polygon(surface, (*crystal, petal_alpha), petal_pts)
    
    # 生命光晕
    for ring in range(5):
        ring_r = 44 - ring * 7 + 4 * math.sin(t * 2 + ring * 0.5)
        ring_alpha = max(0, 35 - ring * 6)
        if ring_r > 0:
            life_surf = pygame.Surface((int(ring_r) * 2 + 4, int(ring_r) * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(life_surf, (*glow, ring_alpha), (int(ring_r) + 2, int(ring_r) + 2), int(ring_r))
            surface.blit(life_surf, (cx - int(ring_r) - 2, cy - int(ring_r) - 2))
    
    # 六片藤蔓叶翼
    leaf_sway = 3.5 * math.sin(t * 1.6)
    for wing_idx in range(6):
        if wing_idx < 2:
            wing_len, wing_y = 40, -7
        elif wing_idx < 4:
            wing_len, wing_y = 33, 11
        else:
            wing_len, wing_y = 26, 24
        
        side = 1 if wing_idx % 2 == 1 else -1
        root_x, root_y = cx + side * 15, cy + wing_y + leaf_sway
        tip_x = root_x + side * wing_len + 5 * math.sin(t * 2.3 + wing_idx * 0.7) * side
        tip_y = root_y + 2 + wing_idx * 2
        
        # 藤蔓茎
        stem_pts = [(int(root_x), int(root_y))]
        for seg in range(5):
            prog = (seg + 1) / 5
            wave = 4 * math.sin(prog * math.pi * 2 + t * 2.5 + wing_idx)
            sx = root_x + (tip_x - root_x) * prog
            sy = root_y + (tip_y - root_y) * prog + wave
            stem_pts.append((int(sx), int(sy)))
        for i in range(len(stem_pts) - 1):
            pygame.draw.line(surface, armor_dark, stem_pts[i], stem_pts[i + 1], 3)
            pygame.draw.line(surface, armor, stem_pts[i], stem_pts[i + 1], 2)
        
        # 叶片形状
        leaf_pts = []
        for seg in range(10):
            prog = seg / 9
            width = 10 * math.sin(prog * math.pi) * (1 - prog * 0.2) + 2 * math.sin(prog * math.pi * 3 + t * 2)
            px, py = root_x + (tip_x - root_x) * prog, root_y + (tip_y - root_y) * prog
            leaf_pts.append((int(px), int(py - max(1, width))))
        for seg in range(8, -1, -1):
            prog = seg / 9
            width = 10 * math.sin(prog * math.pi) * (1 - prog * 0.2) + 2 * math.sin(prog * math.pi * 3 + t * 2)
            px, py = root_x + (tip_x - root_x) * prog, root_y + (tip_y - root_y) * prog
            leaf_pts.append((int(px), int(py + max(1, width))))
        
        if len(leaf_pts) >= 3:
            pygame.draw.polygon(surface, armor, leaf_pts)
            pygame.draw.polygon(surface, armor_light, leaf_pts, 1)
            # 叶脉
            for v in range(3):
                vein_x = root_x + (tip_x - root_x) * (0.25 + v * 0.25)
                vein_y = root_y + (tip_y - root_y) * (0.25 + v * 0.25)
                pygame.draw.line(surface, crystal, (int(root_x + (tip_x - root_x) * 0.5), int(root_y + (tip_y - root_y) * 0.5)), (int(vein_x), int(vein_y - 4)), 1)
                pygame.draw.line(surface, crystal, (int(root_x + (tip_x - root_x) * 0.5), int(root_y + (tip_y - root_y) * 0.5)), (int(vein_x), int(vein_y + 4)), 1)
        
        # 翼尖花苞
        bud_size = 5 + int(2 * math.sin(t * 3.5 + wing_idx))
        pygame.draw.circle(surface, crystal, (int(tip_x), int(tip_y)), bud_size)
        pygame.draw.circle(surface, leaf_bright, (int(tip_x), int(tip_y)), max(2, bud_size - 2))
        pygame.draw.circle(surface, core, (int(tip_x), int(tip_y)), max(1, bud_size - 4))
    
    # 4个花苞浮游炮
    for bud_idx in range(4):
        bud_angle = t * 1.5 + bud_idx * (math.pi / 2)
        bx = cx + math.cos(bud_angle) * (36 + 5 * math.sin(t * 2))
        by = cy + math.sin(bud_angle) * 25 + 5 * math.sin(t * 2.3 + bud_idx * 1.2)
        
        # 花苞形状
        bud_h = 12 + int(3 * math.sin(t * 3 + bud_idx))
        # 花瓣层
        for petal in range(5):
            petal_angle = t * 2 + bud_idx + petal * 1.257
            petal_x = bx + math.cos(petal_angle) * 7
            petal_y = by + math.sin(petal_angle) * 5
            petal_pts = [(int(bx), int(by - 3)), (int(petal_x), int(petal_y)), (int(bx), int(by + 3))]
            pygame.draw.polygon(surface, (*crystal, int(180 + 70 * math.sin(t * 4 + petal))), petal_pts)
        
        pygame.draw.ellipse(surface, armor, (int(bx - 6), int(by - bud_h // 2), 12, bud_h))
        pygame.draw.ellipse(surface, armor_light, (int(bx - 6), int(by - bud_h // 2), 12, bud_h), 1)
        
        # 花蕊
        pygame.draw.circle(surface, core, (int(bx), int(by - 2)), 4)
        pygame.draw.circle(surface, leaf_bright, (int(bx), int(by - 2)), 2)
        
        # 花粉粒子
        for p in range(3):
            p_angle = t * 5 + bud_idx * 2 + p * 2.1
            p_x = bx + math.cos(p_angle) * 14
            p_y = by + math.sin(p_angle) * 11
            pygame.draw.circle(surface, (*crystal, int(150 + 100 * math.sin(t * 6 + p))), (int(p_x), int(p_y)), 1)
        pygame.draw.line(surface, (*glow, 50), (int(bx), int(by)), (cx, cy), 1)
    
    # 树根神殿主体
    body_pts = [(cx, y + 2), (cx + 20, y + 20), (cx + 24, cy + 6), (cx + 19, cy + 18), (cx + 13, y + h - 8), (cx, y + h - 1),
                (cx - 13, y + h - 8), (cx - 19, cy + 18), (cx - 24, cy + 6), (cx - 20, y + 20)]
    pygame.draw.polygon(surface, armor, body_pts)
    pygame.draw.polygon(surface, armor_light, body_pts, 2)
    
    inner_pts = [(cx, y + 10), (cx + 14, y + 25), (cx + 17, cy - 1), (cx + 13, cy + 12), (cx + 8, y + h - 16), (cx, y + h - 10),
                 (cx - 8, y + h - 16), (cx - 13, cy + 12), (cx - 17, cy - 1), (cx - 14, y + 25)]
    pygame.draw.polygon(surface, armor_light, inner_pts)
    
    # 藤蔓纹理
    for i in range(5):
        vine_y = y + 16 + i * 12
        vine_wave = 3 * math.sin(t * 2.5 + i * 0.8)
        vine_alpha = max(0, min(255, int(100 + 120 * math.sin(t * 2.8 + i * 0.9))))
        pygame.draw.arc(surface, (*crystal, vine_alpha), (cx - 12 + vine_wave, vine_y - 4, 24, 8), 0, math.pi, 2)
        pygame.draw.arc(surface, (*leaf_bright, vine_alpha // 2), (cx - 11 + vine_wave, vine_y - 3, 22, 6), 0, math.pi, 1)
    
    # 生命核心
    life_pulse = 1 + 0.25 * math.sin(t * 3)
    life_r = int(11 * life_pulse)
    for ring in range(4):
        r_val = life_r + 6 - ring * 2
        if r_val > 0:
            pygame.draw.circle(surface, (*glow, max(0, 100 - ring * 20)), (cx, cy - 2), r_val)
    pygame.draw.circle(surface, core, (cx, cy - 2), life_r)
    pygame.draw.circle(surface, crystal_light, (cx, cy - 2), max(2, life_r - 4))
    pygame.draw.circle(surface, leaf_bright, (cx, cy - 2), max(1, life_r - 7))
    
    # 生命能量粒子
    for i in range(8):
        particle_angle = t * 2.5 + i * 0.785
        particle_dist = life_r + 8 + 4 * abs(math.sin(t * 4 + i))
        px = cx + math.cos(particle_angle) * particle_dist
        py = cy - 2 + math.sin(particle_angle) * particle_dist * 0.6
        pygame.draw.circle(surface, (*crystal, int(180 + 70 * math.sin(t * 6 + i))), (int(px), int(py)), 2)
    
    # 花冠
    pygame.draw.polygon(surface, armor, [(cx - 13, y + 10), (cx, y - 3), (cx + 13, y + 10)])
    pygame.draw.polygon(surface, armor_light, [(cx - 13, y + 10), (cx, y - 3), (cx + 13, y + 10)], 1)
    
    # 花朵装饰
    for flower_pos in [-1, 0, 1]:
        fx = cx + flower_pos * 8
        fy = y + 4 + abs(flower_pos) * 2
        # 花瓣
        for petal in range(5):
            p_angle = t * 1.5 + petal * 1.257
            petal_x = fx + math.cos(p_angle) * 5
            petal_y = fy + math.sin(p_angle) * 4
            pygame.draw.circle(surface, (*crystal, int(180 + 70 * math.sin(t * 3 + petal))), (int(petal_x), int(petal_y)), 2)
        pygame.draw.circle(surface, core, (fx, fy), 3)
        pygame.draw.circle(surface, leaf_bright, (fx, fy), 2)
    
    gem_size = 4 + int(2 * math.sin(t * 3.5))
    pygame.draw.circle(surface, (*crystal, int(140 + 110 * math.sin(t * 4.5))), (cx, y + 4), gem_size + 2)
    pygame.draw.circle(surface, leaf_bright, (cx, y + 4), gem_size)
    
    # 生命推进
    thrust_len = 15 + int(8 * math.sin(t * 4.5))
    for layer in range(3):
        l_len, l_width = thrust_len - layer * 4, 7 - layer * 2
        pts = [(cx - l_width, y + h - 4), (cx, y + h + l_len), (cx + l_width, y + h - 4)]
        pygame.draw.polygon(surface, [glow, crystal, leaf_bright][layer], pts)
    
    for i in range(7):
        p_y = y + h + 2 + i * 3
        p_alpha = int(200 - i * 28)
        if 2 - i // 5 > 0:
            pygame.draw.circle(surface, (*leaf_bright, p_alpha), (cx + int(4 * math.sin(t * 6 + i * 1.5)), p_y), 2 - i // 5)
    
    for side in [-1, 1]:
        s_len = int(thrust_len * 0.6)
        pygame.draw.polygon(surface, (*glow, 180), [(cx + side * 15 - 2, y + h - 8), (cx + side * 15, y + h + s_len), (cx + side * 15 + 2, y + h - 8)])
    
    pygame.draw.ellipse(surface, armor_dark, (cx - 10, y + h - 6, 20, 5))
    pygame.draw.ellipse(surface, armor_shadow, (cx - 7, y + h - 5, 14, 3))

# ==================== 雷霆圣裁涂装 ====================
def draw_storm_providence(surface, x, y, w, h, frame, style):
    """雷霆圣裁 - 雷电+风暴云主题"""
    theme = get_providence_theme(style)
    armor = theme["armor"]
    crystal = theme["crystal"]
    core = theme["core"]
    flame = theme["flame"]
    glow = theme["glow"]
    
    armor_light = tuple(min(255, c + 55) for c in armor)
    armor_dark = tuple(max(0, c - 40) for c in armor)
    armor_shadow = tuple(max(0, c - 70) for c in armor)
    crystal_light = tuple(min(255, c + 80) for c in crystal)
    thunder_bright = (255, 255, 200)
    thunder_deep = (80, 60, 150)
    
    t = frame * 0.06
    cx, cy = x + w // 2, y + h // 2
    
    # 闪电背景 + 六片雷电翼 + 4个雷球浮游炮 + 雷云神殿 + 雷核 + 雷冠 + 雷电推进
    
    # 随机闪电背景
    if frame % 5 < 2:
        for bolt_idx in range(6):
            bolt_x = cx + int(35 * math.sin(t * 3 + bolt_idx * 1.05))
            bolt_y = cy + int(25 * math.cos(t * 2.5 + bolt_idx * 0.9))
            bolt_alpha = max(0, min(255, int(120 + 130 * math.sin(t * 8 + bolt_idx))))
            # 锯齿闪电
            bolt_pts = [(bolt_x, bolt_y)]
            for seg in range(4):
                bx = bolt_x + int(8 * math.sin(t * 10 + seg * 2 + bolt_idx)) + seg * 3
                by = bolt_y + seg * 6
                bolt_pts.append((bx, by))
            for i in range(len(bolt_pts) - 1):
                pygame.draw.line(surface, (*crystal, bolt_alpha), bolt_pts[i], bolt_pts[i + 1], 2)
                pygame.draw.line(surface, (*thunder_bright, bolt_alpha // 2), (bolt_pts[i][0] + 1, bolt_pts[i][1]), (bolt_pts[i + 1][0] + 1, bolt_pts[i + 1][1]), 1)
    
    # 雷电光晕
    for ring in range(5):
        ring_r = 46 - ring * 7 + 5 * math.sin(t * 3 + ring * 0.6)
        ring_alpha = max(0, 40 - ring * 7)
        if ring_r > 0:
            storm_surf = pygame.Surface((int(ring_r) * 2 + 4, int(ring_r) * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(storm_surf, (*glow, ring_alpha), (int(ring_r) + 2, int(ring_r) + 2), int(ring_r))
            surface.blit(storm_surf, (cx - int(ring_r) - 2, cy - int(ring_r) - 2))
    
    # 六片雷电翼（锯齿闪电形）
    storm_pulse = 4 * math.sin(t * 2.5)
    for wing_idx in range(6):
        if wing_idx < 2:
            wing_len, wing_y = 42, -8
        elif wing_idx < 4:
            wing_len, wing_y = 35, 10
        else:
            wing_len, wing_y = 27, 23
        
        side = 1 if wing_idx % 2 == 1 else -1
        root_x, root_y = cx + side * 16, cy + wing_y + storm_pulse
        tip_x = root_x + side * wing_len + 6 * math.sin(t * 3 + wing_idx * 0.8) * side
        tip_y = root_y + 2 + wing_idx * 2.2
        
        # 锯齿闪电翼形状
        bolt_pts_upper = []
        bolt_pts_lower = []
        for seg in range(10):
            prog = seg / 9
            zigzag = 6 * math.sin(prog * math.pi * 4 + t * 5) * (1 - prog)
            width = 9 * math.sin(prog * math.pi) + 3 * ((seg % 2) - 0.5)
            px, py = root_x + (tip_x - root_x) * prog, root_y + (tip_y - root_y) * prog
            bolt_pts_upper.append((int(px + zigzag * 0.3), int(py - max(2, width))))
            bolt_pts_lower.append((int(px - zigzag * 0.3), int(py + max(2, width))))
        
        bolt_pts = bolt_pts_upper + bolt_pts_lower[::-1]
        if len(bolt_pts) >= 3:
            pygame.draw.polygon(surface, armor_dark, bolt_pts)
            pygame.draw.polygon(surface, crystal, bolt_pts, 2)
            # 电弧发光
            if frame % 4 < 2:
                for c in range(3):
                    cx_arc = root_x + (tip_x - root_x) * (0.25 + c * 0.25)
                    cy_arc = root_y + (tip_y - root_y) * (0.25 + c * 0.25)
                    arc_end_x = cx_arc + 8 * math.sin(t * 8 + wing_idx + c)
                    arc_end_y = cy_arc + 5 * math.cos(t * 8 + wing_idx + c)
                    pygame.draw.line(surface, (*thunder_bright, int(180 + 70 * math.sin(t * 10 + c))), (int(cx_arc), int(cy_arc)), (int(arc_end_x), int(arc_end_y)), 2)
        
        # 翼尖电球
        ball_size = 5 + int(2 * math.sin(t * 5 + wing_idx))
        pygame.draw.circle(surface, thunder_deep, (int(tip_x), int(tip_y)), ball_size + 2)
        pygame.draw.circle(surface, crystal, (int(tip_x), int(tip_y)), ball_size)
        pygame.draw.circle(surface, thunder_bright, (int(tip_x), int(tip_y)), max(2, ball_size - 2))
    
    # 4个雷球浮游炮
    for ball_idx in range(4):
        ball_angle = t * 1.6 + ball_idx * (math.pi / 2)
        bx = cx + math.cos(ball_angle) * (37 + 5 * math.sin(t * 2.2))
        by = cy + math.sin(ball_angle) * 26 + 5 * math.sin(t * 2.5 + ball_idx * 1.3)
        
        # 雷球核心
        ball_r = 9 + int(3 * math.sin(t * 4 + ball_idx))
        pygame.draw.circle(surface, thunder_deep, (int(bx), int(by)), ball_r + 3)
        pygame.draw.circle(surface, armor, (int(bx), int(by)), ball_r)
        pygame.draw.circle(surface, crystal, (int(bx), int(by)), max(3, ball_r - 3))
        pygame.draw.circle(surface, thunder_bright, (int(bx), int(by)), max(1, ball_r - 6))
        
        # 放电弧
        if frame % 3 < 2:
            for arc in range(4):
                arc_angle = t * 6 + ball_idx * 2 + arc * 1.57
                arc_x = bx + math.cos(arc_angle) * 14
                arc_y = by + math.sin(arc_angle) * 12
                pygame.draw.line(surface, (*crystal, int(180 + 70 * math.sin(t * 8 + arc))), (int(bx), int(by)), (int(arc_x), int(arc_y)), 2)
                pygame.draw.line(surface, (*thunder_bright, int(100 + 100 * math.sin(t * 8 + arc))), (int(bx), int(by)), (int(arc_x), int(arc_y)), 1)
        pygame.draw.line(surface, (*glow, 50), (int(bx), int(by)), (cx, cy), 1)
    
    # 雷云神殿主体
    body_pts = [(cx, y + 2), (cx + 21, y + 21), (cx + 25, cy + 7), (cx + 20, cy + 19), (cx + 14, y + h - 8), (cx, y + h - 1),
                (cx - 14, y + h - 8), (cx - 20, cy + 19), (cx - 25, cy + 7), (cx - 21, y + 21)]
    pygame.draw.polygon(surface, armor, body_pts)
    pygame.draw.polygon(surface, armor_light, body_pts, 2)
    
    inner_pts = [(cx, y + 11), (cx + 15, y + 26), (cx + 18, cy - 1), (cx + 14, cy + 12), (cx + 9, y + h - 16), (cx, y + h - 9),
                 (cx - 9, y + h - 16), (cx - 14, cy + 12), (cx - 18, cy - 1), (cx - 15, y + 26)]
    pygame.draw.polygon(surface, armor_light, inner_pts)
    
    # 雷电纹路
    for i in range(5):
        storm_y = y + 16 + i * 12
        storm_offset = 4 * math.sin(t * 4 + i * 0.9)
        storm_alpha = max(0, min(255, int(100 + 150 * math.sin(t * 5 + i * 1.1))))
        pygame.draw.line(surface, (*crystal, storm_alpha), (cx - 11 + storm_offset, storm_y), (cx + 11 - storm_offset, storm_y + 2), 2)
        if frame % 6 < 3:
            pygame.draw.line(surface, (*thunder_bright, storm_alpha // 2), (cx - 10 + storm_offset, storm_y - 1), (cx + 10 - storm_offset, storm_y + 1), 1)
    
    # 雷核
    thunder_pulse = 1 + 0.35 * math.sin(t * 4)
    thunder_r = int(12 * thunder_pulse)
    for ring in range(5):
        r_val = thunder_r + 8 - ring * 2
        if r_val > 0:
            pygame.draw.circle(surface, (*glow, max(0, 120 - ring * 22)), (cx, cy - 2), r_val)
    pygame.draw.circle(surface, core, (cx, cy - 2), thunder_r)
    pygame.draw.circle(surface, crystal_light, (cx, cy - 2), max(2, thunder_r - 4))
    pygame.draw.circle(surface, thunder_bright, (cx, cy - 2), max(1, thunder_r - 7))
    
    # 核心放电
    if frame % 4 < 2:
        for i in range(6):
            arc_angle = t * 5 + i * 1.047
            arc_dist = thunder_r + 8 + 5 * abs(math.sin(t * 6 + i))
            ax = cx + math.cos(arc_angle) * arc_dist
            ay = cy - 2 + math.sin(arc_angle) * arc_dist * 0.7
            pygame.draw.line(surface, (*crystal, int(180 + 70 * math.sin(t * 8 + i))), (cx, cy - 2), (int(ax), int(ay)), 2)
    
    # 雷冠
    pygame.draw.polygon(surface, armor, [(cx - 14, y + 11), (cx, y - 4), (cx + 14, y + 11)])
    pygame.draw.polygon(surface, armor_light, [(cx - 14, y + 11), (cx, y - 4), (cx + 14, y + 11)], 1)
    
    # 闪电符文装饰
    pygame.draw.line(surface, crystal, (cx, y + 2), (cx - 4, y + 7), 2)
    pygame.draw.line(surface, crystal, (cx - 4, y + 7), (cx + 3, y + 9), 2)
    pygame.draw.line(surface, crystal, (cx + 3, y + 9), (cx, y + 12), 2)
    pygame.draw.line(surface, thunder_bright, (cx, y + 2), (cx - 3, y + 6), 1)
    
    gem_size = 4 + int(2 * math.sin(t * 4.5))
    pygame.draw.circle(surface, (*crystal, max(0, min(255, int(140 + 115 * math.sin(t * 5))))), (cx, y + 4), gem_size + 2)
    pygame.draw.circle(surface, thunder_bright, (cx, y + 4), gem_size)
    
    # 雷电推进
    thrust_len = 16 + int(10 * math.sin(t * 5.5))
    for layer in range(3):
        l_len, l_width = thrust_len - layer * 5, 8 - layer * 2
        # 锯齿形尾焰
        pts = [(cx - l_width, y + h - 4), (cx - l_width // 2, y + h + l_len // 2), (cx, y + h + l_len), (cx + l_width // 2, y + h + l_len // 2), (cx + l_width, y + h - 4)]
        pygame.draw.polygon(surface, [glow, crystal, thunder_bright][layer], pts)
    
    for i in range(7):
        p_y = y + h + 2 + i * 3
        p_alpha = int(220 - i * 30)
        if 2 - i // 5 > 0:
            pygame.draw.circle(surface, (*thunder_bright, p_alpha), (cx + int(5 * math.sin(t * 8 + i * 1.8)), p_y), 2 - i // 5)
    
    for side in [-1, 1]:
        s_len = int(thrust_len * 0.6)
        pygame.draw.polygon(surface, (*glow, 190), [(cx + side * 16 - 2, y + h - 9), (cx + side * 16, y + h + s_len), (cx + side * 16 + 2, y + h - 9)])
    
    pygame.draw.ellipse(surface, armor_dark, (cx - 11, y + h - 7, 22, 5))
    pygame.draw.ellipse(surface, armor_shadow, (cx - 8, y + h - 6, 16, 3))

# ==================== 血月神使涂装 ====================
def draw_blood_providence(surface, x, y, w, h, frame, style):
    """血月神使 - 血红+月蚀主题"""
    theme = get_providence_theme(style)
    armor = theme["armor"]
    crystal = theme["crystal"]
    core = theme["core"]
    flame = theme["flame"]
    glow = theme["glow"]
    
    armor_light = tuple(min(255, c + 50) for c in armor)
    armor_dark = tuple(max(0, c - 45) for c in armor)
    armor_shadow = tuple(max(0, c - 75) for c in armor)
    crystal_light = tuple(min(255, c + 70) for c in crystal)
    blood_bright = (255, 100, 100)
    blood_deep = (100, 20, 30)
    
    t = frame * 0.055
    cx, cy = x + w // 2, y + h // 2
    
    # 血雾飘散 + 六片血月翼 + 4个血雾浮游炮 + 血祭坛 + 血核 + 血冠 + 血焰推进
    
    # 血雾飘散背景
    for mist_idx in range(14):
        mist_x = cx + int(40 * math.sin(t * 0.8 + mist_idx * 0.628))
        mist_y = cy + int(30 * math.cos(t * 0.6 + mist_idx * 0.5))
        mist_size = 8 + int(5 * math.sin(t * 2 + mist_idx))
        mist_alpha = int(40 + 40 * math.sin(t * 2.5 + mist_idx * 0.7))
        mist_surf = pygame.Surface((mist_size * 2, mist_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(mist_surf, (*glow, mist_alpha), (mist_size, mist_size), mist_size)
        surface.blit(mist_surf, (int(mist_x - mist_size), int(mist_y - mist_size)))
    
    # 血月光晕
    for ring in range(6):
        ring_r = 48 - ring * 7 + 4 * math.sin(t * 2.2 + ring * 0.6)
        ring_alpha = max(0, 40 - ring * 6)
        if ring_r > 0:
            blood_surf = pygame.Surface((int(ring_r) * 2 + 4, int(ring_r) * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(blood_surf, (*glow, ring_alpha), (int(ring_r) + 2, int(ring_r) + 2), int(ring_r))
            surface.blit(blood_surf, (cx - int(ring_r) - 2, cy - int(ring_r) - 2))
    
    # 六片血月翼
    blood_pulse = 4 * math.sin(t * 1.8)
    for wing_idx in range(6):
        if wing_idx < 2:
            wing_len, wing_y = 42, -8
        elif wing_idx < 4:
            wing_len, wing_y = 35, 10
        else:
            wing_len, wing_y = 27, 23
        
        side = 1 if wing_idx % 2 == 1 else -1
        root_x, root_y = cx + side * 16, cy + wing_y + blood_pulse
        tip_x = root_x + side * wing_len + 5 * math.sin(t * 2.5 + wing_idx * 0.7) * side
        tip_y = root_y + 2 + wing_idx * 2.2
        
        # 血滴形翼
        pts = []
        for seg in range(12):
            prog = seg / 11
            drip = 3 * math.sin(prog * math.pi * 2 + t * 3) * prog
            width = 11 * math.sin(prog * math.pi) * (1 - prog * 0.3) + drip
            px, py = root_x + (tip_x - root_x) * prog, root_y + (tip_y - root_y) * prog
            pts.append((int(px), int(py - max(2, width))))
        for seg in range(11, -1, -1):
            prog = seg / 11
            drip = 3 * math.sin(prog * math.pi * 2 + t * 3) * prog
            width = 11 * math.sin(prog * math.pi) * (1 - prog * 0.3) + drip
            px, py = root_x + (tip_x - root_x) * prog, root_y + (tip_y - root_y) * prog
            pts.append((int(px), int(py + max(2, width))))
        
        if len(pts) >= 3:
            pygame.draw.polygon(surface, armor_dark, pts)
            pygame.draw.polygon(surface, crystal, pts, 1)
            # 血管脉动
            for v in range(4):
                vx = root_x + (tip_x - root_x) * (0.2 + v * 0.2)
                vy = root_y + (tip_y - root_y) * (0.2 + v * 0.2)
                pulse_val = max(0, min(255, int(100 + 150 * math.sin(t * 4 + wing_idx + v))))
                pygame.draw.circle(surface, (*core, pulse_val), (int(vx), int(vy)), 2)
        
        # 翼尖血滴
        drip_y = tip_y + 6 + int(4 * math.sin(t * 3.5 + wing_idx))
        pygame.draw.polygon(surface, crystal, [(int(tip_x - 4), int(tip_y)), (int(tip_x), int(drip_y)), (int(tip_x + 4), int(tip_y))])
        pygame.draw.polygon(surface, blood_bright, [(int(tip_x - 2), int(tip_y)), (int(tip_x), int(drip_y - 2)), (int(tip_x + 2), int(tip_y))])
    
    # 4个血雾浮游炮
    for fog_idx in range(4):
        fog_angle = t * 1.4 + fog_idx * (math.pi / 2)
        fx = cx + math.cos(fog_angle) * (38 + 5 * math.sin(t * 2.2))
        fy = cy + math.sin(fog_angle) * 26 + 5 * math.sin(t * 2.5 + fog_idx * 1.3)
        
        # 血雾球
        fog_r = 10 + int(3 * math.sin(t * 3 + fog_idx))
        # 外层雾气
        for layer in range(3):
            layer_r = fog_r + 5 - layer * 2
            layer_alpha = max(0, 80 - layer * 25)
            pygame.draw.circle(surface, (*glow, layer_alpha), (int(fx), int(fy)), layer_r)
        
        pygame.draw.circle(surface, armor_dark, (int(fx), int(fy)), fog_r)
        pygame.draw.circle(surface, crystal, (int(fx), int(fy)), max(4, fog_r - 3))
        pygame.draw.circle(surface, blood_bright, (int(fx), int(fy)), max(2, fog_r - 6))
        
        # 血滴飞溅
        for drip in range(4):
            drip_angle = t * 4 + fog_idx * 2 + drip * 1.57
            drip_x = fx + math.cos(drip_angle) * 15
            drip_y = fy + math.sin(drip_angle) * 12
            pygame.draw.circle(surface, (*crystal, int(150 + 100 * math.sin(t * 6 + drip))), (int(drip_x), int(drip_y)), 2)
        pygame.draw.line(surface, (*glow, 45), (int(fx), int(fy)), (cx, cy), 1)
    
    # 血祭坛主体
    body_pts = [(cx, y + 2), (cx + 22, y + 21), (cx + 26, cy + 7), (cx + 21, cy + 19), (cx + 14, y + h - 8), (cx, y + h - 1),
                (cx - 14, y + h - 8), (cx - 21, cy + 19), (cx - 26, cy + 7), (cx - 22, y + 21)]
    pygame.draw.polygon(surface, armor, body_pts)
    pygame.draw.polygon(surface, armor_light, body_pts, 2)
    
    inner_pts = [(cx, y + 11), (cx + 15, y + 26), (cx + 18, cy - 1), (cx + 14, cy + 12), (cx + 9, y + h - 16), (cx, y + h - 9),
                 (cx - 9, y + h - 16), (cx - 14, cy + 12), (cx - 18, cy - 1), (cx - 15, y + 26)]
    pygame.draw.polygon(surface, armor_light, inner_pts)
    
    # 血管纹路
    for i in range(5):
        vein_y = y + 16 + i * 12
        vein_pulse = max(0, min(255, int(100 + 150 * math.sin(t * 3.5 + i * 0.8))))
        pygame.draw.line(surface, (*crystal, vein_pulse), (cx - 12, vein_y), (cx + 12, vein_y + 2), 2)
        pygame.draw.line(surface, (*blood_bright, vein_pulse // 2), (cx - 10, vein_y + 1), (cx + 10, vein_y + 1), 1)
    
    # 血核（血月形）
    blood_moon_pulse = 1 + 0.3 * math.sin(t * 3)
    blood_r = int(12 * blood_moon_pulse)
    for ring in range(5):
        r_val = blood_r + 8 - ring * 2
        if r_val > 0:
            pygame.draw.circle(surface, (*glow, max(0, 110 - ring * 20)), (cx, cy - 2), r_val)
    pygame.draw.circle(surface, blood_deep, (cx, cy - 2), blood_r + 2)
    pygame.draw.circle(surface, core, (cx, cy - 2), blood_r)
    pygame.draw.circle(surface, crystal_light, (cx, cy - 2), max(2, blood_r - 4))
    pygame.draw.circle(surface, blood_bright, (cx, cy - 2), max(1, blood_r - 7))
    
    # 月蚀效果（遮挡部分）
    eclipse_offset = int(3 * math.sin(t * 2))
    pygame.draw.circle(surface, armor_shadow, (cx + eclipse_offset + 4, cy - 2), max(3, blood_r - 4))
    
    # 血雾环绕
    for i in range(10):
        mist_angle = t * 2.5 + i * 0.628
        mist_dist = blood_r + 10 + 5 * abs(math.sin(t * 4 + i))
        mx = cx + math.cos(mist_angle) * mist_dist
        my = cy - 2 + math.sin(mist_angle) * mist_dist * 0.7
        pygame.draw.circle(surface, (*crystal, int(150 + 100 * math.sin(t * 6 + i))), (int(mx), int(my)), 2)
    
    # 血冠
    pygame.draw.polygon(surface, armor, [(cx - 14, y + 11), (cx, y - 4), (cx + 14, y + 11)])
    pygame.draw.polygon(surface, armor_light, [(cx - 14, y + 11), (cx, y - 4), (cx + 14, y + 11)], 1)
    
    # 血月符文装饰
    moon_x, moon_y = cx, y + 4
    pygame.draw.circle(surface, blood_deep, (moon_x, moon_y), 6)
    pygame.draw.circle(surface, crystal, (moon_x, moon_y), 5)
    pygame.draw.circle(surface, blood_bright, (moon_x, moon_y), 3)
    # 月蚀遮挡
    pygame.draw.circle(surface, armor_shadow, (moon_x + 2, moon_y), 3)
    
    gem_size = 4 + int(2 * math.sin(t * 4))
    pygame.draw.circle(surface, (*crystal, int(130 + 120 * math.sin(t * 4.5))), (cx, y + 3), gem_size + 2)
    pygame.draw.circle(surface, blood_bright, (cx, y + 3), gem_size)
    
    # 血焰推进
    thrust_len = 16 + int(9 * math.sin(t * 4.8))
    for layer in range(3):
        l_len, l_width = thrust_len - layer * 5, 8 - layer * 2
        pts = [(cx - l_width, y + h - 4), (cx, y + h + l_len), (cx + l_width, y + h - 4)]
        pygame.draw.polygon(surface, [glow, crystal, blood_bright][layer], pts)
    
    for i in range(7):
        p_y = y + h + 2 + i * 3
        p_alpha = int(210 - i * 28)
        if 2 - i // 5 > 0:
            pygame.draw.circle(surface, (*blood_bright, p_alpha), (cx + int(4 * math.sin(t * 7 + i * 1.5)), p_y), 2 - i // 5)
    
    for side in [-1, 1]:
        s_len = int(thrust_len * 0.55)
        pygame.draw.polygon(surface, (*glow, 180), [(cx + side * 16 - 2, y + h - 9), (cx + side * 16, y + h + s_len), (cx + side * 16 + 2, y + h - 9)])
    
    pygame.draw.ellipse(surface, armor_dark, (cx - 11, y + h - 7, 22, 5))
    pygame.draw.ellipse(surface, armor_shadow, (cx - 8, y + h - 6, 16, 3))

# ==================== 皇金审判涂装 ====================
def draw_gold_providence(surface, x, y, w, h, frame, style):
    """皇金审判 - 黄金+王座主题"""
    theme = get_providence_theme(style)
    armor = theme["armor"]
    crystal = theme["crystal"]
    core = theme["core"]
    flame = theme["flame"]
    glow = theme["glow"]
    
    armor_light = tuple(min(255, c + 55) for c in armor)
    armor_dark = tuple(max(0, c - 40) for c in armor)
    armor_shadow = tuple(max(0, c - 70) for c in armor)
    crystal_light = tuple(min(255, c + 75) for c in crystal)
    gold_bright = (255, 240, 150)
    gold_deep = (180, 130, 40)
    
    t = frame * 0.05
    cx, cy = x + w // 2, y + h // 2
    
    # 金光粒子 + 六片皇冠翼 + 4个权杖浮游炮 + 王座神殿 + 金核 + 皇冠 + 金焰推进
    
    # 金光粒子背景
    for particle_idx in range(16):
        p_angle = t * 0.8 + particle_idx * 0.393
        p_dist = 35 + 10 * math.sin(t * 2 + particle_idx)
        px = cx + math.cos(p_angle) * p_dist
        py = cy + math.sin(p_angle) * p_dist * 0.7
        p_size = 2 + int(2 * math.sin(t * 3 + particle_idx))
        p_alpha = int(120 + 100 * math.sin(t * 3.5 + particle_idx * 0.7))
        pygame.draw.circle(surface, (*crystal, p_alpha), (int(px), int(py)), p_size)
        # 光芒放射
        for ray in range(4):
            ray_angle = t * 2 + ray * 1.57
            ray_len = p_size + 3
            rx = px + math.cos(ray_angle) * ray_len
            ry = py + math.sin(ray_angle) * ray_len
            pygame.draw.line(surface, (*gold_bright, p_alpha // 2), (int(px), int(py)), (int(rx), int(ry)), 1)
    
    # 皇金光晕
    for ring in range(6):
        ring_r = 48 - ring * 7 + 4 * math.sin(t * 2 + ring * 0.5)
        ring_alpha = max(0, 40 - ring * 6)
        if ring_r > 0:
            gold_surf = pygame.Surface((int(ring_r) * 2 + 4, int(ring_r) * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(gold_surf, (*glow, ring_alpha), (int(ring_r) + 2, int(ring_r) + 2), int(ring_r))
            surface.blit(gold_surf, (cx - int(ring_r) - 2, cy - int(ring_r) - 2))
    
    # 六片皇冠翼
    crown_pulse = 4 * math.sin(t * 1.7)
    for wing_idx in range(6):
        if wing_idx < 2:
            wing_len, wing_y = 42, -8
        elif wing_idx < 4:
            wing_len, wing_y = 35, 10
        else:
            wing_len, wing_y = 27, 23
        
        side = 1 if wing_idx % 2 == 1 else -1
        root_x, root_y = cx + side * 16, cy + wing_y + crown_pulse
        tip_x = root_x + side * wing_len + 5 * math.sin(t * 2.5 + wing_idx * 0.7) * side
        tip_y = root_y + 2 + wing_idx * 2.2
        
        # 皇冠尖齿形翼
        crown_pts = []
        for seg in range(11):
            prog = seg / 10
            # 皇冠尖齿效果
            tooth = 4 * abs(math.sin(prog * math.pi * 4)) * (1 - prog * 0.3)
            width = 10 * math.sin(prog * math.pi) + tooth
            px, py = root_x + (tip_x - root_x) * prog, root_y + (tip_y - root_y) * prog
            crown_pts.append((int(px), int(py - max(2, width))))
        for seg in range(10, -1, -1):
            prog = seg / 10
            tooth = 4 * abs(math.sin(prog * math.pi * 4)) * (1 - prog * 0.3)
            width = 10 * math.sin(prog * math.pi) + tooth
            px, py = root_x + (tip_x - root_x) * prog, root_y + (tip_y - root_y) * prog
            crown_pts.append((int(px), int(py + max(2, width))))
        
        if len(crown_pts) >= 3:
            pygame.draw.polygon(surface, armor, crown_pts)
            pygame.draw.polygon(surface, armor_light, crown_pts, 2)
            # 宝石镶嵌
            for gem in range(3):
                gem_x = root_x + (tip_x - root_x) * (0.25 + gem * 0.25)
                gem_y = root_y + (tip_y - root_y) * (0.25 + gem * 0.25)
                gem_glow = int(150 + 100 * math.sin(t * 4 + wing_idx + gem))
                pygame.draw.circle(surface, (*crystal, gem_glow), (int(gem_x), int(gem_y)), 3)
                pygame.draw.circle(surface, gold_bright, (int(gem_x), int(gem_y)), 2)
        
        # 翼尖皇冠宝石
        gem_size = 5 + int(2 * math.sin(t * 4 + wing_idx))
        pygame.draw.circle(surface, gold_deep, (int(tip_x), int(tip_y)), gem_size + 2)
        pygame.draw.circle(surface, crystal, (int(tip_x), int(tip_y)), gem_size)
        pygame.draw.circle(surface, gold_bright, (int(tip_x), int(tip_y)), max(2, gem_size - 2))
    
    # 4个权杖浮游炮
    for scepter_idx in range(4):
        scepter_angle = t * 1.5 + scepter_idx * (math.pi / 2)
        sx = cx + math.cos(scepter_angle) * (38 + 5 * math.sin(t * 2))
        sy = cy + math.sin(scepter_angle) * 26 + 5 * math.sin(t * 2.3 + scepter_idx * 1.2)
        
        # 权杖形状
        scepter_h = 16 + int(3 * math.sin(t * 3 + scepter_idx))
        # 权杖杆
        pygame.draw.rect(surface, armor_dark, (int(sx - 3), int(sy - scepter_h // 2 + 4), 6, scepter_h - 4))
        pygame.draw.rect(surface, armor, (int(sx - 2), int(sy - scepter_h // 2 + 5), 4, scepter_h - 6))
        
        # 权杖头（宝珠）
        head_y = sy - scepter_h // 2
        pygame.draw.circle(surface, gold_deep, (int(sx), int(head_y)), 7)
        pygame.draw.circle(surface, crystal, (int(sx), int(head_y)), 5)
        pygame.draw.circle(surface, gold_bright, (int(sx), int(head_y)), 3)
        pygame.draw.circle(surface, (255, 255, 255), (int(sx - 1), int(head_y - 1)), 1)
        
        # 光芒放射
        for ray in range(6):
            ray_angle = t * 3 + scepter_idx * 2 + ray * 1.047
            ray_len = 10 + 3 * math.sin(t * 5 + ray)
            rx = sx + math.cos(ray_angle) * ray_len
            ry = head_y + math.sin(ray_angle) * ray_len * 0.7
            pygame.draw.line(surface, (*crystal, int(120 + 100 * math.sin(t * 6 + ray))), (int(sx), int(head_y)), (int(rx), int(ry)), 1)
        pygame.draw.line(surface, (*glow, 50), (int(sx), int(sy)), (cx, cy), 1)
    
    # 王座神殿主体
    body_pts = [(cx, y + 2), (cx + 22, y + 21), (cx + 26, cy + 7), (cx + 21, cy + 19), (cx + 14, y + h - 8), (cx, y + h - 1),
                (cx - 14, y + h - 8), (cx - 21, cy + 19), (cx - 26, cy + 7), (cx - 22, y + 21)]
    pygame.draw.polygon(surface, armor, body_pts)
    pygame.draw.polygon(surface, armor_light, body_pts, 2)
    
    inner_pts = [(cx, y + 11), (cx + 15, y + 26), (cx + 18, cy - 1), (cx + 14, cy + 12), (cx + 9, y + h - 16), (cx, y + h - 9),
                 (cx - 9, y + h - 16), (cx - 14, cy + 12), (cx - 18, cy - 1), (cx - 15, y + 26)]
    pygame.draw.polygon(surface, armor_light, inner_pts)
    
    # 王座纹路
    for i in range(5):
        throne_y = y + 16 + i * 12
        throne_alpha = max(0, min(255, int(120 + 130 * math.sin(t * 2.8 + i * 0.8))))
        pygame.draw.line(surface, (*crystal, throne_alpha), (cx - 12, throne_y), (cx + 12, throne_y + 2), 2)
        pygame.draw.line(surface, (*gold_bright, throne_alpha // 2), (cx - 10, throne_y + 1), (cx + 10, throne_y + 1), 1)
    
    # 金核
    gold_pulse = 1 + 0.3 * math.sin(t * 3.2)
    gold_r = int(12 * gold_pulse)
    for ring in range(5):
        r_val = gold_r + 8 - ring * 2
        if r_val > 0:
            pygame.draw.circle(surface, (*glow, max(0, 120 - ring * 22)), (cx, cy - 2), r_val)
    pygame.draw.circle(surface, gold_deep, (cx, cy - 2), gold_r + 2)
    pygame.draw.circle(surface, core, (cx, cy - 2), gold_r)
    pygame.draw.circle(surface, crystal_light, (cx, cy - 2), max(2, gold_r - 4))
    pygame.draw.circle(surface, gold_bright, (cx, cy - 2), max(1, gold_r - 7))
    
    # 光芒环绕
    for i in range(10):
        ray_angle = t * 2.5 + i * 0.628
        ray_dist = gold_r + 10 + 5 * abs(math.sin(t * 4 + i))
        rx = cx + math.cos(ray_angle) * ray_dist
        ry = cy - 2 + math.sin(ray_angle) * ray_dist * 0.7
        pygame.draw.circle(surface, (*crystal, int(180 + 70 * math.sin(t * 6 + i))), (int(rx), int(ry)), 2)
    
    # 皇冠头冠
    pygame.draw.polygon(surface, armor, [(cx - 14, y + 11), (cx, y - 4), (cx + 14, y + 11)])
    pygame.draw.polygon(surface, armor_light, [(cx - 14, y + 11), (cx, y - 4), (cx + 14, y + 11)], 1)
    
    # 皇冠尖齿装饰
    for tooth in range(5):
        tooth_x = cx + (tooth - 2) * 6
        tooth_h = 4 + abs(tooth - 2) * 2
        pygame.draw.polygon(surface, crystal, [(tooth_x - 2, y + 6), (tooth_x, y + 6 - tooth_h), (tooth_x + 2, y + 6)])
        pygame.draw.polygon(surface, gold_bright, [(tooth_x - 1, y + 6), (tooth_x, y + 7 - tooth_h), (tooth_x + 1, y + 6)], 1)
    
    gem_size = 5 + int(2 * math.sin(t * 3.5))
    pygame.draw.circle(surface, (*crystal, int(140 + 110 * math.sin(t * 4.5))), (cx, y + 4), gem_size + 3)
    pygame.draw.circle(surface, gold_bright, (cx, y + 4), gem_size)
    pygame.draw.circle(surface, (255, 255, 255), (cx - 1, y + 3), 2)
    
    # 金焰推进
    thrust_len = 16 + int(9 * math.sin(t * 4.5))
    for layer in range(3):
        l_len, l_width = thrust_len - layer * 5, 8 - layer * 2
        pts = [(cx - l_width, y + h - 4), (cx, y + h + l_len), (cx + l_width, y + h - 4)]
        pygame.draw.polygon(surface, [glow, crystal, gold_bright][layer], pts)
    
    for i in range(7):
        p_y = y + h + 2 + i * 3
        p_alpha = int(210 - i * 28)
        if 2 - i // 5 > 0:
            pygame.draw.circle(surface, (*gold_bright, p_alpha), (cx + int(4 * math.sin(t * 6 + i * 1.5)), p_y), 2 - i // 5)
    
    for side in [-1, 1]:
        s_len = int(thrust_len * 0.6)
        pygame.draw.polygon(surface, (*glow, 185), [(cx + side * 16 - 2, y + h - 9), (cx + side * 16, y + h + s_len), (cx + side * 16 + 2, y + h - 9)])
    
    pygame.draw.ellipse(surface, armor_dark, (cx - 11, y + h - 7, 22, 5))
    pygame.draw.ellipse(surface, armor_shadow, (cx - 8, y + h - 6, 16, 3))

# ==================== 极光圣典涂装 ====================
def draw_aurora_providence(surface, x, y, w, h, frame, style):
    """极光圣典 - 极光+彩虹光谱主题"""
    theme = get_providence_theme(style)
    armor = theme["armor"]
    crystal = theme["crystal"]
    core = theme["core"]
    flame = theme["flame"]
    glow = theme["glow"]
    
    armor_light = tuple(min(255, c + 55) for c in armor)
    armor_dark = tuple(max(0, c - 40) for c in armor)
    armor_shadow = tuple(max(0, c - 70) for c in armor)
    crystal_light = tuple(min(255, c + 80) for c in crystal)
    
    # 极光颜色数组
    aurora_colors = [
        (80, 255, 180),   # 青绿
        (100, 200, 255),  # 天蓝
        (180, 120, 255),  # 紫罗兰
        (255, 150, 200),  # 粉红
        (255, 200, 100),  # 金黄
    ]
    
    t = frame * 0.05
    cx, cy = x + w // 2, y + h // 2
    
    # 极光波纹 + 六片彩虹丝带翼 + 4个光粒浮游炮 + 极光神殿 + 极光核 + 极光冠 + 极光推进
    
    # 极光波纹背景
    for wave_idx in range(5):
        wave_y = cy + int(20 * math.sin(t * 1.5 + wave_idx * 0.6)) - 15 + wave_idx * 8
        wave_width = 50 + int(15 * math.sin(t * 2 + wave_idx))
        wave_alpha = int(40 + 30 * math.sin(t * 2.5 + wave_idx * 0.8))
        color_idx = (wave_idx + int(t)) % len(aurora_colors)
        wave_color = aurora_colors[color_idx]
        wave_surf = pygame.Surface((wave_width * 2, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(wave_surf, (*wave_color, wave_alpha), (0, 0, wave_width * 2, 12))
        surface.blit(wave_surf, (cx - wave_width, wave_y - 6))
    
    # 极光光晕
    for ring in range(6):
        ring_r = 48 - ring * 7 + 4 * math.sin(t * 2 + ring * 0.5)
        ring_alpha = max(0, 35 - ring * 5)
        if ring_r > 0:
            color_idx = (ring + int(t * 2)) % len(aurora_colors)
            aurora_surf = pygame.Surface((int(ring_r) * 2 + 4, int(ring_r) * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(aurora_surf, (*aurora_colors[color_idx], ring_alpha), (int(ring_r) + 2, int(ring_r) + 2), int(ring_r))
            surface.blit(aurora_surf, (cx - int(ring_r) - 2, cy - int(ring_r) - 2))
    
    # 六片彩虹丝带翼
    ribbon_flow = 4 * math.sin(t * 1.8)
    for wing_idx in range(6):
        if wing_idx < 2:
            wing_len, wing_y = 42, -8
        elif wing_idx < 4:
            wing_len, wing_y = 35, 10
        else:
            wing_len, wing_y = 27, 23
        
        side = 1 if wing_idx % 2 == 1 else -1
        root_x, root_y = cx + side * 16, cy + wing_y + ribbon_flow
        tip_x = root_x + side * wing_len + 6 * math.sin(t * 2.5 + wing_idx * 0.7) * side
        tip_y = root_y + 3 + wing_idx * 2.2
        
        # 丝带波浪形翼
        for layer in range(3):
            ribbon_pts = []
            layer_offset = layer * 3
            wave_amp = 5 - layer
            color_idx = (wing_idx + layer + int(t * 3)) % len(aurora_colors)
            ribbon_color = aurora_colors[color_idx]
            
            for seg in range(12):
                prog = seg / 11
                wave = wave_amp * math.sin(prog * math.pi * 3 + t * 4 + layer)
                width = (8 - layer * 2) * math.sin(prog * math.pi) * (1 - prog * 0.25)
                px = root_x + (tip_x - root_x) * prog
                py = root_y + (tip_y - root_y) * prog + wave
                ribbon_pts.append((int(px), int(py - max(1, width) + layer_offset)))
            for seg in range(11, -1, -1):
                prog = seg / 11
                wave = wave_amp * math.sin(prog * math.pi * 3 + t * 4 + layer)
                width = (8 - layer * 2) * math.sin(prog * math.pi) * (1 - prog * 0.25)
                px = root_x + (tip_x - root_x) * prog
                py = root_y + (tip_y - root_y) * prog + wave
                ribbon_pts.append((int(px), int(py + max(1, width) + layer_offset)))
            
            if len(ribbon_pts) >= 3:
                layer_alpha = 200 - layer * 40
                pygame.draw.polygon(surface, (*ribbon_color, layer_alpha), ribbon_pts)
        
        # 翼尖光球
        color_idx = (wing_idx + int(t * 4)) % len(aurora_colors)
        tip_color = aurora_colors[color_idx]
        ball_size = 5 + int(2 * math.sin(t * 4 + wing_idx))
        pygame.draw.circle(surface, armor_dark, (int(tip_x), int(tip_y)), ball_size + 2)
        pygame.draw.circle(surface, tip_color, (int(tip_x), int(tip_y)), ball_size)
        pygame.draw.circle(surface, (255, 255, 255), (int(tip_x), int(tip_y)), max(2, ball_size - 2))
    
    # 4个光粒浮游炮
    for light_idx in range(4):
        light_angle = t * 1.5 + light_idx * (math.pi / 2)
        lx = cx + math.cos(light_angle) * (38 + 5 * math.sin(t * 2))
        ly = cy + math.sin(light_angle) * 26 + 5 * math.sin(t * 2.3 + light_idx * 1.2)
        
        # 光粒核心
        color_idx = (light_idx + int(t * 3)) % len(aurora_colors)
        light_color = aurora_colors[color_idx]
        light_r = 9 + int(3 * math.sin(t * 3.5 + light_idx))
        
        # 光晕层
        for layer in range(4):
            layer_r = light_r + 6 - layer * 2
            layer_alpha = max(0, 100 - layer * 25)
            next_color_idx = (color_idx + layer) % len(aurora_colors)
            pygame.draw.circle(surface, (*aurora_colors[next_color_idx], layer_alpha), (int(lx), int(ly)), layer_r)
        
        pygame.draw.circle(surface, armor, (int(lx), int(ly)), light_r)
        pygame.draw.circle(surface, light_color, (int(lx), int(ly)), max(4, light_r - 3))
        pygame.draw.circle(surface, (255, 255, 255), (int(lx), int(ly)), max(2, light_r - 6))
        
        # 光粒飞散
        for p in range(5):
            p_angle = t * 5 + light_idx * 2 + p * 1.257
            p_dist = 14 + 4 * math.sin(t * 6 + p)
            p_x = lx + math.cos(p_angle) * p_dist
            p_y = ly + math.sin(p_angle) * p_dist * 0.8
            p_color_idx = (color_idx + p) % len(aurora_colors)
            pygame.draw.circle(surface, (*aurora_colors[p_color_idx], int(150 + 100 * math.sin(t * 7 + p))), (int(p_x), int(p_y)), 2)
        pygame.draw.line(surface, (*glow, 45), (int(lx), int(ly)), (cx, cy), 1)
    
    # 极光神殿主体
    body_pts = [(cx, y + 2), (cx + 22, y + 21), (cx + 26, cy + 7), (cx + 21, cy + 19), (cx + 14, y + h - 8), (cx, y + h - 1),
                (cx - 14, y + h - 8), (cx - 21, cy + 19), (cx - 26, cy + 7), (cx - 22, y + 21)]
    pygame.draw.polygon(surface, armor, body_pts)
    pygame.draw.polygon(surface, armor_light, body_pts, 2)
    
    inner_pts = [(cx, y + 11), (cx + 15, y + 26), (cx + 18, cy - 1), (cx + 14, cy + 12), (cx + 9, y + h - 16), (cx, y + h - 9),
                 (cx - 9, y + h - 16), (cx - 14, cy + 12), (cx - 18, cy - 1), (cx - 15, y + 26)]
    pygame.draw.polygon(surface, armor_light, inner_pts)
    
    # 极光纹路（彩虹渐变）
    for i in range(5):
        aurora_y = y + 16 + i * 12
        color_idx = (i + int(t * 4)) % len(aurora_colors)
        aurora_alpha = max(0, min(255, int(120 + 130 * math.sin(t * 2.8 + i * 0.8))))
        pygame.draw.line(surface, (*aurora_colors[color_idx], aurora_alpha), (cx - 12, aurora_y), (cx + 12, aurora_y + 2), 2)
        next_color_idx = (color_idx + 1) % len(aurora_colors)
        pygame.draw.line(surface, (*aurora_colors[next_color_idx], aurora_alpha // 2), (cx - 10, aurora_y + 1), (cx + 10, aurora_y + 1), 1)
    
    # 极光核
    aurora_pulse = 1 + 0.3 * math.sin(t * 3)
    aurora_r = int(12 * aurora_pulse)
    for ring in range(5):
        r_val = aurora_r + 8 - ring * 2
        if r_val > 0:
            color_idx = (ring + int(t * 3)) % len(aurora_colors)
            pygame.draw.circle(surface, (*aurora_colors[color_idx], max(0, 110 - ring * 20)), (cx, cy - 2), r_val)
    pygame.draw.circle(surface, core, (cx, cy - 2), aurora_r)
    pygame.draw.circle(surface, crystal_light, (cx, cy - 2), max(2, aurora_r - 4))
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy - 2), max(1, aurora_r - 7))
    
    # 极光粒子环绕
    for i in range(12):
        particle_angle = t * 2.5 + i * 0.524
        particle_dist = aurora_r + 10 + 5 * abs(math.sin(t * 4 + i))
        px = cx + math.cos(particle_angle) * particle_dist
        py = cy - 2 + math.sin(particle_angle) * particle_dist * 0.7
        color_idx = (i + int(t * 5)) % len(aurora_colors)
        pygame.draw.circle(surface, (*aurora_colors[color_idx], int(180 + 70 * math.sin(t * 6 + i))), (int(px), int(py)), 2)
    
    # 极光冠
    pygame.draw.polygon(surface, armor, [(cx - 14, y + 11), (cx, y - 4), (cx + 14, y + 11)])
    pygame.draw.polygon(surface, armor_light, [(cx - 14, y + 11), (cx, y - 4), (cx + 14, y + 11)], 1)
    
    # 彩虹宝石装饰
    for gem_pos in range(5):
        gem_x = cx + (gem_pos - 2) * 5
        gem_y = y + 5 + abs(gem_pos - 2) * 2
        color_idx = (gem_pos + int(t * 4)) % len(aurora_colors)
        pygame.draw.circle(surface, aurora_colors[color_idx], (gem_x, gem_y), 3)
        pygame.draw.circle(surface, (255, 255, 255), (gem_x, gem_y), 1)
    
    gem_size = 5 + int(2 * math.sin(t * 3.5))
    color_idx = int(t * 4) % len(aurora_colors)
    pygame.draw.circle(surface, (*aurora_colors[color_idx], int(140 + 110 * math.sin(t * 4.5))), (cx, y + 4), gem_size + 3)
    pygame.draw.circle(surface, (255, 255, 255), (cx, y + 4), gem_size)
    
    # 极光推进
    thrust_len = 16 + int(9 * math.sin(t * 4.5))
    for layer in range(3):
        l_len, l_width = thrust_len - layer * 5, 8 - layer * 2
        color_idx = (layer + int(t * 5)) % len(aurora_colors)
        pts = [(cx - l_width, y + h - 4), (cx, y + h + l_len), (cx + l_width, y + h - 4)]
        pygame.draw.polygon(surface, aurora_colors[color_idx], pts)
    
    for i in range(8):
        p_y = y + h + 2 + i * 3
        p_alpha = int(210 - i * 25)
        color_idx = (i + int(t * 6)) % len(aurora_colors)
        if 2 - i // 5 > 0:
            pygame.draw.circle(surface, (*aurora_colors[color_idx], p_alpha), (cx + int(4 * math.sin(t * 6 + i * 1.5)), p_y), 2 - i // 5)
    
    for side in [-1, 1]:
        s_len = int(thrust_len * 0.6)
        color_idx = (side + int(t * 4)) % len(aurora_colors)
        pygame.draw.polygon(surface, (*aurora_colors[color_idx], 180), [(cx + side * 16 - 2, y + h - 9), (cx + side * 16, y + h + s_len), (cx + side * 16 + 2, y + h - 9)])
    
    pygame.draw.ellipse(surface, armor_dark, (cx - 11, y + h - 7, 22, 5))
    pygame.draw.ellipse(surface, armor_shadow, (cx - 8, y + h - 6, 16, 3))
