# Eclipse 专属涂装渲染模块
# 包含: eclipse_moon, eclipse_void, eclipse_shadow, eclipse_abyss, eclipse_night, eclipse_dual, eclipse_cosmos

import pygame
import math

# Eclipse涂装列表
ECLIPSE_STYLES = ["eclipse_moon", "eclipse_void", "eclipse_shadow", "eclipse_abyss", "eclipse_night", "eclipse_dual", "eclipse_cosmos", "eclipse_ex", "eclipse_ex2", "eclipse_ex3", "eclipse_ex4", "eclipse_ex5"]

def is_eclipse_style(model_style):
    """检查是否为Eclipse涂装"""
    return model_style in ECLIPSE_STYLES

def render_eclipse_skin(s, c, model_style, t, pid, static=False):
    """渲染Eclipse涂装，返回Surface或None"""
    
    if model_style == "eclipse_moon":
        # 血月当空·月蚀之力 - 血月高悬、月蚀能量、血色月光、月神之力
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：血月（红色月亮）
        moon_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(moon_surface, (150, 0, 0, 240), (60, 50), 18)
        pygame.draw.circle(moon_surface, (255, 50, 50, 220), (60, 50), int(18 * pulse))
        s.blit(moon_surface, (0, 0))
        
        # 月蚀阴影（月面暗纹）
        shadow_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            shadow_x = 55 + i * 3
            shadow_y = 45 + int(8 * math.sin(t + i))
            pygame.draw.circle(shadow_surface, (100, 0, 0, 180), (shadow_x, shadow_y), 4)
        s.blit(shadow_surface, (0, 0))
        
        # 血色月光（放射状光芒）
        ray_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            ray_angle = t * 1.5 + i * math.pi / 6
            ray_length = 25 + 12 * math.sin(t * 3 + i)
            ray_x = 60 + math.cos(ray_angle) * ray_length
            ray_y = 50 + math.sin(ray_angle) * ray_length
            pygame.draw.line(ray_surface, (255, 50, 50, 200), (60, 50), (int(ray_x), int(ray_y)), 2)
        s.blit(ray_surface, (0, 0))
        
        # 月神之力（环绕粒子）
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            particle_angle = t * 2 + i * math.pi / 10
            particle_dist = 25 + 10 * math.sin(t * 2.5 + i)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            pygame.draw.circle(particle_surface, (180, 20, 20, 220), (int(particle_x), int(particle_y)), 3)
        s.blit(particle_surface, (0, 0))
        
        # 月蚀能量波
        for i in range(3):
            wave_radius = (t * 50 + i * 25) % 75
            wave_alpha = int(200 * (1 - wave_radius / 75))
            wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, (255, 50, 50, wave_alpha), (60, 50), int(wave_radius), 2)
            s.blit(wave_surface, (0, 0))
        
        return s
    
    elif model_style == "eclipse_void":
        # 虚空日食·黑洞边缘 - 虚空黑洞、引力透镜、事件视界、光线扭曲
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：黑洞核心（纯黑）
        blackhole_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(blackhole_surface, (0, 0, 0, 255), (60, 50), 14)
        s.blit(blackhole_surface, (0, 0))
        
        # 事件视界（紫色边缘）
        horizon_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(3):
            horizon_radius = 15 + i * 3 + int(2 * pulse)
            horizon_alpha = int(220 * (1 - i / 3))
            pygame.draw.circle(horizon_surface, (100, 0, 150, horizon_alpha), (60, 50), horizon_radius, 2)
        s.blit(horizon_surface, (0, 0))
        
        # 吸积盘（环状物质）
        disk_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            disk_angle = t * 3 + i * math.pi / 4
            # 椭圆轨道
            orbit_dist = 22 + 8 * math.sin(t * 2 + i)
            disk_x = 60 + math.cos(disk_angle) * orbit_dist
            disk_y = 50 + math.sin(disk_angle) * orbit_dist * 0.4  # 压扁效果
            pygame.draw.circle(disk_surface, (50, 0, 100, 220), (int(disk_x), int(disk_y)), 3)
        s.blit(disk_surface, (0, 0))
        
        # 引力透镜效应（扭曲光线）
        lens_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            lens_angle = i * math.pi / 6
            lens_dist = 28
            lens_x = 60 + math.cos(lens_angle) * lens_dist
            lens_y = 50 + math.sin(lens_angle) * lens_dist
            # 弯曲光线
            bend_offset = 8 * math.sin(t * 2 + i)
            bend_x = lens_x + math.cos(lens_angle + math.pi / 2) * bend_offset
            bend_y = lens_y + math.sin(lens_angle + math.pi / 2) * bend_offset
            pygame.draw.line(lens_surface, (100, 50, 150, 180), (int(lens_x), int(lens_y)), 
                           (int(bend_x), int(bend_y)), 2)
        s.blit(lens_surface, (0, 0))
        
        # 虚空粒子吸入
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            particle_angle = t * 4 + i * math.pi / 10
            particle_progress = ((t * 50 + i * 5) % 100) / 100
            particle_dist = 45 - particle_progress * 30
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            particle_alpha = int(220 * (1 - particle_progress))
            pygame.draw.circle(particle_surface, (100, 0, 150, particle_alpha), (int(particle_x), int(particle_y)), 2)
        s.blit(particle_surface, (0, 0))
        
        return s
    
    elif model_style == "eclipse_shadow":
        # 日食幽灵·暗影吞噬 - 日食阴影、黑暗吞食、暗影扩散、光暗界限
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：幽灵形态
        ghost_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        ghost_points = [(60, 25), (70, 40), (75, 60), (70, 75), (50, 75), (45, 60), (50, 40)]
        pygame.draw.polygon(ghost_surface, (30, 30, 50, 230), ghost_points)
        pygame.draw.polygon(ghost_surface, (80, 80, 120, 250), ghost_points, 2)
        s.blit(ghost_surface, (0, 0))
        
        # 暗影扩散（波动阴影）
        shadow_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            shadow_radius = 20 + i * 8 + int(6 * pulse)
            shadow_alpha = int(150 * (1 - i / 5))
            pygame.draw.circle(shadow_surface, (50, 50, 80, shadow_alpha), (60, 50), shadow_radius, 3)
        s.blit(shadow_surface, (0, 0))
        
        # 黑暗吞食（触手）
        tentacle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            tentacle_angle = t + i * math.pi / 4
            tentacle_segments = []
            for j in range(6):
                seg_dist = 15 + j * 4
                seg_angle = tentacle_angle + math.sin(t * 3 + i + j * 0.5) * 0.3
                seg_x = 60 + math.cos(seg_angle) * seg_dist
                seg_y = 50 + math.sin(seg_angle) * seg_dist
                tentacle_segments.append((seg_x, seg_y))
            # 绘制触手
            for j in range(len(tentacle_segments) - 1):
                pygame.draw.line(tentacle_surface, (30, 30, 50, 200), 
                               (int(tentacle_segments[j][0]), int(tentacle_segments[j][1])),
                               (int(tentacle_segments[j+1][0]), int(tentacle_segments[j+1][1])), 3)
        s.blit(tentacle_surface, (0, 0))
        
        # 光暗界限（边缘闪烁）
        border_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            if (int(t * 5) + i) % 3 < 2:
                border_angle = i * math.pi / 6
                border_x = 60 + math.cos(border_angle) * 35
                border_y = 50 + math.sin(border_angle) * 35
                pygame.draw.circle(border_surface, (80, 80, 120, 220), (int(border_x), int(border_y)), 3)
        s.blit(border_surface, (0, 0))
        
        return s
    
    elif model_style == "eclipse_abyss":
        # 深渊凝视·虚无吞噬 - 深渊裂缝、虚无力量、凝视毁灭、深渊吞噬
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：深渊之眼
        abyss_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(abyss_surface, (100, 0, 150, 250), (60, 50), 16)
        pygame.draw.circle(abyss_surface, (180, 50, 200, 230), (60, 50), int(16 * pulse))
        s.blit(abyss_surface, (0, 0))
        
        # 深渊瞳孔（凝视）
        pupil_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(pupil_surface, (50, 0, 100, 255), (60, 50), 8)
        # 恐怖高光
        pygame.draw.circle(pupil_surface, (150, 0, 200, 255), (62, 48), 2)
        s.blit(pupil_surface, (0, 0))
        
        # 深渊裂缝（放射状）
        crack_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            crack_angle = t + i * math.pi / 6
            crack_length = 20 + 15 * math.sin(t * 2 + i)
            crack_x = 60 + math.cos(crack_angle) * crack_length
            crack_y = 50 + math.sin(crack_angle) * crack_length
            # 裂缝（锯齿状）
            pygame.draw.line(crack_surface, (120, 20, 180, 220), (60, 50), (int(crack_x), int(crack_y)), 3)
            pygame.draw.line(crack_surface, (180, 50, 200, 220), (60, 50), (int(crack_x), int(crack_y)), 1)
        s.blit(crack_surface, (0, 0))
        
        # 虚无触手（从深渊伸出）
        tentacle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            tentacle_base_angle = i * math.pi / 4
            tentacle_segments = []
            for j in range(8):
                seg_angle = tentacle_base_angle + math.sin(t * 3 + i + j * 0.3) * 0.4
                seg_dist = 18 + j * 4
                seg_x = 60 + math.cos(seg_angle) * seg_dist
                seg_y = 50 + math.sin(seg_angle) * seg_dist
                tentacle_segments.append((seg_x, seg_y))
            # 绘制触手
            for j in range(len(tentacle_segments) - 1):
                width = 5 - j // 2
                pygame.draw.line(tentacle_surface, (100, 0, 150, 220), 
                               (int(tentacle_segments[j][0]), int(tentacle_segments[j][1])),
                               (int(tentacle_segments[j+1][0]), int(tentacle_segments[j+1][1])), width)
        s.blit(tentacle_surface, (0, 0))
        
        # 毁灭粒子
        destroy_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(25):
            destroy_angle = t * 3 + i * math.pi / 12.5
            destroy_dist = 25 + 20 * (i / 25)
            destroy_x = 60 + math.cos(destroy_angle) * destroy_dist
            destroy_y = 50 + math.sin(destroy_angle) * destroy_dist
            destroy_alpha = int(220 * (1 - (i / 25)))
            pygame.draw.circle(destroy_surface, (120, 20, 180, destroy_alpha), (int(destroy_x), int(destroy_y)), 2)
        s.blit(destroy_surface, (0, 0))
        
        return s
    
    elif model_style == "eclipse_night":
        # 永夜降临·黑暗时代 - 永恒黑夜、黑暗领域、星光消逝、永恒夜幕
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.5) * 0.1 + 1
        
        # 主体：夜幕形态
        night_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(night_surface, (20, 20, 40, 240), (60, 50), 18)
        pygame.draw.circle(night_surface, (80, 80, 120, 220), (60, 50), int(18 * pulse))
        s.blit(night_surface, (0, 0))
        
        # 黑暗领域扩张（多层黑暗）
        for i in range(5):
            darkness_radius = 22 + i * 8 + int(5 * pulse)
            darkness_alpha = int(180 * (1 - i / 5))
            darkness_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(darkness_surface, (40, 40, 70, darkness_alpha), (60, 50), darkness_radius, 3)
            s.blit(darkness_surface, (0, 0))
        
        # 消逝的星光（渐暗的星星）
        star_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(15):
            star_angle = t * 0.5 + i * math.pi / 7.5
            star_dist = 30 + 10 * (i / 15)
            star_x = 60 + math.cos(star_angle) * star_dist
            star_y = 50 + math.sin(star_angle) * star_dist
            # 渐暗效果
            star_brightness = int(200 * (1 - (i / 15)))
            if star_brightness > 50:
                pygame.draw.circle(star_surface, (star_brightness, star_brightness, star_brightness + 50, 220), 
                                 (int(star_x), int(star_y)), 2)
        s.blit(star_surface, (0, 0))
        
        # 永恒夜幕（波动阴影）
        veil_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            veil_angle = t * 2 + i * math.pi / 10
            veil_dist = 25 + 15 * math.sin(t * 2 + i)
            veil_x = 60 + math.cos(veil_angle) * veil_dist
            veil_y = 50 + math.sin(veil_angle) * veil_dist
            pygame.draw.circle(veil_surface, (40, 40, 70, 180), (int(veil_x), int(veil_y)), 4)
        s.blit(veil_surface, (0, 0))
        
        # 夜之精华（暗粒子）
        essence_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            essence_angle = t * 1.5 + i * math.pi / 6
            essence_dist = 35 + 8 * math.sin(t * 2.5 + i)
            essence_x = 60 + math.cos(essence_angle) * essence_dist
            essence_y = 50 + math.sin(essence_angle) * essence_dist
            pygame.draw.circle(essence_surface, (80, 80, 120, 220), (int(essence_x), int(essence_y)), 3)
        s.blit(essence_surface, (0, 0))
        
        return s
    
    elif model_style == "eclipse_dual":
        # 日月双食·阴阳交替 - 日月同食、阴阳力量、双重天象、天地失色
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：日月双核
        # 太阳（左）
        sun_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        sun_x = 45
        pygame.draw.circle(sun_surface, (220, 100, 255, 230), (sun_x, 50), 12)
        pygame.draw.circle(sun_surface, (255, 150, 255, 210), (sun_x, 50), int(12 * pulse))
        s.blit(sun_surface, (0, 0))
        
        # 月亮（右）
        moon_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        moon_x = 75
        pygame.draw.circle(moon_surface, (150, 50, 180, 230), (moon_x, 50), 12)
        pygame.draw.circle(moon_surface, (200, 100, 255, 210), (moon_x, 50), int(12 * pulse))
        s.blit(moon_surface, (0, 0))
        
        # 阴阳交替线（中心连接）
        pygame.draw.line(s, (180, 70, 220), (sun_x, 50), (moon_x, 50), 3)
        
        # 阴阳符号（太极）
        taiji_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 白半
        pygame.draw.arc(taiji_surface, (255, 200, 255, 220), (52, 42, 16, 16), 0, math.pi, 4)
        # 黑半
        pygame.draw.arc(taiji_surface, (100, 0, 150, 220), (52, 42, 16, 16), math.pi, 2 * math.pi, 4)
        s.blit(taiji_surface, (0, 0))
        
        # 日月光环（交错）
        for i in range(6):
            ring_angle = t * 2 + i * math.pi / 3
            ring_dist = 30 + 8 * math.sin(t * 2.5 + i)
            # 日光粒子
            sun_ring_x = sun_x + math.cos(ring_angle) * ring_dist
            sun_ring_y = 50 + math.sin(ring_angle) * ring_dist
            pygame.draw.circle(s, (220, 100, 255, 220), (int(sun_ring_x), int(sun_ring_y)), 3)
            # 月光粒子
            moon_ring_x = moon_x + math.cos(ring_angle + math.pi) * ring_dist
            moon_ring_y = 50 + math.sin(ring_angle + math.pi) * ring_dist
            pygame.draw.circle(s, (150, 50, 180, 220), (int(moon_ring_x), int(moon_ring_y)), 3)
        
        # 双重天象能量波
        for i in range(3):
            wave_radius = (t * 50 + i * 30) % 90
            wave_alpha = int(200 * (1 - wave_radius / 90))
            wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 从两个核心扩散
            pygame.draw.circle(wave_surface, (180, 70, 220, wave_alpha), (sun_x, 50), int(wave_radius), 2)
            pygame.draw.circle(wave_surface, (180, 70, 220, wave_alpha), (moon_x, 50), int(wave_radius), 2)
            s.blit(wave_surface, (0, 0))
        
        return s
    
    elif model_style == "eclipse_cosmos":
        # 宇宙日食·星际黑暗 - 宇宙尺度日食、星际黑暗降临、星光遮蔽、宇宙寂灭
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.8) * 0.25 + 1
        
        # 主体：超大质量黑洞核心
        core_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 事件视界（最黑的部分）
        pygame.draw.circle(core_surface, (10, 0, 20, 255), (60, 50), 18)
        # 吸积盘内环（强引力扭曲）
        for i in range(5):
            ring_r = 18 + i * 3
            ring_alpha = int(250 - i * 40)
            pygame.draw.circle(core_surface, (80, 0, 120, ring_alpha), (60, 50), ring_r, 2)
        s.blit(core_surface, (0, 0))
        
        # 吸积盘（螺旋结构）
        accretion_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for arm in range(3):
            arm_offset = arm * math.pi * 2 / 3
            for i in range(40):
                spiral_progress = i / 40
                spiral_angle = t * 1.5 + spiral_progress * math.pi * 4 + arm_offset
                spiral_dist = 25 + spiral_progress * 30
                spiral_x = 60 + math.cos(spiral_angle) * spiral_dist
                spiral_y = 50 + math.sin(spiral_angle) * spiral_dist
                # 颜色从紫色到深红（高温到低温）
                color_r = int(150 + 105 * spiral_progress)
                color_g = int(100 * (1 - spiral_progress))
                color_b = int(200 * (1 - spiral_progress))
                spiral_alpha = int(240 * (1 - spiral_progress * 0.7))
                if 0 <= spiral_x <= 120 and 0 <= spiral_y <= 120:
                    pygame.draw.circle(accretion_surface, (color_r, color_g, color_b, spiral_alpha), 
                                     (int(spiral_x), int(spiral_y)), 3)
        s.blit(accretion_surface, (0, 0))
        
        # 被遮蔽的星光（星际黑暗）
        stars_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(35):
            star_angle = (t * 0.3 + i * 0.618) * math.pi * 2  # 黄金角
            star_dist = 40 + (i % 3) * 8
            star_x = 60 + math.cos(star_angle) * star_dist
            star_y = 50 + math.sin(star_angle) * star_dist
            # 星光逐渐被遮蔽（渐暗效果）
            fade_factor = (math.sin(t * 2 + i) + 1) / 2
            star_brightness = int(180 * fade_factor)
            if star_brightness > 30:
                star_color = (star_brightness, star_brightness - 30, star_brightness + 50)
                if 0 <= star_x <= 120 and 0 <= star_y <= 120:
                    pygame.draw.circle(stars_surface, (*star_color, 220), 
                                     (int(star_x), int(star_y)), 2)
                    # 十字星芒
                    if star_brightness > 120:
                        for angle in [0, math.pi/2]:
                            ray_len = 4
                            rx1 = star_x + math.cos(angle) * ray_len
                            ry1 = star_y + math.sin(angle) * ray_len
                            rx2 = star_x - math.cos(angle) * ray_len
                            ry2 = star_y - math.sin(angle) * ray_len
                            pygame.draw.line(stars_surface, (*star_color, 180), 
                                           (int(rx1), int(ry1)), (int(rx2), int(ry2)), 1)
        s.blit(stars_surface, (0, 0))
        
        # 引力透镜效果（空间扭曲）
        lensing_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            lens_radius = 25 + i * 6 + int(5 * pulse)
            lens_alpha = int(120 * (1 - i / 6))
            # 绘制扭曲的光环
            for angle_deg in range(0, 360, 30):
                angle = math.radians(angle_deg)
                distortion = 2 * math.sin(t * 2 + angle * 3)
                lens_r = lens_radius + distortion
                lx = 60 + math.cos(angle) * lens_r
                ly = 50 + math.sin(angle) * lens_r
                if 0 <= lx <= 120 and 0 <= ly <= 120:
                    pygame.draw.circle(lensing_surface, (150, 100, 200, lens_alpha), 
                                     (int(lx), int(ly)), 2)
        s.blit(lensing_surface, (0, 0))
        
        # 霍金辐射（黑洞边缘微弱辐射）
        radiation_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            rad_angle = t * 4 + i * math.pi / 10
            rad_dist = 20 + 3 * math.sin(t * 3 + i)
            rad_x = 60 + math.cos(rad_angle) * rad_dist
            rad_y = 50 + math.sin(rad_angle) * rad_dist
            pygame.draw.circle(radiation_surface, (200, 150, 255, 200), (int(rad_x), int(rad_y)), 1)
        s.blit(radiation_surface, (0, 0))
        
        # 宇宙寂灭波（暗能量扩散）
        extinction_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            ext_radius = (t * 35 + i * 20) % 85
            ext_alpha = int(180 * (1 - ext_radius / 85))
            pygame.draw.circle(extinction_surface, (100, 50, 150, ext_alpha), (60, 50), int(ext_radius), 2)
        s.blit(extinction_surface, (0, 0))
        
        # 暗物质云（背景）
        dark_matter_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(30):
            dm_angle = t * 0.8 + i * 0.7
            dm_dist = 15 + 35 * (i / 30)
            dm_x = 60 + math.cos(dm_angle) * dm_dist
            dm_y = 50 + math.sin(dm_angle) * dm_dist
            dm_size = 1 + int(2 * math.sin(t * 2 + i))
            if 0 <= dm_x <= 120 and 0 <= dm_y <= 120:
                pygame.draw.circle(dark_matter_surface, (60, 0, 100, 150), 
                                 (int(dm_x), int(dm_y)), dm_size)
        s.blit(dark_matter_surface, (0, 0))
        
        return s
    
    elif model_style == "eclipse_ex":
        # 日蚀幽灵 - 日月重叠，暗影吞噬
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 背后的太阳（金色）
        sun_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        for layer in range(4, 0, -1):
            sun_radius = int(20 * pulse * (layer / 4))
            sun_alpha = int(200 * (layer / 4))
            pygame.draw.circle(sun_surf, (255, 200, 0, sun_alpha), (55, 50), sun_radius)
        s.blit(sun_surf, (0, 0))
        
        # 前方的月亮（黑暗）- 逐渐移动遮挡太阳
        moon_x = 55 + int(10 * math.sin(t * 0.8))
        pygame.draw.circle(s, (0, 0, 0), (moon_x, 50), 18)
        pygame.draw.circle(s, (100, 0, 150), (moon_x, 50), 18, 2)
        
        # 日冕（从边缘露出）
        corona_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(16):
            corona_angle = i * math.pi / 8
            corona_length = 15 + 8 * math.sin(t * 2.5 + i)
            
            # 从太阳中心向外
            corona_start_x = 55 + math.cos(corona_angle) * 20
            corona_start_y = 50 + math.sin(corona_angle) * 20
            corona_end_x = 55 + math.cos(corona_angle) * (20 + corona_length)
            corona_end_y = 50 + math.sin(corona_angle) * (20 + corona_length)
            
            pygame.draw.line(corona_surf, (255, 150, 0, 200), 
                           (int(corona_start_x), int(corona_start_y)),
                           (int(corona_end_x), int(corona_end_y)), 2)
        s.blit(corona_surf, (0, 0))
        
        # 暗影粒子（被吞噬）
        shadow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            shadow_progress = ((t * 2 + i * 0.3) % 1)
            shadow_angle = i * 0.3
            shadow_dist = 50 - shadow_progress * 30
            shadow_x = moon_x + math.cos(shadow_angle) * shadow_dist
            shadow_y = 50 + math.sin(shadow_angle) * shadow_dist
            shadow_alpha = int(200 * (1 - shadow_progress))
            pygame.draw.circle(shadow_surf, (50, 0, 100, shadow_alpha), (int(shadow_x), int(shadow_y)), 3)
        s.blit(shadow_surf, (0, 0))
        
        return s
    
    elif model_style == "eclipse_ex2":
        # 星系吞噬者 - 黑洞巨口，引力波扭曲
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.25 + 1
        
        # 黑洞核心（绝对黑暗）
        pygame.draw.circle(s, (0, 0, 0), (60, 50), 22)
        
        # 事件视界（紫色边缘）
        for layer in range(4):
            horizon_radius = 22 + layer * 4
            horizon_alpha = int(220 - layer * 50)
            horizon_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(horizon_surf, (100, 0, 150, horizon_alpha), (60, 50), horizon_radius, 3)
            s.blit(horizon_surf, (0, 0))
        
        # 吞噬的星系（螺旋吸入）
        for arm in range(4):
            arm_offset = arm * math.pi / 2
            for star_idx in range(30):
                spiral_progress = star_idx / 30
                spiral_angle = t * 2 + spiral_progress * math.pi * 6 + arm_offset
                spiral_dist = 60 - spiral_progress * 40
                if spiral_dist > 22:  # 不进入事件视界
                    sx = 60 + math.cos(spiral_angle) * spiral_dist
                    sy = 50 + math.sin(spiral_angle) * spiral_dist
                    star_size = int(4 * (1 - spiral_progress))
                    if star_size > 0:
                        star_brightness = int(255 * (1 - spiral_progress * 0.7))
                        pygame.draw.circle(s, (star_brightness, star_brightness // 2, star_brightness), 
                                         (int(sx), int(sy)), star_size)
        
        # 引力波扭曲（同心圆波纹）
        for wave in range(6):
            wave_radius = (t * 60 + wave * 20) % 120
            if wave_radius > 25:  # 从事件视界外开始
                wave_alpha = int(150 * (1 - (wave_radius - 25) / 95))
                wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                # 扭曲效果（椭圆变形）
                distortion = 1 + 0.3 * math.sin(t * 3 + wave)
                pygame.draw.ellipse(wave_surf, (150, 50, 200, wave_alpha),
                                  (60 - wave_radius, int(50 - wave_radius * distortion),
                                   wave_radius * 2, int(wave_radius * 2 * distortion)), 2)
                s.blit(wave_surf, (0, 0))
        
        # 宇宙坍缩粒子
        for particle in range(25):
            particle_progress = ((t * 3 + particle * 0.2) % 1)
            particle_angle = particle * 0.8
            particle_dist = 60 - particle_progress * 38
            if particle_dist > 22:
                px = 60 + math.cos(particle_angle) * particle_dist
                py = 50 + math.sin(particle_angle) * particle_dist
                particle_alpha = int(220 * (1 - particle_progress))
                pygame.draw.circle(s, (120, 20, 180, particle_alpha), (int(px), int(py)), 3)
        
        return s
    
    elif model_style == "eclipse_ex3":
        # 反物质引擎 - 湮灭核心
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.25 + 1
        
        # 湮灭核心（正反物质碰撞）
        core_radius = int(10 * pulse)
        # 能量爆发
        for explosion_layer in range(6, 0, -1):
            layer_radius = int(core_radius * (explosion_layer / 6))
            layer_alpha = 255
            # 白->黄->橙->红渐变
            if explosion_layer > 4:
                layer_color = (255, 255, 255)
            elif explosion_layer > 2:
                layer_color = (255, 255, 100)
            else:
                layer_color = (255, 150, 50)
            pygame.draw.circle(s, (*layer_color, layer_alpha), (60, 50), layer_radius)
        
        # 正物质流（蓝色，从左侧流入）
        matter_particles = 15
        for mp in range(matter_particles):
            mp_progress = (t * 3 + mp * 0.2) % 1
            mp_x = 10 + mp_progress * 45
            mp_y = 50 + math.sin(t * 4 + mp) * 10
            mp_alpha = int(255 * (1 - mp_progress))
            mp_size = 3 + int(3 * (1 - mp_progress))
            
            if mp_alpha > 30:
                pygame.draw.circle(s, (100, 150, 255, mp_alpha),
                                 (int(mp_x), int(mp_y)), mp_size)
        
        # 反物质流（红色，从右侧流入）
        for amp in range(matter_particles):
            amp_progress = (t * 3 + amp * 0.2) % 1
            amp_x = 110 - amp_progress * 45
            amp_y = 50 + math.sin(t * 4 + amp + math.pi) * 10
            amp_alpha = int(255 * (1 - amp_progress))
            amp_size = 3 + int(3 * (1 - amp_progress))
            
            if amp_alpha > 30:
                pygame.draw.circle(s, (255, 100, 100, amp_alpha),
                                 (int(amp_x), int(amp_y)), amp_size)
        
        # 湮灭光子射出（伽马射线）
        gamma_rays = 12
        for gamma in range(gamma_rays):
            gamma_angle = gamma * 2 * math.pi / gamma_rays + t * 4
            gamma_progress = (t * 5 + gamma * 0.3) % 1
            gamma_start_dist = core_radius + 2
            gamma_dist = gamma_start_dist + gamma_progress * 40
            gamma_x = 60 + math.cos(gamma_angle) * gamma_dist
            gamma_y = 50 + math.sin(gamma_angle) * gamma_dist
            gamma_alpha = int(255 * (1 - gamma_progress))
            
            if gamma_alpha > 30:
                # 绘制射线
                gamma_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                gamma_sx = 60 + math.cos(gamma_angle) * gamma_start_dist
                gamma_sy = 50 + math.sin(gamma_angle) * gamma_start_dist
                pygame.draw.line(gamma_surf, (255, 255, 255, gamma_alpha),
                               (int(gamma_sx), int(gamma_sy)),
                               (int(gamma_x), int(gamma_y)), 2)
                s.blit(gamma_surf, (0, 0))
        
        # 能量环（湮灭产生的冲击波）
        for shockwave in range(4):
            wave_progress = (t * 2 + shockwave * 0.3) % 1
            wave_radius = int(15 + wave_progress * 45)
            wave_alpha = int(220 * (1 - wave_progress))
            
            if wave_alpha > 30:
                wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(wave_surf, (255, 200, 150, wave_alpha),
                                 (60, 50), wave_radius, 3)
                s.blit(wave_surf, (0, 0))
        
        # 磁约束场（防止提前湮灭）
        magnetic_field_lines = 8
        for field_line in range(magnetic_field_lines):
            field_angle = field_line * math.pi / 4
            field_rotation = t * 2
            
            # 磁力线弧形
            field_points = []
            for arc_seg in range(15):
                arc_progress = arc_seg / 15
                arc_dist = 20 + arc_progress * 25
                arc_angle = field_angle + field_rotation + math.sin(arc_progress * math.pi) * 0.5
                field_x = 60 + math.cos(arc_angle) * arc_dist
                field_y = 50 + math.sin(arc_angle) * arc_dist
                field_points.append((int(field_x), int(field_y)))
            
            if len(field_points) > 1:
                field_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.lines(field_surf, (100, 255, 255, 150), False, field_points, 1)
                s.blit(field_surf, (0, 0))
        
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
    
    elif model_style == "eclipse_ex5":
        # 漫画分镜·速度线
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        
        # 速度线
        for i in range(24):
            angle = (i / 24.0) * 2 * math.pi
            speed_length = 30 + abs(math.sin(t * 2 + i)) * 15
            line_start_x = center[0] + math.cos(angle) * 10
            line_start_y = center[1] + math.sin(angle) * 10
            line_end_x = center[0] + math.cos(angle) * speed_length
            line_end_y = center[1] + math.sin(angle) * speed_length
            pygame.draw.line(plane_surf, (255, 100, 100), 
                           (line_start_x, line_start_y), (line_end_x, line_end_y), 2)
        
        # 漫画爆炸泡泡
        for i in range(5):
            bubble_angle = t * 2 + i * 1.257
            bubble_radius = 25 + i * 4
            bubble_x = center[0] + math.cos(bubble_angle) * bubble_radius
            bubble_y = center[1] + math.sin(bubble_angle) * bubble_radius
            bubble_size = int(8 + abs(math.sin(t * 3 + i)) * 5)
            
            # 爆炸形状
            points = []
            for j in range(8):
                spike_angle = (j / 8.0) * 2 * math.pi
                spike_radius = bubble_size if j % 2 == 0 else bubble_size * 1.5
                px = bubble_x + math.cos(spike_angle) * spike_radius
                py = bubble_y + math.sin(spike_angle) * spike_radius
                points.append((px, py))
            
            if len(points) >= 3:
                pygame.draw.polygon(plane_surf, (100, 100, 255), points, 2)
        
        # 音效字模拟
        if int(t * 2) % 2 == 0:
            for i in range(3):
                text_x = center[0] + (i - 1) * 18
                text_y = center[1] - 25
                pygame.draw.circle(plane_surf, (255, 255, 100), (text_x, text_y), 6, 2)
                pygame.draw.line(plane_surf, (255, 255, 100), 
                               (text_x - 4, text_y + 6), (text_x + 4, text_y + 6), 2)
        return plane_surf
    
    return None
