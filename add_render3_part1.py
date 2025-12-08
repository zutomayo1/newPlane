# 为第三批16个超级创意涂装添加渲染代码

render_code = '''
    # ========== 第三批16个超级创意涂装（更丰富特效）==========
    elif model_style == "striker_ex3":
        # 次元裂缝 - 空间碎裂，现实崩坏
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
    
    elif model_style == "titan_ex3":
        # 符文巨像 - 古代守护者
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 巨像主体（巨大石块）
        golem_body = [(60, 20), (80, 35), (85, 60), (70, 80), (50, 80), (35, 60), (40, 35)]
        pygame.draw.polygon(s, (120, 90, 60), golem_body)
        pygame.draw.polygon(s, (150, 120, 80), golem_body, 4)
        
        # 古代符文（发光刻纹）
        runes = [
            # 符文位置和形状
            [(52, 30), (54, 28), (56, 30), (54, 32)],  # 额头符文
            [(48, 45), (50, 43), (52, 45), (50, 47)],  # 左眼符文
            [(68, 45), (70, 43), (72, 45), (70, 47)],  # 右眼符文
            [(55, 60), (60, 58), (65, 60), (60, 62)],  # 胸部符文
        ]
        
        for rune_idx, rune in enumerate(runes):
            rune_brightness = int(200 + 55 * math.sin(t * 4 + rune_idx))
            # 符文本体
            pygame.draw.polygon(s, (rune_brightness, 150, 50), rune)
            # 符文辉光
            for glow_layer in range(3):
                glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                glow_size = 8 + glow_layer * 4 + int(4 * pulse)
                center_x = sum(p[0] for p in rune) // len(rune)
                center_y = sum(p[1] for p in rune) // len(rune)
                glow_alpha = int(180 - glow_layer * 50)
                pygame.draw.circle(glow_surf, (rune_brightness, 150, 50, glow_alpha),
                                 (center_x, center_y), glow_size)
                s.blit(glow_surf, (0, 0))
        
        # 魔法阵环绕（3层旋转魔法阵）
        for circle in range(3):
            circle_radius = 30 + circle * 12
            circle_rotation = t * (1 + circle * 0.5)
            circle_alpha = int(200 - circle * 50)
            
            # 魔法阵圆环
            magic_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(magic_surf, (200, 150, 100, circle_alpha),
                             (60, 50), circle_radius, 2)
            
            # 魔法阵符号（6个）
            for symbol in range(6):
                symbol_angle = circle_rotation + symbol * math.pi / 3
                symbol_x = 60 + math.cos(symbol_angle) * circle_radius
                symbol_y = 50 + math.sin(symbol_angle) * circle_radius
                # 绘制符号（小三角形）
                symbol_points = []
                for i in range(3):
                    sp_angle = symbol_angle + i * 2 * math.pi / 3
                    sp_x = symbol_x + math.cos(sp_angle) * 4
                    sp_y = symbol_y + math.sin(sp_angle) * 4
                    symbol_points.append((int(sp_x), int(sp_y)))
                pygame.draw.polygon(magic_surf, (220, 180, 120, circle_alpha), symbol_points)
            
            s.blit(magic_surf, (0, 0))
        
        # 守护者能量护盾（六边形护盾）
        shield_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        shield_radius = 40 + int(5 * pulse)
        shield_points = []
        for i in range(6):
            shield_angle = t * 0.5 + i * math.pi / 3
            shield_x = 60 + math.cos(shield_angle) * shield_radius
            shield_y = 50 + math.sin(shield_angle) * shield_radius
            shield_points.append((int(shield_x), int(shield_y)))
        pygame.draw.polygon(shield_surf, (150, 200, 100, 100), shield_points)
        pygame.draw.polygon(shield_surf, (200, 250, 150, 200), shield_points, 3)
        s.blit(shield_surf, (0, 0))
        
        # 能量粒子流动
        for particle in range(20):
            particle_progress = (t * 2 + particle * 0.2) % 1
            particle_angle = particle * 0.3
            particle_dist = 20 + particle_progress * 30
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            particle_alpha = int(220 * (1 - particle_progress))
            pygame.draw.circle(s, (180, 150, 100, particle_alpha), (int(px), int(py)), 3)
        
        return s
    
    elif model_style == "thunderbird_ex3":
        # 雷霆瓦尔基里 - 战争天使
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 天使头部光环
        halo_radius = 25 + int(5 * pulse)
        halo_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(halo_surf, (255, 255, 200, 220), (60, 30), halo_radius, 3)
        # 光环光芒
        for ray in range(12):
            ray_angle = t * 2 + ray * math.pi / 6
            ray_inner_x = 60 + math.cos(ray_angle) * halo_radius
            ray_inner_y = 30 + math.sin(ray_angle) * halo_radius
            ray_outer_x = 60 + math.cos(ray_angle) * (halo_radius + 8)
            ray_outer_y = 30 + math.sin(ray_angle) * (halo_radius + 8)
            pygame.draw.line(halo_surf, (255, 255, 240, 200),
                           (int(ray_inner_x), int(ray_inner_y)),
                           (int(ray_outer_x), int(ray_outer_y)), 2)
        s.blit(halo_surf, (0, 0))
        
        # 天使身体（人形）
        pygame.draw.circle(s, (255, 255, 220), (60, 35), 8)  # 头
        body_points = [(60, 43), (55, 60), (53, 70), (60, 75), (67, 70), (65, 60)]
        pygame.draw.polygon(s, (255, 255, 240), body_points)
        
        # 雷电翅膀（6片羽翼）
        for wing_pair in range(3):
            wing_y_offset = 45 + wing_pair * 10
            wing_span = 35 - wing_pair * 5
            
            for side in [-1, 1]:
                # 羽翼主干
                wing_base_x = 60
                wing_tip_x = 60 + side * (wing_span + 10 * math.sin(t * 3 + wing_pair))
                wing_tip_y = wing_y_offset + 5 * math.sin(t * 2 + wing_pair)
                
                # 多层羽毛
                for feather in range(5):
                    feather_progress = feather / 5
                    fx = wing_base_x + (wing_tip_x - wing_base_x) * feather_progress
                    fy = wing_y_offset + (wing_tip_y - wing_y_offset) * feather_progress
                    feather_angle = side * (math.pi / 4 + feather * 0.2)
                    feather_length = 12 - feather * 1.5
                    
                    fex = fx + math.cos(feather_angle) * feather_length
                    fey = fy + math.sin(feather_angle) * feather_length
                    
                    # 羽毛带闪电效果
                    feather_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(feather_surf, (255, 255, 220, 230),
                                   (int(fx), int(fy)), (int(fex), int(fey)), 3)
                    # 闪电纹理
                    if (int(t * 10) + feather) % 3 == 0:
                        pygame.draw.line(feather_surf, (200, 200, 255, 255),
                                       (int(fx), int(fy)), (int(fex), int(fey)), 1)
                    s.blit(feather_surf, (0, 0))
        
        # 雷电战矛（斜握）
        spear_angle = math.pi / 4 + math.sin(t * 2) * 0.2
        spear_length = 40
        spear_x1 = 60
        spear_y1 = 55
        spear_x2 = spear_x1 + math.cos(spear_angle) * spear_length
        spear_y2 = spear_y1 + math.sin(spear_angle) * spear_length
        
        # 矛柄
        pygame.draw.line(s, (200, 200, 220), (spear_x1, spear_y1),
                       (int(spear_x2), int(spear_y2)), 4)
        # 矛尖
        spear_tip_points = [
            (spear_x2, spear_y2),
            (spear_x2 + math.cos(spear_angle + 0.3) * 10,
             spear_y2 + math.sin(spear_angle + 0.3) * 10),
            (spear_x2 + math.cos(spear_angle - 0.3) * 10,
             spear_y2 + math.sin(spear_angle - 0.3) * 10)
        ]
        pygame.draw.polygon(s, (255, 255, 255), [(int(p[0]), int(p[1])) for p in spear_tip_points])
        
        # 闪电环绕战矛
        for bolt in range(5):
            bolt_progress = (t * 3 + bolt * 0.4) % 1
            bolt_x = spear_x1 + (spear_x2 - spear_x1) * bolt_progress
            bolt_y = spear_y1 + (spear_y2 - spear_y1) * bolt_progress
            bolt_offset = math.sin(t * 6 + bolt) * 8
            bolt_ox = bolt_x + math.cos(spear_angle + math.pi / 2) * bolt_offset
            bolt_oy = bolt_y + math.sin(spear_angle + math.pi / 2) * bolt_offset
            bolt_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(bolt_surf, (220, 220, 255, 200),
                           (int(bolt_x), int(bolt_y)), (int(bolt_ox), int(bolt_oy)), 2)
            s.blit(bolt_surf, (0, 0))
        
        # 神圣光环效果
        for ring in range(3):
            ring_radius = 35 + ring * 15
            ring_alpha = int(150 - ring * 40)
            ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (255, 255, 240, ring_alpha), (60, 50), ring_radius, 2)
            s.blit(ring_surf, (0, 0))
        
        return s
    
    elif model_style == "viper_ex3":
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
'''

# 读取utils.py，找到第二批代码的末尾
with open('utils.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在 necro_ex2 的 return s 之后插入
insert_after = '''            s.blit(wave_surf, (0, 0))
        
        return s

    # 赛博朋克风格几何飞机'''

# 插入新代码
if insert_after in content:
    new_content = content.replace(insert_after, f'''            s.blit(wave_surf, (0, 0))
        
        return s
{render_code}
    # 赛博朋克风格几何飞机''')
    
    with open('utils.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('成功添加前6个超级创意涂装的渲染代码!')
else:
    print('未找到插入位置，请检查文件')
