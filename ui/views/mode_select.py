# -*- coding: utf-8 -*-
"""
模式选择界面视图
"""

import pygame
import math
from ..context import (
    get_screen, get_mouse_pos, 
    WIDTH, HEIGHT,
    WHITE, GRAY, CYAN, MAGENTA, YELLOW, LIME, RED
)
# 使用utils模块的绘制函数（保持与main.py一致）
from utils.ui import draw_cyber_rect, draw_text

# 字体缓存
_font_cache = {}

def get_cached_font(name, size):
    """获取缓存的字体对象"""
    key = (name, size)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont(name, size)
    return _font_cache[key]


# 模块级状态
mode_select_selected = 0  # 键盘导航索引


def get_mode_select_selected():
    """获取当前选中索引"""
    return mode_select_selected


def set_mode_select_selected(value):
    """设置选中索引"""
    global mode_select_selected
    mode_select_selected = value


def draw_mode_select_ui(screen):
    """绘制游戏模式选择UI
    
    Args:
        screen: pygame屏幕对象
    """
    if screen is None:
        return
    
    # 标题
    t = pygame.time.get_ticks()
    scale = 1.0 + 0.05 * math.sin(t * 0.003)
    draw_text(screen, "选择游戏模式", int(54 * scale), WIDTH//2, 80, CYAN, glow=True)
    
    mx, my = get_mouse_pos()
    
    # 四个模式卡片
    card_width = 280
    card_height = 450
    gap = 25
    start_x = (WIDTH - (card_width * 4 + gap * 3)) // 2
    card_y = 180
    
    modes = [
        {
            "id": "normal",
            "name": "普通模式",
            "title_color": YELLOW,
            "icon": "⚔",
            "features": [
                "经典波次战斗",
                "无尽敌人来袭", 
                "分数决定强度",
                "适合新手入门"
            ],
            "difficulty": "★★☆☆☆"
        },
        {
            "id": "roguelike",
            "name": "房间模式",
            "title_color": MAGENTA,
            "icon": "🗺",
            "features": [
                "Roguelike房间",
                "地图随机生成",
                "策略路线选择",
                "高难度挑战"
            ],
            "difficulty": "★★★★☆"
        },
        {
            "id": "boss_challenge",
            "name": "Boss挑战",
            "title_color": CYAN,
            "icon": "👑",
            "features": [
                "连续Boss战斗",
                "自定义Boss顺序",
                "极限生存考验",
                "终极挑战模式"
            ],
            "difficulty": "★★★★★"
        },
        {
            "id": "training_ground",
            "name": "训练场",
            "title_color": LIME,
            "icon": "🎯",
            "features": [
                "选择任意Boss",
                "无限制练习",
                "测试机体性能",
                "可开启无敌"
            ],
            "difficulty": "自由模式"
        }
    ]
    
    card_rects = []  # 返回卡片区域供点击检测
    
    for i, mode in enumerate(modes):
        card_x = start_x + i * (card_width + gap)
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        card_rects.append((card_rect, mode["id"]))
        
        # 检测悬停和键盘选中
        is_hover = card_rect.collidepoint(mx, my)
        is_keyboard_selected = (i == mode_select_selected)
        
        # 卡片背景
        if is_hover or is_keyboard_selected:
            bg_color = (35, 45, 55)
            border_color = mode["title_color"]
            border_width = 3
        else:
            bg_color = (25, 30, 40)
            border_color = mode["title_color"]
            border_width = 2
        
        draw_cyber_rect(screen, card_rect, bg_color, alpha=230, fill=True)
        draw_cyber_rect(screen, card_rect, border_color, border_width=border_width, fill=False)
        
        # 图标 (使用emoji字体单独渲染)
        icon_y = card_y + 45
        emoji_font_icon = get_cached_font("Segoe UI Emoji", 60)
        icon_surf = emoji_font_icon.render(mode["icon"], True, mode["title_color"])
        screen.blit(icon_surf, (card_rect.centerx - icon_surf.get_width()//2, icon_y - icon_surf.get_height()//2))
        
        # 模式名称 (选中时发光)
        name_y = icon_y + 70
        draw_text(screen, mode["name"], 26, card_rect.centerx, name_y, mode["title_color"], glow=(is_hover or is_keyboard_selected))
        
        # 难度
        difficulty_y = name_y + 40
        draw_text(screen, f"难度: {mode['difficulty']}", 16, card_rect.centerx, difficulty_y, GRAY)
        
        # 特性列表
        features_start_y = difficulty_y + 40
        for j, feature in enumerate(mode["features"]):
            feature_y = features_start_y + j * 28
            draw_text(screen, f"• {feature}", 16, card_rect.centerx, feature_y, WHITE)
        
        # 选中标记（仅鼠标悬停时显示提示）
        if is_hover:
            hint_y = card_y + card_height - 45
            pulse = int(150 + 105 * abs(math.sin(t / 300)))
            draw_text(screen, "点击选择", 20, card_rect.centerx, hint_y, (255, 255, 255))
    
    # 返回按钮
    back_btn_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 60, 200, 50)
    is_back_hover = back_btn_rect.collidepoint(mx, my)
    draw_cyber_rect(screen, back_btn_rect, (50, 20, 20) if is_back_hover else (30, 30, 40), alpha=200, fill=True)
    draw_cyber_rect(screen, back_btn_rect, RED if is_back_hover else GRAY, border_width=2, fill=False)
    draw_text(screen, "返回主菜单 [ESC]", 20, back_btn_rect.centerx, back_btn_rect.y + 18, WHITE if is_back_hover else GRAY)
    
    # 返回UI元素引用供事件处理使用
    return {
        'cards': card_rects,
        'back_btn': back_btn_rect
    }
