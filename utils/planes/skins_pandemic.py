# Pandemic 专属涂装渲染模块
# 包含: pandemic_plague, pandemic_biohazard, pandemic_fungal, pandemic_neon_virus,
#       pandemic_zombie, pandemic_parasite, pandemic_radiation, pandemic_coral,
#       pandemic_prion, pandemic_alien, pandemic_chimera, pandemic_omega

import pygame
import math
import random

# Pandemic涂装列表
PANDEMIC_STYLES = [
    "pandemic_plague", "pandemic_biohazard", "pandemic_fungal", "pandemic_neon_virus",
    "pandemic_zombie", "pandemic_parasite", "pandemic_radiation", "pandemic_coral",
    "pandemic_prion", "pandemic_alien", "pandemic_chimera", "pandemic_omega"
]

def is_pandemic_style(model_style):
    """检查是否为Pandemic涂装"""
    return model_style in PANDEMIC_STYLES

def render_pandemic_skin(s, c, model_style, t, pid, static=False):
    """渲染Pandemic涂装，返回Surface或None"""
    pulse = math.sin(t * 2) * 0.15 + 1
    
    if model_style == "pandemic_plague":
        # 黑死病·乌鸦医生 - 中世纪瘟疫医生，鸟嘴面具
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 黑暗雾气背景
        for fog in range(15):
            fog_x = random.randint(10, 110)
            fog_y = random.randint(10, 110)
            fog_alpha = random.randint(30, 80)
            fog_size = random.randint(10, 25)
            pygame.draw.circle(s, (30, 30, 35, fog_alpha), (fog_x, fog_y), fog_size)
        # 瘟疫医生剪影
        # 宽檐帽
        hat_points = [(30, 35), (60, 20), (90, 35), (85, 40), (35, 40)]
        pygame.draw.polygon(s, (20, 20, 25), hat_points)
        # 鸟嘴面具
        beak_sway = math.sin(t * 2) * 2
        pygame.draw.ellipse(s, (40, 35, 30), (45, 38, 30, 25))  # 头部
        # 长鸟嘴
        beak_points = [(75, 48), (105 + int(beak_sway), 55), (75, 58)]
        pygame.draw.polygon(s, (50, 45, 40), beak_points)
        # 圆形眼镜（红色反光）
        eye_glow = int(150 + 80 * math.sin(t * 4))
        pygame.draw.circle(s, (30, 25, 25), (52, 45), 7)
        pygame.draw.circle(s, (eye_glow, 30, 30), (52, 45), 5)
        pygame.draw.circle(s, (30, 25, 25), (66, 45), 7)
        pygame.draw.circle(s, (eye_glow, 30, 30), (66, 45), 5)
        # 长袍身体
        robe_points = [(40, 60), (80, 60), (90, 110), (30, 110)]
        pygame.draw.polygon(s, (25, 25, 30), robe_points)
        # 手持香炉（摇摆）
        censer_x = 85 + math.sin(t * 3) * 5
        censer_y = 75
        pygame.draw.circle(s, (80, 60, 40), (int(censer_x), censer_y), 6)
        pygame.draw.line(s, (60, 50, 35), (int(censer_x), censer_y - 6), (int(censer_x), censer_y - 20), 2)
        # 香炉烟雾
        for smoke in range(8):
            smoke_phase = ((t * 2 + smoke * 0.2) % 1.0)
            smoke_x = censer_x + math.sin(t * 4 + smoke) * 5
            smoke_y = censer_y - 20 - smoke_phase * 30
            smoke_alpha = int(150 * (1 - smoke_phase))
            if smoke_alpha > 0:
                smoke_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(smoke_surf, (60, 60, 65, smoke_alpha), (int(smoke_x), int(smoke_y)), int(4 + smoke_phase * 5))
                s.blit(smoke_surf, (0, 0))
        # 飘落的乌鸦羽毛
        for feather in range(4):
            feather_phase = ((t * 0.5 + feather * 0.3) % 1.0)
            feather_x = 20 + feather * 25 + math.sin(t + feather) * 10
            feather_y = feather_phase * 100 + 10
            feather_alpha = int(180 * (1 - feather_phase))
            if feather_alpha > 0:
                pygame.draw.ellipse(s, (20, 20, 25, feather_alpha), (int(feather_x) - 2, int(feather_y) - 5, 4, 10))
        return s
    
    elif model_style == "pandemic_biohazard":
        # 生化危机·橙色警报 - 生化危害标志，隔离区
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 警示条纹背景
        for stripe in range(12):
            stripe_y = stripe * 10
            stripe_color = (255, 150, 0) if stripe % 2 == 0 else (40, 40, 40)
            pygame.draw.rect(s, stripe_color, (10, stripe_y, 100, 10))
        # 生化危害符号（大型旋转）
        bio_rot = t * 30
        bio_cx, bio_cy = 60, 60
        # 中心圆
        pygame.draw.circle(s, (40, 40, 40), (bio_cx, bio_cy), 12)
        pygame.draw.circle(s, (255, 150, 0), (bio_cx, bio_cy), 12, 3)
        # 三片扇叶
        for blade in range(3):
            blade_angle = (blade * 120 + bio_rot) * 0.01745
            # 扇形主体
            arc_points = [(bio_cx, bio_cy)]
            for arc_seg in range(10):
                arc_a = blade_angle - 0.4 + arc_seg * 0.08
                arc_r = 40
                ax = bio_cx + math.cos(arc_a) * arc_r
                ay = bio_cy + math.sin(arc_a) * arc_r
                arc_points.append((int(ax), int(ay)))
            pygame.draw.polygon(s, (255, 150, 0), arc_points)
            # 内切口
            cut_angle = blade_angle
            cut_points = [(bio_cx, bio_cy)]
            for cut_seg in range(6):
                cut_a = cut_angle - 0.2 + cut_seg * 0.07
                cut_r = 25
                cx = bio_cx + math.cos(cut_a) * cut_r
                cy = bio_cy + math.sin(cut_a) * cut_r
                cut_points.append((int(cx), int(cy)))
            pygame.draw.polygon(s, (40, 40, 40), cut_points)
        # 警告闪烁效果
        if int(t * 4) % 2 == 0:
            flash_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 200, 100, 80), (60, 60), 55)
            s.blit(flash_surf, (0, 0))
        # 隔离带粒子
        for tape in range(6):
            tape_angle = (tape * 60 + t * 40) * 0.01745
            tape_r = 52
            tape_x = 60 + math.cos(tape_angle) * tape_r
            tape_y = 60 + math.sin(tape_angle) * tape_r
            pygame.draw.rect(s, (255, 200, 0), (int(tape_x) - 8, int(tape_y) - 2, 16, 4))
            pygame.draw.rect(s, (40, 40, 40), (int(tape_x) - 8, int(tape_y) - 2, 16, 4), 1)
        return s
    
    elif model_style == "pandemic_fungal":
        # 真菌帝国·孢子君主 - 恐怖真菌感染，蘑菇群落
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 腐败有机物背景
        for decay in range(20):
            decay_x = random.randint(15, 105)
            decay_y = random.randint(15, 105)
            decay_color = (80 + random.randint(0, 40), 60 + random.randint(0, 30), 50 + random.randint(0, 20))
            pygame.draw.circle(s, decay_color, (decay_x, decay_y), random.randint(3, 8))
        # 中央巨型蘑菇
        # 菌柄
        pygame.draw.rect(s, (180, 150, 120), (52, 60, 16, 40))
        pygame.draw.rect(s, (150, 120, 90), (52, 60, 16, 40), 2)
        # 菌盖（脉动）
        cap_pulse = abs(math.sin(t * 3))
        cap_width = int(40 + cap_pulse * 8)
        cap_height = int(25 + cap_pulse * 5)
        pygame.draw.ellipse(s, (150, 80, 60), (60 - cap_width//2, 35, cap_width, cap_height))
        # 菌盖斑点
        for spot in range(8):
            spot_angle = (spot * 45 + t * 10) * 0.01745
            spot_r = 12 + spot % 3 * 3
            spot_x = 60 + math.cos(spot_angle) * spot_r
            spot_y = 47 + math.sin(spot_angle) * (spot_r * 0.4)
            pygame.draw.circle(s, (200, 150, 100), (int(spot_x), int(spot_y)), 3)
        # 周围小蘑菇群落
        small_mushrooms = [(25, 80, 8), (40, 90, 6), (80, 85, 7), (95, 75, 5), (30, 70, 5), (90, 95, 6)]
        for mx, my, msize in small_mushrooms:
            grow_phase = abs(math.sin(t * 2 + mx * 0.1))
            # 小菌柄
            pygame.draw.rect(s, (160, 130, 100), (mx - 2, my, 4, msize + 5))
            # 小菌盖
            pygame.draw.ellipse(s, (130, 70, 50), (mx - msize, my - msize//2, msize * 2, msize))
        # 孢子云扩散
        for spore in range(25):
            spore_phase = ((t * 1.5 + spore * 0.1) % 1.0)
            spore_angle = (spore * 14.4 + t * 20) * 0.01745
            spore_r = 20 + spore_phase * 40
            spore_x = 60 + math.cos(spore_angle) * spore_r
            spore_y = 50 + math.sin(spore_angle) * spore_r * 0.7
            spore_alpha = int(200 * (1 - spore_phase))
            spore_size = int(3 * (1 - spore_phase * 0.5))
            if spore_alpha > 0:
                spore_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(spore_surf, (180, 150, 100, spore_alpha), (int(spore_x), int(spore_y)), spore_size)
                s.blit(spore_surf, (0, 0))
        return s
    
    elif model_style == "pandemic_neon_virus":
        # 赛博瘟疫·数据病毒 - 数字病毒，荧光绿代码
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 黑色数字背景
        pygame.draw.rect(s, (10, 15, 10), (10, 10, 100, 100))
        # 矩阵代码雨
        for col in range(10):
            col_x = 15 + col * 10
            col_speed = 1 + (col % 3) * 0.5
            for row in range(12):
                char_y = ((t * 30 * col_speed + row * 10 + col * 7) % 100) + 10
                char_alpha = int(255 * (1 - (char_y - 10) / 100))
                if char_alpha > 0:
                    # 绿色方块代表代码字符
                    pygame.draw.rect(s, (0, char_alpha, 0, char_alpha), (col_x, int(char_y), 6, 8))
        # 中央病毒实体（多边形赛博风格）
        virus_rot = t * 40
        virus_cx, virus_cy = 60, 60
        # 外层六边形
        outer_points = []
        for i in range(6):
            angle = (i * 60 + virus_rot) * 0.01745
            ox = virus_cx + math.cos(angle) * 30
            oy = virus_cy + math.sin(angle) * 30
            outer_points.append((int(ox), int(oy)))
        pygame.draw.polygon(s, (0, 80, 0), outer_points)
        pygame.draw.polygon(s, (0, 255, 100), outer_points, 2)
        # 内层三角形（反向旋转）
        inner_points = []
        for i in range(3):
            angle = (i * 120 - virus_rot * 2) * 0.01745
            ix = virus_cx + math.cos(angle) * 15
            iy = virus_cy + math.sin(angle) * 15
            inner_points.append((int(ix), int(iy)))
        pygame.draw.polygon(s, (0, 150, 50), inner_points)
        pygame.draw.polygon(s, (0, 255, 100), inner_points, 2)
        # 连接线（数据流）
        for i in range(6):
            pygame.draw.line(s, (0, 200, 80), outer_points[i], inner_points[i % 3], 1)
        # 核心发光
        glow_pulse = abs(math.sin(t * 5))
        glow_size = int(8 + glow_pulse * 4)
        pygame.draw.circle(s, (0, 255, 100), (virus_cx, virus_cy), glow_size)
        pygame.draw.circle(s, (200, 255, 200), (virus_cx, virus_cy), glow_size - 3)
        # 扫描线效果
        scan_y = int((t * 50) % 100) + 10
        pygame.draw.line(s, (0, 255, 100, 150), (10, scan_y), (110, scan_y), 1)
        return s
    
    elif model_style == "pandemic_zombie":
        # 丧尸末日·腐烂觉醒 - 腐烂丧尸，活死人
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 血渍背景
        for blood in range(15):
            blood_x = random.randint(15, 105)
            blood_y = random.randint(15, 105)
            blood_size = random.randint(5, 15)
            pygame.draw.circle(s, (80, 20, 20), (blood_x, blood_y), blood_size)
        # 丧尸头部
        head_sway = math.sin(t * 1.5) * 3
        head_cx = 60 + head_sway
        # 腐烂皮肤
        pygame.draw.ellipse(s, (90, 120, 70), (int(head_cx) - 18, 25, 36, 40))
        # 腐烂斑块
        rot_spots = [(head_cx - 8, 35), (head_cx + 10, 40), (head_cx - 5, 50), (head_cx + 8, 55)]
        for rx, ry in rot_spots:
            pygame.draw.circle(s, (60, 80, 50), (int(rx), int(ry)), random.randint(3, 6))
        # 空洞眼睛（一只正常一只缺失）
        pygame.draw.circle(s, (20, 20, 20), (int(head_cx) - 7, 38), 6)
        pygame.draw.circle(s, (200, 200, 50), (int(head_cx) - 7, 38), 3)  # 发光眼
        pygame.draw.ellipse(s, (40, 30, 30), (int(head_cx) + 2, 35, 10, 8))  # 缺失眼窝
        # 露出的牙齿
        for tooth in range(5):
            tooth_x = head_cx - 8 + tooth * 4
            tooth_h = 3 + random.randint(0, 3)
            pygame.draw.rect(s, (200, 200, 180), (int(tooth_x), 55, 3, tooth_h))
        # 撕裂的身体
        body_points = [(int(head_cx) - 15, 65), (int(head_cx) + 15, 65), 
                      (int(head_cx) + 20, 100), (int(head_cx) - 20, 100)]
        pygame.draw.polygon(s, (70, 100, 60), body_points)
        # 露出的肋骨
        for rib in range(4):
            rib_y = 72 + rib * 7
            pygame.draw.arc(s, (200, 190, 170), (int(head_cx) - 12, rib_y, 24, 8), 0, 3.14159, 2)
        # 伸出的手臂（抖动）
        arm_shake = math.sin(t * 8) * 3
        pygame.draw.line(s, (80, 110, 65), (int(head_cx) + 15, 75), (int(head_cx) + 40 + arm_shake, 60), 5)
        # 手指（弯曲）
        for finger in range(4):
            f_angle = (-0.5 + finger * 0.3 + math.sin(t * 4 + finger) * 0.2)
            fx = head_cx + 40 + arm_shake + math.cos(f_angle) * 8
            fy = 60 + math.sin(f_angle) * 8
            pygame.draw.line(s, (70, 100, 55), (int(head_cx) + 40 + arm_shake, 60), (int(fx), int(fy)), 2)
        return s
    
    elif model_style == "pandemic_parasite":
        # 寄生虫潮·蠕虫之母 - 恐怖寄生虫群，蠕动触须
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 有机物背景
        pygame.draw.circle(s, (120, 80, 90), (60, 60), 50)
        pygame.draw.circle(s, (100, 60, 70), (60, 60), 45)
        # 中央宿主（肿胀）
        host_pulse = abs(math.sin(t * 2))
        host_size = int(25 + host_pulse * 8)
        pygame.draw.circle(s, (150, 100, 110), (60, 60), host_size)
        pygame.draw.circle(s, (180, 120, 130), (60, 60), host_size - 5)
        # 内部可见的寄生虫轮廓
        for parasite in range(5):
            p_angle = (parasite * 72 + t * 20) * 0.01745
            p_r = 10 + math.sin(t * 3 + parasite) * 3
            px = 60 + math.cos(p_angle) * p_r
            py = 60 + math.sin(p_angle) * p_r
            pygame.draw.ellipse(s, (100, 60, 70), (int(px) - 4, int(py) - 2, 8, 4))
        # 蠕动的触须/蠕虫（从宿主伸出）
        for worm in range(8):
            worm_angle = (worm * 45) * 0.01745
            worm_points = [(60, 60)]
            for seg in range(8):
                seg_r = host_size + seg * 5
                seg_angle = worm_angle + math.sin(t * 4 + seg * 0.5 + worm) * 0.3
                wx = 60 + math.cos(seg_angle) * seg_r
                wy = 60 + math.sin(seg_angle) * seg_r
                worm_points.append((int(wx), int(wy)))
            # 渐变粗细的蠕虫
            for i in range(len(worm_points) - 1):
                width = max(1, 5 - i // 2)
                pygame.draw.line(s, (180, 100, 120), worm_points[i], worm_points[i + 1], width)
            # 蠕虫头部
            if len(worm_points) > 1:
                head_x, head_y = worm_points[-1]
                pygame.draw.circle(s, (200, 120, 140), (head_x, head_y), 3)
        # 脱落的虫卵
        for egg in range(10):
            egg_phase = ((t * 0.8 + egg * 0.15) % 1.0)
            egg_angle = (egg * 36 + t * 15) * 0.01745
            egg_r = 50 + egg_phase * 15
            egg_x = 60 + math.cos(egg_angle) * egg_r
            egg_y = 60 + math.sin(egg_angle) * egg_r
            egg_alpha = int(200 * (1 - egg_phase))
            if egg_alpha > 0:
                egg_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.ellipse(egg_surf, (200, 150, 160, egg_alpha), (int(egg_x) - 3, int(egg_y) - 2, 6, 4))
                s.blit(egg_surf, (0, 0))
        return s
    
    elif model_style == "pandemic_radiation":
        # 核辐射·切尔诺贝利 - 核辐射符号，变异生物
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 辐射光芒背景
        for ray in range(12):
            ray_angle = (ray * 30 + t * 10) * 0.01745
            ray_color = (255, 255, 0, 100) if ray % 2 == 0 else (40, 40, 40, 100)
            ray_points = [(60, 60)]
            r1_x = 60 + math.cos(ray_angle - 0.13) * 60
            r1_y = 60 + math.sin(ray_angle - 0.13) * 60
            r2_x = 60 + math.cos(ray_angle + 0.13) * 60
            r2_y = 60 + math.sin(ray_angle + 0.13) * 60
            ray_points.extend([(int(r1_x), int(r1_y)), (int(r2_x), int(r2_y))])
            ray_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(ray_surf, ray_color, ray_points)
            s.blit(ray_surf, (0, 0))
        # 核辐射三叶符号
        rad_rot = t * 20
        # 中心圆
        pygame.draw.circle(s, (40, 40, 40), (60, 60), 10)
        pygame.draw.circle(s, (255, 255, 0), (60, 60), 10, 2)
        # 三片扇叶
        for leaf in range(3):
            leaf_angle = (leaf * 120 + rad_rot) * 0.01745
            # 扇叶
            leaf_points = []
            for seg in range(-3, 4):
                seg_angle = leaf_angle + seg * 0.12
                seg_r = 35
                lx = 60 + math.cos(seg_angle) * seg_r
                ly = 60 + math.sin(seg_angle) * seg_r
                leaf_points.append((int(lx), int(ly)))
            leaf_points.append((60, 60))
            pygame.draw.polygon(s, (255, 255, 0), leaf_points)
        # 变异生物剪影（扭曲的动物）
        mutant_x = 60 + math.sin(t * 2) * 5
        mutant_y = 85
        # 变异体主体
        pygame.draw.ellipse(s, (80, 100, 60), (int(mutant_x) - 10, mutant_y - 5, 20, 12))
        # 多余的肢体
        for limb in range(5):
            limb_angle = (limb * 50 + t * 30) * 0.01745
            limb_x = mutant_x + math.cos(limb_angle) * 12
            limb_y = mutant_y + math.sin(limb_angle) * 8
            pygame.draw.line(s, (70, 90, 50), (int(mutant_x), mutant_y), (int(limb_x), int(limb_y)), 2)
        # 盖革计数器粒子
        for particle in range(15):
            particle_phase = ((t * 3 + particle * 0.1) % 1.0)
            particle_angle = random.random() * 6.28
            particle_r = particle_phase * 60
            particle_x = 60 + math.cos(particle_angle) * particle_r
            particle_y = 60 + math.sin(particle_angle) * particle_r
            particle_alpha = int(255 * (1 - particle_phase))
            if particle_alpha > 0:
                pygame.draw.circle(s, (255, 255, 0, particle_alpha), (int(particle_x), int(particle_y)), 2)
        return s
    
    elif model_style == "pandemic_coral":
        # 珊瑚瘟疫·深海异变 - 荧光珊瑚病变
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 深海背景
        pygame.draw.rect(s, (10, 30, 50), (10, 10, 100, 100))
        # 水中光线
        for beam in range(5):
            beam_x = 20 + beam * 20
            beam_alpha = int(30 + 20 * math.sin(t * 2 + beam))
            beam_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            beam_points = [(beam_x, 10), (beam_x + 10, 10), (beam_x + 15, 110), (beam_x - 5, 110)]
            pygame.draw.polygon(beam_surf, (100, 150, 200, beam_alpha), beam_points)
            s.blit(beam_surf, (0, 0))
        # 中央病变珊瑚（荧光色）
        coral_colors = [(255, 100, 150), (100, 255, 200), (255, 200, 100), (200, 100, 255)]
        # 主珊瑚分支
        for branch in range(6):
            branch_angle = (branch * 60 + 15) * 0.01745
            branch_sway = math.sin(t * 1.5 + branch) * 3
            branch_color = coral_colors[branch % 4]
            # 分支路径
            branch_points = [(60, 70)]
            for seg in range(5):
                seg_angle = branch_angle + math.sin(t * 2 + seg) * 0.2
                seg_r = 10 + seg * 8
                bx = 60 + math.cos(seg_angle) * seg_r + branch_sway
                by = 70 - seg * 8
                branch_points.append((int(bx), int(by)))
            # 绘制分支
            for i in range(len(branch_points) - 1):
                width = 5 - i
                pygame.draw.line(s, branch_color, branch_points[i], branch_points[i + 1], max(1, width))
            # 分支末端球体（息肉）
            end_x, end_y = branch_points[-1]
            polyp_pulse = abs(math.sin(t * 4 + branch))
            polyp_size = int(4 + polyp_pulse * 3)
            pygame.draw.circle(s, branch_color, (end_x, end_y), polyp_size)
            # 发光效果
            glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*branch_color, 100), (end_x, end_y), polyp_size + 5)
            s.blit(glow_surf, (0, 0))
        # 飘浮的病变碎片
        for debris in range(8):
            debris_phase = ((t * 0.5 + debris * 0.2) % 1.0)
            debris_x = 20 + debris * 12 + math.sin(t + debris) * 5
            debris_y = 100 - debris_phase * 80
            debris_color = coral_colors[debris % 4]
            debris_alpha = int(200 * (1 - abs(debris_phase - 0.5) * 2))
            if debris_alpha > 0:
                pygame.draw.circle(s, (*debris_color, debris_alpha), (int(debris_x), int(debris_y)), 3)
        return s
    
    elif model_style == "pandemic_prion":
        # 朊病毒·疯牛噩梦 - 大脑海绵状病变
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 大脑背景（粉色）
        pygame.draw.ellipse(s, (220, 180, 190), (20, 25, 80, 70))
        # 大脑沟回
        brain_folds = [
            [(30, 40), (40, 35), (50, 40), (45, 50)],
            [(55, 35), (70, 30), (80, 40), (70, 50)],
            [(35, 55), (50, 50), (60, 60), (45, 70)],
            [(65, 55), (80, 50), (85, 65), (70, 70)]
        ]
        for fold in brain_folds:
            pygame.draw.lines(s, (200, 150, 160), False, fold, 2)
        # 海绵状空洞（prion 造成）
        holes = [(35, 45, 5), (55, 40, 6), (75, 45, 4), (45, 60, 7), (65, 55, 5), (50, 75, 4)]
        for hx, hy, hr in holes:
            hole_pulse = abs(math.sin(t * 3 + hx * 0.1))
            hole_r = hr + int(hole_pulse * 2)
            pygame.draw.circle(s, (40, 30, 35), (hx, hy), hole_r)
            pygame.draw.circle(s, (80, 60, 70), (hx, hy), hole_r, 1)
        # 扭曲的蛋白质链（动态蠕动）
        for chain in range(6):
            chain_start_angle = (chain * 60 + t * 30) * 0.01745
            chain_points = []
            for seg in range(10):
                seg_angle = chain_start_angle + seg * 0.5 + math.sin(t * 5 + seg) * 0.3
                seg_r = 5 + seg * 4
                cx = 60 + math.cos(seg_angle) * seg_r
                cy = 55 + math.sin(seg_angle) * seg_r * 0.6
                chain_points.append((int(cx), int(cy)))
            if len(chain_points) > 1:
                pygame.draw.lines(s, (255, 200, 100), False, chain_points, 2)
                # 蛋白质折叠节点
                for point in chain_points[::2]:
                    pygame.draw.circle(s, (255, 220, 150), point, 2)
        # 神经信号干扰（闪烁）
        if random.random() > 0.7:
            glitch_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            glitch_x = random.randint(25, 95)
            glitch_y = random.randint(30, 85)
            pygame.draw.circle(glitch_surf, (255, 255, 255, 150), (glitch_x, glitch_y), 8)
            s.blit(glitch_surf, (0, 0))
        return s
    
    elif model_style == "pandemic_alien":
        # 外星瘟疫·仙女座病毒 - 来自星际的未知病原体
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 外星星空背景
        for star in range(40):
            star_x = random.randint(5, 115)
            star_y = random.randint(5, 115)
            star_bright = int(100 + 155 * random.random())
            pygame.draw.circle(s, (star_bright, star_bright, star_bright), (star_x, star_y), 1)
        # 外星病毒（奇异几何形态）
        alien_rot = t * 25
        alien_cx, alien_cy = 60, 60
        # 四面体核心
        tetra_points = []
        for i in range(4):
            if i < 3:
                angle = (i * 120 + alien_rot) * 0.01745
                tx = alien_cx + math.cos(angle) * 25
                ty = alien_cy + math.sin(angle) * 25
            else:
                tx, ty = alien_cx, alien_cy - 30
            tetra_points.append((int(tx), int(ty)))
        # 绘制四面体边
        pygame.draw.line(s, (100, 255, 200), tetra_points[0], tetra_points[1], 2)
        pygame.draw.line(s, (100, 255, 200), tetra_points[1], tetra_points[2], 2)
        pygame.draw.line(s, (100, 255, 200), tetra_points[2], tetra_points[0], 2)
        pygame.draw.line(s, (80, 200, 160), tetra_points[0], tetra_points[3], 2)
        pygame.draw.line(s, (80, 200, 160), tetra_points[1], tetra_points[3], 2)
        pygame.draw.line(s, (80, 200, 160), tetra_points[2], tetra_points[3], 2)
        # 外星触须（非欧几里得弯曲）
        for tendril in range(8):
            tendril_angle = (tendril * 45 + t * 20) * 0.01745
            tendril_points = [(alien_cx, alien_cy)]
            for seg in range(8):
                seg_r = 25 + seg * 5
                # 非欧几里得弯曲
                seg_curve = math.sin(t * 3 + seg * 0.8 + tendril) * 0.5
                seg_angle = tendril_angle + seg_curve
                tx = alien_cx + math.cos(seg_angle) * seg_r
                ty = alien_cy + math.sin(seg_angle) * seg_r
                tendril_points.append((int(tx), int(ty)))
            tendril_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            tendril_alpha = int(200 - tendril * 10)
            pygame.draw.lines(tendril_surf, (100, 255, 200, tendril_alpha), False, tendril_points, 2)
            s.blit(tendril_surf, (0, 0))
        # 核心脉动
        core_pulse = abs(math.sin(t * 4))
        core_size = int(10 + core_pulse * 5)
        pygame.draw.circle(s, (150, 255, 220), (alien_cx, alien_cy), core_size)
        pygame.draw.circle(s, (200, 255, 240), (alien_cx, alien_cy), core_size - 3)
        return s
    
    elif model_style == "pandemic_chimera":
        # 嵌合瘟疫·基因拼接 - 人造超级病原体，DNA拼接
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 实验室蓝色背景
        pygame.draw.rect(s, (20, 30, 50), (10, 10, 100, 100))
        # DNA双螺旋（多色拼接）
        helix_colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]
        for strand in range(2):
            strand_offset = strand * 3.14159
            strand_points = []
            for seg in range(20):
                seg_t = seg / 20
                seg_y = 15 + seg * 5
                seg_x = 60 + math.sin(seg_t * 6.28 + t * 3 + strand_offset) * 20
                strand_points.append((int(seg_x), seg_y))
                # 拼接色块
                color_idx = seg // 5
                pygame.draw.circle(s, helix_colors[color_idx % 4], (int(seg_x), seg_y), 4)
            # 连接线
            if strand == 0:
                for seg in range(0, 20, 2):
                    seg_t = seg / 20
                    seg_y = 15 + seg * 5
                    seg_x1 = 60 + math.sin(seg_t * 6.28 + t * 3) * 20
                    seg_x2 = 60 + math.sin(seg_t * 6.28 + t * 3 + 3.14159) * 20
                    pygame.draw.line(s, (150, 150, 150), (int(seg_x1), seg_y), (int(seg_x2), seg_y), 1)
        # 基因编辑标记（CRISPR切口）
        for cut in range(3):
            cut_y = 30 + cut * 30
            cut_x = 60 + math.sin(t * 2 + cut) * 15
            # 剪刀符号
            pygame.draw.line(s, (255, 200, 100), (int(cut_x) - 8, cut_y - 5), (int(cut_x) + 8, cut_y + 5), 2)
            pygame.draw.line(s, (255, 200, 100), (int(cut_x) - 8, cut_y + 5), (int(cut_x) + 8, cut_y - 5), 2)
        # 嵌合病毒实体（多种病毒特征融合）
        chimera_x, chimera_y = 85, 90
        # 球形基底
        pygame.draw.circle(s, (200, 100, 255), (chimera_x, chimera_y), 15)
        # 不同病毒的刺突
        for spike in range(8):
            spike_angle = (spike * 45 + t * 30) * 0.01745
            spike_color = helix_colors[spike % 4]
            spike_len = 8 + (spike % 3) * 3
            sx = chimera_x + math.cos(spike_angle) * (15 + spike_len)
            sy = chimera_y + math.sin(spike_angle) * (15 + spike_len)
            pygame.draw.line(s, spike_color, (chimera_x + int(math.cos(spike_angle) * 15), 
                                              chimera_y + int(math.sin(spike_angle) * 15)),
                           (int(sx), int(sy)), 2)
            pygame.draw.circle(s, spike_color, (int(sx), int(sy)), 3)
        return s
    
    elif model_style == "pandemic_omega":
        # 终末瘟疫·Ω灭绝株 - 人类终结病毒，黑色死亡
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 虚空黑暗背景
        for void in range(8):
            void_r = 60 - void * 6
            void_alpha = 50 + void * 20
            pygame.draw.circle(s, (void_alpha // 5, 0, 0, void_alpha), (60, 60), void_r)
        # Ω符号（巨大，旋转）
        omega_rot = t * 5
        omega_cx, omega_cy = 60, 55
        # Ω 主体（手绘近似）
        omega_points = []
        for i in range(20):
            i_t = i / 20
            omega_angle = (-0.5 + i_t * 4.14) + omega_rot * 0.01745
            omega_r = 30
            if i < 18:
                ox = omega_cx + math.cos(omega_angle) * omega_r
                oy = omega_cy + math.sin(omega_angle) * omega_r * 0.8
                omega_points.append((int(ox), int(oy)))
        if len(omega_points) > 2:
            pygame.draw.lines(s, (150, 0, 0), False, omega_points, 5)
        # Ω 底部两脚
        pygame.draw.line(s, (150, 0, 0), (omega_cx - 25, omega_cy + 20), (omega_cx - 25, omega_cy + 35), 5)
        pygame.draw.line(s, (150, 0, 0), (omega_cx + 25, omega_cy + 20), (omega_cx + 25, omega_cy + 35), 5)
        # 死亡能量波（向外扩散）
        for wave in range(5):
            wave_phase = ((t * 1.5 + wave * 0.3) % 1.0)
            wave_r = int(20 + wave_phase * 45)
            wave_alpha = int(200 * (1 - wave_phase))
            if wave_alpha > 0:
                wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(wave_surf, (100, 0, 0, wave_alpha), (60, 60), wave_r, 3)
                s.blit(wave_surf, (0, 0))
        # 熄灭的生命火花（下坠）
        for spark in range(10):
            spark_phase = ((t * 0.8 + spark * 0.15) % 1.0)
            spark_x = 20 + spark * 10 + math.sin(t * 2 + spark) * 5
            spark_y = 10 + spark_phase * 100
            spark_alpha = int(255 * (1 - spark_phase))
            if spark_alpha > 0:
                # 火花从亮变暗
                spark_brightness = int(255 * (1 - spark_phase))
                pygame.draw.circle(s, (spark_brightness, spark_brightness // 3, 0, spark_alpha), 
                                  (int(spark_x), int(spark_y)), 2)
        # 中心黑洞
        pygame.draw.circle(s, (0, 0, 0), (omega_cx, omega_cy), 12)
        pygame.draw.circle(s, (50, 0, 0), (omega_cx, omega_cy), 12, 2)
        return s
    
    return None
