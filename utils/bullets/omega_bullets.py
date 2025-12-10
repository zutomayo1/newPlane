# -*- coding: utf-8 -*-
"""
Omega 战机子弹涂装效果渲染模块 - 终极机体专属

包含以下子弹效果：
- omega_fusion: 七属性融合子弹（基础） - 七芒星轮转
- divine_judgment: 神圣审判光束 - 金白圣光十字
- void_collapse: 虚空坍缩 - 黑洞吸收扭曲
- aurora_cascade: 极光瀑布 - 彩虹流光波动
- celestial_strike: 天界打击 - 蓝金光轮
- infernal_blast: 地狱爆破 - 红黑烈焰
- quantum_shift: 量子位移 - 电子轨道
- primal_force: 原始神力 - 自然能量脉动
"""
import pygame
import math


def render_omega_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Omega战机的子弹效果 - 终极机体级别特效
    
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
    
    if "omega_fusion" in effects or "divine_judgment" in effects:
        # 七属性融合子弹 - 终极七芒星形态
        colors = [
            (255, 80, 30),    # 炎红
            (100, 200, 255),  # 冰蓝
            (255, 255, 100),  # 雷黄
            (150, 255, 80),   # 毒绿
            (255, 255, 255),  # 圣白
            (150, 50, 200),   # 暗紫
            (255, 200, 100),  # 元金
        ]
        
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 外层七芒星光环（脉动）
        pulse = abs(math.sin(t * 5)) * 3
        for i in range(7):
            angle1 = (i * 360 / 7 + t * 80) * math.pi / 180
            angle2 = ((i + 3) * 360 / 7 + t * 80) * math.pi / 180
            outer_r = size // 2 + pulse
            
            x1 = cx + int(math.cos(angle1) * outer_r)
            y1 = cy + int(math.sin(angle1) * outer_r)
            x2 = cx + int(math.cos(angle2) * outer_r)
            y2 = cy + int(math.sin(angle2) * outer_r)
            
            # 七芒星连线
            pygame.draw.line(bullet_surf, colors[i], (x1, y1), (x2, y2), 2)
            
            # 顶点光球
            pygame.draw.circle(bullet_surf, colors[i], (x1, y1), 4)
            pygame.draw.circle(bullet_surf, (255, 255, 255), (x1, y1), 2)
        
        # 中层旋转三角阵
        for layer in range(2):
            for i in range(3):
                angle = (i * 120 + layer * 60 + t * (120 if layer == 0 else -90)) * math.pi / 180
                tri_r = size // 3 - layer * 4
                tx = cx + int(math.cos(angle) * tri_r)
                ty = cy + int(math.sin(angle) * tri_r)
                tri_color = colors[(int(t * 5) + i + layer * 3) % 7]
                # 小三角形
                tri_pts = []
                for j in range(3):
                    ta = angle + j * 2.094  # 120度
                    tri_pts.append((tx + math.cos(ta) * 4, ty + math.sin(ta) * 4))
                pygame.draw.polygon(bullet_surf, tri_color, tri_pts)
        
        # 核心：七色轮转
        core_idx = int(t * 7) % 7
        pygame.draw.circle(bullet_surf, (255, 255, 255), (cx, cy), size // 4 + 2)
        pygame.draw.circle(bullet_surf, colors[core_idx], (cx, cy), size // 4)
        pygame.draw.circle(bullet_surf, colors[(core_idx + 1) % 7], (cx, cy), size // 6)
        
        # 能量光晕
        glow_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        glow_r = size // 2 + int(pulse * 2)
        pygame.draw.circle(glow_surf, (255, 220, 180, 60), (cx, cy), glow_r)
        bullet_surf.blit(glow_surf, (0, 0))
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "void_collapse" in effects:
        # 虚空坍缩 - 黑洞吸收效果（增强版）
        void_purple = (100, 0, 150)
        void_black = (20, 0, 30)
        
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 扭曲空间（螺旋吸收线）
        for spiral in range(4):
            spiral_pts = []
            for seg in range(20):
                progress = seg / 19
                angle = (spiral * 90 - t * 150 + progress * 360) * math.pi / 180
                r = (1 - progress) * (size // 2)
                sx = cx + int(math.cos(angle) * r)
                sy = cy + int(math.sin(angle) * r)
                spiral_pts.append((sx, sy))
            if len(spiral_pts) > 1:
                alpha = 180
                color = (*void_purple, alpha)
                pygame.draw.lines(bullet_surf, color, False, spiral_pts, 2)
        
        # 事件视界（多层环）
        for ring in range(5):
            ring_r = size // 2 - ring * (size // 12)
            rotation = -t * (100 + ring * 40)
            alpha = 200 - ring * 35
            
            pts = []
            for i in range(16):
                a = (i * 22.5 + rotation) * math.pi / 180
                wobble = 2 * math.sin(t * 8 + i + ring)
                r = ring_r + wobble
                pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
            pygame.draw.polygon(bullet_surf, (*void_purple, alpha), pts, 2)
        
        # 吸收粒子
        for particle in range(8):
            p_angle = (particle * 45 + t * 200) * math.pi / 180
            p_r = size // 3 + 5 * math.sin(t * 10 + particle)
            px = cx + int(math.cos(p_angle) * p_r)
            py = cy + int(math.sin(p_angle) * p_r)
            pygame.draw.circle(bullet_surf, (200, 100, 255), (px, py), 2)
        
        # 中心黑洞
        pygame.draw.circle(bullet_surf, void_black, (cx, cy), size // 5 + 2)
        pygame.draw.circle(bullet_surf, (0, 0, 0), (cx, cy), size // 5)
        # 奇点光芒
        for ray in range(6):
            ray_angle = (ray * 60 + t * 50) * math.pi / 180
            rx = cx + math.cos(ray_angle) * (size // 5 + 3)
            ry = cy + math.sin(ray_angle) * (size // 5 + 3)
            pygame.draw.line(bullet_surf, (150, 50, 200), (cx, cy), (rx, ry), 1)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "aurora_cascade" in effects:
        # 极光瀑布 - 彩虹流光（增强版）
        aurora_colors = [
            (255, 100, 150), (255, 200, 100), (200, 255, 100), (100, 255, 200),
            (100, 200, 255), (150, 100, 255), (255, 100, 200)
        ]
        
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 极光波纹层
        for layer in range(5):
            wave_pts = []
            layer_offset = t * 200 + layer * 40
            for i in range(24):
                angle = (i * 15) * math.pi / 180
                wave = 4 * math.sin(i * 0.5 + layer_offset * 0.05 + layer)
                r = size // 2 - layer * 3 + wave
                wave_pts.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
            color = aurora_colors[layer % 7]
            alpha = 180 - layer * 30
            pygame.draw.polygon(bullet_surf, (*color, alpha), wave_pts)
        
        # 流动光带
        for band in range(4):
            band_offset = (t * 300 + band * 50) % 360
            band_color = aurora_colors[(band + int(t * 3)) % 7]
            
            band_pts = []
            for seg in range(12):
                progress = seg / 11
                angle = (band_offset + progress * 120) * math.pi / 180
                r = size // 3 + 5 * math.sin(progress * 6.28 + t * 5)
                band_pts.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
            if len(band_pts) > 1:
                pygame.draw.lines(bullet_surf, band_color, False, band_pts, 3)
        
        # 核心光球
        core_color = aurora_colors[int(t * 5) % 7]
        pygame.draw.circle(bullet_surf, (255, 255, 255), (cx, cy), size // 4)
        pygame.draw.circle(bullet_surf, core_color, (cx, cy), size // 5)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "celestial_strike" in effects:
        # 天界打击 - 蓝金神圣光芒（增强版）
        celestial_blue = (80, 150, 255)
        celestial_gold = (255, 215, 100)
        
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 双层光轮
        for layer in range(2):
            for spoke in range(12):
                spoke_angle = (spoke * 30 + t * (80 if layer == 0 else -60) + layer * 15) * math.pi / 180
                spoke_len = size // 2 - layer * 5
                sx = cx + int(math.cos(spoke_angle) * spoke_len)
                sy = cy + int(math.sin(spoke_angle) * spoke_len)
                
                spoke_color = celestial_gold if (spoke + layer) % 3 == 0 else celestial_blue
                # 光束渐变
                for w in range(3, 0, -1):
                    alpha = 100 + (3 - w) * 50
                    pygame.draw.line(bullet_surf, (*spoke_color, alpha), (cx, cy), (sx, sy), w)
                
                # 顶点星光
                if spoke % 2 == 0:
                    star_pts = [(sx, sy - 3), (sx + 2, sy), (sx, sy + 3), (sx - 2, sy)]
                    pygame.draw.polygon(bullet_surf, (255, 255, 255), star_pts)
        
        # 神圣符文环
        rune_r = size // 3
        for rune in range(6):
            rune_angle = (rune * 60 + t * 40) * math.pi / 180
            rx = cx + int(math.cos(rune_angle) * rune_r)
            ry = cy + int(math.sin(rune_angle) * rune_r)
            # 简单符文形状
            pygame.draw.circle(bullet_surf, celestial_gold, (rx, ry), 4, 1)
            pygame.draw.line(bullet_surf, celestial_gold, (rx - 2, ry - 2), (rx + 2, ry + 2), 1)
        
        # 多层核心
        pygame.draw.circle(bullet_surf, celestial_blue, (cx, cy), size // 4 + 2)
        pygame.draw.circle(bullet_surf, celestial_gold, (cx, cy), size // 4)
        pygame.draw.circle(bullet_surf, (255, 255, 255), (cx, cy), size // 6)
        
        # 十字圣光
        cross_len = size // 3 + 3 * abs(math.sin(t * 6))
        for i in range(4):
            angle = (i * 90 + 45) * math.pi / 180
            ex = cx + math.cos(angle) * cross_len
            ey = cy + math.sin(angle) * cross_len
            pygame.draw.line(bullet_surf, (255, 255, 255, 200), (cx, cy), (ex, ey), 2)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "infernal_blast" in effects:
        # 地狱爆破 - 红黑火焰（增强版）
        infernal_red = (255, 50, 0)
        infernal_orange = (255, 150, 50)
        dark_red = (150, 0, 0)
        
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 地狱火焰旋涡
        for flame_ring in range(3):
            for flame in range(8):
                flame_angle = (flame * 45 + t * (100 - flame_ring * 20) + flame_ring * 20) * math.pi / 180
                flame_len = size // 2 - flame_ring * 4 + int(5 * abs(math.sin(t * 8 + flame + flame_ring)))
                
                # 火焰三角
                fx = cx + int(math.cos(flame_angle) * flame_len)
                fy = cy + int(math.sin(flame_angle) * flame_len)
                
                base_l = (cx + math.cos(flame_angle + 0.3) * (flame_len * 0.3),
                         cy + math.sin(flame_angle + 0.3) * (flame_len * 0.3))
                base_r = (cx + math.cos(flame_angle - 0.3) * (flame_len * 0.3),
                         cy + math.sin(flame_angle - 0.3) * (flame_len * 0.3))
                
                colors = [infernal_red, infernal_orange, (255, 200, 50)]
                flame_color = colors[(flame + flame_ring) % 3]
                pygame.draw.polygon(bullet_surf, flame_color, [base_l, (fx, fy), base_r])
        
        # 裂痕效果
        for crack in range(6):
            crack_angle = (crack * 60 + t * 30) * math.pi / 180
            crack_pts = [(cx, cy)]
            for seg in range(4):
                wobble = 3 * math.sin(t * 10 + crack + seg)
                r = (seg + 1) * (size // 8) + wobble
                crack_pts.append((cx + math.cos(crack_angle + wobble * 0.1) * r,
                                cy + math.sin(crack_angle + wobble * 0.1) * r))
            pygame.draw.lines(bullet_surf, (255, 100, 0), False, crack_pts, 2)
        
        # 核心熔岩
        pygame.draw.circle(bullet_surf, dark_red, (cx, cy), size // 4 + 2)
        pygame.draw.circle(bullet_surf, infernal_red, (cx, cy), size // 4)
        pygame.draw.circle(bullet_surf, infernal_orange, (cx, cy), size // 6)
        pygame.draw.circle(bullet_surf, (255, 255, 100), (cx, cy), size // 10)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "quantum_shift" in effects:
        # 量子位移 - 电子轨道（增强版）
        quantum_cyan = (0, 255, 255)
        quantum_blue = (50, 150, 255)
        
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 多层量子轨道
        for orbit in range(4):
            orbit_r = size // 5 + orbit * (size // 8)
            orbit_rot = t * (150 - orbit * 25) * (1 if orbit % 2 == 0 else -1)
            
            # 椭圆轨道
            orbit_pts = []
            for i in range(36):
                angle = i * 10 * math.pi / 180
                rx = orbit_r
                ry = orbit_r * (0.4 + orbit * 0.15)
                rot = (orbit * 30 + orbit_rot) * math.pi / 180
                # 旋转椭圆
                px = rx * math.cos(angle)
                py = ry * math.sin(angle)
                rotated_x = px * math.cos(rot) - py * math.sin(rot)
                rotated_y = px * math.sin(rot) + py * math.cos(rot)
                orbit_pts.append((cx + rotated_x, cy + rotated_y))
            
            alpha = 150 - orbit * 30
            pygame.draw.polygon(bullet_surf, (*quantum_cyan, alpha), orbit_pts, 1)
            
            # 电子
            for electron in range(2):
                e_angle = (orbit_rot * 2 + electron * 180) * math.pi / 180
                rx = orbit_r
                ry = orbit_r * (0.4 + orbit * 0.15)
                rot = (orbit * 30 + orbit_rot) * math.pi / 180
                px = rx * math.cos(e_angle)
                py = ry * math.sin(e_angle)
                ex = cx + px * math.cos(rot) - py * math.sin(rot)
                ey = cy + px * math.sin(rot) + py * math.cos(rot)
                pygame.draw.circle(bullet_surf, quantum_cyan, (int(ex), int(ey)), 3)
                pygame.draw.circle(bullet_surf, (255, 255, 255), (int(ex), int(ey)), 1)
        
        # 量子波动
        wave_r = size // 2 + 3 * math.sin(t * 10)
        pygame.draw.circle(bullet_surf, (*quantum_blue, 80), (cx, cy), int(wave_r), 2)
        
        # 核心
        pygame.draw.circle(bullet_surf, quantum_blue, (cx, cy), size // 5)
        pygame.draw.circle(bullet_surf, quantum_cyan, (cx, cy), size // 7)
        pygame.draw.circle(bullet_surf, (255, 255, 255), (cx, cy), size // 10)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "primal_force" in effects:
        # 原始神力 - 自然能量（增强版）
        primal_green = (50, 200, 80)
        primal_gold = (255, 215, 0)
        earth_brown = (139, 90, 43)
        
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 自然元素环绕
        elements = [
            (primal_green, "leaf"),
            (100, 180, 255),  # water
            (earth_brown, "earth"),
            (255, 200, 100),  # light
        ]
        
        for i in range(8):
            angle = (i * 45 + t * 50) * math.pi / 180
            elem_r = size // 2 - 2
            ex = cx + int(math.cos(angle) * elem_r)
            ey = cy + int(math.sin(angle) * elem_r)
            
            if i % 2 == 0:
                # 叶片形状
                leaf_angle = angle + math.pi / 2
                leaf_pts = [
                    (ex, ey),
                    (ex + math.cos(leaf_angle + 0.3) * 6, ey + math.sin(leaf_angle + 0.3) * 6),
                    (ex + math.cos(angle) * 8, ey + math.sin(angle) * 8),
                    (ex + math.cos(leaf_angle - 0.3) * 6, ey + math.sin(leaf_angle - 0.3) * 6),
                ]
                pygame.draw.polygon(bullet_surf, primal_green, leaf_pts)
            else:
                # 能量球
                pygame.draw.circle(bullet_surf, primal_gold, (ex, ey), 4)
                pygame.draw.circle(bullet_surf, (255, 255, 200), (ex, ey), 2)
        
        # 生命脉动环
        for ring in range(3):
            ring_r = size // 4 + ring * 5 + 2 * math.sin(t * 6 + ring)
            alpha = 180 - ring * 50
            pygame.draw.circle(bullet_surf, (*primal_green, alpha), (cx, cy), int(ring_r), 2)
        
        # 核心生命力
        pygame.draw.circle(bullet_surf, earth_brown, (cx, cy), size // 4)
        pygame.draw.circle(bullet_surf, primal_green, (cx, cy), size // 5)
        pygame.draw.circle(bullet_surf, primal_gold, (cx, cy), size // 8)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    return False


__all__ = ['render_omega_bullet']
