# Puppeteer 专属涂装渲染模块
# 包含: puppeteer_gothic, puppeteer_music_box, puppeteer_voodoo, puppeteer_circus,
#       puppeteer_kabuki, puppeteer_clockwork, puppeteer_shadow, puppeteer_marionette,
#       puppeteer_porcelain, puppeteer_nightmare, puppeteer_eden, puppeteer_fate

import pygame
import math
import random

# Puppeteer涂装列表
PUPPETEER_STYLES = [
    "puppeteer_gothic", "puppeteer_music_box", "puppeteer_voodoo", "puppeteer_circus",
    "puppeteer_kabuki", "puppeteer_clockwork", "puppeteer_shadow", "puppeteer_marionette",
    "puppeteer_porcelain", "puppeteer_nightmare", "puppeteer_eden", "puppeteer_fate"
]

def is_puppeteer_style(model_style):
    """检查是否为Puppeteer涂装"""
    return model_style in PUPPETEER_STYLES

def render_puppeteer_skin(s, c, model_style, t, pid, static=False):
    """渲染Puppeteer涂装，返回Surface或None"""
    pulse = math.sin(t * 2) * 0.15 + 1
    
    if model_style == "puppeteer_gothic":
        # 哥特剧院·暗夜傀儡 - 维多利亚哥特风格，蜘蛛网+铁艺+红色天鹅绒
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 哥特铁艺蜘蛛网框架
        for web_ring in range(5):
            web_r = 15 + web_ring * 10
            pygame.draw.circle(s, (40, 20, 30), (60, 60), web_r, 1)
        for web_spoke in range(12):
            spoke_angle = (web_spoke * 30) * 0.01745
            sx = 60 + math.cos(spoke_angle) * 55
            sy = 60 + math.sin(spoke_angle) * 55
            pygame.draw.line(s, (50, 25, 35), (60, 60), (int(sx), int(sy)), 1)
        # 中央暗夜傀儡（吊在蛛网上）
        puppet_swing = math.sin(t * 2) * 8
        pcx = 60 + puppet_swing
        # 破碎瓷娃娃脸
        pygame.draw.circle(s, (220, 200, 190), (int(pcx), 45), 14)
        # 裂纹
        for crack in range(3):
            crack_angle = (crack * 60 + 30) * 0.01745
            cx1 = pcx + math.cos(crack_angle) * 5
            cy1 = 45 + math.sin(crack_angle) * 5
            cx2 = pcx + math.cos(crack_angle) * 14
            cy2 = 45 + math.sin(crack_angle) * 14
            pygame.draw.line(s, (80, 40, 50), (int(cx1), int(cy1)), (int(cx2), int(cy2)), 1)
        # 空洞眼睛（红色光点）
        eye_glow = int(200 + 55 * math.sin(t * 5))
        pygame.draw.circle(s, (eye_glow, 30, 30), (int(pcx) - 5, 43), 4)
        pygame.draw.circle(s, (eye_glow, 30, 30), (int(pcx) + 5, 43), 4)
        pygame.draw.circle(s, (255, 100, 100), (int(pcx) - 5, 43), 2)
        pygame.draw.circle(s, (255, 100, 100), (int(pcx) + 5, 43), 2)
        # 红色天鹅绒裙摆（波浪形）
        dress_points = [(int(pcx) - 12, 60)]
        for wave in range(8):
            wave_x = pcx - 12 + wave * 3
            wave_y = 85 + math.sin(t * 4 + wave) * 3
            dress_points.append((int(wave_x), int(wave_y)))
        dress_points.append((int(pcx) + 12, 60))
        pygame.draw.polygon(s, (120, 30, 50), dress_points)
        # 悬挂丝线（蜘蛛丝质感）
        for thread_i in range(5):
            thread_x = pcx - 8 + thread_i * 4
            thread_sway = math.sin(t * 3 + thread_i) * 2
            pygame.draw.line(s, (80, 80, 90), (int(thread_x + thread_sway), 10), (int(thread_x), 45 - 14), 1)
        # 飘落的蜘蛛（3只）
        for spider_i in range(3):
            spider_y = ((t * 20 + spider_i * 40) % 80) + 20
            spider_x = 20 + spider_i * 40 + math.sin(t * 2 + spider_i) * 5
            pygame.draw.circle(s, (30, 20, 25), (int(spider_x), int(spider_y)), 3)
            for leg in range(4):
                leg_angle = (leg * 45 + 22.5) * 0.01745
                lx = spider_x + math.cos(leg_angle) * 5
                ly = spider_y + math.sin(leg_angle) * 5
                pygame.draw.line(s, (30, 20, 25), (int(spider_x), int(spider_y)), (int(lx), int(ly)), 1)
        return s
    
    elif model_style == "puppeteer_music_box":
        # 八音盒·永恒旋律 - 精美八音盒，瓷娃娃芭蕾舞者
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 八音盒底座（金色装饰边框）
        pygame.draw.rect(s, (60, 40, 30), (20, 70, 80, 35), border_radius=5)
        pygame.draw.rect(s, (200, 160, 80), (20, 70, 80, 35), 2, border_radius=5)
        # 金色花纹装饰
        for deco_i in range(6):
            deco_x = 28 + deco_i * 12
            pygame.draw.circle(s, (220, 180, 100), (deco_x, 85), 3)
        # 旋转齿轮（内部机械）
        gear_angle = t * 60
        for gear_i in range(8):
            g_angle = (gear_i * 45 + gear_angle) * 0.01745
            gx = 60 + math.cos(g_angle) * 25
            gy = 87 + math.sin(g_angle) * 8
            pygame.draw.circle(s, (180, 140, 60), (int(gx), int(gy)), 2)
        # 芭蕾舞者瓷娃娃（旋转）
        dancer_angle = t * 90
        dancer_cx = 60
        dancer_cy = 50
        # 旋转的裙摆（圆锥形）
        for skirt_layer in range(3):
            skirt_r = 12 + skirt_layer * 4
            skirt_y = 55 + skirt_layer * 3
            skirt_points = []
            for skirt_seg in range(16):
                seg_angle = (skirt_seg * 22.5 + dancer_angle) * 0.01745
                wave = math.sin(seg_angle * 4) * 2
                sx = dancer_cx + math.cos(seg_angle) * (skirt_r + wave)
                sy = skirt_y + math.sin(seg_angle) * 3
                skirt_points.append((int(sx), int(sy)))
            pygame.draw.polygon(s, (255, 200, 220), skirt_points)
            pygame.draw.polygon(s, (220, 170, 190), skirt_points, 1)
        # 瓷娃娃上身
        pygame.draw.ellipse(s, (255, 240, 235), (dancer_cx - 6, 40, 12, 18))
        # 瓷娃娃头（精致）
        pygame.draw.circle(s, (255, 245, 240), (dancer_cx, 32), 10)
        # 腮红
        pygame.draw.circle(s, (255, 180, 180), (dancer_cx - 5, 34), 3)
        pygame.draw.circle(s, (255, 180, 180), (dancer_cx + 5, 34), 3)
        # 闭眼（弧线）
        pygame.draw.arc(s, (60, 40, 40), (dancer_cx - 7, 28, 6, 6), 0, 3.14159, 2)
        pygame.draw.arc(s, (60, 40, 40), (dancer_cx + 1, 28, 6, 6), 0, 3.14159, 2)
        # 举起的手臂
        arm_l_angle = math.sin(t * 2) * 0.3 - 1.2
        arm_r_angle = math.sin(t * 2 + 1) * 0.3 + 1.2 - 3.14159
        arm_l_x = dancer_cx + math.cos(arm_l_angle) * 15
        arm_l_y = 45 + math.sin(arm_l_angle) * 15
        arm_r_x = dancer_cx + math.cos(arm_r_angle) * 15
        arm_r_y = 45 + math.sin(arm_r_angle) * 15
        pygame.draw.line(s, (255, 240, 235), (dancer_cx - 5, 45), (int(arm_l_x), int(arm_l_y)), 3)
        pygame.draw.line(s, (255, 240, 235), (dancer_cx + 5, 45), (int(arm_r_x), int(arm_r_y)), 3)
        # 音符粒子飘出
        for note_i in range(8):
            note_phase = ((t * 1.5 + note_i * 0.3) % 1.0)
            note_angle = (note_i * 45 + t * 20) * 0.01745
            note_r = 30 + note_phase * 25
            note_x = 60 + math.cos(note_angle) * note_r
            note_y = 50 + math.sin(note_angle) * note_r - note_phase * 20
            note_alpha = int(200 * (1 - note_phase))
            if note_alpha > 0:
                note_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(note_surf, (220, 180, 100, note_alpha), (int(note_x), int(note_y)), 3)
                pygame.draw.line(note_surf, (220, 180, 100, note_alpha), (int(note_x) + 3, int(note_y)), (int(note_x) + 3, int(note_y) - 8), 1)
                s.blit(note_surf, (0, 0))
        return s
    
    elif model_style == "puppeteer_voodoo":
        # 巫毒咒术·灵魂缝针 - 麻布巫毒娃娃，针和符文
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 麻布背景纹理
        for fiber_i in range(20):
            fiber_x = random.randint(20, 100)
            fiber_y = random.randint(20, 100)
            pygame.draw.line(s, (120, 100, 70), (fiber_x, fiber_y), (fiber_x + random.randint(-10, 10), fiber_y + random.randint(-10, 10)), 1)
        # 巫毒娃娃主体（粗糙麻布质感）
        body_points = [(60, 25), (75, 35), (80, 55), (70, 90), (50, 90), (40, 55), (45, 35)]
        pygame.draw.polygon(s, (160, 140, 100), body_points)
        pygame.draw.polygon(s, (100, 80, 50), body_points, 2)
        # 缝合线（X形针脚）
        stitch_positions = [(55, 40), (65, 40), (50, 60), (70, 60), (55, 75), (65, 75)]
        for sx, sy in stitch_positions:
            pygame.draw.line(s, (80, 60, 40), (sx - 3, sy - 3), (sx + 3, sy + 3), 2)
            pygame.draw.line(s, (80, 60, 40), (sx - 3, sy + 3), (sx + 3, sy - 3), 2)
        # 纽扣眼睛
        pygame.draw.circle(s, (40, 30, 20), (52, 35), 5)
        pygame.draw.circle(s, (40, 30, 20), (68, 35), 5)
        pygame.draw.line(s, (80, 60, 40), (49, 32), (55, 38), 1)
        pygame.draw.line(s, (80, 60, 40), (49, 38), (55, 32), 1)
        pygame.draw.line(s, (80, 60, 40), (65, 32), (71, 38), 1)
        pygame.draw.line(s, (80, 60, 40), (65, 38), (71, 32), 1)
        # 扎入的针（动态抖动）
        for pin_i in range(5):
            pin_x = 45 + pin_i * 8
            pin_y = 50 + math.sin(t * 8 + pin_i) * 2
            pin_angle = (pin_i * 15 - 30) * 0.01745
            pin_end_x = pin_x + math.cos(pin_angle) * 20
            pin_end_y = pin_y + math.sin(pin_angle) * 20 - 15
            pygame.draw.line(s, (180, 180, 190), (pin_x, int(pin_y)), (int(pin_end_x), int(pin_end_y)), 2)
            pygame.draw.circle(s, (255, 50, 50), (int(pin_end_x), int(pin_end_y) - 3), 3)
        # 诅咒符文环绕
        for rune_i in range(6):
            rune_angle = (rune_i * 60 + t * 25) * 0.01745
            rune_r = 50
            rune_x = 60 + math.cos(rune_angle) * rune_r
            rune_y = 60 + math.sin(rune_angle) * rune_r
            rune_alpha = int(150 + 80 * math.sin(t * 4 + rune_i))
            rune_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(rune_surf, (200, 100, 50, rune_alpha), (int(rune_x), int(rune_y)), 6, 2)
            pygame.draw.line(rune_surf, (200, 100, 50, rune_alpha), (int(rune_x) - 4, int(rune_y)), (int(rune_x) + 4, int(rune_y)), 1)
            pygame.draw.line(rune_surf, (200, 100, 50, rune_alpha), (int(rune_x), int(rune_y) - 4), (int(rune_x), int(rune_y) + 4), 1)
            s.blit(rune_surf, (0, 0))
        return s
    
    elif model_style == "puppeteer_circus":
        # 暗黑马戏·疯狂大帐 - 恐怖马戏团，小丑傀儡
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 马戏团帐篷条纹（红白染血）
        for stripe_i in range(12):
            stripe_angle = (stripe_i * 30) * 0.01745
            stripe_color = (200, 50, 50) if stripe_i % 2 == 0 else (240, 230, 220)
            if stripe_i % 3 == 0:
                stripe_color = (150, 30, 30)
            stripe_points = [(60, 15)]
            sx1 = 60 + math.cos(stripe_angle - 0.13) * 50
            sy1 = 60 + math.sin(stripe_angle - 0.13) * 50
            sx2 = 60 + math.cos(stripe_angle + 0.13) * 50
            sy2 = 60 + math.sin(stripe_angle + 0.13) * 50
            stripe_points.extend([(int(sx1), int(sy1)), (int(sx2), int(sy2))])
            pygame.draw.polygon(s, stripe_color, stripe_points)
        # 中央疯狂小丑傀儡
        clown_bounce = abs(math.sin(t * 6)) * 5
        clown_y = 50 - clown_bounce
        pygame.draw.circle(s, (255, 255, 255), (60, int(clown_y)), 12)
        pygame.draw.circle(s, (255, 0, 0), (60, int(clown_y) + 2), 4)
        left_eye_x = 55 + math.sin(t * 10) * 2
        right_eye_x = 65 + math.cos(t * 10) * 2
        pygame.draw.circle(s, (0, 0, 0), (int(left_eye_x), int(clown_y) - 3), 4)
        pygame.draw.circle(s, (0, 0, 0), (int(right_eye_x), int(clown_y) - 3), 3)
        pygame.draw.circle(s, (255, 255, 0), (int(left_eye_x), int(clown_y) - 3), 2)
        pygame.draw.circle(s, (255, 0, 0), (int(right_eye_x), int(clown_y) - 3), 1)
        smile_points = [(52, int(clown_y) + 5)]
        for sm in range(5):
            sm_x = 52 + sm * 4
            sm_y = clown_y + 8 + math.sin(t * 8 + sm) * 2
            smile_points.append((sm_x, int(sm_y)))
        smile_points.append((68, int(clown_y) + 5))
        pygame.draw.lines(s, (200, 0, 0), False, smile_points, 2)
        hat_points = [(50, int(clown_y) - 10), (60, int(clown_y) - 30), (70, int(clown_y) - 10)]
        pygame.draw.polygon(s, (200, 50, 50), hat_points)
        pygame.draw.polygon(s, (255, 215, 0), hat_points, 2)
        bell_swing = math.sin(t * 8) * 5
        pygame.draw.circle(s, (255, 215, 0), (60 + int(bell_swing), int(clown_y) - 32), 4)
        for bg_clown in range(3):
            bg_x = 25 + bg_clown * 35
            bg_y = 80 + math.sin(t * 2 + bg_clown) * 5
            bg_alpha = 100
            bg_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(bg_surf, (255, 255, 255, bg_alpha), (bg_x, int(bg_y)), 6)
            pygame.draw.circle(bg_surf, (255, 0, 0, bg_alpha), (bg_x, int(bg_y) + 1), 2)
            s.blit(bg_surf, (0, 0))
        return s
    
    elif model_style == "puppeteer_kabuki":
        # 歌舞伎·能面之舞 - 日本歌舞伎，能面具，和服丝线
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.rect(s, (250, 245, 235), (15, 15, 90, 90))
        for paper_line in range(10):
            pygame.draw.line(s, (240, 230, 220), (15, 15 + paper_line * 10), (105, 15 + paper_line * 10), 1)
        mask_sway = math.sin(t * 1.5) * 3
        mask_cx = 60 + mask_sway
        mask_points = [(int(mask_cx), 25), (int(mask_cx) + 20, 40), (int(mask_cx) + 18, 65), 
                      (int(mask_cx), 75), (int(mask_cx) - 18, 65), (int(mask_cx) - 20, 40)]
        pygame.draw.polygon(s, (255, 250, 245), mask_points)
        pygame.draw.polygon(s, (200, 50, 50), mask_points, 2)
        pygame.draw.arc(s, (20, 20, 20), (int(mask_cx) - 15, 38, 12, 8), 0.5, 2.6, 2)
        pygame.draw.arc(s, (20, 20, 20), (int(mask_cx) + 3, 38, 12, 8), 0.5, 2.6, 2)
        pygame.draw.ellipse(s, (200, 50, 50), (int(mask_cx) - 6, 58, 12, 6))
        pygame.draw.circle(s, (200, 50, 50), (int(mask_cx), 32), 4)
        for silk_i in range(7):
            silk_x = 35 + silk_i * 8
            silk_wave = math.sin(t * 2 + silk_i * 0.5) * 3
            silk_points = []
            for silk_seg in range(8):
                seg_y = 75 + silk_seg * 5
                seg_x = silk_x + math.sin(t * 3 + silk_seg * 0.3) * silk_wave
                silk_points.append((int(seg_x), seg_y))
            if len(silk_points) > 1:
                silk_color = (200, 50, 50) if silk_i % 2 == 0 else (255, 215, 100)
                pygame.draw.lines(s, silk_color, False, silk_points, 2)
        for sakura_i in range(8):
            sakura_phase = ((t * 0.8 + sakura_i * 0.2) % 1.0)
            sakura_x = 20 + sakura_i * 12 + math.sin(t * 2 + sakura_i) * 10
            sakura_y = sakura_phase * 120
            sakura_rot = t * 100 + sakura_i * 45
            sakura_alpha = int(200 * (1 - abs(sakura_phase - 0.5) * 2))
            if sakura_alpha > 0:
                sakura_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                petal_points = []
                for p in range(5):
                    p_angle = (p * 72 + sakura_rot) * 0.01745
                    p_r = 4 if p % 2 == 0 else 2
                    px = sakura_x + math.cos(p_angle) * p_r
                    py = sakura_y + math.sin(p_angle) * p_r
                    petal_points.append((int(px), int(py)))
                pygame.draw.polygon(sakura_surf, (255, 180, 200, sakura_alpha), petal_points)
                s.blit(sakura_surf, (0, 0))
        return s
    
    elif model_style == "puppeteer_clockwork":
        # 发条心脏·机械少女 - 蒸汽朋克发条人偶
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(s, (180, 140, 80), (60, 60), 50)
        pygame.draw.circle(s, (200, 160, 100), (60, 60), 50, 3)
        gear_configs = [(60, 60, 35, 12, 1), (35, 45, 15, 8, -1.5), (85, 45, 15, 8, 1.5),
                       (45, 80, 12, 6, -2), (75, 80, 12, 6, 2)]
        for gx, gy, gr, teeth, speed in gear_configs:
            gear_rot = t * 30 * speed
            pygame.draw.circle(s, (160, 120, 60), (gx, gy), gr)
            pygame.draw.circle(s, (200, 160, 100), (gx, gy), gr, 2)
            for tooth in range(teeth):
                tooth_angle = (tooth * 360 / teeth + gear_rot) * 0.01745
                tx1 = gx + math.cos(tooth_angle) * gr
                ty1 = gy + math.sin(tooth_angle) * gr
                tx2 = gx + math.cos(tooth_angle) * (gr + 5)
                ty2 = gy + math.sin(tooth_angle) * (gr + 5)
                pygame.draw.line(s, (200, 160, 100), (int(tx1), int(ty1)), (int(tx2), int(ty2)), 3)
            pygame.draw.circle(s, (100, 80, 40), (gx, gy), gr // 3)
        pygame.draw.circle(s, (220, 200, 180), (60, 40), 12)
        key_angle = t * 60
        key_x = 60 + math.cos(key_angle * 0.01745) * 8
        key_y = 40 + math.sin(key_angle * 0.01745) * 8
        pygame.draw.rect(s, (200, 160, 100), (int(key_x) - 2, 15, 4, 20))
        pygame.draw.circle(s, (200, 160, 100), (int(key_x), 12), 6, 2)
        for steam_i in range(10):
            steam_phase = ((t * 3 + steam_i * 0.2) % 1.0)
            steam_x = 60 + (random.random() - 0.5) * 20
            steam_y = 20 - steam_phase * 30
            steam_alpha = int(150 * (1 - steam_phase))
            steam_size = int(5 * steam_phase + 2)
            if steam_alpha > 0 and steam_y > 0:
                steam_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(steam_surf, (200, 200, 200, steam_alpha), (int(steam_x), int(steam_y)), steam_size)
                s.blit(steam_surf, (0, 0))
        return s
    
    elif model_style == "puppeteer_shadow":
        # 影子戏·剪影物语 - 中国皮影戏，半透明剪影
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        for light_ring in range(10):
            light_r = 55 - light_ring * 5
            light_alpha = 50 + light_ring * 10
            pygame.draw.circle(s, (255, 220, 150, light_alpha), (60, 60), light_r)
        shadow_sway = math.sin(t * 2) * 5
        shadow_cx = 60 + shadow_sway
        shadow_color = (80, 40, 20, 200)
        shadow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        head_points = [(int(shadow_cx), 25), (int(shadow_cx) + 10, 30), (int(shadow_cx) + 8, 45),
                      (int(shadow_cx) - 8, 45), (int(shadow_cx) - 10, 30)]
        pygame.draw.polygon(shadow_surf, shadow_color, head_points)
        for feather in range(3):
            f_angle = (-30 + feather * 30 + math.sin(t * 3) * 10) * 0.01745
            fx = shadow_cx + math.cos(f_angle) * 15
            fy = 25 + math.sin(f_angle) * 15 - 10
            pygame.draw.line(shadow_surf, (200, 100, 50, 180), (int(shadow_cx), 25), (int(fx), int(fy)), 2)
        body_points = [(int(shadow_cx) - 8, 45), (int(shadow_cx) + 8, 45),
                      (int(shadow_cx) + 12, 80), (int(shadow_cx) - 12, 80)]
        pygame.draw.polygon(shadow_surf, shadow_color, body_points)
        arm_angle = math.sin(t * 3) * 0.5
        left_arm_end = (shadow_cx - 20 + math.cos(arm_angle - 2) * 15, 55 + math.sin(arm_angle - 2) * 15)
        right_arm_end = (shadow_cx + 20 + math.cos(arm_angle + 1) * 15, 55 + math.sin(arm_angle + 1) * 15)
        pygame.draw.line(shadow_surf, shadow_color, (int(shadow_cx) - 8, 50), (int(left_arm_end[0]), int(left_arm_end[1])), 4)
        pygame.draw.line(shadow_surf, shadow_color, (int(shadow_cx) + 8, 50), (int(right_arm_end[0]), int(right_arm_end[1])), 4)
        spear_end = (right_arm_end[0] + 25, right_arm_end[1] - 30)
        pygame.draw.line(shadow_surf, (100, 60, 30, 200), (int(right_arm_end[0]), int(right_arm_end[1])), (int(spear_end[0]), int(spear_end[1])), 3)
        s.blit(shadow_surf, (0, 0))
        for rod in range(3):
            rod_x = 30 + rod * 30
            rod_alpha = 100 + int(50 * math.sin(t * 2 + rod))
            pygame.draw.line(s, (150, 120, 80, rod_alpha), (rod_x, 100), (rod_x, 120), 2)
        return s
    
    elif model_style == "puppeteer_marionette":
        # 提线精灵·星辰丝网 - 银色星光丝线，水晶傀儡
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        for star_i in range(30):
            star_x = random.randint(10, 110)
            star_y = random.randint(10, 110)
            star_twinkle = int(150 + 100 * math.sin(t * 5 + star_i))
            pygame.draw.circle(s, (200, 220, 255, star_twinkle), (star_x, star_y), 1)
        crystal_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        crystal_sway = math.sin(t * 2) * 3
        crystal_cx = 60 + crystal_sway
        head_facets = []
        for facet in range(6):
            f_angle = (facet * 60 + t * 20) * 0.01745
            fx = crystal_cx + math.cos(f_angle) * 10
            fy = 40 + math.sin(f_angle) * 10
            head_facets.append((int(fx), int(fy)))
        pygame.draw.polygon(crystal_surf, (200, 220, 255, 180), head_facets)
        pygame.draw.polygon(crystal_surf, (255, 255, 255, 200), head_facets, 2)
        body_facets = [(int(crystal_cx) - 10, 50), (int(crystal_cx) + 10, 50),
                      (int(crystal_cx) + 8, 80), (int(crystal_cx), 90), (int(crystal_cx) - 8, 80)]
        pygame.draw.polygon(crystal_surf, (180, 200, 255, 150), body_facets)
        pygame.draw.polygon(crystal_surf, (220, 240, 255, 200), body_facets, 2)
        s.blit(crystal_surf, (0, 0))
        thread_points = [(60, 10), (crystal_cx, 30), (40, 15), (crystal_cx - 15, 55),
                        (80, 15), (crystal_cx + 15, 55), (50, 12), (crystal_cx - 5, 85), (70, 12), (crystal_cx + 5, 85)]
        for i in range(0, len(thread_points), 2):
            thread_alpha = int(200 + 55 * math.sin(t * 8 + i))
            thread_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(thread_surf, (220, 230, 255, thread_alpha), 
                           (int(thread_points[i][0]), int(thread_points[i][1])),
                           (int(thread_points[i+1][0]), int(thread_points[i+1][1])), 1)
            for star_pos in range(3):
                star_t = star_pos / 3
                sx = thread_points[i][0] + (thread_points[i+1][0] - thread_points[i][0]) * star_t
                sy = thread_points[i][1] + (thread_points[i+1][1] - thread_points[i][1]) * star_t
                star_pulse = int(200 + 55 * math.sin(t * 10 + i + star_pos))
                pygame.draw.circle(thread_surf, (255, 255, 255, star_pulse), (int(sx), int(sy)), 2)
            s.blit(thread_surf, (0, 0))
        return s
    
    elif model_style == "puppeteer_porcelain":
        # 瓷器人偶·碎裂之美 - 青花瓷娃娃，金缮修复
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (240, 245, 250), (30, 85, 60, 20))
        pygame.draw.ellipse(s, (50, 80, 150), (30, 85, 60, 20), 2)
        pygame.draw.ellipse(s, (250, 252, 255), (45, 45, 30, 45))
        for pattern in range(5):
            p_angle = (pattern * 72 + 20) * 0.01745
            px = 60 + math.cos(p_angle) * 10
            py = 65 + math.sin(p_angle) * 15
            pygame.draw.circle(s, (50, 80, 150), (int(px), int(py)), 3, 1)
        pygame.draw.circle(s, (250, 252, 255), (60, 35), 15)
        pygame.draw.circle(s, (50, 80, 150), (54, 33), 3)
        pygame.draw.circle(s, (50, 80, 150), (66, 33), 3)
        crack_paths = [[(45, 30), (50, 40), (48, 55)], [(70, 25), (75, 35), (72, 50)], [(55, 60), (60, 75), (58, 88)]]
        for crack_path in crack_paths:
            pygame.draw.lines(s, (80, 80, 80), False, crack_path, 1)
            gold_glow = int(200 + 55 * math.sin(t * 3))
            for i in range(len(crack_path) - 1):
                pygame.draw.line(s, (gold_glow, int(gold_glow * 0.7), 50), crack_path[i], crack_path[i+1], 2)
        for shard_i in range(4):
            shard_phase = ((t * 0.5 + shard_i * 0.3) % 1.0)
            shard_x = 30 + shard_i * 20 + math.sin(t + shard_i) * 10
            shard_y = shard_phase * 100 + 10
            shard_rot = t * 100 + shard_i * 90
            shard_alpha = int(200 * (1 - shard_phase))
            if shard_alpha > 0:
                shard_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                shard_points = []
                for sp in range(3):
                    sp_angle = (sp * 120 + shard_rot) * 0.01745
                    spx = shard_x + math.cos(sp_angle) * 5
                    spy = shard_y + math.sin(sp_angle) * 5
                    shard_points.append((int(spx), int(spy)))
                pygame.draw.polygon(shard_surf, (250, 252, 255, shard_alpha), shard_points)
                pygame.draw.polygon(shard_surf, (220, 180, 50, shard_alpha), shard_points, 1)
                s.blit(shard_surf, (0, 0))
        return s
    
    elif model_style == "puppeteer_nightmare":
        # 噩梦编织·深渊之弦 - 恐惧深渊，扭曲丝线连接眼睛
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        for void_ring in range(8):
            void_r = 55 - void_ring * 6
            void_alpha = 30 + void_ring * 15
            pygame.draw.circle(s, (20, 0, 40, void_alpha), (60, 60), void_r)
        eye_pulse = abs(math.sin(t * 2))
        eye_size = int(20 + eye_pulse * 5)
        pygame.draw.circle(s, (100, 0, 60), (60, 60), eye_size)
        pygame.draw.circle(s, (200, 50, 100), (60, 60), eye_size - 5)
        pygame.draw.circle(s, (0, 0, 0), (60, 60), eye_size - 12)
        pupil_x = 60 + math.sin(t * 1.5) * 3
        pupil_y = 60 + math.cos(t * 1.5) * 3
        pygame.draw.circle(s, (255, 0, 100), (int(pupil_x), int(pupil_y)), 3)
        for string_i in range(12):
            string_angle = (string_i * 30 + t * 15) * 0.01745
            string_points = [(60, 60)]
            for seg in range(6):
                seg_r = 20 + seg * 8
                seg_angle = string_angle + math.sin(t * 4 + seg) * 0.3
                sx = 60 + math.cos(seg_angle) * seg_r
                sy = 60 + math.sin(seg_angle) * seg_r
                string_points.append((int(sx), int(sy)))
            string_alpha = int(150 + 80 * math.sin(t * 5 + string_i))
            string_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            if len(string_points) > 1:
                pygame.draw.lines(string_surf, (150, 50, 100, string_alpha), False, string_points, 2)
            s.blit(string_surf, (0, 0))
            end_x, end_y = string_points[-1]
            pygame.draw.circle(s, (200, 50, 100), (end_x, end_y), 4)
            pygame.draw.circle(s, (0, 0, 0), (end_x, end_y), 2)
        return s
    
    elif model_style == "puppeteer_eden":
        # 伊甸傀儡·禁果之弦 - 伊甸园蛇与苹果，神圣与堕落
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        halo_pulse = abs(math.sin(t * 2))
        for halo in range(3):
            halo_r = 50 - halo * 10
            halo_alpha = int(50 + 30 * halo_pulse)
            pygame.draw.circle(s, (255, 230, 150, halo_alpha), (60, 60), halo_r)
        pygame.draw.line(s, (100, 70, 40), (60, 90), (60, 40), 4)
        for branch in range(4):
            b_angle = (-60 + branch * 40) * 0.01745
            bx = 60 + math.cos(b_angle) * 20
            by = 50 + math.sin(b_angle) * 15
            pygame.draw.line(s, (100, 70, 40), (60, 55 - branch * 5), (int(bx), int(by)), 2)
        apple_glow = int(200 + 55 * math.sin(t * 4))
        pygame.draw.circle(s, (apple_glow, 30, 30), (75, 45), 8)
        pygame.draw.circle(s, (255, 50, 50), (75, 45), 6)
        for ray in range(6):
            ray_angle = (ray * 60 + t * 30) * 0.01745
            ray_end_x = 75 + math.cos(ray_angle) * 15
            ray_end_y = 45 + math.sin(ray_angle) * 15
            ray_alpha = int(100 + 50 * math.sin(t * 6 + ray))
            ray_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(ray_surf, (255, 200, 100, ray_alpha), (75, 45), (int(ray_end_x), int(ray_end_y)), 1)
            s.blit(ray_surf, (0, 0))
        snake_points = []
        for snake_seg in range(20):
            snake_t = snake_seg / 20
            snake_y = 85 - snake_t * 50
            snake_x = 60 + math.sin(snake_t * 6 + t * 3) * 10
            snake_points.append((int(snake_x), int(snake_y)))
        if len(snake_points) > 1:
            pygame.draw.lines(s, (50, 100, 50), False, snake_points, 3)
        snake_head_x, snake_head_y = snake_points[-1]
        pygame.draw.circle(s, (60, 120, 60), (snake_head_x, snake_head_y), 5)
        pygame.draw.circle(s, (255, 50, 50), (snake_head_x - 2, snake_head_y - 1), 2)
        pygame.draw.circle(s, (255, 50, 50), (snake_head_x + 2, snake_head_y - 1), 2)
        for feather_i in range(5):
            feather_phase = ((t * 0.3 + feather_i * 0.25) % 1.0)
            feather_x = 20 + feather_i * 20 + math.sin(t + feather_i) * 8
            feather_y = feather_phase * 110 + 5
            feather_alpha = int(180 * (1 - feather_phase))
            if feather_alpha > 0:
                feather_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                f_points = [(int(feather_x), int(feather_y) - 6), 
                           (int(feather_x) - 3, int(feather_y) + 6),
                           (int(feather_x) + 3, int(feather_y) + 6)]
                pygame.draw.polygon(feather_surf, (255, 255, 255, feather_alpha), f_points)
                s.blit(feather_surf, (0, 0))
        return s
    
    elif model_style == "puppeteer_fate":
        # 命运纺车·三女神 - 希腊命运三女神，纺锤、量尺、剪刀
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        wheel_rot = t * 10
        pygame.draw.circle(s, (60, 50, 80), (60, 60), 50, 2)
        for spoke in range(12):
            spoke_angle = (spoke * 30 + wheel_rot) * 0.01745
            sx = 60 + math.cos(spoke_angle) * 50
            sy = 60 + math.sin(spoke_angle) * 50
            pygame.draw.line(s, (80, 70, 100), (60, 60), (int(sx), int(sy)), 1)
        symbols_angle = t * 20
        spindle_angle = (symbols_angle) * 0.01745
        spindle_x = 60 + math.cos(spindle_angle) * 35
        spindle_y = 60 + math.sin(spindle_angle) * 35
        pygame.draw.ellipse(s, (200, 180, 220), (int(spindle_x) - 4, int(spindle_y) - 10, 8, 20))
        for thread in range(8):
            thread_angle = (thread * 45 + t * 50) * 0.01745
            tx = spindle_x + math.cos(thread_angle) * (8 + thread * 2)
            ty = spindle_y + math.sin(thread_angle) * (8 + thread * 2)
            thread_alpha = 200 - thread * 20
            thread_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(thread_surf, (180, 150, 200, thread_alpha), (int(spindle_x), int(spindle_y)), (int(tx), int(ty)), 1)
            s.blit(thread_surf, (0, 0))
        ruler_angle = (symbols_angle + 120) * 0.01745
        ruler_x = 60 + math.cos(ruler_angle) * 35
        ruler_y = 60 + math.sin(ruler_angle) * 35
        pygame.draw.rect(s, (220, 200, 180), (int(ruler_x) - 12, int(ruler_y) - 3, 24, 6))
        for mark in range(5):
            mark_x = ruler_x - 10 + mark * 5
            pygame.draw.line(s, (100, 80, 60), (int(mark_x), int(ruler_y) - 3), (int(mark_x), int(ruler_y) + 3), 1)
        scissors_angle = (symbols_angle + 240) * 0.01745
        scissors_x = 60 + math.cos(scissors_angle) * 35
        scissors_y = 60 + math.sin(scissors_angle) * 35
        scissors_open = abs(math.sin(t * 4)) * 0.3
        pygame.draw.line(s, (180, 180, 200), (int(scissors_x), int(scissors_y)), 
                       (int(scissors_x) - 8, int(scissors_y) - 12 + scissors_open * 20), 3)
        pygame.draw.line(s, (180, 180, 200), (int(scissors_x), int(scissors_y)), 
                       (int(scissors_x) + 8, int(scissors_y) - 12 - scissors_open * 20), 3)
        pygame.draw.circle(s, (150, 150, 170), (int(scissors_x), int(scissors_y)), 4)
        pygame.draw.circle(s, (150, 130, 180), (60, 60), 12)
        pygame.draw.circle(s, (200, 180, 220), (60, 60), 8)
        return s
    
    return None
