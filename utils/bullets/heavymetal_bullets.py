# -*- coding: utf-8 -*-
"""
================================================================================
  🎸 维那斯万岁 · HEAVY METAL - 武器与技能系统
================================================================================
  核心理念: 声波干扰，节奏攻击
  被动: 节拍同步 (BPM Sync)
  普攻: 音符机炮 (Note Blaster)
  技能: 强力和弦 (Power Chord)
  辅助: 安可 (Encore)
  终极奥义:
    - 舞台跳水 (Stage Dive)
    - 回音墙 (Echo Wall)
    - 死亡金属独奏 (Death Metal Solo)
================================================================================
"""

import pygame
import math
import random
from typing import List, Tuple, Optional

# 从config导入精灵组（避免循环导入）
from config import all_sprites, bullets, mobs, enemy_bullets, WIDTH, HEIGHT

# ============================================================
#   性能优化：预计算常量和缓存
# ============================================================
# 预计算三角函数表（避免每帧重复计算）
_SIN_TABLE = [math.sin(i * 0.01) for i in range(629)]  # 0 to 2π
_COS_TABLE = [math.cos(i * 0.01) for i in range(629)]

def _fast_sin(x):
    """快速正弦函数，使用查表"""
    idx = int((x % 6.28318) * 100) % 629
    return _SIN_TABLE[idx]

def _fast_cos(x):
    """快速余弦函数，使用查表"""
    idx = int((x % 6.28318) * 100) % 629
    return _COS_TABLE[idx]

# 预计算屏幕相关常量
_HALF_WIDTH = WIDTH // 2
_HALF_HEIGHT = HEIGHT // 2
_WIDTH_SCALED = WIDTH * 0.15
_HEIGHT_SCALED = HEIGHT * 0.15

# 延迟导入FloatingText
effects = None
FloatingText = None

def _get_effects_group():
    global effects, FloatingText
    if effects is None:
        try:
            from sprites import effects as eff, FloatingText as FT
            effects = eff
            FloatingText = FT
        except ImportError:
            effects = all_sprites  # fallback
            FloatingText = None
    return effects, FloatingText

# ============================================================
#   颜色配置
# ============================================================
HEAVYMETAL_COLORS = {
    "neon_purple": (148, 0, 211),
    "laser_green": (0, 255, 0),
    "hot_pink": (255, 0, 128),
    "cyan": (0, 255, 255),
    "orange": (255, 150, 0),
    "white": (255, 255, 255),
    "note_colors": [
        (255, 0, 128),    # 粉红
        (0, 255, 128),    # 青绿
        (255, 200, 0),    # 金黄
        (128, 0, 255),    # 紫色
        (0, 200, 255),    # 天蓝
    ],
}


# ============================================================
#   普攻：音符机炮 (Note Blaster)
# ============================================================
class NoteBullet(pygame.sprite.Sprite):
    """
    音符子弹 - 正弦波轨迹飞行的彩色音符
    
    视觉: 八分音符♪ 和十六分音符♬
    特性: 弹道呈正弦波上下波动
    """
    
    def __init__(self, x: float, y: float, angle: float = -90, speed: float = 10,
                 damage: int = 12, note_type: int = 0, on_beat: bool = False, **kwargs):
        super().__init__()
        self.x = x
        self.y = y
        self.base_x = x  # 基准X位置（用于正弦波计算）
        self.damage = damage
        self.is_enemy = False
        self.piercing = 0
        self.on_beat = on_beat  # 节拍命中加成
        
        # 运动参数
        self.angle = math.radians(angle)
        self.speed = speed
        self.wave_amplitude = 25  # 波动振幅
        self.wave_frequency = 0.15  # 波动频率
        self.distance_traveled = 0
        
        # 音符类型和颜色
        self.note_type = note_type % 2  # 0=八分音符, 1=十六分音符
        self.color = HEAVYMETAL_COLORS["note_colors"][note_type % 5]
        
        # 动画
        self.lifetime = 0
        self.rotation = random.uniform(0, 360)
        
        # 创建Surface
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        bullets.add(self)
        all_sprites.add(self)
        
        self._render()
    
    def update(self):
        self.lifetime += 1
        
        # 计算移动
        move_x = math.cos(self.angle) * self.speed
        move_y = math.sin(self.angle) * self.speed
        
        self.distance_traveled += self.speed
        
        # 正弦波偏移
        wave_offset = math.sin(self.distance_traveled * self.wave_frequency) * self.wave_amplitude
        
        # 垂直于运动方向的偏移
        perp_angle = self.angle + math.pi / 2
        offset_x = math.cos(perp_angle) * wave_offset
        offset_y = math.sin(perp_angle) * wave_offset
        
        self.x += move_x
        self.y += move_y
        
        # 应用波动偏移到显示位置
        display_x = self.x + offset_x
        display_y = self.y + offset_y
        
        self.rect.center = (int(display_x), int(display_y))
        
        # 旋转动画
        self.rotation += 5
        
        # 超出屏幕销毁
        if self.y < -50 or self.y > HEIGHT + 50 or self.x < -50 or self.x > WIDTH + 50:
            self.kill()
            return
        
        self._render()
    
    def _render(self):
        """渲染音符"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = 20, 20
        
        pulse = 0.8 + 0.2 * _fast_sin(self.lifetime * 0.3)
        
        # 节拍命中时更亮的效果
        if self.on_beat:
            pulse = 1.0 + 0.3 * _fast_sin(self.lifetime * 0.5)
        
        # 外发光（减少层数：2 -> 1）
        glow_size = int(16 * pulse)
        glow_alpha = 100 if self.on_beat else 70
        pygame.draw.circle(self.image, (*self.color, glow_alpha), (cx, cy), glow_size)
        
        if self.note_type == 0:
            # 八分音符 ♪
            pygame.draw.ellipse(self.image, self.color, (cx - 6, cy + 2, 12, 8))
            pygame.draw.line(self.image, self.color, (cx + 5, cy + 5), (cx + 5, cy - 10), 2)
        else:
            # 十六分音符 ♬ (简化)
            pygame.draw.ellipse(self.image, self.color, (cx - 8, cy + 3, 8, 6))
            pygame.draw.ellipse(self.image, self.color, (cx + 2, cy + 3, 8, 6))
            pygame.draw.line(self.image, self.color, (cx - 4, cy + 5), (cx - 4, cy - 6), 2)
            pygame.draw.line(self.image, self.color, (cx + 6, cy + 5), (cx + 6, cy - 6), 2)


# ============================================================
#   核心技能：强力和弦 (Power Chord)
# ============================================================
class PowerChordWave(pygame.sprite.Sprite):
    """
    强力和弦冲击波 - 锥形声波力场
    
    效果:
    - 防御: 震碎力场内所有敌方子弹
    - 攻击: 推开靠近的敌人并造成伤害
    """
    
    def __init__(self, x: float, y: float, damage: int = 30, **kwargs):
        super().__init__()
        self.x = x
        self.y = y
        self.damage = damage
        self.is_enemy = False
        self.piercing = 999
        
        # 冲击波参数
        self.cone_angle = 90  # 锥形角度（度）
        self.max_radius = 250
        self.current_radius = 0
        self.expand_speed = 20
        self.lifetime = 0
        self.max_lifetime = 20
        
        # 消弹范围
        self.bullet_clear_radius = 200
        
        # 创建大Surface - 尺寸基于最大半径，rect中心就是玩家位置
        surf_size = self.max_radius * 2 + 100
        self.image = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        bullets.add(self)
        all_sprites.add(self)
    
    def update(self):
        self.lifetime += 1
        self.current_radius = min(self.max_radius, self.current_radius + self.expand_speed)
        
        if self.lifetime > self.max_lifetime:
            self.kill()
            return
        
        # 消除敌方子弹
        self._clear_enemy_bullets()
        
        # 推开敌人
        self._push_enemies()
        
        self._render()
    
    def _clear_enemy_bullets(self):
        """消除范围内的敌方子弹"""
        for bullet in bullets:
            if hasattr(bullet, 'is_enemy') and bullet.is_enemy:
                if hasattr(bullet, 'rect'):
                    dx = bullet.rect.centerx - self.x
                    dy = bullet.rect.centery - self.y
                    dist = math.sqrt(dx * dx + dy * dy)
                    
                    # 检查是否在锥形范围内
                    if dist < self.current_radius and dy < 0:  # 向前（向上）
                        angle = math.degrees(math.atan2(-dy, dx))
                        if 90 - self.cone_angle / 2 < angle < 90 + self.cone_angle / 2:
                            bullet.kill()
    
    def _push_enemies(self):
        """推开敌人"""
        push_force = 8
        for enemy in mobs:
            if hasattr(enemy, 'rect') and hasattr(enemy, 'hp'):
                dx = enemy.rect.centerx - self.x
                dy = enemy.rect.centery - self.y
                dist = math.sqrt(dx * dx + dy * dy)
                
                if dist < self.current_radius and dist > 0:
                    # 计算推力方向
                    push_x = (dx / dist) * push_force
                    push_y = (dy / dist) * push_force
                    
                    enemy.rect.x += int(push_x)
                    enemy.rect.y += int(push_y)
                    
                    # 造成伤害（只在第一帧）
                    if self.lifetime == 1:
                        enemy.hp -= self.damage
    
    def _render(self):
        """渲染锥形声波"""
        self.image.fill((0, 0, 0, 0))
        # Surface中心 (基于max_radius计算)
        surf_size = self.max_radius * 2 + 100
        cx, cy = surf_size // 2, surf_size // 2
        
        progress = self.current_radius / self.max_radius
        fade = 1 - (self.lifetime / self.max_lifetime)
        
        # 绘制多层锥形波
        for layer in range(5):
            layer_radius = self.current_radius * (1 - layer * 0.15)
            layer_alpha = int(150 * fade * (1 - layer * 0.15))
            
            if layer_radius > 0 and layer_alpha > 0:
                # 锥形顶点在中心，向上展开
                half_angle = math.radians(self.cone_angle / 2)
                
                # 计算锥形边界点
                left_x = cx - int(math.sin(half_angle) * layer_radius)
                left_y = cy - int(math.cos(half_angle) * layer_radius)
                right_x = cx + int(math.sin(half_angle) * layer_radius)
                right_y = cy - int(math.cos(half_angle) * layer_radius)
                
                # 绘制锥形（用弧线和三角形）
                cone_points = [(cx, cy)]
                arc_segments = 20
                for i in range(arc_segments + 1):
                    seg_angle = -math.pi / 2 - half_angle + (2 * half_angle * i / arc_segments)
                    px = cx + int(math.cos(seg_angle) * layer_radius)
                    py = cy + int(math.sin(seg_angle) * layer_radius)
                    cone_points.append((px, py))
                
                # 锥形颜色（紫色渐变）
                color = (148, 0, 211)
                if layer == 0:
                    color = (255, 255, 255)
                elif layer == 1:
                    color = (200, 100, 255)
                
                if len(cone_points) >= 3:
                    pygame.draw.polygon(self.image, (*color, layer_alpha), cone_points)
        
        # 声波纹理线
        wave_count = 8
        for w in range(wave_count):
            wave_radius = self.current_radius * (w + 1) / wave_count
            wave_alpha = int(100 * fade * (1 - w / wave_count))
            
            if wave_alpha > 0:
                half_angle = math.radians(self.cone_angle / 2)
                start_angle = -math.pi / 2 - half_angle
                end_angle = -math.pi / 2 + half_angle
                
                # 绘制弧线
                arc_rect = pygame.Rect(cx - wave_radius, cy - wave_radius,
                                      wave_radius * 2, wave_radius * 2)
                pygame.draw.arc(self.image, (255, 255, 255, wave_alpha),
                              arc_rect, start_angle, end_angle, 2)
        
        # 更新rect位置 - 与初始化保持一致
        self.rect.center = (int(self.x), int(self.y))


# ============================================================
#   辅助攻击：安可 (Encore) - 烟花弹幕
# ============================================================
class EncoreFirework(pygame.sprite.Sprite):
    """
    安可烟花 - 连击达到100时触发的四周烟花弹幕
    """
    
    def __init__(self, x: float, y: float, angle: float, speed: float = 8,
                 damage: int = 15, color: Tuple[int, int, int] = None, **kwargs):
        super().__init__()
        self.x = x
        self.y = y
        self.damage = damage
        self.is_enemy = False
        self.piercing = 1
        
        self.angle = math.radians(angle)
        self.speed = speed
        self.lifetime = 0
        self.max_lifetime = 60
        
        self.color = color or random.choice(HEAVYMETAL_COLORS["note_colors"])
        self.trail = []
        
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        bullets.add(self)
        all_sprites.add(self)
    
    def update(self):
        self.lifetime += 1
        
        if self.lifetime > self.max_lifetime:
            self.kill()
            return
        
        # 移动
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # 记录轨迹
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        self.rect.center = (int(self.x), int(self.y))
        
        # 超出屏幕
        if self.x < -50 or self.x > WIDTH + 50 or self.y < -50 or self.y > HEIGHT + 50:
            self.kill()
            return
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 15, 15
        
        pulse = 0.8 + 0.2 * math.sin(self.lifetime * 0.5)
        
        # 烟花头部
        pygame.draw.circle(self.image, (*self.color, 255), (cx, cy), int(6 * pulse))
        pygame.draw.circle(self.image, (255, 255, 255, 200), (cx, cy), int(3 * pulse))
        
        # 发光
        pygame.draw.circle(self.image, (*self.color, 100), (cx, cy), int(10 * pulse))


def spawn_encore_fireworks(x: float, y: float, count: int = 16, damage: int = 15):
    """生成一圈烟花弹幕"""
    for i in range(count):
        angle = i * (360 / count)
        color = HEAVYMETAL_COLORS["note_colors"][i % len(HEAVYMETAL_COLORS["note_colors"])]
        EncoreFirework(x, y, angle, speed=10, damage=damage, color=color)


# ============================================================
#   终极奥义 I：舞台跳水 (Stage Dive)
# ============================================================
class StageDiveMeteor(pygame.sprite.Sprite):
    """
    舞台跳水 - 火焰包裹的陨石撞击
    """
    
    def __init__(self, start_x: float, start_y: float, 
                 target_x: float, target_y: float, damage: int = 200, **kwargs):
        super().__init__()
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.x = start_x
        self.y = start_y
        self.damage = damage
        self.is_enemy = False
        self.piercing = 999
        
        # 计算运动
        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.sqrt(dx * dx + dy * dy)
        self.speed = 25
        self.vx = (dx / dist) * self.speed if dist > 0 else 0
        self.vy = (dy / dist) * self.speed if dist > 0 else self.speed
        
        self.lifetime = 0
        self.exploded = False
        self.explosion_radius = 150
        self.explosion_lifetime = 0
        
        self.trail = []
        
        self.image = pygame.Surface((300, 300), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        
        eff, _ = _get_effects_group()
        eff.add(self)
        all_sprites.add(self)
    
    def update(self):
        self.lifetime += 1
        
        if not self.exploded:
            # 移动
            self.x += self.vx
            self.y += self.vy
            
            # 记录轨迹
            self.trail.append((int(self.x), int(self.y)))
            if len(self.trail) > 20:
                self.trail.pop(0)
            
            # 到达目标点
            if self.y >= self.target_y:
                self.exploded = True
                self._deal_explosion_damage()
        else:
            self.explosion_lifetime += 1
            if self.explosion_lifetime > 30:
                self.kill()
                return
        
        self.rect.center = (int(self.x), int(self.y))
        self._render()
    
    def _deal_explosion_damage(self):
        """爆炸伤害"""
        for enemy in mobs:
            if hasattr(enemy, 'rect') and hasattr(enemy, 'hp'):
                dx = enemy.rect.centerx - self.x
                dy = enemy.rect.centery - self.y
                dist = math.sqrt(dx * dx + dy * dy)
                
                if dist < self.explosion_radius:
                    damage_mult = 1 - (dist / self.explosion_radius) * 0.5
                    enemy.hp -= int(self.damage * damage_mult)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 150, 150
        
        if not self.exploded:
            # 火焰陨石
            meteor_size = 30
            
            # 外焰
            pygame.draw.circle(self.image, (255, 100, 0, 150), (cx, cy), meteor_size + 15)
            pygame.draw.circle(self.image, (255, 200, 0, 200), (cx, cy), meteor_size + 8)
            pygame.draw.circle(self.image, (255, 255, 100, 255), (cx, cy), meteor_size)
            pygame.draw.circle(self.image, (255, 255, 255, 255), (cx, cy), meteor_size - 10)
            
            # 火焰拖尾
            for i, (tx, ty) in enumerate(self.trail):
                trail_cx = tx - int(self.x) + cx
                trail_cy = ty - int(self.y) + cy
                trail_progress = i / len(self.trail)
                trail_size = int(meteor_size * (1 - trail_progress * 0.7))
                trail_alpha = int(200 * (1 - trail_progress))
                
                pygame.draw.circle(self.image, (255, 150, 0, trail_alpha),
                                 (trail_cx, trail_cy), trail_size)
        else:
            # 爆炸效果
            progress = self.explosion_lifetime / 30
            current_radius = int(self.explosion_radius * min(1, progress * 2))
            fade = 1 - progress
            
            # 多层爆炸环
            for ring in range(5):
                ring_radius = current_radius * (1 - ring * 0.15)
                ring_alpha = int(200 * fade * (1 - ring * 0.15))
                
                if ring_alpha > 0:
                    colors = [(255, 255, 255), (255, 255, 100), (255, 200, 0),
                             (255, 100, 0), (200, 50, 0)]
                    pygame.draw.circle(self.image, (*colors[ring], ring_alpha),
                                     (cx, cy), int(ring_radius))
            
            # 爆炸碎片
            for i in range(16):
                frag_angle = i * 0.393 + self.explosion_lifetime * 0.1
                frag_dist = current_radius * 0.8
                frag_x = cx + int(math.cos(frag_angle) * frag_dist)
                frag_y = cy + int(math.sin(frag_angle) * frag_dist)
                frag_size = int(8 * fade)
                
                if frag_size > 0:
                    pygame.draw.circle(self.image, (255, 200, 50, int(255 * fade)),
                                     (frag_x, frag_y), frag_size)


# ============================================================
#   终极奥义 II：回音墙 (Echo Wall)
# ============================================================
class EchoClone(pygame.sprite.Sprite):
    """
    回音墙分身 - 模仿本体射击的全息投影
    """
    
    def __init__(self, owner, offset_x: int, duration: int = 300, **kwargs):
        super().__init__()
        self.owner = owner
        self.offset_x = offset_x
        self.duration = duration
        self.lifetime = 0
        self.shoot_cooldown = 0
        self.shoot_interval = 10
        
        self.image = pygame.Surface((60, 80), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        eff, _ = _get_effects_group()
        eff.add(self)
        all_sprites.add(self)
    
    def update(self):
        self.lifetime += 1
        
        if self.lifetime > self.duration or not self.owner.alive():
            self.kill()
            return
        
        # 跟随本体位置
        if hasattr(self.owner, 'rect'):
            self.rect.centerx = self.owner.rect.centerx + self.offset_x
            self.rect.centery = self.owner.rect.centery
        
        # 射击（模仿本体）
        self.shoot_cooldown -= 1
        if self.shoot_cooldown <= 0:
            self._shoot()
            self.shoot_cooldown = self.shoot_interval
        
        self._render()
    
    def _shoot(self):
        """分身射击"""
        note_type = random.randint(0, 4)
        NoteBullet(self.rect.centerx, self.rect.top, 
                  angle=-90, speed=12, damage=8, note_type=note_type)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 30, 40
        
        # 全息投影效果（半透明 + 扫描线）
        alpha = int(150 * (0.7 + 0.3 * math.sin(self.lifetime * 0.1)))
        
        # 简化的机体轮廓
        body_color = (0, 255, 255, alpha)
        
        # 琴身
        pygame.draw.ellipse(self.image, body_color, (cx - 20, cy - 25, 40, 50))
        
        # 琴颈
        pygame.draw.rect(self.image, body_color, (cx - 5, cy - 50, 10, 30))
        
        # 扫描线效果
        scan_y = (self.lifetime * 3) % 80
        pygame.draw.line(self.image, (255, 255, 255, alpha // 2),
                        (0, scan_y), (60, scan_y), 2)
        
        # 闪烁边缘
        if self.lifetime % 10 < 5:
            pygame.draw.ellipse(self.image, (255, 255, 255, alpha // 3),
                              (cx - 22, cy - 27, 44, 54), 2)


def spawn_echo_wall(owner, duration: int = 300):
    """生成回音墙分身"""
    EchoClone(owner, offset_x=-80, duration=duration)
    EchoClone(owner, offset_x=80, duration=duration)


# ============================================================
#   终极奥义 III：死亡金属独奏 (Death Metal Solo)
# ============================================================
class DeathMetalSolo(pygame.sprite.Sprite):
    """
    死亡金属独奏 - 全屏音波攻击 + 混乱状态
    """
    
    def __init__(self, x: float, y: float, damage_per_tick: int = 5, 
                 duration: int = 180, **kwargs):
        super().__init__()
        self.x = x
        self.y = y
        self.damage_per_tick = damage_per_tick
        self.duration = duration
        self.lifetime = 0
        self.is_enemy = False
        
        self.wave_count = 0
        self.wave_interval = 15
        self.max_wave_radius = 400
        self.active_waves = []  # [(radius, age)]
        
        # 全屏覆盖 - 使用实际屏幕尺寸
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        eff, _ = _get_effects_group()
        eff.add(self)
        all_sprites.add(self)
    
    def update(self):
        self.lifetime += 1
        
        if self.lifetime > self.duration:
            self.kill()
            return
        
        # 生成新波
        if self.lifetime % self.wave_interval == 0:
            self.active_waves.append([0, 0])  # [radius, age]
        
        # 更新波
        new_waves = []
        for wave in self.active_waves:
            wave[0] += 15  # 扩展速度
            wave[1] += 1
            if wave[0] < self.max_wave_radius:
                new_waves.append(wave)
        self.active_waves = new_waves
        
        # 对敌人造成伤害和混乱
        if self.lifetime % 10 == 0:
            self._damage_and_confuse_enemies()
        
        self._render()
    
    def _damage_and_confuse_enemies(self):
        """伤害并混乱敌人"""
        for enemy in mobs:
            if hasattr(enemy, 'hp'):
                enemy.hp -= self.damage_per_tick
            
            # 混乱效果：随机改变位置
            if hasattr(enemy, 'rect'):
                enemy.rect.x += random.randint(-20, 20)
                enemy.rect.y += random.randint(-10, 10)
                
                # 限制在屏幕内
                enemy.rect.x = max(0, min(WIDTH - 40, enemy.rect.x))
                enemy.rect.y = max(0, min(HEIGHT - 40, enemy.rect.y))
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        
        # 整体暗化效果
        progress = self.lifetime / self.duration
        dark_alpha = int(100 * (1 - progress))
        pygame.draw.rect(self.image, (0, 0, 0, dark_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 聚光灯效果
        spotlight_alpha = int(50 + 30 * _fast_sin(self.lifetime * 0.2))
        pygame.draw.circle(self.image, (255, 255, 200, spotlight_alpha),
                         (int(self.x), int(self.y)), 80)
        
        # 绘制音波涟漪（减少层数）
        colors = [(255, 0, 255), (148, 0, 211), (100, 0, 150)]
        for wave in self.active_waves:
            radius, age = wave
            wave_alpha = int(200 * (1 - radius / self.max_wave_radius))
            
            if wave_alpha > 0:
                # 2层波纹（减少1层）
                for layer in range(2):
                    layer_r = radius - layer * 8
                    if layer_r > 0:
                        layer_alpha = max(0, wave_alpha - layer * 60)
                        pygame.draw.circle(self.image, (*colors[layer], layer_alpha),
                                         (int(self.x), int(self.y)), int(layer_r), 3)
        
        # EQ条跳动效果（减少数量：32 -> 16）
        note_colors = HEAVYMETAL_COLORS["note_colors"]
        two_pi_16 = 2 * 3.14159 / 16
        for i in range(16):
            bar_angle = i * two_pi_16
            bar_height = 20 + 40 * abs(_fast_sin(self.lifetime * 0.3 + i * 1.0))
            cos_a = _fast_cos(bar_angle)
            sin_a = _fast_sin(bar_angle)
            bar_x = int(self.x + cos_a * 100)
            bar_y = int(self.y + sin_a * 100)
            end_x = int(self.x + cos_a * (100 + bar_height))
            end_y = int(self.y + sin_a * (100 + bar_height))
            
            pygame.draw.line(self.image, (*note_colors[i % 5], 200),
                           (bar_x, bar_y), (end_x, end_y), 4)
        
        # 屏幕震动指示（边缘闪烁）
        if self.lifetime % 4 < 2:
            pygame.draw.rect(self.image, (255, 0, 0, 80), (0, 0, WIDTH, HEIGHT), 5)


# ============================================================
#   技能管理器
# ============================================================
class HeavyMetalSkillManager:
    """HEAVY METAL技能管理器"""
    
    def __init__(self, owner):
        self.owner = owner
        self.combo_count = 0
        self.bpm = 120
        self.beat_bonus_window = 0
        
        # 冷却时间
        self.power_chord_cooldown = 0
        self.power_chord_max_cd = 120
        
        self.encore_triggered = False
    
    def update(self):
        """每帧更新"""
        # BPM节拍检测
        beat_interval = 60 / self.bpm * 60  # 帧
        self.beat_bonus_window = max(0, self.beat_bonus_window - 1)
        
        # 简化的节拍检测
        if pygame.time.get_ticks() % int(beat_interval * 16.67) < 100:
            self.beat_bonus_window = 10  # 10帧窗口
        
        # 冷却
        self.power_chord_cooldown = max(0, self.power_chord_cooldown - 1)
        
        # 连击检测安可
        if self.combo_count >= 100 and not self.encore_triggered:
            self.trigger_encore()
            self.encore_triggered = True
        
        if self.combo_count < 100:
            self.encore_triggered = False
    
    def fire_note(self) -> bool:
        """发射音符，返回是否获得节拍加成"""
        if hasattr(self.owner, 'rect'):
            x = self.owner.rect.centerx
            y = self.owner.rect.top
            
            note_type = random.randint(0, 4)
            damage = 12
            
            # 节拍加成
            if self.beat_bonus_window > 0:
                damage = int(damage * 1.2)
            
            NoteBullet(x, y, angle=-90, speed=12, damage=damage, note_type=note_type)
            return self.beat_bonus_window > 0
        return False
    
    def use_power_chord(self) -> bool:
        """使用强力和弦"""
        if self.power_chord_cooldown > 0:
            return False
        
        if hasattr(self.owner, 'rect'):
            PowerChordWave(self.owner.rect.centerx, self.owner.rect.centery, damage=30)
            self.power_chord_cooldown = self.power_chord_max_cd
            return True
        return False
    
    def trigger_encore(self):
        """触发安可"""
        if hasattr(self.owner, 'rect'):
            spawn_encore_fireworks(self.owner.rect.centerx, self.owner.rect.centery,
                                  count=16, damage=15)
    
    def use_stage_dive(self, target_x: float, target_y: float) -> bool:
        """使用舞台跳水"""
        if hasattr(self.owner, 'rect'):
            StageDiveMeteor(self.owner.rect.centerx, -50,
                           target_x, target_y, damage=200)
            return True
        return False
    
    def use_echo_wall(self) -> bool:
        """使用回音墙"""
        spawn_echo_wall(self.owner, duration=300)
        return True
    
    def use_death_metal_solo(self) -> bool:
        """使用死亡金属独奏"""
        if hasattr(self.owner, 'rect'):
            DeathMetalSolo(self.owner.rect.centerx, self.owner.rect.centery,
                          damage_per_tick=5, duration=180)
            return True
        return False
    
    def add_combo(self, count: int = 1):
        """增加连击数"""
        self.combo_count += count
    
    def reset_combo(self):
        """重置连击"""
        self.combo_count = 0


# ============================================================
#   大招：死亡金属独奏 (F技能版本)
# ============================================================
class DeathMetalSoloUlt(pygame.sprite.Sprite):
    """
    死亡金属独奏 - 大招版本
    全屏持续音波攻击 + 混乱状态 + 12个涂装视觉差异
    """
    
    def __init__(self, x: float, y: float, damage: float = 10,
                 owner=None, style: str = "heavymetal_default", **kwargs):
        super().__init__()
        self.x = x
        self.y = y
        self.base_damage = damage
        self.owner = owner
        self.style = style
        self.is_enemy = False
        
        # 从样式获取颜色
        self._setup_style_colors()
        
        self.duration = 300  # 5秒
        self.lifetime = 0
        
        self.wave_count = 0
        self.wave_interval = 12
        self.max_wave_radius = 500
        self.active_waves = []  # [(radius, age, color_idx)]
        
        # 舞台效果
        self.strobe_timer = 0
        self.speaker_pulse = 0
        
        # 音符雨
        self.note_spawn_timer = 0
        
        # 全屏覆盖 - 使用实际屏幕尺寸
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        # 性能优化：预计算常量
        self._eq_bar_width = WIDTH // 24 - 2
        self._eq_bar_positions = [int(i * WIDTH / 24) for i in range(24)]
        self._string_y_positions = [HEIGHT // 3 + i * 40 for i in range(6)]
        self._render_frame = 0  # 用于隔帧渲染某些效果
        
        # 预计算颜色渐变
        self._eq_colors = []
        for i in range(24):
            t = i / 24
            r = int(self.primary_color[0] * (1 - t) + self.secondary_color[0] * t)
            g = int(self.primary_color[1] * (1 - t) + self.secondary_color[1] * t)
            b = int(self.primary_color[2] * (1 - t) + self.secondary_color[2] * t)
            self._eq_colors.append((r, g, b))
        
        eff, _ = _get_effects_group()
        eff.add(self)
        all_sprites.add(self)
    
    def _setup_style_colors(self):
        """根据涂装设置颜色"""
        # 简化：直接定义主题颜色
        theme_colors = {
            "heavymetal_default": ((148, 0, 211), (0, 255, 0), (255, 0, 128)),
            "heavymetal_bloody": ((255, 0, 0), (255, 100, 0), (255, 50, 50)),
            "heavymetal_cyber": ((0, 150, 255), (0, 255, 255), (100, 200, 255)),
            "heavymetal_golden": ((255, 200, 0), (255, 150, 0), (255, 230, 100)),
            "heavymetal_psychedelic": ((255, 0, 255), (150, 0, 255), (255, 100, 255)),
            "heavymetal_toxic": ((0, 255, 0), (150, 255, 0), (100, 255, 100)),
            "heavymetal_frost": ((150, 220, 255), (255, 255, 255), (200, 240, 255)),
            "heavymetal_hellfire": ((255, 100, 0), (255, 200, 0), (255, 150, 50)),
            "heavymetal_midnight": ((50, 50, 200), (100, 100, 255), (80, 80, 230)),
            "heavymetal_rainbow": ((255, 100, 100), (100, 255, 100), (100, 100, 255)),
            "heavymetal_steampunk": ((200, 150, 50), (255, 200, 100), (220, 180, 80)),
            "heavymetal_starpunk": ((255, 100, 200), (100, 200, 255), (200, 150, 255)),
        }
        colors = theme_colors.get(self.style, theme_colors["heavymetal_default"])
        self.primary_color = colors[0]
        self.secondary_color = colors[1]
        self.tertiary_color = colors[2]
    
    def update(self):
        self.lifetime += 1
        self.strobe_timer += 1
        self.speaker_pulse += 0.2
        
        if self.lifetime > self.duration:
            self.kill()
            return
        
        # 生成新波
        if self.lifetime % self.wave_interval == 0:
            color_idx = self.wave_count % 3
            self.active_waves.append([0, 0, color_idx])
            self.wave_count += 1
        
        # 更新波
        new_waves = []
        for wave in self.active_waves:
            wave[0] += 18  # 扩展速度
            wave[1] += 1
            if wave[0] < self.max_wave_radius:
                new_waves.append(wave)
        self.active_waves = new_waves
        
        # 生成音符弹幕雨
        self.note_spawn_timer += 1
        if self.note_spawn_timer >= 8:
            self.note_spawn_timer = 0
            self._spawn_note_rain()
        
        # 对敌人造成伤害和混乱
        if self.lifetime % 8 == 0:
            self._damage_and_confuse_enemies()
        
        self._render()
    
    def _spawn_note_rain(self):
        """生成音符雨"""
        x = random.randint(50, WIDTH - 50)
        y = random.randint(-20, 50)
        NoteBullet(x, y, damage=self.base_damage * 0.5, 
                  note_type=random.randint(0, 3), on_beat=True)
    
    def _damage_and_confuse_enemies(self):
        """伤害并混乱敌人"""
        progress = self.lifetime / self.duration
        damage_mult = 1.0 + progress * 0.5  # 伤害随时间增加
        
        for enemy in mobs:
            if hasattr(enemy, 'hp'):
                enemy.hp -= self.base_damage * damage_mult
                
                # 创建伤害数字
                _, FT = _get_effects_group()
                if self.lifetime % 30 == 0 and hasattr(enemy, 'rect') and FT:
                    FT(enemy.rect.centerx, enemy.rect.top - 10,
                       f"🎸{int(self.base_damage * damage_mult)}", self.primary_color)
            
            # 混乱效果：随机改变位置
            if hasattr(enemy, 'rect'):
                confuse_strength = 15 + int(10 * progress)
                enemy.rect.x += random.randint(-confuse_strength, confuse_strength)
                enemy.rect.y += random.randint(-confuse_strength // 2, confuse_strength // 2)
                
                # 限制在屏幕内
                enemy.rect.x = max(0, min(WIDTH - 40, enemy.rect.x))
                enemy.rect.y = max(0, min(HEIGHT - 40, enemy.rect.y))
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        self._render_frame += 1
        
        progress = self.lifetime / self.duration
        # 使用快速三角函数
        intensity = 1.0 + 0.5 * _fast_sin(self.lifetime * 0.1)
        
        # ========== 1. 全屏背景震动效果（隔帧更新） ==========
        shake_x = int(random.randint(-3, 3) * (1 - progress))
        shake_y = int(random.randint(-2, 2) * (1 - progress))
        
        # 暗红色渐变背景 - 减少绘制频率，每40像素一条
        if self._render_frame % 2 == 0:
            bg_alpha_base = int(40 * (1 - progress))
            for y in range(0, HEIGHT, 40):
                bg_alpha = int(bg_alpha_base * (1 + 0.3 * _fast_sin(y * 0.02 + self.lifetime * 0.1)))
                pygame.draw.rect(self.image, (*self.primary_color, bg_alpha), (0, y, WIDTH, 40))
        
        # ========== 2. 超强频闪灯光 ==========
        strobe_phase = (self.strobe_timer // 2) % 4
        if strobe_phase == 0:
            strobe_alpha = int(80 * intensity)
            pygame.draw.rect(self.image, (*self.primary_color, strobe_alpha), (0, 0, WIDTH, HEIGHT))
        elif strobe_phase == 1:
            strobe_alpha = int(60 * intensity)
            pygame.draw.rect(self.image, (*self.secondary_color, strobe_alpha), (0, 0, WIDTH, HEIGHT))
        elif strobe_phase == 2:
            strobe_alpha = int(50 * intensity)
            pygame.draw.rect(self.image, (*self.tertiary_color, strobe_alpha), (0, 0, WIDTH, HEIGHT))
        
        # ========== 3. 多重聚光灯扫射 ==========
        colors = [self.primary_color, self.secondary_color, self.tertiary_color]
        for spot_idx in range(3):
            spot_phase = self.lifetime * 0.08 + spot_idx * 2.1
            spotlight_x = _HALF_WIDTH + int(_WIDTH_SCALED * _fast_sin(spot_phase))
            spotlight_y = _HALF_HEIGHT + int(_HEIGHT_SCALED * _fast_cos(spot_phase * 0.7))
            
            spot_color = colors[spot_idx]
            spot_intensity = 0.6 + 0.4 * _fast_sin(self.lifetime * 0.15 + spot_idx)
            
            # 减少层数：5 -> 3
            for r in range(3):
                spot_alpha = int((70 - r * 20) * intensity * spot_intensity)
                if spot_alpha > 0:
                    pygame.draw.circle(self.image, (*spot_color, spot_alpha),
                                     (spotlight_x + shake_x, spotlight_y + shake_y), 
                                     60 + r * 40)
        
        # ========== 4. 巨型音波涟漪 ==========
        for wave in self.active_waves:
            radius, age, color_idx = wave
            wave_progress = radius / self.max_wave_radius
            wave_alpha = int(220 * (1 - wave_progress) * intensity)
            
            if wave_alpha > 0:
                wave_color = colors[color_idx]
                
                # 减少层数：5 -> 3
                for layer in range(3):
                    layer_r = int(radius - layer * 18)
                    if layer_r > 0:
                        layer_alpha = max(0, wave_alpha - layer * 55)
                        pygame.draw.circle(self.image, (*wave_color, layer_alpha),
                                         (int(self.x) + shake_x, int(self.y) + shake_y), 
                                         layer_r, max(2, 6 - layer * 2))
        
        # ========== 5. 超级EQ条形图（使用预计算） ==========
        bar_alpha = int(200 * (1 - progress * 0.3))
        for side_y in [0, 1]:
            for i in range(24):
                freq_response = abs(_fast_sin(self.lifetime * 0.2 + i * 0.4)) * \
                               abs(_fast_cos(self.lifetime * 0.15 + i * 0.3))
                bar_height = int(30 + 80 * freq_response * intensity)
                
                bar_x = self._eq_bar_positions[i]
                bar_y = HEIGHT - bar_height if side_y == 0 else 0
                
                pygame.draw.rect(self.image, (*self._eq_colors[i], bar_alpha),
                               (bar_x, bar_y, self._eq_bar_width, bar_height))
        
        # ========== 6. 飞舞的巨型音符（减少数量：12 -> 8） ==========
        for i in range(8):
            phase = self.lifetime * 0.025 + i * 0.785
            orbit_radius = 120 + 80 * _fast_sin(i * 0.8)
            note_x = int(_HALF_WIDTH + orbit_radius * _fast_cos(phase))
            note_y = int(_HALF_HEIGHT + orbit_radius * 0.6 * _fast_sin(phase))
            
            note_alpha = int((180 + 70 * _fast_sin(self.lifetime * 0.12 + i)) * intensity)
            note_size = int(12 + 8 * _fast_sin(self.lifetime * 0.1 + i * 0.5))
            
            glow_color = colors[i % 3]
            # 减少发光层：3 -> 2
            for glow in range(2):
                glow_alpha = max(0, note_alpha - glow * 70)
                pygame.draw.circle(self.image, (*glow_color, glow_alpha),
                                 (note_x, note_y), note_size + glow * 8)
            
            # 音符核心
            pygame.draw.circle(self.image, (255, 255, 255, min(255, note_alpha + 50)),
                             (note_x, note_y), note_size // 2)
        
        # ========== 7. 电吉他弦振动效果（降低采样：8 -> 16像素） ==========
        for string_idx in range(6):
            string_y = self._string_y_positions[string_idx]
            amplitude = 15 + 10 * _fast_sin(self.lifetime * 0.3 + string_idx)
            string_alpha = int(150 * intensity)
            
            points = []
            phase_offset = self.lifetime * 0.4 + string_idx * 0.5
            for x in range(0, WIDTH + 1, 16):  # 16像素采样
                wave = amplitude * _fast_sin(x * 0.05 + phase_offset)
                points.append((x, int(string_y + wave)))
            
            if len(points) >= 2:
                string_color = colors[string_idx % 3]
                pygame.draw.lines(self.image, (*string_color, string_alpha), False, points, 3)
        
        # ========== 8. 中央爆发核心（减少层数：6 -> 4） ==========
        core_pulse = 0.7 + 0.3 * _fast_sin(self.lifetime * 0.25)
        core_size = int(50 * core_pulse * intensity)
        
        # 核心光晕
        for ring in range(4):
            ring_alpha = max(0, int((180 - ring * 40) * core_pulse))
            ring_size = core_size + ring * 30
            pygame.draw.circle(self.image, (*self.primary_color, ring_alpha),
                             (int(self.x) + shake_x, int(self.y) + shake_y), ring_size, 4)
        
        # 核心白色高亮
        pygame.draw.circle(self.image, (255, 255, 255, int(200 * core_pulse)),
                         (int(self.x), int(self.y)), core_size // 2)
        
        # ========== 9. 闪电效果（降低频率：30% -> 15%） ==========
        if random.random() < 0.15 * intensity:
            lightning_start = (random.randint(50, WIDTH - 50), 0)
            
            points = [lightning_start]
            current = list(lightning_start)
            while current[1] < HEIGHT:
                current[0] += random.randint(-40, 40)
                current[1] += random.randint(50, 80)  # 更大步长
                current[0] = max(10, min(WIDTH - 10, current[0]))
                points.append(tuple(current))
            
            if len(points) >= 2:
                pygame.draw.lines(self.image, (*self.secondary_color, 200), False, points, 3)
        
        # ========== 10. 屏幕边缘脉冲 ==========
        edge_pulse = int(60 * (0.5 + 0.5 * _fast_sin(self.lifetime * 0.2)) * intensity)
        pygame.draw.rect(self.image, (*self.primary_color, edge_pulse), (0, 0, WIDTH, HEIGHT), 10)


# ============================================================
#   G键技能：回音墙 (Echo Wall)
# ============================================================
class EchoWallSkill(pygame.sprite.Sprite):
    """
    回音墙 - G键技能
    释放多层环形声波护盾，反弹敌方子弹并造成持续伤害
    """
    
    def __init__(self, x: float, y: float, damage: float = 30, 
                 owner=None, style: str = "heavymetal_default", **kwargs):
        super().__init__()
        self.x = x
        self.y = y
        self.base_damage = damage
        self.owner = owner
        self.style = style
        self.is_enemy = False
        
        self.duration = 240  # 4秒
        self.lifetime = 0
        
        # 声波环参数
        self.rings = []  # [(radius, age, direction)]
        self.ring_spawn_timer = 0
        self.ring_interval = 20
        self.max_rings = 8
        
        # 颜色设置
        self._setup_colors()
        
        # 反弹统计
        self.bullets_reflected = 0
        
        # 全屏覆盖 - 使用实际屏幕尺寸
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        eff, _ = _get_effects_group()
        eff.add(self)
        all_sprites.add(self)
    
    def _setup_colors(self):
        theme_colors = {
            "heavymetal_default": ((148, 0, 211), (0, 255, 0)),
            "heavymetal_bloody": ((255, 0, 0), (255, 100, 0)),
            "heavymetal_cyber": ((0, 150, 255), (0, 255, 255)),
            "heavymetal_golden": ((255, 200, 0), (255, 150, 0)),
            "heavymetal_psychedelic": ((255, 0, 255), (150, 0, 255)),
            "heavymetal_toxic": ((0, 255, 0), (150, 255, 0)),
        }
        colors = theme_colors.get(self.style, theme_colors["heavymetal_default"])
        self.primary = colors[0]
        self.secondary = colors[1]
    
    def update(self):
        self.lifetime += 1
        
        if self.lifetime > self.duration:
            self.kill()
            return
        
        # 跟随玩家
        if self.owner and self.owner.alive():
            self.x = self.owner.rect.centerx
            self.y = self.owner.rect.centery
        
        # 生成新声波环
        self.ring_spawn_timer += 1
        if self.ring_spawn_timer >= self.ring_interval and len(self.rings) < self.max_rings:
            self.ring_spawn_timer = 0
            # 交替向内向外
            direction = 1 if len(self.rings) % 2 == 0 else -1
            start_radius = 50 if direction == 1 else 200
            self.rings.append([start_radius, 0, direction])
        
        # 更新声波环
        new_rings = []
        for ring in self.rings:
            ring[0] += ring[2] * 3  # 扩展或收缩
            ring[1] += 1
            if 30 < ring[0] < 250:
                new_rings.append(ring)
        self.rings = new_rings
        
        # 反弹敌方子弹
        self._reflect_bullets()
        
        # 对触碰敌人造成伤害
        self._damage_enemies()
        
        self._render()
    
    def _reflect_bullets(self):
        """反弹敌方子弹"""
        # 缓存自身坐标
        sx, sy = self.x, self.y
        for bullet in list(enemy_bullets):
            if hasattr(bullet, 'rect'):
                dx = bullet.rect.centerx - sx
                dy = bullet.rect.centery - sy
                dist_sq = dx * dx + dy * dy  # 避免sqrt
                
                # 检查是否在任何声波环范围内
                for ring in self.rings:
                    ring_r = ring[0]
                    # 使用平方比较避免sqrt
                    if abs(dist_sq - ring_r * ring_r) < ring_r * 30:
                        if hasattr(bullet, 'angle'):
                            bullet.angle = bullet.angle + 3.14159
                        bullet.is_enemy = False
                        enemy_bullets.remove(bullet)
                        bullets.add(bullet)
                        self.bullets_reflected += 1
                        break
    
    def _damage_enemies(self):
        """对声波环内敌人造成伤害"""
        if self.lifetime % 15 == 0:
            sx, sy = self.x, self.y
            damage = self.base_damage * 0.3
            for enemy in mobs:
                if hasattr(enemy, 'rect') and hasattr(enemy, 'hp'):
                    dx = enemy.rect.centerx - sx
                    dy = enemy.rect.centery - sy
                    dist_sq = dx * dx + dy * dy
                    
                    for ring in self.rings:
                        ring_r = ring[0]
                        if abs(dist_sq - ring_r * ring_r) < ring_r * 60:
                            enemy.hp -= damage
                            break
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        
        progress = self.lifetime / self.duration
        intensity = 1.0 - progress * 0.3
        ix, iy = int(self.x), int(self.y)
        
        # 中心光晕（减少层数：4 -> 2）
        for glow in range(2):
            glow_alpha = int((80 - glow * 30) * intensity)
            pygame.draw.circle(self.image, (*self.primary, glow_alpha),
                             (ix, iy), 40 + glow * 25)
        
        # 绘制声波环
        for ring in self.rings:
            radius, age, direction = ring
            ring_alpha = int(200 * (1 - abs(radius - 125) / 125) * intensity)
            
            if ring_alpha > 0:
                # 减少层数：3 -> 2
                for layer in range(2):
                    layer_r = int(radius - layer * 8 * direction)
                    layer_alpha = max(0, ring_alpha - layer * 80)
                    color = self.primary if direction == 1 else self.secondary
                    pygame.draw.circle(self.image, (*color, layer_alpha),
                                     (ix, iy), max(1, layer_r), max(1, 4 - layer * 2))
        
        # 音符粒子（减少数量：8 -> 6，使用快速三角）
        note_alpha = int(180 * intensity)
        pi_div_3 = 1.047  # π/3
        for i in range(6):
            angle = self.lifetime * 0.05 + i * pi_div_3
            dist = 80 + 40 * _fast_sin(self.lifetime * 0.1 + i)
            px = int(self.x + _fast_cos(angle) * dist)
            py = int(self.y + _fast_sin(angle) * dist)
            pygame.draw.circle(self.image, (*self.secondary, note_alpha), (px, py), 6)


# ============================================================
#   C键技能：地狱开场 (Hellish Opener)
# ============================================================
class HellishOpenerSkill(pygame.sprite.Sprite):
    """
    地狱开场 - C键技能
    全屏火焰+烟火+音波大爆炸，极致视觉冲击
    """
    
    def __init__(self, x: float, y: float, damage: float = 50,
                 owner=None, style: str = "heavymetal_default", **kwargs):
        super().__init__()
        self.x = x
        self.y = y
        self.base_damage = damage
        self.owner = owner
        self.style = style
        self.is_enemy = False
        
        self.duration = 180  # 3秒
        self.lifetime = 0
        
        # 爆炸阶段
        self.phase = 0  # 0=聚能, 1=爆发, 2=余波
        self.phase_timers = [30, 60, 90]  # 各阶段持续帧数
        
        # 火焰粒子
        self.flames = []
        self.explosions = []
        
        self._setup_colors()
        
        # 全屏覆盖 - 使用实际屏幕尺寸
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        eff, _ = _get_effects_group()
        eff.add(self)
        all_sprites.add(self)
    
    def _setup_colors(self):
        theme_colors = {
            "heavymetal_default": ((148, 0, 211), (0, 255, 0), (255, 0, 128)),
            "heavymetal_bloody": ((255, 0, 0), (255, 100, 0), (255, 50, 50)),
            "heavymetal_hellfire": ((255, 100, 0), (255, 200, 0), (255, 50, 0)),
        }
        colors = theme_colors.get(self.style, theme_colors["heavymetal_default"])
        self.primary = colors[0]
        self.secondary = colors[1]
        self.tertiary = colors[2]
    
    def update(self):
        self.lifetime += 1
        
        if self.lifetime > self.duration:
            self.kill()
            return
        
        # 更新阶段
        if self.lifetime < self.phase_timers[0]:
            self.phase = 0  # 聚能
        elif self.lifetime < self.phase_timers[0] + self.phase_timers[1]:
            self.phase = 1  # 爆发
            if self.lifetime == self.phase_timers[0]:
                self._trigger_explosion()
        else:
            self.phase = 2  # 余波
        
        # 生成火焰粒子
        if self.phase >= 1 and random.random() < 0.5:
            self.flames.append({
                'x': random.randint(50, WIDTH - 50),
                'y': random.randint(100, HEIGHT - 100),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-5, -2),
                'life': random.randint(20, 40),
                'size': random.randint(10, 25)
            })
        
        # 更新火焰
        new_flames = []
        for flame in self.flames:
            flame['x'] += flame['vx']
            flame['y'] += flame['vy']
            flame['life'] -= 1
            flame['size'] = max(1, flame['size'] - 0.3)
            if flame['life'] > 0:
                new_flames.append(flame)
        self.flames = new_flames
        
        # 更新爆炸
        new_explosions = []
        for exp in self.explosions:
            exp['radius'] += exp['speed']
            exp['alpha'] = max(0, exp['alpha'] - 5)
            if exp['alpha'] > 0:
                new_explosions.append(exp)
        self.explosions = new_explosions
        
        # 持续伤害
        if self.phase >= 1 and self.lifetime % 10 == 0:
            self._deal_damage()
        
        self._render()
    
    def _trigger_explosion(self):
        """触发大爆炸"""
        # 生成多个爆炸环
        for i in range(5):
            self.explosions.append({
                'x': self.x + random.randint(-50, 50),
                'y': self.y + random.randint(-50, 50),
                'radius': 10,
                'speed': 8 + i * 2,
                'alpha': 255,
                'color': [self.primary, self.secondary, self.tertiary][i % 3]
            })
        
        # 生成烟火
        for _ in range(24):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(6, 12)
            NoteBullet(self.x, self.y, 
                      angle=math.degrees(angle) - 90,
                      speed=speed,
                      damage=self.base_damage * 0.5,
                      note_type=random.randint(0, 3),
                      on_beat=True)
    
    def _deal_damage(self):
        """造成范围伤害"""
        damage_mult = 1.5 if self.phase == 1 else 0.5
        for enemy in mobs:
            if hasattr(enemy, 'hp'):
                enemy.hp -= self.base_damage * damage_mult
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        
        progress = self.lifetime / self.duration
        
        # 阶段0：聚能效果
        if self.phase == 0:
            charge_progress = self.lifetime / self.phase_timers[0]
            
            # 向中心收缩的能量线
            for i in range(16):
                angle = i * math.pi / 8 + self.lifetime * 0.1
                start_dist = 300 * (1 - charge_progress)
                end_dist = 50
                
                sx = int(self.x + math.cos(angle) * start_dist)
                sy = int(self.y + math.sin(angle) * start_dist)
                ex = int(self.x + math.cos(angle) * end_dist)
                ey = int(self.y + math.sin(angle) * end_dist)
                
                line_alpha = int(200 * charge_progress)
                pygame.draw.line(self.image, (*self.primary, line_alpha),
                               (sx, sy), (ex, ey), 3)
            
            # 中心蓄力球
            core_size = int(30 * charge_progress)
            pygame.draw.circle(self.image, (*self.secondary, int(200 * charge_progress)),
                             (int(self.x), int(self.y)), core_size)
        
        # 绘制爆炸环
        for exp in self.explosions:
            pygame.draw.circle(self.image, (*exp['color'], exp['alpha']),
                             (int(exp['x']), int(exp['y'])), int(exp['radius']), 8)
        
        # 绘制火焰粒子
        for flame in self.flames:
            flame_alpha = int(255 * (flame['life'] / 40))
            # 火焰渐变色
            r = min(255, 255)
            g = min(255, int(100 + flame['life'] * 3))
            b = 0
            pygame.draw.circle(self.image, (r, g, b, flame_alpha),
                             (int(flame['x']), int(flame['y'])), int(flame['size']))
        
        # 阶段1和2：屏幕震动和闪光
        if self.phase >= 1:
            if self.lifetime % 4 < 2:
                flash_alpha = int(100 * (1 - progress))
                pygame.draw.rect(self.image, (*self.primary, flash_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 边缘效果
        edge_alpha = int(80 * (1 - progress))
        pygame.draw.rect(self.image, (*self.tertiary, edge_alpha), (0, 0, WIDTH, HEIGHT), 10)
