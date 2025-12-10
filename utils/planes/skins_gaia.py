# Gaia 专属涂装渲染模块
# 包含: forest, crystal, rock, elemental, overgrowth, treant, titan

import pygame
import math

# Gaia涂装列表
GAIA_STYLES = ["forest", "crystal", "rock", "elemental", "overgrowth", "treant", "titan", "gaia_ex", "gaia_ex2", "gaia_ex3", "gaia_ex4", "gaia_ex5"]

def is_gaia_style(model_style):
    """检查是否为Gaia涂装"""
    return model_style in GAIA_STYLES

def render_gaia_skin(s, c, model_style, t, pid, static=False):
    """渲染Gaia涂装，返回Surface或None"""
    
    if model_style == "forest":
        # 森林守护者·生命之林 - 参天古树、藤蔓缠绕、森林灵体、生命气息
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：古树形态
        trunk_points = [(60, 28), (66, 50), (64, 68), (56, 68), (54, 50)]
        pygame.draw.polygon(s, (60, 40, 20), trunk_points)
        pygame.draw.polygon(s, (100, 80, 50), trunk_points, 2)
        
        # 树冠（多层绿叶）
        for i in range(3):
            crown_y = 35 - i * 8
            crown_radius = 15 - i * 3
            crown_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(crown_surface, (50, 150, 50, 200), (60, crown_y), crown_radius)
            pygame.draw.circle(crown_surface, (80, 180, 80, 220), (60, crown_y), crown_radius, 2)
            s.blit(crown_surface, (0, 0))
        
        # 藤蔓缠绕（动态藤蔓）
        for side in [-1, 1]:
            vine_segments = []
            for i in range(10):
                vine_angle = side * (math.pi / 4) + i * 0.3 + math.sin(t * 2 + i) * 0.2
                vine_dist = 10 + i * 3
                vine_x = 60 + math.cos(vine_angle) * vine_dist
                vine_y = 50 + math.sin(vine_angle) * vine_dist
                vine_segments.append((vine_x, vine_y))
            for i in range(len(vine_segments) - 1):
                pygame.draw.line(s, (40, 120, 40), (int(vine_segments[i][0]), int(vine_segments[i][1])), 
                               (int(vine_segments[i+1][0]), int(vine_segments[i+1][1])), 3)
            # 藤蔓叶子
            for i in range(0, len(vine_segments), 3):
                leaf_x, leaf_y = vine_segments[i]
                pygame.draw.circle(s, (80, 180, 80), (int(leaf_x), int(leaf_y)), 3)
        
        # 森林灵体（绿色精灵）
        spirit_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            spirit_angle = t * 2 + i * math.pi / 4
            spirit_dist = 25 + 8 * math.sin(t * 3 + i)
            spirit_x = 60 + math.cos(spirit_angle) * spirit_dist
            spirit_y = 50 + math.sin(spirit_angle) * spirit_dist
            # 精灵光球
            pygame.draw.circle(spirit_surface, (100, 255, 100, 220), (int(spirit_x), int(spirit_y)), 4)
            pygame.draw.circle(spirit_surface, (150, 255, 150, 180), (int(spirit_x), int(spirit_y)), 6)
        s.blit(spirit_surface, (0, 0))
        
        # 生命气息（绿色粒子上升）
        life_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(15):
            life_x = 50 + (i % 3) * 10 + int(3 * math.sin(t * 2 + i))
            life_y = 70 - ((t * 30 + i * 6) % 50)
            life_alpha = int(200 * (1 - ((t * 30 + i * 6) % 50) / 50))
            pygame.draw.circle(life_surface, (80, 220, 80, life_alpha), (life_x, int(life_y)), 3)
        s.blit(life_surface, (0, 0))
        
        # 根系网络（地下根须）
        root_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            root_angle = math.pi / 2 + (i - 3) * math.pi / 12
            root_length = 20 + 5 * math.sin(t + i)
            root_x = 60 + math.cos(root_angle) * root_length
            root_y = 68 + math.sin(root_angle) * root_length
            pygame.draw.line(root_surface, (80, 60, 40, 180), (60, 68), (int(root_x), int(root_y)), 2)
        s.blit(root_surface, (0, 0))
        
        return s
    
    elif model_style == "crystal":
        # 水晶巨人·棱镜折射 - 水晶形态、光线折射、能量晶核、棱镜效果
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：水晶六边形结构
        crystal_points = [
            (60, 25),
            (70, 35),
            (70, 55),
            (60, 65),
            (50, 55),
            (50, 35)
        ]
        crystal_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(crystal_surface, (150, 200, 255, 230), crystal_points)
        pygame.draw.polygon(crystal_surface, (200, 230, 255, 250), crystal_points, 3)
        s.blit(crystal_surface, (0, 0))
        
        # 水晶内部裂纹（折射线）
        for i in range(8):
            crack_start = crystal_points[i % 6]
            crack_end = crystal_points[(i + 3) % 6]
            pygame.draw.line(s, (180, 220, 255, 200), crack_start, crack_end, 1)
        
        # 能量晶核（中心发光核心）
        core_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        core_radius = int(8 * pulse)
        pygame.draw.circle(core_glow, (100, 200, 255, 250), (60, 45), core_radius)
        pygame.draw.circle(core_glow, (150, 230, 255, 200), (60, 45), core_radius + 4)
        s.blit(core_glow, (0, 0))
        
        # 光线折射（从核心射出）
        refraction_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            ray_angle = t * 3 + i * math.pi / 6
            ray_length = 25 + 10 * math.sin(t * 2 + i)
            ray_x = 60 + math.cos(ray_angle) * ray_length
            ray_y = 45 + math.sin(ray_angle) * ray_length
            # 彩虹色光线
            hue = (i * 30) % 360
            r = int(127 + 127 * math.sin(math.radians(hue)))
            g = int(127 + 127 * math.sin(math.radians(hue + 120)))
            b = int(127 + 127 * math.sin(math.radians(hue + 240)))
            pygame.draw.line(refraction_surface, (r, g, b, 220), (60, 45), (int(ray_x), int(ray_y)), 2)
        s.blit(refraction_surface, (0, 0))
        
        # 水晶碎片环绕
        shard_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            shard_angle = t * 2 + i * math.pi / 5
            shard_dist = 30 + 5 * math.sin(t * 3 + i)
            shard_x = 60 + math.cos(shard_angle) * shard_dist
            shard_y = 45 + math.sin(shard_angle) * shard_dist
            # 小水晶碎片（三角形）
            shard_points = [
                (shard_x, shard_y - 4),
                (shard_x + 3, shard_y + 3),
                (shard_x - 3, shard_y + 3)
            ]
            pygame.draw.polygon(shard_surface, (180, 220, 255, 220), [(int(p[0]), int(p[1])) for p in shard_points])
        s.blit(shard_surface, (0, 0))
        
        # 棱镜光谱效果
        spectrum_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            spectrum_radius = 20 + i * 5 + int(5 * pulse)
            spectrum_alpha = int(150 * (1 - i / 6))
            hue_shift = (t * 100 + i * 60) % 360
            r = int(127 + 127 * math.sin(math.radians(hue_shift)))
            g = int(127 + 127 * math.sin(math.radians(hue_shift + 120)))
            b = int(127 + 127 * math.sin(math.radians(hue_shift + 240)))
            pygame.draw.circle(spectrum_surface, (r, g, b, spectrum_alpha), (60, 45), spectrum_radius, 2)
        s.blit(spectrum_surface, (0, 0))
        
        return s
    
    elif model_style == "rock":
        # 岩石巨人·大地之力 - 岩石形态、大地能量、岩石粒子、坚不可摧
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.5) * 0.1 + 1
        
        # 主体：岩石巨人身躯
        rock_body = [(60, 30), (75, 48), (72, 68), (48, 68), (45, 48)]
        pygame.draw.polygon(s, (100, 80, 60), rock_body)
        pygame.draw.polygon(s, (150, 120, 100), rock_body, 3)
        
        # 岩石纹理（裂缝）
        for i in range(8):
            crack_x1 = 50 + (i % 3) * 10
            crack_y1 = 35 + (i // 3) * 10
            crack_x2 = crack_x1 + 5 + int(3 * math.sin(t + i))
            crack_y2 = crack_y1 + 8
            pygame.draw.line(s, (80, 60, 40), (crack_x1, crack_y1), (crack_x2, crack_y2), 2)
        
        # 大地之力（地脉能量）
        earth_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            earth_angle = i * math.pi / 3
            earth_x = 60 + math.cos(earth_angle) * 20
            earth_y = 50 + math.sin(earth_angle) * 20
            # 地脉节点
            pygame.draw.circle(earth_surface, (200, 150, 100, 220), (int(earth_x), int(earth_y)), 5)
            # 连线到中心
            pygame.draw.line(earth_surface, (180, 130, 80, 180), (60, 50), (int(earth_x), int(earth_y)), 2)
        s.blit(earth_surface, (0, 0))
        
        # 岩石粒子飞舞
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            particle_angle = t * 2 + i * math.pi / 10
            particle_dist = 25 + 15 * (i / 20)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            # 岩石碎片
            pygame.draw.rect(particle_surface, (120, 100, 80, 220), (int(particle_x - 2), int(particle_y - 2), 4, 4))
        s.blit(particle_surface, (0, 0))
        
        # 大地护盾（岩石层）
        for i in range(4):
            shield_radius = 22 + i * 8 + int(6 * pulse)
            shield_alpha = int(150 * (1 - i / 4))
            shield_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 六边形护盾
            shield_points = []
            for j in range(6):
                angle = j * math.pi / 3 + t
                shield_points.append((
                    int(60 + math.cos(angle) * shield_radius),
                    int(50 + math.sin(angle) * shield_radius)
                ))
            pygame.draw.polygon(shield_surface, (150, 120, 100, shield_alpha), shield_points, 2)
            s.blit(shield_surface, (0, 0))
        
        # 地震波动（冲击波）
        for i in range(3):
            wave_radius = (t * 50 + i * 30) % 90
            wave_alpha = int(200 * (1 - wave_radius / 90))
            wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, (180, 130, 80, wave_alpha), (60, 50), int(wave_radius), 3)
            s.blit(wave_surface, (0, 0))
        
        return s
    
    elif model_style == "elemental":
        # 元素领主·自然四元 - 四元素环绕、地水火风交织、元素形态
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：元素核心
        pygame.draw.circle(s, (100, 200, 150), (60, 50), 12)
        pygame.draw.circle(s, (150, 255, 200), (60, 50), 12, 2)
        
        # 四元素环绕（地、水、火、风）
        elements = [
            {"angle": 0, "color": (150, 100, 50), "name": "地"},           # 地（棕色）
            {"angle": math.pi / 2, "color": (50, 150, 255), "name": "水"},  # 水（蓝色）
            {"angle": math.pi, "color": (255, 100, 50), "name": "火"},      # 火（红色）
            {"angle": 3 * math.pi / 2, "color": (200, 255, 200), "name": "风"}  # 风（浅绿）
        ]
        
        for i, elem in enumerate(elements):
            elem_angle = elem["angle"] + t * 1.5
            elem_dist = 28 + 5 * math.sin(t * 3 + i)
            elem_x = 60 + math.cos(elem_angle) * elem_dist
            elem_y = 50 + math.sin(elem_angle) * elem_dist
            
            # 元素球
            elem_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(elem_surface, (*elem["color"], 230), (int(elem_x), int(elem_y)), 8)
            pygame.draw.circle(elem_surface, (*elem["color"], 180), (int(elem_x), int(elem_y)), 12, 2)
            s.blit(elem_surface, (0, 0))
            
            # 元素特效
            if elem["name"] == "地":
                # 地：岩石碎片
                for j in range(3):
                    rock_x = elem_x + (j - 1) * 4
                    rock_y = elem_y + 10
                    pygame.draw.rect(s, elem["color"], (int(rock_x), int(rock_y), 3, 3))
            elif elem["name"] == "水":
                # 水：水滴
                for j in range(3):
                    drop_y = elem_y + 10 + j * 4
                    pygame.draw.circle(s, elem["color"], (int(elem_x), int(drop_y)), 2)
            elif elem["name"] == "火":
                # 火：火焰
                flame_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
                for j in range(3):
                    flame_y = elem_y - 10 - j * 4 - int(3 * math.sin(t * 5 + j))
                    pygame.draw.circle(flame_surface, (*elem["color"], 220 - j * 50), (int(elem_x), int(flame_y)), 3 - j)
                s.blit(flame_surface, (0, 0))
            elif elem["name"] == "风":
                # 风：螺旋气流
                for j in range(3):
                    wind_angle = t * 6 + j * 2 * math.pi / 3
                    wind_x = elem_x + math.cos(wind_angle) * 8
                    wind_y = elem_y + math.sin(wind_angle) * 8
                    pygame.draw.circle(s, elem["color"], (int(wind_x), int(wind_y)), 2)
        
        # 元素连接线（能量流动）
        connection_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(4):
            elem1_angle = elements[i]["angle"] + t * 1.5
            elem2_angle = elements[(i + 1) % 4]["angle"] + t * 1.5
            elem1_dist = 28 + 5 * math.sin(t * 3 + i)
            elem2_dist = 28 + 5 * math.sin(t * 3 + (i + 1))
            x1 = 60 + math.cos(elem1_angle) * elem1_dist
            y1 = 50 + math.sin(elem1_angle) * elem1_dist
            x2 = 60 + math.cos(elem2_angle) * elem2_dist
            y2 = 50 + math.sin(elem2_angle) * elem2_dist
            pygame.draw.line(connection_surface, (150, 255, 200, 150), (int(x1), int(y1)), (int(x2), int(y2)), 2)
        s.blit(connection_surface, (0, 0))
        
        # 元素交织效果
        blend_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            blend_angle = t * 3 + i * math.pi / 6
            blend_dist = 20 + 8 * math.sin(t * 2 + i)
            blend_x = 60 + math.cos(blend_angle) * blend_dist
            blend_y = 50 + math.sin(blend_angle) * blend_dist
            # 混合色
            hue = (i * 30) % 360
            r = int(127 + 127 * math.sin(math.radians(hue)))
            g = int(127 + 127 * math.sin(math.radians(hue + 120)))
            b = int(127 + 127 * math.sin(math.radians(hue + 240)))
            pygame.draw.circle(blend_surface, (r, g, b, 200), (int(blend_x), int(blend_y)), 3)
        s.blit(blend_surface, (0, 0))
        
        return s
    
    elif model_style == "overgrowth":
        # 过度生长·野性爆发 - 植被疯长、藤蔓肆意、野性力量、自然失控
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：被植被覆盖的形态
        overgrown_body = [(60, 32), (70, 48), (68, 64), (52, 64), (50, 48)]
        pygame.draw.polygon(s, (20, 80, 20), overgrown_body)
        pygame.draw.polygon(s, (50, 120, 50), overgrown_body, 2)
        
        # 疯狂生长的藤蔓（多条）
        for vine_idx in range(8):
            vine_angle_base = vine_idx * math.pi / 4
            vine_segments = []
            for i in range(12):
                vine_angle = vine_angle_base + i * 0.2 + math.sin(t * 3 + vine_idx + i * 0.5) * 0.4
                vine_dist = 15 + i * 3
                vine_x = 60 + math.cos(vine_angle) * vine_dist
                vine_y = 50 + math.sin(vine_angle) * vine_dist
                vine_segments.append((vine_x, vine_y))
            # 绘制藤蔓
            for i in range(len(vine_segments) - 1):
                vine_width = max(1, 5 - i // 3)
                pygame.draw.line(s, (40, 140, 40), (int(vine_segments[i][0]), int(vine_segments[i][1])), 
                               (int(vine_segments[i+1][0]), int(vine_segments[i+1][1])), vine_width)
        
        # 野性植物爆发（尖刺）
        thorn_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(16):
            thorn_angle = t * 2 + i * math.pi / 8
            thorn_dist = 22 + 10 * math.sin(t * 4 + i)
            thorn_x = 60 + math.cos(thorn_angle) * thorn_dist
            thorn_y = 50 + math.sin(thorn_angle) * thorn_dist
            # 尖刺
            thorn_tip_x = thorn_x + math.cos(thorn_angle) * 8
            thorn_tip_y = thorn_y + math.sin(thorn_angle) * 8
            pygame.draw.line(thorn_surface, (80, 200, 80, 220), (int(thorn_x), int(thorn_y)), 
                           (int(thorn_tip_x), int(thorn_tip_y)), 3)
            pygame.draw.circle(thorn_surface, (100, 220, 100, 220), (int(thorn_tip_x), int(thorn_tip_y)), 2)
        s.blit(thorn_surface, (0, 0))
        
        # 植被粒子（花粉、孢子）
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(30):
            particle_angle = t * 2 + i * math.pi / 15
            particle_dist = 20 + 20 * (i / 30) + 5 * math.sin(t * 4 + i)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            pygame.draw.circle(particle_surface, (120, 255, 120, 220), (int(particle_x), int(particle_y)), 2)
        s.blit(particle_surface, (0, 0))
        
        # 失控的生命能量（绿色爆发）
        energy_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(4):
            energy_radius = 20 + i * 10 + int(8 * pulse)
            energy_alpha = int(180 * (1 - i / 4))
            pygame.draw.circle(energy_surface, (50, 200, 50, energy_alpha), (60, 50), energy_radius, 3)
        s.blit(energy_surface, (0, 0))
        
        return s
    
    elif model_style == "treant":
        # 树人长老·世界古树 - 树人形态、古树智慧、森林守护
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.5) * 0.1 + 1
        
        # 主体：树人身躯
        treant_body = [(60, 25), (72, 45), (70, 68), (50, 68), (48, 45)]
        pygame.draw.polygon(s, (80, 60, 40), treant_body)
        pygame.draw.polygon(s, (120, 100, 70), treant_body, 3)
        
        # 树人面孔（树皮纹理）
        # 眼睛（发光）
        for eye_x in [55, 65]:
            pygame.draw.circle(s, (100, 255, 100), (eye_x, 40), 3)
            eye_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(eye_glow, (100, 255, 100, 200), (eye_x, 40), 5)
            s.blit(eye_glow, (0, 0))
        # 嘴（树皮裂缝）
        pygame.draw.arc(s, (60, 40, 20), (53, 45, 14, 8), 0, math.pi, 2)
        
        # 树枝手臂
        for side in [-1, 1]:
            arm_base_x = 60 + side * 10
            arm_base_y = 50
            # 主干
            arm_end_x = arm_base_x + side * 15
            arm_end_y = arm_base_y + 5
            pygame.draw.line(s, (100, 80, 60), (arm_base_x, arm_base_y), (arm_end_x, arm_end_y), 4)
            # 分支
            for i in range(3):
                branch_angle = (side * math.pi / 4) + i * 0.3
                branch_x = arm_end_x + math.cos(branch_angle) * 8
                branch_y = arm_end_y + math.sin(branch_angle) * 8
                pygame.draw.line(s, (100, 80, 60), (arm_end_x, arm_end_y), (int(branch_x), int(branch_y)), 2)
        
        # 头顶树冠
        crown_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            crown_x = 50 + i * 5
            crown_y = 20 - int(5 * math.sin(t * 2 + i))
            pygame.draw.circle(crown_surface, (60, 180, 60, 220), (crown_x, crown_y), 4)
        s.blit(crown_surface, (0, 0))
        
        # 古树智慧（符文）
        rune_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            rune_y = 35 + i * 6
            rune_x = 60 + int(3 * math.sin(t * 2 + i))
            # 古老符文（圆形）
            pygame.draw.circle(rune_surface, (150, 200, 100, 200), (rune_x, rune_y), 2)
        s.blit(rune_surface, (0, 0))
        
        # 森林守护光环
        for i in range(3):
            guardian_radius = 25 + i * 10 + int(5 * pulse)
            guardian_alpha = int(150 * (1 - i / 3))
            guardian_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(guardian_surface, (80, 180, 80, guardian_alpha), (60, 50), guardian_radius, 2)
            s.blit(guardian_surface, (0, 0))
        
        # 千年智慧粒子
        wisdom_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            wisdom_angle = t + i * math.pi / 6
            wisdom_dist = 30 + 8 * math.sin(t * 2 + i)
            wisdom_x = 60 + math.cos(wisdom_angle) * wisdom_dist
            wisdom_y = 50 + math.sin(wisdom_angle) * wisdom_dist
            pygame.draw.circle(wisdom_surface, (150, 200, 100, 220), (int(wisdom_x), int(wisdom_y)), 3)
        s.blit(wisdom_surface, (0, 0))
        
        return s
    
    elif model_style == "titan":
        # 盖亚泰坦·星球化身 - 星球泰坦、盖亚意志、地壳浮动、星球之力
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：星球形态（地球）
        planet_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(planet_surface, (50, 150, 250, 230), (60, 50), 20)
        pygame.draw.circle(planet_surface, (80, 180, 255, 250), (60, 50), 20, 2)
        s.blit(planet_surface, (0, 0))
        
        # 大陆板块（绿色陆地）
        continents = [
            [(55, 40), (65, 42), (63, 48), (57, 47)],
            [(48, 52), (54, 54), (52, 58), (47, 56)],
            [(66, 55), (72, 56), (70, 60), (65, 59)]
        ]
        for continent in continents:
            pygame.draw.polygon(s, (100, 200, 100), continent)
        
        # 地壳板块浮动（板块运动）
        plate_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            plate_angle = t * 0.5 + i * math.pi / 4
            plate_dist = 22 + 3 * math.sin(t * 2 + i)
            plate_x = 60 + math.cos(plate_angle) * plate_dist
            plate_y = 50 + math.sin(plate_angle) * plate_dist
            # 板块碎片
            pygame.draw.rect(plate_surface, (150, 130, 100, 200), (int(plate_x - 3), int(plate_y - 3), 6, 6))
        s.blit(plate_surface, (0, 0))
        
        # 盖亚意志（生命能量脉冲）
        will_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(4):
            will_radius = 25 + i * 10 + int(10 * pulse)
            will_alpha = int(200 * (1 - i / 4))
            pygame.draw.circle(will_surface, (100, 200, 150, will_alpha), (60, 50), will_radius, 3)
        s.blit(will_surface, (0, 0))
        
        # 星球之力（能量射线）
        power_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            power_angle = t * 2 + i * math.pi / 6
            power_length = 30 + 15 * (i / 12)
            power_x = 60 + math.cos(power_angle) * power_length
            power_y = 50 + math.sin(power_angle) * power_length
            pygame.draw.line(power_surface, (150, 200, 180, 220), (60, 50), (int(power_x), int(power_y)), 2)
        s.blit(power_surface, (0, 0))
        
        # 大气层（蓝色光晕）
        atmosphere_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(3):
            atm_radius = 22 + i * 4
            atm_alpha = int(150 * (1 - i / 3))
            pygame.draw.circle(atmosphere_surface, (100, 180, 255, atm_alpha), (60, 50), atm_radius, 2)
        s.blit(atmosphere_surface, (0, 0))
        
        # 生命之环（绿色生命圈）
        life_ring_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            ring_angle = t * 3 + i * math.pi / 10
            ring_x = 60 + math.cos(ring_angle) * 28
            ring_y = 50 + math.sin(ring_angle) * 28
            pygame.draw.circle(life_ring_surface, (100, 255, 100, 220), (int(ring_x), int(ring_y)), 2)
        s.blit(life_ring_surface, (0, 0))
        
        return s
    
    elif model_style == "gaia_ex":
        # 晶体丛林 - 生长的水晶，脉动光芒
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心地核
        pygame.draw.circle(s, (0, 150, 100), (60, 50), 15)
        pygame.draw.circle(s, (0, 200, 150), (60, 50), 15, 2)
        
        # 12根水晶柱（向外生长）
        for i in range(12):
            crystal_angle = i * math.pi / 6
            crystal_height = 20 + 15 * math.sin(t * 2 + i * 0.5)
            
            # 水晶基座
            base_x = 60 + math.cos(crystal_angle) * 15
            base_y = 50 + math.sin(crystal_angle) * 15
            
            # 水晶顶部
            tip_x = 60 + math.cos(crystal_angle) * (15 + crystal_height)
            tip_y = 50 + math.sin(crystal_angle) * (15 + crystal_height)
            
            # 水晶侧边
            side_angle1 = crystal_angle + 0.2
            side_angle2 = crystal_angle - 0.2
            side1_x = 60 + math.cos(side_angle1) * 15
            side1_y = 50 + math.sin(side_angle1) * 15
            side2_x = 60 + math.cos(side_angle2) * 15
            side2_y = 50 + math.sin(side_angle2) * 15
            
            crystal_points = [(int(tip_x), int(tip_y)), (int(side1_x), int(side1_y)), (int(side2_x), int(side2_y))]
            
            # 渐变色（由内到外）
            color_intensity = int(155 + 100 * (crystal_height / 35))
            pygame.draw.polygon(s, (0, color_intensity, 100), crystal_points)
            pygame.draw.polygon(s, (0, 255, 150), crystal_points, 2)
            
            # 水晶光芒
            if (int(t * 10) + i) % 3 == 0:
                glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (0, 255, 150, 150), (int(tip_x), int(tip_y)), 6)
                s.blit(glow_surf, (0, 0))
        
        return s
    
    elif model_style == "gaia_ex2":
        # 樱花树灵 - 樱花树形态，花瓣飘落
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 树干
        trunk_rect = pygame.Rect(52, 40, 16, 45)
        pygame.draw.rect(s, (120, 80, 60), trunk_rect)
        pygame.draw.rect(s, (150, 100, 80), trunk_rect, 2)
        
        # 树枝（摇曳）
        for branch_idx in range(5):
            branch_angle = (branch_idx - 2) * 0.4 + math.sin(t * 2 + branch_idx) * 0.2
            branch_length = 20 + branch_idx * 3
            bx = 60 + math.cos(branch_angle) * branch_length
            by = 45 + branch_idx * 5
            pygame.draw.line(s, (140, 90, 70), (60, int(by)), (int(bx), int(by)), 3)
            
            # 樱花簇
            for flower in range(3):
                flower_angle = branch_angle + (flower - 1) * 0.3
                flower_dist = branch_length * 0.7
                fx = 60 + math.cos(flower_angle) * flower_dist
                fy = by
                pygame.draw.circle(s, (255, 180, 200), (int(fx), int(fy)), 5)
        
        # 樱花花瓣飘落（大量）
        for petal_idx in range(30):
            petal_y = (t * 30 + petal_idx * 8) % 120
            petal_x = 40 + (petal_idx * 3) % 40 + math.sin(t * 3 + petal_idx) * 15
            petal_rotation = t * 2 + petal_idx
            # 花瓣形状（椭圆）
            petal_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            petal_points = []
            for i in range(8):
                pa = i * math.pi / 4 + petal_rotation
                px = petal_x + math.cos(pa) * (4 if i % 2 == 0 else 2)
                py = petal_y + math.sin(pa) * (6 if i % 2 == 0 else 3)
                petal_points.append((int(px), int(py)))
            pygame.draw.polygon(petal_surf, (255, 150, 180, 220), petal_points)
            s.blit(petal_surf, (0, 0))
        
        # 春意光环
        for ring in range(3):
            spring_radius = 25 + ring * 12
            spring_alpha = int(180 - ring * 50)
            spring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(spring_surf, (255, 200, 220, spring_alpha), (60, 60), spring_radius, 2)
            s.blit(spring_surf, (0, 0))
        
        return s
    
    elif model_style == "gaia_ex3":
        # 四季更迭 - 轮回之树
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.5) * 0.15 + 1
        
        # 中心树干
        trunk_points = [(55, 80), (58, 40), (62, 40), (65, 80)]
        pygame.draw.polygon(s, (100, 70, 50), trunk_points)
        
        # 四季分区（树冠分成4个象限）
        seasons = [
            ("spring", 0, (100, 255, 150)),      # 春 - 绿色
            ("summer", math.pi / 2, (255, 200, 50)),   # 夏 - 金黄
            ("autumn", math.pi, (255, 100, 50)),      # 秋 - 橙红
            ("winter", 3 * math.pi / 2, (200, 230, 255))  # 冬 - 冰蓝
        ]
        
        for season_name, base_angle, color in seasons:
            # 每个季节占90度
            season_rotation = t * 2  # 整体旋转展示四季轮回
            
            for branch in range(8):
                branch_angle = base_angle + season_rotation + (branch / 8) * (math.pi / 2)
                branch_length = 20 + 15 * ((branch % 3) / 3)
                branch_x = 60 + math.cos(branch_angle) * branch_length
                branch_y = 50 + math.sin(branch_angle) * branch_length
                
                # 季节特色
                if season_name == "spring":  # 春 - 花朵
                    for petal in range(4):
                        petal_angle = t * 3 + petal * math.pi / 2
                        petal_x = branch_x + math.cos(petal_angle) * 4
                        petal_y = branch_y + math.sin(petal_angle) * 4
                        pygame.draw.circle(s, (255, 150, 200), (int(petal_x), int(petal_y)), 3)
                    pygame.draw.circle(s, color, (int(branch_x), int(branch_y)), 2)
                
                elif season_name == "summer":  # 夏 - 太阳光芒
                    pygame.draw.circle(s, color, (int(branch_x), int(branch_y)), 5)
                    for ray in range(6):
                        ray_angle = t * 4 + ray * math.pi / 3
                        ray_x = branch_x + math.cos(ray_angle) * 7
                        ray_y = branch_y + math.sin(ray_angle) * 7
                        pygame.draw.line(s, (255, 255, 100),
                                       (int(branch_x), int(branch_y)),
                                       (int(ray_x), int(ray_y)), 2)
                
                elif season_name == "autumn":  # 秋 - 落叶
                    leaf_fall = (t * 2 + branch) % 1
                    leaf_y = branch_y + leaf_fall * 30
                    leaf_alpha = int(255 * (1 - leaf_fall))
                    if leaf_alpha > 30:
                        leaf_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                        # 椭圆形叶子
                        leaf_rect = pygame.Rect(int(branch_x - 3), int(leaf_y - 2), 6, 4)
                        pygame.draw.ellipse(leaf_surf, (*color, leaf_alpha), leaf_rect)
                        s.blit(leaf_surf, (0, 0))
                
                else:  # 冬 - 雪花
                    # 六角雪花
                    for flake_arm in range(6):
                        flake_angle = branch_angle + flake_arm * math.pi / 3
                        flake_x = branch_x + math.cos(flake_angle) * 4
                        flake_y = branch_y + math.sin(flake_angle) * 4
                        pygame.draw.line(s, color,
                                       (int(branch_x), int(branch_y)),
                                       (int(flake_x), int(flake_y)), 1)
                    pygame.draw.circle(s, color, (int(branch_x), int(branch_y)), 2)
        
        # 轮回之环（四色环绕）
        for ring_seg in range(4):
            ring_color = seasons[ring_seg][2]
            ring_start_angle = seasons[ring_seg][1] + t * 2
            ring_end_angle = ring_start_angle + math.pi / 2
            
            # 绘制弧段
            arc_points = [(60, 50)]
            for arc_step in range(10):
                arc_progress = arc_step / 10
                arc_angle = ring_start_angle + (ring_end_angle - ring_start_angle) * arc_progress
                arc_x = 60 + math.cos(arc_angle) * 35
                arc_y = 50 + math.sin(arc_angle) * 35
                arc_points.append((int(arc_x), int(arc_y)))
            
            if len(arc_points) > 2:
                ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.lines(ring_surf, ring_color, False, arc_points, 3)
                s.blit(ring_surf, (0, 0))
        
        return s
    
    elif model_style == "gaia_ex4":
        # 万花筒梦境 - 镜像迷宫
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 万花筒对称（6重对称）
        symmetry = 6
        for sym in range(symmetry):
            base_angle = sym * math.pi * 2 / symmetry + t
            
            # 对称图案元素
            for element in range(5):
                elem_dist = 15 + element * 8
                elem_angle = base_angle + element * 0.5
                ex = 60 + int(math.cos(elem_angle) * elem_dist)
                ey = 50 + int(math.sin(elem_angle) * elem_dist)
                
                # 颜色循环
                color_index = (sym + element) % 3
                if color_index == 0:
                    elem_color = (255, 180, 100)
                elif color_index == 1:
                    elem_color = (100, 180, 255)
                else:
                    elem_color = (180, 255, 100)
                
                elem_size = 6 - element
                pygame.draw.circle(s, elem_color, (ex, ey), elem_size)
                
                # 连接到中心
                line_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(line_surf, (*elem_color, 150), (60, 50), (ex, ey), 1)
                s.blit(line_surf, (0, 0))
        
        # 旋转的几何形状
        shape_rotation = t * 2
        shape_sides = 6
        shape_radius = 20
        shape_points = []
        for i in range(shape_sides):
            angle = shape_rotation + i * math.pi * 2 / shape_sides
            px = 60 + int(math.cos(angle) * shape_radius)
            py = 50 + int(math.sin(angle) * shape_radius)
            shape_points.append((px, py))
        
        if len(shape_points) > 2:
            pygame.draw.polygon(s, (200, 200, 255, 180), shape_points, 3)
        
        return s
    
    elif model_style == "gaia_ex5":  # DNA螺旋·生命密码
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        
        # 双螺旋结构
        helix_length = 50
        helix_radius = 15
        for i in range(30):
            z = (i / 30.0) * helix_length - helix_length / 2
            angle1 = t + i * 0.3
            angle2 = angle1 + math.pi
            
            # 第一条螺旋
            x1 = center[0] + z * 0.4 + math.cos(angle1) * helix_radius
            y1 = center[1] + math.sin(angle1) * helix_radius
            helix1_color = (100, 255, 150)
            pygame.draw.circle(plane_surf, helix1_color, (int(x1), int(y1)), 3)
            
            # 第二条螺旋
            x2 = center[0] + z * 0.4 + math.cos(angle2) * helix_radius
            y2 = center[1] + math.sin(angle2) * helix_radius
            helix2_color = (255, 150, 100)
            pygame.draw.circle(plane_surf, helix2_color, (int(x2), int(y2)), 3)
            
            # 碱基对连接线
            if i % 3 == 0:
                pygame.draw.line(plane_surf, (150, 100, 255), (x1, y1), (x2, y2), 1)
        
        # 细胞分裂动画
        division_phase = (t % 2.0) / 2.0
        if division_phase < 0.5:
            cell_size = int(10 + division_phase * 30)
            pygame.draw.circle(plane_surf, (100, 255, 200), center, cell_size, 2)
        else:
            split_distance = int((division_phase - 0.5) * 40)
            pygame.draw.circle(plane_surf, (100, 255, 200), (center[0] - split_distance, center[1]), 10, 2)
            pygame.draw.circle(plane_surf, (100, 255, 200), (center[0] + split_distance, center[1]), 10, 2)
        return plane_surf
    
    return None
