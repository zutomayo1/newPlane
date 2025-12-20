# -*- coding: utf-8 -*-
"""
光之在解·VISCERATOR 涂装系统 - 高精度建模版
原型：Calamity Mod - Photoviscerator（光子在解）
风格：双推进器粒子加速器 + EXO科技 + 粉绿能量

设计理念：
- 核心形态：双引擎粒子加速器，H型对称结构
- 驾驶舱：六边形能量核心舱，全息投影界面
- 引擎：圆柱形EXO推进器，能量环带包裹
- 武装：双聚焦透镜炮台，粒子束发射口
- 特效：粉绿双色能量脉络，等离子尾焰
- 装甲：多层金属板+散热格栅+铆钉细节
"""
import pygame
import math

# ==================== 涂装主题（高精度版 - 高差异化）====================
VISCERATOR_THEMES = {
    # ================= [默认涂装] 光之在解 =================
    # 标志性粉+绿双色，暗青金属装甲
    "viscerator_default": {
        "name": "光之在解·VISCERATOR",
        "desc": "EXO科技的双推进器粒子加速武器",
        # 装甲色系：暗青科技金属
        "armor_main": (47, 79, 79),        # 暗青装甲
        "armor_light": (77, 119, 119),     # 高光
        "armor_dark": (25, 45, 45),        # 深阴影
        "armor_edge": (100, 140, 140),     # 亮边缘
        # 能量色系（标志性粉+绿双色）
        "energy_a": (255, 20, 147),        # 深粉能量
        "energy_b": (127, 255, 0),         # 黄绿能量
        "energy_glow": (255, 100, 180),    # 粉色光晕
        # 细节
        "lens": (255, 80, 200),            # 粉透镜
        "lens_core": (255, 200, 230),      # 透镜核心
        "exhaust": (200, 255, 100),        # 黄绿尾焰
        "rivet": (100, 140, 140),          # 青铆钉
        "vent": (15, 30, 30),              # 深散热口
        "cockpit": (200, 50, 130),         # 紫粉驾驶舱
    },
    
    # ================= [战神系列] 阿瑞斯 =================
    # 血红+烈焰橙，暗铁灰装甲，战争机器
    "viscerator_ares": {
        "name": "战神阿瑞斯·ARES",
        "desc": "战争之神的烈焰推进器",
        # 装甲色系：暗铁灰+血迹斑驳
        "armor_main": (75, 45, 45),        # 血锈铁
        "armor_light": (110, 70, 70),      # 血红高光
        "armor_dark": (45, 25, 25),        # 深血色
        "armor_edge": (140, 90, 90),       # 锈红边
        # 能量色系（血红+烈焰）
        "energy_a": (255, 30, 30),         # 血红
        "energy_b": (255, 150, 0),         # 烈焰橙
        "energy_glow": (255, 80, 30),      # 火焰光晕
        "lens": (255, 50, 50),             # 血红透镜
        "lens_core": (255, 200, 150),      # 火焰核心
        "exhaust": (255, 200, 50),         # 金焰尾焰
        "rivet": (160, 80, 60),            # 铜锈铆钉
        "vent": (50, 20, 15),              # 暗红散热
        "cockpit": (255, 80, 40),          # 火焰驾驶舱
    },
    
    # ================= [死神系列] 塔纳托斯 =================
    # 冰蓝+幽紫，纯黑金属，死亡机械
    "viscerator_thanatos": {
        "name": "死神塔纳托斯·THANATOS",
        "desc": "死亡机械的冰冷光芒",
        # 装甲色系：纯黑死亡金属
        "armor_main": (25, 25, 35),        # 死亡黑
        "armor_light": (50, 55, 75),       # 幽蓝高光
        "armor_dark": (10, 10, 18),        # 深渊黑
        "armor_edge": (70, 80, 110),       # 冷蓝边
        # 能量色系（冰蓝+幽紫）
        "energy_a": (0, 200, 255),         # 冰蓝
        "energy_b": (150, 80, 255),        # 幽紫
        "energy_glow": (80, 180, 255),     # 寒光
        "lens": (100, 200, 255),           # 冰晶透镜
        "lens_core": (200, 230, 255),      # 冰核
        "exhaust": (150, 200, 255),        # 冰焰
        "rivet": (60, 70, 100),            # 暗蓝铆钉
        "vent": (8, 8, 20),                # 深渊散热
        "cockpit": (80, 120, 200),         # 冰蓝驾驶舱
    },
    
    # ================= [月神系列] 阿尔忒弥斯 =================
    # 玫红+银白，银灰金属，月光猎手
    "viscerator_artemis": {
        "name": "月神阿尔忒弥斯·ARTEMIS",
        "desc": "月光女猎手的精准之眼",
        # 装甲色系：银月金属
        "armor_main": (90, 85, 100),       # 银紫
        "armor_light": (140, 135, 160),    # 月光高光
        "armor_dark": (55, 50, 65),        # 暗紫
        "armor_edge": (180, 175, 200),     # 银白边
        # 能量色系（玫红+银白月光）
        "energy_a": (255, 50, 130),        # 玫红
        "energy_b": (230, 220, 255),       # 银白
        "energy_glow": (255, 120, 180),    # 粉光
        "lens": (255, 100, 160),           # 玫瑰透镜
        "lens_core": (255, 220, 240),      # 粉白核心
        "exhaust": (255, 180, 220),        # 粉银尾焰
        "rivet": (150, 140, 170),          # 银铆钉
        "vent": (40, 35, 50),              # 暗紫散热
        "cockpit": (255, 100, 150),        # 玫红驾驶舱
    },
    
    # ================= [日神系列] 阿波罗 =================
    # 翠绿+金黄，深棕金属，太阳战车
    "viscerator_apollo": {
        "name": "日神阿波罗·APOLLO",
        "desc": "太阳战车的翠绿光辉",
        # 装甲色系：深棕金铜
        "armor_main": (80, 60, 40),        # 青铜色
        "armor_light": (130, 100, 60),     # 金铜高光
        "armor_dark": (45, 35, 22),        # 深棕
        "armor_edge": (180, 140, 80),      # 金边
        # 能量色系（翠绿+金黄）
        "energy_a": (50, 255, 80),         # 翠绿
        "energy_b": (255, 220, 50),        # 金黄
        "energy_glow": (150, 255, 100),    # 黄绿光晕
        "lens": (80, 255, 100),            # 翠绿透镜
        "lens_core": (200, 255, 180),      # 浅绿核心
        "exhaust": (220, 255, 80),         # 黄绿尾焰
        "rivet": (160, 130, 80),           # 金铜铆钉
        "vent": (35, 28, 18),              # 深棕散热
        "cockpit": (100, 200, 80),         # 翠绿驾驶舱
    },
    
    # ================= [造物主系列] 德雷顿 =================
    # 纯白+冰蓝，极黑金属，创世科技
    "viscerator_draedon": {
        "name": "造物主德雷顿·DRAEDON",
        "desc": "创世科技的纯白光芒",
        # 装甲色系：极黑科技金属
        "armor_main": (15, 15, 25),        # 极黑
        "armor_light": (40, 45, 65),       # 蓝黑高光
        "armor_dark": (5, 5, 12),          # 深渊黑
        "armor_edge": (60, 70, 100),       # 冷光边
        # 能量色系（纯白+冰蓝）
        "energy_a": (255, 255, 255),       # 纯白
        "energy_b": (150, 200, 255),       # 冰蓝
        "energy_glow": (230, 240, 255),    # 白光
        "lens": (255, 255, 255),           # 纯白透镜
        "lens_core": (255, 255, 255),      # 纯白核心
        "exhaust": (200, 230, 255),        # 冰白尾焰
        "rivet": (50, 55, 80),             # 暗蓝铆钉
        "vent": (3, 3, 10),                # 极黑散热
        "cockpit": (180, 200, 255),        # 冰蓝驾驶舱
    },
}

VISCERATOR_STYLES = list(VISCERATOR_THEMES.keys())

def is_viscerator_style(style):
    return style in VISCERATOR_STYLES

def get_viscerator_theme(style):
    return VISCERATOR_THEMES.get(style, VISCERATOR_THEMES["viscerator_default"])


# ==================== 辅助绘制函数 ====================

def _draw_energy_glow(surf, cx, cy, color, radius, alpha=60):
    """绘制能量光晕"""
    glow_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    for i in range(4):
        r = radius - i * 3
        a = max(0, alpha - i * 15)
        if r > 0 and a > 0:
            pygame.draw.circle(glow_surf, (*color[:3], a), (int(cx), int(cy)), r)
    surf.blit(glow_surf, (0, 0))


def _draw_engine_pod(surf, cx, cy, theme, is_left=True):
    """
    绘制高精度引擎吊舱（参考SCARLET的多层装甲设计）
    - 外层装甲壳体
    - 中层能量环带
    - 内层推进核心
    - 散热格栅
    - 铆钉细节
    """
    armor = theme["armor_main"]
    armor_light = theme["armor_light"]
    armor_dark = theme["armor_dark"]
    armor_edge = theme["armor_edge"]
    energy_a = theme["energy_a"]
    energy_b = theme["energy_b"]
    rivet = theme["rivet"]
    vent = theme["vent"]
    
    mirror = -1 if is_left else 1
    
    # ===== 【第一层】引擎外壳主体 =====
    # 圆柱形引擎吊舱（多边形近似）
    engine_body = [
        (cx + mirror * 2, cy - 28),    # 顶部内侧
        (cx + mirror * 12, cy - 26),   # 顶部外侧
        (cx + mirror * 14, cy - 20),   # 上部外弧
        (cx + mirror * 15, cy - 8),    # 中上外侧
        (cx + mirror * 15, cy + 12),   # 中下外侧
        (cx + mirror * 14, cy + 24),   # 下部外弧
        (cx + mirror * 12, cy + 30),   # 底部外侧
        (cx + mirror * 2, cy + 32),    # 底部内侧
        (cx + mirror * 0, cy + 28),    # 底部内弧
        (cx + mirror * -1, cy + 10),   # 中下内侧
        (cx + mirror * -1, cy - 6),    # 中上内侧
        (cx + mirror * 0, cy - 24),    # 顶部内弧
    ]
    engine_body = [(int(p[0]), int(p[1])) for p in engine_body]
    
    # 阴影层
    pygame.draw.polygon(surf, armor_dark, engine_body)
    
    # ===== 【第二层】装甲高光区 =====
    highlight_body = [
        (cx + mirror * 3, cy - 24),
        (cx + mirror * 10, cy - 22),
        (cx + mirror * 12, cy - 15),
        (cx + mirror * 13, cy - 5),
        (cx + mirror * 13, cy + 8),
        (cx + mirror * 12, cy + 18),
        (cx + mirror * 10, cy + 26),
        (cx + mirror * 3, cy + 28),
        (cx + mirror * 1, cy + 22),
        (cx + mirror * 0, cy + 5),
        (cx + mirror * 0, cy - 8),
        (cx + mirror * 1, cy - 20),
    ]
    highlight_body = [(int(p[0]), int(p[1])) for p in highlight_body]
    pygame.draw.polygon(surf, armor, highlight_body)
    
    # ===== 【第三层】装甲核心高光 =====
    core_highlight = [
        (cx + mirror * 5, cy - 18),
        (cx + mirror * 9, cy - 16),
        (cx + mirror * 10, cy - 8),
        (cx + mirror * 10, cy + 5),
        (cx + mirror * 9, cy + 15),
        (cx + mirror * 5, cy + 20),
        (cx + mirror * 3, cy + 12),
        (cx + mirror * 2, cy),
        (cx + mirror * 3, cy - 12),
    ]
    core_highlight = [(int(p[0]), int(p[1])) for p in core_highlight]
    pygame.draw.polygon(surf, armor_light, core_highlight)
    
    # ===== 装甲边缘线 =====
    pygame.draw.polygon(surf, armor_edge, engine_body, 1)
    
    # ===== 【能量环带】顶部 =====
    ring_y_top = cy - 24
    pygame.draw.ellipse(surf, armor_dark, 
                       (int(cx + mirror * 1 - 6), int(ring_y_top - 3), 14, 6))
    pygame.draw.ellipse(surf, energy_a, 
                       (int(cx + mirror * 1 - 5), int(ring_y_top - 2), 12, 4))
    pygame.draw.ellipse(surf, (255, 255, 255), 
                       (int(cx + mirror * 1 - 3), int(ring_y_top - 1), 6, 2))
    
    # ===== 【能量环带】底部 =====
    ring_y_bot = cy + 26
    pygame.draw.ellipse(surf, armor_dark,
                       (int(cx + mirror * 1 - 6), int(ring_y_bot - 3), 14, 6))
    pygame.draw.ellipse(surf, energy_a,
                       (int(cx + mirror * 1 - 5), int(ring_y_bot - 2), 12, 4))
    pygame.draw.ellipse(surf, (255, 255, 255),
                       (int(cx + mirror * 1 - 3), int(ring_y_bot - 1), 6, 2))
    
    # ===== 中央能量环带 =====
    for i, ry in enumerate([cy - 8, cy + 2, cy + 12]):
        ring_alpha = 180
        pygame.draw.line(surf, armor_edge, 
                        (int(cx + mirror * 0), int(ry)),
                        (int(cx + mirror * 14), int(ry)), 1)
        # 能量条
        energy_color = energy_a if i % 2 == 0 else energy_b
        pygame.draw.line(surf, energy_color,
                        (int(cx + mirror * 2), int(ry + 1)),
                        (int(cx + mirror * 12), int(ry + 1)), 2)
    
    # ===== 散热格栅 =====
    vent_x = cx + mirror * 11
    for vy in range(int(cy - 15), int(cy + 18), 5):
        pygame.draw.line(surf, vent, (int(vent_x), vy), (int(vent_x + mirror * 3), vy), 2)
    
    # ===== 铆钉装饰 =====
    rivet_positions = [
        (cx + mirror * 4, cy - 20),
        (cx + mirror * 4, cy + 22),
        (cx + mirror * 8, cy - 5),
        (cx + mirror * 8, cy + 8),
    ]
    for rx, ry in rivet_positions:
        pygame.draw.circle(surf, rivet, (int(rx), int(ry)), 2)
        pygame.draw.circle(surf, armor_light, (int(rx), int(ry)), 1)


def _draw_central_core(surf, cx, cy, theme):
    """
    绘制中央驾驶舱核心（六边形能量舱）
    - 多层装甲框架
    - 六边形驾驶舱
    - 能量脉络网格
    - 全息投影效果
    """
    armor = theme["armor_main"]
    armor_light = theme["armor_light"]
    armor_dark = theme["armor_dark"]
    armor_edge = theme["armor_edge"]
    energy_a = theme["energy_a"]
    energy_b = theme["energy_b"]
    cockpit = theme["cockpit"]
    
    # ===== 连接臂（上下两条） =====
    # 上连接臂
    arm_top = [
        (cx - 16, cy - 12), (cx + 16, cy - 12),
        (cx + 14, cy - 8), (cx - 14, cy - 8),
    ]
    arm_top = [(int(p[0]), int(p[1])) for p in arm_top]
    pygame.draw.polygon(surf, armor_dark, arm_top)
    pygame.draw.polygon(surf, armor_edge, arm_top, 1)
    # 能量管道
    pygame.draw.line(surf, energy_a, (int(cx - 12), int(cy - 10)), (int(cx + 12), int(cy - 10)), 2)
    
    # 下连接臂
    arm_bot = [
        (cx - 16, cy + 10), (cx + 16, cy + 10),
        (cx + 14, cy + 14), (cx - 14, cy + 14),
    ]
    arm_bot = [(int(p[0]), int(p[1])) for p in arm_bot]
    pygame.draw.polygon(surf, armor_dark, arm_bot)
    pygame.draw.polygon(surf, armor_edge, arm_bot, 1)
    pygame.draw.line(surf, energy_b, (int(cx - 12), int(cy + 12)), (int(cx + 12), int(cy + 12)), 2)
    
    # ===== 中央脊柱 =====
    spine = [
        (cx - 3, cy - 22), (cx + 3, cy - 22),
        (cx + 4, cy - 5), (cx + 4, cy + 8),
        (cx + 3, cy + 24), (cx - 3, cy + 24),
        (cx - 4, cy + 8), (cx - 4, cy - 5),
    ]
    spine = [(int(p[0]), int(p[1])) for p in spine]
    pygame.draw.polygon(surf, armor, spine)
    pygame.draw.polygon(surf, armor_edge, spine, 1)
    # 脊柱能量线
    pygame.draw.line(surf, energy_a, (int(cx), int(cy - 20)), (int(cx), int(cy - 5)), 1)
    pygame.draw.line(surf, energy_b, (int(cx), int(cy + 5)), (int(cx), int(cy + 22)), 1)
    
    # ===== 六边形驾驶舱 =====
    hex_size = 10
    hex_points = []
    for i in range(6):
        angle = math.radians(60 * i - 90)
        hx = cx + math.cos(angle) * hex_size
        hy = cy + math.sin(angle) * hex_size * 0.8
        hex_points.append((int(hx), int(hy)))
    
    # 驾驶舱外框
    pygame.draw.polygon(surf, armor_dark, hex_points)
    # 驾驶舱玻璃
    inner_hex = []
    for i in range(6):
        angle = math.radians(60 * i - 90)
        hx = cx + math.cos(angle) * (hex_size - 3)
        hy = cy + math.sin(angle) * (hex_size - 3) * 0.8
        inner_hex.append((int(hx), int(hy)))
    pygame.draw.polygon(surf, cockpit, inner_hex)
    # 驾驶舱高光
    pygame.draw.polygon(surf, energy_a, hex_points, 1)
    pygame.draw.circle(surf, (255, 255, 255), (int(cx - 2), int(cy - 3)), 2)
    
    # ===== 能量脉络 =====
    pulse_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    # 从驾驶舱向两侧延伸
    for i, angle in enumerate([150, 210, 30, -30]):
        rad = math.radians(angle)
        ex = cx + math.cos(rad) * 18
        ey = cy + math.sin(rad) * 12
        color = energy_a if i < 2 else energy_b
        pygame.draw.line(pulse_surf, (*color, 150), (int(cx), int(cy)), (int(ex), int(ey)), 1)
    surf.blit(pulse_surf, (0, 0))


def _draw_focusing_lens(surf, cx, cy, theme, is_left=True):
    """
    绘制聚焦透镜炮台
    - 底座装甲
    - 多层透镜
    - 能量聚焦核心
    - 瞄准激光
    """
    armor = theme["armor_main"]
    armor_dark = theme["armor_dark"]
    armor_edge = theme["armor_edge"]
    lens = theme["lens"]
    lens_core = theme["lens_core"]
    energy_a = theme["energy_a"]
    
    mirror = -1 if is_left else 1
    
    # ===== 透镜底座 =====
    base_x = cx + mirror * 22
    base_y = cy - 28
    
    # 底座装甲（八边形）
    base_size = 10
    base_pts = []
    for i in range(8):
        angle = math.radians(45 * i - 22.5)
        bx = base_x + math.cos(angle) * base_size
        by = base_y + math.sin(angle) * base_size * 0.7
        base_pts.append((int(bx), int(by)))
    pygame.draw.polygon(surf, armor_dark, base_pts)
    pygame.draw.polygon(surf, armor_edge, base_pts, 1)
    
    # ===== 外层透镜环 =====
    pygame.draw.circle(surf, armor, (int(base_x), int(base_y)), 8)
    pygame.draw.circle(surf, armor_edge, (int(base_x), int(base_y)), 8, 1)
    
    # ===== 中层透镜 =====
    pygame.draw.circle(surf, lens, (int(base_x), int(base_y)), 6)
    
    # ===== 内层能量核心 =====
    pygame.draw.circle(surf, lens_core, (int(base_x), int(base_y)), 4)
    pygame.draw.circle(surf, (255, 255, 255), (int(base_x), int(base_y)), 2)
    
    # ===== 高光反射 =====
    pygame.draw.circle(surf, (255, 255, 255), (int(base_x - 2), int(base_y - 2)), 1)
    
    # ===== 透镜支架 =====
    pygame.draw.line(surf, armor_edge, (int(base_x), int(base_y + 7)), 
                    (int(base_x + mirror * 3), int(base_y + 15)), 2)
    pygame.draw.line(surf, armor_edge, (int(base_x + mirror * 5), int(base_y)),
                    (int(base_x + mirror * 8), int(base_y + 5)), 1)


def _draw_exhaust_flame(surf, cx, cy, theme, is_left=True):
    """
    绘制静态尾焰
    - 多层渐变
    - 粉绿双色
    """
    energy_a = theme["energy_a"]
    energy_b = theme["energy_b"]
    exhaust = theme["exhaust"]
    
    mirror = -1 if is_left else 1
    ex = cx + mirror * 7
    ey = cy + 32
    
    # 外层光晕
    glow_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    pygame.draw.ellipse(glow_surf, (*energy_a[:3], 40), (int(ex - 6), int(ey), 12, 25))
    surf.blit(glow_surf, (0, 0))
    
    # 主尾焰（渐变）
    pygame.draw.polygon(surf, exhaust, [
        (int(ex - 4), int(ey)),
        (int(ex + 4), int(ey)),
        (int(ex + 2), int(ey + 15)),
        (int(ex), int(ey + 22)),
        (int(ex - 2), int(ey + 15)),
    ])
    
    # 核心亮线
    pygame.draw.line(surf, energy_b, (int(ex), int(ey)), (int(ex), int(ey + 18)), 2)
    pygame.draw.line(surf, (255, 255, 255), (int(ex), int(ey)), (int(ex), int(ey + 12)), 1)


# ==================== 预渲染缓存 ====================
_cache = {}  # (size, style) -> Surface


def _build_cache(size, style):
    """预渲染高精度机体Surface（静态部分）"""
    theme = get_viscerator_theme(style)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    
    # ===== 【左引擎吊舱】=====
    _draw_engine_pod(surf, cx - 15, cy, theme, True)
    
    # ===== 【右引擎吊舱】=====
    _draw_engine_pod(surf, cx + 15, cy, theme, False)
    
    # ===== 【中央核心】=====
    _draw_central_core(surf, cx, cy, theme)
    
    # ===== 【聚焦透镜】=====
    _draw_focusing_lens(surf, cx, cy, theme, True)
    _draw_focusing_lens(surf, cx, cy, theme, False)
    
    return surf


def _draw_dynamic_effects(surface, size, style, frame, ult_charge=0):
    """
    绘制动态效果层（每帧更新）
    - 粒子加速器威压涟漪（SCARLET血色威压级别）
    - 双色恐怖光晕（末世感）
    - 次元裂隙效果
    - 暗角压迫
    - 尾焰摆动
    - 透镜闪烁
    """
    theme = get_viscerator_theme(style)
    cx, cy = size // 2, size // 2
    
    energy_a = theme["energy_a"]
    energy_b = theme["energy_b"]
    lens = theme["lens"]
    lens_core = theme["lens_core"]
    exhaust = theme["exhaust"]
    cockpit = theme["cockpit"]
    
    t = frame * 0.1  # 时间因子
    pulse = 1.0 + math.sin(t * 3) * 0.3
    doom_pulse = abs(math.sin(t * 2.5))
    
    dyn_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # ========== 【第零层】粒子加速器威压背景 ==========
    
    # ===== 末世压迫感背景（层层黑暗深渊） =====
    void_color = (20, 5, 30)  # 深紫黑虚空
    for layer in range(5):
        doom_r = size * (0.52 - layer * 0.06) + math.sin(t * 0.8 + layer) * 4
        doom_alpha = int((50 - layer * 8) * doom_pulse)
        if doom_alpha > 0:
            pygame.draw.circle(dyn_surf, (*void_color, doom_alpha), (cx, cy), int(doom_r))
    
    # ===== 双色恐惧涟漪（粉绿交织扩散） =====
    for ring in range(6):
        ripple_phase = (t * 0.4 + ring * 0.17) % 1.0
        ripple_r = size * 0.15 + ripple_phase * size * 0.4
        ripple_alpha = int(70 * (1 - ripple_phase))
        ring_color = energy_a if ring % 2 == 0 else energy_b
        if ripple_alpha > 5:
            pygame.draw.circle(dyn_surf, (*ring_color[:3], ripple_alpha), (cx, cy), int(ripple_r), 2)
    
    # ===== 粒子流恐怖光晕（脉动） =====
    for i in range(7):
        glow_r = int(size * 0.48 - i * size * 0.05 + 4 * math.sin(t * 1.5 + i * 0.3))
        glow_alpha = max(0, int(35 * doom_pulse) - i * 4)
        glow_color = energy_a if i % 2 == 0 else energy_b
        if glow_r > 0 and glow_alpha > 0:
            pygame.draw.circle(dyn_surf, (*glow_color[:3], glow_alpha), (cx, cy), glow_r)
    
    # ===== 次元裂隙（粒子加速器能量撕裂空间） =====
    crack_color = (255, 180, 255)  # 亮粉裂隙
    for i in range(6):
        crack_angle = t * 0.15 + i * math.pi / 3
        crack_len = size * 0.42
        
        points = [(cx, cy)]
        for seg in range(5):
            prog = (seg + 1) / 5
            jitter_x = math.sin(t * 0.5 + i + seg * 0.7) * 8 * prog
            jitter_y = math.cos(t * 0.6 + i * 2 + seg) * 6 * prog
            px = cx + math.cos(crack_angle) * crack_len * prog + jitter_x
            py = cy + math.sin(crack_angle) * crack_len * prog * 0.7 + jitter_y
            points.append((int(px), int(py)))
        
        if len(points) >= 2:
            # 裂隙外晕
            pygame.draw.lines(dyn_surf, (*energy_a[:3], 50), False, points, 4)
            # 裂隙主体
            pygame.draw.lines(dyn_surf, (*crack_color, 120), False, points, 2)
    
    # ===== 能量粒子云（飘散的高能粒子） =====
    for i in range(16):
        particle_angle = t * 0.25 + i * 0.4
        particle_r = size * 0.25 + i * size * 0.015 + math.sin(t * 1.2 + i) * 6
        particle_x = cx + math.cos(particle_angle) * particle_r
        particle_y = cy + math.sin(particle_angle * 0.7) * particle_r * 0.65
        particle_size = 4 + math.sin(t * 2.5 + i * 0.6) * 2
        particle_alpha = int(60 + math.sin(t * 3 + i) * 30)
        p_color = energy_a if i % 2 == 0 else energy_b
        pygame.draw.circle(dyn_surf, (*p_color[:3], particle_alpha), (int(particle_x), int(particle_y)), int(particle_size))
    
    # ===== 六芒星能量几何（神圣压迫） =====
    hex_r = size * 0.38 + math.sin(t * 1.2) * 3
    hex_alpha = int(45 * doom_pulse)
    for ring in range(2):
        ring_r = hex_r - ring * 8
        if ring_r > 0:
            hex_pts = []
            for i in range(6):
                angle = math.radians(i * 60 + 30 + t * 12)
                hx = cx + math.cos(angle) * ring_r
                hy = cy + math.sin(angle) * ring_r * 0.85
                hex_pts.append((int(hx), int(hy)))
            hex_color = energy_a if ring == 0 else energy_b
            pygame.draw.polygon(dyn_surf, (*hex_color[:3], max(0, hex_alpha - ring * 15)), hex_pts, 2)
    
    # ===== 暗角效果（四角暗化增强压迫感） =====
    corner_alpha = int(55 * doom_pulse)
    for corner_x, corner_y in [(0, 0), (size, 0), (0, size), (size, size)]:
        for i in range(6):
            corner_r = int(size * 0.32 - i * size * 0.04)
            c_alpha = corner_alpha - i * 8
            if c_alpha > 0 and corner_r > 0:
                pygame.draw.circle(dyn_surf, (0, 0, 0, c_alpha), (corner_x, corner_y), corner_r)
    
    # ========== 【第一层】能量光晕脉动 ==========
    glow_alpha = int(35 + math.sin(t * 4) * 20)
    
    # 中央光晕
    for i in range(4):
        r = int((40 + i * 8) * pulse)
        a = max(0, glow_alpha - i * 6)
        if a > 0:
            pygame.draw.circle(dyn_surf, (*energy_a[:3], a), (cx, cy), r)
    
    # 左引擎光晕
    for i in range(3):
        r = int((22 + i * 6) * pulse)
        a = max(0, glow_alpha - i * 8)
        if a > 0:
            pygame.draw.circle(dyn_surf, (*energy_a[:3], a), (cx - 22, cy), r)
    
    # 右引擎光晕
    for i in range(3):
        r = int((22 + i * 6) * pulse)
        a = max(0, glow_alpha - i * 8)
        if a > 0:
            pygame.draw.circle(dyn_surf, (*energy_b[:3], a), (cx + 22, cy), r)
    
    # ===== 【2】动态尾焰 =====
    flame_wave = math.sin(t * 8)
    flame_length = 18 + flame_wave * 6
    flame_sway = math.sin(t * 5) * 2
    
    for side, color in [(-22, energy_a), (22, energy_b)]:
        ex = cx + side // 3
        ey = cy + 32
        
        # 外层光晕
        glow_r = int(8 + abs(flame_wave) * 4)
        pygame.draw.ellipse(dyn_surf, (*color[:3], 50), 
                           (int(ex - glow_r), int(ey - 2), glow_r * 2, int(flame_length + 10)))
        
        # 主尾焰
        flame_pts = [
            (int(ex - 5 + flame_sway * 0.5), int(ey)),
            (int(ex + 5 + flame_sway * 0.5), int(ey)),
            (int(ex + 3 + flame_sway), int(ey + flame_length * 0.7)),
            (int(ex + flame_sway * 1.5), int(ey + flame_length)),
            (int(ex - 3 + flame_sway), int(ey + flame_length * 0.7)),
        ]
        pygame.draw.polygon(dyn_surf, exhaust, flame_pts)
        
        # 核心亮焰
        core_pts = [
            (int(ex - 2), int(ey)),
            (int(ex + 2), int(ey)),
            (int(ex + flame_sway * 0.8), int(ey + flame_length * 0.8)),
        ]
        pygame.draw.polygon(dyn_surf, (255, 255, 255), core_pts)
        
        # 火花粒子
        for i in range(3):
            spark_y = ey + (frame * 3 + i * 8) % int(flame_length + 5)
            spark_x = ex + math.sin(t * 10 + i * 2) * 3 + flame_sway
            spark_a = max(0, 200 - (spark_y - ey) * 8)
            if spark_a > 0:
                pygame.draw.circle(dyn_surf, (*color[:3], spark_a), 
                                  (int(spark_x), int(spark_y)), 2)
    
    # ===== 【3】透镜闪烁 =====
    lens_pulse = 0.8 + abs(math.sin(t * 6)) * 0.4
    lens_alpha = int(180 + math.sin(t * 5) * 75)
    
    for side in [-22, 22]:
        lx = cx + side
        ly = cy - 28
        
        # 透镜光晕
        pygame.draw.circle(dyn_surf, (*lens[:3], int(60 * lens_pulse)), 
                          (lx, ly), int(10 * lens_pulse))
        # 透镜核心闪烁
        pygame.draw.circle(dyn_surf, (*lens_core[:3], lens_alpha), (lx, ly), 4)
        pygame.draw.circle(dyn_surf, (255, 255, 255, lens_alpha), (lx, ly), 2)
        
        # 瞄准激光（短）
        laser_len = 8 + math.sin(t * 4 + side) * 3
        pygame.draw.line(dyn_surf, (*lens[:3], 150), (lx, ly - 8), (lx, ly - 8 - int(laser_len)), 1)
    
    # ===== 【4】能量环流动 =====
    ring_offset = (frame * 2) % 20
    ring_alpha = int(100 + math.sin(t * 3) * 50)
    
    for side in [-15, 15]:
        engine_x = cx + side
        # 上下移动的能量环
        for i in range(3):
            ry = cy - 20 + ((ring_offset + i * 7) % 20)
            if cy - 20 <= ry <= cy + 5:
                ring_color = energy_a if side < 0 else energy_b
                pygame.draw.ellipse(dyn_surf, (*ring_color[:3], ring_alpha // 2),
                                   (engine_x - 8 + side // 10, ry - 1, 16, 3))
    
    # ===== 【5】驾驶舱光效 =====
    cockpit_pulse = abs(math.sin(t * 2))
    cockpit_alpha = int(80 + cockpit_pulse * 80)
    
    # 驾驶舱内部光
    pygame.draw.circle(dyn_surf, (*cockpit[:3], cockpit_alpha // 2), (cx, cy), 8)
    pygame.draw.circle(dyn_surf, (*energy_a[:3], cockpit_alpha), (cx, cy), 5)
    
    # 全息投影线
    holo_alpha = int(60 + math.sin(t * 4) * 40)
    for i in range(4):
        angle = math.radians(90 * i + frame * 3)
        hx = cx + math.cos(angle) * 6
        hy = cy + math.sin(angle) * 4
        pygame.draw.line(dyn_surf, (*energy_a[:3], holo_alpha), 
                        (cx, cy), (int(hx), int(hy)), 1)
    
    # ===== 【6】充能效果（ult_charge > 50时） =====
    if ult_charge > 50:
        charge_intensity = (ult_charge - 50) / 50
        charge_alpha = int(100 * charge_intensity)
        charge_pulse = 1 + math.sin(t * 6) * 0.2
        
        # 充能光环
        for i in range(3):
            r = int((35 + i * 8) * charge_pulse)
            a = max(0, charge_alpha - i * 25)
            if a > 0:
                pygame.draw.circle(dyn_surf, (*energy_a[:3], a), (cx, cy), r, 2)
        
        # 能量粒子环绕
        for i in range(6):
            p_angle = math.radians(60 * i + frame * 5)
            p_dist = 30 + math.sin(t * 4 + i) * 5
            px = cx + math.cos(p_angle) * p_dist
            py = cy + math.sin(p_angle) * p_dist * 0.6
            p_color = energy_a if i % 2 == 0 else energy_b
            pygame.draw.circle(dyn_surf, (*p_color[:3], charge_alpha), (int(px), int(py)), 3)
    
    surface.blit(dyn_surf, (0, 0))


def draw_viscerator_plane(surface, style, frame, damage_flash=0, shield_active=False, ult_charge=0):
    """绘制机体 - 静态缓存 + 动态效果层"""
    size = surface.get_width()
    cache_key = (size, style)
    
    # 获取或创建缓存
    if cache_key not in _cache:
        _cache[cache_key] = _build_cache(size, style)
    
    surface.fill((0, 0, 0, 0))
    
    # 受伤闪白
    if damage_flash > 0 and (damage_flash // 2) % 2 == 0:
        # 绘制白色轮廓
        white_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        pygame.draw.rect(white_surf, (255, 255, 255), (cx - 30, cy - 30, 60, 65))
        surface.blit(white_surf, (0, 0))
    else:
        # 先绘制动态效果（在机体下方）
        _draw_dynamic_effects(surface, size, style, frame, ult_charge)
        # 再绘制静态机体
        surface.blit(_cache[cache_key], (0, 0))
        # 最后再绘制一层顶部动态效果
        _draw_top_effects(surface, size, style, frame)
    
    # 护盾效果
    if shield_active:
        shield_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        for i in range(3):
            r = 40 - i * 5 + int(math.sin(frame * 0.2) * 3)
            pygame.draw.circle(shield_surf, (100, 200, 255, 60 - i * 15), (cx, cy), r, 2)
        surface.blit(shield_surf, (0, 0))
    
    return surface


def _draw_top_effects(surface, size, style, frame):
    """绘制顶层动态效果（覆盖在机体上方）- 威压强化版"""
    theme = get_viscerator_theme(style)
    cx, cy = size // 2, size // 2
    t = frame * 0.1
    
    energy_a = theme["energy_a"]
    energy_b = theme["energy_b"]
    lens_core = theme["lens_core"]
    
    top_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    doom_pulse = abs(math.sin(t * 2.5))
    
    # ===== 【威压光柱】从透镜射出的恐怖激光 =====
    for side in [-22, 22]:
        lx = cx + side
        ly = cy - 28
        
        # 激光威压柱（向前延伸）
        beam_length = size * 0.35 + math.sin(t * 4) * 8
        beam_alpha = int(80 + doom_pulse * 60)
        beam_color = energy_a if side < 0 else energy_b
        
        # 光柱外晕
        pygame.draw.line(top_surf, (*beam_color[:3], beam_alpha // 2), 
                        (lx, ly), (lx, ly - int(beam_length)), 6)
        # 光柱核心
        pygame.draw.line(top_surf, (*beam_color[:3], beam_alpha), 
                        (lx, ly), (lx, ly - int(beam_length)), 2)
        # 尖端闪光
        pygame.draw.circle(top_surf, (255, 255, 255, beam_alpha), 
                          (lx, int(ly - beam_length)), 3)
    
    # ===== 【恐惧之眼】透镜顶层闪烁（像恶魔之眼） =====
    lens_flash = int(220 + math.sin(t * 7) * 35)
    for side in [-22, 22]:
        lx = cx + side
        ly = cy - 28
        # 外圈光晕
        pygame.draw.circle(top_surf, (*lens_core[:3], int(lens_flash * 0.5)), (lx, ly), 6)
        # 内圈亮核
        pygame.draw.circle(top_surf, (255, 255, 255, lens_flash), (lx, ly), 3)
        # 瞳孔（黑点增加恐惧感）
        pygame.draw.circle(top_surf, (0, 0, 0, 200), (lx, ly), 1)
    
    # ===== 【能量脉冲波】从机体中心向外的威压波 =====
    for i in range(3):
        pulse_phase = (t * 0.5 + i * 0.33) % 1.0
        pulse_r = size * 0.1 + pulse_phase * size * 0.3
        pulse_alpha = int(100 * (1 - pulse_phase) * doom_pulse)
        if pulse_alpha > 5:
            pulse_color = energy_a if i % 2 == 0 else energy_b
            pygame.draw.circle(top_surf, (*pulse_color[:3], pulse_alpha), (cx, cy), int(pulse_r), 1)
    
    # ===== 【引擎顶部能量闪烁】=====
    engine_flash = int(150 + math.sin(t * 5) * 100)
    for side, color in [(-15, energy_a), (15, energy_b)]:
        # 能量核心
        pygame.draw.circle(top_surf, (*color[:3], engine_flash // 2), 
                          (cx + side - side // 15, cy - 22), 5)
        pygame.draw.circle(top_surf, (255, 255, 255, engine_flash), 
                          (cx + side - side // 15, cy - 22), 2)
    
    # ===== 【驾驶舱高光点】=====
    cockpit_flash = int(200 + math.sin(t * 3) * 55)
    pygame.draw.circle(top_surf, (255, 255, 255, cockpit_flash), (cx - 2, cy - 3), 2)
    
    # ===== 【能量粒子喷射】从引擎喷出的威压粒子 =====
    for side in [-1, 1]:
        for i in range(5):
            particle_phase = (t * 1.5 + i * 0.2) % 1.0
            particle_y = cy + 32 + particle_phase * 25
            particle_x = cx + side * 7 + math.sin(t * 8 + i) * 3
            particle_alpha = int(180 * (1 - particle_phase))
            particle_color = energy_a if side < 0 else energy_b
            if particle_alpha > 10:
                pygame.draw.circle(top_surf, (*particle_color[:3], particle_alpha), 
                                  (int(particle_x), int(particle_y)), 2)
    
    surface.blit(top_surf, (0, 0))
