"""
狱炎神龙·犽戎 (Yharon) 弹幕系统
原型：Terraria Calamity Mod - Yharon, Dragon of Rebirth
核心机制：日耀喷流 + 神龙冲拳 + 炼狱边界浮游炮
"""

import pygame
import math
import random
from config import WIDTH, HEIGHT, all_sprites, bullets, mobs, enemy_bullets

# ==================== 导入涂装主题 ====================
try:
    from utils.planes.skins_yharon import get_yharon_theme, YHARON_THEMES
except ImportError:
    YHARON_THEMES = {
        "default": {
            "name": "丛林龙王",
            "armor": (0, 100, 50),
            "flame": (255, 69, 0),
            "core": (255, 0, 0),
            "gold": (255, 215, 0),
            "trail": (255, 140, 0),
            "border": (255, 100, 50),
        }
    }
    def get_yharon_theme(style):
        return YHARON_THEMES.get(style, YHARON_THEMES["default"])


def get_theme(style):
    """获取涂装主题"""
    return get_yharon_theme(style)


# ==================== 主武器：日耀喷流 ====================
class FlareStreamBullet(pygame.sprite.Sprite):
    """
    日耀喷流 - 主武器
    高流速火焰束，命中后溅射余烬火花追踪其他敌人
    """
    
    def __init__(self, x, y, damage, angle=0, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.angle = angle
        self.speed = 18
        
        self.vx = math.cos(math.radians(angle)) * self.speed
        self.vy = math.sin(math.radians(angle)) * self.speed
        
        self.frame = 0
        self.lifetime = 90  # 1.5秒
        self.max_range = HEIGHT * 1.2
        self.traveled = 0
        
        # 火焰拖尾
        self.trail = []
        self.max_trail = 8
        
        self.size = 40
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        self.frame += 1
        
        # 移动
        self.float_x += self.vx
        self.float_y += self.vy
        self.traveled += self.speed
        
        # 添加拖尾
        if self.frame % 2 == 0:
            self.trail.append({'x': self.float_x, 'y': self.float_y, 'alpha': 255})
            if len(self.trail) > self.max_trail:
                self.trail.pop(0)
        
        # 更新拖尾透明度
        for t in self.trail:
            t['alpha'] = max(0, t['alpha'] - 30)
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 出界或超距
        if (self.float_x < -50 or self.float_x > WIDTH + 50 or
            self.float_y < -50 or self.float_y > HEIGHT + 50 or
            self.traveled > self.max_range or self.frame > self.lifetime):
            self.kill()
            return
        
        # 碰撞检测
        self._check_collision()
        self._render()
    
    def _check_collision(self):
        """碰撞检测"""
        for mob in mobs:
            if self.rect.colliderect(mob.rect):
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage)
                # 溅射余烬火花
                self._spawn_embers(mob.rect.centerx, mob.rect.centery)
                self.kill()
                return
    
    def _spawn_embers(self, x, y):
        """生成余烬火花追踪"""
        num_embers = random.randint(3, 5)
        for i in range(num_embers):
            angle = random.uniform(0, 360)
            ember = EmberSpark(x, y, self.damage * 0.3, angle, self.owner, self.style)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.2
        
        flame_col = self.theme["flame"]
        core_col = self.theme["core"]
        gold_col = self.theme["gold"]
        
        # 绘制拖尾
        for i, tr in enumerate(self.trail):
            if tr['alpha'] > 0:
                tx = int(tr['x'] - self.float_x + cx)
                ty = int(tr['y'] - self.float_y + cy)
                r = 6 - i * 0.5
                if 0 < tx < self.size and 0 < ty < self.size and r > 0:
                    pygame.draw.circle(self.image, (*flame_col, tr['alpha']), (tx, ty), int(r))
        
        # 火焰核心
        pulse = 1 + 0.3 * math.sin(t * 3)
        core_r = int(8 * pulse)
        pygame.draw.circle(self.image, core_col, (cx, cy), core_r)
        pygame.draw.circle(self.image, gold_col, (cx, cy), core_r - 3)
        
        # 外层火焰
        for i in range(3):
            angle = t * 5 + i * 2.1
            fx = cx + int(math.cos(angle) * 5)
            fy = cy + int(math.sin(angle) * 5)
            pygame.draw.circle(self.image, flame_col, (fx, fy), 4)


# ==================== 余烬火花（追踪弹） ====================
class EmberSpark(pygame.sprite.Sprite):
    """余烬火花 - 溅射后追踪最近敌人"""
    
    def __init__(self, x, y, damage, angle, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.angle = angle
        self.speed = 6
        self.homing = 0.12
        
        self.vx = math.cos(math.radians(angle)) * self.speed
        self.vy = math.sin(math.radians(angle)) * self.speed
        
        self.frame = 0
        self.lifetime = 90
        self.target = None
        
        self.size = 20
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        self.frame += 1
        
        # 寻找目标
        if self.target is None or not self.target.alive():
            self._find_target()
        
        # 追踪
        if self.target and self.target.alive():
            dx = self.target.rect.centerx - self.float_x
            dy = self.target.rect.centery - self.float_y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.vx += (dx / dist) * self.homing * self.speed
                self.vy += (dy / dist) * self.homing * self.speed
                # 限制速度
                spd = math.hypot(self.vx, self.vy)
                if spd > self.speed * 1.5:
                    self.vx = self.vx / spd * self.speed * 1.5
                    self.vy = self.vy / spd * self.speed * 1.5
        
        self.float_x += self.vx
        self.float_y += self.vy
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 超时或出界
        if self.frame > self.lifetime or self.float_x < -30 or self.float_x > WIDTH + 30:
            self.kill()
            return
        
        # 碰撞
        for mob in mobs:
            if self.rect.colliderect(mob.rect):
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage)
                self.kill()
                return
        
        self._render()
    
    def _find_target(self):
        """寻找最近敌人"""
        min_dist = float('inf')
        for mob in mobs:
            dist = math.hypot(mob.rect.centerx - self.float_x,
                            mob.rect.centery - self.float_y)
            if dist < min_dist:
                min_dist = dist
                self.target = mob
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.3
        
        flame_col = self.theme["flame"]
        core_col = self.theme["core"]
        
        # 闪烁的火花
        pulse = 0.7 + 0.3 * math.sin(t * 5)
        r = int(5 * pulse)
        pygame.draw.circle(self.image, flame_col, (cx, cy), r + 2)
        pygame.draw.circle(self.image, core_col, (cx, cy), r)


# ==================== 炼狱边界浮游炮 ====================
class BorderDrone(pygame.sprite.Sprite):
    """
    炼狱边界 - 浮游炮
    防御模式：扩大旋转消弹+灼烧
    攻击模式：收缩辅助射击
    """
    
    def __init__(self, owner, side, style="default"):
        super().__init__()
        self.owner = owner
        self.side = side  # "left" or "right"
        self.style = style
        self.theme = get_theme(style)
        
        self.orbit_angle = 0 if side == "left" else math.pi
        self.orbit_radius_defense = 100
        self.orbit_radius_attack = 40
        self.orbit_radius = self.orbit_radius_defense
        self.orbit_speed = 0.03
        
        self.mode = "defense"  # defense / attack
        self.frame = 0
        
        self.size = 30
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        all_sprites.add(self)
    
    def update(self):
        if not self.owner or not self.owner.alive():
            self.kill()
            return
        
        self.frame += 1
        
        # 检测模式
        is_firing = getattr(self.owner, 'is_firing', False)
        target_radius = self.orbit_radius_attack if is_firing else self.orbit_radius_defense
        self.orbit_radius += (target_radius - self.orbit_radius) * 0.1
        self.mode = "attack" if is_firing else "defense"
        
        # 更新轨道
        self.orbit_angle += self.orbit_speed
        ox = self.owner.rect.centerx + math.cos(self.orbit_angle) * self.orbit_radius
        oy = self.owner.rect.centery + math.sin(self.orbit_angle) * self.orbit_radius
        self.rect.center = (int(ox), int(oy))
        
        # 防御模式：消弹+灼烧
        if self.mode == "defense" and self.frame % 3 == 0:
            self._defense_effect()
        
        self._render()
    
    def _defense_effect(self):
        """防御效果：消弹+灼烧"""
        cx, cy = self.rect.center
        effect_radius = 60
        
        # 消弹
        for bullet in enemy_bullets:
            dist = math.hypot(bullet.rect.centerx - cx, bullet.rect.centery - cy)
            if dist < effect_radius:
                bullet.kill()
        
        # 灼烧敌人
        for mob in mobs:
            dist = math.hypot(mob.rect.centerx - cx, mob.rect.centery - cy)
            if dist < effect_radius:
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.owner.damage * 0.05)
    
    def fire_assist(self):
        """攻击模式：辅助射击"""
        if self.mode == "attack":
            bullet = BorderBullet(self.rect.centerx, self.rect.centery,
                                 self.owner.damage * 0.4, self.owner, self.style)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.1
        
        gold_col = self.theme["gold"]
        flame_col = self.theme["flame"]
        
        # 菱形外框
        points = [
            (cx, cy - 10),
            (cx + 8, cy),
            (cx, cy + 10),
            (cx - 8, cy)
        ]
        pygame.draw.polygon(self.image, gold_col, points)
        pygame.draw.polygon(self.image, flame_col, points, 2)
        
        # 内核
        pulse = 4 + int(math.sin(t * 3) * 2)
        pygame.draw.circle(self.image, flame_col, (cx, cy), pulse)


class BorderBullet(pygame.sprite.Sprite):
    """浮游炮辅助弹"""
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed = 15
        self.vy = -self.speed
        
        self.frame = 0
        self.lifetime = 60
        
        self.size = 16
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        self.frame += 1
        self.float_y += self.vy
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        if self.float_y < -20 or self.frame > self.lifetime:
            self.kill()
            return
        
        for mob in mobs:
            if self.rect.colliderect(mob.rect):
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage)
                self.kill()
                return
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        gold_col = self.theme["gold"]
        pygame.draw.circle(self.image, gold_col, (cx, cy), 5)


# ==================== 神龙冲拳（长按蓄力冲刺） ====================
class DragonDashSkill(pygame.sprite.Sprite):
    """
    神龙冲拳 - 长按蓄力后冲刺
    无敌冲锋半屏距离，出发点和终点留下龙卷风
    """
    
    def __init__(self, x, y, damage, direction, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        self.start_x = float(x)
        self.start_y = float(y)
        self.float_x = float(x)
        self.float_y = float(y)
        
        self.direction = direction  # 冲刺方向角度
        self.dash_distance = HEIGHT * 0.5  # 半屏距离
        self.dash_speed = 35
        self.traveled = 0
        
        self.frame = 0
        self.phase = "dash"  # dash -> trail
        
        # 无敌
        if owner:
            owner.invincible = True
            owner.skill_locked = True
        
        self.size = 100
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        
        if self.phase == "dash":
            # 冲刺移动
            vx = math.cos(math.radians(self.direction)) * self.dash_speed
            vy = math.sin(math.radians(self.direction)) * self.dash_speed
            self.float_x += vx
            self.float_y += vy
            self.traveled += self.dash_speed
            
            # 更新玩家位置
            if self.owner:
                # 限制在屏幕内
                self.float_x = max(30, min(WIDTH - 30, self.float_x))
                self.float_y = max(30, min(HEIGHT - 30, self.float_y))
                self.owner.rect.center = (int(self.float_x), int(self.float_y))
            
            self.rect.center = (int(self.float_x), int(self.float_y))
            
            # 碰撞伤害
            self._deal_collision_damage()
            
            # 冲刺结束
            if self.traveled >= self.dash_distance:
                self.phase = "trail"
                self._spawn_tornados()
        
        elif self.phase == "trail":
            # 结束技能
            self._end_skill()
            self.kill()
            return
        
        self._render()
    
    def _deal_collision_damage(self):
        """碰撞伤害"""
        for mob in mobs:
            if self.rect.colliderect(mob.rect):
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage * 2)
    
    def _spawn_tornados(self):
        """生成龙卷风"""
        # 起点龙卷风
        t1 = DraconicTornado(self.start_x, self.start_y, self.damage * 0.3, self.owner, self.style)
        # 终点龙卷风
        t2 = DraconicTornado(self.float_x, self.float_y, self.damage * 0.3, self.owner, self.style)
    
    def _end_skill(self):
        if self.owner:
            self.owner.invincible = False
            self.owner.skill_locked = False
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.2
        
        flame_col = self.theme["flame"]
        gold_col = self.theme["gold"]
        core_col = self.theme["core"]
        
        # 冲刺光芒
        for i in range(5):
            angle = t * 3 + i * 1.25
            r = 30 + i * 5
            px = cx + int(math.cos(angle) * 10)
            py = cy + int(math.sin(angle) * 10)
            pygame.draw.circle(self.image, (*flame_col, 150), (px, py), 8 - i)
        
        # 核心
        pygame.draw.circle(self.image, gold_col, (cx, cy), 15)
        pygame.draw.circle(self.image, core_col, (cx, cy), 10)


# ==================== 龙卷风（神龙冲拳留痕） ====================
class DraconicTornado(pygame.sprite.Sprite):
    """
    龙卷风 - 神龙冲拳留下的安全区
    阻挡敌方弹幕，持续绞杀敌人
    """
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(x)
        self.float_y = float(y)
        
        self.frame = 0
        self.lifetime = 180  # 3秒
        self.rotation = 0
        
        self.size = 120
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        self.rotation += 8
        
        if self.frame >= self.lifetime:
            self.kill()
            return
        
        # 消弹
        if self.frame % 2 == 0:
            for bullet in enemy_bullets:
                dist = math.hypot(bullet.rect.centerx - self.float_x,
                                bullet.rect.centery - self.float_y)
                if dist < 50:
                    bullet.kill()
        
        # 伤害敌人
        if self.frame % 10 == 0:
            for mob in mobs:
                dist = math.hypot(mob.rect.centerx - self.float_x,
                                mob.rect.centery - self.float_y)
                if dist < 60:
                    if hasattr(mob, 'take_damage'):
                        mob.take_damage(self.damage)
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.1
        
        flame_col = self.theme["flame"]
        armor_col = self.theme["armor"]
        
        # 淡出效果
        alpha = int(255 * (1 - self.frame / self.lifetime))
        
        # 旋转的龙卷风
        for i in range(8):
            angle = math.radians(self.rotation + i * 45)
            for j in range(4):
                r = 20 + j * 10
                px = cx + int(math.cos(angle + j * 0.3) * r)
                py = cy + int(math.sin(angle + j * 0.3) * r)
                dot_alpha = max(0, alpha - j * 30)
                if dot_alpha > 0:
                    pygame.draw.circle(self.image, (*flame_col, dot_alpha), (px, py), 4 - j)
        
        # 中心
        pygame.draw.circle(self.image, (*armor_col, alpha), (cx, cy), 15)


# ==================== 丛林龙息（被动：每10杀触发） ====================
class JungleBreath(pygame.sprite.Sprite):
    """丛林龙息 - 每消灭10个敌人释放追踪火球"""
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed = 8
        self.homing = 0.1
        self.target = None
        
        self.frame = 0
        self.lifetime = 120
        
        # 初始速度随机方向
        angle = random.uniform(0, 360)
        self.vx = math.cos(math.radians(angle)) * self.speed
        self.vy = math.sin(math.radians(angle)) * self.speed
        
        self.size = 30
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        self.frame += 1
        
        # 寻找目标
        if self.target is None or not self.target.alive():
            self._find_target()
        
        # 追踪
        if self.target:
            dx = self.target.rect.centerx - self.float_x
            dy = self.target.rect.centery - self.float_y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.vx += (dx / dist) * self.homing * self.speed
                self.vy += (dy / dist) * self.homing * self.speed
                spd = math.hypot(self.vx, self.vy)
                if spd > self.speed * 1.3:
                    self.vx = self.vx / spd * self.speed * 1.3
                    self.vy = self.vy / spd * self.speed * 1.3
        
        self.float_x += self.vx
        self.float_y += self.vy
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        if self.frame > self.lifetime:
            self.kill()
            return
        
        # 碰撞
        for mob in mobs:
            if self.rect.colliderect(mob.rect):
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage)
                # 留下毒雾
                self._spawn_poison(mob.rect.centerx, mob.rect.centery)
                self.kill()
                return
        
        self._render()
    
    def _find_target(self):
        min_dist = float('inf')
        for mob in mobs:
            dist = math.hypot(mob.rect.centerx - self.float_x,
                            mob.rect.centery - self.float_y)
            if dist < min_dist:
                min_dist = dist
                self.target = mob
    
    def _spawn_poison(self, x, y):
        """留下毒雾"""
        cloud = PoisonCloud(x, y, self.damage * 0.2, self.owner, self.style)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.2
        
        armor_col = self.theme["armor"]
        flame_col = self.theme["flame"]
        
        # 绿色火球
        pulse = 8 + int(math.sin(t * 3) * 3)
        pygame.draw.circle(self.image, armor_col, (cx, cy), pulse + 4)
        pygame.draw.circle(self.image, flame_col, (cx, cy), pulse)


class PoisonCloud(pygame.sprite.Sprite):
    """毒雾 - 丛林龙息留下的持续伤害区域"""
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(x)
        self.float_y = float(y)
        
        self.frame = 0
        self.lifetime = 60  # 1秒
        
        self.size = 80
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        
        if self.frame >= self.lifetime:
            self.kill()
            return
        
        # 持续伤害
        if self.frame % 15 == 0:
            for mob in mobs:
                dist = math.hypot(mob.rect.centerx - self.float_x,
                                mob.rect.centery - self.float_y)
                if dist < 35:
                    if hasattr(mob, 'take_damage'):
                        mob.take_damage(self.damage)
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        
        armor_col = self.theme["armor"]
        alpha = int(150 * (1 - self.frame / self.lifetime))
        
        # 毒雾圈
        for i in range(3):
            r = 25 + i * 8
            a = max(0, alpha - i * 30)
            if a > 0:
                pygame.draw.circle(self.image, (*armor_col, a), (cx, cy), r, 2)


# ==================== 终极技能 I: 千兆核爆 [F] ====================
class GigaNukeSkill(pygame.sprite.Sprite):
    """
    千兆核爆 - 缩圈机制
    火柱从边缘汇聚推挤敌人，中心引爆日蚀之火
    """
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(WIDTH // 2)
        self.float_y = float(HEIGHT // 2)
        
        self.frame = 0
        self.phase = "converge"  # converge -> explode
        self.converge_duration = 120  # 2秒
        self.explode_duration = 40
        
        self.converge_radius = max(WIDTH, HEIGHT)
        self.min_radius = 80
        
        # 火柱
        self.pillars = []
        for i in range(12):
            angle = i * 30
            self.pillars.append({
                'angle': angle,
                'dist': self.converge_radius
            })
        
        if owner:
            owner.invincible = True
            owner.skill_locked = True
        
        self.size = max(WIDTH, HEIGHT) + 100
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.float_x), int(self.float_y)))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        
        if self.phase == "converge":
            self._update_converge()
            if self.frame >= self.converge_duration:
                self.phase = "explode"
                self.frame = 0
                self._trigger_explosion()
        
        elif self.phase == "explode":
            if self.frame >= self.explode_duration:
                self._end_skill()
                self.kill()
                return
        
        self._render()
    
    def _update_converge(self):
        """火柱收缩，推挤敌人"""
        progress = self.frame / self.converge_duration
        target_radius = self.converge_radius - (self.converge_radius - self.min_radius) * progress
        
        for pillar in self.pillars:
            pillar['dist'] = target_radius
        
        # 每5帧推挤一次敌人
        if self.frame % 5 == 0:
            cx, cy = self.float_x, self.float_y
            for mob in mobs:
                dist = math.hypot(mob.rect.centerx - cx, mob.rect.centery - cy)
                if dist > target_radius - 30:
                    # 推向中心
                    angle = math.atan2(cy - mob.rect.centery, cx - mob.rect.centerx)
                    push = 8
                    mob.rect.centerx += int(math.cos(angle) * push)
                    mob.rect.centery += int(math.sin(angle) * push)
                    # 伤害
                    if hasattr(mob, 'take_damage'):
                        mob.take_damage(self.damage * 0.05)
    
    def _trigger_explosion(self):
        """中心爆炸"""
        # 全屏闪白
        flash = ScreenFlash((255, 200, 100), 30)
        all_sprites.add(flash)
        
        # 对所有敌人造成大伤害
        for mob in mobs:
            if hasattr(mob, 'take_damage'):
                mob.take_damage(self.damage * 3)
    
    def _end_skill(self):
        if self.owner:
            self.owner.invincible = False
            self.owner.skill_locked = False
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.1
        
        flame_col = self.theme["flame"]
        core_col = self.theme["core"]
        gold_col = self.theme["gold"]
        
        if self.phase == "converge":
            # 绘制火柱
            for pillar in self.pillars:
                angle = math.radians(pillar['angle'])
                dist = pillar['dist']
                px = cx + int(math.cos(angle) * dist)
                py = cy + int(math.sin(angle) * dist)
                
                # 火柱
                for j in range(5):
                    r = 15 - j * 2
                    a = 200 - j * 30
                    if r > 0 and a > 0:
                        pygame.draw.circle(self.image, (*flame_col, a), (px, py), r)
            
            # 收缩圈
            ring_r = int(self.pillars[0]['dist'])
            if ring_r > 0:
                pygame.draw.circle(self.image, (*core_col, 100), (cx, cy), ring_r, 3)
        
        elif self.phase == "explode":
            # 爆炸效果
            exp_r = int(self.frame * 15)
            alpha = max(0, 255 - self.frame * 6)
            if alpha > 0:
                pygame.draw.circle(self.image, (*gold_col, alpha), (cx, cy), exp_r)
                pygame.draw.circle(self.image, (*core_col, alpha), (cx, cy), exp_r, 5)


# ==================== 终极技能 II: 龙群盛宴 [G] ====================
class DraconicSwarmSkill(pygame.sprite.Sprite):
    """
    龙群盛宴 - 召唤大黄蜂僚机
    两只机械大黄蜂冲撞敌人并释放环形弹幕
    """
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(x)
        self.float_y = float(y)
        
        self.frame = 0
        self.lifetime = 300  # 5秒
        
        # 召唤两只大黄蜂
        self.bees = []
        for i in range(2):
            side = 1 if i == 0 else -1
            bee = Bumblebirb(x + side * 60, y, damage * 0.5, owner, style)
            self.bees.append(bee)
        
        if owner:
            owner.invincible = True
        
        self.size = 10
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        
        # 检查大黄蜂是否还存活
        alive_bees = [b for b in self.bees if b.alive()]
        
        if self.frame >= self.lifetime or len(alive_bees) == 0:
            # 结束
            for bee in alive_bees:
                bee.kill()
            self._end_skill()
            self.kill()
            return
    
    def _end_skill(self):
        if self.owner:
            self.owner.invincible = False


class Bumblebirb(pygame.sprite.Sprite):
    """机械大黄蜂 - 龙群盛宴召唤物"""
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed = 10
        self.target = None
        
        self.frame = 0
        self.attack_cooldown = 0
        
        self.size = 50
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        self.attack_cooldown = max(0, self.attack_cooldown - 1)
        
        # 寻找目标
        if self.target is None or not self.target.alive():
            self._find_target()
        
        # 追踪并冲撞
        if self.target and self.target.alive():
            dx = self.target.rect.centerx - self.float_x
            dy = self.target.rect.centery - self.float_y
            dist = math.hypot(dx, dy)
            
            if dist > 30:
                self.float_x += (dx / dist) * self.speed
                self.float_y += (dy / dist) * self.speed
            
            # 碰撞攻击
            if dist < 40 and self.attack_cooldown == 0:
                self._attack()
                self.attack_cooldown = 60
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        self._render()
    
    def _find_target(self):
        min_dist = float('inf')
        for mob in mobs:
            dist = math.hypot(mob.rect.centerx - self.float_x,
                            mob.rect.centery - self.float_y)
            if dist < min_dist:
                min_dist = dist
                self.target = mob
    
    def _attack(self):
        """冲撞攻击并释放环形弹幕"""
        if self.target and hasattr(self.target, 'take_damage'):
            self.target.take_damage(self.damage * 2)
        
        # 环形弹幕
        for i in range(8):
            angle = i * 45
            bullet = BumblebirbBullet(self.float_x, self.float_y, 
                                      self.damage * 0.3, angle, self.owner, self.style)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.2
        
        gold_col = self.theme["gold"]
        armor_col = self.theme["armor"]
        flame_col = self.theme["flame"]
        
        # 身体
        pygame.draw.ellipse(self.image, gold_col, (cx - 15, cy - 10, 30, 20))
        pygame.draw.ellipse(self.image, armor_col, (cx - 12, cy - 7, 24, 14))
        
        # 翅膀
        wing_y = cy + int(math.sin(t * 8) * 3)
        pygame.draw.ellipse(self.image, (*flame_col, 150), (cx - 20, wing_y - 12, 15, 24))
        pygame.draw.ellipse(self.image, (*flame_col, 150), (cx + 5, wing_y - 12, 15, 24))


class BumblebirbBullet(pygame.sprite.Sprite):
    """大黄蜂弹幕"""
    
    def __init__(self, x, y, damage, angle, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed = 8
        self.vx = math.cos(math.radians(angle)) * self.speed
        self.vy = math.sin(math.radians(angle)) * self.speed
        
        self.frame = 0
        self.lifetime = 60
        
        self.size = 14
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        self.frame += 1
        self.float_x += self.vx
        self.float_y += self.vy
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        if self.frame > self.lifetime:
            self.kill()
            return
        
        for mob in mobs:
            if self.rect.colliderect(mob.rect):
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage)
                self.kill()
                return
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        gold_col = self.theme["gold"]
        pygame.draw.circle(self.image, gold_col, (cx, cy), 5)


# ==================== 终极技能 III: 宿敌升天 [C] ====================
class EnemyAscendedSkill(pygame.sprite.Sprite):
    """
    魔君之证·宿敌升天 - 最终绝招
    化为巨龙笼罩全屏，光标所指天降地狱火柱
    """
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(WIDTH // 2)
        self.float_y = float(HEIGHT // 2)
        
        self.frame = 0
        self.phase = "transform"  # transform -> rampage -> end
        self.transform_duration = 60   # 1秒
        self.rampage_duration = 300    # 5秒
        self.end_duration = 60         # 1秒
        
        self.fire_cooldown = 0
        
        if owner:
            owner.invincible = True
            owner.skill_locked = True
        
        self.size = max(WIDTH, HEIGHT)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.float_x), int(self.float_y)))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        self.fire_cooldown = max(0, self.fire_cooldown - 1)
        
        if self.phase == "transform":
            if self.frame >= self.transform_duration:
                self.phase = "rampage"
                self.frame = 0
        
        elif self.phase == "rampage":
            # 持续释放火柱
            self._fire_pillars()
            
            if self.frame >= self.rampage_duration:
                self.phase = "end"
                self.frame = 0
                self._final_blast()
        
        elif self.phase == "end":
            if self.frame >= self.end_duration:
                self._end_skill()
                self.kill()
                return
        
        self._render()
    
    def _fire_pillars(self):
        """向敌人位置释放火柱"""
        if self.fire_cooldown > 0:
            return
        
        self.fire_cooldown = 15  # 每0.25秒一发
        
        # 随机选择一个敌人
        if len(mobs) > 0:
            target = random.choice(list(mobs))
            pillar = HellFirePillar(target.rect.centerx, 0, self.damage * 0.5, 
                                   self.owner, self.style)
    
    def _final_blast(self):
        """最终爆发"""
        flash = ScreenFlash((255, 215, 0), 40)
        all_sprites.add(flash)
        
        for mob in mobs:
            if hasattr(mob, 'take_damage'):
                mob.take_damage(self.damage * 5)
    
    def _end_skill(self):
        if self.owner:
            self.owner.invincible = False
            self.owner.skill_locked = False
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.05
        
        gold_col = self.theme["gold"]
        flame_col = self.theme["flame"]
        armor_col = self.theme["armor"]
        
        if self.phase == "transform":
            # 变身效果 - 光芒扩散
            progress = self.frame / self.transform_duration
            r = int(100 + 200 * progress)
            alpha = int(150 * progress)
            pygame.draw.circle(self.image, (*gold_col, alpha), (cx, cy), r, 5)
        
        elif self.phase == "rampage":
            # 巨龙影子
            alpha = 100 + int(50 * math.sin(t * 2))
            
            # 龙形轮廓（简化）
            # 身体
            body_points = [
                (cx - 150, cy - 50),
                (cx + 150, cy - 50),
                (cx + 180, cy),
                (cx + 150, cy + 50),
                (cx - 150, cy + 50),
                (cx - 180, cy),
            ]
            pygame.draw.polygon(self.image, (*gold_col, alpha), body_points)
            
            # 翅膀
            wing_offset = int(math.sin(t * 3) * 20)
            left_wing = [
                (cx - 100, cy),
                (cx - 250, cy - 100 + wing_offset),
                (cx - 200, cy + 50),
            ]
            right_wing = [
                (cx + 100, cy),
                (cx + 250, cy - 100 + wing_offset),
                (cx + 200, cy + 50),
            ]
            pygame.draw.polygon(self.image, (*flame_col, alpha), left_wing)
            pygame.draw.polygon(self.image, (*flame_col, alpha), right_wing)
            
            # 头部
            pygame.draw.circle(self.image, (*armor_col, alpha), (cx + 200, cy), 40)
            # 眼睛
            pygame.draw.circle(self.image, (*flame_col, 200), (cx + 210, cy - 10), 10)
        
        elif self.phase == "end":
            # 消散效果
            alpha = int(150 * (1 - self.frame / self.end_duration))
            if alpha > 0:
                pygame.draw.circle(self.image, (*gold_col, alpha), (cx, cy), 200, 10)


class HellFirePillar(pygame.sprite.Sprite):
    """地狱火柱 - 从天而降"""
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        self.target_x = float(x)
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed = 25
        
        self.frame = 0
        self.hit = False
        
        self.size = 60
        self.image = pygame.Surface((self.size, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(midtop=(int(x), 0))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        self.float_y += self.speed
        
        # 到达目标高度
        if self.float_y >= HEIGHT - 50 and not self.hit:
            self.hit = True
            self._explode()
        
        if self.frame > 60:
            self.kill()
            return
        
        self._render()
    
    def _explode(self):
        """落地爆炸"""
        for mob in mobs:
            dist = abs(mob.rect.centerx - self.target_x)
            if dist < 50:
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx = self.size // 2
        
        flame_col = self.theme["flame"]
        core_col = self.theme["core"]
        
        # 火柱
        h = int(self.float_y)
        if h > 0:
            alpha = 200 if not self.hit else max(0, 200 - (self.frame - 30) * 10)
            pygame.draw.rect(self.image, (*flame_col, alpha), (cx - 15, 0, 30, h))
            pygame.draw.rect(self.image, (*core_col, alpha), (cx - 8, 0, 16, h))


# ==================== 屏幕闪白效果 ====================
class ScreenFlash(pygame.sprite.Sprite):
    """全屏闪光效果"""
    
    def __init__(self, color=(255, 255, 255), duration=15):
        super().__init__()
        self.color = color
        self.frame = 0
        self.duration = duration
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
    
    def update(self):
        self.frame += 1
        if self.frame >= self.duration:
            self.kill()
            return
        
        progress = self.frame / self.duration
        alpha = int(200 * (1 - progress))
        self.image.fill((*self.color, alpha))


# ==================== 预览渲染 ====================
def render_yharon_bullet_preview(style="default"):
    """渲染犽戎弹幕预览"""
    theme = get_theme(style)
    size = 80
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    
    flame_col = theme["flame"]
    gold_col = theme["gold"]
    armor_col = theme["armor"]
    
    # 火焰核心
    pygame.draw.circle(surf, flame_col, (cx, cy), 20)
    pygame.draw.circle(surf, gold_col, (cx, cy), 12)
    
    # 浮游炮
    for i, angle in enumerate([45, -45, 135, -135]):
        px = cx + int(math.cos(math.radians(angle)) * 28)
        py = cy + int(math.sin(math.radians(angle)) * 28)
        points = [
            (px, py - 6),
            (px + 5, py),
            (px, py + 6),
            (px - 5, py)
        ]
        pygame.draw.polygon(surf, gold_col, points)
    
    # 龙形装饰
    pygame.draw.arc(surf, armor_col, (cx - 35, cy - 35, 70, 70), 0.5, 2.6, 3)
    
    return surf
