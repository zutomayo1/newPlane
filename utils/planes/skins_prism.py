# Prism 专属涂装渲染模块
# 包含: prism_diamond, prism_refraction, prism_laser, prism_glass, prism_crystal, prism_rainbow, prism_aurora

import pygame
import math

# Prism涂装列表
PRISM_STYLES = ["prism_diamond", "prism_refraction", "prism_laser", "prism_glass", "prism_crystal", "prism_rainbow", "prism_aurora", "prism_ex", "prism_ex2", "prism_ex3", "prism_ex4", "prism_ex5"]

def is_prism_style(model_style):
    """检查是否为Prism涂装"""
    return model_style in PRISM_STYLES

def render_prism_skin(s, c, model_style, t, pid, static=False):
    """渲染Prism涂装，返回Surface或None"""
    
    if model_style == "prism_diamond":
        # 钻石星辰·完美折射 - 钻石切割面、完美折射、星辰闪耀、光之宝石
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：钻石形状（多面体）
        diamond_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 上半部（锥形）
        diamond_top = [(60, 35), (70, 50), (60, 55), (50, 50)]
        pygame.draw.polygon(diamond_surface, (220, 220, 255, 250), diamond_top)
        pygame.draw.polygon(diamond_surface, (255, 255, 255, 230), diamond_top, 2)
        # 下半部（锥形）
        diamond_bottom = [(60, 55), (70, 50), (75, 65), (60, 70), (45, 65), (50, 50)]
        pygame.draw.polygon(diamond_surface, (240, 240, 255, 250), diamond_bottom)
        pygame.draw.polygon(diamond_surface, (255, 255, 255, 230), diamond_bottom, 2)
        s.blit(diamond_surface, (0, 0))
        
        # 切割面反射（多条光线）
        facet_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            facet_angle = t * 2 + i * math.pi / 6
            facet_length = 15 + 10 * math.sin(t * 3 + i)
            facet_x = 60 + math.cos(facet_angle) * facet_length
            facet_y = 52 + math.sin(facet_angle) * facet_length
            pygame.draw.line(facet_surface, (255, 255, 255, 220), (60, 52), (int(facet_x), int(facet_y)), 2)
        s.blit(facet_surface, (0, 0))
        
        # 星辰闪耀（闪光点）
        sparkle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(15):
            if (int(t * 10) + i) % 5 < 3:
                sparkle_angle = i * math.pi / 7.5
                sparkle_dist = 25 + 15 * (i % 3) / 2
                sparkle_x = 60 + math.cos(sparkle_angle) * sparkle_dist
                sparkle_y = 52 + math.sin(sparkle_angle) * sparkle_dist
                pygame.draw.circle(sparkle_surface, (255, 255, 255, 240), (int(sparkle_x), int(sparkle_y)), 3)
                # 十字闪光
                pygame.draw.line(sparkle_surface, (240, 240, 255, 200), 
                               (int(sparkle_x) - 4, int(sparkle_y)), 
                               (int(sparkle_x) + 4, int(sparkle_y)), 1)
                pygame.draw.line(sparkle_surface, (240, 240, 255, 200), 
                               (int(sparkle_x), int(sparkle_y) - 4), 
                               (int(sparkle_x), int(sparkle_y) + 4), 1)
        s.blit(sparkle_surface, (0, 0))
        
        # 完美折射光环
        refract_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(3):
            refract_radius = 20 + i * 10 + int(5 * pulse)
            refract_alpha = int(200 * (1 - i / 3))
            pygame.draw.circle(refract_surface, (220, 220, 255, refract_alpha), (60, 52), refract_radius, 2)
        s.blit(refract_surface, (0, 0))
        
        return s
    
    elif model_style == "prism_refraction":
        # 多重折射·光线迷宫 - 光线折射、光路复杂、眩目迷离、光学迷宫
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：多棱镜结构
        prism_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 中心三角形
        pygame.draw.polygon(prism_surface, (200, 255, 255, 240), [(60, 40), (70, 60), (50, 60)])
        pygame.draw.polygon(prism_surface, (255, 200, 255, 240), [(60, 40), (75, 55), (70, 60)])
        pygame.draw.polygon(prism_surface, (220, 230, 255, 240), [(60, 40), (45, 55), (50, 60)])
        s.blit(prism_surface, (0, 0))
        
        # 折射光路（复杂路径）
        ray_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            # 入射光
            start_angle = t + i * math.pi / 4
            start_x = 60 + math.cos(start_angle) * 40
            start_y = 50 + math.sin(start_angle) * 40
            
            # 折射点
            refract_x = 60 + math.cos(start_angle) * 20
            refract_y = 50 + math.sin(start_angle) * 20
            
            # 出射光（改变角度）
            exit_angle = start_angle + math.pi / 3 + math.sin(t * 2 + i) * 0.5
            exit_x = 60 + math.cos(exit_angle) * 35
            exit_y = 50 + math.sin(exit_angle) * 35
            
            # 绘制光路
            color_shift = int(50 * math.sin(t + i))
            pygame.draw.line(ray_surface, (200 + color_shift, 255, 255, 200), 
                           (int(start_x), int(start_y)), (int(refract_x), int(refract_y)), 2)
            pygame.draw.line(ray_surface, (255, 200 + color_shift, 255, 200), 
                           (int(refract_x), int(refract_y)), (int(exit_x), int(exit_y)), 2)
        s.blit(ray_surface, (0, 0))
        
        # 光学粒子（在光路上）
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            particle_angle = t * 3 + i * math.pi / 10
            particle_dist = 15 + 25 * (i / 20)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            pygame.draw.circle(particle_surface, (220, 230, 255, 220), (int(particle_x), int(particle_y)), 2)
        s.blit(particle_surface, (0, 0))
        
        return s
    
    elif model_style == "prism_laser":
        # 激光矩阵·光束网络 - 激光矩阵、光束网络、高能光束、光之武器
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：激光发射器核心
        core_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(core_surface, (255, 0, 100, 250), (60, 50), 12)
        pygame.draw.circle(core_surface, (255, 100, 150, 230), (60, 50), int(12 * pulse))
        s.blit(core_surface, (0, 0))
        
        # 激光矩阵节点
        node_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        nodes = []
        for i in range(8):
            node_angle = t + i * math.pi / 4
            node_dist = 30
            node_x = 60 + math.cos(node_angle) * node_dist
            node_y = 50 + math.sin(node_angle) * node_dist
            nodes.append((node_x, node_y))
            pygame.draw.circle(node_surface, (255, 50, 120, 240), (int(node_x), int(node_y)), 6)
        s.blit(node_surface, (0, 0))
        
        # 光束网络（连接所有节点）
        beam_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(len(nodes)):
            # 连接到中心
            pygame.draw.line(beam_surface, (255, 100, 150, 200), (60, 50), 
                           (int(nodes[i][0]), int(nodes[i][1])), 2)
            # 连接相邻节点
            next_i = (i + 1) % len(nodes)
            pygame.draw.line(beam_surface, (255, 50, 120, 180), 
                           (int(nodes[i][0]), int(nodes[i][1])), 
                           (int(nodes[next_i][0]), int(nodes[next_i][1])), 2)
        s.blit(beam_surface, (0, 0))
        
        # 高能脉冲（沿光束移动）
        pulse_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            pulse_progress = ((t * 2 + i * 0.5) % 2) / 2
            pulse_x = 60 + (nodes[i][0] - 60) * pulse_progress
            pulse_y = 50 + (nodes[i][1] - 50) * pulse_progress
            pygame.draw.circle(pulse_surface, (255, 150, 200, 240), (int(pulse_x), int(pulse_y)), 4)
        s.blit(pulse_surface, (0, 0))
        
        return s
    
    elif model_style == "prism_glass":
        # 玻璃艺术·透明美学 - 玻璃材质、透明效果、光影交错、艺术结晶
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：玻璃立方体（透明感）
        glass_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 前面
        glass_front = [(50, 45), (70, 45), (70, 65), (50, 65)]
        pygame.draw.polygon(glass_surface, (100, 255, 220, 120), glass_front)
        pygame.draw.polygon(glass_surface, (150, 255, 255, 200), glass_front, 2)
        # 顶面
        glass_top = [(50, 45), (70, 45), (75, 40), (55, 40)]
        pygame.draw.polygon(glass_surface, (120, 255, 240, 140), glass_top)
        pygame.draw.polygon(glass_surface, (150, 255, 255, 200), glass_top, 2)
        # 侧面
        glass_side = [(70, 45), (75, 40), (75, 60), (70, 65)]
        pygame.draw.polygon(glass_surface, (80, 255, 200, 100), glass_side)
        pygame.draw.polygon(glass_surface, (150, 255, 255, 200), glass_side, 2)
        s.blit(glass_surface, (0, 0))
        
        # 光影效果（穿透玻璃）
        light_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            light_x = 52 + i * 3
            light_alpha = int(150 * math.sin(t * 2 + i))
            if light_alpha > 0:
                pygame.draw.line(light_surface, (150, 255, 255, light_alpha), 
                               (light_x, 40), (light_x, 70), 2)
        s.blit(light_surface, (0, 0))
        
        # 透明折射粒子
        refract_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(15):
            refract_angle = t + i * math.pi / 7.5
            refract_dist = 20 + 15 * math.sin(t * 2 + i)
            refract_x = 60 + math.cos(refract_angle) * refract_dist
            refract_y = 55 + math.sin(refract_angle) * refract_dist
            pygame.draw.circle(refract_surface, (120, 255, 240, 200), (int(refract_x), int(refract_y)), 3)
        s.blit(refract_surface, (0, 0))
        
        # 玻璃光泽（高光）
        highlight_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(highlight_surface, (200, 255, 255, 180), (65, 50), 8)
        pygame.draw.circle(highlight_surface, (255, 255, 255, 220), (66, 49), 3)
        s.blit(highlight_surface, (0, 0))
        
        return s
    
    elif model_style == "prism_crystal":
        # 晶体共振·光芒四射 - 晶体结构、光芒发射、光的放大、晶莹璀璨
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：晶体核心（六边形）
        crystal_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        crystal_points = []
        for i in range(6):
            crystal_angle = i * math.pi / 3
            crystal_x = 60 + math.cos(crystal_angle) * 15
            crystal_y = 50 + math.sin(crystal_angle) * 15
            crystal_points.append((crystal_x, crystal_y))
        pygame.draw.polygon(crystal_surface, (180, 220, 255, 250), crystal_points)
        pygame.draw.polygon(crystal_surface, (220, 255, 255, 230), crystal_points, 2)
        s.blit(crystal_surface, (0, 0))
        
        # 晶体格子（内部结构）
        lattice_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            lattice_angle = i * math.pi / 3
            lattice_x = 60 + math.cos(lattice_angle) * 10
            lattice_y = 50 + math.sin(lattice_angle) * 10
            pygame.draw.line(lattice_surface, (200, 240, 255, 220), (60, 50), 
                           (int(lattice_x), int(lattice_y)), 2)
        s.blit(lattice_surface, (0, 0))
        
        # 光芒四射（强烈放射）
        ray_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            ray_angle = t + i * math.pi / 6
            ray_length = 20 + 20 * math.sin(t * 3 + i)
            ray_x = 60 + math.cos(ray_angle) * ray_length
            ray_y = 50 + math.sin(ray_angle) * ray_length
            # 渐变光束
            for j in range(5):
                ray_alpha = int(220 * (1 - j / 5))
                ray_width = 4 - j
                pygame.draw.line(ray_surface, (200, 240, 255, ray_alpha), (60, 50), 
                               (int(ray_x), int(ray_y)), ray_width)
        s.blit(ray_surface, (0, 0))
        
        # 共振波动
        resonance_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(3):
            res_radius = (t * 60 + i * 30) % 90
            res_alpha = int(200 * (1 - res_radius / 90))
            pygame.draw.circle(resonance_surface, (180, 220, 255, res_alpha), (60, 50), int(res_radius), 2)
        s.blit(resonance_surface, (0, 0))
        
        return s
    
    elif model_style == "prism_rainbow":
        # 棱镜分光·七彩虹光 - 光谱分离、七彩虹光、色彩粒子、光的盛宴
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：棱镜（三角形）
        prism_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        prism_points = [(60, 35), (75, 60), (45, 60)]
        pygame.draw.polygon(prism_surface, (255, 255, 255, 240), prism_points)
        pygame.draw.polygon(prism_surface, (255, 230, 255, 220), prism_points, 2)
        s.blit(prism_surface, (0, 0))
        
        # 七彩光谱（红橙黄绿青蓝紫）
        rainbow_colors = [
            (255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0),
            (0, 255, 255), (0, 0, 255), (127, 0, 255)
        ]
        
        # 分光效果（从棱镜右侧射出）
        spectrum_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i, color in enumerate(rainbow_colors):
            spectrum_angle = -math.pi / 4 + i * 0.15
            spectrum_start_x = 75
            spectrum_start_y = 60
            spectrum_length = 25 + 10 * math.sin(t * 2 + i)
            spectrum_end_x = spectrum_start_x + math.cos(spectrum_angle) * spectrum_length
            spectrum_end_y = spectrum_start_y + math.sin(spectrum_angle) * spectrum_length
            pygame.draw.line(spectrum_surface, (*color, 220), 
                           (spectrum_start_x, spectrum_start_y), 
                           (int(spectrum_end_x), int(spectrum_end_y)), 3)
        s.blit(spectrum_surface, (0, 0))
        
        # 色彩粒子（彩虹粒子飞舞）
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(21):
            particle_angle = t * 2 + i * math.pi / 10.5
            particle_dist = 20 + 20 * (i / 21)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            color_index = i % len(rainbow_colors)
            pygame.draw.circle(particle_surface, (*rainbow_colors[color_index], 220), 
                             (int(particle_x), int(particle_y)), 3)
        s.blit(particle_surface, (0, 0))
        
        # 光的盛宴（环绕光环）
        halo_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(7):
            halo_radius = 18 + i * 4
            color_index = (int(t * 3) + i) % len(rainbow_colors)
            pygame.draw.circle(halo_surface, (*rainbow_colors[color_index], 180), (60, 50), halo_radius, 2)
        s.blit(halo_surface, (0, 0))
        
        return s
    
    elif model_style == "prism_aurora":
        # 极光棱镜·光谱盛宴 - 极光通过棱镜、光谱完全展开、色彩盛宴、绚烂夺目
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心：极光核心球体
        core_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8, 0, -1):
            glow_alpha = int(60 * (i / 8))
            pygame.draw.circle(core_glow, (100, 255, 200, glow_alpha), (60, 50), i * 3)
        s.blit(core_glow, (0, 0))
        pygame.draw.circle(s, (150, 255, 220), (60, 50), 12)
        pygame.draw.circle(s, (200, 255, 255), (60, 50), 12, 2)
        
        # 极光波浪（上下流动）
        for wave_idx in range(3):
            wave_y_base = 30 + wave_idx * 20
            wave_points = []
            for x in range(0, 120, 6):
                wave_y = wave_y_base + 8 * math.sin(t * 3 + x * 0.1 + wave_idx)
                wave_points.append((x, wave_y))
            
            # 绘制波浪带
            for i in range(len(wave_points) - 1):
                # 极光颜色渐变
                progress = i / len(wave_points)
                r = int(100 + 100 * math.sin(progress * math.pi + t))
                g = 255
                b = int(200 + 55 * math.cos(progress * math.pi + t))
                pygame.draw.line(s, (r, g, b, 180), 
                               wave_points[i], wave_points[i + 1], 5)
        
        # 光谱色带（从中心向外扩散）
        spectrum_colors = [
            (255, 50, 50),    # 红
            (255, 150, 50),   # 橙
            (255, 255, 50),   # 黄
            (50, 255, 50),    # 绿
            (50, 255, 255),   # 青
            (50, 50, 255),    # 蓝
            (200, 50, 255)    # 紫
        ]
        
        for i, color in enumerate(spectrum_colors):
            angle = (t + i * 0.5) * 2
            radius_base = 20 + i * 3
            # 绘制彩色圆环段
            for seg in range(12):
                seg_angle = angle + seg * math.pi / 6
                radius = radius_base + 3 * math.sin(t * 3 + seg)
                x = 60 + math.cos(seg_angle) * radius
                y = 50 + math.sin(seg_angle) * radius
                size = 4 + int(2 * math.sin(t * 4 + i + seg))
                pygame.draw.circle(s, color, (int(x), int(y)), size)
        
        # 光谱粒子暴雨
        for i in range(50):
            particle_angle = t * 2 + i * 0.4
            particle_dist = 10 + (i % 5) * 8
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            # 循环彩虹色
            color_idx = (int(t * 5) + i) % len(spectrum_colors)
            if 0 <= px <= 120 and 0 <= py <= 120:
                pygame.draw.circle(s, spectrum_colors[color_idx], (int(px), int(py)), 2)
        
        # 螺旋光束（棱镜效果）
        for beam_idx in range(7):
            beam_angle = beam_idx * math.pi * 2 / 7 + t
            beam_color = spectrum_colors[beam_idx]
            # 从中心发出的光束
            for step in range(15):
                dist = 15 + step * 3
                bx = 60 + math.cos(beam_angle) * dist
                by = 50 + math.sin(beam_angle) * dist
                beam_alpha = int(220 * (1 - step / 15))
                if 0 <= bx <= 120 and 0 <= by <= 120:
                    beam_color_alpha = (beam_color[0], beam_color[1], beam_color[2], beam_alpha)
                    pygame.draw.circle(s, beam_color_alpha, (int(bx), int(by)), 3)
        
        # 彩虹光环（脉动）
        for ring_idx in range(5):
            ring_radius = 25 + ring_idx * 8 + int(5 * pulse)
            ring_alpha = int(150 * (1 - ring_idx / 5))
            # 彩虹色环
            hue_phase = (t + ring_idx * 0.3) % 1.0
            ring_r = int(128 + 127 * math.sin(hue_phase * math.pi * 2))
            ring_g = int(128 + 127 * math.sin((hue_phase + 0.33) * math.pi * 2))
            ring_b = int(128 + 127 * math.sin((hue_phase + 0.67) * math.pi * 2))
            pygame.draw.circle(s, (ring_r, ring_g, ring_b, ring_alpha), (60, 50), ring_radius, 2)
        
        # 星光闪烁（光谱盛宴）
        for i in range(30):
            if (int(t * 8) + i) % 4 < 2:
                star_angle = i * 0.7
                star_dist = 35 + 10 * (i % 3)
                sx = 60 + math.cos(star_angle) * star_dist
                sy = 50 + math.sin(star_angle) * star_dist
                if 0 <= sx <= 120 and 0 <= sy <= 120:
                    star_color_idx = i % len(spectrum_colors)
                    pygame.draw.circle(s, spectrum_colors[star_color_idx], (int(sx), int(sy)), 3)
                    # 十字星芒
                    for offset in [-3, 3]:
                        pygame.draw.circle(s, spectrum_colors[star_color_idx], (int(sx) + offset, int(sy)), 1)
                        pygame.draw.circle(s, spectrum_colors[star_color_idx], (int(sx), int(sy) + offset), 1)
        
        return s
    
    elif model_style == "prism_ex":
        # 棱镜折射 - 三棱镜，彩虹光束分离
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心三棱镜（正三角形）
        prism_size = int(25 * pulse)
        prism_points = [
            (60, 50 - prism_size),
            (60 - int(prism_size * 0.866), 50 + int(prism_size * 0.5)),
            (60 + int(prism_size * 0.866), 50 + int(prism_size * 0.5))
        ]
        pygame.draw.polygon(s, (255, 255, 255), prism_points)
        pygame.draw.polygon(s, (200, 200, 255), prism_points, 3)
        
        # 彩虹色谱
        rainbow_colors = [
            (255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0),
            (0, 255, 255), (0, 0, 255), (127, 0, 255)
        ]
        
        # 三个方向射出彩虹光束
        for direction in range(3):
            base_angle = direction * 2 * math.pi / 3 + math.pi / 6
            
            # 每个方向7种颜色
            for color_idx, color in enumerate(rainbow_colors):
                beam_angle = base_angle + (color_idx - 3) * 0.15
                beam_start_x = prism_points[direction][0]
                beam_start_y = prism_points[direction][1]
                beam_length = 30 + 10 * math.sin(t * 2 + color_idx)
                beam_end_x = beam_start_x + math.cos(beam_angle) * beam_length
                beam_end_y = beam_start_y + math.sin(beam_angle) * beam_length
                
                beam_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(beam_surf, (*color, 200), 
                               (int(beam_start_x), int(beam_start_y)),
                               (int(beam_end_x), int(beam_end_y)), 3)
                s.blit(beam_surf, (0, 0))
        
        # 白光粒子汇聚到棱镜
        for i in range(10):
            particle_progress = ((t * 2 + i * 0.2) % 1)
            particle_angle = t + i * 0.6
            particle_dist = 50 - particle_progress * 30
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            particle_alpha = int(220 * (1 - particle_progress))
            pygame.draw.circle(s, (255, 255, 255, particle_alpha), (int(particle_x), int(particle_y)), 3)
        
        return s
    
    elif model_style == "prism_ex2":
        # 万花筒 - 对称图案，镜像反射
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心万花筒核心
        pygame.draw.circle(s, (255, 100, 255), (60, 50), int(12 * pulse))
        
        # 6重对称图案
        for symmetry in range(6):
            base_angle = symmetry * math.pi / 3 + t * 0.5
            
            # 每个对称区域绘制复杂图案
            for pattern in range(5):
                pattern_dist = 15 + pattern * 8
                pattern_angle = base_angle + pattern * 0.3
                
                # 彩色图案块
                hue = (t * 50 + symmetry * 60 + pattern * 30) % 360
                color_r = int(127 + 127 * math.sin(math.radians(hue)))
                color_g = int(127 + 127 * math.sin(math.radians(hue + 120)))
                color_b = int(127 + 127 * math.sin(math.radians(hue + 240)))
                
                # 主图形
                px = 60 + math.cos(pattern_angle) * pattern_dist
                py = 50 + math.sin(pattern_angle) * pattern_dist
                
                # 绘制小六边形
                poly_points = []
                for i in range(6):
                    poly_angle = pattern_angle + i * math.pi / 3
                    poly_radius = 5 + 2 * math.sin(t * 3 + pattern)
                    poly_x = px + math.cos(poly_angle) * poly_radius
                    poly_y = py + math.sin(poly_angle) * poly_radius
                    poly_points.append((int(poly_x), int(poly_y)))
                pygame.draw.polygon(s, (color_r, color_g, color_b), poly_points)
                
                # 镜像反射（另一侧）
                mirror_angle = base_angle - pattern * 0.3
                mirror_px = 60 + math.cos(mirror_angle) * pattern_dist
                mirror_py = 50 + math.sin(mirror_angle) * pattern_dist
                mirror_poly_points = []
                for i in range(6):
                    mirror_poly_angle = mirror_angle + i * math.pi / 3
                    mirror_poly_radius = 5 + 2 * math.sin(t * 3 + pattern)
                    mirror_poly_x = mirror_px + math.cos(mirror_poly_angle) * mirror_poly_radius
                    mirror_poly_y = mirror_py + math.sin(mirror_poly_angle) * mirror_poly_radius
                    mirror_poly_points.append((int(mirror_poly_x), int(mirror_poly_y)))
                pygame.draw.polygon(s, (color_r, color_g, color_b), mirror_poly_points)
        
        # 迷幻光线
        for ray in range(12):
            ray_angle = ray * math.pi / 6 + t * 2
            ray_length = 25 + 15 * math.sin(t * 3 + ray)
            rx = 60 + math.cos(ray_angle) * ray_length
            ry = 50 + math.sin(ray_angle) * ray_length
            ray_hue = (t * 100 + ray * 30) % 360
            ray_r = int(127 + 127 * math.sin(math.radians(ray_hue)))
            ray_g = int(127 + 127 * math.sin(math.radians(ray_hue + 120)))
            ray_b = int(127 + 127 * math.sin(math.radians(ray_hue + 240)))
            ray_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(ray_surf, (ray_r, ray_g, ray_b, 180), (60, 50), (int(rx), int(ry)), 2)
            s.blit(ray_surf, (0, 0))
        
        return s
    
    elif model_style == "prism_ex3":
        # 五维投影 - 超立方体
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.5) * 0.15 + 1
        
        # 4D超立方体的3D投影顶点（Tesseract）
        # 内立方体顶点
        inner_size = 15
        inner_vertices = [
            (60 - inner_size, 50 - inner_size, -inner_size),
            (60 + inner_size, 50 - inner_size, -inner_size),
            (60 + inner_size, 50 + inner_size, -inner_size),
            (60 - inner_size, 50 + inner_size, -inner_size),
            (60 - inner_size, 50 - inner_size, inner_size),
            (60 + inner_size, 50 - inner_size, inner_size),
            (60 + inner_size, 50 + inner_size, inner_size),
            (60 - inner_size, 50 + inner_size, inner_size),
        ]
        
        # 外立方体顶点
        outer_size = 25
        outer_vertices = [
            (60 - outer_size, 50 - outer_size, -outer_size),
            (60 + outer_size, 50 - outer_size, -outer_size),
            (60 + outer_size, 50 + outer_size, -outer_size),
            (60 - outer_size, 50 + outer_size, -outer_size),
            (60 - outer_size, 50 - outer_size, outer_size),
            (60 + outer_size, 50 - outer_size, outer_size),
            (60 + outer_size, 50 + outer_size, outer_size),
            (60 - outer_size, 50 + outer_size, outer_size),
        ]
        
        # 4D旋转矩阵（简化投影）
        rotation_4d = t * 1.5
        
        # 投影顶点（应用4D旋转）
        def project_4d_vertex(v, w_coord):
            x, y, z = v
            # 简化的4D->3D投影
            w = w_coord * math.cos(rotation_4d)
            proj_scale = 1 / (4 - w * 0.1)
            return (int(x * proj_scale), int(y * proj_scale))
        
        inner_projected = [project_4d_vertex(v, -1) for v in inner_vertices]
        outer_projected = [project_4d_vertex(v, 1) for v in outer_vertices]
        
        # 绘制内立方体边
        inner_edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # 前面
            (4, 5), (5, 6), (6, 7), (7, 4),  # 后面
            (0, 4), (1, 5), (2, 6), (3, 7),  # 连接
        ]
        
        for edge in inner_edges:
            p1 = inner_projected[edge[0]]
            p2 = inner_projected[edge[1]]
            pygame.draw.line(s, (150, 200, 255), p1, p2, 2)
        
        # 绘制外立方体边
        for edge in inner_edges:
            p1 = outer_projected[edge[0]]
            p2 = outer_projected[edge[1]]
            pygame.draw.line(s, (200, 150, 255), p1, p2, 2)
        
        # 连接内外立方体（超立方体的4D边）
        for i in range(8):
            p1 = inner_projected[i]
            p2 = outer_projected[i]
            hyper_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(hyper_surf, (255, 200, 255, 180), p1, p2, 1)
            s.blit(hyper_surf, (0, 0))
        
        # 绘制顶点
        for vertex in inner_projected:
            pygame.draw.circle(s, (100, 255, 255), vertex, 4)
        for vertex in outer_projected:
            pygame.draw.circle(s, (255, 100, 255), vertex, 4)
        
        # 维度波动效果
        for dimension_wave in range(5):
            wave_angle = t * 2 + dimension_wave * 2 * math.pi / 5
            wave_dist = 35 + 10 * math.sin(t * 3 + dimension_wave)
            wave_x = 60 + math.cos(wave_angle) * wave_dist
            wave_y = 50 + math.sin(wave_angle) * wave_dist
            wave_alpha = int(200 * ((math.sin(t * 4 + dimension_wave) + 1) / 2))
            
            # 高维粒子
            for glow in range(3, 0, -1):
                glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                glow_radius = glow * 3
                glow_alpha = int(wave_alpha * (glow / 3))
                pygame.draw.circle(glow_surf, (255, 255, 255, glow_alpha),
                                 (int(wave_x), int(wave_y)), glow_radius)
                s.blit(glow_surf, (0, 0))
        
        # 维度裂缝（3D空间的切面）
        rift_count = 6
        for rift in range(rift_count):
            rift_angle = rift * math.pi / 3 + t
            rift_length = 40
            rift_x1 = 60 + math.cos(rift_angle) * 10
            rift_y1 = 50 + math.sin(rift_angle) * 10
            rift_x2 = 60 + math.cos(rift_angle) * rift_length
            rift_y2 = 50 + math.sin(rift_angle) * rift_length
            
            rift_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            rift_alpha = int(150 * ((math.sin(t * 3 + rift) + 1) / 2))
            pygame.draw.line(rift_surf, (200, 200, 255, rift_alpha),
                           (int(rift_x1), int(rift_y1)),
                           (int(rift_x2), int(rift_y2)), 2)
            s.blit(rift_surf, (0, 0))
        
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
    
    elif model_style == "prism_ex5":
        # 乐高积木·创意拼搭
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        
        block_colors = [(255, 50, 50), (50, 255, 50), (50, 50, 255), 
                      (255, 255, 50), (255, 50, 255), (50, 255, 255)]
        
        for layer in range(4):
            for i in range(6):
                angle = t * 0.5 + layer * 0.785 + i * 1.047
                radius = 20 + layer * 10
                block_x = center[0] + math.cos(angle) * radius
                block_y = center[1] + math.sin(angle) * radius
                
                block_size = 10
                block_color = block_colors[(layer + i) % len(block_colors)]
                
                pygame.draw.rect(plane_surf, block_color, 
                               (block_x - block_size//2, block_y - block_size//2, 
                                block_size, block_size))
                
                # 积木凸起
                for dy in [-3, 3]:
                    for dx in [-3, 3]:
                        pygame.draw.circle(plane_surf, 
                                         tuple(max(0, c - 50) for c in block_color),
                                         (int(block_x + dx), int(block_y + dy)), 1)
        
        # 拼搭动画
        for i in range(8):
            fall_phase = (t * 2 + i * 0.3) % 1.0
            fall_x = center[0] + math.sin(t + i) * 25
            fall_y = center[1] - 35 + fall_phase * 70
            fall_color = block_colors[i % len(block_colors)]
            fall_size = 8
            pygame.draw.rect(plane_surf, fall_color, 
                           (fall_x - fall_size//2, fall_y - fall_size//2, 
                            fall_size, fall_size))
        return plane_surf
    
    return None
