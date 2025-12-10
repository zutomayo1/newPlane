# -*- coding: utf-8 -*-
"""
Truth 至尊·世界的真相 机体涂装渲染模块

设计理念：
- 核心元素：真言之眼（全知之眼）、黑白对立、金色真理
- 机体形态：眼睛为核心的对称设计，代表洞察万物
- 视觉效果：黑白双色流转、金色光芒闪耀、真言符文环绕
"""
import pygame
import math

# Truth 涂装样式列表
TRUTH_STYLES = [
    "truth_base",         # 基础形态 - 本源之眼
    "truth_enlightened",  # 开悟 - 智慧光芒
    "truth_shadow",       # 暗面 - 暗影真言
    "truth_balance",      # 完美平衡 - 太极形态
    "truth_cosmic",       # 宇宙视野 - 星云瞳孔
    "truth_revelation",   # 天启显现 - 神圣裁决
    "truth_judgment",     # 终极审判 - 审判之眼
    "truth_oracle",       # 预言者 - 神谕之眼
    "truth_infinity",     # 无限循环 - 永恒轮回
    "truth_absolute",     # 绝对真理 - 至高形态
]


def is_truth_style(model_style):
    """检查是否为 Truth 涂装样式"""
    return model_style in TRUTH_STYLES


def render_truth_skin(s, c, model_style, t, pid, static):
    """渲染 Truth 专属涂装"""
    if not is_truth_style(model_style):
        return None
    
    pulse = 0 if static else abs(math.sin(t * 3))
    
    if model_style == "truth_base":
        _render_truth_base(s, t, pulse)
    elif model_style == "truth_enlightened":
        render_truth_enlightened(s, t, pulse)
    elif model_style == "truth_shadow":
        render_truth_shadow(s, t, pulse)
    elif model_style == "truth_balance":
        render_truth_balance(s, t, pulse)
    elif model_style == "truth_cosmic":
        render_truth_cosmic(s, t, pulse)
    elif model_style == "truth_revelation":
        render_truth_revelation(s, t, pulse)
    elif model_style == "truth_judgment":
        render_truth_judgment(s, t, pulse)
    elif model_style == "truth_oracle":
        render_truth_oracle(s, t, pulse)
    elif model_style == "truth_infinity":
        render_truth_infinity(s, t, pulse)
    elif model_style == "truth_absolute":
        render_truth_absolute(s, t, pulse)
    else:
        _render_truth_base(s, t, pulse)
    
    return s


# 颜色定义
TRUTH_WHITE = (255, 255, 255)
TRUTH_BLACK = (20, 20, 30)
TRUTH_GOLD = (255, 215, 0)
TRUTH_SILVER = (200, 200, 210)
TRUTH_PURPLE = (150, 100, 200)


def _render_truth_base(surface, t, pulse, visual=None):
    """
    渲染Truth基础机体 - 真言之眼设计
    
    机体特征：
    - 中央巨大的全知之眼
    - 黑白双翼展开
    - 金色真言符文环绕
    """
    cx, cy = 60, 60  # 中心点
    
    # ========== 外层真言符文环 ==========
    rune_rotation = t * 30
    for i in range(12):
        angle = (i * 30 + rune_rotation) * math.pi / 180
        rx = cx + math.cos(angle) * 50
        ry = cy + math.sin(angle) * 50
        # 符文光点
        rune_size = 3 + int(2 * abs(math.sin(t * 3 + i * 0.5)))
        pygame.draw.circle(surface, TRUTH_GOLD, (int(rx), int(ry)), rune_size)
        # 符文连线
        if i % 2 == 0:
            next_i = (i + 2) % 12
            next_angle = (next_i * 30 + rune_rotation) * math.pi / 180
            nx = cx + math.cos(next_angle) * 50
            ny = cy + math.sin(next_angle) * 50
            pygame.draw.line(surface, (*TRUTH_GOLD, 150), (int(rx), int(ry)), (int(nx), int(ny)), 1)
    
    # ========== 黑白双翼 ==========
    # 左翼（白色）
    left_wing = [
        (cx - 10, cy - 5),
        (cx - 45, cy - 30),
        (cx - 50, cy - 15),
        (cx - 40, cy + 10),
        (cx - 15, cy + 5),
    ]
    pygame.draw.polygon(surface, TRUTH_WHITE, left_wing)
    pygame.draw.polygon(surface, TRUTH_SILVER, left_wing, 2)
    
    # 右翼（黑色）
    right_wing = [
        (cx + 10, cy - 5),
        (cx + 45, cy - 30),
        (cx + 50, cy - 15),
        (cx + 40, cy + 10),
        (cx + 15, cy + 5),
    ]
    pygame.draw.polygon(surface, TRUTH_BLACK, right_wing)
    pygame.draw.polygon(surface, TRUTH_SILVER, right_wing, 2)
    
    # 翼部纹理
    for i in range(3):
        # 左翼白色渐变线
        ly = cy - 20 + i * 10
        pygame.draw.line(surface, TRUTH_SILVER, (cx - 15, ly), (cx - 40 + i * 5, ly - 5), 1)
        # 右翼黑色渐变线
        pygame.draw.line(surface, TRUTH_GOLD, (cx + 15, ly), (cx + 40 - i * 5, ly - 5), 1)
    
    # ========== 机身主体 ==========
    # 太极形机身
    # 上半部分（白）
    pygame.draw.arc(surface, TRUTH_WHITE, (cx - 25, cy - 25, 50, 50), math.pi, 2 * math.pi, 15)
    # 下半部分（黑）
    pygame.draw.arc(surface, TRUTH_BLACK, (cx - 25, cy - 25, 50, 50), 0, math.pi, 15)
    
    # 太极小圆
    pygame.draw.circle(surface, TRUTH_BLACK, (cx, cy - 12), 6)
    pygame.draw.circle(surface, TRUTH_WHITE, (cx, cy + 12), 6)
    pygame.draw.circle(surface, TRUTH_WHITE, (cx, cy - 12), 2)
    pygame.draw.circle(surface, TRUTH_BLACK, (cx, cy + 12), 2)
    
    # ========== 中央全知之眼 ==========
    eye_size = 18 + int(3 * pulse)
    
    # 眼眶
    pygame.draw.ellipse(surface, TRUTH_GOLD, (cx - eye_size, cy - eye_size // 2, eye_size * 2, eye_size), 3)
    
    # 眼白
    pygame.draw.ellipse(surface, TRUTH_WHITE, (cx - eye_size + 3, cy - eye_size // 2 + 2, eye_size * 2 - 6, eye_size - 4))
    
    # 虹膜（渐变金色）
    iris_size = eye_size // 2
    pygame.draw.circle(surface, (200, 170, 50), (cx, cy), iris_size)
    pygame.draw.circle(surface, TRUTH_GOLD, (cx, cy), iris_size - 2)
    
    # 瞳孔
    pupil_size = iris_size // 2 + int(2 * abs(math.sin(t * 2)))
    pygame.draw.circle(surface, TRUTH_BLACK, (cx, cy), pupil_size)
    
    # 瞳孔内的真言符号（旋转）
    inner_rotation = t * 60
    for i in range(3):
        angle = (i * 120 + inner_rotation) * math.pi / 180
        ix = cx + math.cos(angle) * (pupil_size - 2)
        iy = cy + math.sin(angle) * (pupil_size - 2)
        pygame.draw.circle(surface, TRUTH_GOLD, (int(ix), int(iy)), 1)
    
    # 眼睛高光
    pygame.draw.circle(surface, TRUTH_WHITE, (cx - 4, cy - 3), 3)
    pygame.draw.circle(surface, TRUTH_WHITE, (cx + 2, cy + 2), 2)
    
    # ========== 底部推进器 ==========
    # 三角形推进器
    thruster_pts = [
        (cx, cy + 35),
        (cx - 12, cy + 50),
        (cx + 12, cy + 50),
    ]
    pygame.draw.polygon(surface, TRUTH_SILVER, thruster_pts)
    pygame.draw.polygon(surface, TRUTH_GOLD, thruster_pts, 2)
    
    # 推进器光焰
    flame_height = 10 + int(5 * pulse)
    flame_pts = [
        (cx - 8, cy + 50),
        (cx, cy + 50 + flame_height),
        (cx + 8, cy + 50),
    ]
    pygame.draw.polygon(surface, TRUTH_GOLD, flame_pts)
    
    # ========== 顶部装饰 ==========
    # 真理之冠
    crown_pts = [
        (cx - 15, cy - 35),
        (cx - 8, cy - 45),
        (cx, cy - 38),
        (cx + 8, cy - 45),
        (cx + 15, cy - 35),
    ]
    pygame.draw.lines(surface, TRUTH_GOLD, False, crown_pts, 2)
    # 冠顶宝石
    pygame.draw.circle(surface, TRUTH_GOLD, (cx, cy - 45), 4)
    pygame.draw.circle(surface, TRUTH_WHITE, (cx, cy - 45), 2)


def render_truth_enlightened(surface, t, pulse, visual=None):
    """
    启示涂装 - 光明版本
    全白色机体，金色光芒，代表被真理照亮
    """
    cx, cy = 60, 60
    
    # 光明光环
    for ring in range(4):
        ring_r = 45 - ring * 8 + int(5 * abs(math.sin(t * 2 + ring)))
        alpha = 200 - ring * 40
        pygame.draw.circle(surface, (*TRUTH_GOLD, alpha), (cx, cy), ring_r, 2)
    
    # 纯白双翼
    left_wing = [(cx - 10, cy), (cx - 50, cy - 25), (cx - 55, cy), (cx - 45, cy + 20), (cx - 15, cy + 5)]
    right_wing = [(cx + 10, cy), (cx + 50, cy - 25), (cx + 55, cy), (cx + 45, cy + 20), (cx + 15, cy + 5)]
    pygame.draw.polygon(surface, TRUTH_WHITE, left_wing)
    pygame.draw.polygon(surface, TRUTH_WHITE, right_wing)
    pygame.draw.polygon(surface, TRUTH_GOLD, left_wing, 2)
    pygame.draw.polygon(surface, TRUTH_GOLD, right_wing, 2)
    
    # 光芒放射
    for i in range(8):
        angle = (i * 45 + t * 20) * math.pi / 180
        length = 35 + int(10 * abs(math.sin(t * 3 + i)))
        ex = cx + math.cos(angle) * length
        ey = cy + math.sin(angle) * length
        pygame.draw.line(surface, TRUTH_GOLD, (cx, cy), (int(ex), int(ey)), 2)
    
    # 白色机身
    pygame.draw.circle(surface, TRUTH_WHITE, (cx, cy), 25)
    pygame.draw.circle(surface, TRUTH_GOLD, (cx, cy), 25, 3)
    
    # 金色全知之眼
    eye_size = 15 + int(3 * pulse)
    pygame.draw.ellipse(surface, TRUTH_GOLD, (cx - eye_size, cy - eye_size // 2, eye_size * 2, eye_size))
    pygame.draw.circle(surface, TRUTH_WHITE, (cx, cy), 8)
    pygame.draw.circle(surface, TRUTH_GOLD, (cx, cy), 4)
    pygame.draw.circle(surface, TRUTH_WHITE, (cx - 2, cy - 2), 2)


def render_truth_shadow(surface, t, pulse, visual=None):
    """
    暗影涂装 - 黑暗版本
    全黑色机体，紫金光芒，代表隐藏的真相
    """
    cx, cy = 60, 60
    
    # 暗影扭曲
    for ring in range(5):
        ring_r = 50 - ring * 8
        distort = 3 * math.sin(t * 4 + ring)
        pts = []
        for j in range(24):
            angle = (j * 15) * math.pi / 180
            r = ring_r + distort * math.sin(j * 0.5)
            pts.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
        pygame.draw.lines(surface, (50 + ring * 10, 0, 80 + ring * 15), True, pts, 1)
    
    # 黑色双翼（尖锐）
    left_wing = [(cx - 8, cy), (cx - 55, cy - 35), (cx - 50, cy + 5), (cx - 35, cy + 25), (cx - 12, cy + 5)]
    right_wing = [(cx + 8, cy), (cx + 55, cy - 35), (cx + 50, cy + 5), (cx + 35, cy + 25), (cx + 12, cy + 5)]
    pygame.draw.polygon(surface, TRUTH_BLACK, left_wing)
    pygame.draw.polygon(surface, TRUTH_BLACK, right_wing)
    pygame.draw.polygon(surface, TRUTH_PURPLE, left_wing, 2)
    pygame.draw.polygon(surface, TRUTH_PURPLE, right_wing, 2)
    
    # 黑色机身
    pygame.draw.circle(surface, TRUTH_BLACK, (cx, cy), 25)
    pygame.draw.circle(surface, TRUTH_PURPLE, (cx, cy), 25, 2)
    
    # 紫金之眼
    eye_size = 16 + int(4 * pulse)
    pygame.draw.ellipse(surface, TRUTH_PURPLE, (cx - eye_size, cy - eye_size // 2, eye_size * 2, eye_size), 2)
    pygame.draw.circle(surface, (80, 50, 120), (cx, cy), 10)
    pygame.draw.circle(surface, TRUTH_PURPLE, (cx, cy), 6)
    pygame.draw.circle(surface, TRUTH_GOLD, (cx, cy), 3)
    # 邪眼光芒
    for i in range(6):
        angle = (i * 60 + t * 40) * math.pi / 180
        pygame.draw.line(surface, TRUTH_PURPLE, (cx, cy), 
                        (cx + math.cos(angle) * 15, cy + math.sin(angle) * 15), 1)


def render_truth_balance(surface, t, pulse, visual=None):
    """
    平衡涂装 - 太极版本
    黑白完美对称，代表真假平衡
    """
    cx, cy = 60, 60
    
    # 太极符号旋转
    rotation = t * 45
    
    # 外圈
    pygame.draw.circle(surface, TRUTH_SILVER, (cx, cy), 45, 3)
    
    # 太极双鱼
    for i in range(2):
        color = TRUTH_WHITE if i == 0 else TRUTH_BLACK
        start_angle = rotation + i * 180
        
        # 大弧
        pygame.draw.arc(surface, color, (cx - 40, cy - 40, 80, 80), 
                       (start_angle) * math.pi / 180, (start_angle + 180) * math.pi / 180, 20)
        
        # 小圆
        small_angle = (start_angle + 90) * math.pi / 180
        sx = cx + math.cos(small_angle) * 20
        sy = cy + math.sin(small_angle) * 20
        pygame.draw.circle(surface, color, (int(sx), int(sy)), 20)
        
        # 鱼眼
        eye_color = TRUTH_BLACK if i == 0 else TRUTH_WHITE
        pygame.draw.circle(surface, eye_color, (int(sx), int(sy)), 6)
    
    # 中央之眼
    eye_size = 12 + int(2 * pulse)
    pygame.draw.circle(surface, TRUTH_GOLD, (cx, cy), eye_size)
    pygame.draw.circle(surface, TRUTH_BLACK, (cx, cy), eye_size - 3)
    pygame.draw.circle(surface, TRUTH_GOLD, (cx, cy), 4)
    pygame.draw.circle(surface, TRUTH_WHITE, (cx - 2, cy - 2), 2)


def render_truth_cosmic(surface, t, pulse, visual=None):
    """
    宇宙涂装 - 星空版本
    星空背景，金色星座连线，代表宇宙真理
    """
    cx, cy = 60, 60
    
    # 星空背景圆
    pygame.draw.circle(surface, (10, 10, 30), (cx, cy), 50)
    
    # 随机星星
    import random
    random.seed(42)  # 固定种子确保星星位置一致
    for _ in range(30):
        sx = cx + random.randint(-45, 45)
        sy = cy + random.randint(-45, 45)
        if math.hypot(sx - cx, sy - cy) < 45:
            twinkle = abs(math.sin(t * 3 + sx + sy))
            size = 1 + int(twinkle * 2)
            pygame.draw.circle(surface, TRUTH_WHITE, (sx, sy), size)
    
    # 星座连线（眼睛形状）
    constellation = [
        (cx - 30, cy - 5), (cx - 20, cy - 15), (cx - 10, cy - 10),
        (cx, cy - 5), (cx + 10, cy - 10), (cx + 20, cy - 15), (cx + 30, cy - 5),
        (cx + 20, cy + 5), (cx + 10, cy), (cx, cy - 5), (cx - 10, cy), 
        (cx - 20, cy + 5), (cx - 30, cy - 5)
    ]
    pygame.draw.lines(surface, TRUTH_GOLD, False, constellation, 2)
    for pt in constellation:
        pygame.draw.circle(surface, TRUTH_GOLD, pt, 3)
    
    # 中央之眼
    pygame.draw.circle(surface, (30, 30, 80), (cx, cy), 15)
    pygame.draw.circle(surface, TRUTH_PURPLE, (cx, cy), 12)
    pygame.draw.circle(surface, TRUTH_GOLD, (cx, cy), 6)
    pygame.draw.circle(surface, TRUTH_WHITE, (cx - 2, cy - 2), 2)
    
    # 翼展示（简化）
    pygame.draw.line(surface, TRUTH_GOLD, (cx - 50, cy), (cx - 15, cy - 5), 2)
    pygame.draw.line(surface, TRUTH_GOLD, (cx + 50, cy), (cx + 15, cy - 5), 2)


def render_truth_revelation(surface, t, pulse, visual=None):
    """
    天启涂装 - 神圣版本
    金白神圣光芒，天使羽翼，代表神圣启示
    """
    cx, cy = 60, 60
    
    # 神圣光轮
    for ring in range(3):
        ring_r = 48 - ring * 12 + int(3 * abs(math.sin(t * 2 + ring)))
        pygame.draw.circle(surface, TRUTH_GOLD, (cx, cy), ring_r, 2)
    
    # 天使羽翼（多层）
    for layer in range(3):
        offset = layer * 8
        left_feather = [
            (cx - 12 - offset, cy),
            (cx - 35 - offset, cy - 20 - layer * 5),
            (cx - 30 - offset, cy + 10),
        ]
        right_feather = [
            (cx + 12 + offset, cy),
            (cx + 35 + offset, cy - 20 - layer * 5),
            (cx + 30 + offset, cy + 10),
        ]
        color = (255, 255, 255 - layer * 30)
        pygame.draw.polygon(surface, color, left_feather)
        pygame.draw.polygon(surface, color, right_feather)
    
    # 金色机身
    pygame.draw.circle(surface, TRUTH_WHITE, (cx, cy), 22)
    pygame.draw.circle(surface, TRUTH_GOLD, (cx, cy), 22, 3)
    
    # 神圣之眼
    eye_size = 14 + int(3 * pulse)
    pygame.draw.ellipse(surface, TRUTH_GOLD, (cx - eye_size, cy - eye_size // 2, eye_size * 2, eye_size))
    pygame.draw.circle(surface, TRUTH_WHITE, (cx, cy), 8)
    pygame.draw.circle(surface, TRUTH_GOLD, (cx, cy), 5)
    
    # 十字光芒
    cross_len = 20 + int(5 * pulse)
    pygame.draw.line(surface, TRUTH_GOLD, (cx, cy - cross_len), (cx, cy + cross_len), 3)
    pygame.draw.line(surface, TRUTH_GOLD, (cx - cross_len, cy), (cx + cross_len, cy), 3)


def render_truth_judgment(surface, t, pulse, visual=None):
    """
    审判涂装 - 末日版本
    黑金审判天平，代表最终裁决
    """
    cx, cy = 60, 60
    
    # 审判光环
    pygame.draw.circle(surface, TRUTH_BLACK, (cx, cy), 48)
    pygame.draw.circle(surface, TRUTH_GOLD, (cx, cy), 48, 3)
    
    # 天平
    # 横梁
    balance_angle = 5 * math.sin(t * 2)
    beam_left = (cx - 35, cy - 10 + balance_angle)
    beam_right = (cx + 35, cy - 10 - balance_angle)
    pygame.draw.line(surface, TRUTH_GOLD, beam_left, beam_right, 3)
    
    # 支点
    pygame.draw.line(surface, TRUTH_GOLD, (cx, cy - 25), (cx, cy - 10), 3)
    pygame.draw.circle(surface, TRUTH_GOLD, (cx, cy - 25), 5)
    
    # 左盘（白）
    pygame.draw.line(surface, TRUTH_SILVER, beam_left, (beam_left[0], beam_left[1] + 15), 1)
    pygame.draw.circle(surface, TRUTH_WHITE, (int(beam_left[0]), int(beam_left[1] + 20)), 12)
    
    # 右盘（黑）
    pygame.draw.line(surface, TRUTH_SILVER, beam_right, (beam_right[0], beam_right[1] + 15), 1)
    pygame.draw.circle(surface, TRUTH_BLACK, (int(beam_right[0]), int(beam_right[1] + 20)), 12)
    pygame.draw.circle(surface, TRUTH_GOLD, (int(beam_right[0]), int(beam_right[1] + 20)), 12, 1)
    
    # 中央审判之眼
    eye_size = 15 + int(3 * pulse)
    pygame.draw.ellipse(surface, TRUTH_GOLD, (cx - eye_size, cy + 5 - eye_size // 2, eye_size * 2, eye_size))
    pygame.draw.circle(surface, TRUTH_BLACK, (cx, cy + 5), 8)
    pygame.draw.circle(surface, TRUTH_GOLD, (cx, cy + 5), 4)


def render_truth_oracle(surface, t, pulse, visual=None):
    """
    神谕涂装 - 预言版本
    水晶球与星光，代表预知未来
    """
    cx, cy = 60, 60
    
    # 神谕光环
    for i in range(6):
        angle = (i * 60 + t * 30) * math.pi / 180
        ox = cx + math.cos(angle) * 45
        oy = cy + math.sin(angle) * 45
        pygame.draw.circle(surface, TRUTH_PURPLE, (int(ox), int(oy)), 5)
        pygame.draw.line(surface, (*TRUTH_PURPLE, 150), (cx, cy), (int(ox), int(oy)), 1)
    
    # 翼（水晶质感）
    left_crystal = [(cx - 10, cy), (cx - 40, cy - 25), (cx - 35, cy), (cx - 40, cy + 20), (cx - 10, cy + 5)]
    right_crystal = [(cx + 10, cy), (cx + 40, cy - 25), (cx + 35, cy), (cx + 40, cy + 20), (cx + 10, cy + 5)]
    pygame.draw.polygon(surface, (180, 150, 220), left_crystal)
    pygame.draw.polygon(surface, (180, 150, 220), right_crystal)
    pygame.draw.polygon(surface, TRUTH_PURPLE, left_crystal, 2)
    pygame.draw.polygon(surface, TRUTH_PURPLE, right_crystal, 2)
    
    # 水晶球主体
    pygame.draw.circle(surface, (100, 80, 150), (cx, cy), 25)
    pygame.draw.circle(surface, (150, 120, 200), (cx, cy), 22)
    pygame.draw.circle(surface, TRUTH_PURPLE, (cx, cy), 25, 2)
    
    # 球内星光
    for i in range(5):
        angle = (i * 72 + t * 50) * math.pi / 180
        dist = 12 + int(5 * abs(math.sin(t * 3 + i)))
        sx = cx + math.cos(angle) * dist
        sy = cy + math.sin(angle) * dist
        pygame.draw.circle(surface, TRUTH_WHITE, (int(sx), int(sy)), 2)
    
    # 核心之眼
    pygame.draw.circle(surface, TRUTH_GOLD, (cx, cy), 8)
    pygame.draw.circle(surface, TRUTH_BLACK, (cx, cy), 4)
    pygame.draw.circle(surface, TRUTH_WHITE, (cx - 1, cy - 1), 1)


def render_truth_infinity(surface, t, pulse, visual=None):
    """
    无限涂装 - 永恒版本
    无限符号与金光，代表永恒真理
    """
    cx, cy = 60, 60
    
    # 无限符号
    infinity_pts = []
    for i in range(60):
        angle = i * 6 * math.pi / 180
        # 8字形参数方程
        x = 35 * math.cos(angle) / (1 + math.sin(angle) ** 2)
        y = 35 * math.sin(angle) * math.cos(angle) / (1 + math.sin(angle) ** 2)
        infinity_pts.append((cx + x, cy + y))
    
    pygame.draw.lines(surface, TRUTH_GOLD, True, infinity_pts, 4)
    
    # 双眼位置
    eye_offsets = [(-18, 0), (18, 0)]
    for ox, oy in eye_offsets:
        ex, ey = cx + ox, cy + oy
        pygame.draw.circle(surface, TRUTH_WHITE, (ex, ey), 12)
        pygame.draw.circle(surface, TRUTH_GOLD, (ex, ey), 12, 2)
        pygame.draw.circle(surface, TRUTH_GOLD, (ex, ey), 6)
        pygame.draw.circle(surface, TRUTH_BLACK, (ex, ey), 3)
    
    # 连接光带
    pygame.draw.line(surface, TRUTH_GOLD, (cx - 18, cy), (cx + 18, cy), 2)
    
    # 简化翼
    pygame.draw.line(surface, TRUTH_SILVER, (cx - 50, cy - 15), (cx - 20, cy), 3)
    pygame.draw.line(surface, TRUTH_SILVER, (cx + 50, cy - 15), (cx + 20, cy), 3)


def render_truth_absolute(surface, t, pulse, visual=None):
    """
    绝对涂装 - 究极版本
    融合所有元素的最终形态
    """
    cx, cy = 60, 60
    
    # 多层光环
    for ring in range(5):
        ring_r = 50 - ring * 8
        rotation = t * (30 + ring * 10) * (1 if ring % 2 == 0 else -1)
        pts = []
        for j in range(6):
            angle = (j * 60 + rotation) * math.pi / 180
            pts.append((cx + math.cos(angle) * ring_r, cy + math.sin(angle) * ring_r))
        colors = [TRUTH_GOLD, TRUTH_WHITE, TRUTH_PURPLE, TRUTH_SILVER, TRUTH_GOLD]
        pygame.draw.polygon(surface, colors[ring], pts, 2)
    
    # 复杂双翼
    for i, side in enumerate([-1, 1]):
        wing_pts = [
            (cx + side * 10, cy - 5),
            (cx + side * 55, cy - 30),
            (cx + side * 50, cy - 10),
            (cx + side * 55, cy + 10),
            (cx + side * 40, cy + 25),
            (cx + side * 15, cy + 10),
        ]
        color = TRUTH_WHITE if i == 0 else TRUTH_BLACK
        pygame.draw.polygon(surface, color, wing_pts)
        pygame.draw.polygon(surface, TRUTH_GOLD, wing_pts, 2)
    
    # 究极之眼
    eye_size = 20 + int(5 * pulse)
    
    # 眼眶（多层）
    for layer in range(3):
        pygame.draw.ellipse(surface, TRUTH_GOLD, 
                          (cx - eye_size + layer * 2, cy - eye_size // 2 + layer, 
                           (eye_size - layer * 2) * 2, eye_size - layer * 2), 2)
    
    # 眼白
    pygame.draw.ellipse(surface, TRUTH_WHITE, 
                       (cx - eye_size + 6, cy - eye_size // 2 + 3, eye_size * 2 - 12, eye_size - 6))
    
    # 虹膜
    pygame.draw.circle(surface, TRUTH_GOLD, (cx, cy), 10)
    
    # 复杂瞳孔
    pygame.draw.circle(surface, TRUTH_BLACK, (cx, cy), 6)
    # 瞳孔内旋转星芒
    for i in range(8):
        angle = (i * 45 + t * 100) * math.pi / 180
        ix = cx + math.cos(angle) * 4
        iy = cy + math.sin(angle) * 4
        pygame.draw.line(surface, TRUTH_GOLD, (cx, cy), (int(ix), int(iy)), 1)
    
    # 高光
    pygame.draw.circle(surface, TRUTH_WHITE, (cx - 3, cy - 2), 3)


__all__ = ['render_truth_skin', 'is_truth_style', 'TRUTH_STYLES', '_render_truth_base']
