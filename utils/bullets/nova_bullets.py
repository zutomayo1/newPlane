"""
苍穹轨断·诺娃 - 专属子弹模块
电磁轨道弹，无衰减贯穿全屏

特性：
- 蓄力机制
- 无限穿透
- 穿盾暴击
"""
import pygame
import math
import random
from config import all_sprites, mobs, get_key_binding_manager


class RailgunBullet(pygame.sprite.Sprite):
    """电磁轨道弹 - 贯穿全屏"""
    
    def __init__(self, x, y, damage, owner=None, charged=False):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.charged = charged  # 是否蓄力射击
        self.is_enemy = False
        self.color = (200, 220, 255)
        
        # 无限穿透
        self.piercing = 999
        self.hit_enemies = set()
        
        # 位置和速度
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed = 35  # 极高速
        
        # 蓄力加成
        if charged:
            self.damage *= 2.5
            self.crit = True
        else:
            self.crit = False
        
        # 动画
        self.frame = 0
        
        # 创建图像
        self.width = 6 if not charged else 12
        self.height = 80 if not charged else 120
        self.image = pygame.Surface((self.width + 30, self.height), pygame.SRCALPHA)
        self._draw_railgun()
        self.rect = self.image.get_rect(center=(x, y))
    
    def _draw_railgun(self):
        """绘制轨道弹"""
        self.image.fill((0, 0, 0, 0))
        cx = (self.width + 30) // 2
        
        # 电磁场光晕
        glow_width = self.width + 20
        for i in range(3):
            w = glow_width - i * 5
            alpha = 80 - i * 20
            if self.charged:
                color = (100, 150, 255, alpha)
            else:
                color = (150, 180, 255, alpha)
            surf = pygame.Surface((w, self.height), pygame.SRCALPHA)
            surf.fill(color)
            self.image.blit(surf, (cx - w // 2, 0))
        
        # 核心弹体
        if self.charged:
            core_color = (200, 220, 255)
        else:
            core_color = (220, 230, 255)
        pygame.draw.rect(self.image, core_color, (cx - self.width // 2, 0, self.width, self.height))
        
        # 中心亮线
        pygame.draw.rect(self.image, (255, 255, 255), (cx - 1, 0, 2, self.height))
        
        # 电弧效果
        if self.charged:
            for _ in range(4):
                start_y = random.randint(10, self.height - 10)
                end_y = start_y + random.randint(-20, 20)
                start_x = cx + random.choice([-1, 1]) * (self.width // 2)
                end_x = start_x + random.choice([-1, 1]) * random.randint(5, 15)
                pygame.draw.line(self.image, (150, 200, 255), (start_x, start_y), (end_x, end_y), 1)
    
    def update(self):
        """更新轨道弹"""
        self.frame += 1
        
        # 极速移动
        self.float_y -= self.speed
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 重绘
        self._draw_railgun()
        
        # 出屏销毁
        if self.rect.bottom < 0:
            self.kill()
    
    def on_hit_enemy(self, enemy):
        """命中敌人 - 无限穿透"""
        if id(enemy) in self.hit_enemies:
            return False
        
        self.hit_enemies.add(id(enemy))
        
        # 蓄力弹穿盾
        if self.charged and hasattr(enemy, 'shield'):
            enemy.shield = 0
        
        return True


class ChargeIndicator(pygame.sprite.Sprite):
    """蓄力指示器"""
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.charge_time = 0
        self.max_charge = 60  # 1秒蓄力
        self.fully_charged = False
        
        # 创建图像
        self.image = pygame.Surface((60, 10), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
    
    def _draw_bar(self):
        """绘制蓄力条"""
        self.image.fill((0, 0, 0, 0))
        
        # 背景
        pygame.draw.rect(self.image, (50, 50, 80, 150), (0, 0, 60, 10), border_radius=3)
        
        # 进度
        progress = min(1.0, self.charge_time / self.max_charge)
        bar_width = int(56 * progress)
        
        if progress >= 1.0:
            bar_color = (100, 200, 255)  # 满蓄力
        else:
            bar_color = (150, 180, 220)
        
        if bar_width > 0:
            pygame.draw.rect(self.image, bar_color, (2, 2, bar_width, 6), border_radius=2)
        
        # 满蓄力闪烁
        if progress >= 1.0:
            flash = int(128 + 127 * math.sin(self.charge_time * 0.2))
            pygame.draw.rect(self.image, (flash, flash, 255, 100), (0, 0, 60, 10), border_radius=3)
    
    def update(self):
        """更新蓄力"""
        if self.owner and self.owner.alive():
            self.rect.midbottom = (self.owner.rect.centerx, self.owner.rect.top - 5)
            
            # 检查是否在蓄力（按住射击键）
            keys = pygame.key.get_pressed()
            kb = get_key_binding_manager()
            if kb.is_action_pressed(keys, "shoot"):
                self.charge_time += 1
                if self.charge_time >= self.max_charge:
                    self.fully_charged = True
            else:
                if self.charge_time > 0:
                    # 松开时射击
                    self._fire()
                self.charge_time = 0
                self.fully_charged = False
            
            self._draw_bar()
        else:
            self.kill()
    
    def _fire(self):
        """发射轨道弹"""
        if not self.owner:
            return
        
        from config import bullets
        
        charged = self.fully_charged
        bullet = RailgunBullet(
            self.owner.rect.centerx,
            self.owner.rect.top,
            self.owner.damage,
            self.owner,
            charged=charged
        )
        all_sprites.add(bullet)
        bullets.add(bullet)


class ChargePierceUlt(pygame.sprite.Sprite):
    """充能击穿 - 大招"""
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 5
        
        # 发射3道超级轨道弹
        self.shots_fired = 0
        self.max_shots = 3
        self.fire_interval = 15
        self.fire_timer = 0
        
        # 生命周期
        self.duration = self.max_shots * self.fire_interval + 30
        self.frame = 0
        
        # 占位图像
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        all_sprites.add(self)
    
    def update(self):
        """更新大招"""
        self.frame += 1
        self.fire_timer += 1
        
        if self.shots_fired < self.max_shots and self.fire_timer >= self.fire_interval:
            self.fire_timer = 0
            self._fire_super_rail()
            self.shots_fired += 1
        
        if self.frame >= self.duration:
            self.kill()
    
    def _fire_super_rail(self):
        """发射超级轨道弹"""
        if not self.owner or not self.owner.alive():
            return
        
        from config import bullets
        
        # 中间一发 + 两侧各一发
        offsets = [0, -40, 40]
        offset = offsets[self.shots_fired] if self.shots_fired < len(offsets) else 0
        
        bullet = RailgunBullet(
            self.owner.rect.centerx + offset,
            self.owner.rect.top,
            self.damage,
            self.owner,
            charged=True
        )
        all_sprites.add(bullet)
        bullets.add(bullet)


class OrbitalStrike(pygame.sprite.Sprite):
    """轨道炮击 - 三技能 ★强化版★ 召唤卫星轨道炮轰炸"""
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 6
        
        # 轰炸次数
        self.strike_count = 7
        self.strikes_done = 0
        self.strike_interval = 15
        self.strike_timer = 0
        
        # 预警位置
        self.targets = []
        self._generate_targets()
        
        # 阶段
        self.phase = 0  # 0=卫星展开, 1=预警, 2=轰炸
        self.satellite_deploy = 30
        self.warning_duration = 50
        self.frame = 0
        
        # 卫星位置（屏幕顶部）
        self.satellites = []
        for i in range(5):
            self.satellites.append({
                'x': 54 + i * 108,
                'y': -50,
                'target_y': 30,
                'charge': 0
            })
        
        # 活跃的光束
        self.active_beams = []
        
        # 电磁干扰效果
        self.interference_lines = []
        
        # 创建图像
        self.image = pygame.Surface((540, 700), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _generate_targets(self):
        """生成轰炸目标"""
        for enemy in list(mobs)[:self.strike_count]:
            self.targets.append((enemy.rect.centerx, enemy.rect.centery))
        
        # 补足随机位置
        while len(self.targets) < self.strike_count:
            self.targets.append((random.randint(50, 490), random.randint(100, 500)))
    
    def _draw_satellite(self, sat, charging=False):
        """绘制单个卫星"""
        x, y = sat['x'], sat['y']
        
        # 卫星主体
        body_color = (100, 120, 150)
        pygame.draw.rect(self.image, body_color, (x - 15, y - 8, 30, 16))
        
        # 太阳能板
        panel_color = (60, 80, 120)
        pygame.draw.rect(self.image, panel_color, (x - 35, y - 5, 18, 10))
        pygame.draw.rect(self.image, panel_color, (x + 17, y - 5, 18, 10))
        # 太阳能板格线
        for i in range(3):
            pygame.draw.line(self.image, (80, 100, 140), (x - 35 + i * 6, y - 5), (x - 35 + i * 6, y + 5), 1)
            pygame.draw.line(self.image, (80, 100, 140), (x + 17 + i * 6, y - 5), (x + 17 + i * 6, y + 5), 1)
        
        # 蓄能指示灯
        if charging:
            charge_pulse = int(128 + 127 * math.sin(self.frame * 0.3))
            pygame.draw.circle(self.image, (charge_pulse, 150, 255), (x, y), 5)
            # 蓄能光环
            for i in range(3):
                ring_r = 10 + i * 5 + int(math.sin(self.frame * 0.2 + i) * 3)
                ring_alpha = 150 - i * 40
                pygame.draw.circle(self.image, (100, 150, 255, ring_alpha), (x, y), ring_r, 1)
        else:
            pygame.draw.circle(self.image, (50, 80, 120), (x, y), 4)
    
    def _draw_warning(self):
        """绘制预警效果 - 高科技风格"""
        self.image.fill((0, 0, 0, 0))
        
        # 绘制卫星
        for sat in self.satellites:
            self._draw_satellite(sat, charging=True)
        
        progress = (self.frame - self.satellite_deploy) / self.warning_duration
        
        for idx, (tx, ty) in enumerate(self.targets):
            # 目标锁定框
            box_size = int(80 * (1 - progress * 0.3))
            box_alpha = int(200 * (0.5 + 0.5 * math.sin(self.frame * 0.3)))
            
            # 四角L形
            corner_len = 15
            corners = [
                (tx - box_size // 2, ty - box_size // 2),
                (tx + box_size // 2, ty - box_size // 2),
                (tx - box_size // 2, ty + box_size // 2),
                (tx + box_size // 2, ty + box_size // 2)
            ]
            
            for i, (cx, cy) in enumerate(corners):
                dx = 1 if i % 2 else -1
                dy = 1 if i >= 2 else -1
                pygame.draw.line(self.image, (100, 150, 255, box_alpha), (cx, cy), (cx + dx * corner_len, cy), 2)
                pygame.draw.line(self.image, (100, 150, 255, box_alpha), (cx, cy), (cx, cy + dy * corner_len), 2)
            
            # 旋转的瞄准环
            ring_r = int(40 - 10 * progress)
            for i in range(8):
                angle = self.frame * 3 + i * 45
                arc_start = math.radians(angle)
                arc_end = math.radians(angle + 30)
                # 绘制弧段
                for a in range(int(arc_start * 180 / math.pi), int(arc_end * 180 / math.pi), 5):
                    ax = tx + math.cos(math.radians(a)) * ring_r
                    ay = ty + math.sin(math.radians(a)) * ring_r
                    pygame.draw.circle(self.image, (100, 180, 255, box_alpha), (int(ax), int(ay)), 2)
            
            # 中心十字
            cross_size = 10
            pygame.draw.line(self.image, (255, 100, 100), (tx - cross_size, ty), (tx + cross_size, ty), 2)
            pygame.draw.line(self.image, (255, 100, 100), (tx, ty - cross_size), (tx, ty + cross_size), 2)
            
            # 连接卫星的预瞄线（虚线）
            sat_idx = idx % len(self.satellites)
            sat = self.satellites[sat_idx]
            if progress > 0.5:
                line_alpha = int(150 * (progress - 0.5) * 2)
                for i in range(0, int(ty - sat['y']), 20):
                    pygame.draw.line(self.image, (100, 150, 255, line_alpha), 
                                   (sat['x'], sat['y'] + i), (sat['x'], sat['y'] + i + 10), 1)
    
    def _draw_strike(self, tx, ty, sat_x):
        """绘制单次轰炸 - 卫星激光"""
        # 主光束
        beam_width = 40
        
        # 外层光晕
        for i in range(4):
            bw = beam_width + 20 - i * 8
            alpha = 80 - i * 15
            pygame.draw.rect(self.image, (100, 150, 255, alpha), (sat_x - bw // 2, 40, bw, ty - 40))
        
        # 核心光束
        pygame.draw.rect(self.image, (150, 200, 255), (sat_x - beam_width // 2, 40, beam_width, ty - 40))
        pygame.draw.rect(self.image, (220, 240, 255), (sat_x - 8, 40, 16, ty - 40))
        pygame.draw.rect(self.image, (255, 255, 255), (sat_x - 3, 40, 6, ty - 40))
        
        # 击中点爆炸
        for layer in range(5):
            exp_r = 60 - layer * 10
            exp_alpha = 200 - layer * 35
            if exp_r > 0:
                exp_surf = pygame.Surface((exp_r * 2, exp_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(exp_surf, (150, 200, 255, exp_alpha), (exp_r, exp_r), exp_r)
                self.image.blit(exp_surf, (tx - exp_r, ty - exp_r))
        
        # 电弧四散
        for i in range(12):
            angle = random.uniform(0, 360)
            length = random.randint(30, 70)
            ex = tx + math.cos(math.radians(angle)) * length
            ey = ty + math.sin(math.radians(angle)) * length
            
            # 闪电路径
            points = [(tx, ty)]
            curr_x, curr_y = tx, ty
            steps = random.randint(3, 5)
            for j in range(steps):
                t = (j + 1) / steps
                next_x = tx + (ex - tx) * t + random.randint(-15, 15)
                next_y = ty + (ey - ty) * t + random.randint(-15, 15)
                points.append((next_x, next_y))
            
            if len(points) > 1:
                pygame.draw.lines(self.image, (180, 220, 255), False, points, 2)
        
        # 地面裂纹
        for i in range(8):
            crack_angle = i * 45
            crack_len = random.randint(30, 60)
            cx = tx + math.cos(math.radians(crack_angle)) * crack_len
            cy = ty + math.sin(math.radians(crack_angle)) * crack_len
            pygame.draw.line(self.image, (80, 120, 180), (tx, ty), (int(cx), int(cy)), 2)
    
    def update(self):
        """更新轨道炮击"""
        self.frame += 1
        
        if self.phase == 0:  # 卫星展开阶段
            self.image.fill((0, 0, 0, 0))
            
            # 卫星下降动画
            for sat in self.satellites:
                if sat['y'] < sat['target_y']:
                    sat['y'] += 3
                self._draw_satellite(sat)
            
            if self.frame >= self.satellite_deploy:
                self.phase = 1
                self.frame = self.satellite_deploy
        
        elif self.phase == 1:  # 预警阶段
            self._draw_warning()
            if self.frame >= self.satellite_deploy + self.warning_duration:
                self.phase = 2
                self.frame = 0
        
        elif self.phase == 2:  # 轰炸阶段
            self.strike_timer += 1
            self.image.fill((0, 0, 0, 0))
            
            # 绘制卫星
            for sat in self.satellites:
                self._draw_satellite(sat)
            
            if self.strikes_done < len(self.targets) and self.strike_timer >= self.strike_interval:
                self.strike_timer = 0
                tx, ty = self.targets[self.strikes_done]
                sat_x = self.satellites[self.strikes_done % len(self.satellites)]['x']
                self._draw_strike(tx, ty, sat_x)
                self._deal_damage(tx, ty)
                self.strikes_done += 1
            
            if self.strikes_done >= len(self.targets):
                self.kill()
    
    def _deal_damage(self, tx, ty):
        """对目标区域造成伤害"""
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - tx, enemy.rect.centery - ty)
            if dist < 80:
                enemy.hp -= self.damage
                if hasattr(enemy, 'hit_flash'):
                    enemy.hit_flash = 15
                # 穿盾
                if hasattr(enemy, 'shield'):
                    enemy.shield = 0
