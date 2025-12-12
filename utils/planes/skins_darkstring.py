# -*- coding: utf-8 -*-
"""
幽影穿心·冥弦 (Darkstring) - 专属涂装渲染模块
暗夜中无声的死神，以弦音标记猎物的归宿

涂装列表 (12种完全不同形态) - 与customization.py同步:
1. darkstring_default - 冥弦原型
2. darkstring_reaper - 死亡竖琴
3. darkstring_void_hunter - 蛛后丝网
4. darkstring_shadow_assassin - 傀儡师
5. darkstring_phantom_thread - 暗影神射
6. darkstring_eclipse_dark - 命运织者
7. darkstring_death_dealer - 虚空刺客
8. darkstring_nightmare - 血色小提琴
9. darkstring_obsidian_arrow - 灵魂陷阱
10. darkstring_fate_weaver - 量子纠缠
11. darkstring_silent_death - 梦魇织机
12. darkstring_blood_moon - 死神琴弦
"""
import pygame
import math
import random

DARKSTRING_STYLES = [
    "darkstring_default",
    "darkstring_reaper",
    "darkstring_void_hunter",
    "darkstring_shadow_assassin",
    "darkstring_phantom_thread",
    "darkstring_eclipse_dark",
    "darkstring_death_dealer",
    "darkstring_nightmare",
    "darkstring_obsidian_arrow",
    "darkstring_fate_weaver",
    "darkstring_silent_death",
    "darkstring_blood_moon"
]


def is_darkstring_style(model_style):
    return model_style in DARKSTRING_STYLES


def render_darkstring_skin(surface, c, model_style, t, pid, static):
    if model_style not in DARKSTRING_STYLES:
        return None
    skin_id = model_style.replace("darkstring_", "")
    frame = 0 if static else int(t * 60) % 360
    draw_darkstring(surface, c, 60, 60, scale=1.8, skin_id=skin_id, frame=frame)
    return surface


def _render_darkstring_base(surface, t, pulse):
    frame = int(t * 60) % 360
    draw_darkstring(surface, (40, 30, 50), 60, 60, scale=1.8, skin_id="default", frame=frame)
    return surface


def draw_darkstring(surface, color, x, y, scale=1.0, skin_id="default", frame=0):
    cx, cy = x, y
    s = scale
    pulse = math.sin(frame * 0.1) * 3
    
    if skin_id == "default":
        _draw_default(surface, cx, cy, s, frame, pulse)
    elif skin_id == "reaper":
        _draw_death_harp(surface, cx, cy, s, frame, pulse)
    elif skin_id == "void_hunter":
        _draw_spider_queen(surface, cx, cy, s, frame, pulse)
    elif skin_id == "shadow_assassin":
        _draw_puppet_master(surface, cx, cy, s, frame, pulse)
    elif skin_id == "phantom_thread":
        _draw_shadow_archer(surface, cx, cy, s, frame, pulse)
    elif skin_id == "eclipse_dark":
        _draw_fate_weaver(surface, cx, cy, s, frame, pulse)
    elif skin_id == "death_dealer":
        _draw_void_assassin(surface, cx, cy, s, frame, pulse)
    elif skin_id == "nightmare":
        _draw_blood_violin(surface, cx, cy, s, frame, pulse)
    elif skin_id == "obsidian_arrow":
        _draw_soul_snare(surface, cx, cy, s, frame, pulse)
    elif skin_id == "fate_weaver":
        _draw_quantum_thread(surface, cx, cy, s, frame, pulse)
    elif skin_id == "silent_death":
        _draw_nightmare_loom(surface, cx, cy, s, frame, pulse)
    elif skin_id == "blood_moon":
        _draw_reaper_strings(surface, cx, cy, s, frame, pulse)
    else:
        _draw_default(surface, cx, cy, s, frame, pulse)


def _draw_default(surface, cx, cy, s, frame, pulse):
    """冥弦形态 - 暗影机体+弦丝延伸+红光标记"""
    shadow_black = (25, 20, 30)
    string_gray = (80, 75, 90)
    beacon_red = (255, 50, 50)
    
    # 暗影主体
    body_points = [
        (cx, cy - 28 * s),
        (cx - 15 * s, cy - 10 * s),
        (cx - 12 * s, cy + 15 * s),
        (cx, cy + 22 * s),
        (cx + 12 * s, cy + 15 * s),
        (cx + 15 * s, cy - 10 * s),
    ]
    pygame.draw.polygon(surface, shadow_black, body_points)
    pygame.draw.polygon(surface, (50, 45, 60), body_points, 2)
    
    # 锐角侧翼
    for side in [-1, 1]:
        wing = [
            (cx + side * 12 * s, cy - 5 * s),
            (cx + side * 38 * s, cy - 15 * s),
            (cx + side * 35 * s, cy + 5 * s),
            (cx + side * 15 * s, cy + 10 * s),
        ]
        pygame.draw.polygon(surface, shadow_black, wing)
        pygame.draw.polygon(surface, string_gray, wing, 1)
    
    # 冥弦丝线 - 从机体延伸
    string_targets = [
        (cx - 40 * s, cy - 25 * s),
        (cx + 40 * s, cy - 25 * s),
        (cx - 35 * s, cy + 30 * s),
        (cx + 35 * s, cy + 30 * s),
    ]
    for i, (tx, ty) in enumerate(string_targets):
        # 弦丝波动
        wave = math.sin(frame * 0.1 + i) * 5 * s
        mid_x = (cx + tx) / 2 + wave
        mid_y = (cy + ty) / 2
        
        # 绘制曲线弦丝
        points = [(cx, cy), (mid_x, mid_y), (tx, ty)]
        pygame.draw.lines(surface, string_gray, False, points, 1)
        # 弦丝末端标记点
        pygame.draw.circle(surface, beacon_red, (int(tx), int(ty)), int(3 * s))
        # 标记脉冲
        mark_pulse = (frame + i * 20) % 40
        if mark_pulse < 20:
            pulse_r = mark_pulse * 0.3 * s
            surf = pygame.Surface((int(pulse_r * 2 + 10), int(pulse_r * 2 + 10)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*beacon_red, 150 - mark_pulse * 7), (int(pulse_r + 5), int(pulse_r + 5)), int(pulse_r), 2)
            surface.blit(surf, (tx - pulse_r - 5, ty - pulse_r - 5))
    
    # 核心信标
    pygame.draw.circle(surface, beacon_red, (int(cx), int(cy)), int(6 * s + pulse / 2))
    pygame.draw.circle(surface, (255, 150, 150), (int(cx), int(cy)), int(3 * s))
    
    # 瞄准线
    aim_len = 35 * s + math.sin(frame * 0.15) * 5 * s
    pygame.draw.line(surface, (*beacon_red, 180), (cx, cy - 28 * s), (cx, cy - 28 * s - aim_len), 2)


def _draw_death_harp(surface, cx, cy, s, frame, pulse):
    """死亡竖琴 - 冥府乐师的夺命琴音形态"""
    harp_gold = (180, 150, 80)
    harp_dark = (40, 35, 50)
    soul_blue = (100, 150, 255)
    
    # 竖琴框架
    frame_points = [
        (cx - 5 * s, cy - 35 * s),
        (cx - 25 * s, cy - 25 * s),
        (cx - 30 * s, cy + 20 * s),
        (cx - 10 * s, cy + 30 * s),
        (cx + 5 * s, cy + 30 * s),
    ]
    pygame.draw.polygon(surface, harp_dark, frame_points)
    pygame.draw.polygon(surface, harp_gold, frame_points, 3)
    
    # 竖琴曲线颈部
    neck_points = []
    for i in range(10):
        t = i / 9
        nx = cx - 5 * s + math.sin(t * math.pi * 0.5) * (-20 * s)
        ny = cy - 35 * s + t * 65 * s
        neck_points.append((nx, ny))
    pygame.draw.lines(surface, harp_gold, False, neck_points, 3)
    
    # 琴弦
    for i in range(8):
        string_x = cx - 8 * s - i * 2.5 * s
        string_top_y = cy - 30 * s + i * 3 * s
        string_bottom_y = cy + 25 * s
        
        # 弦振动
        vibration = math.sin(frame * 0.2 + i * 0.5) * 3 * s
        mid_y = (string_top_y + string_bottom_y) / 2
        
        pygame.draw.line(surface, harp_gold, (string_x, string_top_y), (string_x + vibration, mid_y), 1)
        pygame.draw.line(surface, harp_gold, (string_x + vibration, mid_y), (string_x, string_bottom_y), 1)
        
        # 音符灵魂
        if (frame + i * 15) % 60 < 30:
            note_y = string_top_y + ((frame + i * 15) % 60) * s
            pygame.draw.circle(surface, soul_blue, (int(string_x), int(note_y)), 2)
    
    # 演奏的幽灵手指
    hand_x = cx - 15 * s + math.sin(frame * 0.08) * 10 * s
    hand_y = cy + math.cos(frame * 0.1) * 5 * s
    for finger in range(4):
        fx = hand_x + finger * 3 * s
        fy = hand_y + math.sin(frame * 0.15 + finger) * 3 * s
        pygame.draw.ellipse(surface, (60, 55, 70), (fx - 2 * s, fy - 5 * s, 4 * s, 10 * s))
    
    # 飘散的音符魂魄
    for i in range(5):
        soul_angle = frame * 1.5 + i * 72
        soul_r = 35 * s + math.sin(frame * 0.05 + i) * 5 * s
        soul_x = cx + math.cos(math.radians(soul_angle)) * soul_r
        soul_y = cy + math.sin(math.radians(soul_angle)) * soul_r
        alpha = int(150 + math.sin(frame * 0.1 + i) * 50)
        surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*soul_blue, alpha), (6, 6), 4)
        surface.blit(surf, (soul_x - 6, soul_y - 6))


def _draw_spider_queen(surface, cx, cy, s, frame, pulse):
    """蛛后丝网 - 织命的暗夜蛛后形态"""
    spider_black = (20, 15, 25)
    web_silver = (150, 150, 160)
    venom_green = (100, 255, 100)
    
    # 蛛网背景
    web_rings = 5
    web_spokes = 12
    for ring in range(web_rings):
        ring_r = 10 * s + ring * 8 * s
        ring_points = []
        for spoke in range(web_spokes):
            angle = spoke * 30 + math.sin(frame * 0.03 + ring) * 5
            rx = cx + math.cos(math.radians(angle)) * ring_r
            ry = cy + math.sin(math.radians(angle)) * ring_r
            ring_points.append((int(rx), int(ry)))
        if len(ring_points) > 2:
            pygame.draw.lines(surface, web_silver, True, ring_points, 1)
    
    # 辐射丝线
    for spoke in range(web_spokes):
        angle = spoke * 30
        end_r = 40 * s
        ex = cx + math.cos(math.radians(angle)) * end_r
        ey = cy + math.sin(math.radians(angle)) * end_r
        pygame.draw.line(surface, web_silver, (cx, cy), (int(ex), int(ey)), 1)
    
    # 蛛后身体
    # 腹部
    pygame.draw.ellipse(surface, spider_black, (cx - 12 * s, cy - 5 * s, 24 * s, 30 * s))
    # 头胸部
    pygame.draw.ellipse(surface, spider_black, (cx - 8 * s, cy - 20 * s, 16 * s, 18 * s))
    # 毒腺标记
    pygame.draw.ellipse(surface, (200, 50, 50), (cx - 6 * s, cy + 5 * s, 12 * s, 15 * s))
    
    # 八只蛛腿
    leg_angles = [-150, -120, -60, -30, 30, 60, 120, 150]
    for i, angle in enumerate(leg_angles):
        leg_wave = math.sin(frame * 0.1 + i * 0.5) * 5
        # 三段腿
        joint1_x = cx + math.cos(math.radians(angle)) * 15 * s
        joint1_y = cy - 10 * s + math.sin(math.radians(angle)) * 10 * s
        joint2_x = joint1_x + math.cos(math.radians(angle - 30 + leg_wave)) * 12 * s
        joint2_y = joint1_y + math.sin(math.radians(angle - 30 + leg_wave)) * 12 * s
        tip_x = joint2_x + math.cos(math.radians(angle + 20)) * 10 * s
        tip_y = joint2_y + math.sin(math.radians(angle + 20)) * 10 * s
        
        pygame.draw.line(surface, spider_black, (cx, cy - 10 * s), (joint1_x, joint1_y), 3)
        pygame.draw.line(surface, spider_black, (joint1_x, joint1_y), (joint2_x, joint2_y), 2)
        pygame.draw.line(surface, spider_black, (joint2_x, joint2_y), (tip_x, tip_y), 2)
    
    # 毒液眼睛
    for i in range(4):
        eye_x = cx - 4 * s + (i % 2) * 4 * s + (i // 2) * 2 * s
        eye_y = cy - 16 * s + (i // 2) * 3 * s
        pygame.draw.circle(surface, venom_green, (int(eye_x), int(eye_y)), int(2 * s))
    
    # 猎物标记（丝线末端）
    for i in range(3):
        prey_angle = frame * 0.5 + i * 120
        prey_r = 42 * s
        prey_x = cx + math.cos(math.radians(prey_angle)) * prey_r
        prey_y = cy + math.sin(math.radians(prey_angle)) * prey_r
        pygame.draw.circle(surface, (255, 50, 50), (int(prey_x), int(prey_y)), int(3 * s))


def _draw_puppet_master(surface, cx, cy, s, frame, pulse):
    """傀儡师 - 操控命运之线的形态"""
    master_dark = (30, 25, 40)
    string_red = (200, 50, 50)
    puppet_wood = (150, 100, 60)
    
    # 傀儡师剪影
    cloak = [
        (cx, cy - 30 * s),
        (cx - 20 * s, cy - 15 * s),
        (cx - 25 * s, cy + 25 * s),
        (cx + 25 * s, cy + 25 * s),
        (cx + 20 * s, cy - 15 * s),
    ]
    pygame.draw.polygon(surface, master_dark, cloak)
    # 兜帽
    pygame.draw.arc(surface, (50, 45, 60), (cx - 15 * s, cy - 40 * s, 30 * s, 25 * s), 0, math.pi, 3)
    # 面具
    pygame.draw.ellipse(surface, (200, 200, 210), (cx - 8 * s, cy - 28 * s, 16 * s, 20 * s))
    # 面具眼洞
    pygame.draw.ellipse(surface, master_dark, (cx - 5 * s, cy - 24 * s, 4 * s, 6 * s))
    pygame.draw.ellipse(surface, master_dark, (cx + 1 * s, cy - 24 * s, 4 * s, 6 * s))
    
    # 操控之手
    for side in [-1, 1]:
        hand_x = cx + side * 30 * s
        hand_y = cy - 10 * s + math.sin(frame * 0.1 + side) * 5 * s
        # 手掌
        pygame.draw.ellipse(surface, (60, 55, 70), (hand_x - 5 * s, hand_y - 4 * s, 10 * s, 8 * s))
        # 手指
        for finger in range(5):
            finger_angle = -40 + finger * 20 + side * 90
            finger_len = 8 * s
            fx = hand_x + math.cos(math.radians(finger_angle)) * finger_len
            fy = hand_y + math.sin(math.radians(finger_angle)) * finger_len
            pygame.draw.line(surface, (70, 65, 80), (hand_x, hand_y), (int(fx), int(fy)), 2)
    
    # 傀儡（三个小型）
    puppet_positions = [(cx - 25 * s, cy + 35 * s), (cx, cy + 40 * s), (cx + 25 * s, cy + 35 * s)]
    for i, (px, py) in enumerate(puppet_positions):
        dance_offset = math.sin(frame * 0.15 + i) * 3 * s
        # 傀儡身体
        pygame.draw.ellipse(surface, puppet_wood, (px - 4 * s, py - 8 * s + dance_offset, 8 * s, 12 * s))
        pygame.draw.circle(surface, puppet_wood, (int(px), int(py - 12 * s + dance_offset)), int(4 * s))
        # 控制线
        pygame.draw.line(surface, string_red, (cx + (i - 1) * 10 * s, cy - 5 * s), (px, py - 12 * s + dance_offset), 1)
        pygame.draw.line(surface, string_red, (cx + (i - 1) * 10 * s, cy - 5 * s), (px - 3 * s, py + dance_offset), 1)
        pygame.draw.line(surface, string_red, (cx + (i - 1) * 10 * s, cy - 5 * s), (px + 3 * s, py + dance_offset), 1)
    
    # 命运丝线光效
    for i in range(6):
        thread_alpha = int(100 + math.sin(frame * 0.1 + i) * 50)
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(surf, (*string_red, thread_alpha), 
                        (cx + (i - 2.5) * 8 * s, cy - 5 * s), 
                        (cx + (i - 2.5) * 15 * s, cy + 45 * s), 1)
        surface.blit(surf, (0, 0))


def _draw_shadow_archer(surface, cx, cy, s, frame, pulse):
    """暗影神射 - 暗箭穿心的死神弓手形态"""
    shadow = (25, 20, 35)
    bow_dark = (50, 40, 60)
    arrow_red = (255, 50, 50)
    
    # 弓身（大型战弓）
    bow_curve = []
    for i in range(20):
        t = i / 19
        bow_x = cx - 25 * s + math.sin(t * math.pi) * 15 * s
        bow_y = cy - 30 * s + t * 60 * s
        bow_curve.append((bow_x, bow_y))
    pygame.draw.lines(surface, bow_dark, False, bow_curve, 4)
    
    # 弓弦
    string_pull = math.sin(frame * 0.1) * 8 * s  # 拉弓动画
    pygame.draw.line(surface, (100, 95, 110), 
                    (bow_curve[0][0], bow_curve[0][1]),
                    (cx - 10 * s + string_pull, cy), 2)
    pygame.draw.line(surface, (100, 95, 110),
                    (bow_curve[-1][0], bow_curve[-1][1]),
                    (cx - 10 * s + string_pull, cy), 2)
    
    # 暗影箭矢
    arrow_x = cx - 10 * s + string_pull
    arrow_tip = cx + 40 * s
    # 箭身
    pygame.draw.line(surface, (60, 55, 70), (arrow_x, cy), (arrow_tip - 10 * s, cy), 2)
    # 箭头
    arrow_head = [
        (arrow_tip, cy),
        (arrow_tip - 8 * s, cy - 4 * s),
        (arrow_tip - 8 * s, cy + 4 * s),
    ]
    pygame.draw.polygon(surface, arrow_red, arrow_head)
    # 箭羽
    pygame.draw.polygon(surface, shadow, [
        (arrow_x + 5 * s, cy), (arrow_x, cy - 5 * s), (arrow_x + 8 * s, cy)])
    pygame.draw.polygon(surface, shadow, [
        (arrow_x + 5 * s, cy), (arrow_x, cy + 5 * s), (arrow_x + 8 * s, cy)])
    
    # 弓手剪影
    archer = [
        (cx + 5 * s, cy - 20 * s),
        (cx - 5 * s, cy - 15 * s),
        (cx - 8 * s, cy + 15 * s),
        (cx + 2 * s, cy + 20 * s),
        (cx + 10 * s, cy + 15 * s),
        (cx + 12 * s, cy - 10 * s),
    ]
    pygame.draw.polygon(surface, shadow, archer)
    # 兜帽
    pygame.draw.arc(surface, shadow, (cx - 2 * s, cy - 30 * s, 20 * s, 20 * s), math.pi * 0.2, math.pi * 0.8, 5)
    
    # 瞄准标记
    target_x = cx + 50 * s
    target_y = cy + math.sin(frame * 0.05) * 10 * s
    # 十字准星
    pygame.draw.circle(surface, arrow_red, (int(target_x), int(target_y)), int(8 * s), 2)
    pygame.draw.line(surface, arrow_red, (target_x - 12 * s, target_y), (target_x + 12 * s, target_y), 1)
    pygame.draw.line(surface, arrow_red, (target_x, target_y - 12 * s), (target_x, target_y + 12 * s), 1)


def _draw_fate_weaver(surface, cx, cy, s, frame, pulse):
    """命运织者 - 编织生死的摩伊拉形态"""
    fate_purple = (120, 80, 160)
    thread_gold = (255, 200, 100)
    thread_silver = (200, 200, 210)
    scissors_gray = (150, 150, 160)
    
    # 三位一体的命运女神剪影
    for i in range(3):
        goddess_x = cx - 20 * s + i * 20 * s
        goddess_y = cy + math.sin(frame * 0.05 + i * 2) * 3 * s
        # 长袍
        robe = [
            (goddess_x, goddess_y - 15 * s),
            (goddess_x - 8 * s, goddess_y - 5 * s),
            (goddess_x - 10 * s, goddess_y + 20 * s),
            (goddess_x + 10 * s, goddess_y + 20 * s),
            (goddess_x + 8 * s, goddess_y - 5 * s),
        ]
        colors = [fate_purple, (100, 70, 140), (80, 50, 120)]
        pygame.draw.polygon(surface, colors[i], robe)
        # 头部
        pygame.draw.circle(surface, (180, 170, 190), (int(goddess_x), int(goddess_y - 18 * s)), int(5 * s))
    
    # 命运之线（金色=生命，银色=命运）
    for i in range(8):
        thread_y = cy - 25 * s + i * 6 * s
        wave = math.sin(frame * 0.08 + i * 0.5) * 10 * s
        color = thread_gold if i % 2 == 0 else thread_silver
        pygame.draw.line(surface, color, (cx - 35 * s, thread_y), (cx + 35 * s + wave, thread_y + wave * 0.3), 1)
    
    # 纺锤（左侧女神）
    spindle_x = cx - 25 * s
    spindle_y = cy
    pygame.draw.ellipse(surface, (180, 150, 100), (spindle_x - 3 * s, spindle_y - 10 * s, 6 * s, 20 * s))
    # 旋转的线团
    for j in range(5):
        thread_angle = frame * 3 + j * 72
        tx = spindle_x + math.cos(math.radians(thread_angle)) * 5 * s
        ty = spindle_y + math.sin(math.radians(thread_angle)) * 3 * s
        pygame.draw.circle(surface, thread_gold, (int(tx), int(ty)), 1)
    
    # 剪刀（右侧女神）
    scissors_x = cx + 25 * s
    scissors_y = cy
    scissors_open = abs(math.sin(frame * 0.1)) * 15
    pygame.draw.line(surface, scissors_gray, (scissors_x, scissors_y - 8 * s), 
                    (scissors_x + scissors_open, scissors_y + 8 * s), 3)
    pygame.draw.line(surface, scissors_gray, (scissors_x, scissors_y - 8 * s),
                    (scissors_x - scissors_open, scissors_y + 8 * s), 3)
    # 剪刀柄
    pygame.draw.circle(surface, (100, 95, 110), (int(scissors_x + scissors_open), int(scissors_y + 10 * s)), int(3 * s))
    pygame.draw.circle(surface, (100, 95, 110), (int(scissors_x - scissors_open), int(scissors_y + 10 * s)), int(3 * s))
    
    # 命运之轮光环
    wheel_angle = frame * 0.5
    for spoke in range(8):
        spoke_angle = wheel_angle + spoke * 45
        spoke_r = 38 * s
        sx = cx + math.cos(math.radians(spoke_angle)) * spoke_r
        sy = cy + math.sin(math.radians(spoke_angle)) * spoke_r
        pygame.draw.line(surface, fate_purple, (cx, cy), (int(sx), int(sy)), 1)
    pygame.draw.circle(surface, fate_purple, (int(cx), int(cy)), int(38 * s), 2)


def _draw_void_assassin(surface, cx, cy, s, frame, pulse):
    """虚空刺客 - 来自虚空的无声杀手形态"""
    void_black = (10, 5, 20)
    void_purple = (100, 50, 150)
    blade_silver = (180, 185, 200)
    
    # 虚空裂隙背景
    for rift in range(5):
        rift_angle = frame * 0.3 + rift * 72
        rift_r = 30 * s + math.sin(frame * 0.1 + rift) * 10 * s
        rift_x = cx + math.cos(math.radians(rift_angle)) * rift_r
        rift_y = cy + math.sin(math.radians(rift_angle)) * rift_r
        # 裂隙形状
        rift_points = []
        for j in range(6):
            rp_angle = j * 60 + frame
            rp_r = 5 * s + random.uniform(-2, 2) * s
            rift_points.append((
                rift_x + math.cos(math.radians(rp_angle)) * rp_r,
                rift_y + math.sin(math.radians(rp_angle)) * rp_r
            ))
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (*void_purple, 100), rift_points)
        surface.blit(surf, (0, 0))
    
    # 刺客身影（半透明）
    assassin_alpha = int(150 + math.sin(frame * 0.1) * 50)
    assassin_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    body = [
        (cx, cy - 25 * s),
        (cx - 12 * s, cy - 10 * s),
        (cx - 15 * s, cy + 20 * s),
        (cx + 15 * s, cy + 20 * s),
        (cx + 12 * s, cy - 10 * s),
    ]
    pygame.draw.polygon(assassin_surf, (*void_black, assassin_alpha), body)
    surface.blit(assassin_surf, (0, 0))
    
    # 虚空之刃
    blade_offset = math.sin(frame * 0.15) * 5 * s
    for side in [-1, 1]:
        blade_base_x = cx + side * 15 * s
        blade_base_y = cy
        blade_tip_x = blade_base_x + side * 25 * s + blade_offset * side
        blade_tip_y = cy - 15 * s
        
        blade = [
            (blade_base_x, blade_base_y - 3 * s),
            (blade_tip_x, blade_tip_y),
            (blade_base_x, blade_base_y + 3 * s),
        ]
        pygame.draw.polygon(surface, blade_silver, blade)
        pygame.draw.polygon(surface, void_purple, blade, 1)
    
    # 眼睛（唯一可见部分）
    for side in [-1, 1]:
        eye_x = cx + side * 4 * s
        eye_y = cy - 18 * s
        pygame.draw.ellipse(surface, void_purple, (eye_x - 3 * s, eye_y - 2 * s, 6 * s, 4 * s))
        pygame.draw.circle(surface, (255, 100, 255), (int(eye_x), int(eye_y)), int(1.5 * s))
    
    # 相位转移效果
    phase_alpha = (frame % 60)
    if phase_alpha < 30:
        phase_x = cx + phase_alpha * 0.5 * s
        phase_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        phase_body = [(p[0] + phase_alpha * 0.5 * s, p[1]) for p in body]
        pygame.draw.polygon(phase_surf, (*void_purple, 50 - phase_alpha), phase_body)
        surface.blit(phase_surf, (0, 0))


def _draw_blood_violin(surface, cx, cy, s, frame, pulse):
    """血色小提琴 - 以血为弦的恶魔乐器形态"""
    violin_red = (120, 30, 40)
    blood_red = (200, 20, 20)
    bone_white = (230, 220, 210)
    
    # 小提琴琴身
    # 上半部
    pygame.draw.ellipse(surface, violin_red, (cx - 12 * s, cy - 25 * s, 24 * s, 20 * s))
    # 下半部
    pygame.draw.ellipse(surface, violin_red, (cx - 15 * s, cy - 5 * s, 30 * s, 30 * s))
    # 中间腰部
    pygame.draw.ellipse(surface, (20, 15, 25), (cx - 8 * s, cy - 12 * s, 6 * s, 15 * s))
    pygame.draw.ellipse(surface, (20, 15, 25), (cx + 2 * s, cy - 12 * s, 6 * s, 15 * s))
    
    # 琴颈（骨质）
    pygame.draw.rect(surface, bone_white, (cx - 3 * s, cy - 40 * s, 6 * s, 18 * s))
    # 琴头（骷髅形）
    pygame.draw.circle(surface, bone_white, (int(cx), int(cy - 45 * s)), int(6 * s))
    pygame.draw.ellipse(surface, (20, 15, 25), (cx - 3 * s, cy - 48 * s, 2 * s, 3 * s))
    pygame.draw.ellipse(surface, (20, 15, 25), (cx + 1 * s, cy - 48 * s, 2 * s, 3 * s))
    
    # 血弦
    for i in range(4):
        string_x = cx - 3 * s + i * 2 * s
        vibrate = math.sin(frame * 0.3 + i) * 2 * s
        # 弦的曲线
        for j in range(10):
            y_pos = cy - 40 * s + j * 5 * s
            wave = math.sin(frame * 0.2 + j * 0.5 + i) * vibrate * (1 - abs(j - 5) / 5)
            if j < 9:
                pygame.draw.line(surface, blood_red, 
                               (string_x + wave, y_pos),
                               (string_x + math.sin(frame * 0.2 + (j+1) * 0.5 + i) * vibrate * (1 - abs(j+1 - 5) / 5), y_pos + 5 * s), 1)
    
    # 琴桥
    pygame.draw.rect(surface, bone_white, (cx - 5 * s, cy - 8 * s, 10 * s, 3 * s))
    
    # f孔（血滴形）
    for side in [-1, 1]:
        f_x = cx + side * 6 * s
        pygame.draw.ellipse(surface, (40, 20, 25), (f_x - 2 * s, cy - 2 * s, 4 * s, 10 * s))
    
    # 血滴效果
    for i in range(5):
        drop_y = cy + 25 * s + (frame * 1.5 + i * 20) % 30 * s
        drop_x = cx - 10 * s + i * 5 * s + math.sin(frame * 0.1 + i) * 2 * s
        drop_alpha = max(0, 200 - int((drop_y - cy - 25 * s) * 7))
        if drop_alpha > 0:
            surf = pygame.Surface((8, 12), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (*blood_red, drop_alpha), (1, 0, 6, 10))
            surface.blit(surf, (drop_x - 4, drop_y - 5))
    
    # 恶魔琴弓
    bow_wave = math.sin(frame * 0.12) * 10 * s
    bow_y = cy + bow_wave
    pygame.draw.line(surface, bone_white, (cx + 20 * s, bow_y - 20 * s), (cx + 20 * s, bow_y + 20 * s), 2)
    # 弓毛
    pygame.draw.line(surface, blood_red, (cx + 18 * s, bow_y - 18 * s), (cx + 18 * s, bow_y + 18 * s), 1)


def _draw_soul_snare(surface, cx, cy, s, frame, pulse):
    """灵魂陷阱 - 捕猎灵魂的恶灵猎手形态"""
    trap_dark = (30, 25, 40)
    soul_cyan = (100, 255, 255)
    chain_gray = (120, 115, 130)
    
    # 捕魂笼
    cage_r = 25 * s
    # 笼条
    for i in range(12):
        bar_angle = i * 30 + frame * 0.3
        bx = cx + math.cos(math.radians(bar_angle)) * cage_r
        by = cy + math.sin(math.radians(bar_angle)) * cage_r * 0.3
        pygame.draw.line(surface, chain_gray, (bx, cy - 20 * s), (bx, cy + 20 * s), 2)
    # 笼顶和笼底
    pygame.draw.ellipse(surface, chain_gray, (cx - cage_r, cy - 22 * s, cage_r * 2, 8 * s), 2)
    pygame.draw.ellipse(surface, chain_gray, (cx - cage_r, cy + 18 * s, cage_r * 2, 8 * s), 2)
    
    # 被困的灵魂
    random.seed(42)
    for i in range(5):
        soul_x = cx + random.uniform(-15, 15) * s
        soul_y = cy + random.uniform(-10, 10) * s
        soul_drift = math.sin(frame * 0.1 + i) * 3 * s
        
        # 灵魂形态
        soul_surf = pygame.Surface((20, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(soul_surf, (*soul_cyan, 150), (3, 5, 14, 20))
        # 灵魂眼睛
        pygame.draw.circle(soul_surf, (255, 255, 255), (7, 12), 2)
        pygame.draw.circle(soul_surf, (255, 255, 255), (13, 12), 2)
        surface.blit(soul_surf, (soul_x - 10 + soul_drift, soul_y - 15))
    
    # 锁链
    for corner in range(4):
        chain_angle = corner * 90 + 45
        chain_start_x = cx + math.cos(math.radians(chain_angle)) * 30 * s
        chain_start_y = cy + math.sin(math.radians(chain_angle)) * 15 * s
        chain_end_x = cx + math.cos(math.radians(chain_angle)) * 45 * s
        chain_end_y = cy + math.sin(math.radians(chain_angle)) * 30 * s
        
        # 链环
        chain_links = 5
        for link in range(chain_links):
            t = link / (chain_links - 1)
            lx = chain_start_x + (chain_end_x - chain_start_x) * t
            ly = chain_start_y + (chain_end_y - chain_start_y) * t
            pygame.draw.circle(surface, chain_gray, (int(lx), int(ly)), int(2 * s), 1)
    
    # 猎手眼睛（笼外）
    hunter_y = cy - 35 * s
    for side in [-1, 1]:
        eye_x = cx + side * 8 * s
        pygame.draw.ellipse(surface, (255, 50, 50), (eye_x - 4 * s, hunter_y - 2 * s, 8 * s, 5 * s))
        pygame.draw.circle(surface, (255, 200, 200), (int(eye_x), int(hunter_y)), int(1.5 * s))


def _draw_quantum_thread(surface, cx, cy, s, frame, pulse):
    """量子纠缠 - 跨越时空的命运羁绊形态"""
    quantum_blue = (80, 150, 255)
    quantum_pink = (255, 100, 200)
    entangle_white = (240, 240, 255)
    
    # 双粒子
    particle_dist = 25 * s
    p1_x = cx - particle_dist * math.cos(frame * 0.02)
    p1_y = cy + particle_dist * 0.3 * math.sin(frame * 0.02)
    p2_x = cx + particle_dist * math.cos(frame * 0.02)
    p2_y = cy - particle_dist * 0.3 * math.sin(frame * 0.02)
    
    # 粒子1
    for layer in range(3):
        r = (10 - layer * 2) * s
        alpha = 200 - layer * 50
        surf = pygame.Surface((int(r * 2 + 4), int(r * 2 + 4)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*quantum_blue, alpha), (int(r + 2), int(r + 2)), int(r))
        surface.blit(surf, (p1_x - r - 2, p1_y - r - 2))
    
    # 粒子2
    for layer in range(3):
        r = (10 - layer * 2) * s
        alpha = 200 - layer * 50
        surf = pygame.Surface((int(r * 2 + 4), int(r * 2 + 4)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*quantum_pink, alpha), (int(r + 2), int(r + 2)), int(r))
        surface.blit(surf, (p2_x - r - 2, p2_y - r - 2))
    
    # 纠缠丝线（波动）
    thread_points = []
    for i in range(20):
        t = i / 19
        tx = p1_x + (p2_x - p1_x) * t
        ty = p1_y + (p2_y - p1_y) * t + math.sin(t * math.pi * 3 + frame * 0.2) * 10 * s
        thread_points.append((int(tx), int(ty)))
    if len(thread_points) > 1:
        pygame.draw.lines(surface, entangle_white, False, thread_points, 2)
    
    # 概率云
    random.seed(int(frame / 10))
    for i in range(15):
        cloud_x = cx + random.gauss(0, 20 * s)
        cloud_y = cy + random.gauss(0, 15 * s)
        cloud_alpha = random.randint(30, 100)
        color = quantum_blue if random.random() > 0.5 else quantum_pink
        surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color, cloud_alpha), (5, 5), 3)
        surface.blit(surf, (cloud_x - 5, cloud_y - 5))
    
    # 测量干扰
    if frame % 60 < 10:
        measure_alpha = (10 - frame % 60) * 20
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(surf, (*entangle_white, measure_alpha), (p1_x, p1_y), (p2_x, p2_y), 4)
        surface.blit(surf, (0, 0))
    
    # 自旋指示
    for px, py, color in [(p1_x, p1_y, quantum_blue), (p2_x, p2_y, quantum_pink)]:
        spin_angle = frame * 3 if color == quantum_blue else -frame * 3
        spin_r = 15 * s
        arrow_x = px + math.cos(math.radians(spin_angle)) * spin_r
        arrow_y = py + math.sin(math.radians(spin_angle)) * spin_r
        pygame.draw.line(surface, color, (px, py), (int(arrow_x), int(arrow_y)), 1)


def _draw_nightmare_loom(surface, cx, cy, s, frame, pulse):
    """梦魇织机 - 编织噩梦的恐惧之源形态"""
    nightmare_purple = (60, 30, 80)
    fear_red = (180, 50, 80)
    dread_black = (15, 10, 20)
    
    # 织机框架（扭曲的）
    loom_distort = math.sin(frame * 0.05) * 5 * s
    loom_points = [
        (cx - 35 * s + loom_distort, cy - 25 * s),
        (cx + 35 * s - loom_distort, cy - 25 * s),
        (cx + 30 * s, cy + 25 * s),
        (cx - 30 * s, cy + 25 * s),
    ]
    pygame.draw.polygon(surface, dread_black, loom_points)
    pygame.draw.polygon(surface, nightmare_purple, loom_points, 2)
    
    # 噩梦丝线
    for i in range(10):
        thread_x = cx - 28 * s + i * 6 * s
        # 扭曲的丝线
        thread_points = []
        for j in range(8):
            ty = cy - 22 * s + j * 6 * s
            tx = thread_x + math.sin(frame * 0.1 + j * 0.5 + i * 0.3) * 5 * s
            thread_points.append((tx, ty))
        if len(thread_points) > 1:
            color = fear_red if i % 3 == 0 else nightmare_purple
            pygame.draw.lines(surface, color, False, thread_points, 2)
    
    # 噩梦图像（编织出的恐怖形象）
    # 眼睛
    for eye in range(3):
        eye_x = cx - 15 * s + eye * 15 * s
        eye_y = cy - 5 * s + math.sin(frame * 0.1 + eye) * 3 * s
        # 眼白
        pygame.draw.ellipse(surface, (200, 180, 180), (eye_x - 5 * s, eye_y - 4 * s, 10 * s, 8 * s))
        # 瞳孔（跟踪）
        pupil_offset_x = math.sin(frame * 0.08) * 2 * s
        pupil_offset_y = math.cos(frame * 0.08) * 1 * s
        pygame.draw.circle(surface, fear_red, (int(eye_x + pupil_offset_x), int(eye_y + pupil_offset_y)), int(2 * s))
    
    # 恐惧触手
    for i in range(6):
        tentacle_base_x = cx - 20 * s + i * 8 * s
        tentacle_base_y = cy + 15 * s
        tentacle_points = [(tentacle_base_x, tentacle_base_y)]
        for seg in range(5):
            seg_x = tentacle_base_x + math.sin(frame * 0.15 + seg * 0.5 + i) * (seg + 1) * 2 * s
            seg_y = tentacle_base_y + (seg + 1) * 5 * s
            tentacle_points.append((seg_x, seg_y))
        pygame.draw.lines(surface, nightmare_purple, False, tentacle_points, 2)
    
    # 恐惧光环
    fear_pulse = abs(math.sin(frame * 0.08))
    fear_r = 40 * s + fear_pulse * 5 * s
    fear_surf = pygame.Surface((int(fear_r * 2 + 10), int(fear_r * 2 + 10)), pygame.SRCALPHA)
    pygame.draw.circle(fear_surf, (*fear_red, int(50 + fear_pulse * 30)), (int(fear_r + 5), int(fear_r + 5)), int(fear_r), 3)
    surface.blit(fear_surf, (cx - fear_r - 5, cy - fear_r - 5))


def _draw_reaper_strings(surface, cx, cy, s, frame, pulse):
    """死神琴弦 - 终末收割的死亡奏鸣形态"""
    reaper_black = (15, 10, 20)
    scythe_silver = (180, 185, 200)
    soul_green = (100, 255, 150)
    death_gold = (200, 180, 100)
    
    # 死神斗篷
    cloak = [
        (cx, cy - 30 * s),
        (cx - 25 * s, cy - 10 * s),
        (cx - 30 * s, cy + 30 * s),
        (cx, cy + 25 * s),
        (cx + 30 * s, cy + 30 * s),
        (cx + 25 * s, cy - 10 * s),
    ]
    pygame.draw.polygon(surface, reaper_black, cloak)
    # 斗篷边缘
    pygame.draw.polygon(surface, (40, 35, 50), cloak, 2)
    
    # 骷髅面容
    pygame.draw.ellipse(surface, (200, 195, 180), (cx - 10 * s, cy - 28 * s, 20 * s, 22 * s))
    # 眼眶
    pygame.draw.ellipse(surface, reaper_black, (cx - 7 * s, cy - 24 * s, 6 * s, 8 * s))
    pygame.draw.ellipse(surface, reaper_black, (cx + 1 * s, cy - 24 * s, 6 * s, 8 * s))
    # 眼中灵火
    soul_flicker = int(200 + math.sin(frame * 0.2) * 55)
    pygame.draw.circle(surface, (soul_flicker, 255, 150), (int(cx - 4 * s), int(cy - 21 * s)), int(2 * s))
    pygame.draw.circle(surface, (soul_flicker, 255, 150), (int(cx + 4 * s), int(cy - 21 * s)), int(2 * s))
    # 鼻腔
    pygame.draw.polygon(surface, reaper_black, [
        (cx, cy - 18 * s), (cx - 2 * s, cy - 14 * s), (cx + 2 * s, cy - 14 * s)])
    
    # 死神镰刀
    scythe_angle = frame * 0.5
    scythe_x = cx + 20 * s
    scythe_y = cy - 5 * s
    # 镰刀杆
    pygame.draw.line(surface, (80, 60, 40), (scythe_x, scythe_y + 25 * s), (scythe_x, scythe_y - 20 * s), 3)
    # 镰刀刃（弧形）
    blade_curve = []
    for i in range(10):
        t = i / 9
        blade_angle = -30 + t * 120
        blade_r = 20 * s
        bx = scythe_x + math.cos(math.radians(blade_angle)) * blade_r
        by = scythe_y - 20 * s + math.sin(math.radians(blade_angle)) * blade_r * 0.5
        blade_curve.append((bx, by))
    pygame.draw.lines(surface, scythe_silver, False, blade_curve, 3)
    
    # 灵魂琴弦（从镰刀延伸到被收割的灵魂）
    soul_positions = [
        (cx - 35 * s, cy + 10 * s),
        (cx - 25 * s, cy + 25 * s),
        (cx + 35 * s, cy + 15 * s),
    ]
    for i, (sx, sy) in enumerate(soul_positions):
        # 琴弦
        string_wave = math.sin(frame * 0.15 + i) * 5 * s
        mid_x = (scythe_x + sx) / 2 + string_wave
        mid_y = (scythe_y + sy) / 2
        pygame.draw.line(surface, death_gold, (scythe_x, scythe_y), (mid_x, mid_y), 1)
        pygame.draw.line(surface, death_gold, (mid_x, mid_y), (sx, sy), 1)
        
        # 被收割的灵魂
        soul_alpha = int(150 + math.sin(frame * 0.1 + i) * 50)
        soul_surf = pygame.Surface((20, 25), pygame.SRCALPHA)
        pygame.draw.ellipse(soul_surf, (*soul_green, soul_alpha), (3, 0, 14, 20))
        # 灵魂挣扎
        struggle = math.sin(frame * 0.2 + i) * 3 * s
        surface.blit(soul_surf, (sx - 10 + struggle, sy - 10))
    
    # 死亡符文环
    for rune in range(8):
        rune_angle = frame * 0.3 + rune * 45
        rune_r = 38 * s
        rx = cx + math.cos(math.radians(rune_angle)) * rune_r
        ry = cy + math.sin(math.radians(rune_angle)) * rune_r
        # 符文符号（简化）
        rune_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.line(rune_surf, death_gold, (2, 2), (10, 10), 1)
        pygame.draw.line(rune_surf, death_gold, (10, 2), (2, 10), 1)
        pygame.draw.circle(rune_surf, death_gold, (6, 6), 4, 1)
        surface.blit(rune_surf, (rx - 6, ry - 6))
