"""
幽影穿心·冥弦 - 专属子弹模块
亚音速标记弹，二次暴击

特性：
- 标记敌人
- 标记3秒内穿墙必暴
- 高伤害狙击
"""
import pygame
import math
import random
from config import all_sprites, mobs


class MarkShot(pygame.sprite.Sprite):
    """标记弹 - 亚音速穿透"""
    
    def __init__(self, x, y, damage, owner=None):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.piercing = 0  # 不穿透，但标记敌人
        self.color = (255, 50, 50)
        
        # 位置和速度
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed = 12  # 亚音速
        
        # 动画
        self.frame = 0
        
        # 创建图像
        self.size = 8
        self.trail_length = 40
        self.image = pygame.Surface((self.size + 10, self.trail_length + 20), pygame.SRCALPHA)
        self._draw_shot()
        self.rect = self.image.get_rect(center=(x, y))
        
        # 生命周期
        self.lifetime = 150
    
    def _draw_shot(self):
        """绘制标记弹"""
        self.image.fill((0, 0, 0, 0))
        cx = (self.size + 10) // 2
        cy = self.trail_length
        
        # 拖尾
        for i in range(8):
            ty = cy + i * 5
            alpha = 150 - i * 18
            trail_color = (80, 80, 100, alpha)
            tw = self.size - i
            if tw > 0:
                pygame.draw.circle(self.image, trail_color, (cx, ty), tw)
        
        # 弹体 - 哑光黑
        pygame.draw.circle(self.image, (40, 40, 50), (cx, cy), self.size)
        
        # 信标红核心
        core_pulse = int(3 + 2 * math.sin(self.frame * 0.3))
        pygame.draw.circle(self.image, (255, 50, 50), (cx, cy), core_pulse)
        
        # 外圈信标环
        ring_alpha = int(100 + 50 * math.sin(self.frame * 0.2))
        ring_surf = pygame.Surface((self.size * 2 + 4, self.size * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (255, 50, 50, ring_alpha), (self.size + 2, self.size + 2), self.size + 2, 2)
        self.image.blit(ring_surf, (cx - self.size - 2, cy - self.size - 2))
    
    def update(self):
        """更新标记弹"""
        self.frame += 1
        
        # 移动
        self.float_y -= self.speed
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 重绘
        self._draw_shot()
        
        # 生命周期
        self.lifetime -= 1
        if self.lifetime <= 0 or self.rect.bottom < 0:
            self.kill()
    
    def on_hit_enemy(self, enemy):
        """命中敌人 - 添加标记"""
        # 添加死亡标记
        if not hasattr(enemy, 'death_mark'):
            enemy.death_mark = 0
        enemy.death_mark = 180  # 3秒标记
        
        # 标记视觉效果
        mark = DeathMark(enemy)
        all_sprites.add(mark)
        
        return True


class DeathMark(pygame.sprite.Sprite):
    """死亡标记 - 视觉指示"""
    
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.duration = 180  # 3秒
        self.frame = 0
        
        # 创建图像
        self.size = 30
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self._draw_mark()
        self.rect = self.image.get_rect()
    
    def _draw_mark(self):
        """绘制标记"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size, self.size
        
        # 淡出效果
        remaining = self.duration - self.frame
        if remaining < 30:
            alpha_mult = remaining / 30
        else:
            alpha_mult = 1.0
        
        # 旋转角度
        rot = self.frame * 2
        
        # 外圈
        ring_alpha = int(150 * alpha_mult)
        pygame.draw.circle(self.image, (255, 50, 50, ring_alpha), (cx, cy), self.size, 3)
        
        # 十字准星
        cross_len = 12
        for i in range(4):
            angle = rot + i * 90
            x1 = cx + math.cos(math.radians(angle)) * 10
            y1 = cy + math.sin(math.radians(angle)) * 10
            x2 = cx + math.cos(math.radians(angle)) * (10 + cross_len)
            y2 = cy + math.sin(math.radians(angle)) * (10 + cross_len)
            pygame.draw.line(self.image, (255, 50, 50, ring_alpha), (x1, y1), (x2, y2), 2)
        
        # 中心点
        pulse = int(4 + 2 * math.sin(self.frame * 0.3))
        pygame.draw.circle(self.image, (255, 100, 100, int(200 * alpha_mult)), (cx, cy), pulse)
    
    def update(self):
        """更新标记"""
        self.frame += 1
        
        # 跟随目标
        if self.target and self.target.alive() and hasattr(self.target, 'rect'):
            self.rect.center = self.target.rect.center
            self._draw_mark()
        else:
            self.kill()
            return
        
        # 持续时间
        if self.frame >= self.duration:
            self.kill()


class DeathSniperUlt(pygame.sprite.Sprite):
    """绝杀狙击 - 大招"""
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 3
        
        # 寻找带标记的敌人
        self.targets = []
        for enemy in mobs:
            if hasattr(enemy, 'death_mark') and enemy.death_mark > 0:
                self.targets.append(enemy)
        
        # 如果没有标记目标，选择随机敌人
        if not self.targets:
            for enemy in list(mobs)[:3]:
                self.targets.append(enemy)
        
        # 狙击计数
        self.shots_fired = 0
        self.fire_interval = 20
        self.fire_timer = 0
        
        # 生命周期
        self.duration = len(self.targets) * self.fire_interval + 60
        self.frame = 0
        
        # 占位图像
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        all_sprites.add(self)
    
    def update(self):
        """更新大招"""
        self.frame += 1
        self.fire_timer += 1
        
        if self.shots_fired < len(self.targets) and self.fire_timer >= self.fire_interval:
            self.fire_timer = 0
            self._execute_target(self.targets[self.shots_fired])
            self.shots_fired += 1
        
        if self.frame >= self.duration:
            self.kill()
    
    def _execute_target(self, target):
        """处决目标"""
        if not target or not target.alive():
            return
        
        # 创建穿墙狙击线
        snipe = PiercingSnipe(self.owner, target, self.damage)
        all_sprites.add(snipe)


class PiercingSnipe(pygame.sprite.Sprite):
    """穿墙狙击线"""
    
    def __init__(self, owner, target, damage):
        super().__init__()
        self.owner = owner
        self.target = target
        self.damage = damage
        
        # 计算射线
        if owner and target:
            self.start_x = owner.rect.centerx
            self.start_y = owner.rect.centery
            self.end_x = target.rect.centerx
            self.end_y = target.rect.centery
        else:
            self.kill()
            return
        
        # 动画阶段
        self.phase = 0  # 0=瞄准线, 1=射击, 2=消散
        self.frame = 0
        self.phase_durations = [15, 5, 10]
        
        # 创建图像
        self.image = pygame.Surface((540, 800), pygame.SRCALPHA)
        self._draw_snipe()
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        self.damage_dealt = False
    
    def _draw_snipe(self):
        """绘制狙击线"""
        self.image.fill((0, 0, 0, 0))
        
        if self.phase == 0:
            # 瞄准线 - 虚线
            alpha = int(100 + 50 * math.sin(self.frame * 0.5))
            color = (255, 50, 50, alpha)
            
            # 画虚线
            dx = self.end_x - self.start_x
            dy = self.end_y - self.start_y
            dist = math.hypot(dx, dy)
            if dist > 0:
                steps = int(dist / 10)
                for i in range(0, steps, 2):
                    t = i / steps
                    x1 = self.start_x + dx * t
                    y1 = self.start_y + dy * t
                    t2 = min(1, (i + 1) / steps)
                    x2 = self.start_x + dx * t2
                    y2 = self.start_y + dy * t2
                    pygame.draw.line(self.image, color, (x1, y1), (x2, y2), 2)
        
        elif self.phase == 1:
            # 射击线 - 实线闪光
            pygame.draw.line(self.image, (255, 255, 255), 
                           (self.start_x, self.start_y), (self.end_x, self.end_y), 4)
            pygame.draw.line(self.image, (255, 100, 100), 
                           (self.start_x, self.start_y), (self.end_x, self.end_y), 2)
        
        elif self.phase == 2:
            # 消散
            alpha = int(255 * (1 - self.frame / self.phase_durations[2]))
            pygame.draw.line(self.image, (255, 100, 100, alpha), 
                           (self.start_x, self.start_y), (self.end_x, self.end_y), 2)
    
    def update(self):
        """更新狙击线"""
        self.frame += 1
        
        # 阶段转换
        if self.frame >= self.phase_durations[self.phase]:
            self.frame = 0
            self.phase += 1
            
            # 射击阶段造成伤害
            if self.phase == 1 and not self.damage_dealt:
                self.damage_dealt = True
                if self.target and self.target.alive():
                    # 必暴伤害
                    crit_damage = self.damage * 2
                    self.target.hp -= crit_damage
                    if hasattr(self.target, 'hit_flash'):
                        self.target.hit_flash = 10
        
        if self.phase >= 3:
            self.kill()
            return
        
        self._draw_snipe()


class FateEnder(pygame.sprite.Sprite):
    """命运终结 - 三技能 ★强化版★ 所有标记敌人立即死亡"""
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 10
        
        # 寻找所有带标记的敌人
        self.targets = []
        for enemy in mobs:
            if hasattr(enemy, 'death_mark') and enemy.death_mark > 0:
                self.targets.append(enemy)
        
        # 阶段
        self.phase = 0  # 0=命运之弦编织, 1=锁定, 2=处决, 3=结束
        self.frame = 0
        
        # 弦编织阶段
        self.weave_duration = 35
        
        # 锁定阶段
        self.lock_duration = 40
        
        # 处决阶段
        self.execute_index = 0
        self.execute_interval = 10
        self.execute_timer = 0
        
        # 命运之弦（连接所有目标的线）
        self.fate_strings = []
        self._generate_fate_strings()
        
        # 死亡符文
        self.death_runes = []
        for target in self.targets:
            self.death_runes.append({
                'target': target,
                'rotation': random.uniform(0, 360),
                'scale': 0,
                'alpha': 0
            })
        
        # 暗影粒子
        self.shadow_particles = []
        for _ in range(50):
            self.shadow_particles.append({
                'x': random.randint(0, 540),
                'y': random.randint(0, 700),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-2, 0),
                'size': random.randint(2, 6),
                'alpha': random.randint(50, 150)
            })
        
        # 屏幕暗化
        self.darkness = 0
        
        # 创建图像
        self.image = pygame.Surface((540, 700), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _generate_fate_strings(self):
        """生成命运之弦网络"""
        # 连接所有目标和玩家
        points = []
        if self.owner:
            points.append((self.owner.rect.centerx, self.owner.rect.centery))
        
        for target in self.targets:
            points.append((target.rect.centerx, target.rect.centery))
        
        # 创建全连接网络
        for i, p1 in enumerate(points):
            for j, p2 in enumerate(points):
                if i < j:
                    self.fate_strings.append({
                        'start': p1,
                        'end': p2,
                        'progress': 0,
                        'pulse': random.uniform(0, math.pi * 2)
                    })
    
    def _draw_weave(self):
        """绘制命运之弦编织"""
        self.image.fill((0, 0, 0, 0))
        
        progress = self.frame / self.weave_duration
        
        # 屏幕逐渐变暗
        self.darkness = int(80 * progress)
        dark_surf = pygame.Surface((540, 700), pygame.SRCALPHA)
        dark_surf.fill((0, 0, 0, self.darkness))
        self.image.blit(dark_surf, (0, 0))
        
        # 绘制命运之弦逐渐显现
        for string in self.fate_strings:
            string['progress'] = min(1.0, string['progress'] + 0.05)
            string['pulse'] += 0.1
            
            sx, sy = string['start']
            ex, ey = string['end']
            
            # 当前弦的终点（逐渐延伸）
            curr_ex = sx + (ex - sx) * string['progress']
            curr_ey = sy + (ey - sy) * string['progress']
            
            # 弦的脉动
            pulse_alpha = int(100 + 50 * math.sin(string['pulse']))
            
            # 多层弦
            for layer in range(3):
                layer_alpha = pulse_alpha - layer * 30
                layer_width = 3 - layer
                if layer_alpha > 0:
                    # 绘制曲线弦（贝塞尔曲线效果）
                    points = []
                    steps = 15
                    for t in range(steps + 1):
                        tt = t / steps
                        # 添加波动
                        wave = math.sin(tt * math.pi * 4 + self.frame * 0.2) * 5 * (1 - abs(tt - 0.5) * 2)
                        px = sx + (curr_ex - sx) * tt + wave * (-(ey - sy) / max(1, math.hypot(ex - sx, ey - sy)))
                        py = sy + (curr_ey - sy) * tt + wave * ((ex - sx) / max(1, math.hypot(ex - sx, ey - sy)))
                        points.append((int(px), int(py)))
                    
                    if len(points) > 1:
                        pygame.draw.lines(self.image, (100, 50, 80, layer_alpha), False, points, layer_width)
        
        # 暗影粒子
        self._update_shadow_particles()
    
    def _draw_lock(self):
        """绘制锁定效果 - 死亡符文"""
        self.image.fill((0, 0, 0, 0))
        
        progress = (self.frame - self.weave_duration) / self.lock_duration
        
        # 保持暗度
        dark_surf = pygame.Surface((540, 700), pygame.SRCALPHA)
        dark_surf.fill((0, 0, 0, 100))
        self.image.blit(dark_surf, (0, 0))
        
        # 绘制命运之弦（保持显示）
        for string in self.fate_strings:
            string['pulse'] += 0.15
            sx, sy = string['start']
            ex, ey = string['end']
            pulse_alpha = int(80 + 40 * math.sin(string['pulse']))
            pygame.draw.line(self.image, (150, 50, 80, pulse_alpha), (sx, sy), (ex, ey), 2)
        
        # 绘制死亡符文
        for rune in self.death_runes:
            target = rune['target']
            if not target.alive():
                continue
            
            tx, ty = target.rect.centerx, target.rect.centery
            rune['rotation'] += 2
            rune['scale'] = min(1.0, rune['scale'] + 0.04)
            rune['alpha'] = min(255, rune['alpha'] + 8)
            
            scale = rune['scale']
            alpha = rune['alpha']
            rot = rune['rotation']
            
            # 死亡符文 - 多层六芒星
            rune_r = int(50 * scale)
            
            # 外圈
            pygame.draw.circle(self.image, (100, 30, 50, alpha), (tx, ty), rune_r, 2)
            
            # 六芒星
            for star in range(2):
                points = []
                for i in range(6):
                    angle = rot + star * 30 + i * 60
                    px = tx + math.cos(math.radians(angle)) * (rune_r - 10)
                    py = ty + math.sin(math.radians(angle)) * (rune_r - 10)
                    points.append((px, py))
                
                if len(points) == 6:
                    # 连接形成六芒星
                    for i in range(6):
                        j = (i + 2) % 6
                        pygame.draw.line(self.image, (180, 50, 80, alpha), 
                                       (int(points[i][0]), int(points[i][1])),
                                       (int(points[j][0]), int(points[j][1])), 2)
            
            # 内圈符文
            inner_r = int(25 * scale)
            pygame.draw.circle(self.image, (200, 80, 100, alpha), (tx, ty), inner_r, 1)
            
            # 中心脉动核心
            core_pulse = int(8 + 4 * math.sin(self.frame * 0.3))
            pygame.draw.circle(self.image, (255, 100, 120, alpha), (tx, ty), core_pulse)
            pygame.draw.circle(self.image, (255, 200, 200, alpha), (tx, ty), core_pulse // 2)
            
            # 环绕的死亡文字效果（用小圆点代替）
            for i in range(12):
                text_angle = rot * 0.5 + i * 30
                text_r = rune_r + 8
                text_x = tx + math.cos(math.radians(text_angle)) * text_r
                text_y = ty + math.sin(math.radians(text_angle)) * text_r
                pygame.draw.circle(self.image, (180, 80, 100, alpha // 2), (int(text_x), int(text_y)), 2)
        
        # 暗影粒子
        self._update_shadow_particles()
    
    def _update_shadow_particles(self):
        """更新暗影粒子"""
        for p in self.shadow_particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['alpha'] = max(0, p['alpha'] - 1)
            
            # 绘制
            if p['alpha'] > 0:
                pygame.draw.circle(self.image, (50, 20, 40, p['alpha']), 
                                 (int(p['x']), int(p['y'])), p['size'])
            
            # 重生
            if p['y'] < -10 or p['alpha'] <= 0:
                p['y'] = 710
                p['x'] = random.randint(0, 540)
                p['alpha'] = random.randint(80, 150)
    
    def _draw_execute(self, target, exec_frame):
        """绘制处决效果 - 命运收割"""
        if not target.alive():
            return
        
        tx, ty = target.rect.centerx, target.rect.centery
        
        # 命运之弦收紧动画
        if self.owner:
            ox, oy = self.owner.rect.centerx, self.owner.rect.centery
            
            # 主收割线
            for width in range(5, 0, -1):
                line_alpha = 50 + width * 40
                pygame.draw.line(self.image, (255, 50, 80, line_alpha), (ox, oy), (tx, ty), width)
            
            # 沿线的能量脉冲
            dist = math.hypot(tx - ox, ty - oy)
            if dist > 0:
                pulse_pos = (exec_frame % 10) / 10
                pulse_x = ox + (tx - ox) * pulse_pos
                pulse_y = oy + (ty - oy) * pulse_pos
                pygame.draw.circle(self.image, (255, 150, 150), (int(pulse_x), int(pulse_y)), 8)
        
        # 从四角射来的暗影箭矢
        corners = [(0, 0), (540, 0), (0, 700), (540, 700)]
        for i, (cx, cy) in enumerate(corners):
            # 主箭矢
            for width in range(4, 0, -1):
                arrow_alpha = 100 + width * 30
                pygame.draw.line(self.image, (100, 30, 50, arrow_alpha), (cx, cy), (tx, ty), width)
            
            # 箭头效果
            angle = math.atan2(ty - cy, tx - cx)
            arrow_len = 20
            for j in range(3):
                pa = angle + math.pi + (j - 1) * 0.3
                px = tx + math.cos(pa) * arrow_len
                py = ty + math.sin(pa) * arrow_len
                pygame.draw.line(self.image, (180, 50, 80, 200), (tx, ty), (int(px), int(py)), 2)
        
        # 目标爆裂效果
        burst_r = exec_frame * 4
        for layer in range(5):
            ring_r = burst_r - layer * 8
            if ring_r > 0:
                ring_alpha = 200 - layer * 35 - exec_frame * 5
                if ring_alpha > 0:
                    pygame.draw.circle(self.image, (200, 50, 80, ring_alpha), (tx, ty), ring_r, 3)
        
        # 灵魂撕裂效果（向外扩散的线条）
        for i in range(16):
            soul_angle = i * 22.5 + exec_frame * 5
            soul_len = 30 + exec_frame * 3
            sx = tx + math.cos(math.radians(soul_angle)) * 10
            sy = ty + math.sin(math.radians(soul_angle)) * 10
            sex = tx + math.cos(math.radians(soul_angle)) * soul_len
            sey = ty + math.sin(math.radians(soul_angle)) * soul_len
            
            soul_alpha = 180 - exec_frame * 8
            if soul_alpha > 0:
                pygame.draw.line(self.image, (150, 80, 100, soul_alpha), 
                               (int(sx), int(sy)), (int(sex), int(sey)), 2)
        
        # 中心死亡符号
        pygame.draw.circle(self.image, (255, 50, 80), (tx, ty), 15)
        pygame.draw.circle(self.image, (50, 0, 20), (tx, ty), 10)
        # X标记
        pygame.draw.line(self.image, (255, 200, 200), (tx - 6, ty - 6), (tx + 6, ty + 6), 3)
        pygame.draw.line(self.image, (255, 200, 200), (tx - 6, ty + 6), (tx + 6, ty - 6), 3)
    
    def update(self):
        """更新命运终结"""
        self.frame += 1
        
        if self.phase == 0:  # 命运之弦编织
            self._draw_weave()
            if self.frame >= self.weave_duration:
                self.phase = 1
        
        elif self.phase == 1:  # 锁定阶段
            self._draw_lock()
            if self.frame >= self.weave_duration + self.lock_duration:
                self.phase = 2
                self.execute_timer = 0
        
        elif self.phase == 2:  # 处决阶段
            self.execute_timer += 1
            
            # 保持暗背景
            self.image.fill((0, 0, 0, 0))
            dark_surf = pygame.Surface((540, 700), pygame.SRCALPHA)
            dark_surf.fill((0, 0, 0, 80))
            self.image.blit(dark_surf, (0, 0))
            
            # 保持命运之弦
            for string in self.fate_strings:
                string['pulse'] += 0.2
                sx, sy = string['start']
                ex, ey = string['end']
                pulse_alpha = int(60 + 30 * math.sin(string['pulse']))
                pygame.draw.line(self.image, (120, 40, 60, pulse_alpha), (sx, sy), (ex, ey), 1)
            
            if self.execute_index < len(self.targets) and self.execute_timer >= self.execute_interval:
                self.execute_timer = 0
                target = self.targets[self.execute_index]
                self._draw_execute(target, 0)
                self._execute(target)
                self.execute_index += 1
            elif self.execute_timer < self.execute_interval and self.execute_index > 0:
                # 绘制当前处决动画
                if self.execute_index <= len(self.targets):
                    prev_target = self.targets[self.execute_index - 1]
                    self._draw_execute(prev_target, self.execute_timer)
            
            if self.execute_index >= len(self.targets) and self.execute_timer >= self.execute_interval:
                self.phase = 3
                self.kill()
    
    def _execute(self, target):
        """执行处决"""
        if not target or not target.alive():
            return
        
        # 造成巨额伤害（基本秒杀）
        target.hp -= self.damage
        
        # 清除标记
        if hasattr(target, 'death_mark'):
            target.death_mark = 0
        
        if hasattr(target, 'hit_flash'):
            target.hit_flash = 25
