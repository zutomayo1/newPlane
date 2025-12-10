# Chronos 专属涂装渲染模块
# 包含: chronos_memoir, chronos_biological, chronos_tidal, chronos_musical,
#       chronos_geological, chronos_culinary, chronos_athletic, chronos_gardening,
#       chronos_theatrical, chronos_chemical, chronos_meteorological, chronos_archaeological

import pygame
import math
import random

# Chronos涂装列表
CHRONOS_STYLES = [
    "chronos_memoir", "chronos_biological", "chronos_tidal", "chronos_musical",
    "chronos_geological", "chronos_culinary", "chronos_athletic", "chronos_gardening",
    "chronos_theatrical", "chronos_chemical", "chronos_meteorological", "chronos_archaeological"
]

def is_chronos_style(model_style):
    """检查是否为Chronos涂装"""
    return model_style in CHRONOS_STYLES

def render_chronos_skin(s, c, model_style, t, pid, static=False):
    """渲染Chronos涂装，返回Surface或None"""
    pulse = math.sin(t * 2) * 0.15 + 1
    
    if model_style == "chronos_memoir":
        # 时光相册·记忆胶片 - 老式胶片相机时钟，照片碎片，怀旧棕褐滤镜
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 怀旧棕褐色背景（胶片纹理）
        for grain_i in range(100):
            gx = random.randint(0, 120)
            gy = random.randint(0, 120)
            grain_alpha = random.randint(20, 60)
            pygame.draw.circle(s, (180, 150, 110, grain_alpha), (gx, gy), 1)
        # 相机快门时钟框
        pygame.draw.circle(s, (200, 160, 120), (60, 60), 40, 3)
        pygame.draw.circle(s, (220, 180, 140), (60, 60), 37, 1)
        # 24张照片碎片（环绕旋转）
        for photo_i in range(24):
            photo_angle = (photo_i * 15 + t * 8) * 0.01745
            photo_r = 32 + int(3 * math.sin(t * 2 + photo_i))
            photo_x = 60 + math.cos(photo_angle) * photo_r
            photo_y = 60 + math.sin(photo_angle) * photo_r
            # 照片矩形（不同泛黄程度）
            sepia = (200 - photo_i * 3, 160 - photo_i * 2, 120 - photo_i)
            photo_rect = pygame.Rect(int(photo_x) - 4, int(photo_y) - 3, 8, 6)
            pygame.draw.rect(s, sepia, photo_rect)
            pygame.draw.rect(s, (180, 150, 110), photo_rect, 1)
        # 时钟指针（胶卷条纹）
        for hand_i in range(2):
            hand_angle = (t * (20 if hand_i == 0 else 3) - 90) * 0.01745
            hand_len = 28 if hand_i == 0 else 35
            hx = 60 + math.cos(hand_angle) * hand_len
            hy = 60 + math.sin(hand_angle) * hand_len
            hand_color = (200, 160, 120) if hand_i == 0 else (220, 180, 140)
            pygame.draw.line(s, hand_color, (60, 60), (hx, hy), 3)
        # 中心快门按钮
        pygame.draw.circle(s, (220, 180, 140), (60, 60), 8)
        pygame.draw.circle(s, (200, 160, 120), (60, 60), 5)
        return s
    
    elif model_style == "chronos_biological":
        # 生物钟律·心跳脉搏 - 活体时钟，心脏跳动韵律，血管脉冲，DNA螺旋
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 心脏跳动核心（周期性脉动）
        heartbeat_cycle = int(t * 72 / 60) % 2  # 72 BPM
        beat_phase = (t * 72 / 60) % 1.0
        beat_size = 25 + int(8 * math.sin(beat_phase * math.pi * 2))
        pygame.draw.circle(s, (255, 120, 140), (60, 60), beat_size)
        pygame.draw.circle(s, (255, 100, 120), (60, 60), beat_size - 5)
        # 血管脉冲波纹（8个方向扩散）
        for pulse_i in range(8):
            pulse_angle = (pulse_i * 45) * 0.01745
            pulse_r = 30 + int(15 * beat_phase)
            pulse_alpha = int(200 * (1 - beat_phase))
            if pulse_alpha > 0:
                pulse_x = 60 + math.cos(pulse_angle) * pulse_r
                pulse_y = 60 + math.sin(pulse_angle) * pulse_r
                pygame.draw.circle(s, (255, 150, 170, pulse_alpha), (int(pulse_x), int(pulse_y)), 6)
        # DNA双螺旋缠绕（环绕时钟）
        for helix_i in range(36):
            helix_progress = helix_i / 36
            helix_angle = (helix_progress * 360 + t * 30) * 0.01745
            helix_r = 38
            helix_offset = 5 * math.sin(helix_progress * math.pi * 6)
            # 第一条链
            hx1 = 60 + math.cos(helix_angle) * (helix_r + helix_offset)
            hy1 = 60 + math.sin(helix_angle) * (helix_r + helix_offset)
            pygame.draw.circle(s, (255, 150, 170), (int(hx1), int(hy1)), 2)
            # 第二条链（相位差180度）
            hx2 = 60 + math.cos(helix_angle) * (helix_r - helix_offset)
            hy2 = 60 + math.sin(helix_angle) * (helix_r - helix_offset)
            pygame.draw.circle(s, (230, 80, 100), (int(hx2), int(hy2)), 2)
            # 碱基对连接（每隔3个）
            if helix_i % 3 == 0:
                pygame.draw.line(s, (255, 200, 210), (hx1, hy1), (hx2, hy2), 1)
        # 细胞分裂动画（时钟指针）
        cell_hand_angle = (t * 15 - 90) * 0.01745
        cell_hx = 60 + math.cos(cell_hand_angle) * 30
        cell_hy = 60 + math.sin(cell_hand_angle) * 30
        pygame.draw.line(s, (255, 100, 120), (60, 60), (cell_hx, cell_hy), 3)
        # 生命能量粒子
        for life_i in range(12):
            life_angle = (life_i * 30 + t * 50) * 0.01745
            life_x = 60 + math.cos(life_angle) * 48
            life_y = 60 + math.sin(life_angle) * 48
            pygame.draw.circle(s, (255, 150, 170), (int(life_x), int(life_y)), 3)
        return s
    
    elif model_style == "chronos_tidal":
        # 潮汐涨落·月相周期 - 海洋潮汐时钟，月相盈亏，潮水波纹，贝壳装饰
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 月相周期（8相）
        moon_phase = int((t * 0.5) % 8)
        moon_x, moon_y = 60, 25
        # 绘制月相
        pygame.draw.circle(s, (240, 240, 240), (moon_x, moon_y), 12)
        if moon_phase < 4:  # 上弦
            shadow_offset = int(12 * (moon_phase / 4))
            pygame.draw.circle(s, (100, 120, 140), (moon_x - shadow_offset, moon_y), 12)
        else:  # 下弦
            shadow_offset = int(12 * ((8 - moon_phase) / 4))
            pygame.draw.circle(s, (100, 120, 140), (moon_x + shadow_offset, moon_y), 12)
        # 12层潮汐波纹（从中心扩散）
        for tide_i in range(12):
            tide_phase = ((t * 2 + tide_i * 0.2) % 1.0)
            tide_r = int(20 + tide_phase * 35)
            tide_alpha = int(150 * (1 - tide_phase))
            if tide_alpha > 0:
                # 波浪形状（不规则）
                wave_points = []
                for seg in range(24):
                    wave_angle = (seg * 15) * 0.01745
                    wave_r_offset = tide_r + int(3 * math.sin(seg * 0.8 + t * 4))
                    wx = 60 + math.cos(wave_angle) * wave_r_offset
                    wy = 60 + math.sin(wave_angle) * wave_r_offset
                    wave_points.append((int(wx), int(wy)))
                if len(wave_points) > 2:
                    pygame.draw.polygon(s, (100, 180, 220, tide_alpha), wave_points, 2)
        # 贝壳珍珠点缀（8个）
        for shell_i in range(8):
            shell_angle = (shell_i * 45 + t * 5) * 0.01745
            shell_r = 42
            shell_x = 60 + math.cos(shell_angle) * shell_r
            shell_y = 60 + math.sin(shell_angle) * shell_r
            # 贝壳形状（螺旋渐大）
            for spiral in range(3):
                spiral_r = 4 + spiral * 2
                spiral_offset = spiral * 0.3
                sx = shell_x + math.cos(shell_angle + spiral_offset) * spiral_r
                sy = shell_y + math.sin(shell_angle + spiral_offset) * spiral_r
                pygame.draw.circle(s, (220, 240, 255), (int(sx), int(sy)), 4 - spiral)
        # 中心漩涡（潮汐力）
        pygame.draw.circle(s, (120, 200, 240), (60, 60), 18, 2)
        pygame.draw.circle(s, (100, 180, 220), (60, 60), 12)
        # 时钟指针（海浪形）
        hand_angle = (t * 12 - 90) * 0.01745
        hx = 60 + math.cos(hand_angle) * 32
        hy = 60 + math.sin(hand_angle) * 32
        pygame.draw.line(s, (80, 160, 200), (60, 60), (hx, hy), 3)
        return s
    
    elif model_style == "chronos_musical":
        # 音律节拍·八音盒舞 - 旋转八音盒时钟，音符飘舞，五线谱螺旋，舞者旋转
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 八音盒底座（旋转）
        box_angle = t * 10
        for box_seg in range(8):
            seg_angle = (box_seg * 45 + box_angle) * 0.01745
            box_x = 60 + math.cos(seg_angle) * 45
            box_y = 60 + math.sin(seg_angle) * 45
            pygame.draw.circle(s, (230, 180, 230), (int(box_x), int(box_y)), 4)
        # 五线谱螺旋（3圈）
        for staff_i in range(3):
            staff_r = 25 + staff_i * 8
            for seg in range(24):
                staff_angle = (seg * 15 + t * 20) * 0.01745
                staff_x = 60 + math.cos(staff_angle) * staff_r
                staff_y = 60 + math.sin(staff_angle) * staff_r
                pygame.draw.line(s, (200, 150, 200), (staff_x, staff_y), 
                               (staff_x + 3, staff_y), 1)
        # 32个音符粒子飘舞
        note_shapes = [(2, 4), (3, 3), (2, 5)]  # 不同音符大小
        for note_i in range(32):
            note_angle = (note_i * 11.25 + t * 40) * 0.01745
            note_r = 20 + int(15 * math.sin(t * 3 + note_i * 0.2))
            note_x = 60 + math.cos(note_angle) * note_r
            note_y = 60 + math.sin(note_angle) * note_r
            note_shape = note_shapes[note_i % 3]
            # 音符椭圆
            pygame.draw.ellipse(s, (255, 200, 255), 
                              (int(note_x) - note_shape[0], int(note_y) - note_shape[1],
                               note_shape[0] * 2, note_shape[1] * 2))
            # 音符符杆
            pygame.draw.line(s, (230, 180, 230), (note_x, note_y), 
                           (note_x, note_y - 8), 1)
        # 中心旋转舞者（简化轮廓）
        dancer_angle = t * 60
        dancer_arms = [(15, 0), (15, 90), (15, 180), (15, 270)]
        for arm_r, arm_offset in dancer_arms:
            arm_angle = (dancer_angle + arm_offset) * 0.01745
            arm_x = 60 + math.cos(arm_angle) * arm_r
            arm_y = 60 + math.sin(arm_angle) * arm_r
            pygame.draw.line(s, (255, 200, 255), (60, 60), (arm_x, arm_y), 2)
        pygame.draw.circle(s, (255, 200, 255), (60, 60), 6)
        return s
    
    elif model_style == "chronos_geological":
        # 地质纪元·岩层年轮 - 地层沉积时钟，亿万年岩石叠加，化石镶嵌
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 15层地质沉积圈（从内到外，颜色渐变）
        strata_colors = [
            (160, 140, 120), (155, 135, 115), (150, 130, 110),
            (145, 125, 105), (140, 120, 100), (135, 115, 95),
            (130, 110, 90), (125, 105, 85), (120, 100, 80),
            (115, 95, 75), (110, 90, 70), (105, 85, 65),
            (100, 80, 60), (95, 75, 55), (90, 70, 50)
        ]
        for layer_i in range(15):
            layer_r = 8 + layer_i * 3
            layer_color = strata_colors[layer_i]
            pygame.draw.circle(s, layer_color, (60, 60), layer_r, 2)
            # 地层不规则边缘（裂缝）
            if layer_i % 3 == 0:
                for crack in range(8):
                    crack_angle = (crack * 45 + layer_i * 5) * 0.01745
                    crack_x = 60 + math.cos(crack_angle) * layer_r
                    crack_y = 60 + math.sin(crack_angle) * layer_r
                    crack_len = 3
                    crack_end_x = crack_x + math.cos(crack_angle) * crack_len
                    crack_end_y = crack_y + math.sin(crack_angle) * crack_len
                    pygame.draw.line(s, (80, 60, 40), (crack_x, crack_y), 
                                   (crack_end_x, crack_end_y), 1)
        # 8个化石标记（三叶虫、菊石等）
        for fossil_i in range(8):
            fossil_angle = (fossil_i * 45 + t * 3) * 0.01745
            fossil_r = 38
            fossil_x = 60 + math.cos(fossil_angle) * fossil_r
            fossil_y = 60 + math.sin(fossil_angle) * fossil_r
            # 螺旋化石形状
            for spiral in range(4):
                spiral_offset = spiral * 0.4
                spiral_r = 3 + spiral
                sx = fossil_x + math.cos(fossil_angle + spiral_offset) * spiral_r * 0.5
                sy = fossil_y + math.sin(fossil_angle + spiral_offset) * spiral_r * 0.5
                pygame.draw.circle(s, (100, 80, 60), (int(sx), int(sy)), 2)
        # 地质时钟指针（岩石纹理）
        hand_angle = (t * 5 - 90) * 0.01745
        hx = 60 + math.cos(hand_angle) * 35
        hy = 60 + math.sin(hand_angle) * 35
        pygame.draw.line(s, (140, 120, 100), (60, 60), (hx, hy), 4)
        pygame.draw.circle(s, (160, 140, 120), (60, 60), 6)
        return s
    
    elif model_style == "chronos_culinary":
        # 烹饪计时·美食盛宴 - 厨房定时器时钟，食材翻炒，沸腾泡泡，香料飘散
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 厨房定时器外框（橙色温暖）
        pygame.draw.circle(s, (255, 150, 80), (60, 60), 42, 3)
        pygame.draw.circle(s, (255, 180, 100), (60, 60), 38, 1)
        # 60个刻度（分钟）
        for minute in range(60):
            mark_angle = (minute * 6 - 90) * 0.01745
            mark_r = 35 if minute % 5 == 0 else 37
            mark_len = 5 if minute % 5 == 0 else 3
            mx1 = 60 + math.cos(mark_angle) * mark_r
            my1 = 60 + math.sin(mark_angle) * mark_r
            mx2 = 60 + math.cos(mark_angle) * (mark_r - mark_len)
            my2 = 60 + math.sin(mark_angle) * (mark_r - mark_len)
            pygame.draw.line(s, (230, 130, 60), (mx1, my1), (mx2, my2), 2)
        # 40个食材粒子（环绕旋转）
        ingredients = [
            (255, 100, 100),  # 番茄红
            (100, 255, 100),  # 蔬菜绿
            (255, 200, 100),  # 面包黄
            (200, 150, 100)   # 肉类棕
        ]
        for ing_i in range(40):
            ing_angle = (ing_i * 9 + t * 30) * 0.01745
            ing_r = 28 + int(5 * math.sin(t * 4 + ing_i))
            ing_x = 60 + math.cos(ing_angle) * ing_r
            ing_y = 60 + math.sin(ing_angle) * ing_r
            ing_color = ingredients[ing_i % 4]
            pygame.draw.circle(s, ing_color, (int(ing_x), int(ing_y)), 3)
        # 沸腾泡泡效果（从中心向上）
        for bubble_i in range(20):
            bubble_progress = ((t * 3 + bubble_i * 0.1) % 1.0)
            bubble_x = 60 + int(10 * math.sin(bubble_i + t * 5))
            bubble_y = 60 - int(bubble_progress * 40)
            bubble_size = int(4 * (1 - bubble_progress))
            if bubble_size > 0:
                bubble_alpha = int(180 * (1 - bubble_progress))
                pygame.draw.circle(s, (255, 255, 255, bubble_alpha), 
                                 (bubble_x, bubble_y), bubble_size)
        # 定时器指针（旋转倒数）
        timer_hand_angle = (t * 20 - 90) * 0.01745
        thx = 60 + math.cos(timer_hand_angle) * 30
        thy = 60 + math.sin(timer_hand_angle) * 30
        pygame.draw.line(s, (255, 100, 50), (60, 60), (thx, thy), 4)
        # 中心旋钮
        pygame.draw.circle(s, (255, 150, 80), (60, 60), 8)
        pygame.draw.circle(s, (255, 180, 100), (60, 60), 5)
        return s
    
    elif model_style == "chronos_athletic":
        # 竞技秒表·极速冲刺 - 运动秒表时钟，赛道跑道，冲刺残影，汗水飞溅
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 8条赛道跑道（环形）
        for lane_i in range(8):
            lane_r = 15 + lane_i * 5
            lane_color = (255, 80 + lane_i * 5, 80 + lane_i * 5)
            pygame.draw.circle(s, lane_color, (60, 60), lane_r, 1)
        # 起跑线标记（4个方向）
        for start_i in range(4):
            start_angle = (start_i * 90) * 0.01745
            start_x = 60 + math.cos(start_angle) * 48
            start_y = 60 + math.sin(start_angle) * 48
            pygame.draw.rect(s, (255, 255, 255), (int(start_x) - 2, int(start_y) - 5, 4, 10))
        # 5层冲刺残影（运动员）
        for afterimage_i in range(5):
            afterimage_alpha = 200 - afterimage_i * 40
            afterimage_offset = afterimage_i * 5
            runner_angle = (t * 80 - afterimage_offset * 10) * 0.01745
            runner_r = 35
            runner_x = 60 + math.cos(runner_angle) * runner_r
            runner_y = 60 + math.sin(runner_angle) * runner_r
            # 简化运动员形状（椭圆）
            runner_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.ellipse(runner_surf, (255, 120, 120, afterimage_alpha),
                              (int(runner_x) - 4, int(runner_y) - 6, 8, 12))
            s.blit(runner_surf, (0, 0))
        # 汗水飞溅粒子（20个）
        for sweat_i in range(20):
            sweat_progress = ((t * 5 + sweat_i * 0.1) % 1.0)
            sweat_angle = (t * 80 + sweat_i * 18) * 0.01745
            sweat_r = 35 + int(sweat_progress * 15)
            sweat_x = 60 + math.cos(sweat_angle) * sweat_r
            sweat_y = 60 + math.sin(sweat_angle) * sweat_r
            sweat_alpha = int(200 * (1 - sweat_progress))
            if sweat_alpha > 0:
                pygame.draw.circle(s, (150, 200, 255, sweat_alpha), (int(sweat_x), int(sweat_y)), 2)
        # 秒表指针（极速旋转）
        stopwatch_hand = (t * 100 - 90) * 0.01745
        shx = 60 + math.cos(stopwatch_hand) * 30
        shy = 60 + math.sin(stopwatch_hand) * 30
        pygame.draw.line(s, (255, 80, 80), (60, 60), (shx, shy), 3)
        # 中心秒表按钮
        pygame.draw.circle(s, (255, 120, 120), (60, 60), 10)
        pygame.draw.circle(s, (255, 80, 80), (60, 60), 6)
        return s
    
    elif model_style == "chronos_gardening":
        # 园艺四季·花开花落 - 植物生长时钟，种子发芽，藤蔓攀爬，四季轮转
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 四季背景色环（春夏秋冬）
        season_colors = [
            (150, 255, 150),  # 春-嫩绿
            (100, 200, 100),  # 夏-深绿
            (255, 180, 100),  # 秋-橙黄
            (200, 220, 255)   # 冬-冰蓝
        ]
        current_season = int((t * 0.5) % 4)
        season_color = season_colors[current_season]
        pygame.draw.circle(s, season_color, (60, 60), 45, 8)
        # 12条藤蔓螺旋攀爬
        for vine_i in range(12):
            vine_angle_start = (vine_i * 30) * 0.01745
            vine_points = []
            for seg in range(8):
                vine_progress = seg / 8
                vine_r = 10 + vine_progress * 35
                vine_angle = vine_angle_start + vine_progress * (t * 2)
                vine_offset = 3 * math.sin(t * 3 + vine_i + seg)
                vx = 60 + math.cos(vine_angle) * (vine_r + vine_offset)
                vy = 60 + math.sin(vine_angle) * (vine_r + vine_offset)
                vine_points.append((int(vx), int(vy)))
            if len(vine_points) > 1:
                pygame.draw.lines(s, (100, 180, 80), False, vine_points, 2)
        # 16朵季节性花朵绽放
        bloom_phase = (t * 2) % 1.0
        for bloom_i in range(16):
            bloom_angle = (bloom_i * 22.5 + t * 10) * 0.01745
            bloom_r = 38
            bloom_x = 60 + math.cos(bloom_angle) * bloom_r
            bloom_y = 60 + math.sin(bloom_angle) * bloom_r
            # 花瓣大小随时间变化（绽放-凋零）
            petal_size = int(5 * abs(math.sin(bloom_phase * math.pi + bloom_i * 0.2)))
            if petal_size > 0:
                # 5片花瓣
                for petal in range(5):
                    petal_angle = (petal * 72 + t * 5) * 0.01745
                    petal_x = bloom_x + math.cos(petal_angle) * petal_size
                    petal_y = bloom_y + math.sin(petal_angle) * petal_size
                    pygame.draw.circle(s, season_color, (int(petal_x), int(petal_y)), 3)
                # 花心
                pygame.draw.circle(s, (255, 200, 100), (int(bloom_x), int(bloom_y)), 2)
        # 中心种子（生长核心）
        pygame.draw.circle(s, (140, 220, 120), (60, 60), 12)
        pygame.draw.circle(s, (120, 200, 100), (60, 60), 8)
        # 生长时针
        growth_hand = (t * 8 - 90) * 0.01745
        ghx = 60 + math.cos(growth_hand) * 28
        ghy = 60 + math.sin(growth_hand) * 28
        pygame.draw.line(s, (100, 180, 80), (60, 60), (ghx, ghy), 3)
        # 蒸汽气泡（40个）
        for steam_i in range(40):
            steam_progress = ((t * 2 + steam_i * 0.05) % 1.0)
            steam_x = 60 + random.randint(-20, 20)
            steam_y = 60 + int(steam_progress * 50)
            steam_size = int(3 * (1 - steam_progress))
            if steam_size > 0:
                alpha = int(150 * (1 - steam_progress))
                pygame.draw.circle(s, (220, 220, 220, alpha), (steam_x, steam_y), steam_size)
        # 罗马数字刻度位置（用小圆圈代替）
        for roman in range(12):
            roman_angle = (roman * 30 - 90) * 0.01745
            rx = 60 + math.cos(roman_angle) * 28
            ry = 60 + math.sin(roman_angle) * 28
            pygame.draw.circle(s, (200, 150, 80), (int(rx), int(ry)), 3)
        return s
    
    elif model_style == "chronos_theatrical":
        # 戏剧幕布·三幕悲喜 - 舞台大幕时钟，红色天鹅绒帷幕，面具悲喜，聚光灯
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 8条帷幕波浪（红色天鹅绒）
        for curtain_i in range(8):
            curtain_x = 15 + curtain_i * 13
            curtain_points = []
            for wave_seg in range(10):
                wave_y = 20 + wave_seg * 8 + int(8 * math.sin(t * 3 + curtain_i * 0.5 + wave_seg * 0.3))
                curtain_points.append((curtain_x, wave_y))
            if len(curtain_points) > 1:
                pygame.draw.lines(s, (180, 50, 80), False, curtain_points, 3)
        # 三幕分界线（起承转合）
        for act in range(3):
            act_angle = (act * 120 + t * 5) * 0.01745
            act_r = 38
            act_x = 60 + math.cos(act_angle) * act_r
            act_y = 60 + math.sin(act_angle) * act_r
            pygame.draw.line(s, (200, 80, 100), (60, 60), (act_x, act_y), 2)
        # 3个面具转换（悲伤-中立-欢乐）
        mask_phase = int((t * 0.8) % 3)
        mask_expressions = [
            [(50, 55), (50, 65)],  # 悲伤（下弯嘴）
            [(50, 60), (70, 60)],  # 中立（直线）
            [(50, 65), (50, 55)]   # 欢乐（上弯嘴）
        ]
        # 左侧面具
        pygame.draw.circle(s, (220, 220, 220), (35, 60), 12)
        pygame.draw.circle(s, (50, 50, 50), (32, 57), 3)  # 左眼
        pygame.draw.circle(s, (50, 50, 50), (38, 57), 3)  # 右眼
        mouth_expr = mask_expressions[mask_phase]
        pygame.draw.line(s, (50, 50, 50), (30, mouth_expr[0][1]), (40, mouth_expr[1][1]), 2)
        # 右侧面具（相反表情）
        opposite_phase = (mask_phase + 2) % 3
        pygame.draw.circle(s, (220, 220, 220), (85, 60), 12)
        pygame.draw.circle(s, (50, 50, 50), (82, 57), 3)
        pygame.draw.circle(s, (50, 50, 50), (88, 57), 3)
        opp_expr = mask_expressions[opposite_phase]
        pygame.draw.line(s, (50, 50, 50), (80, opp_expr[0][1]), (90, opp_expr[1][1]), 2)
        # 聚光灯扫射（3束）
        for spot_i in range(3):
            spot_angle = (spot_i * 120 + t * 40) * 0.01745
            spot_len = 45
            spot_x = 60 + math.cos(spot_angle) * spot_len
            spot_y = 60 + math.sin(spot_angle) * spot_len
            spot_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(spot_surf, (255, 255, 200, 80), (60, 60), (spot_x, spot_y), 8)
            s.blit(spot_surf, (0, 0))
        # 中心舞台
        pygame.draw.circle(s, (200, 80, 100), (60, 60), 10)
        pygame.draw.circle(s, (180, 50, 80), (60, 60), 6)
        return s
    
    elif model_style == "chronos_chemical":
        # 化学反应·试管计时 - 实验室烧杯时钟，试剂变色，分子结构，反应泡泡
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 烧杯容器轮廓
        pygame.draw.ellipse(s, (100, 255, 180), (30, 50, 60, 40), 2)
        pygame.draw.line(s, (100, 255, 180), (35, 50), (35, 30), 2)
        pygame.draw.line(s, (100, 255, 180), (85, 50), (85, 30), 2)
        pygame.draw.line(s, (100, 255, 180), (35, 30), (85, 30), 2)
        # 液体颜色变化（化学反应）
        reaction_phase = (t * 1.5) % 1.0
        liquid_colors = [
            (100, 255, 180),
            (120, 255, 200),
            (80, 230, 160)
        ]
        liquid_color_index = int(reaction_phase * 3) % 3
        liquid_color = liquid_colors[liquid_color_index]
        liquid_level = 65 + int(5 * math.sin(t * 3))
        pygame.draw.ellipse(s, liquid_color, (32, liquid_level, 56, 25))
        # 24个分子键结构（环绕）
        for bond_i in range(24):
            bond_angle = (bond_i * 15 + t * 20) * 0.01745
            bond_r = 35
            bond_x = 60 + math.cos(bond_angle) * bond_r
            bond_y = 60 + math.sin(bond_angle) * bond_r
            # 原子节点
            pygame.draw.circle(s, (120, 255, 200), (int(bond_x), int(bond_y)), 3)
            # 化学键连接（每隔3个）
            if bond_i % 3 == 0:
                next_bond_angle = ((bond_i + 3) * 15 + t * 20) * 0.01745
                next_bond_x = 60 + math.cos(next_bond_angle) * bond_r
                next_bond_y = 60 + math.sin(next_bond_angle) * bond_r
                pygame.draw.line(s, (80, 230, 160), (bond_x, bond_y), 
                               (next_bond_x, next_bond_y), 1)
        # 40个反应泡泡（从中心冒出）
        for bubble_i in range(40):
            bubble_progress = ((t * 4 + bubble_i * 0.05) % 1.0)
            bubble_angle = (bubble_i * 9) * 0.01745
            bubble_r = 5 + int(bubble_progress * 40)
            bubble_x = 60 + math.cos(bubble_angle) * bubble_r
            bubble_y = 60 + math.sin(bubble_angle) * bubble_r
            bubble_size = int(3 * (1 - bubble_progress))
            if bubble_size > 0:
                bubble_alpha = int(180 * (1 - bubble_progress))
                pygame.draw.circle(s, (100, 255, 180, bubble_alpha), 
                                 (int(bubble_x), int(bubble_y)), bubble_size)
        # 中心反应核心
        pygame.draw.circle(s, (120, 255, 200), (60, 60), 10)
        pygame.draw.circle(s, (100, 255, 180), (60, 60), 6)
        return s
    
    elif model_style == "chronos_meteorological":
        # 气象预报·风云变幻 - 气象站时钟，天气图标，云图旋转，雨滴雪花
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 12个天气图标位置（环绕）
        weather_icons = [
            (255, 200, 100),  # 阳光
            (200, 200, 200),  # 阴天
            (100, 150, 255),  # 雨
            (255, 255, 255)   # 雪
        ]
        for icon_i in range(12):
            icon_angle = (icon_i * 30 + t * 8) * 0.01745
            icon_r = 40
            icon_x = 60 + math.cos(icon_angle) * icon_r
            icon_y = 60 + math.sin(icon_angle) * icon_r
            icon_color = weather_icons[icon_i % 4]
            # 简化图标（圆圈）
            pygame.draw.circle(s, icon_color, (int(icon_x), int(icon_y)), 5)
            if icon_i % 4 == 0:  # 阳光（射线）
                for ray in range(6):
                    ray_angle = (ray * 60) * 0.01745
                    ray_end_x = icon_x + math.cos(ray_angle) * 8
                    ray_end_y = icon_y + math.sin(ray_angle) * 8
                    pygame.draw.line(s, icon_color, (icon_x, icon_y), 
                                   (ray_end_x, ray_end_y), 1)
            elif icon_i % 4 == 2:  # 雨（下落线）
                for drop in range(3):
                    drop_y = icon_y + 5 + drop * 3
                    pygame.draw.line(s, icon_color, (icon_x, icon_y + 5), 
                                   (icon_x, drop_y), 1)
        # 8个云形成（卫星云图旋转）
        for cloud_i in range(8):
            cloud_angle = (cloud_i * 45 + t * 15) * 0.01745
            cloud_r = 28 + int(5 * math.sin(t * 2 + cloud_i))
            cloud_x = 60 + math.cos(cloud_angle) * cloud_r
            cloud_y = 60 + math.sin(cloud_angle) * cloud_r
            # 云朵形状（3个重叠圆）
            pygame.draw.circle(s, (180, 220, 255), (int(cloud_x) - 3, int(cloud_y)), 4)
            pygame.draw.circle(s, (180, 220, 255), (int(cloud_x) + 3, int(cloud_y)), 4)
            pygame.draw.circle(s, (180, 220, 255), (int(cloud_x), int(cloud_y) - 3), 5)
        # 气压计指针
        pressure_hand = (t * 12 - 90) * 0.01745
        phx = 60 + math.cos(pressure_hand) * 32
        phy = 60 + math.sin(pressure_hand) * 32
        pygame.draw.line(s, (150, 200, 255), (60, 60), (phx, phy), 3)
        # 中心温度计
        pygame.draw.circle(s, (180, 220, 255), (60, 60), 12)
        pygame.draw.circle(s, (150, 200, 255), (60, 60), 8)
        # 下落雨滴（20个）
        for rain_i in range(20):
            rain_progress = ((t * 3 + rain_i * 0.1) % 1.0)
            rain_x = 20 + (rain_i * 5) % 100
            rain_y = int(rain_progress * 120)
            pygame.draw.line(s, (100, 150, 255), (rain_x, rain_y), 
                           (rain_x, rain_y + 4), 1)
        return s
    
    elif model_style == "chronos_archaeological":
        # 考古发掘·文明密码 - 古文明遗迹时钟，象形文字，陶器碎片，分层挖掘
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 考古分层（5层土壤）
        strata_colors = [
            (200, 160, 100), (190, 150, 90),
            (180, 140, 80), (170, 130, 70),
            (160, 120, 60)
        ]
        for layer in range(5):
            layer_y = 25 + layer * 15
            layer_height = 15
            pygame.draw.rect(s, strata_colors[layer], 
                           (10, layer_y, 100, layer_height))
            # 土层纹理线
            for texture_line in range(3):
                line_y = layer_y + texture_line * 5
                pygame.draw.line(s, (180 - layer * 10, 140 - layer * 10, 80 - layer * 10),
                               (10, line_y), (110, line_y), 1)
        # 20个象形文字符号（环绕）
        hieroglyph_shapes = [
            [(0, -3), (0, 3)],        # 竖线
            [(-3, 0), (3, 0)],        # 横线
            [(-2, -2), (2, 2)],       # 斜线
            [(-2, 2), (2, -2)]        # 反斜
        ]
        for glyph_i in range(20):
            glyph_angle = (glyph_i * 18 + t * 5) * 0.01745
            glyph_r = 42
            glyph_x = 60 + math.cos(glyph_angle) * glyph_r
            glyph_y = 60 + math.sin(glyph_angle) * glyph_r
            shape = hieroglyph_shapes[glyph_i % 4]
            glyph_start = (glyph_x + shape[0][0], glyph_y + shape[0][1])
            glyph_end = (glyph_x + shape[1][0], glyph_y + shape[1][1])
            pygame.draw.line(s, (220, 180, 120), glyph_start, glyph_end, 2)
        # 16个陶器碎片（拼接）
        for shard_i in range(16):
            shard_angle = (shard_i * 22.5 + t * 8) * 0.01745
            shard_r = 30 + int(5 * math.sin(t + shard_i))
            shard_x = 60 + math.cos(shard_angle) * shard_r
            shard_y = 60 + math.sin(shard_angle) * shard_r
            # 碎片不规则四边形
            shard_points = [
                (shard_x - 3, shard_y - 2),
                (shard_x + 2, shard_y - 3),
                (shard_x + 3, shard_y + 2),
                (shard_x - 2, shard_y + 3)
            ]
            pygame.draw.polygon(s, (200, 160, 100), shard_points)
            pygame.draw.polygon(s, (180, 140, 80), shard_points, 1)
        # 中心文明核心（罗盘）
        pygame.draw.circle(s, (220, 180, 120), (60, 60), 15, 2)
        pygame.draw.circle(s, (200, 160, 100), (60, 60), 10)
        # 指针（挖掘进度）
        excavation_hand = (t * 6 - 90) * 0.01745
        ehx = 60 + math.cos(excavation_hand) * 28
        ehy = 60 + math.sin(excavation_hand) * 28
        pygame.draw.line(s, (180, 140, 80), (60, 60), (ehx, ehy), 3)
        return s
    
    return None
