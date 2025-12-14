# -*- coding: utf-8 -*-
"""
辉耀天女·斯塔德 - 专属子弹模块
虹幕连闪，皇辉升格，光之女皇

特性：
- 月虹光梭：远程射击，命中展开辉耀残痕
- 辉耀残痕：光板留场3s，自动发射追踪月光弹
- 皇辉束：真伤穿透，可击落弹幕
- 皇辉升格：5层展开皇辉领域
- Rainbow Crash：击杀彩虹碎裂特效
"""
import pygame
import math
import random
from config import all_sprites, mobs, WIDTH, HEIGHT

# ==================== 主题配色 ====================
STARADIA_BULLET_THEMES = {
    "default": {
        "rainbow": (255, 180, 220),      # 女皇虹
        "gold": (255, 215, 120),         # 月耀金
        "beam": (255, 200, 255),         # 皇辉束
        "trail": (255, 170, 200),        # 拖尾
        "particle": (255, 200, 230),     # 粒子
        "glow": (255, 220, 240),         # 光晕
    },
    "empress": {
        # 女皇降临 - 纯白棱镜
        "rainbow": (255, 255, 255),
        "gold": (255, 230, 180),
        "beam": (255, 250, 255),
        "trail": (240, 230, 255),
        "particle": (255, 255, 255),
        "glow": (255, 250, 255),
    },
    "prismatic": {
        # 棱镜幻彩 - 动态彩虹（使用时间变化）
        "rainbow": (255, 100, 200),
        "gold": (100, 255, 200),
        "beam": (200, 100, 255),
        "trail": (255, 200, 100),
        "particle": (100, 200, 255),
        "glow": (255, 150, 255),
    },
    "twilight": {
        # 暮光女神 - 紫金渐变
        "rainbow": (180, 100, 220),
        "gold": (255, 200, 100),
        "beam": (200, 120, 255),
        "trail": (220, 150, 200),
        "particle": (190, 130, 210),
        "glow": (210, 160, 230),
    },
    "aurora": {
        # 极光圣辉 - 青绿紫
        "rainbow": (100, 255, 220),
        "gold": (100, 255, 150),
        "beam": (180, 100, 255),
        "trail": (120, 230, 200),
        "particle": (100, 200, 255),
        "glow": (150, 255, 220),
    },
    "celestial": {
        # 天界使者 - 星辰银蓝
        "rainbow": (220, 230, 255),
        "gold": (100, 150, 255),
        "beam": (180, 200, 255),
        "trail": (200, 210, 255),
        "particle": (230, 240, 255),
        "glow": (200, 220, 255),
    },
    "dawn": {
        # 黎明曙光 - 橙粉金
        "rainbow": (255, 180, 100),
        "gold": (255, 150, 180),
        "beam": (255, 200, 150),
        "trail": (255, 170, 130),
        "particle": (255, 190, 160),
        "glow": (255, 220, 180),
    },
    "moonlight": {
        # 月华流转 - 冷月银白
        "rainbow": (230, 240, 255),
        "gold": (200, 220, 255),
        "beam": (240, 245, 255),
        "trail": (220, 230, 250),
        "particle": (235, 240, 255),
        "glow": (245, 250, 255),
    },
    "rainbow_fury": {
        # 虹怒 - 激烈彩虹
        "rainbow": (255, 80, 120),
        "gold": (255, 200, 50),
        "beam": (255, 100, 255),
        "trail": (255, 150, 80),
        "particle": (80, 255, 150),
        "glow": (255, 120, 200),
    },
    "ethereal": {
        # 空灵仙子 - 淡紫梦幻
        "rainbow": (220, 180, 255),
        "gold": (255, 200, 230),
        "beam": (230, 190, 255),
        "trail": (210, 170, 245),
        "particle": (225, 185, 250),
        "glow": (235, 200, 255),
    },
    "solar_flare": {
        # 日耀烈焰 - 太阳金红
        "rainbow": (255, 200, 50),
        "gold": (255, 120, 30),
        "beam": (255, 160, 60),
        "trail": (255, 140, 40),
        "particle": (255, 180, 80),
        "glow": (255, 220, 100),
    },
    "void_empress": {
        # 虚空女皇 - 暗紫深邃
        "rainbow": (80, 30, 120),
        "gold": (120, 40, 100),
        "beam": (100, 50, 150),
        "trail": (90, 35, 110),
        "particle": (110, 60, 140),
        "glow": (130, 70, 160),
    },
    # ===== 子弹涂装（来自customization.py的BULLET_THEMES） =====
    "rainbow_shuttle": {
        # 虹梭 - 彩虹飞梭
        "rainbow": (255, 100, 150),
        "gold": (255, 200, 100),
        "beam": (200, 150, 255),
        "trail": (255, 150, 200),
        "particle": (150, 200, 255),
        "glow": (255, 180, 220),
    },
    "empress_blade": {
        # 女皇剑刃 - 白金锋芒
        "rainbow": (255, 255, 255),
        "gold": (255, 230, 180),
        "beam": (255, 250, 255),
        "trail": (240, 230, 255),
        "particle": (255, 255, 255),
        "glow": (255, 250, 255),
    },
    "prismatic_lance": {
        # 棱镜长枪 - 动态彩虹
        "rainbow": (255, 100, 200),
        "gold": (100, 255, 200),
        "beam": (200, 100, 255),
        "trail": (255, 200, 100),
        "particle": (100, 200, 255),
        "glow": (255, 150, 255),
    },
    "twilight_star": {
        # 暮光星辰 - 紫金星光
        "rainbow": (180, 100, 220),
        "gold": (255, 200, 100),
        "beam": (200, 120, 255),
        "trail": (220, 150, 200),
        "particle": (190, 130, 210),
        "glow": (210, 160, 230),
    },
    "aurora_wave": {
        # 极光波纹 - 青绿紫
        "rainbow": (100, 255, 220),
        "gold": (100, 255, 150),
        "beam": (180, 100, 255),
        "trail": (120, 230, 200),
        "particle": (100, 200, 255),
        "glow": (150, 255, 220),
    },
    "celestial_arrow": {
        # 天界箭矢 - 星辰银蓝
        "rainbow": (220, 230, 255),
        "gold": (100, 150, 255),
        "beam": (180, 200, 255),
        "trail": (200, 210, 255),
        "particle": (230, 240, 255),
        "glow": (200, 220, 255),
    },
    "dawn_ray": {
        # 黎明光线 - 橙粉金
        "rainbow": (255, 180, 100),
        "gold": (255, 150, 180),
        "beam": (255, 200, 150),
        "trail": (255, 170, 130),
        "particle": (255, 190, 160),
        "glow": (255, 220, 180),
    },
    "moonlight_petal": {
        # 月华花瓣 - 冷月银白
        "rainbow": (230, 240, 255),
        "gold": (200, 220, 255),
        "beam": (240, 245, 255),
        "trail": (220, 230, 250),
        "particle": (235, 240, 255),
        "glow": (245, 250, 255),
    },
    "fury_crash": {
        # 狂怒冲击 - 激烈彩虹
        "rainbow": (255, 80, 120),
        "gold": (255, 200, 50),
        "beam": (255, 100, 255),
        "trail": (255, 150, 80),
        "particle": (80, 255, 150),
        "glow": (255, 120, 200),
    },
    "dream_bubble": {
        # 梦幻泡泡 - 淡紫梦幻
        "rainbow": (220, 180, 255),
        "gold": (255, 200, 230),
        "beam": (230, 190, 255),
        "trail": (210, 170, 245),
        "particle": (225, 185, 250),
        "glow": (235, 200, 255),
    },
    "solar_dance": {
        # 日耀之舞 - 太阳金红
        "rainbow": (255, 200, 50),
        "gold": (255, 120, 30),
        "beam": (255, 160, 60),
        "trail": (255, 140, 40),
        "particle": (255, 180, 80),
        "glow": (255, 220, 100),
    },
    "void_rift": {
        # 虚空裂隙 - 暗紫深渊裂痕
        "rainbow": (80, 30, 120),
        "gold": (120, 40, 100),
        "beam": (100, 50, 150),
        "trail": (90, 35, 110),
        "particle": (110, 60, 140),
        "glow": (130, 70, 160),
    },
}

# ==================== 辅助函数 ====================
def _hue_to_rgb(hue):
    """色相转RGB (0-360度)"""
    hue = hue % 360
    c = 1.0
    x = 1.0 - abs((hue / 60) % 2 - 1)
    if hue < 60:
        r, g, b = c, x, 0
    elif hue < 120:
        r, g, b = x, c, 0
    elif hue < 180:
        r, g, b = 0, c, x
    elif hue < 240:
        r, g, b = 0, x, c
    elif hue < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return (int(r * 255), int(g * 255), int(b * 255))

# ==================== 预览渲染适配器（用于customization预览） ====================
def render_staradia_bullet_preview(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Staradia子弹预览效果 - 光之女皇级别特效（预览接口）
    
    Args:
        surface: pygame绘图表面
        effects: 效果列表
        color: 主题颜色
        center_x, center_y: 中心坐标
        size: 子弹大小
        x, y: 左上角坐标
    
    Returns:
        bool: 如果渲染了效果返回True，否则False
    """
    # 检查是否是Staradia相关效果
    staradia_effects = [
        # 子弹主题effects（来自customization.py BULLET_THEMES）
        "rainbow_trail", "prismatic_shimmer", "blade_slash", "prism_shatter",
        "prismatic_split", "spiral_drill", "twilight_gradient", "sunset_trail",
        "aurora_ripple", "polar_light", "constellation_trail", "meteor_shower",
        "dawn_break", "hope_light", "petal_dance", "moon_scatter",
        "fury_explosion", "instant_kill", "dream_float", "starlight_burst",
        "solar_spin", "flame_dance", "void_tear", "space_rend"
    ]
    
    # 检查是否有Staradia效果
    has_staradia_effect = any(effect in effects for effect in staradia_effects)
    if not has_staradia_effect:
        return False
    
    t = pygame.time.get_ticks() / 1000.0
    frame = int(t * 30)
    
    # 女皇配色
    empress_pink = (255, 180, 220)
    moon_gold = (255, 215, 120)
    rainbow_white = (255, 255, 255)
    
    # 渲染子弹效果
    bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
    cx, cy = size, size
    
    # 动态脉冲
    pulse = abs(math.sin(t * 3)) * 0.2 + 1.0
    
    # ===== 检查是否是虚空裂隙 =====
    is_void_rift = "void_tear" in effects or "space_rend" in effects
    
    if is_void_rift:
        # ===== 虚空裂隙 - 暗紫撕裂空间 =====
        rift_size = int(size // 3 * pulse)
        
        # 暗紫核心
        pygame.draw.circle(bullet_surf, (80, 30, 120, 200), (cx, cy), rift_size)
        
        # 裂隙尖刺
        for i in range(6):
            angle = t * 1.5 + i * math.pi / 3
            spike_len = rift_size + 6 + math.sin(t * 4 + i) * 3
            sx = cx + math.cos(angle) * spike_len
            sy = cy + math.sin(angle) * spike_len
            pygame.draw.line(bullet_surf, (120, 40, 100, 180), (cx, cy), (int(sx), int(sy)), 2)
        
        # 虚空光环
        pygame.draw.circle(bullet_surf, (100, 50, 150, 100), (cx, cy), rift_size + 6, 2)
        
        # 中心亮点
        pygame.draw.circle(bullet_surf, (150, 80, 180), (cx, cy), 4)
        pygame.draw.circle(bullet_surf, (200, 120, 220), (cx, cy), 2)
    else:
        # ===== 其他涂装 - 菱形月虹光梭 =====
        
        # 光之女皇翅膀尾迹
        wing_length = size // 2
        for i in range(4):
            wing_angle = math.radians(30 + i * 10)
            wave = math.sin(t * 4 + i * 0.5) * 2
            
            # 左翼
            lx = cx - math.cos(wing_angle) * wing_length - wave
            ly = cy + size // 3 + i * 2
            alpha = 150 - i * 30
            wing_color = _hue_to_rgb((frame * 8 + i * 30) % 360) if i % 2 == 0 else empress_pink
            pygame.draw.circle(bullet_surf, (*wing_color, alpha), (int(lx), int(ly)), 3 - i // 2)
            
            # 右翼
            rx = cx + math.cos(wing_angle) * wing_length + wave
            pygame.draw.circle(bullet_surf, (*wing_color, alpha), (int(rx), int(ly)), 3 - i // 2)
        
        # 彩虹光晕层
        for i in range(3):
            glow_r = int((size // 2.5 - i * 2) * pulse)
            alpha = 80 - i * 20
            layer_color = _hue_to_rgb((frame * 8 + i * 60) % 360)
            pygame.draw.circle(bullet_surf, (*layer_color, alpha), (cx, cy), glow_r)
        
        # 菱形主体
        diamond_h = int(size * 0.7)
        diamond_w = int(size * 0.4)
        diamond_points = [
            (cx, cy - diamond_h // 2),  # 顶
            (cx + diamond_w // 2, cy),  # 右
            (cx, cy + diamond_h // 2),  # 底
            (cx - diamond_w // 2, cy),  # 左
        ]
        
        # 多层菱形
        for i in range(3):
            scale = 1 - i * 0.2
            pts = [(cx + (px - cx) * scale, cy + (py - cy) * scale) for px, py in diamond_points]
            alpha = 220 - i * 50
            if i == 0:
                pygame.draw.polygon(bullet_surf, (*empress_pink, alpha), pts)
            else:
                pygame.draw.polygon(bullet_surf, (*moon_gold, alpha), pts)
        
        # 顶端高亮
        tip_y = cy - diamond_h // 2
        pygame.draw.circle(bullet_surf, moon_gold, (cx, int(tip_y)), 4)
        pygame.draw.circle(bullet_surf, rainbow_white, (cx, int(tip_y)), 2)
        
        # 顶端棱镜星光
        for i in range(4):
            angle = t * 2 + i * math.pi / 2
            sx = cx + math.cos(angle) * 4
            sy = tip_y + math.sin(angle) * 3
            pygame.draw.circle(bullet_surf, rainbow_white, (int(sx), int(sy)), 2)
    
    surface.blit(bullet_surf, (x, y))
    return True

# ==================== 渲染函数 ====================
def render_staradia_bullet(surface, x, y, frame, style="default"):
    """渲染斯塔德子弹 - 光之女皇级别特效"""
    theme = STARADIA_BULLET_THEMES.get(style, STARADIA_BULLET_THEMES["default"])
    rainbow = theme["rainbow"]
    gold = theme["gold"]
    trail = theme.get("trail", rainbow)
    glow_color = theme.get("glow", (255, 255, 255))
    
    # 动态参数
    pulse = math.sin(frame * 0.3) * 0.2 + 1.0
    
    # 特殊涂装处理
    is_prismatic = (style == "prismatic")
    is_rainbow_fury = (style == "rainbow_fury")
    is_void_empress = (style == "void_empress")
    
    # 棱镜幻彩 - 动态彩虹色
    if is_prismatic:
        hue = (frame * 8) % 360
        rainbow = _hue_to_rgb(hue)
        gold = _hue_to_rgb((hue + 120) % 360)
        trail = _hue_to_rgb((hue + 240) % 360)
    
    # 虹怒 - 更激烈的动态
    if is_rainbow_fury:
        pulse = math.sin(frame * 0.6) * 0.3 + 1.1
        hue = (frame * 15) % 360
        rainbow = _hue_to_rgb(hue)
    
    # ===== 虚空女皇 - 裂隙形状 =====
    if is_void_empress:
        rift_size = int(8 * pulse)
        
        # 暗紫核心
        pygame.draw.circle(surface, (80, 30, 120, 200), (x, y), rift_size)
        
        # 裂隙尖刺
        for i in range(6):
            angle = frame * 0.1 + i * math.pi / 3
            spike_len = rift_size + 4 + math.sin(frame * 0.3 + i) * 2
            sx = x + math.cos(angle) * spike_len
            sy = y + math.sin(angle) * spike_len
            pygame.draw.line(surface, (120, 40, 100, 180), (x, y), (int(sx), int(sy)), 2)
        
        # 虚空光环
        pygame.draw.circle(surface, (100, 50, 150, 100), (x, y), rift_size + 4, 2)
        
        # 中心亮点
        pygame.draw.circle(surface, (150, 80, 180), (x, y), 3)
        return
    
    # ===== 其他涂装 - 菱形月虹光梭 =====
    
    # 光之女皇翅膀尾迹
    wing_length = 10
    for i in range(5):
        wing_angle = math.radians(35 + i * 8)
        wave = math.sin(frame * 0.4 + i * 0.5) * 2
        
        # 左翼
        lx = x - math.cos(wing_angle) * wing_length - wave
        ly = y + 6 + i * 2
        alpha = 130 - i * 22
        
        if is_prismatic:
            wing_color = (*_hue_to_rgb((frame * 8 + i * 30) % 360), alpha)
        else:
            wing_color = (*trail, alpha)
        
        pygame.draw.circle(surface, wing_color, (int(lx), int(ly)), 2)
        
        # 右翼
        rx = x + math.cos(wing_angle) * wing_length + wave
        pygame.draw.circle(surface, wing_color, (int(rx), int(ly)), 2)
    
    # 彩虹光晕层
    for i in range(3):
        glow_r = int((9 - i * 2) * pulse)
        alpha = 60 - i * 15
        
        if is_prismatic:
            layer_color = (*_hue_to_rgb((frame * 8 + i * 60) % 360), alpha)
        else:
            layer_color = (*glow_color, alpha)
        
        pygame.draw.circle(surface, layer_color, (x, y), glow_r)
    
    # 菱形主体
    size = int(9 * pulse)
    diamond_h = int(size * 1.5)
    diamond_w = int(size * 0.8)
    diamond_points = [
        (x, y - diamond_h // 2),  # 顶
        (x + diamond_w // 2, y),  # 右
        (x, y + diamond_h // 2),  # 底
        (x - diamond_w // 2, y),  # 左
    ]
    
    for i in range(3):
        scale = 1 - i * 0.2
        pts = [(x + (px - x) * scale, y + (py - y) * scale) for px, py in diamond_points]
        alpha = 220 - i * 50
        
        if is_prismatic:
            core_color = _hue_to_rgb((frame * 8 + i * 40) % 360)
        elif i == 0:
            core_color = rainbow
        else:
            core_color = gold
        
        pygame.draw.polygon(surface, (*core_color, alpha), pts)
    
    # 顶端高亮
    tip_y = y - diamond_h // 2
    pygame.draw.circle(surface, gold, (x, int(tip_y)), 3)
    pygame.draw.circle(surface, (255, 255, 240), (x, int(tip_y)), 2)
    
    # 顶端棱镜星光
    for i in range(4):
        angle = frame * 0.2 + i * math.pi / 2
        sx = x + math.cos(angle) * 4
        sy = tip_y + math.sin(angle) * 2
        
        if is_prismatic:
            star_color = _hue_to_rgb((frame * 10 + i * 90) % 360)
        else:
            star_color = (255, 255, 255)
        
        pygame.draw.circle(surface, star_color, (int(sx), int(sy)), 2)
    
    # 虹怒额外效果 - 能量爆发
    if is_rainbow_fury:
        for i in range(3):
            burst_angle = frame * 0.5 + i * math.pi * 2 / 3
            bx = x + math.cos(burst_angle) * 8
            by = y + math.sin(burst_angle) * 8
            burst_color = _hue_to_rgb((frame * 20 + i * 120) % 360)
            pygame.draw.circle(surface, burst_color, (int(bx), int(by)), 2)


# ==================== 辉耀残痕（光板）====================
class RadiantRemnant(pygame.sprite.Sprite):
    """辉耀残痕 - 留场光板，自动发射月光弹"""
    
    def __init__(self, x, y, owner=None, enhanced=False, style="default"):
        super().__init__()
        self.owner = owner
        self.is_enemy = False
        self.damage = 0  # 光板本身不造成伤害
        self.piercing = 999
        self.style = style  # 涂装样式
        
        # 位置
        self.float_x = float(x)
        self.float_y = float(y)
        
        # 尺寸（皇辉领域+40%）
        self.enhanced = enhanced
        self.base_width = 80
        self.base_height = 20
        size_mult = 1.4 if enhanced else 1.0
        self.width = int(self.base_width * size_mult)
        self.height = int(self.base_height * size_mult)
        
        # 生命周期
        self.lifetime = 180  # 3秒
        self.spawn_timer = 48 if not enhanced else 0  # 0.8s展开延迟
        self.active = False
        
        # 月光弹发射
        self.fire_interval = 24 if not enhanced else 12  # 0.4s或0.2s
        self.fire_timer = 0
        
        # 激活状态
        self.activated = False
        self.activation_dir = 0
        
        # 视觉
        self.frame = 0
        self.alpha = 0
        self.rainbow_offset = random.random() * math.pi * 2
        
        # 创建surface
        self.image = pygame.Surface((self.width + 40, self.height + 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
    def update(self):
        self.frame += 1
        
        # 展开阶段
        if self.spawn_timer > 0:
            self.spawn_timer -= 1
            self.alpha = min(255, int((48 - self.spawn_timer) / 48 * 255))
            if self.spawn_timer == 0:
                self.active = True
            self._render()
            return
        
        # 生命周期
        self.lifetime -= 1
        if self.lifetime <= 0:
            self._explode()
            # 减少玩家残影计数
            if self.owner and hasattr(self.owner, 'remnant_count'):
                self.owner.remnant_count = max(0, self.owner.remnant_count - 1)
            self.kill()
            return
        
        # 淡出
        if self.lifetime < 30:
            self.alpha = int(self.lifetime / 30 * 255)
        else:
            self.alpha = 255
        
        # 自动发射月光弹
        if self.active and not self.activated:
            self.fire_timer += 1
            if self.fire_timer >= self.fire_interval:
                self.fire_timer = 0
                self._fire_moonlight()
        
        self._render()
        self.rect.center = (int(self.float_x), int(self.float_y))
    
    def _fire_moonlight(self):
        """发射追踪月光弹"""
        bullet = MoonlightBullet(self.float_x, self.float_y, self.owner, self.style)
        all_sprites.add(bullet)
    
    def activate(self, direction):
        """激活残痕，发射皇辉束"""
        if self.activated or not self.active:
            return
        self.activated = True
        self.activation_dir = direction
        
        # 发射皇辉束
        beam = RadiantBeam(self.float_x, self.float_y, direction, self.owner, self.enhanced, self.style)
        all_sprites.add(beam)
        
        # 激活后快速消失
        self.lifetime = min(self.lifetime, 20)
    
    def _explode(self):
        """光板爆炸"""
        # 创建爆炸特效
        effect = RemnantExplosion(self.float_x, self.float_y, self.enhanced)
        all_sprites.add(effect)
        
        # 掉落虹尘
        if hasattr(self.owner, 'energy'):
            drop = 50 if self.enhanced else 25
            self.owner.energy = min(getattr(self.owner, 'max_energy', 100), 
                                   self.owner.energy + drop)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.image.get_width() // 2, self.image.get_height() // 2
        
        # 彩虹渐变光板
        pulse = math.sin(self.frame * 0.15 + self.rainbow_offset) * 0.1 + 1.0
        w, h = int(self.width * pulse), int(self.height * pulse)
        
        # 多层光晕
        for i in range(4):
            layer_alpha = max(0, self.alpha - i * 50)
            # 彩虹色相偏移
            hue = (self.frame * 2 + i * 30) % 360
            color = self._hue_to_rgb(hue, layer_alpha)
            expand = i * 4
            pygame.draw.ellipse(self.image, color,
                              (cx - w//2 - expand, cy - h//2 - expand,
                               w + expand*2, h + expand*2))
        
        # 核心金光
        gold = (255, 215, 120, self.alpha)
        pygame.draw.ellipse(self.image, gold,
                          (cx - w//4, cy - h//4, w//2, h//2))
    
    def _hue_to_rgb(self, hue, alpha):
        """色相转RGB（简化版彩虹）"""
        h = hue / 60
        x = int(255 * (1 - abs(h % 2 - 1)))
        if h < 1: return (255, x, 150, alpha)
        elif h < 2: return (x, 255, 150, alpha)
        elif h < 3: return (150, 255, x, alpha)
        elif h < 4: return (150, x, 255, alpha)
        elif h < 5: return (x, 150, 255, alpha)
        else: return (255, 150, x, alpha)


# ==================== 月光弹（追踪）====================
class MoonlightBullet(pygame.sprite.Sprite):
    """月光弹 - 残痕自动发射的追踪弹"""
    
    def __init__(self, x, y, owner=None, style="default"):
        super().__init__()
        self.damage = 8
        self.owner = owner
        self.is_enemy = False
        self.piercing = 1
        self.style = style  # 涂装样式
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed = 8
        self.angle = -math.pi / 2  # 初始向上
        self.turn_rate = 0.08
        
        self.lifetime = 180
        self.frame = 0
        self.target = None
        
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
    def update(self):
        self.frame += 1
        self.lifetime -= 1
        if self.lifetime <= 0 or self.float_y < -50 or self.float_y > HEIGHT + 50:
            self.kill()
            return
        
        # 寻找目标
        self._find_target()
        
        # 追踪转向
        if self.target and self.target.alive():
            tx, ty = self.target.rect.centerx, self.target.rect.centery
            target_angle = math.atan2(ty - self.float_y, tx - self.float_x)
            angle_diff = target_angle - self.angle
            while angle_diff > math.pi: angle_diff -= 2 * math.pi
            while angle_diff < -math.pi: angle_diff += 2 * math.pi
            self.angle += max(-self.turn_rate, min(self.turn_rate, angle_diff))
        
        # 移动
        self.float_x += math.cos(self.angle) * self.speed
        self.float_y += math.sin(self.angle) * self.speed
        
        self._render()
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 命中检测 + 升格
        self._check_hit()
    
    def _find_target(self):
        if self.target and self.target.alive():
            return
        closest = None
        min_dist = 400
        for mob in mobs:
            if not mob.alive():
                continue
            dist = math.hypot(mob.rect.centerx - self.float_x, 
                            mob.rect.centery - self.float_y)
            if dist < min_dist:
                min_dist = dist
                closest = mob
        self.target = closest
    
    def _check_hit(self):
        for mob in mobs:
            if self.rect.colliderect(mob.rect):
                mob.take_damage(self.damage)
                # 升格计数
                if self.owner and hasattr(self.owner, 'radiant_stacks'):
                    self.owner.radiant_stacks = min(5, self.owner.radiant_stacks + 1)
                self._spawn_hit_effect()
                self.kill()
                return
    
    def _spawn_hit_effect(self):
        effect = MoonlightHitEffect(self.float_x, self.float_y)
        all_sprites.add(effect)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 10, 10
        
        # 获取主题配色
        theme = STARADIA_BULLET_THEMES.get(self.style, STARADIA_BULLET_THEMES["default"])
        rainbow_base = theme["rainbow"]
        gold_base = theme["gold"]
        
        # 月光核心
        pulse = math.sin(self.frame * 0.4) * 0.2 + 1.0
        size = int(6 * pulse)
        
        # 棱镜幻彩特殊处理
        if self.style == "prismatic":
            hue = (self.frame * 10) % 360
            rainbow = self._hue_to_rgb(hue)
        elif self.style == "rainbow_fury":
            hue = (self.frame * 15) % 360
            rainbow = self._hue_to_rgb(hue)
        else:
            # 基于主题色的虹光
            hue = (self.frame * 5) % 360
            rainbow = self._blend_with_theme(hue, rainbow_base)
        
        # 外圈虹光
        pygame.draw.circle(self.image, rainbow, (cx, cy), size + 3)
        
        # 内圈主题金光
        pygame.draw.circle(self.image, gold_base, (cx, cy), size)
        pygame.draw.circle(self.image, (255, 255, 220), (cx, cy), size // 2)
    
    def _blend_with_theme(self, hue, theme_color):
        """将彩虹色与主题色混合"""
        rainbow = self._hue_to_rgb(hue)
        return (
            (rainbow[0] + theme_color[0]) // 2,
            (rainbow[1] + theme_color[1]) // 2,
            (rainbow[2] + theme_color[2]) // 2
        )
    
    def _hue_to_rgb(self, hue):
        h = hue / 60
        x = int(200 * (1 - abs(h % 2 - 1))) + 55
        if h < 1: return (255, x, 180)
        elif h < 2: return (x, 255, 180)
        elif h < 3: return (180, 255, x)
        elif h < 4: return (180, x, 255)
        elif h < 5: return (x, 180, 255)
        else: return (255, 180, x)


# ==================== 皇辉束（真伤穿透）====================
class RadiantBeam(pygame.sprite.Sprite):
    """皇辉束 - 真伤穿透光束，可击落弹幕"""
    
    def __init__(self, x, y, direction, owner=None, crit=False, style="default"):
        super().__init__()
        self.damage = 35
        self.owner = owner
        self.is_enemy = False
        self.piercing = 2
        self.true_damage = True  # 真伤标记
        self.destroy_bullets = True  # 击落弹幕
        self.crit = crit  # 暴击
        self.style = style  # 涂装样式
        
        if self.crit:
            self.damage = int(self.damage * 1.5)
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.direction = direction  # 弧度
        self.speed = 18
        
        self.length = 60
        self.width = 8
        self.lifetime = 60
        self.frame = 0
        self.trail_points = []
        
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
    def update(self):
        self.frame += 1
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 移动
        self.float_x += math.cos(self.direction) * self.speed
        self.float_y += math.sin(self.direction) * self.speed
        
        # 拖尾
        self.trail_points.append((self.float_x, self.float_y))
        if len(self.trail_points) > 15:
            self.trail_points.pop(0)
        
        # 边界检测
        if (self.float_x < -50 or self.float_x > WIDTH + 50 or
            self.float_y < -50 or self.float_y > HEIGHT + 50):
            self.kill()
            return
        
        self._check_hit()
        self._render()
        self.rect.center = (int(self.float_x), int(self.float_y))
    
    def _check_hit(self):
        # 击中敌人
        for mob in mobs:
            if self.rect.colliderect(mob.rect) and self.piercing > 0:
                mob.take_damage(self.damage)
                self.piercing -= 1
                self._spawn_hit_effect()
                if self.piercing <= 0:
                    self.kill()
                    return
        
        # 击落弹幕
        if self.destroy_bullets:
            for sprite in all_sprites:
                if hasattr(sprite, 'is_enemy') and sprite.is_enemy:
                    if hasattr(sprite, 'rect') and self.rect.colliderect(sprite.rect):
                        sprite.kill()
    
    def _spawn_hit_effect(self):
        effect = RadiantHitEffect(self.float_x, self.float_y, self.crit)
        all_sprites.add(effect)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 50, 50
        
        # 获取主题配色
        theme = STARADIA_BULLET_THEMES.get(self.style, STARADIA_BULLET_THEMES["default"])
        rainbow = theme["rainbow"]
        gold = theme["gold"]
        beam_color = theme.get("beam", (255, 200, 255))
        
        # 光束主体
        pulse = math.sin(self.frame * 0.5) * 0.15 + 1.0
        w = int(self.width * pulse)
        
        # 绘制光束（旋转）
        end_x = cx + math.cos(self.direction) * self.length
        end_y = cy + math.sin(self.direction) * self.length
        
        # 棱镜幻彩特殊处理
        if self.style == "prismatic":
            hue = (self.frame * 12) % 360
            c1 = _hue_to_rgb(hue)
            c2 = _hue_to_rgb((hue + 60) % 360)
            c3 = _hue_to_rgb((hue + 120) % 360)
            colors = [c1, c2, c3]
        elif self.style == "rainbow_fury":
            hue = (self.frame * 20) % 360
            c1 = _hue_to_rgb(hue)
            c2 = (255, 255, 200)
            c3 = _hue_to_rgb((hue + 180) % 360)
            colors = [c1, c2, c3]
        elif self.crit:
            # 暴击时金色光束
            colors = [gold, (255, 240, 180), (255, 255, 220)]
        else:
            # 主题色光束
            colors = [
                rainbow,
                beam_color,
                (min(255, beam_color[0] + 30), min(255, beam_color[1] + 30), min(255, beam_color[2] + 30))
            ]
        
        for i, color in enumerate(colors):
            pygame.draw.line(self.image, color, (cx, cy), (end_x, end_y), w + 4 - i*2)
        
        # 光束头部星光
        pygame.draw.circle(self.image, (255, 255, 255), (int(end_x), int(end_y)), w // 2 + 2)


# ==================== 月虹光梭（主武器）====================
class MoonRainbowShuttle(pygame.sprite.Sprite):
    """月虹光梭 - 主武器，命中展开辉耀残痕"""
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.piercing = 1
        self.style = style  # 涂装样式
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed = 20  # 高速
        
        self.frame = 0
        self.lifetime = 90  # 1.5屏
        
        self.image = pygame.Surface((24, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
    def update(self):
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0 or self.float_y < -50:
            self.kill()
            return
        
        # 向上飞行
        self.float_y -= self.speed
        
        self._check_hit()
        self._render()
        self.rect.center = (int(self.float_x), int(self.float_y))
    
    def _check_hit(self):
        for mob in mobs:
            if self.rect.colliderect(mob.rect):
                mob.take_damage(self.damage)
                self._spawn_remnant()
                self._spawn_hit_effect()
                self.kill()
                return
    
    def _spawn_remnant(self):
        """命中时展开辉耀残痕"""
        enhanced = False
        if self.owner and hasattr(self.owner, 'radiant_domain_active'):
            enhanced = self.owner.radiant_domain_active
        remnant = RadiantRemnant(self.float_x, self.float_y, self.owner, enhanced, self.style)
        all_sprites.add(remnant)
    
    def _spawn_hit_effect(self):
        effect = ShuttleHitEffect(self.float_x, self.float_y, self.style)
        all_sprites.add(effect)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 12, 20
        
        # 获取主题配色
        theme = STARADIA_BULLET_THEMES.get(self.style, STARADIA_BULLET_THEMES["default"])
        rainbow_base = theme["rainbow"]
        gold = theme["gold"]
        
        # 动态脉冲
        pulse = math.sin(self.frame * 0.4) * 0.15 + 1.0
        
        # 棱镜幻彩特殊处理
        if self.style == "prismatic":
            hue = (self.frame * 12) % 360
        elif self.style == "rainbow_fury":
            hue = (self.frame * 18) % 360
        else:
            hue = (self.frame * 8) % 360
        
        # ===== 虚空女皇 - 裂隙形状 =====
        if self.style == "void_empress":
            # 裂隙子弹 - 暗紫撕裂空间效果
            rift_size = int(8 * pulse)
            # 暗紫核心
            pygame.draw.circle(self.image, (80, 30, 120, 200), (cx, cy), rift_size)
            # 裂隙尖刺
            for i in range(6):
                angle = self.frame * 0.1 + i * math.pi / 3
                spike_len = rift_size + 4 + math.sin(self.frame * 0.3 + i) * 2
                sx = cx + math.cos(angle) * spike_len
                sy = cy + math.sin(angle) * spike_len
                pygame.draw.line(self.image, (120, 40, 100, 180), (cx, cy), (int(sx), int(sy)), 2)
            # 虚空光环
            pygame.draw.circle(self.image, (100, 50, 150, 100), (cx, cy), rift_size + 4, 2)
            # 中心亮点
            pygame.draw.circle(self.image, (150, 80, 180), (cx, cy), 3)
        else:
            # ===== 其他涂装 - 月虹光梭（菱形+光晕） =====
            size = int(10 * pulse)
            
            # 外层彩虹光晕
            for i in range(3):
                glow_r = size + 5 - i * 2
                if self.style == "prismatic" or self.style == "rainbow_fury":
                    h = (hue + i * 40) % 360
                    glow_color = self._hue_to_rgb(h, 60 - i * 15)
                else:
                    glow_color = (*rainbow_base, 60 - i * 15)
                pygame.draw.circle(self.image, glow_color, (cx, cy), glow_r)
            
            # 菱形主体
            diamond_h = int(size * 1.6)
            diamond_w = int(size * 0.8)
            diamond_points = [
                (cx, cy - diamond_h // 2),  # 顶
                (cx + diamond_w // 2, cy),  # 右
                (cx, cy + diamond_h // 2),  # 底
                (cx - diamond_w // 2, cy),  # 左
            ]
            
            if self.style == "prismatic" or self.style == "rainbow_fury":
                core_color = self._hue_to_rgb(hue, 220)[:3]
            else:
                core_color = rainbow_base
            
            # 多层菱形
            for i in range(3):
                scale = 1 - i * 0.2
                pts = [(cx + (px - cx) * scale, cy + (py - cy) * scale) for px, py in diamond_points]
                alpha = 220 - i * 50
                if i == 0:
                    pygame.draw.polygon(self.image, (*core_color, alpha), pts)
                else:
                    blend = (
                        (core_color[0] + gold[0]) // 2,
                        (core_color[1] + gold[1]) // 2,
                        (core_color[2] + gold[2]) // 2,
                    )
                    pygame.draw.polygon(self.image, (*blend, alpha), pts)
            
            # 金色尖端高亮
            tip_y = cy - diamond_h // 2
            pygame.draw.circle(self.image, gold, (cx, int(tip_y)), 3)
            pygame.draw.circle(self.image, (255, 255, 255), (cx, int(tip_y)), 2)
    
    def _blend_theme_hue(self, hue, theme_color, alpha):
        """将色相与主题色混合"""
        h = hue / 60
        x = int(200 * (1 - abs(h % 2 - 1))) + 55
        if h < 1: rainbow = (255, x, 180)
        elif h < 2: rainbow = (x, 255, 180)
        elif h < 3: rainbow = (180, 255, x)
        elif h < 4: rainbow = (180, x, 255)
        elif h < 5: rainbow = (x, 180, 255)
        else: rainbow = (255, 180, x)
        return (
            (rainbow[0] + theme_color[0]) // 2,
            (rainbow[1] + theme_color[1]) // 2,
            (rainbow[2] + theme_color[2]) // 2,
            alpha
        )
    
    def _hue_to_rgb(self, hue, alpha):
        h = hue / 60
        x = int(200 * (1 - abs(h % 2 - 1))) + 55
        if h < 1: return (255, x, 180, alpha)
        elif h < 2: return (x, 255, 180, alpha)
        elif h < 3: return (180, 255, x, alpha)
        elif h < 4: return (180, x, 255, alpha)
        elif h < 5: return (x, 180, 255, alpha)
        else: return (255, 180, x, alpha)


# ==================== 命中特效（史诗级） ====================
class ShuttleHitEffect(pygame.sprite.Sprite):
    """光梭命中特效 - 史诗级棱光爆裂
    
    特效包含：
    - 菱形碎片爆散
    - 彩虹冲击波
    - 光尘飘散
    - 棱光残影
    """
    def __init__(self, x, y, style="default"):
        super().__init__()
        self.float_x, self.float_y = x, y
        self.frame = 0
        self.lifetime = 35
        self.style = style
        
        # 碎片系统
        self.shards = []
        for i in range(6):
            angle = i * math.pi / 3 + random.uniform(-0.2, 0.2)
            speed = random.uniform(4, 8)
            self.shards.append({
                'angle': angle,
                'speed': speed,
                'dist': 0,
                'size': random.uniform(4, 8),
                'hue': i * 60,
                'rot': random.uniform(0, math.pi * 2),
                'rot_speed': random.uniform(-0.3, 0.3)
            })
        
        # 光尘
        self.particles = []
        for _ in range(8):
            self.particles.append({
                'x': 0, 'y': 0,
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-3, 1),
                'life': random.randint(20, 35),
                'hue': random.randint(0, 360),
                'size': random.uniform(2, 5)
            })
        
        self.image = pygame.Surface((160, 160), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        
        # 更新碎片
        for shard in self.shards:
            shard['dist'] += shard['speed'] * (1 - self.frame / self.lifetime)
            shard['rot'] += shard['rot_speed']
        
        # 更新光尘
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1  # 重力
            p['life'] -= 1
        
        self._render()
        
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 80, 80
        progress = self.frame / self.lifetime
        alpha = int(255 * (1 - progress))
        
        # ===== 1. 彩虹冲击波 =====
        for wave in range(4):
            wave_progress = max(0, progress - wave * 0.08)
            if wave_progress > 0:
                wave_r = int(wave_progress * 70)
                wave_alpha = int(180 * (1 - wave_progress) * (1 - wave * 0.2))
                if wave_r > 0 and wave_alpha > 0:
                    hue = (self.frame * 20 + wave * 60) % 360
                    color = self._hue_to_rgb(hue, wave_alpha)
                    pygame.draw.circle(self.image, color, (cx, cy), wave_r, 3 - wave // 2)
        
        # ===== 2. 菱形碎片爆散 =====
        for shard in self.shards:
            sx = cx + math.cos(shard['angle']) * shard['dist']
            sy = cy + math.sin(shard['angle']) * shard['dist']
            
            shard_alpha = int(alpha * (1 - shard['dist'] / 80))
            if shard_alpha > 0 and 0 <= sx < 160 and 0 <= sy < 160:
                hue = (shard['hue'] + self.frame * 15) % 360
                color = self._hue_to_rgb(hue, shard_alpha)
                
                # 旋转菱形
                size = shard['size'] * (1 - progress * 0.5)
                rot = shard['rot']
                pts = []
                for i in range(4):
                    a = rot + i * math.pi / 2
                    length = size if i % 2 == 0 else size * 0.6
                    pts.append((sx + math.cos(a) * length, sy + math.sin(a) * length))
                if len(pts) >= 3:
                    pygame.draw.polygon(self.image, color, pts)
        
        # ===== 3. 光尘飘散 =====
        for p in self.particles:
            if p['life'] > 0:
                px = cx + p['x']
                py = cy + p['y']
                if 0 <= px < 160 and 0 <= py < 160:
                    p_alpha = int(200 * p['life'] / 35)
                    p_size = int(p['size'] * p['life'] / 35)
                    if p_size > 0:
                        hue = (p['hue'] + self.frame * 10) % 360
                        pygame.draw.circle(self.image, self._hue_to_rgb(hue, p_alpha),
                                         (int(px), int(py)), p_size)
        
        # ===== 4. 中心残影 =====
        core_r = int(20 * (1 - progress))
        if core_r > 0:
            for i in range(3):
                r = core_r - i * 5
                if r > 0:
                    hue = (self.frame * 25 + i * 40) % 360
                    pygame.draw.circle(self.image, self._hue_to_rgb(hue, alpha - i * 40), (cx, cy), r)
            # 白芯
            pygame.draw.circle(self.image, (255, 255, 255, alpha), (cx, cy), max(1, core_r // 3))
        
        # ===== 5. 放射光芒 =====
        if progress < 0.5:
            ray_alpha = int(150 * (1 - progress * 2))
            for i in range(8):
                angle = i * math.pi / 4 + self.frame * 0.08
                ray_len = 50 * (1 - progress * 2)
                ex = cx + math.cos(angle) * ray_len
                ey = cy + math.sin(angle) * ray_len
                hue = (i * 45 + self.frame * 20) % 360
                pygame.draw.line(self.image, self._hue_to_rgb(hue, ray_alpha // 2),
                               (cx, cy), (int(ex), int(ey)), 4)
                pygame.draw.line(self.image, self._hue_to_rgb(hue, ray_alpha),
                               (cx, cy), (int(ex), int(ey)), 2)
    
    def _hue_to_rgb(self, hue, alpha):
        h = hue / 60
        x = int(200 * (1 - abs(h % 2 - 1))) + 55
        if h < 1: return (255, x, 180, alpha)
        elif h < 2: return (x, 255, 180, alpha)
        elif h < 3: return (180, 255, x, alpha)
        elif h < 4: return (180, x, 255, alpha)
        elif h < 5: return (x, 180, 255, alpha)
        else: return (255, 180, x, alpha)


class MoonlightHitEffect(pygame.sprite.Sprite):
    """月光弹命中特效 - 史诗级月华绽放
    
    特效包含：
    - 月牙波纹扩散
    - 星尘粒子升腾
    - 柔光光晕
    - 新月残影
    """
    def __init__(self, x, y):
        super().__init__()
        self.float_x, self.float_y = x, y
        self.frame = 0
        self.lifetime = 30
        
        # 星尘粒子
        self.stardust = []
        for _ in range(6):
            self.stardust.append({
                'x': random.uniform(-10, 10),
                'y': random.uniform(-5, 5),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-4, -1),
                'size': random.uniform(2, 4),
                'twinkle': random.uniform(0, math.pi * 2)
            })
        
        # 月牙数据
        self.crescents = []
        for i in range(3):
            self.crescents.append({
                'radius': 0,
                'delay': i * 5,
                'rot': random.uniform(0, math.pi * 2)
            })
        
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        
        # 更新月牙
        for c in self.crescents:
            if self.frame > c['delay']:
                c['radius'] += 3
                c['rot'] += 0.05
        
        # 更新星尘
        for s in self.stardust:
            s['x'] += s['vx']
            s['y'] += s['vy']
            s['vy'] += 0.08
            s['twinkle'] += 0.3
        
        self._render()
        
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 50, 50
        progress = self.frame / self.lifetime
        alpha = int(255 * (1 - progress))
        
        # ===== 1. 柔光背景晕 =====
        glow_r = int(35 * (1 - progress * 0.3))
        for i in range(4):
            r = glow_r - i * 6
            if r > 0:
                glow_alpha = 50 - i * 10
                pygame.draw.circle(self.image, (255, 245, 220, glow_alpha), (cx, cy), r)
        
        # ===== 2. 月牙波纹 =====
        for c in self.crescents:
            if c['radius'] > 0:
                c_alpha = int(180 * (1 - c['radius'] / 80))
                if c_alpha > 0:
                    # 绘制月牙形状
                    arc_rect = (cx - c['radius'], cy - c['radius'],
                               c['radius'] * 2, c['radius'] * 2)
                    pygame.draw.arc(self.image, (255, 240, 200, c_alpha),
                                  arc_rect, c['rot'], c['rot'] + math.pi, 3)
                    pygame.draw.arc(self.image, (255, 255, 240, c_alpha // 2),
                                  arc_rect, c['rot'] + math.pi, c['rot'] + math.pi * 2, 2)
        
        # ===== 3. 星尘升腾 =====
        for s in self.stardust:
            sx = cx + s['x']
            sy = cy + s['y']
            if 0 <= sx < 100 and 0 <= sy < 100:
                # 闪烁效果
                twinkle = 0.5 + 0.5 * math.sin(s['twinkle'])
                s_alpha = int(200 * twinkle * (1 - progress))
                s_size = int(s['size'] * twinkle)
                if s_size > 0 and s_alpha > 0:
                    pygame.draw.circle(self.image, (255, 250, 220, s_alpha),
                                     (int(sx), int(sy)), s_size)
                    if s_size > 1:
                        pygame.draw.circle(self.image, (255, 255, 255, s_alpha),
                                         (int(sx), int(sy)), max(1, s_size // 2))
        
        # ===== 4. 中心月华 =====
        core_pulse = 1 + 0.2 * math.sin(self.frame * 0.5)
        core_r = int(15 * core_pulse * (1 - progress * 0.7))
        if core_r > 0:
            # 多层光核
            pygame.draw.circle(self.image, (255, 240, 200, alpha), (cx, cy), core_r)
            pygame.draw.circle(self.image, (255, 250, 230, alpha), (cx, cy), int(core_r * 0.7))
            pygame.draw.circle(self.image, (255, 255, 255, alpha), (cx, cy), int(core_r * 0.4))
        
        # ===== 5. 柔光十字 =====
        if progress < 0.6:
            cross_alpha = int(120 * (1 - progress / 0.6))
            cross_len = int(30 * (1 - progress))
            for angle in [0, math.pi / 2]:
                ex = cx + math.cos(angle) * cross_len
                ey = cy + math.sin(angle) * cross_len
                ex2 = cx - math.cos(angle) * cross_len
                ey2 = cy - math.sin(angle) * cross_len
                pygame.draw.line(self.image, (255, 245, 200, cross_alpha // 2),
                               (int(ex), int(ey)), (int(ex2), int(ey2)), 5)
                pygame.draw.line(self.image, (255, 255, 240, cross_alpha),
                               (int(ex), int(ey)), (int(ex2), int(ey2)), 2)


class RadiantHitEffect(pygame.sprite.Sprite):
    """皇辉束命中特效 - 史诗级皇辉爆发
    
    特效包含：
    - 彩虹六芒星爆裂
    - 皇冠光印
    - 金翼展开
    - 虹光粒子风暴
    暴击时：全面强化+女皇印记
    """
    def __init__(self, x, y, crit=False):
        super().__init__()
        self.float_x, self.float_y = x, y
        self.frame = 0
        self.lifetime = 40 if crit else 30
        self.crit = crit
        
        # 粒子风暴
        self.particles = []
        particle_count = 15 if crit else 10
        for _ in range(particle_count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(3, 8) * (1.5 if crit else 1)
            self.particles.append({
                'angle': angle,
                'speed': speed,
                'dist': 0,
                'hue': random.randint(0, 360),
                'size': random.uniform(3, 6)
            })
        
        # 六芒星数据
        self.star_rotation = 0
        
        # 翼展数据
        self.wing_open = 0
        
        size = 160 if crit else 120
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.size = size
        
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        
        # 更新粒子
        for p in self.particles:
            p['dist'] += p['speed']
            p['speed'] *= 0.96
        
        # 更新六芒星
        self.star_rotation += 0.15
        
        # 更新翼展
        if self.crit:
            self.wing_open = min(1, self.wing_open + 0.08)
        
        self._render()
        
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        progress = self.frame / self.lifetime
        alpha = int(255 * (1 - progress))
        
        # ===== 暴击专属效果 =====
        if self.crit:
            # 背景金光闪烁
            if self.frame < 10:
                flash_alpha = int(150 * (1 - self.frame / 10))
                flash_r = 70
                pygame.draw.circle(self.image, (255, 230, 150, flash_alpha), (cx, cy), flash_r)
            
            # 金翼展开
            wing_span = int(60 * self.wing_open)
            wing_alpha = int(180 * (1 - progress))
            for side in [-1, 1]:
                for feather in range(5):
                    f_angle = side * (0.3 + feather * 0.15) - math.pi / 2
                    f_length = wing_span * (1 - feather * 0.12)
                    fx = cx + math.cos(f_angle) * f_length
                    fy = cy + math.sin(f_angle) * f_length
                    pygame.draw.line(self.image, (255, 215, 100, wing_alpha // 2),
                                   (cx, cy), (int(fx), int(fy)), 6)
                    pygame.draw.line(self.image, (255, 240, 180, wing_alpha),
                                   (cx, cy), (int(fx), int(fy)), 3)
            
            # 女皇印记（皇冠）
            crown_y = cy - 25
            crown_r = 15 * (1 - progress * 0.5)
            crown_pts = []
            for i in range(5):
                angle = -math.pi / 2 + (i - 2) * 0.4
                height = crown_r if i % 2 == 0 else crown_r * 0.5
                crown_pts.append((cx + math.cos(angle) * crown_r * 0.8, crown_y - height))
            if len(crown_pts) >= 3:
                pygame.draw.polygon(self.image, (255, 215, 100, alpha), crown_pts)
                pygame.draw.polygon(self.image, (255, 255, 200, alpha // 2), crown_pts, 2)
        
        # ===== 1. 彩虹冲击波 =====
        for wave in range(5):
            wave_delay = wave * 0.06
            wave_progress = max(0, progress - wave_delay)
            if wave_progress > 0 and wave_progress < 1:
                wave_r = int(wave_progress * (70 if self.crit else 50))
                wave_alpha = int(200 * (1 - wave_progress) * (1 - wave * 0.15))
                if wave_r > 0 and wave_alpha > 0:
                    hue = (self.frame * 25 + wave * 50) % 360
                    color = self._hue_to_rgb(hue, wave_alpha)
                    pygame.draw.circle(self.image, color, (cx, cy), wave_r, 4 - wave // 2)
        
        # ===== 2. 六芒星爆裂 =====
        if progress < 0.7:
            star_r = int(40 * (1 - progress / 0.7))
            star_alpha = int(200 * (1 - progress / 0.7))
            for layer in range(2):
                rot = self.star_rotation * (1 if layer == 0 else -0.5)
                pts = []
                for i in range(6):
                    angle = rot + i * math.pi / 3
                    radius = star_r if i % 2 == 0 else star_r * 0.4
                    px = cx + math.cos(angle) * radius
                    py = cy + math.sin(angle) * radius
                    pts.append((px, py))
                
                if len(pts) >= 3:
                    hue = (self.frame * 20 + layer * 90) % 360
                    color = self._hue_to_rgb(hue, star_alpha - layer * 50)
                    pygame.draw.polygon(self.image, color, pts, 2)
        
        # ===== 3. 粒子风暴 =====
        for p in self.particles:
            px = cx + math.cos(p['angle']) * p['dist']
            py = cy + math.sin(p['angle']) * p['dist']
            
            max_dist = 80 if self.crit else 60
            if 0 <= px < self.size and 0 <= py < self.size and p['dist'] < max_dist:
                p_alpha = int(220 * (1 - p['dist'] / max_dist))
                p_size = int(p['size'] * (1 - p['dist'] / max_dist))
                if p_size > 0 and p_alpha > 0:
                    hue = (p['hue'] + self.frame * 12) % 360
                    pygame.draw.circle(self.image, self._hue_to_rgb(hue, p_alpha),
                                     (int(px), int(py)), p_size)
        
        # ===== 4. 中心光核 =====
        core_pulse = 1 + 0.15 * math.sin(self.frame * 0.4)
        core_r = int((25 if self.crit else 18) * core_pulse * (1 - progress * 0.6))
        if core_r > 0:
            for i in range(4):
                r = core_r - i * 4
                if r > 0:
                    hue = (self.frame * 30 + i * 50) % 360
                    pygame.draw.circle(self.image, self._hue_to_rgb(hue, alpha - i * 30), (cx, cy), r)
            # 白芯
            pygame.draw.circle(self.image, (255, 255, 255, alpha), (cx, cy), max(1, core_r // 3))
        
        # ===== 5. 放射光芒 =====
        ray_count = 12 if self.crit else 8
        ray_len = (60 if self.crit else 40) * (1 - progress * 0.8)
        for i in range(ray_count):
            angle = i * (math.pi * 2 / ray_count) + self.frame * 0.06
            ex = cx + math.cos(angle) * ray_len
            ey = cy + math.sin(angle) * ray_len
            
            hue = (i * (360 // ray_count) + self.frame * 15) % 360
            ray_alpha = int(alpha * 0.6)
            pygame.draw.line(self.image, self._hue_to_rgb(hue, ray_alpha // 3),
                           (cx, cy), (int(ex), int(ey)), 5)
            pygame.draw.line(self.image, self._hue_to_rgb(hue, ray_alpha),
                           (cx, cy), (int(ex), int(ey)), 2)
    
    def _hue_to_rgb(self, hue, alpha):
        h = hue / 60
        x = int(200 * (1 - abs(h % 2 - 1))) + 55
        if h < 1: return (255, x, 180, alpha)
        elif h < 2: return (x, 255, 180, alpha)
        elif h < 3: return (180, 255, x, alpha)
        elif h < 4: return (180, x, 255, alpha)
        elif h < 5: return (x, 180, 255, alpha)
        else: return (255, 180, x, alpha)


class RemnantExplosion(pygame.sprite.Sprite):
    """残痕爆炸特效 - 史诗级虹痕湮灭
    
    特效包含：
    - 多层彩虹冲击波
    - 旋转棱光碎片
    - 中心虹核脉冲
    - 光尘飘散
    增强版：规模更大、持续更长
    """
    def __init__(self, x, y, enhanced=False):
        super().__init__()
        self.float_x, self.float_y = x, y
        self.frame = 0
        self.lifetime = 45 if enhanced else 35
        self.enhanced = enhanced
        
        # 碎片系统
        self.shards = []
        shard_count = 10 if enhanced else 6
        for i in range(shard_count):
            angle = i * (math.pi * 2 / shard_count) + random.uniform(-0.15, 0.15)
            speed = random.uniform(5, 10) * (1.3 if enhanced else 1)
            self.shards.append({
                'angle': angle,
                'speed': speed,
                'dist': 0,
                'size': random.uniform(5, 10),
                'hue': i * (360 // max(1, shard_count)),
                'rot': random.uniform(0, math.pi * 2),
                'rot_speed': random.uniform(-0.25, 0.25)
            })
        
        # 光尘
        self.particles = []
        particle_count = 15 if enhanced else 8
        for _ in range(particle_count):
            self.particles.append({
                'x': random.uniform(-15, 15),
                'y': random.uniform(-15, 15),
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-4, 2),
                'life': random.randint(25, 45),
                'hue': random.randint(0, 360),
                'size': random.uniform(2, 5)
            })
        
        size = 180 if enhanced else 140
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.size = size
        
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        
        # 更新碎片
        for shard in self.shards:
            shard['dist'] += shard['speed'] * (1 - self.frame / self.lifetime)
            shard['rot'] += shard['rot_speed']
        
        # 更新光尘
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.08
            p['life'] -= 1
        
        self._render()
        
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        progress = self.frame / self.lifetime
        alpha = int(255 * (1 - progress))
        
        # ===== 1. 初始白闪（增强版） =====
        if self.enhanced and self.frame < 8:
            flash_alpha = int(180 * (1 - self.frame / 8))
            pygame.draw.circle(self.image, (255, 255, 255, flash_alpha), (cx, cy), 60)
        
        # ===== 2. 多层彩虹冲击波 =====
        wave_count = 6 if self.enhanced else 4
        for wave in range(wave_count):
            wave_delay = wave * 0.05
            wave_progress = max(0, progress - wave_delay)
            if wave_progress > 0 and wave_progress < 1:
                wave_r = int(wave_progress * (80 if self.enhanced else 60))
                wave_alpha = int(200 * (1 - wave_progress) * (1 - wave * 0.12))
                if wave_r > 0 and wave_alpha > 0:
                    hue = (self.frame * 20 + wave * 45) % 360
                    color = self._hue_to_rgb(hue, wave_alpha)
                    pygame.draw.circle(self.image, color, (cx, cy), wave_r, 4 - wave // 2)
        
        # ===== 3. 旋转棱光碎片 =====
        for shard in self.shards:
            sx = cx + math.cos(shard['angle']) * shard['dist']
            sy = cy + math.sin(shard['angle']) * shard['dist']
            
            max_dist = 90 if self.enhanced else 70
            if 0 <= sx < self.size and 0 <= sy < self.size and shard['dist'] < max_dist:
                shard_alpha = int(alpha * (1 - shard['dist'] / max_dist))
                if shard_alpha > 0:
                    hue = (shard['hue'] + self.frame * 12) % 360
                    color = self._hue_to_rgb(hue, shard_alpha)
                    
                    # 旋转菱形碎片
                    size = shard['size'] * (1 - progress * 0.4)
                    rot = shard['rot']
                    pts = []
                    for i in range(4):
                        a = rot + i * math.pi / 2
                        length = size if i % 2 == 0 else size * 0.5
                        pts.append((sx + math.cos(a) * length, sy + math.sin(a) * length))
                    if len(pts) >= 3:
                        pygame.draw.polygon(self.image, color, pts)
                        # 光边
                        pygame.draw.polygon(self.image, (255, 255, 255, shard_alpha // 2), pts, 1)
        
        # ===== 4. 光尘飘散 =====
        for p in self.particles:
            if p['life'] > 0:
                px = cx + p['x']
                py = cy + p['y']
                if 0 <= px < self.size and 0 <= py < self.size:
                    p_alpha = int(180 * p['life'] / 45)
                    p_size = int(p['size'] * p['life'] / 45)
                    if p_size > 0 and p_alpha > 0:
                        hue = (p['hue'] + self.frame * 8) % 360
                        pygame.draw.circle(self.image, self._hue_to_rgb(hue, p_alpha),
                                         (int(px), int(py)), p_size)
        
        # ===== 5. 中心虹核 =====
        core_pulse = 1 + 0.2 * math.sin(self.frame * 0.35)
        core_r = int((30 if self.enhanced else 22) * core_pulse * (1 - progress * 0.5))
        if core_r > 0:
            for i in range(5):
                r = core_r - i * 4
                if r > 0:
                    hue = (self.frame * 25 + i * 40) % 360
                    c_alpha = alpha - i * 35
                    if c_alpha > 0:
                        pygame.draw.circle(self.image, self._hue_to_rgb(hue, c_alpha), (cx, cy), r)
            # 白芯
            pygame.draw.circle(self.image, (255, 255, 255, alpha), (cx, cy), max(1, core_r // 3))
        
        # ===== 6. 放射光芒 =====
        ray_count = 16 if self.enhanced else 10
        ray_len = (70 if self.enhanced else 50) * (1 - progress * 0.7)
        for i in range(ray_count):
            angle = i * (math.pi * 2 / ray_count) + self.frame * 0.05
            ex = cx + math.cos(angle) * ray_len
            ey = cy + math.sin(angle) * ray_len
            
            hue = (i * (360 // ray_count) + self.frame * 18) % 360
            ray_alpha = int(alpha * 0.5)
            pygame.draw.line(self.image, self._hue_to_rgb(hue, ray_alpha // 3),
                           (cx, cy), (int(ex), int(ey)), 6)
            pygame.draw.line(self.image, self._hue_to_rgb(hue, ray_alpha),
                           (cx, cy), (int(ex), int(ey)), 2)
        
        # ===== 7. 六芒星印记（增强版专属） =====
        if self.enhanced and progress < 0.6:
            star_alpha = int(150 * (1 - progress / 0.6))
            star_r = int(45 * (1 - progress * 0.5))
            for layer in range(2):
                rot = self.frame * 0.08 * (1 if layer == 0 else -0.6)
                pts = []
                for i in range(6):
                    angle = rot + i * math.pi / 3 + layer * math.pi / 6
                    px = cx + math.cos(angle) * star_r * (1 - layer * 0.25)
                    py = cy + math.sin(angle) * star_r * (1 - layer * 0.25)
                    pts.append((px, py))
                # 连线
                for i in range(6):
                    j = (i + 2) % 6
                    hue = (self.frame * 15 + i * 60) % 360
                    pygame.draw.line(self.image, self._hue_to_rgb(hue, star_alpha - layer * 40),
                                   pts[i], pts[j], 2)
    
    def _hue_to_rgb(self, hue, alpha):
        h = hue / 60
        x = int(200 * (1 - abs(h % 2 - 1))) + 55
        if h < 1: return (255, x, 180, alpha)
        elif h < 2: return (x, 255, 180, alpha)
        elif h < 3: return (180, 255, x, alpha)
        elif h < 4: return (180, x, 255, alpha)
        elif h < 5: return (x, 180, 255, alpha)
        else: return (255, 180, x, alpha)


# ==================== F技能：皇辉暴雨（三阶段史诗大招） ====================
class RadiantStorm(pygame.sprite.Sprite):
    """皇辉暴雨 - 三阶段史诗大招
    
    第一阶段 (2s): 虹幕展开 - 全屏彩虹幕布展开+光板阵列蓄力
    第二阶段 (3s): 皇辉光雨 - 12道皇辉束从天而降+追踪光梭风暴
    第三阶段 (5s): 女皇降临 - 巨型女皇剪影+六翼齐展+终焉爆发
    """
    
    def __init__(self, x, y, owner=None, style="default"):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 2.5 if owner else 50
        self.style = style  # 涂装样式
        
        # 阶段系统
        self.phase = 0
        self.frame = 0
        self.phase_duration = [120, 180, 300]  # 2秒、3秒、5秒
        
        # 光板阵列
        self.light_plates = []
        
        # 皇辉束数据
        self.beams = []
        self.beam_spawn_timer = 0
        
        # 女皇数据
        self.empress_y = -200
        self.wing_open = 0
        self.crown_glow = 0
        
        # 粒子系统
        self.particles = []
        
        # 屏幕效果
        self.screen_flash = 0
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _add_particle(self, x, y, vx, vy, color, life, size=3):
        self.particles.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color, 'life': life, 'max_life': life, 'size': size
        })
    
    def _update_particles(self):
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            alpha = int(255 * p['life'] / p['max_life'])
            size = int(p['size'] * p['life'] / p['max_life'])
            if size > 0:
                pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                                 (int(p['x']), int(p['y'])), size)
    
    def _hue_to_rgb(self, hue, alpha=255):
        h = hue / 60
        x = int(200 * (1 - abs(h % 2 - 1))) + 55
        if h < 1: return (255, x, 180, alpha)
        elif h < 2: return (x, 255, 180, alpha)
        elif h < 3: return (180, 255, x, alpha)
        elif h < 4: return (180, x, 255, alpha)
        elif h < 5: return (x, 180, 255, alpha)
        else: return (255, 180, x, alpha)
    
    def _phase1_rainbow_curtain(self):
        """第一阶段：虹幕展开"""
        self.image.fill((0, 0, 0, 0))
        progress = self.frame / self.phase_duration[0]
        
        # 背景渐变暗化
        dark_alpha = int(60 * math.sin(progress * math.pi))
        pygame.draw.rect(self.image, (255, 200, 230, dark_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 虹幕从两侧展开
        curtain_width = int(progress * WIDTH / 2)
        rainbow_colors = [
            (255, 100, 150), (255, 180, 100), (255, 255, 120),
            (120, 255, 150), (100, 200, 255), (150, 100, 255), (255, 100, 200)
        ]
        
        # 左侧虹幕
        for i, col in enumerate(rainbow_colors):
            y = i * (HEIGHT // len(rainbow_colors))
            h = HEIGHT // len(rainbow_colors) + 5
            alpha = int(120 * progress)
            pygame.draw.rect(self.image, (*col, alpha), (0, y, curtain_width, h))
        
        # 右侧虹幕
        for i, col in enumerate(rainbow_colors):
            y = i * (HEIGHT // len(rainbow_colors))
            h = HEIGHT // len(rainbow_colors) + 5
            alpha = int(120 * progress)
            pygame.draw.rect(self.image, (*col, alpha), (WIDTH - curtain_width, y, curtain_width, h))
        
        # 生成光板阵列
        if self.frame == 1:
            for i in range(8):
                angle = i * 45
                self.light_plates.append({
                    'angle': angle,
                    'dist': 80,
                    'size': 0,
                    'max_size': random.randint(40, 60),
                    'glow': 0,
                    'hue': i * 45
                })
        
        # 绘制蓄力光板
        ox, oy = self.owner.rect.centerx if self.owner else WIDTH//2, self.owner.rect.centery if self.owner else HEIGHT//2
        for plate in self.light_plates:
            if plate['size'] < plate['max_size']:
                plate['size'] += 1.5
            plate['glow'] = min(1, plate['glow'] + 0.03)
            
            angle_rad = math.radians(plate['angle'] + self.frame * 0.5)
            px = ox + math.cos(angle_rad) * plate['dist']
            py = oy + math.sin(angle_rad) * plate['dist']
            
            # 光板本体
            size = plate['size']
            hue = (plate['hue'] + self.frame * 3) % 360
            color = self._hue_to_rgb(hue, int(180 * plate['glow']))
            
            # 菱形光板
            pts = [
                (px, py - size * 0.8),
                (px + size * 0.5, py),
                (px, py + size * 0.8),
                (px - size * 0.5, py)
            ]
            pygame.draw.polygon(self.image, color, pts)
            pygame.draw.polygon(self.image, (255, 255, 255, int(150 * plate['glow'])), pts, 2)
            
            # 连接线到中心
            pygame.draw.line(self.image, (*color[:3], 60), (ox, oy), (int(px), int(py)), 2)
        
        # 中心能量聚集
        core_pulse = abs(math.sin(self.frame * 0.15))
        core_r = int(20 + core_pulse * 15 + progress * 30)
        for i in range(4):
            r = core_r - i * 6
            if r > 0:
                a = 150 - i * 35
                pygame.draw.circle(self.image, (255, 220, 255, a), (ox, oy), r)
        
        # 蓄力粒子
        if self.frame % 3 == 0:
            for _ in range(5):
                angle = random.uniform(0, math.pi * 2)
                dist = random.uniform(150, 250)
                px = ox + math.cos(angle) * dist
                py = oy + math.sin(angle) * dist
                self._add_particle(px, py, -math.cos(angle) * 3, -math.sin(angle) * 3,
                                 self._hue_to_rgb(random.randint(0, 360)), 30, 4)
        
        self._update_particles()
    
    def _phase2_radiant_rain(self):
        """第二阶段：皇辉光雨"""
        self.image.fill((0, 0, 0, 0))
        progress = self.frame / self.phase_duration[1]
        
        # 天空变为彩虹渐变
        for y in range(0, HEIGHT, 20):
            hue = (y * 0.5 + self.frame * 2) % 360
            color = self._hue_to_rgb(hue, 40)
            pygame.draw.rect(self.image, color, (0, y, WIDTH, 22))
        
        # 生成皇辉束
        self.beam_spawn_timer += 1
        if self.beam_spawn_timer >= 12 and len(self.beams) < 15:
            self.beam_spawn_timer = 0
            x = random.randint(50, WIDTH - 50)
            self.beams.append({
                'x': x, 'y': -50,
                'speed': random.uniform(12, 18),
                'width': random.randint(30, 50),
                'hue': random.randint(0, 360),
                'life': 80
            })
        
        # 更新并绘制皇辉束
        for beam in self.beams[:]:
            beam['y'] += beam['speed']
            beam['life'] -= 1
            
            if beam['life'] <= 0 or beam['y'] > HEIGHT + 100:
                self.beams.remove(beam)
                continue
            
            # 多层光束
            for layer in range(5):
                w = beam['width'] - layer * 8
                if w > 0:
                    hue = (beam['hue'] + layer * 20 + self.frame * 5) % 360
                    color = self._hue_to_rgb(hue, 180 - layer * 30)
                    pygame.draw.rect(self.image, color,
                                   (beam['x'] - w//2, 0, w, int(beam['y'])))
            
            # 光束头部光球
            head_r = beam['width'] // 2
            pygame.draw.circle(self.image, (255, 255, 255, 220),
                             (int(beam['x']), int(beam['y'])), head_r)
            pygame.draw.circle(self.image, self._hue_to_rgb(beam['hue']),
                             (int(beam['x']), int(beam['y'])), head_r - 5)
            
            # 伤害检测
            for enemy in mobs:
                if abs(enemy.rect.centerx - beam['x']) < beam['width'] and enemy.rect.centery < beam['y']:
                    if self.frame % 6 == 0:
                        enemy.hp -= self.damage * 0.3
                        self._add_particle(enemy.rect.centerx, enemy.rect.centery,
                                         random.uniform(-4, 4), random.uniform(-4, 4),
                                         self._hue_to_rgb(beam['hue']), 20, 5)
        
        # 追踪光梭风暴
        if self.frame % 8 == 0:
            ox = self.owner.rect.centerx if self.owner else WIDTH // 2
            oy = self.owner.rect.centery if self.owner else HEIGHT // 2
            for i in range(3):
                angle = random.uniform(0, math.pi * 2)
                shuttle = MoonRainbowShuttle(ox + math.cos(angle) * 30,
                                            oy + math.sin(angle) * 30,
                                            self.owner)
                all_sprites.add(shuttle)
        
        # 玩家周围的虹光护环
        if self.owner:
            ox, oy = self.owner.rect.centerx, self.owner.rect.centery
            for i in range(3):
                r = 60 + i * 20 + int(math.sin(self.frame * 0.1 + i) * 10)
                hue = (self.frame * 5 + i * 40) % 360
                pygame.draw.circle(self.image, self._hue_to_rgb(hue, 80), (ox, oy), r, 3)
        
        self._update_particles()
    
    def _phase3_empress_descent(self):
        """第三阶段：女皇降临"""
        self.image.fill((0, 0, 0, 0))
        progress = self.frame / self.phase_duration[2]
        
        # 全屏彩虹渐变背景
        for y in range(0, HEIGHT, 10):
            hue = (y * 0.8 + self.frame * 3) % 360
            alpha = int(80 * (0.5 + 0.5 * math.sin(progress * math.pi)))
            color = self._hue_to_rgb(hue, alpha)
            pygame.draw.rect(self.image, color, (0, y, WIDTH, 12))
        
        # 女皇降临
        if self.empress_y < HEIGHT // 3:
            self.empress_y += 4
        if self.wing_open < 1:
            self.wing_open = min(1, self.wing_open + 0.015)
        if self.crown_glow < 1:
            self.crown_glow = min(1, self.crown_glow + 0.02)
        
        empress_x = WIDTH // 2
        empress_y = int(self.empress_y)
        
        # 女皇背后的神圣光环
        for i in range(8):
            halo_r = 150 + i * 25 + int(math.sin(self.frame * 0.08 + i) * 15)
            hue = (self.frame * 2 + i * 30) % 360
            pygame.draw.circle(self.image, self._hue_to_rgb(hue, 30 - i * 3),
                             (empress_x, empress_y), halo_r)
        
        # 六翼展开
        wing_span = 250 * self.wing_open
        for wing_side in [-1, 1]:
            for wing_idx in range(3):
                base_angle = wing_side * (0.3 + wing_idx * 0.25) - math.pi / 2
                wing_length = (180 - wing_idx * 30) * self.wing_open
                
                # 每翼的羽毛
                for feather in range(12):
                    f_prog = feather / 11
                    f_angle = base_angle + wing_side * f_prog * 0.8
                    f_length = wing_length * (0.3 + 0.7 * math.sin(f_prog * math.pi))
                    
                    f_wave = math.sin(self.frame * 0.1 + feather * 0.5) * 5
                    
                    fx = empress_x + math.cos(f_angle) * f_length + f_wave * wing_side
                    fy = empress_y + 30 + math.sin(f_angle) * f_length * 0.6
                    
                    # 羽毛颜色
                    hue = (self.frame * 3 + wing_idx * 40 + feather * 15) % 360
                    color = self._hue_to_rgb(hue, int(200 * self.wing_open))
                    
                    # 绘制羽毛
                    pygame.draw.line(self.image, (*color[:3], 40),
                                   (empress_x, empress_y + 30), (int(fx), int(fy)), 8)
                    pygame.draw.line(self.image, (*color[:3], 120),
                                   (empress_x, empress_y + 30), (int(fx), int(fy)), 4)
                    pygame.draw.line(self.image, (255, 255, 255, int(180 * self.wing_open)),
                                   (empress_x, empress_y + 30), (int(fx), int(fy)), 2)
                    
                    # 羽尖星芒
                    if feather % 3 == 0:
                        for s in range(4):
                            s_angle = self.frame * 0.1 + s * math.pi / 2
                            sx = fx + math.cos(s_angle) * 8
                            sy = fy + math.sin(s_angle) * 8
                            pygame.draw.line(self.image, (255, 255, 255, 150),
                                           (int(fx), int(fy)), (int(sx), int(sy)), 1)
        
        # 女皇身体轮廓
        body_alpha = int(220 * self.crown_glow)
        # 头部
        pygame.draw.circle(self.image, (255, 220, 240, body_alpha),
                          (empress_x, empress_y - 20), 25)
        # 身体
        body_pts = [
            (empress_x, empress_y - 40),
            (empress_x + 35, empress_y + 60),
            (empress_x + 20, empress_y + 120),
            (empress_x - 20, empress_y + 120),
            (empress_x - 35, empress_y + 60)
        ]
        pygame.draw.polygon(self.image, (255, 200, 230, body_alpha), body_pts)
        
        # 皇冠
        crown_pts = []
        for i in range(7):
            angle = -math.pi / 2 + (i - 3) * 0.25
            height = 30 if i % 2 == 0 else 18
            cx = empress_x + math.cos(angle) * 25
            cy = empress_y - 40 - height
            crown_pts.append((cx, cy))
        crown_pts.append((empress_x + 25, empress_y - 40))
        crown_pts.append((empress_x - 25, empress_y - 40))
        pygame.draw.polygon(self.image, (255, 215, 100, body_alpha), crown_pts)
        pygame.draw.polygon(self.image, (255, 255, 200, body_alpha), crown_pts, 2)
        
        # 皇冠宝石
        for i in range(3):
            gem_x = empress_x + (i - 1) * 15
            gem_y = empress_y - 55
            hue = (self.frame * 10 + i * 120) % 360
            pygame.draw.circle(self.image, self._hue_to_rgb(hue), (int(gem_x), int(gem_y)), 5)
            pygame.draw.circle(self.image, (255, 255, 255, 200), (int(gem_x - 1), int(gem_y - 1)), 2)
        
        # 眼睛（神圣的凝视）
        for side in [-1, 1]:
            eye_x = empress_x + side * 10
            eye_y = empress_y - 22
            pygame.draw.ellipse(self.image, (255, 255, 255, body_alpha),
                              (eye_x - 6, eye_y - 4, 12, 8))
            # 虹膜
            hue = (self.frame * 5) % 360
            pygame.draw.circle(self.image, self._hue_to_rgb(hue, body_alpha),
                             (int(eye_x), int(eye_y)), 3)
        
        # 毁灭光柱
        if progress > 0.3:
            beam_progress = (progress - 0.3) / 0.7
            if beam_progress < 0.15:
                # 蓄力
                charge = beam_progress / 0.15
                for i in range(12):
                    angle = random.uniform(0, math.pi * 2)
                    dist = 300 * (1 - charge) + 50
                    px = empress_x + math.cos(angle) * dist
                    py = empress_y + 100 + math.sin(angle) * dist * 0.3
                    pygame.draw.line(self.image, (255, 220, 255, int(100 * charge)),
                                   (int(px), int(py)), (empress_x, empress_y + 100), 1)
            else:
                # 光柱
                actual_beam = (beam_progress - 0.15) / 0.85
                beam_width = int(100 + actual_beam * 80)
                
                for layer in range(7):
                    w = beam_width - layer * 15
                    if w > 0:
                        hue = (self.frame * 8 + layer * 25) % 360
                        alpha = 200 - layer * 25
                        color = self._hue_to_rgb(hue, alpha)
                        pygame.draw.rect(self.image, color,
                                       (empress_x - w // 2, empress_y + 80, w, HEIGHT))
                
                # 光柱边缘闪电
                for side in [-1, 1]:
                    for j in range(8):
                        lx = empress_x + side * (beam_width // 2 + 10)
                        ly = empress_y + 100 + j * 60 + (self.frame * 8) % 60
                        if ly < HEIGHT:
                            pts = [(lx, ly)]
                            for k in range(5):
                                lx += random.randint(-25, 25) * side
                                ly += random.randint(15, 35)
                                pts.append((lx, ly))
                            pygame.draw.lines(self.image, (255, 200, 255), False, pts, 2)
                
                # 伤害
                if self.frame % 3 == 0:
                    for enemy in mobs:
                        if abs(enemy.rect.centerx - empress_x) < beam_width // 2 + 50:
                            enemy.hp -= self.damage * 0.8
                            self._add_particle(enemy.rect.centerx, enemy.rect.centery,
                                             random.uniform(-6, 6), random.uniform(-10, -3),
                                             self._hue_to_rgb(random.randint(0, 360)), 25, 6)
        
        # 终焉爆发（最后阶段）
        if progress > 0.85:
            explosion_progress = (progress - 0.85) / 0.15
            exp_r = int(explosion_progress * 400)
            for i in range(5):
                r = exp_r - i * 30
                if r > 0:
                    hue = (self.frame * 20 + i * 40) % 360
                    pygame.draw.circle(self.image, self._hue_to_rgb(hue, 150 - i * 25),
                                     (empress_x, empress_y + 50), r, 5)
            
            # 最终伤害
            if self.frame % 2 == 0:
                for enemy in mobs:
                    enemy.hp -= self.damage * 0.5
        
        self._update_particles()
    
    def update(self):
        self.frame += 1
        
        if self.phase == 0:
            self._phase1_rainbow_curtain()
            if self.frame >= self.phase_duration[0]:
                self.phase = 1
                self.frame = 0
                self.light_plates.clear()
        
        elif self.phase == 1:
            self._phase2_radiant_rain()
            if self.frame >= self.phase_duration[1]:
                self.phase = 2
                self.frame = 0
                self.beams.clear()
        
        elif self.phase == 2:
            self._phase3_empress_descent()
            if self.frame >= self.phase_duration[2]:
                self.kill()


# ==================== G技能：月虹轨道炮（全屏彩虹激光矩阵） ====================
class MoonRainbowRail(pygame.sprite.Sprite):
    """月虹轨道炮 - 全屏彩虹激光矩阵
    
    史诗级全屏特效：
    - 7道彩虹激光从天而降形成光柱矩阵
    - 激光交叉编织成光网
    - 中心汇聚形成棱镜爆发
    - 持续4秒的华丽光之盛宴
    """
    
    def __init__(self, x, y, owner=None, style="default"):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 2 if owner else 40
        self.duration = 240  # 4秒
        self.frame = 0
        self.style = style
        
        # 7道光柱数据
        self.pillars = []
        self._init_pillars()
        
        # 光网数据
        self.web_lines = []
        
        # 中心棱镜
        self.prism_charge = 0
        self.prism_active = False
        
        # 粒子系统
        self.particles = []
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _init_pillars(self):
        """初始化7道光柱"""
        colors = [
            (255, 80, 100),   # 红
            (255, 180, 80),   # 橙
            (255, 255, 100),  # 黄
            (100, 255, 150),  # 绿
            (80, 200, 255),   # 青
            (120, 120, 255),  # 蓝
            (200, 100, 255),  # 紫
        ]
        spacing = WIDTH // 8
        for i in range(7):
            self.pillars.append({
                'x': spacing + i * spacing,
                'y': -100,
                'target_y': HEIGHT + 50,
                'width': 0,
                'max_width': 60,
                'color': colors[i],
                'hue': i * 51,
                'phase': i * 0.3,
                'active': False
            })
    
    def _add_particle(self, x, y, vx, vy, color, life, size=3):
        self.particles.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color, 'life': life, 'max_life': life, 'size': size
        })
    
    def _hue_to_rgb(self, hue, alpha=255):
        h = hue / 60
        x = int(200 * (1 - abs(h % 2 - 1))) + 55
        if h < 1: return (255, x, 180, alpha)
        elif h < 2: return (x, 255, 180, alpha)
        elif h < 3: return (180, 255, x, alpha)
        elif h < 4: return (180, x, 255, alpha)
        elif h < 5: return (x, 180, 255, alpha)
        else: return (255, 180, x, alpha)
    
    def update(self):
        self.frame += 1
        self.duration -= 1
        
        if self.duration <= 0:
            self._final_explosion()
            self.kill()
            return
        
        self._update_pillars()
        self._update_web()
        self._update_prism()
        self._render()
    
    def _update_pillars(self):
        """更新光柱状态"""
        for i, p in enumerate(self.pillars):
            # 依次激活光柱
            if self.frame > i * 8 and not p['active']:
                p['active'] = True
            
            if p['active']:
                # 光柱扩张
                if p['width'] < p['max_width']:
                    p['width'] += 4
                
                # 伤害检测
                if self.frame % 10 == 0:
                    for enemy in mobs:
                        if abs(enemy.rect.centerx - p['x']) < p['width'] // 2 + 20:
                            enemy.hp -= self.damage * 0.25
                            self._add_particle(enemy.rect.centerx, enemy.rect.centery,
                                             random.uniform(-3, 3), random.uniform(-5, -2),
                                             p['color'], 20, 4)
    
    def _update_web(self):
        """更新光网"""
        if self.frame > 60 and self.frame % 20 == 0:
            # 生成新的光网线
            if len(self.web_lines) < 15:
                p1 = random.choice(self.pillars)
                p2 = random.choice(self.pillars)
                if p1 != p2:
                    self.web_lines.append({
                        'x1': p1['x'], 'y1': random.randint(100, HEIGHT - 100),
                        'x2': p2['x'], 'y2': random.randint(100, HEIGHT - 100),
                        'hue': random.randint(0, 360),
                        'life': 60,
                        'max_life': 60
                    })
        
        # 更新光网线生命
        for line in self.web_lines[:]:
            line['life'] -= 1
            if line['life'] <= 0:
                self.web_lines.remove(line)
    
    def _update_prism(self):
        """更新中心棱镜"""
        if self.frame > 120:
            self.prism_charge = min(1, self.prism_charge + 0.015)
        if self.frame > 180:
            self.prism_active = True
    
    def _final_explosion(self):
        """终焉爆发"""
        cx, cy = WIDTH // 2, HEIGHT // 2
        explosion = PrismExplosion(cx, cy)
        all_sprites.add(explosion)
        
        # 全屏伤害
        for enemy in mobs:
            enemy.hp -= self.damage * 2
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        progress = self.frame / 240
        
        # ===== 1. 背景渐变 =====
        bg_alpha = int(40 * min(progress * 3, 1))
        for y in range(0, HEIGHT, 15):
            hue = (y * 0.6 + self.frame * 2) % 360
            color = self._hue_to_rgb(hue, bg_alpha)
            pygame.draw.rect(self.image, color, (0, y, WIDTH, 17))
        
        # ===== 2. 绘制7道光柱 =====
        for p in self.pillars:
            if not p['active']:
                continue
            
            x = p['x']
            w = p['width']
            if w <= 0:
                continue
            
            # 多层光柱
            for layer in range(6):
                layer_w = w - layer * 8
                if layer_w > 0:
                    hue = (p['hue'] + self.frame * 3 + layer * 15) % 360
                    alpha = 180 - layer * 25
                    color = self._hue_to_rgb(hue, alpha)
                    pygame.draw.rect(self.image, color,
                                   (x - layer_w // 2, 0, layer_w, HEIGHT))
            
            # 光柱边缘闪烁
            edge_pulse = abs(math.sin(self.frame * 0.15 + p['phase']))
            for side in [-1, 1]:
                ex = x + side * (w // 2 + 3)
                pygame.draw.line(self.image, (*p['color'], int(150 * edge_pulse)),
                               (ex, 0), (ex, HEIGHT), 2)
            
            # 光柱内流动光点
            for i in range(5):
                py = (self.frame * 8 + i * HEIGHT // 5) % HEIGHT
                point_hue = (p['hue'] + self.frame * 5 + i * 30) % 360
                pygame.draw.circle(self.image, self._hue_to_rgb(point_hue, 200),
                                 (x, py), 6)
                pygame.draw.circle(self.image, (255, 255, 255, 220), (x, py), 3)
        
        # ===== 3. 绘制光网 =====
        for line in self.web_lines:
            alpha = int(180 * line['life'] / line['max_life'])
            hue = (line['hue'] + self.frame * 5) % 360
            color = self._hue_to_rgb(hue, alpha)
            
            # 多层光线
            pygame.draw.line(self.image, (*color[:3], alpha // 3),
                           (line['x1'], line['y1']), (line['x2'], line['y2']), 8)
            pygame.draw.line(self.image, (*color[:3], alpha // 2),
                           (line['x1'], line['y1']), (line['x2'], line['y2']), 4)
            pygame.draw.line(self.image, color,
                           (line['x1'], line['y1']), (line['x2'], line['y2']), 2)
            
            # 交点闪烁
            mid_x = (line['x1'] + line['x2']) // 2
            mid_y = (line['y1'] + line['y2']) // 2
            pygame.draw.circle(self.image, (255, 255, 255, alpha), (mid_x, mid_y), 5)
        
        # ===== 4. 中心棱镜 =====
        if self.prism_charge > 0:
            cx, cy = WIDTH // 2, HEIGHT // 2
            prism_size = int(80 * self.prism_charge)
            
            # 棱镜本体（六边形）
            pts = []
            for i in range(6):
                angle = i * math.pi / 3 + self.frame * 0.03
                px = cx + math.cos(angle) * prism_size
                py = cy + math.sin(angle) * prism_size
                pts.append((px, py))
            
            if len(pts) == 6:
                # 多层棱镜
                for layer in range(4):
                    scale = 1 - layer * 0.15
                    layer_pts = [(cx + (p[0] - cx) * scale, cy + (p[1] - cy) * scale) for p in pts]
                    hue = (self.frame * 8 + layer * 40) % 360
                    alpha = int(180 * self.prism_charge) - layer * 35
                    if alpha > 0:
                        pygame.draw.polygon(self.image, self._hue_to_rgb(hue, alpha), layer_pts)
                
                # 棱镜边框
                pygame.draw.polygon(self.image, (255, 255, 255, int(200 * self.prism_charge)), pts, 3)
                
                # 棱镜光芒
                for i in range(12):
                    ray_angle = self.frame * 0.05 + i * math.pi / 6
                    ray_len = prism_size * (1.5 + 0.5 * math.sin(self.frame * 0.1 + i))
                    rx = cx + math.cos(ray_angle) * ray_len
                    ry = cy + math.sin(ray_angle) * ray_len
                    hue = (self.frame * 10 + i * 30) % 360
                    pygame.draw.line(self.image, self._hue_to_rgb(hue, int(120 * self.prism_charge)),
                                   (cx, cy), (int(rx), int(ry)), 3)
            
            # 能量汇聚线
            if self.prism_active:
                for p in self.pillars:
                    pygame.draw.line(self.image, (*p['color'], 100),
                                   (p['x'], HEIGHT // 2), (cx, cy), 2)
        
        # ===== 5. 粒子更新 =====
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            alpha = int(255 * p['life'] / p['max_life'])
            size = int(p['size'] * p['life'] / p['max_life'])
            if size > 0:
                pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                                 (int(p['x']), int(p['y'])), size)


class PrismExplosion(pygame.sprite.Sprite):
    """棱镜终焉爆发"""
    def __init__(self, x, y):
        super().__init__()
        self.cx, self.cy = x, y
        self.frame = 0
        self.lifetime = 60
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
    
    def _hue_to_rgb(self, hue, alpha=255):
        h = hue / 60
        x = int(200 * (1 - abs(h % 2 - 1))) + 55
        if h < 1: return (255, x, 180, alpha)
        elif h < 2: return (x, 255, 180, alpha)
        elif h < 3: return (180, 255, x, alpha)
        elif h < 4: return (180, x, 255, alpha)
        elif h < 5: return (x, 180, 255, alpha)
        else: return (255, 180, x, alpha)
    
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        progress = self.frame / self.lifetime
        alpha = int(255 * (1 - progress))
        
        # 全屏闪光
        if self.frame < 10:
            flash_alpha = int(200 * (1 - self.frame / 10))
            pygame.draw.rect(self.image, (255, 255, 255, flash_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 多层彩虹冲击波
        for wave in range(7):
            wave_progress = max(0, progress - wave * 0.08)
            wave_r = int(wave_progress * 500)
            wave_alpha = int(150 * (1 - wave_progress))
            if wave_r > 0 and wave_alpha > 0:
                hue = (self.frame * 20 + wave * 50) % 360
                color = self._hue_to_rgb(hue, wave_alpha)
                pygame.draw.circle(self.image, color, (self.cx, self.cy), wave_r, 5)
        
        # 放射光芒
        for i in range(12):
            angle = i * math.pi / 6 + self.frame * 0.05
            ray_len = 400 * progress
            hue = (self.frame * 15 + i * 15) % 360
            color = self._hue_to_rgb(hue, alpha // 2)
            ex = self.cx + math.cos(angle) * ray_len
            ey = self.cy + math.sin(angle) * ray_len
            pygame.draw.line(self.image, color, (self.cx, self.cy), (int(ex), int(ey)), 4)


# ==================== C技能：皇辉领域（女皇神域） ====================
class RadiantDomain(pygame.sprite.Sprite):
    """皇辉领域 - 女皇神域
    
    史诗级领域特效：
    - 全屏神圣结界展开+魔法阵
    - 六翼天使环绕护法
    - 追踪光剑审判敌人
    - 领域结束时释放终焉爆发
    持续6秒
    """
    
    def __init__(self, x, y, owner=None, style="default"):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 2 if owner else 40
        self.duration = 360  # 6秒
        self.frame = 0
        self.style = style
        
        # 领域状态
        self.domain_radius = 0
        self.max_radius = 300
        self.domain_active = False
        
        # 六翼天使
        self.angels = []
        self._init_angels()
        
        # 审判光剑
        self.swords = []
        self.sword_timer = 0
        
        # 魔法阵
        self.magic_circle_rotation = 0
        
        # 粒子
        self.particles = []
        
        if self.owner:
            self.owner.radiant_domain_active = True
            self.owner.radiant_domain_timer = self.duration  # 同步领域计时器
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _init_angels(self):
        """初始化6位天使护法"""
        for i in range(6):
            self.angels.append({
                'angle': i * math.pi / 3,
                'dist': 120,
                'wing_phase': random.uniform(0, math.pi * 2),
                'hue': i * 60,
                'size': random.uniform(0.8, 1.2)
            })
    
    def _add_particle(self, x, y, vx, vy, color, life, size=3):
        self.particles.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color, 'life': life, 'max_life': life, 'size': size
        })
    
    def _hue_to_rgb(self, hue, alpha=255):
        h = hue / 60
        x = int(200 * (1 - abs(h % 2 - 1))) + 55
        if h < 1: return (255, x, 180, alpha)
        elif h < 2: return (x, 255, 180, alpha)
        elif h < 3: return (180, 255, x, alpha)
        elif h < 4: return (180, x, 255, alpha)
        elif h < 5: return (x, 180, 255, alpha)
        else: return (255, 180, x, alpha)
    
    def update(self):
        self.frame += 1
        self.duration -= 1
        
        # 同步更新玩家领域计时器
        if self.owner and hasattr(self.owner, 'radiant_domain_timer'):
            self.owner.radiant_domain_timer = self.duration
        
        # 领域展开
        if self.domain_radius < self.max_radius:
            self.domain_radius += 8
        else:
            self.domain_active = True
        
        # 魔法阵旋转
        self.magic_circle_rotation += 0.02
        
        # 天使环绕
        for angel in self.angels:
            angel['angle'] += 0.015
        
        # 生成审判光剑
        self.sword_timer += 1
        if self.domain_active and self.sword_timer >= 30:
            self.sword_timer = 0
            self._spawn_sword()
        
        # 更新光剑
        self._update_swords()
        
        # 领域伤害
        if self.domain_active and self.frame % 15 == 0:
            cx = self.owner.rect.centerx if self.owner else WIDTH // 2
            cy = self.owner.rect.centery if self.owner else HEIGHT // 2
            for enemy in mobs:
                dist = math.hypot(enemy.rect.centerx - cx, enemy.rect.centery - cy)
                if dist < self.domain_radius:
                    enemy.hp -= self.damage * 0.2
                    self._add_particle(enemy.rect.centerx, enemy.rect.centery,
                                     random.uniform(-3, 3), random.uniform(-5, -2),
                                     self._hue_to_rgb(random.randint(0, 360)), 20, 4)
        
        if self.duration <= 0:
            self._end_domain()
            self.kill()
            return
        
        self._render()
    
    def _spawn_sword(self):
        """生成审判光剑"""
        # 找最近敌人
        cx = self.owner.rect.centerx if self.owner else WIDTH // 2
        cy = self.owner.rect.centery if self.owner else HEIGHT // 2
        
        target = None
        min_dist = float('inf')
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - cx, enemy.rect.centery - cy)
            if dist < self.domain_radius and dist < min_dist:
                min_dist = dist
                target = enemy
        
        if target and len(self.swords) < 8:
            # 从天而降的光剑
            self.swords.append({
                'x': target.rect.centerx + random.randint(-30, 30),
                'y': -50,
                'target_x': target.rect.centerx,
                'target_y': target.rect.centery,
                'speed': 15,
                'hue': random.randint(0, 360),
                'life': 60,
                'hit': False
            })
    
    def _update_swords(self):
        """更新光剑"""
        for sword in self.swords[:]:
            sword['y'] += sword['speed']
            sword['life'] -= 1
            
            # 命中检测
            if not sword['hit'] and sword['y'] >= sword['target_y'] - 20:
                sword['hit'] = True
                # 范围伤害
                for enemy in mobs:
                    dist = math.hypot(enemy.rect.centerx - sword['x'], enemy.rect.centery - sword['y'])
                    if dist < 60:
                        enemy.hp -= self.damage * 0.5
                        for _ in range(5):
                            self._add_particle(enemy.rect.centerx, enemy.rect.centery,
                                             random.uniform(-5, 5), random.uniform(-8, -2),
                                             self._hue_to_rgb(sword['hue']), 25, 5)
            
            if sword['life'] <= 0:
                self.swords.remove(sword)
    
    def _end_domain(self):
        """领域结束"""
        if self.owner:
            self.owner.radiant_domain_active = False
            self.owner.radiant_stacks = 0
        
        cx = self.owner.rect.centerx if self.owner else WIDTH // 2
        cy = self.owner.rect.centery if self.owner else HEIGHT // 2
        explosion = DomainExplosion(cx, cy)
        all_sprites.add(explosion)
        
        # 终焉全屏伤害
        for enemy in mobs:
            enemy.hp -= self.damage * 1.5
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        
        cx = self.owner.rect.centerx if self.owner else WIDTH // 2
        cy = self.owner.rect.centery if self.owner else HEIGHT // 2
        progress = self.frame / 360
        
        # ===== 1. 领域背景光晕 =====
        for i in range(5):
            r = self.domain_radius - i * 20
            if r > 0:
                hue = (self.frame * 2 + i * 30) % 360
                alpha = 30 - i * 5
                pygame.draw.circle(self.image, self._hue_to_rgb(hue, alpha), (cx, cy), int(r))
        
        # ===== 2. 魔法阵 =====
        # 外环
        pygame.draw.circle(self.image, (255, 220, 255, 80), (cx, cy), int(self.domain_radius), 3)
        pygame.draw.circle(self.image, (255, 200, 230, 60), (cx, cy), int(self.domain_radius * 0.85), 2)
        pygame.draw.circle(self.image, (255, 180, 220, 40), (cx, cy), int(self.domain_radius * 0.7), 2)
        
        # 六芒星
        star_r = self.domain_radius * 0.6
        for layer in range(2):
            rot_offset = self.magic_circle_rotation * (1 if layer == 0 else -0.5)
            pts = []
            for i in range(6):
                angle = i * math.pi / 3 + rot_offset + layer * math.pi / 6
                px = cx + math.cos(angle) * star_r * (1 - layer * 0.2)
                py = cy + math.sin(angle) * star_r * (1 - layer * 0.2)
                pts.append((px, py))
            
            # 绘制六芒星
            for i in range(6):
                j = (i + 2) % 6
                hue = (self.frame * 5 + i * 60) % 360
                pygame.draw.line(self.image, self._hue_to_rgb(hue, 100),
                               pts[i], pts[j], 2)
        
        # 符文环
        rune_r = self.domain_radius * 0.75
        for i in range(12):
            rune_angle = self.magic_circle_rotation * 0.5 + i * math.pi / 6
            rx = cx + math.cos(rune_angle) * rune_r
            ry = cy + math.sin(rune_angle) * rune_r
            
            hue = (self.frame * 3 + i * 30) % 360
            color = self._hue_to_rgb(hue, 150)
            
            # 简化符文（发光点）
            pygame.draw.circle(self.image, color, (int(rx), int(ry)), 6)
            pygame.draw.circle(self.image, (255, 255, 255, 180), (int(rx), int(ry)), 3)
        
        # ===== 3. 六翼天使 =====
        for angel in self.angels:
            ax = cx + math.cos(angel['angle']) * angel['dist']
            ay = cy + math.sin(angel['angle']) * angel['dist']
            
            size = 25 * angel['size']
            wing_wave = math.sin(self.frame * 0.15 + angel['wing_phase']) * 0.3
            
            # 天使身体
            body_alpha = 180
            pygame.draw.circle(self.image, (255, 230, 240, body_alpha), (int(ax), int(ay)), int(size * 0.4))
            
            # 天使翅膀
            for wing_side in [-1, 1]:
                for feather in range(5):
                    f_prog = feather / 4
                    f_angle = angel['angle'] + wing_side * (0.3 + f_prog * 0.5 + wing_wave * 0.3)
                    f_length = size * (0.8 + f_prog * 0.6)
                    
                    fx = ax + math.cos(f_angle) * f_length
                    fy = ay + math.sin(f_angle) * f_length
                    
                    hue = (angel['hue'] + self.frame * 3 + feather * 20) % 360
                    color = self._hue_to_rgb(hue, 150)
                    
                    pygame.draw.line(self.image, (*color[:3], 50), (int(ax), int(ay)), (int(fx), int(fy)), 5)
                    pygame.draw.line(self.image, color, (int(ax), int(ay)), (int(fx), int(fy)), 2)
            
            # 天使光环
            halo_r = size * 0.6
            hue = (angel['hue'] + self.frame * 5) % 360
            pygame.draw.circle(self.image, self._hue_to_rgb(hue, 100), (int(ax), int(ay - size * 0.5)), int(halo_r), 2)
        
        # ===== 4. 审判光剑 =====
        for sword in self.swords:
            sx, sy = sword['x'], sword['y']
            hue = sword['hue']
            
            # 光剑本体
            sword_length = 80
            for layer in range(4):
                w = 12 - layer * 3
                alpha = 200 - layer * 40
                color = self._hue_to_rgb(hue + layer * 20, alpha)
                pygame.draw.rect(self.image, color,
                               (sx - w // 2, sy - sword_length, w, sword_length))
            
            # 剑尖
            tip_pts = [
                (sx, sy - sword_length - 20),
                (sx - 8, sy - sword_length),
                (sx + 8, sy - sword_length)
            ]
            pygame.draw.polygon(self.image, self._hue_to_rgb(hue, 220), tip_pts)
            pygame.draw.polygon(self.image, (255, 255, 255, 200), tip_pts, 2)
            
            # 拖尾
            trail_alpha = int(150 * (sword['life'] / 60))
            pygame.draw.rect(self.image, self._hue_to_rgb(hue, trail_alpha // 2),
                           (sx - 3, -50, 6, sy + 50))
            
            # 命中爆炸
            if sword['hit']:
                exp_progress = 1 - sword['life'] / 30
                exp_r = int(60 * exp_progress)
                exp_alpha = int(150 * (1 - exp_progress))
                if exp_r > 0 and exp_alpha > 0:
                    pygame.draw.circle(self.image, self._hue_to_rgb(hue, exp_alpha),
                                     (int(sx), int(sword['target_y'])), exp_r, 3)
        
        # ===== 5. 中心女皇光核 =====
        core_pulse = 1 + 0.15 * math.sin(self.frame * 0.1)
        core_r = int(40 * core_pulse)
        
        # 多层光核
        for i in range(5):
            r = core_r - i * 6
            if r > 0:
                hue = (self.frame * 8 + i * 30) % 360
                alpha = 180 - i * 30
                pygame.draw.circle(self.image, self._hue_to_rgb(hue, alpha), (cx, cy), r)
        
        # 皇冠
        crown_r = core_r * 0.8
        crown_pts = []
        for i in range(7):
            angle = -math.pi / 2 + (i - 3) * 0.3
            height = crown_r if i % 2 == 0 else crown_r * 0.5
            crown_pts.append((cx + math.cos(angle) * crown_r * 0.8, cy - core_r - height * 0.3))
        if len(crown_pts) >= 3:
            pygame.draw.polygon(self.image, (255, 215, 100, 200), crown_pts)
            pygame.draw.polygon(self.image, (255, 255, 200, 150), crown_pts, 2)
        
        # 核心白光
        pygame.draw.circle(self.image, (255, 255, 255, 220), (cx, cy), core_r // 3)
        
        # ===== 6. 粒子更新 =====
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            alpha = int(255 * p['life'] / p['max_life'])
            size = int(p['size'] * p['life'] / p['max_life'])
            if size > 0:
                pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                                 (int(p['x']), int(p['y'])), size)


class DomainExplosion(pygame.sprite.Sprite):
    """领域终焉爆发 - 全屏彩虹冲击波"""
    def __init__(self, x, y):
        super().__init__()
        self.cx, self.cy = x, y
        self.frame = 0
        self.lifetime = 60
        self.damage = 150
        self.hit = False
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
    
    def _hue_to_rgb(self, hue, alpha=255):
        h = hue / 60
        x = int(200 * (1 - abs(h % 2 - 1))) + 55
        if h < 1: return (255, x, 180, alpha)
        elif h < 2: return (x, 255, 180, alpha)
        elif h < 3: return (180, 255, x, alpha)
        elif h < 4: return (180, x, 255, alpha)
        elif h < 5: return (x, 180, 255, alpha)
        else: return (255, 180, x, alpha)
    
    def update(self):
        self.frame += 1
        
        # 伤害判定
        if not self.hit and self.frame == 5:
            self.hit = True
            for enemy in mobs:
                enemy.hp -= self.damage
        
        if self.frame >= self.lifetime:
            self.kill()
            return
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        progress = self.frame / self.lifetime
        alpha = int(255 * (1 - progress))
        
        # 全屏白闪
        if self.frame < 15:
            flash_alpha = int(220 * (1 - self.frame / 15))
            pygame.draw.rect(self.image, (255, 255, 255, flash_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 多层彩虹冲击波
        for wave in range(8):
            wave_delay = wave * 0.06
            wave_progress = max(0, progress - wave_delay)
            if wave_progress > 0:
                wave_r = int(wave_progress * 600)
                wave_alpha = int(180 * (1 - wave_progress) * (1 - wave * 0.1))
                if wave_r > 0 and wave_alpha > 0:
                    hue = (self.frame * 15 + wave * 45) % 360
                    color = self._hue_to_rgb(hue, wave_alpha)
                    pygame.draw.circle(self.image, color, (self.cx, self.cy), wave_r, 6 - wave // 2)
        
        # 放射光芒
        for i in range(16):
            angle = i * math.pi / 8 + self.frame * 0.03
            ray_progress = min(1, progress * 2)
            ray_len = 500 * ray_progress
            
            hue = (self.frame * 10 + i * 22) % 360
            ray_alpha = int(alpha * 0.6)
            color = self._hue_to_rgb(hue, ray_alpha)
            
            ex = self.cx + math.cos(angle) * ray_len
            ey = self.cy + math.sin(angle) * ray_len
            
            pygame.draw.line(self.image, (*color[:3], ray_alpha // 3),
                           (self.cx, self.cy), (int(ex), int(ey)), 10)
            pygame.draw.line(self.image, (*color[:3], ray_alpha // 2),
                           (self.cx, self.cy), (int(ex), int(ey)), 5)
            pygame.draw.line(self.image, color,
                           (self.cx, self.cy), (int(ex), int(ey)), 2)
        
        # 飞散棱光碎片
        for i in range(15):
            shard_angle = i * math.pi * 2 / 15 + self.frame * 0.02
            shard_speed = 8 + (i % 5) * 2
            shard_dist = shard_speed * self.frame
            
            sx = self.cx + math.cos(shard_angle) * shard_dist
            sy = self.cy + math.sin(shard_angle) * shard_dist
            
            if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
                shard_alpha = int(200 * (1 - progress))
                hue = (i * 12 + self.frame * 8) % 360
                color = self._hue_to_rgb(hue, shard_alpha)
                
                # 菱形碎片
                size = 8 * (1 - progress * 0.5)
                pts = [
                    (sx, sy - size),
                    (sx + size * 0.6, sy),
                    (sx, sy + size),
                    (sx - size * 0.6, sy)
                ]
                if shard_alpha > 0:
                    pygame.draw.polygon(self.image, color, pts)
        
        # 中心残留光核
        core_r = int(80 * (1 - progress * 0.8))
        if core_r > 0:
            for i in range(4):
                r = core_r - i * 12
                if r > 0:
                    hue = (self.frame * 20 + i * 40) % 360
                    ca = int(alpha * (1 - i * 0.2))
                    pygame.draw.circle(self.image, self._hue_to_rgb(hue, ca), (self.cx, self.cy), r)
            pygame.draw.circle(self.image, (255, 255, 255, alpha), (self.cx, self.cy), core_r // 3)


# ==================== 击杀特效：Rainbow Crash ====================
class RainbowCrash(pygame.sprite.Sprite):
    """Rainbow Crash - 击杀彩虹碎裂特效"""
    
    def __init__(self, x, y, enemy_size=40, style="default"):
        super().__init__()
        self.float_x, self.float_y = x, y
        self.frame = 0
        self.lifetime = 50
        self.enemy_size = enemy_size
        self.style = style  # 涂装样式
        self.shards = []
        for i in range(12):
            angle = i * math.pi / 6 + random.uniform(-0.2, 0.2)
            speed = random.uniform(3, 8)
            hue = i * 30
            size = random.randint(8, 16)
            self.shards.append({
                'x': x, 'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'hue': hue, 'size': size,
                'rot': random.uniform(0, math.pi * 2),
                'rot_speed': random.uniform(-0.2, 0.2)
            })
        self.image = pygame.Surface((300, 300), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        for shard in self.shards:
            shard['x'] += shard['vx']
            shard['y'] += shard['vy']
            shard['vy'] += 0.15
            shard['rot'] += shard['rot_speed']
        self._render()
        
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 150, 150
        progress = self.frame / self.lifetime
        alpha = int(255 * (1 - progress))
        
        if self.frame < 10:
            flash_alpha = int(255 * (1 - self.frame / 10))
            flash_r = int(30 + self.frame * 8)
            pygame.draw.circle(self.image, (255, 255, 255, flash_alpha), (cx, cy), flash_r)
        
        for shard in self.shards:
            sx = cx + (shard['x'] - self.float_x)
            sy = cy + (shard['y'] - self.float_y)
            hue = (shard['hue'] + self.frame * 5) % 360
            h = hue / 60
            x_c = int(200 * (1 - abs(h % 2 - 1))) + 55
            if h < 1: color = (255, x_c, 180, alpha)
            elif h < 2: color = (x_c, 255, 180, alpha)
            elif h < 3: color = (180, 255, x_c, alpha)
            elif h < 4: color = (180, x_c, 255, alpha)
            elif h < 5: color = (x_c, 180, 255, alpha)
            else: color = (255, 180, x_c, alpha)
            size = shard['size'] * (1 - progress * 0.5)
            rot = shard['rot']
            points = []
            for i in range(3):
                a = rot + i * math.pi * 2 / 3
                px = sx + math.cos(a) * size
                py = sy + math.sin(a) * size
                points.append((px, py))
            if len(points) == 3 and size > 1:
                pygame.draw.polygon(self.image, color, points)
        
        if self.frame < 20:
            wave_r = int(self.frame * 10)
            wave_alpha = int(200 * (1 - self.frame / 20))
            for i in range(6):
                hue = (self.frame * 30 + i * 60) % 360
                h = hue / 60
                x_c = int(200 * (1 - abs(h % 2 - 1))) + 55
                a = max(0, wave_alpha - i * 30)
                if h < 1: color = (255, x_c, 180, a)
                elif h < 2: color = (x_c, 255, 180, a)
                elif h < 3: color = (180, 255, x_c, a)
                elif h < 4: color = (180, x_c, 255, a)
                elif h < 5: color = (x_c, 180, 255, a)
                else: color = (255, 180, x_c, a)
                pygame.draw.circle(self.image, color, (cx, cy), wave_r + i * 5, 3)


def spawn_rainbow_crash(x, y, enemy_size=40, style="default"):
    """生成击杀特效"""
    effect = RainbowCrash(x, y, enemy_size, style)
    all_sprites.add(effect)
    return effect
