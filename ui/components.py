# -*- coding: utf-8 -*-
"""
UI组件库 - 可复用的UI绘制组件
"""

import pygame
import math
from . import context as ctx

# ==================== 缓存管理 ====================

_font_cache = {}

def get_font(name, size, bold=False):
    """获取缓存的字体"""
    key = (name, size, bold)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont(name, size, bold=bold)
    return _font_cache[key]

def get_chinese_font(size, bold=False):
    """获取中文字体"""
    return get_font("SimHei", size, bold)

def get_emoji_font(size):
    """获取Emoji字体"""
    return get_font("Segoe UI Emoji", size)

# ==================== 绘制工具 ====================

def draw_cyber_rect(surface, rect, color, alpha=255, fill=True, border_width=1, border_radius=0):
    """绘制赛博朋克风格矩形"""
    if fill:
        if alpha < 255:
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (*color[:3], alpha), s.get_rect(), border_radius=border_radius)
            surface.blit(s, rect.topleft)
        else:
            pygame.draw.rect(surface, color, rect, border_radius=border_radius)
    else:
        pygame.draw.rect(surface, color, rect, border_width, border_radius=border_radius)

def draw_gradient_rect(surface, rect, color_top, color_bottom, alpha=255):
    """绘制渐变矩形"""
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        ratio = y / max(1, rect.height - 1)
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * ratio)
        pygame.draw.line(s, (r, g, b, alpha), (0, y), (rect.width, y))
    surface.blit(s, rect.topleft)

def draw_text(surface, text, size, x, y, color, font_name="SimHei", align="left", bold=False):
    """绘制文本"""
    font = get_font(font_name, size, bold)
    surf = font.render(str(text), True, color)
    if align == "center":
        x = x - surf.get_width() // 2
    elif align == "right":
        x = x - surf.get_width()
    surface.blit(surf, (x, y))
    return surf.get_width(), surf.get_height()

def draw_glow_text(surface, text, size, x, y, color, glow_color=None, font_name="SimHei"):
    """绘制带光晕的文本"""
    if glow_color is None:
        glow_color = (color[0]//3, color[1]//3, color[2]//3)
    font = get_font(font_name, size)
    # 光晕层
    for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
        glow_surf = font.render(str(text), True, glow_color)
        surface.blit(glow_surf, (x + dx, y + dy))
    # 主文本
    main_surf = font.render(str(text), True, color)
    surface.blit(main_surf, (x, y))

# ==================== 按钮组件 ====================

class Button:
    """可复用的按钮组件"""
    
    def __init__(self, rect, text, color=ctx.CYAN, icon=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.icon = icon
        self.hover = False
        self.active = False
    
    def update(self, mx, my):
        """更新按钮状态"""
        self.hover = self.rect.collidepoint(mx, my)
    
    def draw(self, surface):
        """绘制按钮"""
        # 背景
        bg_color = (self.color[0]//3, self.color[1]//3, self.color[2]//3) if self.active else \
                   ((50, 55, 65) if self.hover else (30, 35, 45))
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=6)
        
        # 边框
        border_color = self.color if (self.active or self.hover) else (60, 70, 80)
        pygame.draw.rect(surface, border_color, self.rect, 2 if self.active else 1, border_radius=6)
        
        # 文本
        font = get_chinese_font(16)
        text_color = self.color if self.active else (ctx.WHITE if self.hover else ctx.GRAY)
        text_surf = font.render(self.text, True, text_color)
        
        # 居中
        text_x = self.rect.centerx - text_surf.get_width() // 2
        text_y = self.rect.centery - text_surf.get_height() // 2
        
        # 图标
        if self.icon:
            emoji_font = get_emoji_font(16)
            icon_surf = emoji_font.render(self.icon, True, text_color)
            total_w = icon_surf.get_width() + 5 + text_surf.get_width()
            icon_x = self.rect.centerx - total_w // 2
            surface.blit(icon_surf, (icon_x, text_y))
            text_x = icon_x + icon_surf.get_width() + 5
        
        surface.blit(text_surf, (text_x, text_y))
    
    def is_clicked(self, mx, my, clicked):
        """检查是否被点击"""
        return clicked and self.rect.collidepoint(mx, my)

# ==================== 滑块组件 ====================

class Slider:
    """可复用的滑块组件"""
    
    def __init__(self, rect, value=0.5, color=ctx.CYAN):
        self.rect = pygame.Rect(rect)
        self.value = value
        self.color = color
        self.dragging = False
    
    def update(self, mx, my, mouse_pressed):
        """更新滑块状态"""
        if mouse_pressed and self.rect.collidepoint(mx, my):
            self.dragging = True
        
        if self.dragging:
            if mouse_pressed:
                self.value = (mx - self.rect.x) / self.rect.width
                self.value = max(0.0, min(1.0, self.value))
            else:
                self.dragging = False
    
    def draw(self, surface):
        """绘制滑块"""
        # 轨道
        pygame.draw.rect(surface, (30, 35, 45), self.rect, border_radius=7)
        
        # 进度条
        progress_w = int(self.rect.width * self.value)
        if progress_w > 0:
            progress_rect = pygame.Rect(self.rect.x, self.rect.y, progress_w, self.rect.height)
            pygame.draw.rect(surface, self.color, progress_rect, border_radius=7)
        
        # 手柄
        handle_x = self.rect.x + progress_w
        handle_y = self.rect.centery
        pygame.draw.circle(surface, ctx.WHITE, (handle_x, handle_y), 10)
        pygame.draw.circle(surface, self.color, (handle_x, handle_y), 5)

# ==================== 复选框组件 ====================

class Checkbox:
    """可复用的复选框组件"""
    
    def __init__(self, rect, checked=False, color=ctx.CYAN):
        self.rect = pygame.Rect(rect)
        self.checked = checked
        self.color = color
    
    def draw(self, surface):
        """绘制复选框"""
        # 背景
        bg_color = (self.color[0]//4, self.color[1]//4, self.color[2]//4) if self.checked else (30, 35, 45)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=5)
        
        # 边框
        border_color = self.color if self.checked else (70, 75, 85)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=5)
        
        # 勾选标记
        if self.checked:
            cx, cy = self.rect.center
            pygame.draw.line(surface, self.color, 
                           (self.rect.x + 6, cy), 
                           (cx - 1, self.rect.bottom - 6), 3)
            pygame.draw.line(surface, self.color,
                           (cx - 1, self.rect.bottom - 6),
                           (self.rect.right - 5, self.rect.y + 6), 3)
    
    def toggle(self):
        """切换状态"""
        self.checked = not self.checked
    
    def is_clicked(self, mx, my, clicked):
        """检查是否被点击"""
        return clicked and self.rect.collidepoint(mx, my)

# ==================== 面板组件 ====================

class Panel:
    """可复用的面板组件"""
    
    def __init__(self, rect, title=None, color=ctx.CYAN):
        self.rect = pygame.Rect(rect)
        self.title = title
        self.color = color
    
    def draw(self, surface):
        """绘制面板"""
        # 背景渐变
        draw_gradient_rect(surface, self.rect, (20, 25, 35), (10, 15, 25), 240)
        
        # 边框
        pygame.draw.rect(surface, self.color, self.rect, 2, border_radius=10)
        
        # 标题
        if self.title:
            title_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 35)
            pygame.draw.rect(surface, (self.color[0]//4, self.color[1]//4, self.color[2]//4), 
                           title_rect, border_radius=10)
            font = get_chinese_font(18)
            title_surf = font.render(self.title, True, self.color)
            surface.blit(title_surf, (self.rect.x + 15, self.rect.y + 8))
