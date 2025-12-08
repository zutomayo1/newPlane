# 添加前4个_ex5渲染代码（像素进化、表情包、几何变形、音游节奏）

render_code = '''
        elif model_style == "striker_ex5":  # 像素进化·8bit回忆
            t = ticks * 0.001
            pixel_size = int(abs(math.sin(t * 0.5)) * 15) + 3
            
            # 像素化效果
            for py in range(0, plane_size[1], pixel_size):
                for px in range(0, plane_size[0], pixel_size):
                    color_phase = (px + py + t * 50) / 50.0
                    r = int(128 + 127 * math.sin(color_phase))
                    g = int(128 + 127 * math.sin(color_phase + 2.094))
                    b = int(128 + 127 * math.sin(color_phase + 4.189))
                    pygame.draw.rect(plane_surf, (r, g, b), (px, py, pixel_size, pixel_size))
            
            # 像素方块重组动画
            for i in range(25):
                angle = t * 2 + i * 0.25
                radius = 20 + math.sin(t + i * 0.5) * 10
                block_x = center[0] + math.cos(angle) * radius
                block_y = center[1] + math.sin(angle) * radius
                block_size = int(abs(math.sin(t * 2 + i)) * 8) + 4
                block_color = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)][i % 4]
                pygame.draw.rect(plane_surf, block_color, (block_x - block_size//2, block_y - block_size//2, block_size, block_size), 2)

        elif model_style == "phantom_ex5":  # 表情包战士·颜文字
            t = ticks * 0.001
            emojis = ['(｡◕‿◕｡)', '(╯°□°）╯', '(￣▽￣)', '(｡･ω･｡)', '(>_<)', '(^_^)']
            
            # 绘制文字表情（用简单图形模拟）
            for i, emoji_idx in enumerate([0, 1, 2, 3, 4, 5]):
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
                if emoji_idx % 3 == 0:  # 笑脸
                    pygame.draw.arc(plane_surf, emoji_color, (ex - face_size//2, ey, face_size, face_size//2), 0, 3.14, 2)
                elif emoji_idx % 3 == 1:  # 生气
                    pygame.draw.line(plane_surf, emoji_color, (ex - face_size//2, ey + face_size//3), (ex + face_size//2, ey + face_size//3), 2)
                else:  # 惊讶
                    pygame.draw.circle(plane_surf, emoji_color, (int(ex), int(ey + face_size//3)), face_size//4, 2)

        elif model_style == "titan_ex5":  # 几何变形·欧几里得
            t = ticks * 0.001
            morph_phase = t % 4.0  # 4秒一个循环
            
            # 计算当前形状（0=三角形，1=正方形，2=五边形，3=圆形）
            shape_idx = int(morph_phase)
            transition = morph_phase - shape_idx
            
            for layer in range(4):
                radius = 25 - layer * 5
                rotation = t + layer * 0.5
                alpha = 255 - layer * 50
                
                if shape_idx == 0:  # 三角形
                    sides = 3
                elif shape_idx == 1:  # 正方形
                    sides = 4
                elif shape_idx == 2:  # 五边形
                    sides = 5
                else:  # 圆形（多边形近似）
                    sides = 20
                
                # 绘制多边形
                points = []
                for i in range(sides):
                    angle = rotation + (i / sides) * 2 * math.pi
                    px = center[0] + math.cos(angle) * radius
                    py = center[1] + math.sin(angle) * radius
                    points.append((px, py))
                
                if len(points) >= 3:
                    color_phase = t + layer * 0.5
                    r = int(128 + 127 * math.sin(color_phase))
                    g = int(128 + 127 * math.sin(color_phase + 2.094))
                    b = int(128 + 127 * math.sin(color_phase + 4.189))
                    pygame.draw.polygon(plane_surf, (r, g, b), points, 2)

        elif model_style == "thunderbird_ex5":  # 音游节奏·下落天堂
            t = ticks * 0.001
            
            # 轨道线
            track_count = 4
            track_width = 40
            for i in range(track_count):
                track_x = center[0] - track_width * 1.5 + i * track_width
                pygame.draw.line(plane_surf, (100, 100, 150), (track_x, center[1] - 30), (track_x, center[1] + 30), 1)
            
            # 下落音符
            for i in range(12):
                note_phase = (t * 3 + i * 0.3) % 1.0
                track_idx = i % track_count
                note_x = center[0] - track_width * 1.5 + track_idx * track_width
                note_y = center[1] - 30 + note_phase * 60
                
                # 音符类型
                note_type = i % 3
                if note_type == 0:  # 单点
                    note_color = (255, 100, 150)
                    pygame.draw.circle(plane_surf, note_color, (int(note_x), int(note_y)), 4)
                elif note_type == 1:  # 长条
                    note_color = (100, 255, 150)
                    pygame.draw.rect(plane_surf, note_color, (note_x - 3, note_y, 6, 15))
                else:  # 滑条
                    note_color = (150, 100, 255)
                    pygame.draw.polygon(plane_surf, note_color, [(note_x, note_y), (note_x - 5, note_y + 8), (note_x + 5, note_y + 8)])
                
                # Perfect判定特效
                if 0.85 < note_phase < 0.95:
                    perfect_size = int((0.95 - note_phase) * 100)
                    pygame.draw.circle(plane_surf, (255, 255, 100), (int(note_x), int(center[1] + 25)), perfect_size, 2)
'''

# 读取utils.py
with open('utils.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在necro_ex4后面插入新渲染代码
insert_marker = '''        elif model_style == "necro_ex4":  # 黑洞漩涡·引力舞蹈
            t = ticks * 0.001
            
            # 黑洞中心
            for i in range(5):
                core_radius = 3 + i * 2
                core_alpha = 255 - i * 40
                core_color = (50 + i * 10, 0, 100 + i * 10)
                pygame.draw.circle(plane_surf, core_color, center, core_radius, 1)
            
            # 螺旋吸积盘
            for i in range(40):
                angle = t * 2 + i * 0.157
                radius = 15 + i * 0.8
                spiral_x = center[0] + math.cos(angle) * radius
                spiral_y = center[1] + math.sin(angle) * radius
                
                distance_factor = radius / 47.0
                r = int(50 + 150 * distance_factor)
                g = 0
                b = int(100 + 100 * distance_factor)
                
                particle_size = int(3 - distance_factor * 2)
                pygame.draw.circle(plane_surf, (r, g, b), (int(spiral_x), int(spiral_y)), max(1, particle_size))
            
            # 引力透镜环
            for ring_idx in range(5):
                lens_radius = 25 + ring_idx * 5
                lens_strength = abs(math.sin(t + ring_idx * 0.5))
                distorted_radius = lens_radius * (1 + lens_strength * 0.3)
                ring_color = (80 + ring_idx * 20, 0, 120 + ring_idx * 10)
                pygame.draw.circle(plane_surf, ring_color, center, int(distorted_radius), 1)
            
            # 霍金辐射粒子
            for i in range(12):
                radiation_angle = t * 3 + i * 0.524
                radiation_distance = 35 + abs(math.sin(t * 2 + i)) * 10
                rx = center[0] + math.cos(radiation_angle) * radiation_distance
                ry = center[1] + math.sin(radiation_angle) * radiation_distance
                pygame.draw.circle(plane_surf, (200, 200, 255), (int(rx), int(ry)), 2)'''

# 插入新代码
new_content = content.replace(insert_marker, insert_marker + render_code)

# 写回文件
with open('utils.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('✅ 成功添加前4个_ex5渲染代码!')
print('🎮 包含: 像素进化、表情包战士、几何变形、音游节奏')
