"""
UI绘制工具模块 - 字体、文本渲染、各种UI组件绘制
"""
import pygame

from config import WHITE
from utils.core import log_debug, log_error

# ==============================================================================
#   字体工具
# ==============================================================================
def get_font(size, bold=False):
    font_names = ["roboto", "noto sans", "microsoftyahei", "simhei", "arial"]
    return pygame.font.SysFont(font_names, int(size), bold=bold)

# ==============================================================================
#   文本渲染缓存系统
# ==============================================================================
_text_cache = {}
_cache_frame_counter = 0
_MAX_CACHE_SIZE = 500
_CACHE_CLEAN_INTERVAL = 60

def _get_cache_key(text, size, color, effect):
    """生成缓存键"""
    return (str(text), int(size), tuple(color), effect)

def _clean_text_cache():
    """智能清理缓存"""
    global _text_cache, _cache_frame_counter
    _cache_frame_counter += 1
    
    if _cache_frame_counter >= _CACHE_CLEAN_INTERVAL or len(_text_cache) > _MAX_CACHE_SIZE:
        if len(_text_cache) > _MAX_CACHE_SIZE // 2:
            _text_cache.clear()
        _cache_frame_counter = 0

def draw_text(surf, text, size, x, y, color=WHITE, align="center", shadow=True, glow=False):
    """优化的文本渲染函数 - 带缓存"""
    if surf is None:
        log_debug("draw_text: surf is None, skipping draw")
        return pygame.Rect(x, y, 0, 0)
    
    _clean_text_cache()
    
    if glow:
        effect = "glow"
    elif shadow:
        effect = "shadow"
    else:
        effect = "plain"
    
    cache_key = _get_cache_key(text, size, color, effect)
    
    if cache_key in _text_cache:
        text_surface, shadow_surf, glow_surfaces = _text_cache[cache_key]
    else:
        font = get_font(size, bold=True)
        text_surface = font.render(str(text), True, color)
        
        shadow_surf = None
        glow_surfaces = None
        
        if glow:
            glow_color = (color[0]//2, color[1]//2, color[2]//2)
            glow_surf = font.render(str(text), True, glow_color)
            glow_surfaces = [glow_surf]
        elif shadow:
            shadow_surf = font.render(str(text), True, (0,0,0))
        
        _text_cache[cache_key] = (text_surface, shadow_surf, glow_surfaces)
    
    text_rect = text_surface.get_rect()
    if align == "center":
        text_rect.midtop = (x, y)
    elif align == "left":
        text_rect.topleft = (x, y)
    elif align == "right":
        text_rect.topright = (x, y)
    
    if glow and glow_surfaces:
        glow_surf = glow_surfaces[0]
        surf.blit(glow_surf, (text_rect.x-1, text_rect.y))
        surf.blit(glow_surf, (text_rect.x+1, text_rect.y))
        surf.blit(glow_surf, (text_rect.x, text_rect.y-1))
        surf.blit(glow_surf, (text_rect.x, text_rect.y+1))
    elif shadow and shadow_surf:
        shadow_rect = text_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        surf.blit(shadow_surf, shadow_rect)
    
    surf.blit(text_surface, text_rect)
    return text_rect


def draw_mono_text(surf, text, size, x, y, color=WHITE, align="center", shadow=True):
    """Draw fixed-width (monospace) text"""
    monos = ["consolas", "courier new", "monaco"]
    font = pygame.font.SysFont(monos, int(size), bold=True)
    text_surface = font.render(str(text), True, color)
    rect = text_surface.get_rect()
    if align == "center": rect.midtop = (x, y)
    elif align == "left": rect.topleft = (x, y)
    elif align == "right": rect.topright = (x, y)
    if shadow:
        shadow_surf = font.render(str(text), True, (0,0,0))
        shadow_rect = rect.copy(); shadow_rect.x += 2; shadow_rect.y += 2
        surf.blit(shadow_surf, shadow_rect)
    surf.blit(text_surface, rect)
    return rect


def draw_spaced_text(surf, text, size, x, y, color=WHITE, align="center", spacing=2, shadow=True):
    """Draw text with increased letter-spacing"""
    font = get_font(size, bold=True)
    total_w = sum(font.size(c)[0] for c in text) + spacing * (len(text) - 1)
    if align == "center": start_x = x - total_w//2
    elif align == "left": start_x = x
    else: start_x = x - total_w
    cur_x = start_x
    for ch in text:
        ch_surf = font.render(ch, True, color)
        ch_rect = ch_surf.get_rect()
        ch_rect.topleft = (cur_x, y)
        if shadow:
            shadow_s = font.render(ch, True, (0,0,0))
            surf.blit(shadow_s, (cur_x+2, y+2))
        surf.blit(ch_surf, ch_rect)
        cur_x += ch_rect.width + spacing
    return pygame.Rect(start_x, y, total_w, font.get_linesize())

def draw_cyber_rect(surf, rect, color, alpha=255, cut_size=10, border_width=0, fill=True):
    """绘制赛博风格矩形"""
    if isinstance(rect, tuple):
        x, y, w, h = rect
    else:
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
    
    w = int(max(1, w))
    h = int(max(1, h))
    x = int(x)
    y = int(y)
        
    points = [(x + cut_size, y), (x + w, y), (x + w, y + h - cut_size), (x + w - cut_size, y + h), (x, y + h), (x, y + cut_size)]
    if surf is None:
        log_debug("draw_cyber_rect: surf is None, skipping draw")
        return
    if fill:
        try:
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            if len(color) == 4: draw_color = color
            else: draw_color = (*color, alpha)
            local_points = [(p[0]-x, p[1]-y) for p in points]
            pygame.draw.polygon(s, draw_color, local_points)
            surf.blit(s, (x, y))
        except Exception as e:
            log_error(f"draw_cyber_rect fill error: {e}, w={w}, h={h}")
            
    if border_width > 0:
        try:
            pygame.draw.polygon(surf, color, points, border_width)
        except Exception as e:
            log_error(f"draw_cyber_rect border error: {e}")

def draw_modern_bar(surf, x, y, pct, color, w=200, h=15, label=None, show_bg=True):
    """绘制现代进度条"""
    pct = max(0, min(pct, 100))
    if show_bg:
        bg_points = [(x, y+h), (x+w, y+h), (x+w+h/2, y), (x+h/2, y)]
        min_x = x
        min_y = y
        max_x = x + w + h/2
        max_y = y + h
        surf_w = int(max_x - min_x + 1)
        surf_h = int(max_y - min_y + 1)
        
        s = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        local_points = [(p[0]-min_x, p[1]-min_y) for p in bg_points]
        
        pygame.draw.polygon(s, (20, 20, 30, 150), local_points)
        surf.blit(s, (min_x, min_y))
        pygame.draw.polygon(surf, (100, 100, 100), bg_points, 1)
    fill_w = int((pct / 100) * w)
    if fill_w > 0:
        fill_points = [(x, y+h), (x+fill_w, y+h), (x+fill_w+h/2, y), (x+h/2, y)]
        pygame.draw.polygon(surf, color, fill_points)
        highlight_points = [(x+h/2, y), (x+fill_w+h/2, y), (x+fill_w+h/2, y+2), (x+h/2+2, y+2)]
        pygame.draw.polygon(surf, (255, 255, 255, 100), highlight_points)
    if label:
        draw_text(surf, label, 14, x + w + h + 5, y, WHITE, align="left", shadow=True)


def draw_slanted_bar(surf, x, y, w, h, pct, color, bg_color=(30,30,40), tilt=10, border_color=None, border_width=1):
    """Draw a slanted/parallelogram progress bar"""
    pct = max(0, min(pct, 100))
    points_bg = [(x + tilt, y), (x + w + tilt, y), (x + w, y + h), (x, y + h)]
    s = pygame.Surface((w + tilt + 4, h + 4), pygame.SRCALPHA)
    pygame.draw.polygon(s, (*bg_color, 220), [(p[0]-x, p[1]-y) for p in points_bg])
    fill_w = int((pct / 100.0) * w)
    if fill_w > 0:
        points_fill = [(x + tilt, y), (x + tilt + fill_w, y), (x + fill_w, y + h), (x, y + h)]
        pygame.draw.polygon(s, (*color, 255), [(p[0]-x, p[1]-y) for p in points_fill])
    surf.blit(s, (x, y), special_flags=pygame.BLEND_RGBA_ADD)
    if border_color and border_width > 0:
        pygame.draw.polygon(surf, border_color, points_bg, border_width)
    return points_bg


def draw_rounded_rect_with_gradient(surf, rect, start_color, end_color, radius=4, border_color=None, border_width=1, alpha=200):
    """Draw a rounded rectangle with a vertical gradient"""
    if isinstance(rect, tuple):
        x, y, w, h = rect
    else:
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
    g = pygame.Surface((w, h), pygame.SRCALPHA)
    def to_rgba(c):
        if len(c) == 3: return (c[0], c[1], c[2], alpha)
        return c
    s_col = to_rgba(start_color)
    e_col = to_rgba(end_color)
    for i in range(h):
        t = i / float(max(1, h-1))
        r = int(s_col[0] + (e_col[0] - s_col[0]) * t)
        gcol = int(s_col[1] + (e_col[1] - s_col[1]) * t)
        b = int(s_col[2] + (e_col[2] - s_col[2]) * t)
        a = int(s_col[3] + (e_col[3] - s_col[3]) * t)
        pygame.draw.line(g, (r, gcol, b, a), (0, i), (w, i))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255,255,255,255), (0,0,w,h), border_radius=radius)
    g.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(g, (x, y))
    if border_color and border_width > 0:
        pygame.draw.rect(surf, border_color, (x, y, w, h), border_width, border_radius=radius)


def draw_scanline_overlay(surf, rect, spacing=6, color=(255,255,255,8)):
    """Draw subtle horizontal scanlines"""
    if isinstance(rect, tuple):
        x, y, w, h = rect
    else:
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(0, h, spacing):
        pygame.draw.line(s, color, (0, i), (w, i))
    surf.blit(s, (x, y), special_flags=pygame.BLEND_RGBA_ADD)


def draw_badge(surf, center_x, center_y, diameter, color, text=None, text_color=WHITE, font_size=9):
    """Draw a circular badge with a short label"""
    s = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    pygame.draw.circle(s, color, (diameter//2, diameter//2), diameter//2)
    surf.blit(s, (center_x - diameter//2, center_y - diameter//2))
    if text:
        draw_text(surf, text, font_size, center_x, center_y - font_size//2, text_color, align="center", shadow=False)
