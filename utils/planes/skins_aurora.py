"""
Aurora 专属涂装渲染模块

包含 Aurora 机体的6种专属涂装:
- goddess: 极光至尊·女神真身
- nebula: 星云之心·宇宙梦境
- ice_queen: 冰雪女王·永冻领域
- prism: 棱镜光辉·折射万象
- sakura: 樱花女神·春之降临
- celestial: 天界使者·神圣降临
- aurora_ex: 星环女神
- aurora_ex2: 冰霜精灵
- aurora_ex3: 北极光兽
- aurora_ex4: 蝴蝶效应
- aurora_ex5: 折纸艺术·千纸鹤
"""
import pygame
import math
import random


def render_aurora_skin(s, model_style, c, edge_color, t, pulse):
    """渲染 Aurora 专属涂装"""
    
    if model_style == "goddess":
        # 极光至尊·女神真身 - 冰晶王座、极光天幕、冰雪风暴、世界冻结
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：女神形态
        pygame.draw.ellipse(s, (255, 240, 220), (54, 38, 12, 26))
        pygame.draw.circle(s, (255, 250, 240), (60, 35), 6)  # 头部
        # 女神皇冠
        crown_points = [
            (55, 30), (58, 25), (60, 23), (62, 25), (65, 30)
        ]
        pygame.draw.polygon(s, (255, 255, 220), crown_points)
        pygame.draw.polygon(s, (255, 255, 255), crown_points, 2)
        
        # 冰晶王座（巨大结构）
        throne_points = [
            (40, 65), (45, 45), (55, 48), (60, 50),
            (65, 48), (75, 45), (80, 65)
        ]
        pygame.draw.polygon(s, (200, 240, 255), throne_points)
        pygame.draw.polygon(s, (255, 255, 255), throne_points, 2)
        # 王座细节（冰晶）
        for tx, ty in [(45, 50), (75, 50), (48, 58), (72, 58)]:
            pygame.draw.polygon(s, (220, 255, 255), [
                (tx, ty - 4), (tx + 3, ty), (tx, ty + 4), (tx - 3, ty)
            ])
        
        # 极光天幕覆盖（波浪光带）
        aurora_colors = [
            (100, 255, 200), (150, 255, 220), (200, 255, 240)
        ]
        for layer in range(3):
            aurora_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            for i in range(10):
                wave_x = 30 + i * 6
                wave_y = 20 + layer * 8 + int(5 * math.sin(t * 2 + i * 0.5 + layer))
                next_x = 30 + (i + 1) * 6
                next_y = 20 + layer * 8 + int(5 * math.sin(t * 2 + (i + 1) * 0.5 + layer))
                pygame.draw.line(aurora_surface, (*aurora_colors[layer], 180), (wave_x, wave_y), (next_x, next_y), 4)
            s.blit(aurora_surface, (0, 0))
        
        # 冰雪风暴（环绕冰晶）
        for i in range(20):
            snow_angle = t * 3 + i * math.pi / 10
            snow_dist = 25 + 20 * (i / 20) + 5 * math.sin(t * 2 + i)
            snow_x = 60 + math.cos(snow_angle) * snow_dist
            snow_y = 50 + math.sin(snow_angle) * snow_dist
            # 雪花
            pygame.draw.circle(s, (255, 255, 255), (int(snow_x), int(snow_y)), 2)
            # 六角雪花细节
            for spike in range(6):
                spike_angle = snow_angle + spike * math.pi / 3
                spike_x = snow_x + math.cos(spike_angle) * 3
                spike_y = snow_y + math.sin(spike_angle) * 3
                pygame.draw.line(s, (220, 240, 255), (int(snow_x), int(snow_y)), (int(spike_x), int(spike_y)), 1)
        
        # 世界冻结效果（扩散冰冻圈）
        for i in range(3):
            freeze_radius = 30 + i * 12 + int(8 * pulse)
            freeze_alpha = int(120 * (1 - i / 3))
            freeze_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(freeze_surface, (200, 240, 255, freeze_alpha), (60, 50), freeze_radius, 3)
            s.blit(freeze_surface, (0, 0))
        
        # 神圣光环
        halo_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(halo_surface, (255, 255, 255, 200), (60, 30), int(10 * pulse))
        s.blit(halo_surface, (0, 0))
        
        return s
    
    elif model_style == "nebula":
        # 星云之心·宇宙梦境 - 星云纹理、星尘粒子、宇宙梦境
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：星云核心
        pygame.draw.circle(s, (100, 50, 180), (60, 50), 12)
        pygame.draw.circle(s, (150, 100, 255), (60, 50), 12, 2)
        
        # 星云纹理流动（多层渐变云）
        nebula_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for layer in range(4):
            for i in range(12):
                nebula_angle = t * 1.5 + i * math.pi / 6 + layer * math.pi / 8
                nebula_dist = 15 + layer * 8 + 5 * math.sin(t * 2 + i)
                nx = 60 + math.cos(nebula_angle) * nebula_dist
                ny = 50 + math.sin(nebula_angle) * nebula_dist
                # 星云颜色（紫-蓝-粉渐变）
                color_r = 150 + int(50 * math.sin(t + i))
                color_g = 100 + int(50 * math.sin(t + i + 2))
                color_b = 255
                nebula_size = 10 - layer * 2
                nebula_alpha = 200 - layer * 40
                pygame.draw.circle(nebula_surface, (color_r, color_g, color_b, nebula_alpha), (int(nx), int(ny)), nebula_size)
        s.blit(nebula_surface, (0, 0))
        
        # 星尘粒子暴雨（大量小星星）
        for i in range(40):
            star_angle = t * 2 + i * math.pi / 20
            star_dist = 20 + 25 * (i / 40) + 5 * math.sin(t * 3 + i)
            star_x = 60 + math.cos(star_angle) * star_dist
            star_y = 50 + math.sin(star_angle) * star_dist
            # 闪烁星尘
            if (int(t * 12) + i) % 5 < 3:
                star_brightness = int(200 + 55 * math.sin(t * 4 + i))
                pygame.draw.circle(s, (180, 120, 255, star_brightness), (int(star_x), int(star_y)), 2)
                # 星光
                star_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(star_glow, (200, 150, 255, 120), (int(star_x), int(star_y)), 4)
                s.blit(star_glow, (0, 0))
        
        # 宇宙梦境显现（流动光带）
        dream_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            dream_angle = t * 3 + i * math.pi / 4
            dream_inner = 18
            dream_outer = 35
            inner_x = 60 + math.cos(dream_angle) * dream_inner
            inner_y = 50 + math.sin(dream_angle) * dream_inner
            outer_x = 60 + math.cos(dream_angle) * dream_outer
            outer_y = 50 + math.sin(dream_angle) * dream_outer
            # 梦境光束
            pygame.draw.line(dream_surface, (180, 120, 255, 150), (int(inner_x), int(inner_y)), (int(outer_x), int(outer_y)), 3)
        s.blit(dream_surface, (0, 0))
        
        return s
    
    elif model_style == "ice_queen":
        # 冰雪女王·永冻领域 - 冰晶王冠、冰霜领域、永冻统治
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：女王轮廓
        pygame.draw.ellipse(s, (200, 230, 255), (54, 40, 12, 24))
        pygame.draw.circle(s, (220, 240, 255), (60, 36), 5)
        
        # 冰晶王冠高耸（多层尖塔）
        crown_layers = [
            # 中央最高塔
            [(60, 18), (58, 28), (62, 28)],
            # 左右副塔
            [(54, 22), (52, 30), (56, 30)],
            [(66, 22), (64, 30), (68, 30)],
            # 外侧小塔
            [(50, 26), (48, 32), (52, 32)],
            [(70, 26), (68, 32), (72, 32)],
        ]
        for tower in crown_layers:
            pygame.draw.polygon(s, (200, 240, 255), tower)
            pygame.draw.polygon(s, (255, 255, 255), tower, 2)
            # 塔尖宝石
            tip_x = tower[0][0]
            tip_y = tower[0][1]
            pygame.draw.circle(s, (150, 220, 255), (tip_x, tip_y), 2)
        
        # 冰霜领域扩张（六边形冰域）
        hexagon_points = []
        for i in range(6):
            hex_angle = i * math.pi / 3 + t * 0.5
            hex_dist = 28 + int(8 * pulse)
            hx = 60 + math.cos(hex_angle) * hex_dist
            hy = 50 + math.sin(hex_angle) * hex_dist
            hexagon_points.append((int(hx), int(hy)))
        frost_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(frost_surface, (200, 240, 255, 150), hexagon_points)
        pygame.draw.polygon(frost_surface, (220, 255, 255, 200), hexagon_points, 3)
        s.blit(frost_surface, (0, 0))
        
        # 冰晶飘落（细碎冰晶）
        for i in range(30):
            ice_x = 30 + (t * 20 + i * 3) % 60
            ice_y = 20 + ((t * 25 + i * 4) % 60)
            # 小冰晶（菱形）
            ice_points = [
                (ice_x, ice_y - 2),
                (ice_x + 2, ice_y),
                (ice_x, ice_y + 2),
                (ice_x - 2, ice_y),
            ]
            pygame.draw.polygon(s, (210, 250, 255), [(int(p[0]), int(p[1])) for p in ice_points])
        
        # 永冻统治气息（冰冻波纹）
        for i in range(3):
            freeze_radius = 25 + i * 10 + (t * 25) % 15
            freeze_alpha = int(180 * (1 - ((t * 25) % 15) / 15))
            freeze_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(freeze_surface, (200, 240, 255, freeze_alpha), (60, 50), int(freeze_radius), 2)
            s.blit(freeze_surface, (0, 0))
        
        # 冰权杖（女王权杖）
        staff_x = 48 + int(3 * math.sin(t * 2))
        staff_y = 55
        pygame.draw.line(s, (180, 220, 255), (staff_x, staff_y), (staff_x, staff_y + 20), 3)
        # 权杖顶部宝石
        pygame.draw.circle(s, (150, 220, 255), (staff_x, staff_y), 5)
        staff_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(staff_glow, (200, 240, 255, 200), (staff_x, staff_y), int(8 * pulse))
        s.blit(staff_glow, (0, 0))
        
        return s
    
    elif model_style == "prism":
        # 棱镜光辉·折射万象 - 水晶棱镜、光芒折射、璀璨夺目
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：水晶棱镜结构（六面体）
        prism_points = [
            (60, 35),  # 顶点
            (70, 45), (68, 60), (60, 65),
            (52, 60), (50, 45)
        ]
        pygame.draw.polygon(s, (180, 220, 255), prism_points)
        pygame.draw.polygon(s, (220, 255, 255), prism_points, 3)
        
        # 棱镜内部折射面
        for i in range(6):
            facet_angle = i * math.pi / 3
            fx = 60 + math.cos(facet_angle) * 8
            fy = 50 + math.sin(facet_angle) * 8
            pygame.draw.line(s, (200, 240, 255), (60, 50), (int(fx), int(fy)), 2)
        
        # 光芒无限折射（多重反射光线）
        refraction_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        rainbow_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (139, 0, 255)]
        
        for i in range(21):
            ray_angle = t * 3 + i * math.pi / 10.5
            ray_start_dist = 12
            ray_end_dist = 40 + 5 * math.sin(t * 2 + i)
            start_x = 60 + math.cos(ray_angle) * ray_start_dist
            start_y = 50 + math.sin(ray_angle) * ray_start_dist
            end_x = 60 + math.cos(ray_angle) * ray_end_dist
            end_y = 50 + math.sin(ray_angle) * ray_end_dist
            # 彩色折射光
            color = rainbow_colors[i % 7]
            pygame.draw.line(refraction_surface, (*color, 180), (int(start_x), int(start_y)), (int(end_x), int(end_y)), 2)
            # 次级折射（分支）
            if i % 3 == 0:
                branch_angle = ray_angle + math.pi / 6
                branch_x = end_x + math.cos(branch_angle) * 10
                branch_y = end_y + math.sin(branch_angle) * 10
                pygame.draw.line(refraction_surface, (*color, 120), (int(end_x), int(end_y)), (int(branch_x), int(branch_y)), 1)
        s.blit(refraction_surface, (0, 0))
        
        # 万象光辉（旋转彩色光点）
        for i in range(24):
            light_angle = t * 4 + i * math.pi / 12
            light_dist = 25 + 10 * math.sin(t * 3 + i * 0.5)
            lx = 60 + math.cos(light_angle) * light_dist
            ly = 50 + math.sin(light_angle) * light_dist
            color = rainbow_colors[i % 7]
            pygame.draw.circle(s, color, (int(lx), int(ly)), 3)
            # 光辉闪耀
            light_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(light_glow, (*color, 150), (int(lx), int(ly)), 5)
            s.blit(light_glow, (0, 0))
        
        # 璀璨核心（中心脉冲）
        core_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(core_glow, (255, 255, 255, 220), (60, 50), int(12 * pulse))
        pygame.draw.circle(core_glow, (220, 255, 255, 150), (60, 50), int(18 * pulse))
        s.blit(core_glow, (0, 0))
        
        return s
    
    elif model_style == "sakura":
        # 樱花女神·春之降临 - 樱花暴雨、粉色花瓣海洋、生命绽放
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：女神形态
        pygame.draw.ellipse(s, (255, 200, 220), (54, 40, 12, 24))
        pygame.draw.circle(s, (255, 220, 230), (60, 36), 5)
        
        # 樱花王冠
        for i in range(5):
            petal_angle = i * 2 * math.pi / 5 + t * 2
            petal_x = 60 + math.cos(petal_angle) * 8
            petal_y = 30 + math.sin(petal_angle) * 8
            # 五瓣樱花
            for j in range(5):
                sub_angle = petal_angle + j * 2 * math.pi / 5
                sub_x = petal_x + math.cos(sub_angle) * 3
                sub_y = petal_y + math.sin(sub_angle) * 3
                pygame.draw.circle(s, (255, 180, 200), (int(sub_x), int(sub_y)), 2)
        
        # 樱花暴雨飞舞（大量花瓣）
        for i in range(60):
            petal_x = 20 + (t * 15 + i * 2) % 80
            petal_y = 10 + ((t * 20 + i * 3) % 90)
            petal_rotation = (t * 5 + i) % (2 * math.pi)
            # 五瓣花瓣
            for j in range(5):
                petal_angle = petal_rotation + j * 2 * math.pi / 5
                px = petal_x + math.cos(petal_angle) * 3
                py = petal_y + math.sin(petal_angle) * 3
                pygame.draw.circle(s, (255, 180, 200), (int(px), int(py)), 2)
            # 花瓣中心
            pygame.draw.circle(s, (255, 200, 220), (int(petal_x), int(petal_y)), 1)
        
        # 粉色花瓣海洋（环绕飘散）
        ocean_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(30):
            ocean_angle = t * 2 + i * math.pi / 15
            ocean_dist = 25 + 15 * (i / 30) + 5 * math.sin(t * 3 + i)
            ocean_x = 60 + math.cos(ocean_angle) * ocean_dist
            ocean_y = 50 + math.sin(ocean_angle) * ocean_dist
            # 飘散花瓣（椭圆形）
            pygame.draw.ellipse(ocean_surface, (255, 180, 200, 200), (int(ocean_x) - 3, int(ocean_y) - 2, 6, 4))
        s.blit(ocean_surface, (0, 0))
        
        # 春天生命气息（绿色生机）
        life_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            life_angle = t * 1.5 + i * math.pi / 6
            life_dist = 20 + 10 * math.sin(t * 2 + i)
            life_x = 60 + math.cos(life_angle) * life_dist
            life_y = 50 + math.sin(life_angle) * life_dist
            # 嫩芽（小绿点）
            pygame.draw.circle(life_surface, (150, 255, 150, 180), (int(life_x), int(life_y)), 2)
        s.blit(life_surface, (0, 0))
        
        # 樱花树枝（女神背后）
        branch_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for side in [-1, 1]:
            branch_x = 60 + side * 15
            pygame.draw.line(branch_surface, (139, 90, 60, 200), (60, 50), (branch_x, 30), 3)
            pygame.draw.line(branch_surface, (139, 90, 60, 200), (60, 50), (branch_x, 70), 3)
            # 枝上樱花
            for i in range(3):
                flower_x = 60 + side * (5 + i * 5)
                flower_y = 40 + i * 10
                for j in range(5):
                    f_angle = j * 2 * math.pi / 5 + t
                    fx = flower_x + math.cos(f_angle) * 2
                    fy = flower_y + math.sin(f_angle) * 2
                    pygame.draw.circle(branch_surface, (255, 180, 200, 220), (int(fx), int(fy)), 2)
        s.blit(branch_surface, (0, 0))
        
        return s
    
    elif model_style == "celestial":
        # 天界使者·神圣降临 - 天使光环、圣洁羽翼、天界之门、神圣力量
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：天使形态
        pygame.draw.ellipse(s, (255, 250, 240), (54, 38, 12, 26))
        pygame.draw.circle(s, (255, 255, 255), (60, 35), 5)
        
        # 天使光环闪耀（头顶）
        halo_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(halo_surface, (255, 255, 255, 220), (60, 25), int(10 * pulse))
        pygame.draw.circle(halo_surface, (255, 250, 240, 180), (60, 25), int(12 * pulse), 2)
        # 光环射线
        for i in range(12):
            ray_angle = t * 2 + i * math.pi / 6
            ray_x = 60 + math.cos(ray_angle) * 12
            ray_y = 25 + math.sin(ray_angle) * 12
            pygame.draw.line(halo_surface, (255, 255, 255, 200), (60, 25), (int(ray_x), int(ray_y)), 2)
        s.blit(halo_surface, (0, 0))
        
        # 圣洁羽翼展开（巨大白色翅膀）
        wing_colors = [(255, 255, 255), (255, 252, 245), (255, 250, 240)]
        for side in [-1, 1]:
            for i in range(8):
                wing_angle = side * (math.pi / 4 + i * math.pi / 20) + math.sin(t * 1.5 + i) * 0.1
                wing_length = 32 + i * 2
                wing_x = 60 + math.cos(wing_angle) * wing_length
                wing_y = 50 + math.sin(wing_angle) * wing_length
                # 多层羽毛
                for layer in range(3):
                    feather_offset = layer * 2
                    fx = 60 + math.cos(wing_angle) * (wing_length - feather_offset)
                    fy = 50 + math.sin(wing_angle) * (wing_length - feather_offset)
                    color = wing_colors[layer]
                    pygame.draw.line(s, color, (60, 50), (int(fx), int(fy)), 5 - layer)
                    # 羽毛发光
                    if layer == 0:
                        feather_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
                        pygame.draw.line(feather_glow, (255, 255, 255, 150), (60, 50), (int(fx), int(fy)), 7)
                        s.blit(feather_glow, (0, 0))
        
        # 天界之门打开（背后光门）
        gate_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        gate_width = int(20 * pulse)
        gate_height = 35
        pygame.draw.rect(gate_surface, (255, 255, 255, 180), (60 - gate_width//2, 30, gate_width, gate_height))
        # 门框光芒
        pygame.draw.rect(gate_surface, (255, 250, 240, 220), (60 - gate_width//2 - 2, 28, gate_width + 4, gate_height + 4), 3)
        s.blit(gate_surface, (0, 0))
        
        # 神圣力量（圣光粒子）
        for i in range(30):
            holy_angle = t * 3 + i * math.pi / 15
            holy_dist = 20 + 20 * (i / 30) + 5 * math.sin(t * 2 + i)
            holy_x = 60 + math.cos(holy_angle) * holy_dist
            holy_y = 50 + math.sin(holy_angle) * holy_dist
            pygame.draw.circle(s, (255, 255, 255), (int(holy_x), int(holy_y)), 2)
            # 圣光
            holy_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(holy_glow, (255, 255, 255, 180), (int(holy_x), int(holy_y)), 4)
            s.blit(holy_glow, (0, 0))
        
        # 神圣十字（祝福标记）
        cross_size = int(15 * pulse)
        cross_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(cross_surface, (255, 255, 255, 200), (60, 50 - cross_size), (60, 50 + cross_size), 3)
        pygame.draw.line(cross_surface, (255, 255, 255, 200), (60 - cross_size, 50), (60 + cross_size, 50), 3)
        s.blit(cross_surface, (0, 0))
        
        # 圣洁光环（外圈）
        for i in range(3):
            aura_radius = 30 + i * 10 + int(8 * pulse)
            aura_alpha = int(120 * (1 - i / 3))
            aura_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(aura_surface, (255, 255, 255, aura_alpha), (60, 50), aura_radius, 2)
            s.blit(aura_surface, (0, 0))
        
        return s

    elif model_style == "aurora_ex":
        # 星环女神 - 多重旋转光环，星光闪耀
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心女神形态（人形轮廓）
        pygame.draw.circle(s, (255, 220, 255), (60, 45), 12)
        pygame.draw.polygon(s, (200, 180, 255), [(60, 57), (50, 75), (70, 75)])
        
        # 5个旋转光环
        for ring in range(5):
            ring_radius = 20 + ring * 8
            ring_angle_offset = t * (1 + ring * 0.3)
            ring_alpha = int(200 - ring * 30)
            
            ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 绘制环上的光点
            for i in range(12):
                point_angle = ring_angle_offset + i * math.pi / 6
                px = 60 + math.cos(point_angle) * ring_radius
                py = 50 + math.sin(point_angle) * ring_radius
                pygame.draw.circle(ring_surf, (255, 200, 255, ring_alpha), (int(px), int(py)), 3)
            
            # 绘制环线
            pygame.draw.circle(ring_surf, (255, 180, 255, ring_alpha // 2), (60, 50), ring_radius, 1)
            s.blit(ring_surf, (0, 0))
        
        # 星光闪烁
        for i in range(20):
            if (int(t * 10) + i) % 4 < 2:
                star_x = 20 + (i * 5) % 80
                star_y = 20 + (i * 7) % 60
                pygame.draw.circle(s, (255, 255, 255), (star_x, star_y), 2)
        
        return s
    
    elif model_style == "aurora_ex2":
        # 冰霜精灵 - 冰晶翅膀，雪花飘落
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 精灵身体（冰晶人形）
        pygame.draw.circle(s, (180, 230, 255), (60, 40), 10)  # 头
        body_points = [(60, 50), (55, 65), (53, 75), (60, 80), (67, 75), (65, 65)]
        pygame.draw.polygon(s, (150, 220, 255), body_points)
        
        # 冰晶翅膀（6片）
        for wing_idx in range(6):
            wing_angle = wing_idx * math.pi / 3 + t * 0.5
            wing_length = 25 + 8 * math.sin(t * 2 + wing_idx)
            # 翅膀主干
            wx = 60 + math.cos(wing_angle) * wing_length
            wy = 50 + math.sin(wing_angle) * wing_length
            pygame.draw.line(s, (200, 240, 255), (60, 50), (int(wx), int(wy)), 3)
            # 冰晶分支
            for branch in range(3):
                branch_angle = wing_angle + (branch - 1) * 0.4
                branch_dist = wing_length * 0.6
                bx = 60 + math.cos(branch_angle) * branch_dist
                by = 50 + math.sin(branch_angle) * branch_dist
                pygame.draw.line(s, (180, 230, 255), (int(wx), int(wy)), (int(bx), int(by)), 2)
        
        # 雪花飘落
        for i in range(20):
            snow_y = (t * 40 + i * 10) % 120
            snow_x = 30 + (i * 4) % 60 + math.sin(t * 2 + i) * 10
            # 六角雪花
            for j in range(6):
                sf_angle = j * math.pi / 3
                sf_x1 = snow_x + math.cos(sf_angle) * 3
                sf_y1 = snow_y + math.sin(sf_angle) * 3
                pygame.draw.line(s, (255, 255, 255), (int(snow_x), int(snow_y)), 
                               (int(sf_x1), int(sf_y1)), 1)
        
        # 冰封光环
        for ring in range(3):
            ice_radius = 20 + ring * 12
            ice_alpha = int(180 - ring * 50)
            ice_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(ice_surf, (180, 230, 255, ice_alpha), (60, 50), ice_radius, 2)
            s.blit(ice_surf, (0, 0))
        
        return s
    
    elif model_style == "aurora_ex3":
        # 北极光兽 - 极地守望
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.8) * 0.15 + 1
        
        # 狼形身体轮廓
        wolf_body = [
            (60, 35),  # 头部中心
            (50, 45), (45, 55),  # 前腿
            (48, 70), (52, 75),  # 前爪
            (60, 72), # 胸部
            (68, 75), (72, 70),  # 后腿
            (75, 55), (70, 45)  # 后躯
        ]
        pygame.draw.polygon(s, (180, 220, 255), wolf_body)
        pygame.draw.polygon(s, (200, 240, 255), wolf_body, 3)
        
        # 狼头（尖耳朵）
        # 左耳
        left_ear = [(53, 30), (50, 20), (57, 28)]
        pygame.draw.polygon(s, (180, 220, 255), left_ear)
        # 右耳
        right_ear = [(67, 30), (70, 20), (63, 28)]
        pygame.draw.polygon(s, (180, 220, 255), right_ear)
        # 狼嘴
        snout_points = [(60, 35), (55, 40), (60, 42), (65, 40)]
        pygame.draw.polygon(s, (200, 230, 255), snout_points)
        
        # 北极光毛发（流动的七彩光带）
        aurora_colors = [
            (0, 255, 150), (100, 255, 200), (150, 200, 255),
            (200, 150, 255), (255, 100, 200)
        ]
        
        for fur_layer in range(5):
            fur_y_offset = 40 + fur_layer * 8
            color_idx = fur_layer % len(aurora_colors)
            aurora_color = aurora_colors[color_idx]
            
            # 流动的光带
            fur_points = []
            for seg in range(10):
                seg_x = 40 + seg * 4
                seg_y = fur_y_offset + math.sin(t * 3 + seg * 0.3 + fur_layer) * 5
                fur_points.append((int(seg_x), int(seg_y)))
            
            # 绘制光带
            if len(fur_points) > 1:
                fur_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                for i in range(len(fur_points) - 1):
                    alpha = int(180 - i * 15)
                    pygame.draw.line(fur_surf, (*aurora_color, alpha),
                                   fur_points[i], fur_points[i + 1], 3)
                s.blit(fur_surf, (0, 0))
        
        # 北极光尾巴（长长的光流尾巴）
        tail_segments = 12
        for tail_seg in range(tail_segments):
            tail_progress = tail_seg / tail_segments
            tail_x = 70 + tail_seg * 3
            tail_y = 50 + math.sin(t * 2.5 + tail_seg * 0.4) * 15
            tail_size = int(8 * (1 - tail_progress))
            tail_alpha = int(220 * (1 - tail_progress))
            color_idx = tail_seg % len(aurora_colors)
            tail_color = aurora_colors[color_idx]
            
            if tail_size > 0:
                tail_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(tail_surf, (*tail_color, tail_alpha),
                                 (int(tail_x), int(tail_y)), tail_size)
                s.blit(tail_surf, (0, 0))
        
        # 极光粒子环绕
        for aurora_particle in range(20):
            ap_angle = t * 2 + aurora_particle * 0.3
            ap_dist = 25 + 15 * math.sin(t * 3 + aurora_particle)
            ap_x = 60 + math.cos(ap_angle) * ap_dist
            ap_y = 50 + math.sin(ap_angle) * ap_dist
            color_idx = aurora_particle % len(aurora_colors)
            ap_color = aurora_colors[color_idx]
            pygame.draw.circle(s, ap_color, (int(ap_x), int(ap_y)), 3)
        
        # 冰晶效果
        for crystal in range(8):
            cx_angle = t * 1.5 + crystal * math.pi / 4
            cx_dist = 35
            cx_x = 60 + math.cos(cx_angle) * cx_dist
            cx_y = 50 + math.sin(cx_angle) * cx_dist
            # 六角冰晶
            crystal_points = []
            for i in range(6):
                cp_angle = cx_angle + i * math.pi / 3
                cp_x = cx_x + math.cos(cp_angle) * 4
                cp_y = cx_y + math.sin(cp_angle) * 4
                crystal_points.append((int(cp_x), int(cp_y)))
            pygame.draw.polygon(s, (200, 240, 255, 200), crystal_points)
        
        return s
    
    elif model_style == "aurora_ex4":
        # 蝴蝶效应 - 混沌之翼
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 蝴蝶翅膀形状（洛伦兹吸引子投影）
        wing_points_left = []
        wing_points_right = []
        
        # 使用混沌方程生成翅膀轨迹
        for step in range(30):
            step_prog = step / 30
            # 简化的混沌轨迹
            chaos_x = 20 * math.sin(step_prog * math.pi * 4 + t * 2) * step_prog
            chaos_y = 25 * math.sin(step_prog * math.pi * 2 + t) * (1 - step_prog)
            
            # 左翼
            left_x = int(60 - 10 - chaos_x)
            left_y = int(50 + chaos_y)
            wing_points_left.append((left_x, left_y))
            
            # 右翼（镜像）
            right_x = int(60 + 10 + chaos_x)
            right_y = int(50 + chaos_y)
            wing_points_right.append((right_x, right_y))
        
        # 绘制翅膀（渐变色彩）
        for i in range(len(wing_points_left) - 1):
            color_prog = i / len(wing_points_left)
            # 彩虹渐变
            if color_prog < 0.33:
                wing_r = int(255 * (1 - color_prog / 0.33))
                wing_g = int(255 * (color_prog / 0.33))
                wing_b = 150
            elif color_prog < 0.67:
                wing_r = 150
                wing_g = int(255 * (1 - (color_prog - 0.33) / 0.34))
                wing_b = int(255 * ((color_prog - 0.33) / 0.34))
            else:
                wing_r = int(255 * ((color_prog - 0.67) / 0.33))
                wing_g = 150
                wing_b = int(255 * (1 - (color_prog - 0.67) / 0.33))
            
            wing_alpha = int(200 * (1 - color_prog * 0.5))
            
            # 左翼
            wing_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(wing_surf, (wing_r, wing_g, wing_b, wing_alpha),
                           wing_points_left[i], wing_points_left[i + 1], 4)
            s.blit(wing_surf, (0, 0))
            
            # 右翼
            wing_surf2 = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(wing_surf2, (wing_r, wing_g, wing_b, wing_alpha),
                           wing_points_right[i], wing_points_right[i + 1], 4)
            s.blit(wing_surf2, (0, 0))
        
        # 翅膀上的斑点（半随机生成）
        import random
        random.seed(int(t * 2))  # 半随机
        for spot in range(20):
            spot_side = spot % 2
            spot_prog = (spot // 2) / 10
            
            # 斑点位置
            base_x = 60 + (-25 if spot_side == 0 else 25)
            base_y = 50
            offset_x = int((random.random() - 0.5) * 30 * spot_prog)
            offset_y = int((random.random() - 0.5) * 40 * (1 - spot_prog))
            spot_x = base_x + offset_x
            spot_y = base_y + offset_y
            
            # 斑点颜色（随机）
            spot_colors = [
                (255, 100, 150),
                (150, 200, 255),
                (200, 255, 100),
                (255, 200, 100),
                (150, 100, 255)
            ]
            spot_color = spot_colors[spot % len(spot_colors)]
            spot_size = 3 + int(3 * random.random())
            spot_alpha = int(180 * (1 - spot_prog * 0.5))
            
            if spot_alpha > 30:
                pygame.draw.circle(s, (*spot_color, spot_alpha), (spot_x, spot_y), spot_size)
        
        random.seed()  # 重置随机种子
        
        # 混沌轨迹（粒子流）
        for particle in range(25):
            p_progress = (t * 2 + particle * 0.1) % 1
            # 混沌轨迹
            p_x = 60 + 35 * math.sin(p_progress * math.pi * 6 + particle * 0.3)
            p_y = 50 + 30 * math.cos(p_progress * math.pi * 4 + particle * 0.2)
            p_alpha = int(180 * (1 - p_progress))
            
            if p_alpha > 30:
                # 彩色粒子
                p_hue = (p_progress + particle / 25) % 1
                if p_hue < 0.5:
                    p_color = (255, int(255 * (p_hue * 2)), int(255 * (1 - p_hue * 2)))
                else:
                    p_color = (int(255 * (1 - (p_hue - 0.5) * 2)), int(255 * ((p_hue - 0.5) * 2)), 255)
                
                pygame.draw.circle(s, (*p_color, p_alpha), (int(p_x), int(p_y)), 2)
        
        # 蝴蝶身体
        body_segments = 5
        for seg in range(body_segments):
            seg_y = 35 + seg * 6
            seg_width = 4 - seg // 2
            pygame.draw.circle(s, (50, 50, 80), (60, seg_y), seg_width)
        
        # 触角
        for antenna in [-1, 1]:
            antenna_points = [(60, 35)]
            for ant_seg in range(5):
                ant_prog = ant_seg / 5
                ant_angle = -math.pi / 2 + antenna * (math.pi / 6 + ant_prog * math.pi / 6)
                ant_x = 60 + antenna * 5 + math.cos(ant_angle) * ant_prog * 12
                ant_y = 35 - math.sin(ant_angle) * ant_prog * 12
                antenna_points.append((int(ant_x), int(ant_y)))
            
            if len(antenna_points) > 1:
                pygame.draw.lines(s, (80, 80, 120), False, antenna_points, 2)
        
        return s
    
    elif model_style == "aurora_ex5":
        # 折纸艺术·千纸鹤
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 基础圆形
        pygame.draw.circle(s, (255, 200, 200), (60, 60), 45, 3)
        
        # 纸鹤轮廓
        for crane_idx in range(6):
            angle = t + crane_idx * 1.047
            distance = 20 + abs(math.sin(t + crane_idx)) * 10
            crane_x = 60 + math.cos(angle) * distance
            crane_y = 60 + math.sin(angle) * distance
            
            crane_size = 8
            crane_color = (255, 180 + crane_idx * 10, 180 + crane_idx * 10)
            
            # 纸鹤身体
            body_points = [
                (crane_x, crane_y - crane_size),
                (crane_x - crane_size, crane_y + crane_size//2),
                (crane_x + crane_size, crane_y + crane_size//2)
            ]
            pygame.draw.polygon(s, crane_color, body_points, 2)
            
            # 翅膀
            wing1_points = [
                (crane_x - crane_size//2, crane_y),
                (crane_x - crane_size * 1.5, crane_y - crane_size//2),
                (crane_x - crane_size, crane_y + crane_size//2)
            ]
            pygame.draw.polygon(s, crane_color, wing1_points, 1)
            
            wing2_points = [
                (crane_x + crane_size//2, crane_y),
                (crane_x + crane_size * 1.5, crane_y - crane_size//2),
                (crane_x + crane_size, crane_y + crane_size//2)
            ]
            pygame.draw.polygon(s, crane_color, wing2_points, 1)
        
        # 折痕线动画
        for i in range(8):
            fold_angle = t * 2 + i * 0.393
            fold_radius = 35
            fx1 = 60 + math.cos(fold_angle) * fold_radius
            fy1 = 60 + math.sin(fold_angle) * fold_radius
            fx2 = 60 - math.cos(fold_angle) * fold_radius
            fy2 = 60 - math.sin(fold_angle) * fold_radius
            pygame.draw.line(s, (200, 200, 200), (int(fx1), int(fy1)), (int(fx2), int(fy2)), 1)
        
        return s

    return None


# Aurora 涂装列表
AURORA_STYLES = [
    "goddess", "nebula", "ice_queen", "prism", "sakura", "celestial",
    "aurora_ex", "aurora_ex2", "aurora_ex3", "aurora_ex4", "aurora_ex5"
]


def is_aurora_style(model_style):
    """检查是否是 Aurora 专属涂装"""
    return model_style in AURORA_STYLES
