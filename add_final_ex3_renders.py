# 添加最后6个_ex3渲染代码 (gaia到necro)

final_renders = '''    elif model_style == "gaia_ex3":
        # 四季更迭 - 轮回之树
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.5) * 0.15 + 1
        
        # 中心树干
        trunk_points = [(55, 80), (58, 40), (62, 40), (65, 80)]
        pygame.draw.polygon(s, (100, 70, 50), trunk_points)
        
        # 四季分区（树冠分成4个象限）
        seasons = [
            ("spring", 0, (100, 255, 150)),      # 春 - 绿色
            ("summer", math.pi / 2, (255, 200, 50)),   # 夏 - 金黄
            ("autumn", math.pi, (255, 100, 50)),      # 秋 - 橙红
            ("winter", 3 * math.pi / 2, (200, 230, 255))  # 冬 - 冰蓝
        ]
        
        for season_name, base_angle, color in seasons:
            # 每个季节占90度
            season_rotation = t * 2  # 整体旋转展示四季轮回
            
            for branch in range(8):
                branch_angle = base_angle + season_rotation + (branch / 8) * (math.pi / 2)
                branch_length = 20 + 15 * ((branch % 3) / 3)
                branch_x = 60 + math.cos(branch_angle) * branch_length
                branch_y = 50 + math.sin(branch_angle) * branch_length
                
                # 季节特色
                if season_name == "spring":  # 春 - 花朵
                    for petal in range(4):
                        petal_angle = t * 3 + petal * math.pi / 2
                        petal_x = branch_x + math.cos(petal_angle) * 4
                        petal_y = branch_y + math.sin(petal_angle) * 4
                        pygame.draw.circle(s, (255, 150, 200), (int(petal_x), int(petal_y)), 3)
                    pygame.draw.circle(s, color, (int(branch_x), int(branch_y)), 2)
                
                elif season_name == "summer":  # 夏 - 太阳光芒
                    pygame.draw.circle(s, color, (int(branch_x), int(branch_y)), 5)
                    for ray in range(6):
                        ray_angle = t * 4 + ray * math.pi / 3
                        ray_x = branch_x + math.cos(ray_angle) * 7
                        ray_y = branch_y + math.sin(ray_angle) * 7
                        pygame.draw.line(s, (255, 255, 100),
                                       (int(branch_x), int(branch_y)),
                                       (int(ray_x), int(ray_y)), 2)
                
                elif season_name == "autumn":  # 秋 - 落叶
                    leaf_fall = (t * 2 + branch) % 1
                    leaf_y = branch_y + leaf_fall * 30
                    leaf_alpha = int(255 * (1 - leaf_fall))
                    if leaf_alpha > 30:
                        leaf_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                        # 椭圆形叶子
                        leaf_rect = pygame.Rect(int(branch_x - 3), int(leaf_y - 2), 6, 4)
                        pygame.draw.ellipse(leaf_surf, (*color, leaf_alpha), leaf_rect)
                        s.blit(leaf_surf, (0, 0))
                
                else:  # 冬 - 雪花
                    # 六角雪花
                    for flake_arm in range(6):
                        flake_angle = branch_angle + flake_arm * math.pi / 3
                        flake_x = branch_x + math.cos(flake_angle) * 4
                        flake_y = branch_y + math.sin(flake_angle) * 4
                        pygame.draw.line(s, color,
                                       (int(branch_x), int(branch_y)),
                                       (int(flake_x), int(flake_y)), 1)
                    pygame.draw.circle(s, color, (int(branch_x), int(branch_y)), 2)
        
        # 轮回之环（四色环绕）
        for ring_seg in range(4):
            ring_color = seasons[ring_seg][2]
            ring_start_angle = seasons[ring_seg][1] + t * 2
            ring_end_angle = ring_start_angle + math.pi / 2
            
            # 绘制弧段
            arc_points = [(60, 50)]
            for arc_step in range(10):
                arc_progress = arc_step / 10
                arc_angle = ring_start_angle + (ring_end_angle - ring_start_angle) * arc_progress
                arc_x = 60 + math.cos(arc_angle) * 35
                arc_y = 50 + math.sin(arc_angle) * 35
                arc_points.append((int(arc_x), int(arc_y)))
            
            if len(arc_points) > 2:
                ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.lines(ring_surf, ring_color, False, arc_points, 3)
                s.blit(ring_surf, (0, 0))
        
        return s
    
    elif model_style == "weaver_ex3":
        # 神经网络 - 思维脉冲
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 神经元节点（多层网络）
        neurons = []
        layers = 4
        for layer in range(layers):
            neurons_in_layer = 5 + layer
            for neuron in range(neurons_in_layer):
                neuron_x = 20 + layer * 25
                neuron_y = 20 + (100 / (neurons_in_layer + 1)) * (neuron + 1)
                # 激活强度
                activation = (math.sin(t * 3 + layer * 0.5 + neuron * 0.3) + 1) / 2
                neurons.append((neuron_x, neuron_y, activation, layer))
        
        # 绘制神经连接（突触）
        synapse_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i, (x1, y1, act1, layer1) in enumerate(neurons):
            for j, (x2, y2, act2, layer2) in enumerate(neurons):
                # 只连接相邻层
                if layer2 == layer1 + 1:
                    # 连接强度
                    connection_strength = (act1 + act2) / 2
                    synapse_alpha = int(200 * connection_strength)
                    synapse_width = 1 + int(2 * connection_strength)
                    
                    # 脉冲传递动画
                    pulse_progress = (t * 2 + i * 0.1 + j * 0.1) % 1
                    pulse_x = x1 + (x2 - x1) * pulse_progress
                    pulse_y = y1 + (y2 - y1) * pulse_progress
                    
                    # 绘制连接线
                    pygame.draw.line(synapse_surf, (100, 200, 255, synapse_alpha),
                                   (int(x1), int(y1)), (int(x2), int(y2)), synapse_width)
                    
                    # 绘制脉冲点
                    pulse_size = int(3 * connection_strength)
                    if pulse_size > 0:
                        pygame.draw.circle(synapse_surf, (255, 255, 100),
                                         (int(pulse_x), int(pulse_y)), pulse_size)
        s.blit(synapse_surf, (0, 0))
        
        # 绘制神经元
        for neuron_x, neuron_y, activation, layer in neurons:
            neuron_size = int(5 + 5 * activation)
            neuron_brightness = int(150 + 105 * activation)
            
            # 神经元核心
            pygame.draw.circle(s, (neuron_brightness, neuron_brightness, 255), 
                             (int(neuron_x), int(neuron_y)), neuron_size)
            # 神经元外环
            pygame.draw.circle(s, (200, 200, 255), 
                             (int(neuron_x), int(neuron_y)), neuron_size + 2, 1)
            
            # 激活时发光
            if activation > 0.7:
                glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                glow_alpha = int(150 * (activation - 0.7) / 0.3)
                pygame.draw.circle(glow_surf, (255, 255, 200, glow_alpha),
                                 (int(neuron_x), int(neuron_y)), neuron_size + 5)
                s.blit(glow_surf, (0, 0))
        
        # 电信号波纹（全局思维活动）
        for signal_wave in range(3):
            wave_progress = (t * 1.5 + signal_wave * 0.5) % 1
            wave_x = 20 + wave_progress * 100
            wave_alpha = int(180 * (1 - abs(wave_progress - 0.5) * 2))
            
            if wave_alpha > 30:
                signal_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(signal_surf, (150, 200, 255, wave_alpha),
                               (int(wave_x), 10), (int(wave_x), 110), 2)
                s.blit(signal_surf, (0, 0))
        
        return s
    
    elif model_style == "solar_ex3":
        # 暗物质潮汐 - 引力奇点
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.2 + 1
        
        # 奇点核心（超密黑洞）
        singularity_radius = int(8 * pulse)
        # 事件视界
        for horizon_layer in range(5, 0, -1):
            horizon_radius = int(singularity_radius * (horizon_layer / 5))
            horizon_alpha = int(255 * (horizon_layer / 5))
            # 黑到紫的渐变
            horizon_color = (50 * (horizon_layer / 5), 0, 100 * (horizon_layer / 5))
            pygame.draw.circle(s, (*horizon_color, horizon_alpha), (60, 50), horizon_radius)
        
        # 吸积盘（螺旋旋转）
        accretion_spirals = 3
        for spiral in range(accretion_spirals):
            spiral_offset = spiral * 2 * math.pi / accretion_spirals
            
            for segment in range(30):
                seg_angle = t * 3 + spiral_offset + segment * 0.3
                seg_dist = 12 + segment * 1.5
                seg_x = 60 + math.cos(seg_angle) * seg_dist
                seg_y = 50 + math.sin(seg_angle) * seg_dist * 0.3  # 扁平
                
                # 颜色从外到内：蓝->紫->红（温度上升）
                temp_factor = 1 - (segment / 30)
                if temp_factor > 0.7:
                    seg_color = (100, 100, 255)
                elif temp_factor > 0.4:
                    seg_color = (200, 100, 255)
                else:
                    seg_color = (255, 150, 100)
                
                seg_alpha = int(220 * (1 - temp_factor * 0.5))
                seg_size = int(3 + 3 * temp_factor)
                
                pygame.draw.circle(s, (*seg_color, seg_alpha),
                                 (int(seg_x), int(seg_y)), seg_size)
        
        # 引力透镜效应（光线弯曲）
        for lens_ring in range(4):
            ring_radius = 15 + lens_ring * 10
            ring_rotation = t * (1 + lens_ring * 0.2)
            ring_alpha = int(180 - lens_ring * 40)
            
            # 扭曲的环
            lens_points = []
            for i in range(20):
                lens_angle = i * math.pi / 10 + ring_rotation
                # 引力扭曲
                distortion = 5 * math.sin(lens_angle * 3)
                lensed_radius = ring_radius + distortion
                lens_x = 60 + math.cos(lens_angle) * lensed_radius
                lens_y = 50 + math.sin(lens_angle) * lensed_radius * 0.6
                lens_points.append((int(lens_x), int(lens_y)))
            
            if len(lens_points) > 2:
                lens_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.lines(lens_surf, (150, 150, 255, ring_alpha), True, lens_points, 2)
                s.blit(lens_surf, (0, 0))
        
        # 霍金辐射（从事件视界逃逸的粒子）
        for radiation in range(15):
            rad_angle = t * 4 + radiation * 0.4
            rad_progress = (t * 2 + radiation * 0.2) % 1
            rad_start_dist = singularity_radius + 2
            rad_dist = rad_start_dist + rad_progress * 30
            rad_x = 60 + math.cos(rad_angle) * rad_dist
            rad_y = 50 + math.sin(rad_angle) * rad_dist
            rad_alpha = int(255 * (1 - rad_progress))
            
            if rad_alpha > 30:
                pygame.draw.circle(s, (200, 200, 255, rad_alpha),
                                 (int(rad_x), int(rad_y)), 2)
        
        # 时空扭曲网格
        grid_lines = 8
        for grid_x in range(grid_lines):
            grid_points = []
            for grid_y in range(grid_lines):
                gx = 20 + grid_x * 10
                gy = 20 + grid_y * 10
                # 靠近奇点时扭曲
                dx = gx - 60
                dy = gy - 50
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0:
                    warp_factor = max(0, 1 - dist / 50)
                    warp_strength = warp_factor * 15
                    warp_angle = math.atan2(dy, dx) + math.pi
                    gx += math.cos(warp_angle) * warp_strength
                    gy += math.sin(warp_angle) * warp_strength
                grid_points.append((int(gx), int(gy)))
            
            if len(grid_points) > 1:
                grid_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.lines(grid_surf, (80, 80, 120, 100), False, grid_points, 1)
                s.blit(grid_surf, (0, 0))
        
        return s
    
    elif model_style == "arbiter_ex3":
        # 真理之门 - 全知之眼
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.8) * 0.2 + 1
        
        # 中心全知之眼
        eye_radius = int(15 * pulse)
        # 眼白
        pygame.draw.circle(s, (255, 255, 255), (60, 50), eye_radius)
        # 虹膜（多层）
        iris_colors = [(100, 150, 255), (150, 200, 255), (200, 230, 255)]
        for iris_layer, iris_color in enumerate(iris_colors):
            iris_radius = int(eye_radius * 0.7 * ((3 - iris_layer) / 3))
            pygame.draw.circle(s, iris_color, (60, 50), iris_radius)
        # 瞳孔
        pupil_radius = int(eye_radius * 0.3)
        pygame.draw.circle(s, (0, 0, 0), (60, 50), pupil_radius)
        # 瞳孔反光
        pygame.draw.circle(s, (255, 255, 255), (62, 48), max(2, pupil_radius // 3))
        
        # 眼睑/边框
        pygame.draw.circle(s, (200, 180, 255), (60, 50), eye_radius, 2)
        
        # 真理之门框架（巨大门框）
        gate_width = 80
        gate_height = 100
        gate_left = 60 - gate_width // 2
        gate_top = 50 - gate_height // 2
        
        # 门框立柱
        left_pillar = pygame.Rect(gate_left - 5, gate_top, 5, gate_height)
        right_pillar = pygame.Rect(gate_left + gate_width, gate_top, 5, gate_height)
        pygame.draw.rect(s, (180, 160, 220), left_pillar)
        pygame.draw.rect(s, (180, 160, 220), right_pillar)
        pygame.draw.rect(s, (220, 200, 255), left_pillar, 1)
        pygame.draw.rect(s, (220, 200, 255), right_pillar, 1)
        
        # 门楣
        lintel = pygame.Rect(gate_left - 5, gate_top - 5, gate_width + 10, 5)
        pygame.draw.rect(s, (180, 160, 220), lintel)
        pygame.draw.rect(s, (220, 200, 255), lintel, 1)
        
        # 古代符文（在门框上）
        runes_on_gate = 12
        for rune_idx in range(runes_on_gate):
            rune_progress = rune_idx / runes_on_gate
            rune_brightness = int(150 + 105 * ((math.sin(t * 4 + rune_idx) + 1) / 2))
            
            if rune_idx < 6:  # 左柱
                rune_x = gate_left - 2
                rune_y = gate_top + int(gate_height * rune_progress)
            else:  # 右柱
                rune_x = gate_left + gate_width + 2
                rune_y = gate_top + int(gate_height * ((rune_idx - 6) / 6))
            
            # 简单符文形状（十字）
            rune_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(rune_surf, (rune_brightness, rune_brightness, 255),
                           (rune_x - 2, rune_y), (rune_x + 2, rune_y), 1)
            pygame.draw.line(rune_surf, (rune_brightness, rune_brightness, 255),
                           (rune_x, rune_y - 2), (rune_x, rune_y + 2), 1)
            s.blit(rune_surf, (0, 0))
        
        # 凝视射线（从眼睛射出）
        gaze_count = 16
        for gaze in range(gaze_count):
            gaze_angle = t * 2 + gaze * 2 * math.pi / gaze_count
            gaze_length = 35 + 10 * math.sin(t * 3 + gaze)
            gaze_ex = 60 + math.cos(gaze_angle) * gaze_length
            gaze_ey = 50 + math.sin(gaze_angle) * gaze_length
            
            gaze_alpha = int(150 * ((math.sin(t * 4 + gaze) + 1) / 2))
            if gaze_alpha > 50:
                gaze_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(gaze_surf, (200, 200, 255, gaze_alpha),
                               (60, 50), (int(gaze_ex), int(gaze_ey)), 1)
                s.blit(gaze_surf, (0, 0))
        
        # 知识粒子（环绕）
        for knowledge in range(20):
            know_angle = t * 1.5 + knowledge * 0.3
            know_dist = 25 + 15 * ((knowledge % 4) / 4)
            know_x = 60 + math.cos(know_angle) * know_dist
            know_y = 50 + math.sin(know_angle) * know_dist
            know_brightness = int(200 + 55 * math.sin(t * 5 + knowledge))
            
            # 书本/卷轴形状
            book_rect = pygame.Rect(int(know_x - 2), int(know_y - 3), 4, 6)
            pygame.draw.rect(s, (know_brightness, know_brightness, 255), book_rect)
            pygame.draw.line(s, (255, 255, 255), (int(know_x - 2), int(know_y)),
                           (int(know_x + 2), int(know_y)), 1)
        
        return s
    
    elif model_style == "eclipse_ex3":
        # 反物质引擎 - 湮灭核心
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.25 + 1
        
        # 湮灭核心（正反物质碰撞）
        core_radius = int(10 * pulse)
        # 能量爆发
        for explosion_layer in range(6, 0, -1):
            layer_radius = int(core_radius * (explosion_layer / 6))
            layer_alpha = 255
            # 白->黄->橙->红渐变
            if explosion_layer > 4:
                layer_color = (255, 255, 255)
            elif explosion_layer > 2:
                layer_color = (255, 255, 100)
            else:
                layer_color = (255, 150, 50)
            pygame.draw.circle(s, (*layer_color, layer_alpha), (60, 50), layer_radius)
        
        # 正物质流（蓝色，从左侧流入）
        matter_particles = 15
        for mp in range(matter_particles):
            mp_progress = (t * 3 + mp * 0.2) % 1
            mp_x = 10 + mp_progress * 45
            mp_y = 50 + math.sin(t * 4 + mp) * 10
            mp_alpha = int(255 * (1 - mp_progress))
            mp_size = 3 + int(3 * (1 - mp_progress))
            
            if mp_alpha > 30:
                pygame.draw.circle(s, (100, 150, 255, mp_alpha),
                                 (int(mp_x), int(mp_y)), mp_size)
        
        # 反物质流（红色，从右侧流入）
        for amp in range(matter_particles):
            amp_progress = (t * 3 + amp * 0.2) % 1
            amp_x = 110 - amp_progress * 45
            amp_y = 50 + math.sin(t * 4 + amp + math.pi) * 10
            amp_alpha = int(255 * (1 - amp_progress))
            amp_size = 3 + int(3 * (1 - amp_progress))
            
            if amp_alpha > 30:
                pygame.draw.circle(s, (255, 100, 100, amp_alpha),
                                 (int(amp_x), int(amp_y)), amp_size)
        
        # 湮灭光子射出（伽马射线）
        gamma_rays = 12
        for gamma in range(gamma_rays):
            gamma_angle = gamma * 2 * math.pi / gamma_rays + t * 4
            gamma_progress = (t * 5 + gamma * 0.3) % 1
            gamma_start_dist = core_radius + 2
            gamma_dist = gamma_start_dist + gamma_progress * 40
            gamma_x = 60 + math.cos(gamma_angle) * gamma_dist
            gamma_y = 50 + math.sin(gamma_angle) * gamma_dist
            gamma_alpha = int(255 * (1 - gamma_progress))
            
            if gamma_alpha > 30:
                # 绘制射线
                gamma_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                gamma_sx = 60 + math.cos(gamma_angle) * gamma_start_dist
                gamma_sy = 50 + math.sin(gamma_angle) * gamma_start_dist
                pygame.draw.line(gamma_surf, (255, 255, 255, gamma_alpha),
                               (int(gamma_sx), int(gamma_sy)),
                               (int(gamma_x), int(gamma_y)), 2)
                s.blit(gamma_surf, (0, 0))
        
        # 能量环（湮灭产生的冲击波）
        for shockwave in range(4):
            wave_progress = (t * 2 + shockwave * 0.3) % 1
            wave_radius = int(15 + wave_progress * 45)
            wave_alpha = int(220 * (1 - wave_progress))
            
            if wave_alpha > 30:
                wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(wave_surf, (255, 200, 150, wave_alpha),
                                 (60, 50), wave_radius, 3)
                s.blit(wave_surf, (0, 0))
        
        # 磁约束场（防止提前湮灭）
        magnetic_field_lines = 8
        for field_line in range(magnetic_field_lines):
            field_angle = field_line * math.pi / 4
            field_rotation = t * 2
            
            # 磁力线弧形
            field_points = []
            for arc_seg in range(15):
                arc_progress = arc_seg / 15
                arc_dist = 20 + arc_progress * 25
                arc_angle = field_angle + field_rotation + math.sin(arc_progress * math.pi) * 0.5
                field_x = 60 + math.cos(arc_angle) * arc_dist
                field_y = 50 + math.sin(arc_angle) * arc_dist
                field_points.append((int(field_x), int(field_y)))
            
            if len(field_points) > 1:
                field_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.lines(field_surf, (100, 255, 255, 150), False, field_points, 1)
                s.blit(field_surf, (0, 0))
        
        return s
    
    elif model_style == "prism_ex3":
        # 五维投影 - 超立方体
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.5) * 0.15 + 1
        
        # 4D超立方体的3D投影顶点（Tesseract）
        # 内立方体顶点
        inner_size = 15
        inner_vertices = [
            (60 - inner_size, 50 - inner_size, -inner_size),
            (60 + inner_size, 50 - inner_size, -inner_size),
            (60 + inner_size, 50 + inner_size, -inner_size),
            (60 - inner_size, 50 + inner_size, -inner_size),
            (60 - inner_size, 50 - inner_size, inner_size),
            (60 + inner_size, 50 - inner_size, inner_size),
            (60 + inner_size, 50 + inner_size, inner_size),
            (60 - inner_size, 50 + inner_size, inner_size),
        ]
        
        # 外立方体顶点
        outer_size = 25
        outer_vertices = [
            (60 - outer_size, 50 - outer_size, -outer_size),
            (60 + outer_size, 50 - outer_size, -outer_size),
            (60 + outer_size, 50 + outer_size, -outer_size),
            (60 - outer_size, 50 + outer_size, -outer_size),
            (60 - outer_size, 50 - outer_size, outer_size),
            (60 + outer_size, 50 - outer_size, outer_size),
            (60 + outer_size, 50 + outer_size, outer_size),
            (60 - outer_size, 50 + outer_size, outer_size),
        ]
        
        # 4D旋转矩阵（简化投影）
        rotation_4d = t * 1.5
        
        # 投影顶点（应用4D旋转）
        def project_4d_vertex(v, w_coord):
            x, y, z = v
            # 简化的4D->3D投影
            w = w_coord * math.cos(rotation_4d)
            proj_scale = 1 / (4 - w * 0.1)
            return (int(x * proj_scale), int(y * proj_scale))
        
        inner_projected = [project_4d_vertex(v, -1) for v in inner_vertices]
        outer_projected = [project_4d_vertex(v, 1) for v in outer_vertices]
        
        # 绘制内立方体边
        inner_edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # 前面
            (4, 5), (5, 6), (6, 7), (7, 4),  # 后面
            (0, 4), (1, 5), (2, 6), (3, 7),  # 连接
        ]
        
        for edge in inner_edges:
            p1 = inner_projected[edge[0]]
            p2 = inner_projected[edge[1]]
            pygame.draw.line(s, (150, 200, 255), p1, p2, 2)
        
        # 绘制外立方体边
        for edge in inner_edges:
            p1 = outer_projected[edge[0]]
            p2 = outer_projected[edge[1]]
            pygame.draw.line(s, (200, 150, 255), p1, p2, 2)
        
        # 连接内外立方体（超立方体的4D边）
        for i in range(8):
            p1 = inner_projected[i]
            p2 = outer_projected[i]
            hyper_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(hyper_surf, (255, 200, 255, 180), p1, p2, 1)
            s.blit(hyper_surf, (0, 0))
        
        # 绘制顶点
        for vertex in inner_projected:
            pygame.draw.circle(s, (100, 255, 255), vertex, 4)
        for vertex in outer_projected:
            pygame.draw.circle(s, (255, 100, 255), vertex, 4)
        
        # 维度波动效果
        for dimension_wave in range(5):
            wave_angle = t * 2 + dimension_wave * 2 * math.pi / 5
            wave_dist = 35 + 10 * math.sin(t * 3 + dimension_wave)
            wave_x = 60 + math.cos(wave_angle) * wave_dist
            wave_y = 50 + math.sin(wave_angle) * wave_dist
            wave_alpha = int(200 * ((math.sin(t * 4 + dimension_wave) + 1) / 2))
            
            # 高维粒子
            for glow in range(3, 0, -1):
                glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                glow_radius = glow * 3
                glow_alpha = int(wave_alpha * (glow / 3))
                pygame.draw.circle(glow_surf, (255, 255, 255, glow_alpha),
                                 (int(wave_x), int(wave_y)), glow_radius)
                s.blit(glow_surf, (0, 0))
        
        # 维度裂缝（5D空间的切面）
        rift_count = 6
        for rift in range(rift_count):
            rift_angle = rift * math.pi / 3 + t
            rift_length = 40
            rift_x1 = 60 + math.cos(rift_angle) * 10
            rift_y1 = 50 + math.sin(rift_angle) * 10
            rift_x2 = 60 + math.cos(rift_angle) * rift_length
            rift_y2 = 50 + math.sin(rift_angle) * rift_length
            
            rift_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            rift_alpha = int(150 * ((math.sin(t * 3 + rift) + 1) / 2))
            pygame.draw.line(rift_surf, (200, 200, 255, rift_alpha),
                           (int(rift_x1), int(rift_y1)),
                           (int(rift_x2), int(rift_y2)), 2)
            s.blit(rift_surf, (0, 0))
        
        return s
    
    elif model_style == "necro_ex3":
        # 熵增极限 - 热寂降临
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.2) * 0.1 + 1  # 缓慢脉动
        
        # 中心热寂核心（温度接近绝对零度）
        core_radius = int(12 * pulse)
        # 深蓝到黑的渐变（低温）
        for core_layer in range(6, 0, -1):
            layer_radius = int(core_radius * (core_layer / 6))
            layer_alpha = 255
            layer_blue = int(50 * (core_layer / 6))
            core_color = (layer_blue // 3, layer_blue // 3, layer_blue)
            pygame.draw.circle(s, (*core_color, layer_alpha), (60, 50), layer_radius)
        
        # 能量耗散（粒子运动逐渐停止）
        entropy_particles = 40
        for ep in range(entropy_particles):
            # 粒子速度递减
            ep_speed = 1 - (t % 3) / 3  # 随时间减速
            ep_angle = ep * 0.5 + t * ep_speed
            ep_dist = 15 + (ep % 8) * 4
            ep_x = 60 + math.cos(ep_angle) * ep_dist
            ep_y = 50 + math.sin(ep_angle) * ep_dist
            
            # 颜色渐暗（能量降低）
            ep_brightness = int(150 * ep_speed)
            ep_alpha = int(200 * ep_speed)
            ep_size = max(1, int(3 * ep_speed))
            
            if ep_alpha > 30:
                pygame.draw.circle(s, (ep_brightness // 2, ep_brightness // 2, ep_brightness, ep_alpha),
                                 (int(ep_x), int(ep_y)), ep_size)
        
        # 热死环（能量均匀分布）
        thermal_rings = 6
        for ring in range(thermal_rings):
            ring_radius = 15 + ring * 8
            ring_alpha = int(100 - ring * 15)
            
            # 环不完整（象征结构崩解）
            ring_completeness = 1 - (ring / thermal_rings) * 0.5
            ring_segments = int(20 * ring_completeness)
            
            for seg in range(ring_segments):
                seg_angle = seg * 2 * math.pi / 20 + t * 0.3
                seg_x1 = 60 + math.cos(seg_angle) * ring_radius
                seg_y1 = 50 + math.sin(seg_angle) * ring_radius
                seg_angle2 = (seg + 1) * 2 * math.pi / 20 + t * 0.3
                seg_x2 = 60 + math.cos(seg_angle2) * ring_radius
                seg_y2 = 50 + math.sin(seg_angle2) * ring_radius
                
                if ring_alpha > 10:
                    ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(ring_surf, (50, 50, 80, ring_alpha),
                                   (int(seg_x1), int(seg_y1)),
                                   (int(seg_x2), int(seg_y2)), 2)
                    s.blit(ring_surf, (0, 0))
        
        # 结构崩解（网格瓦解）
        grid_decay = (t % 5) / 5  # 5秒循环
        grid_size = 8
        for gx in range(grid_size):
            for gy in range(grid_size):
                grid_x = 20 + gx * 10
                grid_y = 20 + gy * 10
                
                # 网格点逐渐消失
                decay_progress = (gx + gy) / (grid_size * 2)
                if decay_progress < grid_decay:
                    continue  # 已消失
                
                point_alpha = int(120 * (1 - grid_decay))
                if point_alpha > 20:
                    pygame.draw.circle(s, (60, 60, 90, point_alpha),
                                     (grid_x, grid_y), 1)
                    
                    # 连接线
                    if gx < grid_size - 1:
                        next_x = 20 + (gx + 1) * 10
                        next_decay = (gx + 1 + gy) / (grid_size * 2)
                        if next_decay >= grid_decay:
                            line_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                            pygame.draw.line(line_surf, (60, 60, 90, point_alpha // 2),
                                           (grid_x, grid_y), (next_x, grid_y), 1)
                            s.blit(line_surf, (0, 0))
        
        # 信息丢失（随机闪烁的信息碎片）
        info_fragments = 12
        for frag in range(info_fragments):
            if (int(t * 5) + frag) % 7 < 2:  # 随机出现
                frag_angle = frag * 0.5
                frag_dist = 25 + 20 * random.random()
                frag_x = 60 + math.cos(frag_angle) * frag_dist
                frag_y = 50 + math.sin(frag_angle) * frag_dist
                frag_alpha = int(180 * random.random())
                
                # 二进制位形状
                frag_char = random.choice(['0', '1'])
                # 简化为点（无法渲染文字）
                pygame.draw.circle(s, (100, 100, 120, frag_alpha),
                                 (int(frag_x), int(frag_y)), 2)
        
        # 宇宙微波背景辐射（均匀但冰冷）
        cmb_noise = 30
        for noise in range(cmb_noise):
            noise_x = random.randint(10, 110)
            noise_y = random.randint(10, 110)
            noise_brightness = random.randint(40, 70)
            noise_alpha = random.randint(50, 100)
            pygame.draw.circle(s, (noise_brightness, noise_brightness, noise_brightness + 20, noise_alpha),
                             (noise_x, noise_y), 1)
        
        # 时间箭头停滞（熵达到最大）
        # 绘制停滞的钟表指针
        clock_center = (60, 50)
        clock_radius = 35
        # 时钟边框（破碎）
        for clock_seg in range(8):
            if (clock_seg + int(t * 2)) % 3 != 0:  # 部分缺失
                seg_start_angle = clock_seg * math.pi / 4
                seg_end_angle = seg_start_angle + math.pi / 4
                clock_points = [clock_center]
                for angle_step in range(5):
                    angle = seg_start_angle + (seg_end_angle - seg_start_angle) * (angle_step / 4)
                    cx = clock_center[0] + math.cos(angle) * clock_radius
                    cy = clock_center[1] + math.sin(angle) * clock_radius
                    clock_points.append((int(cx), int(cy)))
                
                if len(clock_points) > 2:
                    clock_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.lines(clock_surf, (80, 80, 100, 150), False, clock_points, 1)
                    s.blit(clock_surf, (0, 0))
        
        # 停滞的指针（几乎不动）
        hand_angle = t * 0.1  # 极慢
        hand_length = 25
        hand_x = 60 + math.cos(hand_angle - math.pi / 2) * hand_length
        hand_y = 50 + math.sin(hand_angle - math.pi / 2) * hand_length
        pygame.draw.line(s, (100, 100, 130), (60, 50), (int(hand_x), int(hand_y)), 2)
        
        return s
'''

# 读取文件
with open('utils.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到插入位置
insert_marker = '''        return s


    # 赛博朋克风格几何飞机 - 13种机体差异化设计 + 动态特性'''

if insert_marker in content:
    new_content = content.replace(insert_marker, f'''        return s
{final_renders}

    # 赛博朋克风格几何飞机 - 13种机体差异化设计 + 动态特性''')
    
    with open('utils.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('✅ 成功添加最后6个超级创意渲染代码! (gaia, weaver, solar, arbiter, eclipse, prism, necro)')
    print('🎉 第三批全部16个_ex3涂装渲染代码已完成!')
else:
    print('未找到插入位置')
