# -*- coding: utf-8 -*-
"""
Omega 战机子弹涂装效果渲染模块

包含以下子弹效果：
- omega_fusion: 七属性融合子弹（基础）
- divine_judgment: 神圣审判光束
- void_collapse: 虚空坍缩
- aurora_cascade: 极光瀑布
- celestial_strike: 天界打击
- infernal_blast: 地狱爆破
- quantum_shift: 量子位移
- primal_force: 原始神力
"""
import pygame
import math


def render_omega_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Omega战机的子弹效果
    
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
        # 七属性融合子弹 - 七芒星形态
        colors = [
            (255, 100, 100),   # 红
            (255, 200, 100),   # 橙
            (255, 255, 100),   # 黄
            (100, 255, 100),   # 绿
            (100, 200, 255),   # 青
            (100, 100, 255),   # 蓝
            (200, 100, 255),   # 紫
        ]
        
        # 七芒星
        for i in range(7):
            angle = (i * 360 / 7 + t * 100) * math.pi / 180
            outer_r = size // 2
            inner_r = size // 4
            
            ox = center_x + int(math.cos(angle) * outer_r)
            oy = center_y + int(math.sin(angle) * outer_r)
            ix = center_x + int(math.cos(angle) * inner_r)
            iy = center_y + int(math.sin(angle) * inner_r)
            
            pygame.draw.line(surface, colors[i], (ix, iy), (ox, oy), 2)
            pygame.draw.circle(surface, colors[i], (ox, oy), 3)
        
        # 中心核心
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size // 4)
        color_idx = int(t * 5) % 7
        pygame.draw.circle(surface, colors[color_idx], (center_x, center_y), size // 6)
        return True
    
    elif "void_collapse" in effects:
        # 虚空坍缩 - 黑洞吸收效果
        void_purple = (80, 0, 120)
        
        # 吸收漩涡
        for ring in range(4):
            ring_r = size // 2 - ring * (size // 10)
            rotation = -t * (100 + ring * 30)  # 逆时针旋转
            
            ring_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            for seg in range(8):
                seg_angle = (seg * 45 + rotation) * math.pi / 180
                sx = size + int(math.cos(seg_angle) * ring_r)
                sy = size + int(math.sin(seg_angle) * ring_r)
                alpha = 200 - ring * 40
                pygame.draw.circle(ring_surf, (*void_purple, alpha), (sx, sy), 2)
            surface.blit(ring_surf, (x - size // 2, y - size // 2))
        
        # 中心黑洞
        pygame.draw.circle(surface, (0, 0, 0), (center_x, center_y), size // 5)
        pygame.draw.circle(surface, (150, 50, 200), (center_x, center_y), size // 5, 2)
        return True
    
    elif "aurora_cascade" in effects:
        # 极光瀑布 - 彩虹流光
        aurora_colors = [
            (255, 100, 150), (255, 200, 100), (200, 255, 100), (100, 255, 200),
            (100, 200, 255), (150, 100, 255), (255, 100, 200)
        ]
        
        # 流动的光带
        for band in range(5):
            band_offset = (t * 200 + band * 30) % 360
            band_color = aurora_colors[band % 7]
            
            wave_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            points = []
            for px in range(0, size + 1, 5):
                py = size // 2 + int(math.sin((px + band_offset) * 0.1 + band) * (size // 6))
                points.append((px + size // 2, py + size // 2))
            
            if len(points) > 1:
                pygame.draw.lines(wave_surf, (*band_color, 150), False, points, 2)
            surface.blit(wave_surf, (x - size // 2, y - size // 2))
        
        # 中心光核
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size // 5)
        return True
    
    elif "celestial_strike" in effects:
        # 天界打击 - 蓝金神圣光芒
        celestial_blue = (80, 150, 255)
        celestial_gold = (255, 215, 100)
        
        # 光轮
        for spoke in range(12):
            spoke_angle = (spoke * 30 + t * 60) * math.pi / 180
            spoke_len = size // 2
            sx = center_x + int(math.cos(spoke_angle) * spoke_len)
            sy = center_y + int(math.sin(spoke_angle) * spoke_len)
            
            spoke_color = celestial_gold if spoke % 3 == 0 else celestial_blue
            pygame.draw.line(surface, spoke_color, (center_x, center_y), (sx, sy), 2)
        
        # 中心
        pygame.draw.circle(surface, celestial_blue, (center_x, center_y), size // 4)
        pygame.draw.circle(surface, celestial_gold, (center_x, center_y), size // 6)
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size // 10)
        return True
    
    elif "infernal_blast" in effects:
        # 地狱爆破 - 红黑火焰
        infernal_red = (255, 50, 0)
        dark_red = (150, 0, 0)
        
        # 火焰
        for flame in range(8):
            flame_angle = (flame * 45 + t * 80) * math.pi / 180
            flame_len = size // 2 + int(abs(math.sin(t * 8 + flame)) * (size // 6))
            fx = center_x + int(math.cos(flame_angle) * flame_len)
            fy = center_y + int(math.sin(flame_angle) * flame_len)
            
            pygame.draw.line(surface, infernal_red, (center_x, center_y), (fx, fy), 3)
            pygame.draw.circle(surface, (255, 200, 50), (fx, fy), 3)
        
        # 核心
        pygame.draw.circle(surface, dark_red, (center_x, center_y), size // 4)
        pygame.draw.circle(surface, infernal_red, (center_x, center_y), size // 6)
        return True
    
    elif "quantum_shift" in effects:
        # 量子位移 - 青蓝科技粒子
        quantum_cyan = (0, 255, 255)
        
        # 量子轨道
        for orbit in range(3):
            orbit_r = size // 4 + orbit * (size // 8)
            orbit_rot = t * (100 - orbit * 20)
            
            pygame.draw.circle(surface, quantum_cyan, (center_x, center_y), orbit_r, 1)
            
            for electron in range(2):
                e_angle = (orbit_rot + electron * 180) * math.pi / 180
                ex = center_x + int(math.cos(e_angle) * orbit_r)
                ey = center_y + int(math.sin(e_angle) * orbit_r)
                pygame.draw.circle(surface, quantum_cyan, (ex, ey), 3)
        
        # 中心
        pygame.draw.circle(surface, (0, 150, 255), (center_x, center_y), size // 6)
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size // 10)
        return True
    
    elif "primal_force" in effects:
        # 原始神力 - 自然能量
        primal_green = (50, 200, 80)
        gold = (255, 215, 0)
        
        # 叶片/能量
        for leaf in range(6):
            leaf_angle = (leaf * 60 + t * 40) * math.pi / 180
            leaf_len = size // 2
            lx = center_x + int(math.cos(leaf_angle) * leaf_len)
            ly = center_y + int(math.sin(leaf_angle) * leaf_len)
            
            leaf_color = primal_green if leaf % 2 == 0 else gold
            pygame.draw.line(surface, leaf_color, (center_x, center_y), (lx, ly), 2)
            pygame.draw.circle(surface, leaf_color, (lx, ly), 3)
        
        # 中心
        pygame.draw.circle(surface, gold, (center_x, center_y), size // 5)
        pygame.draw.circle(surface, primal_green, (center_x, center_y), size // 8)
        return True
    
    return False


__all__ = ['render_omega_bullet']
