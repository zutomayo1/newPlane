# 添加第二批4个_ex5渲染代码（魔法阵、故障艺术、折纸、弹幕地狱）

render_code = '''
        elif model_style == "viper_ex5":  # 魔法阵召唤·炼金术
            t = ticks * 0.001
            
            # 外圈魔法阵
            for ring in range(3):
                ring_radius = 30 - ring * 8
                ring_rotation = t * (1 + ring * 0.5) * (-1 if ring % 2 else 1)
                
                # 魔法阵圆环
                pygame.draw.circle(plane_surf, (200, 150, 255), center, ring_radius, 2)
                
                # 符文符号（用几何图形表示）
                rune_count = 6 + ring * 2
                for i in range(rune_count):
                    angle = ring_rotation + (i / rune_count) * 2 * math.pi
                    rx = center[0] + math.cos(angle) * ring_radius
                    ry = center[1] + math.sin(angle) * ring_radius
                    
                    # 绘制符文（三角形或菱形）
                    if i % 2 == 0:
                        points = [(rx, ry - 4), (rx - 3, ry + 2), (rx + 3, ry + 2)]
                        pygame.draw.polygon(plane_surf, (255, 200, 100), points)
                    else:
                        points = [(rx, ry - 3), (rx + 3, ry), (rx, ry + 3), (rx - 3, ry)]
                        pygame.draw.polygon(plane_surf, (100, 255, 150), points)
            
            # 中心炼金符号
            center_size = int(8 + abs(math.sin(t * 2)) * 5)
            pygame.draw.circle(plane_surf, (255, 200, 100), center, center_size)
            pygame.draw.circle(plane_surf, (200, 150, 255), center, center_size, 2)
            
            # 召唤粒子从天而降
            for i in range(15):
                fall_phase = (t * 2 + i * 0.2) % 1.0
                px = center[0] + math.sin(t + i) * 25
                py = center[1] - 35 + fall_phase * 70
                particle_color = (200 + int(55 * math.sin(t + i)), 150, 255)
                pygame.draw.circle(plane_surf, particle_color, (int(px), int(py)), 3)

        elif model_style == "specter_ex5":  # 故障艺术·系统崩溃
            t = ticks * 0.001
            glitch_intensity = abs(math.sin(t * 3))
            
            # RGB通道分离
            offset = int(glitch_intensity * 8)
            for i in range(3):
                shift_x = offset * (i - 1)
                shift_y = offset * (2 - i) if i % 2 else -offset
                
                # 绘制分离的色块
                for j in range(8):
                    block_angle = t + j * 0.785
                    block_radius = 15 + j * 2
                    bx = center[0] + math.cos(block_angle) * block_radius + shift_x
                    by = center[1] + math.sin(block_angle) * block_radius + shift_y
                    
                    if i == 0:
                        color = (255, 0, 0)
                    elif i == 1:
                        color = (0, 255, 0)
                    else:
                        color = (0, 0, 255)
                    
                    pygame.draw.rect(plane_surf, color, (bx - 4, by - 4, 8, 8))
            
            # 画面撕裂线
            if glitch_intensity > 0.7:
                for i in range(5):
                    tear_y = center[1] - 20 + i * 10
                    tear_offset = int(glitch_intensity * 15 * math.sin(t * 10 + i))
                    pygame.draw.line(plane_surf, (255, 255, 255), 
                                   (center[0] - 30 + tear_offset, tear_y), 
                                   (center[0] + 30 + tear_offset, tear_y), 2)
            
            # 数字乱码粒子
            for i in range(20):
                noise_x = center[0] + (hash((i, int(t * 10))) % 60) - 30
                noise_y = center[1] + (hash((i + 100, int(t * 10))) % 60) - 30
                noise_color = (255, 255, 255) if hash((i, int(t * 5))) % 2 else (0, 0, 0)
                pygame.draw.rect(plane_surf, noise_color, (noise_x, noise_y, 2, 2))

        elif model_style == "aurora_ex5":  # 折纸艺术·千纸鹤
            t = ticks * 0.001
            
            # 纸鹤轮廓（简化版）
            for crane_idx in range(6):
                angle = t + crane_idx * 1.047
                distance = 20 + abs(math.sin(t + crane_idx)) * 10
                crane_x = center[0] + math.cos(angle) * distance
                crane_y = center[1] + math.sin(angle) * distance
                
                crane_size = 8
                crane_color = (255, 180 + crane_idx * 10, 180 + crane_idx * 10)
                
                # 纸鹤身体（三角形）
                body_points = [
                    (crane_x, crane_y - crane_size),
                    (crane_x - crane_size, crane_y + crane_size//2),
                    (crane_x + crane_size, crane_y + crane_size//2)
                ]
                pygame.draw.polygon(plane_surf, crane_color, body_points, 2)
                
                # 翅膀（两个小三角形）
                wing1_points = [
                    (crane_x - crane_size//2, crane_y),
                    (crane_x - crane_size * 1.5, crane_y - crane_size//2),
                    (crane_x - crane_size, crane_y + crane_size//2)
                ]
                pygame.draw.polygon(plane_surf, crane_color, wing1_points, 1)
                
                wing2_points = [
                    (crane_x + crane_size//2, crane_y),
                    (crane_x + crane_size * 1.5, crane_y - crane_size//2),
                    (crane_x + crane_size, crane_y + crane_size//2)
                ]
                pygame.draw.polygon(plane_surf, crane_color, wing2_points, 1)
            
            # 折痕线动画
            for i in range(8):
                fold_angle = t * 2 + i * 0.393
                fold_radius = 25
                fx1 = center[0] + math.cos(fold_angle) * fold_radius
                fy1 = center[1] + math.sin(fold_angle) * fold_radius
                fx2 = center[0] - math.cos(fold_angle) * fold_radius
                fy2 = center[1] - math.sin(fold_angle) * fold_radius
                pygame.draw.line(plane_surf, (200, 200, 200), (fx1, fy1), (fx2, fy2), 1)

        elif model_style == "crimson_ex5":  # 弹幕地狱·东方幻想
            t = ticks * 0.001
            
            # 弹幕图案1：圆形扩散
            pattern1_count = 16
            for i in range(pattern1_count):
                angle = (t * 2) + (i / pattern1_count) * 2 * math.pi
                bullet_phase = (t * 1.5) % 1.0
                radius = 10 + bullet_phase * 25
                bx = center[0] + math.cos(angle) * radius
                by = center[1] + math.sin(angle) * radius
                bullet_color = (255, 100 + int(100 * bullet_phase), 150)
                pygame.draw.circle(plane_surf, bullet_color, (int(bx), int(by)), 2)
            
            # 弹幕图案2：螺旋弹幕
            for i in range(30):
                spiral_angle = t * 3 + i * 0.3
                spiral_radius = 5 + i * 0.8
                sx = center[0] + math.cos(spiral_angle) * spiral_radius
                sy = center[1] + math.sin(spiral_angle) * spiral_radius
                spiral_color = (150, 100, 255)
                pygame.draw.circle(plane_surf, spiral_color, (int(sx), int(sy)), 2)
            
            # 弹幕图案3：十字弹幕
            cross_phase = (t * 2) % 1.0
            for direction in range(4):
                angle = direction * 1.571  # 90度间隔
                for j in range(5):
                    bullet_dist = 10 + (cross_phase + j * 0.2) * 20
                    cx = center[0] + math.cos(angle) * bullet_dist
                    cy = center[1] + math.sin(angle) * bullet_dist
                    pygame.draw.circle(plane_surf, (100, 255, 150), (int(cx), int(cy)), 3)
'''

# 读取utils.py
with open('utils.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到thunderbird_ex5的结尾
insert_marker = '''        elif model_style == "thunderbird_ex5":  # 音游节奏·下落天堂
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
                    pygame.draw.circle(plane_surf, (255, 255, 100), (int(note_x), int(center[1] + 25)), perfect_size, 2)'''

# 插入新代码
new_content = content.replace(insert_marker, insert_marker + render_code)

# 写回文件
with open('utils.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('✅ 成功添加第二批4个_ex5渲染代码!')
print('🎮 包含: 魔法阵召唤、故障艺术、折纸艺术、弹幕地狱')
