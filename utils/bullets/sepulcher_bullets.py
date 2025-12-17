# -*- coding: utf-8 -*-
"""
至尊灾厄·终末王座 (SEPULCHER) 大招技能系统
包含三个终极技能的实现，以及机体辅助系统
"""
import pygame
import math
import random

# 导入游戏核心
from config import WIDTH, HEIGHT, all_sprites, bullets, mobs, enemy_bullets

# ==================== 主题颜色获取 ====================
SEPULCHER_THEMES = {
    "default": {
        "core": (220, 20, 60), "hellfire": (255, 69, 0), "skull": (180, 30, 30),
        "skull_dark": (120, 15, 15), "halo": (255, 50, 50), "eye": (255, 0, 0), 
        "rune": (139, 0, 0), "magic": (255, 100, 80), "obsidian": (20, 20, 25),
    },
    "brimstone": {
        "core": (255, 100, 0), "hellfire": (255, 150, 50), "skull": (220, 100, 50),
        "skull_dark": (160, 60, 30), "halo": (255, 120, 30), "eye": (255, 80, 0), 
        "rune": (200, 80, 0), "magic": (255, 180, 100), "obsidian": (50, 30, 15),
    },
    "witch": {
        "core": (180, 50, 200), "hellfire": (220, 100, 255), "skull": (150, 60, 180),
        "skull_dark": (100, 30, 120), "halo": (200, 80, 255), "eye": (180, 0, 220), 
        "rune": (100, 30, 130), "magic": (200, 150, 255), "obsidian": (30, 18, 45),
    },
    "bloodmoon": {
        "core": (200, 0, 0), "hellfire": (255, 30, 30), "skull": (180, 20, 40),
        "skull_dark": (120, 10, 20), "halo": (255, 50, 80), "eye": (255, 0, 30), 
        "rune": (150, 0, 20), "magic": (255, 100, 120), "obsidian": (40, 10, 15),
    },
    "void": {
        "core": (100, 0, 150), "hellfire": (150, 50, 200), "skull": (80, 40, 120),
        "skull_dark": (50, 20, 80), "halo": (130, 80, 180), "eye": (100, 0, 180), 
        "rune": (60, 20, 100), "magic": (180, 120, 220), "obsidian": (15, 10, 30),
    },
    "shadow": {
        "core": (60, 60, 80), "hellfire": (100, 100, 120), "skull": (50, 50, 70),
        "skull_dark": (30, 30, 45), "halo": (80, 80, 100), "eye": (40, 40, 60), 
        "rune": (30, 30, 50), "magic": (120, 120, 150), "obsidian": (10, 10, 15),
    },
    "magma": {
        "core": (255, 80, 0), "hellfire": (255, 120, 30), "skull": (200, 60, 20),
        "skull_dark": (140, 40, 10), "halo": (255, 100, 50), "eye": (255, 50, 0), 
        "rune": (180, 40, 0), "magic": (255, 150, 80), "obsidian": (60, 20, 10),
    },
    "frost": {
        "core": (100, 200, 255), "hellfire": (150, 220, 255), "skull": (80, 180, 220),
        "skull_dark": (50, 120, 160), "halo": (120, 210, 255), "eye": (80, 200, 255), 
        "rune": (60, 150, 200), "magic": (180, 230, 255), "obsidian": (20, 30, 40),
    },
    "souleater": {
        "core": (0, 200, 100), "hellfire": (50, 255, 150), "skull": (30, 180, 100),
        "skull_dark": (15, 120, 60), "halo": (80, 230, 150), "eye": (0, 255, 120), 
        "rune": (0, 150, 80), "magic": (100, 255, 180), "obsidian": (10, 30, 20),
    },
    "apocalypse": {
        "core": (255, 200, 100), "hellfire": (255, 220, 150), "skull": (220, 180, 80),
        "skull_dark": (160, 130, 50), "halo": (255, 210, 120), "eye": (255, 200, 80), 
        "rune": (200, 150, 50), "magic": (255, 230, 180), "obsidian": (40, 35, 20),
    },
    "seraph": {
        "core": (255, 255, 200), "hellfire": (255, 255, 220), "skull": (230, 230, 180),
        "skull_dark": (180, 180, 140), "halo": (255, 255, 240), "eye": (255, 255, 200), 
        "rune": (200, 200, 150), "magic": (255, 255, 230), "obsidian": (40, 40, 35),
    },
    "quantum": {
        "core": (0, 255, 200), "hellfire": (50, 255, 220), "skull": (30, 200, 180),
        "skull_dark": (15, 140, 120), "halo": (80, 255, 230), "eye": (0, 255, 200), 
        "rune": (0, 180, 150), "magic": (100, 255, 230), "obsidian": (10, 25, 25),
    },
}

def get_theme(style):
    """获取主题颜色"""
    style_key = style.replace("sepulcher_", "") if style.startswith("sepulcher_") else style
    return SEPULCHER_THEMES.get(style_key, SEPULCHER_THEMES["default"])


# ==================== 屏幕闪烁效果 ====================
class ScreenFlash(pygame.sprite.Sprite):
    """全屏闪光效果"""
    def __init__(self, color, duration=20):
        super().__init__()
        self.color = color
        self.duration = duration
        self.frame = 0
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        if self.frame >= self.duration:
            self.kill()
            return
        alpha = int(200 * (1 - self.frame / self.duration))
        self.image.fill((*self.color[:3], alpha))


# ==================== F技能：狱火方阵 ====================
class InfernalBoxSkill(pygame.sprite.Sprite):
    """
    狱火方阵 - F技能
    四面火墙从屏幕边缘向中心收缩，同时释放骷髅在方阵内反弹绞杀敌人
    
    增强视觉效果：
    1. 火墙带有燃烧粒子和热浪扭曲
    2. 骷髅拖曳火焰轨迹
    3. 收缩时地面出现裂痕
    4. 最终收缩时巨大爆炸
    5. 符文魔法阵旋转
    6. 灾厄之眼注视效果
    """
    
    def __init__(self, owner, damage, style="default"):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.style = style
        self.theme = get_theme(style)
        
        self.frame = 0
        self.total_frame = 0
        
        # 阶段：预警 -> 展开 -> 收缩 -> 爆炸 -> 消散
        self.phase = 0
        self.phase_duration = [30, 45, 180, 60, 30]  # 0.5s, 0.75s, 3s, 1s, 0.5s
        
        # 火墙参数
        self.wall_thickness = 40
        self.walls = {
            'top': {'pos': -self.wall_thickness, 'target': 0},
            'bottom': {'pos': HEIGHT, 'target': HEIGHT - self.wall_thickness},
            'left': {'pos': -self.wall_thickness, 'target': 0},
            'right': {'pos': WIDTH, 'target': WIDTH - self.wall_thickness},
        }
        self.shrink_margin = 60  # 收缩到距离边缘60像素
        
        # 骷髅弹列表
        self.skulls = []
        self.skull_count = 8
        self.skull_spawn_timer = 0
        
        # 火焰粒子
        self.fire_particles = []
        
        # 地面裂痕
        self.ground_cracks = []
        
        # 符文魔法阵
        self.rune_angle = 0
        self.rune_symbols = []
        for i in range(12):
            angle = i * 30
            self.rune_symbols.append({
                'angle': angle,
                'pulse': random.random() * math.pi * 2
            })
        
        # 灾厄之眼
        self.eye_scale = 0
        self.eye_pulse = 0
        self.eye_target = None  # 注视目标
        
        # 热浪扭曲参数
        self.heat_wave_offset = 0
        
        # 爆炸参数
        self.explosion_radius = 0
        self.explosion_particles = []
        
        # 锁定玩家
        if owner:
            owner.invincible = True
            owner.skill_locked = True
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def update(self):
        self.total_frame += 1
        
        # 确定当前阶段
        phase_start = 0
        for i, dur in enumerate(self.phase_duration):
            if self.total_frame <= phase_start + dur:
                self.phase = i
                self.frame = self.total_frame - phase_start
                break
            phase_start += dur
        else:
            self._end_skill()
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        # 根据阶段更新
        if self.phase == 0:
            self._phase0_warning()
        elif self.phase == 1:
            self._phase1_deploy()
        elif self.phase == 2:
            self._phase2_shrink()
        elif self.phase == 3:
            self._phase3_explode()
        elif self.phase == 4:
            self._phase4_fade()
        
        # 更新通用元素
        self._update_fire_particles()
        self._update_skulls()
        self._update_ground_cracks()
        self._render_rune_circle()
        self._render_eye()
    
    def _phase0_warning(self):
        """预警阶段：屏幕边缘闪烁红光"""
        progress = self.frame / self.phase_duration[0]
        pulse = abs(math.sin(self.frame * 0.4))
        
        # 边缘警告
        edge_alpha = int(150 * pulse * progress)
        edge_width = int(20 + 15 * pulse)
        
        # 四边闪烁
        pygame.draw.rect(self.image, (*self.theme["hellfire"], edge_alpha), 
                        (0, 0, WIDTH, edge_width))
        pygame.draw.rect(self.image, (*self.theme["hellfire"], edge_alpha), 
                        (0, HEIGHT - edge_width, WIDTH, edge_width))
        pygame.draw.rect(self.image, (*self.theme["hellfire"], edge_alpha), 
                        (0, 0, edge_width, HEIGHT))
        pygame.draw.rect(self.image, (*self.theme["hellfire"], edge_alpha), 
                        (WIDTH - edge_width, 0, edge_width, HEIGHT))
        
        # 中心符文开始显现
        self.rune_angle += 2
        self.eye_scale = progress * 0.3
    
    def _phase1_deploy(self):
        """展开阶段：火墙从四边展开"""
        progress = self.frame / self.phase_duration[1]
        
        # 火墙展开动画
        for wall_name, wall in self.walls.items():
            if wall_name == 'top':
                wall['pos'] = -self.wall_thickness + (self.wall_thickness) * progress
            elif wall_name == 'bottom':
                wall['pos'] = HEIGHT - self.wall_thickness * progress
            elif wall_name == 'left':
                wall['pos'] = -self.wall_thickness + (self.wall_thickness) * progress
            elif wall_name == 'right':
                wall['pos'] = WIDTH - self.wall_thickness * progress
        
        self._render_fire_walls()
        
        # 符文旋转加速
        self.rune_angle += 3
        self.eye_scale = 0.3 + progress * 0.4
        
        # 生成地面裂痕
        if self.frame % 10 == 0:
            self._spawn_ground_crack()
    
    def _phase2_shrink(self):
        """收缩阶段：火墙向中心收缩，骷髅反弹"""
        progress = self.frame / self.phase_duration[2]
        
        # 计算收缩目标
        shrink_top = self.shrink_margin
        shrink_bottom = HEIGHT - self.shrink_margin - self.wall_thickness
        shrink_left = self.shrink_margin
        shrink_right = WIDTH - self.shrink_margin - self.wall_thickness
        
        # 平滑收缩（使用缓动函数）
        ease_progress = 1 - (1 - progress) ** 2
        
        self.walls['top']['pos'] = ease_progress * shrink_top
        self.walls['bottom']['pos'] = HEIGHT - self.wall_thickness - ease_progress * (HEIGHT - self.wall_thickness - shrink_bottom)
        self.walls['left']['pos'] = ease_progress * shrink_left
        self.walls['right']['pos'] = WIDTH - self.wall_thickness - ease_progress * (WIDTH - self.wall_thickness - shrink_right)
        
        self._render_fire_walls()
        
        # 生成骷髅
        self.skull_spawn_timer += 1
        if self.skull_spawn_timer >= 25 and len(self.skulls) < self.skull_count:
            self._spawn_skull()
            self.skull_spawn_timer = 0
        
        # 推挤敌人
        if self.frame % 3 == 0:
            self._push_enemies()
        
        # 伤害敌人（火墙接触）
        self._damage_enemies_in_walls()
        
        # 符文快速旋转
        self.rune_angle += 5
        self.eye_scale = 0.7 + 0.1 * math.sin(self.frame * 0.1)
        self.eye_pulse += 0.15
        
        # 生成更多裂痕
        if self.frame % 15 == 0:
            self._spawn_ground_crack()
        
        # 生成火焰粒子
        if self.frame % 2 == 0:
            self._spawn_fire_particles()
    
    def _phase3_explode(self):
        """爆炸阶段：方阵收缩到极限后爆炸"""
        progress = self.frame / self.phase_duration[3]
        
        if self.frame == 1:
            # 触发爆炸
            ScreenFlash(self.theme["hellfire"], 25)
            # 对所有敌人造成大伤害
            for mob in mobs:
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage * 2)
            # 生成爆炸粒子
            for _ in range(50):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(5, 15)
                self.explosion_particles.append({
                    'x': WIDTH // 2,
                    'y': HEIGHT // 2,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'life': 60,
                    'size': random.randint(8, 20),
                })
        
        # 爆炸扩散
        self.explosion_radius = int(400 * progress)
        exp_alpha = int(200 * (1 - progress))
        
        # 爆炸波
        if exp_alpha > 0:
            pygame.draw.circle(self.image, (*self.theme["hellfire"], exp_alpha),
                             (WIDTH // 2, HEIGHT // 2), self.explosion_radius, 8)
            pygame.draw.circle(self.image, (*self.theme["core"], exp_alpha),
                             (WIDTH // 2, HEIGHT // 2), int(self.explosion_radius * 0.7), 5)
            pygame.draw.circle(self.image, (255, 255, 200, exp_alpha),
                             (WIDTH // 2, HEIGHT // 2), int(self.explosion_radius * 0.4))
        
        # 更新爆炸粒子
        for p in self.explosion_particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vx'] *= 0.96
            p['vy'] *= 0.96
            p['life'] -= 1
            if p['life'] <= 0:
                self.explosion_particles.remove(p)
            else:
                alpha = int(255 * p['life'] / 60)
                pygame.draw.circle(self.image, (*self.theme["hellfire"], alpha),
                                 (int(p['x']), int(p['y'])), p['size'])
        
        # 灾厄之眼消散
        self.eye_scale = 0.8 * (1 - progress)
    
    def _phase4_fade(self):
        """消散阶段"""
        progress = self.frame / self.phase_duration[4]
        
        # 残余粒子
        for p in self.explosion_particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 2
            if p['life'] <= 0:
                self.explosion_particles.remove(p)
            else:
                alpha = int(150 * p['life'] / 60)
                pygame.draw.circle(self.image, (*self.theme["magic"], alpha),
                                 (int(p['x']), int(p['y'])), max(1, p['size'] - 5))
    
    def _render_fire_walls(self):
        """渲染火墙"""
        t = self.total_frame * 0.1
        
        # 热浪扭曲偏移
        self.heat_wave_offset = math.sin(t * 2) * 3
        
        # 顶部火墙
        top_y = int(self.walls['top']['pos'])
        self._draw_fire_wall_horizontal(0, top_y, WIDTH, self.wall_thickness, facing_down=True)
        
        # 底部火墙
        bottom_y = int(self.walls['bottom']['pos'])
        self._draw_fire_wall_horizontal(0, bottom_y, WIDTH, self.wall_thickness, facing_down=False)
        
        # 左侧火墙
        left_x = int(self.walls['left']['pos'])
        self._draw_fire_wall_vertical(left_x, 0, self.wall_thickness, HEIGHT, facing_right=True)
        
        # 右侧火墙
        right_x = int(self.walls['right']['pos'])
        self._draw_fire_wall_vertical(right_x, 0, self.wall_thickness, HEIGHT, facing_right=False)
        
        # 四角火焰旋涡
        corners = [
            (int(self.walls['left']['pos']) + self.wall_thickness, int(self.walls['top']['pos']) + self.wall_thickness),
            (int(self.walls['right']['pos']), int(self.walls['top']['pos']) + self.wall_thickness),
            (int(self.walls['left']['pos']) + self.wall_thickness, int(self.walls['bottom']['pos'])),
            (int(self.walls['right']['pos']), int(self.walls['bottom']['pos'])),
        ]
        for cx, cy in corners:
            self._draw_fire_vortex(cx, cy)
    
    def _draw_fire_wall_horizontal(self, x, y, width, height, facing_down):
        """绘制水平火墙"""
        if y < -height or y > HEIGHT:
            return
        
        # 基础火墙
        for i in range(3):
            layer_alpha = 180 - i * 40
            layer_y = y + (i * 3 if facing_down else -i * 3)
            pygame.draw.rect(self.image, (*self.theme["hellfire"], layer_alpha),
                           (x, layer_y, width, height - i * 6))
        
        # 火焰尖端
        flame_count = width // 20
        for i in range(flame_count):
            fx = x + i * 20 + 10 + math.sin(self.total_frame * 0.2 + i) * 5
            flame_height = 15 + math.sin(self.total_frame * 0.3 + i * 0.5) * 8
            if facing_down:
                fy = y + height
                points = [(fx, fy), (fx - 8, fy + flame_height), (fx + 8, fy + flame_height)]
            else:
                fy = y
                points = [(fx, fy), (fx - 8, fy - flame_height), (fx + 8, fy - flame_height)]
            pygame.draw.polygon(self.image, (*self.theme["core"], 200), points)
        
        # 亮边
        pygame.draw.rect(self.image, (*self.theme["magic"], 150),
                        (x, y if facing_down else y + height - 2, width, 2))
    
    def _draw_fire_wall_vertical(self, x, y, width, height, facing_right):
        """绘制垂直火墙"""
        if x < -width or x > WIDTH:
            return
        
        # 基础火墙
        for i in range(3):
            layer_alpha = 180 - i * 40
            layer_x = x + (i * 3 if facing_right else -i * 3)
            pygame.draw.rect(self.image, (*self.theme["hellfire"], layer_alpha),
                           (layer_x, y, width - i * 6, height))
        
        # 火焰尖端
        flame_count = height // 20
        for i in range(flame_count):
            fy = y + i * 20 + 10 + math.sin(self.total_frame * 0.2 + i) * 5
            flame_width = 15 + math.sin(self.total_frame * 0.3 + i * 0.5) * 8
            if facing_right:
                fx = x + width
                points = [(fx, fy), (fx + flame_width, fy - 8), (fx + flame_width, fy + 8)]
            else:
                fx = x
                points = [(fx, fy), (fx - flame_width, fy - 8), (fx - flame_width, fy + 8)]
            pygame.draw.polygon(self.image, (*self.theme["core"], 200), points)
        
        # 亮边
        pygame.draw.rect(self.image, (*self.theme["magic"], 150),
                        (x if facing_right else x + width - 2, y, 2, height))
    
    def _draw_fire_vortex(self, cx, cy):
        """绘制角落火焰旋涡"""
        for i in range(5):
            angle = self.total_frame * 0.1 + i * math.pi / 2.5
            r = 10 + i * 4
            vx = cx + int(math.cos(angle) * r)
            vy = cy + int(math.sin(angle) * r)
            size = 8 - i
            alpha = 180 - i * 30
            if size > 0 and alpha > 0:
                pygame.draw.circle(self.image, (*self.theme["core"], alpha), (vx, vy), size)
    
    def _spawn_skull(self):
        """生成骷髅弹"""
        # 在方阵内随机位置生成
        margin = self.shrink_margin + self.wall_thickness + 20
        x = random.randint(margin, WIDTH - margin)
        y = random.randint(margin, HEIGHT - margin)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(6, 10)
        
        self.skulls.append({
            'x': x, 'y': y,
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'rotation': 0,
            'trail': [],
            'life': 180,
        })
    
    def _update_skulls(self):
        """更新骷髅弹"""
        left_bound = int(self.walls['left']['pos']) + self.wall_thickness
        right_bound = int(self.walls['right']['pos'])
        top_bound = int(self.walls['top']['pos']) + self.wall_thickness
        bottom_bound = int(self.walls['bottom']['pos'])
        
        for skull in self.skulls[:]:
            # 移动
            skull['x'] += skull['vx']
            skull['y'] += skull['vy']
            skull['rotation'] += 8
            skull['life'] -= 1
            
            # 添加轨迹
            skull['trail'].append((skull['x'], skull['y']))
            if len(skull['trail']) > 15:
                skull['trail'].pop(0)
            
            # 边界反弹
            if skull['x'] < left_bound:
                skull['x'] = left_bound
                skull['vx'] = abs(skull['vx'])
            elif skull['x'] > right_bound:
                skull['x'] = right_bound
                skull['vx'] = -abs(skull['vx'])
            
            if skull['y'] < top_bound:
                skull['y'] = top_bound
                skull['vy'] = abs(skull['vy'])
            elif skull['y'] > bottom_bound:
                skull['y'] = bottom_bound
                skull['vy'] = -abs(skull['vy'])
            
            # 碰撞敌人
            for mob in mobs:
                if math.hypot(mob.rect.centerx - skull['x'], mob.rect.centery - skull['y']) < 30:
                    if hasattr(mob, 'take_damage'):
                        mob.take_damage(self.damage * 0.3)
            
            # 移除过期骷髅
            if skull['life'] <= 0:
                self.skulls.remove(skull)
                continue
            
            # 绘制轨迹
            for i, (tx, ty) in enumerate(skull['trail']):
                trail_alpha = int(150 * i / len(skull['trail']))
                trail_size = int(6 * i / len(skull['trail']))
                if trail_size > 0:
                    pygame.draw.circle(self.image, (*self.theme["hellfire"], trail_alpha),
                                     (int(tx), int(ty)), trail_size)
            
            # 绘制骷髅
            self._draw_skull(int(skull['x']), int(skull['y']), skull['rotation'])
    
    def _draw_skull(self, x, y, rotation):
        """绘制骷髅"""
        # 发光光晕
        pygame.draw.circle(self.image, (*self.theme["halo"], 80), (x, y), 20)
        pygame.draw.circle(self.image, (*self.theme["hellfire"], 120), (x, y), 14)
        
        # 骷髅主体
        pygame.draw.circle(self.image, self.theme["skull"], (x, y), 10)
        pygame.draw.circle(self.image, self.theme["core"], (x, y), 10, 2)
        
        # 眼眶
        eye_offset = 4
        pygame.draw.circle(self.image, (0, 0, 0), (x - eye_offset, y - 2), 3)
        pygame.draw.circle(self.image, (0, 0, 0), (x + eye_offset, y - 2), 3)
        
        # 发光眼睛
        pygame.draw.circle(self.image, self.theme["eye"], (x - eye_offset, y - 2), 2)
        pygame.draw.circle(self.image, self.theme["eye"], (x + eye_offset, y - 2), 2)
        
        # 鼻孔
        pygame.draw.polygon(self.image, (0, 0, 0), [(x, y + 1), (x - 2, y + 4), (x + 2, y + 4)])
        
        # 牙齿
        for i in range(-3, 4):
            tx = x + i * 2
            pygame.draw.line(self.image, (200, 200, 200), (tx, y + 6), (tx, y + 9), 1)
    
    def _spawn_fire_particles(self):
        """生成火焰粒子"""
        # 从火墙边缘生成
        sources = [
            (random.randint(0, WIDTH), int(self.walls['top']['pos']) + self.wall_thickness),
            (random.randint(0, WIDTH), int(self.walls['bottom']['pos'])),
            (int(self.walls['left']['pos']) + self.wall_thickness, random.randint(0, HEIGHT)),
            (int(self.walls['right']['pos']), random.randint(0, HEIGHT)),
        ]
        x, y = random.choice(sources)
        self.fire_particles.append({
            'x': x, 'y': y,
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-3, -1),
            'life': 30,
            'size': random.randint(3, 8),
        })
    
    def _update_fire_particles(self):
        """更新火焰粒子"""
        for p in self.fire_particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            
            if p['life'] <= 0:
                self.fire_particles.remove(p)
            else:
                alpha = int(200 * p['life'] / 30)
                pygame.draw.circle(self.image, (*self.theme["magic"], alpha),
                                 (int(p['x']), int(p['y'])), p['size'])
    
    def _spawn_ground_crack(self):
        """生成地面裂痕"""
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        angle = random.uniform(0, math.pi * 2)
        length = random.randint(30, 80)
        
        self.ground_cracks.append({
            'x': x, 'y': y,
            'angle': angle,
            'length': length,
            'alpha': 200,
            'branches': [(random.uniform(-0.5, 0.5), random.uniform(0.3, 0.7)) for _ in range(random.randint(2, 4))]
        })
    
    def _update_ground_cracks(self):
        """更新地面裂痕"""
        for crack in self.ground_cracks[:]:
            crack['alpha'] -= 1
            if crack['alpha'] <= 0:
                self.ground_cracks.remove(crack)
                continue
            
            # 主裂痕
            end_x = crack['x'] + math.cos(crack['angle']) * crack['length']
            end_y = crack['y'] + math.sin(crack['angle']) * crack['length']
            pygame.draw.line(self.image, (*self.theme["rune"], crack['alpha']),
                           (crack['x'], crack['y']), (int(end_x), int(end_y)), 2)
            
            # 分支
            for branch_angle, branch_pos in crack['branches']:
                bx = crack['x'] + math.cos(crack['angle']) * crack['length'] * branch_pos
                by = crack['y'] + math.sin(crack['angle']) * crack['length'] * branch_pos
                bend_x = bx + math.cos(crack['angle'] + branch_angle) * crack['length'] * 0.4
                bend_y = by + math.sin(crack['angle'] + branch_angle) * crack['length'] * 0.4
                pygame.draw.line(self.image, (*self.theme["rune"], crack['alpha'] // 2),
                               (int(bx), int(by)), (int(bend_x), int(bend_y)), 1)
    
    def _render_rune_circle(self):
        """渲染符文魔法阵"""
        if self.phase < 1:
            return
        
        cx, cy = WIDTH // 2, HEIGHT // 2
        base_radius = 100
        
        # 外圈
        pygame.draw.circle(self.image, (*self.theme["rune"], 100), (cx, cy), base_radius, 2)
        pygame.draw.circle(self.image, (*self.theme["rune"], 60), (cx, cy), base_radius + 15, 1)
        pygame.draw.circle(self.image, (*self.theme["rune"], 40), (cx, cy), base_radius + 30, 1)
        
        # 旋转符文
        for symbol in self.rune_symbols:
            angle = math.radians(symbol['angle'] + self.rune_angle)
            symbol['pulse'] += 0.08
            pulse = 0.7 + 0.3 * math.sin(symbol['pulse'])
            
            # 符文位置
            rx = cx + int(math.cos(angle) * base_radius)
            ry = cy + int(math.sin(angle) * base_radius)
            
            # 符文发光
            glow_size = int(8 * pulse)
            pygame.draw.circle(self.image, (*self.theme["magic"], int(150 * pulse)), (rx, ry), glow_size)
            pygame.draw.circle(self.image, (*self.theme["core"], int(200 * pulse)), (rx, ry), glow_size - 2)
            
            # 连线到中心
            pygame.draw.line(self.image, (*self.theme["rune"], int(80 * pulse)),
                           (rx, ry), (cx, cy), 1)
        
        # 内部六芒星
        star_radius = base_radius * 0.6
        star_angle = math.radians(self.rune_angle * 0.5)
        star_points = []
        for i in range(6):
            angle = star_angle + i * math.pi / 3
            star_points.append((
                cx + int(math.cos(angle) * star_radius),
                cy + int(math.sin(angle) * star_radius)
            ))
        
        # 绘制六芒星（两个三角形）
        pygame.draw.polygon(self.image, (*self.theme["halo"], 80),
                          [star_points[0], star_points[2], star_points[4]], 2)
        pygame.draw.polygon(self.image, (*self.theme["halo"], 80),
                          [star_points[1], star_points[3], star_points[5]], 2)
    
    def _render_eye(self):
        """渲染灾厄之眼"""
        if self.eye_scale <= 0:
            return
        
        cx, cy = WIDTH // 2, HEIGHT // 2
        
        # 寻找目标（最近的敌人）
        if self.eye_target is None or not self.eye_target.alive():
            closest_dist = float('inf')
            for mob in mobs:
                dist = math.hypot(mob.rect.centerx - cx, mob.rect.centery - cy)
                if dist < closest_dist:
                    closest_dist = dist
                    self.eye_target = mob
        
        # 眼睛尺寸
        eye_size = int(50 * self.eye_scale)
        if eye_size < 5:
            return
        
        # 眼白
        pygame.draw.ellipse(self.image, (200, 180, 180),
                          (cx - eye_size, cy - eye_size // 2, eye_size * 2, eye_size))
        pygame.draw.ellipse(self.image, self.theme["core"],
                          (cx - eye_size, cy - eye_size // 2, eye_size * 2, eye_size), 3)
        
        # 瞳孔方向
        pupil_offset_x, pupil_offset_y = 0, 0
        if self.eye_target and self.eye_target.alive():
            dx = self.eye_target.rect.centerx - cx
            dy = self.eye_target.rect.centery - cy
            dist = max(1, math.hypot(dx, dy))
            pupil_offset_x = int(dx / dist * eye_size * 0.3)
            pupil_offset_y = int(dy / dist * eye_size * 0.15)
        
        # 虹膜
        iris_size = int(eye_size * 0.5)
        iris_x = cx + pupil_offset_x
        iris_y = cy + pupil_offset_y
        pygame.draw.circle(self.image, self.theme["eye"], (iris_x, iris_y), iris_size)
        
        # 瞳孔
        pupil_size = int(iris_size * 0.5)
        pygame.draw.circle(self.image, (0, 0, 0), (iris_x, iris_y), pupil_size)
        
        # 高光
        highlight_x = iris_x - int(iris_size * 0.3)
        highlight_y = iris_y - int(iris_size * 0.2)
        pygame.draw.circle(self.image, (255, 255, 255), (highlight_x, highlight_y), int(pupil_size * 0.4))
        
        # 脉动光环
        pulse = abs(math.sin(self.eye_pulse))
        ring_alpha = int(100 * pulse)
        ring_size = int(eye_size * (1.2 + 0.3 * pulse))
        pygame.draw.ellipse(self.image, (*self.theme["halo"], ring_alpha),
                          (cx - ring_size, cy - ring_size // 2, ring_size * 2, ring_size), 2)
    
    def _push_enemies(self):
        """推挤敌人向中心"""
        left_bound = int(self.walls['left']['pos']) + self.wall_thickness + 10
        right_bound = int(self.walls['right']['pos']) - 10
        top_bound = int(self.walls['top']['pos']) + self.wall_thickness + 10
        bottom_bound = int(self.walls['bottom']['pos']) - 10
        
        cx, cy = WIDTH // 2, HEIGHT // 2
        
        for mob in mobs:
            pushed = False
            push_x, push_y = 0, 0
            
            if mob.rect.left < left_bound:
                push_x = 5
                pushed = True
            elif mob.rect.right > right_bound:
                push_x = -5
                pushed = True
            
            if mob.rect.top < top_bound:
                push_y = 5
                pushed = True
            elif mob.rect.bottom > bottom_bound:
                push_y = -5
                pushed = True
            
            if pushed:
                mob.rect.x += push_x
                mob.rect.y += push_y
    
    def _damage_enemies_in_walls(self):
        """伤害接触火墙的敌人"""
        left_bound = int(self.walls['left']['pos']) + self.wall_thickness
        right_bound = int(self.walls['right']['pos'])
        top_bound = int(self.walls['top']['pos']) + self.wall_thickness
        bottom_bound = int(self.walls['bottom']['pos'])
        
        for mob in mobs:
            in_wall = False
            if mob.rect.left < left_bound or mob.rect.right > right_bound:
                in_wall = True
            if mob.rect.top < top_bound or mob.rect.bottom > bottom_bound:
                in_wall = True
            
            if in_wall and hasattr(mob, 'take_damage'):
                mob.take_damage(self.damage * 0.02)  # 持续灼烧
    
    def _end_skill(self):
        """技能结束"""
        if self.owner:
            self.owner.invincible = False
            self.owner.skill_locked = False


# ==================== G技能：天降灾厄 ====================
class RainOfCalamitySkill(pygame.sprite.Sprite):
    """
    天降灾厄 - G技能
    硫磺火球从天空暴雨般落下，覆盖全屏轰炸
    
    增强视觉效果：
    1. 天空染红+闪电预警
    2. 火球带长长的燃烧尾迹
    3. 落地产生爆炸波纹和火焰喷溅
    4. 地面持续燃烧区域
    5. 硫磺烟雾弥漫
    6. 灾厄女巫剪影浮现
    7. 末日号角音效提示
    """
    
    def __init__(self, owner, damage, style="default"):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.style = style
        self.theme = get_theme(style)
        
        self.frame = 0
        self.total_frame = 0
        
        # 阶段：预警 -> 轰炸 -> 余烬
        self.phase = 0
        self.phase_duration = [45, 240, 60]  # 0.75s, 4s, 1s
        
        # 火球列表
        self.fireballs = []
        self.fireball_spawn_timer = 0
        self.fireball_spawn_interval = 4  # 每4帧生成一个
        
        # 爆炸效果
        self.explosions = []
        
        # 地面燃烧区域
        self.burn_zones = []
        
        # 硫磺烟雾
        self.smoke_particles = []
        
        # 闪电
        self.lightning_bolts = []
        
        # 女巫剪影
        self.witch_alpha = 0
        self.witch_y = -200
        
        # 天空染色
        self.sky_intensity = 0
        
        # 火焰碎片
        self.embers = []
        
        # 冲击波
        self.shockwaves = []
        
        # 锁定玩家
        if owner:
            owner.invincible = True
            owner.skill_locked = True
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def update(self):
        self.total_frame += 1
        
        # 确定当前阶段
        phase_start = 0
        for i, dur in enumerate(self.phase_duration):
            if self.total_frame <= phase_start + dur:
                self.phase = i
                self.frame = self.total_frame - phase_start
                break
            phase_start += dur
        else:
            self._end_skill()
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        # 根据阶段更新
        if self.phase == 0:
            self._phase0_warning()
        elif self.phase == 1:
            self._phase1_bombardment()
        elif self.phase == 2:
            self._phase2_aftermath()
        
        # 更新所有效果
        self._render_sky()
        self._update_lightning()
        self._render_witch_silhouette()
        self._update_fireballs()
        self._update_explosions()
        self._update_burn_zones()
        self._update_smoke()
        self._update_embers()
        self._update_shockwaves()
    
    def _phase0_warning(self):
        """预警阶段：天空变红，闪电预示"""
        progress = self.frame / self.phase_duration[0]
        
        # 天空逐渐染红
        self.sky_intensity = progress * 0.6
        
        # 生成预警闪电
        if self.frame % 12 == 0:
            self._spawn_lightning()
        
        # 女巫剪影浮现
        self.witch_alpha = int(150 * progress)
        self.witch_y = -200 + progress * 100
        
        # 边缘警告脉冲
        pulse = abs(math.sin(self.frame * 0.3))
        edge_alpha = int(100 * pulse * progress)
        
        # 顶部重点警告
        for i in range(5):
            y = i * 10
            alpha = edge_alpha - i * 15
            if alpha > 0:
                pygame.draw.rect(self.image, (*self.theme["hellfire"], alpha),
                               (0, y, WIDTH, 10))
        
        # 落点预警标记
        if self.frame > 20:
            mark_count = int(8 * (self.frame - 20) / 25)
            for i in range(min(mark_count, 8)):
                mx = int(WIDTH * (i + 0.5) / 8)
                my = HEIGHT - 50
                # 闪烁的目标圈
                if self.frame % 6 < 3:
                    pygame.draw.circle(self.image, (*self.theme["core"], int(150 * progress)),
                                     (mx, my), 20, 2)
                    pygame.draw.line(self.image, (*self.theme["hellfire"], int(100 * progress)),
                                   (mx, 0), (mx, my - 30), 1)
    
    def _phase1_bombardment(self):
        """轰炸阶段：火球雨"""
        progress = self.frame / self.phase_duration[1]
        
        # 保持天空染红
        self.sky_intensity = 0.6 + 0.2 * math.sin(self.frame * 0.1)
        
        # 女巫完全显现
        self.witch_alpha = 180
        self.witch_y = -100 + math.sin(self.frame * 0.05) * 20
        
        # 生成火球
        self.fireball_spawn_timer += 1
        if self.fireball_spawn_timer >= self.fireball_spawn_interval:
            self._spawn_fireball()
            self.fireball_spawn_timer = 0
            # 随着时间推移加速
            if self.fireball_spawn_interval > 2:
                self.fireball_spawn_interval = max(2, 4 - int(progress * 2))
        
        # 随机闪电
        if random.random() < 0.03:
            self._spawn_lightning()
        
        # 生成烟雾
        if self.frame % 8 == 0:
            self._spawn_smoke()
    
    def _phase2_aftermath(self):
        """余烬阶段：残火消散"""
        progress = self.frame / self.phase_duration[2]
        
        # 天空逐渐恢复
        self.sky_intensity = 0.6 * (1 - progress)
        
        # 女巫消失
        self.witch_alpha = int(180 * (1 - progress))
        self.witch_y = -100 - progress * 100
        
        # 最后的余烬
        if self.frame % 5 == 0 and len(self.embers) < 30:
            self._spawn_ember(random.randint(0, WIDTH), random.randint(HEIGHT - 150, HEIGHT - 50))
    
    def _render_sky(self):
        """渲染染红的天空"""
        if self.sky_intensity <= 0:
            return
        
        # 渐变天空
        for i in range(10):
            y = i * (HEIGHT // 10)
            h = HEIGHT // 10 + 1
            # 越往上越红
            intensity = self.sky_intensity * (1 - i * 0.08)
            alpha = int(80 * intensity)
            if alpha > 0:
                color = (
                    int(self.theme["hellfire"][0] * intensity),
                    int(self.theme["hellfire"][1] * intensity * 0.3),
                    int(self.theme["hellfire"][2] * intensity * 0.2),
                    alpha
                )
                pygame.draw.rect(self.image, color, (0, y, WIDTH, h))
        
        # 脉动效果
        pulse = abs(math.sin(self.total_frame * 0.08))
        pulse_alpha = int(30 * pulse * self.sky_intensity)
        if pulse_alpha > 0:
            pygame.draw.rect(self.image, (*self.theme["core"], pulse_alpha),
                           (0, 0, WIDTH, HEIGHT // 3))
    
    def _spawn_lightning(self):
        """生成闪电"""
        start_x = random.randint(50, WIDTH - 50)
        
        # 生成锯齿状闪电路径
        points = [(start_x, 0)]
        y = 0
        while y < HEIGHT * 0.7:
            y += random.randint(30, 60)
            x = points[-1][0] + random.randint(-40, 40)
            x = max(20, min(WIDTH - 20, x))
            points.append((x, y))
        
        self.lightning_bolts.append({
            'points': points,
            'life': 8,
            'branches': self._generate_lightning_branches(points),
            'alpha': 255,
        })
    
    def _generate_lightning_branches(self, main_points):
        """生成闪电分支"""
        branches = []
        for i, (x, y) in enumerate(main_points[1:-1], 1):
            if random.random() < 0.4:
                branch_len = random.randint(20, 50)
                branch_angle = random.choice([-1, 1]) * random.uniform(0.3, 0.8)
                bx = x + int(math.cos(branch_angle) * branch_len)
                by = y + int(math.sin(branch_angle + math.pi/2) * branch_len)
                branches.append([(x, y), (bx, by)])
        return branches
    
    def _update_lightning(self):
        """更新闪电"""
        for bolt in self.lightning_bolts[:]:
            bolt['life'] -= 1
            bolt['alpha'] = int(255 * bolt['life'] / 8)
            
            if bolt['life'] <= 0:
                self.lightning_bolts.remove(bolt)
                continue
            
            # 绘制主闪电
            if len(bolt['points']) > 1:
                pygame.draw.lines(self.image, (*self.theme["magic"], bolt['alpha']),
                                False, bolt['points'], 3)
                pygame.draw.lines(self.image, (255, 255, 255, bolt['alpha']),
                                False, bolt['points'], 1)
            
            # 绘制分支
            for branch in bolt['branches']:
                pygame.draw.lines(self.image, (*self.theme["hellfire"], bolt['alpha'] // 2),
                                False, branch, 2)
    
    def _render_witch_silhouette(self):
        """渲染灾厄女巫剪影"""
        if self.witch_alpha <= 0:
            return
        
        cx = WIDTH // 2
        cy = int(self.witch_y)
        
        # 女巫身体轮廓（简化的三角形斗篷）
        cloak_points = [
            (cx, cy - 60),      # 头顶
            (cx - 80, cy + 80),  # 左下
            (cx + 80, cy + 80),  # 右下
        ]
        
        # 半透明剪影
        pygame.draw.polygon(self.image, (*self.theme["obsidian"], self.witch_alpha), cloak_points)
        pygame.draw.polygon(self.image, (*self.theme["core"], self.witch_alpha // 2), cloak_points, 2)
        
        # 头部
        pygame.draw.circle(self.image, (*self.theme["obsidian"], self.witch_alpha),
                         (cx, cy - 40), 25)
        
        # 发光的眼睛
        eye_pulse = abs(math.sin(self.total_frame * 0.15))
        eye_alpha = int(self.witch_alpha * (0.7 + 0.3 * eye_pulse))
        pygame.draw.circle(self.image, (*self.theme["eye"], eye_alpha),
                         (cx - 10, cy - 45), 5)
        pygame.draw.circle(self.image, (*self.theme["eye"], eye_alpha),
                         (cx + 10, cy - 45), 5)
        
        # 眼睛光芒
        for eye_x in [cx - 10, cx + 10]:
            for i in range(3):
                glow_r = 8 + i * 4
                glow_alpha = eye_alpha // (i + 2)
                pygame.draw.circle(self.image, (*self.theme["halo"], glow_alpha),
                                 (eye_x, cy - 45), glow_r)
        
        # 女巫手臂（伸出释放火球）
        arm_wave = math.sin(self.total_frame * 0.2) * 10
        left_arm = [(cx - 40, cy + 20), (cx - 70 + arm_wave, cy - 10)]
        right_arm = [(cx + 40, cy + 20), (cx + 70 - arm_wave, cy - 10)]
        pygame.draw.lines(self.image, (*self.theme["obsidian"], self.witch_alpha),
                        False, left_arm, 8)
        pygame.draw.lines(self.image, (*self.theme["obsidian"], self.witch_alpha),
                        False, right_arm, 8)
        
        # 手部火焰
        for hx in [cx - 70 + arm_wave, cx + 70 - arm_wave]:
            hy = cy - 10
            for i in range(3):
                flame_r = 12 - i * 3
                flame_alpha = int(self.witch_alpha * (0.8 - i * 0.2))
                pygame.draw.circle(self.image, (*self.theme["hellfire"], flame_alpha),
                                 (int(hx), hy), flame_r)
    
    def _spawn_fireball(self):
        """生成火球"""
        x = random.randint(30, WIDTH - 30)
        
        # 火球大小变化
        size = random.randint(15, 30)
        speed = random.uniform(8, 14)
        
        self.fireballs.append({
            'x': x,
            'y': -size,
            'size': size,
            'speed': speed,
            'trail': [],
            'rotation': random.uniform(0, math.pi * 2),
            'spin': random.uniform(-0.2, 0.2),
            # 轻微横向漂移
            'drift': random.uniform(-0.5, 0.5),
        })
    
    def _update_fireballs(self):
        """更新火球"""
        for fb in self.fireballs[:]:
            # 移动
            fb['y'] += fb['speed']
            fb['x'] += fb['drift']
            fb['rotation'] += fb['spin']
            
            # 添加轨迹
            fb['trail'].append((fb['x'], fb['y']))
            if len(fb['trail']) > 20:
                fb['trail'].pop(0)
            
            # 检查落地
            if fb['y'] >= HEIGHT - 30:
                self._create_explosion(fb['x'], HEIGHT - 30, fb['size'])
                self.fireballs.remove(fb)
                continue
            
            # 检查碰撞敌人
            for mob in mobs:
                if math.hypot(mob.rect.centerx - fb['x'], mob.rect.centery - fb['y']) < fb['size'] + 20:
                    if hasattr(mob, 'take_damage'):
                        mob.take_damage(self.damage * 0.4)
                    self._create_explosion(fb['x'], fb['y'], fb['size'])
                    self.fireballs.remove(fb)
                    break
            else:
                # 绘制火球轨迹
                for i, (tx, ty) in enumerate(fb['trail']):
                    trail_progress = i / len(fb['trail'])
                    trail_size = int(fb['size'] * 0.6 * trail_progress)
                    trail_alpha = int(180 * trail_progress)
                    if trail_size > 0:
                        pygame.draw.circle(self.image, (*self.theme["hellfire"], trail_alpha),
                                         (int(tx), int(ty)), trail_size)
                
                # 绘制火球本体
                self._draw_fireball(int(fb['x']), int(fb['y']), fb['size'], fb['rotation'])
    
    def _draw_fireball(self, x, y, size, rotation):
        """绘制火球"""
        # 外层光晕
        pygame.draw.circle(self.image, (*self.theme["halo"], 60), (x, y), size + 10)
        pygame.draw.circle(self.image, (*self.theme["hellfire"], 100), (x, y), size + 5)
        
        # 火球核心
        pygame.draw.circle(self.image, self.theme["hellfire"], (x, y), size)
        pygame.draw.circle(self.image, self.theme["core"], (x, y), int(size * 0.7))
        pygame.draw.circle(self.image, (255, 200, 100), (x, y), int(size * 0.4))
        pygame.draw.circle(self.image, (255, 255, 200), (x, y), int(size * 0.2))
        
        # 旋转的火焰纹理
        for i in range(4):
            angle = rotation + i * math.pi / 2
            fx = x + int(math.cos(angle) * size * 0.5)
            fy = y + int(math.sin(angle) * size * 0.5)
            pygame.draw.circle(self.image, (*self.theme["magic"], 150), (fx, fy), int(size * 0.3))
        
        # 顶部火焰尖
        flame_points = [
            (x, y - size - 8),
            (x - 6, y - size + 4),
            (x + 6, y - size + 4),
        ]
        pygame.draw.polygon(self.image, self.theme["core"], flame_points)
    
    def _create_explosion(self, x, y, size):
        """创建爆炸效果"""
        self.explosions.append({
            'x': x,
            'y': y,
            'radius': 0,
            'max_radius': size * 3,
            'life': 30,
            'color': self.theme["hellfire"],
        })
        
        # 创建燃烧区域
        self._create_burn_zone(x, y, size * 2)
        
        # 创建冲击波
        self.shockwaves.append({
            'x': x,
            'y': y,
            'radius': 0,
            'max_radius': size * 4,
            'life': 20,
        })
        
        # 生成火焰碎片
        for _ in range(8):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(3, 8)
            self.embers.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 3,
                'life': random.randint(20, 40),
                'size': random.randint(3, 7),
            })
        
        # 伤害范围内敌人
        for mob in mobs:
            dist = math.hypot(mob.rect.centerx - x, mob.rect.centery - y)
            if dist < size * 3 and hasattr(mob, 'take_damage'):
                mob.take_damage(self.damage * 0.3 * (1 - dist / (size * 3)))
    
    def _update_explosions(self):
        """更新爆炸效果"""
        for exp in self.explosions[:]:
            exp['life'] -= 1
            progress = 1 - exp['life'] / 30
            exp['radius'] = int(exp['max_radius'] * progress)
            
            if exp['life'] <= 0:
                self.explosions.remove(exp)
                continue
            
            alpha = int(200 * (1 - progress))
            
            # 爆炸波纹
            if exp['radius'] > 0 and alpha > 0:
                pygame.draw.circle(self.image, (*exp['color'], alpha),
                                 (int(exp['x']), int(exp['y'])), exp['radius'], 4)
                pygame.draw.circle(self.image, (*self.theme["core"], alpha // 2),
                                 (int(exp['x']), int(exp['y'])), int(exp['radius'] * 0.6))
                
                # 中心闪光
                if exp['life'] > 20:
                    flash_alpha = int(255 * (exp['life'] - 20) / 10)
                    pygame.draw.circle(self.image, (255, 255, 200, flash_alpha),
                                     (int(exp['x']), int(exp['y'])), int(exp['radius'] * 0.3))
    
    def _create_burn_zone(self, x, y, radius):
        """创建地面燃烧区域"""
        self.burn_zones.append({
            'x': x,
            'y': min(y, HEIGHT - 20),
            'radius': radius,
            'life': 120,  # 2秒燃烧
            'intensity': 1.0,
        })
    
    def _update_burn_zones(self):
        """更新燃烧区域"""
        for zone in self.burn_zones[:]:
            zone['life'] -= 1
            zone['intensity'] = zone['life'] / 120
            
            if zone['life'] <= 0:
                self.burn_zones.remove(zone)
                continue
            
            # 绘制燃烧区域
            alpha = int(100 * zone['intensity'])
            
            # 底部火焰渐变
            for i in range(3):
                layer_r = zone['radius'] - i * 5
                layer_alpha = alpha - i * 20
                if layer_r > 0 and layer_alpha > 0:
                    pygame.draw.ellipse(self.image, (*self.theme["hellfire"], layer_alpha),
                                      (zone['x'] - layer_r, zone['y'] - layer_r // 3,
                                       layer_r * 2, layer_r * 2 // 3))
            
            # 火焰跳动
            flame_count = int(zone['radius'] // 8)
            for i in range(flame_count):
                fx = zone['x'] - zone['radius'] + i * 16 + random.randint(-3, 3)
                flame_h = int(15 * zone['intensity'] * (0.5 + 0.5 * math.sin(self.total_frame * 0.3 + i)))
                if flame_h > 3:
                    flame_pts = [
                        (fx, zone['y']),
                        (fx - 5, zone['y'] - flame_h),
                        (fx + 5, zone['y'] - flame_h),
                    ]
                    pygame.draw.polygon(self.image, (*self.theme["core"], int(150 * zone['intensity'])), flame_pts)
            
            # 持续伤害区域内敌人
            if zone['life'] % 15 == 0:
                for mob in mobs:
                    dx = mob.rect.centerx - zone['x']
                    dy = mob.rect.centery - zone['y']
                    if abs(dx) < zone['radius'] and abs(dy) < zone['radius'] // 2:
                        if hasattr(mob, 'take_damage'):
                            mob.take_damage(self.damage * 0.05)
    
    def _spawn_smoke(self):
        """生成硫磺烟雾"""
        x = random.randint(0, WIDTH)
        y = HEIGHT - random.randint(20, 100)
        
        self.smoke_particles.append({
            'x': x,
            'y': y,
            'vx': random.uniform(-1, 1),
            'vy': random.uniform(-2, -0.5),
            'size': random.randint(20, 40),
            'life': random.randint(40, 80),
            'max_life': 80,
        })
    
    def _update_smoke(self):
        """更新烟雾"""
        for smoke in self.smoke_particles[:]:
            smoke['x'] += smoke['vx']
            smoke['y'] += smoke['vy']
            smoke['size'] += 0.3  # 烟雾扩散
            smoke['life'] -= 1
            
            if smoke['life'] <= 0:
                self.smoke_particles.remove(smoke)
                continue
            
            alpha = int(60 * smoke['life'] / smoke['max_life'])
            if alpha > 0 and smoke['size'] > 0:
                pygame.draw.circle(self.image, (*self.theme["obsidian"], alpha),
                                 (int(smoke['x']), int(smoke['y'])), int(smoke['size']))
    
    def _spawn_ember(self, x, y):
        """生成余烬"""
        angle = random.uniform(-math.pi, 0)  # 向上
        speed = random.uniform(1, 4)
        self.embers.append({
            'x': x,
            'y': y,
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'life': random.randint(30, 60),
            'size': random.randint(2, 5),
        })
    
    def _update_embers(self):
        """更新余烬"""
        for ember in self.embers[:]:
            ember['x'] += ember['vx']
            ember['y'] += ember['vy']
            ember['vy'] += 0.1  # 重力
            ember['vx'] *= 0.98
            ember['life'] -= 1
            
            if ember['life'] <= 0 or ember['y'] > HEIGHT:
                self.embers.remove(ember)
                continue
            
            alpha = int(255 * ember['life'] / 60)
            pygame.draw.circle(self.image, (*self.theme["magic"], alpha),
                             (int(ember['x']), int(ember['y'])), ember['size'])
            # 发光效果
            pygame.draw.circle(self.image, (*self.theme["hellfire"], alpha // 2),
                             (int(ember['x']), int(ember['y'])), ember['size'] + 2)
    
    def _update_shockwaves(self):
        """更新冲击波"""
        for wave in self.shockwaves[:]:
            wave['life'] -= 1
            progress = 1 - wave['life'] / 20
            wave['radius'] = int(wave['max_radius'] * progress)
            
            if wave['life'] <= 0:
                self.shockwaves.remove(wave)
                continue
            
            alpha = int(100 * (1 - progress))
            if wave['radius'] > 0 and alpha > 0:
                # 椭圆形冲击波（地面效果）
                pygame.draw.ellipse(self.image, (*self.theme["halo"], alpha),
                                  (wave['x'] - wave['radius'],
                                   wave['y'] - wave['radius'] // 3,
                                   wave['radius'] * 2,
                                   wave['radius'] * 2 // 3), 3)
    
    def _end_skill(self):
        """技能结束 - RainOfCalamitySkill"""
        if self.owner:
            self.owner.invincible = False
            self.owner.skill_locked = False


# ==================== C技能：湮灭之眼 ====================
class EyeOfOblivionSkill(pygame.sprite.Sprite):
    """
    湮灭之眼 - C技能
    召唤巨大的灾厄之眼，发射1/3屏宽的毁灭光束持续5秒
    
    增强视觉效果：
    1. 巨大的灾厄之眼逐渐睁开
    2. 能量聚集阶段的粒子漩涡
    3. 光束带有能量波动和边缘粒子
    4. 光束扫过区域产生灼烧痕迹
    5. 眼睛周围的符文环旋转
    6. 光束命中产生爆裂火花
    7. 屏幕震动效果
    8. 最终眼睛闭合消散
    """
    
    def __init__(self, owner, damage, style="default"):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.style = style
        self.theme = get_theme(style)
        
        self.frame = 0
        self.total_frame = 0
        
        # 阶段：睁眼 -> 蓄力 -> 发射 -> 闭眼
        self.phase = 0
        self.phase_duration = [45, 30, 300, 30]  # 0.75s, 0.5s, 5s, 0.5s
        
        # 眼睛参数
        self.eye_x = WIDTH // 2
        self.eye_y = 120
        self.eye_size = 0  # 逐渐变大
        self.max_eye_size = 100
        self.eye_open = 0  # 0=闭合, 1=完全睁开
        self.pupil_target = None
        
        # 光束参数
        self.beam_width = WIDTH // 3
        self.beam_active = False
        self.beam_intensity = 0
        self.beam_x = WIDTH // 2  # 光束中心X位置
        self.beam_sweep_speed = 0  # 扫射速度
        self.beam_sweep_dir = 1
        
        # 能量粒子
        self.energy_particles = []
        
        # 符文环
        self.rune_angle = 0
        self.rune_rings = [
            {'radius': 130, 'speed': 2, 'symbols': 8},
            {'radius': 160, 'speed': -1.5, 'symbols': 12},
            {'radius': 190, 'speed': 1, 'symbols': 16},
        ]
        
        # 光束粒子
        self.beam_particles = []
        
        # 灼烧痕迹
        self.burn_trails = []
        
        # 爆裂火花
        self.sparks = []
        
        # 屏幕震动
        self.screen_shake = 0
        
        # 能量脉冲环
        self.pulse_rings = []
        
        # 虹膜纹理角度
        self.iris_pattern_angle = 0
        
        # 锁定玩家
        if owner:
            owner.invincible = True
            owner.skill_locked = True
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def update(self):
        self.total_frame += 1
        
        # 确定当前阶段
        phase_start = 0
        for i, dur in enumerate(self.phase_duration):
            if self.total_frame <= phase_start + dur:
                self.phase = i
                self.frame = self.total_frame - phase_start
                break
            phase_start += dur
        else:
            self._end_skill()
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        # 应用屏幕震动偏移
        shake_offset_x = 0
        shake_offset_y = 0
        if self.screen_shake > 0:
            shake_offset_x = random.randint(-self.screen_shake, self.screen_shake)
            shake_offset_y = random.randint(-self.screen_shake, self.screen_shake)
            self.screen_shake = max(0, self.screen_shake - 1)
        
        # 根据阶段更新
        if self.phase == 0:
            self._phase0_open_eye()
        elif self.phase == 1:
            self._phase1_charge()
        elif self.phase == 2:
            self._phase2_fire()
        elif self.phase == 3:
            self._phase3_close()
        
        # 渲染所有元素
        self._update_energy_particles()
        self._render_rune_rings()
        self._render_eye(shake_offset_x, shake_offset_y)
        self._render_beam()
        self._update_beam_particles()
        self._update_burn_trails()
        self._update_sparks()
        self._update_pulse_rings()
    
    def _phase0_open_eye(self):
        """睁眼阶段"""
        progress = self.frame / self.phase_duration[0]
        
        # 眼睛逐渐变大
        self.eye_size = int(self.max_eye_size * progress)
        
        # 眼睛逐渐睁开
        self.eye_open = progress
        
        # 生成聚集粒子
        if self.frame % 2 == 0:
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(150, 300)
            self.energy_particles.append({
                'x': self.eye_x + math.cos(angle) * dist,
                'y': self.eye_y + math.sin(angle) * dist,
                'target_x': self.eye_x,
                'target_y': self.eye_y,
                'speed': random.uniform(3, 6),
                'size': random.randint(3, 8),
                'color': self.theme["core"],
            })
        
        # 符文环开始旋转
        self.rune_angle += 1
        
        # 背景变暗效果
        dark_alpha = int(80 * progress)
        pygame.draw.rect(self.image, (0, 0, 0, dark_alpha), (0, 0, WIDTH, HEIGHT))
    
    def _phase1_charge(self):
        """蓄力阶段"""
        progress = self.frame / self.phase_duration[1]
        
        self.eye_size = self.max_eye_size
        self.eye_open = 1.0
        
        # 更快生成粒子
        if self.frame % 1 == 0:
            for _ in range(3):
                angle = random.uniform(0, math.pi * 2)
                dist = random.uniform(100, 250)
                self.energy_particles.append({
                    'x': self.eye_x + math.cos(angle) * dist,
                    'y': self.eye_y + math.sin(angle) * dist,
                    'target_x': self.eye_x,
                    'target_y': self.eye_y,
                    'speed': random.uniform(5, 10),
                    'size': random.randint(4, 10),
                    'color': self.theme["hellfire"],
                })
        
        # 符文环加速
        self.rune_angle += 3
        
        # 能量脉冲
        if self.frame % 10 == 0:
            self.pulse_rings.append({
                'x': self.eye_x,
                'y': self.eye_y,
                'radius': 0,
                'max_radius': 200,
                'life': 20,
            })
        
        # 光束预热
        self.beam_intensity = progress * 0.3
        
        # 背景保持暗
        pygame.draw.rect(self.image, (0, 0, 0, 80), (0, 0, WIDTH, HEIGHT))
        
        # 瞳孔收缩聚焦
        self.iris_pattern_angle += 5
    
    def _phase2_fire(self):
        """发射阶段"""
        progress = self.frame / self.phase_duration[2]
        
        self.beam_active = True
        self.beam_intensity = 0.8 + 0.2 * math.sin(self.frame * 0.2)
        
        # 光束左右扫射
        sweep_range = WIDTH // 4
        self.beam_sweep_speed = math.sin(self.frame * 0.02) * 2
        self.beam_x += self.beam_sweep_speed
        self.beam_x = max(self.beam_width // 2, min(WIDTH - self.beam_width // 2, self.beam_x))
        
        # 持续屏幕震动
        if self.frame % 3 == 0:
            self.screen_shake = 3
        
        # 符文环持续旋转
        self.rune_angle += 2
        self.iris_pattern_angle += 3
        
        # 生成光束边缘粒子
        if self.frame % 2 == 0:
            self._spawn_beam_particles()
        
        # 创建灼烧痕迹
        if self.frame % 5 == 0:
            self._create_burn_trail()
        
        # 伤害光束范围内敌人
        self._damage_enemies_in_beam()
        
        # 背景保持暗+红色调
        pygame.draw.rect(self.image, (0, 0, 0, 60), (0, 0, WIDTH, HEIGHT))
        pygame.draw.rect(self.image, (*self.theme["hellfire"], 20), (0, 0, WIDTH, HEIGHT))
        
        # 能量脉冲
        if self.frame % 30 == 0:
            self.pulse_rings.append({
                'x': self.eye_x,
                'y': self.eye_y,
                'radius': 0,
                'max_radius': 250,
                'life': 25,
            })
    
    def _phase3_close(self):
        """闭眼阶段"""
        progress = self.frame / self.phase_duration[3]
        
        # 光束逐渐消失
        self.beam_active = True
        self.beam_intensity = 1.0 - progress
        
        # 眼睛逐渐闭合
        self.eye_open = 1.0 - progress
        self.eye_size = int(self.max_eye_size * (1 - progress * 0.5))
        
        # 背景恢复
        dark_alpha = int(60 * (1 - progress))
        pygame.draw.rect(self.image, (0, 0, 0, dark_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 最后的能量消散
        if self.frame % 3 == 0:
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5)
            self.sparks.append({
                'x': self.eye_x,
                'y': self.eye_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 30,
                'size': random.randint(4, 8),
            })
    
    def _render_eye(self, offset_x=0, offset_y=0):
        """渲染灾厄之眼"""
        if self.eye_size <= 0:
            return
        
        cx = self.eye_x + offset_x
        cy = self.eye_y + offset_y
        
        # 眼睛外部光晕
        for i in range(5):
            glow_r = self.eye_size + 20 + i * 15
            glow_alpha = int(40 - i * 7)
            if glow_alpha > 0:
                pygame.draw.circle(self.image, (*self.theme["halo"], glow_alpha),
                                 (cx, cy), glow_r)
        
        # 眼白（椭圆形，根据睁开程度变化）
        eye_height = int(self.eye_size * self.eye_open)
        if eye_height > 5:
            # 眼白
            pygame.draw.ellipse(self.image, (200, 180, 180),
                              (cx - self.eye_size, cy - eye_height // 2,
                               self.eye_size * 2, eye_height))
            
            # 眼白边缘
            pygame.draw.ellipse(self.image, self.theme["core"],
                              (cx - self.eye_size, cy - eye_height // 2,
                               self.eye_size * 2, eye_height), 4)
            
            # 血丝效果
            if self.eye_open > 0.5:
                for i in range(8):
                    angle = math.radians(i * 45 + self.total_frame * 0.5)
                    vein_len = self.eye_size * 0.7
                    vx = cx + int(math.cos(angle) * self.eye_size * 0.3)
                    vy = cy + int(math.sin(angle) * eye_height * 0.2)
                    vex = cx + int(math.cos(angle) * vein_len)
                    vey = cy + int(math.sin(angle) * eye_height * 0.4)
                    pygame.draw.line(self.image, (*self.theme["core"], 100),
                                   (vx, vy), (vex, vey), 1)
            
            # 虹膜
            iris_size = int(self.eye_size * 0.6 * min(1.0, self.eye_open * 1.5))
            if iris_size > 5:
                # 虹膜底色
                pygame.draw.circle(self.image, self.theme["eye"], (cx, cy), iris_size)
                
                # 虹膜纹理（旋转图案）
                for i in range(12):
                    angle = math.radians(i * 30 + self.iris_pattern_angle)
                    inner_r = iris_size * 0.3
                    outer_r = iris_size * 0.9
                    ix = cx + int(math.cos(angle) * inner_r)
                    iy = cy + int(math.sin(angle) * inner_r)
                    ox = cx + int(math.cos(angle) * outer_r)
                    oy = cy + int(math.sin(angle) * outer_r)
                    pygame.draw.line(self.image, (*self.theme["halo"], 150),
                                   (ix, iy), (ox, oy), 2)
                
                # 虹膜内环
                pygame.draw.circle(self.image, (*self.theme["core"], 200),
                                 (cx, cy), int(iris_size * 0.7), 2)
                
                # 瞳孔
                pupil_size = int(iris_size * 0.4)
                
                # 瞳孔方向（跟随光束）
                pupil_offset_x = int((self.beam_x - cx) * 0.02)
                pupil_offset_y = int(eye_height * 0.1)  # 略微向下看
                
                pygame.draw.circle(self.image, (0, 0, 0),
                                 (cx + pupil_offset_x, cy + pupil_offset_y), pupil_size)
                
                # 瞳孔内的深渊纹理
                for i in range(3):
                    spiral_angle = self.total_frame * 0.1 + i * math.pi * 2 / 3
                    spiral_r = pupil_size * 0.6
                    sx = cx + pupil_offset_x + int(math.cos(spiral_angle) * spiral_r * 0.5)
                    sy = cy + pupil_offset_y + int(math.sin(spiral_angle) * spiral_r * 0.5)
                    pygame.draw.circle(self.image, (*self.theme["eye"], 100),
                                     (sx, sy), 3)
                
                # 高光
                highlight_x = cx - int(iris_size * 0.3)
                highlight_y = cy - int(eye_height * 0.15)
                pygame.draw.circle(self.image, (255, 255, 255, 200),
                                 (highlight_x, highlight_y), int(pupil_size * 0.4))
        
        # 眼睑
        lid_color = self.theme["obsidian"]
        lid_height = int(self.eye_size * (1 - self.eye_open))
        if lid_height > 0:
            # 上眼睑
            pygame.draw.ellipse(self.image, lid_color,
                              (cx - self.eye_size - 5, cy - self.eye_size // 2 - 5,
                               self.eye_size * 2 + 10, lid_height + 10))
            # 下眼睑
            pygame.draw.ellipse(self.image, lid_color,
                              (cx - self.eye_size - 5, cy + eye_height // 2 - 5,
                               self.eye_size * 2 + 10, lid_height + 10))
    
    def _render_rune_rings(self):
        """渲染符文环"""
        if self.eye_size <= 0:
            return
        
        cx, cy = self.eye_x, self.eye_y
        
        for ring in self.rune_rings:
            ring_angle = self.rune_angle * ring['speed']
            
            # 符文环圆圈
            ring_alpha = int(80 * min(1.0, self.eye_open * 2))
            if ring_alpha > 0:
                pygame.draw.circle(self.image, (*self.theme["rune"], ring_alpha),
                                 (cx, cy), ring['radius'], 1)
            
            # 符文符号
            for i in range(ring['symbols']):
                angle = math.radians(ring_angle + i * (360 / ring['symbols']))
                rx = cx + int(math.cos(angle) * ring['radius'])
                ry = cy + int(math.sin(angle) * ring['radius'])
                
                # 符文发光点
                glow_pulse = 0.7 + 0.3 * math.sin(self.total_frame * 0.1 + i)
                glow_size = int(6 * glow_pulse)
                glow_alpha = int(150 * glow_pulse * min(1.0, self.eye_open * 2))
                
                if glow_alpha > 0:
                    pygame.draw.circle(self.image, (*self.theme["magic"], glow_alpha),
                                     (rx, ry), glow_size)
                    pygame.draw.circle(self.image, (*self.theme["halo"], glow_alpha // 2),
                                     (rx, ry), glow_size + 3)
    
    def _render_beam(self):
        """渲染毁灭光束"""
        if not self.beam_active or self.beam_intensity <= 0:
            return
        
        beam_left = int(self.beam_x - self.beam_width // 2)
        beam_right = int(self.beam_x + self.beam_width // 2)
        beam_top = self.eye_y + int(self.eye_size * 0.3)
        
        # 光束核心（多层渐变）
        layers = [
            (self.beam_width, self.theme["halo"], 0.3),
            (self.beam_width * 0.7, self.theme["hellfire"], 0.5),
            (self.beam_width * 0.4, self.theme["core"], 0.7),
            (self.beam_width * 0.2, (255, 200, 150), 0.9),
            (self.beam_width * 0.1, (255, 255, 200), 1.0),
        ]
        
        for layer_width, color, intensity_mult in layers:
            layer_alpha = int(200 * self.beam_intensity * intensity_mult)
            if layer_alpha > 0:
                lx = int(self.beam_x - layer_width // 2)
                pygame.draw.rect(self.image, (*color[:3], layer_alpha),
                               (lx, beam_top, int(layer_width), HEIGHT - beam_top))
        
        # 光束边缘波动
        wave_amplitude = 10 * self.beam_intensity
        for side in [-1, 1]:
            edge_x = self.beam_x + side * self.beam_width // 2
            points = []
            for y in range(beam_top, HEIGHT, 10):
                wave = math.sin(y * 0.05 + self.total_frame * 0.2) * wave_amplitude
                points.append((int(edge_x + wave * side), y))
            
            if len(points) > 1:
                pygame.draw.lines(self.image, (*self.theme["magic"], int(150 * self.beam_intensity)),
                                False, points, 3)
        
        # 光束内能量流
        for i in range(5):
            flow_y = beam_top + ((self.total_frame * 15 + i * 50) % (HEIGHT - beam_top))
            flow_alpha = int(100 * self.beam_intensity * (0.5 + 0.5 * math.sin(i + self.total_frame * 0.1)))
            flow_width = int(self.beam_width * 0.6)
            pygame.draw.rect(self.image, (*self.theme["core"], flow_alpha),
                           (int(self.beam_x - flow_width // 2), flow_y, flow_width, 20))
        
        # 光束与地面接触点
        ground_y = HEIGHT - 20
        impact_width = int(self.beam_width * 1.2)
        
        # 地面爆发效果
        for i in range(3):
            burst_r = int(impact_width * (0.3 + i * 0.2))
            burst_alpha = int(120 * self.beam_intensity * (1 - i * 0.25))
            pygame.draw.ellipse(self.image, (*self.theme["hellfire"], burst_alpha),
                              (int(self.beam_x - burst_r), ground_y - burst_r // 4,
                               burst_r * 2, burst_r // 2))
        
        # 向上飞溅的火花
        if self.total_frame % 3 == 0:
            for _ in range(3):
                spark_x = self.beam_x + random.randint(-self.beam_width // 3, self.beam_width // 3)
                self.sparks.append({
                    'x': spark_x,
                    'y': ground_y,
                    'vx': random.uniform(-3, 3),
                    'vy': random.uniform(-8, -3),
                    'life': random.randint(15, 30),
                    'size': random.randint(3, 6),
                })
    
    def _spawn_beam_particles(self):
        """生成光束边缘粒子"""
        for side in [-1, 1]:
            edge_x = self.beam_x + side * self.beam_width // 2
            y = random.randint(self.eye_y, HEIGHT)
            
            self.beam_particles.append({
                'x': edge_x + random.randint(-10, 10),
                'y': y,
                'vx': side * random.uniform(1, 3),
                'vy': random.uniform(-1, 1),
                'life': random.randint(15, 30),
                'size': random.randint(3, 7),
            })
    
    def _update_beam_particles(self):
        """更新光束粒子"""
        for p in self.beam_particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            
            if p['life'] <= 0:
                self.beam_particles.remove(p)
                continue
            
            alpha = int(200 * p['life'] / 30)
            pygame.draw.circle(self.image, (*self.theme["magic"], alpha),
                             (int(p['x']), int(p['y'])), p['size'])
    
    def _create_burn_trail(self):
        """创建灼烧痕迹"""
        trail_x = self.beam_x + random.randint(-self.beam_width // 3, self.beam_width // 3)
        trail_y = HEIGHT - random.randint(10, 30)
        
        self.burn_trails.append({
            'x': trail_x,
            'y': trail_y,
            'width': random.randint(20, 40),
            'life': 90,
        })
    
    def _update_burn_trails(self):
        """更新灼烧痕迹"""
        for trail in self.burn_trails[:]:
            trail['life'] -= 1
            
            if trail['life'] <= 0:
                self.burn_trails.remove(trail)
                continue
            
            alpha = int(80 * trail['life'] / 90)
            pygame.draw.ellipse(self.image, (*self.theme["hellfire"], alpha),
                              (trail['x'] - trail['width'] // 2, trail['y'] - 5,
                               trail['width'], 10))
    
    def _update_energy_particles(self):
        """更新能量粒子"""
        for p in self.energy_particles[:]:
            # 向目标移动
            dx = p['target_x'] - p['x']
            dy = p['target_y'] - p['y']
            dist = max(1, math.hypot(dx, dy))
            
            p['x'] += dx / dist * p['speed']
            p['y'] += dy / dist * p['speed']
            
            # 到达目标
            if dist < 10:
                self.energy_particles.remove(p)
                continue
            
            # 绘制
            pygame.draw.circle(self.image, (*p['color'], 200),
                             (int(p['x']), int(p['y'])), p['size'])
            pygame.draw.circle(self.image, (*self.theme["magic"], 100),
                             (int(p['x']), int(p['y'])), p['size'] + 3)
    
    def _update_sparks(self):
        """更新火花"""
        for spark in self.sparks[:]:
            spark['x'] += spark['vx']
            spark['y'] += spark['vy']
            spark['vy'] += 0.3  # 重力
            spark['life'] -= 1
            
            if spark['life'] <= 0 or spark['y'] > HEIGHT:
                self.sparks.remove(spark)
                continue
            
            alpha = int(255 * spark['life'] / 30)
            pygame.draw.circle(self.image, (*self.theme["hellfire"], alpha),
                             (int(spark['x']), int(spark['y'])), spark['size'])
    
    def _update_pulse_rings(self):
        """更新能量脉冲环"""
        for ring in self.pulse_rings[:]:
            ring['life'] -= 1
            progress = 1 - ring['life'] / 25
            ring['radius'] = int(ring['max_radius'] * progress)
            
            if ring['life'] <= 0:
                self.pulse_rings.remove(ring)
                continue
            
            alpha = int(150 * (1 - progress))
            if ring['radius'] > 0 and alpha > 0:
                pygame.draw.circle(self.image, (*self.theme["halo"], alpha),
                                 (ring['x'], ring['y']), ring['radius'], 3)
    
    def _damage_enemies_in_beam(self):
        """伤害光束范围内的敌人"""
        if not self.beam_active:
            return
        
        beam_left = self.beam_x - self.beam_width // 2
        beam_right = self.beam_x + self.beam_width // 2
        
        for mob in mobs:
            if beam_left < mob.rect.centerx < beam_right:
                if hasattr(mob, 'take_damage'):
                    # 持续伤害
                    mob.take_damage(self.damage * 0.03)
                    
                    # 生成命中火花
                    if random.random() < 0.1:
                        self.sparks.append({
                            'x': mob.rect.centerx,
                            'y': mob.rect.centery,
                            'vx': random.uniform(-4, 4),
                            'vy': random.uniform(-4, 4),
                            'life': 15,
                            'size': 4,
                        })
    
    def _end_skill(self):
        """技能结束 - EyeOfOblivionSkill"""
        if self.owner:
            self.owner.invincible = False
            self.owner.skill_locked = False


# ==================== 机体辅助系统 ====================

class SkullTail(pygame.sprite.Sprite):
    """
    骷髅长尾 - Sepulcher机体的标志性尾巴
    由多个骷髅节段组成，跟随机体移动并摆动
    """
    
    def __init__(self, owner, style="default"):
        super().__init__()
        self.owner = owner
        self.style = style
        self.theme = get_theme(style)
        
        # 尾巴节段
        self.segments = []
        self.segment_count = 8
        self.segment_spacing = 18
        
        # 初始化节段
        for i in range(self.segment_count):
            self.segments.append({
                'x': 0,
                'y': 0,
                'angle': 0,
                'size': 12 - i,  # 逐渐变小
            })
        
        # 摆动参数
        self.sway_offset = 0
        self.sway_speed = 0.08
        self.sway_amplitude = 15
        
        # 火焰粒子
        self.flame_particles = []
        
        self.image = pygame.Surface((200, 300), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
    
    def update(self):
        if not self.owner or not self.owner.alive():
            self.kill()
            return
        
        # 更新摆动
        self.sway_offset += self.sway_speed
        
        # 更新节段位置（跟随头部）
        head_x = self.owner.rect.centerx
        head_y = self.owner.rect.bottom
        
        for i, seg in enumerate(self.segments):
            if i == 0:
                # 第一节跟随机体
                target_x = head_x
                target_y = head_y + 10
            else:
                # 后续节段跟随前一节
                prev = self.segments[i - 1]
                target_x = prev['x']
                target_y = prev['y'] + self.segment_spacing
            
            # 添加摆动
            sway = math.sin(self.sway_offset + i * 0.5) * self.sway_amplitude * (i / self.segment_count)
            target_x += sway
            
            # 平滑跟随
            seg['x'] += (target_x - seg['x']) * 0.3
            seg['y'] += (target_y - seg['y']) * 0.3
            
            # 计算朝向
            if i > 0:
                prev = self.segments[i - 1]
                seg['angle'] = math.atan2(seg['y'] - prev['y'], seg['x'] - prev['x'])
        
        # 生成火焰粒子
        if random.random() < 0.3:
            last_seg = self.segments[-1]
            self.flame_particles.append({
                'x': last_seg['x'] + random.randint(-5, 5),
                'y': last_seg['y'],
                'vy': random.uniform(1, 3),
                'life': 20,
                'size': random.randint(3, 6),
            })
        
        # 更新粒子
        for p in self.flame_particles[:]:
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.flame_particles.remove(p)
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        
        # 计算绘制偏移
        min_x = min(seg['x'] for seg in self.segments) - 50
        min_y = min(seg['y'] for seg in self.segments) - 50
        
        self.rect.x = int(min_x)
        self.rect.y = int(min_y)
        
        # 绘制连接线
        if len(self.segments) > 1:
            points = [(int(seg['x'] - min_x), int(seg['y'] - min_y)) for seg in self.segments]
            pygame.draw.lines(self.image, self.theme["skull_dark"], False, points, 6)
            pygame.draw.lines(self.image, self.theme["skull"], False, points, 3)
        
        # 绘制骷髅节段
        for i, seg in enumerate(self.segments):
            sx = int(seg['x'] - min_x)
            sy = int(seg['y'] - min_y)
            size = seg['size']
            
            # 节段光晕
            pygame.draw.circle(self.image, (*self.theme["halo"], 50), (sx, sy), size + 5)
            
            # 骷髅节段主体
            pygame.draw.circle(self.image, self.theme["skull"], (sx, sy), size)
            pygame.draw.circle(self.image, self.theme["skull_dark"], (sx, sy), size, 2)
            
            # 眼睛（只有前几节有）
            if i < 3 and size > 6:
                eye_size = max(2, size // 4)
                pygame.draw.circle(self.image, self.theme["eye"], (sx - 3, sy - 2), eye_size)
                pygame.draw.circle(self.image, self.theme["eye"], (sx + 3, sy - 2), eye_size)
        
        # 绘制尾部火焰粒子
        for p in self.flame_particles:
            px = int(p['x'] - min_x)
            py = int(p['y'] - min_y)
            alpha = int(200 * p['life'] / 20)
            pygame.draw.circle(self.image, (*self.theme["hellfire"], alpha), (px, py), p['size'])
    
    def render(self, surface):
        """渲染到指定surface"""
        if self.image and self.rect:
            surface.blit(self.image, self.rect)


class CalamityAura(pygame.sprite.Sprite):
    """
    灾厄光环 - 围绕机体的能量场
    根据怒气值变化强度和颜色
    """
    
    def __init__(self, owner, style="default"):
        super().__init__()
        self.owner = owner
        self.style = style
        self.theme = get_theme(style)
        
        # 光环参数
        self.base_radius = 60
        self.pulse = 0
        self.pulse_speed = 0.1
        
        # 能量粒子
        self.particles = []
        
        # 符文环
        self.rune_angle = 0
        
        # 闪电弧
        self.arcs = []
        
        self.image = pygame.Surface((200, 200), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
    
    def update(self):
        if not self.owner or not self.owner.alive():
            self.kill()
            return
        
        # 获取怒气值（如果有）
        fury = getattr(self.owner, 'sepulcher_fury', 0)
        fury_ratio = min(1.0, fury / 100)
        
        # 更新脉动
        self.pulse += self.pulse_speed
        pulse_scale = 1 + 0.1 * math.sin(self.pulse) * (1 + fury_ratio)
        
        # 更新符文角度
        self.rune_angle += 1 + fury_ratio * 2
        
        # 生成粒子
        if random.random() < 0.2 + fury_ratio * 0.3:
            angle = random.uniform(0, math.pi * 2)
            dist = self.base_radius * pulse_scale
            self.particles.append({
                'angle': angle,
                'dist': dist,
                'target_dist': dist * 0.3,
                'speed': random.uniform(1, 3),
                'life': 30,
                'size': random.randint(2, 5),
            })
        
        # 生成闪电弧（高怒气时）
        if fury_ratio > 0.5 and random.random() < 0.1:
            self.arcs.append({
                'start_angle': random.uniform(0, math.pi * 2),
                'arc_length': random.uniform(0.5, 1.5),
                'life': 8,
            })
        
        # 更新粒子
        for p in self.particles[:]:
            p['dist'] += (p['target_dist'] - p['dist']) * 0.1
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
        
        # 更新闪电弧
        for arc in self.arcs[:]:
            arc['life'] -= 1
            if arc['life'] <= 0:
                self.arcs.remove(arc)
        
        self._render(pulse_scale, fury_ratio)
    
    def _render(self, pulse_scale, fury_ratio):
        self.image.fill((0, 0, 0, 0))
        
        cx, cy = 100, 100
        radius = int(self.base_radius * pulse_scale)
        
        # 定位到机体中心
        self.rect.center = self.owner.rect.center
        
        # 外层光晕
        for i in range(3):
            glow_r = radius + 10 + i * 8
            glow_alpha = int((30 - i * 8) * (0.5 + fury_ratio * 0.5))
            if glow_alpha > 0:
                pygame.draw.circle(self.image, (*self.theme["halo"], glow_alpha), (cx, cy), glow_r)
        
        # 主光环
        ring_alpha = int(80 + fury_ratio * 80)
        pygame.draw.circle(self.image, (*self.theme["core"], ring_alpha), (cx, cy), radius, 2)
        
        # 内环
        inner_radius = int(radius * 0.7)
        pygame.draw.circle(self.image, (*self.theme["hellfire"], int(ring_alpha * 0.7)), (cx, cy), inner_radius, 1)
        
        # 符文点
        rune_count = 6
        for i in range(rune_count):
            angle = math.radians(self.rune_angle + i * (360 / rune_count))
            rx = cx + int(math.cos(angle) * radius)
            ry = cy + int(math.sin(angle) * radius)
            
            rune_pulse = 0.7 + 0.3 * math.sin(self.pulse + i)
            rune_size = int(4 * rune_pulse * (1 + fury_ratio * 0.5))
            
            pygame.draw.circle(self.image, (*self.theme["magic"], int(180 * rune_pulse)), (rx, ry), rune_size)
        
        # 能量粒子
        for p in self.particles:
            px = cx + int(math.cos(p['angle']) * p['dist'])
            py = cy + int(math.sin(p['angle']) * p['dist'])
            alpha = int(200 * p['life'] / 30)
            pygame.draw.circle(self.image, (*self.theme["hellfire"], alpha), (px, py), p['size'])
        
        # 闪电弧
        for arc in self.arcs:
            arc_alpha = int(255 * arc['life'] / 8)
            points = []
            for j in range(8):
                a = arc['start_angle'] + j * arc['arc_length'] / 8
                r = radius + random.randint(-5, 5)
                points.append((cx + int(math.cos(a) * r), cy + int(math.sin(a) * r)))
            if len(points) > 1:
                pygame.draw.lines(self.image, (*self.theme["magic"], arc_alpha), False, points, 2)
    
    def flash(self):
        """擦弹闪烁效果"""
        # 生成一圈闪烁粒子
        for i in range(8):
            angle = i * math.pi / 4
            self.particles.append({
                'angle': angle,
                'dist': self.base_radius * 1.2,
                'target_dist': self.base_radius * 0.5,
                'speed': 3,
                'life': 15,
                'size': 4,
            })
        # 生成闪电弧
        self.arcs.append({
            'start_angle': random.uniform(0, math.pi * 2),
            'arc_length': random.uniform(1.0, 2.0),
            'life': 10,
        })
    
    def render(self, surface):
        """渲染到指定surface"""
        if self.image and self.rect:
            surface.blit(self.image, self.rect)


class MagicHalo(pygame.sprite.Sprite):
    """
    魔法光环 - 机体头顶的旋转符文阵
    """
    
    def __init__(self, owner, style="default"):
        super().__init__()
        self.owner = owner
        self.style = style
        self.theme = get_theme(style)
        
        # 光环参数
        self.radius = 35
        self.angle = 0
        self.rotation_speed = 2
        
        # 符文
        self.runes = []
        for i in range(6):
            self.runes.append({
                'angle_offset': i * 60,
                'pulse': random.random() * math.pi * 2,
            })
        
        # 浮动偏移
        self.float_offset = 0
        
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
    
    def update(self, fury_ratio=0):
        """更新魔法光环，fury_ratio控制旋转速度"""
        if not self.owner or not self.owner.alive():
            self.kill()
            return
        
        # 更新旋转（根据暴怒值加速）
        self.angle += self.rotation_speed * (1 + fury_ratio * 2)
        
        # 更新浮动
        self.float_offset += 0.1
        float_y = math.sin(self.float_offset) * 3
        
        # 定位
        self.rect.centerx = self.owner.rect.centerx
        self.rect.centery = self.owner.rect.top - 25 + int(float_y)
        
        # 更新符文脉动（暴怒时加快）
        for rune in self.runes:
            rune['pulse'] += 0.08 * (1 + fury_ratio)
        
        # 保存fury_ratio用于渲染
        self.current_fury_ratio = fury_ratio
        
        self._render(fury_ratio)
    
    def _render(self, fury_ratio=0):
        self.image.fill((0, 0, 0, 0))
        
        cx, cy = 50, 50
        
        # 外圈光晕（暴怒时更亮）
        glow_alpha = int(30 + fury_ratio * 40)
        pygame.draw.circle(self.image, (*self.theme["halo"], glow_alpha), (cx, cy), self.radius + 10)
        
        # 主圆环
        ring_alpha = int(100 + fury_ratio * 100)
        pygame.draw.circle(self.image, (*self.theme["rune"], ring_alpha), (cx, cy), self.radius, 2)
        pygame.draw.circle(self.image, (*self.theme["magic"], int(60 + fury_ratio * 60)), (cx, cy), self.radius - 5, 1)
        
        # 六芒星
        star_points_outer = []
        star_points_inner = []
        for i in range(6):
            angle = math.radians(self.angle + i * 60)
            ox = cx + int(math.cos(angle) * self.radius * 0.9)
            oy = cy + int(math.sin(angle) * self.radius * 0.9)
            star_points_outer.append((ox, oy))
            
            inner_angle = math.radians(self.angle + i * 60 + 30)
            ix = cx + int(math.cos(inner_angle) * self.radius * 0.5)
            iy = cy + int(math.sin(inner_angle) * self.radius * 0.5)
            star_points_inner.append((ix, iy))
        
        # 绘制六芒星
        star_alpha = int(80 + fury_ratio * 80)
        pygame.draw.polygon(self.image, (*self.theme["halo"], star_alpha),
                          [star_points_outer[0], star_points_outer[2], star_points_outer[4]], 1)
        pygame.draw.polygon(self.image, (*self.theme["halo"], star_alpha),
                          [star_points_outer[1], star_points_outer[3], star_points_outer[5]], 1)
        
        # 符文点
        for rune in self.runes:
            angle = math.radians(self.angle + rune['angle_offset'])
            rx = cx + int(math.cos(angle) * self.radius)
            ry = cy + int(math.sin(angle) * self.radius)
            
            pulse = 0.6 + 0.4 * math.sin(rune['pulse'])
            size = int((4 + fury_ratio * 2) * pulse)
            alpha = int((200 + fury_ratio * 55) * pulse)
            
            pygame.draw.circle(self.image, (*self.theme["core"], alpha), (rx, ry), size)
            pygame.draw.circle(self.image, (*self.theme["magic"], alpha // 2), (rx, ry), size + 2)
        
        # 中心符号（暴怒时更亮）
        eye_alpha = int(150 + fury_ratio * 105)
        pygame.draw.circle(self.image, (*self.theme["eye"], eye_alpha), (cx, cy), int(6 + fury_ratio * 3))
        pygame.draw.circle(self.image, self.theme["core"], (cx, cy), int(4 + fury_ratio * 2))
    
    def render(self, surface):
        """渲染到指定surface"""
        if self.image and self.rect:
            surface.blit(self.image, self.rect)


class BrimstoneBolt(pygame.sprite.Sprite):
    """
    硫磺火弹 - Sepulcher的主要攻击弹幕
    带有火焰尾迹和爆炸效果
    """
    
    def __init__(self, x, y, damage, angle=-90, owner=None, style="default"):
        super().__init__()
        self.float_x = float(x)
        self.float_y = float(y)
        self.angle = angle
        self.damage = damage
        self.owner = owner
        self.style = style
        self.theme = get_theme(style)
        
        # 标准子弹属性（兼容游戏系统）
        self.color = self.theme["core"]
        self.piercing = 0
        self.is_enemy = False
        self.b_type = "sepulcher_bolt"
        
        self.speed = 12
        self.vx = math.cos(math.radians(angle)) * self.speed
        self.vy = math.sin(math.radians(angle)) * self.speed
        
        # 轨迹
        self.trail = []
        self.trail_length = 10
        
        # 旋转
        self.rotation = 0
        
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        # 移动
        self.float_x += self.vx
        self.float_y += self.vy
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 记录轨迹
        self.trail.append((self.float_x, self.float_y))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)
        
        # 旋转
        self.rotation += 10
        
        # 边界检查
        if self.rect.right < 0 or self.rect.left > WIDTH or \
           self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()
            return
        
        # 碰撞检测
        for mob in mobs:
            if self.rect.colliderect(mob.rect):
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage)
                self._create_explosion()
                self.kill()
                return
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 20, 20
        
        # 绘制轨迹
        for i, (tx, ty) in enumerate(self.trail):
            trail_x = int(tx - self.float_x + cx)
            trail_y = int(ty - self.float_y + cy)
            progress = i / len(self.trail)
            size = int(6 * progress)
            alpha = int(150 * progress)
            if size > 0:
                pygame.draw.circle(self.image, (*self.theme["hellfire"], alpha),
                                 (trail_x, trail_y), size)
        
        # 光晕
        pygame.draw.circle(self.image, (*self.theme["halo"], 60), (cx, cy), 15)
        
        # 主体
        pygame.draw.circle(self.image, self.theme["hellfire"], (cx, cy), 10)
        pygame.draw.circle(self.image, self.theme["core"], (cx, cy), 7)
        pygame.draw.circle(self.image, (255, 200, 150), (cx, cy), 4)
        
        # 旋转光芒
        for i in range(4):
            angle = math.radians(self.rotation + i * 90)
            lx = cx + int(math.cos(angle) * 12)
            ly = cy + int(math.sin(angle) * 12)
            pygame.draw.line(self.image, (*self.theme["magic"], 150), (cx, cy), (lx, ly), 2)
    
    def _create_explosion(self):
        """创建爆炸效果"""
        # 可以在这里生成爆炸粒子精灵
        pass


class SepulcherSkull(pygame.sprite.Sprite):
    """
    骷髅召唤物 - Sepulcher召唤的辅助攻击单位
    """
    
    def __init__(self, x, y, target, damage, owner=None, style="default"):
        super().__init__()
        self.float_x = float(x)
        self.float_y = float(y)
        self.target = target
        self.damage = damage
        self.owner = owner
        self.style = style
        self.theme = get_theme(style)
        
        self.speed = 5
        self.hp = 50
        self.lifetime = 300  # 5秒
        
        # 攻击间隔
        self.attack_cooldown = 0
        self.attack_interval = 30
        
        # 轨迹
        self.trail = []
        
        # 动画
        self.bob_offset = random.random() * math.pi * 2
        
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 浮动效果
        self.bob_offset += 0.1
        bob = math.sin(self.bob_offset) * 3
        
        # 追踪目标 - 确保target是有效的精灵对象
        if self.target and hasattr(self.target, 'alive') and self.target.alive():
            dx = self.target.rect.centerx - self.float_x
            dy = self.target.rect.centery - self.float_y
            dist = max(1, math.hypot(dx, dy))
            
            # 保持距离
            if dist > 80:
                self.float_x += dx / dist * self.speed
                self.float_y += dy / dist * self.speed
        else:
            # 寻找新目标
            self.target = None
            closest_dist = float('inf')
            for mob in mobs:
                if hasattr(mob, 'rect'):
                    d = math.hypot(mob.rect.centerx - self.float_x, mob.rect.centery - self.float_y)
                    if d < closest_dist:
                        closest_dist = d
                        self.target = mob
        
        self.rect.center = (int(self.float_x), int(self.float_y + bob))
        
        # 记录轨迹
        self.trail.append((self.float_x, self.float_y + bob))
        if len(self.trail) > 8:
            self.trail.pop(0)
        
        # 攻击
        self.attack_cooldown -= 1
        if self.attack_cooldown <= 0 and self.target and hasattr(self.target, 'alive') and self.target.alive():
            dist = math.hypot(self.target.rect.centerx - self.float_x,
                            self.target.rect.centery - self.float_y)
            if dist < 150:
                self._attack()
                self.attack_cooldown = self.attack_interval
        
        self._render()
    
    def _attack(self):
        """发射火弹攻击"""
        if self.target and hasattr(self.target, 'rect'):
            angle = math.degrees(math.atan2(
                self.target.rect.centery - self.float_y,
                self.target.rect.centerx - self.float_x
            ))
            BrimstoneBolt(self.float_x, self.float_y, self.damage, angle=angle, owner=self.owner, style=self.style)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 20, 20
        
        # 轨迹
        for i, (tx, ty) in enumerate(self.trail):
            trail_x = int(tx - self.float_x + cx)
            trail_y = int(ty - (self.float_y + math.sin(self.bob_offset) * 3) + cy)
            progress = i / len(self.trail)
            alpha = int(100 * progress)
            size = int(8 * progress)
            if size > 0:
                pygame.draw.circle(self.image, (*self.theme["hellfire"], alpha),
                                 (trail_x, trail_y), size)
        
        # 光晕
        pygame.draw.circle(self.image, (*self.theme["halo"], 50), (cx, cy), 18)
        
        # 骷髅主体
        pygame.draw.circle(self.image, self.theme["skull"], (cx, cy), 12)
        pygame.draw.circle(self.image, self.theme["skull_dark"], (cx, cy), 12, 2)
        
        # 眼眶
        pygame.draw.circle(self.image, (0, 0, 0), (cx - 4, cy - 2), 4)
        pygame.draw.circle(self.image, (0, 0, 0), (cx + 4, cy - 2), 4)
        
        # 发光眼睛
        eye_pulse = 0.7 + 0.3 * math.sin(self.bob_offset * 2)
        eye_alpha = int(255 * eye_pulse)
        pygame.draw.circle(self.image, (*self.theme["eye"], eye_alpha), (cx - 4, cy - 2), 2)
        pygame.draw.circle(self.image, (*self.theme["eye"], eye_alpha), (cx + 4, cy - 2), 2)
        
        # 鼻子
        pygame.draw.polygon(self.image, (0, 0, 0), [(cx, cy + 1), (cx - 2, cy + 4), (cx + 2, cy + 4)])
        
        # 牙齿
        for i in range(-2, 3):
            pygame.draw.line(self.image, (200, 200, 200), (cx + i * 3, cy + 6), (cx + i * 3, cy + 9), 1)


class TheBrothersSkill(pygame.sprite.Sprite):
    """
    灾厄双子 - 召唤两个骷髅护卫环绕机体
    """
    
    def __init__(self, owner, damage, style="default"):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.style = style
        self.theme = get_theme(style)
        
        # 双子位置
        self.brothers = [
            {'angle': 0, 'dist': 70, 'attack_cd': 0},
            {'angle': 180, 'dist': 70, 'attack_cd': 15},
        ]
        
        self.rotation_speed = 2
        self.lifetime = 600  # 10秒
        
        self.image = pygame.Surface((200, 200), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        all_sprites.add(self)
    
    def update(self):
        if not self.owner or not self.owner.alive():
            self.kill()
            return
        
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 更新位置
        self.rect.center = self.owner.rect.center
        
        # 旋转
        for brother in self.brothers:
            brother['angle'] += self.rotation_speed
            brother['attack_cd'] -= 1
            
            # 攻击
            if brother['attack_cd'] <= 0:
                self._brother_attack(brother)
                brother['attack_cd'] = 45
        
        self._render()
    
    def _brother_attack(self, brother):
        """兄弟攻击"""
        angle_rad = math.radians(brother['angle'])
        bx = self.owner.rect.centerx + math.cos(angle_rad) * brother['dist']
        by = self.owner.rect.centery + math.sin(angle_rad) * brother['dist']
        
        # 向最近敌人发射
        closest = None
        closest_dist = float('inf')
        for mob in mobs:
            d = math.hypot(mob.rect.centerx - bx, mob.rect.centery - by)
            if d < closest_dist:
                closest_dist = d
                closest = mob
        
        if closest:
            attack_angle = math.degrees(math.atan2(
                closest.rect.centery - by,
                closest.rect.centerx - bx
            ))
            BrimstoneBolt(bx, by, self.damage, angle=attack_angle, owner=self.owner, style=self.style)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 100, 100
        
        # 连接线
        for brother in self.brothers:
            angle = math.radians(brother['angle'])
            bx = cx + int(math.cos(angle) * brother['dist'])
            by = cy + int(math.sin(angle) * brother['dist'])
            pygame.draw.line(self.image, (*self.theme["rune"], 80), (cx, cy), (bx, by), 1)
        
        # 绘制兄弟
        for brother in self.brothers:
            angle = math.radians(brother['angle'])
            bx = cx + int(math.cos(angle) * brother['dist'])
            by = cy + int(math.sin(angle) * brother['dist'])
            
            # 光晕
            pygame.draw.circle(self.image, (*self.theme["halo"], 40), (bx, by), 18)
            
            # 骷髅
            pygame.draw.circle(self.image, self.theme["skull"], (bx, by), 12)
            pygame.draw.circle(self.image, self.theme["skull_dark"], (bx, by), 12, 2)
            
            # 眼睛
            pygame.draw.circle(self.image, self.theme["eye"], (bx - 3, by - 2), 3)
            pygame.draw.circle(self.image, self.theme["eye"], (bx + 3, by - 2), 3)


# ==================== 导出列表 ====================
__all__ = [
    # 主要技能
    "InfernalBoxSkill",      # F键 - 炼狱牢笼
    "RainOfCalamitySkill",   # G键 - 灾厄之雨
    "EyeOfOblivionSkill",    # C键 - 湮灭之眼
    # 辅助系统
    "SkullTail",             # 骷髅尾巴
    "CalamityAura",          # 灾厄力场
    "MagicHalo",             # 魔法阵光环
    # 攻击弹幕
    "BrimstoneBolt",         # 硫磺火弹
    "SepulcherSkull",        # 召唤骷髅
    "TheBrothersSkill",      # 兄弟骷髅
    # 辅助类
    "ScreenFlash",           # 屏幕闪光
    "get_theme",             # 主题获取函数
]
