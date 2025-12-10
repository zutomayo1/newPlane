# Necro 专属涂装渲染模块
# 包含: necro_lich, necro_bone, necro_plague, necro_soul, necro_reaper, necro_vampire, necro_undead

import pygame
import math

# Necro涂装列表
NECRO_STYLES = ["necro_lich", "necro_bone", "necro_plague", "necro_soul", "necro_reaper", "necro_vampire", "necro_undead",
                "necro_ex", "necro_ex2", "necro_ex3", "necro_ex4", "necro_ex5"]

def is_necro_style(model_style):
    """检查是否为Necro涂装"""
    return model_style in NECRO_STYLES

def render_necro_skin(s, c, model_style, t, pid, static=False):
    """渲染Necro涂装，返回Surface或None"""
    
    if model_style == "necro_lich":
        # 巫妖王·不死法师 - 巫妖形态、死亡魔法、灵魂囚笼、不死之力
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：巫妖头颅（骷髅头）
        skull_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(skull_surface, (100, 255, 100, 240), (60, 45), 16)
        pygame.draw.circle(skull_surface, (150, 255, 150, 220), (60, 45), int(16 * pulse))
        # 眼眶（绿色火焰）
        pygame.draw.circle(skull_surface, (50, 200, 50, 255), (54, 42), 5)
        pygame.draw.circle(skull_surface, (50, 200, 50, 255), (66, 42), 5)
        pygame.draw.circle(skull_surface, (150, 255, 150, 255), (54, 42), 3)
        pygame.draw.circle(skull_surface, (150, 255, 150, 255), (66, 42), 3)
        s.blit(skull_surface, (0, 0))
        
        # 灵魂囚笼（环绕的灵魂）
        soul_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            soul_angle = t * 2 + i * math.pi / 4
            soul_dist = 25 + 10 * math.sin(t * 2.5 + i)
            soul_x = 60 + math.cos(soul_angle) * soul_dist
            soul_y = 45 + math.sin(soul_angle) * soul_dist
            # 灵魂形态（小鬼魂）
            pygame.draw.circle(soul_surface, (100, 255, 100, 200), (int(soul_x), int(soul_y)), 5)
            pygame.draw.circle(soul_surface, (150, 255, 150, 180), (int(soul_x), int(soul_y) + 5), 4)
        s.blit(soul_surface, (0, 0))
        
        # 死亡魔法（法术符文）
        magic_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            rune_angle = t + i * math.pi / 3
            rune_dist = 35
            rune_x = 60 + math.cos(rune_angle) * rune_dist
            rune_y = 45 + math.sin(rune_angle) * rune_dist
            # 符文（五角星）
            rune_points = []
            for j in range(5):
                star_angle = rune_angle + j * 2 * math.pi / 5
                star_x = rune_x + math.cos(star_angle) * 4
                star_y = rune_y + math.sin(star_angle) * 4
                rune_points.append((star_x, star_y))
            if len(rune_points) >= 3:
                pygame.draw.polygon(magic_surface, (100, 255, 100, 220), 
                                  [(int(p[0]), int(p[1])) for p in rune_points], 2)
        s.blit(magic_surface, (0, 0))
        
        # 不死之力（能量波动）
        power_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(3):
            power_radius = (t * 50 + i * 30) % 90
            power_alpha = int(200 * (1 - power_radius / 90))
            pygame.draw.circle(power_surface, (100, 255, 100, power_alpha), (60, 45), int(power_radius), 2)
        s.blit(power_surface, (0, 0))
        
        return s
    
    elif model_style == "necro_bone":
        # 白骨王座·骸骨帝王 - 白骨王座、骸骨帝王、骨骼军团、死亡统治
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.1 + 1
        
        # 主体：王座（骨架结构）
        throne_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 王座底座
        pygame.draw.rect(throne_surface, (200, 200, 200, 240), (45, 55, 30, 15))
        # 王座靠背
        pygame.draw.rect(throne_surface, (220, 220, 220, 240), (48, 30, 24, 25))
        # 骨刺装饰
        for i in range(5):
            spike_x = 50 + i * 5
            pygame.draw.polygon(throne_surface, (255, 255, 255, 240), 
                              [(spike_x, 30), (spike_x + 2, 25), (spike_x + 4, 30)])
        s.blit(throne_surface, (0, 0))
        
        # 骸骨帝王头颅
        skull_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(skull_surface, (220, 220, 220, 250), (60, 40), 12)
        # 王冠（骨制）
        crown_points = [(54, 32), (60, 28), (66, 32)]
        pygame.draw.polygon(skull_surface, (255, 255, 255, 250), crown_points)
        # 眼眶
        pygame.draw.circle(skull_surface, (100, 100, 100, 255), (56, 40), 3)
        pygame.draw.circle(skull_surface, (100, 100, 100, 255), (64, 40), 3)
        s.blit(skull_surface, (0, 0))
        
        # 骨骼军团（环绕骷髅）
        army_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            army_angle = t * 1.5 + i * math.pi / 4
            army_dist = 35 + 10 * math.sin(t + i)
            army_x = 60 + math.cos(army_angle) * army_dist
            army_y = 50 + math.sin(army_angle) * army_dist
            # 小骷髅头
            pygame.draw.circle(army_surface, (200, 200, 200, 220), (int(army_x), int(army_y)), 5)
            pygame.draw.circle(army_surface, (100, 100, 100, 220), (int(army_x) - 2, int(army_y)), 2)
            pygame.draw.circle(army_surface, (100, 100, 100, 220), (int(army_x) + 2, int(army_y)), 2)
        s.blit(army_surface, (0, 0))
        
        # 死亡统治光环
        aura_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(3):
            aura_radius = 20 + i * 10 + int(5 * pulse)
            aura_alpha = int(180 * (1 - i / 3))
            pygame.draw.circle(aura_surface, (220, 220, 220, aura_alpha), (60, 45), aura_radius, 2)
        s.blit(aura_surface, (0, 0))
        
        return s
    
    elif model_style == "necro_plague":
        # 瘟疫传播·死亡疫病 - 瘟疫云团、疾病粒子、感染特效、死亡瘟疫
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：瘟疫核心
        plague_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(plague_surface, (100, 255, 0, 240), (60, 50), 14)
        pygame.draw.circle(plague_surface, (150, 255, 50, 220), (60, 50), int(14 * pulse))
        s.blit(plague_surface, (0, 0))
        
        # 瘟疫云团（扩散烟雾）
        cloud_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            cloud_angle = t + i * math.pi / 6
            cloud_dist = 18 + 12 * math.sin(t * 2 + i)
            cloud_x = 60 + math.cos(cloud_angle) * cloud_dist
            cloud_y = 50 + math.sin(cloud_angle) * cloud_dist
            cloud_size = 6 + 4 * math.sin(t * 2.5 + i)
            pygame.draw.circle(cloud_surface, (120, 255, 20, 180), (int(cloud_x), int(cloud_y)), int(cloud_size))
        s.blit(cloud_surface, (0, 0))
        
        # 疾病粒子（漂浮孢子）
        spore_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            spore_angle = t * 1.5 + i * math.pi / 10
            spore_dist = 25 + 20 * (i / 20)
            spore_x = 60 + math.cos(spore_angle) * spore_dist
            spore_y = 50 + math.sin(spore_angle) * spore_dist + 5 * math.sin(t * 3 + i)
            pygame.draw.circle(spore_surface, (150, 255, 50, 220), (int(spore_x), int(spore_y)), 3)
        s.blit(spore_surface, (0, 0))
        
        # 感染特效（蔓延纹路）
        infect_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            infect_angle = i * math.pi / 4
            infect_segments = []
            for j in range(6):
                seg_dist = 15 + j * 4
                seg_angle = infect_angle + math.sin(t * 2 + i + j * 0.5) * 0.3
                seg_x = 60 + math.cos(seg_angle) * seg_dist
                seg_y = 50 + math.sin(seg_angle) * seg_dist
                infect_segments.append((seg_x, seg_y))
            # 绘制感染线
            for j in range(len(infect_segments) - 1):
                pygame.draw.line(infect_surface, (100, 255, 0, 200), 
                               (int(infect_segments[j][0]), int(infect_segments[j][1])),
                               (int(infect_segments[j+1][0]), int(infect_segments[j+1][1])), 2)
        s.blit(infect_surface, (0, 0))
        
        return s
    
    elif model_style == "necro_soul":
        # 灵魂收集·魂瓶封印 - 魂瓶、封印魂魄、灵魂能量、亡魂哀嚎
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：魂瓶（瓶状）
        bottle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 瓶身
        pygame.draw.rect(bottle_surface, (0, 220, 255, 200), (50, 45, 20, 25))
        # 瓶颈
        pygame.draw.rect(bottle_surface, (0, 220, 255, 220), (55, 40, 10, 5))
        # 瓶盖
        pygame.draw.rect(bottle_surface, (100, 255, 255, 240), (54, 37, 12, 3))
        # 瓶口光芒
        pygame.draw.circle(bottle_surface, (100, 255, 255, 200), (60, 42), int(6 * pulse))
        s.blit(bottle_surface, (0, 0))
        
        # 封印的魂魄（瓶内灵魂）
        trapped_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            soul_y = 48 + i * 3 + int(5 * math.sin(t * 3 + i))
            if 48 <= soul_y <= 68:
                pygame.draw.circle(trapped_surface, (50, 240, 255, 220), (60, int(soul_y)), 3)
        s.blit(trapped_surface, (0, 0))
        
        # 灵魂能量涌动（从瓶口溢出）
        energy_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            energy_angle = t * 2 + i * math.pi / 5
            energy_dist = 10 + 15 * (i / 10)
            energy_x = 60 + math.cos(energy_angle) * energy_dist
            energy_y = 40 - (i / 10) * 15
            pygame.draw.circle(energy_surface, (100, 255, 255, int(220 * (1 - i / 10))), 
                             (int(energy_x), int(energy_y)), 3)
        s.blit(energy_surface, (0, 0))
        
        # 亡魂哀嚎（环绕鬼魂）
        ghost_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            ghost_angle = t * 1.5 + i * math.pi / 4
            ghost_dist = 30 + 10 * math.sin(t * 2 + i)
            ghost_x = 60 + math.cos(ghost_angle) * ghost_dist
            ghost_y = 55 + math.sin(ghost_angle) * ghost_dist
            # 鬼魂形态
            pygame.draw.circle(ghost_surface, (0, 220, 255, 180), (int(ghost_x), int(ghost_y)), 5)
            pygame.draw.circle(ghost_surface, (100, 255, 255, 160), (int(ghost_x), int(ghost_y) + 5), 4)
        s.blit(ghost_surface, (0, 0))
        
        return s
    
    elif model_style == "necro_reaper":
        # 死神化身·灵魂收割 - 死神形态、收割镰刀、死亡宣判、生命终结
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：死神头颅（骷髅）
        reaper_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(reaper_surface, (150, 0, 150, 240), (60, 45), 14)
        # 眼窝（紫色火焰）
        pygame.draw.circle(reaper_surface, (200, 100, 200, 255), (55, 43), 4)
        pygame.draw.circle(reaper_surface, (200, 100, 200, 255), (65, 43), 4)
        # 兜帽
        hood_points = [(45, 35), (60, 30), (75, 35), (70, 50), (50, 50)]
        pygame.draw.polygon(reaper_surface, (80, 0, 80, 220), hood_points)
        s.blit(reaper_surface, (0, 0))
        
        # 收割镰刀
        scythe_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 镰刀柄
        pygame.draw.line(scythe_surface, (100, 50, 100, 240), (60, 55), (60, 75), 4)
        # 镰刀刃（弧形）
        blade_points = [(60, 50), (75, 45), (78, 48), (62, 55)]
        pygame.draw.polygon(scythe_surface, (180, 50, 180, 240), blade_points)
        pygame.draw.polygon(scythe_surface, (200, 100, 200, 240), blade_points, 2)
        s.blit(scythe_surface, (0, 0))
        
        # 死亡宣判（降临光柱）
        judgment_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            beam_x = 58 + i
            beam_alpha = int(200 * math.sin(t * 3 + i))
            if beam_alpha > 0:
                pygame.draw.line(judgment_surface, (150, 0, 150, beam_alpha), 
                               (beam_x, 20), (beam_x, 80), 3)
        s.blit(judgment_surface, (0, 0))
        
        # 灵魂收割粒子
        harvest_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(15):
            harvest_angle = t * 2 + i * math.pi / 7.5
            harvest_dist = 25 + 15 * math.sin(t * 2.5 + i)
            harvest_x = 60 + math.cos(harvest_angle) * harvest_dist
            harvest_y = 50 + math.sin(harvest_angle) * harvest_dist
            pygame.draw.circle(harvest_surface, (180, 50, 180, 220), (int(harvest_x), int(harvest_y)), 3)
        s.blit(harvest_surface, (0, 0))
        
        # 生命终结光环
        end_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(3):
            end_radius = (t * 55 + i * 30) % 85
            end_alpha = int(200 * (1 - end_radius / 85))
            pygame.draw.circle(end_surface, (150, 0, 150, end_alpha), (60, 50), int(end_radius), 2)
        s.blit(end_surface, (0, 0))
        
        return s
    
    elif model_style == "necro_vampire":
        # 吸血鬼伯爵·永夜不朽 - 吸血鬼形态、蝙蝠群、鲜血吸收、永夜不朽
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：吸血鬼头像（苍白面容）
        vampire_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(vampire_surface, (150, 0, 50, 240), (60, 45), 14)
        # 眼睛（红色）
        pygame.draw.circle(vampire_surface, (200, 50, 100, 255), (55, 43), 3)
        pygame.draw.circle(vampire_surface, (200, 50, 100, 255), (65, 43), 3)
        # 獠牙
        pygame.draw.polygon(vampire_surface, (255, 255, 255, 255), [(57, 50), (57, 55), (59, 52)])
        pygame.draw.polygon(vampire_surface, (255, 255, 255, 255), [(63, 50), (63, 55), (61, 52)])
        s.blit(vampire_surface, (0, 0))
        
        # 蝙蝠群（飞舞）
        bat_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            bat_angle = t * 2.5 + i * math.pi / 4
            bat_dist = 25 + 15 * math.sin(t * 2 + i)
            bat_x = 60 + math.cos(bat_angle) * bat_dist
            bat_y = 45 + math.sin(bat_angle) * bat_dist
            # 蝙蝠形态（简化翅膀）
            wing_span = 6 + 2 * math.sin(t * 5 + i)
            pygame.draw.line(bat_surface, (80, 0, 40, 220), 
                           (int(bat_x - wing_span), int(bat_y)), 
                           (int(bat_x + wing_span), int(bat_y)), 2)
            pygame.draw.circle(bat_surface, (100, 0, 50, 220), (int(bat_x), int(bat_y)), 2)
        s.blit(bat_surface, (0, 0))
        
        # 鲜血吸收（血液粒子流向中心）
        blood_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(15):
            blood_progress = ((t * 2 + i * 0.2) % 1)
            blood_angle = i * math.pi / 7.5
            blood_dist = 40 - blood_progress * 25
            blood_x = 60 + math.cos(blood_angle) * blood_dist
            blood_y = 45 + math.sin(blood_angle) * blood_dist
            blood_alpha = int(220 * (1 - blood_progress))
            pygame.draw.circle(blood_surface, (180, 20, 70, blood_alpha), (int(blood_x), int(blood_y)), 3)
        s.blit(blood_surface, (0, 0))
        
        # 永夜光环（暗红色）
        aura_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(3):
            aura_radius = 18 + i * 10 + int(6 * pulse)
            aura_alpha = int(180 * (1 - i / 3))
            pygame.draw.circle(aura_surface, (150, 0, 50, aura_alpha), (60, 45), aura_radius, 2)
        s.blit(aura_surface, (0, 0))
        
        return s
    
    elif model_style == "necro_undead":
        # 不死军团·永恒行军 - 军团行军、永恒战争、亡者复苏、死而复生
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.5) * 0.1 + 1
        
        # 主体：军团旗帜（骷髅标志）
        banner_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 旗杆
        pygame.draw.line(banner_surface, (100, 160, 100, 240), (60, 30), (60, 70), 4)
        # 旗帜
        flag_points = [(60, 30), (75, 35), (75, 50), (60, 45)]
        pygame.draw.polygon(banner_surface, (80, 120, 80, 220), flag_points)
        # 骷髅标志
        pygame.draw.circle(banner_surface, (150, 200, 150, 240), (67, 40), 4)
        pygame.draw.circle(banner_surface, (50, 100, 50, 255), (66, 39), 1)
        pygame.draw.circle(banner_surface, (50, 100, 50, 255), (68, 39), 1)
        s.blit(banner_surface, (0, 0))
        
        # 行军的军团（前进的骷髅）
        legion_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            legion_x = 30 + (t * 20 + i * 8) % 60
            legion_y = 60 + i % 3 * 8
            # 骷髅头
            pygame.draw.circle(legion_surface, (150, 200, 150, 220), (int(legion_x), legion_y), 4)
            # 眼眶
            pygame.draw.circle(legion_surface, (80, 120, 80, 220), (int(legion_x) - 1, legion_y), 1)
            pygame.draw.circle(legion_surface, (80, 120, 80, 220), (int(legion_x) + 1, legion_y), 1)
        s.blit(legion_surface, (0, 0))
        
        # 亡者复苏特效（从地面升起）
        rise_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            rise_x = 40 + i * 10
            rise_progress = ((t * 2 + i * 0.3) % 1)
            rise_y = 80 - rise_progress * 20
            rise_alpha = int(220 * rise_progress)
            if rise_alpha > 50:
                pygame.draw.circle(rise_surface, (100, 160, 100, rise_alpha), (rise_x, int(rise_y)), 3)
        s.blit(rise_surface, (0, 0))
        
        # 永恒战争能量（环绕旋转）
        war_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            war_angle = t * 2 + i * math.pi / 6
            war_dist = 30 + 8 * math.sin(t * 2.5 + i)
            war_x = 60 + math.cos(war_angle) * war_dist
            war_y = 50 + math.sin(war_angle) * war_dist
            pygame.draw.circle(war_surface, (150, 200, 150, 220), (int(war_x), int(war_y)), 3)
        s.blit(war_surface, (0, 0))
        
        return s
    
    elif model_style == "necro_ex":
        # 死灵骑士 - 骷髅马，亡魂召唤
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 骑士头盔
        helmet_rect = pygame.Rect(45, 25, 30, 25)
        pygame.draw.rect(s, (100, 100, 100), helmet_rect)
        pygame.draw.rect(s, (150, 150, 150), helmet_rect, 2)
        
        # 幽绿眼睛
        pygame.draw.circle(s, (0, 255, 100), (52, 35), 4)
        pygame.draw.circle(s, (0, 255, 100), (68, 35), 4)
        
        # 骷髅马头（下方）
        horse_points = [(60, 55), (50, 65), (45, 75), (55, 80), (65, 80), (75, 75), (70, 65)]
        pygame.draw.polygon(s, (200, 200, 200), horse_points)
        pygame.draw.polygon(s, (255, 255, 255), horse_points, 2)
        
        # 马眼（幽火）
        pygame.draw.circle(s, (100, 255, 100), (54, 68), 3)
        
        # 召唤的亡魂（环绕）
        for i in range(12):
            soul_angle = t * 2 + i * math.pi / 6
            soul_dist = 35 + 10 * math.sin(t * 2.5 + i)
            soul_x = 60 + math.cos(soul_angle) * soul_dist
            soul_y = 55 + math.sin(soul_angle) * soul_dist
            
            # 骷髅头轮廓
            skull_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(skull_surf, (100, 255, 100, 200), (int(soul_x), int(soul_y)), 5)
            pygame.draw.circle(skull_surf, (100, 255, 100, 180), (int(soul_x - 2), int(soul_y - 1)), 1)
            pygame.draw.circle(skull_surf, (100, 255, 100, 180), (int(soul_x + 2), int(soul_y - 1)), 1)
            s.blit(skull_surf, (0, 0))
        
        # 死灵能量波
        for ring in range(3):
            wave_radius = (t * 55 + ring * 25) % 75
            wave_alpha = int(200 * (1 - wave_radius / 75))
            wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surf, (100, 255, 100, wave_alpha), (60, 55), int(wave_radius), 2)
            s.blit(wave_surf, (0, 0))
        
        return s
    
    elif model_style == "necro_ex2":
        # 虚无教主 - 万物归无，存在湮灭
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.2 + 1
        
        # 虚无核心（纯黑但带紫色边缘）
        pygame.draw.circle(s, (0, 0, 0), (60, 50), int(20 * pulse))
        for layer in range(3):
            void_radius = int(20 * pulse) + layer * 5
            void_alpha = int(150 - layer * 40)
            void_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(void_surf, (50, 0, 50, void_alpha), (60, 50), void_radius, 2)
            s.blit(void_surf, (0, 0))
        
        # 存在消散（粒子被吸入虚无）
        for particle in range(30):
            particle_progress = ((t * 2 + particle * 0.15) % 1)
            particle_angle = particle * 0.7
            particle_dist = 60 - particle_progress * 40
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            # 粒子逐渐消失
            particle_alpha = int(220 * (1 - particle_progress))
            particle_size = int(5 * (1 - particle_progress * 0.7))
            if particle_size > 0 and particle_alpha > 0:
                particle_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, (50, 50, 50, particle_alpha), 
                                 (int(px), int(py)), particle_size)
                s.blit(particle_surf, (0, 0))
        
        # 终焉之书（漂浮的黑色书页）
        for page in range(4):
            page_angle = t + page * math.pi / 2
            page_dist = 35 + 10 * math.sin(t * 2 + page)
            page_x = 60 + math.cos(page_angle) * page_dist
            page_y = 50 + math.sin(page_angle) * page_dist
            # 书页（矩形）
            page_rotation = math.sin(t * 3 + page) * 0.3
            page_points = []
            for corner in range(4):
                corner_angle = page_angle + corner * math.pi / 2 + page_rotation
                corner_dist = 8
                cx = page_x + math.cos(corner_angle) * corner_dist
                cy = page_y + math.sin(corner_angle) * corner_dist * 0.7
                page_points.append((int(cx), int(cy)))
            pygame.draw.polygon(s, (20, 20, 20), page_points)
            pygame.draw.polygon(s, (50, 50, 50), page_points, 1)
            # 书页上的符文
            pygame.draw.line(s, (80, 80, 80), (int(page_x - 5), int(page_y)), 
                           (int(page_x + 5), int(page_y)), 1)
        
        # 湮灭波动
        for wave in range(4):
            wave_radius = (t * 50 + wave * 25) % 100
            wave_alpha = int(180 * (1 - wave_radius / 100))
            wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surf, (20, 20, 20, wave_alpha), (60, 50), int(wave_radius), 2)
            s.blit(wave_surf, (0, 0))
        
        return s
    
    elif model_style == "necro_ex3":
        # 熵寂极限 - 热寂降临
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.2) * 0.1 + 1  # 缓慢脉动
        
        # 中心热寂核心（温度接近绝对零度）
        core_radius = int(12 * pulse)
        # 深蓝到黑的渐变（低温）
        for core_layer in range(6, 0, -1):
            layer_radius = int(core_radius * (core_layer / 6))
            layer_alpha = 255
            layer_blue = int(50 * (core_layer / 6))
            core_color = (layer_blue // 3, layer_blue // 3, layer_blue)
            pygame.draw.circle(s, (*core_color, layer_alpha), (60, 50), layer_radius)
        
        # 能量耗散（粒子运动逐渐停止）
        entropy_particles = 40
        for ep in range(entropy_particles):
            # 粒子速度递减
            ep_speed = 1 - (t % 3) / 3  # 随时间减速
            ep_angle = ep * 0.5 + t * ep_speed
            ep_dist = 15 + (ep % 8) * 4
            ep_x = 60 + math.cos(ep_angle) * ep_dist
            ep_y = 50 + math.sin(ep_angle) * ep_dist
            
            # 颜色渐暗（能量降低）
            ep_brightness = int(150 * ep_speed)
            ep_alpha = int(200 * ep_speed)
            ep_size = max(1, int(3 * ep_speed))
            
            if ep_alpha > 30:
                pygame.draw.circle(s, (ep_brightness // 2, ep_brightness // 2, ep_brightness, ep_alpha),
                                 (int(ep_x), int(ep_y)), ep_size)
        
        # 热环（能量均匀分布）
        thermal_rings = 6
        for ring in range(thermal_rings):
            ring_radius = 15 + ring * 8
            ring_alpha = int(100 - ring * 15)
            
            # 环不完整（象征结构崩解）
            ring_completeness = 1 - (ring / thermal_rings) * 0.5
            ring_segments = int(20 * ring_completeness)
            
            for seg in range(ring_segments):
                seg_angle = seg * 2 * math.pi / 20 + t * 0.3
                seg_x1 = 60 + math.cos(seg_angle) * ring_radius
                seg_y1 = 50 + math.sin(seg_angle) * ring_radius
                seg_angle2 = (seg + 1) * 2 * math.pi / 20 + t * 0.3
                seg_x2 = 60 + math.cos(seg_angle2) * ring_radius
                seg_y2 = 50 + math.sin(seg_angle2) * ring_radius
                
                if ring_alpha > 10:
                    ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(ring_surf, (50, 50, 80, ring_alpha),
                                   (int(seg_x1), int(seg_y1)),
                                   (int(seg_x2), int(seg_y2)), 2)
                    s.blit(ring_surf, (0, 0))
        
        # 宇宙微波背景辐射（均匀但冰冷）
        import random
        cmb_noise = 30
        for noise in range(cmb_noise):
            noise_x = random.randint(10, 110)
            noise_y = random.randint(10, 110)
            noise_brightness = random.randint(40, 70)
            noise_alpha = random.randint(50, 100)
            pygame.draw.circle(s, (noise_brightness, noise_brightness, noise_brightness + 20, noise_alpha),
                             (noise_x, noise_y), 1)
        
        # 时间箭头停滞（熵达到最大）
        # 绘制停滞的钟表指针
        clock_center = (60, 50)
        clock_radius = 35
        # 时钟边框（破碎）
        for clock_seg in range(8):
            if (clock_seg + int(t * 2)) % 3 != 0:  # 部分缺失
                seg_start_angle = clock_seg * math.pi / 4
                seg_end_angle = seg_start_angle + math.pi / 4
                clock_points = [clock_center]
                for angle_step in range(5):
                    angle = seg_start_angle + (seg_end_angle - seg_start_angle) * (angle_step / 4)
                    cx = clock_center[0] + math.cos(angle) * clock_radius
                    cy = clock_center[1] + math.sin(angle) * clock_radius
                    clock_points.append((int(cx), int(cy)))
                
                if len(clock_points) > 2:
                    clock_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.lines(clock_surf, (80, 80, 100, 150), False, clock_points, 1)
                    s.blit(clock_surf, (0, 0))
        
        # 停滞的指针（几乎不动）
        hand_angle = t * 0.1  # 极慢
        hand_length = 25
        hand_x = 60 + math.cos(hand_angle - math.pi / 2) * hand_length
        hand_y = 50 + math.sin(hand_angle - math.pi / 2) * hand_length
        pygame.draw.line(s, (100, 100, 130), (60, 50), (int(hand_x), int(hand_y)), 2)
        
        return s
    
    elif model_style == "necro_ex4":
        # 黑洞漩涡 - 引力舞蹈
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 黑洞中心（纯黑）
        event_horizon = 12
        for layer in range(5, 0, -1):
            layer_radius = int(event_horizon * (layer / 5))
            layer_darkness = int(100 * (1 - layer / 5))
            pygame.draw.circle(s, (layer_darkness // 3, 0, layer_darkness),
                             (60, 50), layer_radius)
        
        # 吸积盘（螺旋向内）
        accretion_particles = 40
        for particle in range(accretion_particles):
            p_angle = particle * 0.5 + t * 3
            p_progress = (t + particle * 0.05) % 1
            # 螺旋向内
            p_dist = 50 * (1 - p_progress) + event_horizon
            px = 60 + int(math.cos(p_angle) * p_dist)
            py = 50 + int(math.sin(p_angle) * p_dist * 0.3)  # 扁平化
            
            # 颜色：外围蓝->内部红（温度）
            if p_progress < 0.3:
                p_color = (100, 100, 255)
            elif p_progress < 0.6:
                p_color = (200, 150, 255)
            else:
                p_color = (255, int(150 * (1 - p_progress)), 100)
            
            p_alpha = int(220 * (1 - p_progress * 0.5))
            p_size = int(4 * (1 - p_progress)) + 1
            
            if p_alpha > 30:
                pygame.draw.circle(s, (*p_color, p_alpha), (px, py), p_size)
        
        # 引力透镜（光线弯曲）
        lens_rings = 5
        for ring in range(lens_rings):
            ring_radius = event_horizon + 10 + ring * 8
            ring_alpha = int(150 - ring * 25)
            
            # 扭曲的环
            ring_points = []
            for i in range(16):
                ring_angle = i * math.pi / 8 + t
                distortion = 5 * math.sin(t * 2 + i + ring)
                rx = 60 + int(math.cos(ring_angle) * (ring_radius + distortion))
                ry = 50 + int(math.sin(ring_angle) * (ring_radius + distortion))
                ring_points.append((rx, ry))
            
            if ring_alpha > 20 and len(ring_points) > 2:
                lens_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.lines(lens_surf, (100, 0, 150, ring_alpha), True, ring_points, 2)
                s.blit(lens_surf, (0, 0))
        
        # 霍金辐射
        for radiation in range(12):
            rad_angle = radiation * 0.5 + t * 4
            rad_progress = (t * 2 + radiation * 0.2) % 1
            rad_dist = event_horizon + 3 + rad_progress * 35
            rad_x = 60 + int(math.cos(rad_angle) * rad_dist)
            rad_y = 50 + int(math.sin(rad_angle) * rad_dist)
            rad_alpha = int(200 * (1 - rad_progress))
            
            if rad_alpha > 30:
                pygame.draw.circle(s, (150, 100, 200, rad_alpha), (rad_x, rad_y), 2)
        
        return s
    
    elif model_style == "necro_ex5":
        # 俄罗斯方块·消除爆炸
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        
        # 下落的方块
        tetromino_types = [
            [(0, 0), (1, 0), (2, 0), (3, 0)],
            [(0, 0), (1, 0), (0, 1), (1, 1)],
            [(0, 0), (1, 0), (2, 0), (1, 1)],
        ]
        
        for i in range(6):
            fall_phase = (t * 2 + i * 0.4) % 1.0
            tetromino = tetromino_types[i % len(tetromino_types)]
            
            base_x = center[0] - 18 + (i % 3) * 18
            base_y = center[1] - 35 + fall_phase * 70
            
            block_size = 6
            block_color = [(100, 255, 255), (255, 255, 100), (255, 100, 255)][i % 3]
            
            for block_dx, block_dy in tetromino:
                block_x = base_x + block_dx * block_size
                block_y = base_y + block_dy * block_size
                pygame.draw.rect(s, block_color, 
                               (block_x, block_y, block_size - 1, block_size - 1))
                pygame.draw.rect(s, 
                               tuple(min(255, c + 50) for c in block_color),
                               (block_x, block_y, block_size - 1, block_size - 1), 1)
        
        # 消除特效
        clear_phase = (t * 3) % 1.0
        if clear_phase < 0.3:
            clear_y = center[1] + 25
            clear_width = int(50 * (1 - clear_phase / 0.3))
            pygame.draw.rect(s, (255, 255, 255), 
                           (center[0] - 25, clear_y - 3, clear_width, 6))
            
            # 爆炸粒子
            for i in range(10):
                particle_angle = (i / 10.0) * 2 * math.pi
                particle_dist = (clear_phase / 0.3) * 35
                px = center[0] + math.cos(particle_angle) * particle_dist
                py = clear_y + math.sin(particle_angle) * particle_dist
                pygame.draw.circle(s, (255, 255, 100), (int(px), int(py)), 3)
        
        return s
    
    return None
