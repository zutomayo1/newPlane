# -*- coding: utf-8 -*-
"""
酸蚀喷溅·腐沼 - 专属子弹模块
抛物酸囊，落地溅射，酸液汇合

特性：
- 高抛酸囊落地碎裂
- 6股酸液独立寻敌附着DOT
- 3股命中同目标合成酸沼池
"""
import pygame
import math
import random
from config import all_sprites, mobs


class AcidBlob(pygame.sprite.Sprite):
    """酸囊 - 抛物线飞行，落地碎裂"""
    
    def __init__(self, x, y, target_x, target_y, damage, owner=None):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.piercing = 0
        
        # 颜色
        self.acid_color = (150, 255, 80)
        self.dark_color = (50, 80, 30)
        
        # 位置
        self.float_x = float(x)
        self.float_y = float(y)
        self.start_x = float(x)
        self.start_y = float(y)
        
        # 目标位置
        self.target_x = target_x
        self.target_y = target_y
        
        # 抛物线参数
        self.progress = 0.0
        self.flight_time = 50
        self.arc_height = 120
        
        # 动画
        self.frame = 0
        self.wobble = 0
        
        # 图像
        self.size = 25
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
    
    def _draw_blob(self):
        """绘制酸囊"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size, self.size
        
        # 晃动效果
        wobble_x = math.sin(self.wobble) * 3
        wobble_y = math.cos(self.wobble * 1.3) * 2
        
        # 外层暗色
        pygame.draw.ellipse(self.image, self.dark_color, 
                          (cx - 12 + wobble_x, cy - 10 + wobble_y, 24, 20))
        
        # 内层亮色酸液
        pygame.draw.ellipse(self.image, self.acid_color, 
                          (cx - 10 + wobble_x, cy - 8 + wobble_y, 20, 16))
        
        # 高光
        pygame.draw.ellipse(self.image, (200, 255, 150), 
                          (cx - 5 + wobble_x, cy - 5 + wobble_y, 8, 6))
        
        # 气泡
        for i in range(3):
            bx = cx + random.randint(-8, 8) + wobble_x
            by = cy + random.randint(-6, 6) + wobble_y
            pygame.draw.circle(self.image, (200, 255, 180, 150), (int(bx), int(by)), 2)
    
    def update(self):
        """更新酸囊"""
        self.frame += 1
        self.wobble += 0.3
        
        # 更新进度
        self.progress += 1.0 / self.flight_time
        
        if self.progress >= 1.0:
            self._explode()
            return
        
        # 抛物线位置
        self.float_x = self.start_x + (self.target_x - self.start_x) * self.progress
        arc = 4 * self.arc_height * self.progress * (1 - self.progress)
        self.float_y = self.start_y + (self.target_y - self.start_y) * self.progress - arc
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        self._draw_blob()
    
    def _explode(self):
        """落地碎裂"""
        # 生成6股酸液
        for i in range(6):
            angle = i * 60 + random.randint(-15, 15)
            splash = AcidSplash(self.float_x, self.float_y, angle, self.damage, self.owner)
            all_sprites.add(splash)
        
        # 爆炸效果
        burst = AcidBurst(self.float_x, self.float_y)
        all_sprites.add(burst)
        
        self.kill()


class AcidSplash(pygame.sprite.Sprite):
    """酸液溅射 - 独立寻敌"""
    
    def __init__(self, x, y, angle, damage, owner):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        
        self.float_x = float(x)
        self.float_y = float(y)
        
        # 初始速度
        self.speed = 6
        rad = math.radians(angle)
        self.vx = math.cos(rad) * self.speed
        self.vy = math.sin(rad) * self.speed
        
        # 寻敌
        self.target = None
        self.homing_strength = 0.15
        
        # DOT参数
        self.dot_duration = 180  # 3秒
        self.dot_damage = damage * 0.2
        
        # 图像
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.frame = 0
        self.lifetime = 120
        self.trail = []
    
    def _draw(self):
        """绘制酸液"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = 15, 15
        
        # 拖尾
        for i, (tx, ty) in enumerate(self.trail[-8:]):
            trail_x = tx - self.rect.left
            trail_y = ty - self.rect.top
            alpha = int(100 * (i + 1) / 8)
            size = max(1, 4 - i // 2)
            pygame.draw.circle(self.image, (150, 255, 80, alpha), 
                             (int(trail_x), int(trail_y)), size)
        
        # 主体
        pygame.draw.circle(self.image, (50, 80, 30), (cx, cy), 7)
        pygame.draw.circle(self.image, (150, 255, 80), (cx, cy), 5)
        pygame.draw.circle(self.image, (200, 255, 150), (cx - 1, cy - 1), 2)
    
    def update(self):
        """更新酸液"""
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 记录拖尾
        self.trail.append((self.float_x, self.float_y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        # 寻敌
        if not self.target or not self.target.alive():
            self._find_target()
        
        if self.target and self.target.alive():
            # 追踪
            dx = self.target.rect.centerx - self.float_x
            dy = self.target.rect.centery - self.float_y
            dist = math.hypot(dx, dy)
            
            if dist > 0:
                self.vx += (dx / dist) * self.homing_strength
                self.vy += (dy / dist) * self.homing_strength
                
                # 限制速度
                speed = math.hypot(self.vx, self.vy)
                if speed > 10:
                    self.vx = self.vx / speed * 10
                    self.vy = self.vy / speed * 10
            
            # 命中检测
            if dist < 25:
                self._hit_target()
                return
        
        # 移动
        self.float_x += self.vx
        self.float_y += self.vy
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        self._draw()
    
    def _find_target(self):
        """寻找目标"""
        min_dist = float('inf')
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.float_x,
                            enemy.rect.centery - self.float_y)
            if dist < min_dist:
                min_dist = dist
                self.target = enemy
    
    def _hit_target(self):
        """命中目标"""
        if not self.target:
            return
        
        # 初始伤害
        self.target.hp -= self.damage
        if hasattr(self.target, 'hit_flash'):
            self.target.hit_flash = 8
        
        # 附着DOT
        if not hasattr(self.target, 'acid_stacks'):
            self.target.acid_stacks = 0
            self.target.acid_timer = 0
            self.target.acid_damage = 0
        
        self.target.acid_stacks += 1
        self.target.acid_timer = self.dot_duration
        self.target.acid_damage += self.dot_damage
        
        # 检查酸液汇合
        if self.target.acid_stacks >= 3:
            self._create_acid_pool()
        
        # 创建附着效果
        attach = AcidAttach(self.target)
        all_sprites.add(attach)
        
        self.kill()
    
    def _create_acid_pool(self):
        """创建酸沼池"""
        pool = AcidPool(self.target.rect.centerx, self.target.rect.centery, 
                       self.damage * 2, self.owner)
        all_sprites.add(pool)
        
        # 重置叠层
        self.target.acid_stacks = 0


class AcidAttach(pygame.sprite.Sprite):
    """酸液附着效果"""
    
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.duration = 180
        self.frame = 0
        
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
    
    def _draw(self):
        """绘制附着效果"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = 25, 25
        
        fade = min(1.0, (self.duration - self.frame) / 30) if self.frame > self.duration - 30 else 1.0
        
        # 酸蚀环
        ring_r = 20 + int(5 * math.sin(self.frame * 0.2))
        pygame.draw.circle(self.image, (150, 255, 80, int(100 * fade)), (cx, cy), ring_r, 2)
        
        # 滴落的酸液
        for i in range(3):
            drip_y = cy + (self.frame * 2 + i * 15) % 30
            drip_x = cx + math.sin(self.frame * 0.1 + i) * 10
            pygame.draw.circle(self.image, (150, 255, 80, int(150 * fade)), 
                             (int(drip_x), int(drip_y)), 3)
    
    def update(self):
        """更新附着"""
        self.frame += 1
        
        if not self.target or not self.target.alive():
            self.kill()
            return
        
        # DOT伤害
        if self.frame % 18 == 0:  # 每0.3秒
            if hasattr(self.target, 'acid_damage') and self.target.acid_damage > 0:
                self.target.hp -= self.target.acid_damage
        
        self.rect.center = self.target.rect.center
        self._draw()
        
        if self.frame >= self.duration:
            self.kill()


class AcidPool(pygame.sprite.Sprite):
    """酸沼池 - 区域持续伤害"""
    
    def __init__(self, x, y, damage, owner):
        super().__init__()
        self.x = x
        self.y = y
        self.damage = damage
        self.owner = owner
        
        # 持续4秒
        self.duration = 240
        self.frame = 0
        
        # 区域
        self.radius = 80
        
        # 伤害间隔
        self.damage_interval = 18
        self.damage_timer = 0
        
        # 图像
        self.image = pygame.Surface((self.radius * 2 + 20, self.radius * 2 + 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        # 气泡位置
        self.bubbles = []
        for _ in range(15):
            self.bubbles.append({
                'x': random.uniform(-self.radius * 0.8, self.radius * 0.8),
                'y': random.uniform(-self.radius * 0.8, self.radius * 0.8),
                'size': random.randint(3, 8),
                'phase': random.uniform(0, math.pi * 2)
            })
    
    def _draw(self):
        """绘制酸沼池"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.radius + 10, self.radius + 10
        
        fade = min(1.0, (self.duration - self.frame) / 30) if self.frame > self.duration - 30 else 1.0
        
        # 底层暗色
        pygame.draw.ellipse(self.image, (30, 50, 20, int(150 * fade)), 
                          (cx - self.radius, cy - self.radius * 0.6, 
                           self.radius * 2, self.radius * 1.2))
        
        # 酸液层
        pygame.draw.ellipse(self.image, (100, 180, 60, int(180 * fade)), 
                          (cx - self.radius + 5, cy - self.radius * 0.5, 
                           self.radius * 2 - 10, self.radius))
        
        # 高光
        pygame.draw.ellipse(self.image, (150, 255, 80, int(100 * fade)), 
                          (cx - self.radius + 15, cy - self.radius * 0.4, 
                           self.radius - 20, self.radius * 0.5))
        
        # 气泡
        for bubble in self.bubbles:
            bx = cx + bubble['x']
            # 气泡上浮动画
            by = cy + bubble['y'] - (self.frame * 0.5 + bubble['phase']) % 20
            # 大小脉动
            size = bubble['size'] + int(2 * math.sin(self.frame * 0.1 + bubble['phase']))
            
            if size > 0:
                pygame.draw.circle(self.image, (200, 255, 150, int(120 * fade)), 
                                 (int(bx), int(by)), size)
                pygame.draw.circle(self.image, (255, 255, 220, int(80 * fade)), 
                                 (int(bx - 1), int(by - 1)), max(1, size - 2))
    
    def update(self):
        """更新酸沼池"""
        self.frame += 1
        self.damage_timer += 1
        
        # 伤害
        if self.damage_timer >= self.damage_interval:
            self.damage_timer = 0
            self._deal_damage()
        
        self._draw()
        
        if self.frame >= self.duration:
            self.kill()
    
    def _deal_damage(self):
        """对区域内敌人造成伤害"""
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.x, enemy.rect.centery - self.y)
            if dist < self.radius:
                # 双倍DOT
                enemy.hp -= self.damage
                if hasattr(enemy, 'hit_flash'):
                    enemy.hit_flash = 5
                
                # 减速效果
                if hasattr(enemy, 'speed_mult'):
                    enemy.speed_mult = 0.6  # -40%移速


class AcidBurst(pygame.sprite.Sprite):
    """酸囊爆炸效果"""
    
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.frame = 0
        self.duration = 20
        
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        """更新爆炸效果"""
        self.frame += 1
        self.image.fill((0, 0, 0, 0))
        
        progress = self.frame / self.duration
        cx, cy = 50, 50
        
        # 扩散圆
        r = int(40 * progress)
        alpha = int(200 * (1 - progress))
        pygame.draw.circle(self.image, (150, 255, 80, alpha), (cx, cy), r, 3)
        
        # 飞溅液滴
        for i in range(6):
            angle = i * 60
            dist = 20 + 30 * progress
            dx = cx + math.cos(math.radians(angle)) * dist
            dy = cy + math.sin(math.radians(angle)) * dist
            size = int(5 * (1 - progress))
            if size > 0:
                pygame.draw.circle(self.image, (150, 255, 80, alpha), (int(dx), int(dy)), size)
        
        if self.frame >= self.duration:
            self.kill()


class AcidFlood(pygame.sprite.Sprite):
    """酸蚀洪流 - 大招：大范围酸沼覆盖"""
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 2
        
        # 酸囊数量
        self.blob_count = 12
        self.blobs_spawned = 0
        self.spawn_interval = 8
        self.spawn_timer = 0
        
        # 阶段
        self.phase = 0
        self.charge_duration = 30
        self.frame = 0
        
        self.image = pygame.Surface((540, 700), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _draw_charge(self):
        """绘制蓄力"""
        self.image.fill((0, 0, 0, 0))
        
        progress = self.frame / self.charge_duration
        cx, cy = self.owner.rect.centerx, self.owner.rect.centery
        
        # 酸液聚集
        for i in range(8):
            angle = i * 45 + self.frame * 4
            dist = 80 * (1 - progress)
            ax = cx + math.cos(math.radians(angle)) * dist
            ay = cy + math.sin(math.radians(angle)) * dist
            
            size = int(10 * progress)
            pygame.draw.circle(self.image, (150, 255, 80, int(200 * progress)), 
                             (int(ax), int(ay)), size)
        
        # 中心酸池
        pool_r = int(30 * progress)
        pygame.draw.circle(self.image, (100, 200, 60, int(150 * progress)), (cx, cy), pool_r)
    
    def _spawn_blob(self):
        """生成酸囊"""
        from config import bullets
        
        # 扇形发射
        angle = -60 + self.blobs_spawned * (120 / self.blob_count)
        
        # 目标位置
        dist = random.randint(200, 400)
        target_x = self.owner.rect.centerx + math.cos(math.radians(angle - 90)) * dist
        target_y = self.owner.rect.centery + math.sin(math.radians(angle - 90)) * dist
        
        blob = AcidBlob(self.owner.rect.centerx, self.owner.rect.centery, 
                       target_x, target_y, self.damage, self.owner)
        
        all_sprites.add(blob)
        bullets.add(blob)
    
    def update(self):
        """更新酸蚀洪流"""
        self.frame += 1
        
        if self.phase == 0:
            self._draw_charge()
            if self.frame >= self.charge_duration:
                self.phase = 1
                self.frame = 0
        
        elif self.phase == 1:
            self.spawn_timer += 1
            self.image.fill((0, 0, 0, 0))
            
            if self.blobs_spawned < self.blob_count and self.spawn_timer >= self.spawn_interval:
                self.spawn_timer = 0
                self._spawn_blob()
                self.blobs_spawned += 1
            
            if self.blobs_spawned >= self.blob_count and self.frame > 60:
                self.kill()


# ==============================================================================
#   子弹预览渲染函数
# ==============================================================================

def render_acidswamp_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Acidswamp子弹涂装预览效果 - 酸蚀囊弹特效
    
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
    
    # 检查是否是Acidswamp子弹涂装
    acidswamp_effects = [
        "acid_splash", "pool_merge", "infection_spread",
        "area_dot", "burn_corrode", "void_corrode"
    ]
    
    matched_effect = None
    for effect in acidswamp_effects:
        if effect in effects:
            matched_effect = effect
            break
    
    if not matched_effect:
        return False
    
    # 根据效果类型绘制不同的预览
    blob_size = size // 3
    wobble = math.sin(t * 4) * 3  # 酸液波动
    
    if matched_effect == "acid_splash":
        # 酸蚀囊弹 - 酸绿囊弹
        _draw_acid_blob(surface, center_x, center_y, blob_size, wobble,
                       (100, 180, 80), (130, 200, 90), t)
        # 溅射液滴
        _draw_acid_splashes(surface, center_x, center_y, blob_size, (100, 180, 80), t)
    elif matched_effect == "pool_merge":
        # 剧毒酸池 - 深绿融合
        _draw_acid_blob(surface, center_x, center_y, blob_size, wobble,
                       (60, 120, 50), (80, 150, 60), t)
        # 多个小酸池汇聚
        for i in range(3):
            angle = i * 120 + t * 30
            dist = blob_size + 10
            px = center_x + int(math.cos(math.radians(angle)) * dist)
            py = center_y + int(math.sin(math.radians(angle)) * dist)
            pygame.draw.circle(surface, (60, 120, 50), (px, py), 6)
            pygame.draw.circle(surface, (80, 150, 60), (px, py), 4)
    elif matched_effect == "infection_spread":
        # 瘟疫酸液 - 紫绿瘟疫
        _draw_acid_blob(surface, center_x, center_y, blob_size, wobble,
                       (100, 80, 120), (150, 120, 180), t)
        # 感染扩散粒子
        for i in range(5):
            angle = t * 60 + i * 72
            dist = blob_size + int(math.sin(t * 3 + i) * 8) + 8
            px = center_x + int(math.cos(math.radians(angle)) * dist)
            py = center_y + int(math.sin(math.radians(angle)) * dist)
            pygame.draw.circle(surface, (130, 100, 150), (px, py), 3)
    elif matched_effect == "area_dot":
        # 核辐酸液 - 荧光绿
        _draw_acid_blob(surface, center_x, center_y, blob_size, wobble,
                       (100, 255, 100), (120, 255, 120), t)
        # 辐射波纹
        wave_r = int((t * 20) % 30) + blob_size
        wave_alpha = int(200 - (wave_r - blob_size) * 6)
        if wave_alpha > 0:
            pygame.draw.circle(surface, (100, 255, 100), (center_x, center_y), wave_r, 2)
    elif matched_effect == "burn_corrode":
        # 熔岩酸液 - 橙红熔岩
        _draw_acid_blob(surface, center_x, center_y, blob_size, wobble,
                       (255, 100, 50), (255, 150, 80), t)
        # 火焰+酸液混合
        for i in range(4):
            flame_x = center_x + random.randint(-blob_size//2, blob_size//2)
            flame_y = center_y + random.randint(-blob_size//2, blob_size//2)
            pygame.draw.circle(surface, (255, 180, 80), (flame_x, flame_y), 4)
    elif matched_effect == "void_corrode":
        # 虚空腐蚀 - 暗紫虚空
        _draw_acid_blob(surface, center_x, center_y, blob_size, wobble,
                       (80, 60, 100), (120, 100, 150), t)
        # 虚空漩涡
        for i in range(3):
            angle = t * 80 + i * 120
            dist = blob_size // 2 + i * 3
            px = center_x + int(math.cos(math.radians(angle)) * dist)
            py = center_y + int(math.sin(math.radians(angle)) * dist)
            pygame.draw.circle(surface, (120, 100, 150), (px, py), 3 - i)
    
    return True


def _draw_acid_blob(surface, cx, cy, size, wobble, main_color, highlight_color, t):
    """绘制酸液囊弹形状"""
    # 主体 - 椭圆形酸液
    width = size + int(wobble)
    height = size - int(wobble * 0.5)
    
    # 外层光晕
    pygame.draw.ellipse(surface, (*main_color, 100),
                       (cx - width - 3, cy - height - 3, (width + 3) * 2, (height + 3) * 2))
    
    # 主体
    pygame.draw.ellipse(surface, main_color,
                       (cx - width, cy - height, width * 2, height * 2))
    
    # 高光
    highlight_x = cx - size // 3
    highlight_y = cy - size // 3
    pygame.draw.ellipse(surface, highlight_color,
                       (highlight_x, highlight_y, size // 2, size // 3))
    
    # 气泡
    for i in range(3):
        bubble_x = cx + int(math.sin(t * 3 + i * 2) * size // 2)
        bubble_y = cy + int(math.cos(t * 2 + i) * size // 3)
        pygame.draw.circle(surface, (200, 255, 200), (bubble_x, bubble_y), 2)


def _draw_acid_splashes(surface, cx, cy, size, color, t):
    """绘制酸液溅射"""
    for i in range(6):
        angle = i * 60 + t * 50
        dist = size + 8 + int(math.sin(t * 4 + i) * 5)
        px = cx + int(math.cos(math.radians(angle)) * dist)
        py = cy + int(math.sin(math.radians(angle)) * dist)
        
        # 液滴
        drop_size = 3 + int(math.sin(t * 3 + i * 0.5) * 2)
        pygame.draw.circle(surface, color, (px, py), drop_size)
        pygame.draw.circle(surface, (200, 255, 150), (px, py), max(1, drop_size - 2))
