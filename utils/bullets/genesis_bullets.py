# -*- coding: utf-8 -*-
"""
Genesis 战机子弹涂装效果渲染模块 - 终极机体专属

包含以下子弹效果：
- genesis_star: 创世之星（基础） - 宇宙大爆炸核心
- cosmic_origin: 宇宙起源 - 星云诞生扩散
- solar_birth: 太阳诞生 - 金红炽焰日冕
- nebula_seed: 星云种子 - 紫粉梦幻气体
- void_creation: 虚无创生 - 黑白太极阴阳
- life_spark: 生命火花 - DNA螺旋生命
- crystal_shard: 水晶碎片 - 棱镜折射
- chaos_burst: 混沌爆发 - 多彩能量风暴
"""
import pygame
import math


def render_genesis_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Genesis战机的子弹效果 - 终极机体级别特效
    
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
    
    if "genesis_star" in effects or "cosmic_origin" in effects:
        # 创世之星 - 宇宙大爆炸扩散（终极版）
        cosmic_gold = (255, 200, 100)
        star_white = (255, 255, 255)
        
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 宇宙扩散环
        for ring in range(5):
            ring_r = size // 6 + ring * (size // 10) + int(4 * math.sin(t * 6 - ring * 0.5))
            ring_alpha = 220 - ring * 40
            
            ring_color = (
                int(255 - ring * 10),
                int(200 - ring * 20),
                int(100 + ring * 25)
            )
            pygame.draw.circle(bullet_surf, (*ring_color, ring_alpha), (cx, cy), ring_r, 2)
        
        # 星系旋臂
        for arm in range(4):
            arm_pts = []
            for seg in range(15):
                progress = seg / 14
                angle = (arm * 90 + progress * 180 + t * 80) * math.pi / 180
                r = progress * (size // 2)
                arm_pts.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
            if len(arm_pts) > 1:
                pygame.draw.lines(bullet_surf, (*cosmic_gold, 180), False, arm_pts, 2)
        
        # 轨道行星
        planet_colors = [
            (255, 100, 100), (255, 200, 100), (100, 255, 100),
            (100, 200, 255), (150, 100, 255), (255, 100, 200)
        ]
        for planet in range(6):
            p_angle = (planet * 60 + t * 120) * math.pi / 180
            p_r = size // 3
            px = cx + int(math.cos(p_angle) * p_r)
            py = cy + int(math.sin(p_angle) * p_r * 0.6)
            
            pygame.draw.circle(bullet_surf, planet_colors[planet], (px, py), 3)
            pygame.draw.circle(bullet_surf, (255, 255, 255), (px, py), 1)
        
        # 创世核心（多层）
        for core in range(4):
            core_r = size // 5 + 2 - core
            pygame.draw.circle(bullet_surf, cosmic_gold if core < 2 else star_white, (cx, cy), core_r)
        
        # 神圣光芒
        for ray in range(8):
            ray_angle = (ray * 45 + t * 60) * math.pi / 180
            ray_len = size // 3 + 3 * abs(math.sin(t * 5 + ray))
            rx = cx + math.cos(ray_angle) * ray_len
            ry = cy + math.sin(ray_angle) * ray_len
            pygame.draw.line(bullet_surf, (255, 255, 200, 150), (cx, cy), (rx, ry), 1)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "solar_birth" in effects:
        # 太阳诞生 - 金红炽焰（增强版）
        solar_gold = (255, 200, 50)
        solar_orange = (255, 150, 0)
        solar_red = (255, 80, 30)
        
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 日冕喷发
        for flare in range(10):
            flare_angle = (flare * 36 + t * 80) * math.pi / 180
            base_len = size // 3
            flare_len = base_len + int(8 * abs(math.sin(t * 10 + flare * 0.7)))
            
            # 火焰形状
            base_l = (cx + math.cos(flare_angle + 0.2) * (base_len * 0.4),
                     cy + math.sin(flare_angle + 0.2) * (base_len * 0.4))
            base_r = (cx + math.cos(flare_angle - 0.2) * (base_len * 0.4),
                     cy + math.sin(flare_angle - 0.2) * (base_len * 0.4))
            tip = (cx + math.cos(flare_angle) * flare_len, cy + math.sin(flare_angle) * flare_len)
            
            colors = [solar_red, solar_orange, solar_gold]
            pygame.draw.polygon(bullet_surf, colors[flare % 3], [base_l, tip, base_r])
        
        # 太阳黑子
        for spot in range(3):
            spot_angle = (spot * 120 + t * 30) * math.pi / 180
            spot_r = size // 6
            sx = cx + int(math.cos(spot_angle) * spot_r)
            sy = cy + int(math.sin(spot_angle) * spot_r)
            pygame.draw.circle(bullet_surf, (200, 100, 50), (sx, sy), 3)
        
        # 核心层
        pygame.draw.circle(bullet_surf, solar_orange, (cx, cy), size // 4 + 2)
        pygame.draw.circle(bullet_surf, solar_gold, (cx, cy), size // 4)
        pygame.draw.circle(bullet_surf, (255, 255, 200), (cx, cy), size // 6)
        pygame.draw.circle(bullet_surf, (255, 255, 255), (cx, cy), size // 10)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "nebula_seed" in effects:
        # 星云种子 - 紫粉梦幻（增强版）
        nebula_purple = (180, 100, 255)
        nebula_pink = (255, 150, 200)
        nebula_blue = (150, 180, 255)
        
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 星云气体层
        for layer in range(4):
            layer_offset = t * 40 * (1 if layer % 2 == 0 else -1)
            colors = [nebula_purple, nebula_pink, nebula_blue, (200, 150, 255)]
            
            # 不规则气体团
            for blob in range(6):
                blob_angle = (blob * 60 + layer_offset + layer * 15) * math.pi / 180
                blob_r = size // 4 + layer * (size // 16)
                bx = cx + int(math.cos(blob_angle) * blob_r)
                by = cy + int(math.sin(blob_angle) * blob_r)
                
                blob_size = size // 8 + int(3 * math.sin(t * 4 + blob + layer))
                blob_alpha = 120 - layer * 25
                pygame.draw.circle(bullet_surf, (*colors[(layer + blob) % 4], blob_alpha), (bx, by), blob_size)
        
        # 新生恒星
        for star in range(5):
            star_angle = (star * 72 + t * 60) * math.pi / 180
            star_r = size // 3
            sx = cx + int(math.cos(star_angle) * star_r)
            sy = cy + int(math.sin(star_angle) * star_r)
            
            twinkle = abs(math.sin(t * 8 + star)) * 2
            pygame.draw.circle(bullet_surf, (255, 255, 255), (sx, sy), int(2 + twinkle))
        
        # 原恒星核心
        pygame.draw.circle(bullet_surf, nebula_purple, (cx, cy), size // 5)
        pygame.draw.circle(bullet_surf, nebula_pink, (cx, cy), size // 7)
        pygame.draw.circle(bullet_surf, (255, 255, 255), (cx, cy), size // 12)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "void_creation" in effects:
        # 虚无创生 - 黑白太极（增强版）
        pure_white = (255, 255, 255)
        pure_black = (0, 0, 0)
        gray = (128, 128, 128)
        
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        rotation = t * 100
        
        # 外圈阴阳场
        field_r = size // 2
        pygame.draw.circle(bullet_surf, (*gray, 100), (cx, cy), field_r + 3, 2)
        
        # 太极圆（白半）
        white_points = [(cx, cy)]
        for i in range(181):
            angle = (i + rotation) * math.pi / 180
            white_points.append((
                cx + int(math.cos(angle) * (size // 3)),
                cy + int(math.sin(angle) * (size // 3))
            ))
        if len(white_points) > 2:
            pygame.draw.polygon(bullet_surf, pure_white, white_points)
        
        # 太极圆（黑半）
        black_points = [(cx, cy)]
        for i in range(181):
            angle = (i + 180 + rotation) * math.pi / 180
            black_points.append((
                cx + int(math.cos(angle) * (size // 3)),
                cy + int(math.sin(angle) * (size // 3))
            ))
        if len(black_points) > 2:
            pygame.draw.polygon(bullet_surf, pure_black, black_points)
        
        # 小圆（S曲线）
        curve_r = size // 6
        white_curve_angle = (90 + rotation) * math.pi / 180
        black_curve_angle = (270 + rotation) * math.pi / 180
        
        # 白色S部分
        wcx = cx + int(math.cos(white_curve_angle) * curve_r)
        wcy = cy + int(math.sin(white_curve_angle) * curve_r)
        pygame.draw.circle(bullet_surf, pure_white, (wcx, wcy), curve_r)
        
        # 黑色S部分
        bcx = cx + int(math.cos(black_curve_angle) * curve_r)
        bcy = cy + int(math.sin(black_curve_angle) * curve_r)
        pygame.draw.circle(bullet_surf, pure_black, (bcx, bcy), curve_r)
        
        # 鱼眼
        pygame.draw.circle(bullet_surf, pure_white, (wcx, wcy), size // 12)
        pygame.draw.circle(bullet_surf, pure_black, (wcx, wcy), size // 24)
        pygame.draw.circle(bullet_surf, pure_black, (bcx, bcy), size // 12)
        pygame.draw.circle(bullet_surf, pure_white, (bcx, bcy), size // 24)
        
        # 旋转粒子
        for particle in range(8):
            p_angle = (particle * 45 + rotation * 1.5) * math.pi / 180
            p_r = size // 2 - 3
            px = cx + int(math.cos(p_angle) * p_r)
            py = cy + int(math.sin(p_angle) * p_r)
            p_color = pure_white if particle % 2 == 0 else pure_black
            pygame.draw.circle(bullet_surf, p_color, (px, py), 2)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "life_spark" in effects:
        # 生命火花 - DNA螺旋生命（增强版）
        life_green = (50, 200, 100)
        life_gold = (255, 215, 100)
        life_blue = (100, 180, 255)
        
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # DNA双螺旋
        for helix in range(2):
            helix_offset = helix * math.pi
            helix_color = life_green if helix == 0 else life_gold
            
            helix_pts = []
            for i in range(16):
                progress = i / 15
                angle = progress * math.pi * 3 + t * 8 + helix_offset
                hx = cx + int(math.cos(angle) * (size // 4))
                hy = cy - size // 2 + int(progress * size)
                helix_pts.append((hx, hy))
            
            if len(helix_pts) > 1:
                pygame.draw.lines(bullet_surf, helix_color, False, helix_pts, 2)
            
            # 碱基点
            for i in range(0, 16, 2):
                progress = i / 15
                angle = progress * math.pi * 3 + t * 8 + helix_offset
                hx = cx + int(math.cos(angle) * (size // 4))
                hy = cy - size // 2 + int(progress * size)
                pygame.draw.circle(bullet_surf, (255, 255, 255), (hx, hy), 2)
        
        # 碱基对连接
        for i in range(0, 16, 3):
            progress = i / 15
            angle1 = progress * math.pi * 3 + t * 8
            angle2 = angle1 + math.pi
            
            x1 = cx + int(math.cos(angle1) * (size // 4))
            y1 = cy - size // 2 + int(progress * size)
            x2 = cx + int(math.cos(angle2) * (size // 4))
            y2 = y1
            
            pygame.draw.line(bullet_surf, life_blue, (x1, y1), (x2, y2), 1)
        
        # 生命能量光环
        for ring in range(2):
            ring_r = size // 3 + ring * 5 + 2 * math.sin(t * 5 + ring)
            pygame.draw.circle(bullet_surf, (*life_green, 100 - ring * 40), (cx, cy), int(ring_r), 1)
        
        # 核心
        pygame.draw.circle(bullet_surf, life_gold, (cx, cy), size // 6)
        pygame.draw.circle(bullet_surf, life_green, (cx, cy), size // 9)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "crystal_shard" in effects:
        # 水晶碎片 - 棱镜折射（增强版）
        crystal_blue = (150, 220, 255)
        ice_white = (220, 240, 255)
        rainbow = [
            (255, 100, 100), (255, 200, 100), (255, 255, 100),
            (100, 255, 100), (100, 255, 255), (100, 100, 255), (255, 100, 255)
        ]
        
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 主晶体（八面体形）
        crystal_r = size // 3
        hex_points = []
        for i in range(8):
            angle = (i * 45 + 22.5 + t * 30) * math.pi / 180
            r = crystal_r if i % 2 == 0 else crystal_r * 0.7
            hx = cx + int(math.cos(angle) * r)
            hy = cy + int(math.sin(angle) * r)
            hex_points.append((hx, hy))
        
        pygame.draw.polygon(bullet_surf, (*crystal_blue, 180), hex_points)
        pygame.draw.polygon(bullet_surf, ice_white, hex_points, 2)
        
        # 折射面
        for i in range(4):
            angle = (i * 90 + t * 30) * math.pi / 180
            fx1 = cx + int(math.cos(angle) * (crystal_r * 0.3))
            fy1 = cy + int(math.sin(angle) * (crystal_r * 0.3))
            fx2 = cx + int(math.cos(angle) * crystal_r)
            fy2 = cy + int(math.sin(angle) * crystal_r)
            pygame.draw.line(bullet_surf, ice_white, (fx1, fy1), (fx2, fy2), 1)
        
        # 彩虹折射光
        for i, ray_color in enumerate(rainbow):
            ray_angle = (i * (360 / 7) + t * 60) * math.pi / 180
            ray_len = size // 2 + 3 * math.sin(t * 8 + i)
            rx = cx + int(math.cos(ray_angle) * ray_len)
            ry = cy + int(math.sin(ray_angle) * ray_len)
            pygame.draw.line(bullet_surf, (*ray_color, 150), (cx, cy), (rx, ry), 2)
        
        # 光点闪烁
        for sparkle in range(6):
            s_angle = (sparkle * 60 + t * 100) * math.pi / 180
            s_r = crystal_r + 3
            sx = cx + int(math.cos(s_angle) * s_r)
            sy = cy + int(math.sin(s_angle) * s_r)
            twinkle = abs(math.sin(t * 12 + sparkle)) * 3
            pygame.draw.circle(bullet_surf, (255, 255, 255), (sx, sy), int(1 + twinkle))
        
        # 核心
        pygame.draw.circle(bullet_surf, ice_white, (cx, cy), size // 8)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "chaos_burst" in effects:
        # 混沌爆发 - 多彩能量风暴（增强版）
        chaos_colors = [
            (255, 50, 50), (255, 150, 50), (255, 255, 50),
            (50, 255, 50), (50, 255, 255), (50, 50, 255), (255, 50, 255)
        ]
        
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 混沌漩涡
        for vortex in range(3):
            vortex_pts = []
            for seg in range(20):
                progress = seg / 19
                angle = (vortex * 120 + progress * 360 + t * (120 - vortex * 30)) * math.pi / 180
                r = progress * (size // 2)
                vortex_pts.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
            
            v_color = chaos_colors[(vortex + int(t * 5)) % 7]
            if len(vortex_pts) > 1:
                pygame.draw.lines(bullet_surf, v_color, False, vortex_pts, 2)
        
        # 混沌能量爆发
        for burst in range(12):
            burst_angle = (burst * 30 + t * 180) * math.pi / 180
            burst_len = size // 4 + int(6 * abs(math.sin(t * 15 + burst * 0.5)))
            bx = cx + int(math.cos(burst_angle) * burst_len)
            by = cy + int(math.sin(burst_angle) * burst_len)
            
            burst_color = chaos_colors[(burst + int(t * 8)) % 7]
            # 能量尖刺
            spike = [
                (cx + math.cos(burst_angle) * (burst_len * 0.4), cy + math.sin(burst_angle) * (burst_len * 0.4)),
                (bx + math.cos(burst_angle + 0.3) * 4, by + math.sin(burst_angle + 0.3) * 4),
                (bx, by),
                (bx + math.cos(burst_angle - 0.3) * 4, by + math.sin(burst_angle - 0.3) * 4),
            ]
            pygame.draw.polygon(bullet_surf, burst_color, spike)
        
        # 混沌核心（颜色快速变换）
        core_idx = int(t * 15) % 7
        pygame.draw.circle(bullet_surf, chaos_colors[core_idx], (cx, cy), size // 4)
        pygame.draw.circle(bullet_surf, chaos_colors[(core_idx + 3) % 7], (cx, cy), size // 6)
        pygame.draw.circle(bullet_surf, (255, 255, 255), (cx, cy), size // 10)
        
        # 混沌粒子
        for particle in range(8):
            p_angle = (particle * 45 + t * 200) * math.pi / 180
            p_r = size // 3 + 5 * math.sin(t * 10 + particle)
            px = cx + int(math.cos(p_angle) * p_r)
            py = cy + int(math.sin(p_angle) * p_r)
            pygame.draw.circle(bullet_surf, chaos_colors[(particle + int(t * 10)) % 7], (px, py), 3)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    return False


__all__ = ['render_genesis_bullet']
