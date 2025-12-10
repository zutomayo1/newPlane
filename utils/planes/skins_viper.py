"""
Viper 专属涂装渲染模块
包含: cobra, acid, bio, plasma_viper, hydra, neon, serpent_god
"""
import pygame
import math

VIPER_STYLES = [
    'cobra', 'acid', 'bio', 'plasma_viper', 'hydra', 'neon', 'serpent_god',
    'viper_ex', 'viper_ex2', 'viper_ex3', 'viper_ex4', 'viper_ex5'
]

def is_viper_style(model_style):
    return model_style in VIPER_STYLES

def render_viper_skin(s, model_style, c, edge_color, t, pulse):
    """渲染 Viper 专属涂装"""
    
    if model_style == "cobra":
        # 眼镜蛇·毒牙致命
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.15 + 1
        
        head_points = [(60, 30), (70, 45), (50, 45)]
        pygame.draw.polygon(s, (100, 200, 0), head_points)
        pygame.draw.polygon(s, (150, 255, 50), head_points, 2)
        
        hood_points = [(50, 45), (40, 50), (42, 60), (60, 58), (78, 60), (80, 50), (70, 45)]
        pygame.draw.polygon(s, (120, 220, 20), hood_points)
        pygame.draw.polygon(s, (150, 255, 50), hood_points, 2)
        for side_x in [48, 72]:
            pygame.draw.circle(s, (80, 180, 0), (side_x, 53), 5)
            pygame.draw.circle(s, (150, 255, 50), (side_x, 53), 5, 1)
        
        body_points = []
        for i in range(10):
            segment_y = 58 + i * 4
            segment_x = 60 + int(12 * math.sin(t * 3 + i * 0.5))
            body_points.append((segment_x, segment_y))
        for i in range(len(body_points) - 1):
            pygame.draw.line(s, (100, 200, 0), body_points[i], body_points[i+1], 8)
        
        fang_length = int(8 * pulse)
        pygame.draw.line(s, (255, 255, 255), (55, 38), (53, 38 + fang_length), 3)
        pygame.draw.line(s, (255, 255, 255), (65, 38), (67, 38 + fang_length), 3)
        for fang_x in [53, 67]:
            poison_y = 38 + fang_length + int(3 * math.sin(t * 5))
            pygame.draw.circle(s, (100, 255, 0), (fang_x, poison_y), 2)
        
        tongue_length = 10 + int(5 * math.sin(t * 4))
        tongue_base_x, tongue_base_y = 60, 40
        tongue_tip_y = tongue_base_y + tongue_length
        pygame.draw.line(s, (255, 100, 100), (tongue_base_x, tongue_base_y), (tongue_base_x, tongue_tip_y), 2)
        pygame.draw.line(s, (255, 100, 100), (tongue_base_x, tongue_tip_y), (tongue_base_x - 3, tongue_tip_y + 3), 1)
        pygame.draw.line(s, (255, 100, 100), (tongue_base_x, tongue_tip_y), (tongue_base_x + 3, tongue_tip_y + 3), 1)
        
        for i in range(8):
            spray_angle = math.pi / 2 + (i - 4) * math.pi / 16
            spray_dist = 15 + (t * 20 + i * 5) % 25
            spray_x = 60 + math.cos(spray_angle) * spray_dist
            spray_y = 40 + math.sin(spray_angle) * spray_dist
            pygame.draw.circle(s, (120, 240, 20), (int(spray_x), int(spray_y)), 2)
        return s
    
    elif model_style == "acid":
        # 强酸腐蚀·溶解一切
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        pygame.draw.rect(s, (180, 180, 0), (48, 35, 24, 30))
        pygame.draw.rect(s, (220, 220, 50), (48, 35, 24, 30), 2)
        
        acid_level = 50 + int(5 * math.sin(t * 3))
        pygame.draw.rect(s, (200, 255, 0), (50, acid_level, 20, 65 - acid_level))
        for i in range(5):
            wave_x = 50 + i * 5
            wave_y = acid_level + int(2 * math.sin(t * 4 + i))
            pygame.draw.circle(s, (255, 255, 100), (wave_x, wave_y), 2)
        
        smoke_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            smoke_x = 55 + (i % 3) * 5 + int(3 * math.sin(t * 2 + i))
            smoke_y = 35 - (t * 15 + i * 5) % 30
            smoke_size = 4 + int(2 * (30 - (t * 15 + i * 5) % 30) / 30)
            pygame.draw.circle(smoke_surface, (220, 255, 50, 180 - i * 15), (int(smoke_x), int(smoke_y)), smoke_size)
        s.blit(smoke_surface, (0, 0))
        
        for i in range(12):
            splash_angle = i * math.pi / 6 + t * 2
            splash_dist = 25 + 10 * math.sin(t * 3 + i)
            splash_x = 60 + math.cos(splash_angle) * splash_dist
            splash_y = 50 + math.sin(splash_angle) * splash_dist
            pygame.draw.circle(s, (220, 255, 50), (int(splash_x), int(splash_y)), 3)
            trail_x = splash_x - math.cos(splash_angle) * 5
            trail_y = splash_y - math.sin(splash_angle) * 5
            pygame.draw.line(s, (200, 240, 20), (int(splash_x), int(splash_y)), (int(trail_x), int(trail_y)), 1)
        
        corrosion_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            pit_x = 50 + i * 5
            pit_size = 4 + int(2 * pulse)
            pygame.draw.circle(corrosion_surface, (150, 180, 0, 200), (pit_x, 70), pit_size)
            if int(t * 5 + i) % 3 == 0:
                bubble_y = 65 - int(5 * math.sin(t * 4 + i))
                pygame.draw.circle(corrosion_surface, (220, 255, 50, 150), (pit_x, bubble_y), 3)
        s.blit(corrosion_surface, (0, 0))
        return s
    
    elif model_style == "bio":
        # 生化武器·病毒扩散
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        pygame.draw.rect(s, (0, 150, 80), (52, 38, 16, 28))
        pygame.draw.ellipse(s, (0, 180, 100), (52, 35, 16, 6))
        pygame.draw.ellipse(s, (0, 180, 100), (52, 60, 16, 6))
        pygame.draw.rect(s, (100, 255, 150), (52, 38, 16, 28), 2)
        
        virus_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.rect(virus_glow, (50, 220, 120, 200), (54, 40, 12, 24))
        s.blit(virus_glow, (0, 0))
        
        for layer in range(3):
            for i in range(8):
                cloud_angle = t * 1.5 + i * math.pi / 4 + layer * math.pi / 6
                cloud_dist = 25 + layer * 10
                cloud_x = 60 + math.cos(cloud_angle) * cloud_dist
                cloud_y = 50 + math.sin(cloud_angle) * cloud_dist
                cloud_size = 8 - layer * 2
                cloud_alpha = 180 - layer * 60
                cloud_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(cloud_surface, (50, 220, 120, cloud_alpha), (int(cloud_x), int(cloud_y)), cloud_size)
                s.blit(cloud_surface, (0, 0))
        
        for i in range(20):
            particle_angle = t * 2 + i * math.pi / 10
            particle_dist = 20 + 20 * (i / 20) + 5 * math.sin(t * 3 + i)
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            pygame.draw.circle(s, (50, 220, 120), (int(px), int(py)), 3)
            for spike_dir in range(4):
                spike_angle = spike_dir * math.pi / 2 + t * 3
                spike_x = px + math.cos(spike_angle) * 4
                spike_y = py + math.sin(spike_angle) * 4
                pygame.draw.line(s, (100, 255, 150), (int(px), int(py)), (int(spike_x), int(spike_y)), 1)
        
        if int(t * 3) % 2 == 0:
            symbol_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            for i in range(3):
                symbol_angle = i * 2 * math.pi / 3 + t
                symbol_x = 60 + math.cos(symbol_angle) * 12
                symbol_y = 50 + math.sin(symbol_angle) * 12
                pygame.draw.circle(symbol_surface, (255, 255, 0, 200), (int(symbol_x), int(symbol_y)), 5)
                pygame.draw.line(symbol_surface, (255, 255, 0, 200), (60, 50), (int(symbol_x), int(symbol_y)), 3)
            pygame.draw.circle(symbol_surface, (255, 255, 0, 200), (60, 50), 6)
            pygame.draw.circle(symbol_surface, (200, 200, 0, 200), (60, 50), 6, 2)
            s.blit(symbol_surface, (0, 0))
        return s
    
    elif model_style == "plasma_viper":
        # 等离子毒液·能量腐蚀
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        pygame.draw.circle(s, (150, 0, 200), (60, 50), 15)
        pygame.draw.circle(s, (200, 0, 255), (60, 50), 15, 2)
        
        plasma_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            plasma_angle = t * 4 + i * math.pi / 6
            plasma_dist = 18 + 5 * math.sin(t * 3 + i)
            px = 60 + math.cos(plasma_angle) * plasma_dist
            py = 50 + math.sin(plasma_angle) * plasma_dist
            drop_size = int(4 * pulse)
            pygame.draw.circle(plasma_surface, (200, 0, 255, 220), (int(px), int(py)), drop_size)
            pygame.draw.circle(plasma_surface, (255, 100, 255, 150), (int(px), int(py)), drop_size + 2)
        s.blit(plasma_surface, (0, 0))
        
        for i in range(3):
            corrosion_radius = 20 + i * 10 + (t * 30) % 20
            corrosion_alpha = int(200 * (1 - ((t * 30) % 20) / 20))
            corrosion_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(corrosion_surface, (220, 50, 255, corrosion_alpha), (60, 50), int(corrosion_radius), 2)
            s.blit(corrosion_surface, (0, 0))
        
        ray_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            if (int(t * 8) + i) % 3 == 0:
                ray_angle = i * math.pi / 4 + t * 0.5
                ray_length = 30 + 10 * math.sin(t * 3 + i)
                ray_x = 60 + math.cos(ray_angle) * ray_length
                ray_y = 50 + math.sin(ray_angle) * ray_length
                pygame.draw.line(ray_surface, (200, 0, 255, 200), (60, 50), (int(ray_x), int(ray_y)), 2)
                pygame.draw.circle(ray_surface, (255, 100, 255, 150), (int(ray_x), int(ray_y)), 5)
        s.blit(ray_surface, (0, 0))
        
        for i in range(15):
            disintegrate_angle = t * 3 + i * math.pi / 7.5
            disintegrate_dist = 25 + 15 * (i / 15)
            dx = 60 + math.cos(disintegrate_angle) * disintegrate_dist
            dy = 50 + math.sin(disintegrate_angle) * disintegrate_dist
            particle_size = 2 + int(2 * math.sin(t * 4 + i))
            pygame.draw.rect(s, (220, 50, 255), (int(dx) - particle_size//2, int(dy) - particle_size//2, particle_size, particle_size))
            particle_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(particle_glow, (255, 100, 255, 120), (int(dx), int(dy)), 4)
            s.blit(particle_glow, (0, 0))
        return s
    
    elif model_style == "hydra":
        # 九头蛇·致命群蛇
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        pygame.draw.circle(s, (0, 120, 40), (60, 50), 12)
        pygame.draw.circle(s, (100, 200, 100), (60, 50), 12, 2)
        
        for i in range(9):
            snake_angle = i * 2 * math.pi / 9 + t * 1.5
            snake_dist = 25 + 8 * math.sin(t * 2 + i * 0.5)
            head_x = 60 + math.cos(snake_angle) * snake_dist
            head_y = 50 + math.sin(snake_angle) * snake_dist
            
            neck_segments = 5
            for seg in range(neck_segments):
                seg_ratio = (seg + 1) / neck_segments
                seg_x = 60 + (head_x - 60) * seg_ratio + math.sin(t * 4 + i + seg) * 2
                seg_y = 50 + (head_y - 50) * seg_ratio + math.cos(t * 4 + i + seg) * 2
                prev_ratio = seg / neck_segments
                prev_x = 60 + (head_x - 60) * prev_ratio + math.sin(t * 4 + i + seg - 1) * 2
                prev_y = 50 + (head_y - 50) * prev_ratio + math.cos(t * 4 + i + seg - 1) * 2
                pygame.draw.line(s, (50, 180, 80), (int(prev_x), int(prev_y)), (int(seg_x), int(seg_y)), 4)
            
            head_size = 6
            head_angle_offset = snake_angle
            head_points = [
                (head_x + math.cos(head_angle_offset) * head_size, head_y + math.sin(head_angle_offset) * head_size),
                (head_x + math.cos(head_angle_offset + 2.5) * 4, head_y + math.sin(head_angle_offset + 2.5) * 4),
                (head_x + math.cos(head_angle_offset - 2.5) * 4, head_y + math.sin(head_angle_offset - 2.5) * 4),
            ]
            pygame.draw.polygon(s, (0, 150, 50), [(int(p[0]), int(p[1])) for p in head_points])
            
            fang_x = head_x + math.cos(head_angle_offset) * (head_size + 3)
            fang_y = head_y + math.sin(head_angle_offset) * (head_size + 3)
            pygame.draw.line(s, (255, 255, 255), (int(head_x), int(head_y)), (int(fang_x), int(fang_y)), 2)
        
        rain_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(25):
            rain_x = 30 + (i * 3.6) % 60
            rain_y = 20 + ((t * 50 + i * 4) % 70)
            pygame.draw.line(rain_surface, (50, 255, 0, 200), (int(rain_x), int(rain_y)), (int(rain_x), int(rain_y + 5)), 2)
            pygame.draw.circle(rain_surface, (100, 255, 50, 180), (int(rain_x), int(rain_y + 5)), 2)
        s.blit(rain_surface, (0, 0))
        return s
    
    elif model_style == "neon":
        # 霓虹毒蛇·致命诱惑
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        body_points = []
        for i in range(15):
            segment_y = 30 + i * 4
            segment_x = 60 + int(15 * math.sin(t * 2 + i * 0.4))
            body_points.append((segment_x, segment_y))
        
        for i in range(len(body_points) - 1):
            hue = (t * 50 + i * 20) % 360
            color_r = int(127 + 127 * math.sin(math.radians(hue)))
            color_g = int(127 + 127 * math.sin(math.radians(hue + 120)))
            color_b = int(127 + 127 * math.sin(math.radians(hue + 240)))
            pygame.draw.line(s, (color_r, color_g, color_b), body_points[i], body_points[i+1], 10)
            glow_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(glow_surface, (color_r, color_g, color_b, 150), body_points[i], body_points[i+1], 14)
            s.blit(glow_surface, (0, 0))
        
        fog_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            fog_angle = t * 2 + i * math.pi / 6
            fog_dist = 25 + 10 * math.sin(t * 1.5 + i)
            fog_x = 60 + math.cos(fog_angle) * fog_dist
            fog_y = 50 + math.sin(fog_angle) * fog_dist
            hue = (t * 80 + i * 30) % 360
            fog_r = int(127 + 127 * math.sin(math.radians(hue)))
            fog_g = int(127 + 127 * math.sin(math.radians(hue + 120)))
            fog_b = int(127 + 127 * math.sin(math.radians(hue + 240)))
            pygame.draw.circle(fog_surface, (fog_r, fog_g, fog_b, 120), (int(fog_x), int(fog_y)), 8)
        s.blit(fog_surface, (0, 0))
        
        for i in range(20):
            if (int(t * 10) + i) % 4 < 2:
                particle_angle = t * 3 + i * math.pi / 10
                particle_dist = 20 + 20 * (i / 20)
                px = 60 + math.cos(particle_angle) * particle_dist
                py = 50 + math.sin(particle_angle) * particle_dist
                hue = (t * 100 + i * 18) % 360
                p_r = int(127 + 127 * math.sin(math.radians(hue)))
                p_g = int(127 + 127 * math.sin(math.radians(hue + 120)))
                p_b = int(127 + 127 * math.sin(math.radians(hue + 240)))
                pygame.draw.circle(s, (p_r, p_g, p_b), (int(px), int(py)), 3)
                particle_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(particle_glow, (p_r, p_g, p_b, 180), (int(px), int(py)), 6)
                s.blit(particle_glow, (0, 0))
        return s
    
    elif model_style == "serpent_god":
        # 蛇神降世·巴蛇吞象
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        head_points = [(60, 25), (75, 45), (70, 55), (60, 58), (50, 55), (45, 45)]
        pygame.draw.polygon(s, (200, 160, 0), head_points)
        pygame.draw.polygon(s, (255, 215, 0), head_points, 3)
        
        for eye_x in [52, 68]:
            pygame.draw.circle(s, (255, 255, 100), (eye_x, 40), 5)
            pygame.draw.circle(s, (255, 215, 0), (eye_x, 40), 5, 2)
            pygame.draw.circle(s, (200, 0, 0), (eye_x, 40), 2)
            eye_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(eye_glow, (255, 255, 100, 150), (eye_x, 40), int(8 * pulse))
            s.blit(eye_glow, (0, 0))
        
        body_segments = []
        for i in range(12):
            segment_angle = t * 1.5 + i * math.pi / 6
            segment_dist = 20 + i * 2
            seg_x = 60 + math.cos(segment_angle) * segment_dist
            seg_y = 58 + i * 3
            body_segments.append((seg_x, seg_y))
        for i in range(len(body_segments) - 1):
            pygame.draw.line(s, (220, 180, 0), (int(body_segments[i][0]), int(body_segments[i][1])), 
                           (int(body_segments[i+1][0]), int(body_segments[i+1][1])), 12)
        
        scale_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            scale_angle = t * 2 + i * math.pi / 10
            scale_dist = 15 + 20 * (i / 20)
            scale_x = 60 + math.cos(scale_angle) * scale_dist
            scale_y = 50 + math.sin(scale_angle) * scale_dist
            if (int(t * 8) + i) % 5 < 2:
                scale_points = [
                    (scale_x, scale_y - 3), (scale_x + 2, scale_y),
                    (scale_x, scale_y + 3), (scale_x - 2, scale_y),
                ]
                pygame.draw.polygon(scale_surface, (255, 255, 100, 220), [(int(p[0]), int(p[1])) for p in scale_points])
        s.blit(scale_surface, (0, 0))
        
        for i in range(3):
            halo_radius = 30 + i * 10 + int(5 * pulse)
            halo_alpha = int(150 * (1 - i / 3))
            halo_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(halo_surface, (255, 215, 0, halo_alpha), (60, 45), halo_radius, 2)
            s.blit(halo_surface, (0, 0))
        
        power_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            power_angle = t * 3 + i * math.pi / 4
            power_dist = 35 + 10 * math.sin(t * 2 + i)
            power_x = 60 + math.cos(power_angle) * power_dist
            power_y = 50 + math.sin(power_angle) * power_dist
            pygame.draw.circle(power_surface, (255, 230, 50, 200), (int(power_x), int(power_y)), 4)
            pygame.draw.line(power_surface, (255, 215, 0, 150), (60, 50), (int(power_x), int(power_y)), 2)
        s.blit(power_surface, (0, 0))
        return s
    
    elif model_style == "viper_ex":
        # 异形孢子 - 生物触手，孢子飘散
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中央孢囊
        pygame.draw.circle(s, (100, 255, 0), (60, 50), int(18 * pulse))
        pygame.draw.circle(s, (150, 255, 100), (60, 50), int(18 * pulse), 3)
        
        # 8根触手（动态摆动）
        for i in range(8):
            angle = i * math.pi / 4
            # 触手分段
            segments = []
            for j in range(6):
                seg_dist = 20 + j * 6
                seg_angle = angle + math.sin(t * 3 + i + j * 0.5) * 0.4
                seg_x = 60 + math.cos(seg_angle) * seg_dist
                seg_y = 50 + math.sin(seg_angle) * seg_dist
                segments.append((int(seg_x), int(seg_y)))
            
            # 绘制触手
            for j in range(len(segments) - 1):
                width = 6 - j
                pygame.draw.line(s, (80, 200, 0), segments[j], segments[j+1], width)
        
        # 孢子飘散
        for i in range(15):
            spore_angle = t * 2 + i * 0.4
            spore_dist = 25 + (t * 20 + i * 5) % 40
            spx = 60 + math.cos(spore_angle) * spore_dist
            spy = 50 + math.sin(spore_angle) * spore_dist
            pygame.draw.circle(s, (150, 255, 50), (int(spx), int(spy)), 4)
        
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
    
    elif model_style == "viper_ex4":
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
    
    elif model_style == "viper_ex5":
        # 魔法阵召唤·炼金术
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        
        # 外圈魔法阵
        for ring in range(3):
            ring_radius = 40 - ring * 10
            ring_rotation = t * (1 + ring * 0.5) * (-1 if ring % 2 else 1)
            
            pygame.draw.circle(plane_surf, (200, 150, 255), center, ring_radius, 2)
            
            # 符文符号
            rune_count = 6 + ring * 2
            for i in range(rune_count):
                angle = ring_rotation + (i / rune_count) * 2 * math.pi
                rx = center[0] + math.cos(angle) * ring_radius
                ry = center[1] + math.sin(angle) * ring_radius
                
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
        return plane_surf
    
    return None
