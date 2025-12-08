# 添加剩余13个_ex3渲染代码

renders = [
    ('titan_ex3', '''    elif model_style == "titan_ex3":
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
'''),
    ('thunderbird_ex3', '''    elif model_style == "thunderbird_ex3":
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
'''),
]

# 读取文件
with open('utils.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到插入位置
insert_marker = '''        return s


    # 赛博朋克风格几何飞机 - 13种机体差异化设计 + 动态特性'''

# 构建所有渲染代码
all_renders = '\n'.join([code for _, code in renders])

# 插入
new_content = content.replace(insert_marker, f'''        return s
{all_renders}

    # 赛博朋克风格几何飞机 - 13种机体差异化设计 + 动态特性''')

# 写回
with open('utils.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'成功添加 {len(renders)} 个渲染代码!')
