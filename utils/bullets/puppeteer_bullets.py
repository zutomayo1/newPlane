# -*- coding: utf-8 -*-
"""
Puppeteer 战机子弹涂装效果渲染模块

包含以下子弹效果：
- thread_weave/fate_bind: 命运丝线弹
- pierce_soul/voodoo_curse: 巫毒缝针弹
- puppet_swarm/string_burst: 迷你木偶弹
- control_link/master_will: 十字控制弹
- soul_wail/ghost_bind: 灵魂碎片弹
- web_spread/sticky_trap: 蛛网陷阱弹
- fate_cut/life_sever: 命运剪刀弹
"""
import pygame
import math


def render_puppeteer_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Puppeteer战机的子弹效果
    
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
    
    if "thread_weave" in effects or "fate_bind" in effects:
        # 命运丝线弹：金色细线+小钩
        # 中心线团
        pygame.draw.circle(surface, color, (center_x, center_y), size//5)
        # 散射丝线
        for i in range(6):
            angle = (i * 60 + pygame.time.get_ticks() / 100) * 3.14159 / 180
            x1 = center_x + int(size//5 * math.cos(angle))
            y1 = center_y + int(size//5 * math.sin(angle))
            x2 = center_x + int(size//2.2 * math.cos(angle))
            y2 = center_y + int(size//2.2 * math.sin(angle))
            pygame.draw.line(surface, (200, 180, 220), (x1, y1), (x2, y2), 1)
            # 末端小钩
            hook_angle = angle + 0.5
            hx = x2 + int(size//15 * math.cos(hook_angle))
            hy = y2 + int(size//15 * math.sin(hook_angle))
            pygame.draw.line(surface, (180, 150, 80), (x2, y2), (hx, hy), 2)
        return True
    
    elif "pierce_soul" in effects or "voodoo_curse" in effects:
        # 巫毒缝针弹：长针+符文
        # 针身
        pygame.draw.line(surface, (180, 180, 200), (center_x, int(center_y - size//2.5)), (center_x, center_y + size//3), 3)
        # 针眼
        pygame.draw.circle(surface, (100, 100, 120), (center_x, int(center_y - size//2.5)), size//12)
        pygame.draw.circle(surface, (60, 60, 80), (center_x, int(center_y - size//2.5)), size//18)
        # 针尖
        tip_points = [(center_x, int(center_y + size//2.5)), (center_x - size//15, center_y + size//3), (center_x + size//15, center_y + size//3)]
        pygame.draw.polygon(surface, (200, 200, 220), tip_points)
        # 符文光环
        pygame.draw.circle(surface, color, (center_x, center_y), size//4, 1)
        return True
    
    elif "puppet_swarm" in effects or "string_burst" in effects:
        # 迷你木偶弹：小傀儡
        # 傀儡头
        pygame.draw.circle(surface, (240, 220, 200), (center_x, center_y - size//6), size//6)
        # X眼睛
        eye_size = size//20
        for dx in [-size//12, size//12]:
            pygame.draw.line(surface, (80, 40, 120), (center_x + dx - eye_size, center_y - size//6 - eye_size), (center_x + dx + eye_size, center_y - size//6 + eye_size), 2)
            pygame.draw.line(surface, (80, 40, 120), (center_x + dx - eye_size, center_y - size//6 + eye_size), (center_x + dx + eye_size, center_y - size//6 - eye_size), 2)
        # 傀儡身体
        pygame.draw.rect(surface, color, (center_x - size//8, center_y, size//4, size//3), border_radius=2)
        # 提线
        pygame.draw.line(surface, (200, 180, 220), (center_x, int(center_y - size//2.5)), (center_x, center_y - size//6 - size//6), 1)
        return True
    
    elif "control_link" in effects or "master_will" in effects:
        # 十字控制弹：木制十字架
        # 竖杆
        pygame.draw.rect(surface, (180, 150, 80), (center_x - size//16, int(center_y - size//2.5), size//8, size*2//3))
        # 横杆
        pygame.draw.rect(surface, (180, 150, 80), (center_x - size//3, center_y - size//5, size*2//3, size//10))
        # 金属边框
        pygame.draw.rect(surface, (200, 170, 100), (center_x - size//16, int(center_y - size//2.5), size//8, size*2//3), 2)
        pygame.draw.rect(surface, (200, 170, 100), (center_x - size//3, center_y - size//5, size*2//3, size//10), 2)
        # 悬挂丝线
        for dx in [-size//4, 0, size//4]:
            pygame.draw.line(surface, (200, 180, 220), (center_x + dx, center_y - size//10), (center_x + dx, center_y + size//3), 1)
        return True
    
    elif "soul_wail" in effects or "ghost_bind" in effects:
        # 灵魂碎片弹：半透明灵魂
        temp_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        # 灵魂形状（波浪边缘）
        points = []
        for i in range(12):
            angle = i * 30 * 3.14159 / 180
            r = size//3 + size//10 * math.sin(i * 2 + pygame.time.get_ticks() / 200)
            px = size//2 + int(r * math.cos(angle))
            py = size//2 + int(r * math.sin(angle))
            points.append((px, py))
        pygame.draw.polygon(temp_surf, (*color, 150), points)
        surface.blit(temp_surf, (x, y))
        # 哀嚎眼睛
        pygame.draw.circle(surface, (100, 150, 200), (center_x - size//10, center_y - size//12), size//15)
        pygame.draw.circle(surface, (100, 150, 200), (center_x + size//10, center_y - size//12), size//15)
        # 张开的嘴
        pygame.draw.ellipse(surface, (80, 130, 180), (center_x - size//12, center_y + size//20, size//6, size//8))
        return True
    
    elif "web_spread" in effects or "sticky_trap" in effects:
        # 蛛网陷阱弹：蜘蛛网
        # 同心圆
        for r in range(size//6, size//2, size//8):
            pygame.draw.circle(surface, color, (center_x, center_y), r, 1)
        # 放射线
        for i in range(8):
            angle = i * 45 * 3.14159 / 180
            x1 = center_x
            y1 = center_y
            x2 = center_x + int(size//2 * math.cos(angle))
            y2 = center_y + int(size//2 * math.sin(angle))
            pygame.draw.line(surface, (200, 200, 210), (x1, y1), (x2, y2), 1)
        # 中心亮点
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//15)
        return True
    
    elif "fate_cut" in effects or "life_sever" in effects:
        # 命运剪刀弹：剪刀形状
        # 剪刀两片刀刃
        blade1 = [(center_x - size//20, center_y), (center_x - size//3, int(center_y - size//2.5)), (center_x - size//4, int(center_y - size//2.5))]
        blade2 = [(center_x + size//20, center_y), (center_x + size//3, int(center_y - size//2.5)), (center_x + size//4, int(center_y - size//2.5))]
        pygame.draw.polygon(surface, (150, 150, 170), blade1)
        pygame.draw.polygon(surface, (150, 150, 170), blade2)
        pygame.draw.polygon(surface, (200, 200, 220), blade1, 2)
        pygame.draw.polygon(surface, (200, 200, 220), blade2, 2)
        # 中心枢轴
        pygame.draw.circle(surface, (100, 100, 120), (center_x, center_y), size//10)
        # 手柄
        pygame.draw.ellipse(surface, (80, 80, 100), (center_x - size//6, center_y + size//10, size//6, size//4))
        pygame.draw.ellipse(surface, (80, 80, 100), (center_x, center_y + size//10, size//6, size//4))
        return True
    
    return False
