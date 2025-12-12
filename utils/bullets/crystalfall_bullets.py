# -*- coding: utf-8 -*-
"""
晶簇射流·晶瀑 - 专属子弹模块
晶簇扇喷，落地成柱，连锁成墙

特性：
- 扇形喷射晶簇箭雨
- 落地竖立成晶柱持续穿刺
- 2柱间距<200px自动连接成水晶墙
"""
import pygame
import math
import random
from config import all_sprites, mobs


# 全局晶柱管理
active_pillars = []


class CrystalArrow(pygame.sprite.Sprite):
    """晶簇箭 - 扇形发射，落地成柱"""
    
    def __init__(self, x, y, angle, damage, owner=None):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.piercing = 0
        self.angle = angle
        
        # 颜色
        self.crystal_color = (180, 120, 220)  # 水晶紫
        self.rock_color = (100, 150, 180)     # 岩青
        
        # 位置
        self.float_x = float(x)
        self.float_y = float(y)
        self.start_x = float(x)
        self.start_y = float(y)
        
        # 速度
        self.speed = 12
        rad = math.radians(angle)
        self.vx = math.cos(rad) * self.speed
        self.vy = math.sin(rad) * self.speed
        
        # 重力
        self.gravity = 0.25
        
        # 旋转
        self.rotation = angle
        
        # 图像
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.frame = 0
        self.lifetime = 120
    
    def _draw(self):
        """绘制晶簇箭"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = 20, 20
        
        # 根据速度方向旋转
        angle = math.degrees(math.atan2(self.vy, self.vx))
        
        # 箭头形状
        # 主晶体
        length = 18
        points = [
            (cx + math.cos(math.radians(angle)) * length,
             cy + math.sin(math.radians(angle)) * length),
            (cx + math.cos(math.radians(angle + 150)) * 8,
             cy + math.sin(math.radians(angle + 150)) * 8),
            (cx + math.cos(math.radians(angle + 180)) * 5,
             cy + math.sin(math.radians(angle + 180)) * 5),
            (cx + math.cos(math.radians(angle - 150)) * 8,
             cy + math.sin(math.radians(angle - 150)) * 8),
        ]
        
        pygame.draw.polygon(self.image, self.rock_color, points)
        
        # 晶体高光
        inner_points = [
            (cx + math.cos(math.radians(angle)) * 14,
             cy + math.sin(math.radians(angle)) * 14),
            (cx + math.cos(math.radians(angle + 150)) * 5,
             cy + math.sin(math.radians(angle + 150)) * 5),
            (cx + math.cos(math.radians(angle - 150)) * 5,
             cy + math.sin(math.radians(angle - 150)) * 5),
        ]
        pygame.draw.polygon(self.image, self.crystal_color, inner_points)
        
        # 发光尖端
        tip_x = cx + math.cos(math.radians(angle)) * length
        tip_y = cy + math.sin(math.radians(angle)) * length
        pygame.draw.circle(self.image, (220, 180, 255), (int(tip_x), int(tip_y)), 3)
    
    def update(self):
        """更新晶簇箭"""
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 应用重力
        self.vy += self.gravity
        
        # 移动
        self.float_x += self.vx
        self.float_y += self.vy
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        self._draw()
        
        # 落地检测（超过目标高度或到达屏幕下方）
        if self.float_y > self.start_y or self.float_y > 650:
            self._land()
        
        # 命中敌人
        for enemy in mobs:
            if self.rect.colliderect(enemy.rect):
                enemy.hp -= self.damage
                if hasattr(enemy, 'hit_flash'):
                    enemy.hit_flash = 8
                self._land()
                break
    
    def _land(self):
        """落地生成晶柱"""
        pillar = CrystalPillar(self.float_x, self.float_y, self.damage, self.owner)
        all_sprites.add(pillar)
        active_pillars.append(pillar)
        
        # 检查连锁
        pillar.check_link()
        
        self.kill()


class CrystalPillar(pygame.sprite.Sprite):
    """晶簇柱 - 持续穿刺，阻挡弹幕"""
    
    def __init__(self, x, y, damage, owner):
        super().__init__()
        self.x = x
        self.y = y
        self.damage = damage
        self.owner = owner
        
        # 持续3秒
        self.duration = 180
        self.frame = 0
        
        # 生长动画
        self.height = 0
        self.max_height = 60
        self.growth_speed = 4
        
        # 伤害间隔
        self.damage_interval = 30
        self.damage_timer = 0
        
        # 阻挡次数
        self.block_count = 1
        self.blocked = False
        
        # 连接的墙
        self.linked_pillar = None
        self.wall = None
        
        # 图像
        self.image = pygame.Surface((40, 80), pygame.SRCALPHA)
        self.rect = self.image.get_rect(midbottom=(x, y))
    
    def _draw(self):
        """绘制晶柱"""
        self.image.fill((0, 0, 0, 0))
        cx = 20
        base_y = 75
        
        # 淡出效果
        fade = min(1.0, (self.duration - self.frame) / 30) if self.frame > self.duration - 30 else 1.0
        
        # 生长高度
        h = min(self.height, self.max_height)
        
        if h <= 0:
            return
        
        # 基座
        base_points = [
            (cx - 15, base_y),
            (cx + 15, base_y),
            (cx + 10, base_y - 10),
            (cx - 10, base_y - 10),
        ]
        pygame.draw.polygon(self.image, (80, 120, 150, int(200 * fade)), base_points)
        
        # 主晶体
        crystal_points = [
            (cx, base_y - h),  # 顶点
            (cx - 12, base_y - 10),
            (cx - 8, base_y - 5),
            (cx + 8, base_y - 5),
            (cx + 12, base_y - 10),
        ]
        pygame.draw.polygon(self.image, (140, 100, 180, int(220 * fade)), crystal_points)
        
        # 高光面
        highlight_points = [
            (cx, base_y - h),
            (cx - 6, base_y - 15),
            (cx + 2, base_y - 10),
        ]
        pygame.draw.polygon(self.image, (200, 160, 240, int(180 * fade)), highlight_points)
        
        # 侧晶簇
        for i, (offset_x, offset_h, size) in enumerate([(-8, 0.5, 0.6), (10, 0.4, 0.5), (-5, 0.7, 0.4)]):
            side_h = h * offset_h
            side_points = [
                (cx + offset_x, base_y - side_h * 1.2),
                (cx + offset_x - 4 * size, base_y - side_h * 0.3),
                (cx + offset_x + 4 * size, base_y - side_h * 0.3),
            ]
            pygame.draw.polygon(self.image, (160, 120, 200, int(180 * fade)), side_points)
        
        # 顶部发光
        glow_y = base_y - h
        glow_pulse = int(4 + 2 * math.sin(self.frame * 0.2))
        pygame.draw.circle(self.image, (220, 180, 255, int(150 * fade)), (cx, int(glow_y)), glow_pulse)
    
    def update(self):
        """更新晶柱"""
        self.frame += 1
        self.damage_timer += 1
        
        # 生长
        if self.height < self.max_height:
            self.height += self.growth_speed
        
        # 穿刺伤害
        if self.damage_timer >= self.damage_interval:
            self.damage_timer = 0
            self._deal_damage()
        
        self._draw()
        
        # 结束
        if self.frame >= self.duration:
            self._destroy()
    
    def _deal_damage(self):
        """对近身敌人造成穿刺伤害"""
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.x, enemy.rect.centery - self.y)
            if dist < 50:
                enemy.hp -= self.damage
                if hasattr(enemy, 'hit_flash'):
                    enemy.hit_flash = 8
    
    def check_link(self):
        """检查与其他晶柱的连接"""
        global active_pillars
        
        for other in active_pillars:
            if other == self or not other.alive():
                continue
            if other.linked_pillar:
                continue
            
            dist = math.hypot(other.x - self.x, other.y - self.y)
            if dist < 200:
                # 创建水晶墙
                self.linked_pillar = other
                other.linked_pillar = self
                
                wall = CrystalWall(self, other, self.damage * 1.5)
                all_sprites.add(wall)
                self.wall = wall
                other.wall = wall
                break
    
    def block_bullet(self):
        """阻挡弹幕"""
        if self.blocked:
            return False
        
        self.blocked = True
        self.block_count -= 1
        
        # 碎裂效果
        for i in range(5):
            shard = CrystalShard(self.x + random.randint(-15, 15), 
                               self.y - self.height + random.randint(-20, 0))
            all_sprites.add(shard)
        
        return True
    
    def _destroy(self):
        """销毁晶柱"""
        global active_pillars
        if self in active_pillars:
            active_pillars.remove(self)
        
        if self.wall:
            self.wall.kill()
        
        self.kill()


class CrystalWall(pygame.sprite.Sprite):
    """水晶墙 - 连接两根晶柱"""
    
    def __init__(self, pillar1, pillar2, damage):
        super().__init__()
        self.pillar1 = pillar1
        self.pillar2 = pillar2
        self.damage = damage
        
        # 真伤间隔
        self.damage_interval = 30
        self.damage_timer = 0
        
        self.frame = 0
        
        # 计算墙体范围
        min_x = min(pillar1.x, pillar2.x) - 20
        max_x = max(pillar1.x, pillar2.x) + 20
        min_y = min(pillar1.y, pillar2.y) - 80
        max_y = max(pillar1.y, pillar2.y) + 10
        
        width = max(100, int(max_x - min_x))
        height = max(100, int(max_y - min_y))
        
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(min_x, min_y))
        
        # 相对坐标
        self.p1_rel = (pillar1.x - min_x, pillar1.y - min_y)
        self.p2_rel = (pillar2.x - min_x, pillar2.y - min_y)
    
    def _draw(self):
        """绘制水晶墙"""
        self.image.fill((0, 0, 0, 0))
        
        x1, y1 = self.p1_rel
        x2, y2 = self.p2_rel
        
        # 墙体高度
        wall_top = min(y1, y2) - 50
        wall_bottom = max(y1, y2)
        
        # 半透明水晶墙
        pulse = 0.7 + 0.3 * math.sin(self.frame * 0.1)
        
        # 绘制连接线段（多层）
        for i in range(5):
            offset_y = i * 10
            alpha = int((150 - i * 25) * pulse)
            
            # 水晶面
            wall_points = [
                (x1, y1 - 50 + offset_y),
                (x2, y2 - 50 + offset_y),
                (x2, y2 - 40 + offset_y),
                (x1, y1 - 40 + offset_y),
            ]
            pygame.draw.polygon(self.image, (180, 120, 220, alpha), wall_points)
        
        # 能量线
        energy_y = wall_top + (self.frame * 2) % 50
        pygame.draw.line(self.image, (220, 180, 255, 200), 
                        (x1, energy_y), (x2, energy_y), 2)
        
        # 晶体颗粒
        for i in range(8):
            px = x1 + (x2 - x1) * i / 8
            py = (y1 + y2) / 2 - 45 + math.sin(self.frame * 0.2 + i) * 10
            pygame.draw.circle(self.image, (200, 160, 240, 180), (int(px), int(py)), 3)
    
    def update(self):
        """更新水晶墙"""
        self.frame += 1
        self.damage_timer += 1
        
        # 检查晶柱是否存活
        if not self.pillar1.alive() or not self.pillar2.alive():
            self.kill()
            return
        
        # 真伤
        if self.damage_timer >= self.damage_interval:
            self.damage_timer = 0
            self._deal_true_damage()
        
        self._draw()
    
    def _deal_true_damage(self):
        """对墙内敌人造成真伤"""
        x1, y1 = self.pillar1.x, self.pillar1.y
        x2, y2 = self.pillar2.x, self.pillar2.y
        
        for enemy in mobs:
            ex, ey = enemy.rect.centerx, enemy.rect.centery
            
            # 检查是否在墙体范围内
            min_x = min(x1, x2) - 20
            max_x = max(x1, x2) + 20
            min_y = min(y1, y2) - 60
            max_y = max(y1, y2)
            
            if min_x <= ex <= max_x and min_y <= ey <= max_y:
                # 真伤（无视防御）
                enemy.hp -= self.damage
                if hasattr(enemy, 'hit_flash'):
                    enemy.hit_flash = 8


class CrystalShard(pygame.sprite.Sprite):
    """水晶碎片"""
    
    def __init__(self, x, y):
        super().__init__()
        self.float_x = float(x)
        self.float_y = float(y)
        
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -2)
        
        self.lifetime = 30
        self.rotation = random.uniform(0, 360)
        
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        self._draw()
    
    def _draw(self):
        """绘制碎片"""
        self.image.fill((0, 0, 0, 0))
        
        fade = self.lifetime / 30
        color = (180, 140, 220, int(200 * fade))
        
        # 三角形碎片
        cx, cy = 7, 7
        points = []
        for i in range(3):
            angle = self.rotation + i * 120
            px = cx + math.cos(math.radians(angle)) * 5
            py = cy + math.sin(math.radians(angle)) * 5
            points.append((px, py))
        
        pygame.draw.polygon(self.image, color, points)
    
    def update(self):
        """更新碎片"""
        self.lifetime -= 1
        self.rotation += 10
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        self.vy += 0.3
        self.float_x += self.vx
        self.float_y += self.vy
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        self._draw()


class CrystalStorm(pygame.sprite.Sprite):
    """晶簇风暴 - 大招：大范围晶簇覆盖"""
    
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.damage = owner.damage * 2
        
        # 箭雨波数
        self.wave_count = 5
        self.waves_done = 0
        self.wave_interval = 15
        self.wave_timer = 0
        
        # 每波箭数
        self.arrows_per_wave = 8
        
        # 阶段
        self.phase = 0
        self.charge_duration = 25
        self.frame = 0
        
        self.image = pygame.Surface((540, 700), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _draw_charge(self):
        """绘制蓄力"""
        self.image.fill((0, 0, 0, 0))
        
        progress = self.frame / self.charge_duration
        cx, cy = self.owner.rect.centerx, self.owner.rect.centery
        
        # 晶体聚集
        for i in range(12):
            angle = i * 30 + self.frame * 5
            dist = 100 * (1 - progress) + 20
            px = cx + math.cos(math.radians(angle)) * dist
            py = cy + math.sin(math.radians(angle)) * dist
            
            # 小晶体
            size = int(8 * progress)
            points = [
                (px, py - size),
                (px - size * 0.6, py + size * 0.3),
                (px + size * 0.6, py + size * 0.3),
            ]
            pygame.draw.polygon(self.image, (180, 120, 220, int(200 * progress)), points)
        
        # 中心光环
        ring_r = int(25 * progress)
        pygame.draw.circle(self.image, (200, 150, 240, int(180 * progress)), (cx, cy), ring_r, 3)
    
    def _spawn_wave(self):
        """生成一波箭雨"""
        from config import bullets
        
        cx = self.owner.rect.centerx
        cy = self.owner.rect.centery
        
        for i in range(self.arrows_per_wave):
            # 扇形发射
            angle = -90 - 60 + i * (120 / (self.arrows_per_wave - 1))
            offset_x = random.randint(-20, 20)
            
            arrow = CrystalArrow(cx + offset_x, cy, angle, self.damage, self.owner)
            all_sprites.add(arrow)
            bullets.add(arrow)
    
    def update(self):
        """更新晶簇风暴"""
        self.frame += 1
        
        if self.phase == 0:
            self._draw_charge()
            if self.frame >= self.charge_duration:
                self.phase = 1
                self.frame = 0
        
        elif self.phase == 1:
            self.wave_timer += 1
            self.image.fill((0, 0, 0, 0))
            
            if self.waves_done < self.wave_count and self.wave_timer >= self.wave_interval:
                self.wave_timer = 0
                self._spawn_wave()
                self.waves_done += 1
            
            if self.waves_done >= self.wave_count and self.frame > 60:
                self.kill()


# ==============================================================================
#   子弹预览渲染函数
# ==============================================================================

def render_crystalfall_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Crystalfall子弹涂装预览效果 - 晶簇射流特效
    
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
    
    # 检查是否是Crystalfall子弹涂装
    crystalfall_effects = [
        "pillar_form", "wall_link", "magic_amp",
        "flame_crystal", "diamond_shine", "space_shard"
    ]
    
    matched_effect = None
    for effect in crystalfall_effects:
        if effect in effects:
            matched_effect = effect
            break
    
    if not matched_effect:
        return False
    
    # 根据效果类型绘制不同的预览
    crystal_size = size // 3
    sparkle = math.sin(t * 5) * 0.3 + 0.7  # 闪烁效果
    
    if matched_effect == "pillar_form":
        # 晶矢射流 - 透明晶矢
        _draw_crystal_arrow(surface, center_x, center_y, crystal_size,
                           (150, 200, 220), (180, 220, 250), sparkle)
        # 小晶柱
        _draw_mini_pillars(surface, center_x, center_y, crystal_size, (150, 200, 220), t)
    elif matched_effect == "wall_link":
        # 晶柱连壁 - 双柱连接
        _draw_crystal_arrow(surface, center_x, center_y, crystal_size,
                           (100, 150, 200), (150, 200, 255), sparkle)
        # 连接的双柱
        _draw_pillar_wall(surface, center_x, center_y, crystal_size, t)
    elif matched_effect == "magic_amp":
        # 紫晶射流 - 紫水晶
        _draw_crystal_arrow(surface, center_x, center_y, crystal_size,
                           (150, 100, 200), (200, 150, 255), sparkle)
        # 魔法光环
        ring_r = crystal_size + 8 + int(math.sin(t * 3) * 3)
        pygame.draw.circle(surface, (180, 130, 220), (center_x, center_y), ring_r, 2)
    elif matched_effect == "flame_crystal":
        # 红宝石瀑 - 火焰晶簇
        _draw_crystal_arrow(surface, center_x, center_y, crystal_size,
                           (200, 50, 80), (255, 100, 130), sparkle)
        # 火焰效果
        for i in range(4):
            flame_x = center_x + random.randint(-crystal_size//2, crystal_size//2)
            flame_y = center_y + random.randint(-crystal_size//2, crystal_size//2)
            pygame.draw.circle(surface, (255, 150, 80), (flame_x, flame_y), 3)
    elif matched_effect == "diamond_shine":
        # 钻石晶瀑 - 璀璨钻石
        _draw_crystal_arrow(surface, center_x, center_y, crystal_size,
                           (220, 220, 230), (255, 255, 255), sparkle)
        # 钻石闪光
        _draw_diamond_sparkles(surface, center_x, center_y, crystal_size, t)
    elif matched_effect == "space_shard":
        # 虚空晶瀑 - 空间碎片
        _draw_crystal_arrow(surface, center_x, center_y, crystal_size,
                           (80, 60, 120), (130, 110, 180), sparkle)
        # 空间碎片效果
        for i in range(3):
            angle = t * 90 + i * 120
            dist = crystal_size + 8
            fx = center_x + int(math.cos(math.radians(angle)) * dist)
            fy = center_y + int(math.sin(math.radians(angle)) * dist)
            # 小碎片
            frag_points = [
                (fx, fy - 5),
                (fx - 4, fy + 3),
                (fx + 4, fy + 3),
            ]
            pygame.draw.polygon(surface, (100, 80, 150), frag_points)
    
    return True


def _draw_crystal_arrow(surface, cx, cy, size, main_color, highlight_color, sparkle):
    """绘制晶矢形状"""
    # 主体 - 六角晶体
    points = []
    for i in range(6):
        angle = i * 60 - 90  # 尖端朝上
        if i % 2 == 0:
            # 长轴
            dist = size * sparkle
        else:
            # 短轴
            dist = size * 0.5 * sparkle
        px = cx + int(math.cos(math.radians(angle)) * dist)
        py = cy + int(math.sin(math.radians(angle)) * dist)
        points.append((px, py))
    
    # 外层光晕
    pygame.draw.polygon(surface, (*main_color, 80), points)
    
    # 主体
    pygame.draw.polygon(surface, main_color, points)
    pygame.draw.polygon(surface, highlight_color, points, 2)
    
    # 中心高光
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy), size // 4)


def _draw_mini_pillars(surface, cx, cy, size, color, t):
    """绘制小晶柱"""
    for i in range(3):
        angle = i * 120 + 30
        dist = size + 10
        px = cx + int(math.cos(math.radians(angle)) * dist)
        py = cy + int(math.sin(math.radians(angle)) * dist)
        
        # 小柱子
        pillar_h = 10 + int(math.sin(t * 2 + i) * 3)
        pillar_points = [
            (px, py - pillar_h),
            (px - 4, py),
            (px + 4, py),
        ]
        pygame.draw.polygon(surface, color, pillar_points)
        pygame.draw.polygon(surface, (255, 255, 255), pillar_points, 1)


def _draw_pillar_wall(surface, cx, cy, size, t):
    """绘制晶柱墙壁"""
    # 两根柱子
    offset = size + 5
    for side in [-1, 1]:
        px = cx + side * offset
        py = cy
        
        # 柱子
        pillar_h = 15
        pillar_points = [
            (px, py - pillar_h),
            (px - 5, py),
            (px + 5, py),
        ]
        pygame.draw.polygon(surface, (100, 150, 200), pillar_points)
        pygame.draw.polygon(surface, (150, 200, 255), pillar_points, 1)
    
    # 连接线
    wave = int(math.sin(t * 4) * 2)
    pygame.draw.line(surface, (150, 200, 255), 
                    (cx - offset, cy - 8 + wave),
                    (cx + offset, cy - 8 - wave), 2)


def _draw_diamond_sparkles(surface, cx, cy, size, t):
    """绘制钻石闪光"""
    for i in range(8):
        angle = i * 45 + t * 60
        dist = size + int(math.sin(t * 5 + i * 0.5) * 5) + 5
        px = cx + int(math.cos(math.radians(angle)) * dist)
        py = cy + int(math.sin(math.radians(angle)) * dist)
        
        # 闪光星
        star_size = 2 + int(math.sin(t * 6 + i) * 2)
        pygame.draw.line(surface, (255, 255, 255), 
                        (px - star_size, py), (px + star_size, py), 1)
        pygame.draw.line(surface, (255, 255, 255),
                        (px, py - star_size), (px, py + star_size), 1)
