# -*- coding: utf-8 -*-
"""
棘刺藤骨·荆穹 - 专属子弹模块
骨蔓鞭射击，缠绕目标持续抽打

特性：
- 骨藤鞭弧线飞行
- 命中后缠绕目标2秒持续抽打
- 受击5次藤骨断裂生成次级短鞭
"""
import pygame
import math
import random
from config import all_sprites, mobs


class BoneWhip(pygame.sprite.Sprite):
    """骨蔓鞭 - 弧线飞行，命中缠绕"""
    
    def __init__(self, x, y, damage, owner=None, target=None):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.piercing = 0
        self.target = target
        
        # 颜色
        self.bone_color = (240, 235, 220)
        self.thorn_color = (180, 50, 50)
        
        # 位置
        self.float_x = float(x)
        self.float_y = float(y)
        self.start_x = float(x)
        self.start_y = float(y)
        
        # 寻找目标
        if not self.target:
            self._find_target()
        
        # 弧线参数
        self.progress = 0.0
        self.flight_time = 45  # 帧
        self.arc_offset = random.choice([-1, 1]) * random.randint(80, 120)
        
        # 鞭体段数
        self.segments = 8
        self.segment_positions = []
        
        # 动画
        self.frame = 0
        self.whip_wave = 0
        
        # 图像
        self.image = pygame.Surface((200, 200), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.lifetime = 120
    
    def _find_target(self):
        """寻找最近的敌人"""
        min_dist = float('inf')
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.float_x, 
                            enemy.rect.centery - self.float_y)
            if dist < min_dist:
                min_dist = dist
                self.target = enemy
    
    def _draw_whip(self):
        """绘制骨蔓鞭"""
        self.image.fill((0, 0, 0, 0))
        
        if len(self.segment_positions) < 2:
            return
        
        # 绘制鞭体
        for i in range(len(self.segment_positions) - 1):
            p1 = self.segment_positions[i]
            p2 = self.segment_positions[i + 1]
            
            # 转换到图像坐标
            img_p1 = (int(p1[0] - self.rect.left), int(p1[1] - self.rect.top))
            img_p2 = (int(p2[0] - self.rect.left), int(p2[1] - self.rect.top))
            
            # 骨节粗细渐变
            thickness = max(2, 6 - i)
            
            # 骨白主体
            pygame.draw.line(self.image, self.bone_color, img_p1, img_p2, thickness)
            
            # 棘刺
            if i % 2 == 0:
                mid_x = (img_p1[0] + img_p2[0]) // 2
                mid_y = (img_p1[1] + img_p2[1]) // 2
                
                # 计算垂直方向
                dx = img_p2[0] - img_p1[0]
                dy = img_p2[1] - img_p1[1]
                length = max(1, math.hypot(dx, dy))
                perp_x = -dy / length * 8
                perp_y = dx / length * 8
                
                # 棘刺
                thorn_alpha = 200 - i * 15
                pygame.draw.line(self.image, (*self.thorn_color, thorn_alpha),
                               (mid_x, mid_y), 
                               (int(mid_x + perp_x), int(mid_y + perp_y)), 2)
                pygame.draw.line(self.image, (*self.thorn_color, thorn_alpha),
                               (mid_x, mid_y), 
                               (int(mid_x - perp_x), int(mid_y - perp_y)), 2)
        
        # 鞭头
        if self.segment_positions:
            head = self.segment_positions[-1]
            head_img = (int(head[0] - self.rect.left), int(head[1] - self.rect.top))
            pygame.draw.circle(self.image, self.thorn_color, head_img, 5)
            pygame.draw.circle(self.image, self.bone_color, head_img, 3)
    
    def _calculate_arc_position(self, progress):
        """计算弧线位置"""
        if not self.target or not self.target.alive():
            return self.float_x, self.float_y - 10 * progress
        
        target_x = self.target.rect.centerx
        target_y = self.target.rect.centery
        
        # 线性插值
        x = self.start_x + (target_x - self.start_x) * progress
        y = self.start_y + (target_y - self.start_y) * progress
        
        # 弧线偏移（抛物线形状）
        arc = 4 * self.arc_offset * progress * (1 - progress)
        x += arc * 0.5
        
        return x, y
    
    def _update_segments(self):
        """更新鞭体各段位置"""
        self.segment_positions = []
        
        for i in range(self.segments):
            seg_progress = max(0, self.progress - i * 0.08)
            if seg_progress > 0:
                sx, sy = self._calculate_arc_position(min(1.0, seg_progress))
                # 波动效果
                wave = math.sin(self.whip_wave + i * 0.5) * 5
                sx += wave
                self.segment_positions.append((sx, sy))
    
    def update(self):
        """更新骨蔓鞭"""
        self.frame += 1
        self.whip_wave += 0.3
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 更新进度
        self.progress += 1.0 / self.flight_time
        
        # 更新鞭体
        self._update_segments()
        
        if self.segment_positions:
            head_x, head_y = self.segment_positions[-1]
            self.float_x = head_x
            self.float_y = head_y
            
            # 更新rect位置
            self.rect.center = (int(head_x), int(head_y))
        
        # 绘制
        self._draw_whip()
        
        # 命中检测
        if self.progress >= 0.9:
            self._check_hit()
    
    def _check_hit(self):
        """检测命中"""
        if self.target and self.target.alive():
            dist = math.hypot(self.float_x - self.target.rect.centerx,
                            self.float_y - self.target.rect.centery)
            if dist < 40:
                # 创建缠绕效果
                wrap = VineWrap(self.target, self.damage, self.owner)
                all_sprites.add(wrap)
                self.kill()


class VineWrap(pygame.sprite.Sprite):
    """藤蔓缠绕 - 持续抽打目标"""
    
    def __init__(self, target, damage, owner=None):
        super().__init__()
        self.target = target
        self.damage = damage
        self.owner = owner
        
        # 缠绕持续2秒
        self.duration = 120
        self.frame = 0
        
        # 抽打间隔0.3秒
        self.whip_interval = 18
        self.whip_timer = 0
        
        # 受击计数（用于分裂机制）
        self.hit_count = 0
        self.split_threshold = 5
        self.has_split = False
        
        # 藤蔓角度
        self.vine_angles = [random.uniform(0, 360) for _ in range(4)]
        
        # 图像
        self.size = 60
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        # 标记目标被缠绕
        if hasattr(target, 'is_wrapped'):
            target.is_wrapped = True
    
    def _draw_wrap(self):
        """绘制缠绕效果"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size, self.size
        
        # 淡出效果
        fade = min(1.0, (self.duration - self.frame) / 30) if self.frame > self.duration - 30 else 1.0
        
        # 缠绕藤蔓
        for i, angle in enumerate(self.vine_angles):
            # 旋转
            rot_angle = angle + self.frame * 2
            
            # 螺旋缠绕
            for j in range(8):
                t = j / 8
                r = 15 + j * 4
                a = rot_angle + j * 30
                vx = cx + math.cos(math.radians(a)) * r
                vy = cy + math.sin(math.radians(a)) * r
                
                # 藤蔓节点
                node_size = int((4 - j * 0.3) * fade)
                if node_size > 0:
                    pygame.draw.circle(self.image, (240, 235, 220, int(200 * fade)), 
                                     (int(vx), int(vy)), node_size)
                    
                    # 棘刺
                    if j % 2 == 0:
                        thorn_len = 5
                        thorn_angle = a + 90
                        tx = vx + math.cos(math.radians(thorn_angle)) * thorn_len
                        ty = vy + math.sin(math.radians(thorn_angle)) * thorn_len
                        pygame.draw.line(self.image, (180, 50, 50, int(200 * fade)),
                                       (int(vx), int(vy)), (int(tx), int(ty)), 2)
        
        # 抽打闪光
        if self.whip_timer < 5:
            flash_alpha = int(150 * (1 - self.whip_timer / 5))
            pygame.draw.circle(self.image, (255, 100, 100, flash_alpha), (cx, cy), 25)
    
    def update(self):
        """更新缠绕效果"""
        self.frame += 1
        self.whip_timer += 1
        
        # 检查目标
        if not self.target or not self.target.alive():
            self.kill()
            return
        
        # 跟随目标
        self.rect.center = self.target.rect.center
        
        # 抽打
        if self.whip_timer >= self.whip_interval:
            self.whip_timer = 0
            self._whip_attack()
        
        # 绘制
        self._draw_wrap()
        
        # 结束
        if self.frame >= self.duration:
            self._end_wrap()
    
    def _whip_attack(self):
        """抽打攻击"""
        if not self.target or not self.target.alive():
            return
        
        # 对目标造成伤害
        self.target.hp -= self.damage
        self.hit_count += 1
        
        if hasattr(self.target, 'hit_flash'):
            self.target.hit_flash = 8
        
        # 溅射伤害
        splash_range = 50
        splash_damage = self.damage * 0.3
        for enemy in mobs:
            if enemy != self.target:
                dist = math.hypot(enemy.rect.centerx - self.target.rect.centerx,
                                enemy.rect.centery - self.target.rect.centery)
                if dist < splash_range:
                    enemy.hp -= splash_damage
                    if hasattr(enemy, 'hit_flash'):
                        enemy.hit_flash = 5
        
        # 检查分裂
        if self.hit_count >= self.split_threshold and not self.has_split:
            self.has_split = True
            self._split_vines()
    
    def _split_vines(self):
        """藤骨断裂分裂"""
        # 生成2根次级短鞭
        for _ in range(2):
            # 寻找附近其他敌人
            nearby_enemies = []
            for enemy in mobs:
                if enemy != self.target and enemy.alive():
                    dist = math.hypot(enemy.rect.centerx - self.rect.centerx,
                                    enemy.rect.centery - self.rect.centery)
                    if dist < 300:
                        nearby_enemies.append(enemy)
            
            if nearby_enemies:
                target = random.choice(nearby_enemies)
                mini_whip = MiniWhip(self.rect.centerx, self.rect.centery, 
                                    self.damage * 0.6, self.owner, target)
                all_sprites.add(mini_whip)
    
    def _end_wrap(self):
        """结束缠绕"""
        if self.target and hasattr(self.target, 'is_wrapped'):
            self.target.is_wrapped = False
        self.kill()


class MiniWhip(pygame.sprite.Sprite):
    """次级短鞭 - 追踪攻击"""
    
    def __init__(self, x, y, damage, owner, target):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.target = target
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed = 8
        
        # 攻击次数
        self.attack_count = 0
        self.max_attacks = 3
        
        # 图像
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.frame = 0
        self.lifetime = 180
    
    def _draw(self):
        """绘制短鞭"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = 20, 20
        
        # 旋转的短鞭
        angle = self.frame * 10
        
        # 骨节
        for i in range(4):
            seg_angle = angle + i * 20
            dist = 5 + i * 4
            sx = cx + math.cos(math.radians(seg_angle)) * dist
            sy = cy + math.sin(math.radians(seg_angle)) * dist
            
            pygame.draw.circle(self.image, (240, 235, 220), (int(sx), int(sy)), 4 - i)
            
            # 棘刺
            if i == 3:
                pygame.draw.circle(self.image, (180, 50, 50), (int(sx), int(sy)), 3)
    
    def update(self):
        """更新短鞭"""
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0 or self.attack_count >= self.max_attacks:
            self.kill()
            return
        
        # 追踪目标
        if self.target and self.target.alive():
            dx = self.target.rect.centerx - self.float_x
            dy = self.target.rect.centery - self.float_y
            dist = math.hypot(dx, dy)
            
            if dist > 0:
                self.float_x += dx / dist * self.speed
                self.float_y += dy / dist * self.speed
            
            # 命中检测
            if dist < 25:
                self._attack()
        else:
            # 寻找新目标
            self._find_new_target()
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        self._draw()
    
    def _attack(self):
        """攻击目标"""
        if self.target and self.target.alive():
            self.target.hp -= self.damage
            if hasattr(self.target, 'hit_flash'):
                self.target.hit_flash = 8
            self.attack_count += 1
            
            # 寻找下一个目标
            self._find_new_target()
    
    def _find_new_target(self):
        """寻找新目标"""
        min_dist = float('inf')
        new_target = None
        
        for enemy in mobs:
            if enemy != self.target and enemy.alive():
                dist = math.hypot(enemy.rect.centerx - self.float_x,
                                enemy.rect.centery - self.float_y)
                if dist < min_dist:
                    min_dist = dist
                    new_target = enemy
        
        if new_target:
            self.target = new_target


class ThornStorm(pygame.sprite.Sprite):
    """荆棘风暴 - 大招：释放大量骨蔓鞭覆盖全场"""
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 3
        
        # 释放波数
        self.wave_count = 5
        self.waves_done = 0
        self.wave_interval = 20
        self.wave_timer = 0
        
        # 每波鞭数
        self.whips_per_wave = 8
        
        # 阶段
        self.phase = 0  # 0=蓄力, 1=释放
        self.charge_duration = 30
        self.frame = 0
        
        # 图像
        self.image = pygame.Surface((540, 700), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _draw_charge(self):
        """绘制蓄力效果"""
        self.image.fill((0, 0, 0, 0))
        
        progress = self.frame / self.charge_duration
        cx, cy = self.owner.rect.centerx, self.owner.rect.centery
        
        # 藤蔓聚集
        for i in range(12):
            angle = i * 30 + self.frame * 3
            dist = 150 * (1 - progress)
            vx = cx + math.cos(math.radians(angle)) * dist
            vy = cy + math.sin(math.radians(angle)) * dist
            
            # 藤蔓线
            for j in range(5):
                t = j / 5
                px = vx + (cx - vx) * t
                py = vy + (cy - vy) * t
                size = int(4 * (1 - t) * progress)
                if size > 0:
                    pygame.draw.circle(self.image, (240, 235, 220, int(200 * progress)),
                                     (int(px), int(py)), size)
        
        # 中心光环
        ring_r = int(30 * progress)
        pygame.draw.circle(self.image, (180, 50, 50, int(150 * progress)), (cx, cy), ring_r, 3)
    
    def _spawn_wave(self):
        """释放一波骨蔓鞭"""
        from config import bullets
        
        for i in range(self.whips_per_wave):
            # 随机目标
            if mobs:
                target = random.choice(list(mobs))
            else:
                target = None
            
            # 从玩家周围不同角度发射
            angle = i * (360 / self.whips_per_wave) + self.waves_done * 20
            spawn_dist = 30
            spawn_x = self.owner.rect.centerx + math.cos(math.radians(angle)) * spawn_dist
            spawn_y = self.owner.rect.centery + math.sin(math.radians(angle)) * spawn_dist
            
            whip = BoneWhip(spawn_x, spawn_y, self.damage, self.owner, target)
            all_sprites.add(whip)
            bullets.add(whip)
    
    def update(self):
        """更新荆棘风暴"""
        self.frame += 1
        
        if self.phase == 0:  # 蓄力
            self._draw_charge()
            if self.frame >= self.charge_duration:
                self.phase = 1
                self.frame = 0
        
        elif self.phase == 1:  # 释放
            self.wave_timer += 1
            self.image.fill((0, 0, 0, 0))
            
            if self.waves_done < self.wave_count and self.wave_timer >= self.wave_interval:
                self.wave_timer = 0
                self._spawn_wave()
                self.waves_done += 1
            
            if self.waves_done >= self.wave_count:
                self.kill()


# ==============================================================================
#   子弹预览渲染函数
# ==============================================================================

def render_thornvine_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Thornvine子弹涂装预览效果 - 骨蔓鞭特效
    
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
    
    # 检查是否是Thornvine子弹涂装
    thornvine_effects = [
        "vine_wrap", "blood_drain", "poison_dot",
        "frost_slow", "burn_soul", "void_devour"
    ]
    
    matched_effect = None
    for effect in thornvine_effects:
        if effect in effects:
            matched_effect = effect
            break
    
    if not matched_effect:
        return False
    
    # 根据效果类型绘制不同的预览
    whip_length = size // 2
    wave = math.sin(t * 4) * 5  # 鞭体波动
    
    if matched_effect == "vine_wrap":
        # 骨蔓之鞭 - 骨白色弯曲藤蔓
        _draw_thornvine_whip(surface, center_x, center_y, whip_length, wave, 
                            (200, 180, 150), (240, 235, 220), t)
    elif matched_effect == "blood_drain":
        # 血棘之鞭 - 血红色荆棘
        _draw_thornvine_whip(surface, center_x, center_y, whip_length, wave,
                            (150, 30, 40), (200, 50, 60), t)
        # 血滴效果
        for i in range(3):
            drop_y = center_y + int(size//4 + (t * 50 + i * 30) % 20)
            drop_x = center_x + int(math.sin(t * 2 + i) * 10)
            pygame.draw.circle(surface, (180, 30, 30), (drop_x, drop_y), 3)
    elif matched_effect == "poison_dot":
        # 毒蔓之鞭 - 绿色剧毒
        _draw_thornvine_whip(surface, center_x, center_y, whip_length, wave,
                            (50, 150, 50), (80, 180, 60), t)
        # 毒雾效果
        for i in range(5):
            angle = t * 2 + i * 72
            dist = size // 3 + math.sin(t * 3 + i) * 5
            px = center_x + int(math.cos(math.radians(angle)) * dist)
            py = center_y + int(math.sin(math.radians(angle)) * dist)
            pygame.draw.circle(surface, (50, 180, 50, 100), (px, py), 4)
    elif matched_effect == "frost_slow":
        # 霜骨寒鞭 - 冰蓝色霜冻
        _draw_thornvine_whip(surface, center_x, center_y, whip_length, wave,
                            (180, 220, 250), (200, 240, 255), t)
        # 冰晶效果
        for i in range(4):
            angle = i * 90 + t * 30
            dist = size // 3
            px = center_x + int(math.cos(math.radians(angle)) * dist)
            py = center_y + int(math.sin(math.radians(angle)) * dist)
            _draw_ice_crystal(surface, px, py, 6)
    elif matched_effect == "burn_soul":
        # 炼狱棘鞭 - 橙红火焰
        _draw_thornvine_whip(surface, center_x, center_y, whip_length, wave,
                            (255, 100, 30), (255, 150, 50), t)
        # 火焰效果
        for i in range(6):
            flame_x = center_x + random.randint(-size//4, size//4)
            flame_y = center_y + random.randint(-size//4, size//4)
            flame_size = random.randint(3, 6)
            pygame.draw.circle(surface, (255, 150, 50), (flame_x, flame_y), flame_size)
    elif matched_effect == "void_devour":
        # 虚空藤骨 - 暗紫虚空
        _draw_thornvine_whip(surface, center_x, center_y, whip_length, wave,
                            (60, 40, 80), (100, 80, 150), t)
        # 虚空漩涡
        for i in range(3):
            angle = t * 100 + i * 120
            dist = size // 4 + i * 3
            px = center_x + int(math.cos(math.radians(angle)) * dist)
            py = center_y + int(math.sin(math.radians(angle)) * dist)
            pygame.draw.circle(surface, (100, 80, 150), (px, py), 4 - i)
    
    return True


def _draw_thornvine_whip(surface, cx, cy, length, wave, color, tip_color, t):
    """绘制骨蔓鞭形状"""
    # 鞭体曲线
    points = []
    segments = 8
    for i in range(segments + 1):
        progress = i / segments
        # S形曲线
        px = cx + int(progress * length * 0.3)
        py = cy - int(progress * length) + int(math.sin(progress * math.pi * 2 + t * 4) * wave * progress)
        points.append((px, py))
    
    # 绘制鞭体
    if len(points) >= 2:
        pygame.draw.lines(surface, color, False, points, 4)
        pygame.draw.lines(surface, tip_color, False, points, 2)
    
    # 绘制棘刺
    for i, (px, py) in enumerate(points[1:-1], 1):
        if i % 2 == 0:
            # 左右交替棘刺
            side = 1 if i % 4 == 0 else -1
            thorn_x = px + side * 8
            thorn_y = py
            pygame.draw.line(surface, (180, 50, 50), (px, py), (thorn_x, thorn_y), 2)
    
    # 鞭尾尖端
    if points:
        end_x, end_y = points[-1]
        pygame.draw.circle(surface, tip_color, (end_x, end_y), 5)
        pygame.draw.circle(surface, color, (end_x, end_y), 3)


def _draw_ice_crystal(surface, x, y, size):
    """绘制小冰晶"""
    for i in range(6):
        angle = i * 60
        ex = x + int(math.cos(math.radians(angle)) * size)
        ey = y + int(math.sin(math.radians(angle)) * size)
        pygame.draw.line(surface, (200, 240, 255), (x, y), (ex, ey), 1)
