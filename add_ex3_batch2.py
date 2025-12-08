# 添加viper_ex3 到 necro_ex3 的11个渲染代码

import re

renders_code = '''    elif model_style == "viper_ex3":
        # 毒液交响曲 - 剧毒旋律
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心毒液唱片（旋转）
        disc_rotation = t * 2
        disc_radius = 18
        pygame.draw.circle(s, (0, 200, 80), (60, 50), disc_radius)
        pygame.draw.circle(s, (0, 255, 100), (60, 50), disc_radius, 2)
        # 唱片纹路
        for groove in range(5):
            groove_radius = disc_radius - groove * 3
            pygame.draw.circle(s, (0, 150, 60), (60, 50), groove_radius, 1)
        
        # 音符形状飞舞（各种音乐符号）
        notes = []
        for note in range(16):
            note_angle = disc_rotation + note * math.pi / 8
            note_dist = 25 + 20 * ((note % 4) / 4)
            note_x = 60 + math.cos(note_angle) * note_dist
            note_y = 50 + math.sin(note_angle) * note_dist
            notes.append((note_x, note_y, note))
            
            # 绘制不同类型的音符
            note_type = note % 4
            if note_type == 0:  # 四分音符
                pygame.draw.circle(s, (100, 255, 150), (int(note_x), int(note_y)), 4)
                pygame.draw.line(s, (100, 255, 150), (int(note_x + 4), int(note_y)),
                               (int(note_x + 4), int(note_y - 12)), 2)
            elif note_type == 1:  # 八分音符
                pygame.draw.circle(s, (100, 255, 150), (int(note_x), int(note_y)), 3)
                pygame.draw.line(s, (100, 255, 150), (int(note_x + 3), int(note_y)),
                               (int(note_x + 3), int(note_y - 10)), 2)
                pygame.draw.circle(s, (100, 255, 150), (int(note_x + 8), int(note_y - 10)), 2)
            elif note_type == 2:  # 升调符号
                pygame.draw.line(s, (100, 255, 150), (int(note_x - 3), int(note_y - 6)),
                               (int(note_x - 3), int(note_y + 6)), 2)
                pygame.draw.line(s, (100, 255, 150), (int(note_x + 3), int(note_y - 6)),
                               (int(note_x + 3), int(note_y + 6)), 2)
            else:  # 降调符号
                pygame.draw.circle(s, (100, 255, 150), (int(note_x), int(note_y - 3)), 3)
                pygame.draw.circle(s, (100, 255, 150), (int(note_x), int(note_y + 3)), 3)
        
        # 毒液音波（同心圆波纹带毒液效果）
        for wave in range(6):
            wave_radius = (t * 60 + wave * 15) % 90
            wave_alpha = int(200 * (1 - wave_radius / 90))
            # 波纹不是完美圆形，有毒液扭曲
            wave_points = []
            for i in range(16):
                wave_angle = i * math.pi / 8
                distortion = 3 * math.sin(t * 4 + wave + i)
                wx = 60 + math.cos(wave_angle) * (wave_radius + distortion)
                wy = 50 + math.sin(wave_angle) * (wave_radius + distortion)
                wave_points.append((int(wx), int(wy)))
            
            wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            if len(wave_points) > 2:
                pygame.draw.polygon(wave_surf, (0, 255, 100, wave_alpha), wave_points, 3)
            s.blit(wave_surf, (0, 0))
        
        # 五线谱线条
        for staff_line in range(5):
            staff_y = 20 + staff_line * 8
            staff_alpha = int(150 + 100 * math.sin(t * 3 + staff_line))
            staff_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(staff_surf, (50, 255, 120, staff_alpha),
                           (10, staff_y), (110, staff_y), 1)
            s.blit(staff_surf, (0, 0))
        
        # 毒液飞溅粒子（跟随旋律）
        for splash in range(12):
            splash_angle = t * 4 + splash * 0.5
            splash_dist = 30 + 15 * math.sin(t * 2 + splash)
            splash_x = 60 + math.cos(splash_angle) * splash_dist
            splash_y = 50 + math.sin(splash_angle) * splash_dist
            splash_size = 3 + int(2 * math.sin(t * 6 + splash))
            pygame.draw.circle(s, (150, 255, 50), (int(splash_x), int(splash_y)), splash_size)
        
        return s
    
    elif model_style == "specter_ex3":
        # 量子幽灵 - 叠加态，多位置存在
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 量子叠加（同时在多个位置）
        superposition_count = 8
        for pos in range(superposition_count):
            # 概率幅度（位置的可能性）
            amplitude = 0.3 + 0.7 * ((math.sin(t * 3 + pos) + 1) / 2)
            alpha = int(200 * amplitude)
            
            # 位置偏移
            offset_angle = pos * 2 * math.pi / superposition_count
            offset_dist = 15 * math.sin(t * 2 + pos)
            pos_x = 60 + math.cos(offset_angle) * offset_dist
            pos_y = 50 + math.sin(offset_angle) * offset_dist
            
            # 绘制幽灵形态
            ghost_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 头部
            pygame.draw.circle(ghost_surf, (100, 255, 255, alpha), (int(pos_x), int(pos_y - 10)), 8)
            # 身体（飘渺状）
            body_points = [
                (pos_x, pos_y - 2),
                (pos_x - 8, pos_y + 10),
                (pos_x - 6, pos_y + 18),
                (pos_x + 6, pos_y + 18),
                (pos_x + 8, pos_y + 10)
            ]
            pygame.draw.polygon(ghost_surf, (100, 255, 255, alpha),
                              [(int(p[0]), int(p[1])) for p in body_points])
            s.blit(ghost_surf, (0, 0))
        
        # 量子纠缠线（连接不同位置）
        entangle_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(superposition_count):
            for j in range(i + 1, superposition_count):
                if random.random() < 0.4:
                    angle_i = i * 2 * math.pi / superposition_count
                    offset_i = 15 * math.sin(t * 2 + i)
                    pos_xi = 60 + math.cos(angle_i) * offset_i
                    pos_yi = 50 + math.sin(angle_i) * offset_i
                    
                    angle_j = j * 2 * math.pi / superposition_count
                    offset_j = 15 * math.sin(t * 2 + j)
                    pos_xj = 60 + math.cos(angle_j) * offset_j
                    pos_yj = 50 + math.sin(angle_j) * offset_j
                    
                    pygame.draw.line(entangle_surf, (150, 255, 255, 120),
                                   (int(pos_xi), int(pos_yi)), (int(pos_xj), int(pos_yj)), 1)
        s.blit(entangle_surf, (0, 0))
        
        # 波函数（概率密度云）
        for cloud_particle in range(40):
            cloud_angle = cloud_particle * 0.5
            cloud_dist = 10 + 35 * random.random()
            cloud_x = 60 + math.cos(cloud_angle) * cloud_dist
            cloud_y = 50 + math.sin(cloud_angle) * cloud_dist
            cloud_probability = 1 - (cloud_dist - 10) / 35
            cloud_alpha = int(180 * cloud_probability)
            cloud_size = 2 + int(3 * cloud_probability)
            if cloud_alpha > 30:
                pygame.draw.circle(s, (120, 255, 255, cloud_alpha),
                                 (int(cloud_x), int(cloud_y)), cloud_size)
        
        # 观测者效应（当观测时坍缩）
        collapse_progress = (math.sin(t * 1.5) + 1) / 2
        if collapse_progress > 0.7:  # 观测发生
            # 坍缩到中心位置
            collapse_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            collapse_intensity = int(255 * ((collapse_progress - 0.7) / 0.3))
            for ring in range(5):
                ring_radius = 45 - ring * 8 - int(collapse_progress * 10)
                ring_alpha = int(200 * (1 - ring / 5))
                pygame.draw.circle(collapse_surf, (100, 255, 255, ring_alpha),
                                 (60, 50), ring_radius, 2)
            s.blit(collapse_surf, (0, 0))
        
        # 量子涨落粒子
        for fluctuation in range(15):
            if (int(t * 20) + fluctuation) % 10 < 5:
                fluc_angle = fluctuation * 0.8
                fluc_dist = 20 + 25 * random.random()
                fluc_x = 60 + math.cos(fluc_angle) * fluc_dist
                fluc_y = 50 + math.sin(fluc_angle) * fluc_dist
                pygame.draw.circle(s, (200, 255, 255), (int(fluc_x), int(fluc_y)), 2)
        
        return s
    
    elif model_style == "aurora_ex3":
        # 北极光兽 - 极地守望
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.8) * 0.15 + 1
        
        # 狼形身体轮廓
        wolf_body = [
            (60, 35),  # 头部中心
            (50, 45), (45, 55),  # 前腿
            (48, 70), (52, 75),  # 前爪
            (60, 72), # 胸部
            (68, 75), (72, 70),  # 后腿
            (75, 55), (70, 45)  # 后躯
        ]
        pygame.draw.polygon(s, (180, 220, 255), wolf_body)
        pygame.draw.polygon(s, (200, 240, 255), wolf_body, 3)
        
        # 狼头（尖耳朵）
        # 左耳
        left_ear = [(53, 30), (50, 20), (57, 28)]
        pygame.draw.polygon(s, (180, 220, 255), left_ear)
        # 右耳
        right_ear = [(67, 30), (70, 20), (63, 28)]
        pygame.draw.polygon(s, (180, 220, 255), right_ear)
        # 狼嘴
        snout_points = [(60, 35), (55, 40), (60, 42), (65, 40)]
        pygame.draw.polygon(s, (200, 230, 255), snout_points)
        
        # 北极光毛发（流动的七彩光带）
        aurora_colors = [
            (0, 255, 150), (100, 255, 200), (150, 200, 255),
            (200, 150, 255), (255, 100, 200)
        ]
        
        for fur_layer in range(5):
            fur_y_offset = 40 + fur_layer * 8
            fur_wave = math.sin(t * 2 + fur_layer * 0.5) * 8
            color_idx = fur_layer % len(aurora_colors)
            aurora_color = aurora_colors[color_idx]
            
            # 流动的光带
            fur_points = []
            for seg in range(10):
                seg_x = 40 + seg * 4
                seg_y = fur_y_offset + math.sin(t * 3 + seg * 0.3 + fur_layer) * 5
                fur_points.append((int(seg_x), int(seg_y)))
            
            # 绘制光带
            if len(fur_points) > 1:
                fur_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                for i in range(len(fur_points) - 1):
                    alpha = int(180 - i * 15)
                    pygame.draw.line(fur_surf, (*aurora_color, alpha),
                                   fur_points[i], fur_points[i + 1], 3)
                s.blit(fur_surf, (0, 0))
        
        # 北极光尾巴（长长的光流尾巴）
        tail_segments = 12
        for tail_seg in range(tail_segments):
            tail_progress = tail_seg / tail_segments
            tail_x = 70 + tail_seg * 3
            tail_y = 50 + math.sin(t * 2.5 + tail_seg * 0.4) * 15
            tail_size = int(8 * (1 - tail_progress))
            tail_alpha = int(220 * (1 - tail_progress))
            color_idx = tail_seg % len(aurora_colors)
            tail_color = aurora_colors[color_idx]
            
            if tail_size > 0:
                tail_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(tail_surf, (*tail_color, tail_alpha),
                                 (int(tail_x), int(tail_y)), tail_size)
                s.blit(tail_surf, (0, 0))
        
        # 极光粒子环绕
        for aurora_particle in range(20):
            ap_angle = t * 2 + aurora_particle * 0.3
            ap_dist = 25 + 15 * math.sin(t * 3 + aurora_particle)
            ap_x = 60 + math.cos(ap_angle) * ap_dist
            ap_y = 50 + math.sin(ap_angle) * ap_dist
            color_idx = aurora_particle % len(aurora_colors)
            ap_color = aurora_colors[color_idx]
            pygame.draw.circle(s, ap_color, (int(ap_x), int(ap_y)), 3)
        
        # 冰晶效果
        for crystal in range(8):
            cx_angle = t * 1.5 + crystal * math.pi / 4
            cx_dist = 35
            cx_x = 60 + math.cos(cx_angle) * cx_dist
            cx_y = 50 + math.sin(cx_angle) * cx_dist
            # 六角冰晶
            crystal_points = []
            for i in range(6):
                cp_angle = cx_angle + i * math.pi / 3
                cp_x = cx_x + math.cos(cp_angle) * 4
                cp_y = cx_y + math.sin(cp_angle) * 4
                crystal_points.append((int(cp_x), int(cp_y)))
            pygame.draw.polygon(s, (200, 240, 255, 200), crystal_points)
        
        return s
    
    elif model_style == "crimson_ex3":
        # 恒星熔炉 - 核聚变
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.25 + 1
        
        # 核心反应堆（超亮中心）
        core_radius = int(12 * pulse)
        for core_layer in range(6, 0, -1):
            layer_radius = int(core_radius * (core_layer / 6))
            layer_brightness = int(255 * (core_layer / 6))
            layer_alpha = 255
            core_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 颜色从白到黄到红渐变
            if core_layer > 4:
                core_color = (255, 255, layer_brightness)
            elif core_layer > 2:
                core_color = (255, layer_brightness, 100)
            else:
                core_color = (255, 100, 50)
            pygame.draw.circle(core_surf, (*core_color, layer_alpha),
                             (60, 50), layer_radius)
            s.blit(core_surf, (0, 0))
        
        # 等离子体环流（旋转）
        plasma_rings = 4
        for ring in range(plasma_rings):
            ring_radius = 18 + ring * 8
            ring_rotation = t * (2 + ring * 0.3)
            ring_alpha = int(220 - ring * 40)
            
            # 不完整的圆环（模拟磁场线）
            for arc_seg in range(6):
                arc_start = ring_rotation + arc_seg * math.pi / 3
                arc_end = arc_start + math.pi / 4
                # 绘制弧段
                arc_points = []
                for arc_step in range(8):
                    arc_angle = arc_start + (arc_end - arc_start) * (arc_step / 8)
                    arc_x = 60 + math.cos(arc_angle) * ring_radius
                    arc_y = 50 + math.sin(arc_angle) * ring_radius
                    arc_points.append((int(arc_x), int(arc_y)))
                
                if len(arc_points) > 1:
                    plasma_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    for i in range(len(arc_points) - 1):
                        plasma_color = (255, 150 - ring * 30, 50)
                        pygame.draw.line(plasma_surf, (*plasma_color, ring_alpha),
                                       arc_points[i], arc_points[i + 1], 3)
                    s.blit(plasma_surf, (0, 0))
        
        # 太阳耀斑（喷射）
        flare_count = 8
        for flare in range(flare_count):
            flare_angle = t * 1.5 + flare * 2 * math.pi / flare_count
            flare_intensity = (math.sin(t * 4 + flare) + 1) / 2
            
            if flare_intensity > 0.5:  # 只在高强度时显示
                flare_length = 30 + 20 * flare_intensity
                flare_start_dist = 15
                flare_sx = 60 + math.cos(flare_angle) * flare_start_dist
                flare_sy = 50 + math.sin(flare_angle) * flare_start_dist
                flare_ex = 60 + math.cos(flare_angle) * flare_length
                flare_ey = 50 + math.sin(flare_angle) * flare_length
                
                # 多层耀斑
                for flare_layer in range(3):
                    flare_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    layer_offset = flare_layer * 2
                    layer_alpha = int(200 * flare_intensity - flare_layer * 50)
                    flare_color = (255, 200 - flare_layer * 50, 100)
                    
                    offset_angle = flare_angle + math.pi / 2
                    offset_x = math.cos(offset_angle) * layer_offset
                    offset_y = math.sin(offset_angle) * layer_offset
                    
                    pygame.draw.line(flare_surf, (*flare_color, layer_alpha),
                                   (int(flare_sx + offset_x), int(flare_sy + offset_y)),
                                   (int(flare_ex + offset_x), int(flare_ey + offset_y)), 4 - flare_layer)
                    s.blit(flare_surf, (0, 0))
        
        # 核反应粒子（高速喷射）
        for particle in range(30):
            particle_angle = particle * 0.4 + t * 5
            particle_progress = (t * 4 + particle * 0.1) % 1
            particle_dist = 10 + particle_progress * 45
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            particle_alpha = int(255 * (1 - particle_progress))
            particle_size = int(4 * (1 - particle_progress)) + 1
            
            if particle_alpha > 30:
                pygame.draw.circle(s, (255, 255, 200, particle_alpha),
                                 (int(px), int(py)), particle_size)
        
        # 热浪扭曲（环形热波）
        for heat_wave in range(3):
            wave_radius = (t * 50 + heat_wave * 25) % 75
            wave_alpha = int(150 * (1 - wave_radius / 75))
            wave_distortion = 5 * math.sin(t * 4 + heat_wave)
            
            wave_points = []
            for i in range(16):
                wave_angle = i * math.pi / 8
                distort = wave_distortion * math.sin(i)
                wx = 60 + math.cos(wave_angle) * (wave_radius + distort)
                wy = 50 + math.sin(wave_angle) * (wave_radius + distort)
                wave_points.append((int(wx), int(wy)))
            
            if len(wave_points) > 2:
                heat_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.polygon(heat_surf, (255, 150, 50, wave_alpha), wave_points, 2)
                s.blit(heat_surf, (0, 0))
        
        return s
    
    elif model_style == "stalker_ex3":
        # 纳米风暴 - 灰雾吞噬
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 纳米机器人云（密集小粒子）
        nano_particle_count = 80
        for nano in range(nano_particle_count):
            # 螺旋运动
            nano_angle = t * 3 + nano * 0.2
            nano_spiral_radius = 10 + (nano % 30)
            nano_height = math.sin(t * 2 + nano * 0.1) * 15
            nano_x = 60 + math.cos(nano_angle) * nano_spiral_radius
            nano_y = 50 + nano_height + (nano % 5) * 3 - 10
            
            # 纳米粒子大小和颜色变化
            nano_size = 1 + int((nano % 3))
            nano_brightness = 100 + int(155 * ((math.sin(t * 4 + nano) + 1) / 2))
            nano_alpha = 150 + int(100 * ((nano_spiral_radius - 10) / 30))
            
            pygame.draw.circle(s, (nano_brightness, nano_brightness, nano_brightness, nano_alpha),
                             (int(nano_x), int(nano_y)), nano_size)
        
        # 吞噬波纹（向内收缩）
        for devour_wave in range(5):
            wave_progress = (t * 2 + devour_wave * 0.4) % 1
            # 从外向内
            wave_radius = int(50 * (1 - wave_progress))
            wave_alpha = int(200 * wave_progress)
            
            if wave_radius > 5:
                devour_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(devour_surf, (80, 80, 80, wave_alpha),
                                 (60, 50), wave_radius, 2)
                s.blit(devour_surf, (0, 0))
        
        # 灰雾触手（从中心延伸）
        tentacle_count = 8
        for tentacle in range(tentacle_count):
            tentacle_angle = tentacle * 2 * math.pi / tentacle_count + t * 0.5
            tentacle_length = 35 + 10 * math.sin(t * 2 + tentacle)
            
            # 触手由多段组成
            tentacle_segments = 8
            tentacle_points = [(60, 50)]
            
            for seg in range(1, tentacle_segments + 1):
                seg_progress = seg / tentacle_segments
                seg_dist = tentacle_length * seg_progress
                # 触手摆动
                seg_offset = math.sin(t * 3 + seg * 0.5) * 8 * seg_progress
                seg_angle = tentacle_angle + seg_offset * 0.1
                
                seg_x = 60 + math.cos(seg_angle) * seg_dist
                seg_y = 50 + math.sin(seg_angle) * seg_dist
                tentacle_points.append((int(seg_x), int(seg_y)))
            
            # 绘制触手
            if len(tentacle_points) > 1:
                tentacle_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                for i in range(len(tentacle_points) - 1):
                    segment_alpha = int(180 * (1 - i / len(tentacle_points)))
                    segment_width = int(5 * (1 - i / len(tentacle_points))) + 1
                    pygame.draw.line(tentacle_surf, (100, 100, 100, segment_alpha),
                                   tentacle_points[i], tentacle_points[i + 1], segment_width)
                s.blit(tentacle_surf, (0, 0))
        
        # 被吞噬的碎片（向中心飞）
        for debris in range(15):
            debris_progress = (t * 2.5 + debris * 0.3) % 1
            debris_angle = debris * 0.8
            # 从外向内
            debris_dist = 50 * (1 - debris_progress)
            debris_x = 60 + math.cos(debris_angle) * debris_dist
            debris_y = 50 + math.sin(debris_angle) * debris_dist
            debris_alpha = int(255 * (1 - debris_progress))
            debris_size = 3 + int(3 * (1 - debris_progress))
            
            if debris_alpha > 30 and debris_dist > 5:
                debris_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                # 碎片形状（小方块）
                debris_rect = pygame.Rect(int(debris_x - debris_size / 2),
                                        int(debris_y - debris_size / 2),
                                        debris_size, debris_size)
                pygame.draw.rect(debris_surf, (150, 150, 150, debris_alpha), debris_rect)
                s.blit(debris_surf, (0, 0))
        
        # 中心吞噬核心
        core_pulse_radius = int(8 + 4 * pulse)
        for core_layer in range(4, 0, -1):
            layer_radius = int(core_pulse_radius * (core_layer / 4))
            layer_alpha = int(200 * (core_layer / 4))
            core_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(core_surf, (50, 50, 50, layer_alpha),
                             (60, 50), layer_radius)
            s.blit(core_surf, (0, 0))
        
        return s
'''

# 读取文件
with open('utils.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到插入位置 (在 thunderbird_ex3 的 return s 之后)
insert_marker = '''        return s


    # 赛博朋克风格几何飞机 - 13种机体差异化设计 + 动态特性'''

if insert_marker in content:
    new_content = content.replace(insert_marker, f'''        return s
{renders_code}

    # 赛博朋克风格几何飞机 - 13种机体差异化设计 + 动态特性''')
    
    with open('utils.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('成功添加 viper, specter, aurora, crimson, stalker 共5个渲染代码!')
else:
    print('未找到插入位置')
