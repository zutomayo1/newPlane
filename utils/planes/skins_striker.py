# -*- coding: utf-8 -*-
"""
Striker 专属涂装模块
"""
import pygame
import math
import random


def render_striker_skin(s, model_style, c, edge_color, t, pulse):
    """
    渲染 Striker 专属涂装
    
    Returns:
        pygame.Surface or None - 成功返回渲染结果，不匹配返回 None
    """
    if model_style == "mech_wings":
        # 机械飞升：纳米机械装甲，悬浮零件
        pygame.draw.polygon(s, (60, 60, 80), [(60, 10), (90, 90), (60, 85), (30, 90)])
        pygame.draw.polygon(s, c, [(60, 15), (85, 85), (60, 80), (35, 85)])
        
        # 悬浮机械零件
        gear_radius = 5 + int(3 * pulse)
        for i in range(4):
            angle = t * 2 + i * math.pi / 2
            gx = 60 + math.cos(angle) * 35
            gy = 50 + math.sin(angle) * 35
            pygame.draw.circle(s, (0, 255, 255), (int(gx), int(gy)), gear_radius)
            pygame.draw.circle(s, (255, 200, 0), (int(gx), int(gy)), gear_radius - 2)
        
        # 双涡轮推进器
        turbo_pulse = int(5 * pulse)
        pygame.draw.circle(s, (0, 200, 255), (40, 80), 8 + turbo_pulse)
        pygame.draw.circle(s, (0, 200, 255), (80, 80), 8 + turbo_pulse)
        pygame.draw.circle(s, (255, 255, 255), (40, 80), 4)
        pygame.draw.circle(s, (255, 255, 255), (80, 80), 4)
        
        # 机械关节连线
        pygame.draw.line(s, (100, 255, 255), (60, 40), (40, 80), 2)
        pygame.draw.line(s, (100, 255, 255), (60, 40), (80, 80), 2)
        return s

    elif model_style == "phase_shift":
        # 暗影相位：半透明，相位扭曲，暗影分身
        s2 = pygame.Surface((120, 120), pygame.SRCALPHA)
        main_alpha = 120 + int(50 * pulse)
        pygame.draw.polygon(s2, (*c[:3], main_alpha), [(60, 10), (90, 90), (60, 85), (30, 90)])
        s.blit(s2, (0, 0))
        
        # 相位扭曲效果 - 多层分身
        for i in range(3):
            offset_x = int(10 * math.sin(t * 3 + i))
            offset_y = int(5 * math.cos(t * 3 + i))
            alpha = 40 - i * 10
            s3 = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(s3, (80, 80, 150, alpha), 
                              [(60 + offset_x, 10 + offset_y), 
                               (90 + offset_x, 90 + offset_y), 
                               (60 + offset_x, 85 + offset_y), 
                               (30 + offset_x, 90 + offset_y)])
            s.blit(s3, (0, 0))
        
        # 空间裂缝纹理
        for i in range(5):
            y = 20 + i * 15
            x_offset = int(5 * math.sin(t * 4 + i))
            pygame.draw.line(s, (150, 150, 200), (40 + x_offset, y), (80 - x_offset, y), 1)
        return s

    elif model_style == "critical_mass":
        # 核心熔毁：反应堆过载，岩浆裂痕，爆炸火花
        pygame.draw.polygon(s, (100, 50, 0), [(60, 10), (90, 90), (60, 85), (30, 90)])
        
        # 核心反应堆（脉动）
        core_size = 15 + int(8 * pulse)
        pygame.draw.circle(s, (255, 200, 0), (60, 50), core_size)
        pygame.draw.circle(s, (255, 100, 0), (60, 50), core_size - 5)
        pygame.draw.circle(s, (255, 50, 0), (60, 50), core_size - 10)
        
        # 裂痕系统 - 岩浆流淌
        crack_lines = [
            [(60, 50), (40, 30), (30, 40)],
            [(60, 50), (80, 30), (90, 40)],
            [(60, 50), (50, 70), (40, 85)],
            [(60, 50), (70, 70), (80, 85)]
        ]
        for crack in crack_lines:
            pygame.draw.lines(s, (255, 255, 0), False, crack, 2)
            pygame.draw.lines(s, (255, 150, 0), False, crack, 1)
        
        # 爆炸火花粒子
        if random.random() < 0.5:
            for i in range(3):
                spark_x = 60 + random.randint(-20, 20)
                spark_y = 50 + random.randint(-20, 20)
                spark_size = random.randint(2, 4)
                pygame.draw.circle(s, (255, 255, 100), (spark_x, spark_y), spark_size)
        
        # 能量波纹扩散
        wave_radius = int(30 + 15 * pulse)
        pygame.draw.circle(s, (255, 100, 0), (60, 50), wave_radius, 2)
        return s

    elif model_style == "quantum_flux":
        # 量子纠缠：薛定谔之翼，量子叠加态
        base_points = [(60, 10), (90, 90), (60, 85), (30, 90)]
        
        # 量子叠加 - 同时存在多个位置
        for i in range(5):
            phase_offset = t * 5 + i * 0.4
            offset_x = int(15 * math.sin(phase_offset))
            offset_y = int(10 * math.cos(phase_offset * 1.3))
            alpha = 60 - i * 10
            
            s4 = pygame.Surface((120, 120), pygame.SRCALPHA)
            shifted_points = [(p[0] + offset_x, p[1] + offset_y) for p in base_points]
            pygame.draw.polygon(s4, (*c[:3], alpha), shifted_points)
            s.blit(s4, (0, 0))
        
        # 量子纠缠连线
        for i in range(4):
            angle = t * 4 + i * math.pi / 2
            qx = 60 + math.cos(angle) * 40
            qy = 50 + math.sin(angle) * 30
            pygame.draw.line(s, (150, 255, 255), (60, 50), (int(qx), int(qy)), 1)
            pygame.draw.circle(s, (255, 150, 255), (int(qx), int(qy)), 3)
        
        # 粒子风暴
        for i in range(8):
            storm_angle = t * 10 + i * math.pi / 4
            storm_dist = 25 + 10 * math.sin(t * 8 + i)
            sx = 60 + math.cos(storm_angle) * storm_dist
            sy = 50 + math.sin(storm_angle) * storm_dist
            pygame.draw.circle(s, (200, 220, 255), (int(sx), int(sy)), 2)
        return s

    elif model_style == "seraph_wings":
        # 天使降临：神圣羽翼，光之使者，圣光柱
        pygame.draw.polygon(s, (200, 200, 150), [(60, 15), (80, 85), (60, 80), (40, 85)])
        
        # 天使光环
        halo_pulse = 25 + int(5 * pulse)
        pygame.draw.circle(s, (255, 255, 220), (60, 20), halo_pulse, 3)
        pygame.draw.circle(s, (255, 255, 255), (60, 20), halo_pulse - 5, 2)
        
        # 神圣羽翼展开（六翼）
        wing_colors = [(255, 255, 230), (255, 250, 220), (255, 245, 210)]
        for layer in range(3):
            wing_y = 40 + layer * 5
            # 左翼
            left_wing = [(40, wing_y), (10, wing_y - 10), (5, wing_y + 15), (30, wing_y + 10)]
            pygame.draw.polygon(s, wing_colors[layer], left_wing)
            pygame.draw.polygon(s, (255, 255, 255), left_wing, 1)
            # 右翼
            right_wing = [(80, wing_y), (110, wing_y - 10), (115, wing_y + 15), (90, wing_y + 10)]
            pygame.draw.polygon(s, wing_colors[layer], right_wing)
            pygame.draw.polygon(s, (255, 255, 255), right_wing, 1)
        
        # 圣光柱
        beam_alpha = 100 + int(50 * pulse)
        s5 = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.rect(s5, (255, 255, 255, beam_alpha), (55, 0, 10, 120))
        s.blit(s5, (0, 0))
        
        # 光之粒子环绕
        for i in range(6):
            particle_angle = t * 3 + i * math.pi / 3
            px = 60 + math.cos(particle_angle) * 35
            py = 50 + math.sin(particle_angle) * 35
            pygame.draw.circle(s, (255, 255, 200), (int(px), int(py)), 3)
        return s

    elif model_style == "eastern_dragon":
        # 赤龙之怒：东方神龙
        dragon_body = []
        for i in range(8):
            segment_y = 15 + i * 10
            segment_x = 60 + int(8 * math.sin(t * 3 + i * 0.5))
            dragon_body.append((segment_x, segment_y))
        
        # 绘制龙身
        for i in range(len(dragon_body) - 1):
            width = 20 - i * 2
            pygame.draw.line(s, (220, 0, 0), dragon_body[i], dragon_body[i + 1], width)
            pygame.draw.line(s, (255, 215, 0), dragon_body[i], dragon_body[i + 1], width - 4)
        
        # 龙首机头
        head_x, head_y = dragon_body[0]
        dragon_head = [(head_x, head_y - 10), (head_x - 12, head_y), (head_x - 8, head_y + 8), 
                      (head_x, head_y + 5), (head_x + 8, head_y + 8), (head_x + 12, head_y)]
        pygame.draw.polygon(s, (200, 0, 0), dragon_head)
        pygame.draw.polygon(s, (255, 215, 0), dragon_head, 2)
        
        # 龙角
        pygame.draw.line(s, (255, 215, 0), (head_x - 8, head_y - 5), (head_x - 15, head_y - 15), 3)
        pygame.draw.line(s, (255, 215, 0), (head_x + 8, head_y - 5), (head_x + 15, head_y - 15), 3)
        
        # 龙眼
        pygame.draw.circle(s, (255, 255, 0), (head_x - 5, head_y - 3), 3)
        pygame.draw.circle(s, (255, 255, 0), (head_x + 5, head_y - 3), 3)
        pygame.draw.circle(s, (255, 0, 0), (head_x - 5, head_y - 3), 1)
        pygame.draw.circle(s, (255, 0, 0), (head_x + 5, head_y - 3), 1)
        
        # 龙爪机翼
        mid_x, mid_y = dragon_body[3]
        claw_left = [(mid_x - 10, mid_y), (mid_x - 25, mid_y - 10), (mid_x - 30, mid_y - 5)]
        pygame.draw.lines(s, (255, 215, 0), False, claw_left, 3)
        for i in range(3):
            pygame.draw.line(s, (255, 215, 0), (mid_x - 30, mid_y - 5 + i * 3), 
                           (mid_x - 35, mid_y - 5 + i * 3), 2)
        claw_right = [(mid_x + 10, mid_y), (mid_x + 25, mid_y - 10), (mid_x + 30, mid_y - 5)]
        pygame.draw.lines(s, (255, 215, 0), False, claw_right, 3)
        for i in range(3):
            pygame.draw.line(s, (255, 215, 0), (mid_x + 30, mid_y - 5 + i * 3), 
                           (mid_x + 35, mid_y - 5 + i * 3), 2)
        
        # 金色龙鳞纹理
        for i in range(1, len(dragon_body) - 1):
            scale_x, scale_y = dragon_body[i]
            pygame.draw.circle(s, (255, 215, 0), (scale_x - 6, scale_y), 2)
            pygame.draw.circle(s, (255, 215, 0), (scale_x + 6, scale_y), 2)
        return s

    elif model_style == "energy_blade":
        # 无尽锋刃：能量光剑
        pygame.draw.rect(s, (100, 100, 150), (55, 40, 10, 30))
        pygame.draw.circle(s, (0, 255, 255), (60, 55), 8)
        
        blade_glow = int(5 * pulse)
        blade_points = [(60, 10), (65 + blade_glow, 15), (68, 85), (60, 95), (52, 85), (55 - blade_glow, 15)]
        
        # 多层光剑效果
        s6 = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(s6, (0, 255, 255, 100), blade_points)
        s.blit(s6, (0, 0))
        
        pygame.draw.polygon(s, (100, 255, 255), blade_points, 3)
        pygame.draw.polygon(s, (255, 255, 255), [(60, 15), (63, 20), (63, 90), (60, 90), (57, 90), (57, 20)])
        
        # 刀刃机翼
        left_blade = [(60, 45), (20, 35), (15, 50), (40, 60)]
        s7 = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(s7, (0, 255, 255, 150), left_blade)
        s.blit(s7, (0, 0))
        pygame.draw.polygon(s, (150, 200, 255), left_blade, 2)
        
        right_blade = [(60, 45), (100, 35), (105, 50), (80, 60)]
        s8 = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(s8, (255, 0, 255, 150), right_blade)
        s.blit(s8, (0, 0))
        pygame.draw.polygon(s, (255, 150, 255), right_blade, 2)
        
        # 闪电链连接
        if random.random() < 0.4:
            for i in range(2):
                lx = random.randint(40, 80)
                ly = random.randint(20, 80)
                pygame.draw.line(s, (255, 255, 255), (60, 55), (lx, ly), 1)
        
        # 等离子刃光粒子
        for i in range(6):
            blade_angle = t * 8 + i * math.pi / 3
            blade_dist = 30 + 5 * math.sin(t * 10 + i)
            bx = 60 + math.cos(blade_angle) * blade_dist
            by = 50 + math.sin(blade_angle) * blade_dist
            pygame.draw.circle(s, (150, 200, 255), (int(bx), int(by)), 2)
        return s

    elif model_style == "striker_heavy":
        # 重装突击：厚重的装甲板
        pygame.draw.rect(s, (100, 50, 50), (40, 20, 40, 80))
        pygame.draw.rect(s, (150, 80, 80), (30, 40, 60, 40))
        pygame.draw.rect(s, c, (45, 25, 30, 70))
        for y in range(30, 100, 20):
            pygame.draw.circle(s, (200, 200, 200), (42, y), 2)
            pygame.draw.circle(s, (200, 200, 200), (78, y), 2)
        return s

    elif model_style == "striker_speed":
        # 极速锋刃：细长的针状机体
        pygame.draw.polygon(s, c, [(60, 0), (70, 100), (60, 90), (50, 100)])
        pygame.draw.line(s, (255, 255, 255), (60, 0), (60, 100), 2)
        pygame.draw.polygon(s, edge_color, [(60, 40), (90, 80), (60, 70)])
        pygame.draw.polygon(s, edge_color, [(60, 40), (30, 80), (60, 70)])
        return s

    elif model_style == "striker_overload":
        # 能量过载
        pygame.draw.polygon(s, c, [(60, 10), (90, 90), (60, 85), (30, 90)])
        overload_pulse = int(20 * pulse)
        for i in range(3):
            radius = 20 + i * 10 + overload_pulse
            alpha = 100 - i * 30
            energy_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(energy_surf, (0, 255, 255, alpha), (60, 50), radius)
            s.blit(energy_surf, (0, 0))
        return s

    elif model_style == "striker_hologram":
        # 全息投影
        base_alpha = 80 + int(60 * pulse)
        s_holo = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(s_holo, (*c[:3], base_alpha), [(60, 10), (90, 90), (60, 85), (30, 90)])
        s.blit(s_holo, (0, 0))
        # 扫描线
        for y in range(0, 120, 4):
            line_alpha = int(30 + 20 * math.sin(t * 10 + y * 0.1))
            pygame.draw.line(s, (0, 255, 255, line_alpha), (0, y), (120, y), 1)
        return s

    elif model_style == "striker_mecha_god":
        # 机神形态
        pygame.draw.polygon(s, (80, 80, 100), [(60, 5), (100, 85), (60, 95), (20, 85)])
        pygame.draw.polygon(s, (0, 255, 255), [(60, 10), (95, 80), (60, 90), (25, 80)])
        # 机神光环
        for i in range(3):
            ring_radius = 30 + i * 8
            pygame.draw.circle(s, (0, 200, 255), (60, 50), ring_radius, 1)
        return s

    elif model_style == "striker_cyber_dragon":
        # 赛博龙形态
        pygame.draw.polygon(s, (200, 0, 100), [(60, 5), (90, 40), (85, 95), (60, 85), (35, 95), (30, 40)])
        # 龙翼
        pygame.draw.polygon(s, (255, 0, 150), [(30, 40), (5, 30), (15, 60)])
        pygame.draw.polygon(s, (255, 0, 150), [(90, 40), (115, 30), (105, 60)])
        # 龙眼
        pygame.draw.circle(s, (0, 255, 255), (50, 30), 4)
        pygame.draw.circle(s, (0, 255, 255), (70, 30), 4)
        return s

    elif model_style == "striker_dimension_breaker":
        # 次元破碎者
        pygame.draw.polygon(s, (50, 0, 100), [(60, 10), (90, 90), (60, 85), (30, 90)])
        # 次元裂缝
        for i in range(5):
            crack_y = 20 + i * 15
            crack_offset = int(10 * math.sin(t * 3 + i))
            pygame.draw.line(s, (200, 0, 255), (40 + crack_offset, crack_y), (80 - crack_offset, crack_y + 10), 2)
        return s

    elif model_style == "striker_ex":
        # 裂空雷刃 - 分叉闪电刀刃，动态电弧
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主刃身（闪电形状）
        blade_points = [(60, 10), (70, 35), (65, 35), (75, 60), (70, 60), (80, 90), (60, 75), (40, 90), (50, 60), (45, 60), (55, 35), (50, 35)]
        pygame.draw.polygon(s, (255, 255, 100), blade_points)
        pygame.draw.polygon(s, (255, 255, 255), blade_points, 3)
        
        # 电弧效果
        for i in range(6):
            if random.random() < 0.3:
                start_idx = random.randint(0, len(blade_points)-1)
                end_idx = random.randint(0, len(blade_points)-1)
                pygame.draw.line(s, (200, 255, 255), blade_points[start_idx], blade_points[end_idx], 2)
        
        # 能量核心
        pygame.draw.circle(s, (255, 255, 255), (60, 50), int(8 * pulse))
        
        return s

    elif model_style == "striker_ex2":
        # 龙卷风暴 - 螺旋气流，风刃切割
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 中心风眼
        pygame.draw.circle(s, (100, 255, 100), (60, 50), int(10 * pulse))
        
        # 螺旋气流（3层）
        for layer in range(3):
            spiral_radius = 20 + layer * 15
            for i in range(12):
                angle = (t * 4 + i * math.pi / 6 + layer) % (2 * math.pi)
                x = 60 + math.cos(angle) * spiral_radius
                y = 50 + math.sin(angle) * spiral_radius
                # 风刃形状
                blade_points = [
                    (x, y),
                    (x + math.cos(angle + 0.5) * 8, y + math.sin(angle + 0.5) * 8),
                    (x + math.cos(angle - 0.5) * 8, y + math.sin(angle - 0.5) * 8)
                ]
                pygame.draw.polygon(s, (150, 255, 150, 200 - layer * 50), [(int(p[0]), int(p[1])) for p in blade_points])
        
        return s

    elif model_style == "striker_ex3":
        # 次元裂缝 - 空间碎裂，现实崩塌
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体裂缝（闪电形状但更扭曲）
        crack_center = (60, 50)
        crack_segments = []
        for i in range(20):
            angle = (i / 20) * math.pi * 2 + t * 0.5
            dist = 15 + 25 * (i / 20) + math.sin(t * 3 + i) * 8
            x = crack_center[0] + math.cos(angle) * dist
            y = crack_center[1] + math.sin(angle) * dist
            crack_segments.append((int(x), int(y)))
        
        # 绘制扭曲裂缝
        for i in range(len(crack_segments) - 1):
            # 多层裂缝效果
            for layer in range(3):
                offset = layer * 2
                color_intensity = 255 - layer * 80
                crack_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(crack_surf, (color_intensity, 0, color_intensity, 220 - layer * 50),
                               (crack_segments[i][0] + offset, crack_segments[i][1]),
                               (crack_segments[i+1][0] + offset, crack_segments[i+1][1]), 4 - layer)
                s.blit(crack_surf, (0, 0))
        
        # 空间碎片（漂浮的碎裂空间）
        for frag in range(25):
            frag_angle = t * 2 + frag * 0.4
            frag_dist = 20 + 30 * ((frag % 5) / 5)
            frag_x = 60 + math.cos(frag_angle) * frag_dist
            frag_y = 50 + math.sin(frag_angle) * frag_dist
            frag_rotation = t * 3 + frag
            
            # 碎片形状（不规则四边形）
            frag_points = []
            for i in range(4):
                fp_angle = frag_rotation + i * math.pi / 2
                fp_dist = 5 + random.randint(-2, 2)
                frag_points.append((int(frag_x + math.cos(fp_angle) * fp_dist),
                                  int(frag_y + math.sin(fp_angle) * fp_dist)))
            
            frag_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(frag_surf, (200, 0, 255, 180), frag_points)
            pygame.draw.polygon(frag_surf, (255, 100, 255, 220), frag_points, 2)
            s.blit(frag_surf, (0, 0))
        
        # 维度扭曲波纹
        for wave in range(5):
            wave_radius = (t * 70 + wave * 20) % 100
            wave_alpha = int(200 * (1 - wave_radius / 100))
            for angle_seg in range(8):
                seg_angle = angle_seg * math.pi / 4
                distortion = math.sin(t * 4 + angle_seg) * 10
                wx = 60 + math.cos(seg_angle) * (wave_radius + distortion)
                wy = 50 + math.sin(seg_angle) * (wave_radius + distortion)
                if angle_seg < 7:
                    next_angle = (angle_seg + 1) * math.pi / 4
                    next_distortion = math.sin(t * 4 + angle_seg + 1) * 10
                    next_wx = 60 + math.cos(next_angle) * (wave_radius + next_distortion)
                    next_wy = 50 + math.sin(next_angle) * (wave_radius + next_distortion)
                    wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(wave_surf, (255, 0, 255, wave_alpha),
                                   (int(wx), int(wy)), (int(next_wx), int(next_wy)), 3)
                    s.blit(wave_surf, (0, 0))
        
        return s

    elif model_style == "striker_ex4":
        # 液态金属 - 活体机械
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 流动的液态金属效果（像水银一样）
        blob_count = 12
        for blob in range(blob_count):
            # 每个液滴的运动轨迹
            blob_angle = (blob / blob_count) * math.pi * 2 + t * 1.5
            blob_orbit = 20 + 10 * math.sin(t * 2 + blob * 0.5)
            blob_x = 60 + math.cos(blob_angle) * blob_orbit
            blob_y = 50 + math.sin(blob_angle) * blob_orbit
            
            # 液滴大小变化（呼吸效果）
            blob_size = 8 + 4 * math.sin(t * 3 + blob)
            
            # 金属反光效果（多层渐变）
            for layer in range(4, 0, -1):
                layer_size = blob_size * (layer / 4)
                layer_brightness = 140 + int(80 * (layer / 4))
                pygame.draw.circle(s, (layer_brightness, layer_brightness, layer_brightness + 20),
                                 (int(blob_x), int(blob_y)), int(layer_size))
        
        # 液态连接线（液滴之间的金属丝）
        for i in range(blob_count):
            angle_i = (i / blob_count) * math.pi * 2 + t * 1.5
            orbit_i = 20 + 10 * math.sin(t * 2 + i * 0.5)
            x1 = 60 + math.cos(angle_i) * orbit_i
            y1 = 50 + math.sin(angle_i) * orbit_i
            
            # 连接到相邻液滴
            next_i = (i + 1) % blob_count
            angle_next = (next_i / blob_count) * math.pi * 2 + t * 1.5
            orbit_next = 20 + 10 * math.sin(t * 2 + next_i * 0.5)
            x2 = 60 + math.cos(angle_next) * orbit_next
            y2 = 50 + math.sin(angle_next) * orbit_next
            
            # 波动的连接线
            segments = 5
            for seg in range(segments):
                seg_prog = seg / segments
                sx = x1 + (x2 - x1) * seg_prog
                sy = y1 + (y2 - y1) * seg_prog
                wave_offset = 3 * math.sin(t * 4 + seg + i)
                perp_angle = angle_i + math.pi / 2
                sx += math.cos(perp_angle) * wave_offset
                sy += math.sin(perp_angle) * wave_offset
                
                if seg < segments - 1:
                    next_prog = (seg + 1) / segments
                    ex = x1 + (x2 - x1) * next_prog
                    ey = y1 + (y2 - y1) * next_prog
                    next_wave = 3 * math.sin(t * 4 + seg + 1 + i)
                    ex += math.cos(perp_angle) * next_wave
                    ey += math.sin(perp_angle) * next_wave
                    
                    pygame.draw.line(s, (180, 180, 200), 
                                   (int(sx), int(sy)), (int(ex), int(ey)), 2)
        
        # 机械呼吸效果（中心脉动）
        breath_radius = int(15 + 8 * math.sin(t * 1.5))
        for ring in range(3):
            ring_radius = breath_radius + ring * 5
            ring_alpha = int(150 - ring * 40)
            ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (200, 200, 220, ring_alpha), (60, 50), ring_radius, 2)
            s.blit(ring_surf, (0, 0))
        
        # 流动粒子（展现液态特性）
        for particle in range(20):
            p_progress = (t * 2 + particle * 0.15) % 1
            p_angle = particle * 0.7 + t * 0.5
            p_dist = 15 + p_progress * 35
            px = 60 + math.cos(p_angle) * p_dist
            py = 50 + math.sin(p_angle) * p_dist
            p_alpha = int(200 * (1 - p_progress))
            
            if p_alpha > 30:
                pygame.draw.circle(s, (220, 220, 240, p_alpha), (int(px), int(py)), 2)
        
        return s

    elif model_style == "striker_ex5":
        # 像素进化·8bit回忆
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        plane_size = (120, 120)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        pixel_size = int(abs(math.sin(t * 0.5)) * 15) + 3
        
        # 像素化效果
        for py_coord in range(0, plane_size[1], pixel_size):
            for px_coord in range(0, plane_size[0], pixel_size):
                color_phase = (px_coord + py_coord + t * 50) / 50.0
                r = int(128 + 127 * math.sin(color_phase))
                g = int(128 + 127 * math.sin(color_phase + 2.094))
                b = int(128 + 127 * math.sin(color_phase + 4.189))
                pygame.draw.rect(plane_surf, (r, g, b), (px_coord, py_coord, pixel_size, pixel_size))
        
        # 像素方块重组动画
        for i in range(25):
            angle = t * 2 + i * 0.25
            radius = 20 + math.sin(t + i * 0.5) * 10
            block_x = center[0] + math.cos(angle) * radius
            block_y = center[1] + math.sin(angle) * radius
            block_size = int(abs(math.sin(t * 2 + i)) * 8) + 4
            block_color = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)][i % 4]
            pygame.draw.rect(plane_surf, block_color, (block_x - block_size//2, block_y - block_size//2, block_size, block_size), 2)
        return plane_surf

    return None


# 涂装列表
STRIKER_STYLES = [
    "mech_wings", "phase_shift", "critical_mass", "quantum_flux",
    "seraph_wings", "eastern_dragon", "energy_blade",
    "striker_heavy", "striker_speed", "striker_overload", "striker_hologram",
    "striker_mecha_god", "striker_cyber_dragon", "striker_dimension_breaker",
    "striker_ex", "striker_ex2", "striker_ex3", "striker_ex4", "striker_ex5"
]


def is_striker_style(model_style):
    """检查是否是 Striker 专属涂装"""
    return model_style in STRIKER_STYLES
