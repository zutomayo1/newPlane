# -*- coding: utf-8 -*-
"""
孢子幕炮·菌幕 - 专属子弹模块
孢子云幕DOT，累计伤害链式传播

特性：
- 抛物孢子壳爆裂成伞状孢子云幕
- 云幕内DOT伤害+降低命中率30%
- 累计10点伤害生成子孢子，链式传播2次
"""
import pygame
import math
import random
from config import all_sprites, mobs


class SporeShell(pygame.sprite.Sprite):
    """孢子壳 - 抛物飞行，爆裂成云幕"""
    
    def __init__(self, x, y, target_x, target_y, damage, owner=None):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.piercing = 0
        
        # 孢子绿配色
        self.shell_color = (60, 140, 80)  # 孢子绿
        self.glow_color = (140, 200, 120)  # 发光
        
        # 位置
        self.float_x = float(x)
        self.float_y = float(y)
        self.start_x = float(x)
        self.start_y = float(y)
        self.target_x = target_x
        self.target_y = target_y
        
        # 抛物线
        dist_y = target_y - y
        self.arc_height = abs(dist_y) * 0.3
        self.progress = 0.0
        self.speed = 0.025
        
        # 旋转
        self.rotation = 0
        
        # 图像
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.frame = 0
        self.lifetime = 80
    
    def _draw(self):
        """绘制孢子壳"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = 15, 15
        
        # 外壳
        pygame.draw.circle(self.image, self.shell_color, (cx, cy), 10)
        
        # 纹理
        for i in range(6):
            angle = self.rotation + i * 60
            x1 = cx + math.cos(math.radians(angle)) * 4
            y1 = cy + math.sin(math.radians(angle)) * 4
            x2 = cx + math.cos(math.radians(angle)) * 9
            y2 = cy + math.sin(math.radians(angle)) * 9
            pygame.draw.line(self.image, (40, 100, 60), (x1, y1), (x2, y2), 1)
        
        # 中心
        pygame.draw.circle(self.image, self.glow_color, (cx, cy), 4)
        
        # 发光点
        glow_alpha = int(150 + 50 * math.sin(self.frame * 0.3))
        glow_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.glow_color[:3], glow_alpha), (3, 3), 3)
        self.image.blit(glow_surf, (cx - 3, cy - 3))
    
    def update(self):
        """更新孢子壳"""
        self.frame += 1
        self.rotation += 5
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 抛物线运动
        self.progress += self.speed
        
        # 水平和垂直位置（含抛物弧度）
        self.float_x = self.start_x + (self.target_x - self.start_x) * self.progress
        linear_y = self.start_y + (self.target_y - self.start_y) * self.progress
        arc_offset = -math.sin(self.progress * math.pi) * self.arc_height
        self.float_y = linear_y + arc_offset
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        self._draw()
        
        # 到达目标
        if self.progress >= 1.0:
            self._burst()
            return
        
        # 命中敌人提前爆发
        for enemy in mobs:
            if self.rect.colliderect(enemy.rect):
                self._burst()
                return
    
    def _burst(self):
        """爆裂成孢子云幕"""
        cloud = SporeCloud(self.float_x, self.float_y, self.damage, self.owner)
        all_sprites.add(cloud)
        
        # 爆裂粒子
        for i in range(12):
            angle = i * 30
            dist = random.uniform(10, 30)
            px = self.float_x + math.cos(math.radians(angle)) * dist
            py = self.float_y + math.sin(math.radians(angle)) * dist
            
            particle = SporeParticle(px, py, angle)
            all_sprites.add(particle)
        
        self.kill()


class SporeCloud(pygame.sprite.Sprite):
    """孢子云幕 - 持续5秒的DOT区域"""
    
    def __init__(self, x, y, damage, owner, generation=0):
        super().__init__()
        self.x = x
        self.y = y
        self.damage = damage
        self.owner = owner
        self.generation = generation  # 链式传播代数
        
        # 持续5秒
        self.duration = 300
        self.frame = 0
        
        # DOT间隔
        self.dot_interval = 30
        self.dot_timer = 0
        
        # 子孢子累计伤害
        self.damage_accumulated = {}  # enemy_id: total_damage
        self.child_spawn_threshold = 10
        
        # 大小
        self.radius = 70
        self.current_radius = 0
        self.growth_speed = 5
        
        # 降低命中标记
        self.debuff_enemies = set()
        
        # 图像
        self.image = pygame.Surface((180, 180), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
    
    def _draw(self):
        """绘制孢子云幕"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = 90, 90
        
        r = min(self.current_radius, self.radius)
        
        if r <= 0:
            return
        
        # 淡出
        fade = min(1.0, (self.duration - self.frame) / 60) if self.frame > self.duration - 60 else 1.0
        
        # 多层云雾
        for i, (scale, alpha_mult) in enumerate([(1.0, 0.3), (0.8, 0.4), (0.6, 0.5)]):
            layer_r = int(r * scale)
            base_alpha = int(80 * alpha_mult * fade)
            
            # 渐变云雾
            for j in range(layer_r, 0, -5):
                alpha = int(base_alpha * (j / layer_r))
                color = (100, 180, 100, alpha)
                pygame.draw.circle(self.image, color, (cx, cy), j)
        
        # 飘动的孢子粒子
        for i in range(15):
            angle = (self.frame * 2 + i * 24) % 360
            wobble = math.sin(self.frame * 0.1 + i) * 10
            dist = (r * 0.4 + wobble) * (0.5 + (i % 3) * 0.2)
            
            px = cx + math.cos(math.radians(angle)) * dist
            py = cy + math.sin(math.radians(angle)) * dist
            
            size = 2 + (i % 3)
            pygame.draw.circle(self.image, (140, 200, 120, int(180 * fade)), 
                             (int(px), int(py)), size)
        
        # 中心核心
        core_pulse = 8 + 3 * math.sin(self.frame * 0.15)
        pygame.draw.circle(self.image, (80, 160, 80, int(150 * fade)), (cx, cy), int(core_pulse))
        pygame.draw.circle(self.image, (160, 220, 140, int(200 * fade)), (cx, cy), int(core_pulse * 0.5))
    
    def update(self):
        """更新孢子云幕"""
        self.frame += 1
        self.dot_timer += 1
        
        # 生长
        if self.current_radius < self.radius:
            self.current_radius += self.growth_speed
        
        # DOT伤害
        if self.dot_timer >= self.dot_interval:
            self.dot_timer = 0
            self._deal_dot()
        
        # 更新debuff
        self._update_debuff()
        
        self._draw()
        
        # 结束
        if self.frame >= self.duration:
            self._cleanup()
            self.kill()
    
    def _deal_dot(self):
        """DOT伤害"""
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.x, enemy.rect.centery - self.y)
            if dist < self.current_radius:
                # 造成DOT
                dot_damage = self.damage * 0.5
                enemy.hp -= dot_damage
                if hasattr(enemy, 'hit_flash'):
                    enemy.hit_flash = 4
                
                # 累计伤害
                enemy_id = id(enemy)
                if enemy_id not in self.damage_accumulated:
                    self.damage_accumulated[enemy_id] = 0
                self.damage_accumulated[enemy_id] += dot_damage
                
                # 检查子孢子生成
                if self.damage_accumulated[enemy_id] >= self.child_spawn_threshold:
                    self._spawn_child_spore(enemy)
                    self.damage_accumulated[enemy_id] -= self.child_spawn_threshold
    
    def _spawn_child_spore(self, enemy):
        """生成子孢子"""
        if self.generation >= 2:  # 最多链式2次
            return
        
        child = ChildSpore(enemy.rect.centerx, enemy.rect.centery, 
                          self.damage * 0.7, self.owner, self.generation + 1)
        all_sprites.add(child)
    
    def _update_debuff(self):
        """更新命中率降低debuff"""
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.x, enemy.rect.centery - self.y)
            enemy_id = id(enemy)
            
            if dist < self.current_radius:
                if enemy_id not in self.debuff_enemies:
                    self.debuff_enemies.add(enemy_id)
                    # 设置命中率降低标记
                    if hasattr(enemy, 'accuracy_debuff'):
                        enemy.accuracy_debuff = max(enemy.accuracy_debuff, 0.3)
                    else:
                        enemy.accuracy_debuff = 0.3
            else:
                if enemy_id in self.debuff_enemies:
                    self.debuff_enemies.discard(enemy_id)
                    if hasattr(enemy, 'accuracy_debuff'):
                        enemy.accuracy_debuff = 0
    
    def _cleanup(self):
        """清理debuff"""
        for enemy in mobs:
            enemy_id = id(enemy)
            if enemy_id in self.debuff_enemies:
                if hasattr(enemy, 'accuracy_debuff'):
                    enemy.accuracy_debuff = 0


class ChildSpore(pygame.sprite.Sprite):
    """子孢子 - 链式传播"""
    
    def __init__(self, x, y, damage, owner, generation):
        super().__init__()
        self.x = x
        self.y = y
        self.damage = damage
        self.owner = owner
        self.generation = generation
        
        # 寻找最近敌人
        self.target = self._find_target()
        
        self.speed = 5
        self.frame = 0
        self.lifetime = 60
        
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
    
    def _find_target(self):
        """寻找最近的敌人"""
        min_dist = float('inf')
        target = None
        
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.x, enemy.rect.centery - self.y)
            if dist > 30 and dist < min_dist:  # 不选择太近的
                min_dist = dist
                target = enemy
        
        return target
    
    def _draw(self):
        """绘制子孢子"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = 10, 10
        
        # 小型孢子
        pygame.draw.circle(self.image, (80, 160, 80), (cx, cy), 6)
        pygame.draw.circle(self.image, (140, 200, 120), (cx, cy), 3)
        
        # 尾迹
        for i in range(3):
            trail_alpha = 100 - i * 30
            pygame.draw.circle(self.image, (100, 180, 100, trail_alpha), 
                             (cx - i * 2, cy), 4 - i)
    
    def update(self):
        """更新子孢子"""
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        if self.target and self.target.alive():
            # 追踪目标
            dx = self.target.rect.centerx - self.x
            dy = self.target.rect.centery - self.y
            dist = math.hypot(dx, dy)
            
            if dist > 0:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
            
            self.rect.center = (int(self.x), int(self.y))
            
            # 到达目标
            if dist < 15:
                self._create_cloud()
                return
        else:
            # 无目标，直线飞行
            self.y -= self.speed
            self.rect.center = (int(self.x), int(self.y))
        
        self._draw()
    
    def _create_cloud(self):
        """创建子云幕"""
        cloud = SporeCloud(self.x, self.y, self.damage, self.owner, self.generation)
        cloud.radius = 40  # 更小的范围
        cloud.duration = 150  # 更短的持续时间
        all_sprites.add(cloud)
        self.kill()


class SporeParticle(pygame.sprite.Sprite):
    """孢子粒子 - 爆裂效果"""
    
    def __init__(self, x, y, angle):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        
        rad = math.radians(angle)
        self.vx = math.cos(rad) * random.uniform(2, 4)
        self.vy = math.sin(rad) * random.uniform(2, 4)
        
        self.lifetime = 30
        self.size = random.randint(3, 6)
        
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
    
    def _draw(self):
        """绘制粒子"""
        self.image.fill((0, 0, 0, 0))
        
        fade = self.lifetime / 30
        color = (100, 180, 100, int(200 * fade))
        
        pygame.draw.circle(self.image, color, (7, 7), int(self.size * fade))
    
    def update(self):
        """更新粒子"""
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        self.vx *= 0.95
        self.vy *= 0.95
        self.vy += 0.1  # 轻微下沉
        
        self.x += self.vx
        self.y += self.vy
        
        self.rect.center = (int(self.x), int(self.y))
        self._draw()


class SporeBloom(pygame.sprite.Sprite):
    """孢子盛放 - 大招：全屏孢子云幕"""
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 1.5
        
        # 阶段
        self.phase = 0
        self.charge_duration = 30
        self.frame = 0
        
        # 云幕生成
        self.clouds_spawned = 0
        self.max_clouds = 6
        self.spawn_interval = 10
        self.spawn_timer = 0
        
        self.image = pygame.Surface((540, 700), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _draw_charge(self):
        """绘制蓄力"""
        self.image.fill((0, 0, 0, 0))
        
        progress = self.frame / self.charge_duration
        cx, cy = self.owner.rect.centerx, self.owner.rect.centery
        
        # 孢子聚集
        for i in range(20):
            angle = i * 18 + self.frame * 3
            dist = 80 * (1 - progress) + 15
            px = cx + math.cos(math.radians(angle)) * dist
            py = cy + math.sin(math.radians(angle)) * dist
            
            size = int(5 * progress)
            pygame.draw.circle(self.image, (100, 180, 100, int(200 * progress)), 
                             (int(px), int(py)), size)
        
        # 核心光环
        ring_r = int(30 * progress)
        pygame.draw.circle(self.image, (140, 200, 120, int(200 * progress)), (cx, cy), ring_r, 4)
        
        # 中心核心
        core_r = int(15 * progress)
        pygame.draw.circle(self.image, (80, 160, 80, int(220 * progress)), (cx, cy), core_r)
    
    def _spawn_cloud(self):
        """生成孢子云幕"""
        # 随机位置（靠近敌人区域）
        x = random.randint(80, 460)
        y = random.randint(100, 400)
        
        cloud = SporeCloud(x, y, self.damage, self.owner, generation=0)
        cloud.radius = 90  # 大范围
        all_sprites.add(cloud)
    
    def update(self):
        """更新孢子盛放"""
        self.frame += 1
        
        if self.phase == 0:
            self._draw_charge()
            if self.frame >= self.charge_duration:
                self.phase = 1
                self.frame = 0
        
        elif self.phase == 1:
            self.spawn_timer += 1
            self.image.fill((0, 0, 0, 0))
            
            if self.clouds_spawned < self.max_clouds and self.spawn_timer >= self.spawn_interval:
                self.spawn_timer = 0
                self._spawn_cloud()
                self.clouds_spawned += 1
            
            if self.clouds_spawned >= self.max_clouds and self.frame > 40:
                self.kill()

# ==============================================================================
#   子弹预览渲染函数
# ==============================================================================

def render_sporeveil_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Sporeveil子弹涂装预览效果 - 孢子幕弹特效
    
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
    
    # 检查是否是Sporeveil子弹涂装
    sporeveil_effects = [
        "cloud_dot", "accuracy_debuff", "poison_cloud",
        "chain_spread", "burn_cloud", "void_parasite"
    ]
    
    matched_effect = None
    for effect in sporeveil_effects:
        if effect in effects:
            matched_effect = effect
            break
    
    if not matched_effect:
        return False
    
    # 根据效果类型绘制不同的预览
    spore_size = size // 3
    float_offset = math.sin(t * 2) * 3  # 浮动效果
    
    if matched_effect == "cloud_dot":
        # 孢子幕弹 - 青绿孢子
        _draw_spore_shell(surface, center_x, center_y + int(float_offset), spore_size,
                         (120, 180, 100), (150, 200, 130), t)
        # DOT云雾
        _draw_dot_cloud(surface, center_x, center_y, spore_size, (100, 180, 100, 60), t)
    elif matched_effect == "accuracy_debuff":
        # 迷雾孢子 - 灰蓝迷雾
        _draw_spore_shell(surface, center_x, center_y + int(float_offset), spore_size,
                         (150, 180, 200), (180, 200, 220), t)
        # 迷雾效果
        _draw_mist_effect(surface, center_x, center_y, spore_size, t)
    elif matched_effect == "poison_cloud":
        # 剧毒孢子 - 深紫毒菌
        _draw_spore_shell(surface, center_x, center_y + int(float_offset), spore_size,
                         (80, 60, 100), (120, 100, 150), t)
        # 毒云效果
        _draw_dot_cloud(surface, center_x, center_y, spore_size, (100, 80, 130, 80), t)
        # 毒液滴落
        for i in range(3):
            drop_y = center_y + spore_size + int((t * 30 + i * 15) % 15)
            drop_x = center_x + int(math.sin(t + i) * 8)
            pygame.draw.circle(surface, (100, 60, 120), (drop_x, drop_y), 2)
    elif matched_effect == "chain_spread":
        # 荧光孢子 - 生物发光
        _draw_spore_shell(surface, center_x, center_y + int(float_offset), spore_size,
                         (80, 200, 220), (150, 255, 255), t)
        # 链式传播线
        _draw_chain_links(surface, center_x, center_y, spore_size, (80, 200, 220), t)
    elif matched_effect == "burn_cloud":
        # 灰烬孢子 - 火焰菌类
        _draw_spore_shell(surface, center_x, center_y + int(float_offset), spore_size,
                         (200, 100, 50), (255, 150, 80), t)
        # 灰烬火焰
        for i in range(5):
            ember_x = center_x + random.randint(-spore_size, spore_size)
            ember_y = center_y + random.randint(-spore_size//2, spore_size//2)
            pygame.draw.circle(surface, (255, 180, 80), (ember_x, ember_y), 2)
    elif matched_effect == "void_parasite":
        # 虚空菌丝 - 暗紫寄生
        _draw_spore_shell(surface, center_x, center_y + int(float_offset), spore_size,
                         (60, 40, 80), (100, 80, 130), t)
        # 虚空触须
        _draw_void_tendrils(surface, center_x, center_y, spore_size, t)
    
    return True


def _draw_spore_shell(surface, cx, cy, size, main_color, highlight_color, t):
    """绘制孢子壳形状"""
    # 蘑菇帽形状
    cap_w = size
    cap_h = size * 0.7
    
    # 帽子
    pygame.draw.ellipse(surface, main_color,
                       (cx - cap_w, cy - cap_h, cap_w * 2, cap_h * 1.5))
    
    # 帽子边缘高光
    pygame.draw.arc(surface, highlight_color,
                   (cx - cap_w, cy - cap_h, cap_w * 2, cap_h * 1.5),
                   math.pi * 0.2, math.pi * 0.8, 2)
    
    # 柄
    pygame.draw.rect(surface, main_color,
                    (cx - size//4, cy, size//2, size * 0.6))
    
    # 顶部斑点
    for i in range(4):
        spot_x = cx + int(math.sin(i * 1.5) * cap_w * 0.5)
        spot_y = cy - cap_h * 0.3 + int(math.cos(i) * cap_h * 0.2)
        spot_r = 3 + int(math.sin(t * 2 + i) * 1)
        pygame.draw.circle(surface, (255, 255, 255, 150), (spot_x, spot_y), spot_r)


def _draw_dot_cloud(surface, cx, cy, size, cloud_color, t):
    """绘制DOT云雾"""
    for i in range(6):
        angle = t * 40 + i * 60
        dist = size + 5 + int(math.sin(t * 2 + i) * 5)
        px = cx + int(math.cos(math.radians(angle)) * dist)
        py = cy + int(math.sin(math.radians(angle)) * dist)
        
        cloud_r = 6 + int(math.sin(t * 3 + i * 0.5) * 2)
        pygame.draw.circle(surface, cloud_color, (px, py), cloud_r)


def _draw_mist_effect(surface, cx, cy, size, t):
    """绘制迷雾效果"""
    # 半透明迷雾层
    for layer in range(3):
        offset_x = int(math.sin(t + layer) * 5)
        offset_y = int(math.cos(t * 0.8 + layer) * 3)
        mist_r = size + 10 + layer * 5
        mist_alpha = 40 - layer * 10
        pygame.draw.circle(surface, (180, 200, 220, mist_alpha),
                          (cx + offset_x, cy + offset_y), mist_r)


def _draw_chain_links(surface, cx, cy, size, color, t):
    """绘制链式传播连接"""
    # 三个方向的链接线
    for i in range(3):
        angle = i * 120 + 30
        dist = size + 15
        ex = cx + int(math.cos(math.radians(angle)) * dist)
        ey = cy + int(math.sin(math.radians(angle)) * dist)
        
        # 虚线连接
        segments = 3
        for s in range(segments):
            progress = s / segments
            sx = int(cx + (ex - cx) * progress)
            sy = int(cy + (ey - cy) * progress)
            if s % 2 == int(t * 4) % 2:
                pygame.draw.circle(surface, color, (sx, sy), 2)
        
        # 端点小孢子
        pygame.draw.circle(surface, color, (ex, ey), 5)
        pygame.draw.circle(surface, (200, 255, 255), (ex, ey), 3)


def _draw_void_tendrils(surface, cx, cy, size, t):
    """绘制虚空触须"""
    for i in range(4):
        angle = i * 90 + t * 30
        
        # 弯曲触须
        points = []
        for j in range(5):
            progress = j / 4
            dist = size + progress * 15
            wave = math.sin(t * 3 + j + i) * 5 * progress
            px = cx + int(math.cos(math.radians(angle + wave)) * dist)
            py = cy + int(math.sin(math.radians(angle + wave)) * dist)
            points.append((px, py))
        
        if len(points) >= 2:
            pygame.draw.lines(surface, (80, 60, 100), False, points, 2)