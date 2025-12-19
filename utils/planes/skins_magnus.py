# -*- coding: utf-8 -*-
"""
真理之书 MAGNUS 涂装渲染系统
Grimoire-System "MAGNUS" - The Tome of Fates

设计理念：
- 核心形态：浮游魔法古籍，摊开朝前飞行
- 书页天使翅膀：数十张发光书页形成羽翼
- 水晶球驾驶舱：全视之眼，威压注视
- 符文环护盾：多层嵌套复杂魔法阵
- 希腊字母拖尾：α, β, Ω 文字脱离飘散
- 附属魔法书：环绕主体的小型魔典
- 锁链封印：金色锁链束缚解放的禁忌之力
"""

import pygame
import math
import random

# 预计算的符文符号路径
RUNE_SYMBOLS = [
    # 符文1: 三角形符文
    [(0, -1), (0.87, 0.5), (-0.87, 0.5), (0, -1)],
    # 符文2: 菱形
    [(0, -1), (0.7, 0), (0, 1), (-0.7, 0), (0, -1)],
    # 符文3: 六芒星外框
    [(0, -1), (0.5, -0.3), (1, -0.3), (0.6, 0.2), (0.8, 1), (0, 0.5), (-0.8, 1), (-0.6, 0.2), (-1, -0.3), (-0.5, -0.3), (0, -1)],
    # 符文4: 十字
    [(0, -1), (0.2, -0.2), (1, -0.2), (1, 0.2), (0.2, 0.2), (0, 1), (-0.2, 0.2), (-1, 0.2), (-1, -0.2), (-0.2, -0.2), (0, -1)],
]

# 希腊字母表
GREEK_LETTERS = ['Α', 'Β', 'Γ', 'Δ', 'Ε', 'Ζ', 'Η', 'Θ', 'Ι', 'Κ', 'Λ', 'Μ', 
                 'Ν', 'Ξ', 'Ο', 'Π', 'Ρ', 'Σ', 'Τ', 'Υ', 'Φ', 'Χ', 'Ψ', 'Ω']

# ============================================================
#   MAGNUS 涂装主题定义（形态差异化增强版）
#   每个涂装具有独特的：形态、附属物、特殊效果
# ============================================================
MAGNUS_THEMES = {
    "default": {
        "name": "真理之书",
        "book_cover": (139, 0, 0),       # 暗红龙皮 #8B0000
        "book_spine": (100, 0, 0),       # 深红书脊
        "page_color": (245, 222, 179),   # 小麦色书页 #F5DEB3
        "page_glow": (255, 245, 220),    # 书页光晕
        "rune_primary": (255, 0, 255),   # 洋红符文 #FF00FF
        "rune_secondary": (200, 0, 200), # 次级符文
        "gold_trim": (255, 215, 0),      # 金色包角
        "crystal": (200, 180, 255),      # 水晶球
        "spirit": (180, 150, 255),       # 灵体
        "trail": (255, 200, 255),        # 拖尾
        # === 形态差异 ===
        "book_shape": "classic",         # 经典展开魔法书
        "wing_style": "page_wings",      # 书页羽翼
        "eye_type": "single_crystal",    # 单水晶球全视之眼
        "accessory": "floating_tomes",   # 环绕浮游小魔典
        "chain_type": "gold_seal",       # 金色封印锁链
    },
    "arcane": {
        "name": "奥术典籍",
        "book_cover": (30, 30, 80),      # 深蓝
        "book_spine": (20, 20, 60),
        "page_color": (220, 230, 255),   # 淡蓝书页
        "page_glow": (180, 200, 255),
        "rune_primary": (100, 150, 255), # 蓝色符文
        "rune_secondary": (80, 120, 220),
        "gold_trim": (150, 180, 255),    # 银蓝
        "crystal": (150, 180, 255),
        "spirit": (100, 150, 255),
        "trail": (150, 180, 255),
        # === 形态差异 ===
        "book_shape": "scroll_hybrid",   # 书卷混合体 - 部分卷轴展开
        "wing_style": "energy_ribbons",  # 能量丝带翅膀
        "eye_type": "arcane_lens",       # 奥术透镜阵列（3层同心圆）
        "accessory": "orbit_glyphs",     # 轨道符文球
        "chain_type": "none",            # 无锁链
    },
    "necro": {
        "name": "死灵禁书",
        "book_cover": (30, 30, 30),      # 黑色
        "book_spine": (20, 20, 20),
        "page_color": (80, 80, 70),      # 灰黄
        "page_glow": (100, 255, 100),    # 绿色光
        "rune_primary": (100, 255, 100), # 绿色符文
        "rune_secondary": (80, 200, 80),
        "gold_trim": (100, 100, 80),     # 做旧金
        "crystal": (100, 255, 100),      # 绿色水晶
        "spirit": (150, 255, 150),       # 幽灵绿
        "trail": (100, 255, 100),
        # === 形态差异 ===
        "book_shape": "torn_grimoire",   # 破损禁书 - 撕裂边缘，漂浮碎页
        "wing_style": "bone_wings",      # 骨骼翅膀 - 骷髅骨架构成
        "eye_type": "skull_socket",      # 骷髅眼窝 - 绿焰燃烧
        "accessory": "floating_skulls",  # 漂浮骷髅头
        "chain_type": "bone_chain",      # 骨链封印
    },
    "holy": {
        "name": "圣典",
        "book_cover": (255, 255, 240),   # 象牙白
        "book_spine": (240, 230, 200),
        "page_color": (255, 255, 255),   # 纯白
        "page_glow": (255, 255, 200),    # 金光
        "rune_primary": (255, 215, 0),   # 金色符文
        "rune_secondary": (255, 200, 100),
        "gold_trim": (255, 215, 0),
        "crystal": (255, 255, 200),
        "spirit": (255, 255, 180),
        "trail": (255, 255, 150),
        # === 形态差异 ===
        "book_shape": "altar_tablet",    # 祭坛石板 - 厚重圣典，十字架形
        "wing_style": "angel_feathers",  # 天使羽翼 - 纯白发光羽毛
        "eye_type": "divine_halo",       # 神圣光轮 - 光环中嵌眼
        "accessory": "prayer_beads",     # 漂浮念珠环
        "chain_type": "holy_rosary",     # 圣念珠链
    },
    "infernal": {
        "name": "地狱魔典",
        "book_cover": (50, 0, 0),        # 暗血红
        "book_spine": (30, 0, 0),
        "page_color": (80, 60, 50),      # 焦黄
        "page_glow": (255, 100, 0),      # 火焰光
        "rune_primary": (255, 100, 0),   # 橙红符文
        "rune_secondary": (255, 50, 0),
        "gold_trim": (255, 150, 50),     # 熔岩金
        "crystal": (255, 100, 50),       # 火焰水晶
        "spirit": (255, 150, 100),       # 火灵
        "trail": (255, 100, 0),
        # === 形态差异 ===
        "book_shape": "burning_tome",    # 燃烧之书 - 边缘着火，融化效果
        "wing_style": "flame_wings",     # 烈焰翅膀 - 火焰喷涌
        "eye_type": "demon_eye",         # 恶魔之眼 - 竖瞳，血红巩膜
        "accessory": "lava_orbs",        # 熔岩球环绕
        "chain_type": "molten_chain",    # 熔岩锁链
    },
    "void": {
        "name": "虚空典籍",
        "book_cover": (20, 0, 40),       # 深紫
        "book_spine": (10, 0, 20),
        "page_color": (60, 40, 80),      # 暗紫
        "page_glow": (150, 100, 200),    # 紫光
        "rune_primary": (180, 100, 255), # 紫色符文
        "rune_secondary": (150, 80, 200),
        "gold_trim": (150, 100, 200),
        "crystal": (180, 100, 255),
        "spirit": (200, 150, 255),
        "trail": (180, 100, 255),
        # === 形态差异 ===
        "book_shape": "rift_portal",     # 裂隙门户 - 书展开成空间裂缝
        "wing_style": "tentacle_wings",  # 触手翅膀 - 扭曲触须
        "eye_type": "void_maw",          # 虚空巨口 - 深渊之眼
        "accessory": "mini_portals",     # 迷你传送门
        "chain_type": "void_tendrils",   # 虚空触须
    },
    "celestial": {
        "name": "星辰宝典",
        "book_cover": (20, 30, 60),      # 星空蓝
        "book_spine": (10, 20, 40),
        "page_color": (200, 220, 255),   # 星光色
        "page_glow": (255, 255, 200),    # 星光
        "rune_primary": (255, 255, 150), # 星光符文
        "rune_secondary": (200, 200, 255),
        "gold_trim": (255, 255, 200),
        "crystal": (200, 220, 255),
        "spirit": (220, 230, 255),
        "trail": (255, 255, 200),
        # === 形态差异 ===
        "book_shape": "orrery_book",     # 星仪之书 - 嵌入天体模型
        "wing_style": "comet_trails",    # 彗星尾翼 - 流星轨迹
        "eye_type": "galaxy_core",       # 银河核心 - 旋转星云
        "accessory": "orbit_planets",    # 环绕行星
        "chain_type": "star_chain",      # 星链
    },
    "blood": {
        "name": "血之魔典",
        "book_cover": (80, 0, 20),       # 血红
        "book_spine": (60, 0, 10),
        "page_color": (200, 180, 180),   # 血染书页
        "page_glow": (255, 50, 50),      # 血光
        "rune_primary": (255, 0, 50),    # 血红符文
        "rune_secondary": (200, 0, 30),
        "gold_trim": (180, 100, 100),    # 血锈金
        "crystal": (255, 100, 100),      # 血晶
        "spirit": (255, 150, 150),
        "trail": (255, 50, 50),
        # === 形态差异 ===
        "book_shape": "flesh_tome",      # 血肉之书 - 活体表皮，脉动
        "wing_style": "vein_wings",      # 血管翅膀 - 血脉网络
        "eye_type": "bloodshot_eye",     # 充血之眼 - 血丝密布
        "accessory": "blood_droplets",   # 漂浮血滴
        "chain_type": "artery_chain",    # 动脉锁链
    },
    "elder": {
        "name": "远古遗典",
        "book_cover": (60, 50, 40),      # 古铜褐
        "book_spine": (50, 40, 30),
        "page_color": (210, 190, 150),   # 羊皮纸色
        "page_glow": (255, 220, 150),    # 古老金光
        "rune_primary": (180, 150, 100), # 褐金符文
        "rune_secondary": (150, 120, 80),
        "gold_trim": (180, 150, 80),     # 古铜金
        "crystal": (200, 180, 120),      # 琥珀
        "spirit": (220, 200, 150),
        "trail": (200, 180, 120),
        # === 形态差异 ===
        "book_shape": "stone_tablet",    # 石刻碑典 - 厚重石板，裂纹
        "wing_style": "fossil_wings",    # 化石翅膀 - 骨骼化石纹理
        "eye_type": "amber_eye",         # 琥珀之眼 - 封存虫子
        "accessory": "rune_stones",      # 漂浮符石
        "chain_type": "rusted_chain",    # 锈蚀铁链
    },
    "frost": {
        "name": "霜寒魔典",
        "book_cover": (40, 60, 80),      # 寒冰蓝
        "book_spine": (30, 50, 70),
        "page_color": (220, 240, 255),   # 冰霜白
        "page_glow": (180, 220, 255),    # 冰蓝光
        "rune_primary": (100, 200, 255), # 冰蓝符文
        "rune_secondary": (80, 180, 240),
        "gold_trim": (180, 220, 255),    # 冰银
        "crystal": (150, 220, 255),      # 冰晶
        "spirit": (200, 240, 255),
        "trail": (150, 220, 255),
        # === 形态差异 ===
        "book_shape": "ice_crystal",     # 冰晶之书 - 六棱柱形，透明
        "wing_style": "snowflake_wings", # 雪花翅膀 - 六角冰晶阵列
        "eye_type": "frozen_tear",       # 冰封之泪 - 冰滴形态
        "accessory": "ice_shards",       # 漂浮冰锥
        "chain_type": "icicle_chain",    # 冰锥链
    },
    "chaos": {
        "name": "混沌禁典",
        "book_cover": (40, 20, 50),      # 混沌紫黑
        "book_spine": (30, 10, 40),
        "page_color": (100, 80, 120),    # 扭曲灰紫
        "page_glow": (255, 100, 200),    # 混沌粉
        "rune_primary": (255, 50, 150),  # 混沌符文
        "rune_secondary": (200, 100, 255),
        "gold_trim": (200, 100, 200),    # 混沌紫金
        "crystal": (255, 100, 200),      # 混沌晶
        "spirit": (255, 150, 220),
        "trail": (255, 100, 200),
        # === 形态差异 ===
        "book_shape": "glitch_book",     # 故障之书 - 像素化，闪烁错位
        "wing_style": "fractal_wings",   # 分形翅膀 - 无限递归图案
        "eye_type": "kaleidoscope",      # 万花筒之眼 - 不断变形
        "accessory": "glitch_cubes",     # 故障方块
        "chain_type": "data_stream",     # 数据流
    },
    "nature": {
        "name": "自然秘典",
        "book_cover": (40, 60, 30),      # 森林绿
        "book_spine": (30, 50, 20),
        "page_color": (220, 240, 200),   # 叶绿白
        "page_glow": (150, 255, 150),    # 自然光
        "rune_primary": (100, 200, 100), # 翠绿符文
        "rune_secondary": (80, 180, 80),
        "gold_trim": (180, 200, 100),    # 草木金
        "crystal": (150, 220, 150),      # 翠绿晶
        "spirit": (180, 255, 180),
        "trail": (150, 220, 150),
        # === 形态差异 ===
        "book_shape": "tree_bark",       # 树皮之书 - 木质纹理，年轮
        "wing_style": "leaf_wings",      # 枝叶翅膀 - 藤蔓与叶片
        "eye_type": "forest_spirit",     # 森灵之眼 - 绿光瞳孔
        "accessory": "floating_leaves",  # 漂浮落叶
        "chain_type": "vine_chain",      # 藤蔓链
    },
}


def get_magnus_theme(theme_name):
    """获取MAGNUS涂装主题"""
    return MAGNUS_THEMES.get(theme_name, MAGNUS_THEMES["default"])


def is_magnus_style(style_name):
    """判断是否为MAGNUS涂装"""
    return style_name in MAGNUS_THEMES or style_name.startswith("magnus_")


def get_all_magnus_styles():
    """获取所有MAGNUS涂装列表"""
    return list(MAGNUS_THEMES.keys())


def draw_rune_symbol(surface, cx, cy, size, rotation, color, alpha):
    """绘制复杂符文符号"""
    rune_idx = int(abs(rotation * 10)) % len(RUNE_SYMBOLS)
    rune = RUNE_SYMBOLS[rune_idx]
    
    points = []
    cos_r = math.cos(rotation)
    sin_r = math.sin(rotation)
    for px, py in rune:
        rx = px * cos_r - py * sin_r
        ry = px * sin_r + py * cos_r
        points.append((int(cx + rx * size), int(cy + ry * size)))
    
    if len(points) >= 3:
        safe_alpha = max(0, min(255, int(alpha)))
        pygame.draw.polygon(surface, (*color[:3], safe_alpha), points, max(1, int(size * 0.15)))


# ============================================================
#   形态差异化渲染函数 - 12种涂装独特形态
# ============================================================

def _draw_wing_variant(surface, cx, cy, wing_side, theme, t, scale, book_width):
    """根据涂装类型绘制不同风格的翅膀"""
    wing_style = theme.get("wing_style", "page_wings")
    wing_base_x = cx + wing_side * (book_width // 2 + int(5 * scale))
    wing_base_y = cy - int(5 * scale)
    
    if wing_style == "page_wings":
        # 经典书页羽翼（默认）
        _draw_page_wings(surface, wing_base_x, wing_base_y, wing_side, theme, t, scale)
    
    elif wing_style == "energy_ribbons":
        # 奥术：能量丝带翅膀 - 流动的魔力丝带
        for ribbon in range(4):
            ribbon_length = int((35 - ribbon * 5) * scale)
            ribbon_wave = math.sin(t * 4 + ribbon * 0.8) * 0.3
            ribbon_angle = wing_side * (0.3 + ribbon * 0.15) + ribbon_wave
            
            points = []
            for seg in range(12):
                seg_t = seg / 11
                wave = math.sin(t * 6 + seg * 0.5 + ribbon) * 5 * scale * seg_t
                px = wing_base_x + int(math.cos(ribbon_angle) * ribbon_length * seg_t) + int(wave * wing_side)
                py = wing_base_y + ribbon * int(8 * scale) + int(math.sin(ribbon_angle) * ribbon_length * seg_t * 0.4)
                points.append((px, py))
            
            if len(points) > 2:
                ribbon_alpha = max(0, min(255, int(200 - ribbon * 35)))
                # 丝带光晕
                pygame.draw.lines(surface, (*theme["rune_primary"], ribbon_alpha // 2), False, points, max(4, int(6 * scale)))
                # 丝带主体
                pygame.draw.lines(surface, (*theme["page_glow"], ribbon_alpha), False, points, max(2, int(3 * scale)))
                # 丝带亮边
                pygame.draw.lines(surface, (255, 255, 255, ribbon_alpha // 2), False, points, 1)
    
    elif wing_style == "bone_wings":
        # 死灵：骨骼翅膀 - 骷髅骨架
        for bone_layer in range(3):
            bone_length = int((30 - bone_layer * 6) * scale)
            bone_angle = wing_side * (0.2 + bone_layer * 0.25)
            
            # 主骨
            end_x = wing_base_x + int(math.cos(bone_angle) * bone_length)
            end_y = wing_base_y + bone_layer * int(10 * scale) + int(math.sin(bone_angle) * bone_length * 0.3)
            bone_alpha = max(0, min(255, 220 - bone_layer * 30))
            
            pygame.draw.line(surface, (200, 190, 170, bone_alpha), 
                           (wing_base_x, wing_base_y + bone_layer * int(10 * scale)), (end_x, end_y), max(3, int(4 * scale)))
            # 关节
            for joint in range(3):
                jx = wing_base_x + int((end_x - wing_base_x) * joint / 3)
                jy = wing_base_y + bone_layer * int(10 * scale) + int((end_y - wing_base_y - bone_layer * int(10 * scale)) * joint / 3)
                pygame.draw.circle(surface, (220, 210, 190, bone_alpha), (jx, jy), max(2, int(3 * scale)))
            
            # 骨刺
            for spike in range(2):
                spike_x = wing_base_x + int((end_x - wing_base_x) * (spike + 1) / 3)
                spike_y = wing_base_y + bone_layer * int(10 * scale) + int((end_y - wing_base_y - bone_layer * int(10 * scale)) * (spike + 1) / 3)
                spike_angle = bone_angle + wing_side * 0.8
                spike_len = int(8 * scale)
                pygame.draw.line(surface, (180, 170, 150, bone_alpha),
                               (spike_x, spike_y), 
                               (spike_x + int(math.cos(spike_angle) * spike_len), spike_y + int(math.sin(spike_angle) * spike_len * 0.4)), 2)
    
    elif wing_style == "angel_feathers":
        # 圣典：天使羽翼 - 纯白发光羽毛
        for layer in range(5):
            feather_count = 7 - layer
            for feather in range(feather_count):
                f_angle = wing_side * (0.15 + layer * 0.08 + feather * 0.18)
                flutter = math.sin(t * 4 + feather * 0.5 + layer) * 0.08
                f_length = int((32 - layer * 4 - feather) * scale)
                
                fx = wing_base_x + wing_side * layer * int(2 * scale)
                fy = wing_base_y + feather * int(5 * scale) + layer * int(3 * scale)
                end_x = fx + int(math.cos(f_angle + flutter) * f_length)
                end_y = fy + int(math.sin(f_angle + flutter) * f_length * 0.35)
                
                f_pulse = 0.7 + 0.3 * math.sin(t * 3 + feather + layer)
                f_alpha = max(0, min(255, int((255 - layer * 30) * f_pulse)))
                
                # 神圣光晕
                pygame.draw.line(surface, (255, 255, 200, f_alpha // 3), (fx, fy), (end_x, end_y), max(6, int(8 * scale)))
                # 羽毛主体
                pygame.draw.line(surface, (255, 255, 255, f_alpha), (fx, fy), (end_x, end_y), max(3, int(4 * scale)))
                # 金色羽轴
                pygame.draw.line(surface, (*theme["gold_trim"], f_alpha), (fx, fy), (end_x, end_y), 1)
    
    elif wing_style == "flame_wings":
        # 地狱：烈焰翅膀 - 火焰喷涌
        for flame in range(20):
            f_life = ((t * 25 + flame * 5) % 60) / 60
            f_angle = wing_side * (0.2 + (flame % 5) * 0.15 + math.sin(t * 3 + flame) * 0.1)
            f_spread = (8 + (flame // 5) * 6) * scale
            
            fx = wing_base_x + int(math.sin(t * 4 + flame) * f_spread * 0.3 * wing_side)
            fy = wing_base_y + (flame // 5) * int(8 * scale) - int(f_life * 35 * scale)
            fx += int(math.cos(f_angle) * f_life * 25 * scale)
            
            f_alpha = max(0, min(255, int(255 * (1 - f_life) ** 0.8)))
            f_size = max(2, int((6 - f_life * 4) * scale))
            
            # 火焰核心
            pygame.draw.circle(surface, (255, 220, 100, f_alpha), (fx, fy), f_size)
            pygame.draw.circle(surface, (255, 150, 50, max(0, f_alpha - 40)), (fx, fy), int(f_size * 1.4))
            pygame.draw.circle(surface, (200, 80, 20, max(0, f_alpha - 80)), (fx, fy), int(f_size * 1.8))
    
    elif wing_style == "tentacle_wings":
        # 虚空：触手翅膀 - 扭曲触须
        for tentacle in range(5):
            t_length = int((28 - tentacle * 3) * scale)
            base_y = wing_base_y + tentacle * int(7 * scale)
            
            points = []
            for seg in range(10):
                seg_t = seg / 9
                # 蠕动效果
                wave1 = math.sin(t * 3 + seg * 0.6 + tentacle) * 8 * scale * seg_t
                wave2 = math.sin(t * 5 + seg * 0.4 + tentacle * 2) * 4 * scale * seg_t
                
                px = wing_base_x + int(seg_t * t_length * wing_side) + int(wave1 * wing_side)
                py = base_y + int(wave2)
                points.append((px, py))
            
            if len(points) > 2:
                t_alpha = max(0, min(255, 200 - tentacle * 25))
                # 触手主体
                pygame.draw.lines(surface, (*theme["rune_primary"], t_alpha), False, points, max(3, int((5 - tentacle * 0.5) * scale)))
                # 触手吸盘
                for i in range(0, len(points), 2):
                    sucker_alpha = max(0, t_alpha - 40)
                    pygame.draw.circle(surface, (*theme["rune_secondary"], sucker_alpha), points[i], max(2, int(2 * scale)))
    
    elif wing_style == "comet_trails":
        # 星辰：彗星尾翼 - 流星轨迹
        for trail in range(6):
            trail_angle = wing_side * (0.1 + trail * 0.12)
            trail_length = int((35 - trail * 3) * scale)
            
            tx = wing_base_x
            ty = wing_base_y + trail * int(6 * scale)
            
            for seg in range(15):
                seg_t = seg / 14
                # 星尘粒子
                px = tx + int(math.cos(trail_angle) * trail_length * seg_t)
                py = ty + int(math.sin(trail_angle) * trail_length * seg_t * 0.35)
                
                sparkle = abs(math.sin(t * 8 + seg + trail * 2))
                p_alpha = max(0, min(255, int((200 - seg * 12) * sparkle)))
                p_size = max(1, int((3 - seg * 0.15) * scale))
                
                if p_alpha > 20:
                    pygame.draw.circle(surface, (*theme["page_glow"], p_alpha), (px, py), p_size)
                    if seg % 3 == 0:
                        pygame.draw.circle(surface, (255, 255, 200, p_alpha // 2), (px, py), p_size + 2)
    
    elif wing_style == "vein_wings":
        # 血之魔典：血管翅膀 - 血脉网络
        for vein in range(4):
            v_length = int((30 - vein * 4) * scale)
            v_angle = wing_side * (0.25 + vein * 0.18)
            base_y = wing_base_y + vein * int(9 * scale)
            
            # 主血管
            end_x = wing_base_x + int(math.cos(v_angle) * v_length)
            end_y = base_y + int(math.sin(v_angle) * v_length * 0.35)
            
            # 脉动效果
            pulse = 0.6 + 0.4 * math.sin(t * 5 + vein)
            v_alpha = max(0, min(255, int(220 * pulse)))
            
            pygame.draw.line(surface, (180, 30, 50, v_alpha), (wing_base_x, base_y), (end_x, end_y), max(3, int(4 * scale)))
            
            # 分支血管
            for branch in range(3):
                bx = wing_base_x + int((end_x - wing_base_x) * (branch + 1) / 4)
                by = base_y + int((end_y - base_y) * (branch + 1) / 4)
                b_angle = v_angle + wing_side * 0.4 * (1 if branch % 2 == 0 else -1)
                b_len = int(10 * scale)
                
                pygame.draw.line(surface, (200, 50, 70, max(0, v_alpha - 40)),
                               (bx, by), (bx + int(math.cos(b_angle) * b_len), by + int(math.sin(b_angle) * b_len * 0.3)), 2)
    
    elif wing_style == "fossil_wings":
        # 远古：化石翅膀 - 骨骼化石纹理
        for fossil in range(4):
            f_length = int((28 - fossil * 5) * scale)
            f_angle = wing_side * (0.2 + fossil * 0.2)
            base_y = wing_base_y + fossil * int(10 * scale)
            
            end_x = wing_base_x + int(math.cos(f_angle) * f_length)
            end_y = base_y + int(math.sin(f_angle) * f_length * 0.3)
            
            f_alpha = max(0, min(255, 180 - fossil * 25))
            
            # 石化骨骼
            pygame.draw.line(surface, (160, 140, 100, f_alpha), (wing_base_x, base_y), (end_x, end_y), max(4, int(5 * scale)))
            # 裂纹
            for crack in range(2):
                cx_pos = wing_base_x + int((end_x - wing_base_x) * (crack + 1) / 3)
                cy_pos = base_y + int((end_y - base_y) * (crack + 1) / 3)
                pygame.draw.line(surface, (120, 100, 70, f_alpha // 2),
                               (cx_pos - int(3 * scale), cy_pos - int(2 * scale)),
                               (cx_pos + int(3 * scale), cy_pos + int(2 * scale)), 1)
    
    elif wing_style == "snowflake_wings":
        # 霜寒：雪花翅膀 - 六角冰晶阵列
        for crystal in range(4):
            c_dist = int((15 + crystal * 12) * scale)
            c_angle = wing_side * (0.3 + crystal * 0.1)
            cx_pos = wing_base_x + int(math.cos(c_angle) * c_dist)
            cy_pos = wing_base_y + crystal * int(8 * scale) + int(math.sin(c_angle) * c_dist * 0.3)
            
            c_size = int((8 - crystal) * scale)
            c_rotation = t * 2 + crystal
            c_alpha = max(0, min(255, 220 - crystal * 35))
            
            # 六角冰晶
            for spoke in range(6):
                sp_angle = spoke * 1.047 + c_rotation
                sp_x = cx_pos + int(math.cos(sp_angle) * c_size)
                sp_y = cy_pos + int(math.sin(sp_angle) * c_size)
                pygame.draw.line(surface, (*theme["rune_primary"], c_alpha), (cx_pos, cy_pos), (sp_x, sp_y), max(1, int(1.5 * scale)))
                
                # 冰晶分叉
                for branch in [-0.5, 0.5]:
                    br_angle = sp_angle + branch
                    br_len = c_size * 0.4
                    pygame.draw.line(surface, (*theme["rune_primary"], max(0, c_alpha - 50)),
                                   (sp_x, sp_y), (sp_x + int(math.cos(br_angle) * br_len), sp_y + int(math.sin(br_angle) * br_len)), 1)
    
    elif wing_style == "fractal_wings":
        # 混沌：分形翅膀 - 无限递归图案（闪烁故障效果）
        for frac in range(6):
            # 随机偏移（故障效果）
            glitch_x = int(math.sin(t * 12 + frac * 3) * 3 * scale) if int(t * 10) % 7 == 0 else 0
            glitch_y = int(math.cos(t * 10 + frac * 2) * 2 * scale) if int(t * 10) % 11 == 0 else 0
            
            f_length = int((25 - frac * 3) * scale)
            f_angle = wing_side * (0.15 + frac * 0.12 + math.sin(t * 5 + frac) * 0.1)
            base_y = wing_base_y + frac * int(7 * scale)
            
            fx = wing_base_x + glitch_x
            fy = base_y + glitch_y
            end_x = fx + int(math.cos(f_angle) * f_length)
            end_y = fy + int(math.sin(f_angle) * f_length * 0.35)
            
            # 颜色闪烁
            color_shift = int(math.sin(t * 15 + frac) * 50)
            frac_color = (
                max(0, min(255, theme["rune_primary"][0] + color_shift)),
                max(0, min(255, theme["rune_primary"][1] - color_shift // 2)),
                max(0, min(255, theme["rune_primary"][2] + color_shift // 3))
            )
            f_alpha = max(0, min(255, int(180 * abs(math.sin(t * 8 + frac)))))
            
            pygame.draw.line(surface, (*frac_color, f_alpha), (fx, fy), (end_x, end_y), max(2, int(3 * scale)))
            
            # 分形分支
            for branch in range(2):
                bx = fx + int((end_x - fx) * (branch + 1) / 3)
                by = fy + int((end_y - fy) * (branch + 1) / 3)
                b_len = int(8 * scale)
                b_angle = f_angle + wing_side * 0.6 * (1 if branch % 2 == 0 else -1)
                pygame.draw.line(surface, (*frac_color, max(0, f_alpha - 40)),
                               (bx, by), (bx + int(math.cos(b_angle) * b_len), by + int(math.sin(b_angle) * b_len * 0.3)), 1)
    
    elif wing_style == "leaf_wings":
        # 自然：枝叶翅膀 - 藤蔓与叶片
        for branch in range(4):
            b_length = int((30 - branch * 5) * scale)
            b_angle = wing_side * (0.2 + branch * 0.15)
            base_y = wing_base_y + branch * int(9 * scale)
            
            # 藤蔓主干
            points = []
            for seg in range(8):
                seg_t = seg / 7
                wave = math.sin(t * 3 + seg * 0.4 + branch) * 3 * scale * seg_t
                px = wing_base_x + int(math.cos(b_angle) * b_length * seg_t) + int(wave * wing_side)
                py = base_y + int(math.sin(b_angle) * b_length * seg_t * 0.35)
                points.append((px, py))
            
            if len(points) > 2:
                b_alpha = max(0, min(255, 200 - branch * 30))
                pygame.draw.lines(surface, (80, 140, 60, b_alpha), False, points, max(2, int(3 * scale)))
            
            # 叶片
            for leaf in range(3):
                lx = wing_base_x + int((points[-1][0] - wing_base_x) * (leaf + 1) / 4)
                ly = base_y + int((points[-1][1] - base_y) * (leaf + 1) / 4)
                l_angle = b_angle + wing_side * 0.5 * (1 if leaf % 2 == 0 else -1)
                l_size = int(6 * scale)
                l_flutter = math.sin(t * 4 + leaf + branch) * 0.2
                
                leaf_points = [
                    (lx, ly),
                    (lx + int(math.cos(l_angle + l_flutter) * l_size), ly + int(math.sin(l_angle + l_flutter) * l_size * 0.5)),
                    (lx + int(math.cos(l_angle + l_flutter) * l_size * 0.6), ly + int(math.sin(l_angle + l_flutter) * l_size * 0.3) + int(2 * scale)),
                ]
                l_alpha = max(0, min(255, 180 - branch * 25))
                pygame.draw.polygon(surface, (*theme["rune_primary"], l_alpha), leaf_points)


def _draw_page_wings(surface, wing_base_x, wing_base_y, wing_side, theme, t, scale):
    """绘制经典书页羽翼"""
    for layer in range(4):
        feather_count = 6 - layer
        layer_offset = layer * int(3 * scale)
        
        for feather in range(feather_count):
            base_angle = wing_side * (0.25 + layer * 0.12)
            feather_spread = wing_side * feather * 0.22
            flutter_speed = 5 - layer * 0.5
            flutter_amount = 0.12 - layer * 0.02
            flutter = math.sin(t * flutter_speed + feather * 0.6 + layer * 0.8) * flutter_amount
            
            feather_angle = base_angle + feather_spread + flutter
            feather_length = int((28 - layer * 5 - feather * 1.5) * scale)
            
            start_x = wing_base_x + wing_side * layer_offset
            start_y = wing_base_y + feather * int(6 * scale) + layer * int(4 * scale)
            end_x = start_x + int(math.cos(feather_angle) * feather_length)
            end_y = start_y + int(math.sin(feather_angle) * feather_length * 0.45)
            
            feather_pulse = 0.6 + 0.4 * math.sin(t * 4 + feather * 0.8 + layer * 1.2)
            feather_alpha = max(0, min(255, int((240 - layer * 45) * feather_pulse)))
            feather_width = max(2, int((5 - layer * 0.8) * scale))
            
            if layer < 3:
                glow_alpha = max(0, feather_alpha // 3)
                pygame.draw.line(surface, (*theme["page_glow"], glow_alpha),
                                (start_x, start_y), (end_x, end_y), feather_width + int(4 * scale))
            
            inner_glow_alpha = max(0, feather_alpha // 2)
            pygame.draw.line(surface, (*theme["page_glow"], inner_glow_alpha),
                            (start_x, start_y), (end_x, end_y), feather_width + int(2 * scale))
            pygame.draw.line(surface, (*theme["page_color"], feather_alpha),
                            (start_x, start_y), (end_x, end_y), feather_width)
            
            spine_alpha = max(0, min(255, int(feather_alpha * 0.7)))
            pygame.draw.line(surface, (*theme["gold_trim"], spine_alpha),
                            (start_x, start_y), (end_x, end_y), max(1, feather_width // 2))


def _draw_eye_variant(surface, cx, eye_y, theme, t, scale, eye_radius):
    """根据涂装类型绘制不同风格的眼睛"""
    eye_type = theme.get("eye_type", "single_crystal")
    eye_pulse = 0.85 + 0.15 * math.sin(t * 2.5)
    
    if eye_type == "single_crystal":
        # 经典单水晶球全视之眼（使用原有逻辑）
        return False  # 返回False表示使用原有渲染
    
    elif eye_type == "arcane_lens":
        # 奥术透镜阵列 - 3层同心圆透镜
        for lens in range(3):
            lens_r = eye_radius * (1.2 - lens * 0.25)
            lens_rotation = t * (1 + lens * 0.3) * (1 if lens % 2 == 0 else -1)
            lens_alpha = max(0, min(255, int((180 - lens * 40) * eye_pulse)))
            
            # 透镜环
            pygame.draw.circle(surface, (*theme["rune_primary"], lens_alpha), (cx, eye_y), int(lens_r), max(2, int(2 * scale)))
            
            # 透镜刻度
            for mark in range(8):
                m_angle = lens_rotation + mark * 0.785
                mx1 = cx + int(math.cos(m_angle) * lens_r * 0.85)
                my1 = eye_y + int(math.sin(m_angle) * lens_r * 0.85)
                mx2 = cx + int(math.cos(m_angle) * lens_r)
                my2 = eye_y + int(math.sin(m_angle) * lens_r)
                pygame.draw.line(surface, (*theme["gold_trim"], lens_alpha), (mx1, my1), (mx2, my2), 1)
        
        # 中心聚焦点
        pygame.draw.circle(surface, (*theme["page_glow"], int(220 * eye_pulse)), (cx, eye_y), max(3, int(4 * scale)))
        pygame.draw.circle(surface, (255, 255, 255, 255), (cx, eye_y), max(2, int(2 * scale)))
        return True
    
    elif eye_type == "skull_socket":
        # 骷髅眼窝 - 绿焰燃烧
        # 眼窝
        pygame.draw.circle(surface, (30, 25, 20, 255), (cx, eye_y), eye_radius)
        pygame.draw.circle(surface, (50, 40, 35, 200), (cx, eye_y), eye_radius, max(2, int(3 * scale)))
        
        # 绿焰
        for flame in range(8):
            f_life = ((t * 30 + flame * 8) % 40) / 40
            f_angle = flame * 0.785 + math.sin(t * 4 + flame) * 0.3
            fx = cx + int(math.cos(f_angle) * eye_radius * 0.5 * (1 - f_life))
            fy = eye_y - int(f_life * eye_radius * 1.5)
            f_alpha = max(0, min(255, int(200 * (1 - f_life))))
            f_size = max(2, int((5 - f_life * 3) * scale))
            
            pygame.draw.circle(surface, (100, 255, 100, f_alpha), (fx, fy), f_size)
            pygame.draw.circle(surface, (200, 255, 200, max(0, f_alpha - 80)), (fx, fy), max(1, f_size - 1))
        
        # 核心光点
        core_pulse = 0.5 + 0.5 * math.sin(t * 6)
        pygame.draw.circle(surface, (100, 255, 100, int(255 * core_pulse)), (cx, eye_y), max(3, int(5 * scale)))
        return True
    
    elif eye_type == "divine_halo":
        # 神圣光轮 - 光环中嵌眼
        # 外层光轮
        for halo in range(3):
            halo_r = eye_radius * (1.8 - halo * 0.3)
            halo_rotation = t * 0.5 * (1 if halo % 2 == 0 else -1)
            halo_alpha = max(0, min(255, int((150 - halo * 35) * eye_pulse)))
            
            pygame.draw.circle(surface, (*theme["gold_trim"], halo_alpha // 2), (cx, eye_y), int(halo_r), max(2, int(3 * scale)))
            
            # 光轮装饰
            for deco in range(6):
                d_angle = halo_rotation + deco * 1.047
                dx = cx + int(math.cos(d_angle) * halo_r)
                dy = eye_y + int(math.sin(d_angle) * halo_r)
                pygame.draw.circle(surface, (*theme["page_glow"], halo_alpha), (dx, dy), max(2, int(2 * scale)))
        
        # 中心圣眼
        pygame.draw.circle(surface, (255, 255, 240, 255), (cx, eye_y), int(eye_radius * 0.6))
        pygame.draw.circle(surface, (*theme["gold_trim"], 255), (cx, eye_y), int(eye_radius * 0.35))
        pygame.draw.circle(surface, (255, 255, 200, 255), (cx, eye_y), int(eye_radius * 0.15))
        return True
    
    elif eye_type == "demon_eye":
        # 恶魔之眼 - 竖瞳，血红巩膜
        # 血红巩膜
        pygame.draw.circle(surface, (200, 50, 50, 255), (cx, eye_y), eye_radius)
        
        # 血丝
        for vein in range(12):
            v_angle = vein * 0.524
            vx1 = cx + int(math.cos(v_angle) * eye_radius * 0.3)
            vy1 = eye_y + int(math.sin(v_angle) * eye_radius * 0.3)
            vx2 = cx + int(math.cos(v_angle) * eye_radius * 0.95)
            vy2 = eye_y + int(math.sin(v_angle) * eye_radius * 0.95)
            pygame.draw.line(surface, (150, 30, 30, 180), (vx1, vy1), (vx2, vy2), 1)
        
        # 黄色虹膜
        pygame.draw.circle(surface, (255, 180, 50, 255), (cx, eye_y), int(eye_radius * 0.55))
        
        # 竖瞳
        pupil_h = int(eye_radius * 0.8)
        pupil_w = int(eye_radius * 0.15) + int(math.sin(t * 4) * eye_radius * 0.08)
        pygame.draw.ellipse(surface, (0, 0, 0, 255), 
                           (cx - pupil_w, eye_y - pupil_h // 2, pupil_w * 2, pupil_h))
        return True
    
    elif eye_type == "void_maw":
        # 虚空巨口 - 深渊之眼
        # 深邃虚空
        pygame.draw.circle(surface, (10, 0, 20, 255), (cx, eye_y), eye_radius)
        
        # 虚空漩涡
        for swirl in range(20):
            s_angle = t * 2 + swirl * 0.314
            s_dist = eye_radius * (1 - (swirl / 20))
            sx = cx + int(math.cos(s_angle) * s_dist)
            sy = eye_y + int(math.sin(s_angle) * s_dist)
            s_alpha = max(0, min(255, 150 - swirl * 6))
            pygame.draw.circle(surface, (*theme["rune_primary"], s_alpha), (sx, sy), max(1, int(2 * scale)))
        
        # 中心深渊
        pygame.draw.circle(surface, (0, 0, 0, 255), (cx, eye_y), int(eye_radius * 0.4))
        # 深渊中的微光
        for spark in range(3):
            sp_angle = t * 3 + spark * 2.094
            sp_dist = eye_radius * 0.2
            spx = cx + int(math.cos(sp_angle) * sp_dist)
            spy = eye_y + int(math.sin(sp_angle) * sp_dist)
            sp_alpha = int(150 * abs(math.sin(t * 5 + spark)))
            pygame.draw.circle(surface, (*theme["rune_primary"], sp_alpha), (spx, spy), max(1, int(1.5 * scale)))
        return True
    
    elif eye_type == "galaxy_core":
        # 银河核心 - 旋转星云
        # 星云背景
        pygame.draw.circle(surface, (20, 30, 60, 255), (cx, eye_y), eye_radius)
        
        # 旋转星云臂
        for arm in range(3):
            arm_angle = t * 1.5 + arm * 2.094
            for star in range(15):
                s_t = star / 14
                s_angle = arm_angle + s_t * 3.14
                s_dist = eye_radius * s_t * 0.9
                sx = cx + int(math.cos(s_angle) * s_dist)
                sy = eye_y + int(math.sin(s_angle) * s_dist)
                s_alpha = max(0, min(255, int(200 * (1 - s_t * 0.5))))
                s_size = max(1, int((2 + (1 - s_t) * 2) * scale))
                pygame.draw.circle(surface, (*theme["page_glow"], s_alpha), (sx, sy), s_size)
        
        # 核心亮点
        pygame.draw.circle(surface, (255, 255, 200, 255), (cx, eye_y), max(3, int(4 * scale)))
        pygame.draw.circle(surface, (255, 255, 255, 255), (cx, eye_y), max(2, int(2 * scale)))
        return True
    
    elif eye_type == "bloodshot_eye":
        # 充血之眼 - 血丝密布
        # 淡红眼白
        pygame.draw.circle(surface, (255, 220, 220, 255), (cx, eye_y), eye_radius)
        
        # 密集血丝
        for vein in range(20):
            v_angle = vein * 0.314 + math.sin(t * 2 + vein) * 0.1
            v_length = eye_radius * (0.5 + random.Random(vein).random() * 0.45)
            vx1 = cx + int(math.cos(v_angle) * eye_radius * 0.2)
            vy1 = eye_y + int(math.sin(v_angle) * eye_radius * 0.2)
            vx2 = cx + int(math.cos(v_angle) * v_length)
            vy2 = eye_y + int(math.sin(v_angle) * v_length)
            v_pulse = 0.5 + 0.5 * math.sin(t * 4 + vein)
            v_alpha = max(0, min(255, int(180 * v_pulse)))
            pygame.draw.line(surface, (200, 50, 50, v_alpha), (vx1, vy1), (vx2, vy2), 1)
        
        # 血红虹膜
        pygame.draw.circle(surface, (180, 30, 50, 255), (cx, eye_y), int(eye_radius * 0.5))
        # 瞳孔
        pygame.draw.circle(surface, (0, 0, 0, 255), (cx, eye_y), int(eye_radius * 0.25))
        return True
    
    elif eye_type == "amber_eye":
        # 琥珀之眼 - 封存虫子
        # 琥珀色眼球
        pygame.draw.circle(surface, (200, 150, 80, 255), (cx, eye_y), eye_radius)
        pygame.draw.circle(surface, (180, 130, 60, 200), (cx, eye_y), eye_radius, max(2, int(3 * scale)))
        
        # 琥珀光泽
        for gleam in range(3):
            g_angle = gleam * 2.094 + 0.5
            gx = cx + int(math.cos(g_angle) * eye_radius * 0.5)
            gy = eye_y + int(math.sin(g_angle) * eye_radius * 0.5)
            pygame.draw.circle(surface, (255, 220, 150, 100), (gx, gy), max(2, int(3 * scale)))
        
        # 封存的古老符文
        draw_rune_symbol(surface, cx, eye_y, eye_radius * 0.5, t * 0.2, theme["rune_primary"], 180)
        
        # 高光
        pygame.draw.circle(surface, (255, 255, 200, 200), (cx - int(3 * scale), eye_y - int(3 * scale)), max(2, int(3 * scale)))
        return True
    
    elif eye_type == "frozen_tear":
        # 冰封之泪 - 冰滴形态
        # 冰滴形状（菱形）
        tear_points = [
            (cx, eye_y - int(eye_radius * 1.2)),
            (cx + eye_radius, eye_y),
            (cx, eye_y + int(eye_radius * 0.6)),
            (cx - eye_radius, eye_y),
        ]
        pygame.draw.polygon(surface, (200, 230, 255, 255), tear_points)
        pygame.draw.polygon(surface, (150, 200, 255, 200), tear_points, max(2, int(2 * scale)))
        
        # 冰晶纹理
        for ice_line in range(4):
            il_angle = ice_line * 0.785 + 0.393
            ilx1 = cx
            ily1 = eye_y
            ilx2 = cx + int(math.cos(il_angle) * eye_radius * 0.7)
            ily2 = eye_y + int(math.sin(il_angle) * eye_radius * 0.5)
            pygame.draw.line(surface, (180, 220, 255, 150), (ilx1, ily1), (ilx2, ily2), 1)
        
        # 中心光点
        pygame.draw.circle(surface, (255, 255, 255, 255), (cx, eye_y - int(eye_radius * 0.3)), max(2, int(3 * scale)))
        return True
    
    elif eye_type == "kaleidoscope":
        # 万花筒之眼 - 不断变形
        # 闪烁背景
        bg_hue = int(t * 50) % 360
        bg_color = _hsv_to_rgb(bg_hue, 0.5, 0.3)
        pygame.draw.circle(surface, (*bg_color, 255), (cx, eye_y), eye_radius)
        
        # 万花筒图案
        segment_count = 6
        for seg in range(segment_count):
            seg_angle = t * 2 + seg * (6.28 / segment_count)
            for ring in range(4):
                r_dist = eye_radius * (0.2 + ring * 0.2)
                px = cx + int(math.cos(seg_angle) * r_dist)
                py = eye_y + int(math.sin(seg_angle) * r_dist)
                
                p_hue = (bg_hue + seg * 30 + ring * 20) % 360
                p_color = _hsv_to_rgb(p_hue, 0.8, 1.0)
                p_alpha = max(0, min(255, 200 - ring * 30))
                p_size = max(1, int((3 - ring * 0.5) * scale))
                
                pygame.draw.circle(surface, (*p_color, p_alpha), (px, py), p_size)
        
        # 中心核心
        core_hue = (bg_hue + 180) % 360
        core_color = _hsv_to_rgb(core_hue, 1.0, 1.0)
        pygame.draw.circle(surface, (*core_color, 255), (cx, eye_y), max(3, int(4 * scale)))
        return True
    
    elif eye_type == "forest_spirit":
        # 森灵之眼 - 绿光瞳孔
        # 树皮纹理眼眶
        pygame.draw.circle(surface, (100, 80, 50, 255), (cx, eye_y), eye_radius)
        
        # 年轮纹理
        for ring in range(5):
            ring_r = eye_radius * (0.3 + ring * 0.15)
            ring_alpha = 150 - ring * 20
            pygame.draw.circle(surface, (80, 60, 40, ring_alpha), (cx, eye_y), int(ring_r), 1)
        
        # 翠绿瞳孔
        pygame.draw.circle(surface, (80, 180, 80, 255), (cx, eye_y), int(eye_radius * 0.5))
        
        # 灵光闪烁
        for spark in range(5):
            sp_angle = t * 3 + spark * 1.257
            sp_dist = eye_radius * 0.3
            spx = cx + int(math.cos(sp_angle) * sp_dist)
            spy = eye_y + int(math.sin(sp_angle) * sp_dist)
            sp_alpha = int(200 * abs(math.sin(t * 4 + spark)))
            pygame.draw.circle(surface, (150, 255, 150, sp_alpha), (spx, spy), max(1, int(2 * scale)))
        
        # 瞳孔核心
        pygame.draw.circle(surface, (50, 120, 50, 255), (cx, eye_y), int(eye_radius * 0.2))
        return True
    
    return False  # 未知类型，使用默认渲染


def _hsv_to_rgb(h, s, v):
    """HSV转RGB"""
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))



    """绘制复杂多层魔法阵"""
    base_alpha = max(0, min(255, int(200 * alpha_mult)))
    
    # 外圈 - 粗实线
    pygame.draw.circle(surface, (*theme["gold_trim"], base_alpha), 
                      (cx, cy), int(radius), max(2, int(radius * 0.04)))
    
    # 内圈装饰线
    for ring in range(complexity):
        ring_radius = radius * (0.85 - ring * 0.15)
        ring_alpha = max(0, min(255, int(base_alpha * (0.9 - ring * 0.15))))
        pygame.draw.circle(surface, (*theme["rune_primary"], ring_alpha),
                          (cx, cy), int(ring_radius), max(1, int(radius * 0.02)))
    
    # 六芒星/八芒星
    star_points = 6 + (complexity % 3) * 2
    for i in range(star_points):
        angle1 = rotation + i * (math.pi * 2 / star_points)
        angle2 = rotation + (i + star_points // 2) * (math.pi * 2 / star_points)
        x1 = cx + int(math.cos(angle1) * radius * 0.9)
        y1 = cy + int(math.sin(angle1) * radius * 0.9)
        x2 = cx + int(math.cos(angle2) * radius * 0.9)
        y2 = cy + int(math.sin(angle2) * radius * 0.9)
        line_alpha = max(0, min(255, int(base_alpha * 0.7)))
        pygame.draw.line(surface, (*theme["gold_trim"], line_alpha),
                        (x1, y1), (x2, y2), max(1, int(radius * 0.02)))
    
    # 符文点位
    rune_count = 12 + complexity * 4
    for i in range(rune_count):
        rune_angle = rotation * 0.5 + i * (math.pi * 2 / rune_count)
        rune_radius = radius * (0.7 + 0.2 * math.sin(i * 0.5))
        rx = cx + int(math.cos(rune_angle) * rune_radius)
        ry = cy + int(math.sin(rune_angle) * rune_radius)
        rune_size = radius * 0.08
        rune_alpha = max(0, min(255, int(base_alpha * 0.8)))
        draw_rune_symbol(surface, rx, ry, rune_size, rune_angle, theme["rune_primary"], rune_alpha)


def render_magnus_plane(surface, color, x, y, w, h, frame, style="magnus_default"):
    """
    渲染MAGNUS机体 - 真理之书魔法书飞行器
    超精细版本 - 2500+行极致细节
    
    渲染层级：
    1. 远景魔力星云背景
    2. 环绕符文粒子云
    3. 外层护盾魔法阵
    4. 书籍主体（极致精细）
    5. 附属浮游魔法书
    6. 书页天使羽翼
    7. 封印锁链系统
    8. 全视之眼核心
    9. 希腊字母拖尾
    10. 涂装专属特效
    """
    if style.startswith("magnus_"):
        theme_name = style[7:]
    else:
        theme_name = style if style in MAGNUS_THEMES else "default"
    
    theme = get_magnus_theme(theme_name)
    cx = x + w // 2
    cy = y + h // 2
    scale = min(w, h) / 100 * 2.2  # 放大整体比例
    t = frame * 0.05
    
    # 悬浮呼吸动画
    hover = int(math.sin(t * 1.5) * 3 * scale)
    cy += hover
    
    # 书籍核心参数（放大书籍）
    book_width = int(95 * scale)    # 书宽（展开后两页总宽）- 放大
    book_height = int(62 * scale)   # 书高 - 放大
    book_depth = int(16 * scale)    # 书厚
    spine_width = int(12 * scale)   # 书脊宽
    
    # ============================================================
    #   第一层：远景魔力星云背景 - 螺旋魔力涡流（外围）
    # ============================================================
    for spiral_arm in range(4):  # 4个螺旋臂
        arm_offset = spiral_arm * 1.571  # 90度分布
        arm_color_shift = int(math.sin(t * 2 + spiral_arm) * 30)
        for trail in range(20):  # 减少数量
            trail_progress = (t * 1.2 + trail * 0.15 + arm_offset) % 6.28
            trail_dist = 65 + trail * 2.5  # 起始距离更远
            trail_x = cx + int(math.cos(trail_progress) * trail_dist * scale)
            trail_y = cy + int(math.sin(trail_progress) * trail_dist * scale * 0.45)
            trail_size = max(1, int((20 - trail) / 5))
            trail_alpha = max(0, min(255, 80 - trail * 3))
            if trail_alpha > 0:
                nebula_color = (
                    max(0, min(255, theme["rune_primary"][0] + arm_color_shift)),
                    max(0, min(255, theme["rune_primary"][1] - abs(arm_color_shift) // 2)),
                    max(0, min(255, theme["rune_primary"][2] + arm_color_shift // 2))
                )
                pygame.draw.circle(surface, (*nebula_color, trail_alpha), 
                                 (trail_x, trail_y), trail_size)
    
    # 背景魔力雾气层（移到更外围）
    for mist in range(12):  # 减少数量
        mist_angle = t * 0.5 + mist * 0.524
        mist_dist = (70 + math.sin(t * 1.5 + mist) * 10) * scale  # 更远
        mist_x = cx + int(math.cos(mist_angle) * mist_dist)
        mist_y = cy + int(math.sin(mist_angle) * mist_dist * 0.4)
        mist_pulse = 0.4 + 0.6 * math.sin(t * 2 + mist * 0.5)
        mist_alpha = max(0, min(255, int(35 * mist_pulse)))  # 更淡
        mist_size = int((5 + math.sin(t * 3 + mist) * 2) * scale)
        pygame.draw.circle(surface, (*theme["spirit"], mist_alpha), (mist_x, mist_y), mist_size)
    
    # ============================================================
    #   第二层：环绕符文粒子云 - 单层轨道（远外围）
    # ============================================================
    orbit_radius = 75  # 移到更外围
    particle_count = 16  # 减少数量
    for particle in range(particle_count):
        p_angle = t * 1.2 + particle * (6.28 / particle_count)
        p_dist = orbit_radius + 4 * math.sin(t * 4 + particle * 0.5)
        p_x = cx + int(math.cos(p_angle) * p_dist * scale)
        p_y = cy + int(math.sin(p_angle) * p_dist * scale * 0.4)
        p_pulse = 0.5 + 0.5 * math.sin(t * 5 + particle * 1.1)
        p_size = max(1, int(2.5 * p_pulse))
        p_alpha = max(0, min(255, int(120 * p_pulse)))
        pygame.draw.circle(surface, (*theme["rune_secondary"], p_alpha), (p_x, p_y), p_size)
    
    # ============================================================
    #   第三层：外层护盾魔法阵 - 双层嵌套法阵（远外围）
    # ============================================================
    for ring_layer in range(2):  # 减少为2层
        ring_radius = (70 - ring_layer * 8) * scale  # 移到更外围
        ring_rotation = t * (0.25 + ring_layer * 0.1) * (1 if ring_layer % 2 == 0 else -1)
        ring_pulse = 0.7 + 0.3 * math.sin(t * 2.5 + ring_layer)
        ring_alpha = max(0, min(255, int((100 - ring_layer * 30) * ring_pulse)))  # 更淡
        
        # 外圈主线
        pygame.draw.circle(surface, (*theme["gold_trim"], ring_alpha), 
                          (cx, cy), int(ring_radius), max(1, int((2 - ring_layer) * scale)))
        
        # 装饰弧线段（简化）
        arc_count = 6 + ring_layer * 2
        for arc in range(arc_count):
            arc_start = ring_rotation + arc * (6.28 / arc_count)
            arc_end = arc_start + 6.28 / arc_count / 3
            arc_alpha = max(0, min(255, int(ring_alpha * 0.6)))
            for seg in range(5):
                seg_angle = arc_start + (arc_end - arc_start) * seg / 4
                seg_x = cx + int(math.cos(seg_angle) * ring_radius)
                seg_y = cy + int(math.sin(seg_angle) * ring_radius * 0.45)
                pygame.draw.circle(surface, (*theme["rune_primary"], arc_alpha), (seg_x, seg_y), max(1, int(scale)))
        
        # 法阵节点
        node_count = 6 + ring_layer * 2
        for node in range(node_count):
            node_angle = ring_rotation * 0.5 + node * (6.28 / node_count)
            node_x = cx + int(math.cos(node_angle) * ring_radius)
            node_y = cy + int(math.sin(node_angle) * ring_radius * 0.45)
            node_pulse = 0.6 + 0.4 * math.sin(t * 4 + node)
            node_size = max(2, int((4 - ring_layer) * scale * node_pulse))
            node_alpha = max(0, min(255, int(ring_alpha * node_pulse)))
            
            # 节点核心
            pygame.draw.circle(surface, (*theme["rune_primary"], node_alpha), (node_x, node_y), node_size)
            # 节点光晕
            pygame.draw.circle(surface, (*theme["page_glow"], node_alpha // 2), (node_x, node_y), node_size + 2)
            
            # 符文装饰
            if ring_layer == 0 and node % 2 == 0:
                draw_rune_symbol(surface, node_x, node_y, 5 * scale, node_angle + t, theme["rune_primary"], node_alpha)
        
        # 星芒连线
        if ring_layer < 2:
            star_points = 5 + ring_layer
            for i in range(star_points):
                angle1 = ring_rotation + i * (6.28 / star_points)
                angle2 = ring_rotation + (i + star_points // 2) * (6.28 / star_points)
                x1 = cx + int(math.cos(angle1) * ring_radius * 0.95)
                y1 = cy + int(math.sin(angle1) * ring_radius * 0.95 * 0.45)
                x2 = cx + int(math.cos(angle2) * ring_radius * 0.95)
                y2 = cy + int(math.sin(angle2) * ring_radius * 0.95 * 0.45)
                line_alpha = max(0, min(255, int(ring_alpha * 0.5)))
                pygame.draw.line(surface, (*theme["gold_trim"], line_alpha), (x1, y1), (x2, y2), 1)
    
    # ============================================================
    #   第四层：书籍主体 - 超精细魔法古籍
    # ============================================================
    
    # ---------- 4.1 底层阴影（多层渐变） ----------
    shadow_layers = 10
    for i in range(shadow_layers):
        shadow_alpha = max(0, 50 - i * 5)
        shadow_offset = i * 2
        shadow_w = book_width + 50 - i * 4
        shadow_h = int((book_height + 50 - i * 4) * 0.5)
        shadow_x = cx - shadow_w // 2 - 25 + shadow_offset
        shadow_y = cy + book_height // 2 - 5 + shadow_offset
        pygame.draw.ellipse(surface, (10, 5, 20, shadow_alpha),
                           (shadow_x, shadow_y, shadow_w, shadow_h))
    
    # ---------- 4.2 书页厚度层（底部可见的书页堆叠） ----------
    # 多层书页堆叠效果
    page_layers = 8
    for layer in range(page_layers):
        layer_offset = layer * 1.5
        layer_alpha = max(0, min(255, 200 - layer * 15))
        layer_color_shift = layer * 8
        
        # 左侧书页堆
        left_stack = [
            (cx - spine_width // 2 - 2, cy + book_height // 2 - 2 + layer_offset),
            (cx - book_width // 2 + 6, cy + book_height // 2 - 2 + layer_offset),
            (cx - book_width // 2 + 6, cy + book_height // 2 + book_depth - layer_offset),
            (cx - spine_width // 2 - 2, cy + book_height // 2 + book_depth - layer_offset),
        ]
        left_color = (
            max(0, theme["page_color"][0] - layer_color_shift),
            max(0, theme["page_color"][1] - layer_color_shift),
            max(0, theme["page_color"][2] - layer_color_shift)
        )
        pygame.draw.polygon(surface, (*left_color, layer_alpha), left_stack)
        
        # 右侧书页堆
        right_stack = [
            (cx + spine_width // 2 + 2, cy + book_height // 2 - 2 + layer_offset),
            (cx + book_width // 2 - 6, cy + book_height // 2 - 2 + layer_offset),
            (cx + book_width // 2 - 6, cy + book_height // 2 + book_depth - layer_offset),
            (cx + spine_width // 2 + 2, cy + book_height // 2 + book_depth - layer_offset),
        ]
        pygame.draw.polygon(surface, (*left_color, layer_alpha), right_stack)
    
    # 书页横线纹理（精细）
    for i in range(10):
        line_y = cy + book_height // 2 + int((i + 1) * book_depth / 11)
        line_pulse = 0.5 + 0.5 * math.sin(t * 4 + i * 0.3)
        line_alpha = max(0, min(255, int(100 * line_pulse)))
        # 左侧
        pygame.draw.line(surface, (*theme["book_spine"], line_alpha),
                        (cx - book_width // 2 + 10, line_y), (cx - spine_width // 2 - 4, line_y), 1)
        # 右侧
        pygame.draw.line(surface, (*theme["book_spine"], line_alpha),
                        (cx + spine_width // 2 + 4, line_y), (cx + book_width // 2 - 10, line_y), 1)
    
    # ---------- 4.3 书脊主体（中央脊柱 - 超精细） ----------
    spine_points = [
        (cx - spine_width // 2, cy - book_height // 2 + 6),
        (cx + spine_width // 2, cy - book_height // 2 + 6),
        (cx + spine_width // 2, cy + book_height // 2 + book_depth),
        (cx - spine_width // 2, cy + book_height // 2 + book_depth),
    ]
    pygame.draw.polygon(surface, (*theme["book_spine"], 255), spine_points)
    
    # 书脊皮革纹理
    for tex in range(15):
        tex_y = cy - book_height // 2 + 8 + int(tex * (book_height + book_depth - 10) / 14)
        tex_pulse = 0.7 + 0.3 * math.sin(t * 2 + tex * 0.5)
        tex_alpha = max(0, min(255, int(80 * tex_pulse)))
        pygame.draw.line(surface, (*theme["book_cover"], tex_alpha),
                        (cx - spine_width // 2 + 2, tex_y), (cx + spine_width // 2 - 2, tex_y), 1)
    
    # 书脊金属装饰条（5条）
    for band in range(5):
        band_y = cy - book_height // 2 + int((15 + band * 12) * scale / 2)
        band_pulse = 0.8 + 0.2 * math.sin(t * 3 + band * 0.6)
        band_alpha = max(0, min(255, int(240 * band_pulse)))
        band_width = max(2, int(2.5 * scale))
        
        # 金属条主体
        pygame.draw.line(surface, (*theme["gold_trim"], band_alpha),
                        (cx - spine_width // 2 - 2, band_y), (cx + spine_width // 2 + 2, band_y), band_width)
        # 金属条高光
        pygame.draw.line(surface, (255, 255, 255, max(0, band_alpha - 80)),
                        (cx - spine_width // 2, band_y - 1), (cx + spine_width // 2, band_y - 1), 1)
        
        # 金属条两端铆钉
        rivet_size = max(2, int(2 * scale))
        pygame.draw.circle(surface, (*theme["gold_trim"], band_alpha),
                          (cx - spine_width // 2 - 1, band_y), rivet_size)
        pygame.draw.circle(surface, (*theme["gold_trim"], band_alpha),
                          (cx + spine_width // 2 + 1, band_y), rivet_size)
    
    # 书脊中央大型徽章
    spine_badge_y = cy
    spine_badge_size = int(8 * scale)
    spine_badge_pulse = 0.7 + 0.3 * math.sin(t * 2)
    spine_badge_alpha = max(0, min(255, int(255 * spine_badge_pulse)))
    
    # 徽章底座
    pygame.draw.circle(surface, (*theme["gold_trim"], spine_badge_alpha),
                      (cx, spine_badge_y), spine_badge_size)
    # 徽章内圈
    pygame.draw.circle(surface, (*theme["book_spine"], spine_badge_alpha),
                      (cx, spine_badge_y), int(spine_badge_size * 0.7))
    # 徽章宝石
    pygame.draw.circle(surface, (*theme["rune_primary"], spine_badge_alpha),
                      (cx, spine_badge_y), int(spine_badge_size * 0.4))
    # 宝石高光
    pygame.draw.circle(surface, (255, 255, 255, max(0, spine_badge_alpha - 50)),
                      (cx - int(scale), spine_badge_y - int(scale)), max(1, int(1.5 * scale)))
    
    # ---------- 4.4 左右封面（皮革质感 - 超精细） ----------
    # 左封面
    left_cover = [
        (cx - spine_width // 2, cy - book_height // 2 + 4),
        (cx - book_width // 2, cy - book_height // 2 + 10),
        (cx - book_width // 2, cy + book_height // 2 + 4),
        (cx - spine_width // 2, cy + book_height // 2),
    ]
    pygame.draw.polygon(surface, (*theme["book_cover"], 255), left_cover)
    
    # 右封面
    right_cover = [
        (cx + spine_width // 2, cy - book_height // 2 + 4),
        (cx + book_width // 2, cy - book_height // 2 + 10),
        (cx + book_width // 2, cy + book_height // 2 + 4),
        (cx + spine_width // 2, cy + book_height // 2),
    ]
    pygame.draw.polygon(surface, (*theme["book_cover"], 255), right_cover)
    
    # 封面金边装饰
    pygame.draw.polygon(surface, (*theme["gold_trim"], 200), left_cover, max(2, int(2.5 * scale)))
    pygame.draw.polygon(surface, (*theme["gold_trim"], 200), right_cover, max(2, int(2.5 * scale)))
    
    # 封面皮革纹理（压花效果）
    for side in [-1, 1]:
        cover_cx = cx + side * (book_width // 4 + spine_width // 4)
        
        # 主框装饰线
        frame_w = int(25 * scale)
        frame_h = int(35 * scale)
        frame_pulse = 0.8 + 0.2 * math.sin(t * 2 + side)
        frame_alpha = max(0, min(255, int(150 * frame_pulse)))
        
        # 外框
        frame_points = [
            (cover_cx - frame_w // 2, cy - frame_h // 2),
            (cover_cx + frame_w // 2, cy - frame_h // 2),
            (cover_cx + frame_w // 2, cy + frame_h // 2),
            (cover_cx - frame_w // 2, cy + frame_h // 2),
        ]
        pygame.draw.polygon(surface, (*theme["gold_trim"], frame_alpha), frame_points, max(1, int(scale)))
        
        # 内框
        inner_w = int(18 * scale)
        inner_h = int(28 * scale)
        inner_points = [
            (cover_cx - inner_w // 2, cy - inner_h // 2),
            (cover_cx + inner_w // 2, cy - inner_h // 2),
            (cover_cx + inner_w // 2, cy + inner_h // 2),
            (cover_cx - inner_w // 2, cy + inner_h // 2),
        ]
        pygame.draw.polygon(surface, (*theme["gold_trim"], max(0, frame_alpha - 40)), inner_points, 1)
        
        # 角落花纹
        corner_size = int(5 * scale)
        for corner_idx in range(4):
            corner_x = cover_cx + (1 if corner_idx % 2 else -1) * (frame_w // 2 - corner_size // 2)
            corner_y = cy + (1 if corner_idx >= 2 else -1) * (frame_h // 2 - corner_size // 2)
            corner_pulse = 0.6 + 0.4 * math.sin(t * 3 + corner_idx)
            corner_alpha = max(0, min(255, int(frame_alpha * corner_pulse)))
            
            # 角落圆形装饰
            pygame.draw.circle(surface, (*theme["gold_trim"], corner_alpha), (corner_x, corner_y), corner_size)
            pygame.draw.circle(surface, (*theme["rune_secondary"], max(0, corner_alpha - 30)),
                              (corner_x, corner_y), int(corner_size * 0.6))
    
    # ---------- 4.5 内页（羊皮纸书页 - 超精细） ----------
    page_margin = int(6 * scale)
    
    # 左页
    left_page = [
        (cx - spine_width // 2 - 3, cy - book_height // 2 + 10 + page_margin),
        (cx - book_width // 2 + page_margin + 4, cy - book_height // 2 + 16 + page_margin),
        (cx - book_width // 2 + page_margin + 4, cy + book_height // 2 - page_margin),
        (cx - spine_width // 2 - 3, cy + book_height // 2 - page_margin - 4),
    ]
    pygame.draw.polygon(surface, (*theme["page_color"], 255), left_page)
    
    # 右页
    right_page = [
        (cx + spine_width // 2 + 3, cy - book_height // 2 + 10 + page_margin),
        (cx + book_width // 2 - page_margin - 4, cy - book_height // 2 + 16 + page_margin),
        (cx + book_width // 2 - page_margin - 4, cy + book_height // 2 - page_margin),
        (cx + spine_width // 2 + 3, cy + book_height // 2 - page_margin - 4),
    ]
    pygame.draw.polygon(surface, (*theme["page_color"], 255), right_page)
    
    # 书页边缘阴影
    edge_alpha = 60
    pygame.draw.polygon(surface, (*theme["book_spine"], edge_alpha), left_page, 1)
    pygame.draw.polygon(surface, (*theme["book_spine"], edge_alpha), right_page, 1)
    
    # ---------- 4.6 书页符文文字（静态装饰） ----------
    text_lines = 10
    for line in range(text_lines):
        line_y = cy - book_height // 2 + int((24 + line * 5) * scale / 2)
        line_alpha = 60  # 静态淡色
        
        # 左页文字
        for seg in range(4):
            seed = random.Random(line * 100 + seg)
            seg_len = int((5 + seed.random() * 6) * scale / 2)
            seg_start = cx - book_width // 2 + int((18 + seg * 12) * scale / 2)
            if seg_start + seg_len < cx - spine_width // 2 - 6:
                pygame.draw.line(surface, (*theme["rune_secondary"], line_alpha),
                                (seg_start, line_y), (seg_start + seg_len, line_y), 1)
        
        # 右页文字
        for seg in range(4):
            seed = random.Random(line * 100 + seg + 500)
            seg_len = int((5 + seed.random() * 6) * scale / 2)
            seg_start = cx + spine_width // 2 + int((12 + seg * 12) * scale / 2)
            if seg_start + seg_len < cx + book_width // 2 - 14:
                pygame.draw.line(surface, (*theme["rune_secondary"], line_alpha),
                                (seg_start, line_y), (seg_start + seg_len, line_y), 1)
    
    # 首字母装饰（简化为静态）
    for side in [-1, 1]:
        initial_x = cx + side * (book_width // 4)
        initial_y = cy - book_height // 2 + int(25 * scale / 2)
        initial_alpha = 100  # 静态
        initial_size = int(5 * scale)
        pygame.draw.rect(surface, (*theme["rune_primary"], initial_alpha),
                        (initial_x - initial_size, initial_y - initial_size,
                         initial_size * 2, initial_size * 2), 1)
    
    # ---------- 4.7 书页中央装饰（简化为静态圆形） ----------
    for side in [-1, 1]:
        circle_x = cx + side * (book_width // 4 + spine_width // 4)
        circle_y = cy + int(5 * scale)
        circle_radius = int(10 * scale)
        circle_alpha = 80  # 静态淡色
        
        # 简单同心圆
        pygame.draw.circle(surface, (*theme["rune_primary"], circle_alpha // 2),
                          (circle_x, circle_y), circle_radius)
        pygame.draw.circle(surface, (*theme["rune_primary"], circle_alpha),
                          (circle_x, circle_y), circle_radius, 1)
        pygame.draw.circle(surface, (*theme["gold_trim"], circle_alpha),
                          (circle_x, circle_y), int(circle_radius * 0.6), 1)
    
    # ---------- 4.8 封面中央徽章（简化静态） ----------
    for side in [-1, 1]:
        badge_x = cx + side * (book_width // 4 + spine_width // 4)
        badge_y = cy
        badge_size = int(12 * scale)
        badge_alpha = 180  # 静态
        
        # 徽章底座
        pygame.draw.circle(surface, (*theme["gold_trim"], badge_alpha),
                          (badge_x, badge_y), badge_size, max(1, int(2 * scale)))
        
        # 徽章内圈
        pygame.draw.circle(surface, (*theme["book_cover"], badge_alpha),
                          (badge_x, badge_y), int(badge_size * 0.6))
        
        # 中心宝石
        pygame.draw.circle(surface, (*theme["rune_primary"], 200),
                          (badge_x, badge_y), int(badge_size * 0.3))
    
    # ---------- 4.9 四角金属包角（超精细） ----------
    corner_size = int(12 * scale)
    corners_data = [
        (cx - book_width // 2, cy - book_height // 2 + 10, -0.785, -1),
        (cx + book_width // 2, cy - book_height // 2 + 10, 0.785, 1),
        (cx - book_width // 2, cy + book_height // 2 + 4, -2.356, -1),
        (cx + book_width // 2, cy + book_height // 2 + 4, 2.356, 1),
    ]
    
    for corner_x, corner_y, angle, direction in corners_data:
        # 包角主体（多层）
        for layer in range(3):
            layer_size = corner_size - layer * int(2 * scale)
            layer_alpha = max(0, min(255, 255 - layer * 30))
            
            c_pts = [
                (corner_x, corner_y - int(layer_size * 0.7)),
                (corner_x + int(direction * layer_size * 0.9), corner_y),
                (corner_x, corner_y + int(layer_size * 0.7)),
            ]
            pygame.draw.polygon(surface, (*theme["gold_trim"], layer_alpha), c_pts)
        
        # 包角内层装饰
        inner_pts = [
            (corner_x, corner_y - int(corner_size * 0.4)),
            (corner_x + int(direction * corner_size * 0.5), corner_y),
            (corner_x, corner_y + int(corner_size * 0.4)),
        ]
        pygame.draw.polygon(surface, (*theme["book_cover"], 200), inner_pts)
        
        # 铆钉（3个）
        for rivet in range(3):
            rivet_offset = (rivet - 1) * int(corner_size * 0.35)
            rivet_x = corner_x + int(direction * corner_size * 0.3)
            rivet_y = corner_y + rivet_offset
            rivet_pulse = 0.8 + 0.2 * math.sin(t * 4 + rivet + angle)
            rivet_alpha = max(0, min(255, int(230 * rivet_pulse)))
            
            pygame.draw.circle(surface, (*theme["gold_trim"], rivet_alpha),
                              (rivet_x, rivet_y), max(2, int(2 * scale)))
            pygame.draw.circle(surface, (255, 255, 255, max(0, rivet_alpha - 80)),
                              (rivet_x - 1, rivet_y - 1), max(1, int(scale)))
        
        # 中心宝石
        gem_pulse = 0.6 + 0.4 * math.sin(t * 5 + angle)
        gem_alpha = max(0, min(255, int(255 * gem_pulse)))
        gem_x = corner_x + int(direction * corner_size * 0.45)
        
        pygame.draw.circle(surface, (*theme["rune_primary"], gem_alpha),
                          (gem_x, corner_y), max(3, int(4 * scale)))
        pygame.draw.circle(surface, (255, 255, 255, max(0, gem_alpha - 60)),
                          (gem_x - 1, corner_y - 1), max(1, int(2 * scale)))
    
    # ============================================================
    #   第五层：附属浮游魔法书 - 环绕主体的小型魔典（外围）
    # ============================================================
    mini_book_count = 4  # 减少数量
    for book_idx in range(mini_book_count):
        # 轨道参数 - 移到更外围
        orbit_angle = t * 0.8 + book_idx * (6.28 / mini_book_count)
        orbit_radius = 70 * scale  # 更大轨道
        
        mb_x = cx + int(math.cos(orbit_angle) * orbit_radius)
        mb_y = cy + int(math.sin(orbit_angle) * orbit_radius * 0.4)
        mb_hover = int(math.sin(t * 3 + book_idx * 1.5) * 3 * scale)
        mb_y += mb_hover
        
        # 小书尺寸
        mb_w = int(10 * scale)
        mb_h = int(7 * scale)
        mb_d = int(2 * scale)
        
        # 脉动
        mb_pulse = 0.7 + 0.3 * math.sin(t * 4 + book_idx)
        mb_alpha = max(0, min(255, int(180 * mb_pulse)))
        
        # 小书封面
        mb_cover = [
            (mb_x - mb_w // 2, mb_y - mb_h // 2),
            (mb_x + mb_w // 2, mb_y - mb_h // 2 + 2),
            (mb_x + mb_w // 2, mb_y + mb_h // 2),
            (mb_x - mb_w // 2, mb_y + mb_h // 2 - 2),
        ]
        pygame.draw.polygon(surface, (*theme["book_cover"], mb_alpha), mb_cover)
        pygame.draw.polygon(surface, (*theme["gold_trim"], max(0, mb_alpha - 40)), mb_cover, 1)
        
        # 小书书脊
        mb_spine_w = int(2 * scale)
        pygame.draw.line(surface, (*theme["book_spine"], mb_alpha),
                        (mb_x, mb_y - mb_h // 2), (mb_x, mb_y + mb_h // 2), mb_spine_w)
        
        # 小书中心符文
        rune_pulse = 0.5 + 0.5 * math.sin(t * 5 + book_idx * 2)
        rune_alpha = max(0, min(255, int(mb_alpha * rune_pulse)))
        pygame.draw.circle(surface, (*theme["rune_primary"], rune_alpha),
                          (mb_x, mb_y), max(2, int(2 * scale)))
    
    # ============================================================
    #   第六层：书页天使羽翼 - 根据涂装差异化渲染
    # ============================================================
    for wing_side in [-1, 1]:
        _draw_wing_variant(surface, cx, cy, wing_side, theme, t, scale, book_width)
    
    # ============================================================
    #   第七层：封印锁链系统 - 从书角延伸的诅咒锁链
    # ============================================================
    chain_anchors = [
        (cx - book_width // 2 - int(5 * scale), cy - book_height // 2 + 15, -2.5),
        (cx + book_width // 2 + int(5 * scale), cy - book_height // 2 + 15, -0.64),
        (cx - book_width // 2 - int(5 * scale), cy + book_height // 2, 2.5),
        (cx + book_width // 2 + int(5 * scale), cy + book_height // 2, 0.64),
    ]
    
    for anchor_idx, (anchor_x, anchor_y, anchor_angle) in enumerate(chain_anchors):
        chain_length = int(35 * scale)
        chain_segments = 10
        chain_wave = math.sin(t * 3 + anchor_idx * 1.2) * 5 * scale
        chain_pulse = 0.6 + 0.4 * math.sin(t * 2.5 + anchor_idx)
        chain_alpha = max(0, min(255, int(180 * chain_pulse)))
        
        # 锁链终点
        end_x = anchor_x + int(math.cos(anchor_angle) * chain_length)
        end_y = anchor_y + int(math.sin(anchor_angle) * chain_length * 0.5)
        
        prev_x, prev_y = anchor_x, anchor_y
        
        for seg in range(chain_segments):
            seg_t = (seg + 1) / chain_segments
            
            # 锁链位置（带波动）
            seg_x = int(anchor_x + (end_x - anchor_x) * seg_t)
            seg_y = int(anchor_y + (end_y - anchor_y) * seg_t + 
                       math.sin(seg_t * 3.14 + t * 4) * chain_wave * seg_t)
            
            seg_alpha = max(0, min(255, int(chain_alpha * (1 - seg_t * 0.3))))
            
            # 锁链环节
            pygame.draw.line(surface, (*theme["gold_trim"], seg_alpha),
                            (prev_x, prev_y), (seg_x, seg_y), max(2, int(2.5 * scale)))
            
            # 锁链节点
            if seg % 2 == 0:
                node_pulse = 0.7 + 0.3 * math.sin(t * 5 + seg)
                node_alpha = max(0, min(255, int(seg_alpha * node_pulse)))
                pygame.draw.circle(surface, (*theme["gold_trim"], node_alpha),
                                  (seg_x, seg_y), max(2, int(2.5 * scale)))
                # 节点高光
                pygame.draw.circle(surface, (255, 255, 255, max(0, node_alpha - 80)),
                                  (seg_x - 1, seg_y - 1), max(1, int(scale)))
            
            prev_x, prev_y = seg_x, seg_y
        
        # 锁链末端封印符
        seal_x = end_x
        seal_y = end_y
        seal_pulse = 0.5 + 0.5 * math.sin(t * 3 + anchor_idx * 2)
        seal_alpha = max(0, min(255, int(200 * seal_pulse)))
        seal_size = int(5 * scale)
        
        # 封印圆
        pygame.draw.circle(surface, (*theme["rune_primary"], seal_alpha),
                          (seal_x, seal_y), seal_size)
        pygame.draw.circle(surface, (*theme["gold_trim"], max(0, seal_alpha - 30)),
                          (seal_x, seal_y), seal_size, 1)
        
        # 封印符文
        draw_rune_symbol(surface, seal_x, seal_y, seal_size * 0.7, t + anchor_idx,
                        theme["rune_primary"], seal_alpha)
    
    # ============================================================
    #   第八层：全视之眼核心 - 根据涂装差异化渲染
    # ============================================================
    eye_y = cy - int(55 * scale)  # 眼睛位置上移，避免遮挡书籍
    eye_radius = int(12 * scale)  # 眼睛尺寸缩小
    eye_pulse = 0.85 + 0.15 * math.sin(t * 2.5)
    
    # 尝试使用差异化眼睛渲染
    used_variant = _draw_eye_variant(surface, cx, eye_y, theme, t, scale, eye_radius)
    
    if not used_variant:
        # ---------- 默认眼睛渲染（经典全视之眼） ----------
        # 8.1 眼睛周围暗黑涡流
        for vortex in range(6):  # 减少数量
            vortex_angle = t * 0.8 + vortex * 1.047
            vortex_dist = (16 + 5 * math.sin(t * 2.5 + vortex)) * scale  # 缩小范围
            vortex_x = cx + int(math.cos(vortex_angle) * vortex_dist)
            vortex_y = eye_y + int(math.sin(vortex_angle) * vortex_dist * 0.55)
            vortex_alpha = max(0, min(255, int(80 * (0.5 + 0.5 * math.sin(t * 3 + vortex)))))
            vortex_size = int((3 + math.sin(t * 4 + vortex) * 1.5) * scale)
            pygame.draw.circle(surface, (20, 0, 40, vortex_alpha), (vortex_x, vortex_y), vortex_size)
        
        # 8.2 外层威压光环（缩小范围）
        for halo in range(6):  # 减少层数
            halo_radius = eye_radius + int((6 - halo) * 2 * scale)  # 缩小范围
            halo_pulse = 0.4 + 0.6 * math.sin(t * 3 + halo * 0.35)
            halo_alpha = max(0, min(255, int((60 - halo * 8) * eye_pulse * halo_pulse)))
            pygame.draw.circle(surface, (50, 20, 80, halo_alpha), (cx, eye_y), halo_radius)
        
        # 8.3 威压光晕（缩小）
        for glow in range(4):  # 减少层数
            glow_radius = eye_radius + int(glow * 2.5 * scale)  # 缩小范围
            glow_alpha = max(0, min(255, int((100 - glow * 20) * eye_pulse)))
            pygame.draw.circle(surface, (*theme["crystal"], glow_alpha), (cx, eye_y), glow_radius)
        
        # 8.4 眼球主体
        pygame.draw.circle(surface, (248, 248, 252, 255), (cx, eye_y), eye_radius)
        pygame.draw.circle(surface, (180, 170, 200, 100), (cx, eye_y), eye_radius, max(3, int(3 * scale)))
        
        # 8.5 血丝纹理
        for vein in range(10):
            vein_angle = vein * 0.628 + math.sin(t * 2 + vein) * 0.1
            vein_length = eye_radius * 0.85
            vein_start_x = cx + int(math.cos(vein_angle) * eye_radius * 0.35)
            vein_start_y = eye_y + int(math.sin(vein_angle) * eye_radius * 0.35)
            vein_end_x = cx + int(math.cos(vein_angle) * vein_length)
            vein_end_y = eye_y + int(math.sin(vein_angle) * vein_length)
            vein_alpha = max(0, min(255, int(70 + 40 * math.sin(t * 4 + vein))))
            pygame.draw.line(surface, (180, 80, 80, vein_alpha),
                            (vein_start_x, vein_start_y), (vein_end_x, vein_end_y), 1)
        
        # 8.6 虹膜
        iris_radius = int(eye_radius * 0.58)
        pygame.draw.circle(surface, (*theme["book_spine"], 220), (cx, eye_y), iris_radius + max(2, int(2.5 * scale)))
        pygame.draw.circle(surface, (*theme["rune_primary"], 255), (cx, eye_y), iris_radius)
        
        # 虹膜纹理
        for iris_line in range(16):
            iris_angle = iris_line * 0.393 + t * 0.25
            iris_x1 = cx + int(math.cos(iris_angle) * iris_radius * 0.3)
            iris_y1 = eye_y + int(math.sin(iris_angle) * iris_radius * 0.3)
            iris_x2 = cx + int(math.cos(iris_angle) * iris_radius * 0.92)
            iris_y2 = eye_y + int(math.sin(iris_angle) * iris_radius * 0.92)
            iris_alpha = max(0, min(255, int(100 + 50 * math.sin(t * 3 + iris_line))))
            pygame.draw.line(surface, (*theme["book_spine"], iris_alpha), (iris_x1, iris_y1), (iris_x2, iris_y2), 1)
        
        # 8.7 瞳孔
        pupil_radius = int(iris_radius * 0.55)
        pupil_pulse = 0.7 + 0.3 * math.sin(t * 4)
        actual_pupil_r = int(pupil_radius * pupil_pulse)
        pygame.draw.circle(surface, (15, 5, 25, 255), (cx, eye_y), actual_pupil_r + 2)
        pygame.draw.circle(surface, (0, 0, 0, 255), (cx, eye_y), actual_pupil_r)
        
        # 瞳孔中心微光
        inner_glow_pulse = 0.5 + 0.5 * math.sin(t * 5)
        inner_glow_alpha = max(0, min(255, int(120 * inner_glow_pulse)))
        pygame.draw.circle(surface, (*theme["rune_primary"], inner_glow_alpha),
                          (cx, eye_y), max(2, int(pupil_radius * 0.25)))
        
        # 8.8 眼球高光
        pygame.draw.circle(surface, (255, 255, 255, 245),
                          (cx - int(5 * scale), eye_y - int(5 * scale)), max(3, int(4 * scale)))
        pygame.draw.circle(surface, (255, 255, 255, 180),
                          (cx + int(3 * scale), eye_y - int(3 * scale)), max(2, int(2.5 * scale)))
    
    # ---------- 8.9 眼睛符文环（远离书籍） ----------
    rune_ring_radius = eye_radius + int(12 * scale)  # 紧凑符文环
    for rune_idx in range(6):  # 减少符文数量
        rune_angle = t * 0.35 + rune_idx * 1.047
        rune_x = cx + int(math.cos(rune_angle) * rune_ring_radius)
        rune_y = eye_y + int(math.sin(rune_angle) * rune_ring_radius * 0.5)
        rune_pulse = 0.5 + 0.5 * math.sin(t * 3 + rune_idx * 1.2)
        rune_alpha = max(0, min(255, int(150 * rune_pulse)))
        rune_size = 3 * scale  # 缩小符文
        draw_rune_symbol(surface, rune_x, rune_y, rune_size, rune_angle + t,
                        theme["rune_secondary"], rune_alpha)
    
    # ============================================================
    #   第九层：希腊字母拖尾 - 简化版（仅在外围）
    # ============================================================
    # 左右两侧字母流（从外围开始）
    for side in [-1, 1]:
        for trail_idx in range(8):  # 减少数量
            trail_life = ((t * 20 + trail_idx * 10) % 100) / 100
            
            seed = random.Random(trail_idx * 17 + (500 if side > 0 else 0))
            start_x = cx + side * (book_width // 2 + 10)  # 从书外开始
            start_y = cy + book_height // 4
            
            drift_x = side * int(trail_life * 40 * scale + seed.random() * 15 * scale)
            drift_y = int(trail_life * 30 * scale)
            
            trail_x = start_x + drift_x
            trail_y = start_y + drift_y
            
            trail_alpha = max(0, min(255, int(120 * math.sin(trail_life * math.pi))))
            
            if trail_alpha > 20:
                pygame.draw.circle(surface, (*theme["rune_primary"], trail_alpha // 3),
                                  (trail_x, trail_y), max(2, int(4 * scale)))
    
    # ============================================================
    #   第十层：涂装专属特效（12种超精细差异化效果）
    #   注意：这些特效应该作为背景层，不遮挡书籍主体
    #   通过降低alpha值和调整绘制半径实现
    # ============================================================
    # 涂装专属特效已移至第三层和第四层之间，见 _render_magnus_theme_effects 函数调用
    # 此处保留标记，实际特效渲染在书籍主体之前完成
    pass  # 特效已移至正确层级
    
    # ============================================================
    #   原第十层代码 - 涂装特效在书籍外围环绕
    # ============================================================
    # 书籍半宽约42*scale，特效半径需要55+才不会遮挡
    
    if theme_name == "default":
        # ============================================================
        #   真理之书 - 洋红智慧光辉
        # ============================================================
        # 10.1 多层魔力粒子环绕（三轨道）- 在书外围
        for orbit in range(3):
            orbit_radius = (55 + orbit * 12) * scale
            particle_count = 12 - orbit * 2
            orbit_speed = 1.5 - orbit * 0.3
            
            for p in range(particle_count):
                p_angle = t * orbit_speed + p * (6.28 / particle_count) + orbit * 1.047
                p_wobble = math.sin(t * 4 + p + orbit * 2) * 0.15
                px = cx + int(math.cos(p_angle + p_wobble) * orbit_radius)
                py = cy + int(math.sin(p_angle + p_wobble) * orbit_radius * 0.4)
                p_pulse = 0.5 + 0.5 * math.sin(t * 5 + p + orbit)
                p_alpha = max(0, min(255, int((200 - orbit * 40) * p_pulse)))
                p_size = max(2, int((4 - orbit * 0.5) * scale))
                
                # 粒子光晕
                pygame.draw.circle(surface, (*theme["rune_primary"], p_alpha // 3),
                                  (px, py), p_size + int(3 * scale))
                pygame.draw.circle(surface, (*theme["rune_primary"], p_alpha),
                                  (px, py), p_size)
                # 粒子核心高光
                pygame.draw.circle(surface, (255, 200, 255, max(0, p_alpha - 60)),
                                  (px - 1, py - 1), max(1, p_size // 2))
        
        # 10.2 真理光芒（从眼睛发出的智慧射线）- 从外围发出
        for ray in range(8):
            ray_angle = t * 0.5 + ray * 0.785
            ray_length = (70 + math.sin(t * 3 + ray) * 15) * scale
            ray_alpha = max(0, min(255, int(100 * (0.4 + 0.6 * math.sin(t * 2 + ray)))))
            
            ray_start_x = cx + int(math.cos(ray_angle) * 50 * scale)
            ray_start_y = eye_y + int(math.sin(ray_angle) * 10 * scale)
            ray_end_x = cx + int(math.cos(ray_angle) * ray_length)
            ray_end_y = eye_y + int(math.sin(ray_angle) * ray_length * 0.5)
            
            # 渐变光线（多段）
            for seg in range(10):
                seg_t = seg / 9
                next_t = (seg + 1) / 9
                sx = int(ray_start_x + (ray_end_x - ray_start_x) * seg_t)
                sy = int(ray_start_y + (ray_end_y - ray_start_y) * seg_t)
                ex = int(ray_start_x + (ray_end_x - ray_start_x) * next_t)
                ey = int(ray_start_y + (ray_end_y - ray_start_y) * next_t)
                seg_alpha = max(0, int(ray_alpha * (1 - seg_t * 0.8)))
                if seg_alpha > 5:
                    pygame.draw.line(surface, (*theme["rune_secondary"], seg_alpha),
                                    (sx, sy), (ex, ey), max(1, int((3 - seg_t * 2) * scale)))
        
        # 10.3 悬浮符文阵列 - 在书下方外围
        for rune_row in range(2):
            for rune_col in range(5):
                rune_x = cx + int((rune_col - 2) * 18 * scale)
                rune_y = cy + int((55 + rune_row * 15) * scale)
                rune_phase = math.sin(t * 3 + rune_row * 2 + rune_col) * 0.5 + 0.5
                rune_alpha = max(0, min(255, int(160 * rune_phase)))
                rune_size = int(5 * scale)
                
                if rune_alpha > 20:
                    draw_rune_symbol(surface, rune_x, rune_y, rune_size, 
                                    t + rune_row + rune_col, theme["rune_primary"], rune_alpha)
    
    elif theme_name == "arcane":
        # ============================================================
        #   奥术典籍 - 蓝色魔力漩涡与悬浮符文
        # ============================================================
        # 10.1 双层魔力漩涡（逆向旋转）
        for swirl_layer in range(2):
            swirl_dir = 1 if swirl_layer == 0 else -1
            particle_count = 30 - swirl_layer * 5
            max_radius = (70 - swirl_layer * 10) * scale  # 外围环绕
            
            for p in range(particle_count):
                p_t = p / particle_count
                p_angle = t * 2 * swirl_dir + p_t * 12.56
                p_radius = max_radius * p_t
                p_wobble = math.sin(t * 3 + p) * 3 * scale
                
                px = cx + int(math.cos(p_angle) * (p_radius + p_wobble))
                py = cy + int(math.sin(p_angle) * (p_radius + p_wobble) * 0.4)
                p_alpha = max(0, min(255, int(220 * (1 - p_t * 0.6))))
                p_size = max(1, int((4 - p_t * 2) * scale))
                
                pygame.draw.circle(surface, (*theme["rune_primary"], p_alpha // 3),
                                  (px, py), p_size + 2)
                pygame.draw.circle(surface, (*theme["rune_primary"], p_alpha),
                                  (px, py), p_size)
        
        # 10.2 悬浮奥术符文环 - 外围
        for rune_ring in range(2):
            ring_radius = (55 + rune_ring * 15) * scale
            rune_count = 8 - rune_ring * 2
            ring_rotation = t * (0.6 - rune_ring * 0.2) * (1 if rune_ring == 0 else -1)
            
            for r in range(rune_count):
                r_angle = ring_rotation + r * (6.28 / rune_count)
                rx = cx + int(math.cos(r_angle) * ring_radius)
                ry = cy + int(math.sin(r_angle) * ring_radius * 0.4)
                r_pulse = 0.5 + 0.5 * math.sin(t * 4 + r + rune_ring * 3)
                r_alpha = max(0, min(255, int((200 - rune_ring * 40) * r_pulse)))
                r_size = (8 - rune_ring * 2) * scale
                
                # 符文背景光
                pygame.draw.circle(surface, (*theme["rune_primary"], r_alpha // 4),
                                  (rx, ry), int(r_size * 1.5))
                draw_rune_symbol(surface, rx, ry, r_size, t * 2 + r, theme["rune_primary"], r_alpha)
        
        # 10.3 蓝色能量脉冲波
        pulse_count = 3
        for pulse in range(pulse_count):
            pulse_life = ((t * 40 + pulse * 33) % 100) / 100
            pulse_radius = int(pulse_life * 70 * scale)
            pulse_alpha = max(0, min(255, int(150 * (1 - pulse_life))))
            pulse_width = max(1, int((4 - pulse_life * 3) * scale))
            
            if pulse_alpha > 10:
                pygame.draw.circle(surface, (*theme["rune_primary"], pulse_alpha),
                                  (cx, cy), pulse_radius, pulse_width)
        
        # 10.4 奥术连接线网 - 外围
        connect_points = []
        for cp in range(6):
            cp_angle = t * 0.4 + cp * 1.047
            cp_x = cx + int(math.cos(cp_angle) * 60 * scale)
            cp_y = cy + int(math.sin(cp_angle) * 60 * scale * 0.4)
            connect_points.append((cp_x, cp_y))
        
        for i in range(len(connect_points)):
            for j in range(i + 1, len(connect_points)):
                dist = math.sqrt((connect_points[i][0] - connect_points[j][0]) ** 2 + 
                               (connect_points[i][1] - connect_points[j][1]) ** 2)
                if dist < 60 * scale:
                    line_alpha = max(0, min(255, int(80 * (1 - dist / (60 * scale)))))
                    pulse_alpha = int(line_alpha * (0.5 + 0.5 * math.sin(t * 5 + i + j)))
                    pygame.draw.line(surface, (*theme["rune_secondary"], pulse_alpha),
                                    connect_points[i], connect_points[j], 1)
    
    elif theme_name == "necro":
        # ============================================================
        #   死灵禁书 - 幽魂群舞与骷髅符阵
        # ============================================================
        # 10.1 幽魂环绕（详细的魂魄形态）
        ghost_count = 10
        for g in range(ghost_count):
            g_angle = t * 1.2 + g * (6.28 / ghost_count)
            g_dist = (60 + math.sin(t * 2 + g * 1.5) * 10) * scale  # 外围
            gx = cx + int(math.cos(g_angle) * g_dist)
            gy = cy + int(math.sin(g_angle) * g_dist * 0.4) + int(math.sin(t * 4 + g * 2) * 5 * scale)
            g_pulse = 0.4 + 0.6 * math.sin(t * 3 + g)
            g_alpha = max(0, min(255, int(180 * g_pulse)))
            
            # 幽魂主体（椭圆头部）
            ghost_head_w = int(6 * scale)
            ghost_head_h = int(5 * scale)
            pygame.draw.ellipse(surface, (*theme["page_glow"], g_alpha),
                               (gx - ghost_head_w, gy - ghost_head_h, ghost_head_w * 2, ghost_head_h * 2))
            
            # 幽魂拖尾（飘逸的尾巴）
            for tail in range(6):
                tail_offset = tail * 3 * scale
                tail_x = gx - int(tail_offset * math.cos(g_angle))
                tail_y = gy + int(tail * 2 * scale) + int(math.sin(t * 5 + tail + g) * 2 * scale)
                tail_alpha = max(0, int(g_alpha * (1 - tail / 7)))
                tail_size = max(2, int((5 - tail * 0.7) * scale))
                pygame.draw.circle(surface, (*theme["page_glow"], tail_alpha), (int(tail_x), int(tail_y)), tail_size)
            
            # 幽魂眼睛（发红光）
            pygame.draw.circle(surface, (255, 80, 80, g_alpha), (gx - int(2 * scale), gy - int(scale)), max(1, int(1.5 * scale)))
            pygame.draw.circle(surface, (255, 80, 80, g_alpha), (gx + int(2 * scale), gy - int(scale)), max(1, int(1.5 * scale)))
        
        # 10.2 骷髅魔法阵（地面）
        skull_ring_radius = 55 * scale
        skull_pulse = 0.6 + 0.4 * math.sin(t * 2)
        skull_alpha = max(0, min(255, int(120 * skull_pulse)))
        
        # 六芒星底阵
        for star_pt in range(6):
            pt_angle = t * 0.3 + star_pt * 1.047
            next_pt = (star_pt + 2) % 6
            next_angle = t * 0.3 + next_pt * 1.047
            x1 = cx + int(math.cos(pt_angle) * skull_ring_radius)
            y1 = cy + int(35 * scale) + int(math.sin(pt_angle) * skull_ring_radius * 0.25)
            x2 = cx + int(math.cos(next_angle) * skull_ring_radius)
            y2 = cy + int(35 * scale) + int(math.sin(next_angle) * skull_ring_radius * 0.25)
            pygame.draw.line(surface, (*theme["rune_primary"], skull_alpha), (x1, y1), (x2, y2), max(1, int(2 * scale)))
        
        # 骷髅符文点
        for skull_rune in range(6):
            sr_angle = t * 0.3 + skull_rune * 1.047
            sr_x = cx + int(math.cos(sr_angle) * skull_ring_radius)
            sr_y = cy + int(35 * scale) + int(math.sin(sr_angle) * skull_ring_radius * 0.25)
            sr_pulse = 0.5 + 0.5 * math.sin(t * 4 + skull_rune)
            sr_alpha = max(0, min(255, int(skull_alpha * sr_pulse)))
            pygame.draw.circle(surface, (*theme["rune_primary"], sr_alpha), (sr_x, sr_y), max(3, int(5 * scale)))
        
        # 10.3 腐烂绿光粒子上升
        for decay in range(15):
            decay_life = ((t * 15 + decay * 7) % 80) / 80
            seed = random.Random(decay * 13)
            dx = cx + int((seed.random() - 0.5) * 60 * scale)
            dy = cy + int(40 * scale - decay_life * 90 * scale)
            d_alpha = max(0, min(255, int(150 * math.sin(decay_life * math.pi))))
            d_size = max(2, int((4 - decay_life * 2) * scale))
            
            pygame.draw.circle(surface, (*theme["rune_primary"], d_alpha), (dx, dy), d_size)
        
        # 10.4 死亡光环
        death_ring_count = 3
        for ring in range(death_ring_count):
            ring_life = ((t * 25 + ring * 33) % 100) / 100
            ring_radius = int(ring_life * 50 * scale)
            ring_alpha = max(0, min(255, int(100 * (1 - ring_life))))
            if ring_alpha > 10:
                pygame.draw.circle(surface, (*theme["page_glow"], ring_alpha),
                                  (cx, cy), ring_radius, max(1, int(2 * scale)))
    
    elif theme_name == "holy":
        # ============================================================
        #   圣典 - 神圣光柱与天使光环
        # ============================================================
        # 10.1 中央神圣光柱（多层渐变）
        pillar_phase = (t * 1.2) % 1.0
        pillar_intensity = math.sin(pillar_phase * math.pi)
        pillar_base_alpha = max(0, min(255, int(180 * pillar_intensity)))
        
        if pillar_base_alpha > 15:
            for layer in range(8):
                layer_alpha = max(0, int(pillar_base_alpha * (1 - layer / 10)))
                layer_width = int((28 - layer * 3) * scale)
                layer_height = int(150 * scale)
                if layer_width > 0 and layer_alpha > 5:
                    pygame.draw.rect(surface, (*theme["rune_primary"], layer_alpha),
                                    (cx - layer_width // 2, cy - int(70 * scale), layer_width, layer_height))
        
        # 10.2 光柱内上升光点
        for light in range(20):
            light_life = ((t * 40 + light * 5) % 100) / 100
            lx = cx + int((random.Random(light).random() - 0.5) * 20 * scale)
            ly = cy + int(60 * scale - light_life * 140 * scale)
            l_alpha = max(0, min(255, int(200 * math.sin(light_life * math.pi) * pillar_intensity)))
            l_size = max(1, int(3 * scale * (1 - light_life * 0.5)))
            
            if l_alpha > 10:
                pygame.draw.circle(surface, (255, 255, 200, l_alpha), (lx, ly), l_size)
        
        # 10.3 头顶三层天使光环
        for halo_layer in range(3):
            halo_y = eye_y - int((20 + halo_layer * 8) * scale)
            halo_w = int((32 - halo_layer * 5) * scale)
            halo_h = int((7 - halo_layer) * scale)
            halo_pulse = 0.7 + 0.3 * math.sin(t * 3 + halo_layer)
            halo_alpha = max(0, min(255, int((230 - halo_layer * 50) * halo_pulse)))
            halo_thickness = max(2, int((3 - halo_layer * 0.5) * scale))
            
            pygame.draw.ellipse(surface, (*theme["gold_trim"], halo_alpha),
                               (cx - halo_w // 2, halo_y - halo_h // 2, halo_w, halo_h), halo_thickness)
        
        # 10.4 光环发光粒子
        for hp in range(12):
            hp_angle = t * 1.5 + hp * 0.524
            hp_radius = 28 * scale
            hp_x = cx + int(math.cos(hp_angle) * hp_radius)
            hp_y = eye_y - int(20 * scale) + int(math.sin(hp_angle) * 5 * scale)
            hp_pulse = 0.5 + 0.5 * math.sin(t * 5 + hp)
            hp_alpha = max(0, min(255, int(200 * hp_pulse)))
            
            pygame.draw.circle(surface, (*theme["rune_primary"], hp_alpha // 2), (hp_x, hp_y), max(3, int(4 * scale)))
            pygame.draw.circle(surface, (255, 255, 200, hp_alpha), (hp_x, hp_y), max(2, int(2.5 * scale)))
        
        # 10.5 祝福符文环绕
        bless_count = 6
        for bless in range(bless_count):
            b_angle = t * 0.4 + bless * (6.28 / bless_count)
            b_dist = 50 * scale
            bx = cx + int(math.cos(b_angle) * b_dist)
            by = cy + int(math.sin(b_angle) * b_dist * 0.35)
            b_pulse = 0.5 + 0.5 * math.sin(t * 3 + bless * 2)
            b_alpha = max(0, min(255, int(160 * b_pulse)))
            
            # 祝福符文光晕
            pygame.draw.circle(surface, (*theme["rune_primary"], b_alpha // 4), (bx, by), int(8 * scale))
            draw_rune_symbol(surface, bx, by, 6 * scale, t + bless, theme["gold_trim"], b_alpha)
        
        # 10.6 羽毛飘落
        for feather in range(8):
            f_life = ((t * 12 + feather * 12) % 100) / 100
            seed = random.Random(feather * 17)
            fx = cx + int((seed.random() - 0.5) * 80 * scale + math.sin(t * 2 + feather) * 10 * scale)
            fy = cy - int(50 * scale) + int(f_life * 120 * scale)
            f_rot = t * 2 + feather
            f_alpha = max(0, min(255, int(180 * math.sin(f_life * math.pi))))
            f_length = int(6 * scale)
            
            if f_alpha > 20:
                # 羽毛形状
                fx1 = fx + int(math.cos(f_rot) * f_length)
                fy1 = fy + int(math.sin(f_rot) * f_length * 0.3)
                fx2 = fx - int(math.cos(f_rot) * f_length)
                fy2 = fy - int(math.sin(f_rot) * f_length * 0.3)
                pygame.draw.line(surface, (255, 255, 200, f_alpha), (fx1, fy1), (fx2, fy2), max(1, int(2 * scale)))
    
    elif theme_name == "infernal":
        # ============================================================
        #   地狱魔典 - 烈焰喷涌与熔岩裂隙
        # ============================================================
        # 10.1 火焰粒子系统（多层火焰）
        for flame_layer in range(3):
            flame_count = 20 - flame_layer * 4
            for f in range(flame_count):
                f_life = ((t * (35 - flame_layer * 5) + f * 4) % 60) / 60
                f_angle = f * (0.4 - flame_layer * 0.05) + t * 2 + math.sin(t * 4 + f) * 0.3
                f_spread = (25 - flame_layer * 5) * scale
                fx = cx + int(math.sin(f_angle) * f_spread * (1 - f_life * 0.4))
                fy = cy + int(10 * scale - f_life * (60 - flame_layer * 10) * scale)
                f_alpha = max(0, min(255, int((255 - flame_layer * 50) * (1 - f_life) ** 1.2)))
                f_size = max(1, int((8 - flame_layer * 2 - f_life * 5) * scale))
                
                # 火焰核心（黄色）
                pygame.draw.circle(surface, (255, 220, 80, f_alpha), (fx, fy), f_size)
                # 火焰边缘（橙红色）
                pygame.draw.circle(surface, (*theme["rune_primary"], max(0, f_alpha - 40)), (fx, fy), int(f_size * 1.3))
                # 火焰外圈（暗红）
                pygame.draw.circle(surface, (150, 50, 20, max(0, f_alpha - 100)), (fx, fy), int(f_size * 1.6))
        
        # 10.2 熔岩裂隙系统
        for crack in range(8):
            seed = random.Random(crack * 7)
            crack_x = cx + int((seed.random() - 0.5) * 70 * scale)
            crack_y = cy + int(20 * scale + seed.random() * 30 * scale)
            crack_pulse = 0.4 + 0.6 * math.sin(t * 5 + crack)
            crack_alpha = max(0, min(255, int(220 * crack_pulse)))
            crack_length = int((15 + seed.random() * 10) * scale * crack_pulse)
            crack_angle = seed.random() * 0.5 + 0.5
            
            # 裂隙主体
            cx1 = crack_x
            cy1 = crack_y
            cx2 = crack_x + int(crack_length * 0.3 * math.cos(crack_angle))
            cy2 = crack_y + int(crack_length * math.sin(crack_angle))
            
            # 裂隙光晕
            pygame.draw.line(surface, (*theme["rune_primary"], crack_alpha // 3),
                            (cx1, cy1), (cx2, cy2), max(4, int(5 * scale)))
            pygame.draw.line(surface, (255, 200, 100, crack_alpha),
                            (cx1, cy1), (cx2, cy2), max(2, int(3 * scale)))
            pygame.draw.line(surface, (255, 255, 200, max(0, crack_alpha - 50)),
                            (cx1, cy1), (cx2, cy2), max(1, int(1.5 * scale)))
            
            # 裂隙分叉
            if seed.random() > 0.4:
                branch_angle = crack_angle + (0.5 if seed.random() > 0.5 else -0.5)
                branch_len = crack_length * 0.5
                bx2 = cx2 + int(branch_len * 0.3 * math.cos(branch_angle))
                by2 = cy2 + int(branch_len * math.sin(branch_angle))
                pygame.draw.line(surface, (*theme["rune_primary"], max(0, crack_alpha - 30)),
                                (cx2, cy2), (bx2, by2), max(1, int(2 * scale)))
        
        # 10.3 地狱火焰光环
        for hell_ring in range(4):
            ring_radius = (58 + hell_ring * 10) * scale  # 外围
            ring_alpha = max(0, min(255, int((100 - hell_ring * 20) * (0.5 + 0.5 * math.sin(t * 3 + hell_ring)))))
            
            # 断裂的火焰环
            for arc in range(8):
                arc_start = t * 0.5 + arc * 0.785 + hell_ring * 0.2
                arc_length = 0.4 + math.sin(t * 4 + arc + hell_ring) * 0.2
                
                for seg in range(6):
                    seg_angle = arc_start + seg * (arc_length / 6)
                    seg_x = cx + int(math.cos(seg_angle) * ring_radius)
                    seg_y = cy + int(math.sin(seg_angle) * ring_radius * 0.4)
                    seg_alpha = max(0, int(ring_alpha * (0.5 + 0.5 * math.sin(t * 6 + seg))))
                    pygame.draw.circle(surface, (*theme["rune_primary"], seg_alpha),
                                      (seg_x, seg_y), max(2, int((3 - hell_ring * 0.5) * scale)))
        
        # 10.4 灼热余烬飘落
        for ember in range(12):
            e_life = ((t * 20 + ember * 8) % 80) / 80
            seed = random.Random(ember * 23)
            ex = cx + int((seed.random() - 0.5) * 60 * scale + math.sin(t * 3 + ember) * 5 * scale)
            ey = cy - int(30 * scale) + int(e_life * 80 * scale)
            e_alpha = max(0, min(255, int(200 * math.sin(e_life * math.pi))))
            e_size = max(1, int(3 * scale * (1 - e_life * 0.5)))
            
            pygame.draw.circle(surface, (255, 150, 50, e_alpha), (ex, ey), e_size)
            pygame.draw.circle(surface, (255, 255, 150, max(0, e_alpha - 80)), (ex, ey), max(1, e_size - 1))
    
    elif theme_name == "void":
        # ============================================================
        #   虚空典籍 - 维度裂隙与窥视之眼
        # ============================================================
        # 10.1 维度裂隙（深邃的空间撕裂）
        for rift in range(7):
            r_angle = t * 0.8 + rift * 0.898
            r_base_len = (25 + math.sin(t * 2 + rift * 2) * 8) * scale
            rx1 = cx + int(math.cos(r_angle) * 22 * scale)
            ry1 = cy + int(math.sin(r_angle) * 22 * scale * 0.4)
            rx2 = rx1 + int(math.cos(r_angle + 0.35) * r_base_len)
            ry2 = ry1 + int(math.sin(r_angle + 0.35) * r_base_len * 0.5)
            r_pulse = 0.4 + 0.6 * math.sin(t * 4 + rift)
            r_alpha = max(0, min(255, int(200 * r_pulse)))
            
            # 裂隙外层光晕（紫色）
            pygame.draw.line(surface, (*theme["trail"], r_alpha // 4), (rx1, ry1), (rx2, ry2), max(6, int(8 * scale)))
            # 裂隙中层
            pygame.draw.line(surface, (*theme["rune_secondary"], r_alpha // 2), (rx1, ry1), (rx2, ry2), max(4, int(5 * scale)))
            # 裂隙核心
            pygame.draw.line(surface, (*theme["rune_primary"], r_alpha), (rx1, ry1), (rx2, ry2), max(2, int(3 * scale)))
            # 裂隙中心（白色高亮）
            pygame.draw.line(surface, (200, 180, 255, max(0, r_alpha - 50)), (rx1, ry1), (rx2, ry2), max(1, int(scale)))
            
            # 裂隙端点粒子逸散
            for particle in range(4):
                p_offset = (particle + 1) * 5 * scale
                p_angle_offset = (random.Random(rift * 10 + particle).random() - 0.5) * 0.5
                px = rx2 + int(math.cos(r_angle + 0.35 + p_angle_offset) * p_offset)
                py = ry2 + int(math.sin(r_angle + 0.35 + p_angle_offset) * p_offset * 0.5)
                p_alpha = max(0, int(r_alpha * (1 - particle / 5)))
                pygame.draw.circle(surface, (*theme["rune_primary"], p_alpha), (px, py), max(1, int(2 * scale)))
        
        # 10.2 虚空之眼（窥视的异界存在）
        void_eye_count = 4
        for ve in range(void_eye_count):
            ve_angle = t * 0.6 + ve * (6.28 / void_eye_count)
            ve_dist = (38 + math.sin(t * 3 + ve * 2) * 8) * scale
            vex = cx + int(math.cos(ve_angle) * ve_dist)
            vey = cy + int(math.sin(ve_angle) * ve_dist * 0.4)
            ve_pulse = 0.5 + 0.5 * math.sin(t * 4 + ve * 1.5)
            ve_alpha = max(0, min(255, int(200 * ve_pulse)))
            
            # 眼眶光晕
            pygame.draw.circle(surface, (*theme["rune_secondary"], ve_alpha // 3), (vex, vey), int(8 * scale))
            # 眼白
            pygame.draw.circle(surface, (*theme["rune_primary"], ve_alpha), (vex, vey), int(5 * scale))
            # 瞳孔（深邃黑暗）
            pygame.draw.circle(surface, (15, 5, 30, min(255, int(ve_alpha * 1.3))), (vex, vey), int(3 * scale))
            # 瞳孔核心
            pygame.draw.circle(surface, (0, 0, 0, 255), (vex, vey), int(1.5 * scale))
            # 高光
            pygame.draw.circle(surface, (200, 180, 255, max(0, ve_alpha - 40)),
                              (vex - int(scale), vey - int(scale)), max(1, int(1.5 * scale)))
        
        # 10.3 虚空能量涡旋
        for vortex in range(3):
            vortex_particles = 15
            vortex_radius = (20 + vortex * 15) * scale
            vortex_speed = 2 - vortex * 0.4
            vortex_dir = 1 if vortex % 2 == 0 else -1
            
            for vp in range(vortex_particles):
                vp_t = vp / vortex_particles
                vp_angle = t * vortex_speed * vortex_dir + vp_t * 6.28
                vp_r = vortex_radius * (0.3 + vp_t * 0.7)
                vpx = cx + int(math.cos(vp_angle) * vp_r)
                vpy = cy + int(math.sin(vp_angle) * vp_r * 0.4)
                vp_alpha = max(0, min(255, int((150 - vortex * 30) * (0.5 + 0.5 * vp_t))))
                vp_size = max(1, int((3 - vortex * 0.5) * scale * vp_t))
                
                pygame.draw.circle(surface, (*theme["rune_primary"], vp_alpha), (vpx, vpy), vp_size)
        
        # 10.4 空间扭曲波纹
        for wave in range(4):
            wave_life = ((t * 30 + wave * 25) % 100) / 100
            wave_radius = int(wave_life * 60 * scale)
            wave_alpha = max(0, min(255, int(120 * (1 - wave_life) * math.sin(wave_life * math.pi * 2))))
            wave_width = max(1, int((3 - wave_life * 2) * scale))
            
            if abs(wave_alpha) > 10:
                pygame.draw.circle(surface, (*theme["trail"], abs(wave_alpha)),
                                  (cx, cy), wave_radius, wave_width)
    
    elif theme_name == "celestial":
        # ============================================================
        #   星辰宝典 - 星座连线与闪烁星光
        # ============================================================
        # 10.1 星空背景星点（多层深度）
        star_positions = []
        for depth in range(3):
            star_count = 25 - depth * 5
            for s in range(star_count):
                seed = random.Random(s * 13 + depth * 1000)
                sx = cx + int((seed.random() - 0.5) * (100 - depth * 15) * scale)
                sy = cy + int((seed.random() - 0.5) * (80 - depth * 12) * scale)
                
                # 星星闪烁
                twinkle_speed = 5 + depth
                twinkle = 0.2 + 0.8 * abs(math.sin(t * twinkle_speed + s * 0.9 + depth))
                s_alpha = max(0, min(255, int((240 - depth * 40) * twinkle)))
                s_size = max(1, int((4 - depth) * scale * twinkle))
                
                pygame.draw.circle(surface, (*theme["rune_primary"], s_alpha), (sx, sy), s_size)
                
                # 大星星有光芒
                if s_size >= 3 and twinkle > 0.6:
                    for ray in range(4):
                        r_angle = ray * 0.785 + t * 0.3
                        r_len = s_size * 2.5
                        rx = sx + int(math.cos(r_angle) * r_len)
                        ry = sy + int(math.sin(r_angle) * r_len)
                        pygame.draw.line(surface, (*theme["trail"], max(0, s_alpha - 80)),
                                        (sx, sy), (rx, ry), 1)
                
                if depth == 0:
                    star_positions.append((sx, sy, s_alpha))
        
        # 10.2 星座连线（动态连接）
        if len(star_positions) >= 2:
            for i in range(min(len(star_positions) - 1, 15)):
                # 动态连接判定
                connect_phase = (t * 2 + i) % 8
                if connect_phase < 4:
                    j = (i + 1 + int(math.sin(t + i) * 2)) % len(star_positions)
                    if i != j:
                        dist = math.sqrt((star_positions[i][0] - star_positions[j][0]) ** 2 +
                                        (star_positions[i][1] - star_positions[j][1]) ** 2)
                        if dist < 50 * scale:
                            line_alpha = max(0, min(255, int(80 * (1 - dist / (50 * scale)) * 
                                            (0.5 + 0.5 * math.sin(t * 3 + i)))))
                            pygame.draw.line(surface, (*theme["gold_trim"], line_alpha),
                                            (star_positions[i][0], star_positions[i][1]),
                                            (star_positions[j][0], star_positions[j][1]), 1)
        
        # 10.3 流星划过
        for meteor in range(3):
            m_life = ((t * 60 + meteor * 100) % 300) / 300
            if m_life < 0.15:
                m_progress = m_life / 0.15
                seed = random.Random(meteor * 37 + int(t // 5))
                m_start_x = cx + int((seed.random() - 0.3) * 80 * scale)
                m_start_y = cy - int(50 * scale)
                m_end_x = m_start_x + int(60 * scale)
                m_end_y = m_start_y + int(40 * scale)
                
                mx = int(m_start_x + (m_end_x - m_start_x) * m_progress)
                my = int(m_start_y + (m_end_y - m_start_y) * m_progress)
                m_alpha = max(0, min(255, int(255 * math.sin(m_progress * math.pi))))
                
                # 流星头部
                pygame.draw.circle(surface, (255, 255, 220, m_alpha), (mx, my), max(2, int(3 * scale)))
                # 流星尾巴
                for tail in range(8):
                    tail_t = tail / 8
                    tx = int(mx - (m_end_x - m_start_x) * tail_t * 0.3)
                    ty = int(my - (m_end_y - m_start_y) * tail_t * 0.3)
                    t_alpha = max(0, int(m_alpha * (1 - tail_t)))
                    t_size = max(1, int((3 - tail_t * 2) * scale))
                    pygame.draw.circle(surface, (*theme["rune_primary"], t_alpha), (tx, ty), t_size)
        
        # 10.4 银河带
        galaxy_particles = 30
        for gp in range(galaxy_particles):
            seed = random.Random(gp * 19)
            gp_angle = gp * (6.28 / galaxy_particles) + t * 0.2
            gp_radius = (55 + seed.random() * 15) * scale  # 外围
            gp_wobble = math.sin(t * 2 + gp) * 5 * scale
            gpx = cx + int(math.cos(gp_angle) * gp_radius)
            gpy = cy + int(math.sin(gp_angle) * (gp_radius * 0.3 + gp_wobble))
            gp_alpha = max(0, min(255, int(120 * (0.4 + 0.6 * seed.random()))))
            gp_size = max(1, int(2 * scale * seed.random()))
            
            pygame.draw.circle(surface, (*theme["trail"], gp_alpha), (gpx, gpy), gp_size)
    
    elif theme_name == "blood":
        # ============================================================
        #   血之魔典 - 血液漩涡与血滴飞溅
        # ============================================================
        # 10.1 三层血液漩涡（螺旋状）
        for swirl in range(3):
            swirl_radius = (55 + swirl * 14) * scale  # 外围
            swirl_speed = 1.8 - swirl * 0.3
            swirl_particles = 20 - swirl * 3
            swirl_alpha_base = 160 - swirl * 35
            
            for pt in range(swirl_particles):
                pt_t = pt / swirl_particles
                pt_angle = t * swirl_speed + pt_t * 9.42
                pt_r = swirl_radius * (0.4 + pt_t * 0.6)
                px = cx + int(math.cos(pt_angle) * pt_r)
                py = cy + int(math.sin(pt_angle) * pt_r * 0.4)
                pt_alpha = max(0, min(255, int(swirl_alpha_base * (0.5 + 0.5 * pt_t))))
                pt_size = max(1, int((4 - swirl * 0.8 - pt_t * 1.5) * scale))
                
                # 血液粒子
                pygame.draw.circle(surface, (*theme["rune_primary"], pt_alpha), (px, py), pt_size)
                # 血液高光
                pygame.draw.circle(surface, (255, 150, 150, max(0, pt_alpha - 80)),
                                  (px - 1, py - 1), max(1, pt_size - 1))
        
        # 10.2 血滴飞溅（从书上滴落）
        for blood in range(15):
            b_life = ((t * 22 + blood * 7) % 70) / 70
            seed = random.Random(blood * 11)
            b_start_x = cx + int((seed.random() - 0.5) * 40 * scale)
            b_start_y = cy - int(15 * scale)
            
            # 抛物线轨迹
            bx = b_start_x + int(math.sin(seed.random() * 6.28) * b_life * 20 * scale)
            by = b_start_y + int(b_life * 70 * scale + b_life * b_life * 30 * scale)
            b_alpha = max(0, min(255, int(240 * (1 - b_life * 0.6))))
            b_size = max(2, int((6 - b_life * 3) * scale))
            
            # 血滴主体
            pygame.draw.circle(surface, (*theme["rune_primary"], b_alpha), (bx, by), b_size)
            # 血滴拖尾
            for tail in range(4):
                tail_offset = tail * 4 * scale * b_life
                tx = bx
                ty = int(by - tail_offset)
                t_alpha = max(0, int(b_alpha * (1 - tail / 5)))
                t_size = max(1, int(b_size * (1 - tail * 0.15)))
                pygame.draw.circle(surface, (*theme["rune_primary"], t_alpha), (tx, ty), t_size)
        
        # 10.3 血池涟漪（书下方）
        pool_y = cy + int(45 * scale)
        for ripple in range(4):
            ripple_life = ((t * 35 + ripple * 25) % 100) / 100
            ripple_radius = int(ripple_life * 35 * scale)
            ripple_alpha = max(0, min(255, int(100 * (1 - ripple_life))))
            ripple_width = max(1, int((3 - ripple_life * 2) * scale))
            
            if ripple_alpha > 10:
                pygame.draw.ellipse(surface, (*theme["rune_primary"], ripple_alpha),
                                   (cx - ripple_radius, pool_y - int(ripple_radius * 0.3),
                                    ripple_radius * 2, int(ripple_radius * 0.6)), ripple_width)
        
        # 10.4 血红符文脉动
        for br in range(6):
            br_angle = t * 0.4 + br * 1.047
            br_dist = 60 * scale  # 外围
            brx = cx + int(math.cos(br_angle) * br_dist)
            bry = cy + int(math.sin(br_angle) * br_dist * 0.35)
            br_pulse = 0.3 + 0.7 * math.sin(t * 4 + br * 1.5)
            br_alpha = max(0, min(255, int(180 * br_pulse)))
            
            # 符文光晕
            pygame.draw.circle(surface, (*theme["rune_primary"], br_alpha // 4), (brx, bry), int(8 * scale))
            draw_rune_symbol(surface, brx, bry, 6 * scale, t + br, theme["rune_primary"], br_alpha)
        
        # 10.5 心跳脉冲
        heartbeat_phase = (t * 80) % 100
        if heartbeat_phase < 15:
            beat_intensity = math.sin(heartbeat_phase / 15 * math.pi)
            beat_alpha = max(0, min(255, int(100 * beat_intensity)))
            beat_radius = int((55 + beat_intensity * 15) * scale)  # 外围
            pygame.draw.circle(surface, (*theme["rune_primary"], beat_alpha),
                              (cx, cy), beat_radius, max(2, int(3 * scale)))
    
    elif theme_name == "elder":
        # ============================================================
        #   远古遗典 - 褐金沙尘与古老符文
        # ============================================================
        # 10.1 沙尘粒子系统（多层上升）
        for dust_layer in range(3):
            dust_count = 30 - dust_layer * 8
            for dust in range(dust_count):
                d_life = ((t * (14 - dust_layer * 2) + dust * 4) % 90) / 90
                seed = random.Random(dust * 7 + dust_layer * 1000)
                
                # 沙尘起点和飘动
                dx = cx + int((seed.random() - 0.5) * (90 - dust_layer * 15) * scale)
                dx += int(math.sin(t * 2 + dust + dust_layer) * 8 * scale)
                dy = cy + int(40 * scale - d_life * (80 - dust_layer * 10) * scale)
                
                d_alpha = max(0, min(255, int((180 - dust_layer * 40) * math.sin(d_life * math.pi))))
                d_size = max(1, int((3 - dust_layer * 0.5) * scale))
                
                pygame.draw.circle(surface, (*theme["rune_primary"], d_alpha), (dx, dy), d_size)
        
        # 10.2 古老符文浮现（逐渐显现又消失）
        for rune in range(6):
            rune_phase = ((t * 0.8 + rune * 1.2) % 8) / 8
            r_angle = rune * 1.047 + 0.3
            r_dist = 60 * scale  # 外围
            rx = cx + int(math.cos(r_angle) * r_dist)
            ry = cy + int(math.sin(r_angle) * r_dist * 0.4)
            
            # 符文透明度（淡入淡出）
            if rune_phase < 0.3:
                r_alpha = int(200 * (rune_phase / 0.3))
            elif rune_phase < 0.7:
                r_alpha = 200
            else:
                r_alpha = int(200 * (1 - (rune_phase - 0.7) / 0.3))
            r_alpha = max(0, min(255, r_alpha))
            
            if r_alpha > 20:
                # 符文光晕
                pygame.draw.circle(surface, (*theme["rune_primary"], r_alpha // 4), (rx, ry), int(10 * scale))
                pygame.draw.circle(surface, (*theme["rune_primary"], r_alpha // 2), (rx, ry), int(7 * scale))
                draw_rune_symbol(surface, rx, ry, 8 * scale, t * 0.5 + rune, theme["rune_primary"], r_alpha)
        
        # 10.3 岁月裂纹（书表面的古老裂痕）
        for crack in range(8):
            seed = random.Random(crack * 23)
            crack_x = cx + int((seed.random() - 0.5) * 50 * scale)
            crack_y = cy + int((seed.random() - 0.3) * 40 * scale)
            crack_angle = seed.random() * 3.14
            crack_length = int((10 + seed.random() * 15) * scale)
            crack_pulse = 0.4 + 0.6 * math.sin(t * 2 + crack)
            crack_alpha = max(0, min(255, int(100 * crack_pulse)))
            
            cx1 = crack_x
            cy1 = crack_y
            cx2 = crack_x + int(math.cos(crack_angle) * crack_length)
            cy2 = crack_y + int(math.sin(crack_angle) * crack_length * 0.5)
            
            pygame.draw.line(surface, (*theme["gold_trim"], crack_alpha), (cx1, cy1), (cx2, cy2), max(1, int(scale)))
            
            # 裂纹分叉
            if seed.random() > 0.5:
                branch_angle = crack_angle + (0.4 if seed.random() > 0.5 else -0.4)
                branch_len = crack_length * 0.4
                bx = cx2 + int(math.cos(branch_angle) * branch_len)
                by = cy2 + int(math.sin(branch_angle) * branch_len * 0.5)
                pygame.draw.line(surface, (*theme["gold_trim"], max(0, crack_alpha - 30)),
                                (cx2, cy2), (bx, by), 1)
        
        # 10.4 时间沙漏粒子
        hourglass_count = 12
        for hg in range(hourglass_count):
            hg_life = ((t * 18 + hg * 8) % 100) / 100
            
            # 上半部分（落下）
            if hg_life < 0.5:
                hg_t = hg_life / 0.5
                hx = cx + int(math.sin(t * 3 + hg) * 5 * scale * (1 - hg_t))
                hy = cy - int(20 * scale) + int(hg_t * 20 * scale)
            else:
                # 下半部分（堆积）
                hg_t = (hg_life - 0.5) / 0.5
                hx = cx + int((random.Random(hg).random() - 0.5) * 15 * scale * hg_t)
                hy = cy + int(hg_t * 20 * scale)
            
            hg_alpha = max(0, min(255, int(180 * math.sin(hg_life * math.pi))))
            hg_size = max(1, int(2 * scale))
            pygame.draw.circle(surface, (*theme["rune_primary"], hg_alpha), (hx, hy), hg_size)
        
        # 10.5 远古能量环
        elder_ring_pulse = 0.5 + 0.5 * math.sin(t * 1.5)
        elder_ring_alpha = max(0, min(255, int(80 * elder_ring_pulse)))
        pygame.draw.circle(surface, (*theme["gold_trim"], elder_ring_alpha),
                          (cx, cy), int(50 * scale), max(1, int(2 * scale)))
    
    elif theme_name == "frost":
        # ============================================================
        #   霜寒魔典 - 冰晶飘落与霜冻光环
        # ============================================================
        # 10.1 六角冰晶飘落系统
        for ice in range(25):
            i_life = ((t * 12 + ice * 5) % 100) / 100
            seed = random.Random(ice * 11)
            ix = cx + int((seed.random() - 0.5) * 80 * scale)
            ix += int(math.sin(t * 2 + ice) * 5 * scale)
            iy = cy - int(45 * scale) + int(i_life * 100 * scale)
            i_rotation = t * 2 + ice
            i_alpha = max(0, min(255, int(220 * math.sin(i_life * math.pi))))
            i_size = int((5 + seed.random() * 3) * scale)
            
            if i_alpha > 20:
                # 六角冰晶（六条辐射线）
                for spoke in range(6):
                    sp_angle = spoke * 1.047 + i_rotation
                    sp_x = ix + int(math.cos(sp_angle) * i_size)
                    sp_y = iy + int(math.sin(sp_angle) * i_size)
                    pygame.draw.line(surface, (*theme["rune_primary"], i_alpha),
                                    (ix, iy), (sp_x, sp_y), max(1, int(scale)))
                    
                    # 冰晶分叉
                    if i_size > 4 * scale:
                        for branch in [-0.5, 0.5]:
                            br_angle = sp_angle + branch
                            br_len = i_size * 0.5
                            brx = sp_x + int(math.cos(br_angle) * br_len)
                            bry = sp_y + int(math.sin(br_angle) * br_len)
                            pygame.draw.line(surface, (*theme["rune_primary"], max(0, i_alpha - 40)),
                                            (sp_x, sp_y), (brx, bry), 1)
                
                # 冰晶中心
                pygame.draw.circle(surface, (200, 230, 255, i_alpha), (ix, iy), max(1, int(2 * scale)))
        
        # 10.2 多层霜冻光环
        for frost_ring in range(4):
            ring_radius = (58 + frost_ring * 12) * scale  # 外围
            ring_pulse = 0.5 + 0.5 * math.sin(t * 2.5 + frost_ring)
            ring_alpha = max(0, min(255, int((120 - frost_ring * 25) * ring_pulse)))
            ring_width = max(1, int((3 - frost_ring * 0.5) * scale))
            
            # 不完整的环（断裂感）
            for arc in range(6):
                arc_start = t * 0.3 + arc * 1.047 + frost_ring * 0.2
                arc_length = 0.7 + math.sin(t * 3 + arc + frost_ring) * 0.2
                
                for seg in range(8):
                    seg_angle = arc_start + seg * (arc_length / 8)
                    seg_x = cx + int(math.cos(seg_angle) * ring_radius)
                    seg_y = cy + int(math.sin(seg_angle) * ring_radius * 0.4)
                    seg_alpha = max(0, int(ring_alpha * (0.6 + 0.4 * math.sin(t * 4 + seg))))
                    pygame.draw.circle(surface, (*theme["rune_primary"], seg_alpha),
                                      (seg_x, seg_y), ring_width)
        
        # 10.3 寒气蒸腾效果
        for mist in range(15):
            m_life = ((t * 10 + mist * 7) % 80) / 80
            seed = random.Random(mist * 19)
            mx = cx + int((seed.random() - 0.5) * 50 * scale)
            my = cy + int(30 * scale - m_life * 50 * scale)
            m_spread = m_life * 10 * scale
            mx += int(math.sin(t * 2 + mist) * m_spread)
            m_alpha = max(0, min(255, int(100 * math.sin(m_life * math.pi))))
            m_size = int((8 + m_life * 6) * scale)
            
            pygame.draw.circle(surface, (*theme["page_glow"], m_alpha // 4), (mx, my), m_size)
            pygame.draw.circle(surface, (*theme["rune_primary"], m_alpha // 2), (mx, my), int(m_size * 0.6))
        
        # 10.4 冰晶符文
        for fr in range(5):
            fr_angle = t * 0.35 + fr * 1.257
            fr_dist = 62 * scale  # 外围
            frx = cx + int(math.cos(fr_angle) * fr_dist)
            fry = cy + int(math.sin(fr_angle) * fr_dist * 0.35)
            fr_pulse = 0.4 + 0.6 * math.sin(t * 3 + fr * 2)
            fr_alpha = max(0, min(255, int(180 * fr_pulse)))
            
            # 冰晶符文光晕
            pygame.draw.circle(surface, (*theme["rune_primary"], fr_alpha // 4), (frx, fry), int(9 * scale))
            draw_rune_symbol(surface, frx, fry, 6 * scale, t + fr, theme["rune_primary"], fr_alpha)
        
        # 10.5 寒冰碎片闪烁
        for shard in range(8):
            seed = random.Random(shard * 31)
            shx = cx + int((seed.random() - 0.5) * 70 * scale)
            shy = cy + int((seed.random() - 0.5) * 50 * scale)
            sh_pulse = abs(math.sin(t * 6 + shard * 1.3))
            sh_alpha = max(0, min(255, int(200 * sh_pulse))) if sh_pulse > 0.7 else 0
            
            if sh_alpha > 0:
                pygame.draw.circle(surface, (220, 240, 255, sh_alpha), (shx, shy), max(2, int(3 * scale)))
                for ray in range(4):
                    r_angle = ray * 0.785 + t
                    pygame.draw.line(surface, (*theme["rune_primary"], max(0, sh_alpha - 50)),
                                    (shx, shy), (shx + int(math.cos(r_angle) * 5 * scale),
                                                shy + int(math.sin(r_angle) * 5 * scale)), 1)
    
    elif theme_name == "chaos":
        # ============================================================
        #   混沌禁典 - 扭曲闪烁与混沌能量
        # ============================================================
        # 10.1 混沌粒子风暴（不规则运动）
        for ch in range(20):
            # 混沌轨迹（多重正弦叠加）
            ch_angle = (t * 3 + ch * 0.4 + 
                       math.sin(t * 5 + ch) * 0.6 +
                       math.sin(t * 7 + ch * 2) * 0.3)
            ch_dist = (28 + 
                      math.sin(t * 4 + ch * 2) * 15 +
                      math.sin(t * 6 + ch) * 8) * scale
            chx = cx + int(math.cos(ch_angle) * ch_dist)
            chy = cy + int(math.sin(ch_angle) * ch_dist * 0.5)
            
            # 闪烁效果（随机强度）
            ch_flicker = abs(math.sin(t * 8 + ch * 1.5) * math.cos(t * 6 + ch))
            ch_alpha = max(0, min(255, int(230 * ch_flicker)))
            ch_size = max(2, int((5 + math.sin(t * 10 + ch) * 2) * scale))
            
            if ch_alpha > 30:
                # 混沌颜色偏移
                color_shift_r = int(math.sin(t * 12 + ch) * 60)
                color_shift_g = int(math.sin(t * 10 + ch + 2) * 40)
                color_shift_b = int(math.sin(t * 8 + ch + 4) * 50)
                ch_color = (
                    max(0, min(255, theme["rune_primary"][0] + color_shift_r)),
                    max(0, min(255, theme["rune_primary"][1] + color_shift_g)),
                    max(0, min(255, theme["rune_primary"][2] + color_shift_b))
                )
                
                # 粒子光晕
                pygame.draw.circle(surface, (*ch_color, ch_alpha // 3), (chx, chy), ch_size + int(3 * scale))
                pygame.draw.circle(surface, (*ch_color, ch_alpha), (chx, chy), ch_size)
        
        # 10.2 扭曲线网（不规则连接）
        warp_points = []
        for wp in range(8):
            wp_angle = t * 2 + wp * 0.785 + math.sin(t * 4 + wp) * 0.5
            wp_dist = (58 + math.sin(t * 3 + wp * 2) * 10) * scale  # 外围
            wpx = cx + int(math.cos(wp_angle) * wp_dist)
            wpy = cy + int(math.sin(wp_angle) * wp_dist * 0.4)
            warp_points.append((wpx, wpy))
        
        for i in range(len(warp_points)):
            for j in range(i + 1, len(warp_points)):
                # 随机连接
                connect_chance = math.sin(t * 5 + i + j * 2)
                if connect_chance > 0.3:
                    line_alpha = max(0, min(255, int(100 * connect_chance)))
                    pygame.draw.line(surface, (*theme["rune_secondary"], line_alpha),
                                    warp_points[i], warp_points[j], max(1, int(scale)))
        
        # 10.3 空间撕裂效果
        for tear in range(5):
            tear_phase = ((t * 40 + tear * 50) % 200) / 200
            if tear_phase < 0.3:
                seed = random.Random(tear * 17 + int(t // 3))
                tear_x = cx + int((seed.random() - 0.5) * 60 * scale)
                tear_y = cy + int((seed.random() - 0.5) * 40 * scale)
                tear_intensity = math.sin(tear_phase / 0.3 * math.pi)
                tear_alpha = max(0, min(255, int(200 * tear_intensity)))
                tear_length = int(15 * scale * tear_intensity)
                tear_angle = seed.random() * 6.28
                
                # 撕裂线
                tx1 = tear_x - int(math.cos(tear_angle) * tear_length / 2)
                ty1 = tear_y - int(math.sin(tear_angle) * tear_length / 2)
                tx2 = tear_x + int(math.cos(tear_angle) * tear_length / 2)
                ty2 = tear_y + int(math.sin(tear_angle) * tear_length / 2)
                
                pygame.draw.line(surface, (*theme["rune_primary"], tear_alpha), (tx1, ty1), (tx2, ty2), max(2, int(3 * scale)))
                pygame.draw.line(surface, (255, 200, 255, max(0, tear_alpha - 80)), (tx1, ty1), (tx2, ty2), max(1, int(scale)))
        
        # 10.4 混沌脉冲波
        for pulse in range(3):
            pulse_life = ((t * 50 + pulse * 33) % 100) / 100
            pulse_radius = int(pulse_life * 55 * scale)
            # 不规则半径
            irregularity = math.sin(t * 8 + pulse * 3) * 8 * scale
            pulse_alpha = max(0, min(255, int(120 * (1 - pulse_life) * abs(math.sin(pulse_life * 6)))))
            
            if pulse_alpha > 10:
                for seg in range(12):
                    seg_angle = seg * 0.524 + t * 2
                    seg_r = pulse_radius + irregularity * math.sin(seg * 2 + t * 5)
                    seg_x = cx + int(math.cos(seg_angle) * seg_r)
                    seg_y = cy + int(math.sin(seg_angle) * seg_r * 0.4)
                    pygame.draw.circle(surface, (*theme["rune_primary"], pulse_alpha),
                                      (seg_x, seg_y), max(2, int(2.5 * scale)))
        
        # 10.5 能量漩涡核心
        vortex_pulse = 0.6 + 0.4 * math.sin(t * 5)
        vortex_alpha = max(0, min(255, int(150 * vortex_pulse)))
        for v_ring in range(3):
            v_radius = (12 + v_ring * 8) * scale
            v_speed = 3 - v_ring * 0.5
            v_dir = 1 if v_ring % 2 == 0 else -1
            
            for vp in range(8):
                vp_angle = t * v_speed * v_dir + vp * 0.785
                vpx = cx + int(math.cos(vp_angle) * v_radius)
                vpy = cy + int(math.sin(vp_angle) * v_radius * 0.4)
                pygame.draw.circle(surface, (*theme["rune_secondary"], max(0, vortex_alpha - v_ring * 30)),
                                  (vpx, vpy), max(2, int((3 - v_ring * 0.5) * scale)))
    
    elif theme_name == "nature":
        # ============================================================
        #   自然秘典 - 叶片飘落与生命藤蔓
        # ============================================================
        # 10.1 多层叶片飘落系统
        for leaf_layer in range(2):
            leaf_count = 15 - leaf_layer * 5
            for leaf in range(leaf_count):
                l_life = ((t * (10 - leaf_layer * 2) + leaf * 8) % 120) / 120
                seed = random.Random(leaf * 19 + leaf_layer * 1000)
                
                # 叶片轨迹（曲线下落）
                lx = cx + int((seed.random() - 0.5) * (80 - leaf_layer * 15) * scale)
                lx += int(math.sin(t * 2 + leaf + l_life * 4) * 12 * scale)
                ly = cy - int(40 * scale) + int(l_life * 100 * scale)
                l_rotation = t * 3 + leaf + l_life * 2
                l_alpha = max(0, min(255, int((200 - leaf_layer * 50) * math.sin(l_life * math.pi))))
                l_size = int((6 - leaf_layer) * scale)
                
                if l_alpha > 20:
                    # 叶片形状（椭圆+尖端）
                    leaf_pts = [
                        (lx, ly - int(l_size * math.cos(l_rotation))),
                        (lx + int(l_size * 0.7 * math.sin(l_rotation)), ly),
                        (lx, ly + int(l_size * math.cos(l_rotation))),
                        (lx - int(l_size * 0.7 * math.sin(l_rotation)), ly),
                    ]
                    pygame.draw.polygon(surface, (*theme["rune_primary"], l_alpha), leaf_pts)
                    
                    # 叶脉
                    pygame.draw.line(surface, (*theme["rune_secondary"], max(0, l_alpha - 50)),
                                    (leaf_pts[0][0], leaf_pts[0][1]), (leaf_pts[2][0], leaf_pts[2][1]), 1)
        
        # 10.2 生命藤蔓系统（从书四周生长）
        vine_origins = [
            (cx - book_width // 2 - int(5 * scale), cy, 3.14),
            (cx + book_width // 2 + int(5 * scale), cy, 0),
            (cx, cy + book_height // 2 + int(5 * scale), 1.57),
            (cx, cy - book_height // 2 - int(5 * scale), -1.57),
        ]
        
        for vo_idx, (vo_x, vo_y, vo_base_angle) in enumerate(vine_origins):
            vine_segments = 12
            vine_length = (58 + math.sin(t * 1.5 + vo_idx) * 8) * scale  # 外围
            
            prev_x, prev_y = vo_x, vo_y
            for seg in range(vine_segments):
                seg_t = (seg + 1) / vine_segments
                seg_angle = vo_base_angle + math.sin(t * 2 + seg * 0.4 + vo_idx) * 0.4
                seg_dist = vine_length * seg_t
                
                seg_x = vo_x + int(math.cos(seg_angle) * seg_dist)
                seg_y = vo_y + int(math.sin(seg_angle) * seg_dist * 0.5)
                
                v_pulse = 0.5 + 0.5 * math.sin(t * 3 + seg + vo_idx)
                v_alpha = max(0, min(255, int(180 * (1 - seg_t * 0.5) * v_pulse)))
                v_width = max(1, int((4 - seg_t * 3) * scale))
                
                pygame.draw.line(surface, (*theme["rune_secondary"], v_alpha),
                                (prev_x, prev_y), (seg_x, seg_y), v_width)
                
                # 藤蔓节点
                if seg % 3 == 0:
                    pygame.draw.circle(surface, (*theme["rune_primary"], max(0, v_alpha - 30)),
                                      (seg_x, seg_y), max(2, int(2.5 * scale)))
                
                prev_x, prev_y = seg_x, seg_y
            
            # 藤蔓末端花苞
            bud_pulse = 0.6 + 0.4 * math.sin(t * 4 + vo_idx)
            bud_alpha = max(0, min(255, int(200 * bud_pulse)))
            bud_size = int(4 * scale)
            pygame.draw.circle(surface, (*theme["rune_primary"], bud_alpha), (prev_x, prev_y), bud_size)
            pygame.draw.circle(surface, (*theme["page_glow"], max(0, bud_alpha - 60)),
                              (prev_x, prev_y), int(bud_size * 0.6))
        
        # 10.3 花粉/孢子粒子
        for pollen in range(20):
            p_life = ((t * 8 + pollen * 6) % 90) / 90
            seed = random.Random(pollen * 23)
            px = cx + int((seed.random() - 0.5) * 70 * scale)
            px += int(math.sin(t * 3 + pollen) * 10 * scale)
            py = cy + int((seed.random() - 0.3) * 60 * scale)
            py -= int(p_life * 30 * scale)
            
            p_alpha = max(0, min(255, int(150 * math.sin(p_life * math.pi))))
            p_size = max(1, int(2 * scale))
            
            pygame.draw.circle(surface, (*theme["trail"], p_alpha), (px, py), p_size)
        
        # 10.4 生命能量光环
        life_ring_pulse = 0.5 + 0.5 * math.sin(t * 1.8)
        life_ring_alpha = max(0, min(255, int(80 * life_ring_pulse)))
        pygame.draw.circle(surface, (*theme["rune_primary"], life_ring_alpha),
                          (cx, cy), int(48 * scale), max(1, int(2 * scale)))
        
        # 10.5 自然符文
        for nr in range(4):
            nr_angle = t * 0.3 + nr * 1.571
            nr_dist = 60 * scale  # 外围
            nrx = cx + int(math.cos(nr_angle) * nr_dist)
            nry = cy + int(math.sin(nr_angle) * nr_dist * 0.4)
            nr_pulse = 0.5 + 0.5 * math.sin(t * 2.5 + nr * 2)
            nr_alpha = max(0, min(255, int(160 * nr_pulse)))
            
            pygame.draw.circle(surface, (*theme["rune_primary"], nr_alpha // 4), (nrx, nry), int(8 * scale))
            draw_rune_symbol(surface, nrx, nry, 6 * scale, t + nr, theme["rune_primary"], nr_alpha)
    
    # ============================================================
    #   [END] 第十层代码结束
    # ============================================================
    
    # ============================================================
    #   通用效果层 - 所有涂装共享的精细装饰
    # ============================================================
    
    # ---------- 11.1 书籍边缘微光 ----------
    edge_glow_pulse = 0.6 + 0.4 * math.sin(t * 2)
    edge_glow_alpha = max(0, min(255, int(60 * edge_glow_pulse)))
    
    # 上边缘
    for ex in range(int(book_width // (3 * scale))):
        edge_x = cx - book_width // 2 + int(ex * 3 * scale) + int(1.5 * scale)
        edge_y = cy - book_height // 2 + 10
        edge_pulse = 0.5 + 0.5 * math.sin(t * 4 + ex * 0.3)
        e_alpha = max(0, min(255, int(edge_glow_alpha * edge_pulse)))
        pygame.draw.circle(surface, (*theme["page_glow"], e_alpha), (edge_x, edge_y), max(1, int(scale)))
    
    # 下边缘
    for ex in range(int(book_width // (3 * scale))):
        edge_x = cx - book_width // 2 + int(ex * 3 * scale) + int(1.5 * scale)
        edge_y = cy + book_height // 2 + 4
        edge_pulse = 0.5 + 0.5 * math.sin(t * 4 + ex * 0.3 + 1.5)
        e_alpha = max(0, min(255, int(edge_glow_alpha * edge_pulse)))
        pygame.draw.circle(surface, (*theme["page_glow"], e_alpha), (edge_x, edge_y), max(1, int(scale)))
    
    # ---------- 11.2 魔法尘埃飘散 ----------
    for dust in range(25):
        dust_seed = random.Random(dust * 37)
        dust_life = ((t * 6 + dust * 4) % 120) / 120
        
        # 起点在书周围
        dust_angle = dust_seed.random() * 6.28
        dust_start_r = (55 + dust_seed.random() * 15) * scale  # 外围
        dust_x = cx + int(math.cos(dust_angle) * dust_start_r)
        dust_x += int(math.sin(t * 2 + dust) * 8 * scale * dust_life)
        dust_y = cy + int(math.sin(dust_angle) * dust_start_r * 0.4)
        dust_y -= int(dust_life * 40 * scale)
        
        dust_alpha = max(0, min(255, int(100 * math.sin(dust_life * math.pi))))
        dust_size = max(1, int(1.5 * scale * (1 - dust_life * 0.5)))
        
        pygame.draw.circle(surface, (*theme["trail"], dust_alpha), (dust_x, dust_y), dust_size)
    
    # ---------- 11.3 书角装饰光点 ----------
    corner_lights = [
        (cx - book_width // 2 - int(3 * scale), cy - book_height // 2 + 12),
        (cx + book_width // 2 + int(3 * scale), cy - book_height // 2 + 12),
        (cx - book_width // 2 - int(3 * scale), cy + book_height // 2 + 2),
        (cx + book_width // 2 + int(3 * scale), cy + book_height // 2 + 2),
    ]
    
    for cl_idx, (cl_x, cl_y) in enumerate(corner_lights):
        cl_pulse = 0.5 + 0.5 * math.sin(t * 5 + cl_idx * 1.5)
        cl_alpha = max(0, min(255, int(180 * cl_pulse)))
        cl_size = max(2, int(3 * scale * cl_pulse))
        
        # 光点外层
        pygame.draw.circle(surface, (*theme["rune_primary"], cl_alpha // 3), (cl_x, cl_y), cl_size + int(3 * scale))
        # 光点核心
        pygame.draw.circle(surface, (*theme["rune_primary"], cl_alpha), (cl_x, cl_y), cl_size)
        # 高光
        pygame.draw.circle(surface, (255, 255, 255, max(0, cl_alpha - 50)), (cl_x - 1, cl_y - 1), max(1, cl_size // 2))
    
    # ---------- 11.4 脊柱装饰纹路延伸 ----------
    spine_detail_count = 8
    for sd in range(spine_detail_count):
        sd_y = cy - book_height // 2 + 15 + int(sd * (book_height - 10) / spine_detail_count)
        sd_pulse = 0.4 + 0.6 * math.sin(t * 3 + sd * 0.8)
        sd_alpha = max(0, min(255, int(100 * sd_pulse)))
        
        # 左侧延伸
        pygame.draw.line(surface, (*theme["gold_trim"], sd_alpha),
                        (cx - spine_width // 2 - int(2 * scale), sd_y),
                        (cx - spine_width // 2 - int(8 * scale), sd_y), 1)
        # 右侧延伸
        pygame.draw.line(surface, (*theme["gold_trim"], sd_alpha),
                        (cx + spine_width // 2 + int(2 * scale), sd_y),
                        (cx + spine_width // 2 + int(8 * scale), sd_y), 1)
    
    # ---------- 11.5 魔法书签飘带 ----------
    bookmark_count = 2
    for bm in range(bookmark_count):
        bm_x = cx + int((bm - 0.5) * 12 * scale)
        bm_start_y = cy - book_height // 2 + 8
        bm_length = int(25 * scale)
        bm_wave = math.sin(t * 4 + bm * 2) * 6 * scale
        
        prev_x, prev_y = bm_x, bm_start_y
        for seg in range(8):
            seg_t = (seg + 1) / 8
            seg_x = bm_x + int(math.sin(t * 3 + seg * 0.5 + bm) * bm_wave * seg_t)
            seg_y = bm_start_y - int(seg_t * bm_length)
            seg_pulse = 0.6 + 0.4 * math.sin(t * 4 + seg + bm)
            seg_alpha = max(0, min(255, int(200 * seg_pulse * (1 - seg_t * 0.3))))
            seg_width = max(1, int((3 - seg_t) * scale))
            
            pygame.draw.line(surface, (*theme["rune_secondary"], seg_alpha),
                            (prev_x, prev_y), (seg_x, seg_y), seg_width)
            prev_x, prev_y = seg_x, seg_y
        
        # 书签末端装饰
        end_pulse = 0.5 + 0.5 * math.sin(t * 5 + bm)
        end_alpha = max(0, min(255, int(180 * end_pulse)))
        pygame.draw.circle(surface, (*theme["rune_primary"], end_alpha),
                          (prev_x, prev_y), max(2, int(3 * scale)))
    
    # ---------- 11.6 封面浮雕文字光效 ----------
    text_glow_count = 6
    for tg in range(text_glow_count):
        for side in [-1, 1]:
            tg_x = cx + side * (book_width // 4)
            tg_y = cy - book_height // 4 + int(tg * 8 * scale)
            tg_width = int((8 + random.Random(tg + side).random() * 6) * scale)
            tg_pulse = 0.3 + 0.7 * math.sin(t * 2.5 + tg * 0.5 + side)
            tg_alpha = max(0, min(255, int(60 * tg_pulse)))
            
            pygame.draw.line(surface, (*theme["gold_trim"], tg_alpha),
                            (tg_x - tg_width // 2, tg_y), (tg_x + tg_width // 2, tg_y), 1)
    
    # ---------- 11.7 外圈能量护盾涟漪 ----------
    for ripple in range(3):
        ripple_life = ((t * 25 + ripple * 33) % 100) / 100
        ripple_radius = int(50 * scale + ripple_life * 30 * scale)
        ripple_alpha = max(0, min(255, int(50 * (1 - ripple_life))))
        ripple_width = max(1, int((2 - ripple_life) * scale))
        
        if ripple_alpha > 5:
            pygame.draw.circle(surface, (*theme["crystal"], ripple_alpha),
                              (cx, cy), ripple_radius, ripple_width)
    
    # ---------- 11.8 悬浮符号环绕（最外层） ----------
    outer_symbol_count = 12
    outer_orbit_radius = 75 * scale
    for os in range(outer_symbol_count):
        os_angle = t * 0.2 + os * (6.28 / outer_symbol_count)
        os_x = cx + int(math.cos(os_angle) * outer_orbit_radius)
        os_y = cy + int(math.sin(os_angle) * outer_orbit_radius * 0.35)
        os_pulse = 0.3 + 0.7 * math.sin(t * 2 + os * 0.8)
        os_alpha = max(0, min(255, int(80 * os_pulse)))
        os_size = 4 * scale
        
        if os_alpha > 15:
            # 小型符号
            draw_rune_symbol(surface, os_x, os_y, os_size, os_angle + t * 0.5,
                            theme["rune_secondary"], os_alpha)
    
    # ---------- 11.9 书脊中央宝石光芒 ----------
    spine_gem_y = cy
    gem_ray_count = 8
    gem_ray_pulse = 0.5 + 0.5 * math.sin(t * 3)
    gem_ray_alpha = max(0, min(255, int(100 * gem_ray_pulse)))
    
    for ray in range(gem_ray_count):
        ray_angle = t * 0.8 + ray * (6.28 / gem_ray_count)
        ray_length = int((12 + math.sin(t * 4 + ray) * 4) * scale)
        ray_x = cx + int(math.cos(ray_angle) * ray_length)
        ray_y = spine_gem_y + int(math.sin(ray_angle) * ray_length * 0.3)
        
        # 光芒渐变
        for seg in range(5):
            seg_t = seg / 4
            seg_x = cx + int(math.cos(ray_angle) * ray_length * seg_t)
            seg_y = spine_gem_y + int(math.sin(ray_angle) * ray_length * 0.3 * seg_t)
            seg_alpha = max(0, int(gem_ray_alpha * (1 - seg_t * 0.6)))
            seg_size = max(1, int((2 - seg_t) * scale))
            pygame.draw.circle(surface, (*theme["rune_primary"], seg_alpha), (seg_x, seg_y), seg_size)
    
    # ---------- 11.10 整体氛围光晕（最底层但最后绘制以混合） ----------
    # 注意：这个光晕应该非常透明，只是增加氛围感，不能覆盖主体
    # 已移除实心圆绘制，因为它会覆盖掉所有细节渲染

    return surface
