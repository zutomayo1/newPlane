# -*- coding: utf-8 -*-
"""
方舟·苍穹 (GALAXIA) 大招技能系统
原型致敬: Ark of the Cosmos (泰拉瑞亚宇宙方舟)
核心概念: 剪刀变型机 - 星辰切割与次元撕裂
"""
import pygame
import math
import random

# 导入游戏核心
from config import WIDTH, HEIGHT, all_sprites, bullets, mobs, enemy_bullets

# ==================== 主题颜色获取 ====================
GALAXIA_THEMES = {
    "default": {
        "midnight_blue": (25, 25, 112),      # 午夜蓝
        "nebula_purple": (147, 112, 219),    # 星云紫
        "lavender": (230, 230, 250),         # 薰衣草白
        "star_glow": (255, 255, 200),        # 星光
        "void_black": (10, 10, 20),          # 虚空黑
        "cosmic_cyan": (0, 191, 255),        # 宇宙青
    },
    "solar": {
        "midnight_blue": (255, 100, 0),      # 太阳橙
        "nebula_purple": (255, 140, 50),     # 日冕
        "lavender": (255, 220, 150),         # 日光
        "star_glow": (255, 255, 100),        # 耀斑
        "void_black": (50, 20, 0),           # 暗红
        "cosmic_cyan": (255, 180, 50),       # 金橙
    },
    "nebula": {
        "midnight_blue": (180, 50, 200),     # 深紫
        "nebula_purple": (220, 100, 255),    # 亮紫
        "lavender": (255, 180, 255),         # 粉紫
        "star_glow": (200, 150, 255),        # 紫光
        "void_black": (30, 10, 45),          # 暗紫
        "cosmic_cyan": (150, 80, 220),       # 紫青
    },
    "vortex": {
        "midnight_blue": (0, 100, 150),      # 深青
        "nebula_purple": (50, 180, 200),     # 青绿
        "lavender": (150, 230, 255),         # 冰蓝
        "star_glow": (100, 255, 255),        # 青光
        "void_black": (0, 30, 40),           # 深海蓝
        "cosmic_cyan": (0, 200, 255),        # 电光青
    },
    "stardust": {
        "midnight_blue": (0, 150, 100),      # 翠绿
        "nebula_purple": (50, 220, 150),     # 青翠
        "lavender": (150, 255, 200),         # 浅绿
        "star_glow": (100, 255, 180),        # 星尘绿
        "void_black": (10, 40, 30),          # 深绿
        "cosmic_cyan": (0, 255, 150),        # 荧光绿
    },
    "crimson": {
        "midnight_blue": (150, 0, 0),        # 深红
        "nebula_purple": (220, 50, 50),      # 血红
        "lavender": (255, 150, 150),         # 粉红
        "star_glow": (255, 100, 100),        # 红光
        "void_black": (40, 0, 0),            # 暗血
        "cosmic_cyan": (255, 50, 100),       # 玫红
    },
    "corruption": {
        "midnight_blue": (80, 0, 120),       # 暗紫
        "nebula_purple": (140, 50, 180),     # 腐化紫
        "lavender": (200, 150, 230),         # 紫丁香
        "star_glow": (180, 100, 220),        # 紫辉
        "void_black": (25, 0, 35),           # 深紫黑
        "cosmic_cyan": (120, 50, 180),       # 魔紫
    },
    "hallowed": {
        "midnight_blue": (255, 200, 100),    # 圣金
        "nebula_purple": (255, 230, 150),    # 圣光
        "lavender": (255, 255, 200),         # 神圣白
        "star_glow": (255, 255, 255),        # 纯白
        "void_black": (60, 50, 30),          # 暗金
        "cosmic_cyan": (255, 220, 120),      # 金辉
    },
    "lunar": {
        "midnight_blue": (180, 180, 200),    # 月蓝
        "nebula_purple": (200, 200, 230),    # 月光
        "lavender": (230, 230, 255),         # 月白
        "star_glow": (200, 220, 255),        # 月华
        "void_black": (40, 40, 50),          # 月影
        "cosmic_cyan": (180, 200, 255),      # 寒月
    },
    "zenith": {
        "midnight_blue": (255, 150, 0),      # 极致橙
        "nebula_purple": (255, 100, 200),    # 极致粉
        "lavender": (200, 255, 255),         # 极致青
        "star_glow": (255, 255, 100),        # 极致金
        "void_black": (50, 30, 50),          # 极致暗
        "cosmic_cyan": (100, 255, 255),      # 极致亮青
    },
    "rainbow": {
        "midnight_blue": (255, 0, 127),      # 彩虹1
        "nebula_purple": (127, 0, 255),      # 彩虹2
        "lavender": (0, 255, 127),           # 彩虹3
        "star_glow": (255, 255, 0),          # 彩虹4
        "void_black": (30, 30, 30),          # 黑
        "cosmic_cyan": (0, 255, 255),        # 彩虹5
    },
    "void": {
        "midnight_blue": (50, 0, 80),        # 虚空紫
        "nebula_purple": (100, 0, 150),      # 深空紫
        "lavender": (180, 100, 220),         # 虚空光
        "star_glow": (150, 50, 200),         # 虚空辉
        "void_black": (5, 5, 10),            # 纯黑
        "cosmic_cyan": (80, 0, 120),         # 虚空青
    },
}

def get_theme(style):
    """获取主题颜色"""
    style_key = style.replace("galaxia_", "") if style.startswith("galaxia_") else style
    return GALAXIA_THEMES.get(style_key, GALAXIA_THEMES["default"])


# ==================== F键 - 次元斩 (Dimensional Slash) ====================
class DimensionalSlashSkill(pygame.sprite.Sprite):
    """
    F键终极技能 - 次元斩
    机体瞬间消失，屏幕出现三道贯穿全屏的紫色裂痕
    裂痕错位滑动，对全屏敌人造成真实伤害切割
    【超级视觉增强版】
    """
    
    def __init__(self, player_x, player_y, damage, style="default"):
        super().__init__()
        self.player_x = player_x
        self.player_y = player_y
        self.damage = damage
        self.style = style
        self.theme = get_theme(style)
        
        self.frame = 0
        self.max_frames = 180  # 3秒技能
        
        # 五道裂痕（增加到5道）
        self.slashes = []
        for i in range(5):
            self.slashes.append({
                'angle': random.uniform(-45, 45),  # 更大角度变化
                'offset': (i - 2) * 70,            # Y轴偏移
                'progress': 0,                      # 裂开进度
                'width': random.randint(20, 40),    # 更宽裂痕
                'shift': 0,                         # 错位量
                'phase': random.uniform(0, 6.28),   # 相位差
                'wave_amp': random.uniform(30, 60), # 波动幅度
            })
        
        # 粒子效果（大幅增加）
        self.particles = []
        
        # 闪电效果
        self.lightning_bolts = []
        
        # 星尘尾迹
        self.stardust_trails = []
        
        # 次元裂隙光柱
        self.light_pillars = []
        
        # 屏幕闪光
        self.screen_flash = 255
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        
        # 屏幕闪光衰减
        self.screen_flash = max(0, self.screen_flash - 15)
        
        # 阶段1: 裂痕形成 (0-60帧) - 伴随剧烈震动效果
        if self.frame <= 60:
            for slash in self.slashes:
                slash['progress'] = min(1.0, slash['progress'] + 0.025)
            
            # 每帧生成大量初始粒子
            if self.frame % 2 == 0:
                for _ in range(15):
                    self.particles.append({
                        'x': random.randint(0, WIDTH),
                        'y': random.randint(0, HEIGHT),
                        'vx': random.uniform(-8, 8),
                        'vy': random.uniform(-8, 8),
                        'life': random.randint(30, 60),
                        'size': random.randint(4, 12),
                        'color_type': random.choice(['glow', 'purple', 'cyan']),
                    })
        
        # 阶段2: 错位滑动 + 伤害 (30-150帧)
        if 30 <= self.frame <= 150:
            for i, slash in enumerate(self.slashes):
                # 复杂波动动画
                t = self.frame * 0.08 + slash['phase']
                slash['shift'] = math.sin(t) * slash['wave_amp'] + math.sin(t * 2.3) * 20
            
            # 每8帧造成一次伤害
            if self.frame % 8 == 0:
                self._deal_damage()
            
            # 生成闪电
            if self.frame % 12 == 0:
                self._spawn_lightning()
            
            # 生成光柱
            if self.frame % 20 == 0:
                self._spawn_light_pillar()
        
        # 阶段3: 愈合消失 (150-180帧)
        if self.frame > 150:
            for slash in self.slashes:
                slash['progress'] = max(0, slash['progress'] - 0.04)
        
        # 持续生成星尘粒子
        if self.frame % 2 == 0 and self.frame < 160:
            for slash in self.slashes:
                y = HEIGHT // 2 + slash['offset'] + slash['shift']
                for _ in range(3):
                    self.particles.append({
                        'x': random.randint(0, WIDTH),
                        'y': y + random.randint(-50, 50),
                        'vx': random.uniform(-4, 4),
                        'vy': random.uniform(-4, 4),
                        'life': random.randint(25, 50),
                        'size': random.randint(3, 10),
                        'color_type': random.choice(['glow', 'purple', 'cyan', 'white']),
                    })
        
        # 更新粒子
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vx'] *= 0.96
            p['vy'] *= 0.96
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
        
        # 更新闪电
        for bolt in self.lightning_bolts[:]:
            bolt['life'] -= 1
            if bolt['life'] <= 0:
                self.lightning_bolts.remove(bolt)
        
        # 更新光柱
        for pillar in self.light_pillars[:]:
            pillar['life'] -= 1
            pillar['width'] *= 0.95
            if pillar['life'] <= 0:
                self.light_pillars.remove(pillar)
        
        if self.frame >= self.max_frames:
            self.kill()
            return
        
        self._render()
    
    def _spawn_lightning(self):
        """生成次元闪电"""
        for _ in range(2):
            start_x = random.randint(0, WIDTH)
            self.lightning_bolts.append({
                'start_x': start_x,
                'points': self._generate_lightning_path(start_x),
                'life': 15,
                'width': random.randint(2, 5),
            })
    
    def _generate_lightning_path(self, start_x):
        """生成闪电路径"""
        points = [(start_x, 0)]
        y = 0
        x = start_x
        while y < HEIGHT:
            y += random.randint(20, 50)
            x += random.randint(-40, 40)
            x = max(0, min(WIDTH, x))
            points.append((x, min(y, HEIGHT)))
        return points
    
    def _spawn_light_pillar(self):
        """生成光柱"""
        self.light_pillars.append({
            'x': random.randint(50, WIDTH - 50),
            'life': 30,
            'width': random.randint(30, 60),
            'color': random.choice(['cyan', 'purple', 'glow']),
        })
    
    def _deal_damage(self):
        """对全屏敌人造成伤害"""
        for mob in mobs:
            if hasattr(mob, 'take_damage'):
                for slash in self.slashes:
                    slash_y = HEIGHT // 2 + slash['offset'] + slash['shift']
                    if abs(mob.rect.centery - slash_y) < 120:
                        mob.take_damage(self.damage * 0.5)
                        # 命中特效
                        for _ in range(5):
                            self.particles.append({
                                'x': mob.rect.centerx,
                                'y': mob.rect.centery,
                                'vx': random.uniform(-10, 10),
                                'vy': random.uniform(-10, 10),
                                'life': 20,
                                'size': random.randint(5, 12),
                                'color_type': 'white',
                            })
                        break
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        
        # 屏幕闪光
        if self.screen_flash > 0:
            flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((*self.theme["lavender"], self.screen_flash))
            self.image.blit(flash_surf, (0, 0))
        
        # 绘制光柱
        for pillar in self.light_pillars:
            alpha = int(180 * (pillar['life'] / 30))
            w = int(pillar['width'])
            color_key = pillar['color']
            if color_key == 'cyan':
                color = self.theme["cosmic_cyan"]
            elif color_key == 'purple':
                color = self.theme["nebula_purple"]
            else:
                color = self.theme["star_glow"]
            
            # 渐变光柱
            for i in range(3):
                layer_w = w - i * 10
                if layer_w > 0:
                    layer_alpha = alpha // (i + 1)
                    pygame.draw.rect(self.image, (*color, layer_alpha),
                                   (pillar['x'] - layer_w // 2, 0, layer_w, HEIGHT))
        
        # 绘制裂痕
        for slash in self.slashes:
            if slash['progress'] <= 0:
                continue
            
            y = HEIGHT // 2 + slash['offset'] + slash['shift']
            width = int(slash['width'] * slash['progress'])
            alpha = int(230 * slash['progress'])
            
            # 裂痕外层光晕（紫色扩散）
            for glow_layer in range(4):
                glow_width = width + glow_layer * 8
                glow_alpha = max(0, alpha // (glow_layer + 1))
                pygame.draw.line(self.image, (*self.theme["nebula_purple"], glow_alpha),
                               (0, y), (WIDTH, y), glow_width)
            
            # 裂痕主体（虚空黑）
            pygame.draw.line(self.image, (*self.theme["void_black"], alpha),
                           (0, y), (WIDTH, y), width)
            
            # 裂痕内部能量线
            for inner in range(3):
                inner_y = y + (inner - 1) * (width // 4)
                inner_alpha = int(alpha * 0.8)
                pygame.draw.line(self.image, (*self.theme["cosmic_cyan"], inner_alpha),
                               (0, inner_y), (WIDTH, inner_y), 2)
            
            # 锯齿边缘
            for i in range(0, WIDTH, 15):
                jag_offset = int(math.sin(i * 0.1 + self.frame * 0.3) * (width // 3))
                jag_alpha = int(alpha * 0.7)
                pygame.draw.circle(self.image, (*self.theme["star_glow"], jag_alpha),
                                 (i, int(y + jag_offset)), 4)
                pygame.draw.circle(self.image, (*self.theme["star_glow"], jag_alpha),
                                 (i, int(y - jag_offset)), 4)
            
            # 星光闪烁（更密集）
            for i in range(0, WIDTH, 25):
                star_phase = self.frame * 0.25 + i * 0.5 + slash['phase']
                star_alpha = int((alpha // 2) * (0.5 + 0.5 * math.sin(star_phase)))
                star_size = int(3 + 3 * math.sin(star_phase * 1.5))
                pygame.draw.circle(self.image, (*self.theme["star_glow"], star_alpha),
                                 (i, int(y)), star_size)
        
        # 绘制闪电
        for bolt in self.lightning_bolts:
            alpha = int(255 * (bolt['life'] / 15))
            points = bolt['points']
            if len(points) >= 2:
                # 主闪电
                pygame.draw.lines(self.image, (*self.theme["cosmic_cyan"], alpha),
                                False, points, bolt['width'] + 2)
                pygame.draw.lines(self.image, (*self.theme["lavender"], alpha),
                                False, points, bolt['width'])
        
        # 绘制粒子
        for p in self.particles:
            progress = p['life'] / 50
            alpha = int(200 * progress)
            size = int(p['size'] * (0.4 + 0.6 * progress))
            if size > 0:
                if p['color_type'] == 'glow':
                    color = self.theme["star_glow"]
                elif p['color_type'] == 'purple':
                    color = self.theme["nebula_purple"]
                elif p['color_type'] == 'cyan':
                    color = self.theme["cosmic_cyan"]
                else:
                    color = self.theme["lavender"]
                pygame.draw.circle(self.image, (*color, alpha),
                                 (int(p['x']), int(p['y'])), size)


# ==================== G键 - 星系陷阱 (Galaxy Trap) ====================
class GalaxyTrapSkill(pygame.sprite.Sprite):
    """
    G键终极技能 - 星系陷阱
    扔出剪刀在屏幕中心高速旋转，产生引力吸附敌人
    向四周散射密集的星座弹幕
    【超级视觉增强版】
    """
    
    def __init__(self, player_x, player_y, damage, style="default"):
        super().__init__()
        self.float_x = float(player_x)
        self.float_y = float(player_y)
        self.damage = damage
        self.style = style
        self.theme = get_theme(style)
        
        self.frame = 0
        self.max_frames = 240  # 4秒技能
        
        # 移动到屏幕中心
        self.target_x = WIDTH // 2
        self.target_y = HEIGHT // 2
        
        # 旋转角度
        self.angle = 0
        self.spin_speed = 5
        
        # 吸引力
        self.gravity_radius = 280
        self.gravity_strength = 0.4
        
        # 弹幕发射
        self.shoot_cooldown = 0
        
        # 粒子系统
        self.particles = []
        self.orbit_stars = []  # 环绕星体
        self.spiral_arms = []  # 螺旋臂
        self.absorbed_trails = []  # 吸收尾迹
        
        # 初始化环绕星体
        for i in range(12):
            self.orbit_stars.append({
                'angle': i * 30,
                'radius': random.randint(80, 150),
                'speed': random.uniform(0.5, 1.5),
                'size': random.randint(4, 10),
                'phase': random.uniform(0, 6.28),
            })
        
        # 初始化螺旋臂
        for i in range(4):
            self.spiral_arms.append({
                'base_angle': i * 90,
                'particles': [],
            })
        
        self.image = pygame.Surface((500, 500), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(player_x), int(player_y)))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        
        # 阶段1: 飞向中心 (0-30帧)
        if self.frame <= 30:
            self.float_x += (self.target_x - self.float_x) * 0.12
            self.float_y += (self.target_y - self.float_y) * 0.12
        
        # 阶段2: 高速旋转 + 引力 + 弹幕 (30-210帧)
        if 30 < self.frame <= 210:
            self.angle += self.spin_speed
            self.spin_speed = min(25, self.spin_speed + 0.15)
            
            # 引力效果
            self._apply_gravity()
            
            # 发射星座弹幕
            self.shoot_cooldown -= 1
            if self.shoot_cooldown <= 0:
                self._shoot_constellation()
                self.shoot_cooldown = 8
            
            # 持续伤害
            if self.frame % 12 == 0:
                self._deal_damage()
            
            # 更新螺旋臂粒子
            self._update_spiral_arms()
        
        # 阶段3: 减速消失 (210-240帧)
        if self.frame > 210:
            self.spin_speed = max(1, self.spin_speed - 1.5)
        
        # 更新环绕星体
        for star in self.orbit_stars:
            star['angle'] += star['speed'] + self.spin_speed * 0.1
            star['radius'] += math.sin(self.frame * 0.1 + star['phase']) * 0.5
        
        # 更新粒子
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
        
        # 更新吸收尾迹
        for trail in self.absorbed_trails[:]:
            trail['progress'] += 0.08
            if trail['progress'] >= 1:
                self.absorbed_trails.remove(trail)
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        if self.frame >= self.max_frames:
            self.kill()
            return
        
        self._render()
    
    def _update_spiral_arms(self):
        """更新螺旋臂粒子"""
        for arm in self.spiral_arms:
            # 生成新粒子
            if self.frame % 3 == 0:
                for dist in range(50, 200, 30):
                    angle = math.radians(arm['base_angle'] + self.angle + dist * 0.5)
                    arm['particles'].append({
                        'dist': dist,
                        'angle_offset': dist * 0.5,
                        'life': 40,
                        'size': max(2, 6 - dist // 40),
                    })
            
            # 更新粒子
            for p in arm['particles'][:]:
                p['life'] -= 1
                p['dist'] -= 1
                if p['life'] <= 0 or p['dist'] < 20:
                    arm['particles'].remove(p)
    
    def _apply_gravity(self):
        """对周围敌人施加引力"""
        for mob in mobs:
            dx = self.float_x - mob.rect.centerx
            dy = self.float_y - mob.rect.centery
            dist = max(1, math.hypot(dx, dy))
            
            if dist < self.gravity_radius:
                # 引力强度随距离衰减
                force = self.gravity_strength * (1 - dist / self.gravity_radius)
                if hasattr(mob, 'rect'):
                    mob.rect.x += int(dx / dist * force * 12)
                    mob.rect.y += int(dy / dist * force * 12)
                    
                    # 生成吸收尾迹
                    if self.frame % 8 == 0:
                        self.absorbed_trails.append({
                            'start_x': mob.rect.centerx,
                            'start_y': mob.rect.centery,
                            'progress': 0,
                        })
    
    def _shoot_constellation(self):
        """发射星座弹幕"""
        num_bullets = 12
        for i in range(num_bullets):
            angle = (360 / num_bullets) * i + self.angle
            ConstellationBullet(self.float_x, self.float_y, angle, 
                              self.damage * 0.35, style=self.style)
    
    def _deal_damage(self):
        """对周围敌人造成伤害"""
        for mob in mobs:
            dx = self.float_x - mob.rect.centerx
            dy = self.float_y - mob.rect.centery
            dist = math.hypot(dx, dy)
            
            if dist < self.gravity_radius and hasattr(mob, 'take_damage'):
                mob.take_damage(self.damage * 0.25)
                # 命中粒子
                for _ in range(3):
                    self.particles.append({
                        'x': mob.rect.centerx,
                        'y': mob.rect.centery,
                        'vx': random.uniform(-6, 6),
                        'vy': random.uniform(-6, 6),
                        'life': 25,
                        'size': random.randint(4, 8),
                    })
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 250, 250
        
        # 绘制吸收尾迹
        for trail in self.absorbed_trails:
            t = trail['progress']
            # 计算当前位置
            sx = trail['start_x'] - self.float_x + cx
            sy = trail['start_y'] - self.float_y + cy
            ex, ey = cx, cy
            
            cur_x = sx + (ex - sx) * t
            cur_y = sy + (ey - sy) * t
            alpha = int(150 * (1 - t))
            
            pygame.draw.line(self.image, (*self.theme["cosmic_cyan"], alpha),
                           (int(sx), int(sy)), (int(cur_x), int(cur_y)), 2)
        
        # 绘制多层引力场
        for layer in range(5):
            layer_radius = int(self.gravity_radius * (1 - layer * 0.15))
            gravity_alpha = int(15 + 15 * math.sin(self.frame * 0.1 + layer))
            pygame.draw.circle(self.image, (*self.theme["cosmic_cyan"], gravity_alpha),
                             (cx, cy), layer_radius, 2)
        
        # 绘制螺旋臂
        for arm in self.spiral_arms:
            for p in arm['particles']:
                angle = math.radians(arm['base_angle'] + self.angle + p['angle_offset'])
                px = cx + int(math.cos(angle) * p['dist'])
                py = cy + int(math.sin(angle) * p['dist'])
                alpha = int(180 * (p['life'] / 40))
                size = p['size']
                
                pygame.draw.circle(self.image, (*self.theme["nebula_purple"], alpha),
                                 (px, py), size + 2)
                pygame.draw.circle(self.image, (*self.theme["star_glow"], alpha),
                                 (px, py), size)
        
        # 绘制环绕星体
        for star in self.orbit_stars:
            angle = math.radians(star['angle'])
            sx = cx + int(math.cos(angle) * star['radius'])
            sy = cy + int(math.sin(angle) * star['radius'])
            
            pulse = 0.7 + 0.3 * math.sin(self.frame * 0.15 + star['phase'])
            size = int(star['size'] * pulse)
            
            pygame.draw.circle(self.image, (*self.theme["star_glow"], 200), (sx, sy), size + 3)
            pygame.draw.circle(self.image, (*self.theme["lavender"], 255), (sx, sy), size)
            
            # 星体尾迹
            for t in range(1, 4):
                trail_angle = math.radians(star['angle'] - t * 8)
                tx = cx + int(math.cos(trail_angle) * star['radius'])
                ty = cy + int(math.sin(trail_angle) * star['radius'])
                trail_alpha = 150 // t
                trail_size = max(1, size - t)
                pygame.draw.circle(self.image, (*self.theme["cosmic_cyan"], trail_alpha),
                                 (tx, ty), trail_size)
        
        # 剪刀刃部 - 更大更华丽
        blade_length = 180
        blade_width = 40
        
        # 上刃
        angle_rad = math.radians(self.angle)
        x1 = cx + int(math.cos(angle_rad) * blade_length)
        y1 = cy + int(math.sin(angle_rad) * blade_length)
        
        # 刃光晕
        pygame.draw.line(self.image, (*self.theme["cosmic_cyan"], 100),
                       (cx, cy), (x1, y1), blade_width + 20)
        pygame.draw.line(self.image, (*self.theme["midnight_blue"], 220),
                       (cx, cy), (x1, y1), blade_width)
        pygame.draw.line(self.image, (*self.theme["nebula_purple"], 255),
                       (cx, cy), (x1, y1), blade_width // 2)
        pygame.draw.line(self.image, (*self.theme["star_glow"], 255),
                       (cx, cy), (x1, y1), blade_width // 4)
        
        # 下刃（180度对向）
        angle_rad2 = math.radians(self.angle + 180)
        x2 = cx + int(math.cos(angle_rad2) * blade_length)
        y2 = cy + int(math.sin(angle_rad2) * blade_length)
        
        pygame.draw.line(self.image, (*self.theme["cosmic_cyan"], 100),
                       (cx, cy), (x2, y2), blade_width + 20)
        pygame.draw.line(self.image, (*self.theme["midnight_blue"], 220),
                       (cx, cy), (x2, y2), blade_width)
        pygame.draw.line(self.image, (*self.theme["nebula_purple"], 255),
                       (cx, cy), (x2, y2), blade_width // 2)
        pygame.draw.line(self.image, (*self.theme["star_glow"], 255),
                       (cx, cy), (x2, y2), blade_width // 4)
        
        # 中心星核 - 多层发光
        for i in range(4):
            core_size = 20 - i * 4
            core_alpha = 150 + i * 25
            pygame.draw.circle(self.image, (*self.theme["star_glow"], core_alpha),
                             (cx, cy), core_size)
        pygame.draw.circle(self.image, self.theme["lavender"], (cx, cy), 8)
        
        # 绘制粒子
        for p in self.particles:
            progress = p['life'] / 25
            alpha = int(200 * progress)
            size = int(p['size'] * progress)
            if size > 0:
                pygame.draw.circle(self.image, (*self.theme["star_glow"], alpha),
                                 (int(p['x'] - self.float_x + cx), 
                                  int(p['y'] - self.float_y + cy)), size)


# ==================== C键 - 苍穹撕裂 (The Big Rip) ====================
class BigRipSkill(pygame.sprite.Sprite):
    """
    C键最终绝招 - 苍穹撕裂
    机体化作占据屏幕80%的光之巨剪
    强行将屏幕从中间"剪"开，裂缝中喷涌出星体毁灭一切
    【超级视觉增强版】
    """
    
    def __init__(self, player_x, player_y, damage, style="default"):
        super().__init__()
        self.player_x = player_x
        self.player_y = player_y
        self.damage = damage
        self.style = style
        self.theme = get_theme(style)
        
        self.frame = 0
        self.max_frames = 300  # 5秒技能
        
        # 剪刀刃的位置
        self.upper_blade_angle = -45  # 上刃角度
        self.lower_blade_angle = 45   # 下刃角度
        
        # 裂缝
        self.rip_width = 0
        self.rip_max_width = 200  # 更宽的裂缝
        
        # 星体喷涌
        self.stars = []
        
        # 增强特效
        self.screen_flash = 0
        self.blade_sparks = []  # 刃尖火花
        self.void_tendrils = []  # 虚空触须
        self.cosmic_debris = []  # 宇宙碎片
        self.energy_waves = []  # 能量波
        self.nebula_clouds = []  # 星云云雾
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        
        # 屏幕闪光衰减
        self.screen_flash = max(0, self.screen_flash - 8)
        
        # 阶段1: 巨剪形成 (0-60帧) - 伴随能量聚集
        if self.frame <= 60:
            progress = self.frame / 60
            self.upper_blade_angle = -45 + progress * 45  # 从-45度到0度
            self.lower_blade_angle = 45 - progress * 45   # 从45度到0度
            
            # 刃尖能量聚集火花
            if self.frame % 3 == 0:
                self._spawn_blade_sparks()
            
            # 能量波纹
            if self.frame % 15 == 0:
                self.energy_waves.append({
                    'radius': 0,
                    'max_radius': 300,
                    'life': 40,
                })
        
        # 阶段2: 剪开屏幕 (60-120帧) - 剧烈撕裂
        elif 60 < self.frame <= 120:
            progress = (self.frame - 60) / 60
            self.rip_width = int(self.rip_max_width * progress)
            
            # 屏幕震动闪光
            if self.frame == 61:
                self.screen_flash = 255
            
            # 每帧造成大量伤害
            if self.frame % 5 == 0:
                self._deal_massive_damage()
            
            # 生成虚空触须
            if self.frame % 8 == 0:
                self._spawn_void_tendrils()
            
            # 生成宇宙碎片
            if self.frame % 4 == 0:
                self._spawn_cosmic_debris()
        
        # 阶段3: 星体喷涌 (120-240帧) - 海量星体
        elif 120 < self.frame <= 240:
            # 生成星体（大幅增加）
            if self.frame % 2 == 0:
                self._spawn_stars()
            
            # 生成星云云雾
            if self.frame % 10 == 0:
                self._spawn_nebula_cloud()
            
            # 持续造成伤害
            if self.frame % 10 == 0:
                for mob in mobs:
                    if hasattr(mob, 'take_damage'):
                        mob.take_damage(self.damage * 0.3)
        
        # 阶段4: 愈合 (240-300帧)
        elif self.frame > 240:
            progress = (self.frame - 240) / 60
            self.rip_width = int(self.rip_max_width * (1 - progress))
        
        # 更新所有特效
        self._update_effects()
        
        if self.frame >= self.max_frames:
            self.kill()
            return
        
        self._render()
    
    def _spawn_blade_sparks(self):
        """生成刃尖火花"""
        cx = WIDTH // 2
        cy = HEIGHT // 2
        blade_length = int(HEIGHT * 0.8)
        
        for blade_angle in [self.upper_blade_angle, self.lower_blade_angle]:
            rad = math.radians(blade_angle)
            tip_x = cx + int(math.cos(rad) * blade_length)
            tip_y = cy + int(math.sin(rad) * blade_length)
            
            for _ in range(5):
                self.blade_sparks.append({
                    'x': tip_x + random.randint(-20, 20),
                    'y': tip_y + random.randint(-20, 20),
                    'vx': random.uniform(-8, 8),
                    'vy': random.uniform(-8, 8),
                    'life': random.randint(15, 30),
                    'size': random.randint(3, 8),
                })
    
    def _spawn_void_tendrils(self):
        """生成虚空触须"""
        cx = WIDTH // 2
        for _ in range(3):
            self.void_tendrils.append({
                'x': cx + random.randint(-self.rip_width, self.rip_width),
                'y': random.randint(0, HEIGHT),
                'length': random.randint(50, 150),
                'angle': random.uniform(-60, 60),
                'wave_phase': random.uniform(0, 6.28),
                'life': 60,
                'side': random.choice([-1, 1]),
            })
    
    def _spawn_cosmic_debris(self):
        """生成宇宙碎片"""
        cx = WIDTH // 2
        for _ in range(3):
            side = random.choice([-1, 1])
            self.cosmic_debris.append({
                'x': cx + side * self.rip_width,
                'y': random.randint(0, HEIGHT),
                'vx': side * random.uniform(3, 10),
                'vy': random.uniform(-3, 3),
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-10, 10),
                'size': random.randint(8, 25),
                'life': random.randint(40, 80),
                'color_type': random.choice(['purple', 'cyan', 'glow']),
            })
    
    def _spawn_nebula_cloud(self):
        """生成星云云雾"""
        cx = WIDTH // 2
        self.nebula_clouds.append({
            'x': cx + random.randint(-self.rip_width, self.rip_width),
            'y': random.randint(0, HEIGHT),
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-2, 2),
            'size': random.randint(40, 100),
            'life': random.randint(60, 120),
            'alpha': random.randint(30, 80),
        })
    
    def _deal_massive_damage(self):
        """对全屏敌人造成巨额伤害"""
        for mob in mobs:
            if hasattr(mob, 'take_damage'):
                mob.take_damage(self.damage * 1.8)
                # 命中特效
                for _ in range(8):
                    self.blade_sparks.append({
                        'x': mob.rect.centerx,
                        'y': mob.rect.centery,
                        'vx': random.uniform(-12, 12),
                        'vy': random.uniform(-12, 12),
                        'life': 25,
                        'size': random.randint(5, 12),
                    })
    
    def _spawn_stars(self):
        """从裂缝中喷涌星体"""
        cx = WIDTH // 2
        for _ in range(8):  # 增加数量
            x = cx + random.randint(-self.rip_width, self.rip_width)
            y = random.randint(0, HEIGHT)
            
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(6, 18)
            
            self.stars.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.randint(50, 90),
                'size': random.randint(8, 30),
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-8, 8),
                'is_supernova': random.random() < 0.1,  # 10%概率是超新星
            })
    
    def _update_effects(self):
        """更新所有特效"""
        # 更新星体
        for star in self.stars[:]:
            star['x'] += star['vx']
            star['y'] += star['vy']
            star['life'] -= 1
            star['rotation'] += star['rot_speed']
            
            # 碰撞检测
            for mob in mobs:
                if hasattr(mob, 'rect'):
                    dist = math.hypot(mob.rect.centerx - star['x'], 
                                    mob.rect.centery - star['y'])
                    if dist < 40 and hasattr(mob, 'take_damage'):
                        dmg = self.damage * (0.8 if star['is_supernova'] else 0.4)
                        mob.take_damage(dmg)
            
            if star['life'] <= 0:
                self.stars.remove(star)
        
        # 更新刃尖火花
        for spark in self.blade_sparks[:]:
            spark['x'] += spark['vx']
            spark['y'] += spark['vy']
            spark['vx'] *= 0.95
            spark['vy'] *= 0.95
            spark['life'] -= 1
            if spark['life'] <= 0:
                self.blade_sparks.remove(spark)
        
        # 更新虚空触须
        for tendril in self.void_tendrils[:]:
            tendril['life'] -= 1
            tendril['wave_phase'] += 0.2
            if tendril['life'] <= 0:
                self.void_tendrils.remove(tendril)
        
        # 更新宇宙碎片
        for debris in self.cosmic_debris[:]:
            debris['x'] += debris['vx']
            debris['y'] += debris['vy']
            debris['rotation'] += debris['rot_speed']
            debris['life'] -= 1
            if debris['life'] <= 0:
                self.cosmic_debris.remove(debris)
        
        # 更新星云云雾
        for cloud in self.nebula_clouds[:]:
            cloud['x'] += cloud['vx']
            cloud['y'] += cloud['vy']
            cloud['life'] -= 1
            cloud['size'] += 0.5  # 慢慢扩散
            if cloud['life'] <= 0:
                self.nebula_clouds.remove(cloud)
        
        # 更新能量波
        for wave in self.energy_waves[:]:
            wave['radius'] += 8
            wave['life'] -= 1
            if wave['life'] <= 0 or wave['radius'] > wave['max_radius']:
                self.energy_waves.remove(wave)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        
        cx = WIDTH // 2
        cy = HEIGHT // 2
        blade_length = int(HEIGHT * 0.85)
        
        # 屏幕闪光
        if self.screen_flash > 0:
            flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((*self.theme["star_glow"], self.screen_flash))
            self.image.blit(flash_surf, (0, 0))
        
        # 绘制能量波
        for wave in self.energy_waves:
            alpha = int(100 * (wave['life'] / 40))
            pygame.draw.circle(self.image, (*self.theme["cosmic_cyan"], alpha),
                             (cx, cy), int(wave['radius']), 3)
        
        # 绘制星云云雾（背景层）
        for cloud in self.nebula_clouds:
            alpha = int(cloud['alpha'] * (cloud['life'] / 120))
            size = int(cloud['size'])
            # 多层叠加营造云雾感
            for i in range(3):
                layer_size = size - i * 15
                if layer_size > 0:
                    layer_alpha = alpha // (i + 1)
                    pygame.draw.circle(self.image, (*self.theme["nebula_purple"], layer_alpha),
                                     (int(cloud['x']), int(cloud['y'])), layer_size)
        
        # 绘制上刃（多层渐变）
        upper_rad = math.radians(self.upper_blade_angle)
        ux = cx + int(math.cos(upper_rad) * blade_length)
        uy = cy + int(math.sin(upper_rad) * blade_length)
        
        # 刃光晕层
        for glow in range(5):
            glow_width = 100 - glow * 15
            glow_alpha = 50 + glow * 20
            pygame.draw.line(self.image, (*self.theme["cosmic_cyan"], glow_alpha),
                           (cx, cy), (ux, uy), glow_width)
        pygame.draw.line(self.image, (*self.theme["midnight_blue"], 240),
                       (cx, cy), (ux, uy), 60)
        pygame.draw.line(self.image, (*self.theme["nebula_purple"], 255),
                       (cx, cy), (ux, uy), 35)
        pygame.draw.line(self.image, (*self.theme["lavender"], 255),
                       (cx, cy), (ux, uy), 15)
        pygame.draw.line(self.image, (*self.theme["star_glow"], 255),
                       (cx, cy), (ux, uy), 5)
        
        # 绘制下刃
        lower_rad = math.radians(self.lower_blade_angle)
        lx = cx + int(math.cos(lower_rad) * blade_length)
        ly = cy + int(math.sin(lower_rad) * blade_length)
        
        for glow in range(5):
            glow_width = 100 - glow * 15
            glow_alpha = 50 + glow * 20
            pygame.draw.line(self.image, (*self.theme["cosmic_cyan"], glow_alpha),
                           (cx, cy), (lx, ly), glow_width)
        pygame.draw.line(self.image, (*self.theme["midnight_blue"], 240),
                       (cx, cy), (lx, ly), 60)
        pygame.draw.line(self.image, (*self.theme["nebula_purple"], 255),
                       (cx, cy), (lx, ly), 35)
        pygame.draw.line(self.image, (*self.theme["lavender"], 255),
                       (cx, cy), (lx, ly), 15)
        pygame.draw.line(self.image, (*self.theme["star_glow"], 255),
                       (cx, cy), (lx, ly), 5)
        
        # 刃尖光芒
        for tip_x, tip_y in [(ux, uy), (lx, ly)]:
            for i in range(4):
                tip_size = 20 - i * 4
                tip_alpha = 200 - i * 40
                pygame.draw.circle(self.image, (*self.theme["star_glow"], tip_alpha),
                                 (tip_x, tip_y), tip_size)
        
        # 绘制裂缝
        if self.rip_width > 0:
            # 虚空裂缝主体
            pygame.draw.rect(self.image, (*self.theme["void_black"], 255),
                           (cx - self.rip_width, 0, self.rip_width * 2, HEIGHT))
            
            # 裂缝内部星空
            for i in range(0, HEIGHT, 8):
                for j in range(-self.rip_width + 10, self.rip_width - 10, 15):
                    if random.random() < 0.3:
                        star_x = cx + j
                        star_y = i
                        star_alpha = int(100 + 100 * math.sin(self.frame * 0.2 + i * 0.1))
                        star_size = random.randint(1, 3)
                        pygame.draw.circle(self.image, (*self.theme["star_glow"], star_alpha),
                                         (star_x, star_y), star_size)
            
            # 裂缝边缘锯齿光效
            for i in range(0, HEIGHT, 6):
                jag_offset = int(math.sin(i * 0.15 + self.frame * 0.2) * 15)
                glow_alpha = int(220 * (0.6 + 0.4 * math.sin(self.frame * 0.15 + i * 0.1)))
                
                # 左边缘
                pygame.draw.circle(self.image, (*self.theme["cosmic_cyan"], glow_alpha),
                                 (cx - self.rip_width + jag_offset, i), 6)
                pygame.draw.circle(self.image, (*self.theme["lavender"], glow_alpha),
                                 (cx - self.rip_width + jag_offset, i), 3)
                
                # 右边缘
                pygame.draw.circle(self.image, (*self.theme["cosmic_cyan"], glow_alpha),
                                 (cx + self.rip_width - jag_offset, i), 6)
                pygame.draw.circle(self.image, (*self.theme["lavender"], glow_alpha),
                                 (cx + self.rip_width - jag_offset, i), 3)
        
        # 绘制虚空触须
        for tendril in self.void_tendrils:
            alpha = int(180 * (tendril['life'] / 60))
            start_x = tendril['x']
            start_y = tendril['y']
            
            # 波动的触须
            points = [(start_x, start_y)]
            for seg in range(1, 8):
                wave = math.sin(tendril['wave_phase'] + seg * 0.8) * 20
                seg_x = start_x + tendril['side'] * seg * 20 + wave
                seg_y = start_y + math.sin(tendril['angle'] * 0.0175 + seg) * 15
                points.append((int(seg_x), int(seg_y)))
            
            if len(points) >= 2:
                pygame.draw.lines(self.image, (*self.theme["nebula_purple"], alpha),
                                False, points, 4)
                pygame.draw.lines(self.image, (*self.theme["cosmic_cyan"], alpha // 2),
                                False, points, 2)
        
        # 绘制宇宙碎片
        for debris in self.cosmic_debris:
            alpha = int(220 * (debris['life'] / 80))
            size = debris['size']
            
            if debris['color_type'] == 'purple':
                color = self.theme["nebula_purple"]
            elif debris['color_type'] == 'cyan':
                color = self.theme["cosmic_cyan"]
            else:
                color = self.theme["star_glow"]
            
            # 旋转的多边形碎片
            rad = math.radians(debris['rotation'])
            points = []
            for i in range(5):
                angle = rad + i * 1.257
                r = size * (0.6 if i % 2 else 1.0)
                px = debris['x'] + math.cos(angle) * r
                py = debris['y'] + math.sin(angle) * r
                points.append((int(px), int(py)))
            
            pygame.draw.polygon(self.image, (*color, alpha), points)
        
        # 绘制刃尖火花
        for spark in self.blade_sparks:
            progress = spark['life'] / 30
            alpha = int(255 * progress)
            size = int(spark['size'] * progress)
            if size > 0:
                pygame.draw.circle(self.image, (*self.theme["star_glow"], alpha),
                                 (int(spark['x']), int(spark['y'])), size)
        
        # 绘制喷涌的星体
        for star in self.stars:
            progress = star['life'] / 90
            alpha = int(255 * min(1.0, progress * 1.5))
            size = int(star['size'] * (0.5 + 0.5 * progress))
            
            if star['is_supernova']:
                # 超新星效果 - 更亮更大
                for i in range(4):
                    nova_size = size + i * 8
                    nova_alpha = alpha // (i + 1)
                    pygame.draw.circle(self.image, (*self.theme["star_glow"], nova_alpha),
                                     (int(star['x']), int(star['y'])), nova_size)
                pygame.draw.circle(self.image, self.theme["lavender"],
                                 (int(star['x']), int(star['y'])), size // 2)
            else:
                # 普通星体
                pygame.draw.circle(self.image, (*self.theme["nebula_purple"], alpha // 2),
                                 (int(star['x']), int(star['y'])), size + 5)
                pygame.draw.circle(self.image, (*self.theme["star_glow"], alpha),
                                 (int(star['x']), int(star['y'])), size)
                pygame.draw.circle(self.image, (*self.theme["lavender"], alpha),
                                 (int(star['x']), int(star['y'])), size // 2)
        
        # 中心剪刀轴心 - 巨大光球
        for i in range(6):
            core_size = 40 - i * 6
            core_alpha = 100 + i * 25
            pygame.draw.circle(self.image, (*self.theme["star_glow"], core_alpha),
                             (cx, cy), core_size)
        pygame.draw.circle(self.image, self.theme["lavender"], (cx, cy), 15)


# ==================== 星座弹幕 (Constellation Bullet) ====================
class ConstellationBullet(pygame.sprite.Sprite):
    """星座弹幕 - 从星系陷阱发射的星星弹幕"""
    
    def __init__(self, x, y, angle, damage, style="default"):
        super().__init__()
        self.float_x = float(x)
        self.float_y = float(y)
        self.angle = angle
        self.damage = damage
        self.style = style
        self.theme = get_theme(style)
        
        # 标准子弹属性
        self.color = self.theme["star_glow"]
        self.piercing = 0
        self.is_enemy = False
        self.b_type = "galaxia_constellation"
        
        self.speed = 8
        self.vx = math.cos(math.radians(angle)) * self.speed
        self.vy = math.sin(math.radians(angle)) * self.speed
        
        self.trail = []
        self.rotation = 0
        
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        self.float_x += self.vx
        self.float_y += self.vy
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 记录轨迹
        self.trail.append((self.float_x, self.float_y))
        if len(self.trail) > 8:
            self.trail.pop(0)
        
        self.rotation += 10
        
        # 边界检查
        if (self.float_x < -50 or self.float_x > WIDTH + 50 or
            self.float_y < -50 or self.float_y > HEIGHT + 50):
            self.kill()
            return
        
        # 碰撞检测
        for mob in mobs:
            if hasattr(mob, 'rect') and self.rect.colliderect(mob.rect):
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage)
                self.kill()
                return
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 15, 15
        
        # 绘制轨迹
        for i, (tx, ty) in enumerate(self.trail):
            trail_x = int(tx - self.float_x + cx)
            trail_y = int(ty - self.float_y + cy)
            progress = i / len(self.trail)
            alpha = int(100 * progress)
            size = int(4 * progress)
            if size > 0:
                pygame.draw.circle(self.image, (*self.theme["cosmic_cyan"], alpha),
                                 (trail_x, trail_y), size)
        
        # 五角星
        points = []
        for i in range(5):
            angle = math.radians(self.rotation + i * 72)
            px = cx + int(math.cos(angle) * 10)
            py = cy + int(math.sin(angle) * 10)
            points.append((px, py))
            
            # 内凹点
            angle2 = math.radians(self.rotation + i * 72 + 36)
            px2 = cx + int(math.cos(angle2) * 5)
            py2 = cy + int(math.sin(angle2) * 5)
            points.append((px2, py2))
        
        pygame.draw.polygon(self.image, self.theme["star_glow"], points)
        pygame.draw.circle(self.image, self.theme["lavender"], (cx, cy), 4)


# ==================== 裂变星体 (Split Star) ====================
class SplitStar(pygame.sprite.Sprite):
    """裂变星体 - 每次剪切命中产生的追踪星星"""
    
    def __init__(self, x, y, target, damage, style="default"):
        super().__init__()
        self.float_x = float(x)
        self.float_y = float(y)
        self.target = target
        self.damage = damage
        self.style = style
        self.theme = get_theme(style)
        
        # 标准子弹属性
        self.color = self.theme["nebula_purple"]
        self.piercing = 0
        self.is_enemy = False
        self.b_type = "galaxia_split_star"
        
        self.speed = 6
        self.lifetime = 120
        
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 追踪目标
        if self.target and hasattr(self.target, 'alive') and self.target.alive():
            dx = self.target.rect.centerx - self.float_x
            dy = self.target.rect.centery - self.float_y
            dist = max(1, math.hypot(dx, dy))
            
            self.float_x += (dx / dist) * self.speed
            self.float_y += (dy / dist) * self.speed
        else:
            # 寻找新目标
            self.target = None
            closest_dist = float('inf')
            for mob in mobs:
                if hasattr(mob, 'rect'):
                    d = math.hypot(mob.rect.centerx - self.float_x,
                                  mob.rect.centery - self.float_y)
                    if d < closest_dist:
                        closest_dist = d
                        self.target = mob
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 碰撞检测
        for mob in mobs:
            if hasattr(mob, 'rect') and self.rect.colliderect(mob.rect):
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage)
                self.kill()
                return
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 10, 10
        
        pulse = 0.7 + 0.3 * math.sin(self.lifetime * 0.2)
        size = int(8 * pulse)
        
        pygame.draw.circle(self.image, (*self.theme["nebula_purple"], 150),
                         (cx, cy), size + 3)
        pygame.draw.circle(self.image, self.theme["star_glow"], (cx, cy), size)
        pygame.draw.circle(self.image, self.theme["lavender"], (cx, cy), size // 2)


# ==================== 宇宙剪刃 (Cosmic Scissor Bullet) ====================
class CosmicScissorBullet(pygame.sprite.Sprite):
    """
    GALAXIA主武器 - 宇宙剪刃
    剪刀形状的星能弹，高速飞行，命中时产生小型切割效果
    """
    
    def __init__(self, x, y, damage, angle=-90, owner=None, style="default"):
        super().__init__()
        self.float_x = float(x)
        self.float_y = float(y)
        self.damage = damage
        self.angle = angle
        self.owner = owner
        self.style = style
        self.theme = get_theme(style)
        
        # 标准子弹属性
        self.color = self.theme["nebula_purple"]
        self.piercing = 1  # 可穿透1个敌人
        self.is_enemy = False
        self.b_type = "galaxia_scissor"
        
        self.speed = 14
        self.lifetime = 90
        self.spin = 0  # 旋转角度
        
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        # 计算速度分量
        rad = math.radians(angle)
        self.vx = math.cos(rad) * self.speed
        self.vy = math.sin(rad) * self.speed
        
        all_sprites.add(self)
        bullets.add(self)
        
        self._render()
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 移动
        self.float_x += self.vx
        self.float_y += self.vy
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 出屏检测
        if self.rect.bottom < -50 or self.rect.top > HEIGHT + 50:
            self.kill()
            return
        if self.rect.right < -50 or self.rect.left > WIDTH + 50:
            self.kill()
            return
        
        # 旋转
        self.spin += 15
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 12, 12
        
        # 绘制剪刀形状（两个交叉的刀刃）
        rad = math.radians(self.spin)
        
        # 刀刃1
        blade1_points = []
        for i in range(4):
            angles = [rad, rad + 0.3, rad + 0.15, rad - 0.15]
            lengths = [10, 3, 6, 6]
            bx = cx + int(math.cos(angles[i]) * lengths[i])
            by = cy + int(math.sin(angles[i]) * lengths[i])
            blade1_points.append((bx, by))
        if len(blade1_points) >= 3:
            pygame.draw.polygon(self.image, self.theme["cosmic_cyan"], blade1_points)
        
        # 刀刃2（对称）
        blade2_points = []
        for i in range(4):
            angles = [rad + 3.14, rad + 3.14 + 0.3, rad + 3.14 + 0.15, rad + 3.14 - 0.15]
            lengths = [10, 3, 6, 6]
            bx = cx + int(math.cos(angles[i]) * lengths[i])
            by = cy + int(math.sin(angles[i]) * lengths[i])
            blade2_points.append((bx, by))
        if len(blade2_points) >= 3:
            pygame.draw.polygon(self.image, self.theme["nebula_purple"], blade2_points)
        
        # 中心星光
        pygame.draw.circle(self.image, self.theme["star_glow"], (cx, cy), 4)
        pygame.draw.circle(self.image, self.theme["lavender"], (cx, cy), 2)


# ==================== 导出列表 ====================
__all__ = [
    # 主要技能
    "DimensionalSlashSkill",   # F键 - 次元斩
    "GalaxyTrapSkill",         # G键 - 星系陷阱
    "BigRipSkill",             # C键 - 苍穹撕裂
    # 攻击弹幕
    "CosmicScissorBullet",     # 主武器 - 宇宙剪刃
    "ConstellationBullet",     # 星座弹幕
    "SplitStar",               # 裂变星体
    # 辅助函数
    "get_theme",               # 主题获取函数
]
