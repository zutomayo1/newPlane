"""
折纸鹤·零式 - 外形定义
千羽化形的和平使者

涂装列表 (12种):
1. default - 零式原型（钛白+虹彩折痕）
2. golden_crane - 金鹤献瑞（金色+祥云纹+金粒子）
3. shadow_crane - 暗夜折影（暗灰+紫电脉冲+暗影拖尾）
4. sakura_crane - 樱吹雪（粉白+飘落樱花瓣）
5. cyber_crane - 数据折叠（深蓝+电路流光+数据流）
6. phoenix_crane - 浴火凤凰（火红+燃烧羽焰+火星）
7. ice_crane - 霜华冰鹤（冰蓝透明+结晶粒子+冰霜光环）
8. jade_crane - 碧玉仙鹤（翡翠绿+云纹浮雕+玉光）
9. origami_master - 千纸匠心（彩纸拼接+折痕呼吸动画）
10. celestial_crane - 星河归鹤（星空纹理+流星尾迹）
11. void_crane - 虚无之翼（黑洞核心+空间扭曲+吸收光效）
12. festival_crane - 新春祈愿（红金+祈福符文+灯笼光）
"""
import pygame
import math
import random

# ============================================================================
#   涂装样式识别
# ============================================================================

ORIGAMI_STYLES = [
    "origami_default",
    "origami_golden_crane",
    "origami_shadow_crane", 
    "origami_sakura_crane",
    "origami_cyber_crane",
    "origami_phoenix_crane",
    "origami_ice_crane",
    "origami_jade_crane",
    "origami_master",
    "origami_celestial_crane",
    "origami_void_crane",
    "origami_festival_crane"
]


def is_origami_style(model_style):
    """检查是否为 Origami 涂装样式"""
    return model_style in ORIGAMI_STYLES


def render_origami_skin(surface, c, model_style, t, pid, static):
    """渲染 Origami 专属涂装"""
    if model_style not in ORIGAMI_STYLES:
        return None
    
    skin_map = {
        "origami_default": "default",
        "origami_golden_crane": "golden_crane",
        "origami_shadow_crane": "shadow_crane",
        "origami_sakura_crane": "sakura_crane",
        "origami_cyber_crane": "cyber_crane",
        "origami_phoenix_crane": "phoenix_crane",
        "origami_ice_crane": "ice_crane",
        "origami_jade_crane": "jade_crane",
        "origami_master": "origami_master",
        "origami_celestial_crane": "celestial_crane",
        "origami_void_crane": "void_crane",
        "origami_festival_crane": "festival_crane"
    }
    skin_id = skin_map.get(model_style, "default")
    
    frame = 0 if static else int(t * 60) % 360
    draw_origami(surface, c, 60, 60, scale=1.8, skin_id=skin_id, frame=frame)
    return surface


def _render_origami_base(surface, t, pulse):
    """渲染 Origami 基础外形"""
    frame = int(t * 60) % 360
    draw_origami(surface, (245, 245, 250), 60, 60, scale=1.8, skin_id="default", frame=frame)
    return surface


def _get_skin_colors(skin_id, frame):
    """获取涂装对应的颜色配置"""
    # 默认虹彩
    hue = (frame * 3) % 360
    rainbow = (
        int(128 + 127 * math.sin(math.radians(hue))),
        int(128 + 127 * math.sin(math.radians(hue + 120))),
        int(128 + 127 * math.sin(math.radians(hue + 240)))
    )
    
    configs = {
        "default": {
            "base": (245, 245, 250),
            "crease": rainbow,
            "shadow": (200, 205, 215),
            "glow": rainbow,
            "accent": (255, 255, 255)
        },
        "golden_crane": {
            "base": (255, 235, 180),
            "crease": (255, 200, 80),
            "shadow": (200, 170, 100),
            "glow": (255, 215, 0),
            "accent": (255, 180, 50)
        },
        "shadow_crane": {
            "base": (50, 50, 65),
            "crease": (150, 100, 200),
            "shadow": (30, 30, 40),
            "glow": (180, 100, 255),
            "accent": (100, 60, 150)
        },
        "sakura_crane": {
            "base": (255, 240, 245),
            "crease": (255, 150, 180),
            "shadow": (240, 210, 220),
            "glow": (255, 180, 200),
            "accent": (255, 120, 160)
        },
        "cyber_crane": {
            "base": (30, 40, 60),
            "crease": (0, 255, 255),
            "shadow": (20, 25, 40),
            "glow": (0, 200, 255),
            "accent": (100, 255, 255)
        },
        "phoenix_crane": {
            "base": (80, 30, 20),
            "crease": (255, 150, 50),
            "shadow": (50, 20, 15),
            "glow": (255, 100, 30),
            "accent": (255, 200, 100)
        },
        "ice_crane": {
            "base": (200, 230, 255),
            "crease": (150, 200, 255),
            "shadow": (170, 200, 230),
            "glow": (180, 220, 255),
            "accent": (220, 240, 255)
        },
        "jade_crane": {
            "base": (140, 200, 150),
            "crease": (80, 180, 100),
            "shadow": (100, 160, 110),
            "glow": (100, 220, 130),
            "accent": (180, 230, 180)
        },
        "origami_master": {
            "base": (
                int(200 + 55 * math.sin(frame * 0.05)),
                int(200 + 55 * math.sin(frame * 0.05 + 2)),
                int(200 + 55 * math.sin(frame * 0.05 + 4))
            ),
            "crease": (
                int(128 + 127 * math.sin(frame * 0.03)),
                int(128 + 127 * math.sin(frame * 0.03 + 2.1)),
                int(128 + 127 * math.sin(frame * 0.03 + 4.2))
            ),
            "shadow": (180, 180, 180),
            "glow": rainbow,
            "accent": (255, 255, 255)
        },
        "celestial_crane": {
            "base": (20, 20, 50),
            "crease": (200, 180, 255),
            "shadow": (10, 10, 30),
            "glow": (255, 255, 200),
            "accent": (180, 200, 255)
        },
        "void_crane": {
            "base": (15, 10, 20),
            "crease": (100, 50, 150),
            "shadow": (5, 5, 10),
            "glow": (150, 50, 200),
            "accent": (80, 40, 120)
        },
        "festival_crane": {
            "base": (200, 50, 50),
            "crease": (255, 215, 0),
            "shadow": (150, 30, 30),
            "glow": (255, 200, 100),
            "accent": (255, 100, 100)
        }
    }
    
    return configs.get(skin_id, configs["default"])


def draw_origami(surface, color, x, y, scale=1.0, skin_id="default", frame=0):
    """绘制折纸鹤·零式 - 12种独特涂装"""
    
    colors = _get_skin_colors(skin_id, frame)
    base_color = colors["base"]
    crease_color = colors["crease"]
    shadow_color = colors["shadow"]
    glow_color = colors["glow"]
    accent_color = colors["accent"]
    
    cx, cy = x, y
    s = scale
    
    # 呼吸和翅膀动画
    breath = math.sin(frame * 0.08) * 2
    wing_angle = math.sin(frame * 0.06) * 5
    wing_offset = wing_angle * s
    
    # ========== 特效层（背景） ==========
    _draw_background_effects(surface, cx, cy, s, skin_id, frame, colors)
    
    # ========== 翅膀阴影 ==========
    left_shadow = [
        (cx - 35*s - wing_offset, cy + 5*s),
        (cx - 8*s, cy - 5*s),
        (cx - 12*s, cy + 8*s),
        (cx - 30*s - wing_offset, cy + 15*s)
    ]
    right_shadow = [
        (cx + 35*s + wing_offset, cy + 5*s),
        (cx + 8*s, cy - 5*s),
        (cx + 12*s, cy + 8*s),
        (cx + 30*s + wing_offset, cy + 15*s)
    ]
    pygame.draw.polygon(surface, shadow_color, left_shadow)
    pygame.draw.polygon(surface, shadow_color, right_shadow)
    
    # ========== 主翅膀 ==========
    left_wing = [
        (cx - 32*s - wing_offset, cy - breath),
        (cx - 6*s, cy - 12*s - breath),
        (cx - 8*s, cy + 5*s),
        (cx - 28*s - wing_offset, cy + 10*s)
    ]
    right_wing = [
        (cx + 32*s + wing_offset, cy - breath),
        (cx + 6*s, cy - 12*s - breath),
        (cx + 8*s, cy + 5*s),
        (cx + 28*s + wing_offset, cy + 10*s)
    ]
    
    # 特殊涂装的翅膀处理
    if skin_id == "ice_crane":
        # 冰晶半透明翅膀
        wing_surf = pygame.Surface((80, 60), pygame.SRCALPHA)
        shifted_left = [(p[0] - (cx - 40*s), p[1] - (cy - 15*s)) for p in left_wing]
        pygame.draw.polygon(wing_surf, (*base_color, 180), shifted_left)
        surface.blit(wing_surf, (cx - 40*s, cy - 15*s))
        
        wing_surf2 = pygame.Surface((80, 60), pygame.SRCALPHA)
        shifted_right = [(p[0] - (cx - 5*s), p[1] - (cy - 15*s)) for p in right_wing]
        pygame.draw.polygon(wing_surf2, (*base_color, 180), shifted_right)
        surface.blit(wing_surf2, (cx - 5*s, cy - 15*s))
    elif skin_id == "void_crane":
        # 虚空扭曲翅膀
        for i in range(3):
            offset_factor = 1 + i * 0.1 * math.sin(frame * 0.1 + i)
            distorted_left = [(p[0] * offset_factor - (offset_factor - 1) * cx, p[1]) for p in left_wing]
            distorted_right = [(p[0] * offset_factor - (offset_factor - 1) * cx, p[1]) for p in right_wing]
            alpha = 100 - i * 30
            wing_surf = pygame.Surface((120, 80), pygame.SRCALPHA)
            pygame.draw.polygon(wing_surf, (*base_color, alpha), 
                              [(p[0] - (cx - 60), p[1] - (cy - 20)) for p in distorted_left])
            pygame.draw.polygon(wing_surf, (*base_color, alpha),
                              [(p[0] - (cx - 60), p[1] - (cy - 20)) for p in distorted_right])
            surface.blit(wing_surf, (cx - 60, cy - 20))
        pygame.draw.polygon(surface, base_color, left_wing)
        pygame.draw.polygon(surface, base_color, right_wing)
    else:
        pygame.draw.polygon(surface, base_color, left_wing)
        pygame.draw.polygon(surface, base_color, right_wing)
    
    # ========== 翅膀折痕 ==========
    crease_width = 3 if skin_id == "cyber_crane" else 2
    pygame.draw.line(surface, crease_color, 
                     (cx - 6*s, cy - 10*s - breath), 
                     (cx - 30*s - wing_offset, cy + 3*s), crease_width)
    pygame.draw.line(surface, crease_color, 
                     (cx + 6*s, cy - 10*s - breath), 
                     (cx + 30*s + wing_offset, cy + 3*s), crease_width)
    
    # ========== 机身 ==========
    body = [
        (cx, cy - 22*s - breath),
        (cx - 10*s, cy - 5*s),
        (cx - 6*s, cy + 18*s),
        (cx, cy + 12*s),
        (cx + 6*s, cy + 18*s),
        (cx + 10*s, cy - 5*s),
    ]
    pygame.draw.polygon(surface, base_color, body)
    
    # 机身中央折痕
    pygame.draw.line(surface, crease_color, (cx, cy - 20*s - breath), (cx, cy + 15*s), 2)
    pygame.draw.line(surface, crease_color, (cx - 8*s, cy - 3*s), (cx, cy + 10*s), 1)
    pygame.draw.line(surface, crease_color, (cx + 8*s, cy - 3*s), (cx, cy + 10*s), 1)
    
    # ========== 鹤首 ==========
    head = [
        (cx, cy - 28*s - breath),
        (cx - 4*s, cy - 18*s - breath),
        (cx + 4*s, cy - 18*s - breath)
    ]
    pygame.draw.polygon(surface, base_color, head)
    pygame.draw.line(surface, crease_color, (cx, cy - 26*s - breath), (cx, cy - 18*s - breath), 1)
    
    # ========== 尾羽 ==========
    tail_left = [(cx - 6*s, cy + 18*s), (cx - 10*s, cy + 28*s), (cx - 3*s, cy + 22*s)]
    tail_right = [(cx + 6*s, cy + 18*s), (cx + 10*s, cy + 28*s), (cx + 3*s, cy + 22*s)]
    pygame.draw.polygon(surface, base_color, tail_left)
    pygame.draw.polygon(surface, base_color, tail_right)
    pygame.draw.line(surface, crease_color, (cx - 5*s, cy + 18*s), (cx - 8*s, cy + 25*s), 1)
    pygame.draw.line(surface, crease_color, (cx + 5*s, cy + 18*s), (cx + 8*s, cy + 25*s), 1)
    
    # ========== 涂装特殊细节 ==========
    _draw_skin_details(surface, cx, cy, s, skin_id, frame, colors, breath, wing_offset)
    
    # ========== 引擎光效 ==========
    glow_size = 4 + breath * 0.5
    for i in range(3):
        glow_alpha = 150 - i * 40
        glow_r = int(glow_size + i * 2)
        glow_surf = pygame.Surface((glow_r * 4, glow_r * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*glow_color[:3], glow_alpha), 
                          (glow_r * 2, glow_r * 2), glow_r)
        surface.blit(glow_surf, (cx - glow_r * 2, cy + 20*s - glow_r * 2))
    
    # ========== 前景特效 ==========
    _draw_foreground_effects(surface, cx, cy, s, skin_id, frame, colors)
    
    return surface


def _draw_background_effects(surface, cx, cy, s, skin_id, frame, colors):
    """绘制背景特效"""
    
    if skin_id == "celestial_crane":
        # 星空背景粒子
        random.seed(42)
        for _ in range(15):
            star_x = cx + random.uniform(-40, 40) * s
            star_y = cy + random.uniform(-30, 30) * s
            star_size = random.uniform(1, 3)
            twinkle = (math.sin(frame * 0.1 + random.random() * 10) + 1) / 2
            alpha = int(100 + 155 * twinkle)
            star_surf = pygame.Surface((int(star_size * 4), int(star_size * 4)), pygame.SRCALPHA)
            pygame.draw.circle(star_surf, (255, 255, 200, alpha), 
                             (int(star_size * 2), int(star_size * 2)), int(star_size))
            surface.blit(star_surf, (star_x - star_size * 2, star_y - star_size * 2))
    
    elif skin_id == "void_crane":
        # 黑洞吸收效果
        for i in range(5):
            ring_r = 25 * s - i * 4 * s + math.sin(frame * 0.05 + i) * 3
            if ring_r > 0:
                ring_surf = pygame.Surface((int(ring_r * 2 + 10), int(ring_r * 2 + 10)), pygame.SRCALPHA)
                pygame.draw.circle(ring_surf, (*colors["crease"], 30 + i * 10), 
                                 (int(ring_r + 5), int(ring_r + 5)), int(ring_r), 2)
                surface.blit(ring_surf, (cx - ring_r - 5, cy - ring_r - 5))
    
    elif skin_id == "phoenix_crane":
        # 火焰光环
        for i in range(8):
            angle = frame * 0.02 + i * math.pi / 4
            flame_x = cx + math.cos(angle) * 30 * s
            flame_y = cy + math.sin(angle) * 20 * s
            flame_h = 8 + math.sin(frame * 0.2 + i) * 4
            flame_surf = pygame.Surface((12, int(flame_h * 2)), pygame.SRCALPHA)
            pygame.draw.ellipse(flame_surf, (255, 150, 50, 100), (0, 0, 12, int(flame_h * 2)))
            surface.blit(flame_surf, (flame_x - 6, flame_y - flame_h))


def _draw_skin_details(surface, cx, cy, s, skin_id, frame, colors, breath, wing_offset):
    """绘制涂装专属细节"""
    
    crease_color = colors["crease"]
    accent_color = colors["accent"]
    
    if skin_id == "golden_crane":
        # 祥云纹 - 翅膀上的云纹装饰
        for i in range(2):
            for side in [-1, 1]:
                cloud_x = cx + side * (15 + i * 8) * s - side * wing_offset * 0.5
                cloud_y = cy + i * 5 * s
                for j in range(3):
                    arc_x = cloud_x + (j - 1) * 4 * s * side
                    pygame.draw.arc(surface, accent_color, 
                                   (arc_x - 3*s, cloud_y - 2*s, 6*s, 4*s),
                                   0, math.pi, 1)
    
    elif skin_id == "cyber_crane":
        # 电路流光
        for i in range(5):
            progress = ((frame * 0.02 + i * 0.2) % 1.0)
            lx = cx - 6*s - (24*s * progress) - wing_offset * progress
            ly = cy - 10*s + (13*s * progress) - breath * (1 - progress)
            rx = cx + 6*s + (24*s * progress) + wing_offset * progress
            ry = ly
            
            glow_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*crease_color, 200), (5, 5), 3)
            pygame.draw.circle(glow_surf, (255, 255, 255, 255), (5, 5), 1)
            surface.blit(glow_surf, (lx - 5, ly - 5))
            surface.blit(glow_surf, (rx - 5, ry - 5))
        
        # 数据矩阵
        for i in range(3):
            for j in range(2):
                dx = cx + (i - 1) * 6 * s
                dy = cy - 5*s + j * 8 * s
                if (i + j + int(frame * 0.1)) % 3 == 0:
                    pygame.draw.rect(surface, crease_color, (dx - 1, dy - 1, 3, 3))
    
    elif skin_id == "jade_crane":
        # 云纹浮雕
        inner_color = tuple(max(0, c - 30) for c in colors["base"])
        pygame.draw.arc(surface, inner_color,
                       (cx - 6*s, cy - 10*s, 12*s, 8*s), 0, math.pi, 1)
        pygame.draw.arc(surface, inner_color,
                       (cx - 4*s, cy + 2*s, 8*s, 6*s), math.pi, 2*math.pi, 1)
        # 翡翠光泽
        highlight_surf = pygame.Surface((20, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(highlight_surf, (255, 255, 255, 40), (0, 0, 20, 40))
        surface.blit(highlight_surf, (cx - 3*s, cy - 15*s))
    
    elif skin_id == "origami_master":
        # 彩色拼接区域
        regions = [
            [(cx - 10*s, cy - 5*s), (cx - 6*s, cy + 5*s), (cx, cy), (cx - 5*s, cy - 10*s)],
            [(cx + 10*s, cy - 5*s), (cx + 6*s, cy + 5*s), (cx, cy), (cx + 5*s, cy - 10*s)],
        ]
        for idx, region in enumerate(regions):
            hue = (frame * 2 + idx * 120) % 360
            region_color = (
                int(180 + 75 * math.sin(math.radians(hue))),
                int(180 + 75 * math.sin(math.radians(hue + 120))),
                int(180 + 75 * math.sin(math.radians(hue + 240)))
            )
            pygame.draw.polygon(surface, region_color, region)
            pygame.draw.polygon(surface, crease_color, region, 1)
        
        # 折痕呼吸动画
        crease_pulse = 1 + math.sin(frame * 0.1) * 0.5
        pygame.draw.line(surface, crease_color, (cx, cy - 15*s), (cx, cy + 10*s), 
                        max(1, int(2 * crease_pulse)))
    
    elif skin_id == "festival_crane":
        # 祈福符文
        rune_color = colors["crease"]
        pygame.draw.rect(surface, rune_color, (cx - 4*s, cy - 8*s, 8*s, 1))
        pygame.draw.rect(surface, rune_color, (cx - 4*s, cy - 4*s, 8*s, 1))
        pygame.draw.rect(surface, rune_color, (cx - 1, cy - 8*s, 2, 10*s))
        # 灯笼光晕
        lantern_glow = pygame.Surface((30, 30), pygame.SRCALPHA)
        glow_alpha = int(80 + 40 * math.sin(frame * 0.08))
        pygame.draw.circle(lantern_glow, (255, 200, 100, glow_alpha), (15, 15), 15)
        surface.blit(lantern_glow, (cx - 15, cy - 15))
    
    # 翅膀细节折痕（通用）
    for i in range(3):
        offset = (i + 1) * 8 * s
        pygame.draw.line(surface, crease_color,
                        (cx - 10*s - offset - wing_offset * 0.5, cy - 2*s + i*3*s),
                        (cx - 15*s - offset - wing_offset * 0.5, cy + 5*s + i*2*s), 1)
        pygame.draw.line(surface, crease_color,
                        (cx + 10*s + offset + wing_offset * 0.5, cy - 2*s + i*3*s),
                        (cx + 15*s + offset + wing_offset * 0.5, cy + 5*s + i*2*s), 1)


def _draw_foreground_effects(surface, cx, cy, s, skin_id, frame, colors):
    """绘制前景特效"""
    
    if skin_id == "sakura_crane":
        # 飘落的樱花瓣
        random.seed(int(frame / 30))
        for i in range(8):
            petal_frame = (frame + i * 20) % 120
            px = cx + math.sin(petal_frame * 0.1 + i) * 30 * s + (i - 4) * 8 * s
            py = cy - 40*s + petal_frame * 0.8 * s
            petal_rot = petal_frame * 3 + i * 45
            
            if -30*s < py - cy < 40*s:
                petal_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
                petal_pts = []
                for j in range(8):
                    angle = math.radians(petal_rot + j * 45)
                    r = 3 if j % 2 == 0 else 5
                    petal_pts.append((5 + math.cos(angle) * r, 5 + math.sin(angle) * r))
                pygame.draw.polygon(petal_surf, (255, 180, 200, 180), petal_pts)
                surface.blit(petal_surf, (px - 5, py - 5))
    
    elif skin_id == "shadow_crane":
        # 紫电脉冲
        if frame % 8 < 4:
            random.seed(frame // 8)
            for _ in range(2):
                start_x = cx + random.uniform(-25, 25) * s
                start_y = cy + random.uniform(-20, 20) * s
                end_x = start_x + random.uniform(-15, 15) * s
                end_y = start_y + random.uniform(-15, 15) * s
                mid_x = (start_x + end_x) / 2 + random.uniform(-5, 5) * s
                mid_y = (start_y + end_y) / 2 + random.uniform(-5, 5) * s
                pygame.draw.line(surface, colors["crease"], (start_x, start_y), (mid_x, mid_y), 2)
                pygame.draw.line(surface, colors["crease"], (mid_x, mid_y), (end_x, end_y), 2)
        
        # 暗影拖尾
        for i in range(3):
            trail_alpha = 60 - i * 20
            trail_offset = (i + 1) * 3
            trail_surf = pygame.Surface((80, 60), pygame.SRCALPHA)
            trail_body = [
                (40, 8 + trail_offset),
                (30, 25 + trail_offset),
                (34, 48 + trail_offset),
                (40, 42 + trail_offset),
                (46, 48 + trail_offset),
                (50, 25 + trail_offset),
            ]
            pygame.draw.polygon(trail_surf, (*colors["base"], trail_alpha), trail_body)
            surface.blit(trail_surf, (cx - 40, cy - 30*s))
    
    elif skin_id == "ice_crane":
        # 冰晶粒子
        random.seed(42)
        for i in range(12):
            crystal_x = cx + random.uniform(-35, 35) * s
            crystal_y = cy + random.uniform(-25, 30) * s
            crystal_size = random.uniform(2, 4)
            sparkle = (math.sin(frame * 0.15 + i * 0.5) + 1) / 2
            alpha = int(80 + 120 * sparkle)
            
            crystal_surf = pygame.Surface((int(crystal_size * 4), int(crystal_size * 4)), pygame.SRCALPHA)
            for j in range(6):
                angle = j * 60 + frame * 0.5
                rad = math.radians(angle)
                lx = crystal_size * 2 + math.cos(rad) * crystal_size * 1.5
                ly = crystal_size * 2 + math.sin(rad) * crystal_size * 1.5
                pygame.draw.line(crystal_surf, (200, 230, 255, alpha), 
                               (crystal_size * 2, crystal_size * 2), (lx, ly), 1)
            surface.blit(crystal_surf, (crystal_x - crystal_size * 2, crystal_y - crystal_size * 2))
        
        # 冰霜光环
        frost_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
        frost_alpha = int(40 + 20 * math.sin(frame * 0.05))
        pygame.draw.circle(frost_surf, (200, 230, 255, frost_alpha), (40, 40), 35, 3)
        surface.blit(frost_surf, (cx - 40, cy - 40))
    
    elif skin_id == "phoenix_crane":
        # 燃烧的火星
        random.seed(int(frame / 3))
        for i in range(10):
            spark_life = (frame + i * 10) % 40
            spark_x = cx + random.uniform(-30, 30) * s
            spark_y = cy + 25*s - spark_life * 1.5 * s
            spark_size = max(1, 3 - spark_life * 0.08)
            
            if spark_y > cy - 30*s:
                colors_fire = [(255, 200, 50), (255, 150, 30), (255, 100, 20)]
                spark_color = colors_fire[min(2, int(spark_life / 15))]
                alpha = max(0, 255 - spark_life * 6)
                spark_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
                pygame.draw.circle(spark_surf, (*spark_color, alpha), (4, 4), int(spark_size))
                surface.blit(spark_surf, (spark_x - 4, spark_y - 4))
    
    elif skin_id == "celestial_crane":
        # 流星尾迹
        for i in range(3):
            meteor_phase = (frame * 0.02 + i * 0.33) % 1.0
            if meteor_phase < 0.7:
                start_x = cx - 30*s + meteor_phase * 60*s
                start_y = cy - 25*s + meteor_phase * 50*s
                trail_length = 15 * (1 - meteor_phase / 0.7)
                
                for j in range(int(trail_length)):
                    trail_x = start_x - j * 0.8
                    trail_y = start_y - j * 0.6
                    trail_alpha = int(200 * (1 - j / trail_length))
                    trail_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
                    pygame.draw.circle(trail_surf, (255, 255, 200, trail_alpha), (3, 3), 2 - j * 0.1)
                    surface.blit(trail_surf, (trail_x - 3, trail_y - 3))
    
    elif skin_id == "void_crane":
        # 空间扭曲粒子
        for i in range(8):
            angle = frame * 0.03 + i * math.pi / 4
            dist = 35 * s - (frame % 60) * 0.5 * s
            if dist > 5:
                px = cx + math.cos(angle) * dist
                py = cy + math.sin(angle) * dist * 0.6
                alpha = int(200 * (dist / (35 * s)))
                void_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
                pygame.draw.circle(void_surf, (*colors["crease"], alpha), (4, 4), 2)
                surface.blit(void_surf, (px - 4, py - 4))
    
    # 浮动小纸鹤装饰
    if skin_id in ["default", "sakura_crane", "golden_crane", "festival_crane"]:
        for i in range(2):
            angle = frame * 0.03 + i * math.pi
            mini_x = cx + math.cos(angle) * 25 * s
            mini_y = cy + math.sin(angle) * 15 * s
            
            mini_crane = [
                (mini_x, mini_y - 5),
                (mini_x - 8, mini_y),
                (mini_x, mini_y + 3),
                (mini_x + 8, mini_y)
            ]
            crane_color = colors["crease"] if skin_id != "festival_crane" else (255, 215, 0)
            pygame.draw.polygon(surface, crane_color, mini_crane)
