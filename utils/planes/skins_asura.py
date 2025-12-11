# -*- coding: utf-8 -*-
"""
Asura 修罗·斩龙者 机体涂装渲染模块

设计理念：
- 核心元素：六臂战神、剑气纵横、修罗之怒
- 机体形态：多臂剑士造型，锐利的剑刃轮廓
- 视觉效果：红黑主色调，金色剑气光芒，狂暴火焰特效
"""
import pygame
import math

# Asura 涂装样式列表
ASURA_STYLES = [
    "asura_base",         # 基础形态 - 六臂战神
    "asura_rage",         # 修罗之怒 - 狂暴火焰
    "asura_dragon",       # 斩龙 - 金龙缠绕
    "asura_shadow",       # 暗影 - 暗夜刺客
    "asura_crimson",      # 绯红 - 血月形态
    "asura_celestial",    # 天罚 - 天界审判者
    "asura_void",         # 虚空 - 空间裂隙
    "asura_golden",       # 黄金 - 金刚不坏
    "asura_demon",        # 魔神 - 地狱修罗
    "asura_divine",       # 神罚 - 阴阳一体
]


def is_asura_style(model_style):
    """检查是否为 Asura 涂装样式"""
    return model_style in ASURA_STYLES


def render_asura_skin(s, c, model_style, t, pid, static):
    """渲染 Asura 专属涂装"""
    if not is_asura_style(model_style):
        return None
    
    pulse = 0 if static else abs(math.sin(t * 3))
    
    if model_style == "asura_base":
        _render_asura_base(s, t, pulse)
    elif model_style == "asura_rage":
        _render_asura_rage(s, t, pulse)
    elif model_style == "asura_dragon":
        _render_asura_dragon(s, t, pulse)
    elif model_style == "asura_shadow":
        _render_asura_shadow(s, t, pulse)
    elif model_style == "asura_crimson":
        _render_asura_crimson(s, t, pulse)
    elif model_style == "asura_celestial":
        _render_asura_celestial(s, t, pulse)
    elif model_style == "asura_void":
        _render_asura_void(s, t, pulse)
    elif model_style == "asura_golden":
        _render_asura_golden(s, t, pulse)
    elif model_style == "asura_demon":
        _render_asura_demon(s, t, pulse)
    elif model_style == "asura_divine":
        _render_asura_divine(s, t, pulse)
    else:
        _render_asura_base(s, t, pulse)
    
    return s


def _render_asura_base(surface, t, pulse, visual=None):
    """基础形态 - 六臂战神：血红色六臂剑士"""
    cx, cy = 60, 60
    
    # 背景气场
    aura_r = int(48 + 5 * pulse)
    pygame.draw.circle(surface, (80, 20, 30), (cx, cy), aura_r, 2)
    
    # 六臂旋转剑刃
    for i in range(6):
        angle = (i * 60 + t * 30) * math.pi / 180
        # 剑身
        base_x = cx + math.cos(angle) * 18
        base_y = cy + math.sin(angle) * 18
        tip_x = cx + math.cos(angle) * 52
        tip_y = cy + math.sin(angle) * 52
        
        # 剑刃形状（菱形）
        perp_angle = angle + math.pi / 2
        w = 6
        blade_pts = [
            (tip_x, tip_y),
            (base_x + math.cos(perp_angle) * w, base_y + math.sin(perp_angle) * w),
            (base_x - math.cos(angle) * 5, base_y - math.sin(angle) * 5),
            (base_x - math.cos(perp_angle) * w, base_y - math.sin(perp_angle) * w),
        ]
        pygame.draw.polygon(surface, (180, 50, 50), blade_pts)
        pygame.draw.polygon(surface, (255, 100, 100), blade_pts, 1)
        
        # 剑气拖尾
        trail_x = cx + math.cos(angle) * 42
        trail_y = cy + math.sin(angle) * 42
        pygame.draw.circle(surface, (255, 150, 150), (int(trail_x), int(trail_y)), 3)
    
    # 修罗机体核心（六边形）
    body_pts = []
    for i in range(6):
        angle = (i * 60 - 90) * math.pi / 180
        body_pts.append((cx + math.cos(angle) * 22, cy + math.sin(angle) * 22))
    pygame.draw.polygon(surface, (60, 20, 30), body_pts)
    pygame.draw.polygon(surface, (180, 50, 50), body_pts, 2)
    
    # 内核（三角形叠加）
    inner_r = 12
    for rot in [0, 60]:
        inner_pts = []
        for i in range(3):
            angle = (i * 120 + rot - 90) * math.pi / 180
            inner_pts.append((cx + math.cos(angle) * inner_r, cy + math.sin(angle) * inner_r))
        pygame.draw.polygon(surface, (120, 30, 40), inner_pts)
        pygame.draw.polygon(surface, (255, 80, 80), inner_pts, 1)
    
    # 修罗之眼
    eye_size = int(6 + 2 * pulse)
    pygame.draw.circle(surface, (255, 200, 100), (cx, cy), eye_size)
    pygame.draw.circle(surface, (255, 50, 50), (cx, cy), 4)
    pygame.draw.circle(surface, (255, 255, 255), (cx - 2, cy - 2), 2)


def _render_asura_rage(surface, t, pulse, visual=None):
    """修罗之怒 - 狂暴火焰：燃烧的怒火形态"""
    cx, cy = 60, 60
    
    # 火焰光环
    for ring in range(3):
        r = 35 + ring * 8 + int(4 * pulse)
        flame_color = [(255, 100, 30), (255, 150, 50), (255, 200, 100)][ring]
        pygame.draw.circle(surface, flame_color, (cx, cy), r, 2)
    
    # 火焰粒子喷发
    for i in range(12):
        angle = (i * 30 + t * 80) * math.pi / 180
        dist = 35 + 15 * abs(math.sin(t * 5 + i * 0.5))
        fx = cx + math.cos(angle) * dist
        fy = cy + math.sin(angle) * dist
        flame_size = int(4 + 3 * abs(math.sin(t * 8 + i)))
        
        # 火焰渐变
        pygame.draw.circle(surface, (255, 200, 50), (int(fx), int(fy)), flame_size)
        pygame.draw.circle(surface, (255, 100, 30), (int(fx), int(fy)), flame_size - 1)
    
    # 六臂火剑
    for i in range(6):
        angle = (i * 60 + t * 40) * math.pi / 180
        base_x = cx + math.cos(angle) * 16
        base_y = cy + math.sin(angle) * 16
        tip_x = cx + math.cos(angle) * 48
        tip_y = cy + math.sin(angle) * 48
        
        # 火焰剑身
        pygame.draw.line(surface, (255, 200, 100), (int(base_x), int(base_y)), (int(tip_x), int(tip_y)), 5)
        pygame.draw.line(surface, (255, 100, 50), (int(base_x), int(base_y)), (int(tip_x), int(tip_y)), 3)
        pygame.draw.line(surface, (255, 255, 200), (int(base_x), int(base_y)), (int(tip_x), int(tip_y)), 1)
    
    # 狂暴核心（不规则多边形）
    rage_pts = []
    for i in range(8):
        angle = (i * 45 - 90) * math.pi / 180
        r = 18 + 4 * math.sin(t * 6 + i * 2)
        rage_pts.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
    pygame.draw.polygon(surface, (100, 30, 20), rage_pts)
    pygame.draw.polygon(surface, (255, 150, 50), rage_pts, 2)
    
    # 怒火之眼（三只眼）
    for ex, ey in [(cx, cy - 6), (cx - 7, cy + 4), (cx + 7, cy + 4)]:
        pygame.draw.circle(surface, (255, 200, 100), (ex, ey), 5)
        pygame.draw.circle(surface, (255, 50, 30), (ex, ey), 3)


def _render_asura_dragon(surface, t, pulse, visual=None):
    """斩龙形态 - 金龙缠绕：金色龙纹与剑气交织"""
    cx, cy = 60, 60
    
    # 金龙环绕轨迹
    dragon_segments = 20
    for i in range(dragon_segments):
        seg_angle = (i * 18 + t * 60) * math.pi / 180
        seg_r = 38 + 8 * math.sin(t * 3 + i * 0.3)
        dx = cx + math.cos(seg_angle) * seg_r
        dy = cy + math.sin(seg_angle) * seg_r
        seg_size = int(5 + 2 * math.sin(i * 0.5))
        
        # 龙身渐变
        gold_val = int(200 + 55 * math.sin(i * 0.3))
        pygame.draw.circle(surface, (255, gold_val, 50), (int(dx), int(dy)), seg_size)
    
    # 龙首
    head_angle = t * 60 * math.pi / 180
    head_x = cx + math.cos(head_angle) * 45
    head_y = cy + math.sin(head_angle) * 45
    # 龙头形状
    head_pts = [
        (head_x + math.cos(head_angle) * 12, head_y + math.sin(head_angle) * 12),
        (head_x + math.cos(head_angle + 2.5) * 8, head_y + math.sin(head_angle + 2.5) * 8),
        (head_x + math.cos(head_angle + math.pi) * 5, head_y + math.sin(head_angle + math.pi) * 5),
        (head_x + math.cos(head_angle - 2.5) * 8, head_y + math.sin(head_angle - 2.5) * 8),
    ]
    pygame.draw.polygon(surface, (255, 220, 100), head_pts)
    # 龙眼
    pygame.draw.circle(surface, (255, 50, 50), (int(head_x), int(head_y)), 3)
    
    # 斩龙六剑
    for i in range(6):
        angle = (i * 60 + t * 25) * math.pi / 180
        base_x = cx + math.cos(angle) * 15
        base_y = cy + math.sin(angle) * 15
        tip_x = cx + math.cos(angle) * 50
        tip_y = cy + math.sin(angle) * 50
        
        # 金色剑刃
        perp = angle + math.pi / 2
        blade_pts = [
            (tip_x, tip_y),
            (base_x + math.cos(perp) * 5, base_y + math.sin(perp) * 5),
            (base_x - math.cos(perp) * 5, base_y - math.sin(perp) * 5),
        ]
        pygame.draw.polygon(surface, (255, 200, 80), blade_pts)
        pygame.draw.polygon(surface, (255, 255, 200), blade_pts, 1)
    
    # 斩龙核心
    body_pts = []
    for i in range(6):
        angle = (i * 60 - 90) * math.pi / 180
        body_pts.append((cx + math.cos(angle) * 20, cy + math.sin(angle) * 20))
    pygame.draw.polygon(surface, (120, 80, 30), body_pts)
    pygame.draw.polygon(surface, (255, 200, 100), body_pts, 2)
    
    # 龙纹核心眼
    pygame.draw.circle(surface, (255, 220, 100), (cx, cy), int(8 + 3 * pulse))
    pygame.draw.circle(surface, (200, 150, 50), (cx, cy), 5)
    pygame.draw.circle(surface, (255, 255, 200), (cx - 2, cy - 2), 2)


def _render_asura_shadow(surface, t, pulse, visual=None):
    """暗影形态 - 暗夜刺客：黑紫色隐秘杀手"""
    cx, cy = 60, 60
    
    # 暗影波纹
    for ring in range(4):
        r = 25 + ring * 10 + int(3 * math.sin(t * 4 + ring))
        pygame.draw.circle(surface, (80, 40, 120), (cx, cy), r, 2)
    
    # 残影分身
    for i in range(3):
        shadow_angle = (i * 120 + t * 50) * math.pi / 180
        shadow_dist = 30 + 5 * math.sin(t * 3)
        sx = cx + math.cos(shadow_angle) * shadow_dist
        sy = cy + math.sin(shadow_angle) * shadow_dist
        
        # 分身轮廓（半透明）
        shadow_pts = []
        for j in range(6):
            a = (j * 60 - 90) * math.pi / 180
            shadow_pts.append((sx + math.cos(a) * 10, sy + math.sin(a) * 10))
        pygame.draw.polygon(surface, (60, 30, 80), shadow_pts)
        pygame.draw.polygon(surface, (120, 80, 160), shadow_pts, 1)
    
    # 暗影六刃（闪烁）
    for i in range(6):
        angle = (i * 60 + t * 35) * math.pi / 180
        visible = (int(t * 10) + i) % 3 != 0  # 闪烁效果
        if visible:
            base_x = cx + math.cos(angle) * 18
            base_y = cy + math.sin(angle) * 18
            tip_x = cx + math.cos(angle) * 48
            tip_y = cy + math.sin(angle) * 48
            
            pygame.draw.line(surface, (150, 100, 200), (int(base_x), int(base_y)), (int(tip_x), int(tip_y)), 3)
            pygame.draw.line(surface, (200, 150, 255), (int(base_x), int(base_y)), (int(tip_x), int(tip_y)), 1)
    
    # 暗影核心
    body_pts = []
    for i in range(6):
        angle = (i * 60 - 90) * math.pi / 180
        r = 20 + 3 * math.sin(t * 5 + i)
        body_pts.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
    pygame.draw.polygon(surface, (30, 15, 40), body_pts)
    pygame.draw.polygon(surface, (100, 60, 140), body_pts, 2)
    
    # 暗影之眼（紫红色）
    pygame.draw.circle(surface, (150, 80, 180), (cx, cy), int(7 + 2 * pulse))
    pygame.draw.circle(surface, (200, 100, 220), (cx, cy), 4)
    pygame.draw.circle(surface, (255, 200, 255), (cx - 1, cy - 1), 2)


def _render_asura_crimson(surface, t, pulse, visual=None):
    """绯红形态 - 血月形态：深红血色与月光"""
    cx, cy = 60, 60
    
    # 血月光环
    moon_r = int(45 + 5 * pulse)
    pygame.draw.circle(surface, (150, 30, 50), (cx, cy), moon_r, 3)
    pygame.draw.circle(surface, (200, 50, 70), (cx, cy), moon_r - 5, 1)
    
    # 血滴粒子
    for i in range(16):
        drop_angle = (i * 22.5 + t * 20) * math.pi / 180
        drop_dist = 40 + 8 * abs(math.sin(t * 2 + i * 0.4))
        dx = cx + math.cos(drop_angle) * drop_dist
        dy = cy + math.sin(drop_angle) * drop_dist
        
        # 血滴形状
        drop_size = int(3 + 2 * abs(math.sin(t * 4 + i)))
        pygame.draw.circle(surface, (180, 20, 40), (int(dx), int(dy)), drop_size)
        pygame.draw.circle(surface, (255, 100, 120), (int(dx), int(dy - 2)), drop_size - 1)
    
    # 血色六刃
    for i in range(6):
        angle = (i * 60 + t * 28) * math.pi / 180
        base_x = cx + math.cos(angle) * 16
        base_y = cy + math.sin(angle) * 16
        tip_x = cx + math.cos(angle) * 50
        tip_y = cy + math.sin(angle) * 50
        
        # 血红剑刃（带滴血效果）
        pygame.draw.line(surface, (150, 20, 40), (int(base_x), int(base_y)), (int(tip_x), int(tip_y)), 5)
        pygame.draw.line(surface, (255, 80, 100), (int(base_x), int(base_y)), (int(tip_x), int(tip_y)), 2)
        
        # 滴血
        drip_y = tip_y + 5 + 3 * math.sin(t * 6 + i)
        pygame.draw.circle(surface, (180, 20, 40), (int(tip_x), int(drip_y)), 2)
    
    # 血月核心
    body_pts = []
    for i in range(6):
        angle = (i * 60 - 90) * math.pi / 180
        body_pts.append((cx + math.cos(angle) * 22, cy + math.sin(angle) * 22))
    pygame.draw.polygon(surface, (80, 15, 30), body_pts)
    pygame.draw.polygon(surface, (180, 40, 60), body_pts, 2)
    
    # 血月之眼
    pygame.draw.circle(surface, (200, 50, 70), (cx, cy), int(9 + 3 * pulse))
    pygame.draw.circle(surface, (255, 100, 120), (cx, cy), 5)
    pygame.draw.circle(surface, (100, 10, 20), (cx, cy), 2)


def _render_asura_celestial(surface, t, pulse, visual=None):
    """天罚形态 - 天界审判者：金白神圣光芒"""
    cx, cy = 60, 60
    
    # 天界光轮
    for ring in range(4):
        r = 30 + ring * 10 + int(3 * pulse)
        color = [(255, 250, 240), (255, 230, 180), (255, 215, 100), (255, 200, 80)][ring]
        pygame.draw.circle(surface, color, (cx, cy), r, 2)
    
    # 神圣符文环
    for i in range(12):
        rune_angle = (i * 30 + t * 15) * math.pi / 180
        rune_r = 42
        rx = cx + math.cos(rune_angle) * rune_r
        ry = cy + math.sin(rune_angle) * rune_r
        
        # 符文样式（十字/菱形交替）
        if i % 2 == 0:
            pygame.draw.line(surface, (255, 230, 150), (int(rx - 4), int(ry)), (int(rx + 4), int(ry)), 2)
            pygame.draw.line(surface, (255, 230, 150), (int(rx), int(ry - 4)), (int(rx), int(ry + 4)), 2)
        else:
            rune_pts = [(rx, ry - 4), (rx + 3, ry), (rx, ry + 4), (rx - 3, ry)]
            pygame.draw.polygon(surface, (255, 215, 100), rune_pts)
    
    # 天剑六芒
    for i in range(6):
        angle = (i * 60 + t * 20) * math.pi / 180
        base_x = cx + math.cos(angle) * 15
        base_y = cy + math.sin(angle) * 15
        tip_x = cx + math.cos(angle) * 52
        tip_y = cy + math.sin(angle) * 52
        
        # 圣光剑刃
        pygame.draw.line(surface, (255, 240, 200), (int(base_x), int(base_y)), (int(tip_x), int(tip_y)), 4)
        pygame.draw.line(surface, (255, 255, 255), (int(base_x), int(base_y)), (int(tip_x), int(tip_y)), 2)
        
        # 剑尖光芒
        pygame.draw.circle(surface, (255, 255, 220), (int(tip_x), int(tip_y)), 4)
    
    # 天界核心
    body_pts = []
    for i in range(6):
        angle = (i * 60 - 90) * math.pi / 180
        body_pts.append((cx + math.cos(angle) * 20, cy + math.sin(angle) * 20))
    pygame.draw.polygon(surface, (255, 245, 220), body_pts)
    pygame.draw.polygon(surface, (255, 215, 100), body_pts, 2)
    
    # 神圣之眼（光芒四射）
    eye_r = int(8 + 4 * pulse)
    pygame.draw.circle(surface, (255, 240, 180), (cx, cy), eye_r)
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 5)
    # 光芒
    for i in range(8):
        ray_angle = (i * 45 + t * 30) * math.pi / 180
        ray_end_x = cx + math.cos(ray_angle) * (eye_r + 5)
        ray_end_y = cy + math.sin(ray_angle) * (eye_r + 5)
        pygame.draw.line(surface, (255, 255, 200), (cx, cy), (int(ray_end_x), int(ray_end_y)), 1)


def _render_asura_void(surface, t, pulse, visual=None):
    """虚空形态 - 空间裂隙：紫黑虚空裂隙"""
    cx, cy = 60, 60
    
    # 虚空漩涡
    for ring in range(5):
        r = 20 + ring * 8 + int(4 * math.sin(t * 3 + ring))
        angle_offset = t * (30 - ring * 5)
        
        # 破碎的圆环
        for seg in range(6):
            start_angle = (seg * 60 + angle_offset) * math.pi / 180
            end_angle = (seg * 60 + 40 + angle_offset) * math.pi / 180
            pygame.draw.arc(surface, (100, 50, 150), 
                          (cx - r, cy - r, r * 2, r * 2), start_angle, end_angle, 2)
    
    # 空间裂隙线
    for i in range(8):
        crack_angle = (i * 45 + t * 25) * math.pi / 180
        # 锯齿裂隙
        points = [(cx, cy)]
        for j in range(5):
            dist = 10 + j * 10
            offset = 5 * math.sin(t * 8 + i + j)
            perp_angle = crack_angle + math.pi / 2
            px = cx + math.cos(crack_angle) * dist + math.cos(perp_angle) * offset
            py = cy + math.sin(crack_angle) * dist + math.sin(perp_angle) * offset
            points.append((int(px), int(py)))
        pygame.draw.lines(surface, (150, 80, 200), False, points, 2)
    
    # 虚空六刃
    for i in range(6):
        angle = (i * 60 + t * 32) * math.pi / 180
        base_x = cx + math.cos(angle) * 15
        base_y = cy + math.sin(angle) * 15
        tip_x = cx + math.cos(angle) * 48
        tip_y = cy + math.sin(angle) * 48
        
        # 虚空剑（半透明效果）
        mid_x = (base_x + tip_x) / 2
        mid_y = (base_y + tip_y) / 2
        pygame.draw.line(surface, (80, 40, 120), (int(base_x), int(base_y)), (int(mid_x), int(mid_y)), 4)
        pygame.draw.line(surface, (150, 100, 200), (int(mid_x), int(mid_y)), (int(tip_x), int(tip_y)), 3)
    
    # 虚空核心（黑洞效果）
    pygame.draw.circle(surface, (20, 10, 30), (cx, cy), 18)
    pygame.draw.circle(surface, (80, 50, 120), (cx, cy), 18, 2)
    pygame.draw.circle(surface, (150, 100, 200), (cx, cy), 12, 1)
    
    # 虚空之眼
    pygame.draw.circle(surface, (150, 80, 200), (cx, cy), int(6 + 3 * pulse))
    pygame.draw.circle(surface, (200, 150, 255), (cx, cy), 3)


def _render_asura_golden(surface, t, pulse, visual=None):
    """黄金形态 - 金刚不坏：纯金装甲形态"""
    cx, cy = 60, 60
    
    # 金色光芒
    for ring in range(3):
        r = 38 + ring * 8 + int(5 * pulse)
        pygame.draw.circle(surface, (255, 220 - ring * 20, 50), (cx, cy), r, 3)
    
    # 金色粒子
    for i in range(10):
        particle_angle = (i * 36 + t * 40) * math.pi / 180
        particle_dist = 42 + 6 * math.sin(t * 4 + i)
        px = cx + math.cos(particle_angle) * particle_dist
        py = cy + math.sin(particle_angle) * particle_dist
        pygame.draw.circle(surface, (255, 255, 200), (int(px), int(py)), 3)
        pygame.draw.circle(surface, (255, 200, 50), (int(px), int(py)), 2)
    
    # 金刚六剑
    for i in range(6):
        angle = (i * 60 + t * 22) * math.pi / 180
        base_x = cx + math.cos(angle) * 18
        base_y = cy + math.sin(angle) * 18
        tip_x = cx + math.cos(angle) * 52
        tip_y = cy + math.sin(angle) * 52
        
        # 黄金剑刃
        perp = angle + math.pi / 2
        blade_pts = [
            (tip_x, tip_y),
            (base_x + math.cos(perp) * 6, base_y + math.sin(perp) * 6),
            (base_x - math.cos(perp) * 6, base_y - math.sin(perp) * 6),
        ]
        pygame.draw.polygon(surface, (255, 200, 50), blade_pts)
        pygame.draw.polygon(surface, (255, 255, 150), blade_pts, 1)
    
    # 金刚核心（八边形）
    body_pts = []
    for i in range(8):
        angle = (i * 45 - 90) * math.pi / 180
        body_pts.append((cx + math.cos(angle) * 20, cy + math.sin(angle) * 20))
    pygame.draw.polygon(surface, (200, 150, 30), body_pts)
    pygame.draw.polygon(surface, (255, 220, 100), body_pts, 2)
    
    # 金刚内核
    inner_pts = []
    for i in range(8):
        angle = (i * 45 + 22.5 - 90) * math.pi / 180
        inner_pts.append((cx + math.cos(angle) * 12, cy + math.sin(angle) * 12))
    pygame.draw.polygon(surface, (255, 200, 50), inner_pts)
    pygame.draw.polygon(surface, (255, 255, 200), inner_pts, 1)
    
    # 金刚之眼
    pygame.draw.circle(surface, (255, 255, 200), (cx, cy), int(7 + 3 * pulse))
    pygame.draw.circle(surface, (255, 220, 100), (cx, cy), 4)


def _render_asura_demon(surface, t, pulse, visual=None):
    """魔神形态 - 地狱修罗：黑红邪恶形态"""
    cx, cy = 60, 60
    
    # 地狱火焰
    for i in range(16):
        flame_angle = (i * 22.5 + t * 60) * math.pi / 180
        flame_dist = 35 + 15 * abs(math.sin(t * 6 + i * 0.4))
        fx = cx + math.cos(flame_angle) * flame_dist
        fy = cy + math.sin(flame_angle) * flame_dist
        
        # 黑火焰
        flame_size = int(5 + 3 * abs(math.sin(t * 8 + i)))
        pygame.draw.circle(surface, (80, 20, 40), (int(fx), int(fy)), flame_size)
        pygame.draw.circle(surface, (150, 50, 80), (int(fx), int(fy)), flame_size - 2)
    
    # 魔纹环
    for ring in range(2):
        r = 40 + ring * 10 + int(4 * pulse)
        pygame.draw.circle(surface, (100, 20, 40), (cx, cy), r, 2)
    
    # 魔神八刃（比基础多两把）
    for i in range(8):
        angle = (i * 45 + t * 35) * math.pi / 180
        base_x = cx + math.cos(angle) * 15
        base_y = cy + math.sin(angle) * 15
        tip_x = cx + math.cos(angle) * 50
        tip_y = cy + math.sin(angle) * 50
        
        # 魔刃（锯齿状）
        mid1_x = cx + math.cos(angle) * 28 + math.cos(angle + 0.5) * 5
        mid1_y = cy + math.sin(angle) * 28 + math.sin(angle + 0.5) * 5
        mid2_x = cx + math.cos(angle) * 38 + math.cos(angle - 0.5) * 5
        mid2_y = cy + math.sin(angle) * 38 + math.sin(angle - 0.5) * 5
        
        pygame.draw.lines(surface, (150, 30, 60), False, [
            (int(base_x), int(base_y)), (int(mid1_x), int(mid1_y)),
            (int(mid2_x), int(mid2_y)), (int(tip_x), int(tip_y))
        ], 3)
        pygame.draw.lines(surface, (255, 80, 120), False, [
            (int(base_x), int(base_y)), (int(mid1_x), int(mid1_y)),
            (int(mid2_x), int(mid2_y)), (int(tip_x), int(tip_y))
        ], 1)
    
    # 魔神核心
    body_pts = []
    for i in range(6):
        angle = (i * 60 - 90) * math.pi / 180
        r = 22 + 3 * math.sin(t * 4 + i * 2)
        body_pts.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
    pygame.draw.polygon(surface, (40, 10, 25), body_pts)
    pygame.draw.polygon(surface, (150, 40, 70), body_pts, 2)
    
    # 恶魔之角
    for side in [-1, 1]:
        horn_base = (cx + side * 12, cy - 15)
        horn_tip = (cx + side * 20, cy - 30)
        horn_mid = (cx + side * 18, cy - 20)
        pygame.draw.polygon(surface, (100, 30, 50), [horn_base, horn_mid, horn_tip])
        pygame.draw.polygon(surface, (180, 60, 90), [horn_base, horn_mid, horn_tip], 1)
    
    # 魔眼（竖瞳）
    pygame.draw.ellipse(surface, (200, 50, 80), (cx - 8, cy - 6, 16, 12))
    pygame.draw.ellipse(surface, (255, 100, 130), (cx - 5, cy - 4, 10, 8))
    pygame.draw.ellipse(surface, (50, 10, 20), (cx - 2, cy - 3, 4, 6))


def _render_asura_divine(surface, t, pulse, visual=None):
    """神罚形态 - 阴阳一体：光暗交织的终极形态"""
    cx, cy = 60, 60
    
    # 阴阳光环（旋转太极）
    taiji_angle = t * 40
    for ring in range(3):
        r = 42 + ring * 6 + int(4 * pulse)
        # 半黑半白的环
        pygame.draw.arc(surface, (255, 250, 240), (cx - r, cy - r, r * 2, r * 2),
                       (taiji_angle * math.pi / 180), (taiji_angle * math.pi / 180 + math.pi), 2)
        pygame.draw.arc(surface, (40, 30, 50), (cx - r, cy - r, r * 2, r * 2),
                       (taiji_angle * math.pi / 180 + math.pi), (taiji_angle * math.pi / 180 + 2 * math.pi), 2)
    
    # 光暗粒子
    for i in range(12):
        particle_angle = (i * 30 + t * 30) * math.pi / 180
        particle_dist = 38 + 6 * math.sin(t * 3 + i)
        px = cx + math.cos(particle_angle) * particle_dist
        py = cy + math.sin(particle_angle) * particle_dist
        
        color = (255, 250, 240) if i % 2 == 0 else (60, 50, 80)
        pygame.draw.circle(surface, color, (int(px), int(py)), 4)
    
    # 神罚八剑（光暗交替）
    for i in range(8):
        angle = (i * 45 + t * 25) * math.pi / 180
        base_x = cx + math.cos(angle) * 16
        base_y = cy + math.sin(angle) * 16
        tip_x = cx + math.cos(angle) * 55
        tip_y = cy + math.sin(angle) * 55
        
        # 光剑或暗剑
        if i % 2 == 0:
            blade_color = (255, 250, 240)
            edge_color = (255, 215, 100)
        else:
            blade_color = (60, 40, 80)
            edge_color = (150, 100, 200)
        
        pygame.draw.line(surface, blade_color, (int(base_x), int(base_y)), (int(tip_x), int(tip_y)), 4)
        pygame.draw.line(surface, edge_color, (int(base_x), int(base_y)), (int(tip_x), int(tip_y)), 1)
        pygame.draw.circle(surface, edge_color, (int(tip_x), int(tip_y)), 3)
    
    # 阴阳核心
    # 外层
    pygame.draw.circle(surface, (200, 180, 160), (cx, cy), 22, 2)
    # 阴半
    pygame.draw.arc(surface, (40, 30, 50), (cx - 20, cy - 20, 40, 40), math.pi / 2, math.pi * 1.5, 20)
    # 阳半
    pygame.draw.arc(surface, (255, 250, 240), (cx - 20, cy - 20, 40, 40), -math.pi / 2, math.pi / 2, 20)
    # 小圆
    pygame.draw.circle(surface, (255, 250, 240), (cx, cy - 10), 6)
    pygame.draw.circle(surface, (40, 30, 50), (cx, cy + 10), 6)
    pygame.draw.circle(surface, (40, 30, 50), (cx, cy - 10), 3)
    pygame.draw.circle(surface, (255, 250, 240), (cx, cy + 10), 3)
    
    # 神罚之眼（金色）
    pygame.draw.circle(surface, (255, 215, 100), (cx, cy), int(6 + 3 * pulse))
    pygame.draw.circle(surface, (255, 255, 255), (cx - 1, cy - 1), 2)
