# 添加viper_ex4到aurora_ex4的4个渲染代码

renders_code = '''    elif model_style == "viper_ex4":
        # 生物荧光 - 深海幻影
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 荧光触手（像水母触手）
        tentacles = 8
        for tentacle in range(tentacles):
            tentacle_base_angle = tentacle * math.pi / 4
            
            # 触手节点
            tentacle_points = [(60, 50)]
            current_angle = tentacle_base_angle
            
            for segment in range(10):
                # 波动摆动
                wave = math.sin(t * 2 - segment * 0.3) * 0.3
                current_angle = tentacle_base_angle + wave
                segment_dist = (segment + 1) * 4
                tx = 60 + math.cos(current_angle) * segment_dist
                ty = 50 + math.sin(current_angle) * segment_dist
                tentacle_points.append((int(tx), int(ty)))
            
            # 绘制触手（渐变色）
            for i in range(len(tentacle_points) - 1):
                seg_progress = i / len(tentacle_points)
                # 青绿到蓝紫渐变
                seg_r = int(0 + 100 * seg_progress)
                seg_g = int(255 - 105 * seg_progress)
                seg_b = int(200 + 55 * seg_progress)
                seg_alpha = int(220 * (1 - seg_progress))
                seg_width = int(6 * (1 - seg_progress)) + 1
                
                if seg_alpha > 30:
                    tent_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(tent_surf, (seg_r, seg_g, seg_b, seg_alpha),
                                   tentacle_points[i], tentacle_points[i + 1], seg_width)
                    s.blit(tent_surf, (0, 0))
        
        # 荧光脉冲（从中心向外）
        pulse_waves = 5
        for wave in range(pulse_waves):
            wave_progress = (t * 1.5 + wave * 0.3) % 1
            wave_radius = int(10 + wave_progress * 45)
            wave_alpha = int(200 * (1 - wave_progress))
            
            if wave_alpha > 30:
                # 颜色随波动变化
                wave_hue_shift = wave_progress
                wave_r = int(0 + 100 * wave_hue_shift)
                wave_g = int(255 - 55 * wave_hue_shift)
                wave_b = int(200 + 55 * wave_hue_shift)
                
                wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(wave_surf, (wave_r, wave_g, wave_b, wave_alpha),
                                 (60, 50), wave_radius, 3)
                s.blit(wave_surf, (0, 0))
        
        # 荧光粒子漂浮
        for particle in range(40):
            # 粒子波动路径
            p_base_angle = particle * 0.4
            p_wave = math.sin(t * 2 + particle * 0.2) * 10
            p_dist = 15 + (particle % 8) * 4 + p_wave
            px = 60 + math.cos(p_base_angle) * p_dist
            py = 50 + math.sin(p_base_angle) * p_dist
            
            # 粒子闪烁
            p_brightness = (math.sin(t * 4 + particle * 0.5) + 1) / 2
            p_alpha = int(200 * p_brightness)
            p_size = 2 + int(2 * p_brightness)
            
            # 青绿荧光
            if p_alpha > 30:
                pygame.draw.circle(s, (0, 255, 200, p_alpha), (int(px), int(py)), p_size)
        
        # 中心荧光核（像水母伞部）
        core_radius = int(12 + 5 * math.sin(t * 2))
        for core_layer in range(4, 0, -1):
            layer_radius = int(core_radius * (core_layer / 4))
            layer_alpha = int(180 * (core_layer / 4))
            # 渐变：青色到蓝色
            layer_g = int(255 * (core_layer / 4))
            layer_b = int(200 + 55 * (1 - core_layer / 4))
            core_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(core_surf, (50, layer_g, layer_b, layer_alpha),
                             (60, 50), layer_radius)
            s.blit(core_surf, (0, 0))
        
        # 生物电流（螺旋）
        for spiral in range(3):
            spiral_offset = spiral * 2 * math.pi / 3
            spiral_points = []
            
            for step in range(15):
                step_prog = step / 15
                spiral_angle = spiral_offset + step_prog * math.pi * 4 + t * 2
                spiral_radius = 15 + step_prog * 30
                sx = 60 + math.cos(spiral_angle) * spiral_radius
                sy = 50 + math.sin(spiral_angle) * spiral_radius
                spiral_points.append((int(sx), int(sy)))
            
            # 绘制螺旋
            for i in range(len(spiral_points) - 1):
                alpha = int(150 * (1 - i / len(spiral_points)))
                if alpha > 30:
                    spiral_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(spiral_surf, (100, 255, 220, alpha),
                                   spiral_points[i], spiral_points[i + 1], 2)
                    s.blit(spiral_surf, (0, 0))
        
        return s
    
    elif model_style == "specter_ex4":
        # 全息投影 - 数据流动
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 扫描线效果
        scan_lines = 15
        for scan in range(scan_lines):
            scan_y = int((t * 80 + scan * 8) % 120)
            scan_alpha = int(150 * (math.sin(t * 3 + scan) + 1) / 2)
            
            if scan_alpha > 30:
                scan_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(scan_surf, (0, 255, 255, scan_alpha),
                               (10, scan_y), (110, scan_y), 1)
                s.blit(scan_surf, (0, 0))
        
        # 数据流粒子（二进制）
        data_particles = 50
        for dp in range(data_particles):
            dp_x = 20 + (dp % 10) * 10
            dp_progress = (t * 2 + dp * 0.1) % 1
            dp_y = 10 + dp_progress * 100
            dp_alpha = int(200 * (1 - abs(dp_progress - 0.5) * 2))
            
            if dp_alpha > 30:
                # 二进制位（0或1）
                dp_value = (int(t * 10) + dp) % 2
                dp_color = (0, 255, 255) if dp_value == 1 else (255, 0, 255)
                pygame.draw.circle(s, (*dp_color, dp_alpha), (dp_x, int(dp_y)), 2)
        
        # 全息网格（三维投影）
        grid_layers = 4
        for layer in range(grid_layers):
            layer_depth = layer / grid_layers
            layer_scale = 0.5 + layer_depth * 0.5
            layer_offset_y = int(layer * 5 * math.sin(t + layer))
            layer_alpha = int(120 + 80 * layer_depth)
            
            # 网格线
            grid_size = 4
            for gx in range(grid_size + 1):
                # 垂直线
                x_pos = int(30 + gx * 15 * layer_scale)
                y_start = int(30 + layer_offset_y)
                y_end = int(70 + layer_offset_y)
                
                grid_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(grid_surf, (100, 200, 255, layer_alpha),
                               (x_pos, y_start), (x_pos, y_end), 1)
                s.blit(grid_surf, (0, 0))
            
            for gy in range(grid_size + 1):
                # 水平线
                y_pos = int(30 + gy * 10 * layer_scale + layer_offset_y)
                x_start = int(30)
                x_end = int(30 + grid_size * 15 * layer_scale)
                
                grid_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(grid_surf, (100, 200, 255, layer_alpha),
                               (x_start, y_pos), (x_end, y_pos), 1)
                s.blit(grid_surf, (0, 0))
        
        # 像素化重构效果
        pixel_blocks = 12
        for block in range(pixel_blocks):
            # 随机出现的像素块
            if (int(t * 5) + block) % 8 < 5:
                block_angle = block * 0.5
                block_dist = 20 + (block % 4) * 8
                block_x = int(60 + math.cos(block_angle) * block_dist)
                block_y = int(50 + math.sin(block_angle) * block_dist)
                block_size = 6
                
                # 青色和品红交替
                block_color = (0, 255, 255) if block % 2 == 0 else (255, 0, 255)
                block_alpha = int(180 * ((math.sin(t * 4 + block) + 1) / 2))
                
                if block_alpha > 30:
                    block_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    block_rect = pygame.Rect(block_x - block_size // 2,
                                            block_y - block_size // 2,
                                            block_size, block_size)
                    pygame.draw.rect(block_surf, (*block_color, block_alpha), block_rect)
                    pygame.draw.rect(block_surf, (255, 255, 255, block_alpha), block_rect, 1)
                    s.blit(block_surf, (0, 0))
        
        # 中心全息核心
        holo_core_radius = int(15 + 5 * math.sin(t * 2.5))
        for holo_ring in range(3):
            ring_radius = holo_core_radius + holo_ring * 8
            ring_alpha = int(150 - holo_ring * 40)
            holo_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 青蓝色
            pygame.draw.circle(holo_surf, (0, 200, 255, ring_alpha), (60, 50), ring_radius, 2)
            s.blit(holo_surf, (0, 0))
        
        # 数据流螺旋
        data_stream_points = []
        for stream_step in range(20):
            stream_prog = stream_step / 20
            stream_angle = stream_prog * math.pi * 6 + t * 3
            stream_radius = 10 + stream_prog * 35
            stream_x = 60 + math.cos(stream_angle) * stream_radius
            stream_y = 50 + math.sin(stream_angle) * stream_radius
            data_stream_points.append((int(stream_x), int(stream_y)))
        
        # 绘制数据流
        for i in range(len(data_stream_points) - 1):
            stream_alpha = int(180 * (1 - i / len(data_stream_points)))
            if stream_alpha > 30:
                stream_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                stream_color = (0, 255, 255) if i % 2 == 0 else (255, 0, 255)
                pygame.draw.line(stream_surf, (*stream_color, stream_alpha),
                               data_stream_points[i], data_stream_points[i + 1], 2)
                s.blit(stream_surf, (0, 0))
        
        return s
    
    elif model_style == "aurora_ex4":
        # 蝴蝶效应 - 混沌之翼
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 蝴蝶翅膀形状（洛伦兹吸引子投影）
        wing_points_left = []
        wing_points_right = []
        
        # 使用混沌方程生成翅膀轨迹
        for step in range(30):
            step_prog = step / 30
            # 简化的混沌轨迹
            chaos_x = 20 * math.sin(step_prog * math.pi * 4 + t * 2) * step_prog
            chaos_y = 25 * math.sin(step_prog * math.pi * 2 + t) * (1 - step_prog)
            
            # 左翼
            left_x = int(60 - 10 - chaos_x)
            left_y = int(50 + chaos_y)
            wing_points_left.append((left_x, left_y))
            
            # 右翼（镜像）
            right_x = int(60 + 10 + chaos_x)
            right_y = int(50 + chaos_y)
            wing_points_right.append((right_x, right_y))
        
        # 绘制翅膀（渐变色彩）
        for i in range(len(wing_points_left) - 1):
            color_prog = i / len(wing_points_left)
            # 彩虹渐变
            if color_prog < 0.33:
                wing_r = int(255 * (1 - color_prog / 0.33))
                wing_g = int(255 * (color_prog / 0.33))
                wing_b = 150
            elif color_prog < 0.67:
                wing_r = 150
                wing_g = int(255 * (1 - (color_prog - 0.33) / 0.34))
                wing_b = int(255 * ((color_prog - 0.33) / 0.34))
            else:
                wing_r = int(255 * ((color_prog - 0.67) / 0.33))
                wing_g = 150
                wing_b = int(255 * (1 - (color_prog - 0.67) / 0.33))
            
            wing_alpha = int(200 * (1 - color_prog * 0.5))
            
            # 左翼
            wing_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(wing_surf, (wing_r, wing_g, wing_b, wing_alpha),
                           wing_points_left[i], wing_points_left[i + 1], 4)
            s.blit(wing_surf, (0, 0))
            
            # 右翼
            wing_surf2 = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(wing_surf2, (wing_r, wing_g, wing_b, wing_alpha),
                           wing_points_right[i], wing_points_right[i + 1], 4)
            s.blit(wing_surf2, (0, 0))
        
        # 翅膀上的斑点（随机生成）
        random.seed(int(t * 2))  # 半随机
        for spot in range(20):
            spot_side = spot % 2
            spot_prog = (spot // 2) / 10
            
            # 斑点位置
            base_x = 60 + (-25 if spot_side == 0 else 25)
            base_y = 50
            offset_x = int((random.random() - 0.5) * 30 * spot_prog)
            offset_y = int((random.random() - 0.5) * 40 * (1 - spot_prog))
            spot_x = base_x + offset_x
            spot_y = base_y + offset_y
            
            # 斑点颜色（随机）
            spot_colors = [
                (255, 100, 150),
                (150, 200, 255),
                (200, 255, 100),
                (255, 200, 100),
                (150, 100, 255)
            ]
            spot_color = spot_colors[spot % len(spot_colors)]
            spot_size = 3 + int(3 * random.random())
            spot_alpha = int(180 * (1 - spot_prog * 0.5))
            
            if spot_alpha > 30:
                pygame.draw.circle(s, (*spot_color, spot_alpha), (spot_x, spot_y), spot_size)
        
        random.seed()  # 重置随机种子
        
        # 混沌轨迹（粒子流）
        for particle in range(25):
            p_progress = (t * 2 + particle * 0.1) % 1
            # 混沌轨迹
            p_x = 60 + 35 * math.sin(p_progress * math.pi * 6 + particle * 0.3)
            p_y = 50 + 30 * math.cos(p_progress * math.pi * 4 + particle * 0.2)
            p_alpha = int(180 * (1 - p_progress))
            
            if p_alpha > 30:
                # 彩色粒子
                p_hue = (p_progress + particle / 25) % 1
                if p_hue < 0.5:
                    p_color = (255, int(255 * (p_hue * 2)), int(255 * (1 - p_hue * 2)))
                else:
                    p_color = (int(255 * (1 - (p_hue - 0.5) * 2)), int(255 * ((p_hue - 0.5) * 2)), 255)
                
                pygame.draw.circle(s, (*p_color, p_alpha), (int(p_x), int(p_y)), 2)
        
        # 蝴蝶身体
        body_segments = 5
        for seg in range(body_segments):
            seg_y = 35 + seg * 6
            seg_width = 4 - seg // 2
            pygame.draw.circle(s, (50, 50, 80), (60, seg_y), seg_width)
        
        # 触角
        for antenna in [-1, 1]:
            antenna_points = [(60, 35)]
            for ant_seg in range(5):
                ant_prog = ant_seg / 5
                ant_angle = -math.pi / 2 + antenna * (math.pi / 6 + ant_prog * math.pi / 6)
                ant_x = 60 + antenna * 5 + math.cos(ant_angle) * ant_prog * 12
                ant_y = 35 - math.sin(ant_angle) * ant_prog * 12
                antenna_points.append((int(ant_x), int(ant_y)))
            
            if len(antenna_points) > 1:
                pygame.draw.lines(s, (80, 80, 120), False, antenna_points, 2)
        
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
{renders_code}

    # 赛博朋克风格几何飞机 - 13种机体差异化设计 + 动态特性''')
    
    with open('utils.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('✅ 成功添加 viper, specter, aurora 共3个渲染代码!')
else:
    print('未找到插入位置')
