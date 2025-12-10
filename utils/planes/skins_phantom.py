# -*- coding: utf-8 -*-
"""
Phantom 专属涂装模块
"""
import pygame
import math
import random


def render_phantom_skin(s, model_style, c, edge_color, t, pulse):
    """
    渲染 Phantom 专属涂装
    
    Returns:
        pygame.Surface or None - 成功返回渲染结果，不匹配返回 None
    """
    if model_style == "void_walker":
        # 虚空行者：星云纹理，虚空裂痕，黑洞效果
        void_center = (60, 50)
        for i in range(5):
            radius = 35 - i * 6
            alpha = 50 + i * 20
            void_color = (120 - i * 20, 0, 220 - i * 30, alpha)
            s_void = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(s_void, void_color, void_center, radius)
            s.blit(s_void, (0, 0))
        
        # 星云流动纹理
        for i in range(8):
            angle = t * 2 + i * math.pi / 4
            dist = 40 + 10 * math.sin(t * 3 + i)
            nx = 60 + math.cos(angle) * dist
            ny = 50 + math.sin(angle) * dist
            nebula_size = 8 + int(4 * math.sin(t * 5 + i))
            s_nebula = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(s_nebula, (200, 100, 255, 80), (int(nx), int(ny)), nebula_size)
            s.blit(s_nebula, (0, 0))
        
        # 虚空裂痕
        crack_points = [
            [(40, 30), (35, 40), (30, 50)],
            [(80, 30), (85, 40), (90, 50)],
            [(50, 70), (45, 80), (40, 90)],
            [(70, 70), (75, 80), (80, 90)]
        ]
        for crack in crack_points:
            for i in range(len(crack) - 1):
                pygame.draw.line(s, (140, 50, 200), crack[i], crack[i + 1], 2)
                s_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(s_glow, (200, 100, 255, 100), crack[i], crack[i + 1], 4)
                s.blit(s_glow, (0, 0))
        
        # 虚空粒子旋涡
        for i in range(12):
            spiral_angle = t * 4 + i * math.pi / 6
            spiral_dist = 25 + i * 2
            vx = 60 + math.cos(spiral_angle) * spiral_dist
            vy = 50 + math.sin(spiral_angle) * spiral_dist
            pygame.draw.circle(s, (140, 50, 200), (int(vx), int(vy)), 2)
        return s

    elif model_style == "multi_ghost":
        # 千幻魔影：多层幽灵分身，魂火粒子，灵魂锁链
        base_shape = [(60, 15), (85, 85), (60, 75), (35, 85)]
        
        # 6层幽灵分身
        for i in range(6):
            offset_angle = t * 2 + i * math.pi / 3
            offset_x = int(15 * math.cos(offset_angle))
            offset_y = int(10 * math.sin(offset_angle))
            alpha = 120 - i * 15
            
            ghost_shape = [(p[0] + offset_x, p[1] + offset_y) for p in base_shape]
            s_ghost = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(s_ghost, (200, 200, 255, alpha), ghost_shape)
            s.blit(s_ghost, (0, 0))
            pygame.draw.polygon(s, (240, 240, 255), ghost_shape, 1)
        
        # 魂火粒子浮游
        for i in range(8):
            soul_angle = t * 3 + i * math.pi / 4
            soul_dist = 35 + 5 * math.sin(t * 6 + i)
            soul_x = 60 + math.cos(soul_angle) * soul_dist
            soul_y = 50 + math.sin(soul_angle) * soul_dist
            fire_size = 4 + int(2 * pulse)
            pygame.draw.circle(s, (180, 180, 255), (int(soul_x), int(soul_y)), fire_size)
            pygame.draw.circle(s, (220, 220, 255), (int(soul_x), int(soul_y)), fire_size - 2)
        
        # 灵魂锁链缠绕
        chain_points = []
        for i in range(8):
            chain_angle = t * 4 + i * math.pi / 4
            cx = 60 + math.cos(chain_angle) * 30
            cy = 50 + math.sin(chain_angle) * 30
            chain_points.append((int(cx), int(cy)))
        
        for i in range(len(chain_points)):
            next_i = (i + 1) % len(chain_points)
            pygame.draw.line(s, (180, 180, 240), chain_points[i], chain_points[next_i], 1)
        return s

    elif model_style == "kaleidoscope":
        # 万花筒分形：镜像对称，钻石粒子，无限反射
        pygame.draw.circle(s, (240, 240, 240), (60, 50), 15)
        pygame.draw.circle(s, (255, 255, 255), (60, 50), 12)
        
        # 万花筒对称图案（6重对称）
        for sym in range(6):
            base_angle = t + sym * math.pi / 3
            
            for i in range(3):
                angle = base_angle + i * 0.3
                dist = 25 + i * 8
                mx = 60 + math.cos(angle) * dist
                my = 50 + math.sin(angle) * dist
                
                mirror_size = 8 - i * 2
                mirror_points = [
                    (mx, my - mirror_size),
                    (mx + mirror_size * 0.6, my),
                    (mx, my + mirror_size),
                    (mx - mirror_size * 0.6, my)
                ]
                
                hue = (sym * 60 + i * 30) % 360
                mirror_color = pygame.Color(0)
                mirror_color.hsva = (hue, 80, 100, 100)
                
                s_mirror = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.polygon(s_mirror, (*mirror_color[:3], 150), mirror_points)
                s.blit(s_mirror, (0, 0))
                pygame.draw.polygon(s, (255, 255, 255), mirror_points, 1)
        
        # 钻石粒子漩涡
        for i in range(16):
            diamond_angle = -t * 5 + i * math.pi / 8
            diamond_dist = 35 + 5 * math.sin(t * 8 + i)
            dx = 60 + math.cos(diamond_angle) * diamond_dist
            dy = 50 + math.sin(diamond_angle) * diamond_dist
            
            d_size = 3
            d_points = [(dx, dy - d_size), (dx + d_size, dy), (dx, dy + d_size), (dx - d_size, dy)]
            pygame.draw.polygon(s, (220, 220, 250), d_points)
        return s

    elif model_style == "eldritch_horror":
        # 深渊恐惧：扭曲触手，黑雾，恐惧之眼
        body_pulse = int(5 * pulse)
        pygame.draw.ellipse(s, (100, 0, 140), (40 - body_pulse, 30, 40 + body_pulse * 2, 50))
        pygame.draw.ellipse(s, (120, 0, 160), (45, 35, 30, 40))
        
        # 扭曲触手（8条）
        for i in range(8):
            tentacle_angle = t * 2 + i * math.pi / 4
            tentacle_length = 35 + 10 * math.sin(t * 5 + i)
            
            tentacle_segments = []
            for seg in range(5):
                seg_angle = tentacle_angle + seg * 0.2 * math.sin(t * 3)
                seg_dist = (seg + 1) * tentacle_length / 5
                tx = 60 + math.cos(seg_angle) * seg_dist
                ty = 50 + math.sin(seg_angle) * seg_dist
                tentacle_segments.append((int(tx), int(ty)))
            
            if len(tentacle_segments) > 1:
                pygame.draw.lines(s, (170, 0, 170), False, tentacle_segments, 3)
                pygame.draw.lines(s, (120, 0, 160), False, tentacle_segments, 1)
                end_x, end_y = tentacle_segments[-1]
                pygame.draw.circle(s, (100, 0, 140), (end_x, end_y), 4)
        
        # 黑雾弥漫效果
        for i in range(6):
            fog_x = 40 + random.randint(0, 40)
            fog_y = 30 + random.randint(0, 50)
            fog_size = random.randint(8, 15)
            s_fog = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(s_fog, (50, 0, 70, 40), (fog_x, fog_y), fog_size)
            s.blit(s_fog, (0, 0))
        
        # 恐惧之眼
        eye_positions = [(50, 40), (70, 40), (60, 55)]
        for ex, ey in eye_positions:
            pygame.draw.ellipse(s, (200, 180, 180), (ex - 5, ey - 3, 10, 6))
            pupil_offset = int(2 * math.sin(t * 4))
            pygame.draw.circle(s, (255, 0, 0), (ex + pupil_offset, ey), 2)
        return s

    elif model_style == "aurora_borealis":
        # 北极天幕：极光流光，彩色光带
        outline = [(60, 15), (80, 80), (60, 70), (40, 80)]
        
        aurora_colors = [
            (100, 255, 200),
            (150, 200, 255),
            (255, 100, 255),
            (100, 255, 255)
        ]
        
        for layer in range(4):
            aurora_points = []
            for i in range(10):
                x = 20 + i * 8
                y_offset = 10 * math.sin(t * 2 + i * 0.5 + layer)
                y = 40 + layer * 10 + y_offset
                aurora_points.append((x, y))
            
            if len(aurora_points) > 1:
                s_aurora = pygame.Surface((120, 120), pygame.SRCALPHA)
                for i in range(len(aurora_points) - 1):
                    pygame.draw.line(s_aurora, (*aurora_colors[layer], 100), 
                                   aurora_points[i], aurora_points[i + 1], 8)
                s.blit(s_aurora, (0, 0))
        
        s_body = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(s_body, (*c[:3], 150), outline)
        s.blit(s_body, (0, 0))
        
        for i in range(20):
            particle_angle = t * 3 + i * math.pi / 10
            particle_dist = 30 + 15 * math.sin(t * 4 + i)
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            p_color = aurora_colors[i % 4]
            pygame.draw.circle(s, p_color, (int(px), int(py)), 2)
        
        halo_alpha = 80 + int(40 * pulse)
        s_halo = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(s_halo, (150, 220, 255, halo_alpha), (60, 50), 40)
        s.blit(s_halo, (0, 0))
        return s

    elif model_style == "chronos":
        # 时间逆流者：沙漏纹理，时空波纹
        hourglass_top = [(40, 20), (80, 20), (60, 50)]
        hourglass_bottom = [(60, 50), (40, 80), (80, 80)]
        
        pygame.draw.polygon(s, (200, 180, 255), hourglass_top)
        pygame.draw.polygon(s, (220, 200, 240), hourglass_bottom)
        pygame.draw.polygon(s, edge_color, hourglass_top, 2)
        pygame.draw.polygon(s, edge_color, hourglass_bottom, 2)
        
        pygame.draw.circle(s, (255, 220, 200), (60, 50), 5)
        
        sand_y = 20 + int(30 * ((t * 2) % 1))
        for i in range(8):
            sand_x = 55 + random.randint(0, 10)
            pygame.draw.circle(s, (255, 220, 200), (sand_x, sand_y + i * 3), 1)
        
        for i in range(4):
            wave_phase = (t * 3 + i * 0.5) % 2
            wave_radius = int(20 + wave_phase * 25)
            wave_alpha = int(150 * (1 - wave_phase / 2))
            s_wave = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(s_wave, (220, 200, 240, wave_alpha), (60, 50), wave_radius, 2)
            s.blit(s_wave, (0, 0))
        
        for i in range(3):
            time_offset = i + 1
            past_alpha = 60 - i * 15
            past_y_offset = int(-15 * math.sin(t * 2 - time_offset))
            
            s_past = pygame.Surface((120, 120), pygame.SRCALPHA)
            past_top = [(p[0], p[1] + past_y_offset) for p in hourglass_top]
            past_bottom = [(p[0], p[1] + past_y_offset) for p in hourglass_bottom]
            pygame.draw.polygon(s_past, (200, 180, 255, past_alpha), past_top)
            pygame.draw.polygon(s_past, (220, 200, 240, past_alpha), past_bottom)
            s.blit(s_past, (0, 0))
        
        for i in range(12):
            clock_angle = i * math.pi / 6
            tick_x1 = 60 + math.cos(clock_angle) * 35
            tick_y1 = 50 + math.sin(clock_angle) * 35
            tick_x2 = 60 + math.cos(clock_angle) * 40
            tick_y2 = 50 + math.sin(clock_angle) * 40
            pygame.draw.line(s, (200, 180, 255), (tick_x1, tick_y1), (tick_x2, tick_y2), 1)
        return s

    elif model_style == "data_god":
        # 数据之神：代码矩阵构成，数据流瀑布
        matrix_chars = "01"
        font_size = 8
        
        for col in range(0, 120, 10):
            stream_height = random.randint(30, 80)
            stream_y = int((t * 50) % 120)
            for row in range(stream_height // font_size):
                char_y = (stream_y + row * font_size) % 120
                brightness = 255 - (row * 3)
                if brightness > 0:
                    pygame.draw.rect(s, (0, brightness, brightness // 2), 
                                   (col, char_y, font_size - 2, font_size - 2))
        
        code_shape = [(60, 15), (85, 80), (60, 70), (35, 80)]
        
        for i in range(20):
            code_x = 40 + random.randint(0, 40)
            code_y = 20 + random.randint(0, 60)
            pygame.draw.rect(s, (100, 255, 150), (code_x, code_y, 4, 6))
        
        pygame.draw.polygon(s, (0, 255, 50), code_shape, 2)
        
        for i in range(15):
            rain_angle = t * 4 + i * math.pi / 7.5
            rain_dist = 35 + 10 * math.sin(t * 5 + i)
            rain_x = 60 + math.cos(rain_angle) * rain_dist
            rain_y = 50 + math.sin(rain_angle) * rain_dist
            
            pygame.draw.rect(s, (0, 255, 50), (int(rain_x) - 2, int(rain_y) - 3, 4, 6))
            s_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(s_glow, (100, 255, 150, 100), (int(rain_x), int(rain_y)), 6)
            s.blit(s_glow, (0, 0))
        
        for i in range(6):
            line_angle = t * 3 + i * math.pi / 3
            lx = 60 + math.cos(line_angle) * 30
            ly = 50 + math.sin(line_angle) * 30
            pygame.draw.line(s, (30, 240, 70), (60, 50), (int(lx), int(ly)), 1)
        return s

    elif model_style == "phantom_void":
        # 虚空深渊
        for i in range(5):
            void_r = 40 - i * 7
            void_alpha = 40 + i * 30
            void_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(void_surf, (80, 0, 120, void_alpha), (60, 60), void_r)
            s.blit(void_surf, (0, 0))
        # 虚空粒子
        for i in range(12):
            p_angle = t * 3 + i * math.pi / 6
            p_dist = 30 + 10 * math.sin(t * 4 + i)
            px = 60 + math.cos(p_angle) * p_dist
            py = 60 + math.sin(p_angle) * p_dist
            pygame.draw.circle(s, (150, 50, 200), (int(px), int(py)), 2)
        return s

    elif model_style == "phantom_phase":
        # 相位穿梭
        for i in range(4):
            offset_x = int(20 * math.sin(t * 2 + i * math.pi / 2))
            alpha = 150 - i * 30
            phase_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(phase_surf, (*c[:3], alpha), 
                              [(60 + offset_x, 20), (80 + offset_x, 80), (60 + offset_x, 90), (40 + offset_x, 80)])
            s.blit(phase_surf, (0, 0))
        return s

    elif model_style == "phantom_assassin":
        # 刺客形态
        pygame.draw.polygon(s, (40, 0, 60), [(60, 10), (85, 85), (60, 100), (35, 85)])
        pygame.draw.polygon(s, c, [(60, 15), (80, 80), (60, 95), (40, 80)])
        # 暗影刀刃
        pygame.draw.line(s, (150, 100, 200), (35, 40), (15, 30), 3)
        pygame.draw.line(s, (150, 100, 200), (85, 40), (105, 30), 3)
        return s

    elif model_style == "phantom_mirage":
        # 幻影分身
        for i in range(5):
            mirage_offset = int(10 * math.sin(t * 3 + i))
            mirage_alpha = 120 - i * 20
            mirage_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(mirage_surf, (*c[:3], mirage_alpha),
                              [(60 + mirage_offset, 15), (80, 80), (60 + mirage_offset, 90), (40, 80)])
            s.blit(mirage_surf, (0, 0))
        return s

    elif model_style == "phantom_ex":
        # 虚影裂隙 - 多层空间扭曲，相位偏移
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 多层相位飞机（3层错位）
        for layer in range(3):
            offset_x = int(10 * math.sin(t * 2 + layer * 2))
            offset_y = layer * 5
            alpha = 180 - layer * 50
            
            layer_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            phantom_points = [(60 + offset_x, 15 + offset_y), (85 + offset_x, 50 + offset_y), (75 + offset_x, 85 + offset_y), (45 + offset_x, 85 + offset_y), (35 + offset_x, 50 + offset_y)]
            pygame.draw.polygon(layer_surf, (150, 0, 255, alpha), phantom_points)
            pygame.draw.polygon(layer_surf, (200, 100, 255, alpha), phantom_points, 2)
            s.blit(layer_surf, (0, 0))
        
        # 空间裂隙
        for i in range(8):
            angle = t * 3 + i * math.pi / 4
            dist = 35 + 5 * math.sin(t * 4 + i)
            px = 60 + math.cos(angle) * dist
            py = 50 + math.sin(angle) * dist
            pygame.draw.circle(s, (255, 0, 255), (int(px), int(py)), 3)
        
        return s

    elif model_style == "phantom_ex2":
        # 时间裂缝 - 时钟齿轮，时光倒流
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心时钟表盘
        pygame.draw.circle(s, (255, 215, 0), (60, 50), 20)
        pygame.draw.circle(s, (255, 240, 150), (60, 50), 20, 3)
        
        # 12个刻度
        for i in range(12):
            angle = i * math.pi / 6 - math.pi / 2
            x1 = 60 + math.cos(angle) * 16
            y1 = 50 + math.sin(angle) * 16
            x2 = 60 + math.cos(angle) * 20
            y2 = 50 + math.sin(angle) * 20
            pygame.draw.line(s, (200, 150, 0), (int(x1), int(y1)), (int(x2), int(y2)), 2)
        
        # 时针（逆时针旋转）
        hour_angle = -t * 0.5
        minute_angle = -t * 6
        pygame.draw.line(s, (150, 100, 0), (60, 50), 
                        (int(60 + math.cos(hour_angle) * 12), int(50 + math.sin(hour_angle) * 12)), 3)
        pygame.draw.line(s, (180, 130, 0), (60, 50),
                        (int(60 + math.cos(minute_angle) * 18), int(50 + math.sin(minute_angle) * 18)), 2)
        
        # 沙漏沙粒
        for i in range(15):
            sand_y = 30 + (t * 50 + i * 5) % 40
            sand_x = 55 + (i % 3) * 5
            pygame.draw.circle(s, (255, 230, 100), (sand_x, int(sand_y)), 2)
        
        return s

    elif model_style == "phantom_ex3":
        # 星云诞生 - 宇宙摇篮，恒星胚胎
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.5) * 0.2 + 1
        
        # 星云气体（大块半透明云团）
        for cloud in range(8):
            cloud_angle = t * 0.5 + cloud * math.pi / 4
            cloud_dist = 25 + 15 * math.sin(t * 2 + cloud)
            cloud_x = 60 + math.cos(cloud_angle) * cloud_dist
            cloud_y = 50 + math.sin(cloud_angle) * cloud_dist
            cloud_size = 20 + 10 * math.sin(t * 1.5 + cloud)
            
            # 渐变云团
            for layer in range(5, 0, -1):
                layer_radius = int(cloud_size * (layer / 5))
                layer_alpha = int(100 * (layer / 5))
                cloud_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(cloud_surf, (100, 150, 255, layer_alpha),
                                 (int(cloud_x), int(cloud_y)), layer_radius)
                s.blit(cloud_surf, (0, 0))
        
        # 恒星胚胎（明亮的原恒星）
        proto_stars = []
        for star in range(12):
            star_angle = t * 1.2 + star * 0.5
            star_dist = 15 + 25 * ((star % 3) / 3)
            star_x = 60 + math.cos(star_angle) * star_dist
            star_y = 50 + math.sin(star_angle) * star_dist
            proto_stars.append((star_x, star_y))
            
            # 原恒星核心
            star_brightness = int(200 + 55 * math.sin(t * 5 + star))
            for glow in range(4, 0, -1):
                glow_radius = int(6 * pulse * (glow / 4))
                glow_alpha = int(255 * (glow / 4))
                star_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(star_surf, (star_brightness, star_brightness + 30, 255, glow_alpha),
                                 (int(star_x), int(star_y)), glow_radius)
                s.blit(star_surf, (0, 0))
        
        # 星际尘埃（连接恒星的尘埃流）
        for i in range(len(proto_stars)):
            for j in range(i + 1, len(proto_stars)):
                if random.random() < 0.3:  # 随机连接
                    dust_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    # 尘埃流动
                    for seg in range(5):
                        seg_prog = seg / 5
                        sx = proto_stars[i][0] + (proto_stars[j][0] - proto_stars[i][0]) * seg_prog
                        sy = proto_stars[i][1] + (proto_stars[j][1] - proto_stars[i][1]) * seg_prog
                        # 波动
                        offset_x = math.sin(t * 3 + seg) * 5
                        offset_y = math.cos(t * 3 + seg) * 5
                        if seg < 4:
                            next_prog = (seg + 1) / 5
                            ex = proto_stars[i][0] + (proto_stars[j][0] - proto_stars[i][0]) * next_prog
                            ey = proto_stars[i][1] + (proto_stars[j][1] - proto_stars[i][1]) * next_prog
                            next_offset_x = math.sin(t * 3 + seg + 1) * 5
                            next_offset_y = math.cos(t * 3 + seg + 1) * 5
                            pygame.draw.line(dust_surf, (150, 200, 255, 120),
                                           (int(sx + offset_x), int(sy + offset_y)),
                                           (int(ex + next_offset_x), int(ey + next_offset_y)), 2)
                    s.blit(dust_surf, (0, 0))
        
        # 宇宙射线
        for ray in range(20):
            if (int(t * 10) + ray) % 5 < 2:
                ray_angle = t * 4 + ray * 0.3
                ray_start_dist = 10
                ray_end_dist = 50
                ray_sx = 60 + math.cos(ray_angle) * ray_start_dist
                ray_sy = 50 + math.sin(ray_angle) * ray_start_dist
                ray_ex = 60 + math.cos(ray_angle) * ray_end_dist
                ray_ey = 50 + math.sin(ray_angle) * ray_end_dist
                ray_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(ray_surf, (255, 255, 255, 200),
                               (int(ray_sx), int(ray_sy)), (int(ray_ex), int(ray_ey)), 1)
                s.blit(ray_surf, (0, 0))
        
        return s

    elif model_style == "phantom_ex4":
        # 彩虹漩涡 - 光谱风暴
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 旋转的七彩光柱
        color_segments = 7
        for segment in range(color_segments):
            # HSV色彩空间循环
            hue = (segment / color_segments + t * 0.5) % 1
            # HSV转RGB
            h = hue * 6
            c_val = 1
            x = 1 - abs(h % 2 - 1)
            if h < 1:
                r, g, b = c_val, x, 0
            elif h < 2:
                r, g, b = x, c_val, 0
            elif h < 3:
                r, g, b = 0, c_val, x
            elif h < 4:
                r, g, b = 0, x, c_val
            elif h < 5:
                r, g, b = x, 0, c_val
            else:
                r, g, b = c_val, 0, x
            
            color = (int(r * 255), int(g * 255), int(b * 255))
            
            # 螺旋光束
            spiral_turns = 3
            points = []
            for step in range(20):
                step_prog = step / 20
                spiral_angle = (segment / color_segments) * math.pi * 2 + step_prog * spiral_turns * math.pi * 2 + t * 2
                spiral_radius = 10 + step_prog * 40
                sx = 60 + math.cos(spiral_angle) * spiral_radius
                sy = 50 + math.sin(spiral_angle) * spiral_radius
                points.append((int(sx), int(sy)))
            
            # 绘制彩色螺旋
            if len(points) > 1:
                for i in range(len(points) - 1):
                    alpha = int(220 * (1 - i / len(points)))
                    spiral_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(spiral_surf, (*color, alpha), points[i], points[i + 1], 3)
                    s.blit(spiral_surf, (0, 0))
        
        # 色彩粒子漩涡
        for particle in range(30):
            p_angle = (particle / 30) * math.pi * 2 + t * 3
            p_dist = 15 + (particle % 10) * 3
            px = 60 + math.cos(p_angle) * p_dist
            py = 50 + math.sin(p_angle) * p_dist
            
            # 粒子颜色随位置变化
            particle_hue = ((particle / 30) + t * 0.5) % 1
            h = particle_hue * 6
            if h < 1:
                pr, pg, pb = 255, int(255 * (h % 1)), 0
            elif h < 2:
                pr, pg, pb = int(255 * (1 - h % 1)), 255, 0
            elif h < 3:
                pr, pg, pb = 0, 255, int(255 * (h % 1))
            elif h < 4:
                pr, pg, pb = 0, int(255 * (1 - h % 1)), 255
            elif h < 5:
                pr, pg, pb = int(255 * (h % 1)), 0, 255
            else:
                pr, pg, pb = 255, 0, int(255 * (1 - h % 1))
            
            pygame.draw.circle(s, (pr, pg, pb), (int(px), int(py)), 3)
        
        # 彩虹环（扩散波）
        for wave in range(4):
            wave_progress = (t * 2 + wave * 0.3) % 1
            wave_radius = int(20 + wave_progress * 40)
            wave_alpha = int(180 * (1 - wave_progress))
            
            if wave_alpha > 30:
                # 彩虹分段
                for arc_seg in range(12):
                    arc_hue = ((arc_seg / 12) + t * 0.3) % 1
                    h = arc_hue * 6
                    if h < 3:
                        ar = int(255 * max(0, 1 - abs(h - 1)))
                        ag = int(255 * max(0, 1 - abs(h - 2)))
                        ab = int(255 * max(0, 1 - abs(h)))
                    else:
                        ar = int(255 * max(0, 1 - abs(h - 5)))
                        ag = int(255 * max(0, 1 - abs(h - 6)))
                        ab = int(255 * max(0, 1 - abs(h - 4)))
                    
                    arc_start = arc_seg * math.pi / 6
                    arc_end = (arc_seg + 1) * math.pi / 6
                    arc_points = []
                    for arc_step in range(5):
                        arc_angle = arc_start + (arc_end - arc_start) * (arc_step / 4)
                        ax = 60 + math.cos(arc_angle) * wave_radius
                        ay = 50 + math.sin(arc_angle) * wave_radius
                        arc_points.append((int(ax), int(ay)))
                    
                    if len(arc_points) > 1:
                        wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                        pygame.draw.lines(wave_surf, (ar, ag, ab, wave_alpha), False, arc_points, 3)
                        s.blit(wave_surf, (0, 0))
        
        return s

    elif model_style == "phantom_ex5":
        # 表情包战士·颜文字
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        
        # 基础形状
        pygame.draw.circle(plane_surf, c, center, 45)
        pygame.draw.circle(plane_surf, edge_color, center, 45, 3)
        
        # 绘制表情（用简单图形模拟）
        for i in range(6):
            angle = t + i * 1.047
            radius = 25 + math.sin(t * 2 + i) * 8
            ex = center[0] + math.cos(angle) * radius
            ey = center[1] + math.sin(angle) * radius
            
            # 表情圆脸
            face_size = int(8 + abs(math.sin(t * 3 + i)) * 4)
            emoji_color = (255, int(200 + 55 * math.sin(t + i)), int(100 + 100 * math.cos(t + i)))
            pygame.draw.circle(plane_surf, emoji_color, (int(ex), int(ey)), face_size, 2)
            
            # 眼睛
            pygame.draw.circle(plane_surf, emoji_color, (int(ex - face_size//3), int(ey - face_size//4)), 2)
            pygame.draw.circle(plane_surf, emoji_color, (int(ex + face_size//3), int(ey - face_size//4)), 2)
            
            # 嘴巴（根据索引改变表情）
            if i % 3 == 0:  # 笑脸
                pygame.draw.arc(plane_surf, emoji_color, (ex - face_size//2, ey, face_size, face_size//2), 0, 3.14, 2)
            elif i % 3 == 1:  # 生气
                pygame.draw.line(plane_surf, emoji_color, (ex - face_size//2, ey + face_size//3), (ex + face_size//2, ey + face_size//3), 2)
            else:  # 惊讶
                pygame.draw.circle(plane_surf, emoji_color, (int(ex), int(ey + face_size//3)), face_size//4, 2)
        return plane_surf

    return None


# 涂装列表
PHANTOM_STYLES = [
    "void_walker", "multi_ghost", "kaleidoscope", "eldritch_horror",
    "aurora_borealis", "chronos", "data_god",
    "phantom_void", "phantom_phase", "phantom_assassin", "phantom_mirage",
    "phantom_ex", "phantom_ex2", "phantom_ex3", "phantom_ex4", "phantom_ex5"
]


def is_phantom_style(model_style):
    """检查是否是 Phantom 专属涂装"""
    return model_style in PHANTOM_STYLES
