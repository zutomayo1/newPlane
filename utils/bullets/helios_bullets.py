"""
星渊火陨·赫利俄斯 - 专属子弹模块
抛物线火雨弹，落地分裂燃烧区

特性：
- 抛物线弹道
- 落地后分裂成燃烧区域
- 流星群大招覆盖全场
"""
import pygame
import math
import random
from config import all_sprites, mobs


class MeteorBullet(pygame.sprite.Sprite):
    """陨石弹 - 抛物线轨迹，落地分裂"""
    
    def __init__(self, x, y, target_x, target_y, damage, owner=None):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.piercing = 0  # 不穿透，落地爆炸
        self.color = (255, 100, 50)
        
        # 起点和终点
        self.start_x = float(x)
        self.start_y = float(y)
        self.target_x = float(target_x)
        self.target_y = float(target_y)
        
        # 飞行进度 (0-1)
        self.progress = 0.0
        self.flight_time = 60  # 帧数
        
        # 抛物线高度
        self.arc_height = 150
        
        # 当前位置
        self.float_x = float(x)
        self.float_y = float(y)
        
        # 动画
        self.frame = 0
        self.rotation = random.uniform(0, 360)
        
        # 创建图像
        self.size = 20
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self._draw_meteor()
        self.rect = self.image.get_rect(center=(x, y))
        
        # 拖尾
        self.trail = []
        self.max_trail = 10
    
    def _draw_meteor(self):
        """绘制陨石"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size, self.size
        
        # 根据进度调整大小（越接近地面越大）
        scale = 0.5 + self.progress * 0.5
        meteor_size = int(12 * scale)
        
        # 外焰 - 橙红色
        for i in range(3):
            flame_size = meteor_size + 4 - i * 2
            alpha = 150 - i * 40
            flame_color = (255, 100 + i * 30, 0, alpha)
            flame_surf = pygame.Surface((flame_size * 2, flame_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(flame_surf, flame_color, (flame_size, flame_size), flame_size)
            self.image.blit(flame_surf, (cx - flame_size, cy - flame_size))
        
        # 陨石核心 - 暗红/黑色
        core_color = (80, 30, 10)
        pygame.draw.circle(self.image, core_color, (cx, cy), meteor_size)
        
        # 熔岩裂纹
        crack_color = (255, 150, 50)
        for i in range(4):
            angle = self.rotation + i * 90
            end_x = cx + math.cos(math.radians(angle)) * meteor_size * 0.8
            end_y = cy + math.sin(math.radians(angle)) * meteor_size * 0.8
            pygame.draw.line(self.image, crack_color, (cx, cy), (end_x, end_y), 2)
        
        # 核心亮点
        pygame.draw.circle(self.image, (255, 200, 100), (cx - 3, cy - 3), 3)
    
    def update(self):
        """更新陨石"""
        self.frame += 1
        self.rotation += 5
        
        # 记录拖尾
        self.trail.append((self.float_x, self.float_y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
        
        # 更新进度
        self.progress += 1.0 / self.flight_time
        
        if self.progress >= 1.0:
            # 落地 - 创建燃烧区
            self._create_burn_zone()
            self.kill()
            return
        
        # 抛物线位置计算
        # 水平线性插值
        self.float_x = self.start_x + (self.target_x - self.start_x) * self.progress
        # 垂直抛物线
        arc = 4 * self.arc_height * self.progress * (1 - self.progress)
        self.float_y = self.start_y + (self.target_y - self.start_y) * self.progress - arc
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        self._draw_meteor()
    
    def _create_burn_zone(self):
        """创建燃烧区域"""
        zone = BurnZone(self.target_x, self.target_y, self.damage, self.owner)
        all_sprites.add(zone)


class BurnZone(pygame.sprite.Sprite):
    """燃烧区域 - 持续伤害"""
    
    def __init__(self, x, y, damage, owner=None):
        super().__init__()
        self.damage = damage * 0.3  # 每tick伤害
        self.owner = owner
        self.x = x
        self.y = y
        
        # 区域半径
        self.radius = 50
        self.max_radius = 60
        
        # 持续时间
        self.duration = 120  # 2秒
        self.frame = 0
        
        # 伤害间隔
        self.damage_tick = 0
        self.damage_interval = 15  # 每15帧伤害一次
        
        # 创建图像
        self.image = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        self._draw_zone()
        self.rect = self.image.get_rect(center=(x, y))
    
    def _draw_zone(self):
        """绘制燃烧区域"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.max_radius, self.max_radius
        
        # 淡出效果
        fade = 1.0 - (self.frame / self.duration)
        
        # 外圈火焰
        for i in range(3):
            r = self.radius - i * 10
            if r > 0:
                alpha = int(100 * fade)
                color = (255, 80 + i * 40, 0, alpha)
                surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (r, r), r)
                self.image.blit(surf, (cx - r, cy - r))
        
        # 随机火焰粒子
        for _ in range(5):
            fx = cx + random.randint(-self.radius + 10, self.radius - 10)
            fy = cy + random.randint(-self.radius + 10, self.radius - 10)
            fsize = random.randint(3, 8)
            falpha = int(random.randint(100, 200) * fade)
            fcolor = (255, random.randint(100, 200), 0, falpha)
            pygame.draw.circle(self.image, fcolor, (fx, fy), fsize)
    
    def update(self):
        """更新燃烧区域"""
        self.frame += 1
        self.damage_tick += 1
        
        # 扩展效果
        if self.frame < 10:
            self.radius = min(self.max_radius, self.radius + 2)
        
        # 伤害敌人
        if self.damage_tick >= self.damage_interval:
            self.damage_tick = 0
            self._damage_enemies()
        
        # 重绘
        self._draw_zone()
        
        # 结束
        if self.frame >= self.duration:
            self.kill()
    
    def _damage_enemies(self):
        """对区域内敌人造成伤害"""
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.x, enemy.rect.centery - self.y)
            if dist < self.radius:
                enemy.hp -= self.damage
                if hasattr(enemy, 'hit_flash'):
                    enemy.hit_flash = 5


class MeteorShower(pygame.sprite.Sprite):
    """流星群 - 大招效果 ★强化版★"""
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 2
        
        # 陨石数量和间隔
        self.meteor_count = 12  # 增加陨石数量
        self.meteors_spawned = 0
        self.spawn_interval = 6  # 更密集
        self.spawn_timer = 0
        
        # 生命周期
        self.duration = self.meteor_count * self.spawn_interval + 90
        self.frame = 0
        
        # 创建全屏图像用于绘制震撼效果
        self.image = pygame.Surface((540, 700), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        # 天空变红效果
        self.sky_tint = 0
        
        # 爆炸点记录（用于绘制残留火焰）
        self.explosion_points = []
        
        all_sprites.add(self)
    
    def _draw_sky_effect(self):
        """绘制天空燃烧效果"""
        self.image.fill((0, 0, 0, 0))
        
        # 天空红色渲染
        if self.frame < 30:
            self.sky_tint = min(80, self.sky_tint + 4)
        elif self.frame > self.duration - 30:
            self.sky_tint = max(0, self.sky_tint - 4)
        
        if self.sky_tint > 0:
            sky_surf = pygame.Surface((540, 300), pygame.SRCALPHA)
            # 渐变天空
            for i in range(30):
                alpha = int(self.sky_tint * (1 - i / 30))
                pygame.draw.rect(sky_surf, (255, 50 + i * 3, 0, alpha), (0, i * 10, 540, 12))
            self.image.blit(sky_surf, (0, 0))
        
        # 绘制爆炸残留火焰
        for i, (ex, ey, ef) in enumerate(self.explosion_points[:]):
            ef_progress = (self.frame - ef) / 60
            if ef_progress > 1:
                self.explosion_points.remove((ex, ey, ef))
                continue
            
            # 火焰柱
            flame_h = int(80 * (1 - ef_progress))
            flame_w = int(40 * (1 - ef_progress * 0.5))
            flame_alpha = int(150 * (1 - ef_progress))
            
            for j in range(5):
                fw = flame_w - j * 6
                fh = flame_h - j * 10
                if fw > 0 and fh > 0:
                    flame_color = (255, 100 + j * 30, 0, flame_alpha - j * 25)
                    flame_surf = pygame.Surface((fw, fh), pygame.SRCALPHA)
                    # 火焰形状
                    points = [(fw // 2, 0), (0, fh), (fw, fh)]
                    pygame.draw.polygon(flame_surf, flame_color, points)
                    self.image.blit(flame_surf, (ex - fw // 2, ey - fh))
            
            # 余烬粒子
            for _ in range(3):
                px = ex + random.randint(-30, 30)
                py = ey - random.randint(0, int(flame_h * 1.5))
                psize = random.randint(2, 5)
                palpha = int(200 * (1 - ef_progress))
                pygame.draw.circle(self.image, (255, 200, 50, palpha), (px, py), psize)
        
        # 环境火星
        for _ in range(8):
            spark_x = random.randint(0, 540)
            spark_y = random.randint(0, 400)
            spark_size = random.randint(1, 3)
            spark_alpha = random.randint(100, 200)
            pygame.draw.circle(self.image, (255, 150, 50, spark_alpha), (spark_x, spark_y), spark_size)
    
    def update(self):
        """更新流星群"""
        self.frame += 1
        self.spawn_timer += 1
        
        # 绘制环境效果
        self._draw_sky_effect()
        
        # 生成陨石
        if self.meteors_spawned < self.meteor_count and self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self._spawn_meteor()
            self.meteors_spawned += 1
        
        # 结束
        if self.frame >= self.duration:
            self.kill()
    
    def _spawn_meteor(self):
        """生成一颗陨石"""
        # 随机目标位置
        target_x = random.randint(50, 490)
        target_y = random.randint(150, 550)
        
        # 起始位置（屏幕上方随机）
        start_x = target_x + random.randint(-150, 150)
        start_y = -80
        
        # 记录爆炸点
        self.explosion_points.append((target_x, target_y, self.frame + 60))
        
        meteor = MeteorBullet(start_x, start_y, target_x, target_y, self.damage, self.owner)
        all_sprites.add(meteor)


class SunFall(pygame.sprite.Sprite):
    """太阳坠落 - 三技能，召唤巨型太阳从天而降"""
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 5
        
        # 巨型太阳参数
        self.sun_x = 270
        self.sun_y = -100
        self.target_y = 300
        self.sun_radius = 80
        
        # 下落速度
        self.fall_speed = 3
        
        # 阶段: 0=下落, 1=爆发, 2=结束
        self.phase = 0
        self.frame = 0
        self.explosion_frame = 0
        self.explosion_duration = 60
        
        # 创建图像
        self.image = pygame.Surface((200, 200), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(self.sun_x, self.sun_y))
        
        all_sprites.add(self)
    
    def _draw_sun(self):
        """绘制太阳"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = 100, 100
        
        # 外层光晕
        for i in range(5):
            glow_r = self.sun_radius + 20 - i * 5
            alpha = 50 - i * 10
            glow_color = (255, 200, 50, alpha)
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, glow_color, (glow_r, glow_r), glow_r)
            self.image.blit(glow_surf, (cx - glow_r, cy - glow_r))
        
        # 太阳核心
        pygame.draw.circle(self.image, (255, 180, 50), (cx, cy), self.sun_radius)
        pygame.draw.circle(self.image, (255, 220, 100), (cx, cy), self.sun_radius - 15)
        
        # 日冕射线
        for i in range(12):
            angle = self.frame * 2 + i * 30
            length = self.sun_radius + 30 + math.sin(self.frame * 0.1 + i) * 10
            end_x = cx + math.cos(math.radians(angle)) * length
            end_y = cy + math.sin(math.radians(angle)) * length
            pygame.draw.line(self.image, (255, 150, 0), (cx, cy), (end_x, end_y), 4)
    
    def _draw_explosion(self):
        """绘制爆炸"""
        self.image = pygame.Surface((540, 700), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(270, 350))
        
        cx, cy = 270, self.target_y
        progress = self.explosion_frame / self.explosion_duration
        
        # 扩散环
        ring_r = int(300 * progress)
        ring_alpha = int(200 * (1 - progress))
        if ring_alpha > 0:
            ring_color = (255, 150, 50, ring_alpha)
            ring_surf = pygame.Surface((ring_r * 2, ring_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, ring_color, (ring_r, ring_r), ring_r, 5)
            self.image.blit(ring_surf, (cx - ring_r, cy - ring_r))
        
        # 火焰波
        for i in range(8):
            wave_r = int(200 * progress) + i * 20
            wave_alpha = int(150 * (1 - progress))
            if wave_alpha > 0:
                wave_color = (255, 100 + i * 15, 0, wave_alpha)
                wave_surf = pygame.Surface((wave_r * 2, wave_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(wave_surf, wave_color, (wave_r, wave_r), wave_r)
                self.image.blit(wave_surf, (cx - wave_r, cy - wave_r))
    
    def update(self):
        """更新太阳坠落"""
        self.frame += 1
        
        if self.phase == 0:  # 下落阶段
            self.sun_y += self.fall_speed
            self.rect.centery = int(self.sun_y)
            self._draw_sun()
            
            # 持续伤害经过的敌人
            for enemy in mobs:
                dist = math.hypot(enemy.rect.centerx - self.sun_x, enemy.rect.centery - self.sun_y)
                if dist < self.sun_radius + 20:
                    enemy.hp -= self.damage * 0.05
            
            # 到达目标
            if self.sun_y >= self.target_y:
                self.phase = 1
                self._explode()
        
        elif self.phase == 1:  # 爆发阶段
            self.explosion_frame += 1
            self._draw_explosion()
            
            # 持续伤害
            if self.explosion_frame % 10 == 0:
                for enemy in mobs:
                    enemy.hp -= self.damage * 0.2
            
            if self.explosion_frame >= self.explosion_duration:
                self.phase = 2
                self.kill()
    
    def _explode(self):
        """爆发效果"""
        # 全屏伤害
        for enemy in mobs:
            enemy.hp -= self.damage
            if hasattr(enemy, 'hit_flash'):
                enemy.hit_flash = 15
        
        # 创建燃烧区
        for i in range(5):
            bx = random.randint(50, 490)
            by = random.randint(100, 600)
            zone = BurnZone(bx, by, self.damage * 0.5, self.owner)
            all_sprites.add(zone)
