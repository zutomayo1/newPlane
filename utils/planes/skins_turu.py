# -*- coding: utf-8 -*-
"""
至尊机体涂装 - Turu（巨石核拳·图鲁）

远古巨石战神的化身，双腕发射巨石拳头，岩核充能后可卸甲强化
主题配色：岩灰 (120, 115, 110) + 核熔橙 (255, 120, 40)
"""
import pygame
import math
import random

# Turu 涂装样式列表
TURU_STYLES = [
    "turu_default",         # 岩核战神 - 默认巨石形态
    "turu_magma",          # 熔岩之心 - 岩浆裂纹+熔融核心
    "turu_obsidian",       # 黑曜石王 - 黑曜石质感+紫电光芒
    "turu_crystal",        # 晶簇巨像 - 水晶集群+棱镜折射
    "turu_jade",           # 翡翠巨兽 - 东方玉石+符文刻纹
    "turu_meteor",         # 陨铁图鲁 - 陨石纹理+太空金属
    "turu_sandstone",      # 沙岩古神 - 沙漠风化+埃及图腾
    "turu_ice",            # 冰川巨人 - 冰晶结构+寒霜光芒
    "turu_volcanic",       # 火山领主 - 火山熔岩+喷发特效
    "turu_diamond",        # 钻石核心 - 钻石切面+虹光反射
    "turu_rusty",          # 锈蚀远古 - 生锈金属+苔藓覆盖
    "turu_golden",         # 黄金图鲁 - 镀金表面+圣光环绕
]


def is_turu_style(model_style):
    return model_style in TURU_STYLES


def render_turu_skin(s, c, model_style, t, pid, static):
    if not is_turu_style(model_style):
        return None
    pulse = 0 if static else abs(math.sin(t * 2))
    
    # 检测卸甲状态（从全局player获取）
    unarmor_mode = False
    try:
        from sprites import player
        if player and hasattr(player, 'armor_mode') and not player.armor_mode:
            unarmor_mode = True
    except:
        pass
    
    renderers = {
        "turu_default": _render_turu_default,
        "turu_magma": _render_turu_magma,
        "turu_obsidian": _render_turu_obsidian,
        "turu_crystal": _render_turu_crystal,
        "turu_jade": _render_turu_jade,
        "turu_meteor": _render_turu_meteor,
        "turu_sandstone": _render_turu_sandstone,
        "turu_ice": _render_turu_ice,
        "turu_volcanic": _render_turu_volcanic,
        "turu_diamond": _render_turu_diamond,
        "turu_rusty": _render_turu_rusty,
        "turu_golden": _render_turu_golden,
    }
    renderer = renderers.get(model_style, _render_turu_default)
    renderer(s, t, pulse)
    
    # 卸甲状态特效：全身橙色能量光环+裂纹爆发
    if unarmor_mode and not static:
        _render_unarmor_effect(s, t)
    
    return s


def _render_unarmor_effect(s, t):
    """卸甲强化状态特效 - 能量爆发光环"""
    cx, cy = s.get_width() // 2, s.get_height() // 2
    
    # 能量脉冲光环（从里到外）
    pulse = abs(math.sin(t * 6))
    
    # 橙色能量外圈
    for i in range(3):
        ring_r = 28 + i * 5 + int(pulse * 4)
        ring_alpha = int(80 - i * 20 + pulse * 40)
        ring_surf = pygame.Surface(s.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (255, 120, 40, ring_alpha), (cx, cy), ring_r, 2)
        s.blit(ring_surf, (0, 0))
    
    # 能量裂纹从身体向外爆发
    for i in range(6):
        angle = (i * 60 + t * 100) * 0.01745
        inner_r = 18
        outer_r = 28 + int(pulse * 8)
        crack_surf = pygame.Surface(s.get_size(), pygame.SRCALPHA)
        sx = cx + math.cos(angle) * inner_r
        sy = cy + math.sin(angle) * inner_r
        ex = cx + math.cos(angle) * outer_r
        ey = cy + math.sin(angle) * outer_r
        pygame.draw.line(crack_surf, (255, 180, 80, int(150 + pulse * 100)), 
                        (int(sx), int(sy)), (int(ex), int(ey)), 2)
        s.blit(crack_surf, (0, 0))
    
    # 核心能量闪烁
    core_r = int(6 + pulse * 4)
    pygame.draw.circle(s, (255, 200, 100), (cx, cy), core_r)
    pygame.draw.circle(s, (255, 255, 200), (cx, cy), core_r // 2)


def _render_turu_base(s, t, pulse):
    """基础机体渲染（无涂装时使用）"""
    _render_turu_default(s, t, pulse)


# =============================================================================
#   通用绘制函数 - 高精度岩石战神渲染
# =============================================================================

def _draw_rock_body(s, cx, cy, size, t, base_color, dark_color, crack_color, segments=12):
    """岩石身躯 - 不规则多边形+动态裂纹+层次阴影"""
    # 外层阴影
    shadow_points = []
    for i in range(segments):
        angle = i * (360 / segments) * 0.01745 + math.sin(t * 0.3 + i * 0.4) * 0.08
        r = size * (0.95 + random.Random(i + 7).random() * 0.15)
        shadow_points.append((int(cx + math.cos(angle) * r + 2), int(cy + math.sin(angle) * r + 2)))
    pygame.draw.polygon(s, (30, 25, 20), shadow_points)
    
    # 主岩块
    points = []
    for i in range(segments):
        angle = i * (360 / segments) * 0.01745 + math.sin(t * 0.3 + i * 0.4) * 0.08
        r = size * (0.85 + random.Random(i + 7).random() * 0.25)
        points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
    pygame.draw.polygon(s, base_color, points)
    
    # 岩石纹理层
    inner_points = []
    for i in range(segments):
        angle = i * (360 / segments) * 0.01745 + 0.15
        r = size * 0.7
        inner_points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
    pygame.draw.polygon(s, dark_color, inner_points, 2)
    
    # 动态裂纹网（从中心向外辐射）
    crack_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(6):
        seed = random.Random(i + 42)
        start_angle = i * 60 * 0.01745
        # 主裂纹
        sx, sy = cx, cy
        for seg in range(3):
            angle_var = start_angle + seed.uniform(-0.3, 0.3)
            seg_len = size * 0.25 + seed.randint(0, int(size * 0.15))
            ex = sx + math.cos(angle_var) * seg_len
            ey = sy + math.sin(angle_var) * seg_len
            glow = int(120 + 80 * abs(math.sin(t * 2.5 + i * 0.8 + seg)))
            pygame.draw.line(crack_surf, (*crack_color, glow), (int(sx), int(sy)), (int(ex), int(ey)), 2)
            # 分支裂纹
            if seg < 2:
                branch_angle = angle_var + seed.choice([-0.5, 0.5])
                bex = sx + math.cos(branch_angle) * seg_len * 0.6
                bey = sy + math.sin(branch_angle) * seg_len * 0.6
                pygame.draw.line(crack_surf, (*crack_color, glow // 2), (int(sx), int(sy)), (int(bex), int(bey)), 1)
            sx, sy = ex, ey
    s.blit(crack_surf, (0, 0))
    
    # 边缘描边
    pygame.draw.polygon(s, dark_color, points, 3)


def _draw_stone_fist(s, fx, fy, size, t, rock_color, dark_color, glow_color, side='left'):
    """巨石战拳 - 带指节、裂纹、能量脉冲的拳头"""
    # 拳头光晕
    if glow_color:
        glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        pulse = abs(math.sin(t * 3))
        for i in range(3):
            glow_r = int(size * 0.6) + 8 - i * 4 + int(pulse * 4)
            pygame.draw.circle(glow_surf, (*glow_color, 60 - i * 18), (30, 30), glow_r)
        s.blit(glow_surf, (int(fx - 30), int(fy - 30)))
    
    # 拳头主体（不规则岩石形状）
    fist_points = []
    offset = 3 if side == 'left' else -3
    for i in range(8):
        angle = i * 45 * 0.01745 + (0.1 if side == 'left' else -0.1)
        r = size * 0.5 + random.Random(i + 17).randint(-2, 4)
        fist_points.append((int(fx + math.cos(angle) * r + offset), int(fy + math.sin(angle) * r)))
    pygame.draw.polygon(s, rock_color, fist_points)
    pygame.draw.polygon(s, dark_color, fist_points, 2)
    
    # 指节凸起（4个）
    for i in range(4):
        knuckle_angle = (-50 + i * 25) * 0.01745 if side == 'left' else (130 + i * 25) * 0.01745
        kx = fx + math.cos(knuckle_angle) * size * 0.45
        ky = fy + math.sin(knuckle_angle) * size * 0.45
        pygame.draw.circle(s, dark_color, (int(kx), int(ky)), int(size * 0.12))
        pygame.draw.circle(s, rock_color, (int(kx), int(ky)), int(size * 0.08))
    
    # 拳心能量核
    core_pulse = abs(math.sin(t * 4 + (0 if side == 'left' else math.pi)))
    if glow_color:
        pygame.draw.circle(s, glow_color, (int(fx), int(fy)), int(size * 0.2 + core_pulse * 3))
        pygame.draw.circle(s, (255, 240, 200), (int(fx), int(fy)), int(size * 0.1))


def _draw_charge_bar(s, cx, cy, max_charge, t, color):
    """充能槽 - 背部4格能量指示器（带动态效果）
    
    从玩家实例获取实际充能值，显示实时充能状态
    """
    bar_y = int(cy + 35)
    bar_width = 44
    segment_width = 10
    gap = 1
    
    # 获取实际充能值
    actual_charge = 0
    is_unarmored = False
    try:
        from sprites import player
        if player and hasattr(player, 'rock_charge'):
            actual_charge = int(player.rock_charge)
        if player and hasattr(player, 'armor_mode'):
            is_unarmored = not player.armor_mode
    except:
        actual_charge = 0
    
    # 底座
    base_color = (255, 100, 30) if is_unarmored else (25, 22, 20)
    pygame.draw.rect(s, base_color, (cx - bar_width//2 - 2, bar_y - 2, bar_width + 4, 12), border_radius=2)
    
    for i in range(max_charge):
        seg_x = cx - bar_width//2 + i * (segment_width + gap)
        filled = i < actual_charge
        
        if filled:
            # 填充格 - 带渐变和脉冲
            pulse = abs(math.sin(t * 6 + i * 0.5))
            bright = tuple(min(255, c + int(40 * pulse)) for c in color)
            pygame.draw.rect(s, color, (seg_x, bar_y, segment_width, 8), border_radius=1)
            # 高光
            pygame.draw.rect(s, bright, (seg_x + 1, bar_y + 1, segment_width - 2, 3), border_radius=1)
        elif is_unarmored:
            # 卸甲状态：空格也发光
            pulse = abs(math.sin(t * 8 + i * 0.3))
            glow_alpha = int(60 + pulse * 40)
            glow_surf = pygame.Surface((segment_width, 8), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (255, 120, 40, glow_alpha), (0, 0, segment_width, 8), border_radius=1)
            s.blit(glow_surf, (seg_x, bar_y))
        else:
            # 空格
            pygame.draw.rect(s, (40, 38, 35), (seg_x, bar_y, segment_width, 8), border_radius=1)
            pygame.draw.rect(s, (55, 50, 45), (seg_x, bar_y, segment_width, 8), 1, border_radius=1)
    
    # 满格闪烁（即将触发卸甲）
    if actual_charge >= max_charge:
        if abs(math.sin(t * 10)) > 0.6:
            flash_surf = pygame.Surface((bar_width + 4, 12), pygame.SRCALPHA)
            pygame.draw.rect(flash_surf, (255, 255, 255, 100), (0, 0, bar_width + 4, 12), border_radius=2)
            s.blit(flash_surf, (cx - bar_width//2 - 2, bar_y - 2))
    
    # 卸甲状态文字提示
    if is_unarmored:
        # 在充能条下方显示 "卸甲强化"
        try:
            from sprites import player
            if player and hasattr(player, 'unarmor_timer'):
                remaining = player.unarmor_timer / 60  # 转换为秒
                # 用进度条显示剩余时间
                progress = player.unarmor_timer / 300  # 总共5秒
                progress_width = int(bar_width * progress)
                pygame.draw.rect(s, (80, 40, 20), (cx - bar_width//2, bar_y + 12, bar_width, 4), border_radius=1)
                pygame.draw.rect(s, (255, 120, 40), (cx - bar_width//2, bar_y + 12, progress_width, 4), border_radius=1)
        except:
            pass


def _draw_core_eye(s, cx, cy, size, t, iris_color, pupil_color=(20, 15, 10)):
    """核心之眼 - 岩石巨人的能量核心"""
    # 眼眶
    pygame.draw.ellipse(s, (60, 55, 50), (cx - size - 2, cy - size * 0.7 - 2, size * 2 + 4, size * 1.4 + 4))
    pygame.draw.ellipse(s, (40, 35, 30), (cx - size, cy - size * 0.7, size * 2, size * 1.4))
    
    # 虹膜（带脉冲）
    pulse = abs(math.sin(t * 2.5))
    iris_r = int(size * 0.7 + pulse * 2)
    wobble_x = math.sin(t * 1.2) * 2
    wobble_y = math.cos(t * 0.9) * 1
    pygame.draw.circle(s, iris_color, (int(cx + wobble_x), int(cy + wobble_y)), iris_r)
    
    # 能量纹路
    for i in range(6):
        angle = i * 60 * 0.01745 + t * 0.5
        lx = cx + wobble_x + math.cos(angle) * iris_r * 0.3
        ly = cy + wobble_y + math.sin(angle) * iris_r * 0.3
        ex = cx + wobble_x + math.cos(angle) * iris_r * 0.9
        ey = cy + wobble_y + math.sin(angle) * iris_r * 0.9
        pygame.draw.line(s, (255, 200, 120), (int(lx), int(ly)), (int(ex), int(ey)), 1)
    
    # 瞳孔（竖瞳）
    pw = max(2, int(size * 0.15 + pulse * 2))
    ph = int(size * 0.9)
    pygame.draw.ellipse(s, pupil_color, (int(cx - pw//2 + wobble_x), int(cy - ph//2 + wobble_y), pw, ph))
    
    # 高光
    pygame.draw.circle(s, (255, 255, 240), (int(cx - size * 0.35), int(cy - size * 0.25)), max(2, int(size * 0.18)))


# =============================================================================
#   1. 岩核战神 - 默认巨石形态（至尊品质）
# =============================================================================

def _render_turu_default(s, t, pulse):
    rock_gray = (120, 115, 110)
    rock_dark = (70, 65, 60)
    core_orange = (255, 120, 40)
    crack_orange = (255, 160, 80)
    accent_brown = (100, 80, 60)
    
    # 多层能量光晕
    for i in range(4):
        glow_r = 52 - i * 10 + int(pulse * 6)
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        alpha = 55 - i * 13
        pygame.draw.circle(glow_surf, (*core_orange, alpha), (60, 60), glow_r)
        s.blit(glow_surf, (0, 0))
    
    # 岩石身躯
    _draw_rock_body(s, 60, 55, 32, t, rock_gray, rock_dark, crack_orange, 14)
    
    # 肩甲岩块（左右）
    for side, sx in [(-1, 32), (1, 88)]:
        shoulder_points = []
        for i in range(6):
            angle = (i * 60 + 30) * 0.01745 + side * 0.3
            r = 12 + random.Random(i + side * 10).randint(-2, 3)
            shoulder_points.append((int(sx + math.cos(angle) * r), int(42 + math.sin(angle) * r)))
        pygame.draw.polygon(s, rock_gray, shoulder_points)
        pygame.draw.polygon(s, rock_dark, shoulder_points, 2)
        # 肩甲发光裂纹
        pygame.draw.line(s, crack_orange, (sx, 38), (sx + side * 5, 46), 2)
    
    # 头部岩块（带头盔感）
    head_points = [(60, 22), (75, 32), (78, 42), (70, 48), (50, 48), (42, 42), (45, 32)]
    pygame.draw.polygon(s, rock_gray, head_points)
    pygame.draw.polygon(s, rock_dark, head_points, 2)
    # 头盔纹路
    pygame.draw.line(s, rock_dark, (52, 28), (52, 45), 2)
    pygame.draw.line(s, rock_dark, (68, 28), (68, 45), 2)
    
    # 核心之眼
    _draw_core_eye(s, 60, 38, 9, t, core_orange)
    
    # 胸甲核心（能量源）
    chest_pulse = abs(math.sin(t * 3))
    pygame.draw.polygon(s, accent_brown, [(50, 50), (70, 50), (65, 65), (55, 65)])
    pygame.draw.circle(s, core_orange, (60, 58), int(8 + chest_pulse * 3))
    pygame.draw.circle(s, (255, 200, 120), (60, 58), int(4 + chest_pulse * 2))
    pygame.draw.circle(s, (255, 240, 200), (60, 58), 2)
    
    # 能量脉冲线（从核心向外）
    pulse_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(4):
        angle = (i * 90 + 45 + t * 30) * 0.01745
        line_len = 15 + int(chest_pulse * 8)
        ex = 60 + math.cos(angle) * line_len
        ey = 58 + math.sin(angle) * line_len
        pygame.draw.line(pulse_surf, (*core_orange, int(150 * chest_pulse)), (60, 58), (int(ex), int(ey)), 2)
    s.blit(pulse_surf, (0, 0))
    
    # 手臂（粗壮岩石）
    arm_color = (90, 85, 80)
    # 左臂
    pygame.draw.line(s, arm_color, (38, 48), (22, 56), 8)
    pygame.draw.line(s, rock_dark, (38, 48), (22, 56), 8)
    pygame.draw.line(s, rock_gray, (36, 46), (24, 54), 6)
    # 右臂
    pygame.draw.line(s, arm_color, (82, 48), (98, 56), 8)
    pygame.draw.line(s, rock_dark, (82, 48), (98, 56), 8)
    pygame.draw.line(s, rock_gray, (84, 46), (96, 54), 6)
    
    # 巨石战拳
    fist_offset = int(pulse * 3)
    _draw_stone_fist(s, 18 - fist_offset, 58, 22, t, rock_gray, rock_dark, core_orange, 'left')
    _draw_stone_fist(s, 102 + fist_offset, 58, 22, t, rock_gray, rock_dark, core_orange, 'right')
    
    # 腿部岩石
    pygame.draw.polygon(s, rock_gray, [(48, 70), (56, 70), (52, 95), (44, 95)])
    pygame.draw.polygon(s, rock_gray, [(64, 70), (72, 70), (76, 95), (68, 95)])
    pygame.draw.polygon(s, rock_dark, [(48, 70), (56, 70), (52, 95), (44, 95)], 2)
    pygame.draw.polygon(s, rock_dark, [(64, 70), (72, 70), (76, 95), (68, 95)], 2)
    
    # 充能槽
    _draw_charge_bar(s, 60, 58, 4, t, core_orange)
    
    # 岩石碎屑飘落
    for i in range(4):
        debris_t = (t * 0.5 + i * 0.7) % 2
        debris_y = 25 + debris_t * 40
        debris_x = 30 + i * 20 + math.sin(t + i) * 5
        debris_alpha = int(255 * (1 - debris_t / 2))
        debris_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(debris_surf, (*rock_dark, debris_alpha), (4, 4), 2)
        s.blit(debris_surf, (int(debris_x), int(debris_y)))


# =============================================================================
#   2. 熔岩之心 - 岩浆裂纹+熔融核心（至尊品质）
# =============================================================================

def _render_turu_magma(s, t, pulse):
    magma_red = (255, 80, 20)
    lava_orange = (255, 150, 50)
    dark_rock = (50, 35, 25)
    molten_yellow = (255, 220, 100)
    ember_color = (255, 100, 30)
    crust_brown = (80, 50, 35)
    
    # 熔岩能量场光晕
    for i in range(5):
        glow_r = 55 - i * 9 + int(pulse * 8)
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*magma_red, 60 - i * 11), (60, 60), glow_r)
        s.blit(glow_surf, (0, 0))
    
    # 熔岩身躯（带冷却壳）
    body_points = []
    for i in range(16):
        angle = i * 22.5 * 0.01745
        r = 34 + math.sin(t * 1.5 + i * 0.5) * 3 + random.Random(i).randint(-2, 3)
        body_points.append((int(60 + math.cos(angle) * r), int(56 + math.sin(angle) * r * 0.9)))
    pygame.draw.polygon(s, dark_rock, body_points)
    
    # 熔岩裂纹网（多层动态）
    crack_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for layer in range(2):
        for i in range(8):
            seed = random.Random(i + layer * 20 + 13)
            sx = 60 + seed.randint(-22, 22)
            sy = 56 + seed.randint(-18, 18)
            # 分支裂纹
            for branch in range(2 + layer):
                angle = seed.uniform(0, 2 * math.pi)
                length = seed.randint(8, 18)
                ex = sx + math.cos(angle) * length
                ey = sy + math.sin(angle) * length
                # 流动效果
                flow_phase = (t * 2 + i * 0.5 + branch * 0.3) % 1
                col = lava_orange if flow_phase > 0.5 else magma_red
                alpha = int(180 + 75 * abs(math.sin(t * 3 + i)))
                pygame.draw.line(crack_surf, (*col, alpha), (int(sx), int(sy)), (int(ex), int(ey)), 3 - layer)
                sx, sy = ex, ey
    s.blit(crack_surf, (0, 0))
    
    # 熔岩气泡
    for i in range(6):
        bubble_phase = (t * 0.8 + i * 0.4) % 1.5
        if bubble_phase < 1:
            bx = 45 + i * 6 + math.sin(t + i) * 3
            by = 70 - bubble_phase * 30
            br = 3 + int((1 - bubble_phase) * 3)
            bubble_surf = pygame.Surface((br*4, br*4), pygame.SRCALPHA)
            pygame.draw.circle(bubble_surf, (*lava_orange, int(200 * (1 - bubble_phase))), (br*2, br*2), br)
            s.blit(bubble_surf, (int(bx - br*2), int(by - br*2)))
    
    # 熔融核心
    core_pulse = abs(math.sin(t * 4))
    core_r = int(14 + core_pulse * 5)
    # 核心光晕
    core_glow = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.circle(core_glow, (*molten_yellow, 100), (30, 30), core_r + 8)
    pygame.draw.circle(core_glow, (*lava_orange, 150), (30, 30), core_r + 4)
    s.blit(core_glow, (30, 26))
    # 核心本体
    pygame.draw.circle(s, molten_yellow, (60, 56), core_r)
    pygame.draw.circle(s, (255, 250, 220), (60, 56), int(core_r * 0.5))
    
    # 头部（熔岩穹顶）
    head_points = [(48, 42), (72, 42), (75, 32), (60, 22), (45, 32)]
    pygame.draw.polygon(s, dark_rock, head_points)
    # 头部裂纹
    for i in range(3):
        hx = 52 + i * 8
        pygame.draw.line(s, magma_red, (hx, 40), (hx + random.Random(i).randint(-3, 3), 28), 2)
    # 熔岩眼
    pygame.draw.ellipse(s, magma_red, (52, 32, 16, 10))
    pygame.draw.ellipse(s, molten_yellow, (56, 34, 8, 6))
    
    # 熔岩肩甲
    for sx in [28, 92]:
        pygame.draw.circle(s, dark_rock, (sx, 48), 10)
        # 熔岩裂纹
        for i in range(3):
            angle = (i * 120 + t * 50) * 0.01745
            pygame.draw.line(s, lava_orange, (sx, 48), 
                           (int(sx + math.cos(angle) * 8), int(48 + math.sin(angle) * 8)), 2)
    
    # 熔岩战拳
    for fx, side in [(18, 'left'), (102, 'right')]:
        # 拳头光晕
        fist_glow = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(fist_glow, (*magma_red, 80), (20, 20), 16)
        s.blit(fist_glow, (fx - 20, 38))
        # 拳头
        pygame.draw.circle(s, dark_rock, (fx, 58), 14)
        pygame.draw.circle(s, crust_brown, (fx, 58), 14, 2)
        # 熔岩核
        pygame.draw.circle(s, magma_red, (fx, 58), 9)
        pygame.draw.circle(s, lava_orange, (fx, 58), 5)
        pygame.draw.circle(s, molten_yellow, (fx, 58), 2)
    
    # 火星飞溅
    for i in range(8):
        spark_phase = (t * 1.2 + i * 0.3) % 1
        spark_angle = (i * 45 + t * 60) * 0.01745
        spark_dist = 35 + spark_phase * 25
        spark_x = 60 + math.cos(spark_angle) * spark_dist
        spark_y = 56 + math.sin(spark_angle) * spark_dist
        spark_alpha = int(255 * (1 - spark_phase))
        spark_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(spark_surf, (*ember_color, spark_alpha), (4, 4), 2)
        s.blit(spark_surf, (int(spark_x - 4), int(spark_y - 4)))
    
    _draw_charge_bar(s, 60, 60, int(3 + pulse), t, magma_red)


# =============================================================================
#   3. 黑曜石王 - 黑曜石质感+紫电光芒（至尊品质）
# =============================================================================

def _render_turu_obsidian(s, t, pulse):
    obsidian_black = (15, 12, 20)
    obsidian_purple = (60, 35, 90)
    obsidian_edge = (40, 25, 55)
    lightning_purple = (180, 100, 255)
    spark_white = (230, 210, 255)
    deep_violet = (100, 60, 150)
    
    # 紫电能量场
    for i in range(4):
        glow_r = 52 - i * 10 + int(pulse * 5)
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*obsidian_purple, 45 - i * 10), (60, 60), glow_r)
        s.blit(glow_surf, (0, 0))
    
    # 黑曜石身体（锐利切面）
    body_points = [(38, 28), (82, 28), (95, 55), (88, 82), (32, 82), (25, 55)]
    # 阴影
    shadow_points = [(p[0] + 2, p[1] + 2) for p in body_points]
    pygame.draw.polygon(s, (8, 5, 12), shadow_points)
    # 主体
    pygame.draw.polygon(s, obsidian_black, body_points)
    pygame.draw.polygon(s, obsidian_edge, body_points, 2)
    
    # 切面高光（玻璃质感）
    facet_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    # 主切面
    pygame.draw.polygon(facet_surf, (*spark_white, 35), [(48, 32), (72, 32), (68, 48), (44, 48)])
    # 次切面
    pygame.draw.polygon(facet_surf, (*deep_violet, 50), [(40, 50), (55, 50), (52, 68), (38, 68)])
    pygame.draw.polygon(facet_surf, (*deep_violet, 50), [(65, 50), (80, 50), (82, 68), (68, 68)])
    s.blit(facet_surf, (0, 0))
    
    # 紫电闪烁（动态雷电）
    lightning_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    if abs(math.sin(t * 8)) > 0.5:
        for i in range(4):
            seed = random.Random(int(t * 15) + i)
            # 雷电起点
            sx = 60 + seed.randint(-20, 20)
            sy = 55 + seed.randint(-18, 18)
            # 多段雷电
            for seg in range(3):
                ex = sx + seed.randint(-12, 12)
                ey = sy + seed.randint(-10, 10)
                pygame.draw.line(lightning_surf, lightning_purple, (int(sx), int(sy)), (int(ex), int(ey)), 2)
                # 分支
                if seed.random() > 0.5:
                    bx = sx + seed.randint(-8, 8)
                    by = sy + seed.randint(-6, 6)
                    pygame.draw.line(lightning_surf, (*spark_white, 180), (int(sx), int(sy)), (int(bx), int(by)), 1)
                sx, sy = ex, ey
            # 末端火花
            pygame.draw.circle(lightning_surf, spark_white, (int(ex), int(ey)), 3)
    s.blit(lightning_surf, (0, 0))
    
    # 黑曜石头盔
    head_points = [(50, 38), (70, 38), (75, 28), (60, 18), (45, 28)]
    pygame.draw.polygon(s, obsidian_black, head_points)
    pygame.draw.polygon(s, obsidian_edge, head_points, 2)
    # 头盔高光
    pygame.draw.line(s, (*spark_white, 80), (52, 32), (62, 22), 1)
    
    # 紫水晶核心
    core_pulse = abs(math.sin(t * 3.5))
    # 核心光晕
    core_glow = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(core_glow, (*lightning_purple, 120), (20, 20), int(12 + core_pulse * 4))
    s.blit(core_glow, (40, 35))
    # 核心
    pygame.draw.polygon(s, deep_violet, [(60, 48), (68, 56), (60, 64), (52, 56)])
    pygame.draw.polygon(s, lightning_purple, [(60, 48), (68, 56), (60, 64), (52, 56)], 2)
    pygame.draw.circle(s, spark_white, (60, 56), 4)
    
    # 紫电眼
    eye_glow = int(150 + 100 * abs(math.sin(t * 4)))
    pygame.draw.ellipse(s, (*lightning_purple, eye_glow), (52, 30, 16, 8))
    pygame.draw.ellipse(s, spark_white, (57, 32, 6, 4))
    
    # 黑曜石战拳（锐利切面）
    for fx, mirror in [(18, 1), (102, -1)]:
        fist_points = [(fx, 48), (fx + 12*mirror, 54), (fx + 10*mirror, 66), (fx - 2*mirror, 68), (fx - 10*mirror, 58)]
        pygame.draw.polygon(s, obsidian_black, fist_points)
        pygame.draw.polygon(s, obsidian_edge, fist_points, 2)
        # 拳头紫电
        if abs(math.sin(t * 6 + fx * 0.1)) > 0.7:
            pygame.draw.line(s, lightning_purple, (fx, 52), (fx + 5*mirror, 62), 2)
        # 拳心能量
        pygame.draw.circle(s, deep_violet, (fx, 58), 5)
        pygame.draw.circle(s, spark_white, (fx, 58), 2)
    
    # 环绕紫电火花
    for i in range(6):
        spark_angle = (i * 60 + t * 80) * 0.01745
        spark_dist = 42 + abs(math.sin(t * 3 + i)) * 8
        spark_x = 60 + math.cos(spark_angle) * spark_dist
        spark_y = 56 + math.sin(spark_angle) * spark_dist
        spark_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(spark_surf, (*lightning_purple, 180), (5, 5), 3)
        pygame.draw.circle(spark_surf, spark_white, (5, 5), 1)
        s.blit(spark_surf, (int(spark_x - 5), int(spark_y - 5)))
    
    _draw_charge_bar(s, 60, 60, 4, t, lightning_purple)


# =============================================================================
#   4. 晶簇巨像 - 水晶集群+棱镜折射（至尊品质）
# =============================================================================

def _render_turu_crystal(s, t, pulse):
    crystal_cyan = (100, 220, 255)
    crystal_pink = (255, 140, 200)
    crystal_white = (245, 252, 255)
    crystal_purple = (180, 140, 255)
    base_blue = (50, 90, 130)
    prism_colors = [(255, 120, 120), (255, 200, 100), (120, 255, 120), (100, 200, 255), (200, 120, 255)]
    
    # 棱镜折射光晕（彩虹旋转）
    prism_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i, col in enumerate(prism_colors):
        angle = t * 0.6 + i * 1.26
        glow_x = 60 + math.cos(angle) * 38
        glow_y = 60 + math.sin(angle) * 38
        pygame.draw.circle(prism_surf, (*col, 55), (int(glow_x), int(glow_y)), 18)
        # 光线轨迹
        for j in range(3):
            trail_angle = angle - j * 0.15
            trail_x = 60 + math.cos(trail_angle) * (38 - j * 5)
            trail_y = 60 + math.sin(trail_angle) * (38 - j * 5)
            pygame.draw.circle(prism_surf, (*col, 30 - j * 8), (int(trail_x), int(trail_y)), 10 - j * 2)
    s.blit(prism_surf, (0, 0))
    
    # 中央光晕
    for i in range(3):
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*crystal_cyan, 40 - i * 12), (60, 60), 45 - i * 10)
        s.blit(glow_surf, (0, 0))
    
    # 水晶簇身体（多个生长的晶体）
    crystals = [
        (60, 35, 28, -90),   # 顶部主晶
        (40, 50, 22, -120),  # 左上
        (80, 50, 22, -60),   # 右上
        (35, 65, 18, -150),  # 左
        (85, 65, 18, -30),   # 右
        (50, 75, 16, 150),   # 左下
        (70, 75, 16, 30),    # 右下
    ]
    for cx, cy, length, angle_deg in crystals:
        angle = angle_deg * 0.01745
        # 水晶尖端
        tip_x = cx + math.cos(angle) * length
        tip_y = cy + math.sin(angle) * length
        # 水晶宽度
        perp = angle + math.pi / 2
        w = length * 0.25
        base_left = (cx + math.cos(perp) * w, cy + math.sin(perp) * w)
        base_right = (cx - math.cos(perp) * w, cy - math.sin(perp) * w)
        
        # 选择颜色
        col = crystal_cyan if crystals.index((cx, cy, length, angle_deg)) % 2 == 0 else crystal_pink
        
        # 绘制水晶
        crystal_points = [base_left, (tip_x, tip_y), base_right]
        pygame.draw.polygon(s, col, crystal_points)
        pygame.draw.polygon(s, crystal_white, crystal_points, 1)
        
        # 内部折射线
        mid_x = (cx + tip_x) / 2
        mid_y = (cy + tip_y) / 2
        pygame.draw.line(s, (*crystal_white, 150), (int(cx), int(cy)), (int(mid_x), int(mid_y)), 1)
        
        # 尖端闪光
        sparkle = abs(math.sin(t * 3 + angle_deg * 0.1))
        if sparkle > 0.7:
            pygame.draw.circle(s, crystal_white, (int(tip_x), int(tip_y)), 3)
    
    # 核心水晶（大型菱形）
    core_pulse = abs(math.sin(t * 2.5))
    core_size = int(18 + core_pulse * 4)
    pygame.draw.polygon(s, crystal_cyan, [(60, 55 - core_size), (60 + core_size, 55), (60, 55 + core_size), (60 - core_size, 55)])
    pygame.draw.polygon(s, crystal_purple, [(60, 55 - core_size), (60 + core_size, 55), (60, 55 + core_size), (60 - core_size, 55)], 2)
    # 核心光芒
    pygame.draw.circle(s, crystal_white, (60, 55), int(8 + core_pulse * 3))
    pygame.draw.circle(s, (255, 255, 255), (60, 55), 4)
    
    # 六芒星光芒
    star_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(6):
        angle = (i * 60 + t * 40) * 0.01745
        ray_len = 12 + int(core_pulse * 6)
        ex = 60 + math.cos(angle) * ray_len
        ey = 55 + math.sin(angle) * ray_len
        pygame.draw.line(star_surf, (*crystal_white, 180), (60, 55), (int(ex), int(ey)), 2)
    s.blit(star_surf, (0, 0))
    
    # 水晶战拳
    for fx, mirror in [(16, 1), (104, -1)]:
        # 拳形水晶
        fist_points = [(fx, 48), (fx + 14*mirror, 56), (fx + 10*mirror, 68), (fx - 6*mirror, 66), (fx - 10*mirror, 54)]
        pygame.draw.polygon(s, crystal_pink, fist_points)
        pygame.draw.polygon(s, crystal_white, fist_points, 1)
        # 小水晶簇
        for i in range(3):
            c_angle = (-45 + i * 45) * 0.01745 * mirror
            c_len = 8
            cx2 = fx + math.cos(c_angle) * c_len
            cy2 = 58 + math.sin(c_angle) * c_len
            pygame.draw.line(s, crystal_cyan, (fx, 58), (int(cx2), int(cy2)), 3)
            pygame.draw.circle(s, crystal_white, (int(cx2), int(cy2)), 2)
    
    # 飘散的水晶碎片
    for i in range(6):
        shard_phase = (t * 0.4 + i * 0.5) % 2
        shard_angle = i * 60 * 0.01745 + t * 0.3
        shard_dist = 30 + shard_phase * 25
        shard_x = 60 + math.cos(shard_angle) * shard_dist
        shard_y = 55 + math.sin(shard_angle) * shard_dist
        shard_alpha = int(200 * (1 - shard_phase / 2))
        shard_col = prism_colors[i % 5]
        shard_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.polygon(shard_surf, (*shard_col, shard_alpha), [(5, 0), (10, 5), (5, 10), (0, 5)])
        s.blit(shard_surf, (int(shard_x - 5), int(shard_y - 5)))
    
    _draw_charge_bar(s, 60, 58, 4, t, crystal_cyan)


# =============================================================================
#   5. 翡翠巨兽 - 东方玉石+符文刻纹（至尊品质）
# =============================================================================

def _render_turu_jade(s, t, pulse):
    jade_green = (90, 170, 110)
    jade_dark = (45, 95, 65)
    jade_light = (170, 215, 180)
    jade_glow = (130, 200, 150)
    gold_rune = (230, 190, 70)
    gold_bright = (255, 230, 140)
    red_gem = (200, 50, 50)
    
    # 玉石光泽光晕
    for i in range(3):
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*jade_glow, 35 - i * 10), (60, 60), 50 - i * 12)
        s.blit(glow_surf, (0, 0))
    
    # 圆润的玉石身躯
    body_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    # 主体椭圆
    pygame.draw.ellipse(body_surf, jade_green, (28, 32, 64, 52))
    # 玉石层次
    pygame.draw.ellipse(body_surf, jade_dark, (28, 32, 64, 52), 3)
    s.blit(body_surf, (0, 0))
    
    # 玉石光泽高光（多层）
    highlight = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.ellipse(highlight, (*jade_light, 120), (38, 36, 28, 14))
    pygame.draw.ellipse(highlight, (*jade_light, 80), (42, 40, 18, 8))
    # 边缘反光
    pygame.draw.arc(highlight, (*jade_light, 100), (30, 34, 60, 48), 2.5, 3.5, 2)
    s.blit(highlight, (0, 0))
    
    # 金色符文圆环
    rune_r = 26 + int(pulse * 2)
    rune_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    # 双层符文圈
    pygame.draw.circle(rune_surf, (*gold_rune, 200), (60, 56), rune_r, 2)
    pygame.draw.circle(rune_surf, (*gold_rune, 150), (60, 56), rune_r - 6, 1)
    
    # 八卦符文
    for i in range(8):
        angle = i * 45 * 0.01745 + t * 0.3
        rx = 60 + math.cos(angle) * rune_r
        ry = 56 + math.sin(angle) * rune_r
        # 符文点
        pygame.draw.circle(rune_surf, gold_rune, (int(rx), int(ry)), 3)
        # 符文线（阴阳卦象）
        if i % 2 == 0:
            pygame.draw.line(rune_surf, gold_bright, (int(rx - 4), int(ry)), (int(rx + 4), int(ry)), 2)
        else:
            pygame.draw.line(rune_surf, gold_bright, (int(rx - 4), int(ry)), (int(rx - 1), int(ry)), 2)
            pygame.draw.line(rune_surf, gold_bright, (int(rx + 1), int(ry)), (int(rx + 4), int(ry)), 2)
    s.blit(rune_surf, (0, 0))
    
    # 核心太极符文
    core_pulse = abs(math.sin(t * 2))
    # 阴阳鱼
    pygame.draw.circle(s, jade_light, (60, 56), 12)
    pygame.draw.arc(s, jade_dark, (48, 44, 24, 24), math.pi/2, math.pi*1.5, 12)
    pygame.draw.circle(s, jade_dark, (60, 50), 6)
    pygame.draw.circle(s, jade_light, (60, 62), 6)
    pygame.draw.circle(s, jade_light, (60, 50), 2)
    pygame.draw.circle(s, jade_dark, (60, 62), 2)
    # 外圈
    pygame.draw.circle(s, gold_rune, (60, 56), 13, 2)
    
    # 翡翠头部（莲花冠）
    # 头部玉石
    pygame.draw.ellipse(s, jade_green, (44, 20, 32, 22))
    pygame.draw.ellipse(s, jade_dark, (44, 20, 32, 22), 2)
    # 莲花瓣冠
    for i in range(5):
        petal_angle = (-60 + i * 30) * 0.01745
        px = 60 + math.cos(petal_angle) * 12
        py = 22 + math.sin(petal_angle) * 8
        pygame.draw.ellipse(s, jade_light, (int(px - 5), int(py - 8), 10, 12))
        pygame.draw.ellipse(s, jade_green, (int(px - 5), int(py - 8), 10, 12), 1)
    # 中央宝石
    pygame.draw.circle(s, red_gem, (60, 26), 5)
    pygame.draw.circle(s, (255, 150, 150), (58, 24), 2)
    
    # 玉石之眼
    pygame.draw.ellipse(s, gold_rune, (52, 32, 16, 8))
    pygame.draw.ellipse(s, (40, 35, 30), (56, 34, 8, 4))
    pygame.draw.circle(s, jade_light, (54, 34), 1)
    
    # 翡翠战拳（圆润玉镯形）
    for fx, mirror in [(18, 1), (102, -1)]:
        # 玉镯拳
        pygame.draw.circle(s, jade_green, (fx, 56), 14)
        pygame.draw.circle(s, jade_dark, (fx, 56), 14, 2)
        # 高光
        pygame.draw.arc(s, jade_light, (fx - 12, 46, 24, 20), 0.5, 1.5, 3)
        # 金色符文
        pygame.draw.circle(s, gold_rune, (fx, 56), 8, 1)
        for j in range(4):
            r_angle = (j * 90 + t * 50) * 0.01745
            pygame.draw.circle(s, gold_bright, (int(fx + math.cos(r_angle) * 6), int(56 + math.sin(r_angle) * 6)), 2)
    
    # 符文能量粒子
    for i in range(8):
        particle_angle = (i * 45 + t * 25) * 0.01745
        particle_dist = 40 + abs(math.sin(t * 2 + i)) * 10
        px = 60 + math.cos(particle_angle) * particle_dist
        py = 56 + math.sin(particle_angle) * particle_dist
        particle_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, (*gold_bright, 150), (4, 4), 2)
        s.blit(particle_surf, (int(px - 4), int(py - 4)))
    
    _draw_charge_bar(s, 60, 60, 4, t, gold_rune)


# =============================================================================
#   6. 陨铁图鲁 - 陨石纹理+太空金属（至尊品质）
# =============================================================================

def _render_turu_meteor(s, t, pulse):
    meteor_gray = (75, 80, 90)
    meteor_dark = (45, 48, 55)
    meteor_brown = (95, 70, 55)
    space_blue = (60, 100, 180)
    space_glow = (100, 150, 220)
    fire_orange = (255, 160, 50)
    fire_red = (255, 80, 30)
    star_white = (240, 245, 255)
    
    # 再入大气层火焰尾迹（多层动态）
    trail_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for layer in range(3):
        for i in range(6 - layer):
            trail_y = 72 + i * 7 + layer * 3
            trail_phase = (t * 1.5 + i * 0.2 + layer * 0.3) % 1
            trail_alpha = int((160 - layer * 40) * (1 - trail_phase * 0.5))
            trail_width = 32 - i * 4 - layer * 3
            col = fire_orange if layer == 0 else (fire_red if layer == 1 else (255, 220, 100))
            pygame.draw.ellipse(trail_surf, (*col, trail_alpha),
                              (60 - trail_width//2 + math.sin(t * 3 + i) * 3, trail_y, trail_width, 8 - layer))
    s.blit(trail_surf, (0, 0))
    
    # 太空金属光晕
    for i in range(3):
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*space_blue, 35 - i * 10), (60, 52), 48 - i * 12)
        s.blit(glow_surf, (0, 0))
    
    # 陨石身躯（不规则撞击形态）
    body_points = []
    for i in range(12):
        angle = i * 30 * 0.01745
        r = 30 + random.Random(i + 99).randint(-6, 8) + math.sin(t * 0.3 + i * 0.5) * 2
        body_points.append((int(60 + math.cos(angle) * r), int(52 + math.sin(angle) * r * 0.85)))
    pygame.draw.polygon(s, meteor_gray, body_points)
    pygame.draw.polygon(s, meteor_dark, body_points, 2)
    
    # 熔融边缘
    for i in range(len(body_points)):
        if random.Random(i + 50).random() > 0.6:
            pygame.draw.circle(s, fire_orange, body_points[i], 3)
    
    # 陨石坑（多个）
    craters = [(50, 48, 6), (68, 52, 5), (58, 62, 7), (72, 45, 4), (45, 58, 5)]
    for cx, cy, cr in craters:
        # 坑边缘
        pygame.draw.circle(s, meteor_dark, (cx, cy), cr + 1)
        # 坑内部
        pygame.draw.circle(s, (35, 38, 45), (cx, cy), cr)
        # 坑底高光
        pygame.draw.circle(s, meteor_brown, (cx - 1, cy - 1), cr - 2)
    
    # 太空金属光泽
    metal_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.ellipse(metal_surf, (*space_glow, 70), (42, 38, 36, 18))
    pygame.draw.ellipse(metal_surf, (*star_white, 40), (48, 42, 24, 10))
    s.blit(metal_surf, (0, 0))
    
    # 核心（宇宙能量）
    core_pulse = abs(math.sin(t * 2.5))
    pygame.draw.circle(s, space_blue, (60, 52), int(10 + core_pulse * 3))
    pygame.draw.circle(s, space_glow, (60, 52), int(6 + core_pulse * 2))
    pygame.draw.circle(s, star_white, (60, 52), 3)
    # 能量环
    pygame.draw.circle(s, (*space_glow, 150), (60, 52), int(14 + core_pulse * 4), 1)
    
    # 头部（陨石碎片）
    head_points = [(52, 38), (68, 38), (72, 28), (60, 20), (48, 28)]
    pygame.draw.polygon(s, meteor_gray, head_points)
    pygame.draw.polygon(s, meteor_dark, head_points, 2)
    # 头部陨石坑
    pygame.draw.circle(s, (35, 38, 45), (60, 30), 4)
    # 太空金属眼
    pygame.draw.ellipse(s, space_blue, (52, 33, 16, 7))
    pygame.draw.ellipse(s, space_glow, (57, 35, 6, 3))
    
    # 陨铁战拳
    for fx, mirror in [(16, 1), (104, -1)]:
        # 拳头火焰尾迹
        for i in range(3):
            trail_alpha = 150 - i * 45
            pygame.draw.ellipse(s, (*fire_orange, trail_alpha),
                              (fx - 8 + i * 2 * mirror, 62 + i * 5, 16 - i * 3, 8 - i * 2))
        # 陨石拳
        fist_points = []
        for i in range(8):
            angle = i * 45 * 0.01745
            r = 12 + random.Random(i + fx).randint(-2, 3)
            fist_points.append((int(fx + math.cos(angle) * r), int(54 + math.sin(angle) * r)))
        pygame.draw.polygon(s, meteor_gray, fist_points)
        pygame.draw.polygon(s, meteor_dark, fist_points, 2)
        # 拳心能量
        pygame.draw.circle(s, space_blue, (fx, 54), 5)
        pygame.draw.circle(s, fire_orange, (fx, 54), 3)
    
    # 星尘粒子
    for i in range(10):
        star_phase = (t * 0.6 + i * 0.3) % 1.5
        star_angle = (i * 36 + t * 15) * 0.01745
        star_dist = 25 + star_phase * 30
        sx = 60 + math.cos(star_angle) * star_dist
        sy = 52 + math.sin(star_angle) * star_dist * 0.7
        star_alpha = int(200 * (1 - star_phase / 1.5))
        star_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(star_surf, (*star_white, star_alpha), (3, 3), 2)
        s.blit(star_surf, (int(sx - 3), int(sy - 3)))
    
    _draw_charge_bar(s, 60, 58, 4, t, space_blue)


# =============================================================================
#   7. 沙岩古神 - 沙漠风化+埃及图腾（至尊品质）
# =============================================================================

def _render_turu_sandstone(s, t, pulse):
    sand_yellow = (215, 185, 125)
    sand_dark = (165, 135, 85)
    sand_light = (240, 220, 180)
    egypt_gold = (230, 190, 60)
    egypt_bright = (255, 230, 130)
    turquoise = (70, 180, 175)
    lapis = (40, 80, 160)
    hieroglyph = (180, 140, 80)
    
    # 沙尘光晕
    for i in range(4):
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*sand_yellow, 35 - i * 8), (60, 60), 52 - i * 10)
        s.blit(glow_surf, (0, 0))
    
    # 金字塔形身躯
    pyramid_points = [(60, 25), (95, 85), (25, 85)]
    pygame.draw.polygon(s, sand_yellow, pyramid_points)
    pygame.draw.polygon(s, sand_dark, pyramid_points, 3)
    
    # 砖块纹理
    for row in range(4):
        y = 45 + row * 12
        for col in range(3 + row):
            x = 60 - (3 + row) * 8 // 2 + col * 8 + (row % 2) * 4
            if 30 < x < 90:
                pygame.draw.rect(s, sand_dark, (x, y, 7, 5), 1)
    
    # 荷鲁斯之眼（核心）
    eye_cx, eye_cy = 60, 55
    # 眼眶
    pygame.draw.ellipse(s, egypt_gold, (eye_cx - 14, eye_cy - 6, 28, 14))
    pygame.draw.ellipse(s, (35, 30, 25), (eye_cx - 10, eye_cy - 4, 20, 10))
    # 瞳孔
    pygame.draw.circle(s, lapis, (eye_cx, eye_cy), 5)
    pygame.draw.circle(s, turquoise, (eye_cx, eye_cy), 3)
    pygame.draw.circle(s, (200, 255, 255), (eye_cx - 1, eye_cy - 1), 1)
    # 眼线（荷鲁斯标志）
    pygame.draw.line(s, egypt_gold, (eye_cx + 14, eye_cy), (eye_cx + 25, eye_cy + 12), 3)
    pygame.draw.line(s, egypt_gold, (eye_cx + 20, eye_cy + 6), (eye_cx + 22, eye_cy + 15), 2)
    pygame.draw.line(s, egypt_gold, (eye_cx - 14, eye_cy), (eye_cx - 22, eye_cy + 8), 3)
    # 眉毛
    pygame.draw.arc(s, egypt_gold, (eye_cx - 16, eye_cy - 12, 32, 16), 0.3, 2.8, 2)
    
    # 法老头饰（尼美斯头巾）
    head_points = [(40, 42), (80, 42), (85, 25), (60, 12), (35, 25)]
    pygame.draw.polygon(s, egypt_gold, head_points)
    pygame.draw.polygon(s, sand_dark, head_points, 2)
    # 条纹
    for i in range(5):
        stripe_y = 20 + i * 5
        pygame.draw.line(s, lapis, (45 + i * 2, stripe_y), (75 - i * 2, stripe_y), 2)
    # 眼镜蛇装饰
    pygame.draw.ellipse(s, egypt_gold, (56, 8, 8, 12))
    pygame.draw.circle(s, turquoise, (60, 12), 3)
    pygame.draw.circle(s, (255, 50, 50), (60, 10), 2)
    
    # 象形文字装饰（两侧柱）
    for side, sx in [(-1, 32), (1, 88)]:
        # 柱子
        pygame.draw.rect(s, sand_dark, (sx - 4, 45, 8, 35))
        pygame.draw.rect(s, sand_yellow, (sx - 3, 46, 6, 33))
        # 象形文字
        glyphs = [(0, 0), (0, 8), (0, 16), (0, 24)]
        for i, (gx, gy) in enumerate(glyphs):
            glyph_type = (i + int(t * 0.5)) % 4
            gy_pos = 48 + gy
            if glyph_type == 0:  # 安卡符
                pygame.draw.circle(s, hieroglyph, (sx, gy_pos), 2)
                pygame.draw.line(s, hieroglyph, (sx, gy_pos + 2), (sx, gy_pos + 6), 1)
            elif glyph_type == 1:  # 眼睛
                pygame.draw.ellipse(s, hieroglyph, (sx - 2, gy_pos, 4, 2))
            elif glyph_type == 2:  # 鸟
                pygame.draw.arc(s, hieroglyph, (sx - 3, gy_pos - 2, 6, 4), 0, math.pi, 1)
            else:  # 波浪
                for j in range(2):
                    pygame.draw.arc(s, hieroglyph, (sx - 3 + j * 3, gy_pos, 3, 2), 0, math.pi, 1)
    
    # 沙岩战拳（方形石块）
    for fx, mirror in [(14, 1), (106, -1)]:
        # 沙尘环绕
        for i in range(4):
            dust_angle = (i * 90 + t * 60) * 0.01745
            dust_dist = 16 + abs(math.sin(t * 2 + i)) * 4
            dx = fx + math.cos(dust_angle) * dust_dist
            dy = 58 + math.sin(dust_angle) * dust_dist
            dust_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(dust_surf, (*sand_light, 100), (4, 4), 2)
            s.blit(dust_surf, (int(dx - 4), int(dy - 4)))
        
        # 方形拳头
        pygame.draw.rect(s, sand_yellow, (fx - 12, 48, 24, 22))
        pygame.draw.rect(s, sand_dark, (fx - 12, 48, 24, 22), 2)
        # 砖纹
        pygame.draw.line(s, sand_dark, (fx - 10, 55), (fx + 10, 55), 1)
        pygame.draw.line(s, sand_dark, (fx - 10, 62), (fx + 10, 62), 1)
        # 小型荷鲁斯眼
        pygame.draw.ellipse(s, egypt_gold, (fx - 5, 52, 10, 6))
        pygame.draw.circle(s, lapis, (fx, 55), 2)
    
    # 漂浮沙尘
    for i in range(12):
        sand_phase = (t * 0.4 + i * 0.25) % 1.5
        sand_angle = (i * 30 + math.sin(t + i) * 20) * 0.01745
        sand_dist = 35 + sand_phase * 20
        sand_x = 60 + math.cos(sand_angle) * sand_dist
        sand_y = 55 + math.sin(sand_angle) * sand_dist
        sand_alpha = int(150 * (1 - sand_phase / 1.5))
        sand_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(sand_surf, (*sand_light, sand_alpha), (3, 3), random.Random(i).randint(1, 2))
        s.blit(sand_surf, (int(sand_x - 3), int(sand_y - 3)))
    
    _draw_charge_bar(s, 60, 62, 4, t, egypt_gold)


# =============================================================================
#   8. 冰川巨人 - 冰晶结构+寒霜光芒（至尊品质）
# =============================================================================

def _render_turu_ice(s, t, pulse):
    ice_blue = (170, 215, 250)
    ice_dark = (90, 140, 190)
    ice_deep = (60, 100, 160)
    frost_white = (245, 252, 255)
    core_cyan = (100, 220, 255)
    aurora_green = (150, 255, 200)
    aurora_purple = (200, 150, 255)
    
    # 极光光晕
    aurora_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(3):
        aurora_phase = (t * 0.5 + i * 0.8) % 2
        aurora_col = aurora_green if i % 2 == 0 else aurora_purple
        aurora_y = 30 + int(aurora_phase * 20) + i * 15
        pygame.draw.ellipse(aurora_surf, (*aurora_col, 40), (20 + i * 5, aurora_y, 80 - i * 10, 20))
    s.blit(aurora_surf, (0, 0))
    
    # 寒霜光晕
    for i in range(4):
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*ice_blue, 45 - i * 10), (60, 58), 50 - i * 10)
        s.blit(glow_surf, (0, 0))
    
    # 冰晶身躯（六边形基础）
    hex_points = []
    for i in range(6):
        angle = i * 60 * 0.01745 - 30 * 0.01745
        r = 34 + math.sin(t * 0.5 + i) * 2
        hex_points.append((int(60 + math.cos(angle) * r), int(58 + math.sin(angle) * r)))
    pygame.draw.polygon(s, ice_blue, hex_points)
    pygame.draw.polygon(s, frost_white, hex_points, 2)
    
    # 冰晶内部结构
    inner_hex = []
    for i in range(6):
        angle = i * 60 * 0.01745
        r = 20
        inner_hex.append((int(60 + math.cos(angle) * r), int(58 + math.sin(angle) * r)))
    pygame.draw.polygon(s, ice_dark, inner_hex, 1)
    # 连接线
    for i in range(6):
        pygame.draw.line(s, ice_dark, hex_points[i], inner_hex[i], 1)
    
    # 冰晶纹理
    for i in range(6):
        angle = i * 60 * 0.01745
        # 主纹理线
        pygame.draw.line(s, (*frost_white, 150), (60, 58),
                        (int(60 + math.cos(angle) * 30), int(58 + math.sin(angle) * 30)), 1)
        # 分支冰晶
        for j in range(2):
            branch_len = 8 + j * 4
            branch_angle = angle + (0.4 if j % 2 == 0 else -0.4)
            mid_x = 60 + math.cos(angle) * (15 + j * 8)
            mid_y = 58 + math.sin(angle) * (15 + j * 8)
            pygame.draw.line(s, (*ice_dark, 180), (int(mid_x), int(mid_y)),
                           (int(mid_x + math.cos(branch_angle) * branch_len),
                            int(mid_y + math.sin(branch_angle) * branch_len)), 1)
    
    # 冰霜核心
    core_pulse = abs(math.sin(t * 2.5))
    # 核心光晕
    core_glow = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.circle(core_glow, (*core_cyan, 100), (25, 25), int(15 + core_pulse * 5))
    pygame.draw.circle(core_glow, (*frost_white, 80), (25, 25), int(10 + core_pulse * 3))
    s.blit(core_glow, (35, 33))
    # 核心
    pygame.draw.circle(s, core_cyan, (60, 58), int(10 + core_pulse * 2))
    pygame.draw.circle(s, frost_white, (60, 58), 5)
    # 六芒星
    for i in range(6):
        angle = (i * 60 + t * 30) * 0.01745
        star_len = 6 + int(core_pulse * 4)
        pygame.draw.line(s, frost_white, (60, 58),
                        (int(60 + math.cos(angle) * star_len), int(58 + math.sin(angle) * star_len)), 2)
    
    # 冰晶尖刺头部
    head_crystal = [(60, 15), (72, 32), (68, 42), (52, 42), (48, 32)]
    pygame.draw.polygon(s, ice_blue, head_crystal)
    pygame.draw.polygon(s, frost_white, head_crystal, 2)
    # 头部内部纹理
    pygame.draw.line(s, ice_dark, (60, 20), (60, 38), 1)
    pygame.draw.line(s, ice_dark, (54, 35), (66, 35), 1)
    # 冰晶眼
    pygame.draw.ellipse(s, core_cyan, (53, 30, 14, 8))
    pygame.draw.ellipse(s, frost_white, (57, 32, 6, 4))
    
    # 肩部冰刺
    for side, sx in [(-1, 35), (1, 85)]:
        spike_points = [(sx, 50), (sx + side * 12, 42), (sx + side * 8, 55)]
        pygame.draw.polygon(s, ice_blue, spike_points)
        pygame.draw.polygon(s, frost_white, spike_points, 1)
    
    # 冰晶战拳
    for fx, mirror in [(14, 1), (106, -1)]:
        # 寒霜光环
        frost_aura = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(frost_aura, (*ice_blue, 60), (20, 20), 18)
        s.blit(frost_aura, (fx - 20, 40))
        
        # 六边形拳头
        fist_hex = []
        for i in range(6):
            angle = (i * 60 + 30 * mirror) * 0.01745
            r = 13
            fist_hex.append((int(fx + math.cos(angle) * r), int(58 + math.sin(angle) * r)))
        pygame.draw.polygon(s, ice_blue, fist_hex)
        pygame.draw.polygon(s, frost_white, fist_hex, 2)
        # 拳心
        pygame.draw.circle(s, core_cyan, (fx, 58), 5)
        pygame.draw.circle(s, frost_white, (fx, 58), 2)
    
    # 冰霜飘落粒子
    for i in range(8):
        flake_phase = (t * 0.6 + i * 0.35) % 1.5
        flake_x = 25 + i * 10 + math.sin(t * 1.5 + i) * 8
        flake_y = 15 + flake_phase * 60
        flake_alpha = int(200 * (1 - flake_phase / 1.5))
        flake_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        # 雪花形状
        for j in range(6):
            angle = j * 60 * 0.01745
            pygame.draw.line(flake_surf, (*frost_white, flake_alpha), (5, 5),
                           (int(5 + math.cos(angle) * 3), int(5 + math.sin(angle) * 3)), 1)
        s.blit(flake_surf, (int(flake_x - 5), int(flake_y - 5)))
    
    _draw_charge_bar(s, 60, 62, 4, t, core_cyan)


# =============================================================================
#   9. 火山领主 - 火山熔岩+喷发特效（至尊品质）
# =============================================================================

def _render_turu_volcanic(s, t, pulse):
    volcano_black = (35, 28, 22)
    volcano_gray = (60, 50, 45)
    lava_red = (255, 50, 15)
    lava_orange = (255, 130, 30)
    lava_yellow = (255, 210, 60)
    smoke_gray = (70, 65, 60)
    smoke_dark = (45, 42, 40)
    ember = (255, 180, 80)
    
    # 火山喷发光晕
    for i in range(5):
        glow_r = 58 - i * 9 + int(pulse * 10)
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*lava_red, 65 - i * 12), (60, 60), glow_r)
        s.blit(glow_surf, (0, 0))
    
    # 烟柱
    smoke_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for layer in range(4):
        for i in range(4 - layer):
            smoke_phase = (t * 0.8 + i * 0.4 + layer * 0.2) % 2
            smoke_y = 35 - smoke_phase * 25 - layer * 8
            smoke_x = 60 + math.sin(t * 2 + i + layer) * (8 + layer * 3)
            smoke_r = 10 + layer * 3 - int(smoke_phase * 3)
            smoke_alpha = int((80 - layer * 15) * (1 - smoke_phase / 2))
            col = smoke_gray if layer < 2 else smoke_dark
            pygame.draw.circle(smoke_surf, (*col, smoke_alpha), (int(smoke_x), int(smoke_y)), smoke_r)
    s.blit(smoke_surf, (0, 0))
    
    # 火山锥形身躯
    volcano_points = [(30, 88), (90, 88), (82, 45), (60, 35), (38, 45)]
    pygame.draw.polygon(s, volcano_black, volcano_points)
    pygame.draw.polygon(s, volcano_gray, volcano_points, 2)
    
    # 岩层纹理
    for i in range(4):
        layer_y = 55 + i * 10
        pygame.draw.line(s, volcano_gray, (35 + i * 3, layer_y), (85 - i * 3, layer_y), 1)
    
    # 火山口
    crater_points = [(48, 38), (72, 38), (78, 45), (60, 50), (42, 45)]
    pygame.draw.polygon(s, volcano_gray, crater_points)
    pygame.draw.polygon(s, lava_red, crater_points, 2)
    # 熔岩池
    lava_pulse = abs(math.sin(t * 3))
    pygame.draw.ellipse(s, lava_red, (50, 40, 20, 8))
    pygame.draw.ellipse(s, lava_orange, (53, 42, 14, 5))
    pygame.draw.ellipse(s, lava_yellow, (56, 43, 8, 3))
    
    # 熔岩流
    lava_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(5):
        seed = random.Random(i + 33)
        start_x = 50 + i * 5
        # 蜿蜒流动
        flow_points = [(start_x, 48)]
        x, y = start_x, 48
        for seg in range(4):
            x += seed.randint(-4, 4) + (i - 2) * 2
            y += 10 + seed.randint(-2, 2)
            flow_points.append((x, y))
        # 流动动画
        flow_phase = (t * 1.5 + i * 0.3) % 1
        for j in range(len(flow_points) - 1):
            seg_phase = (flow_phase + j * 0.2) % 1
            col = lava_yellow if seg_phase > 0.6 else (lava_orange if seg_phase > 0.3 else lava_red)
            alpha = int(220 - j * 30)
            pygame.draw.line(lava_surf, (*col, alpha), flow_points[j], flow_points[j + 1], 4 - j)
    s.blit(lava_surf, (0, 0))
    
    # 喷发岩块
    erupt_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(6):
        erupt_phase = (t * 1.2 + i * 0.5) % 1.5
        if erupt_phase < 1:
            erupt_angle = (-90 + (i - 3) * 25) * 0.01745
            erupt_dist = 15 + erupt_phase * 40
            erupt_x = 60 + math.cos(erupt_angle) * erupt_dist
            erupt_y = 42 + math.sin(erupt_angle) * erupt_dist + erupt_phase * erupt_phase * 20  # 抛物线
            erupt_r = int(5 * (1 - erupt_phase))
            if erupt_y < 70:  # 只显示未落地的
                # 岩块
                pygame.draw.circle(erupt_surf, volcano_black, (int(erupt_x), int(erupt_y)), erupt_r + 1)
                pygame.draw.circle(erupt_surf, lava_red, (int(erupt_x), int(erupt_y)), erupt_r)
                # 火焰尾迹
                tail_len = erupt_r * 2
                pygame.draw.line(erupt_surf, (*lava_orange, 150), (int(erupt_x), int(erupt_y)),
                               (int(erupt_x - math.cos(erupt_angle) * tail_len),
                                int(erupt_y - math.sin(erupt_angle) * tail_len + erupt_phase * 5)), 2)
    s.blit(erupt_surf, (0, 0))
    
    # 核心熔岩室
    pygame.draw.ellipse(s, lava_red, (48, 58, 24, 16))
    pygame.draw.ellipse(s, lava_orange, (52, 61, 16, 10))
    pygame.draw.ellipse(s, lava_yellow, (56, 64, 8, 5))
    
    # 熔岩战拳
    for fx, mirror in [(12, 1), (108, -1)]:
        # 火焰光晕
        flame_glow = pygame.Surface((50, 50), pygame.SRCALPHA)
        for i in range(3):
            pygame.draw.circle(flame_glow, (*lava_red, 80 - i * 25), (25, 25), 20 - i * 4)
        s.blit(flame_glow, (fx - 25, 35))
        
        # 火山岩拳
        pygame.draw.circle(s, volcano_black, (fx, 60), 15)
        pygame.draw.circle(s, volcano_gray, (fx, 60), 15, 2)
        # 熔岩裂纹
        for j in range(4):
            crack_angle = (j * 90 + t * 40) * 0.01745
            pygame.draw.line(s, lava_red, (fx, 60),
                           (int(fx + math.cos(crack_angle) * 12),
                            int(60 + math.sin(crack_angle) * 12)), 2)
        # 拳心熔岩
        pygame.draw.circle(s, lava_orange, (fx, 60), 6)
        pygame.draw.circle(s, lava_yellow, (fx, 60), 3)
    
    # 火星飞溅
    ember_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(15):
        ember_phase = (t * 1.5 + i * 0.2) % 1
        ember_angle = (i * 24 + t * 30) * 0.01745
        ember_dist = 30 + ember_phase * 35
        ember_x = 60 + math.cos(ember_angle) * ember_dist
        ember_y = 55 + math.sin(ember_angle) * ember_dist - ember_phase * 15
        ember_alpha = int(255 * (1 - ember_phase))
        pygame.draw.circle(ember_surf, (*ember, ember_alpha), (int(ember_x), int(ember_y)), 2)
    s.blit(ember_surf, (0, 0))
    
    _draw_charge_bar(s, 60, 68, 4, t, lava_yellow)


# =============================================================================
#   10. 钻石核心 - 钻石切面+虹光反射（至尊品质）
# =============================================================================

def _render_turu_diamond(s, t, pulse):
    diamond_white = (245, 248, 255)
    diamond_blue = (200, 220, 255)
    diamond_edge = (180, 200, 240)
    rainbow_colors = [(255, 140, 140), (255, 220, 140), (140, 255, 140), (140, 220, 255), (220, 140, 255)]
    sparkle_white = (255, 255, 255)
    inner_blue = (220, 235, 255)
    
    # 虹光反射光晕
    rainbow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i, col in enumerate(rainbow_colors):
        angle = t * 0.7 + i * 1.26
        ref_x = 60 + math.cos(angle) * 42
        ref_y = 58 + math.sin(angle) * 42
        pygame.draw.circle(rainbow_surf, (*col, 55), (int(ref_x), int(ref_y)), 14)
        # 光线尾迹
        for j in range(3):
            trail_angle = angle - (j + 1) * 0.12
            trail_x = 60 + math.cos(trail_angle) * (42 - j * 4)
            trail_y = 58 + math.sin(trail_angle) * (42 - j * 4)
            pygame.draw.circle(rainbow_surf, (*col, 30 - j * 8), (int(trail_x), int(trail_y)), 10 - j * 2)
    s.blit(rainbow_surf, (0, 0))
    
    # 中央光晕
    for i in range(3):
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*diamond_blue, 40 - i * 12), (60, 58), 48 - i * 12)
        s.blit(glow_surf, (0, 0))
    
    # 钻石切面身躯（八边形）
    oct_points = []
    for i in range(8):
        angle = (i * 45 + 22.5) * 0.01745
        r = 32
        oct_points.append((int(60 + math.cos(angle) * r), int(58 + math.sin(angle) * r)))
    pygame.draw.polygon(s, diamond_white, oct_points)
    pygame.draw.polygon(s, diamond_edge, oct_points, 2)
    
    # 钻石切面（多层）
    inner_oct = []
    for i in range(8):
        angle = i * 45 * 0.01745
        r = 18
        inner_oct.append((int(60 + math.cos(angle) * r), int(58 + math.sin(angle) * r)))
    pygame.draw.polygon(s, inner_blue, inner_oct, 1)
    
    # 切面连接线
    for i in range(8):
        pygame.draw.line(s, diamond_edge, oct_points[i], inner_oct[i], 1)
    
    # 内部折射
    refract_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(4):
        ref_angle = (i * 90 + t * 25) * 0.01745
        ref_points = [
            (60, 58),
            (int(60 + math.cos(ref_angle) * 12), int(58 + math.sin(ref_angle) * 12)),
            (int(60 + math.cos(ref_angle + 0.4) * 20), int(58 + math.sin(ref_angle + 0.4) * 20))
        ]
        col = rainbow_colors[i % 5]
        pygame.draw.polygon(refract_surf, (*col, 60), ref_points)
    s.blit(refract_surf, (0, 0))
    
    # 核心光点
    core_pulse = abs(math.sin(t * 3))
    pygame.draw.circle(s, sparkle_white, (60, 58), int(10 + core_pulse * 4))
    pygame.draw.circle(s, diamond_blue, (60, 58), 6)
    pygame.draw.circle(s, sparkle_white, (60, 58), 3)
    
    # 十字星芒
    star_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(4):
        angle = (i * 90 + t * 50) * 0.01745
        star_len = 10 + int(core_pulse * 8)
        pygame.draw.line(star_surf, (*sparkle_white, 200), (60, 58),
                        (int(60 + math.cos(angle) * star_len), int(58 + math.sin(angle) * star_len)), 3)
        # 次星芒
        for j in range(2):
            sub_angle = angle + (0.3 if j == 0 else -0.3)
            sub_len = star_len * 0.5
            pygame.draw.line(star_surf, (*sparkle_white, 120), (60, 58),
                           (int(60 + math.cos(sub_angle) * sub_len), int(58 + math.sin(sub_angle) * sub_len)), 1)
    s.blit(star_surf, (0, 0))
    
    # 钻石头部
    head_points = [(60, 18), (75, 35), (70, 44), (50, 44), (45, 35)]
    pygame.draw.polygon(s, diamond_white, head_points)
    pygame.draw.polygon(s, diamond_edge, head_points, 2)
    # 头部切面
    pygame.draw.line(s, diamond_edge, (60, 22), (60, 40), 1)
    pygame.draw.line(s, diamond_edge, (52, 38), (68, 38), 1)
    # 头部高光
    pygame.draw.polygon(s, (*sparkle_white, 100), [(58, 25), (65, 32), (55, 32)])
    # 钻石眼
    pygame.draw.ellipse(s, diamond_blue, (52, 32, 16, 8))
    pygame.draw.ellipse(s, sparkle_white, (57, 34, 6, 4))
    
    # 钻石战拳
    for fx, mirror in [(14, 1), (106, -1)]:
        # 虹光环绕
        for i, col in enumerate(rainbow_colors[:3]):
            r_angle = (i * 120 + t * 60 + fx) * 0.01745
            rx = fx + math.cos(r_angle) * 16
            ry = 58 + math.sin(r_angle) * 16
            pygame.draw.circle(s, (*col, 80), (int(rx), int(ry)), 4)
        
        # 菱形拳
        fist_points = [(fx, 46), (fx + 12 * mirror, 58), (fx, 70), (fx - 8 * mirror, 58)]
        pygame.draw.polygon(s, diamond_white, fist_points)
        pygame.draw.polygon(s, diamond_edge, fist_points, 2)
        # 切面线
        pygame.draw.line(s, diamond_edge, (fx, 50), (fx, 66), 1)
        # 拳心星芒
        pygame.draw.circle(s, sparkle_white, (fx, 58), 5)
        for j in range(4):
            s_angle = (j * 90 + t * 80) * 0.01745
            pygame.draw.line(s, sparkle_white, (fx, 58),
                           (int(fx + math.cos(s_angle) * 8), int(58 + math.sin(s_angle) * 8)), 1)
    
    # 飘散钻石碎片
    for i in range(8):
        shard_phase = (t * 0.5 + i * 0.4) % 2
        shard_angle = (i * 45 + t * 20) * 0.01745
        shard_dist = 35 + shard_phase * 20
        shard_x = 60 + math.cos(shard_angle) * shard_dist
        shard_y = 58 + math.sin(shard_angle) * shard_dist
        shard_alpha = int(200 * (1 - shard_phase / 2))
        shard_col = rainbow_colors[i % 5]
        shard_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.polygon(shard_surf, (*shard_col, shard_alpha), [(5, 0), (10, 5), (5, 10), (0, 5)])
        pygame.draw.polygon(shard_surf, (*sparkle_white, shard_alpha // 2), [(5, 0), (10, 5), (5, 10), (0, 5)], 1)
        s.blit(shard_surf, (int(shard_x - 5), int(shard_y - 5)))
    
    _draw_charge_bar(s, 60, 62, 4, t, diamond_blue)


# =============================================================================
#   11. 锈蚀远古 - 生锈金属+苔藓覆盖（至尊品质）
# =============================================================================

def _render_turu_rusty(s, t, pulse):
    rust_orange = (175, 95, 55)
    rust_brown = (115, 65, 35)
    rust_dark = (75, 45, 25)
    metal_gray = (95, 90, 85)
    metal_dark = (55, 52, 48)
    moss_green = (55, 95, 45)
    moss_dark = (35, 65, 30)
    moss_light = (80, 130, 60)
    decay_yellow = (140, 120, 60)
    
    # 锈迹光晕（暗淡）
    for i in range(2):
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*rust_orange, 25 - i * 10), (60, 58), 48 - i * 15)
        s.blit(glow_surf, (0, 0))
    
    # 锈蚀身躯
    body_points = []
    for i in range(12):
        angle = i * 30 * 0.01745
        r = 32 + random.Random(i + 55).randint(-5, 6)
        body_points.append((int(60 + math.cos(angle) * r), int(58 + math.sin(angle) * r)))
    pygame.draw.polygon(s, rust_brown, body_points)
    pygame.draw.polygon(s, rust_dark, body_points, 2)
    
    # 锈斑纹理（多层）
    rust_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for layer in range(2):
        for i in range(8 - layer * 3):
            seed = random.Random(i + layer * 20 + 88)
            rx = 60 + seed.randint(-25, 25)
            ry = 58 + seed.randint(-22, 22)
            rr = seed.randint(4, 9) - layer * 2
            col = rust_orange if layer == 0 else decay_yellow
            pygame.draw.circle(rust_surf, (*col, 150 - layer * 50), (rx, ry), rr)
    s.blit(rust_surf, (0, 0))
    
    # 金属剥落痕迹
    for i in range(5):
        seed = random.Random(i + 111)
        px = 60 + seed.randint(-20, 20)
        py = 58 + seed.randint(-18, 18)
        peel_points = []
        for j in range(4):
            peel_points.append((px + seed.randint(-5, 5), py + seed.randint(-5, 5)))
        pygame.draw.polygon(s, metal_gray, peel_points)
        pygame.draw.polygon(s, metal_dark, peel_points, 1)
    
    # 苔藓覆盖（有机生长）
    moss_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    moss_clusters = [(42, 50), (75, 52), (50, 72), (68, 68), (55, 45), (65, 78)]
    for mx, my in moss_clusters:
        # 苔藓团
        for j in range(4 + random.Random(mx + my).randint(0, 3)):
            seed = random.Random(j + mx * my)
            ox = mx + seed.randint(-6, 6)
            oy = my + seed.randint(-5, 5)
            or_ = seed.randint(2, 5)
            col = moss_green if j % 2 == 0 else moss_dark
            pygame.draw.circle(moss_surf, col, (ox, oy), or_)
        # 苔藓高光
        pygame.draw.circle(moss_surf, moss_light, (mx, my - 2), 2)
    s.blit(moss_surf, (0, 0))
    
    # 藤蔓延伸
    vine_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(3):
        seed = random.Random(i + 222)
        vx, vy = 40 + i * 20, 75
        for seg in range(5):
            nvx = vx + seed.randint(-3, 3)
            nvy = vy - 8 - seed.randint(0, 3)
            pygame.draw.line(vine_surf, moss_dark, (vx, vy), (nvx, nvy), 2)
            # 小叶
            if seg % 2 == 0:
                pygame.draw.circle(vine_surf, moss_green, (nvx + 3, nvy), 3)
            vx, vy = nvx, nvy
    s.blit(vine_surf, (0, 0))
    
    # 残破核心（暗淡闪烁）
    core_flicker = abs(math.sin(t * 1.5)) * 0.3 + 0.2  # 微弱闪烁
    core_col = (int(rust_orange[0] * core_flicker), int(rust_orange[1] * core_flicker), int(rust_orange[2] * core_flicker))
    pygame.draw.circle(s, metal_dark, (60, 58), 12)
    pygame.draw.circle(s, rust_dark, (60, 58), 12, 2)
    pygame.draw.circle(s, core_col, (60, 58), 7)
    # 裂纹
    for i in range(3):
        crack_angle = (i * 120 + 30) * 0.01745
        pygame.draw.line(s, rust_dark, (60, 58),
                        (int(60 + math.cos(crack_angle) * 10), int(58 + math.sin(crack_angle) * 10)), 2)
    
    # 残破头部
    head_points = [(48, 42), (72, 42), (75, 30), (60, 22), (45, 30)]
    pygame.draw.polygon(s, rust_brown, head_points)
    pygame.draw.polygon(s, rust_dark, head_points, 2)
    # 头部锈蚀
    pygame.draw.circle(s, rust_orange, (55, 35), 5)
    pygame.draw.circle(s, decay_yellow, (68, 38), 4)
    # 苔藓覆盖
    for j in range(3):
        pygame.draw.circle(s, moss_green, (50 + j * 8, 40), 3)
    # 暗淡的眼（几乎熄灭）
    eye_dim = int(80 + 40 * core_flicker)
    pygame.draw.ellipse(s, (eye_dim, eye_dim // 2, eye_dim // 4), (52, 30, 16, 8))
    pygame.draw.ellipse(s, (50, 45, 40), (56, 32, 8, 4))
    
    # 锈蚀战拳
    for fx, mirror in [(16, 1), (104, -1)]:
        # 锈迹拳头
        fist_points = []
        for i in range(8):
            angle = i * 45 * 0.01745
            r = 13 + random.Random(i + fx).randint(-2, 3)
            fist_points.append((int(fx + math.cos(angle) * r), int(58 + math.sin(angle) * r)))
        pygame.draw.polygon(s, rust_brown, fist_points)
        pygame.draw.polygon(s, rust_dark, fist_points, 2)
        # 锈斑
        pygame.draw.circle(s, rust_orange, (fx + 3 * mirror, 55), 4)
        pygame.draw.circle(s, decay_yellow, (fx - 2 * mirror, 62), 3)
        # 苔藓
        pygame.draw.circle(s, moss_green, (fx + 5 * mirror, 60), 3)
        pygame.draw.circle(s, moss_dark, (fx + 4 * mirror, 58), 2)
    
    # 飘落的锈屑
    for i in range(6):
        rust_phase = (t * 0.3 + i * 0.5) % 2
        rust_x = 35 + i * 10 + math.sin(t * 0.8 + i) * 5
        rust_y = 30 + rust_phase * 50
        rust_alpha = int(150 * (1 - rust_phase / 2))
        rust_frag = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(rust_frag, (*rust_orange, rust_alpha), (3, 3), 2)
        s.blit(rust_frag, (int(rust_x), int(rust_y)))
    
    _draw_charge_bar(s, 60, 62, 2, t, rust_orange)  # 只有2格（损坏状态）


# =============================================================================
#   12. 黄金图鲁 - 镀金表面+圣光环绕（至尊品质）
# =============================================================================

def _render_turu_golden(s, t, pulse):
    gold_bright = (255, 220, 90)
    gold_main = (230, 190, 60)
    gold_dark = (180, 140, 30)
    gold_shadow = (140, 100, 20)
    gold_light = (255, 245, 180)
    holy_white = (255, 255, 245)
    holy_glow = (255, 250, 220)
    ruby_red = (220, 50, 60)
    sapphire = (60, 100, 200)
    emerald = (50, 180, 80)
    
    # 圣光环绕
    halo_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(5):
        angle = t * 1.0 + i * 1.26
        halo_x = 60 + math.cos(angle) * 48
        halo_y = 58 + math.sin(angle) * 48
        pygame.draw.circle(halo_surf, (*gold_light, 70), (int(halo_x), int(halo_y)), 12)
        # 光线尾迹
        for j in range(4):
            trail_angle = angle - (j + 1) * 0.1
            trail_x = 60 + math.cos(trail_angle) * (48 - j * 3)
            trail_y = 58 + math.sin(trail_angle) * (48 - j * 3)
            pygame.draw.circle(halo_surf, (*holy_glow, 40 - j * 8), (int(trail_x), int(trail_y)), 8 - j)
    s.blit(halo_surf, (0, 0))
    
    # 圣光光晕
    for i in range(4):
        glow_r = 55 - i * 11 + int(pulse * 5)
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*gold_bright, 55 - i * 12), (60, 58), glow_r)
        s.blit(glow_surf, (0, 0))
    
    # 黄金身躯
    body_points = []
    for i in range(12):
        angle = i * 30 * 0.01745
        r = 34
        body_points.append((int(60 + math.cos(angle) * r), int(58 + math.sin(angle) * r)))
    pygame.draw.polygon(s, gold_main, body_points)
    pygame.draw.polygon(s, gold_dark, body_points, 2)
    
    # 金色浮雕纹理
    relief_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    # 中央花纹
    for i in range(6):
        angle = i * 60 * 0.01745
        # 主纹路
        pygame.draw.line(relief_surf, (*gold_dark, 180), (60, 58),
                        (int(60 + math.cos(angle) * 28), int(58 + math.sin(angle) * 28)), 2)
        # 装饰节点
        node_x = 60 + math.cos(angle) * 20
        node_y = 58 + math.sin(angle) * 20
        pygame.draw.circle(relief_surf, gold_bright, (int(node_x), int(node_y)), 4)
        pygame.draw.circle(relief_surf, gold_dark, (int(node_x), int(node_y)), 4, 1)
    s.blit(relief_surf, (0, 0))
    
    # 高光带
    highlight_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.ellipse(highlight_surf, (*gold_light, 100), (42, 42, 36, 16))
    pygame.draw.ellipse(highlight_surf, (*holy_white, 60), (48, 46, 24, 8))
    s.blit(highlight_surf, (0, 0))
    
    # 神圣核心
    core_pulse = abs(math.sin(t * 2.5))
    # 核心光晕
    core_glow = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.circle(core_glow, (*holy_glow, 120), (30, 30), int(18 + core_pulse * 6))
    pygame.draw.circle(core_glow, (*gold_light, 100), (30, 30), int(14 + core_pulse * 4))
    s.blit(core_glow, (30, 28))
    # 核心
    pygame.draw.circle(s, gold_light, (60, 58), int(12 + core_pulse * 3))
    pygame.draw.circle(s, holy_white, (60, 58), 6)
    
    # 十字圣光
    cross_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    cross_len = 20 + int(core_pulse * 8)
    for i in range(4):
        angle = (i * 90) * 0.01745
        pygame.draw.line(cross_surf, (*holy_white, 220), (60, 58),
                        (int(60 + math.cos(angle) * cross_len), int(58 + math.sin(angle) * cross_len)), 3)
        # 光芒渐变
        for j in range(3):
            fade_len = cross_len - j * 5
            pygame.draw.line(cross_surf, (*gold_light, 150 - j * 40), (60, 58),
                           (int(60 + math.cos(angle) * fade_len), int(58 + math.sin(angle) * fade_len)), 5 - j)
    s.blit(cross_surf, (0, 0))
    
    # 皇冠头部
    crown_base = [(42, 45), (78, 45), (80, 38), (60, 28), (40, 38)]
    pygame.draw.polygon(s, gold_main, crown_base)
    pygame.draw.polygon(s, gold_dark, crown_base, 2)
    # 皇冠尖刺
    spikes = [(48, 38, 45, 22), (60, 35, 60, 15), (72, 38, 75, 22)]
    for sx, sy, tx, ty in spikes:
        pygame.draw.polygon(s, gold_bright, [(sx - 4, sy), (tx, ty), (sx + 4, sy)])
        pygame.draw.polygon(s, gold_dark, [(sx - 4, sy), (tx, ty), (sx + 4, sy)], 1)
    # 皇冠宝石
    pygame.draw.circle(s, ruby_red, (60, 22), 5)
    pygame.draw.circle(s, (255, 150, 150), (58, 20), 2)
    pygame.draw.circle(s, sapphire, (48, 28), 3)
    pygame.draw.circle(s, emerald, (72, 28), 3)
    # 皇冠高光
    pygame.draw.line(s, gold_light, (45, 40), (55, 32), 2)
    pygame.draw.line(s, gold_light, (65, 32), (75, 40), 2)
    
    # 黄金之眼
    pygame.draw.ellipse(s, gold_dark, (50, 36, 20, 10))
    pygame.draw.ellipse(s, holy_white, (54, 38, 12, 6))
    pygame.draw.ellipse(s, gold_bright, (58, 40, 4, 2))
    
    # 黄金战拳
    for fx, mirror in [(12, 1), (108, -1)]:
        # 圣光环绕
        fist_halo = pygame.Surface((50, 50), pygame.SRCALPHA)
        for i in range(3):
            h_angle = (i * 120 + t * 80) * 0.01745
            hx = 25 + math.cos(h_angle) * 18
            hy = 25 + math.sin(h_angle) * 18
            pygame.draw.circle(fist_halo, (*gold_light, 100), (int(hx), int(hy)), 5)
        s.blit(fist_halo, (fx - 25, 33))
        
        # 黄金拳
        pygame.draw.circle(s, gold_main, (fx, 58), 16)
        pygame.draw.circle(s, gold_dark, (fx, 58), 16, 2)
        # 高光
        pygame.draw.arc(s, gold_light, (fx - 14, 46, 28, 24), 0.5, 1.8, 3)
        # 拳心宝石
        pygame.draw.circle(s, ruby_red, (fx, 58), 6)
        pygame.draw.circle(s, (255, 180, 180), (fx - 2, 56), 2)
        # 十字纹
        pygame.draw.line(s, gold_dark, (fx - 8, 58), (fx + 8, 58), 1)
        pygame.draw.line(s, gold_dark, (fx, 50), (fx, 66), 1)
    
    # 飘散的金色光粒
    for i in range(10):
        particle_phase = (t * 0.6 + i * 0.3) % 1.5
        particle_angle = (i * 36 + t * 25) * 0.01745
        particle_dist = 30 + particle_phase * 30
        px = 60 + math.cos(particle_angle) * particle_dist
        py = 58 + math.sin(particle_angle) * particle_dist - particle_phase * 10
        particle_alpha = int(220 * (1 - particle_phase / 1.5))
        particle_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, (*gold_light, particle_alpha), (4, 4), 3)
        pygame.draw.circle(particle_surf, (*holy_white, particle_alpha // 2), (4, 4), 1)
        s.blit(particle_surf, (int(px - 4), int(py - 4)))
    
    _draw_charge_bar(s, 60, 64, 4, t, gold_light)
