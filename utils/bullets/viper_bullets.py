# -*- coding: utf-8 -*-
"""
Viper 战机子弹涂装效果渲染模块

包含以下子弹效果：
- venom_fang: 毒牙（眼镜蛇）
- acid_drop: 强酸液滴（强酸）
- biohazard_symbol: 生化危机符号（生化）
- plasma_orb: 等离子毒液球（等离子）
- hydra_heads: 九头蛇（九头蛇）
- neon_glow: 霓虹毒液（霓虹）
- serpent_eye: 蛇神之眼（蛇神）
"""
import pygame
import math


def render_viper_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Viper战机的子弹效果
    
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
    
    if "venom_fang" in effects:
        # 毒牙：尖锐三角形+滴落毒液
        # 牙齿主体（三角形）
        fang = [
            (center_x, center_y + size//2),
            (center_x - size//4, center_y - size//3),
            (center_x + size//4, center_y - size//3)
        ]
        pygame.draw.polygon(surface, (200, 200, 200), fang)
        pygame.draw.polygon(surface, color, fang, 3)
        # 毒液滴（三个小滴）
        for i in range(3):
            drop_y = center_y + size//2 + (i + 1) * size//8
            drop_x = center_x + (i - 1) * size//12
            # 泪滴形状
            pygame.draw.circle(surface, color, (drop_x, drop_y), size//12)
            pygame.draw.polygon(surface, color, [
                (drop_x, drop_y - size//12),
                (drop_x - size//20, drop_y),
                (drop_x + size//20, drop_y)
            ])
        return True
    
    elif "acid_drop" in effects:
        # 强酸液滴：滴落的酸液
        # 主液滴
        pygame.draw.circle(surface, color, (center_x, center_y), size//3)
        pygame.draw.circle(surface, (255, 255, 100), (center_x, center_y), size//5)
        # 泪滴尖端
        drop_tip = [
            (center_x, center_y + size//3),
            (center_x - size//8, center_y + size//6),
            (center_x + size//8, center_y + size//6)
        ]
        pygame.draw.polygon(surface, color, drop_tip)
        # 腐蚀轨迹（向下的小滴）
        for i in range(4):
            trail_y = center_y + size//2 + i * size//10
            trail_size = size//15 - i * 2
            if trail_size > 0:
                alpha = 200 - i * 40
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (size, int(trail_y - center_y + size)), trail_size)
                surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "biohazard_symbol" in effects:
        # 生化危机符号：三叶辐射标志
        # 中心圆
        pygame.draw.circle(surface, (0, 0, 0), (center_x, center_y), size//8)
        pygame.draw.circle(surface, color, (center_x, center_y), size//8, 2)
        # 三个扇形叶片
        for i in range(3):
            angle = (i * 120) * 3.14159 / 180
            # 外圆
            leaf_x = center_x + int(size//3 * math.cos(angle))
            leaf_y = center_y + int(size//3 * math.sin(angle))
            pygame.draw.circle(surface, color, (leaf_x, leaf_y), size//6)
            pygame.draw.circle(surface, (0, 0, 0), (leaf_x, leaf_y), size//10)
            # 连接线
            inner_x = center_x + int(size//8 * math.cos(angle))
            inner_y = center_y + int(size//8 * math.sin(angle))
            outer_x = center_x + int(size//4 * math.cos(angle))
            outer_y = center_y + int(size//4 * math.sin(angle))
            pygame.draw.line(surface, color, (inner_x, inner_y), (outer_x, outer_y), 4)
        return True
    
    elif "plasma_orb" in effects:
        # 等离子毒液球：紫色能量球+波纹
        # 多层脉冲波纹
        pulse = abs(math.sin(pygame.time.get_ticks() / 200))
        for i in range(3):
            radius = size//4 + int(i * size//8 * pulse)
            alpha = int(150 * (1 - i/3))
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (size, size), radius)
            surface.blit(temp_surf, (x - size, y - size))
        # 核心球
        pygame.draw.circle(surface, (255, 100, 255), (center_x, center_y), size//5)
        pygame.draw.circle(surface, color, (center_x, center_y), size//6)
        return True
    
    elif "hydra_heads" in effects:
        # 九头蛇：中心+多个蛇头
        # 中心身体
        pygame.draw.circle(surface, (100, 150, 50), (center_x, center_y), size//4)
        pygame.draw.circle(surface, color, (center_x, center_y), size//4, 2)
        # 5个蛇头（简化为5头）
        for i in range(5):
            angle = (i * 72 - 90) * 3.14159 / 180
            head_x = center_x + int(size//2 * math.cos(angle))
            head_y = center_y + int(size//2 * math.sin(angle))
            # 蛇头（小三角）
            head_tip = [
                (head_x + int(size//8 * math.cos(angle)), head_y + int(size//8 * math.sin(angle))),
                (head_x + int(size//12 * math.cos(angle + 0.5)), head_y + int(size//12 * math.sin(angle + 0.5))),
                (head_x + int(size//12 * math.cos(angle - 0.5)), head_y + int(size//12 * math.sin(angle - 0.5)))
            ]
            pygame.draw.polygon(surface, (150, 200, 50), head_tip)
            pygame.draw.polygon(surface, color, head_tip, 2)
            # 连接线（脖子）
            pygame.draw.line(surface, color, (center_x, center_y), (head_x, head_y), 2)
        return True
    
    elif "neon_glow" in effects:
        # 霓虹毒液：发光液滴
        # 主液滴+外发光
        for r in range(size//2, size//6, -size//12):
            alpha = int(180 * (1 - (size//2 - r) / (size//3)))
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (size, size), r)
            surface.blit(temp_surf, (x - size, y - size))
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//6)
        pygame.draw.circle(surface, color, (center_x, center_y), size//8)
        # 泪滴尖端
        tip = [
            (center_x, center_y + size//3),
            (center_x - size//10, center_y + size//8),
            (center_x + size//10, center_y + size//8)
        ]
        pygame.draw.polygon(surface, color, tip)
        return True
    
    elif "serpent_eye" in effects:
        # 蛇神之眼：竖瞳
        # 外眼轮廓
        pygame.draw.ellipse(surface, (255, 200, 0), 
                          (center_x - size//3, center_y - size//4, size*2//3, size//2))
        pygame.draw.ellipse(surface, color, 
                          (center_x - size//3, center_y - size//4, size*2//3, size//4), 3)
        # 竖瞳（细长椭圆）
        pupil_width = size // 10
        pupil_height = size // 3
        pygame.draw.ellipse(surface, (0, 0, 0), 
                          (center_x - pupil_width//2, center_y - pupil_height//2, pupil_width, pupil_height))
        # 眼神光
        pygame.draw.circle(surface, (255, 255, 200), (center_x - size//12, center_y - size//12), size//15)
        return True
    
    return False
