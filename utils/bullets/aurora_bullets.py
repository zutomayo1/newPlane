# -*- coding: utf-8 -*-
"""
Aurora 战机子弹涂装效果渲染模块

包含以下子弹效果：
- goddess_aura: 女神光辉（女神）
- holy_rings: 圣洁光环（星云）
- nebula_swirl: 星云漩涡（冰雪女王替代）
- star_sparkle: 星辰闪烁（彩虹）
- ice_crown: 冰雪王冠（棱镜）
- frost_spikes: 冰霜尖刺
- rainbow_beam: 彩虹光束（樱花）
- chromatic_shift: 彩虹折射
- prism_split: 棱镜折射
- light_refract: 光线折射
- sakura_petal: 樱花飞舞
- petal_spin: 樱花旋转
- celestial_ring: 天界光环（天界）
- divine_blessing: 神圣祝福
"""
import pygame
import math
import random


def render_aurora_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Aurora战机的子弹效果
    
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
    
    if "goddess_aura" in effects:
        # 女神光辉：神圣光环+光晕
        # 中心神圣核心
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//6)
        pygame.draw.circle(surface, color, (center_x, center_y), size//8)
        # 神圣光环（3层）
        for i in range(3):
            ring_radius = size//4 + i * size//8
            alpha = 200 - i * 50
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (size, size), ring_radius, 3)
            surface.blit(temp_surf, (x - size, y - size))
        # 光晕粒子
        for i in range(8):
            angle = (i * 45 + pygame.time.get_ticks() / 30) * 3.14159 / 180
            px = center_x + int(size//2.5 * math.cos(angle))
            py = center_y + int(size//2.5 * math.sin(angle))
            pygame.draw.circle(surface, (255, 255, 220), (px, py), size//20)
        return True
    
    elif "holy_rings" in effects:
        # 圣洁光环：多层旋转光环
        # 中心
        pygame.draw.circle(surface, (255, 255, 240), (center_x, center_y), size//8)
        # 旋转光环
        for i in range(4):
            angle_offset = (i * 90 + pygame.time.get_ticks() / 20) * 3.14159 / 180
            ring_radius = size//3 + i * size//12
            # 绘制弧形光环
            arc_points = []
            for a in range(0, 180, 10):
                rad = (a + angle_offset) * 3.14159 / 180
                px = center_x + int(ring_radius * math.cos(rad))
                py = center_y + int(ring_radius * math.sin(rad))
                arc_points.append((px, py))
            if len(arc_points) > 1:
                pygame.draw.lines(surface, color, False, arc_points, 2)
        return True
    
    elif "nebula_swirl" in effects:
        # 星云漩涡：旋转星云
        # 星云中心
        pygame.draw.circle(surface, (200, 150, 255), (center_x, center_y), size//6)
        # 漩涡臂
        for arm in range(3):
            arm_points = []
            arm_offset = arm * 120
            for i in range(15):
                angle = (i * 24 + arm_offset + pygame.time.get_ticks() / 50) * 3.14159 / 180
                radius = size//8 + i * size//30
                px = center_x + int(radius * math.cos(angle))
                py = center_y + int(radius * math.sin(angle))
                arm_points.append((px, py))
            if len(arm_points) > 1:
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.lines(temp_surf, (*color, 180), False, 
                                [(px - center_x + size, py - center_y + size) for px, py in arm_points], 3)
                surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "star_sparkle" in effects:
        # 星辰闪烁：闪烁星点
        # 主星
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//6)
        pygame.draw.circle(surface, color, (center_x, center_y), size//8)
        # 十字星芒
        for angle in [0, 90, 180, 270]:
            rad = angle * 3.14159 / 180
            x1 = center_x + int(size//8 * math.cos(rad))
            y1 = center_y + int(size//8 * math.sin(rad))
            x2 = center_x + int(size//2 * math.cos(rad))
            y2 = center_y + int(size//2 * math.sin(rad))
            pygame.draw.line(surface, (255, 255, 255), (x1, y1), (x2, y2), 3)
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), 1)
        # 闪烁小星
        random.seed(int(pygame.time.get_ticks() / 200))
        for _ in range(6):
            sx = center_x + random.randint(-size//2, size//2)
            sy = center_y + random.randint(-size//2, size//2)
            star_size = random.randint(1, 3)
            pygame.draw.circle(surface, (255, 255, 255), (sx, sy), star_size)
        return True
    
    elif "ice_crown" in effects:
        # 冰雪王冠：冰晶王冠形状
        # 王冠底部（圆环）
        pygame.draw.circle(surface, color, (center_x, center_y), size//3, 3)
        # 冰晶尖刺（6个）
        for i in range(6):
            angle = (i * 60) * 3.14159 / 180
            base_x = center_x + int(size//3 * math.cos(angle))
            base_y = center_y + int(size//3 * math.sin(angle))
            tip_x = center_x + int(size//2 * math.cos(angle))
            tip_y = center_y + int(size//2 * math.sin(angle))
            # 冰锥三角
            ice_spike = [
                (tip_x, tip_y),
                (base_x + int(size//15 * math.cos(angle + 1.5708)), base_y + int(size//15 * math.sin(angle + 1.5708))),
                (base_x - int(size//15 * math.cos(angle + 1.5708)), base_y - int(size//15 * math.sin(angle + 1.5708)))
            ]
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.polygon(temp_surf, (*color, 200), 
                              [(px - center_x + size, py - center_y + size) for px, py in ice_spike])
            surface.blit(temp_surf, (x - size, y - size))
            pygame.draw.polygon(surface, (255, 255, 255), ice_spike, 2)
        return True
    
    elif "frost_spikes" in effects:
        # 冰霜尖刺：多根冰刺
        # 中心冰核
        pygame.draw.circle(surface, (230, 245, 255), (center_x, center_y), size//8)
        # 冰刺（8根）
        for i in range(8):
            angle = (i * 45) * 3.14159 / 180
            spike_length = size//2 + (i % 2) * size//8
            x1 = center_x + int(size//8 * math.cos(angle))
            y1 = center_y + int(size//8 * math.sin(angle))
            x2 = center_x + int(spike_length * math.cos(angle))
            y2 = center_y + int(spike_length * math.sin(angle))
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), 4)
            pygame.draw.line(surface, (255, 255, 255), (x1, y1), (x2, y2), 1)
        return True
    
    elif "rainbow_beam" in effects:
        # 彩虹光束：七彩射线
        # 彩虹颜色
        rainbow_colors = [
            (255, 0, 0), (255, 127, 0), (255, 255, 0),
            (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)
        ]
        # 射线束
        for i, rainbow_color in enumerate(rainbow_colors):
            angle = (i * 360 / 7) * 3.14159 / 180
            x1 = center_x + int(size//6 * math.cos(angle))
            y1 = center_y + int(size//6 * math.sin(angle))
            x2 = center_x + int(size//2 * math.cos(angle))
            y2 = center_y + int(size//2 * math.sin(angle))
            pygame.draw.line(surface, rainbow_color, (x1, y1), (x2, y2), 3)
        # 中心白光
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//6)
        return True
    
    elif "chromatic_shift" in effects:
        # 彩虹折射：色彩变换
        # 主体（圆形）
        for i in range(7):
            rainbow_color = [
                (255, 0, 0), (255, 127, 0), (255, 255, 0),
                (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)
            ][i]
            offset = i * 3
            alpha = 200 - i * 20
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*rainbow_color, alpha), (size + offset, size), size//4)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "prism_split" in effects:
        # 棱镜折射：菱形棱镜+折射光
        # 棱镜主体（菱形）
        prism = [
            (center_x, center_y - size//2),
            (center_x + size//3, center_y),
            (center_x, center_y + size//2),
            (center_x - size//3, center_y)
        ]
        temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.polygon(temp_surf, (*color, 180), 
                          [(px - center_x + size, py - center_y + size) for px, py in prism])
        surface.blit(temp_surf, (x - size, y - size))
        pygame.draw.polygon(surface, (255, 255, 255), prism, 2)
        # 折射光线
        for i in range(3):
            angle = (30 + i * 30) * 3.14159 / 180
            x1 = center_x + int(size//3 * math.cos(angle))
            y1 = center_y + int(size//3 * math.sin(angle))
            x2 = center_x + int(size//2 * math.cos(angle + 0.3))
            y2 = center_y + int(size//2 * math.sin(angle + 0.3))
            refract_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            pygame.draw.line(surface, refract_colors[i], (x1, y1), (x2, y2), 2)
        return True
    
    elif "light_refract" in effects:
        # 光线折射：多条折射光
        # 中心光源
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//8)
        # 折射光线（8条）
        colors_cycle = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        for i in range(8):
            angle = (i * 45) * 3.14159 / 180
            # 第一段
            x1 = center_x + int(size//8 * math.cos(angle))
            y1 = center_y + int(size//8 * math.sin(angle))
            x2 = center_x + int(size//3 * math.cos(angle))
            y2 = center_y + int(size//3 * math.sin(angle))
            # 第二段（折射）
            angle2 = angle + 0.4
            x3 = x2 + int(size//4 * math.cos(angle2))
            y3 = y2 + int(size//4 * math.sin(angle2))
            line_color = colors_cycle[i % 4]
            pygame.draw.line(surface, line_color, (x1, y1), (x2, y2), 2)
            pygame.draw.line(surface, line_color, (x2, y2), (x3, y3), 2)
        return True
    
    elif "sakura_petal" in effects:
        # 樱花飞舞：樱花花瓣形状
        # 花瓣（5瓣）
        for i in range(5):
            angle = (i * 72 + pygame.time.get_ticks() / 50) * 3.14159 / 180
            # 花瓣形状（椭圆）
            petal_x = center_x + int(size//4 * math.cos(angle))
            petal_y = center_y + int(size//4 * math.sin(angle))
            petal_width = size // 5
            petal_height = size // 3
            # 旋转的椭圆
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            petal_rect = pygame.Rect(0, 0, petal_width, petal_height)
            petal_rect.center = (size + int(size//4 * math.cos(angle)), 
                                size + int(size//4 * math.sin(angle)))
            pygame.draw.ellipse(temp_surf, (*color, 200), petal_rect)
            pygame.draw.ellipse(temp_surf, (255, 180, 200), petal_rect, 1)
            surface.blit(temp_surf, (x - size, y - size))
        # 花心
        pygame.draw.circle(surface, (255, 200, 220), (center_x, center_y), size//10)
        return True
    
    elif "petal_spin" in effects:
        # 樱花旋转：旋转花瓣
        # 螺旋飘落的花瓣
        for i in range(4):
            angle = (i * 90 + pygame.time.get_ticks() / 30) * 3.14159 / 180
            radius = size//3 + (i % 2) * size//8
            px = center_x + int(radius * math.cos(angle))
            py = center_y + int(radius * math.sin(angle))
            # 单个花瓣（泪滴形）
            petal = [
                (px, py - size//12),
                (px + size//20, py),
                (px, py + size//10),
                (px - size//20, py)
            ]
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.polygon(temp_surf, (*color, 220), 
                              [(px - center_x + size, py - center_y + size) for px, py in petal])
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "celestial_ring" in effects:
        # 天界光环：天使光环
        # 主光环
        pygame.draw.circle(surface, (255, 250, 240), (center_x, center_y - size//4), size//2, 4)
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y - size//4), size//2, 2)
        # 身体（简化的人形光芒）
        pygame.draw.circle(surface, color, (center_x, center_y + size//8), size//6)
        # 光芒射线
        for i in range(8):
            angle = (i * 45) * 3.14159 / 180
            x1 = center_x + int(size//6 * math.cos(angle))
            y1 = center_y + size//8 + int(size//6 * math.sin(angle))
            x2 = center_x + int(size//2.5 * math.cos(angle))
            y2 = center_y + size//8 + int(size//2.5 * math.sin(angle))
            pygame.draw.line(surface, (255, 250, 220), (x1, y1), (x2, y2), 2)
        return True
    
    elif "divine_blessing" in effects:
        # 神圣祝福：十字光芒+圣光
        # 十字光芒
        pygame.draw.line(surface, (255, 255, 240), 
                       (center_x, center_y - size//2), 
                       (center_x, center_y + size//2), 5)
        pygame.draw.line(surface, (255, 255, 240), 
                       (center_x - size//2, center_y), 
                       (center_x + size//2, center_y), 5)
        pygame.draw.line(surface, color, 
                       (center_x, center_y - size//2), 
                       (center_x, center_y + size//2), 2)
        pygame.draw.line(surface, color, 
                       (center_x - size//2, center_y), 
                       (center_x + size//2, center_y), 2)
        # 中心光核
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//6)
        pygame.draw.circle(surface, color, (center_x, center_y), size//8)
        # 外圈圣光
        for i in range(4):
            alpha = 150 - i * 30
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (size, size), size//4 + i * size//12, 2)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    return False
