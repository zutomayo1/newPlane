"""
Specter 专属涂装渲染模块

包含 Specter 机体的7种专属涂装:
- reaper: 死神收割·灵魂收集者
- assassin: 幽灵刺客·无声夺命
- wraith: 幽灵怨灵·冤魂缠绕
- sniper: 幽灵狙击·远程收割
- poltergeist: 骚灵现象·灵异事件
- fallen_angel: 死亡天使·黑色羽翼
- void_hunter: 虚空猎手·维度收割
"""
import pygame
import math
import random


def render_specter_skin(s, model_style, c, edge_color, t, pulse):
    """渲染 Specter 专属涂装"""
    
    if model_style == "reaper":
        # 死神收割·灵魂收集者 - 死神镰刀、灵魂火焰、收割特效、亡魂哀嚎
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：死神斗篷轮廓
        cloak_points = [
            (60, 30), (70, 45), (68, 65), (60, 70),
            (52, 65), (50, 45)
        ]
        pygame.draw.polygon(s, (30, 0, 50), cloak_points)
        pygame.draw.polygon(s, (100, 0, 150), cloak_points, 2)
        
        # 死神头部（骷髅）
        pygame.draw.circle(s, (200, 200, 200), (60, 35), 6)
        # 空洞眼眶（发红光）
        for eye_x in [57, 63]:
            pygame.draw.circle(s, (255, 0, 0), (eye_x, 34), 2)
            eye_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(eye_glow, (255, 0, 0, 150), (eye_x, 34), 4)
            s.blit(eye_glow, (0, 0))
        
        # 死神镰刀（大镰刀）
        scythe_angle = math.sin(t * 2) * 0.3
        # 镰刀柄
        handle_x = 75 + math.cos(scythe_angle) * 5
        handle_y = 50 + math.sin(scythe_angle) * 5
        pygame.draw.line(s, (100, 100, 100), (60, 45), (int(handle_x), int(handle_y)), 3)
        # 镰刀刃（弧形）
        blade_points = [
            (handle_x, handle_y),
            (handle_x + 15 * math.cos(scythe_angle + 0.5), handle_y + 15 * math.sin(scythe_angle + 0.5)),
            (handle_x + 12 * math.cos(scythe_angle + 1.5), handle_y + 12 * math.sin(scythe_angle + 1.5)),
            (handle_x + 5 * math.cos(scythe_angle + 2), handle_y + 5 * math.sin(scythe_angle + 2))
        ]
        pygame.draw.polygon(s, (200, 200, 200), [(int(p[0]), int(p[1])) for p in blade_points])
        pygame.draw.polygon(s, (255, 255, 255), [(int(p[0]), int(p[1])) for p in blade_points], 2)
        
        # 灵魂火焰飘荡（绿色鬼火）
        for i in range(10):
            flame_angle = t * 2 + i * math.pi / 5
            flame_dist = 25 + 10 * math.sin(t * 1.5 + i)
            flame_x = 60 + math.cos(flame_angle) * flame_dist
            flame_y = 50 + math.sin(flame_angle) * flame_dist
            flame_height = 8 + 4 * math.sin(t * 4 + i)
            # 鬼火形状
            fire_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(fire_surface, (100, 255, 100, 200), [
                (int(flame_x), int(flame_y)),
                (int(flame_x - 3), int(flame_y + flame_height)),
                (int(flame_x + 3), int(flame_y + flame_height))
            ])
            s.blit(fire_surface, (0, 0))
        
        # 收割特效（灵魂轨迹）
        soul_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            soul_offset = (t * 30 + i * 15) % 50
            soul_x = 60 + soul_offset - 25
            soul_y = 45 + int(5 * math.sin(t * 3 + i))
            # 小灵魂
            pygame.draw.circle(soul_surface, (180, 255, 180, 200 - int(soul_offset * 4)), (int(soul_x), int(soul_y)), 4)
        s.blit(soul_surface, (0, 0))
        
        # 亡魂哀嚎（声波圈）
        for i in range(3):
            wail_radius = (t * 40 + i * 20) % 60
            wail_alpha = int(150 * (1 - wail_radius / 60))
            wail_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wail_surface, (100, 0, 150, wail_alpha), (60, 50), int(wail_radius), 2)
            s.blit(wail_surface, (0, 0))
        
        return s
    
    elif model_style == "assassin":
        # 幽灵刺客·无声夺命 - 刺客形态、无声接近、致命一击
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.15 + 1
        
        # 主体：刺客身影（半透明）
        body_alpha = int(150 + 50 * math.sin(t * 2))  # 闪烁隐身
        body_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 身体轮廓
        body_points = [(60, 35), (68, 50), (64, 65), (60, 68), (56, 65), (52, 50)]
        pygame.draw.polygon(body_surface, (50, 50, 80, body_alpha), body_points)
        pygame.draw.polygon(body_surface, (100, 100, 150, body_alpha), body_points, 2)
        s.blit(body_surface, (0, 0))
        
        # 刺客兜帽
        hood_points = [(60, 30), (65, 38), (55, 38)]
        pygame.draw.polygon(s, (30, 30, 50), hood_points)
        
        # 隐身残影（多个半透明分身）
        for i in range(3):
            shadow_offset = 8 * (i + 1)
            shadow_alpha = int(100 - i * 30)
            shadow_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            shadow_points = [(p[0] - shadow_offset, p[1]) for p in body_points]
            pygame.draw.polygon(shadow_surface, (50, 50, 80, shadow_alpha), shadow_points)
            s.blit(shadow_surface, (0, 0))
        
        # 双刀（刺客武器）
        knife_angle = math.sin(t * 3) * 0.3
        # 左手刀
        left_knife_x = 52 + math.cos(knife_angle) * 8
        left_knife_y = 55 + math.sin(knife_angle) * 8
        pygame.draw.line(s, (150, 150, 200), (52, 55), (int(left_knife_x), int(left_knife_y)), 3)
        pygame.draw.polygon(s, (200, 200, 255), [
            (int(left_knife_x), int(left_knife_y)),
            (int(left_knife_x + 5 * math.cos(knife_angle)), int(left_knife_y + 5 * math.sin(knife_angle))),
            (int(left_knife_x + 3 * math.cos(knife_angle + 0.5)), int(left_knife_y + 3 * math.sin(knife_angle + 0.5)))
        ])
        # 右手刀
        right_knife_x = 68 + math.cos(-knife_angle) * 8
        right_knife_y = 55 + math.sin(-knife_angle) * 8
        pygame.draw.line(s, (150, 150, 200), (68, 55), (int(right_knife_x), int(right_knife_y)), 3)
        pygame.draw.polygon(s, (200, 200, 255), [
            (int(right_knife_x), int(right_knife_y)),
            (int(right_knife_x + 5 * math.cos(-knife_angle)), int(right_knife_y + 5 * math.sin(-knife_angle))),
            (int(right_knife_x + 3 * math.cos(-knife_angle - 0.5)), int(right_knife_y + 3 * math.sin(-knife_angle - 0.5)))
        ])
        
        # 致命一击标记（红色叉）
        if int(t * 4) % 3 == 0:
            mark_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(mark_surface, (255, 0, 0, 200), (52, 42), (68, 58), 3)
            pygame.draw.line(mark_surface, (255, 0, 0, 200), (68, 42), (52, 58), 3)
            s.blit(mark_surface, (0, 0))
        
        # 无声移动粒子（黑雾）
        fog_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            fog_x = 60 + int(15 * math.cos(t * 2 + i * math.pi / 4))
            fog_y = 50 + int(15 * math.sin(t * 2 + i * math.pi / 4))
            pygame.draw.circle(fog_surface, (30, 30, 50, 100), (fog_x, fog_y), 6)
        s.blit(fog_surface, (0, 0))
        
        return s
    
    elif model_style == "wraith":
        # 幽灵怨灵·冤魂缠绕 - 半透明幽灵、怨灵面孔、灵魂锁链、冤魂飘荡
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：幽灵飘荡形态（半透明波动布料）
        ghost_points = []
        for i in range(10):
            angle = i * math.pi / 5 + math.pi / 2
            dist = 20 + 5 * math.sin(t * 3 + i * 0.5)
            gx = 60 + math.cos(angle) * dist
            gy = 40 + math.sin(angle) * dist + i * 3
            ghost_points.append((gx, gy))
        ghost_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(len(ghost_points) - 1):
            pygame.draw.line(ghost_surface, (150, 255, 255, 180), (int(ghost_points[i][0]), int(ghost_points[i][1])), 
                           (int(ghost_points[i+1][0]), int(ghost_points[i+1][1])), 12)
        s.blit(ghost_surface, (0, 0))
        
        # 怨灵面孔浮现（扭曲的脸）
        face_alpha = int(200 + 55 * math.sin(t * 2.5))
        face_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 脸部轮廓
        pygame.draw.circle(face_surface, (200, 255, 255, face_alpha), (60, 45), 12)
        # 空洞眼睛
        pygame.draw.circle(face_surface, (0, 0, 0, face_alpha), (55, 43), 3)
        pygame.draw.circle(face_surface, (0, 0, 0, face_alpha), (65, 43), 3)
        # 痛苦的嘴（O形）
        pygame.draw.circle(face_surface, (0, 0, 0, face_alpha), (60, 50), 4)
        s.blit(face_surface, (0, 0))
        
        # 灵魂锁链束缚（环绕锁链）
        chain_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            chain_angle = t * 2 + i * math.pi / 10
            chain_dist = 25 + 5 * math.sin(i * 0.5)
            chain_x = 60 + math.cos(chain_angle) * chain_dist
            chain_y = 50 + math.sin(chain_angle) * chain_dist
            # 锁链环节
            pygame.draw.circle(chain_surface, (180, 220, 220, 200), (int(chain_x), int(chain_y)), 2)
            if i > 0:
                prev_angle = t * 2 + (i - 1) * math.pi / 10
                prev_x = 60 + math.cos(prev_angle) * (25 + 5 * math.sin((i - 1) * 0.5))
                prev_y = 50 + math.sin(prev_angle) * (25 + 5 * math.sin((i - 1) * 0.5))
                pygame.draw.line(chain_surface, (180, 220, 220, 150), (int(prev_x), int(prev_y)), (int(chain_x), int(chain_y)), 1)
        s.blit(chain_surface, (0, 0))
        
        # 冤魂飘荡（小幽灵）
        for i in range(5):
            soul_angle = t * 1.5 + i * 2 * math.pi / 5
            soul_dist = 30 + 10 * math.sin(t * 2 + i)
            soul_x = 60 + math.cos(soul_angle) * soul_dist
            soul_y = 50 + math.sin(soul_angle) * soul_dist
            # 小幽灵轮廓
            soul_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(soul_surface, (180, 255, 255, 180), (int(soul_x), int(soul_y)), 5)
            # 哀伤表情
            pygame.draw.circle(soul_surface, (100, 200, 200, 180), (int(soul_x) - 2, int(soul_y) - 1), 1)
            pygame.draw.circle(soul_surface, (100, 200, 200, 180), (int(soul_x) + 2, int(soul_y) - 1), 1)
            s.blit(soul_surface, (0, 0))
        
        return s
    
    elif model_style == "sniper":
        # 幽灵狙击·远程收割 - 狙击手形态、精准射击、灵魂狙击、激光瞄准
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.15 + 1
        
        # 主体：狙击手轮廓
        pygame.draw.rect(s, (0, 100, 200), (52, 42, 16, 22))
        pygame.draw.rect(s, (100, 200, 255), (52, 42, 16, 22), 2)
        
        # 狙击枪（长枪管）
        rifle_angle = math.sin(t * 2) * 0.2
        rifle_length = 30
        rifle_end_x = 60 + math.cos(rifle_angle) * rifle_length
        rifle_end_y = 50 + math.sin(rifle_angle) * rifle_length
        # 枪身
        pygame.draw.line(s, (80, 80, 100), (60, 50), (int(rifle_end_x), int(rifle_end_y)), 4)
        # 瞄准镜
        scope_x = 60 + math.cos(rifle_angle) * 10
        scope_y = 50 + math.sin(rifle_angle) * 10
        pygame.draw.circle(s, (50, 150, 255), (int(scope_x), int(scope_y)), 5)
        pygame.draw.circle(s, (100, 200, 255), (int(scope_x), int(scope_y)), 5, 2)
        
        # 激光瞄准线（红色激光）
        laser_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        laser_extended_x = rifle_end_x + math.cos(rifle_angle) * 50
        laser_extended_y = rifle_end_y + math.sin(rifle_angle) * 50
        pygame.draw.line(laser_surface, (255, 0, 0, 200), (int(rifle_end_x), int(rifle_end_y)), 
                        (int(laser_extended_x), int(laser_extended_y)), 1)
        # 激光点（闪烁）
        if int(t * 8) % 2 == 0:
            pygame.draw.circle(laser_surface, (255, 0, 0, 250), (int(laser_extended_x), int(laser_extended_y)), 3)
        s.blit(laser_surface, (0, 0))
        
        # 瞄准准星（十字线）
        target_x, target_y = int(laser_extended_x), int(laser_extended_y)
        crosshair_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(crosshair_surface, (255, 100, 100, 200), (target_x - 8, target_y), (target_x + 8, target_y), 1)
        pygame.draw.line(crosshair_surface, (255, 100, 100, 200), (target_x, target_y - 8), (target_x, target_y + 8), 1)
        pygame.draw.circle(crosshair_surface, (255, 100, 100, 200), (target_x, target_y), 6, 1)
        s.blit(crosshair_surface, (0, 0))
        
        # 灵魂狙击特效（能量波动）
        for i in range(3):
            energy_dist = 15 + i * 8 + (t * 20) % 15
            energy_x = 60 + math.cos(rifle_angle) * energy_dist
            energy_y = 50 + math.sin(rifle_angle) * energy_dist
            energy_alpha = int(200 * (1 - ((t * 20) % 15) / 15))
            energy_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(energy_surface, (50, 150, 255, energy_alpha), (int(energy_x), int(energy_y)), 4)
            s.blit(energy_surface, (0, 0))
        
        # 幽灵迷彩（半透明粒子）
        camo_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            camo_x = 60 + int(10 * math.cos(t * 2 + i))
            camo_y = 50 + int(10 * math.sin(t * 2 + i))
            pygame.draw.circle(camo_surface, (50, 180, 255, 100), (camo_x, camo_y), 4)
        s.blit(camo_surface, (0, 0))
        
        return s
    
    elif model_style == "poltergeist":
        # 骚灵现象·灵异事件 - 物体悬浮飞舞、灵异力量、超自然现象
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：骚灵能量核心（不可见实体）
        core_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(core_glow, (200, 100, 255, 180), (60, 50), int(15 * pulse))
        pygame.draw.circle(core_glow, (255, 150, 255, 120), (60, 50), int(20 * pulse))
        s.blit(core_glow, (0, 0))
        
        # 悬浮飞舞物体（多个物品旋转）
        objects = [
            # 书本
            lambda x, y: pygame.draw.rect(s, (150, 100, 50), (int(x) - 5, int(y) - 3, 10, 6)),
            # 椅子
            lambda x, y: pygame.draw.polygon(s, (100, 50, 0), [(int(x), int(y) - 5), (int(x) - 4, int(y) + 3), (int(x) + 4, int(y) + 3)]),
            # 灯具
            lambda x, y: pygame.draw.circle(s, (255, 255, 100), (int(x), int(y)), 4),
            # 花瓶
            lambda x, y: pygame.draw.polygon(s, (100, 200, 150), [(int(x), int(y) - 4), (int(x) - 3, int(y) + 4), (int(x) + 3, int(y) + 4)]),
        ]
        
        for i in range(8):
            obj_angle = t * 3 + i * math.pi / 4
            obj_dist = 25 + 10 * math.sin(t * 2 + i)
            obj_x = 60 + math.cos(obj_angle) * obj_dist
            obj_y = 50 + math.sin(obj_angle) * obj_dist + 5 * math.sin(t * 4 + i)  # 上下浮动
            # 绘制物体
            obj_func = objects[i % len(objects)]
            obj_func(obj_x, obj_y)
            # 物体旋转轨迹
            trail_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(trail_surface, (200, 100, 255, 100), (60, 50), (int(obj_x), int(obj_y)), 1)
            s.blit(trail_surface, (0, 0))
        
        # 灵异力量波动（能量圈）
        for i in range(3):
            wave_radius = 20 + i * 10 + (t * 30) % 20
            wave_alpha = int(180 * (1 - ((t * 30) % 20) / 20))
            wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, (220, 120, 255, wave_alpha), (60, 50), int(wave_radius), 2)
            s.blit(wave_surface, (0, 0))
        
        # 超自然现象（扭曲空间）
        distortion_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            dist_angle = i * math.pi / 6
            dist_inner = 10
            dist_outer = 18 + 5 * math.sin(t * 3 + i)
            inner_x = 60 + math.cos(dist_angle) * dist_inner
            inner_y = 50 + math.sin(dist_angle) * dist_inner
            outer_x = 60 + math.cos(dist_angle) * dist_outer
            outer_y = 50 + math.sin(dist_angle) * dist_outer
            pygame.draw.line(distortion_surface, (200, 100, 255, 150), (int(inner_x), int(inner_y)), (int(outer_x), int(outer_y)), 2)
        s.blit(distortion_surface, (0, 0))
        
        return s
    
    elif model_style == "fallen_angel":
        # 死亡天使·黑色羽翼 - 天使降临、黑色羽翼、天使审判、灵魂引渡
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.12 + 1
        
        # 主体：天使人形
        pygame.draw.ellipse(s, (30, 30, 50), (54, 38, 12, 28))
        pygame.draw.circle(s, (50, 50, 80), (60, 35), 5)  # 头部
        
        # 黑色羽翼展开（暗黑天使）
        wing_colors = [(20, 20, 40), (30, 30, 50), (50, 50, 80)]
        for side in [-1, 1]:
            for i in range(7):
                wing_angle = side * (math.pi / 4 + i * math.pi / 18) + math.sin(t * 1.5 + i) * 0.15
                wing_length = 28 + i * 2
                wing_x = 60 + math.cos(wing_angle) * wing_length
                wing_y = 50 + math.sin(wing_angle) * wing_length
                # 羽毛层次
                for layer in range(3):
                    feather_offset = layer * 2
                    fx = 60 + math.cos(wing_angle) * (wing_length - feather_offset)
                    fy = 50 + math.sin(wing_angle) * (wing_length - feather_offset)
                    color = wing_colors[layer]
                    pygame.draw.line(s, color, (60, 50), (int(fx), int(fy)), 4 - layer)
                    # 暗光效果
                    if layer == 0:
                        glow = pygame.Surface((120, 120), pygame.SRCALPHA)
                        pygame.draw.line(glow, (100, 100, 180, 100), (60, 50), (int(fx), int(fy)), 6)
                        s.blit(glow, (0, 0))
        
        # 天使审判光环（暗紫色）
        halo_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(halo_surface, (100, 50, 150, 200), (60, 30), int(8 * pulse))
        pygame.draw.circle(halo_surface, (150, 100, 200, 150), (60, 30), int(10 * pulse), 2)
        s.blit(halo_surface, (0, 0))
        
        # 灵魂引渡（上升的灵魂）
        for i in range(6):
            soul_y = 70 - (t * 25 + i * 12) % 50
            soul_x = 60 + int(5 * math.sin(t * 3 + i))
            soul_alpha = int(200 * ((t * 25 + i * 12) % 50) / 50)
            soul_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 灵魂形状（小人形）
            pygame.draw.circle(soul_surface, (200, 200, 255, soul_alpha), (int(soul_x), int(soul_y)), 3)
            pygame.draw.line(soul_surface, (200, 200, 255, soul_alpha), (int(soul_x), int(soul_y) + 3), (int(soul_x), int(soul_y) + 8), 2)
            s.blit(soul_surface, (0, 0))
        
        # 审判之剑（光剑）
        sword_angle = math.sin(t * 2) * 0.3
        sword_x = 70 + math.cos(sword_angle) * 20
        sword_y = 55 + math.sin(sword_angle) * 20
        pygame.draw.line(s, (200, 200, 255), (60, 50), (int(sword_x), int(sword_y)), 3)
        # 剑刃发光
        sword_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(sword_glow, (200, 200, 255, 150), (60, 50), (int(sword_x), int(sword_y)), 6)
        s.blit(sword_glow, (0, 0))
        
        # 黑色羽毛飘落
        for i in range(10):
            feather_x = 40 + (t * 20 + i * 8) % 40
            feather_y = 30 + ((t * 30 + i * 6) % 50)
            pygame.draw.line(s, (30, 30, 50), (int(feather_x), int(feather_y)), (int(feather_x + 2), int(feather_y + 4)), 2)
        
        return s
    
    elif model_style == "void_hunter":
        # 虚空猎手·维度收割 - 跨维度狩猎、虚空镰刀、维度裂缝、收割一切
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：虚空猎手形态（扭曲的黑影）
        hunter_points = [
            (60, 30), (70, 45), (68, 60), (60, 68),
            (52, 60), (50, 45)
        ]
        # 虚空扭曲效果
        distorted_points = []
        for i, (x, y) in enumerate(hunter_points):
            distort_x = x + int(3 * math.sin(t * 4 + i))
            distort_y = y + int(3 * math.cos(t * 4 + i))
            distorted_points.append((distort_x, distort_y))
        pygame.draw.polygon(s, (50, 0, 80), distorted_points)
        pygame.draw.polygon(s, (100, 20, 150), distorted_points, 2)
        
        # 虚空镰刀（巨大紫色镰刀）
        scythe_angle = t * 1.5
        scythe_length = 35
        scythe_x = 60 + math.cos(scythe_angle) * scythe_length
        scythe_y = 50 + math.sin(scythe_angle) * scythe_length
        # 镰刀柄（虚空能量）
        for i in range(5):
            segment_ratio = i / 4
            seg_x = 60 + (scythe_x - 60) * segment_ratio
            seg_y = 50 + (scythe_y - 50) * segment_ratio
            pygame.draw.circle(s, (100, 20, 150), (int(seg_x), int(seg_y)), 2)
        pygame.draw.line(s, (80, 0, 120), (60, 50), (int(scythe_x), int(scythe_y)), 4)
        # 镰刀刃（弧形虚空刃）
        blade_points = [
            (scythe_x, scythe_y),
            (scythe_x + 18 * math.cos(scythe_angle + 1), scythe_y + 18 * math.sin(scythe_angle + 1)),
            (scythe_x + 15 * math.cos(scythe_angle + 2), scythe_y + 15 * math.sin(scythe_angle + 2)),
        ]
        pygame.draw.polygon(s, (150, 50, 180), [(int(p[0]), int(p[1])) for p in blade_points])
        blade_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(blade_glow, (180, 100, 220, 180), [(int(p[0]), int(p[1])) for p in blade_points])
        s.blit(blade_glow, (0, 0))
        
        # 维度裂缝（空间撕裂）
        for i in range(4):
            crack_angle = i * math.pi / 2 + t * 0.5
            crack_length = 20 + 10 * math.sin(t * 2 + i)
            crack_x = 60 + math.cos(crack_angle) * crack_length
            crack_y = 50 + math.sin(crack_angle) * crack_length
            # 裂缝线
            crack_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(crack_surface, (100, 0, 150, 220), (60, 50), (int(crack_x), int(crack_y)), 3)
            # 裂缝边缘发光
            pygame.draw.line(crack_surface, (180, 80, 220, 150), (60, 50), (int(crack_x), int(crack_y)), 5)
            s.blit(crack_surface, (0, 0))
            # 裂缝末端虚空能量
            pygame.draw.circle(s, (150, 50, 180), (int(crack_x), int(crack_y)), 5)
        
        # 跨维度粒子（虚空粒子飞散）
        for i in range(20):
            particle_angle = t * 3 + i * math.pi / 10
            particle_dist = 20 + 20 * (i / 20) + 8 * math.sin(t * 2 + i)
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            # 虚空粒子（方块）
            particle_size = 2 + int(2 * math.sin(t * 4 + i))
            pygame.draw.rect(s, (100, 20, 150), (int(px) - particle_size//2, int(py) - particle_size//2, particle_size, particle_size))
            # 粒子能量尾迹
            tail_x = px - math.cos(particle_angle) * 5
            tail_y = py - math.sin(particle_angle) * 5
            particle_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(particle_glow, (150, 50, 180, 150), (int(px), int(py)), (int(tail_x), int(tail_y)), 1)
            s.blit(particle_glow, (0, 0))
        
        # 虚空能量场（外圈脉冲）
        for i in range(3):
            void_radius = 25 + i * 10 + int(8 * pulse)
            void_alpha = int(150 * (1 - i / 3))
            void_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(void_surface, (100, 20, 150, void_alpha), (60, 50), void_radius, 2)
            s.blit(void_surface, (0, 0))
        
        return s

    elif model_style == "specter_ex":
        # 幽冥镰刀 - 巨型镰刀，挥砍动画
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 镰刀摆动角度
        swing_angle = math.sin(t * 2) * 0.6
        
        # 镰刀柄
        handle_start = (60, 70)
        handle_end = (60 + int(30 * math.sin(swing_angle)), 30 + int(10 * math.cos(swing_angle)))
        pygame.draw.line(s, (100, 100, 100), handle_start, handle_end, 6)
        
        # 镰刀刃（弧形）
        blade_center = handle_end
        blade_curve = []
        for i in range(10):
            curve_angle = swing_angle - math.pi / 2 + i * 0.2
            curve_dist = 25 + i * 2
            bx = blade_center[0] + int(math.cos(curve_angle) * curve_dist)
            by = blade_center[1] + int(math.sin(curve_angle) * curve_dist)
            blade_curve.append((bx, by))
        
        pygame.draw.lines(s, (200, 200, 255), False, blade_curve, 8)
        
        # 幽冥气息
        for i in range(12):
            ghost_angle = t * 2 + i * math.pi / 6
            ghost_dist = 30 + 10 * math.sin(t * 3 + i)
            gx = 60 + math.cos(ghost_angle) * ghost_dist
            gy = 50 + math.sin(ghost_angle) * ghost_dist
            pygame.draw.circle(s, (150, 150, 255, 180), (int(gx), int(gy)), 4)
        
        return s
    
    elif model_style == "specter_ex2":
        # 暗影刺客 - 双刀交叉，分身闪烁
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 刺客身影（模糊轮廓）
        for layer in range(3):
            offset = layer * 5
            alpha = 150 - layer * 40
            shadow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 头部
            pygame.draw.circle(shadow_surf, (50, 50, 100, alpha), (60 + offset, 35), 8)
            # 身体
            body_points = [(60 + offset, 43), (55 + offset, 60), (50 + offset, 75), (60 + offset, 70), (70 + offset, 75), (65 + offset, 60)]
            pygame.draw.polygon(shadow_surf, (50, 50, 100, alpha), body_points)
            s.blit(shadow_surf, (0, 0))
        
        # 双刀交叉
        blade_angle1 = math.pi / 4 + math.sin(t * 3) * 0.3
        blade_angle2 = -math.pi / 4 - math.sin(t * 3) * 0.3
        for blade_angle in [blade_angle1, blade_angle2]:
            blade_start_x = 60
            blade_start_y = 50
            blade_end_x = 60 + math.cos(blade_angle) * 35
            blade_end_y = 50 + math.sin(blade_angle) * 35
            pygame.draw.line(s, (100, 100, 150), (blade_start_x, blade_start_y), 
                           (int(blade_end_x), int(blade_end_y)), 4)
            pygame.draw.line(s, (150, 150, 200), (blade_start_x, blade_start_y),
                           (int(blade_end_x), int(blade_end_y)), 2)
        
        # 手里剑飞旋
        for i in range(4):
            shuriken_angle = t * 5 + i * math.pi / 2
            shuriken_dist = 30 + 10 * math.sin(t * 2 + i)
            sx = 60 + math.cos(shuriken_angle) * shuriken_dist
            sy = 50 + math.sin(shuriken_angle) * shuriken_dist
            # 四角星形
            star_points = []
            for j in range(8):
                star_angle = shuriken_angle + j * math.pi / 4
                star_radius = 5 if j % 2 == 0 else 3
                star_points.append((int(sx + math.cos(star_angle) * star_radius),
                                  int(sy + math.sin(star_angle) * star_radius)))
            pygame.draw.polygon(s, (80, 80, 130), star_points)
        
        return s
    
    elif model_style == "specter_ex3":
        # 量子幽灵 - 叠加态，多位置存在
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 量子叠加（同时在多个位置）
        superposition_count = 8
        for pos in range(superposition_count):
            # 概率幅度（位置的可能性）
            amplitude = 0.3 + 0.7 * ((math.sin(t * 3 + pos) + 1) / 2)
            alpha = int(200 * amplitude)
            
            # 位置偏移
            offset_angle = pos * 2 * math.pi / superposition_count
            offset_dist = 15 * math.sin(t * 2 + pos)
            pos_x = 60 + math.cos(offset_angle) * offset_dist
            pos_y = 50 + math.sin(offset_angle) * offset_dist
            
            # 绘制幽灵形态
            ghost_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 头部
            pygame.draw.circle(ghost_surf, (100, 255, 255, alpha), (int(pos_x), int(pos_y - 10)), 8)
            # 身体（飘渺状）
            body_points = [
                (pos_x, pos_y - 2),
                (pos_x - 8, pos_y + 10),
                (pos_x - 6, pos_y + 18),
                (pos_x + 6, pos_y + 18),
                (pos_x + 8, pos_y + 10)
            ]
            pygame.draw.polygon(ghost_surf, (100, 255, 255, alpha),
                              [(int(p[0]), int(p[1])) for p in body_points])
            s.blit(ghost_surf, (0, 0))
        
        # 量子纠缠线（连接不同位置）
        entangle_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(superposition_count):
            for j in range(i + 1, superposition_count):
                if random.random() < 0.4:
                    angle_i = i * 2 * math.pi / superposition_count
                    offset_i = 15 * math.sin(t * 2 + i)
                    pos_xi = 60 + math.cos(angle_i) * offset_i
                    pos_yi = 50 + math.sin(angle_i) * offset_i
                    
                    angle_j = j * 2 * math.pi / superposition_count
                    offset_j = 15 * math.sin(t * 2 + j)
                    pos_xj = 60 + math.cos(angle_j) * offset_j
                    pos_yj = 50 + math.sin(angle_j) * offset_j
                    
                    pygame.draw.line(entangle_surf, (150, 255, 255, 120),
                                   (int(pos_xi), int(pos_yi)), (int(pos_xj), int(pos_yj)), 1)
        s.blit(entangle_surf, (0, 0))
        
        # 波函数（概率密度云）
        for cloud_particle in range(40):
            cloud_angle = cloud_particle * 0.5
            cloud_dist = 10 + 35 * random.random()
            cloud_x = 60 + math.cos(cloud_angle) * cloud_dist
            cloud_y = 50 + math.sin(cloud_angle) * cloud_dist
            cloud_probability = 1 - (cloud_dist - 10) / 35
            cloud_alpha = int(180 * cloud_probability)
            cloud_size = 2 + int(3 * cloud_probability)
            if cloud_alpha > 30:
                pygame.draw.circle(s, (120, 255, 255, cloud_alpha),
                                 (int(cloud_x), int(cloud_y)), cloud_size)
        
        # 观测者效应（当被观测时坍缩）
        collapse_progress = (math.sin(t * 1.5) + 1) / 2
        if collapse_progress > 0.7:  # 观测发生
            # 坍缩到中心位置
            collapse_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            collapse_intensity = int(255 * ((collapse_progress - 0.7) / 0.3))
            for ring in range(5):
                ring_radius = 45 - ring * 8 - int(collapse_progress * 10)
                ring_alpha = int(200 * (1 - ring / 5))
                pygame.draw.circle(collapse_surf, (100, 255, 255, ring_alpha),
                                 (60, 50), ring_radius, 2)
            s.blit(collapse_surf, (0, 0))
        
        # 量子涨落粒子
        for fluctuation in range(15):
            if (int(t * 20) + fluctuation) % 10 < 5:
                fluc_angle = fluctuation * 0.8
                fluc_dist = 20 + 25 * random.random()
                fluc_x = 60 + math.cos(fluc_angle) * fluc_dist
                fluc_y = 50 + math.sin(fluc_angle) * fluc_dist
                pygame.draw.circle(s, (200, 255, 255), (int(fluc_x), int(fluc_y)), 2)
        
        return s
    
    elif model_style == "specter_ex4":
        # 全息投影 - 数据流动
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 扫描线效果
        scan_lines = 15
        for scan in range(scan_lines):
            scan_y = int((t * 80 + scan * 8) % 120)
            scan_alpha = int(150 * (math.sin(t * 3 + scan) + 1) / 2)
            
            if scan_alpha > 30:
                scan_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(scan_surf, (0, 255, 255, scan_alpha),
                               (10, scan_y), (110, scan_y), 1)
                s.blit(scan_surf, (0, 0))
        
        # 数据流粒子（二进制）
        data_particles = 50
        for dp in range(data_particles):
            dp_x = 20 + (dp % 10) * 10
            dp_progress = (t * 2 + dp * 0.1) % 1
            dp_y = 10 + dp_progress * 100
            dp_alpha = int(200 * (1 - abs(dp_progress - 0.5) * 2))
            
            if dp_alpha > 30:
                # 二进制位（0或1）
                dp_value = (int(t * 10) + dp) % 2
                dp_color = (0, 255, 255) if dp_value == 1 else (255, 0, 255)
                pygame.draw.circle(s, (*dp_color, dp_alpha), (dp_x, int(dp_y)), 2)
        
        # 全息网格（三维投影）
        grid_layers = 4
        for layer in range(grid_layers):
            layer_depth = layer / grid_layers
            layer_scale = 0.5 + layer_depth * 0.5
            layer_offset_y = int(layer * 5 * math.sin(t + layer))
            layer_alpha = int(120 + 80 * layer_depth)
            
            # 网格线
            grid_size = 4
            for gx in range(grid_size + 1):
                # 垂直线
                x_pos = int(30 + gx * 15 * layer_scale)
                y_start = int(30 + layer_offset_y)
                y_end = int(70 + layer_offset_y)
                
                grid_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(grid_surf, (100, 200, 255, layer_alpha),
                               (x_pos, y_start), (x_pos, y_end), 1)
                s.blit(grid_surf, (0, 0))
            
            for gy in range(grid_size + 1):
                # 水平线
                y_pos = int(30 + gy * 10 * layer_scale + layer_offset_y)
                x_start = int(30)
                x_end = int(30 + grid_size * 15 * layer_scale)
                
                grid_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(grid_surf, (100, 200, 255, layer_alpha),
                               (x_start, y_pos), (x_end, y_pos), 1)
                s.blit(grid_surf, (0, 0))
        
        # 像素化重构效果
        pixel_blocks = 12
        for block in range(pixel_blocks):
            # 随机出现的像素块
            if (int(t * 5) + block) % 8 < 5:
                block_angle = block * 0.5
                block_dist = 20 + (block % 4) * 8
                block_x = int(60 + math.cos(block_angle) * block_dist)
                block_y = int(50 + math.sin(block_angle) * block_dist)
                block_size = 6
                
                # 青色和品红交替
                block_color = (0, 255, 255) if block % 2 == 0 else (255, 0, 255)
                block_alpha = int(180 * ((math.sin(t * 4 + block) + 1) / 2))
                
                if block_alpha > 30:
                    block_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    block_rect = pygame.Rect(block_x - block_size // 2,
                                            block_y - block_size // 2,
                                            block_size, block_size)
                    pygame.draw.rect(block_surf, (*block_color, block_alpha), block_rect)
                    pygame.draw.rect(block_surf, (255, 255, 255, block_alpha), block_rect, 1)
                    s.blit(block_surf, (0, 0))
        
        # 中心全息核心
        holo_core_radius = int(15 + 5 * math.sin(t * 2.5))
        for holo_ring in range(3):
            ring_radius = holo_core_radius + holo_ring * 8
            ring_alpha = int(150 - holo_ring * 40)
            holo_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 青蓝色
            pygame.draw.circle(holo_surf, (0, 200, 255, ring_alpha), (60, 50), ring_radius, 2)
            s.blit(holo_surf, (0, 0))
        
        # 数据流螺旋
        data_stream_points = []
        for stream_step in range(20):
            stream_prog = stream_step / 20
            stream_angle = stream_prog * math.pi * 6 + t * 3
            stream_radius = 10 + stream_prog * 35
            stream_x = 60 + math.cos(stream_angle) * stream_radius
            stream_y = 50 + math.sin(stream_angle) * stream_radius
            data_stream_points.append((int(stream_x), int(stream_y)))
        
        # 绘制数据流
        for i in range(len(data_stream_points) - 1):
            stream_alpha = int(180 * (1 - i / len(data_stream_points)))
            if stream_alpha > 30:
                stream_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                stream_color = (0, 255, 255) if i % 2 == 0 else (255, 0, 255)
                pygame.draw.line(stream_surf, (*stream_color, stream_alpha),
                               data_stream_points[i], data_stream_points[i + 1], 2)
                s.blit(stream_surf, (0, 0))
        
        return s
    
    elif model_style == "specter_ex5":
        # 故障艺术·系统崩溃
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        glitch_intensity = abs(math.sin(t * 3))
        
        # RGB通道分离
        offset = int(glitch_intensity * 8)
        for i in range(3):
            shift_x = offset * (i - 1)
            shift_y = offset * (2 - i) if i % 2 else -offset
            
            for j in range(8):
                block_angle = t + j * 0.785
                block_radius = 20 + j * 3
                bx = center[0] + math.cos(block_angle) * block_radius + shift_x
                by = center[1] + math.sin(block_angle) * block_radius + shift_y
                
                if i == 0:
                    color = (255, 0, 0)
                elif i == 1:
                    color = (0, 255, 0)
                else:
                    color = (0, 0, 255)
                
                pygame.draw.rect(s, color, (bx - 4, by - 4, 8, 8))
        
        # 画面撕裂线
        if glitch_intensity > 0.7:
            for i in range(5):
                tear_y = center[1] - 20 + i * 10
                tear_offset = int(glitch_intensity * 15 * math.sin(t * 10 + i))
                pygame.draw.line(s, (255, 255, 255), 
                               (center[0] - 30 + tear_offset, tear_y), 
                               (center[0] + 30 + tear_offset, tear_y), 2)
        
        # 数字乱码粒子
        for i in range(20):
            noise_x = center[0] + (hash((i, int(t * 10))) % 60) - 30
            noise_y = center[1] + (hash((i + 100, int(t * 10))) % 60) - 30
            noise_color = (255, 255, 255) if hash((i, int(t * 5))) % 2 else (0, 0, 0)
            pygame.draw.rect(s, noise_color, (noise_x, noise_y, 2, 2))
        
        return s

    return None


# Specter 涂装列表
SPECTER_STYLES = [
    "reaper", "assassin", "wraith", "sniper",
    "poltergeist", "fallen_angel", "void_hunter",
    "specter_ex", "specter_ex2", "specter_ex3", "specter_ex4", "specter_ex5"
]


def is_specter_style(model_style):
    """检查是否是 Specter 专属涂装"""
    return model_style in SPECTER_STYLES
