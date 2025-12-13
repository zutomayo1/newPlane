# -*- coding: utf-8 -*-
"""
Cthulhu 战机子弹涂装效果渲染模块 - 月蚀星骸·克苏鲁专属

包含以下子弹效果：
- moon_laser: 月虹激光 - 贯穿全屏的月虹光束
- moon_eye: 月眼 - 追踪目标的月蚀巨眼
- eclipse_beam: 月蚀光束 - 二段真伤
- starbone_tentacle: 星骸触手 - 月能触手攻击
- eclipse_mark: 蚀印子弹 - 叠加蚀印的子弹
- lunar_spine: 月之脊 - 触手防御弹
- void_rift: 虚空裂隙 - 裂隙子弹
"""
import pygame
import math
import random
from config import all_sprites, mobs, enemy_bullets, bullets, WIDTH, HEIGHT


def render_cthulhu_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Cthulhu战机的子弹效果 - 月蚀星骸级别特效
    
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
    
    # 月蚀配色
    moon_blue = (100, 150, 220)
    star_purple = (160, 100, 200)
    void_black = (20, 15, 35)
    eye_white = (220, 230, 250)
    eclipse_glow = (180, 150, 255)
    
    if "moon_laser" in effects:
        # 月虹激光 - 贯穿光束
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 激光核心（竖向光束形态）
        beam_width = size // 3
        beam_height = size
        
        # 多层光晕
        for i in range(4):
            layer_width = beam_width + i * 4
            layer_alpha = 180 - i * 40
            pygame.draw.rect(bullet_surf, (*moon_blue, layer_alpha),
                           (cx - layer_width // 2, cy - beam_height // 2, layer_width, beam_height))
        
        # 光束脉冲波纹
        pulse = abs(math.sin(t * 8))
        for wave in range(3):
            wave_y = cy - beam_height // 2 + (wave * beam_height // 3) + int(pulse * 5)
            wave_alpha = 150 - wave * 40
            pygame.draw.ellipse(bullet_surf, (*eclipse_glow, wave_alpha),
                              (cx - beam_width, wave_y - 3, beam_width * 2, 6))
        
        # 月虹边缘
        pygame.draw.line(bullet_surf, star_purple, 
                        (cx - beam_width // 2, cy - beam_height // 2),
                        (cx - beam_width // 2, cy + beam_height // 2), 2)
        pygame.draw.line(bullet_surf, star_purple,
                        (cx + beam_width // 2, cy - beam_height // 2),
                        (cx + beam_width // 2, cy + beam_height // 2), 2)
        
        # 顶端月形装饰
        pygame.draw.arc(bullet_surf, eye_white,
                       (cx - beam_width, cy - beam_height // 2 - 4, beam_width * 2, 8),
                       0, math.pi, 2)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "moon_eye" in effects:
        # 月眼 - 追踪的月蚀巨眼
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 眼部光晕
        for i in range(3):
            glow_r = size // 2 + 3 - i * 3
            glow_alpha = 80 - i * 20
            pygame.draw.circle(bullet_surf, (*star_purple, glow_alpha), (cx, cy), glow_r)
        
        # 眼白（巩膜）- 椭圆
        eye_width = size // 2 + 4
        eye_height = size // 3 + 2
        pygame.draw.ellipse(bullet_surf, eye_white,
                          (cx - eye_width, cy - eye_height, eye_width * 2, eye_height * 2))
        
        # 虹膜
        iris_r = size // 4 + 2
        iris_wobble = math.sin(t * 3) * 2
        pygame.draw.circle(bullet_surf, moon_blue, (int(cx + iris_wobble), cy), iris_r)
        
        # 瞳孔（竖瞳）
        pupil_h = size // 3
        pupil_w = size // 8 + abs(math.sin(t * 4)) * 3
        pygame.draw.ellipse(bullet_surf, void_black,
                          (cx - pupil_w // 2, cy - pupil_h // 2, pupil_w, pupil_h))
        
        # 眼部高光
        pygame.draw.circle(bullet_surf, (255, 255, 255), (int(cx - 3), int(cy - 3)), 2)
        
        # 眼部边缘
        pygame.draw.ellipse(bullet_surf, star_purple,
                          (cx - eye_width, cy - eye_height, eye_width * 2, eye_height * 2), 2)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "eclipse_beam" in effects:
        # 月蚀光束 - 真伤光柱
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 光柱核心
        pillar_width = size // 4
        pillar_height = size + 4
        
        # 外层光晕（紫色）
        for i in range(3):
            layer_w = pillar_width + i * 6
            layer_alpha = 120 - i * 35
            pygame.draw.rect(bullet_surf, (*star_purple, layer_alpha),
                           (cx - layer_w // 2, cy - pillar_height // 2, layer_w, pillar_height))
        
        # 核心（月蓝）
        pygame.draw.rect(bullet_surf, moon_blue,
                        (cx - pillar_width // 2, cy - pillar_height // 2, pillar_width, pillar_height))
        
        # 真伤标记（蚀印符号）
        mark_y = cy + int(math.sin(t * 6) * 5)
        pygame.draw.circle(bullet_surf, eclipse_glow, (cx, mark_y), 4)
        pygame.draw.circle(bullet_surf, void_black, (cx, mark_y), 2)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "starbone_tentacle" in effects:
        # 星骸触手
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 触手蜿蜒
        segments = 8
        points = []
        for i in range(segments + 1):
            prog = i / segments
            wave = math.sin(t * 4 + prog * 3) * (5 + prog * 8)
            dist = size // 2 * prog
            
            px = cx + wave
            py = cy - size // 2 + dist * 2
            points.append((int(px), int(py)))
        
        # 触手主体
        if len(points) >= 2:
            pygame.draw.lines(bullet_surf, star_purple, False, points, 4)
            # 触手高光
            pygame.draw.lines(bullet_surf, eclipse_glow, False, points, 2)
        
        # 触手末端
        if points:
            end = points[-1]
            pygame.draw.circle(bullet_surf, moon_blue, end, 4)
            pygame.draw.circle(bullet_surf, void_black, end, 2)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "eclipse_mark" in effects:
        # 蚀印子弹 - 叠加标记
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 蚀印光环
        for i in range(3):
            ring_r = size // 3 + i * 4
            ring_alpha = 150 - i * 40
            pygame.draw.circle(bullet_surf, (*star_purple, ring_alpha), (cx, cy), ring_r, 2)
        
        # 中心月蚀符号
        pygame.draw.circle(bullet_surf, void_black, (cx, cy), size // 4)
        # 月牙遮罩
        eclipse_offset = 3 + int(math.sin(t * 2) * 2)
        pygame.draw.circle(bullet_surf, moon_blue, (cx - eclipse_offset, cy), size // 5)
        
        # 蚀印光点
        for i in range(5):
            dot_angle = (i * 72 + t * 60) * math.pi / 180
            dot_r = size // 3
            dx = cx + int(math.cos(dot_angle) * dot_r)
            dy = cy + int(math.sin(dot_angle) * dot_r)
            pygame.draw.circle(bullet_surf, eclipse_glow, (dx, dy), 2)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "lunar_spine" in effects:
        # 月之脊 - 防御触手弹
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 脊椎骨节
        spine_count = 5
        for i in range(spine_count):
            seg_y = cy - size // 2 + i * (size // spine_count)
            seg_width = size // 3 - abs(i - spine_count // 2) * 2
            
            # 骨节
            pygame.draw.ellipse(bullet_surf, moon_blue,
                              (cx - seg_width // 2, seg_y, seg_width, size // spine_count))
            pygame.draw.ellipse(bullet_surf, star_purple,
                              (cx - seg_width // 2, seg_y, seg_width, size // spine_count), 1)
        
        # 能量核心
        core_pulse = abs(math.sin(t * 4))
        core_r = 3 + int(core_pulse * 2)
        pygame.draw.circle(bullet_surf, eclipse_glow, (cx, cy), core_r)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "void_rift" in effects:
        # 虚空裂隙
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 裂隙线条
        rift_width = 2 + int(abs(math.sin(t * 5)) * 3)
        for i in range(5):
            offset = (i - 2) * 3
            line_alpha = 200 - abs(i - 2) * 50
            pygame.draw.line(bullet_surf, (*star_purple, line_alpha),
                           (cx + offset, cy - size // 2),
                           (cx - offset, cy + size // 2), rift_width - abs(i - 2))
        
        # 裂隙边缘光晕
        for side in [-1, 1]:
            for glow in range(3):
                glow_x = cx + side * (4 + glow * 2)
                pygame.draw.line(bullet_surf, (*eclipse_glow, 80 - glow * 25),
                               (glow_x, cy - size // 2),
                               (glow_x, cy + size // 2), 1)
        
        # 虚空粒子
        random.seed(int(t * 5))
        for _ in range(4):
            px = cx + random.randint(-size // 3, size // 3)
            py = cy + random.randint(-size // 2, size // 2)
            pygame.draw.circle(bullet_surf, void_black, (px, py), 2)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "moonlight_orb" in effects:
        # 月光弹 - 小型追踪月光球
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 月光光晕
        for i in range(4):
            glow_r = size // 3 + i * 3
            glow_alpha = 120 - i * 25
            pygame.draw.circle(bullet_surf, (*moon_blue, glow_alpha), (cx, cy), glow_r)
        
        # 月光核心
        core_r = size // 4
        pygame.draw.circle(bullet_surf, eye_white, (cx, cy), core_r)
        pygame.draw.circle(bullet_surf, moon_blue, (cx, cy), core_r - 2)
        
        # 月相装饰
        phase = int(t * 2) % 4
        if phase == 1:
            pygame.draw.circle(bullet_surf, void_black, (cx - 2, cy), core_r - 3)
        elif phase == 3:
            pygame.draw.circle(bullet_surf, void_black, (cx + 2, cy), core_r - 3)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "eldritch_horror" in effects:
        # 不可名状之物 - 扭曲变形的弹丸
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 蠕动肉块外形
        points = []
        for i in range(12):
            angle = i * 30 * 0.01745
            r = size // 3 * (1 + math.sin(t * 4 + i * 0.7) * 0.4 + math.cos(t * 3 + i) * 0.2)
            points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
        pygame.draw.polygon(bullet_surf, (60, 50, 70), points)
        pygame.draw.polygon(bullet_surf, star_purple, points, 2)
        
        # 随机眼睛
        random.seed(int(t * 3))
        for _ in range(random.randint(2, 4)):
            ex = cx + random.randint(-size//4, size//4)
            ey = cy + random.randint(-size//4, size//4)
            pygame.draw.circle(bullet_surf, eye_white, (ex, ey), 3)
            pygame.draw.circle(bullet_surf, void_black, (ex, ey), 1)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "blood_tentacle" in effects:
        # 血腥触手 - 带吸盘的触手弹
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        blood_red = (150, 30, 40)
        
        # 触手蜿蜒
        points = []
        for i in range(10):
            prog = i / 9
            wave = math.sin(t * 5 + prog * 4) * (4 + prog * 10)
            px = cx + wave
            py = cy - size // 2 + prog * size
            points.append((int(px), int(py)))
        
        if len(points) >= 2:
            pygame.draw.lines(bullet_surf, blood_red, False, points, 5)
            pygame.draw.lines(bullet_surf, (200, 80, 80), False, points, 2)
        
        # 吸盘
        for i in range(1, len(points) - 1, 2):
            pygame.draw.circle(bullet_surf, (100, 20, 30), points[i], 3)
            pygame.draw.circle(bullet_surf, (60, 10, 15), points[i], 2)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "madness_orb" in effects:
        # 疯狂之球 - 让人失去理智的光球
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 不稳定光晕
        for i in range(5):
            glow_r = size // 3 + i * 4 + int(math.sin(t * 8 + i) * 3)
            # 颜色闪烁
            h = (t * 2 + i * 0.3) % 1
            col = (int(150 + 100 * h), int(50 + 50 * (1-h)), int(150 + 100 * (1-h)))
            pygame.draw.circle(bullet_surf, (*col, 100 - i * 18), (cx, cy), glow_r)
        
        # 核心漩涡
        for i in range(8):
            spiral_angle = t * 6 + i * 0.78
            spiral_r = (size // 4) * (1 - i / 8)
            sx = cx + int(math.cos(spiral_angle) * spiral_r)
            sy = cy + int(math.sin(spiral_angle) * spiral_r)
            pygame.draw.circle(bullet_surf, eclipse_glow, (sx, sy), 2)
        
        # 中心眼
        pygame.draw.circle(bullet_surf, eye_white, (cx, cy), 4)
        pygame.draw.circle(bullet_surf, void_black, (cx, cy), 2)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "abyssal_maw" in effects:
        # 深渊巨口 - 张开的恐怖大嘴
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        abyss = (15, 20, 25)
        
        # 嘴部轮廓
        mouth_open = abs(math.sin(t * 4)) * (size // 3) + size // 4
        pygame.draw.ellipse(bullet_surf, abyss, 
                           (cx - size // 3, cy - int(mouth_open) // 2, size * 2 // 3, int(mouth_open)))
        
        # 尖牙
        teeth_count = 6
        for i in range(teeth_count):
            tx = cx - size // 3 + 4 + i * (size * 2 // 3 - 8) // (teeth_count - 1)
            # 上牙
            pygame.draw.polygon(bullet_surf, (200, 190, 180),
                              [(tx, cy - int(mouth_open) // 2 + 2),
                               (tx - 2, cy - int(mouth_open) // 2 + 8),
                               (tx + 2, cy - int(mouth_open) // 2 + 8)])
            # 下牙
            pygame.draw.polygon(bullet_surf, (200, 190, 180),
                              [(tx, cy + int(mouth_open) // 2 - 2),
                               (tx - 2, cy + int(mouth_open) // 2 - 8),
                               (tx + 2, cy + int(mouth_open) // 2 - 8)])
        
        # 嘴唇
        pygame.draw.ellipse(bullet_surf, (80, 50, 60),
                           (cx - size // 3, cy - int(mouth_open) // 2, size * 2 // 3, int(mouth_open)), 2)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "nightmare_shard" in effects:
        # 梦魇碎片 - 锐利的恐惧结晶
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        nightmare = (40, 20, 50)
        
        # 不规则碎片
        shard_points = [
            (cx, cy - size // 2),
            (cx + size // 3, cy - size // 4),
            (cx + size // 4, cy + size // 3),
            (cx - size // 5, cy + size // 2 - 3),
            (cx - size // 3, cy),
        ]
        # 添加抖动
        shard_points = [(px + int(math.sin(t * 6 + i) * 2), py + int(math.cos(t * 5 + i) * 2)) 
                        for i, (px, py) in enumerate(shard_points)]
        pygame.draw.polygon(bullet_surf, nightmare, shard_points)
        pygame.draw.polygon(bullet_surf, (180, 100, 200), shard_points, 2)
        
        # 内部纹路
        pygame.draw.line(bullet_surf, (100, 60, 120), shard_points[0], shard_points[3], 1)
        pygame.draw.line(bullet_surf, (100, 60, 120), shard_points[1], shard_points[4], 1)
        
        # 核心光点
        pygame.draw.circle(bullet_surf, eclipse_glow, (cx, cy), 3)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "cosmic_worm" in effects:
        # 宇宙蠕虫弹 - 小型蠕动虫体
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        worm_flesh = (160, 120, 140)
        
        # 虫体节段
        segments = 5
        for i in range(segments):
            prog = i / (segments - 1)
            seg_x = cx + math.sin(t * 4 + prog * 3) * 5
            seg_y = cy - size // 2 + prog * size
            seg_r = size // 5 - abs(i - segments // 2)
            
            pygame.draw.circle(bullet_surf, worm_flesh, (int(seg_x), int(seg_y)), seg_r)
            pygame.draw.circle(bullet_surf, (120, 80, 100), (int(seg_x), int(seg_y)), seg_r, 1)
        
        # 头部嘴
        head_y = cy - size // 2
        mouth = abs(math.sin(t * 5)) * 3 + 2
        pygame.draw.ellipse(bullet_surf, void_black, (cx - 3, int(head_y - mouth), 6, int(mouth * 2)))
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "ritual_sigil" in effects:
        # 祭祀符印 - 旋转的邪教符文
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        sigil_gold = (180, 140, 80)
        
        # 外圈
        pygame.draw.circle(bullet_surf, sigil_gold, (cx, cy), size // 3, 2)
        pygame.draw.circle(bullet_surf, sigil_gold, (cx, cy), size // 3 - 4, 1)
        
        # 旋转符文
        for i in range(6):
            angle = t * 2 + i * (math.pi / 3)
            # 外点
            ox = cx + int(math.cos(angle) * (size // 3))
            oy = cy + int(math.sin(angle) * (size // 3))
            pygame.draw.circle(bullet_surf, sigil_gold, (ox, oy), 2)
            # 连线到中心
            pygame.draw.line(bullet_surf, sigil_gold, (cx, cy), (ox, oy), 1)
        
        # 内五角星
        star_r = size // 5
        star_points = []
        for i in range(5):
            angle = t * 1.5 + i * (2 * math.pi / 5) - math.pi / 2
            star_points.append((int(cx + math.cos(angle) * star_r), int(cy + math.sin(angle) * star_r)))
        # 画五角星
        for i in range(5):
            pygame.draw.line(bullet_surf, (200, 50, 50), star_points[i], star_points[(i + 2) % 5], 1)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "deep_one_spawn" in effects:
        # 深潜者卵 - 鱼人后代
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        spawn_green = (40, 80, 60)
        
        # 卵形外壳
        pygame.draw.ellipse(bullet_surf, spawn_green, 
                           (cx - size // 4, cy - size // 3, size // 2, size * 2 // 3))
        pygame.draw.ellipse(bullet_surf, (60, 120, 80),
                           (cx - size // 4, cy - size // 3, size // 2, size * 2 // 3), 2)
        
        # 内部胚胎轮廓
        embryo_y = cy + int(math.sin(t * 2) * 2)
        pygame.draw.ellipse(bullet_surf, (30, 50, 40),
                           (cx - size // 6, embryo_y - size // 5, size // 3, size * 2 // 5))
        
        # 眼睛
        pygame.draw.circle(bullet_surf, (200, 180, 100), (cx - 2, embryo_y - 3), 2)
        pygame.draw.circle(bullet_surf, (200, 180, 100), (cx + 2, embryo_y - 3), 2)
        pygame.draw.circle(bullet_surf, void_black, (cx - 2, embryo_y - 3), 1)
        pygame.draw.circle(bullet_surf, void_black, (cx + 2, embryo_y - 3), 1)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "shoggoth_blob" in effects:
        # 修格斯泡 - 不定形粘液
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        shoggoth = (20, 25, 30)
        
        # 不定形外壳
        points = []
        for i in range(16):
            angle = i * (2 * math.pi / 16)
            r = size // 3 * (1 + math.sin(t * 5 + i * 0.9) * 0.35 + math.cos(t * 4 + i * 1.3) * 0.25)
            points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
        pygame.draw.polygon(bullet_surf, shoggoth, points)
        
        # 表面反光
        pygame.draw.polygon(bullet_surf, (40, 50, 60), points, 1)
        
        # 无数眼睛
        random.seed(int(t * 2))
        for _ in range(random.randint(3, 6)):
            ex = cx + random.randint(-size//4, size//4)
            ey = cy + random.randint(-size//4, size//4)
            pygame.draw.circle(bullet_surf, (150, 200, 180), (ex, ey), 2)
            pygame.draw.circle(bullet_surf, void_black, (ex, ey), 1)
        
        # 伪足
        for i in range(3):
            angle = t * 2 + i * 2.1
            length = size // 4 + int(math.sin(t * 3 + i) * 5)
            ex = cx + int(math.cos(angle) * (size // 3 + length))
            ey = cy + int(math.sin(angle) * (size // 3 + length))
            pygame.draw.line(bullet_surf, shoggoth, (cx + int(math.cos(angle) * size // 4), 
                                                     cy + int(math.sin(angle) * size // 4)), (ex, ey), 3)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "yog_bubble" in effects:
        # 犹格之泡 - 时空扭曲的气泡
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 多层扭曲圆
        for i in range(4):
            r = size // 3 - i * 3
            offset_x = math.sin(t * 3 + i * 1.5) * 3
            offset_y = math.cos(t * 2.5 + i * 1.2) * 3
            alpha = 150 - i * 30
            pygame.draw.circle(bullet_surf, (*star_purple, alpha), 
                             (int(cx + offset_x), int(cy + offset_y)), r, 2)
        
        # 内部星空
        random.seed(42)
        for _ in range(8):
            sx = cx + random.randint(-size//4, size//4)
            sy = cy + random.randint(-size//4, size//4)
            twinkle = abs(math.sin(t * 4 + sx + sy))
            if twinkle > 0.5:
                pygame.draw.circle(bullet_surf, (255, 255, 200), (sx, sy), 1)
        
        # 核心
        pygame.draw.circle(bullet_surf, eclipse_glow, (cx, cy), 3)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    return False


# 子弹主题配置
CTHULHU_BULLET_THEMES = {
    "moon_laser": {
        "name": "月虹激光",
        "desc": "贯穿全屏的月虹光束",
        "effects": ["moon_laser"],
        "color": (100, 150, 220),
        "trail_color": (160, 100, 200),
    },
    "moon_eye": {
        "name": "月眼",
        "desc": "追踪目标的月蚀巨眼",
        "effects": ["moon_eye"],
        "color": (220, 230, 250),
        "trail_color": (100, 150, 220),
    },
    "eclipse_beam": {
        "name": "月蚀光束",
        "desc": "造成二段真伤的光柱",
        "effects": ["eclipse_beam"],
        "color": (160, 100, 200),
        "trail_color": (180, 150, 255),
    },
    "starbone_tentacle": {
        "name": "星骸触手",
        "desc": "蜿蜒追踪的月能触手",
        "effects": ["starbone_tentacle"],
        "color": (160, 100, 200),
        "trail_color": (100, 150, 220),
    },
    "eclipse_mark": {
        "name": "蚀印弹",
        "desc": "叠加蚀印的标记子弹",
        "effects": ["eclipse_mark"],
        "color": (180, 150, 255),
        "trail_color": (160, 100, 200),
    },
    "lunar_spine": {
        "name": "月之脊",
        "desc": "可抵挡弹幕的脊骨触手",
        "effects": ["lunar_spine"],
        "color": (100, 150, 220),
        "trail_color": (160, 100, 200),
    },
    "void_rift": {
        "name": "虚空裂隙",
        "desc": "撕裂空间的裂隙弹",
        "effects": ["void_rift"],
        "color": (20, 15, 35),
        "trail_color": (160, 100, 200),
    },
    "eldritch_horror": {
        "name": "不可名状",
        "desc": "扭曲变形、长满眼睛的肉块",
        "effects": ["eldritch_horror"],
        "color": (60, 50, 70),
        "trail_color": (160, 100, 200),
    },
    "blood_tentacle": {
        "name": "血腥触手",
        "desc": "带吸盘的蠕动血肉触手",
        "effects": ["blood_tentacle"],
        "color": (150, 30, 40),
        "trail_color": (200, 80, 80),
    },
    "madness_orb": {
        "name": "疯狂之球",
        "desc": "令人失去理智的诡异光球",
        "effects": ["madness_orb"],
        "color": (180, 100, 200),
        "trail_color": (150, 80, 180),
    },
    "abyssal_maw": {
        "name": "深渊巨口",
        "desc": "张开利齿的恐怖大嘴",
        "effects": ["abyssal_maw"],
        "color": (15, 20, 25),
        "trail_color": (80, 50, 60),
    },
    "nightmare_shard": {
        "name": "梦魇碎片",
        "desc": "锐利的恐惧结晶体",
        "effects": ["nightmare_shard"],
        "color": (40, 20, 50),
        "trail_color": (180, 100, 200),
    },
    "cosmic_worm": {
        "name": "宇宙蠕虫",
        "desc": "蠕动的星际寄生虫",
        "effects": ["cosmic_worm"],
        "color": (160, 120, 140),
        "trail_color": (120, 80, 100),
    },
    "ritual_sigil": {
        "name": "祭祀符印",
        "desc": "旋转的邪教符文阵",
        "effects": ["ritual_sigil"],
        "color": (180, 140, 80),
        "trail_color": (200, 50, 50),
    },
    "deep_one_spawn": {
        "name": "深潜者卵",
        "desc": "鱼人后代的恐怖卵囊",
        "effects": ["deep_one_spawn"],
        "color": (40, 80, 60),
        "trail_color": (60, 120, 80),
    },
    "shoggoth_blob": {
        "name": "修格斯泡",
        "desc": "不定形的黑色粘液生物",
        "effects": ["shoggoth_blob"],
        "color": (20, 25, 30),
        "trail_color": (40, 50, 60),
    },
    "yog_bubble": {
        "name": "犹格之泡",
        "desc": "扭曲时空的异次元气泡",
        "effects": ["yog_bubble"],
        "color": (160, 100, 200),
        "trail_color": (180, 150, 255),
    },
}


# =========================================================================
#   Cthulhu 子弹类定义
# =========================================================================
from config import all_sprites, mobs, enemy_bullets, WIDTH, HEIGHT


class MoonLaser(pygame.sprite.Sprite):
    """月虹激光 - 贯穿全屏的月虹光束"""
    
    def __init__(self, x, y, damage, owner=None, bullet_theme=None):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.piercing = 999  # 无限穿透
        self.bullet_theme = bullet_theme
        
        # 月蚀配色 - 如果有涂装则使用涂装颜色
        if bullet_theme and bullet_theme.get('color'):
            self.moon_blue = bullet_theme.get('color') or (100, 150, 220)
            self.star_purple = bullet_theme.get('trail_color') or (160, 100, 200)
        else:
            self.moon_blue = (100, 150, 220)
            self.star_purple = (160, 100, 200)
        self.glow_white = (220, 230, 250)
        
        # 位置
        self.float_x = float(x)
        self.float_y = float(y)
        self.width = 24  # 加宽以容纳不同形状
        self.height = 48
        self.speed = 25  # 激光速度
        
        # 获取涂装效果
        self.effects = []
        if bullet_theme:
            self.effects = bullet_theme.get('effects', [])
        
        # 图像
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(midbottom=(x, y))
        
        self.frame = 0
        self.hit_enemies = set()  # 已命中的敌人
        
        self._draw()
    
    def _draw(self):
        """根据涂装效果绘制不同形状的子弹"""
        self.image.fill((0, 0, 0, 0))
        w, h = self.width, self.height
        cx, cy = w // 2, h // 2
        t = self.frame * 0.1
        
        # 根据涂装效果绘制不同形状
        if "blood_tentacle" in self.effects:
            # 血肉触手 - 蠕动的触手
            points = []
            for i in range(8):
                prog = i / 7
                wave = math.sin(t * 5 + prog * 4) * (3 + prog * 6)
                px = cx + wave
                py = h - prog * h
                points.append((int(px), int(py)))
            if len(points) >= 2:
                pygame.draw.lines(self.image, self.moon_blue, False, points, 5)
                pygame.draw.lines(self.image, self.star_purple, False, points, 2)
            # 吸盘
            for i in range(1, len(points) - 1, 2):
                pygame.draw.circle(self.image, self.star_purple, points[i], 3)
        
        elif "madness_orb" in self.effects:
            # 疯狂之球 - 闪烁的光球
            pulse = abs(math.sin(t * 4))
            r = int(8 + pulse * 4)
            for i in range(3):
                glow_r = r + i * 3
                alpha = 180 - i * 50
                pygame.draw.circle(self.image, (*self.moon_blue, alpha), (cx, cy), glow_r)
            pygame.draw.circle(self.image, self.glow_white, (cx, cy), 4)
            # 漩涡线
            for i in range(6):
                angle = t * 3 + i * 1.05
                sx = cx + int(math.cos(angle) * r * 0.7)
                sy = cy + int(math.sin(angle) * r * 0.7)
                pygame.draw.circle(self.image, self.star_purple, (sx, sy), 2)
        
        elif "eldritch_horror" in self.effects:
            # 不可名状 - 扭曲变形的肉块
            points = []
            for i in range(10):
                angle = i * 36 * 0.01745
                r = 10 * (1 + math.sin(t * 4 + i * 0.7) * 0.4)
                points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
            pygame.draw.polygon(self.image, self.moon_blue, points)
            pygame.draw.polygon(self.image, self.star_purple, points, 2)
            # 随机眼睛
            random.seed(int(t * 2))
            for _ in range(2):
                ex = cx + random.randint(-5, 5)
                ey = cy + random.randint(-5, 5)
                pygame.draw.circle(self.image, self.glow_white, (ex, ey), 3)
                pygame.draw.circle(self.image, (20, 20, 30), (ex, ey), 1)
        
        elif "abyssal_maw" in self.effects:
            # 深渊巨口 - 张开的嘴
            mouth_open = abs(math.sin(t * 3)) * 8 + 6
            pygame.draw.ellipse(self.image, (20, 15, 25),
                              (cx - 10, cy - int(mouth_open) // 2, 20, int(mouth_open)))
            # 尖牙
            for i in range(4):
                tx = cx - 8 + i * 5
                pygame.draw.polygon(self.image, self.glow_white,
                                  [(tx, cy - int(mouth_open) // 2 + 2),
                                   (tx - 2, cy - int(mouth_open) // 2 + 6),
                                   (tx + 2, cy - int(mouth_open) // 2 + 6)])
            pygame.draw.ellipse(self.image, self.star_purple,
                              (cx - 10, cy - int(mouth_open) // 2, 20, int(mouth_open)), 2)
        
        elif "nightmare_shard" in self.effects:
            # 噩梦碎片 - 锐利的结晶
            shard_points = [
                (cx, cy - 18),
                (cx + 8, cy - 5),
                (cx + 5, cy + 15),
                (cx - 5, cy + 12),
                (cx - 8, cy - 2),
            ]
            # 添加抖动
            shard_points = [(px + int(math.sin(t * 5 + i) * 2), py + int(math.cos(t * 4 + i) * 2))
                           for i, (px, py) in enumerate(shard_points)]
            pygame.draw.polygon(self.image, self.moon_blue, shard_points)
            pygame.draw.polygon(self.image, self.star_purple, shard_points, 2)
            pygame.draw.circle(self.image, self.glow_white, (cx, cy), 3)
        
        elif "cosmic_worm" in self.effects:
            # 宇宙蠕虫 - 蠕动虫体
            segments = 5
            for i in range(segments):
                prog = i / (segments - 1)
                seg_x = cx + math.sin(t * 4 + prog * 3) * 4
                seg_y = h - 8 - prog * (h - 16)
                seg_r = 6 - abs(i - segments // 2)
                pygame.draw.circle(self.image, self.moon_blue, (int(seg_x), int(seg_y)), seg_r)
                pygame.draw.circle(self.image, self.star_purple, (int(seg_x), int(seg_y)), seg_r, 1)
            # 头部嘴
            pygame.draw.ellipse(self.image, (20, 20, 30), (cx - 3, 2, 6, 4))
        
        elif "ritual_sigil" in self.effects:
            # 仪式符文 - 旋转的符文阵
            pygame.draw.circle(self.image, self.moon_blue, (cx, cy), 10, 2)
            pygame.draw.circle(self.image, self.moon_blue, (cx, cy), 6, 1)
            for i in range(6):
                angle = t * 2 + i * (math.pi / 3)
                ox = cx + int(math.cos(angle) * 10)
                oy = cy + int(math.sin(angle) * 10)
                pygame.draw.circle(self.image, self.star_purple, (ox, oy), 2)
                pygame.draw.line(self.image, self.star_purple, (cx, cy), (ox, oy), 1)
            # 内五角星
            for i in range(5):
                angle = t * 1.5 + i * (2 * math.pi / 5) - math.pi / 2
                p1 = (int(cx + math.cos(angle) * 5), int(cy + math.sin(angle) * 5))
                angle2 = t * 1.5 + ((i + 2) % 5) * (2 * math.pi / 5) - math.pi / 2
                p2 = (int(cx + math.cos(angle2) * 5), int(cy + math.sin(angle2) * 5))
                pygame.draw.line(self.image, (200, 50, 50), p1, p2, 1)
        
        elif "deep_one_spawn" in self.effects:
            # 深潜者卵 - 鱼人卵
            pygame.draw.ellipse(self.image, self.moon_blue,
                              (cx - 8, cy - 12, 16, 24))
            pygame.draw.ellipse(self.image, self.star_purple,
                              (cx - 8, cy - 12, 16, 24), 2)
            # 内部胚胎
            ey = cy + int(math.sin(t * 2) * 2)
            pygame.draw.ellipse(self.image, (30, 50, 40),
                              (cx - 4, ey - 4, 8, 10))
            pygame.draw.circle(self.image, self.glow_white, (cx - 2, ey - 2), 2)
            pygame.draw.circle(self.image, self.glow_white, (cx + 2, ey - 2), 2)
        
        elif "shoggoth_blob" in self.effects:
            # 修格斯泡 - 不定形粘液
            points = []
            for i in range(12):
                angle = i * (2 * math.pi / 12)
                r = 10 * (1 + math.sin(t * 5 + i * 0.9) * 0.3)
                points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
            pygame.draw.polygon(self.image, self.moon_blue, points)
            pygame.draw.polygon(self.image, self.star_purple, points, 1)
            # 眼睛
            random.seed(int(t * 2))
            for _ in range(3):
                ex = cx + random.randint(-6, 6)
                ey = cy + random.randint(-6, 6)
                pygame.draw.circle(self.image, (150, 200, 180), (ex, ey), 2)
                pygame.draw.circle(self.image, (20, 20, 30), (ex, ey), 1)
        
        elif "yog_bubble" in self.effects:
            # 犹格之泡 - 时空气泡
            for i in range(3):
                r = 10 - i * 2
                offset_x = math.sin(t * 3 + i * 1.5) * 2
                offset_y = math.cos(t * 2.5 + i * 1.2) * 2
                pygame.draw.circle(self.image, (*self.star_purple, 150 - i * 40),
                                 (int(cx + offset_x), int(cy + offset_y)), r, 2)
            # 内部星空
            random.seed(42)
            for _ in range(5):
                sx = cx + random.randint(-6, 6)
                sy = cy + random.randint(-6, 6)
                if abs(math.sin(t * 4 + sx + sy)) > 0.5:
                    pygame.draw.circle(self.image, (255, 255, 200), (sx, sy), 1)
            pygame.draw.circle(self.image, self.glow_white, (cx, cy), 3)
        
        elif "moon_eye" in self.effects:
            # 月眼形态
            eye_r = 10
            pygame.draw.ellipse(self.image, self.glow_white,
                              (cx - eye_r, cy - eye_r * 0.6, eye_r * 2, eye_r * 1.2))
            iris_wobble = math.sin(t * 3) * 2
            pygame.draw.circle(self.image, self.moon_blue, (int(cx + iris_wobble), cy), 5)
            pygame.draw.ellipse(self.image, (20, 15, 35),
                              (cx - 1, cy - 4, 3, 8))
            pygame.draw.circle(self.image, (255, 255, 255), (cx - 2, cy - 2), 1)
            pygame.draw.ellipse(self.image, self.star_purple,
                              (cx - eye_r, cy - eye_r * 0.6, eye_r * 2, eye_r * 1.2), 2)
        
        else:
            # 默认：月虹激光（长条光束）
            beam_w = 10
            # 多层光晕
            for i in range(4):
                layer_w = beam_w - i * 2
                layer_alpha = 200 - i * 40
                pygame.draw.rect(self.image, (*self.moon_blue, layer_alpha),
                               (cx - layer_w // 2, 0, layer_w, h))
            # 核心光束
            pygame.draw.rect(self.image, self.glow_white,
                            (cx - 2, 0, 4, h))
            # 边缘紫光
            pygame.draw.line(self.image, self.star_purple, (cx - beam_w // 2, 0), (cx - beam_w // 2, h), 2)
            pygame.draw.line(self.image, self.star_purple, (cx + beam_w // 2, 0), (cx + beam_w // 2, h), 2)
            # 脉动效果
            if abs(math.sin(t * 5)) > 0.7:
                pygame.draw.rect(self.image, (*self.glow_white, 100), (cx - beam_w // 2, 0, beam_w, h))
    
    def update(self):
        """更新月虹激光"""
        self.frame += 1
        self.float_y -= self.speed
        self.rect.centery = int(self.float_y)
        
        self._draw()
        
        # 离开屏幕
        if self.rect.bottom < -20:
            self.kill()
            return
        
        # 碰撞检测
        for enemy in mobs:
            if enemy not in self.hit_enemies and self.rect.colliderect(enemy.rect):
                self.hit_enemies.add(enemy)
                enemy.hp -= self.damage
                
                # 生成月眼二段伤害
                eye = MoonEyeExplosion(enemy.rect.centerx, enemy.rect.centery, 
                                       self.damage * 0.3, self.owner)
                all_sprites.add(eye)
                
                # 累加蚀印
                if not hasattr(enemy, 'eclipse_marks'):
                    enemy.eclipse_marks = 0
                enemy.eclipse_marks += 1
                
                # 蚀印效果
                if enemy.eclipse_marks >= 5:
                    enemy.eclipse_marks = 0
                    # 月蚀削弱：减速+增伤
                    if not hasattr(enemy, 'eclipse_debuff'):
                        enemy.eclipse_debuff = 0
                    enemy.eclipse_debuff = 180  # 3秒


class MoonEye(pygame.sprite.Sprite):
    """月眼 - 追踪目标的月蚀巨眼"""
    
    def __init__(self, x, y, damage, owner=None, bullet_theme=None):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.piercing = 0
        self.bullet_theme = bullet_theme
        
        # 配色 - 如果有涂装则使用涂装颜色
        if bullet_theme and bullet_theme.get('color'):
            theme_color = bullet_theme.get('color') or (100, 150, 220)
            self.sclera_color = (220, 230, 250)  # 眼白保持不变
            self.iris_color = theme_color        # 虹膜使用涂装颜色
            self.pupil_color = bullet_theme.get('trail_color') or (20, 15, 35)  # 瞳孔
        else:
            self.sclera_color = (220, 230, 250)  # 眼白
            self.iris_color = (100, 150, 220)    # 虹膜
            self.pupil_color = (20, 15, 35)      # 瞳孔
        
        # 位置
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed = 4
        self.target = None
        
        # 尺寸
        self.size = 24
        
        # 图像
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.frame = 0
        self.lifetime = 240  # 4秒
        
        self._draw()
    
    def _draw(self):
        """绘制月眼"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        r = self.size // 2 - 2
        
        # 眼白
        pygame.draw.ellipse(self.image, self.sclera_color,
                           (cx - r, cy - r * 0.6, r * 2, r * 1.2))
        
        # 虹膜
        iris_r = int(r * 0.6)
        wobble = math.sin(self.frame * 0.1) * 2
        pygame.draw.circle(self.image, self.iris_color, 
                          (int(cx + wobble), cy), iris_r)
        
        # 瞳孔（竖瞳）
        pupil_h = int(r * 0.7)
        pupil_w = max(2, int(r * 0.15 + abs(math.sin(self.frame * 0.2)) * 3))
        pygame.draw.ellipse(self.image, self.pupil_color,
                           (cx - pupil_w // 2, cy - pupil_h // 2, pupil_w, pupil_h))
        
        # 高光
        pygame.draw.circle(self.image, (255, 255, 255), 
                          (int(cx - r * 0.25), int(cy - r * 0.2)), 2)
    
    def _find_target(self):
        """寻找最近目标"""
        min_dist = float('inf')
        closest = None
        for enemy in mobs:
            dx = enemy.rect.centerx - self.float_x
            dy = enemy.rect.centery - self.float_y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < min_dist:
                min_dist = dist
                closest = enemy
        return closest
    
    def update(self):
        """更新月眼"""
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 追踪目标
        if self.target is None or not self.target.alive():
            self.target = self._find_target()
        
        if self.target:
            dx = self.target.rect.centerx - self.float_x
            dy = self.target.rect.centery - self.float_y
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist > 0:
                self.float_x += (dx / dist) * self.speed
                self.float_y += (dy / dist) * self.speed
        else:
            # 无目标时向上移动
            self.float_y -= self.speed * 0.5
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        self._draw()
        
        # 离开屏幕
        if self.rect.bottom < -20 or self.rect.top > HEIGHT + 20:
            self.kill()
            return
        
        # 碰撞检测
        for enemy in mobs:
            if self.rect.colliderect(enemy.rect):
                enemy.hp -= self.damage
                
                # 爆炸效果
                exp = MoonEyeExplosion(enemy.rect.centerx, enemy.rect.centery,
                                       self.damage * 0.5, self.owner)
                all_sprites.add(exp)
                
                self.kill()
                return


class MoonEyeExplosion(pygame.sprite.Sprite):
    """月眼爆炸 - 二段真伤"""
    
    def __init__(self, x, y, damage, owner=None):
        super().__init__()
        self.damage = damage
        self.owner = owner
        
        self.x = x
        self.y = y
        self.radius = 40
        self.max_radius = 60
        
        self.image = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.frame = 0
        self.duration = 20
        self.damage_dealt = False
    
    def _draw(self):
        """绘制爆炸"""
        self.image.fill((0, 0, 0, 0))
        progress = self.frame / self.duration
        
        cx, cy = self.max_radius, self.max_radius
        current_r = int(self.radius + (self.max_radius - self.radius) * progress)
        alpha = int(200 * (1 - progress))
        
        # 外环
        pygame.draw.circle(self.image, (160, 100, 200, alpha), (cx, cy), current_r, 4)
        
        # 内核
        inner_r = int(current_r * 0.5)
        pygame.draw.circle(self.image, (100, 150, 220, alpha), (cx, cy), inner_r)
        
        # 眼睛图案
        if progress < 0.5:
            eye_alpha = int(200 * (1 - progress * 2))
            pygame.draw.ellipse(self.image, (220, 230, 250, eye_alpha),
                               (cx - 15, cy - 8, 30, 16))
            pygame.draw.ellipse(self.image, (20, 15, 35, eye_alpha),
                               (cx - 3, cy - 6, 6, 12))
    
    def update(self):
        """更新爆炸"""
        self.frame += 1
        self._draw()
        
        # 造成伤害
        if not self.damage_dealt and self.frame >= 5:
            self.damage_dealt = True
            for enemy in mobs:
                dx = enemy.rect.centerx - self.x
                dy = enemy.rect.centery - self.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < self.max_radius:
                    # 真伤 - 无视防御
                    enemy.hp -= self.damage
        
        if self.frame >= self.duration:
            self.kill()


class EclipseDescent(pygame.sprite.Sprite):
    """月蚀降临 - 三段大招
    
    第一阶段 (2s): 月虹解放 - 全屏月虹光束扫射+吸收弹幕化为护盾
    第二阶段 (3s): 星骸召唤 - 召唤8条月能触手+吸盘攻击+末端眼球
    第三阶段 (5s): 月蚀降临 - 巨眼降临+触手环绕+毁灭光柱+疯狂debuff
    """
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 2.5
        
        # 阶段
        self.phase = 0
        self.frame = 0
        self.phase_duration = [120, 180, 300]  # 每阶段帧数（2秒、3秒、5秒）
        
        # 触手数据
        self.tentacles = []
        
        # 巨眼数据
        self.giant_eye_y = -120
        self.eye_open = 0  # 眼睛睁开程度
        self.pupil_target = None  # 瞳孔追踪目标
        
        # 小眼球
        self.small_eyes = []
        
        # 屏幕震动
        self.screen_shake = 0
        
        # 粒子效果
        self.particles = []
        
        # 符文
        self.runes = []
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _add_particle(self, x, y, vx, vy, color, life, size=3):
        """添加粒子"""
        self.particles.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color, 'life': life, 'max_life': life, 'size': size
        })
    
    def _update_particles(self):
        """更新并绘制粒子"""
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            
            alpha = int(255 * p['life'] / p['max_life'])
            size = int(p['size'] * p['life'] / p['max_life'])
            if size > 0:
                pygame.draw.circle(self.image, (*p['color'][:3], alpha), 
                                 (int(p['x']), int(p['y'])), size)
    
    def _phase1_moon_rainbow(self):
        """第一阶段：月虹解放 - 全屏横扫+弹幕吸收"""
        self.image.fill((0, 0, 0, 0))
        progress = self.frame / self.phase_duration[0]
        
        # 背景暗化
        dark_alpha = int(80 * math.sin(progress * math.pi))
        pygame.draw.rect(self.image, (10, 5, 20, dark_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 月虹光束 - 从上到下扫射
        beam_y = int(50 + progress * 550)
        beam_h = 40 + int(math.sin(self.frame * 0.3) * 10)
        
        # 光束前的预警线
        warn_y = beam_y + 60
        if warn_y < HEIGHT:
            pygame.draw.line(self.image, (255, 100, 100, 100), (0, warn_y), (WIDTH, warn_y), 2)
        
        # 多层月虹光束（彩虹渐变）
        rainbow_colors = [
            (255, 100, 150),  # 粉红
            (255, 150, 100),  # 橙
            (255, 255, 150),  # 黄
            (150, 255, 150),  # 绿
            (100, 200, 255),  # 青
            (100, 150, 255),  # 蓝
            (180, 100, 255),  # 紫
        ]
        for i, col in enumerate(rainbow_colors):
            layer_y = beam_y - beam_h // 2 + i * (beam_h // len(rainbow_colors))
            layer_h = beam_h // len(rainbow_colors) + 4
            alpha = 180 - i * 10
            pygame.draw.rect(self.image, (*col, alpha), (0, layer_y, WIDTH, layer_h))
        
        # 核心白光
        pygame.draw.rect(self.image, (255, 255, 255, 220), (0, beam_y - 6, WIDTH, 12))
        
        # 光束边缘火花
        for i in range(8):
            spark_x = random.randint(0, WIDTH)
            spark_y = beam_y + random.randint(-beam_h//2, beam_h//2)
            self._add_particle(spark_x, spark_y, random.uniform(-3, 3), random.uniform(-5, 0),
                             random.choice(rainbow_colors), random.randint(10, 25), 4)
        
        # 吸收敌弹 - 带吸收特效
        for bullet in list(enemy_bullets):
            if abs(bullet.rect.centery - beam_y) < 80:
                # 吸收光线
                pygame.draw.line(self.image, (255, 255, 200, 150),
                               (bullet.rect.centerx, bullet.rect.centery),
                               (self.owner.rect.centerx, self.owner.rect.centery), 2)
                bullet.kill()
                if hasattr(self.owner, 'shield'):
                    self.owner.shield = min(self.owner.shield + 2, self.owner.max_shield)
                # 吸收粒子
                self._add_particle(bullet.rect.centerx, bullet.rect.centery,
                                 0, -3, (200, 255, 255), 20, 5)
        
        # 对路径上敌人造成伤害
        if self.frame % 8 == 0:
            for enemy in mobs:
                if abs(enemy.rect.centery - beam_y) < 50:
                    enemy.hp -= self.damage * 0.35
                    # 命中特效
                    for _ in range(5):
                        self._add_particle(enemy.rect.centerx, enemy.rect.centery,
                                         random.uniform(-4, 4), random.uniform(-4, 4),
                                         (255, 200, 100), 15, 3)
        
        # 玩家周围的能量环
        ox, oy = self.owner.rect.centerx, self.owner.rect.centery
        ring_r = 50 + int(math.sin(self.frame * 0.2) * 10)
        pygame.draw.circle(self.image, (100, 150, 220, 100), (ox, oy), ring_r, 3)
        pygame.draw.circle(self.image, (160, 100, 200, 80), (ox, oy), ring_r + 15, 2)
        
        self._update_particles()
    
    def _phase2_starbone_summon(self):
        """第二阶段：星骸召唤 - 8条触手+吸盘+眼球"""
        self.image.fill((0, 0, 0, 0))
        
        # 背景深渊化
        pygame.draw.rect(self.image, (5, 10, 15, 60), (0, 0, WIDTH, HEIGHT))
        
        # 在阶段开始时生成8条触手
        if self.frame == 1:
            for i in range(8):
                angle = i * 45
                tentacle = {
                    'angle': angle,
                    'length': 0,
                    'max_length': 250,
                    'x': self.owner.rect.centerx,
                    'y': self.owner.rect.centery,
                    'phase_offset': random.uniform(0, 2 * math.pi),
                    'thickness': random.randint(8, 14),
                    'eye_size': random.randint(10, 18),
                    'sucker_count': random.randint(6, 10),
                }
                self.tentacles.append(tentacle)
        
        # 更新玩家位置（触手跟随）
        for t in self.tentacles:
            t['x'] = self.owner.rect.centerx
            t['y'] = self.owner.rect.centery
        
        # 绘制触手
        for ti, t in enumerate(self.tentacles):
            if t['length'] < t['max_length']:
                t['length'] += 4
            
            # 触手蜿蜒路径
            segments = 25
            points = []
            suckers = []
            
            for i in range(segments + 1):
                prog = i / segments
                base_angle = math.radians(t['angle'])
                
                # 多重波动
                wave1 = math.sin(self.frame * 0.08 + prog * 5 + t['phase_offset']) * (15 + prog * 25)
                wave2 = math.cos(self.frame * 0.12 + prog * 3 + t['phase_offset']) * 8
                
                dist = t['length'] * prog
                perp = base_angle + math.pi / 2
                
                px = t['x'] + math.cos(base_angle) * dist + math.cos(perp) * (wave1 + wave2)
                py = t['y'] + math.sin(base_angle) * dist + math.sin(perp) * (wave1 + wave2)
                points.append((int(px), int(py)))
                
                # 吸盘位置
                if i > 2 and i < segments - 2 and i % 3 == 0:
                    suckers.append((int(px), int(py), prog))
            
            if len(points) >= 2:
                # 触手阴影
                shadow_points = [(p[0] + 3, p[1] + 3) for p in points]
                pygame.draw.lines(self.image, (20, 10, 30), False, shadow_points, t['thickness'] + 2)
                
                # 触手主体（渐变）
                for i in range(len(points) - 1):
                    prog = i / len(points)
                    thickness = int(t['thickness'] * (1 - prog * 0.7))
                    # 颜色从紫到青绿
                    r = int(160 - prog * 80)
                    g = int(100 + prog * 60)
                    b = int(200 - prog * 40)
                    pygame.draw.line(self.image, (r, g, b), points[i], points[i + 1], thickness)
                
                # 触手高光
                for i in range(len(points) - 1):
                    pygame.draw.line(self.image, (180, 150, 220), points[i], points[i + 1], 2)
                
                # 吸盘
                for sx, sy, prog in suckers:
                    sucker_r = int(6 * (1 - prog * 0.5))
                    pygame.draw.circle(self.image, (80, 50, 100), (sx, sy), sucker_r)
                    pygame.draw.circle(self.image, (40, 25, 50), (sx, sy), sucker_r - 2)
                
                # 末端眼球
                if len(points) > 0:
                    end_x, end_y = points[-1]
                    eye_r = t['eye_size']
                    
                    # 眼白
                    pygame.draw.ellipse(self.image, (220, 210, 200),
                                       (end_x - eye_r, end_y - eye_r * 0.6, eye_r * 2, eye_r * 1.2))
                    # 血丝
                    for bi in range(4):
                        ba = bi * 90 + self.frame * 2
                        bx = end_x + math.cos(math.radians(ba)) * eye_r * 0.6
                        by = end_y + math.sin(math.radians(ba)) * eye_r * 0.35
                        pygame.draw.line(self.image, (180, 60, 60), (end_x, end_y), (int(bx), int(by)), 1)
                    
                    # 虹膜（看向最近敌人）
                    iris_r = int(eye_r * 0.5)
                    look_x, look_y = 0, 0
                    min_dist = float('inf')
                    for enemy in mobs:
                        dx = enemy.rect.centerx - end_x
                        dy = enemy.rect.centery - end_y
                        d = math.sqrt(dx*dx + dy*dy)
                        if d < min_dist:
                            min_dist = d
                            if d > 0:
                                look_x = dx / d * 3
                                look_y = dy / d * 2
                    pygame.draw.circle(self.image, (100, 180, 150), 
                                      (int(end_x + look_x), int(end_y + look_y)), iris_r)
                    # 瞳孔
                    pygame.draw.ellipse(self.image, (10, 15, 12),
                                       (int(end_x + look_x) - 2, int(end_y + look_y) - iris_r * 0.7,
                                        4, int(iris_r * 1.4)))
                    # 高光
                    pygame.draw.circle(self.image, (255, 255, 255),
                                      (int(end_x - eye_r * 0.3), int(end_y - eye_r * 0.2)), 2)
        
        # 触手攻击
        if self.frame % 12 == 0:
            for t in self.tentacles:
                angle_rad = math.radians(t['angle'])
                for enemy in mobs:
                    dx = enemy.rect.centerx - t['x']
                    dy = enemy.rect.centery - t['y']
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist < t['length'] + 40:
                        enemy.hp -= self.damage * 0.25
                        # 攻击特效
                        for _ in range(3):
                            self._add_particle(enemy.rect.centerx, enemy.rect.centery,
                                             random.uniform(-3, 3), random.uniform(-3, 3),
                                             (160, 100, 200), 15, 4)
        
        # 中心能量核心
        ox, oy = self.owner.rect.centerx, self.owner.rect.centery
        core_pulse = abs(math.sin(self.frame * 0.15))
        core_r = 25 + int(core_pulse * 15)
        pygame.draw.circle(self.image, (160, 100, 200, 150), (ox, oy), core_r)
        pygame.draw.circle(self.image, (220, 200, 255, 200), (ox, oy), core_r - 10)
        
        self._update_particles()
    
    def _phase3_eclipse_descent(self):
        """第三阶段：月蚀降临 - 巨眼降临+触手环绕+毁灭光柱"""
        self.image.fill((0, 0, 0, 0))
        phase_progress = self.frame / self.phase_duration[2]
        
        # 黑暗笼罩
        dark_intensity = min(phase_progress * 2, 1)
        pygame.draw.rect(self.image, (5, 5, 10, int(100 * dark_intensity)), (0, 0, WIDTH, HEIGHT))
        
        # 巨眼降临
        if self.giant_eye_y < 120:
            self.giant_eye_y += 3
        if self.eye_open < 1:
            self.eye_open = min(1, self.eye_open + 0.02)
        
        eye_x = WIDTH // 2
        eye_y = int(self.giant_eye_y)
        eye_r = 100  # 更大的眼睛
        
        # 眼睛周围的黑暗光晕
        for i in range(5):
            halo_r = eye_r + 30 + i * 20
            pygame.draw.circle(self.image, (20, 10, 30, 50 - i * 8), (eye_x, eye_y), halo_r)
        
        # 眼部边框（眼皮）
        lid_close = (1 - self.eye_open) * eye_r * 0.6
        
        # 眼白
        pygame.draw.ellipse(self.image, (200, 190, 180),
                           (eye_x - eye_r, eye_y - eye_r * 0.5 * self.eye_open + lid_close,
                            eye_r * 2, eye_r * self.eye_open))
        
        # 血丝网
        if self.eye_open > 0.5:
            for i in range(12):
                angle = i * 30 + self.frame
                bx = eye_x + math.cos(math.radians(angle)) * eye_r * 0.8
                by = eye_y + math.sin(math.radians(angle)) * eye_r * 0.4 * self.eye_open
                pygame.draw.line(self.image, (180, 50, 50), (eye_x, eye_y), (int(bx), int(by)), 1)
        
        # 虹膜 - 寻找目标
        if self.pupil_target is None or not self.pupil_target.alive():
            for enemy in mobs:
                self.pupil_target = enemy
                break
        
        iris_r = int(eye_r * 0.55 * self.eye_open)
        look_x, look_y = 0, 0
        if self.pupil_target:
            dx = self.pupil_target.rect.centerx - eye_x
            dy = self.pupil_target.rect.centery - eye_y
            d = max(1, math.sqrt(dx*dx + dy*dy))
            look_x = dx / d * 8
            look_y = dy / d * 4
        
        # 虹膜（诡异的颜色）
        iris_color_shift = self.frame * 0.05
        iris_r_col = int(80 + math.sin(iris_color_shift) * 40)
        iris_g_col = int(150 + math.cos(iris_color_shift * 0.7) * 50)
        iris_b_col = int(180 + math.sin(iris_color_shift * 1.3) * 40)
        pygame.draw.circle(self.image, (iris_r_col, iris_g_col, iris_b_col),
                          (int(eye_x + look_x), int(eye_y + look_y)), iris_r)
        
        # 虹膜纹理
        for i in range(8):
            ia = self.frame * 0.1 + i * 0.78
            ix = eye_x + look_x + math.cos(ia) * iris_r * 0.7
            iy = eye_y + look_y + math.sin(ia) * iris_r * 0.7 * self.eye_open
            pygame.draw.line(self.image, (50, 80, 100),
                           (int(eye_x + look_x), int(eye_y + look_y)), (int(ix), int(iy)), 2)
        
        # 瞳孔（竖瞳，会收缩）
        pupil_h = int(eye_r * 0.7 * self.eye_open)
        pupil_w = max(3, int(eye_r * 0.12 + abs(math.sin(self.frame * 0.08)) * 15))
        pygame.draw.ellipse(self.image, (5, 5, 8),
                           (int(eye_x + look_x) - pupil_w // 2, 
                            int(eye_y + look_y) - pupil_h // 2, pupil_w, pupil_h))
        
        # 高光
        pygame.draw.circle(self.image, (255, 255, 255),
                          (int(eye_x - eye_r * 0.3), int(eye_y - eye_r * 0.15)), 8)
        pygame.draw.circle(self.image, (255, 255, 255),
                          (int(eye_x - eye_r * 0.15), int(eye_y - eye_r * 0.25)), 4)
        
        # 眼皮阴影
        pygame.draw.arc(self.image, (40, 20, 50),
                       (eye_x - eye_r - 5, eye_y - eye_r * 0.6, eye_r * 2 + 10, eye_r * 1.2),
                       0, math.pi, 8)
        
        # 眼睛周围的小触手
        for i in range(12):
            t_angle = i * 30 + math.sin(self.frame * 0.05 + i) * 10
            t_length = 40 + math.sin(self.frame * 0.1 + i * 0.5) * 15
            t_start_x = eye_x + math.cos(math.radians(t_angle)) * eye_r
            t_start_y = eye_y + math.sin(math.radians(t_angle)) * eye_r * 0.6
            
            points = [(int(t_start_x), int(t_start_y))]
            for j in range(6):
                prog = (j + 1) / 6
                wave = math.sin(self.frame * 0.15 + prog * 4 + i) * 10
                dist = t_length * prog
                px = t_start_x + math.cos(math.radians(t_angle)) * dist + wave
                py = t_start_y + math.sin(math.radians(t_angle)) * dist
                points.append((int(px), int(py)))
            
            for j in range(len(points) - 1):
                thick = max(1, 4 - j)
                pygame.draw.line(self.image, (100, 60, 120), points[j], points[j + 1], thick)
        
        # 月蚀光柱
        if phase_progress > 0.25:
            beam_progress = (phase_progress - 0.25) / 0.75
            
            # 蓄力效果
            if beam_progress < 0.2:
                charge = beam_progress / 0.2
                # 能量聚集
                for i in range(20):
                    angle = random.uniform(0, 360)
                    dist = 200 * (1 - charge) + 50
                    px = eye_x + math.cos(math.radians(angle)) * dist
                    py = eye_y + eye_r + math.sin(math.radians(angle)) * dist * 0.5
                    pygame.draw.line(self.image, (180, 100, 255, int(150 * charge)),
                                   (int(px), int(py)), (eye_x, eye_y + int(eye_r * 0.8)), 1)
            
            # 光柱
            if beam_progress >= 0.2:
                actual_beam = (beam_progress - 0.2) / 0.8
                beam_width = int(80 + actual_beam * 60)
                beam_alpha = int(220 * min(actual_beam * 3, 1))
                
                # 多层光柱
                layer_colors = [
                    (100, 50, 150),   # 深紫
                    (140, 80, 180),   # 紫
                    (180, 120, 220),  # 浅紫
                    (200, 160, 240),  # 粉紫
                    (255, 255, 255),  # 白核心
                ]
                for i, col in enumerate(layer_colors):
                    layer_w = beam_width - i * 15
                    if layer_w > 0:
                        layer_alpha = max(0, beam_alpha - i * 30)
                        pygame.draw.rect(self.image, (*col, layer_alpha),
                                       (eye_x - layer_w // 2, eye_y + int(eye_r * 0.8), layer_w, HEIGHT))
                
                # 光柱边缘闪电
                for side in [-1, 1]:
                    for j in range(5):
                        lx = eye_x + side * (beam_width // 2 + 5)
                        ly = eye_y + eye_r + j * 80 + int(self.frame * 5) % 80
                        if ly < HEIGHT:
                            # 锯齿闪电
                            lightning_points = [(lx, ly)]
                            for k in range(4):
                                lx += random.randint(-20, 20) * side
                                ly += random.randint(10, 30)
                                lightning_points.append((lx, ly))
                            pygame.draw.lines(self.image, (200, 150, 255), False, lightning_points, 2)
                
                # 伤害
                if self.frame % 4 == 0:
                    for enemy in mobs:
                        if abs(enemy.rect.centerx - eye_x) < beam_width // 2 + 40:
                            enemy.hp -= self.damage * 0.6
                            # 疯狂debuff
                            if not hasattr(enemy, 'madness'):
                                enemy.madness = 0
                            enemy.madness += 1
                            # 命中特效
                            self._add_particle(enemy.rect.centerx, enemy.rect.centery,
                                             random.uniform(-5, 5), random.uniform(-8, -2),
                                             (200, 150, 255), 20, 5)
        
        # 空间扭曲效果
        if phase_progress > 0.5:
            for i in range(3):
                warp_r = 150 + i * 50 + int(math.sin(self.frame * 0.1 + i) * 20)
                pygame.draw.circle(self.image, (160, 100, 200, 40), (eye_x, eye_y + 200), warp_r, 2)
        
        # 邪教符文环绕
        rune_r = 180 + int(math.sin(self.frame * 0.08) * 20)
        for i in range(8):
            rune_angle = self.frame * 0.5 + i * 45
            rx = eye_x + math.cos(math.radians(rune_angle)) * rune_r
            ry = eye_y + 150 + math.sin(math.radians(rune_angle)) * rune_r * 0.3
            
            # 符文（简化几何）
            if i % 2 == 0:
                # 三角
                tri_r = 12
                tri_points = [(rx, ry - tri_r),
                             (rx - tri_r * 0.866, ry + tri_r * 0.5),
                             (rx + tri_r * 0.866, ry + tri_r * 0.5)]
                pygame.draw.polygon(self.image, (180, 140, 80), tri_points, 2)
            else:
                # 圆+十字
                pygame.draw.circle(self.image, (180, 140, 80), (int(rx), int(ry)), 10, 2)
                pygame.draw.line(self.image, (180, 140, 80), (int(rx) - 6, int(ry)), (int(rx) + 6, int(ry)), 2)
                pygame.draw.line(self.image, (180, 140, 80), (int(rx), int(ry) - 6), (int(rx), int(ry) + 6), 2)
        
        self._update_particles()
    
    def update(self):
        """更新月蚀降临"""
        self.frame += 1
        
        if self.phase == 0:
            self._phase1_moon_rainbow()
            if self.frame >= self.phase_duration[0]:
                self.phase = 1
                self.frame = 0
        
        elif self.phase == 1:
            self._phase2_starbone_summon()
            if self.frame >= self.phase_duration[1]:
                self.phase = 2
                self.frame = 0
                self.tentacles.clear()
        
        elif self.phase == 2:
            self._phase3_eclipse_descent()
            if self.frame >= self.phase_duration[2]:
                self.kill()


class AbyssalTentacles(pygame.sprite.Sprite):
    """【深渊触手】G键第二大招 - 从屏幕边缘伸出巨型触手抓取敌人
    
    效果：
    1. 从四个屏幕边缘各伸出3条巨型触手
    2. 触手会自动寻找并抓取敌人
    3. 被抓取的敌人持续受伤+减速
    4. 触手末端有巨大眼球监视
    """
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 1.8
        self.frame = 0
        self.duration = 300  # 5秒
        
        # 触手数据
        self.tentacles = []
        self._init_tentacles()
        
        # 粒子
        self.particles = []
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _init_tentacles(self):
        """初始化12条触手（每边3条）"""
        edges = [
            ('top', 0, 1),      # 从上边向下伸入
            ('bottom', 0, -1),  # 从下边向上伸入
            ('left', 1, 0),     # 从左边向右伸入
            ('right', -1, 0),   # 从右边向左伸入
        ]
        
        for edge_name, dx, dy in edges:
            for i in range(3):
                if edge_name == 'top':
                    start_x = WIDTH // 4 + i * (WIDTH // 4)
                    start_y = -20
                elif edge_name == 'bottom':
                    start_x = WIDTH // 4 + i * (WIDTH // 4)
                    start_y = HEIGHT + 20
                elif edge_name == 'left':
                    start_x = -20
                    start_y = HEIGHT // 4 + i * (HEIGHT // 4)
                else:  # right
                    start_x = WIDTH + 20
                    start_y = HEIGHT // 4 + i * (HEIGHT // 4)
                
                self.tentacles.append({
                    'start_x': start_x,
                    'start_y': start_y,
                    'dx': dx,
                    'dy': dy,
                    'length': 0,
                    'max_length': 280,
                    'target': None,
                    'grab_timer': 0,
                    'phase_offset': random.uniform(0, 2 * math.pi),
                    'thickness': random.randint(12, 18),
                    'color': random.choice([
                        (120, 80, 150),
                        (100, 60, 130),
                        (140, 90, 160),
                    ]),
                })
    
    def _find_target(self, tentacle):
        """为触手寻找目标"""
        min_dist = float('inf')
        best_target = None
        tip_x = tentacle['start_x'] + tentacle['dx'] * tentacle['length']
        tip_y = tentacle['start_y'] + tentacle['dy'] * tentacle['length']
        
        for enemy in mobs:
            if not hasattr(enemy, 'grabbed_by') or enemy.grabbed_by is None:
                dx = enemy.rect.centerx - tip_x
                dy = enemy.rect.centery - tip_y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < min_dist and dist < 150:
                    min_dist = dist
                    best_target = enemy
        
        return best_target
    
    def _add_particle(self, x, y, vx, vy, color, life, size=3):
        self.particles.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color, 'life': life, 'max_life': life, 'size': size
        })
    
    def _update_particles(self):
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            alpha = int(255 * p['life'] / p['max_life'])
            size = int(p['size'] * p['life'] / p['max_life'])
            if size > 0:
                pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                                 (int(p['x']), int(p['y'])), size)
    
    def update(self):
        self.frame += 1
        self.image.fill((0, 0, 0, 0))
        
        # 深渊背景
        pygame.draw.rect(self.image, (10, 5, 20, 40), (0, 0, WIDTH, HEIGHT))
        
        for t in self.tentacles:
            # 触手伸展
            if t['length'] < t['max_length']:
                t['length'] += 4
            
            # 寻找目标
            if t['target'] is None and self.frame % 30 == 0:
                t['target'] = self._find_target(t)
            
            # 计算触手路径
            segments = 20
            points = []
            
            for i in range(segments + 1):
                prog = i / segments
                
                # 基础位置
                base_x = t['start_x'] + t['dx'] * t['length'] * prog
                base_y = t['start_y'] + t['dy'] * t['length'] * prog
                
                # 波动
                wave = math.sin(self.frame * 0.1 + prog * 4 + t['phase_offset']) * (20 * prog)
                if t['dx'] != 0:  # 水平触手，垂直波动
                    base_y += wave
                else:  # 垂直触手，水平波动
                    base_x += wave
                
                # 如果有目标，末端弯向目标
                if t['target'] and t['target'].alive() and prog > 0.7:
                    bend = (prog - 0.7) / 0.3
                    target_x = t['target'].rect.centerx
                    target_y = t['target'].rect.centery
                    base_x = base_x + (target_x - base_x) * bend * 0.5
                    base_y = base_y + (target_y - base_y) * bend * 0.5
                
                points.append((int(base_x), int(base_y)))
            
            # 绘制触手
            if len(points) >= 2:
                # 阴影
                shadow_points = [(p[0] + 4, p[1] + 4) for p in points]
                pygame.draw.lines(self.image, (20, 10, 30), False, shadow_points, t['thickness'] + 4)
                
                # 主体渐变
                for i in range(len(points) - 1):
                    prog = i / len(points)
                    thick = int(t['thickness'] * (1 - prog * 0.6))
                    r = int(t['color'][0] * (1 - prog * 0.3))
                    g = int(t['color'][1] * (1 - prog * 0.3))
                    b = int(t['color'][2] * (1 - prog * 0.3))
                    pygame.draw.line(self.image, (r, g, b), points[i], points[i + 1], thick)
                
                # 高光
                pygame.draw.lines(self.image, (180, 150, 200), False, points, 2)
                
                # 吸盘
                for i in range(3, len(points) - 3, 4):
                    sx, sy = points[i]
                    sucker_r = int(6 * (1 - i / len(points) * 0.5))
                    pygame.draw.circle(self.image, (60, 40, 80), (sx, sy), sucker_r)
                    pygame.draw.circle(self.image, (30, 20, 40), (sx, sy), sucker_r - 2)
                
                # 末端眼球
                end_x, end_y = points[-1]
                eye_r = 15
                pygame.draw.ellipse(self.image, (220, 210, 200),
                                   (end_x - eye_r, end_y - eye_r * 0.7, eye_r * 2, eye_r * 1.4))
                
                # 虹膜
                iris_offset_x, iris_offset_y = 0, 0
                if t['target'] and t['target'].alive():
                    dx = t['target'].rect.centerx - end_x
                    dy = t['target'].rect.centery - end_y
                    d = max(1, math.sqrt(dx*dx + dy*dy))
                    iris_offset_x = dx / d * 4
                    iris_offset_y = dy / d * 3
                pygame.draw.circle(self.image, (80, 150, 120),
                                  (int(end_x + iris_offset_x), int(end_y + iris_offset_y)), 8)
                pygame.draw.ellipse(self.image, (10, 15, 10),
                                   (int(end_x + iris_offset_x) - 2, int(end_y + iris_offset_y) - 6, 4, 12))
                pygame.draw.circle(self.image, (255, 255, 255),
                                  (int(end_x - 4), int(end_y - 3)), 2)
            
            # 抓取伤害
            if t['target'] and t['target'].alive() and len(points) > 0:
                end_x, end_y = points[-1]
                dist = math.sqrt((t['target'].rect.centerx - end_x)**2 + 
                                (t['target'].rect.centery - end_y)**2)
                if dist < 40:
                    t['grab_timer'] += 1
                    if t['grab_timer'] % 15 == 0:
                        t['target'].hp -= self.damage * 0.15
                        # 粘液粒子
                        self._add_particle(t['target'].rect.centerx, t['target'].rect.centery,
                                          random.uniform(-2, 2), random.uniform(-2, 2),
                                          (100, 150, 100), 20, 4)
                    # 减速效果
                    if hasattr(t['target'], 'slow_timer'):
                        t['target'].slow_timer = 30
            else:
                t['grab_timer'] = 0
                if t['target'] and not t['target'].alive():
                    t['target'] = None
        
        self._update_particles()
        
        if self.frame >= self.duration:
            # 释放所有被抓取的敌人
            for t in self.tentacles:
                if t['target'] and hasattr(t['target'], 'grabbed_by'):
                    t['target'].grabbed_by = None
            self.kill()


class MadnessAura(pygame.sprite.Sprite):
    """【疯狂领域】C键第三大招 - 释放精神污染波动
    
    效果：
    1. 以玩家为中心释放不断扩大的疯狂波动
    2. 敌人在领域内持续掉SAN值（持续伤害）
    3. SAN值归零的敌人会陷入混乱（攻击友军）
    4. 全屏幻觉效果：非欧几何、扭曲的眼睛、浮动符文
    """
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 2.0
        self.frame = 0
        self.duration = 360  # 6秒
        
        # 波动数据
        self.waves = []
        self.wave_interval = 40  # 每40帧释放一波
        
        # 幻觉元素
        self.hallucinations = []
        self._init_hallucinations()
        
        # 疯狂眼睛
        self.mad_eyes = []
        
        # 非欧几何碎片
        self.geometry_shards = []
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _init_hallucinations(self):
        """初始化幻觉元素"""
        for _ in range(15):
            self.hallucinations.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'type': random.choice(['eye', 'rune', 'tentacle', 'geometry']),
                'size': random.randint(15, 40),
                'phase': random.uniform(0, 2 * math.pi),
                'speed': random.uniform(0.02, 0.08),
                'alpha': 0,
            })
    
    def _draw_hallucination(self, h):
        """绘制单个幻觉"""
        x, y = int(h['x']), int(h['y'])
        size = h['size']
        alpha = int(h['alpha'])
        
        if h['type'] == 'eye':
            # 疯狂之眼
            pygame.draw.ellipse(self.image, (200, 190, 180, alpha),
                               (x - size, y - size // 2, size * 2, size))
            # 血丝
            for i in range(6):
                angle = i * 60 + self.frame
                bx = x + math.cos(math.radians(angle)) * size * 0.7
                by = y + math.sin(math.radians(angle)) * size * 0.35
                pygame.draw.line(self.image, (180, 50, 50, alpha // 2), (x, y), (int(bx), int(by)), 1)
            # 虹膜
            iris_r = size // 3
            shift = math.sin(self.frame * 0.1 + h['phase']) * 3
            pygame.draw.circle(self.image, (100, 180, 150, alpha), (int(x + shift), y), iris_r)
            # 瞳孔
            pygame.draw.ellipse(self.image, (10, 10, 10, alpha),
                               (int(x + shift) - 2, y - iris_r + 2, 4, iris_r * 2 - 4))
        
        elif h['type'] == 'rune':
            # 邪教符文
            points = []
            for i in range(5):
                angle = i * 72 - 90 + self.frame * 0.5
                px = x + math.cos(math.radians(angle)) * size
                py = y + math.sin(math.radians(angle)) * size
                points.append((int(px), int(py)))
            if len(points) >= 5:
                # 五芒星
                star_order = [0, 2, 4, 1, 3, 0]
                star_points = [points[i] for i in star_order]
                pygame.draw.lines(self.image, (180, 140, 80, alpha), True, star_points, 2)
                pygame.draw.circle(self.image, (180, 140, 80, alpha // 2), (x, y), size, 1)
        
        elif h['type'] == 'tentacle':
            # 小触手
            segments = 8
            t_points = [(x, y)]
            for i in range(1, segments + 1):
                prog = i / segments
                wave = math.sin(self.frame * 0.15 + prog * 3 + h['phase']) * (10 * prog)
                px = x + wave
                py = y + prog * size * 1.5
                t_points.append((int(px), int(py)))
            pygame.draw.lines(self.image, (120, 80, 140, alpha), False, t_points, max(1, 4 - len(t_points) // 3))
        
        elif h['type'] == 'geometry':
            # 非欧几何
            # 不可能三角
            tri_size = size
            p1 = (x, y - tri_size)
            p2 = (x - tri_size * 0.866, y + tri_size * 0.5)
            p3 = (x + tri_size * 0.866, y + tri_size * 0.5)
            pygame.draw.polygon(self.image, (160, 100, 200, alpha), [p1, p2, p3], 2)
            # 内部扭曲
            inner_r = tri_size * 0.4
            for i in range(3):
                ia = self.frame * 0.1 + i * 2.094
                ix = x + math.cos(ia) * inner_r
                iy = y + math.sin(ia) * inner_r
                pygame.draw.line(self.image, (200, 150, 255, alpha // 2), (x, y), (int(ix), int(iy)), 1)
    
    def update(self):
        self.frame += 1
        self.image.fill((0, 0, 0, 0))
        
        # 疯狂背景脉动
        pulse = abs(math.sin(self.frame * 0.05))
        bg_alpha = int(30 + pulse * 30)
        pygame.draw.rect(self.image, (20, 10, 30, bg_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 释放疯狂波动
        if self.frame % self.wave_interval == 0:
            self.waves.append({
                'x': self.owner.rect.centerx,
                'y': self.owner.rect.centery,
                'radius': 30,
                'max_radius': 400,
                'alpha': 200,
            })
        
        # 更新和绘制波动
        for wave in self.waves[:]:
            wave['radius'] += 5
            wave['alpha'] = int(200 * (1 - wave['radius'] / wave['max_radius']))
            
            if wave['radius'] >= wave['max_radius']:
                self.waves.remove(wave)
                continue
            
            # 绘制波动圈（多层）
            for i in range(3):
                r = wave['radius'] - i * 10
                if r > 0:
                    a = max(0, wave['alpha'] - i * 40)
                    color_shift = (self.frame * 2 + i * 30) % 360
                    # 彩虹疯狂色
                    cr = int(160 + math.sin(math.radians(color_shift)) * 60)
                    cg = int(100 + math.sin(math.radians(color_shift + 120)) * 60)
                    cb = int(200 + math.sin(math.radians(color_shift + 240)) * 40)
                    pygame.draw.circle(self.image, (cr, cg, cb, a), 
                                      (int(wave['x']), int(wave['y'])), int(r), 3)
            
            # 波动对敌人造成效果
            for enemy in mobs:
                dist = math.sqrt((enemy.rect.centerx - wave['x'])**2 + 
                                (enemy.rect.centery - wave['y'])**2)
                if abs(dist - wave['radius']) < 30:
                    # 造成伤害
                    if self.frame % 20 == 0:
                        enemy.hp -= self.damage * 0.1
                    # 施加疯狂效果
                    if not hasattr(enemy, 'madness'):
                        enemy.madness = 0
                    enemy.madness = min(100, enemy.madness + 2)
                    # 疯狂满了？混乱！
                    if enemy.madness >= 100 and not getattr(enemy, 'confused', False):
                        enemy.confused = True
                        enemy.confused_timer = 180  # 3秒混乱
        
        # 更新幻觉
        for h in self.hallucinations:
            # 漂浮运动
            h['x'] += math.sin(self.frame * h['speed'] + h['phase']) * 0.5
            h['y'] += math.cos(self.frame * h['speed'] * 0.7 + h['phase']) * 0.3
            
            # 透明度脉动
            h['alpha'] = 100 + math.sin(self.frame * 0.08 + h['phase']) * 80
            
            # 绘制
            self._draw_hallucination(h)
        
        # 玩家周围的疯狂光环
        ox, oy = self.owner.rect.centerx, self.owner.rect.centery
        aura_r = 60 + int(math.sin(self.frame * 0.1) * 15)
        pygame.draw.circle(self.image, (160, 100, 200, 100), (ox, oy), aura_r, 4)
        pygame.draw.circle(self.image, (200, 150, 255, 60), (ox, oy), aura_r + 20, 2)
        
        # 中心邪眼
        eye_pulse = abs(math.sin(self.frame * 0.08))
        eye_r = 25 + int(eye_pulse * 10)
        pygame.draw.ellipse(self.image, (200, 190, 180),
                           (ox - eye_r, oy - eye_r * 0.6, eye_r * 2, eye_r * 1.2))
        # 瞳孔随机看向
        look_angle = self.frame * 0.05
        look_x = math.cos(look_angle) * 5
        look_y = math.sin(look_angle) * 3
        pygame.draw.circle(self.image, (80, 150, 130), (int(ox + look_x), int(oy + look_y)), int(eye_r * 0.5))
        pygame.draw.ellipse(self.image, (10, 10, 10),
                           (int(ox + look_x) - 3, int(oy + look_y) - int(eye_r * 0.4), 6, int(eye_r * 0.8)))
        
        if self.frame >= self.duration:
            self.kill()
