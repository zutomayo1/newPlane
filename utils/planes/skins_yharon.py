# -*- coding: utf-8 -*-
"""
狱炎神龙·犽戎 (Yharon) 涂装系统
原型：Terraria Calamity Mod - Yharon, Dragon of Rebirth
风格：丛林龙王变体 - 保留龙形核心元素的12套主题涂装
"""
import pygame
import math

# ==================== 12种涂装主题 ====================
YHARON_THEMES = {
    # 默认涂装 - 狱炎神龙原型
    "yharon_default": {
        "name": "狱炎神龙",
        "armor": (0, 100, 50),       # 深丛林绿
        "flame": (255, 69, 0),       # 熔岩橙
        "core": (255, 0, 0),         # 耀斑红
        "gold": (255, 215, 0),       # 圣金
        "trail": (255, 140, 0),      # 尾焰橙
        "border": (255, 100, 50),    # 边界色
    },
    
    # 【文明遗物系列】
    "yharon_pharaoh": {
        "name": "法老龙王",
        "armor": (220, 180, 80),     # 沙金色
        "flame": (100, 180, 220),    # 天蓝圣光
        "core": (255, 215, 0),       # 全视之眼金
        "gold": (255, 200, 50),      # 黄金边
        "trail": (180, 150, 100),    # 沙尘
        "border": (255, 220, 150),   # 埃及金边
    },
    
    "yharon_galleon": {
        "name": "幽灵龙船",
        "armor": (80, 60, 50),       # 腐朽木色
        "flame": (100, 200, 150),    # 幽灵绿
        "core": (150, 255, 200),     # 鬼火
        "gold": (120, 100, 70),      # 铜锈
        "trail": (150, 180, 160),    # 雾气
        "border": (100, 200, 150),   # 幽灵绿边
    },
    
    "yharon_trojan": {
        "name": "木马龙骑",
        "armor": (160, 120, 80),     # 木头色
        "flame": (200, 100, 50),     # 战火红
        "core": (255, 200, 150),     # 窗口光
        "gold": (180, 140, 80),      # 青铜
        "trail": (100, 80, 60),      # 烟尘
        "border": (200, 160, 100),   # 木纹边
    },
    
    # 【异界美食系列】
    "yharon_sashimi": {
        "name": "刺身龙王",
        "armor": (255, 130, 80),     # 三文鱼橙
        "flame": (255, 240, 230),    # 脂肪白
        "core": (255, 255, 255),     # 光泽
        "gold": (200, 80, 50),       # 深橙
        "trail": (255, 250, 240),    # 米饭色
        "border": (20, 40, 30),      # 海苔边
    },
    
    "yharon_candy": {
        "name": "糖龙暴君",
        "armor": (255, 100, 100),    # 半透明红
        "flame": (255, 220, 220),    # 糖霜白
        "core": (255, 150, 200),     # 果心
        "gold": (200, 50, 80),       # 深红
        "trail": (255, 150, 180),    # 糖浆
        "border": (255, 200, 100),   # 糖边
    },
    
    "yharon_pizza": {
        "name": "披萨飞龙",
        "armor": (255, 200, 80),     # 芝士黄
        "flame": (200, 50, 50),      # 番茄红
        "core": (255, 220, 150),     # 融化芝士
        "gold": (180, 100, 50),      # 焦边
        "trail": (220, 180, 120),    # 饼皮
        "border": (200, 50, 30),     # 番茄边
    },
    
    # 【生活异化系列】
    "yharon_surgeon": {
        "name": "外科龙刃",
        "armor": (200, 200, 210),    # 不锈钢
        "flame": (180, 50, 50),      # 血红
        "core": (255, 255, 255),     # 无影灯
        "gold": (220, 220, 230),     # 银边
        "trail": (180, 220, 200),    # 消毒绿
        "border": (100, 180, 150),   # 手术衣
    },
    
    "yharon_jackpot": {
        "name": "赌龙机神",
        "armor": (200, 50, 80),      # 赌场红
        "flame": (255, 200, 50),     # 金币金
        "core": (255, 255, 150),     # 大奖光
        "gold": (255, 180, 0),       # 铬金边
        "trail": (255, 100, 150),    # 彩带
        "border": (255, 215, 0),     # 金边
    },
    
    "yharon_office": {
        "name": "文具龙魔",
        "armor": (120, 120, 130),    # 办公灰
        "flame": (200, 200, 210),    # 订书针银
        "core": (255, 80, 80),       # 红色按钮
        "gold": (50, 50, 60),        # 黑色塑料
        "trail": (255, 255, 150),    # 便利贴黄
        "border": (200, 200, 210),   # 金属边
    },
    
    # 【自然奇观系列】
    "yharon_storm": {
        "name": "雷霆龙云",
        "armor": (100, 80, 150),     # 雷暴紫
        "flame": (255, 255, 100),    # 闪电黄
        "core": (200, 200, 255),     # 电核
        "gold": (255, 255, 255),     # 云边白
        "trail": (100, 100, 150),    # 雨云紫
        "border": (150, 200, 255),   # 天空蓝
    },
    
    "yharon_hive": {
        "name": "蜂巢龙母",
        "armor": (255, 200, 50),     # 蜜蜂黄
        "flame": (50, 30, 10),       # 蜂巢棕
        "core": (255, 255, 200),     # 蜂蜜色
        "gold": (200, 150, 50),      # 深蜂黄
        "trail": (255, 220, 100),    # 蜂蜜橙
        "border": (0, 0, 0),         # 条纹黑
    },
    
    "yharon_geode": {
        "name": "晶簇龙脉",
        "armor": (80, 80, 90),       # 岩石灰
        "flame": (200, 100, 255),    # 紫水晶
        "core": (255, 200, 255),     # 晶心粉
        "gold": (150, 80, 200),      # 紫晶边
        "trail": (180, 150, 255),    # 折射光
        "border": (100, 50, 150),    # 深紫
    },
}


def get_yharon_theme(style):
    """获取犽戎涂装主题"""
    if style in YHARON_THEMES:
        return YHARON_THEMES[style]
    return YHARON_THEMES["yharon_default"]


def get_yharon_skin_list():
    """获取所有涂装列表"""
    return list(YHARON_THEMES.keys())


def get_yharon_skin_info(style):
    """获取涂装详细信息"""
    theme = get_yharon_theme(style)
    return {
        "id": style,
        "name": theme["name"],
        "colors": {
            "armor": theme["armor"],
            "flame": theme["flame"],
            "gold": theme["gold"]
        }
    }


YHARON_STYLES = list(YHARON_THEMES.keys())


def is_yharon_style(style):
    """检查是否为犽戎涂装"""
    return style in YHARON_STYLES


# ==================== 涂装绘制调度 ====================
def draw_yharon(surface, color, x, y, w, h, frame, style="yharon_default"):
    """绘制犽戎机体 - 根据涂装调用专属绘制"""
    # 每个涂装独立绘制函数
    drawers = {
        "yharon_default": draw_default_dragon,
        "yharon_pharaoh": draw_pharaoh_dragon,
        "yharon_galleon": draw_galleon_dragon,
        "yharon_trojan": draw_trojan_dragon,
        "yharon_sashimi": draw_sashimi_dragon,
        "yharon_candy": draw_candy_dragon,
        "yharon_pizza": draw_pizza_dragon,
        "yharon_surgeon": draw_surgeon_dragon,
        "yharon_jackpot": draw_jackpot_dragon,
        "yharon_office": draw_office_dragon,
        "yharon_storm": draw_storm_dragon,
        "yharon_hive": draw_hive_dragon,
        "yharon_geode": draw_geode_dragon,
    }
    drawer = drawers.get(style, draw_default_dragon)
    drawer(surface, x, y, w, h, frame, style)


def draw_default_dragon(surface, x, y, w, h, frame, style):
    """默认狱炎神龙 - 经典丛林龙形态"""
    theme = get_yharon_theme(style)
    
    armor = theme["armor"]
    flame = theme["flame"]
    core = theme["core"]
    gold = theme["gold"]
    trail = theme["trail"]
    
    armor_light = tuple(min(255, c + 40) for c in armor)
    armor_dark = tuple(max(0, c - 30) for c in armor)
    flame_bright = tuple(min(255, c + 50) for c in flame)
    
    t = frame * 0.06
    cx, cy = x + w // 2, y + h // 2
    
    # ========== 火焰光晕 ==========
    for i in range(4):
        r = int(50 - i * 8 + 5 * math.sin(t * 2 + i))
        alpha = 40 - i * 8
        if r > 0 and alpha > 0:
            glow_surf = pygame.Surface((r * 2 + 20, r * 2 + 20), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*flame, alpha), (r + 10, r + 10), r)
            surface.blit(glow_surf, (cx - r - 10, cy - r - 10), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    # ========== 龙翼 ==========
    wing_flap = 4 * math.sin(t * 2.5)
    wing_flap2 = 3 * math.sin(t * 2.5 + 0.5)
    
    for side in [-1, 1]:
        root_x = cx + side * 10
        root_y = cy - 8
        
        tip1 = (cx + side * (w // 2 + 25), y - 15 + wing_flap)
        tip2 = (cx + side * (w // 2 + 20), cy - 10 + wing_flap2)
        tip3 = (cx + side * (w // 2 + 8), cy + 20)
        
        wing_membrane = [
            (root_x, root_y),
            (cx + side * 25, y + 5), tip1,
            (tip1[0] - side * 5, (tip1[1] + tip2[1]) // 2),
            tip2,
            (tip2[0] - side * 3, (tip2[1] + tip3[1]) // 2),
            tip3,
            (root_x, cy + 10)
        ]
        pygame.draw.polygon(surface, armor_dark, wing_membrane)
        
        # 翼膜纹理
        for i in range(5):
            vein_start = (root_x + side * 3, root_y + i * 6)
            vein_end_x = cx + side * (w // 2 + 15 - i * 4)
            vein_end_y = y + i * 12 + wing_flap * (1 - i * 0.15)
            pygame.draw.line(surface, armor_light, vein_start, (vein_end_x, vein_end_y), 1)
        
        # 翼骨
        pygame.draw.line(surface, gold, (root_x, root_y), tip1, 3)
        pygame.draw.line(surface, gold, (root_x, root_y + 5), tip2, 2)
        pygame.draw.line(surface, gold, (root_x, root_y + 12), tip3, 2)
        
        # 翼尖火焰
        flicker = 2 + int(3 * abs(math.sin(t * 6 + side)))
        pygame.draw.circle(surface, flame_bright, (int(tip1[0]), int(tip1[1])), flicker + 3)
        pygame.draw.circle(surface, core, (int(tip1[0]), int(tip1[1])), flicker)
    
    # ========== 龙躯主装甲 ==========
    body_outer = [
        (cx, y + 5),
        (cx + 20, y + 18),
        (cx + 18, cy + 8),
        (cx + 12, y + h - 12),
        (cx, y + h - 5),
        (cx - 12, y + h - 12),
        (cx - 18, cy + 8),
        (cx - 20, y + 18),
    ]
    pygame.draw.polygon(surface, armor, body_outer)
    pygame.draw.lines(surface, armor_light, True, body_outer, 2)
    
    # 内层装甲
    body_inner = [
        (cx, y + 12),
        (cx + 12, y + 22),
        (cx + 10, cy + 5),
        (cx + 6, y + h - 18),
        (cx, y + h - 12),
        (cx - 6, y + h - 18),
        (cx - 10, cy + 5),
        (cx - 12, y + 22),
    ]
    pygame.draw.polygon(surface, armor_light, body_inner)
    
    # 腹甲鳞片
    for i in range(5):
        seg_y = y + 25 + i * 12
        seg_w = 14 - i * 2
        seg_h = 8
        if seg_w > 4:
            pygame.draw.ellipse(surface, gold, (cx - seg_w // 2, seg_y, seg_w, seg_h))
    
    # 中央能量核心
    core_pulse = 6 + int(3 * math.sin(t * 4))
    pygame.draw.circle(surface, (*core, 150), (cx, cy - 5), core_pulse + 4)
    pygame.draw.circle(surface, core, (cx, cy - 5), core_pulse)
    pygame.draw.circle(surface, (255, 255, 200), (cx, cy - 5), max(1, core_pulse - 3))
    
    # ========== 龙首 ==========
    head_y = y + 6
    
    # 龙角
    for side in [-1, 1]:
        horn_base = (cx + side * 12, head_y + 2)
        horn_tip = (cx + side * 22, head_y - 14)
        horn_pts = [horn_base, horn_tip, (cx + side * 15, head_y + 5)]
        pygame.draw.polygon(surface, gold, horn_pts)
        pygame.draw.circle(surface, flame_bright, horn_tip, 2)
    
    # 头部轮廓
    head_pts = [
        (cx, y), (cx + 14, head_y + 3), (cx + 16, head_y + 14),
        (cx + 10, head_y + 22), (cx, head_y + 18), (cx - 10, head_y + 22),
        (cx - 16, head_y + 14), (cx - 14, head_y + 3),
    ]
    pygame.draw.polygon(surface, armor, head_pts)
    pygame.draw.lines(surface, armor_light, True, head_pts, 1)
    
    # 头部装甲细节
    pygame.draw.line(surface, gold, (cx, y + 2), (cx, head_y + 12), 2)
    
    # 眼睛
    for side in [-1, 1]:
        ex, ey = cx + side * 8, head_y + 10
        pygame.draw.ellipse(surface, (20, 10, 10), (ex - 5, ey - 4, 10, 8))
        eye_glow = 3 + int(2 * math.sin(t * 5))
        pygame.draw.circle(surface, core, (ex, ey), eye_glow + 2)
        pygame.draw.circle(surface, (255, 220, 150), (ex, ey), eye_glow)
        pygame.draw.ellipse(surface, (0, 0, 0), (ex - 1, ey - 3, 3, 6))
    
    # 獠牙
    for side in [-1, 1]:
        fx = cx + side * 6
        pygame.draw.polygon(surface, (255, 255, 240), [
            (fx, head_y + 18), (fx + side * 2, head_y + 26), (fx - side * 1, head_y + 19)
        ])
    
    # 鼻息火焰
    breath_intensity = abs(math.sin(t * 3))
    if breath_intensity > 0.3:
        breath_r = int(4 * breath_intensity)
        pygame.draw.circle(surface, (*flame, int(200 * breath_intensity)), (cx, head_y + 22), breath_r + 2)
    
    # ========== 尾部 ==========
    for i in range(5):
        seg_y = y + h - 8 + i * 7
        seg_w = max(2, 10 - i * 2)
        pygame.draw.ellipse(surface, armor, (cx - seg_w // 2, seg_y, seg_w, 6))
    
    # 尾刺
    pygame.draw.polygon(surface, gold, [(cx, y + h + 20), (cx - 4, y + h + 10), (cx + 4, y + h + 10)])
    
    # ========== 引擎尾焰 ==========
    flame_len = 18 + int(10 * math.sin(t * 7))
    pygame.draw.polygon(surface, trail, [(cx - 8, y + h - 3), (cx, y + h + flame_len + 5), (cx + 8, y + h - 3)])
    pygame.draw.polygon(surface, flame, [(cx - 5, y + h - 3), (cx, y + h + flame_len), (cx + 5, y + h - 3)])
    pygame.draw.polygon(surface, (255, 255, 200), [(cx - 2, y + h - 3), (cx, y + h + flame_len - 8), (cx + 2, y + h - 3)])
    
    # ========== 浮游炮阵列 ==========
    drone_time = t * 30
    drone_orbit = 40
    
    for i in range(4):
        base_angle = i * 90 + 45
        angle = math.radians(base_angle + drone_time)
        dx = int(math.cos(angle) * drone_orbit)
        dy = int(math.sin(angle) * drone_orbit * 0.5)
        drone_x, drone_y = cx + dx, cy + dy
        
        drone_size = 5
        dp = [(drone_x, drone_y - drone_size), (drone_x + drone_size - 1, drone_y),
              (drone_x, drone_y + drone_size), (drone_x - drone_size + 1, drone_y)]
        pygame.draw.polygon(surface, gold, dp)
        pygame.draw.polygon(surface, (255, 255, 200), dp, 1)
        pygame.draw.circle(surface, flame, (drone_x, drone_y), 2)
    
    # ========== 主题装饰 ==========
    draw_theme_decorations(surface, x, y, w, h, frame, style, theme, cx, cy)


# ==================== 法老龙王 - 金字塔翼+法老头冠 ====================
def draw_pharaoh_dragon(surface, x, y, w, h, frame, style):
    """法老龙王 - 金字塔状翅膀，法老头冠，圣甲虫护卫"""
    theme = get_yharon_theme(style)
    armor, flame, core, gold, trail = theme["armor"], theme["flame"], theme["core"], theme["gold"], theme["trail"]
    armor_light = tuple(min(255, c + 40) for c in armor)
    armor_dark = tuple(max(0, c - 30) for c in armor)
    t = frame * 0.06
    cx, cy = x + w // 2, y + h // 2
    
    # 金字塔翅膀 - 三角形结构
    for side in [-1, 1]:
        # 大金字塔翼
        base_x = cx + side * 15
        tip_x = cx + side * 55
        tip_y = cy - 25 + 3 * math.sin(t * 2)
        pygame.draw.polygon(surface, armor, [(base_x, cy - 10), (tip_x, tip_y), (base_x, cy + 15)])
        pygame.draw.polygon(surface, gold, [(base_x, cy - 10), (tip_x, tip_y), (base_x, cy + 15)], 2)
        # 金字塔纹理
        for i in range(4):
            ly = cy - 5 + i * 6
            lx1 = base_x + side * (5 + i * 8)
            pygame.draw.line(surface, armor_light, (base_x, ly), (int(lx1), ly), 1)
        # 荷鲁斯之眼
        eye_x = cx + side * 35
        pygame.draw.circle(surface, flame, (int(eye_x), int(tip_y + 15)), 5)
        pygame.draw.circle(surface, (255, 255, 200), (int(eye_x), int(tip_y + 15)), 3)
    
    # 法老躯干
    body = [(cx, y + 8), (cx + 18, cy), (cx + 12, y + h - 8), (cx, y + h), (cx - 12, y + h - 8), (cx - 18, cy)]
    pygame.draw.polygon(surface, armor, body)
    pygame.draw.polygon(surface, gold, body, 2)
    
    # 法老头冠 - 双层皇冠
    crown_h = 25
    pygame.draw.polygon(surface, gold, [(cx - 12, y + 12), (cx, y - crown_h), (cx + 12, y + 12)])
    pygame.draw.polygon(surface, flame, [(cx - 8, y + 10), (cx, y - crown_h + 8), (cx + 8, y + 10)])
    # 眼镜蛇装饰
    pygame.draw.arc(surface, gold, (cx - 5, y - crown_h - 5, 10, 15), 0, math.pi, 2)
    pygame.draw.circle(surface, core, (cx, y - crown_h - 3), 3)
    
    # 法老之眼
    for side in [-1, 1]:
        ex = cx + side * 8
        pygame.draw.ellipse(surface, (0, 0, 0), (ex - 4, y + 18, 8, 5))
        pygame.draw.circle(surface, flame, (ex, y + 20), 3)
    
    # 圣甲虫浮游炮
    for i in range(4):
        angle = t * 1.5 + i * math.pi / 2
        sx = cx + math.cos(angle) * 45
        sy = cy + math.sin(angle) * 28
        # 甲虫身体
        pygame.draw.ellipse(surface, gold, (int(sx) - 6, int(sy) - 4, 12, 8))
        pygame.draw.arc(surface, armor_dark, (int(sx) - 5, int(sy) - 3, 10, 6), 0, math.pi, 2)
        # 翅膀
        wing_open = 3 + 2 * math.sin(t * 8 + i)
        pygame.draw.ellipse(surface, (*flame, 150), (int(sx) - 8, int(sy) - int(wing_open) - 2, 6, int(wing_open)))
        pygame.draw.ellipse(surface, (*flame, 150), (int(sx) + 2, int(sy) - int(wing_open) - 2, 6, int(wing_open)))
    
    # 沙尘尾焰
    for i in range(5):
        sand_x = cx + (i - 2) * 4 + 3 * math.sin(t * 5 + i)
        sand_len = 15 + 8 * math.sin(t * 6 + i)
        pygame.draw.polygon(surface, trail, [(sand_x - 2, y + h), (sand_x, int(y + h + sand_len)), (sand_x + 2, y + h)])


# ==================== 幽灵龙船 - 破帆翼+骷髅龙首 ====================
def draw_galleon_dragon(surface, x, y, w, h, frame, style):
    """幽灵龙船 - 破烂船帆翅膀，骷髅船首，幽灵水手"""
    theme = get_yharon_theme(style)
    armor, flame, core, gold, trail = theme["armor"], theme["flame"], theme["core"], theme["gold"], theme["trail"]
    armor_light = tuple(min(255, c + 40) for c in armor)
    t = frame * 0.06
    cx, cy = x + w // 2, y + h // 2
    
    # 破烂船帆翅膀
    for side in [-1, 1]:
        mast_x = cx + side * 12
        # 桅杆
        pygame.draw.line(surface, gold, (mast_x, cy - 15), (mast_x, cy + 20), 3)
        # 破帆 - 不规则多边形
        sail_flap = 5 * math.sin(t * 2 + side)
        sail_pts = [
            (mast_x, cy - 12),
            (cx + side * 50 + sail_flap, cy - 20 + sail_flap),
            (cx + side * 55 + sail_flap * 1.5, cy),
            (cx + side * 45 + sail_flap, cy + 15),
            (mast_x, cy + 18)
        ]
        pygame.draw.polygon(surface, armor, sail_pts)
        # 破洞
        hole_x = cx + side * 35
        pygame.draw.circle(surface, (0, 0, 0, 0), (int(hole_x), cy - 5), 6)
        pygame.draw.circle(surface, armor_light, (int(hole_x), cy - 5), 6, 1)
        # 帆绳
        pygame.draw.line(surface, gold, (mast_x, cy - 12), (cx + side * 50, cy - 18), 1)
        pygame.draw.line(surface, gold, (mast_x, cy + 5), (cx + side * 48, cy + 10), 1)
    
    # 船体躯干
    hull = [(cx - 15, cy - 5), (cx + 15, cy - 5), (cx + 20, cy + 15), (cx, y + h + 5), (cx - 20, cy + 15)]
    pygame.draw.polygon(surface, armor, hull)
    pygame.draw.polygon(surface, gold, hull, 2)
    
    # 骷髅船首
    skull_y = y + 5
    # 骷髅轮廓
    pygame.draw.ellipse(surface, (200, 200, 180), (cx - 10, skull_y, 20, 18))
    # 眼洞 - 鬼火
    for side in [-1, 1]:
        ex = cx + side * 5
        pygame.draw.ellipse(surface, (0, 0, 0), (ex - 3, skull_y + 5, 6, 7))
        glow = 2 + int(2 * math.sin(t * 5))
        pygame.draw.circle(surface, flame, (ex, skull_y + 8), glow)
    # 鼻孔
    pygame.draw.polygon(surface, (0, 0, 0), [(cx - 2, skull_y + 13), (cx + 2, skull_y + 13), (cx, skull_y + 16)])
    # 牙齿
    for i in range(-2, 3):
        tx = cx + i * 3
        pygame.draw.rect(surface, (200, 200, 180), (tx - 1, skull_y + 17, 2, 4))
    
    # 幽灵水手浮游
    for i in range(3):
        angle = t * 1.2 + i * 2.1
        gx = cx + math.cos(angle) * 42
        gy = cy + math.sin(angle) * 25
        alpha = int(120 + 60 * math.sin(t * 3 + i))
        # 幽灵身体
        ghost_surf = pygame.Surface((16, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(ghost_surf, (*flame, alpha), (3, 0, 10, 12))
        pygame.draw.polygon(ghost_surf, (*flame, alpha - 40), [(3, 8), (13, 8), (11, 20), (5, 20)])
        # 幽灵眼睛
        pygame.draw.circle(ghost_surf, (255, 255, 255, alpha), (6, 5), 2)
        pygame.draw.circle(ghost_surf, (255, 255, 255, alpha), (10, 5), 2)
        surface.blit(ghost_surf, (int(gx) - 8, int(gy) - 10))
    
    # 鬼火尾焰
    for i in range(3):
        gf_x = cx + (i - 1) * 8
        gf_len = 20 + 10 * math.sin(t * 4 + i * 2)
        gf_alpha = int(150 + 50 * math.sin(t * 6 + i))
        pygame.draw.polygon(surface, (*flame, gf_alpha), [(gf_x - 4, y + h), (gf_x, int(y + h + gf_len)), (gf_x + 4, y + h)])
        pygame.draw.polygon(surface, (*core, gf_alpha), [(gf_x - 2, y + h), (gf_x, int(y + h + gf_len - 5)), (gf_x + 2, y + h)])


# ==================== 木马龙骑 ====================
def draw_trojan_dragon(surface, x, y, w, h, frame, style):
    """木板翅膀，战马头，车轮浮游"""
    theme = get_yharon_theme(style)
    armor, flame, core, gold, trail = theme["armor"], theme["flame"], theme["core"], theme["gold"], theme["trail"]
    armor_dark = tuple(max(0, c - 40) for c in armor)
    wood_grain = tuple(max(0, c - 20) for c in armor)
    t = frame * 0.06
    cx, cy = x + w // 2, y + h // 2
    
    # 木板拼接翅膀 - 多层木板+铆钉
    for side in [-1, 1]:
        for i in range(5):
            by = cy - 20 + i * 10
            bw = 40 - i * 6
            flap = 3 * math.sin(t * 2 + i * 0.5)
            bx1, bx2 = cx + side * 12, cx + side * (12 + bw)
            # 木板主体
            pygame.draw.polygon(surface, armor, [
                (bx1, by + flap), (bx2, by - 4 + flap),
                (bx2, by + 8 + flap), (bx1, by + 10 + flap)])
            # 木板边缘阴影
            pygame.draw.line(surface, armor_dark, (bx1, by + flap), (bx2, by - 4 + flap), 1)
            pygame.draw.line(surface, armor_dark, (bx1, by + 10 + flap), (bx2, by + 8 + flap), 1)
            # 木纹
            for j in range(2):
                gx = bx1 + side * (8 + j * 12)
                pygame.draw.line(surface, wood_grain, (int(gx), int(by + 2 + flap)), (int(gx + side * 8), int(by + 6 + flap)), 1)
            # 铆钉
            pygame.draw.circle(surface, gold, (int(bx1 + side * 5), int(by + 5 + flap)), 2)
            if bw > 20:
                pygame.draw.circle(surface, gold, (int(bx2 - side * 5), int(by + 3 + flap)), 2)
    
    # 木马躯干 - 木制拼装
    body_pts = [(cx - 14, cy - 12), (cx + 14, cy - 12), (cx + 18, cy + 22), (cx, y + h + 3), (cx - 18, cy + 22)]
    pygame.draw.polygon(surface, armor, body_pts)
    # 木纹细节
    for i in range(4):
        pygame.draw.line(surface, wood_grain, (cx - 10 + i * 7, cy - 8), (cx - 8 + i * 7, cy + 18), 1)
    # 腹部装甲板
    pygame.draw.polygon(surface, armor_dark, [(cx - 10, cy + 5), (cx + 10, cy + 5), (cx + 8, cy + 20), (cx - 8, cy + 20)])
    # 金属边框
    pygame.draw.polygon(surface, gold, body_pts, 2)
    # 铆钉装饰
    for i in range(3):
        pygame.draw.circle(surface, gold, (cx - 10, cy - 5 + i * 12), 2)
        pygame.draw.circle(surface, gold, (cx + 10, cy - 5 + i * 12), 2)
    
    # 战马头部 - 精细雕刻
    head_y = y + 3
    # 马头轮廓
    pygame.draw.polygon(surface, armor, [
        (cx - 10, head_y + 22), (cx - 12, head_y + 8), (cx - 8, head_y),
        (cx, head_y - 5), (cx + 8, head_y), (cx + 12, head_y + 8), (cx + 10, head_y + 22)])
    # 马脸中线
    pygame.draw.line(surface, wood_grain, (cx, head_y - 3), (cx, head_y + 18), 1)
    # 鬃毛 - 火焰状
    for i in range(7):
        mx = cx - 4 + i * 1.3
        mh = 10 + 5 * math.sin(t * 5 + i * 0.8)
        mw = 2 * math.sin(t * 3 + i)
        pygame.draw.line(surface, flame, (int(mx), head_y - 2), (int(mx + mw), int(head_y - 2 - mh)), 2)
        pygame.draw.line(surface, core, (int(mx), head_y - 2), (int(mx + mw * 0.5), int(head_y - 2 - mh * 0.7)), 1)
    # 眼睛 - 燃烧
    for side in [-1, 1]:
        ex = cx + side * 6
        pygame.draw.ellipse(surface, (0, 0, 0), (ex - 4, head_y + 8, 8, 6))
        glow = 3 + int(2 * math.sin(t * 4))
        pygame.draw.circle(surface, flame, (ex, head_y + 11), glow)
        pygame.draw.circle(surface, core, (ex, head_y + 11), max(1, glow - 2))
    # 鼻孔喷火
    breath = abs(math.sin(t * 3))
    if breath > 0.4:
        for side in [-1, 1]:
            bx = cx + side * 3
            bl = 8 * breath
            pygame.draw.polygon(surface, (*flame, int(200 * breath)), [
                (bx - 2, head_y + 18), (bx, int(head_y + 18 + bl)), (bx + 2, head_y + 18)])
    # 马耳
    for side in [-1, 1]:
        pygame.draw.polygon(surface, armor, [
            (cx + side * 9, head_y + 3), (cx + side * 12, head_y - 3), (cx + side * 10, head_y + 8)])
    
    # 战车轮浮游炮 - 精细轮辐
    for i in range(4):
        angle = t * 2 + i * math.pi / 2
        wx = cx + math.cos(angle) * 48
        wy = cy + math.sin(angle) * 28
        # 外轮圈
        pygame.draw.circle(surface, gold, (int(wx), int(wy)), 12, 2)
        pygame.draw.circle(surface, armor, (int(wx), int(wy)), 10, 2)
        # 轮辐 - 旋转
        for j in range(8):
            sa = t * 5 + j * math.pi / 4
            pygame.draw.line(surface, gold, (int(wx), int(wy)),
                (int(wx + math.cos(sa) * 9), int(wy + math.sin(sa) * 9)), 1)
        # 轮毂 - 火焰核心
        pygame.draw.circle(surface, armor, (int(wx), int(wy)), 5)
        pygame.draw.circle(surface, flame, (int(wx), int(wy)), 3)
        pygame.draw.circle(surface, core, (int(wx), int(wy)), 1)
    
    # 烟尘尾迹 - 战车扬尘
    for i in range(6):
        dx = cx + (i - 2.5) * 5 + 5 * math.sin(t * 6 + i)
        phase = (t * 35 + i * 10) % 30
        dy = y + h + 3 + phase
        dr = max(2, 7 - int(phase / 5))
        alpha = max(0, 150 - int(phase * 5))
        pygame.draw.circle(surface, (*trail, alpha), (int(dx), int(dy)), dr)


# ==================== 刺身龙王 ====================
def draw_sashimi_dragon(surface, x, y, w, h, frame, style):
    """鱼鳍翅膀，寿司卷躯干，筷子浮游"""
    theme = get_yharon_theme(style)
    armor, flame, core, gold, trail = theme["armor"], theme["flame"], theme["core"], theme["gold"], theme["trail"]
    armor_light = tuple(min(255, c + 50) for c in armor)
    t = frame * 0.06
    cx, cy = x + w // 2, y + h // 2
    
    # 三文鱼鳍翅膀 - 半透明+脂肪纹
    for side in [-1, 1]:
        flap = 8 * math.sin(t * 3 + side)
        # 主鳍轮廓
        fin_pts = [
            (cx + side * 8, cy - 18), (cx + side * 25, cy - 35 + flap),
            (cx + side * 48, cy - 30 + flap * 0.8), (cx + side * 58, cy - 8 + flap * 0.5),
            (cx + side * 52, cy + 15), (cx + side * 35, cy + 25),
            (cx + side * 10, cy + 12)]
        pygame.draw.polygon(surface, (*armor, 200), fin_pts)
        # 鳍边缘高光
        pygame.draw.lines(surface, armor_light, False, fin_pts[:4], 2)
        # 鳍纹 - 放射状
        for i in range(5):
            fx1 = cx + side * (12 + i * 8)
            fy1 = cy - 10 + i * 4
            fx2 = cx + side * (25 + i * 6)
            fy2 = cy - 25 + i * 8 + flap * 0.6
            pygame.draw.line(surface, (*armor_light, 150), (int(fx1), int(fy1)), (int(fx2), int(fy2)), 1)
        # 脂肪光泽斑块
        for i in range(3):
            fx = cx + side * (22 + i * 12)
            fy = cy - 18 + i * 10 + flap * 0.4
            pygame.draw.ellipse(surface, (*flame, 120), (int(fx) - 6, int(fy) - 3, 12, 6))
    
    # 寿司卷躯干 - 多层结构
    # 海苔外层
    pygame.draw.ellipse(surface, (15, 35, 25), (cx - 20, cy - 14, 40, 55))
    pygame.draw.ellipse(surface, (25, 50, 35), (cx - 20, cy - 14, 40, 55), 2)
    # 米饭层
    pygame.draw.ellipse(surface, trail, (cx - 16, cy - 10, 32, 47))
    # 米粒细节
    for i in range(8):
        rx = cx - 10 + (i % 4) * 6 + 2 * math.sin(i)
        ry = cy - 5 + (i // 4) * 35
        pygame.draw.ellipse(surface, (255, 255, 250), (int(rx), int(ry), 4, 2))
    # 三文鱼芯
    pygame.draw.ellipse(surface, armor, (cx - 12, cy - 5, 24, 38))
    # 脂肪纹路 - 白色条纹
    for i in range(4):
        pygame.draw.line(surface, flame, (cx - 8 + i * 5, cy), (cx - 6 + i * 5, cy + 25), 3)
        pygame.draw.line(surface, armor_light, (cx - 7 + i * 5, cy + 2), (cx - 5 + i * 5, cy + 22), 1)
    
    # 鱼头 - 可爱圆润
    head_y = y + 5
    pygame.draw.ellipse(surface, armor, (cx - 14, head_y - 3, 28, 24))
    # 腮部光泽
    for side in [-1, 1]:
        pygame.draw.ellipse(surface, (*armor_light, 100), (cx + side * 6 - 4, head_y + 10, 8, 6))
    # 眼睛 - 大而圆
    for side in [-1, 1]:
        ex = cx + side * 7
        pygame.draw.circle(surface, (0, 0, 0), (ex, head_y + 8), 5)
        pygame.draw.circle(surface, (255, 255, 255), (ex - 1, head_y + 6), 2)
        pygame.draw.circle(surface, (255, 255, 255), (ex + 1, head_y + 9), 1)
    # 嘴巴
    pygame.draw.arc(surface, gold, (cx - 4, head_y + 15, 8, 5), math.pi, 2 * math.pi, 2)
    
    # 筷子浮游炮 - 双筷夹持
    for i in range(2):
        ca = t * 1.5 + i * math.pi
        csx = cx + 52 * math.cos(ca)
        csy = cy + 28 * math.sin(ca)
        # 筷子对 - 木纹
        for j in range(2):
            offset = 4 * (j - 0.5)
            ea = ca - math.pi / 2
            ex = csx + math.cos(ea) * 28
            ey = csy + math.sin(ea) * 28
            # 筷子主体
            pygame.draw.line(surface, (160, 110, 60), 
                (int(csx + offset * math.cos(ca + math.pi/2)), int(csy + offset * math.sin(ca + math.pi/2))),
                (int(ex + offset * math.cos(ca + math.pi/2)), int(ey + offset * math.sin(ca + math.pi/2))), 3)
            # 筷头装饰
            pygame.draw.circle(surface, gold, (int(csx + offset * math.cos(ca + math.pi/2)), 
                int(csy + offset * math.sin(ca + math.pi/2))), 2)
    
    # 配菜浮游
    # 芥末
    wasabi_pulse = 6 + 3 * math.sin(t * 3)
    pygame.draw.circle(surface, (100, 180, 60), (cx + 25, y + 2), int(wasabi_pulse))
    pygame.draw.circle(surface, (140, 220, 100), (cx + 25, y), int(wasabi_pulse * 0.6))
    # 姜片
    pygame.draw.ellipse(surface, (255, 200, 210), (cx - 30, y + 3, 14, 8))
    pygame.draw.ellipse(surface, (255, 180, 190), (cx - 28, y + 5, 10, 4))
    # 酱油碟
    pygame.draw.ellipse(surface, (60, 40, 30), (cx - 8, y - 3, 16, 8))
    soy_wave = 2 * math.sin(t * 4)
    pygame.draw.ellipse(surface, (40, 25, 15), (cx - 6, y - 1 + soy_wave, 12, 4))
    
    # 酱油尾迹
    for i in range(4):
        sx = cx + (i - 1.5) * 6
        sl = 18 + 10 * math.sin(t * 5 + i)
        pygame.draw.polygon(surface, (50, 30, 20), [
            (sx - 3, y + h), (sx, int(y + h + sl)), (sx + 3, y + h)])
        pygame.draw.polygon(surface, (70, 45, 30), [
            (sx - 1, y + h), (sx, int(y + h + sl * 0.7)), (sx + 1, y + h)])


# ==================== 糖龙暴君 ====================
def draw_candy_dragon(surface, x, y, w, h, frame, style):
    """融化糖翼，软糖熊躯干，棒棒糖浮游"""
    theme = get_yharon_theme(style)
    armor, flame, core, gold, trail = theme["armor"], theme["flame"], theme["core"], theme["gold"], theme["trail"]
    armor_light = tuple(min(255, c + 60) for c in armor)
    t = frame * 0.06
    cx, cy = x + w // 2, y + h // 2
    
    # 融化糖浆翅膀 - 不规则流动形状
    for side in [-1, 1]:
        dp = t * 2 + side
        # 主翼轮廓 - 波动边缘
        pts = []
        base_pts = [
            (cx + side * 10, cy - 12), (cx + side * 25, cy - 30), (cx + side * 42, cy - 25),
            (cx + side * 52, cy - 8), (cx + side * 48, cy + 12), (cx + side * 38, cy + 25),
            (cx + side * 20, cy + 22), (cx + side * 12, cy + 15)]
        for i, (px, py) in enumerate(base_pts):
            wave = 4 * math.sin(dp + i * 0.8)
            pts.append((px + wave * 0.3, py + wave))
        pygame.draw.polygon(surface, (*armor, 210), pts)
        # 糖衣光泽层
        pygame.draw.polygon(surface, (*armor_light, 80), pts)
        # 气泡
        for i in range(4):
            bx = cx + side * (18 + i * 10) + 3 * math.sin(t * 3 + i)
            by = cy - 15 + i * 8 + 2 * math.cos(t * 4 + i)
            br = 3 + int(2 * math.sin(t * 5 + i))
            pygame.draw.circle(surface, (*armor_light, 150), (int(bx), int(by)), br)
            pygame.draw.circle(surface, (255, 255, 255, 100), (int(bx) - 1, int(by) - 1), max(1, br - 1))
        # 糖浆滴落
        for i in range(4):
            dx = cx + side * (22 + i * 8)
            dl = 10 + 8 * math.sin(t * 4 + i + side)
            dy = cy + 15 + i * 3
            pygame.draw.polygon(surface, (*trail, 200), [
                (dx - 3, dy), (dx, int(dy + dl)), (dx + 3, dy)])
            pygame.draw.polygon(surface, (*armor_light, 150), [
                (dx - 1, dy), (dx, int(dy + dl * 0.7)), (dx + 1, dy)])
    
    # 软糖熊躯干 - QQ弹弹
    # 身体主体
    pygame.draw.ellipse(surface, armor, (cx - 18, cy - 10, 36, 48))
    # 半透明糖衣
    pygame.draw.ellipse(surface, (*armor_light, 100), (cx - 14, cy - 6, 28, 38))
    # 高光
    pygame.draw.ellipse(surface, (*flame, 80), (cx - 8, cy - 4, 10, 6))
    # 肚子 - 更亮
    pygame.draw.ellipse(surface, (*trail, 180), (cx - 10, cy + 8, 20, 16))
    pygame.draw.ellipse(surface, (255, 255, 255, 80), (cx - 6, cy + 10, 8, 6))
    
    # 软糖熊头 - 圆润可爱
    head_y = y + 3
    pygame.draw.ellipse(surface, armor, (cx - 14, head_y - 2, 28, 24))
    # 头部高光
    pygame.draw.ellipse(surface, (*armor_light, 120), (cx - 8, head_y, 12, 8))
    # 耳朵
    for side in [-1, 1]:
        pygame.draw.circle(surface, armor, (cx + side * 11, head_y + 2), 7)
        pygame.draw.circle(surface, trail, (cx + side * 11, head_y + 2), 4)
        pygame.draw.circle(surface, (*armor_light, 100), (cx + side * 11 - 1, head_y), 2)
    # 眼睛 - 糖豆眼
    for side in [-1, 1]:
        ex = cx + side * 5
        pygame.draw.ellipse(surface, (20, 20, 20), (ex - 3, head_y + 8, 6, 8))
        pygame.draw.circle(surface, (255, 255, 255), (ex - 1, head_y + 10), 2)
        pygame.draw.circle(surface, (255, 255, 255), (ex + 1, head_y + 13), 1)
    # 鼻子
    pygame.draw.ellipse(surface, gold, (cx - 3, head_y + 16, 6, 5))
    pygame.draw.ellipse(surface, (*armor_light, 150), (cx - 2, head_y + 16, 3, 2))
    # 嘴巴
    pygame.draw.arc(surface, (180, 80, 100), (cx - 4, head_y + 19, 8, 4), math.pi, 2 * math.pi, 1)
    
    # 棒棒糖浮游炮 - 彩色螺旋
    candy_colors = [(255, 100, 150), (100, 255, 150), (150, 100, 255), (255, 220, 100)]
    for i in range(4):
        la = t * 2.2 + i * math.pi / 2
        lx = cx + math.cos(la) * 48
        ly = cy + math.sin(la) * 30
        # 棒子
        pygame.draw.line(surface, (220, 200, 170), (int(lx), int(ly + 3)), (int(lx), int(ly + 16)), 3)
        pygame.draw.line(surface, (240, 225, 200), (int(lx) - 1, int(ly + 3)), (int(lx) - 1, int(ly + 14)), 1)
        # 糖球
        pygame.draw.circle(surface, candy_colors[i], (int(lx), int(ly)), 9)
        # 螺旋纹
        for j in range(3):
            spiral_a = t * 4 + i + j * math.pi * 2 / 3
            pygame.draw.arc(surface, (255, 255, 255), 
                (int(lx) - 7, int(ly) - 7, 14, 14), spiral_a, spiral_a + 0.8, 2)
        # 高光
        pygame.draw.circle(surface, (255, 255, 255, 180), (int(lx) - 3, int(ly) - 3), 3)
    
    # 糖屑粒子
    for i in range(6):
        px = cx + 35 * math.sin(t * 2.5 + i * 1.1)
        py = cy + 20 * math.cos(t * 2 + i * 0.9)
        pc = candy_colors[i % 4]
        pygame.draw.circle(surface, pc, (int(px), int(py)), 2)
    
    # 糖浆尾迹
    for i in range(5):
        sx = cx + (i - 2) * 5
        sl = 20 + 12 * math.sin(t * 3.5 + i)
        pygame.draw.polygon(surface, (*trail, 200), [
            (sx - 4, y + h), (sx, int(y + h + sl)), (sx + 4, y + h)])
        pygame.draw.polygon(surface, (*armor_light, 120), [
            (sx - 2, y + h), (sx, int(y + h + sl * 0.7)), (sx + 2, y + h)])


# ==================== 披萨龙王 ====================
def draw_pizza_dragon(surface, x, y, w, h, frame, style):
    """披萨片翅膀，芝士拉丝躯干，辣椒浮游"""
    theme = get_yharon_theme(style)
    armor, flame, core, gold, trail = theme["armor"], theme["flame"], theme["core"], theme["gold"], theme["trail"]
    armor_dark = tuple(max(0, c - 30) for c in armor)
    t = frame * 0.06
    cx, cy = x + w // 2, y + h // 2
    
    # 披萨片翅膀 - 三角形配料丰富
    for side in [-1, 1]:
        flap = 4 * math.sin(t * 2.5 + side)
        # 饼底
        pizza_pts = [(cx + side * 8, cy + 5), (cx + side * 58, cy - 28 + flap), (cx + side * 52, cy + 22 + flap)]
        pygame.draw.polygon(surface, trail, pizza_pts)
        # 焦边
        pygame.draw.polygon(surface, armor_dark, pizza_pts, 3)
        # 芝士层
        cheese_pts = [(cx + side * 10, cy + 3), (cx + side * 52, cy - 22 + flap), (cx + side * 48, cy + 18 + flap)]
        pygame.draw.polygon(surface, armor, cheese_pts)
        # 番茄酱底
        pygame.draw.polygon(surface, (*flame, 150), [
            (cx + side * 12, cy + 1), (cx + side * 48, cy - 18 + flap), (cx + side * 45, cy + 15 + flap)])
        # 配料
        # 意大利辣香肠
        for i in range(4):
            px = cx + side * (18 + i * 10)
            py = cy - 8 + i * 6 + flap * 0.5
            pygame.draw.circle(surface, (180, 50, 40), (int(px), int(py)), 5)
            pygame.draw.circle(surface, (200, 70, 60), (int(px), int(py)), 5, 1)
            # 油光点
            pygame.draw.circle(surface, (220, 100, 80), (int(px) - 1, int(py) - 1), 2)
        # 青椒
        for i in range(2):
            gx = cx + side * (25 + i * 15)
            gy = cy + 5 + i * 5 + flap * 0.3
            pygame.draw.arc(surface, (50, 150, 50), (int(gx) - 4, int(gy) - 6, 8, 12), 0, math.pi, 2)
        # 蘑菇
        mx = cx + side * 35
        my = cy - 15 + flap * 0.6
        pygame.draw.ellipse(surface, (240, 230, 210), (int(mx) - 4, int(my), 8, 5))
        pygame.draw.arc(surface, (220, 210, 190), (int(mx) - 5, int(my) - 4, 10, 8), 0, math.pi, 2)
    
    # 躯干 - 芝士拉丝效果
    # 饼底
    pygame.draw.polygon(surface, trail, [(cx - 16, cy - 16), (cx + 16, cy - 16), (cx + 14, cy + 28), (cx, y + h + 2), (cx - 14, cy + 28)])
    # 芝士层
    pygame.draw.polygon(surface, armor, [(cx - 14, cy - 14), (cx + 14, cy - 14), (cx + 12, cy + 24), (cx, y + h - 2), (cx - 12, cy + 24)])
    # 芝士拉丝 - 动态
    for i in range(6):
        sx = cx - 10 + i * 4
        sw = 4 * math.sin(t * 5 + i)
        sl = 12 + 6 * abs(math.sin(t * 3 + i * 0.7))
        # 拉丝主体
        pts = [(sx - 1, cy - 5), (int(sx + sw), int(cy + sl)), (sx + 1, cy - 5)]
        pygame.draw.polygon(surface, core, pts)
        # 拉丝高光
        pygame.draw.line(surface, (255, 240, 200), (sx, cy - 3), (int(sx + sw * 0.5), int(cy + sl * 0.6)), 1)
    # 焦边
    pygame.draw.polygon(surface, armor_dark, [(cx - 16, cy - 16), (cx + 16, cy - 16), (cx + 14, cy + 28), (cx, y + h + 2), (cx - 14, cy + 28)], 2)
    
    # 头部 - 披萨角
    head_y = y + 2
    pygame.draw.polygon(surface, trail, [(cx - 12, head_y + 20), (cx, head_y - 5), (cx + 12, head_y + 20)])
    pygame.draw.polygon(surface, armor, [(cx - 10, head_y + 18), (cx, head_y - 2), (cx + 10, head_y + 18)])
    pygame.draw.polygon(surface, armor_dark, [(cx - 12, head_y + 20), (cx, head_y - 5), (cx + 12, head_y + 20)], 2)
    # 眼睛 - 橄榄
    for side in [-1, 1]:
        pygame.draw.ellipse(surface, (30, 60, 30), (cx + side * 4 - 3, head_y + 8, 6, 8))
        pygame.draw.circle(surface, (180, 50, 40), (cx + side * 4, head_y + 12), 2)
    # 顶部配料
    pygame.draw.circle(surface, flame, (cx, head_y + 3), 4)
    
    # 辣椒浮游炮 - 红绿辣椒
    pepper_colors = [(200, 30, 30), (30, 160, 30), (200, 30, 30), (220, 180, 30)]
    for i in range(4):
        pa = t * 2.2 + i * math.pi / 2
        px = cx + math.cos(pa) * 48
        py = cy + math.sin(pa) * 28
        pc = pepper_colors[i]
        # 辣椒身体
        pygame.draw.ellipse(surface, pc, (int(px) - 8, int(py) - 4, 16, 8))
        # 辣椒尖
        pygame.draw.polygon(surface, pc, [
            (int(px) + 6, int(py)), (int(px) + 14, int(py) - 1), (int(px) + 6, int(py) + 2)])
        # 辣椒蒂
        pygame.draw.polygon(surface, (40, 120, 40), [
            (int(px) - 8, int(py) - 1), (int(px) - 12, int(py) - 3), (int(px) - 8, int(py) + 1)])
        # 高光
        pygame.draw.ellipse(surface, (*[min(255, c + 60) for c in pc], 150), (int(px) - 4, int(py) - 3, 6, 3))
    
    # 热气尾迹
    for i in range(4):
        phase = (t * 45 + i * 12) % 30
        sx = cx - 8 + i * 5 + 4 * math.sin(t * 3 + i)
        sy = y + h + 3 + phase
        sr = max(2, 8 - int(phase / 4))
        alpha = max(0, 120 - int(phase * 4))
        steam = pygame.Surface((sr * 2 + 4, sr * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(steam, (255, 255, 255, alpha), (sr + 2, sr + 2), sr)
        surface.blit(steam, (int(sx) - sr - 2, int(sy) - sr - 2))


# ==================== 外科龙医 ====================
def draw_surgeon_dragon(surface, x, y, w, h, frame, style):
    """手术刀翅膀，绷带躯干，注射器浮游"""
    theme = get_yharon_theme(style)
    armor, flame, core, gold, trail = theme["armor"], theme["flame"], theme["core"], theme["gold"], theme["trail"]
    armor_dark = tuple(max(0, c - 25) for c in armor)
    t = frame * 0.06
    cx, cy = x + w // 2, y + h // 2
    
    # 手术刀翅膀 - 锋利金属质感
    for side in [-1, 1]:
        flap = 5 * math.sin(t * 3 + side)
        # 刀片 - 渐变金属
        blade_pts = [
            (cx + side * 10, cy - 8), (cx + side * 20, cy - 18 + flap),
            (cx + side * 58, cy - 12 + flap), (cx + side * 62, cy + 2 + flap),
            (cx + side * 55, cy + 8 + flap), (cx + side * 12, cy + 8)]
        pygame.draw.polygon(surface, armor, blade_pts)
        # 刀刃高光
        pygame.draw.line(surface, (255, 255, 255), 
            (cx + side * 20, int(cy - 16 + flap)), (cx + side * 60, int(cy - 8 + flap)), 2)
        pygame.draw.line(surface, armor_dark, 
            (cx + side * 12, cy + 6), (cx + side * 55, int(cy + 6 + flap)), 1)
        # 刀柄 - 橡胶握把
        pygame.draw.rect(surface, gold, (cx + side * 6 - 4, cy - 10, 8, 20))
        pygame.draw.rect(surface, armor_dark, (cx + side * 6 - 4, cy - 10, 8, 20), 1)
        # 握把纹路
        for i in range(4):
            gy = cy - 7 + i * 5
            pygame.draw.line(surface, armor_dark, (cx + side * 6 - 3, gy), (cx + side * 6 + 3, gy), 1)
        # 血迹效果
        if side > 0:
            for i in range(3):
                bx = cx + 30 + i * 12
                by = cy - 5 + i * 3 + flap * 0.5
                pygame.draw.circle(surface, (*flame, 150), (int(bx), int(by)), 3 - i)
    
    # 绷带躯干 - 层层缠绕
    # 底层身体
    pygame.draw.ellipse(surface, trail, (cx - 16, cy - 12, 32, 50))
    # 绷带缠绕
    for i in range(6):
        by = cy - 8 + i * 8
        bw = 14 - abs(i - 2.5) * 2
        # 绷带条
        pygame.draw.polygon(surface, armor, [
            (cx - int(bw), by), (cx + int(bw), by + 3),
            (cx + int(bw), by + 6), (cx - int(bw), by + 3)])
        # 绷带阴影
        pygame.draw.line(surface, armor_dark, (cx - int(bw), by + 3), (cx + int(bw), by + 6), 1)
    # 交叉绷带
    pygame.draw.line(surface, armor, (cx - 10, cy - 5), (cx + 10, cy + 15), 4)
    pygame.draw.line(surface, armor, (cx + 10, cy - 5), (cx - 10, cy + 15), 4)
    # 固定夹
    pygame.draw.rect(surface, gold, (cx - 2, cy + 3, 4, 6))
    
    # 头部 - 外科口罩
    head_y = y + 2
    # 头部轮廓
    pygame.draw.ellipse(surface, trail, (cx - 12, head_y - 2, 24, 22))
    # 外科帽
    pygame.draw.arc(surface, (100, 180, 160), (cx - 14, head_y - 8, 28, 20), 0, math.pi, 3)
    pygame.draw.ellipse(surface, (100, 180, 160), (cx - 12, head_y - 4, 24, 10))
    # 口罩
    pygame.draw.rect(surface, (130, 200, 220), (cx - 10, head_y + 10, 20, 10))
    pygame.draw.rect(surface, (100, 170, 200), (cx - 10, head_y + 10, 20, 10), 1)
    # 口罩褶皱
    for i in range(3):
        pygame.draw.line(surface, (100, 170, 200), (cx - 8, head_y + 12 + i * 3), (cx + 8, head_y + 12 + i * 3), 1)
    # 眼睛 - 专注
    for side in [-1, 1]:
        ex = cx + side * 5
        pygame.draw.ellipse(surface, (255, 255, 255), (ex - 4, head_y + 3, 8, 6))
        pygame.draw.circle(surface, flame, (ex, head_y + 6), 3)
        pygame.draw.circle(surface, (0, 0, 0), (ex, head_y + 6), 2)
        # 眼神高光
        pygame.draw.circle(surface, (255, 255, 255), (ex - 1, head_y + 5), 1)
    # 额镜
    pygame.draw.circle(surface, gold, (cx, head_y), 5)
    pygame.draw.circle(surface, (255, 255, 255), (cx, head_y), 3)
    
    # 注射器浮游炮 - 彩色药剂
    syringe_colors = [(255, 100, 100), (100, 200, 255), (150, 255, 150), (255, 200, 100)]
    for i in range(4):
        sa = t * 2.2 + i * math.pi / 2
        sx = cx + math.cos(sa) * 46
        sy = cy + math.sin(sa) * 28
        ea = sa + math.pi / 2
        # 针筒
        ex = sx + math.cos(ea) * 22
        ey = sy + math.sin(ea) * 22
        pygame.draw.line(surface, armor, (int(sx), int(sy)), (int(ex), int(ey)), 4)
        pygame.draw.line(surface, armor_dark, (int(sx), int(sy)), (int(ex), int(ey)), 4)
        # 药剂
        mx = sx + math.cos(ea) * 8
        my = sy + math.sin(ea) * 8
        pygame.draw.line(surface, syringe_colors[i], (int(sx), int(sy)), (int(mx), int(my)), 3)
        # 针头
        nx = ex + math.cos(ea) * 6
        ny = ey + math.sin(ea) * 6
        pygame.draw.line(surface, gold, (int(ex), int(ey)), (int(nx), int(ny)), 1)
        # 推杆
        px = sx - math.cos(ea) * 5
        py = sy - math.sin(ea) * 5
        pygame.draw.circle(surface, armor, (int(px), int(py)), 3)
    
    # 心电图尾迹 - 动态波形
    wave_pts = []
    wave_offset = int(t * 20) % 5
    for i in range(20):
        wx = cx - 15 + i * 1.5
        wo = 0
        idx = (i + wave_offset) % 10
        if idx == 3: wo = -10
        elif idx == 4: wo = 8
        elif idx == 5: wo = -4
        elif idx == 6: wo = 2
        wave_pts.append((int(wx), int(y + h + 12 + wo)))
    if len(wave_pts) > 1:
        pygame.draw.lines(surface, (0, 255, 100), False, wave_pts, 2)
        # 光点
        glow_idx = int(t * 8) % len(wave_pts)
        if glow_idx < len(wave_pts):
            pygame.draw.circle(surface, (150, 255, 150), wave_pts[glow_idx], 3)


# ==================== 老虎机龙 ====================
def draw_jackpot_dragon(surface, x, y, w, h, frame, style):
    """霓虹翅膀，老虎机躯干，金币浮游"""
    theme = get_yharon_theme(style)
    armor, flame, core, gold, trail = theme["armor"], theme["flame"], theme["core"], theme["gold"], theme["trail"]
    armor_dark = tuple(max(0, c - 40) for c in armor)
    t = frame * 0.06
    cx, cy = x + w // 2, y + h // 2
    
    # 霓虹灯管翅膀 - 多层发光
    neon_colors = [(255, 50, 120), (255, 220, 50), (50, 255, 150), (100, 150, 255)]
    for side in [-1, 1]:
        for i, nc in enumerate(neon_colors):
            flap = 4 * math.sin(t * 3 + i * 0.5 + side)
            pulse = 0.6 + 0.4 * math.sin(t * 6 + i * 1.5)
            alpha = int(180 * pulse)
            # 霓虹管轮廓
            pts = [
                (cx + side * (10 + i * 2), cy - 10 + i * 4),
                (cx + side * (48 - i * 8), cy - 28 + i * 6 + flap),
                (cx + side * (45 - i * 8), cy + 18 - i * 4 + flap)]
            pygame.draw.polygon(surface, (*nc, alpha), pts)
            # 发光边缘
            pygame.draw.polygon(surface, (*nc, int(alpha * 0.5)), pts, 2)
        # 霓虹闪烁点
        for j in range(3):
            fx = cx + side * (20 + j * 12)
            fy = cy - 15 + j * 10 + 3 * math.sin(t * 4)
            if math.sin(t * 8 + j + side) > 0.3:
                pygame.draw.circle(surface, (255, 255, 200), (int(fx), int(fy)), 3)
    
    # 老虎机躯干 - 精致机械
    # 机身外壳
    pygame.draw.rect(surface, armor, (cx - 18, cy - 14, 36, 50))
    pygame.draw.rect(surface, armor_dark, (cx - 18, cy - 14, 36, 50), 2)
    # 金属边框
    pygame.draw.rect(surface, gold, (cx - 20, cy - 16, 40, 54), 3)
    # 装饰线条
    pygame.draw.line(surface, gold, (cx - 16, cy - 10), (cx + 16, cy - 10), 1)
    pygame.draw.line(surface, gold, (cx - 16, cy + 32), (cx + 16, cy + 32), 1)
    # 转轴窗口
    for i in range(3):
        rx = cx - 12 + i * 12
        # 窗口背景
        pygame.draw.rect(surface, (20, 20, 30), (rx - 5, cy - 2, 10, 18))
        pygame.draw.rect(surface, gold, (rx - 5, cy - 2, 10, 18), 1)
        # 转动符号
        symbol_phase = int((t * 10 + i * 2.5) % 4)
        sym_colors = [(255, 50, 50), (50, 255, 50), (255, 215, 0), (150, 50, 255)]
        sym_y = cy + 6 + 2 * math.sin(t * 15 + i)
        pygame.draw.circle(surface, sym_colors[symbol_phase], (rx, int(sym_y)), 4)
        # 符号细节
        if symbol_phase == 0:  # 樱桃
            pygame.draw.circle(surface, (200, 30, 30), (rx - 2, int(sym_y) + 1), 2)
        elif symbol_phase == 2:  # 金条
            pygame.draw.rect(surface, (255, 200, 50), (rx - 3, int(sym_y) - 2, 6, 4))
    # 投币口
    pygame.draw.ellipse(surface, (30, 30, 40), (cx + 10, cy - 10, 6, 3))
    
    # 头部 - 拉杆造型
    head_y = y + 2
    pygame.draw.rect(surface, armor, (cx - 14, head_y, 28, 18))
    pygame.draw.rect(surface, gold, (cx - 14, head_y, 28, 18), 2)
    # 顶部装饰
    pygame.draw.polygon(surface, gold, [(cx - 10, head_y), (cx, head_y - 8), (cx + 10, head_y)])
    pygame.draw.polygon(surface, flame, [(cx - 6, head_y), (cx, head_y - 5), (cx + 6, head_y)])
    # 眼睛 - LED灯
    for side in [-1, 1]:
        ex = cx + side * 6
        glow = 0.5 + 0.5 * math.sin(t * 5 + side)
        pygame.draw.circle(surface, (*flame, int(255 * glow)), (ex, head_y + 10), 4)
        pygame.draw.circle(surface, core, (ex, head_y + 10), 2)
    # 777显示
    if math.sin(t * 2) > 0:
        for i in range(3):
            pygame.draw.circle(surface, gold, (cx - 4 + i * 4, head_y + 5), 2)
    
    # 金币浮游炮 - 旋转金币
    for i in range(6):
        ca = t * 2.8 + i * math.pi / 3
        ccx = cx + math.cos(ca) * 48
        ccy = cy + math.sin(ca) * 30
        # 金币 - 3D效果
        coin_rot = t * 5 + i
        coin_w = int(8 * abs(math.cos(coin_rot)))
        pygame.draw.ellipse(surface, gold, (int(ccx) - coin_w, int(ccy) - 8, coin_w * 2, 16))
        pygame.draw.ellipse(surface, flame, (int(ccx) - max(1, coin_w - 2), int(ccy) - 6, max(2, (coin_w - 2) * 2), 12))
        # 金币符号
        if coin_w > 4:
            pygame.draw.circle(surface, gold, (int(ccx), int(ccy)), 3, 1)
    
    # 金币喷涌尾迹
    for i in range(8):
        ct = (t * 4 + i * 0.4) % 2.5
        ccx = cx - 15 + i * 4 + 8 * math.sin(t * 6 + i)
        ccy = y + h + ct * 25
        cr = max(1, 5 - ct * 2)
        alpha = max(0, 200 - int(ct * 80))
        pygame.draw.circle(surface, (*gold, alpha), (int(ccx), int(ccy)), int(cr))


# ==================== 办公龙 ====================
def draw_office_dragon(surface, x, y, w, h, frame, style):
    """便利贴翅膀，文件夹躯干，回形针浮游"""
    theme = get_yharon_theme(style)
    armor, flame, core, gold, trail = theme["armor"], theme["flame"], theme["core"], theme["gold"], theme["trail"]
    armor_dark = tuple(max(0, c - 30) for c in armor)
    t = frame * 0.06
    cx, cy = x + w // 2, y + h // 2
    
    # 便利贴翅膀 - 彩色层叠
    note_colors = [(255, 255, 120), (120, 255, 180), (255, 180, 200), (180, 220, 255), (255, 200, 120)]
    for side in [-1, 1]:
        for i in range(4):
            nx = cx + side * (14 + i * 13)
            ny = cy - 12 + i * 9
            flap = 4 * math.sin(t * 2.5 + i * 0.7 + side)
            # 便利贴主体 - 略微翘起
            note_pts = [
                (int(nx) - 10, int(ny + flap) - 10),
                (int(nx) + 10, int(ny + flap) - 10),
                (int(nx) + 10, int(ny + flap) + 10),
                (int(nx) - 8, int(ny + flap) + 10),
                (int(nx) - 10, int(ny + flap) + 8)]
            pygame.draw.polygon(surface, note_colors[i], note_pts)
            # 便利贴阴影
            pygame.draw.polygon(surface, (*[max(0, c - 40) for c in note_colors[i]], 100), note_pts, 1)
            # 翘角
            pygame.draw.polygon(surface, (*[min(255, c + 30) for c in note_colors[i]], 200), [
                (int(nx) - 10, int(ny + flap) + 8),
                (int(nx) - 8, int(ny + flap) + 10),
                (int(nx) - 6, int(ny + flap) + 6)])
            # 文字线条
            for j in range(3):
                ly = ny + flap - 5 + j * 5
                lw = 12 - j * 2
                pygame.draw.line(surface, (100, 100, 100), 
                    (int(nx) - int(lw/2), int(ly)), (int(nx) + int(lw/2), int(ly)), 1)
    
    # 文件夹躯干 - 立体感
    # 文件夹主体
    pygame.draw.rect(surface, armor, (cx - 16, cy - 10, 32, 46))
    # 文件夹脊
    pygame.draw.rect(surface, armor_dark, (cx - 18, cy - 10, 4, 46))
    pygame.draw.rect(surface, armor_dark, (cx + 14, cy - 10, 4, 46))
    # 标签页
    pygame.draw.rect(surface, flame, (cx - 12, cy - 16, 24, 8))
    pygame.draw.rect(surface, gold, (cx - 12, cy - 16, 24, 8), 1)
    # 文件页
    for i in range(3):
        py = cy - 5 + i * 12
        pygame.draw.rect(surface, trail, (cx - 12, py, 24, 10))
        pygame.draw.line(surface, (180, 180, 180), (cx - 10, py + 3), (cx + 8, py + 3), 1)
        pygame.draw.line(surface, (180, 180, 180), (cx - 10, py + 6), (cx + 4, py + 6), 1)
    # 金属环
    for i in range(3):
        ry = cy - 2 + i * 14
        pygame.draw.ellipse(surface, gold, (cx - 18, ry, 6, 8), 2)
    
    # 头部 - 戴眼镜的办公人员
    head_y = y + 2
    # 头部轮廓
    pygame.draw.ellipse(surface, trail, (cx - 12, head_y - 2, 24, 22))
    # 发型
    pygame.draw.arc(surface, armor_dark, (cx - 10, head_y - 5, 20, 12), 0, math.pi, 3)
    # 眼镜框
    for side in [-1, 1]:
        gx = cx + side * 5
        pygame.draw.rect(surface, (40, 40, 40), (gx - 5, head_y + 5, 10, 8), 1)
        # 镜片反光
        pygame.draw.rect(surface, (220, 230, 255, 100), (gx - 4, head_y + 6, 8, 6))
        # 眼睛
        pygame.draw.circle(surface, (0, 0, 0), (gx, head_y + 9), 2)
    # 眼镜腿
    pygame.draw.line(surface, (40, 40, 40), (cx - 10, head_y + 9), (cx + 10, head_y + 9), 1)
    # 嘴巴
    pygame.draw.arc(surface, (180, 120, 120), (cx - 3, head_y + 15, 6, 4), math.pi, 2 * math.pi, 1)
    # 领带
    pygame.draw.polygon(surface, flame, [(cx - 3, head_y + 20), (cx + 3, head_y + 20), (cx + 2, head_y + 28), (cx - 2, head_y + 28)])
    
    # 回形针浮游炮 - 彩色回形针
    clip_colors = [(200, 200, 220), (255, 180, 180), (180, 255, 180), (180, 180, 255)]
    for i in range(4):
        pa = t * 2.2 + i * math.pi / 2
        px = cx + math.cos(pa) * 48
        py = cy + math.sin(pa) * 28
        pc = clip_colors[i]
        # 回形针形状 - 双环
        pygame.draw.arc(surface, pc, (int(px) - 5, int(py) - 8, 10, 16), -math.pi/2, math.pi/2, 2)
        pygame.draw.arc(surface, pc, (int(px) - 3, int(py) - 6, 6, 12), math.pi/2, 3*math.pi/2, 2)
        pygame.draw.line(surface, pc, (int(px), int(py) - 8), (int(px), int(py) - 6), 2)
        pygame.draw.line(surface, pc, (int(px), int(py) + 6), (int(px), int(py) + 8), 2)
    
    # 文具浮游 - 铅笔、橡皮
    pencil_a = t * 1.5
    pencil_x = cx + math.cos(pencil_a + math.pi) * 45
    pencil_y = cy + math.sin(pencil_a + math.pi) * 25
    # 铅笔
    pygame.draw.rect(surface, (255, 220, 100), (int(pencil_x) - 2, int(pencil_y) - 10, 4, 18))
    pygame.draw.polygon(surface, (255, 200, 150), [(int(pencil_x) - 2, int(pencil_y) + 8), 
        (int(pencil_x) + 2, int(pencil_y) + 8), (int(pencil_x), int(pencil_y) + 14)])
    pygame.draw.polygon(surface, (40, 40, 40), [(int(pencil_x) - 1, int(pencil_y) + 12), 
        (int(pencil_x) + 1, int(pencil_y) + 12), (int(pencil_x), int(pencil_y) + 14)])
    # 橡皮
    eraser_x = cx + math.cos(pencil_a) * 45
    eraser_y = cy + math.sin(pencil_a) * 25
    pygame.draw.rect(surface, (255, 180, 200), (int(eraser_x) - 5, int(eraser_y) - 4, 10, 8))
    
    # 纸张尾迹
    for i in range(4):
        phase = (t * 35 + i * 12) % 30
        py = y + h + 3 + phase
        pw = max(2, 10 - int(phase / 4))
        alpha = max(0, 180 - int(phase * 6))
        pygame.draw.rect(surface, (*trail, alpha), (cx - 5 + i * 3, int(py), pw, pw))


# ==================== 雷暴龙 ====================
def draw_storm_dragon(surface, x, y, w, h, frame, style):
    """闪电翅膀，雷云躯干，雨滴浮游"""
    theme = get_yharon_theme(style)
    armor, flame, core, gold, trail = theme["armor"], theme["flame"], theme["core"], theme["gold"], theme["trail"]
    armor_dark = tuple(max(0, c - 40) for c in armor)
    t = frame * 0.06
    cx, cy = x + w // 2, y + h // 2
    
    # 闪电翅膀 - 锯齿状分叉
    for side in [-1, 1]:
        flap = 6 * math.sin(t * 4 + side)
        pulse = 0.7 + 0.3 * math.sin(t * 8)
        # 主闪电
        bolt_pts = [
            (cx + side * 10, cy - 12),
            (cx + side * 28, cy - 32 + flap),
            (cx + side * 22, cy - 18 + flap),
            (cx + side * 45, cy - 25 + flap),
            (cx + side * 38, cy - 8 + flap),
            (cx + side * 55, cy + 5 + flap),
            (cx + side * 42, cy + 8 + flap),
            (cx + side * 50, cy + 20 + flap),
            (cx + side * 35, cy + 18 + flap),
            (cx + side * 12, cy + 10)]
        pygame.draw.polygon(surface, (*flame, int(255 * pulse)), bolt_pts)
        # 闪电边缘发光
        pygame.draw.polygon(surface, (255, 255, 220), bolt_pts, 2)
        # 内部亮线
        inner_pts = [(int(p[0] * 0.95 + cx * 0.05), int(p[1] * 0.95 + cy * 0.05)) for p in bolt_pts]
        pygame.draw.polygon(surface, (*core, int(200 * pulse)), inner_pts)
        # 电弧分支
        for i in range(2):
            bx = cx + side * (25 + i * 15)
            by = cy - 15 + i * 12 + flap * 0.6
            branch_pts = [(int(bx), int(by)), 
                (int(bx + side * 8), int(by - 6)), 
                (int(bx + side * 12), int(by - 10))]
            pygame.draw.lines(surface, flame, False, branch_pts, 2)
    
    # 雷云躯干 - 蓬松积雨云
    # 云底
    pygame.draw.ellipse(surface, armor, (cx - 20, cy - 5, 40, 42))
    # 云朵层叠
    cloud_parts = [
        (cx - 12, cy - 12, 18), (cx + 8, cy - 10, 16), (cx, cy - 18, 14),
        (cx - 8, cy + 5, 15), (cx + 6, cy + 8, 14)]
    for ccx, ccy, cr in cloud_parts:
        pygame.draw.circle(surface, armor, (int(ccx), int(ccy)), cr)
    # 云的阴影
    pygame.draw.ellipse(surface, armor_dark, (cx - 15, cy + 15, 30, 12))
    # 内部闪光
    if math.sin(t * 10) > 0.6:
        pygame.draw.ellipse(surface, (*flame, 100), (cx - 10, cy - 5, 20, 15))
    
    # 头部 - 怒云
    head_y = y + 3
    pygame.draw.ellipse(surface, armor, (cx - 14, head_y - 3, 28, 22))
    # 云鬓
    for i in range(3):
        pygame.draw.circle(surface, armor, (cx - 10 + i * 10, head_y - 2), 8)
    # 眼睛 - 闪电眼
    for side in [-1, 1]:
        ex = cx + side * 6
        glow = 0.5 + 0.5 * math.sin(t * 6 + side)
        pygame.draw.circle(surface, (*flame, int(255 * glow)), (ex, head_y + 8), 5)
        pygame.draw.circle(surface, core, (ex, head_y + 8), 3)
        pygame.draw.circle(surface, (255, 255, 255), (ex, head_y + 8), 1)
    # 怒眉
    for side in [-1, 1]:
        pygame.draw.line(surface, armor_dark, 
            (cx + side * 2, head_y + 3), (cx + side * 10, head_y + 1), 2)
    
    # 随机闪电 - 更剧烈
    if abs(math.sin(t * 8)) > 0.65:
        bolt_x = cx + 15 * math.sin(t * 11)
        bpts = [(int(bolt_x), cy + 8)]
        bx, by = bolt_x, cy + 8
        for i in range(5):
            by += 7 + int(3 * math.sin(t * 9 + i))
            bx += int(math.sin(t * 13 + i * 2) * 8)
            bpts.append((int(bx), int(by)))
        pygame.draw.lines(surface, flame, False, bpts, 3)
        pygame.draw.lines(surface, (255, 255, 220), False, bpts, 1)
        # 分叉
        if len(bpts) > 2:
            fork_pt = bpts[2]
            pygame.draw.line(surface, flame, fork_pt, 
                (fork_pt[0] + 10, fork_pt[1] + 8), 2)
    
    # 雨滴浮游炮 - 水滴形
    for i in range(6):
        ra = t * 2.5 + i * math.pi / 3
        rx = cx + math.cos(ra) * 46
        ry = cy + math.sin(ra) * 26
        # 水滴形状
        pygame.draw.polygon(surface, (*trail, 200), [
            (int(rx), int(ry) - 8), (int(rx) - 5, int(ry) + 4), 
            (int(rx), int(ry) + 8), (int(rx) + 5, int(ry) + 4)])
        # 高光
        pygame.draw.polygon(surface, (255, 255, 255, 150), [
            (int(rx) - 1, int(ry) - 4), (int(rx) - 3, int(ry) + 2), (int(rx) - 1, int(ry) + 2)])
    
    # 雨滴尾迹 - 密集雨幕
    for i in range(10):
        phase = (t * 60 + i * 8) % 35
        rx = cx - 22 + i * 5 + 3 * math.sin(i)
        ry = cy + 25 + phase
        rl = 6 + int(phase / 10)
        alpha = max(0, 150 - int(phase * 4))
        pygame.draw.line(surface, (*trail, alpha), (int(rx), int(ry)), (int(rx), int(ry + rl)), 1)


# ==================== 蜂巢龙 ====================
def draw_hive_dragon(surface, x, y, w, h, frame, style):
    """蜂巢翅膀，蜂蜡躯干，蜜蜂浮游"""
    theme = get_yharon_theme(style)
    armor, flame, core, gold, trail = theme["armor"], theme["flame"], theme["core"], theme["gold"], theme["trail"]
    armor_dark = tuple(max(0, c - 35) for c in armor)
    t = frame * 0.06
    cx, cy = x + w // 2, y + h // 2
    
    # 蜂巢翅膀 - 精细六边形结构
    for side in [-1, 1]:
        # 蜂巢底板
        wing_pts = [
            (cx + side * 10, cy - 15), (cx + side * 50, cy - 25),
            (cx + side * 55, cy + 5), (cx + side * 45, cy + 25),
            (cx + side * 12, cy + 18)]
        pygame.draw.polygon(surface, armor_dark, wing_pts)
        # 六边形蜂房
        for i in range(4):
            for j in range(3):
                hx = cx + side * (18 + i * 12)
                hy = cy - 12 + j * 14 + (i % 2) * 7
                flap = 2 * math.sin(t * 2 + i + j)
                # 六边形
                hex_pts = []
                for k in range(6):
                    ha = k * math.pi / 3 + math.pi / 6
                    hex_pts.append((int(hx + math.cos(ha) * 6), int(hy + flap + math.sin(ha) * 6)))
                pygame.draw.polygon(surface, armor, hex_pts)
                pygame.draw.polygon(surface, gold, hex_pts, 1)
                # 蜂房深度 - 中心阴影
                pygame.draw.circle(surface, armor_dark, (int(hx), int(hy + flap)), 3)
                # 蜂蜜填充 - 部分蜂房
                if (i + j) % 3 == 0:
                    pygame.draw.circle(surface, (*trail, 180), (int(hx), int(hy + flap)), 4)
    
    # 蜂蜡躯干 - 有机质感
    # 躯干主体
    pygame.draw.ellipse(surface, armor, (cx - 16, cy - 12, 32, 50))
    # 蜂蜡纹理
    for i in range(4):
        ty = cy - 5 + i * 10
        pygame.draw.ellipse(surface, armor_dark, (cx - 12, ty, 24, 8), 1)
    # 蜂蜜光泽
    pygame.draw.ellipse(surface, (*flame, 150), (cx - 10, cy - 2, 20, 28))
    pygame.draw.ellipse(surface, (*trail, 100), (cx - 6, cy + 5, 12, 15))
    # 高光
    pygame.draw.ellipse(surface, (255, 255, 200, 80), (cx - 4, cy, 6, 4))
    
    # 头部 - 蜜蜂女王
    head_y = y + 3
    pygame.draw.ellipse(surface, armor, (cx - 12, head_y + 2, 24, 20))
    # 触角 - 动态摆动
    for side in [-1, 1]:
        ant_wave = 3 * math.sin(t * 4 + side)
        # 触角杆
        pygame.draw.line(surface, gold, (cx + side * 5, head_y + 5), 
            (int(cx + side * 10 + ant_wave), head_y - 8), 2)
        # 触角球
        pygame.draw.circle(surface, flame, (int(cx + side * 10 + ant_wave), head_y - 8), 4)
        pygame.draw.circle(surface, core, (int(cx + side * 10 + ant_wave), head_y - 8), 2)
    # 复眼
    for side in [-1, 1]:
        ex = cx + side * 5
        pygame.draw.ellipse(surface, (20, 20, 20), (ex - 4, head_y + 8, 8, 10))
        # 复眼纹理
        for i in range(3):
            for j in range(2):
                pygame.draw.circle(surface, (40, 40, 50), 
                    (ex - 2 + i * 2, head_y + 10 + j * 3), 1)
        # 复眼高光
        pygame.draw.ellipse(surface, (80, 80, 100), (ex - 2, head_y + 8, 3, 4))
    # 口器
    pygame.draw.polygon(surface, gold, [(cx - 2, head_y + 18), (cx + 2, head_y + 18), (cx, head_y + 24)])
    
    # 蜜蜂浮游炮 - 精细工蜂
    for i in range(6):
        ba = t * 3.5 + i * math.pi / 3
        bx = cx + math.cos(ba) * 48
        by = cy + math.sin(ba) * 28
        # 蜜蜂身体
        pygame.draw.ellipse(surface, armor, (int(bx) - 5, int(by) - 3, 10, 6))
        # 条纹
        pygame.draw.line(surface, (30, 30, 30), (int(bx) - 3, int(by) - 3), (int(bx) - 3, int(by) + 3), 1)
        pygame.draw.line(surface, (30, 30, 30), (int(bx), int(by) - 3), (int(bx), int(by) + 3), 1)
        pygame.draw.line(surface, (30, 30, 30), (int(bx) + 3, int(by) - 3), (int(bx) + 3, int(by) + 3), 1)
        # 头
        pygame.draw.circle(surface, armor, (int(bx) - 6, int(by)), 3)
        # 翅膀 - 高频振动
        wf = 4 * math.sin(t * 20 + i)
        pygame.draw.ellipse(surface, (*trail, 120), (int(bx) - 7, int(by) - 6 - int(abs(wf)), 6, 5))
        pygame.draw.ellipse(surface, (*trail, 120), (int(bx) + 1, int(by) - 6 - int(abs(wf)), 6, 5))
        # 尾针
        pygame.draw.line(surface, (30, 30, 30), (int(bx) + 5, int(by)), (int(bx) + 9, int(by)), 1)
    
    # 蜂蜜尾迹 - 粘稠滴落
    for i in range(4):
        phase = (t * 20 + i * 15) % 25
        dx = cx - 8 + i * 5
        dy = y + h + 5 + phase
        dr = max(2, 6 - int(phase / 5))
        # 蜂蜜滴
        pygame.draw.circle(surface, trail, (int(dx), int(dy)), dr)
        # 拉丝效果
        if phase < 10:
            pygame.draw.line(surface, (*trail, 150), (int(dx), y + h), (int(dx), int(dy - dr)), 2)


# ==================== 晶洞龙 ====================
def draw_geode_dragon(surface, x, y, w, h, frame, style):
    """水晶翅膀，晶洞躯干，碎晶浮游"""
    theme = get_yharon_theme(style)
    armor, flame, core, gold, trail = theme["armor"], theme["flame"], theme["core"], theme["gold"], theme["trail"]
    armor_dark = tuple(max(0, c - 50) for c in armor)
    t = frame * 0.06
    cx, cy = x + w // 2, y + h // 2
    
    # 水晶生长翅膀 - 不规则晶簇
    for side in [-1, 1]:
        # 大晶簇
        crystal_data = [
            (0.2, 35, 8), (0.5, 42, 10), (0.8, 38, 7), (1.1, 32, 9),
            (1.4, 28, 6), (-0.1, 30, 7), (0.35, 45, 11)]
        for angle_off, length, width in crystal_data:
            ca = (angle_off if side > 0 else math.pi - angle_off)
            cl = length + 5 * math.sin(t * 2 + angle_off)
            # 晶体基座
            bx = cx + side * 10
            by = cy - 5 + angle_off * 15
            # 晶体尖端
            tx = bx + math.cos(ca - math.pi/2) * cl * side
            ty = by + math.sin(ca - math.pi/2) * cl * 0.7
            # 晶体多面体
            pts = [
                (bx - width//2, by + 3), (bx + width//2, by + 3),
                (int(tx + width//3), int(ty + 5)), (int(tx), int(ty)),
                (int(tx - width//3), int(ty + 5))]
            # 晶体主体 - 半透明
            glow = 0.5 + 0.5 * math.sin(t * 3 + angle_off * 2)
            pygame.draw.polygon(surface, (*flame, int(200 * glow)), pts)
            # 晶体边缘
            pygame.draw.polygon(surface, gold, pts, 1)
            # 晶体内部折射线
            pygame.draw.line(surface, (*core, int(150 * glow)), 
                (bx, by), (int(tx), int(ty)), 1)
            # 晶体尖端发光
            pygame.draw.circle(surface, (*core, int(200 * glow)), (int(tx), int(ty)), 4)
            pygame.draw.circle(surface, (255, 255, 255, int(100 * glow)), (int(tx), int(ty)), 2)
    
    # 晶洞躯干 - 外壳+内部晶腔
    # 外壳 - 粗糙岩石
    pygame.draw.ellipse(surface, armor, (cx - 18, cy - 10, 36, 48))
    # 岩石纹理
    for i in range(5):
        rx = cx - 12 + i * 6
        ry = cy - 5 + (i % 3) * 12
        pygame.draw.circle(surface, armor_dark, (rx, ry), 4 + i % 3)
    # 晶腔 - 深紫色内部
    pygame.draw.ellipse(surface, (30, 20, 50), (cx - 14, cy - 5, 28, 38))
    # 内部晶簇 - 向内生长
    inner_crystals = [
        (cx - 8, cy + 25, 12, 0.3), (cx, cy + 28, 15, 0),
        (cx + 8, cy + 25, 11, -0.3), (cx - 5, cy + 20, 10, 0.2),
        (cx + 5, cy + 20, 10, -0.2), (cx, cy + 15, 8, 0)]
    for icx, icy, il, ia in inner_crystals:
        glow = 0.6 + 0.4 * math.sin(t * 4 + icx * 0.1)
        tip_x = icx + math.sin(ia) * il * 0.3
        tip_y = icy - il - 3 * math.sin(t * 3)
        pts = [(icx - 3, icy), (int(tip_x), int(tip_y)), (icx + 3, icy)]
        pygame.draw.polygon(surface, (*flame, int(220 * glow)), pts)
        pygame.draw.polygon(surface, (*core, int(180 * glow)), pts, 1)
    
    # 头部 - 晶冠龙首
    head_y = y + 2
    # 头部岩石外层
    pygame.draw.polygon(surface, armor, [
        (cx - 12, head_y + 20), (cx - 10, head_y + 5), (cx - 5, head_y),
        (cx + 5, head_y), (cx + 10, head_y + 5), (cx + 12, head_y + 20)])
    # 头顶晶冠
    crown_crystals = [(-6, 8), (-2, 12), (2, 10), (6, 7)]
    for ccx_off, cl in crown_crystals:
        glow = 0.5 + 0.5 * math.sin(t * 5 + ccx_off)
        pts = [(cx + ccx_off - 2, head_y + 3), 
               (cx + ccx_off, head_y - cl + 3 * math.sin(t * 2)), 
               (cx + ccx_off + 2, head_y + 3)]
        pygame.draw.polygon(surface, (*flame, int(230 * glow)), pts)
        pygame.draw.circle(surface, (*core, int(200 * glow)), 
            (cx + ccx_off, int(head_y - cl + 3 * math.sin(t * 2))), 2)
    # 眼睛 - 宝石眼
    for side in [-1, 1]:
        ex = cx + side * 5
        pygame.draw.polygon(surface, (30, 20, 50), [
            (ex - 3, head_y + 10), (ex, head_y + 7), (ex + 3, head_y + 10), (ex, head_y + 14)])
        glow = 0.5 + 0.5 * math.sin(t * 4 + side)
        pygame.draw.circle(surface, (*core, int(255 * glow)), (ex, head_y + 10), 3)
        pygame.draw.circle(surface, (255, 255, 255), (ex - 1, head_y + 9), 1)
    
    # 碎晶浮游炮 - 旋转多面体
    for i in range(5):
        fa = t * 2 + i * math.pi * 2 / 5
        fx = cx + math.cos(fa) * 50
        fy = cy + math.sin(fa) * 30
        fr = t * 4 + i * 2
        glow = 0.5 + 0.5 * math.sin(t * 5 + i)
        # 八面体晶体
        pts = []
        for j in range(4):
            pa = fr + j * math.pi / 2
            pts.append((int(fx + math.cos(pa) * 8), int(fy + math.sin(pa) * 8)))
        pygame.draw.polygon(surface, (*flame, int(200 * glow)), pts)
        pygame.draw.polygon(surface, gold, pts, 1)
        # 顶点
        pygame.draw.circle(surface, (*core, int(220 * glow)), (int(fx), int(fy)), 4)
        # 光芒
        for j in range(4):
            ra = fr + j * math.pi / 2 + math.pi / 4
            pygame.draw.line(surface, (*core, int(100 * glow)), (int(fx), int(fy)),
                (int(fx + math.cos(ra) * 12), int(fy + math.sin(ra) * 12)), 1)
    
    # 折射光尾迹 - 彩虹棱镜
    prism_colors = [(255, 100, 100), (255, 200, 100), (100, 255, 100), (100, 200, 255), (200, 100, 255)]
    for i, pc in enumerate(prism_colors):
        ra = t * 0.8 + i * math.pi / 2.5
        rl = 40 + 10 * math.sin(t * 3 + i)
        alpha = int(80 + 40 * math.sin(t * 4 + i))
        pygame.draw.line(surface, (*pc, alpha), (cx, cy),
            (int(cx + math.cos(ra) * rl), int(cy + math.sin(ra) * rl)), 2)


def render_yharon_skin(surface, color, x, y, w, h, frame, style):
    """渲染犽戎涂装"""
    draw_yharon(surface, color, x, y, w, h, frame, style)
