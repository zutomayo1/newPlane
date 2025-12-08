# 添加最后8个_ex5渲染代码

render_code = '''
        elif model_style == "stalker_ex5":  # 时钟齿轮·蒸汽朋克
            t = ticks * 0.001
            
            # 大齿轮
            for gear_idx in range(3):
                gear_radius = 25 - gear_idx * 8
                gear_rotation = t * (1 + gear_idx * 0.5) * (-1 if gear_idx % 2 else 1)
                teeth_count = 12 - gear_idx * 2
                
                # 齿轮主体
                gear_color = (180 + gear_idx * 20, 140 + gear_idx * 20, 100 + gear_idx * 10)
                pygame.draw.circle(plane_surf, gear_color, center, gear_radius, 2)
                
                # 齿轮齿
                for i in range(teeth_count):
                    tooth_angle = gear_rotation + (i / teeth_count) * 2 * math.pi
                    inner_x = center[0] + math.cos(tooth_angle) * (gear_radius - 3)
                    inner_y = center[1] + math.sin(tooth_angle) * (gear_radius - 3)
                    outer_x = center[0] + math.cos(tooth_angle) * (gear_radius + 3)
                    outer_y = center[1] + math.sin(tooth_angle) * (gear_radius + 3)
                    pygame.draw.line(plane_surf, gear_color, (inner_x, inner_y), (outer_x, outer_y), 2)
            
            # 钟表指针
            for hand_idx in range(3):
                hand_length = 20 - hand_idx * 5
                hand_speed = 1 + hand_idx * 2
                hand_angle = t * hand_speed - 1.571  # -90度起始
                hand_x = center[0] + math.cos(hand_angle) * hand_length
                hand_y = center[1] + math.sin(hand_angle) * hand_length
                hand_color = (220, 180, 120)
                pygame.draw.line(plane_surf, hand_color, center, (hand_x, hand_y), 3 - hand_idx)
            
            # 蒸汽粒子
            for i in range(15):
                steam_phase = (t + i * 0.2) % 1.5
                steam_x = center[0] + math.sin(t + i) * 20
                steam_y = center[1] + 25 - steam_phase * 50
                steam_size = int(3 + steam_phase * 4)
                steam_alpha = int(255 * (1 - steam_phase / 1.5))
                steam_color = (200, 200, 200)
                pygame.draw.circle(plane_surf, steam_color, (int(steam_x), int(steam_y)), steam_size, 1)

        elif model_style == "gaia_ex5":  # DNA螺旋·生命密码
            t = ticks * 0.001
            
            # 双螺旋结构
            helix_length = 40
            helix_radius = 12
            for i in range(30):
                z = (i / 30.0) * helix_length - helix_length / 2
                angle1 = t + i * 0.3
                angle2 = angle1 + math.pi
                
                # 第一条螺旋
                x1 = center[0] + z * 0.5 + math.cos(angle1) * helix_radius
                y1 = center[1] + math.sin(angle1) * helix_radius
                helix1_color = (100, 255, 150)
                pygame.draw.circle(plane_surf, helix1_color, (int(x1), int(y1)), 3)
                
                # 第二条螺旋
                x2 = center[0] + z * 0.5 + math.cos(angle2) * helix_radius
                y2 = center[1] + math.sin(angle2) * helix_radius
                helix2_color = (255, 150, 100)
                pygame.draw.circle(plane_surf, helix2_color, (int(x2), int(y2)), 3)
                
                # 碱基对连接线
                if i % 3 == 0:
                    pygame.draw.line(plane_surf, (150, 100, 255), (x1, y1), (x2, y2), 1)
            
            # 细胞分裂动画
            division_phase = (t % 2.0) / 2.0
            if division_phase < 0.5:
                cell_size = int(8 + division_phase * 20)
                pygame.draw.circle(plane_surf, (100, 255, 200), center, cell_size, 2)
            else:
                split_distance = int((division_phase - 0.5) * 30)
                pygame.draw.circle(plane_surf, (100, 255, 200), (center[0] - split_distance, center[1]), 8, 2)
                pygame.draw.circle(plane_surf, (100, 255, 200), (center[0] + split_distance, center[1]), 8, 2)

        elif model_style == "weaver_ex5":  # 棋盘游戏·策略大师
            t = ticks * 0.001
            
            # 棋盘格子
            board_size = 6
            cell_size = 8
            for row in range(board_size):
                for col in range(board_size):
                    cell_x = center[0] - (board_size * cell_size) // 2 + col * cell_size
                    cell_y = center[1] - (board_size * cell_size) // 2 + row * cell_size
                    
                    if (row + col) % 2 == 0:
                        cell_color = (220, 220, 220)
                    else:
                        cell_color = (50, 50, 50)
                    
                    pygame.draw.rect(plane_surf, cell_color, (cell_x, cell_y, cell_size, cell_size))
            
            # 国际象棋棋子（简化）
            for i in range(8):
                piece_angle = t + i * 0.785
                piece_radius = 28
                piece_x = center[0] + math.cos(piece_angle) * piece_radius
                piece_y = center[1] + math.sin(piece_angle) * piece_radius
                
                piece_type = i % 4
                if piece_type == 0:  # 王
                    pygame.draw.circle(plane_surf, (255, 215, 0), (int(piece_x), int(piece_y)), 4)
                    pygame.draw.line(plane_surf, (255, 215, 0), (piece_x, piece_y - 6), (piece_x, piece_y - 2), 2)
                elif piece_type == 1:  # 后
                    pygame.draw.circle(plane_surf, (192, 192, 192), (int(piece_x), int(piece_y)), 5)
                elif piece_type == 2:  # 车
                    pygame.draw.rect(plane_surf, (139, 69, 19), (piece_x - 4, piece_y - 4, 8, 8))
                else:  # 兵
                    pygame.draw.circle(plane_surf, (150, 150, 150), (int(piece_x), int(piece_y)), 3)
            
            # 围棋棋子
            go_positions = [(0, -15), (15, 0), (0, 15), (-15, 0)]
            for idx, (dx, dy) in enumerate(go_positions):
                go_x = center[0] + dx
                go_y = center[1] + dy
                go_color = (0, 0, 0) if idx % 2 == 0 else (255, 255, 255)
                pygame.draw.circle(plane_surf, go_color, (int(go_x), int(go_y)), 4)

        elif model_style == "solar_ex5":  # 天气预报·气象万千
            t = ticks * 0.001
            weather_cycle = int(t / 2) % 4  # 每2秒切换一次天气
            
            if weather_cycle == 0:  # 晴天
                # 太阳
                sun_size = int(10 + abs(math.sin(t * 2)) * 3)
                pygame.draw.circle(plane_surf, (255, 220, 100), center, sun_size)
                
                # 太阳光线
                for i in range(8):
                    ray_angle = t + i * 0.785
                    ray_length = 20 + abs(math.sin(t * 3 + i)) * 8
                    ray_x = center[0] + math.cos(ray_angle) * ray_length
                    ray_y = center[1] + math.sin(ray_angle) * ray_length
                    pygame.draw.line(plane_surf, (255, 220, 100), center, (ray_x, ray_y), 2)
            
            elif weather_cycle == 1:  # 雨天
                for i in range(25):
                    rain_phase = (t * 5 + i * 0.1) % 1.0
                    rain_x = center[0] + (i % 5 - 2) * 10
                    rain_y = center[1] - 25 + rain_phase * 50
                    pygame.draw.line(plane_surf, (100, 180, 255), 
                                   (rain_x, rain_y), (rain_x - 2, rain_y + 6), 2)
            
            elif weather_cycle == 2:  # 雪天
                for i in range(20):
                    snow_phase = (t * 2 + i * 0.15) % 1.0
                    snow_x = center[0] + math.sin(t + i) * 25
                    snow_y = center[1] - 25 + snow_phase * 50
                    
                    # 雪花（6个分支）
                    for branch in range(6):
                        branch_angle = (branch / 6.0) * 2 * math.pi
                        bx = snow_x + math.cos(branch_angle) * 3
                        by = snow_y + math.sin(branch_angle) * 3
                        pygame.draw.line(plane_surf, (200, 200, 200), (snow_x, snow_y), (bx, by), 1)
            
            else:  # 雷暴
                # 闪电
                if int(t * 10) % 3 == 0:
                    for i in range(5):
                        lightning_x = center[0] + (i - 2) * 8
                        lightning_y1 = center[1] - 20 + i * 8
                        lightning_y2 = lightning_y1 + 8
                        pygame.draw.line(plane_surf, (255, 255, 100), 
                                       (lightning_x, lightning_y1), (lightning_x + 5, lightning_y2), 2)

        elif model_style == "arbiter_ex5":  # 星座连线·黄道十二宫
            t = ticks * 0.001
            constellation_idx = int(t / 3) % 12
            
            # 星座星星位置（简化版）
            constellations = [
                [(0, -20), (10, -15), (-10, -10), (0, 0)],  # 白羊座
                [(0, -15), (15, -10), (15, 5), (0, 10), (-15, 5), (-15, -10)],  # 金牛座
                [(-10, -15), (10, -15), (10, 0), (-10, 0)],  # 双子座
                [(0, -15), (10, -5), (10, 5), (0, 15), (-10, 5), (-10, -5)],  # 巨蟹座
            ]
            
            current_constellation = constellations[constellation_idx % len(constellations)]
            
            # 绘制星星
            for idx, (dx, dy) in enumerate(current_constellation):
                star_x = center[0] + dx
                star_y = center[1] + dy
                star_brightness = int(200 + 55 * math.sin(t * 3 + idx))
                pygame.draw.circle(plane_surf, (star_brightness, star_brightness, 200), 
                                 (int(star_x), int(star_y)), 3)
                
                # 绘制连线
                if idx > 0:
                    prev_dx, prev_dy = current_constellation[idx - 1]
                    pygame.draw.line(plane_surf, (200, 200, 255), 
                                   (center[0] + prev_dx, center[1] + prev_dy),
                                   (star_x, star_y), 1)
            
            # 星座符号环绕
            for i in range(12):
                symbol_angle = t * 0.5 + i * 0.524
                symbol_radius = 30
                sx = center[0] + math.cos(symbol_angle) * symbol_radius
                sy = center[1] + math.sin(symbol_angle) * symbol_radius
                symbol_color = (255, 255, 200) if i == constellation_idx else (150, 150, 150)
                pygame.draw.circle(plane_surf, symbol_color, (int(sx), int(sy)), 2)

        elif model_style == "eclipse_ex5":  # 漫画分镜·速度线
            t = ticks * 0.001
            
            # 速度线（集中线）
            for i in range(24):
                angle = (i / 24.0) * 2 * math.pi
                speed_length = 25 + abs(math.sin(t * 2 + i)) * 15
                line_start_x = center[0] + math.cos(angle) * 8
                line_start_y = center[1] + math.sin(angle) * 8
                line_end_x = center[0] + math.cos(angle) * speed_length
                line_end_y = center[1] + math.sin(angle) * speed_length
                pygame.draw.line(plane_surf, (255, 100, 100), 
                               (line_start_x, line_start_y), (line_end_x, line_end_y), 2)
            
            # 漫画爆炸泡泡
            for i in range(5):
                bubble_angle = t * 2 + i * 1.257
                bubble_radius = 20 + i * 3
                bubble_x = center[0] + math.cos(bubble_angle) * bubble_radius
                bubble_y = center[1] + math.sin(bubble_angle) * bubble_radius
                bubble_size = int(6 + abs(math.sin(t * 3 + i)) * 4)
                
                # 爆炸形状（尖刺圆）
                points = []
                for j in range(8):
                    spike_angle = (j / 8.0) * 2 * math.pi
                    spike_radius = bubble_size if j % 2 == 0 else bubble_size * 1.5
                    px = bubble_x + math.cos(spike_angle) * spike_radius
                    py = bubble_y + math.sin(spike_angle) * spike_radius
                    points.append((px, py))
                
                if len(points) >= 3:
                    pygame.draw.polygon(plane_surf, (100, 100, 255), points, 2)
            
            # 音效字模拟（用图形表示"砰"）
            if int(t * 2) % 2 == 0:
                for i in range(3):
                    text_x = center[0] + (i - 1) * 15
                    text_y = center[1] - 20
                    pygame.draw.circle(plane_surf, (255, 255, 100), (text_x, text_y), 5, 2)
                    pygame.draw.line(plane_surf, (255, 255, 100), 
                                   (text_x - 3, text_y + 5), (text_x + 3, text_y + 5), 2)

        elif model_style == "prism_ex5":  # 乐高积木·创意拼搭
            t = ticks * 0.001
            
            # 积木块堆叠
            block_colors = [(255, 50, 50), (50, 255, 50), (50, 50, 255), 
                          (255, 255, 50), (255, 50, 255), (50, 255, 255)]
            
            for layer in range(4):
                for i in range(6):
                    angle = t * 0.5 + layer * 0.785 + i * 1.047
                    radius = 15 + layer * 8
                    block_x = center[0] + math.cos(angle) * radius
                    block_y = center[1] + math.sin(angle) * radius
                    
                    block_size = 8
                    block_color = block_colors[(layer + i) % len(block_colors)]
                    
                    # 积木块主体
                    pygame.draw.rect(plane_surf, block_color, 
                                   (block_x - block_size//2, block_y - block_size//2, 
                                    block_size, block_size))
                    
                    # 积木凸起（2x2小圆点）
                    for dy in [-2, 2]:
                        for dx in [-2, 2]:
                            pygame.draw.circle(plane_surf, 
                                             tuple(max(0, c - 50) for c in block_color),
                                             (int(block_x + dx), int(block_y + dy)), 1)
            
            # 拼搭动画（积木从上方落下）
            for i in range(8):
                fall_phase = (t * 2 + i * 0.3) % 1.0
                fall_x = center[0] + math.sin(t + i) * 20
                fall_y = center[1] - 30 + fall_phase * 60
                fall_color = block_colors[i % len(block_colors)]
                fall_size = 6
                pygame.draw.rect(plane_surf, fall_color, 
                               (fall_x - fall_size//2, fall_y - fall_size//2, 
                                fall_size, fall_size))

        elif model_style == "necro_ex5":  # 俄罗斯方块·消除爆炸
            t = ticks * 0.001
            
            # 下落的方块
            tetromino_types = [
                [(0, 0), (1, 0), (2, 0), (3, 0)],  # I型
                [(0, 0), (1, 0), (0, 1), (1, 1)],  # O型
                [(0, 0), (1, 0), (2, 0), (1, 1)],  # T型
            ]
            
            for i in range(6):
                fall_phase = (t * 2 + i * 0.4) % 1.0
                tetromino = tetromino_types[i % len(tetromino_types)]
                
                base_x = center[0] - 15 + (i % 3) * 15
                base_y = center[1] - 30 + fall_phase * 60
                
                block_size = 5
                block_color = [(100, 255, 255), (255, 255, 100), (255, 100, 255)][i % 3]
                
                for block_dx, block_dy in tetromino:
                    block_x = base_x + block_dx * block_size
                    block_y = base_y + block_dy * block_size
                    pygame.draw.rect(plane_surf, block_color, 
                                   (block_x, block_y, block_size - 1, block_size - 1))
                    pygame.draw.rect(plane_surf, 
                                   tuple(min(255, c + 50) for c in block_color),
                                   (block_x, block_y, block_size - 1, block_size - 1), 1)
            
            # 消除特效
            clear_phase = (t * 3) % 1.0
            if clear_phase < 0.3:
                clear_y = center[1] + 20
                clear_width = int(40 * (1 - clear_phase / 0.3))
                pygame.draw.rect(plane_surf, (255, 255, 255), 
                               (center[0] - 20, clear_y - 2, clear_width, 4))
                
                # 爆炸粒子
                for i in range(10):
                    particle_angle = (i / 10.0) * 2 * math.pi
                    particle_dist = (clear_phase / 0.3) * 30
                    px = center[0] + math.cos(particle_angle) * particle_dist
                    py = clear_y + math.sin(particle_angle) * particle_dist
                    pygame.draw.circle(plane_surf, (255, 255, 100), (int(px), int(py)), 2)
'''

# 读取utils.py
with open('utils.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到crimson_ex5的结尾
insert_marker = '''        elif model_style == "crimson_ex5":  # 弹幕地狱·东方幻想
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
                    pygame.draw.circle(plane_surf, (100, 255, 150), (int(cx), int(cy)), 3)'''

# 插入新代码
new_content = content.replace(insert_marker, insert_marker + render_code)

# 写回文件
with open('utils.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('✅ 成功添加最后8个_ex5渲染代码!')
print('🎮 包含: 蒸汽朋克、DNA螺旋、棋盘游戏、天气预报')
print('       星座连线、漫画分镜、乐高积木、俄罗斯方块')
print('🎉 第五批全部16个_ex5涂装渲染代码已完成!')
