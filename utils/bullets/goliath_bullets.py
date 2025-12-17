"""
瘟疫使者·歌莉娅 (Goliath) 弹幕系统
原型：Terraria Calamity Mod - The Plaguebringer Goliath
核心机制：瘟疫导弹(毒云残留) + 瘟疫无人机(自爆) + DOT轰炸
"""

import pygame
import math
import random
from config import WIDTH, HEIGHT, all_sprites, bullets, mobs, enemy_bullets

# ==================== 导入涂装主题 ====================
try:
    from utils.planes.skins_goliath import get_goliath_theme, GOLIATH_THEMES
except ImportError:
    GOLIATH_THEMES = {
        "default": {
            "name": "瘟疫使者",
            "armor": (85, 107, 47),
            "toxic": (57, 255, 20),
            "rust": (139, 69, 19),
            "eye": (255, 0, 0),
            "smoke": (50, 60, 40),
            "glow": (100, 255, 100),
        }
    }
    def get_goliath_theme(style):
        return GOLIATH_THEMES.get(style, GOLIATH_THEMES["default"])


def get_theme(style):
    """获取涂装主题"""
    return get_goliath_theme(style)


# ==================== 主武器：瘟疫巡航导弹 ====================
class PlagueMissileBullet(pygame.sprite.Sprite):
    """
    瘟疫巡航导弹 - 主武器
    慢速重型导弹，爆炸后留下持续5秒的毒云
    """
    
    def __init__(self, x, y, damage, angle=-90, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        # 必需属性（供main.py碰撞处理使用）
        self.color = self.theme["toxic"]
        self.b_type = "plague_missile"
        self.piercing = 0  # 不穿透
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.angle = angle
        self.speed = 8  # 慢速导弹
        
        self.vx = math.cos(math.radians(angle)) * self.speed
        self.vy = math.sin(math.radians(angle)) * self.speed
        
        self.frame = 0
        self.lifetime = 180  # 3秒
        
        # 烟雾拖尾
        self.trail = []
        self.max_trail = 15
        
        self.size = 32
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        self.frame += 1
        
        # 移动
        self.float_x += self.vx
        self.float_y += self.vy
        
        # 添加烟雾拖尾
        if self.frame % 2 == 0:
            self.trail.append({
                'x': self.float_x,
                'y': self.float_y,
                'alpha': 200,
                'size': random.randint(4, 8)
            })
            if len(self.trail) > self.max_trail:
                self.trail.pop(0)
        
        # 更新拖尾
        for t in self.trail:
            t['alpha'] = max(0, t['alpha'] - 15)
            t['size'] = max(1, t['size'] - 0.2)
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 出界检测
        if (self.float_x < -50 or self.float_x > WIDTH + 50 or
            self.float_y < -50 or self.float_y > HEIGHT + 50 or
            self.frame > self.lifetime):
            self._explode()
            self.kill()
            return
        
        self._render()
    
    def _explode(self):
        """爆炸并生成毒云"""
        # 生成毒云
        cloud = PlagueCloud(self.float_x, self.float_y, self.damage * 0.3, 
                           self.owner, self.style, duration=300)  # 5秒
        
        # 爆炸伤害
        from sprites import FloatingText, Particle
        explosion_radius = 60
        
        for mob in list(mobs):
            dist = math.sqrt((mob.rect.centerx - self.float_x)**2 + 
                           (mob.rect.centery - self.float_y)**2)
            if dist < explosion_radius:
                dmg_mult = 1 - (dist / explosion_radius) * 0.5
                final_damage = int(self.damage * dmg_mult)
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(final_damage)
                else:
                    mob.hp -= final_damage
                FloatingText(mob.rect.centerx, mob.rect.top - 10,
                           f"-{final_damage}", self.theme["toxic"])
                
                # 感染瘟疫状态
                if hasattr(mob, 'plague_stacks'):
                    mob.plague_stacks = min(5, mob.plague_stacks + 1)
                else:
                    mob.plague_stacks = 1
        
        # 爆炸特效
        for _ in range(8):
            Particle((self.float_x, self.float_y), self.theme["toxic"], mode='spark')
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.15
        
        armor = self.theme["armor"]
        toxic = self.theme["toxic"]
        rust = self.theme["rust"]
        smoke = self.theme["smoke"]
        
        # 绘制烟雾拖尾
        for trail in self.trail:
            tx = int(trail['x'] - self.float_x + cx)
            ty = int(trail['y'] - self.float_y + cy)
            if 0 < tx < self.size and 0 < ty < self.size:
                alpha = int(trail['alpha'])
                size = int(trail['size'])
                if size > 0 and alpha > 0:
                    # 绿色毒烟
                    pygame.draw.circle(self.image, (*toxic, alpha // 2), (tx, ty), size)
                    pygame.draw.circle(self.image, (*smoke, alpha), (tx, ty), size - 1)
        
        # 导弹主体
        # 弹体
        missile_len = 14
        missile_w = 6
        
        # 计算方向
        angle_rad = math.radians(self.angle)
        
        # 弹头
        head_x = cx + int(math.cos(angle_rad) * missile_len * 0.5)
        head_y = cy + int(math.sin(angle_rad) * missile_len * 0.5)
        pygame.draw.circle(self.image, armor, (head_x, head_y), missile_w // 2 + 1)
        
        # 弹身
        tail_x = cx - int(math.cos(angle_rad) * missile_len * 0.5)
        tail_y = cy - int(math.sin(angle_rad) * missile_len * 0.5)
        pygame.draw.line(self.image, armor, (head_x, head_y), (tail_x, tail_y), missile_w)
        
        # 尾翼
        for side in [-1, 1]:
            perp_angle = angle_rad + math.pi / 2
            fin_x = tail_x + int(math.cos(perp_angle) * side * 5)
            fin_y = tail_y + int(math.sin(perp_angle) * side * 5)
            pygame.draw.line(self.image, rust, (tail_x, tail_y), (fin_x, fin_y), 2)
        
        # 危险标志（弹头）
        pygame.draw.circle(self.image, toxic, (head_x, head_y), 3)
        
        # 推进火焰
        flame_len = int(8 + 3 * math.sin(t * 3))
        flame_x = tail_x - int(math.cos(angle_rad) * flame_len)
        flame_y = tail_y - int(math.sin(angle_rad) * flame_len)
        pygame.draw.line(self.image, toxic, (tail_x, tail_y), (flame_x, flame_y), 3)


# ==================== 毒云 ====================
class PlagueCloud(pygame.sprite.Sprite):
    """
    瘟疫毒云 - 导弹爆炸残留
    持续伤害区域，敌人在内会受到DOT
    """
    
    def __init__(self, x, y, damage_per_tick, owner=None, style="default", duration=300):
        super().__init__()
        self.damage = damage_per_tick
        self.owner = owner
        self.style = style
        self.theme = get_theme(style)
        
        self.center_x = x
        self.center_y = y
        self.duration = duration
        self.frame = 0
        
        self.radius = 50
        self.tick_interval = 15  # 每15帧造成一次伤害
        
        # 粒子系统
        self.particles = []
        for _ in range(20):
            self.particles.append({
                'angle': random.uniform(0, math.pi * 2),
                'dist': random.uniform(0, self.radius),
                'speed': random.uniform(0.5, 1.5),
                'size': random.randint(3, 8),
                'alpha': random.randint(100, 200)
            })
        
        self.size = int(self.radius * 2.5)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        
        if self.frame > self.duration:
            self.kill()
            return
        
        # 造成伤害
        if self.frame % self.tick_interval == 0:
            self._deal_damage()
        
        # 更新粒子
        for p in self.particles:
            p['angle'] += p['speed'] * 0.02
            p['dist'] += math.sin(self.frame * 0.1) * 0.5
            p['dist'] = max(0, min(self.radius, p['dist']))
        
        self._render()
    
    def _deal_damage(self):
        """对范围内敌人造成伤害"""
        from sprites import FloatingText
        
        for mob in mobs:
            dist = math.sqrt((mob.rect.centerx - self.center_x)**2 + 
                           (mob.rect.centery - self.center_y)**2)
            if dist < self.radius + 20:
                final_damage = int(self.damage)
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(final_damage)
                else:
                    mob.hp -= final_damage
                
                # 小字伤害提示
                FloatingText(mob.rect.centerx + random.randint(-10, 10), 
                           mob.rect.top - 5,
                           f"☠{final_damage}", self.theme["toxic"])
                
                # 叠加瘟疫
                if not hasattr(mob, 'plague_stacks'):
                    mob.plague_stacks = 0
                mob.plague_stacks = min(5, mob.plague_stacks + 1)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        
        toxic = self.theme["toxic"]
        smoke = self.theme["smoke"]
        
        # 淡出效果
        fade = 1 - (self.frame / self.duration)
        
        # 底层烟雾
        for i in range(3):
            r = int((self.radius - i * 10) * (0.8 + 0.2 * math.sin(self.frame * 0.05)))
            alpha = int(50 * fade * (1 - i * 0.2))
            if r > 0 and alpha > 0:
                pygame.draw.circle(self.image, (*smoke, alpha), (cx, cy), r)
        
        # 毒气粒子
        for p in self.particles:
            px = cx + int(math.cos(p['angle']) * p['dist'])
            py = cy + int(math.sin(p['angle']) * p['dist'])
            alpha = int(p['alpha'] * fade)
            size = int(p['size'] * (0.5 + 0.5 * fade))
            if size > 0 and alpha > 0:
                pygame.draw.circle(self.image, (*toxic, alpha), (px, py), size)
        
        # 边缘发光
        glow_alpha = int(30 * fade * (0.5 + 0.5 * math.sin(self.frame * 0.1)))
        if glow_alpha > 0:
            pygame.draw.circle(self.image, (*toxic, glow_alpha), (cx, cy), int(self.radius * 1.2), 3)


# ==================== 副武器：瘟疫无人机 ====================
class PlagueDrone(pygame.sprite.Sprite):
    """
    瘟疫无人机 - 机械小蜜蜂
    自动追踪血量最高的敌人，接触后自爆
    """
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        # 必需属性（供main.py碰撞处理使用）
        self.color = self.theme["toxic"]
        self.b_type = "plague_drone"
        self.piercing = 0
        self.is_special_bullet = True  # 无人机自己处理爆炸伤害
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed = 4
        self.turn_rate = 0.08
        
        self.vx = random.uniform(-2, 2)
        self.vy = -3
        
        self.frame = 0
        self.lifetime = 360  # 6秒
        self.target = None
        self.retarget_timer = 0
        
        # 翅膀动画
        self.wing_angle = 0
        
        self.size = 24
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        self.frame += 1
        self.wing_angle += 0.5  # 翅膀快速扇动
        
        if self.frame > self.lifetime:
            self._explode()
            self.kill()
            return
        
        # 寻找目标
        self.retarget_timer += 1
        if self.retarget_timer >= 30 or self.target is None or not self.target.alive():
            self._find_target()
            self.retarget_timer = 0
        
        # 追踪移动
        if self.target and self.target.alive():
            dx = self.target.rect.centerx - self.float_x
            dy = self.target.rect.centery - self.float_y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 5:
                # 平滑转向
                target_vx = (dx / dist) * self.speed
                target_vy = (dy / dist) * self.speed
                self.vx += (target_vx - self.vx) * self.turn_rate
                self.vy += (target_vy - self.vy) * self.turn_rate
            
            # 接触爆炸
            if dist < 25:
                self._explode()
                self.kill()
                return
        
        # 移动
        self.float_x += self.vx
        self.float_y += self.vy
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 出界检测
        if (self.float_x < -50 or self.float_x > WIDTH + 50 or
            self.float_y < -50 or self.float_y > HEIGHT + 50):
            self.kill()
            return
        
        self._render()
    
    def _find_target(self):
        """寻找血量最高的敌人"""
        best_target = None
        max_hp = 0
        
        for mob in mobs:
            if mob.alive() and hasattr(mob, 'hp'):
                if mob.hp > max_hp:
                    max_hp = mob.hp
                    best_target = mob
        
        self.target = best_target
    
    def _explode(self):
        """自爆"""
        from sprites import FloatingText, Particle
        
        explosion_radius = 40
        
        for mob in list(mobs):
            dist = math.sqrt((mob.rect.centerx - self.float_x)**2 + 
                           (mob.rect.centery - self.float_y)**2)
            if dist < explosion_radius:
                dmg_mult = 1 - (dist / explosion_radius) * 0.3
                final_damage = int(self.damage * dmg_mult)
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(final_damage)
                else:
                    mob.hp -= final_damage
                FloatingText(mob.rect.centerx, mob.rect.top - 10,
                           f"-{final_damage}", self.theme["toxic"])
        
        # 生成小毒云
        PlagueCloud(self.float_x, self.float_y, self.damage * 0.15, 
                   self.owner, self.style, duration=120)  # 2秒小毒云
        
        # 爆炸特效
        for _ in range(6):
            Particle((self.float_x, self.float_y), self.theme["toxic"], mode='spark')
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        
        armor = self.theme["armor"]
        toxic = self.theme["toxic"]
        eye = self.theme["eye"]
        
        # 身体
        pygame.draw.ellipse(self.image, armor, (cx - 6, cy - 4, 12, 8))
        
        # 翅膀
        wing_offset = int(3 * math.sin(self.wing_angle))
        # 左翅
        pygame.draw.ellipse(self.image, (*toxic, 150), 
                           (cx - 10, cy - 6 + wing_offset, 8, 4))
        # 右翅
        pygame.draw.ellipse(self.image, (*toxic, 150), 
                           (cx + 2, cy - 6 - wing_offset, 8, 4))
        
        # 眼睛
        pygame.draw.circle(self.image, eye, (cx + 4, cy), 3)
        
        # 尾刺
        pygame.draw.line(self.image, toxic, (cx - 6, cy), (cx - 10, cy + 2), 2)
        
        # 毒液滴落
        if self.frame % 10 < 5:
            pygame.draw.circle(self.image, toxic, (cx - 8, cy + 4), 2)


# ==================== F技能：饱和轰炸·地毯式打击 ====================
class CarpetBombingSkill(pygame.sprite.Sprite):
    """
    饱和轰炸·地毯式打击 - F技能
    数十枚瘟疫炸弹从屏幕顶端呈波浪状落下，覆盖全屏
    增强版：战斗机编队飞过、雷达扫描、地面焦土、震波效果
    """
    
    def __init__(self, owner, damage, style="default"):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.style = style
        self.theme = get_theme(style)
        
        self.frame = 0
        self.total_frame = 0
        self.phase = 0
        self.phase_duration = [45, 210, 90]  # 预警0.75s, 轰炸3.5s, 余烬1.5s
        
        # 炸弹列表
        self.bombs = []
        self.explosions = []
        self.bomb_wave = 0
        self.bombs_per_wave = 10
        self.wave_interval = 18
        
        # 新增：战斗机编队
        self.bombers = []
        self.bomber_spawn_timer = 0
        
        # 新增：雷达扫描线
        self.radar_angle = 0
        
        # 新增：冲击波
        self.shockwaves = []
        
        # 新增：火焰痕迹
        self.fire_trails = []
        
        # 新增：碎片粒子
        self.debris = []
        
        # 新增：烟柱
        self.smoke_columns = []
        
        # 新增：闪电
        self.lightning_bolts = []
        
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
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        if self.phase == 0:
            self._phase1_warning()
        elif self.phase == 1:
            self._phase2_bombing()
        elif self.phase == 2:
            self._phase3_aftermath()
        
        self._update_bombers()
        self._update_bombs()
        self._update_explosions()
        self._update_shockwaves()
        self._update_fire_trails()
        self._update_debris()
        self._update_smoke_columns()
        self._update_lightning()
    
    def _phase1_warning(self):
        """第一阶段：预警 - 雷达扫描+轰炸机编队进场"""
        progress = self.frame / self.phase_duration[0]
        
        # 屏幕边缘红色警告脉冲
        pulse = abs(math.sin(self.frame * 0.3))
        edge_alpha = int(80 * pulse * progress)
        edge_width = int(30 + 20 * pulse)
        
        # 四边警告框
        pygame.draw.rect(self.image, (255, 0, 0, edge_alpha), (0, 0, WIDTH, edge_width))
        pygame.draw.rect(self.image, (255, 0, 0, edge_alpha), (0, HEIGHT - edge_width, WIDTH, edge_width))
        pygame.draw.rect(self.image, (255, 0, 0, edge_alpha), (0, 0, edge_width, HEIGHT))
        pygame.draw.rect(self.image, (255, 0, 0, edge_alpha), (WIDTH - edge_width, 0, edge_width, HEIGHT))
        
        # 雷达扫描效果
        self.radar_angle += 0.15
        radar_cx, radar_cy = WIDTH // 2, HEIGHT // 2
        radar_radius = int(min(WIDTH, HEIGHT) * 0.4 * progress)
        
        # 雷达圆环
        for i in range(3):
            r = int(radar_radius * (i + 1) / 3)
            if r > 0:
                pygame.draw.circle(self.image, (0, 255, 0, int(60 * progress)), 
                                 (radar_cx, radar_cy), r, 1)
        
        # 雷达扫描线
        scan_len = radar_radius
        scan_x = radar_cx + int(math.cos(self.radar_angle) * scan_len)
        scan_y = radar_cy + int(math.sin(self.radar_angle) * scan_len)
        pygame.draw.line(self.image, (0, 255, 0, int(150 * progress)),
                        (radar_cx, radar_cy), (scan_x, scan_y), 2)
        
        # 扫描尾迹
        for i in range(10):
            trail_angle = self.radar_angle - i * 0.05
            trail_alpha = int(100 * (1 - i / 10) * progress)
            tx = radar_cx + int(math.cos(trail_angle) * scan_len)
            ty = radar_cy + int(math.sin(trail_angle) * scan_len)
            pygame.draw.line(self.image, (0, 255, 0, trail_alpha),
                           (radar_cx, radar_cy), (tx, ty), 1)
        
        # 目标标记点
        for i in range(self.bombs_per_wave):
            target_x = int(WIDTH * (i + 0.5) / self.bombs_per_wave)
            target_y = HEIGHT - 100
            
            # 闪烁的十字准星
            if self.frame % 8 < 4:
                cross_size = int(15 * progress)
                pygame.draw.line(self.image, (255, 0, 0, int(200 * progress)),
                               (target_x - cross_size, target_y), (target_x + cross_size, target_y), 2)
                pygame.draw.line(self.image, (255, 0, 0, int(200 * progress)),
                               (target_x, target_y - cross_size), (target_x, target_y + cross_size), 2)
                # 瞄准圈
                pygame.draw.circle(self.image, (255, 0, 0, int(150 * progress)),
                                 (target_x, target_y), int(20 * progress), 1)
        
        # 轰炸机编队从屏幕左上角进入
        if self.frame > 15 and self.frame % 10 == 0:
            self._spawn_bomber()
        
        # 警告文字背景
        text_alpha = int(200 * pulse * progress)
        pygame.draw.rect(self.image, (0, 0, 0, int(150 * progress)),
                        (WIDTH // 2 - 100, 50, 200, 40))
        pygame.draw.rect(self.image, (255, 0, 0, text_alpha),
                        (WIDTH // 2 - 100, 50, 200, 40), 2)
    
    def _phase2_bombing(self):
        """第二阶段：地毯轰炸 - 炸弹雨+爆炸链"""
        # 生成炸弹波
        if self.frame % self.wave_interval == 0:
            self._spawn_bomb_wave()
        
        # 持续生成轰炸机
        self.bomber_spawn_timer += 1
        if self.bomber_spawn_timer >= 30:
            self._spawn_bomber()
            self.bomber_spawn_timer = 0
        
        # 天空染色 - 战争迷雾
        progress = self.frame / self.phase_duration[1]
        smoke_intensity = int(40 * (0.5 + 0.5 * math.sin(self.frame * 0.08)))
        
        # 多层烟雾渐变
        for i in range(5):
            layer_y = int(i * HEIGHT / 5)
            layer_alpha = smoke_intensity - i * 5
            if layer_alpha > 0:
                pygame.draw.rect(self.image, (*self.theme["smoke"], layer_alpha),
                               (0, layer_y, WIDTH, HEIGHT // 5))
        
        # 毒气扩散波纹
        wave_count = 3
        for i in range(wave_count):
            wave_progress = ((self.frame + i * 30) % 90) / 90
            wave_radius = int(WIDTH * 0.8 * wave_progress)
            wave_alpha = int(30 * (1 - wave_progress))
            if wave_radius > 0 and wave_alpha > 0:
                pygame.draw.circle(self.image, (*self.theme["toxic"], wave_alpha),
                                 (WIDTH // 2, HEIGHT // 2), wave_radius, 2)
        
        # 地面火光闪烁
        if random.random() < 0.3:
            flash_x = random.randint(0, WIDTH)
            flash_y = HEIGHT - random.randint(20, 100)
            flash_r = random.randint(30, 60)
            pygame.draw.circle(self.image, (255, 200, 100, 100),
                             (flash_x, flash_y), flash_r)
        
        # 随机闪电（轰炸产生的电磁干扰）
        if random.random() < 0.05:
            self._spawn_lightning()
    
    def _phase3_aftermath(self):
        """第三阶段：余烬 - 废墟+残火+毒烟"""
        progress = self.frame / self.phase_duration[2]
        
        # 地面焦土效果
        scorched_alpha = int(80 * (1 - progress))
        if scorched_alpha > 0:
            # 简化焦土层
            pygame.draw.rect(self.image, (50, 35, 20, scorched_alpha), 
                           (0, HEIGHT - 100, WIDTH, 100))
        
        # 升腾的毒烟柱（优化：减少烟柱数量）
        smoke_count = 4  # 从8减少到4
        for i in range(smoke_count):
            sx = int(WIDTH * (i + 0.5) / smoke_count)
            sy = HEIGHT - 80
            sway = math.sin(self.frame * 0.1 + i) * 10
            
            # 简化烟雾层（从5层减少到2层）
            for j in range(2):
                smoke_y = sy - j * 60
                smoke_size = int((35 - j * 10) * (1 - progress * 0.5))
                smoke_a = int((60 - j * 20) * (1 - progress))
                
                if smoke_size > 0 and smoke_a > 0:
                    pygame.draw.circle(self.image, (*self.theme["smoke"], smoke_a),
                                     (int(sx + sway * (j + 1) * 0.3), smoke_y), smoke_size)
        
        # 残余火星（优化：减少数量）
        if progress < 0.7:
            ember_count = int(8 * (1 - progress))  # 从20减少到8
            for _ in range(ember_count):
                ex = random.randint(0, WIDTH)
                ey = HEIGHT - random.randint(50, 150) - int(self.frame * 0.5) % 50
                pygame.draw.circle(self.image, (255, 150, 30, int(200 * (1 - progress))),
                                 (ex, ey), random.randint(1, 3))
        
        # 辐射尘埃飘落（优化：减少数量）
        dust_alpha = int(40 * (1 - progress))
        if dust_alpha > 0:
            for i in range(12):  # 从30减少到12
                dx = (i * 47 + self.frame * 2) % WIDTH
                dy = (i * 31 + self.frame) % HEIGHT
                pygame.draw.circle(self.image, (*self.theme["toxic"], dust_alpha),
                                 (dx, dy), 2)
    
    def _spawn_bomber(self):
        """生成轰炸机"""
        # 从不同方向进入
        side = random.choice(['left', 'right', 'top'])
        
        if side == 'left':
            x, y = -50, random.randint(50, 150)
            vx, vy = random.uniform(4, 6), random.uniform(0.5, 1)
        elif side == 'right':
            x, y = WIDTH + 50, random.randint(50, 150)
            vx, vy = random.uniform(-6, -4), random.uniform(0.5, 1)
        else:
            x, y = random.randint(100, WIDTH - 100), -50
            vx, vy = random.uniform(-1, 1), random.uniform(3, 5)
        
        self.bombers.append({
            'x': x, 'y': y,
            'vx': vx, 'vy': vy,
            'size': random.randint(25, 35),
            'trail': []
        })
    
    def _update_bombers(self):
        """更新轰炸机"""
        for bomber in self.bombers[:]:
            bomber['x'] += bomber['vx']
            bomber['y'] += bomber['vy']
            
            # 添加尾迹
            bomber['trail'].append((bomber['x'], bomber['y']))
            if len(bomber['trail']) > 15:
                bomber['trail'].pop(0)
            
            # 超出屏幕移除
            if (bomber['x'] < -100 or bomber['x'] > WIDTH + 100 or
                bomber['y'] < -100 or bomber['y'] > HEIGHT + 100):
                self.bombers.remove(bomber)
                continue
            
            bx, by = int(bomber['x']), int(bomber['y'])
            size = bomber['size']
            
            # 绘制尾迹（引擎烟雾）
            for i, (tx, ty) in enumerate(bomber['trail']):
                trail_alpha = int(80 * i / len(bomber['trail']))
                trail_size = int(size * 0.15 * (i / len(bomber['trail'])))
                if trail_size > 0:
                    pygame.draw.circle(self.image, (*self.theme["smoke"], trail_alpha),
                                     (int(tx), int(ty)), trail_size)
            
            # 机身
            body_color = self.theme["armor"]
            pygame.draw.ellipse(self.image, body_color,
                              (bx - size, by - size // 4, size * 2, size // 2))
            
            # 机翼
            wing_span = size * 1.5
            pygame.draw.polygon(self.image, body_color, [
                (bx - wing_span, by),
                (bx - size // 2, by - size // 6),
                (bx - size // 2, by + size // 6),
                (bx - wing_span, by + size // 4)
            ])
            pygame.draw.polygon(self.image, body_color, [
                (bx + wing_span, by),
                (bx + size // 2, by - size // 6),
                (bx + size // 2, by + size // 6),
                (bx + wing_span, by + size // 4)
            ])
            
            # 机头
            pygame.draw.polygon(self.image, self.theme["rust"], [
                (bx + size, by),
                (bx + size + 15, by),
                (bx + size, by - size // 6),
                (bx + size, by + size // 6)
            ])
            
            # 驾驶舱
            pygame.draw.ellipse(self.image, (100, 150, 200),
                              (bx + size // 3, by - size // 6, size // 3, size // 4))
            
            # 引擎火焰
            flame_size = int(8 + 4 * math.sin(self.total_frame * 0.5))
            pygame.draw.circle(self.image, (255, 200, 100),
                             (bx - size - 5, by), flame_size)
            pygame.draw.circle(self.image, (255, 100, 50),
                             (bx - size - 8, by), flame_size // 2)
    
    def _spawn_bomb_wave(self):
        """生成一波炸弹"""
        # 波浪式分布
        wave_offset = math.sin(self.bomb_wave * 0.5) * 50
        
        for i in range(self.bombs_per_wave):
            x = int(WIDTH * (i + 0.5) / self.bombs_per_wave) + random.randint(-30, 30)
            y = -20 + wave_offset + random.randint(-20, 20)
            
            self.bombs.append({
                'x': x,
                'y': y,
                'vy': random.uniform(7, 12),
                'size': random.randint(10, 16),
                'rotation': random.uniform(0, math.pi * 2),
                'trail': [],
                'wobble': random.uniform(-0.5, 0.5)
            })
        
        self.bomb_wave += 1
    
    def _update_bombs(self):
        """更新炸弹"""
        for bomb in self.bombs[:]:
            bomb['y'] += bomb['vy']
            bomb['vy'] += 0.15  # 加速度
            bomb['rotation'] += 0.1
            bomb['x'] += bomb['wobble']  # 轻微横向摆动
            
            # 记录轨迹
            bomb['trail'].append((bomb['x'], bomb['y']))
            if len(bomb['trail']) > 8:
                bomb['trail'].pop(0)
            
            # 落地爆炸
            if bomb['y'] > HEIGHT - 50:
                self._create_explosion(bomb['x'], bomb['y'])
                self.bombs.remove(bomb)
                continue
            
            # 绘制炸弹尾迹
            for i, (tx, ty) in enumerate(bomb['trail']):
                trail_alpha = int(150 * i / len(bomb['trail']))
                trail_size = int(bomb['size'] * 0.3 * (i / len(bomb['trail'])))
                if trail_size > 0:
                    pygame.draw.circle(self.image, (*self.theme["toxic"], trail_alpha),
                                     (int(tx), int(ty)), trail_size)
            
            # 绘制炸弹
            bx, by = int(bomb['x']), int(bomb['y'])
            size = bomb['size']
            
            # 炸弹体 - 更精细的绘制
            pygame.draw.ellipse(self.image, self.theme["armor"], 
                              (bx - size//2, by - size, size, size * 2))
            # 尾翼 - 十字形
            pygame.draw.polygon(self.image, self.theme["rust"], [
                (bx - size//2, by - size),
                (bx + size//2, by - size),
                (bx, by - size - 12)
            ])
            pygame.draw.polygon(self.image, self.theme["rust"], [
                (bx - size//2 - 5, by - size + 5),
                (bx + size//2 + 5, by - size + 5),
                (bx, by - size + 5)
            ])
            
            # 危险标志 - 核辐射符号
            pygame.draw.circle(self.image, self.theme["toxic"], (bx, by), 5)
            pygame.draw.circle(self.image, (0, 0, 0), (bx, by), 3)
            
            # 尾部火焰
            flame_len = int(10 + 5 * math.sin(self.total_frame * 0.5 + bomb['rotation']))
            pygame.draw.polygon(self.image, (255, 200, 100, 200), [
                (bx - 3, by + size),
                (bx + 3, by + size),
                (bx, by + size + flame_len)
            ])
            pygame.draw.polygon(self.image, (255, 100, 50, 150), [
                (bx - 2, by + size),
                (bx + 2, by + size),
                (bx, by + size + flame_len - 3)
            ])
    
    def _create_explosion(self, x, y):
        """创建爆炸 - 增强版多层爆炸"""
        self.explosions.append({
            'x': x,
            'y': y,
            'frame': 0,
            'max_frame': 45,
            'radius': 0,
            'type': random.choice(['normal', 'toxic', 'fire'])
        })
        
        # 添加冲击波
        self.shockwaves.append({
            'x': x, 'y': y,
            'radius': 0,
            'max_radius': random.randint(80, 120),
            'frame': 0
        })
        
        # 添加火焰痕迹
        self.fire_trails.append({
            'x': x, 'y': y,
            'frame': 0,
            'max_frame': 60
        })
        
        # 添加碎片
        for _ in range(8):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(3, 8)
            self.debris.append({
                'x': x, 'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 3,
                'size': random.randint(2, 5),
                'frame': 0,
                'max_frame': random.randint(20, 40),
                'color': random.choice([self.theme["armor"], self.theme["rust"], (100, 100, 100)])
            })
        
        # 造成伤害
        from sprites import FloatingText, Particle
        
        explosion_radius = 100
        for mob in list(mobs):
            dist = math.sqrt((mob.rect.centerx - x)**2 + (mob.rect.centery - y)**2)
            if dist < explosion_radius:
                dmg_mult = 1 - (dist / explosion_radius) * 0.5
                final_damage = int(self.damage * 0.5 * dmg_mult)
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(final_damage)
                else:
                    mob.hp -= final_damage
                FloatingText(mob.rect.centerx, mob.rect.top - 10,
                           f"-{final_damage}", self.theme["toxic"])
        
        # 特效
        for _ in range(8):
            Particle((x, y), self.theme["toxic"], mode='spark')
        
        # 小毒云
        if random.random() < 0.4:
            PlagueCloud(x, y, self.damage * 0.15, self.owner, self.style, duration=120)
        
        # 添加烟柱
        if random.random() < 0.5:
            self.smoke_columns.append({
                'x': x + random.randint(-20, 20),
                'y': y,
                'frame': 0,
                'max_frame': 90,
                'height': 0
            })
    
    def _update_explosions(self):
        """更新爆炸效果 - 增强版"""
        for exp in self.explosions[:]:
            exp['frame'] += 1
            progress = exp['frame'] / exp['max_frame']
            
            # 爆炸半径先快速扩张后缓慢
            if progress < 0.3:
                exp['radius'] = int(100 * (progress / 0.3))
            else:
                exp['radius'] = int(100 * (1 + 0.3 * (progress - 0.3) / 0.7))
            
            if exp['frame'] >= exp['max_frame']:
                self.explosions.remove(exp)
                continue
            
            ex, ey = int(exp['x']), int(exp['y'])
            
            # 根据类型绘制不同爆炸
            if exp['type'] == 'toxic':
                # 毒气爆炸 - 绿色为主
                alpha = int(200 * (1 - progress))
                
                # 毒雾扩散
                for i in range(3):
                    r = int(exp['radius'] * (0.6 + i * 0.2))
                    a = int(alpha * (1 - i * 0.3))
                    if r > 0 and a > 0:
                        pygame.draw.circle(self.image, (*self.theme["toxic"], a),
                                         (ex, ey), r)
                
                # 毒液飞溅
                for i in range(6):
                    angle = i * math.pi / 3 + progress * 2
                    dist = exp['radius'] * (0.5 + 0.3 * math.sin(progress * 5 + i))
                    sx = ex + int(math.cos(angle) * dist)
                    sy = ey + int(math.sin(angle) * dist)
                    pygame.draw.circle(self.image, (*self.theme["toxic"], int(alpha * 0.8)),
                                     (sx, sy), int(8 * (1 - progress)))
            
            elif exp['type'] == 'fire':
                # 火焰爆炸 - 橙红色
                colors = [
                    (255, 255, 200),  # 中心白热
                    (255, 200, 100),  # 内层橙黄
                    (255, 100, 50),   # 中层橙红
                    (200, 50, 20),    # 外层深红
                ]
                
                for i, color in enumerate(colors):
                    r = int(exp['radius'] * (1 - i * 0.2))
                    a = int(200 * (1 - progress) * (1 - i * 0.2))
                    if r > 0 and a > 0:
                        pygame.draw.circle(self.image, (*color, a), (ex, ey), r)
                
                # 火舌
                for i in range(8):
                    angle = i * math.pi / 4 + self.total_frame * 0.1
                    flame_len = exp['radius'] * (0.5 + 0.3 * random.random())
                    fx = ex + int(math.cos(angle) * flame_len)
                    fy = ey + int(math.sin(angle) * flame_len)
                    pygame.draw.circle(self.image, (255, 150, 50, int(150 * (1 - progress))),
                                     (fx, fy), int(12 * (1 - progress)))
            
            else:  # normal
                # 标准爆炸
                alpha = int(200 * (1 - progress))
                
                # 外圈 - 冲击波
                pygame.draw.circle(self.image, (*self.theme["glow"], int(alpha * 0.5)),
                                 (ex, ey), exp['radius'], 4)
                
                # 中圈 - 火球
                inner_r = int(exp['radius'] * 0.7)
                if inner_r > 0:
                    pygame.draw.circle(self.image, (255, 200, 100, alpha),
                                     (ex, ey), inner_r)
                
                # 内圈 - 核心
                core_r = int(exp['radius'] * 0.4)
                if core_r > 0:
                    pygame.draw.circle(self.image, (255, 255, 200, int(alpha * 1.2)),
                                     (ex, ey), core_r)
                
                # 毒气晕染
                toxic_r = int(exp['radius'] * 0.5)
                if toxic_r > 0:
                    pygame.draw.circle(self.image, (*self.theme["toxic"], int(alpha * 0.6)),
                                     (ex, ey), toxic_r)
    
    def _update_shockwaves(self):
        """更新冲击波"""
        for sw in self.shockwaves[:]:
            sw['frame'] += 1
            progress = sw['frame'] / 20
            sw['radius'] = int(sw['max_radius'] * progress)
            
            if progress >= 1:
                self.shockwaves.remove(sw)
                continue
            
            alpha = int(150 * (1 - progress))
            if sw['radius'] > 0 and alpha > 0:
                # 主冲击波
                pygame.draw.circle(self.image, (255, 255, 255, alpha),
                                 (int(sw['x']), int(sw['y'])), sw['radius'], 3)
                # 内层
                inner_r = int(sw['radius'] * 0.8)
                if inner_r > 0:
                    pygame.draw.circle(self.image, (*self.theme["glow"], int(alpha * 0.7)),
                                     (int(sw['x']), int(sw['y'])), inner_r, 2)
    
    def _update_fire_trails(self):
        """更新火焰痕迹"""
        for ft in self.fire_trails[:]:
            ft['frame'] += 1
            progress = ft['frame'] / ft['max_frame']
            
            if progress >= 1:
                self.fire_trails.remove(ft)
                continue
            
            fx, fy = int(ft['x']), int(ft['y'])
            
            # 地面燃烧
            burn_width = int(60 * (1 - progress * 0.5))
            burn_height = int(20 * (1 - progress))
            burn_alpha = int(150 * (1 - progress))
            
            if burn_width > 0 and burn_height > 0:
                # 火焰底座
                pygame.draw.ellipse(self.image, (255, 100, 30, burn_alpha),
                                  (fx - burn_width//2, fy - burn_height//2, burn_width, burn_height))
                
                # 跳动的火苗
                for i in range(5):
                    flame_x = fx + random.randint(-burn_width//3, burn_width//3)
                    flame_height = int(20 * (1 - progress) * (0.5 + 0.5 * random.random()))
                    if flame_height > 3:
                        pygame.draw.polygon(self.image, (255, 200, 100, int(burn_alpha * 0.8)), [
                            (flame_x - 4, fy),
                            (flame_x + 4, fy),
                            (flame_x, fy - flame_height)
                        ])
    
    def _update_debris(self):
        """更新碎片"""
        for d in self.debris[:]:
            d['frame'] += 1
            d['x'] += d['vx']
            d['y'] += d['vy']
            d['vy'] += 0.3  # 重力
            
            if d['frame'] >= d['max_frame']:
                self.debris.remove(d)
                continue
            
            progress = d['frame'] / d['max_frame']
            alpha = int(255 * (1 - progress))
            
            if alpha > 0:
                pygame.draw.circle(self.image, (*d['color'], alpha),
                                 (int(d['x']), int(d['y'])), d['size'])
    
    def _update_smoke_columns(self):
        """更新烟柱"""
        for sc in self.smoke_columns[:]:
            sc['frame'] += 1
            progress = sc['frame'] / sc['max_frame']
            sc['height'] = min(150, sc['frame'] * 3)
            
            if progress >= 1:
                self.smoke_columns.remove(sc)
                continue
            
            sx, sy = int(sc['x']), int(sc['y'])
            
            # 多层烟雾
            layers = 6
            for i in range(layers):
                layer_y = sy - int(sc['height'] * (i + 1) / layers)
                layer_size = int((40 - i * 5) * (1 - progress * 0.5))
                layer_alpha = int((80 - i * 10) * (1 - progress))
                
                # 随风摆动
                sway = math.sin(self.total_frame * 0.05 + i * 0.5) * (i + 1) * 3
                
                if layer_size > 0 and layer_alpha > 0:
                    pygame.draw.circle(self.image, (*self.theme["smoke"], layer_alpha),
                                     (int(sx + sway), layer_y), layer_size)
    
    def _spawn_lightning(self):
        """生成闪电"""
        start_x = random.randint(50, WIDTH - 50)
        self.lightning_bolts.append({
            'start': (start_x, 0),
            'end': (start_x + random.randint(-100, 100), HEIGHT),
            'frame': 0,
            'max_frame': 8,
            'branches': self._generate_lightning_path(start_x, 0, start_x + random.randint(-50, 50), HEIGHT)
        })
    
    def _generate_lightning_path(self, x1, y1, x2, y2, depth=0):
        """生成闪电路径"""
        if depth > 4:
            return [(x1, y1), (x2, y2)]
        
        mid_x = (x1 + x2) // 2 + random.randint(-30, 30)
        mid_y = (y1 + y2) // 2
        
        path = [(x1, y1), (mid_x, mid_y)]
        
        # 随机分支
        if random.random() < 0.3 and depth < 3:
            branch_end_x = mid_x + random.randint(-50, 50)
            branch_end_y = mid_y + random.randint(30, 80)
            path.extend(self._generate_lightning_path(mid_x, mid_y, branch_end_x, branch_end_y, depth + 2))
        
        path.extend(self._generate_lightning_path(mid_x, mid_y, x2, y2, depth + 1))
        return path
    
    def _update_lightning(self):
        """更新闪电"""
        for bolt in self.lightning_bolts[:]:
            bolt['frame'] += 1
            
            if bolt['frame'] >= bolt['max_frame']:
                self.lightning_bolts.remove(bolt)
                continue
            
            progress = bolt['frame'] / bolt['max_frame']
            alpha = int(255 * (1 - progress))
            
            # 绘制闪电路径
            if len(bolt['branches']) >= 2:
                for i in range(len(bolt['branches']) - 1):
                    p1 = bolt['branches'][i]
                    p2 = bolt['branches'][i + 1]
                    
                    # 主闪电
                    pygame.draw.line(self.image, (200, 200, 255, alpha),
                                   p1, p2, 3)
                    # 内核
                    pygame.draw.line(self.image, (255, 255, 255, alpha),
                                   p1, p2, 1)


# ==================== G技能：瘟疫核弹 ====================
class PlagueNukeSkill(pygame.sprite.Sprite):
    """
    瘟疫核弹 - G技能
    投下巨大绿色核弹，蘑菇云清屏
    增强版：核弹详细建模、下落尾迹、多层蘑菇云、辐射波、地面焦化
    """
    
    def __init__(self, owner, damage, style="default"):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.style = style
        self.theme = get_theme(style)
        
        self.frame = 0
        self.total_frame = 0
        self.phase = 0
        self.phase_duration = [90, 45, 180]  # 投弹1.5s, 爆炸0.75s, 蘑菇云3s
        
        # 核弹位置
        self.nuke_x = WIDTH // 2
        self.nuke_y = -150
        self.nuke_target_y = HEIGHT // 2
        self.nuke_rotation = 0
        self.nuke_trail = []
        
        # 蘑菇云
        self.mushroom_radius = 0
        self.stem_height = 0
        
        # 冲击波
        self.shockwaves = []
        
        # 辐射粒子
        self.radiation_particles = []
        
        # 碎片
        self.debris = []
        
        # 地面裂痕
        self.ground_cracks = []
        
        # 闪光
        self.flash_intensity = 0
        
        # 辐射云层
        self.radiation_clouds = []
        
        # 落灰
        self.fallout = []
        
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
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        if self.phase == 0:
            self._phase1_drop()
        elif self.phase == 1:
            self._phase2_explosion()
        elif self.phase == 2:
            self._phase3_mushroom()
        
        self._update_shockwaves()
        self._update_radiation_particles()
        self._update_debris()
        self._update_radiation_clouds()
        self._update_fallout()
    
    def _phase1_drop(self):
        """第一阶段：核弹下落 - 增强版"""
        progress = self.frame / self.phase_duration[0]
        
        # 核弹下落 - 带加速度
        fall_progress = progress ** 1.5  # 加速曲线
        self.nuke_y = -150 + (self.nuke_target_y + 150) * fall_progress
        self.nuke_rotation += 0.02
        
        # 记录尾迹
        self.nuke_trail.append((self.nuke_x, self.nuke_y))
        if len(self.nuke_trail) > 30:
            self.nuke_trail.pop(0)
        
        # 绘制下落尾迹
        for i, (tx, ty) in enumerate(self.nuke_trail):
            trail_alpha = int(150 * i / len(self.nuke_trail))
            trail_size = int(25 * i / len(self.nuke_trail))
            
            # 火焰尾迹
            pygame.draw.circle(self.image, (255, 150, 50, trail_alpha),
                             (int(tx), int(ty)), trail_size)
            pygame.draw.circle(self.image, (255, 200, 100, trail_alpha // 2),
                             (int(tx), int(ty)), trail_size // 2)
        
        # 绘制核弹 - 详细版
        nuke_size = 60
        nx, ny = int(self.nuke_x), int(self.nuke_y)
        
        # 弹体主体
        body_color = self.theme["armor"]
        pygame.draw.ellipse(self.image, body_color,
                          (nx - nuke_size//2, ny - nuke_size * 1.5, nuke_size, nuke_size * 3))
        
        # 弹体高光
        highlight_color = tuple(min(255, c + 40) for c in body_color[:3])
        pygame.draw.ellipse(self.image, highlight_color,
                          (nx - nuke_size//3, ny - nuke_size * 1.3, nuke_size//3, nuke_size * 2))
        
        # 弹头锥形
        nose_points = [
            (nx, ny - nuke_size * 1.5 - 30),
            (nx - nuke_size//2, ny - nuke_size * 1.5),
            (nx + nuke_size//2, ny - nuke_size * 1.5)
        ]
        pygame.draw.polygon(self.image, self.theme["rust"], nose_points)
        pygame.draw.polygon(self.image, body_color, nose_points, 2)
        
        # 尾翼 - 四片
        for i in range(4):
            angle = i * math.pi / 2 + self.nuke_rotation
            fin_base_x = nx + int(math.cos(angle) * nuke_size // 2)
            fin_base_y = ny + nuke_size
            fin_tip_x = nx + int(math.cos(angle) * (nuke_size // 2 + 25))
            fin_tip_y = ny + nuke_size + 15
            
            fin_points = [
                (fin_base_x, fin_base_y - 20),
                (fin_tip_x, fin_tip_y),
                (fin_base_x, fin_base_y + 10)
            ]
            pygame.draw.polygon(self.image, self.theme["rust"], fin_points)
        
        # 核辐射标志 - 大号
        rad_y = ny
        rad_size = 20
        pygame.draw.circle(self.image, self.theme["toxic"], (nx, rad_y), rad_size)
        pygame.draw.circle(self.image, (0, 0, 0), (nx, rad_y), rad_size - 6)
        
        # 简化三叶草辐射符号 - 只画3个圆
        for i in range(3):
            angle = i * 2 * math.pi / 3 - math.pi / 2 + self.nuke_rotation
            lx = nx + int(math.cos(angle) * (rad_size - 4))
            ly = rad_y + int(math.sin(angle) * (rad_size - 4))
            pygame.draw.circle(self.image, self.theme["toxic"], (lx, ly), 5)
        
        # 弹体上的条纹
        stripe_count = 5
        for i in range(stripe_count):
            stripe_y = ny - nuke_size + i * (nuke_size * 2 // stripe_count)
            stripe_alpha = 100
            pygame.draw.line(self.image, (*self.theme["rust"], stripe_alpha),
                           (nx - nuke_size//2 + 5, stripe_y),
                           (nx + nuke_size//2 - 5, stripe_y), 2)
        
        # 尾部推进火焰
        flame_len = int(50 + 20 * math.sin(self.frame * 0.3))
        flame_width = 25
        
        # 外层火焰
        pygame.draw.polygon(self.image, (255, 100, 30, 200), [
            (nx - flame_width, ny + nuke_size * 1.5),
            (nx + flame_width, ny + nuke_size * 1.5),
            (nx, ny + nuke_size * 1.5 + flame_len)
        ])
        # 中层火焰
        pygame.draw.polygon(self.image, (255, 180, 80, 220), [
            (nx - flame_width * 0.6, ny + nuke_size * 1.5),
            (nx + flame_width * 0.6, ny + nuke_size * 1.5),
            (nx, ny + nuke_size * 1.5 + flame_len * 0.8)
        ])
        # 内核
        pygame.draw.polygon(self.image, (255, 255, 200, 255), [
            (nx - flame_width * 0.3, ny + nuke_size * 1.5),
            (nx + flame_width * 0.3, ny + nuke_size * 1.5),
            (nx, ny + nuke_size * 1.5 + flame_len * 0.5)
        ])
        
        # 火花粒子
        for _ in range(3):
            spark_x = nx + random.randint(-20, 20)
            spark_y = ny + nuke_size * 1.5 + flame_len + random.randint(0, 20)
            pygame.draw.circle(self.image, (255, 200, 100, 200),
                             (spark_x, spark_y), random.randint(2, 4))
        
        # 警告线 - 动态虚线
        dash_len = 10
        dash_gap = 10
        current_y = ny + nuke_size * 1.5 + flame_len
        dash_offset = (self.frame * 5) % (dash_len + dash_gap)
        
        while current_y < HEIGHT:
            if (current_y + dash_offset) % (dash_len + dash_gap) < dash_len:
                pygame.draw.line(self.image, (255, 0, 0, 180),
                               (nx, current_y), (nx, min(current_y + dash_len, HEIGHT)), 2)
            current_y += 1
        
        # 目标点标记
        target_pulse = abs(math.sin(self.frame * 0.2))
        target_size = int(40 + 20 * target_pulse)
        target_y = int(self.nuke_target_y)
        
        # 十字准星
        pygame.draw.line(self.image, (255, 0, 0, int(200 * target_pulse)),
                        (nx - target_size, target_y), (nx + target_size, target_y), 2)
        pygame.draw.line(self.image, (255, 0, 0, int(200 * target_pulse)),
                        (nx, target_y - target_size), (nx, target_y + target_size), 2)
        # 瞄准圈
        pygame.draw.circle(self.image, (255, 0, 0, int(150 * target_pulse)),
                         (nx, target_y), target_size, 2)
        pygame.draw.circle(self.image, (255, 0, 0, int(100 * target_pulse)),
                         (nx, target_y), target_size // 2, 1)
        
        # 屏幕边缘警告
        edge_pulse = abs(math.sin(self.frame * 0.15))
        edge_alpha = int(60 * edge_pulse * progress)
        edge_width = 20
        pygame.draw.rect(self.image, (255, 0, 0, edge_alpha), (0, 0, WIDTH, edge_width))
        pygame.draw.rect(self.image, (255, 0, 0, edge_alpha), (0, HEIGHT - edge_width, WIDTH, edge_width))
    
    def _phase2_explosion(self):
        """第二阶段：爆炸 - 增强版核爆"""
        progress = self.frame / self.phase_duration[1]
        
        # 强烈白闪
        if progress < 0.3:
            flash_progress = progress / 0.3
            flash_alpha = int(255 * (1 - flash_progress ** 2))
            pygame.draw.rect(self.image, (255, 255, 240, flash_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 造成伤害 - 只在第一帧
        if self.frame == 1:
            self._deal_nuke_damage()
            
            # 生成大量辐射粒子
            for _ in range(50):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(5, 15)
                self.radiation_particles.append({
                    'x': self.nuke_x,
                    'y': self.nuke_target_y,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'size': random.randint(3, 8),
                    'life': random.randint(30, 60),
                    'max_life': random.randint(30, 60)
                })
            
            # 生成碎片
            for _ in range(30):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(8, 20)
                self.debris.append({
                    'x': self.nuke_x,
                    'y': self.nuke_target_y,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed - 5,
                    'size': random.randint(4, 12),
                    'rotation': random.uniform(0, math.pi * 2),
                    'rot_speed': random.uniform(-0.3, 0.3),
                    'life': random.randint(40, 80)
                })
            
            # 生成地面裂痕
            for i in range(8):
                angle = i * math.pi / 4
                self.ground_cracks.append({
                    'start_x': self.nuke_x,
                    'start_y': self.nuke_target_y,
                    'angle': angle,
                    'length': 0,
                    'max_length': random.randint(150, 300)
                })
        
        # 多重冲击波
        if self.frame <= 30 and self.frame % 5 == 0:
            self.shockwaves.append({
                'x': self.nuke_x,
                'y': self.nuke_target_y,
                'radius': 0,
                'max_radius': WIDTH,
                'speed': 15 + self.frame,
                'alpha': 200
            })
        
        # 核心火球
        if progress < 0.8:
            fireball_radius = int(200 * (progress / 0.8))
            
            # 简化火球（3层代替5层）
            colors = [
                (255, 255, 255),  # 内核白
                (255, 200, 100),  # 橙黄
                (200, 50, 20),    # 深红
            ]
            
            for i, color in enumerate(colors):
                r = int(fireball_radius * (1 - i * 0.25))
                a = int(200 * (1 - progress / 0.8) * (1 - i * 0.2))
                if r > 0 and a > 0:
                    pygame.draw.circle(self.image, (*color, a),
                                     (int(self.nuke_x), int(self.nuke_target_y)), r)
            
            # 简化火球边缘扰动（从20个减少到8个）
            for i in range(8):
                angle = i * math.pi / 4 + self.frame * 0.1
                dist = fireball_radius + random.randint(-10, 30)
                fx = self.nuke_x + int(math.cos(angle) * dist)
                fy = self.nuke_target_y + int(math.sin(angle) * dist)
                pygame.draw.circle(self.image, (255, 150, 50, int(150 * (1 - progress))),
                                 (fx, fy), random.randint(8, 12))
        
        # 地面裂痕扩展
        for crack in self.ground_cracks:
            crack['length'] = min(crack['max_length'], crack['length'] + 15)
            
            end_x = crack['start_x'] + int(math.cos(crack['angle']) * crack['length'])
            end_y = crack['start_y'] + int(math.sin(crack['angle']) * crack['length'])
            
            # 主裂痕
            pygame.draw.line(self.image, (50, 30, 20, int(200 * (1 - progress * 0.5))),
                           (int(crack['start_x']), int(crack['start_y'])),
                           (end_x, end_y), 4)
            # 裂痕发光
            pygame.draw.line(self.image, (255, 100, 50, int(150 * (1 - progress))),
                           (int(crack['start_x']), int(crack['start_y'])),
                           (end_x, end_y), 2)
    
    def _phase3_mushroom(self):
        """第三阶段：蘑菇云 - 史诗级"""
        progress = self.frame / self.phase_duration[2]
        
        # 蘑菇云生长
        growth_curve = min(1, progress * 1.5)  # 先快后稳定
        self.mushroom_radius = int(200 * growth_curve)
        self.stem_height = int(280 * growth_curve)
        
        cx = int(self.nuke_x)
        cy = int(self.nuke_target_y)
        
        # 生成落灰
        if random.random() < 0.3:
            self.fallout.append({
                'x': random.randint(0, WIDTH),
                'y': 0,
                'vy': random.uniform(1, 3),
                'size': random.randint(1, 4),
                'sway': random.uniform(-0.5, 0.5)
            })
        
        # 生成辐射云
        if self.frame % 20 == 0 and len(self.radiation_clouds) < 10:
            angle = random.uniform(0, math.pi * 2)
            dist = random.randint(100, 250)
            self.radiation_clouds.append({
                'x': cx + int(math.cos(angle) * dist),
                'y': cy - self.stem_height // 2 + random.randint(-50, 50),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-0.5, 0.5),
                'size': random.randint(40, 80),
                'alpha': random.randint(60, 100)
            })
        
        # ====== 绘制蘑菇云 ======
        
        # 地面焦痕（简化：从5层减到2层）
        scorch_radius = int(180 * growth_curve)
        for i in range(2):
            r = scorch_radius - i * 40
            a = int(80 * (1 - progress * 0.3) * (1 - i * 0.3))
            if r > 0 and a > 0:
                pygame.draw.ellipse(self.image, (40, 25, 10, a),
                                  (cx - r, cy + 50 - r // 4, r * 2, r // 2))
        
        # 地面火焰（简化：从15个减到6个）
        if progress < 0.7:
            fire_intensity = 1 - progress / 0.7
            for i in range(6):
                angle = i * math.pi / 3 + self.frame * 0.03
                fire_dist = random.randint(20, int(80 * fire_intensity))
                fx = cx + int(math.cos(angle) * fire_dist)
                fy = cy + 30
                fire_height = int(30 * fire_intensity * random.random())
                
                if fire_height > 5:
                    pygame.draw.polygon(self.image, (255, 150, 50, int(200 * fire_intensity)), [
                        (fx - 5, fy), (fx + 5, fy), (fx, fy - fire_height)
                    ])
        
        # 云柱（茎）- 简化为4层
        stem_width_base = int(100 * growth_curve)
        stem_top = cy - self.stem_height
        
        stem_layers = 4
        for i in range(stem_layers):
            layer_y = cy - int(self.stem_height * i / stem_layers)
            layer_width = stem_width_base * (1 - i * 0.05)
            roll_offset = math.sin(self.frame * 0.1 + i * 0.5) * 15
            layer_alpha = int(120 * (1 - progress * 0.4))
            
            if layer_width > 0 and layer_alpha > 0:
                pygame.draw.ellipse(self.image, (*self.theme["smoke"], layer_alpha),
                                  (cx - layer_width//2 + roll_offset, layer_y - 15,
                                   layer_width, 30))
        
        # 蘑菇头 - 简化
        head_y = stem_top - self.mushroom_radius // 3
        
        # 主蘑菇头（简化为2层）
        for i in range(2):
            layer_r = self.mushroom_radius - i * 40
            layer_alpha = int((130 - i * 30) * (1 - progress * 0.4))
            vertical_squash = 0.55
            
            if layer_r > 0 and layer_alpha > 0:
                pygame.draw.ellipse(self.image, (*self.theme["smoke"], layer_alpha),
                                  (cx - layer_r, head_y - int(layer_r * vertical_squash),
                                   layer_r * 2, int(layer_r * vertical_squash * 2)))
        
        # 顶部云团（从8个减到3个）
        for i in range(3):
            angle = i * 2 * math.pi / 3 + self.frame * 0.03
            tc_x = cx + int(math.cos(angle) * self.mushroom_radius * 0.5)
            tc_y = head_y - self.mushroom_radius * 0.3
            tc_r = int(40 * (1 - progress * 0.3))
            tc_alpha = int(80 * (1 - progress * 0.5))
            
            if tc_r > 0 and tc_alpha > 0:
                pygame.draw.circle(self.image, (*self.theme["smoke"], tc_alpha),
                                 (tc_x, tc_y), tc_r)
        
        # 内部辐射光
        glow_r = int(self.mushroom_radius * 0.5)
        glow_intensity = 0.5 + 0.5 * math.sin(self.frame * 0.15)
        glow_alpha = int(100 * (1 - progress * 0.6) * glow_intensity)
        
        if glow_r > 0 and glow_alpha > 0:
            pygame.draw.ellipse(self.image, (*self.theme["toxic"], glow_alpha),
                              (cx - glow_r, head_y - glow_r//2, glow_r * 2, glow_r))
        
        # 飘散的辐射粒子环绕蘑菇云
        particle_count = 20
        for i in range(particle_count):
            p_angle = self.frame * 0.02 + i * math.pi * 2 / particle_count
            p_dist = self.mushroom_radius * (0.8 + 0.3 * math.sin(self.frame * 0.05 + i))
            p_height = math.sin(p_angle * 3 + self.frame * 0.1) * 50
            
            px = cx + int(math.cos(p_angle) * p_dist)
            py = head_y + int(p_height)
            p_size = int(6 * (1 - progress * 0.5) * (0.5 + 0.5 * math.sin(self.frame * 0.2 + i)))
            p_alpha = int(150 * (1 - progress * 0.6))
            
            if p_size > 0 and p_alpha > 0:
                pygame.draw.circle(self.image, (*self.theme["toxic"], p_alpha),
                                 (px, py), p_size)
        
        # 底部烟雾扩散
        base_smoke_count = 6
        for i in range(base_smoke_count):
            angle = i * math.pi * 2 / base_smoke_count + self.frame * 0.01
            smoke_dist = int(150 * growth_curve + self.frame * 0.5)
            smoke_x = cx + int(math.cos(angle) * smoke_dist)
            smoke_y = cy + 20
            smoke_r = int(60 * (1 - progress * 0.4))
            smoke_alpha = int(60 * (1 - progress * 0.5))
            
            if smoke_r > 0 and smoke_alpha > 0:
                pygame.draw.circle(self.image, (*self.theme["smoke"], smoke_alpha),
                                 (smoke_x, smoke_y), smoke_r)
        
        # 环形冲击波（持续扩散）
        ring_progress = (self.frame % 60) / 60
        ring_radius = int(300 * ring_progress)
        ring_alpha = int(50 * (1 - ring_progress) * (1 - progress * 0.5))
        
        if ring_radius > 0 and ring_alpha > 0:
            pygame.draw.circle(self.image, (*self.theme["toxic"], ring_alpha),
                             (cx, cy), ring_radius, 2)
        
        # 屏幕边缘辐射染色
        vignette_alpha = int(30 * (1 - progress * 0.7))
        if vignette_alpha > 0:
            vignette_width = 80
            for i in range(vignette_width):
                a = int(vignette_alpha * (1 - i / vignette_width))
                if a > 0:
                    pygame.draw.rect(self.image, (*self.theme["toxic"], a), (i, 0, 1, HEIGHT))
                    pygame.draw.rect(self.image, (*self.theme["toxic"], a), (WIDTH - i - 1, 0, 1, HEIGHT))
                    pygame.draw.rect(self.image, (*self.theme["toxic"], a), (0, i, WIDTH, 1))
                    pygame.draw.rect(self.image, (*self.theme["toxic"], a), (0, HEIGHT - i - 1, WIDTH, 1))
    
    def _update_shockwaves(self):
        """更新冲击波"""
        for sw in self.shockwaves[:]:
            sw['radius'] += sw['speed']
            sw['alpha'] = max(0, sw['alpha'] - 5)
            
            if sw['radius'] > sw['max_radius'] or sw['alpha'] <= 0:
                self.shockwaves.remove(sw)
                continue
            
            # 绘制冲击波
            if sw['alpha'] > 0:
                # 外环
                pygame.draw.circle(self.image, (255, 255, 255, sw['alpha']),
                                 (int(sw['x']), int(sw['y'])), int(sw['radius']), 4)
                # 内环
                inner_r = int(sw['radius'] * 0.9)
                if inner_r > 0:
                    pygame.draw.circle(self.image, (*self.theme["glow"], sw['alpha'] // 2),
                                     (int(sw['x']), int(sw['y'])), inner_r, 2)
    
    def _update_radiation_particles(self):
        """更新辐射粒子"""
        for p in self.radiation_particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vx'] *= 0.97  # 阻力
            p['vy'] *= 0.97
            p['life'] -= 1
            
            if p['life'] <= 0:
                self.radiation_particles.remove(p)
                continue
            
            alpha = int(200 * p['life'] / p['max_life'])
            if alpha > 0:
                pygame.draw.circle(self.image, (*self.theme["toxic"], alpha),
                                 (int(p['x']), int(p['y'])), p['size'])
                # 发光效果
                pygame.draw.circle(self.image, (*self.theme["glow"], alpha // 2),
                                 (int(p['x']), int(p['y'])), p['size'] + 2)
    
    def _update_debris(self):
        """更新碎片"""
        for d in self.debris[:]:
            d['x'] += d['vx']
            d['y'] += d['vy']
            d['vy'] += 0.4  # 重力
            d['rotation'] += d['rot_speed']
            d['life'] -= 1
            
            if d['life'] <= 0 or d['y'] > HEIGHT:
                self.debris.remove(d)
                continue
            
            # 绘制旋转碎片
            alpha = min(255, int(255 * d['life'] / 40))
            dx, dy = int(d['x']), int(d['y'])
            size = d['size']
            rot = d['rotation']
            
            # 不规则四边形碎片
            points = []
            for i in range(4):
                angle = rot + i * math.pi / 2
                dist = size * (0.7 + 0.3 * ((i + int(rot * 10)) % 3) / 2)
                px = dx + int(math.cos(angle) * dist)
                py = dy + int(math.sin(angle) * dist)
                points.append((px, py))
            
            pygame.draw.polygon(self.image, (*self.theme["armor"], alpha), points)
            # 高温边缘
            pygame.draw.polygon(self.image, (255, 150, 50, alpha // 2), points, 1)
    
    def _update_radiation_clouds(self):
        """更新辐射云"""
        for cloud in self.radiation_clouds[:]:
            cloud['x'] += cloud['vx']
            cloud['y'] += cloud['vy']
            cloud['alpha'] -= 0.5
            cloud['size'] += 0.3
            
            if cloud['alpha'] <= 0:
                self.radiation_clouds.remove(cloud)
                continue
            
            alpha = int(cloud['alpha'])
            if alpha > 0:
                pygame.draw.circle(self.image, (*self.theme["toxic"], alpha),
                                 (int(cloud['x']), int(cloud['y'])), int(cloud['size']))
    
    def _update_fallout(self):
        """更新落灰"""
        for f in self.fallout[:]:
            f['x'] += f['sway']
            f['y'] += f['vy']
            f['sway'] += random.uniform(-0.1, 0.1)
            f['sway'] = max(-1, min(1, f['sway']))
            
            if f['y'] > HEIGHT:
                self.fallout.remove(f)
                continue
            
            alpha = int(100 * (1 - self.frame / sum(self.phase_duration)))
            if alpha > 0:
                pygame.draw.circle(self.image, (*self.theme["smoke"], alpha),
                                 (int(f['x']), int(f['y'])), f['size'])
    
    def _deal_nuke_damage(self):
        """核弹伤害"""
        from sprites import FloatingText, Particle
        
        # 全屏清小怪
        for mob in list(mobs):
            # 根据距离计算伤害
            dist = math.sqrt((mob.rect.centerx - self.nuke_x)**2 + 
                           (mob.rect.centery - self.nuke_target_y)**2)
            
            # 中心区域直接秒杀
            if dist < 150:
                final_damage = 99999
            else:
                # 距离衰减
                dmg_mult = max(0.3, 1 - dist / WIDTH)
                final_damage = int(self.damage * 3 * dmg_mult)
            
            if hasattr(mob, 'take_damage'):
                mob.take_damage(final_damage)
            else:
                mob.hp -= final_damage
            
            FloatingText(mob.rect.centerx, mob.rect.top - 10,
                       f"☢{final_damage}", self.theme["toxic"])
            
            # 粒子
            for _ in range(3):
                Particle(mob.rect.center, self.theme["toxic"], mode='spark')


# ==================== C技能：盖亚之死 ====================
class DeathOfGaiaSkill(pygame.sprite.Sprite):
    """
    盖亚之死 - C技能
    15秒全屏debuff领域，敌人HP上限-50%，大幅减速
    增强版：荒芜裂地、毒雾翻涌、辐射符号阵、枯骨残骸、末日天空
    """
    
    def __init__(self, owner, damage, style="default"):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.style = style
        self.theme = get_theme(style)
        
        self.frame = 0
        self.duration = 900  # 15秒
        
        # 受影响的敌人记录
        self.affected_enemies = {}
        
        # 环境粒子 - 优化版（减少数量）
        self.particles = []
        for _ in range(30):  # 从80减少到30
            self.particles.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(0.5, 2),
                'size': random.randint(2, 6),
                'alpha': random.randint(50, 150),
                'type': random.choice(['dust', 'spore', 'ash'])
            })
        
        # 地面裂缝（优化）
        self.cracks = []
        for _ in range(6):  # 从12减少到6
            self.cracks.append({
                'x': random.randint(50, WIDTH - 50),
                'y': HEIGHT - random.randint(50, 150),
                'segments': self._generate_crack_path(),
                'glow': random.uniform(0.5, 1.0)
            })
        
        # 毒雾团（优化）
        self.fog_clouds = []
        for _ in range(6):  # 从15减少到6
            self.fog_clouds.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(HEIGHT // 2, HEIGHT),
                'size': random.randint(60, 120),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-0.3, 0.3),
                'alpha': random.randint(30, 60),
                'pulse_offset': random.uniform(0, math.pi * 2)
            })
        
        # 枯骨/残骸（优化）
        self.bones = []
        for _ in range(4):  # 从8减少到4
            self.bones.append({
                'x': random.randint(50, WIDTH - 50),
                'y': HEIGHT - random.randint(30, 80),
                'type': random.choice(['skull', 'ribcage', 'spine', 'hand']),
                'size': random.randint(15, 30),
                'rotation': random.uniform(0, math.pi),
                'emerge_progress': 0
            })
        
        # 辐射符号阵（优化）
        self.radiation_symbols = []
        symbol_count = 3  # 从5减少到3
        for i in range(symbol_count):
            angle = i * math.pi * 2 / symbol_count
            dist = min(WIDTH, HEIGHT) * 0.35
            self.radiation_symbols.append({
                'x': WIDTH // 2 + int(math.cos(angle) * dist),
                'y': HEIGHT // 2 + int(math.sin(angle) * dist),
                'size': 40,
                'rotation': angle,
                'pulse_offset': i * 0.5
            })
        
        # 地面毒池（优化）
        self.toxic_pools = []
        for _ in range(3):  # 从6减少到3
            self.toxic_pools.append({
                'x': random.randint(100, WIDTH - 100),
                'y': HEIGHT - random.randint(20, 60),
                'width': random.randint(80, 150),
                'height': random.randint(20, 40),
                'bubble_timer': 0
            })
        
        # 新增：天空效果
        self.sky_cracks = []
        for _ in range(5):
            self.sky_cracks.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT // 3),
                'length': random.randint(50, 150),
                'angle': random.uniform(-math.pi / 4, math.pi / 4),
                'branches': random.randint(2, 5)
            })
        
        # 新增：腐蚀波
        self.corruption_waves = []
        
        # 新增：漂浮文字
        self.floating_warnings = []
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _generate_crack_path(self):
        """生成裂缝路径"""
        segments = []
        current_x, current_y = 0, 0
        
        for _ in range(random.randint(5, 10)):
            dx = random.randint(-30, 30)
            dy = random.randint(10, 40)
            segments.append((current_x + dx, current_y + dy))
            current_x += dx
            current_y += dy
        
        return segments
    
    def update(self):
        self.frame += 1
        
        if self.frame > self.duration:
            self._restore_enemies()
            self.kill()
            return
        
        # 应用debuff
        self._apply_debuff()
        
        # 持续伤害
        if self.frame % 60 == 0:  # 每秒
            self._deal_dot()
        
        # 生成腐蚀波
        if self.frame % 120 == 0:
            self.corruption_waves.append({
                'radius': 0,
                'max_radius': max(WIDTH, HEIGHT),
                'alpha': 80
            })
        
        # 更新各种效果
        self._update_particles()
        self._update_fog_clouds()
        self._update_bones()
        self._update_corruption_waves()
        self._update_toxic_pools()
        
        self._render()
    
    def _update_particles(self):
        """更新粒子"""
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            
            # 不同类型粒子的行为
            if p['type'] == 'spore':
                p['vx'] += random.uniform(-0.1, 0.1)
                p['vy'] = math.sin(self.frame * 0.05 + p['x'] * 0.01) * 0.5
            elif p['type'] == 'ash':
                p['vy'] = 0.5 + math.sin(self.frame * 0.03 + p['x'] * 0.02) * 0.3
            
            # 边界处理
            if p['y'] > HEIGHT:
                p['y'] = 0
                p['x'] = random.randint(0, WIDTH)
            if p['x'] < 0:
                p['x'] = WIDTH
            elif p['x'] > WIDTH:
                p['x'] = 0
    
    def _update_fog_clouds(self):
        """更新毒雾团"""
        for fog in self.fog_clouds:
            fog['x'] += fog['vx']
            fog['y'] += fog['vy']
            
            # 边界反弹
            if fog['x'] < -fog['size'] or fog['x'] > WIDTH + fog['size']:
                fog['vx'] *= -1
            if fog['y'] < HEIGHT // 3 or fog['y'] > HEIGHT:
                fog['vy'] *= -1
    
    def _update_bones(self):
        """更新枯骨"""
        for bone in self.bones:
            # 缓慢从地面升起
            if bone['emerge_progress'] < 1:
                bone['emerge_progress'] = min(1, bone['emerge_progress'] + 0.01)
    
    def _update_corruption_waves(self):
        """更新腐蚀波"""
        for wave in self.corruption_waves[:]:
            wave['radius'] += 5
            wave['alpha'] = max(0, wave['alpha'] - 1)
            
            if wave['radius'] > wave['max_radius']:
                self.corruption_waves.remove(wave)
    
    def _update_toxic_pools(self):
        """更新毒池"""
        for pool in self.toxic_pools:
            pool['bubble_timer'] += 1
    
    def _apply_debuff(self):
        """应用debuff到所有敌人"""
        for mob in mobs:
            enemy_id = id(mob)
            
            if enemy_id not in self.affected_enemies:
                # 首次影响：记录原始数据并应用debuff
                original_max_hp = getattr(mob, 'max_hp', mob.hp)
                original_speed = getattr(mob, 'speed', 2)
                
                self.affected_enemies[enemy_id] = {
                    'mob': mob,
                    'original_max_hp': original_max_hp,
                    'original_speed': original_speed
                }
                
                # 应用debuff
                mob.max_hp = int(original_max_hp * 0.5)
                mob.hp = min(mob.hp, mob.max_hp)
                if hasattr(mob, 'speed'):
                    mob.speed = original_speed * 0.4
    
    def _restore_enemies(self):
        """恢复所有敌人的原始属性"""
        for enemy_id, data in self.affected_enemies.items():
            mob = data['mob']
            if mob.alive():
                mob.max_hp = data['original_max_hp']
                if hasattr(mob, 'speed'):
                    mob.speed = data['original_speed']
    
    def _deal_dot(self):
        """造成持续伤害"""
        from sprites import FloatingText
        
        dot_damage = int(self.damage * 0.2)
        
        for mob in mobs:
            if hasattr(mob, 'take_damage'):
                mob.take_damage(dot_damage)
            else:
                mob.hp -= dot_damage
            
            FloatingText(mob.rect.centerx + random.randint(-15, 15),
                       mob.rect.top - 5,
                       f"☠{dot_damage}", self.theme["toxic"])
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        
        # 计算淡入淡出
        if self.frame < 90:
            fade = self.frame / 90
        elif self.frame > self.duration - 90:
            fade = (self.duration - self.frame) / 90
        else:
            fade = 1
        
        # ====== 1. 末日天空效果 ======
        # 天空渐变 - 从正常到死亡绿/红
        sky_layers = 5
        for i in range(sky_layers):
            layer_height = HEIGHT // (sky_layers + 2)
            layer_y = i * layer_height
            
            # 颜色从顶部的深色到底部的浅色
            r = int(30 + i * 10 + 20 * math.sin(self.frame * 0.02))
            g = int(50 + i * 15 + 30 * math.sin(self.frame * 0.02 + 1))
            b = int(20 + i * 5)
            a = int(40 * fade * (1 - i * 0.15))
            
            if a > 0:
                pygame.draw.rect(self.image, (r, g, b, a),
                               (0, layer_y, WIDTH, layer_height + 1))
        
        # 天空裂痕
        for crack in self.sky_cracks:
            crack_alpha = int(60 * fade * (0.5 + 0.5 * math.sin(self.frame * 0.05 + crack['x'] * 0.01)))
            if crack_alpha > 0:
                # 主裂缝
                end_x = crack['x'] + int(math.cos(crack['angle']) * crack['length'])
                end_y = crack['y'] + int(math.sin(crack['angle']) * crack['length'])
                pygame.draw.line(self.image, (*self.theme["toxic"], crack_alpha),
                               (crack['x'], crack['y']), (end_x, end_y), 2)
                # 裂缝发光
                pygame.draw.line(self.image, (255, 255, 200, crack_alpha // 2),
                               (crack['x'], crack['y']), (end_x, end_y), 1)
                
                # 分支
                for b in range(crack['branches']):
                    branch_start_t = random.uniform(0.3, 0.8)
                    branch_x = crack['x'] + int((end_x - crack['x']) * branch_start_t)
                    branch_y = crack['y'] + int((end_y - crack['y']) * branch_start_t)
                    branch_angle = crack['angle'] + random.uniform(-0.5, 0.5)
                    branch_len = crack['length'] * 0.4
                    branch_end_x = branch_x + int(math.cos(branch_angle) * branch_len)
                    branch_end_y = branch_y + int(math.sin(branch_angle) * branch_len)
                    pygame.draw.line(self.image, (*self.theme["toxic"], crack_alpha // 2),
                                   (branch_x, branch_y), (branch_end_x, branch_end_y), 1)
        
        # ====== 2. 废土网格线 ======
        grid_alpha = int(25 * fade)
        grid_spacing = 40
        grid_offset = (self.frame * 0.5) % grid_spacing
        
        # 透视网格效果
        for i, x in enumerate(range(-int(grid_offset), WIDTH + grid_spacing, grid_spacing)):
            wave = math.sin(self.frame * 0.03 + i * 0.2) * 3
            pygame.draw.line(self.image, (*self.theme["smoke"], grid_alpha),
                           (x + wave, 0), (x - wave, HEIGHT), 1)
        
        for i, y in enumerate(range(-int(grid_offset), HEIGHT + grid_spacing, grid_spacing)):
            wave = math.sin(self.frame * 0.03 + i * 0.2) * 3
            # 透视效果 - 底部线条更密
            actual_y = int(y + (HEIGHT - y) * 0.1 * math.sin(self.frame * 0.02))
            pygame.draw.line(self.image, (*self.theme["smoke"], grid_alpha),
                           (0, actual_y + wave), (WIDTH, actual_y - wave), 1)
        
        # ====== 3. 地面裂缝 ======
        for crack in self.cracks:
            crack_alpha = int(80 * fade * crack['glow'])
            glow_pulse = 0.7 + 0.3 * math.sin(self.frame * 0.1 + crack['x'] * 0.01)
            
            # 绘制裂缝路径
            prev_x, prev_y = crack['x'], crack['y']
            for seg_x, seg_y in crack['segments']:
                curr_x = crack['x'] + seg_x
                curr_y = crack['y'] + seg_y
                
                # 裂缝阴影
                pygame.draw.line(self.image, (20, 15, 10, crack_alpha),
                               (prev_x + 2, prev_y + 2), (curr_x + 2, curr_y + 2), 4)
                # 裂缝主体
                pygame.draw.line(self.image, (40, 30, 20, crack_alpha),
                               (prev_x, prev_y), (curr_x, curr_y), 3)
                # 裂缝发光边缘
                pygame.draw.line(self.image, (*self.theme["toxic"], int(crack_alpha * glow_pulse * 0.6)),
                               (prev_x, prev_y), (curr_x, curr_y), 1)
                
                prev_x, prev_y = curr_x, curr_y
        
        # ====== 4. 毒池 ======
        for pool in self.toxic_pools:
            pool_alpha = int(60 * fade)
            
            # 毒池底色
            pygame.draw.ellipse(self.image, (*self.theme["toxic"], pool_alpha),
                              (pool['x'] - pool['width']//2, pool['y'] - pool['height']//2,
                               pool['width'], pool['height']))
            
            # 毒池高光
            highlight_w = pool['width'] * 0.6
            highlight_h = pool['height'] * 0.4
            pygame.draw.ellipse(self.image, (*self.theme["glow"], pool_alpha // 2),
                              (pool['x'] - highlight_w//2, pool['y'] - highlight_h//2 - 5,
                               highlight_w, highlight_h))
            
            # 气泡效果
            bubble_count = 3
            for i in range(bubble_count):
                bubble_phase = (pool['bubble_timer'] * 0.1 + i * 2) % 10
                if bubble_phase < 5:
                    bx = pool['x'] + random.randint(-pool['width']//3, pool['width']//3)
                    by = pool['y'] - int(bubble_phase * 3)
                    br = int(3 + 2 * (1 - bubble_phase / 5))
                    pygame.draw.circle(self.image, (*self.theme["toxic"], int(pool_alpha * (1 - bubble_phase / 5))),
                                     (bx, by), br)
        
        # ====== 5. 毒雾团（优化版）======
        for fog in self.fog_clouds:
            pulse = 0.8 + 0.2 * math.sin(self.frame * 0.05 + fog['pulse_offset'])
            fog_alpha = int(fog['alpha'] * fade * pulse)
            fog_size = int(fog['size'] * pulse)
            
            if fog_alpha > 0 and fog_size > 0:
                # 单层渲染（优化性能）
                pygame.draw.circle(self.image, (*self.theme["toxic"], fog_alpha),
                                 (int(fog['x']), int(fog['y'])), fog_size)
        
        # ====== 6. 粒子 ======
        for p in self.particles:
            alpha = int(p['alpha'] * fade)
            if alpha > 0:
                if p['type'] == 'dust':
                    pygame.draw.circle(self.image, (*self.theme["smoke"], alpha),
                                     (int(p['x']), int(p['y'])), p['size'])
                elif p['type'] == 'spore':
                    pygame.draw.circle(self.image, (*self.theme["toxic"], alpha),
                                     (int(p['x']), int(p['y'])), p['size'])
                    # 孢子发光
                    pygame.draw.circle(self.image, (*self.theme["glow"], alpha // 2),
                                     (int(p['x']), int(p['y'])), p['size'] + 1)
                elif p['type'] == 'ash':
                    # 灰烬 - 不规则形状
                    pygame.draw.polygon(self.image, (80, 70, 60, alpha), [
                        (int(p['x']), int(p['y']) - p['size']),
                        (int(p['x']) + p['size'], int(p['y'])),
                        (int(p['x']), int(p['y']) + p['size'] // 2),
                        (int(p['x']) - p['size'], int(p['y']))
                    ])
        
        # ====== 7. 辐射符号阵（优化版）======
        for sym in self.radiation_symbols:
            pulse = 0.5 + 0.5 * math.sin(self.frame * 0.08 + sym['pulse_offset'])
            sym_alpha = int(50 * fade * pulse)
            sym_rotation = sym['rotation'] + self.frame * 0.02
            
            if sym_alpha > 0:
                sx, sy = sym['x'], sym['y']
                size = sym['size']
                
                # 外圈
                pygame.draw.circle(self.image, (*self.theme["toxic"], sym_alpha),
                                 (sx, sy), size, 3)
                
                # 内圈
                pygame.draw.circle(self.image, (*self.theme["toxic"], sym_alpha),
                                 (sx, sy), size // 2, 2)
                
                # 中心点
                pygame.draw.circle(self.image, (*self.theme["toxic"], int(sym_alpha * 1.5)),
                                 (sx, sy), 5)
                
                # 简化三叶草 - 只画3个圆代表叶片
                for i in range(3):
                    angle = sym_rotation + i * 2 * math.pi / 3
                    px = sx + int(math.cos(angle) * (size - 10))
                    py = sy + int(math.sin(angle) * (size - 10))
                    pygame.draw.circle(self.image, (*self.theme["toxic"], sym_alpha),
                                     (px, py), 8)
        
        # ====== 8. 枯骨残骸 ======
        for bone in self.bones:
            if bone['emerge_progress'] > 0:
                bone_alpha = int(80 * fade * bone['emerge_progress'])
                bx, by = bone['x'], bone['y']
                size = bone['size']
                
                # 根据emerge_progress调整y位置（从地下升起）
                emerge_offset = int((1 - bone['emerge_progress']) * 30)
                by += emerge_offset
                
                if bone['type'] == 'skull':
                    # 骷髅头
                    pygame.draw.ellipse(self.image, (200, 190, 170, bone_alpha),
                                      (bx - size, by - size, size * 2, int(size * 1.5)))
                    # 眼眶
                    eye_size = size // 4
                    pygame.draw.ellipse(self.image, (30, 20, 20, bone_alpha),
                                      (bx - size // 2, by - size // 3, eye_size, eye_size))
                    pygame.draw.ellipse(self.image, (30, 20, 20, bone_alpha),
                                      (bx + size // 4, by - size // 3, eye_size, eye_size))
                    # 眼眶发光
                    pygame.draw.ellipse(self.image, (*self.theme["toxic"], bone_alpha // 2),
                                      (bx - size // 2 + 1, by - size // 3 + 1, eye_size - 2, eye_size - 2))
                    pygame.draw.ellipse(self.image, (*self.theme["toxic"], bone_alpha // 2),
                                      (bx + size // 4 + 1, by - size // 3 + 1, eye_size - 2, eye_size - 2))
                    # 鼻孔
                    pygame.draw.polygon(self.image, (30, 20, 20, bone_alpha), [
                        (bx, by + size // 6),
                        (bx - size // 6, by + size // 3),
                        (bx + size // 6, by + size // 3)
                    ])
                    # 牙齿
                    for i in range(5):
                        tx = bx - size // 2 + i * size // 4
                        pygame.draw.rect(self.image, (200, 190, 170, bone_alpha),
                                       (tx, by + size // 2, size // 6, size // 4))
                
                elif bone['type'] == 'ribcage':
                    # 肋骨
                    for i in range(5):
                        rib_y = by + i * (size // 5)
                        curve = math.sin(i * 0.5) * 10
                        pygame.draw.arc(self.image, (200, 190, 170, bone_alpha),
                                       (bx - size + curve, rib_y, size * 2, size // 3),
                                       0, math.pi, 2)
                
                elif bone['type'] == 'spine':
                    # 脊椎
                    for i in range(6):
                        vert_y = by + i * (size // 4)
                        vert_size = size // 3
                        pygame.draw.circle(self.image, (200, 190, 170, bone_alpha),
                                         (bx, vert_y), vert_size)
                        # 横突
                        pygame.draw.line(self.image, (200, 190, 170, bone_alpha),
                                       (bx - vert_size * 2, vert_y),
                                       (bx + vert_size * 2, vert_y), 2)
                
                elif bone['type'] == 'hand':
                    # 手骨
                    palm_size = size // 2
                    pygame.draw.circle(self.image, (200, 190, 170, bone_alpha),
                                     (bx, by), palm_size)
                    # 手指
                    for i in range(5):
                        finger_angle = -math.pi / 2 + (i - 2) * 0.3 + bone['rotation']
                        finger_len = size * (0.8 if i == 0 or i == 4 else 1.0)
                        fx = bx + int(math.cos(finger_angle) * finger_len)
                        fy = by + int(math.sin(finger_angle) * finger_len)
                        pygame.draw.line(self.image, (200, 190, 170, bone_alpha),
                                       (bx, by), (fx, fy), 3)
                        # 指节
                        for j in range(2):
                            jx = bx + int(math.cos(finger_angle) * finger_len * (0.4 + j * 0.3))
                            jy = by + int(math.sin(finger_angle) * finger_len * (0.4 + j * 0.3))
                            pygame.draw.circle(self.image, (180, 170, 150, bone_alpha),
                                             (jx, jy), 2)
        
        # ====== 9. 腐蚀波 ======
        for wave in self.corruption_waves:
            if wave['alpha'] > 0:
                pygame.draw.circle(self.image, (*self.theme["toxic"], int(wave['alpha'] * fade)),
                                 (WIDTH // 2, HEIGHT // 2), int(wave['radius']), 3)
                # 内环
                inner_r = int(wave['radius'] * 0.9)
                if inner_r > 0:
                    pygame.draw.circle(self.image, (*self.theme["glow"], int(wave['alpha'] * fade * 0.5)),
                                     (WIDTH // 2, HEIGHT // 2), inner_r, 1)
        
        # ====== 10. 边缘辐射效果（优化版 - 减少绘制次数）======
        vignette_alpha = int(50 * fade)
        if vignette_alpha > 0:
            # 只绘制几层而不是120层
            for i in range(0, 80, 20):  # 只绘制4层
                alpha = int(vignette_alpha * (1 - i / 80))
                if alpha > 0:
                    # 使用更宽的矩形而不是单像素
                    pygame.draw.rect(self.image, (*self.theme["toxic"], alpha),
                                   (i, i, 20, HEIGHT - i * 2))  # 左
                    pygame.draw.rect(self.image, (*self.theme["toxic"], alpha),
                                   (WIDTH - i - 20, i, 20, HEIGHT - i * 2))  # 右
                    pygame.draw.rect(self.image, (*self.theme["toxic"], alpha),
                                   (i, i, WIDTH - i * 2, 20))  # 上
                    pygame.draw.rect(self.image, (*self.theme["toxic"], alpha),
                                   (i, HEIGHT - i - 20, WIDTH - i * 2, 20))  # 下
        
        # ====== 11. 中心大型辐射符号水印（优化版）======
        t = self.frame * 0.02
        center_pulse = 0.5 + 0.5 * math.sin(t)
        center_alpha = int(25 * fade * center_pulse)
        center_size = 150
        
        if center_alpha > 0:
            cx, cy = WIDTH // 2, HEIGHT // 2
            
            # 外圈
            pygame.draw.circle(self.image, (*self.theme["toxic"], center_alpha),
                             (cx, cy), center_size, 4)
            
            # 内圈
            pygame.draw.circle(self.image, (*self.theme["toxic"], center_alpha),
                             (cx, cy), center_size // 2, 2)
            
            # 中心
            pygame.draw.circle(self.image, (*self.theme["toxic"], int(center_alpha * 1.5)),
                             (cx, cy), 20)
            
            # 简化的三叶草 - 只绘制3个扇形
            for i in range(3):
                angle = t + i * 2 * math.pi / 3
                # 扇形端点
                px = cx + int(math.cos(angle) * (center_size - 10))
                py = cy + int(math.sin(angle) * (center_size - 10))
                pygame.draw.circle(self.image, (*self.theme["toxic"], center_alpha),
                                 (px, py), 15)
        
        # ====== 12. 动态警告文字效果（用图形模拟）======
        warning_y = 50 + int(10 * math.sin(self.frame * 0.1))
        warning_alpha = int(60 * fade * (0.5 + 0.5 * math.sin(self.frame * 0.15)))
        
        if warning_alpha > 0:
            # 警告条背景
            pygame.draw.rect(self.image, (0, 0, 0, warning_alpha),
                           (WIDTH // 2 - 120, warning_y - 5, 240, 30))
            pygame.draw.rect(self.image, (*self.theme["toxic"], warning_alpha),
                           (WIDTH // 2 - 120, warning_y - 5, 240, 30), 2)
            
            # 危险三角形符号
            tri_size = 15
            for i in range(3):
                tx = WIDTH // 2 - 80 + i * 80
                pygame.draw.polygon(self.image, (*self.theme["toxic"], warning_alpha), [
                    (tx, warning_y),
                    (tx - tri_size, warning_y + tri_size * 1.5),
                    (tx + tri_size, warning_y + tri_size * 1.5)
                ], 2)
                pygame.draw.line(self.image, (*self.theme["toxic"], warning_alpha),
                               (tx, warning_y + 5), (tx, warning_y + tri_size), 2)
                pygame.draw.circle(self.image, (*self.theme["toxic"], warning_alpha),
                                 (tx, warning_y + tri_size + 3), 2)


# ==================== 瘟疫尘埃（被动） ====================
class PlagueDust(pygame.sprite.Sprite):
    """
    瘟疫尘埃 - 被动：飞行路径残留
    接触的敌人感染瘟疫状态
    """
    
    def __init__(self, x, y, owner=None, style="default"):
        super().__init__()
        self.owner = owner
        self.style = style
        self.theme = get_theme(style)
        
        self.x = x
        self.y = y
        self.frame = 0
        self.duration = 60  # 1秒
        
        self.size = 30
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        
        if self.frame > self.duration:
            self.kill()
            return
        
        # 感染接触的敌人
        for mob in mobs:
            if self.rect.colliderect(mob.rect):
                if not hasattr(mob, 'plague_stacks'):
                    mob.plague_stacks = 0
                if mob.plague_stacks < 5:
                    mob.plague_stacks += 1
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        
        fade = 1 - (self.frame / self.duration)
        alpha = int(80 * fade)
        size = int(self.size // 2 * (0.5 + 0.5 * fade))
        
        if size > 0 and alpha > 0:
            pygame.draw.circle(self.image, (*self.theme["toxic"], alpha), (cx, cy), size)
            pygame.draw.circle(self.image, (*self.theme["smoke"], alpha // 2), (cx, cy), size - 3)


# ==================== 工厂函数 ====================
def create_plague_missile(x, y, damage, angle=-90, owner=None, style="default"):
    """创建瘟疫导弹"""
    return PlagueMissileBullet(x, y, damage, angle, owner, style)


def create_plague_drone(x, y, damage, owner=None, style="default"):
    """创建瘟疫无人机"""
    return PlagueDrone(x, y, damage, owner, style)


def create_carpet_bombing(owner, damage, style="default"):
    """创建饱和轰炸"""
    return CarpetBombingSkill(owner, damage, style)


def create_plague_nuke(owner, damage, style="default"):
    """创建瘟疫核弹"""
    return PlagueNukeSkill(owner, damage, style)


def create_death_of_gaia(owner, damage, style="default"):
    """创建盖亚之死"""
    return DeathOfGaiaSkill(owner, damage, style)


def create_plague_dust(x, y, owner=None, style="default"):
    """创建瘟疫尘埃"""
    return PlagueDust(x, y, owner, style)


# ==================== 子弹预览渲染器 ====================
def render_goliath_bullet_preview(surface, effects, color, center_x, center_y, size, x, y, plane_id=None):
    """渲染歌莉娅子弹预览"""
    goliath_effects = [
        "plague_missile", "plague_smoke",
        "nuclear_glow", "radiation_pulse",
        "desert_dust", "sand_trail",
        "arctic_frost", "ice_mist",
        "necrosis_drip", "decay_aura",
        "pandemic_virus", "infection_spread",
        "spore_cloud", "fungal_burst",
        "chemical_leak", "acid_bubble",
        "oil_flame", "smoke_trail",
        "hive_swarm", "honey_drip",
        "xeno_acid", "alien_glow",
        "blood_splatter", "crimson_mist",
    ]
    
    has_goliath_effect = any(effect in effects for effect in goliath_effects)
    is_goliath_plane = (plane_id == "goliath")
    
    if not has_goliath_effect and not is_goliath_plane:
        return False
    
    t = pygame.time.get_ticks() / 1000.0
    bullet_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    cx, cy = size, size
    pulse = abs(math.sin(t * 3)) * 0.2 + 0.9
    
    # 默认：瘟疫导弹
    toxic = (57, 255, 20)
    armor = (85, 107, 47)
    
    # 导弹形状
    missile_len = int(size // 2 * pulse)
    missile_w = int(size // 4)
    
    # 弹体
    pygame.draw.ellipse(bullet_surf, armor,
                       (cx - missile_w//2, cy - missile_len, missile_w, missile_len * 2))
    
    # 弹头
    pygame.draw.circle(bullet_surf, toxic, (cx, cy - missile_len), missile_w // 2)
    
    # 尾焰
    flame_len = int(missile_len * 0.6 * (1 + 0.3 * math.sin(t * 8)))
    pygame.draw.polygon(bullet_surf, toxic, [
        (cx - missile_w//3, cy + missile_len),
        (cx + missile_w//3, cy + missile_len),
        (cx, cy + missile_len + flame_len)
    ])
    
    # 烟雾
    for i in range(3):
        smoke_y = cy + missile_len + flame_len + i * 5
        smoke_alpha = 150 - i * 40
        smoke_size = int((missile_w // 2 + i * 2) * (1 + 0.2 * math.sin(t * 4 + i)))
        pygame.draw.circle(bullet_surf, (50, 60, 40, smoke_alpha),
                         (cx + int(3 * math.sin(t * 3 + i)), smoke_y), smoke_size)
    
    surface.blit(bullet_surf, (x - size, y - size))
    return True
