# -*- coding: utf-8 -*-
"""
Dragoon 龙骑士·雷因哈特 武器涂装效果渲染模块

近战武器：龙骑长枪
- 直线突刺攻击
- 武器涂装影响长枪外观

武器涂装列表：
- dragoon_lance_base: 龙骑枪（基础） - 蓝银长枪
- dragoon_lance_storm: 风暴之矛 - 雷电长枪
- dragoon_lance_azure: 苍蓝之枪 - 深蓝长枪
- dragoon_lance_silver: 银龙之矛 - 银白长枪
- dragoon_lance_dragon: 龙魂之矛 - 龙纹长枪
- dragoon_lance_royal: 皇家之枪 - 金红长枪
- dragoon_lance_valkyrie: 女武神之矛 - 圣洁长枪
- dragoon_lance_divine: 神圣裁决 - 终极神圣长枪
"""
import pygame
import math


def render_dragoon_weapon(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Dragoon武器涂装预览效果 - 龙骑长枪特效
    
    Args:
        surface: pygame绘图表面
        effects: 效果列表
        color: 主题颜色
        center_x, center_y: 中心坐标
        size: 预览大小
        x, y: 左上角坐标
    
    Returns:
        bool: 如果渲染了效果返回True，否则False
    """
    t = pygame.time.get_ticks() / 1000.0
    
    # 检查是否是Dragoon武器涂装
    dragoon_effects = [
        "dragoon_lance_base", "dragoon_lance_storm", "dragoon_lance_azure",
        "dragoon_lance_silver", "dragoon_lance_dragon", "dragoon_lance_royal",
        "dragoon_lance_valkyrie", "dragoon_lance_divine"
    ]
    
    matched_effect = None
    for effect in dragoon_effects:
        if effect in effects:
            matched_effect = effect
            break
    
    if not matched_effect:
        return False
    
    # 根据涂装设置颜色
    lance_color = (100, 150, 220)
    shaft_color = (150, 180, 230)
    tip_color = (220, 240, 255)
    glow_color = (180, 210, 255)
    
    if "storm" in matched_effect:
        lance_color = (200, 200, 80)
        shaft_color = (255, 255, 120)
        tip_color = (255, 255, 200)
        glow_color = (255, 255, 150)
    elif "azure" in matched_effect:
        lance_color = (30, 80, 150)
        shaft_color = (60, 120, 200)
        tip_color = (150, 200, 255)
        glow_color = (100, 160, 255)
    elif "silver" in matched_effect:
        lance_color = (200, 210, 220)
        shaft_color = (230, 235, 245)
        tip_color = (255, 255, 255)
        glow_color = (240, 245, 255)
    elif "dragon" in matched_effect:
        lance_color = (60, 120, 60)
        shaft_color = (100, 180, 100)
        tip_color = (180, 255, 180)
        glow_color = (150, 220, 150)
    elif "royal" in matched_effect:
        lance_color = (180, 50, 50)
        shaft_color = (255, 200, 80)
        tip_color = (255, 240, 180)
        glow_color = (255, 220, 120)
    elif "valkyrie" in matched_effect:
        lance_color = (180, 200, 255)
        shaft_color = (220, 230, 255)
        tip_color = (255, 255, 255)
        glow_color = (200, 220, 255)
    elif "divine" in matched_effect:
        lance_color = (255, 250, 230)
        shaft_color = (255, 255, 245)
        tip_color = (255, 255, 255)
        glow_color = (255, 250, 220)
    
    # 绘制长枪预览
    lance_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    
    # 突刺动画
    thrust_offset = math.sin(t * 5) * 8
    
    # 长枪参数
    lance_length = size * 0.8
    shaft_width = 6
    
    # 枪尖位置（朝上）
    tip_y = cy - lance_length / 2 + thrust_offset
    base_y = cy + lance_length / 2 + thrust_offset
    
    # 能量尾迹
    if thrust_offset < 0:
        for i in range(4):
            trail_alpha = int(100 * (1 - i * 0.25))
            trail_y = base_y + i * 6
            trail_width = int(15 * (1 - i * 0.2))
            pygame.draw.ellipse(lance_surf, (*glow_color, trail_alpha),
                              (cx - trail_width//2, int(trail_y) - 3, trail_width, 6))
    
    # 枪杆
    pygame.draw.rect(lance_surf, shaft_color, 
                    (cx - shaft_width//2, int(tip_y) + 20, shaft_width, int(lance_length) - 20))
    pygame.draw.rect(lance_surf, lance_color,
                    (cx - shaft_width//2, int(tip_y) + 20, shaft_width, int(lance_length) - 20), 1)
    
    # 枪杆装饰环
    for ring_offset in [30, 50, 70]:
        ring_y = int(tip_y) + ring_offset
        if ring_y < base_y:
            pygame.draw.rect(lance_surf, lance_color,
                           (cx - shaft_width//2 - 2, ring_y, shaft_width + 4, 3))
    
    # 枪头（三角形）
    tip_height = 25
    tip_pts = [
        (cx, int(tip_y)),  # 尖端
        (cx - 10, int(tip_y) + tip_height),
        (cx + 10, int(tip_y) + tip_height),
    ]
    pygame.draw.polygon(lance_surf, tip_color, tip_pts)
    pygame.draw.polygon(lance_surf, lance_color, tip_pts, 2)
    
    # 枪头装饰（翼形）
    wing_pts = [
        (cx - 12, int(tip_y) + tip_height),
        (cx - 6, int(tip_y) + tip_height - 5),
        (cx, int(tip_y) + tip_height),
        (cx + 6, int(tip_y) + tip_height - 5),
        (cx + 12, int(tip_y) + tip_height),
        (cx + 6, int(tip_y) + tip_height + 6),
        (cx - 6, int(tip_y) + tip_height + 6),
    ]
    pygame.draw.polygon(lance_surf, lance_color, wing_pts)
    
    # 枪尖光芒
    pygame.draw.circle(lance_surf, glow_color, (cx, int(tip_y) + 5), 5)
    pygame.draw.circle(lance_surf, (255, 255, 255), (cx, int(tip_y) + 5), 2)
    
    # 枪尾
    pygame.draw.circle(lance_surf, lance_color, (cx, int(base_y)), 5)
    
    surface.blit(lance_surf, (x, y))
    return True


# 为了兼容旧接口
def render_dragoon_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """兼容旧接口，重定向到武器渲染"""
    return render_dragoon_weapon(surface, effects, color, center_x, center_y, size, x, y)


# 武器涂装主题列表
DRAGOON_WEAPON_THEMES = [
    {
        "id": "dragoon_lance_base",
        "name": "龙骑枪",
        "description": "蓝银色的基础龙骑长枪",
        "rarity": "common",
        "effects": ["dragoon_lance_base"]
    },
    {
        "id": "dragoon_lance_azure",
        "name": "苍蓝之枪",
        "description": "深邃的苍蓝色长枪",
        "rarity": "common",
        "effects": ["dragoon_lance_azure"]
    },
    {
        "id": "dragoon_lance_storm",
        "name": "风暴之矛",
        "description": "带有雷电能量的长枪",
        "rarity": "uncommon",
        "effects": ["dragoon_lance_storm"]
    },
    {
        "id": "dragoon_lance_silver",
        "name": "银龙之矛",
        "description": "银白色的高贵长枪",
        "rarity": "uncommon",
        "effects": ["dragoon_lance_silver"]
    },
    {
        "id": "dragoon_lance_dragon",
        "name": "龙魂之矛",
        "description": "蕴含龙魂的长枪",
        "rarity": "rare",
        "effects": ["dragoon_lance_dragon"]
    },
    {
        "id": "dragoon_lance_royal",
        "name": "皇家之枪",
        "description": "金红色的皇室长枪",
        "rarity": "rare",
        "effects": ["dragoon_lance_royal"]
    },
    {
        "id": "dragoon_lance_valkyrie",
        "name": "女武神之矛",
        "description": "圣洁的白金长枪",
        "rarity": "epic",
        "effects": ["dragoon_lance_valkyrie"]
    },
    {
        "id": "dragoon_lance_divine",
        "name": "神圣裁决",
        "description": "终极神圣长枪，天罚之力",
        "rarity": "legendary",
        "effects": ["dragoon_lance_divine"]
    }
]

# 兼容旧名称
DRAGOON_BULLET_THEMES = DRAGOON_WEAPON_THEMES
