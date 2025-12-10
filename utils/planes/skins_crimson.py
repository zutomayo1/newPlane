"""
Crimson 专属涂装渲染模块

包含 Crimson 机体的7种专属涂装:
- blood: 绯红之刃·血月降临
- samurai: 绯红武士·血刃斩魂
- demon: 血魔降世·魔王降临
- inferno: 地狱烈焰·炼狱之火
- rose: 血玫瑰·致命之美
- dragon: 血龙咆哮·龙息焚天
- vampire: 吸血鬼·血族领主
"""
import pygame
import math


def render_crimson_skin(s, model_style, c, edge_color, t, pulse):
    """渲染 Crimson 专属涂装"""
    
    if model_style == "blood":
        # 绯红之刃·血月降临 - 血色光芒、血雾弥漫、血液飞溅、嗜血气息
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：刀刃形态
        blade_points = [(60, 30), (68, 48), (64, 65), (60, 68), (56, 65), (52, 48)]
        pygame.draw.polygon(s, (150, 0, 0), blade_points)
        pygame.draw.polygon(s, (200, 20, 20), blade_points, 2)
        
        # 血色光芒笼罩（红色辉光）
        blood_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(blood_glow, (180, 0, 0, 180), (60, 50), int(25 * pulse))
        pygame.draw.circle(blood_glow, (200, 30, 30, 120), (60, 50), int(32 * pulse))
        s.blit(blood_glow, (0, 0))
        
        # 血雾弥漫升腾（环绕雾气）
        fog_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(15):
            fog_angle = t * 1.5 + i * math.pi / 7.5
            fog_dist = 20 + 10 * math.sin(t * 2 + i)
            fog_x = 60 + math.cos(fog_angle) * fog_dist
            fog_y = 50 + math.sin(fog_angle) * fog_dist
            fog_size = 8 + int(4 * math.sin(t * 3 + i))
            pygame.draw.circle(fog_surface, (150, 0, 0, 150), (int(fog_x), int(fog_y)), fog_size)
        s.blit(fog_surface, (0, 0))
        
        # 血液飞溅特效（四周飞溅）
        for i in range(20):
            splash_angle = t * 3 + i * math.pi / 10
            splash_dist = 25 + 15 * (i / 20)
            splash_x = 60 + math.cos(splash_angle) * splash_dist
            splash_y = 50 + math.sin(splash_angle) * splash_dist
            # 血滴
            pygame.draw.circle(s, (200, 20, 20), (int(splash_x), int(splash_y)), 3)
            # 血迹轨迹
            trail_x = splash_x - math.cos(splash_angle) * 5
            trail_y = splash_y - math.sin(splash_angle) * 5
            pygame.draw.line(s, (180, 10, 10), (int(splash_x), int(splash_y)), (int(trail_x), int(trail_y)), 2)
        
        # 嗜血气息（红色波纹）
        for i in range(3):
            wave_radius = (t * 40 + i * 20) % 60
            wave_alpha = int(180 * (1 - wave_radius / 60))
            wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, (200, 0, 0, wave_alpha), (60, 50), int(wave_radius), 2)
            s.blit(wave_surface, (0, 0))
        
        return s
    
    elif model_style == "samurai":
        # 绯红武士·血刃斩魂 - 武士刀、武士道、快速斩击、一击毙命
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.15 + 1
        
        # 主体：武士轮廓
        pygame.draw.rect(s, (150, 0, 0), (52, 40, 16, 26))
        pygame.draw.rect(s, (200, 0, 0), (52, 40, 16, 26), 2)
        # 武士头盔
        helmet_points = [(60, 35), (65, 40), (55, 40)]
        pygame.draw.polygon(s, (100, 0, 0), helmet_points)
        
        # 武士刀闪耀（长刀）
        katana_angle = math.sin(t * 4) * 0.5 + math.pi / 4
        katana_length = 35
        katana_x = 60 + math.cos(katana_angle) * katana_length
        katana_y = 50 + math.sin(katana_angle) * katana_length
        # 刀身
        pygame.draw.line(s, (200, 200, 220), (60, 50), (int(katana_x), int(katana_y)), 4)
        # 刀刃发光
        blade_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(blade_glow, (255, 255, 255, 200), (60, 50), (int(katana_x), int(katana_y)), 6)
        s.blit(blade_glow, (0, 0))
        # 刀柄（金色护手）
        pygame.draw.circle(s, (255, 215, 0), (60, 50), 5)
        pygame.draw.circle(s, (220, 180, 0), (60, 50), 5, 2)
        
        # 快速斩击轨迹（残影）
        for i in range(5):
            trail_angle = katana_angle + (i - 2) * 0.2
            trail_alpha = int(200 - i * 40)
            trail_x = 60 + math.cos(trail_angle) * katana_length
            trail_y = 50 + math.sin(trail_angle) * katana_length
            trail_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(trail_surface, (255, 100, 100, trail_alpha), (60, 50), (int(trail_x), int(trail_y)), 3)
            s.blit(trail_surface, (0, 0))
        
        # 血刃特效（刀刃滴血）
        for i in range(3):
            blood_dist = 20 + i * 8
            blood_x = 60 + math.cos(katana_angle) * blood_dist
            blood_y = 50 + math.sin(katana_angle) * blood_dist
            drop_offset = int(5 * math.sin(t * 5 + i))
            pygame.draw.circle(s, (200, 0, 0), (int(blood_x), int(blood_y + drop_offset)), 2)
        
        # 武士道精神（红色气息）
        spirit_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            spirit_angle = t * 2 + i * math.pi / 4
            spirit_dist = 25 + 8 * math.sin(t * 2 + i)
            spirit_x = 60 + math.cos(spirit_angle) * spirit_dist
            spirit_y = 50 + math.sin(spirit_angle) * spirit_dist
            pygame.draw.circle(spirit_surface, (200, 0, 0, 150), (int(spirit_x), int(spirit_y)), 4)
        s.blit(spirit_surface, (0, 0))
        
        return s
    
    elif model_style == "demon":
        # 血魔降世·魔王降临 - 血魔之翼、血色魔纹、魔王形态、血之君主
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：魔王身躯
        demon_points = [(60, 32), (70, 48), (66, 62), (60, 68), (54, 62), (50, 48)]
        pygame.draw.polygon(s, (80, 0, 0), demon_points)
        pygame.draw.polygon(s, (120, 0, 0), demon_points, 3)
        
        # 魔王头部（角）
        # 左角
        pygame.draw.line(s, (100, 0, 0), (55, 32), (50, 22), 4)
        pygame.draw.circle(s, (120, 0, 0), (50, 22), 3)
        # 右角
        pygame.draw.line(s, (100, 0, 0), (65, 32), (70, 22), 4)
        pygame.draw.circle(s, (120, 0, 0), (70, 22), 3)
        
        # 血魔之翼展开（蝙蝠翼）
        wing_offset = int(10 * math.sin(t * 2))
        for side in [-1, 1]:
            # 翼膜
            wing_points = [
                (60, 48),
                (60 + side * (20 + wing_offset), 40),
                (60 + side * (25 + wing_offset), 50),
                (60 + side * (22 + wing_offset), 60),
                (60, 58)
            ]
            wing_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(wing_surface, (100, 0, 0, 200), wing_points)
            pygame.draw.polygon(wing_surface, (150, 10, 10, 220), wing_points, 2)
            s.blit(wing_surface, (0, 0))
            # 翼骨
            for i in range(3):
                bone_x = 60 + side * (18 + wing_offset + i * 3)
                bone_y = 42 + i * 8
                pygame.draw.line(s, (120, 0, 0), (60, 48), (bone_x, bone_y), 2)
        
        # 血色魔纹遍布（发光符文）
        rune_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            rune_angle = t * 2 + i * math.pi / 6
            rune_dist = 18 + 8 * math.sin(t * 3 + i)
            rune_x = 60 + math.cos(rune_angle) * rune_dist
            rune_y = 50 + math.sin(rune_angle) * rune_dist
            # 魔纹符号（十字）
            if (int(t * 6) + i) % 3 == 0:
                pygame.draw.line(rune_surface, (200, 0, 0, 220), (int(rune_x) - 3, int(rune_y)), (int(rune_x) + 3, int(rune_y)), 2)
                pygame.draw.line(rune_surface, (200, 0, 0, 220), (int(rune_x), int(rune_y) - 3), (int(rune_x), int(rune_y) + 3), 2)
        s.blit(rune_surface, (0, 0))
        
        # 血之君主气息（深红光环）
        for i in range(3):
            aura_radius = 28 + i * 10 + int(8 * pulse)
            aura_alpha = int(150 * (1 - i / 3))
            aura_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(aura_surface, (120, 0, 0, aura_alpha), (60, 50), aura_radius, 3)
            s.blit(aura_surface, (0, 0))
        
        return s
    
    elif model_style == "inferno":
        # 地狱烈焰·炼狱之火 - 地狱火海、烈焰席卷、炼狱高温、焚毁世界
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：火焰核心
        pygame.draw.circle(s, (200, 50, 0), (60, 50), 15)
        pygame.draw.circle(s, (255, 100, 0), (60, 50), 15, 2)
        
        # 地狱火海燃烧（底部火焰）
        inferno_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            fire_x = 30 + i * 3
            fire_y = 70 + int(10 * math.sin(t * 4 + i * 0.5))
            fire_height = 20 + 10 * math.sin(t * 5 + i)
            # 火焰柱
            pygame.draw.polygon(inferno_surface, (255, 80, 0, 220), [
                (fire_x, fire_y),
                (fire_x - 3, fire_y - fire_height),
                (fire_x + 3, fire_y - fire_height)
            ])
            # 火焰内核
            pygame.draw.polygon(inferno_surface, (255, 150, 0, 180), [
                (fire_x, fire_y),
                (fire_x - 2, fire_y - fire_height * 0.7),
                (fire_x + 2, fire_y - fire_height * 0.7)
            ])
        s.blit(inferno_surface, (0, 0))
        
        # 烈焰席卷一切（环绕火焰）
        for i in range(16):
            flame_angle = t * 4 + i * math.pi / 8
            flame_dist = 25 + 10 * math.sin(t * 3 + i)
            flame_x = 60 + math.cos(flame_angle) * flame_dist
            flame_y = 50 + math.sin(flame_angle) * flame_dist
            flame_size = 8 + int(4 * pulse)
            # 火球
            flame_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(flame_surface, (255, 100, 0, 220), (int(flame_x), int(flame_y)), flame_size)
            pygame.draw.circle(flame_surface, (255, 150, 0, 180), (int(flame_x), int(flame_y)), flame_size - 2)
            s.blit(flame_surface, (0, 0))
        
        # 炼狱高温（热浪扭曲）
        heat_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(3):
            heat_radius = 20 + i * 8 + (t * 30) % 20
            heat_alpha = int(150 * (1 - ((t * 30) % 20) / 20))
            pygame.draw.circle(heat_surface, (255, 120, 0, heat_alpha), (60, 50), int(heat_radius), 2)
        s.blit(heat_surface, (0, 0))
        
        # 焚毁世界（火焰爆发）
        explosion_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            exp_angle = i * math.pi / 6 + t * 2
            exp_dist = 30 + 15 * math.sin(t * 2.5 + i)
            exp_x = 60 + math.cos(exp_angle) * exp_dist
            exp_y = 50 + math.sin(exp_angle) * exp_dist
            # 爆炸火花
            pygame.draw.circle(explosion_surface, (255, 150, 0, 200), (int(exp_x), int(exp_y)), 5)
            pygame.draw.circle(explosion_surface, (255, 200, 100, 150), (int(exp_x), int(exp_y)), 8)
        s.blit(explosion_surface, (0, 0))
        
        return s
    
    elif model_style == "rose":
        # 血玫瑰·致命之美 - 血红玫瑰、带刺玫瑰丛、美丽致命、芬芳杀机
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：中心大玫瑰
        center_x, center_y = 60, 45
        # 玫瑰花瓣（多层）
        for layer in range(4):
            petal_count = 6 + layer * 2
            petal_dist = 6 + layer * 4
            for i in range(petal_count):
                petal_angle = t * 0.5 + i * 2 * math.pi / petal_count + layer * 0.3
                petal_x = center_x + math.cos(petal_angle) * petal_dist
                petal_y = center_y + math.sin(petal_angle) * petal_dist
                # 花瓣（椭圆）
                petal_color = (200 - layer * 20, 50, 80)
                pygame.draw.ellipse(s, petal_color, (int(petal_x) - 4, int(petal_y) - 3, 8, 6))
        # 花心
        pygame.draw.circle(s, (150, 30, 60), (center_x, center_y), 4)
        
        # 带刺玫瑰丛（藤蔓+刺）
        vine_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            vine_angle = i * 2 * math.pi / 5 + t * 0.3
            vine_length = 30
            # 藤蔓主干（波浪线）
            for j in range(8):
                segment_dist = j * 4
                segment_x = center_x + math.cos(vine_angle) * segment_dist + math.sin(t * 3 + j) * 3
                segment_y = center_y + math.sin(vine_angle) * segment_dist + math.cos(t * 3 + j) * 3
                next_dist = (j + 1) * 4
                next_x = center_x + math.cos(vine_angle) * next_dist + math.sin(t * 3 + j + 1) * 3
                next_y = center_y + math.sin(vine_angle) * next_dist + math.cos(t * 3 + j + 1) * 3
                pygame.draw.line(vine_surface, (100, 50, 0, 200), (int(segment_x), int(segment_y)), (int(next_x), int(next_y)), 3)
                # 刺（每隔一段）
                if j % 2 == 0:
                    thorn_angle = vine_angle + math.pi / 2
                    thorn_x = segment_x + math.cos(thorn_angle) * 5
                    thorn_y = segment_y + math.sin(thorn_angle) * 5
                    pygame.draw.line(vine_surface, (80, 0, 0, 220), (int(segment_x), int(segment_y)), (int(thorn_x), int(thorn_y)), 2)
        s.blit(vine_surface, (0, 0))
        
        # 血红玫瑰绽放（环绕小玫瑰）
        for i in range(8):
            rose_angle = t * 1.5 + i * math.pi / 4
            rose_dist = 28 + 8 * math.sin(t * 2 + i)
            rose_x = center_x + math.cos(rose_angle) * rose_dist
            rose_y = center_y + math.sin(rose_angle) * rose_dist
            # 小玫瑰
            for j in range(5):
                small_petal_angle = rose_angle + j * 2 * math.pi / 5
                small_petal_x = rose_x + math.cos(small_petal_angle) * 3
                small_petal_y = rose_y + math.sin(small_petal_angle) * 3
                pygame.draw.circle(s, (200, 50, 80), (int(small_petal_x), int(small_petal_y)), 2)
        
        # 芬芳杀机（粉红迷雾）
        mist_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            mist_x = center_x + int(25 * math.cos(t * 2 + i * 0.5))
            mist_y = center_y + int(25 * math.sin(t * 2 + i * 0.5))
            pygame.draw.circle(mist_surface, (220, 70, 100, 100), (mist_x, mist_y), 8)
        s.blit(mist_surface, (0, 0))
        
        return s
    
    elif model_style == "dragon":
        # 血龙咆哮·龙息焚天 - 血龙形态、龙息喷涌、血色龙鳞、龙威镇世
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：血龙头部
        dragon_head = [(60, 35), (70, 45), (68, 52), (60, 55), (52, 52), (50, 45)]
        pygame.draw.polygon(s, (180, 0, 0), dragon_head)
        pygame.draw.polygon(s, (220, 0, 0), dragon_head, 3)
        
        # 龙角
        pygame.draw.line(s, (200, 0, 0), (55, 35), (50, 25), 4)
        pygame.draw.circle(s, (255, 215, 0), (50, 25), 3)
        pygame.draw.line(s, (200, 0, 0), (65, 35), (70, 25), 4)
        pygame.draw.circle(s, (255, 215, 0), (70, 25), 3)
        
        # 龙眼（金色发光）
        for eye_x in [54, 66]:
            pygame.draw.circle(s, (255, 215, 0), (eye_x, 43), 4)
            pygame.draw.circle(s, (200, 0, 0), (eye_x, 43), 2)
            eye_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(eye_glow, (255, 215, 0, 180), (eye_x, 43), int(6 * pulse))
            s.blit(eye_glow, (0, 0))
        
        # 龙身（蛇形）
        body_segments = []
        for i in range(10):
            segment_angle = t * 2 + i * math.pi / 5
            segment_dist = 15 + i * 2
            seg_x = 60 + math.cos(segment_angle) * segment_dist
            seg_y = 55 + i * 3
            body_segments.append((seg_x, seg_y))
        for i in range(len(body_segments) - 1):
            pygame.draw.line(s, (180, 0, 0), (int(body_segments[i][0]), int(body_segments[i][1])), 
                           (int(body_segments[i+1][0]), int(body_segments[i+1][1])), 10)
        
        # 血色龙鳞闪耀
        scale_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(25):
            scale_angle = t * 2 + i * math.pi / 12.5
            scale_dist = 15 + 20 * (i / 25)
            scale_x = 60 + math.cos(scale_angle) * scale_dist
            scale_y = 50 + math.sin(scale_angle) * scale_dist
            # 龙鳞（菱形）
            if (int(t * 8) + i) % 4 < 2:
                scale_points = [
                    (scale_x, scale_y - 2),
                    (scale_x + 2, scale_y),
                    (scale_x, scale_y + 2),
                    (scale_x - 2, scale_y)
                ]
                pygame.draw.polygon(scale_surface, (220, 0, 0, 220), [(int(p[0]), int(p[1])) for p in scale_points])
                pygame.draw.polygon(scale_surface, (255, 215, 0, 200), [(int(p[0]), int(p[1])) for p in scale_points], 1)
        s.blit(scale_surface, (0, 0))
        
        # 龙息喷涌（火焰吐息）
        breath_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        breath_angle = math.pi / 2
        for i in range(15):
            breath_dist = 15 + i * 4
            breath_x = 60 + math.cos(breath_angle) * breath_dist
            breath_y = 55 + math.sin(breath_angle) * breath_dist
            breath_width = 8 + i
            breath_alpha = int(220 - i * 10)
            # 火焰扩散
            pygame.draw.circle(breath_surface, (255, 100, 0, breath_alpha), (int(breath_x), int(breath_y)), breath_width)
        s.blit(breath_surface, (0, 0))
        
        # 龙威镇世（威压波动）
        for i in range(3):
            aura_radius = 30 + i * 12 + int(10 * pulse)
            aura_alpha = int(150 * (1 - i / 3))
            aura_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(aura_surface, (220, 0, 0, aura_alpha), (60, 50), aura_radius, 3)
            s.blit(aura_surface, (0, 0))
        
        return s
    
    elif model_style == "vampire":
        # 吸血鬼·血族领主 - 吸血蝙蝠、血族纹章、血液吸收光束、暗夜猎食者
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：吸血鬼轮廓
        vampire_cloak = [
            (60, 35), (68, 48), (66, 65), (60, 70),
            (54, 65), (52, 48)
        ]
        pygame.draw.polygon(s, (50, 0, 30), vampire_cloak)
        pygame.draw.polygon(s, (100, 0, 50), vampire_cloak, 2)
        
        # 吸血鬼面部
        pygame.draw.circle(s, (150, 130, 130), (60, 40), 6)
        # 红眼
        for eye_x in [57, 63]:
            pygame.draw.circle(s, (200, 0, 0), (eye_x, 39), 2)
            eye_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(eye_glow, (200, 0, 0, 180), (eye_x, 39), 4)
            s.blit(eye_glow, (0, 0))
        # 尖牙
        pygame.draw.line(s, (255, 255, 255), (58, 42), (58, 45), 2)
        pygame.draw.line(s, (255, 255, 255), (62, 42), (62, 45), 2)
        
        # 吸血蝙蝠环绕（8只蝙蝠）
        for i in range(8):
            bat_angle = t * 3 + i * math.pi / 4
            bat_dist = 28 + 10 * math.sin(t * 2 + i)
            bat_x = 60 + math.cos(bat_angle) * bat_dist
            bat_y = 50 + math.sin(bat_angle) * bat_dist
            # 蝙蝠身体
            pygame.draw.circle(s, (80, 0, 40), (int(bat_x), int(bat_y)), 3)
            # 蝙蝠翅膀（左右）
            wing_offset = int(4 * math.sin(t * 6 + i))
            pygame.draw.line(s, (100, 0, 50), (int(bat_x), int(bat_y)), (int(bat_x - 5 - wing_offset), int(bat_y)), 2)
            pygame.draw.line(s, (100, 0, 50), (int(bat_x), int(bat_y)), (int(bat_x + 5 + wing_offset), int(bat_y)), 2)
        
        # 血族纹章（胸前）
        crest_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 纹章盾形
        crest_points = [(60, 48), (65, 52), (63, 58), (60, 60), (57, 58), (55, 52)]
        pygame.draw.polygon(crest_surface, (150, 0, 70, 220), crest_points)
        pygame.draw.polygon(crest_surface, (200, 0, 100, 220), crest_points, 2)
        # 纹章符号（蝙蝠）
        pygame.draw.circle(crest_surface, (200, 0, 100, 220), (60, 54), 2)
        pygame.draw.line(crest_surface, (200, 0, 100, 220), (60, 54), (57, 56), 1)
        pygame.draw.line(crest_surface, (200, 0, 100, 220), (60, 54), (63, 56), 1)
        s.blit(crest_surface, (0, 0))
        
        # 血液吸收光束（吸血射线）
        for i in range(4):
            beam_angle = t * 2 + i * math.pi / 2
            beam_length = 35 + 8 * math.sin(t * 3 + i)
            beam_x = 60 + math.cos(beam_angle) * beam_length
            beam_y = 50 + math.sin(beam_angle) * beam_length
            beam_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 吸血光束（从外向内）
            pygame.draw.line(beam_surface, (150, 0, 70, 200), (int(beam_x), int(beam_y)), (60, 50), 3)
            pygame.draw.circle(beam_surface, (200, 0, 100, 220), (int(beam_x), int(beam_y)), 4)
            s.blit(beam_surface, (0, 0))
        
        # 暗夜猎食者气息（暗红雾气）
        mist_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            mist_angle = t * 1.5 + i * math.pi / 5
            mist_dist = 20 + 8 * math.sin(t * 2 + i)
            mist_x = 60 + math.cos(mist_angle) * mist_dist
            mist_y = 50 + math.sin(mist_angle) * mist_dist
            pygame.draw.circle(mist_surface, (100, 0, 50, 120), (int(mist_x), int(mist_y)), 6)
        s.blit(mist_surface, (0, 0))
        
        return s

    elif model_style == "crimson_ex":
        # 血色尖刺 - 尖刺向外延伸，血液飞溅
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 中心血核
        pygame.draw.circle(s, (200, 0, 0), (60, 50), int(15 * pulse))
        pygame.draw.circle(s, (255, 50, 50), (60, 50), int(15 * pulse), 2)
        
        # 8根尖刺（动态伸缩）
        for i in range(8):
            spike_angle = i * math.pi / 4
            spike_length = 25 + 15 * math.sin(t * 3 + i)
            
            # 尖刺顶点
            spike_tip_x = 60 + math.cos(spike_angle) * spike_length
            spike_tip_y = 50 + math.sin(spike_angle) * spike_length
            
            # 尖刺基座（三角形）
            base_angle1 = spike_angle + 0.3
            base_angle2 = spike_angle - 0.3
            base_dist = 12
            base1_x = 60 + math.cos(base_angle1) * base_dist
            base1_y = 50 + math.sin(base_angle1) * base_dist
            base2_x = 60 + math.cos(base_angle2) * base_dist
            base2_y = 50 + math.sin(base_angle2) * base_dist
            
            spike_points = [(int(spike_tip_x), int(spike_tip_y)), (int(base1_x), int(base1_y)), (int(base2_x), int(base2_y))]
            pygame.draw.polygon(s, (180, 0, 0), spike_points)
            pygame.draw.polygon(s, (255, 0, 0), spike_points, 2)
        
        # 血液飞溅粒子
        for i in range(15):
            blood_angle = t * 4 + i * 0.4
            blood_dist = 20 + (t * 30 + i * 5) % 35
            bx = 60 + math.cos(blood_angle) * blood_dist
            by = 50 + math.sin(blood_angle) * blood_dist
            pygame.draw.circle(s, (200, 0, 50), (int(bx), int(by)), 3)
        
        return s

    elif model_style == "crimson_ex2":
        # 爆炸之星（超新星） - 星体爆发，能量释放
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.25 + 1
        
        # 超新星核心（极亮）
        for layer in range(6, 0, -1):
            core_radius = int(18 * pulse * (layer / 6))
            core_alpha = int(255 * (layer / 6))
            core_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(core_surf, (255, 255, 200, core_alpha), (60, 50), core_radius)
            s.blit(core_surf, (0, 0))
        
        # 爆炸冲击波（多层扩散）
        for wave in range(5):
            wave_radius = (t * 80 + wave * 20) % 100
            wave_alpha = int(200 * (1 - wave_radius / 100))
            wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surf, (255, 255, 150, wave_alpha), (60, 50), int(wave_radius), 4)
            s.blit(wave_surf, (0, 0))
        
        # 星云碎片飞溅（24个方向）
        for i in range(24):
            fragment_angle = i * math.pi / 12
            fragment_dist = 20 + (t * 60 + i * 5) % 50
            fx = 60 + math.cos(fragment_angle) * fragment_dist
            fy = 50 + math.sin(fragment_angle) * fragment_dist
            fragment_size = 6 - int(fragment_dist / 15)
            if fragment_size > 1:
                pygame.draw.circle(s, (255, 255, 100), (int(fx), int(fy)), fragment_size)
        
        # 能量射线
        for ray in range(12):
            ray_angle = ray * math.pi / 6 + t
            ray_length = 30 + 15 * math.sin(t * 2 + ray)
            rx = 60 + math.cos(ray_angle) * ray_length
            ry = 50 + math.sin(ray_angle) * ray_length
            ray_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(ray_surf, (255, 255, 200, 200), (60, 50), (int(rx), int(ry)), 3)
            s.blit(ray_surf, (0, 0))
        
        return s

    elif model_style == "crimson_ex3":
        # 恒星熔炉 - 核聚变
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.25 + 1
        
        # 核心反应堆（超亮中心）
        core_radius = int(12 * pulse)
        for core_layer in range(6, 0, -1):
            layer_radius = int(core_radius * (core_layer / 6))
            layer_brightness = int(255 * (core_layer / 6))
            layer_alpha = 255
            core_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 颜色从白到黄到红渐变
            if core_layer > 4:
                core_color = (255, 255, layer_brightness)
            elif core_layer > 2:
                core_color = (255, layer_brightness, 100)
            else:
                core_color = (255, 100, 50)
            pygame.draw.circle(core_surf, (*core_color, layer_alpha),
                             (60, 50), layer_radius)
            s.blit(core_surf, (0, 0))
        
        # 等离子体环流（旋转）
        plasma_rings = 4
        for ring in range(plasma_rings):
            ring_radius = 18 + ring * 8
            ring_rotation = t * (2 + ring * 0.3)
            ring_alpha = int(220 - ring * 40)
            
            # 不完整的圆环（模拟磁场线）
            for arc_seg in range(6):
                arc_start = ring_rotation + arc_seg * math.pi / 3
                arc_end = arc_start + math.pi / 4
                # 绘制弧段
                arc_points = []
                for arc_step in range(8):
                    arc_angle = arc_start + (arc_end - arc_start) * (arc_step / 8)
                    arc_x = 60 + math.cos(arc_angle) * ring_radius
                    arc_y = 50 + math.sin(arc_angle) * ring_radius
                    arc_points.append((int(arc_x), int(arc_y)))
                
                if len(arc_points) > 1:
                    plasma_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    for i in range(len(arc_points) - 1):
                        plasma_color = (255, 150 - ring * 30, 50)
                        pygame.draw.line(plasma_surf, (*plasma_color, ring_alpha),
                                       arc_points[i], arc_points[i + 1], 3)
                    s.blit(plasma_surf, (0, 0))
        
        # 太阳耀斑（喷射）
        flare_count = 8
        for flare in range(flare_count):
            flare_angle = t * 1.5 + flare * 2 * math.pi / flare_count
            flare_intensity = (math.sin(t * 4 + flare) + 1) / 2
            
            if flare_intensity > 0.5:  # 只在高强度时显示
                flare_length = 30 + 20 * flare_intensity
                flare_start_dist = 15
                flare_sx = 60 + math.cos(flare_angle) * flare_start_dist
                flare_sy = 50 + math.sin(flare_angle) * flare_start_dist
                flare_ex = 60 + math.cos(flare_angle) * flare_length
                flare_ey = 50 + math.sin(flare_angle) * flare_length
                
                # 多层耀斑
                for flare_layer in range(3):
                    flare_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    layer_offset = flare_layer * 2
                    layer_alpha = int(200 * flare_intensity - flare_layer * 50)
                    flare_color = (255, 200 - flare_layer * 50, 100)
                    
                    offset_angle = flare_angle + math.pi / 2
                    offset_x = math.cos(offset_angle) * layer_offset
                    offset_y = math.sin(offset_angle) * layer_offset
                    
                    pygame.draw.line(flare_surf, (*flare_color, layer_alpha),
                                   (int(flare_sx + offset_x), int(flare_sy + offset_y)),
                                   (int(flare_ex + offset_x), int(flare_ey + offset_y)), 4 - flare_layer)
                    s.blit(flare_surf, (0, 0))
        
        # 核反应粒子（高速喷射）
        for particle in range(30):
            particle_angle = particle * 0.4 + t * 5
            particle_progress = (t * 4 + particle * 0.1) % 1
            particle_dist = 10 + particle_progress * 45
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            particle_alpha = int(255 * (1 - particle_progress))
            particle_size = int(4 * (1 - particle_progress)) + 1
            
            if particle_alpha > 30:
                pygame.draw.circle(s, (255, 255, 200, particle_alpha),
                                 (int(px), int(py)), particle_size)
        
        # 热浪扭曲（环形热波）
        for heat_wave in range(3):
            wave_radius = (t * 50 + heat_wave * 25) % 75
            wave_alpha = int(150 * (1 - wave_radius / 75))
            wave_distortion = 5 * math.sin(t * 4 + heat_wave)
            
            wave_points = []
            for i in range(16):
                wave_angle = i * math.pi / 8
                distort = wave_distortion * math.sin(i)
                wx = 60 + math.cos(wave_angle) * (wave_radius + distort)
                wy = 50 + math.sin(wave_angle) * (wave_radius + distort)
                wave_points.append((int(wx), int(wy)))
            
            if len(wave_points) > 2:
                heat_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.polygon(heat_surf, (255, 150, 50, wave_alpha), wave_points, 2)
                s.blit(heat_surf, (0, 0))
        
        return s

    elif model_style == "crimson_ex4":
        # 烟火绽放 - 庆典之舞
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 烟花爆炸点（多个）
        fireworks = 5
        for fw in range(fireworks):
            # 每个烟花的爆炸进度
            fw_progress = ((t * 1.5 + fw * 0.4) % 1)
            fw_angle_offset = fw * 1.3
            fw_x = 60 + int(25 * math.cos(fw_angle_offset))
            fw_y = 50 + int(25 * math.sin(fw_angle_offset))
            
            # 烟花粒子
            if fw_progress < 0.8:
                particle_count = 16
                for particle in range(particle_count):
                    particle_angle = (particle / particle_count) * math.pi * 2
                    particle_dist = fw_progress * 30
                    px = fw_x + int(math.cos(particle_angle) * particle_dist)
                    py = fw_y + int(math.sin(particle_angle) * particle_dist)
                    
                    # 粒子颜色（随烟花变化）
                    if fw % 3 == 0:
                        p_color = (255, int(100 + 155 * (1 - fw_progress)), 100)
                    elif fw % 3 == 1:
                        p_color = (int(100 + 155 * (1 - fw_progress)), 255, 100)
                    else:
                        p_color = (100, int(100 + 155 * (1 - fw_progress)), 255)
                    
                    p_alpha = int(250 * (1 - fw_progress))
                    p_size = int(4 * (1 - fw_progress)) + 1
                    
                    if p_alpha > 30:
                        pygame.draw.circle(s, (*p_color, p_alpha), (px, py), p_size)
                        # 拖尾
                        trail_len = int(5 * (1 - fw_progress))
                        trail_x = fw_x + int(math.cos(particle_angle) * (particle_dist - trail_len))
                        trail_y = fw_y + int(math.sin(particle_angle) * (particle_dist - trail_len))
                        trail_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                        pygame.draw.line(trail_surf, (*p_color, p_alpha // 2),
                                       (trail_x, trail_y), (px, py), 2)
                        s.blit(trail_surf, (0, 0))
        
        # 持续的火花雨
        for spark in range(30):
            spark_progress = (t * 2 + spark * 0.1) % 1
            spark_x = 30 + (spark % 10) * 9
            spark_y = -10 + spark_progress * 130
            spark_alpha = int(200 * (1 - spark_progress))
            
            if spark_alpha > 30 and spark_y < 110:
                spark_colors = [(255, 50, 100), (255, 200, 50), (100, 150, 255)]
                spark_color = spark_colors[spark % 3]
                pygame.draw.circle(s, (*spark_color, spark_alpha), (spark_x, int(spark_y)), 2)
        
        return s

    elif model_style == "crimson_ex5":
        # 弹幕地狱·东方幻想
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 基础形状
        pygame.draw.circle(s, c, (60, 60), 45)
        pygame.draw.circle(s, edge_color, (60, 60), 45, 3)
        
        # 弹幕图案1：圆形扩散
        pattern1_count = 16
        for i in range(pattern1_count):
            angle = (t * 2) + (i / pattern1_count) * 2 * math.pi
            bullet_phase = (t * 1.5) % 1.0
            radius = 10 + bullet_phase * 25
            bx = 60 + math.cos(angle) * radius
            by = 60 + math.sin(angle) * radius
            bullet_color = (255, 100 + int(100 * bullet_phase), 150)
            pygame.draw.circle(s, bullet_color, (int(bx), int(by)), 2)
        
        # 弹幕图案2：螺旋弹幕
        for i in range(30):
            spiral_angle = t * 3 + i * 0.3
            spiral_radius = 5 + i * 0.8
            sx = 60 + math.cos(spiral_angle) * spiral_radius
            sy = 60 + math.sin(spiral_angle) * spiral_radius
            spiral_color = (150, 100, 255)
            pygame.draw.circle(s, spiral_color, (int(sx), int(sy)), 2)
        
        # 弹幕图案3：十字弹幕
        cross_phase = (t * 2) % 1.0
        for direction in range(4):
            angle = direction * 1.571
            for j in range(5):
                bullet_dist = 10 + (cross_phase + j * 0.2) * 20
                cx = 60 + math.cos(angle) * bullet_dist
                cy = 60 + math.sin(angle) * bullet_dist
                pygame.draw.circle(s, (100, 255, 150), (int(cx), int(cy)), 3)
        
        return s

    return None


# Crimson 涂装列表
CRIMSON_STYLES = [
    "blood", "samurai", "demon", "inferno", "rose", "dragon", "vampire",
    "crimson_ex", "crimson_ex2", "crimson_ex3", "crimson_ex4", "crimson_ex5"
]


def is_crimson_style(model_style):
    """检查是否是 Crimson 专属涂装"""
    return model_style in CRIMSON_STYLES
