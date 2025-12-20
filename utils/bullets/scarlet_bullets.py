# -*- coding: utf-8 -*-
"""
绯红恶魔·SCARLET 战机子弹涂装效果渲染模块

包含以下子弹效果：
- scarlet_lance: 魔枪投掷（普攻）- 高速旋转的红色能量长枪
- scarlet_mist: 迷雾闪烁（技能）- 红雾瞬移效果
- scarlet_meister: 绯红不夜城（终极I）- 东方弹幕风格
- scarlet_gungnir: 命运之枪（终极II）- 贯穿全屏的红色光枪
- scarlet_world: 深红世界（终极III）- 时停斩击
- scarlet_vampire: 吸血效果 - 生命偷取视觉
"""
import pygame
import math
import random

# 导入屏幕尺寸和精灵组
from config import WIDTH, HEIGHT, all_sprites, bullets, mobs, enemy_bullets


def render_scarlet_bullet(surface, effects, color, center_x, center_y, size, x, y, plane_id=None):
    """
    渲染SCARLET战机的子弹效果
    
    Args:
        surface: pygame绘图表面
        effects: 效果列表
        color: 主题颜色
        center_x, center_y: 中心坐标
        size: 子弹大小
        x, y: 左上角坐标
        plane_id: 机体ID
    
    Returns:
        bool: 如果渲染了效果返回True，否则False
    """
    
    # ========== 普攻：魔枪投掷 ==========
    if "scarlet_lance" in effects:
        # 高速旋转的红色能量长枪
        t = pygame.time.get_ticks() / 1000.0
        rotation = t * 8  # 高速旋转
        
        # 长枪主体
        lance_len = size // 2 + 5
        lance_width = 3
        
        # 旋转后的端点
        rad = math.radians(rotation)
        x1 = center_x - math.cos(rad) * lance_len
        y1 = center_y - math.sin(rad) * lance_len
        x2 = center_x + math.cos(rad) * lance_len
        y2 = center_y + math.sin(rad) * lance_len
        
        # 能量拖尾
        trail_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        for i in range(5):
            trail_rad = math.radians(rotation - i * 15)
            tx1 = size - math.cos(trail_rad) * (lance_len - i * 3)
            ty1 = size - math.sin(trail_rad) * (lance_len - i * 3)
            tx2 = size + math.cos(trail_rad) * (lance_len - i * 3)
            ty2 = size + math.sin(trail_rad) * (lance_len - i * 3)
            alpha = 150 - i * 30
            pygame.draw.line(trail_surf, (220, 20, 60, alpha), (int(tx1), int(ty1)), (int(tx2), int(ty2)), lance_width - 1)
        surface.blit(trail_surf, (x - size, y - size))
        
        # 主枪身
        pygame.draw.line(surface, (220, 20, 60), (int(x1), int(y1)), (int(x2), int(y2)), lance_width)
        pygame.draw.line(surface, (255, 100, 120), (int(x1), int(y1)), (int(x2), int(y2)), 1)
        
        # 金色尖端
        pygame.draw.circle(surface, (255, 215, 0), (int(x1), int(y1)), 3)
        pygame.draw.circle(surface, (255, 215, 0), (int(x2), int(y2)), 3)
        
        # 中心能量核心
        pygame.draw.circle(surface, (255, 50, 80), (center_x, center_y), 5)
        pygame.draw.circle(surface, (255, 215, 0), (center_x, center_y), 5, 1)
        
        return True
    
    # ========== 技能：迷雾闪烁 ==========
    elif "scarlet_mist" in effects:
        # 红雾瞬移效果
        t = pygame.time.get_ticks() / 1000.0
        
        # 红雾扩散
        mist_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        for i in range(15):
            mist_angle = t * 2 + i * 0.4
            mist_r = 5 + (i * 2) + math.sin(t * 3 + i) * 3
            mist_x = size + math.cos(mist_angle) * mist_r
            mist_y = size + math.sin(mist_angle * 0.8) * mist_r * 0.7
            mist_size = 6 + math.sin(t * 4 + i) * 2
            alpha = 120 - i * 7
            pygame.draw.circle(mist_surf, (180, 20, 50, alpha), (int(mist_x), int(mist_y)), int(mist_size))
        surface.blit(mist_surf, (x - size, y - size))
        
        # 闪烁核心
        blink_alpha = int(200 + math.sin(t * 10) * 55)
        blink_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(blink_surf, (255, 50, 80, blink_alpha), (size, size), size // 4)
        surface.blit(blink_surf, (x - size, y - size))
        
        # 无敌闪光线
        for i in range(4):
            flash_angle = t * 5 + i * (math.pi / 2)
            flash_len = size // 3 + math.sin(t * 8 + i) * 5
            fx = center_x + math.cos(flash_angle) * flash_len
            fy = center_y + math.sin(flash_angle) * flash_len
            pygame.draw.line(surface, (255, 200, 200), (center_x, center_y), (int(fx), int(fy)), 2)
        
        return True
    
    # ========== 终极I：绯红不夜城 ==========
    elif "scarlet_meister" in effects:
        # 东方Project弹幕风格 - 高密度规则排列
        t = pygame.time.get_ticks() / 1000.0
        
        # 弹幕花纹（多层环形）
        danmaku_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # 外层大环
        for i in range(16):
            angle = i * (math.pi / 8) + t * 1.5
            r = size // 2 + 8
            bx = size + math.cos(angle) * r
            by = size + math.sin(angle) * r
            bullet_size = 4 + math.sin(t * 3 + i * 0.5) * 1
            pygame.draw.circle(danmaku_surf, (220, 20, 60, 200), (int(bx), int(by)), int(bullet_size))
            pygame.draw.circle(danmaku_surf, (255, 150, 150, 180), (int(bx), int(by)), int(bullet_size), 1)
        
        # 中层环
        for i in range(12):
            angle = i * (math.pi / 6) - t * 2
            r = size // 3 + 3
            bx = size + math.cos(angle) * r
            by = size + math.sin(angle) * r
            pygame.draw.circle(danmaku_surf, (200, 30, 50, 220), (int(bx), int(by)), 3)
        
        # 内层花瓣
        for i in range(8):
            angle = i * (math.pi / 4) + t * 3
            r = size // 5
            bx = size + math.cos(angle) * r
            by = size + math.sin(angle) * r
            pygame.draw.circle(danmaku_surf, (255, 100, 120, 250), (int(bx), int(by)), 2)
        
        surface.blit(danmaku_surf, (x - size, y - size))
        
        # 中心红核
        pygame.draw.circle(surface, (255, 0, 50), (center_x, center_y), 6)
        pygame.draw.circle(surface, (255, 215, 0), (center_x, center_y), 6, 2)
        
        return True
    
    # ========== 终极II：命运之枪 Gungnir ==========
    elif "scarlet_gungnir" in effects:
        # 巨大的贯穿光枪
        t = pygame.time.get_ticks() / 1000.0
        
        # 主光枪
        lance_width = 8 + int(math.sin(t * 6) * 2)
        
        # 从中心向上延伸的光柱
        pygame.draw.line(surface, (255, 0, 50), (center_x, center_y + size // 2), (center_x, center_y - size // 2 - 10), lance_width)
        
        # 发光边缘
        glow_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        for i in range(3):
            glow_width = lance_width + (3 - i) * 4
            alpha = 80 - i * 25
            pygame.draw.line(glow_surf, (255, 100, 120, alpha), 
                           (size, size + size // 2), (size, size - size // 2 - 10), glow_width)
        surface.blit(glow_surf, (x - size, y - size))
        
        # 枪尖（三叉戟）
        tip_y = center_y - size // 2 - 10
        pygame.draw.polygon(surface, (255, 215, 0), [
            (center_x, tip_y - 8),
            (center_x - 6, tip_y),
            (center_x + 6, tip_y),
        ])
        # 左叉
        pygame.draw.line(surface, (255, 215, 0), (center_x - 4, tip_y), (center_x - 10, tip_y - 5), 2)
        # 右叉
        pygame.draw.line(surface, (255, 215, 0), (center_x + 4, tip_y), (center_x + 10, tip_y - 5), 2)
        
        # 能量波纹
        wave_r = (t * 50) % 30
        wave_alpha = int(200 * (1 - wave_r / 30))
        wave_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(wave_surf, (255, 50, 80, wave_alpha), (size, size), int(wave_r), 2)
        surface.blit(wave_surf, (x - size, y - size))
        
        return True
    
    # ========== 终极III：深红世界 ==========
    elif "scarlet_world" in effects:
        # 时停斩击效果
        t = pygame.time.get_ticks() / 1000.0
        
        # 时停效果 - 扭曲的时空
        world_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # 背景红色扭曲
        for i in range(8):
            distort_angle = i * (math.pi / 4)
            distort_r = size // 2 + math.sin(t * 0.5 + i) * 5  # 缓慢扭动
            dx = size + math.cos(distort_angle) * distort_r
            dy = size + math.sin(distort_angle) * distort_r
            pygame.draw.circle(world_surf, (128, 0, 0, 60), (int(dx), int(dy)), 10)
        
        # 时钟刻度（时停象征）
        for i in range(12):
            tick_angle = i * (math.pi / 6) - math.pi / 2
            tick_r1 = size // 2 - 3
            tick_r2 = size // 2 + 3
            tx1 = size + math.cos(tick_angle) * tick_r1
            ty1 = size + math.sin(tick_angle) * tick_r1
            tx2 = size + math.cos(tick_angle) * tick_r2
            ty2 = size + math.sin(tick_angle) * tick_r2
            pygame.draw.line(world_surf, (180, 50, 70, 150), (int(tx1), int(ty1)), (int(tx2), int(ty2)), 2)
        
        # 停止的时针（固定角度）
        frozen_angle = -math.pi / 4
        hx = size + math.cos(frozen_angle) * (size // 3)
        hy = size + math.sin(frozen_angle) * (size // 3)
        pygame.draw.line(world_surf, (255, 215, 0, 200), (size, size), (int(hx), int(hy)), 3)
        
        surface.blit(world_surf, (x - size, y - size))
        
        # 影分身斩击线
        slash_count = 6
        for i in range(slash_count):
            slash_angle = i * (math.pi / 3) + t * 0.2
            slash_len = size // 2 + 5
            sx1 = center_x + math.cos(slash_angle) * 5
            sy1 = center_y + math.sin(slash_angle) * 5
            sx2 = center_x + math.cos(slash_angle) * slash_len
            sy2 = center_y + math.sin(slash_angle) * slash_len
            
            # 斩击光
            pygame.draw.line(surface, (255, 100, 100), (int(sx1), int(sy1)), (int(sx2), int(sy2)), 3)
            pygame.draw.line(surface, (255, 255, 255), (int(sx1), int(sy1)), (int(sx2), int(sy2)), 1)
        
        # 中心核心
        pygame.draw.circle(surface, (180, 0, 30), (center_x, center_y), 8)
        pygame.draw.circle(surface, (255, 50, 80), (center_x, center_y), 5)
        
        return True
    
    # ========== 被动：吸血效果 ==========
    elif "scarlet_vampire" in effects:
        # 生命偷取视觉效果
        t = pygame.time.get_ticks() / 1000.0
        
        # 血滴吸收动画
        drain_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        for i in range(6):
            # 血滴从外向内收缩
            progress = (t * 1.5 + i * 0.3) % 1.0
            drop_r = size // 2 * (1 - progress) + 5
            drop_angle = i * (math.pi / 3) + t * 0.5
            dx = size + math.cos(drop_angle) * drop_r
            dy = size + math.sin(drop_angle) * drop_r
            
            # 血滴大小随进度减小
            drop_size = int(4 * (1 - progress) + 2)
            alpha = int(200 * (1 - progress))
            
            pygame.draw.circle(drain_surf, (200, 20, 40, alpha), (int(dx), int(dy)), drop_size)
        
        surface.blit(drain_surf, (x - size, y - size))
        
        # 中心吸收核心
        core_pulse = 1 + math.sin(t * 4) * 0.2
        core_r = int(6 * core_pulse)
        pygame.draw.circle(surface, (150, 0, 20), (center_x, center_y), core_r + 3)
        pygame.draw.circle(surface, (220, 20, 60), (center_x, center_y), core_r)
        
        # 生命恢复光环
        heal_alpha = int(100 + math.sin(t * 5) * 50)
        heal_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(heal_surf, (255, 100, 120, heal_alpha), (size, size), size // 3, 2)
        surface.blit(heal_surf, (x - size, y - size))
        
        return True
    
    # ========== 潜行一击（满潜行后的强化攻击） ==========
    elif "scarlet_stealth_strike" in effects:
        # 300%伤害的穿透攻击
        t = pygame.time.get_ticks() / 1000.0
        
        # 超长穿透枪
        strike_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # 主枪身（加长加粗）
        lance_len = size // 2 + 15
        pygame.draw.line(strike_surf, (255, 0, 50, 250), 
                        (size, size + lance_len // 2), (size, size - lance_len), 6)
        
        # 穿透残影
        for i in range(4):
            offset = i * 3
            alpha = 180 - i * 40
            pygame.draw.line(strike_surf, (220, 20, 60, alpha),
                           (size - offset, size + lance_len // 2), (size - offset, size - lance_len), 4)
            pygame.draw.line(strike_surf, (220, 20, 60, alpha),
                           (size + offset, size + lance_len // 2), (size + offset, size - lance_len), 4)
        
        surface.blit(strike_surf, (x - size, y - size))
        
        # 暴击星芒
        star_points = []
        for i in range(8):
            angle = i * (math.pi / 4) + t * 2
            outer_r = 12 if i % 2 == 0 else 6
            px = center_x + math.cos(angle) * outer_r
            py = center_y + math.sin(angle) * outer_r
            star_points.append((int(px), int(py)))
        
        if len(star_points) >= 3:
            pygame.draw.polygon(surface, (255, 215, 0), star_points)
            pygame.draw.polygon(surface, (255, 255, 200), star_points, 1)
        
        # 伤害数字暗示 "x3"
        pygame.draw.circle(surface, (255, 50, 80), (center_x, center_y), 4)
        
        return True
    
    return False


# =============================================================================
#   SCARLET 子弹类 - 魔枪投掷
# =============================================================================

class ScarletLanceBullet(pygame.sprite.Sprite):
    """
    魔枪投掷 - SCARLET的普攻子弹
    高速旋转的红色能量长枪，带有微弱吸血效果
    """
    def __init__(self, x, y, damage, owner=None, style="scarlet_default"):
        super().__init__()
        self.image = pygame.Surface((40, 12), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.damage = damage
        self.owner = owner
        self.style = style
        self.speed = 18  # 极快弹速
        self.rotation = 0
        self.lifetime = 120
        self.lifesteal = 0.05  # 5%吸血
        
        # 碰撞检测必需属性
        self.is_enemy = False  # 不是敌人的子弹
        self.piercing = 0      # 穿透次数（0=击中后消失）
        self.is_melee = False  # 不是近战武器
        self.is_special_bullet = False  # 不是特殊子弹
        
        # 颜色配置
        self.colors = {
            "scarlet_default": ((220, 20, 60), (255, 215, 0)),
            "scarlet_lunar": ((139, 0, 0), (255, 180, 100)),
            "scarlet_golden": ((255, 215, 0), (255, 255, 220)),
            "scarlet_mist": ((180, 20, 50), (200, 180, 160)),
            "scarlet_gothic": ((60, 40, 70), (200, 180, 200)),
            "scarlet_destiny": ((255, 0, 50), (255, 220, 180)),
        }
        self.body_color, self.gold_color = self.colors.get(style, self.colors["scarlet_default"])
        
    def update(self):
        self.rect.y -= self.speed
        self.rotation += 15
        self.lifetime -= 1
        
        if self.rect.bottom < 0 or self.lifetime <= 0:
            self.kill()
        
        self._render()
    
    def _render(self):
        self.image = pygame.Surface((40, 12), pygame.SRCALPHA)
        
        # 枪身
        pygame.draw.ellipse(self.image, self.body_color, (0, 3, 35, 6))
        pygame.draw.ellipse(self.image, self.gold_color, (0, 3, 35, 6), 1)
        
        # 枪尖
        pygame.draw.polygon(self.image, self.gold_color, [(35, 6), (40, 6), (37, 3), (37, 9)])
        
        # 旋转
        self.image = pygame.transform.rotate(self.image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)
    
    def on_hit(self, target):
        """击中时触发吸血"""
        if self.owner and hasattr(self.owner, 'hp') and hasattr(self.owner, 'max_hp'):
            heal = int(self.damage * self.lifesteal)
            self.owner.hp = min(self.owner.max_hp, self.owner.hp + heal)


# =============================================================================
#   SCARLET 技能类 - 迷雾闪烁 (F技能) - 增强版
# =============================================================================

class MistBlinkSkill(pygame.sprite.Sprite):
    """
    迷雾闪烁 - 化作红雾瞬移，过程无敌并伤害敌人
    增强版：更多粒子、血红拖尾、蝙蝠群特效
    """
    def __init__(self, owner, target_pos, damage, style="scarlet_default"):
        super().__init__()
        self.owner = owner
        self.start_pos = (owner.rect.centerx, owner.rect.centery)
        self.target_pos = target_pos
        self.damage = damage
        self.style = style
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        self.phase = 0  # 0=消散, 1=移动, 2=重现
        self.timer = 0
        self.mist_particles = []
        self.bats = []  # 蝙蝠群
        self.trail_points = []  # 血红拖尾
        self.blood_splashes = []  # 血花
        
        # 设置玩家无敌
        if self.owner:
            self.owner.invincible = True
            self.owner.invincible_timer = 90
        
        # 生成更多迷雾粒子 - 多层次
        for layer in range(3):
            for i in range(25):
                angle = random.random() * math.pi * 2
                dist = random.random() * (30 + layer * 20)
                self.mist_particles.append({
                    'x': self.start_pos[0] + math.cos(angle) * dist,
                    'y': self.start_pos[1] + math.sin(angle) * dist,
                    'vx': (random.random() - 0.5) * (3 + layer),
                    'vy': (random.random() - 0.5) * (3 + layer),
                    'size': random.randint(8, 20 - layer * 3),
                    'alpha': 255,
                    'layer': layer,
                    'color': [(180, 20, 50), (220, 40, 70), (150, 10, 30)][layer]
                })
        
        # 生成蝙蝠群
        for i in range(8):
            angle = random.random() * math.pi * 2
            self.bats.append({
                'x': self.start_pos[0],
                'y': self.start_pos[1],
                'angle': angle,
                'speed': random.uniform(8, 15),
                'size': random.randint(10, 18),
                'wing_phase': random.random() * math.pi * 2,
                'alpha': 255
            })
    
    def update(self):
        self.timer += 1
        
        if self.phase == 0:  # 消散阶段
            for p in self.mist_particles:
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['vx'] *= 0.95
                p['vy'] *= 0.95
                p['alpha'] = max(0, p['alpha'] - 12)
                p['size'] = max(1, p['size'] - 0.3)
            
            # 蝙蝠向外飞散
            for bat in self.bats:
                bat['x'] += math.cos(bat['angle']) * bat['speed']
                bat['y'] += math.sin(bat['angle']) * bat['speed']
                bat['wing_phase'] += 0.5
                bat['alpha'] = max(0, bat['alpha'] - 15)
            
            if self.timer >= 20:
                self.phase = 1
                self.timer = 0
                # 瞬移玩家
                if self.owner:
                    self.owner.rect.center = self.target_pos
                
                # 生成瞬移轨迹
                steps = 20
                for i in range(steps):
                    t = i / steps
                    tx = self.start_pos[0] + (self.target_pos[0] - self.start_pos[0]) * t
                    ty = self.start_pos[1] + (self.target_pos[1] - self.start_pos[1]) * t
                    self.trail_points.append({
                        'x': tx + random.randint(-10, 10),
                        'y': ty + random.randint(-10, 10),
                        'alpha': 200,
                        'size': random.randint(3, 8)
                    })
        
        elif self.phase == 1:  # 移动阶段 - 造成伤害
            # 轨迹消退
            for tp in self.trail_points:
                tp['alpha'] = max(0, tp['alpha'] - 8)
            
            # 对路径上的敌人造成伤害
            for mob in mobs:
                if hasattr(mob, 'rect') and hasattr(mob, 'hp'):
                    dist = self._point_to_line_dist(mob.rect.center, self.start_pos, self.target_pos)
                    if dist < 80:
                        mob.hp -= self.damage
                        # 血花特效
                        for _ in range(5):
                            angle = random.random() * math.pi * 2
                            self.blood_splashes.append({
                                'x': mob.rect.centerx,
                                'y': mob.rect.centery,
                                'vx': math.cos(angle) * random.uniform(3, 8),
                                'vy': math.sin(angle) * random.uniform(3, 8),
                                'size': random.randint(3, 8),
                                'alpha': 255
                            })
                        from sprites import Particle
                        Particle(mob.rect.center, (220, 20, 60), mode='shockwave')
            
            if self.timer >= 10:
                self.phase = 2
                self.timer = 0
                
                # 在目标位置生成重现粒子 - 更华丽
                self.mist_particles = []
                for layer in range(3):
                    for i in range(30):
                        angle = random.random() * math.pi * 2
                        dist = random.random() * 80
                        self.mist_particles.append({
                            'x': self.target_pos[0] + math.cos(angle) * dist,
                            'y': self.target_pos[1] + math.sin(angle) * dist,
                            'vx': -math.cos(angle) * (3 - layer),
                            'vy': -math.sin(angle) * (3 - layer),
                            'size': random.randint(5, 18),
                            'alpha': 0,
                            'layer': layer,
                            'color': [(220, 20, 60), (255, 50, 80), (180, 10, 40)][layer]
                        })
                
                # 重新生成蝙蝠群聚集
                self.bats = []
                for i in range(12):
                    angle = random.random() * math.pi * 2
                    dist = random.uniform(100, 200)
                    self.bats.append({
                        'x': self.target_pos[0] + math.cos(angle) * dist,
                        'y': self.target_pos[1] + math.sin(angle) * dist,
                        'target_x': self.target_pos[0],
                        'target_y': self.target_pos[1],
                        'size': random.randint(8, 15),
                        'wing_phase': random.random() * math.pi * 2,
                        'alpha': 0
                    })
        
        elif self.phase == 2:  # 重现阶段
            for p in self.mist_particles:
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['vx'] *= 0.9
                p['vy'] *= 0.9
                p['alpha'] = min(220, p['alpha'] + 18)
            
            # 蝙蝠聚集
            for bat in self.bats:
                dx = bat['target_x'] - bat['x']
                dy = bat['target_y'] - bat['y']
                bat['x'] += dx * 0.15
                bat['y'] += dy * 0.15
                bat['wing_phase'] += 0.4
                bat['alpha'] = min(200, bat['alpha'] + 20)
            
            # 血花更新
            for splash in self.blood_splashes:
                splash['x'] += splash['vx']
                splash['y'] += splash['vy']
                splash['vy'] += 0.3  # 重力
                splash['alpha'] = max(0, splash['alpha'] - 8)
            
            if self.timer >= 30:
                self.kill()
        
        self._render()
    
    def _point_to_line_dist(self, point, line_start, line_end):
        """计算点到线段的距离"""
        px, py = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)
        
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        
        return math.hypot(px - proj_x, py - proj_y)
    
    def _render(self):
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # 全屏红色闪烁（瞬移时刻）
        if self.phase == 1 and self.timer < 5:
            flash_alpha = int(60 * (1 - self.timer / 5))
            pygame.draw.rect(self.image, (220, 20, 60, flash_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 绘制瞬移轨迹
        for tp in self.trail_points:
            if tp['alpha'] > 0:
                pygame.draw.circle(self.image, (200, 20, 50, int(tp['alpha'])),
                                 (int(tp['x']), int(tp['y'])), tp['size'])
        
        # 连接轨迹的线
        if len(self.trail_points) > 1 and self.phase >= 1:
            for i in range(len(self.trail_points) - 1):
                if self.trail_points[i]['alpha'] > 20:
                    pygame.draw.line(self.image, (255, 50, 80, int(self.trail_points[i]['alpha'] * 0.5)),
                                   (int(self.trail_points[i]['x']), int(self.trail_points[i]['y'])),
                                   (int(self.trail_points[i+1]['x']), int(self.trail_points[i+1]['y'])), 3)
        
        # 绘制迷雾粒子（按层次）
        for layer in range(3):
            for p in self.mist_particles:
                if p['layer'] == layer and p['alpha'] > 0:
                    color = (*p['color'], int(p['alpha'] * 0.7))
                    pygame.draw.circle(self.image, color, (int(p['x']), int(p['y'])), int(p['size']))
        
        # 绘制蝙蝠
        for bat in self.bats:
            if bat['alpha'] > 0:
                self._draw_bat(bat)
        
        # 绘制血花
        for splash in self.blood_splashes:
            if splash['alpha'] > 0:
                pygame.draw.circle(self.image, (180, 0, 30, int(splash['alpha'])),
                                 (int(splash['x']), int(splash['y'])), splash['size'])
    
    def _draw_bat(self, bat):
        """绘制蝙蝠"""
        x, y = int(bat['x']), int(bat['y'])
        size = bat['size']
        wing = math.sin(bat['wing_phase']) * 0.5 + 0.5
        alpha = int(bat['alpha'])
        
        # 身体
        pygame.draw.ellipse(self.image, (40, 0, 20, alpha), (x - size//4, y - size//6, size//2, size//3))
        
        # 翅膀
        wing_span = int(size * (0.8 + wing * 0.4))
        wing_y = int(y - size//4 * wing)
        pygame.draw.polygon(self.image, (60, 0, 30, alpha), [
            (x, y),
            (x - wing_span, wing_y),
            (x - wing_span//2, y + size//4)
        ])
        pygame.draw.polygon(self.image, (60, 0, 30, alpha), [
            (x, y),
            (x + wing_span, wing_y),
            (x + wing_span//2, y + size//4)
        ])


# =============================================================================
#   SCARLET 技能类 - 绯红不夜城 (G技能) - 增强版
# =============================================================================

class ScarletMeisterSkill(pygame.sprite.Sprite):
    """
    绯红不夜城 - 东方弹幕风格高密度规则弹幕花纹覆盖全屏
    增强版：更华丽的弹幕图案、魔法阵、光束网格、符卡宣言效果
    """
    def __init__(self, x, y, damage, owner=None, style="scarlet_default"):
        super().__init__()
        self.x = x
        self.y = y
        self.damage = damage
        self.owner = owner
        self.style = style
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        self.timer = 0
        self.duration = 240  # 4秒
        self.bullets = []
        self.spawn_timer = 0
        self.magic_circles = []  # 魔法阵
        self.laser_beams = []    # 激光束
        self.rose_petals = []    # 玫瑰花瓣
        self.spell_declared = False
        
        # 初始化魔法阵
        for i in range(3):
            self.magic_circles.append({
                'x': WIDTH // 2,
                'y': 120 + i * 80,
                'radius': 60 + i * 30,
                'rotation': i * 30,
                'alpha': 0
            })
        
    def update(self):
        self.timer += 1
        self.spawn_timer += 1
        
        # 符卡宣言阶段（开场）
        if self.timer < 30:
            for mc in self.magic_circles:
                mc['alpha'] = min(200, mc['alpha'] + 8)
                mc['rotation'] += 2
            return self._render()
        
        # 魔法阵持续旋转
        for mc in self.magic_circles:
            mc['rotation'] += 1.5
        
        # 每隔几帧生成弹幕
        if self.spawn_timer >= 4 and self.timer < self.duration - 30:
            self.spawn_timer = 0
            self._spawn_danmaku_wave()
        
        # 定期生成激光
        if self.timer % 60 == 30 and self.timer < self.duration - 60:
            self._spawn_laser_beam()
        
        # 生成玫瑰花瓣
        if random.random() < 0.15:
            self.rose_petals.append({
                'x': random.randint(0, WIDTH),
                'y': -20,
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(2, 4),
                'rotation': random.random() * 360,
                'rot_speed': random.uniform(-5, 5),
                'size': random.randint(8, 15),
                'alpha': random.randint(150, 220)
            })
        
        # 更新弹幕
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['vx']
            bullet['y'] += bullet['vy']
            bullet['life'] -= 1
            bullet['pulse'] = bullet.get('pulse', 0) + 0.2
            
            if bullet['life'] <= 0 or bullet['y'] > HEIGHT + 50 or bullet['x'] < -50 or bullet['x'] > WIDTH + 50:
                self.bullets.remove(bullet)
            else:
                # 碰撞检测
                for mob in mobs:
                    if hasattr(mob, 'rect') and hasattr(mob, 'hp'):
                        if math.hypot(mob.rect.centerx - bullet['x'], mob.rect.centery - bullet['y']) < 25:
                            mob.hp -= self.damage * 0.25
                            from sprites import Particle
                            Particle((bullet['x'], bullet['y']), bullet['color'], mode='spark')
                            if bullet in self.bullets:
                                self.bullets.remove(bullet)
                            break
        
        # 更新激光
        for laser in self.laser_beams[:]:
            laser['life'] -= 1
            laser['width'] = max(1, laser['width'] - 0.3)
            if laser['life'] <= 0:
                self.laser_beams.remove(laser)
            else:
                # 激光伤害
                for mob in mobs:
                    if hasattr(mob, 'rect') and hasattr(mob, 'hp'):
                        if self._point_on_laser(mob.rect.center, laser):
                            mob.hp -= self.damage * 0.1
        
        # 更新花瓣
        for petal in self.rose_petals[:]:
            petal['x'] += petal['vx']
            petal['y'] += petal['vy']
            petal['rotation'] += petal['rot_speed']
            petal['alpha'] = max(0, petal['alpha'] - 1)
            if petal['y'] > HEIGHT + 30 or petal['alpha'] <= 0:
                self.rose_petals.remove(petal)
        
        # 结束阶段
        if self.timer >= self.duration - 30:
            for mc in self.magic_circles:
                mc['alpha'] = max(0, mc['alpha'] - 8)
        
        if self.timer >= self.duration:
            self.kill()
        
        self._render()
    
    def _point_on_laser(self, point, laser):
        """检查点是否在激光上"""
        px, py = point
        x1, y1 = laser['start']
        x2, y2 = laser['end']
        
        # 简化：检查点到线段距离
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1) < laser['width'] * 2
        
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        proj_x, proj_y = x1 + t * dx, y1 + t * dy
        return math.hypot(px - proj_x, py - proj_y) < laser['width'] * 2
    
    def _spawn_laser_beam(self):
        """生成激光束"""
        angle = random.uniform(-0.3, 0.3)
        start_x = random.randint(100, WIDTH - 100)
        self.laser_beams.append({
            'start': (start_x, 0),
            'end': (start_x + math.tan(angle) * HEIGHT, HEIGHT),
            'width': 20,
            'life': 40,
            'color': random.choice([(255, 50, 80), (255, 100, 150), (200, 30, 60)])
        })
    
    def _spawn_danmaku_wave(self):
        """生成东方弹幕风格的弹幕波 - 更华丽"""
        wave_type = (self.timer // 40) % 5
        cx = WIDTH // 2
        t = self.timer * 0.05
        
        if wave_type == 0:
            # 双螺旋环形弹幕
            num_bullets = 24
            for i in range(num_bullets):
                angle = (i / num_bullets) * math.pi * 2 + t
                speed = 3.5
                for spiral in range(2):
                    offset = spiral * math.pi
                    self.bullets.append({
                        'x': cx + math.cos(angle + offset) * 50,
                        'y': 80,
                        'vx': math.cos(angle + offset) * speed * 0.6,
                        'vy': speed + math.sin(t * 3) * 0.5,
                        'size': 7,
                        'color': (255, 50, 80) if spiral == 0 else (255, 180, 200),
                        'life': 150,
                        'glow': True
                    })
        
        elif wave_type == 1:
            # 扇形展开弹幕
            for i in range(12):
                angle = math.pi / 2 + (i - 5.5) * 0.12
                speed = 5
                self.bullets.append({
                    'x': cx + (i - 5.5) * 40,
                    'y': 60,
                    'vx': math.cos(angle) * speed * 0.4,
                    'vy': math.sin(angle) * speed,
                    'size': 6,
                    'color': (220, 20, 60),
                    'life': 130
                })
        
        elif wave_type == 2:
            # 四方向十字弹幕
            for dir_idx in range(4):
                base_angle = dir_idx * (math.pi / 2) + t * 0.5
                for j in range(3):
                    angle = base_angle + (j - 1) * 0.15
                    speed = 4 + j * 0.5
                    start_x = cx + math.cos(base_angle) * 80
                    start_y = 200 + math.sin(base_angle) * 80
                    self.bullets.append({
                        'x': start_x,
                        'y': start_y,
                        'vx': math.cos(angle) * speed,
                        'vy': math.sin(angle) * speed,
                        'size': 5 + j,
                        'color': [(255, 80, 100), (255, 150, 180), (200, 40, 70)][j],
                        'life': 120
                    })
        
        elif wave_type == 3:
            # 花瓣形弹幕
            petals = 6
            for i in range(petals):
                petal_angle = (i / petals) * math.pi * 2 + t
                for j in range(5):
                    r = 30 + j * 15
                    bx = cx + math.cos(petal_angle) * r
                    by = 150 + math.sin(petal_angle) * r * 0.5
                    self.bullets.append({
                        'x': bx,
                        'y': by,
                        'vx': math.cos(petal_angle + math.pi/2) * 2,
                        'vy': 3 + j * 0.3,
                        'size': 8 - j,
                        'color': (255, 100 + j * 20, 150),
                        'life': 100
                    })
        
        else:
            # 密集螺旋弹幕
            for i in range(8):
                angle = t * 2 + i * (math.pi / 4)
                speed = 3
                self.bullets.append({
                    'x': cx + math.cos(angle) * 120,
                    'y': 100 + math.sin(angle) * 40,
                    'vx': math.cos(angle + math.pi / 2) * speed * 0.8,
                    'vy': speed,
                    'size': 9,
                    'color': (180, 20, 50),
                    'life': 140,
                    'glow': True
                })
    
    def _render(self):
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # 背景渐变红色
        progress = self.timer / self.duration
        bg_alpha = int(40 * math.sin(progress * math.pi))
        pygame.draw.rect(self.image, (100, 0, 20, bg_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 绘制魔法阵
        for mc in self.magic_circles:
            if mc['alpha'] > 0:
                self._draw_magic_circle(mc)
        
        # 绘制激光
        for laser in self.laser_beams:
            if laser['life'] > 0:
                # 外层光晕
                for i in range(3):
                    width = laser['width'] + i * 4
                    alpha = max(0, min(255, int(laser['life'] * 4 - i * 30)))
                    pygame.draw.line(self.image, (*laser['color'][:3], alpha),
                                   laser['start'], laser['end'], int(width))
                # 核心
                pygame.draw.line(self.image, (255, 255, 255, min(255, laser['life'] * 6)),
                               laser['start'], laser['end'], max(1, int(laser['width'] * 0.3)))
        
        # 绘制弹幕
        for bullet in self.bullets:
            bx, by = int(bullet['x']), int(bullet['y'])
            size = bullet['size']
            pulse = 1 + math.sin(bullet.get('pulse', 0)) * 0.2
            
            # 发光效果
            if bullet.get('glow'):
                for i in range(2):
                    glow_size = int(size * (1.5 + i * 0.5) * pulse)
                    glow_alpha = max(0, 100 - i * 40)
                    pygame.draw.circle(self.image, (*bullet['color'], glow_alpha), (bx, by), glow_size)
            
            # 核心
            pygame.draw.circle(self.image, bullet['color'], (bx, by), int(size * pulse))
            pygame.draw.circle(self.image, (255, 220, 230), (bx, by), max(1, int(size * 0.4 * pulse)))
        
        # 绘制玫瑰花瓣
        for petal in self.rose_petals:
            self._draw_rose_petal(petal)
        
        # 符卡名称（开场显示）
        if self.timer < 60:
            alpha = min(255, self.timer * 8) if self.timer < 30 else max(0, 255 - (self.timer - 30) * 8)
            # 这里只是视觉装饰，实际文字由游戏主循环绘制
    
    def _draw_magic_circle(self, mc):
        """绘制魔法阵"""
        x, y = int(mc['x']), int(mc['y'])
        r = mc['radius']
        rot = math.radians(mc['rotation'])
        alpha = int(mc['alpha'])
        
        # 外圈
        pygame.draw.circle(self.image, (220, 20, 60, alpha), (x, y), r, 2)
        pygame.draw.circle(self.image, (255, 100, 120, alpha // 2), (x, y), r + 5, 1)
        
        # 内部图案 - 六芒星
        for i in range(6):
            angle = rot + i * (math.pi / 3)
            x1 = x + math.cos(angle) * r * 0.9
            y1 = y + math.sin(angle) * r * 0.9
            x2 = x + math.cos(angle + math.pi / 3) * r * 0.9
            y2 = y + math.sin(angle + math.pi / 3) * r * 0.9
            pygame.draw.line(self.image, (255, 50, 80, alpha), (int(x1), int(y1)), (int(x2), int(y2)), 2)
        
        # 中心符文
        inner_r = r * 0.4
        pygame.draw.circle(self.image, (255, 180, 200, alpha), (x, y), int(inner_r), 1)
        for i in range(8):
            angle = -rot * 2 + i * (math.pi / 4)
            lx = x + math.cos(angle) * inner_r
            ly = y + math.sin(angle) * inner_r
            pygame.draw.circle(self.image, (255, 100, 150, alpha), (int(lx), int(ly)), 3)
    
    def _draw_rose_petal(self, petal):
        """绘制玫瑰花瓣"""
        x, y = int(petal['x']), int(petal['y'])
        size = petal['size']
        rot = math.radians(petal['rotation'])
        alpha = int(petal['alpha'])
        
        # 简化花瓣形状
        points = []
        for i in range(8):
            angle = rot + i * (math.pi / 4)
            r = size * (0.8 + 0.2 * math.sin(i * 2))
            points.append((x + math.cos(angle) * r, y + math.sin(angle) * r))
        
        pygame.draw.polygon(self.image, (200, 30, 60, alpha), points)


# =============================================================================
#   SCARLET 技能类 - 命运之枪 Gungnir (C技能) - 增强版
# =============================================================================

class GungnirSpearSkill(pygame.sprite.Sprite):
    """
    命运之枪 - 投掷贯穿全屏的巨大红色光枪，在尽头爆炸
    增强版：蓄力光环、能量聚集、枪身华丽装饰、震撼爆炸
    """
    def __init__(self, x, y, damage, owner=None, style="scarlet_default"):
        super().__init__()
        self.start_x = x
        self.start_y = y
        self.damage = damage
        self.owner = owner
        self.style = style
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        self.phase = 0  # 0=蓄力, 1=投掷, 2=爆炸
        self.timer = 0
        self.spear_y = y
        self.hit_enemies = set()
        
        # 蓄力粒子
        self.charge_particles = []
        self.energy_rings = []
        self.trail_particles = []
        self.explosion_particles = []
        self.shockwaves = []
        
        # 初始化能量环
        for i in range(5):
            self.energy_rings.append({
                'radius': 150 - i * 25,
                'rotation': i * 30,
                'alpha': 0
            })
        
    def update(self):
        self.timer += 1
        
        if self.phase == 0:  # 蓄力阶段
            # 生成聚集粒子
            if self.timer % 2 == 0:
                angle = random.random() * math.pi * 2
                dist = random.uniform(100, 200)
                self.charge_particles.append({
                    'x': self.start_x + math.cos(angle) * dist,
                    'y': self.start_y + math.sin(angle) * dist,
                    'target_x': self.start_x,
                    'target_y': self.start_y,
                    'size': random.randint(3, 8),
                    'color': random.choice([(255, 50, 80), (255, 215, 0), (255, 150, 180)])
                })
            
            # 粒子聚集
            for p in self.charge_particles[:]:
                dx = p['target_x'] - p['x']
                dy = p['target_y'] - p['y']
                p['x'] += dx * 0.15
                p['y'] += dy * 0.15
                if math.hypot(dx, dy) < 10:
                    self.charge_particles.remove(p)
            
            # 能量环扩张
            for ring in self.energy_rings:
                ring['alpha'] = min(200, ring['alpha'] + 6)
                ring['rotation'] += 3
            
            if self.timer >= 45:
                self.phase = 1
                self.timer = 0
                self.charge_particles = []
        
        elif self.phase == 1:  # 投掷阶段
            self.spear_y -= 35  # 更快速度
            
            # 生成尾迹粒子
            for i in range(3):
                self.trail_particles.append({
                    'x': self.start_x + random.randint(-15, 15),
                    'y': self.spear_y + random.randint(20, 60),
                    'vx': random.uniform(-1, 1),
                    'vy': random.uniform(2, 5),
                    'size': random.randint(4, 10),
                    'alpha': 255,
                    'color': random.choice([(255, 0, 50), (255, 100, 100), (255, 215, 0)])
                })
            
            # 更新尾迹
            for p in self.trail_particles[:]:
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['alpha'] = max(0, p['alpha'] - 12)
                p['size'] = max(1, p['size'] - 0.3)
                if p['alpha'] <= 0:
                    self.trail_particles.remove(p)
            
            # 能量环收缩消失
            for ring in self.energy_rings:
                ring['radius'] = max(0, ring['radius'] - 5)
                ring['alpha'] = max(0, ring['alpha'] - 8)
            
            # 碰撞检测
            for mob in mobs:
                if hasattr(mob, 'rect') and hasattr(mob, 'hp'):
                    if id(mob) not in self.hit_enemies:
                        if abs(mob.rect.centerx - self.start_x) < 50:
                            if mob.rect.top < self.spear_y < mob.rect.bottom + 250:
                                mob.hp -= self.damage
                                self.hit_enemies.add(id(mob))
                                from sprites import Particle
                                Particle(mob.rect.center, (255, 215, 0), mode='shockwave')
                                # 额外血花
                                for _ in range(8):
                                    angle = random.random() * math.pi * 2
                                    self.explosion_particles.append({
                                        'x': mob.rect.centerx,
                                        'y': mob.rect.centery,
                                        'vx': math.cos(angle) * random.uniform(5, 12),
                                        'vy': math.sin(angle) * random.uniform(5, 12),
                                        'size': random.randint(4, 10),
                                        'alpha': 255,
                                        'color': (255, 50, 80)
                                    })
            
            if self.spear_y < -150:
                self.phase = 2
                self.timer = 0
                # 生成爆炸冲击波
                for i in range(4):
                    self.shockwaves.append({
                        'x': self.start_x,
                        'y': 50,
                        'radius': 10,
                        'max_radius': 200 + i * 80,
                        'alpha': 255,
                        'delay': i * 5
                    })
                # 大量爆炸粒子
                for _ in range(50):
                    angle = random.random() * math.pi * 2
                    speed = random.uniform(5, 20)
                    self.explosion_particles.append({
                        'x': self.start_x,
                        'y': 30,
                        'vx': math.cos(angle) * speed,
                        'vy': math.sin(angle) * speed + random.uniform(-2, 5),
                        'size': random.randint(3, 12),
                        'alpha': 255,
                        'color': random.choice([(255, 0, 50), (255, 215, 0), (255, 100, 50), (255, 255, 200)])
                    })
        
        elif self.phase == 2:  # 爆炸阶段
            # 更新冲击波
            for sw in self.shockwaves[:]:
                if sw['delay'] > 0:
                    sw['delay'] -= 1
                else:
                    sw['radius'] += 15
                    sw['alpha'] = max(0, 255 * (1 - sw['radius'] / sw['max_radius']))
                    if sw['radius'] >= sw['max_radius']:
                        self.shockwaves.remove(sw)
            
            # 更新爆炸粒子
            for p in self.explosion_particles[:]:
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['vy'] += 0.3  # 重力
                p['vx'] *= 0.98
                p['alpha'] = max(0, p['alpha'] - 5)
                p['size'] = max(1, p['size'] - 0.1)
                if p['alpha'] <= 0:
                    self.explosion_particles.remove(p)
            
            if self.timer >= 60:
                self.kill()
        
        self._render()
    
    def _render(self):
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        if self.phase == 0:
            # 蓄力背景闪烁
            flash = int(20 + 15 * math.sin(self.timer * 0.3))
            pygame.draw.rect(self.image, (100, 0, 20, flash), (0, 0, WIDTH, HEIGHT))
            
            # 能量环
            for ring in self.energy_rings:
                if ring['alpha'] > 0:
                    self._draw_energy_ring(self.start_x, self.start_y, ring)
            
            # 聚集粒子
            for p in self.charge_particles:
                pygame.draw.circle(self.image, p['color'], (int(p['x']), int(p['y'])), p['size'])
            
            # 中心蓄力光球
            charge = self.timer / 45
            glow_r = int(40 * charge)
            for i in range(4):
                r = glow_r - i * 8
                if r > 0:
                    alpha = min(255, int(200 - i * 40))
                    color = (255, 50 + i * 30, 80 + i * 20, alpha)
                    pygame.draw.circle(self.image, color, (self.start_x, self.start_y), r)
            
            # 金色核心
            core_r = int(15 * charge)
            pygame.draw.circle(self.image, (255, 215, 0), (self.start_x, self.start_y), core_r)
            pygame.draw.circle(self.image, (255, 255, 220), (self.start_x, self.start_y), core_r // 2)
        
        elif self.phase == 1:
            # 尾迹粒子
            for p in self.trail_particles:
                if p['alpha'] > 0:
                    pygame.draw.circle(self.image, (*p['color'], int(p['alpha'])),
                                     (int(p['x']), int(p['y'])), int(p['size']))
            
            # 巨型光枪
            self._draw_gungnir_spear()
        
        elif self.phase == 2:
            # 爆炸闪光
            if self.timer < 10:
                flash_alpha = int(150 * (1 - self.timer / 10))
                pygame.draw.rect(self.image, (255, 200, 150, flash_alpha), (0, 0, WIDTH, HEIGHT))
            
            # 冲击波
            for sw in self.shockwaves:
                if sw['delay'] <= 0 and sw['alpha'] > 0:
                    pygame.draw.circle(self.image, (255, 100, 50, int(sw['alpha'])),
                                     (int(sw['x']), int(sw['y'])), int(sw['radius']), 4)
                    pygame.draw.circle(self.image, (255, 215, 0, int(sw['alpha'] * 0.6)),
                                     (int(sw['x']), int(sw['y'])), int(sw['radius'] * 0.7), 2)
            
            # 爆炸粒子
            for p in self.explosion_particles:
                if p['alpha'] > 0:
                    pygame.draw.circle(self.image, (*p['color'], int(p['alpha'])),
                                     (int(p['x']), int(p['y'])), int(p['size']))
    
    def _draw_energy_ring(self, cx, cy, ring):
        """绘制能量环"""
        r = ring['radius']
        rot = math.radians(ring['rotation'])
        alpha = int(ring['alpha'])
        
        # 外环
        pygame.draw.circle(self.image, (255, 50, 80, alpha), (cx, cy), int(r), 2)
        
        # 符文点
        for i in range(8):
            angle = rot + i * (math.pi / 4)
            px = cx + math.cos(angle) * r
            py = cy + math.sin(angle) * r
            pygame.draw.circle(self.image, (255, 215, 0, alpha), (int(px), int(py)), 4)
    
    def _draw_gungnir_spear(self):
        """绘制命运之枪"""
        cx = self.start_x
        spear_length = 180
        tip_y = int(self.spear_y)
        base_y = tip_y + spear_length
        
        # 外层发光
        for i in range(5):
            width = 30 - i * 5
            alpha = max(0, 150 - i * 30)
            pygame.draw.line(self.image, (255, 0, 50, alpha),
                           (cx, tip_y), (cx, base_y), width)
        
        # 枪身渐变
        pygame.draw.line(self.image, (255, 50, 80), (cx, tip_y + 30), (cx, base_y), 16)
        pygame.draw.line(self.image, (255, 100, 120), (cx, tip_y + 30), (cx, base_y), 10)
        pygame.draw.line(self.image, (255, 180, 200), (cx, tip_y + 30), (cx, base_y), 4)
        
        # 三叉戟尖端 - 更华丽
        # 中央尖刃
        pygame.draw.polygon(self.image, (255, 215, 0), [
            (cx, tip_y),
            (cx - 12, tip_y + 40),
            (cx + 12, tip_y + 40)
        ])
        pygame.draw.polygon(self.image, (255, 255, 220), [
            (cx, tip_y + 5),
            (cx - 6, tip_y + 35),
            (cx + 6, tip_y + 35)
        ])
        
        # 左侧刃
        pygame.draw.polygon(self.image, (255, 215, 0), [
            (cx - 25, tip_y + 15),
            (cx - 8, tip_y + 35),
            (cx - 15, tip_y + 50)
        ])
        
        # 右侧刃
        pygame.draw.polygon(self.image, (255, 215, 0), [
            (cx + 25, tip_y + 15),
            (cx + 8, tip_y + 35),
            (cx + 15, tip_y + 50)
        ])
        
        # 装饰环
        pygame.draw.circle(self.image, (255, 215, 0), (cx, tip_y + 60), 12, 3)
        pygame.draw.circle(self.image, (255, 50, 80), (cx, tip_y + 60), 8)
        
        # 枪尾焰
        flame_y = base_y
        for i in range(8):
            flame_length = random.randint(20, 50)
            flame_x = cx + random.randint(-10, 10)
            alpha = max(0, 200 - i * 20)
            pygame.draw.line(self.image, (255, 100, 50, alpha),
                           (flame_x, flame_y), (flame_x, flame_y + flame_length), 3 - i // 3)


# =============================================================================
#   SCARLET 终极技能 - 深红世界 (大招) - 增强版
# =============================================================================

class CrimsonWorldUltimate(pygame.sprite.Sprite):
    """
    深红世界 - 时间停止3秒，影分身同时斩击所有敌人
    增强版：全屏时停滤镜、巨大时钟、华丽影分身、刀光斩击、血雨结束
    """
    def __init__(self, owner, damage):
        super().__init__()
        self.owner = owner
        self.damage = damage
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        self.phase = 0  # 0=时停, 1=分身出现, 2=斩击, 3=结束
        self.timer = 0
        self.shadows = []
        self.slash_lines = []
        self.clock_hands = {'hour': 0, 'minute': 0}
        self.blood_drops = []
        self.shatter_pieces = []
        self.after_images = []
        
        # 时间停止效果
        self.frozen_mobs = list(mobs)
        self.frozen_bullets = list(enemy_bullets)
        
        # 冻结敌人和子弹
        for mob in self.frozen_mobs:
            if hasattr(mob, 'frozen'):
                mob.frozen = True
        for bullet in self.frozen_bullets:
            if hasattr(bullet, 'frozen'):
                bullet.frozen = True
        
        # 记录敌人位置，生成影分身（更精致）
        for mob in self.frozen_mobs:
            if hasattr(mob, 'rect'):
                # 多个角度的分身
                for angle_offset in [-0.3, 0, 0.3]:
                    angle = math.atan2(mob.rect.centery - owner.rect.centery,
                                      mob.rect.centerx - owner.rect.centerx) + angle_offset
                    dist = 60
                    shadow_x = mob.rect.centerx - math.cos(angle) * dist
                    shadow_y = mob.rect.centery - math.sin(angle) * dist
                    self.shadows.append({
                        'x': shadow_x,
                        'y': shadow_y,
                        'target': mob,
                        'alpha': 0,
                        'angle': angle,
                        'scale': random.uniform(0.8, 1.2),
                        'attack_delay': random.randint(0, 10)
                    })
        
        # 生成时钟碎片（预备）
        for i in range(20):
            angle = random.random() * math.pi * 2
            self.shatter_pieces.append({
                'x': WIDTH // 2,
                'y': HEIGHT // 2,
                'vx': math.cos(angle) * random.uniform(5, 15),
                'vy': math.sin(angle) * random.uniform(5, 15),
                'rotation': random.random() * 360,
                'rot_speed': random.uniform(-10, 10),
                'size': random.randint(10, 30),
                'alpha': 0,
                'active': False
            })
    
    def update(self):
        self.timer += 1
        
        if self.phase == 0:  # 时停阶段
            # 时钟指针急停效果
            stop_progress = min(1, self.timer / 20)
            self.clock_hands['minute'] = 360 * (1 - stop_progress) * 2
            self.clock_hands['hour'] = 30 * (1 - stop_progress)
            
            if self.timer >= 40:
                self.phase = 1
                self.timer = 0
        
        elif self.phase == 1:  # 分身出现
            for shadow in self.shadows:
                shadow['alpha'] = min(220, shadow['alpha'] + 12)
            
            # 生成残影
            if self.timer % 3 == 0:
                for shadow in self.shadows[:5]:
                    if shadow['alpha'] > 50:
                        self.after_images.append({
                            'x': shadow['x'] + random.randint(-20, 20),
                            'y': shadow['y'] + random.randint(-20, 20),
                            'alpha': 100
                        })
            
            # 残影消退
            for ai in self.after_images[:]:
                ai['alpha'] -= 8
                if ai['alpha'] <= 0:
                    self.after_images.remove(ai)
            
            if self.timer >= 50:
                self.phase = 2
                self.timer = 0
                
                # 生成斩击线（更华丽）
                for shadow in self.shadows:
                    if shadow['target'] and hasattr(shadow['target'], 'rect'):
                        # 多条斩击线
                        for i in range(3):
                            offset = (i - 1) * 15
                            self.slash_lines.append({
                                'start': (shadow['x'] + offset, shadow['y']),
                                'end': (shadow['target'].rect.centerx + offset, shadow['target'].rect.centery),
                                'alpha': 255,
                                'width': 6 - i,
                                'target': shadow['target'] if i == 1 else None,
                                'delay': shadow['attack_delay'] + i * 2,
                                'color': [(255, 50, 80), (255, 100, 150), (255, 200, 220)][i]
                            })
        
        elif self.phase == 2:  # 斩击阶段
            # 造成伤害（延迟触发）
            for slash in self.slash_lines:
                if slash['delay'] > 0:
                    slash['delay'] -= 1
                elif slash['delay'] == 0:
                    slash['delay'] = -1  # 标记已触发
                    if slash['target'] and hasattr(slash['target'], 'hp'):
                        slash['target'].hp -= self.damage
                        from sprites import Particle
                        Particle(slash['target'].rect.center, (220, 20, 60), mode='shockwave')
                        
                        # 血花飞溅
                        for _ in range(12):
                            angle = random.random() * math.pi * 2
                            speed = random.uniform(3, 10)
                            self.blood_drops.append({
                                'x': slash['target'].rect.centerx,
                                'y': slash['target'].rect.centery,
                                'vx': math.cos(angle) * speed,
                                'vy': math.sin(angle) * speed,
                                'size': random.randint(2, 6),
                                'alpha': 255
                            })
            
            # 斩击线效果
            for slash in self.slash_lines:
                if slash['delay'] < 0:
                    slash['alpha'] = max(0, slash['alpha'] - 12)
            
            # 更新血滴
            for drop in self.blood_drops[:]:
                drop['x'] += drop['vx']
                drop['y'] += drop['vy']
                drop['vy'] += 0.3
                drop['alpha'] = max(0, drop['alpha'] - 4)
                if drop['alpha'] <= 0:
                    self.blood_drops.remove(drop)
            
            if self.timer >= 50:
                self.phase = 3
                self.timer = 0
                
                # 激活时钟碎片
                for piece in self.shatter_pieces:
                    piece['active'] = True
                    piece['alpha'] = 200
                
                # 解除时停
                for mob in self.frozen_mobs:
                    if hasattr(mob, 'frozen'):
                        mob.frozen = False
                for bullet in self.frozen_bullets:
                    if hasattr(bullet, 'frozen'):
                        bullet.frozen = False
        
        elif self.phase == 3:  # 结束
            # 碎片飞散
            for piece in self.shatter_pieces:
                if piece['active']:
                    piece['x'] += piece['vx']
                    piece['y'] += piece['vy']
                    piece['vy'] += 0.2
                    piece['rotation'] += piece['rot_speed']
                    piece['alpha'] = max(0, piece['alpha'] - 6)
            
            # 血滴继续下落
            for drop in self.blood_drops[:]:
                drop['x'] += drop['vx']
                drop['y'] += drop['vy']
                drop['vy'] += 0.3
                drop['alpha'] = max(0, drop['alpha'] - 3)
                if drop['alpha'] <= 0:
                    self.blood_drops.remove(drop)
            
            if self.timer >= 40:
                self.kill()
        
        self._render()
    
    def _render(self):
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # 时停滤镜效果
        if self.phase < 3:
            # 深红色滤镜 + 灰度边缘
            filter_alpha = 50 if self.phase < 2 else int(50 * (1 - self.timer / 40))
            pygame.draw.rect(self.image, (80, 0, 20, filter_alpha), (0, 0, WIDTH, HEIGHT))
            
            # 边缘渐变暗角
            for i in range(4):
                vignette_alpha = int(30 - i * 8)
                if vignette_alpha > 0:
                    pygame.draw.rect(self.image, (0, 0, 0, vignette_alpha), 
                                   (i * 50, i * 30, WIDTH - i * 100, HEIGHT - i * 60), 
                                   width=50)
        
        # 巨大时钟
        if self.phase <= 1:
            self._draw_clock()
        
        # 时钟碎片
        for piece in self.shatter_pieces:
            if piece['active'] and piece['alpha'] > 0:
                self._draw_clock_piece(piece)
        
        # 绘制残影
        for ai in self.after_images:
            if ai['alpha'] > 0:
                pygame.draw.circle(self.image, (220, 20, 60, int(ai['alpha'])),
                                 (int(ai['x']), int(ai['y'])), 15)
        
        # 绘制影分身
        for shadow in self.shadows:
            if shadow['alpha'] > 0:
                self._draw_shadow(shadow)
        
        # 绘制斩击线
        for slash in self.slash_lines:
            if slash['alpha'] > 0 and slash['delay'] <= 0:
                self._draw_slash_line(slash)
        
        # 绘制血滴
        for drop in self.blood_drops:
            if drop['alpha'] > 0:
                pygame.draw.circle(self.image, (180, 0, 30, int(drop['alpha'])),
                                 (int(drop['x']), int(drop['y'])), drop['size'])
        
        # 结束时的"咔嚓"裂纹效果
        if self.phase == 3 and self.timer < 15:
            self._draw_screen_crack()
    
    def _draw_clock(self):
        """绘制巨大时钟"""
        cx, cy = WIDTH // 2, HEIGHT // 2
        clock_radius = 280
        
        # 外圈 - 多层发光
        for i in range(4):
            r = clock_radius + i * 8
            alpha = max(0, 150 - i * 35)
            pygame.draw.circle(self.image, (180, 50, 70, alpha), (cx, cy), r, 3)
        
        # 刻度
        for i in range(60):
            angle = i * (math.pi / 30) - math.pi / 2
            is_hour = i % 5 == 0
            inner_r = clock_radius - (25 if is_hour else 15)
            outer_r = clock_radius - 5
            
            x1 = cx + math.cos(angle) * inner_r
            y1 = cy + math.sin(angle) * inner_r
            x2 = cx + math.cos(angle) * outer_r
            y2 = cy + math.sin(angle) * outer_r
            
            width = 4 if is_hour else 2
            color = (255, 215, 0, 200) if is_hour else (220, 100, 120, 150)
            pygame.draw.line(self.image, color, (int(x1), int(y1)), (int(x2), int(y2)), width)
        
        # 罗马数字位置的装饰
        for i in range(12):
            angle = i * (math.pi / 6) - math.pi / 2
            num_r = clock_radius - 50
            nx = cx + math.cos(angle) * num_r
            ny = cy + math.sin(angle) * num_r
            pygame.draw.circle(self.image, (255, 50, 80, 180), (int(nx), int(ny)), 8)
            pygame.draw.circle(self.image, (255, 200, 200, 200), (int(nx), int(ny)), 4)
        
        # 时针
        hour_angle = math.radians(self.clock_hands['hour']) - math.pi / 2
        hour_length = 120
        hx = cx + math.cos(hour_angle) * hour_length
        hy = cy + math.sin(hour_angle) * hour_length
        pygame.draw.line(self.image, (255, 215, 0), (cx, cy), (int(hx), int(hy)), 8)
        pygame.draw.line(self.image, (255, 255, 220), (cx, cy), (int(hx), int(hy)), 4)
        
        # 分针
        min_angle = math.radians(self.clock_hands['minute']) - math.pi / 2
        min_length = 180
        mx = cx + math.cos(min_angle) * min_length
        my = cy + math.sin(min_angle) * min_length
        pygame.draw.line(self.image, (255, 100, 120), (cx, cy), (int(mx), int(my)), 5)
        pygame.draw.line(self.image, (255, 200, 200), (cx, cy), (int(mx), int(my)), 2)
        
        # 中心装饰
        pygame.draw.circle(self.image, (255, 215, 0), (cx, cy), 20)
        pygame.draw.circle(self.image, (255, 50, 80), (cx, cy), 15)
        pygame.draw.circle(self.image, (255, 255, 220), (cx, cy), 8)
    
    def _draw_clock_piece(self, piece):
        """绘制时钟碎片"""
        x, y = int(piece['x']), int(piece['y'])
        size = piece['size']
        rot = math.radians(piece['rotation'])
        alpha = int(piece['alpha'])
        
        # 不规则碎片
        points = []
        for i in range(5):
            angle = rot + i * (math.pi * 2 / 5)
            r = size * (0.7 + random.random() * 0.3)
            points.append((x + math.cos(angle) * r, y + math.sin(angle) * r))
        
        pygame.draw.polygon(self.image, (180, 80, 100, alpha), points)
        pygame.draw.polygon(self.image, (255, 150, 170, alpha), points, 2)
    
    def _draw_shadow(self, shadow):
        """绘制影分身"""
        x, y = int(shadow['x']), int(shadow['y'])
        alpha = int(shadow['alpha'])
        scale = shadow['scale']
        angle = shadow['angle']
        
        # 机体轮廓 - 三角形
        size = int(35 * scale)
        points = [
            (x + math.cos(angle) * size, y + math.sin(angle) * size),
            (x + math.cos(angle + 2.5) * size * 0.8, y + math.sin(angle + 2.5) * size * 0.8),
            (x + math.cos(angle - 2.5) * size * 0.8, y + math.sin(angle - 2.5) * size * 0.8)
        ]
        
        # 外层光晕
        pygame.draw.polygon(self.image, (255, 50, 80, alpha // 2), points)
        pygame.draw.polygon(self.image, (220, 20, 60, alpha), points, 2)
        
        # 眼睛（红色亮点）
        eye_x = x + math.cos(angle) * size * 0.3
        eye_y = y + math.sin(angle) * size * 0.3
        pygame.draw.circle(self.image, (255, 0, 0, alpha), (int(eye_x), int(eye_y)), 4)
        pygame.draw.circle(self.image, (255, 255, 200, alpha), (int(eye_x), int(eye_y)), 2)
    
    def _draw_slash_line(self, slash):
        """绘制斩击线"""
        alpha = int(slash['alpha'])
        width = slash['width']
        color = slash['color']
        
        # 主线
        pygame.draw.line(self.image, (*color, alpha), slash['start'], slash['end'], width)
        
        # 发光
        pygame.draw.line(self.image, (255, 255, 255, alpha // 2), slash['start'], slash['end'], max(1, width - 2))
    
    def _draw_screen_crack(self):
        """绘制屏幕裂纹效果"""
        cx, cy = WIDTH // 2, HEIGHT // 2
        
        # 从中心向外的裂纹
        num_cracks = 8
        for i in range(num_cracks):
            angle = i * (math.pi * 2 / num_cracks) + 0.2
            
            # 主裂纹
            length = random.randint(200, 400)
            end_x = cx + math.cos(angle) * length
            end_y = cy + math.sin(angle) * length
            
            alpha = int(200 * (1 - self.timer / 15))
            pygame.draw.line(self.image, (255, 255, 255, alpha), (cx, cy), (int(end_x), int(end_y)), 3)
            
            # 分支裂纹
            for j in range(2):
                branch_start = (cx + math.cos(angle) * length * (0.3 + j * 0.3),
                              cy + math.sin(angle) * length * (0.3 + j * 0.3))
                branch_angle = angle + random.uniform(-0.5, 0.5)
                branch_length = random.randint(30, 80)
                branch_end = (branch_start[0] + math.cos(branch_angle) * branch_length,
                            branch_start[1] + math.sin(branch_angle) * branch_length)
                pygame.draw.line(self.image, (255, 200, 200, alpha),
                               (int(branch_start[0]), int(branch_start[1])),
                               (int(branch_end[0]), int(branch_end[1])), 2)


# 导出
__all__ = [
    'render_scarlet_bullet',
    'ScarletLanceBullet',
    'MistBlinkSkill',
    'ScarletMeisterSkill', 
    'GungnirSpearSkill',
    'CrimsonWorldUltimate'
]
