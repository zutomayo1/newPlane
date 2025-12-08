# 批量添加16个新涂装的渲染代码到utils.py

render_codes = '''
    # ========== 第二批16个新专属涂装外形 ==========
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
    
    elif model_style == "titan_ex2":
        # 熔岩巨兽 - 岩浆裂纹，火山喷发
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.2 + 1
        
        # 巨兽身躯（岩石质感）
        body_rect = pygame.Rect(30, 20, 60, 60)
        pygame.draw.rect(s, (100, 50, 0), body_rect)
        pygame.draw.rect(s, (150, 80, 0), body_rect, 4)
        
        # 岩浆裂纹（发光）
        crack_lines = [
            [(40, 30), (50, 50), (45, 70)],
            [(70, 35), (60, 55), (65, 75)],
            [(50, 25), (55, 45), (60, 65)]
        ]
        for crack in crack_lines:
            for i in range(len(crack) - 1):
                pygame.draw.line(s, (255, 100, 0), crack[i], crack[i+1], 3)
                # 发光效果
                glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(glow_surf, (255, 150, 0, 180), crack[i], crack[i+1], 6)
                s.blit(glow_surf, (0, 0))
        
        # 火山喷发粒子
        for i in range(10):
            particle_angle = t * 3 + i * 0.6
            particle_dist = 15 + (t * 30 + i * 5) % 30
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 - particle_dist * 0.5
            pygame.draw.circle(s, (255, 120, 20), (int(px), int(py)), 4)
        
        return s
    
    elif model_style == "thunderbird_ex2":
        # 凤凰涅槃 - 火焰羽毛，浴火重生
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 凤凰头部
        pygame.draw.circle(s, (255, 50, 50), (60, 40), 12)
        pygame.draw.polygon(s, (255, 100, 0), [(60, 30), (55, 20), (65, 20)])  # 凤冠
        
        # 凤凰身体
        body_points = [(60, 52), (50, 65), (45, 75), (55, 80), (60, 85), (65, 80), (75, 75), (70, 65)]
        pygame.draw.polygon(s, (255, 80, 80), body_points)
        
        # 火焰翅膀（左右对称）
        for side in [-1, 1]:
            wing_base_x = 60 + side * 10
            for feather in range(5):
                feather_angle = side * (math.pi / 3 + feather * 0.3) + math.sin(t * 3 + feather) * 0.2
                feather_length = 25 + feather * 3
                fx = wing_base_x + math.cos(feather_angle) * feather_length
                fy = 55 + math.sin(feather_angle) * feather_length * 0.6
                # 羽毛（渐变火焰色）
                for seg in range(3):
                    seg_prog = seg / 3
                    color_r = 255
                    color_g = int(150 - seg_prog * 100)
                    sx = wing_base_x + math.cos(feather_angle) * feather_length * seg_prog
                    sy = 55 + math.sin(feather_angle) * feather_length * 0.6 * seg_prog
                    ex = wing_base_x + math.cos(feather_angle) * feather_length * (seg_prog + 0.33)
                    ey = 55 + math.sin(feather_angle) * feather_length * 0.6 * (seg_prog + 0.33)
                    pygame.draw.line(s, (color_r, color_g, 0), (int(sx), int(sy)), (int(ex), int(ey)), 4)
        
        # 涅槃光环
        for ring in range(3):
            ring_radius = 25 + ring * 12 + int(8 * pulse)
            ring_alpha = int(200 - ring * 60)
            ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (255, 100, 0, ring_alpha), (60, 50), ring_radius, 2)
            s.blit(ring_surf, (0, 0))
        
        return s
    
    elif model_style == "viper_ex2":
        # 深海巨鲸 - 鲸鱼形态，水波扩散
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 鲸鱼身体（流线型）
        whale_body = [(30, 50), (40, 40), (60, 35), (80, 40), (90, 50), (85, 60), (60, 65), (35, 60)]
        pygame.draw.polygon(s, (0, 100, 200), whale_body)
        pygame.draw.polygon(s, (0, 150, 255), whale_body, 3)
        
        # 鲸鱼眼睛
        pygame.draw.circle(s, (255, 255, 255), (70, 45), 4)
        pygame.draw.circle(s, (0, 0, 0), (71, 45), 2)
        
        # 锯齿背鳍
        for i in range(5):
            fin_x = 45 + i * 10
            fin_points = [(fin_x, 35), (fin_x - 3, 25), (fin_x + 3, 25)]
            pygame.draw.polygon(s, (0, 120, 220), fin_points)
        
        # 尾鳍（摆动）
        tail_swing = math.sin(t * 4) * 10
        tail_points = [(90, 50), (100 + tail_swing, 40), (105 + tail_swing, 50), (100 + tail_swing, 60)]
        pygame.draw.polygon(s, (0, 130, 230), tail_points)
        
        # 水波纹
        for ring in range(4):
            wave_radius = (t * 40 + ring * 20) % 80
            wave_alpha = int(180 * (1 - wave_radius / 80))
            wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surf, (100, 200, 255, wave_alpha), (60, 50), int(wave_radius), 2)
            s.blit(wave_surf, (0, 0))
        
        # 气泡上浮
        for i in range(10):
            bubble_y = 80 - (t * 40 + i * 8) % 60
            bubble_x = 50 + i * 3
            pygame.draw.circle(s, (150, 220, 255), (bubble_x, int(bubble_y)), 3)
        
        return s
    
    elif model_style == "specter_ex2":
        # 暗影刺客 - 双刀交叉，分身闪烁
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 刺客身影（模糊轮廓）
        for layer in range(3):
            offset = layer * 5
            alpha = 150 - layer * 40
            shadow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 头部
            pygame.draw.circle(shadow_surf, (50, 50, 100, alpha), (60 + offset, 35), 8)
            # 身体
            body_points = [(60 + offset, 43), (55 + offset, 60), (50 + offset, 75), (60 + offset, 70), (70 + offset, 75), (65 + offset, 60)]
            pygame.draw.polygon(shadow_surf, (50, 50, 100, alpha), body_points)
            s.blit(shadow_surf, (0, 0))
        
        # 双刀交叉
        blade_angle1 = math.pi / 4 + math.sin(t * 3) * 0.3
        blade_angle2 = -math.pi / 4 - math.sin(t * 3) * 0.3
        for blade_angle in [blade_angle1, blade_angle2]:
            blade_start_x = 60
            blade_start_y = 50
            blade_end_x = 60 + math.cos(blade_angle) * 35
            blade_end_y = 50 + math.sin(blade_angle) * 35
            pygame.draw.line(s, (100, 100, 150), (blade_start_x, blade_start_y), 
                           (int(blade_end_x), int(blade_end_y)), 4)
            pygame.draw.line(s, (150, 150, 200), (blade_start_x, blade_start_y),
                           (int(blade_end_x), int(blade_end_y)), 2)
        
        # 手里剑飞旋
        for i in range(4):
            shuriken_angle = t * 5 + i * math.pi / 2
            shuriken_dist = 30 + 10 * math.sin(t * 2 + i)
            sx = 60 + math.cos(shuriken_angle) * shuriken_dist
            sy = 50 + math.sin(shuriken_angle) * shuriken_dist
            # 四角星形
            star_points = []
            for j in range(8):
                star_angle = shuriken_angle + j * math.pi / 4
                star_radius = 5 if j % 2 == 0 else 3
                star_points.append((int(sx + math.cos(star_angle) * star_radius),
                                  int(sy + math.sin(star_angle) * star_radius)))
            pygame.draw.polygon(s, (80, 80, 130), star_points)
        
        return s
    
    elif model_style == "aurora_ex2":
        # 冰霜精灵 - 冰晶翅膀，雪花飘落
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 精灵身体（冰晶人形）
        pygame.draw.circle(s, (180, 230, 255), (60, 40), 10)  # 头
        body_points = [(60, 50), (55, 65), (53, 75), (60, 80), (67, 75), (65, 65)]
        pygame.draw.polygon(s, (150, 220, 255), body_points)
        
        # 冰晶翅膀（6片）
        for wing_idx in range(6):
            wing_angle = wing_idx * math.pi / 3 + t * 0.5
            wing_length = 25 + 8 * math.sin(t * 2 + wing_idx)
            # 翅膀主干
            wx = 60 + math.cos(wing_angle) * wing_length
            wy = 50 + math.sin(wing_angle) * wing_length
            pygame.draw.line(s, (200, 240, 255), (60, 50), (int(wx), int(wy)), 3)
            # 冰晶分支
            for branch in range(3):
                branch_angle = wing_angle + (branch - 1) * 0.4
                branch_dist = wing_length * 0.6
                bx = 60 + math.cos(branch_angle) * branch_dist
                by = 50 + math.sin(branch_angle) * branch_dist
                pygame.draw.line(s, (180, 230, 255), (int(wx), int(wy)), (int(bx), int(by)), 2)
        
        # 雪花飘落
        for i in range(20):
            snow_y = (t * 40 + i * 10) % 120
            snow_x = 30 + (i * 4) % 60 + math.sin(t * 2 + i) * 10
            # 六角雪花
            for j in range(6):
                sf_angle = j * math.pi / 3
                sf_x1 = snow_x + math.cos(sf_angle) * 3
                sf_y1 = snow_y + math.sin(sf_angle) * 3
                pygame.draw.line(s, (255, 255, 255), (int(snow_x), int(snow_y)), 
                               (int(sf_x1), int(sf_y1)), 1)
        
        # 冰封光环
        for ring in range(3):
            ice_radius = 20 + ring * 12
            ice_alpha = int(180 - ring * 50)
            ice_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(ice_surf, (180, 230, 255, ice_alpha), (60, 50), ice_radius, 2)
            s.blit(ice_surf, (0, 0))
        
        return s
    
    elif model_style == "crimson_ex2":
        # 爆炸之星（超新星） - 星体爆发，能量释放
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.25 + 1
        
        # 超新星核心（极亮）
        for layer in range(6, 0, -1):
            core_radius = int(18 * pulse * (layer / 6))
            core_alpha = int(255 * (layer / 6))
            core_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(core_surf, (255, 255, 200, core_alpha), (60, 50), core_radius)
            s.blit(core_surf, (0, 0))
        
        # 爆炸冲击波（多层扩散）
        for wave in range(5):
            wave_radius = (t * 80 + wave * 20) % 100
            wave_alpha = int(200 * (1 - wave_radius / 100))
            wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surf, (255, 255, 150, wave_alpha), (60, 50), int(wave_radius), 4)
            s.blit(wave_surf, (0, 0))
        
        # 星云碎片飞溅（24个方向）
        for i in range(24):
            fragment_angle = i * math.pi / 12
            fragment_dist = 20 + (t * 60 + i * 5) % 50
            fx = 60 + math.cos(fragment_angle) * fragment_dist
            fy = 50 + math.sin(fragment_angle) * fragment_dist
            fragment_size = 6 - int(fragment_dist / 15)
            if fragment_size > 1:
                pygame.draw.circle(s, (255, 255, 100), (int(fx), int(fy)), fragment_size)
        
        # 能量射线
        for ray in range(12):
            ray_angle = ray * math.pi / 6 + t
            ray_length = 30 + 15 * math.sin(t * 2 + ray)
            rx = 60 + math.cos(ray_angle) * ray_length
            ry = 50 + math.sin(ray_angle) * ray_length
            ray_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(ray_surf, (255, 255, 200, 200), (60, 50), (int(rx), int(ry)), 3)
            s.blit(ray_surf, (0, 0))
        
        return s
    
    elif model_style == "stalker_ex2":
        # 机械蜘蛛 - 8条机械腿，纳米虫群
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 蜘蛛主体（机械球体）
        pygame.draw.circle(s, (150, 150, 150), (60, 50), int(15 * pulse))
        pygame.draw.circle(s, (200, 200, 200), (60, 50), int(15 * pulse), 2)
        
        # 电子复眼（多个镜头）
        for eye_idx in range(6):
            eye_angle = eye_idx * math.pi / 3
            eye_x = 60 + math.cos(eye_angle) * 8
            eye_y = 50 + math.sin(eye_angle) * 8
            eye_brightness = int(155 + 100 * math.sin(t * 8 + eye_idx))
            pygame.draw.circle(s, (eye_brightness, 0, 0), (int(eye_x), int(eye_y)), 3)
        
        # 8条机械腿
        for leg_idx in range(8):
            leg_angle = leg_idx * math.pi / 4
            # 腿部关节动画
            leg_bend = math.sin(t * 4 + leg_idx) * 0.3
            
            # 第一节
            joint1_x = 60 + math.cos(leg_angle) * 18
            joint1_y = 50 + math.sin(leg_angle) * 18
            pygame.draw.line(s, (180, 180, 180), (60, 50), (int(joint1_x), int(joint1_y)), 4)
            
            # 第二节
            joint2_angle = leg_angle + leg_bend
            joint2_x = joint1_x + math.cos(joint2_angle) * 15
            joint2_y = joint1_y + math.sin(joint2_angle) * 15
            pygame.draw.line(s, (160, 160, 160), (int(joint1_x), int(joint1_y)), 
                           (int(joint2_x), int(joint2_y)), 3)
            
            # 第三节（末端）
            joint3_angle = joint2_angle - leg_bend * 0.5
            joint3_x = joint2_x + math.cos(joint3_angle) * 10
            joint3_y = joint2_y + math.sin(joint3_angle) * 10
            pygame.draw.line(s, (140, 140, 140), (int(joint2_x), int(joint2_y)),
                           (int(joint3_x), int(joint3_y)), 2)
        
        # 纳米虫群（小型飞行机器人）
        for nano_idx in range(20):
            nano_angle = t * 3 + nano_idx * 0.3
            nano_dist = 30 + 15 * math.sin(t * 2 + nano_idx)
            nx = 60 + math.cos(nano_angle) * nano_dist
            ny = 50 + math.sin(nano_angle) * nano_dist
            pygame.draw.rect(s, (220, 220, 220), (int(nx)-2, int(ny)-2, 4, 4))
        
        return s
    
    elif model_style == "gaia_ex2":
        # 樱花树灵 - 樱花树形态，花瓣飘落
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 树干
        trunk_rect = pygame.Rect(52, 40, 16, 45)
        pygame.draw.rect(s, (120, 80, 60), trunk_rect)
        pygame.draw.rect(s, (150, 100, 80), trunk_rect, 2)
        
        # 树枝（摇曳）
        for branch_idx in range(5):
            branch_angle = (branch_idx - 2) * 0.4 + math.sin(t * 2 + branch_idx) * 0.2
            branch_length = 20 + branch_idx * 3
            bx = 60 + math.cos(branch_angle) * branch_length
            by = 45 + branch_idx * 5
            pygame.draw.line(s, (140, 90, 70), (60, int(by)), (int(bx), int(by)), 3)
            
            # 樱花簇
            for flower in range(3):
                flower_angle = branch_angle + (flower - 1) * 0.3
                flower_dist = branch_length * 0.7
                fx = 60 + math.cos(flower_angle) * flower_dist
                fy = by
                pygame.draw.circle(s, (255, 180, 200), (int(fx), int(fy)), 5)
        
        # 樱花花瓣飘落（大量）
        for petal_idx in range(30):
            petal_y = (t * 30 + petal_idx * 8) % 120
            petal_x = 40 + (petal_idx * 3) % 40 + math.sin(t * 3 + petal_idx) * 15
            petal_rotation = t * 2 + petal_idx
            # 花瓣形状（椭圆）
            petal_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            petal_points = []
            for i in range(8):
                pa = i * math.pi / 4 + petal_rotation
                px = petal_x + math.cos(pa) * (4 if i % 2 == 0 else 2)
                py = petal_y + math.sin(pa) * (6 if i % 2 == 0 else 3)
                petal_points.append((int(px), int(py)))
            pygame.draw.polygon(petal_surf, (255, 150, 180, 220), petal_points)
            s.blit(petal_surf, (0, 0))
        
        # 春意光环
        for ring in range(3):
            spring_radius = 25 + ring * 12
            spring_alpha = int(180 - ring * 50)
            spring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(spring_surf, (255, 200, 220, spring_alpha), (60, 60), spring_radius, 2)
            s.blit(spring_surf, (0, 0))
        
        return s
    
    elif model_style == "weaver_ex2":
        # DNA螺旋 - 双螺旋结构，碱基对连接
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 双螺旋主链
        helix_points_1 = []
        helix_points_2 = []
        for i in range(20):
            y = 20 + i * 4
            angle1 = t * 2 + i * 0.4
            angle2 = angle1 + math.pi
            x1 = 60 + math.cos(angle1) * 20
            x2 = 60 + math.cos(angle2) * 20
            helix_points_1.append((int(x1), y))
            helix_points_2.append((int(x2), y))
        
        # 绘制螺旋线
        pygame.draw.lines(s, (0, 255, 150), False, helix_points_1, 3)
        pygame.draw.lines(s, (100, 255, 200), False, helix_points_2, 3)
        
        # 碱基对连接（横杠）
        for i in range(0, len(helix_points_1), 2):
            # 闪烁效果
            if (int(t * 10) + i) % 4 < 3:
                pygame.draw.line(s, (50, 255, 180), helix_points_1[i], helix_points_2[i], 2)
                # 碱基节点
                pygame.draw.circle(s, (0, 255, 150), helix_points_1[i], 4)
                pygame.draw.circle(s, (100, 255, 200), helix_points_2[i], 4)
        
        # 基因序列流动（发光粒子）
        for particle_idx in range(15):
            particle_progress = (t * 2 + particle_idx * 0.3) % 1
            particle_i = int(particle_progress * (len(helix_points_1) - 1))
            if particle_i < len(helix_points_1):
                px, py = helix_points_1[particle_i]
                particle_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, (200, 255, 200, 220), (px, py), 6)
                s.blit(particle_surf, (0, 0))
        
        return s
    
    elif model_style == "solar_ex2":
        # 雷电之神（宙斯） - 雷神锤，闪电链条
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 雷神锤头（巨大方锤）
        hammer_head = pygame.Rect(35, 30, 50, 30)
        pygame.draw.rect(s, (150, 150, 150), hammer_head)
        pygame.draw.rect(s, (200, 200, 200), hammer_head, 3)
        # 锤面雕刻（闪电纹）
        pygame.draw.line(s, (100, 100, 255), (40, 35), (50, 55), 2)
        pygame.draw.line(s, (100, 100, 255), (50, 55), (45, 55), 2)
        pygame.draw.line(s, (100, 100, 255), (70, 35), (75, 55), 2)
        pygame.draw.line(s, (100, 100, 255), (75, 55), (80, 55), 2)
        
        # 锤柄
        pygame.draw.rect(s, (100, 80, 60), (55, 60, 10, 30))
        
        # 闪电链条缠绕（4条）
        for chain_idx in range(4):
            chain_angle = chain_idx * math.pi / 2 + t * 2
            chain_dist = 30 + 10 * math.sin(t * 3 + chain_idx)
            cx = 60 + math.cos(chain_angle) * chain_dist
            cy = 45 + math.sin(chain_angle) * chain_dist
            # 闪电链条
            pygame.draw.line(s, (200, 200, 255), (60, 45), (int(cx), int(cy)), 3)
            # 链条末端电球
            ball_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(ball_surf, (220, 220, 255, 220), (int(cx), int(cy)), 6)
            s.blit(ball_surf, (0, 0))
        
        # 雷云环绕
        for cloud_idx in range(8):
            cloud_angle = t + cloud_idx * math.pi / 4
            cloud_dist = 35 + 8 * math.sin(t * 2 + cloud_idx)
            cloud_x = 60 + math.cos(cloud_angle) * cloud_dist
            cloud_y = 45 + math.sin(cloud_angle) * cloud_dist
            pygame.draw.circle(s, (100, 100, 150), (int(cloud_x), int(cloud_y)), 5)
        
        # 天降神雷（随机闪电）
        if int(t * 10) % 3 == 0:
            for bolt in range(3):
                bolt_x = 40 + bolt * 20
                bolt_points = [(bolt_x, 10)]
                for seg in range(5):
                    bolt_y = 10 + seg * 15
                    bolt_x += random.choice([-5, 0, 5])
                    bolt_points.append((bolt_x, bolt_y))
                pygame.draw.lines(s, (255, 255, 255), False, bolt_points, 2)
        
        return s
    
    elif model_style == "arbiter_ex2":
        # 正义天秤 - 天秤平衡，律法之眼
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 天秤横杆
        pygame.draw.line(s, (255, 215, 0), (30, 40), (90, 40), 4)
        pygame.draw.circle(s, (255, 240, 100), (60, 40), 8)
        
        # 天秤支撑柱
        pygame.draw.line(s, (255, 215, 0), (60, 40), (60, 60), 4)
        
        # 左右秤盘（轻微倾斜表示审判）
        tilt = math.sin(t * 1.5) * 5
        # 左秤盘
        left_pan_y = 55 + tilt
        pygame.draw.line(s, (255, 230, 50), (30, 40), (35, int(left_pan_y)), 2)
        pygame.draw.ellipse(s, (255, 240, 100), (25, int(left_pan_y), 20, 8))
        # 右秤盘
        right_pan_y = 55 - tilt
        pygame.draw.line(s, (255, 230, 50), (90, 40), (85, int(right_pan_y)), 2)
        pygame.draw.ellipse(s, (255, 240, 100), (75, int(right_pan_y), 20, 8))
        
        # 律法之眼（悬浮在上方）
        eye_y = 25 + math.sin(t * 2) * 3
        pygame.draw.ellipse(s, (255, 215, 0), (50, int(eye_y), 20, 12))
        pygame.draw.circle(s, (255, 240, 100), (60, int(eye_y + 6)), 6)
        pygame.draw.circle(s, (100, 80, 0), (60, int(eye_y + 6)), 3)
        # 眼睛光芒
        eye_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(eye_surf, (255, 240, 100, 180), (60, int(eye_y + 6)), int(10 * pulse))
        s.blit(eye_surf, (0, 0))
        
        # 正义光柱（从眼睛向下）
        for beam in range(3):
            beam_x = 58 + beam
            pygame.draw.line(s, (255, 240, 100, 150), (beam_x, int(eye_y + 12)), (beam_x, 120), 2)
        
        # 审判之剑（悬浮在天秤上方）
        sword_x = 60 + math.sin(t * 2) * 10
        sword_points = [(sword_x, 15), (sword_x - 3, 25), (sword_x + 3, 25)]
        pygame.draw.polygon(s, (255, 215, 0), [(int(p[0]), p[1]) for p in sword_points])
        pygame.draw.line(s, (255, 230, 50), (int(sword_x), 25), (int(sword_x), 35), 3)
        
        return s
    
    elif model_style == "eclipse_ex2":
        # 星系吞噬者 - 黑洞巨口，引力波扭曲
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.25 + 1
        
        # 黑洞核心（绝对黑暗）
        pygame.draw.circle(s, (0, 0, 0), (60, 50), 22)
        
        # 事件视界（紫色边缘）
        for layer in range(4):
            horizon_radius = 22 + layer * 4
            horizon_alpha = int(220 - layer * 50)
            horizon_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(horizon_surf, (100, 0, 150, horizon_alpha), (60, 50), horizon_radius, 3)
            s.blit(horizon_surf, (0, 0))
        
        # 吞噬的星系（螺旋吸入）
        for arm in range(4):
            arm_offset = arm * math.pi / 2
            for star_idx in range(30):
                spiral_progress = star_idx / 30
                spiral_angle = t * 2 + spiral_progress * math.pi * 6 + arm_offset
                spiral_dist = 60 - spiral_progress * 40
                if spiral_dist > 22:  # 不进入事件视界
                    sx = 60 + math.cos(spiral_angle) * spiral_dist
                    sy = 50 + math.sin(spiral_angle) * spiral_dist
                    star_size = int(4 * (1 - spiral_progress))
                    if star_size > 0:
                        star_brightness = int(255 * (1 - spiral_progress * 0.7))
                        pygame.draw.circle(s, (star_brightness, star_brightness // 2, star_brightness), 
                                         (int(sx), int(sy)), star_size)
        
        # 引力波扭曲（同心圆波纹）
        for wave in range(6):
            wave_radius = (t * 60 + wave * 20) % 120
            if wave_radius > 25:  # 从事件视界外开始
                wave_alpha = int(150 * (1 - (wave_radius - 25) / 95))
                wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                # 扭曲效果（椭圆变形）
                distortion = 1 + 0.3 * math.sin(t * 3 + wave)
                pygame.draw.ellipse(wave_surf, (150, 50, 200, wave_alpha),
                                  (60 - wave_radius, int(50 - wave_radius * distortion),
                                   wave_radius * 2, int(wave_radius * 2 * distortion)), 2)
                s.blit(wave_surf, (0, 0))
        
        # 宇宙坍缩粒子
        for particle in range(25):
            particle_progress = ((t * 3 + particle * 0.2) % 1)
            particle_angle = particle * 0.8
            particle_dist = 60 - particle_progress * 38
            if particle_dist > 22:
                px = 60 + math.cos(particle_angle) * particle_dist
                py = 50 + math.sin(particle_angle) * particle_dist
                particle_alpha = int(220 * (1 - particle_progress))
                pygame.draw.circle(s, (120, 20, 180, particle_alpha), (int(px), int(py)), 3)
        
        return s
    
    elif model_style == "prism_ex2":
        # 万花筒 - 对称图案，镜像反射
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心万花筒核心
        pygame.draw.circle(s, (255, 100, 255), (60, 50), int(12 * pulse))
        
        # 6重对称图案
        for symmetry in range(6):
            base_angle = symmetry * math.pi / 3 + t * 0.5
            
            # 每个对称区域绘制复杂图案
            for pattern in range(5):
                pattern_dist = 15 + pattern * 8
                pattern_angle = base_angle + pattern * 0.3
                
                # 彩色图案块
                hue = (t * 50 + symmetry * 60 + pattern * 30) % 360
                color_r = int(127 + 127 * math.sin(math.radians(hue)))
                color_g = int(127 + 127 * math.sin(math.radians(hue + 120)))
                color_b = int(127 + 127 * math.sin(math.radians(hue + 240)))
                
                # 主图形
                px = 60 + math.cos(pattern_angle) * pattern_dist
                py = 50 + math.sin(pattern_angle) * pattern_dist
                
                # 绘制小多边形
                poly_points = []
                for i in range(6):
                    poly_angle = pattern_angle + i * math.pi / 3
                    poly_radius = 5 + 2 * math.sin(t * 3 + pattern)
                    poly_x = px + math.cos(poly_angle) * poly_radius
                    poly_y = py + math.sin(poly_angle) * poly_radius
                    poly_points.append((int(poly_x), int(poly_y)))
                pygame.draw.polygon(s, (color_r, color_g, color_b), poly_points)
                
                # 镜像反射（另一侧）
                mirror_angle = base_angle - pattern * 0.3
                mirror_px = 60 + math.cos(mirror_angle) * pattern_dist
                mirror_py = 50 + math.sin(mirror_angle) * pattern_dist
                mirror_poly_points = []
                for i in range(6):
                    mirror_poly_angle = mirror_angle + i * math.pi / 3
                    mirror_poly_radius = 5 + 2 * math.sin(t * 3 + pattern)
                    mirror_poly_x = mirror_px + math.cos(mirror_poly_angle) * mirror_poly_radius
                    mirror_poly_y = mirror_py + math.sin(mirror_poly_angle) * mirror_poly_radius
                    mirror_poly_points.append((int(mirror_poly_x), int(mirror_poly_y)))
                pygame.draw.polygon(s, (color_r, color_g, color_b), mirror_poly_points)
        
        # 迷幻光线
        for ray in range(12):
            ray_angle = ray * math.pi / 6 + t * 2
            ray_length = 25 + 15 * math.sin(t * 3 + ray)
            rx = 60 + math.cos(ray_angle) * ray_length
            ry = 50 + math.sin(ray_angle) * ray_length
            ray_hue = (t * 100 + ray * 30) % 360
            ray_r = int(127 + 127 * math.sin(math.radians(ray_hue)))
            ray_g = int(127 + 127 * math.sin(math.radians(ray_hue + 120)))
            ray_b = int(127 + 127 * math.sin(math.radians(ray_hue + 240)))
            ray_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(ray_surf, (ray_r, ray_g, ray_b, 180), (60, 50), (int(rx), int(ry)), 2)
            s.blit(ray_surf, (0, 0))
        
        return s
    
    elif model_style == "necro_ex2":
        # 虚无教主 - 万物归墟，存在湮灭
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.2 + 1
        
        # 虚无核心（纯黑但带紫色边缘）
        pygame.draw.circle(s, (0, 0, 0), (60, 50), int(20 * pulse))
        for layer in range(3):
            void_radius = int(20 * pulse) + layer * 5
            void_alpha = int(150 - layer * 40)
            void_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(void_surf, (50, 0, 50, void_alpha), (60, 50), void_radius, 2)
            s.blit(void_surf, (0, 0))
        
        # 存在消散（粒子被吸入虚无）
        for particle in range(30):
            particle_progress = ((t * 2 + particle * 0.15) % 1)
            particle_angle = particle * 0.7
            particle_dist = 60 - particle_progress * 40
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            # 粒子逐渐消失
            particle_alpha = int(220 * (1 - particle_progress))
            particle_size = int(5 * (1 - particle_progress * 0.7))
            if particle_size > 0 and particle_alpha > 0:
                particle_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, (50, 50, 50, particle_alpha), 
                                 (int(px), int(py)), particle_size)
                s.blit(particle_surf, (0, 0))
        
        # 终焉之书（漂浮的黑色书页）
        for page in range(4):
            page_angle = t + page * math.pi / 2
            page_dist = 35 + 10 * math.sin(t * 2 + page)
            page_x = 60 + math.cos(page_angle) * page_dist
            page_y = 50 + math.sin(page_angle) * page_dist
            # 书页（矩形）
            page_rotation = math.sin(t * 3 + page) * 0.3
            page_points = []
            for corner in range(4):
                corner_angle = page_angle + corner * math.pi / 2 + page_rotation
                corner_dist = 8
                cx = page_x + math.cos(corner_angle) * corner_dist
                cy = page_y + math.sin(corner_angle) * corner_dist * 0.7
                page_points.append((int(cx), int(cy)))
            pygame.draw.polygon(s, (20, 20, 20), page_points)
            pygame.draw.polygon(s, (50, 50, 50), page_points, 1)
            # 书页上的符文
            pygame.draw.line(s, (80, 80, 80), (int(page_x - 5), int(page_y)), 
                           (int(page_x + 5), int(page_y)), 1)
        
        # 湮灭波动
        for wave in range(4):
            wave_radius = (t * 50 + wave * 25) % 100
            wave_alpha = int(180 * (1 - wave_radius / 100))
            wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surf, (20, 20, 20, wave_alpha), (60, 50), int(wave_radius), 2)
            s.blit(wave_surf, (0, 0))
        
        return s

'''

# 读取utils.py
with open('utils.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到插入位置（在 necro_ex 的 return s 之后，默认绘制之前）
insert_marker = '''        return s

    # 赛博朋克风格几何飞机 - 13种机体差异化设计 + 动态特性
    if pid == "striker":'''

# 插入新代码
new_content = content.replace(insert_marker, f'''        return s
{render_codes}
    # 赛博朋克风格几何飞机 - 13种机体差异化设计 + 动态特性
    if pid == "striker":''')

# 写回文件
with open('utils.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('成功添加16个新涂装的渲染代码!')
