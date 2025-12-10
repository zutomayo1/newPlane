"""
敌人和Boss渲染模块

包含Boss外观和程序化敌人单位渲染
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


def get_boss_surf(type_name, color, visual=None):
    """生成Boss外观"""
    s = pygame.Surface((240, 240), pygame.SRCALPHA)
    
    # 辅助绘制函数 (闭包)
    def draw_carrier(): 
        pygame.draw.polygon(s, (80, 0, 0), [(0, 60), (120, 180), (240, 60), (120, 0)])
        pygame.draw.polygon(s, color, [(20, 60), (120, 160), (220, 60), (120, 20)], 3)
        pygame.draw.rect(s, color, (100, 60, 40, 40))
        pygame.draw.rect(s, (50, 0, 0), (20, 20, 40, 80))
        pygame.draw.rect(s, (50, 0, 0), (180, 20, 40, 80))
    
    def draw_fortress(): 
        pygame.draw.rect(s, (50, 30, 0), (0, 0, 200, 200), border_radius=20)
        pygame.draw.rect(s, color, (20, 20, 160, 160), 5, border_radius=15)
        pygame.draw.circle(s, DARK_RED, (100, 100), 60)
        pygame.draw.circle(s, color, (100, 100), 40)
    
    def draw_assassin(): 
        pygame.draw.polygon(s, (30, 0, 50), [(0, 0), (90, 120), (180, 0), (90, 40)])
        pygame.draw.polygon(s, color, [(20, 10), (90, 100), (160, 10), (90, 50)], 3)
    
    def draw_seraphim():
        cx, cy = 110, 110
        pygame.draw.circle(s, color, (cx, cy), 100, 4)
        pygame.draw.circle(s, WHITE, (cx, cy), 90, 2)
        pygame.draw.circle(s, WHITE, (cx, cy), 40)
        pygame.draw.circle(s, color, (cx, cy), 30)
        for i in range(0, 360, 60): 
            rad = math.radians(i)
            end_x = cx + math.cos(rad) * 100
            end_y = cy + math.sin(rad) * 100
            pygame.draw.line(s, color, (cx, cy), (end_x, end_y), 5)
    
    def draw_leviathan():
        for i in range(5): 
            y = 50 + i * 50
            size = 60 - i * 8
            pygame.draw.circle(s, color, (100, y), size)
            pygame.draw.circle(s, (50, 0, 80), (100, y), size-5)
        pygame.draw.polygon(s, color, [(50, 50), (150, 50), (100, 0)])
    
    def draw_overlord():
        pygame.draw.circle(s, (20, 20, 30), (100, 100), 90)
        pygame.draw.circle(s, color, (100, 100), 90, 4)
        pygame.draw.circle(s, RED, (100, 100), 30)
        for i in range(0, 360, 45): 
            rad = math.radians(i)
            end_x = 100 + math.cos(rad) * 100
            end_y = 100 + math.sin(rad) * 100
            pygame.draw.line(s, GRAY, (100, 100), (end_x, end_y), 2)
    
    def draw_ragnarok(): 
        pygame.draw.rect(s, color, (60, 40, 120, 100), border_radius=10)
        pygame.draw.rect(s, DARK_RED, (90, 70, 60, 40))
        pygame.draw.line(s, RED, (90, 90), (150, 90), 2)
        pygame.draw.polygon(s, GRAY, [(40, 40), (60, 60), (60, 120), (40, 140)])
        pygame.draw.polygon(s, GRAY, [(200, 40), (180, 60), (180, 120), (200, 140)])
    
    def draw_hydra():
        for i, offset in enumerate([-50, 0, 50]): 
            mx, my = 120 + offset, 100 - abs(offset)//2
            pygame.draw.circle(s, color, (mx, my), 30)
            pygame.draw.circle(s, LIME, (mx, my), 20)
            pygame.draw.line(s, (0, 100, 0), (120, 200), (mx, my+20), 10)
    
    def draw_chronos():
        pygame.draw.circle(s, color, (120, 120), 100, 2)
        pygame.draw.circle(s, color, (120, 120), 80, 1)
        pygame.draw.circle(s, WHITE, (120, 120), 10)
        pygame.draw.line(s, WHITE, (120, 120), (120, 50), 4)
        pygame.draw.line(s, WHITE, (120, 120), (180, 120), 3)
        for i in range(12): 
            rad = math.radians(i * 30)
            sx = 120 + math.cos(rad) * 90
            sy = 120 + math.sin(rad) * 90
            pygame.draw.circle(s, color, (int(sx), int(sy)), 5)
    
    def draw_gazer():
        pygame.draw.circle(s, (50, 0, 0), (120, 120), 100)
        pygame.draw.circle(s, RED, (120, 120), 80, 2)
        pygame.draw.circle(s, BLACK, (120, 120), 40)
        pygame.draw.circle(s, RED, (120, 120), 15)
        for i in range(0, 360, 45): 
            rad = math.radians(i)
            ex = 120 + math.cos(rad) * 110
            ey = 120 + math.sin(rad) * 110
            pygame.draw.line(s, (100, 0, 0), (120, 120), (ex, ey), 2)
    
    def draw_lich(): 
        pygame.draw.polygon(s, (20, 0, 30), [(60, 180), (180, 180), (120, 40)])
        pygame.draw.circle(s, GHOST_CYAN, (120, 80), 25)
        pygame.draw.circle(s, BLACK, (110, 75), 5)
        pygame.draw.circle(s, BLACK, (130, 75), 5)
        pygame.draw.rect(s, GHOST_CYAN, (40, 100, 20, 40), 1)
        pygame.draw.rect(s, GHOST_CYAN, (180, 100, 20, 40), 1)
    
    def draw_tempest():
        pygame.draw.circle(s, GRAY, (120, 120), 90, 5)
        pygame.draw.circle(s, WIND_BLUE, (120, 120), 20)
        for i in range(0, 360, 60): 
            rad = math.radians(i)
            ex = 120 + math.cos(rad) * 90
            ey = 120 + math.sin(rad) * 90
            pygame.draw.line(s, WIND_BLUE, (120, 120), (ex, ey), 8)
    
    def draw_void_golem():
        # 虚空魔像：机械齿轮风格，紫色能量核心
        cx, cy = 120, 120
        # 外层齿轮轮廓
        pygame.draw.circle(s, color, (cx, cy), 90, 4)
        # 内层齿轮
        pygame.draw.circle(s, (60, 0, 100), (cx, cy), 70, 2)
        # 中央能量核心（脉动）
        core_size = 30 + int(10 * math.sin(pygame.time.get_ticks() / 300))
        pygame.draw.circle(s, (200, 100, 255), (cx, cy), core_size)
        pygame.draw.circle(s, (255, 150, 255), (cx, cy), core_size - 5)
        # 齿轮齿片（8个方向）
        for i in range(8):
            rad = math.radians(i * 45)
            # 外齿
            gx1 = cx + math.cos(rad) * 100
            gy1 = cy + math.sin(rad) * 100
            gx2 = cx + math.cos(rad + 0.3) * 90
            gy2 = cy + math.sin(rad + 0.3) * 90
            gx3 = cx + math.cos(rad - 0.3) * 90
            gy3 = cy + math.sin(rad - 0.3) * 90
            pygame.draw.polygon(s, color, [(int(gx1), int(gy1)), (int(gx2), int(gy2)), (int(gx3), int(gy3))])
        # 能量辐射线（4条）
        for i in range(0, 360, 90):
            rad = math.radians(i)
            ex = cx + math.cos(rad) * 110
            ey = cy + math.sin(rad) * 110
            pygame.draw.line(s, (150, 50, 200), (cx, cy), (int(ex), int(ey)), 3)
    
    def draw_abyss_queen():
        # 星渊女王：星体和王冠形状，紫蓝色
        cx, cy = 120, 120
        # 王冠顶部（三个尖角）
        crown_y = 50
        pygame.draw.polygon(s, color, [
            (cx - 40, crown_y + 20),
            (cx - 60, crown_y),
            (cx, crown_y - 30),
            (cx + 60, crown_y),
            (cx + 40, crown_y + 20)
        ])
        # 皇冠下的珍珠（3个）
        for offset in [-30, 0, 30]:
            pygame.draw.circle(s, (255, 200, 255), (cx + offset, crown_y + 35), 8)
        # 主体球形（星渊能量）
        pygame.draw.circle(s, (80, 40, 150), (cx, cy), 70, 2)
        pygame.draw.circle(s, color, (cx, cy), 65, 3)
        # 中央星体（脉动）
        star_size = 25 + int(8 * math.sin(pygame.time.get_ticks() / 250))
        pygame.draw.circle(s, (255, 200, 255), (cx, cy), star_size)
        # 环绕的小星体（5个）
        for i in range(5):
            rad = math.radians(i * 72 + pygame.time.get_ticks() / 50)
            sx = cx + math.cos(rad) * 85
            sy = cy + math.sin(rad) * 85
            pygame.draw.circle(s, (200, 100, 255), (int(sx), int(sy)), 6)
            # 星体光晕
            pygame.draw.circle(s, (150, 80, 200), (int(sx), int(sy)), 10, 1)
        # 底部触手轮廓（3根）
        for offset in [-30, 0, 30]:
            pygame.draw.line(s, (100, 50, 180), (cx + offset, cy + 70), (cx + offset, cy + 110), 4)
            # 触手节点
            for j in range(3):
                node_y = cy + 70 + j * 13
                pygame.draw.circle(s, color, (cx + offset, node_y), 4)

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
