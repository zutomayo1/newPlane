# -*- coding: utf-8 -*-
"""
隐藏机体渲染模块 - Puppeteer & Pandemic
"""
import pygame
import math
import random


def render_hidden(s, pid, c, edge_color, t, pulse):
    """
    渲染隐藏机体 (puppeteer, pandemic) 基础外观
    
    Args:
        s: pygame.Surface - 渲染目标
        pid: str - 机体ID
        c: tuple - 主色
        edge_color: tuple - 边缘色
        t: float - 时间参数
        pulse: float - 脉冲值
    
    Returns:
        bool - 是否成功渲染
    """
    if pid == "puppeteer":
        _render_puppeteer_base(s, c, edge_color, t, pulse)
        return True
    elif pid == "pandemic":
        _render_pandemic_base(s, c, edge_color, t, pulse)
        return True
    return False


def _render_puppeteer_base(s, c, edge_color, t, pulse):
    """Puppeteer - 牵线木偶师·玛丽奥 基础渲染"""
    # 哥特傀儡美学，提线木偶+十字架+丝线，深紫与暗金配色
    purple_dark = (80, 40, 120)
    purple_light = (150, 100, 200)
    gold_dark = (180, 150, 80)
    thread_color = (200, 180, 220)
    
    # 主体十字架控制架
    pygame.draw.rect(s, purple_dark, (55, 15, 10, 50))  # 竖杆
    pygame.draw.rect(s, purple_dark, (35, 25, 50, 8))   # 横杆
    pygame.draw.rect(s, gold_dark, (55, 15, 10, 50), 2)
    pygame.draw.rect(s, gold_dark, (35, 25, 50, 8), 2)
    
    # 中心傀儡人偶
    puppet_sway = math.sin(t * 3) * 5
    puppet_cx = 60 + puppet_sway
    # 傀儡头
    pygame.draw.circle(s, (240, 220, 200), (int(puppet_cx), 50), 12)
    pygame.draw.circle(s, purple_dark, (int(puppet_cx) - 4, 48), 3)  # 左眼
    pygame.draw.circle(s, purple_dark, (int(puppet_cx) + 4, 48), 3)  # 右眼
    pygame.draw.line(s, purple_dark, (int(puppet_cx) - 3, 55), (int(puppet_cx) + 3, 55), 2)  # 嘴
    # 傀儡身体
    pygame.draw.rect(s, purple_light, (int(puppet_cx) - 8, 62, 16, 25))
    pygame.draw.rect(s, gold_dark, (int(puppet_cx) - 8, 62, 16, 25), 1)
    # 傀儡手臂
    arm_angle_l = math.sin(t * 4) * 0.3
    arm_angle_r = math.sin(t * 4 + 1) * 0.3
    arm_l_x = puppet_cx - 8 + math.cos(arm_angle_l - 2.5) * 18
    arm_l_y = 68 + math.sin(arm_angle_l - 2.5) * 18
    arm_r_x = puppet_cx + 8 + math.cos(arm_angle_r - 0.5) * 18
    arm_r_y = 68 + math.sin(arm_angle_r - 0.5) * 18
    pygame.draw.line(s, (240, 220, 200), (int(puppet_cx) - 8, 68), (int(arm_l_x), int(arm_l_y)), 3)
    pygame.draw.line(s, (240, 220, 200), (int(puppet_cx) + 8, 68), (int(arm_r_x), int(arm_r_y)), 3)
    # 傀儡腿
    leg_angle_l = math.sin(t * 4 + 0.5) * 0.2
    leg_angle_r = math.sin(t * 4 + 1.5) * 0.2
    leg_l_x = puppet_cx - 4 + math.cos(leg_angle_l + 1.57) * 20
    leg_l_y = 87 + math.sin(leg_angle_l + 1.57) * 20
    leg_r_x = puppet_cx + 4 + math.cos(leg_angle_r + 1.57) * 20
    leg_r_y = 87 + math.sin(leg_angle_r + 1.57) * 20
    pygame.draw.line(s, (240, 220, 200), (int(puppet_cx) - 4, 87), (int(leg_l_x), int(leg_l_y)), 3)
    pygame.draw.line(s, (240, 220, 200), (int(puppet_cx) + 4, 87), (int(leg_r_x), int(leg_r_y)), 3)
    
    # 提线（从控制架到傀儡各部位）
    thread_points = [
        (60, 33, puppet_cx, 38),        # 头
        (45, 29, arm_l_x, arm_l_y),     # 左手
        (75, 29, arm_r_x, arm_r_y),     # 右手
        (50, 29, leg_l_x, leg_l_y),     # 左脚
        (70, 29, leg_r_x, leg_r_y),     # 右脚
    ]
    for tx1, ty1, tx2, ty2 in thread_points:
        # 丝线闪烁效果
        thread_alpha = int(150 + 50 * math.sin(t * 6 + tx1 * 0.1))
        thread_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(thread_surf, (*thread_color, thread_alpha), 
                       (int(tx1), int(ty1)), (int(tx2), int(ty2)), 1)
        s.blit(thread_surf, (0, 0))
    
    # 环绕的小傀儡灵魂（6个）
    for soul_i in range(6):
        soul_angle = (soul_i * 60 + t * 30) * 0.01745
        soul_r = 48
        soul_x = 60 + math.cos(soul_angle) * soul_r
        soul_y = 60 + math.sin(soul_angle) * soul_r
        # 迷你傀儡头
        soul_alpha = int(180 + 50 * math.sin(t * 4 + soul_i))
        soul_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(soul_surf, (*purple_light, soul_alpha), (int(soul_x), int(soul_y)), 6)
        pygame.draw.circle(soul_surf, (*gold_dark, soul_alpha), (int(soul_x), int(soul_y)), 6, 1)
        # 迷你X眼
        pygame.draw.line(soul_surf, (*purple_dark, soul_alpha), 
                       (int(soul_x) - 2, int(soul_y) - 2), (int(soul_x) + 2, int(soul_y) + 2), 1)
        pygame.draw.line(soul_surf, (*purple_dark, soul_alpha), 
                       (int(soul_x) - 2, int(soul_y) + 2), (int(soul_x) + 2, int(soul_y) - 2), 1)
        s.blit(soul_surf, (0, 0))
    
    # 命运丝线网络（连接各小傀儡）
    for net_i in range(6):
        net_angle1 = (net_i * 60 + t * 30) * 0.01745
        net_angle2 = ((net_i + 1) * 60 + t * 30) * 0.01745
        nx1 = 60 + math.cos(net_angle1) * 48
        ny1 = 60 + math.sin(net_angle1) * 48
        nx2 = 60 + math.cos(net_angle2) * 48
        ny2 = 60 + math.sin(net_angle2) * 48
        net_alpha = int(80 + 40 * math.sin(t * 3 + net_i))
        net_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(net_surf, (*thread_color, net_alpha), 
                       (int(nx1), int(ny1)), (int(nx2), int(ny2)), 1)
        s.blit(net_surf, (0, 0))


def _render_pandemic_base(s, c, edge_color, t, pulse):
    """Pandemic - 末日瘟神·零号 基础渲染"""
    # 生化瘟疫美学，病毒+细菌+毒雾，毒绿与腐紫配色
    toxic_green = (80, 255, 80)
    decay_purple = (150, 80, 180)
    bio_yellow = (200, 200, 80)
    fog_color = (100, 180, 100)
    
    # 主体病毒球体
    pygame.draw.circle(s, decay_purple, (60, 60), 35)
    pygame.draw.circle(s, (100, 50, 130), (60, 60), 30)
    pygame.draw.circle(s, toxic_green, (60, 60), 35, 2)
    
    # 病毒刺突蛋白（16个）
    for spike_i in range(16):
        spike_angle = (spike_i * 22.5 + t * 20) * 0.01745
        spike_base_r = 32
        spike_tip_r = 42 + int(3 * math.sin(t * 5 + spike_i))
        spike_bx = 60 + math.cos(spike_angle) * spike_base_r
        spike_by = 60 + math.sin(spike_angle) * spike_base_r
        spike_tx = 60 + math.cos(spike_angle) * spike_tip_r
        spike_ty = 60 + math.sin(spike_angle) * spike_tip_r
        # 刺突杆
        pygame.draw.line(s, toxic_green, (int(spike_bx), int(spike_by)), 
                       (int(spike_tx), int(spike_ty)), 2)
        # 刺突头（球形）
        pygame.draw.circle(s, bio_yellow, (int(spike_tx), int(spike_ty)), 4)
        pygame.draw.circle(s, toxic_green, (int(spike_tx), int(spike_ty)), 4, 1)
    
    # 内部DNA/RNA螺旋
    for helix_i in range(24):
        helix_progress = helix_i / 24
        helix_angle = (helix_progress * 720 + t * 60) * 0.01745
        helix_r = 18
        helix_offset = 8 * math.sin(helix_progress * math.pi * 4)
        # 双螺旋
        hx1 = 60 + math.cos(helix_angle) * (helix_r + helix_offset) * 0.5
        hy1 = 60 + helix_progress * 40 - 20
        hx2 = 60 + math.cos(helix_angle + math.pi) * (helix_r + helix_offset) * 0.5
        hy2 = hy1
        if 35 < hy1 < 85:  # 只在球体内部绘制
            pygame.draw.circle(s, toxic_green, (int(hx1), int(hy1)), 2)
            pygame.draw.circle(s, bio_yellow, (int(hx2), int(hy2)), 2)
            # 碱基对连接
            if helix_i % 3 == 0:
                pygame.draw.line(s, (150, 200, 150), (int(hx1), int(hy1)), 
                               (int(hx2), int(hy2)), 1)
    
    # 毒雾粒子扩散（20个）
    for fog_i in range(20):
        fog_phase = ((t * 2 + fog_i * 0.15) % 1.0)
        fog_angle = (fog_i * 18 + t * 8) * 0.01745
        fog_r = 35 + fog_phase * 25
        fog_x = 60 + math.cos(fog_angle) * fog_r
        fog_y = 60 + math.sin(fog_angle) * fog_r
        fog_alpha = int(150 * (1 - fog_phase))
        fog_size = int(6 * (1 - fog_phase * 0.5))
        if fog_alpha > 0:
            fog_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(fog_surf, (*fog_color, fog_alpha), 
                             (int(fog_x), int(fog_y)), fog_size)
            s.blit(fog_surf, (0, 0))
    
    # 感染标记（生物危害符号）
    bio_r = 12
    for bio_i in range(3):
        bio_angle = (bio_i * 120 + 30) * 0.01745
        bx = 60 + math.cos(bio_angle) * bio_r
        by = 60 + math.sin(bio_angle) * bio_r
        # 扇形
        arc_start = bio_angle - 0.4
        arc_end = bio_angle + 0.4
        arc_points = [(60, 60)]
        for arc_seg in range(8):
            arc_a = arc_start + (arc_end - arc_start) * arc_seg / 7
            ax = 60 + math.cos(arc_a) * 20
            ay = 60 + math.sin(arc_a) * 20
            arc_points.append((int(ax), int(ay)))
        if len(arc_points) > 2:
            pygame.draw.polygon(s, toxic_green, arc_points)
    pygame.draw.circle(s, (100, 50, 130), (60, 60), 8)
    
    # 变异闪烁效果
    mutation_pulse = abs(math.sin(t * 4))
    if mutation_pulse > 0.8:
        pulse_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse_alpha = int((mutation_pulse - 0.8) * 5 * 200)
        pygame.draw.circle(pulse_surf, (*toxic_green, pulse_alpha), (60, 60), 40)
        s.blit(pulse_surf, (0, 0))
