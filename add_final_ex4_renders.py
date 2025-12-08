# 添加最后9个_ex4渲染代码（crimson到necro）

final_renders = '''    elif model_style == "crimson_ex4":
        # 烟火绽放 - 庆典之舞
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 烟花爆炸点（多个）
        fireworks = 5
        for fw in range(fireworks):
            # 每个烟花的爆炸进度
            fw_progress = ((t * 1.5 + fw * 0.4) % 1)
            fw_angle_offset = fw * 1.3
            fw_x = 60 + int(25 * math.cos(fw_angle_offset))
            fw_y = 50 + int(25 * math.sin(fw_angle_offset))
            
            # 烟花粒子
            if fw_progress < 0.8:
                particle_count = 16
                for particle in range(particle_count):
                    particle_angle = (particle / particle_count) * math.pi * 2
                    particle_dist = fw_progress * 30
                    px = fw_x + int(math.cos(particle_angle) * particle_dist)
                    py = fw_y + int(math.sin(particle_angle) * particle_dist)
                    
                    # 粒子颜色（随烟花变化）
                    if fw % 3 == 0:
                        p_color = (255, int(100 + 155 * (1 - fw_progress)), 100)
                    elif fw % 3 == 1:
                        p_color = (int(100 + 155 * (1 - fw_progress)), 255, 100)
                    else:
                        p_color = (100, int(100 + 155 * (1 - fw_progress)), 255)
                    
                    p_alpha = int(250 * (1 - fw_progress))
                    p_size = int(4 * (1 - fw_progress)) + 1
                    
                    if p_alpha > 30:
                        pygame.draw.circle(s, (*p_color, p_alpha), (px, py), p_size)
                        # 拖尾
                        trail_len = int(5 * (1 - fw_progress))
                        trail_x = fw_x + int(math.cos(particle_angle) * (particle_dist - trail_len))
                        trail_y = fw_y + int(math.sin(particle_angle) * (particle_dist - trail_len))
                        trail_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                        pygame.draw.line(trail_surf, (*p_color, p_alpha // 2),
                                       (trail_x, trail_y), (px, py), 2)
                        s.blit(trail_surf, (0, 0))
        
        # 持续的火花雨
        for spark in range(30):
            spark_progress = (t * 2 + spark * 0.1) % 1
            spark_x = 30 + (spark % 10) * 9
            spark_y = -10 + spark_progress * 130
            spark_alpha = int(200 * (1 - spark_progress))
            
            if spark_alpha > 30 and spark_y < 110:
                spark_colors = [(255, 50, 100), (255, 200, 50), (100, 150, 255)]
                spark_color = spark_colors[spark % 3]
                pygame.draw.circle(s, (*spark_color, spark_alpha), (spark_x, int(spark_y)), 2)
        
        return s
    
    elif model_style == "stalker_ex4":
        # 迷幻漩涡 - 催眠螺旋
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 多层旋转螺旋
        spiral_layers = 6
        for layer in range(spiral_layers):
            layer_rotation = t * (1 + layer * 0.3)
            layer_radius_start = 5 + layer * 8
            
            # 螺旋线
            spiral_points = []
            segments = 30
            for seg in range(segments):
                seg_prog = seg / segments
                seg_angle = layer_rotation + seg_prog * math.pi * 6
                seg_radius = layer_radius_start + seg_prog * 30
                sx = 60 + int(math.cos(seg_angle) * seg_radius)
                sy = 50 + int(math.sin(seg_angle) * seg_radius)
                spiral_points.append((sx, sy))
            
            # 颜色渐变（紫色到青色）
            for i in range(len(spiral_points) - 1):
                color_prog = i / len(spiral_points)
                r = int(255 * (1 - color_prog))
                g = int(100 + 155 * color_prog)
                b = 255
                alpha = int(180 - layer * 25)
                
                if alpha > 30:
                    spiral_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(spiral_surf, (r, g, b, alpha),
                                   spiral_points[i], spiral_points[i + 1], 3)
                    s.blit(spiral_surf, (0, 0))
        
        # 催眠环
        ring_count = 8
        for ring in range(ring_count):
            ring_progress = (t + ring * 0.2) % 1
            ring_radius = int(10 + ring_progress * 45)
            ring_alpha = int(200 * (1 - ring_progress))
            
            if ring_alpha > 30:
                ring_hue = (ring / ring_count + t * 0.3) % 1
                if ring_hue < 0.5:
                    ring_color = (255, int(255 * ring_hue * 2), 255)
                else:
                    ring_color = (int(255 * (1 - (ring_hue - 0.5) * 2)), 255, 255)
                
                ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(ring_surf, (*ring_color, ring_alpha), (60, 50), ring_radius, 2)
                s.blit(ring_surf, (0, 0))
        
        return s
    
    elif model_style == "gaia_ex4":
        # 万花筒梦境 - 镜像迷宫
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 万花筒对称（6重对称）
        symmetry = 6
        for sym in range(symmetry):
            base_angle = sym * math.pi * 2 / symmetry + t
            
            # 对称图案元素
            for element in range(5):
                elem_dist = 15 + element * 8
                elem_angle = base_angle + element * 0.5
                ex = 60 + int(math.cos(elem_angle) * elem_dist)
                ey = 50 + int(math.sin(elem_angle) * elem_dist)
                
                # 颜色循环
                color_index = (sym + element) % 3
                if color_index == 0:
                    elem_color = (255, 180, 100)
                elif color_index == 1:
                    elem_color = (100, 180, 255)
                else:
                    elem_color = (180, 255, 100)
                
                elem_size = 6 - element
                pygame.draw.circle(s, elem_color, (ex, ey), elem_size)
                
                # 连接到中心
                line_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(line_surf, (*elem_color, 150), (60, 50), (ex, ey), 1)
                s.blit(line_surf, (0, 0))
        
        # 旋转的几何形状
        shape_rotation = t * 2
        shape_sides = 6
        shape_radius = 20
        shape_points = []
        for i in range(shape_sides):
            angle = shape_rotation + i * math.pi * 2 / shape_sides
            px = 60 + int(math.cos(angle) * shape_radius)
            py = 50 + int(math.sin(angle) * shape_radius)
            shape_points.append((px, py))
        
        if len(shape_points) > 2:
            pygame.draw.polygon(s, (200, 200, 255, 180), shape_points, 3)
        
        return s
    
    elif model_style == "weaver_ex4":
        # 波动艺术 - 声波可视
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 波形（类似音频波形）
        waveforms = 4
        for wave in range(waveforms):
            wave_y_base = 30 + wave * 20
            wave_points = []
            
            for x in range(120):
                # 多重频率叠加
                y_offset = 0
                y_offset += 8 * math.sin((x / 10 + t * 3) * math.pi)
                y_offset += 4 * math.sin((x / 5 + t * 5) * math.pi * 2)
                y_offset += 2 * math.sin((x / 3 + t * 7) * math.pi * 3)
                
                y = int(wave_y_base + y_offset)
                wave_points.append((x, y))
            
            # 颜色渐变
            if wave == 0:
                wave_color = (100, 255, 150)
            elif wave == 1:
                wave_color = (255, 150, 100)
            elif wave == 2:
                wave_color = (150, 100, 255)
            else:
                wave_color = (255, 255, 100)
            
            if len(wave_points) > 1:
                wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.lines(wave_surf, (*wave_color, 200), False, wave_points, 2)
                s.blit(wave_surf, (0, 0))
        
        # 频率指示器
        for freq_bar in range(10):
            bar_x = 20 + freq_bar * 10
            bar_height = int(20 + 20 * abs(math.sin(t * 4 + freq_bar * 0.5)))
            bar_rect = pygame.Rect(bar_x, 90 - bar_height, 6, bar_height)
            
            bar_color_val = int(100 + 155 * abs(math.sin(t * 3 + freq_bar)))
            pygame.draw.rect(s, (100, bar_color_val, 255), bar_rect)
        
        return s
    
    elif model_style == "solar_ex4":
        # 极光风暴 - 磁暴舞曲
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 极光带（波动的彩色丝带）
        aurora_bands = 5
        for band in range(aurora_bands):
            band_y_base = 30 + band * 15
            band_points = []
            
            for x in range(0, 121, 3):
                wave_y = band_y_base + int(15 * math.sin((x / 15 + t * 2 + band) * math.pi))
                band_points.append((x, wave_y))
            
            # 极光颜色（绿到紫渐变）
            band_prog = band / aurora_bands
            if band_prog < 0.33:
                band_r = int(255 * band_prog / 0.33)
                band_g = 255
                band_b = 150
            elif band_prog < 0.67:
                band_r = 255
                band_g = int(255 * (1 - (band_prog - 0.33) / 0.34))
                band_b = int(150 + 105 * (band_prog - 0.33) / 0.34)
            else:
                band_r = int(255 * (1 - (band_prog - 0.67) / 0.33))
                band_g = 150
                band_b = 255
            
            # 绘制极光带（带透明度）
            for i in range(len(band_points) - 1):
                aurora_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                alpha = int(180 + 75 * math.sin(t * 3 + i * 0.1 + band))
                pygame.draw.line(aurora_surf, (band_r, band_g, band_b, alpha),
                               band_points[i], band_points[i + 1], 4)
                s.blit(aurora_surf, (0, 0))
        
        # 磁场粒子
        for particle in range(40):
            p_angle = particle * 0.3 + t * 2
            p_dist = 20 + int(15 * math.sin(t * 3 + particle * 0.2))
            px = 60 + int(math.cos(p_angle) * p_dist)
            py = 50 + int(math.sin(p_angle) * p_dist)
            
            p_colors = [(0, 255, 150), (150, 0, 255), (255, 150, 0)]
            p_color = p_colors[particle % 3]
            pygame.draw.circle(s, p_color, (px, py), 2)
        
        return s
    
    elif model_style == "arbiter_ex4":
        # 水墨丹青 - 墨滴扩散
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 墨滴扩散（从中心）
        ink_drops = 6
        for drop in range(ink_drops):
            drop_progress = ((t + drop * 0.3) % 1.5) / 1.5
            
            if drop_progress < 1:
                # 墨迹边缘（不规则）
                ink_points = []
                segments = 20
                for seg in range(segments):
                    seg_angle = seg * math.pi * 2 / segments
                    # 不规则边缘
                    radius_var = 1 + 0.3 * math.sin(seg * 2 + drop * 3)
                    ink_radius = drop_progress * 40 * radius_var
                    ix = 60 + int(math.cos(seg_angle) * ink_radius)
                    iy = 50 + int(math.sin(seg_angle) * ink_radius)
                    ink_points.append((ix, iy))
                
                # 墨色渐变（深到浅）
                ink_darkness = int(80 * (1 - drop_progress * 0.7))
                ink_alpha = int(200 * (1 - drop_progress))
                
                if ink_alpha > 20 and len(ink_points) > 2:
                    ink_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.polygon(ink_surf, (ink_darkness, ink_darkness, ink_darkness + 30, ink_alpha),
                                      ink_points)
                    s.blit(ink_surf, (0, 0))
        
        # 笔触（飘逸的线条）
        for stroke in range(4):
            stroke_angle = stroke * math.pi / 2 + t * 0.5
            stroke_points = []
            
            for seg in range(8):
                seg_prog = seg / 8
                seg_dist = 15 + seg_prog * 25
                seg_angle = stroke_angle + math.sin(t * 2 + seg) * 0.3
                sx = 60 + int(math.cos(seg_angle) * seg_dist)
                sy = 50 + int(math.sin(seg_angle) * seg_dist)
                stroke_points.append((sx, sy))
            
            # 绘制笔触
            for i in range(len(stroke_points) - 1):
                width = int(5 * (1 - i / len(stroke_points)))
                alpha = int(180 * (1 - i / len(stroke_points)))
                if alpha > 30:
                    stroke_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(stroke_surf, (50, 50, 80, alpha),
                                   stroke_points[i], stroke_points[i + 1], width)
                    s.blit(stroke_surf, (0, 0))
        
        return s
    
    elif model_style == "eclipse_ex4":
        # 霓虹都市 - 赛博脉动
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 霓虹灯管（垂直线条）
        neon_tubes = 12
        for tube in range(neon_tubes):
            tube_x = 15 + tube * 9
            tube_height = int(40 + 30 * abs(math.sin(t * 3 + tube * 0.5)))
            tube_y_start = 55 - tube_height // 2
            
            # 霓虹颜色交替
            if tube % 3 == 0:
                neon_color = (255, 0, 150)
            elif tube % 3 == 1:
                neon_color = (0, 255, 200)
            else:
                neon_color = (255, 200, 0)
            
            # 闪烁效果
            if (int(t * 10) + tube) % 6 < 5:
                # 外发光
                for glow in range(3, 0, -1):
                    glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    glow_alpha = int(180 - glow * 50)
                    pygame.draw.line(glow_surf, (*neon_color, glow_alpha),
                                   (tube_x, tube_y_start),
                                   (tube_x, tube_y_start + tube_height),
                                   glow * 2)
                    s.blit(glow_surf, (0, 0))
                
                # 核心
                pygame.draw.line(s, (255, 255, 255),
                               (tube_x, tube_y_start),
                               (tube_x, tube_y_start + tube_height), 2)
        
        # 赛博网格
        grid_lines = 8
        for grid in range(grid_lines):
            grid_y = 20 + grid * 12
            grid_alpha = int(100 + 100 * abs(math.sin(t * 2 + grid)))
            grid_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(grid_surf, (0, 255, 200, grid_alpha),
                           (10, grid_y), (110, grid_y), 1)
            s.blit(grid_surf, (0, 0))
        
        # 数据流粒子
        for data in range(20):
            data_progress = (t * 2 + data * 0.15) % 1
            data_x = 20 + int(data_progress * 80)
            data_y = 30 + (data % 5) * 15
            data_alpha = int(220 * (1 - abs(data_progress - 0.5) * 2))
            
            if data_alpha > 30:
                data_color = (255, 0, 150) if data % 2 == 0 else (0, 255, 200)
                pygame.draw.circle(s, (*data_color, data_alpha), (data_x, data_y), 2)
        
        return s
    
    elif model_style == "prism_ex4":
        # 油画笔触 - 印象流动
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 厚重笔触（梵高风格旋转）
        brush_strokes = 20
        for stroke in range(brush_strokes):
            stroke_angle = (stroke / brush_strokes) * math.pi * 2 + t * 0.5
            stroke_dist = 10 + (stroke % 4) * 10
            
            # 笔触中心
            stroke_cx = 60 + int(math.cos(stroke_angle) * stroke_dist)
            stroke_cy = 50 + int(math.sin(stroke_angle) * stroke_dist)
            
            # 笔触形状（短线段）
            stroke_length = 12
            stroke_dir = stroke_angle + math.pi / 2 + math.sin(t * 2 + stroke) * 0.5
            stroke_x1 = stroke_cx - int(math.cos(stroke_dir) * stroke_length / 2)
            stroke_y1 = stroke_cy - int(math.sin(stroke_dir) * stroke_length / 2)
            stroke_x2 = stroke_cx + int(math.cos(stroke_dir) * stroke_length / 2)
            stroke_y2 = stroke_cy + int(math.sin(stroke_dir) * stroke_length / 2)
            
            # 油画色彩（暖色调）
            color_var = (stroke / brush_strokes + t * 0.2) % 1
            if color_var < 0.33:
                stroke_color = (200, int(150 + 105 * color_var / 0.33), 100)
            elif color_var < 0.67:
                stroke_color = (int(200 - 100 * (color_var - 0.33) / 0.34), 255, 100)
            else:
                stroke_color = (100, int(255 - 105 * (color_var - 0.67) / 0.33), 200)
            
            # 绘制厚重笔触
            for layer in range(3):
                stroke_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                layer_alpha = 200 - layer * 50
                pygame.draw.line(stroke_surf, (*stroke_color, layer_alpha),
                               (stroke_x1, stroke_y1), (stroke_x2, stroke_y2), 5 - layer)
                s.blit(stroke_surf, (0, 0))
        
        # 旋转星空效果（中心）
        for star in range(15):
            star_angle = star * 0.8 + t * 2
            star_dist = 10 + int(15 * math.sin(t + star))
            star_x = 60 + int(math.cos(star_angle) * star_dist)
            star_y = 50 + int(math.sin(star_angle) * star_dist)
            
            star_brightness = int(150 + 105 * abs(math.sin(t * 3 + star)))
            pygame.draw.circle(s, (star_brightness, star_brightness, 200), (star_x, star_y), 3)
        
        return s
    
    elif model_style == "necro_ex4":
        # 黑洞漩涡 - 引力舞蹈
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 黑洞中心（纯黑）
        event_horizon = 12
        for layer in range(5, 0, -1):
            layer_radius = int(event_horizon * (layer / 5))
            layer_darkness = int(100 * (1 - layer / 5))
            pygame.draw.circle(s, (layer_darkness // 3, 0, layer_darkness),
                             (60, 50), layer_radius)
        
        # 吸积盘（螺旋向内）
        accretion_particles = 40
        for particle in range(accretion_particles):
            p_angle = particle * 0.5 + t * 3
            p_progress = (t + particle * 0.05) % 1
            # 螺旋向内
            p_dist = 50 * (1 - p_progress) + event_horizon
            px = 60 + int(math.cos(p_angle) * p_dist)
            py = 50 + int(math.sin(p_angle) * p_dist * 0.3)  # 扁平化
            
            # 颜色：外围蓝->内部红（温度）
            if p_progress < 0.3:
                p_color = (100, 100, 255)
            elif p_progress < 0.6:
                p_color = (200, 150, 255)
            else:
                p_color = (255, int(150 * (1 - p_progress)), 100)
            
            p_alpha = int(220 * (1 - p_progress * 0.5))
            p_size = int(4 * (1 - p_progress)) + 1
            
            if p_alpha > 30:
                pygame.draw.circle(s, (*p_color, p_alpha), (px, py), p_size)
        
        # 引力透镜（光线弯曲）
        lens_rings = 5
        for ring in range(lens_rings):
            ring_radius = event_horizon + 10 + ring * 8
            ring_alpha = int(150 - ring * 25)
            
            # 扭曲的环
            ring_points = []
            for i in range(16):
                ring_angle = i * math.pi / 8 + t
                distortion = 5 * math.sin(t * 2 + i + ring)
                rx = 60 + int(math.cos(ring_angle) * (ring_radius + distortion))
                ry = 50 + int(math.sin(ring_angle) * (ring_radius + distortion))
                ring_points.append((rx, ry))
            
            if ring_alpha > 20 and len(ring_points) > 2:
                lens_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.lines(lens_surf, (100, 0, 150, ring_alpha), True, ring_points, 2)
                s.blit(lens_surf, (0, 0))
        
        # 霍金辐射
        for radiation in range(12):
            rad_angle = radiation * 0.5 + t * 4
            rad_progress = (t * 2 + radiation * 0.2) % 1
            rad_dist = event_horizon + 3 + rad_progress * 35
            rad_x = 60 + int(math.cos(rad_angle) * rad_dist)
            rad_y = 50 + int(math.sin(rad_angle) * rad_dist)
            rad_alpha = int(200 * (1 - rad_progress))
            
            if rad_alpha > 30:
                pygame.draw.circle(s, (150, 100, 200, rad_alpha), (rad_x, rad_y), 2)
        
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
    
    print('✅ 成功添加最后9个超级动态渲染代码!')
    print('🎨 包含: 烟火绽放、迷幻漩涡、万花筒、波动艺术、极光风暴、')
    print('       水墨丹青、霓虹都市、油画笔触、黑洞漩涡')
    print('🎉 第四批全部16个_ex4涂装渲染代码已完成!')
else:
    print('未找到插入位置')
