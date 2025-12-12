"""
极昼寒界·霜曜 - 专属子弹模块
极寒激光，穿透2次并减速，命中3次冻结

特性：
- 直线激光穿透
- 命中减速效果
- 叠3层冻结2秒
"""
import pygame
import math
import random
from config import all_sprites, mobs


class FrostLaser(pygame.sprite.Sprite):
    """极寒激光 - 穿透+减速+冻结"""
    
    def __init__(self, x, y, damage, owner=None):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.color = (150, 220, 255)
        
        # 穿透次数
        self.piercing = 2
        self.hit_enemies = set()
        
        # 位置和速度
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed = 18
        
        # 动画
        self.frame = 0
        self.pulse = 0
        
        # 创建图像
        self.width = 8
        self.height = 40
        self.image = pygame.Surface((self.width + 20, self.height), pygame.SRCALPHA)
        self._draw_laser()
        self.rect = self.image.get_rect(center=(x, y))
        
        # 生命周期
        self.lifetime = 120
    
    def _draw_laser(self):
        """绘制激光"""
        self.image.fill((0, 0, 0, 0))
        cx = (self.width + 20) // 2
        
        # 脉冲效果
        pulse_size = 2 + int(2 * math.sin(self.frame * 0.3))
        
        # 外层光晕
        glow_color = (100, 200, 255, 80)
        glow_surf = pygame.Surface((self.width + 10 + pulse_size * 2, self.height), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, glow_color, (0, 0, self.width + 10 + pulse_size * 2, self.height))
        self.image.blit(glow_surf, (cx - (self.width + 10 + pulse_size * 2) // 2, 0))
        
        # 中间激光
        laser_color = (150, 220, 255)
        pygame.draw.rect(self.image, laser_color, (cx - self.width // 2, 0, self.width, self.height))
        
        # 核心亮线
        core_color = (220, 240, 255)
        pygame.draw.rect(self.image, core_color, (cx - 2, 0, 4, self.height))
        
        # 霜冻粒子
        for i in range(3):
            fy = random.randint(5, self.height - 5)
            fx = cx + random.randint(-self.width // 2, self.width // 2)
            pygame.draw.circle(self.image, (200, 240, 255), (fx, fy), 2)
    
    def update(self):
        """更新激光"""
        self.frame += 1
        
        # 移动
        self.float_y -= self.speed
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 重绘
        self._draw_laser()
        
        # 生命周期
        self.lifetime -= 1
        if self.lifetime <= 0 or self.rect.bottom < 0:
            self.kill()
    
    def on_hit_enemy(self, enemy):
        """命中敌人"""
        if id(enemy) in self.hit_enemies:
            return False
        
        self.hit_enemies.add(id(enemy))
        
        # 减速效果
        if not hasattr(enemy, 'frost_slow'):
            enemy.frost_slow = 0
        enemy.frost_slow = 60  # 1秒减速
        
        # 叠加冻结层数
        if not hasattr(enemy, 'frost_stacks'):
            enemy.frost_stacks = 0
        enemy.frost_stacks += 1
        
        # 3层冻结
        if enemy.frost_stacks >= 3:
            enemy.frost_stacks = 0
            if not hasattr(enemy, 'frozen'):
                enemy.frozen = 0
            enemy.frozen = 120  # 2秒冻结
        
        # 消耗穿透次数
        self.piercing -= 1
        if self.piercing < 0:
            self.kill()
        
        return True


class ZeroDegreeRay(pygame.sprite.Sprite):
    """零度射线 - 大招效果"""
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 3
        
        # 射线参数
        self.x = owner.rect.centerx
        self.width = 60
        
        # 持续时间
        self.duration = 90  # 1.5秒
        self.frame = 0
        
        # 伤害间隔
        self.damage_tick = 0
        self.damage_interval = 10
        
        # 创建图像
        self.image = pygame.Surface((self.width + 40, 800), pygame.SRCALPHA)
        self._draw_ray()
        self.rect = self.image.get_rect(midtop=(self.x, 0))
        
        all_sprites.add(self)
    
    def _draw_ray(self):
        """绘制射线"""
        self.image.fill((0, 0, 0, 0))
        cx = (self.width + 40) // 2
        
        # 淡入淡出
        if self.frame < 15:
            alpha_mult = self.frame / 15
        elif self.frame > self.duration - 15:
            alpha_mult = (self.duration - self.frame) / 15
        else:
            alpha_mult = 1.0
        
        # 外层寒气
        for i in range(3):
            w = self.width + 20 - i * 10
            alpha = int((60 - i * 15) * alpha_mult)
            color = (100, 180, 255, alpha)
            surf = pygame.Surface((w, 800), pygame.SRCALPHA)
            surf.fill(color)
            self.image.blit(surf, (cx - w // 2, 0))
        
        # 核心射线
        alpha = int(200 * alpha_mult)
        core_color = (150, 220, 255, alpha)
        pygame.draw.rect(self.image, core_color, (cx - self.width // 2, 0, self.width, 800))
        
        # 中心亮线
        bright_alpha = int(255 * alpha_mult)
        bright_color = (220, 245, 255, bright_alpha)
        pygame.draw.rect(self.image, bright_color, (cx - 5, 0, 10, 800))
        
        # 冰晶粒子
        for _ in range(10):
            px = cx + random.randint(-self.width // 2, self.width // 2)
            py = random.randint(0, 800)
            psize = random.randint(2, 5)
            pygame.draw.circle(self.image, (200, 240, 255, int(200 * alpha_mult)), (px, py), psize)
    
    def update(self):
        """更新射线"""
        self.frame += 1
        self.damage_tick += 1
        
        # 跟随玩家
        if self.owner and self.owner.alive():
            self.x = self.owner.rect.centerx
            self.rect.midtop = (self.x, 0)
        
        # 伤害敌人
        if self.damage_tick >= self.damage_interval:
            self.damage_tick = 0
            self._damage_enemies()
        
        # 重绘
        self._draw_ray()
        
        # 结束
        if self.frame >= self.duration:
            self.kill()
    
    def _damage_enemies(self):
        """对射线内敌人造成伤害"""
        for enemy in mobs:
            if abs(enemy.rect.centerx - self.x) < self.width // 2 + 10:
                enemy.hp -= self.damage
                if hasattr(enemy, 'hit_flash'):
                    enemy.hit_flash = 5
                # 冻结效果
                if not hasattr(enemy, 'frozen'):
                    enemy.frozen = 0
                enemy.frozen = max(enemy.frozen, 30)


class AbsoluteZero(pygame.sprite.Sprite):
    """绝对零度 - 三技能 ★强化版★ 全屏冻结所有敌人"""
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 4
        
        # 阶段
        self.phase = 0  # 0=聚能, 1=爆发, 2=冰封持续, 3=结束
        self.frame = 0
        
        # 聚能时间
        self.charge_duration = 45
        # 冻结时间
        self.freeze_duration = 180  # 3秒
        
        # 中心位置
        self.center_x = 270
        self.center_y = 350
        
        # 效果半径
        self.effect_radius = 0
        self.max_radius = 450
        
        # 冰晶碎片
        self.ice_shards = []
        for _ in range(50):
            self.ice_shards.append({
                'x': random.randint(0, 540),
                'y': random.randint(0, 700),
                'size': random.randint(5, 20),
                'rotation': random.uniform(0, 360),
                'fall_speed': random.uniform(0.5, 2),
                'sway': random.uniform(-1, 1)
            })
        
        # 冰霜纹理点
        self.frost_points = []
        
        # 创建图像
        self.image = pygame.Surface((540, 700), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _draw_charge(self):
        """绘制聚能效果 - 冰晶漩涡"""
        self.image.fill((0, 0, 0, 0))
        
        progress = self.frame / self.charge_duration
        cx, cy = self.center_x, self.center_y
        
        # 收缩的冰晶螺旋
        for ring in range(5):
            ring_r = int(250 * (1 - progress) + ring * 30)
            num_crystals = 8 + ring * 4
            for i in range(num_crystals):
                angle = i * (360 / num_crystals) + self.frame * (5 - ring) + ring * 30
                px = cx + math.cos(math.radians(angle)) * ring_r
                py = cy + math.sin(math.radians(angle)) * ring_r
                
                # 冰晶大小随收缩增大
                crystal_size = int(6 + progress * 8 - ring)
                if crystal_size > 0:
                    self._draw_ice_crystal(px, py, crystal_size, angle)
        
        # 中心积聚的能量球
        core_r = int(50 * progress)
        if core_r > 5:
            # 多层光晕
            for i in range(4):
                glow_r = core_r + i * 8
                glow_alpha = int((150 - i * 30) * progress)
                glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (150, 220, 255, glow_alpha), (glow_r, glow_r), glow_r)
                self.image.blit(glow_surf, (cx - glow_r, cy - glow_r))
            
            # 核心
            pygame.draw.circle(self.image, (220, 245, 255), (cx, cy), core_r)
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), max(5, core_r - 10))
        
        # 环境温度下降效果 - 屏幕边缘冰霜
        frost_alpha = int(80 * progress)
        if frost_alpha > 0:
            self._draw_screen_frost(frost_alpha)
    
    def _draw_ice_crystal(self, x, y, size, rotation):
        """绘制单个冰晶"""
        points = []
        for i in range(6):
            angle = rotation + i * 60
            length = size if i % 2 == 0 else size * 0.5
            px = x + math.cos(math.radians(angle)) * length
            py = y + math.sin(math.radians(angle)) * length
            points.append((int(px), int(py)))
        if len(points) >= 3:
            pygame.draw.polygon(self.image, (180, 230, 255, 200), points)
            pygame.draw.polygon(self.image, (220, 245, 255), points, 1)
    
    def _draw_screen_frost(self, alpha):
        """绘制屏幕边缘冰霜"""
        # 顶部
        for i in range(50):
            fx = random.randint(0, 540)
            fy = random.randint(0, 80)
            fsize = random.randint(3, 15)
            falpha = int(alpha * (1 - fy / 80))
            if falpha > 0:
                pygame.draw.circle(self.image, (200, 240, 255, falpha), (fx, fy), fsize)
        # 底部
        for i in range(50):
            fx = random.randint(0, 540)
            fy = random.randint(620, 700)
            fsize = random.randint(3, 15)
            falpha = int(alpha * ((fy - 620) / 80))
            if falpha > 0:
                pygame.draw.circle(self.image, (200, 240, 255, falpha), (fx, fy), fsize)
    
    def _draw_explosion(self):
        """绘制爆发效果 - 冰封扩散"""
        self.image.fill((0, 0, 0, 0))
        
        cx, cy = self.center_x, self.center_y
        
        # 主扩散冰环
        if self.effect_radius < self.max_radius:
            # 多层冰环
            for i in range(5):
                ring_r = self.effect_radius - i * 20
                if ring_r > 0:
                    ring_alpha = int(200 * (1 - self.effect_radius / self.max_radius) - i * 30)
                    if ring_alpha > 0:
                        # 冰蓝色环
                        pygame.draw.circle(self.image, (150, 220, 255, ring_alpha), (cx, cy), ring_r, 8 - i)
            
            # 冰封波纹
            for wave in range(3):
                wave_r = self.effect_radius - wave * 40
                if wave_r > 0:
                    wave_alpha = int(100 * (1 - self.effect_radius / self.max_radius))
                    surf = pygame.Surface((wave_r * 2, wave_r * 2), pygame.SRCALPHA)
                    pygame.draw.circle(surf, (200, 245, 255, wave_alpha), (wave_r, wave_r), wave_r, 3)
                    self.image.blit(surf, (cx - wave_r, cy - wave_r))
        
        # 飞散的冰晶碎片
        for shard in self.ice_shards:
            shard['y'] += shard['fall_speed']
            shard['x'] += shard['sway']
            shard['rotation'] += 2
            
            if shard['y'] > 720:
                shard['y'] = -20
                shard['x'] = random.randint(0, 540)
            
            self._draw_ice_crystal(shard['x'], shard['y'], shard['size'], shard['rotation'])
        
        # 冰冻地面效果
        ground_alpha = int(150 * (1 - self.effect_radius / self.max_radius / 2))
        if ground_alpha > 0:
            self._draw_screen_frost(ground_alpha)
    
    def update(self):
        """更新绝对零度"""
        self.frame += 1
        
        if self.phase == 0:  # 聚能阶段
            self._draw_charge()
            if self.frame >= self.charge_duration:
                self.phase = 1
                self.frame = 0
                self._apply_freeze()
        
        elif self.phase == 1:  # 爆发阶段
            self.effect_radius += 25
            self._draw_explosion()
            
            if self.effect_radius >= self.max_radius:
                self.phase = 2
                self.frame = 0
        
        elif self.phase == 2:  # 冰封持续阶段
            # 持续显示冰封效果
            self.image.fill((0, 0, 0, 0))
            fade = 1 - self.frame / 60
            if fade > 0:
                self._draw_screen_frost(int(100 * fade))
                # 继续飘落冰晶
                for shard in self.ice_shards[:20]:
                    shard['y'] += shard['fall_speed'] * 0.5
                    shard['rotation'] += 1
                    if shard['y'] < 720:
                        self._draw_ice_crystal(shard['x'], shard['y'], int(shard['size'] * fade), shard['rotation'])
            
            if self.frame >= 60:
                self.kill()
    
    def _apply_freeze(self):
        """应用冻结效果"""
        for enemy in mobs:
            # 造成伤害
            enemy.hp -= self.damage
            if hasattr(enemy, 'hit_flash'):
                enemy.hit_flash = 15
            
            # 冻结
            if not hasattr(enemy, 'frozen'):
                enemy.frozen = 0
            enemy.frozen = self.freeze_duration
