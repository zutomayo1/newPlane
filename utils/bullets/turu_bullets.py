# -*- coding: utf-8 -*-
"""
Turu 战机子弹涂装效果渲染模块 - 巨石核拳·图鲁专属

包含以下子弹效果：
- rock_fist: 岩核飞拳 - 穿透2次，命中后爆裂成岩块AOE
- rock_debris: 岩块碎片 - AOE爆裂产生的碎片
- meteor_fist: 巨型岩核拳 - F大招的巨型拳头
- rock_wall: 岩壁碎片 - G大招岩壁碎片
- tremor_wave: 震荡波 - C大招的冲击波

三大招:
- F键「岩拳暴雨」: 2秒内连射6枚巨型岩核拳，穿透无限且每过1屏体积+20%
- G键「巨石护盾」: 展开环形岩壁（持续4s），抵挡前方弹幕，壁碎时向外爆炸造成真伤
- C键「图鲁跃砸」: 远程定位跳跃砸地，震荡波击飞+减速场内敌人，回跳原位（无敌0.8s）
"""
import pygame
import math
import random
from config import all_sprites, mobs, enemy_bullets, bullets, WIDTH, HEIGHT


def render_turu_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Turu战机的子弹效果 - 巨石核拳级别特效（至尊品质）
    
    Args:
        surface: pygame绘图表面
        effects: 效果列表
        color: 主题颜色
        center_x, center_y: 中心坐标
        size: 子弹大小
        x, y: 左上角坐标
    
    Returns:
        bool: 如果渲染了效果返回True，否则False
    """
    t = pygame.time.get_ticks() / 1000.0
    
    # 图鲁配色
    rock_gray = (120, 115, 110)
    rock_dark = (70, 65, 60)
    core_orange = (255, 120, 40)
    core_bright = (255, 180, 100)
    crack_glow = (255, 160, 60)
    debris_brown = (130, 95, 65)
    
    if "rock_fist" in effects:
        # 岩核飞拳 - 至尊品质巨石拳头
        bullet_surf = pygame.Surface((size*2 + 20, size*2 + 20), pygame.SRCALPHA)
        cx, cy = size + 10, size + 10
        
        # 多层能量光晕
        for i in range(4):
            glow_r = int(size * 0.6) + 8 - i * 3 + int(abs(math.sin(t * 4)) * 3)
            glow_alpha = 90 - i * 20
            pygame.draw.circle(bullet_surf, (*core_orange, glow_alpha), (cx, cy), glow_r)
        
        # 拳头阴影
        shadow_points = []
        for i in range(10):
            angle = i * 36 * 0.01745
            r = size * 0.4 + random.Random(i + 5).randint(-2, 3)
            shadow_points.append((int(cx + math.cos(angle) * r + 2), int(cy + math.sin(angle) * r + 2)))
        pygame.draw.polygon(bullet_surf, (40, 35, 30), shadow_points)
        
        # 拳头主体（不规则岩块）
        fist_points = []
        for i in range(10):
            angle = i * 36 * 0.01745
            r = size * 0.38 + random.Random(i + 5).randint(-2, 4)
            fist_points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
        pygame.draw.polygon(bullet_surf, rock_gray, fist_points)
        pygame.draw.polygon(bullet_surf, rock_dark, fist_points, 2)
        
        # 岩石纹理层
        for layer in range(2):
            inner_r = size * (0.25 - layer * 0.08)
            for i in range(6):
                angle = (i * 60 + layer * 30) * 0.01745
                ix = cx + math.cos(angle) * inner_r
                iy = cy + math.sin(angle) * inner_r
                pygame.draw.circle(bullet_surf, rock_dark, (int(ix), int(iy)), 2)
        
        # 核心裂纹发光网络
        crack_surf = pygame.Surface((size*2 + 20, size*2 + 20), pygame.SRCALPHA)
        crack_pulse = abs(math.sin(t * 6))
        for i in range(5):
            seed = random.Random(i + 7)
            # 主裂纹
            sx, sy = cx, cy
            for seg in range(2):
                angle = seed.uniform(0, 2 * math.pi)
                length = size * 0.15 + seed.randint(0, int(size * 0.1))
                ex = sx + math.cos(angle) * length
                ey = sy + math.sin(angle) * length
                alpha = int(140 + crack_pulse * 100)
                pygame.draw.line(crack_surf, (*crack_glow, alpha), (int(sx), int(sy)), (int(ex), int(ey)), 2)
                # 分支
                if seg == 0:
                    bangle = angle + seed.choice([-0.6, 0.6])
                    bex = sx + math.cos(bangle) * length * 0.6
                    bey = sy + math.sin(bangle) * length * 0.6
                    pygame.draw.line(crack_surf, (*core_bright, alpha // 2), (int(sx), int(sy)), (int(bex), int(bey)), 1)
                sx, sy = ex, ey
        bullet_surf.blit(crack_surf, (0, 0))
        
        # 指节凸起（4个）
        for i in range(4):
            knuckle_angle = (-50 + i * 28) * 0.01745
            kx = cx + math.cos(knuckle_angle) * (size * 0.35)
            ky = cy + math.sin(knuckle_angle) * (size * 0.35) - size * 0.12
            pygame.draw.circle(bullet_surf, rock_dark, (int(kx), int(ky)), max(2, int(size * 0.08)))
            pygame.draw.circle(bullet_surf, rock_gray, (int(kx), int(ky)), max(1, int(size * 0.05)))
        
        # 核心能量点
        core_r = int(size * 0.12 + crack_pulse * 3)
        pygame.draw.circle(bullet_surf, core_orange, (cx, cy), core_r)
        pygame.draw.circle(bullet_surf, core_bright, (cx, cy), core_r // 2)
        
        # 能量尾迹
        for i in range(3):
            trail_y = cy + size * 0.3 + i * 4
            trail_alpha = 100 - i * 30
            trail_w = size * 0.3 - i * 2
            pygame.draw.ellipse(bullet_surf, (*core_orange, trail_alpha),
                              (cx - trail_w, trail_y, trail_w * 2, 4))
        
        surface.blit(bullet_surf, (x - size - 10, y - size - 10))
        return True
    
    elif "rock_debris" in effects:
        # 岩块碎片 - 高质量AOE爆裂产物
        bullet_surf = pygame.Surface((size*2 + 10, size*2 + 10), pygame.SRCALPHA)
        cx, cy = size + 5, size + 5
        
        # 碎片光晕
        pygame.draw.circle(bullet_surf, (*core_orange, 60), (cx, cy), int(size * 0.5))
        
        # 不规则碎片（多层）
        debris_points = []
        for i in range(7):
            angle = i * 51.4 * 0.01745 + t * 4
            r = size * 0.3 + random.Random(i + 11).randint(-3, 5)
            debris_points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
        pygame.draw.polygon(bullet_surf, debris_brown, debris_points)
        pygame.draw.polygon(bullet_surf, rock_dark, debris_points, 2)
        
        # 内部纹理
        for i in range(3):
            seed = random.Random(i + 33)
            pygame.draw.line(bullet_surf, rock_gray,
                           (cx + seed.randint(-int(size*0.2), int(size*0.2)), cy + seed.randint(-int(size*0.2), int(size*0.2))),
                           (cx + seed.randint(-int(size*0.2), int(size*0.2)), cy + seed.randint(-int(size*0.2), int(size*0.2))), 1)
        
        # 残留能量
        energy_pulse = abs(math.sin(t * 5))
        pygame.draw.circle(bullet_surf, (*core_orange, int(100 + energy_pulse * 80)), (cx, cy), int(size * 0.15))
        
        # 火星尾迹
        for i in range(4):
            trail_phase = (t * 2 + i * 0.3) % 1
            trail_y = cy + size * 0.2 + trail_phase * size * 0.4
            trail_alpha = int(150 * (1 - trail_phase))
            pygame.draw.circle(bullet_surf, (*crack_glow, trail_alpha), (cx + random.Random(i).randint(-3, 3), int(trail_y)), 2)
        
        surface.blit(bullet_surf, (x - size - 5, y - size - 5))
        return True
    
    elif "meteor_fist" in effects:
        # 巨型岩核拳 - F大招（至尊品质）
        bullet_surf = pygame.Surface((size*2 + 30, size*2 + 30), pygame.SRCALPHA)
        cx, cy = size + 15, size + 15
        
        # 巨大能量光晕（多层渐变）
        for i in range(6):
            glow_r = int(size * 0.65) + 12 - i * 4 + int(abs(math.sin(t * 3)) * 5)
            glow_alpha = 100 - i * 15
            pygame.draw.circle(bullet_surf, (*core_orange, glow_alpha), (cx, cy), glow_r)
        
        # 能量环
        ring_r = int(size * 0.55) + int(abs(math.sin(t * 4)) * 4)
        pygame.draw.circle(bullet_surf, (*crack_glow, 120), (cx, cy), ring_r, 2)
        
        # 巨型拳头阴影
        shadow_points = []
        for i in range(12):
            angle = i * 30 * 0.01745
            r = size * 0.48 + random.Random(i + 99).randint(-4, 6)
            shadow_points.append((int(cx + math.cos(angle) * r + 3), int(cy + math.sin(angle) * r + 3)))
        pygame.draw.polygon(bullet_surf, (35, 30, 25), shadow_points)
        
        # 巨型拳头主体
        fist_points = []
        for i in range(12):
            angle = i * 30 * 0.01745
            r = size * 0.45 + random.Random(i + 99).randint(-4, 7)
            fist_points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
        pygame.draw.polygon(bullet_surf, rock_gray, fist_points)
        pygame.draw.polygon(bullet_surf, (180, 90, 30), fist_points, 3)
        
        # 熔岩裂纹网
        lava_surf = pygame.Surface((size*2 + 30, size*2 + 30), pygame.SRCALPHA)
        for i in range(8):
            seed = random.Random(i + 33)
            sx, sy = cx, cy
            for seg in range(3):
                angle = seed.uniform(0, 2 * math.pi)
                length = size * 0.12 + seed.randint(0, int(size * 0.08))
                ex = sx + math.cos(angle) * length
                ey = sy + math.sin(angle) * length
                lava_pulse = abs(math.sin(t * 4 + i * 0.5))
                col = core_bright if lava_pulse > 0.5 else crack_glow
                pygame.draw.line(lava_surf, col, (int(sx), int(sy)), (int(ex), int(ey)), 2)
                sx, sy = ex, ey
        bullet_surf.blit(lava_surf, (0, 0))
        
        # 核心熔融
        core_pulse = abs(math.sin(t * 5))
        core_r = int(size * 0.18 + core_pulse * 5)
        pygame.draw.circle(bullet_surf, crack_glow, (cx, cy), core_r)
        pygame.draw.circle(bullet_surf, core_bright, (cx, cy), int(core_r * 0.6))
        pygame.draw.circle(bullet_surf, (255, 245, 220), (cx, cy), int(core_r * 0.3))
        
        # 能量射线
        for i in range(6):
            ray_angle = (i * 60 + t * 40) * 0.01745
            ray_len = size * 0.35 + int(core_pulse * 8)
            pygame.draw.line(bullet_surf, (*core_bright, 180), (cx, cy),
                           (int(cx + math.cos(ray_angle) * ray_len), int(cy + math.sin(ray_angle) * ray_len)), 2)
        
        surface.blit(bullet_surf, (x - size - 15, y - size - 15))
        return True
    
    elif "rock_wall" in effects:
        # 岩壁碎片 - G大招岩壁（至尊品质）
        bullet_surf = pygame.Surface((size*2 + 20, size*2 + 20), pygame.SRCALPHA)
        cx, cy = size + 10, size + 10
        
        rock_dark = (70, 65, 60)
        
        # 岩壁块光晕
        for i in range(3):
            glow_r = int(size * 0.5) + 6 - i * 4
            pygame.draw.circle(bullet_surf, (*core_orange, 50 - i * 15), (cx, cy), glow_r)
        
        # 岩壁块阴影
        wall_w = int(size * 0.45)
        wall_h = int(size * 0.65)
        pygame.draw.rect(bullet_surf, (50, 45, 40), 
                        (cx - wall_w // 2 + 2, cy - wall_h // 2 + 2, wall_w, wall_h))
        
        # 岩壁主体
        pygame.draw.rect(bullet_surf, rock_gray, 
                        (cx - wall_w // 2, cy - wall_h // 2, wall_w, wall_h))
        pygame.draw.rect(bullet_surf, rock_dark,
                        (cx - wall_w // 2, cy - wall_h // 2, wall_w, wall_h), 2)
        
        # 岩石纹理（砖块状）
        for i in range(3):
            line_y = cy - wall_h // 2 + (i + 1) * wall_h // 4
            pygame.draw.line(bullet_surf, rock_dark, 
                           (cx - wall_w // 2 + 2, int(line_y)), (cx + wall_w // 2 - 2, int(line_y)), 1)
        
        # 裂纹发光
        crack_pulse = abs(math.sin(t * 4))
        pygame.draw.line(bullet_surf, (*crack_glow, int(100 + crack_pulse * 100)),
                        (cx - wall_w // 4, cy - wall_h // 4), (cx + wall_w // 4, cy + wall_h // 4), 2)
        
        surface.blit(bullet_surf, (x - size - 10, y - size - 10))
        return True
    
    elif "tremor_wave" in effects:
        # 震荡波 - C大招（至尊品质）
        bullet_surf = pygame.Surface((size*2 + 30, size*2 + 30), pygame.SRCALPHA)
        cx, cy = size + 15, size + 15
        
        wave_orange = (255, 140, 60)
        wave_bright = (255, 200, 120)
        
        # 多层同心圆震荡波（脉动扩散）
        for i in range(4):
            wave_phase = (t * 2 + i * 0.25) % 1
            wave_r = int(size * 0.2 + wave_phase * size * 0.4) + i * 3
            wave_alpha = int(200 * (1 - wave_phase)) - i * 20
            if wave_alpha > 0:
                pygame.draw.circle(bullet_surf, (*wave_orange, wave_alpha), (cx, cy), wave_r, 3)
        
        # 能量线条
        for i in range(6):
            angle = (i * 60 + t * 50) * 0.01745
            inner_r = size * 0.15
            outer_r = size * 0.4 + abs(math.sin(t * 4 + i)) * 5
            pygame.draw.line(bullet_surf, (*wave_bright, 150), 
                           (int(cx + math.cos(angle) * inner_r), int(cy + math.sin(angle) * inner_r)),
                           (int(cx + math.cos(angle) * outer_r), int(cy + math.sin(angle) * outer_r)), 2)
        
        # 中心冲击点
        pygame.draw.circle(bullet_surf, rock_gray, (cx, cy), int(size * 0.15))
        pygame.draw.circle(bullet_surf, crack_glow, (cx, cy), int(size * 0.1))
        core_pulse = abs(math.sin(t * 6))
        pygame.draw.circle(bullet_surf, core_bright, (cx, cy), int(size * 0.05 + core_pulse * 3))
        
        surface.blit(bullet_surf, (x - size - 15, y - size - 15))
        return True
    
    elif "magma_fist" in effects:
        # 熔岩飞拳 - 至尊品质
        bullet_surf = pygame.Surface((size*2 + 20, size*2 + 20), pygame.SRCALPHA)
        cx, cy = size + 10, size + 10
        
        magma_dark = (60, 30, 20)
        magma_red = (255, 80, 20)
        magma_orange = (255, 150, 50)
        magma_bright = (255, 220, 150)
        
        # 多层熔岩光晕
        for i in range(5):
            glow_r = int(size * 0.55) + 8 - i * 3 + int(abs(math.sin(t * 4)) * 4)
            glow_alpha = 100 - i * 18
            pygame.draw.circle(bullet_surf, (*magma_red, glow_alpha), (cx, cy), glow_r)
        
        # 熔岩粒子环绕
        for i in range(6):
            particle_angle = t * 3 + i * 1.05
            particle_r = size * 0.4 + abs(math.sin(t * 4 + i)) * 5
            px = cx + math.cos(particle_angle) * particle_r
            py = cy + math.sin(particle_angle) * particle_r
            pygame.draw.circle(bullet_surf, magma_orange, (int(px), int(py)), 3)
        
        # 熔岩拳头阴影
        fist_points = []
        for i in range(10):
            angle = i * 36 * 0.01745
            r = size * 0.38 + random.Random(i + 13).randint(-3, 5)
            fist_points.append((int(cx + math.cos(angle) * r + 2), int(cy + math.sin(angle) * r + 2)))
        pygame.draw.polygon(bullet_surf, (30, 15, 10), fist_points)
        
        # 熔岩拳头主体
        fist_points2 = []
        for i in range(10):
            angle = i * 36 * 0.01745
            r = size * 0.35 + random.Random(i + 13).randint(-3, 5)
            fist_points2.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
        pygame.draw.polygon(bullet_surf, magma_dark, fist_points2)
        pygame.draw.polygon(bullet_surf, magma_red, fist_points2, 2)
        
        # 熔岩裂纹网络（脉动）
        lava_pulse = abs(math.sin(t * 5))
        for i in range(6):
            seed = random.Random(i + 77)
            sx, sy = cx, cy
            for seg in range(2):
                angle = seed.uniform(0, 2 * math.pi)
                length = size * 0.12 + seed.randint(0, int(size * 0.08))
                ex = sx + math.cos(angle) * length
                ey = sy + math.sin(angle) * length
                col = magma_bright if lava_pulse > 0.5 else magma_orange
                pygame.draw.line(bullet_surf, col, (int(sx), int(sy)), (int(ex), int(ey)), 2)
                sx, sy = ex, ey
        
        # 核心熔岩泡
        core_r = int(size * 0.12 + lava_pulse * 4)
        pygame.draw.circle(bullet_surf, magma_orange, (cx, cy), core_r)
        pygame.draw.circle(bullet_surf, magma_bright, (cx, cy), core_r // 2)
        
        # 火焰尾迹
        for i in range(4):
            trail_y = cy + size * 0.25 + i * 5
            trail_alpha = 120 - i * 28
            trail_w = size * 0.25 - i * 3
            pygame.draw.ellipse(bullet_surf, (*magma_orange, trail_alpha),
                              (cx - trail_w, trail_y, trail_w * 2, 5))
        
        surface.blit(bullet_surf, (x - size - 10, y - size - 10))
        return True
    
    elif "obsidian_fist" in effects:
        # 黑曜石拳 - 至尊品质
        bullet_surf = pygame.Surface((size*2 + 20, size*2 + 20), pygame.SRCALPHA)
        cx, cy = size + 10, size + 10
        
        obsidian_black = (15, 12, 20)
        obsidian_dark = (35, 30, 45)
        lightning_purple = (180, 100, 255)
        lightning_bright = (220, 180, 255)
        crystal_glow = (140, 80, 200)
        
        # 紫色能量光晕
        for i in range(4):
            glow_r = int(size * 0.55) + 8 - i * 4 + int(abs(math.sin(t * 5)) * 3)
            pygame.draw.circle(bullet_surf, (*lightning_purple, 70 - i * 15), (cx, cy), glow_r)
        
        # 黑曜石主体阴影
        diamond_points = [
            (cx, cy - int(size * 0.4)),
            (cx + int(size * 0.38), cy),
            (cx, cy + int(size * 0.4)),
            (cx - int(size * 0.38), cy)
        ]
        shadow_points = [(p[0] + 2, p[1] + 2) for p in diamond_points]
        pygame.draw.polygon(bullet_surf, (10, 8, 15), shadow_points)
        
        # 黑曜石菱形主体
        pygame.draw.polygon(bullet_surf, obsidian_black, diamond_points)
        
        # 切割面高光
        pygame.draw.polygon(bullet_surf, obsidian_dark, 
                          [diamond_points[0], (cx, cy), diamond_points[1]])
        pygame.draw.polygon(bullet_surf, lightning_purple, diamond_points, 2)
        
        # 动态紫电效果
        lightning_active = abs(math.sin(t * 8)) > 0.4
        if lightning_active:
            for i in range(3):
                seed = random.Random(int(t * 10) + i)
                sx = cx + seed.randint(-int(size * 0.25), int(size * 0.25))
                sy = cy + seed.randint(-int(size * 0.25), int(size * 0.25))
                ex = sx + seed.randint(-8, 8)
                ey = sy + seed.randint(-8, 8)
                pygame.draw.line(bullet_surf, lightning_bright, (sx, sy), (ex, ey), 2)
        
        # 核心紫水晶光
        core_pulse = abs(math.sin(t * 6))
        core_r = int(size * 0.1 + core_pulse * 3)
        pygame.draw.circle(bullet_surf, crystal_glow, (cx, cy), core_r)
        pygame.draw.circle(bullet_surf, lightning_bright, (cx, cy), core_r // 2)
        
        # 紫色粒子尾迹
        for i in range(3):
            trail_phase = (t * 2 + i * 0.4) % 1
            trail_y = cy + size * 0.2 + trail_phase * size * 0.3
            pygame.draw.circle(bullet_surf, (*lightning_purple, int(120 * (1 - trail_phase))),
                             (cx + random.Random(i + 5).randint(-4, 4), int(trail_y)), 2)
        
        surface.blit(bullet_surf, (x - size - 10, y - size - 10))
        return True
    
    elif "crystal_fist" in effects:
        # 水晶拳 - 至尊品质棱镜效果
        bullet_surf = pygame.Surface((size*2 + 20, size*2 + 20), pygame.SRCALPHA)
        cx, cy = size + 10, size + 10
        
        crystal_cyan = (100, 220, 255)
        crystal_pink = (255, 150, 200)
        crystal_white = (240, 250, 255)
        
        # 彩虹棱镜光晕（旋转）
        prism_colors = [
            (255, 120, 120, 50), (255, 200, 100, 50), (200, 255, 120, 50),
            (120, 255, 200, 50), (120, 200, 255, 50), (200, 120, 255, 50)
        ]
        for i, col in enumerate(prism_colors):
            angle = t * 1.5 + i * 1.05
            pr = size * 0.4 + abs(math.sin(t * 3 + i)) * 4
            px = cx + math.cos(angle) * pr
            py = cy + math.sin(angle) * pr
            pygame.draw.circle(bullet_surf, col, (int(px), int(py)), int(size * 0.12))
        
        # 水晶主体光晕
        for i in range(3):
            glow_r = int(size * 0.45) + 6 - i * 4
            pygame.draw.circle(bullet_surf, (*crystal_cyan, 60 - i * 18), (cx, cy), glow_r)
        
        # 六面体水晶
        crystal_points = []
        for i in range(6):
            angle = (i * 60 - 90) * 0.01745
            r = size * 0.32 + (0.05 * size if i % 2 == 0 else 0)
            crystal_points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
        pygame.draw.polygon(bullet_surf, crystal_cyan, crystal_points)
        pygame.draw.polygon(bullet_surf, crystal_pink, crystal_points, 2)
        
        # 内部切割面
        pygame.draw.polygon(bullet_surf, crystal_white, 
                          [crystal_points[0], (cx, cy), crystal_points[1]])
        
        # 核心折射光点
        refract_pulse = abs(math.sin(t * 5))
        pygame.draw.circle(bullet_surf, crystal_white, (cx, cy), int(size * 0.08 + refract_pulse * 3))
        
        # 星芒闪烁
        if refract_pulse > 0.6:
            for i in range(4):
                angle = (i * 45 + t * 30) * 0.01745
                pygame.draw.line(bullet_surf, (*crystal_white, 200), (cx, cy),
                               (int(cx + math.cos(angle) * size * 0.25), int(cy + math.sin(angle) * size * 0.25)), 1)
        
        surface.blit(bullet_surf, (x - size - 10, y - size - 10))
        return True
    
    elif "jade_fist" in effects:
        # 翡翠拳 - 至尊品质东方玉石
        bullet_surf = pygame.Surface((size*2 + 20, size*2 + 20), pygame.SRCALPHA)
        cx, cy = size + 10, size + 10
        
        jade_green = (100, 180, 120)
        jade_dark = (60, 120, 80)
        jade_light = (150, 220, 170)
        gold_rune = (220, 180, 80)
        gold_bright = (255, 220, 120)
        
        # 玉石柔和光晕
        for i in range(4):
            glow_r = int(size * 0.5) + 8 - i * 4
            pygame.draw.circle(bullet_surf, (*jade_green, 60 - i * 12), (cx, cy), glow_r)
        
        # 圆润玉石主体
        pygame.draw.circle(bullet_surf, jade_dark, (cx + 1, cy + 1), int(size * 0.35))
        pygame.draw.circle(bullet_surf, jade_green, (cx, cy), int(size * 0.33))
        
        # 玉质纹理（温润感）
        for i in range(3):
            seed = random.Random(i + 55)
            arc_start = seed.uniform(0, 2 * math.pi)
            arc_end = arc_start + seed.uniform(0.5, 1.5)
            for a in range(int(arc_start * 10), int(arc_end * 10)):
                ang = a / 10
                r = size * (0.15 + seed.uniform(0, 0.12))
                pygame.draw.circle(bullet_surf, jade_light, 
                                 (int(cx + math.cos(ang) * r), int(cy + math.sin(ang) * r)), 1)
        
        # 阴阳符文
        pygame.draw.circle(bullet_surf, gold_rune, (cx, cy), int(size * 0.15), 2)
        
        # 八卦线
        for i in range(8):
            angle = i * 45 * 0.01745
            inner_r = size * 0.06
            outer_r = size * 0.2
            pygame.draw.line(bullet_surf, gold_rune,
                           (int(cx + math.cos(angle) * inner_r), int(cy + math.sin(angle) * inner_r)),
                           (int(cx + math.cos(angle) * outer_r), int(cy + math.sin(angle) * outer_r)), 1)
        
        # 核心玉髓
        jade_pulse = abs(math.sin(t * 4))
        pygame.draw.circle(bullet_surf, (*gold_bright, int(120 + jade_pulse * 80)), (cx, cy), int(size * 0.06))
        
        # 灵气尾迹
        for i in range(3):
            trail_y = cy + size * 0.2 + i * 5
            pygame.draw.ellipse(bullet_surf, (*jade_light, 80 - i * 25),
                              (cx - size * 0.15, trail_y, size * 0.3, 4))
        
        surface.blit(bullet_surf, (x - size - 10, y - size - 10))
        return True
    
    elif "meteor_rock" in effects:
        # 陨铁飞拳 - 至尊品质太空陨石
        bullet_surf = pygame.Surface((size*2 + 20, size*2 + 20), pygame.SRCALPHA)
        cx, cy = size + 10, size + 10
        
        meteor_gray = (80, 85, 95)
        meteor_dark = (50, 55, 65)
        metal_shine = (140, 150, 170)
        fire_orange = (255, 150, 50)
        fire_bright = (255, 220, 150)
        
        # 再入大气层火焰光晕
        for i in range(4):
            glow_r = int(size * 0.5) + 8 - i * 4
            pygame.draw.circle(bullet_surf, (*fire_orange, 70 - i * 15), (cx, cy), glow_r)
        
        # 火焰尾迹（长）
        for i in range(5):
            trail_y = cy + size * 0.2 + i * 6
            trail_alpha = 140 - i * 25
            trail_w = size * 0.28 - i * 3
            pygame.draw.ellipse(bullet_surf, (*fire_orange, trail_alpha),
                              (cx - trail_w, trail_y, trail_w * 2, 6))
        
        # 陨石主体阴影
        pygame.draw.circle(bullet_surf, meteor_dark, (cx + 2, cy + 2), int(size * 0.35))
        
        # 陨石主体（不规则）
        meteor_points = []
        for i in range(10):
            angle = i * 36 * 0.01745
            r = size * 0.32 + random.Random(i + 88).randint(-4, 6)
            meteor_points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
        pygame.draw.polygon(bullet_surf, meteor_gray, meteor_points)
        pygame.draw.polygon(bullet_surf, metal_shine, meteor_points, 1)
        
        # 陨石坑
        for i in range(3):
            seed = random.Random(i + 44)
            crater_x = cx + seed.randint(-int(size * 0.15), int(size * 0.15))
            crater_y = cy + seed.randint(-int(size * 0.15), int(size * 0.15))
            crater_r = max(2, int(size * 0.06) + seed.randint(-1, 2))
            pygame.draw.circle(bullet_surf, meteor_dark, (crater_x, crater_y), crater_r)
        
        # 金属光泽
        pygame.draw.arc(bullet_surf, metal_shine, 
                       (cx - int(size * 0.25), cy - int(size * 0.25), int(size * 0.5), int(size * 0.5)),
                       0.5, 2.0, 2)
        
        # 星尘粒子
        for i in range(4):
            particle_phase = (t * 2 + i * 0.4) % 1
            py = cy + size * 0.35 + particle_phase * size * 0.3
            px = cx + random.Random(i + 22).randint(-6, 6)
            pygame.draw.circle(bullet_surf, (*fire_bright, int(150 * (1 - particle_phase))), (px, int(py)), 2)
        
        surface.blit(bullet_surf, (x - size - 10, y - size - 10))
        return True
    
    elif "sandstone_fist" in effects:
        # 沙岩飞拳 - 至尊品质埃及风格
        bullet_surf = pygame.Surface((size*2 + 20, size*2 + 20), pygame.SRCALPHA)
        cx, cy = size + 10, size + 10
        
        sand_yellow = (210, 180, 120)
        sand_dark = (160, 130, 80)
        egypt_gold = (220, 180, 50)
        gold_bright = (255, 220, 100)
        
        # 沙尘光晕
        for i in range(4):
            glow_r = int(size * 0.5) + 8 - i * 4
            pygame.draw.circle(bullet_surf, (*sand_yellow, 50 - i * 10), (cx, cy), glow_r)
        
        # 沙尘粒子环绕
        for i in range(8):
            particle_angle = t * 2 + i * 0.8
            particle_r = size * 0.4 + abs(math.sin(t * 3 + i)) * 5
            px = cx + math.cos(particle_angle) * particle_r
            py = cy + math.sin(particle_angle) * particle_r
            pygame.draw.circle(bullet_surf, (*sand_dark, 120), (int(px), int(py)), 2)
        
        # 金字塔形状阴影
        pyramid_h = int(size * 0.4)
        pyramid_w = int(size * 0.35)
        shadow_points = [(cx + 2, cy - pyramid_h + 2), (cx + pyramid_w + 2, cy + pyramid_h // 2 + 2), 
                        (cx - pyramid_w + 2, cy + pyramid_h // 2 + 2)]
        pygame.draw.polygon(bullet_surf, (100, 80, 50), shadow_points)
        
        # 金字塔主体
        pyramid_points = [(cx, cy - pyramid_h), (cx + pyramid_w, cy + pyramid_h // 2), 
                         (cx - pyramid_w, cy + pyramid_h // 2)]
        pygame.draw.polygon(bullet_surf, sand_yellow, pyramid_points)
        pygame.draw.polygon(bullet_surf, egypt_gold, pyramid_points, 2)
        
        # 金字塔层级线
        for i in range(3):
            line_y = cy - pyramid_h + (i + 1) * pyramid_h * 0.4
            line_w = pyramid_w * (0.3 + i * 0.25)
            pygame.draw.line(bullet_surf, sand_dark, (int(cx - line_w), int(line_y)), (int(cx + line_w), int(line_y)), 1)
        
        # 荷鲁斯之眼
        eye_y = cy - int(pyramid_h * 0.3)
        pygame.draw.ellipse(bullet_surf, egypt_gold, (cx - 4, eye_y - 2, 8, 4))
        pygame.draw.circle(bullet_surf, gold_bright, (cx, eye_y), 2)
        
        # 圣甲虫符号尾迹
        for i in range(3):
            trail_y = cy + pyramid_h // 2 + 5 + i * 5
            pygame.draw.ellipse(bullet_surf, (*egypt_gold, 80 - i * 25),
                              (cx - size * 0.15, trail_y, size * 0.3, 4))
        
        surface.blit(bullet_surf, (x - size - 10, y - size - 10))
        return True
    
    elif "ice_fist" in effects:
        # 冰晶飞拳 - 至尊品质冰川巨人
        bullet_surf = pygame.Surface((size*2 + 20, size*2 + 20), pygame.SRCALPHA)
        cx, cy = size + 10, size + 10
        
        ice_blue = (180, 220, 255)
        ice_deep = (100, 160, 220)
        frost_white = (240, 250, 255)
        aurora_cyan = (100, 255, 220)
        
        # 寒霜光晕（多层脉动）
        for i in range(4):
            glow_r = int(size * 0.5) + 8 - i * 4 + int(abs(math.sin(t * 3)) * 3)
            pygame.draw.circle(bullet_surf, (*ice_blue, 60 - i * 12), (cx, cy), glow_r)
        
        # 极光粒子环绕
        for i in range(6):
            aurora_angle = t * 2 + i * 1.05
            aurora_r = size * 0.42 + abs(math.sin(t * 4 + i)) * 4
            ax = cx + math.cos(aurora_angle) * aurora_r
            ay = cy + math.sin(aurora_angle) * aurora_r
            pygame.draw.circle(bullet_surf, (*aurora_cyan, 100), (int(ax), int(ay)), 2)
        
        # 六边形冰晶主体阴影
        hex_points_shadow = []
        for i in range(6):
            angle = (i * 60 - 90) * 0.01745
            r = size * 0.35
            hex_points_shadow.append((int(cx + math.cos(angle) * r + 2), int(cy + math.sin(angle) * r + 2)))
        pygame.draw.polygon(bullet_surf, ice_deep, hex_points_shadow)
        
        # 六边形冰晶主体
        hex_points = []
        for i in range(6):
            angle = (i * 60 - 90) * 0.01745
            r = size * 0.33
            hex_points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
        pygame.draw.polygon(bullet_surf, ice_blue, hex_points)
        pygame.draw.polygon(bullet_surf, frost_white, hex_points, 2)
        
        # 内部冰纹
        for i in range(3):
            angle1 = (i * 120 - 90) * 0.01745
            angle2 = ((i + 1) * 120 - 90) * 0.01745
            pygame.draw.line(bullet_surf, frost_white, (cx, cy),
                           (int(cx + math.cos(angle1) * size * 0.25), int(cy + math.sin(angle1) * size * 0.25)), 1)
        
        # 霜晶核心
        frost_pulse = abs(math.sin(t * 4))
        core_r = int(size * 0.1 + frost_pulse * 3)
        pygame.draw.circle(bullet_surf, frost_white, (cx, cy), core_r)
        pygame.draw.circle(bullet_surf, (255, 255, 255), (cx, cy), core_r // 2)
        
        # 雪花尾迹
        for i in range(4):
            trail_phase = (t * 1.5 + i * 0.3) % 1
            trail_y = cy + size * 0.2 + trail_phase * size * 0.35
            pygame.draw.circle(bullet_surf, (*frost_white, int(130 * (1 - trail_phase))),
                             (cx + random.Random(i + 77).randint(-5, 5), int(trail_y)), 2)
        
        surface.blit(bullet_surf, (x - size - 10, y - size - 10))
        return True
    
    elif "volcanic_fist" in effects:
        # 火山飞拳 - 至尊品质火山领主
        bullet_surf = pygame.Surface((size*2 + 20, size*2 + 20), pygame.SRCALPHA)
        cx, cy = size + 10, size + 10
        
        volcano_black = (40, 30, 25)
        volcano_gray = (70, 55, 45)
        lava_red = (255, 60, 20)
        lava_orange = (255, 120, 40)
        lava_yellow = (255, 200, 50)
        smoke_gray = (80, 75, 70)
        
        # 火焰光晕（多层脉动）
        for i in range(5):
            glow_r = int(size * 0.55) + 10 - i * 4 + int(abs(math.sin(t * 4)) * 5)
            pygame.draw.circle(bullet_surf, (*lava_red, 80 - i * 14), (cx, cy), glow_r)
        
        # 喷发火星
        for i in range(6):
            spark_angle = t * 3 + i * 1.05
            spark_r = size * 0.45 + abs(math.sin(t * 5 + i * 0.8)) * 6
            sx = cx + math.cos(spark_angle) * spark_r
            sy = cy + math.sin(spark_angle) * spark_r
            pygame.draw.circle(bullet_surf, lava_orange, (int(sx), int(sy)), 2)
        
        # 火山岩主体阴影
        pygame.draw.circle(bullet_surf, (25, 18, 15), (cx + 2, cy + 2), int(size * 0.38))
        
        # 火山岩主体
        rock_points = []
        for i in range(10):
            angle = i * 36 * 0.01745
            r = size * 0.35 + random.Random(i + 66).randint(-3, 5)
            rock_points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
        pygame.draw.polygon(bullet_surf, volcano_black, rock_points)
        pygame.draw.polygon(bullet_surf, volcano_gray, rock_points, 2)
        
        # 熔岩裂纹网络
        lava_pulse = abs(math.sin(t * 5))
        for i in range(4):
            seed = random.Random(i + 99)
            angle = seed.uniform(0, 2 * math.pi)
            length = size * 0.25
            col = lava_yellow if lava_pulse > 0.5 else lava_orange
            pygame.draw.line(bullet_surf, col, (cx, cy),
                           (int(cx + math.cos(angle) * length), int(cy + math.sin(angle) * length)), 2)
        
        # 火山口（顶部）
        crater_y = cy - int(size * 0.15)
        pygame.draw.ellipse(bullet_surf, volcano_gray, (cx - 6, crater_y - 3, 12, 6))
        pygame.draw.ellipse(bullet_surf, lava_orange, (cx - 4, crater_y - 2, 8, 4))
        pygame.draw.ellipse(bullet_surf, lava_yellow, (cx - 2, crater_y - 1, 4, 2))
        
        # 烟雾尾迹
        for i in range(4):
            smoke_phase = (t + i * 0.3) % 1
            smoke_y = cy + size * 0.25 + smoke_phase * size * 0.4
            smoke_r = 3 + int(smoke_phase * 3)
            pygame.draw.circle(bullet_surf, (*smoke_gray, int(100 * (1 - smoke_phase))),
                             (cx + random.Random(i).randint(-4, 4), int(smoke_y)), smoke_r)
        
        surface.blit(bullet_surf, (x - size - 10, y - size - 10))
        return True
    
    elif "diamond_fist" in effects:
        # 钻石飞拳 - 至尊品质璀璨钻石
        bullet_surf = pygame.Surface((size*2 + 20, size*2 + 20), pygame.SRCALPHA)
        cx, cy = size + 10, size + 10
        
        diamond_white = (245, 250, 255)
        diamond_blue = (200, 220, 255)
        diamond_core = (255, 255, 255)
        
        # 彩虹光晕（旋转）
        rainbow_colors = [
            (255, 180, 180, 40), (255, 220, 180, 40), (255, 255, 180, 40),
            (180, 255, 180, 40), (180, 255, 255, 40), (180, 180, 255, 40), (255, 180, 255, 40)
        ]
        for i, col in enumerate(rainbow_colors):
            angle = t * 1.5 + i * 0.9
            pr = size * 0.42 + abs(math.sin(t * 3 + i * 0.5)) * 4
            px = cx + math.cos(angle) * pr
            py = cy + math.sin(angle) * pr
            pygame.draw.circle(bullet_surf, col, (int(px), int(py)), int(size * 0.1))
        
        # 钻石光芒光晕
        for i in range(4):
            glow_r = int(size * 0.48) + 8 - i * 4 + int(abs(math.sin(t * 4)) * 3)
            pygame.draw.circle(bullet_surf, (*diamond_blue, 50 - i * 10), (cx, cy), glow_r)
        
        # 八边形钻石主体
        oct_points = []
        for i in range(8):
            angle = (i * 45 + 22.5) * 0.01745
            r = size * 0.32
            oct_points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
        pygame.draw.polygon(bullet_surf, diamond_white, oct_points)
        pygame.draw.polygon(bullet_surf, diamond_blue, oct_points, 2)
        
        # 切割面（多个三角形）
        for i in range(4):
            idx = i * 2
            pygame.draw.polygon(bullet_surf, (*diamond_core, 100),
                              [oct_points[idx], (cx, cy), oct_points[(idx + 1) % 8]])
        
        # 星芒闪烁核心
        sparkle_pulse = abs(math.sin(t * 6))
        if sparkle_pulse > 0.3:
            for i in range(8):
                angle = (i * 45 + t * 60) * 0.01745
                ray_len = size * (0.15 + sparkle_pulse * 0.15)
                pygame.draw.line(bullet_surf, diamond_core, (cx, cy),
                               (int(cx + math.cos(angle) * ray_len), int(cy + math.sin(angle) * ray_len)), 1)
        
        # 核心亮点
        pygame.draw.circle(bullet_surf, diamond_core, (cx, cy), int(size * 0.08 + sparkle_pulse * 2))
        
        surface.blit(bullet_surf, (x - size - 10, y - size - 10))
        return True
    
    elif "rusty_fist" in effects:
        # 锈蚀飞拳 - 至尊品质远古锈蚀
        bullet_surf = pygame.Surface((size*2 + 20, size*2 + 20), pygame.SRCALPHA)
        cx, cy = size + 10, size + 10
        
        rust_orange = (180, 100, 60)
        rust_brown = (120, 70, 40)
        rust_dark = (80, 50, 30)
        moss_green = (60, 90, 50)
        decay_glow = (150, 120, 80)
        
        # 衰败光晕
        for i in range(3):
            glow_r = int(size * 0.45) + 6 - i * 4
            pygame.draw.circle(bullet_surf, (*rust_orange, 40 - i * 12), (cx, cy), glow_r)
        
        # 锈蚀拳头阴影
        pygame.draw.circle(bullet_surf, rust_dark, (cx + 2, cy + 2), int(size * 0.35))
        
        # 锈蚀拳头主体
        rusty_points = []
        for i in range(10):
            angle = i * 36 * 0.01745
            r = size * 0.32 + random.Random(i + 88).randint(-4, 5)
            rusty_points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
        pygame.draw.polygon(bullet_surf, rust_brown, rusty_points)
        pygame.draw.polygon(bullet_surf, rust_dark, rusty_points, 2)
        
        # 锈斑（多层）
        for i in range(5):
            seed = random.Random(i + 88)
            rx = cx + seed.randint(-int(size * 0.2), int(size * 0.2))
            ry = cy + seed.randint(-int(size * 0.2), int(size * 0.2))
            rr = 2 + seed.randint(0, 2)
            pygame.draw.circle(bullet_surf, rust_orange, (rx, ry), rr)
        
        # 苔藓斑点
        for i in range(3):
            seed = random.Random(i + 55)
            mx = cx + seed.randint(-int(size * 0.22), int(size * 0.22))
            my = cy + seed.randint(-int(size * 0.22), int(size * 0.22))
            pygame.draw.circle(bullet_surf, moss_green, (mx, my), 2)
        
        # 衰败核心（暗淡脉动）
        decay_pulse = abs(math.sin(t * 2)) * 0.5 + 0.3
        core_alpha = int(60 + decay_pulse * 60)
        pygame.draw.circle(bullet_surf, (*decay_glow, core_alpha), (cx, cy), int(size * 0.1))
        
        # 锈蚀粒子尾迹
        for i in range(3):
            trail_phase = (t * 1.5 + i * 0.4) % 1
            trail_y = cy + size * 0.2 + trail_phase * size * 0.3
            pygame.draw.circle(bullet_surf, (*rust_orange, int(100 * (1 - trail_phase))),
                             (cx + random.Random(i + 33).randint(-4, 4), int(trail_y)), 2)
        
        surface.blit(bullet_surf, (x - size - 10, y - size - 10))
        return True
    
    elif "golden_fist" in effects:
        # 黄金飞拳 - 至尊品质神圣黄金
        bullet_surf = pygame.Surface((size*2 + 20, size*2 + 20), pygame.SRCALPHA)
        cx, cy = size + 10, size + 10
        
        gold_bright = (255, 215, 80)
        gold_deep = (200, 160, 40)
        gold_light = (255, 240, 180)
        holy_white = (255, 255, 240)
        
        # 圣光光晕（多层脉动）
        for i in range(5):
            glow_r = int(size * 0.55) + 10 - i * 4 + int(abs(math.sin(t * 3)) * 4)
            pygame.draw.circle(bullet_surf, (*gold_bright, 70 - i * 12), (cx, cy), glow_r)
        
        # 神圣粒子环绕
        for i in range(6):
            holy_angle = t * 2 + i * 1.05
            holy_r = size * 0.45 + abs(math.sin(t * 4 + i)) * 4
            hx = cx + math.cos(holy_angle) * holy_r
            hy = cy + math.sin(holy_angle) * holy_r
            pygame.draw.circle(bullet_surf, (*holy_white, 150), (int(hx), int(hy)), 2)
        
        # 黄金拳头阴影
        pygame.draw.circle(bullet_surf, gold_deep, (cx + 2, cy + 2), int(size * 0.35))
        
        # 黄金拳头主体
        pygame.draw.circle(bullet_surf, gold_bright, (cx, cy), int(size * 0.33))
        pygame.draw.circle(bullet_surf, gold_deep, (cx, cy), int(size * 0.33), 2)
        
        # 金纹浮雕
        for i in range(3):
            angle1 = (i * 120) * 0.01745
            angle2 = (i * 120 + 60) * 0.01745
            pygame.draw.arc(bullet_surf, gold_light, 
                          (cx - int(size * 0.2), cy - int(size * 0.2), int(size * 0.4), int(size * 0.4)),
                          angle1, angle2, 2)
        
        # 十字圣光
        holy_pulse = abs(math.sin(t * 4))
        cross_len = size * (0.3 + holy_pulse * 0.1)
        for angle in [0, 90, 180, 270]:
            rad = angle * 0.01745
            pygame.draw.line(bullet_surf, holy_white, (cx, cy),
                           (int(cx + math.cos(rad) * cross_len), int(cy + math.sin(rad) * cross_len)), 2)
        
        # 核心神圣光点
        pygame.draw.circle(bullet_surf, holy_white, (cx, cy), int(size * 0.1 + holy_pulse * 3))
        pygame.draw.circle(bullet_surf, (255, 255, 255), (cx, cy), int(size * 0.05 + holy_pulse * 2))
        
        # 圣光尾迹
        for i in range(4):
            trail_y = cy + size * 0.2 + i * 5
            pygame.draw.ellipse(bullet_surf, (*gold_light, 90 - i * 20),
                              (cx - size * 0.18, trail_y, size * 0.36, 4))
        
        surface.blit(bullet_surf, (x - size - 10, y - size - 10))
        return True
    
    return False


# =============================================================================
#   击中特效类 - 增强打击感
# =============================================================================

class RockImpactEffect(pygame.sprite.Sprite):
    """岩石冲击特效 - 击中敌人时的震撼效果"""
    
    def __init__(self, x, y, size='medium', color_theme=None):
        super().__init__()
        
        # 特效大小
        sizes = {'small': 40, 'medium': 60, 'large': 100, 'mega': 150}
        self.max_radius = sizes.get(size, 60)
        
        # 颜色主题 - 支持字典或字符串
        if isinstance(color_theme, dict):
            # 直接使用传入的颜色字典
            self.color_main = color_theme.get('primary', (255, 120, 40))
            self.color_bright = color_theme.get('glow', (255, 180, 80))
            self.color_dark = color_theme.get('secondary', (120, 100, 80))
        else:
            # 预设颜色主题
            themes = {
                'default': ((255, 120, 40), (255, 180, 80), (120, 100, 80)),
                'magma': ((255, 60, 20), (255, 140, 40), (80, 40, 20)),
                'obsidian': ((180, 100, 255), (220, 150, 255), (60, 40, 80)),
                'crystal': ((100, 220, 255), (200, 240, 255), (80, 150, 180)),
                'jade': ((100, 200, 120), (180, 240, 180), (60, 120, 80)),
                'golden': ((255, 215, 80), (255, 240, 180), (180, 140, 40)),
            }
            self.color_main, self.color_bright, self.color_dark = themes.get(color_theme, themes['default'])
        
        self.x = x
        self.y = y
        
        self.image = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.frame = 0
        self.duration = 18
        
        # 粒子
        self.particles = []
        self._create_particles()
        
        # 裂纹
        self.cracks = []
        self._create_cracks()
        
        # 注意：调用方负责将此特效添加到 all_sprites
    
    def _create_particles(self):
        """创建飞溅粒子"""
        for i in range(12):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(4, 12)
            self.particles.append({
                'x': self.max_radius,
                'y': self.max_radius,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 3,
                'size': random.randint(2, 6),
                'life': random.randint(10, 18),
            })
    
    def _create_cracks(self):
        """创建裂纹"""
        for i in range(6):
            angle = i * 60 * 0.01745 + random.uniform(-0.3, 0.3)
            length = self.max_radius * 0.4 + random.randint(0, int(self.max_radius * 0.2))
            self.cracks.append({
                'angle': angle,
                'length': length,
            })
    
    def update(self):
        self.frame += 1
        self.image.fill((0, 0, 0, 0))
        
        progress = self.frame / self.duration
        cx, cy = self.max_radius, self.max_radius
        
        # 冲击波环（多层扩散）
        for i in range(3):
            wave_r = int((self.max_radius * 0.3 + progress * self.max_radius * 0.7) * (1 - i * 0.15))
            wave_alpha = int(200 * (1 - progress) * (1 - i * 0.25))
            if wave_alpha > 0 and wave_r > 0:
                pygame.draw.circle(self.image, (*self.color_main, wave_alpha), (cx, cy), wave_r, 3 - i)
        
        # 中心闪光（快速消失）
        if progress < 0.4:
            flash_alpha = int(255 * (1 - progress / 0.4))
            flash_r = int(self.max_radius * 0.4 * (1 - progress))
            pygame.draw.circle(self.image, (*self.color_bright, flash_alpha), (cx, cy), flash_r)
            # 白色核心
            pygame.draw.circle(self.image, (255, 255, 255, flash_alpha), (cx, cy), flash_r // 2)
        
        # 裂纹效果
        crack_alpha = int(180 * (1 - progress * 0.8))
        if crack_alpha > 0:
            for crack in self.cracks:
                # 主裂纹
                end_x = cx + math.cos(crack['angle']) * crack['length'] * min(progress * 3, 1)
                end_y = cy + math.sin(crack['angle']) * crack['length'] * min(progress * 3, 1)
                pygame.draw.line(self.image, (*self.color_dark, crack_alpha),
                               (cx, cy), (int(end_x), int(end_y)), 2)
                # 发光
                pygame.draw.line(self.image, (*self.color_main, crack_alpha // 2),
                               (cx, cy), (int(end_x), int(end_y)), 1)
        
        # 飞溅粒子
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.5  # 重力
            p['life'] -= 1
            
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            
            p_alpha = int(255 * p['life'] / 18)
            p_size = int(p['size'] * p['life'] / 18)
            if p_size > 0:
                # 粒子光晕
                pygame.draw.circle(self.image, (*self.color_main, p_alpha // 2),
                                 (int(p['x']), int(p['y'])), p_size + 2)
                pygame.draw.circle(self.image, (*self.color_bright, p_alpha),
                                 (int(p['x']), int(p['y'])), p_size)
        
        # 岩石碎片飞溅（前期）
        if progress < 0.5:
            for i in range(4):
                angle = i * 90 * 0.01745 + progress * 2
                dist = progress * self.max_radius * 0.8
                rx = cx + math.cos(angle) * dist
                ry = cy + math.sin(angle) * dist
                frag_alpha = int(200 * (1 - progress * 2))
                frag_size = int(6 * (1 - progress))
                if frag_size > 0:
                    points = []
                    for j in range(5):
                        pa = j * 72 * 0.01745 + angle
                        pr = frag_size * (0.7 + 0.3 * (j % 2))
                        points.append((int(rx + math.cos(pa) * pr), int(ry + math.sin(pa) * pr)))
                    pygame.draw.polygon(self.image, (*self.color_dark, frag_alpha), points)
        
        if self.frame >= self.duration:
            self.kill()


class RockSmashEffect(pygame.sprite.Sprite):
    """岩石粉碎特效 - 大型击中效果（用于大招）"""
    
    def __init__(self, x, y):
        super().__init__()
        
        self.max_radius = 100
        self.x = x
        self.y = y
        
        self.image = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.frame = 0
        self.duration = 25
        
        # 大块岩石碎片
        self.chunks = []
        for i in range(8):
            angle = i * 45 * 0.01745 + random.uniform(-0.2, 0.2)
            speed = random.uniform(8, 15)
            self.chunks.append({
                'x': self.max_radius,
                'y': self.max_radius,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 5,
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-10, 10),
                'size': random.randint(8, 15),
                'life': random.randint(15, 25),
            })
        
        # 注意：调用方负责将此特效添加到 all_sprites
    
    def update(self):
        self.frame += 1
        self.image.fill((0, 0, 0, 0))
        
        progress = self.frame / self.duration
        cx, cy = self.max_radius, self.max_radius
        
        # 大型冲击波
        for i in range(4):
            wave_r = int((20 + progress * 80) * (1 - i * 0.12))
            wave_alpha = int(220 * (1 - progress) * (1 - i * 0.2))
            if wave_alpha > 0 and wave_r > 0:
                pygame.draw.circle(self.image, (255, 140, 60, wave_alpha), (cx, cy), wave_r, 4 - i)
        
        # 中心爆炸
        if progress < 0.3:
            exp_r = int(30 * (1 - progress / 0.3))
            exp_alpha = int(255 * (1 - progress / 0.3))
            pygame.draw.circle(self.image, (255, 200, 100, exp_alpha), (cx, cy), exp_r)
            pygame.draw.circle(self.image, (255, 255, 200, exp_alpha), (cx, cy), exp_r // 2)
        
        # 岩石碎块
        for chunk in self.chunks[:]:
            chunk['x'] += chunk['vx']
            chunk['y'] += chunk['vy']
            chunk['vy'] += 0.6  # 重力
            chunk['rotation'] += chunk['rot_speed']
            chunk['life'] -= 1
            
            if chunk['life'] <= 0:
                self.chunks.remove(chunk)
                continue
            
            c_alpha = int(255 * chunk['life'] / 25)
            c_size = chunk['size']
            
            # 绘制旋转的岩石块
            points = []
            for i in range(6):
                angle = math.radians(chunk['rotation'] + i * 60)
                r = c_size * (0.8 + 0.2 * (i % 2))
                points.append((int(chunk['x'] + math.cos(angle) * r),
                             int(chunk['y'] + math.sin(angle) * r)))
            
            pygame.draw.polygon(self.image, (100, 85, 70, c_alpha), points)
            pygame.draw.polygon(self.image, (255, 140, 60, c_alpha // 2), points, 2)
        
        if self.frame >= self.duration:
            self.kill()


# =============================================================================
#   岩核飞拳 - 主武器类
# =============================================================================

class RockFist(pygame.sprite.Sprite):
    """岩核飞拳 - 穿透2次，命中后爆裂成岩块AOE"""
    
    def __init__(self, x, y, damage, owner=None, bullet_theme=None):
        super().__init__()
        self.width = 32
        self.height = 32
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.damage = damage
        self.owner = owner
        self.bullet_theme = bullet_theme
        self.speed = 12
        self.pierce_count = 2  # 穿透次数
        self.pierced_enemies = set()  # 已穿透的敌人
        self.alive_flag = True
        
        # 巨石充能（通知机体）
        if owner and hasattr(owner, 'rock_charge'):
            owner.rock_charge = min(4, owner.rock_charge + 1)
    
    def update(self):
        if not self.alive_flag:
            self.kill()
            return
        
        self.rect.y -= self.speed
        
        # 绘制
        self._draw()
        
        # 碰撞检测
        hits = pygame.sprite.spritecollide(self, mobs, False)
        for mob in hits:
            if mob not in self.pierced_enemies:
                self.pierced_enemies.add(mob)
                mob.take_damage(self.damage)
                
                # 【特效】生成岩石冲击特效增强打击感
                hit_effect = RockImpactEffect(mob.rect.centerx, mob.rect.centery, 'medium', self._get_color_theme())
                all_sprites.add(hit_effect)
                
                # 【修复】给玩家充能大招和巨石能量
                if self.owner:
                    self._charge_ult(self.damage)
                    # 击中敌人时给巨石充能条充能
                    if hasattr(self.owner, 'rock_charge'):
                        self.owner.rock_charge = min(4, self.owner.rock_charge + 0.5)
                
                # 生成AOE碎片
                self._spawn_debris()
                
                self.pierce_count -= 1
                if self.pierce_count <= 0:
                    self.alive_flag = False
                    break
        
        # 出界
        if self.rect.bottom < -50:
            self.alive_flag = False
    
    def _charge_ult(self, damage):
        """给玩家充能大招"""
        if not self.owner:
            return
        ult_charge_rate = getattr(self.owner, 'ult_charge_rate', 1.0)
        ult_charge_gain = (damage / 10) * ult_charge_rate
        
        # 充能三个大招
        if hasattr(self.owner, 'ult_charge'):
            self.owner.ult_charge = min(self.owner.max_ult_charge, self.owner.ult_charge + ult_charge_gain)
        if hasattr(self.owner, 'ult2_charge'):
            self.owner.ult2_charge = min(self.owner.max_ult2_charge, self.owner.ult2_charge + ult_charge_gain * 0.8)
        if hasattr(self.owner, 'ult3_charge'):
            self.owner.ult3_charge = min(self.owner.max_ult3_charge, self.owner.ult3_charge + ult_charge_gain * 0.6)
    
    def _spawn_debris(self):
        """生成岩块碎片AOE"""
        for i in range(4):
            angle = i * 90 + random.randint(-20, 20)
            debris = RockDebris(self.rect.centerx, self.rect.centery, 
                              self.damage * 0.3, angle, self.owner)
            all_sprites.add(debris)
            bullets.add(debris)
    
    def _get_color_theme(self):
        """获取当前涂装的颜色主题，用于击中特效"""
        effects = []
        if self.bullet_theme and self.bullet_theme.get('effects'):
            effects = self.bullet_theme.get('effects', [])
        
        # 根据涂装效果返回不同颜色主题
        if "magma_fist" in effects:
            return {'primary': (255, 80, 20), 'secondary': (60, 40, 30), 'glow': (255, 120, 40)}
        elif "obsidian_fist" in effects:
            return {'primary': (180, 100, 255), 'secondary': (20, 15, 25), 'glow': (220, 150, 255)}
        elif "crystal_fist" in effects:
            return {'primary': (100, 220, 255), 'secondary': (200, 230, 255), 'glow': (150, 240, 255)}
        elif "jade_fist" in effects:
            return {'primary': (100, 180, 120), 'secondary': (220, 180, 80), 'glow': (150, 220, 150)}
        elif "golden_fist" in effects:
            return {'primary': (255, 215, 80), 'secondary': (255, 240, 180), 'glow': (255, 230, 120)}
        else:
            # 默认熔岩风格
            return {'primary': (255, 120, 40), 'secondary': (120, 115, 110), 'glow': (255, 160, 60)}
    
    def _draw(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.width // 2, self.height // 2
        t = pygame.time.get_ticks() / 1000.0
        
        # 获取涂装效果
        effects = []
        if self.bullet_theme and self.bullet_theme.get('effects'):
            effects = self.bullet_theme.get('effects', [])
        
        # 根据涂装效果选择形状
        rock_gray = (120, 115, 110)
        core_orange = (255, 120, 40)
        dark_gray = (80, 75, 70)
        
        # 处理不同涂装效果
        if "magma_fist" in effects:
            rock_gray = (60, 40, 30)
            core_orange = (255, 80, 20)
        elif "obsidian_fist" in effects:
            rock_gray = (20, 15, 25)
            core_orange = (180, 100, 255)
        elif "crystal_fist" in effects:
            rock_gray = (100, 220, 255)
            core_orange = (255, 150, 200)
        elif "jade_fist" in effects:
            rock_gray = (100, 180, 120)
            core_orange = (220, 180, 80)
        elif "golden_fist" in effects:
            rock_gray = (255, 215, 80)
            core_orange = (255, 240, 180)
        
        # 核心光晕
        for i in range(3):
            glow_r = 14 - i * 3
            glow_alpha = 100 - i * 30
            glow_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*core_orange, glow_alpha), (cx, cy), glow_r)
            self.image.blit(glow_surf, (0, 0))
        
        # 拳头主体
        fist_points = []
        for i in range(8):
            angle = i * 45 * 0.01745
            r = 10 + random.Random(i + 5).randint(-1, 2)
            fist_points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
        pygame.draw.polygon(self.image, rock_gray, fist_points)
        pygame.draw.polygon(self.image, dark_gray, fist_points, 2)
        
        # 核心裂纹
        crack_pulse = abs(math.sin(t * 5))
        for i in range(3):
            seed = random.Random(i + 7)
            sx = cx + seed.randint(-4, 4)
            sy = cy + seed.randint(-4, 4)
            ex = cx + seed.randint(-6, 6)
            ey = cy + seed.randint(-6, 6)
            glow_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.line(glow_surf, (*core_orange, int(150 + crack_pulse * 100)), 
                           (sx, sy), (ex, ey), 2)
            self.image.blit(glow_surf, (0, 0))


class RockDebris(pygame.sprite.Sprite):
    """岩块碎片 - AOE爆裂产物"""
    
    def __init__(self, x, y, damage, angle, owner=None):
        super().__init__()
        self.width = 16
        self.height = 16
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.damage = damage
        self.owner = owner
        
        # 运动方向
        self.angle_rad = math.radians(angle)
        self.speed = 8
        self.lifetime = 30  # 帧
        
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 移动
        self.rect.x += math.cos(self.angle_rad) * self.speed
        self.rect.y += math.sin(self.angle_rad) * self.speed
        self.speed *= 0.92  # 减速
        
        # 绘制
        self._draw()
        
        # 碰撞
        hits = pygame.sprite.spritecollide(self, mobs, False)
        for mob in hits:
            mob.take_damage(self.damage)
            
            # 【特效】生成小型岩石冲击特效
            hit_effect = RockImpactEffect(mob.rect.centerx, mob.rect.centery, 'small')
            all_sprites.add(hit_effect)
            
            # 【修复】给玩家充能大招和巨石能量
            self._charge_ult(self.damage)
            if self.owner and hasattr(self.owner, 'rock_charge'):
                self.owner.rock_charge = min(4, self.owner.rock_charge + 0.2)
            self.kill()
            break
    
    def _charge_ult(self, damage):
        """给玩家充能大招"""
        if not self.owner:
            return
        ult_charge_rate = getattr(self.owner, 'ult_charge_rate', 1.0)
        ult_charge_gain = (damage / 10) * ult_charge_rate
        if hasattr(self.owner, 'ult_charge'):
            self.owner.ult_charge = min(self.owner.max_ult_charge, self.owner.ult_charge + ult_charge_gain)
        if hasattr(self.owner, 'ult2_charge'):
            self.owner.ult2_charge = min(self.owner.max_ult2_charge, self.owner.ult2_charge + ult_charge_gain * 0.8)
        if hasattr(self.owner, 'ult3_charge'):
            self.owner.ult3_charge = min(self.owner.max_ult3_charge, self.owner.ult3_charge + ult_charge_gain * 0.6)
    
    def _draw(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.width // 2, self.height // 2
        t = pygame.time.get_ticks() / 1000.0
        
        debris_brown = (140, 100, 70)
        rock_gray = (120, 115, 110)
        core_orange = (255, 120, 40)
        
        # 不规则碎片
        debris_points = []
        for i in range(5):
            angle = i * 72 * 0.01745 + t * 3
            r = 5 + random.Random(i).randint(-1, 2)
            debris_points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
        pygame.draw.polygon(self.image, debris_brown, debris_points)
        pygame.draw.polygon(self.image, rock_gray, debris_points, 1)
        
        # 尾迹火星
        alpha = int(200 * (self.lifetime / 30))
        trail_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.circle(trail_surf, (*core_orange, alpha), (cx, cy + 3), 3)
        self.image.blit(trail_surf, (0, 0))


# =============================================================================
#   F大招 - 岩拳暴雨（至尊品质震撼版）
# =============================================================================

class RockFistBarrage(pygame.sprite.Sprite):
    """岩拳暴雨 - 至尊震撼版
    
    2秒内连射6枚巨型岩核拳，附带以下震撼效果：
    1. 全屏大地震动背景 + 岩浆涌动
    2. 发射时巨型能量爆发 + 岩浆喷发
    3. 巨型拳头带熔岩尾迹 + 冲击波
    4. 屏幕边缘岩石碎裂效果 + 裂纹蔓延
    5. 巨型能量环绕玩家 + 浮空岩石
    """
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        all_sprites.add(self)
        
        # 全屏特效画布
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        self.duration = 180  # 3秒 @ 60fps（延长以展示更多特效）
        self.fist_count = 8  # 增加到8枚
        self.fist_interval = 18  # 更快的发射间隔
        self.fist_timer = 0
        self.fists_fired = 0
        
        self.base_damage = owner.damage * 3
        
        # 粒子系统
        self.particles = []
        self.max_particles = 120  # 限制粒子数量
        self.lava_streams = []
        self.rock_debris = []
        
        # 浮空岩石
        self.floating_rocks = []
        self._init_floating_rocks()
        
        # 地面裂纹
        self.ground_cracks = []
        self._init_ground_cracks()
        
        # 屏幕震动
        self.screen_shake = 0
        self.shake_intensity = 0
        
        # 启动时的巨大冲击
        self._create_initial_shockwave()
    
    def _init_floating_rocks(self):
        """初始化浮空岩石"""
        ox, oy = self.owner.rect.centerx, self.owner.rect.centery
        for i in range(8):
            angle = i * 45 * 0.01745
            self.floating_rocks.append({
                'base_angle': angle,
                'distance': 60 + (i % 3) * 15,
                'size': 10 + (i % 4) * 3,
                'rotation': i * 30,
                'rot_speed': 2 + (i % 3),
                'bob_offset': i * 0.5,
            })
    
    def _init_ground_cracks(self):
        """初始化地面裂纹"""
        for i in range(10):
            angle = i * 36 * 0.01745
            self.ground_cracks.append({
                'angle': angle,
                'length': 0,
                'max_length': 120 + (i % 4) * 30,
                'segments': [],
                'active': False,
            })
    
    def _create_initial_shockwave(self):
        """创建启动冲击波"""
        ox, oy = self.owner.rect.centerx, self.owner.rect.centery
        # 生成岩浆喷发
        for i in range(30):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 15)
            self.particles.append({
                'x': ox, 'y': oy,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 8,
                'color': random.choice([(255, 120, 40), (255, 180, 80), (255, 80, 20)]),
                'life': random.randint(30, 60),
                'max_life': 60,
                'size': random.randint(4, 10),
                'type': 'lava'
            })
        self.shake_intensity = 15
    
    def _add_particle(self, x, y, vx, vy, color, life, size=3, ptype='normal'):
        # 限制粒子数量防止卡顿
        if len(self.particles) >= self.max_particles:
            return
        self.particles.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color, 'life': life, 'max_life': life, 'size': size, 'type': ptype
        })
    
    def _update_particles(self):
        """更新并绘制粒子"""
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            
            # 重力和减速
            if p['type'] == 'lava':
                p['vy'] += 0.3  # 重力
                p['vx'] *= 0.98
            
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            
            alpha = int(255 * p['life'] / p['max_life'])
            size = int(p['size'] * (0.5 + 0.5 * p['life'] / p['max_life']))
            if size > 0 and 0 <= p['x'] < WIDTH and 0 <= p['y'] < HEIGHT:
                # 熔岩粒子有光晕
                if p['type'] == 'lava':
                    for glow in range(2):
                        glow_r = size + glow * 2
                        glow_alpha = alpha // (glow + 2)
                        pygame.draw.circle(self.image, (*p['color'], glow_alpha),
                                         (int(p['x']), int(p['y'])), glow_r)
                pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                                 (int(p['x']), int(p['y'])), size)
    
    def update(self):
        self.duration -= 1
        self.fist_timer += 1
        self.image.fill((0, 0, 0, 0))
        
        t = pygame.time.get_ticks() / 1000.0
        progress = 1 - (self.duration / 150)
        
        # 全屏大地震动背景
        quake_intensity = 0.3 + abs(math.sin(t * 15)) * 0.3
        dark_alpha = int(40 * quake_intensity)
        pygame.draw.rect(self.image, (80, 40, 20, dark_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 屏幕边缘裂纹效果
        self._draw_screen_cracks(t)
        
        # 发射岩拳
        if self.fist_timer >= self.fist_interval and self.fists_fired < self.fist_count:
            self.fist_timer = 0
            self.fists_fired += 1
            self._fire_giant_fist()
            self.shake_intensity = 12
        
        # 屏幕震动
        if self.shake_intensity > 0:
            self.shake_intensity *= 0.9
            # 震动效果在绘制中体现为边缘光效抖动
            shake_x = random.randint(-int(self.shake_intensity), int(self.shake_intensity))
            shake_y = random.randint(-int(self.shake_intensity), int(self.shake_intensity))
            # 绘制震动边缘
            if self.shake_intensity > 2:
                pygame.draw.rect(self.image, (255, 120, 40, int(self.shake_intensity * 8)),
                               (shake_x, shake_y, WIDTH, 5))
                pygame.draw.rect(self.image, (255, 120, 40, int(self.shake_intensity * 8)),
                               (shake_x, HEIGHT - 5 + shake_y, WIDTH, 5))
        
        # 玩家周围的能量环（增强版）
        ox, oy = self.owner.rect.centerx, self.owner.rect.centery
        ring_pulse = abs(math.sin(t * 6))
        
        # 多层能量环
        for i in range(5):
            ring_r = 35 + i * 12 + int(ring_pulse * 8)
            ring_alpha = 150 - i * 25
            ring_width = 4 - i // 2
            pygame.draw.circle(self.image, (255, 140, 60, ring_alpha), (ox, oy), ring_r, ring_width)
            # 内层发光
            if i == 0:
                pygame.draw.circle(self.image, (255, 200, 100, ring_alpha // 2), (ox, oy), ring_r - 5, 2)
        
        # 浮空岩石环绕
        self._draw_floating_rocks(t, ox, oy)
        
        # 地面裂纹扩散
        self._draw_ground_cracks(t, ox)
        
        # 地面熔岩裂纹
        self._draw_ground_lava(t)
        
        self._update_particles()
        
        if self.duration <= 0:
            self.kill()
    
    def _draw_screen_cracks(self, t):
        """绘制屏幕边缘裂纹"""
        crack_color = (120, 80, 50)
        lava_color = (255, 120, 40)
        
        # 从四个角延伸的裂纹
        corners = [(0, 0), (WIDTH, 0), (0, HEIGHT), (WIDTH, HEIGHT)]
        for ci, (cx, cy) in enumerate(corners):
            random.seed(ci + 42)
            for crack in range(3):
                points = [(cx, cy)]
                px, py = cx, cy
                for seg in range(6):
                    angle = random.uniform(0.3, 1.2) if ci < 2 else random.uniform(1.9, 2.8)
                    if ci % 2 == 1:
                        angle = math.pi - angle
                    length = 30 + random.randint(0, 20)
                    px += math.cos(angle) * length
                    py += math.sin(angle) * length
                    points.append((int(px), int(py)))
                
                if len(points) >= 2:
                    pygame.draw.lines(self.image, crack_color, False, points, 3)
                    # 裂纹发光
                    pulse = abs(math.sin(t * 4 + ci + crack))
                    if pulse > 0.5:
                        pygame.draw.lines(self.image, (*lava_color, int(pulse * 150)), False, points, 2)
    
    def _draw_ground_lava(self, t):
        """绘制地面熔岩"""
        base_y = HEIGHT - 80
        
        # 熔岩波浪
        points_top = []
        points_bottom = []
        for x in range(0, WIDTH + 20, 20):
            wave = math.sin(t * 3 + x * 0.02) * 15 + math.sin(t * 5 + x * 0.03) * 8
            points_top.append((x, base_y + int(wave)))
            points_bottom.append((x, HEIGHT))
        
        # 闭合多边形
        points = points_top + points_bottom[::-1]
        if len(points) >= 3:
            # 熔岩层
            pygame.draw.polygon(self.image, (60, 30, 15, 100), points)
            # 发光边缘
            pygame.draw.lines(self.image, (255, 120, 40, 180), False, points_top, 4)
            pygame.draw.lines(self.image, (255, 200, 100, 120), False, points_top, 2)
        
        # 熔岩气泡
        for i in range(5):
            bx = (i * 120 + int(t * 30)) % WIDTH
            by = base_y + 20 + int(math.sin(t * 2 + i) * 10)
            br = 5 + int(abs(math.sin(t * 4 + i * 1.5)) * 5)
            pygame.draw.circle(self.image, (255, 180, 80, 150), (bx, by), br)
            pygame.draw.circle(self.image, (255, 100, 40, 200), (bx, by), br, 2)
    
    def _draw_floating_rocks(self, t, ox, oy):
        """绘制浮空岩石环绕"""
        for i, rock in enumerate(self.floating_rocks):
            # 计算当前位置
            angle = rock['base_angle'] + t * 2  # 环绕速度
            bob = math.sin(t * 3 + rock['bob_offset']) * 8  # 上下浮动
            rx = ox + math.cos(angle) * rock['distance']
            ry = oy + math.sin(angle) * rock['distance'] * 0.6 + bob  # 椭圆轨道
            
            rock['rotation'] += rock['rot_speed']
            
            # 绘制旋转的岩石
            size = rock['size']
            points = []
            for j in range(6):
                pa = math.radians(rock['rotation'] + j * 60)
                pr = size * (0.7 + 0.3 * (j % 2))
                points.append((int(rx + math.cos(pa) * pr), int(ry + math.sin(pa) * pr)))
            
            if all(0 <= p[0] < WIDTH and 0 <= p[1] < HEIGHT for p in points):
                # 岩石本体
                pygame.draw.polygon(self.image, (100, 85, 70), points)
                pygame.draw.polygon(self.image, (140, 120, 100), points, 2)
                # 熔岩光芒
                glow_alpha = int(100 + abs(math.sin(t * 5 + i)) * 80)
                pygame.draw.circle(self.image, (255, 120, 40, glow_alpha), (int(rx), int(ry)), size // 2)
    
    def _draw_ground_cracks(self, t, ox):
        """绘制从脚下扩散的地面裂纹"""
        progress = 1 - (self.duration / 180)
        base_y = self.owner.rect.bottom
        
        for i, crack in enumerate(self.ground_cracks):
            # 逐步激活裂纹
            if progress > i * 0.08:
                crack['active'] = True
            
            if not crack['active']:
                continue
            
            # 裂纹生长
            if crack['length'] < crack['max_length']:
                crack['length'] += 4
            
            # 生成裂纹路径
            if len(crack['segments']) < int(crack['length'] / 12):
                if not crack['segments']:
                    crack['segments'].append((ox, base_y))
                
                last = crack['segments'][-1]
                angle = crack['angle']
                variation = math.sin(len(crack['segments']) * 0.5) * 0.3
                new_x = last[0] + math.cos(angle + variation) * 12
                new_y = last[1] + math.sin(angle + variation) * 12
                crack['segments'].append((int(new_x), int(new_y)))
            
            # 绘制裂纹
            if len(crack['segments']) >= 2:
                # 裂纹主体
                pygame.draw.lines(self.image, (80, 60, 50), False, crack['segments'], 3)
                # 熔岩发光
                lava_pulse = abs(math.sin(t * 6 + i * 0.5))
                lava_alpha = int(120 * lava_pulse)
                if lava_alpha > 0:
                    pygame.draw.lines(self.image, (255, 100, 30, lava_alpha), False, crack['segments'], 2)

    def _fire_giant_fist(self):
        """发射巨型岩核拳 - 带震撼特效"""
        cx = self.owner.rect.centerx + ((self.fists_fired * 37) % 80) - 40
        cy = self.owner.rect.top - 30
        
        # 发射冲击波特效
        shockwave = RockImpactEffect(cx, cy, 'large', 
                                    {'primary': (255, 140, 60), 'secondary': (120, 80, 50), 'glow': (255, 200, 100)})
        all_sprites.add(shockwave)
        
        # 发射时喷发粒子（减少数量）
        if len(self.particles) < self.max_particles - 20:
            for i in range(12):
                angle = -math.pi * 0.2 - i * 0.1
                speed = 8 + (i % 5) * 2
                colors = [(255, 140, 60), (255, 200, 100), (200, 80, 30)]
                self._add_particle(cx, cy,
                                 math.cos(angle) * speed,
                                 math.sin(angle) * speed,
                                 colors[i % 3],
                                 25 + (i % 3) * 8, 5 + (i % 4), 'lava')
        
        # 发射光环
        for i in range(8):
            angle = i * 45 * 0.01745
            self._add_particle(cx + math.cos(angle) * 35, cy + math.sin(angle) * 35,
                             math.cos(angle) * 4, math.sin(angle) * 4,
                             (255, 200, 100), 18, 6, 'normal')
        
        # 屏幕闪烁
        self.shake_intensity = 15
        
        fist = GiantRockFist(cx, cy, self.base_damage, self.owner, self.fists_fired)
        all_sprites.add(fist)
        bullets.add(fist)


class GiantRockFist(pygame.sprite.Sprite):
    """巨型岩核拳 - 穿透无限，每过1屏体积+20%"""
    
    def __init__(self, x, y, damage, owner, index):
        super().__init__()
        self.base_size = 48
        self.current_size = self.base_size
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.damage = damage
        self.owner = owner
        self.index = index
        self.speed = 10
        self.travel_distance = 0
        self.pierced_enemies = set()
        
    def update(self):
        # 移动
        self.rect.y -= self.speed
        self.travel_distance += self.speed
        
        # 每过1屏(720px)体积+20%
        screens_passed = self.travel_distance / HEIGHT
        self.current_size = int(self.base_size * (1 + screens_passed * 0.2))
        
        # 绘制
        self._draw()
        
        # 碰撞（无限穿透）
        hits = pygame.sprite.spritecollide(self, mobs, False)
        for mob in hits:
            if mob not in self.pierced_enemies:
                self.pierced_enemies.add(mob)
                mob.take_damage(self.damage)
                # 【修复】给玩家充能大招
                self._charge_ult(self.damage)
                # 击中特效
                self._spawn_impact_effect(mob)
        
        # 出界
        if self.rect.bottom < -100:
            self.kill()
    
    def _charge_ult(self, damage):
        """给玩家充能大招"""
        if not self.owner:
            return
        ult_charge_rate = getattr(self.owner, 'ult_charge_rate', 1.0)
        ult_charge_gain = (damage / 10) * ult_charge_rate
        if hasattr(self.owner, 'ult_charge'):
            self.owner.ult_charge = min(self.owner.max_ult_charge, self.owner.ult_charge + ult_charge_gain)
        if hasattr(self.owner, 'ult2_charge'):
            self.owner.ult2_charge = min(self.owner.max_ult2_charge, self.owner.ult2_charge + ult_charge_gain * 0.8)
        if hasattr(self.owner, 'ult3_charge'):
            self.owner.ult3_charge = min(self.owner.max_ult3_charge, self.owner.ult3_charge + ult_charge_gain * 0.6)
    
    def _spawn_impact_effect(self, mob):
        """击中时生成震撼特效和碎片"""
        # 【特效】生成大型岩石粉碎特效
        smash_effect = RockSmashEffect(mob.rect.centerx, mob.rect.centery)
        all_sprites.add(smash_effect)
        
        # 生成碎片
        for i in range(6):
            angle = i * 60 + random.randint(-15, 15)
            debris = RockDebris(mob.rect.centerx, mob.rect.centery,
                              self.damage * 0.2, angle, self.owner)
            all_sprites.add(debris)
            bullets.add(debris)
    
    def _draw(self):
        # 重建surface以适应尺寸变化
        surf_size = max(80, self.current_size + 20)
        self.image = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)
        
        cx, cy = surf_size // 2, surf_size // 2
        t = pygame.time.get_ticks() / 1000.0
        
        rock_gray = (120, 115, 110)
        core_orange = (255, 120, 40)
        crack_glow = (255, 180, 80)
        dark_gray = (80, 75, 70)
        
        # 巨大光晕
        for i in range(5):
            glow_r = self.current_size // 2 + 10 - i * 4
            glow_alpha = 120 - i * 22
            glow_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*core_orange, glow_alpha), (cx, cy), glow_r)
            self.image.blit(glow_surf, (0, 0))
        
        # 巨型拳头
        fist_points = []
        for i in range(10):
            angle = i * 36 * 0.01745
            r = self.current_size // 2.5 + random.Random(i + 99).randint(-4, 6)
            fist_points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
        pygame.draw.polygon(self.image, rock_gray, fist_points)
        pygame.draw.polygon(self.image, (200, 100, 30), fist_points, 3)
        
        # 熔岩裂纹网
        for i in range(6):
            seed = random.Random(i + 33)
            sx = cx + seed.randint(-self.current_size//4, self.current_size//4)
            sy = cy + seed.randint(-self.current_size//4, self.current_size//4)
            for j in range(2):
                ex = sx + seed.randint(-self.current_size//5, self.current_size//5)
                ey = sy + seed.randint(-self.current_size//5, self.current_size//5)
                pygame.draw.line(self.image, crack_glow, (int(sx), int(sy)), (int(ex), int(ey)), 2)
                sx, sy = ex, ey
        
        # 核心发光
        pygame.draw.circle(self.image, crack_glow, (cx, cy), self.current_size // 5)
        pygame.draw.circle(self.image, (255, 240, 200), (cx, cy), self.current_size // 8)


# =============================================================================
#   G大招 - 巨石护盾（至尊品质震撼版）
# =============================================================================

class RockShield(pygame.sprite.Sprite):
    """巨石护盾 - 至尊震撼版
    
    展开环形岩石阵，附带以下震撼效果：
    1. 护盾升起时地面裂开动画
    2. 环形岩柱阵+中央能量核心
    3. 岩浆光环脉动
    4. 护盾上的符文和能量流动
    5. 破碎时全屏岩石风暴+地震效果
    """
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        all_sprites.add(self)
        
        # 使用全屏画布以绘制震撼效果
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        # 护盾属性
        self.duration = 300  # 5秒（延长以展示特效）
        self.hp = 800  # 提高护盾生命
        self.max_hp = 800
        self.base_damage = owner.damage * 2.5
        
        # 护盾核心位置
        self.shield_x = owner.rect.centerx
        self.shield_y = owner.rect.top - 50
        self.shield_width = 220
        self.shield_height = 80
        
        # 动画状态
        self.rise_progress = 0  # 升起进度
        self.phase = 'rising'  # rising -> active -> breaking
        
        # 粒子系统
        self.particles = []
        self.energy_lines = []
        
        # 岩柱数据
        self.pillars = []
        self._init_pillars()
        
        # 符文
        self.runes = []
        self._init_runes()
        
        # 创建升起特效
        self._create_rise_effect()
    
    def _init_pillars(self):
        """初始化岩柱"""
        pillar_count = 9
        for i in range(pillar_count):
            progress = i / (pillar_count - 1)
            x = -self.shield_width // 2 + progress * self.shield_width
            self.pillars.append({
                'x': x,
                'height': random.randint(40, 70),
                'width': random.randint(20, 30),
                'offset': random.uniform(0, 2 * math.pi),
                'crack_seed': random.randint(0, 1000),
            })
    
    def _init_runes(self):
        """初始化护盾符文"""
        for i in range(6):
            self.runes.append({
                'angle': i * 60,
                'r': random.randint(60, 80),
                'type': random.choice(['triangle', 'circle', 'diamond']),
                'pulse_offset': random.uniform(0, 2 * math.pi),
            })
    
    def _create_rise_effect(self):
        """创建护盾升起特效"""
        cx = self.owner.rect.centerx
        cy = self.owner.rect.top
        
        # 地面裂开粒子
        for i in range(40):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 10)
            self.particles.append({
                'x': cx + random.randint(-60, 60),
                'y': cy + random.randint(-20, 20),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 5,
                'color': random.choice([(120, 100, 80), (100, 80, 60), (80, 60, 40)]),
                'life': random.randint(30, 60),
                'max_life': 60,
                'size': random.randint(3, 8),
                'type': 'rock'
            })
    
    def _add_particle(self, x, y, vx, vy, color, life, size=3, ptype='normal'):
        # 限制粒子数量防止卡顿
        if len(self.particles) >= 100:
            return
        self.particles.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color, 'life': life, 'max_life': life, 'size': size, 'type': ptype
        })
    
    def _update_particles(self):
        """更新并绘制粒子"""
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            
            if p['type'] == 'rock':
                p['vy'] += 0.4  # 重力
            elif p['type'] == 'lava':
                p['vy'] += 0.2
            
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            
            alpha = int(255 * p['life'] / p['max_life'])
            size = int(p['size'] * (0.5 + 0.5 * p['life'] / p['max_life']))
            if size > 0 and 0 <= p['x'] < WIDTH and 0 <= p['y'] < HEIGHT:
                if p['type'] == 'lava':
                    for glow in range(2):
                        glow_r = size + glow * 2
                        glow_alpha = alpha // (glow + 2)
                        pygame.draw.circle(self.image, (*p['color'], glow_alpha),
                                         (int(p['x']), int(p['y'])), glow_r)
                pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                                 (int(p['x']), int(p['y'])), size)
    
    def update(self):
        self.duration -= 1
        self.image.fill((0, 0, 0, 0))
        
        # 更新护盾位置
        self.shield_x = self.owner.rect.centerx
        self.shield_y = self.owner.rect.top - 50
        
        t = pygame.time.get_ticks() / 1000.0
        hp_ratio = self.hp / self.max_hp
        
        # 阶段处理
        if self.phase == 'rising':
            self.rise_progress = min(1, self.rise_progress + 0.05)
            if self.rise_progress >= 1:
                self.phase = 'active'
        
        # 碰撞检测（使用自定义矩形）
        shield_rect = pygame.Rect(
            self.shield_x - self.shield_width // 2,
            self.shield_y - self.shield_height // 2,
            self.shield_width,
            self.shield_height
        )
        
        for bullet in list(enemy_bullets):
            if shield_rect.colliderect(bullet.rect):
                self.hp -= getattr(bullet, 'damage', 10)
                # 吸收特效
                self._add_particle(bullet.rect.centerx, bullet.rect.centery,
                                 0, -2, (255, 180, 80), 15, 4, 'lava')
                bullet.kill()
        
        # 绘制
        self._draw_shield(t, hp_ratio)
        self._update_particles()
        
        # 护盾破碎或超时
        if self.hp <= 0 or self.duration <= 0:
            self._mega_explode()
            self.kill()
    
    def _draw_shield(self, t, hp_ratio):
        """绘制震撼护盾"""
        cx, cy = self.shield_x, self.shield_y
        
        rock_gray = (120, 115, 110)
        rock_dark = (80, 70, 65)
        core_orange = (255, 120, 40)
        lava_bright = (255, 200, 100)
        
        rise = self.rise_progress
        
        # 背景地面裂纹
        if rise > 0.3:
            self._draw_ground_cracks(cx, self.owner.rect.bottom, t)
        
        # 岩浆光环（环绕护盾）
        ring_r = 80 + int(math.sin(t * 3) * 10)
        for i in range(3):
            r = ring_r + i * 20
            alpha = int((80 - i * 25) * hp_ratio * rise)
            pygame.draw.circle(self.image, (*core_orange, alpha), (cx, cy), r, 3)
        
        # 能量流线（从玩家到护盾）
        if rise > 0.5:
            for i in range(4):
                wave = math.sin(t * 6 + i * 1.5) * 15
                line_x = self.owner.rect.centerx + (i - 1.5) * 20 + wave
                pygame.draw.line(self.image, (*lava_bright, int(100 * hp_ratio)),
                               (int(line_x), self.owner.rect.top),
                               (int(line_x + wave * 0.5), int(cy + 20)), 2)
        
        # 岩柱阵
        for pillar in self.pillars:
            px = cx + pillar['x']
            pillar_h = int(pillar['height'] * rise)
            pillar_w = pillar['width']
            
            if pillar_h < 5:
                continue
            
            py = cy - pillar_h // 2
            
            # 岩柱主体
            pygame.draw.rect(self.image, rock_gray,
                           (px - pillar_w // 2, py, pillar_w, pillar_h))
            pygame.draw.rect(self.image, rock_dark,
                           (px - pillar_w // 2, py, pillar_w, pillar_h), 2)
            
            # 岩柱顶部尖端
            top_points = [
                (px - pillar_w // 2 - 3, py),
                (px, py - 12),
                (px + pillar_w // 2 + 3, py)
            ]
            pygame.draw.polygon(self.image, rock_gray, top_points)
            pygame.draw.polygon(self.image, rock_dark, top_points, 2)
            
            # 岩柱裂纹发光
            random.seed(pillar['crack_seed'])
            crack_pulse = abs(math.sin(t * 4 + pillar['offset']))
            if hp_ratio < 0.7 or crack_pulse > 0.6:
                for crack in range(2):
                    cx1 = px + random.randint(-pillar_w // 3, pillar_w // 3)
                    cy1 = py + random.randint(5, pillar_h - 5)
                    cx2 = cx1 + random.randint(-5, 5)
                    cy2 = cy1 + random.randint(5, 15)
                    pygame.draw.line(self.image, (*core_orange, int(crack_pulse * 200)),
                                   (cx1, cy1), (cx2, cy2), 2)
        
        # 符文环绕
        for rune in self.runes:
            rune_angle = math.radians(rune['angle'] + t * 30)
            rx = cx + math.cos(rune_angle) * rune['r']
            ry = cy + math.sin(rune_angle) * rune['r'] * 0.4
            
            pulse = abs(math.sin(t * 4 + rune['pulse_offset']))
            rune_alpha = int((100 + pulse * 100) * hp_ratio * rise)
            
            if rune['type'] == 'triangle':
                tri_r = 8
                tri_points = [
                    (rx, ry - tri_r),
                    (rx - tri_r * 0.866, ry + tri_r * 0.5),
                    (rx + tri_r * 0.866, ry + tri_r * 0.5)
                ]
                pygame.draw.polygon(self.image, (*lava_bright, rune_alpha), tri_points, 2)
            elif rune['type'] == 'circle':
                pygame.draw.circle(self.image, (*lava_bright, rune_alpha), (int(rx), int(ry)), 6, 2)
            else:  # diamond
                d_points = [(rx, ry - 7), (rx + 5, ry), (rx, ry + 7), (rx - 5, ry)]
                pygame.draw.polygon(self.image, (*lava_bright, rune_alpha), d_points, 2)
        
        # 低血量警告效果
        if hp_ratio < 0.3:
            shake = random.randint(-3, 3)
            pygame.draw.rect(self.image, (255, 50, 50, int(60 * (1 - hp_ratio))),
                           (cx - self.shield_width // 2 + shake, cy - 50, self.shield_width, 100), 3)
        
        # HP条
        bar_w = 100
        bar_h = 6
        bar_x = cx - bar_w // 2
        bar_y = cy + 50
        pygame.draw.rect(self.image, (40, 40, 40), (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2))
        pygame.draw.rect(self.image, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h))
        hp_color = (60, 200, 80) if hp_ratio > 0.5 else ((255, 180, 0) if hp_ratio > 0.25 else (255, 60, 60))
        pygame.draw.rect(self.image, hp_color, (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))
    
    def _draw_ground_cracks(self, cx, ground_y, t):
        """绘制地面裂纹"""
        crack_color = (100, 80, 60)
        lava_color = (255, 100, 40)
        
        for i in range(5):
            random.seed(i + 77)
            points = [(cx + (i - 2) * 40, ground_y)]
            px, py = points[0]
            for seg in range(4):
                angle = random.uniform(math.pi * 0.3, math.pi * 0.7)
                length = 20 + random.randint(0, 15)
                px += math.cos(angle) * length * random.choice([-1, 1])
                py += math.sin(angle) * length
                points.append((int(px), int(py)))
            
            if len(points) >= 2:
                pygame.draw.lines(self.image, crack_color, False, points, 2)
                if abs(math.sin(t * 3 + i)) > 0.5:
                    pygame.draw.lines(self.image, (*lava_color, 100), False, points, 1)
    
    def _mega_explode(self):
        """巨大爆炸 - 全屏岩石风暴"""
        cx, cy = self.shield_x, self.shield_y
        
        # 生成大量碎片
        for i in range(24):
            angle = i * 15
            debris = ShieldDebris(cx, cy, self.base_damage, angle, self.owner)
            all_sprites.add(debris)
            bullets.add(debris)
        
        # 创建全屏爆炸效果精灵
        explosion = RockShieldExplosion(cx, cy, self.base_damage * 0.5, self.owner)
        all_sprites.add(explosion)


class ShieldDebris(pygame.sprite.Sprite):
    """护盾碎片 - 爆炸向外飞散造成真伤"""
    
    def __init__(self, x, y, damage, angle, owner):
        super().__init__()
        self.width = 24
        self.height = 24
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.damage = damage
        self.owner = owner
        self.is_true_damage = True  # 真伤标记
        
        self.angle_rad = math.radians(angle)
        self.speed = 15
        self.lifetime = 40
        
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 移动
        self.rect.x += math.cos(self.angle_rad) * self.speed
        self.rect.y += math.sin(self.angle_rad) * self.speed
        self.speed *= 0.95
        
        # 绘制
        self._draw()
        
        # 碰撞
        hits = pygame.sprite.spritecollide(self, mobs, False)
        for mob in hits:
            # 真伤忽略护甲
            if hasattr(mob, 'take_true_damage'):
                mob.take_true_damage(self.damage)
            else:
                mob.take_damage(self.damage)
            
            # 【特效】生成中型岩石冲击特效（护盾碎片用金色主题）
            shield_theme = {'primary': (255, 200, 100), 'secondary': (180, 140, 80), 'glow': (255, 220, 150)}
            hit_effect = RockImpactEffect(mob.rect.centerx, mob.rect.centery, 'medium', shield_theme)
            all_sprites.add(hit_effect)
            
            # 【修复】给玩家充能大招
            self._charge_ult(self.damage)
            self.kill()
            break
    
    def _charge_ult(self, damage):
        """给玩家充能大招"""
        if not self.owner:
            return
        ult_charge_rate = getattr(self.owner, 'ult_charge_rate', 1.0)
        ult_charge_gain = (damage / 10) * ult_charge_rate
        if hasattr(self.owner, 'ult_charge'):
            self.owner.ult_charge = min(self.owner.max_ult_charge, self.owner.ult_charge + ult_charge_gain)
        if hasattr(self.owner, 'ult2_charge'):
            self.owner.ult2_charge = min(self.owner.max_ult2_charge, self.owner.ult2_charge + ult_charge_gain * 0.8)
        if hasattr(self.owner, 'ult3_charge'):
            self.owner.ult3_charge = min(self.owner.max_ult3_charge, self.owner.ult3_charge + ult_charge_gain * 0.6)
    
    def _draw(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.width // 2, self.height // 2
        
        rock_gray = (120, 115, 110)
        core_orange = (255, 120, 40)
        
        # 碎片
        points = []
        for i in range(5):
            angle = i * 72 * 0.01745 + self.angle_rad
            r = 8 + random.Random(i + 7).randint(-2, 3)
            points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
        pygame.draw.polygon(self.image, rock_gray, points)
        pygame.draw.polygon(self.image, core_orange, points, 2)
        
        # 火焰尾迹
        alpha = int(200 * (self.lifetime / 40))
        trail_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        trail_x = cx - math.cos(self.angle_rad) * 5
        trail_y = cy - math.sin(self.angle_rad) * 5
        pygame.draw.circle(trail_surf, (*core_orange, alpha), (int(trail_x), int(trail_y)), 4)
        self.image.blit(trail_surf, (0, 0))


# =============================================================================
#   护盾爆炸特效
# =============================================================================

class RockShieldExplosion(pygame.sprite.Sprite):
    """护盾爆炸 - 全屏岩石风暴特效"""
    
    def __init__(self, x, y, damage, owner):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.damage = damage
        self.owner = owner
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        self.frame = 0
        self.duration = 60
        
        # 粒子
        self.particles = []
        self.rock_chunks = []
        
        # 初始化爆炸
        self._create_explosion()
    
    def _create_explosion(self):
        """创建爆炸粒子"""
        for i in range(60):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(8, 25)
            self.particles.append({
                'x': self.center_x,
                'y': self.center_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': random.choice([
                    (255, 120, 40), (255, 180, 80), (200, 80, 30),
                    (120, 100, 80), (100, 80, 60)
                ]),
                'life': random.randint(30, 60),
                'max_life': 60,
                'size': random.randint(4, 12),
            })
        
        # 大块岩石
        for i in range(12):
            angle = i * 30 * 0.01745
            speed = random.uniform(10, 18)
            self.rock_chunks.append({
                'x': self.center_x,
                'y': self.center_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 8,
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-15, 15),
                'size': random.randint(15, 30),
                'life': 50,
            })
    
    def update(self):
        self.frame += 1
        self.image.fill((0, 0, 0, 0))
        
        t = pygame.time.get_ticks() / 1000.0
        progress = self.frame / self.duration
        
        # 全屏震动光效
        if self.frame < 20:
            shake_alpha = int(100 * (1 - self.frame / 20))
            pygame.draw.rect(self.image, (255, 180, 80, shake_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 冲击波环
        wave_r = int(progress * 400)
        wave_alpha = int(200 * (1 - progress))
        if wave_alpha > 0:
            pygame.draw.circle(self.image, (255, 140, 60, wave_alpha),
                             (self.center_x, self.center_y), wave_r, 6)
            pygame.draw.circle(self.image, (255, 200, 100, wave_alpha // 2),
                             (self.center_x, self.center_y), wave_r - 20, 4)
        
        # 更新岩石块
        for rock in self.rock_chunks[:]:
            rock['x'] += rock['vx']
            rock['y'] += rock['vy']
            rock['vy'] += 0.5  # 重力
            rock['rotation'] += rock['rot_speed']
            rock['life'] -= 1
            
            if rock['life'] <= 0:
                self.rock_chunks.remove(rock)
                continue
            
            # 绘制旋转的岩石
            rx, ry = int(rock['x']), int(rock['y'])
            rs = rock['size']
            alpha = int(255 * rock['life'] / 50)
            
            points = []
            for i in range(6):
                angle = math.radians(rock['rotation'] + i * 60)
                r = rs * (0.7 + 0.3 * ((i % 2) == 0))
                points.append((int(rx + math.cos(angle) * r), int(ry + math.sin(angle) * r)))
            
            if all(0 <= p[0] < WIDTH and 0 <= p[1] < HEIGHT for p in points):
                pygame.draw.polygon(self.image, (120, 100, 80, alpha), points)
                pygame.draw.polygon(self.image, (255, 140, 60, alpha // 2), points, 2)
        
        # 更新粒子
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.3
            p['vx'] *= 0.97
            p['life'] -= 1
            
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            
            alpha = int(255 * p['life'] / p['max_life'])
            size = int(p['size'] * p['life'] / p['max_life'])
            if size > 0 and 0 <= p['x'] < WIDTH and 0 <= p['y'] < HEIGHT:
                pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                                 (int(p['x']), int(p['y'])), size)
        
        # 地面裂纹
        self._draw_cracks(progress)
        
        if self.frame >= self.duration:
            self.kill()
    
    def _draw_cracks(self, progress):
        """绘制地面裂纹扩散"""
        crack_color = (100, 80, 60)
        lava_color = (255, 120, 40)
        
        crack_length = progress * 200
        
        for i in range(8):
            random.seed(i + 99)
            angle = i * 45 * 0.01745
            
            points = [(self.center_x, self.center_y)]
            px, py = self.center_x, self.center_y
            
            for seg in range(5):
                seg_len = crack_length / 5
                variation = random.uniform(-0.3, 0.3)
                px += math.cos(angle + variation) * seg_len
                py += math.sin(angle + variation) * seg_len
                points.append((int(px), int(py)))
            
            if len(points) >= 2:
                alpha = int(200 * (1 - progress * 0.5))
                pygame.draw.lines(self.image, (*crack_color, alpha), False, points, 3)
                pygame.draw.lines(self.image, (*lava_color, alpha // 2), False, points, 1)


# =============================================================================
#   C大招 - 图鲁跃砸（至尊品质震撼版）
# =============================================================================

class TuruLeapSlam(pygame.sprite.Sprite):
    """图鲁跃砸 - 至尊震撼版
    
    远程定位跳跃砸地，附带以下震撼效果：
    1. 跃起时岩石环绕+能量聚集
    2. 下坠时熔岩尾迹+燃烧残影
    3. 落地时全屏震动+巨型裂纹扩散+岩浆喷发
    4. 减速场地持续发光
    """
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        all_sprites.add(self)
        
        # 全屏画布
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        # 记录原始位置
        self.origin_x = owner.rect.centerx
        self.origin_y = owner.rect.centery
        
        # 目标位置（随机选择敌人或屏幕中央）
        self.target_x = WIDTH // 2
        self.target_y = HEIGHT // 3
        
        # 寻找最近敌人
        nearest_mob = None
        min_dist = float('inf')
        for mob in mobs:
            dist = math.hypot(mob.rect.centerx - owner.rect.centerx, 
                            mob.rect.centery - owner.rect.centery)
            if dist < min_dist:
                min_dist = dist
                nearest_mob = mob
        
        if nearest_mob:
            self.target_x = nearest_mob.rect.centerx
            self.target_y = nearest_mob.rect.centery
        
        # 阶段
        self.phase = "leap_up"  # leap_up -> descend -> slam -> return
        self.phase_timer = 0
        
        # 无敌时间
        self.invincible_frames = 48  # 0.8秒
        
        # 设置玩家无敌
        if hasattr(owner, 'invincible'):
            owner.invincible = True
            owner.invincible_timer = self.invincible_frames
        
        self.base_damage = owner.damage * 4
        
        # 粒子系统（限制数量防止卡顿）
        self.particles = []
        self.afterimages = []
        self.max_particles = 80  # 限制最大粒子数
        
        # 轨迹点
        self.trajectory = []
        
        # 预生成随机种子避免每帧创建Random对象
        self._rock_seeds = [random.Random(i + 99) for i in range(6)]
    
    def _add_particle(self, x, y, vx, vy, color, life, size=3, ptype='normal'):
        # 限制粒子数量防止卡顿
        if len(self.particles) >= self.max_particles:
            return
        self.particles.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color, 'life': life, 'max_life': life, 'size': size, 'type': ptype
        })
    
    def _update_particles(self):
        """更新并绘制粒子"""
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            
            if p['type'] == 'lava':
                p['vy'] += 0.3
            elif p['type'] == 'rock':
                p['vy'] += 0.5
            
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            
            alpha = int(255 * p['life'] / p['max_life'])
            size = int(p['size'] * (0.5 + 0.5 * p['life'] / p['max_life']))
            if size > 0 and 0 <= p['x'] < WIDTH and 0 <= p['y'] < HEIGHT:
                if p['type'] == 'lava':
                    for glow in range(2):
                        glow_r = size + glow * 2
                        glow_alpha = alpha // (glow + 2)
                        pygame.draw.circle(self.image, (*p['color'], glow_alpha),
                                         (int(p['x']), int(p['y'])), glow_r)
                pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                                 (int(p['x']), int(p['y'])), size)
    
    def update(self):
        self.phase_timer += 1
        self.image.fill((0, 0, 0, 0))
        
        t = pygame.time.get_ticks() / 1000.0
        ox, oy = self.owner.rect.centerx, self.owner.rect.centery
        
        if self.phase == "leap_up":
            # 上跃阶段 - 带岩石环绕特效
            if self.phase_timer < 20:
                self.owner.rect.centery -= 10
                
                # 岩石环绕
                for i in range(6):
                    angle = t * 8 + i * 1.05
                    r = 40 + math.sin(t * 4 + i) * 10
                    rx = ox + math.cos(angle) * r
                    ry = oy + math.sin(angle) * r
                    # 岩石块（使用预生成的随机种子）
                    rock_points = []
                    seed = self._rock_seeds[i]
                    for j in range(5):
                        ra = j * 72 * 0.01745 + t * 3
                        rr = 6 + ((i + j * 3) % 3) - 1  # 确定性计算避免每帧创建Random
                        rock_points.append((int(rx + math.cos(ra) * rr), int(ry + math.sin(ra) * rr)))
                    if all(0 <= p[0] < WIDTH and 0 <= p[1] < HEIGHT for p in rock_points):
                        pygame.draw.polygon(self.image, (120, 100, 80), rock_points)
                        pygame.draw.polygon(self.image, (255, 140, 60), rock_points, 2)
                
                # 能量聚集特效（减少粒子数量）
                if self.phase_timer % 3 == 0:  # 每3帧添加一个
                    offset_x = ((self.phase_timer * 17) % 120) - 60
                    offset_y = ((self.phase_timer * 23) % 120) - 60
                    self._add_particle(
                        ox + offset_x, oy + offset_y,
                        -offset_x * 0.08, -offset_y * 0.08,
                        (255, 180, 80), 15, 4, 'normal'
                    )
                
                # 上升尾迹（减少频率）
                if self.phase_timer % 2 == 0:
                    self._add_particle(ox, oy + 20, (self.phase_timer % 4) - 2, 3,
                                     (255, 120, 40), 20, 6, 'lava')
            else:
                self.phase = "descend"
                self.phase_timer = 0
                # 瞬移到目标上空
                self.owner.rect.centerx = self.target_x
                self.owner.rect.centery = self.target_y - 150
                
                # 瞬移闪光
                for i in range(20):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(5, 12)
                    self._add_particle(self.target_x, self.target_y - 150,
                                     math.cos(angle) * speed, math.sin(angle) * speed,
                                     (255, 200, 100), 25, 5, 'normal')
        
        elif self.phase == "descend":
            # 下落阶段 - 带熔岩尾迹
            fall_speed = 15 + self.phase_timer * 0.5  # 加速下落
            self.owner.rect.centery += fall_speed
            
            # 记录轨迹
            self.trajectory.append((ox, oy))
            if len(self.trajectory) > 15:
                self.trajectory.pop(0)
            
            # 绘制燃烧尾迹
            for i, (tx, ty) in enumerate(self.trajectory):
                alpha = int(200 * i / len(self.trajectory))
                size = int(20 * i / len(self.trajectory))
                if size > 0:
                    pygame.draw.circle(self.image, (255, 120, 40, alpha), (tx, ty), size)
                    pygame.draw.circle(self.image, (255, 200, 100, alpha // 2), (tx, ty), size // 2)
            
            # 熔岩粒子尾迹（减少粒子数量，使用确定性计算）
            if self.phase_timer % 2 == 0:  # 每2帧添加
                colors = [(255, 100, 30), (255, 160, 60), (200, 60, 20)]
                offset = (self.phase_timer * 7) % 30 - 15
                self._add_particle(ox + offset, oy,
                                 (self.phase_timer % 6) - 3, (self.phase_timer % 4) - 2,
                                 colors[self.phase_timer % 3],
                                 30, 4 + (self.phase_timer % 4), 'lava')
            
            # 预警圈
            warn_y = self.target_y
            warn_r = 80 + int(math.sin(t * 10) * 10)
            pygame.draw.circle(self.image, (255, 80, 40, 100), (self.target_x, warn_y), warn_r, 3)
            
            if self.owner.rect.centery >= self.target_y:
                self.owner.rect.centery = self.target_y
                self.phase = "slam"
                self.phase_timer = 0
                self._create_mega_tremor()
        
        elif self.phase == "slam":
            # 砸地停顿 - 持续震动效果
            shake = max(0, 10 - self.phase_timer // 2)
            if shake > 0:
                # 屏幕边缘闪光
                pygame.draw.rect(self.image, (255, 140, 60, int(shake * 15)), (0, 0, WIDTH, shake))
                pygame.draw.rect(self.image, (255, 140, 60, int(shake * 15)), (0, HEIGHT - shake, WIDTH, shake))
            
            # 持续的冲击波纹
            for i in range(3):
                wave_r = 30 + (self.phase_timer + i * 10) * 5
                wave_alpha = max(0, 150 - self.phase_timer * 5 - i * 30)
                if wave_alpha > 0:
                    pygame.draw.circle(self.image, (255, 120, 40, wave_alpha),
                                     (self.target_x, self.target_y), wave_r, 4)
            
            if self.phase_timer >= 30:
                self.phase = "return"
                self.phase_timer = 0
        
        elif self.phase == "return":
            # 返回原位 - 带能量拖尾
            dx = self.origin_x - self.owner.rect.centerx
            dy = self.origin_y - self.owner.rect.centery
            dist = math.hypot(dx, dy)
            
            # 返回拖尾
            self._add_particle(ox, oy, -dx * 0.02, -dy * 0.02,
                             (255, 180, 80), 15, 4, 'normal')
            
            if dist < 10:
                self.owner.rect.centerx = self.origin_x
                self.owner.rect.centery = self.origin_y
                self.kill()
            else:
                speed = min(25, dist * 0.35)
                self.owner.rect.centerx += dx / dist * speed
                self.owner.rect.centery += dy / dist * speed
        
        self._update_particles()
    
    def _create_mega_tremor(self):
        """创建巨型震荡波"""
        tremor = MegaTremorWave(self.target_x, self.target_y, self.base_damage, self.owner)
        all_sprites.add(tremor)
        bullets.add(tremor)


class MegaTremorWave(pygame.sprite.Sprite):
    """巨型震荡波 - 至尊震撼版"""
    
    def __init__(self, x, y, damage, owner):
        super().__init__()
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.center_x = x
        self.center_y = y
        self.damage = damage
        self.owner = owner
        
        self.max_radius = 280
        self.current_radius = 30
        self.affected_mobs = set()
        self.expansion_speed = 10
        self.lifetime = 90
        
        # 粒子
        self.particles = []
        
        # 裂纹
        self.cracks = []
        self._init_cracks()
        
        # 初始爆发
        self._create_initial_burst()
    
    def _init_cracks(self):
        """初始化地面裂纹"""
        for i in range(12):
            angle = i * 30 * 0.01745
            self.cracks.append({
                'angle': angle,
                'length': 0,
                'max_length': 150 + random.randint(0, 80),
                'segments': [],
                'lava_pulse': random.uniform(0, 2 * math.pi),
            })
    
    def _create_initial_burst(self):
        """创建初始爆发"""
        colors = [(255, 120, 40), (255, 180, 80), (200, 80, 30), (120, 100, 80), (100, 80, 60)]
        for i in range(35):  # 减少粒子数量
            angle = i * 0.18  # 确定性分布
            speed = 8 + (i % 8) * 1.5
            self.particles.append({
                'x': self.center_x, 'y': self.center_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 5,
                'color': colors[i % 5],
                'life': 45 + (i % 3) * 10,
                'max_life': 70,
                'size': 5 + (i % 5),
            })
        
        # 岩浆喷射（减少数量）
        for i in range(12):
            angle = -math.pi * 0.2 - i * 0.08
            speed = 12 + (i % 5) * 2
            self.particles.append({
                'x': self.center_x, 'y': self.center_y,
                'vx': math.cos(angle) * speed * 0.5,
                'vy': math.sin(angle) * speed,
                'color': (255, 160, 60),
                'life': 35 + (i % 3) * 8,
                'max_life': 50,
                'size': 6 + (i % 6),
            })
    
    def update(self):
        self.lifetime -= 1
        self.image.fill((0, 0, 0, 0))
        
        t = pygame.time.get_ticks() / 1000.0
        progress = 1 - (self.lifetime / 90)
        
        # 扩展冲击波
        if self.current_radius < self.max_radius:
            self.current_radius += self.expansion_speed
        
        # 绘制多层冲击波
        for i in range(4):
            wave_r = self.current_radius - i * 20
            if wave_r > 0:
                wave_alpha = int((200 - i * 45) * (1 - progress * 0.5))
                if wave_alpha > 0:
                    # 外圈
                    pygame.draw.circle(self.image, (255, 120, 40, wave_alpha),
                                     (self.center_x, self.center_y), int(wave_r), 5 - i)
                    # 内圈发光
                    if i == 0:
                        pygame.draw.circle(self.image, (255, 200, 100, wave_alpha // 2),
                                         (self.center_x, self.center_y), int(wave_r) - 5, 3)
        
        # 绘制和扩展裂纹
        for crack in self.cracks:
            if crack['length'] < crack['max_length']:
                crack['length'] += 8
            
            # 生成裂纹路径
            if len(crack['segments']) < int(crack['length'] / 15):
                if not crack['segments']:
                    crack['segments'].append((self.center_x, self.center_y))
                
                last = crack['segments'][-1]
                variation = random.uniform(-0.3, 0.3)
                new_x = last[0] + math.cos(crack['angle'] + variation) * 15
                new_y = last[1] + math.sin(crack['angle'] + variation) * 15
                crack['segments'].append((int(new_x), int(new_y)))
            
            # 绘制裂纹
            if len(crack['segments']) >= 2:
                # 裂纹主体
                pygame.draw.lines(self.image, (100, 80, 60), False, crack['segments'], 4)
                
                # 熔岩发光
                lava_pulse = abs(math.sin(t * 5 + crack['lava_pulse']))
                lava_alpha = int(150 * lava_pulse * (1 - progress * 0.3))
                if lava_alpha > 0:
                    pygame.draw.lines(self.image, (255, 120, 40, lava_alpha), False, crack['segments'], 2)
        
        # 中心冲击点
        core_r = 30 + int(math.sin(t * 8) * 5)
        core_alpha = int(200 * (1 - progress))
        pygame.draw.circle(self.image, (120, 100, 80, core_alpha), (self.center_x, self.center_y), core_r)
        pygame.draw.circle(self.image, (255, 140, 60, core_alpha), (self.center_x, self.center_y), core_r - 10)
        pygame.draw.circle(self.image, (255, 220, 150, core_alpha), (self.center_x, self.center_y), core_r // 3)
        
        # 更新粒子
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.4  # 重力
            p['vx'] *= 0.98
            p['life'] -= 1
            
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            
            alpha = int(255 * p['life'] / p['max_life'])
            size = int(p['size'] * p['life'] / p['max_life'])
            if size > 0 and 0 <= p['x'] < WIDTH and 0 <= p['y'] < HEIGHT:
                pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                                 (int(p['x']), int(p['y'])), size)
        
        # 检测范围内敌人
        for mob in mobs:
            if mob in self.affected_mobs:
                continue
            
            dist = math.hypot(mob.rect.centerx - self.center_x, 
                            mob.rect.centery - self.center_y)
            
            if dist <= self.current_radius:
                self.affected_mobs.add(mob)
                mob.take_damage(self.damage)
                
                # 【特效】生成大型粉碎特效
                smash_effect = RockSmashEffect(mob.rect.centerx, mob.rect.centery)
                all_sprites.add(smash_effect)
                
                # 充能
                self._charge_ult(self.damage)
                
                # 击飞效果
                if dist > 0:
                    push_dir_x = (mob.rect.centerx - self.center_x) / dist
                    push_dir_y = (mob.rect.centery - self.center_y) / dist
                    mob.rect.x += int(push_dir_x * 70)
                    mob.rect.y += int(push_dir_y * 70)
                
                # 减速效果
                if hasattr(mob, 'slow_timer'):
                    mob.slow_timer = 180  # 3秒减速
                if hasattr(mob, 'speed_mult'):
                    mob.speed_mult = 0.4
        
        if self.lifetime <= 0:
            self.kill()
    
    def _charge_ult(self, damage):
        """给玩家充能大招"""
        if not self.owner:
            return
        ult_charge_rate = getattr(self.owner, 'ult_charge_rate', 1.0)
        ult_charge_gain = (damage / 10) * ult_charge_rate
        if hasattr(self.owner, 'ult_charge'):
            self.owner.ult_charge = min(self.owner.max_ult_charge, self.owner.ult_charge + ult_charge_gain)
        if hasattr(self.owner, 'ult2_charge'):
            self.owner.ult2_charge = min(self.owner.max_ult2_charge, self.owner.ult2_charge + ult_charge_gain * 0.8)
        if hasattr(self.owner, 'ult3_charge'):
            self.owner.ult3_charge = min(self.owner.max_ult3_charge, self.owner.ult3_charge + ult_charge_gain * 0.6)
