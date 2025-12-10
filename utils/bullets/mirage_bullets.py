# -*- coding: utf-8 -*-
"""
Mirage 战机子弹涂装效果渲染模块

包含以下子弹效果：
- refraction_split/rainbow_trail: 棱镜折射弹
- mirror_reflect/sharp_edge: 镜面碎片弹
- afterimage_split/phantom_clone: 分身幻影弹
- pattern_rotate/color_shift: 万花旋转弹
- ripple_expand/symmetry_reflect: 水面倒影弹
- scan_line/data_stream: 全息幻象弹
- recursive_mirror/depth_infinite: 无限镜像弹
"""
import pygame
import math


def render_mirage_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Mirage战机的子弹效果
    
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
    
    if "refraction_split" in effects or "rainbow_trail" in effects:
        # 棱镜折射弹：三角棱镜+彩虹折射
        # 棱镜主体（三角形）
        prism_points = [
            (center_x, center_y - size//2),
            (center_x + size//3, center_y + size//3),
            (center_x - size//3, center_y + size//3)
        ]
        pygame.draw.polygon(surface, (200, 180, 255), prism_points)
        pygame.draw.polygon(surface, color, prism_points, 3)
        # 彩虹折射光线
        rainbow_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (148, 0, 211)]
        for i, ray_color in enumerate(rainbow_colors):
            angle = (30 + i * 25) * 3.14159 / 180
            x1 = center_x + size//6
            y1 = center_y
            x2 = center_x + int(size//2 * math.cos(angle))
            y2 = center_y + int(size//2 * math.sin(angle))
            pygame.draw.line(surface, ray_color, (x1, y1), (x2, y2), 2)
        # 入射白光
        pygame.draw.line(surface, (255, 255, 255), (center_x - size//2, center_y - size//4), (center_x - size//8, center_y), 3)
        return True
    
    elif "mirror_reflect" in effects or "sharp_edge" in effects:
        # 镜面碎片弹：破碎镜片+锋利边缘
        # 多个不规则碎片
        shards = [
            [(center_x - size//6, center_y - size//4), (center_x + size//8, center_y - size//3), (center_x, center_y)],
            [(center_x + size//8, center_y - size//3), (center_x + size//3, center_y), (center_x, center_y)],
            [(center_x, center_y), (center_x + size//3, center_y), (center_x + size//6, center_y + size//3)],
            [(center_x, center_y), (center_x + size//6, center_y + size//3), (center_x - size//4, center_y + size//4)],
            [(center_x - size//6, center_y - size//4), (center_x, center_y), (center_x - size//4, center_y + size//4)]
        ]
        for i, shard in enumerate(shards):
            # 镜面渐变色
            mirror_color = (220 - i*10, 220 - i*10, 240 - i*5)
            pygame.draw.polygon(surface, mirror_color, shard)
            pygame.draw.polygon(surface, color, shard, 2)
        # 反射光点
        pygame.draw.circle(surface, (255, 255, 255), (center_x - size//8, center_y - size//6), size//15)
        return True
    
    elif "afterimage_split" in effects or "phantom_clone" in effects:
        # 分身幻影弹：主体+多个虚影
        # 虚影（半透明）
        for i in range(3):
            offset = (i + 1) * size//8
            alpha = 80 - i * 20
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (size + offset, size), size//4)
            surface.blit(temp_surf, (x - size, y - size))
        # 主体（实心）
        pygame.draw.circle(surface, (180, 120, 255), (center_x, center_y), size//4)
        pygame.draw.circle(surface, color, (center_x, center_y), size//4, 3)
        # 幻影分裂线
        for i in range(3):
            angle = (60 + i * 60) * 3.14159 / 180
            x2 = center_x + int(size//2 * math.cos(angle))
            y2 = center_y + int(size//2 * math.sin(angle))
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.line(temp_surf, (*color, 150), 
                           (center_x - x + size, center_y - y + size), 
                           (x2 - x + size, y2 - y + size), 1)
            surface.blit(temp_surf, (x - size, y - size))
        return True
    
    elif "pattern_rotate" in effects or "color_shift" in effects:
        # 万花旋转弹：万花筒图案
        # 旋转对称图案
        rotation = pygame.time.get_ticks() / 200
        segments = 6
        for seg in range(segments):
            angle = (seg * 60 + rotation) * 3.14159 / 180
            # 花瓣形状
            petal_colors = [(255, 180, 200), (200, 150, 255), (150, 200, 255), (200, 255, 200), (255, 230, 150), (255, 150, 180)]
            petal_color = petal_colors[seg % len(petal_colors)]
            x1 = center_x + int(size//6 * math.cos(angle))
            y1 = center_y + int(size//6 * math.sin(angle))
            x2 = center_x + int(size//2.5 * math.cos(angle + 0.3))
            y2 = center_y + int(size//2.5 * math.sin(angle + 0.3))
            x3 = center_x + int(size//2.5 * math.cos(angle - 0.3))
            y3 = center_y + int(size//2.5 * math.sin(angle - 0.3))
            pygame.draw.polygon(surface, petal_color, [(center_x, center_y), (x2, y2), (x3, y3)])
            pygame.draw.polygon(surface, color, [(center_x, center_y), (x2, y2), (x3, y3)], 1)
        # 中心宝石
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//8)
        pygame.draw.circle(surface, color, (center_x, center_y), size//10)
        return True
    
    elif "ripple_expand" in effects or "symmetry_reflect" in effects:
        # 水面倒影弹：涟漪+对称倒影
        # 水波纹（椭圆）
        for i in range(4):
            wave_width = size//2 - i * size//12
            wave_height = size//4 - i * size//16
            alpha = 180 - i * 40
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.ellipse(temp_surf, (*color, alpha), 
                              (size - wave_width, size - wave_height, wave_width*2, wave_height*2), 2)
            surface.blit(temp_surf, (x - size, y - size))
        # 上半部分（实体）
        pygame.draw.arc(surface, (150, 200, 255), 
                      (center_x - size//4, center_y - size//4, size//2, size//2), 0, 3.14159, 4)
        # 下半部分（倒影，半透明）
        temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.arc(temp_surf, (150, 200, 255, 120), 
                      (size - size//4, size, size//2, size//4), 3.14159, 6.28318, 3)
        surface.blit(temp_surf, (x - size, y - size))
        # 分界线
        pygame.draw.line(surface, (200, 220, 255), (center_x - size//3, center_y), (center_x + size//3, center_y), 2)
        return True
    
    elif "scan_line" in effects or "data_stream" in effects:
        # 全息幻象弹：扫描线+数据流
        # 全息网格
        grid_step = size // 6
        for i in range(-3, 4):
            # 横线
            y_line = center_y + i * grid_step
            alpha = 100 if abs(i) < 2 else 60
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.line(temp_surf, (*color, alpha), 
                           (size - size//2, y_line - y + size),
                           (size + size//2, y_line - y + size), 1)
            surface.blit(temp_surf, (x - size, y - size))
            # 竖线
            x_line = center_x + i * grid_step
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.line(temp_surf, (*color, alpha),
                           (x_line - x + size, size - size//2),
                           (x_line - x + size, size + size//2), 1)
            surface.blit(temp_surf, (x - size, y - size))
        # 扫描线（动态）
        scan_y = center_y + int(size//2 * math.sin(pygame.time.get_ticks() / 200))
        pygame.draw.line(surface, (100, 255, 255), (center_x - size//2, scan_y), (center_x + size//2, scan_y), 2)
        # 数据点
        for i in range(5):
            data_x = center_x - size//3 + i * size//6
            data_y = center_y + int(size//6 * math.sin(pygame.time.get_ticks() / 100 + i))
            pygame.draw.circle(surface, (100, 200, 255), (data_x, data_y), 3)
        return True
    
    elif "recursive_mirror" in effects or "depth_infinite" in effects:
        # 无限镜像弹：递归嵌套镜像
        # 多层递归方框
        for i in range(5):
            box_size = size//2 - i * size//12
            alpha = 200 - i * 35
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            rect = (size - box_size, size - box_size, box_size*2, box_size*2)
            pygame.draw.rect(temp_surf, (*color, alpha), rect, 2)
            surface.blit(temp_surf, (x - size, y - size))
        # 无限符号
        inf_size = size // 6
        left_c = (center_x - inf_size, center_y)
        right_c = (center_x + inf_size, center_y)
        pygame.draw.circle(surface, (255, 200, 255), left_c, inf_size, 3)
        pygame.draw.circle(surface, (255, 200, 255), right_c, inf_size, 3)
        # 中心焦点
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//15)
        return True
    
    return False
