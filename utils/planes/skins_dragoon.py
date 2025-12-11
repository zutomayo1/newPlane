# -*- coding: utf-8 -*-
"""
Dragoon 龙骑士·雷因哈特 机体涂装渲染模块

设计理念：
- 核心元素：骑士精神、龙枪冲锋、荣耀铠甲
- 机体形态：重装骑士造型，长枪与盾牌
- 视觉效果：蓝银主色调，金色装饰，雷电特效
"""
import pygame
import math

# Dragoon 涂装样式列表
DRAGOON_STYLES = [
    "dragoon_base",       # 基础形态 - 蓝银骑士
    "dragoon_knight",     # 白银骑士 - 全银甲
    "dragoon_azure",      # 苍蓝 - 深蓝风暴
    "dragoon_silver",     # 白银 - 纯银圣骑
    "dragoon_storm",      # 风暴 - 雷电骑士
    "dragoon_ancient",    # 远古 - 古龙遗迹
    "dragoon_dragon",     # 真龙 - 龙化形态
    "dragoon_royal",      # 皇家 - 金红王者
    "dragoon_valkyrie",   # 瓦尔基里 - 战争女神
    "dragoon_divine",     # 神圣 - 圣光骑士
]


def is_dragoon_style(model_style):
    """检查是否为 Dragoon 涂装样式"""
    return model_style in DRAGOON_STYLES


def render_dragoon_skin(s, c, model_style, t, pid, static):
    """渲染 Dragoon 专属涂装"""
    if not is_dragoon_style(model_style):
        return None
    
    pulse = 0 if static else abs(math.sin(t * 3))
    
    if model_style == "dragoon_base":
        _render_dragoon_base(s, t, pulse)
    elif model_style == "dragoon_knight":
        _render_dragoon_knight(s, t, pulse)
    elif model_style == "dragoon_azure":
        _render_dragoon_azure(s, t, pulse)
    elif model_style == "dragoon_silver":
        _render_dragoon_silver(s, t, pulse)
    elif model_style == "dragoon_storm":
        _render_dragoon_storm(s, t, pulse)
    elif model_style == "dragoon_ancient":
        _render_dragoon_ancient(s, t, pulse)
    elif model_style == "dragoon_dragon":
        _render_dragoon_dragon(s, t, pulse)
    elif model_style == "dragoon_royal":
        _render_dragoon_royal(s, t, pulse)
    elif model_style == "dragoon_valkyrie":
        _render_dragoon_valkyrie(s, t, pulse)
    elif model_style == "dragoon_divine":
        _render_dragoon_divine(s, t, pulse)
    else:
        _render_dragoon_base(s, t, pulse)
    
    return s


def _render_dragoon_base(surface, t, pulse, visual=None):
    """基础形态 - 蓝银骑士：经典龙骑士造型"""
    cx, cy = 60, 60
    
    # 能量护盾圈
    shield_r = int(45 + 4 * pulse)
    pygame.draw.circle(surface, (80, 120, 180), (cx, cy), shield_r, 2)
    
    # 主体装甲（梯形身体）
    body_pts = [
        (cx, cy - 30),       # 头顶
        (cx - 20, cy + 5),   # 左肩
        (cx - 18, cy + 25),  # 左下
        (cx + 18, cy + 25),  # 右下
        (cx + 20, cy + 5),   # 右肩
    ]
    pygame.draw.polygon(surface, (50, 70, 100), body_pts)
    pygame.draw.polygon(surface, (100, 150, 200), body_pts, 2)
    
    # 头盔（骑士头盔）
    helmet_pts = [
        (cx, cy - 35),       # 头盔顶
        (cx - 12, cy - 20),  # 左
        (cx - 10, cy - 10),  # 左下
        (cx + 10, cy - 10),  # 右下
        (cx + 12, cy - 20),  # 右
    ]
    pygame.draw.polygon(surface, (60, 80, 110), helmet_pts)
    pygame.draw.polygon(surface, (120, 160, 200), helmet_pts, 2)
    
    # 面甲缝隙（T字形）
    pygame.draw.line(surface, (150, 200, 255), (cx - 6, cy - 22), (cx + 6, cy - 22), 2)
    pygame.draw.line(surface, (150, 200, 255), (cx, cy - 22), (cx, cy - 15), 2)
    
    # 龙枪（长枪朝前）
    lance_tip_y = cy - 55
    lance_base_y = cy + 20
    # 枪身
    pygame.draw.line(surface, (80, 100, 130), (cx, lance_base_y), (cx, lance_tip_y + 15), 4)
    pygame.draw.line(surface, (150, 180, 210), (cx, lance_base_y), (cx, lance_tip_y + 15), 2)
    # 枪头
    lance_pts = [
        (cx, lance_tip_y),
        (cx - 8, lance_tip_y + 15),
        (cx, lance_tip_y + 10),
        (cx + 8, lance_tip_y + 15),
    ]
    pygame.draw.polygon(surface, (180, 200, 230), lance_pts)
    pygame.draw.polygon(surface, (220, 240, 255), lance_pts, 1)
    
    # 盾牌（左侧）
    shield_pts = [
        (cx - 32, cy - 10),
        (cx - 38, cy),
        (cx - 38, cy + 15),
        (cx - 32, cy + 25),
        (cx - 25, cy + 15),
        (cx - 25, cy),
    ]
    pygame.draw.polygon(surface, (70, 90, 120), shield_pts)
    pygame.draw.polygon(surface, (140, 170, 210), shield_pts, 2)
    # 盾牌纹章
    pygame.draw.circle(surface, (100, 140, 190), (cx - 32, cy + 8), 5)
    
    # 肩甲装饰
    for side in [-1, 1]:
        shoulder_x = cx + side * 22
        pygame.draw.circle(surface, (80, 110, 150), (shoulder_x, cy), 8)
        pygame.draw.circle(surface, (140, 180, 220), (shoulder_x, cy), 8, 2)
    
    # 核心能量
    pygame.draw.circle(surface, (120, 180, 255), (cx, cy + 5), int(6 + 2 * pulse))
    pygame.draw.circle(surface, (200, 230, 255), (cx, cy + 5), 3)


def _render_dragoon_knight(surface, t, pulse, visual=None):
    """白银骑士 - 全银甲：全身银色重甲"""
    cx, cy = 60, 60
    
    # 银光光环
    for ring in range(3):
        r = 40 + ring * 8 + int(3 * pulse)
        silver = 180 + ring * 20
        pygame.draw.circle(surface, (silver, silver, silver + 10), (cx, cy), r, 2)
    
    # 银甲主体（更厚重）
    body_pts = [
        (cx, cy - 28),
        (cx - 25, cy + 5),
        (cx - 22, cy + 28),
        (cx + 22, cy + 28),
        (cx + 25, cy + 5),
    ]
    pygame.draw.polygon(surface, (160, 170, 180), body_pts)
    pygame.draw.polygon(surface, (220, 230, 240), body_pts, 2)
    
    # 银色头盔（全封闭）
    pygame.draw.ellipse(surface, (180, 190, 200), (cx - 15, cy - 35, 30, 28))
    pygame.draw.ellipse(surface, (220, 230, 240), (cx - 15, cy - 35, 30, 28), 2)
    # 面甲横缝
    pygame.draw.line(surface, (240, 245, 255), (cx - 8, cy - 22), (cx + 8, cy - 22), 3)
    
    # 银枪
    lance_tip_y = cy - 58
    pygame.draw.line(surface, (200, 210, 220), (cx + 5, cy + 20), (cx + 5, lance_tip_y + 12), 5)
    pygame.draw.line(surface, (240, 245, 255), (cx + 5, cy + 20), (cx + 5, lance_tip_y + 12), 2)
    # 枪头
    lance_pts = [
        (cx + 5, lance_tip_y),
        (cx - 5, lance_tip_y + 15),
        (cx + 5, lance_tip_y + 8),
        (cx + 15, lance_tip_y + 15),
    ]
    pygame.draw.polygon(surface, (220, 230, 240), lance_pts)
    pygame.draw.polygon(surface, (255, 255, 255), lance_pts, 1)
    
    # 银盾（圆形）
    pygame.draw.circle(surface, (180, 190, 200), (cx - 28, cy + 5), 18)
    pygame.draw.circle(surface, (220, 230, 240), (cx - 28, cy + 5), 18, 2)
    pygame.draw.circle(surface, (240, 245, 255), (cx - 28, cy + 5), 10, 2)
    # 盾心
    pygame.draw.circle(surface, (240, 245, 255), (cx - 28, cy + 5), 4)
    
    # 银甲肩刺
    for side in [-1, 1]:
        spike_x = cx + side * 28
        spike_pts = [
            (spike_x, cy - 15),
            (spike_x - 5, cy + 5),
            (spike_x + 5, cy + 5),
        ]
        pygame.draw.polygon(surface, (200, 210, 220), spike_pts)
        pygame.draw.polygon(surface, (240, 245, 255), spike_pts, 1)
    
    # 核心
    pygame.draw.circle(surface, (220, 230, 255), (cx, cy + 8), int(7 + 2 * pulse))
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy + 8), 3)


def _render_dragoon_azure(surface, t, pulse, visual=None):
    """苍蓝形态 - 深蓝风暴：深蓝色风暴骑士"""
    cx, cy = 60, 60
    
    # 风暴漩涡
    for ring in range(5):
        r = 25 + ring * 8 + int(5 * math.sin(t * 4 + ring))
        angle_offset = t * (50 - ring * 8)
        # 漩涡弧线
        for seg in range(4):
            start_angle = (seg * 90 + angle_offset) * math.pi / 180
            end_angle = (seg * 90 + 60 + angle_offset) * math.pi / 180
            blue_val = 150 + ring * 20
            pygame.draw.arc(surface, (30, 80, blue_val), 
                          (cx - r, cy - r, r * 2, r * 2), start_angle, end_angle, 3)
    
    # 苍蓝装甲
    body_pts = [
        (cx, cy - 30),
        (cx - 22, cy + 5),
        (cx - 20, cy + 26),
        (cx + 20, cy + 26),
        (cx + 22, cy + 5),
    ]
    pygame.draw.polygon(surface, (20, 50, 100), body_pts)
    pygame.draw.polygon(surface, (60, 120, 200), body_pts, 2)
    
    # 风暴头盔
    helmet_pts = [
        (cx, cy - 38),
        (cx - 14, cy - 20),
        (cx - 12, cy - 8),
        (cx + 12, cy - 8),
        (cx + 14, cy - 20),
    ]
    pygame.draw.polygon(surface, (30, 60, 120), helmet_pts)
    pygame.draw.polygon(surface, (80, 140, 220), helmet_pts, 2)
    # 风纹面甲
    for i in range(3):
        y = cy - 22 + i * 4
        pygame.draw.line(surface, (100, 180, 255), (cx - 6 + i, y), (cx + 6 - i, y), 2)
    
    # 风暴枪
    lance_tip_y = cy - 60
    # 枪身带风纹
    pygame.draw.line(surface, (40, 90, 160), (cx, cy + 18), (cx, lance_tip_y + 15), 5)
    for i in range(5):
        y = cy + 10 - i * 12
        pygame.draw.arc(surface, (80, 150, 220), (cx - 8, y - 4, 16, 8), 0, math.pi, 2)
    # 枪头（旋风形）
    for rot in range(3):
        angle = (rot * 120 + t * 80) * math.pi / 180
        tip_x = cx + math.cos(angle) * 10
        tip_y = lance_tip_y + 8 + math.sin(angle) * 5
        pygame.draw.polygon(surface, (100, 180, 255), [
            (cx, lance_tip_y), (tip_x, tip_y), (cx, lance_tip_y + 15)
        ])
    
    # 风盾
    shield_pts = [
        (cx - 35, cy - 5),
        (cx - 42, cy + 5),
        (cx - 40, cy + 20),
        (cx - 30, cy + 25),
        (cx - 25, cy + 10),
    ]
    pygame.draw.polygon(surface, (30, 70, 140), shield_pts)
    pygame.draw.polygon(surface, (80, 150, 230), shield_pts, 2)
    # 风纹
    pygame.draw.arc(surface, (120, 180, 255), (cx - 42, cy, 20, 15), 0, math.pi, 2)
    
    # 核心（风暴眼）
    pygame.draw.circle(surface, (80, 150, 230), (cx, cy + 5), int(8 + 3 * pulse))
    pygame.draw.circle(surface, (150, 200, 255), (cx, cy + 5), 4)


def _render_dragoon_silver(surface, t, pulse, visual=None):
    """白银形态 - 纯银圣骑：神圣白银"""
    cx, cy = 60, 60
    
    # 圣光环
    for ring in range(4):
        r = 35 + ring * 8 + int(4 * pulse)
        pygame.draw.circle(surface, (230, 235, 245), (cx, cy), r, 2)
    
    # 圣光粒子
    for i in range(8):
        particle_angle = (i * 45 + t * 25) * math.pi / 180
        particle_dist = 42 + 5 * math.sin(t * 3 + i)
        px = cx + math.cos(particle_angle) * particle_dist
        py = cy + math.sin(particle_angle) * particle_dist
        pygame.draw.circle(surface, (255, 255, 255), (int(px), int(py)), 3)
    
    # 纯银装甲（流线型）
    body_pts = [
        (cx, cy - 32),
        (cx - 18, cy - 5),
        (cx - 20, cy + 25),
        (cx, cy + 30),
        (cx + 20, cy + 25),
        (cx + 18, cy - 5),
    ]
    pygame.draw.polygon(surface, (210, 220, 235), body_pts)
    pygame.draw.polygon(surface, (240, 245, 255), body_pts, 2)
    
    # 天使头盔
    helmet_pts = [
        (cx, cy - 40),
        (cx - 10, cy - 22),
        (cx - 8, cy - 12),
        (cx + 8, cy - 12),
        (cx + 10, cy - 22),
    ]
    pygame.draw.polygon(surface, (220, 230, 245), helmet_pts)
    pygame.draw.polygon(surface, (250, 252, 255), helmet_pts, 2)
    # Y字面甲
    pygame.draw.line(surface, (255, 255, 255), (cx - 5, cy - 25), (cx, cy - 20), 2)
    pygame.draw.line(surface, (255, 255, 255), (cx + 5, cy - 25), (cx, cy - 20), 2)
    pygame.draw.line(surface, (255, 255, 255), (cx, cy - 20), (cx, cy - 14), 2)
    
    # 圣枪
    lance_tip_y = cy - 58
    pygame.draw.line(surface, (220, 230, 245), (cx, cy + 18), (cx, lance_tip_y + 12), 4)
    pygame.draw.line(surface, (255, 255, 255), (cx, cy + 18), (cx, lance_tip_y + 12), 2)
    # 十字枪头
    pygame.draw.polygon(surface, (240, 245, 255), [
        (cx, lance_tip_y), (cx - 5, lance_tip_y + 12), (cx + 5, lance_tip_y + 12)
    ])
    pygame.draw.line(surface, (255, 255, 255), (cx - 10, lance_tip_y + 8), (cx + 10, lance_tip_y + 8), 3)
    
    # 圣盾
    shield_r = 16
    pygame.draw.circle(surface, (220, 230, 245), (cx - 30, cy + 5), shield_r)
    pygame.draw.circle(surface, (250, 252, 255), (cx - 30, cy + 5), shield_r, 2)
    # 十字纹
    pygame.draw.line(surface, (255, 255, 255), (cx - 30, cy - 5), (cx - 30, cy + 15), 3)
    pygame.draw.line(surface, (255, 255, 255), (cx - 40, cy + 5), (cx - 20, cy + 5), 3)
    
    # 光翼暗示
    for side in [-1, 1]:
        wing_base_x = cx + side * 25
        for i in range(3):
            wing_x = wing_base_x + side * (8 + i * 4)
            wing_y = cy - 10 + i * 5
            pygame.draw.line(surface, (240, 245, 255), (wing_base_x, cy - 5), (wing_x, wing_y), 2)
    
    # 核心
    pygame.draw.circle(surface, (240, 245, 255), (cx, cy + 5), int(8 + 3 * pulse))
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy + 5), 4)


def _render_dragoon_storm(surface, t, pulse, visual=None):
    """风暴形态 - 雷电骑士：闪电风暴"""
    cx, cy = 60, 60
    
    # 雷电环
    for ring in range(3):
        r = 38 + ring * 10 + int(5 * pulse)
        # 闪烁的闪电圈
        if (int(t * 15) + ring) % 3 != 0:
            pygame.draw.circle(surface, (200, 200, 50), (cx, cy), r, 2)
    
    # 闪电条
    for i in range(6):
        bolt_angle = (i * 60 + t * 40) * math.pi / 180
        start_r = 20
        end_r = 50
        
        points = []
        for j in range(6):
            r = start_r + (end_r - start_r) * j / 5
            offset = 8 * math.sin(j * 2 + t * 10) * (1 if j % 2 == 0 else -1)
            bx = cx + math.cos(bolt_angle) * r + math.cos(bolt_angle + math.pi/2) * offset
            by = cy + math.sin(bolt_angle) * r + math.sin(bolt_angle + math.pi/2) * offset
            points.append((int(bx), int(by)))
        
        pygame.draw.lines(surface, (255, 255, 100), False, points, 3)
        pygame.draw.lines(surface, (255, 255, 255), False, points, 1)
    
    # 雷电装甲
    body_pts = [
        (cx, cy - 30),
        (cx - 22, cy + 5),
        (cx - 18, cy + 26),
        (cx + 18, cy + 26),
        (cx + 22, cy + 5),
    ]
    pygame.draw.polygon(surface, (60, 60, 80), body_pts)
    pygame.draw.polygon(surface, (200, 200, 100), body_pts, 2)
    
    # 头盔（带闪电角）
    helmet_pts = [
        (cx, cy - 35),
        (cx - 12, cy - 18),
        (cx - 10, cy - 8),
        (cx + 10, cy - 8),
        (cx + 12, cy - 18),
    ]
    pygame.draw.polygon(surface, (70, 70, 90), helmet_pts)
    pygame.draw.polygon(surface, (220, 220, 120), helmet_pts, 2)
    # 闪电角
    for side in [-1, 1]:
        horn_pts = [
            (cx + side * 12, cy - 25),
            (cx + side * 18, cy - 40),
            (cx + side * 15, cy - 28),
        ]
        pygame.draw.polygon(surface, (255, 255, 100), horn_pts)
    
    # 雷电面甲
    pygame.draw.line(surface, (255, 255, 150), (cx - 5, cy - 22), (cx + 5, cy - 22), 2)
    
    # 雷枪
    lance_tip_y = cy - 58
    pygame.draw.line(surface, (100, 100, 60), (cx, cy + 18), (cx, lance_tip_y + 15), 5)
    # 闪电缠绕
    for i in range(4):
        y = cy + 10 - i * 15
        offset = 6 * (1 if i % 2 == 0 else -1)
        pygame.draw.line(surface, (255, 255, 100), (cx + offset, y), (cx - offset, y - 10), 2)
    # 枪头
    pygame.draw.polygon(surface, (255, 255, 150), [
        (cx, lance_tip_y), (cx - 8, lance_tip_y + 15), (cx + 8, lance_tip_y + 15)
    ])
    
    # 核心（闪烁）
    core_brightness = int(200 + 55 * math.sin(t * 15))
    pygame.draw.circle(surface, (core_brightness, core_brightness, 100), (cx, cy + 5), int(8 + 4 * pulse))
    pygame.draw.circle(surface, (255, 255, 200), (cx, cy + 5), 4)


def _render_dragoon_ancient(surface, t, pulse, visual=None):
    """远古形态 - 古龙遗迹：石质古老造型"""
    cx, cy = 60, 60
    
    # 远古符文环
    for ring in range(3):
        r = 40 + ring * 8 + int(3 * pulse)
        pygame.draw.circle(surface, (100, 90, 70), (cx, cy), r, 2)
    
    # 远古符文
    for i in range(8):
        rune_angle = (i * 45 + t * 10) * math.pi / 180
        rune_r = 45
        rx = cx + math.cos(rune_angle) * rune_r
        ry = cy + math.sin(rune_angle) * rune_r
        
        # 不同符文形状
        if i % 4 == 0:
            pygame.draw.rect(surface, (150, 130, 90), (rx - 3, ry - 3, 6, 6))
        elif i % 4 == 1:
            pygame.draw.circle(surface, (150, 130, 90), (int(rx), int(ry)), 4, 2)
        elif i % 4 == 2:
            pygame.draw.polygon(surface, (150, 130, 90), [
                (rx, ry - 4), (rx + 4, ry + 3), (rx - 4, ry + 3)
            ])
        else:
            pygame.draw.line(surface, (150, 130, 90), (int(rx - 4), int(ry)), (int(rx + 4), int(ry)), 2)
            pygame.draw.line(surface, (150, 130, 90), (int(rx), int(ry - 4)), (int(rx), int(ry + 4)), 2)
    
    # 石质装甲（粗糙边缘）
    body_pts = [
        (cx - 2, cy - 28),
        (cx + 3, cy - 30),
        (cx - 24, cy + 3),
        (cx - 22, cy + 8),
        (cx - 20, cy + 25),
        (cx - 18, cy + 28),
        (cx + 18, cy + 28),
        (cx + 20, cy + 25),
        (cx + 24, cy + 5),
    ]
    pygame.draw.polygon(surface, (90, 80, 60), body_pts)
    pygame.draw.polygon(surface, (140, 120, 90), body_pts, 2)
    
    # 古龙头盔
    helmet_pts = [
        (cx - 3, cy - 38),
        (cx + 2, cy - 36),
        (cx - 15, cy - 18),
        (cx - 12, cy - 8),
        (cx + 12, cy - 8),
        (cx + 15, cy - 18),
    ]
    pygame.draw.polygon(surface, (100, 90, 70), helmet_pts)
    pygame.draw.polygon(surface, (160, 140, 100), helmet_pts, 2)
    # 古老眼缝
    pygame.draw.line(surface, (180, 160, 100), (cx - 8, cy - 20), (cx + 8, cy - 20), 3)
    
    # 石枪
    lance_tip_y = cy - 55
    pygame.draw.line(surface, (120, 100, 70), (cx, cy + 18), (cx, lance_tip_y + 12), 6)
    pygame.draw.line(surface, (160, 140, 100), (cx, cy + 18), (cx, lance_tip_y + 12), 2)
    # 石质枪头
    pygame.draw.polygon(surface, (140, 120, 80), [
        (cx, lance_tip_y), (cx - 10, lance_tip_y + 18), (cx + 10, lance_tip_y + 18)
    ])
    pygame.draw.polygon(surface, (180, 160, 120), [
        (cx, lance_tip_y), (cx - 10, lance_tip_y + 18), (cx + 10, lance_tip_y + 18)
    ], 2)
    
    # 裂纹装饰
    crack_pts = [(cx - 5, cy), (cx - 8, cy + 10), (cx - 3, cy + 18)]
    pygame.draw.lines(surface, (60, 50, 40), False, crack_pts, 2)
    crack_pts2 = [(cx + 8, cy - 5), (cx + 12, cy + 5), (cx + 6, cy + 12)]
    pygame.draw.lines(surface, (60, 50, 40), False, crack_pts2, 2)
    
    # 核心（古老光芒）
    pygame.draw.circle(surface, (180, 150, 80), (cx, cy + 5), int(7 + 2 * pulse))
    pygame.draw.circle(surface, (220, 200, 120), (cx, cy + 5), 4)


def _render_dragoon_dragon(surface, t, pulse, visual=None):
    """真龙形态 - 龙化形态：化身巨龙"""
    cx, cy = 60, 60
    
    # 龙焰环
    for ring in range(3):
        r = 40 + ring * 10 + int(5 * pulse)
        pygame.draw.circle(surface, (200, 100, 50), (cx, cy), r, 2)
    
    # 龙焰粒子
    for i in range(12):
        flame_angle = (i * 30 + t * 50) * math.pi / 180
        flame_dist = 45 + 8 * abs(math.sin(t * 5 + i * 0.5))
        fx = cx + math.cos(flame_angle) * flame_dist
        fy = cy + math.sin(flame_angle) * flame_dist
        flame_size = int(4 + 3 * abs(math.sin(t * 8 + i)))
        pygame.draw.circle(surface, (255, 150, 50), (int(fx), int(fy)), flame_size)
        pygame.draw.circle(surface, (255, 200, 100), (int(fx), int(fy)), flame_size - 1)
    
    # 龙鳞装甲
    body_pts = [
        (cx, cy - 28),
        (cx - 25, cy + 5),
        (cx - 22, cy + 30),
        (cx + 22, cy + 30),
        (cx + 25, cy + 5),
    ]
    pygame.draw.polygon(surface, (60, 100, 60), body_pts)
    pygame.draw.polygon(surface, (100, 180, 100), body_pts, 2)
    
    # 龙鳞纹理
    for row in range(3):
        for col in range(4):
            sx = cx - 12 + col * 8
            sy = cy - 5 + row * 10
            scale_pts = [(sx, sy - 4), (sx + 4, sy), (sx, sy + 4), (sx - 4, sy)]
            pygame.draw.polygon(surface, (80, 140, 80), scale_pts)
            pygame.draw.polygon(surface, (120, 200, 120), scale_pts, 1)
    
    # 龙头盔
    helmet_pts = [
        (cx, cy - 40),
        (cx - 15, cy - 20),
        (cx - 12, cy - 8),
        (cx + 12, cy - 8),
        (cx + 15, cy - 20),
    ]
    pygame.draw.polygon(surface, (70, 110, 70), helmet_pts)
    pygame.draw.polygon(surface, (120, 180, 120), helmet_pts, 2)
    
    # 龙角
    for side in [-1, 1]:
        horn_pts = [
            (cx + side * 12, cy - 25),
            (cx + side * 22, cy - 45),
            (cx + side * 18, cy - 35),
            (cx + side * 14, cy - 30),
        ]
        pygame.draw.polygon(surface, (150, 100, 50), horn_pts)
        pygame.draw.polygon(surface, (200, 150, 80), horn_pts, 1)
    
    # 龙眼
    pygame.draw.ellipse(surface, (255, 200, 50), (cx - 6, cy - 24, 5, 4))
    pygame.draw.ellipse(surface, (255, 200, 50), (cx + 1, cy - 24, 5, 4))
    pygame.draw.circle(surface, (255, 50, 30), (cx - 4, cy - 22), 2)
    pygame.draw.circle(surface, (255, 50, 30), (cx + 4, cy - 22), 2)
    
    # 龙爪枪
    lance_tip_y = cy - 58
    pygame.draw.line(surface, (80, 120, 80), (cx, cy + 20), (cx, lance_tip_y + 15), 5)
    # 龙爪枪头
    for claw in range(3):
        claw_angle = (claw - 1) * 20 - 90
        claw_rad = claw_angle * math.pi / 180
        claw_x = cx + math.cos(claw_rad) * 15
        claw_y = lance_tip_y + math.sin(claw_rad) * 15 + 5
        pygame.draw.line(surface, (200, 150, 80), (cx, lance_tip_y + 10), (int(claw_x), int(claw_y)), 3)
    
    # 龙翼
    for side in [-1, 1]:
        wing_pts = [
            (cx + side * 22, cy - 5),
            (cx + side * 45, cy - 20),
            (cx + side * 50, cy),
            (cx + side * 45, cy + 15),
            (cx + side * 25, cy + 10),
        ]
        pygame.draw.polygon(surface, (60, 100, 60), wing_pts)
        pygame.draw.polygon(surface, (100, 180, 100), wing_pts, 2)
        # 翼骨
        pygame.draw.line(surface, (80, 140, 80), (cx + side * 22, cy - 5), (cx + side * 45, cy - 15), 2)
        pygame.draw.line(surface, (80, 140, 80), (cx + side * 22, cy - 5), (cx + side * 48, cy + 5), 2)
    
    # 核心
    pygame.draw.circle(surface, (255, 150, 50), (cx, cy + 8), int(8 + 3 * pulse))
    pygame.draw.circle(surface, (255, 220, 100), (cx, cy + 8), 4)


def _render_dragoon_royal(surface, t, pulse, visual=None):
    """皇家形态 - 金红王者：王族金红配色"""
    cx, cy = 60, 60
    
    # 皇家光环
    for ring in range(3):
        r = 40 + ring * 8 + int(4 * pulse)
        gold = (255, 200 - ring * 20, 50)
        pygame.draw.circle(surface, gold, (cx, cy), r, 2)
    
    # 金色粒子
    for i in range(10):
        particle_angle = (i * 36 + t * 30) * math.pi / 180
        particle_dist = 45 + 5 * math.sin(t * 3 + i)
        px = cx + math.cos(particle_angle) * particle_dist
        py = cy + math.sin(particle_angle) * particle_dist
        pygame.draw.circle(surface, (255, 220, 100), (int(px), int(py)), 3)
    
    # 皇家装甲（华丽）
    body_pts = [
        (cx, cy - 30),
        (cx - 22, cy + 3),
        (cx - 20, cy + 26),
        (cx + 20, cy + 26),
        (cx + 22, cy + 3),
    ]
    pygame.draw.polygon(surface, (150, 30, 30), body_pts)
    pygame.draw.polygon(surface, (255, 200, 80), body_pts, 3)
    
    # 金纹装饰
    pygame.draw.line(surface, (255, 220, 100), (cx, cy - 25), (cx, cy + 20), 2)
    pygame.draw.line(surface, (255, 220, 100), (cx - 12, cy), (cx + 12, cy), 2)
    
    # 王冠头盔
    helmet_pts = [
        (cx, cy - 38),
        (cx - 12, cy - 22),
        (cx - 10, cy - 10),
        (cx + 10, cy - 10),
        (cx + 12, cy - 22),
    ]
    pygame.draw.polygon(surface, (180, 40, 40), helmet_pts)
    pygame.draw.polygon(surface, (255, 200, 80), helmet_pts, 2)
    
    # 王冠
    crown_pts = [
        (cx - 10, cy - 35),
        (cx - 8, cy - 42),
        (cx - 4, cy - 38),
        (cx, cy - 48),
        (cx + 4, cy - 38),
        (cx + 8, cy - 42),
        (cx + 10, cy - 35),
    ]
    pygame.draw.polygon(surface, (255, 200, 50), crown_pts)
    pygame.draw.polygon(surface, (255, 255, 150), crown_pts, 1)
    # 宝石
    pygame.draw.circle(surface, (255, 50, 50), (cx, cy - 43), 3)
    
    # 王者之枪
    lance_tip_y = cy - 60
    pygame.draw.line(surface, (200, 150, 50), (cx + 3, cy + 18), (cx + 3, lance_tip_y + 15), 5)
    pygame.draw.line(surface, (255, 220, 100), (cx + 3, cy + 18), (cx + 3, lance_tip_y + 15), 2)
    # 枪头
    pygame.draw.polygon(surface, (255, 200, 80), [
        (cx + 3, lance_tip_y), (cx - 7, lance_tip_y + 18), (cx + 13, lance_tip_y + 18)
    ])
    # 红宝石装饰
    pygame.draw.circle(surface, (255, 50, 50), (cx + 3, lance_tip_y + 10), 4)
    pygame.draw.circle(surface, (255, 150, 150), (cx + 1, lance_tip_y + 8), 2)
    
    # 皇家盾牌
    shield_pts = [
        (cx - 32, cy - 8),
        (cx - 42, cy + 5),
        (cx - 38, cy + 22),
        (cx - 28, cy + 22),
        (cx - 24, cy + 5),
    ]
    pygame.draw.polygon(surface, (150, 30, 30), shield_pts)
    pygame.draw.polygon(surface, (255, 200, 80), shield_pts, 2)
    # 皇家徽章
    pygame.draw.circle(surface, (255, 200, 80), (cx - 33, cy + 8), 8, 2)
    pygame.draw.polygon(surface, (255, 220, 100), [
        (cx - 33, cy + 2), (cx - 30, cy + 8), (cx - 33, cy + 14), (cx - 36, cy + 8)
    ])
    
    # 核心
    pygame.draw.circle(surface, (255, 200, 80), (cx, cy + 5), int(8 + 3 * pulse))
    pygame.draw.circle(surface, (255, 50, 50), (cx, cy + 5), 4)


def _render_dragoon_valkyrie(surface, t, pulse, visual=None):
    """瓦尔基里形态 - 战争女神：蓝银羽翼"""
    cx, cy = 60, 60
    
    # 神圣光环
    for ring in range(3):
        r = 42 + ring * 8 + int(4 * pulse)
        pygame.draw.circle(surface, (180, 200, 255), (cx, cy), r, 2)
    
    # 光羽粒子
    for i in range(10):
        feather_angle = (i * 36 + t * 25) * math.pi / 180
        feather_dist = 46 + 6 * math.sin(t * 3 + i)
        fx = cx + math.cos(feather_angle) * feather_dist
        fy = cy + math.sin(feather_angle) * feather_dist
        # 羽毛形状
        pygame.draw.ellipse(surface, (200, 220, 255), (int(fx) - 2, int(fy) - 5, 4, 10))
    
    # 女武神装甲（流线型）
    body_pts = [
        (cx, cy - 28),
        (cx - 18, cy + 2),
        (cx - 16, cy + 24),
        (cx, cy + 28),
        (cx + 16, cy + 24),
        (cx + 18, cy + 2),
    ]
    pygame.draw.polygon(surface, (80, 100, 150), body_pts)
    pygame.draw.polygon(surface, (150, 180, 230), body_pts, 2)
    
    # 女武神头盔（有翼）
    helmet_pts = [
        (cx, cy - 35),
        (cx - 10, cy - 20),
        (cx - 8, cy - 10),
        (cx + 8, cy - 10),
        (cx + 10, cy - 20),
    ]
    pygame.draw.polygon(surface, (100, 120, 170), helmet_pts)
    pygame.draw.polygon(surface, (170, 200, 250), helmet_pts, 2)
    
    # 头盔翼装饰
    for side in [-1, 1]:
        wing_pts = [
            (cx + side * 10, cy - 25),
            (cx + side * 20, cy - 38),
            (cx + side * 25, cy - 32),
            (cx + side * 18, cy - 25),
        ]
        pygame.draw.polygon(surface, (200, 220, 255), wing_pts)
        pygame.draw.polygon(surface, (255, 255, 255), wing_pts, 1)
    
    # Y字面甲
    pygame.draw.line(surface, (200, 220, 255), (cx - 4, cy - 24), (cx, cy - 18), 2)
    pygame.draw.line(surface, (200, 220, 255), (cx + 4, cy - 24), (cx, cy - 18), 2)
    pygame.draw.line(surface, (200, 220, 255), (cx, cy - 18), (cx, cy - 12), 2)
    
    # 神枪
    lance_tip_y = cy - 58
    pygame.draw.line(surface, (120, 140, 180), (cx, cy + 18), (cx, lance_tip_y + 12), 4)
    pygame.draw.line(surface, (200, 220, 255), (cx, cy + 18), (cx, lance_tip_y + 12), 2)
    # 枪头
    pygame.draw.polygon(surface, (200, 220, 255), [
        (cx, lance_tip_y), (cx - 8, lance_tip_y + 15), (cx + 8, lance_tip_y + 15)
    ])
    pygame.draw.polygon(surface, (255, 255, 255), [
        (cx, lance_tip_y), (cx - 8, lance_tip_y + 15), (cx + 8, lance_tip_y + 15)
    ], 1)
    
    # 巨大羽翼
    for side in [-1, 1]:
        # 翼骨
        wing_base = (cx + side * 18, cy - 5)
        wing_tips = [
            (cx + side * 50, cy - 30),
            (cx + side * 55, cy - 15),
            (cx + side * 52, cy + 5),
            (cx + side * 45, cy + 20),
        ]
        for tip in wing_tips:
            pygame.draw.line(surface, (150, 180, 230), wing_base, tip, 2)
        
        # 羽毛
        for i, tip in enumerate(wing_tips):
            feather_pts = [
                wing_base,
                tip,
                (tip[0] - side * 5, tip[1] + 8),
            ]
            pygame.draw.polygon(surface, (200, 220, 255), feather_pts)
    
    # 核心
    pygame.draw.circle(surface, (180, 200, 255), (cx, cy + 5), int(8 + 3 * pulse))
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy + 5), 4)


def _render_dragoon_divine(surface, t, pulse, visual=None):
    """神圣形态 - 圣光骑士：终极圣光"""
    cx, cy = 60, 60
    
    # 神圣光轮
    for ring in range(5):
        r = 30 + ring * 8 + int(4 * pulse)
        pygame.draw.circle(surface, (255, 250, 220), (cx, cy), r, 2)
    
    # 圣光粒子
    for i in range(16):
        particle_angle = (i * 22.5 + t * 20) * math.pi / 180
        particle_dist = 48 + 6 * math.sin(t * 3 + i * 0.5)
        px = cx + math.cos(particle_angle) * particle_dist
        py = cy + math.sin(particle_angle) * particle_dist
        pygame.draw.circle(surface, (255, 255, 255), (int(px), int(py)), 3)
        pygame.draw.circle(surface, (255, 240, 200), (int(px), int(py)), 2)
    
    # 神圣装甲（发光）
    body_pts = [
        (cx, cy - 30),
        (cx - 20, cy + 3),
        (cx - 18, cy + 26),
        (cx + 18, cy + 26),
        (cx + 20, cy + 3),
    ]
    pygame.draw.polygon(surface, (255, 250, 240), body_pts)
    pygame.draw.polygon(surface, (255, 220, 150), body_pts, 2)
    
    # 圣光纹
    pygame.draw.line(surface, (255, 230, 180), (cx, cy - 25), (cx, cy + 20), 3)
    pygame.draw.line(surface, (255, 230, 180), (cx - 15, cy), (cx + 15, cy), 3)
    
    # 神圣头盔（光环）
    helmet_pts = [
        (cx, cy - 38),
        (cx - 12, cy - 20),
        (cx - 10, cy - 10),
        (cx + 10, cy - 10),
        (cx + 12, cy - 20),
    ]
    pygame.draw.polygon(surface, (255, 252, 245), helmet_pts)
    pygame.draw.polygon(surface, (255, 230, 180), helmet_pts, 2)
    
    # 天使光环
    halo_y = cy - 45
    pygame.draw.ellipse(surface, (255, 240, 180), (cx - 15, halo_y - 3, 30, 10), 3)
    
    # 十字面甲
    pygame.draw.line(surface, (255, 240, 200), (cx - 6, cy - 22), (cx + 6, cy - 22), 3)
    pygame.draw.line(surface, (255, 240, 200), (cx, cy - 26), (cx, cy - 14), 3)
    
    # 圣枪（发光）
    lance_tip_y = cy - 62
    pygame.draw.line(surface, (255, 250, 230), (cx, cy + 18), (cx, lance_tip_y + 15), 5)
    pygame.draw.line(surface, (255, 255, 255), (cx, cy + 18), (cx, lance_tip_y + 15), 2)
    # 十字枪头
    pygame.draw.polygon(surface, (255, 250, 220), [
        (cx, lance_tip_y), (cx - 6, lance_tip_y + 15), (cx + 6, lance_tip_y + 15)
    ])
    # 十字横杠
    pygame.draw.line(surface, (255, 240, 200), (cx - 12, lance_tip_y + 8), (cx + 12, lance_tip_y + 8), 4)
    pygame.draw.line(surface, (255, 255, 255), (cx - 12, lance_tip_y + 8), (cx + 12, lance_tip_y + 8), 2)
    
    # 圣光翼
    for side in [-1, 1]:
        for wing in range(5):
            wing_angle = (side * (40 + wing * 15) + 90) * math.pi / 180
            wing_length = 35 + wing * 5
            wx = cx + math.cos(wing_angle) * wing_length
            wy = cy - 5 + math.sin(wing_angle) * wing_length
            
            # 光羽
            pygame.draw.line(surface, (255, 250, 230), (cx + side * 15, cy - 5), (int(wx), int(wy)), 3)
            pygame.draw.line(surface, (255, 255, 255), (cx + side * 15, cy - 5), (int(wx), int(wy)), 1)
            
            # 羽尖光点
            pygame.draw.circle(surface, (255, 255, 255), (int(wx), int(wy)), 3)
    
    # 圣盾
    shield_r = 18
    pygame.draw.circle(surface, (255, 250, 240), (cx - 32, cy + 5), shield_r)
    pygame.draw.circle(surface, (255, 230, 180), (cx - 32, cy + 5), shield_r, 2)
    # 十字
    pygame.draw.line(surface, (255, 240, 200), (cx - 32, cy - 8), (cx - 32, cy + 18), 4)
    pygame.draw.line(surface, (255, 240, 200), (cx - 44, cy + 5), (cx - 20, cy + 5), 4)
    
    # 核心（圣光闪耀）
    core_r = int(10 + 5 * pulse)
    pygame.draw.circle(surface, (255, 250, 220), (cx, cy + 5), core_r)
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy + 5), 5)
    # 光芒
    for i in range(8):
        ray_angle = (i * 45 + t * 40) * math.pi / 180
        ray_x = cx + math.cos(ray_angle) * (core_r + 6)
        ray_y = cy + 5 + math.sin(ray_angle) * (core_r + 6)
        pygame.draw.line(surface, (255, 255, 255), (cx, cy + 5), (int(ray_x), int(ray_y)), 2)
