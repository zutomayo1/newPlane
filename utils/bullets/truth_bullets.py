# -*- coding: utf-8 -*-
"""
Truth 至尊·世界的真相 子弹涂装效果渲染模块

包含以下子弹效果：
- truth_revelation: 真理揭示弹（基础） - 黑白眼睛形态
- truth_judgment: 审判之光 - 金色天平
- truth_insight: 洞察之矢 - 穿透一切的白色光芒
- truth_illusion: 幻象破灭 - 破碎镜面效果
- truth_prophecy: 预言之星 - 紫金星芒
- truth_absolute: 绝对真理 - 终极形态
- truth_yin: 阴极之弹 - 黑色
- truth_yang: 阳极之弹 - 白色
"""
import pygame
import math


def render_truth_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Truth战机的子弹效果 - 至尊机体级别特效
    
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
    
    TRUTH_WHITE = (255, 255, 255)
    TRUTH_BLACK = (20, 20, 30)
    TRUTH_GOLD = (255, 215, 0)
    TRUTH_PURPLE = (150, 100, 200)
    
    if "truth_revelation" in effects or "truth_insight" in effects:
        # 真理揭示弹 - 全知之眼形态
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 外层光环
        pulse = abs(math.sin(t * 5)) * 3
        pygame.draw.circle(bullet_surf, (*TRUTH_GOLD, 150), (cx, cy), int(size//2 + pulse), 2)
        
        # 眼睛形态
        eye_w = size // 1.5
        eye_h = size // 3
        pygame.draw.ellipse(bullet_surf, TRUTH_WHITE, (cx - eye_w, cy - eye_h, eye_w * 2, eye_h * 2))
        pygame.draw.ellipse(bullet_surf, TRUTH_GOLD, (cx - eye_w, cy - eye_h, eye_w * 2, eye_h * 2), 2)
        
        # 虹膜
        pygame.draw.circle(bullet_surf, TRUTH_GOLD, (cx, cy), size // 4)
        
        # 瞳孔
        pygame.draw.circle(bullet_surf, TRUTH_BLACK, (cx, cy), size // 6)
        
        # 高光
        pygame.draw.circle(bullet_surf, TRUTH_WHITE, (cx - size // 8, cy - size // 10), size // 10)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "truth_judgment" in effects:
        # 审判之光 - 天平形态
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 光芒背景
        for i in range(6):
            angle = (i * 60 + t * 60) * math.pi / 180
            length = size // 2
            ex = cx + math.cos(angle) * length
            ey = cy + math.sin(angle) * length
            pygame.draw.line(bullet_surf, (*TRUTH_GOLD, 180), (cx, cy), (int(ex), int(ey)), 2)
        
        # 天平横梁
        balance_angle = 10 * math.sin(t * 4)
        left_y = cy - 2 + balance_angle * 0.1
        right_y = cy - 2 - balance_angle * 0.1
        pygame.draw.line(bullet_surf, TRUTH_GOLD, (cx - size // 3, left_y), (cx + size // 3, right_y), 2)
        
        # 支点
        pygame.draw.line(bullet_surf, TRUTH_GOLD, (cx, cy - size // 4), (cx, cy - 2), 2)
        pygame.draw.circle(bullet_surf, TRUTH_GOLD, (cx, cy - size // 4), 3)
        
        # 双盘
        pygame.draw.circle(bullet_surf, TRUTH_WHITE, (cx - size // 3, int(left_y + 6)), size // 6)
        pygame.draw.circle(bullet_surf, TRUTH_BLACK, (cx + size // 3, int(right_y + 6)), size // 6)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "truth_illusion" in effects:
        # 幻象破灭 - 破碎镜面
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 破碎镜面碎片
        shard_colors = [TRUTH_WHITE, (220, 220, 230), (200, 200, 210), TRUTH_GOLD]
        for i in range(8):
            angle = (i * 45 + t * 40) * math.pi / 180
            dist = size // 4 + size // 8 * abs(math.sin(t * 3 + i))
            
            # 三角形碎片
            shard_pts = []
            for j in range(3):
                sa = angle + j * 2.094
                sr = dist + 4 * (j % 2)
                shard_pts.append((cx + math.cos(sa) * sr, cy + math.sin(sa) * sr))
            
            pygame.draw.polygon(bullet_surf, shard_colors[i % 4], shard_pts)
            pygame.draw.polygon(bullet_surf, TRUTH_GOLD, shard_pts, 1)
        
        # 中心光点
        pygame.draw.circle(bullet_surf, TRUTH_GOLD, (cx, cy), size // 6)
        pygame.draw.circle(bullet_surf, TRUTH_WHITE, (cx, cy), size // 8)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "truth_prophecy" in effects:
        # 预言之星 - 紫金星芒
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 外层星芒
        for i in range(8):
            angle = (i * 45 + t * 30) * math.pi / 180
            length = size // 2 + size // 8 * abs(math.sin(t * 4 + i))
            ex = cx + math.cos(angle) * length
            ey = cy + math.sin(angle) * length
            
            color = TRUTH_GOLD if i % 2 == 0 else TRUTH_PURPLE
            pygame.draw.line(bullet_surf, color, (cx, cy), (int(ex), int(ey)), 2)
            pygame.draw.circle(bullet_surf, color, (int(ex), int(ey)), 3)
        
        # 核心球
        pygame.draw.circle(bullet_surf, TRUTH_PURPLE, (cx, cy), size // 4)
        pygame.draw.circle(bullet_surf, TRUTH_GOLD, (cx, cy), size // 5)
        pygame.draw.circle(bullet_surf, TRUTH_WHITE, (cx - 2, cy - 2), 2)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "truth_absolute" in effects:
        # 绝对真理 - 终极形态
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 多层旋转环
        for ring in range(3):
            ring_r = size // 3 + ring * 5
            rotation = t * (60 + ring * 30) * (1 if ring % 2 == 0 else -1)
            pts = []
            for j in range(6):
                angle = (j * 60 + rotation) * math.pi / 180
                pts.append((cx + math.cos(angle) * ring_r, cy + math.sin(angle) * ring_r))
            colors = [TRUTH_GOLD, TRUTH_WHITE, TRUTH_PURPLE]
            pygame.draw.polygon(bullet_surf, colors[ring], pts, 2)
        
        # 太极核心
        pygame.draw.circle(bullet_surf, TRUTH_WHITE, (cx - 4, cy), size // 6)
        pygame.draw.circle(bullet_surf, TRUTH_BLACK, (cx + 4, cy), size // 6)
        pygame.draw.circle(bullet_surf, TRUTH_BLACK, (cx - 4, cy), size // 12)
        pygame.draw.circle(bullet_surf, TRUTH_WHITE, (cx + 4, cy), size // 12)
        
        # 金色外框
        pygame.draw.circle(bullet_surf, TRUTH_GOLD, (cx, cy), size // 3, 2)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "truth_yin" in effects:
        # 阴极之弹 - 黑色
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 黑色主体
        pygame.draw.circle(bullet_surf, TRUTH_BLACK, (cx, cy), size // 2)
        pygame.draw.circle(bullet_surf, TRUTH_PURPLE, (cx, cy), size // 2, 2)
        
        # 阴极符号
        pygame.draw.arc(bullet_surf, TRUTH_PURPLE, 
                       (cx - size // 3, cy - size // 3, size * 2 // 3, size * 2 // 3),
                       math.pi, 2 * math.pi, 3)
        
        # 小白点
        pygame.draw.circle(bullet_surf, TRUTH_WHITE, (cx, cy - size // 6), size // 10)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    elif "truth_yang" in effects:
        # 阳极之弹 - 白色
        bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        cx, cy = size, size
        
        # 白色主体
        pygame.draw.circle(bullet_surf, TRUTH_WHITE, (cx, cy), size // 2)
        pygame.draw.circle(bullet_surf, TRUTH_GOLD, (cx, cy), size // 2, 2)
        
        # 阳极符号
        pygame.draw.arc(bullet_surf, TRUTH_GOLD, 
                       (cx - size // 3, cy - size // 3, size * 2 // 3, size * 2 // 3),
                       0, math.pi, 3)
        
        # 小黑点
        pygame.draw.circle(bullet_surf, TRUTH_BLACK, (cx, cy + size // 6), size // 10)
        
        surface.blit(bullet_surf, (x - size // 2, y - size // 2))
        return True
    
    return False


__all__ = ['render_truth_bullet']
