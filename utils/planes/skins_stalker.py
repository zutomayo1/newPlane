# Stalker 专属涂装渲染模块
# 包含: predator, alien, chameleon, insect, drone, void, xenomorph

import pygame
import math

# Stalker涂装列表
STALKER_STYLES = ["predator", "alien", "chameleon", "insect", "drone", "void", "xenomorph", "stalker_ex", "stalker_ex2", "stalker_ex3", "stalker_ex4", "stalker_ex5"]

def is_stalker_style(model_style):
    """检查是否为Stalker涂装"""
    return model_style in STALKER_STYLES

def render_stalker_skin(s, c, model_style, t, pid, static=False):
    """渲染Stalker涂装，返回Surface或None"""
    
    if model_style == "predator":
        # 铁血战士·热能追踪 - 铁血战士形态、热能视觉、等离子炮、狩猎荣耀
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：铁血战士装甲
        armor_points = [(60, 32), (70, 46), (68, 60), (60, 66), (52, 60), (50, 46)]
        pygame.draw.polygon(s, (80, 0, 120), armor_points)
        pygame.draw.polygon(s, (150, 80, 180), armor_points, 3)
        
        # 铁血战士面罩（标志性）
        mask_points = [(60, 35), (65, 42), (60, 45), (55, 42)]
        pygame.draw.polygon(s, (120, 60, 140), mask_points)
        pygame.draw.polygon(s, (180, 100, 200), mask_points, 2)
        # 面罩发光眼睛（红色）
        for eye_x in [57, 63]:
            pygame.draw.circle(s, (255, 0, 0), (eye_x, 40), 2)
            eye_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(eye_glow, (255, 0, 0, 200), (eye_x, 40), 4)
            s.blit(eye_glow, (0, 0))
        
        # 热能视觉追踪（热成像扫描线）
        thermal_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        scan_y = int(30 + (t * 40) % 50)
        # 扫描线
        pygame.draw.line(thermal_surface, (255, 100, 0, 220), (30, scan_y), (90, scan_y), 2)
        # 热能区域
        for i in range(8):
            heat_x = 40 + i * 8
            heat_y = scan_y + int(5 * math.sin(t * 5 + i))
            pygame.draw.circle(thermal_surface, (255, 150, 0, 150), (heat_x, heat_y), 4)
        s.blit(thermal_surface, (0, 0))
        
        # 等离子炮（肩部武器）
        cannon_angle = math.sin(t * 2) * 0.3
        cannon_x = 72 + math.cos(cannon_angle) * 8
        cannon_y = 45 + math.sin(cannon_angle) * 8
        # 炮管
        pygame.draw.line(s, (100, 100, 150), (72, 45), (int(cannon_x), int(cannon_y)), 4)
        # 炮口
        pygame.draw.circle(s, (150, 150, 255), (int(cannon_x), int(cannon_y)), 4)
        # 等离子充能
        if int(t * 4) % 3 == 0:
            plasma_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(plasma_glow, (150, 150, 255, 220), (int(cannon_x), int(cannon_y)), int(8 * pulse))
            s.blit(plasma_glow, (0, 0))
        
        # 狩猎荣耀标记（战利品符文）
        rune_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            rune_angle = t + i * math.pi / 3
            rune_x = 60 + math.cos(rune_angle) * 22
            rune_y = 50 + math.sin(rune_angle) * 22
            # 铁血符文（三角）
            if (int(t * 5) + i) % 3 == 0:
                rune_points = [
                    (rune_x, rune_y - 3),
                    (rune_x + 3, rune_y + 2),
                    (rune_x - 3, rune_y + 2)
                ]
                pygame.draw.polygon(rune_surface, (180, 100, 200, 200), [(int(p[0]), int(p[1])) for p in rune_points])
        s.blit(rune_surface, (0, 0))
        
        # 隐形装置（半透明效果）
        cloak_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            cloak_x = 60 + int(8 * math.cos(t * 2 + i))
            cloak_y = 50 + int(8 * math.sin(t * 2 + i))
            pygame.draw.circle(cloak_surface, (100, 150, 200, 80), (cloak_x, cloak_y), 6)
        s.blit(cloak_surface, (0, 0))
        
        return s
    
    elif model_style == "alien":
        # 异形猎手·完美生物 - 异形形态、酸性血液、致命猎杀
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：异形躯体（有机曲线）
        alien_points = [(60, 30), (72, 45), (68, 62), (60, 68), (52, 62), (48, 45)]
        pygame.draw.polygon(s, (40, 80, 20), alien_points)
        pygame.draw.polygon(s, (80, 150, 50), alien_points, 2)
        
        # 异形头部（长型）
        head_points = [(60, 25), (65, 30), (63, 38), (57, 38), (55, 30)]
        pygame.draw.polygon(s, (30, 70, 10), head_points)
        pygame.draw.polygon(s, (70, 140, 30), head_points, 2)
        
        # 异形内颚（经典双颚）
        if int(t * 4) % 3 == 0:
            inner_jaw_y = 38 + int(5 * math.sin(t * 6))
            pygame.draw.circle(s, (200, 200, 200), (60, inner_jaw_y), 3)
            pygame.draw.line(s, (200, 200, 200), (60, 38), (60, inner_jaw_y), 2)
        
        # 异形尾部（带刺）
        tail_segments = []
        for i in range(8):
            tail_angle = math.pi / 2 + math.sin(t * 3 + i * 0.5) * 0.3
            tail_dist = 10 + i * 4
            tail_x = 60 + math.cos(tail_angle) * tail_dist
            tail_y = 68 + math.sin(tail_angle) * tail_dist
            tail_segments.append((tail_x, tail_y))
        for i in range(len(tail_segments) - 1):
            pygame.draw.line(s, (50, 100, 30), (int(tail_segments[i][0]), int(tail_segments[i][1])), 
                           (int(tail_segments[i+1][0]), int(tail_segments[i+1][1])), 5)
        # 尾部尖刺
        if tail_segments:
            tip_x, tip_y = tail_segments[-1]
            pygame.draw.polygon(s, (80, 150, 50), [
                (int(tip_x), int(tip_y)),
                (int(tip_x - 4), int(tip_y + 6)),
                (int(tip_x + 4), int(tip_y + 6))
            ])
        
        # 酸性血液（绿色液滴）
        acid_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            acid_angle = t * 2 + i * math.pi / 4
            acid_dist = 25 + 8 * math.sin(t * 3 + i)
            acid_x = 60 + math.cos(acid_angle) * acid_dist
            acid_y = 50 + math.sin(acid_angle) * acid_dist
            # 酸液滴
            pygame.draw.circle(acid_surface, (100, 255, 50, 220), (int(acid_x), int(acid_y)), 3)
            # 酸液腐蚀效果
            pygame.draw.circle(acid_surface, (150, 255, 100, 150), (int(acid_x), int(acid_y)), 5)
        s.blit(acid_surface, (0, 0))
        
        # 完美生物进化纹理（有机纹路）
        texture_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            texture_y = 35 + i * 4
            texture_offset = int(3 * math.sin(t * 3 + i))
            pygame.draw.line(texture_surface, (70, 140, 30, 180), (50 + texture_offset, texture_y), (70 + texture_offset, texture_y), 2)
        s.blit(texture_surface, (0, 0))
        
        # 致命猎杀姿态（攻击爪）
        for side in [-1, 1]:
            claw_x = 60 + side * 15
            claw_y = 55 + int(5 * math.sin(t * 3))
            # 爪子
            for i in range(3):
                claw_tip_x = claw_x + side * (3 + i * 2)
                claw_tip_y = claw_y + 8 + i * 2
                pygame.draw.line(s, (80, 150, 50), (claw_x, claw_y), (claw_tip_x, claw_tip_y), 2)
        
        return s
    
    elif model_style == "chameleon":
        # 变色龙·完美伪装 - 色彩变幻、环境融入、伪装隐身
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：变色龙身体（颜色变化）
        hue_shift = int(t * 100) % 360
        color_r = int(127 + 127 * math.sin(math.radians(hue_shift)))
        color_g = int(127 + 127 * math.sin(math.radians(hue_shift + 120)))
        color_b = int(127 + 127 * math.sin(math.radians(hue_shift + 240)))
        
        body_points = [(60, 35), (68, 48), (65, 62), (60, 66), (55, 62), (52, 48)]
        chameleon_alpha = int(180 + 75 * math.sin(t * 2.5))  # 透明度变化
        body_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(body_surface, (color_r, color_g, color_b, chameleon_alpha), body_points)
        pygame.draw.polygon(body_surface, (color_r + 50, color_g + 50, color_b + 50, chameleon_alpha), body_points, 2)
        s.blit(body_surface, (0, 0))
        
        # 变色龙眼睛（独立转动）
        for side, eye_rotation in [(-1, t * 2), (1, -t * 2)]:
            eye_x = 60 + side * 6
            eye_y = 42
            # 眼球底座
            pygame.draw.circle(s, (color_r, color_g, color_b), (eye_x, eye_y), 5)
            # 瞳孔（独立转动）
            pupil_x = eye_x + int(2 * math.cos(eye_rotation))
            pupil_y = eye_y + int(2 * math.sin(eye_rotation))
            pygame.draw.circle(s, (0, 0, 0), (pupil_x, pupil_y), 2)
        
        # 色彩变幻波纹（皮肤纹理）
        pattern_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(15):
            pattern_angle = t * 3 + i * math.pi / 7.5
            pattern_dist = 18 + 8 * math.sin(t * 2 + i)
            pattern_x = 60 + math.cos(pattern_angle) * pattern_dist
            pattern_y = 50 + math.sin(pattern_angle) * pattern_dist
            # 色斑
            spot_hue = (hue_shift + i * 24) % 360
            spot_r = int(127 + 127 * math.sin(math.radians(spot_hue)))
            spot_g = int(127 + 127 * math.sin(math.radians(spot_hue + 120)))
            spot_b = int(127 + 127 * math.sin(math.radians(spot_hue + 240)))
            pygame.draw.circle(pattern_surface, (spot_r, spot_g, spot_b, 180), (int(pattern_x), int(pattern_y)), 4)
        s.blit(pattern_surface, (0, 0))
        
        # 环境融入效果（背景纹理模拟）
        blend_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            blend_x = 45 + (i % 4) * 10
            blend_y = 40 + (i // 4) * 15
            blend_alpha = int(100 + 100 * math.sin(t * 3 + i))
            pygame.draw.rect(blend_surface, (color_r, color_g, color_b, blend_alpha), (blend_x, blend_y, 8, 8))
        s.blit(blend_surface, (0, 0))
        
        # 伪装隐身（轮廓扭曲）
        distortion_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            dist_angle = i * math.pi / 3
            dist_x = 60 + math.cos(dist_angle) * 25
            dist_y = 50 + math.sin(dist_angle) * 25
            pygame.draw.circle(distortion_surface, (color_r, color_g, color_b, 100), (int(dist_x), int(dist_y)), 6)
        s.blit(distortion_surface, (0, 0))
        
        return s
    
    elif model_style == "insect":
        # 虫群潜行·复眼侦测 - 虫群形态、复眼、潜行猎杀、群体智慧
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：昆虫身躯（分节）
        segments = [
            (60, 40, 12, 8),   # 头部
            (60, 50, 14, 10),  # 胸部
            (60, 62, 12, 8),   # 腹部
        ]
        for seg_x, seg_y, seg_w, seg_h in segments:
            pygame.draw.ellipse(s, (0, 80, 40), (seg_x - seg_w//2, seg_y - seg_h//2, seg_w, seg_h))
            pygame.draw.ellipse(s, (50, 130, 80), (seg_x - seg_w//2, seg_y - seg_h//2, seg_w, seg_h), 2)
        
        # 复眼全方位侦测（多个小眼）
        compound_eye_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for side in [-1, 1]:
            eye_base_x = 60 + side * 5
            eye_base_y = 38
            # 复眼构造（蜂窝状）
            for row in range(3):
                for col in range(3):
                    eye_x = eye_base_x + side * col * 2
                    eye_y = eye_base_y + row * 2
                    # 小眼单元
                    pygame.draw.circle(compound_eye_surface, (100, 255, 100, 220), (eye_x, eye_y), 1)
        s.blit(compound_eye_surface, (0, 0))
        
        # 昆虫触角（感知器官）
        for side in [-1, 1]:
            antenna_segments = []
            for i in range(6):
                antenna_angle = side * (math.pi / 3) + i * 0.2 + math.sin(t * 3 + i) * 0.2
                antenna_dist = 8 + i * 3
                antenna_x = 60 + math.cos(antenna_angle) * antenna_dist
                antenna_y = 35 + math.sin(antenna_angle) * antenna_dist
                antenna_segments.append((antenna_x, antenna_y))
            for i in range(len(antenna_segments) - 1):
                pygame.draw.line(s, (50, 130, 80), (int(antenna_segments[i][0]), int(antenna_segments[i][1])), 
                               (int(antenna_segments[i+1][0]), int(antenna_segments[i+1][1])), 2)
        
        # 昆虫腿部（6条腿）
        for i in range(6):
            leg_side = -1 if i < 3 else 1
            leg_segment = i % 3
            leg_base_x = 60 + leg_side * 7
            leg_base_y = 45 + leg_segment * 8
            leg_angle = leg_side * (math.pi / 3) + math.sin(t * 4 + i) * 0.4
            leg_length = 15
            leg_x = leg_base_x + math.cos(leg_angle) * leg_length
            leg_y = leg_base_y + math.sin(leg_angle) * leg_length
            pygame.draw.line(s, (50, 130, 80), (leg_base_x, leg_base_y), (int(leg_x), int(leg_y)), 2)
            # 腿部关节
            joint_x = leg_base_x + math.cos(leg_angle) * leg_length * 0.6
            joint_y = leg_base_y + math.sin(leg_angle) * leg_length * 0.6
            pygame.draw.circle(s, (20, 100, 50), (int(joint_x), int(joint_y)), 2)
        
        # 虫群粒子（小虫环绕）
        swarm_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            swarm_angle = t * 4 + i * math.pi / 10
            swarm_dist = 28 + 12 * (i / 20) + 5 * math.sin(t * 3 + i)
            swarm_x = 60 + math.cos(swarm_angle) * swarm_dist
            swarm_y = 50 + math.sin(swarm_angle) * swarm_dist
            # 小虫（点）
            pygame.draw.circle(swarm_surface, (20, 120, 70, 200), (int(swarm_x), int(swarm_y)), 2)
        s.blit(swarm_surface, (0, 0))
        
        # 群体智慧连接线（信息网络）
        network_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            if i < 4:
                continue
            angle1 = t * 2 + i * math.pi / 4
            angle2 = t * 2 + (i - 4) * math.pi / 4
            x1 = 60 + math.cos(angle1) * 20
            y1 = 50 + math.sin(angle1) * 20
            x2 = 60 + math.cos(angle2) * 20
            y2 = 50 + math.sin(angle2) * 20
            pygame.draw.line(network_surface, (50, 150, 100, 100), (int(x1), int(y1)), (int(x2), int(y2)), 1)
        s.blit(network_surface, (0, 0))
        
        return s
    
    elif model_style == "drone":
        # 无人机群·天罗地网 - 无人机部署、监控网络、智能追踪
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：中心控制无人机
        pygame.draw.circle(s, (180, 130, 0), (60, 50), 10)
        pygame.draw.circle(s, (220, 180, 20), (60, 50), 10, 2)
        # 中心摄像头
        pygame.draw.circle(s, (255, 200, 50), (60, 50), 5)
        pygame.draw.circle(s, (0, 0, 0), (60, 50), 3)
        
        # 螺旋桨（4个）
        prop_angles = [0, math.pi / 2, math.pi, 3 * math.pi / 2]
        for prop_angle in prop_angles:
            prop_x = 60 + math.cos(prop_angle) * 15
            prop_y = 50 + math.sin(prop_angle) * 15
            # 螺旋桨臂
            pygame.draw.line(s, (150, 120, 0), (60, 50), (int(prop_x), int(prop_y)), 3)
            # 螺旋桨旋转
            blade_angle = t * 10 + prop_angle
            for blade in range(2):
                blade_offset = blade * math.pi
                blade_x1 = prop_x + math.cos(blade_angle + blade_offset) * 6
                blade_y1 = prop_y + math.sin(blade_angle + blade_offset) * 6
                blade_x2 = prop_x + math.cos(blade_angle + blade_offset + math.pi) * 6
                blade_y2 = prop_y + math.sin(blade_angle + blade_offset + math.pi) * 6
                pygame.draw.line(s, (200, 150, 0), (int(blade_x1), int(blade_y1)), (int(blade_x2), int(blade_y2)), 2)
        
        # 子无人机群（8个小无人机）
        for i in range(8):
            drone_angle = t * 2 + i * math.pi / 4
            drone_dist = 30 + 8 * math.sin(t * 1.5 + i)
            drone_x = 60 + math.cos(drone_angle) * drone_dist
            drone_y = 50 + math.sin(drone_angle) * drone_dist
            # 小无人机
            pygame.draw.circle(s, (200, 150, 0), (int(drone_x), int(drone_y)), 4)
            pygame.draw.circle(s, (255, 200, 50), (int(drone_x), int(drone_y)), 2)
        
        # 天罗地网监控连接线
        network_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            drone_angle = t * 2 + i * math.pi / 4
            drone_dist = 30 + 8 * math.sin(t * 1.5 + i)
            drone_x = 60 + math.cos(drone_angle) * drone_dist
            drone_y = 50 + math.sin(drone_angle) * drone_dist
            # 连接到中心
            pygame.draw.line(network_surface, (255, 200, 50, 150), (60, 50), (int(drone_x), int(drone_y)), 1)
            # 相邻连接
            next_i = (i + 1) % 8
            next_angle = t * 2 + next_i * math.pi / 4
            next_dist = 30 + 8 * math.sin(t * 1.5 + next_i)
            next_x = 60 + math.cos(next_angle) * next_dist
            next_y = 50 + math.sin(next_angle) * next_dist
            pygame.draw.line(network_surface, (255, 200, 50, 100), (int(drone_x), int(drone_y)), (int(next_x), int(next_y)), 1)
        s.blit(network_surface, (0, 0))
        
        # 智能追踪扫描（雷达波）
        for i in range(3):
            scan_radius = (t * 50 + i * 25) % 75
            scan_alpha = int(200 * (1 - scan_radius / 75))
            scan_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(scan_surface, (220, 180, 20, scan_alpha), (60, 50), int(scan_radius), 2)
            s.blit(scan_surface, (0, 0))
        
        # 数据传输粒子
        data_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            data_angle = t * 3 + i * math.pi / 6
            data_dist = 15 + ((t * 30 + i * 6) % 25)
            data_x = 60 + math.cos(data_angle) * data_dist
            data_y = 50 + math.sin(data_angle) * data_dist
            pygame.draw.circle(data_surface, (255, 200, 50, 220), (int(data_x), int(data_y)), 2)
        s.blit(data_surface, (0, 0))
        
        return s
    
    elif model_style == "void":
        # 虚空潜伏·无形存在 - 虚空隐匿、存在感抹除、维度穿梭、虚无形态
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.2 + 1
        
        # 主体：虚无形态（几乎透明）
        void_alpha = int(120 + 80 * math.sin(t * 2.5))
        void_points = [(60, 35), (68, 48), (64, 62), (60, 68), (56, 62), (52, 48)]
        void_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(void_surface, (80, 0, 120, void_alpha), void_points)
        pygame.draw.polygon(void_surface, (150, 50, 180, void_alpha + 50), void_points, 2)
        s.blit(void_surface, (0, 0))
        
        # 维度缝隙穿梭（空间裂缝）
        for i in range(5):
            crack_angle = t * 1.5 + i * 2 * math.pi / 5
            crack_length = 20 + 10 * math.sin(t * 2 + i)
            crack_x = 60 + math.cos(crack_angle) * crack_length
            crack_y = 50 + math.sin(crack_angle) * crack_length
            crack_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 裂缝线
            pygame.draw.line(crack_surface, (100, 20, 150, 220), (60, 50), (int(crack_x), int(crack_y)), 3)
            # 裂缝边缘光
            pygame.draw.line(crack_surface, (180, 80, 220, 150), (60, 50), (int(crack_x), int(crack_y)), 5)
            s.blit(crack_surface, (0, 0))
        
        # 存在感抹除（扭曲波纹）
        distortion_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(4):
            distort_radius = 20 + i * 8 + (t * 25) % 20
            distort_alpha = int(150 * (1 - ((t * 25) % 20) / 20))
            pygame.draw.circle(distortion_surface, (100, 20, 150, distort_alpha), (60, 50), int(distort_radius), 2)
        s.blit(distortion_surface, (0, 0))
        
        # 虚空粒子（消失粒子）
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            particle_angle = t * 3 + i * math.pi / 10
            particle_dist = 20 + 20 * (i / 20)
            particle_alpha = int(220 - (i / 20) * 150)
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            pygame.draw.circle(particle_surface, (100, 20, 150, particle_alpha), (int(px), int(py)), 2)
        s.blit(particle_surface, (0, 0))
        
        # 虚空眼睛（唯一可见）
        if (int(t * 3) % 5) < 2:
            eye_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(eye_glow, (150, 50, 180, 250), (60, 45), int(6 * pulse))
            pygame.draw.circle(eye_glow, (100, 20, 150, 200), (60, 45), 4)
            s.blit(eye_glow, (0, 0))
        
        # 虚无能量场
        for i in range(3):
            void_radius = 25 + i * 10 + int(8 * pulse)
            void_alpha_ring = int(100 * (1 - i / 3))
            void_ring = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(void_ring, (100, 20, 150, void_alpha_ring), (60, 50), void_radius, 2)
            s.blit(void_ring, (0, 0))
        
        return s
    
    elif model_style == "xenomorph":
        # 异形皇后·终极猎食 - 异形皇后、完美进化、生物链顶端
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：异形皇后巨大躯体
        queen_body = [(60, 28), (75, 48), (70, 65), (60, 72), (50, 65), (45, 48)]
        pygame.draw.polygon(s, (20, 60, 20), queen_body)
        pygame.draw.polygon(s, (80, 120, 80), queen_body, 3)
        
        # 皇后冠状头部
        crown_points = [
            (60, 20),  # 顶峰
            (65, 25), (70, 22),  # 右侧尖刺
            (55, 25), (50, 22),  # 左侧尖刺
        ]
        for i in range(0, len(crown_points) - 1, 2):
            if i + 1 < len(crown_points):
                pygame.draw.line(s, (100, 150, 100), (60, 28), crown_points[i], 3)
                pygame.draw.circle(s, (80, 120, 80), crown_points[i], 3)
        
        # 皇后巨大内颚
        jaw_extension = int(8 * math.sin(t * 3))
        jaw_y = 42 + jaw_extension
        pygame.draw.circle(s, (180, 180, 180), (60, jaw_y), 4)
        pygame.draw.line(s, (180, 180, 180), (60, 38), (60, jaw_y), 3)
        # 内颚尖端
        pygame.draw.circle(s, (200, 200, 200), (60, jaw_y), 2)
        
        # 多节装甲尾部（更长更强）
        tail_segments_queen = []
        for i in range(12):
            tail_angle = math.pi / 2 + math.sin(t * 2 + i * 0.3) * 0.4
            tail_dist = 12 + i * 4
            tail_x = 60 + math.cos(tail_angle) * tail_dist
            tail_y = 72 + math.sin(tail_angle) * tail_dist
            tail_segments_queen.append((tail_x, tail_y))
        for i in range(len(tail_segments_queen) - 1):
            tail_width = 8 - int(i * 0.5)
            pygame.draw.line(s, (40, 90, 40), (int(tail_segments_queen[i][0]), int(tail_segments_queen[i][1])), 
                           (int(tail_segments_queen[i+1][0]), int(tail_segments_queen[i+1][1])), tail_width)
        # 尾部巨刺
        if tail_segments_queen:
            tip_x, tip_y = tail_segments_queen[-1]
            pygame.draw.polygon(s, (100, 150, 100), [
                (int(tip_x), int(tip_y)),
                (int(tip_x - 6), int(tip_y + 10)),
                (int(tip_x + 6), int(tip_y + 10))
            ])
        
        # 皇后背部尖刺（4对）
        for i in range(4):
            spike_x = 60
            spike_y = 35 + i * 8
            for side in [-1, 1]:
                spike_end_x = spike_x + side * (8 + i * 2)
                spike_end_y = spike_y - 5
                pygame.draw.line(s, (80, 120, 80), (spike_x, spike_y), (spike_end_x, spike_end_y), 3)
                pygame.draw.circle(s, (100, 150, 100), (spike_end_x, spike_end_y), 2)
        
        # 完美进化生物质（有机纹理）
        bio_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            bio_angle = t * 2 + i * math.pi / 10
            bio_dist = 20 + 15 * (i / 20)
            bio_x = 60 + math.cos(bio_angle) * bio_dist
            bio_y = 50 + math.sin(bio_angle) * bio_dist
            # 生物质节点
            pygame.draw.circle(bio_surface, (50, 120, 50, 200), (int(bio_x), int(bio_y)), 3)
        s.blit(bio_surface, (0, 0))
        
        # 酸液喷射（皇后能力）
        acid_spray = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            if (int(t * 6) + i) % 4 < 2:
                spray_angle = math.pi / 2 + (i - 6) * math.pi / 24
                spray_dist = 25 + (t * 30 + i * 5) % 30
                spray_x = 60 + math.cos(spray_angle) * spray_dist
                spray_y = 42 + math.sin(spray_angle) * spray_dist
                pygame.draw.circle(acid_spray, (150, 255, 100, 220), (int(spray_x), int(spray_y)), 3)
        s.blit(acid_spray, (0, 0))
        
        # 生物链顶端威压（能量场）
        for i in range(3):
            dominance_radius = 30 + i * 12 + int(10 * pulse)
            dominance_alpha = int(150 * (1 - i / 3))
            dominance_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(dominance_surface, (50, 120, 50, dominance_alpha), (60, 50), dominance_radius, 3)
            s.blit(dominance_surface, (0, 0))
        
        return s
    
    elif model_style == "stalker_ex":
        # 异界猎手 - 昆虫节肢结构，复眼闪光
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体（昆虫头胸）
        pygame.draw.ellipse(s, (80, 0, 120), (40, 35, 40, 30))
        pygame.draw.ellipse(s, (120, 0, 180), (40, 35, 40, 30), 3)
        
        # 复眼（闪烁）
        for eye_x in [50, 70]:
            eye_brightness = int(155 + 100 * math.sin(t * 5))
            pygame.draw.circle(s, (eye_brightness, 0, eye_brightness), (eye_x, 45), 6)
        
        # 6条节肢（3对）
        for pair in range(3):
            for side in [-1, 1]:
                leg_base_y = 40 + pair * 8
                leg_angle = side * (math.pi / 3 + pair * 0.2) + math.sin(t * 3 + pair) * 0.2
                
                # 节肢分段
                segments = []
                for seg in range(4):
                    seg_dist = 15 + seg * 8
                    seg_x = 60 + side * math.cos(leg_angle) * seg_dist
                    seg_y = leg_base_y + math.sin(leg_angle) * seg_dist * 0.5
                    segments.append((int(seg_x), int(seg_y)))
                
                # 绘制节肢
                for seg in range(len(segments) - 1):
                    pygame.draw.line(s, (100, 0, 150), segments[seg], segments[seg+1], 4)
        
        # 触须
        for side in [-1, 1]:
            antenna = []
            for i in range(5):
                ant_x = 60 + side * (5 + i * 3)
                ant_y = 35 - i * 4 + math.sin(t * 4 + side) * 3
                antenna.append((int(ant_x), int(ant_y)))
            pygame.draw.lines(s, (150, 0, 200), False, antenna, 2)
        
        return s
    
    elif model_style == "stalker_ex2":
        # 机械蜘蛛 - 8条机械腿，纳米虫群
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 蜘蛛主体（机械球体）
        pygame.draw.circle(s, (150, 150, 150), (60, 50), int(15 * pulse))
        pygame.draw.circle(s, (200, 200, 200), (60, 50), int(15 * pulse), 2)
        
        # 电子复眼（多个镜头）
        for eye_idx in range(6):
            eye_angle = eye_idx * math.pi / 3
            eye_x = 60 + math.cos(eye_angle) * 8
            eye_y = 50 + math.sin(eye_angle) * 8
            eye_brightness = int(155 + 100 * math.sin(t * 8 + eye_idx))
            pygame.draw.circle(s, (eye_brightness, 0, 0), (int(eye_x), int(eye_y)), 3)
        
        # 8条机械腿
        for leg_idx in range(8):
            leg_angle = leg_idx * math.pi / 4
            # 腿部关节动画
            leg_bend = math.sin(t * 4 + leg_idx) * 0.3
            
            # 第一节
            joint1_x = 60 + math.cos(leg_angle) * 18
            joint1_y = 50 + math.sin(leg_angle) * 18
            pygame.draw.line(s, (180, 180, 180), (60, 50), (int(joint1_x), int(joint1_y)), 4)
            
            # 第二节
            joint2_angle = leg_angle + leg_bend
            joint2_x = joint1_x + math.cos(joint2_angle) * 15
            joint2_y = joint1_y + math.sin(joint2_angle) * 15
            pygame.draw.line(s, (160, 160, 160), (int(joint1_x), int(joint1_y)), 
                           (int(joint2_x), int(joint2_y)), 3)
            
            # 第三节（末端）
            joint3_angle = joint2_angle - leg_bend * 0.5
            joint3_x = joint2_x + math.cos(joint3_angle) * 10
            joint3_y = joint2_y + math.sin(joint3_angle) * 10
            pygame.draw.line(s, (140, 140, 140), (int(joint2_x), int(joint2_y)),
                           (int(joint3_x), int(joint3_y)), 2)
        
        # 纳米虫群（小型飞行机器人）
        for nano_idx in range(20):
            nano_angle = t * 3 + nano_idx * 0.3
            nano_dist = 30 + 15 * math.sin(t * 2 + nano_idx)
            nx = 60 + math.cos(nano_angle) * nano_dist
            ny = 50 + math.sin(nano_angle) * nano_dist
            pygame.draw.rect(s, (220, 220, 220), (int(nx)-2, int(ny)-2, 4, 4))
        
        return s
    
    elif model_style == "stalker_ex3":
        # 纳米风暴 - 灰雾吞噬
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 纳米机器人云（密集小粒子）
        nano_particle_count = 80
        for nano in range(nano_particle_count):
            # 螺旋运动
            nano_angle = t * 3 + nano * 0.2
            nano_spiral_radius = 10 + (nano % 30)
            nano_height = math.sin(t * 2 + nano * 0.1) * 15
            nano_x = 60 + math.cos(nano_angle) * nano_spiral_radius
            nano_y = 50 + nano_height + (nano % 5) * 3 - 10
            
            # 纳米粒子大小和颜色变化
            nano_size = 1 + int((nano % 3))
            nano_brightness = 100 + int(155 * ((math.sin(t * 4 + nano) + 1) / 2))
            nano_alpha = 150 + int(100 * ((nano_spiral_radius - 10) / 30))
            
            pygame.draw.circle(s, (nano_brightness, nano_brightness, nano_brightness, nano_alpha),
                             (int(nano_x), int(nano_y)), nano_size)
        
        # 吞噬波纹（向内收缩）
        for devour_wave in range(5):
            wave_progress = (t * 2 + devour_wave * 0.4) % 1
            # 从外向内
            wave_radius = int(50 * (1 - wave_progress))
            wave_alpha = int(200 * wave_progress)
            
            if wave_radius > 5:
                devour_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(devour_surf, (80, 80, 80, wave_alpha),
                                 (60, 50), wave_radius, 2)
                s.blit(devour_surf, (0, 0))
        
        # 灰雾触手（从中心延伸）
        tentacle_count = 8
        for tentacle in range(tentacle_count):
            tentacle_angle = tentacle * 2 * math.pi / tentacle_count + t * 0.5
            tentacle_length = 35 + 10 * math.sin(t * 2 + tentacle)
            
            # 触手由多段组成
            tentacle_segments = 8
            tentacle_points = [(60, 50)]
            
            for seg in range(1, tentacle_segments + 1):
                seg_progress = seg / tentacle_segments
                seg_dist = tentacle_length * seg_progress
                # 触手摆动
                seg_offset = math.sin(t * 3 + seg * 0.5) * 8 * seg_progress
                seg_angle = tentacle_angle + seg_offset * 0.1
                
                seg_x = 60 + math.cos(seg_angle) * seg_dist
                seg_y = 50 + math.sin(seg_angle) * seg_dist
                tentacle_points.append((int(seg_x), int(seg_y)))
            
            # 绘制触手
            if len(tentacle_points) > 1:
                tentacle_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                for i in range(len(tentacle_points) - 1):
                    segment_alpha = int(180 * (1 - i / len(tentacle_points)))
                    segment_width = int(5 * (1 - i / len(tentacle_points))) + 1
                    pygame.draw.line(tentacle_surf, (100, 100, 100, segment_alpha),
                                   tentacle_points[i], tentacle_points[i + 1], segment_width)
                s.blit(tentacle_surf, (0, 0))
        
        # 被吞噬的碎片（向中心飞）
        for debris in range(15):
            debris_progress = (t * 2.5 + debris * 0.3) % 1
            debris_angle = debris * 0.8
            # 从外向内
            debris_dist = 50 * (1 - debris_progress)
            debris_x = 60 + math.cos(debris_angle) * debris_dist
            debris_y = 50 + math.sin(debris_angle) * debris_dist
            debris_alpha = int(255 * (1 - debris_progress))
            debris_size = 3 + int(3 * (1 - debris_progress))
            
            if debris_alpha > 30 and debris_dist > 5:
                debris_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                # 碎片形状（小方块）
                debris_rect = pygame.Rect(int(debris_x - debris_size / 2),
                                        int(debris_y - debris_size / 2),
                                        debris_size, debris_size)
                pygame.draw.rect(debris_surf, (150, 150, 150, debris_alpha), debris_rect)
                s.blit(debris_surf, (0, 0))
        
        # 中心吞噬核心
        core_pulse_radius = int(8 + 4 * pulse)
        for core_layer in range(4, 0, -1):
            layer_radius = int(core_pulse_radius * (core_layer / 4))
            layer_alpha = int(200 * (core_layer / 4))
            core_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(core_surf, (50, 50, 50, layer_alpha),
                             (60, 50), layer_radius)
            s.blit(core_surf, (0, 0))
        
        return s
    
    elif model_style == "stalker_ex4":
        # 迷幻漩涡 - 催眠螺旋
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 多层旋转螺旋
        spiral_layers = 6
        for layer in range(spiral_layers):
            layer_rotation = t * (1 + layer * 0.3)
            layer_radius_start = 5 + layer * 8
            
            # 螺旋线
            spiral_points = []
            segments = 30
            for seg in range(segments):
                seg_prog = seg / segments
                seg_angle = layer_rotation + seg_prog * math.pi * 6
                seg_radius = layer_radius_start + seg_prog * 30
                sx = 60 + int(math.cos(seg_angle) * seg_radius)
                sy = 50 + int(math.sin(seg_angle) * seg_radius)
                spiral_points.append((sx, sy))
            
            # 颜色渐变（紫色到青色）
            for i in range(len(spiral_points) - 1):
                color_prog = i / len(spiral_points)
                r = int(255 * (1 - color_prog))
                g = int(100 + 155 * color_prog)
                b = 255
                alpha = int(180 - layer * 25)
                
                if alpha > 30:
                    spiral_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(spiral_surf, (r, g, b, alpha),
                                   spiral_points[i], spiral_points[i + 1], 3)
                    s.blit(spiral_surf, (0, 0))
        
        # 催眠环
        ring_count = 8
        for ring in range(ring_count):
            ring_progress = (t + ring * 0.2) % 1
            ring_radius = int(10 + ring_progress * 45)
            ring_alpha = int(200 * (1 - ring_progress))
            
            if ring_alpha > 30:
                ring_hue = (ring / ring_count + t * 0.3) % 1
                if ring_hue < 0.5:
                    ring_color = (255, int(255 * ring_hue * 2), 255)
                else:
                    ring_color = (int(255 * (1 - (ring_hue - 0.5) * 2)), 255, 255)
                
                ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(ring_surf, (*ring_color, ring_alpha), (60, 50), ring_radius, 2)
                s.blit(ring_surf, (0, 0))
        
        return s
    
    elif model_style == "stalker_ex5":
        # 时钟齿轮·蒸汽朋克
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 50)
        
        # 大齿轮
        for gear_idx in range(3):
            gear_radius = 35 - gear_idx * 10
            gear_rotation = t * (1 + gear_idx * 0.5) * (-1 if gear_idx % 2 else 1)
            teeth_count = 12 - gear_idx * 2
            
            gear_color = (180 + gear_idx * 20, 140 + gear_idx * 20, 100 + gear_idx * 10)
            pygame.draw.circle(s, gear_color, center, gear_radius, 2)
            
            # 齿轮齿
            for i in range(teeth_count):
                tooth_angle = gear_rotation + (i / teeth_count) * 2 * math.pi
                inner_x = center[0] + math.cos(tooth_angle) * (gear_radius - 3)
                inner_y = center[1] + math.sin(tooth_angle) * (gear_radius - 3)
                outer_x = center[0] + math.cos(tooth_angle) * (gear_radius + 3)
                outer_y = center[1] + math.sin(tooth_angle) * (gear_radius + 3)
                pygame.draw.line(s, gear_color, (inner_x, inner_y), (outer_x, outer_y), 2)
        
        # 钟表指针
        for hand_idx in range(3):
            hand_length = 25 - hand_idx * 7
            hand_speed = 1 + hand_idx * 2
            hand_angle = t * hand_speed - 1.571
            hand_x = center[0] + math.cos(hand_angle) * hand_length
            hand_y = center[1] + math.sin(hand_angle) * hand_length
            hand_color = (220, 180, 120)
            pygame.draw.line(s, hand_color, center, (hand_x, hand_y), 3 - hand_idx)
        
        # 蒸汽粒子
        for i in range(15):
            steam_phase = (t + i * 0.2) % 1.5
            steam_x = center[0] + math.sin(t + i) * 20
            steam_y = center[1] + 30 - steam_phase * 40
            steam_size = int(3 + steam_phase * 4)
            steam_color = (200, 200, 200)
            pygame.draw.circle(s, steam_color, (int(steam_x), int(steam_y)), steam_size, 1)
        
        return s
    
    return None
