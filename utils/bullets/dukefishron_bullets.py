# -*- coding: utf-8 -*-
"""
深渊龙鱼·猪公爵 - 专属子弹模块
鲨龙卷横扫，深渊泡折射，海啸席卷

特性：
- 深渊水矛：远程射击，命中生成鲨龙卷
- 鲨龙卷：留场2.5s，吸扯+发射小鲨追踪弹
- 深渊泡：拾取后折射分裂
- 龙鱼俯冲：低空滑行无敌+海浪幕DOT
"""
import pygame
import math
import random
from config import all_sprites, mobs, WIDTH, HEIGHT

# ==================== 主题配色 ====================
DUKE_BULLET_THEMES = {
    "default": {
        "water": (30, 80, 180),        # 深海蓝
        "pink": (255, 120, 180),       # 龙鱼粉
        "foam": (180, 220, 255),       # 海沫白
        "trail": (50, 100, 200),       # 水流拖尾
        "tornado": (40, 120, 220),     # 龙卷蓝
        "bubble": (100, 180, 255),     # 气泡色
        "shark": (60, 90, 150),        # 小鲨灰蓝
    },
    "abyss": {
        # 深渊形态 - 暗紫深蓝
        "water": (40, 30, 120),
        "pink": (180, 80, 200),
        "foam": (150, 140, 220),
        "trail": (60, 40, 150),
        "tornado": (70, 50, 180),
        "bubble": (120, 100, 200),
        "shark": (80, 60, 140),
    },
    "rage": {
        # 狂暴形态 - 血红黑
        "water": (150, 30, 50),
        "pink": (255, 80, 100),
        "foam": (255, 180, 180),
        "trail": (180, 40, 60),
        "tornado": (200, 50, 80),
        "bubble": (255, 120, 140),
        "shark": (120, 40, 60),
    },
    "storm": {
        # 风暴形态 - 电光蓝白
        "water": (80, 150, 255),
        "pink": (200, 220, 255),
        "foam": (240, 250, 255),
        "trail": (100, 180, 255),
        "tornado": (120, 200, 255),
        "bubble": (180, 220, 255),
        "shark": (100, 150, 220),
    },
    "coral": {
        # 珊瑚礁 - 粉橙绿
        "water": (50, 180, 150),
        "pink": (255, 150, 120),
        "foam": (255, 220, 200),
        "trail": (80, 200, 170),
        "tornado": (100, 220, 180),
        "bubble": (255, 180, 150),
        "shark": (80, 150, 130),
    },
    "void_sea": {
        # 虚空之海 - 暗黑紫
        "water": (20, 15, 60),
        "pink": (120, 50, 150),
        "foam": (100, 80, 140),
        "trail": (40, 25, 80),
        "tornado": (60, 40, 120),
        "bubble": (80, 60, 140),
        "shark": (50, 35, 100),
    },
    "tsunami": {
        # 海啸形态 - 深浪蓝青
        "water": (20, 100, 180),
        "pink": (120, 200, 255),
        "foam": (200, 240, 255),
        "trail": (60, 140, 200),
        "tornado": (80, 180, 240),
        "bubble": (140, 220, 255),
        "shark": (50, 120, 180),
    },
    "phantom": {
        # 幽灵形态 - 幽白透蓝
        "water": (180, 200, 220),
        "pink": (140, 180, 200),
        "foam": (220, 240, 255),
        "trail": (160, 190, 210),
        "tornado": (170, 200, 230),
        "bubble": (200, 230, 255),
        "shark": (150, 175, 200),
    },
    "blood_moon": {
        # 血月形态 - 血红暗黑
        "water": (120, 20, 40),
        "pink": (200, 50, 80),
        "foam": (255, 100, 120),
        "trail": (100, 30, 50),
        "tornado": (180, 40, 70),
        "bubble": (220, 80, 100),
        "shark": (100, 25, 45),
    },
    "tropical": {
        # 热带形态 - 金粉彩虹
        "water": (255, 180, 50),
        "pink": (255, 100, 150),
        "foam": (255, 220, 150),
        "trail": (255, 160, 80),
        "tornado": (255, 200, 100),
        "bubble": (255, 150, 180),
        "shark": (255, 140, 60),
    },
    "frost": {
        # 寒霜形态 - 冰蓝霜白
        "water": (100, 180, 220),
        "pink": (180, 220, 255),
        "foam": (220, 245, 255),
        "trail": (130, 200, 240),
        "tornado": (150, 210, 250),
        "bubble": (190, 230, 255),
        "shark": (110, 170, 210),
    },
    "golden": {
        # 黄金形态 - 皇金烈焰
        "water": (220, 180, 50),
        "pink": (255, 220, 100),
        "foam": (255, 245, 200),
        "trail": (230, 190, 70),
        "tornado": (240, 200, 90),
        "bubble": (255, 230, 150),
        "shark": (200, 160, 50),
    },
}


# ==================== 深渊水矛（主武器）====================
class AbyssSpear(pygame.sprite.Sprite):
    """深渊水矛 - 主武器，1.3屏射程，命中生成鲨龙卷"""
    
    def __init__(self, x, y, damage, owner=None, style="default", is_refract=False):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.piercing = 1 if not is_refract else 2  # 折射泡可穿透1次
        self.style = style
        self.is_refract = is_refract  # 是否折射模式
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed = 22
        self.max_range = HEIGHT * 1.3  # 1.3屏射程
        self.traveled = 0
        
        self.frame = 0
        self.angle = -math.pi / 2  # 向上
        
        # 水流拖尾
        self.trail = []
        
        self.image = pygame.Surface((20, 50), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
    def update(self):
        self.frame += 1
        
        # 移动
        dx = math.cos(self.angle) * self.speed
        dy = math.sin(self.angle) * self.speed
        self.float_x += dx
        self.float_y += dy
        self.traveled += self.speed
        
        # 记录拖尾
        self.trail.append((self.float_x, self.float_y))
        if len(self.trail) > 8:
            self.trail.pop(0)
        
        # 超出射程
        if self.traveled > self.max_range or self.float_y < -50:
            self.kill()
            return
        
        # 命中检测
        self._check_hit()
        
        self._render()
        self.rect.center = (int(self.float_x), int(self.float_y))
    
    def _check_hit(self):
        for mob in mobs:
            if self.rect.colliderect(mob.rect):
                mob.take_damage(self.damage)
                self._spawn_tornado()
                self._spawn_hit_effect()
                
                # 折射模式：分裂2枚小泡追踪弹
                if self.is_refract and self.piercing > 0:
                    self._spawn_refract_bubbles()
                    self.piercing -= 1
                    if self.piercing <= 0:
                        self.kill()
                    return
                
                self.kill()
                return
    
    def _spawn_tornado(self):
        """命中时生成鲨龙卷"""
        tornado = SharkTornado(self.float_x, self.float_y, self.owner, self.style)
        all_sprites.add(tornado)
    
    def _spawn_refract_bubbles(self):
        """折射分裂小泡"""
        for i in range(2):
            angle = self.angle + (i - 0.5) * math.pi / 3
            bubble = MiniSharkBullet(self.float_x, self.float_y, 
                                     self.damage * 0.5, self.owner, self.style, angle)
            all_sprites.add(bubble)
    
    def _spawn_hit_effect(self):
        effect = SpearHitEffect(self.float_x, self.float_y, self.style)
        all_sprites.add(effect)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = DUKE_BULLET_THEMES.get(self.style, DUKE_BULLET_THEMES["default"])
        water = theme["water"]
        pink = theme["pink"]
        foam = theme["foam"]
        
        cx, cy = 10, 25
        
        # 水流脉动
        pulse = math.sin(self.frame * 0.4) * 0.1 + 1.0
        
        # ========== 根据涂装渲染不同形状 ==========
        style = self.style
        
        if style == "abyss":
            # 深渊之矛 - 暗紫扭曲矛+虚空裂隙
            spear_len = int(22 * pulse)
            spear_w = int(7 * pulse)
            
            # 虚空光晕
            for i in range(2):
                r = spear_w + 4 + i * 3
                pygame.draw.circle(self.image, (*water, 60 - i * 20), (cx, cy), r)
            
            # 扭曲矛身 - 不规则边缘
            twist = math.sin(self.frame * 0.5) * 2
            spear_pts = [
                (cx, cy - spear_len - 10),
                (cx + spear_w + twist, cy - spear_len // 2),
                (cx + spear_w - 1, cy + spear_len // 3),
                (cx, cy + spear_len // 2),
                (cx - spear_w + 1, cy + spear_len // 3),
                (cx - spear_w - twist, cy - spear_len // 2),
            ]
            pygame.draw.polygon(self.image, pink, spear_pts)
            
            # 裂隙效果
            for i in range(3):
                rift_angle = self.frame * 0.3 + i * math.pi * 2 / 3
                rx = cx + math.cos(rift_angle) * 6
                ry = cy + math.sin(rift_angle) * 8
                pygame.draw.line(self.image, (*foam, 180), (cx, cy - 5), (int(rx), int(ry)), 2)
        
        elif style == "rage":
            # 狂暴獠牙矛 - 尖锐锯齿+血雾
            spear_len = int(24 * pulse)
            
            # 血雾光晕
            for i in range(2):
                r = 8 + i * 4
                pygame.draw.circle(self.image, (*water, 80 - i * 30), (cx, cy - 5), r)
            
            # 锯齿矛身
            teeth_pts = []
            teeth_count = 4
            for i in range(teeth_count):
                t = i / (teeth_count - 1)
                y_pos = cy - spear_len + t * spear_len * 1.3
                # 左侧锯齿
                if i % 2 == 0:
                    teeth_pts.append((cx - 5 - (1-t) * 3, int(y_pos)))
                else:
                    teeth_pts.append((cx - 3, int(y_pos)))
            # 底部
            teeth_pts.append((cx, cy + 8))
            # 右侧锯齿（反向）
            for i in range(teeth_count - 1, -1, -1):
                t = i / (teeth_count - 1)
                y_pos = cy - spear_len + t * spear_len * 1.3
                if i % 2 == 0:
                    teeth_pts.append((cx + 5 + (1-t) * 3, int(y_pos)))
                else:
                    teeth_pts.append((cx + 3, int(y_pos)))
            
            pygame.draw.polygon(self.image, pink, teeth_pts)
            pygame.draw.polygon(self.image, foam, teeth_pts, 1)
            
            # 血滴粒子
            drip_y = cy + 8 + abs(math.sin(self.frame * 0.3)) * 6
            pygame.draw.circle(self.image, water, (cx, int(drip_y)), 2)
        
        elif style == "storm":
            # 电弧矛 - 闪电环绕+电光
            spear_len = int(20 * pulse)
            spear_w = int(5 * pulse)
            
            # 电光外层
            for i in range(3):
                flash = math.sin(self.frame * 0.8 + i) * 0.5 + 0.5
                r = spear_w + 5 + i * 2
                alpha = int(100 * flash)
                pygame.draw.circle(self.image, (*foam, alpha), (cx, cy), r)
            
            # 闪电矛身
            pygame.draw.ellipse(self.image, pink, 
                              (cx - spear_w, cy - spear_len, spear_w * 2, spear_len * 2))
            
            # 电弧环绕
            for i in range(4):
                arc_angle = self.frame * 0.5 + i * math.pi / 2
                ax1 = cx + math.cos(arc_angle) * 8
                ay1 = cy + math.sin(arc_angle) * 6
                ax2 = cx + math.cos(arc_angle + 0.5) * 10
                ay2 = cy + math.sin(arc_angle + 0.5) * 8
                pygame.draw.line(self.image, foam, (int(ax1), int(ay1)), (int(ax2), int(ay2)), 2)
            
            # 矛尖闪电
            pygame.draw.polygon(self.image, foam, [
                (cx, cy - spear_len - 12),
                (cx - 3, cy - spear_len),
                (cx + 3, cy - spear_len),
            ])
        
        elif style == "coral":
            # 珊瑚矛 - 珊瑚形状+小鱼围绕
            spear_len = int(18 * pulse)
            spear_w = int(6 * pulse)
            
            # 珊瑚分支
            branch_pts = [
                (cx, cy - spear_len - 5),
                (cx - 4, cy - spear_len + 5),
                (cx - spear_w, cy - spear_len // 2),
                (cx - spear_w + 2, cy),
                (cx - 3, cy + spear_len // 3),
                (cx + 3, cy + spear_len // 3),
                (cx + spear_w - 2, cy),
                (cx + spear_w, cy - spear_len // 2),
                (cx + 4, cy - spear_len + 5),
            ]
            pygame.draw.polygon(self.image, pink, branch_pts)
            
            # 珊瑚纹理点
            for i in range(4):
                px = cx + (i - 1.5) * 3
                py = cy - 5 + i * 3
                pygame.draw.circle(self.image, foam, (int(px), int(py)), 2)
            
            # 小鱼环绕
            for i in range(2):
                fish_angle = self.frame * 0.2 + i * math.pi
                fx = cx + math.cos(fish_angle) * 10
                fy = cy + math.sin(fish_angle) * 6
                pygame.draw.circle(self.image, water, (int(fx), int(fy)), 3)
                # 鱼尾
                tx = fx - math.cos(fish_angle) * 4
                ty = fy - math.sin(fish_angle) * 2
                pygame.draw.circle(self.image, water, (int(tx), int(ty)), 2)
        
        elif style == "void_sea":
            # 虚空矛 - 黑洞扭曲+空间撕裂
            spear_len = int(20 * pulse)
            
            # 黑洞核心
            pygame.draw.circle(self.image, (10, 5, 30), (cx, cy), 8)
            
            # 事件视界
            for i in range(3):
                r = 10 + i * 3 + int(math.sin(self.frame * 0.3) * 2)
                pygame.draw.circle(self.image, (*water, 80 - i * 20), (cx, cy), r, 1)
            
            # 扭曲空间线
            for i in range(6):
                angle = self.frame * 0.2 + i * math.pi / 3
                inner_r = 5
                outer_r = 15 + math.sin(self.frame * 0.5 + i) * 3
                x1 = cx + math.cos(angle) * inner_r
                y1 = cy + math.sin(angle) * inner_r
                x2 = cx + math.cos(angle + 0.3) * outer_r
                y2 = cy + math.sin(angle + 0.3) * outer_r
                pygame.draw.line(self.image, (*pink, 150), (int(x1), int(y1)), (int(x2), int(y2)), 2)
            
            # 吞噬之矛
            pygame.draw.polygon(self.image, foam, [
                (cx, cy - spear_len - 5),
                (cx - 4, cy - 8),
                (cx + 4, cy - 8),
            ])
        
        elif style == "tsunami":
            # 海啸巨浪矛 - 浪形轮廓+浪花粒子
            spear_len = int(22 * pulse)
            wave_w = int(8 * pulse)
            
            # 浪形轮廓
            wave_offset = math.sin(self.frame * 0.4) * 2
            wave_pts = [
                (cx, cy - spear_len - 6),
                (cx + wave_w + wave_offset, cy - spear_len // 2),
                (cx + wave_w - 2, cy - 2),
                (cx + wave_w // 2, cy + 5 + wave_offset),
                (cx, cy + 8),
                (cx - wave_w // 2, cy + 5 - wave_offset),
                (cx - wave_w + 2, cy - 2),
                (cx - wave_w - wave_offset, cy - spear_len // 2),
            ]
            pygame.draw.polygon(self.image, water, wave_pts)
            pygame.draw.polygon(self.image, foam, wave_pts, 2)
            
            # 浪花泡沫
            for i in range(3):
                bx = cx + (i - 1) * 4
                by = cy - spear_len // 2 + math.sin(self.frame * 0.5 + i) * 3
                pygame.draw.circle(self.image, foam, (int(bx), int(by)), 2)
            
            # 矛尖卷浪
            curl_x = cx + math.sin(self.frame * 0.6) * 2
            pygame.draw.circle(self.image, foam, (int(curl_x), int(cy - spear_len - 3)), 3)
        
        elif style == "phantom":
            # 幽灵矛 - 半透明飘渺+灵魂尾迹
            spear_len = int(20 * pulse)
            spear_w = int(6 * pulse)
            
            # 透明度波动
            ghost_alpha = int(120 + 60 * math.sin(self.frame * 0.3))
            
            # 幽灵光晕
            for i in range(3):
                r = spear_w + i * 4
                alpha = int((80 - i * 20) * (ghost_alpha / 180))
                pygame.draw.circle(self.image, (*water, alpha), (cx, cy), r)
            
            # 飘渺矛身
            wave = math.sin(self.frame * 0.4) * 2
            phantom_pts = [
                (cx, cy - spear_len - 8),
                (cx + spear_w + wave, cy - spear_len // 3),
                (cx + spear_w - 1 - wave, cy + spear_len // 3),
                (cx, cy + spear_len // 2),
                (cx - spear_w + 1 + wave, cy + spear_len // 3),
                (cx - spear_w - wave, cy - spear_len // 3),
            ]
            pygame.draw.polygon(self.image, (*pink, ghost_alpha), phantom_pts)
            
            # 灵魂粒子尾迹
            for i in range(4):
                trail_y = cy + spear_len // 2 + i * 4
                trail_alpha = ghost_alpha - i * 25
                if trail_alpha > 0:
                    pygame.draw.circle(self.image, (*foam, trail_alpha), 
                                     (cx, int(trail_y)), 3 - i // 2)
        
        elif style == "blood_moon":
            # 血月獠牙 - 双獠牙+滴血
            fang_len = int(24 * pulse)
            
            # 血色光晕
            pygame.draw.circle(self.image, (*water, 100), (cx, cy - 5), 10)
            
            # 左獠牙
            left_fang = [
                (cx - 2, cy - fang_len - 8),
                (cx - 6, cy - fang_len // 2),
                (cx - 4, cy + 5),
                (cx - 1, cy + 5),
            ]
            pygame.draw.polygon(self.image, pink, left_fang)
            
            # 右獠牙
            right_fang = [
                (cx + 2, cy - fang_len - 8),
                (cx + 6, cy - fang_len // 2),
                (cx + 4, cy + 5),
                (cx + 1, cy + 5),
            ]
            pygame.draw.polygon(self.image, pink, right_fang)
            
            # 獠牙边缘高光
            pygame.draw.polygon(self.image, foam, left_fang, 1)
            pygame.draw.polygon(self.image, foam, right_fang, 1)
            
            # 滴血效果
            drip_progress = (self.frame % 30) / 30
            drip_y = cy + 5 + drip_progress * 12
            drip_size = 3 - int(drip_progress * 2)
            if drip_size > 0:
                pygame.draw.circle(self.image, water, (cx, int(drip_y)), drip_size)
        
        elif style == "tropical":
            # 热带彩虹矛 - 彩虹渐变+热带鱼
            spear_len = int(20 * pulse)
            spear_w = int(6 * pulse)
            
            # 彩虹光环
            rainbow_colors = [
                (255, 100, 100), (255, 180, 80), (255, 255, 100),
                (100, 255, 150), (100, 200, 255), (180, 120, 255)
            ]
            for i, rc in enumerate(rainbow_colors):
                ring_r = spear_w + 2 + i
                pygame.draw.circle(self.image, (*rc, 120), (cx, cy), ring_r, 1)
            
            # 金色矛身
            pygame.draw.ellipse(self.image, pink,
                              (cx - spear_w, cy - spear_len, spear_w * 2, spear_len * 2))
            pygame.draw.ellipse(self.image, foam,
                              (cx - spear_w + 2, cy - spear_len + 3, 
                               spear_w * 2 - 4, spear_len * 2 - 6))
            
            # 矛尖星芒
            pygame.draw.polygon(self.image, (255, 255, 200), [
                (cx, cy - spear_len - 10),
                (cx - 4, cy - spear_len + 2),
                (cx + 4, cy - spear_len + 2),
            ])
            
            # 热带鱼
            fish_angle = self.frame * 0.25
            fx = cx + math.cos(fish_angle) * 9
            fy = cy + math.sin(fish_angle) * 5
            pygame.draw.circle(self.image, (255, 150, 100), (int(fx), int(fy)), 3)
        
        elif style == "frost":
            # 冰晶矛 - 六边形冰晶+霜冻粒子
            spear_len = int(22 * pulse)
            
            # 冰霜光晕
            for i in range(2):
                r = 10 + i * 4
                pygame.draw.circle(self.image, (*foam, 80 - i * 25), (cx, cy), r)
            
            # 冰晶六边形矛身
            hex_r = 6
            hex_pts = []
            for i in range(6):
                angle = i * math.pi / 3 - math.pi / 2
                hx = cx + math.cos(angle) * hex_r
                hy = cy + math.sin(angle) * hex_r
                hex_pts.append((int(hx), int(hy)))
            pygame.draw.polygon(self.image, water, hex_pts)
            pygame.draw.polygon(self.image, foam, hex_pts, 1)
            
            # 冰晶尖端
            pygame.draw.polygon(self.image, foam, [
                (cx, cy - spear_len - 8),
                (cx - 5, cy - hex_r),
                (cx + 5, cy - hex_r),
            ])
            
            # 霜冻粒子
            for i in range(4):
                frost_angle = self.frame * 0.2 + i * math.pi / 2
                frost_dist = 10 + math.sin(self.frame * 0.4 + i) * 3
                frost_x = cx + math.cos(frost_angle) * frost_dist
                frost_y = cy + math.sin(frost_angle) * frost_dist * 0.6
                pygame.draw.circle(self.image, (220, 245, 255), (int(frost_x), int(frost_y)), 2)
        
        elif style == "golden":
            # 帝王金矛 - 皇冠形+金焰环绕
            spear_len = int(22 * pulse)
            spear_w = int(7 * pulse)
            
            # 金焰光晕
            flame_pulse = abs(math.sin(self.frame * 0.4))
            for i in range(3):
                r = spear_w + 3 + i * 3 + int(flame_pulse * 2)
                alpha = int((120 - i * 30) * (0.7 + flame_pulse * 0.3))
                pygame.draw.circle(self.image, (*pink, alpha), (cx, cy), r)
            
            # 皇冠矛身
            crown_pts = [
                (cx, cy - spear_len - 10),
                (cx - 3, cy - spear_len),
                (cx - spear_w, cy - spear_len // 2),
                (cx - spear_w + 2, cy + 3),
                (cx, cy + 8),
                (cx + spear_w - 2, cy + 3),
                (cx + spear_w, cy - spear_len // 2),
                (cx + 3, cy - spear_len),
            ]
            pygame.draw.polygon(self.image, water, crown_pts)
            pygame.draw.polygon(self.image, foam, crown_pts, 2)
            
            # 皇冠尖齿
            for i in range(3):
                tip_x = cx - 4 + i * 4
                tip_h = 5 + (1 if i == 1 else 0) * 3
                pygame.draw.polygon(self.image, pink, [
                    (tip_x, int(cy - spear_len - tip_h)),
                    (tip_x - 2, int(cy - spear_len + 2)),
                    (tip_x + 2, int(cy - spear_len + 2)),
                ])
            
            # 金焰粒子
            for i in range(3):
                flame_angle = self.frame * 0.4 + i * math.pi * 2 / 3
                flame_r = 12 + math.sin(self.frame * 0.5 + i) * 2
                flame_x = cx + math.cos(flame_angle) * flame_r
                flame_y = cy + math.sin(flame_angle) * flame_r * 0.5
                pygame.draw.circle(self.image, foam, (int(flame_x), int(flame_y)), 3)
        
        else:
            # 默认 - 标准深渊水矛
            spear_len = int(20 * pulse)
            spear_w = int(6 * pulse)
            
            # 外层水光
            pygame.draw.ellipse(self.image, (*water, 150), 
                              (cx - spear_w, cy - spear_len, spear_w * 2, spear_len * 2))
            
            # 内层亮芯
            inner_w = spear_w - 2
            inner_len = spear_len - 3
            pygame.draw.ellipse(self.image, (*foam, 200),
                              (cx - inner_w, cy - inner_len, inner_w * 2, inner_len * 2))
            
            # 矛尖
            tip_pts = [
                (cx, cy - spear_len - 8),
                (cx - 4, cy - spear_len + 2),
                (cx + 4, cy - spear_len + 2),
            ]
            pygame.draw.polygon(self.image, pink, tip_pts)
            pygame.draw.polygon(self.image, foam, tip_pts, 1)
        
        # 折射模式特效（所有涂装通用）
        if self.is_refract:
            # 气泡环绕
            for i in range(3):
                b_angle = self.frame * 0.3 + i * math.pi * 2 / 3
                bx = cx + math.cos(b_angle) * 8
                by = cy + math.sin(b_angle) * 5
                pygame.draw.circle(self.image, (*theme["bubble"], 150), (int(bx), int(by)), 3)


# ==================== 鲨龙卷（留场实体）====================
class SharkTornado(pygame.sprite.Sprite):
    """鲨龙卷 - 留场2.5s，吸扯敌人+发射小鲨追踪弹"""
    
    def __init__(self, x, y, owner=None, style="default"):
        super().__init__()
        self.owner = owner
        self.is_enemy = False
        self.damage = 0  # 本身不造成伤害
        self.style = style
        
        self.float_x = float(x)
        self.float_y = float(y)
        
        # 生命周期
        self.lifetime = 150  # 2.5秒
        self.frame = 0
        self.active = True
        self.exploded = False
        
        # 吸扯范围
        self.pull_radius = 120
        self.pull_strength = 2.5
        
        # 小鲨发射
        self.shark_timer = 0
        self.shark_interval = 30  # 0.5秒一发
        
        # 龙卷视觉
        self.rotation = 0
        self.particles = []
        
        # 注册到owner
        if owner and hasattr(owner, 'active_tornados'):
            owner.active_tornados.append(self)
        
        self.image = pygame.Surface((100, 140), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self._fade_out()
            return
        
        if not self.active:
            return
        
        # 旋转
        self.rotation += 0.15
        
        # 吸扯敌人
        self._pull_enemies()
        
        # 发射小鲨
        self.shark_timer += 1
        if self.shark_timer >= self.shark_interval:
            self.shark_timer = 0
            self._fire_shark()
        
        # 更新粒子
        self._update_particles()
        
        self._render()
        self.rect.center = (int(self.float_x), int(self.float_y))
    
    def _pull_enemies(self):
        """吸扯范围内敌人"""
        for enemy in mobs:
            dx = self.float_x - enemy.rect.centerx
            dy = self.float_y - enemy.rect.centery
            dist = math.hypot(dx, dy)
            if dist < self.pull_radius and dist > 10:
                # 吸扯
                pull_x = (dx / dist) * self.pull_strength
                pull_y = (dy / dist) * self.pull_strength
                enemy.rect.x += int(pull_x)
                enemy.rect.y += int(pull_y)
    
    def _fire_shark(self):
        """发射小鲨追踪弹"""
        # 找最近敌人
        target = None
        min_dist = float('inf')
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.float_x, 
                            enemy.rect.centery - self.float_y)
            if dist < 300 and dist < min_dist:
                min_dist = dist
                target = enemy
        
        if target:
            angle = math.atan2(target.rect.centery - self.float_y,
                             target.rect.centerx - self.float_x)
        else:
            angle = -math.pi / 2 + random.uniform(-0.5, 0.5)
        
        damage = self.owner.damage * 0.35 if self.owner else 10
        shark = MiniSharkBullet(self.float_x, self.float_y - 30, damage, self.owner, self.style, angle)
        all_sprites.add(shark)
    
    def activate_explosion(self):
        """激活爆炸（玩家再次普攻触发）"""
        if self.exploded:
            return
        self.exploded = True
        self.active = False
        
        # 爆炸真伤
        damage = self.owner.damage * 1.5 if self.owner else 40
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.float_x,
                            enemy.rect.centery - self.float_y)
            if dist < self.pull_radius * 1.2:
                enemy.take_damage(damage, true_damage=True)
        
        # 掉落深渊泡
        bubble = AbyssBubblePickup(self.float_x, self.float_y, self.owner)
        all_sprites.add(bubble)
        
        # 爆炸特效
        effect = TornadoExplosion(self.float_x, self.float_y, self.style)
        all_sprites.add(effect)
        
        # 从owner移除
        if self.owner and hasattr(self.owner, 'active_tornados'):
            if self in self.owner.active_tornados:
                self.owner.active_tornados.remove(self)
        
        self.kill()
    
    def _fade_out(self):
        """自然消失"""
        if self.owner and hasattr(self.owner, 'active_tornados'):
            if self in self.owner.active_tornados:
                self.owner.active_tornados.remove(self)
        self.kill()
    
    def _update_particles(self):
        """水花粒子"""
        if self.frame % 3 == 0:
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(20, 50)
            self.particles.append({
                'x': math.cos(angle) * dist,
                'y': math.sin(angle) * dist * 0.5 + 30,
                'vy': random.uniform(-3, -1),
                'life': random.randint(15, 25),
                'size': random.uniform(2, 5)
            })
        
        for p in self.particles[:]:
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = DUKE_BULLET_THEMES.get(self.style, DUKE_BULLET_THEMES["default"])
        tornado_color = theme["tornado"]
        foam = theme["foam"]
        pink = theme["pink"]
        water = theme["water"]
        
        cx, cy = 50, 70
        style = self.style
        
        # ========== 根据涂装渲染不同龙卷形状 ==========
        
        if style == "abyss":
            # 深渊漩涡 - 暗紫扭曲空间
            for layer in range(5):
                layer_y = cy + layer * 15 - 30
                layer_w = 18 + layer * 7
                twist = math.sin(self.rotation * 2 + layer) * layer_w * 0.4
                alpha = 160 - layer * 25
                pygame.draw.ellipse(self.image, (*tornado_color, alpha),
                                  (cx - layer_w // 2 + int(twist), layer_y - 10, layer_w, 20))
            # 虚空裂缝
            for i in range(4):
                rift_angle = self.rotation + i * math.pi / 2
                rx = cx + math.cos(rift_angle) * 25
                ry = cy - 20 + math.sin(rift_angle) * 15
                pygame.draw.line(self.image, (*pink, 150), (cx, cy - 20), (int(rx), int(ry)), 2)
            pygame.draw.circle(self.image, (20, 10, 50), (cx, cy - 20), 10)
        
        elif style == "rage":
            # 狂暴血龙卷 - 血红锯齿旋转
            for layer in range(5):
                layer_y = cy + layer * 15 - 30
                layer_w = 20 + layer * 8
                rot = self.rotation * 1.5 + layer * 0.4
                alpha = 180 - layer * 25
                # 锯齿边缘
                for tooth in range(6):
                    t_angle = rot + tooth * math.pi / 3
                    tx = cx + math.cos(t_angle) * (layer_w // 2 + 5)
                    ty = layer_y + math.sin(t_angle) * 8
                    pygame.draw.circle(self.image, (*tornado_color, alpha), (int(tx), int(ty)), 4)
                pygame.draw.ellipse(self.image, (*tornado_color, alpha - 30),
                                  (cx - layer_w // 2, layer_y - 10, layer_w, 20))
            # 血雾核心
            pygame.draw.circle(self.image, pink, (cx, cy - 20), 15)
            pygame.draw.circle(self.image, foam, (cx, cy - 20), 8)
        
        elif style == "storm":
            # 雷暴龙卷 - 电弧闪烁
            for layer in range(5):
                layer_y = cy + layer * 15 - 30
                layer_w = 15 + layer * 9
                flash = abs(math.sin(self.rotation * 3 + layer * 0.5))
                alpha = int((150 + flash * 50) - layer * 20)
                pygame.draw.ellipse(self.image, (*tornado_color, alpha),
                                  (cx - layer_w // 2, layer_y - 10, layer_w, 20))
            # 闪电弧
            for i in range(6):
                arc_start = self.rotation * 2 + i * math.pi / 3
                x1 = cx + math.cos(arc_start) * 20
                y1 = cy - 30 + math.sin(arc_start) * 10
                x2 = cx + math.cos(arc_start + 0.8) * 35
                y2 = cy + 10 + math.sin(arc_start + 0.8) * 15
                pygame.draw.line(self.image, foam, (int(x1), int(y1)), (int(x2), int(y2)), 2)
            # 电核
            pygame.draw.circle(self.image, (200, 230, 255), (cx, cy - 20), 12)
        
        elif style == "coral":
            # 珊瑚涡流 - 柔和螺旋+小鱼
            for layer in range(5):
                layer_y = cy + layer * 14 - 28
                layer_w = 14 + layer * 7
                wave = math.sin(self.rotation + layer * 0.5) * 8
                alpha = 160 - layer * 22
                pygame.draw.ellipse(self.image, (*tornado_color, alpha),
                                  (cx - layer_w // 2 + int(wave), layer_y - 9, layer_w, 18))
            # 珊瑚纹理
            for i in range(5):
                cx_off = (i - 2) * 8
                cy_off = math.sin(self.rotation + i) * 10
                pygame.draw.circle(self.image, (*pink, 120), (cx + cx_off, int(cy - 15 + cy_off)), 4)
            # 小鱼环绕
            for i in range(3):
                f_angle = self.rotation * 0.8 + i * math.pi * 2 / 3
                fx = cx + math.cos(f_angle) * 35
                fy = cy - 20 + math.sin(f_angle) * 20
                pygame.draw.circle(self.image, water, (int(fx), int(fy)), 4)
        
        elif style == "void_sea":
            # 虚空深渊 - 黑洞吞噬
            # 黑洞事件视界
            for ring in range(4):
                r = 35 - ring * 8
                alpha = 60 + ring * 20
                pygame.draw.circle(self.image, (*tornado_color, alpha), (cx, cy - 15), r, 2)
            # 吞噬螺旋
            for arm in range(3):
                for seg in range(5):
                    arm_angle = self.rotation + arm * math.pi * 2 / 3 + seg * 0.3
                    arm_r = 10 + seg * 6
                    ax = cx + math.cos(arm_angle) * arm_r
                    ay = cy - 15 + math.sin(arm_angle) * arm_r * 0.5
                    size = 4 - seg // 2
                    pygame.draw.circle(self.image, (*pink, 150 - seg * 25), (int(ax), int(ay)), size)
            # 虚空核心
            pygame.draw.circle(self.image, (5, 0, 20), (cx, cy - 15), 12)
        
        elif style == "tsunami":
            # 海啸巨涡 - 巨浪翻涌
            for layer in range(5):
                layer_y = cy + layer * 16 - 32
                layer_w = 18 + layer * 10
                wave_h = 12 + int(math.sin(self.rotation * 2 + layer) * 4)
                alpha = 170 - layer * 25
                pygame.draw.ellipse(self.image, (*tornado_color, alpha),
                                  (cx - layer_w // 2, layer_y - wave_h // 2, layer_w, wave_h))
            # 浪花飞溅
            for i in range(8):
                splash_angle = self.rotation * 1.5 + i * math.pi / 4
                splash_r = 30 + math.sin(self.rotation * 2 + i) * 10
                sx = cx + math.cos(splash_angle) * splash_r
                sy = cy - 20 + math.sin(splash_angle) * splash_r * 0.4
                pygame.draw.circle(self.image, foam, (int(sx), int(sy)), 3)
            pygame.draw.circle(self.image, foam, (cx, cy - 25), 10)
        
        elif style == "phantom":
            # 幽灵涡旋 - 透明飘渺
            ghost_alpha = int(80 + 40 * math.sin(self.rotation))
            for layer in range(5):
                layer_y = cy + layer * 15 - 30
                layer_w = 16 + layer * 8
                drift = math.sin(self.rotation + layer * 0.6) * 10
                alpha = int((140 - layer * 22) * ghost_alpha / 120)
                pygame.draw.ellipse(self.image, (*tornado_color, alpha),
                                  (cx - layer_w // 2 + int(drift), layer_y - 10, layer_w, 20))
            # 灵魂飘散
            for i in range(5):
                soul_y = cy - 40 + i * 12
                soul_alpha = ghost_alpha - i * 15
                if soul_alpha > 0:
                    pygame.draw.circle(self.image, (*foam, soul_alpha), (cx, int(soul_y)), 5 - i // 2)
        
        elif style == "blood_moon":
            # 血月漩涡 - 血色深渊
            for layer in range(5):
                layer_y = cy + layer * 15 - 30
                layer_w = 17 + layer * 8
                pulse = math.sin(self.rotation * 1.5 + layer) * 3
                alpha = 170 - layer * 25
                pygame.draw.ellipse(self.image, (*tornado_color, alpha),
                                  (cx - layer_w // 2 + int(pulse), layer_y - 11, layer_w, 22))
            # 血滴飞溅
            for i in range(6):
                drip_angle = self.rotation + i * math.pi / 3
                drip_r = 25 + i * 3
                dx = cx + math.cos(drip_angle) * drip_r
                dy = cy - 10 + abs(math.sin(drip_angle)) * 15
                pygame.draw.circle(self.image, pink, (int(dx), int(dy)), 3)
            pygame.draw.circle(self.image, (80, 0, 20), (cx, cy - 18), 12)
            pygame.draw.circle(self.image, pink, (cx, cy - 18), 6)
        
        elif style == "tropical":
            # 热带风暴 - 彩虹旋转
            rainbow = [(255,100,100), (255,180,80), (255,255,100), 
                       (100,255,150), (100,200,255), (180,120,255)]
            for layer in range(5):
                layer_y = cy + layer * 14 - 28
                layer_w = 16 + layer * 8
                color_idx = (layer + int(self.rotation * 2)) % 6
                wave = math.sin(self.rotation + layer * 0.4) * 6
                pygame.draw.ellipse(self.image, (*rainbow[color_idx], 160),
                                  (cx - layer_w // 2 + int(wave), layer_y - 9, layer_w, 18))
            # 热带花瓣
            for i in range(5):
                petal_angle = self.rotation * 0.7 + i * math.pi * 2 / 5
                px = cx + math.cos(petal_angle) * 28
                py = cy - 18 + math.sin(petal_angle) * 15
                pygame.draw.circle(self.image, pink, (int(px), int(py)), 5)
            pygame.draw.circle(self.image, (255, 220, 100), (cx, cy - 18), 10)
        
        elif style == "frost":
            # 寒霜风暴 - 冰晶旋转
            for layer in range(5):
                layer_y = cy + layer * 15 - 30
                layer_w = 15 + layer * 8
                alpha = 150 - layer * 20
                pygame.draw.ellipse(self.image, (*tornado_color, alpha),
                                  (cx - layer_w // 2, layer_y - 10, layer_w, 20))
            # 冰晶碎片
            for i in range(6):
                ice_angle = self.rotation + i * math.pi / 3
                ice_r = 30
                ix = cx + math.cos(ice_angle) * ice_r
                iy = cy - 15 + math.sin(ice_angle) * ice_r * 0.5
                # 六边形冰晶
                for j in range(6):
                    ja = j * math.pi / 3
                    pygame.draw.line(self.image, foam, (int(ix), int(iy)),
                                   (int(ix + math.cos(ja) * 5), int(iy + math.sin(ja) * 5)), 1)
            pygame.draw.circle(self.image, (200, 240, 255), (cx, cy - 18), 10)
        
        elif style == "golden":
            # 黄金风暴 - 金焰旋涡
            for layer in range(5):
                layer_y = cy + layer * 15 - 30
                layer_w = 18 + layer * 9
                flame = abs(math.sin(self.rotation * 2 + layer * 0.5)) * 0.3 + 0.7
                alpha = int((180 - layer * 25) * flame)
                pygame.draw.ellipse(self.image, (*tornado_color, alpha),
                                  (cx - layer_w // 2, layer_y - 11, layer_w, 22))
            # 金焰尾迹
            for i in range(5):
                flame_angle = self.rotation * 1.2 + i * math.pi * 2 / 5
                flame_r = 28 + math.sin(self.rotation * 3 + i) * 5
                fx = cx + math.cos(flame_angle) * flame_r
                fy = cy - 15 + math.sin(flame_angle) * flame_r * 0.4
                pygame.draw.circle(self.image, foam, (int(fx), int(fy)), 4)
            # 皇冠核心
            pygame.draw.circle(self.image, water, (cx, cy - 18), 14)
            pygame.draw.circle(self.image, foam, (cx, cy - 18), 8)
        
        else:
            # 默认龙卷
            for layer in range(5):
                layer_y = cy + layer * 15 - 30
                layer_w = 15 + layer * 8
                layer_h = 20
                rot_offset = self.rotation + layer * 0.3
                wave = math.sin(rot_offset) * layer_w * 0.3
                alpha = 180 - layer * 25
                pygame.draw.ellipse(self.image, (*tornado_color, alpha),
                                  (cx - layer_w // 2 + int(wave), layer_y - layer_h // 2,
                                   layer_w, layer_h))
            for i in range(3):
                r = 12 - i * 3
                alpha = 200 - i * 40
                pygame.draw.circle(self.image, (*foam, alpha), (cx, cy - 20), r)
        
        # 水花粒子（所有涂装通用）
        for p in self.particles:
            px = cx + p['x']
            py = cy + p['y'] - 40
            if 0 <= px < 100 and 0 <= py < 140:
                p_alpha = int(200 * p['life'] / 25)
                pygame.draw.circle(self.image, (*foam, p_alpha), 
                                 (int(px), int(py)), int(p['size']))


# ==================== 小鲨追踪弹 ====================
class MiniSharkBullet(pygame.sprite.Sprite):
    """小鲨追踪弹 - 龙卷发射的追踪子弹"""
    
    def __init__(self, x, y, damage, owner=None, style="default", angle=-math.pi/2):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.piercing = 1
        self.style = style
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.angle = angle
        self.speed = 10
        self.turn_rate = 0.06
        
        self.frame = 0
        self.lifetime = 120  # 2秒
        
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0 or self.float_y < -20 or self.float_y > HEIGHT + 20:
            self.kill()
            return
        
        # 追踪最近敌人
        target = self._find_target()
        if target:
            tx, ty = target.rect.center
            target_angle = math.atan2(ty - self.float_y, tx - self.float_x)
            angle_diff = target_angle - self.angle
            while angle_diff > math.pi: angle_diff -= math.pi * 2
            while angle_diff < -math.pi: angle_diff += math.pi * 2
            self.angle += max(-self.turn_rate, min(self.turn_rate, angle_diff))
        
        # 移动
        self.float_x += math.cos(self.angle) * self.speed
        self.float_y += math.sin(self.angle) * self.speed
        
        # 命中检测
        for mob in mobs:
            if self.rect.colliderect(mob.rect):
                mob.take_damage(self.damage)
                self._spawn_hit_effect()
                self.kill()
                return
        
        self._render()
        self.rect.center = (int(self.float_x), int(self.float_y))
    
    def _find_target(self):
        min_dist = 200
        target = None
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.float_x,
                            enemy.rect.centery - self.float_y)
            if dist < min_dist:
                min_dist = dist
                target = enemy
        return target
    
    def _spawn_hit_effect(self):
        effect = SharkHitEffect(self.float_x, self.float_y, self.style)
        all_sprites.add(effect)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = DUKE_BULLET_THEMES.get(self.style, DUKE_BULLET_THEMES["default"])
        shark_color = theme["shark"]
        pink = theme["pink"]
        foam = theme["foam"]
        water = theme["water"]
        
        cx, cy = 8, 8
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        style = self.style
        
        # ========== 根据涂装渲染不同小鲨形状 ==========
        
        if style == "abyss":
            # 深渊幽灵鲨 - 暗紫扭曲
            pygame.draw.circle(self.image, (*shark_color, 180), (cx, cy), 6)
            pygame.draw.circle(self.image, (*pink, 150), (cx, cy), 4)
            # 虚空尾迹
            for i in range(3):
                tx = cx - cos_a * (5 + i * 3)
                ty = cy - sin_a * (5 + i * 3)
                pygame.draw.circle(self.image, (*shark_color, 100 - i * 30), (int(tx), int(ty)), 3 - i)
            # 暗紫眼
            eye_x = cx + cos_a * 3
            eye_y = cy + sin_a * 3
            pygame.draw.circle(self.image, (180, 80, 200), (int(eye_x), int(eye_y)), 2)
        
        elif style == "rage":
            # 狂暴血鲨 - 血红锯齿
            pygame.draw.circle(self.image, shark_color, (cx, cy), 6)
            # 锯齿鳍
            for i in range(3):
                fin_angle = self.angle + math.pi/2 + (i - 1) * 0.4
                fx = cx + math.cos(fin_angle) * 5
                fy = cy + math.sin(fin_angle) * 5
                pygame.draw.circle(self.image, pink, (int(fx), int(fy)), 2)
            # 血色核心
            pygame.draw.circle(self.image, pink, (cx, cy), 3)
            # 怒目
            eye_x = cx + cos_a * 3
            eye_y = cy + sin_a * 3
            pygame.draw.circle(self.image, (255, 50, 50), (int(eye_x), int(eye_y)), 2)
        
        elif style == "storm":
            # 闪电鲨 - 电光环绕
            flash = abs(math.sin(self.frame * 0.5))
            pygame.draw.circle(self.image, shark_color, (cx, cy), 5)
            pygame.draw.circle(self.image, (*foam, int(150 + flash * 100)), (cx, cy), 7, 1)
            # 电弧
            arc_x = cx + math.cos(self.frame * 0.6) * 6
            arc_y = cy + math.sin(self.frame * 0.6) * 6
            pygame.draw.line(self.image, foam, (cx, cy), (int(arc_x), int(arc_y)), 1)
            # 电眼
            eye_x = cx + cos_a * 3
            eye_y = cy + sin_a * 3
            pygame.draw.circle(self.image, (200, 230, 255), (int(eye_x), int(eye_y)), 2)
        
        elif style == "coral":
            # 珊瑚小鱼 - 可爱圆润
            pygame.draw.circle(self.image, shark_color, (cx, cy), 5)
            pygame.draw.circle(self.image, pink, (cx, cy), 4)
            # 小鳍
            fin_x = cx - cos_a * 4
            fin_y = cy - sin_a * 4 - 3
            pygame.draw.circle(self.image, shark_color, (int(fin_x), int(fin_y)), 2)
            # 可爱大眼
            eye_x = cx + cos_a * 2
            eye_y = cy + sin_a * 2
            pygame.draw.circle(self.image, (255, 255, 255), (int(eye_x), int(eye_y)), 3)
            pygame.draw.circle(self.image, (0, 0, 0), (int(eye_x), int(eye_y)), 1)
        
        elif style == "void_sea":
            # 虚空吞噬者 - 黑洞核心
            pygame.draw.circle(self.image, (10, 5, 30), (cx, cy), 6)
            pygame.draw.circle(self.image, (*shark_color, 150), (cx, cy), 6, 1)
            pygame.draw.circle(self.image, (*pink, 100), (cx, cy), 4, 1)
            # 无眼
            pygame.draw.circle(self.image, (40, 20, 80), (cx, cy), 2)
        
        elif style == "tsunami":
            # 海啸浪鲨 - 水波环绕
            pygame.draw.circle(self.image, shark_color, (cx, cy), 5)
            pygame.draw.circle(self.image, foam, (cx, cy), 3)
            # 水波尾迹
            for i in range(2):
                wave_offset = math.sin(self.frame * 0.4 + i) * 2
                tx = cx - cos_a * (5 + i * 3) + wave_offset
                ty = cy - sin_a * (5 + i * 3)
                pygame.draw.circle(self.image, (*foam, 150 - i * 50), (int(tx), int(ty)), 3)
            # 蓝眼
            eye_x = cx + cos_a * 2
            eye_y = cy + sin_a * 2
            pygame.draw.circle(self.image, (100, 200, 255), (int(eye_x), int(eye_y)), 2)
        
        elif style == "phantom":
            # 幽灵鲨 - 半透明飘渺
            ghost_alpha = int(120 + 60 * math.sin(self.frame * 0.3))
            pygame.draw.circle(self.image, (*shark_color, ghost_alpha), (cx, cy), 6)
            pygame.draw.circle(self.image, (*foam, ghost_alpha - 30), (cx, cy), 4)
            # 幽灵尾迹
            for i in range(3):
                tx = cx - cos_a * (4 + i * 2)
                ty = cy - sin_a * (4 + i * 2)
                pygame.draw.circle(self.image, (*foam, ghost_alpha - 40 - i * 25), (int(tx), int(ty)), 2)
            # 幽光眼
            eye_x = cx + cos_a * 2
            eye_y = cy + sin_a * 2
            pygame.draw.circle(self.image, (*foam, ghost_alpha), (int(eye_x), int(eye_y)), 2)
        
        elif style == "blood_moon":
            # 血月獠牙鲨 - 血红眼
            pygame.draw.circle(self.image, shark_color, (cx, cy), 5)
            # 獠牙
            fang1_x = cx + cos_a * 5 + math.cos(self.angle + 0.5) * 2
            fang1_y = cy + sin_a * 5 + math.sin(self.angle + 0.5) * 2
            fang2_x = cx + cos_a * 5 + math.cos(self.angle - 0.5) * 2
            fang2_y = cy + sin_a * 5 + math.sin(self.angle - 0.5) * 2
            pygame.draw.circle(self.image, pink, (int(fang1_x), int(fang1_y)), 2)
            pygame.draw.circle(self.image, pink, (int(fang2_x), int(fang2_y)), 2)
            # 血色核心
            pygame.draw.circle(self.image, pink, (cx, cy), 3)
            # 血眼
            eye_x = cx + cos_a * 2
            eye_y = cy + sin_a * 2
            pygame.draw.circle(self.image, (255, 50, 50), (int(eye_x), int(eye_y)), 2)
            pygame.draw.circle(self.image, (180, 0, 0), (int(eye_x), int(eye_y)), 1)
        
        elif style == "tropical":
            # 热带彩鱼 - 彩虹色
            rainbow = [(255,100,100), (255,180,80), (255,255,100)]
            color_idx = (self.frame // 5) % 3
            pygame.draw.circle(self.image, rainbow[color_idx], (cx, cy), 5)
            pygame.draw.circle(self.image, pink, (cx, cy), 3)
            # 彩色尾鳍
            tail_x = cx - cos_a * 5
            tail_y = cy - sin_a * 5
            pygame.draw.circle(self.image, rainbow[(color_idx + 1) % 3], (int(tail_x), int(tail_y)), 3)
            # 闪亮眼
            eye_x = cx + cos_a * 2
            eye_y = cy + sin_a * 2
            pygame.draw.circle(self.image, (255, 255, 200), (int(eye_x), int(eye_y)), 2)
        
        elif style == "frost":
            # 冰霜鲨 - 冰晶形态
            pygame.draw.circle(self.image, shark_color, (cx, cy), 5)
            pygame.draw.circle(self.image, foam, (cx, cy), 5, 1)
            # 冰晶尖刺
            for i in range(4):
                spike_angle = self.angle + i * math.pi / 2
                sx = cx + math.cos(spike_angle) * 6
                sy = cy + math.sin(spike_angle) * 6
                pygame.draw.line(self.image, foam, (cx, cy), (int(sx), int(sy)), 1)
            # 冰核
            pygame.draw.circle(self.image, (200, 240, 255), (cx, cy), 2)
            # 冰眼
            eye_x = cx + cos_a * 2
            eye_y = cy + sin_a * 2
            pygame.draw.circle(self.image, (180, 220, 255), (int(eye_x), int(eye_y)), 2)
        
        elif style == "golden":
            # 黄金鲨 - 金光闪闪
            flash = abs(math.sin(self.frame * 0.4)) * 0.3 + 0.7
            pygame.draw.circle(self.image, shark_color, (cx, cy), 5)
            pygame.draw.circle(self.image, (*foam, int(200 * flash)), (cx, cy), 6, 1)
            # 金冠
            crown_y = cy - 4
            pygame.draw.polygon(self.image, foam, [
                (cx - 3, crown_y), (cx - 1, crown_y - 3),
                (cx + 1, crown_y - 3), (cx + 3, crown_y)
            ])
            # 金眼
            pygame.draw.circle(self.image, pink, (cx, cy), 3)
            eye_x = cx + cos_a * 2
            eye_y = cy + sin_a * 2
            pygame.draw.circle(self.image, (255, 220, 100), (int(eye_x), int(eye_y)), 2)
        
        else:
            # 默认小鲨
            pygame.draw.circle(self.image, shark_color, (cx, cy), 5)
            pygame.draw.circle(self.image, pink, (cx, cy), 3)
            # 尾鳍
            tail_x = cx - cos_a * 6
            tail_y = cy - sin_a * 6
            pygame.draw.circle(self.image, shark_color, (int(tail_x), int(tail_y)), 3)
            # 眼睛
            eye_x = cx + cos_a * 3
            eye_y = cy + sin_a * 3
            pygame.draw.circle(self.image, (255, 255, 255), (int(eye_x), int(eye_y)), 2)
            pygame.draw.circle(self.image, (0, 0, 0), (int(eye_x), int(eye_y)), 1)


# ==================== 深渊泡拾取物 ====================
class AbyssBubblePickup(pygame.sprite.Sprite):
    """深渊泡 - 拾取回复15能量，下次普攻折射"""
    
    def __init__(self, x, y, owner=None):
        super().__init__()
        self.owner = owner
        self.float_x = float(x)
        self.float_y = float(y)
        self.energy_value = 15
        
        self.frame = 0
        self.lifetime = 300  # 5秒
        
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 漂浮动画
        self.float_y += math.sin(self.frame * 0.1) * 0.3
        
        # 检测玩家拾取
        if self.owner and self.rect.colliderect(self.owner.rect):
            self._pickup()
            return
        
        self._render()
        self.rect.center = (int(self.float_x), int(self.float_y))
    
    def _pickup(self):
        """被拾取"""
        if self.owner:
            # 回复能量
            if hasattr(self.owner, 'energy'):
                self.owner.energy = min(getattr(self.owner, 'max_energy', 100),
                                       self.owner.energy + self.energy_value)
            # 标记下次普攻折射
            self.owner.duke_refract_ready = True
        
        # 拾取特效
        effect = BubblePickupEffect(self.float_x, self.float_y)
        all_sprites.add(effect)
        
        self.kill()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 15, 15
        
        # 闪烁
        flash = abs(math.sin(self.frame * 0.15))
        
        # 气泡外层
        r = 12 + int(flash * 3)
        pygame.draw.circle(self.image, (100, 180, 255, 150), (cx, cy), r)
        pygame.draw.circle(self.image, (180, 220, 255, 200), (cx, cy), r, 2)
        
        # 高光
        pygame.draw.circle(self.image, (255, 255, 255, 200), (cx - 4, cy - 4), 3)
        
        # 快消失时闪烁
        if self.lifetime < 60 and self.frame % 10 < 5:
            pygame.draw.circle(self.image, (255, 255, 100, 150), (cx, cy), r + 2, 2)


# ==================== 命中特效 ====================
class SpearHitEffect(pygame.sprite.Sprite):
    """水矛命中特效"""
    def __init__(self, x, y, style="default"):
        super().__init__()
        self.float_x, self.float_y = x, y
        self.frame = 0
        self.lifetime = 25
        self.style = style
        
        self.splashes = []
        for i in range(6):
            angle = i * math.pi / 3 + random.uniform(-0.2, 0.2)
            speed = random.uniform(3, 6)
            self.splashes.append({
                'angle': angle, 'speed': speed, 'dist': 0,
                'size': random.uniform(3, 6)
            })
        
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        
        for s in self.splashes:
            s['dist'] += s['speed'] * (1 - self.frame / self.lifetime)
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = DUKE_BULLET_THEMES.get(self.style, DUKE_BULLET_THEMES["default"])
        cx, cy = 40, 40
        progress = self.frame / self.lifetime
        alpha = int(255 * (1 - progress))
        
        # 水花扩散
        for wave in range(3):
            wave_r = int(progress * 35 + wave * 5)
            wave_alpha = int(150 * (1 - progress) * (1 - wave * 0.25))
            if wave_r > 0 and wave_alpha > 0:
                pygame.draw.circle(self.image, (*theme["water"], wave_alpha), 
                                 (cx, cy), wave_r, 2)
        
        # 水滴飞溅
        for s in self.splashes:
            sx = cx + math.cos(s['angle']) * s['dist']
            sy = cy + math.sin(s['angle']) * s['dist']
            s_alpha = int(alpha * (1 - s['dist'] / 40))
            if s_alpha > 0 and 0 <= sx < 80 and 0 <= sy < 80:
                size = int(s['size'] * (1 - progress * 0.5))
                if size > 0:
                    pygame.draw.circle(self.image, (*theme["foam"], s_alpha),
                                     (int(sx), int(sy)), size)


class SharkHitEffect(pygame.sprite.Sprite):
    """小鲨命中特效"""
    def __init__(self, x, y, style="default"):
        super().__init__()
        self.float_x, self.float_y = x, y
        self.frame = 0
        self.lifetime = 20
        self.style = style
        
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = DUKE_BULLET_THEMES.get(self.style, DUKE_BULLET_THEMES["default"])
        cx, cy = 25, 25
        progress = self.frame / self.lifetime
        alpha = int(200 * (1 - progress))
        
        # 咬痕效果
        r = int(15 * (1 - progress * 0.5))
        pygame.draw.circle(self.image, (*theme["pink"], alpha), (cx, cy), r)
        pygame.draw.circle(self.image, (*theme["shark"], alpha // 2), (cx, cy), r, 2)


class TornadoExplosion(pygame.sprite.Sprite):
    """龙卷爆炸特效"""
    def __init__(self, x, y, style="default"):
        super().__init__()
        self.float_x, self.float_y = x, y
        self.frame = 0
        self.lifetime = 35
        self.style = style
        
        self.shards = []
        for i in range(8):
            angle = i * math.pi / 4 + random.uniform(-0.2, 0.2)
            speed = random.uniform(5, 10)
            self.shards.append({
                'angle': angle, 'speed': speed, 'dist': 0,
                'rot': random.uniform(0, math.pi * 2)
            })
        
        self.image = pygame.Surface((160, 160), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        
        for s in self.shards:
            s['dist'] += s['speed'] * (1 - self.frame / self.lifetime)
            s['rot'] += 0.2
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = DUKE_BULLET_THEMES.get(self.style, DUKE_BULLET_THEMES["default"])
        cx, cy = 80, 80
        progress = self.frame / self.lifetime
        alpha = int(255 * (1 - progress))
        
        # 爆炸冲击波
        for wave in range(4):
            wave_r = int(progress * 70 + wave * 8)
            wave_alpha = int(180 * (1 - progress) * (1 - wave * 0.2))
            if wave_r > 0 and wave_alpha > 0:
                pygame.draw.circle(self.image, (*theme["tornado"], wave_alpha),
                                 (cx, cy), wave_r, 3)
        
        # 水旋碎片
        for s in self.shards:
            sx = cx + math.cos(s['angle']) * s['dist']
            sy = cy + math.sin(s['angle']) * s['dist']
            if 0 <= sx < 160 and 0 <= sy < 160:
                # 旋转的水滴形
                size = 8 * (1 - progress * 0.5)
                pygame.draw.circle(self.image, (*theme["foam"], alpha // 2),
                                 (int(sx), int(sy)), int(size))


class BubblePickupEffect(pygame.sprite.Sprite):
    """气泡拾取特效"""
    def __init__(self, x, y):
        super().__init__()
        self.float_x, self.float_y = x, y
        self.frame = 0
        self.lifetime = 20
        
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 30, 30
        progress = self.frame / self.lifetime
        
        # 气泡破裂
        for i in range(6):
            angle = i * math.pi / 3 + progress * 2
            dist = progress * 25
            px = cx + math.cos(angle) * dist
            py = cy + math.sin(angle) * dist
            alpha = int(200 * (1 - progress))
            size = int(4 * (1 - progress))
            if size > 0:
                pygame.draw.circle(self.image, (150, 220, 255, alpha),
                                 (int(px), int(py)), size)


# ==================== 海浪幕（DOT区域）====================
class WaveTrail(pygame.sprite.Sprite):
    """海浪幕 - 俯冲路径留下的DOT区域"""
    
    def __init__(self, x, y, owner=None, style="default"):
        super().__init__()
        self.owner = owner
        self.style = style
        self.float_x = float(x)
        self.float_y = float(y)
        
        self.lifetime = 120  # 2秒
        self.frame = 0
        self.damage_timer = 0
        self.damage_interval = 15  # 0.25秒
        self.dot_damage = owner.damage * 0.15 if owner else 5
        
        self.width = 60
        self.height = 30
        
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        # DOT伤害
        self.damage_timer += 1
        if self.damage_timer >= self.damage_interval:
            self.damage_timer = 0
            for enemy in mobs:
                if self.rect.colliderect(enemy.rect):
                    enemy.take_damage(self.dot_damage)
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = DUKE_BULLET_THEMES.get(self.style, DUKE_BULLET_THEMES["default"])
        
        progress = 1 - self.lifetime / 120
        alpha = int(150 * (1 - progress))
        
        # 波浪效果
        wave = math.sin(self.frame * 0.2) * 3
        pygame.draw.ellipse(self.image, (*theme["water"], alpha),
                          (0, int(wave), self.width, self.height - 5))
        pygame.draw.ellipse(self.image, (*theme["foam"], alpha // 2),
                          (5, 5 + int(wave), self.width - 10, self.height - 15), 2)


# ==================== F技能：鲨龙卷暴雨 ====================
class SharkTornadoStorm(pygame.sprite.Sprite):
    """鲨龙卷暴雨 - F技能：连续生成强化鲨龙卷（性能优化版）"""
    
    def __init__(self, owner=None, style="default"):
        super().__init__()
        self.owner = owner
        self.style = style
        self.damage = owner.damage * 1.5 if owner else 30
        
        self.frame = 0
        self.duration = 120  # 2秒
        
        self.tornado_count = 5  # 减少数量提升性能
        self.tornado_timer = 0
        self.tornado_interval = 20
        self.spawned = 0
        
        # 简化粒子系统
        self.lightning_timer = 0
        self.current_lightning = None  # 只保留一道闪电
        
        # 预计算云层（不再每帧更新）
        self.cloud_phase = random.uniform(0, math.pi * 2)
        
        # 使用较小的Surface减少内存
        self.image = pygame.Surface((WIDTH, 200), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
    
    def update(self):
        self.frame += 1
        self.duration -= 1
        
        if self.duration <= 0:
            self.kill()
            return
        
        # 生成龙卷
        self.tornado_timer += 1
        if self.tornado_timer >= self.tornado_interval and self.spawned < self.tornado_count:
            self.tornado_timer = 0
            self.spawned += 1
            self._spawn_tornado()
        
        # 简化闪电：固定间隔生成
        self.lightning_timer += 1
        if self.lightning_timer >= 12:
            self.lightning_timer = 0
            self._spawn_lightning()
        
        # 更新闪电
        if self.current_lightning:
            self.current_lightning['life'] -= 1
            if self.current_lightning['life'] <= 0:
                self.current_lightning = None
        
        self._render()
    
    def _spawn_tornado(self):
        """生成强化龙卷"""
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT // 2)
        
        tornado = SharkTornado(x, y, self.owner, self.style)
        tornado.lifetime = 180
        tornado.pull_radius = 150
        all_sprites.add(tornado)
    
    def _spawn_lightning(self):
        """生成单道大闪电"""
        x = random.randint(80, WIDTH - 80)
        segments = []
        y = 0
        curr_x = x
        for _ in range(8):
            next_y = y + random.randint(50, 100)
            segments.append((curr_x, y, curr_x + random.randint(-40, 40), next_y))
            y = next_y
            curr_x = segments[-1][2]
        
        self.current_lightning = {'segments': segments, 'life': 10, 'x': x}
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = DUKE_BULLET_THEMES.get(self.style, DUKE_BULLET_THEMES["default"])
        water = theme["water"]
        foam = theme["foam"]
        tornado_c = theme["tornado"]
        pink = theme["pink"]
        
        progress = self.frame / 120
        
        # ===== 1. 顶部风暴云带（醒目） =====
        wave = math.sin(self.frame * 0.08 + self.cloud_phase) * 15
        
        # 主云层 - 更大更亮
        for i in range(3):
            cloud_alpha = 180 - i * 40
            y_off = i * 25 + int(wave)
            pygame.draw.ellipse(self.image, (*tornado_c, cloud_alpha),
                              (-50, y_off - 20, WIDTH + 100, 100 - i * 15))
        
        # 云层边缘高光
        pygame.draw.ellipse(self.image, (*foam, 120),
                          (-30, int(wave) + 5, WIDTH + 60, 50), 3)
        
        # ===== 2. 大闪电（醒目） =====
        if self.current_lightning:
            bolt = self.current_lightning
            alpha = min(255, int(255 * bolt['life'] / 6))
            
            for seg in bolt['segments']:
                x1, y1, x2, y2 = seg
                # 粗光晕
                pygame.draw.line(self.image, (*foam, alpha // 2), (x1, y1), (x2, y2), 12)
                # 中光晕  
                pygame.draw.line(self.image, (*foam, alpha), (x1, y1), (x2, y2), 6)
                # 白芯
                pygame.draw.line(self.image, (255, 255, 255, alpha), (x1, y1), (x2, y2), 2)
            
            # 闪电落点光圈
            last_seg = bolt['segments'][-1]
            pygame.draw.circle(self.image, (*foam, alpha), (last_seg[2], min(last_seg[3], 190)), 25, 4)
        
        # ===== 3. 下落水柱线（简化版雨） =====
        for i in range(8):
            rx = (self.frame * 3 + i * 60) % WIDTH
            ry_start = 80 + (i * 7) % 30
            ry_end = min(195, ry_start + 60 + i * 10)
            alpha = 150 - i * 10
            pygame.draw.line(self.image, (*water, alpha), (rx, ry_start), (rx + 5, ry_end), 3)
        
        # ===== 4. 技能名显示 =====
        if self.frame < 40:
            text_alpha = int(255 * (1 - self.frame / 40))
            # 用圆形模拟文字光晕
            pygame.draw.circle(self.image, (*pink, text_alpha // 2), (WIDTH // 2, 100), 80)


# ==================== G技能：深渊泡风暴 ====================
class AbyssBubbleStorm(pygame.sprite.Sprite):
    """深渊泡风暴 - G技能：巨型气泡领域+追踪鲨群+真伤爆破"""
    
    def __init__(self, x, y, owner=None, style="default"):
        super().__init__()
        self.owner = owner
        self.style = style
        self.float_x = float(x)
        self.float_y = float(y)
        
        self.duration = 180  # 3秒（缩短提升性能）
        self.frame = 0
        self.radius = 160  # 稍小一点
        self.pulse = 0
        
        self.shark_timer = 0
        self.shark_interval = 25
        self.sharks_fired = 0
        
        # 简化气泡系统
        self.bubbles = []
        for _ in range(12):  # 减少数量
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(30, self.radius - 20)
            self.bubbles.append({
                'angle': angle,
                'dist': dist,
                'size': random.uniform(10, 30),  # 更大的气泡
                'speed': random.uniform(0.01, 0.03),
                'wobble': random.uniform(0, math.pi * 2)
            })
        
        # 核心旋转
        self.core_rotation = 0
        
        dim = self.radius * 2 + 60
        self.image = pygame.Surface((dim, dim), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        self.duration -= 1
        self.pulse = math.sin(self.frame * 0.1) * 0.1 + 1.0
        self.core_rotation += 0.08
        
        if self.duration <= 0:
            self._explode()
            self.kill()
            return
        
        # 吸扯+减速区域内敌人
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.float_x,
                            enemy.rect.centery - self.float_y)
            if dist < self.radius:
                if hasattr(enemy, 'speed'):
                    enemy.speed *= 0.7
                if dist > 30:
                    dx = (self.float_x - enemy.rect.centerx) / dist
                    dy = (self.float_y - enemy.rect.centery) / dist
                    enemy.rect.x += int(dx * 2)
                    enemy.rect.y += int(dy * 2)
        
        # 发射追踪鲨
        self.shark_timer += 1
        if self.shark_timer >= self.shark_interval:
            self.shark_timer = 0
            self._fire_shark_swarm()
        
        # 简化更新
        for b in self.bubbles:
            b['angle'] += b['speed']
            b['wobble'] += 0.1
        
        self._render()
        self.rect.center = (int(self.float_x), int(self.float_y))
    
    def _fire_shark_swarm(self):
        """发射小鲨群（3只扇形）"""
        self.sharks_fired += 1
        base_damage = self.owner.damage * 0.35 if self.owner else 12
        
        # 寻找目标
        target = None
        min_dist = 400
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.float_x,
                            enemy.rect.centery - self.float_y)
            if dist < min_dist:
                min_dist = dist
                target = enemy
        
        if target:
            base_angle = math.atan2(target.rect.centery - self.float_y,
                                   target.rect.centerx - self.float_x)
        else:
            base_angle = -math.pi / 2
        
        # 3只扇形发射
        for i in range(3):
            angle = base_angle + (i - 1) * 0.4
            shark = MiniSharkBullet(self.float_x, self.float_y, base_damage, 
                                   self.owner, self.style, angle)
            shark.speed = 12  # 更快
            all_sprites.add(shark)
    
    def _explode(self):
        """结束时巨型爆炸真伤"""
        damage = self.owner.damage * 2.5 if self.owner else 60
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.float_x,
                            enemy.rect.centery - self.float_y)
            if dist < self.radius * 1.3:
                damage_mult = 1.5 - (dist / self.radius) * 0.5
                enemy.take_damage(int(damage * damage_mult), true_damage=True)
        
        effect = BubbleStormExplosion(self.float_x, self.float_y, self.style, self.radius)
        all_sprites.add(effect)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = DUKE_BULLET_THEMES.get(self.style, DUKE_BULLET_THEMES["default"])
        water = theme["water"]
        pink = theme["pink"]
        foam = theme["foam"]
        bubble_c = theme["bubble"]
        
        dim = self.radius * 2 + 60
        cx, cy = dim // 2, dim // 2
        progress = 1 - self.duration / 180
        
        # ===== 1. 大型外圈光环（醒目）=====
        outer_r = int(self.radius * self.pulse)
        # 粗外圈
        pygame.draw.circle(self.image, (*water, 180), (cx, cy), outer_r, 8)
        pygame.draw.circle(self.image, (*foam, 220), (cx, cy), outer_r, 3)
        
        # ===== 2. 旋转漩涡线 =====
        for i in range(4):
            arm_angle = self.core_rotation + i * math.pi / 2
            points = []
            for seg in range(6):
                t = seg / 5
                seg_r = 20 + t * (self.radius - 30)
                seg_angle = arm_angle + t * math.pi * 0.6
                points.append((
                    int(cx + math.cos(seg_angle) * seg_r),
                    int(cy + math.sin(seg_angle) * seg_r)
                ))
            if len(points) > 1:
                pygame.draw.lines(self.image, (*water, 200), False, points, 4)
        
        # ===== 3. 大气泡 =====
        for b in self.bubbles:
            bx = cx + math.cos(b['angle']) * b['dist'] * self.pulse
            by = cy + math.sin(b['angle']) * b['dist'] * self.pulse
            wave = math.sin(b['wobble']) * 3
            b_size = int(b['size'] * self.pulse)
            
            if b_size > 2:
                # 气泡外圈
                pygame.draw.circle(self.image, (*bubble_c, 200), 
                                 (int(bx), int(by + wave)), b_size)
                pygame.draw.circle(self.image, (*foam, 255), 
                                 (int(bx), int(by + wave)), b_size, 2)
                # 高光
                pygame.draw.circle(self.image, (255, 255, 255, 200),
                                 (int(bx - b_size//3), int(by + wave - b_size//3)), 
                                 max(2, b_size // 3))
        
        # ===== 4. 中心核心（大且亮）=====
        core_r = 30 + int(5 * math.sin(self.frame * 0.15))
        # 多层发光
        pygame.draw.circle(self.image, (*pink, 100), (cx, cy), core_r + 20)
        pygame.draw.circle(self.image, (*pink, 180), (cx, cy), core_r)
        pygame.draw.circle(self.image, (*foam, 255), (cx, cy), core_r // 2)
        pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), core_r // 4)
        
        # ===== 5. 旋转符号 =====
        for i in range(6):
            sym_angle = self.core_rotation * 2 + i * math.pi / 3
            sym_r = core_r + 25
            sx = cx + math.cos(sym_angle) * sym_r
            sy = cy + math.sin(sym_angle) * sym_r
            pygame.draw.circle(self.image, foam, (int(sx), int(sy)), 5)
        
        # ===== 6. 吸引指示线 =====
        if self.frame % 20 < 10:
            for i in range(8):
                line_angle = i * math.pi / 4 + self.frame * 0.02
                inner_r = self.radius - 30
                outer_point = (cx + math.cos(line_angle) * self.radius,
                              cy + math.sin(line_angle) * self.radius)
                inner_point = (cx + math.cos(line_angle) * inner_r,
                              cy + math.sin(line_angle) * inner_r)
                pygame.draw.line(self.image, (*foam, 150), 
                               (int(outer_point[0]), int(outer_point[1])),
                               (int(inner_point[0]), int(inner_point[1])), 3)


class BubbleStormExplosion(pygame.sprite.Sprite):
    """气泡风暴爆炸特效 - 巨型水爆"""
    def __init__(self, x, y, style="default", radius=180):
        super().__init__()
        self.float_x, self.float_y = x, y
        self.frame = 0
        self.lifetime = 45
        self.style = style
        self.radius = radius
        
        # 爆炸碎片
        self.fragments = []
        for _ in range(40):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(8, 25)
            self.fragments.append({
                'x': 0, 'y': 0,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.uniform(5, 20),
                'type': random.choice(['bubble', 'water', 'foam'])
            })
        
        dim = int(self.radius * 3)
        self.image = pygame.Surface((dim, dim), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.dim = dim
    
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        
        # 更新碎片
        for f in self.fragments:
            f['x'] += f['vx']
            f['y'] += f['vy']
            f['vx'] *= 0.95
            f['vy'] *= 0.95
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = DUKE_BULLET_THEMES.get(self.style, DUKE_BULLET_THEMES["default"])
        water = theme["water"]
        pink = theme["pink"]
        foam = theme["foam"]
        bubble_c = theme["bubble"]
        
        cx, cy = self.dim // 2, self.dim // 2
        progress = self.frame / self.lifetime
        
        # 中心爆炸波
        for wave in range(6):
            wave_r = int(progress * self.radius * 1.5 + wave * 15)
            wave_alpha = int(220 * (1 - progress) * (1 - wave * 0.12))
            if wave_r > 0 and wave_alpha > 0:
                color = [bubble_c, water, foam, pink][wave % 4]
                pygame.draw.circle(self.image, (*color, wave_alpha), (cx, cy), wave_r, 5 - wave // 2)
        
        # 爆炸碎片
        for f in self.fragments:
            fx = cx + f['x']
            fy = cy + f['y']
            f_alpha = int(255 * (1 - progress))
            f_size = int(f['size'] * (1 - progress * 0.5))
            if f_size > 0 and 0 < fx < self.dim and 0 < fy < self.dim:
                if f['type'] == 'bubble':
                    pygame.draw.circle(self.image, (*bubble_c, f_alpha), (int(fx), int(fy)), f_size)
                    pygame.draw.circle(self.image, (*foam, f_alpha), (int(fx), int(fy)), f_size, 1)
                elif f['type'] == 'water':
                    pygame.draw.circle(self.image, (*water, f_alpha), (int(fx), int(fy)), f_size)
                else:
                    pygame.draw.circle(self.image, (*foam, f_alpha), (int(fx), int(fy)), f_size)
        
        # 中心闪光
        flash_alpha = int(255 * (1 - progress * 2)) if progress < 0.5 else 0
        if flash_alpha > 0:
            pygame.draw.circle(self.image, (255, 255, 255, flash_alpha), (cx, cy), 
                             int(40 * (1 - progress)))


# ==================== C技能：龙鱼海啸 ====================
class DragonFishTsunami(pygame.sprite.Sprite):
    """【龙鱼海啸】C键大招 - 召唤深海风暴与海啸巨浪
    
    效果：
    1. 玩家进入龙鱼形态，高速滑翔1.5秒（无敌+速度+40%）
    2. 滑翔路径留下持续5秒的海啸墙（减速+命中debuff）
    3. 滑翔结束时召唤巨型深渊龙卷+海啸巨浪席卷全屏
    4. 全屏深海风暴视觉：波涛、鲨群、雷暴、水下光影
    """
    
    def __init__(self, owner=None, style="default"):
        super().__init__()
        self.owner = owner
        self.style = style
        
        self.duration = 360  # 6秒总时长
        self.frame = 0
        self.slide_duration = 90  # 滑翔1.5秒
        self.sliding = True
        self.tsunami_phase = False
        
        # 海啸墙列表
        self.walls = []
        self.wall_timer = 0
        
        # 深海风暴视觉
        self.storm_waves = []  # 海浪
        self.lightning_bolts = []  # 闪电
        self.shark_silhouettes = []  # 鲨鱼剪影
        self.water_particles = []  # 水粒子
        self.bubble_streams = []  # 气泡流
        
        # 初始化背景元素
        self._init_storm_elements()
        
        # 龙鱼形态光环
        self.dragon_aura = {
            'radius': 80,
            'rotation': 0,
            'pulse': 0
        }
        
        # 海啸巨浪
        self.tsunami_waves = []
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        # 开始滑翔
        if owner:
            owner.duke_tsunami_active = True
            owner.duke_tsunami_speed_bonus = 0.4
    
    def _init_storm_elements(self):
        """初始化深海风暴元素"""
        # 海浪
        for i in range(6):
            self.storm_waves.append({
                'y': HEIGHT - 80 - i * 60,
                'amplitude': random.randint(15, 35),
                'frequency': random.uniform(0.01, 0.025),
                'phase': random.uniform(0, math.pi * 2),
                'speed': random.uniform(2, 5),
                'alpha': 120 - i * 15
            })
        
        # 鲨鱼剪影
        for _ in range(8):
            self.shark_silhouettes.append({
                'x': random.randint(-100, WIDTH + 100),
                'y': random.randint(HEIGHT // 3, HEIGHT - 100),
                'vx': random.choice([-1, 1]) * random.uniform(3, 8),
                'size': random.uniform(0.6, 1.5),
                'depth': random.uniform(0.3, 1.0),  # 深度影响透明度
                'fin_phase': random.uniform(0, math.pi * 2)
            })
        
        # 气泡流
        for _ in range(12):
            self.bubble_streams.append({
                'x': random.randint(0, WIDTH),
                'y': HEIGHT + random.randint(0, 100),
                'bubbles': [
                    {'offset': random.uniform(-10, 10), 'size': random.randint(3, 10), 
                     'phase': random.uniform(0, math.pi * 2)}
                    for _ in range(random.randint(4, 8))
                ],
                'speed': random.uniform(2, 5)
            })
    
    def _spawn_lightning(self):
        """生成闪电"""
        x = random.randint(50, WIDTH - 50)
        segments = []
        y = 0
        for _ in range(random.randint(5, 8)):
            next_y = y + random.randint(30, 70)
            segments.append({
                'x1': x + random.randint(-30, 30),
                'y1': y,
                'x2': x + random.randint(-40, 40),
                'y2': next_y
            })
            y = next_y
            x = segments[-1]['x2']
        
        self.lightning_bolts.append({
            'segments': segments,
            'life': 12,
            'width': random.randint(2, 4),
            'branches': random.randint(1, 3)
        })
    
    def _spawn_tsunami_wave(self):
        """生成海啸巨浪"""
        self.tsunami_waves.append({
            'y': HEIGHT + 50,
            'height': random.randint(120, 200),
            'speed': random.uniform(8, 15),
            'foam_particles': [],
            'damage_dealt': set()  # 记录已伤害的敌人
        })
    
    def update(self):
        self.frame += 1
        self.duration -= 1
        
        if self.duration <= 0:
            self._end_tsunami()
            self.kill()
            return
        
        # 滑翔阶段
        if self.sliding and self.frame <= self.slide_duration:
            self.wall_timer += 1
            if self.wall_timer >= 4:
                self.wall_timer = 0
                self._spawn_wave_wall()
            
            # 滑翔粒子
            if self.owner:
                for _ in range(3):
                    self.water_particles.append({
                        'x': self.owner.rect.centerx + random.randint(-30, 30),
                        'y': self.owner.rect.centery + random.randint(-10, 10),
                        'vx': random.uniform(-3, 3),
                        'vy': random.uniform(2, 6),
                        'size': random.uniform(2, 6),
                        'life': random.randint(20, 40),
                        'type': random.choice(['water', 'foam', 'bubble'])
                    })
            
            # 随机闪电
            if random.random() < 0.08:
                self._spawn_lightning()
        
        elif self.sliding:
            # 滑翔结束，进入海啸阶段
            self.sliding = False
            self.tsunami_phase = True
            self._spawn_giant_tornado()
            self._trigger_tsunami()
            if self.owner:
                self.owner.duke_tsunami_active = False
                self.owner.duke_tsunami_speed_bonus = 0
        
        # 海啸阶段
        if self.tsunami_phase:
            # 持续生成海啸波
            if self.frame % 25 == 0 and len(self.tsunami_waves) < 5:
                self._spawn_tsunami_wave()
            
            # 随机闪电
            if random.random() < 0.05:
                self._spawn_lightning()
        
        # 更新所有元素
        self._update_elements()
        self._apply_effects()
        self._render()
    
    def _spawn_wave_wall(self):
        """生成海啸墙片段"""
        if self.owner:
            wall = TsunamiWall(self.owner.rect.centerx, self.owner.rect.centery,
                             self.owner, self.style)
            all_sprites.add(wall)
            self.walls.append(wall)
    
    def _spawn_giant_tornado(self):
        """滑翔结束生成巨型龙卷"""
        if self.owner:
            # 中心巨型龙卷
            tornado = SharkTornado(self.owner.rect.centerx, self.owner.rect.centery,
                                  self.owner, self.style)
            tornado.pull_radius = 200
            tornado.lifetime = 300
            all_sprites.add(tornado)
            
            # 两侧辅助龙卷
            for offset in [-120, 120]:
                side_tornado = SharkTornado(self.owner.rect.centerx + offset, 
                                           self.owner.rect.centery,
                                           self.owner, self.style)
                side_tornado.pull_radius = 120
                side_tornado.lifetime = 240
                all_sprites.add(side_tornado)
            
            # 掉落深渊泡
            for i in range(3):
                offset_x = (i - 1) * 60
                bubble = AbyssBubblePickup(self.owner.rect.centerx + offset_x,
                                          self.owner.rect.centery + 50, self.owner)
                bubble.energy_value = 30
                all_sprites.add(bubble)
    
    def _trigger_tsunami(self):
        """触发海啸"""
        for _ in range(3):
            self._spawn_tsunami_wave()
    
    def _update_elements(self):
        """更新所有视觉元素"""
        # 更新闪电
        for bolt in self.lightning_bolts[:]:
            bolt['life'] -= 1
            if bolt['life'] <= 0:
                self.lightning_bolts.remove(bolt)
        
        # 更新水粒子
        for p in self.water_particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1  # 重力
            p['life'] -= 1
            if p['life'] <= 0 or p['y'] > HEIGHT:
                self.water_particles.remove(p)
        
        # 更新鲨鱼
        for shark in self.shark_silhouettes:
            shark['x'] += shark['vx']
            shark['fin_phase'] += 0.15
            if shark['vx'] > 0 and shark['x'] > WIDTH + 100:
                shark['x'] = -100
            elif shark['vx'] < 0 and shark['x'] < -100:
                shark['x'] = WIDTH + 100
        
        # 更新气泡流
        for stream in self.bubble_streams:
            stream['y'] -= stream['speed']
            if stream['y'] < -50:
                stream['y'] = HEIGHT + 50
                stream['x'] = random.randint(0, WIDTH)
        
        # 更新海啸巨浪
        for wave in self.tsunami_waves[:]:
            wave['y'] -= wave['speed']
            
            # 生成浪花粒子
            if random.random() < 0.3:
                wave['foam_particles'].append({
                    'x': random.randint(0, WIDTH),
                    'y': wave['y'],
                    'vx': random.uniform(-5, 5),
                    'vy': random.uniform(-8, -2),
                    'size': random.uniform(3, 10),
                    'life': random.randint(15, 30)
                })
            
            # 更新浪花粒子
            for fp in wave['foam_particles'][:]:
                fp['x'] += fp['vx']
                fp['y'] += fp['vy']
                fp['vy'] += 0.3
                fp['life'] -= 1
                if fp['life'] <= 0:
                    wave['foam_particles'].remove(fp)
            
            # 对敌人造成伤害
            for enemy in mobs:
                if enemy not in wave['damage_dealt']:
                    if abs(enemy.rect.centery - wave['y']) < wave['height'] // 2:
                        damage = self.owner.damage * 1.5 if self.owner else 40
                        enemy.take_damage(damage)
                        wave['damage_dealt'].add(enemy)
            
            if wave['y'] < -wave['height']:
                self.tsunami_waves.remove(wave)
    
    def _apply_effects(self):
        """应用减速等效果"""
        for wall in self.walls:
            if wall.alive():
                for enemy in mobs:
                    if wall.rect.colliderect(enemy.rect):
                        if hasattr(enemy, 'speed'):
                            enemy.speed *= 0.6
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = DUKE_BULLET_THEMES.get(self.style, DUKE_BULLET_THEMES["default"])
        water = theme["water"]
        pink = theme["pink"]
        foam = theme["foam"]
        tornado_c = theme["tornado"]
        
        progress = self.frame / 360
        
        # ===== 1. 深海背景 =====
        bg_alpha = int(50 + 30 * math.sin(self.frame * 0.05))
        pygame.draw.rect(self.image, (*water[:2], water[2] // 2, bg_alpha), (0, 0, WIDTH, HEIGHT))
        
        # ===== 2. 海浪背景 =====
        for wave in self.storm_waves:
            wave['phase'] += wave['frequency']
            points = []
            for x in range(0, WIDTH + 20, 20):
                y = wave['y'] + math.sin(wave['phase'] + x * 0.02) * wave['amplitude']
                points.append((x, int(y)))
            points.append((WIDTH, HEIGHT))
            points.append((0, HEIGHT))
            
            pygame.draw.polygon(self.image, (*water, wave['alpha']), points)
            # 浪尖泡沫
            for i, (px, py) in enumerate(points[:-2]):
                if i % 3 == 0:
                    pygame.draw.circle(self.image, (*foam, wave['alpha'] // 2), 
                                     (px, py - 3), 3)
        
        # ===== 3. 鲨鱼剪影 =====
        for shark in self.shark_silhouettes:
            alpha = int(100 * shark['depth'])
            size = shark['size']
            x, y = int(shark['x']), int(shark['y'])
            
            # 鲨鱼身体
            body_len = int(60 * size)
            body_h = int(20 * size)
            direction = 1 if shark['vx'] > 0 else -1
            
            # 身体
            body_points = [
                (x - direction * body_len // 2, y),
                (x + direction * body_len // 3, y - body_h // 2),
                (x + direction * body_len // 2, y),
                (x + direction * body_len // 3, y + body_h // 2),
            ]
            pygame.draw.polygon(self.image, (*tornado_c, alpha), body_points)
            
            # 背鳍
            fin_offset = math.sin(shark['fin_phase']) * 3
            fin_points = [
                (x, y - body_h // 2),
                (x - direction * 8, int(y - body_h - 15 * size + fin_offset)),
                (x + direction * 8, y - body_h // 2 - 3),
            ]
            pygame.draw.polygon(self.image, (*tornado_c, alpha), fin_points)
            
            # 尾鳍
            tail_x = x - direction * body_len // 2
            pygame.draw.polygon(self.image, (*tornado_c, alpha), [
                (tail_x, y),
                (tail_x - direction * 20, int(y - 12 * size)),
                (tail_x - direction * 20, int(y + 12 * size)),
            ])
        
        # ===== 4. 气泡流 =====
        for stream in self.bubble_streams:
            for i, bubble in enumerate(stream['bubbles']):
                bx = stream['x'] + bubble['offset'] + math.sin(self.frame * 0.1 + bubble['phase']) * 5
                by = stream['y'] + i * 15
                if 0 < by < HEIGHT:
                    alpha = int(150 * (1 - by / HEIGHT))
                    pygame.draw.circle(self.image, (*foam, alpha), (int(bx), int(by)), bubble['size'])
                    pygame.draw.circle(self.image, (*foam, alpha // 2), (int(bx), int(by)), bubble['size'], 1)
        
        # ===== 5. 海啸巨浪 =====
        for wave in self.tsunami_waves:
            wave_y = int(wave['y'])
            wave_h = wave['height']
            
            # 巨浪主体
            wave_alpha = min(200, int(220 * (1 - abs(wave_y - HEIGHT // 2) / HEIGHT)))
            
            # 多层浪
            for layer in range(4):
                layer_y = wave_y + layer * 15
                layer_h = wave_h - layer * 20
                layer_alpha = wave_alpha - layer * 40
                if layer_h > 0 and layer_alpha > 0:
                    # 波浪曲线
                    points = [(0, layer_y + layer_h)]
                    for x in range(0, WIDTH + 30, 30):
                        curve = math.sin(x * 0.02 + self.frame * 0.15 + layer) * 20
                        points.append((x, layer_y + curve))
                    points.append((WIDTH, layer_y + layer_h))
                    
                    color = water if layer % 2 == 0 else tornado_c
                    pygame.draw.polygon(self.image, (*color, layer_alpha), points)
            
            # 浪尖卷曲
            for x in range(50, WIDTH - 50, 100):
                curl_x = x + math.sin(self.frame * 0.2 + x * 0.01) * 30
                curl_y = wave_y - 20
                pygame.draw.arc(self.image, (*foam, wave_alpha),
                              (int(curl_x) - 25, int(curl_y) - 15, 50, 30),
                              0, math.pi, 3)
            
            # 浪花粒子
            for fp in wave['foam_particles']:
                fp_alpha = int(200 * fp['life'] / 30)
                pygame.draw.circle(self.image, (*foam, fp_alpha), 
                                 (int(fp['x']), int(fp['y'])), int(fp['size']))
        
        # ===== 6. 闪电 =====
        for bolt in self.lightning_bolts:
            alpha = int(255 * bolt['life'] / 12)
            for seg in bolt['segments']:
                # 主闪电
                pygame.draw.line(self.image, (*foam, alpha),
                               (seg['x1'], seg['y1']), (seg['x2'], seg['y2']), bolt['width'])
                # 光晕
                pygame.draw.line(self.image, (*foam, alpha // 3),
                               (seg['x1'], seg['y1']), (seg['x2'], seg['y2']), bolt['width'] + 6)
                
                # 分支
                if random.random() < 0.3:
                    branch_end_x = seg['x2'] + random.randint(-40, 40)
                    branch_end_y = seg['y2'] + random.randint(20, 50)
                    pygame.draw.line(self.image, (*foam, alpha // 2),
                                   (seg['x2'], seg['y2']), (branch_end_x, branch_end_y), 1)
        
        # ===== 7. 水粒子 =====
        for p in self.water_particles:
            p_alpha = int(200 * p['life'] / 40)
            if p['type'] == 'water':
                pygame.draw.circle(self.image, (*water, p_alpha), (int(p['x']), int(p['y'])), int(p['size']))
            elif p['type'] == 'foam':
                pygame.draw.circle(self.image, (*foam, p_alpha), (int(p['x']), int(p['y'])), int(p['size']))
            else:
                pygame.draw.circle(self.image, (*foam, p_alpha), (int(p['x']), int(p['y'])), int(p['size']))
                pygame.draw.circle(self.image, (255, 255, 255, p_alpha // 2), 
                                 (int(p['x']) - 1, int(p['y']) - 1), max(1, int(p['size']) // 2))
        
        # ===== 8. 龙鱼形态光环 =====
        if self.sliding and self.owner:
            ox, oy = self.owner.rect.centerx, self.owner.rect.centery
            self.dragon_aura['rotation'] += 0.08
            self.dragon_aura['pulse'] = math.sin(self.frame * 0.15) * 0.2 + 1.0
            
            aura_r = int(self.dragon_aura['radius'] * self.dragon_aura['pulse'])
            
            # 多层光环
            for i in range(4):
                ring_r = aura_r - i * 12
                ring_alpha = 150 - i * 35
                pygame.draw.circle(self.image, (*pink, ring_alpha), (ox, oy), ring_r, 3)
            
            # 旋转鲨鱼符号
            for i in range(6):
                angle = self.dragon_aura['rotation'] + i * math.pi / 3
                sx = ox + math.cos(angle) * (aura_r + 15)
                sy = oy + math.sin(angle) * (aura_r + 15)
                # 小鲨标记
                pygame.draw.circle(self.image, foam, (int(sx), int(sy)), 6)
                pygame.draw.circle(self.image, pink, (int(sx), int(sy)), 4)
            
            # 龙鱼之眼
            pygame.draw.ellipse(self.image, foam, (ox - 15, oy - 10, 30, 20))
            pygame.draw.circle(self.image, pink, (ox, oy), 8)
            pygame.draw.ellipse(self.image, (20, 30, 60), (ox - 2, oy - 6, 4, 12))
    
    def _end_tsunami(self):
        if self.owner:
            self.owner.duke_tsunami_active = False
            self.owner.duke_tsunami_speed_bonus = 0


class TsunamiWall(pygame.sprite.Sprite):
    """海啸墙片段 - 留场障碍，减速+命中debuff"""
    
    def __init__(self, x, y, owner=None, style="default"):
        super().__init__()
        self.owner = owner
        self.style = style
        self.float_x = float(x)
        self.float_y = float(y)
        
        self.lifetime = 300  # 5秒
        self.frame = 0
        self.width = 100
        self.height = 140
        
        # 内部波浪
        self.inner_waves = []
        for i in range(4):
            self.inner_waves.append({
                'phase': random.uniform(0, math.pi * 2),
                'speed': random.uniform(0.08, 0.15),
                'amplitude': random.uniform(5, 12)
            })
        
        # 气泡
        self.bubbles = []
        for _ in range(8):
            self.bubbles.append({
                'x': random.uniform(-self.width//2, self.width//2),
                'y': random.uniform(-self.height//2, self.height//2),
                'size': random.uniform(3, 10),
                'speed': random.uniform(0.5, 2),
                'wobble': random.uniform(0, math.pi * 2)
            })
        
        self.image = pygame.Surface((self.width + 40, self.height + 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 更新气泡
        for b in self.bubbles:
            b['y'] -= b['speed']
            b['wobble'] += 0.1
            if b['y'] < -self.height // 2:
                b['y'] = self.height // 2
                b['x'] = random.uniform(-self.width//2, self.width//2)
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = DUKE_BULLET_THEMES.get(self.style, DUKE_BULLET_THEMES["default"])
        water = theme["water"]
        foam = theme["foam"]
        tornado_c = theme["tornado"]
        
        cx, cy = self.width // 2 + 20, self.height // 2 + 20
        progress = 1 - self.lifetime / 300
        base_alpha = int(180 * (1 - progress * 0.6))
        
        # 外层光晕
        pygame.draw.ellipse(self.image, (*tornado_c, base_alpha // 3),
                          (cx - self.width//2 - 10, cy - self.height//2 - 10,
                           self.width + 20, self.height + 20))
        
        # 多层水墙
        for i, wave in enumerate(self.inner_waves):
            wave['phase'] += wave['speed']
            layer_offset = math.sin(wave['phase']) * wave['amplitude']
            layer_alpha = base_alpha - i * 30
            
            if layer_alpha > 0:
                pygame.draw.ellipse(self.image, (*water, layer_alpha),
                                  (cx - self.width//2 + i * 5 + int(layer_offset),
                                   cy - self.height//2 + i * 8,
                                   self.width - i * 10, self.height - i * 16))
        
        # 内层亮芯
        pygame.draw.ellipse(self.image, (*foam, base_alpha // 2),
                          (cx - self.width//4, cy - self.height//3,
                           self.width//2, self.height * 2 // 3))
        
        # 气泡
        for b in self.bubbles:
            bx = cx + b['x'] + math.sin(b['wobble']) * 3
            by = cy + b['y']
            b_alpha = int(base_alpha * 0.7)
            pygame.draw.circle(self.image, (*foam, b_alpha), (int(bx), int(by)), int(b['size']))
            # 高光
            pygame.draw.circle(self.image, (255, 255, 255, b_alpha // 2),
                             (int(bx) - 1, int(by) - 1), max(1, int(b['size']) // 3))
        
        # 边缘水流线
        for i in range(6):
            line_y = cy - self.height//2 + i * (self.height // 5)
            wave_x = math.sin(self.frame * 0.1 + i) * 8
            pygame.draw.line(self.image, (*foam, base_alpha // 2),
                           (cx - self.width//2 + int(wave_x), line_y),
                           (cx + self.width//2 + int(wave_x), line_y), 1)
        
        # 快消失时闪烁警告
        if self.lifetime < 60 and self.frame % 10 < 5:
            pygame.draw.ellipse(self.image, (*foam, 100),
                              (cx - self.width//2 - 5, cy - self.height//2 - 5,
                               self.width + 10, self.height + 10), 3)


# ==================== 击杀特效 ====================
class DukeKillEffect(pygame.sprite.Sprite):
    """猪公爵击杀特效 - 深海漩涡吞噬"""
    
    def __init__(self, x, y, size=1.0):
        super().__init__()
        self.float_x, self.float_y = x, y
        self.size = size
        self.frame = 0
        self.lifetime = 45
        
        self.vortex_rotation = 0
        self.sharks = []
        for i in range(5):
            self.sharks.append({
                'angle': i * math.pi * 2 / 5,
                'dist': 60 * size,
                'speed': 0.15 + random.uniform(-0.03, 0.03)
            })
        
        dim = int(160 * size)
        self.image = pygame.Surface((dim, dim), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.dim = dim
    
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        
        self.vortex_rotation += 0.2
        
        for s in self.sharks:
            s['angle'] += s['speed']
            s['dist'] -= 1.5 * self.size
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.dim // 2, self.dim // 2
        progress = self.frame / self.lifetime
        alpha = int(255 * (1 - progress))
        
        # 深海漩涡
        for layer in range(5):
            r = int((60 - layer * 10) * self.size * (1 - progress * 0.5))
            if r > 0:
                rot = self.vortex_rotation + layer * 0.5
                layer_alpha = alpha - layer * 40
                if layer_alpha > 0:
                    color = (30 + layer * 15, 80 + layer * 20, 180 - layer * 20, layer_alpha)
                    pygame.draw.circle(self.image, color, (cx, cy), r, 3)
        
        # 环绕小鲨
        for s in self.sharks:
            if s['dist'] > 0:
                sx = cx + math.cos(s['angle']) * s['dist']
                sy = cy + math.sin(s['angle']) * s['dist']
                if 0 <= sx < self.dim and 0 <= sy < self.dim:
                    pygame.draw.circle(self.image, (60, 90, 150, alpha),
                                     (int(sx), int(sy)), int(5 * self.size))
                    pygame.draw.circle(self.image, (255, 120, 180, alpha),
                                     (int(sx), int(sy)), int(3 * self.size))
        
        # 中心吞噬
        core_r = int(15 * self.size * progress)
        pygame.draw.circle(self.image, (10, 20, 50, alpha), (cx, cy), core_r)


def spawn_duke_kill_effect(x, y, size=1.0):
    """生成猪公爵击杀特效"""
    effect = DukeKillEffect(x, y, size)
    all_sprites.add(effect)


# ==================== 预览渲染适配器（用于customization预览） ====================
def render_dukefishron_bullet_preview(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染深渊龙鱼·猪公爵子弹预览效果
    
    Args:
        surface: pygame绘图表面
        effects: 效果列表
        color: 主题颜色
        center_x, center_y: 中心坐标
        size: 预览尺寸
        x, y: 左上角坐标
    
    Returns:
        bool: 如果渲染了效果返回True，否则False
    """
    # 检查是否是Duke Fishron相关效果
    duke_effects = [
        # 子弹主题effects（来自customization.py BULLET_THEMES）
        "water_splash", "tornado_spawn",      # duke_default
        "void_splash", "dark_tornado",        # duke_abyss_spear
        "shark_chase", "bite_hit",            # duke_shark_missile
        "bubble_refract", "split_chase",      # duke_bubble_bomb
        "tornado_burst", "true_damage",       # duke_tornado_blast
        "tsunami_sweep", "accuracy_debuff",   # duke_tsunami_wave
        "phase_through", "soul_drain",        # duke_phantom_pierce
        "life_steal", "blood_curse",          # duke_blood_fang
        "rainbow_burst", "dazzle",            # duke_tropical_burst
        "freeze", "shatter",                  # duke_frost_shard
        "golden_blaze", "imperial_wrath",     # duke_imperial_gold
    ]
    
    # 检查是否有Duke Fishron效果
    has_duke_effect = any(effect in effects for effect in duke_effects)
    if not has_duke_effect:
        return False
    
    t = pygame.time.get_ticks() / 1000.0
    frame = int(t * 30)
    
    # 渲染子弹效果
    bullet_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
    cx, cy = size, size
    
    # 动态脉冲
    pulse = abs(math.sin(t * 3)) * 0.2 + 0.9
    
    # ===== 判断子弹类型并渲染对应效果 =====
    
    # 幽灵形态 - 透明穿刺矛
    if "phase_through" in effects or "soul_drain" in effects:
        # 幽灵矛 - 半透明波动效果
        ghost_color = (180, 200, 220)
        
        # 幽灵光晕
        for i in range(3):
            glow_r = int((size // 3 + i * 4) * pulse)
            alpha = 60 - i * 15
            pygame.draw.circle(bullet_surf, (*ghost_color, alpha), (cx, cy), glow_r)
        
        # 矛形轮廓 - 透明闪烁
        spear_len = int(size * 0.6)
        spear_w = int(size * 0.15)
        wave_offset = math.sin(t * 5) * 2
        
        spear_points = [
            (cx, cy - spear_len),               # 顶端
            (cx + spear_w, cy - spear_len//3 + wave_offset),
            (cx + spear_w//2, cy + spear_len//2),
            (cx - spear_w//2, cy + spear_len//2),
            (cx - spear_w, cy - spear_len//3 + wave_offset),
        ]
        
        ghost_alpha = int(120 + 50 * math.sin(t * 4))
        pygame.draw.polygon(bullet_surf, (*ghost_color, ghost_alpha), spear_points)
        
        # 灵魂粒子
        for i in range(4):
            angle = t * 2 + i * math.pi / 2
            dist = size // 4 + math.sin(t * 3 + i) * 4
            sx = cx + math.cos(angle) * dist
            sy = cy + math.sin(angle) * dist
            pygame.draw.circle(bullet_surf, (220, 240, 255, 150), (int(sx), int(sy)), 3)
    
    # 血月形态 - 猩红獠牙
    elif "life_steal" in effects or "blood_curse" in effects:
        blood_red = (150, 30, 50)
        blood_glow = (200, 50, 80)
        
        # 血色光晕
        for i in range(2):
            r = int((size // 3.5 + i * 5) * pulse)
            alpha = 100 - i * 30
            pygame.draw.circle(bullet_surf, (*blood_red, alpha), (cx, cy), r)
        
        # 獠牙形状
        fang_len = int(size * 0.5)
        fang_w = int(size * 0.12)
        
        # 左獠牙
        lf_points = [
            (cx - 3, cy - fang_len),
            (cx - 3 + fang_w, cy - fang_len // 2),
            (cx - 3 + fang_w // 2, cy + fang_len // 3),
        ]
        pygame.draw.polygon(bullet_surf, blood_glow, lf_points)
        
        # 右獠牙
        rf_points = [
            (cx + 3, cy - fang_len),
            (cx + 3 - fang_w, cy - fang_len // 2),
            (cx + 3 - fang_w // 2, cy + fang_len // 3),
        ]
        pygame.draw.polygon(bullet_surf, blood_glow, rf_points)
        
        # 滴血效果
        drip_y = cy + fang_len // 3 + abs(math.sin(t * 4)) * 5
        pygame.draw.circle(bullet_surf, (255, 50, 80), (cx, int(drip_y)), 3)
    
    # 热带形态 - 彩虹爆裂
    elif "rainbow_burst" in effects or "dazzle" in effects:
        # 彩虹光环
        for i in range(5):
            hue = (frame * 10 + i * 72) % 360
            # 简易HSV转RGB
            h = hue / 60
            x_val = 1 - abs(h % 2 - 1)
            if h < 1: r, g, b = 1, x_val, 0
            elif h < 2: r, g, b = x_val, 1, 0
            elif h < 3: r, g, b = 0, 1, x_val
            elif h < 4: r, g, b = 0, x_val, 1
            elif h < 5: r, g, b = x_val, 0, 1
            else: r, g, b = 1, 0, x_val
            rainbow_c = (int(r * 255), int(g * 255), int(b * 255))
            
            ring_r = int((size // 4 + i * 3) * pulse)
            pygame.draw.circle(bullet_surf, (*rainbow_c, 180), (cx, cy), ring_r, 2)
        
        # 中心金色鱼形
        fish_len = int(size * 0.35)
        pygame.draw.ellipse(bullet_surf, (255, 200, 80), 
                          (cx - fish_len//2, cy - fish_len//4, fish_len, fish_len//2))
        pygame.draw.circle(bullet_surf, (255, 255, 255), (cx + fish_len//4, cy - 2), 3)
    
    # 霜冻形态 - 冰晶碎片
    elif "freeze" in effects or "shatter" in effects:
        ice_blue = (100, 180, 220)
        frost_white = (220, 245, 255)
        
        # 冰晶六边形
        crystal_r = int(size // 3.5 * pulse)
        for i in range(6):
            angle = i * math.pi / 3 + t * 0.5
            x1 = cx + math.cos(angle) * crystal_r
            y1 = cy + math.sin(angle) * crystal_r
            x2 = cx + math.cos(angle + math.pi / 3) * crystal_r
            y2 = cy + math.sin(angle + math.pi / 3) * crystal_r
            pygame.draw.line(bullet_surf, (*ice_blue, 200), (int(x1), int(y1)), (int(x2), int(y2)), 2)
        
        # 冰刺
        for i in range(6):
            angle = i * math.pi / 3 + t * 0.5
            spike_len = crystal_r + 8 + math.sin(t * 4 + i) * 3
            sx = cx + math.cos(angle) * spike_len
            sy = cy + math.sin(angle) * spike_len
            pygame.draw.line(bullet_surf, frost_white, (cx, cy), (int(sx), int(sy)), 2)
        
        # 冰核
        pygame.draw.circle(bullet_surf, ice_blue, (cx, cy), 6)
        pygame.draw.circle(bullet_surf, frost_white, (cx, cy), 3)
    
    # 黄金形态 - 帝王金焰
    elif "golden_blaze" in effects or "imperial_wrath" in effects:
        gold = (220, 180, 50)
        bright_gold = (255, 220, 100)
        
        # 皇冠形状
        crown_w = int(size * 0.4)
        crown_h = int(size * 0.3)
        
        # 皇冠底部
        pygame.draw.rect(bullet_surf, gold, 
                        (cx - crown_w//2, cy, crown_w, crown_h//2))
        
        # 皇冠尖齿
        for i in range(3):
            tip_x = cx - crown_w//3 + i * crown_w//3
            points = [
                (tip_x - 5, cy),
                (tip_x + 5, cy),
                (tip_x, cy - crown_h - math.sin(t * 4 + i) * 3),
            ]
            pygame.draw.polygon(bullet_surf, bright_gold, points)
        
        # 金焰效果
        for i in range(4):
            flame_angle = t * 3 + i * math.pi / 2
            fx = cx + math.cos(flame_angle) * (size // 3)
            fy = cy + 5 + math.sin(flame_angle) * 5
            pygame.draw.circle(bullet_surf, (*bright_gold, 150), (int(fx), int(fy)), 4)
    
    # 海啸形态 - 巨浪
    elif "tsunami_sweep" in effects or "accuracy_debuff" in effects:
        wave_blue = (30, 100, 200)
        foam = (200, 240, 255)
        
        # 巨浪曲线
        wave_h = int(size * 0.4)
        wave_w = int(size * 0.8)
        
        # 波浪形状
        wave_points = []
        for i in range(10):
            wx = cx - wave_w//2 + i * wave_w // 9
            wave_offset = math.sin(t * 4 + i * 0.5) * 5
            wy = cy - wave_h//2 + wave_offset if i % 2 == 0 else cy + wave_offset
            wave_points.append((wx, wy))
        wave_points.append((cx + wave_w//2, cy + wave_h//2))
        wave_points.append((cx - wave_w//2, cy + wave_h//2))
        
        if len(wave_points) >= 3:
            pygame.draw.polygon(bullet_surf, (*wave_blue, 180), wave_points)
        
        # 浪花泡沫
        for i in range(5):
            fx = cx - wave_w//3 + i * wave_w // 5
            fy = cy - wave_h//3 + math.sin(t * 5 + i) * 3
            pygame.draw.circle(bullet_surf, foam, (int(fx), int(fy)), 3)
    
    # 龙卷形态 - 鲨龙卷
    elif "tornado_burst" in effects or "true_damage" in effects:
        tornado_blue = (40, 120, 220)
        
        # 龙卷螺旋
        tornado_r = int(size // 3 * pulse)
        for layer in range(4):
            layer_r = tornado_r - layer * 4
            if layer_r > 0:
                angle_offset = t * 3 + layer * 0.5
                alpha = 200 - layer * 40
                pygame.draw.circle(bullet_surf, (*tornado_blue, alpha), 
                                 (cx, cy - layer * 4), layer_r, 2)
        
        # 小鲨标记
        shark_y = cy + size // 4
        pygame.draw.ellipse(bullet_surf, (60, 90, 150), 
                          (cx - 8, shark_y - 4, 16, 8))
        # 鲨鱼鳍
        pygame.draw.polygon(bullet_surf, (60, 90, 150),
                          [(cx, shark_y - 4), (cx + 4, shark_y - 10), (cx + 6, shark_y - 2)])
    
    # 气泡形态 - 折射泡
    elif "bubble_refract" in effects or "split_chase" in effects:
        bubble_blue = (100, 180, 255)
        
        # 主气泡
        bubble_r = int(size // 3.5 * pulse)
        pygame.draw.circle(bullet_surf, (*bubble_blue, 150), (cx, cy), bubble_r)
        pygame.draw.circle(bullet_surf, (255, 255, 255), (cx, cy), bubble_r, 2)
        
        # 高光
        pygame.draw.circle(bullet_surf, (255, 255, 255, 200), 
                         (cx - bubble_r//3, cy - bubble_r//3), bubble_r//4)
        
        # 分裂小泡
        for i in range(3):
            angle = t * 2 + i * 2 * math.pi / 3
            bx = cx + math.cos(angle) * (bubble_r + 8)
            by = cy + math.sin(angle) * (bubble_r + 8)
            pygame.draw.circle(bullet_surf, (*bubble_blue, 120), (int(bx), int(by)), 5)
    
    # 小鲨形态 - 追踪鲨
    elif "shark_chase" in effects or "bite_hit" in effects:
        shark_gray = (60, 90, 150)
        shark_pink = (255, 120, 180)
        
        # 小鲨身体
        shark_len = int(size * 0.4)
        pygame.draw.ellipse(bullet_surf, shark_gray,
                          (cx - shark_len//2, cy - shark_len//4, shark_len, shark_len//2))
        
        # 鲨鱼鳍
        fin_points = [
            (cx, cy - shark_len//4),
            (cx + 5, cy - shark_len//2 - 3),
            (cx + 8, cy - shark_len//5),
        ]
        pygame.draw.polygon(bullet_surf, shark_gray, fin_points)
        
        # 尾鳍
        tail_points = [
            (cx - shark_len//2, cy),
            (cx - shark_len//2 - 8, cy - 6),
            (cx - shark_len//2 - 8, cy + 6),
        ]
        pygame.draw.polygon(bullet_surf, shark_pink, tail_points)
        
        # 眼睛
        pygame.draw.circle(bullet_surf, (255, 255, 255), (cx + shark_len//4, cy - 2), 3)
        pygame.draw.circle(bullet_surf, (0, 0, 0), (cx + shark_len//4, cy - 2), 2)
    
    # 深渊之矛 - 暗紫形态
    elif "void_splash" in effects or "dark_tornado" in effects:
        abyss_purple = (40, 30, 120)
        void_pink = (180, 80, 200)
        
        # 深渊光晕
        for i in range(2):
            r = int((size // 4 + i * 6) * pulse)
            alpha = 80 - i * 25
            pygame.draw.circle(bullet_surf, (*abyss_purple, alpha), (cx, cy), r)
        
        # 尖锐水矛
        spear_len = int(size * 0.55)
        spear_w = int(size * 0.12)
        
        spear_points = [
            (cx, cy - spear_len),                 # 顶端
            (cx + spear_w, cy - spear_len // 3),  # 右肩
            (cx + spear_w // 2, cy + spear_len // 2),  # 右底
            (cx - spear_w // 2, cy + spear_len // 2),  # 左底
            (cx - spear_w, cy - spear_len // 3),  # 左肩
        ]
        pygame.draw.polygon(bullet_surf, void_pink, spear_points)
        
        # 矛尖高光
        pygame.draw.circle(bullet_surf, (220, 150, 255), (cx, cy - spear_len + 4), 4)
    
    # 默认 - 深渊水矛（深海蓝）
    else:
        water_blue = color if color else (30, 80, 180)
        pink = (255, 120, 180)
        foam = (180, 220, 255)
        
        # 水波光晕
        for i in range(3):
            r = int((size // 4 + i * 5) * pulse)
            alpha = 100 - i * 25
            pygame.draw.circle(bullet_surf, (*water_blue, alpha), (cx, cy), r)
        
        # 水矛形状
        spear_len = int(size * 0.5)
        spear_w = int(size * 0.1)
        
        spear_points = [
            (cx, cy - spear_len),                 # 顶端
            (cx + spear_w, cy - spear_len // 3),  # 右肩
            (cx + spear_w // 2, cy + spear_len // 2),  # 右底
            (cx - spear_w // 2, cy + spear_len // 2),  # 左底
            (cx - spear_w, cy - spear_len // 3),  # 左肩
        ]
        pygame.draw.polygon(bullet_surf, pink, spear_points)
        pygame.draw.polygon(bullet_surf, foam, spear_points, 2)
        
        # 矛尖高光
        pygame.draw.circle(bullet_surf, foam, (cx, cy - spear_len + 3), 3)
        
        # 小龙卷标记
        tornado_y = cy + size // 3
        for i in range(3):
            tr = 4 - i
            pygame.draw.circle(bullet_surf, (*water_blue, 150 - i * 40), 
                             (cx, int(tornado_y - i * 3)), tr)
    
    surface.blit(bullet_surf, (x, y))
    return True
