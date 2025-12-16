# -*- coding: utf-8 -*-
"""
终噬星链·奥罗 (Deus-Eater · ORO)
TYPE-VOID "神明吞噬者"

设计理念：维度穿梭型 · 分段式蠕虫战舰
视觉关键词：赛博蠕虫、虚空紫、激光网格、浮游装甲

12款异质化涂装 - 每个涂装独立绘制函数
"""
import pygame
import math
import random

# =============================================================================
#   12款皮肤主题配置
# =============================================================================

ORO_THEMES = {
    # ================= [系列一：传说重现] =================
    "oro_default": {
        "name": "宇宙吞噬者·原初",
        "body": (20, 20, 35),          # 深空蓝黑
        "armor": (40, 35, 60),         # 暗紫装甲
        "core": (148, 0, 211),         # 紫罗兰核心
        "glow": (0, 255, 255),         # 青色光芒
        "energy": (180, 100, 255),     # 能量紫
        "accent": (255, 100, 255),     # 品红强调
    },
    "oro_phantom": {
        "name": "星神游龙·幽灵",
        "body": (30, 30, 50),          # 幽灵蓝
        "armor": (60, 60, 90),         # 半透明甲
        "core": (100, 149, 237),       # 矢车菊蓝
        "glow": (200, 220, 255),       # 幽光白
        "energy": (150, 180, 255),     # 灵魂蓝
        "accent": (255, 255, 255),     # 纯白
    },
    "oro_golden": {
        "name": "弑神装甲·重装",
        "body": (45, 40, 35),          # 青铜底
        "armor": (80, 70, 50),         # 重甲
        "core": (255, 215, 0),         # 黄金
        "glow": (255, 140, 0),         # 橙焰
        "energy": (255, 180, 50),      # 金能量
        "accent": (255, 100, 50),      # 熔金
    },

    # ================= [系列二：元素反转] =================
    "oro_inferno": {
        "name": "狱炎长虫·熔岩",
        "body": (60, 20, 10),          # 岩浆黑
        "armor": (120, 40, 20),        # 熔岩红
        "core": (255, 140, 0),         # 熔岩橙
        "glow": (255, 220, 100),       # 火焰黄
        "energy": (255, 80, 30),       # 炽焰
        "accent": (255, 255, 150),     # 白热
    },
    "oro_frost": {
        "name": "极地灾厄·冰晶",
        "body": (200, 230, 255),       # 冰蓝
        "armor": (150, 200, 240),      # 霜甲
        "core": (100, 200, 255),       # 寒冰核
        "glow": (220, 240, 255),       # 霜光
        "energy": (180, 230, 255),     # 冰能量
        "accent": (255, 255, 255),     # 雪白
    },
    "oro_toxic": {
        "name": "生化危机·辐射",
        "body": (30, 40, 20),          # 毒沼绿
        "armor": (60, 80, 30),         # 辐射甲
        "core": (100, 255, 50),        # 辐射绿
        "glow": (180, 255, 100),       # 毒光
        "energy": (150, 255, 80),      # 毒能量
        "accent": (255, 255, 100),     # 警示黄
    },

    # ================= [系列三：概念重构] =================
    "oro_cosmic": {
        "name": "矩阵代码·黑客",
        "body": (5, 10, 5),            # 纯黑
        "armor": (10, 30, 10),         # 暗绿
        "core": (0, 255, 100),         # 矩阵绿
        "glow": (100, 255, 150),       # 代码光
        "energy": (0, 200, 80),        # 数据流
        "accent": (200, 255, 200),     # 亮绿
    },
    "oro_royal": {
        "name": "水墨游龙·写意",
        "body": (15, 15, 20),          # 墨黑
        "armor": (40, 40, 50),         # 淡墨
        "core": (255, 255, 255),       # 留白
        "glow": (180, 180, 190),       # 墨晕
        "energy": (120, 120, 130),     # 浓墨
        "accent": (200, 50, 50),       # 朱砂
    },
    "oro_crimson": {
        "name": "折纸大蛇·维度",
        "body": (255, 250, 240),       # 和纸白
        "armor": (245, 235, 220),      # 折纸色
        "core": (220, 50, 80),         # 朱红
        "glow": (200, 100, 120),       # 樱粉
        "energy": (180, 80, 100),      # 折痕
        "accent": (100, 80, 60),       # 墨线
    },

    # ================= [系列四：终极幻想] =================
    "oro_void": {
        "name": "视界线·虚空",
        "body": (5, 0, 10),            # 虚空黑
        "armor": (20, 10, 30),         # 暗物质
        "core": (100, 0, 150),         # 虚空紫
        "glow": (150, 50, 200),        # 视界光
        "energy": (180, 80, 255),      # 奇点能
        "accent": (255, 150, 255),     # 湮灭粉
    },
    "oro_abyss": {
        "name": "机械降神·齿轮",
        "body": (50, 40, 30),          # 黄铜
        "armor": (100, 80, 50),        # 齿轮铜
        "core": (0, 220, 220),         # 蒸汽蓝
        "glow": (220, 180, 100),       # 黄铜光
        "energy": (180, 220, 255),     # 蒸汽
        "accent": (255, 200, 100),     # 火花
    },
    "oro_blood": {
        "name": "数据删除·终焉",
        "body": (250, 250, 250),       # 故障白
        "armor": (220, 220, 230),      # 噪点灰
        "core": (255, 30, 30),         # 错误红
        "glow": (255, 100, 100),       # 警告光
        "energy": (255, 0, 100),       # 崩溃粉
        "accent": (0, 255, 255),       # 青色闪烁
    },
}

ORO_STYLES = list(ORO_THEMES.keys())


def is_oro_style(style):
    """检查是否为奥罗涂装"""
    return style in ORO_STYLES


def get_oro_theme(style):
    """获取涂装主题"""
    return ORO_THEMES.get(style, ORO_THEMES["oro_default"])


# =============================================================================
#   [系列一：传说重现] - 精细化独立绘制函数
# =============================================================================

def draw_oro_default(s, cx, cy, w, h, t):
    """
    宇宙吞噬者·原初 - 深空赛博蠕虫
    特点：标准六节段蠕虫 + 紫罗兰能量核心 + 青色激光网格翼
    """
    theme = get_oro_theme("oro_default")
    seg_count = 6
    base_size = min(w, h) * 0.36
    spacing = h * 0.12
    positions = []
    
    # === 绘制蠕虫身体节段 ===
    for i in range(seg_count):
        wave = math.sin(t * 0.1 + i * 0.5) * (4 + i * 0.8)
        seg_y = cy - h * 0.28 + i * spacing
        seg_x = cx + wave
        seg_size = base_size * (1.0 - i * 0.08)
        positions.append((seg_x, seg_y, seg_size))
        
        # 外层装甲 - 矩形装甲板
        armor_w = int(seg_size * 1.1)
        armor_h = int(seg_size * 0.65)
        armor_rect = pygame.Rect(seg_x - armor_w//2, seg_y - armor_h//2, armor_w, armor_h)
        
        # 装甲底色 + 渐变边缘
        pygame.draw.rect(s, theme["body"], armor_rect, border_radius=4)
        pygame.draw.rect(s, theme["armor"], armor_rect, 2, border_radius=4)
        
        # 装甲纹理线
        for j in range(3):
            line_x = seg_x - armor_w//2 + (j+1) * armor_w//4
            pygame.draw.line(s, (*theme["armor"], 100), 
                           (line_x, seg_y - armor_h//2 + 3),
                           (line_x, seg_y + armor_h//2 - 3), 1)
        
        # 内核能量槽 - 紫罗兰核心
        core_w = int(armor_w * 0.5)
        core_h = int(armor_h * 0.4)
        core_rect = pygame.Rect(seg_x - core_w//2, seg_y - core_h//2, core_w, core_h)
        
        # 核心脉动
        pulse = 0.7 + 0.3 * math.sin(t * 0.15 + i * 0.4)
        core_color = tuple(int(c * pulse) for c in theme["core"])
        pygame.draw.rect(s, core_color, core_rect, border_radius=2)
        
        # 核心发光边缘
        glow_alpha = int(100 + 50 * math.sin(t * 0.12 + i * 0.3))
        pygame.draw.rect(s, (*theme["glow"], glow_alpha), core_rect.inflate(4, 4), 1, border_radius=3)
        
        # 装甲铆钉
        for corner in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            rivet_x = seg_x + corner[0] * (armor_w//2 - 5)
            rivet_y = seg_y + corner[1] * (armor_h//2 - 4)
            pygame.draw.circle(s, theme["energy"], (int(rivet_x), int(rivet_y)), 2)
        
        # 头部特殊处理
        if i == 0:
            _draw_default_head(s, seg_x, seg_y, seg_size, t, theme)
    
    # === 磁力连接光束 ===
    for i in range(len(positions) - 1):
        x1, y1, _ = positions[i]
        x2, y2, _ = positions[i + 1]
        
        # 双线能量链接
        pygame.draw.line(s, (*theme["core"], 80), (int(x1-3), int(y1)), (int(x2-3), int(y2)), 2)
        pygame.draw.line(s, (*theme["core"], 80), (int(x1+3), int(y1)), (int(x2+3), int(y2)), 2)
        
        # 能量脉冲球
        pulse_t = (t * 0.2 + i * 0.4) % 1.0
        px = int(x1 + (x2 - x1) * pulse_t)
        py = int(y1 + (y2 - y1) * pulse_t)
        pygame.draw.circle(s, theme["glow"], (px, py), 4)
        pygame.draw.circle(s, (*theme["energy"], 100), (px, py), 6, 1)
    
    # === 尾部水晶刺 ===
    tail_x, tail_y, _ = positions[-1]
    _draw_default_tail(s, tail_x, tail_y + spacing * 0.7, t, theme)
    
    # === 激光网格翼 ===
    head_x, head_y, _ = positions[0]
    _draw_default_wings(s, head_x, head_y, w, h, t, theme)
    
    # === 浮游炮 ===
    _draw_default_turrets(s, cx, cy, w, h, t, theme)


def _draw_default_head(s, cx, cy, size, t, theme):
    """原初涂装 - 头部：复眼 + 双颚"""
    # 主复眼 - 三眼阵列
    for offset in [-8, 0, 8]:
        eye_y = cy + offset * 0.4
        eye_size = 4 if offset == 0 else 3
        # 眼底
        pygame.draw.circle(s, (0, 0, 0), (int(cx), int(eye_y)), eye_size + 1)
        # 眼球
        pygame.draw.circle(s, theme["glow"], (int(cx), int(eye_y)), eye_size)
        # 瞳孔
        pygame.draw.circle(s, (255, 255, 255), (int(cx + 1), int(eye_y - 1)), 1)
    
    # 巨颚 - 机械钳形
    jaw_open = 3 + abs(math.sin(t * 0.1)) * 5
    jaw_len = size * 0.55
    
    for side in [-1, 1]:
        # 颚基座
        base_y = cy + side * (5 + jaw_open)
        pygame.draw.ellipse(s, theme["armor"],
                          (cx + 5, base_y - 3, 8, 6))
        
        # 颚臂
        end_x = cx + 8 + jaw_len
        end_y = base_y + side * 4
        pygame.draw.line(s, theme["glow"], (cx + 10, base_y), (end_x, end_y), 3)
        
        # 颚尖锯齿
        for j in range(3):
            tooth_x = cx + 15 + j * 8
            tooth_y = base_y + side * (2 + j * 0.5)
            pts = [(tooth_x, tooth_y), 
                   (tooth_x + 4, tooth_y + side * 5),
                   (tooth_x + 6, tooth_y)]
            pygame.draw.polygon(s, theme["accent"], pts)
    
    # 额角
    for side in [-1, 1]:
        horn_pts = [
            (cx - 5, cy + side * 10),
            (cx - 15, cy + side * 18),
            (cx - 8, cy + side * 12)
        ]
        pygame.draw.polygon(s, theme["energy"], horn_pts)


def _draw_default_tail(s, cx, cy, t, theme):
    """原初涂装 - 尾部：三叉水晶"""
    offsets = [(0, 0), (-14, -8), (14, -8)]
    
    for idx, (ox, oy) in enumerate(offsets):
        float_y = math.sin(t * 0.12 + idx * 2.1) * 4
        crx, cry = cx + ox, cy + oy + float_y
        
        # 水晶主体
        crystal_h = 12 if idx == 0 else 9
        pts = [
            (crx, cry - crystal_h),
            (crx - 5, cry - 2),
            (crx - 3, cry + crystal_h),
            (crx + 3, cry + crystal_h),
            (crx + 5, cry - 2)
        ]
        pygame.draw.polygon(s, theme["core"], pts)
        pygame.draw.polygon(s, theme["glow"], pts, 1)
        
        # 内部折射线
        pygame.draw.line(s, (*theme["glow"], 150), 
                        (crx - 2, cry - crystal_h + 3),
                        (crx - 1, cry + crystal_h - 3), 1)
        
        # 能量残影
        for j in range(3):
            ghost_y = cry + crystal_h + 4 + j * 3
            alpha = 60 - j * 20
            pygame.draw.ellipse(s, (*theme["core"], alpha),
                              (crx - 4, ghost_y, 8, 3))


def _draw_default_wings(s, cx, cy, w, h, t, theme):
    """原初涂装 - 激光网格翼"""
    wing_w = int(w * 0.38)
    wing_h = int(h * 0.32)
    grid = 10
    
    for side in [-1, 1]:
        base_x = cx + side * int(w * 0.22)
        breathe = 1.0 + 0.08 * math.sin(t * 0.08)
        actual_w = int(wing_w * breathe)
        
        # 外框
        frame_pts = [
            (base_x, cy - wing_h//2),
            (base_x + side * actual_w, cy - wing_h//3),
            (base_x + side * actual_w, cy + wing_h//3),
            (base_x, cy + wing_h//2)
        ]
        pygame.draw.polygon(s, (*theme["core"], 30), frame_pts)
        pygame.draw.polygon(s, (*theme["glow"], 100), frame_pts, 1)
        
        # 横向网格线
        for i in range(5):
            y_pos = cy - wing_h//2 + (i + 0.5) * wing_h // 5
            alpha = int(80 + 40 * math.sin(t * 0.1 + i * 0.4))
            pygame.draw.line(s, (*theme["glow"], alpha),
                           (base_x, int(y_pos)),
                           (base_x + side * actual_w * 0.9, int(y_pos)), 1)
        
        # 纵向网格线
        for i in range(4):
            x_off = (i + 1) * actual_w // 5
            line_x = base_x + side * x_off
            alpha = int(60 + 50 * math.sin(t * 0.12 + i * 0.6))
            pygame.draw.line(s, (*theme["core"], alpha),
                           (int(line_x), cy - wing_h//2 + 5),
                           (int(line_x), cy + wing_h//2 - 5), 1)
        
        # 能量节点
        for i in range(3):
            node_x = base_x + side * (i + 1) * actual_w // 4
            node_y = cy + math.sin(t * 0.15 + i) * 5
            pygame.draw.circle(s, theme["glow"], (int(node_x), int(node_y)), 3)
            pygame.draw.circle(s, (*theme["core"], 80), (int(node_x), int(node_y)), 5, 1)


def _draw_default_turrets(s, cx, cy, w, h, t, theme):
    """原初涂装 - 四基浮游炮"""
    orbit_r = w * 0.4
    
    for i in range(4):
        angle = t * 0.06 + i * math.pi / 2
        tx = cx + math.cos(angle) * orbit_r
        ty = cy + math.sin(angle) * orbit_r * 0.45
        
        # 浮游炮主体
        turret_size = 8
        pygame.draw.rect(s, theme["body"],
                        (tx - turret_size//2, ty - turret_size//2, turret_size, turret_size),
                        border_radius=2)
        pygame.draw.rect(s, theme["core"],
                        (tx - turret_size//2, ty - turret_size//2, turret_size, turret_size),
                        1, border_radius=2)
        
        # 炮口
        pygame.draw.circle(s, theme["glow"], (int(tx), int(ty)), 3)
        
        # 能量链接线
        pygame.draw.line(s, (*theme["core"], 50), (int(cx), int(cy)), (int(tx), int(ty)), 1)


def draw_oro_phantom(s, cx, cy, w, h, t):
    """
    星神游龙·幽灵 - 半透明灵体蠕虫
    特点：圆形半透明节段 + 多层光晕 + 幽灵残影 + 灵魂之翼
    """
    theme = get_oro_theme("oro_phantom")
    seg_count = 7  # 更长的灵体
    base_size = min(w, h) * 0.32
    spacing = h * 0.11
    positions = []
    
    # 先绘制残影层（在主体后面）
    for layer in range(3, 0, -1):
        alpha_mult = 0.2 / layer
        offset_t = t - layer * 3
        for i in range(seg_count):
            wave = math.sin(offset_t * 0.08 + i * 0.4) * (5 + i * 0.6)
            seg_y = cy - h * 0.32 + i * spacing
            seg_x = cx + wave
            radius = int(base_size * (1.0 - i * 0.07) * 0.45)
            
            alpha = int(30 * alpha_mult)
            pygame.draw.circle(s, (*theme["glow"], alpha), (int(seg_x), int(seg_y)), radius + layer * 3)
    
    # === 绘制主体节段 ===
    for i in range(seg_count):
        wave = math.sin(t * 0.08 + i * 0.4) * (5 + i * 0.6)
        seg_y = cy - h * 0.32 + i * spacing
        seg_x = cx + wave
        radius = int(base_size * (1.0 - i * 0.07) * 0.45)
        positions.append((seg_x, seg_y, radius))
        
        # 多层幽灵光晕
        for glow_layer in range(4, 0, -1):
            glow_r = radius + glow_layer * 4
            glow_alpha = 25 - glow_layer * 5
            pygame.draw.circle(s, (*theme["glow"], glow_alpha), (int(seg_x), int(seg_y)), glow_r)
        
        # 半透明外壳
        pygame.draw.circle(s, (*theme["body"], 80), (int(seg_x), int(seg_y)), radius)
        pygame.draw.circle(s, (*theme["armor"], 120), (int(seg_x), int(seg_y)), radius, 2)
        
        # 内核 - 更亮的灵魂核心
        core_r = int(radius * 0.5)
        core_pulse = 0.6 + 0.4 * math.sin(t * 0.12 + i * 0.5)
        pygame.draw.circle(s, (*theme["core"], int(180 * core_pulse)), (int(seg_x), int(seg_y)), core_r)
        
        # 内核高光
        highlight_x = seg_x - core_r * 0.3
        highlight_y = seg_y - core_r * 0.3
        pygame.draw.circle(s, (*theme["accent"], 150), (int(highlight_x), int(highlight_y)), max(2, core_r // 3))
        
        # 幽灵纹路 - 漩涡状
        for j in range(3):
            swirl_angle = t * 0.1 + j * 2.1 + i * 0.3
            swirl_r = radius * 0.7
            sx = seg_x + math.cos(swirl_angle) * swirl_r * 0.5
            sy = seg_y + math.sin(swirl_angle) * swirl_r * 0.5
            ex = seg_x + math.cos(swirl_angle + 0.5) * swirl_r
            ey = seg_y + math.sin(swirl_angle + 0.5) * swirl_r
            pygame.draw.line(s, (*theme["energy"], 60), (int(sx), int(sy)), (int(ex), int(ey)), 1)
        
        # 头部处理
        if i == 0:
            _draw_phantom_head(s, seg_x, seg_y, radius, t, theme)
    
    # === 灵魂连接丝 ===
    for i in range(len(positions) - 1):
        x1, y1, r1 = positions[i]
        x2, y2, r2 = positions[i + 1]
        
        # 多股灵魂丝
        for strand in range(3):
            offset = (strand - 1) * 3
            wave_off = math.sin(t * 0.15 + i + strand) * 2
            pygame.draw.line(s, (*theme["energy"], 60),
                           (int(x1 + offset + wave_off), int(y1)),
                           (int(x2 + offset - wave_off), int(y2)), 1)
        
        # 灵魂粒子
        for p in range(2):
            particle_t = (t * 0.15 + i * 0.3 + p * 0.5) % 1.0
            px = int(x1 + (x2 - x1) * particle_t)
            py = int(y1 + (y2 - y1) * particle_t)
            pygame.draw.circle(s, (*theme["accent"], 150), (px, py), 2)
    
    # === 幽灵尾焰 ===
    tail_x, tail_y, _ = positions[-1]
    _draw_phantom_tail(s, tail_x, tail_y + spacing * 0.6, t, theme)
    
    # === 灵魂之翼 ===
    head_x, head_y, _ = positions[0]
    _draw_phantom_wings(s, head_x, head_y, w, h, t, theme)


def _draw_phantom_head(s, cx, cy, radius, t, theme):
    """幽灵涂装 - 头部：空洞双眼 + 幽灵须"""
    # 空洞眼眶
    for side in [-1, 1]:
        eye_x = cx + side * radius * 0.4
        eye_y = cy - radius * 0.1
        
        # 眼眶深渊
        pygame.draw.circle(s, (0, 0, 0), (int(eye_x), int(eye_y)), 5)
        # 灵魂之光
        glow_pulse = 0.5 + 0.5 * math.sin(t * 0.15 + side)
        pygame.draw.circle(s, (*theme["accent"], int(200 * glow_pulse)), (int(eye_x), int(eye_y)), 3)
        # 眼眶光晕
        pygame.draw.circle(s, (*theme["glow"], 80), (int(eye_x), int(eye_y)), 7, 1)
    
    # 幽灵触须
    for i in range(5):
        tendril_angle = math.pi * 0.3 + i * math.pi * 0.1
        tendril_wave = math.sin(t * 0.12 + i * 0.8) * 8
        tendril_len = radius * (0.8 + i * 0.15)
        
        start_x = cx + math.cos(tendril_angle) * radius * 0.5
        start_y = cy + math.sin(tendril_angle) * radius * 0.3
        end_x = start_x + tendril_len + tendril_wave
        end_y = start_y + math.sin(t * 0.1 + i) * 5
        
        # 渐变触须
        for seg in range(4):
            seg_t = seg / 4
            sx = start_x + (end_x - start_x) * seg_t
            sy = start_y + (end_y - start_y) * seg_t
            ex = start_x + (end_x - start_x) * (seg_t + 0.25)
            ey = start_y + (end_y - start_y) * (seg_t + 0.25)
            alpha = int(100 - seg * 20)
            pygame.draw.line(s, (*theme["energy"], alpha), (int(sx), int(sy)), (int(ex), int(ey)), 2 - seg // 2)


def _draw_phantom_tail(s, cx, cy, t, theme):
    """幽灵涂装 - 尾部：消散的灵魂"""
    # 灵魂火焰
    for i in range(8):
        flame_angle = i * math.pi / 4
        flame_len = 15 + math.sin(t * 0.2 + i) * 8
        wave = math.sin(t * 0.15 + i * 0.6) * 3
        
        fx = cx + math.cos(flame_angle) * 5 + wave
        fy = cy + i * 3
        
        # 火焰粒子
        alpha = int(100 - i * 10)
        size = max(1, 4 - i // 2)
        pygame.draw.circle(s, (*theme["energy"], alpha), (int(fx), int(fy)), size)
    
    # 消散粒子
    for i in range(6):
        px = cx + math.sin(t * 0.1 + i * 1.2) * 15
        py = cy + 10 + i * 5 + math.sin(t * 0.08 + i) * 3
        alpha = int(80 - i * 12)
        pygame.draw.circle(s, (*theme["glow"], alpha), (int(px), int(py)), 2)


def _draw_phantom_wings(s, cx, cy, w, h, t, theme):
    """幽灵涂装 - 灵魂之翼：流动的能量"""
    wing_span = int(w * 0.45)
    
    for side in [-1, 1]:
        base_x = cx + side * 8
        
        # 翼膜 - 多层半透明
        for layer in range(3):
            wing_pts = []
            for i in range(6):
                angle = math.pi * 0.5 + side * (i * 0.15 + 0.1)
                wave = math.sin(t * 0.1 + i * 0.5 + layer) * 5
                dist = wing_span * (0.3 + i * 0.14) - layer * 5
                wx = base_x + side * dist + wave
                wy = cy - 10 + i * 8 + math.cos(t * 0.08 + i) * 3
                wing_pts.append((wx, wy))
            
            alpha = 40 - layer * 12
            if len(wing_pts) >= 3:
                pygame.draw.polygon(s, (*theme["energy"], alpha), wing_pts)
        
        # 翼脉
        for i in range(4):
            vein_x = base_x + side * (10 + i * 12)
            vein_wave = math.sin(t * 0.12 + i) * 3
            pygame.draw.line(s, (*theme["glow"], 80),
                           (int(vein_x + vein_wave), cy - 5),
                           (int(vein_x + vein_wave + side * 8), cy + 25), 1)


def draw_oro_golden(s, cx, cy, w, h, t):
    """
    弑神装甲·重装 - 六边形重甲蠕虫
    特点：六边形装甲板 + 金色镶边 + 熔金能量 + 重型炮塔
    """
    theme = get_oro_theme("oro_golden")
    seg_count = 5  # 更少但更大的节段
    base_size = min(w, h) * 0.42
    spacing = h * 0.14
    positions = []
    
    # === 绘制重装节段 ===
    for i in range(seg_count):
        wave = math.sin(t * 0.06 + i * 0.3) * (2 + i * 0.3)  # 重甲蠕动更慢
        seg_y = cy - h * 0.25 + i * spacing
        seg_x = cx + wave
        seg_size = base_size * (1.0 - i * 0.1)
        positions.append((seg_x, seg_y, seg_size))
        
        # 六边形装甲
        hex_r = seg_size * 0.5
        hex_pts = []
        for j in range(6):
            angle = math.radians(j * 60 - 90)
            hx = seg_x + math.cos(angle) * hex_r
            hy = seg_y + math.sin(angle) * hex_r * 0.7
            hex_pts.append((hx, hy))
        
        # 装甲底层
        pygame.draw.polygon(s, theme["body"], hex_pts)
        
        # 金色镶边 - 双层
        pygame.draw.polygon(s, theme["core"], hex_pts, 3)
        inner_pts = [(seg_x + (p[0] - seg_x) * 0.85, seg_y + (p[1] - seg_y) * 0.85) for p in hex_pts]
        pygame.draw.polygon(s, (*theme["energy"], 150), inner_pts, 2)
        
        # 装甲纹理 - 放射状分割线
        for j in range(6):
            pygame.draw.line(s, (*theme["armor"], 100),
                           (int(seg_x), int(seg_y)),
                           (int(hex_pts[j][0] * 0.95 + seg_x * 0.05), 
                            int(hex_pts[j][1] * 0.95 + seg_y * 0.05)), 1)
        
        # 核心能量舱 - 熔金脉动
        core_r = int(hex_r * 0.35)
        pulse = 0.7 + 0.3 * abs(math.sin(t * 0.1 + i * 0.4))
        
        # 熔金外环
        pygame.draw.circle(s, theme["core"], (int(seg_x), int(seg_y)), core_r + 3, 2)
        # 熔金核心
        core_color = tuple(int(c * pulse) for c in theme["energy"])
        pygame.draw.circle(s, core_color, (int(seg_x), int(seg_y)), core_r)
        # 白热中心
        pygame.draw.circle(s, theme["accent"], (int(seg_x), int(seg_y)), core_r // 2)
        
        # 六角铆钉
        for pt in hex_pts:
            pygame.draw.circle(s, theme["core"], (int(pt[0]), int(pt[1])), 4)
            pygame.draw.circle(s, theme["body"], (int(pt[0]), int(pt[1])), 2)
        
        # 头部
        if i == 0:
            _draw_golden_head(s, seg_x, seg_y, seg_size, t, theme)
    
    # === 重甲连接件 ===
    for i in range(len(positions) - 1):
        x1, y1, s1 = positions[i]
        x2, y2, s2 = positions[i + 1]
        
        # 液压连接杆
        for offset in [-8, 0, 8]:
            pygame.draw.line(s, theme["armor"],
                           (int(x1 + offset), int(y1 + s1 * 0.25)),
                           (int(x2 + offset), int(y2 - s2 * 0.25)), 3)
        
        # 金色装饰条
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        pygame.draw.rect(s, theme["core"],
                        (mid_x - 6, mid_y - 3, 12, 6), border_radius=2)
        
        # 能量流
        flow_t = (t * 0.12 + i * 0.5) % 1.0
        fx = int(x1 + (x2 - x1) * flow_t)
        fy = int(y1 + (y2 - y1) * flow_t)
        pygame.draw.circle(s, theme["accent"], (fx, fy), 4)
    
    # === 尾部推进器 ===
    tail_x, tail_y, tail_s = positions[-1]
    _draw_golden_tail(s, tail_x, tail_y + tail_s * 0.4, t, theme)
    
    # === 重型装甲翼 ===
    head_x, head_y, _ = positions[0]
    _draw_golden_wings(s, head_x, head_y, w, h, t, theme)
    
    # === 重型浮游炮 ===
    _draw_golden_turrets(s, cx, cy, w, h, t, theme)


def _draw_golden_head(s, cx, cy, size, t, theme):
    """重装涂装 - 头部：装甲面罩 + 金色王冠"""
    # 王冠
    crown_pts = [
        (cx - 15, cy - size * 0.35),
        (cx - 10, cy - size * 0.5),
        (cx - 5, cy - size * 0.4),
        (cx, cy - size * 0.55),
        (cx + 5, cy - size * 0.4),
        (cx + 10, cy - size * 0.5),
        (cx + 15, cy - size * 0.35),
    ]
    pygame.draw.polygon(s, theme["core"], crown_pts)
    pygame.draw.polygon(s, theme["accent"], crown_pts, 2)
    
    # 王冠宝石
    for i in [1, 3, 5]:
        gem_x, gem_y = crown_pts[i]
        pygame.draw.circle(s, theme["accent"], (int(gem_x), int(gem_y - 3)), 3)
        pygame.draw.circle(s, (255, 255, 255), (int(gem_x - 1), int(gem_y - 4)), 1)
    
    # 装甲面罩
    visor_pts = [
        (cx - 12, cy),
        (cx + 20, cy - 8),
        (cx + 25, cy),
        (cx + 20, cy + 8),
        (cx - 12, cy)
    ]
    pygame.draw.polygon(s, theme["body"], visor_pts)
    pygame.draw.polygon(s, theme["core"], visor_pts, 2)
    
    # 眼槽
    pygame.draw.line(s, theme["accent"], (cx - 5, cy - 3), (cx + 10, cy - 5), 3)
    pygame.draw.line(s, theme["accent"], (cx - 5, cy + 3), (cx + 10, cy + 5), 3)


def _draw_golden_tail(s, cx, cy, t, theme):
    """重装涂装 - 尾部：三联推进器"""
    for i, offset in enumerate([-12, 0, 12]):
        tx = cx + offset
        ty = cy + abs(offset) * 0.2
        
        # 推进器外壳
        pygame.draw.ellipse(s, theme["body"], (tx - 6, ty - 4, 12, 20))
        pygame.draw.ellipse(s, theme["core"], (tx - 6, ty - 4, 12, 20), 2)
        
        # 推进火焰
        flame_len = 8 + math.sin(t * 0.3 + i) * 4
        flame_pts = [
            (tx - 4, ty + 8),
            (tx, ty + 8 + flame_len),
            (tx + 4, ty + 8)
        ]
        pygame.draw.polygon(s, theme["accent"], flame_pts)
        
        # 火焰内核
        inner_pts = [
            (tx - 2, ty + 10),
            (tx, ty + 8 + flame_len * 0.7),
            (tx + 2, ty + 10)
        ]
        pygame.draw.polygon(s, (255, 255, 200), inner_pts)


def _draw_golden_wings(s, cx, cy, w, h, t, theme):
    """重装涂装 - 装甲翼：厚重的金属板"""
    wing_w = int(w * 0.35)
    wing_h = int(h * 0.25)
    
    for side in [-1, 1]:
        base_x = cx + side * 15
        
        # 主装甲翼
        wing_pts = [
            (base_x, cy - wing_h // 2),
            (base_x + side * wing_w, cy - wing_h // 3),
            (base_x + side * wing_w * 1.1, cy),
            (base_x + side * wing_w, cy + wing_h // 3),
            (base_x, cy + wing_h // 2)
        ]
        pygame.draw.polygon(s, theme["body"], wing_pts)
        pygame.draw.polygon(s, theme["core"], wing_pts, 3)
        
        # 装甲板分割
        for i in range(3):
            div_x = base_x + side * (i + 1) * wing_w // 4
            pygame.draw.line(s, theme["armor"],
                           (int(div_x), cy - wing_h // 2 + 5),
                           (int(div_x), cy + wing_h // 2 - 5), 2)
        
        # 翼尖武器
        tip_x = base_x + side * wing_w * 1.1
        pygame.draw.circle(s, theme["core"], (int(tip_x), int(cy)), 5)
        pygame.draw.circle(s, theme["accent"], (int(tip_x), int(cy)), 3)


def _draw_golden_turrets(s, cx, cy, w, h, t, theme):
    """重装涂装 - 重型浮游炮"""
    orbit_r = w * 0.38
    
    for i in range(4):
        angle = t * 0.04 + i * math.pi / 2  # 更慢的旋转
        tx = cx + math.cos(angle) * orbit_r
        ty = cy + math.sin(angle) * orbit_r * 0.5
        
        # 重型炮塔
        turret_w, turret_h = 14, 10
        pygame.draw.rect(s, theme["body"],
                        (tx - turret_w//2, ty - turret_h//2, turret_w, turret_h),
                        border_radius=3)
        pygame.draw.rect(s, theme["core"],
                        (tx - turret_w//2, ty - turret_h//2, turret_w, turret_h),
                        2, border_radius=3)
        
        # 炮管
        barrel_dir = math.atan2(cy - ty, cx - tx)
        bx = tx - math.cos(barrel_dir) * 8
        by = ty - math.sin(barrel_dir) * 8
        pygame.draw.line(s, theme["core"], (int(tx), int(ty)), (int(bx), int(by)), 4)
        pygame.draw.circle(s, theme["accent"], (int(bx), int(by)), 3)
        
        # 能量链接
        pygame.draw.line(s, (*theme["energy"], 80), (int(cx), int(cy)), (int(tx), int(ty)), 2)


# =============================================================================
#   [系列二：元素反转] - 精细化独立绘制函数
# =============================================================================

def draw_oro_inferno(s, cx, cy, w, h, t):
    """
    狱炎长虫·熔岩 - 岩浆蠕虫
    特点：熔岩脉动圆形节段 + 裂纹纹理 + 火焰喷射 + 熔岩翼
    """
    theme = get_oro_theme("oro_inferno")
    seg_count = 6
    base_size = min(w, h) * 0.34
    spacing = h * 0.12
    positions = []
    
    # === 绘制熔岩节段 ===
    for i in range(seg_count):
        # 不规则蠕动
        wave = math.sin(t * 0.12 + i * 0.6) * (4 + i * 0.5)
        pulse = 1.0 + 0.08 * math.sin(t * 0.15 + i * 0.4)
        seg_y = cy - h * 0.28 + i * spacing
        seg_x = cx + wave
        radius = int(base_size * (1.0 - i * 0.08) * 0.5 * pulse)
        positions.append((seg_x, seg_y, radius))
        
        # 外层岩壳
        pygame.draw.circle(s, theme["body"], (int(seg_x), int(seg_y)), radius + 3)
        pygame.draw.circle(s, theme["armor"], (int(seg_x), int(seg_y)), radius)
        
        # 熔岩裂纹
        for j in range(5):
            crack_angle = j * math.pi * 0.4 + i * 0.5
            crack_wave = math.sin(t * 0.1 + j + i) * 2
            
            start_r = radius * 0.3
            end_r = radius * 0.95
            sx = seg_x + math.cos(crack_angle) * start_r
            sy = seg_y + math.sin(crack_angle) * start_r
            ex = seg_x + math.cos(crack_angle + crack_wave * 0.1) * end_r
            ey = seg_y + math.sin(crack_angle + crack_wave * 0.1) * end_r
            
            # 裂纹发光
            crack_glow = 0.7 + 0.3 * math.sin(t * 0.2 + j)
            crack_color = tuple(int(c * crack_glow) for c in theme["core"])
            pygame.draw.line(s, crack_color, (int(sx), int(sy)), (int(ex), int(ey)), 2)
        
        # 熔岩核心 - 脉动发光
        core_r = int(radius * 0.4)
        core_pulse = 0.6 + 0.4 * abs(math.sin(t * 0.18 + i * 0.5))
        
        pygame.draw.circle(s, theme["core"], (int(seg_x), int(seg_y)), core_r + 2)
        core_bright = tuple(int(c * core_pulse) for c in theme["glow"])
        pygame.draw.circle(s, core_bright, (int(seg_x), int(seg_y)), core_r)
        
        # 白热中心
        if core_pulse > 0.8:
            pygame.draw.circle(s, theme["accent"], (int(seg_x), int(seg_y)), core_r // 2)
        
        # 熔岩飞溅粒子
        if random.random() > 0.7:
            spark_x = seg_x + random.randint(-radius, radius)
            spark_y = seg_y + random.randint(-radius, radius)
            pygame.draw.circle(s, theme["glow"], (int(spark_x), int(spark_y)), 2)
        
        # 头部
        if i == 0:
            _draw_inferno_head(s, seg_x, seg_y, radius, t, theme)
    
    # === 熔岩连接 ===
    for i in range(len(positions) - 1):
        x1, y1, r1 = positions[i]
        x2, y2, r2 = positions[i + 1]
        
        # 熔岩流
        flow_pts = []
        for j in range(5):
            ft = j / 4
            fx = x1 + (x2 - x1) * ft + math.sin(t * 0.15 + j) * 3
            fy = y1 + (y2 - y1) * ft
            flow_pts.append((fx, fy))
        
        for j in range(len(flow_pts) - 1):
            glow = 0.6 + 0.4 * math.sin(t * 0.2 + j)
            color = tuple(int(c * glow) for c in theme["core"])
            pygame.draw.line(s, color, 
                           (int(flow_pts[j][0]), int(flow_pts[j][1])),
                           (int(flow_pts[j+1][0]), int(flow_pts[j+1][1])), 4)
    
    # === 尾部火山口 ===
    tail_x, tail_y, _ = positions[-1]
    _draw_inferno_tail(s, tail_x, tail_y + spacing * 0.7, t, theme)
    
    # === 熔岩翼 ===
    head_x, head_y, _ = positions[0]
    _draw_inferno_wings(s, head_x, head_y, w, h, t, theme)


def _draw_inferno_head(s, cx, cy, radius, t, theme):
    """熔岩涂装 - 头部：火焰眼 + 熔岩颚"""
    # 熔岩眼 - 发光的裂缝
    for side in [-1, 1]:
        eye_x = cx + side * radius * 0.5
        eye_y = cy - radius * 0.2
        
        # 眼眶裂纹
        pygame.draw.ellipse(s, theme["body"], 
                          (eye_x - 6, eye_y - 4, 12, 8))
        # 熔岩眼球
        eye_glow = 0.7 + 0.3 * math.sin(t * 0.15 + side)
        pygame.draw.ellipse(s, tuple(int(c * eye_glow) for c in theme["glow"]),
                          (eye_x - 4, eye_y - 2, 8, 5))
        # 瞳孔火焰
        pygame.draw.circle(s, theme["accent"], (int(eye_x), int(eye_y)), 2)
    
    # 熔岩颚
    jaw_open = 4 + math.sin(t * 0.1) * 3
    
    for side in [-1, 1]:
        jaw_y = cy + side * (radius * 0.3 + jaw_open)
        
        # 岩石颚
        jaw_pts = [
            (cx + 5, jaw_y - side * 5),
            (cx + radius + 10, jaw_y),
            (cx + radius + 5, jaw_y + side * 4),
            (cx + 8, jaw_y + side * 2)
        ]
        pygame.draw.polygon(s, theme["armor"], jaw_pts)
        
        # 熔岩牙齿
        for j in range(3):
            tooth_x = cx + 12 + j * 8
            tooth_y = jaw_y - side * 2
            pygame.draw.polygon(s, theme["glow"], [
                (tooth_x, tooth_y),
                (tooth_x + 3, tooth_y + side * 6),
                (tooth_x + 6, tooth_y)
            ])


def _draw_inferno_tail(s, cx, cy, t, theme):
    """熔岩涂装 - 尾部：火山喷发"""
    # 火山口
    pygame.draw.ellipse(s, theme["body"], (cx - 12, cy - 6, 24, 12))
    pygame.draw.ellipse(s, theme["core"], (cx - 8, cy - 4, 16, 8))
    
    # 喷发火焰
    for i in range(8):
        flame_angle = (i - 3.5) * 0.15
        flame_len = 15 + math.sin(t * 0.25 + i) * 10
        wave = math.sin(t * 0.2 + i * 0.7) * 4
        
        fx = cx + flame_angle * 20 + wave
        fy = cy + 5 + i * 2 + flame_len * 0.3
        
        # 火焰粒子
        size = max(2, 5 - i // 2)
        if i < 4:
            pygame.draw.circle(s, theme["glow"], (int(fx), int(fy)), size)
        else:
            pygame.draw.circle(s, theme["core"], (int(fx), int(fy)), size)
    
    # 熔岩飞溅
    for i in range(4):
        splash_x = cx + math.sin(t * 0.3 + i * 1.5) * 20
        splash_y = cy + 20 + random.randint(0, 10)
        pygame.draw.circle(s, theme["accent"], (int(splash_x), int(splash_y)), 2)


def _draw_inferno_wings(s, cx, cy, w, h, t, theme):
    """熔岩涂装 - 熔岩翼：流动的岩浆"""
    wing_w = int(w * 0.4)
    
    for side in [-1, 1]:
        base_x = cx + side * 10
        
        # 翼骨架
        for i in range(4):
            bone_angle = side * (0.3 + i * 0.15)
            bone_len = wing_w * (0.5 + i * 0.15)
            bone_wave = math.sin(t * 0.1 + i) * 3
            
            ex = base_x + side * bone_len + bone_wave
            ey = cy - 10 + i * 12
            
            pygame.draw.line(s, theme["armor"], (int(base_x), int(cy)), (int(ex), int(ey)), 3)
            
            # 熔岩滴落
            drip_y = ey + abs(math.sin(t * 0.15 + i)) * 8
            pygame.draw.circle(s, theme["core"], (int(ex), int(drip_y)), 3)
        
        # 熔岩膜
        membrane_pts = []
        for i in range(5):
            mx = base_x + side * (10 + i * 8) + math.sin(t * 0.12 + i) * 3
            my = cy - 5 + i * 10
            membrane_pts.append((mx, my))
        
        if len(membrane_pts) >= 3:
            pygame.draw.polygon(s, (*theme["core"], 60), membrane_pts)


def draw_oro_frost(s, cx, cy, w, h, t):
    """
    极地灾厄·冰晶 - 菱形冰晶蠕虫
    特点：锐利菱形节段 + 冰霜纹理 + 寒气尾迹 + 冰晶翼
    """
    theme = get_oro_theme("oro_frost")
    seg_count = 7
    base_size = min(w, h) * 0.35
    spacing = h * 0.11
    positions = []
    
    # === 绘制冰晶节段 ===
    for i in range(seg_count):
        wave = math.sin(t * 0.08 + i * 0.5) * (3 + i * 0.4)
        seg_y = cy - h * 0.3 + i * spacing
        seg_x = cx + wave
        seg_size = base_size * (1.0 - i * 0.07)
        positions.append((seg_x, seg_y, seg_size))
        
        # 菱形主体
        diamond_w = seg_size * 0.55
        diamond_h = seg_size * 0.35
        
        # 多层冰晶
        for layer in range(3):
            scale = 1.0 - layer * 0.2
            pts = [
                (seg_x, seg_y - diamond_h * scale),
                (seg_x + diamond_w * scale, seg_y),
                (seg_x, seg_y + diamond_h * scale),
                (seg_x - diamond_w * scale, seg_y)
            ]
            
            if layer == 0:
                # 外层冰壳
                pygame.draw.polygon(s, theme["body"], pts)
                pygame.draw.polygon(s, theme["glow"], pts, 2)
            elif layer == 1:
                # 中层折射
                pygame.draw.polygon(s, (*theme["armor"], 150), pts)
                pygame.draw.polygon(s, (*theme["energy"], 100), pts, 1)
            else:
                # 核心
                pygame.draw.polygon(s, theme["core"], pts)
        
        # 冰晶纹理 - 放射状
        for j in range(4):
            angle = j * math.pi / 2 + math.pi / 4
            inner_r = seg_size * 0.1
            outer_r = seg_size * 0.4
            
            sx = seg_x + math.cos(angle) * inner_r
            sy = seg_y + math.sin(angle) * inner_r * 0.6
            ex = seg_x + math.cos(angle) * outer_r
            ey = seg_y + math.sin(angle) * outer_r * 0.6
            
            pygame.draw.line(s, (*theme["glow"], 150), (int(sx), int(sy)), (int(ex), int(ey)), 1)
        
        # 霜花装饰
        for j in range(6):
            frost_angle = j * math.pi / 3
            frost_r = diamond_w * 0.8
            fx = seg_x + math.cos(frost_angle) * frost_r
            fy = seg_y + math.sin(frost_angle) * frost_r * 0.6
            
            # 六角雪花
            for k in range(6):
                flake_angle = k * math.pi / 3
                flake_len = 3
                fex = fx + math.cos(flake_angle) * flake_len
                fey = fy + math.sin(flake_angle) * flake_len
                pygame.draw.line(s, (*theme["accent"], 120), (int(fx), int(fy)), (int(fex), int(fey)), 1)
        
        # 头部
        if i == 0:
            _draw_frost_head(s, seg_x, seg_y, seg_size, t, theme)
    
    # === 寒冰连接 ===
    for i in range(len(positions) - 1):
        x1, y1, s1 = positions[i]
        x2, y2, s2 = positions[i + 1]
        
        # 冰桥
        bridge_pts = [
            (x1 - 4, y1 + s1 * 0.15),
            (x1 + 4, y1 + s1 * 0.15),
            (x2 + 3, y2 - s2 * 0.15),
            (x2 - 3, y2 - s2 * 0.15)
        ]
        pygame.draw.polygon(s, (*theme["energy"], 100), bridge_pts)
        pygame.draw.polygon(s, (*theme["glow"], 150), bridge_pts, 1)
        
        # 寒气粒子
        for p in range(3):
            pt = (t * 0.1 + i * 0.3 + p * 0.33) % 1.0
            px = int(x1 + (x2 - x1) * pt + math.sin(t * 0.2 + p) * 3)
            py = int(y1 + (y2 - y1) * pt)
            pygame.draw.circle(s, (*theme["accent"], 180), (px, py), 2)
    
    # === 冰晶尾刺 ===
    tail_x, tail_y, _ = positions[-1]
    _draw_frost_tail(s, tail_x, tail_y + spacing * 0.6, t, theme)
    
    # === 冰晶翼 ===
    head_x, head_y, _ = positions[0]
    _draw_frost_wings(s, head_x, head_y, w, h, t, theme)


def _draw_frost_head(s, cx, cy, size, t, theme):
    """冰晶涂装 - 头部：冰眼 + 冰刺角"""
    # 冰晶眼
    for side in [-1, 1]:
        eye_x = cx + side * size * 0.25
        eye_y = cy - size * 0.1
        
        # 菱形眼眶
        eye_pts = [
            (eye_x, eye_y - 5),
            (eye_x + 5, eye_y),
            (eye_x, eye_y + 5),
            (eye_x - 5, eye_y)
        ]
        pygame.draw.polygon(s, theme["body"], eye_pts)
        pygame.draw.polygon(s, theme["core"], eye_pts, 1)
        
        # 冰蓝瞳孔
        pygame.draw.circle(s, theme["glow"], (int(eye_x), int(eye_y)), 3)
        pygame.draw.circle(s, theme["accent"], (int(eye_x), int(eye_y)), 1)
    
    # 冰刺角
    for side in [-1, 1]:
        horn_base_x = cx + side * size * 0.35
        horn_base_y = cy - size * 0.2
        
        # 主角
        horn_pts = [
            (horn_base_x, horn_base_y),
            (horn_base_x + side * 8, horn_base_y - 15),
            (horn_base_x + side * 3, horn_base_y - 5)
        ]
        pygame.draw.polygon(s, theme["energy"], horn_pts)
        pygame.draw.polygon(s, theme["glow"], horn_pts, 1)
        
        # 副刺
        pygame.draw.polygon(s, (*theme["accent"], 180), [
            (horn_base_x + side * 5, horn_base_y - 8),
            (horn_base_x + side * 12, horn_base_y - 12),
            (horn_base_x + side * 7, horn_base_y - 6)
        ])
    
    # 前颚冰锥
    for i in range(3):
        spike_x = cx + 10 + i * 6
        spike_wave = math.sin(t * 0.1 + i) * 2
        
        spike_pts = [
            (spike_x, cy - 3 + spike_wave),
            (spike_x + 8, cy + spike_wave),
            (spike_x, cy + 3 + spike_wave)
        ]
        pygame.draw.polygon(s, theme["glow"], spike_pts)


def _draw_frost_tail(s, cx, cy, t, theme):
    """冰晶涂装 - 尾部：三叉冰锥"""
    offsets = [(0, 0), (-15, -5), (15, -5)]
    
    for idx, (ox, oy) in enumerate(offsets):
        float_y = math.sin(t * 0.1 + idx * 2) * 3
        tx, ty = cx + ox, cy + oy + float_y
        
        # 冰锥
        spike_len = 18 if idx == 0 else 14
        spike_pts = [
            (tx, ty - 5),
            (tx - 5, ty),
            (tx - 3, ty + spike_len),
            (tx + 3, ty + spike_len),
            (tx + 5, ty)
        ]
        pygame.draw.polygon(s, theme["body"], spike_pts)
        pygame.draw.polygon(s, theme["glow"], spike_pts, 1)
        
        # 内部折射
        inner_pts = [
            (tx, ty),
            (tx - 2, ty + spike_len * 0.8),
            (tx + 2, ty + spike_len * 0.8)
        ]
        pygame.draw.polygon(s, theme["core"], inner_pts)
        
        # 寒气
        for j in range(3):
            mist_y = ty + spike_len + 3 + j * 3
            mist_alpha = 80 - j * 25
            pygame.draw.ellipse(s, (*theme["energy"], mist_alpha),
                              (tx - 4, mist_y, 8, 3))


def _draw_frost_wings(s, cx, cy, w, h, t, theme):
    """冰晶涂装 - 冰晶翼：棱镜结构"""
    wing_span = int(w * 0.4)
    
    for side in [-1, 1]:
        base_x = cx + side * 8
        
        # 主冰晶翼 - 三层棱镜
        for layer in range(3):
            scale = 1.0 - layer * 0.25
            crystal_pts = [
                (base_x, cy - 15 * scale),
                (base_x + side * wing_span * scale, cy - 5 * scale),
                (base_x + side * wing_span * 0.8 * scale, cy + 15 * scale),
                (base_x, cy + 10 * scale)
            ]
            
            if layer == 0:
                pygame.draw.polygon(s, (*theme["body"], 180), crystal_pts)
                pygame.draw.polygon(s, theme["glow"], crystal_pts, 2)
            else:
                pygame.draw.polygon(s, (*theme["energy"], 80 - layer * 20), crystal_pts)
        
        # 棱镜折射线
        for i in range(4):
            rx = base_x + side * (5 + i * 10)
            ry_start = cy - 12 + i * 2
            ry_end = cy + 8 + i * 2
            pygame.draw.line(s, (*theme["accent"], 100), 
                           (int(rx), int(ry_start)), (int(rx), int(ry_end)), 1)


def draw_oro_toxic(s, cx, cy, w, h, t):
    """
    生化危机·辐射 - 有机变异蠕虫
    特点：不规则蠕动节段 + 毒液滴落 + 辐射光晕 + 孢子翼
    """
    theme = get_oro_theme("oro_toxic")
    seg_count = 6
    base_size = min(w, h) * 0.34
    spacing = h * 0.12
    positions = []
    
    # === 绘制变异节段 ===
    for i in range(seg_count):
        # 有机蠕动 - 更不规则
        wave = math.sin(t * 0.14 + i * 0.7) * (5 + i * 0.8)
        squash = 1.0 + 0.1 * math.sin(t * 0.18 + i * 0.5)
        seg_y = cy - h * 0.28 + i * spacing
        seg_x = cx + wave
        radius = int(base_size * (1.0 - i * 0.08) * 0.45)
        positions.append((seg_x, seg_y, radius))
        
        # 不规则外形 - 8边变形圆
        organic_pts = []
        for j in range(8):
            angle = j * math.pi / 4
            r_var = radius + math.sin(t * 0.15 + j * 0.8 + i) * 4
            ox = seg_x + math.cos(angle) * r_var
            oy = seg_y + math.sin(angle) * r_var * squash
            organic_pts.append((ox, oy))
        
        # 外膜
        pygame.draw.polygon(s, theme["body"], organic_pts)
        pygame.draw.polygon(s, (*theme["armor"], 150), organic_pts, 2)
        
        # 毒液泡
        for j in range(3):
            bubble_angle = t * 0.1 + j * 2 + i
            bubble_r = radius * 0.6
            bx = seg_x + math.cos(bubble_angle) * bubble_r * 0.5
            by = seg_y + math.sin(bubble_angle) * bubble_r * 0.5
            bubble_size = 3 + int(math.sin(t * 0.2 + j) * 2)
            
            pygame.draw.circle(s, (*theme["core"], 150), (int(bx), int(by)), bubble_size)
            pygame.draw.circle(s, (*theme["glow"], 100), (int(bx), int(by)), bubble_size, 1)
        
        # 辐射核心
        core_r = int(radius * 0.35)
        core_pulse = 0.6 + 0.4 * abs(math.sin(t * 0.12 + i * 0.6))
        
        pygame.draw.circle(s, theme["core"], (int(seg_x), int(seg_y)), core_r + 2)
        glow_color = tuple(int(c * core_pulse) for c in theme["glow"])
        pygame.draw.circle(s, glow_color, (int(seg_x), int(seg_y)), core_r)
        
        # 辐射警示环
        warn_r = core_r + 5 + int(math.sin(t * 0.15) * 3)
        pygame.draw.circle(s, (*theme["accent"], 80), (int(seg_x), int(seg_y)), warn_r, 1)
        
        # 毒液滴落
        if random.random() > 0.8:
            drip_x = seg_x + random.randint(-radius, radius)
            drip_y = seg_y + radius + random.randint(5, 15)
            pygame.draw.circle(s, theme["core"], (int(drip_x), int(drip_y)), 2)
        
        # 头部
        if i == 0:
            _draw_toxic_head(s, seg_x, seg_y, radius, t, theme)
    
    # === 毒液连接 ===
    for i in range(len(positions) - 1):
        x1, y1, r1 = positions[i]
        x2, y2, r2 = positions[i + 1]
        
        # 粘液丝
        for strand in range(3):
            offset = (strand - 1) * 4
            strand_wave = math.sin(t * 0.12 + strand + i) * 3
            
            # 粘液弧线
            mid_x = (x1 + x2) / 2 + strand_wave + offset
            mid_y = (y1 + y2) / 2
            
            pygame.draw.line(s, (*theme["core"], 100), 
                           (int(x1 + offset), int(y1)), (int(mid_x), int(mid_y)), 2)
            pygame.draw.line(s, (*theme["core"], 100),
                           (int(mid_x), int(mid_y)), (int(x2 + offset), int(y2)), 2)
        
        # 毒液滴
        drip_t = (t * 0.15 + i * 0.4) % 1.0
        dx = int(x1 + (x2 - x1) * drip_t)
        dy = int(y1 + (y2 - y1) * drip_t + 3)
        pygame.draw.circle(s, theme["glow"], (dx, dy), 3)
    
    # === 毒刺尾 ===
    tail_x, tail_y, _ = positions[-1]
    _draw_toxic_tail(s, tail_x, tail_y + spacing * 0.7, t, theme)
    
    # === 孢子翼 ===
    head_x, head_y, _ = positions[0]
    _draw_toxic_wings(s, head_x, head_y, w, h, t, theme)


def _draw_toxic_head(s, cx, cy, radius, t, theme):
    """辐射涂装 - 头部：复眼 + 毒颚"""
    # 复眼阵列
    eye_positions = [(-0.3, -0.2), (0.3, -0.2), (0, -0.35), (-0.2, 0.1), (0.2, 0.1)]
    
    for ex_mult, ey_mult in eye_positions:
        eye_x = cx + radius * ex_mult
        eye_y = cy + radius * ey_mult
        eye_size = 4 if abs(ex_mult) < 0.2 else 3
        
        # 眼球
        pygame.draw.circle(s, (0, 0, 0), (int(eye_x), int(eye_y)), eye_size + 1)
        pygame.draw.circle(s, theme["glow"], (int(eye_x), int(eye_y)), eye_size)
        # 反光
        pygame.draw.circle(s, theme["accent"], (int(eye_x - 1), int(eye_y - 1)), 1)
    
    # 毒颚触须
    for side in [-1, 1]:
        for tendril in range(2):
            base_x = cx + 5
            base_y = cy + side * (8 + tendril * 5)
            
            tendril_wave = math.sin(t * 0.15 + tendril + side) * 5
            tendril_len = 15 + tendril * 5
            
            end_x = base_x + tendril_len + tendril_wave
            end_y = base_y + side * tendril_wave * 0.5
            
            pygame.draw.line(s, theme["armor"], (int(base_x), int(base_y)), (int(end_x), int(end_y)), 3)
            
            # 毒刺尖
            pygame.draw.circle(s, theme["glow"], (int(end_x), int(end_y)), 3)


def _draw_toxic_tail(s, cx, cy, t, theme):
    """辐射涂装 - 尾部：毒囊 + 孢子"""
    # 主毒囊
    sac_pulse = 1.0 + 0.1 * math.sin(t * 0.15)
    pygame.draw.ellipse(s, theme["body"], 
                       (cx - 10 * sac_pulse, cy - 6 * sac_pulse, 
                        20 * sac_pulse, 12 * sac_pulse))
    pygame.draw.ellipse(s, theme["core"],
                       (cx - 6 * sac_pulse, cy - 3 * sac_pulse,
                        12 * sac_pulse, 6 * sac_pulse))
    
    # 释放孢子
    for i in range(6):
        spore_angle = t * 0.1 + i * 1.05
        spore_dist = 15 + i * 3 + math.sin(t * 0.2 + i) * 5
        sx = cx + math.sin(spore_angle) * 8
        sy = cy + 8 + spore_dist * 0.3 + i * 2
        
        spore_size = max(1, 3 - i // 2)
        alpha = int(150 - i * 20)
        pygame.draw.circle(s, (*theme["glow"], alpha), (int(sx), int(sy)), spore_size)


def _draw_toxic_wings(s, cx, cy, w, h, t, theme):
    """辐射涂装 - 孢子翼：有机膜翼"""
    wing_span = int(w * 0.38)
    
    for side in [-1, 1]:
        base_x = cx + side * 8
        
        # 翼脉
        veins = []
        for i in range(4):
            vein_angle = side * (0.2 + i * 0.12)
            vein_len = wing_span * (0.4 + i * 0.15)
            vein_wave = math.sin(t * 0.1 + i) * 4
            
            vx = base_x + side * vein_len + vein_wave
            vy = cy - 8 + i * 10
            veins.append((vx, vy))
            
            pygame.draw.line(s, theme["armor"], (int(base_x), int(cy)), (int(vx), int(vy)), 2)
        
        # 翼膜
        if len(veins) >= 3:
            membrane_pts = [(base_x, cy - 5)] + veins + [(base_x, cy + 25)]
            pygame.draw.polygon(s, (*theme["core"], 40), membrane_pts)
            pygame.draw.polygon(s, (*theme["glow"], 80), membrane_pts, 1)
        
        # 孢子点
        for i, (vx, vy) in enumerate(veins):
            mid_x = (base_x + vx) / 2
            mid_y = (cy + vy) / 2
            spore_pulse = 0.7 + 0.3 * math.sin(t * 0.15 + i)
            pygame.draw.circle(s, tuple(int(c * spore_pulse) for c in theme["glow"]),
                             (int(mid_x), int(mid_y)), 3)


# =============================================================================
#   [系列三：概念重构] - 精细化独立绘制函数
# =============================================================================

def draw_oro_cosmic(s, cx, cy, w, h, t):
    """
    矩阵代码·黑客 - 数字虚拟蠕虫
    特点：空心线框节段 + 流动代码 + 数据流连接 + 全息翼
    """
    theme = get_oro_theme("oro_cosmic")
    seg_count = 6
    base_size = min(w, h) * 0.36
    spacing = h * 0.12
    positions = []
    
    # === 绘制矩阵节段 ===
    for i in range(seg_count):
        wave = math.sin(t * 0.1 + i * 0.5) * (3 + i * 0.5)
        seg_y = cy - h * 0.28 + i * spacing
        seg_x = cx + wave
        seg_size = base_size * (1.0 - i * 0.08)
        positions.append((seg_x, seg_y, seg_size))
        
        # 矩形线框
        rect_w = int(seg_size * 1.0)
        rect_h = int(seg_size * 0.6)
        
        # 外框 - 扫描线效果
        scan_offset = int((t * 2 + i * 10) % rect_h)
        
        # 主框架 - 空心
        rect = pygame.Rect(seg_x - rect_w//2, seg_y - rect_h//2, rect_w, rect_h)
        pygame.draw.rect(s, theme["core"], rect, 1)
        
        # 内框
        inner_rect = rect.inflate(-6, -4)
        pygame.draw.rect(s, (*theme["glow"], 150), inner_rect, 1)
        
        # 扫描线
        scan_y = seg_y - rect_h//2 + scan_offset
        if seg_y - rect_h//2 <= scan_y <= seg_y + rect_h//2:
            pygame.draw.line(s, (*theme["accent"], 100),
                           (seg_x - rect_w//2 + 2, int(scan_y)),
                           (seg_x + rect_w//2 - 2, int(scan_y)), 1)
        
        # 角落装饰
        corner_size = 4
        corners = [
            (seg_x - rect_w//2, seg_y - rect_h//2),
            (seg_x + rect_w//2, seg_y - rect_h//2),
            (seg_x - rect_w//2, seg_y + rect_h//2),
            (seg_x + rect_w//2, seg_y + rect_h//2)
        ]
        for cx_c, cy_c in corners:
            pygame.draw.rect(s, theme["core"], 
                           (cx_c - corner_size//2, cy_c - corner_size//2, 
                            corner_size, corner_size))
        
        # 流动代码文字效果
        code_chars = "01"
        for j in range(4):
            char_x = seg_x - rect_w//2 + 5 + j * 10
            char_y = seg_y - rect_h//2 + 3 + int((t * 3 + j * 2 + i) % (rect_h - 6))
            char_alpha = int(100 + 50 * math.sin(t * 0.2 + j))
            
            # 模拟代码字符（用小方块）
            if (int(t * 5 + j + i) % 2) == 0:
                pygame.draw.rect(s, (*theme["glow"], char_alpha),
                               (char_x, char_y, 3, 5))
            else:
                pygame.draw.rect(s, (*theme["core"], char_alpha),
                               (char_x, char_y, 3, 5))
                pygame.draw.rect(s, (*theme["glow"], char_alpha),
                               (char_x + 1, char_y + 1, 1, 3))
        
        # 数据节点
        node_pulse = 0.5 + 0.5 * math.sin(t * 0.15 + i * 0.6)
        pygame.draw.circle(s, (*theme["core"], int(200 * node_pulse)), 
                         (int(seg_x), int(seg_y)), 4)
        pygame.draw.circle(s, theme["glow"], (int(seg_x), int(seg_y)), 6, 1)
        
        # 头部
        if i == 0:
            _draw_cosmic_head(s, seg_x, seg_y, seg_size, t, theme)
    
    # === 数据流连接 ===
    for i in range(len(positions) - 1):
        x1, y1, s1 = positions[i]
        x2, y2, s2 = positions[i + 1]
        
        # 数据管道
        pygame.draw.line(s, (*theme["core"], 60), (int(x1 - 5), int(y1)), (int(x2 - 5), int(y2)), 1)
        pygame.draw.line(s, (*theme["core"], 60), (int(x1 + 5), int(y1)), (int(x2 + 5), int(y2)), 1)
        
        # 数据包
        for p in range(3):
            packet_t = (t * 0.2 + i * 0.3 + p * 0.33) % 1.0
            px = int(x1 + (x2 - x1) * packet_t)
            py = int(y1 + (y2 - y1) * packet_t)
            
            # 数据包方块
            pygame.draw.rect(s, theme["glow"], (px - 2, py - 2, 4, 4))
    
    # === 数据尾流 ===
    tail_x, tail_y, _ = positions[-1]
    _draw_cosmic_tail(s, tail_x, tail_y + spacing * 0.6, t, theme)
    
    # === 全息翼 ===
    head_x, head_y, _ = positions[0]
    _draw_cosmic_wings(s, head_x, head_y, w, h, t, theme)


def _draw_cosmic_head(s, cx, cy, size, t, theme):
    """黑客涂装 - 头部：数字眼 + 天线"""
    # 数字眼 - 方形
    for side in [-1, 1]:
        eye_x = cx + side * size * 0.25
        eye_y = cy - size * 0.1
        
        # 眼框
        pygame.draw.rect(s, theme["core"], (eye_x - 5, eye_y - 4, 10, 8), 1)
        
        # 扫描光
        scan_x = eye_x - 4 + int((t * 4) % 8)
        pygame.draw.line(s, theme["glow"], 
                        (scan_x, eye_y - 3), (scan_x, eye_y + 3), 1)
        
        # 瞳孔数据
        pygame.draw.rect(s, theme["accent"], (eye_x - 2, eye_y - 1, 4, 2))
    
    # 数据天线
    for side in [-1, 1]:
        ant_x = cx + side * size * 0.4
        ant_y = cy - size * 0.25
        
        # 天线杆
        pygame.draw.line(s, theme["core"], 
                        (int(ant_x), int(ant_y)), 
                        (int(ant_x + side * 8), int(ant_y - 12)), 2)
        
        # 信号球
        signal_pulse = 0.5 + 0.5 * math.sin(t * 0.2 + side)
        pygame.draw.circle(s, (*theme["glow"], int(200 * signal_pulse)),
                         (int(ant_x + side * 8), int(ant_y - 12)), 3)
    
    # 前端数据探针
    for i in range(3):
        probe_x = cx + 12 + i * 8
        probe_wave = math.sin(t * 0.15 + i) * 3
        
        pygame.draw.line(s, theme["core"],
                        (int(probe_x), int(cy - 3 + probe_wave)),
                        (int(probe_x + 10), int(cy + probe_wave)), 2)
        pygame.draw.circle(s, theme["glow"], (int(probe_x + 10), int(cy + probe_wave)), 2)


def _draw_cosmic_tail(s, cx, cy, t, theme):
    """黑客涂装 - 尾部：数据输出端口"""
    # 主端口
    pygame.draw.rect(s, theme["body"], (cx - 10, cy - 5, 20, 10))
    pygame.draw.rect(s, theme["core"], (cx - 10, cy - 5, 20, 10), 1)
    
    # 端口灯
    for i in range(4):
        light_x = cx - 7 + i * 5
        light_on = (int(t * 3 + i) % 4) == 0
        color = theme["glow"] if light_on else (*theme["core"], 80)
        pygame.draw.rect(s, color, (light_x, cy - 2, 3, 4))
    
    # 数据流出
    for i in range(5):
        flow_y = cy + 8 + i * 4
        flow_alpha = int(150 - i * 25)
        flow_x = cx + math.sin(t * 0.2 + i) * 5
        
        pygame.draw.rect(s, (*theme["glow"], flow_alpha),
                        (flow_x - 3, flow_y, 6, 2))


def _draw_cosmic_wings(s, cx, cy, w, h, t, theme):
    """黑客涂装 - 全息翼：网格投影"""
    wing_w = int(w * 0.4)
    wing_h = int(h * 0.3)
    grid_size = 8
    
    for side in [-1, 1]:
        base_x = cx + side * 12
        
        # 全息边框
        wing_pts = [
            (base_x, cy - wing_h//2),
            (base_x + side * wing_w, cy - wing_h//3),
            (base_x + side * wing_w * 0.9, cy + wing_h//3),
            (base_x, cy + wing_h//2)
        ]
        pygame.draw.polygon(s, (*theme["core"], 30), wing_pts)
        pygame.draw.polygon(s, (*theme["glow"], 100), wing_pts, 1)
        
        # 网格线
        for i in range(5):
            # 横线
            y_pos = cy - wing_h//2 + (i + 0.5) * wing_h // 5
            alpha = int(60 + 30 * math.sin(t * 0.12 + i))
            pygame.draw.line(s, (*theme["core"], alpha),
                           (int(base_x), int(y_pos)),
                           (int(base_x + side * wing_w * 0.85), int(y_pos)), 1)
        
        for i in range(4):
            # 竖线
            x_pos = base_x + side * (i + 1) * wing_w // 5
            alpha = int(50 + 40 * math.sin(t * 0.1 + i * 0.5))
            pygame.draw.line(s, (*theme["glow"], alpha),
                           (int(x_pos), int(cy - wing_h//2 + 3)),
                           (int(x_pos), int(cy + wing_h//2 - 3)), 1)
        
        # 数据节点
        for i in range(3):
            node_x = base_x + side * (i + 1) * wing_w // 4
            node_y = cy + math.sin(t * 0.15 + i) * 5
            pulse = 0.5 + 0.5 * math.sin(t * 0.2 + i * 0.8)
            
            pygame.draw.rect(s, (*theme["glow"], int(150 * pulse)),
                           (node_x - 2, node_y - 2, 4, 4))


def draw_oro_royal(s, cx, cy, w, h, t):
    """
    水墨游龙·写意 - 中国风水墨蠕虫
    特点：墨晕圆形节段 + 飞白笔触 + 墨点飞溅 + 云纹翼
    """
    theme = get_oro_theme("oro_royal")
    seg_count = 7
    base_size = min(w, h) * 0.32
    spacing = h * 0.11
    positions = []
    
    # === 绘制水墨节段 ===
    for i in range(seg_count):
        # 流畅蜿蜒
        wave = math.sin(t * 0.08 + i * 0.4) * (4 + i * 0.6)
        seg_y = cy - h * 0.32 + i * spacing
        seg_x = cx + wave
        radius = int(base_size * (1.0 - i * 0.06) * 0.45)
        positions.append((seg_x, seg_y, radius))
        
        # 墨晕效果 - 多层渐变
        for layer in range(4, 0, -1):
            layer_r = radius + layer * 3
            # 墨色深浅变化
            ink_alpha = 30 + (4 - layer) * 20
            ink_var = random.randint(-5, 5) if layer > 2 else 0
            pygame.draw.circle(s, (*theme["body"], ink_alpha + ink_var),
                             (int(seg_x), int(seg_y)), layer_r)
        
        # 主墨圈
        pygame.draw.circle(s, theme["body"], (int(seg_x), int(seg_y)), radius)
        
        # 飞白效果 - 不完整的圆
        for j in range(3):
            arc_start = j * 2.1 + t * 0.05 + i * 0.3
            arc_len = 0.8 + random.random() * 0.4
            
            arc_pts = []
            for k in range(8):
                angle = arc_start + k * arc_len / 8
                ax = seg_x + math.cos(angle) * (radius - 2)
                ay = seg_y + math.sin(angle) * (radius - 2)
                arc_pts.append((ax, ay))
            
            if len(arc_pts) >= 2:
                pygame.draw.lines(s, (*theme["glow"], 80), False, 
                                [(int(p[0]), int(p[1])) for p in arc_pts], 2)
        
        # 留白核心
        core_r = int(radius * 0.4)
        pygame.draw.circle(s, theme["core"], (int(seg_x), int(seg_y)), core_r)
        # 墨点
        pygame.draw.circle(s, theme["body"], 
                         (int(seg_x - core_r * 0.3), int(seg_y - core_r * 0.3)), 
                         max(1, core_r // 3))
        
        # 墨点飞溅
        for j in range(2):
            splash_angle = random.random() * math.pi * 2
            splash_dist = radius + random.randint(3, 10)
            sx = seg_x + math.cos(splash_angle) * splash_dist
            sy = seg_y + math.sin(splash_angle) * splash_dist
            pygame.draw.circle(s, theme["body"], (int(sx), int(sy)), random.randint(1, 3))
        
        # 头部
        if i == 0:
            _draw_royal_head(s, seg_x, seg_y, radius, t, theme)
    
    # === 墨丝连接 ===
    for i in range(len(positions) - 1):
        x1, y1, r1 = positions[i]
        x2, y2, r2 = positions[i + 1]
        
        # 书法笔触 - 粗细变化
        ctrl_x = (x1 + x2) / 2 + math.sin(t * 0.1 + i) * 5
        ctrl_y = (y1 + y2) / 2
        
        # 分段绘制以模拟毛笔效果
        for j in range(10):
            t1 = j / 10
            t2 = (j + 1) / 10
            
            # 贝塞尔曲线点
            px1 = (1-t1)**2 * x1 + 2*(1-t1)*t1 * ctrl_x + t1**2 * x2
            py1 = (1-t1)**2 * y1 + 2*(1-t1)*t1 * ctrl_y + t1**2 * y2
            px2 = (1-t2)**2 * x1 + 2*(1-t2)*t2 * ctrl_x + t2**2 * x2
            py2 = (1-t2)**2 * y1 + 2*(1-t2)*t2 * ctrl_y + t2**2 * y2
            
            # 笔触粗细
            thickness = int(3 - abs(t1 - 0.5) * 4)
            pygame.draw.line(s, theme["body"], 
                           (int(px1), int(py1)), (int(px2), int(py2)), 
                           max(1, thickness))
    
    # === 墨云尾 ===
    tail_x, tail_y, _ = positions[-1]
    _draw_royal_tail(s, tail_x, tail_y + spacing * 0.5, t, theme)
    
    # === 云纹翼 ===
    head_x, head_y, _ = positions[0]
    _draw_royal_wings(s, head_x, head_y, w, h, t, theme)


def _draw_royal_head(s, cx, cy, radius, t, theme):
    """水墨涂装 - 头部：龙眼 + 须髯"""
    # 龙眼 - 圆中有神
    for side in [-1, 1]:
        eye_x = cx + side * radius * 0.5
        eye_y = cy - radius * 0.1
        
        # 眼眶
        pygame.draw.circle(s, theme["body"], (int(eye_x), int(eye_y)), 6)
        pygame.draw.circle(s, theme["core"], (int(eye_x), int(eye_y)), 4)
        
        # 瞳孔 - 墨点
        pygame.draw.circle(s, theme["body"], (int(eye_x), int(eye_y)), 2)
        
        # 眼神光
        pygame.draw.circle(s, theme["core"], 
                         (int(eye_x - 1), int(eye_y - 1)), 1)
    
    # 龙须
    for side in [-1, 1]:
        for i in range(3):
            whisker_base_x = cx + 8
            whisker_base_y = cy + side * (3 + i * 4)
            
            whisker_wave = math.sin(t * 0.1 + i * 0.5 + side) * 5
            whisker_len = 20 + i * 5
            
            # 须的曲线
            ctrl_x = whisker_base_x + whisker_len * 0.5
            ctrl_y = whisker_base_y + side * 5 + whisker_wave
            end_x = whisker_base_x + whisker_len
            end_y = whisker_base_y + side * (i + 1) * 2
            
            # 分段绘制
            for j in range(8):
                t1 = j / 8
                t2 = (j + 1) / 8
                
                px1 = (1-t1)**2 * whisker_base_x + 2*(1-t1)*t1 * ctrl_x + t1**2 * end_x
                py1 = (1-t1)**2 * whisker_base_y + 2*(1-t1)*t1 * ctrl_y + t1**2 * end_y
                px2 = (1-t2)**2 * whisker_base_x + 2*(1-t2)*t2 * ctrl_x + t2**2 * end_x
                py2 = (1-t2)**2 * whisker_base_y + 2*(1-t2)*t2 * ctrl_y + t2**2 * end_y
                
                thickness = max(1, 2 - j // 3)
                pygame.draw.line(s, theme["body"],
                               (int(px1), int(py1)), (int(px2), int(py2)), thickness)
    
    # 朱砂点 - 额间
    pygame.draw.circle(s, theme["accent"], (int(cx), int(cy - radius * 0.4)), 3)


def _draw_royal_tail(s, cx, cy, t, theme):
    """水墨涂装 - 尾部：墨云消散"""
    # 云纹尾
    for i in range(5):
        cloud_x = cx + math.sin(t * 0.08 + i * 1.2) * 10
        cloud_y = cy + i * 5
        cloud_r = max(3, 8 - i)
        
        # 云朵 - 多圆组合
        for j in range(3):
            offset_x = (j - 1) * cloud_r * 0.6
            pygame.draw.circle(s, (*theme["body"], 150 - i * 25),
                             (int(cloud_x + offset_x), int(cloud_y)), cloud_r - j)
    
    # 墨点飞溅
    for i in range(4):
        dot_x = cx + random.randint(-15, 15)
        dot_y = cy + 20 + random.randint(0, 15)
        pygame.draw.circle(s, (*theme["body"], 100), (int(dot_x), int(dot_y)), 
                         random.randint(1, 2))


def _draw_royal_wings(s, cx, cy, w, h, t, theme):
    """水墨涂装 - 云纹翼：祥云图案"""
    wing_span = int(w * 0.42)
    
    for side in [-1, 1]:
        base_x = cx + side * 10
        
        # 祥云主体
        for layer in range(3):
            cloud_y = cy + layer * 8 - 8
            cloud_scale = 1.0 - layer * 0.2
            
            # 云朵轮廓
            for i in range(4):
                wave = math.sin(t * 0.06 + i * 0.5 + layer) * 3
                cloud_x = base_x + side * (10 + i * 12) * cloud_scale + wave
                cloud_r = int((8 - i) * cloud_scale)
                
                # 云圈
                pygame.draw.circle(s, (*theme["body"], 100 - layer * 25),
                                 (int(cloud_x), int(cloud_y)), cloud_r)
                
                # 云边
                if layer == 0:
                    pygame.draw.circle(s, (*theme["glow"], 60),
                                     (int(cloud_x), int(cloud_y)), cloud_r, 1)
        
        # 云气飘动
        for i in range(3):
            wisp_x = base_x + side * (wing_span * 0.3 + i * 15)
            wisp_y = cy + math.sin(t * 0.1 + i) * 8
            wisp_len = 12 - i * 3
            
            pygame.draw.arc(s, (*theme["glow"], 80),
                          (wisp_x - wisp_len, wisp_y - wisp_len//2, 
                           wisp_len * 2, wisp_len),
                          0 if side > 0 else math.pi, math.pi if side > 0 else math.pi * 2, 1)


def draw_oro_crimson(s, cx, cy, w, h, t):
    """
    折纸大蛇·维度 - 折纸艺术蠕虫
    特点：菱形折纸节段 + 折痕阴影 + 纸鹤装饰 + 千纸鹤翼
    """
    theme = get_oro_theme("oro_crimson")
    seg_count = 6
    base_size = min(w, h) * 0.38
    spacing = h * 0.12
    positions = []
    
    # === 绘制折纸节段 ===
    for i in range(seg_count):
        wave = math.sin(t * 0.07 + i * 0.4) * (3 + i * 0.4)
        seg_y = cy - h * 0.28 + i * spacing
        seg_x = cx + wave
        seg_size = base_size * (1.0 - i * 0.08)
        positions.append((seg_x, seg_y, seg_size))
        
        # 折纸菱形
        diamond_w = seg_size * 0.55
        diamond_h = seg_size * 0.35
        
        # 主折纸体
        main_pts = [
            (seg_x, seg_y - diamond_h),
            (seg_x + diamond_w, seg_y),
            (seg_x, seg_y + diamond_h),
            (seg_x - diamond_w, seg_y)
        ]
        pygame.draw.polygon(s, theme["body"], main_pts)
        
        # 折痕 - 中央十字
        pygame.draw.line(s, theme["core"], 
                        (int(seg_x), int(seg_y - diamond_h)),
                        (int(seg_x), int(seg_y + diamond_h)), 2)
        pygame.draw.line(s, (*theme["core"], 150),
                        (int(seg_x - diamond_w), int(seg_y)),
                        (int(seg_x + diamond_w), int(seg_y)), 1)
        
        # 对角折痕
        pygame.draw.line(s, (*theme["accent"], 100),
                        (int(seg_x - diamond_w * 0.5), int(seg_y - diamond_h * 0.5)),
                        (int(seg_x + diamond_w * 0.5), int(seg_y + diamond_h * 0.5)), 1)
        pygame.draw.line(s, (*theme["accent"], 100),
                        (int(seg_x + diamond_w * 0.5), int(seg_y - diamond_h * 0.5)),
                        (int(seg_x - diamond_w * 0.5), int(seg_y + diamond_h * 0.5)), 1)
        
        # 阴影面 - 折纸立体感
        shadow_pts = [
            (seg_x, seg_y),
            (seg_x + diamond_w, seg_y),
            (seg_x, seg_y + diamond_h)
        ]
        pygame.draw.polygon(s, (*theme["armor"], 80), shadow_pts)
        
        # 边缘描边
        pygame.draw.polygon(s, theme["accent"], main_pts, 1)
        
        # 朱红装饰点
        if i % 2 == 0:
            pygame.draw.circle(s, theme["core"], (int(seg_x), int(seg_y)), 4)
        
        # 头部
        if i == 0:
            _draw_crimson_head(s, seg_x, seg_y, seg_size, t, theme)
    
    # === 折纸连接 ===
    for i in range(len(positions) - 1):
        x1, y1, s1 = positions[i]
        x2, y2, s2 = positions[i + 1]
        
        # 折叠连接片
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        connect_pts = [
            (x1 - 4, y1 + s1 * 0.15),
            (x1 + 4, y1 + s1 * 0.15),
            (mid_x + 6, mid_y),
            (x2 + 3, y2 - s2 * 0.15),
            (x2 - 3, y2 - s2 * 0.15),
            (mid_x - 6, mid_y)
        ]
        pygame.draw.polygon(s, theme["body"], connect_pts)
        pygame.draw.polygon(s, (*theme["accent"], 150), connect_pts, 1)
        
        # 折痕线
        pygame.draw.line(s, theme["core"],
                        (int(mid_x - 6), int(mid_y)),
                        (int(mid_x + 6), int(mid_y)), 1)
    
    # === 折纸尾羽 ===
    tail_x, tail_y, _ = positions[-1]
    _draw_crimson_tail(s, tail_x, tail_y + spacing * 0.6, t, theme)
    
    # === 千纸鹤翼 ===
    head_x, head_y, _ = positions[0]
    _draw_crimson_wings(s, head_x, head_y, w, h, t, theme)


def _draw_crimson_head(s, cx, cy, size, t, theme):
    """折纸涂装 - 头部：蛇首折纸"""
    # 三角形蛇头
    head_w = size * 0.4
    head_h = size * 0.5
    
    head_pts = [
        (cx + head_w, cy),           # 蛇嘴尖
        (cx - head_w * 0.3, cy - head_h * 0.4),
        (cx - head_w * 0.5, cy),
        (cx - head_w * 0.3, cy + head_h * 0.4)
    ]
    pygame.draw.polygon(s, theme["body"], head_pts)
    pygame.draw.polygon(s, theme["accent"], head_pts, 1)
    
    # 折痕
    pygame.draw.line(s, theme["core"],
                    (int(cx + head_w), int(cy)),
                    (int(cx - head_w * 0.5), int(cy)), 1)
    
    # 眼睛 - 三角形
    for side in [-1, 1]:
        eye_x = cx
        eye_y = cy + side * head_h * 0.2
        
        eye_pts = [
            (eye_x - 3, eye_y),
            (eye_x + 3, eye_y - side * 2),
            (eye_x + 3, eye_y + side * 2)
        ]
        pygame.draw.polygon(s, theme["core"], eye_pts)
    
    # 分叉舌
    tongue_wave = math.sin(t * 0.15) * 3
    tongue_pts = [
        (cx + head_w, cy),
        (cx + head_w + 8, cy - 3 + tongue_wave),
        (cx + head_w + 5, cy),
        (cx + head_w + 8, cy + 3 + tongue_wave)
    ]
    pygame.draw.lines(s, theme["core"], False, 
                     [(int(p[0]), int(p[1])) for p in tongue_pts], 1)


def _draw_crimson_tail(s, cx, cy, t, theme):
    """折纸涂装 - 尾部：扇形尾羽"""
    # 扇形展开
    fan_count = 5
    fan_len = 15
    
    for i in range(fan_count):
        angle = (i - 2) * 0.2 + math.sin(t * 0.08) * 0.1
        wave = math.sin(t * 0.1 + i * 0.5) * 2
        
        end_x = cx + math.sin(angle) * fan_len
        end_y = cy + math.cos(angle) * fan_len + abs(i - 2) * 2
        
        # 扇骨
        pygame.draw.line(s, theme["accent"],
                        (int(cx), int(cy)), (int(end_x), int(end_y)), 2)
        
        # 扇面三角
        if i < fan_count - 1:
            next_angle = ((i + 1) - 2) * 0.2 + math.sin(t * 0.08) * 0.1
            next_x = cx + math.sin(next_angle) * fan_len
            next_y = cy + math.cos(next_angle) * fan_len + abs((i + 1) - 2) * 2
            
            fan_pts = [
                (cx, cy),
                (end_x, end_y),
                (next_x, next_y)
            ]
            pygame.draw.polygon(s, (*theme["body"], 150), fan_pts)
            pygame.draw.polygon(s, (*theme["accent"], 100), fan_pts, 1)


def _draw_crimson_wings(s, cx, cy, w, h, t, theme):
    """折纸涂装 - 千纸鹤翼"""
    wing_span = int(w * 0.45)
    
    for side in [-1, 1]:
        base_x = cx + side * 8
        
        # 纸鹤翼形
        wing_wave = math.sin(t * 0.1) * 5
        
        # 主翼三角
        wing_pts = [
            (base_x, cy),
            (base_x + side * wing_span, cy - 10 + wing_wave),
            (base_x + side * wing_span * 0.7, cy + 5)
        ]
        pygame.draw.polygon(s, theme["body"], wing_pts)
        
        # 翼折痕
        pygame.draw.line(s, theme["core"],
                        (int(base_x), int(cy)),
                        (int(base_x + side * wing_span * 0.85), int(cy - 5 + wing_wave * 0.5)), 1)
        
        # 翼尖
        tip_pts = [
            (base_x + side * wing_span, cy - 10 + wing_wave),
            (base_x + side * (wing_span + 8), cy - 15 + wing_wave),
            (base_x + side * wing_span * 0.95, cy - 5 + wing_wave)
        ]
        pygame.draw.polygon(s, theme["armor"], tip_pts)
        
        # 边缘
        pygame.draw.polygon(s, theme["accent"], wing_pts, 1)
        
        # 装饰 - 小鹤
        crane_x = base_x + side * wing_span * 0.5
        crane_y = cy - 3
        _draw_mini_crane(s, crane_x, crane_y, 6, theme)


def _draw_mini_crane(s, cx, cy, size, theme):
    """绘制迷你纸鹤"""
    # 身体
    body_pts = [
        (cx - size, cy),
        (cx, cy - size * 0.5),
        (cx + size, cy),
        (cx, cy + size * 0.5)
    ]
    pygame.draw.polygon(s, theme["core"], body_pts)
    
    # 翅膀
    pygame.draw.line(s, theme["accent"],
                    (int(cx), int(cy)),
                    (int(cx - size * 0.8), int(cy - size * 0.8)), 1)
    pygame.draw.line(s, theme["accent"],
                    (int(cx), int(cy)),
                    (int(cx + size * 0.8), int(cy - size * 0.8)), 1)


# =============================================================================
#   [系列四：终极幻想] - 精细化独立绘制函数
# =============================================================================

def draw_oro_void(s, cx, cy, w, h, t):
    """
    视界线·虚空 - 暗物质蠕虫
    特点：纯黑菱形节段 + 脉冲发光边缘 + 吸积盘尾 + 事件视界翼
    """
    theme = get_oro_theme("oro_void")
    seg_count = 6
    base_size = min(w, h) * 0.36
    spacing = h * 0.12
    positions = []
    
    # === 绘制虚空节段 ===
    for i in range(seg_count):
        wave = math.sin(t * 0.08 + i * 0.5) * (3 + i * 0.4)
        seg_y = cy - h * 0.28 + i * spacing
        seg_x = cx + wave
        seg_size = base_size * (1.0 - i * 0.08)
        positions.append((seg_x, seg_y, seg_size))
        
        # 菱形虚空体
        diamond_w = seg_size * 0.55
        diamond_h = seg_size * 0.35
        
        pts = [
            (seg_x, seg_y - diamond_h),
            (seg_x + diamond_w, seg_y),
            (seg_x, seg_y + diamond_h),
            (seg_x - diamond_w, seg_y)
        ]
        
        # 纯黑核心
        pygame.draw.polygon(s, theme["body"], pts)
        
        # 脉冲发光边缘
        pulse = 0.3 + 0.7 * abs(math.sin(t * 0.1 + i * 0.4))
        glow_width = int(2 + pulse * 3)
        glow_color = tuple(int(c * pulse) for c in theme["glow"])
        
        # 多层光晕
        for glow_layer in range(3):
            glow_alpha = int((150 - glow_layer * 40) * pulse)
            layer_pts = [
                (seg_x, seg_y - diamond_h - glow_layer * 2),
                (seg_x + diamond_w + glow_layer * 2, seg_y),
                (seg_x, seg_y + diamond_h + glow_layer * 2),
                (seg_x - diamond_w - glow_layer * 2, seg_y)
            ]
            pygame.draw.polygon(s, (*theme["glow"], glow_alpha), layer_pts, 1)
        
        # 中心奇点 - 绝对黑暗
        void_r = int(seg_size * 0.12)
        pygame.draw.circle(s, (0, 0, 0), (int(seg_x), int(seg_y)), void_r)
        
        # 奇点光环
        ring_pulse = 0.5 + 0.5 * math.sin(t * 0.15 + i)
        pygame.draw.circle(s, (*theme["energy"], int(150 * ring_pulse)),
                         (int(seg_x), int(seg_y)), void_r + 3, 1)
        
        # 扭曲效果 - 空间波纹
        for j in range(3):
            ripple_r = void_r + 5 + j * 4 + int(math.sin(t * 0.2 + j) * 2)
            ripple_alpha = int(60 - j * 15)
            pygame.draw.circle(s, (*theme["core"], ripple_alpha),
                             (int(seg_x), int(seg_y)), ripple_r, 1)
        
        # 头部
        if i == 0:
            _draw_void_head(s, seg_x, seg_y, seg_size, t, theme)
    
    # === 暗物质连接 ===
    for i in range(len(positions) - 1):
        x1, y1, s1 = positions[i]
        x2, y2, s2 = positions[i + 1]
        
        # 扭曲的暗物质流
        for strand in range(3):
            offset = (strand - 1) * 3
            wave_phase = t * 0.12 + strand * 0.7 + i
            
            # 曲线路径
            points = []
            for j in range(8):
                pt = j / 7
                px = x1 + (x2 - x1) * pt + offset + math.sin(wave_phase + pt * 3) * 3
                py = y1 + (y2 - y1) * pt
                points.append((int(px), int(py)))
            
            pygame.draw.lines(s, (*theme["glow"], 80), False, points, 1)
        
        # 湮灭粒子
        particle_t = (t * 0.18 + i * 0.4) % 1.0
        px = int(x1 + (x2 - x1) * particle_t)
        py = int(y1 + (y2 - y1) * particle_t)
        pygame.draw.circle(s, theme["energy"], (px, py), 3)
        pygame.draw.circle(s, (*theme["accent"], 100), (px, py), 5, 1)
    
    # === 吸积盘尾 ===
    tail_x, tail_y, _ = positions[-1]
    _draw_void_tail(s, tail_x, tail_y + spacing * 0.6, t, theme)
    
    # === 事件视界翼 ===
    head_x, head_y, _ = positions[0]
    _draw_void_wings(s, head_x, head_y, w, h, t, theme)


def _draw_void_head(s, cx, cy, size, t, theme):
    """虚空涂装 - 头部：深渊之眼"""
    # 单一巨眼 - 虚空凝视
    eye_r = size * 0.25
    
    # 眼眶深渊
    pygame.draw.circle(s, (0, 0, 0), (int(cx), int(cy)), int(eye_r) + 3)
    
    # 虹膜环
    for ring in range(3):
        ring_r = eye_r - ring * 3
        ring_alpha = int(100 + ring * 30)
        pygame.draw.circle(s, (*theme["glow"], ring_alpha),
                         (int(cx), int(cy)), int(ring_r), 1)
    
    # 瞳孔 - 绝对虚空
    pygame.draw.circle(s, (0, 0, 0), (int(cx), int(cy)), int(eye_r * 0.4))
    
    # 视线光芒 - 辐射状
    for i in range(8):
        angle = t * 0.05 + i * math.pi / 4
        ray_len = eye_r + 10 + math.sin(t * 0.15 + i) * 5
        
        ex = cx + math.cos(angle) * ray_len
        ey = cy + math.sin(angle) * ray_len
        
        pygame.draw.line(s, (*theme["energy"], 80),
                        (int(cx + math.cos(angle) * eye_r), int(cy + math.sin(angle) * eye_r)),
                        (int(ex), int(ey)), 1)
    
    # 前方虚空触手
    for i in range(3):
        tendril_y = cy + (i - 1) * 8
        tendril_wave = math.sin(t * 0.12 + i) * 4
        
        pygame.draw.line(s, theme["glow"],
                        (int(cx + size * 0.3), int(tendril_y)),
                        (int(cx + size * 0.5 + tendril_wave), int(tendril_y + tendril_wave * 0.5)), 2)


def _draw_void_tail(s, cx, cy, t, theme):
    """虚空涂装 - 尾部：微型吸积盘"""
    # 吸积盘环
    for ring in range(4):
        ring_r = 8 + ring * 5
        ring_alpha = int(100 - ring * 20)
        
        # 椭圆吸积盘
        ellipse_w = ring_r * 2
        ellipse_h = ring_r * 0.6
        
        # 旋转效果
        rotation = t * 0.1 + ring * 0.3
        
        # 绘制旋转的粒子
        for i in range(8):
            angle = rotation + i * math.pi / 4
            px = cx + math.cos(angle) * ring_r
            py = cy + math.sin(angle) * ring_r * 0.3 + ring * 2
            
            pygame.draw.circle(s, (*theme["glow"], ring_alpha), (int(px), int(py)), 2)
    
    # 中心黑洞
    pygame.draw.circle(s, (0, 0, 0), (int(cx), int(cy)), 5)
    pygame.draw.circle(s, theme["energy"], (int(cx), int(cy)), 7, 1)
    
    # 喷流
    for side in [-1, 1]:
        for i in range(4):
            jet_y = cy + 10 + i * 4
            jet_x = cx + side * (3 + i * 0.5)
            jet_alpha = int(120 - i * 25)
            pygame.draw.circle(s, (*theme["accent"], jet_alpha), 
                             (int(jet_x), int(jet_y)), 2)


def _draw_void_wings(s, cx, cy, w, h, t, theme):
    """虚空涂装 - 事件视界翼"""
    wing_span = int(w * 0.42)
    
    for side in [-1, 1]:
        base_x = cx + side * 10
        
        # 扭曲的空间翼
        wing_pts = []
        for i in range(8):
            angle = side * (0.3 + i * 0.08)
            dist = wing_span * (0.3 + i * 0.1)
            wave = math.sin(t * 0.1 + i * 0.5) * 5
            
            wx = base_x + side * dist + wave
            wy = cy - 15 + i * 5
            wing_pts.append((wx, wy))
        
        # 翼膜 - 渐变透明
        if len(wing_pts) >= 3:
            # 填充
            full_pts = [(base_x, cy - 10)] + wing_pts + [(base_x, cy + 20)]
            pygame.draw.polygon(s, (*theme["body"], 60), full_pts)
            
            # 发光边缘
            pulse = 0.5 + 0.5 * math.sin(t * 0.12)
            pygame.draw.lines(s, (*theme["glow"], int(150 * pulse)), False,
                            [(int(p[0]), int(p[1])) for p in wing_pts], 2)
        
        # 空间裂隙
        for i in range(3):
            crack_x = base_x + side * (10 + i * 12)
            crack_y = cy + (i - 1) * 8
            crack_len = 8 + math.sin(t * 0.15 + i) * 3
            
            pygame.draw.line(s, (*theme["energy"], 100),
                           (int(crack_x), int(crack_y - crack_len)),
                           (int(crack_x), int(crack_y + crack_len)), 1)


def draw_oro_abyss(s, cx, cy, w, h, t):
    """
    机械降神·齿轮 - 蒸汽朋克蠕虫
    特点：八边形齿轮节段 + 铜管连接 + 蒸汽喷射 + 机械翼
    """
    theme = get_oro_theme("oro_abyss")
    seg_count = 5
    base_size = min(w, h) * 0.4
    spacing = h * 0.14
    positions = []
    
    # === 绘制齿轮节段 ===
    for i in range(seg_count):
        wave = math.sin(t * 0.06 + i * 0.4) * (2 + i * 0.3)
        seg_y = cy - h * 0.25 + i * spacing
        seg_x = cx + wave
        seg_size = base_size * (1.0 - i * 0.1)
        positions.append((seg_x, seg_y, seg_size))
        
        # 八边形齿轮
        gear_r = seg_size * 0.45
        tooth_count = 8
        
        # 齿轮主体点
        gear_pts = []
        for j in range(tooth_count * 2):
            angle = j * math.pi / tooth_count - math.pi / 2 + t * 0.02  # 缓慢旋转
            
            # 交替齿顶和齿根
            if j % 2 == 0:
                r = gear_r
            else:
                r = gear_r * 0.8
            
            gx = seg_x + math.cos(angle) * r
            gy = seg_y + math.sin(angle) * r * 0.7
            gear_pts.append((gx, gy))
        
        # 齿轮外壳
        pygame.draw.polygon(s, theme["body"], gear_pts)
        pygame.draw.polygon(s, theme["core"], gear_pts, 2)
        
        # 齿轮内环
        inner_r = gear_r * 0.5
        pygame.draw.circle(s, theme["armor"], (int(seg_x), int(seg_y)), int(inner_r))
        pygame.draw.circle(s, theme["core"], (int(seg_x), int(seg_y)), int(inner_r), 2)
        
        # 中心轴孔
        pygame.draw.circle(s, theme["body"], (int(seg_x), int(seg_y)), int(inner_r * 0.4))
        pygame.draw.circle(s, theme["glow"], (int(seg_x), int(seg_y)), int(inner_r * 0.4), 1)
        
        # 辐条
        for j in range(4):
            spoke_angle = j * math.pi / 2 + t * 0.02
            inner_x = seg_x + math.cos(spoke_angle) * inner_r * 0.5
            inner_y = seg_y + math.sin(spoke_angle) * inner_r * 0.5 * 0.7
            outer_x = seg_x + math.cos(spoke_angle) * gear_r * 0.75
            outer_y = seg_y + math.sin(spoke_angle) * gear_r * 0.75 * 0.7
            
            pygame.draw.line(s, theme["core"],
                           (int(inner_x), int(inner_y)),
                           (int(outer_x), int(outer_y)), 2)
        
        # 铆钉装饰
        for j in range(tooth_count):
            rivet_angle = j * math.pi * 2 / tooth_count + t * 0.02
            rivet_r = gear_r * 0.65
            rx = seg_x + math.cos(rivet_angle) * rivet_r
            ry = seg_y + math.sin(rivet_angle) * rivet_r * 0.7
            
            pygame.draw.circle(s, theme["accent"], (int(rx), int(ry)), 3)
            pygame.draw.circle(s, theme["core"], (int(rx), int(ry)), 3, 1)
        
        # 蒸汽泄漏
        if random.random() > 0.85:
            steam_x = seg_x + random.randint(-int(gear_r), int(gear_r))
            steam_y = seg_y + random.randint(-5, 5)
            pygame.draw.circle(s, (*theme["energy"], 100), (int(steam_x), int(steam_y)), 3)
        
        # 头部
        if i == 0:
            _draw_abyss_head(s, seg_x, seg_y, seg_size, t, theme)
    
    # === 铜管连接 ===
    for i in range(len(positions) - 1):
        x1, y1, s1 = positions[i]
        x2, y2, s2 = positions[i + 1]
        
        # 三根铜管
        for pipe in range(3):
            offset = (pipe - 1) * 10
            
            # 铜管主体
            pygame.draw.line(s, theme["body"],
                           (int(x1 + offset), int(y1 + s1 * 0.2)),
                           (int(x2 + offset), int(y2 - s2 * 0.2)), 5)
            pygame.draw.line(s, theme["core"],
                           (int(x1 + offset), int(y1 + s1 * 0.2)),
                           (int(x2 + offset), int(y2 - s2 * 0.2)), 5)
            
            # 管道接头
            mid_y = (y1 + y2) / 2
            pygame.draw.circle(s, theme["accent"], 
                             (int(x1 + offset + (x2 - x1) * 0.5), int(mid_y)), 4)
        
        # 蒸汽喷射
        steam_t = (t * 0.15 + i * 0.5) % 1.0
        if steam_t < 0.3:
            sx = x1 + (x2 - x1) * 0.5
            sy = y1 + (y2 - y1) * 0.5
            for j in range(3):
                pygame.draw.circle(s, (*theme["energy"], 150 - j * 40),
                                 (int(sx + random.randint(-5, 5)), 
                                  int(sy + j * 4)), 3 - j)
    
    # === 排气尾管 ===
    tail_x, tail_y, tail_s = positions[-1]
    _draw_abyss_tail(s, tail_x, tail_y + tail_s * 0.35, t, theme)
    
    # === 机械翼 ===
    head_x, head_y, _ = positions[0]
    _draw_abyss_wings(s, head_x, head_y, w, h, t, theme)


def _draw_abyss_head(s, cx, cy, size, t, theme):
    """齿轮涂装 - 头部：机械蛇首"""
    # 机械眼罩
    visor_w = size * 0.5
    visor_h = size * 0.25
    
    visor_pts = [
        (cx - visor_w * 0.3, cy - visor_h),
        (cx + visor_w, cy - visor_h * 0.5),
        (cx + visor_w, cy + visor_h * 0.5),
        (cx - visor_w * 0.3, cy + visor_h)
    ]
    pygame.draw.polygon(s, theme["body"], visor_pts)
    pygame.draw.polygon(s, theme["core"], visor_pts, 2)
    
    # 透镜眼
    for side in [-1, 1]:
        eye_x = cx + visor_w * 0.3
        eye_y = cy + side * visor_h * 0.3
        
        # 透镜
        pygame.draw.circle(s, theme["glow"], (int(eye_x), int(eye_y)), 5)
        pygame.draw.circle(s, theme["accent"], (int(eye_x), int(eye_y)), 3)
        pygame.draw.circle(s, theme["core"], (int(eye_x), int(eye_y)), 5, 1)
    
    # 机械颚
    jaw_open = 3 + math.sin(t * 0.1) * 2
    
    for side in [-1, 1]:
        jaw_y = cy + side * (visor_h + jaw_open)
        
        # 颚板
        jaw_pts = [
            (cx + visor_w * 0.5, jaw_y - side * 3),
            (cx + visor_w + 10, jaw_y),
            (cx + visor_w + 5, jaw_y + side * 4),
            (cx + visor_w * 0.3, jaw_y + side * 2)
        ]
        pygame.draw.polygon(s, theme["armor"], jaw_pts)
        pygame.draw.polygon(s, theme["core"], jaw_pts, 1)
        
        # 齿轮牙
        for j in range(2):
            tooth_x = cx + visor_w * 0.6 + j * 8
            pygame.draw.circle(s, theme["accent"], 
                             (int(tooth_x), int(jaw_y + side * 2)), 2)


def _draw_abyss_tail(s, cx, cy, t, theme):
    """齿轮涂装 - 尾部：排气管"""
    # 三联排气管
    for i, offset in enumerate([-12, 0, 12]):
        pipe_x = cx + offset
        pipe_y = cy
        
        # 管道
        pygame.draw.ellipse(s, theme["body"], 
                          (pipe_x - 5, pipe_y - 3, 10, 18))
        pygame.draw.ellipse(s, theme["core"],
                          (pipe_x - 5, pipe_y - 3, 10, 18), 2)
        
        # 排气口
        pygame.draw.ellipse(s, theme["armor"],
                          (pipe_x - 3, pipe_y + 8, 6, 4))
        
        # 蒸汽喷射
        steam_phase = (t * 0.2 + i * 0.3) % 1.0
        if steam_phase < 0.5:
            for j in range(4):
                steam_y = pipe_y + 15 + j * 4
                steam_alpha = int(150 - j * 35)
                steam_size = 4 - j
                pygame.draw.circle(s, (*theme["energy"], steam_alpha),
                                 (int(pipe_x + math.sin(t * 0.3 + j) * 3), 
                                  int(steam_y)), steam_size)


def _draw_abyss_wings(s, cx, cy, w, h, t, theme):
    """齿轮涂装 - 机械翼：铰接结构"""
    wing_span = int(w * 0.4)
    
    for side in [-1, 1]:
        base_x = cx + side * 12
        
        # 机械臂骨架
        joints = [(base_x, cy)]
        
        for i in range(3):
            joint_len = (wing_span // 3) * (1 - i * 0.1)
            joint_angle = side * (0.3 + i * 0.1) + math.sin(t * 0.08 + i) * 0.1
            
            prev_x, prev_y = joints[-1]
            jx = prev_x + side * joint_len
            jy = prev_y - 5 + i * 8
            joints.append((jx, jy))
            
            # 机械臂
            pygame.draw.line(s, theme["body"],
                           (int(prev_x), int(prev_y)),
                           (int(jx), int(jy)), 4)
            pygame.draw.line(s, theme["core"],
                           (int(prev_x), int(prev_y)),
                           (int(jx), int(jy)), 4)
        
        # 关节铰链
        for jx, jy in joints:
            pygame.draw.circle(s, theme["accent"], (int(jx), int(jy)), 4)
            pygame.draw.circle(s, theme["core"], (int(jx), int(jy)), 4, 1)
        
        # 翼膜（金属板）
        if len(joints) >= 3:
            membrane_pts = [joints[0], joints[1], joints[2], 
                          (joints[2][0], joints[2][1] + 15),
                          (joints[1][0], joints[1][1] + 10)]
            pygame.draw.polygon(s, (*theme["armor"], 100), membrane_pts)
            pygame.draw.polygon(s, (*theme["core"], 150), membrane_pts, 1)


def draw_oro_blood(s, cx, cy, w, h, t):
    """
    数据删除·终焉 - 故障崩溃蠕虫
    特点：随机位移节段 + 故障条纹 + 数据碎片 + 崩溃翼
    """
    theme = get_oro_theme("oro_blood")
    seg_count = 6
    base_size = min(w, h) * 0.36
    spacing = h * 0.12
    positions = []
    
    # 故障偏移种子
    glitch_seed = int(t * 10) % 100
    
    # === 绘制故障节段 ===
    for i in range(seg_count):
        wave = math.sin(t * 0.1 + i * 0.5) * (3 + i * 0.5)
        
        # 随机故障位移
        glitch_x = random.randint(-4, 4) if random.random() > 0.7 else 0
        glitch_y = random.randint(-2, 2) if random.random() > 0.8 else 0
        
        seg_y = cy - h * 0.28 + i * spacing + glitch_y
        seg_x = cx + wave + glitch_x
        seg_size = base_size * (1.0 - i * 0.08)
        positions.append((seg_x, seg_y, seg_size))
        
        # 矩形节段
        rect_w = int(seg_size * 1.0)
        rect_h = int(seg_size * 0.6)
        
        # 故障色块分裂
        split_offset = random.randint(-3, 3) if random.random() > 0.6 else 0
        
        # 主体白色
        rect = pygame.Rect(seg_x - rect_w//2, seg_y - rect_h//2, rect_w, rect_h)
        pygame.draw.rect(s, theme["body"], rect)
        
        # 青色偏移层
        if split_offset != 0:
            cyan_rect = rect.move(split_offset, 0)
            pygame.draw.rect(s, (*theme["accent"], 100), cyan_rect)
        
        # 红色偏移层
        if split_offset != 0:
            red_rect = rect.move(-split_offset, 0)
            pygame.draw.rect(s, (*theme["core"], 80), red_rect)
        
        # 内核
        inner_rect = rect.inflate(-12, -8)
        if inner_rect.width > 0 and inner_rect.height > 0:
            pygame.draw.rect(s, theme["armor"], inner_rect)
        
        # 故障条纹
        stripe_count = random.randint(2, 5)
        for j in range(stripe_count):
            stripe_y = seg_y - rect_h//2 + random.randint(2, rect_h - 2)
            stripe_len = random.randint(rect_w // 4, rect_w)
            stripe_x = seg_x - rect_w//2 + random.randint(0, rect_w - stripe_len)
            
            stripe_color = theme["core"] if random.random() > 0.5 else theme["accent"]
            pygame.draw.line(s, stripe_color,
                           (int(stripe_x), int(stripe_y)),
                           (int(stripe_x + stripe_len), int(stripe_y)), 1)
        
        # 噪点
        for _ in range(random.randint(3, 8)):
            noise_x = seg_x + random.randint(-rect_w//2, rect_w//2)
            noise_y = seg_y + random.randint(-rect_h//2, rect_h//2)
            noise_color = random.choice([theme["core"], theme["accent"], theme["body"]])
            pygame.draw.rect(s, noise_color, (noise_x, noise_y, 2, 2))
        
        # 错误核心
        if random.random() > 0.3:
            error_pulse = 0.5 + 0.5 * math.sin(t * 0.2 + i)
            pygame.draw.circle(s, (*theme["core"], int(200 * error_pulse)),
                             (int(seg_x), int(seg_y)), 5)
        
        # 头部
        if i == 0:
            _draw_blood_head(s, seg_x, seg_y, seg_size, t, theme)
    
    # === 断裂连接 ===
    for i in range(len(positions) - 1):
        x1, y1, s1 = positions[i]
        x2, y2, s2 = positions[i + 1]
        
        # 断断续续的连接
        segments = 6
        for j in range(segments):
            if random.random() > 0.3:  # 30%概率断开
                t1 = j / segments
                t2 = (j + 1) / segments
                
                px1 = x1 + (x2 - x1) * t1 + random.randint(-2, 2)
                py1 = y1 + (y2 - y1) * t1
                px2 = x1 + (x2 - x1) * t2 + random.randint(-2, 2)
                py2 = y1 + (y2 - y1) * t2
                
                color = theme["core"] if random.random() > 0.5 else theme["accent"]
                pygame.draw.line(s, color, (int(px1), int(py1)), (int(px2), int(py2)), 2)
        
        # 数据碎片
        for _ in range(random.randint(1, 3)):
            frag_t = random.random()
            fx = x1 + (x2 - x1) * frag_t + random.randint(-8, 8)
            fy = y1 + (y2 - y1) * frag_t + random.randint(-5, 5)
            frag_size = random.randint(2, 5)
            
            pygame.draw.rect(s, random.choice([theme["core"], theme["accent"]]),
                           (fx, fy, frag_size, frag_size // 2))
    
    # === 崩溃尾迹 ===
    tail_x, tail_y, _ = positions[-1]
    _draw_blood_tail(s, tail_x, tail_y + spacing * 0.6, t, theme)
    
    # === 碎裂翼 ===
    head_x, head_y, _ = positions[0]
    _draw_blood_wings(s, head_x, head_y, w, h, t, theme)


def _draw_blood_head(s, cx, cy, size, t, theme):
    """故障涂装 - 头部：错误眼"""
    # 故障眼
    for side in [-1, 1]:
        eye_x = cx + side * size * 0.25 + random.randint(-2, 2)
        eye_y = cy - size * 0.1 + random.randint(-1, 1)
        
        # 眼眶故障
        pygame.draw.rect(s, theme["body"], (eye_x - 5, eye_y - 4, 10, 8))
        
        # 错误符号
        if random.random() > 0.5:
            pygame.draw.line(s, theme["core"],
                           (int(eye_x - 3), int(eye_y - 2)),
                           (int(eye_x + 3), int(eye_y + 2)), 2)
            pygame.draw.line(s, theme["core"],
                           (int(eye_x + 3), int(eye_y - 2)),
                           (int(eye_x - 3), int(eye_y + 2)), 2)
        else:
            pygame.draw.circle(s, theme["accent"], (int(eye_x), int(eye_y)), 3)
    
    # 故障触角
    for i in range(3):
        ant_x = cx + 15 + i * 8
        ant_y = cy + random.randint(-5, 5)
        ant_len = 10 + random.randint(-3, 3)
        
        if random.random() > 0.4:
            pygame.draw.line(s, theme["core"] if random.random() > 0.5 else theme["accent"],
                           (int(ant_x), int(ant_y)),
                           (int(ant_x + ant_len), int(ant_y + random.randint(-3, 3))), 2)


def _draw_blood_tail(s, cx, cy, t, theme):
    """故障涂装 - 尾部：数据崩溃"""
    # 崩溃粒子流
    for i in range(12):
        particle_y = cy + i * 3
        particle_x = cx + math.sin(t * 0.3 + i) * 10 + random.randint(-5, 5)
        
        # 逐渐消散
        alpha = int(200 - i * 15)
        size = max(1, 4 - i // 3)
        
        color = theme["core"] if i % 3 == 0 else theme["accent"] if i % 3 == 1 else theme["body"]
        pygame.draw.rect(s, (*color, alpha), 
                        (particle_x - size//2, particle_y, size, size))
    
    # 错误代码
    for i in range(3):
        code_x = cx + random.randint(-15, 15)
        code_y = cy + 35 + i * 4
        code_len = random.randint(5, 15)
        
        for j in range(code_len):
            if random.random() > 0.3:
                pygame.draw.rect(s, (*theme["accent"], 100 - i * 25),
                               (code_x + j * 2, code_y, 1, 3))


def _draw_blood_wings(s, cx, cy, w, h, t, theme):
    """故障涂装 - 碎裂翼"""
    wing_span = int(w * 0.4)
    
    for side in [-1, 1]:
        base_x = cx + side * 10
        
        # 碎裂的翼片
        for i in range(5):
            frag_x = base_x + side * (5 + i * 10) + random.randint(-3, 3)
            frag_y = cy - 10 + i * 8 + random.randint(-2, 2)
            frag_w = random.randint(8, 15)
            frag_h = random.randint(4, 8)
            
            # 碎片
            if random.random() > 0.2:
                frag_color = random.choice([theme["body"], theme["armor"]])
                pygame.draw.rect(s, frag_color, (frag_x, frag_y, frag_w, frag_h))
                
                # 故障边缘
                edge_color = theme["core"] if random.random() > 0.5 else theme["accent"]
                pygame.draw.rect(s, edge_color, (frag_x, frag_y, frag_w, frag_h), 1)
        
        # 数据流
        for i in range(3):
            stream_x = base_x + side * (wing_span * 0.5)
            stream_y = cy + (i - 1) * 10
            
            for j in range(4):
                if random.random() > 0.4:
                    px = stream_x + side * j * 5 + random.randint(-2, 2)
                    py = stream_y + random.randint(-2, 2)
                    pygame.draw.rect(s, theme["accent"], (px, py, 2, 2))


# =============================================================================
#   公共接口 - 调度器
# =============================================================================

# 涂装绘制函数映射
_ORO_RENDERERS = {
    "oro_default": draw_oro_default,
    "oro_phantom": draw_oro_phantom,
    "oro_golden": draw_oro_golden,
    "oro_inferno": draw_oro_inferno,
    "oro_frost": draw_oro_frost,
    "oro_toxic": draw_oro_toxic,
    "oro_cosmic": draw_oro_cosmic,
    "oro_royal": draw_oro_royal,
    "oro_crimson": draw_oro_crimson,
    "oro_void": draw_oro_void,
    "oro_abyss": draw_oro_abyss,
    "oro_blood": draw_oro_blood,
}


def draw_oro(surface, color, x, y, w, h, frame=0, style="oro_default"):
    """
    绘制终噬星链·奥罗
    
    Args:
        surface: pygame Surface
        color: 基础颜色（未使用，保持接口兼容）
        x, y: 左上角坐标
        w, h: 尺寸
        frame: 动画帧数
        style: 涂装样式名
    """
    cx = x + w // 2
    cy = y + h // 2
    t = frame * 0.06  # 转换为时间参数
    
    # 获取对应的绘制函数
    draw_func = _ORO_RENDERERS.get(style, draw_oro_default)
    draw_func(surface, cx, cy, w, h, t)


def render_oro_skin(surface, color, model_style, t, pid, static):
    """渲染奥罗涂装入口"""
    if not is_oro_style(model_style):
        return None
    frame = int(t * 60) if not static else 0
    draw_oro(surface, color, 10, 10, 100, 100, frame, model_style)
    return surface
