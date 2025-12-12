"""
天幕虹裂·光谱 - 专属子弹模块
扇形彩虹光束，7道并行

特性：
- 7色彩虹光束
- 3道同点命中额外真伤
- 全息银视觉
"""
import pygame
import math
import random
from config import all_sprites, mobs


# 彩虹7色
RAINBOW_COLORS = [
    (255, 50, 50),    # 红
    (255, 150, 50),   # 橙
    (255, 255, 50),   # 黄
    (50, 255, 50),    # 绿
    (50, 200, 255),   # 青
    (100, 100, 255),  # 蓝
    (200, 50, 255),   # 紫
]


class RainbowBeam(pygame.sprite.Sprite):
    """彩虹光束 - 7道之一"""
    
    def __init__(self, x, y, angle, damage, color_index, owner=None):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.color_index = color_index
        self.color = RAINBOW_COLORS[color_index % 7]
        self.is_enemy = False
        self.piercing = 0  # 不穿透
        
        # 位置和速度
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed = 14
        self.angle = angle
        
        rad = math.radians(angle)
        self.vx = math.cos(rad) * self.speed
        self.vy = math.sin(rad) * self.speed
        
        # 动画
        self.frame = 0
        
        # 创建图像
        self.length = 30
        self.width = 6
        self.image = pygame.Surface((self.length + 20, self.width + 20), pygame.SRCALPHA)
        self._draw_beam()
        self.rect = self.image.get_rect(center=(x, y))
        
        # 生命周期
        self.lifetime = 90
    
    def _draw_beam(self):
        """绘制光束"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = (self.length + 20) // 2, (self.width + 20) // 2
        
        # 旋转绘制
        rad = math.radians(self.angle + 90)
        
        # 外层光晕
        glow_color = (*self.color, 80)
        glow_surf = pygame.Surface((self.length + 10, self.width + 10), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, glow_color, (0, 0, self.length + 10, self.width + 10))
        
        # 旋转
        rotated = pygame.transform.rotate(glow_surf, -self.angle - 90)
        self.image.blit(rotated, rotated.get_rect(center=(cx, cy)))
        
        # 核心光束
        beam_surf = pygame.Surface((self.length, self.width), pygame.SRCALPHA)
        pygame.draw.ellipse(beam_surf, self.color, (0, 0, self.length, self.width))
        
        # 中心亮点
        pygame.draw.ellipse(beam_surf, (255, 255, 255), (self.length // 2 - 3, self.width // 2 - 2, 6, 4))
        
        rotated_beam = pygame.transform.rotate(beam_surf, -self.angle - 90)
        self.image.blit(rotated_beam, rotated_beam.get_rect(center=(cx, cy)))
    
    def update(self):
        """更新光束"""
        self.frame += 1
        
        # 移动
        self.float_x += self.vx
        self.float_y += self.vy
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 重绘
        self._draw_beam()
        
        # 生命周期
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        
        # 边界检测
        if self.rect.right < 0 or self.rect.left > 540 or self.rect.bottom < 0 or self.rect.top > 800:
            self.kill()


class SpectrumStack:
    """光谱叠加计数器 - 用于追踪同点命中"""
    
    _enemy_hits = {}  # {enemy_id: {frame: [color_indices]}}
    _hit_window = 10  # 10帧内算同时命中
    
    @classmethod
    def register_hit(cls, enemy, color_index, frame):
        """记录命中"""
        eid = id(enemy)
        if eid not in cls._enemy_hits:
            cls._enemy_hits[eid] = {}
        
        # 清理过期记录
        expired = [f for f in cls._enemy_hits[eid] if frame - f > cls._hit_window]
        for f in expired:
            del cls._enemy_hits[eid][f]
        
        # 添加新记录
        if frame not in cls._enemy_hits[eid]:
            cls._enemy_hits[eid][frame] = []
        cls._enemy_hits[eid][frame].append(color_index)
        
        # 检查是否达到3色同中
        all_colors = set()
        for f, colors in cls._enemy_hits[eid].items():
            all_colors.update(colors)
        
        if len(all_colors) >= 3:
            # 触发真伤
            cls._enemy_hits[eid] = {}  # 重置
            return True
        
        return False


class SpectrumStackUlt(pygame.sprite.Sprite):
    """光谱叠加 - 大招"""
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 2
        
        # 持续发射彩虹扫射
        self.duration = 120  # 2秒
        self.frame = 0
        
        # 发射间隔
        self.fire_interval = 5
        self.fire_timer = 0
        
        # 旋转角度
        self.sweep_angle = -120
        self.sweep_dir = 1
        
        # 占位图像
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        all_sprites.add(self)
    
    def update(self):
        """更新大招"""
        self.frame += 1
        self.fire_timer += 1
        
        # 扫射角度变化 (-90是正上方)
        self.sweep_angle += self.sweep_dir * 3
        if self.sweep_angle > -60:
            self.sweep_dir = -1
        elif self.sweep_angle < -120:
            self.sweep_dir = 1
        
        # 发射彩虹光束
        if self.fire_timer >= self.fire_interval:
            self.fire_timer = 0
            self._fire_rainbow()
        
        if self.frame >= self.duration:
            self.kill()
    
    def _fire_rainbow(self):
        """发射7色光束"""
        if not self.owner or not self.owner.alive():
            self.kill()
            return
        
        from config import bullets
        
        cx, cy = self.owner.rect.centerx, self.owner.rect.top
        
        # 7道光束，向上发射
        for i in range(7):
            # 角度范围: sweep_angle 为中心，左右各3道
            angle = self.sweep_angle + (i - 3) * 8
            beam = RainbowBeam(cx, cy, angle, self.damage, i, self.owner)
            all_sprites.add(beam)
            bullets.add(beam)


class RainbowApocalypse(pygame.sprite.Sprite):
    """虹光终焉 - 三技能 ★强化版★ 全屏彩虹爆发"""
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 4
        
        # 阶段
        self.phase = 0  # 0=聚集, 1=棱镜形成, 2=爆发, 3=余波
        self.frame = 0
        
        # 聚集阶段
        self.gather_duration = 45
        
        # 棱镜形成
        self.prism_duration = 25
        
        # 爆发波数
        self.wave_count = 7
        self.waves_done = 0
        self.wave_interval = 8
        self.wave_timer = 0
        
        # 爆发半径
        self.explosion_radius = 0
        self.max_radius = 400
        
        # 中心位置
        self.center_x = 270
        self.center_y = 350
        
        # 彩虹粒子系统
        self.particles = []
        for _ in range(80):
            self.particles.append({
                'x': random.randint(0, 540),
                'y': random.randint(0, 700),
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-3, 3),
                'color': random.choice(RAINBOW_COLORS),
                'size': random.randint(3, 8),
                'life': random.randint(30, 90)
            })
        
        # 光柱
        self.light_pillars = []
        for i in range(7):
            angle = i * (360 / 7)
            self.light_pillars.append({
                'angle': angle,
                'height': 0,
                'color': RAINBOW_COLORS[i],
                'width': 20 + i * 3
            })
        
        # 创建图像
        self.image = pygame.Surface((540, 700), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _draw_gather(self):
        """绘制聚集效果 - 七彩旋涡"""
        self.image.fill((0, 0, 0, 0))
        
        progress = self.frame / self.gather_duration
        cx, cy = self.center_x, self.center_y
        
        # 背景彩虹渐变涡旋
        for layer in range(5):
            vortex_r = int(200 - layer * 30 - 80 * progress)
            if vortex_r > 0:
                vortex_surf = pygame.Surface((vortex_r * 2, vortex_r * 2), pygame.SRCALPHA)
                vortex_alpha = int(60 - layer * 10)
                # 渐变色环
                for i in range(36):
                    arc_angle = i * 10 + self.frame * (3 + layer)
                    color_idx = (i + self.frame) % 7
                    arc_color = (*RAINBOW_COLORS[color_idx], vortex_alpha)
                    start_rad = math.radians(arc_angle)
                    end_rad = math.radians(arc_angle + 10)
                    # 绘制弧段
                    points = []
                    for a in range(int(arc_angle), int(arc_angle + 12), 3):
                        ax = vortex_r + math.cos(math.radians(a)) * vortex_r
                        ay = vortex_r + math.sin(math.radians(a)) * vortex_r
                        points.append((ax, ay))
                    if len(points) > 1:
                        pygame.draw.lines(vortex_surf, arc_color, False, points, 3)
                self.image.blit(vortex_surf, (cx - vortex_r, cy - vortex_r))
        
        # 7色收缩螺旋
        for i, color in enumerate(RAINBOW_COLORS):
            spiral_angle = i * (360 / 7) + self.frame * 8
            dist = 180 * (1 - progress * 0.9)
            # 螺旋收缩
            spiral_dist = dist * (1 + 0.3 * math.sin(self.frame * 0.1 + i))
            px = cx + math.cos(math.radians(spiral_angle)) * spiral_dist
            py = cy + math.sin(math.radians(spiral_angle)) * spiral_dist
            
            # 光球 - 多层发光
            ball_r = int(18 + 12 * progress)
            for lr in range(4):
                br = ball_r + (3 - lr) * 5
                ba = 60 + lr * 40
                ball_surf = pygame.Surface((br * 2, br * 2), pygame.SRCALPHA)
                pygame.draw.circle(ball_surf, (*color, ba), (br, br), br)
                self.image.blit(ball_surf, (int(px) - br, int(py) - br))
            
            # 连接中心的能量线
            if progress > 0.3:
                line_alpha = int(150 * (progress - 0.3) / 0.7)
                points = [(int(px), int(py))]
                # 曲线连接
                for t in range(1, 6):
                    lt = t / 5
                    lx = px + (cx - px) * lt + math.sin(lt * math.pi * 3) * 20
                    ly = py + (cy - py) * lt
                    points.append((int(lx), int(ly)))
                if len(points) > 1:
                    pygame.draw.lines(self.image, (*color, line_alpha), False, points, 2)
            
            # 长拖尾
            for j in range(6):
                trail_angle = spiral_angle - j * 8
                trail_dist = dist + j * 25
                tx = cx + math.cos(math.radians(trail_angle)) * trail_dist
                ty = cy + math.sin(math.radians(trail_angle)) * trail_dist
                trail_r = ball_r - j * 2
                trail_alpha = 150 - j * 25
                if trail_r > 0 and trail_alpha > 0:
                    pygame.draw.circle(self.image, (*color, trail_alpha), (int(tx), int(ty)), trail_r)
        
        # 中心聚能核心
        core_pulse = int(20 + 10 * math.sin(self.frame * 0.3))
        core_alpha = int(100 + 100 * progress)
        for i in range(7):
            core_surf = pygame.Surface((core_pulse * 2 + 20, core_pulse * 2 + 20), pygame.SRCALPHA)
            pygame.draw.circle(core_surf, (*RAINBOW_COLORS[i], core_alpha // 7), 
                             (core_pulse + 10, core_pulse + 10), core_pulse + 10 - i * 2)
            self.image.blit(core_surf, (cx - core_pulse - 10, cy - core_pulse - 10))
    
    def _draw_prism(self):
        """绘制棱镜形成"""
        self.image.fill((0, 0, 0, 0))
        
        progress = (self.frame - self.gather_duration) / self.prism_duration
        cx, cy = self.center_x, self.center_y
        
        # 七边形棱镜
        prism_r = int(80 * progress)
        points = []
        for i in range(7):
            angle = i * (360 / 7) - 90
            px = cx + math.cos(math.radians(angle)) * prism_r
            py = cy + math.sin(math.radians(angle)) * prism_r
            points.append((px, py))
        
        if len(points) == 7:
            # 填充（半透明彩虹）
            for i in range(7):
                tri_points = [
                    (cx, cy),
                    points[i],
                    points[(i + 1) % 7]
                ]
                tri_surf = pygame.Surface((540, 700), pygame.SRCALPHA)
                pygame.draw.polygon(tri_surf, (*RAINBOW_COLORS[i], 100), tri_points)
                self.image.blit(tri_surf, (0, 0))
            
            # 边框
            for i in range(7):
                pygame.draw.line(self.image, (*RAINBOW_COLORS[i], 255), points[i], points[(i + 1) % 7], 3)
        
        # 光柱预备
        for pillar in self.light_pillars:
            pillar['height'] = int(300 * progress)
            angle = pillar['angle']
            px = cx + math.cos(math.radians(angle)) * (prism_r + 10)
            py = cy + math.sin(math.radians(angle)) * (prism_r + 10)
            
            # 从棱镜向外的光束
            end_x = px + math.cos(math.radians(angle)) * pillar['height']
            end_y = py + math.sin(math.radians(angle)) * pillar['height']
            
            for w in range(4):
                beam_alpha = 200 - w * 40
                beam_w = pillar['width'] - w * 4
                if beam_w > 0:
                    # 绘制渐变光束
                    pygame.draw.line(self.image, (*pillar['color'], beam_alpha), 
                                   (px, py), (end_x, end_y), beam_w)
    
    def _draw_explosion(self):
        """绘制爆发效果 - 彩虹冲击波"""
        self.image.fill((0, 0, 0, 0))
        
        cx, cy = self.center_x, self.center_y
        
        # 全屏彩虹闪光（爆发初期）
        if self.explosion_radius < 100:
            flash_alpha = int(150 * (1 - self.explosion_radius / 100))
            flash_surf = pygame.Surface((540, 700), pygame.SRCALPHA)
            # 彩虹渐变
            for y in range(700):
                color_idx = int((y / 100) % 7)
                color = RAINBOW_COLORS[color_idx]
                pygame.draw.line(flash_surf, (*color, flash_alpha), (0, y), (540, y), 1)
            self.image.blit(flash_surf, (0, 0))
        
        # 彩虹扩散环 - 多层
        for layer in range(3):
            layer_offset = layer * 30
            for i, color in enumerate(RAINBOW_COLORS):
                ring_r = self.explosion_radius - i * 12 - layer_offset
                if 0 < ring_r < 500:
                    ring_alpha = int((150 - layer * 40) * (1 - self.explosion_radius / self.max_radius))
                    if ring_alpha > 0:
                        ring_width = 8 - layer * 2
                        pygame.draw.circle(self.image, (*color, ring_alpha), (cx, cy), ring_r, ring_width)
        
        # 射线爆发
        ray_count = 14
        for i in range(ray_count):
            ray_angle = i * (360 / ray_count) + self.frame * 2
            color_idx = i % 7
            ray_length = self.explosion_radius * 1.2
            
            rx1 = cx + math.cos(math.radians(ray_angle)) * 30
            ry1 = cy + math.sin(math.radians(ray_angle)) * 30
            rx2 = cx + math.cos(math.radians(ray_angle)) * ray_length
            ry2 = cy + math.sin(math.radians(ray_angle)) * ray_length
            
            ray_alpha = int(180 * (1 - self.explosion_radius / self.max_radius))
            if ray_alpha > 0:
                pygame.draw.line(self.image, (*RAINBOW_COLORS[color_idx], ray_alpha), 
                               (rx1, ry1), (rx2, ry2), 3)
        
        # 更新和绘制粒子
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            
            if p['life'] > 0:
                p_alpha = int(200 * (p['life'] / 90))
                pygame.draw.circle(self.image, (*p['color'], p_alpha), (int(p['x']), int(p['y'])), p['size'])
            else:
                # 重生粒子
                p['x'] = cx + random.uniform(-50, 50)
                p['y'] = cy + random.uniform(-50, 50)
                angle = random.uniform(0, 360)
                speed = random.uniform(5, 12)
                p['vx'] = math.cos(math.radians(angle)) * speed
                p['vy'] = math.sin(math.radians(angle)) * speed
                p['life'] = random.randint(20, 50)
                p['color'] = RAINBOW_COLORS[self.waves_done % 7]
        
        # 受击敌人彩虹高亮
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - cx, enemy.rect.centery - cy)
            if abs(dist - self.explosion_radius) < 60:
                ex, ey = enemy.rect.centerx, enemy.rect.centery
                hit_color = RAINBOW_COLORS[self.waves_done % 7]
                for hr in range(3):
                    hit_r = 25 - hr * 6
                    hit_alpha = 150 - hr * 40
                    pygame.draw.circle(self.image, (*hit_color, hit_alpha), (ex, ey), hit_r)
    
    def update(self):
        """更新虹光终焉"""
        self.frame += 1
        
        if self.phase == 0:  # 聚集阶段
            self._draw_gather()
            if self.frame >= self.gather_duration:
                self.phase = 1
        
        elif self.phase == 1:  # 棱镜形成
            self._draw_prism()
            if self.frame >= self.gather_duration + self.prism_duration:
                self.phase = 2
                self.frame = self.gather_duration + self.prism_duration
                self._explode()
        
        elif self.phase == 2:  # 爆发阶段
            self.wave_timer += 1
            self.explosion_radius += 12
            self._draw_explosion()
            
            if self.wave_timer >= self.wave_interval:
                self.wave_timer = 0
                self._deal_wave_damage()
                self.waves_done += 1
            
            if self.explosion_radius >= self.max_radius:
                self.kill()
    
    def _explode(self):
        """初始爆发"""
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.center_x, enemy.rect.centery - self.center_y)
            if dist < 120:
                enemy.hp -= self.damage * 1.5
                if hasattr(enemy, 'hit_flash'):
                    enemy.hit_flash = 25
    
    def _deal_wave_damage(self):
        """扩散波伤害"""
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.center_x, enemy.rect.centery - self.center_y)
            if abs(dist - self.explosion_radius) < 60:
                enemy.hp -= self.damage * 0.5
                if hasattr(enemy, 'hit_flash'):
                    enemy.hit_flash = 10
