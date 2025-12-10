# Solar 专属涂装渲染模块
# 包含: sun_god, phoenix, fusion, flare, corona, supernova, eclipse

import pygame
import math
import random

# Solar涂装列表
SOLAR_STYLES = ["sun_god", "phoenix", "fusion", "flare", "corona", "supernova", "eclipse", "solar_ex", "solar_ex2", "solar_ex3", "solar_ex4", "solar_ex5"]

def is_solar_style(model_style):
    """检查是否为Solar涂装"""
    return model_style in SOLAR_STYLES

def render_solar_skin(s, c, model_style, t, pid, static=False):
    """渲染Solar涂装，返回Surface或None"""
    
    if model_style == "sun_god":
        # 太阳神拉·审判 - 太阳神形态、神圣光芒、审判之光
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：太阳神核心
        sun_core = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(sun_core, (255, 200, 0, 250), (60, 50), 18)
        pygame.draw.circle(sun_core, (255, 255, 100, 220), (60, 50), int(18 * pulse))
        s.blit(sun_core, (0, 0))
        
        # 太阳神光环（多层）
        for i in range(4):
            ring_radius = 22 + i * 8 + int(6 * pulse)
            ring_alpha = int(200 * (1 - i / 4))
            ring_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(ring_surface, (255, 220, 50, ring_alpha), (60, 50), ring_radius, 3)
            s.blit(ring_surface, (0, 0))
        
        # 神圣光芒（放射状）
        ray_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(16):
            ray_angle = t * 1.5 + i * math.pi / 8
            ray_length = 30 + 15 * math.sin(t * 3 + i)
            ray_x = 60 + math.cos(ray_angle) * ray_length
            ray_y = 50 + math.sin(ray_angle) * ray_length
            pygame.draw.line(ray_surface, (255, 255, 100, 220), (60, 50), (int(ray_x), int(ray_y)), 3)
        s.blit(ray_surface, (0, 0))
        
        # 审判之眼（神之凝视）
        eye_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(eye_glow, (255, 255, 200, 250), (60, 50), int(8 * pulse))
        pygame.draw.circle(eye_glow, (255, 200, 0, 200), (60, 50), 6)
        s.blit(eye_glow, (0, 0))
        
        # 神圣粒子
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            particle_angle = t * 2 + i * math.pi / 10
            particle_dist = 25 + 15 * (i / 20)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            pygame.draw.circle(particle_surface, (255, 255, 200, 220), (int(particle_x), int(particle_y)), 2)
        s.blit(particle_surface, (0, 0))
        
        return s
    
    elif model_style == "phoenix":
        # 太阳凤凰·永恒烈焰 - 凤凰形态、涅槃之火、不灭烈焰
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：凤凰身躯
        phoenix_body = [(60, 30), (70, 45), (68, 60), (52, 60), (50, 45)]
        pygame.draw.polygon(s, (255, 100, 0), phoenix_body)
        pygame.draw.polygon(s, (255, 200, 0), phoenix_body, 2)
        
        # 凤凰头冠
        crown_points = [(60, 25), (65, 30), (63, 20), (57, 20), (55, 30)]
        for i, point in enumerate(crown_points):
            flame_y = point[1] - int(5 * math.sin(t * 5 + i))
            pygame.draw.line(s, (255, 150, 0), point, (point[0], flame_y), 2)
            pygame.draw.circle(s, (255, 200, 0), (point[0], flame_y), 2)
        
        # 凤凰翅膀（火焰翅膀）
        for side in [-1, 1]:
            wing_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            for i in range(8):
                wing_angle = side * (math.pi / 3) + i * 0.2 + math.sin(t * 4 + i) * 0.3
                wing_dist = 15 + i * 3
                wing_x = 60 + math.cos(wing_angle) * wing_dist
                wing_y = 48 + math.sin(wing_angle) * wing_dist
                # 火焰羽毛
                flame_length = 8 + int(4 * math.sin(t * 5 + i))
                flame_tip_x = wing_x + math.cos(wing_angle) * flame_length
                flame_tip_y = wing_y + math.sin(wing_angle) * flame_length
                pygame.draw.line(wing_surface, (255, 100, 0, 220), (int(wing_x), int(wing_y)), 
                               (int(flame_tip_x), int(flame_tip_y)), 3)
                pygame.draw.circle(wing_surface, (255, 200, 0, 220), (int(flame_tip_x), int(flame_tip_y)), 2)
            s.blit(wing_surface, (0, 0))
        
        # 凤凰尾羽（火焰尾迹）
        tail_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            tail_angle = math.pi / 2 + (i - 5) * 0.1 + math.sin(t * 3 + i) * 0.2
            tail_dist = 15 + i * 4
            tail_x = 60 + math.cos(tail_angle) * tail_dist
            tail_y = 60 + math.sin(tail_angle) * tail_dist
            tail_alpha = int(220 - i * 15)
            pygame.draw.circle(tail_surface, (255, 150, 0, tail_alpha), (int(tail_x), int(tail_y)), 4 - i // 3)
        s.blit(tail_surface, (0, 0))
        
        # 涅槃之火（环绕火焰）
        fire_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(16):
            fire_angle = t * 4 + i * math.pi / 8
            fire_dist = 22 + 8 * math.sin(t * 3 + i)
            fire_x = 60 + math.cos(fire_angle) * fire_dist
            fire_y = 48 + math.sin(fire_angle) * fire_dist
            pygame.draw.circle(fire_surface, (255, 100, 0, 220), (int(fire_x), int(fire_y)), 3)
        s.blit(fire_surface, (0, 0))
        
        # 不灭烈焰（核心脉冲）
        for i in range(3):
            flame_radius = 15 + i * 8 + int(8 * pulse)
            flame_alpha = int(180 * (1 - i / 3))
            flame_ring = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(flame_ring, (255, 150, 0, flame_alpha), (60, 48), flame_radius, 2)
            s.blit(flame_ring, (0, 0))
        
        return s
    
    elif model_style == "fusion":
        # 核聚变·恒星之心 - 核聚变反应、氢氦燃烧、聚变能量
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：聚变核心
        core_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(core_surface, (100, 150, 255, 250), (60, 50), 15)
        pygame.draw.circle(core_surface, (200, 220, 255, 230), (60, 50), int(15 * pulse))
        s.blit(core_surface, (0, 0))
        
        # 核聚变反应环（多层等离子环）
        for i in range(4):
            ring_angle = t * 2 + i * math.pi / 2
            ring_tilt = 0.3
            # 椭圆环（模拟3D效果）
            ring_radius = 20 + i * 6
            ring_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            ring_alpha = int(200 * (1 - i / 4))
            # 绘制椭圆轨道
            pygame.draw.ellipse(ring_surface, (150, 180, 255, ring_alpha), 
                              (60 - ring_radius, 50 - int(ring_radius * ring_tilt), 
                               ring_radius * 2, int(ring_radius * ring_tilt * 2)), 2)
            s.blit(ring_surface, (0, 0))
        
        # 氢氦原子粒子（环绕运动）
        atom_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            atom_angle = t * 3 + i * math.pi / 6
            atom_dist = 22 + 8 * math.sin(t * 2 + i)
            atom_x = 60 + math.cos(atom_angle) * atom_dist
            atom_y = 50 + math.sin(atom_angle) * atom_dist
            # 氢（蓝色）和氦（白色）交替
            if i % 2 == 0:
                pygame.draw.circle(atom_surface, (150, 200, 255, 220), (int(atom_x), int(atom_y)), 3)
            else:
                pygame.draw.circle(atom_surface, (255, 255, 255, 220), (int(atom_x), int(atom_y)), 3)
        s.blit(atom_surface, (0, 0))
        
        # 聚变能量释放（能量波）
        for i in range(3):
            wave_radius = (t * 60 + i * 30) % 90
            wave_alpha = int(220 * (1 - wave_radius / 90))
            wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, (200, 220, 255, wave_alpha), (60, 50), int(wave_radius), 3)
            s.blit(wave_surface, (0, 0))
        
        # 高能光子
        photon_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            photon_angle = t * 4 + i * math.pi / 10
            photon_dist = 15 + ((t * 40 + i * 4) % 30)
            photon_x = 60 + math.cos(photon_angle) * photon_dist
            photon_y = 50 + math.sin(photon_angle) * photon_dist
            photon_alpha = int(220 * (1 - ((t * 40 + i * 4) % 30) / 30))
            pygame.draw.circle(photon_surface, (255, 255, 255, photon_alpha), (int(photon_x), int(photon_y)), 2)
        s.blit(photon_surface, (0, 0))
        
        return s
    
    elif model_style == "flare":
        # 日冕耀斑·太阳风暴 - 耀斑爆发、日冕物质抛射、太阳风
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：太阳表面
        sun_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(sun_surface, (255, 255, 200, 240), (60, 50), 16)
        pygame.draw.circle(sun_surface, (255, 255, 255, 220), (60, 50), int(16 * pulse))
        s.blit(sun_surface, (0, 0))
        
        # 日冕耀斑（巨大火焰喷射）
        for i in range(8):
            flare_angle = t + i * math.pi / 4
            flare_intensity = math.sin(t * 2 + i) * 0.5 + 0.5
            flare_length = 20 + 25 * flare_intensity
            flare_x = 60 + math.cos(flare_angle) * flare_length
            flare_y = 50 + math.sin(flare_angle) * flare_length
            
            # 耀斑主体
            flare_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            flare_width = int(8 * flare_intensity)
            pygame.draw.line(flare_surface, (255, 255, 200, 220), (60, 50), (int(flare_x), int(flare_y)), flare_width)
            # 耀斑尖端
            pygame.draw.circle(flare_surface, (255, 255, 255, 220), (int(flare_x), int(flare_y)), flare_width // 2)
            s.blit(flare_surface, (0, 0))
        
        # 日冕物质抛射（CME粒子流）
        cme_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(30):
            cme_angle = t * 1.5 + i * math.pi / 15
            cme_speed = 2 + (i % 3)
            cme_dist = 18 + ((t * 40 * cme_speed + i * 6) % 40)
            cme_x = 60 + math.cos(cme_angle) * cme_dist
            cme_y = 50 + math.sin(cme_angle) * cme_dist
            cme_alpha = int(220 * (1 - ((t * 40 * cme_speed + i * 6) % 40) / 40))
            pygame.draw.circle(cme_surface, (255, 255, 220, cme_alpha), (int(cme_x), int(cme_y)), 2)
        s.blit(cme_surface, (0, 0))
        
        # 太阳风粒子暴雨
        wind_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(25):
            wind_angle = t * 2.5 + i * math.pi / 12.5
            wind_dist = 15 + ((t * 50 + i * 5) % 35)
            wind_x = 60 + math.cos(wind_angle) * wind_dist
            wind_y = 50 + math.sin(wind_angle) * wind_dist
            pygame.draw.circle(wind_surface, (255, 255, 200, 200), (int(wind_x), int(wind_y)), 1)
        s.blit(wind_surface, (0, 0))
        
        return s
    
    elif model_style == "corona":
        # 日冕王冠·太阳之子 - 日冕光环、黄金光辉、太阳神形态
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：太阳核心
        core_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(core_glow, (255, 180, 100, 250), (60, 50), 14)
        pygame.draw.circle(core_glow, (255, 220, 150, 230), (60, 50), int(14 * pulse))
        s.blit(core_glow, (0, 0))
        
        # 日冕王冠（多层光环）
        for i in range(5):
            crown_radius = 18 + i * 6 + int(5 * pulse)
            crown_alpha = int(200 * (1 - i / 5))
            crown_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(crown_surface, (255, 200, 120, crown_alpha), (60, 50), crown_radius, 2)
            s.blit(crown_surface, (0, 0))
        
        # 王冠尖刺（辐射状）
        spike_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            spike_angle = i * math.pi / 6
            spike_base_dist = 20
            spike_length = 18 + 8 * math.sin(t * 3 + i)
            spike_base_x = 60 + math.cos(spike_angle) * spike_base_dist
            spike_base_y = 50 + math.sin(spike_angle) * spike_base_dist
            spike_tip_x = 60 + math.cos(spike_angle) * (spike_base_dist + spike_length)
            spike_tip_y = 50 + math.sin(spike_angle) * (spike_base_dist + spike_length)
            # 尖刺
            pygame.draw.line(spike_surface, (255, 220, 150, 220), (int(spike_base_x), int(spike_base_y)), 
                           (int(spike_tip_x), int(spike_tip_y)), 3)
            pygame.draw.circle(spike_surface, (255, 255, 200, 220), (int(spike_tip_x), int(spike_tip_y)), 2)
        s.blit(spike_surface, (0, 0))
        
        # 黄金光辉（环绕粒子）
        golden_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            golden_angle = t * 2 + i * math.pi / 10
            golden_dist = 25 + 10 * math.sin(t * 2.5 + i)
            golden_x = 60 + math.cos(golden_angle) * golden_dist
            golden_y = 50 + math.sin(golden_angle) * golden_dist
            pygame.draw.circle(golden_surface, (255, 220, 150, 220), (int(golden_x), int(golden_y)), 3)
        s.blit(golden_surface, (0, 0))
        
        # 太阳神光芒
        ray_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            ray_angle = t * 1.5 + i * math.pi / 4
            ray_length = 35 + 10 * math.sin(t * 3 + i)
            ray_x = 60 + math.cos(ray_angle) * ray_length
            ray_y = 50 + math.sin(ray_angle) * ray_length
            pygame.draw.line(ray_surface, (255, 200, 120, 200), (60, 50), (int(ray_x), int(ray_y)), 2)
        s.blit(ray_surface, (0, 0))
        
        return s
    
    elif model_style == "supernova":
        # 超新星·恒星爆炸 - 超新星爆发、恒星崩解、能量波扩散、星云形成
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.3 + 1
        
        # 主体：爆炸核心（极亮）
        core_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        core_size = int(12 * pulse)
        pygame.draw.circle(core_surface, (255, 255, 255, 250), (60, 50), core_size)
        pygame.draw.circle(core_surface, (255, 200, 255, 230), (60, 50), core_size + 4)
        pygame.draw.circle(core_surface, (255, 230, 255, 200), (60, 50), core_size + 8)
        s.blit(core_surface, (0, 0))
        
        # 超新星爆炸波（多层冲击波）
        for i in range(5):
            wave_phase = (t * 2 + i * 0.4) % 2
            wave_radius = 15 + wave_phase * 35
            wave_alpha = int(220 * (1 - wave_phase / 2))
            wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, (255, 230, 255, wave_alpha), (60, 50), int(wave_radius), 4)
            s.blit(wave_surface, (0, 0))
        
        # 恒星碎片（高速喷射）
        debris_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(30):
            debris_angle = i * math.pi / 15
            debris_speed = 1.5 + (i % 3) * 0.5
            debris_dist = 15 + ((t * 50 * debris_speed + i * 3) % 45)
            debris_x = 60 + math.cos(debris_angle) * debris_dist
            debris_y = 50 + math.sin(debris_angle) * debris_dist
            debris_alpha = int(240 * (1 - ((t * 50 * debris_speed + i * 3) % 45) / 45))
            # 碎片（彩色）
            hue = (i * 12) % 360
            r = int(200 + 55 * math.sin(math.radians(hue)))
            g = int(150 + 105 * math.sin(math.radians(hue + 120)))
            b = int(200 + 55 * math.sin(math.radians(hue + 240)))
            pygame.draw.circle(debris_surface, (r, g, b, debris_alpha), (int(debris_x), int(debris_y)), 3)
        s.blit(debris_surface, (0, 0))
        
        # 星云形成（扩散气体）
        nebula_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            nebula_angle = t + i * math.pi / 10
            nebula_dist = 20 + 20 * (i / 20) + 8 * math.sin(t * 2 + i)
            nebula_x = 60 + math.cos(nebula_angle) * nebula_dist
            nebula_y = 50 + math.sin(nebula_angle) * nebula_dist
            nebula_alpha = int(150 * (1 - (i / 20)))
            pygame.draw.circle(nebula_surface, (255, 200, 255, nebula_alpha), (int(nebula_x), int(nebula_y)), 5)
        s.blit(nebula_surface, (0, 0))
        
        # 辐射光线
        radiation_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(16):
            rad_angle = t * 2 + i * math.pi / 8
            rad_length = 30 + 15 * math.sin(t * 4 + i)
            rad_x = 60 + math.cos(rad_angle) * rad_length
            rad_y = 50 + math.sin(rad_angle) * rad_length
            pygame.draw.line(radiation_surface, (255, 255, 255, 200), (60, 50), (int(rad_x), int(rad_y)), 2)
        s.blit(radiation_surface, (0, 0))
        
        return s
    
    elif model_style == "eclipse":
        # 日全食·光暗交替 - 日食现象、光暗转换、日冕边缘、贝利珠
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.1 + 1
        
        # 主体：被遮挡的太阳
        sun_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(sun_surface, (255, 200, 0, 240), (60, 50), 18)
        s.blit(sun_surface, (0, 0))
        
        # 月球遮挡（黑色圆盘）
        moon_offset_x = int(8 * math.sin(t))
        moon_offset_y = int(4 * math.cos(t))
        moon_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(moon_surface, (50, 50, 100, 250), (60 + moon_offset_x, 50 + moon_offset_y), 16)
        s.blit(moon_surface, (0, 0))
        
        # 日冕边缘发光（环形光晕）
        corona_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(4):
            corona_radius = 20 + i * 4 + int(3 * pulse)
            corona_alpha = int(200 * (1 - i / 4))
            pygame.draw.circle(corona_surface, (255, 200, 0, corona_alpha), (60, 50), corona_radius, 2)
        s.blit(corona_surface, (0, 0))
        
        # 贝利珠效应（钻石环）
        bailey_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            if (int(t * 3) + i) % 4 < 2:  # 闪烁效果
                bailey_angle = i * math.pi / 4
                bailey_x = 60 + math.cos(bailey_angle) * 18
                bailey_y = 50 + math.sin(bailey_angle) * 18
                pygame.draw.circle(bailey_surface, (255, 255, 255, 250), (int(bailey_x), int(bailey_y)), 3)
                # 光晕
                pygame.draw.circle(bailey_surface, (255, 255, 200, 180), (int(bailey_x), int(bailey_y)), 5)
        s.blit(bailey_surface, (0, 0))
        
        # 日冕流（极光般的流动）
        streamer_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            streamer_angle = i * math.pi / 6 + t * 0.5
            streamer_length = 22 + 10 * math.sin(t * 2 + i)
            streamer_x = 60 + math.cos(streamer_angle) * streamer_length
            streamer_y = 50 + math.sin(streamer_angle) * streamer_length
            pygame.draw.line(streamer_surface, (255, 200, 0, 180), (60, 50), (int(streamer_x), int(streamer_y)), 2)
        s.blit(streamer_surface, (0, 0))
        
        # 光暗交替粒子
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(15):
            particle_angle = t * 2.5 + i * math.pi / 7.5
            particle_dist = 25 + 8 * math.sin(t * 3 + i)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            # 交替明暗
            if i % 2 == 0:
                pygame.draw.circle(particle_surface, (255, 200, 0, 220), (int(particle_x), int(particle_y)), 2)
            else:
                pygame.draw.circle(particle_surface, (100, 100, 150, 220), (int(particle_x), int(particle_y)), 2)
        s.blit(particle_surface, (0, 0))
        
        return s
    
    elif model_style == "solar_ex":
        # 耀斑之心 - 太阳核心，动态耀斑射线
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 太阳核心（多层辉光）
        for layer in range(5, 0, -1):
            layer_radius = int(18 * pulse * (layer / 5))
            layer_alpha = int(255 * (layer / 5))
            glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 200, 0, layer_alpha), (60, 50), layer_radius)
            s.blit(glow_surf, (0, 0))
        
        pygame.draw.circle(s, (255, 255, 100), (60, 50), 15)
        
        # 12道耀斑射线（动态长度）
        for i in range(12):
            flare_angle = i * math.pi / 6 + t * 0.5
            flare_length = 30 + 20 * math.sin(t * 3 + i)
            
            # 射线起点
            ray_start_x = 60 + math.cos(flare_angle) * 18
            ray_start_y = 50 + math.sin(flare_angle) * 18
            
            # 射线终点
            ray_end_x = 60 + math.cos(flare_angle) * (18 + flare_length)
            ray_end_y = 50 + math.sin(flare_angle) * (18 + flare_length)
            
            # 绘制渐变射线（多层）
            for layer in range(3):
                layer_width = 6 - layer * 2
                layer_alpha = int(220 - layer * 60)
                ray_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(ray_surf, (255, 150, 0, layer_alpha), 
                               (int(ray_start_x), int(ray_start_y)), 
                               (int(ray_end_x), int(ray_end_y)), layer_width)
                s.blit(ray_surf, (0, 0))
        
        # 日冕粒子
        for i in range(15):
            corona_angle = t * 2 + i * 0.4
            corona_dist = 25 + 15 * math.sin(t * 2.5 + i)
            cx = 60 + math.cos(corona_angle) * corona_dist
            cy = 50 + math.sin(corona_angle) * corona_dist
            pygame.draw.circle(s, (255, 200, 100), (int(cx), int(cy)), 3)
        
        return s
    
    elif model_style == "solar_ex2":
        # 雷电之神（宙斯） - 雷神锤，闪电链条
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 雷神锤头（巨大方锤）
        hammer_head = pygame.Rect(35, 30, 50, 30)
        pygame.draw.rect(s, (150, 150, 150), hammer_head)
        pygame.draw.rect(s, (200, 200, 200), hammer_head, 3)
        # 锤面雕刻（闪电纹）
        pygame.draw.line(s, (100, 100, 255), (40, 35), (50, 55), 2)
        pygame.draw.line(s, (100, 100, 255), (50, 55), (45, 55), 2)
        pygame.draw.line(s, (100, 100, 255), (70, 35), (75, 55), 2)
        pygame.draw.line(s, (100, 100, 255), (75, 55), (80, 55), 2)
        
        # 锤柄
        pygame.draw.rect(s, (100, 80, 60), (55, 60, 10, 30))
        
        # 闪电链条缠绕（4条）
        for chain_idx in range(4):
            chain_angle = chain_idx * math.pi / 2 + t * 2
            chain_dist = 30 + 10 * math.sin(t * 3 + chain_idx)
            cx = 60 + math.cos(chain_angle) * chain_dist
            cy = 45 + math.sin(chain_angle) * chain_dist
            # 闪电链条
            pygame.draw.line(s, (200, 200, 255), (60, 45), (int(cx), int(cy)), 3)
            # 链条末端电球
            ball_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(ball_surf, (220, 220, 255, 220), (int(cx), int(cy)), 6)
            s.blit(ball_surf, (0, 0))
        
        # 雷云环绕
        for cloud_idx in range(8):
            cloud_angle = t + cloud_idx * math.pi / 4
            cloud_dist = 35 + 8 * math.sin(t * 2 + cloud_idx)
            cloud_x = 60 + math.cos(cloud_angle) * cloud_dist
            cloud_y = 45 + math.sin(cloud_angle) * cloud_dist
            pygame.draw.circle(s, (100, 100, 150), (int(cloud_x), int(cloud_y)), 5)
        
        # 天降神雷（随机闪电）
        if int(t * 10) % 3 == 0:
            for bolt in range(3):
                bolt_x = 40 + bolt * 20
                bolt_points = [(bolt_x, 10)]
                for seg in range(5):
                    bolt_y = 10 + seg * 15
                    bolt_x += random.choice([-5, 0, 5])
                    bolt_points.append((bolt_x, bolt_y))
                pygame.draw.lines(s, (255, 255, 255), False, bolt_points, 2)
        
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
    
    elif model_style == "solar_ex5":  # 天气预报·气象万千
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        weather_cycle = int(t / 2) % 4
        
        if weather_cycle == 0:  # 晴天
            sun_size = int(15 + abs(math.sin(t * 2)) * 5)
            pygame.draw.circle(plane_surf, (255, 220, 100), center, sun_size)
            
            for i in range(8):
                ray_angle = t + i * 0.785
                ray_length = 25 + abs(math.sin(t * 3 + i)) * 10
                ray_x = center[0] + math.cos(ray_angle) * ray_length
                ray_y = center[1] + math.sin(ray_angle) * ray_length
                pygame.draw.line(plane_surf, (255, 220, 100), center, (ray_x, ray_y), 3)
        
        elif weather_cycle == 1:  # 雨天
            pygame.draw.circle(plane_surf, (150, 150, 150), center, 20)
            for i in range(25):
                rain_phase = (t * 5 + i * 0.1) % 1.0
                rain_x = center[0] + (i % 5 - 2) * 12
                rain_y = center[1] - 30 + rain_phase * 60
                pygame.draw.line(plane_surf, (100, 180, 255), 
                               (rain_x, rain_y), (rain_x - 2, rain_y + 8), 2)
        
        elif weather_cycle == 2:  # 雪天
            pygame.draw.circle(plane_surf, (200, 200, 200), center, 20)
            for i in range(20):
                snow_phase = (t * 2 + i * 0.15) % 1.0
                snow_x = center[0] + math.sin(t + i) * 30
                snow_y = center[1] - 30 + snow_phase * 60
                
                for branch in range(6):
                    branch_angle = (branch / 6.0) * 2 * math.pi
                    bx = snow_x + math.cos(branch_angle) * 4
                    by = snow_y + math.sin(branch_angle) * 4
                    pygame.draw.line(plane_surf, (255, 255, 255), (snow_x, snow_y), (bx, by), 1)
        
        else:  # 雷暴
            pygame.draw.circle(plane_surf, (80, 80, 80), center, 20)
            if int(t * 10) % 3 == 0:
                for i in range(5):
                    lightning_x = center[0] + (i - 2) * 10
                    lightning_y1 = center[1] - 25 + i * 10
                    lightning_y2 = lightning_y1 + 10
                    pygame.draw.line(plane_surf, (255, 255, 100), 
                                   (lightning_x, lightning_y1), (lightning_x + 6, lightning_y2), 3)
        return plane_surf
    
    return None
