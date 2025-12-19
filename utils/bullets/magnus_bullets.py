# -*- coding: utf-8 -*-
"""
真理之书 MAGNUS 子弹和技能系统
Grimoire-System "MAGNUS" - Combat System

战斗机制：
- 被动：法力过载（不射击时充能，满后三倍弹幕）
- 普攻：奥术飞弹（彩色希腊字母符文，微弱追踪）
- 核心技能：法术轮盘（火球/冰霜波/闪电链切换）
- 辅助：书页护卫（自动防护）

大招：
- F键：禁忌篇章·暴风雪（冰锥雨+冻结）
- G键：召唤·远古之灵（骷髅头冲撞）
- C键：真理之圆（魔法阵持续伤害）
"""

import pygame
import math
import random
from config import WIDTH, HEIGHT, all_sprites, bullets, mobs, enemy_bullets

# ============================================================
#   MAGNUS 颜色定义
# ============================================================
MAGNUS_COLORS = {
    "arcane": (255, 0, 255),      # 洋红 - 奥术
    "fire": (255, 100, 0),        # 橙红 - 火焰
    "ice": (100, 200, 255),       # 青色 - 冰霜
    "lightning": (180, 100, 255), # 紫色 - 闪电
    "holy": (255, 255, 150),      # 金光 - 神圣
    "page": (245, 222, 179),      # 书页色
    "rune": (255, 215, 0),        # 金色符文
}


# ============================================================
#   普攻：奥术飞弹 - 彩色希腊字母符文
# ============================================================
class ArcaneMissileBullet(pygame.sprite.Sprite):
    """
    奥术飞弹 - MAGNUS主武器
    
    视觉：彩色希腊字母符文飞弹
    特性：带有微弱追踪能力
    """
    
    def __init__(self, x, y, angle=None, speed=12, damage=15, 
                 element="arcane", overloaded=False, **kwargs):
        super().__init__()
        self.x = x
        self.y = y
        self.damage = damage
        self.is_enemy = False
        self.piercing = 0
        
        # 创建image和rect
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        # 添加到精灵组
        bullets.add(self)
        all_sprites.add(self)
        
        self.base_angle = angle if angle is not None else -math.pi / 2
        self.angle = self.base_angle
        self.speed = speed
        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed
        self.element = element  # arcane, fire, ice, lightning
        self.overloaded = overloaded  # 过载状态
        self.lifetime = 0
        self.max_lifetime = 120
        self.tracking_strength = 0.02  # 追踪强度
        self.trail = []
        self.greek_letters = ['α', 'β', 'γ', 'δ', 'Ω', 'Σ', 'Π']
        self.letter = random.choice(self.greek_letters)
        
        # 元素颜色
        self.color = MAGNUS_COLORS.get(element, MAGNUS_COLORS["arcane"])
        
        # 过载增强
        if overloaded:
            self.damage *= 1.5
            self.speed *= 1.2
    
    def alive(self):
        return self.groups()
    
    def update(self):
        self.lifetime += 1
        if self.lifetime > self.max_lifetime:
            self.kill()
            return
        
        # 微弱追踪最近敌人
        if self.tracking_strength > 0:
            nearest = None
            nearest_dist = float('inf')
            for enemy in mobs:
                if hasattr(enemy, 'rect') and hasattr(enemy, 'hp') and enemy.hp > 0:
                    dist = math.sqrt((enemy.rect.centerx - self.x) ** 2 + 
                                   (enemy.rect.centery - self.y) ** 2)
                    if dist < nearest_dist and dist < 300:
                        nearest_dist = dist
                        nearest = enemy
            
            if nearest:
                target_angle = math.atan2(nearest.rect.centery - self.y,
                                         nearest.rect.centerx - self.x)
                angle_diff = target_angle - self.angle
                # 归一化角度差
                while angle_diff > math.pi:
                    angle_diff -= 2 * math.pi
                while angle_diff < -math.pi:
                    angle_diff += 2 * math.pi
                
                self.angle += angle_diff * self.tracking_strength
                self.vx = math.cos(self.angle) * self.speed
                self.vy = math.sin(self.angle) * self.speed
        
        # 更新位置
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))
        
        # 记录轨迹
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 8:
            self.trail.pop(0)
        
        # 边界检查
        if self.x < -50 or self.x > 850 or self.y < -50 or self.y > 700:
            self.kill()
        
        # 更新image
        self._render()
    
    def _render(self):
        t = self.lifetime * 0.1
        pulse = 0.7 + 0.3 * math.sin(t * 5)
        
        self.image.fill((0, 0, 0, 0))
        
        # 主体光晕
        glow_size = int(12 * pulse) if self.overloaded else int(8 * pulse)
        center = 12
        
        # 外层光晕
        pygame.draw.circle(self.image, (*self.color, 60), (center, center), min(12, glow_size * 2))
        # 中层
        pygame.draw.circle(self.image, (*self.color, 120), (center, center), min(8, glow_size))
        # 核心
        pygame.draw.circle(self.image, (255, 255, 255, 200), (center, center), max(2, glow_size // 2))
    
    def draw(self, surface):
        # 绘制拖尾
        t = self.lifetime * 0.1
        pulse = 0.7 + 0.3 * math.sin(t * 5)
        for i, pos in enumerate(self.trail):
            trail_alpha = int(100 * (i / len(self.trail)) * pulse)
            trail_size = max(1, int(4 * (i / len(self.trail))))
            s = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, trail_alpha), 
                             (trail_size, trail_size), trail_size)
            surface.blit(s, (pos[0] - trail_size, pos[1] - trail_size))
            pygame.draw.circle(s, (*self.color, trail_alpha), 
                             (trail_size, trail_size), trail_size)
            surface.blit(s, (pos[0] - trail_size, pos[1] - trail_size))
        
        # 主体光晕
        glow_size = int(12 * pulse) if self.overloaded else int(8 * pulse)
        s = pygame.Surface((glow_size * 4, glow_size * 4), pygame.SRCALPHA)
        
        # 外层光晕
        pygame.draw.circle(s, (*self.color, 60), 
                         (glow_size * 2, glow_size * 2), glow_size * 2)
        # 中层
        pygame.draw.circle(s, (*self.color, 120), 
                         (glow_size * 2, glow_size * 2), glow_size)
        # 核心
        pygame.draw.circle(s, (255, 255, 255, 200), 
                         (glow_size * 2, glow_size * 2), glow_size // 2)
        
        surface.blit(s, (int(self.x) - glow_size * 2, int(self.y) - glow_size * 2))
        
        # 过载特效
        if self.overloaded:
            for i in range(3):
                spark_angle = t * 10 + i * 2.09
                spark_dist = 10 * pulse
                spark_x = int(self.x + math.cos(spark_angle) * spark_dist)
                spark_y = int(self.y + math.sin(spark_angle) * spark_dist)
                spark_s = pygame.Surface((8, 8), pygame.SRCALPHA)
                pygame.draw.circle(spark_s, (*self.color, 150), (4, 4), 3)
                surface.blit(spark_s, (spark_x - 4, spark_y - 4))


# ============================================================
#   法术轮盘：火球术
# ============================================================
class FireballBullet(pygame.sprite.Sprite):
    """
    火球术 - 直线高伤，击中爆炸
    """
    
    def __init__(self, x, y, angle=None, speed=10, damage=25, **kwargs):
        super().__init__()
        self.x = x
        self.y = y
        self.damage = damage
        self.is_enemy = False
        self.piercing = 0
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        bullets.add(self)
        all_sprites.add(self)
        self.angle = angle if angle is not None else -math.pi / 2
        self.speed = speed
        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed
        self.lifetime = 0
        self.max_lifetime = 90
        self.exploded = False
        self.explosion_radius = 40
        self.explosion_timer = 0
        self.trail = []
        self.color = MAGNUS_COLORS["fire"]
    
    def alive(self):
        return self.groups()
    
    def update(self):
        self.lifetime += 1
        
        if self.exploded:
            self.explosion_timer += 1
            if self.explosion_timer > 15:
                self.kill()
            return
        
        if self.lifetime > self.max_lifetime:
            self.kill()
            return
        
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))
        
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        if self.x < -50 or self.x > 850 or self.y < -50 or self.y > 700:
            self.kill()
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        t = self.lifetime * 0.1
        pulse = 0.8 + 0.2 * math.sin(t * 8)
        size = int(12 * pulse)
        pygame.draw.circle(self.image, (255, 150, 50, 200), (12, 12), min(10, size))
        pygame.draw.circle(self.image, (255, 255, 200, 255), (12, 12), min(4, size // 3))
    
    def on_hit(self, enemy):
        """击中时触发爆炸"""
        if not self.exploded:
            self.exploded = True
            self.vx = 0
            self.vy = 0
            return True
        return False
    
    def draw(self, surface):
        if not self.alive:
            return
        
        t = self.lifetime * 0.1
        
        if self.exploded:
            # 爆炸效果
            progress = self.explosion_timer / 15
            exp_radius = int(self.explosion_radius * (0.5 + 0.5 * progress))
            exp_alpha = int(200 * (1 - progress))
            
            s = pygame.Surface((exp_radius * 2 + 20, exp_radius * 2 + 20), pygame.SRCALPHA)
            center = exp_radius + 10
            
            # 多层爆炸
            pygame.draw.circle(s, (255, 200, 100, exp_alpha // 3), 
                             (center, center), exp_radius)
            pygame.draw.circle(s, (255, 150, 50, exp_alpha // 2), 
                             (center, center), int(exp_radius * 0.7))
            pygame.draw.circle(s, (255, 100, 0, exp_alpha), 
                             (center, center), int(exp_radius * 0.4))
            pygame.draw.circle(s, (255, 255, 200, exp_alpha), 
                             (center, center), int(exp_radius * 0.2))
            
            surface.blit(s, (int(self.x) - center, int(self.y) - center))
        else:
            # 火球拖尾
            for i, pos in enumerate(self.trail):
                trail_progress = i / len(self.trail)
                trail_alpha = int(150 * trail_progress)
                trail_size = max(1, int(8 * trail_progress))
                s = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 150, 50, trail_alpha), 
                                 (trail_size, trail_size), trail_size)
                surface.blit(s, (pos[0] - trail_size, pos[1] - trail_size))
            
            # 火球主体
            pulse = 0.8 + 0.2 * math.sin(t * 8)
            size = int(12 * pulse)
            s = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            
            pygame.draw.circle(s, (255, 200, 100, 80), (size * 2, size * 2), size * 2)
            pygame.draw.circle(s, (255, 150, 50, 150), (size * 2, size * 2), size)
            pygame.draw.circle(s, (255, 100, 0, 200), (size * 2, size * 2), size // 2)
            pygame.draw.circle(s, (255, 255, 200, 255), (size * 2, size * 2), size // 4)
            
            surface.blit(s, (int(self.x) - size * 2, int(self.y) - size * 2))


# ============================================================
#   法术轮盘：冰霜波
# ============================================================
class FrostWaveBullet(pygame.sprite.Sprite):
    """
    冰霜波 - 宽扇形散射，低伤但减速
    """
    
    def __init__(self, x, y, angle=None, speed=8, damage=8, **kwargs):
        super().__init__()
        self.x = x
        self.y = y
        self.damage = damage
        self.is_enemy = False
        self.piercing = 0
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        bullets.add(self)
        all_sprites.add(self)
        self.angle = angle if angle is not None else -math.pi / 2
        self.speed = speed
        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed
        self.lifetime = 0
        self.max_lifetime = 60
        self.slow_effect = 0.5  # 减速50%
        self.slow_duration = 60  # 减速持续1秒
        self.color = MAGNUS_COLORS["ice"]
        self.size = 6
    
    def alive(self):
        return self.groups()
    
    def update(self):
        self.lifetime += 1
        if self.lifetime > self.max_lifetime:
            self.kill()
            return
        
        # 冰霜波逐渐扩散变大
        self.size = 6 + self.lifetime * 0.1
        
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))
        
        if self.x < -50 or self.x > 850 or self.y < -50 or self.y > 700:
            self.kill()
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        t = self.lifetime * 0.1
        pulse = 0.7 + 0.3 * math.sin(t * 6)
        size = int(self.size * pulse)
        pygame.draw.circle(self.image, (*self.color, 150), (10, 10), min(8, size))
        pygame.draw.circle(self.image, (200, 240, 255, 200), (10, 10), min(4, size // 2))
    
    def on_hit(self, enemy):
        """击中时施加减速"""
        if hasattr(enemy, 'apply_slow'):
            enemy.apply_slow(self.slow_effect, self.slow_duration)
        return True
    
    def draw(self, surface):
        if not self.alive:
            return
        
        t = self.lifetime * 0.1
        pulse = 0.7 + 0.3 * math.sin(t * 6)
        size = int(self.size * pulse)
        
        s = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
        
        # 冰晶效果
        alpha_fade = 1 - (self.lifetime / self.max_lifetime) * 0.5
        pygame.draw.circle(s, (*self.color, int(60 * alpha_fade)), 
                         (size * 2, size * 2), size * 2)
        pygame.draw.circle(s, (*self.color, int(120 * alpha_fade)), 
                         (size * 2, size * 2), size)
        pygame.draw.circle(s, (200, 240, 255, int(180 * alpha_fade)), 
                         (size * 2, size * 2), size // 2)
        
        # 冰晶尖刺
        for spike in range(6):
            spike_angle = t * 2 + spike * 1.047
            spike_len = size * 1.5
            spike_x = size * 2 + int(math.cos(spike_angle) * spike_len)
            spike_y = size * 2 + int(math.sin(spike_angle) * spike_len)
            pygame.draw.line(s, (*self.color, int(150 * alpha_fade)),
                           (size * 2, size * 2), (spike_x, spike_y), 2)
        
        surface.blit(s, (int(self.x) - size * 2, int(self.y) - size * 2))


# ============================================================
#   法术轮盘：闪电链
# ============================================================
class LightningChainBullet(pygame.sprite.Sprite):
    """
    闪电链 - 自动在敌人之间弹射（超强特效版）
    """
    
    def __init__(self, x, y, target=None, damage=12, chain_count=3, **kwargs):
        super().__init__()
        self.x = x
        self.y = y
        self.damage = damage
        self.is_enemy = False
        self.piercing = 0
        # 更大的surface以容纳更大特效
        self.image = pygame.Surface((500, 500), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        bullets.add(self)
        all_sprites.add(self)
        self.target = target
        self.chain_count = chain_count
        self.chain_range = 200
        self.speed = 25  # 稍慢以便观察
        self.hit_enemies = set()
        self.lifetime = 0
        self.max_lifetime = 20  # 延长显示时间
        # 更亮的闪电颜色
        self.color = (200, 150, 255)  # 亮紫色
        self.bright_color = (255, 220, 255)  # 高亮粉紫
        self.core_color = (255, 255, 255)  # 白色核心
        
        if target and hasattr(target, 'rect'):
            self.target_x = target.rect.centerx
            self.target_y = target.rect.centery
        else:
            self.target_x = x
            self.target_y = y - 100
    
    def update(self):
        self.lifetime += 1
        
        if self.lifetime > self.max_lifetime:
            self.kill()
            return
        
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist < self.speed:
            self.x = self.target_x
            self.y = self.target_y
            
            if self.target and self.chain_count > 0:
                self.hit_enemies.add(id(self.target))
                if hasattr(self.target, 'hp'):
                    self.target.hp -= self.damage
                
                next_target = None
                next_dist = float('inf')
                for enemy in mobs:
                    if (hasattr(enemy, 'rect') and hasattr(enemy, 'hp') and 
                        enemy.hp > 0 and id(enemy) not in self.hit_enemies):
                        d = math.hypot(enemy.rect.centerx - self.x, enemy.rect.centery - self.y)
                        if d < self.chain_range and d < next_dist:
                            next_dist = d
                            next_target = enemy
                
                if next_target:
                    self.target = next_target
                    self.target_x = next_target.rect.centerx
                    self.target_y = next_target.rect.centery
                    self.chain_count -= 1
                    self.lifetime = 0
                else:
                    self.kill()
            else:
                self.kill()
        else:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed
        
        self._render()
    
    def _render(self):
        """渲染超强闪电效果"""
        self.image.fill((0, 0, 0, 0))
        
        # 计算局部坐标
        cx, cy = 250, 250  # surface中心（更大）
        sx, sy = int(self.x), int(self.y)
        tx, ty = int(self.target_x), int(self.target_y)
        
        # 更新rect位置到两点中间
        mid_x = (sx + tx) // 2
        mid_y = (sy + ty) // 2
        self.rect.center = (mid_x, mid_y)
        
        # 转换到局部坐标
        local_sx = sx - mid_x + cx
        local_sy = sy - mid_y + cy
        local_tx = tx - mid_x + cx
        local_ty = ty - mid_y + cy
        
        ldx = local_tx - local_sx
        ldy = local_ty - local_sy
        dist = math.sqrt(ldx * ldx + ldy * ldy)
        
        # 强烈闪烁
        flicker = 0.6 + 0.4 * math.sin(self.lifetime * 4)
        flash = 0.8 + 0.2 * math.sin(self.lifetime * 8)  # 快速闪烁
        
        # ========== 1. 起点大型电弧球 ==========
        start_glow = int(35 * flicker)
        pygame.draw.circle(self.image, (100, 50, 150, 40), (local_sx, local_sy), start_glow + 15)
        pygame.draw.circle(self.image, (*self.color, 70), (local_sx, local_sy), start_glow)
        pygame.draw.circle(self.image, (*self.bright_color, 150), (local_sx, local_sy), int(start_glow * 0.5))
        pygame.draw.circle(self.image, self.core_color, (local_sx, local_sy), int(start_glow * 0.25))
        
        # 起点电弧射线
        for s in range(8):
            s_ang = s * 0.785 + self.lifetime * 0.8
            s_len = random.randint(20, 40)
            s_x = local_sx + int(math.cos(s_ang) * s_len)
            s_y = local_sy + int(math.sin(s_ang) * s_len)
            pygame.draw.line(self.image, (*self.color, 180), (local_sx, local_sy), (s_x, s_y), 3)
            pygame.draw.line(self.image, self.core_color, (local_sx, local_sy), (s_x, s_y), 1)
        
        # ========== 2. 生成多条主闪电路径 ==========
        all_paths = []
        for path_idx in range(3):  # 3条主闪电
            points = [(local_sx, local_sy)]
            if dist > 10:
                segments = min(15, max(6, int(dist / 15)))
                for i in range(1, segments):
                    progress = i / segments
                    # 大幅锯齿偏移
                    offset = int(35 * (1 - abs(progress - 0.5) * 1.5)) + path_idx * 8
                    px = local_sx + ldx * progress + random.randint(-offset, offset)
                    py = local_sy + ldy * progress + random.randint(-offset, offset)
                    points.append((int(px), int(py)))
            points.append((local_tx, local_ty))
            all_paths.append(points)
        
        # ========== 3. 绘制所有主闪电 ==========
        for path_idx, points in enumerate(all_paths):
            if len(points) < 2:
                continue
            
            # 主闪电粗细和透明度
            base_width = 20 - path_idx * 5  # 20, 15, 10
            base_alpha = 255 - path_idx * 40
            
            # 最外层 - 超大光晕
            for i in range(len(points) - 1):
                pygame.draw.line(self.image, (100, 50, 150, int(30 * flicker)), 
                               points[i], points[i + 1], base_width + 10)
            # 大光晕
            for i in range(len(points) - 1):
                pygame.draw.line(self.image, (*self.color, int(50 * flicker)), 
                               points[i], points[i + 1], base_width)
            # 中光晕
            for i in range(len(points) - 1):
                pygame.draw.line(self.image, (*self.color, int(100 * flicker)), 
                               points[i], points[i + 1], base_width - 6)
            # 亮色主体
            for i in range(len(points) - 1):
                pygame.draw.line(self.image, (*self.bright_color, int(base_alpha * flash)), 
                               points[i], points[i + 1], max(3, base_width - 12))
            # 白色核心
            for i in range(len(points) - 1):
                pygame.draw.line(self.image, self.core_color, 
                               points[i], points[i + 1], max(1, base_width - 16))
        
        # ========== 4. 大量分支闪电 ==========
        main_points = all_paths[0]
        for i, pt in enumerate(main_points[1:-1], 1):
            # 每个节点70%概率产生分支
            if random.random() < 0.7:
                branch_angle = math.atan2(ldy, ldx) + random.uniform(-1.5, 1.5)
                branch_len = random.randint(25, 60)
                branch_pts = [pt]
                bx, by = pt
                for seg in range(4):
                    bx += int(math.cos(branch_angle) * branch_len / 4 + random.randint(-10, 10))
                    by += int(math.sin(branch_angle) * branch_len / 4 + random.randint(-10, 10))
                    branch_pts.append((bx, by))
                
                # 绘制分支（多层）
                for j in range(len(branch_pts) - 1):
                    fade = 1 - j / len(branch_pts)
                    pygame.draw.line(self.image, (*self.color, int(80 * fade * flicker)), 
                                   branch_pts[j], branch_pts[j + 1], 8)
                    pygame.draw.line(self.image, (*self.bright_color, int(150 * fade * flicker)), 
                                   branch_pts[j], branch_pts[j + 1], 4)
                    pygame.draw.line(self.image, self.core_color, 
                                   branch_pts[j], branch_pts[j + 1], 1)
        
        # ========== 5. 电弧节点（更大更亮） ==========
        for pt in main_points[1:-1]:
            node_size = random.randint(6, 12)
            pygame.draw.circle(self.image, (*self.color, int(100 * flicker)), pt, node_size + 4)
            pygame.draw.circle(self.image, (*self.bright_color, int(180 * flicker)), pt, node_size)
            pygame.draw.circle(self.image, self.core_color, pt, node_size // 2)
        
        # ========== 6. 终点超大爆裂电弧 ==========
        end_glow = int(45 * flicker)
        pygame.draw.circle(self.image, (100, 50, 150, 35), (local_tx, local_ty), end_glow + 20)
        pygame.draw.circle(self.image, (*self.color, 60), (local_tx, local_ty), end_glow)
        pygame.draw.circle(self.image, (*self.bright_color, 120), (local_tx, local_ty), int(end_glow * 0.6))
        pygame.draw.circle(self.image, self.core_color, (local_tx, local_ty), int(end_glow * 0.3))
        
        # 终点大量电弧射线
        for spark in range(12):
            spark_angle = spark * 0.524 + self.lifetime * 0.6
            spark_len = random.randint(25, 50)
            # 锯齿状射线
            prev_x, prev_y = local_tx, local_ty
            for seg in range(3):
                seg_prog = (seg + 1) / 3
                next_x = local_tx + int(math.cos(spark_angle) * spark_len * seg_prog + random.randint(-8, 8))
                next_y = local_ty + int(math.sin(spark_angle) * spark_len * seg_prog + random.randint(-8, 8))
                alpha = int(200 * (1 - seg_prog) * flicker)
                pygame.draw.line(self.image, (*self.bright_color, alpha), (prev_x, prev_y), (next_x, next_y), 4)
                pygame.draw.line(self.image, self.core_color, (prev_x, prev_y), (next_x, next_y), 1)
                prev_x, prev_y = next_x, next_y
        
        # 起点光球
        pygame.draw.circle(self.image, (*self.color, 120), (local_sx, local_sy), 10)
        pygame.draw.circle(self.image, (255, 255, 255), (local_sx, local_sy), 4)
        
        # 终点光球
        pygame.draw.circle(self.image, (*self.color, 120), (local_tx, local_ty), 8)
        pygame.draw.circle(self.image, (255, 255, 255), (local_tx, local_ty), 3)
    
    def draw(self, surface):
        pass


# ============================================================
#   大招Ⅰ：禁忌篇章·暴风雪
# ============================================================
class BlizzardSkill(pygame.sprite.Sprite):
    """
    禁忌篇章·暴风雪 - 三阶段冰霜大招
    
    第一阶段 (1.5s): 魔法阵展开 - 书页飞舞形成魔法阵+冰霜扩散
    第二阶段 (3s):   暴风雪肆虐 - 全屏冰锥雨+雪花风暴+冻结光环
    第三阶段 (1.5s): 极寒终结 - 巨型冰柱爆裂+屏幕冻结
    """
    
    def __init__(self, x, y, owner=None, **kwargs):
        super().__init__()
        self.x = x
        self.y = y
        self.owner = owner
        self.damage = 35
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        all_sprites.add(self)
        
        # 阶段系统
        self.phase = 0  # 0=展开 1=肆虐 2=终结
        self.frame = 0
        self.phase_duration = [90, 180, 90]  # 每阶段帧数
        
        # 冰霜配色
        self.ice_blue = (100, 200, 255)
        self.frost_white = (220, 240, 255)
        self.deep_blue = (60, 120, 200)
        self.magic_purple = (160, 140, 255)
        
        # 书页系统
        self.pages = []
        
        # 冰锥系统
        self.ice_shards = []
        
        # 雪花系统
        self.snowflakes = []
        
        # 粒子系统
        self.particles = []
        
        # 魔法阵
        self.circle_radius = 0
        self.rune_rings = []
        
        # 巨型冰柱
        self.ice_pillars = []
        
        # 冻结效果
        self.freeze_duration = 300  # 5秒冻结
        
        # 屏幕震动
        self.screen_shake = 0
    
    def _add_particle(self, x, y, vx, vy, color, life, size=3):
        """添加粒子"""
        self.particles.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color, 'life': life, 'max_life': life, 'size': size
        })
    
    def _update_particles(self):
        """更新粒子"""
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            alpha = int(255 * p['life'] / p['max_life'])
            size = max(1, int(p['size'] * p['life'] / p['max_life']))
            pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                             (int(p['x']), int(p['y'])), size)
    
    def _phase0_formation(self):
        """第一阶段：魔法阵展开"""
        self.image.fill((0, 0, 0, 0))
        progress = self.frame / self.phase_duration[0]
        
        # 背景冷却
        cold_alpha = int(40 * progress)
        pygame.draw.rect(self.image, (10, 20, 40, cold_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 书页飞舞 - 从玩家位置飞出形成圆阵
        if self.frame % 4 == 0 and len(self.pages) < 24:
            angle = len(self.pages) * (360 / 24)
            self.pages.append({
                'angle': angle,
                'dist': 0,
                'target_dist': 120 + random.uniform(-20, 20),
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-8, 8),
                'flutter': random.uniform(0, 6.28),
            })
        
        # 更新书页
        cx, cy = self.x, self.y
        for page in self.pages:
            if page['dist'] < page['target_dist']:
                page['dist'] += 6
            page['rotation'] += page['rot_speed']
            page['flutter'] += 0.15
            
            flutter = math.sin(page['flutter']) * 8
            rad = math.radians(page['angle'] + self.frame * 0.5)
            px = cx + math.cos(rad) * (page['dist'] + flutter)
            py = cy + math.sin(rad) * (page['dist'] + flutter)
            
            # 绘制书页
            page_surf = pygame.Surface((20, 26), pygame.SRCALPHA)
            pygame.draw.rect(page_surf, (240, 235, 220, 200), (0, 0, 20, 26))
            pygame.draw.rect(page_surf, self.magic_purple, (0, 0, 20, 26), 1)
            # 书页上的符文线
            for line in range(4):
                pygame.draw.line(page_surf, (*self.ice_blue, 100),
                               (3, 4 + line * 6), (17, 4 + line * 6), 1)
            rotated = pygame.transform.rotate(page_surf, page['rotation'])
            self.image.blit(rotated, (int(px) - rotated.get_width()//2,
                                      int(py) - rotated.get_height()//2))
            
            # 冰霜拖尾
            self._add_particle(px + random.uniform(-5, 5), py + random.uniform(-5, 5),
                             random.uniform(-1, 1), random.uniform(-2, 0),
                             self.frost_white, 15, 3)
        
        # 魔法阵逐渐展开
        self.circle_radius = int(150 * progress)
        if self.circle_radius > 0:
            # 外圈
            pygame.draw.circle(self.image, (*self.ice_blue, 150), (int(cx), int(cy)),
                             self.circle_radius, 3)
            # 内圈
            pygame.draw.circle(self.image, (*self.magic_purple, 100), (int(cx), int(cy)),
                             int(self.circle_radius * 0.6), 2)
            
            # 符文点
            for i in range(12):
                rune_angle = self.frame * 0.8 + i * 30
                rx = cx + math.cos(math.radians(rune_angle)) * self.circle_radius
                ry = cy + math.sin(math.radians(rune_angle)) * self.circle_radius
                pygame.draw.circle(self.image, self.frost_white, (int(rx), int(ry)), 4)
                pygame.draw.circle(self.image, self.ice_blue, (int(rx), int(ry)), 2)
        
        # 中心能量聚集
        core_pulse = abs(math.sin(self.frame * 0.2))
        core_r = int(20 + core_pulse * 15)
        for i in range(3):
            pygame.draw.circle(self.image, (*self.ice_blue, 80 - i * 25),
                             (int(cx), int(cy)), core_r + i * 10)
        pygame.draw.circle(self.image, self.frost_white, (int(cx), int(cy)), 8)
        
        self._update_particles()
    
    def _phase1_blizzard(self):
        """第二阶段：暴风雪肆虐"""
        self.image.fill((0, 0, 0, 0))
        progress = self.frame / self.phase_duration[1]
        
        # 全屏暴风雪效果
        storm_alpha = int(50 + 20 * math.sin(self.frame * 0.1))
        pygame.draw.rect(self.image, (20, 40, 60, storm_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 生成冰锥
        if self.frame % 2 == 0:
            for _ in range(8):
                shard = {
                    'x': random.randint(-50, WIDTH + 50),
                    'y': random.randint(-80, -20),
                    'vx': random.uniform(-3, 3),
                    'vy': random.uniform(10, 18),
                    'size': random.randint(12, 22),
                    'rotation': random.uniform(-30, 30),
                    'lifetime': 0,
                }
                self.ice_shards.append(shard)
        
        # 生成雪花
        if self.frame % 3 == 0:
            for _ in range(15):
                self.snowflakes.append({
                    'x': random.randint(0, WIDTH),
                    'y': random.randint(-20, 0),
                    'vx': random.uniform(-4, -1),  # 向左风吹
                    'vy': random.uniform(3, 7),
                    'size': random.randint(2, 5),
                    'rotation': random.uniform(0, 360),
                    'rot_speed': random.uniform(-5, 5),
                })
        
        # 更新雪花
        for flake in self.snowflakes[:]:
            flake['x'] += flake['vx']
            flake['y'] += flake['vy']
            flake['rotation'] += flake['rot_speed']
            
            if flake['y'] > HEIGHT or flake['x'] < -20:
                self.snowflakes.remove(flake)
                continue
            
            # 绘制雪花（六角形）
            fx, fy = int(flake['x']), int(flake['y'])
            r = flake['size']
            for i in range(6):
                angle = math.radians(flake['rotation'] + i * 60)
                ex = fx + math.cos(angle) * r
                ey = fy + math.sin(angle) * r
                pygame.draw.line(self.image, (*self.frost_white, 180),
                               (fx, fy), (int(ex), int(ey)), 1)
        
        # 更新冰锥
        for shard in self.ice_shards[:]:
            shard['x'] += shard['vx']
            shard['y'] += shard['vy']
            shard['lifetime'] += 1
            
            if shard['y'] > HEIGHT + 50:
                self.ice_shards.remove(shard)
                continue
            
            # 绘制冰锥（精细版）
            sx, sy = int(shard['x']), int(shard['y'])
            size = shard['size']
            alpha = max(0, 220 - shard['lifetime'] * 2)
            
            # 冰锥外层光晕
            pygame.draw.polygon(self.image, (*self.deep_blue, alpha // 3), [
                (sx, sy - size),
                (sx - size // 2 - 4, sy + size),
                (sx + size // 2 + 4, sy + size),
            ])
            
            # 冰锥主体
            pygame.draw.polygon(self.image, (*self.ice_blue, alpha), [
                (sx, sy - size),
                (sx - size // 2, sy + size),
                (sx + size // 2, sy + size),
            ])
            
            # 冰锥高光
            pygame.draw.line(self.image, (*self.frost_white, alpha),
                           (sx - 2, sy - size + 4), (sx - size // 4, sy + size // 2), 2)
            
            # 冰锥边缘
            pygame.draw.polygon(self.image, (*self.frost_white, alpha // 2), [
                (sx, sy - size),
                (sx - size // 2, sy + size),
                (sx + size // 2, sy + size),
            ], 1)
        
        # 冻结光环 - 从中心扩散
        cx, cy = self.x, self.y
        pulse_r = 80 + int(math.sin(self.frame * 0.15) * 30)
        for i in range(3):
            ring_r = pulse_r + i * 40
            ring_alpha = 100 - i * 30
            pygame.draw.circle(self.image, (*self.ice_blue, ring_alpha),
                             (int(cx), int(cy)), ring_r, 2)
        
        # 持续冻结敌人
        if self.frame % 20 == 0:
            for enemy in mobs:
                if hasattr(enemy, 'hp'):
                    enemy.hp -= self.damage * 0.3
                if hasattr(enemy, 'frozen_timer') and not getattr(enemy, 'is_boss', False):
                    enemy.frozen_timer = max(getattr(enemy, 'frozen_timer', 0), 60)
                # 命中特效
                self._add_particle(enemy.rect.centerx, enemy.rect.centery,
                                 random.uniform(-3, 3), random.uniform(-5, 0),
                                 self.ice_blue, 20, 4)
        
        self._update_particles()
    
    def _phase2_finale(self):
        """第三阶段：极寒终结"""
        self.image.fill((0, 0, 0, 0))
        progress = self.frame / self.phase_duration[2]
        
        # 全屏冻结闪烁
        if progress < 0.3:
            flash_alpha = int(200 * (1 - progress / 0.3))
            pygame.draw.rect(self.image, (*self.frost_white, flash_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 生成巨型冰柱（只在开始时）
        if self.frame == 1:
            for _ in range(5):
                self.ice_pillars.append({
                    'x': random.randint(100, 700),
                    'y': HEIGHT + 50,
                    'target_y': random.randint(200, 400),
                    'width': random.randint(40, 70),
                    'height': 0,
                    'max_height': random.randint(200, 350),
                    'shatter_timer': 0,
                    'shattered': False,
                })
        
        # 更新冰柱
        for pillar in self.ice_pillars:
            if not pillar['shattered']:
                if pillar['height'] < pillar['max_height']:
                    pillar['height'] += 15
                else:
                    pillar['shatter_timer'] += 1
                    if pillar['shatter_timer'] > 30:
                        pillar['shattered'] = True
                        # 爆炸特效
                        cx = pillar['x']
                        cy = pillar['target_y']
                        for _ in range(40):
                            angle = random.uniform(0, 6.28)
                            speed = random.uniform(3, 12)
                            self._add_particle(cx, cy,
                                             math.cos(angle) * speed,
                                             math.sin(angle) * speed,
                                             self.ice_blue, 40, random.randint(3, 8))
                        # 爆炸伤害
                        for enemy in mobs:
                            dist = math.hypot(enemy.rect.centerx - cx, enemy.rect.centery - cy)
                            if dist < 150:
                                enemy.hp -= self.damage * 1.5
                                if hasattr(enemy, 'frozen_timer') and not getattr(enemy, 'is_boss', False):
                                    enemy.frozen_timer = self.freeze_duration
            
            # 绘制冰柱
            if not pillar['shattered']:
                px, py = int(pillar['x']), int(pillar['target_y'])
                w, h = pillar['width'], int(pillar['height'])
                
                # 冰柱外层光晕
                for i in range(3):
                    glow_w = w + i * 10
                    glow_alpha = 60 - i * 20
                    pygame.draw.polygon(self.image, (*self.deep_blue, glow_alpha), [
                        (px - glow_w // 2, py + h // 2),
                        (px, py - h // 2),
                        (px + glow_w // 2, py + h // 2),
                    ])
                
                # 冰柱主体
                pygame.draw.polygon(self.image, (*self.ice_blue, 220), [
                    (px - w // 2, py + h // 2),
                    (px - w // 4, py - h // 2),
                    (px + w // 4, py - h // 2),
                    (px + w // 2, py + h // 2),
                ])
                
                # 冰柱纹理
                for i in range(5):
                    line_y = py - h // 2 + i * (h // 5)
                    line_w = w * (0.8 - i * 0.1)
                    pygame.draw.line(self.image, (*self.frost_white, 100),
                                   (int(px - line_w // 2), int(line_y)),
                                   (int(px + line_w // 2), int(line_y)), 1)
                
                # 顶端尖刺光
                pygame.draw.circle(self.image, (*self.frost_white, 200),
                                 (px, py - h // 2), 8)
                
                # 震动
                if pillar['shatter_timer'] > 0:
                    shake = int(math.sin(pillar['shatter_timer'] * 0.8) * 3)
                    self.screen_shake = shake
        
        # 继续更新残留粒子
        self._update_particles()
        
        # 背景逐渐恢复
        if progress > 0.7:
            fade = (progress - 0.7) / 0.3
            pygame.draw.rect(self.image, (20, 40, 60, int(50 * (1 - fade))), (0, 0, WIDTH, HEIGHT))
    
    def update(self):
        """更新暴风雪大招"""
        self.frame += 1
        
        if self.phase == 0:
            self._phase0_formation()
            if self.frame >= self.phase_duration[0]:
                self.phase = 1
                self.frame = 0
                self.pages.clear()
        
        elif self.phase == 1:
            self._phase1_blizzard()
            if self.frame >= self.phase_duration[1]:
                self.phase = 2
                self.frame = 0
                self.ice_shards.clear()
                self.snowflakes.clear()
        
        elif self.phase == 2:
            self._phase2_finale()
            if self.frame >= self.phase_duration[2]:
                self.kill()
    
    def _render(self):
        pass  # 各阶段方法直接渲染
    
    def draw(self, surface):
        pass  # 使用 image/rect 系统


# ============================================================
#   大招Ⅱ：召唤·远古之灵
# ============================================================
class AncientSpiritSkill(pygame.sprite.Sprite):
    """
    召唤·远古之灵 - 三阶段召唤大招
    
    第一阶段 (1.5s): 禁书开启 - 书页翻飞+暗紫能量涌动+召唤阵展开
    第二阶段 (3.5s): 灵魂降临 - 巨型骷髅头显现+追踪冲撞+骨龙环绕
    第三阶段 (1.5s): 亡者之歌 - 灵魂爆发+死亡领域+灵魂碎片飞散
    """
    
    def __init__(self, x, y, owner=None, **kwargs):
        super().__init__()
        self.x = x
        self.y = y
        self.owner = owner
        self.damage = 90
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        all_sprites.add(self)
        
        # 阶段系统
        self.phase = 0
        self.frame = 0
        self.phase_duration = [90, 210, 90]
        
        # 配色
        self.dark_purple = (80, 40, 120)
        self.spirit_purple = (180, 100, 255)
        self.soul_blue = (100, 150, 255)
        self.bone_white = (240, 235, 220)
        self.death_green = (100, 200, 150)
        
        # 书页
        self.pages = []
        
        # 召唤阵
        self.summon_circle_radius = 0
        self.rune_rotation = 0
        
        # 骷髅头
        self.skull_x = x
        self.skull_y = y
        self.skull_size = 0
        self.skull_eye_glow = 0
        self.skull_target = None
        
        # 骨龙
        self.bone_dragons = []
        
        # 粒子
        self.particles = []
        self.soul_fragments = []
        
        # 击中敌人
        self.hit_enemies = set()
    
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
            size = max(1, int(p['size'] * p['life'] / p['max_life']))
            pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                             (int(p['x']), int(p['y'])), size)
    
    def _phase0_summon(self):
        """第一阶段：禁书开启"""
        self.image.fill((0, 0, 0, 0))
        progress = self.frame / self.phase_duration[0]
        
        # 背景黑暗化
        dark_alpha = int(60 * progress)
        pygame.draw.rect(self.image, (20, 10, 30, dark_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 生成书页
        if self.frame % 3 == 0 and len(self.pages) < 30:
            self.pages.append({
                'x': self.x + random.uniform(-20, 20),
                'y': self.y + random.uniform(-20, 20),
                'angle': random.uniform(0, 360),
                'dist': 0,
                'target_dist': random.uniform(80, 180),
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-10, 10),
                'flutter': random.uniform(0, 6.28),
            })
        
        # 更新书页
        cx, cy = self.x, self.y
        for page in self.pages:
            page['dist'] = min(page['dist'] + 4, page['target_dist'])
            page['rotation'] += page['rot_speed']
            page['flutter'] += 0.2
            
            rad = math.radians(page['angle'] + self.frame * 0.3)
            flutter = math.sin(page['flutter']) * 10
            px = cx + math.cos(rad) * (page['dist'] + flutter)
            py = cy + math.sin(rad) * (page['dist'] + flutter)
            
            # 绘制暗黑书页
            page_surf = pygame.Surface((24, 30), pygame.SRCALPHA)
            pygame.draw.rect(page_surf, (*self.bone_white, 180), (0, 0, 24, 30))
            # 禁忌符文
            for i in range(4):
                pygame.draw.line(page_surf, (*self.spirit_purple, 150),
                               (4, 5 + i * 7), (20, 5 + i * 7), 1)
            pygame.draw.rect(page_surf, (*self.spirit_purple, 100), (0, 0, 24, 30), 1)
            rotated = pygame.transform.rotate(page_surf, page['rotation'])
            self.image.blit(rotated, (int(px) - rotated.get_width()//2,
                                      int(py) - rotated.get_height()//2))
            
            # 暗能量拖尾
            self._add_particle(px, py, random.uniform(-1, 1), random.uniform(-2, 0),
                             self.spirit_purple, 15, 3)
        
        # 召唤阵展开
        self.summon_circle_radius = int(150 * progress)
        self.rune_rotation += 1.5
        
        if self.summon_circle_radius > 0:
            # 多层召唤阵
            for ring in range(3):
                ring_r = self.summon_circle_radius - ring * 30
                if ring_r > 0:
                    ring_alpha = 180 - ring * 50
                    pygame.draw.circle(self.image, (*self.spirit_purple, ring_alpha),
                                     (int(cx), int(cy)), ring_r, 2)
            
            # 旋转符文
            for i in range(8):
                rune_angle = self.rune_rotation + i * 45
                rx = cx + math.cos(math.radians(rune_angle)) * self.summon_circle_radius
                ry = cy + math.sin(math.radians(rune_angle)) * self.summon_circle_radius
                
                # 符文点 + 连线
                pygame.draw.circle(self.image, self.bone_white, (int(rx), int(ry)), 5)
                pygame.draw.circle(self.image, self.spirit_purple, (int(rx), int(ry)), 3)
                pygame.draw.line(self.image, (*self.spirit_purple, 80),
                               (int(cx), int(cy)), (int(rx), int(ry)), 1)
            
            # 五芒星
            star_r = self.summon_circle_radius * 0.7
            for i in range(5):
                angle1 = self.rune_rotation * 0.5 + i * 72 - 90
                angle2 = self.rune_rotation * 0.5 + ((i + 2) % 5) * 72 - 90
                p1 = (int(cx + math.cos(math.radians(angle1)) * star_r),
                      int(cy + math.sin(math.radians(angle1)) * star_r))
                p2 = (int(cx + math.cos(math.radians(angle2)) * star_r),
                      int(cy + math.sin(math.radians(angle2)) * star_r))
                pygame.draw.line(self.image, (*self.death_green, 150), p1, p2, 2)
        
        # 中心能量核心
        core_pulse = abs(math.sin(self.frame * 0.15))
        core_r = int(15 + core_pulse * 20)
        for i in range(4):
            pygame.draw.circle(self.image, (*self.spirit_purple, 100 - i * 25),
                             (int(cx), int(cy)), core_r + i * 8)
        
        self._update_particles()
    
    def _phase1_descent(self):
        """第二阶段：灵魂降临"""
        self.image.fill((0, 0, 0, 0))
        progress = self.frame / self.phase_duration[1]
        
        # 深渊背景
        pygame.draw.rect(self.image, (15, 8, 25, 70), (0, 0, WIDTH, HEIGHT))
        
        # 骷髅头逐渐显现
        if self.skull_size < 100:
            self.skull_size += 3
        self.skull_eye_glow = min(1, self.skull_eye_glow + 0.03)
        
        # 生成骨龙（只在开始时）
        if self.frame == 1:
            for i in range(4):
                self.bone_dragons.append({
                    'angle': i * 90,
                    'dist': 80,
                    'segments': [],
                    'phase_offset': random.uniform(0, 6.28),
                })
        
        # 寻找目标
        if self.skull_target is None or (hasattr(self.skull_target, 'hp') and self.skull_target.hp <= 0):
            min_dist = float('inf')
            for enemy in mobs:
                dx = enemy.rect.centerx - self.skull_x
                dy = enemy.rect.centery - self.skull_y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < min_dist:
                    min_dist = dist
                    self.skull_target = enemy
        
        # 骷髅头追踪移动
        if self.skull_target and hasattr(self.skull_target, 'rect'):
            dx = self.skull_target.rect.centerx - self.skull_x
            dy = self.skull_target.rect.centery - self.skull_y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 5:
                speed = 8 + progress * 6
                self.skull_x += (dx / dist) * speed
                self.skull_y += (dy / dist) * speed
            
            # 碰撞检测
            if dist < self.skull_size * 0.8:
                if id(self.skull_target) not in self.hit_enemies:
                    self.skull_target.hp -= self.damage
                    self.hit_enemies.add(id(self.skull_target))
                    # 命中爆炸
                    for _ in range(20):
                        angle = random.uniform(0, 6.28)
                        speed = random.uniform(4, 10)
                        self._add_particle(self.skull_x, self.skull_y,
                                         math.cos(angle) * speed, math.sin(angle) * speed,
                                         self.spirit_purple, 25, 5)
                    self.skull_target = None
        
        # 绘制骷髅头
        sx, sy = int(self.skull_x), int(self.skull_y)
        size = int(self.skull_size)
        t = self.frame * 0.1
        pulse = 0.9 + 0.1 * math.sin(t * 4)
        size = int(size * pulse)
        
        # 骷髅头光晕
        for i in range(5):
            glow_r = size + i * 15
            glow_alpha = 60 - i * 12
            pygame.draw.circle(self.image, (*self.dark_purple, glow_alpha),
                             (sx, sy), glow_r)
        
        # 骷髅头主体
        pygame.draw.circle(self.image, self.spirit_purple, (sx, sy), size)
        pygame.draw.circle(self.image, (*self.bone_white, 60), (sx, sy), size, 3)
        
        # 眼眶（发光）
        eye_offset = size // 3
        eye_size = size // 4
        for side in [-1, 1]:
            ex = sx + side * eye_offset
            ey = sy - size // 6
            # 眼眶黑洞
            pygame.draw.circle(self.image, (0, 0, 0), (ex, ey), eye_size)
            # 眼睛发光
            glow_intensity = int(255 * self.skull_eye_glow)
            pygame.draw.circle(self.image, (*self.death_green, glow_intensity),
                             (ex, ey), int(eye_size * 0.6))
            # 眼睛核心
            pygame.draw.circle(self.image, (255, 255, 200, glow_intensity),
                             (ex, ey), int(eye_size * 0.3))
        
        # 鼻孔
        nose_y = sy + size // 8
        pygame.draw.polygon(self.image, (0, 0, 0, 200), [
            (sx, nose_y - size // 8),
            (sx - size // 8, nose_y + size // 8),
            (sx + size // 8, nose_y + size // 8),
        ])
        
        # 牙齿
        jaw_y = sy + size // 2
        for tooth in range(6):
            tooth_x = sx - size // 2 + tooth * size // 5 + size // 10
            pygame.draw.rect(self.image, self.bone_white,
                           (tooth_x - size // 12, jaw_y - size // 5,
                            size // 6, size // 4))
        
        # 骨龙环绕
        for dragon in self.bone_dragons:
            dragon['angle'] += 2
            rad = math.radians(dragon['angle'])
            dragon_x = sx + math.cos(rad) * dragon['dist']
            dragon_y = sy + math.sin(rad) * dragon['dist']
            
            # 骨龙蜿蜒
            segments = 8
            points = []
            for i in range(segments):
                prog = i / (segments - 1)
                wave = math.sin(self.frame * 0.15 + prog * 4 + dragon['phase_offset']) * 12
                seg_x = dragon_x + math.cos(rad + math.pi) * i * 8 + wave * math.sin(rad)
                seg_y = dragon_y + math.sin(rad + math.pi) * i * 8 + wave * math.cos(rad)
                points.append((int(seg_x), int(seg_y)))
            
            if len(points) >= 2:
                # 骨龙身体
                for i in range(len(points) - 1):
                    thick = 6 - i // 2
                    pygame.draw.line(self.image, self.bone_white, points[i], points[i + 1], max(1, thick))
                
                # 骨龙头
                head_x, head_y = int(dragon_x), int(dragon_y)
                pygame.draw.circle(self.image, self.bone_white, (head_x, head_y), 8)
                pygame.draw.circle(self.image, self.death_green, (head_x, head_y), 4)
            
            # 骨龙攻击
            if self.frame % 30 == 0:
                for enemy in mobs:
                    if math.hypot(enemy.rect.centerx - dragon_x, enemy.rect.centery - dragon_y) < 60:
                        enemy.hp -= self.damage * 0.3
        
        # 死亡领域波动
        wave_r = 120 + int(math.sin(self.frame * 0.08) * 30)
        pygame.draw.circle(self.image, (*self.spirit_purple, 40), (sx, sy), wave_r, 3)
        
        self._update_particles()
    
    def _phase2_finale(self):
        """第三阶段：亡者之歌"""
        self.image.fill((0, 0, 0, 0))
        progress = self.frame / self.phase_duration[2]
        
        # 爆发闪光
        if progress < 0.2:
            flash_alpha = int(180 * (1 - progress / 0.2))
            pygame.draw.rect(self.image, (*self.spirit_purple, flash_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 灵魂碎片飞散
        if self.frame == 1:
            for _ in range(50):
                angle = random.uniform(0, 6.28)
                speed = random.uniform(5, 15)
                self.soul_fragments.append({
                    'x': self.skull_x,
                    'y': self.skull_y,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'size': random.randint(4, 12),
                    'rotation': random.uniform(0, 360),
                    'life': random.randint(40, 80),
                })
        
        # 更新灵魂碎片
        for frag in self.soul_fragments[:]:
            frag['x'] += frag['vx']
            frag['y'] += frag['vy']
            frag['vx'] *= 0.97
            frag['vy'] *= 0.97
            frag['rotation'] += 5
            frag['life'] -= 1
            
            if frag['life'] <= 0:
                self.soul_fragments.remove(frag)
                continue
            
            alpha = int(255 * frag['life'] / 80)
            size = frag['size']
            fx, fy = int(frag['x']), int(frag['y'])
            
            # 灵魂碎片（三角形）
            points = []
            for i in range(3):
                angle = math.radians(frag['rotation'] + i * 120)
                points.append((fx + math.cos(angle) * size, fy + math.sin(angle) * size))
            pygame.draw.polygon(self.image, (*self.spirit_purple, alpha), points)
            pygame.draw.polygon(self.image, (*self.bone_white, alpha // 2), points, 1)
        
        # 死亡领域扩散
        death_r = int(300 * progress)
        for i in range(3):
            ring_r = death_r - i * 30
            if ring_r > 0:
                ring_alpha = int(80 * (1 - progress) * (1 - i * 0.3))
                pygame.draw.circle(self.image, (*self.spirit_purple, ring_alpha),
                                 (int(self.skull_x), int(self.skull_y)), ring_r, 3)
        
        # 范围伤害
        if self.frame % 10 == 0:
            for enemy in mobs:
                dist = math.hypot(enemy.rect.centerx - self.skull_x, enemy.rect.centery - self.skull_y)
                if dist < death_r:
                    enemy.hp -= self.damage * 0.4
        
        self._update_particles()
    
    def update(self):
        self.frame += 1
        
        if self.phase == 0:
            self._phase0_summon()
            if self.frame >= self.phase_duration[0]:
                self.phase = 1
                self.frame = 0
                self.pages.clear()
        
        elif self.phase == 1:
            self._phase1_descent()
            if self.frame >= self.phase_duration[1]:
                self.phase = 2
                self.frame = 0
        
        elif self.phase == 2:
            self._phase2_finale()
            if self.frame >= self.phase_duration[2]:
                self.kill()
    
    def _render(self):
        pass
    
    def draw(self, surface):
        pass


# ============================================================
#   大招Ⅲ：真理之圆
# ============================================================
class CircleOfTruthSkill(pygame.sprite.Sprite):
    """
    真理之圆 - 三阶段终极大招
    
    第一阶段 (1s):   禁书封印 - 书页收拢+能量压缩+黑暗笼罩
    第二阶段 (1.5s): 真理爆发 - 书页爆散+魔法阵展开+光柱升腾
    第三阶段 (4s):   审判领域 - 符文环旋转+真理之眼+持续灼烧+最终审判
    """
    
    def __init__(self, x, y, owner=None, **kwargs):
        super().__init__()
        self.x = x
        self.y = y
        self.owner = owner
        self.damage = 20
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        all_sprites.add(self)
        
        # 阶段系统
        self.phase = 0
        self.frame = 0
        self.phase_duration = [60, 90, 240]
        
        # 配色
        self.holy_gold = (255, 215, 100)
        self.pure_white = (255, 250, 240)
        self.divine_blue = (100, 180, 255)
        self.truth_purple = (200, 150, 255)
        self.page_color = (245, 235, 220)
        
        # 书页
        self.pages = []
        
        # 魔法阵
        self.center_x = WIDTH // 2
        self.center_y = HEIGHT // 2
        self.circle_radius = 0
        self.max_radius = 280
        self.rune_rings = []
        
        # 真理之眼
        self.eye_open = 0
        self.eye_target = None
        
        # 光柱
        self.light_pillars = []
        
        # 粒子
        self.particles = []
        
        # 符文文字
        self.floating_runes = []
    
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
            size = max(1, int(p['size'] * p['life'] / p['max_life']))
            pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                             (int(p['x']), int(p['y'])), size)
    
    def _phase0_seal(self):
        """第一阶段：禁书封印"""
        self.image.fill((0, 0, 0, 0))
        progress = self.frame / self.phase_duration[0]
        
        # 黑暗笼罩
        dark_alpha = int(80 * progress)
        pygame.draw.rect(self.image, (10, 5, 20, dark_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 生成收拢的书页
        if self.frame % 2 == 0 and len(self.pages) < 40:
            angle = random.uniform(0, 360)
            dist = 300 + random.uniform(-50, 50)
            self.pages.append({
                'angle': angle,
                'dist': dist,
                'target_dist': 30,
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-15, 15),
            })
        
        # 更新书页 - 向中心收拢
        cx, cy = self.x, self.y
        for page in self.pages:
            page['dist'] = max(page['target_dist'], page['dist'] - 8)
            page['rotation'] += page['rot_speed']
            
            rad = math.radians(page['angle'])
            px = cx + math.cos(rad) * page['dist']
            py = cy + math.sin(rad) * page['dist']
            
            # 绘制书页
            page_surf = pygame.Surface((20, 26), pygame.SRCALPHA)
            alpha = int(200 * (1 - progress * 0.5))
            pygame.draw.rect(page_surf, (*self.page_color, alpha), (0, 0, 20, 26))
            pygame.draw.rect(page_surf, (*self.holy_gold, alpha // 2), (0, 0, 20, 26), 1)
            rotated = pygame.transform.rotate(page_surf, page['rotation'])
            self.image.blit(rotated, (int(px) - rotated.get_width()//2,
                                      int(py) - rotated.get_height()//2))
        
        # 能量压缩光环
        compress_r = int(150 * (1 - progress))
        for i in range(3):
            ring_r = compress_r + i * 20
            ring_alpha = int(100 * progress)
            pygame.draw.circle(self.image, (*self.holy_gold, ring_alpha),
                             (int(cx), int(cy)), ring_r, 2)
        
        # 中心能量核心（越来越亮）
        core_intensity = progress
        core_r = int(20 + 30 * core_intensity)
        for i in range(4):
            glow_r = core_r + i * 10
            glow_alpha = int(200 * core_intensity * (1 - i * 0.25))
            pygame.draw.circle(self.image, (*self.pure_white, glow_alpha),
                             (int(cx), int(cy)), glow_r)
        
        self._update_particles()
    
    def _phase1_explosion(self):
        """第二阶段：真理爆发"""
        self.image.fill((0, 0, 0, 0))
        progress = self.frame / self.phase_duration[1]
        
        # 背景神圣光芒
        if progress < 0.3:
            flash = int(200 * (1 - progress / 0.3))
            pygame.draw.rect(self.image, (*self.pure_white, flash), (0, 0, WIDTH, HEIGHT))
        
        pygame.draw.rect(self.image, (20, 15, 35, 60), (0, 0, WIDTH, HEIGHT))
        
        cx, cy = self.center_x, self.center_y
        
        # 书页爆散
        for page in self.pages:
            page['dist'] += 12
            page['rotation'] += page['rot_speed'] * 1.5
            
            if page['dist'] > 400:
                continue
            
            rad = math.radians(page['angle'])
            px = self.x + math.cos(rad) * page['dist']
            py = self.y + math.sin(rad) * page['dist']
            
            alpha = max(0, int(200 * (1 - page['dist'] / 400)))
            if alpha > 0:
                page_surf = pygame.Surface((20, 26), pygame.SRCALPHA)
                pygame.draw.rect(page_surf, (*self.page_color, alpha), (0, 0, 20, 26))
                pygame.draw.rect(page_surf, (*self.holy_gold, alpha // 2), (0, 0, 20, 26), 1)
                rotated = pygame.transform.rotate(page_surf, page['rotation'])
                self.image.blit(rotated, (int(px) - rotated.get_width()//2,
                                          int(py) - rotated.get_height()//2))
            
            # 光粒子
            if self.frame % 3 == 0:
                self._add_particle(px, py, random.uniform(-2, 2), random.uniform(-2, 2),
                                 self.holy_gold, 20, 3)
        
        # 魔法阵展开
        self.circle_radius = int(self.max_radius * progress)
        
        if self.circle_radius > 0:
            # 多层魔法阵
            for ring in range(4):
                ring_r = self.circle_radius - ring * 40
                if ring_r > 0:
                    ring_alpha = 180 - ring * 40
                    pygame.draw.circle(self.image, (*self.holy_gold, ring_alpha),
                                     (cx, cy), ring_r, 2 + ring)
            
            # 八芒星
            star_r = self.circle_radius * 0.8
            for i in range(8):
                angle1 = i * 45 + self.frame * 0.5
                angle2 = ((i + 3) % 8) * 45 + self.frame * 0.5
                p1 = (int(cx + math.cos(math.radians(angle1)) * star_r),
                      int(cy + math.sin(math.radians(angle1)) * star_r))
                p2 = (int(cx + math.cos(math.radians(angle2)) * star_r),
                      int(cy + math.sin(math.radians(angle2)) * star_r))
                pygame.draw.line(self.image, (*self.divine_blue, 150), p1, p2, 2)
        
        # 光柱升腾
        if progress > 0.5:
            beam_h = int((progress - 0.5) * 2 * HEIGHT)
            beam_w = 60
            for i in range(3):
                layer_w = beam_w - i * 15
                layer_alpha = 150 - i * 40
                pygame.draw.rect(self.image, (*self.pure_white, layer_alpha),
                               (cx - layer_w // 2, cy - beam_h, layer_w, beam_h * 2))
        
        self._update_particles()
    
    def _phase2_judgment(self):
        """第三阶段：审判领域"""
        self.image.fill((0, 0, 0, 0))
        progress = self.frame / self.phase_duration[2]
        
        # 神圣背景
        pygame.draw.rect(self.image, (15, 12, 30, 50), (0, 0, WIDTH, HEIGHT))
        
        cx, cy = self.center_x, self.center_y
        t = self.frame * 0.1
        
        # 初始化符文环
        if self.frame == 1:
            for i in range(4):
                self.rune_rings.append({
                    'radius': 60 + i * 60,
                    'rotation': 0,
                    'speed': 0.8 * (1 if i % 2 == 0 else -1),
                    'runes': 6 + i * 2,
                })
        
        # 魔法阵底层光晕
        for i in range(5):
            glow_r = self.max_radius - i * 30
            glow_alpha = 30 - i * 5
            pygame.draw.circle(self.image, (*self.holy_gold, glow_alpha), (cx, cy), glow_r)
        
        # 更新并绘制符文环
        for ring in self.rune_rings:
            ring['rotation'] += ring['speed']
            
            # 环
            pygame.draw.circle(self.image, (*self.holy_gold, 80), (cx, cy), ring['radius'], 2)
            
            # 符文点
            for i in range(ring['runes']):
                rune_angle = ring['rotation'] + i * (360 / ring['runes'])
                rx = cx + math.cos(math.radians(rune_angle)) * ring['radius']
                ry = cy + math.sin(math.radians(rune_angle)) * ring['radius']
                
                pulse = 0.7 + 0.3 * math.sin(t * 3 + i)
                rune_size = int(8 * pulse)
                
                # 符文光点
                for j in range(2):
                    glow_size = rune_size + j * 4
                    glow_alpha = int(180 * pulse * (1 - j * 0.4))
                    pygame.draw.circle(self.image, (*self.holy_gold, glow_alpha),
                                     (int(rx), int(ry)), glow_size)
                pygame.draw.circle(self.image, (*self.pure_white, int(220 * pulse)),
                                 (int(rx), int(ry)), rune_size // 2)
                
                # 符文连线
                if i > 0:
                    prev_angle = ring['rotation'] + (i - 1) * (360 / ring['runes'])
                    prev_x = cx + math.cos(math.radians(prev_angle)) * ring['radius']
                    prev_y = cy + math.sin(math.radians(prev_angle)) * ring['radius']
                    pygame.draw.line(self.image, (*self.divine_blue, 60),
                                   (int(prev_x), int(prev_y)), (int(rx), int(ry)), 1)
        
        # 真理之眼（中心）
        self.eye_open = min(1, self.eye_open + 0.02)
        eye_r = 50
        
        # 眼部光晕
        for i in range(4):
            pygame.draw.circle(self.image, (*self.truth_purple, 40 - i * 10),
                             (cx, cy), eye_r + 20 + i * 15)
        
        # 眼白
        eye_h = int(eye_r * 0.8 * self.eye_open)
        if eye_h > 0:
            pygame.draw.ellipse(self.image, self.pure_white,
                              (cx - eye_r, cy - eye_h, eye_r * 2, eye_h * 2))
        
        # 寻找目标
        if self.eye_target is None or (hasattr(self.eye_target, 'hp') and self.eye_target.hp <= 0):
            for enemy in mobs:
                self.eye_target = enemy
                break
        
        # 虹膜
        iris_r = int(eye_r * 0.5 * self.eye_open)
        look_x, look_y = 0, 0
        if self.eye_target and hasattr(self.eye_target, 'rect'):
            dx = self.eye_target.rect.centerx - cx
            dy = self.eye_target.rect.centery - cy
            d = max(1, math.sqrt(dx * dx + dy * dy))
            look_x = dx / d * 8
            look_y = dy / d * 5
        
        if iris_r > 0:
            # 虹膜渐变
            pygame.draw.circle(self.image, self.divine_blue,
                             (int(cx + look_x), int(cy + look_y)), iris_r)
            pygame.draw.circle(self.image, self.truth_purple,
                             (int(cx + look_x), int(cy + look_y)), int(iris_r * 0.7))
            # 瞳孔
            pygame.draw.ellipse(self.image, (10, 10, 20),
                              (int(cx + look_x) - 3, int(cy + look_y) - int(iris_r * 0.6),
                               6, int(iris_r * 1.2)))
            # 高光
            pygame.draw.circle(self.image, (255, 255, 255),
                             (int(cx - eye_r * 0.3), int(cy - eye_r * 0.2)), 4)
        
        # 审判光线 - 从眼睛射向敌人
        if self.eye_target and self.eye_open > 0.8 and self.frame % 3 == 0:
            tx = self.eye_target.rect.centerx
            ty = self.eye_target.rect.centery
            # 光线
            pygame.draw.line(self.image, (*self.holy_gold, 150),
                           (cx, cy), (tx, ty), 4)
            pygame.draw.line(self.image, (*self.pure_white, 200),
                           (cx, cy), (tx, ty), 2)
            # 造成伤害
            self.eye_target.hp -= self.damage * 0.15
        
        # 范围内敌人持续灼烧
        if self.frame % 5 == 0:
            for enemy in mobs:
                dist = math.hypot(enemy.rect.centerx - cx, enemy.rect.centery - cy)
                if dist < self.max_radius:
                    enemy.hp -= self.damage * 0.1
                    # 灼烧粒子
                    self._add_particle(enemy.rect.centerx, enemy.rect.centery,
                                     random.uniform(-2, 2), random.uniform(-4, -1),
                                     self.holy_gold, 15, 3)
        
        # 最终审判（结束前爆发）
        if progress > 0.85:
            finale_progress = (progress - 0.85) / 0.15
            
            # 全屏神圣光芒
            flash_alpha = int(180 * math.sin(finale_progress * math.pi))
            pygame.draw.rect(self.image, (*self.holy_gold, flash_alpha // 2), (0, 0, WIDTH, HEIGHT))
            
            # 最终伤害
            if self.frame % 10 == 0:
                for enemy in mobs:
                    dist = math.hypot(enemy.rect.centerx - cx, enemy.rect.centery - cy)
                    if dist < self.max_radius:
                        enemy.hp -= self.damage * 0.5
        
        self._update_particles()
    
    def update(self):
        self.frame += 1
        
        if self.phase == 0:
            self._phase0_seal()
            if self.frame >= self.phase_duration[0]:
                self.phase = 1
                self.frame = 0
        
        elif self.phase == 1:
            self._phase1_explosion()
            if self.frame >= self.phase_duration[1]:
                self.phase = 2
                self.frame = 0
                self.pages.clear()
                self.center_x = int(self.x)
                self.center_y = int(self.y)
        
        elif self.phase == 2:
            self._phase2_judgment()
            if self.frame >= self.phase_duration[2]:
                self.kill()
    
    def _render(self):
        pass
    
    def draw(self, surface):
        pass


# ============================================================
#   辅助攻击：书页护卫
# ============================================================
class PageGuardBullet(pygame.sprite.Sprite):
    """
    书页护卫 - 自动防护
    
    触发：受到伤害时自动触发
    效果：消耗书页阻挡伤害
    """
    
    def __init__(self, x, y, **kwargs):
        super().__init__()
        self.x = x
        self.y = y
        self.damage = 0
        self.is_enemy = False
        self.piercing = False
        self.image = pygame.Surface((140, 140), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        bullets.add(self)
        all_sprites.add(self)
        self.lifetime = 0
        self.duration = 30
        self.shield_radius = 40
        self.pages_used = 2
        self.color = MAGNUS_COLORS["page"]
    
    def update(self):
        self.lifetime += 1
        if self.lifetime > self.duration:
            self.kill()
            return
        self._render()
        self.rect.center = (int(self.x), int(self.y))
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        t = self.lifetime * 0.1
        progress = self.lifetime / self.duration
        alpha = int(200 * (1 - progress))
        center = 70
        
        # 书页环绕
        for page in range(self.pages_used):
            page_angle = t * 8 + page * 3.14
            page_x = center + int(math.cos(page_angle) * self.shield_radius)
            page_y = center + int(math.sin(page_angle) * self.shield_radius)
            
            pygame.draw.rect(self.image, (*self.color, alpha), 
                           (page_x - 8, page_y - 10, 16, 20))
            pygame.draw.rect(self.image, (255, 215, 0, alpha // 2), 
                           (page_x - 8, page_y - 10, 16, 20), 1)
        
        # 护盾光环
        pygame.draw.circle(self.image, (*MAGNUS_COLORS["rune"], alpha // 3),
                         (center, center), self.shield_radius, 2)
    
    def draw(self, surface):
        pass  # 使用 image/rect 系统渲染
