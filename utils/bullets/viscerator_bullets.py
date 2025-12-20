# -*- coding: utf-8 -*-
"""
光之在解·VISCERATOR 弹幕系统
追踪光流 + 高性能优化版

核心优化：
- 预缓存子弹图像，不每帧重绘
- 追踪计算简化，每5帧更新一次方向
- 使用简单的速度向量而非复杂的段系统
"""
import pygame
import math
import random
from config import WIDTH, HEIGHT, all_sprites, bullets, mobs, enemy_bullets

# ==================== 预缓存子弹图像 ====================
_bullet_cache = {}

def _get_bullet_image(color, size=10):
    """获取缓存的子弹图像"""
    cache_key = (color, size)
    if cache_key not in _bullet_cache:
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (size//2, size//2), size//2 - 1)
        pygame.draw.circle(surf, (255, 255, 255), (size//2, size//2), size//4)
        _bullet_cache[cache_key] = surf
    return _bullet_cache[cache_key]


# ==================== 主武器：追踪光弹 ====================
class ExoStreamBullet(pygame.sprite.Sprite):
    """
    追踪光弹 - 高性能版
    - 每5帧更新追踪方向
    - 使用预缓存图像
    """
    
    def __init__(self, x, y, damage, owner=None, style="viscerator_default", side="left"):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.is_enemy = False
        self.side = side
        
        self.x = float(x)
        self.y = float(y)
        self.vx = 0
        self.vy = -12
        
        self.target = None
        self.frame = 0
        self.pierce = 2
        self.hit_set = set()
        
        # 使用预缓存图像
        color = (255, 20, 147) if side == "left" else (127, 255, 0)
        self.image = _get_bullet_image(color, 12)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        self.frame += 1
        
        # 每5帧更新追踪方向
        if self.frame % 5 == 0:
            self._update_tracking()
        
        # 移动
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))
        
        # 碰撞检测
        for m in mobs:
            if m.alive() and id(m) not in self.hit_set and self.rect.colliderect(m.rect):
                m.take_damage(self.damage)
                self.hit_set.add(id(m))
                # 添加火花 - 使用owner的spark_manager
                if self.owner and hasattr(self.owner, 'viscerator_spark_manager'):
                    self.owner.viscerator_spark_manager.add_spark(m)
                self.pierce -= 1
                if self.pierce <= 0:
                    self.kill()
                    return
        
        # 边界检测
        if self.y < -20 or self.y > HEIGHT + 20 or self.x < -20 or self.x > WIDTH + 20:
            self.kill()
    
    def _update_tracking(self):
        """更新追踪方向"""
        # 找最近敌人
        best = None
        min_dist = 250000  # 500^2
        for m in mobs:
            if m.alive():
                dx = m.rect.centerx - self.x
                dy = m.rect.centery - self.y
                d = dx*dx + dy*dy
                if d < min_dist:
                    min_dist = d
                    best = m
        
        if best:
            dx = best.rect.centerx - self.x
            dy = best.rect.centery - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                # 追踪强度
                self.vx += dx / dist * 1.5
                self.vy += dy / dist * 1.5
        
        # 限速
        speed = math.sqrt(self.vx*self.vx + self.vy*self.vy)
        max_speed = 14
        if speed > max_speed:
            self.vx = self.vx / speed * max_speed
            self.vy = self.vy / speed * max_speed


class SparkStickManager:
    """
    光子粘滞管理器 - 被动系统
    攻击在敌人身上留下"光子火花"，积累到一定程度爆炸
    """
    
    def __init__(self):
        self.sparks = {}  # enemy_id -> spark_count
        self.spark_threshold = 8  # 爆炸阈值
    
    def add_spark(self, enemy):
        """在敌人身上添加光子火花"""
        if not enemy or not enemy.alive():
            return 0
        
        eid = id(enemy)
        self.sparks[eid] = self.sparks.get(eid, 0) + 1
        
        # 检查是否达到爆炸阈值
        if self.sparks[eid] >= self.spark_threshold:
            self._trigger_explosion(enemy)
            self.sparks[eid] = 0
            return self.spark_threshold
        
        return self.sparks[eid]
    
    def _trigger_explosion(self, enemy):
        """触发光子爆炸"""
        if enemy and enemy.alive():
            # 造成额外爆炸伤害
            enemy.take_damage(50)
            # 创建爆炸效果
            SparkExplosion(enemy.rect.centerx, enemy.rect.centery)
    
    def get_sparks(self, enemy):
        """获取敌人身上的火花数量"""
        if not enemy:
            return 0
        return self.sparks.get(id(enemy), 0)
    
    def cleanup(self):
        """清理无效敌人"""
        # 简单清理，不每帧执行
        pass


class SparkExplosion(pygame.sprite.Sprite):
    """火花爆炸效果"""
    
    def __init__(self, x, y):
        super().__init__()
        self.frame = 0
        self.x, self.y = x, y
        
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        radius = self.frame * 4
        alpha = max(0, 200 - self.frame * 20)
        
        self.image.fill((0, 0, 0, 0))
        if alpha > 0:
            pygame.draw.circle(self.image, (255, 20, 147, alpha), (30, 30), min(radius, 28))
            pygame.draw.circle(self.image, (127, 255, 0, alpha), (30, 30), min(radius, 28), 2)
        
        if self.frame > 10:
            self.kill()


# 全局火花管理器
_spark_manager = None

def get_spark_manager():
    global _spark_manager
    if _spark_manager is None:
        _spark_manager = SparkStickManager()
    return _spark_manager


# ==================== 技能1：推进器反转 ====================
# 预缓存锥形图像
_thrust_cache = {}

def _get_thrust_cone(radius, alpha):
    """获取预渲染的锥形图像"""
    key = (radius, alpha)
    if key not in _thrust_cache:
        size = radius * 2 + 40
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2 - 20
        
        # 外层粉色
        points = [(cx, cy)]
        for ang in range(-50, 51, 10):
            rad = math.radians(ang + 90)
            points.append((int(cx + math.cos(rad) * radius), int(cy + math.sin(rad) * radius)))
        if len(points) > 2:
            pygame.draw.polygon(surf, (255, 20, 147, alpha), points)
        
        # 内层白色
        inner_r = radius * 0.6
        points2 = [(cx, cy)]
        for ang in range(-40, 41, 10):
            rad = math.radians(ang + 90)
            points2.append((int(cx + math.cos(rad) * inner_r), int(cy + math.sin(rad) * inner_r)))
        if len(points2) > 2:
            pygame.draw.polygon(surf, (255, 255, 255, alpha), points2)
        
        # 核心绿光
        pygame.draw.circle(surf, (127, 255, 0, alpha), (cx, cy), 15)
        pygame.draw.circle(surf, (255, 255, 255, min(255, alpha + 50)), (cx, cy), 8)
        
        _thrust_cache[key] = surf
    return _thrust_cache[key]


class ReverseThrustBlast(pygame.sprite.Sprite):
    """推进器反转 - 高性能版（预渲染 + 简化粒子）"""
    
    def __init__(self, x, y, damage, owner=None, style="viscerator_default"):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.is_enemy = False
        
        self.cx = x
        self.cy = y
        self.frame = 0
        self.hit_set = set()
        
        # 预计算扩展半径序列
        self.radii = [min(150, 10 + i * 12) for i in range(26)]
        self.alphas = [max(0, 220 - i * 9) for i in range(26)]
        
        self.image = pygame.Surface((340, 340), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        bullets.add(self)
        enemy_bullets.empty()
    
    def update(self):
        self.frame += 1
        self.cy += 6
        self.rect.center = (int(self.cx), int(self.cy))
        
        # 伤害检测
        radius = self.radii[min(self.frame, 25)]
        for m in mobs:
            if m.alive() and id(m) not in self.hit_set:
                dx = m.rect.centerx - self.cx
                dy = m.rect.centery - self.cy
                if dx*dx + dy*dy < radius*radius:
                    m.take_damage(self.damage)
                    self.hit_set.add(id(m))
        
        # 绘制（使用预渲染）
        self.image.fill((0, 0, 0, 0))
        if self.frame <= 25:
            alpha = self.alphas[self.frame]
            if alpha > 0:
                cone = _get_thrust_cone(radius, alpha)
                self.image.blit(cone, (170 - cone.get_width()//2, 170 - cone.get_height()//2))
                
                # 简单冲击波环
                if self.frame % 4 == 0:
                    wave_r = self.frame * 6
                    pygame.draw.circle(self.image, (127, 255, 0, alpha // 2), (170, 150), wave_r, 3)
        
        if self.frame > 25:
            self.kill()


# ==================== 技能2：粒子风暴（增强版）====================
# 预计算多波次粒子方向（24个方向，3波）
_storm_dirs_24 = [(math.cos(math.radians(i * 15)), math.sin(math.radians(i * 15))) for i in range(24)]
_storm_dirs_12 = [(math.cos(math.radians(i * 30 + 15)), math.sin(math.radians(i * 30 + 15))) for i in range(12)]

# 预缓存华丽粒子图像
_storm_bullet_cache = {}

def _get_storm_bullet(color, size):
    """获取华丽粒子图像（带光晕）"""
    key = (color, size)
    if key not in _storm_bullet_cache:
        surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
        cx, cy = size * 3 // 2, size * 3 // 2
        # 外层光晕
        pygame.draw.circle(surf, (*color, 40), (cx, cy), size + 8)
        pygame.draw.circle(surf, (*color, 80), (cx, cy), size + 4)
        # 主体
        pygame.draw.circle(surf, color, (cx, cy), size)
        # 白色核心
        pygame.draw.circle(surf, (255, 255, 255), (cx, cy), size // 2)
        # 高光点
        pygame.draw.circle(surf, (255, 255, 255, 200), (cx - size//3, cy - size//3), size // 4)
        _storm_bullet_cache[key] = surf
    return _storm_bullet_cache[key]


class ParticleStormBullet(pygame.sprite.Sprite):
    """粒子风暴弹 - 带华丽拖尾"""
    
    def __init__(self, x, y, damage, dx, dy, color, speed, owner=None):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.is_enemy = False
        
        self.x = float(x)
        self.y = float(y)
        self.vx = dx * speed
        self.vy = dy * speed
        self.color = color
        self.frame = 0
        self.speed = speed
        
        # 拖尾历史
        self.trail = []
        
        # 使用华丽图像
        self.base_image = _get_storm_bullet(color, 8)
        self.image = self.base_image
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        self.frame += 1
        
        # 记录拖尾
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 6:
            self.trail.pop(0)
        
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))
        
        # 碰撞检测
        for m in mobs:
            if m.alive() and self.rect.colliderect(m.rect):
                m.take_damage(self.damage)
                # 命中爆炸效果
                ParticleHitEffect(self.x, self.y, self.color)
                self.kill()
                return
        
        # 超出边界
        if self.x < -30 or self.x > WIDTH + 30 or self.y < -30 or self.y > HEIGHT + 30:
            self.kill()


class ParticleHitEffect(pygame.sprite.Sprite):
    """粒子命中小爆炸"""
    
    def __init__(self, x, y, color):
        super().__init__()
        self.x = x
        self.y = y
        self.color = color
        self.frame = 0
        
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        self.image.fill((0, 0, 0, 0))
        
        if self.frame <= 8:
            r = self.frame * 6
            a = max(0, 255 - self.frame * 30)
            pygame.draw.circle(self.image, (*self.color, a), (30, 30), r, 3)
            pygame.draw.circle(self.image, (255, 255, 255, a), (30, 30), max(1, r - 10), 2)
        else:
            self.kill()


class ParticleStormCore(pygame.sprite.Sprite):
    """粒子风暴中心特效"""
    
    def __init__(self, x, y, owner=None):
        super().__init__()
        self.cx = x
        self.cy = y
        self.owner = owner
        self.frame = 0
        
        self.image = pygame.Surface((200, 200), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        self.image.fill((0, 0, 0, 0))
        
        if self.frame <= 30:
            prog = self.frame / 30
            
            # 扩散光环
            for i in range(3):
                r = int(20 + self.frame * 3 + i * 15)
                a = max(0, 200 - self.frame * 6 - i * 40)
                color = (255, 20, 147) if i % 2 == 0 else (127, 255, 0)
                pygame.draw.circle(self.image, (*color, a), (100, 100), r, 3)
            
            # 中心旋转能量
            if self.frame < 20:
                core_a = max(0, 255 - self.frame * 10)
                pygame.draw.circle(self.image, (255, 255, 255, core_a), (100, 100), 25 - self.frame)
                pygame.draw.circle(self.image, (255, 20, 147, core_a), (100, 100), 35 - self.frame, 3)
                pygame.draw.circle(self.image, (127, 255, 0, core_a), (100, 100), 45 - self.frame, 2)
        else:
            self.kill()


def fire_particle_storm(x, y, damage, owner=None, style="viscerator_default"):
    """发射粒子风暴 - 3波华丽扩散"""
    colors = [(255, 20, 147), (127, 255, 0)]
    
    # 中心特效
    ParticleStormCore(x, y, owner)
    
    # 第1波：24方向快速弹
    for i, (dx, dy) in enumerate(_storm_dirs_24):
        color = colors[i % 2]
        ParticleStormBullet(x, y, damage * 0.6, dx, dy, color, 16, owner)
    
    # 第2波：12方向中速弹（延迟效果通过初始位置偏移实现）
    for i, (dx, dy) in enumerate(_storm_dirs_12):
        color = colors[(i + 1) % 2]
        ParticleStormBullet(x + dx * 20, y + dy * 20, damage * 0.8, dx, dy, color, 12, owner)
    
    # 第3波：24方向慢速大弹
    for i, (dx, dy) in enumerate(_storm_dirs_24):
        color = colors[(i + 1) % 2]
        # 稍微偏移起点
        ParticleStormBullet(x + dx * 40, y + dy * 40, damage, dx, dy, color, 8, owner)


# ==================== 技能3：星流过载 ====================
# 预缓存棱镜图像
_prism_cache = {}

def _get_prism_image(color, rotation):
    """获取预渲染的棱镜图像"""
    # 只缓存8个旋转角度
    rot_key = (rotation // 15) * 15
    key = (color, rot_key)
    if key not in _prism_cache:
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        cx, cy = 25, 25
        
        # 光晕
        pygame.draw.circle(surf, (*color, 60), (cx, cy), 20)
        
        # 旋转三角
        points = []
        for i in range(3):
            angle = math.radians(rot_key + i * 120)
            points.append((int(cx + math.cos(angle) * 14), int(cy + math.sin(angle) * 14)))
        pygame.draw.polygon(surf, color, points)
        pygame.draw.polygon(surf, (255, 255, 255), points, 2)
        
        # 核心
        pygame.draw.circle(surf, (255, 255, 255), (cx, cy), 5)
        pygame.draw.circle(surf, (*color, 150), (cx, cy), 18, 2)
        
        _prism_cache[key] = surf
    return _prism_cache[key]


class ExoPrism(pygame.sprite.Sprite):
    """EXO棱镜 - 高性能版（预渲染棱镜）"""
    
    def __init__(self, owner, damage, style, angle_offset):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.angle = float(angle_offset)
        self.orbit_radius = 70
        self.frame = 0
        self.fire_cooldown = 0
        
        self.prism_color = (255, 20, 147) if angle_offset % 180 == 0 else (127, 255, 0)
        
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        self.angle += 2.5
        
        if not self.owner or not self.owner.alive():
            self.kill()
            return
        
        # 环绕位置（预计算sin/cos避免重复）
        rad = self.angle * 0.0174533  # math.radians
        self.rect.centerx = int(self.owner.rect.centerx + math.cos(rad) * self.orbit_radius)
        self.rect.centery = int(self.owner.rect.centery + math.sin(rad) * self.orbit_radius)
        
        # 发射激光
        self.fire_cooldown -= 1
        if self.fire_cooldown <= 0:
            self._fire_laser()
            self.fire_cooldown = 20
        
        # 使用预渲染图像
        self.image = _get_prism_image(self.prism_color, int(self.frame * 3))
        
        if self.frame > 180:
            self.kill()
    
    def _fire_laser(self):
        """发射追踪激光"""
        best = None
        min_dist = 999999
        for m in mobs:
            if m.alive():
                dx = m.rect.centerx - self.rect.centerx
                dy = m.rect.centery - self.rect.centery
                d = dx*dx + dy*dy
                if d < min_dist:
                    min_dist = d
                    best = m
        
        if best:
            PrismLaser(self.rect.centerx, self.rect.centery, best, self.damage, self.prism_color)


class PrismLaser(pygame.sprite.Sprite):
    """棱镜激光 - 高性能版（无尾迹，简化绘制）"""
    
    def __init__(self, x, y, target, damage, color):
        super().__init__()
        self.damage = damage
        self.target = target
        self.x = float(x)
        self.y = float(y)
        self.frame = 0
        self.is_enemy = False
        self.color = color
        
        # 预渲染激光图像
        self.image = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255), (9, 9), 6)
        pygame.draw.circle(self.image, color, (9, 9), 8, 2)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        self.frame += 1
        
        if self.target and self.target.alive():
            dx = self.target.rect.centerx - self.x
            dy = self.target.rect.centery - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                self.x += dx / dist * 20
                self.y += dy / dist * 20
                self.rect.center = (int(self.x), int(self.y))
                
                if dist < 25:
                    self.target.take_damage(self.damage)
                    self.kill()
                    return
        
        if self.frame > 40 or self.y < -20 or self.y > HEIGHT + 20:
            self.kill()


# ==================== 技能4：光子湮灭（增强版）====================
# 预缓存激光弹图像
_laser_cache = {}

def _get_laser_image(color, length=40):
    """获取华丽激光弹图像"""
    key = (color, length)
    if key not in _laser_cache:
        surf = pygame.Surface((20, length), pygame.SRCALPHA)
        # 外发光
        pygame.draw.rect(surf, (*color, 60), (2, 0, 16, length))
        # 主体
        pygame.draw.rect(surf, color, (5, 0, 10, length))
        # 核心
        pygame.draw.rect(surf, (255, 255, 255), (7, 0, 6, length))
        # 头部高光
        pygame.draw.circle(surf, (255, 255, 255), (10, 5), 6)
        pygame.draw.circle(surf, color, (10, 5), 8, 2)
        _laser_cache[key] = surf
    return _laser_cache[key]


class CrossLaserBullet(pygame.sprite.Sprite):
    """交叉激光弹 - 华丽版带拖尾"""
    
    def __init__(self, start_x, damage, is_left, delay, owner=None):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.is_enemy = False
        self.is_left = is_left
        self.delay = delay
        
        # 从屏幕顶部射入
        self.x = float(start_x)
        self.y = float(-20 - delay * 8)
        self.vx = 10 if is_left else -10
        self.vy = 14
        
        self.color = (255, 20, 147) if is_left else (127, 255, 0)
        self.frame = 0
        
        # 拖尾历史
        self.trail = []
        
        # 使用华丽激光图像
        self.base_image = _get_laser_image(self.color, 35)
        # 旋转图像
        angle = -35 if is_left else 35
        self.image = pygame.transform.rotate(self.base_image, angle)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        self.frame += 1
        
        # 记录拖尾
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 12:
            self.trail.pop(0)
        
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))
        
        # 碰撞检测
        for m in mobs:
            if m.alive() and self.rect.colliderect(m.rect):
                m.take_damage(self.damage)
                # 命中特效
                LaserHitSpark(self.x, self.y, self.color)
                self.kill()
                return
        
        # 超出边界
        if self.y > HEIGHT + 50:
            self.kill()


class LaserHitSpark(pygame.sprite.Sprite):
    """激光命中火花"""
    
    def __init__(self, x, y, color):
        super().__init__()
        self.x = x
        self.y = y
        self.color = color
        self.frame = 0
        
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        self.image.fill((0, 0, 0, 0))
        
        if self.frame <= 10:
            # 十字闪光
            a = max(0, 255 - self.frame * 25)
            length = self.frame * 4
            pygame.draw.line(self.image, (*self.color, a), (25 - length, 25), (25 + length, 25), 3)
            pygame.draw.line(self.image, (*self.color, a), (25, 25 - length), (25, 25 + length), 3)
            pygame.draw.circle(self.image, (255, 255, 255, a), (25, 25), max(1, 8 - self.frame))
        else:
            self.kill()


class PhotonAnnihilationEffect(pygame.sprite.Sprite):
    """光子湮灭主爆炸 - 超华丽版"""
    
    def __init__(self, x, y, damage, owner=None):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.is_enemy = False
        
        self.cx = x
        self.cy = y
        self.frame = 0
        self.hit_set = set()
        
        # 预计算
        self.radii = [int(i * 20) for i in range(40)]
        
        self.image = pygame.Surface((600, 600), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        self.frame += 1
        
        # 伤害检测（扩大范围）
        if self.frame <= 20:
            radius = self.radii[min(self.frame, 39)]
            radius_sq = radius * radius
            for m in mobs:
                if m.alive() and id(m) not in self.hit_set:
                    dx = m.rect.centerx - self.cx
                    dy = m.rect.centery - self.cy
                    if dx*dx + dy*dy < radius_sq:
                        m.take_damage(self.damage)
                        self.hit_set.add(id(m))
        
        self.image.fill((0, 0, 0, 0))
        
        if self.frame <= 35:
            self._draw_explosion()
        else:
            self.kill()
    
    def _draw_explosion(self):
        """绘制华丽爆炸"""
        cx, cy = 300, 300
        
        # 阶段1：中心闪光（1-8帧）
        if self.frame <= 8:
            flash_a = min(255, self.frame * 40)
            core_r = 80 - self.frame * 5
            pygame.draw.circle(self.image, (255, 255, 255, flash_a), (cx, cy), max(1, core_r))
            pygame.draw.circle(self.image, (255, 20, 147, flash_a), (cx, cy), max(1, core_r + 20))
            pygame.draw.circle(self.image, (127, 255, 0, flash_a // 2), (cx, cy), max(1, core_r + 40))
        
        # 阶段2：双色冲击波扩散（5-30帧）
        if self.frame > 4:
            wave_frame = self.frame - 4
            
            # 多层冲击波
            for i in range(4):
                delay = i * 4
                if wave_frame > delay:
                    r = (wave_frame - delay) * 18
                    a = max(0, 220 - (wave_frame - delay) * 8 - i * 30)
                    
                    if a > 0 and r < 280:
                        color = (255, 20, 147) if i % 2 == 0 else (127, 255, 0)
                        thickness = max(2, 8 - i * 2)
                        pygame.draw.circle(self.image, (*color, a), (cx, cy), r, thickness)
            
            # 白色核心波
            if wave_frame < 20:
                core_r = wave_frame * 12
                core_a = max(0, 255 - wave_frame * 12)
                pygame.draw.circle(self.image, (255, 255, 255, core_a), (cx, cy), core_r, 4)
        
        # 阶段3：能量射线（8-25帧）
        if 8 < self.frame <= 25:
            ray_frame = self.frame - 8
            num_rays = 8
            ray_length = min(250, ray_frame * 20)
            ray_a = max(0, 200 - ray_frame * 10)
            
            for i in range(num_rays):
                angle = math.radians(i * 45 + ray_frame * 3)
                ex = int(cx + math.cos(angle) * ray_length)
                ey = int(cy + math.sin(angle) * ray_length)
                color = (255, 20, 147) if i % 2 == 0 else (127, 255, 0)
                pygame.draw.line(self.image, (*color, ray_a), (cx, cy), (ex, ey), 4)
                # 射线端点光球
                pygame.draw.circle(self.image, (255, 255, 255, ray_a), (ex, ey), 8)


class AnnihilationChargeEffect(pygame.sprite.Sprite):
    """湮灭蓄力特效 - 显示在释放瞬间"""
    
    def __init__(self, x, y, owner=None):
        super().__init__()
        self.cx = x
        self.cy = y
        self.owner = owner
        self.frame = 0
        
        self.image = pygame.Surface((300, 300), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        self.image.fill((0, 0, 0, 0))
        
        if self.frame <= 20:
            # 能量汇聚效果
            prog = self.frame / 20
            
            # 收缩光环
            for i in range(3):
                r = int(120 * (1 - prog) + i * 20)
                a = int(180 * prog)
                color = (255, 20, 147) if i % 2 == 0 else (127, 255, 0)
                pygame.draw.circle(self.image, (*color, a), (150, 150), max(1, r), 3)
            
            # 汇聚粒子线
            for i in range(6):
                angle = math.radians(i * 60 + self.frame * 8)
                start_r = 100 * (1 - prog)
                sx = int(150 + math.cos(angle) * start_r)
                sy = int(150 + math.sin(angle) * start_r)
                color = (255, 20, 147) if i % 2 == 0 else (127, 255, 0)
                pygame.draw.line(self.image, (*color, 200), (sx, sy), (150, 150), 2)
                pygame.draw.circle(self.image, (255, 255, 255), (sx, sy), 5)
            
            # 中心能量球
            core_r = int(10 + prog * 30)
            pygame.draw.circle(self.image, (255, 255, 255, 200), (150, 150), core_r)
            pygame.draw.circle(self.image, (255, 20, 147, 150), (150, 150), core_r + 10, 3)
            pygame.draw.circle(self.image, (127, 255, 0, 100), (150, 150), core_r + 20, 2)
        else:
            self.kill()


def fire_photon_annihilation(owner, damage, style="viscerator_default"):
    """光子湮灭 - 华丽交叉激光雨"""
    cx = owner.rect.centerx if owner else WIDTH // 2
    cy = owner.rect.centery if owner else HEIGHT // 2
    
    # 蓄力特效
    AnnihilationChargeEffect(cx, cy, owner)
    
    # 发射大量交叉激光（左右各8道，分批次）
    for wave in range(3):
        for i in range(8):
            delay = wave * 8 + i
            offset = i * 50 + wave * 20
            
            # 左侧粉色激光
            CrossLaserBullet(cx - 100 - offset, damage * 0.35, True, delay, owner)
            # 右侧绿色激光
            CrossLaserBullet(cx + 100 + offset, damage * 0.35, False, delay, owner)
    
    # 中心主爆炸
    PhotonAnnihilationEffect(cx, HEIGHT // 2 + 50, damage * 1.5, owner)


# ==================== 发射函数 ====================
def fire_exo_stream(x, y, damage, owner=None, style="viscerator_default"):
    """发射双追踪光弹"""
    ExoStreamBullet(x - 18, y - 20, damage, owner, style, "left")
    ExoStreamBullet(x + 18, y - 20, damage, owner, style, "right")


def fire_reverse_thrust(x, y, damage, owner=None, style="viscerator_default"):
    """推进器反转"""
    ReverseThrustBlast(x, y + 30, damage, owner, style)


def fire_focus_beam(x, y, damage, owner=None, style="viscerator_default"):
    """粒子风暴（原归束轰击）"""
    fire_particle_storm(x, y, damage, owner, style)


def fire_light_of_destruction(owner, damage, style="viscerator_default"):
    """光子湮灭（原毁灭之光）"""
    fire_photon_annihilation(owner, damage, style)


def create_exo_overload(owner, damage, style="viscerator_default"):
    """星流过载 - 召唤环绕棱镜"""
    for i in range(4):
        ExoPrism(owner, damage, style, i * 90)
