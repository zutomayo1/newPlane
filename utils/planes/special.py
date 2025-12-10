"""
特殊机体渲染

包含 3 种特殊机体的渲染函数:
- chronos: 时之回响·克洛诺斯
- mirage: 幻镜·万华
- gambit: 命运赌徒·艾斯
"""
import pygame
import math

from config import WHITE


def render_special(s, pid, c, edge_color, t, pulse, visual):
    """渲染特殊机体"""
    
    if pid == "chronos":
        _render_chronos(s, c, edge_color, t, pulse)
    elif pid == "mirage":
        _render_mirage(s, c, edge_color, t, pulse)
    elif pid == "gambit":
        _render_gambit(s, c, edge_color, t, pulse)


def _render_chronos(s, c, edge_color, t, pulse):
    """Chronos - 时之回响：时钟机械美学，时间轨迹记录"""
    main_color = (100, 220, 255)
    accent_color = (255, 200, 100)
    
    # 时钟外壳（双环结构）
    pygame.draw.circle(s, (80, 180, 230), (60, 60), 42, 3)
    pygame.draw.circle(s, main_color, (60, 60), 38, 2)
    pygame.draw.circle(s, (50, 150, 200), (60, 60), 34)
    
    # 12个时刻刻度
    for hour in range(12):
        angle = (hour * 30 - 90) * 0.01745
        tick_len = 6 if hour % 3 == 0 else 3
        outer_x = 60 + math.cos(angle) * 34
        outer_y = 60 + math.sin(angle) * 34
        inner_x = 60 + math.cos(angle) * (34 - tick_len)
        inner_y = 60 + math.sin(angle) * (34 - tick_len)
        pygame.draw.line(s, accent_color, (outer_x, outer_y), (inner_x, inner_y), 2)
    
    # 旋转的时针和分针
    hour_angle = (t * 0.5 - 90) * 0.01745
    minute_angle = (t * 6 - 90) * 0.01745
    
    # 时针
    hour_x = 60 + math.cos(hour_angle) * 18
    hour_y = 60 + math.sin(hour_angle) * 18
    pygame.draw.line(s, accent_color, (60, 60), (hour_x, hour_y), 4)
    pygame.draw.circle(s, (255, 220, 150), (int(hour_x), int(hour_y)), 3)
    
    # 分针
    minute_x = 60 + math.cos(minute_angle) * 28
    minute_y = 60 + math.sin(minute_angle) * 28
    pygame.draw.line(s, WHITE, (60, 60), (minute_x, minute_y), 3)
    pygame.draw.circle(s, (255, 255, 255), (int(minute_x), int(minute_y)), 2)
    
    # 秒针
    second_angle = (t * 30 - 90) * 0.01745
    second_x = 60 + math.cos(second_angle) * 32
    second_y = 60 + math.sin(second_angle) * 32
    pygame.draw.line(s, (0, 255, 255), (60, 60), (second_x, second_y), 1)
    
    # 中心齿轮
    pygame.draw.circle(s, (255, 200, 100), (60, 60), 8)
    pygame.draw.circle(s, (255, 220, 150), (60, 60), 5)
    for i in range(8):
        gear_angle = (t * 10 + i * 45) * 0.01745
        gear_x1 = 60 + math.cos(gear_angle) * 8
        gear_y1 = 60 + math.sin(gear_angle) * 8
        gear_x2 = 60 + math.cos(gear_angle) * 12
        gear_y2 = 60 + math.sin(gear_angle) * 12
        pygame.draw.line(s, (200, 160, 80), (gear_x1, gear_y1), (gear_x2, gear_y2), 2)
    
    # 时间回响轨迹
    for echo_i in range(6):
        echo_progress = (t * 2 + echo_i * 0.5) % 1.0
        echo_angle = (echo_progress * 360 - 90) * 0.01745
        echo_r = 25 + echo_progress * 15
        echo_x = 60 + math.cos(echo_angle) * echo_r
        echo_y = 60 + math.sin(echo_angle) * echo_r
        echo_alpha = int(200 * (1 - echo_progress))
        if echo_alpha > 0:
            echo_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(echo_surf, (*main_color, echo_alpha), (int(echo_x), int(echo_y)), 4 - echo_i)
            s.blit(echo_surf, (0, 0))
    
    # 外围时间粒子环
    for particle_i in range(12):
        particle_angle = (-t * 3 + particle_i * 30) * 0.01745
        particle_r = 48 + math.sin(t * 5 + particle_i) * 3
        px = 60 + math.cos(particle_angle) * particle_r
        py = 60 + math.sin(particle_angle) * particle_r
        particle_size = 3 + int(abs(math.sin(t * 4 + particle_i)) * 2)
        pygame.draw.circle(s, (100, 220, 255), (int(px), int(py)), particle_size)
        pygame.draw.circle(s, (200, 240, 255), (int(px), int(py)), particle_size - 1)


def _render_mirage(s, c, edge_color, t, pulse):
    """Mirage - 幻镜·万华：镜像分身，万花筒美学"""
    main_color = (200, 150, 255)
    accent_color = (255, 200, 255)
    
    # 三角棱镜主体
    prism_points = [(60, 25), (30, 85), (90, 85)]
    prism_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.polygon(prism_surf, (*main_color, 180), prism_points)
    s.blit(prism_surf, (0, 0))
    pygame.draw.polygon(s, accent_color, prism_points, 2)
    
    # 内部折射分割线
    pygame.draw.line(s, (255, 220, 255), (60, 25), (60, 75), 1)
    pygame.draw.line(s, (255, 220, 255), (60, 55), (40, 75), 1)
    pygame.draw.line(s, (255, 220, 255), (60, 55), (80, 75), 1)
    
    # 旋转的分身影像
    for mirror_i in range(3):
        mirror_angle = (t * 2 + mirror_i * 120) * 0.01745
        mirror_r = 38 + math.sin(t * 3 + mirror_i) * 5
        mx = 60 + math.cos(mirror_angle) * mirror_r
        my = 60 + math.sin(mirror_angle) * mirror_r
        
        mini_size = 8
        mini_angle_rad = (t * 5 + mirror_i * 120) * 0.01745
        mini_points = []
        for vertex_i in range(3):
            vertex_angle = mini_angle_rad + vertex_i * (2 * math.pi / 3)
            px = mx + math.cos(vertex_angle) * mini_size
            py = my + math.sin(vertex_angle) * mini_size
            mini_points.append((px, py))
        
        mirror_alpha = 180 - mirror_i * 30
        mirror_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(mirror_surf, (*accent_color, mirror_alpha), mini_points)
        s.blit(mirror_surf, (0, 0))
        pygame.draw.polygon(s, (255, 255, 255), mini_points, 1)
    
    # 万花筒光线
    for ray_i in range(6):
        ray_angle = (ray_i * 60 + t * 8) * 0.01745
        for seg in range(5):
            seg_start_r = 15 + seg * 7
            seg_end_r = seg_start_r + 8
            seg_alpha = 200 - seg * 35
            seg_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            sx1 = 60 + math.cos(ray_angle) * seg_start_r
            sy1 = 60 + math.sin(ray_angle) * seg_start_r
            sx2 = 60 + math.cos(ray_angle) * seg_end_r
            sy2 = 60 + math.sin(ray_angle) * seg_end_r
            pygame.draw.line(seg_surf, (*main_color, seg_alpha), (sx1, sy1), (sx2, sy2), 2)
            s.blit(seg_surf, (0, 0))
    
    # 核心水晶
    pygame.draw.circle(s, (255, 255, 255), (60, 55), 8)
    pygame.draw.circle(s, accent_color, (60, 55), 6)
    pygame.draw.circle(s, (255, 200, 255), (60, 55), 4)
    
    # 镜像粒子环
    for particle_i in range(16):
        particle_angle = (particle_i * 22.5 + t * 5) * 0.01745
        particle_r = 48 + math.sin(t * 6 + particle_i) * 4
        px = 60 + math.cos(particle_angle) * particle_r
        py = 60 + math.sin(particle_angle) * particle_r
        particle_size = 2 + int(abs(math.sin(t * 3 + particle_i)))
        pygame.draw.circle(s, (220, 180, 255), (int(px), int(py)), particle_size)


def _render_gambit(s, c, edge_color, t, pulse):
    """Gambit - 命运赌徒：赌场美学，扑克牌+骰子+轮盘"""
    gold_color = (255, 215, 0)
    red_color = (255, 50, 50)
    black_color = (30, 30, 30)
    
    # 主体轮盘
    pygame.draw.circle(s, black_color, (60, 60), 42)
    pygame.draw.circle(s, gold_color, (60, 60), 42, 3)
    pygame.draw.circle(s, (40, 40, 40), (60, 60), 38)
    
    # 轮盘分区
    for sector_i in range(12):
        sector_angle_start = (sector_i * 30 + t * 3) * 0.01745
        sector_angle_end = ((sector_i + 1) * 30 + t * 3) * 0.01745
        sector_color = red_color if sector_i % 2 == 0 else black_color
        sector_points = [(60, 60)]
        for ang in range(int(sector_angle_start * 57.3), int(sector_angle_end * 57.3) + 1, 3):
            ang_rad = ang * 0.01745
            sector_points.append((60 + math.cos(ang_rad) * 35, 60 + math.sin(ang_rad) * 35))
        if len(sector_points) > 2:
            pygame.draw.polygon(s, sector_color, sector_points)
    
    pygame.draw.circle(s, gold_color, (60, 60), 36, 2)
    
    # 中心旋转骰子
    dice_size = 14
    dice_angle = t * 8
    dice_points = []
    for corner_i in range(4):
        corner_angle = (dice_angle + corner_i * 90) * 0.01745
        dx = 60 + math.cos(corner_angle) * dice_size
        dy = 60 + math.sin(corner_angle) * dice_size
        dice_points.append((dx, dy))
    pygame.draw.polygon(s, (255, 255, 255), dice_points)
    pygame.draw.polygon(s, gold_color, dice_points, 2)
    
    # 骰子点数
    dice_dots = int(t * 2) % 6 + 1
    _draw_dice_dots(s, dice_dots, black_color)
    
    # 四张旋转扑克牌
    for card_i in range(4):
        card_angle = (card_i * 90 + t * 4) * 0.01745
        card_r = 46
        cx = 60 + math.cos(card_angle) * card_r
        cy = 60 + math.sin(card_angle) * card_r
        card_w, card_h = 10, 14
        card_rot = card_angle + math.pi / 2
        card_pts = []
        corners = [(-card_w/2, -card_h/2), (card_w/2, -card_h/2), 
                   (card_w/2, card_h/2), (-card_w/2, card_h/2)]
        for corner in corners:
            rx = corner[0] * math.cos(card_rot) - corner[1] * math.sin(card_rot)
            ry = corner[0] * math.sin(card_rot) + corner[1] * math.cos(card_rot)
            card_pts.append((cx + rx, cy + ry))
        card_color = red_color if card_i % 2 == 0 else black_color
        pygame.draw.polygon(s, (255, 255, 255), card_pts)
        pygame.draw.polygon(s, card_color, card_pts, 1)
    
    # 金色运气粒子
    for luck_i in range(10):
        luck_phase = (t * 3 + luck_i * 0.3) % 1.0
        luck_angle = (luck_i * 36 + t * 6) * 0.01745
        luck_r = 30 + luck_phase * 25
        lx = 60 + math.cos(luck_angle) * luck_r
        ly = 60 + math.sin(luck_angle) * luck_r
        luck_alpha = int(255 * (1 - luck_phase))
        luck_size = int(4 * (1 - luck_phase)) + 1
        luck_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(luck_surf, (*gold_color, luck_alpha), (int(lx), int(ly)), luck_size)
        s.blit(luck_surf, (0, 0))
    
    # 幸运星闪烁
    for star_i in range(5):
        star_angle = (star_i * 72 + t * 2) * 0.01745
        star_r = 52
        star_x = 60 + math.cos(star_angle) * star_r
        star_y = 60 + math.sin(star_angle) * star_r
        star_brightness = abs(math.sin(t * 8 + star_i * 1.5))
        if star_brightness > 0.7:
            star_size = 4
            pygame.draw.line(s, gold_color, (star_x - star_size, star_y), (star_x + star_size, star_y), 2)
            pygame.draw.line(s, gold_color, (star_x, star_y - star_size), (star_x, star_y + star_size), 2)


def _draw_dice_dots(s, dots, color):
    """绘制骰子点数"""
    if dots == 1:
        pygame.draw.circle(s, color, (60, 60), 3)
    elif dots == 2:
        pygame.draw.circle(s, color, (56, 56), 2)
        pygame.draw.circle(s, color, (64, 64), 2)
    elif dots == 3:
        pygame.draw.circle(s, color, (56, 56), 2)
        pygame.draw.circle(s, color, (60, 60), 2)
        pygame.draw.circle(s, color, (64, 64), 2)
    elif dots == 4:
        pygame.draw.circle(s, color, (56, 56), 2)
        pygame.draw.circle(s, color, (64, 56), 2)
        pygame.draw.circle(s, color, (56, 64), 2)
        pygame.draw.circle(s, color, (64, 64), 2)
    elif dots == 5:
        pygame.draw.circle(s, color, (56, 56), 2)
        pygame.draw.circle(s, color, (64, 56), 2)
        pygame.draw.circle(s, color, (60, 60), 2)
        pygame.draw.circle(s, color, (56, 64), 2)
        pygame.draw.circle(s, color, (64, 64), 2)
    else:  # 6
        pygame.draw.circle(s, color, (56, 56), 2)
        pygame.draw.circle(s, color, (64, 56), 2)
        pygame.draw.circle(s, color, (56, 60), 2)
        pygame.draw.circle(s, color, (64, 60), 2)
        pygame.draw.circle(s, color, (56, 64), 2)
        pygame.draw.circle(s, color, (64, 64), 2)


__all__ = ['render_special']
