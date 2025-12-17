# -*- coding: utf-8 -*-
"""
至尊灾厄·终末王座 (SCal-System "SEPULCHER") 涂装系统
原型：Terraria Calamity Mod - Supreme Calamitas (The Witch of Calamity)
设计风格：哥特式神秘学 + 几何科技 + 反重力浮游架构
机体造型：倒三角形黑曜石祭坛 + 中央灾厄之眼 + 浮游符文石板 + 机械骷髅长尾 + 旋转魔法阵光环
"""
import pygame
import math

# ==================== 12种涂装主题定义 ====================
SEPULCHER_THEMES = {
    # 默认涂装：终末王座 - 至尊灾厄的原始形态
    "sepulcher_default": {
        "name": "终末王座",
        "description": "至尊灾厄的原始形态，黑曜石祭坛散发着猩红压迫感",
        "armor": (26, 26, 26),           # 木炭黑 #1A1A1A - 主装甲
        "armor_light": (50, 50, 55),     # 亮边
        "armor_dark": (15, 15, 18),      # 暗部
        "armor_shadow": (8, 8, 10),      # 阴影
        "core": (220, 20, 60),           # 猩红 #DC143C - 核心能量
        "core_bright": (255, 80, 100),   # 核心高亮
        "core_dark": (150, 10, 40),      # 核心暗部
        "hellfire": (255, 69, 0),        # 地狱橙 #FF4500 - 地狱火焰
        "hellfire_bright": (255, 120, 50),
        "rune": (139, 0, 0),             # 暗红符文
        "rune_glow": (200, 50, 50),      # 符文发光
        "skull": (180, 30, 30),          # 骷髅红
        "skull_dark": (120, 20, 20),     # 骷髅暗部
        "halo": (255, 50, 50),           # 光环红
        "halo_bright": (255, 100, 100),  # 光环高亮
        "eye": (255, 0, 0),              # 灾厄之眼 - 纯红
        "eye_glow": (255, 50, 50),       # 眼部光晕
        "obsidian": (20, 20, 25),        # 黑曜石
        "obsidian_vein": (40, 20, 30),   # 黑曜石纹理
        "magic": (255, 100, 80),         # 魔法粒子
        "rarity": "legendary",
    },
    
    # 涂装2：硫磺炼狱 - 地狱硫磺火焰主题
    "sepulcher_brimstone": {
        "name": "硫磺炼狱",
        "description": "浸染硫磺之火的祭坛，燃烧着永恒的地狱之焰",
        "armor": (45, 25, 15),
        "armor_light": (70, 45, 30),
        "armor_dark": (30, 15, 8),
        "armor_shadow": (20, 10, 5),
        "core": (255, 100, 0),
        "core_bright": (255, 150, 50),
        "core_dark": (200, 60, 0),
        "hellfire": (255, 150, 50),
        "hellfire_bright": (255, 200, 100),
        "rune": (200, 80, 0),
        "rune_glow": (255, 120, 30),
        "skull": (220, 100, 50),
        "skull_dark": (160, 60, 30),
        "halo": (255, 120, 30),
        "halo_bright": (255, 170, 80),
        "eye": (255, 80, 0),
        "eye_glow": (255, 130, 50),
        "obsidian": (50, 30, 15),
        "obsidian_vein": (80, 50, 25),
        "magic": (255, 180, 100),
        "rarity": "epic",
    },
    
    # 涂装3：深渊女巫 - 灾厄女巫的诅咒紫形态
    "sepulcher_witch": {
        "name": "深渊女巫",
        "description": "灾厄女巫的真实形态，紫黑色的诅咒之力",
        "armor": (35, 20, 50),
        "armor_light": (55, 40, 80),
        "armor_dark": (25, 12, 35),
        "armor_shadow": (15, 8, 25),
        "core": (180, 50, 200),
        "core_bright": (220, 100, 255),
        "core_dark": (130, 30, 150),
        "hellfire": (220, 100, 255),
        "hellfire_bright": (240, 150, 255),
        "rune": (100, 30, 130),
        "rune_glow": (160, 80, 200),
        "skull": (150, 60, 180),
        "skull_dark": (100, 40, 130),
        "halo": (200, 80, 255),
        "halo_bright": (230, 130, 255),
        "eye": (180, 0, 220),
        "eye_glow": (220, 80, 255),
        "obsidian": (30, 18, 45),
        "obsidian_vein": (50, 30, 70),
        "magic": (200, 150, 255),
        "rarity": "legendary",
    },
    
    # 涂装4：血月祭礼 - 鲜血染红的祭坛
    "sepulcher_bloodmoon": {
        "name": "血月祭礼",
        "description": "血月之夜觉醒的祭坛，鲜血染红了一切",
        "armor": (55, 15, 15),
        "armor_light": (80, 30, 30),
        "armor_dark": (40, 8, 8),
        "armor_shadow": (25, 5, 5),
        "core": (200, 0, 30),
        "core_bright": (255, 50, 70),
        "core_dark": (150, 0, 20),
        "hellfire": (255, 30, 60),
        "hellfire_bright": (255, 80, 100),
        "rune": (150, 0, 20),
        "rune_glow": (200, 30, 50),
        "skull": (180, 20, 40),
        "skull_dark": (130, 10, 30),
        "halo": (230, 20, 50),
        "halo_bright": (255, 60, 90),
        "eye": (200, 0, 0),
        "eye_glow": (255, 50, 50),
        "obsidian": (45, 12, 18),
        "obsidian_vein": (70, 25, 35),
        "magic": (255, 100, 120),
        "rarity": "epic",
    },
    
    # 涂装5：虚空主宰 - 吞噬一切的虚空
    "sepulcher_void": {
        "name": "虚空主宰",
        "description": "超越灾厄的虚空存在，吞噬一切光明",
        "armor": (12, 12, 25),
        "armor_light": (25, 25, 45),
        "armor_dark": (6, 6, 15),
        "armor_shadow": (3, 3, 10),
        "core": (100, 50, 150),
        "core_bright": (150, 100, 200),
        "core_dark": (60, 30, 100),
        "hellfire": (80, 40, 120),
        "hellfire_bright": (120, 80, 160),
        "rune": (60, 30, 90),
        "rune_glow": (100, 60, 140),
        "skull": (90, 50, 130),
        "skull_dark": (60, 30, 90),
        "halo": (120, 60, 180),
        "halo_bright": (160, 100, 220),
        "eye": (150, 80, 200),
        "eye_glow": (180, 120, 230),
        "obsidian": (8, 8, 20),
        "obsidian_vein": (20, 15, 40),
        "magic": (140, 100, 200),
        "rarity": "legendary",
    },
    
    # 涂装6：暗影行者 - 极致暗黑，仅眼睛发光
    "sepulcher_shadow": {
        "name": "暗影行者",
        "description": "与暗影融为一体的祭坛，仅有眼睛在黑暗中闪烁",
        "armor": (18, 18, 18),
        "armor_light": (35, 35, 35),
        "armor_dark": (10, 10, 10),
        "armor_shadow": (5, 5, 5),
        "core": (100, 100, 100),
        "core_bright": (140, 140, 140),
        "core_dark": (60, 60, 60),
        "hellfire": (80, 80, 80),
        "hellfire_bright": (120, 120, 120),
        "rune": (50, 50, 50),
        "rune_glow": (80, 80, 80),
        "skull": (70, 70, 70),
        "skull_dark": (45, 45, 45),
        "halo": (90, 90, 90),
        "halo_bright": (130, 130, 130),
        "eye": (255, 255, 255),          # 唯一亮点 - 纯白眼
        "eye_glow": (200, 200, 200),
        "obsidian": (12, 12, 12),
        "obsidian_vein": (25, 25, 25),
        "magic": (150, 150, 150),
        "rarity": "rare",
    },
    
    # 涂装7：熔岩领主 - 火山岩浆主题
    "sepulcher_magma": {
        "name": "熔岩领主",
        "description": "从地核深处升起的祭坛，岩浆在裂缝中流淌",
        "armor": (65, 35, 15),
        "armor_light": (90, 55, 30),
        "armor_dark": (45, 25, 10),
        "armor_shadow": (30, 15, 5),
        "core": (255, 100, 0),
        "core_bright": (255, 150, 50),
        "core_dark": (200, 70, 0),
        "hellfire": (255, 180, 50),
        "hellfire_bright": (255, 220, 100),
        "rune": (200, 60, 0),
        "rune_glow": (255, 100, 30),
        "skull": (230, 120, 30),
        "skull_dark": (180, 80, 20),
        "halo": (255, 150, 50),
        "halo_bright": (255, 200, 100),
        "eye": (255, 80, 0),
        "eye_glow": (255, 130, 50),
        "obsidian": (80, 45, 25),
        "obsidian_vein": (120, 70, 40),
        "magic": (255, 200, 100),
        "rarity": "rare",
    },
    
    # 涂装8：寒霜灾厄 - 冰封的死寂
    "sepulcher_frost": {
        "name": "寒霜灾厄",
        "description": "冰封的灾厄祭坛，散发着死寂的寒气",
        "armor": (35, 45, 60),
        "armor_light": (55, 70, 90),
        "armor_dark": (25, 35, 45),
        "armor_shadow": (15, 25, 35),
        "core": (100, 180, 220),
        "core_bright": (150, 220, 255),
        "core_dark": (60, 130, 180),
        "hellfire": (150, 220, 255),
        "hellfire_bright": (200, 240, 255),
        "rune": (70, 130, 170),
        "rune_glow": (120, 180, 220),
        "skull": (120, 180, 210),
        "skull_dark": (80, 140, 170),
        "halo": (140, 200, 240),
        "halo_bright": (180, 230, 255),
        "eye": (100, 200, 255),
        "eye_glow": (150, 230, 255),
        "obsidian": (45, 55, 70),
        "obsidian_vein": (70, 85, 105),
        "magic": (180, 230, 255),
        "rarity": "epic",
    },
    
    # 涂装9：噬魂者 - 幽绿灵魂能量
    "sepulcher_souleater": {
        "name": "噬魂者",
        "description": "以灵魂为食的邪恶祭坛，幽绿色的冥光",
        "armor": (25, 35, 25),
        "armor_light": (45, 60, 45),
        "armor_dark": (15, 25, 15),
        "armor_shadow": (10, 18, 10),
        "core": (80, 200, 100),
        "core_bright": (120, 255, 140),
        "core_dark": (50, 150, 70),
        "hellfire": (100, 255, 130),
        "hellfire_bright": (150, 255, 180),
        "rune": (50, 150, 70),
        "rune_glow": (90, 200, 110),
        "skull": (70, 180, 90),
        "skull_dark": (45, 130, 60),
        "halo": (90, 220, 110),
        "halo_bright": (130, 255, 150),
        "eye": (100, 255, 120),
        "eye_glow": (150, 255, 170),
        "obsidian": (20, 30, 22),
        "obsidian_vein": (35, 50, 38),
        "magic": (150, 255, 180),
        "rarity": "epic",
    },
    
    # 涂装10：末日审判 - 神圣金色天罚
    "sepulcher_apocalypse": {
        "name": "末日审判",
        "description": "世界终结时刻的祭坛，金红色的天罚之光",
        "armor": (50, 40, 25),
        "armor_light": (75, 65, 45),
        "armor_dark": (35, 28, 18),
        "armor_shadow": (25, 20, 12),
        "core": (255, 180, 0),
        "core_bright": (255, 220, 80),
        "core_dark": (200, 140, 0),
        "hellfire": (255, 220, 100),
        "hellfire_bright": (255, 240, 150),
        "rune": (200, 150, 50),
        "rune_glow": (255, 200, 100),
        "skull": (220, 180, 80),
        "skull_dark": (180, 140, 50),
        "halo": (255, 200, 50),
        "halo_bright": (255, 230, 120),
        "eye": (255, 200, 0),
        "eye_glow": (255, 230, 100),
        "obsidian": (55, 45, 30),
        "obsidian_vein": (85, 70, 50),
        "magic": (255, 240, 150),
        "rarity": "legendary",
    },
    
    # 涂装11：炽天使 - 堕落的神圣光辉
    "sepulcher_seraph": {
        "name": "炽天使",
        "description": "堕落天使的形态，圣光与暗焰交织",
        "armor": (55, 55, 65),
        "armor_light": (80, 80, 95),
        "armor_dark": (40, 40, 50),
        "armor_shadow": (30, 30, 38),
        "core": (255, 220, 180),
        "core_bright": (255, 245, 220),
        "core_dark": (220, 180, 140),
        "hellfire": (255, 240, 200),
        "hellfire_bright": (255, 250, 230),
        "rune": (200, 180, 150),
        "rune_glow": (240, 220, 190),
        "skull": (220, 200, 170),
        "skull_dark": (180, 160, 130),
        "halo": (255, 230, 190),
        "halo_bright": (255, 245, 220),
        "eye": (255, 215, 0),            # 金色神圣之眼
        "eye_glow": (255, 235, 100),
        "obsidian": (65, 65, 75),
        "obsidian_vein": (95, 95, 110),
        "magic": (255, 250, 220),
        "rarity": "legendary",
    },
    
    # 涂装12：量子灾变 - 科技蓝量子能量
    "sepulcher_quantum": {
        "name": "量子灾变",
        "description": "融合量子科技的祭坛，数据流与魔法交织",
        "armor": (25, 30, 45),
        "armor_light": (45, 55, 75),
        "armor_dark": (15, 20, 32),
        "armor_shadow": (10, 12, 22),
        "core": (0, 200, 255),
        "core_bright": (80, 230, 255),
        "core_dark": (0, 150, 200),
        "hellfire": (100, 220, 255),
        "hellfire_bright": (150, 240, 255),
        "rune": (50, 150, 200),
        "rune_glow": (100, 200, 250),
        "skull": (80, 180, 220),
        "skull_dark": (50, 140, 180),
        "halo": (0, 220, 255),
        "halo_bright": (100, 240, 255),
        "eye": (0, 255, 255),            # 青色量子之眼
        "eye_glow": (100, 255, 255),
        "obsidian": (20, 25, 40),
        "obsidian_vein": (35, 45, 65),
        "magic": (150, 240, 255),
        "rarity": "epic",
    },
}

# 涂装ID列表
SEPULCHER_STYLES = list(SEPULCHER_THEMES.keys()) + ["default"]


def get_sepulcher_theme(style):
    """获取Sepulcher涂装主题配色"""
    if style == "default":
        style = "sepulcher_default"
    elif not style.startswith("sepulcher_") and f"sepulcher_{style}" in SEPULCHER_THEMES:
        style = f"sepulcher_{style}"
    
    if style in SEPULCHER_THEMES:
        return SEPULCHER_THEMES[style]
    return SEPULCHER_THEMES["sepulcher_default"]


def get_sepulcher_skin_list():
    """获取所有涂装ID列表"""
    return list(SEPULCHER_THEMES.keys())


def get_all_sepulcher_skins():
    """获取所有涂装列表"""
    return list(SEPULCHER_THEMES.keys())


def is_sepulcher_style(style):
    """检查是否为Sepulcher涂装"""
    if style in SEPULCHER_STYLES:
        return True
    if style in SEPULCHER_THEMES:
        return True
    return False


def get_sepulcher_skin_info(style):
    """获取涂装详细信息"""
    theme = get_sepulcher_theme(style)
    return {
        "id": style,
        "name": theme.get("name", "Unknown"),
        "description": theme.get("description", ""),
        "rarity": theme.get("rarity", "common"),
    }


# ==================== 绘制调度函数 ====================
def draw_sepulcher(surface, color, x, y, w, h, frame, style="sepulcher_default"):
    """
    绘制Sepulcher机体 - 根据涂装调用专属绘制函数
    
    参数:
        surface: pygame绘制表面
        color: 基础颜色（可被涂装覆盖）
        x, y: 绘制位置
        w, h: 绘制尺寸
        frame: 当前帧数（用于动画）
        style: 涂装ID
    """
    if style == "default":
        style = "sepulcher_default"
    elif not style.startswith("sepulcher_") and f"sepulcher_{style}" in SEPULCHER_THEMES:
        style = f"sepulcher_{style}"
    
    # 涂装绘制器映射
    drawers = {
        "sepulcher_default": draw_default_sepulcher,
        "sepulcher_brimstone": draw_brimstone_sepulcher,
        "sepulcher_witch": draw_witch_sepulcher,
        "sepulcher_bloodmoon": draw_bloodmoon_sepulcher,
        "sepulcher_void": draw_void_sepulcher,
        "sepulcher_shadow": draw_shadow_sepulcher,
        "sepulcher_magma": draw_magma_sepulcher,
        "sepulcher_frost": draw_frost_sepulcher,
        "sepulcher_souleater": draw_souleater_sepulcher,
        "sepulcher_apocalypse": draw_apocalypse_sepulcher,
        "sepulcher_seraph": draw_seraph_sepulcher,
        "sepulcher_quantum": draw_quantum_sepulcher,
    }
    
    drawer = drawers.get(style, draw_default_sepulcher)
    drawer(surface, x, y, w, h, frame, style)


# ==================== 核心绘制函数 ====================
def _draw_sepulcher_body(surface, x, y, w, h, frame, theme):
    """
    绘制Sepulcher主体 - 哥特式黑曜石祭坛型浮游战舰
    
    十层精细绘制：
    1. 深层魔法阵背景光晕
    2. 六芒星能量底纹
    3. 旋转魔法阵光环（头顶悬浮）
    4. 浮游符文石板阵列（两侧）
    5. 倒三角形黑曜石祭坛主体
    6. 灾厄之眼核心（中央大眼）
    7. 眼睫状机械护栏尖刺
    8. 机械骷髅长尾浮游炮
    9. 哥特式尖刺冠与侧翼
    10. 能量管道与细节装饰
    """
    # 获取主题颜色
    armor = theme["armor"]
    armor_light = theme["armor_light"]
    armor_dark = theme["armor_dark"]
    armor_shadow = theme["armor_shadow"]
    core = theme["core"]
    core_bright = theme["core_bright"]
    core_dark = theme["core_dark"]
    hellfire = theme["hellfire"]
    hellfire_bright = theme["hellfire_bright"]
    rune = theme["rune"]
    rune_glow = theme["rune_glow"]
    skull = theme["skull"]
    skull_dark = theme["skull_dark"]
    halo = theme["halo"]
    halo_bright = theme["halo_bright"]
    eye_color = theme["eye"]
    eye_glow = theme["eye_glow"]
    obsidian = theme["obsidian"]
    obsidian_vein = theme["obsidian_vein"]
    magic = theme["magic"]
    
    # 中心点和时间变量
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.04
    
    # ========== 【第一层】深层魔法阵背景光晕 ==========
    # 多层扩散光环，从外到内逐渐明亮
    for ring in range(8):
        ring_radius = int(65 - ring * 7 + 5 * math.sin(t * 1.2 + ring * 0.3))
        ring_alpha = max(0, 35 - ring * 4)
        
        if ring_radius > 0 and ring_alpha > 0:
            glow_surf = pygame.Surface((ring_radius * 2 + 6, ring_radius * 2 + 6), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*core, ring_alpha), 
                             (ring_radius + 3, ring_radius + 3), ring_radius)
            surface.blit(glow_surf, (cx - ring_radius - 3, cy - ring_radius - 3))
    
    # 核心光晕脉动
    pulse_intensity = int(25 + 15 * math.sin(t * 2.5))
    core_glow_r = int(40 + 8 * math.sin(t * 2))
    if core_glow_r > 0:
        inner_glow = pygame.Surface((core_glow_r * 2 + 4, core_glow_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(inner_glow, (*core_bright, pulse_intensity),
                          (core_glow_r + 2, core_glow_r + 2), core_glow_r)
        surface.blit(inner_glow, (cx - core_glow_r - 2, cy - core_glow_r - 2))
    
    # ========== 【第二层】六芒星能量底纹 ==========
    hex_radius = 55 + 4 * math.sin(t * 0.5)
    hex_rotation = t * 1.5
    
    # 外层六芒星
    for i in range(6):
        angle1 = math.radians(i * 60) + hex_rotation
        angle2 = math.radians((i + 2) * 60) + hex_rotation
        
        x1 = cx + int(math.cos(angle1) * hex_radius)
        y1 = cy + int(math.sin(angle1) * hex_radius * 0.55)  # 椭圆压缩
        x2 = cx + int(math.cos(angle2) * hex_radius)
        y2 = cy + int(math.sin(angle2) * hex_radius * 0.55)
        
        # 六芒星线条
        line_alpha = int(50 + 20 * math.sin(t * 2 + i * 0.5))
        pygame.draw.line(surface, (*rune, line_alpha), (x1, y1), (x2, y2), 1)
        
        # 顶点光点
        vertex_x = cx + int(math.cos(angle1) * hex_radius)
        vertex_y = cy + int(math.sin(angle1) * hex_radius * 0.55)
        vertex_glow = int(3 + 2 * math.sin(t * 4 + i))
        pygame.draw.circle(surface, (*rune_glow, 100), (vertex_x, vertex_y), vertex_glow)
    
    # 内层六芒星（反向旋转）
    inner_hex_r = hex_radius * 0.6
    for i in range(6):
        angle1 = math.radians(i * 60 + 30) - hex_rotation * 0.7
        angle2 = math.radians((i + 2) * 60 + 30) - hex_rotation * 0.7
        
        x1 = cx + int(math.cos(angle1) * inner_hex_r)
        y1 = cy + int(math.sin(angle1) * inner_hex_r * 0.55)
        x2 = cx + int(math.cos(angle2) * inner_hex_r)
        y2 = cy + int(math.sin(angle2) * inner_hex_r * 0.55)
        
        pygame.draw.line(surface, (*rune, 35), (x1, y1), (x2, y2), 1)
    
    # 连接线（内外六芒星）
    for i in range(6):
        outer_angle = math.radians(i * 60) + hex_rotation
        inner_angle = math.radians(i * 60 + 30) - hex_rotation * 0.7
        
        ox = cx + int(math.cos(outer_angle) * hex_radius)
        oy = cy + int(math.sin(outer_angle) * hex_radius * 0.55)
        ix = cx + int(math.cos(inner_angle) * inner_hex_r)
        iy = cy + int(math.sin(inner_angle) * inner_hex_r * 0.55)
        
        pygame.draw.line(surface, (*core, 25), (ox, oy), (ix, iy), 1)
    
    # ========== 【第三层】旋转魔法阵光环（头顶悬浮） ==========
    halo_center_y = cy - int(h * 0.48)
    halo_radius = int(w * 0.32)
    halo_rotation = t * 2.5
    
    # 光环浮动效果
    halo_float = int(3 * math.sin(t * 1.8))
    halo_center_y += halo_float
    
    # 外圈主环
    pygame.draw.circle(surface, (*halo, 150), (cx, halo_center_y), halo_radius, 3)
    pygame.draw.circle(surface, (*halo, 80), (cx, halo_center_y), halo_radius + 4, 1)
    pygame.draw.circle(surface, (*halo, 40), (cx, halo_center_y), halo_radius + 7, 1)
    
    # 中圈
    mid_halo_r = int(halo_radius * 0.7)
    pygame.draw.circle(surface, (*core, 120), (cx, halo_center_y), mid_halo_r, 2)
    
    # 内圈
    inner_halo_r = int(halo_radius * 0.4)
    pygame.draw.circle(surface, (*core_bright, 100), (cx, halo_center_y), inner_halo_r, 2)
    
    # 符文节点（12个，外圈）
    for i in range(12):
        node_angle = halo_rotation + i * (math.pi / 6)
        node_x = cx + int(math.cos(node_angle) * halo_radius)
        node_y = halo_center_y + int(math.sin(node_angle) * halo_radius)
        
        # 节点脉动
        node_pulse = 4 + int(2 * math.sin(t * 5 + i * 0.5))
        
        # 节点发光（外圈）
        pygame.draw.circle(surface, (*halo_bright, 180), (node_x, node_y), node_pulse + 2)
        pygame.draw.circle(surface, halo, (node_x, node_y), node_pulse)
        pygame.draw.circle(surface, halo_bright, (node_x, node_y), max(1, node_pulse - 2))
    
    # 符文节点（8个，中圈）
    for i in range(8):
        node_angle = -halo_rotation * 0.8 + i * (math.pi / 4)
        node_x = cx + int(math.cos(node_angle) * mid_halo_r)
        node_y = halo_center_y + int(math.sin(node_angle) * mid_halo_r)
        
        node_pulse = 3 + int(1.5 * math.sin(t * 4 + i * 0.7))
        pygame.draw.circle(surface, (*core_bright, 150), (node_x, node_y), node_pulse + 1)
        pygame.draw.circle(surface, core, (node_x, node_y), node_pulse)
    
    # 内部十字图案
    cross_len = int(inner_halo_r * 0.8)
    for i in range(4):
        cross_angle = halo_rotation * 1.5 + i * (math.pi / 2)
        x1 = cx + int(math.cos(cross_angle) * 5)
        y1 = halo_center_y + int(math.sin(cross_angle) * 5)
        x2 = cx + int(math.cos(cross_angle) * cross_len)
        y2 = halo_center_y + int(math.sin(cross_angle) * cross_len)
        pygame.draw.line(surface, (*halo, 120), (x1, y1), (x2, y2), 2)
    
    # 对角连线
    for i in range(4):
        angle1 = halo_rotation + i * (math.pi / 2)
        angle2 = halo_rotation + (i + 1) * (math.pi / 2)
        x1 = cx + int(math.cos(angle1) * inner_halo_r)
        y1 = halo_center_y + int(math.sin(angle1) * inner_halo_r)
        x2 = cx + int(math.cos(angle2) * inner_halo_r)
        y2 = halo_center_y + int(math.sin(angle2) * inner_halo_r)
        pygame.draw.line(surface, (*core, 80), (x1, y1), (x2, y2), 1)
    
    # ========== 【第四层】浮游符文石板阵列（两侧） ==========
    for side in [-1, 1]:
        for slab_idx in range(5):
            # 石板基础位置（阶梯式分布）
            slab_base_x = cx + side * (int(w * 0.48) + slab_idx * 5)
            slab_base_y = cy - int(h * 0.18) + slab_idx * int(h * 0.10)
            
            # 浮动动画（每块石板独立）
            float_phase = t * 2.2 + slab_idx * 0.9 + side * 0.5
            float_x = int(3 * math.sin(float_phase * 0.8))
            float_y = int(5 * math.sin(float_phase))
            
            slab_x = slab_base_x + float_x
            slab_y = slab_base_y + float_y
            
            # 石板尺寸（越远越小）
            slab_w = int(w * 0.14) - slab_idx * 2
            slab_h = int(h * 0.20) - slab_idx * 2
            
            if slab_w > 6 and slab_h > 8:
                # 石板阴影
                shadow_offset = 3
                shadow_pts = [
                    (slab_x - slab_w//2 + shadow_offset, slab_y - slab_h//2 + 4 + shadow_offset),
                    (slab_x - slab_w//2 + 4 + shadow_offset, slab_y - slab_h//2 + shadow_offset),
                    (slab_x + slab_w//2 - 4 + shadow_offset, slab_y - slab_h//2 + shadow_offset),
                    (slab_x + slab_w//2 + shadow_offset, slab_y - slab_h//2 + 4 + shadow_offset),
                    (slab_x + slab_w//2 + shadow_offset, slab_y + slab_h//2 - 4 + shadow_offset),
                    (slab_x + slab_w//2 - 4 + shadow_offset, slab_y + slab_h//2 + shadow_offset),
                    (slab_x - slab_w//2 + 4 + shadow_offset, slab_y + slab_h//2 + shadow_offset),
                    (slab_x - slab_w//2 + shadow_offset, slab_y + slab_h//2 - 4 + shadow_offset),
                ]
                pygame.draw.polygon(surface, (*armor_shadow, 80), shadow_pts)
                
                # 石板主体（八边形切角）
                slab_pts = [
                    (slab_x - slab_w//2, slab_y - slab_h//2 + 4),
                    (slab_x - slab_w//2 + 4, slab_y - slab_h//2),
                    (slab_x + slab_w//2 - 4, slab_y - slab_h//2),
                    (slab_x + slab_w//2, slab_y - slab_h//2 + 4),
                    (slab_x + slab_w//2, slab_y + slab_h//2 - 4),
                    (slab_x + slab_w//2 - 4, slab_y + slab_h//2),
                    (slab_x - slab_w//2 + 4, slab_y + slab_h//2),
                    (slab_x - slab_w//2, slab_y + slab_h//2 - 4),
                ]
                pygame.draw.polygon(surface, obsidian, slab_pts)
                pygame.draw.polygon(surface, armor_light, slab_pts, 2)
                
                # 黑曜石纹理
                for vein in range(3):
                    vein_y = slab_y - slab_h//3 + vein * int(slab_h * 0.3)
                    vein_x1 = slab_x - slab_w//3 + int(5 * math.sin(t + vein + slab_idx))
                    vein_x2 = slab_x + slab_w//3 + int(3 * math.cos(t * 1.3 + vein))
                    pygame.draw.line(surface, (*obsidian_vein, 80), 
                                   (vein_x1, vein_y), (vein_x2, vein_y + 3), 1)
                
                # 中央符文刻痕
                rune_glow_alpha = 180 + int(70 * math.sin(t * 3.5 + slab_idx + side))
                
                # 竖线符文
                pygame.draw.line(surface, (*rune, rune_glow_alpha),
                               (slab_x, slab_y - slab_h//3),
                               (slab_x, slab_y + slab_h//3), 2)
                
                # 横线符文
                pygame.draw.line(surface, (*rune, rune_glow_alpha),
                               (slab_x - slab_w//4, slab_y),
                               (slab_x + slab_w//4, slab_y), 2)
                
                # 符文交点发光
                rune_center_glow = 3 + int(2 * math.sin(t * 4 + slab_idx))
                pygame.draw.circle(surface, rune_glow, (slab_x, slab_y), rune_center_glow)
                
                # 角落小符文
                for corner in range(4):
                    corner_x = slab_x + (1 if corner % 2 == 0 else -1) * (slab_w//3)
                    corner_y = slab_y + (1 if corner < 2 else -1) * (slab_h//3)
                    pygame.draw.circle(surface, (*rune, 120), (corner_x, corner_y), 2)
                
                # 能量连接线（到主体）
                connect_alpha = 80 + int(50 * math.sin(t * 2.5 + slab_idx * 0.7))
                body_connect_x = cx + side * int(w * 0.28)
                body_connect_y = cy + int(h * 0.05)
                
                # 贝塞尔曲线效果（简化为折线）
                mid_x = (slab_x - side * slab_w//2 + body_connect_x) // 2
                mid_y = (slab_y + body_connect_y) // 2 - 10
                
                pygame.draw.line(surface, (*core, connect_alpha),
                               (slab_x - side * slab_w//2, slab_y),
                               (mid_x, mid_y), 1)
                pygame.draw.line(surface, (*core, connect_alpha),
                               (mid_x, mid_y),
                               (body_connect_x, body_connect_y), 1)
                
                # 能量流动粒子
                particle_progress = (t * 2 + slab_idx * 0.5) % 1.0
                particle_x = int(slab_x - side * slab_w//2 + (body_connect_x - slab_x + side * slab_w//2) * particle_progress)
                particle_y = int(slab_y + (body_connect_y - slab_y) * particle_progress)
                pygame.draw.circle(surface, (*core_bright, 200), (particle_x, particle_y), 2)
    
    # ========== 【第五层】倒三角形黑曜石祭坛主体 ==========
    body_top = cy - int(h * 0.30)
    body_bottom = cy + int(h * 0.28)
    body_width = int(w * 0.48)
    
    # 外层轮廓点（倒三角 + 切角 + 肩部突起）
    outer_body_pts = [
        # 顶部
        (cx, body_top - 5),                                      # 顶尖
        (cx + int(body_width * 0.2), body_top),                  # 右顶斜
        (cx + int(body_width * 0.5), body_top + int(h * 0.08)),  # 右肩内
        (cx + int(body_width * 0.7), body_top + int(h * 0.05)),  # 右肩尖
        (cx + body_width, body_top + int(h * 0.15)),             # 右上角
        # 右侧
        (cx + int(body_width * 0.92), body_bottom - int(h * 0.08)),  # 右下角上
        (cx + int(body_width * 0.5), body_bottom - 5),              # 右底角
        # 底部
        (cx + int(body_width * 0.25), body_bottom + 3),           # 右底
        (cx, body_bottom + 8),                                     # 底尖
        (cx - int(body_width * 0.25), body_bottom + 3),           # 左底
        # 左侧
        (cx - int(body_width * 0.5), body_bottom - 5),              # 左底角
        (cx - int(body_width * 0.92), body_bottom - int(h * 0.08)),  # 左下角上
        (cx - body_width, body_top + int(h * 0.15)),             # 左上角
        (cx - int(body_width * 0.7), body_top + int(h * 0.05)),  # 左肩尖
        (cx - int(body_width * 0.5), body_top + int(h * 0.08)),  # 左肩内
        (cx - int(body_width * 0.2), body_top),                  # 左顶斜
    ]
    
    # 主体阴影
    shadow_body_pts = [(px + 4, py + 4) for px, py in outer_body_pts]
    pygame.draw.polygon(surface, armor_shadow, shadow_body_pts)
    
    # 主体外壳
    pygame.draw.polygon(surface, armor, outer_body_pts)
    pygame.draw.polygon(surface, armor_light, outer_body_pts, 3)
    
    # 内层装甲（黑曜石核心）
    inner_scale = 0.72
    inner_body_pts = []
    for px, py in outer_body_pts:
        ix = cx + int((px - cx) * inner_scale)
        iy = cy + int((py - cy) * inner_scale)
        inner_body_pts.append((ix, iy))
    pygame.draw.polygon(surface, obsidian, inner_body_pts)
    pygame.draw.polygon(surface, (*core, 60), inner_body_pts, 2)
    
    # 黑曜石内部纹理
    for vein_idx in range(5):
        vein_angle = t * 0.5 + vein_idx * (math.pi * 2 / 5)
        vein_len = int(w * 0.15) + int(5 * math.sin(t + vein_idx))
        vein_x1 = cx + int(math.cos(vein_angle) * 10)
        vein_y1 = cy + int(math.sin(vein_angle) * 8)
        vein_x2 = cx + int(math.cos(vein_angle) * vein_len)
        vein_y2 = cy + int(math.sin(vein_angle) * vein_len * 0.7)
        pygame.draw.line(surface, (*obsidian_vein, 60), (vein_x1, vein_y1), (vein_x2, vein_y2), 1)
    
    # 装甲分割线（水平）
    for i in range(4):
        line_y = body_top + int((body_bottom - body_top) * (i + 1) / 5)
        line_width_factor = 1 - i * 0.12
        line_width = int(body_width * line_width_factor)
        pygame.draw.line(surface, armor_light, 
                        (cx - line_width, line_y), (cx + line_width, line_y), 1)
    
    # 装甲分割线（斜向）
    for side in [-1, 1]:
        pygame.draw.line(surface, armor_dark,
                        (cx + side * int(body_width * 0.3), body_top + int(h * 0.05)),
                        (cx + side * int(body_width * 0.15), body_bottom - int(h * 0.05)), 1)
    
    # 铆钉装饰
    for side in [-1, 1]:
        for rivet_idx in range(5):
            rivet_x = cx + side * int(body_width * 0.6)
            rivet_y = body_top + int(h * 0.12) + rivet_idx * int(h * 0.08)
            pygame.draw.circle(surface, armor_dark, (rivet_x, rivet_y), 3)
            pygame.draw.circle(surface, armor_light, (rivet_x - 1, rivet_y - 1), 1)
    
    # ========== 【第六层】灾厄之眼核心（中央大眼） ==========
    eye_center_y = cy - int(h * 0.03)
    eye_socket_radius = int(w * 0.20)
    
    # 眼眶机械结构（三层环）
    # 外环 - 装甲环
    pygame.draw.circle(surface, armor_shadow, (cx, eye_center_y), eye_socket_radius + 8)
    pygame.draw.circle(surface, armor_dark, (cx, eye_center_y), eye_socket_radius + 6)
    pygame.draw.circle(surface, armor, (cx, eye_center_y), eye_socket_radius + 4)
    pygame.draw.circle(surface, armor_light, (cx, eye_center_y), eye_socket_radius + 6, 2)
    
    # 中环 - 能量环
    pygame.draw.circle(surface, (*core, 100), (cx, eye_center_y), eye_socket_radius + 2, 3)
    
    # 内环 - 黑曜石边框
    pygame.draw.circle(surface, obsidian, (cx, eye_center_y), eye_socket_radius)
    pygame.draw.circle(surface, armor_light, (cx, eye_center_y), eye_socket_radius, 2)
    
    # 眼眶装饰刻痕
    for i in range(8):
        notch_angle = i * (math.pi / 4) + t * 0.3
        notch_x1 = cx + int(math.cos(notch_angle) * (eye_socket_radius - 2))
        notch_y1 = eye_center_y + int(math.sin(notch_angle) * (eye_socket_radius - 2))
        notch_x2 = cx + int(math.cos(notch_angle) * (eye_socket_radius + 5))
        notch_y2 = eye_center_y + int(math.sin(notch_angle) * (eye_socket_radius + 5))
        pygame.draw.line(surface, armor_dark, (notch_x1, notch_y1), (notch_x2, notch_y2), 2)
    
    # 眼球底层（深黑）
    eyeball_radius = int(eye_socket_radius * 0.88)
    pygame.draw.circle(surface, (15, 5, 8), (cx, eye_center_y), eyeball_radius)
    
    # 眼球脉动效果
    eye_pulse = 1 + 0.18 * math.sin(t * 4.5)
    pulse_radius = int(eyeball_radius * eye_pulse)
    
    # 血丝纹理
    for vein in range(12):
        vein_angle = vein * (math.pi / 6) + t * 0.2
        vein_length = int(eyeball_radius * (0.5 + 0.3 * math.sin(t * 2 + vein)))
        vein_x1 = cx + int(math.cos(vein_angle) * eyeball_radius * 0.3)
        vein_y1 = eye_center_y + int(math.sin(vein_angle) * eyeball_radius * 0.3)
        vein_x2 = cx + int(math.cos(vein_angle) * vein_length)
        vein_y2 = eye_center_y + int(math.sin(vein_angle) * vein_length)
        pygame.draw.line(surface, (*core_dark, 80), (vein_x1, vein_y1), (vein_x2, vein_y2), 1)
    
    # 虹膜（多层渐变）
    iris_radius = int(pulse_radius * 0.78)
    for layer in range(6):
        layer_radius = iris_radius - layer * 3
        if layer_radius > 0:
            layer_alpha = 255 - layer * 30
            layer_color = (
                int(core[0] + (core_bright[0] - core[0]) * layer / 6),
                int(core[1] + (core_bright[1] - core[1]) * layer / 6),
                int(core[2] + (core_bright[2] - core[2]) * layer / 6),
            )
            pygame.draw.circle(surface, (*layer_color, layer_alpha), (cx, eye_center_y), layer_radius)
    
    # 虹膜纹理（径向线条）
    for i in range(24):
        iris_line_angle = i * (math.pi / 12) + t * 0.5
        iris_x1 = cx + int(math.cos(iris_line_angle) * (iris_radius * 0.3))
        iris_y1 = eye_center_y + int(math.sin(iris_line_angle) * (iris_radius * 0.3))
        iris_x2 = cx + int(math.cos(iris_line_angle) * (iris_radius - 2))
        iris_y2 = eye_center_y + int(math.sin(iris_line_angle) * (iris_radius - 2))
        pygame.draw.line(surface, (*core_dark, 100), (iris_x1, iris_y1), (iris_x2, iris_y2), 1)
    
    # 瞳孔
    pupil_radius = int(iris_radius * 0.38)
    pygame.draw.circle(surface, (5, 0, 0), (cx, eye_center_y), pupil_radius + 3)
    pygame.draw.circle(surface, (0, 0, 0), (cx, eye_center_y), pupil_radius + 1)
    pygame.draw.circle(surface, eye_color, (cx, eye_center_y), pupil_radius)
    
    # 瞳孔内部花纹
    for i in range(6):
        inner_angle = i * (math.pi / 3) + t * 2
        inner_x = cx + int(math.cos(inner_angle) * pupil_radius * 0.5)
        inner_y = eye_center_y + int(math.sin(inner_angle) * pupil_radius * 0.5)
        pygame.draw.circle(surface, (*eye_glow, 150), (inner_x, inner_y), 2)
    
    # 瞳孔核心亮点
    pygame.draw.circle(surface, eye_glow, (cx, eye_center_y), max(1, pupil_radius // 3))
    
    # 眼球高光（多个）
    highlight_offset_x = int(iris_radius * 0.35)
    highlight_offset_y = int(iris_radius * 0.35)
    pygame.draw.circle(surface, (255, 220, 220), (cx - highlight_offset_x, eye_center_y - highlight_offset_y), 4)
    pygame.draw.circle(surface, (255, 255, 255), (cx - highlight_offset_x + 1, eye_center_y - highlight_offset_y + 1), 2)
    # 次高光
    pygame.draw.circle(surface, (255, 200, 200), (cx + highlight_offset_x // 2, eye_center_y + highlight_offset_y // 2), 2)
    
    # 眼球周围能量涟漪
    for ripple in range(4):
        ripple_radius = eye_socket_radius + 8 + ripple * 6 + int(4 * math.sin(t * 3.5 - ripple * 0.5))
        ripple_alpha = max(0, 100 - ripple * 25)
        if ripple_alpha > 0:
            pygame.draw.circle(surface, (*hellfire, ripple_alpha), (cx, eye_center_y), ripple_radius, 1)
    
    # 能量弧光
    for arc in range(3):
        arc_start = t * 2 + arc * (math.pi * 2 / 3)
        arc_end = arc_start + math.pi * 0.4
        arc_radius = eye_socket_radius + 12 + arc * 4
        arc_rect = (cx - arc_radius, eye_center_y - arc_radius, arc_radius * 2, arc_radius * 2)
        pygame.draw.arc(surface, (*core_bright, 150), arc_rect, arc_start, arc_end, 2)
    
    # ========== 【第七层】眼睫状机械护栏尖刺 ==========
    spike_count = 16
    spike_base_radius = eye_socket_radius + 8
    spike_length = int(w * 0.10)
    
    for i in range(spike_count):
        spike_angle = math.radians(i * (360 / spike_count)) + t * 0.08
        
        # 只在上半部分绘制睫毛状尖刺
        angle_sin = math.sin(spike_angle)
        if angle_sin < 0.35:
            # 尖刺基部位置
            base_x = cx + int(math.cos(spike_angle) * spike_base_radius)
            base_y = eye_center_y + int(math.sin(spike_angle) * spike_base_radius)
            
            # 尖刺长度随角度变化（顶部最长）
            length_factor = 1.0 - abs(angle_sin) * 0.5
            current_spike_len = int(spike_length * length_factor)
            
            # 尖刺尖端位置
            tip_x = cx + int(math.cos(spike_angle) * (spike_base_radius + current_spike_len))
            tip_y = eye_center_y + int(math.sin(spike_angle) * (spike_base_radius + current_spike_len))
            
            # 尖刺宽度
            perp_angle = spike_angle + math.pi / 2
            half_width = 4
            
            # 尖刺形状（三角形）
            spike_pts = [
                (int(base_x + math.cos(perp_angle) * half_width),
                 int(base_y + math.sin(perp_angle) * half_width)),
                (int(tip_x), int(tip_y)),
                (int(base_x - math.cos(perp_angle) * half_width),
                 int(base_y - math.sin(perp_angle) * half_width)),
            ]
            
            # 绘制尖刺
            pygame.draw.polygon(surface, armor, spike_pts)
            pygame.draw.polygon(surface, armor_light, spike_pts, 1)
            
            # 尖刺中线
            pygame.draw.line(surface, armor_dark, (base_x, base_y), (tip_x, tip_y), 1)
            
            # 尖刺尖端发光
            tip_glow_size = 3 + int(2 * math.sin(t * 6 + i * 0.5))
            pygame.draw.circle(surface, (*hellfire, 220), (int(tip_x), int(tip_y)), tip_glow_size)
            pygame.draw.circle(surface, hellfire_bright, (int(tip_x), int(tip_y)), max(1, tip_glow_size - 2))
            
            # 基部关节
            pygame.draw.circle(surface, armor_dark, (base_x, base_y), 3)
            pygame.draw.circle(surface, armor_light, (base_x - 1, base_y - 1), 1)
    
    # ========== 【第八层】机械骷髅长尾浮游炮 ==========
    tail_start_y = body_bottom + 10
    tail_segments = 10
    
    for seg_idx in range(tail_segments):
        # 蛇形波动运动
        wave_phase = t * 2.8 + seg_idx * 0.55
        wave_offset_x = int(10 * math.sin(wave_phase))
        wave_offset_y = int(3 * math.cos(wave_phase * 0.7))
        
        seg_x = cx + wave_offset_x
        seg_y = tail_start_y + seg_idx * int(h * 0.065) + wave_offset_y
        
        # 骷髅尺寸递减
        skull_size = max(5, int(w * 0.09) - seg_idx)
        
        # 骷髅阴影
        pygame.draw.circle(surface, (*armor_shadow, 100), (seg_x + 2, seg_y + 2), skull_size + 1)
        
        # 骷髅头轮廓
        pygame.draw.circle(surface, skull, (seg_x, seg_y), skull_size + 1)
        pygame.draw.circle(surface, skull_dark, (seg_x, seg_y), skull_size - 1)
        pygame.draw.circle(surface, skull, (seg_x, seg_y), skull_size, 2)
        
        # 颅骨顶部凸起
        pygame.draw.ellipse(surface, skull, 
                           (seg_x - skull_size + 2, seg_y - skull_size - 2, 
                            (skull_size - 2) * 2, skull_size))
        
        # 眼窝（双眼）
        eye_offset_x = max(2, skull_size // 3)
        eye_offset_y = max(1, skull_size // 5)
        eye_size = max(2, skull_size // 3)
        
        # 左眼窝
        pygame.draw.circle(surface, (0, 0, 0), (seg_x - eye_offset_x, seg_y - eye_offset_y), eye_size + 1)
        # 右眼窝
        pygame.draw.circle(surface, (0, 0, 0), (seg_x + eye_offset_x, seg_y - eye_offset_y), eye_size + 1)
        
        # 眼中火焰
        eye_flame_size = max(1, eye_size - 1) + int(math.sin(t * 6 + seg_idx) * 1.5)
        flame_alpha = 200 + int(50 * math.sin(t * 5 + seg_idx * 0.8))
        
        pygame.draw.circle(surface, (*core, flame_alpha), (seg_x - eye_offset_x, seg_y - eye_offset_y), eye_flame_size)
        pygame.draw.circle(surface, (*core, flame_alpha), (seg_x + eye_offset_x, seg_y - eye_offset_y), eye_flame_size)
        
        # 眼火高亮
        pygame.draw.circle(surface, core_bright, (seg_x - eye_offset_x, seg_y - eye_offset_y - 1), max(1, eye_flame_size // 2))
        pygame.draw.circle(surface, core_bright, (seg_x + eye_offset_x, seg_y - eye_offset_y - 1), max(1, eye_flame_size // 2))
        
        # 鼻孔
        nose_y = seg_y + max(1, skull_size // 6)
        pygame.draw.polygon(surface, (0, 0, 0), [
            (seg_x, nose_y - 2),
            (seg_x - 2, nose_y + 2),
            (seg_x + 2, nose_y + 2),
        ])
        
        # 牙齿（下部）
        teeth_y = seg_y + skull_size // 2
        teeth_width = skull_size - 2
        if teeth_width > 4:
            for tooth in range(max(2, teeth_width // 3)):
                tooth_x = seg_x - teeth_width // 2 + tooth * 3 + 1
                pygame.draw.rect(surface, (200, 200, 200), (tooth_x, teeth_y, 2, 3))
        
        # 机械装饰（螺栓）
        if skull_size > 6:
            for bolt_side in [-1, 1]:
                bolt_x = seg_x + bolt_side * (skull_size - 2)
                pygame.draw.circle(surface, armor_dark, (bolt_x, seg_y), 2)
        
        # 连接链
        if seg_idx > 0:
            prev_wave_x = int(10 * math.sin(t * 2.8 + (seg_idx - 1) * 0.55))
            prev_wave_y = int(3 * math.cos((t * 2.8 + (seg_idx - 1) * 0.55) * 0.7))
            prev_x = cx + prev_wave_x
            prev_y = tail_start_y + (seg_idx - 1) * int(h * 0.065) + prev_wave_y
            
            # 链条主体
            pygame.draw.line(surface, skull, (prev_x, prev_y), (seg_x, seg_y), 3)
            pygame.draw.line(surface, skull_dark, (prev_x, prev_y), (seg_x, seg_y), 1)
            
            # 链节装饰
            mid_x = (prev_x + seg_x) // 2
            mid_y = (prev_y + seg_y) // 2
            pygame.draw.circle(surface, armor_dark, (mid_x, mid_y), 2)
        
        # 能量流动（从主体到尾部）
        if seg_idx % 3 == 0:
            flow_alpha = 100 + int(80 * math.sin(t * 4 + seg_idx))
            pygame.draw.circle(surface, (*core, flow_alpha), (seg_x, seg_y), skull_size + 3, 1)
    
    # ========== 【第九层】哥特式尖刺冠与侧翼 ==========
    # 顶部尖刺冠
    crown_base_y = body_top - 8
    
    for spike_idx in range(-3, 4):
        spike_x = cx + spike_idx * int(w * 0.08)
        # 中间最高，两边递减
        spike_height = int(h * 0.12) - abs(spike_idx) * 5
        
        if spike_height > 5:
            # 尖刺阴影
            pygame.draw.polygon(surface, (*armor_shadow, 120), [
                (spike_x - 4 + 2, crown_base_y + 2),
                (spike_x + 2, crown_base_y - spike_height + 2),
                (spike_x + 4 + 2, crown_base_y + 2),
            ])
            
            # 尖刺主体
            pygame.draw.polygon(surface, armor, [
                (spike_x - 4, crown_base_y),
                (spike_x, crown_base_y - spike_height),
                (spike_x + 4, crown_base_y),
            ])
            pygame.draw.polygon(surface, armor_light, [
                (spike_x - 4, crown_base_y),
                (spike_x, crown_base_y - spike_height),
                (spike_x + 4, crown_base_y),
            ], 1)
            
            # 尖刺中线
            pygame.draw.line(surface, armor_dark, 
                           (spike_x, crown_base_y), 
                           (spike_x, crown_base_y - spike_height), 1)
            
            # 尖刺尖端宝石
            gem_glow = 3 + int(2 * math.sin(t * 4 + spike_idx))
            pygame.draw.circle(surface, (*core, 200), (spike_x, crown_base_y - spike_height), gem_glow)
            pygame.draw.circle(surface, core_bright, (spike_x, crown_base_y - spike_height), max(1, gem_glow - 2))
    
    # 侧翼装饰
    for side in [-1, 1]:
        wing_base_x = cx + side * int(body_width * 0.95)
        wing_base_y = cy - int(h * 0.05)
        
        # 翼根
        pygame.draw.circle(surface, armor_dark, (wing_base_x, wing_base_y), 5)
        pygame.draw.circle(surface, armor, (wing_base_x, wing_base_y), 4)
        
        # 主翼（三角形）
        wing_pts = [
            (wing_base_x, wing_base_y - 12),
            (wing_base_x + side * 20, wing_base_y),
            (wing_base_x, wing_base_y + 12),
        ]
        pygame.draw.polygon(surface, armor, wing_pts)
        pygame.draw.polygon(surface, armor_light, wing_pts, 2)
        
        # 翼内装饰线
        pygame.draw.line(surface, armor_dark, 
                        (wing_base_x, wing_base_y - 8),
                        (wing_base_x + side * 12, wing_base_y), 1)
        pygame.draw.line(surface, armor_dark,
                        (wing_base_x, wing_base_y + 8),
                        (wing_base_x + side * 12, wing_base_y), 1)
        
        # 翼尖发光
        wing_tip_x = wing_base_x + side * 20
        wing_glow = 3 + int(2 * math.sin(t * 3.5 + side))
        pygame.draw.circle(surface, (*hellfire, 180), (wing_tip_x, wing_base_y), wing_glow)
        
        # 副翼（上下小翼）
        for sub_wing in [-1, 1]:
            sub_y = wing_base_y + sub_wing * 18
            sub_pts = [
                (wing_base_x, sub_y),
                (wing_base_x + side * 12, sub_y + sub_wing * 3),
                (wing_base_x, sub_y + sub_wing * 6),
            ]
            pygame.draw.polygon(surface, armor_dark, sub_pts)
            pygame.draw.polygon(surface, armor_light, sub_pts, 1)
    
    # ========== 【第十层】能量管道与细节装饰 ==========
    # 主能量管道（从核心到各部位）
    for side in [-1, 1]:
        # 管道到肩部
        pipe_start = (cx + side * int(w * 0.08), cy - int(h * 0.15))
        pipe_mid = (cx + side * int(w * 0.25), cy - int(h * 0.08))
        pipe_end = (cx + side * int(body_width * 0.7), body_top + int(h * 0.08))
        
        # 管道阴影
        pygame.draw.line(surface, armor_shadow, pipe_start, pipe_mid, 5)
        pygame.draw.line(surface, armor_shadow, pipe_mid, pipe_end, 4)
        
        # 管道主体
        pygame.draw.line(surface, armor_dark, pipe_start, pipe_mid, 4)
        pygame.draw.line(surface, armor_dark, pipe_mid, pipe_end, 3)
        
        # 管道高亮
        pygame.draw.line(surface, armor_light, pipe_start, pipe_mid, 1)
        
        # 能量流动
        flow_progress = (t * 1.5 + side * 0.3) % 1.0
        flow_x = int(pipe_start[0] + (pipe_end[0] - pipe_start[0]) * flow_progress)
        flow_y = int(pipe_start[1] + (pipe_end[1] - pipe_start[1]) * flow_progress)
        pygame.draw.circle(surface, (*core, 180), (flow_x, flow_y), 3)
        pygame.draw.circle(surface, core_bright, (flow_x, flow_y), 2)
        
        # 管道到尾部
        tail_pipe_start = (cx + side * int(w * 0.05), cy + int(h * 0.15))
        tail_pipe_end = (cx + side * int(w * 0.02), body_bottom + 5)
        pygame.draw.line(surface, armor_dark, tail_pipe_start, tail_pipe_end, 3)
        pygame.draw.line(surface, (*core, 60), tail_pipe_start, tail_pipe_end, 1)
    
    # 中央能量核心装饰
    core_deco_y = cy + int(h * 0.12)
    pygame.draw.ellipse(surface, armor_dark, 
                       (cx - 8, core_deco_y - 5, 16, 10))
    pygame.draw.ellipse(surface, (*core, 150),
                       (cx - 6, core_deco_y - 3, 12, 6))
    
    # 底部推进器暗示
    thruster_y = body_bottom + 5
    for i in range(-1, 2):
        thruster_x = cx + i * int(w * 0.12)
        # 推进器口
        pygame.draw.ellipse(surface, armor_shadow,
                           (thruster_x - 6, thruster_y - 3, 12, 8))
        pygame.draw.ellipse(surface, armor_dark,
                           (thruster_x - 5, thruster_y - 2, 10, 6))
        # 推进火焰
        flame_len = 8 + int(5 * math.sin(t * 8 + i))
        flame_alpha = 150 + int(80 * math.sin(t * 6 + i * 0.5))
        pygame.draw.polygon(surface, (*hellfire, flame_alpha), [
            (thruster_x - 4, thruster_y + 2),
            (thruster_x, thruster_y + flame_len),
            (thruster_x + 4, thruster_y + 2),
        ])
        pygame.draw.polygon(surface, (*core, flame_alpha), [
            (thruster_x - 2, thruster_y + 2),
            (thruster_x, thruster_y + flame_len - 3),
            (thruster_x + 2, thruster_y + 2),
        ])
    
    # 漂浮粒子效果
    for particle in range(8):
        particle_angle = t * 1.2 + particle * (math.pi / 4)
        particle_dist = 50 + int(15 * math.sin(t * 2 + particle))
        particle_x = cx + int(math.cos(particle_angle) * particle_dist)
        particle_y = cy + int(math.sin(particle_angle) * particle_dist * 0.6)
        particle_size = 2 + int(math.sin(t * 4 + particle) * 1.5)
        particle_alpha = 120 + int(80 * math.sin(t * 3 + particle * 0.7))
        pygame.draw.circle(surface, (*magic, particle_alpha), (particle_x, particle_y), particle_size)


# ==================== 涂装专属特效函数 ====================
def _draw_theme_effects(surface, x, y, w, h, frame, theme, variant):
    """绘制各涂装专属的特殊效果 - 大幅差异化"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.04
    
    core = theme["core"]
    core_bright = theme["core_bright"]
    hellfire = theme["hellfire"]
    hellfire_bright = theme["hellfire_bright"]
    magic = theme["magic"]
    halo = theme["halo"]
    rune = theme["rune"]
    
    if variant == "default":
        # 默认 - 灾厄之眼血泪 + 猩红血雾 + 灾厄徽章 + 血脉纹路 + 猩红触须
        # 血泪从眼睛流下
        eye_y = cy - int(h * 0.03)
        for tear in range(3):
            tear_progress = (t * 0.6 + tear * 0.33) % 1.0
            tear_x = cx + (tear - 1) * 8
            tear_y = eye_y + int(tear_progress * h * 0.45)
            tear_size = 4 - int(tear_progress * 2)
            if tear_size > 1:
                # 血泪形状
                pygame.draw.ellipse(surface, (*core, 220), (tear_x - 2, tear_y, 4, tear_size * 2 + 3))
                pygame.draw.circle(surface, (*hellfire, 180), (tear_x, tear_y + tear_size), 2)
        
        # 血雾环绕
        for mist in range(6):
            mist_angle = t * 0.8 + mist * (math.pi / 3)
            mist_dist = 45 + int(12 * math.sin(t * 1.5 + mist))
            mist_x = cx + int(math.cos(mist_angle) * mist_dist)
            mist_y = cy + int(math.sin(mist_angle) * mist_dist * 0.5)
            mist_size = 14 + int(6 * math.sin(t * 2 + mist))
            mist_surf = pygame.Surface((mist_size * 2, mist_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(mist_surf, (*core, 40), (mist_size, mist_size), mist_size)
            surface.blit(mist_surf, (mist_x - mist_size, mist_y - mist_size))
        
        # 灾厄徽章（顶部）
        badge_y = cy - int(h * 0.42)
        badge_r = 12 + int(3 * math.sin(t * 2))
        pygame.draw.circle(surface, (*core, 150), (cx, badge_y), badge_r, 2)
        # 徽章内的灾厄符号
        pygame.draw.line(surface, (*hellfire, 200), (cx - 6, badge_y - 4), (cx + 6, badge_y + 4), 2)
        pygame.draw.line(surface, (*hellfire, 200), (cx + 6, badge_y - 4), (cx - 6, badge_y + 4), 2)
        pygame.draw.circle(surface, hellfire_bright, (cx, badge_y), 3)
        
        # ★新增：血脉纹路（从中心向外扩散）
        for vein in range(8):
            vein_angle = vein * (math.pi / 4) + t * 0.3
            # 主血管
            for seg in range(6):
                seg_start = 15 + seg * 8
                seg_end = seg_start + 8
                wave = int(2 * math.sin(t * 4 + seg * 0.5 + vein))
                vx1 = cx + int(math.cos(vein_angle + wave * 0.05) * seg_start)
                vy1 = cy + int(math.sin(vein_angle + wave * 0.05) * seg_start * 0.5)
                vx2 = cx + int(math.cos(vein_angle + wave * 0.05) * seg_end)
                vy2 = cy + int(math.sin(vein_angle + wave * 0.05) * seg_end * 0.5)
                vein_alpha = 150 - seg * 20
                vein_thick = max(1, 3 - seg // 2)
                if vein_alpha > 0:
                    pygame.draw.line(surface, (*core, vein_alpha), (vx1, vy1), (vx2, vy2), vein_thick)
        
        # ★新增：猩红触须（底部伸出）
        for tentacle in range(5):
            t_x = cx - int(w * 0.25) + tentacle * int(w * 0.13)
            t_base_y = cy + int(h * 0.25)
            prev_x, prev_y = t_x, t_base_y
            for seg in range(8):
                seg_wave = math.sin(t * 3 + tentacle * 0.8 + seg * 0.4) * (seg * 1.5)
                seg_x = prev_x + int(seg_wave)
                seg_y = prev_y + 6
                seg_alpha = 180 - seg * 18
                seg_thick = max(1, 4 - seg // 2)
                if seg_alpha > 0:
                    pygame.draw.line(surface, (*core, seg_alpha), (prev_x, prev_y), (seg_x, seg_y), seg_thick)
                prev_x, prev_y = seg_x, seg_y
            # 触须尖端吸盘
            pygame.draw.circle(surface, (*hellfire, 150), (prev_x, prev_y), 3)
        
        # ★新增：灾厄核心（胸口发光宝石）
        gem_y = cy - int(h * 0.1)
        gem_pulse = 1.0 + 0.3 * math.sin(t * 4)
        gem_r = int(10 * gem_pulse)
        # 宝石光晕
        for glow in range(4):
            pygame.draw.circle(surface, (*hellfire, 60 - glow * 15), (cx, gem_y), gem_r + glow * 5)
        # 宝石本体
        pygame.draw.polygon(surface, (*hellfire_bright, 220),
                          [(cx, gem_y - gem_r), (cx - gem_r, gem_y), (cx, gem_y + gem_r), (cx + gem_r, gem_y)])
        pygame.draw.polygon(surface, (*core_bright, 180),
                          [(cx, gem_y - gem_r), (cx - gem_r, gem_y), (cx, gem_y + gem_r), (cx + gem_r, gem_y)], 2)
    
    elif variant == "brimstone":
        # 硫磺炼狱 - 地狱火柱 + 硫磺骷髅 + 火山喷发 + 熔岩铠甲 + 恶魔之角
        # 两侧地狱火柱
        for side in [-1, 1]:
            pillar_x = cx + side * int(w * 0.38)
            pillar_h = int(h * 0.6)
            pillar_w = 12
            # 火柱本体
            for layer in range(pillar_h // 4):
                layer_y = cy + int(h * 0.2) - layer * 4
                layer_w = pillar_w - layer // 4
                layer_alpha = 150 - layer * 2
                wave = int(3 * math.sin(t * 5 + layer * 0.3))
                if layer_w > 0 and layer_alpha > 0:
                    pygame.draw.rect(surface, (*hellfire, layer_alpha),
                                   (pillar_x - layer_w // 2 + wave, layer_y, layer_w, 5))
            # 火柱顶端火焰
            flame_y = cy + int(h * 0.2) - pillar_h
            for flame in range(5):
                flame_h = 8 + int(6 * math.sin(t * 6 + flame))
                flame_x = pillar_x + (flame - 2) * 3
                pygame.draw.polygon(surface, (*hellfire_bright, 200),
                                  [(flame_x, flame_y), (flame_x - 3, flame_y + flame_h), (flame_x + 3, flame_y + flame_h)])
        
        # 硫磺骷髅漂浮
        for skull in range(3):
            skull_angle = t * 0.8 + skull * (math.pi * 2 / 3)
            skull_dist = 35 + int(8 * math.sin(t * 1.5 + skull))
            skull_x = cx + int(math.cos(skull_angle) * skull_dist)
            skull_y = cy - int(h * 0.1) + int(math.sin(skull_angle) * skull_dist * 0.3)
            # 骷髅头轮廓
            pygame.draw.circle(surface, (*hellfire, 180), (skull_x, skull_y), 8)
            pygame.draw.circle(surface, (40, 20, 10), (skull_x, skull_y), 6)
            # 眼睛
            pygame.draw.circle(surface, hellfire_bright, (skull_x - 2, skull_y - 1), 2)
            pygame.draw.circle(surface, hellfire_bright, (skull_x + 2, skull_y - 1), 2)
            # 牙齿
            pygame.draw.line(surface, (*hellfire, 200), (skull_x - 3, skull_y + 4), (skull_x + 3, skull_y + 4), 1)
        
        # 底部岩浆池
        lava_y = cy + int(h * 0.32)
        for bubble in range(8):
            bubble_x = cx - int(w * 0.3) + bubble * int(w * 0.1)
            bubble_pop = (t * 3 + bubble * 0.4) % 1.0
            bubble_y = lava_y - int(bubble_pop * 15)
            bubble_size = int(5 * (1 - bubble_pop))
            if bubble_size > 0:
                pygame.draw.circle(surface, (*hellfire_bright, 220), (bubble_x, bubble_y), bubble_size)
        
        # ★新增：恶魔之角（头顶两侧）
        for side in [-1, 1]:
            horn_base_x = cx + side * int(w * 0.18)
            horn_base_y = cy - int(h * 0.35)
            horn_len = 25 + int(5 * math.sin(t * 2))
            horn_angle = side * 0.4 - math.pi / 2
            # 角的曲线
            for seg in range(10):
                seg_t = seg / 9
                curve = side * seg_t * 0.6
                seg_x = horn_base_x + int(math.cos(horn_angle + curve) * seg_t * horn_len)
                seg_y = horn_base_y + int(math.sin(horn_angle + curve) * seg_t * horn_len)
                seg_r = int(5 * (1 - seg_t * 0.7))
                if seg_r > 0:
                    pygame.draw.circle(surface, (60, 20, 10), (seg_x, seg_y), seg_r)
                    # 角上的纹路发光
                    if seg % 3 == 0:
                        pygame.draw.circle(surface, (*hellfire, 150), (seg_x, seg_y), seg_r - 1)
        
        # ★新增：熔岩铠甲纹路
        armor_y_positions = [cy - int(h * 0.15), cy, cy + int(h * 0.12)]
        for i, ay in enumerate(armor_y_positions):
            armor_w = int(w * (0.3 - i * 0.05))
            # 熔岩裂缝
            for crack in range(3):
                crack_x = cx - armor_w + crack * armor_w
                crack_end_y = ay + 15 + int(5 * math.sin(t * 3 + crack))
                pygame.draw.line(surface, (*hellfire, 180), (crack_x, ay), (crack_x + 5, crack_end_y), 2)
                pygame.draw.line(surface, (*hellfire_bright, 120), (crack_x + 1, ay + 2), (crack_x + 4, crack_end_y - 2), 1)
        
        # ★新增：地狱火环
        fire_ring_r = 55 + int(5 * math.sin(t * 2))
        for fr in range(20):
            fr_angle = fr * (math.pi / 10) + t * 1.5
            fr_x = cx + int(math.cos(fr_angle) * fire_ring_r)
            fr_y = cy + int(math.sin(fr_angle) * fire_ring_r * 0.35)
            fr_h = 8 + int(5 * math.sin(t * 6 + fr))
            # 小火焰
            pygame.draw.polygon(surface, (*hellfire, 150),
                              [(fr_x, fr_y - fr_h), (fr_x - 3, fr_y), (fr_x + 3, fr_y)])
            pygame.draw.polygon(surface, (*hellfire_bright, 100),
                              [(fr_x, fr_y - fr_h + 2), (fr_x - 2, fr_y - 1), (fr_x + 2, fr_y - 1)])
        
        # ★新增：硫磺结晶（底部）
        for crystal in range(4):
            c_x = cx - int(w * 0.25) + crystal * int(w * 0.18)
            c_y = cy + int(h * 0.28)
            c_h = 18 + int(5 * math.sin(t * 2 + crystal))
            c_w = 6
            # 结晶体
            pygame.draw.polygon(surface, (180, 160, 50),
                              [(c_x, c_y - c_h), (c_x - c_w, c_y), (c_x + c_w, c_y)])
            # 结晶光泽
            pygame.draw.line(surface, (220, 200, 100), (c_x - 2, c_y - c_h + 5), (c_x - 1, c_y - 5), 1)
    
    elif variant == "witch":
        # 深渊女巫 - 女巫帽 + 魔法药瓶 + 飞行扫帚 + 五芒星 + 魔法书 + 黑猫 + 咒术符文
        # 女巫帽（顶部）
        hat_y = cy - int(h * 0.48)
        hat_w = 28
        # 帽檐
        pygame.draw.ellipse(surface, (*core, 200), (cx - hat_w // 2, hat_y + 15, hat_w, 8))
        # 帽身（三角形）
        pygame.draw.polygon(surface, (*core, 180),
                          [(cx, hat_y - 20), (cx - 12, hat_y + 18), (cx + 12, hat_y + 18)])
        # 帽尖弯曲
        pygame.draw.arc(surface, core_bright, (cx - 5, hat_y - 25, 20, 15), math.pi * 0.3, math.pi * 1.2, 2)
        # 帽带
        pygame.draw.line(surface, (*magic, 200), (cx - 10, hat_y + 12), (cx + 10, hat_y + 12), 2)
        # 帽带装饰（星星）
        pygame.draw.circle(surface, magic, (cx, hat_y + 12), 3)
        
        # 两侧飞行药瓶
        for side in [-1, 1]:
            bottle_x = cx + side * int(w * 0.35)
            bottle_y = cy + int(5 * math.sin(t * 2 + side))
            # 瓶身
            pygame.draw.ellipse(surface, (*core, 150), (bottle_x - 5, bottle_y - 6, 10, 14))
            # 瓶颈
            pygame.draw.rect(surface, (*core, 180), (bottle_x - 2, bottle_y - 10, 4, 5))
            # 瓶塞
            pygame.draw.rect(surface, (*magic, 200), (bottle_x - 3, bottle_y - 12, 6, 3))
            # 药水发光
            glow_alpha = 150 + int(80 * math.sin(t * 3 + side))
            pygame.draw.ellipse(surface, (*magic, glow_alpha), (bottle_x - 3, bottle_y - 2, 6, 8))
            # 气泡
            for bubble in range(2):
                b_y = bottle_y - 4 + int((t * 2 + bubble) % 1.0 * 8)
                pygame.draw.circle(surface, (*core_bright, 180), (bottle_x + (bubble - 1) * 2, b_y), 1)
        
        # 底部扫帚
        broom_y = cy + int(h * 0.28)
        broom_angle = math.sin(t * 1.5) * 0.2
        # 扫帚柄
        broom_len = int(w * 0.5)
        broom_end_x = cx + int(math.cos(broom_angle) * broom_len // 2)
        broom_end_y = broom_y + int(math.sin(broom_angle) * 10)
        pygame.draw.line(surface, (139, 90, 43), (cx - int(math.cos(broom_angle) * broom_len // 2), broom_y - int(math.sin(broom_angle) * 10)), (broom_end_x, broom_end_y), 3)
        # 扫帚头
        for bristle in range(7):
            b_angle = broom_angle + (bristle - 3) * 0.15
            b_len = 12 + int(4 * math.sin(t * 4 + bristle))
            pygame.draw.line(surface, (180, 120, 60, 180),
                           (broom_end_x, broom_end_y),
                           (broom_end_x + int(math.cos(b_angle) * b_len), broom_end_y + int(math.sin(b_angle) * b_len) + b_len // 2), 2)
        
        # 魔法五芒星（环绕）
        star_dist = 50 + int(5 * math.sin(t * 1.5))
        for star_i in range(5):
            star_angle = t * 0.6 + star_i * (math.pi * 2 / 5)
            star_x = cx + int(math.cos(star_angle) * star_dist)
            star_y = cy + int(math.sin(star_angle) * star_dist * 0.4)
            star_r = 6
            # 绘制小五芒星
            for i in range(5):
                a1 = -math.pi/2 + i * (math.pi * 2 / 5)
                a2 = -math.pi/2 + ((i + 2) % 5) * (math.pi * 2 / 5)
                x1, y1 = star_x + int(math.cos(a1) * star_r), star_y + int(math.sin(a1) * star_r)
                x2, y2 = star_x + int(math.cos(a2) * star_r), star_y + int(math.sin(a2) * star_r)
                pygame.draw.line(surface, (*core_bright, 180), (x1, y1), (x2, y2), 1)
        
        # ★新增：魔法书（浮空打开）
        book_x = cx - int(w * 0.5)
        book_y = cy - int(h * 0.1) + int(6 * math.sin(t * 1.8))
        book_rot = math.sin(t * 1.2) * 0.15
        # 书本打开状态
        pygame.draw.rect(surface, (80, 50, 30), (book_x - 15, book_y - 12, 30, 24))  # 封面
        pygame.draw.rect(surface, (220, 210, 180), (book_x - 12, book_y - 10, 12, 20))  # 左页
        pygame.draw.rect(surface, (230, 220, 190), (book_x, book_y - 10, 12, 20))  # 右页
        # 书脊
        pygame.draw.line(surface, (60, 40, 20), (book_x, book_y - 12), (book_x, book_y + 12), 2)
        # 魔法文字发光
        for text_line in range(4):
            pygame.draw.line(surface, (*magic, 120 + int(50 * math.sin(t * 4 + text_line))),
                           (book_x - 10, book_y - 6 + text_line * 4), (book_x - 3, book_y - 6 + text_line * 4), 1)
            pygame.draw.line(surface, (*magic, 120 + int(50 * math.sin(t * 4 + text_line + 0.5))),
                           (book_x + 2, book_y - 6 + text_line * 4), (book_x + 10, book_y - 6 + text_line * 4), 1)
        # 书本发出的魔法粒子
        for p in range(5):
            p_angle = t * 2 + p * (math.pi * 2 / 5)
            p_dist = 12 + int(8 * (t * 0.5 + p * 0.2) % 1.0)
            px = book_x + int(math.cos(p_angle) * p_dist)
            py = book_y + int(math.sin(p_angle) * p_dist * 0.6) - 5
            pygame.draw.circle(surface, (*magic, 180), (px, py), 2)
        
        # ★新增：黑猫（坐在扫帚上）
        cat_x = cx - int(w * 0.15)
        cat_y = broom_y - 8
        # 猫身体
        pygame.draw.ellipse(surface, (30, 25, 35), (cat_x - 6, cat_y - 4, 12, 10))
        # 猫头
        pygame.draw.circle(surface, (35, 30, 40), (cat_x - 8, cat_y - 8), 6)
        # 猫耳朵
        pygame.draw.polygon(surface, (35, 30, 40), [(cat_x - 12, cat_y - 12), (cat_x - 14, cat_y - 18), (cat_x - 8, cat_y - 12)])
        pygame.draw.polygon(surface, (35, 30, 40), [(cat_x - 4, cat_y - 12), (cat_x - 2, cat_y - 18), (cat_x - 6, cat_y - 12)])
        # 猫眼睛（发光）
        eye_glow = int(200 + 55 * math.sin(t * 5))
        pygame.draw.circle(surface, (eye_glow, eye_glow, 50), (cat_x - 10, cat_y - 9), 2)
        pygame.draw.circle(surface, (eye_glow, eye_glow, 50), (cat_x - 6, cat_y - 9), 2)
        # 猫尾巴（摆动）
        tail_wave = math.sin(t * 3) * 0.5
        for ts in range(5):
            tx = cat_x + 5 + ts * 3
            ty = cat_y - 2 + int(math.sin(tail_wave + ts * 0.4) * (ts * 1.5))
            pygame.draw.circle(surface, (30, 25, 35), (tx, ty), 2)
        
        # ★新增：咒术光环符文（身体周围）
        rune_r = 35 + int(3 * math.sin(t * 2))
        rune_count = 8
        for r in range(rune_count):
            r_angle = t * 0.8 + r * (math.pi * 2 / rune_count)
            rx = cx + int(math.cos(r_angle) * rune_r)
            ry = cy + int(math.sin(r_angle) * rune_r * 0.5)
            r_alpha = 150 + int(80 * math.sin(t * 3 + r))
            # 不同形状的符文
            rune_type = r % 4
            if rune_type == 0:  # 三角
                pygame.draw.polygon(surface, (*magic, r_alpha), 
                                  [(rx, ry - 5), (rx - 4, ry + 3), (rx + 4, ry + 3)], 1)
            elif rune_type == 1:  # 圆
                pygame.draw.circle(surface, (*magic, r_alpha), (rx, ry), 4, 1)
            elif rune_type == 2:  # 菱形
                pygame.draw.polygon(surface, (*magic, r_alpha),
                                  [(rx, ry - 5), (rx - 4, ry), (rx, ry + 5), (rx + 4, ry)], 1)
            else:  # 十字
                pygame.draw.line(surface, (*magic, r_alpha), (rx - 4, ry), (rx + 4, ry), 1)
                pygame.draw.line(surface, (*magic, r_alpha), (rx, ry - 4), (rx, ry + 4), 1)
    
    elif variant == "bloodmoon":
        # 血月祭礼 - 巨型血月 + 蝙蝠群 + 血祭坛 + 血池 + 狼人爪印 + 血色荆棘
        # 巨大血月背景
        moon_y = cy - int(h * 0.38)
        moon_r = 35 + int(5 * math.sin(t * 1.2))
        # 月晕层
        for glow in range(5):
            glow_r = moon_r + glow * 10
            glow_alpha = 40 - glow * 8
            pygame.draw.circle(surface, (*core, glow_alpha), (cx, moon_y), glow_r)
        # 月球本体
        pygame.draw.circle(surface, (*core, 120), (cx, moon_y), moon_r)
        pygame.draw.circle(surface, (*hellfire, 80), (cx, moon_y), moon_r - 5)
        # 月球陨石坑
        pygame.draw.circle(surface, (*core, 60), (cx - 10, moon_y - 8), 8)
        pygame.draw.circle(surface, (*core, 50), (cx + 12, moon_y + 5), 6)
        pygame.draw.circle(surface, (*core, 45), (cx - 5, moon_y + 10), 5)
        
        # 蝙蝠群飞过
        for bat in range(6):
            bat_progress = (t * 0.4 + bat * 0.18) % 1.0
            bat_x = cx - int(w * 0.6) + int(bat_progress * w * 1.2)
            bat_y = moon_y + int(15 * math.sin(t * 5 + bat * 2)) + (bat % 3) * 12
            bat_wing = 6 + int(3 * math.sin(t * 10 + bat * 2))
            # 蝙蝠身体
            pygame.draw.ellipse(surface, (30, 0, 0), (bat_x - 2, bat_y - 1, 4, 3))
            # 蝙蝠翅膀
            pygame.draw.polygon(surface, (50, 0, 0),
                              [(bat_x, bat_y), (bat_x - bat_wing, bat_y - 3), (bat_x - bat_wing + 2, bat_y)])
            pygame.draw.polygon(surface, (50, 0, 0),
                              [(bat_x, bat_y), (bat_x + bat_wing, bat_y - 3), (bat_x + bat_wing - 2, bat_y)])
        
        # 底部血池
        pool_y = cy + int(h * 0.3)
        pool_w = int(w * 0.6)
        # 血池本体
        pygame.draw.ellipse(surface, (*core, 100), (cx - pool_w // 2, pool_y - 5, pool_w, 15))
        pygame.draw.ellipse(surface, (*hellfire, 60), (cx - pool_w // 2 + 5, pool_y - 3, pool_w - 10, 10))
        # 血波纹
        for ripple in range(3):
            ripple_r = int((t * 0.5 + ripple * 0.33) % 1.0 * pool_w // 2)
            ripple_alpha = 80 - int(ripple_r * 1.5)
            if ripple_alpha > 0:
                pygame.draw.ellipse(surface, (*core, ripple_alpha),
                                  (cx - ripple_r, pool_y - ripple_r // 4, ripple_r * 2, ripple_r // 2), 1)
        
        # 血滴从上方落入池中
        for drop in range(5):
            drop_progress = (t * 0.8 + drop * 0.2) % 1.0
            drop_x = cx - int(w * 0.2) + drop * int(w * 0.1)
            drop_y = cy - int(h * 0.15) + int(drop_progress * h * 0.45)
            drop_size = 4 - int(drop_progress * 2)
            if drop_size > 1:
                pygame.draw.ellipse(surface, (*core, 220), (drop_x - 2, drop_y, 4, drop_size * 2))
        
        # ★新增：狼人爪印（从血池边缘向外）
        for claw_set in range(4):
            claw_x = cx - int(w * 0.4) + claw_set * int(w * 0.28)
            claw_y = pool_y + 8 + claw_set % 2 * 6
            claw_alpha = 150 - claw_set * 25
            # 四个爪印
            for claw in range(4):
                c_offset = (claw - 1.5) * 4
                # 爪垫
                pygame.draw.ellipse(surface, (*core, claw_alpha), 
                                  (claw_x + c_offset - 2, claw_y - 3, 4, 5))
                # 爪痕
                pygame.draw.line(surface, (*hellfire, claw_alpha),
                               (claw_x + c_offset, claw_y), (claw_x + c_offset, claw_y + 8), 2)
        
        # ★新增：血色荆棘（从两侧生长）
        for side in [-1, 1]:
            thorn_base_x = cx + side * int(w * 0.45)
            thorn_base_y = cy + int(h * 0.2)
            # 主茎
            prev_x, prev_y = thorn_base_x, thorn_base_y
            for seg in range(8):
                wave = int(side * 3 * math.sin(t * 2 + seg * 0.5))
                new_x = prev_x + wave
                new_y = prev_y - 10
                pygame.draw.line(surface, (60, 0, 0), (prev_x, prev_y), (new_x, new_y), 3)
                # 刺
                if seg % 2 == 0:
                    thorn_angle = side * 0.8
                    pygame.draw.line(surface, (80, 10, 10),
                                   (new_x, new_y), 
                                   (new_x + int(math.cos(thorn_angle) * 8), new_y + int(math.sin(thorn_angle) * 8)), 2)
                prev_x, prev_y = new_x, new_y
            # 顶端血玫瑰
            rose_x, rose_y = prev_x, prev_y
            for petal in range(6):
                p_angle = petal * (math.pi / 3) + t * 0.5
                p_dist = 8 + int(3 * math.sin(t * 2 + petal))
                px = rose_x + int(math.cos(p_angle) * p_dist)
                py = rose_y + int(math.sin(p_angle) * p_dist * 0.6)
                pygame.draw.ellipse(surface, (*core, 180), (px - 4, py - 3, 8, 6))
            pygame.draw.circle(surface, (*hellfire_bright, 200), (rose_x, rose_y), 4)
        
        # ★新增：悬浮的血晶
        for crystal in range(3):
            c_angle = t * 0.7 + crystal * (math.pi * 2 / 3)
            c_dist = 40 + int(8 * math.sin(t * 1.5 + crystal))
            c_x = cx + int(math.cos(c_angle) * c_dist)
            c_y = cy - int(h * 0.15) + int(math.sin(c_angle) * c_dist * 0.3)
            c_rot = t * 2 + crystal
            # 菱形血晶
            c_size = 10 + int(3 * math.sin(t * 3 + crystal))
            pygame.draw.polygon(surface, (*core, 200),
                              [(c_x, c_y - c_size), (c_x - c_size // 2, c_y),
                               (c_x, c_y + c_size // 2), (c_x + c_size // 2, c_y)])
            # 血晶光芒
            pygame.draw.polygon(surface, (*hellfire_bright, 120),
                              [(c_x, c_y - c_size), (c_x - c_size // 2, c_y),
                               (c_x, c_y + c_size // 2), (c_x + c_size // 2, c_y)], 1)
            # 中心发光
            pygame.draw.circle(surface, core_bright, (c_x, c_y), 3)
        
        # ★新增：猩红之眼（月亮中心）
        eye_pulse = 1.0 + 0.2 * math.sin(t * 4)
        eye_r = int(12 * eye_pulse)
        pygame.draw.circle(surface, (0, 0, 0), (cx, moon_y), eye_r + 4)
        pygame.draw.circle(surface, (*core, 200), (cx, moon_y), eye_r)
        # 眼瞳
        pupil_x = cx + int(3 * math.sin(t * 1.5))
        pupil_y = moon_y + int(2 * math.cos(t * 1.2))
        pygame.draw.ellipse(surface, (0, 0, 0), (pupil_x - 3, pupil_y - 6, 6, 12))
    
    elif variant == "void":
        # 虚空主宰 - 黑洞 + 虚空触手 + 空间裂缝 + 被吸入的星光 + 次元门 + 虚空眼
        # 中心黑洞
        hole_r = 18
        # 事件视界
        pygame.draw.circle(surface, (0, 0, 0), (cx, cy), hole_r)
        # 吸积盘
        for ring in range(8):
            ring_r = hole_r + 5 + ring * 6
            ring_alpha = 100 - ring * 10
            ring_thickness = 3 - ring // 3
            if ring_alpha > 0 and ring_thickness > 0:
                pygame.draw.circle(surface, (*core, ring_alpha), (cx, cy), ring_r, ring_thickness)
        # 黑洞边缘光
        pygame.draw.circle(surface, (*core_bright, 180), (cx, cy), hole_r + 2, 2)
        
        # 虚空触手从黑洞伸出
        for tentacle in range(6):
            t_angle = t * 0.8 + tentacle * (math.pi / 3)
            t_segments = 8
            prev_x, prev_y = cx, cy
            for seg in range(t_segments):
                seg_len = 8 + seg * 2
                wave = math.sin(t * 3 + tentacle + seg * 0.5) * (seg * 2)
                seg_angle = t_angle + wave * 0.1
                seg_x = prev_x + int(math.cos(seg_angle) * seg_len)
                seg_y = prev_y + int(math.sin(seg_angle) * seg_len * 0.5)
                seg_thick = max(1, 4 - seg // 2)
                seg_alpha = 180 - seg * 15
                if seg_alpha > 0:
                    pygame.draw.line(surface, (*core, seg_alpha), (prev_x, prev_y), (seg_x, seg_y), seg_thick)
                prev_x, prev_y = seg_x, seg_y
            # 触手尖端
            pygame.draw.circle(surface, (*core_bright, 150), (prev_x, prev_y), 3)
        
        # 空间裂缝
        for crack in range(4):
            crack_angle = crack * (math.pi / 2) + t * 0.3
            crack_x = cx + int(math.cos(crack_angle) * 55)
            crack_y = cy + int(math.sin(crack_angle) * 35)
            crack_len = 20 + int(8 * math.sin(t * 2 + crack))
            # 裂缝本体（锯齿状）
            points = [(crack_x, crack_y)]
            for seg in range(5):
                px = crack_x + (seg + 1) * 4 * (1 if crack % 2 == 0 else -1)
                py = crack_y + seg * crack_len // 5 + int(3 * math.sin(t * 4 + seg))
                points.append((px, py))
            pygame.draw.lines(surface, (*magic, 180), False, points, 2)
            # 裂缝发光
            pygame.draw.circle(surface, (*magic, 100), (crack_x, crack_y), 6)
        
        # 被吸入的星光粒子
        for star in range(15):
            star_angle = t * 2.5 + star * (math.pi * 2 / 15)
            star_dist = 70 - ((t * 25 + star * 5) % 55)
            star_x = cx + int(math.cos(star_angle) * star_dist)
            star_y = cy + int(math.sin(star_angle) * star_dist * 0.5)
            star_size = max(1, int(star_dist / 20))
            star_alpha = min(255, int(star_dist * 3.5))
            pygame.draw.circle(surface, (*magic, star_alpha), (star_x, star_y), star_size)
        
        # ★新增：次元门（两侧）
        for side in [-1, 1]:
            portal_x = cx + side * int(w * 0.5)
            portal_y = cy
            portal_w = 15 + int(5 * math.sin(t * 2 + side))
            portal_h = 35 + int(8 * math.sin(t * 1.5 + side))
            # 门框
            pygame.draw.ellipse(surface, (*magic, 150), 
                              (portal_x - portal_w, portal_y - portal_h // 2, portal_w * 2, portal_h), 3)
            # 门内漩涡
            for swirl in range(5):
                s_r = portal_w - swirl * 3
                if s_r > 0:
                    s_alpha = 100 - swirl * 20
                    pygame.draw.ellipse(surface, (*core, s_alpha),
                                      (portal_x - s_r, portal_y - int(s_r * portal_h / portal_w / 2), 
                                       s_r * 2, int(s_r * portal_h / portal_w)))
            # 门内深渊
            pygame.draw.ellipse(surface, (0, 0, 0), 
                              (portal_x - portal_w // 2, portal_y - portal_h // 4, portal_w, portal_h // 2))
            # 能量外泄
            for leak in range(4):
                leak_angle = side * (math.pi / 2) + math.sin(t * 3 + leak) * 0.5
                leak_len = 15 + int((t * 20 + leak * 8) % 20)
                lx = portal_x + side * int(math.cos(leak_angle) * leak_len)
                ly = portal_y + int(math.sin(leak_angle * 3) * 8)
                pygame.draw.line(surface, (*magic, 150), (portal_x, portal_y), (lx, ly), 1)
        
        # ★新增：虚空之眼（浮空）
        for eye in range(3):
            eye_angle = t * 0.6 + eye * (math.pi * 2 / 3)
            eye_dist = 45 + int(10 * math.sin(t * 1.5 + eye))
            eye_x = cx + int(math.cos(eye_angle) * eye_dist)
            eye_y = cy - int(h * 0.2) + int(math.sin(eye_angle) * eye_dist * 0.3)
            # 眼眶
            pygame.draw.ellipse(surface, (*core, 180), (eye_x - 8, eye_y - 5, 16, 10))
            pygame.draw.ellipse(surface, (0, 0, 0), (eye_x - 6, eye_y - 4, 12, 8))
            # 眼瞳（看向玩家/中心）
            pupil_offset_x = int(2 * math.cos(eye_angle + math.pi))
            pupil_offset_y = int(1 * math.sin(eye_angle + math.pi))
            pygame.draw.circle(surface, core_bright, (eye_x + pupil_offset_x, eye_y + pupil_offset_y), 3)
            pygame.draw.circle(surface, (255, 255, 255), (eye_x + pupil_offset_x - 1, eye_y + pupil_offset_y - 1), 1)
        
        # ★新增：虚空符文环
        rune_r = 60 + int(5 * math.sin(t * 1.5))
        for rune in range(12):
            r_angle = rune * (math.pi / 6) + t * 0.4
            rx = cx + int(math.cos(r_angle) * rune_r)
            ry = cy + int(math.sin(r_angle) * rune_r * 0.35)
            r_alpha = 150 + int(80 * math.sin(t * 4 + rune))
            # 符文字符（各种形状）
            r_type = rune % 4
            if r_type == 0:
                pygame.draw.circle(surface, (*magic, r_alpha), (rx, ry), 4, 1)
                pygame.draw.circle(surface, (*magic, r_alpha), (rx, ry), 2)
            elif r_type == 1:
                pygame.draw.rect(surface, (*magic, r_alpha), (rx - 3, ry - 3, 6, 6), 1)
            elif r_type == 2:
                pygame.draw.polygon(surface, (*magic, r_alpha),
                                  [(rx, ry - 4), (rx - 4, ry + 3), (rx + 4, ry + 3)], 1)
            else:
                pygame.draw.line(surface, (*magic, r_alpha), (rx - 4, ry), (rx + 4, ry), 2)
                pygame.draw.line(surface, (*magic, r_alpha), (rx, ry - 4), (rx, ry + 4), 2)
        
        # ★新增：时空扭曲波纹
        distort_phase = t * 2
        for wave in range(3):
            wave_r = 30 + wave * 20 + int((distort_phase + wave * 0.5) % 1.0 * 20)
            wave_alpha = 100 - int(wave_r * 1.2)
            if wave_alpha > 0:
                # 扭曲的椭圆
                points = []
                for seg in range(20):
                    seg_angle = seg * (math.pi / 10)
                    distort = math.sin(seg_angle * 3 + t * 5) * 5
                    px = cx + int(math.cos(seg_angle) * (wave_r + distort))
                    py = cy + int(math.sin(seg_angle) * (wave_r + distort) * 0.4)
                    points.append((px, py))
                if len(points) > 2:
                    pygame.draw.polygon(surface, (*core, wave_alpha), points, 1)
            pygame.draw.lines(surface, (*magic, 180), False, points, 2)
            # 裂缝发光
            pygame.draw.circle(surface, (*magic, 100), (crack_x, crack_y), 6)
        
        # 被吸入的星光粒子
        for star in range(15):
            star_angle = t * 2.5 + star * (math.pi * 2 / 15)
            star_dist = 70 - ((t * 25 + star * 5) % 55)
            star_x = cx + int(math.cos(star_angle) * star_dist)
            star_y = cy + int(math.sin(star_angle) * star_dist * 0.5)
            star_size = max(1, int(star_dist / 20))
            star_alpha = min(255, int(star_dist * 3.5))
            pygame.draw.circle(surface, (*magic, star_alpha), (star_x, star_y), star_size)
    
    elif variant == "shadow":
        # 暗影行者 - 分身残影 + 暗影匕首 + 暗影步痕迹 + 唯一白眼 + 暗杀印记 + 影子斗篷
        # 多层残影（更多层）
        for shadow in range(10):
            shadow_offset_x = int(10 * math.sin(t * 2 + shadow * 0.5))
            shadow_offset_y = int(6 * math.cos(t * 1.8 + shadow * 0.4))
            shadow_x = cx + shadow_offset_x + (shadow - 5) * 4
            shadow_y = cy + shadow * 3
            shadow_alpha = 40 - shadow * 4
            if shadow_alpha > 0:
                shadow_surf = pygame.Surface((int(w * 0.45), int(h * 0.35)), pygame.SRCALPHA)
                pygame.draw.ellipse(shadow_surf, (0, 0, 0, shadow_alpha), 
                                   (0, 0, int(w * 0.45), int(h * 0.35)))
                surface.blit(shadow_surf, (shadow_x - int(w * 0.225), shadow_y - int(h * 0.175)))
        
        # 两侧暗影匕首
        for side in [-1, 1]:
            dagger_x = cx + side * int(w * 0.4)
            dagger_y = cy - int(h * 0.05) + int(8 * math.sin(t * 2.5 + side))
            dagger_angle = side * 0.4 + math.sin(t * 3) * 0.2
            dagger_len = 25
            # 刀身
            tip_x = dagger_x + int(math.cos(dagger_angle) * dagger_len) * side
            tip_y = dagger_y - int(math.sin(dagger_angle) * dagger_len)
            pygame.draw.polygon(surface, (60, 60, 80),
                              [(dagger_x, dagger_y - 3), (dagger_x, dagger_y + 3), (tip_x, tip_y)])
            # 刀刃高光
            pygame.draw.line(surface, (120, 120, 150), (dagger_x, dagger_y), (tip_x, tip_y), 1)
            # 刀柄
            handle_x = dagger_x - int(math.cos(dagger_angle) * 8) * side
            handle_y = dagger_y + int(math.sin(dagger_angle) * 8)
            pygame.draw.line(surface, (40, 30, 50), (dagger_x, dagger_y), (handle_x, handle_y), 4)
            # 暗影能量
            pygame.draw.circle(surface, (*core, 100), (tip_x, tip_y), 5)
        
        # 暗影步痕迹（地面）
        for step in range(5):
            step_progress = (t * 0.5 + step * 0.2) % 1.0
            step_x = cx - int(w * 0.35) + int(step_progress * w * 0.7)
            step_y = cy + int(h * 0.28)
            step_alpha = int(80 * (1 - step_progress))
            step_w = 15 - int(step_progress * 8)
            if step_alpha > 0 and step_w > 0:
                pygame.draw.ellipse(surface, (0, 0, 0, step_alpha), (step_x - step_w // 2, step_y - 3, step_w, 6))
        
        # 超亮白眼（唯一亮点 - 更强化）
        eye_y = cy - int(h * 0.03)
        eye_flash = 220 + int(35 * math.sin(t * 8))
        # 眼光晕（大范围）
        for glow in range(6):
            glow_r = 15 + glow * 5
            glow_alpha = eye_flash - glow * 35
            if glow_alpha > 0:
                pygame.draw.circle(surface, (255, 255, 255, glow_alpha), (cx, eye_y), glow_r)
        # 眼核
        pygame.draw.circle(surface, (255, 255, 255), (cx, eye_y), 7)
        pygame.draw.circle(surface, (200, 200, 255), (cx, eye_y), 4)
        # 眼神光芒射线
        for ray in range(12):
            ray_angle = t * 2 + ray * (math.pi / 6)
            ray_len = 25 + int(12 * math.sin(t * 5 + ray))
            ray_x = cx + int(math.cos(ray_angle) * ray_len)
            ray_y = eye_y + int(math.sin(ray_angle) * ray_len)
            pygame.draw.line(surface, (255, 255, 255, 100), (cx, eye_y), (ray_x, ray_y), 1)
        
        # ★新增：暗杀印记（目标身上的标记）
        for mark in range(4):
            mark_angle = mark * (math.pi / 2) + t * 0.5
            mark_dist = 50 + int(5 * math.sin(t * 2 + mark))
            mark_x = cx + int(math.cos(mark_angle) * mark_dist)
            mark_y = cy + int(math.sin(mark_angle) * mark_dist * 0.4)
            mark_r = 8 + int(2 * math.sin(t * 4 + mark))
            # 瞄准圈
            pygame.draw.circle(surface, (*core, 150), (mark_x, mark_y), mark_r, 2)
            # 十字准星
            pygame.draw.line(surface, (*core_bright, 180), (mark_x - mark_r - 3, mark_y), (mark_x - mark_r + 5, mark_y), 1)
            pygame.draw.line(surface, (*core_bright, 180), (mark_x + mark_r - 5, mark_y), (mark_x + mark_r + 3, mark_y), 1)
            pygame.draw.line(surface, (*core_bright, 180), (mark_x, mark_y - mark_r - 3), (mark_x, mark_y - mark_r + 5), 1)
            pygame.draw.line(surface, (*core_bright, 180), (mark_x, mark_y + mark_r - 5), (mark_x, mark_y + mark_r + 3), 1)
        
        # ★新增：影子斗篷（飘动）
        cloak_base_y = cy - int(h * 0.25)
        for side in [-1, 1]:
            cloak_points = []
            for i in range(8):
                wave = math.sin(t * 3 + i * 0.5) * (i * 2)
                cx_point = cx + side * int(w * 0.15) + side * i * 5 + int(wave)
                cy_point = cloak_base_y + i * 12
                cloak_points.append((cx_point, cy_point))
            # 斗篷轮廓
            if len(cloak_points) > 2:
                pygame.draw.lines(surface, (20, 15, 30), False, cloak_points, 3)
                # 斗篷内部阴影
                for i in range(len(cloak_points) - 1):
                    alpha = 80 - i * 10
                    if alpha > 0:
                        pygame.draw.line(surface, (10, 5, 20, alpha), cloak_points[i], cloak_points[i + 1], 5)
        
        # ★新增：暗影分身（半透明复制体）
        for clone in range(2):
            clone_x = cx + (clone * 2 - 1) * int(w * 0.55)
            clone_y = cy + int(5 * math.sin(t * 2 + clone))
            clone_alpha = 40 + int(30 * math.sin(t * 3 + clone))
            # 分身轮廓
            pygame.draw.ellipse(surface, (0, 0, 0, clone_alpha), 
                              (clone_x - int(w * 0.2), clone_y - int(h * 0.3), int(w * 0.4), int(h * 0.5)))
            # 分身的眼睛
            clone_eye_y = clone_y - int(h * 0.05)
            pygame.draw.circle(surface, (255, 255, 255, clone_alpha + 50), (clone_x, clone_eye_y), 4)
        
        # ★新增：暗影之刃轨迹
        blade_trail_count = 6
        for bt in range(blade_trail_count):
            bt_progress = (t * 1.5 + bt * 0.15) % 1.0
            bt_angle = bt_progress * math.pi * 2
            bt_x = cx + int(math.cos(bt_angle) * 35)
            bt_y = cy + int(math.sin(bt_angle) * 35 * 0.5)
            bt_alpha = int(150 * (1 - bt_progress))
            if bt_alpha > 0:
                # 刀光
                pygame.draw.line(surface, (200, 200, 220, bt_alpha),
                               (bt_x - 5, bt_y - 5), (bt_x + 5, bt_y + 5), 2)
        
        # ★新增：烟雾弹效果
        smoke_x = cx + int(30 * math.sin(t * 0.8))
        smoke_y = cy + int(h * 0.15)
        for smoke in range(5):
            s_offset_x = int(15 * math.sin(t * 2 + smoke * 1.5))
            s_offset_y = int(10 * math.cos(t * 1.8 + smoke))
            s_r = 12 + smoke * 3 - int((t * 0.3) % 1.0 * 5)
            s_alpha = 40 - smoke * 8
            if s_r > 0 and s_alpha > 0:
                pygame.draw.circle(surface, (30, 30, 40, s_alpha), 
                                 (smoke_x + s_offset_x, smoke_y + s_offset_y), s_r)
    
    elif variant == "magma":
        # 熔岩领主 - 火山 + 岩浆河流 + 浮空岩石 + 熔岩喷发 + 熔岩巨人 + 火焰护盾
        # 背景小火山
        volcano_x = cx
        volcano_y = cy + int(h * 0.35)
        volcano_w = int(w * 0.5)
        volcano_h = int(h * 0.25)
        # 火山体
        pygame.draw.polygon(surface, (60, 30, 20),
                          [(volcano_x - volcano_w // 2, volcano_y),
                           (volcano_x - volcano_w // 4, volcano_y - volcano_h),
                           (volcano_x + volcano_w // 4, volcano_y - volcano_h),
                           (volcano_x + volcano_w // 2, volcano_y)])
        # 火山口
        pygame.draw.ellipse(surface, (*hellfire, 150),
                          (volcano_x - volcano_w // 4, volcano_y - volcano_h - 5, volcano_w // 2, 12))
        pygame.draw.ellipse(surface, (*hellfire_bright, 100),
                          (volcano_x - volcano_w // 6, volcano_y - volcano_h - 3, volcano_w // 3, 8))
        
        # 岩浆喷发
        for erupt in range(8):
            erupt_progress = (t * 1.5 + erupt * 0.12) % 1.0
            erupt_x = volcano_x + int(15 * math.sin(t * 3 + erupt * 2))
            erupt_y = volcano_y - volcano_h - int(erupt_progress * h * 0.4)
            erupt_size = int(6 * (1 - erupt_progress * 0.5))
            if erupt_size > 0:
                pygame.draw.circle(surface, (*hellfire_bright, 230), (erupt_x, erupt_y), erupt_size)
                # 火星尾迹
                for tail in range(4):
                    tail_y = erupt_y + tail * 4
                    tail_alpha = 180 - tail * 40
                    if tail_alpha > 0:
                        pygame.draw.circle(surface, (*hellfire, tail_alpha), (erupt_x, tail_y), max(1, erupt_size - tail))
        
        # 两侧岩浆河流
        for side in [-1, 1]:
            river_x = cx + side * int(w * 0.3)
            for seg in range(6):
                seg_y = cy - int(h * 0.15) + seg * int(h * 0.08)
                seg_w = 10 - seg
                wave = int(3 * math.sin(t * 4 + seg + side))
                if seg_w > 0:
                    pygame.draw.ellipse(surface, (*hellfire, 150 - seg * 15),
                                      (river_x - seg_w // 2 + wave, seg_y, seg_w, 8))
        
        # 浮空燃烧岩石
        for rock in range(4):
            rock_angle = t * 0.6 + rock * (math.pi / 2)
            rock_dist = 40 + int(10 * math.sin(t * 1.5 + rock))
            rock_x = cx + int(math.cos(rock_angle) * rock_dist)
            rock_y = cy - int(h * 0.1) + int(math.sin(rock_angle) * rock_dist * 0.3)
            rock_size = 8 + int(3 * math.sin(t * 2 + rock))
            # 岩石本体
            pygame.draw.polygon(surface, (80, 40, 20),
                              [(rock_x, rock_y - rock_size),
                               (rock_x - rock_size, rock_y + rock_size // 2),
                               (rock_x + rock_size, rock_y + rock_size // 2)])
            # 岩石裂缝发光
            pygame.draw.line(surface, (*hellfire, 200), (rock_x - 2, rock_y - rock_size + 3), (rock_x + 1, rock_y + 2), 2)
            # 燃烧效果
            pygame.draw.circle(surface, (*hellfire, 120), (rock_x, rock_y - rock_size - 3), 5)
        
        # ★新增：熔岩巨人手臂（从两侧伸出）
        for side in [-1, 1]:
            arm_x = cx + side * int(w * 0.5)
            arm_y = cy + int(h * 0.1)
            # 手臂
            arm_segments = [(arm_x, arm_y)]
            for seg in range(5):
                seg_wave = math.sin(t * 2 + seg * 0.5) * 5
                seg_x = arm_x - side * (seg + 1) * 10 + int(seg_wave)
                seg_y = arm_y - seg * 5 + int(math.sin(t * 3 + seg) * 3)
                arm_segments.append((seg_x, seg_y))
            # 绘制手臂
            for i in range(len(arm_segments) - 1):
                seg_thick = 8 - i
                pygame.draw.line(surface, (100, 50, 25), arm_segments[i], arm_segments[i + 1], seg_thick)
                # 岩浆裂缝
                pygame.draw.line(surface, (*hellfire, 180), arm_segments[i], arm_segments[i + 1], max(1, seg_thick - 4))
            # 巨人拳头
            fist_x, fist_y = arm_segments[-1]
            pygame.draw.circle(surface, (90, 45, 20), (fist_x, fist_y), 12)
            # 拳头熔岩纹路
            for crack in range(4):
                c_angle = crack * (math.pi / 2) + t * 0.5
                c_len = 8
                pygame.draw.line(surface, (*hellfire, 200), (fist_x, fist_y),
                               (fist_x + int(math.cos(c_angle) * c_len), fist_y + int(math.sin(c_angle) * c_len)), 2)
        
        # ★新增：火焰护盾
        shield_r = 55 + int(5 * math.sin(t * 2))
        for flame in range(16):
            f_angle = flame * (math.pi / 8) + t * 2
            f_x = cx + int(math.cos(f_angle) * shield_r)
            f_y = cy + int(math.sin(f_angle) * shield_r * 0.4)
            f_h = 15 + int(8 * math.sin(t * 6 + flame))
            f_w = 8
            # 火焰
            pygame.draw.polygon(surface, (*hellfire, 150),
                              [(f_x, f_y - f_h), (f_x - f_w // 2, f_y), (f_x + f_w // 2, f_y)])
            pygame.draw.polygon(surface, (*hellfire_bright, 100),
                              [(f_x, f_y - f_h + 3), (f_x - f_w // 4, f_y - 2), (f_x + f_w // 4, f_y - 2)])
        
        # ★新增：熔岩地裂
        for crack in range(3):
            crack_x = cx - int(w * 0.3) + crack * int(w * 0.3)
            crack_y = cy + int(h * 0.25)
            # 地裂线
            crack_points = [(crack_x, crack_y)]
            for seg in range(5):
                px = crack_x + int(math.sin(seg * 1.5) * 8)
                py = crack_y + seg * 8
                crack_points.append((px, py))
            pygame.draw.lines(surface, (40, 20, 10), False, crack_points, 3)
            # 地裂发光
            pygame.draw.lines(surface, (*hellfire, 150), False, crack_points, 1)
            # 从裂缝中喷出的火焰
            if int(t * 10 + crack) % 5 == 0:
                spray_h = 15 + int(10 * math.sin(t * 8))
                pygame.draw.polygon(surface, (*hellfire_bright, 200),
                                  [(crack_x, crack_y - spray_h), (crack_x - 5, crack_y), (crack_x + 5, crack_y)])
        
        # ★新增：熔岩核心（胸口）
        core_y = cy - int(h * 0.08)
        core_pulse = 1.0 + 0.3 * math.sin(t * 5)
        core_r = int(12 * core_pulse)
        # 核心光晕
        for glow in range(4):
            pygame.draw.circle(surface, (*hellfire_bright, 80 - glow * 20), (cx, core_y), core_r + glow * 6)
        # 核心本体
        pygame.draw.circle(surface, (*hellfire_bright, 250), (cx, core_y), core_r)
        pygame.draw.circle(surface, (255, 255, 200), (cx, core_y), core_r // 2)
        
        # ★新增：火山灰云
        for ash in range(10):
            ash_x = cx + int(40 * math.sin(t * 0.5 + ash * 0.8))
            ash_y = cy - int(h * 0.4) - int((t * 15 + ash * 12) % 40)
            ash_r = 5 + int(3 * math.sin(t * 2 + ash))
            ash_alpha = 80 - int(((cy - int(h * 0.4) - ash_y) / 40) * 60)
            if ash_alpha > 0:
                pygame.draw.circle(surface, (60, 50, 45, ash_alpha), (ash_x, ash_y), ash_r)
    
    elif variant == "frost":
        # 寒霜灾厄 - 暴风雪 + 巨型冰锥 + 冰冻链条 + 雪花 + 冰晶护盾 + 冰龙
        # 暴风雪粒子（大量）
        for snow in range(30):
            snow_x = cx - int(w * 0.55) + int((snow * 19 + t * 50) % (w * 1.1))
            snow_y = cy - int(h * 0.5) + int((t * 40 + snow * 13) % h)
            snow_size = 2 + int(math.sin(t * 3 + snow) * 1.5)
            # 雪花形状（六角）
            for spoke in range(6):
                spoke_angle = spoke * (math.pi / 3) + t * 0.5
                spoke_len = snow_size + 1
                end_x = snow_x + int(math.cos(spoke_angle) * spoke_len)
                end_y = snow_y + int(math.sin(spoke_angle) * spoke_len)
                pygame.draw.line(surface, (*core_bright, 180), (snow_x, snow_y), (end_x, end_y), 1)
        
        # 两侧巨型冰锥
        for side in [-1, 1]:
            icicle_x = cx + side * int(w * 0.38)
            icicle_y = cy - int(h * 0.35)
            icicle_h = int(h * 0.45) + int(8 * math.sin(t * 1.5 + side))
            # 冰锥本体
            pygame.draw.polygon(surface, (*core, 150),
                              [(icicle_x - 8, icicle_y),
                               (icicle_x + 8, icicle_y),
                               (icicle_x + 2, icicle_y + icicle_h),
                               (icicle_x - 2, icicle_y + icicle_h)])
            # 冰锥高光
            pygame.draw.line(surface, (*core_bright, 200), (icicle_x - 3, icicle_y + 5), (icicle_x - 1, icicle_y + icicle_h - 5), 2)
            # 冰锥滴水
            drip_progress = (t * 0.8 + side * 0.5) % 1.0
            drip_y = icicle_y + icicle_h + int(drip_progress * 15)
            drip_alpha = int(200 * (1 - drip_progress))
            pygame.draw.circle(surface, (*core_bright, drip_alpha), (icicle_x, drip_y), 2)
        
        # 冰冻锁链环绕
        chain_points = []
        for i in range(10):
            chain_angle = t * 1.2 + i * (math.pi / 5)
            chain_dist = 45 + int(8 * math.sin(t * 2 + i))
            chain_x = cx + int(math.cos(chain_angle) * chain_dist)
            chain_y = cy + int(math.sin(chain_angle) * chain_dist * 0.45)
            chain_points.append((chain_x, chain_y))
            # 链节
            pygame.draw.circle(surface, (*core, 180), (chain_x, chain_y), 5)
            pygame.draw.circle(surface, core_bright, (chain_x, chain_y), 3)
        # 连接链
        for i in range(len(chain_points)):
            pygame.draw.line(surface, (*core, 100), chain_points[i], chain_points[(i + 1) % len(chain_points)], 2)
        
        # 寒气地面
        for mist in range(4):
            mist_y = cy + int(h * 0.32) + mist * 5
            mist_alpha = 60 - mist * 15
            mist_w = int(w * 0.65) + int(20 * math.sin(t + mist))
            pygame.draw.ellipse(surface, (*core, mist_alpha),
                              (cx - mist_w // 2, mist_y - 4, mist_w, 8))
        
        # 大型六角雪花装饰（顶部）
        flake_y = cy - int(h * 0.45)
        flake_r = 15 + int(4 * math.sin(t * 2))
        flake_rot = t * 0.3
        for branch in range(6):
            branch_angle = branch * (math.pi / 3) + flake_rot
            bx = cx + int(math.cos(branch_angle) * flake_r)
            by = flake_y + int(math.sin(branch_angle) * flake_r)
            pygame.draw.line(surface, (*core_bright, 200), (cx, flake_y), (bx, by), 2)
            # 分叉
            for sub in [-1, 1]:
                sub_angle = branch_angle + sub * 0.5
                sub_len = flake_r * 0.5
                sx = bx + int(math.cos(sub_angle) * sub_len)
                sy = by + int(math.sin(sub_angle) * sub_len)
                pygame.draw.line(surface, (*core, 180), (bx, by), (sx, sy), 1)
        
        # ★新增：六边形冰晶护盾
        shield_r = int(w * 0.55) + int(5 * math.sin(t * 2))
        for i in range(6):
            angle1 = i * (math.pi / 3) + t * 0.2
            angle2 = (i + 1) * (math.pi / 3) + t * 0.2
            x1 = cx + int(math.cos(angle1) * shield_r)
            y1 = cy + int(math.sin(angle1) * shield_r * 0.5)
            x2 = cx + int(math.cos(angle2) * shield_r)
            y2 = cy + int(math.sin(angle2) * shield_r * 0.5)
            pygame.draw.line(surface, (*core_bright, 100), (x1, y1), (x2, y2), 3)
            # 护盾节点
            pygame.draw.circle(surface, (*core_bright, 200), (x1, y1), 5)
        
        # ★新增：冰龙形态（环绕）
        dragon_angle = t * 1.5
        for seg in range(20):
            seg_angle = dragon_angle - seg * 0.25
            seg_dist = 55 + int(15 * math.sin(seg * 0.3))
            seg_x = cx + int(math.cos(seg_angle) * seg_dist)
            seg_y = cy + int(math.sin(seg_angle) * seg_dist * 0.4)
            seg_size = 8 - int(seg * 0.3)
            if seg_size > 1:
                pygame.draw.circle(surface, (*core, 180 - seg * 8), (seg_x, seg_y), seg_size)
                if seg == 0:  # 龙头
                    head_angle = dragon_angle + math.pi / 2
                    # 龙角
                    for horn in [-1, 1]:
                        horn_x = seg_x + int(math.cos(head_angle + horn * 0.5) * 12)
                        horn_y = seg_y + int(math.sin(head_angle + horn * 0.5) * 12)
                        pygame.draw.line(surface, core_bright, (seg_x, seg_y), (horn_x, horn_y), 2)
                    # 龙眼
                    pygame.draw.circle(surface, (200, 230, 255), (seg_x, seg_y), 4)
                    pygame.draw.circle(surface, (50, 100, 200), (seg_x, seg_y), 2)
        
        # ★新增：冰霜吐息
        breath_x = cx + int(math.cos(dragon_angle + math.pi / 2) * 60)
        breath_y = cy + int(math.sin(dragon_angle + math.pi / 2) * 25)
        for b in range(5):
            b_spread = b * 5
            b_alpha = 150 - b * 30
            pygame.draw.circle(surface, (*core_bright, b_alpha), 
                             (breath_x + b * 4, breath_y + int(math.sin(t * 5 + b) * 3)), 4 + b)
    
    elif variant == "souleater":
        # 噬魂者 - 骷髅堆 + 灵魂漩涡 + 灵魂链 + 幽灵面孔 + 死神镰刀 + 亡灵军团
        # 底部骷髅堆
        skull_base_y = cy + int(h * 0.28)
        for skull_i in range(7):
            skull_x = cx - int(w * 0.28) + skull_i * int(w * 0.1)
            skull_y = skull_base_y + int(5 * math.sin(skull_i * 0.8))
            skull_size = 7 + skull_i % 3
            # 骷髅头
            pygame.draw.circle(surface, (200, 200, 180), (skull_x, skull_y), skull_size)
            pygame.draw.circle(surface, (60, 60, 50), (skull_x, skull_y), skull_size - 2)
            # 眼窝
            pygame.draw.circle(surface, (*core, 200), (skull_x - 2, skull_y - 1), 2)
            pygame.draw.circle(surface, (*core, 200), (skull_x + 2, skull_y - 1), 2)
            # 鼻子
            pygame.draw.polygon(surface, (80, 80, 70),
                              [(skull_x, skull_y + 1), (skull_x - 1, skull_y + 3), (skull_x + 1, skull_y + 3)])
        
        # 灵魂漩涡
        for soul in range(10):
            soul_angle = t * 2.5 + soul * (math.pi / 5)
            soul_dist = 30 + int(25 * math.sin(t * 1.2 + soul * 0.5))
            soul_x = cx + int(math.cos(soul_angle) * soul_dist)
            soul_y = cy - int(h * 0.08) + int(math.sin(soul_angle) * soul_dist * 0.4)
            
            # 灵魂光球
            soul_size = 7 + int(4 * math.sin(t * 3 + soul * 0.8))
            pygame.draw.circle(surface, (*core, 60), (soul_x, soul_y), soul_size + 6)
            pygame.draw.circle(surface, (*core, 120), (soul_x, soul_y), soul_size)
            pygame.draw.circle(surface, core_bright, (soul_x, soul_y), max(2, soul_size - 4))
            
            # 长尾迹
            for tail in range(8):
                tail_angle = soul_angle - tail * 0.1
                tail_dist = soul_dist - tail * 4
                tail_x = cx + int(math.cos(tail_angle) * tail_dist)
                tail_y = cy - int(h * 0.08) + int(math.sin(tail_angle) * tail_dist * 0.4)
                tail_alpha = 100 - tail * 12
                if tail_alpha > 0:
                    pygame.draw.circle(surface, (*core, tail_alpha), (tail_x, tail_y), max(1, soul_size - tail))
        
        # 灵魂链（从骷髅连到机体）
        for chain in range(3):
            chain_start_x = cx - int(w * 0.2) + chain * int(w * 0.2)
            chain_start_y = skull_base_y - 5
            chain_end_y = cy
            # 链条
            for seg in range(5):
                seg_y = chain_start_y - seg * (chain_start_y - chain_end_y) // 5
                wave = int(4 * math.sin(t * 4 + chain + seg * 0.5))
                pygame.draw.circle(surface, (*core, 150 - seg * 20), (chain_start_x + wave, seg_y), 3)
        
        # 幽灵面孔浮现
        for ghost in range(2):
            ghost_angle = t * 0.5 + ghost * math.pi
            ghost_x = cx + int(math.cos(ghost_angle) * 50)
            ghost_y = cy - int(h * 0.2) + int(math.sin(ghost_angle) * 15)
            ghost_alpha = int(60 + 40 * math.sin(t * 2 + ghost))
            # 面孔轮廓
            pygame.draw.ellipse(surface, (*core, ghost_alpha), (ghost_x - 10, ghost_y - 12, 20, 25))
            # 眼睛
            pygame.draw.circle(surface, (*core_bright, ghost_alpha + 50), (ghost_x - 4, ghost_y - 3), 3)
            pygame.draw.circle(surface, (*core_bright, ghost_alpha + 50), (ghost_x + 4, ghost_y - 3), 3)
            # 嘴（张开）
            pygame.draw.ellipse(surface, (0, 0, 0, ghost_alpha), (ghost_x - 5, ghost_y + 4, 10, 8))
        
        # ★新增：死神镰刀（巨大）
        scythe_angle = math.sin(t * 1.2) * 0.3 - 0.5
        scythe_x = cx + int(w * 0.55)
        scythe_y = cy - int(h * 0.1)
        # 镰刀柄
        handle_len = 70
        handle_end_x = scythe_x + int(math.cos(scythe_angle + math.pi) * handle_len)
        handle_end_y = scythe_y + int(math.sin(scythe_angle + math.pi) * handle_len)
        pygame.draw.line(surface, (80, 60, 50), (scythe_x, scythe_y), (handle_end_x, handle_end_y), 4)
        # 镰刀刃
        blade_start = scythe_angle - math.pi / 4
        blade_end = scythe_angle + math.pi / 3
        for b in range(15):
            b_angle = blade_start + (blade_end - blade_start) * (b / 14)
            b_r = 35 + int(15 * math.sin(b * 0.5))
            bx = scythe_x + int(math.cos(b_angle) * b_r)
            by = scythe_y + int(math.sin(b_angle) * b_r)
            pygame.draw.circle(surface, (*core, 200), (bx, by), 3 if b < 3 or b > 12 else 4)
        # 刃上的灵魂
        soul_on_blade = int(t * 3) % 15
        sb_angle = blade_start + (blade_end - blade_start) * (soul_on_blade / 14)
        sb_x = scythe_x + int(math.cos(sb_angle) * 30)
        sb_y = scythe_y + int(math.sin(sb_angle) * 30)
        pygame.draw.circle(surface, core_bright, (sb_x, sb_y), 5)
        
        # ★新增：亡灵军团（底部升起的骷髅手）
        for hand in range(5):
            hand_x = cx - int(w * 0.35) + hand * int(w * 0.18)
            rise_progress = (t * 0.5 + hand * 0.3) % 1.5
            if rise_progress < 1.0:
                hand_y = cy + int(h * 0.45) - int(rise_progress * 25)
                hand_alpha = int(200 * min(1, rise_progress * 2))
                # 手臂
                pygame.draw.line(surface, (180, 170, 150, hand_alpha), 
                               (hand_x, cy + int(h * 0.45)), (hand_x, hand_y), 3)
                # 手掌
                pygame.draw.circle(surface, (200, 190, 170), (hand_x, hand_y), 5)
                # 手指
                for finger in range(5):
                    f_angle = -math.pi / 2 - 0.4 + finger * 0.2
                    f_len = 8 + finger % 2 * 2
                    fx = hand_x + int(math.cos(f_angle) * f_len)
                    fy = hand_y + int(math.sin(f_angle) * f_len)
                    pygame.draw.line(surface, (180, 170, 150), (hand_x, hand_y), (fx, fy), 2)
        
        # ★新增：死亡沙漏
        hourglass_x = cx - int(w * 0.45)
        hourglass_y = cy - int(h * 0.1)
        # 上半部
        pygame.draw.polygon(surface, (*core, 150),
                          [(hourglass_x - 10, hourglass_y - 20), (hourglass_x + 10, hourglass_y - 20),
                           (hourglass_x, hourglass_y)])
        # 下半部
        pygame.draw.polygon(surface, (*core, 150),
                          [(hourglass_x, hourglass_y),
                           (hourglass_x - 10, hourglass_y + 20), (hourglass_x + 10, hourglass_y + 20)])
        # 沙子流动
        sand_progress = t % 1.0
        sand_y = hourglass_y - 15 + int(sand_progress * 30)
        pygame.draw.circle(surface, core_bright, (hourglass_x, sand_y), 2)
        # 框架
        pygame.draw.rect(surface, (100, 80, 60), (hourglass_x - 12, hourglass_y - 22, 24, 4))
        pygame.draw.rect(surface, (100, 80, 60), (hourglass_x - 12, hourglass_y + 18, 24, 4))
    
    elif variant == "apocalypse":
        # 末日审判 - 神圣天平 + 圣书 + 审判光柱 + 十字架 + 号角 + 石板
        # 顶部十字架
        cross_y = cy - int(h * 0.48)
        cross_h = 30
        cross_w = 20
        # 十字架本体
        pygame.draw.rect(surface, (*halo, 200), (cx - 3, cross_y - cross_h // 2, 6, cross_h))
        pygame.draw.rect(surface, (*halo, 200), (cx - cross_w // 2, cross_y - cross_h // 4, cross_w, 6))
        # 十字架光芒
        for ray in range(8):
            ray_angle = ray * (math.pi / 4) + t * 0.5
            ray_len = 12 + int(6 * math.sin(t * 3 + ray))
            pygame.draw.line(surface, (*hellfire, 150),
                           (cx, cross_y), (cx + int(math.cos(ray_angle) * ray_len), cross_y + int(math.sin(ray_angle) * ray_len)), 1)
        
        # 神圣天平
        scale_y = cy + int(h * 0.15)
        scale_w = int(w * 0.5)
        # 天平杆
        scale_tilt = math.sin(t * 1.5) * 0.15
        pygame.draw.line(surface, (*halo, 180),
                       (cx - scale_w // 2, scale_y + int(scale_tilt * 20)),
                       (cx + scale_w // 2, scale_y - int(scale_tilt * 20)), 3)
        # 天平中心支点
        pygame.draw.polygon(surface, (*halo, 200),
                          [(cx, scale_y - 8), (cx - 5, scale_y + 5), (cx + 5, scale_y + 5)])
        # 两侧托盘
        for side in [-1, 1]:
            pan_x = cx + side * scale_w // 2
            pan_y = scale_y + int(scale_tilt * 20) * (-side)
            # 链条
            pygame.draw.line(surface, (*halo, 150), (pan_x, pan_y), (pan_x, pan_y + 15), 1)
            # 托盘
            pygame.draw.arc(surface, (*halo, 180), (pan_x - 12, pan_y + 12, 24, 12), 0, math.pi, 2)
            # 托盘上的东西
            if side == -1:  # 灵魂
                pygame.draw.circle(surface, (*core, 150), (pan_x, pan_y + 18), 5)
            else:  # 羽毛
                pygame.draw.ellipse(surface, (*hellfire, 150), (pan_x - 3, pan_y + 14, 6, 10))
        
        # 两侧圣书
        for side in [-1, 1]:
            book_x = cx + side * int(w * 0.38)
            book_y = cy - int(h * 0.1) + int(6 * math.sin(t * 2 + side))
            book_angle = side * 0.2 + math.sin(t * 1.5) * 0.1
            # 书本
            pygame.draw.rect(surface, (180, 160, 100), (book_x - 8, book_y - 10, 16, 20))
            pygame.draw.line(surface, (120, 100, 60), (book_x, book_y - 10), (book_x, book_y + 10), 2)
            # 书页发光
            pygame.draw.rect(surface, (*hellfire, 100), (book_x - 6, book_y - 8, 12, 16))
            # 神圣符文
            rune_alpha = 180 + int(60 * math.sin(t * 4 + side))
            pygame.draw.line(surface, (*halo, rune_alpha), (book_x - 4, book_y - 4), (book_x + 4, book_y - 4), 1)
            pygame.draw.line(surface, (*halo, rune_alpha), (book_x - 4, book_y), (book_x + 4, book_y), 1)
            pygame.draw.line(surface, (*halo, rune_alpha), (book_x - 4, book_y + 4), (book_x + 4, book_y + 4), 1)
        
        # 审判光柱
        for beam in range(2):
            beam_x = cx + (beam * 2 - 1) * int(w * 0.2)
            beam_w = 15 + int(6 * math.sin(t * 3 + beam))
            beam_alpha = 60 + int(40 * math.sin(t * 2.5 + beam * 0.5))
            pygame.draw.rect(surface, (*hellfire, beam_alpha),
                            (beam_x - beam_w // 2, y - 50, beam_w, int(h * 0.45)))
            pygame.draw.rect(surface, (*halo, beam_alpha + 20),
                            (beam_x - beam_w // 4, y - 50, beam_w // 2, int(h * 0.45)))
        
        # ★新增：审判号角（两侧，更大更详细）
        for side in [-1, 1]:
            horn_x = cx + side * int(w * 0.5)
            horn_y = cy - int(h * 0.3) + int(5 * math.sin(t * 1.5 + side))
            # 号角本体（长弯曲）
            for seg in range(12):
                seg_angle = side * (0.2 + seg * 0.08)
                seg_x = horn_x - side * seg * 4
                seg_y = horn_y + int(math.sin(seg_angle) * seg * 2)
                seg_r = 3 + seg // 3
                pygame.draw.circle(surface, (220, 200, 150), (seg_x, seg_y), seg_r)
            # 号角口（喇叭状）
            bell_x = horn_x - side * 48
            pygame.draw.ellipse(surface, (200, 180, 130), (bell_x - 8, horn_y + 5, 16, 12))
            # 音波效果
            for wave in range(3):
                wave_r = 8 + wave * 8 + int(t * 15) % 8
                wave_alpha = 150 - wave * 50 - int((t * 15) % 8) * 10
                if wave_alpha > 0:
                    pygame.draw.arc(surface, (*halo, wave_alpha), 
                                  (bell_x - wave_r, horn_y + 10 - wave_r // 2, wave_r * 2, wave_r), 
                                  math.pi * 0.3 if side > 0 else math.pi * 0.7,
                                  math.pi * 0.7 if side > 0 else math.pi * 1.3, 2)
        
        # ★新增：十诫石板
        tablet_x = cx - int(w * 0.55)
        tablet_y = cy + int(h * 0.05)
        # 石板本体
        pygame.draw.polygon(surface, (150, 140, 120),
                          [(tablet_x - 12, tablet_y - 25), (tablet_x + 12, tablet_y - 25),
                           (tablet_x + 15, tablet_y - 20), (tablet_x + 15, tablet_y + 25),
                           (tablet_x - 15, tablet_y + 25), (tablet_x - 15, tablet_y - 20)])
        # 圆顶
        pygame.draw.arc(surface, (150, 140, 120), (tablet_x - 12, tablet_y - 35, 24, 20), 0, math.pi, 3)
        # 文字线条
        for line in range(8):
            line_y = tablet_y - 18 + line * 5
            line_w = 20 - (line % 3) * 4
            pygame.draw.line(surface, (*halo, 180), (tablet_x - line_w // 2, line_y), (tablet_x + line_w // 2, line_y), 1)
        # 石板光晕
        pygame.draw.ellipse(surface, (*halo, 40), (tablet_x - 25, tablet_y - 35, 50, 70))
        
        # ★新增：堕落天使羽毛（飘落）
        for feather in range(8):
            f_x = cx + int(40 * math.sin(t * 0.8 + feather * 1.2))
            f_y = cy - int(h * 0.4) + int((t * 20 + feather * 20) % (h * 0.9))
            f_rot = t * 2 + feather
            f_alpha = 200 - int(((f_y - (cy - int(h * 0.4))) / (h * 0.9)) * 150)
            if f_alpha > 0:
                # 羽毛形状
                f_len = 12
                pygame.draw.ellipse(surface, (*halo, f_alpha), 
                                  (f_x - 2, f_y - f_len // 2, 4, f_len))
                # 羽毛中线
                pygame.draw.line(surface, (180, 170, 140, f_alpha), (f_x, f_y - f_len // 2), (f_x, f_y + f_len // 2), 1)
        
        # ★新增：烙印符号（额头）
        mark_y = cy - int(h * 0.32)
        mark_r = 8 + int(3 * math.sin(t * 3))
        # 三角形烙印
        pygame.draw.polygon(surface, (*hellfire, 200),
                          [(cx, mark_y - mark_r), (cx - mark_r, mark_y + mark_r // 2), (cx + mark_r, mark_y + mark_r // 2)], 2)
        # 中心眼睛
        pygame.draw.circle(surface, (*halo, 220), (cx, mark_y), 4)
        pygame.draw.circle(surface, (0, 0, 0), (cx, mark_y), 2)
    
    elif variant == "seraph":
        # 炽天使 - 六翼完整羽翼 + 圣剑 + 号角 + 头顶光环 + 圣光粒子 + 圣火 + 神圣铠甲
        # 六翼天使完整羽翼（3对）
        for wing_pair in range(3):
            wing_base_y = cy - int(h * 0.15) + wing_pair * int(h * 0.1)
            wing_len_base = int(w * 0.42) - wing_pair * 8
            for side in [-1, 1]:
                wing_x = cx + side * int(w * 0.12)
                wing_angle = side * (math.pi / 5 + wing_pair * 0.12) + math.sin(t * 3 + wing_pair) * 0.08
                
                # 羽翼骨架
                tip_x = wing_x + int(math.cos(wing_angle) * wing_len_base) * side
                tip_y = wing_base_y + int(math.sin(wing_angle) * wing_len_base * 0.25)
                pygame.draw.line(surface, (*core, 200), (wing_x, wing_base_y), (tip_x, tip_y), 3)
                
                # 羽毛（多层）
                for feather in range(8):
                    f_progress = (feather + 1) / 9
                    f_x = wing_x + int((tip_x - wing_x) * f_progress)
                    f_y = wing_base_y + int((tip_y - wing_base_y) * f_progress)
                    f_len = 12 - feather
                    f_angle = wing_angle + side * (math.pi / 2.5) + math.sin(t * 4 + feather) * 0.1
                    # 主羽毛
                    f_end_x = f_x + int(math.cos(f_angle) * f_len) * side
                    f_end_y = f_y + int(math.sin(f_angle) * f_len)
                    pygame.draw.line(surface, (*core, 180 - feather * 10), (f_x, f_y), (f_end_x, f_end_y), 2)
                    # 次级羽毛
                    if feather < 5:
                        sub_len = f_len * 0.6
                        sub_angle = f_angle + side * 0.4
                        pygame.draw.line(surface, (*core, 120), (f_x, f_y),
                                       (f_x + int(math.cos(sub_angle) * sub_len) * side, f_y + int(math.sin(sub_angle) * sub_len)), 1)
        
        # 两侧圣剑
        for side in [-1, 1]:
            sword_x = cx + side * int(w * 0.45)
            sword_y = cy + int(5 * math.sin(t * 2 + side))
            sword_angle = side * 0.3 + math.sin(t * 1.5) * 0.15
            sword_len = 35
            # 剑身
            blade_tip_x = sword_x + int(math.cos(sword_angle) * sword_len) * side * 0.3
            blade_tip_y = sword_y - int(math.sin(sword_angle) * sword_len * 0.8) - sword_len
            pygame.draw.polygon(surface, (220, 220, 240),
                              [(sword_x - 3, sword_y), (sword_x + 3, sword_y), (blade_tip_x, blade_tip_y)])
            # 剑刃高光
            pygame.draw.line(surface, (255, 255, 255), (sword_x, sword_y), (blade_tip_x, blade_tip_y), 1)
            # 剑柄
            pygame.draw.rect(surface, (180, 150, 80), (sword_x - 2, sword_y, 4, 10))
            # 剑格
            pygame.draw.rect(surface, (*core, 200), (sword_x - 8, sword_y - 2, 16, 4))
            # 圣光
            pygame.draw.circle(surface, (*core, 80), (blade_tip_x, blade_tip_y), 8)
        
        # 头顶大光环
        halo_y_pos = cy - int(h * 0.52)
        halo_r_size = int(w * 0.22) + int(5 * math.sin(t * 2))
        # 光环光晕
        for glow in range(3):
            glow_r = halo_r_size + glow * 5
            pygame.draw.ellipse(surface, (*core, 80 - glow * 25),
                              (cx - glow_r, halo_y_pos - glow_r // 3, glow_r * 2, glow_r * 2 // 3))
        # 光环本体
        pygame.draw.ellipse(surface, (*core, 200),
                          (cx - halo_r_size, halo_y_pos - halo_r_size // 3, halo_r_size * 2, halo_r_size * 2 // 3), 4)
        
        # 号角（两侧）
        for side in [-1, 1]:
            horn_x = cx + side * int(w * 0.3)
            horn_y = cy - int(h * 0.35)
            horn_angle = side * 0.6
            # 号角本体
            pygame.draw.arc(surface, (220, 200, 150),
                          (horn_x - 15, horn_y - 10, 30, 20), 
                          math.pi * 0.2 if side > 0 else math.pi * 0.8, 
                          math.pi * 0.8 if side > 0 else math.pi * 1.8, 3)
            # 号角口
            pygame.draw.circle(surface, (200, 180, 130), (horn_x + side * 12, horn_y + 5), 4)
            # 音符效果
            note_progress = (t * 0.8) % 1.0
            note_x = horn_x + side * (15 + int(note_progress * 15))
            note_y = horn_y + 5 - int(note_progress * 10)
            note_alpha = int(200 * (1 - note_progress))
            pygame.draw.circle(surface, (*core_bright, note_alpha), (note_x, note_y), 3)
        
        # 圣光粒子上升
        for particle in range(15):
            p_x = cx + int(35 * math.sin(t * 1.0 + particle * 0.7))
            p_y = cy + int(h * 0.35) - int((t * 20 + particle * 10) % (h * 0.8))
            p_size = 2 + int(math.sin(t * 4 + particle) * 1.5)
            p_alpha = 200 - int(((cy + int(h * 0.35) - p_y) / (h * 0.8)) * 150)
            if p_alpha > 0:
                pygame.draw.circle(surface, (*core_bright, p_alpha), (p_x, p_y), p_size)
        
        # ★新增：燃烧的圣火（双手持）
        for side in [-1, 1]:
            torch_x = cx + side * int(w * 0.58)
            torch_y = cy + int(h * 0.1)
            # 火炬柄
            pygame.draw.rect(surface, (160, 130, 80), (torch_x - 3, torch_y, 6, 25))
            # 圣火
            for flame in range(8):
                flame_h = 20 + int(10 * math.sin(t * 8 + flame * 0.5 + side))
                flame_w = 10 - flame
                flame_y = torch_y - flame_h
                flame_alpha = 220 - flame * 25
                if flame_alpha > 0:
                    pygame.draw.ellipse(surface, (*core_bright, flame_alpha),
                                      (torch_x - flame_w // 2 + int(math.sin(t * 10 + flame) * 3), 
                                       flame_y, flame_w, flame_h // 2))
            # 火星
            for spark in range(5):
                spark_x = torch_x + int(math.sin(t * 6 + spark * 2 + side) * 8)
                spark_y = torch_y - 25 - int((t * 30 + spark * 8) % 30)
                pygame.draw.circle(surface, (*core_bright, 200), (spark_x, spark_y), 2)
        
        # ★新增：神圣铠甲纹路（身体上）
        armor_lines = [
            (cy - int(h * 0.15), 0.3),  # 胸甲线
            (cy, 0.25),                   # 腰甲线
            (cy + int(h * 0.12), 0.2),   # 下甲线
        ]
        for armor_y, armor_w_ratio in armor_lines:
            armor_w = int(w * armor_w_ratio)
            # 水平线
            pygame.draw.line(surface, (*core, 150), (cx - armor_w, armor_y), (cx + armor_w, armor_y), 2)
            # 装饰点
            pygame.draw.circle(surface, core_bright, (cx - armor_w, armor_y), 3)
            pygame.draw.circle(surface, core_bright, (cx + armor_w, armor_y), 3)
            pygame.draw.circle(surface, core_bright, (cx, armor_y), 4)
        # 中心神圣符号
        symbol_y = cy - int(h * 0.08)
        symbol_r = 12
        pygame.draw.circle(surface, (*core, 100), (cx, symbol_y), symbol_r + 5)
        pygame.draw.circle(surface, (*core, 180), (cx, symbol_y), symbol_r, 2)
        # 内部十字
        pygame.draw.line(surface, core_bright, (cx, symbol_y - 8), (cx, symbol_y + 8), 2)
        pygame.draw.line(surface, core_bright, (cx - 8, symbol_y), (cx + 8, symbol_y), 2)
        
        # ★新增：神圣光环轨道（额外的小光环）
        for orb in range(4):
            orb_angle = t * 2 + orb * (math.pi / 2)
            orb_dist = 60
            orb_x = cx + int(math.cos(orb_angle) * orb_dist)
            orb_y = cy + int(math.sin(orb_angle) * orb_dist * 0.35)
            # 小光环
            pygame.draw.circle(surface, (*core, 60), (orb_x, orb_y), 10)
            pygame.draw.circle(surface, core_bright, (orb_x, orb_y), 6)
            pygame.draw.circle(surface, (255, 255, 255), (orb_x, orb_y), 3)
        
        # ★新增：神圣光柱从天而降
        pillar_x = cx + int(20 * math.sin(t * 0.5))
        pillar_w = 30 + int(10 * math.sin(t * 2))
        pillar_alpha = 40 + int(20 * math.sin(t * 3))
        pygame.draw.rect(surface, (*core_bright, pillar_alpha),
                        (pillar_x - pillar_w // 2, y - 100, pillar_w, int(h * 0.5)))
    
    elif variant == "quantum":
        # 量子灾变 - 数据矩阵 + 错误代码 + 像素故障 + 电弧网络 + 二进制流 + 全息投影 + 病毒
        # 数据矩阵背景
        for row in range(10):
            for col in range(8):
                block_x = cx - int(w * 0.4) + col * int(w * 0.11)
                block_y = cy - int(h * 0.42) + row * int(h * 0.09)
                block_progress = (t * 4 + row * 0.15 + col * 0.2) % 1.0
                block_alpha = int(120 * block_progress) if block_progress > 0.5 else int(120 * (1 - block_progress))
                block_w = 4 + int(2 * math.sin(t * 6 + row + col))
                if block_alpha > 20:
                    pygame.draw.rect(surface, (*core, block_alpha),
                                   (block_x - block_w // 2, block_y, block_w, 3))
        
        # 二进制数字流（两侧）
        for side in [-1, 1]:
            stream_x = cx + side * int(w * 0.42)
            for digit in range(12):
                digit_y = cy - int(h * 0.4) + int((t * 50 + digit * 15) % (h * 0.85))
                digit_val = int(t * 10 + digit) % 2
                digit_alpha = 180 - int(abs(digit_y - cy) * 2)
                if digit_alpha > 0:
                    # 简化的0/1显示
                    if digit_val == 0:
                        pygame.draw.circle(surface, (*core, digit_alpha), (stream_x, digit_y), 3, 1)
                    else:
                        pygame.draw.line(surface, (*core, digit_alpha), (stream_x, digit_y - 3), (stream_x, digit_y + 3), 2)
        
        # 错误代码显示框
        error_y = cy - int(h * 0.3)
        error_w = int(w * 0.5)
        error_h = 20
        # 错误框
        pygame.draw.rect(surface, (*core, 80), (cx - error_w // 2, error_y, error_w, error_h))
        pygame.draw.rect(surface, (*core, 150), (cx - error_w // 2, error_y, error_w, error_h), 1)
        # 错误文字效果（用线条模拟）
        for line in range(3):
            line_w = int((error_w - 10) * (0.8 - line * 0.2))
            line_y = error_y + 5 + line * 5
            line_alpha = 180 + int(60 * math.sin(t * 5 + line))
            pygame.draw.line(surface, (*hellfire, line_alpha),
                           (cx - error_w // 2 + 5, line_y), (cx - error_w // 2 + 5 + line_w, line_y), 1)
        
        # 像素故障方块（随机闪烁）
        glitch_seed = int(t * 20)
        for glitch in range(8):
            if (glitch_seed + glitch) % 4 == 0:
                g_x = cx + int(50 * math.cos(glitch_seed * 0.7 + glitch * 1.3))
                g_y = cy + int(35 * math.sin(glitch_seed * 0.5 + glitch * 1.7))
                g_w = 6 + glitch % 4
                g_h = 4 + glitch % 3
                pygame.draw.rect(surface, (*core_bright, 250), (g_x - g_w // 2, g_y - g_h // 2, g_w, g_h))
        
        # RGB分离效果
        rgb_offset = int(3 * math.sin(t * 8))
        if abs(rgb_offset) > 1:
            # 红色偏移层
            pygame.draw.circle(surface, (255, 0, 0, 60), (cx - rgb_offset, cy), 25, 1)
            # 蓝色偏移层  
            pygame.draw.circle(surface, (0, 0, 255, 60), (cx + rgb_offset, cy), 25, 1)
        
        # 电弧网络
        nodes = []
        for i in range(8):
            node_angle = i * (math.pi / 4) + t * 0.4
            node_dist = 42 + int(10 * math.sin(t * 2 + i))
            node_x = cx + int(math.cos(node_angle) * node_dist)
            node_y = cy + int(math.sin(node_angle) * node_dist * 0.45)
            nodes.append((node_x, node_y))
            pygame.draw.circle(surface, (*core_bright, 220), (node_x, node_y), 4)
            pygame.draw.circle(surface, (*core, 150), (node_x, node_y), 6, 1)
        
        # 电弧连接（动态）
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if (int(t * 15) + i + j) % 5 == 0:
                    # 电弧线（带锯齿）
                    mid_x = (nodes[i][0] + nodes[j][0]) // 2 + int(8 * math.sin(t * 10 + i + j))
                    mid_y = (nodes[i][1] + nodes[j][1]) // 2 + int(5 * math.cos(t * 10 + i + j))
                    pygame.draw.line(surface, (*core, 180), nodes[i], (mid_x, mid_y), 1)
                    pygame.draw.line(surface, (*core, 180), (mid_x, mid_y), nodes[j], 1)
        
        # 扫描线效果
        scan_y = cy - int(h * 0.4) + int((t * 80) % (h * 0.8))
        pygame.draw.line(surface, (*core, 100), (cx - int(w * 0.4), scan_y), (cx + int(w * 0.4), scan_y), 1)
        
        # ★新增：全息投影圆环
        holo_rings = 3
        for ring in range(holo_rings):
            ring_r = 30 + ring * 15
            ring_rot = t * (1.5 - ring * 0.3)
            # 旋转的圆环
            for seg in range(20):
                seg_angle = ring_rot + seg * (math.pi / 10)
                seg_x = cx + int(math.cos(seg_angle) * ring_r)
                seg_y = cy + int(math.sin(seg_angle) * ring_r * 0.3)
                seg_alpha = 100 + int(80 * math.sin(seg_angle * 2))
                if seg % 2 == 0:
                    pygame.draw.circle(surface, (*core, seg_alpha), (seg_x, seg_y), 2)
        
        # ★新增：数据上传/下载箭头
        for side in [-1, 1]:
            arrow_x = cx + side * int(w * 0.55)
            arrow_dir = 1 if side > 0 else -1
            for arrow in range(4):
                arrow_y = cy - int(h * 0.3) + int((t * 40 * arrow_dir + arrow * 25) % (h * 0.7))
                arrow_alpha = 200 - int(abs(arrow_y - cy) * 2)
                if arrow_alpha > 0:
                    # 箭头
                    pygame.draw.polygon(surface, (*core_bright, arrow_alpha),
                                      [(arrow_x, arrow_y - 8 * arrow_dir), 
                                       (arrow_x - 5, arrow_y), (arrow_x + 5, arrow_y)])
                    pygame.draw.line(surface, (*core, arrow_alpha), 
                                   (arrow_x, arrow_y), (arrow_x, arrow_y + 10 * arrow_dir), 2)
        
        # ★新增：病毒形态（三角警告符号）
        virus_count = 3
        for v in range(virus_count):
            v_angle = t * 0.8 + v * (2 * math.pi / virus_count)
            v_dist = 55 + int(10 * math.sin(t * 2 + v))
            v_x = cx + int(math.cos(v_angle) * v_dist)
            v_y = cy + int(math.sin(v_angle) * v_dist * 0.4)
            v_size = 10 + int(3 * math.sin(t * 4 + v))
            # 警告三角
            pygame.draw.polygon(surface, (*hellfire, 200),
                              [(v_x, v_y - v_size), (v_x - v_size, v_y + v_size // 2), 
                               (v_x + v_size, v_y + v_size // 2)], 2)
            # 感叹号
            pygame.draw.line(surface, hellfire, (v_x, v_y - v_size // 2), (v_x, v_y + 1), 2)
            pygame.draw.circle(surface, hellfire, (v_x, v_y + v_size // 3), 2)
        
        # ★新增：数据立方体（3D效果）
        cube_x = cx - int(w * 0.5)
        cube_y = cy + int(h * 0.15)
        cube_size = 18
        cube_rot = t * 1.5
        # 正面
        pygame.draw.rect(surface, (*core, 150), (cube_x - cube_size // 2, cube_y - cube_size // 2, cube_size, cube_size), 1)
        # 顶面（透视）
        top_offset = int(8 * math.cos(cube_rot))
        pygame.draw.polygon(surface, (*core, 100),
                          [(cube_x - cube_size // 2, cube_y - cube_size // 2),
                           (cube_x + cube_size // 2, cube_y - cube_size // 2),
                           (cube_x + cube_size // 2 + top_offset, cube_y - cube_size // 2 - 8),
                           (cube_x - cube_size // 2 + top_offset, cube_y - cube_size // 2 - 8)], 1)
        # 侧面
        pygame.draw.polygon(surface, (*core, 80),
                          [(cube_x + cube_size // 2, cube_y - cube_size // 2),
                           (cube_x + cube_size // 2, cube_y + cube_size // 2),
                           (cube_x + cube_size // 2 + top_offset, cube_y + cube_size // 2 - 8),
                           (cube_x + cube_size // 2 + top_offset, cube_y - cube_size // 2 - 8)], 1)
        # 立方体内部数据点
        for dp in range(4):
            dp_x = cube_x + int(math.sin(t * 5 + dp) * cube_size * 0.3)
            dp_y = cube_y + int(math.cos(t * 4 + dp) * cube_size * 0.3)
            pygame.draw.circle(surface, core_bright, (dp_x, dp_y), 2)
        
        # ★新增：进度条（加载中）
        bar_x = cx + int(w * 0.35)
        bar_y = cy + int(h * 0.2)
        bar_w = 35
        bar_h = 6
        progress = (t * 0.5) % 1.0
        # 外框
        pygame.draw.rect(surface, (*core, 180), (bar_x - bar_w // 2, bar_y, bar_w, bar_h), 1)
        # 进度填充
        fill_w = int(bar_w * progress)
        pygame.draw.rect(surface, (*core_bright, 200), (bar_x - bar_w // 2 + 1, bar_y + 1, fill_w - 2, bar_h - 2))
        # 百分比文字用点表示
        for dot in range(int(progress * 3)):
            pygame.draw.circle(surface, core_bright, (bar_x + bar_w // 2 + 8 + dot * 5, bar_y + 3), 2)


# ==================== 12种涂装专属绘制函数 ====================

def draw_default_sepulcher(surface, x, y, w, h, frame, style):
    """默认涂装 - 终末王座：至尊灾厄的原始猩红形态"""
    theme = get_sepulcher_theme(style)
    _draw_sepulcher_body(surface, x, y, w, h, frame, theme)
    _draw_theme_effects(surface, x, y, w, h, frame, theme, "default")


def draw_brimstone_sepulcher(surface, x, y, w, h, frame, style):
    """硫磺炼狱涂装 - 地狱硫磺火焰主题"""
    theme = get_sepulcher_theme(style)
    _draw_sepulcher_body(surface, x, y, w, h, frame, theme)
    _draw_theme_effects(surface, x, y, w, h, frame, theme, "brimstone")


def draw_witch_sepulcher(surface, x, y, w, h, frame, style):
    """深渊女巫涂装 - 灾厄女巫的诅咒紫形态"""
    theme = get_sepulcher_theme(style)
    _draw_sepulcher_body(surface, x, y, w, h, frame, theme)
    _draw_theme_effects(surface, x, y, w, h, frame, theme, "witch")


def draw_bloodmoon_sepulcher(surface, x, y, w, h, frame, style):
    """血月祭礼涂装 - 鲜血染红的祭坛"""
    theme = get_sepulcher_theme(style)
    _draw_sepulcher_body(surface, x, y, w, h, frame, theme)
    _draw_theme_effects(surface, x, y, w, h, frame, theme, "bloodmoon")


def draw_void_sepulcher(surface, x, y, w, h, frame, style):
    """虚空主宰涂装 - 吞噬一切的虚空"""
    theme = get_sepulcher_theme(style)
    _draw_sepulcher_body(surface, x, y, w, h, frame, theme)
    _draw_theme_effects(surface, x, y, w, h, frame, theme, "void")


def draw_shadow_sepulcher(surface, x, y, w, h, frame, style):
    """暗影行者涂装 - 极致暗黑，仅眼睛发光"""
    theme = get_sepulcher_theme(style)
    _draw_sepulcher_body(surface, x, y, w, h, frame, theme)
    _draw_theme_effects(surface, x, y, w, h, frame, theme, "shadow")


def draw_magma_sepulcher(surface, x, y, w, h, frame, style):
    """熔岩领主涂装 - 火山岩浆主题"""
    theme = get_sepulcher_theme(style)
    _draw_sepulcher_body(surface, x, y, w, h, frame, theme)
    _draw_theme_effects(surface, x, y, w, h, frame, theme, "magma")


def draw_frost_sepulcher(surface, x, y, w, h, frame, style):
    """寒霜灾厄涂装 - 冰封的死寂"""
    theme = get_sepulcher_theme(style)
    _draw_sepulcher_body(surface, x, y, w, h, frame, theme)
    _draw_theme_effects(surface, x, y, w, h, frame, theme, "frost")


def draw_souleater_sepulcher(surface, x, y, w, h, frame, style):
    """噬魂者涂装 - 幽绿灵魂能量"""
    theme = get_sepulcher_theme(style)
    _draw_sepulcher_body(surface, x, y, w, h, frame, theme)
    _draw_theme_effects(surface, x, y, w, h, frame, theme, "souleater")


def draw_apocalypse_sepulcher(surface, x, y, w, h, frame, style):
    """末日审判涂装 - 神圣金色天罚"""
    theme = get_sepulcher_theme(style)
    _draw_sepulcher_body(surface, x, y, w, h, frame, theme)
    _draw_theme_effects(surface, x, y, w, h, frame, theme, "apocalypse")


def draw_seraph_sepulcher(surface, x, y, w, h, frame, style):
    """炽天使涂装 - 堕落的神圣光辉"""
    theme = get_sepulcher_theme(style)
    _draw_sepulcher_body(surface, x, y, w, h, frame, theme)
    _draw_theme_effects(surface, x, y, w, h, frame, theme, "seraph")


def draw_quantum_sepulcher(surface, x, y, w, h, frame, style):
    """量子灾变涂装 - 科技蓝量子能量"""
    theme = get_sepulcher_theme(style)
    _draw_sepulcher_body(surface, x, y, w, h, frame, theme)
    _draw_theme_effects(surface, x, y, w, h, frame, theme, "quantum")
