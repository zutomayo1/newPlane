# -*- coding: utf-8 -*-
"""
浮游刃环·星镰 - 专属子弹模块
环刃巡航，悬停扫割，可召回暴击

特性：
- 投掷环刃飞出后悬停
- 水平往返扫割
- 可召回暴击×1.8
"""
import pygame
import math
import random
from config import all_sprites, mobs


class RingBlade(pygame.sprite.Sprite):
    """环刃 - 巡航扫割"""
    
    def __init__(self, x, y, damage, owner=None):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.piercing = 999  # 无限穿透
        
        # 颜色
        self.blade_color = (200, 210, 230)  # 钛银
        self.glow_color = (100, 180, 255)   # 星尘蓝
        
        # 位置
        self.float_x = float(x)
        self.float_y = float(y)
        self.start_x = float(x)
        self.start_y = float(y)
        
        # 状态
        self.state = "flying"  # flying, hovering, recalling
        self.target_y = max(100, y - 500)  # 悬停位置（飞出1.2屏）
        self.fly_speed = 15
        
        # 悬停参数
        self.hover_duration = 240  # 4秒
        self.hover_timer = 0
        self.sweep_dir = 1
        self.sweep_speed = 6
        self.sweep_range = 200
        self.hover_center_x = x
        
        # 命中计数
        self.hit_count = 0
        self.max_hits = 6
        
        # 召回
        self.can_recall = False
        self.is_recalled = False
        self.recall_damage_mult = 1.8
        
        # 旋转
        self.rotation = 0
        self.spin_speed = 15
        
        # 图像
        self.size = 50
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.frame = 0
        self.hit_cooldown = 0  # 命中冷却
    
    def _draw_blade(self):
        """绘制环刃"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size, self.size
        
        # 旋转角度
        rot = self.rotation
        
        # 外层光晕
        glow_alpha = 100 + int(50 * math.sin(self.frame * 0.2))
        glow_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.glow_color, glow_alpha), (cx, cy), 35, 8)
        self.image.blit(glow_surf, (0, 0))
        
        # 主环刃
        ring_r = 28
        pygame.draw.circle(self.image, self.blade_color, (cx, cy), ring_r, 5)
        
        # 6片刃
        for i in range(6):
            blade_angle = rot + i * 60
            rad = math.radians(blade_angle)
            
            # 刃的起点（环上）
            bx = cx + math.cos(rad) * ring_r
            by = cy + math.sin(rad) * ring_r
            
            # 刃的终点（向外延伸）
            blade_len = 15
            ex = cx + math.cos(rad) * (ring_r + blade_len)
            ey = cy + math.sin(rad) * (ring_r + blade_len)
            
            # 绘制刃（三角形）
            perp_rad = rad + math.pi / 2
            w = 4
            p1 = (ex, ey)
            p2 = (bx + math.cos(perp_rad) * w, by + math.sin(perp_rad) * w)
            p3 = (bx - math.cos(perp_rad) * w, by - math.sin(perp_rad) * w)
            
            pygame.draw.polygon(self.image, self.blade_color, [p1, p2, p3])
            
            # 刃尖发光
            pygame.draw.circle(self.image, self.glow_color, (int(ex), int(ey)), 3)
        
        # 中心宝石
        gem_pulse = int(8 + 3 * math.sin(self.frame * 0.15))
        pygame.draw.circle(self.image, self.glow_color, (cx, cy), gem_pulse)
        pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), gem_pulse - 3)
        
        # 召回状态发光
        if self.is_recalled:
            recall_glow = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            glow_r = 40 + int(10 * math.sin(self.frame * 0.5))
            pygame.draw.circle(recall_glow, (*self.glow_color, 150), (cx, cy), glow_r, 5)
            self.image.blit(recall_glow, (0, 0))
    
    def update(self):
        """更新环刃"""
        self.frame += 1
        self.rotation += self.spin_speed
        
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        
        if self.state == "flying":
            self._update_flying()
        elif self.state == "hovering":
            self._update_hovering()
        elif self.state == "recalling":
            self._update_recalling()
        
        # 更新位置
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 绘制
        self._draw_blade()
        
        # 命中检测
        self._check_hits()
    
    def _update_flying(self):
        """飞行状态"""
        self.float_y -= self.fly_speed
        
        if self.float_y <= self.target_y:
            self.state = "hovering"
            self.hover_center_x = self.float_x
            self.can_recall = True
    
    def _update_hovering(self):
        """悬停扫割状态"""
        self.hover_timer += 1
        
        # 水平往返
        self.float_x += self.sweep_dir * self.sweep_speed
        
        # 边界反弹
        if self.float_x > self.hover_center_x + self.sweep_range:
            self.sweep_dir = -1
        elif self.float_x < self.hover_center_x - self.sweep_range:
            self.sweep_dir = 1
        
        # 检查结束条件
        if self.hover_timer >= self.hover_duration or self.hit_count >= self.max_hits:
            self._end()
    
    def _update_recalling(self):
        """召回状态"""
        if not self.owner or not self.owner.alive():
            self.kill()
            return
        
        # 向玩家飞行
        dx = self.owner.rect.centerx - self.float_x
        dy = self.owner.rect.centery - self.float_y
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            speed = 25  # 召回加速
            self.float_x += dx / dist * speed
            self.float_y += dy / dist * speed
        
        # 到达玩家
        if dist < 30:
            self.kill()
    
    def _check_hits(self):
        """检测命中"""
        if self.hit_cooldown > 0:
            return
        
        damage = self.damage
        if self.is_recalled:
            damage *= self.recall_damage_mult
        
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.float_x,
                            enemy.rect.centery - self.float_y)
            if dist < 45:
                enemy.hp -= damage
                self.hit_count += 1
                self.hit_cooldown = 15  # 命中冷却
                
                if hasattr(enemy, 'hit_flash'):
                    enemy.hit_flash = 10 if self.is_recalled else 5
                
                # 暴击效果
                if self.is_recalled:
                    # 创建暴击特效
                    crit_effect = BladeCritEffect(enemy.rect.centerx, enemy.rect.centery)
                    all_sprites.add(crit_effect)
                
                break
    
    def recall(self):
        """召回环刃"""
        if self.can_recall and self.state == "hovering":
            self.state = "recalling"
            self.is_recalled = True
            self.spin_speed = 30  # 加速旋转
            return True
        return False
    
    def _end(self):
        """环刃崩解"""
        # 创建崩解效果
        for i in range(6):
            angle = i * 60
            shard = BladeShard(self.float_x, self.float_y, angle, self.damage * 0.3)
            all_sprites.add(shard)
        self.kill()


class BladeShard(pygame.sprite.Sprite):
    """环刃碎片 - 崩解后散射"""
    
    def __init__(self, x, y, angle, damage):
        super().__init__()
        self.damage = damage
        self.float_x = float(x)
        self.float_y = float(y)
        self.angle = angle
        self.speed = 8
        
        self.vx = math.cos(math.radians(angle)) * self.speed
        self.vy = math.sin(math.radians(angle)) * self.speed
        
        self.lifetime = 30
        self.frame = 0
        
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        self._draw()
    
    def _draw(self):
        """绘制碎片"""
        self.image.fill((0, 0, 0, 0))
        
        fade = self.lifetime / 30
        color = (200, 210, 230, int(255 * fade))
        
        # 三角形碎片
        points = [(10, 2), (18, 15), (2, 15)]
        pygame.draw.polygon(self.image, color, points)
    
    def update(self):
        """更新碎片"""
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        self.float_x += self.vx
        self.float_y += self.vy
        self.vy += 0.3  # 重力
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        self._draw()


class BladeCritEffect(pygame.sprite.Sprite):
    """暴击特效"""
    
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.frame = 0
        self.duration = 20
        
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        """更新特效"""
        self.frame += 1
        self.image.fill((0, 0, 0, 0))
        
        progress = self.frame / self.duration
        
        # X形斩痕
        size = int(40 * progress)
        alpha = int(255 * (1 - progress))
        
        cx, cy = 50, 50
        pygame.draw.line(self.image, (100, 180, 255, alpha), 
                        (cx - size, cy - size), (cx + size, cy + size), 4)
        pygame.draw.line(self.image, (100, 180, 255, alpha), 
                        (cx - size, cy + size), (cx + size, cy - size), 4)
        
        # 光环
        ring_r = int(30 * progress)
        pygame.draw.circle(self.image, (200, 220, 255, alpha // 2), (cx, cy), ring_r, 2)
        
        if self.frame >= self.duration:
            self.kill()


class BladeStorm(pygame.sprite.Sprite):
    """星镰风暴 - 大招：多重环刃同时巡航"""
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 2
        
        # 环刃数量
        self.blade_count = 7
        self.blades_spawned = 0
        self.spawn_interval = 10
        self.spawn_timer = 0
        
        # 阶段
        self.phase = 0  # 0=蓄力, 1=释放
        self.charge_duration = 25
        self.frame = 0
        
        # 活跃的环刃
        self.active_blades = []
        
        # 图像
        self.image = pygame.Surface((540, 700), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _draw_charge(self):
        """绘制蓄力"""
        self.image.fill((0, 0, 0, 0))
        
        progress = self.frame / self.charge_duration
        cx, cy = self.owner.rect.centerx, self.owner.rect.centery
        
        # 环刃聚集
        for i in range(self.blade_count):
            angle = i * (360 / self.blade_count) + self.frame * 5
            dist = 100 * (1 - progress) + 30
            bx = cx + math.cos(math.radians(angle)) * dist
            by = cy + math.sin(math.radians(angle)) * dist
            
            # 小环刃预览
            pygame.draw.circle(self.image, (200, 210, 230, int(200 * progress)), 
                             (int(bx), int(by)), 15, 2)
            pygame.draw.circle(self.image, (100, 180, 255, int(150 * progress)), 
                             (int(bx), int(by)), 10)
        
        # 中心能量
        core_r = int(20 * progress)
        pygame.draw.circle(self.image, (100, 180, 255, int(200 * progress)), (cx, cy), core_r)
    
    def _spawn_blade(self):
        """生成环刃"""
        from config import bullets
        
        # 不同角度发射
        angle = self.blades_spawned * (360 / self.blade_count)
        offset_x = math.cos(math.radians(angle)) * 30
        
        blade = RingBlade(self.owner.rect.centerx + offset_x, 
                         self.owner.rect.centery,
                         self.damage, self.owner)
        # 不同悬停高度
        blade.target_y = 80 + self.blades_spawned * 60
        blade.hover_center_x = 100 + self.blades_spawned * 60
        
        all_sprites.add(blade)
        bullets.add(blade)
        self.active_blades.append(blade)
    
    def update(self):
        """更新星镰风暴"""
        self.frame += 1
        
        if self.phase == 0:  # 蓄力
            self._draw_charge()
            if self.frame >= self.charge_duration:
                self.phase = 1
                self.frame = 0
        
        elif self.phase == 1:  # 释放
            self.spawn_timer += 1
            self.image.fill((0, 0, 0, 0))
            
            if self.blades_spawned < self.blade_count and self.spawn_timer >= self.spawn_interval:
                self.spawn_timer = 0
                self._spawn_blade()
                self.blades_spawned += 1
            
            # 检查是否所有环刃都结束
            if self.blades_spawned >= self.blade_count:
                active = [b for b in self.active_blades if b.alive()]
                if not active:
                    self.kill()


# ==============================================================================
#   子弹预览渲染函数
# ==============================================================================

def render_starblade_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Starblade子弹涂装预览效果 - 环刃星镰特效
    
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
    
    # 检查是否是Starblade子弹涂装
    starblade_effects = [
        "blade_sweep", "crit_recall", "chain_lightning",
        "life_steal", "rebirth_flame", "space_cut"
    ]
    
    matched_effect = None
    for effect in starblade_effects:
        if effect in effects:
            matched_effect = effect
            break
    
    if not matched_effect:
        return False
    
    # 根据效果类型绘制不同的预览
    blade_size = size // 3
    rotation = t * 120  # 旋转动画
    
    if matched_effect == "blade_sweep":
        # 星镰环刃 - 银白旋转环刃
        _draw_starblade_ring(surface, center_x, center_y, blade_size, rotation,
                            (180, 200, 220), (150, 180, 255))
    elif matched_effect == "crit_recall":
        # 暴击星镰 - 金色+暴击光效
        _draw_starblade_ring(surface, center_x, center_y, blade_size, rotation,
                            (255, 200, 80), (255, 180, 50))
        # 暴击闪光
        flash_alpha = int(128 + 127 * math.sin(t * 6))
        _draw_crit_flash(surface, center_x, center_y, blade_size, flash_alpha)
    elif matched_effect == "chain_lightning":
        # 雷电刃环 - 电弧缠绕
        _draw_starblade_ring(surface, center_x, center_y, blade_size, rotation,
                            (100, 200, 255), (150, 230, 255))
        # 电弧效果
        _draw_lightning_arcs(surface, center_x, center_y, blade_size, t)
    elif matched_effect == "life_steal":
        # 血刃星镰 - 猩红吸血
        _draw_starblade_ring(surface, center_x, center_y, blade_size, rotation,
                            (180, 40, 50), (220, 60, 70))
        # 血滴效果
        for i in range(4):
            angle = t * 90 + i * 90
            dist = blade_size + 5
            dx = center_x + int(math.cos(math.radians(angle)) * dist)
            dy = center_y + int(math.sin(math.radians(angle)) * dist)
            pygame.draw.circle(surface, (180, 30, 30), (dx, dy), 3)
    elif matched_effect == "rebirth_flame":
        # 凤凰星镰 - 火焰环刃
        _draw_starblade_ring(surface, center_x, center_y, blade_size, rotation,
                            (255, 120, 50), (255, 180, 80))
        # 火焰尾迹
        for i in range(6):
            flame_angle = rotation + i * 60
            fx = center_x + int(math.cos(math.radians(flame_angle)) * (blade_size + 10))
            fy = center_y + int(math.sin(math.radians(flame_angle)) * (blade_size + 10))
            pygame.draw.circle(surface, (255, 150, 50), (fx, fy), 4)
            pygame.draw.circle(surface, (255, 200, 100), (fx, fy), 2)
    elif matched_effect == "space_cut":
        # 虚空星镰 - 空间裂隙
        _draw_starblade_ring(surface, center_x, center_y, blade_size, rotation,
                            (80, 60, 120), (120, 100, 180))
        # 空间裂隙效果
        _draw_space_rift(surface, center_x, center_y, blade_size, t)
    
    return True


def _draw_starblade_ring(surface, cx, cy, size, rotation, blade_color, glow_color):
    """绘制环刃形状"""
    # 外光晕
    pygame.draw.circle(surface, glow_color, (cx, cy), size + 5, 3)
    
    # 主环
    pygame.draw.circle(surface, blade_color, (cx, cy), size, 4)
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy), size, 1)
    
    # 6片刃
    for i in range(6):
        angle = rotation + i * 60
        rad = math.radians(angle)
        
        # 刃起点
        bx = cx + int(math.cos(rad) * size)
        by = cy + int(math.sin(rad) * size)
        
        # 刃终点
        ex = cx + int(math.cos(rad) * (size + 12))
        ey = cy + int(math.sin(rad) * (size + 12))
        
        # 绘制三角刃
        perp = rad + math.pi / 2
        w = 4
        p1 = (bx + int(math.cos(perp) * w), by + int(math.sin(perp) * w))
        p2 = (bx - int(math.cos(perp) * w), by - int(math.sin(perp) * w))
        pygame.draw.polygon(surface, blade_color, [p1, (ex, ey), p2])
        pygame.draw.polygon(surface, (255, 255, 255), [p1, (ex, ey), p2], 1)


def _draw_crit_flash(surface, cx, cy, size, alpha):
    """绘制暴击闪光"""
    flash_surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
    for i in range(4):
        angle = i * 45
        rad = math.radians(angle)
        ex = size * 1.5 + int(math.cos(rad) * size * 1.2)
        ey = size * 1.5 + int(math.sin(rad) * size * 1.2)
        pygame.draw.line(flash_surf, (255, 255, 200, alpha),
                        (size * 1.5, size * 1.5), (ex, ey), 2)
    surface.blit(flash_surf, (cx - size * 1.5, cy - size * 1.5))


def _draw_lightning_arcs(surface, cx, cy, size, t):
    """绘制闪电弧"""
    for i in range(3):
        start_angle = t * 200 + i * 120
        end_angle = start_angle + 60
        
        sx = cx + int(math.cos(math.radians(start_angle)) * size)
        sy = cy + int(math.sin(math.radians(start_angle)) * size)
        ex = cx + int(math.cos(math.radians(end_angle)) * size)
        ey = cy + int(math.sin(math.radians(end_angle)) * size)
        
        # 锯齿闪电
        mid_x = (sx + ex) // 2 + random.randint(-5, 5)
        mid_y = (sy + ey) // 2 + random.randint(-5, 5)
        pygame.draw.line(surface, (150, 230, 255), (sx, sy), (mid_x, mid_y), 2)
        pygame.draw.line(surface, (150, 230, 255), (mid_x, mid_y), (ex, ey), 2)


def _draw_space_rift(surface, cx, cy, size, t):
    """绘制空间裂隙"""
    for i in range(3):
        angle = t * 60 + i * 120
        dist = size + 8
        rx = cx + int(math.cos(math.radians(angle)) * dist)
        ry = cy + int(math.sin(math.radians(angle)) * dist)
        
        # 小裂隙
        rift_len = 10
        rift_angle = angle + 90
        ex = rx + int(math.cos(math.radians(rift_angle)) * rift_len)
        ey = ry + int(math.sin(math.radians(rift_angle)) * rift_len)
        pygame.draw.line(surface, (150, 100, 200), (rx, ry), (ex, ey), 2)
