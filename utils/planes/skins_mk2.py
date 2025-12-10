# -*- coding: utf-8 -*-
"""
MK2 涂装模块 - 各机体的基础改装涂装
"""
import pygame
import math
import random


def render_mk2_skin(s, pid, model_style, c, edge_color, t, pulse):
    """
    渲染 MK2 系列涂装
    
    Returns:
        pygame.Surface or None - 成功返回渲染结果，不匹配返回 None
    """
    if model_style == "striker_mk2":
        # 绯红之刃·改：更尖锐的造型，双翼展开
        pygame.draw.polygon(s, (80, 0, 0), [(60, 0), (120, 100), (60, 80), (0, 100)])
        pygame.draw.polygon(s, c, [(60, 5), (115, 95), (60, 75), (5, 95)])
        pygame.draw.polygon(s, edge_color, [(60, 5), (115, 95), (60, 75), (5, 95)], 2)
        # 额外的能量翼
        wing_pulse = int(10 * pulse)
        pygame.draw.line(s, (255, 100, 100), (60, 40), (10 - wing_pulse, 80), 3)
        pygame.draw.line(s, (255, 100, 100), (60, 40), (110 + wing_pulse, 80), 3)
        return s
        
    elif model_style == "phantom_mk2":
        # 虚空行者：破碎的几何体，半透明
        center_alpha = 150 + int(100 * pulse)
        pygame.draw.circle(s, (*c[:3], center_alpha), (60, 60), 20)
        pygame.draw.circle(s, edge_color, (60, 60), 20, 2)
        # 环绕的碎片
        for i in range(4):
            angle = t * 3 + (i * math.pi / 2)
            dist = 35 + 5 * math.sin(t * 5)
            px = 60 + math.cos(angle) * dist
            py = 60 + math.sin(angle) * dist
            pygame.draw.polygon(s, c, [(px, py-5), (px+5, py), (px, py+5), (px-5, py)])
        return s

    elif model_style == "titan_mk2":
        # 移动要塞：巨大的正方形结构，厚重
        pygame.draw.rect(s, (50, 30, 10), (10, 10, 100, 100))
        pygame.draw.rect(s, c, (15, 15, 90, 90))
        pygame.draw.rect(s, edge_color, (15, 15, 90, 90), 4)
        # 反应堆核心
        core_pulse = int(20 * pulse)
        pygame.draw.circle(s, (255, 100, 0), (60, 60), 15 + core_pulse // 4)
        pygame.draw.line(s, (255, 200, 0), (15, 15), (105, 105), 2)
        pygame.draw.line(s, (255, 200, 0), (105, 15), (15, 105), 2)
        return s

    elif model_style == "thunderbird_mk2":
        # 风暴领主：闪电形状的机翼
        points = [(60, 0), (90, 40), (120, 30), (100, 70), (120, 100), (60, 80), (0, 100), (20, 70), (0, 30), (30, 40)]
        pygame.draw.polygon(s, (100, 100, 0), points)
        inner_points = []
        for p in points:
            dx = p[0] - 60
            dy = p[1] - 60
            inner_points.append((60 + dx * 0.8, 60 + dy * 0.8))
        pygame.draw.polygon(s, c, inner_points)
        pygame.draw.lines(s, edge_color, True, points, 2)
        # 电弧效果
        if random.random() < 0.3:
            start_p = random.choice(points)
            end_p = random.choice(points)
            pygame.draw.line(s, (255, 255, 255), start_p, end_p, 2)
        return s

    elif model_style == "viper_mk2":
        # 九头蛇·毒液：生物质感，多头结构
        pygame.draw.ellipse(s, (20, 80, 20), (40, 20, 40, 80))
        pygame.draw.ellipse(s, c, (45, 25, 30, 70))
        head_y = 20 + int(5 * math.sin(t * 4))
        pygame.draw.circle(s, edge_color, (60, head_y), 15)
        for i in [-1, 1]:
            offset_x = i * 30
            offset_y = 40 + int(5 * math.sin(t * 4 + i))
            pygame.draw.circle(s, (50, 150, 50), (60 + offset_x, offset_y), 10)
            pygame.draw.line(s, (20, 80, 20), (60, 60), (60 + offset_x, offset_y), 5)
        return s

    elif model_style == "specter_mk2":
        # 死神之镰：巨大的镰刀形状
        pygame.draw.line(s, (50, 50, 50), (60, 100), (60, 20), 4)
        blade_points = [(60, 20), (100, 10), (110, 40), (80, 60), (60, 40)]
        pygame.draw.polygon(s, (150, 150, 150), blade_points)
        pygame.draw.polygon(s, c, blade_points, 2)
        glow_alpha = 100 + int(50 * pulse)
        pygame.draw.circle(s, (*c[:3], glow_alpha), (60, 40), 30, 2)
        return s

    elif model_style == "aurora_mk2":
        # 星辰女神：光环结构
        pygame.draw.circle(s, (255, 255, 255), (60, 60), 15)
        for i in range(3):
            radius = 30 + i * 10
            angle_offset = t * (i + 1)
            arc_rect = (60 - radius, 60 - radius, radius * 2, radius * 2)
            pygame.draw.arc(s, c, arc_rect, angle_offset, angle_offset + math.pi, 2)
        for i in range(4):
            px = 60 + math.cos(t * 2 + i * math.pi / 2) * 40
            py = 60 + math.sin(t * 2 + i * math.pi / 2) * 40
            pygame.draw.circle(s, edge_color, (int(px), int(py)), 4)
        return s

    elif model_style == "crimson_mk2":
        # 血魔领主：尖刺结构
        pygame.draw.polygon(s, (100, 0, 0), [(60, 10), (90, 40), (60, 100), (30, 40)])
        spike_len = 10 + 5 * pulse
        pygame.draw.line(s, edge_color, (30, 40), (30 - spike_len, 30), 3)
        pygame.draw.line(s, edge_color, (90, 40), (90 + spike_len, 30), 3)
        pygame.draw.line(s, edge_color, (60, 100), (60, 110 + spike_len), 3)
        pygame.draw.line(s, (255, 0, 0), (60, 20), (60, 90), 2)
        return s

    elif model_style == "stalker_mk2":
        # 虚空猎手：昆虫/异形结构
        pygame.draw.ellipse(s, (50, 0, 100), (45, 30, 30, 60))
        for i in range(3):
            y_off = i * 15
            leg_len = 20 + 5 * math.sin(t * 10 + i)
            pygame.draw.line(s, c, (45, 40 + y_off), (45 - leg_len, 50 + y_off), 2)
            pygame.draw.line(s, c, (75, 40 + y_off), (75 + leg_len, 50 + y_off), 2)
        pygame.draw.circle(s, (0, 255, 0), (55, 35), 3)
        pygame.draw.circle(s, (0, 255, 0), (65, 35), 3)
        return s

    elif model_style == "gaia_mk2":
        # 大地堡垒：水晶簇
        crystals = [
            ((60, 60), 30, (100, 255, 100)),
            ((40, 70), 20, (50, 200, 50)),
            ((80, 70), 20, (50, 200, 50)),
            ((60, 30), 25, (150, 255, 150))
        ]
        for pos, size, col in crystals:
            pts = [
                (pos[0], pos[1] - size),
                (pos[0] + size * 0.6, pos[1]),
                (pos[0], pos[1] + size),
                (pos[0] - size * 0.6, pos[1])
            ]
            pygame.draw.polygon(s, col, pts)
            pygame.draw.polygon(s, edge_color, pts, 1)
        return s

    elif model_style == "weaver_mk2":
        # 命运编织者：网状结构
        nodes = [(60, 20), (30, 50), (90, 50), (60, 80), (20, 90), (100, 90)]
        for p in nodes:
            pygame.draw.circle(s, c, p, 4)
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                dist = math.hypot(nodes[i][0] - nodes[j][0], nodes[i][1] - nodes[j][1])
                if dist < 60:
                    width = 1
                    if random.random() < 0.1: width = 2
                    pygame.draw.line(s, (200, 200, 200), nodes[i], nodes[j], width)
        return s

    elif model_style == "solar_mk2":
        # 太阳神：旋转的太阳
        pygame.draw.circle(s, (255, 200, 0), (60, 60), 25)
        num_rays = 12
        for i in range(num_rays):
            angle = t + i * (2 * math.pi / num_rays)
            ray_len = 40 + 10 * math.sin(t * 5)
            end_x = 60 + math.cos(angle) * ray_len
            end_y = 60 + math.sin(angle) * ray_len
            pygame.draw.line(s, (255, 100, 0), (60, 60), (end_x, end_y), 3)
        return s

    elif model_style == "arbiter_mk2":
        # 真理裁决：完美的几何体
        angle = t * 2
        size = 40
        pts = []
        for i in range(4):
            a = angle + i * (math.pi / 2)
            pts.append((60 + math.cos(a) * size, 60 + math.sin(a) * size))
        pygame.draw.polygon(s, c, pts, 2)
        angle2 = -t * 3
        size2 = 20
        pts2 = []
        for i in range(3):
            a = angle2 + i * (2 * math.pi / 3)
            pts2.append((60 + math.cos(a) * size2, 60 + math.sin(a) * size2))
        pygame.draw.polygon(s, edge_color, pts2)
        return s

    elif model_style == "eclipse_mk2":
        # 永夜之蚀：日食效果
        pygame.draw.circle(s, (0, 0, 0), (60, 60), 30)
        pygame.draw.circle(s, (100, 50, 150), (60, 60), 32, 2)
        offset = 10 * math.sin(t)
        pygame.draw.circle(s, (20, 0, 40), (60 + offset, 60), 25)
        return s

    elif model_style == "prism_mk2":
        # 水晶棱镜：透明三角
        pts = [(60, 20), (100, 90), (20, 90)]
        s2 = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(s2, (*c[:3], 100), pts)
        s.blit(s2, (0, 0))
        pygame.draw.polygon(s, (255, 255, 255), pts, 2)
        pygame.draw.line(s, (255, 255, 255), (60, 20), (60, 90), 1)
        return s

    elif model_style == "necro_mk2":
        # 巫妖王：骷髅头形状
        pygame.draw.ellipse(s, (200, 200, 200), (40, 30, 40, 50))
        eye_color = (0, 255, 0)
        pygame.draw.circle(s, eye_color, (50, 45), 4)
        pygame.draw.circle(s, eye_color, (70, 45), 4)
        for i in range(3):
            x = 50 + i * 10
            pygame.draw.line(s, (150, 150, 150), (x, 70), (x, 80), 2)
        return s

    return None  # 不匹配


# 导出函数列表
MK2_STYLES = [
    "striker_mk2", "phantom_mk2", "titan_mk2", "thunderbird_mk2",
    "viper_mk2", "specter_mk2", "aurora_mk2", "crimson_mk2",
    "stalker_mk2", "gaia_mk2", "weaver_mk2", "solar_mk2",
    "arbiter_mk2", "eclipse_mk2", "prism_mk2", "necro_mk2"
]


def is_mk2_style(model_style):
    """检查是否是 MK2 涂装"""
    return model_style in MK2_STYLES
