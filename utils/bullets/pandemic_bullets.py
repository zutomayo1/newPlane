# -*- coding: utf-8 -*-
"""
Pandemic 战机子弹涂装效果渲染模块

包含以下子弹效果：
- spike_attach/infect_spread: 刺突病毒弹
- nerve_poison/paralyze: 神经毒素弹
- fungal_growth/parasitic_burst: 真菌孢子弹
- hazard_mark/quarantine_zone: 生化标志弹
- cell_corrupt/blood_infect: 感染细胞弹
- gene_mutate/evolve_adapt: 变异株弹
- extinction_touch/omega_doom: 灭绝病原弹
"""
import pygame
import math


def render_pandemic_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Pandemic战机的子弹效果
    
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
    
    if "spike_attach" in effects or "infect_spread" in effects:
        # 刺突病毒弹：冠状病毒
        # 中心球体
        pygame.draw.circle(surface, color, (center_x, center_y), size//4)
        pygame.draw.circle(surface, (60, 235, 60), (center_x, center_y), size//5)
        # 刺突蛋白
        for i in range(12):
            angle = i * 30 * 3.14159 / 180
            x1 = center_x + int(size//4 * math.cos(angle))
            y1 = center_y + int(size//4 * math.sin(angle))
            x2 = center_x + int(size//2.5 * math.cos(angle))
            y2 = center_y + int(size//2.5 * math.sin(angle))
            pygame.draw.line(surface, (100, 200, 100), (x1, y1), (x2, y2), 2)
            # 刺突头
            pygame.draw.circle(surface, (200, 200, 80), (x2, y2), size//18)
        return True
    
    elif "nerve_poison" in effects or "paralyze" in effects:
        # 神经毒素弹：毒液滴
        # 水滴形状
        drop_points = [(center_x, int(center_y - size//2.5)), (center_x - size//4, center_y + size//8), (center_x, center_y + size//3), (center_x + size//4, center_y + size//8)]
        pygame.draw.polygon(surface, color, drop_points)
        pygame.draw.polygon(surface, (200, 100, 220), drop_points, 2)
        # 内部骷髅
        pygame.draw.circle(surface, (220, 220, 220), (center_x, center_y - size//12), size//10)
        pygame.draw.circle(surface, (50, 50, 50), (center_x - size//25, center_y - size//10), size//30)
        pygame.draw.circle(surface, (50, 50, 50), (center_x + size//25, center_y - size//10), size//30)
        return True
    
    elif "fungal_growth" in effects or "parasitic_burst" in effects:
        # 真菌孢子弹：蘑菇云
        # 蘑菇伞盖
        pygame.draw.ellipse(surface, color, (center_x - size//3, center_y - size//4, size*2//3, size//3))
        pygame.draw.ellipse(surface, (170, 120, 100), (center_x - size//3, center_y - size//4, size*2//3, size//3), 2)
        # 斑点
        for i in range(4):
            spot_x = center_x + (i - 2) * size//8
            spot_y = center_y - size//8
            pygame.draw.circle(surface, (200, 150, 120), (spot_x, spot_y), size//20)
        # 菌柄
        pygame.draw.rect(surface, (180, 140, 110), (center_x - size//12, center_y, size//6, size//3))
        # 孢子粒子
        for i in range(5):
            angle = (i * 72 + pygame.time.get_ticks() / 50) * 3.14159 / 180
            px = center_x + int(size//2.5 * math.cos(angle))
            py = center_y + int(size//2.5 * math.sin(angle))
            pygame.draw.circle(surface, (130, 80, 60), (px, py), size//25)
        return True
    
    elif "hazard_mark" in effects or "quarantine_zone" in effects:
        # 生化标志弹：生化危害符号
        # 中心圆
        pygame.draw.circle(surface, (40, 40, 40), (center_x, center_y), size//6)
        pygame.draw.circle(surface, color, (center_x, center_y), size//6, 2)
        # 三片扇叶
        for i in range(3):
            angle = i * 120 * 3.14159 / 180
            # 扇形
            arc_points = [(center_x, center_y)]
            for j in range(-30, 31, 10):
                a = angle + j * 3.14159 / 180
                px = center_x + int(size//2.5 * math.cos(a))
                py = center_y + int(size//2.5 * math.sin(a))
                arc_points.append((px, py))
            pygame.draw.polygon(surface, color, arc_points)
        # 内圈间隙
        pygame.draw.circle(surface, (40, 40, 40), (center_x, center_y), size//4)
        return True
    
    elif "cell_corrupt" in effects or "blood_infect" in effects:
        # 感染细胞弹：变异血细胞
        # 细胞轮廓（不规则椭圆）
        pygame.draw.ellipse(surface, color, (center_x - size//3, center_y - size//4, size*2//3, size//2))
        pygame.draw.ellipse(surface, (220, 100, 100), (center_x - size//3, center_y - size//4, size*2//3, size//2), 2)
        # 细胞核
        pygame.draw.circle(surface, (150, 50, 50), (center_x, center_y), size//6)
        # 变异斑点
        for i in range(3):
            spot_angle = i * 120 * 3.14159 / 180
            spot_x = center_x + int(size//6 * math.cos(spot_angle))
            spot_y = center_y + int(size//8 * math.sin(spot_angle))
            pygame.draw.circle(surface, (100, 40, 40), (spot_x, spot_y), size//15)
        return True
    
    elif "gene_mutate" in effects or "evolve_adapt" in effects:
        # 变异株弹：DNA双螺旋
        # DNA链条
        for i in range(8):
            y_pos = center_y - int(size//2.5) + i * size//6
            offset = size//6 * math.sin(i * 0.8 + pygame.time.get_ticks() / 200)
            # 左链
            pygame.draw.circle(surface, color, (int(center_x - offset), int(y_pos)), size//15)
            # 右链
            pygame.draw.circle(surface, (255, 150, 100), (int(center_x + offset), int(y_pos)), size//15)
            # 碱基对连接
            if i % 2 == 0:
                pygame.draw.line(surface, (150, 200, 150), (int(center_x - offset), int(y_pos)), (int(center_x + offset), int(y_pos)), 2)
        return True
    
    elif "extinction_touch" in effects or "omega_doom" in effects:
        # 灭绝病原弹：Ω终末病毒
        # 黑色核心
        pygame.draw.circle(surface, (10, 10, 10), (center_x, center_y), size//3)
        pygame.draw.circle(surface, (50, 0, 0), (center_x, center_y), size//3, 2)
        # Ω符号（手绘）
        omega_rect = (center_x - size//6, center_y - size//8, size//3, size//4)
        pygame.draw.arc(surface, (150, 0, 0), omega_rect, 0, 3.14159, 3)
        # 底部两脚
        pygame.draw.line(surface, (150, 0, 0), (center_x - size//6, center_y + size//10), (center_x - size//6, center_y + size//5), 3)
        pygame.draw.line(surface, (150, 0, 0), (center_x + size//6, center_y + size//10), (center_x + size//6, center_y + size//5), 3)
        # 死亡光环
        pulse = abs(math.sin(pygame.time.get_ticks() / 300))
        temp_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(temp_surf, (100, 0, 0, int(100 * pulse)), (size//2, size//2), int(size//2.5))
        surface.blit(temp_surf, (x, y))
        return True
    
    return False
