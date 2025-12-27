# -*- coding: utf-8 -*-
"""
UI工具函数 - 常用绘制工具
"""

import pygame
import math
from typing import Tuple, Optional

# ==================== 背景绘制 ====================

def draw_grid_background(screen: pygame.Surface, time_ms: int, 
                         grid_size: int = 40, alpha: int = 15):
    """绘制动态网格背景"""
    width, height = screen.get_size()
    grid_color = (alpha, int(alpha * 1.5), alpha * 2)
    offset = int(time_ms / 100) % grid_size
    
    for x in range(-offset, width + grid_size, grid_size):
        pygame.draw.line(screen, grid_color, (x, 0), (x, height))
    for y in range(-offset, height + grid_size, grid_size):
        pygame.draw.line(screen, grid_color, (0, y), (width, y))


def draw_particles(screen: pygame.Surface, time_ms: int, count: int = 30):
    """绘制装饰性粒子"""
    width, height = screen.get_size()
    for i in range(count):
        px = (i * 97 + int(time_ms / 40)) % width
        py = (i * 61 + int(time_ms / 60)) % height
        p_alpha = int(40 + 30 * math.sin(time_ms / 400 + i))
        pygame.draw.circle(screen, (p_alpha, p_alpha, int(p_alpha * 1.5)), (px, py), 1)


def draw_glow_border(screen: pygame.Surface, time_ms: int, color: Tuple[int, int, int] = (0, 150, 180)):
    """绘制边框发光效果"""
    width, height = screen.get_size()
    glow_intensity = int(100 + 40 * math.sin(time_ms / 500))
    border_color = (
        min(255, color[0] + glow_intensity // 5),
        min(255, glow_intensity),
        min(255, int(glow_intensity * 1.2))
    )
    pygame.draw.rect(screen, border_color, (0, 0, width, 3))
    pygame.draw.rect(screen, border_color, (0, height - 3, width, 3))


# ==================== 面板绘制 ====================

def draw_title_panel(screen: pygame.Surface, title: str, emoji: str,
                     x: int, y: int, width: int = 400, height: int = 55,
                     color: Tuple[int, int, int] = (0, 200, 255),
                     time_ms: int = 0):
    """绘制标题面板"""
    rect = pygame.Rect(x, y, width, height)
    
    # 渐变背景
    bg = pygame.Surface((width, height), pygame.SRCALPHA)
    for ty in range(height):
        alpha = int(180 - ty * 2)
        pygame.draw.line(bg, (20, 40, 60, alpha), (0, ty), (width, ty))
    screen.blit(bg, rect.topleft)
    
    # 边框
    pygame.draw.rect(screen, color, rect, 2, border_radius=8)
    
    # 文字（动态发光）
    title_glow = int(255 * (0.8 + 0.2 * math.sin(time_ms / 300)))
    title_color = (title_glow, title_glow, title_glow)
    
    title_font = pygame.font.SysFont("SimHei", 38)
    emoji_font = pygame.font.SysFont("Segoe UI Emoji", 32)
    
    emoji_surf = emoji_font.render(emoji, True, color)
    title_surf = title_font.render(f" {title} ", True, title_color)
    
    total_w = emoji_surf.get_width() + title_surf.get_width() + emoji_surf.get_width()
    start_x = x + width // 2 - total_w // 2
    
    screen.blit(emoji_surf, (start_x, y + 8))
    screen.blit(title_surf, (start_x + emoji_surf.get_width(), y + 4))
    screen.blit(emoji_surf, (start_x + emoji_surf.get_width() + title_surf.get_width(), y + 8))


def draw_section_header(screen: pygame.Surface, title: str, emoji: str,
                        x: int, y: int, width: int = 350,
                        color: Tuple[int, int, int] = (0, 200, 255)):
    """绘制区域标题"""
    rect = pygame.Rect(x, y, width, 35)
    bg_color = (color[0] // 10 + 10, color[1] // 10 + 30, color[2] // 10 + 50, 180)
    pygame.draw.rect(screen, bg_color, rect, border_radius=6)
    pygame.draw.rect(screen, color, rect, 1, border_radius=6)
    
    vol_font = pygame.font.SysFont("SimHei", 20)
    emoji_font = pygame.font.SysFont("Segoe UI Emoji", 18)
    
    icon = emoji_font.render(emoji, True, color)
    text = vol_font.render(f" {title}", True, color)
    
    screen.blit(icon, (x + 12, y + 7))
    screen.blit(text, (x + 38, y + 6))


# ==================== 进度条绘制 ====================

def draw_progress_bar(screen: pygame.Surface, x: int, y: int, 
                      width: int, height: int, progress: float,
                      color: Tuple[int, int, int] = (0, 200, 255),
                      bg_color: Tuple[int, int, int] = (30, 35, 45)):
    """绘制进度条"""
    # 背景轨道
    track_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, bg_color, track_rect, border_radius=height // 2)
    
    # 进度填充
    progress_width = int(width * max(0, min(1, progress)))
    if progress_width > 0:
        progress_rect = pygame.Rect(x, y, progress_width, height)
        avg_color = (
            min(255, int(color[0] * 0.7 + 60)),
            min(255, int(color[1] * 0.7 + 60)),
            min(255, int(color[2] * 0.7 + 60))
        )
        pygame.draw.rect(screen, avg_color, progress_rect, border_radius=height // 2)
        pygame.draw.rect(screen, color, progress_rect, 1, border_radius=height // 2)
    
    return progress_width


def draw_slider_handle(screen: pygame.Surface, x: int, y: int, 
                       radius: int = 11, is_hover: bool = False,
                       is_dragging: bool = False,
                       color: Tuple[int, int, int] = (0, 200, 255)):
    """绘制滑块手柄"""
    handle_color = (255, 255, 255) if is_dragging else (color if is_hover else (180, 180, 180))
    
    # 悬停/拖动时的发光效果
    if is_hover or is_dragging:
        pygame.draw.circle(screen, (*color[:3], 80), (x, y), radius + 6)
    
    # 主体
    pygame.draw.circle(screen, handle_color, (x, y), radius)
    pygame.draw.circle(screen, (255, 255, 255), (x, y), radius, 2)
    pygame.draw.circle(screen, color, (x, y), 5)  # 中心点


# ==================== 按钮绘制 ====================

def draw_action_button(screen: pygame.Surface, rect: pygame.Rect,
                       text: str, emoji: str,
                       color: Tuple[int, int, int] = (0, 200, 255),
                       is_hover: bool = False):
    """绘制动作按钮"""
    # 背景渐变
    bg = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for by in range(rect.height):
        alpha = 200 - by * 2
        c = (color[0] // 3 if is_hover else color[0] // 4,
             color[1] // 3 if is_hover else color[1] // 4,
             color[2] // 3 if is_hover else color[2] // 4)
        pygame.draw.line(bg, (*c, alpha), (0, by), (rect.width, by))
    screen.blit(bg, rect.topleft)
    
    # 边框
    border_color = color if is_hover else tuple(c // 2 for c in color)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=8)
    
    # 悬停光晕
    if is_hover:
        glow_color = (*color, 50)
        pygame.draw.rect(screen, glow_color, rect.inflate(4, 4), 2, border_radius=10)
    
    # 文字
    font = pygame.font.SysFont("SimHei", 20)
    emoji_font = pygame.font.SysFont("Segoe UI Emoji", 18)
    
    icon = emoji_font.render(emoji, True, color)
    text_surf = font.render(f" {text}", True, (255, 255, 255))
    
    screen.blit(icon, (rect.centerx - 35, rect.centery - 8))
    screen.blit(text_surf, (rect.centerx - 10, rect.centery - 10))


# ==================== 卡片绘制 ====================

def draw_item_card(screen: pygame.Surface, rect: pygame.Rect,
                   is_hover: bool = False, is_selected: bool = False,
                   color: Tuple[int, int, int] = (60, 70, 90)):
    """绘制项目卡片背景"""
    bg_color = (25, 35, 50) if is_hover else (18, 25, 40)
    pygame.draw.rect(screen, bg_color, rect, border_radius=8)
    
    border_color = color if is_selected else ((80, 90, 110) if is_hover else (50, 55, 65))
    pygame.draw.rect(screen, border_color, rect, 1, border_radius=8)


# ==================== 对话框绘制 ====================

def draw_popup_panel(screen: pygame.Surface, rect: pygame.Rect,
                     title: str, title_emoji: str,
                     color: Tuple[int, int, int] = (255, 200, 0)):
    """绘制弹出面板"""
    # 阴影
    shadow_rect = rect.inflate(8, 8)
    shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 100), shadow_surf.get_rect(), border_radius=10)
    screen.blit(shadow_surf, shadow_rect.topleft)
    
    # 主体
    pygame.draw.rect(screen, (25, 28, 38), rect, border_radius=8)
    pygame.draw.rect(screen, color, rect, 2, border_radius=8)
    
    # 标题
    title_font = pygame.font.SysFont("SimHei", 16)
    emoji_font = pygame.font.SysFont("Segoe UI Emoji", 14)
    
    icon = emoji_font.render(title_emoji, True, color)
    text = title_font.render(title, True, color)
    
    screen.blit(icon, (rect.x + 12, rect.y + 10))
    screen.blit(text, (rect.x + 40, rect.y + 12))
    
    # 分隔线
    pygame.draw.line(screen, (60, 65, 80), 
                     (rect.x + 10, rect.y + 40), 
                     (rect.right - 10, rect.y + 40), 1)


# ==================== 保存提示 ====================

def draw_save_message(screen: pygame.Surface, message: str, 
                      alpha: int, y_offset: int = 0,
                      color: Tuple[int, int, int] = (100, 255, 100)):
    """绘制保存成功消息"""
    if alpha <= 0:
        return
    
    width = screen.get_width()
    font = pygame.font.SysFont("SimHei", 22)
    surf = font.render(message, True, color)
    surf.set_alpha(min(255, alpha))
    screen.blit(surf, (width // 2 - surf.get_width() // 2, 78 + y_offset))
