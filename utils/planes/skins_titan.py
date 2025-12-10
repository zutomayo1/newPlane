"""
Titan 专属涂装渲染模块
包含: mega_fortress, nuclear_core, volcanic_rage, steel_giant, crystal, hell_lord, space_station
"""
import pygame
import math
import random

# Titan 专属涂装列表
TITAN_STYLES = [
    'mega_fortress', 'nuclear_core', 'volcanic_rage', 'steel_giant',
    'crystal', 'hell_lord', 'space_station',
    'titan_ex', 'titan_ex2', 'titan_ex3', 'titan_ex4', 'titan_ex5'
]

def is_titan_style(model_style):
    """检查是否为 Titan 专属涂装"""
    return model_style in TITAN_STYLES

def render_titan_skin(s, model_style, c, edge_color, t, pulse):
    """渲染 Titan 专属涂装"""
    
    if model_style == "mega_fortress":
        # 移动要塞·钢铁堡垒 - 层叠装甲板、多炮塔、防御塔形态
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.1 + 1
        
        # 主体：层叠装甲板（方形堡垒）
        armor_layers = [
            (70, 60, (120, 120, 120)),
            (60, 50, (140, 140, 140)),
            (50, 40, (160, 160, 160)),
        ]
        for layer_w, layer_h, color in armor_layers:
            pygame.draw.rect(s, color, (60 - layer_w//2, 50 - layer_h//2, layer_w, layer_h))
            pygame.draw.rect(s, (200, 200, 200), (60 - layer_w//2, 50 - layer_h//2, layer_w, layer_h), 2)
        
        # 主炮塔
        pygame.draw.rect(s, (100, 100, 100), (50, 30, 20, 12))
        pygame.draw.rect(s, (180, 180, 180), (56, 24, 8, 8))
        
        # 副炮塔
        for side_x in [35, 85]:
            pygame.draw.rect(s, (110, 110, 110), (side_x - 8, 45, 16, 10))
            pygame.draw.circle(s, (150, 150, 150), (side_x, 50), 3)
        
        # 防御塔
        for corner_x, corner_y in [(40, 35), (80, 35), (40, 65), (80, 65)]:
            pygame.draw.polygon(s, (130, 130, 130), [
                (corner_x, corner_y - 6),
                (corner_x - 5, corner_y + 2),
                (corner_x + 5, corner_y + 2),
            ])
        
        # 工业烟雾
        smoke_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            smoke_offset = math.sin(t * 2 + i * math.pi / 4) * 5
            smoke_x = 60 + smoke_offset
            smoke_y = 70 + i * 8
            pygame.draw.circle(smoke_surface, (80, 80, 80, 120), (int(smoke_x), int(smoke_y)), int(8 + i * pulse))
        s.blit(smoke_surface, (0, 0))
        return s
    
    elif model_style == "nuclear_core":
        # 核动力泰坦·裂变反应堆
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        pygame.draw.circle(s, (50, 50, 50), (60, 50), 28)
        pygame.draw.circle(s, (0, 200, 100), (60, 50), 24, 3)
        
        core_size = int(18 * pulse)
        core_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(core_glow, (0, 255, 120, 200), (60, 50), core_size)
        pygame.draw.circle(core_glow, (120, 255, 60, 150), (60, 50), core_size + 5)
        pygame.draw.circle(core_glow, (220, 255, 100, 80), (60, 50), core_size + 10)
        s.blit(core_glow, (0, 0))
        
        for i in range(3):
            wave_radius = (t * 40 + i * 20) % 60
            wave_alpha = int(200 * (1 - wave_radius / 60))
            wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, (0, 255, 120, wave_alpha), (60, 50), int(wave_radius), 2)
            s.blit(wave_surface, (0, 0))
        
        for i in range(12):
            particle_angle = t * 4 + i * math.pi / 6
            particle_dist = 35 + 5 * math.sin(t * 3 + i)
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            pygame.draw.circle(s, (120, 255, 60), (int(px), int(py)), 3)
            p_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(p_glow, (120, 255, 60, 100), (int(px), int(py)), 5)
            s.blit(p_glow, (0, 0))
        
        symbol_angle = t * 2
        for i in range(3):
            angle = symbol_angle + i * 2 * math.pi / 3
            sx = 60 + math.cos(angle) * 20
            sy = 50 + math.sin(angle) * 20
            pygame.draw.circle(s, (255, 255, 0), (int(sx), int(sy)), 4)
            pygame.draw.line(s, (255, 255, 0), (60, 50), (int(sx), int(sy)), 2)
        return s
    
    elif model_style == "volcanic_rage":
        # 熔岩巨兽·火山之怒
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.15 + 1
        
        body_points = [(60, 30), (80, 45), (75, 65), (60, 70), (45, 65), (40, 45)]
        pygame.draw.polygon(s, (60, 30, 0), body_points)
        pygame.draw.polygon(s, (100, 50, 0), body_points, 2)
        
        magma_cracks = [
            [(50, 35), (55, 45), (52, 55)],
            [(65, 40), (68, 50), (70, 60)],
            [(55, 58), (60, 65), (65, 62)],
        ]
        for crack in magma_cracks:
            for i in range(len(crack) - 1):
                pygame.draw.line(s, (255, 120, 0), crack[i], crack[i+1], 3)
                crack_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(crack_glow, (255, 220, 50, 150), crack[i], crack[i+1], 6)
                s.blit(crack_glow, (0, 0))
        
        eruption_y = 20 - int(10 * pulse)
        for i in range(5):
            spark_x = 60 + (i - 2) * 8
            spark_y = eruption_y + i * 3
            pygame.draw.circle(s, (255, 100, 0), (spark_x, spark_y), 3)
            pygame.draw.line(s, (255, 150, 0), (spark_x, spark_y), (spark_x, spark_y + 10), 1)
        
        for i in range(8):
            rock_angle = t * 2 + i * math.pi / 4
            rock_dist = 30 + 15 * math.sin(t * 3 + i)
            rock_x = 60 + math.cos(rock_angle) * rock_dist
            rock_y = 50 + math.sin(rock_angle) * rock_dist
            pygame.draw.rect(s, (80, 40, 0), (int(rock_x) - 3, int(rock_y) - 3, 6, 6))
            fire_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(fire_glow, (255, 100, 0, 150), (int(rock_x), int(rock_y)), 5)
            s.blit(fire_glow, (0, 0))
        
        hell_fire = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            fire_x = 40 + i * 8
            fire_height = 10 + 5 * math.sin(t * 5 + i)
            pygame.draw.polygon(hell_fire, (255, 100, 0, 180), [
                (fire_x, 80), (fire_x - 3, 80 - fire_height), (fire_x + 3, 80 - fire_height),
            ])
        s.blit(hell_fire, (0, 0))
        return s
    
    elif model_style == "steel_giant":
        # 机甲战神·钢铁巨人
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.1 + 1
        
        pygame.draw.rect(s, (0, 150, 200), (50, 40, 20, 25))
        pygame.draw.rect(s, (255, 180, 0), (50, 40, 20, 25), 2)
        
        for shoulder_x in [48, 72]:
            pygame.draw.circle(s, (100, 100, 100), (shoulder_x, 45), 6)
            pygame.draw.circle(s, (255, 180, 0), (shoulder_x, 45), 6, 2)
            piston_offset = int(5 * math.sin(t * 3))
            pygame.draw.line(s, (150, 150, 150), (shoulder_x, 45), (shoulder_x, 55 + piston_offset), 3)
        
        for side_x, phase in [(35, 0), (85, math.pi)]:
            cylinder_length = 15 + int(5 * math.sin(t * 2.5 + phase))
            pygame.draw.rect(s, (120, 120, 120), (side_x - 3, 45, 6, cylinder_length))
            pygame.draw.circle(s, (200, 200, 0), (side_x, 45 + cylinder_length), 4)
        
        for weapon_x in [40, 80]:
            pygame.draw.rect(s, (80, 80, 80), (weapon_x - 5, 50, 10, 8))
            pygame.draw.rect(s, (200, 50, 0), (weapon_x - 2, 45, 4, 6))
            pygame.draw.polygon(s, (255, 100, 0), [
                (weapon_x, 45), (weapon_x - 2, 48), (weapon_x + 2, 48),
            ])
        
        thruster_positions = [(52, 68), (58, 68), (62, 68), (68, 68)]
        for tx, ty in thruster_positions:
            pygame.draw.rect(s, (60, 60, 60), (tx - 2, ty, 4, 6))
            flame_length = int(12 * pulse)
            flame_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(flame_surface, (100, 200, 255, 200), [
                (tx, ty + 6), (tx - 3, ty + 6 + flame_length), (tx + 3, ty + 6 + flame_length),
            ])
            s.blit(flame_surface, (0, 0))
        
        for bolt_x, bolt_y in [(54, 42), (66, 42), (54, 60), (66, 60)]:
            pygame.draw.circle(s, (180, 180, 180), (bolt_x, bolt_y), 2)
        return s
    
    elif model_style == "crystal":
        # 晶簇装甲·永恒之冰
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.1 + 1
        
        pygame.draw.polygon(s, (150, 220, 255), [(60, 35), (70, 50), (60, 65), (50, 50)])
        pygame.draw.polygon(s, (200, 255, 255), [(60, 35), (70, 50), (60, 65), (50, 50)], 2)
        
        for i in range(6):
            crystal_angle = i * math.pi / 3 + t * 0.5
            cx = 60 + math.cos(crystal_angle) * 25
            cy = 50 + math.sin(crystal_angle) * 25
            crystal_points = [(cx, cy - 8), (cx + 5, cy), (cx, cy + 8), (cx - 5, cy)]
            pygame.draw.polygon(s, (180, 240, 255), crystal_points)
            pygame.draw.polygon(s, (200, 255, 255), crystal_points, 1)
        
        refraction_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            ray_angle = t * 3 + i * math.pi / 4
            ray_length = 40 + 10 * math.sin(t * 2 + i)
            ray_x = 60 + math.cos(ray_angle) * ray_length
            ray_y = 50 + math.sin(ray_angle) * ray_length
            pygame.draw.line(refraction_surface, (200, 255, 255, 100), (60, 50), (int(ray_x), int(ray_y)), 2)
        s.blit(refraction_surface, (0, 0))
        
        for i in range(16):
            spiral_angle = t * 4 + i * math.pi / 8
            spiral_dist = 20 + 15 * (i / 16)
            px = 60 + math.cos(spiral_angle) * spiral_dist
            py = 50 + math.sin(spiral_angle) * spiral_dist
            pygame.draw.circle(s, (180, 240, 255), (int(px), int(py)), 2)
            sparkle = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(sparkle, (200, 255, 255, 150), (int(px), int(py)), 4)
            s.blit(sparkle, (0, 0))
        
        for i in range(3):
            halo_radius = 30 + i * 8
            halo_alpha = int(100 * (1 - i / 3) * pulse)
            halo_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(halo_surface, (200, 255, 255, halo_alpha), (60, 50), halo_radius, 1)
            s.blit(halo_surface, (0, 0))
        return s
    
    elif model_style == "hell_lord":
        # 恶魔战车·地狱领主
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.15 + 1
        
        pygame.draw.ellipse(s, (60, 0, 0), (45, 40, 30, 20))
        pygame.draw.ellipse(s, (120, 0, 0), (45, 40, 30, 20), 2)
        
        gate_width = int(20 * pulse)
        gate_height = 25
        pygame.draw.rect(s, (30, 0, 0), (60 - gate_width//2, 38, gate_width, gate_height))
        gate_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.rect(gate_glow, (200, 30, 0, 150), (60 - gate_width//2 - 3, 35, gate_width + 6, gate_height + 6), 3)
        s.blit(gate_glow, (0, 0))
        
        wing_offset = int(10 * math.sin(t * 2))
        left_wing_points = [(50, 50), (30 - wing_offset, 40), (25 - wing_offset, 50), (30 - wing_offset, 60)]
        pygame.draw.polygon(s, (100, 0, 0), left_wing_points)
        pygame.draw.polygon(s, (180, 0, 0), left_wing_points, 2)
        right_wing_points = [(70, 50), (90 + wing_offset, 40), (95 + wing_offset, 50), (90 + wing_offset, 60)]
        pygame.draw.polygon(s, (100, 0, 0), right_wing_points)
        pygame.draw.polygon(s, (180, 0, 0), right_wing_points, 2)
        
        for i in range(10):
            blood_angle = t * 4 + i * math.pi / 5
            blood_dist = 30 + 10 * math.sin(t * 3 + i)
            bx = 60 + math.cos(blood_angle) * blood_dist
            by = 50 + math.sin(blood_angle) * blood_dist
            pygame.draw.circle(s, (200, 30, 0), (int(bx), int(by)), 3)
            pygame.draw.line(s, (150, 20, 0), (int(bx), int(by)), 
                           (int(bx - math.cos(blood_angle) * 5), int(by - math.sin(blood_angle) * 5)), 2)
        
        hell_fire = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            fire_angle = i * math.pi / 4
            fx = 60 + math.cos(fire_angle) * 28
            fy = 50 + math.sin(fire_angle) * 28
            fire_height = 8 + 5 * math.sin(t * 5 + i)
            pygame.draw.polygon(hell_fire, (200, 30, 0, 200), [
                (fx, fy), (fx - 3, fy - fire_height), (fx + 3, fy - fire_height),
            ])
        s.blit(hell_fire, (0, 0))
        
        for i in range(3):
            soul_angle = t * 2 + i * 2 * math.pi / 3
            soul_dist = 35 + 5 * math.sin(t * 4 + i)
            sx = 60 + math.cos(soul_angle) * soul_dist
            sy = 50 + math.sin(soul_angle) * soul_dist
            pygame.draw.circle(s, (100, 50, 50), (int(sx), int(sy)), 6)
            pygame.draw.circle(s, (255, 0, 0), (int(sx) - 2, int(sy) - 1), 2)
            pygame.draw.circle(s, (255, 0, 0), (int(sx) + 2, int(sy) - 1), 2)
        return s
    
    elif model_style == "space_station":
        # 轨道轰炸机·天基武库
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.1 + 1
        
        platform_points = []
        for i in range(6):
            angle = i * math.pi / 3
            px = 60 + math.cos(angle) * 25
            py = 50 + math.sin(angle) * 25
            platform_points.append((px, py))
        pygame.draw.polygon(s, (200, 200, 220), platform_points)
        pygame.draw.polygon(s, (240, 240, 255), platform_points, 3)
        
        pygame.draw.circle(s, (255, 255, 255), (60, 50), 10)
        pygame.draw.circle(s, (240, 240, 255), (60, 50), 10, 2)
        
        for i in range(6):
            cannon_angle = i * math.pi / 3 + t * 0.5
            cannon_dist = 25
            cannon_x = 60 + math.cos(cannon_angle) * cannon_dist
            cannon_y = 50 + math.sin(cannon_angle) * cannon_dist
            pygame.draw.circle(s, (180, 180, 200), (int(cannon_x), int(cannon_y)), 5)
            barrel_x = cannon_x + math.cos(cannon_angle) * 8
            barrel_y = cannon_y + math.sin(cannon_angle) * 8
            pygame.draw.line(s, (220, 220, 255), (int(cannon_x), int(cannon_y)), (int(barrel_x), int(barrel_y)), 3)
            if i % 2 == 0:
                plasma_x = barrel_x + math.cos(cannon_angle) * 10
                plasma_y = barrel_y + math.sin(cannon_angle) * 10
                plasma_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(plasma_glow, (220, 220, 255, 200), (int(plasma_x), int(plasma_y)), 4)
                pygame.draw.circle(plasma_glow, (255, 255, 255, 100), (int(plasma_x), int(plasma_y)), 7)
                s.blit(plasma_glow, (0, 0))
        
        beam_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            angle1 = i * math.pi / 3 + t * 0.5
            angle2 = (i + 2) % 6 * math.pi / 3 + t * 0.5
            x1 = 60 + math.cos(angle1) * 25
            y1 = 50 + math.sin(angle1) * 25
            x2 = 60 + math.cos(angle2) * 25
            y2 = 50 + math.sin(angle2) * 25
            pygame.draw.line(beam_surface, (220, 220, 255, 100), (int(x1), int(y1)), (int(x2), int(y2)), 2)
        s.blit(beam_surface, (0, 0))
        
        for i in range(3):
            laser_x = 50 + i * 10
            laser_length = 30 + int(10 * pulse)
            laser_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(laser_surface, (255, 255, 255, 200), (laser_x, 60), (laser_x, 60 + laser_length), 2)
            pygame.draw.circle(laser_surface, (255, 255, 255, 150), (laser_x, 60 + laser_length), 5)
            s.blit(laser_surface, (0, 0))
        
        for i in range(2):
            shield_radius = 35 + i * 8 + int(5 * pulse)
            shield_alpha = int(80 * (1 - i / 2))
            shield_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (220, 220, 255, shield_alpha), (60, 50), shield_radius, 2)
            s.blit(shield_surface, (0, 0))
        return s

    elif model_style == "titan_ex":
        # 重装巨锤 - 锤形机体，冲击波扩散
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 锤头（巨大矩形）
        hammer_rect = pygame.Rect(30, 20, 60, 40)
        pygame.draw.rect(s, (100, 100, 100), hammer_rect)
        pygame.draw.rect(s, (150, 150, 150), hammer_rect, 4)
        
        # 锤柄
        pygame.draw.rect(s, (80, 80, 80), (52, 60, 16, 35))
        
        # 冲击波（扩散圆环）
        for i in range(3):
            wave_radius = (t * 60 + i * 25) % 75
            wave_alpha = int(200 * (1 - wave_radius / 75))
            wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surf, (255, 200, 0, wave_alpha), (60, 40), int(wave_radius), 3)
            s.blit(wave_surf, (0, 0))
        
        # 能量脉冲
        pygame.draw.circle(s, (255, 150, 0), (60, 40), int(12 * pulse))
        
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

    elif model_style == "titan_ex3":
        # 符文巨像 - 古代守护者
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 巨像主体（巨大石块）
        golem_body = [(60, 20), (80, 35), (85, 60), (70, 80), (50, 80), (35, 60), (40, 35)]
        pygame.draw.polygon(s, (120, 90, 60), golem_body)
        pygame.draw.polygon(s, (150, 120, 80), golem_body, 4)
        
        # 古代符文（发光刻纹）
        runes = [
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

    elif model_style == "titan_ex4":
        # 熔岩巨兽 - 地核之怒
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 熔岩裂缝网络（像地壳裂开）
        crack_lines = 8
        for crack in range(crack_lines):
            crack_angle = crack * math.pi / 4 + math.sin(t * 0.5) * 0.2
            
            # 裂缝主干
            crack_points = [(60, 50)]
            segments = 8
            for seg in range(1, segments + 1):
                seg_dist = seg * 6
                seg_angle = crack_angle + (random.random() - 0.5) * 0.3
                seg_x = 60 + math.cos(seg_angle) * seg_dist
                seg_y = 50 + math.sin(seg_angle) * seg_dist
                crack_points.append((int(seg_x), int(seg_y)))
            
            # 裂缝发光（从内部发出红光）
            for i in range(len(crack_points) - 1):
                glow_intensity = 1 - (i / len(crack_points))
                glow_brightness = int(200 * glow_intensity)
                
                # 多层发光
                for glow_layer in range(3):
                    glow_width = 6 - glow_layer * 2
                    glow_alpha = int(220 * glow_intensity - glow_layer * 40)
                    if glow_alpha > 30:
                        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                        # 颜色从白到黄到橙到红
                        if glow_layer == 0:
                            glow_color = (255, 255, 200)
                        elif glow_layer == 1:
                            glow_color = (255, glow_brightness, 50)
                        else:
                            glow_color = (glow_brightness, 50, 0)
                        
                        pygame.draw.line(glow_surf, (*glow_color, glow_alpha),
                                       crack_points[i], crack_points[i + 1], glow_width)
                        s.blit(glow_surf, (0, 0))
        
        # 熔岩气泡（上升）
        for bubble in range(15):
            bubble_progress = (t * 1.5 + bubble * 0.2) % 1
            bubble_angle = bubble * 0.6 + math.sin(t + bubble) * 0.3
            bubble_start_dist = 10
            bubble_dist = bubble_start_dist + bubble_progress * 40
            bx = 60 + math.cos(bubble_angle) * bubble_dist
            by = 50 + math.sin(bubble_angle) * bubble_dist
            
            # 气泡大小随上升而变大
            bubble_size = int(3 + bubble_progress * 5)
            bubble_alpha = int(220 * (1 - bubble_progress))
            
            if bubble_alpha > 30:
                # 橙红色气泡
                pygame.draw.circle(s, (255, 100 + int(100 * (1 - bubble_progress)), 0, bubble_alpha),
                                 (int(bx), int(by)), bubble_size)
                # 气泡边缘更亮
                pygame.draw.circle(s, (255, 200, 100, bubble_alpha), (int(bx), int(by)), bubble_size, 1)
        
        # 岩浆脉动（中心）
        pulse_intensity = (math.sin(t * 2.5) + 1) / 2
        for pulse_ring in range(5, 0, -1):
            pulse_radius = int(15 * pulse_intensity * (pulse_ring / 5))
            pulse_brightness = int(200 + 55 * pulse_intensity)
            pulse_color = (255, pulse_brightness // 2, 0)
            pygame.draw.circle(s, pulse_color, (60, 50), pulse_radius)
        
        # 火星飞溅
        for spark in range(20):
            if (int(t * 10) + spark) % 7 < 3:
                spark_angle = spark * 0.5 + t * 3
                spark_dist = 20 + 30 * random.random()
                spark_x = 60 + math.cos(spark_angle) * spark_dist
                spark_y = 50 + math.sin(spark_angle) * spark_dist
                spark_brightness = int(200 + 55 * random.random())
                
                # 小火星
                pygame.draw.circle(s, (255, spark_brightness, 0), (int(spark_x), int(spark_y)), 2)
        
        # 热浪扭曲（环形波）
        for heat_ring in range(3):
            heat_progress = (t * 1.5 + heat_ring * 0.4) % 1
            heat_radius = int(20 + heat_progress * 35)
            heat_alpha = int(150 * (1 - heat_progress))
            
            if heat_alpha > 30:
                # 扭曲的圆环
                heat_points = []
                for i in range(16):
                    heat_angle = i * math.pi / 8
                    distortion = 5 * math.sin(t * 3 + i + heat_ring)
                    hx = 60 + math.cos(heat_angle) * (heat_radius + distortion)
                    hy = 50 + math.sin(heat_angle) * (heat_radius + distortion)
                    heat_points.append((int(hx), int(hy)))
                
                if len(heat_points) > 2:
                    heat_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.polygon(heat_surf, (255, 150, 50, heat_alpha), heat_points, 2)
                    s.blit(heat_surf, (0, 0))
        
        return s

    elif model_style == "titan_ex5":
        # 几何变形·欧几里得
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        morph_phase = t % 4.0
        
        # 计算当前形状
        shape_idx = int(morph_phase)
        
        for layer in range(4):
            radius = 40 - layer * 8
            rotation = t + layer * 0.5
            
            if shape_idx == 0:
                sides = 3
            elif shape_idx == 1:
                sides = 4
            elif shape_idx == 2:
                sides = 5
            else:
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
                pygame.draw.polygon(plane_surf, (r, g, b), points, 3)
        return plane_surf
    
    return None
