"""
Thunderbird 专属涂装渲染模块
包含: storm, tesla, plasma, aurora_bird, valkyrie, phoenix, cosmic
"""
import pygame
import math
import random

THUNDERBIRD_STYLES = [
    'storm', 'tesla', 'plasma', 'aurora_bird', 'valkyrie', 'phoenix', 'cosmic',
    'thunderbird_ex', 'thunderbird_ex2', 'thunderbird_ex3', 'thunderbird_ex4', 'thunderbird_ex5'
]

def is_thunderbird_style(model_style):
    return model_style in THUNDERBIRD_STYLES

def render_thunderbird_skin(s, model_style, c, edge_color, t, pulse):
    """渲染 Thunderbird 专属涂装"""
    
    if model_style == "storm":
        # 风暴之眼·雷霆主宰
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.15 + 1
        
        bird_points = [(60, 35), (75, 55), (60, 60), (45, 55)]
        pygame.draw.polygon(s, (100, 100, 150), bird_points)
        pygame.draw.polygon(s, (200, 200, 255), bird_points, 2)
        
        cloud_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for layer in range(3):
            for i in range(8):
                cloud_angle = t * 2 + i * math.pi / 4 + layer * math.pi / 6
                cloud_dist = 25 + layer * 8
                cx = 60 + math.cos(cloud_angle) * cloud_dist
                cy = 50 + math.sin(cloud_angle) * cloud_dist
                cloud_size = 6 - layer * 2
                pygame.draw.circle(cloud_surface, (80, 80, 120, 150 - layer * 50), (int(cx), int(cy)), cloud_size)
        s.blit(cloud_surface, (0, 0))
        
        lightning_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            if (int(t * 10) + i) % 3 == 0:
                lightning_angle = i * math.pi / 6
                start_x = 60 + math.cos(lightning_angle) * 15
                start_y = 50 + math.sin(lightning_angle) * 15
                end_x = 60 + math.cos(lightning_angle) * 40
                end_y = 50 + math.sin(lightning_angle) * 40
                pygame.draw.line(lightning_surface, (200, 200, 255, 250), (int(start_x), int(start_y)), (int(end_x), int(end_y)), 2)
                mid_x, mid_y = (start_x + end_x) / 2, (start_y + end_y) / 2
                branch_angle = lightning_angle + math.pi / 6
                branch_x = mid_x + math.cos(branch_angle) * 10
                branch_y = mid_y + math.sin(branch_angle) * 10
                pygame.draw.line(lightning_surface, (150, 150, 255, 200), (int(mid_x), int(mid_y)), (int(branch_x), int(branch_y)), 1)
        s.blit(lightning_surface, (0, 0))
        
        core_size = int(12 * pulse)
        core_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(core_glow, (200, 200, 255, 220), (60, 50), core_size)
        pygame.draw.circle(core_glow, (150, 150, 255, 150), (60, 50), core_size + 5)
        pygame.draw.circle(core_glow, (100, 100, 200, 80), (60, 50), core_size + 10)
        s.blit(core_glow, (0, 0))
        return s
    
    elif model_style == "tesla":
        # 特斯拉线圈·电磁风暴
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.15 + 1
        
        pygame.draw.circle(s, (0, 80, 200), (60, 50), 15)
        pygame.draw.circle(s, (0, 100, 255), (60, 50), 15, 2)
        
        for i in range(6):
            coil_angle = i * math.pi / 3 + t * 0.5
            coil_x = 60 + math.cos(coil_angle) * 25
            coil_y = 50 + math.sin(coil_angle) * 25
            pygame.draw.circle(s, (50, 150, 255), (int(coil_x), int(coil_y)), 6)
            pygame.draw.circle(s, (100, 200, 255), (int(coil_x), int(coil_y)), 6, 2)
            for j in range(3):
                spiral_r = 3 + j
                spiral_angle = t * 5 + j * math.pi / 1.5
                sx = coil_x + math.cos(spiral_angle) * spiral_r
                sy = coil_y + math.sin(spiral_angle) * spiral_r
                pygame.draw.circle(s, (100, 200, 255), (int(sx), int(sy)), 1)
        
        arc_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            if (int(t * 8) + i) % 2 == 0:
                angle1 = i * math.pi / 3 + t * 0.5
                angle2 = ((i + 1) % 6) * math.pi / 3 + t * 0.5
                x1 = 60 + math.cos(angle1) * 25
                y1 = 50 + math.sin(angle1) * 25
                x2 = 60 + math.cos(angle2) * 25
                y2 = 50 + math.sin(angle2) * 25
                pygame.draw.line(arc_surface, (100, 200, 255, 200), (int(x1), int(y1)), (int(x2), int(y2)), 2)
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                pygame.draw.circle(arc_surface, (150, 220, 255, 150), (int(mid_x), int(mid_y)), 5)
        s.blit(arc_surface, (0, 0))
        
        for i in range(3):
            pulse_radius = (t * 50 + i * 25) % 80
            pulse_alpha = int(200 * (1 - pulse_radius / 80))
            pulse_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(pulse_surface, (50, 150, 255, pulse_alpha), (60, 50), int(pulse_radius), 2)
            s.blit(pulse_surface, (0, 0))
        
        for i in range(8):
            plasma_angle = t * 4 + i * math.pi / 4
            plasma_dist = 35 + 5 * math.sin(t * 3 + i)
            px = 60 + math.cos(plasma_angle) * plasma_dist
            py = 50 + math.sin(plasma_angle) * plasma_dist
            plasma_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(plasma_glow, (100, 200, 255, 220), (int(px), int(py)), 4)
            pygame.draw.circle(plasma_glow, (150, 220, 255, 120), (int(px), int(py)), 7)
            s.blit(plasma_glow, (0, 0))
        return s
    
    elif model_style == "plasma":
        # 等离子羽翼·能量天使
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        pygame.draw.ellipse(s, (255, 150, 255), (50, 40, 20, 25))
        pygame.draw.ellipse(s, (255, 200, 255), (50, 40, 20, 25), 2)
        
        wing_base_y = 50
        for side in [-1, 1]:
            for i in range(5):
                feather_angle = side * (math.pi / 6 + i * math.pi / 12) + math.sin(t * 2 + i) * 0.2
                feather_length = 25 + i * 3
                feather_x = 60 + math.cos(feather_angle) * feather_length
                feather_y = wing_base_y + math.sin(feather_angle) * feather_length
                feather_color = (255, 150 + i * 10, 255)
                pygame.draw.line(s, feather_color, (60, wing_base_y), (int(feather_x), int(feather_y)), 3)
                feather_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(feather_glow, (255, 200, 255, 150), (60, wing_base_y), (int(feather_x), int(feather_y)), 6)
                s.blit(feather_glow, (0, 0))
        
        for i in range(15):
            feather_angle = t * 3 + i * math.pi / 7.5
            feather_dist = 30 + 15 * math.sin(t * 2 + i)
            fx = 60 + math.cos(feather_angle) * feather_dist
            fy = 50 + math.sin(feather_angle) * feather_dist
            pygame.draw.line(s, (230, 170, 255), (int(fx), int(fy)), (int(fx + 3), int(fy + 5)), 2)
            particle_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(particle_glow, (255, 200, 255, 120), (int(fx), int(fy)), 4)
            s.blit(particle_glow, (0, 0))
        
        spiral_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            spiral_angle = t * 4 + i * math.pi / 10
            spiral_dist = 10 + i * 2
            sx = 60 + math.cos(spiral_angle) * spiral_dist
            sy = 50 + math.sin(spiral_angle) * spiral_dist
            pygame.draw.circle(spiral_surface, (255, 150, 255, 180 - i * 8), (int(sx), int(sy)), 2)
        s.blit(spiral_surface, (0, 0))
        
        for i in range(3):
            halo_radius = 35 + i * 8 + int(5 * pulse)
            halo_alpha = int(100 * (1 - i / 3))
            halo_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(halo_surface, (255, 200, 255, halo_alpha), (60, 50), halo_radius, 2)
            s.blit(halo_surface, (0, 0))
        return s
    
    elif model_style == "aurora_bird":
        # 极光战鹰·北境之翼
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        pygame.draw.ellipse(s, (0, 200, 150), (52, 42, 16, 20))
        pygame.draw.ellipse(s, (100, 255, 200), (52, 42, 16, 20), 2)
        
        aurora_colors = [(255, 100, 100), (255, 200, 100), (255, 255, 100), (100, 255, 100), (100, 200, 255), (200, 100, 255)]
        for side in [-1, 1]:
            for i in range(6):
                wave_angle = side * math.pi / 3 + math.sin(t * 3 + i * 0.5) * 0.3
                wave_length = 20 + i * 4
                wave_x = 60 + math.cos(wave_angle) * wave_length
                wave_y = 50 + math.sin(wave_angle) * wave_length
                aurora_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
                color = aurora_colors[i]
                for j in range(5):
                    segment_ratio = j / 4
                    seg_x = 60 + (wave_x - 60) * segment_ratio
                    seg_y = 50 + (wave_y - 50) * segment_ratio + math.sin(t * 4 + j) * 3
                    next_ratio = (j + 1) / 4
                    next_x = 60 + (wave_x - 60) * next_ratio
                    next_y = 50 + (wave_y - 50) * next_ratio + math.sin(t * 4 + j + 1) * 3
                    pygame.draw.line(aurora_surface, (*color, 180), (int(seg_x), int(seg_y)), (int(next_x), int(next_y)), 3)
                s.blit(aurora_surface, (0, 0))
        
        for i in range(6):
            ribbon_x = 60
            ribbon_y = 70 + i * 5 + int(5 * math.sin(t * 3 + i))
            ribbon_length = 20 - i * 2
            color = aurora_colors[i]
            pygame.draw.line(s, color, (ribbon_x, ribbon_y), (ribbon_x + ribbon_length, ribbon_y + 5), 2)
        
        for i in range(20):
            feather_x = 40 + (t * 30 + i * 6) % 40
            feather_y = 30 + i * 3
            color = aurora_colors[i % 6]
            pygame.draw.line(s, color, (int(feather_x), int(feather_y)), (int(feather_x + 2), int(feather_y + 4)), 1)
            glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*color, 100), (int(feather_x), int(feather_y)), 3)
            s.blit(glow, (0, 0))
        return s
    
    elif model_style == "valkyrie":
        # 女武神·战争使者
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.12 + 1
        
        pygame.draw.ellipse(s, (255, 240, 200), (54, 38, 12, 28))
        pygame.draw.circle(s, (255, 250, 230), (60, 35), 5)
        pygame.draw.ellipse(s, (255, 245, 220), (54, 38, 12, 28), 2)
        
        wing_colors = [(255, 255, 255), (255, 250, 230), (255, 245, 220)]
        for side in [-1, 1]:
            for i in range(6):
                wing_angle = side * (math.pi / 4 + i * math.pi / 18)
                wing_length = 30 + i * 2
                wing_x = 60 + math.cos(wing_angle) * wing_length
                wing_y = 50 + math.sin(wing_angle) * wing_length
                for layer in range(3):
                    feather_offset = layer * 2
                    fx = 60 + math.cos(wing_angle) * (wing_length - feather_offset)
                    fy = 50 + math.sin(wing_angle) * (wing_length - feather_offset)
                    color = wing_colors[layer]
                    pygame.draw.line(s, color, (60, 50), (int(fx), int(fy)), 4 - layer)
        
        for i in range(25):
            feather_angle = t * 2 + i * math.pi / 12.5
            feather_dist = 25 + 20 * math.sin(t * 1.5 + i * 0.2)
            fx = 60 + math.cos(feather_angle) * feather_dist
            fy = 50 + math.sin(feather_angle) * feather_dist
            pygame.draw.line(s, (255, 250, 230), (int(fx), int(fy)), (int(fx + 3), int(fy + 5)), 2)
            holy_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(holy_glow, (255, 255, 255, 120), (int(fx), int(fy)), 4)
            s.blit(holy_glow, (0, 0))
        
        cross_length = int(25 * pulse)
        cross_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(cross_glow, (255, 255, 255, 200), (60, 50 - cross_length), (60, 50 + cross_length), 4)
        pygame.draw.line(cross_glow, (255, 255, 255, 200), (60 - cross_length, 50), (60 + cross_length, 50), 4)
        s.blit(cross_glow, (0, 0))
        
        halo_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(halo_surface, (255, 255, 255, 150), (60, 30), int(8 * pulse))
        s.blit(halo_surface, (0, 0))
        return s
    
    elif model_style == "phoenix":
        # 雷电凤凰·涅槃重生
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        phoenix_body = [(60, 35), (70, 50), (65, 62), (60, 65), (55, 62), (50, 50)]
        pygame.draw.polygon(s, (255, 180, 0), phoenix_body)
        pygame.draw.polygon(s, (255, 255, 100), phoenix_body, 2)
        
        pygame.draw.circle(s, (255, 200, 0), (60, 30), 6)
        for i in range(3):
            crown_x = 60 + (i - 1) * 4
            crown_y = 25 - i * 2
            pygame.draw.line(s, (255, 220, 50), (60, 30), (crown_x, crown_y), 2)
            pygame.draw.circle(s, (255, 100, 0), (crown_x, crown_y), 2)
        
        for side in [-1, 1]:
            for i in range(7):
                wing_angle = side * (math.pi / 3 + i * math.pi / 14) + math.sin(t * 2 + i) * 0.15
                wing_length = 28 + i * 2
                wing_x = 60 + math.cos(wing_angle) * wing_length
                wing_y = 50 + math.sin(wing_angle) * wing_length
                fire_gradient = (255, 220 - i * 15, 50 - i * 5)
                pygame.draw.line(s, fire_gradient, (60, 50), (int(wing_x), int(wing_y)), 3)
                if i % 2 == 0 and (int(t * 10) % 3 == 0):
                    lightning = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(lightning, (100, 200, 255, 200), (60, 50), (int(wing_x), int(wing_y)), 1)
                    s.blit(lightning, (0, 0))
        
        rebirth_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            fire_angle = t * 5 + i * math.pi / 6
            fire_dist = 20 + 15 * math.sin(t * 3 + i * 0.5)
            fire_x = 60 + math.cos(fire_angle) * fire_dist
            fire_y = 50 + math.sin(fire_angle) * fire_dist
            fire_size = 6 + 3 * math.sin(t * 4 + i)
            pygame.draw.circle(rebirth_surface, (255, 100, 0, 200), (int(fire_x), int(fire_y)), int(fire_size))
        s.blit(rebirth_surface, (0, 0))
        
        for i in range(30):
            flame_angle = t * 3 + i * math.pi / 15
            flame_dist = 25 + 20 * (i / 30)
            fx = 60 + math.cos(flame_angle) * flame_dist
            fy = 50 + math.sin(flame_angle) * flame_dist
            pygame.draw.line(s, (255, 200, 0), (int(fx), int(fy)), (int(fx + 2), int(fy + 4)), 1)
            flame_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(flame_glow, (255, 150, 0, 150), (int(fx), int(fy)), 4)
            s.blit(flame_glow, (0, 0))
        
        for i in range(3):
            wave_radius = (t * 40 + i * 20) % 60
            wave_alpha = int(180 * (1 - wave_radius / 60))
            wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, (255, 200, 0, wave_alpha), (60, 50), int(wave_radius), 2)
            s.blit(wave_surface, (0, 0))
        return s
    
    elif model_style == "cosmic":
        # 宇宙雷神·星云之翼
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.12 + 1
        
        pygame.draw.circle(s, (100, 50, 150), (60, 50), 12)
        pygame.draw.circle(s, (150, 100, 255), (60, 50), 12, 2)
        
        nebula_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for side in [-1, 1]:
            for i in range(8):
                nebula_angle = side * (math.pi / 4 + i * math.pi / 16)
                nebula_dist = 20 + i * 3
                nx = 60 + math.cos(nebula_angle) * nebula_dist
                ny = 50 + math.sin(nebula_angle) * nebula_dist
                color_r = 150 + int(50 * math.sin(t + i))
                color_g = 100 + int(50 * math.sin(t + i + 1))
                color_b = 255
                nebula_size = 8 - i
                pygame.draw.circle(nebula_surface, (color_r, color_g, color_b, 180), (int(nx), int(ny)), nebula_size)
        s.blit(nebula_surface, (0, 0))
        
        for i in range(25):
            spiral_angle = t * 3 + i * math.pi / 12.5
            spiral_dist = 10 + i * 1.5
            sx = 60 + math.cos(spiral_angle) * spiral_dist
            sy = 50 + math.sin(spiral_angle) * spiral_dist
            star_color = (180 + int(30 * math.sin(i)), 120, 255)
            pygame.draw.circle(s, star_color, (int(sx), int(sy)), 2)
        
        for i in range(40):
            star_angle = t * 2 + i * math.pi / 20
            star_dist = 20 + 25 * (i / 40) + 5 * math.sin(t * 3 + i)
            star_x = 60 + math.cos(star_angle) * star_dist
            star_y = 50 + math.sin(star_angle) * star_dist
            if (int(t * 10) + i) % 4 < 2:
                pygame.draw.circle(s, (200, 150, 255), (int(star_x), int(star_y)), 2)
                star_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(star_glow, (200, 150, 255, 120), (int(star_x), int(star_y)), 4)
                s.blit(star_glow, (0, 0))
        
        galaxy_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            band_y = 40 + i * 4 + int(5 * math.sin(t * 2 + i * 0.5))
            band_x_start = 50 - i * 2
            band_x_end = 70 + i * 2
            for j in range(20):
                segment_x = band_x_start + (band_x_end - band_x_start) * j / 20
                color_intensity = int(200 * (1 - abs(j - 10) / 10))
                pygame.draw.circle(galaxy_surface, (150, 100, 255, color_intensity), (int(segment_x), band_y), 2)
        s.blit(galaxy_surface, (0, 0))
        
        for i in range(3):
            explosion_radius = 30 + i * 10 + int(8 * pulse)
            explosion_alpha = int(120 * (1 - i / 3))
            explosion_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surface, (180, 120, 255, explosion_alpha), (60, 50), explosion_radius, 3)
            s.blit(explosion_surface, (0, 0))
        return s
    
    elif model_style == "thunderbird_ex":
        # 极光风暴 - 多层展翼，极光流动
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 三层翅膀（由内到外）
        for layer in range(3):
            wing_span = 40 + layer * 15
            wing_height = 30 + layer * 10
            alpha = 220 - layer * 40
            
            wing_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 左翼
            left_wing = [(60, 50), (60 - wing_span, 50 - wing_height), (60 - wing_span, 50 + wing_height)]
            pygame.draw.polygon(wing_surf, (0, 255, 200, alpha), left_wing)
            # 右翼
            right_wing = [(60, 50), (60 + wing_span, 50 - wing_height), (60 + wing_span, 50 + wing_height)]
            pygame.draw.polygon(wing_surf, (0, 255, 200, alpha), right_wing)
            s.blit(wing_surf, (0, 0))
        
        # 极光粒子流
        for i in range(20):
            particle_angle = t * 3 + i * math.pi / 10
            particle_dist = 30 + 20 * (i / 20)
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            # 彩虹色
            hue = (t * 50 + i * 18) % 360
            color_r = int(127 + 127 * math.sin(math.radians(hue)))
            color_g = int(127 + 127 * math.sin(math.radians(hue + 120)))
            color_b = int(127 + 127 * math.sin(math.radians(hue + 240)))
            pygame.draw.circle(s, (color_r, color_g, color_b), (int(px), int(py)), 3)
        
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
    
    elif model_style == "thunderbird_ex3":
        # 雷电瓦尔基里 - 战争天使
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
        
        # 雷电翅膀（3片羽翼）
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
    
    elif model_style == "thunderbird_ex4":
        # 等离子生命 - 电弧之魂
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 等离子球（核心）
        plasma_core_radius = int(10 + 5 * math.sin(t * 3))
        for core_layer in range(5, 0, -1):
            layer_radius = int(plasma_core_radius * (core_layer / 5))
            layer_alpha = 255
            # 从青蓝到白的渐变
            layer_brightness = int(100 + 155 * (core_layer / 5))
            core_color = (layer_brightness, 255, 255)
            pygame.draw.circle(s, core_color, (60, 50), layer_radius)
        
        # 闪电分叉（随机生成）
        lightning_branches = 6
        for branch in range(lightning_branches):
            # 主闪电路径
            branch_angle = branch * math.pi / 3 + t * 2
            
            # 闪电节点
            lightning_points = [(60, 50)]
            current_x, current_y = 60, 50
            
            for seg in range(6):
                # 随机偏移
                seg_angle = branch_angle + (random.random() - 0.5) * 0.8
                seg_dist = 8 + random.random() * 5
                current_x += math.cos(seg_angle) * seg_dist
                current_y += math.sin(seg_angle) * seg_dist
                lightning_points.append((int(current_x), int(current_y)))
            
            # 绘制闪电
            for i in range(len(lightning_points) - 1):
                # 闪烁效果
                if (int(t * 20) + branch) % 5 < 4:
                    lightning_brightness = int(200 + 55 * random.random())
                    
                    # 多层闪电
                    for layer in range(3):
                        layer_width = 4 - layer
                        layer_alpha = 255 - layer * 70
                        lightning_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                        
                        if layer == 0:
                            lightning_color = (255, 255, 255)
                        elif layer == 1:
                            lightning_color = (lightning_brightness, 255, 255)
                        else:
                            lightning_color = (100, lightning_brightness, 255)
                        
                        pygame.draw.line(lightning_surf, (*lightning_color, layer_alpha),
                                       lightning_points[i], lightning_points[i + 1], layer_width)
                        s.blit(lightning_surf, (0, 0))
                
                # 小分支
                if random.random() < 0.3:
                    sub_angle = branch_angle + (random.random() - 0.5) * 1.5
                    sub_dist = 10
                    sub_x = lightning_points[i][0] + int(math.cos(sub_angle) * sub_dist)
                    sub_y = lightning_points[i][1] + int(math.sin(sub_angle) * sub_dist)
                    
                    if (int(t * 20) + i) % 6 < 4:
                        pygame.draw.line(s, (150, 255, 255),
                                       lightning_points[i], (sub_x, sub_y), 2)
        
        # 电弧粒子环绕
        for particle in range(25):
            p_angle = particle * 0.4 + t * 4
            p_dist = 20 + 15 * math.sin(t * 2 + particle * 0.3)
            px = 60 + math.cos(p_angle) * p_dist
            py = 50 + math.sin(p_angle) * p_dist
            
            # 粒子闪烁
            if (int(t * 15) + particle) % 4 < 3:
                particle_brightness = int(200 + 55 * math.sin(t * 6 + particle))
                pygame.draw.circle(s, (particle_brightness, 255, 255), (int(px), int(py)), 2)
        
        # 电磁场波动
        for field_wave in range(4):
            wave_progress = (t * 2.5 + field_wave * 0.3) % 1
            wave_radius = int(15 + wave_progress * 40)
            wave_alpha = int(200 * (1 - wave_progress))
            
            if wave_alpha > 30:
                # 波动不规则
                wave_points = []
                for i in range(12):
                    wave_angle = i * math.pi / 6
                    distortion = 5 * math.sin(t * 4 + i + field_wave)
                    wx = 60 + math.cos(wave_angle) * (wave_radius + distortion)
                    wy = 50 + math.sin(wave_angle) * (wave_radius + distortion)
                    wave_points.append((int(wx), int(wy)))
                
                if len(wave_points) > 2:
                    field_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.lines(field_surf, (100, 255, 255, wave_alpha), True, wave_points, 2)
                    s.blit(field_surf, (0, 0))
        
        # 电离气体云
        for gas_particle in range(30):
            gas_angle = gas_particle * 0.3
            gas_dist = 10 + 35 * random.random()
            gas_x = 60 + math.cos(gas_angle) * gas_dist
            gas_y = 50 + math.sin(gas_angle) * gas_dist
            gas_alpha = int(120 * (1 - (gas_dist - 10) / 35))
            
            if gas_alpha > 20:
                pygame.draw.circle(s, (150, 255, 255, gas_alpha), (int(gas_x), int(gas_y)), 2)
        
        return s
    
    elif model_style == "thunderbird_ex5":
        # 音游节拍 - 下落天堂
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        
        # 基础圆形
        pygame.draw.circle(plane_surf, c, center, 45)
        pygame.draw.circle(plane_surf, edge_color, center, 45, 3)
        
        # 轨道线
        track_count = 4
        track_width = 20
        for i in range(track_count):
            track_x = center[0] - track_width * 1.5 + i * track_width
            pygame.draw.line(plane_surf, (100, 100, 150), (track_x, center[1] - 30), (track_x, center[1] + 30), 1)
        
        # 下落音符
        for i in range(12):
            note_phase = (t * 3 + i * 0.3) % 1.0
            track_idx = i % track_count
            note_x = center[0] - track_width * 1.5 + track_idx * track_width
            note_y = center[1] - 30 + note_phase * 60
            
            note_type = i % 3
            if note_type == 0:
                note_color = (255, 100, 150)
                pygame.draw.circle(plane_surf, note_color, (int(note_x), int(note_y)), 4)
            elif note_type == 1:
                note_color = (100, 255, 150)
                pygame.draw.rect(plane_surf, note_color, (note_x - 3, note_y, 6, 15))
            else:
                note_color = (150, 100, 255)
                pygame.draw.polygon(plane_surf, note_color, [(note_x, note_y), (note_x - 5, note_y + 8), (note_x + 5, note_y + 8)])
            
            # Perfect判定特效
            if 0.85 < note_phase < 0.95:
                perfect_size = int((0.95 - note_phase) * 100)
                pygame.draw.circle(plane_surf, (255, 255, 100), (int(note_x), int(center[1] + 25)), perfect_size, 2)
        return plane_surf
    
    return None
