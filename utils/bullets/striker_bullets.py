# Striker 子弹涂装渲染
import pygame
import math

def render_striker_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """渲染Striker子弹效果，返回True表示已处理"""
    
    if "gear_rotate" in effects:
        # 机械齿轮：六边形齿轮+旋转齿
        rotation = pygame.time.get_ticks() / 500
        # 绘制六边形主体
        points = []
        for i in range(6):
            angle = (i * 60 + rotation * 50) * 3.14159 / 180
            px = center_x + int(size//3 * math.cos(angle))
            py = center_y + int(size//3 * math.sin(angle))
            points.append((px, py))
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (255, 255, 255), points, 2)
        # 绘制齿轮齿
        for i in range(6):
            angle = (i * 60 + rotation * 50) * 3.14159 / 180
            x1 = center_x + int(size//3 * math.cos(angle))
            y1 = center_y + int(size//3 * math.sin(angle))
            x2 = center_x + int(size//2.2 * math.cos(angle))
            y2 = center_y + int(size//2.2 * math.sin(angle))
            pygame.draw.line(surface, (200, 200, 200), (x1, y1), (x2, y2), 3)
        return True
    
    elif "phase_flicker" in effects:
        # 幽灵：波浪形半透明体
        alpha_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        alpha = int(128 + 64 * math.sin(pygame.time.get_ticks() / 200))
        # 绘制波浪形状
        points = []
        for i in range(8):
            angle = (i * 45) * 3.14159 / 180
            radius = size//3 + size//8 * math.sin(i + pygame.time.get_ticks() / 100)
            px = size//2 + int(radius * math.cos(angle))
            py = size//2 + int(radius * math.sin(angle))
            points.append((px, py))
        pygame.draw.polygon(alpha_surf, (*color, alpha), points)
        surface.blit(alpha_surf, (x, y))
        return True
    
    elif "lava_crack" in effects:
        # 反应堆：裂开的方形+内部能量核心
        fragments = [
            [(center_x-size//3, center_y-size//3), (center_x, center_y-size//2.5), (center_x-size//6, center_y-size//6)],
            [(center_x, center_y-size//2.5), (center_x+size//3, center_y-size//3), (center_x+size//6, center_y-size//6)],
            [(center_x+size//3, center_y-size//3), (center_x+size//2.5, center_y), (center_x+size//6, center_y+size//6)],
            [(center_x+size//2.5, center_y), (center_x+size//3, center_y+size//3), (center_x+size//6, center_y+size//6)]
        ]
        for frag in fragments:
            pygame.draw.polygon(surface, (100, 50, 50), frag)
            pygame.draw.polygon(surface, (255, 200, 0), frag, 2)
        pygame.draw.circle(surface, (255, 255, 0), (center_x, center_y), size//6)
        pygame.draw.circle(surface, color, (center_x, center_y), size//8)
        return True
    
    elif "quantum_shift" in effects:
        # 量子：三个菱形叠加
        offset = int(size//6 * math.sin(pygame.time.get_ticks() / 300))
        for i, dx in [(-offset, 180), (0, 255), (offset, 180)]:
            temp_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            diamond = [
                (size//2 + dx, size//2 - size//4),
                (size//2 + dx + size//4, size//2),
                (size//2 + dx, size//2 + size//4),
                (size//2 + dx - size//4, size//2)
            ]
            pygame.draw.polygon(temp_surf, (*color, dx), diamond)
            surface.blit(temp_surf, (x, y))
        return True
    
    elif "holy_ray" in effects:
        # 圣光：八芒星形
        for rotation in [0, 45]:
            points = []
            for i in range(4):
                angle = (i * 90 + rotation) * 3.14159 / 180
                px = center_x + int(size//2.8 * math.cos(angle))
                py = center_y + int(size//2.8 * math.sin(angle))
                points.append((px, py))
            pygame.draw.polygon(surface, color, points)
        pygame.draw.circle(surface, (255, 255, 220), (center_x, center_y), size//6)
        return True
    
    elif "dragon_breath" in effects:
        # 龙息：尖刺球体+向后喷射火焰
        pygame.draw.circle(surface, color, (center_x, center_y), size//4)
        for i in range(6):
            angle = (i * 60) * 3.14159 / 180
            x1 = center_x + int(size//4 * math.cos(angle))
            y1 = center_y + int(size//4 * math.sin(angle))
            x2 = center_x + int(size//2.2 * math.cos(angle))
            y2 = center_y + int(size//2.2 * math.sin(angle))
            angle_left = (angle - 0.3)
            angle_right = (angle + 0.3)
            px1 = center_x + int(size//4 * math.cos(angle_left))
            py1 = center_y + int(size//4 * math.sin(angle_left))
            px2 = center_x + int(size//4 * math.cos(angle_right))
            py2 = center_y + int(size//4 * math.sin(angle_right))
            pygame.draw.polygon(surface, (255, 100, 0), [(px1, py1), (x2, y2), (px2, py2)])
        return True
    
    elif "blade_orbit" in effects:
        # 光刃：三角形核心+3把长剑环绕
        tri_points = [
            (center_x, center_y - size//6),
            (center_x - size//7, center_y + size//8),
            (center_x + size//7, center_y + size//8)
        ]
        pygame.draw.polygon(surface, color, tri_points)
        for i in range(3):
            angle = (pygame.time.get_ticks() / 300 + i * 120) * 3.14159 / 180
            base_x = center_x + int(size//5 * math.cos(angle))
            base_y = center_y + int(size//5 * math.sin(angle))
            tip_x = center_x + int(size//2.2 * math.cos(angle))
            tip_y = center_y + int(size//2.2 * math.sin(angle))
            perp_angle = angle + 3.14159/2
            w1 = size//15
            w2 = size//30
            sword_points = [
                (base_x + int(w1 * math.cos(perp_angle)), base_y + int(w1 * math.sin(perp_angle))),
                (tip_x + int(w2 * math.cos(perp_angle)), tip_y + int(w2 * math.sin(perp_angle))),
                (tip_x - int(w2 * math.cos(perp_angle)), tip_y - int(w2 * math.sin(perp_angle))),
                (base_x - int(w1 * math.cos(perp_angle)), base_y - int(w1 * math.sin(perp_angle)))
            ]
            pygame.draw.polygon(surface, (150, 200, 255), sword_points)
        return True
    
    return False
