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

def draw_text(surf, text, size, x, y, color=WHITE, align="center", shadow=True, glow=False, outline=False):
    """优化的文本渲染函数 - 带缓存和增强效果"""
    if surf is None:
        log_debug("draw_text: surf is None, skipping draw")
        return pygame.Rect(x, y, 0, 0)
    
    _clean_text_cache()
    
    if glow:
        effect = "glow"
    elif outline:
        effect = "outline"
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
            # 增强的发光效果 - 多层渐变
            glow_color = (color[0]//2, color[1]//2, color[2]//2)
            bright_color = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
            glow_surf = font.render(str(text), True, glow_color)
            bright_surf = font.render(str(text), True, bright_color)
            glow_surfaces = [glow_surf, bright_surf]
        elif outline:
            # 描边效果
            outline_surf = font.render(str(text), True, (20, 20, 30))
            glow_surfaces = [outline_surf]
        elif shadow:
            # 双层阴影 - 更有深度
            shadow_surf = font.render(str(text), True, (0, 0, 0))
        
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
        # 外层发光 - 8方向
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            surf.blit(glow_surf, (text_rect.x + dx, text_rect.y + dy))
        # 内层发光 - 4方向
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            surf.blit(glow_surf, (text_rect.x + dx, text_rect.y + dy))
        # 高光层（如果有）
        if len(glow_surfaces) > 1:
            bright_surf = glow_surfaces[1]
            surf.blit(bright_surf, (text_rect.x, text_rect.y - 1))
    elif outline and glow_surfaces:
        outline_surf = glow_surfaces[0]
        # 8方向描边
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            surf.blit(outline_surf, (text_rect.x + dx, text_rect.y + dy))
    elif shadow and shadow_surf:
        # 双层阴影
        shadow_rect = text_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        surf.blit(shadow_surf, shadow_rect)
        shadow_rect.x -= 1
        shadow_rect.y -= 1
        surf.blit(shadow_surf, shadow_rect)
    
    surf.blit(text_surface, text_rect)
    return text_rect


# 高质感文字缓存
_premium_text_cache = {}
_premium_cache_max = 150

def _clean_premium_cache():
    global _premium_text_cache
    if len(_premium_text_cache) > _premium_cache_max:
        keys = list(_premium_text_cache.keys())[:_premium_cache_max // 2]
        for k in keys:
            del _premium_text_cache[k]

def draw_premium_text(surf, text, size, x, y, color=WHITE, align="center", style="default"):
    """高质感文本渲染 - 带缓存优化"""
    if surf is None:
        return pygame.Rect(x, y, 0, 0)
    
    _clean_premium_cache()
    
    # 缓存键
    cache_key = (str(text), size, color, style)
    
    if cache_key in _premium_text_cache:
        cached_surf, w, h = _premium_text_cache[cache_key]
    else:
        font = get_font(size, bold=True)
        text_surface = font.render(str(text), True, color)
        tw, th = text_surface.get_size()
        
        # 预计算需要的surface大小（留出描边/发光空间）
        padding = 6 if style == "neon" else 4
        cached_surf = pygame.Surface((tw + padding * 2, th + padding * 2), pygame.SRCALPHA)
        ox, oy = padding, padding  # 偏移量
        
        if style == "cyber":
            # 赛博风格 - 深色描边
            outline_surf = font.render(str(text), True, (15, 25, 35))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                cached_surf.blit(outline_surf, (ox + dx, oy + dy))
            cached_surf.blit(text_surface, (ox, oy))
            # 底部微光
            pygame.draw.line(cached_surf, (color[0]//2, color[1]//2, color[2]//2), 
                            (ox, oy + th), (ox + tw, oy + th), 1)
        
        elif style == "glow":
            # 发光风格 - 简化为2层
            glow_color = (color[0]//3, color[1]//3, color[2]//3)
            glow_surf = font.render(str(text), True, glow_color)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                cached_surf.blit(glow_surf, (ox + dx, oy + dy))
            bright_color = (min(255, color[0] + 30), min(255, color[1] + 30), min(255, color[2] + 30))
            bright_surf = font.render(str(text), True, bright_color)
            cached_surf.blit(bright_surf, (ox, oy))
        
        elif style == "metal":
            # 金属质感
            shadow_surf = font.render(str(text), True, (0, 0, 0))
            cached_surf.blit(shadow_surf, (ox + 2, oy + 2))
            cached_surf.blit(text_surface, (ox, oy))
            bright_color = (min(255, color[0] + 60), min(255, color[1] + 60), min(255, color[2] + 60))
            highlight_surf = font.render(str(text), True, bright_color)
            # 上半部分高光
            for px in range(tw):
                for py in range(th // 2):
                    cached_surf.blit(highlight_surf, (ox, oy - 1), 
                                    pygame.Rect(0, 0, tw, th // 2), special_flags=pygame.BLEND_RGBA_MAX)
                    break
                break
        
        elif style == "neon":
            # 霓虹风格 - 简化为2层发光
            glow_color = (color[0]//4, color[1]//4, color[2]//4)
            glow_surf = font.render(str(text), True, glow_color)
            # 外层发光
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                cached_surf.blit(glow_surf, (ox + dx, oy + dy))
            # 内层
            mid_color = (color[0]//2, color[1]//2, color[2]//2)
            mid_surf = font.render(str(text), True, mid_color)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                cached_surf.blit(mid_surf, (ox + dx, oy + dy))
            # 主体
            bright_surf = font.render(str(text), True, (min(255, color[0]+50), min(255, color[1]+50), min(255, color[2]+50)))
            cached_surf.blit(bright_surf, (ox, oy))
        
        else:
            # 默认 - 简单描边
            shadow_surf = font.render(str(text), True, (0, 0, 0))
            cached_surf.blit(shadow_surf, (ox + 2, oy + 2))
            outline_surf = font.render(str(text), True, (20, 30, 40))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                cached_surf.blit(outline_surf, (ox + dx, oy + dy))
            cached_surf.blit(text_surface, (ox, oy))
        
        w, h = cached_surf.get_size()
        _premium_text_cache[cache_key] = (cached_surf, w, h)
    
    # 计算位置（考虑padding偏移）
    padding = 6 if style == "neon" else 4
    if align == "center":
        blit_x = x - w // 2
        blit_y = y - padding
    elif align == "left":
        blit_x = x - padding
        blit_y = y - padding
    elif align == "right":
        blit_x = x - w + padding
        blit_y = y - padding
    
    surf.blit(cached_surf, (blit_x, blit_y))
    return pygame.Rect(blit_x + padding, blit_y + padding, w - padding * 2, h - padding * 2)


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


# ==============================================================================
#   美化版HUD进度条系统
# ==============================================================================
import math

def draw_premium_bar(surf, x, y, w, h, pct, color, bg_color=(20, 25, 35), 
                     icon=None, label=None, value_text=None, glow=True, 
                     animate_frame=0, bar_style="shield"):
    """
    绘制高级美化进度条
    bar_style: "shield"=护盾, "health"=血量, "energy"=能量, "special"=特殊资源
    """
    pct = max(0, min(pct, 100))
    
    # 创建Surface用于混合
    bar_surf = pygame.Surface((w + 40, h + 20), pygame.SRCALPHA)
    
    # === 背景层 - 带渐变 ===
    bg_points = [(12, 0), (w + 12, 0), (w, h), (0, h)]
    
    # 绘制深色背景
    for i in range(h):
        ratio = i / max(1, h - 1)
        r = int(bg_color[0] * (1 - ratio * 0.3))
        g = int(bg_color[1] * (1 - ratio * 0.3))
        b = int(bg_color[2] * (1 - ratio * 0.3))
        # 计算当前行的倾斜范围
        left_x = int(12 - 12 * ratio)
        right_x = int(w + 12 - 12 * ratio)
        pygame.draw.line(bar_surf, (r, g, b, 200), (left_x, i), (right_x, i))
    
    # === 填充层 - 带渐变和光泽 ===
    fill_w = int((pct / 100.0) * w)
    if fill_w > 2:
        # 主色填充 - 垂直渐变
        for i in range(h):
            ratio = i / max(1, h - 1)
            # 上半部分更亮，下半部分更暗
            if ratio < 0.5:
                brightness = 1.0 + (0.5 - ratio) * 0.4
            else:
                brightness = 1.0 - (ratio - 0.5) * 0.3
            
            r = min(255, int(color[0] * brightness))
            g = min(255, int(color[1] * brightness))
            b = min(255, int(color[2] * brightness))
            
            left_x = int(12 - 12 * ratio)
            right_x = int(12 + fill_w - 12 * ratio)
            pygame.draw.line(bar_surf, (r, g, b, 255), (left_x, i), (right_x, i))
        
        # 顶部高光条纹
        highlight_h = max(2, h // 4)
        for i in range(highlight_h):
            alpha = int(80 * (1 - i / highlight_h))
            ratio = i / max(1, h - 1)
            left_x = int(12 - 12 * ratio) + 2
            right_x = int(12 + fill_w - 12 * ratio) - 2
            if right_x > left_x:
                pygame.draw.line(bar_surf, (255, 255, 255, alpha), (left_x, i + 1), (right_x, i + 1))
        
        # 外发光效果（高能量时）
        if glow and pct > 20:
            glow_intensity = int(30 + 40 * (pct / 100))
            pulse = abs(math.sin(animate_frame * 0.05)) * 0.3 + 0.7 if animate_frame else 1.0
            glow_surf = pygame.Surface((fill_w + 10, h + 10), pygame.SRCALPHA)
            glow_color = (color[0], color[1], color[2], int(glow_intensity * pulse))
            pygame.draw.rect(glow_surf, glow_color, (2, 2, fill_w + 6, h + 6))
            surf.blit(glow_surf, (x - 3, y - 3), special_flags=pygame.BLEND_RGBA_ADD)
    
    # === 边框层 - 双层边框 ===
    # 外边框（暗色）
    outer_points = [(12, 0), (w + 12, 0), (w, h), (0, h)]
    pygame.draw.polygon(bar_surf, (60, 70, 90, 255), outer_points, 2)
    # 内边框（亮色高光）
    inner_points = [(13, 1), (w + 11, 1), (w - 1, h - 1), (1, h - 1)]
    pygame.draw.polygon(bar_surf, (100, 110, 130, 100), inner_points, 1)
    
    # === 装饰元素 ===
    # 左侧装饰点
    pygame.draw.circle(bar_surf, color, (6, h // 2), 3)
    pygame.draw.circle(bar_surf, (255, 255, 255), (6, h // 2), 1)
    
    # 右端装饰线
    if fill_w > 10:
        end_x = 12 + fill_w - 6
        end_ratio = (h // 2) / max(1, h - 1)
        end_x_adj = int(end_x - 12 * end_ratio)
        pygame.draw.line(bar_surf, (255, 255, 255, 150), (end_x_adj, 2), (end_x_adj, h - 2), 2)
    
    # 绘制到屏幕
    surf.blit(bar_surf, (x, y))
    
    # === 图标（如果有）===
    if icon:
        # icon是一个字符或emoji
        draw_text(surf, icon, h + 4, x - 5, y - 3, color, align="right", glow=True)
    
    return pygame.Rect(x, y, w + 12, h)


def draw_hud_panel_bg(surf, x, y, w, h, alpha=180, border_color=(80, 100, 140)):
    """绘制HUD面板背景"""
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    
    # 渐变背景
    for i in range(h):
        ratio = i / max(1, h - 1)
        r = int(15 + 10 * ratio)
        g = int(20 + 15 * ratio)
        b = int(35 + 20 * ratio)
        a = int(alpha * (0.9 + 0.1 * ratio))
        pygame.draw.line(panel, (r, g, b, a), (0, i), (w, i))
    
    # 底部高光线
    pygame.draw.line(panel, (*border_color, 60), (5, h - 1), (w - 5, h - 1))
    
    # 角落装饰
    corner_size = 8
    # 左上
    pygame.draw.line(panel, border_color, (0, corner_size), (0, 0))
    pygame.draw.line(panel, border_color, (0, 0), (corner_size, 0))
    # 右上
    pygame.draw.line(panel, border_color, (w - corner_size, 0), (w - 1, 0))
    pygame.draw.line(panel, border_color, (w - 1, 0), (w - 1, corner_size))
    # 左下
    pygame.draw.line(panel, (*border_color, 100), (0, h - corner_size), (0, h - 1))
    pygame.draw.line(panel, (*border_color, 100), (0, h - 1), (corner_size, h - 1))
    
    surf.blit(panel, (x, y))


def draw_status_icon(surf, x, y, size, icon_type, color, frame=0):
    """绘制状态图标"""
    icon_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    
    if icon_type == "shield":
        # 盾牌图标
        points = [(cx, 2), (size - 4, cy - 2), (size - 4, cy + 4), (cx, size - 2), (4, cy + 4), (4, cy - 2)]
        pygame.draw.polygon(icon_surf, (*color, 200), points)
        pygame.draw.polygon(icon_surf, (255, 255, 255), points, 1)
        # 内部光泽
        pygame.draw.line(icon_surf, (255, 255, 255, 100), (cx, 5), (cx, size - 5))
    
    elif icon_type == "heart":
        # 心形图标
        pygame.draw.circle(icon_surf, color, (cx - 3, cy - 1), 5)
        pygame.draw.circle(icon_surf, color, (cx + 3, cy - 1), 5)
        pygame.draw.polygon(icon_surf, color, [(cx - 7, cy), (cx, size - 3), (cx + 7, cy)])
        # 高光
        pygame.draw.circle(icon_surf, (255, 255, 255, 150), (cx - 4, cy - 3), 2)
    
    elif icon_type == "bolt":
        # 闪电图标（推进器）
        points = [(cx + 2, 2), (cx - 4, cy + 2), (cx, cy + 2), (cx - 2, size - 2), (cx + 4, cy - 2), (cx, cy - 2)]
        pygame.draw.polygon(icon_surf, color, points)
        pygame.draw.polygon(icon_surf, (255, 255, 255), points, 1)
    
    elif icon_type == "flame":
        # 火焰图标
        pulse = abs(math.sin(frame * 0.1)) * 0.2 + 0.8
        # 外焰
        pygame.draw.ellipse(icon_surf, (*color[:3], int(150 * pulse)), (cx - 5, 4, 10, size - 4))
        # 内焰
        inner_color = (min(255, color[0] + 50), min(255, color[1] + 80), color[2])
        pygame.draw.ellipse(icon_surf, inner_color, (cx - 3, 6, 6, size - 8))
    
    elif icon_type == "skull":
        # 骷髅图标（血契等）
        pygame.draw.circle(icon_surf, color, (cx, cy - 2), 6)
        pygame.draw.rect(icon_surf, color, (cx - 4, cy + 2, 8, 5))
        # 眼睛
        pygame.draw.circle(icon_surf, (0, 0, 0), (cx - 2, cy - 3), 2)
        pygame.draw.circle(icon_surf, (0, 0, 0), (cx + 2, cy - 3), 2)
    
    elif icon_type == "star":
        # 星星图标
        import math as m
        for i in range(5):
            angle1 = m.radians(-90 + i * 72)
            angle2 = m.radians(-90 + i * 72 + 36)
            x1 = cx + int(m.cos(angle1) * 7)
            y1 = cy + int(m.sin(angle1) * 7)
            x2 = cx + int(m.cos(angle2) * 3)
            y2 = cy + int(m.sin(angle2) * 3)
            pygame.draw.line(icon_surf, color, (cx, cy), (x1, y1), 2)
            pygame.draw.line(icon_surf, (*color, 150), (x1, y1), (x2, y2), 1)
    
    surf.blit(icon_surf, (x, y))


def draw_premium_ult_bar(surf, x, y, w, h, pct, color, label, key_text, 
                          ready=False, cooldown=0, animate_frame=0):
    """
    绘制高级大招能量条
    ready: 是否满能量可释放
    cooldown: CD剩余秒数
    """
    pct = max(0, min(pct, 100))
    
    # === 背景层 ===
    bar_surf = pygame.Surface((w + 50, h + 8), pygame.SRCALPHA)
    
    # 倾斜背景
    tilt = 6
    bg_points = [(tilt, 0), (w + tilt, 0), (w, h), (0, h)]
    
    # 渐变背景
    for i in range(h):
        ratio = i / max(1, h - 1)
        left_x = int(tilt - tilt * ratio)
        right_x = int(w + tilt - tilt * ratio)
        r, g, b = 20, 25, 35
        # 底部稍亮
        r = int(r + 10 * ratio)
        g = int(g + 10 * ratio)
        b = int(b + 10 * ratio)
        pygame.draw.line(bar_surf, (r, g, b, 220), (left_x, i), (right_x, i))
    
    # === 填充层 ===
    fill_w = int((pct / 100.0) * w)
    if fill_w > 2:
        for i in range(h):
            ratio = i / max(1, h - 1)
            # 光泽效果
            if ratio < 0.4:
                brightness = 1.2 - ratio * 0.3
            else:
                brightness = 0.95 - (ratio - 0.4) * 0.2
            
            r = min(255, int(color[0] * brightness))
            g = min(255, int(color[1] * brightness))
            b = min(255, int(color[2] * brightness))
            
            left_x = int(tilt - tilt * ratio)
            right_x = int(tilt + fill_w - tilt * ratio)
            pygame.draw.line(bar_surf, (r, g, b, 255), (left_x, i), (right_x, i))
        
        # 顶部高光
        highlight_h = max(2, h // 3)
        for i in range(highlight_h):
            alpha = int(100 * (1 - i / highlight_h))
            ratio = i / max(1, h - 1)
            left_x = int(tilt - tilt * ratio) + 2
            right_x = int(tilt + fill_w - tilt * ratio) - 1
            if right_x > left_x:
                pygame.draw.line(bar_surf, (255, 255, 255, alpha), (left_x, i + 1), (right_x, i + 1))
        
        # 满能量时的脉冲发光
        if ready:
            pulse = abs(math.sin(animate_frame * 0.08)) * 0.5 + 0.5
            glow_color = (color[0], color[1], color[2], int(80 * pulse))
            glow_surf = pygame.Surface((fill_w + 6, h + 4), pygame.SRCALPHA)
            glow_surf.fill(glow_color)
            surf.blit(glow_surf, (x - 2, y - 2), special_flags=pygame.BLEND_RGBA_ADD)
    
    # === 边框 ===
    border_color = (200, 200, 220) if ready else (80, 90, 110)
    pygame.draw.polygon(bar_surf, border_color, bg_points, 2)
    
    # 满能量边框闪烁
    if ready:
        pulse = abs(math.sin(animate_frame * 0.1))
        glow_points = [(tilt - 1, -1), (w + tilt + 1, -1), (w + 1, h + 1), (-1, h + 1)]
        glow_color = (*color, int(150 * pulse))
        pygame.draw.polygon(bar_surf, glow_color, glow_points, 1)
    
    # === 装饰 ===
    # 左端装饰圆点
    pygame.draw.circle(bar_surf, color, (3, h // 2), 2)
    
    # 右端能量标记线
    if fill_w > 5:
        end_x = tilt + fill_w - 3
        end_ratio = (h // 2) / max(1, h - 1)
        end_x_adj = int(end_x - tilt * end_ratio)
        pygame.draw.line(bar_surf, (255, 255, 255, 180), (end_x_adj, 2), (end_x_adj, h - 2), 1)
    
    # 绘制到屏幕
    surf.blit(bar_surf, (x, y))
    
    # === CD覆盖层 ===
    if cooldown > 0:
        cd_overlay = pygame.Surface((w + tilt, h), pygame.SRCALPHA)
        cd_overlay.fill((0, 0, 0, 160))
        surf.blit(cd_overlay, (x, y))
        # CD文字
        from utils.ui import draw_text
        cd_text = f"CD {cooldown:.1f}s"
        draw_text(surf, cd_text, max(10, h - 2), x + w // 2, y + 1, (255, 80, 80), align="center")
    
    return pygame.Rect(x, y, w, h)


def draw_premium_weapon_slot(surf, x, y, size, weapon_info, is_current=False, 
                              cooldown=0, animate_frame=0):
    """
    绘制高级武器槽 - 斜切六边形赛博风格
    weapon_info: None或包含 name, color 的字典
    is_current: 是否当前选中
    cooldown: CD剩余秒数
    """
    padding = 4
    total_size = size + padding * 2
    slot_surf = pygame.Surface((total_size, total_size), pygame.SRCALPHA)
    
    # 斜切角大小
    cut = 8
    
    # === 六边形轮廓点 ===
    # 左上斜切，右下斜切的六边形
    cx, cy = padding, padding
    points = [
        (cx + cut, cy),           # 左上斜切后的顶点
        (cx + size, cy),          # 右上
        (cx + size, cy + size - cut),  # 右下斜切前
        (cx + size - cut, cy + size),  # 右下斜切后
        (cx, cy + size),          # 左下
        (cx, cy + cut)            # 左上斜切前
    ]
    
    # === 背景填充 ===
    if weapon_info:
        base_color = weapon_info.get('color', (80, 80, 100))
    else:
        base_color = (35, 40, 50)
    
    # 渐变背景多边形
    bg_surf = pygame.Surface((total_size, total_size), pygame.SRCALPHA)
    for i in range(size):
        ratio = i / max(1, size - 1)
        # 从上到下渐变
        brightness = 0.9 - ratio * 0.3
        r = int(base_color[0] * brightness)
        g = int(base_color[1] * brightness)
        b = int(base_color[2] * brightness)
        
        # 计算当前行在六边形内的左右边界
        y_pos = cy + i
        # 简化处理：直接填充矩形区域
        left_edge = cx + (cut - int(cut * i / cut)) if i < cut else cx
        right_edge = cx + size
        if i > size - cut:
            right_edge = cx + size - (i - (size - cut))
        
        pygame.draw.line(bg_surf, (r, g, b, 220), (left_edge, y_pos), (right_edge, y_pos))
    
    # 用多边形裁剪
    mask_surf = pygame.Surface((total_size, total_size), pygame.SRCALPHA)
    pygame.draw.polygon(mask_surf, (255, 255, 255, 255), points)
    bg_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    slot_surf.blit(bg_surf, (0, 0))
    
    # 直接绘制填充多边形作为基础
    pygame.draw.polygon(slot_surf, (*base_color, 200), points)
    
    # 顶部高光区域
    highlight_points = [
        (cx + cut, cy + 1),
        (cx + size - 1, cy + 1),
        (cx + size - 1, cy + size // 3),
        (cx + 1, cy + size // 3),
        (cx + 1, cy + cut)
    ]
    pygame.draw.polygon(slot_surf, (255, 255, 255, 30), highlight_points)
    
    # === 边框系统 ===
    if is_current:
        # 选中状态 - 发光效果
        pulse = abs(math.sin(animate_frame * 0.08))
        
        # 外发光层
        glow_points = [(p[0] - 2, p[1] - 2) if i < 2 else (p[0] + 2, p[1] + 2) if i < 4 else (p[0] - 2, p[1] + 2) for i, p in enumerate(points)]
        glow_color = (80, 255, 140, int(40 + 30 * pulse))
        pygame.draw.polygon(slot_surf, glow_color, points, 4)
        
        # 主边框 - 亮绿色
        pygame.draw.polygon(slot_surf, (100, 255, 150), points, 2)
        
        # 角落装饰线
        accent_color = (180, 255, 200)
        # 左上角
        pygame.draw.line(slot_surf, accent_color, (cx + cut, cy), (cx + cut + 10, cy), 2)
        pygame.draw.line(slot_surf, accent_color, (cx, cy + cut), (cx, cy + cut + 10), 2)
        # 右下角  
        pygame.draw.line(slot_surf, accent_color, (cx + size - cut, cy + size), (cx + size - cut - 10, cy + size), 2)
        pygame.draw.line(slot_surf, accent_color, (cx + size, cy + size - cut), (cx + size, cy + size - cut - 10), 2)
        
        # 内部装饰点
        pygame.draw.circle(slot_surf, (150, 255, 200), (cx + 5, cy + size - 5), 2)
        pygame.draw.circle(slot_surf, (150, 255, 200), (cx + size - 5, cy + 5), 2)
    else:
        # 未选中 - 暗色边框
        pygame.draw.polygon(slot_surf, (60, 70, 90), points, 1)
        # 顶边高光
        pygame.draw.line(slot_surf, (90, 100, 120), (cx + cut + 2, cy), (cx + size - 2, cy), 1)
    
    # === 武器名称 ===
    center_x = cx + size // 2
    center_y = cy + size // 2
    
    if weapon_info:
        w_name = weapon_info.get('name', '？')[:2]
        font = pygame.font.SysFont(["microsoftyahei", "simhei"], 14, bold=True)
        
        # 文字阴影
        shadow_surf = font.render(w_name, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(center_x + 1, center_y + 1))
        slot_surf.blit(shadow_surf, shadow_rect)
        
        # 主文字
        text_surf = font.render(w_name, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(center_x, center_y))
        slot_surf.blit(text_surf, text_rect)
    else:
        # 空槽标记 - X形状
        line_color = (50, 60, 70)
        pygame.draw.line(slot_surf, line_color, (cx + 12, cy + 12), (cx + size - 12, cy + size - 12), 2)
        pygame.draw.line(slot_surf, line_color, (cx + size - 12, cy + 12), (cx + 12, cy + size - 12), 2)
    
    # 绘制到屏幕
    surf.blit(slot_surf, (x - padding, y - padding))
    
    # === CD覆盖 ===
    if cooldown > 0:
        cd_surf = pygame.Surface((total_size, total_size), pygame.SRCALPHA)
        pygame.draw.polygon(cd_surf, (0, 0, 0, 150), points)
        surf.blit(cd_surf, (x - padding, y - padding))
        
        # CD数字
        cd_text = f"{cooldown:.1f}"
        font_cd = pygame.font.SysFont(["consolas", "monaco"], 12, bold=True)
        cd_text_surf = font_cd.render(cd_text, True, (255, 100, 100))
        cd_rect = cd_text_surf.get_rect(center=(x + size // 2, y + size // 2))
        surf.blit(cd_text_surf, cd_rect)
    
    return pygame.Rect(x, y, size, size)


def draw_wingman_indicator(surf, x, y, current, maximum, animate_frame=0):
    """绘制僚机指示器"""
    # 计算总宽度
    dot_size = 10
    gap = 4
    total_w = maximum * dot_size + (maximum - 1) * gap
    start_x = x - total_w // 2
    
    # 绘制每个僚机槽位
    for i in range(maximum):
        dx = start_x + i * (dot_size + gap)
        
        if i < current:
            # 有僚机 - 青色发光圆点
            pulse = abs(math.sin(animate_frame * 0.05 + i * 0.5))
            
            # 发光背景
            glow_color = (0, 180 + int(50 * pulse), 220 + int(35 * pulse))
            pygame.draw.circle(surf, glow_color, (dx + dot_size // 2, y), dot_size // 2 + 1)
            
            # 内部亮点
            pygame.draw.circle(surf, (150, 255, 255), (dx + dot_size // 2, y), 2)
        else:
            # 空槽位 - 暗色空心圆
            pygame.draw.circle(surf, (50, 60, 70), (dx + dot_size // 2, y), dot_size // 2)
            pygame.draw.circle(surf, (80, 90, 100), (dx + dot_size // 2, y), dot_size // 2, 1)
    
    # 顶部标签
    from utils.ui import draw_text
    draw_text(surf, "僚机", 10, x, y - 15, (100, 200, 220), align="center")
