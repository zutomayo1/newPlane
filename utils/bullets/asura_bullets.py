# -*- coding: utf-8 -*-
"""
Asura 修罗·斩龙者 武器涂装效果渲染模块

近战武器：修罗剑刃
- 扇形挥斩攻击
- 武器涂装影响剑刃外观

武器涂装列表：
- asura_blade_base: 修罗剑（基础） - 血红剑刃
- asura_blade_rage: 狂怒之刃 - 燃烧的剑刃
- asura_blade_shadow: 暗影剑 - 黑紫色剑刃
- asura_blade_dragon: 斩龙剑 - 金龙纹剑刃
- asura_blade_crimson: 血染之剑 - 深红血刃
- asura_blade_void: 虚空剑 - 空间裂隙
- asura_blade_golden: 黄金剑 - 金色神剑
- asura_blade_divine: 神罚之剑 - 圣光剑刃
"""
import pygame
import math


def render_asura_weapon(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Asura武器涂装预览效果 - 修罗剑刃特效
    
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
    
    # 检查是否是Asura武器涂装
    asura_effects = [
        "asura_blade_base", "asura_blade_rage", "asura_blade_shadow",
        "asura_blade_dragon", "asura_blade_crimson", "asura_blade_void",
        "asura_blade_golden", "asura_blade_divine"
    ]
    
    matched_effect = None
    for effect in asura_effects:
        if effect in effects:
            matched_effect = effect
            break
    
    if not matched_effect:
        return False
    
    # 根据涂装设置颜色
    blade_color = (180, 50, 50)
    edge_color = (255, 100, 80)
    glow_color = (255, 200, 100)
    
    if "rage" in matched_effect:
        blade_color = (255, 100, 30)
        edge_color = (255, 200, 50)
        glow_color = (255, 255, 150)
    elif "shadow" in matched_effect:
        blade_color = (80, 40, 120)
        edge_color = (150, 100, 200)
        glow_color = (200, 150, 255)
    elif "dragon" in matched_effect:
        blade_color = (200, 150, 50)
        edge_color = (255, 220, 100)
        glow_color = (255, 255, 200)
    elif "crimson" in matched_effect:
        blade_color = (150, 20, 40)
        edge_color = (255, 50, 80)
        glow_color = (255, 100, 120)
    elif "void" in matched_effect:
        blade_color = (60, 30, 80)
        edge_color = (120, 80, 180)
        glow_color = (180, 120, 255)
    elif "golden" in matched_effect:
        blade_color = (255, 200, 50)
        edge_color = (255, 240, 150)
        glow_color = (255, 255, 200)
    elif "divine" in matched_effect:
        blade_color = (255, 250, 240)
        edge_color = (255, 230, 180)
        glow_color = (255, 255, 255)
    
    # 绘制剑刃预览
    blade_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    
    # 挥舞动画
    swing_angle = math.sin(t * 4) * 30 - 90
    rad = math.radians(swing_angle)
    blade_length = size * 0.4
    
    tip_x = cx + math.cos(rad) * blade_length
    tip_y = cy + math.sin(rad) * blade_length
    
    # 残影轨迹
    for i in range(5):
        trail_angle = swing_angle - i * 8
        trail_rad = math.radians(trail_angle)
        trail_tip_x = cx + math.cos(trail_rad) * blade_length * (1 - i * 0.1)
        trail_tip_y = cy + math.sin(trail_rad) * blade_length * (1 - i * 0.1)
        alpha = 150 - i * 30
        pygame.draw.line(blade_surf, (*blade_color[:3], alpha), 
                        (cx, cy), (int(trail_tip_x), int(trail_tip_y)), 4 - i)
    
    # 主剑刃
    perp_rad = rad + math.pi / 2
    blade_width = 8
    blade_pts = [
        (tip_x, tip_y),
        (cx + math.cos(perp_rad) * blade_width + math.cos(rad) * 10, 
         cy + math.sin(perp_rad) * blade_width + math.sin(rad) * 10),
        (cx, cy),
        (cx - math.cos(perp_rad) * blade_width + math.cos(rad) * 10, 
         cy - math.sin(perp_rad) * blade_width + math.sin(rad) * 10),
    ]
    pygame.draw.polygon(blade_surf, blade_color, blade_pts)
    pygame.draw.polygon(blade_surf, edge_color, blade_pts, 2)
    
    # 剑刃高光
    pygame.draw.line(blade_surf, glow_color, (cx, cy), (int(tip_x), int(tip_y)), 2)
    
    # 剑尖光芒
    pygame.draw.circle(blade_surf, glow_color, (int(tip_x), int(tip_y)), 5)
    pygame.draw.circle(blade_surf, (255, 255, 255), (int(tip_x), int(tip_y)), 2)
    
    # 剑柄
    handle_rad = rad + math.pi
    handle_x = cx + math.cos(handle_rad) * 12
    handle_y = cy + math.sin(handle_rad) * 12
    pygame.draw.line(blade_surf, (80, 60, 50), (cx, cy), (int(handle_x), int(handle_y)), 4)
    pygame.draw.circle(blade_surf, edge_color, (int(handle_x), int(handle_y)), 4)
    
    surface.blit(blade_surf, (x, y))
    return True


# 为了兼容旧接口
def render_asura_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """兼容旧接口，重定向到武器渲染"""
    return render_asura_weapon(surface, effects, color, center_x, center_y, size, x, y)


# 武器涂装主题列表
ASURA_WEAPON_THEMES = [
    {
        "id": "asura_blade_base",
        "name": "修罗剑",
        "description": "血红色的修罗剑刃，斩尽一切",
        "rarity": "common",
        "effects": ["asura_blade_base"]
    },
    {
        "id": "asura_blade_rage", 
        "name": "狂怒之刃",
        "description": "燃烧着怒火的剑刃",
        "rarity": "uncommon",
        "effects": ["asura_blade_rage"]
    },
    {
        "id": "asura_blade_shadow",
        "name": "暗影剑",
        "description": "暗紫色的暗影剑刃",
        "rarity": "uncommon", 
        "effects": ["asura_blade_shadow"]
    },
    {
        "id": "asura_blade_crimson",
        "name": "血染之剑",
        "description": "深红色的血染剑刃",
        "rarity": "rare",
        "effects": ["asura_blade_crimson"]
    },
    {
        "id": "asura_blade_golden",
        "name": "黄金剑",
        "description": "金光闪闪的神剑",
        "rarity": "rare",
        "effects": ["asura_blade_golden"]
    },
    {
        "id": "asura_blade_dragon",
        "name": "斩龙剑",
        "description": "金龙纹饰的剑刃，破灭万物",
        "rarity": "epic",
        "effects": ["asura_blade_dragon"]
    },
    {
        "id": "asura_blade_void",
        "name": "虚空剑",
        "description": "撕裂空间的剑刃",
        "rarity": "epic",
        "effects": ["asura_blade_void"]
    },
    {
        "id": "asura_blade_divine",
        "name": "神罚之剑",
        "description": "圣光与暗影交织的终极剑刃",
        "rarity": "legendary",
        "effects": ["asura_blade_divine"]
    }
]

# 兼容旧名称
ASURA_BULLET_THEMES = ASURA_WEAPON_THEMES
