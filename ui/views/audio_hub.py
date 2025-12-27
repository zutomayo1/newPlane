# -*- coding: utf-8 -*-
"""
音乐枢纽界面视图
"""

import pygame
import math
import textwrap
from ..context import (
    get_mouse_pos, 
    WIDTH, HEIGHT,
    WHITE, CYAN
)
# 使用utils模块的绘制函数
from utils.ui import draw_cyber_rect, draw_text

# 字体缓存
_font_cache = {}

def get_cached_font(name, size):
    """获取缓存的字体对象"""
    key = (name, size)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont(name, size)
    return _font_cache[key]


# 音乐枢纽选项配置
CYBER_AMBER = (255, 191, 0)

AUDIO_HUB_OPTIONS = [
    {
        "id": "music_library",
        "title": "音乐馆",
        "tagline": "原声殿堂",
        "desc": "浏览所有BGM并试听不同场景的音乐氛围。",
        "color": CYAN,
    },
    {
        "id": "sound_lab",
        "title": "音效实验室",
        "tagline": "战术声场",
        "desc": "预览战斗与系统音效，微调节奏与反馈。",
        "color": CYBER_AMBER,
    },
]

# 模块级状态
audio_hub_selected = 0


def get_audio_hub_selected():
    """获取当前选中索引"""
    return audio_hub_selected


def set_audio_hub_selected(value):
    """设置选中索引"""
    global audio_hub_selected
    audio_hub_selected = value


def get_audio_hub_options():
    """获取选项列表"""
    return AUDIO_HUB_OPTIONS


def _get_card_rects():
    """获取卡片区域"""
    card_w = 360
    card_h = 380
    gap = 60
    total = len(AUDIO_HUB_OPTIONS)
    start_x = (WIDTH - (card_w * total + gap * (total - 1))) // 2
    card_y = 210
    rects = []
    for i in range(total):
        x = start_x + i * (card_w + gap)
        rects.append(pygame.Rect(x, card_y, card_w, card_h))
    return rects


def _get_back_rect():
    """获取返回按钮区域"""
    return pygame.Rect(WIDTH//2 - 120, HEIGHT - 120, 240, 48)


def draw_audio_hub_ui(screen):
    """绘制音乐枢纽界面 - 赛博朋克风格
    
    Args:
        screen: pygame屏幕对象
    """
    if screen is None:
        return
    
    t = pygame.time.get_ticks()
    mx, my = get_mouse_pos()
    
    # ====== 背景 ======
    screen.fill((6, 10, 18))
    
    # 动态网格背景
    grid_alpha = int(15 + 8 * math.sin(t / 1200))
    for gx in range(0, WIDTH, 80):
        pygame.draw.line(screen, (0, grid_alpha, grid_alpha * 2), (gx, 0), (gx, HEIGHT), 1)
    for gy in range(0, HEIGHT, 80):
        pygame.draw.line(screen, (0, grid_alpha, grid_alpha * 2), (0, gy), (WIDTH, gy), 1)
    
    # 音波装饰线（水平波动）
    wave_y = 160
    for i in range(0, WIDTH, 8):
        wave_offset = math.sin((i + t * 0.1) * 0.02) * 15
        pygame.draw.circle(screen, (0, 60, 80), (i, int(wave_y + wave_offset)), 2)
    
    # 角落装饰 - 音符主题
    corner_size = 35
    corner_color = (0, 180, 220)
    pygame.draw.lines(screen, corner_color, False, [(0, corner_size), (0, 0), (corner_size, 0)], 2)
    pygame.draw.lines(screen, corner_color, False, [(WIDTH - corner_size, 0), (WIDTH - 1, 0), (WIDTH - 1, corner_size)], 2)
    pygame.draw.lines(screen, corner_color, False, [(0, HEIGHT - corner_size), (0, HEIGHT - 1), (corner_size, HEIGHT - 1)], 2)
    pygame.draw.lines(screen, corner_color, False, [(WIDTH - corner_size, HEIGHT - 1), (WIDTH - 1, HEIGHT - 1), (WIDTH - 1, HEIGHT - corner_size)], 2)
    
    # ====== 标题区 ======
    title_glow = int(180 + 60 * math.sin(t / 600))
    # 标题背景条
    title_bg = pygame.Surface((WIDTH, 55), pygame.SRCALPHA)
    pygame.draw.rect(title_bg, (0, 35, 55, 140), (0, 0, WIDTH, 55))
    screen.blit(title_bg, (0, 25))
    pygame.draw.line(screen, (0, title_glow, title_glow), (80, 80), (WIDTH - 80, 80), 2)
    
    # 标题文字 - 音符装饰
    title_font = get_cached_font("SimHei", 48)
    emoji_font = get_cached_font("Segoe UI Emoji", 32)
    
    title_surf = title_font.render("音乐枢纽", True, (0, title_glow, title_glow))
    note_left = emoji_font.render("🎵", True, (0, title_glow - 40, title_glow - 20))
    note_right = emoji_font.render("🎶", True, (0, title_glow - 40, title_glow - 20))
    
    title_x = WIDTH//2 - title_surf.get_width()//2
    screen.blit(note_left, (title_x - 50, 38))
    screen.blit(title_surf, (title_x, 35))
    screen.blit(note_right, (title_x + title_surf.get_width() + 15, 38))
    
    # 副标题
    draw_text(screen, "探索霓虹深空的声音世界", 18, WIDTH//2, 100, (80, 120, 140))
    
    # ====== 功能卡片 ======
    rects = _get_card_rects()
    for idx, (rect, option) in enumerate(zip(rects, AUDIO_HUB_OPTIONS)):
        hover = rect.collidepoint(mx, my)
        selected = (idx == audio_hub_selected)
        base_color = option["color"]
        
        # 卡片背景 - 渐变效果
        if hover or selected:
            bg = (base_color[0]//3 + 20, base_color[1]//3 + 15, base_color[2]//3 + 20)
            # 发光效果
            glow_surf = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (base_color[0]//4, base_color[1]//4, base_color[2]//4, 80), 
                           (0, 0, rect.width + 20, rect.height + 20), border_radius=8)
            screen.blit(glow_surf, (rect.x - 10, rect.y - 10))
        else:
            bg = (15, 20, 32)
        
        draw_cyber_rect(screen, rect, bg, alpha=245, fill=True)
        
        # 边框动画
        border_width = 3 if selected else (2 if hover else 1)
        border_color = base_color if (hover or selected) else (50, 60, 75)
        draw_cyber_rect(screen, rect, border_color, border_width=border_width, fill=False)
        
        # 顶部装饰条
        deco_rect = pygame.Rect(rect.x + 10, rect.y + 8, rect.width - 20, 4)
        pygame.draw.rect(screen, base_color if (hover or selected) else (40, 50, 65), deco_rect, border_radius=2)
        
        # 图标区域
        icon_y = rect.y + 50
        icon_size = 60
        icon_rect = pygame.Rect(rect.centerx - icon_size//2, icon_y, icon_size, icon_size)
        pygame.draw.rect(screen, (base_color[0]//6, base_color[1]//6, base_color[2]//6), icon_rect, border_radius=8)
        pygame.draw.rect(screen, base_color if (hover or selected) else (60, 70, 90), icon_rect, 2, border_radius=8)
        
        # 图标
        icon_font = get_cached_font("Segoe UI Emoji", 32)
        icon_text = "🎵" if option["id"] == "music_library" else "🔊"
        icon_surf = icon_font.render(icon_text, True, WHITE)
        screen.blit(icon_surf, (icon_rect.centerx - icon_surf.get_width()//2, icon_rect.centery - icon_surf.get_height()//2))
        
        # 标题
        title_color = WHITE if (hover or selected) else (200, 200, 210)
        draw_text(screen, option["title"], 36, rect.centerx, rect.y + 130, title_color, glow=(hover or selected))
        
        # 标语
        draw_text(screen, option["tagline"], 20, rect.centerx, rect.y + 170, base_color)
        
        # 分隔线
        sep_y = rect.y + 195
        pygame.draw.line(screen, (40, 50, 65), (rect.x + 30, sep_y), (rect.x + rect.width - 30, sep_y), 1)
        
        # 描述
        desc_lines = textwrap.wrap(option["desc"], width=16)
        text_y = rect.y + 215
        for line in desc_lines[:4]:
            draw_text(screen, line, 17, rect.centerx, text_y, (140, 150, 165))
            text_y += 26
        
        # 进入按钮
        btn_rect = pygame.Rect(rect.centerx - 60, rect.bottom - 65, 120, 36)
        btn_hover = btn_rect.collidepoint(mx, my)
        btn_bg = (base_color[0]//3, base_color[1]//3, base_color[2]//3) if btn_hover else (25, 30, 42)
        draw_cyber_rect(screen, btn_rect, btn_bg, alpha=230, fill=True)
        draw_cyber_rect(screen, btn_rect, base_color if btn_hover else (70, 80, 100), border_width=1, fill=False)
        # 分开渲染符号和文字
        btn_text_col = WHITE if btn_hover else (180, 180, 190)
        btn_emoji_font = get_cached_font("Segoe UI Emoji", 16)
        btn_text_font = get_cached_font("SimHei", 16)
        btn_icon_surf = btn_emoji_font.render("▸", True, btn_text_col)
        btn_label_surf = btn_text_font.render(" 进入", True, btn_text_col)
        btn_total_w = btn_icon_surf.get_width() + btn_label_surf.get_width()
        screen.blit(btn_icon_surf, (btn_rect.centerx - btn_total_w//2, btn_rect.centery - btn_icon_surf.get_height()//2))
        screen.blit(btn_label_surf, (btn_rect.centerx - btn_total_w//2 + btn_icon_surf.get_width(), btn_rect.centery - btn_label_surf.get_height()//2))
        
        # 选中指示器
        if selected:
            indicator_y = rect.bottom - 18
            pygame.draw.circle(screen, base_color, (rect.centerx, indicator_y), 5)
            pygame.draw.circle(screen, WHITE, (rect.centerx, indicator_y), 3)
    
    # ====== 返回按钮 ======
    back_rect = _get_back_rect()
    back_hover = back_rect.collidepoint(mx, my)
    back_bg = (40, 35, 50) if back_hover else (20, 22, 32)
    draw_cyber_rect(screen, back_rect, back_bg, alpha=235, fill=True)
    draw_cyber_rect(screen, back_rect, CYAN if back_hover else (60, 70, 85), border_width=2, fill=False)
    # 分开渲染符号和文字
    back_text_col = WHITE if back_hover else (150, 160, 170)
    back_emoji_font = get_cached_font("Segoe UI Emoji", 18)
    back_text_font = get_cached_font("SimHei", 18)
    back_icon_surf = back_emoji_font.render("◀", True, back_text_col)
    back_label_surf = back_text_font.render(" 返回主菜单", True, back_text_col)
    back_total_w = back_icon_surf.get_width() + back_label_surf.get_width()
    screen.blit(back_icon_surf, (back_rect.centerx - back_total_w//2, back_rect.centery - back_icon_surf.get_height()//2))
    screen.blit(back_label_surf, (back_rect.centerx - back_total_w//2 + back_icon_surf.get_width(), back_rect.centery - back_label_surf.get_height()//2))
    
    # 底部装饰线
    pygame.draw.line(screen, (0, 60, 80), (100, HEIGHT - 50), (WIDTH - 100, HEIGHT - 50), 1)
    
    # 返回UI元素引用
    return {
        'cards': list(zip(rects, [opt["id"] for opt in AUDIO_HUB_OPTIONS])),
        'back_btn': back_rect
    }
