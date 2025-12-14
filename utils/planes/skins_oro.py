# -*- coding: utf-8 -*-
"""
维度吞噬者·神杀 (Deus-Eater · Godslayer)
TYPE-VOID "UNIVERSAL COLLAPSE"

设计理念：维度穿梭型 · 轨道炮击战舰
视觉关键词：赛博蠕虫、虚空紫、激光网格、浮游装甲

12款皮肤系列：
- 传说重现：原初、幽灵、重装
- 元素反转：熔岩、冰晶、辐射
- 概念重构：黑客、水墨、折纸
- 终极幻想：虚空、齿轮、终焉
"""
import pygame
import math
import random

# =============================================================================
#   12款皮肤配置 (借鉴神明吞噬者设计)
# =============================================================================

ORO_SKINS = {
    # ================= [系列一：传说重现] =================
    "oro_default": {
        "name": "宇宙吞噬者·原初",
        "colors": {"body": (20, 20, 30), "core": (148, 0, 211), "glow": (0, 255, 255)},
        "shape": "rect",
        "style": "standard",  # 标准装甲
    },
    "oro_phantom": {
        "name": "星神游龙·幽灵",
        "colors": {"body": (30, 30, 50), "core": (100, 149, 237), "glow": (255, 255, 255)},
        "shape": "circle",
        "style": "ghost",  # 半透明+模糊
    },
    "oro_golden": {
        "name": "弑神装甲·重装",
        "colors": {"body": (50, 50, 50), "core": (255, 215, 0), "glow": (255, 69, 0)},
        "shape": "hexagon",
        "style": "metallic",  # 六边形重甲
    },

    # ================= [系列二：元素反转] =================
    "oro_inferno": {
        "name": "狱炎长虫·熔岩",
        "colors": {"body": (139, 0, 0), "core": (255, 140, 0), "glow": (255, 255, 0)},
        "shape": "circle",
        "style": "magma",  # 核心闪烁
    },
    "oro_frost": {
        "name": "极地灾厄·冰晶",
        "colors": {"body": (240, 255, 255), "core": (0, 191, 255), "glow": (255, 255, 255)},
        "shape": "diamond",
        "style": "shard",  # 锐利的菱形
    },
    "oro_toxic": {
        "name": "生化危机·辐射",
        "colors": {"body": (50, 50, 0), "core": (50, 205, 50), "glow": (173, 255, 47)},
        "shape": "organic",
        "style": "slime",  # 不规则蠕动
    },

    # ================= [系列三：概念重构] =================
    "oro_cosmic": {
        "name": "矩阵代码·黑客",
        "colors": {"body": (0, 0, 0), "core": (0, 255, 0), "glow": (0, 255, 0)},
        "shape": "rect",
        "style": "wireframe",  # 空心线框
    },
    "oro_royal": {
        "name": "水墨游龙·写意",
        "colors": {"body": (0, 0, 0), "core": (255, 255, 255), "glow": (100, 100, 100)},
        "shape": "circle",
        "style": "ink",  # 边缘抖动
    },
    "oro_crimson": {
        "name": "折纸大蛇·维度",
        "colors": {"body": (255, 250, 205), "core": (220, 20, 60), "glow": (0, 0, 0)},
        "shape": "diamond",
        "style": "flat",  # 无光效，纯色
    },

    # ================= [系列四：终极幻想] =================
    "oro_void": {
        "name": "视界线·虚空",
        "colors": {"body": (0, 0, 0), "core": (0, 0, 0), "glow": (138, 43, 226)},
        "shape": "diamond",
        "style": "void",  # 纯黑+外发光脉冲
    },
    "oro_abyss": {
        "name": "机械降神·齿轮",
        "colors": {"body": (139, 69, 19), "core": (0, 255, 255), "glow": (218, 165, 32)},
        "shape": "gear",
        "style": "steampunk",  # 齿轮状
    },
    "oro_blood": {
        "name": "数据删除·终焉",
        "colors": {"body": (255, 255, 255), "core": (255, 0, 0), "glow": (255, 0, 0)},
        "shape": "rect",
        "style": "glitch",  # 随机色块+位移
    },
}

# 涂装样式列表
ORO_STYLES = list(ORO_SKINS.keys())


def is_oro_style(model_style):
    """检查是否为奥罗涂装"""
    return model_style in ORO_STYLES


def get_skin(style):
    """获取皮肤配置"""
    return ORO_SKINS.get(style, ORO_SKINS["oro_default"])


# =============================================================================
#   节段绘制核心函数 - 支持多种形状和风格
# =============================================================================

def _draw_segment(s, cx, cy, size, t, seg_index, skin, is_head=False):
    """
    绘制单个节段
    s: 目标surface
    cx, cy: 中心坐标
    size: 节段大小
    t: 时间/帧数
    seg_index: 节段索引（用于波动偏移）
    skin: 皮肤配置
    is_head: 是否为头部
    """
    cols = skin['colors']
    shape = skin['shape']
    style = skin['style']
    
    # 特效：呼吸脉动 (Magma/Organic/Void)
    if style in ["magma", "slime", "void", "pulse"]:
        size += math.sin(t * 0.15 - seg_index * 0.3) * 3
    
    size = int(size)
    
    # --- 形状绘制逻辑 ---
    
    # 1. 矩形 (Rect) - 适用于: 原始, 矩阵, 故障
    if shape == "rect":
        r_w, r_h = int(size * 1.0), int(size * 0.7)
        r_rect = pygame.Rect(cx - r_w // 2, cy - r_h // 2, r_w, r_h)
        
        if style == "wireframe":  # 矩阵风格：空心线框
            pygame.draw.rect(s, cols['core'], r_rect, 1)
            pygame.draw.rect(s, (*cols['glow'], 150), r_rect.inflate(4, 4), 1)
        elif style == "glitch":  # 故障风格：随机位移
            off_x = random.randint(-3, 3)
            off_y = random.randint(-2, 2)
            pygame.draw.rect(s, cols['body'], r_rect.move(off_x, off_y))
            pygame.draw.rect(s, cols['core'], r_rect.inflate(-8, -8))
            # 故障条纹
            if random.random() > 0.7:
                glitch_y = cy + random.randint(-r_h // 2, r_h // 2)
                pygame.draw.line(s, cols['glow'], (cx - r_w, glitch_y), (cx + r_w, glitch_y), 1)
        else:  # standard: 标准装甲
            pygame.draw.rect(s, cols['body'], r_rect)
            pygame.draw.rect(s, cols['glow'], r_rect, 2)
            # 内核
            inner = r_rect.inflate(-10, -8)
            if inner.width > 0 and inner.height > 0:
                pygame.draw.rect(s, cols['core'], inner)
    
    # 2. 圆形 (Circle/Organic) - 适用于: 幽灵, 熔岩, 水墨, 辐射
    elif shape == "circle" or shape == "organic":
        radius = size // 2
        
        if style == "ink":  # 水墨抖动
            radius += random.randint(-1, 1)
            pygame.draw.circle(s, cols['body'], (cx, cy), radius)
            pygame.draw.circle(s, (*cols['glow'], 120), (cx, cy), radius, 1)
            # 墨点飞溅
            for _ in range(2):
                sx = cx + random.randint(-radius, radius)
                sy = cy + random.randint(-radius // 2, radius // 2)
                pygame.draw.circle(s, cols['body'], (sx, sy), random.randint(1, 3))
        elif style == "ghost":  # 半透明幽灵
            pygame.draw.circle(s, (*cols['body'], 100), (cx, cy), radius)
            pygame.draw.circle(s, (*cols['core'], 180), (cx, cy), radius // 2)
            # 幽灵光晕
            for i in range(3):
                pygame.draw.circle(s, (*cols['glow'], 30 - i * 10), (cx, cy), radius + i * 3, 1)
        elif style == "magma":  # 熔岩脉动
            # 外壳
            pygame.draw.circle(s, cols['body'], (cx, cy), radius)
            # 熔岩核心（脉动）
            core_pulse = abs(math.sin(t * 0.2 + seg_index * 0.5))
            core_r = int(radius * 0.5 * (0.7 + core_pulse * 0.3))
            pygame.draw.circle(s, cols['core'], (cx, cy), core_r)
            pygame.draw.circle(s, cols['glow'], (cx, cy), core_r, 2)
        elif style == "slime":  # 有机蠕动
            # 不规则边缘
            pts = []
            for i in range(8):
                angle = i * math.pi / 4
                r = radius + math.sin(t * 0.2 + i + seg_index) * 3
                px = cx + math.cos(angle) * r
                py = cy + math.sin(angle) * r
                pts.append((px, py))
            pygame.draw.polygon(s, cols['body'], pts)
            pygame.draw.polygon(s, cols['glow'], pts, 1)
            pygame.draw.circle(s, cols['core'], (cx, cy), radius // 3)
        else:  # 默认圆形
            pygame.draw.circle(s, cols['body'], (cx, cy), radius)
            pygame.draw.circle(s, cols['glow'], (cx, cy), radius, 2)
            pygame.draw.circle(s, cols['core'], (cx, cy), radius * 2 // 5)
    
    # 3. 菱形 (Diamond) - 适用于: 冰晶, 虚空, 折纸
    elif shape == "diamond":
        w, h = size * 0.6, size * 0.4
        pts = [
            (cx, cy - h),       # Top
            (cx + w, cy),       # Right
            (cx, cy + h),       # Bottom
            (cx - w, cy),       # Left
        ]
        
        if style == "void":  # 虚空: 黑底+发光边脉冲
            pygame.draw.polygon(s, cols['body'], pts)
            glow_w = 2 + int(abs(math.sin(t * 0.1)) * 3)
            pygame.draw.polygon(s, cols['glow'], pts, glow_w)
            # 中心虚空
            pygame.draw.circle(s, (0, 0, 0), (cx, cy), size // 6)
        elif style == "flat":  # 折纸: 无边框纯色
            pygame.draw.polygon(s, cols['body'], pts)
            # 折痕线
            pygame.draw.line(s, cols['core'], pts[0], pts[2], 2)
            pygame.draw.line(s, (*cols['core'], 100), pts[1], pts[3], 1)
        elif style == "shard":  # 冰晶: 锐利多层
            pygame.draw.polygon(s, cols['body'], pts)
            pygame.draw.polygon(s, cols['glow'], pts, 2)
            # 内层冰晶
            inner_pts = [(cx, cy - h * 0.5), (cx + w * 0.5, cy), 
                        (cx, cy + h * 0.5), (cx - w * 0.5, cy)]
            pygame.draw.polygon(s, cols['core'], inner_pts)
        else:
            pygame.draw.polygon(s, cols['body'], pts)
            pygame.draw.polygon(s, cols['glow'], pts, 2)
    
    # 4. 六边形/齿轮 (Hexagon/Gear) - 适用于: 重装, 机械
    elif shape == "hexagon" or shape == "gear":
        sides = 6 if shape == "hexagon" else 8
        rad = size / 2.2
        pts = []
        for i in range(sides):
            angle = math.radians(i * (360 / sides) - 90)  # 从顶部开始
            px = cx + rad * math.cos(angle)
            py = cy + rad * math.sin(angle)
            pts.append((px, py))
        
        pygame.draw.polygon(s, cols['body'], pts)
        pygame.draw.polygon(s, cols['glow'], pts, 2)
        pygame.draw.circle(s, cols['core'], (cx, cy), int(rad * 0.4))
        
        if shape == "gear":  # 齿轮齿
            for p in pts:
                pygame.draw.circle(s, cols['glow'], (int(p[0]), int(p[1])), 3)
            # 齿轮孔
            pygame.draw.circle(s, cols['body'], (cx, cy), int(rad * 0.2))
    
    # --- 头部覆盖层 ---
    if is_head:
        _draw_head_overlay(s, cx, cy, size, t, skin)


def _draw_head_overlay(s, cx, cy, size, t, skin):
    """
    头部专属绘制：巨颚 + 发光眼
    """
    cols = skin['colors']
    style = skin['style']
    
    # 发光眼（根据风格调整颜色）
    if style == "void":
        eye_color = (100, 0, 100)
    elif style == "glitch":
        eye_color = (255, 0, 0) if random.random() > 0.5 else (0, 255, 255)
    else:
        eye_color = (255, 255, 255)
    
    # 主眼
    pygame.draw.circle(s, eye_color, (cx, cy), 4)
    pygame.draw.circle(s, (*cols['glow'], 150), (cx, cy), 6, 1)
    
    # 巨颚 (Mandibles) - 上下分体
    jaw_len = size * 0.6
    jaw_color = cols['glow']
    jaw_open = abs(math.sin(t * 0.08)) * 4 + 2  # 张合动画
    
    # 上颚
    pygame.draw.line(s, jaw_color, 
                    (cx + 8, cy - 3 - jaw_open), 
                    (cx + 8 + jaw_len, cy - 8 - jaw_open), 3)
    # 下颚
    pygame.draw.line(s, jaw_color, 
                    (cx + 8, cy + 3 + jaw_open), 
                    (cx + 8 + jaw_len, cy + 8 + jaw_open), 3)
    
    # 獠牙装饰
    fang_pts = [
        (cx + 8 + jaw_len, cy - 8 - jaw_open),
        (cx + 12 + jaw_len, cy - 2 - jaw_open),
        (cx + 6 + jaw_len, cy - 6 - jaw_open),
    ]
    pygame.draw.polygon(s, jaw_color, fang_pts)


# =============================================================================
#   蛇形身体绘制 - 分段式蠕虫结构
# =============================================================================

def _draw_worm_body(s, cx, cy, w, h, t, skin):
    """
    绘制完整的蠕虫式机体
    - 头部 + 5个身体节段 + 尾部
    - 节段间有磁力光束连接
    """
    cols = skin['colors']
    
    segment_count = 6
    base_size = min(w, h) * 0.35
    segment_spacing = h * 0.12
    
    # 存储各节段位置（用于绘制连接线）
    positions = []
    
    # 从头到尾绘制节段
    for i in range(segment_count):
        # 蛇形蠕动偏移
        wave_x = math.sin(t * 0.12 + i * 0.6) * (3 + i * 0.5)
        seg_y = cy - h * 0.3 + i * segment_spacing
        seg_x = cx + wave_x
        
        # 节段逐渐变小
        seg_size = base_size * (1.0 - i * 0.1)
        
        positions.append((seg_x, seg_y))
        
        # 绘制节段
        is_head = (i == 0)
        _draw_segment(s, int(seg_x), int(seg_y), seg_size, t, i, skin, is_head)
    
    # 绘制磁力光束连接
    for i in range(len(positions) - 1):
        x1, y1 = positions[i]
        x2, y2 = positions[i + 1]
        _draw_magnetic_link(s, x1, y1, x2, y2, t, i, cols)
    
    # 绘制尾部水晶刺
    tail_x, tail_y = positions[-1]
    _draw_tail_crystals(s, int(tail_x), int(tail_y + segment_spacing * 0.8), t, cols)
    
    # 绘制激光网格光翼
    head_x, head_y = positions[0]
    _draw_laser_wings(s, int(head_x), int(head_y), w, h, t, cols)
    
    # 绘制浮游炮
    _draw_floating_turrets(s, cx, cy, w, h, t, cols)


def _draw_magnetic_link(s, x1, y1, x2, y2, t, index, cols):
    """磁力光束连接"""
    # 主光束
    pygame.draw.line(s, (*cols['core'], 120), (int(x1), int(y1)), (int(x2), int(y2)), 2)
    
    # 能量脉冲
    pulse_pos = (t * 0.15 + index * 0.3) % 1.0
    px = int(x1 + (x2 - x1) * pulse_pos)
    py = int(y1 + (y2 - y1) * pulse_pos)
    pygame.draw.circle(s, cols['glow'], (px, py), 3)


def _draw_tail_crystals(s, cx, cy, t, cols):
    """尾部三枚浮游水晶刺"""
    crystal_offsets = [(0, 0), (-12, -5), (12, -5)]
    
    for i, (ox, oy) in enumerate(crystal_offsets):
        # 浮动动画
        float_y = math.sin(t * 0.15 + i * 2) * 3
        crx = cx + ox
        cry = cy + oy + float_y
        
        # 水晶形状
        pts = [
            (crx, cry - 6),
            (crx - 4, cry),
            (crx, cry + 8),
            (crx + 4, cry),
        ]
        pygame.draw.polygon(s, cols['core'], pts)
        pygame.draw.polygon(s, cols['glow'], pts, 1)
        
        # 残影
        for j in range(2):
            ghost_y = cry + 10 + j * 4
            pygame.draw.ellipse(s, (*cols['core'], 40 - j * 15),
                              (crx - 3, ghost_y, 6, 2))


def _draw_laser_wings(s, cx, cy, w, h, t, cols):
    """激光网格光翼"""
    grid_size = 8
    wing_w = int(w * 0.4)
    wing_h = int(h * 0.35)
    
    for side in [-1, 1]:
        wing_x = cx + side * int(w * 0.25)
        
        # 网格线
        breathe = 1.0 + 0.1 * math.sin(t * 0.1)
        actual_w = int(wing_w * breathe)
        
        # 横线
        for i in range(4):
            y_off = (i - 1.5) * grid_size
            line_y = int(cy + y_off)
            alpha = int(100 + 50 * math.sin(t * 0.15 + i * 0.5))
            col = cols['core'] if i % 2 == 0 else cols['glow']
            end_x = wing_x + side * actual_w
            pygame.draw.line(s, (*col, alpha), (wing_x, line_y), (end_x, line_y), 1)
        
        # 竖线
        for i in range(3):
            x_off = (i + 1) * grid_size * side
            line_x = wing_x + x_off
            alpha = int(80 + 60 * math.sin(t * 0.12 + i * 0.7))
            pygame.draw.line(s, (*cols['glow'], alpha),
                           (line_x, int(cy - wing_h * 0.4)),
                           (line_x, int(cy + wing_h * 0.4)), 1)


def _draw_floating_turrets(s, cx, cy, w, h, t, cols, count=4):
    """浮游炮"""
    orbit_radius = w * 0.42
    
    for i in range(count):
        angle = t * 0.08 + i * (2 * math.pi / count)
        tx = cx + math.cos(angle) * orbit_radius
        ty = cy + math.sin(angle) * orbit_radius * 0.4
        
        # 方形浮游单元
        size = 6
        rect = pygame.Rect(tx - size // 2, ty - size // 2, size, size)
        pygame.draw.rect(s, cols['body'], rect)
        pygame.draw.rect(s, cols['core'], rect, 1)
        pygame.draw.circle(s, cols['glow'], (int(tx), int(ty)), 2)
        
        # 能量链接
        pygame.draw.line(s, (*cols['core'], 40), (cx, cy), (int(tx), int(ty)), 1)


# =============================================================================
#   各涂装渲染函数
# =============================================================================

def _draw_oro_style(s, color, x, y, w, h, t, style_name):
    """通用涂装绘制"""
    skin = get_skin(style_name)
    _draw_worm_body(s, x + w // 2, y + h // 2, w, h, t, skin)


def _draw_oro_default(s, color, x, y, w, h, t):
    _draw_oro_style(s, color, x, y, w, h, t, "oro_default")

def _draw_oro_crimson(s, color, x, y, w, h, t):
    _draw_oro_style(s, color, x, y, w, h, t, "oro_crimson")

def _draw_oro_void(s, color, x, y, w, h, t):
    _draw_oro_style(s, color, x, y, w, h, t, "oro_void")

def _draw_oro_inferno(s, color, x, y, w, h, t):
    _draw_oro_style(s, color, x, y, w, h, t, "oro_inferno")

def _draw_oro_frost(s, color, x, y, w, h, t):
    _draw_oro_style(s, color, x, y, w, h, t, "oro_frost")

def _draw_oro_toxic(s, color, x, y, w, h, t):
    _draw_oro_style(s, color, x, y, w, h, t, "oro_toxic")

def _draw_oro_royal(s, color, x, y, w, h, t):
    _draw_oro_style(s, color, x, y, w, h, t, "oro_royal")

def _draw_oro_phantom(s, color, x, y, w, h, t):
    _draw_oro_style(s, color, x, y, w, h, t, "oro_phantom")

def _draw_oro_blood(s, color, x, y, w, h, t):
    _draw_oro_style(s, color, x, y, w, h, t, "oro_blood")

def _draw_oro_cosmic(s, color, x, y, w, h, t):
    _draw_oro_style(s, color, x, y, w, h, t, "oro_cosmic")

def _draw_oro_abyss(s, color, x, y, w, h, t):
    _draw_oro_style(s, color, x, y, w, h, t, "oro_abyss")

def _draw_oro_golden(s, color, x, y, w, h, t):
    _draw_oro_style(s, color, x, y, w, h, t, "oro_golden")


# =============================================================================
#   公共接口
# =============================================================================

def draw_oro(surface, color, x, y, w, h, frame=0, style="oro_default"):
    """绘制维度吞噬者·神杀"""
    renderers = {
        "oro_default": _draw_oro_default,
        "oro_crimson": _draw_oro_crimson,
        "oro_void": _draw_oro_void,
        "oro_inferno": _draw_oro_inferno,
        "oro_frost": _draw_oro_frost,
        "oro_toxic": _draw_oro_toxic,
        "oro_royal": _draw_oro_royal,
        "oro_phantom": _draw_oro_phantom,
        "oro_blood": _draw_oro_blood,
        "oro_cosmic": _draw_oro_cosmic,
        "oro_abyss": _draw_oro_abyss,
        "oro_golden": _draw_oro_golden,
    }
    draw_func = renderers.get(style, _draw_oro_default)
    draw_func(surface, color, x, y, w, h, frame)


def render_oro_skin(surface, color, model_style, t, pid, static):
    """渲染奥罗涂装入口"""
    if not is_oro_style(model_style):
        return None
    frame = int(t * 60) if not static else 0
    draw_oro(surface, color, 10, 10, 100, 100, frame, model_style)
    return surface
