"""
敌人和Boss渲染模块

包含Boss外观和程序化敌人单位渲染
高质量版本 - 多层渲染、动态效果、精细细节
"""
import pygame
import math
import random

from config import WHITE, GRAY, RED, DARK_RED, BLACK, LIME, GHOST_CYAN, WIND_BLUE
from .core import log_error


def _bloom(surface, center, color, max_radius=60, layers=4):
    """Draw bloom by blitting expanding translucent circles."""
    cx, cy = center
    for i in range(layers, 0, -1):
        r = int(max_radius * (i / float(layers)))
        alpha = int(80 * (i / float(layers)))
        tmp = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(tmp, (*color[:3], alpha), (r, r), r)
        surface.blit(tmp, (cx - r, cy - r), special_flags=pygame.BLEND_ADD)


def _draw_glow_circle(surface, center, color, radius, glow_layers=3):
    """绘制带光晕的圆形"""
    cx, cy = center
    for i in range(glow_layers, 0, -1):
        r = radius + i * 4
        alpha = 60 // i
        pygame.draw.circle(surface, (*color[:3], alpha), (cx, cy), r)
    pygame.draw.circle(surface, color, (cx, cy), radius)


def _draw_energy_ring(surface, center, radius, color, t, segments=12, width=2):
    """绘制能量环"""
    cx, cy = center
    for i in range(segments):
        angle1 = math.radians(i * (360 / segments) + t * 50)
        angle2 = math.radians((i + 0.7) * (360 / segments) + t * 50)
        x1 = cx + math.cos(angle1) * radius
        y1 = cy + math.sin(angle1) * radius
        x2 = cx + math.cos(angle2) * radius
        y2 = cy + math.sin(angle2) * radius
        pygame.draw.line(surface, color, (int(x1), int(y1)), (int(x2), int(y2)), width)


def _draw_armor_plate(surface, rect, color, highlight=True):
    """绘制装甲板"""
    x, y, w, h = rect
    # 主体
    pygame.draw.rect(surface, color, rect, border_radius=3)
    # 高光边缘
    if highlight:
        highlight_color = (min(255, color[0]+60), min(255, color[1]+60), min(255, color[2]+60))
        pygame.draw.line(surface, highlight_color, (x+2, y+1), (x+w-2, y+1), 1)
    # 阴影边缘
    shadow_color = (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40))
    pygame.draw.line(surface, shadow_color, (x+2, y+h-1), (x+w-2, y+h-1), 1)


def _draw_mechanical_detail(surface, cx, cy, size, color, t):
    """绘制机械细节"""
    # 螺栓
    bolt_positions = [(cx-size//3, cy-size//3), (cx+size//3, cy-size//3), 
                      (cx-size//3, cy+size//3), (cx+size//3, cy+size//3)]
    for bx, by in bolt_positions:
        pygame.draw.circle(surface, (60, 60, 70), (bx, by), 3)
        pygame.draw.circle(surface, (100, 100, 110), (bx, by), 2)
    # 通风口
    for i in range(3):
        vy = cy - 10 + i * 10
        pygame.draw.line(surface, (30, 30, 40), (cx-size//4, vy), (cx+size//4, vy), 2)


def _draw_energy_core(surface, cx, cy, base_radius, color, t, pulse_speed=200):
    """绘制能量核心"""
    pulse = math.sin(t / pulse_speed) * 0.3 + 0.7
    # 外圈光晕
    for i in range(4, 0, -1):
        r = int(base_radius + i * 6)
        alpha = int(40 * pulse / i)
        pygame.draw.circle(surface, (*color[:3], alpha), (cx, cy), r)
    # 核心
    core_r = int(base_radius * pulse)
    pygame.draw.circle(surface, color, (cx, cy), core_r)
    # 内核高光
    inner_r = int(core_r * 0.6)
    highlight = (min(255, color[0]+100), min(255, color[1]+100), min(255, color[2]+100))
    pygame.draw.circle(surface, highlight, (cx - inner_r//3, cy - inner_r//3), inner_r)


def get_boss_surf(type_name, color, visual=None):
    """生成高质量Boss外观"""
    s = pygame.Surface((240, 240), pygame.SRCALPHA)
    t = pygame.time.get_ticks()
    cx, cy = 120, 120
    
    # ===== 基础Boss =====
    def draw_carrier():
        """航母 - 重型战舰，多层装甲"""
        # 主体轮廓
        hull_pts = [(20, 80), (120, 200), (220, 80), (120, 20)]
        pygame.draw.polygon(s, (60, 20, 20), hull_pts)
        pygame.draw.polygon(s, (100, 30, 30), [(30, 80), (120, 180), (210, 80), (120, 30)], 0)
        # 装甲层次
        for i in range(3):
            offset = i * 15
            pts = [(40+offset, 80), (120, 170-offset), (200-offset, 80), (120, 35+offset)]
            pygame.draw.polygon(s, color, pts, 2)
        # 飞行甲板
        pygame.draw.rect(s, (80, 30, 30), (90, 70, 60, 50), border_radius=3)
        pygame.draw.rect(s, color, (95, 75, 50, 40), 2, border_radius=2)
        # 机库
        for i in range(3):
            pygame.draw.rect(s, (40, 15, 15), (100 + i*15, 80, 12, 25))
            pygame.draw.rect(s, (150, 80, 80), (102 + i*15, 82, 8, 21), 1)
        # 侧翼武器舱
        pygame.draw.rect(s, (50, 20, 20), (15, 40, 50, 90), border_radius=5)
        pygame.draw.rect(s, (50, 20, 20), (175, 40, 50, 90), border_radius=5)
        pygame.draw.rect(s, color, (20, 45, 40, 80), 2, border_radius=4)
        pygame.draw.rect(s, color, (180, 45, 40, 80), 2, border_radius=4)
        # 导弹发射管
        for i in range(4):
            pygame.draw.circle(s, (30, 10, 10), (30, 55 + i*18), 6)
            pygame.draw.circle(s, (200, 100, 100), (30, 55 + i*18), 4)
            pygame.draw.circle(s, (30, 10, 10), (210, 55 + i*18), 6)
            pygame.draw.circle(s, (200, 100, 100), (210, 55 + i*18), 4)
        # 引擎光芒
        engine_pulse = math.sin(t / 100) * 0.3 + 0.7
        for ex in [80, 120, 160]:
            _draw_glow_circle(s, (ex, 195), (255, 150, 50), int(8 * engine_pulse))
        # 舰桥
        pygame.draw.polygon(s, (100, 40, 40), [(100, 50), (140, 50), (130, 30), (110, 30)])
        pygame.draw.polygon(s, (200, 150, 150), [(105, 48), (135, 48), (128, 33), (112, 33)], 1)
        # 灯光
        pygame.draw.circle(s, (255, 50, 50), (120, 40), 3)
    
    def draw_fortress():
        """堡垒 - 重装防御平台"""
        # 外层装甲
        pygame.draw.rect(s, (40, 25, 15), (20, 20, 200, 200), border_radius=25)
        # 多层装甲板
        for i in range(4):
            offset = i * 12
            armor_color = (50 + i*10, 30 + i*5, 10 + i*3)
            pygame.draw.rect(s, armor_color, (25+offset, 25+offset, 190-offset*2, 190-offset*2), 
                           border_radius=22-i*3)
        pygame.draw.rect(s, color, (35, 35, 170, 170), 4, border_radius=18)
        # 中央武器平台
        pygame.draw.circle(s, (30, 15, 10), (cx, cy), 70)
        pygame.draw.circle(s, DARK_RED, (cx, cy), 60)
        pygame.draw.circle(s, color, (cx, cy), 55, 3)
        # 旋转炮塔底座
        _draw_energy_ring(s, (cx, cy), 45, color, t/1000, 8, 3)
        # 核心
        _draw_energy_core(s, cx, cy, 25, (255, 100, 50), t)
        # 四角防御塔
        corners = [(45, 45), (195, 45), (45, 195), (195, 195)]
        for corner_x, corner_y in corners:
            pygame.draw.circle(s, (60, 35, 20), (corner_x, corner_y), 20)
            pygame.draw.circle(s, color, (corner_x, corner_y), 18, 2)
            pygame.draw.circle(s, (200, 100, 50), (corner_x, corner_y), 8)
        # 护盾发生器
        shield_pulse = math.sin(t / 150) * 0.3 + 0.7
        pygame.draw.circle(s, (*color[:3], int(60 * shield_pulse)), (cx, cy), 95, 2)
    
    def draw_assassin():
        """刺客 - 隐形战机"""
        # 主体
        body_pts = [(10, 20), (110, 160), (210, 20), (110, 70)]
        pygame.draw.polygon(s, (25, 15, 40), body_pts)
        # 隐形涂层效果
        for i in range(3):
            offset = i * 8
            pts = [(15+offset, 25+offset//2), (110, 155-offset*2), (205-offset, 25+offset//2), (110, 72+offset)]
            alpha = 180 - i * 40
            layer_color = (40 + i*15, 20 + i*10, 60 + i*20)
            pygame.draw.polygon(s, layer_color, pts)
        pygame.draw.polygon(s, color, [(25, 30), (110, 140), (195, 30), (110, 80)], 2)
        # 隐形场发生器
        cloak_pulse = math.sin(t / 120) * 0.5 + 0.5
        pygame.draw.circle(s, (*color[:3], int(80 * cloak_pulse)), (110, 90), 40, 1)
        # 前置武器
        pygame.draw.polygon(s, (60, 30, 80), [(100, 30), (120, 30), (110, 10)])
        pygame.draw.polygon(s, color, [(103, 28), (117, 28), (110, 14)], 1)
        # 尾翼引擎
        for ex in [60, 160]:
            pygame.draw.circle(s, (100, 50, 150), (ex, 140), 10)
            pygame.draw.circle(s, (200, 100, 255), (ex, 140), 6)
        # 干扰器阵列
        for i in range(5):
            jx = 70 + i * 20
            jy = 100 + (i % 2) * 10
            pygame.draw.circle(s, (150, 80, 200), (jx, jy), 3)

    def draw_seraphim():
        """炽天使 - 神圣光环战机"""
        # 多重光环
        for i in range(5):
            r = 100 - i * 15
            alpha = 150 - i * 25
            ring_color = (*color[:3], alpha)
            pygame.draw.circle(s, ring_color, (cx, cy), r, 3 - i//2)
        # 光翼
        wing_pulse = math.sin(t / 80) * 10
        for side in [-1, 1]:
            pts = [
                (cx + side * 20, cy),
                (cx + side * 100, cy - 40 + wing_pulse),
                (cx + side * 90, cy + 20),
                (cx + side * 30, cy + 10)
            ]
            pygame.draw.polygon(s, (*WHITE[:3], 180), pts)
            pygame.draw.polygon(s, color, pts, 2)
        # 中央神核
        pygame.draw.circle(s, WHITE, (cx, cy), 45)
        pygame.draw.circle(s, (255, 255, 200), (cx, cy), 40)
        _draw_energy_core(s, cx, cy, 25, color, t, 150)
        # 神圣符文
        for i in range(6):
            rad = math.radians(i * 60 + t / 50)
            rx = cx + math.cos(rad) * 70
            ry = cy + math.sin(rad) * 70
            pygame.draw.circle(s, color, (int(rx), int(ry)), 8)
            pygame.draw.circle(s, WHITE, (int(rx), int(ry)), 5)
            # 连接线
            pygame.draw.line(s, (*color[:3], 150), (cx, cy), (int(rx), int(ry)), 2)
        # 光柱
        for i in range(0, 360, 60):
            rad = math.radians(i)
            end_x = cx + math.cos(rad) * 105
            end_y = cy + math.sin(rad) * 105
            pygame.draw.line(s, color, (cx, cy), (int(end_x), int(end_y)), 4)
            pygame.draw.line(s, WHITE, (cx, cy), (int(end_x), int(end_y)), 2)

    def draw_leviathan():
        """利维坦 - 深海巨兽"""
        # 身体节段
        segments = [(100, 35, 55), (100, 70, 50), (100, 110, 45), (100, 150, 38), (100, 185, 30)]
        for i, (sx, sy, size) in enumerate(segments):
            # 外壳
            pygame.draw.circle(s, (40, 20, 70), (sx, sy), size + 5)
            pygame.draw.circle(s, color, (sx, sy), size)
            pygame.draw.circle(s, (70, 30, 100), (sx, sy), size - 8)
            # 鳞片纹理
            for j in range(3):
                scale_y = sy - size//2 + j * (size//2)
                pygame.draw.arc(s, (100, 50, 150), (sx-size+10, scale_y, size*2-20, 20), 0, 3.14, 1)
        # 头部
        pygame.draw.polygon(s, color, [(50, 50), (150, 50), (100, 5)])
        pygame.draw.polygon(s, (150, 80, 200), [(60, 48), (140, 48), (100, 12)], 2)
        # 眼睛
        pygame.draw.circle(s, (200, 50, 255), (75, 45), 12)
        pygame.draw.circle(s, BLACK, (75, 45), 6)
        pygame.draw.circle(s, (200, 50, 255), (125, 45), 12)
        pygame.draw.circle(s, BLACK, (125, 45), 6)
        pygame.draw.circle(s, WHITE, (73, 43), 3)
        pygame.draw.circle(s, WHITE, (123, 43), 3)
        # 触手
        for i in range(4):
            tx = 60 + i * 25
            for j in range(3):
                ty = 200 + j * 12
                pygame.draw.circle(s, (80, 40, 120), (tx + (j-1)*3, ty), 5 - j)

    def draw_overlord():
        """霸主 - 指挥舰"""
        # 主体圆盘
        pygame.draw.circle(s, (15, 15, 25), (cx, cy), 95)
        pygame.draw.circle(s, (25, 25, 40), (cx, cy), 90)
        # 装甲环
        for i in range(4):
            r = 90 - i * 18
            pygame.draw.circle(s, color, (cx, cy), r, 3)
        # 指挥核心
        pygame.draw.circle(s, (40, 40, 60), (cx, cy), 35)
        _draw_energy_core(s, cx, cy, 22, RED, t)
        # 辐射状武器阵列
        for i in range(0, 360, 45):
            rad = math.radians(i + t / 80)
            # 武器臂
            end_x = cx + math.cos(rad) * 85
            end_y = cy + math.sin(rad) * 85
            mid_x = cx + math.cos(rad) * 50
            mid_y = cy + math.sin(rad) * 50
            pygame.draw.line(s, GRAY, (cx, cy), (int(end_x), int(end_y)), 4)
            pygame.draw.line(s, color, (cx, cy), (int(end_x), int(end_y)), 2)
            # 武器节点
            pygame.draw.circle(s, (60, 60, 80), (int(mid_x), int(mid_y)), 8)
            pygame.draw.circle(s, color, (int(mid_x), int(mid_y)), 5)
            # 末端炮台
            pygame.draw.circle(s, (80, 80, 100), (int(end_x), int(end_y)), 10)
            pygame.draw.circle(s, (200, 50, 50), (int(end_x), int(end_y)), 6)
        # 护盾投影
        shield_alpha = int(40 + 20 * math.sin(t / 200))
        pygame.draw.circle(s, (*color[:3], shield_alpha), (cx, cy), 100, 2)

    def draw_ragnarok():
        """末日 - 毁灭战舰"""
        # 主体装甲
        pygame.draw.rect(s, (50, 25, 15), (50, 30, 140, 120), border_radius=15)
        pygame.draw.rect(s, color, (55, 35, 130, 110), 3, border_radius=12)
        # 多层装甲
        for i in range(3):
            _draw_armor_plate(s, (60 + i*10, 40 + i*10, 120 - i*20, 90 - i*20), 
                            (60 + i*15, 30 + i*10, 15 + i*5))
        # 中央武器系统
        pygame.draw.rect(s, DARK_RED, (85, 65, 70, 50), border_radius=5)
        pygame.draw.rect(s, color, (90, 70, 60, 40), 2, border_radius=3)
        # 主炮
        pygame.draw.line(s, (150, 60, 60), (90, 85), (50, 85), 6)
        pygame.draw.line(s, (150, 60, 60), (150, 85), (190, 85), 6)
        pygame.draw.circle(s, (200, 80, 80), (50, 85), 8)
        pygame.draw.circle(s, (200, 80, 80), (190, 85), 8)
        # 能量核心
        _draw_energy_core(s, 120, 85, 18, (255, 100, 50), t, 120)
        # 侧翼
        pygame.draw.polygon(s, GRAY, [(30, 35), (50, 55), (50, 125), (30, 145)])
        pygame.draw.polygon(s, GRAY, [(210, 35), (190, 55), (190, 125), (210, 145)])
        pygame.draw.polygon(s, color, [(32, 40), (48, 58), (48, 122), (32, 140)], 2)
        pygame.draw.polygon(s, color, [(208, 40), (192, 58), (192, 122), (208, 140)], 2)
        # 引擎
        for ey in [50, 90, 130]:
            pygame.draw.rect(s, (80, 40, 30), (52, ey-8, 15, 16), border_radius=2)
            pygame.draw.rect(s, (80, 40, 30), (173, ey-8, 15, 16), border_radius=2)
            # 引擎光
            engine_glow = int(200 + 55 * math.sin(t / 50 + ey))
            pygame.draw.circle(s, (engine_glow, 100, 50), (45, ey), 5)
            pygame.draw.circle(s, (engine_glow, 100, 50), (195, ey), 5)

    def draw_hydra():
        """九头蛇 - 多头生物"""
        # 身体
        pygame.draw.ellipse(s, (20, 60, 30), (70, 140, 100, 80))
        pygame.draw.ellipse(s, (40, 100, 50), (75, 145, 90, 70), 2)
        # 三个头
        head_data = [(-45, -30, 0.9), (0, -50, 1.0), (45, -30, 0.9)]
        for offset_x, offset_y, scale in head_data:
            hx, hy = 120 + offset_x, 120 + offset_y
            head_size = int(32 * scale)
            # 颈部
            pygame.draw.line(s, (30, 80, 40), (120, 170), (hx, hy + head_size), 12)
            pygame.draw.line(s, (50, 120, 60), (120, 170), (hx, hy + head_size), 8)
            # 头部
            pygame.draw.circle(s, color, (hx, hy), head_size)
            pygame.draw.circle(s, LIME, (hx, hy), head_size - 8)
            # 眼睛
            pygame.draw.circle(s, (200, 255, 200), (hx - 8, hy - 5), 8)
            pygame.draw.circle(s, BLACK, (hx - 8, hy - 5), 4)
            pygame.draw.circle(s, (200, 255, 200), (hx + 8, hy - 5), 8)
            pygame.draw.circle(s, BLACK, (hx + 8, hy - 5), 4)
            # 毒液滴落
            drip_y = hy + head_size + int(10 * math.sin(t / 100 + offset_x))
            pygame.draw.circle(s, (100, 255, 100), (hx, drip_y), 4)
        # 鳞片效果
        for i in range(5):
            sy = 155 + i * 12
            pygame.draw.arc(s, (60, 150, 70), (80, sy, 80, 15), 0, 3.14, 2)

    def draw_chronos():
        """克洛诺斯 - 时间领主"""
        # 外圈时钟
        pygame.draw.circle(s, (30, 30, 50), (cx, cy), 105)
        pygame.draw.circle(s, color, (cx, cy), 100, 3)
        pygame.draw.circle(s, (*color[:3], 150), (cx, cy), 95, 1)
        pygame.draw.circle(s, color, (cx, cy), 80, 2)
        # 时间刻度
        for i in range(12):
            rad = math.radians(i * 30 - 90)
            inner_r = 85 if i % 3 == 0 else 90
            outer_r = 95
            x1 = cx + math.cos(rad) * inner_r
            y1 = cy + math.sin(rad) * inner_r
            x2 = cx + math.cos(rad) * outer_r
            y2 = cy + math.sin(rad) * outer_r
            width = 3 if i % 3 == 0 else 1
            pygame.draw.line(s, color, (int(x1), int(y1)), (int(x2), int(y2)), width)
        # 中心机芯
        pygame.draw.circle(s, (50, 50, 80), (cx, cy), 40)
        pygame.draw.circle(s, color, (cx, cy), 35, 2)
        pygame.draw.circle(s, WHITE, (cx, cy), 15)
        pygame.draw.circle(s, color, (cx, cy), 12)
        # 时针分针
        hour_angle = math.radians((t / 5000) % 360 - 90)
        min_angle = math.radians((t / 500) % 360 - 90)
        # 时针
        hx = cx + math.cos(hour_angle) * 40
        hy = cy + math.sin(hour_angle) * 40
        pygame.draw.line(s, WHITE, (cx, cy), (int(hx), int(hy)), 5)
        pygame.draw.line(s, color, (cx, cy), (int(hx), int(hy)), 3)
        # 分针
        mx = cx + math.cos(min_angle) * 65
        my = cy + math.sin(min_angle) * 65
        pygame.draw.line(s, WHITE, (cx, cy), (int(mx), int(my)), 3)
        pygame.draw.line(s, color, (cx, cy), (int(mx), int(my)), 1)
        # 时间涟漪
        ripple_r = 60 + int(20 * math.sin(t / 300))
        pygame.draw.circle(s, (*color[:3], 80), (cx, cy), ripple_r, 1)

    def draw_gazer():
        """凝视者 - 全视之眼"""
        # 眼眶
        pygame.draw.circle(s, (40, 10, 10), (cx, cy), 100)
        pygame.draw.circle(s, (60, 15, 15), (cx, cy), 95)
        # 血丝
        for i in range(16):
            rad = math.radians(i * 22.5 + random.random() * 10)
            inner_r = 45 + random.randint(0, 10)
            outer_r = 95
            x1 = cx + math.cos(rad) * inner_r
            y1 = cy + math.sin(rad) * inner_r
            x2 = cx + math.cos(rad) * outer_r
            y2 = cy + math.sin(rad) * outer_r
            pygame.draw.line(s, (150, 30, 30), (int(x1), int(y1)), (int(x2), int(y2)), 2)
        # 虹膜
        pygame.draw.circle(s, RED, (cx, cy), 70, 4)
        pygame.draw.circle(s, (180, 40, 40), (cx, cy), 55)
        # 虹膜纹理
        for i in range(24):
            rad = math.radians(i * 15)
            x1 = cx + math.cos(rad) * 30
            y1 = cy + math.sin(rad) * 30
            x2 = cx + math.cos(rad) * 52
            y2 = cy + math.sin(rad) * 52
            pygame.draw.line(s, (200, 60, 60), (int(x1), int(y1)), (int(x2), int(y2)), 1)
        # 瞳孔
        pygame.draw.circle(s, BLACK, (cx, cy), 35)
        pygame.draw.circle(s, (30, 5, 5), (cx, cy), 30)
        # 瞳孔收缩动画
        pupil_size = 15 + int(5 * math.sin(t / 200))
        pygame.draw.circle(s, RED, (cx, cy), pupil_size)
        pygame.draw.circle(s, (255, 100, 100), (cx, cy), pupil_size - 5)
        # 高光
        pygame.draw.circle(s, (255, 200, 200), (cx - 25, cy - 25), 15)
        pygame.draw.circle(s, WHITE, (cx - 20, cy - 20), 8)
        # 死亡凝视射线
        for i in range(0, 360, 45):
            rad = math.radians(i)
            ex = cx + math.cos(rad) * 115
            ey = cy + math.sin(rad) * 115
            pygame.draw.line(s, (150, 30, 30, 150), (cx, cy), (int(ex), int(ey)), 2)

    def draw_lich():
        """巫妖 - 亡灵法师"""
        # 斗篷
        pygame.draw.polygon(s, (15, 5, 25), [(50, 200), (190, 200), (170, 80), (120, 30), (70, 80)])
        pygame.draw.polygon(s, (25, 10, 40), [(55, 195), (185, 195), (167, 85), (120, 38), (73, 85)])
        pygame.draw.polygon(s, (40, 20, 60), [(60, 190), (180, 190), (164, 90), (120, 45), (76, 90)], 2)
        # 骷髅脸
        pygame.draw.circle(s, (200, 190, 180), (120, 75), 30)
        pygame.draw.circle(s, (230, 220, 210), (120, 75), 28)
        # 眼眶
        pygame.draw.circle(s, BLACK, (108, 70), 10)
        pygame.draw.circle(s, BLACK, (132, 70), 10)
        # 幽魂之火眼睛
        eye_pulse = 5 + int(3 * math.sin(t / 100))
        pygame.draw.circle(s, GHOST_CYAN, (108, 70), eye_pulse)
        pygame.draw.circle(s, GHOST_CYAN, (132, 70), eye_pulse)
        pygame.draw.circle(s, (200, 255, 255), (108, 70), eye_pulse - 2)
        pygame.draw.circle(s, (200, 255, 255), (132, 70), eye_pulse - 2)
        # 鼻腔
        pygame.draw.polygon(s, (50, 40, 35), [(117, 80), (123, 80), (120, 90)])
        # 牙齿
        for i in range(5):
            tx = 107 + i * 6
            pygame.draw.rect(s, (220, 210, 200), (tx, 92, 4, 6))
        # 法杖
        pygame.draw.rect(s, (60, 40, 30), (35, 95, 8, 100))
        pygame.draw.rect(s, (180, 160, 140), (35, 95, 8, 100), 1)
        pygame.draw.rect(s, (60, 40, 30), (197, 95, 8, 100))
        pygame.draw.rect(s, (180, 160, 140), (197, 95, 8, 100), 1)
        # 法杖宝珠
        _draw_energy_core(s, 39, 90, 12, GHOST_CYAN, t, 80)
        _draw_energy_core(s, 201, 90, 12, GHOST_CYAN, t, 80)
        # 幽魂光环
        ghost_alpha = int(60 + 30 * math.sin(t / 150))
        pygame.draw.circle(s, (*GHOST_CYAN[:3], ghost_alpha), (120, 100), 80, 2)

    def draw_tempest():
        """风暴 - 元素领主"""
        # 风暴漩涡
        for i in range(6):
            r = 90 - i * 12
            angle_offset = t / (100 + i * 20)
            pygame.draw.circle(s, (80 + i*15, 100 + i*15, 120 + i*10), (cx, cy), r, 4)
        # 闪电臂
        for i in range(0, 360, 60):
            rad = math.radians(i + t / 30)
            # 主臂
            points = [(cx, cy)]
            length = 90
            for j in range(5):
                jitter = random.randint(-8, 8)
                seg_len = length * (j + 1) / 5
                px = cx + math.cos(rad) * seg_len + jitter
                py = cy + math.sin(rad) * seg_len + jitter
                points.append((int(px), int(py)))
            pygame.draw.lines(s, WIND_BLUE, False, points, 6)
            pygame.draw.lines(s, (200, 230, 255), False, points, 2)
        # 风暴核心
        pygame.draw.circle(s, GRAY, (cx, cy), 35, 4)
        pygame.draw.circle(s, (100, 120, 140), (cx, cy), 30)
        _draw_energy_core(s, cx, cy, 18, WIND_BLUE, t, 60)
        # 云层效果
        for i in range(8):
            cloud_x = cx + math.cos(math.radians(i * 45 + t / 100)) * 70
            cloud_y = cy + math.sin(math.radians(i * 45 + t / 100)) * 70
            pygame.draw.circle(s, (150, 160, 180, 120), (int(cloud_x), int(cloud_y)), 15)
            pygame.draw.circle(s, (180, 190, 210, 100), (int(cloud_x) + 8, int(cloud_y) - 5), 10)

    def draw_void_golem():
        """虚空魔像 - 机械齿轮"""
        # 外层齿轮
        pygame.draw.circle(s, (40, 20, 60), (cx, cy), 95)
        pygame.draw.circle(s, color, (cx, cy), 90, 4)
        # 齿轮齿
        for i in range(12):
            rad = math.radians(i * 30 + t / 50)
            gx = cx + math.cos(rad) * 100
            gy = cy + math.sin(rad) * 100
            tooth_pts = [
                (cx + math.cos(rad) * 85, cy + math.sin(rad) * 85),
                (gx, gy),
                (cx + math.cos(rad + 0.15) * 85, cy + math.sin(rad + 0.15) * 85)
            ]
            pygame.draw.polygon(s, color, [(int(p[0]), int(p[1])) for p in tooth_pts])
        # 内层齿轮（反向旋转）
        pygame.draw.circle(s, (50, 25, 80), (cx, cy), 60, 3)
        for i in range(8):
            rad = math.radians(i * 45 - t / 70)
            gx = cx + math.cos(rad) * 70
            gy = cy + math.sin(rad) * 70
            tooth_pts = [
                (cx + math.cos(rad) * 55, cy + math.sin(rad) * 55),
                (gx, gy),
                (cx + math.cos(rad + 0.2) * 55, cy + math.sin(rad + 0.2) * 55)
            ]
            pygame.draw.polygon(s, (150, 80, 200), [(int(p[0]), int(p[1])) for p in tooth_pts])
        # 能量核心
        core_pulse = 30 + int(10 * math.sin(t / 150))
        pygame.draw.circle(s, (60, 30, 100), (cx, cy), 40)
        _draw_energy_core(s, cx, cy, core_pulse, (200, 100, 255), t)
        # 能量辐射
        for i in range(0, 360, 90):
            rad = math.radians(i + t / 40)
            ex = cx + math.cos(rad) * 110
            ey = cy + math.sin(rad) * 110
            pygame.draw.line(s, (150, 50, 200), (cx, cy), (int(ex), int(ey)), 3)
            pygame.draw.line(s, (220, 150, 255), (cx, cy), (int(ex), int(ey)), 1)
        # 符文
        _draw_energy_ring(s, (cx, cy), 75, (180, 100, 220), t/1000, 6, 2)

    def draw_abyss_queen():
        """星渊女王 - 星体王冠"""
        # 王冠
        crown_pts = [
            (cx - 50, 70), (cx - 70, 35), (cx - 40, 25), (cx - 30, 50),
            (cx, 15), (cx + 30, 50), (cx + 40, 25), (cx + 70, 35), (cx + 50, 70)
        ]
        pygame.draw.polygon(s, (80, 50, 150), crown_pts)
        pygame.draw.polygon(s, color, crown_pts, 3)
        # 王冠宝石
        gem_positions = [(cx - 55, 40), (cx, 25), (cx + 55, 40)]
        for gx, gy in gem_positions:
            pygame.draw.circle(s, (255, 200, 255), (gx, gy), 10)
            pygame.draw.circle(s, (255, 150, 255), (gx, gy), 7)
            pygame.draw.circle(s, WHITE, (gx - 2, gy - 2), 3)
        # 主体
        pygame.draw.circle(s, (60, 30, 120), (cx, cy), 65)
        pygame.draw.circle(s, color, (cx, cy), 60, 3)
        # 星云效果
        for i in range(8):
            nebula_x = cx + math.cos(math.radians(i * 45 + t / 80)) * 45
            nebula_y = cy + math.sin(math.radians(i * 45 + t / 80)) * 45
            pygame.draw.circle(s, (150, 80, 200, 100), (int(nebula_x), int(nebula_y)), 12)
        # 中央星体
        star_pulse = 25 + int(8 * math.sin(t / 200))
        _draw_energy_core(s, cx, cy, star_pulse, (255, 200, 255), t, 180)
        # 环绕星体
        for i in range(5):
            rad = math.radians(i * 72 + t / 40)
            sx = cx + math.cos(rad) * 80
            sy = cy + math.sin(rad) * 80
            pygame.draw.circle(s, (180, 100, 220), (int(sx), int(sy)), 8)
            pygame.draw.circle(s, (220, 150, 255), (int(sx), int(sy)), 5)
            # 轨道
            pygame.draw.circle(s, (*color[:3], 60), (cx, cy), 80, 1)
        # 触手
        for i in range(5):
            tx = cx - 40 + i * 20
            for j in range(4):
                ty = cy + 70 + j * 15 + int(5 * math.sin(t / 100 + i))
                size = 6 - j
                pygame.draw.circle(s, (100, 50, 180), (tx, ty), size)
                pygame.draw.circle(s, color, (tx, ty), size - 1)

    # ===== 10个新Boss绘图函数 - 高质量版 =====
    def draw_fungal_colossus():
        """菌生蟹皇 - 六足巨蟹，背负利维坦头骨"""
        # 半透明深蓝琥珀外壳 - 多层
        pygame.draw.ellipse(s, (20, 60, 100), (cx-85, cy-55, 170, 110))
        pygame.draw.ellipse(s, (30, 80, 120), (cx-80, cy-50, 160, 100))
        pygame.draw.ellipse(s, (40, 100, 140), (cx-75, cy-45, 150, 90))
        # 外壳纹理
        for i in range(5):
            shell_x = cx - 60 + i * 30
            pygame.draw.arc(s, (60, 180, 200), (shell_x - 15, cy - 40, 30, 60), 0.5, 2.5, 2)
        pygame.draw.ellipse(s, (80, 200, 220), (cx-80, cy-50, 160, 100), 3)
        # 六条腿 - 分节关节
        leg_positions = [(-75, 35), (-55, 55), (-35, 65), (35, 65), (55, 55), (75, 35)]
        for lx, ly in leg_positions:
            # 大腿
            thigh_end_x = cx + lx // 2
            thigh_end_y = cy + 25
            pygame.draw.line(s, (50, 120, 160), (cx + lx // 4, cy + 10), (thigh_end_x, thigh_end_y), 8)
            # 小腿
            calf_end_x = cx + lx
            calf_end_y = cy + ly + 45
            pygame.draw.line(s, (40, 100, 140), (thigh_end_x, thigh_end_y), (calf_end_x, calf_end_y), 6)
            # 关节
            pygame.draw.circle(s, (80, 180, 200), (thigh_end_x, thigh_end_y), 6)
            pygame.draw.circle(s, (100, 220, 240), (thigh_end_x, thigh_end_y), 4)
            # 爪尖
            pygame.draw.circle(s, (100, 220, 240), (calf_end_x, calf_end_y), 5)
            pygame.draw.circle(s, (150, 255, 255), (calf_end_x, calf_end_y), 3)
        # 背部利维坦头骨 - 精细骨骼
        skull_y = cy - 75
        pygame.draw.ellipse(s, (180, 180, 170), (cx-45, skull_y, 90, 55))
        pygame.draw.ellipse(s, (220, 220, 210), (cx-40, skull_y+5, 80, 45))
        # 骨骼裂纹
        for i in range(6):
            fx = cx - 30 + i * 12
            pygame.draw.line(s, (160, 160, 150), (fx, skull_y + 10), (fx + 5, skull_y + 35), 1)
        # 眼窝蘑菇炮台
        for side in [-1, 1]:
            eye_x = cx + side * 22
            eye_y = skull_y + 20
            pygame.draw.circle(s, (60, 60, 50), (eye_x, eye_y), 14)
            pygame.draw.circle(s, (80, 200, 120), (eye_x, eye_y), 12)
            # 蘑菇纹理
            pygame.draw.circle(s, (120, 255, 180), (eye_x, eye_y), 8)
            pygame.draw.circle(s, (150, 255, 200), (eye_x - 3, eye_y - 3), 3)
            # 孢子光环
            spore_pulse = int(3 * math.sin(t / 100 + side))
            pygame.draw.circle(s, (100, 255, 150, 100), (eye_x, eye_y), 16 + spore_pulse, 1)
        # 菌丝脉络 - 动态发光
        for i in range(8):
            rad = math.radians(i * 45 + t / 60)
            fx = cx + math.cos(rad) * 55
            fy = cy + math.sin(rad) * 35
            pygame.draw.circle(s, (80, 220, 180), (int(fx), int(fy)), 5)
            pygame.draw.circle(s, (120, 255, 220), (int(fx), int(fy)), 3)
            # 连接线
            pygame.draw.line(s, (60, 180, 150, 150), (cx, cy), (int(fx), int(fy)), 1)
        # 珊瑚晶体关节
        for side in [-1, 1]:
            crystal_pts = [
                (cx + side * 65, cy + 5),
                (cx + side * 55, cy - 25),
                (cx + side * 45, cy + 5),
                (cx + side * 55, cy + 15)
            ]
            pygame.draw.polygon(s, (130, 200, 240), crystal_pts)
            pygame.draw.polygon(s, (180, 230, 255), crystal_pts, 2)
            # 晶体高光
            pygame.draw.line(s, (220, 250, 255), (cx + side * 55, cy - 20), (cx + side * 52, cy - 5), 2)
        # 中央蟹眼
        pygame.draw.circle(s, (40, 80, 100), (cx, cy - 10), 18)
        _draw_energy_core(s, cx, cy - 10, 12, (80, 220, 200), t, 120)

    def draw_dune_reaper():
        """旱海狂鲨 - 沙漠机械蠕虫"""
        worm_cx, worm_cy = 120, 100
        # 身体节段 - 立体效果
        segments = [(70, 0), (65, 25), (58, 50), (50, 75), (42, 100), (34, 125)]
        for i, (seg_w, offset_y) in enumerate(segments):
            seg_y = worm_cy + offset_y
            # 多层外壳
            pygame.draw.ellipse(s, (140, 110, 50), (worm_cx - seg_w // 2 - 3, seg_y - 3, seg_w + 6, 36))
            pygame.draw.ellipse(s, (180, 140, 60), (worm_cx - seg_w // 2, seg_y, seg_w, 30))
            pygame.draw.ellipse(s, (200, 160, 80), (worm_cx - seg_w // 2 + 5, seg_y + 3, seg_w - 10, 24))
            # 青铜拘束环 - 精细
            ring_color = (180, 130, 60)
            pygame.draw.ellipse(s, ring_color, (worm_cx - seg_w // 2 - 4, seg_y + 8, seg_w + 8, 14), 3)
            # 铆钉
            for rivet in range(-2, 3):
                rx = worm_cx + rivet * (seg_w // 5)
                pygame.draw.circle(s, (150, 100, 40), (rx, seg_y + 15), 3)
                pygame.draw.circle(s, (200, 150, 80), (rx, seg_y + 14), 2)
            # 流沙能量光 - 脉动
            glow_alpha = int(150 + 80 * math.sin(t / 80 + i))
            pygame.draw.line(s, (255, 220, 100), (worm_cx - seg_w // 2 + 8, seg_y + 15), 
                           (worm_cx + seg_w // 2 - 8, seg_y + 15), 2)
        # 头部盾构机钻头 - 高精度
        head_y = worm_cy - 25
        pygame.draw.circle(s, (120, 95, 45), (worm_cx, head_y), 48)
        pygame.draw.circle(s, (160, 130, 60), (worm_cx, head_y), 42)
        pygame.draw.circle(s, (140, 110, 50), (worm_cx, head_y), 36)
        # 旋转锯齿
        for i in range(16):
            rad = math.radians(i * 22.5 + t / 20)
            inner_x = worm_cx + math.cos(rad) * 28
            inner_y = head_y + math.sin(rad) * 28
            outer_x = worm_cx + math.cos(rad) * 45
            outer_y = head_y + math.sin(rad) * 45
            # 齿形
            tooth_pts = [
                (inner_x, inner_y),
                (outer_x + math.cos(rad + 0.15) * 5, outer_y + math.sin(rad + 0.15) * 5),
                (outer_x, outer_y),
                (outer_x + math.cos(rad - 0.15) * 5, outer_y + math.sin(rad - 0.15) * 5)
            ]
            pygame.draw.polygon(s, (100, 80, 40), [(int(p[0]), int(p[1])) for p in tooth_pts])
            pygame.draw.polygon(s, (140, 110, 60), [(int(p[0]), int(p[1])) for p in tooth_pts], 1)
        # 中心熔岩核心
        core_pulse = 18 + int(6 * math.sin(t / 100))
        _draw_energy_core(s, worm_cx, head_y, core_pulse, (255, 200, 50), t, 80)
        # 沙尘效果
        for i in range(10):
            dust_x = worm_cx + random.randint(-60, 60)
            dust_y = worm_cy + 130 + random.randint(0, 30)
            pygame.draw.circle(s, (180, 150, 100, 80), (dust_x, dust_y), random.randint(3, 8))

    def draw_plague_empress():
        """歌莉娅女王 - 巨型生化蜜蜂"""
        bee_cx, bee_cy = 120, 115
        # 翅膀 - 高频振动模糊效果
        wing_phase = t / 15
        wing_alpha = 120 + int(60 * math.sin(wing_phase))
        # 上翅膀
        for side in [-1, 1]:
            wing_pts = [
                (bee_cx + side * 25, bee_cy - 30),
                (bee_cx + side * 90, bee_cy - 70),
                (bee_cx + side * 100, bee_cy - 40),
                (bee_cx + side * 80, bee_cy - 10),
                (bee_cx + side * 40, bee_cy - 15)
            ]
            # 多层翅膀
            pygame.draw.polygon(s, (180, 230, 180, wing_alpha), wing_pts)
            pygame.draw.polygon(s, (200, 255, 200, wing_alpha + 30), wing_pts, 2)
            # 翅脉
            pygame.draw.line(s, (150, 200, 150), (bee_cx + side * 30, bee_cy - 25), (bee_cx + side * 85, bee_cy - 50), 1)
            pygame.draw.line(s, (150, 200, 150), (bee_cx + side * 35, bee_cy - 20), (bee_cx + side * 90, bee_cy - 30), 1)
        # 下翅膀
        for side in [-1, 1]:
            wing_pts = [
                (bee_cx + side * 30, bee_cy + 5),
                (bee_cx + side * 75, bee_cy - 20),
                (bee_cx + side * 80, bee_cy + 10),
                (bee_cx + side * 50, bee_cy + 25)
            ]
            pygame.draw.polygon(s, (160, 220, 160, wing_alpha - 20), wing_pts)
            pygame.draw.polygon(s, (180, 240, 180), wing_pts, 1)
        # 胸部 - 毛绒质感
        pygame.draw.ellipse(s, (65, 87, 37), (bee_cx - 55, bee_cy - 35, 110, 70))
        pygame.draw.ellipse(s, (85, 107, 47), (bee_cx - 50, bee_cy - 30, 100, 60))
        # 胸部条纹
        for i in range(4):
            stripe_y = bee_cy - 20 + i * 12
            pygame.draw.line(s, (50, 70, 30), (bee_cx - 40, stripe_y), (bee_cx + 40, stripe_y), 3)
        pygame.draw.ellipse(s, (100, 140, 60), (bee_cx - 50, bee_cy - 30, 100, 60), 2)
        # 腹部 - 透明离心机效果
        pygame.draw.ellipse(s, (40, 70, 25), (bee_cx - 45, bee_cy + 25, 90, 60))
        pygame.draw.ellipse(s, (60, 100, 35, 200), (bee_cx - 40, bee_cy + 30, 80, 50))
        pygame.draw.ellipse(s, (80, 140, 45), (bee_cx - 40, bee_cy + 30, 80, 50), 2)
        # 毒液翻滚 - 动态
        for i in range(6):
            lx = bee_cx - 32 + i * 13
            ly = bee_cy + 45 + int(6 * math.sin(t / 80 + i * 0.8))
            pygame.draw.circle(s, (80, 200, 40), (lx, ly), 6)
            pygame.draw.circle(s, (120, 255, 60), (lx, ly), 4)
            pygame.draw.circle(s, (180, 255, 100), (lx - 1, ly - 1), 2)
        # 腹部发光条纹
        pygame.draw.ellipse(s, (100, 255, 50, 150), (bee_cx - 35, bee_cy + 40, 70, 35), 1)
        # 头部
        pygame.draw.circle(s, (50, 70, 35), (bee_cx, bee_cy - 55), 30)
        pygame.draw.circle(s, (70, 95, 50), (bee_cx, bee_cy - 55), 26)
        # 复眼 - 夜视仪效果
        for side in [-1, 1]:
            eye_x = bee_cx + side * 12
            eye_y = bee_cy - 60
            pygame.draw.circle(s, (200, 30, 30), (eye_x, eye_y), 12)
            pygame.draw.circle(s, (255, 50, 50), (eye_x, eye_y), 9)
            pygame.draw.circle(s, (255, 100, 100), (eye_x, eye_y), 6)
            # 复眼网格
            for j in range(3):
                for k in range(3):
                    fx = eye_x - 6 + j * 6
                    fy = eye_y - 6 + k * 6
                    pygame.draw.circle(s, (180, 20, 20), (fx, fy), 2)
        # 触角
        for side in [-1, 1]:
            pygame.draw.line(s, (80, 100, 50), (bee_cx + side * 8, bee_cy - 80), (bee_cx + side * 25, bee_cy - 100), 2)
            pygame.draw.circle(s, (100, 130, 60), (bee_cx + side * 25, bee_cy - 100), 4)
        # 导弹发射巢
        for side in [-1, 1]:
            for j in range(4):
                missile_x = bee_cx + side * 40
                missile_y = bee_cy - 20 + j * 12
                pygame.draw.circle(s, (80, 80, 85), (missile_x, missile_y), 6)
                pygame.draw.circle(s, (120, 120, 130), (missile_x, missile_y), 4)
                pygame.draw.circle(s, (60, 60, 65), (missile_x, missile_y), 2)
        # 毒刺
        pygame.draw.polygon(s, (60, 80, 30), [(bee_cx, bee_cy + 80), (bee_cx - 8, bee_cy + 95), (bee_cx + 8, bee_cy + 95)])
        pygame.draw.polygon(s, (100, 130, 50), [(bee_cx, bee_cy + 85), (bee_cx - 5, bee_cy + 95), (bee_cx + 5, bee_cy + 95)], 1)

    def draw_flesh_totem():
        """毁灭魔像 - 血肉与机械的融合"""
        golem_cx, golem_cy = 120, 115
        # 主体黑砖 - 多层阴影
        pygame.draw.rect(s, (20, 12, 12), (golem_cx - 65, golem_cy - 85, 130, 170), border_radius=8)
        pygame.draw.rect(s, (35, 22, 22), (golem_cx - 60, golem_cy - 80, 120, 160), border_radius=6)
        pygame.draw.rect(s, (45, 30, 30), (golem_cx - 55, golem_cy - 75, 110, 150), border_radius=4)
        # 砖块纹理
        for row in range(6):
            for col in range(3):
                bx = golem_cx - 50 + col * 35 + (row % 2) * 15
                by = golem_cy - 70 + row * 25
                pygame.draw.rect(s, (55, 40, 40), (bx, by, 30, 20), border_radius=2)
                pygame.draw.rect(s, (40, 28, 28), (bx, by, 30, 20), 1, border_radius=2)
        # 石缝渗血 - 动态
        for i in range(10):
            bx = golem_cx - 45 + (i % 4) * 25
            by = golem_cy - 65 + (i // 4) * 45
            blood_len = 15 + int(8 * math.sin(t / 150 + i))
            pygame.draw.line(s, (120, 20, 20), (bx, by), (bx + 3, by + blood_len), 2)
            pygame.draw.line(s, (180, 40, 40), (bx + 1, by), (bx + 2, by + blood_len - 3), 1)
        # 肌肉纤维缝合线
        for i in range(6):
            fy = golem_cy - 55 + i * 25
            # 缝合线
            pygame.draw.line(s, (160, 45, 45), (golem_cx - 50, fy), (golem_cx + 50, fy), 4)
            # 缝合针脚
            for j in range(6):
                stitch_x = golem_cx - 40 + j * 16
                pygame.draw.line(s, (200, 60, 60), (stitch_x, fy - 5), (stitch_x + 6, fy + 5), 2)
        # 巨大电子眼 - 精细
        eye_y = golem_cy - 25
        pygame.draw.circle(s, (40, 40, 45), (golem_cx, eye_y), 40)
        pygame.draw.circle(s, (60, 60, 70), (golem_cx, eye_y), 36)
        pygame.draw.circle(s, (220, 40, 40), (golem_cx, eye_y), 30)
        pygame.draw.circle(s, (255, 60, 60), (golem_cx, eye_y), 25)
        pygame.draw.circle(s, (200, 20, 20), (golem_cx, eye_y), 18)
        pygame.draw.circle(s, (150, 10, 10), (golem_cx, eye_y), 12)
        # 瞳孔十字准星
        pygame.draw.line(s, (255, 100, 100), (golem_cx - 8, eye_y), (golem_cx + 8, eye_y), 2)
        pygame.draw.line(s, (255, 100, 100), (golem_cx, eye_y - 8), (golem_cx, eye_y + 8), 2)
        # 激光扫描线 - 旋转
        scan_angle = (t / 15) % 360
        rad = math.radians(scan_angle)
        lx = golem_cx + math.cos(rad) * 110
        ly = eye_y + math.sin(rad) * 110
        pygame.draw.line(s, (255, 50, 50, 180), (golem_cx, eye_y), (int(lx), int(ly)), 2)
        pygame.draw.line(s, (255, 150, 150, 100), (golem_cx, eye_y), (int(lx), int(ly)), 4)
        # 眼部光晕
        eye_pulse = int(8 * math.sin(t / 100))
        pygame.draw.circle(s, (255, 50, 50, 60), (golem_cx, eye_y), 45 + eye_pulse, 2)
        # 悬浮石拳 - 精细建模
        fist_y = golem_cy + 25 + int(12 * math.sin(t / 180))
        for side in [-1, 1]:
            fist_x = golem_cx + side * 95
            # 拳头阴影
            pygame.draw.circle(s, (50, 40, 40), (fist_x + 3, fist_y + 3), 32)
            # 拳头主体
            pygame.draw.circle(s, (70, 55, 55), (fist_x, fist_y), 32)
            pygame.draw.circle(s, (90, 70, 70), (fist_x, fist_y), 28)
            pygame.draw.circle(s, (110, 85, 85), (fist_x, fist_y), 22)
            # 指节
            for j in range(4):
                knuckle_angle = math.radians(-30 + j * 20)
                kx = fist_x + math.cos(knuckle_angle) * 25
                ky = fist_y + math.sin(knuckle_angle) * 25
                pygame.draw.circle(s, (60, 45, 45), (int(kx), int(ky)), 8)
                pygame.draw.circle(s, (80, 65, 65), (int(kx), int(ky)), 6)
            # 血肉锁链
            chain_start = (golem_cx + side * 55, golem_cy + 10)
            chain_end = (fist_x, fist_y)
            # 锁链节段
            segments = 8
            for seg in range(segments):
                ratio = seg / segments
                chain_x = chain_start[0] + (chain_end[0] - chain_start[0]) * ratio
                chain_y = chain_start[1] + (chain_end[1] - chain_start[1]) * ratio
                chain_y += int(10 * math.sin(ratio * 3.14 + t / 100)) * (1 - ratio)
                link_color = (180, 50, 50) if seg % 2 == 0 else (140, 35, 35)
                pygame.draw.circle(s, link_color, (int(chain_x), int(chain_y)), 5)
        # 顶部角
        for side in [-1, 1]:
            horn_pts = [
                (golem_cx + side * 40, golem_cy - 80),
                (golem_cx + side * 60, golem_cy - 110),
                (golem_cx + side * 50, golem_cy - 85)
            ]
            pygame.draw.polygon(s, (60, 45, 45), horn_pts)
            pygame.draw.polygon(s, (100, 75, 75), horn_pts, 2)

    def draw_star_serpent():
        """星神游龙 - 宇宙巨蛇"""
        serpent_cx, serpent_cy = 120, 120
        # 蛇形轨迹 - 更精细的节段
        segments = 25
        for i in range(segments):
            anim_t = t / 400
            # 螺旋轨迹
            angle = (i * 14 + anim_t * 25) % 360
            rad = math.radians(angle)
            dist = 25 + i * 3.5
            sx = serpent_cx + math.cos(rad + i * 0.25) * dist
            sy = serpent_cy + math.sin(rad + i * 0.25) * dist * 0.55
            # 节段大小渐变
            seg_size = 14 - i * 0.45
            if seg_size < 3:
                seg_size = 3
            # 橙紫双色渐变
            if i % 2 == 0:
                seg_color = (255, 180 - i * 4, 50 + i * 3)
            else:
                seg_color = (180 - i * 3, 50 + i * 2, 220)
            # 多层绘制
            pygame.draw.circle(s, (15, 8, 25), (int(sx), int(sy)), int(seg_size) + 2)
            pygame.draw.circle(s, seg_color, (int(sx), int(sy)), int(seg_size))
            # 鳞片高光
            pygame.draw.circle(s, (255, 255, 255, 100), (int(sx) - 2, int(sy) - 2), max(1, int(seg_size) - 3))
            # 节段连接线
            if i > 0:
                prev_angle = ((i - 1) * 14 + anim_t * 25) % 360
                prev_rad = math.radians(prev_angle)
                prev_dist = 25 + (i - 1) * 3.5
                prev_x = serpent_cx + math.cos(prev_rad + (i - 1) * 0.25) * prev_dist
                prev_y = serpent_cy + math.sin(prev_rad + (i - 1) * 0.25) * prev_dist * 0.55
                pygame.draw.line(s, (80, 40, 120), (int(prev_x), int(prev_y)), (int(sx), int(sy)), 2)
        # 头部 - 精细
        head_anim = t / 400 * 25
        head_rad = math.radians(head_anim)
        hx = serpent_cx + math.cos(head_rad) * 25
        hy = serpent_cy + math.sin(head_rad) * 14
        # 头部多层
        pygame.draw.circle(s, (40, 15, 65), (int(hx), int(hy)), 24)
        pygame.draw.circle(s, (180, 80, 220), (int(hx), int(hy)), 20)
        pygame.draw.circle(s, (220, 120, 255), (int(hx), int(hy)), 15)
        # 龙眼
        for side in [-1, 1]:
            eye_offset_rad = head_rad + side * 0.4
            eye_x = hx + math.cos(eye_offset_rad) * 10
            eye_y = hy + math.sin(eye_offset_rad) * 10
            pygame.draw.circle(s, (255, 200, 100), (int(eye_x), int(eye_y)), 5)
            pygame.draw.circle(s, (255, 255, 200), (int(eye_x), int(eye_y)), 3)
            pygame.draw.circle(s, BLACK, (int(eye_x), int(eye_y)), 2)
        # 龙须
        for side in [-1, 1]:
            whisker_start_rad = head_rad + side * 0.6
            ws_x = hx + math.cos(whisker_start_rad) * 18
            ws_y = hy + math.sin(whisker_start_rad) * 18
            we_x = hx + math.cos(whisker_start_rad) * 35 + side * 5
            we_y = hy + math.sin(whisker_start_rad) * 35
            pygame.draw.line(s, (200, 100, 255), (int(ws_x), int(ws_y)), (int(we_x), int(we_y)), 2)
        # 星云气体效果 - 多层
        for i in range(12):
            nebula_rad = math.radians(i * 30 + t / 80)
            nx = serpent_cx + math.cos(nebula_rad) * 75
            ny = serpent_cy + math.sin(nebula_rad) * 45
            nebula_size = 10 + int(4 * math.sin(t / 120 + i))
            pygame.draw.circle(s, (100, 50, 150, 60), (int(nx), int(ny)), nebula_size)
            pygame.draw.circle(s, (150, 80, 200, 40), (int(nx), int(ny)), nebula_size + 4)
        # 星尘轨迹
        for i in range(8):
            dust_angle = (i * 45 + t / 50) % 360
            dust_rad = math.radians(dust_angle)
            dust_dist = 50 + random.randint(0, 30)
            dx = serpent_cx + math.cos(dust_rad) * dust_dist
            dy = serpent_cy + math.sin(dust_rad) * dust_dist * 0.6
            pygame.draw.circle(s, (255, 200, 100), (int(dx), int(dy)), 2)
        # 能量环
        _draw_energy_ring(s, (serpent_cx, serpent_cy), 95, (180, 100, 220), t / 1000, 8, 1)

    def draw_exo_ares():
        """终焉巨械·阿瑞斯 - RGB霓虹机械骷髅"""
        ares_cx, ares_cy = 120, 120
        # RGB霓虹相位
        rgb_phase = t / 80
        r_val = int(127 + 127 * math.sin(math.radians(rgb_phase * 60)))
        g_val = int(127 + 127 * math.sin(math.radians(rgb_phase * 60 + 120)))
        b_val = int(127 + 127 * math.sin(math.radians(rgb_phase * 60 + 240)))
        rgb_color = (r_val, g_val, b_val)
        # RGB背景光晕
        for i in range(4):
            pygame.draw.circle(s, (*rgb_color, 20 + i * 10), (ares_cx, ares_cy), 105 - i * 15)
        # 骷髅核心 - 精细建模
        pygame.draw.circle(s, (180, 180, 200), (ares_cx, ares_cy), 45)
        pygame.draw.circle(s, (200, 200, 220), (ares_cx, ares_cy), 42)
        pygame.draw.circle(s, (40, 40, 50), (ares_cx, ares_cy), 38)
        pygame.draw.circle(s, (50, 50, 65), (ares_cx, ares_cy), 34)
        # 骷髅面部细节
        # 眼眶
        for side in [-1, 1]:
            eye_x = ares_cx + side * 14
            eye_y = ares_cy - 8
            pygame.draw.circle(s, (30, 30, 40), (eye_x, eye_y), 12)
            pygame.draw.circle(s, rgb_color, (eye_x, eye_y), 9)
            pygame.draw.circle(s, (255, 255, 255), (eye_x, eye_y), 5)
            # 眼部光芒
            for ray in range(4):
                ray_rad = math.radians(ray * 90 + t / 30)
                rx = eye_x + math.cos(ray_rad) * 15
                ry = eye_y + math.sin(ray_rad) * 15
                pygame.draw.line(s, rgb_color, (eye_x, eye_y), (int(rx), int(ry)), 1)
        # 鼻腔
        pygame.draw.polygon(s, (25, 25, 35), [(ares_cx, ares_cy + 5), (ares_cx - 6, ares_cy + 18), (ares_cx + 6, ares_cy + 18)])
        # 牙齿
        for i in range(6):
            tx = ares_cx - 12 + i * 5
            pygame.draw.rect(s, (200, 200, 210), (tx, ares_cy + 22, 4, 8), border_radius=1)
        # 下颚
        pygame.draw.arc(s, (180, 180, 190), (ares_cx - 25, ares_cy + 15, 50, 30), 3.14, 6.28, 2)
        # 四条机械触手 - 精细
        arm_data = [
            (0, "高斯炮", (255, 120, 60)),
            (90, "特斯拉", (80, 180, 255)),
            (180, "激光刀", (255, 60, 80)),
            (270, "等离子", (60, 255, 120))
        ]
        for base_angle, name, arm_color in arm_data:
            ang = math.radians(base_angle + t / 40)
            # 触手关节
            joint1_x = ares_cx + math.cos(ang) * 45
            joint1_y = ares_cy + math.sin(ang) * 45
            joint2_x = ares_cx + math.cos(ang) * 75
            joint2_y = ares_cy + math.sin(ang) * 75
            end_x = ares_cx + math.cos(ang) * 95
            end_y = ares_cy + math.sin(ang) * 95
            # 触手段
            pygame.draw.line(s, (160, 160, 180), (ares_cx, ares_cy), (int(joint1_x), int(joint1_y)), 8)
            pygame.draw.line(s, (140, 140, 160), (int(joint1_x), int(joint1_y)), (int(joint2_x), int(joint2_y)), 6)
            pygame.draw.line(s, (120, 120, 140), (int(joint2_x), int(joint2_y)), (int(end_x), int(end_y)), 4)
            # 关节球
            pygame.draw.circle(s, (180, 180, 200), (int(joint1_x), int(joint1_y)), 8)
            pygame.draw.circle(s, rgb_color, (int(joint1_x), int(joint1_y)), 5)
            pygame.draw.circle(s, (180, 180, 200), (int(joint2_x), int(joint2_y)), 6)
            pygame.draw.circle(s, rgb_color, (int(joint2_x), int(joint2_y)), 4)
            # 末端武器
            pygame.draw.circle(s, arm_color, (int(end_x), int(end_y)), 18)
            pygame.draw.circle(s, (255, 255, 255), (int(end_x), int(end_y)), 12)
            _draw_energy_core(s, int(end_x), int(end_y), 8, arm_color, t, 60)
            # 武器光环
            pygame.draw.circle(s, (*arm_color, 80), (int(end_x), int(end_y)), 22, 1)
        # 中央能量核心
        _draw_energy_core(s, ares_cx, ares_cy, 15, rgb_color, t, 100)
        # 外圈装饰环
        _draw_energy_ring(s, (ares_cx, ares_cy), 55, rgb_color, t / 1000, 12, 2)

    def draw_radiance_goddess():
        """亵渎天神·普罗维登斯 - 神圣熔岩女神"""
        goddess_cx, goddess_cy = 120, 120
        # 金色粒子尘埃背景 - 更多粒子
        for i in range(30):
            particle_angle = (i * 12 + t / 50) % 360
            particle_rad = math.radians(particle_angle)
            particle_dist = 40 + (i * 3) % 60
            px = goddess_cx + math.cos(particle_rad) * particle_dist
            py = goddess_cy + math.sin(particle_rad) * particle_dist
            particle_size = 2 + (i % 3)
            pygame.draw.circle(s, (255, 215, 0, 120), (int(px), int(py)), particle_size)
        # 三对彩色玻璃晶体翼 - 精细
        wing_colors = [
            ((255, 100, 100), (255, 180, 180)),  # 红翼
            ((100, 255, 100), (180, 255, 180)),  # 绿翼
            ((100, 100, 255), (180, 180, 255))   # 蓝翼
        ]
        for i, (wc, wc_light) in enumerate(wing_colors):
            wing_offset = i * 18
            wing_wave = int(8 * math.sin(t / 100 + i * 0.5))
            for side in [-1, 1]:
                # 翼形状
                pts = [
                    (goddess_cx + side * 22, goddess_cy - wing_offset),
                    (goddess_cx + side * 85, goddess_cy - 50 - wing_offset + wing_wave),
                    (goddess_cx + side * 95, goddess_cy - 30 - wing_offset + wing_wave),
                    (goddess_cx + side * 80, goddess_cy + 15 - wing_offset),
                    (goddess_cx + side * 55, goddess_cy + 25 - wing_offset)
                ]
                # 多层翼
                pygame.draw.polygon(s, (*wc, 120), pts)
                pygame.draw.polygon(s, (*wc, 180), pts, 2)
                # 翼脉
                pygame.draw.line(s, wc_light, pts[0], pts[1], 1)
                pygame.draw.line(s, wc_light, pts[0], pts[2], 1)
                pygame.draw.line(s, wc_light, pts[0], pts[3], 1)
                # 翼尖宝石
                pygame.draw.circle(s, wc_light, (int(pts[2][0]), int(pts[2][1])), 4)
        # 主体 - 熔岩心脏
        pygame.draw.circle(s, (200, 80, 0), (goddess_cx, goddess_cy), 42)
        pygame.draw.circle(s, (255, 120, 20), (goddess_cx, goddess_cy), 38)
        pygame.draw.circle(s, (255, 160, 50), (goddess_cx, goddess_cy), 32)
        # 熔岩核心脉动
        core_pulse = 22 + int(8 * math.sin(t / 120))
        _draw_energy_core(s, goddess_cx, goddess_cy, core_pulse, (255, 200, 80), t, 100)
        # 熔岩纹理
        for i in range(8):
            lava_rad = math.radians(i * 45 + t / 60)
            lx1 = goddess_cx + math.cos(lava_rad) * 15
            ly1 = goddess_cy + math.sin(lava_rad) * 15
            lx2 = goddess_cx + math.cos(lava_rad) * 35
            ly2 = goddess_cy + math.sin(lava_rad) * 35
            pygame.draw.line(s, (255, 100, 0), (int(lx1), int(ly1)), (int(lx2), int(ly2)), 2)
        # 宗教浮雕光环
        for i in range(3):
            ring_r = 55 + i * 12
            pygame.draw.circle(s, (255, 215, 0), (goddess_cx, goddess_cy), ring_r, 2 - i // 2)
        # 神圣符文
        for i in range(6):
            rune_rad = math.radians(i * 60 + t / 80)
            rx = goddess_cx + math.cos(rune_rad) * 65
            ry = goddess_cy + math.sin(rune_rad) * 65
            # 符文形状
            pygame.draw.polygon(s, (255, 215, 0), [
                (int(rx), int(ry) - 8),
                (int(rx) + 5, int(ry)),
                (int(rx), int(ry) + 8),
                (int(rx) - 5, int(ry))
            ])
            pygame.draw.polygon(s, (255, 255, 200), [
                (int(rx), int(ry) - 8),
                (int(rx) + 5, int(ry)),
                (int(rx), int(ry) + 8),
                (int(rx) - 5, int(ry))
            ], 1)
        # 头冠
        crown_y = goddess_cy - 55
        pygame.draw.polygon(s, (255, 200, 50), [
            (goddess_cx - 30, crown_y + 15),
            (goddess_cx - 40, crown_y),
            (goddess_cx - 20, crown_y - 10),
            (goddess_cx, crown_y - 20),
            (goddess_cx + 20, crown_y - 10),
            (goddess_cx + 40, crown_y),
            (goddess_cx + 30, crown_y + 15)
        ])
        pygame.draw.polygon(s, (255, 255, 200), [
            (goddess_cx - 30, crown_y + 15),
            (goddess_cx - 40, crown_y),
            (goddess_cx - 20, crown_y - 10),
            (goddess_cx, crown_y - 20),
            (goddess_cx + 20, crown_y - 10),
            (goddess_cx + 40, crown_y),
            (goddess_cx + 30, crown_y + 15)
        ], 2)
        # 头冠宝石
        pygame.draw.circle(s, (255, 100, 100), (goddess_cx, crown_y - 15), 6)
        pygame.draw.circle(s, (255, 200, 200), (goddess_cx, crown_y - 15), 4)

    def draw_dimension_devourer():
        """维度之噬·奥罗 - 虚空巨蛇"""
        devourer_cx, devourer_cy = 120, 95
        # 空间裂隙背景
        for i in range(6):
            rift_x = devourer_cx - 100 + i * 40
            pygame.draw.line(s, (60, 0, 100, 80), (rift_x, 0), (rift_x + 15, 240), 2)
            pygame.draw.line(s, (100, 0, 160, 40), (rift_x + 2, 0), (rift_x + 17, 240), 1)
        # 身体节段 - Vantablack装甲
        segments = [
            (50, 0), (48, 22), (44, 44), (40, 66), (35, 88), 
            (30, 110), (24, 132), (18, 154)
        ]
        for i, (seg_w, offset_y) in enumerate(segments):
            seg_y = devourer_cy + offset_y
            # 多层黑甲
            pygame.draw.ellipse(s, (3, 0, 8), (devourer_cx - seg_w // 2 - 2, seg_y - 2, seg_w + 4, 28))
            pygame.draw.ellipse(s, (8, 2, 15), (devourer_cx - seg_w // 2, seg_y, seg_w, 24))
            pygame.draw.ellipse(s, (12, 4, 22), (devourer_cx - seg_w // 2 + 3, seg_y + 3, seg_w - 6, 18))
            # 紫色能量缝隙
            pygame.draw.line(s, (150, 50, 200), (devourer_cx - seg_w // 2 + 5, seg_y + 12), 
                           (devourer_cx + seg_w // 2 - 5, seg_y + 12), 1)
            # 紫水晶倒刺
            if i % 2 == 0:
                for side in [-1, 1]:
                    spike_x = devourer_cx + side * (seg_w // 2 + 8)
                    spike_pts = [
                        (spike_x, seg_y + 12),
                        (spike_x + side * 12, seg_y + 6),
                        (spike_x + side * 8, seg_y + 12),
                        (spike_x + side * 12, seg_y + 18)
                    ]
                    pygame.draw.polygon(s, (130, 40, 180), spike_pts)
                    pygame.draw.polygon(s, (180, 80, 220), spike_pts, 1)
                    # 晶体高光
                    pygame.draw.line(s, (220, 150, 255), (spike_x + side * 10, seg_y + 8), 
                                   (spike_x + side * 8, seg_y + 14), 1)
        # 头部 - 颚部紫色漩涡
        head_y = devourer_cy - 35
        pygame.draw.circle(s, (5, 0, 12), (devourer_cx, head_y), 50)
        pygame.draw.circle(s, (10, 2, 20), (devourer_cx, head_y), 45)
        pygame.draw.circle(s, (15, 4, 28), (devourer_cx, head_y), 40)
        # 漩涡效果 - 多层旋转
        for layer in range(6):
            vortex_r = 38 - layer * 6
            for i in range(5):
                vortex_angle = i * 72 + t / (20 + layer * 5) + layer * 30
                vortex_rad = math.radians(vortex_angle)
                vx = devourer_cx + math.cos(vortex_rad) * vortex_r * 0.4
                vy = head_y + math.sin(vortex_rad) * vortex_r * 0.4
                arc_color = (100 + layer * 20, 0, 180 + layer * 10)
                pygame.draw.circle(s, arc_color, (int(vx), int(vy)), vortex_r, 2)
        # 中心奇点
        singularity_pulse = 12 + int(5 * math.sin(t / 80))
        pygame.draw.circle(s, (180, 0, 255), (devourer_cx, head_y), singularity_pulse)
        pygame.draw.circle(s, (220, 100, 255), (devourer_cx, head_y), singularity_pulse - 4)
        pygame.draw.circle(s, (255, 200, 255), (devourer_cx, head_y), singularity_pulse - 8)
        # 颚牙
        for i in range(8):
            tooth_angle = i * 45 + t / 40
            tooth_rad = math.radians(tooth_angle)
            tx = devourer_cx + math.cos(tooth_rad) * 42
            ty = head_y + math.sin(tooth_rad) * 42
            tooth_pts = [
                (int(tx), int(ty)),
                (int(devourer_cx + math.cos(tooth_rad) * 55), int(head_y + math.sin(tooth_rad) * 55)),
                (int(devourer_cx + math.cos(tooth_rad + 0.2) * 42), int(head_y + math.sin(tooth_rad + 0.2) * 42))
            ]
            pygame.draw.polygon(s, (20, 5, 35), tooth_pts)
            pygame.draw.polygon(s, (80, 20, 120), tooth_pts, 1)
        # 虚空光环
        pygame.draw.circle(s, (100, 0, 160, 60), (devourer_cx, head_y), 58, 2)

    def draw_infernal_dragon():
        """暴君犽戎 - 炼狱龙神"""
        dragon_cx, dragon_cy = 120, 115
        # 炼狱火柱背景 - 动态
        fire_phase = t / 30
        for side in [-1, 1]:
            fire_x = dragon_cx + side * 105
            for i in range(8):
                fire_y = i * 30
                fire_offset = int(10 * math.sin(fire_phase + i * 0.5))
                fire_w = 25 + int(10 * math.sin(fire_phase + i))
                pygame.draw.ellipse(s, (255, 100, 0, 120), (fire_x - fire_w // 2 + fire_offset, fire_y, fire_w, 35))
                pygame.draw.ellipse(s, (255, 180, 50, 80), (fire_x - fire_w // 2 + 5 + fire_offset, fire_y + 5, fire_w - 10, 25))
        # 龙翼 - 日耀火焰
        wing_flicker = int(15 * math.sin(t / 40))
        for side in [-1, 1]:
            # 翼骨
            for bone in range(4):
                bone_angle = -30 + bone * 20
                bone_rad = math.radians(bone_angle * side + 90)
                bone_len = 70 - bone * 8
                bx = dragon_cx + side * 45
                by = dragon_cy - 20
                bone_end_x = bx + math.cos(bone_rad) * bone_len * side
                bone_end_y = by + math.sin(bone_rad) * bone_len + wing_flicker * (bone / 4)
                pygame.draw.line(s, (180, 140, 50), (bx, by), (int(bone_end_x), int(bone_end_y)), 3)
            # 翼膜
            wing_pts = [
                (dragon_cx + side * 35, dragon_cy - 25),
                (dragon_cx + side * 95, dragon_cy - 55 + wing_flicker),
                (dragon_cx + side * 105, dragon_cy - 20 + wing_flicker),
                (dragon_cx + side * 90, dragon_cy + 25),
                (dragon_cx + side * 50, dragon_cy + 15)
            ]
            pygame.draw.polygon(s, (255, 140, 30, 150), wing_pts)
            pygame.draw.polygon(s, (255, 200, 80), wing_pts, 2)
            # 翼膜火焰纹理
            for i in range(3):
                fx = dragon_cx + side * (55 + i * 15)
                fy = dragon_cy - 30 + i * 15 + wing_flicker * (i / 3)
                pygame.draw.circle(s, (255, 220, 100), (int(fx), int(fy)), 5)
        # 龙身 - 鳞片纹理
        pygame.draw.ellipse(s, (150, 25, 25), (dragon_cx - 55, dragon_cy - 45, 110, 90))
        pygame.draw.ellipse(s, (180, 35, 35), (dragon_cx - 50, dragon_cy - 40, 100, 80))
        # 鳞片
        for row in range(4):
            for col in range(5):
                sx = dragon_cx - 35 + col * 18
                sy = dragon_cy - 30 + row * 18
                pygame.draw.ellipse(s, (200, 45, 45), (sx, sy, 15, 12))
                pygame.draw.ellipse(s, (220, 80, 80), (sx + 2, sy + 1, 11, 8))
        # 金色机械骨骼
        for i in range(5):
            by = dragon_cy - 32 + i * 16
            pygame.draw.line(s, (200, 160, 40), (dragon_cx - 42, by), (dragon_cx + 42, by), 3)
            pygame.draw.line(s, (255, 220, 100), (dragon_cx - 40, by + 1), (dragon_cx + 40, by + 1), 1)
        # 泰斯拉反应堆心脏
        core_pulse = 22 + int(8 * math.sin(t / 80))
        pygame.draw.circle(s, (200, 160, 30), (dragon_cx, dragon_cy), 28)
        _draw_energy_core(s, dragon_cx, dragon_cy, core_pulse, (255, 220, 80), t, 60)
        # 电弧
        for i in range(4):
            arc_angle = i * 90 + t / 20
            arc_rad = math.radians(arc_angle)
            arc_end_x = dragon_cx + math.cos(arc_rad) * 40
            arc_end_y = dragon_cy + math.sin(arc_rad) * 40
            pygame.draw.line(s, (255, 255, 150), (dragon_cx, dragon_cy), (int(arc_end_x), int(arc_end_y)), 2)
        # 龙头
        head_y = dragon_cy - 65
        pygame.draw.polygon(s, (180, 35, 35), [
            (dragon_cx, head_y - 30),
            (dragon_cx - 35, head_y + 15),
            (dragon_cx - 25, head_y + 25),
            (dragon_cx + 25, head_y + 25),
            (dragon_cx + 35, head_y + 15)
        ])
        pygame.draw.polygon(s, (220, 60, 60), [
            (dragon_cx, head_y - 25),
            (dragon_cx - 30, head_y + 12),
            (dragon_cx - 22, head_y + 22),
            (dragon_cx + 22, head_y + 22),
            (dragon_cx + 30, head_y + 12)
        ], 2)
        # 龙角
        for side in [-1, 1]:
            horn_pts = [
                (dragon_cx + side * 25, head_y + 5),
                (dragon_cx + side * 40, head_y - 20),
                (dragon_cx + side * 30, head_y + 10)
            ]
            pygame.draw.polygon(s, (200, 160, 50), horn_pts)
            pygame.draw.polygon(s, (255, 220, 100), horn_pts, 1)
        # 龙眼
        for side in [-1, 1]:
            eye_x = dragon_cx + side * 12
            eye_y = head_y + 5
            pygame.draw.circle(s, (255, 200, 50), (eye_x, eye_y), 8)
            pygame.draw.circle(s, (255, 255, 150), (eye_x, eye_y), 5)
            pygame.draw.circle(s, (200, 50, 50), (eye_x, eye_y), 3)
        # 龙嘴火焰
        for i in range(3):
            flame_x = dragon_cx - 10 + i * 10
            flame_y = head_y + 30
            flame_h = 15 + int(8 * math.sin(t / 50 + i))
            pygame.draw.polygon(s, (255, 150, 50), [
                (flame_x, flame_y),
                (flame_x - 5, flame_y + flame_h),
                (flame_x + 5, flame_y + flame_h)
            ])
        # 龙尾
        tail_start_y = dragon_cy + 45
        for i in range(5):
            tail_y = tail_start_y + i * 12
            tail_w = 30 - i * 5
            pygame.draw.ellipse(s, (160, 30, 30), (dragon_cx - tail_w // 2, tail_y, tail_w, 15))
            if i == 4:
                # 尾刺
                pygame.draw.polygon(s, (200, 50, 50), [
                    (dragon_cx, tail_y + 15),
                    (dragon_cx - 8, tail_y + 30),
                    (dragon_cx + 8, tail_y + 30)
                ])

    def draw_entropy_avatar():
        """熵之化身·终末王座 - 宇宙真理之神"""
        avatar_cx, avatar_cy = 120, 125
        # 苍白巨人躯干 - 大理石质感
        pygame.draw.ellipse(s, (200, 200, 210), (avatar_cx - 65, avatar_cy - 85, 130, 160))
        pygame.draw.ellipse(s, (220, 220, 230), (avatar_cx - 60, avatar_cy - 80, 120, 150))
        pygame.draw.ellipse(s, (235, 235, 245), (avatar_cx - 55, avatar_cy - 75, 110, 140))
        # 裂痕纹理 - 更精细
        for i in range(12):
            fx = avatar_cx - 45 + (i % 4) * 25
            fy = avatar_cy - 65 + (i // 4) * 40
            # 主裂纹
            pygame.draw.line(s, (180, 180, 190), (fx, fy), (fx + random.randint(5, 15), fy + random.randint(10, 25)), 1)
            # 分支裂纹
            if i % 3 == 0:
                pygame.draw.line(s, (190, 190, 200), (fx + 5, fy + 8), (fx + 12, fy + 5), 1)
        # 胸口真理之眼 - 主眼
        chest_eye_y = avatar_cy - 5
        pygame.draw.circle(s, (200, 200, 210), (avatar_cx, chest_eye_y), 32)
        pygame.draw.circle(s, (255, 255, 255), (avatar_cx, chest_eye_y), 28)
        pygame.draw.circle(s, (255, 220, 220), (avatar_cx, chest_eye_y), 22)
        pygame.draw.circle(s, (255, 120, 120), (avatar_cx, chest_eye_y), 16)
        pygame.draw.circle(s, (220, 40, 40), (avatar_cx, chest_eye_y), 10)
        pygame.draw.circle(s, BLACK, (avatar_cx, chest_eye_y), 5)
        # 瞳孔十字
        pygame.draw.line(s, (180, 20, 20), (avatar_cx - 8, chest_eye_y), (avatar_cx + 8, chest_eye_y), 2)
        pygame.draw.line(s, (180, 20, 20), (avatar_cx, chest_eye_y - 8), (avatar_cx, chest_eye_y + 8), 2)
        # 眼部光晕
        eye_pulse = int(6 * math.sin(t / 100))
        pygame.draw.circle(s, (255, 100, 100, 80), (avatar_cx, chest_eye_y), 35 + eye_pulse, 2)
        # 额头真理之眼
        forehead_y = avatar_cy - 65
        pygame.draw.circle(s, (200, 200, 210), (avatar_cx, forehead_y), 24)
        pygame.draw.circle(s, (255, 255, 255), (avatar_cx, forehead_y), 20)
        pygame.draw.circle(s, (255, 230, 180), (avatar_cx, forehead_y), 15)
        pygame.draw.circle(s, (255, 215, 0), (avatar_cx, forehead_y), 10)
        pygame.draw.circle(s, BLACK, (avatar_cx, forehead_y), 5)
        # 智慧光芒
        for i in range(8):
            ray_rad = math.radians(i * 45 + t / 60)
            rx = avatar_cx + math.cos(ray_rad) * 30
            ry = forehead_y + math.sin(ray_rad) * 30
            pygame.draw.line(s, (255, 215, 0, 150), (avatar_cx, forehead_y), (int(rx), int(ry)), 1)
        # 手臂与手心真理之眼
        for side in [-1, 1]:
            # 手臂
            shoulder_x = avatar_cx + side * 50
            shoulder_y = avatar_cy - 30
            elbow_x = avatar_cx + side * 75
            elbow_y = avatar_cy + 5
            hand_x = avatar_cx + side * 90
            hand_y = avatar_cy + 25
            # 上臂
            pygame.draw.line(s, (210, 210, 220), (shoulder_x, shoulder_y), (elbow_x, elbow_y), 12)
            pygame.draw.line(s, (230, 230, 240), (shoulder_x + side, shoulder_y), (elbow_x + side, elbow_y), 8)
            # 下臂
            pygame.draw.line(s, (210, 210, 220), (elbow_x, elbow_y), (hand_x, hand_y), 10)
            pygame.draw.line(s, (230, 230, 240), (elbow_x + side, elbow_y), (hand_x + side, hand_y), 6)
            # 肘关节
            pygame.draw.circle(s, (220, 220, 230), (elbow_x, elbow_y), 8)
            # 手心真理之眼
            pygame.draw.circle(s, (200, 200, 210), (hand_x, hand_y), 18)
            pygame.draw.circle(s, (255, 255, 255), (hand_x, hand_y), 15)
            pygame.draw.circle(s, (255, 230, 180), (hand_x, hand_y), 11)
            pygame.draw.circle(s, (255, 215, 0), (hand_x, hand_y), 7)
            pygame.draw.circle(s, BLACK, (hand_x, hand_y), 3)
            # 手心光晕
            pygame.draw.circle(s, (255, 215, 0, 60), (hand_x, hand_y), 22, 1)
        # 光纤数据线触手
        for i in range(8):
            base_x = avatar_cx - 55 + i * 16
            base_y = avatar_cy + 55
            # 曲线触手
            data_points = []
            for j in range(6):
                tx = base_x + (i - 4) * j * 1.5 + int(5 * math.sin(t / 80 + i + j * 0.3))
                ty = base_y + j * 18
                data_points.append((int(tx), int(ty)))
            # 绘制触手
            if len(data_points) > 1:
                pygame.draw.lines(s, (80, 180, 240), False, data_points, 3)
                pygame.draw.lines(s, (150, 220, 255), False, data_points, 1)
            # 数据流光点
            flow_offset = int((t / 50 + i * 10) % 6)
            if flow_offset < len(data_points):
                pygame.draw.circle(s, (200, 255, 255), data_points[flow_offset], 4)
                pygame.draw.circle(s, (255, 255, 255), data_points[flow_offset], 2)
        # 真理光环
        for ring in range(3):
            ring_r = 100 - ring * 15
            ring_alpha = 100 - ring * 25
            pygame.draw.circle(s, (255, 215, 0, ring_alpha), (avatar_cx, avatar_cy - 20), ring_r, 1)
        # 头部装饰 - 光环
        halo_y = avatar_cy - 90
        pygame.draw.ellipse(s, (255, 215, 0), (avatar_cx - 40, halo_y - 8, 80, 16), 2)
        pygame.draw.ellipse(s, (255, 240, 180), (avatar_cx - 38, halo_y - 6, 76, 12), 1)

    def draw_sonic_banshee():
        """绝音夜煞 - 音波恐怖生物"""
        banshee_cx, banshee_cy = 120, 120
        # 漆黑吸音绒毛躯体
        for layer in range(20):
            fur_x = banshee_cx - 55 + random.randint(-3, 3)
            fur_y = banshee_cy - 60 + layer * 6
            fur_w = 110 - abs(layer - 10) * 4
            # 绒毛层
            pygame.draw.ellipse(s, (15, 10, 20), (fur_x, fur_y, fur_w, 12))
            # 绒毛纹理
            for f in range(5):
                fx = fur_x + 10 + f * 18
                pygame.draw.line(s, (8, 5, 12), (fx, fur_y), (fx + random.randint(-3, 3), fur_y + 10), 1)
        # 胸腔骨质扬声器阵列
        speaker_y = banshee_cy - 10
        for row in range(3):
            for col in range(3):
                sp_x = banshee_cx - 30 + col * 30
                sp_y = speaker_y + row * 25
                # 骨质外壳
                pygame.draw.circle(s, (220, 210, 190), (sp_x, sp_y), 14)
                pygame.draw.circle(s, (180, 170, 150), (sp_x, sp_y), 12)
                # 扬声器膜
                pygame.draw.circle(s, (40, 30, 50), (sp_x, sp_y), 10)
                pygame.draw.circle(s, (60, 50, 70), (sp_x, sp_y), 6)
                pygame.draw.circle(s, (100, 90, 110), (sp_x, sp_y), 3)
                # 振动波纹
                pulse = int(3 * math.sin(t / 50 + row + col))
                if pulse > 0:
                    pygame.draw.circle(s, (150, 50, 200), (sp_x, sp_y), 12 + pulse, 1)
        # 无脸大嘴 - 头部
        head_y = banshee_cy - 75
        pygame.draw.ellipse(s, (20, 15, 25), (banshee_cx - 40, head_y - 25, 80, 55))
        # 巨大嘴巴
        mouth_open = int(10 * abs(math.sin(t / 80)))
        mouth_points = [
            (banshee_cx - 35, head_y - 5),
            (banshee_cx - 25, head_y + 15 + mouth_open),
            (banshee_cx, head_y + 25 + mouth_open),
            (banshee_cx + 25, head_y + 15 + mouth_open),
            (banshee_cx + 35, head_y - 5),
            (banshee_cx + 20, head_y),
            (banshee_cx, head_y + 5),
            (banshee_cx - 20, head_y),
        ]
        pygame.draw.polygon(s, (80, 0, 20), mouth_points)
        pygame.draw.polygon(s, (120, 20, 40), mouth_points, 2)
        # 锯齿状牙齿
        for i in range(7):
            tooth_x = banshee_cx - 30 + i * 10
            pygame.draw.polygon(s, (240, 230, 220), [
                (tooth_x, head_y - 3),
                (tooth_x + 5, head_y + 10),
                (tooth_x + 10, head_y - 3)
            ])
        # 声波翅膀
        for side in [-1, 1]:
            wing_x = banshee_cx + side * 70
            for w in range(5):
                wave_y = banshee_cy - 40 + w * 20
                wave_amp = 15 + w * 3
                points = []
                for p in range(10):
                    px = wing_x + side * p * 8
                    py = wave_y + int(wave_amp * math.sin(t / 60 + p * 0.5 + w))
                    points.append((int(px), int(py)))
                if len(points) > 1:
                    pygame.draw.lines(s, (100, 50, 150), False, points, 2)
        # 音波脉冲光环
        for ring in range(4):
            ring_r = 50 + ring * 20 + int(10 * math.sin(t / 40 + ring))
            ring_alpha = 150 - ring * 30
            pygame.draw.circle(s, (150, 50, 200, ring_alpha), (banshee_cx, banshee_cy), ring_r, 2)

    def draw_prism_overlord():
        """棱镜核心 - 光学几何体"""
        prism_cx, prism_cy = 120, 120
        # 正二十面体核心 - 简化为多边形表示
        core_r = 45
        # 外层幻彩镜面
        for i in range(20):
            angle1 = math.radians(i * 18 + t / 100)
            angle2 = math.radians((i + 1) * 18 + t / 100)
            # 渐变色
            hue = (i * 18 + int(t / 50)) % 360
            rgb = pygame.Color(0)
            rgb.hsva = (hue, 100, 100, 100)
            r1 = core_r + int(5 * math.sin(t / 60 + i))
            x1 = prism_cx + int(r1 * math.cos(angle1))
            y1 = prism_cy + int(r1 * math.sin(angle1))
            x2 = prism_cx + int(r1 * math.cos(angle2))
            y2 = prism_cy + int(r1 * math.sin(angle2))
            pygame.draw.line(s, rgb, (x1, y1), (x2, y2), 3)
            # 内层填充
            pygame.draw.polygon(s, (rgb.r // 2, rgb.g // 2, rgb.b // 2, 100), [
                (prism_cx, prism_cy), (x1, y1), (x2, y2)
            ])
        # 内封雷电球
        lightning_r = 25
        pygame.draw.circle(s, (200, 220, 255), (prism_cx, prism_cy), lightning_r)
        pygame.draw.circle(s, (255, 255, 255), (prism_cx, prism_cy), lightning_r - 5)
        # 雷电效果
        for bolt in range(6):
            bolt_angle = math.radians(bolt * 60 + t / 30)
            points = [(prism_cx, prism_cy)]
            for seg in range(4):
                seg_r = 5 + seg * 6
                seg_angle = bolt_angle + random.uniform(-0.3, 0.3)
                bx = prism_cx + int(seg_r * math.cos(seg_angle))
                by = prism_cy + int(seg_r * math.sin(seg_angle))
                points.append((bx, by))
            pygame.draw.lines(s, (100, 150, 255), False, points, 2)
            pygame.draw.lines(s, (200, 220, 255), False, points, 1)
        # 6块浮游折射盾
        for i in range(6):
            shield_angle = math.radians(i * 60 + t / 80)
            shield_dist = 75 + int(10 * math.sin(t / 50 + i))
            shield_x = prism_cx + int(shield_dist * math.cos(shield_angle))
            shield_y = prism_cy + int(shield_dist * math.sin(shield_angle))
            # 三角形盾牌
            shield_rot = i * 60 + t / 50
            shield_points = []
            for p in range(3):
                p_angle = math.radians(shield_rot + p * 120)
                px = shield_x + int(18 * math.cos(p_angle))
                py = shield_y + int(18 * math.sin(p_angle))
                shield_points.append((px, py))
            # 幻彩填充
            shield_hue = (i * 60 + int(t / 30)) % 360
            shield_color = pygame.Color(0)
            shield_color.hsva = (shield_hue, 80, 100, 100)
            pygame.draw.polygon(s, (shield_color.r, shield_color.g, shield_color.b, 150), shield_points)
            pygame.draw.polygon(s, (255, 255, 255), shield_points, 2)
            # 折射光线
            refract_end_x = shield_x + int(40 * math.cos(shield_angle + math.pi))
            refract_end_y = shield_y + int(40 * math.sin(shield_angle + math.pi))
            pygame.draw.line(s, (shield_color.r, shield_color.g, shield_color.b, 100), 
                           (shield_x, shield_y), (refract_end_x, refract_end_y), 1)
        # 全息光环
        for ring in range(3):
            ring_r = 55 + ring * 25
            ring_hue = (ring * 120 + int(t / 20)) % 360
            ring_color = pygame.Color(0)
            ring_color.hsva = (ring_hue, 70, 100, 100)
            pygame.draw.circle(s, ring_color, (prism_cx, prism_cy), ring_r, 1)

    def draw_rotting_kensei():
        """腐朽剑圣 - 僵尸武士"""
        kensei_cx, kensei_cy = 120, 125
        # 残破战国盔甲 - 胴体
        armor_color = (60, 50, 45)
        rust_color = (90, 60, 40)
        # 胸甲
        pygame.draw.ellipse(s, armor_color, (kensei_cx - 35, kensei_cy - 50, 70, 90))
        pygame.draw.ellipse(s, rust_color, (kensei_cx - 30, kensei_cy - 45, 60, 80))
        # 锈迹斑驳
        for rust in range(8):
            rx = kensei_cx - 25 + random.randint(0, 50)
            ry = kensei_cy - 40 + random.randint(0, 70)
            pygame.draw.circle(s, (100, 70, 50), (rx, ry), random.randint(2, 5))
        # 红色寄生触手 - 从盔甲缝隙伸出
        tentacle_origins = [
            (kensei_cx - 30, kensei_cy - 20),
            (kensei_cx + 30, kensei_cy - 20),
            (kensei_cx - 25, kensei_cy + 10),
            (kensei_cx + 25, kensei_cy + 10),
            (kensei_cx, kensei_cy + 30),
        ]
        for origin in tentacle_origins:
            points = [origin]
            for seg in range(5):
                tx = origin[0] + (origin[0] - kensei_cx) * seg * 0.4 + int(8 * math.sin(t / 60 + seg))
                ty = origin[1] + seg * 8 + int(5 * math.cos(t / 50 + seg))
                points.append((int(tx), int(ty)))
            pygame.draw.lines(s, (150, 30, 30), False, points, 4)
            pygame.draw.lines(s, (200, 50, 50), False, points, 2)
            # 触手尖端
            pygame.draw.circle(s, (180, 40, 40), (int(points[-1][0]), int(points[-1][1])), 5)
        # 头盔 - �的面具
        helmet_y = kensei_cy - 70
        pygame.draw.ellipse(s, armor_color, (kensei_cx - 28, helmet_y - 25, 56, 50))
        # 面具
        pygame.draw.ellipse(s, (80, 70, 65), (kensei_cx - 22, helmet_y - 15, 44, 35))
        # 发光眼睛
        eye_glow = int(3 * math.sin(t / 40))
        pygame.draw.circle(s, (255, 50, 50), (kensei_cx - 10, helmet_y - 5), 5 + eye_glow)
        pygame.draw.circle(s, (255, 50, 50), (kensei_cx + 10, helmet_y - 5), 5 + eye_glow)
        pygame.draw.circle(s, (255, 200, 200), (kensei_cx - 10, helmet_y - 5), 3)
        pygame.draw.circle(s, (255, 200, 200), (kensei_cx + 10, helmet_y - 5), 3)
        # 头盔装饰 - �的角
        for side in [-1, 1]:
            horn_points = [
                (kensei_cx + side * 25, helmet_y - 20),
                (kensei_cx + side * 35, helmet_y - 45),
                (kensei_cx + side * 28, helmet_y - 25),
            ]
            pygame.draw.polygon(s, (50, 40, 35), horn_points)
        # 40米野太刀！
        sword_angle = math.radians(-30 + int(15 * math.sin(t / 100)))
        sword_length = 180  # 超长！
        sword_start_x = kensei_cx + 40
        sword_start_y = kensei_cy - 30
        sword_end_x = sword_start_x + int(sword_length * math.cos(sword_angle))
        sword_end_y = sword_start_y + int(sword_length * math.sin(sword_angle))
        # 刀身
        pygame.draw.line(s, (150, 140, 130), (sword_start_x, sword_start_y), (sword_end_x, sword_end_y), 6)
        pygame.draw.line(s, (200, 195, 185), (sword_start_x, sword_start_y), (sword_end_x, sword_end_y), 3)
        # 刀刃光芒
        pygame.draw.line(s, (255, 255, 255), (sword_start_x + 5, sword_start_y - 2), 
                        (sword_end_x + 5, sword_end_y - 2), 1)
        # 刀柄
        pygame.draw.line(s, (80, 40, 30), (sword_start_x, sword_start_y), 
                        (sword_start_x - 15, sword_start_y + 10), 8)
        # 腐败气息
        for i in range(5):
            aura_x = kensei_cx + random.randint(-50, 50)
            aura_y = kensei_cy + random.randint(-60, 60)
            aura_r = random.randint(3, 8)
            pygame.draw.circle(s, (100, 40, 40, 80), (aura_x, aura_y), aura_r)

    def draw_paradox_clockwork():
        """悖论时钟 - 蒸汽朋克机械天使"""
        clock_cx, clock_cy = 120, 120
        brass_color = (205, 165, 95)
        copper_color = (185, 135, 85)
        dark_brass = (155, 125, 70)
        # 主体 - 复杂齿轮结构
        # 大齿轮
        gear_rot = t / 80
        for gear_layer in range(3):
            gear_r = 50 - gear_layer * 12
            gear_teeth = 16 - gear_layer * 4
            gear_angle_offset = gear_rot * (1 if gear_layer % 2 == 0 else -1)
            # 齿轮主体
            pygame.draw.circle(s, brass_color if gear_layer % 2 == 0 else copper_color, 
                             (clock_cx, clock_cy), gear_r)
            pygame.draw.circle(s, dark_brass, (clock_cx, clock_cy), gear_r - 3)
            # 齿轮齿
            for tooth in range(gear_teeth):
                tooth_angle = math.radians(tooth * (360 / gear_teeth) + gear_angle_offset * 50)
                tx1 = clock_cx + int((gear_r - 2) * math.cos(tooth_angle))
                ty1 = clock_cy + int((gear_r - 2) * math.sin(tooth_angle))
                tx2 = clock_cx + int((gear_r + 8) * math.cos(tooth_angle))
                ty2 = clock_cy + int((gear_r + 8) * math.sin(tooth_angle))
                pygame.draw.line(s, brass_color, (tx1, ty1), (tx2, ty2), 4)
        # 表盘光环
        dial_r = 35
        pygame.draw.circle(s, (240, 230, 210), (clock_cx, clock_cy), dial_r)
        pygame.draw.circle(s, (220, 210, 190), (clock_cx, clock_cy), dial_r, 2)
        # 罗马数字刻度
        for i in range(12):
            num_angle = math.radians(i * 30 - 90)
            num_x = clock_cx + int(28 * math.cos(num_angle))
            num_y = clock_cy + int(28 * math.sin(num_angle))
            pygame.draw.circle(s, (80, 60, 40), (num_x, num_y), 2)
        # 指针 - 疯狂旋转
        hour_angle = math.radians(t / 30)
        minute_angle = math.radians(t / 10)
        second_angle = math.radians(t / 2)
        # 时针
        pygame.draw.line(s, (60, 40, 20), (clock_cx, clock_cy),
                        (clock_cx + int(15 * math.cos(hour_angle - math.pi/2)),
                         clock_cy + int(15 * math.sin(hour_angle - math.pi/2))), 3)
        # 分针
        pygame.draw.line(s, (80, 60, 40), (clock_cx, clock_cy),
                        (clock_cx + int(22 * math.cos(minute_angle - math.pi/2)),
                         clock_cy + int(22 * math.sin(minute_angle - math.pi/2))), 2)
        # 秒针
        pygame.draw.line(s, (150, 50, 50), (clock_cx, clock_cy),
                        (clock_cx + int(28 * math.cos(second_angle - math.pi/2)),
                         clock_cy + int(28 * math.sin(second_angle - math.pi/2))), 1)
        # 破碎怀表脸 - 裂纹
        for crack in range(6):
            crack_angle = math.radians(crack * 60 + 15)
            crack_points = [(clock_cx, clock_cy)]
            for seg in range(4):
                cr = 8 + seg * 8
                ca = crack_angle + random.uniform(-0.2, 0.2)
                crack_points.append((clock_cx + int(cr * math.cos(ca)), 
                                   clock_cy + int(cr * math.sin(ca))))
            pygame.draw.lines(s, (100, 80, 60), False, crack_points, 1)
        # 机械天使翅膀 - 齿轮翅膀
        for side in [-1, 1]:
            wing_base_x = clock_cx + side * 55
            wing_base_y = clock_cy - 20
            # 多个小齿轮组成翅膀
            for w in range(4):
                w_x = wing_base_x + side * w * 18
                w_y = wing_base_y - w * 12 + int(5 * math.sin(t / 40 + w))
                w_r = 15 - w * 2
                w_rot = gear_rot * (1 if w % 2 == 0 else -1)
                pygame.draw.circle(s, copper_color, (w_x, w_y), w_r)
                pygame.draw.circle(s, dark_brass, (w_x, w_y), w_r - 2)
                # 齿
                for tooth in range(8):
                    tooth_angle = math.radians(tooth * 45 + w_rot * 60)
                    pygame.draw.line(s, brass_color, 
                                   (w_x + int((w_r - 1) * math.cos(tooth_angle)),
                                    w_y + int((w_r - 1) * math.sin(tooth_angle))),
                                   (w_x + int((w_r + 4) * math.cos(tooth_angle)),
                                    w_y + int((w_r + 4) * math.sin(tooth_angle))), 2)
        # 蒸汽喷射
        for i in range(3):
            steam_x = clock_cx + random.randint(-40, 40)
            steam_y = clock_cy + 50 + i * 10
            steam_r = random.randint(5, 12)
            pygame.draw.circle(s, (200, 200, 200, 80), (steam_x, steam_y), steam_r)
        # 时间扭曲光环
        for ring in range(2):
            ring_r = 70 + ring * 20 + int(5 * math.sin(t / 30 + ring))
            pygame.draw.circle(s, (205, 165, 95, 80), (clock_cx, clock_cy), ring_r, 1)

    def draw_molten_behemoth():
        """熔核巨兽 - 活火山"""
        behemoth_cx, behemoth_cy = 120, 130
        obsidian_color = (30, 25, 35)
        magma_color = (255, 100, 30)
        lava_glow = (255, 200, 100)
        # 火山形主体 - 黑曜石皮肤
        # 主体轮廓
        body_points = [
            (behemoth_cx - 70, behemoth_cy + 60),
            (behemoth_cx - 60, behemoth_cy + 20),
            (behemoth_cx - 50, behemoth_cy - 30),
            (behemoth_cx - 30, behemoth_cy - 60),
            (behemoth_cx, behemoth_cy - 80),
            (behemoth_cx + 30, behemoth_cy - 60),
            (behemoth_cx + 50, behemoth_cy - 30),
            (behemoth_cx + 60, behemoth_cy + 20),
            (behemoth_cx + 70, behemoth_cy + 60),
        ]
        pygame.draw.polygon(s, obsidian_color, body_points)
        # 黑曜石纹理
        for i in range(10):
            tex_x = behemoth_cx - 50 + random.randint(0, 100)
            tex_y = behemoth_cy - 50 + random.randint(0, 90)
            tex_points = [
                (tex_x, tex_y),
                (tex_x + random.randint(5, 15), tex_y + random.randint(-5, 5)),
                (tex_x + random.randint(0, 10), tex_y + random.randint(5, 15)),
            ]
            pygame.draw.polygon(s, (40, 35, 45), tex_points)
        # 岩浆裂缝
        crack_lines = [
            [(behemoth_cx - 40, behemoth_cy + 40), (behemoth_cx - 30, behemoth_cy), 
             (behemoth_cx - 20, behemoth_cy - 40), (behemoth_cx - 10, behemoth_cy - 60)],
            [(behemoth_cx + 40, behemoth_cy + 40), (behemoth_cx + 30, behemoth_cy), 
             (behemoth_cx + 20, behemoth_cy - 40), (behemoth_cx + 10, behemoth_cy - 60)],
            [(behemoth_cx, behemoth_cy + 50), (behemoth_cx, behemoth_cy), 
             (behemoth_cx, behemoth_cy - 50)],
        ]
        lava_pulse = int(2 * math.sin(t / 30))
        for crack in crack_lines:
            # 裂缝发光
            pygame.draw.lines(s, lava_glow, False, crack, 6 + lava_pulse)
            pygame.draw.lines(s, magma_color, False, crack, 4 + lava_pulse)
            pygame.draw.lines(s, (255, 255, 200), False, crack, 2)
        # 火山口 - 头顶
        crater_y = behemoth_cy - 75
        pygame.draw.ellipse(s, obsidian_color, (behemoth_cx - 25, crater_y - 10, 50, 25))
        pygame.draw.ellipse(s, magma_color, (behemoth_cx - 20, crater_y - 5, 40, 18))
        pygame.draw.ellipse(s, lava_glow, (behemoth_cx - 15, crater_y, 30, 12))
        # 喷发岩浆
        for i in range(5):
            lava_x = behemoth_cx + random.randint(-15, 15)
            lava_y = crater_y - 10 - i * 8 - random.randint(0, 10)
            lava_r = random.randint(3, 8)
            pygame.draw.circle(s, magma_color, (lava_x, lava_y), lava_r)
            pygame.draw.circle(s, lava_glow, (lava_x, lava_y), lava_r - 2)
        # 熔岩眼睛
        eye_y = behemoth_cy - 40
        for side in [-1, 1]:
            eye_x = behemoth_cx + side * 25
            pygame.draw.circle(s, magma_color, (eye_x, eye_y), 12)
            pygame.draw.circle(s, lava_glow, (eye_x, eye_y), 8)
            pygame.draw.circle(s, (255, 255, 220), (eye_x, eye_y), 4)
            # 眼睛光晕
            pygame.draw.circle(s, (255, 100, 30, 80), (eye_x, eye_y), 16, 2)
        # 下半身融化 - 流淌的岩浆
        melt_y = behemoth_cy + 50
        for drip in range(7):
            drip_x = behemoth_cx - 60 + drip * 20
            drip_length = 20 + random.randint(0, 30) + int(10 * math.sin(t / 50 + drip))
            # 岩浆滴
            pygame.draw.ellipse(s, magma_color, (drip_x - 6, melt_y, 12, drip_length))
            pygame.draw.ellipse(s, lava_glow, (drip_x - 4, melt_y + 2, 8, drip_length - 4))
            # 底部岩浆池
            pygame.draw.ellipse(s, magma_color, (drip_x - 10, melt_y + drip_length - 5, 20, 12))
        # 熔岩光环
        for ring in range(3):
            ring_r = 80 + ring * 15
            ring_pulse = int(3 * math.sin(t / 25 + ring))
            pygame.draw.circle(s, (255, 100, 30, 60 - ring * 15), 
                             (behemoth_cx, behemoth_cy), ring_r + ring_pulse, 2)
        # 烟雾粒子
        for i in range(4):
            smoke_x = behemoth_cx + random.randint(-30, 30)
            smoke_y = crater_y - 20 - i * 15
            smoke_r = random.randint(8, 15)
            pygame.draw.circle(s, (80, 70, 70, 60), (smoke_x, smoke_y), smoke_r)

    if visual:
        # Add subtle aura if provided
        aura = visual.get('aura')
        if aura:
            aura_surf = pygame.Surface((260, 260), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (*aura, 40), (130, 130), 120)
            s.blit(aura_surf, (-10, -10), special_flags=pygame.BLEND_ADD)
    
    if type_name == "carrier": draw_carrier()
    elif type_name == "fortress": draw_fortress()
    elif type_name == "assassin": draw_assassin()
    elif type_name == "seraphim": draw_seraphim()
    elif type_name == "leviathan": draw_leviathan()
    elif type_name == "overlord": draw_overlord()
    elif type_name == "ragnarok":
        # Use procedural dreadnought renderer for higher fidelity boss appearance
        try:
            t = pygame.time.get_ticks() / 1000.0
            proc = procedural_dreadnought_surface(240, color, visual.get('core_color', color) if visual else color, t)
            s.blit(proc, (0, 0), special_flags=pygame.BLEND_ADD)
        except Exception:
            draw_ragnarok()
    elif type_name == "hydra": draw_hydra()
    elif type_name == "chronos": draw_chronos()
    elif type_name == "gazer": draw_gazer()
    elif type_name == "lich": draw_lich()
    elif type_name == "tempest": draw_tempest()
    elif type_name == "void_golem": draw_void_golem()
    elif type_name == "abyss_queen": draw_abyss_queen()
    # 10个新Boss
    elif type_name == "fungal_colossus": draw_fungal_colossus()
    elif type_name == "dune_reaper": draw_dune_reaper()
    elif type_name == "plague_empress": draw_plague_empress()
    elif type_name == "flesh_totem": draw_flesh_totem()
    elif type_name == "star_serpent": draw_star_serpent()
    elif type_name == "exo_ares": draw_exo_ares()
    elif type_name == "radiance_goddess": draw_radiance_goddess()
    elif type_name == "dimension_devourer": draw_dimension_devourer()
    elif type_name == "infernal_dragon": draw_infernal_dragon()
    elif type_name == "entropy_avatar": draw_entropy_avatar()
    # 5个最新Boss
    elif type_name == "sonic_banshee": draw_sonic_banshee()
    elif type_name == "prism_overlord": draw_prism_overlord()
    elif type_name == "rotting_kensei": draw_rotting_kensei()
    elif type_name == "paradox_clockwork": draw_paradox_clockwork()
    elif type_name == "molten_behemoth": draw_molten_behemoth()
    return s


def procedural_interceptor_surface(size=80, neon=(0, 255, 200), accent=(255,255,255), t=None):
    """Generate an Interceptor (sharp/triangular) surface."""
    if t is None: t = pygame.time.get_ticks() / 1000.0
    s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
    cx, cy = size, size
    # outline and base
    pts = [
        (cx, cy - int(size*0.9)),
        (cx + int(size*0.6), cy + int(size*0.4)),
        (cx, cy + int(size*0.2)),
        (cx - int(size*0.6), cy + int(size*0.4))
    ]
    # vertex breathing effect
    jitter = math.sin(t * 15) * 2
    pts = [(x + (jitter if i % 2 == 0 else -jitter), y) for i, (x, y) in enumerate(pts)]
    pygame.draw.polygon(s, (*neon[:3], 160), pts)
    pygame.draw.polygon(s, (*accent[:3], 255), pts, 2)
    # interior greebles (lines, vents, circuitry traces)
    for i in range(4):
        a = i / 4.0
        sx = cx + (pts[0][0] - cx) * (0.2 + a*0.6)
        sy = cy + (pts[0][1] - cy) * (0.2 + a*0.6)
        ex = sx + (random.random()-0.5) * 12
        ey = sy + (random.random()-0.5) * 12
        pygame.draw.line(s, (*accent[:3], 80), (sx, sy), (ex, ey), 1)
        # small vents (rectangles)
        vx = int(sx + (ex - sx) * 0.6)
        vy = int(sy + (ey - sy) * 0.6)
        pygame.draw.rect(s, (*neon[:3], 140), (vx-2, vy-1, 4, 2))
    # more circuitry/trace dots
    for g in range(6):
        rr = random.random()
        gx = cx + (random.random() - 0.5) * size * 0.5
        gy = cy + (random.random() - 0.5) * size * 0.25
        pygame.draw.circle(s, (*accent[:3], 120), (int(gx), int(gy)), 1)
    # engine vibrate thrusters
    thr_y = cy + int(size*0.4) + math.sin(t*30) * 3
    pygame.draw.circle(s, (*neon[:3], 230), (cx - int(size*0.22), thr_y), int(size*0.08))
    pygame.draw.circle(s, (*neon[:3], 200), (cx + int(size*0.22), thr_y), int(size*0.08))
    # internal greebles
    for g in range(6):
        angle = g * 60 + (t*30 % 360)
        ga = math.radians(angle)
        gx = cx + math.cos(ga) * (size*0.22)
        gy = cy + math.sin(ga) * (size*0.22)
        pygame.draw.circle(s, (*accent[:3], 120), (int(gx), int(gy)), 2)
    # glow
    _bloom(s, (cx, cy), neon, max_radius=int(size*0.8), layers=3)
    return s


def procedural_juggernaut_surface(size=80, color=(255,140,0), accent=(200,100,0), t=None):
    """Generate a Juggernaut (blocky, layered) surface."""
    if t is None: t = pygame.time.get_ticks() / 1000.0
    s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
    cx, cy = size, size
    # core rectangle
    rect = pygame.Rect(cx - size*0.7//2, cy - size*0.5//2, int(size*1.4), int(size*1.0))
    pygame.draw.rect(s, (*color[:3], 220), rect, border_radius=8)
    # nested armor plates
    for i in range(3):
        inset = i * 8
        r = rect.inflate(-inset, -inset)
        pygame.draw.rect(s, (*accent[:3], 120), r, 2, border_radius=max(2, 8-i*2))
        # panel gaps: horizontal lines
        gap_y = r.top + 10 + i * 12
        pygame.draw.line(s, (50, 20, 0), (r.left + 6, gap_y), (r.right - 6, gap_y), 2)
    # rotating vents
    for i in range(3):
        ang = math.radians(i * 120 + t * 60)
        vx = cx + math.cos(ang) * int(size*0.8)
        vy = cy + math.sin(ang) * int(size*0.4)
        pygame.draw.circle(s, (*accent[:3], 230), (int(vx), int(vy)), int(size*0.12))
        pygame.draw.circle(s, (255, 200, 120), (int(vx), int(vy)), int(size*0.06))
    # greebles: bolts and rivets, panel gaps, diagonal seams
    for bx in range(rect.left+6, rect.right-6, 12):
        pygame.draw.circle(s, (50, 20, 0), (bx, rect.bottom-6), 2)
    # vertical panel gaps
    for x in range(rect.left + 12, rect.right - 12, 24):
        pygame.draw.line(s, (40, 15, 0), (x, rect.top + 6), (x, rect.bottom - 6), 1)
    # diagonal seam
    pygame.draw.line(s, (40, 20, 10), (rect.left+6, rect.top+6), (rect.right-6, rect.bottom-6), 1)
    pygame.draw.line(s, (40, 20, 10), (rect.left+6, rect.bottom-6), (rect.right-6, rect.top+6), 1)
    _bloom(s, (cx, cy), color, max_radius=int(size*0.6), layers=3)
    return s


def procedural_swarmer_surface(size=64, color=(150, 0, 255), accent=(255, 0, 200), t=None):
    """Generate a Swarmer (organic) surface with moving mandibles."""
    if t is None: t = pygame.time.get_ticks() / 1000.0
    s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
    cx, cy = size, size
    # central orb
    pygame.draw.circle(s, (*color[:3], 230), (cx, cy), int(size*0.5))
    pygame.draw.circle(s, (*accent[:3], 200), (cx, cy), int(size*0.35))
    # mandibles - animated
    for i in range(3):
        a = i * 120
        ang = math.radians(a + math.sin(t * 6 + i) * 20)
        ox = cx + math.cos(ang) * int(size*0.7)
        oy = cy + math.sin(ang) * int(size*0.7)
        mx1 = cx + math.cos(ang) * int(size*0.35)
        my1 = cy + math.sin(ang) * int(size*0.35)
        pts = [(cx, cy), (mx1, my1), (ox, oy)]
        pygame.draw.polygon(s, (*accent[:3], 200), pts)
        # vein detail
        pygame.draw.line(s, (120, 0, 180), (cx + 2, cy), (int(mx1), int(my1)), 1)
    # internal small circles / greebles (veins and organic dots)
    for i in range(10):
        ang = math.radians(i * 36 + t * 40)
        r = 8 + (i % 2) * 5
        px = cx + math.cos(ang) * (int(size*0.25) + (i % 2) * 6)
        py = cy + math.sin(ang) * (int(size*0.25) + (i % 2) * 6)
        pygame.draw.circle(s, (*accent[:3], 120), (int(px), int(py)), int(r/8))
    # veins: sinuous curves around center
    for v in range(3):
        pts = []
        for k in range(-10, 11):
            x = cx + (k/11) * (size * 0.6)
            y = cy + math.sin((k + v*3) * 0.6 + t * 4) * 6 + (v-1) * 6
            pts.append((int(x), int(y)))
        pygame.draw.lines(s, (120, 0, 180, 120), False, pts, 1)
        # dots along the vein
        for p in pts[::4]:
            pygame.draw.circle(s, (*color[:3], 120), p, 1)
    _bloom(s, (cx, cy), color, max_radius=int(size*0.8), layers=3)
    return s


def procedural_dreadnought_surface(size=240, color=(200,0,50), accent=(255,120,120), t=None):
    """Large multi-part dreadnought boss with rotating core and turrets"""
    if t is None: t = pygame.time.get_ticks() / 1000.0
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size//2, size//2
    # Core mandala: concentric rings + rotated spokes
    for i in range(6):
        r = 20 + i * 18
        pygame.draw.circle(s, (*accent[:3], 40), (cx, cy), r, 2)
    # spokes (slowly rotate)
    angle_offset = (t * 10) % 360
    for i in range(0, 360, 30):
        ang = math.radians(i + angle_offset)
        ex = cx + math.cos(ang) * int(size*0.4)
        ey = cy + math.sin(ang) * int(size*0.4)
        pygame.draw.line(s, (*color[:3], 120), (cx, cy), (ex, ey), 3)
    # Turrets rotating around core
    turret_count = 8
    for i in range(turret_count):
        ang = math.radians(i * (360 / turret_count) + t * 45)
        tx = cx + math.cos(ang) * int(size*0.42)
        ty = cy + math.sin(ang) * int(size*0.42)
        pygame.draw.circle(s, (*color[:3], 200), (int(tx), int(ty)), 18)
        pygame.draw.circle(s, (*accent[:3], 255), (int(tx), int(ty)), 6)
    # Weak points pulsing
    for i in range(4):
        ang = math.radians(i * 90 + angle_offset)
        wx = cx + math.cos(ang) * int(size*0.25)
        wy = cy + math.sin(ang) * int(size*0.25)
        p = int(6 + 4 * (0.5 + 0.5 * math.sin(t * 6 + i)))
        pygame.draw.circle(s, (255, 50, 50, 220), (int(wx), int(wy)), p)
    _bloom(s, (cx, cy), color, max_radius=int(size*0.6), layers=4)
    return s


__all__ = [
    'get_boss_surf',
    'procedural_interceptor_surface',
    'procedural_juggernaut_surface',
    'procedural_swarmer_surface',
    'procedural_dreadnought_surface',
    '_bloom'
]
