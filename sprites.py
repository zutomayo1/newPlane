import pygame
import math
import random
from config import *
from utils import sound_mgr, draw_text, get_plane_surf, get_boss_surf, draw_cyber_rect, log_error, procedural_interceptor_surface, procedural_juggernaut_surface, procedural_swarmer_surface
from systems import arsenal_save_data, create_weapon, WeaponSystem

# ==============================================================================
#   特效与辅助实体
# ==============================================================================
class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, color, mode="spark"):
        super().__init__()
        all_sprites.add(self)
        self.mode = mode
        self.color = color
        # allow optional parameters for size/speed/life
        self.life = random.randint(20, 40)
        self.size = 4
        self.vx = 0
        self.vy = 0
        self.owner = None
        # parse mode string if custom
        self.params = {}
        if mode == "shockwave":
            self.image = pygame.Surface((2, 2), pygame.SRCALPHA)
            self.radius = 10
            self.pos = pos
            self.rect = self.image.get_rect(center=pos)
        elif mode == "lightning":
            self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            self.rect = self.image.get_rect()
            self.points = pos
        elif mode == 'bloom':
            # large soft glow
            self.size = 70
            self.life = self.life * 2
            self.image = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (*self.color, 50), (self.size, self.size), self.size)
            self.rect = self.image.get_rect(center=pos)
            self.mode = 'bloom'
        elif mode == 'pulse':
            self.size = 30
            self.life = 30
            self.radius = 5
            self.pos = pos
            self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
            self.rect = self.image.get_rect(center=pos)
            self.mode = 'pulse'
        elif mode == 'star':
            self.size = random.randint(2, 6)
            self.life = random.randint(10, 30)
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            self.image.fill(color)
            self.rect = self.image.get_rect(center=pos)
            angle = random.uniform(0, 6.28)
            speed = random.uniform(0.5, 2.5)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.mode = 'star'
        else:
            size = random.randint(3, 6)
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            self.image.fill(color)
            self.rect = self.image.get_rect(center=pos)
            angle = random.uniform(0, 6.28)
            speed = random.uniform(2, 6)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
            
        if self.mode == "shockwave":
            self.radius += 3
            width = int((self.life / 40) * 5)
            # 由于Pygame绘图是在screen上，这里粒子是Sprite，需要特殊处理
            # 简化：通过不断变大的圆形Surface模拟
            dim = int(self.radius * 2)
            self.image = pygame.Surface((dim, dim), pygame.SRCALPHA)
            if width > 0:
                pygame.draw.circle(self.image, self.color, (dim//2, dim//2), int(self.radius), width)
            self.rect = self.image.get_rect(center=self.pos)
            
        elif self.mode == "lightning":
            self.image.fill((0,0,0,0))
            if len(self.points) >= 2:
                # 闪烁效果
                if self.life % 2 == 0:
                    pygame.draw.lines(self.image, self.color, False, self.points, 2)
        elif self.mode == 'bloom':
            # slowly fade the bloom by reducing alpha
            cur = int(50 * (self.life / (40 * 2)))
            self.image.fill((0, 0, 0, 0))
            pygame.draw.circle(self.image, (*self.color, max(0, cur)), (self.size, self.size), self.size)
            self.rect = self.image.get_rect(center=self.pos if hasattr(self, 'pos') else self.rect.center)
        elif self.mode == 'pulse':
            self.radius += 2
            width = int((self.life / 30) * 4)
            dim = int(self.radius * 2)
            self.image = pygame.Surface((dim, dim), pygame.SRCALPHA)
            if width > 0: pygame.draw.circle(self.image, self.color, (dim//2, dim//2), int(self.radius), width)
            self.rect = self.image.get_rect(center=self.pos)
        elif self.mode == 'star':
            self.rect.x += self.vx
            self.rect.y += self.vy
            self.image.set_alpha(int(self.life/40 * 255))
        else:
            self.rect.x += self.vx
            self.rect.y += self.vy
            self.image.set_alpha(int(self.life/40 * 255))

class FloatingText(pygame.sprite.Sprite):
    def __init__(self, x, y, text, color):
        super().__init__()
        all_sprites.add(self)
        # 避免循环引用 utils.get_font，这里直接使用pygame.font
        font = pygame.font.SysFont(["microsoftyahei", "simhei", "arial"], 24, bold=True)
        self.image = font.render(str(text), True, color)
        # 描边
        outline = font.render(str(text), True, BLACK)
        s = pygame.Surface((self.image.get_width()+2, self.image.get_height()+2), pygame.SRCALPHA)
        s.blit(outline, (2,2))
        s.blit(self.image, (0,0))
        self.image = s
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_y = -3
        self.life = 40

    def update(self):
        self.rect.y += self.vel_y
        self.life -= 1
        if self.life <= 0: self.kill()

class DamageNumber(pygame.sprite.Sprite):
    def __init__(self, x, y, amount, is_crit=False):
        super().__init__()
        all_sprites.add(self)
        size = 24 if is_crit else 16
        color = (255, 100, 0) if is_crit else WHITE
        font = pygame.font.SysFont(["arial"], size, bold=is_crit)
        self.image = font.render(str(int(amount)), True, color)
        outline = font.render(str(int(amount)), True, BLACK)
        s = pygame.Surface((self.image.get_width()+2, self.image.get_height()+2), pygame.SRCALPHA)
        s.blit(outline, (2,2))
        s.blit(self.image, (0,0))
        self.image = s
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = random.uniform(-1, 1)
        self.vy = -3
        self.life = 30

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.vy += 0.1
        self.life -= 1
        if self.life <= 0: self.kill()
        if self.life < 10: self.image.set_alpha(int(self.life / 10 * 255))

# ==============================================================================
#   经验球类
# ==============================================================================
class ExperienceOrb(pygame.sprite.Sprite):
    """掉落的经验球，玩家碰触后获得经验"""
    def __init__(self, x, y, amount=5):
        super().__init__()
        all_sprites.add(self)
        self.amount = amount
        self.life = 600  # 存在时间 10 秒
        self.birth_time = pygame.time.get_ticks()
        self.pickup_range = 150  # 吸取范围
        
        # 根据经验量决定大小和颜色
        if amount >= 10:
            self.size = 8
            self.color = YELLOW  # 精英敌人掉落 (255, 255, 0)
            self.glow_color = (255, 200, 0)  # 外圈光晕颜色
        else:
            self.size = 6
            self.color = LIME    # 普通敌人掉落 (0, 255, 0)
            self.glow_color = (100, 255, 0)  # 外圈光晕颜色
        
        # 掉落位置
        self.x = float(x)
        self.y = float(y)
        
        # 掉落速度
        self.vy = 0.0  # 垂直速度
        self.gravity = 0.15  # 重力加速度
        self.max_fall_speed = 3.0  # 最大下落速度
        
        # 吸取动画状态
        self.being_absorbed = False  # 是否正在被吸取
        self.absorption_frames = 0  # 吸取动画帧数
        self.target_x = 0
        self.target_y = 0
        
        # 创建棱形纹理
        self.image = pygame.Surface((self.size*3, self.size*3), pygame.SRCALPHA)
        self.draw_diamond()
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        
    def draw_diamond(self):
        """绘制经验球 - 复杂多色设计"""
        self.image.fill((0, 0, 0, 0))
        center = self.size * 1.5
        
        if self.amount >= 10:  # 精英掉落（黄色）
            # 外层：黄色八边形框架
            oct_size = self.size
            oct_points = []
            for i in range(8):
                angle = i * 45
                rad = math.radians(angle)
                x = center + oct_size * math.cos(rad)
                y = center + oct_size * math.sin(rad)
                oct_points.append((x, y))
            pygame.draw.polygon(self.image, (255, 255, 0), oct_points)
            pygame.draw.polygon(self.image, (255, 200, 0), oct_points, 2)
            
            # 中层：内菱形（橙色）
            diamond_inner = [
                (center, center - self.size * 0.6),
                (center + self.size * 0.6, center),
                (center, center + self.size * 0.6),
                (center - self.size * 0.6, center)
            ]
            pygame.draw.polygon(self.image, (255, 150, 0), diamond_inner)
            pygame.draw.polygon(self.image, (255, 100, 0), diamond_inner, 1)
            
            # 内层：中心星形（亮黄）
            star_points = []
            for i in range(5):
                angle = i * 72
                if i % 2 == 0:
                    r = self.size * 0.3
                else:
                    r = self.size * 0.15
                rad = math.radians(angle)
                x = center + r * math.cos(rad)
                y = center + r * math.sin(rad)
                star_points.append((x, y))
            pygame.draw.polygon(self.image, (255, 255, 100), star_points)
            
            # 中心核心（金色发光）
            pygame.draw.circle(self.image, (255, 255, 150), (int(center), int(center)), int(self.size * 0.2))
            
            # 背景光晕
            for i in range(3, 0, -1):
                pygame.draw.circle(self.image, (255, 200, 0), (int(center), int(center)), int(self.size * 1.3 + i), 1)
        
        else:  # 普通掉落（绿色）
            # 外层：绿色六边形框架
            hex_size = self.size
            hex_points = []
            for i in range(6):
                angle = i * 60
                rad = math.radians(angle)
                x = center + hex_size * math.cos(rad)
                y = center + hex_size * math.sin(rad)
                hex_points.append((x, y))
            pygame.draw.polygon(self.image, (0, 255, 100), hex_points)
            pygame.draw.polygon(self.image, (100, 255, 150), hex_points, 2)
            
            # 中层：内菱形（青绿）
            diamond_inner = [
                (center, center - self.size * 0.6),
                (center + self.size * 0.6, center),
                (center, center + self.size * 0.6),
                (center - self.size * 0.6, center)
            ]
            pygame.draw.polygon(self.image, (100, 200, 150), diamond_inner)
            pygame.draw.polygon(self.image, (0, 255, 100), diamond_inner, 1)
            
            # 内层：4个角的小点（彩虹色）
            corner_colors = [(100, 255, 200), (255, 100, 200), (100, 200, 255), (200, 100, 255)]
            corner_angles = [45, 135, 225, 315]
            for angle, col in zip(corner_angles, corner_colors):
                rad = math.radians(angle)
                x = center + self.size * 0.5 * math.cos(rad)
                y = center + self.size * 0.5 * math.sin(rad)
                pygame.draw.circle(self.image, col, (int(x), int(y)), 2)
            
            # 中心圆（亮绿色）
            pygame.draw.circle(self.image, (150, 255, 200), (int(center), int(center)), int(self.size * 0.25))
            
            # 背景光晕
            for i in range(3, 0, -1):
                pygame.draw.circle(self.image, (100, 255, 150), (int(center), int(center)), int(self.size * 1.3 + i), 1)
        
    def update(self):
        # 如果正在被吸取，向玩家移动
        if self.being_absorbed:
            self.absorption_frames += 1
            # 加速朝向玩家移动
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = math.hypot(dx, dy)
            
            if dist < 5:  # 到达玩家
                self.kill()
                return
            
            # 加速移动（抛物线加速）
            speed = 8 + self.absorption_frames * 0.3
            if dist > 0:
                self.x += (dx / dist) * speed
                self.y += (dy / dist) * speed
            
            # 缩小和淡出
            fade_ratio = 1.0 - (self.absorption_frames / 20.0)
            if fade_ratio <= 0:
                self.kill()
                return
            
            # 重新绘制缩小的经验球
            old_size = self.size
            self.size = int(old_size * fade_ratio)
            self.draw_diamond()
            self.size = old_size
            
            self.rect.center = (int(self.x), int(self.y))
            return
        
        # 正常状态：重力下落
        self.vy += self.gravity
        if self.vy > self.max_fall_speed:
            self.vy = self.max_fall_speed
        
        self.y += self.vy
        
        # 更新矩形位置
        self.rect.center = (int(self.x), int(self.y))
        
        # 碰到边界就消失
        if (self.x < 0 or self.x > WIDTH or 
            self.y < 0 or self.y > HEIGHT):
            self.kill()
            return
        
        self.life -= 1
        
        # 闪烁效果
        elapsed = (pygame.time.get_ticks() - self.birth_time) / 1000.0
        alpha = 220 + int(35 * math.sin(elapsed * 4))
        alpha = max(150, min(255, alpha))
        self.image.set_alpha(alpha)
        
        # 生命期满消失（最后100帧淡出）
        if self.life <= 0:
            self.kill()
        elif self.life < 100:
            fade_alpha = int(alpha * (self.life / 100))
            self.image.set_alpha(fade_alpha)

class LightningBolt(pygame.sprite.Sprite):
    def __init__(self, start_pos, end_pos):
        super().__init__()
        all_sprites.add(self)
        self.life = 10
        self.start = start_pos
        self.end = end_pos
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.draw_bolt()
        
    def draw_bolt(self):
        self.image.fill((0,0,0,0))
        self._recursive_draw(self.start, self.end, 2)
        
    def _recursive_draw(self, p1, p2, thickness):
        dist = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
        if dist < 15:
            pygame.draw.line(self.image, CYAN, p1, p2, thickness)
            return
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        offset = random.randint(-15, 15)
        mid = (mid_x + offset, mid_y + offset)
        self._recursive_draw(p1, mid, thickness)
        self._recursive_draw(mid, p2, thickness)
        
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill()
        elif self.life % 3 == 0: self.draw_bolt()

# ==============================================================================
#   大招特效类
# ==============================================================================
class FinalBeam(pygame.sprite.Sprite):
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 120
        self.width = 20
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.hit_enemies = set()  # 追踪已击中的敌人
        sound_mgr.play("laser")

    def update(self):
        self.life -= 1
        self.image.fill((0,0,0,0))
        if self.life <= 0: self.kill(); return
        
        # 脉冲宽度效果
        pulse = math.sin(self.life / 120 * math.pi)
        w = 150 * pulse
        center_x = self.owner.rect.centerx
        
        # 主光束 - 白色核心
        pygame.draw.rect(self.image, WHITE, (center_x - w/4, 0, w/2, HEIGHT), 0)
        
        # 外层青色光晕
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 255, 255, 100), (center_x - w/2, 0, w, HEIGHT))
        self.image.blit(s, (0,0))
        
        # 边缘极光效果
        glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(5):
            pygame.draw.rect(glow_surf, (0, 255, 255, 30), 
                           (center_x - w/2 - i*2, 0, w + i*4, HEIGHT))
        self.image.blit(glow_surf, (0,0))
        
        # 伤害和粒子效果
        if self.life % 3 == 0:
            for m in mobs:
                if abs(m.rect.centerx - center_x) < w/2 + m.radius:
                    if m not in self.hit_enemies:
                        m.hp -= 250
                        self.hit_enemies.add(m)
                        # 多个粒子
                        for _ in range(3):
                            Particle(m.rect.center, CYBER_CYAN_BRIGHT)
                        FloatingText(m.rect.centerx, m.rect.top - 30, "BEAM!", CYAN)
                    else:
                        # 继续伤害，但降低
                        m.hp -= 50
                        Particle(m.rect.center, CYAN)

class TimeSlash(pygame.sprite.Sprite):
    def __init__(self, target_pos):
        super().__init__()
        all_sprites.add(self)
        self.pos = target_pos
        self.life = 30
        self.image = pygame.Surface((120, 120), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=target_pos)
        self.angle = random.randint(0, 360)
        sound_mgr.play("hit")

    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        self.image.fill((0,0,0,0))
        
        # 扩展斜线范围
        progress = 1 - self.life / 30
        l = 80 * progress
        rad = math.radians(self.angle)
        
        # 中心点
        cx, cy = 60, 60
        start = (cx - math.cos(rad)*l, cy - math.sin(rad)*l)
        end = (cx + math.cos(rad)*l, cy + math.sin(rad)*l)
        
        # 主斜线 - 紫色
        pygame.draw.line(self.image, MAGENTA, start, end, 6)
        # 高光边缘 - 白色
        pygame.draw.line(self.image, WHITE, start, end, 2)
        
        # 十字斜线 (垂直)
        cross_rad = rad + math.pi / 2
        cross_start = (cx - math.cos(cross_rad)*l*0.7, cy - math.sin(cross_rad)*l*0.7)
        cross_end = (cx + math.cos(cross_rad)*l*0.7, cy + math.sin(cross_rad)*l*0.7)
        pygame.draw.line(self.image, (150, 50, 200), cross_start, cross_end, 3)
        
        # 脉冲光圈
        radius = 60 * progress
        pygame.draw.circle(self.image, (200, 100, 255, 100), (cx, cy), radius, 2)

class NukeExplosion(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        all_sprites.add(self)
        self.life = 60
        self.radius = 10
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.hit_enemies = set()
        sound_mgr.play("nuke")

    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        self.radius += 30  # 快速扩散
        self.image.fill((0,0,0,0))
        
        cx, cy = WIDTH/2, HEIGHT/2
        
        # 阶段1: 核心爆炸 (前30帧)
        if self.life > 30:
            # 白色炽热核心
            pygame.draw.circle(self.image, WHITE, (cx, cy), 40)
            # 橙色外层
            pygame.draw.circle(self.image, (255, 150, 0), (cx, cy), 80, 5)
        
        # 冲击波 - 扩展圆环
        wave_width = 15
        pygame.draw.circle(self.image, (255, 200, 0, 150), (cx, cy), self.radius, wave_width)
        pygame.draw.circle(self.image, (255, 100, 0, 100), (cx, cy), self.radius + 20, wave_width)
        
        # 放射线效果
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            start_x = cx + math.cos(rad) * 30
            start_y = cy + math.sin(rad) * 30
            end_x = cx + math.cos(rad) * self.radius
            end_y = cy + math.sin(rad) * self.radius
            pygame.draw.line(self.image, (255, 150, 0, 150), (start_x, start_y), (end_x, end_y), 3)
        
        # 伤害判定
        if self.life % 2 == 0:
            for m in mobs:
                dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
                if dist < self.radius:
                    if m not in self.hit_enemies:
                        m.hp -= 300
                        self.hit_enemies.add(m)
                        for _ in range(5):
                            Particle(m.rect.center, ORANGE)
                    else:
                        m.hp -= 50

class BlackHole(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        all_sprites.add(self)
        self.pos = pos
        self.life = 180
        self.radius = 10
        self.max_radius = 150  # 增大吸引范围
        self.image = pygame.Surface((self.max_radius*2, self.max_radius*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        self.angle = 0
        self.hit_enemies = set()
        sound_mgr.play("blackhole")

    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        # 控制黑洞大小变化
        if self.life > 150: 
            self.radius = min(self.max_radius, self.radius + 4)
        elif self.life < 30: 
            self.radius = max(0, self.radius - 4)
        
        self.angle = (self.angle + 10) % 360
        self.image = pygame.Surface((self.radius*2 + 40, self.radius*2 + 40), pygame.SRCALPHA)
        cx, cy = self.radius + 20, self.radius + 20
        
        # 黑色核心（绝对黑）
        pygame.draw.circle(self.image, (10, 10, 20), (cx, cy), self.radius)
        
        # 事件视界 - 紫色边框
        pygame.draw.circle(self.image, MAGENTA, (cx, cy), self.radius, 5)
        pygame.draw.circle(self.image, (200, 100, 255), (cx, cy), self.radius - 8, 2)
        
        # 旋转的引力线
        for i in range(0, 360, 30):
            rad = math.radians(i + self.angle)
            start_x = cx + math.cos(rad) * (self.radius - 20)
            start_y = cy + math.sin(rad) * (self.radius - 20)
            end_x = cx + math.cos(rad) * self.radius
            end_y = cy + math.sin(rad) * self.radius
            pygame.draw.line(self.image, MAGENTA, (start_x, start_y), (end_x, end_y), 2)
        
        # 外层吸引光圈
        outer_radius = self.radius + 20
        pygame.draw.circle(self.image, (150, 0, 200, 80), (cx, cy), outer_radius, 3)
        
        # 旋转的粒子环
        for j in range(12):
            angle = (self.angle + j * 30) % 360
            rad = math.radians(angle)
            px = cx + math.cos(rad) * (self.radius + 30)
            py = cy + math.sin(rad) * (self.radius + 30)
            pygame.draw.circle(self.image, (200, 100, 255), (int(px), int(py)), 3)
            
        self.rect = self.image.get_rect(center=self.pos)
        
        # 强大的吸附和伤害效果
        for m in mobs:
            dist = math.hypot(m.rect.centerx - self.pos[0], m.rect.centery - self.pos[1])
            
            # 强吸附范围大
            if dist < self.radius * 3:
                pull_strength = 0.15 * (1 - dist / (self.radius * 3))
                m.rect.centerx += (self.pos[0] - m.rect.centerx) * pull_strength
                m.rect.centery += (self.pos[1] - m.rect.centery) * pull_strength
                
                # 范围内持续伤害
                if dist < self.radius * 1.5:
                    if m not in self.hit_enemies:
                        m.hp -= 150
                        self.hit_enemies.add(m)
                    else:
                        m.hp -= 20
                    # 粒子吸入效果
                    if random.random() < 0.5:
                        Particle(m.rect.center, (200, 100, 255))

class AuroraCurtain(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        all_sprites.add(self)
        self.life = 120
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0,0))
        self.offset = 0
        self.damage_timer = 0
        self.hit_enemies = set()
        sound_mgr.play("hit")

    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        self.offset += 0.3
        self.image.fill((0,0,0,0))
        
        # 3条波纹线，各种极光色
        colors = [TEAL, (0, 255, 128), (0, 100, 255)]
        
        for i, color in enumerate(colors):
            points = []
            for y in range(0, HEIGHT, 20):
                x = WIDTH/2 + math.sin(y * 0.01 + self.offset + i) * (WIDTH/2 - 50)
                points.append((x, y))
            
            if len(points) > 1:
                pygame.draw.lines(self.image, (*color, 150), False, points, 12)
                # 高光边缘
                pygame.draw.lines(self.image, (255, 255, 255, 80), False, points, 3)
        
        # 底部波纹特效
        for i in range(3):
            wave_y = HEIGHT - 50 - i*20
            pygame.draw.line(self.image, CYBER_CYAN_BRIGHT, (0, wave_y), (WIDTH, wave_y), 2)

        # 持续伤害和冻结
        self.damage_timer += 1
        if self.damage_timer % 4 == 0:
            for m in mobs:
                if m not in self.hit_enemies:
                    m.hp -= 120
                    self.hit_enemies.add(m)
                    FloatingText(m.rect.centerx, m.rect.top - 20, "AURORA", TEAL)
                else:
                    m.hp -= 30
                m.frozen_timer = 20
                Particle(m.rect.center, TEAL)

class DeathScythe(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        all_sprites.add(self)
        self.center = center
        self.angle = 0
        self.life = 60
        self.radius = 10
        self.max_radius = 450  # 增大范围
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self.damage_timer = 0
        self.hit_enemies = set()
        sound_mgr.play("laser")

    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        self.angle += 15
        if self.life > 40: self.radius = min(self.max_radius, self.radius + 25)
        
        self.image.fill((0,0,0,0))
        
        # 绘制3条旋转的镰刀弧线
        for i in range(3):
            offset_angle = self.angle + i * 120
            rad = math.radians(offset_angle)
            points = []
            for j in range(20):
                t_angle = offset_angle - j * 3
                t_rad = math.radians(t_angle)
                r = self.radius * (1 - j/40)
                px = self.center[0] + math.cos(t_rad) * r
                py = self.center[1] + math.sin(t_rad) * r
                points.append((px, py))
            
            if len(points) > 2:
                # 主镰刀 - 紫色
                pygame.draw.lines(self.image, (200, 50, 255), False, points, 8)
                # 高光 - 白色
                pygame.draw.lines(self.image, WHITE, False, points, 2)
        
        # 中心光点
        pygame.draw.circle(self.image, WHITE, self.center, 20)
        pygame.draw.circle(self.image, (200, 100, 255), self.center, 15)
        
        # 伤害判定
        self.damage_timer += 1
        if self.damage_timer % 3 == 0:
            for m in mobs:
                dist = math.hypot(m.rect.centerx - self.center[0], m.rect.centery - self.center[1])
                if dist < self.radius:
                    if m not in self.hit_enemies:
                        m.hp -= 350
                        self.hit_enemies.add(m)
                        for _ in range(4):
                            Particle(m.rect.center, (200, 50, 255))
                        FloatingText(m.rect.centerx, m.rect.top - 20, "SCYTHE!", (200, 100, 255))
                    else:
                        m.hp -= 80

# ==============================================================================
#   核心实体：Bullet, Player, Enemy, Boss
# ==============================================================================
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0, is_enemy=False, piercing=0, color=YELLOW, homing=0, bounce=0, b_type="beam"):
        super().__init__()
        self.is_enemy = is_enemy
        self.piercing = piercing
        self.homing = homing
        self.bounce = bounce
        self.color = color
        self.b_type = b_type
        self.timer = 0
        self.frozen = False  # 【新】时间冻结标记
        
        if not is_enemy and homing > 0: 
            self.color = HOMING_COLOR
            
        if is_enemy:
            enemy_bullets.add(self)
            all_sprites.add(self)
            self.speed = 5
            # --- 敌方子弹样式（赛博朋克风格） ---
            if b_type == "needle": 
                # 极光青长针
                self.image = pygame.Surface((6, 20), pygame.SRCALPHA)
                pygame.draw.rect(self.image, CYBER_CYAN_BRIGHT, (2, 0, 2, 20))
                pygame.draw.rect(self.image, CYBER_CYAN, (2, 0, 2, 20), 1)
                self.speed = 9
            elif b_type == "plasma": 
                # 等离子球，警报红
                self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
                pygame.draw.circle(self.image, CYBER_RED_ALERT, (12, 12), 10)
                pygame.draw.circle(self.image, CYBER_RED_ALERT, (12, 12), 10, 2)
                pygame.draw.circle(self.image, (255, 100, 100), (12, 12), 6)
                self.speed = 3.5
            elif b_type == "wave": 
                # 波纹，紫色
                self.image = pygame.Surface((30, 10), pygame.SRCALPHA)
                pygame.draw.arc(self.image, MAGENTA, (0,0,30,10), 0, 3.14, 3)
                pygame.draw.arc(self.image, CYBER_CYAN_BRIGHT, (0,0,30,10), 0, 3.14, 1)
                self.speed = 4.5
            elif b_type == "orb": 
                # 球体，各种颜色
                self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(self.image, color, (10,10), 10)
                pygame.draw.circle(self.image, color, (10,10), 10, 2)
                pygame.draw.circle(self.image, WHITE, (10,10), 5)
                self.speed = 4
            elif b_type == "laser_beam": 
                # 激光束，红色
                self.image = pygame.Surface((10, 40), pygame.SRCALPHA)
                pygame.draw.rect(self.image, CYBER_RED_ALERT, (0,0,10,40))
                pygame.draw.rect(self.image, CYBER_RED_ALERT, (0,0,10,40), 1)
                self.speed = 12
            elif b_type == "skull": 
                # 骷髅，幽灵青
                self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(self.image, CYBER_CYAN_BRIGHT, (10,8), 8)
                pygame.draw.circle(self.image, CYBER_CYAN_BRIGHT, (10,8), 8, 1)
                pygame.draw.rect(self.image, CYBER_CYAN_BRIGHT, (6, 12, 8, 6))
                self.speed = 3
            elif b_type == "blade_wind": 
                # 风刃，蓝色
                self.image = pygame.Surface((24, 10), pygame.SRCALPHA)
                pygame.draw.arc(self.image, WIND_BLUE, (0,0,24,10), 0, 3.14, 2)
                pygame.draw.arc(self.image, CYBER_CYAN_BRIGHT, (0,0,24,10), 0, 3.14, 1)
                self.speed = 8
            elif b_type == "gear":  # 齿轮弹 - 虚空魔像
                self.image = pygame.Surface((18, 18), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (120, 0, 180), (9, 9), 7)
                for j in range(8):
                    angle = j * math.pi / 4
                    x1 = 9 + int(7 * math.cos(angle))
                    y1 = 9 + int(7 * math.sin(angle))
                    x2 = 9 + int(10 * math.cos(angle))
                    y2 = 9 + int(10 * math.sin(angle))
                    pygame.draw.line(self.image, (180, 0, 220), (x1, y1), (x2, y2), 1)
                self.speed = 5
            elif b_type == "energy":  # 能量弹 - 虚空魔像
                self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (180, 20, 220), (8, 8), 6)
                pygame.draw.circle(self.image, (220, 100, 255), (8, 8), 4)
                pygame.draw.circle(self.image, WHITE, (8, 8), 2)
                self.speed = 6
            elif b_type == "core":  # 核心冲击弹 - 虚空魔像
                self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (255, 80, 180), (10, 10), 8)
                pygame.draw.circle(self.image, (255, 150, 200), (10, 10), 5)
                pygame.draw.circle(self.image, WHITE, (10, 10), 2)
                self.speed = 7
            elif b_type == "star":  # 星形弹 - 星渊女王
                self.image = pygame.Surface((18, 18), pygame.SRCALPHA)
                pygame.draw.polygon(self.image, (180, 80, 255), [(9,0), (11,6), (18,9), (11,12), (9,18), (6,12), (0,9), (6,6)])
                pygame.draw.polygon(self.image, (220, 150, 255), [(9,0), (11,6), (18,9), (11,12), (9,18), (6,12), (0,9), (6,6)], 1)
                self.speed = 5
            elif b_type == "star_guard":  # 星卫卫兵弹 - 星渊女王
                self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.polygon(self.image, (120, 60, 200), [(8,0), (10,5), (16,8), (10,11), (8,16), (5,11), (0,8), (5,5)])
                pygame.draw.circle(self.image, (180, 100, 255), (8, 8), 3)
                self.speed = 4
            elif b_type == "star_burst":  # 星爆弹 - 星渊女王
                self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (255, 180, 255), (10, 10), 8)
                pygame.draw.circle(self.image, (255, 200, 255), (10, 10), 5)
                for j in range(8):
                    angle = j * math.pi / 4
                    x = 10 + int(12 * math.cos(angle))
                    y = 10 + int(12 * math.sin(angle))
                    pygame.draw.line(self.image, (255, 150, 220), (10, 10), (x, y), 1)
                self.speed = 6
            elif b_type == "ice_shard":  # 冰晶 - 时间/冻结主题
                self.image = pygame.Surface((14, 14), pygame.SRCALPHA)
                pygame.draw.polygon(self.image, (200, 255, 255), [(7,0), (14,7), (7,14), (0,7)])
                pygame.draw.polygon(self.image, CYBER_CYAN_BRIGHT, [(7,0), (14,7), (7,14), (0,7)], 1)
                self.speed = 5.5
            elif b_type == "flame_burst":  # 火焰喷射 - 末日/热能主题
                self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (255, 80, 0), (8, 8), 6)
                pygame.draw.circle(self.image, (255, 140, 20), (8, 8), 4)
                pygame.draw.circle(self.image, CYBER_AMBER, (8, 8), 2)
                self.speed = 6.5
            elif b_type == "tentacle":  # 触手弹 - 深渊/生物主题
                self.image = pygame.Surface((14, 20), pygame.SRCALPHA)
                pygame.draw.lines(self.image, (120, 30, 150), False, [(7,0), (3,8), (7,16), (11,20)], 2)
                pygame.draw.lines(self.image, (200, 100, 200), False, [(7,0), (3,8), (7,16), (11,20)], 1)
                self.speed = 5
            elif b_type == "drone_swarm":  # 无人机群弹 - 虚空母舰
                self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (200, 50, 50), (2, 2, 8, 8))
                pygame.draw.rect(self.image, (255, 100, 100), (2, 2, 8, 8), 1)
                pygame.draw.circle(self.image, WHITE, (6, 6), 2)
                self.speed = 5.5
            elif b_type == "laser_barrage":  # 激光扫射 - 堡垒/工业主题
                self.image = pygame.Surface((8, 32), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (255, 140, 0), (2, 0, 4, 32))
                pygame.draw.rect(self.image, CYBER_AMBER, (2, 0, 4, 32), 1)
                self.speed = 8
            elif b_type == "phantom":  # 幻影弹 - 虚空刺客
                self.image = pygame.Surface((14, 14), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (150, 50, 150), (7, 7), 5)
                pygame.draw.circle(self.image, (200, 100, 200), (7, 7), 3)
                pygame.draw.circle(self.image, CYBER_CYAN_BRIGHT, (7, 7), 1)
                self.speed = 7
            elif b_type == "holy_light":  # 圣光 - 审判/天使主题
                self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (255, 200, 100), (8, 8), 6)
                pygame.draw.circle(self.image, CYBER_AMBER, (8, 8), 4)
                pygame.draw.circle(self.image, WHITE, (8, 8), 2)
                self.speed = 5.5
            elif b_type == "glitch":  # 故障体素 - 网络/病毒主题
                self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (0, 200, 0), (0, 2, 4, 4))
                pygame.draw.rect(self.image, (0, 255, 100), (8, 6, 4, 4))
                pygame.draw.rect(self.image, CYBER_LIME, (4, 0, 4, 4))
                self.speed = 4.5
            elif b_type == "void_spike":  # 虚空尖刺 - 深渊主题
                self.image = pygame.Surface((10, 22), pygame.SRCALPHA)
                pygame.draw.polygon(self.image, (100, 0, 150), [(5,0), (10,10), (7,22), (3,22), (0,10)])
                pygame.draw.polygon(self.image, (180, 0, 255), [(5,0), (10,10), (7,22), (3,22), (0,10)], 1)
                self.speed = 6.5
            else: 
                # 默认敌方子弹，红色
                self.image = pygame.Surface((14, 14), pygame.SRCALPHA)
                pygame.draw.circle(self.image, CYBER_RED_ALERT, (7,7), 5)
                pygame.draw.circle(self.image, CYBER_RED_ALERT, (7,7), 5, 1)
                pygame.draw.circle(self.image, WHITE, (7,7), 2)
        else:
            bullets.add(self)
            all_sprites.add(self)
            self.speed = -12
            # --- 玩家子弹样式（赛博朋克风格） ---
            if b_type == "beam": 
                # 极光青光束
                self.image = pygame.Surface((10, 30), pygame.SRCALPHA)
                pygame.draw.rect(self.image, CYBER_CYAN, (3, 0, 4, 30))
                pygame.draw.rect(self.image, CYBER_CYAN_BRIGHT, (3, 0, 4, 30), 1)
                pygame.draw.rect(self.image, WHITE, (4, 5, 2, 20))
            elif b_type == "shard": 
                # 菱形碎片，紫色
                self.image = pygame.Surface((16, 24), pygame.SRCALPHA)
                pygame.draw.polygon(self.image, MAGENTA, [(8,0), (16,12), (8,24), (0,12)])
                pygame.draw.polygon(self.image, CYBER_CYAN_BRIGHT, [(8,0), (16,12), (8,24), (0,12)], 1)
            elif b_type == "rocket": 
                # 火箭，琥珀黄头部
                self.image = pygame.Surface((14, 28), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (255, 140, 0), (2, 8, 10, 16))
                pygame.draw.rect(self.image, CYBER_AMBER, (2, 8, 10, 16), 1)
                pygame.draw.polygon(self.image, CYBER_AMBER, [(2,8), (7,2), (12,8)])
                pygame.draw.rect(self.image, CYBER_RED_ALERT, (4, 24, 6, 4))
            elif b_type == "lightning": 
                # 连锁闪电，琥珀黄
                self.image = pygame.Surface((12, 30), pygame.SRCALPHA)
                pygame.draw.lines(self.image, CYBER_AMBER, False, [(6,0), (2,10), (10,20), (6,30)], 2)
                pygame.draw.lines(self.image, WHITE, False, [(6,0), (2,10), (10,20), (6,30)], 1)
            elif b_type == "acid": 
                # 腐蚀液，荧光绿
                self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(self.image, CYBER_LIME, (8,8), 6)
                pygame.draw.circle(self.image, CYBER_LIME, (8,8), 6, 1)
                pygame.draw.circle(self.image, WHITE, (6,6), 2)
            elif b_type == "spectral": 
                # 谱能，紫色
                self.image = pygame.Surface((14, 30), pygame.SRCALPHA)
                pygame.draw.lines(self.image, (180, 150, 255), False, [(7,0), (2,10), (12,20), (7,30)], 3)
                pygame.draw.circle(self.image, WHITE, (7, 5), 3)
            elif b_type == "prism": 
                # 棱镜，青色
                self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.polygon(self.image, WHITE, [(8,0), (16,8), (8,16), (0,8)])
                pygame.draw.polygon(self.image, CYBER_CYAN, [(8,4), (12,8), (8,12), (4,8)])
                self.speed = -10
            elif b_type == "blade": 
                # 光刃，红色
                self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.arc(self.image, CYBER_RED_ALERT, (0,0,30,30), 0, 3.14, 3)
                pygame.draw.arc(self.image, CYBER_CYAN_BRIGHT, (0,0,30,30), 0, 3.14, 1)
                self.speed = -15
            elif b_type == "star": 
                # 星镖，靛蓝
                self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.polygon(self.image, INDIGO, [(10,0), (13,7), (20,10), (13,13), (10,20), (7,13), (0,10), (7,7)])
                pygame.draw.polygon(self.image, CYBER_CYAN_BRIGHT, [(10,0), (13,7), (20,10), (13,13), (10,20), (7,13), (0,10), (7,7)], 1)
                pygame.draw.circle(self.image, WHITE, (10,10), 3)
            elif b_type == "thorn": 
                # 荆棘，绿色
                self.image = pygame.Surface((10, 24), pygame.SRCALPHA)
                pygame.draw.polygon(self.image, FOREST, [(5,0), (10,10), (5,24), (0,10)])
                pygame.draw.polygon(self.image, CYBER_LIME, [(5,0), (10,10), (5,24), (0,10)], 1)
            elif b_type == "web": 
                # 蛛网，灰色
                self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
                pygame.draw.line(self.image, (200, 200, 200), (0,12), (24,12), 2)
                pygame.draw.line(self.image, (200, 200, 200), (12,0), (12,24), 2)
                pygame.draw.circle(self.image, CYBER_CYAN_BRIGHT, (12, 12), 3, 1)
                self.speed = -8
            elif b_type == "flame": 
                # 烈焰，橙色
                self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (255, 140, 0), (8,8), 6)
                pygame.draw.circle(self.image, CYBER_AMBER, (8,8), 6, 1)
                pygame.draw.circle(self.image, CYBER_RED_ALERT, (8,8), 3)
                self.speed = -14
            elif b_type == "quant": 
                # 量子，紫色方块
                self.image = pygame.Surface((14, 14), pygame.SRCALPHA)
                pygame.draw.rect(self.image, NEON_PURPLE, (2,2,10,10))
                pygame.draw.rect(self.image, CYBER_CYAN_BRIGHT, (2,2,10,10), 1)
                pygame.draw.rect(self.image, WHITE, (4,4,6,6))
                self.speed = -10
            elif b_type == "shadow":
                # 暗影，深紫色
                self.image = pygame.Surface((12, 28), pygame.SRCALPHA)
                pygame.draw.polygon(self.image, (100, 50, 180), [(6,0), (12,8), (10,28), (2,28), (0,8)])
                pygame.draw.polygon(self.image, (150, 100, 255), [(6,0), (12,8), (10,28), (2,28), (0,8)], 1)
                pygame.draw.circle(self.image, (200, 150, 255), (6, 8), 2)
                self.speed = -11
            else: 
                # 默认标准光束
                self.image = pygame.Surface((10, 24), pygame.SRCALPHA)
                pygame.draw.rect(self.image, CYBER_CYAN, (3,0,4,24))
                pygame.draw.rect(self.image, WHITE, (3,0,4,24), 1)
        
        if angle != 0: 
            self.image = pygame.transform.rotate(self.image, -angle)
        
        self.rect = self.image.get_rect(center=(x, y))
        rad = math.radians(angle)
        
        if is_enemy: 
            self.vel = pygame.math.Vector2(math.sin(rad) * self.speed, math.cos(rad) * self.speed)
        else: 
            self.vel = pygame.math.Vector2(-math.sin(rad) * abs(self.speed), -math.cos(rad) * abs(self.speed))
        
        self.pos = pygame.math.Vector2(x, y)
        self.start_x = x

    def update(self):
        self.timer += 1
        
        # 【改进】时间冻结时跳过移动
        if self.frozen:
            return
        
        # 特殊移动逻辑
        if not self.is_enemy and self.b_type == "flame":
            if self.timer > 25: self.kill()
            self.pos += self.vel * (1.0 - self.timer/30.0)
        else: 
            self.pos += self.vel
            
        # 追踪逻辑
        if not self.is_enemy and self.homing > 0:
            target = None
            min_dist = 9999
            for m in mobs:
                dist = self.pos.distance_to(pygame.math.Vector2(m.rect.center))
                if dist < min_dist and dist < 500: # 增加索敌范围
                    min_dist = dist
                    target = m
            if target:
                target_vec = pygame.math.Vector2(target.rect.center) - self.pos
                if target_vec.length() > 0: 
                    target_vec = target_vec.normalize() * abs(self.speed)
                    self.vel = self.vel.lerp(target_vec, 0.15) # 平滑转向
                    
        self.rect.center = self.pos
        
        # 反弹逻辑
        if not self.is_enemy and self.bounce > 0:
            bounced = False
            if self.rect.left < 0: 
                self.vel.x *= -1
                self.pos.x = self.rect.width
                bounced = True
            elif self.rect.right > WIDTH: 
                self.vel.x *= -1
                self.pos.x = WIDTH - self.rect.width
                bounced = True
            elif self.rect.top < 0: 
                self.vel.y *= -1
                self.pos.y = self.rect.height
                bounced = True
            if bounced: 
                self.bounce -= 1
                
        if not screen_rect.colliderect(self.rect): 
            self.kill()

# 辅助: 屏幕矩形
screen_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, type_name):
        super().__init__()
        mobs.add(self)
        all_sprites.add(self)
        self.type = type_name
        self.frozen_timer = 0
        self.base_speed = 0
        self.is_elite = False
        self.state = "move"
        self.timer = 0
        self.radius = 20
        self.affix = None
        
        if random.random() < 0.1: self.is_elite = True
        lvl = 1 
        
        if type_name == "drone":
            # 无人机：机身+螺旋桨设计
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            center = 25
            # 中央机身（椭圆）
            pygame.draw.ellipse(self.image, (255, 100, 150), (10, 18, 30, 14))
            pygame.draw.ellipse(self.image, (255, 200, 100), (10, 18, 30, 14), 2)
            # 4个螺旋桨
            for i in range(4):
                angle = i * 90
                rad = math.radians(angle)
                x1 = center + math.cos(rad) * 8
                y1 = center + math.sin(rad) * 8
                x2 = center + math.cos(rad) * 20
                y2 = center + math.sin(rad) * 20
                pygame.draw.line(self.image, (100, 255, 200), (x1, y1), (x2, y2), 3)
                pygame.draw.circle(self.image, (0, 255, 255), (int(x1), int(y1)), 3)
            # 驾驶舱（前端发光点）
            pygame.draw.circle(self.image, (255, 255, 100), (center, center), 4)
            self.base_speed = 3; self.hp = 25 + lvl * 10
            self.neon_color = (255, 100, 150)
            
        elif type_name == "chaser":
            # 拦截者：尖端战斗机设计
            self.image = pygame.Surface((45, 50), pygame.SRCALPHA)
            # 机身（尖端）
            body_points = [(22, 5), (35, 35), (22, 48), (9, 35)]
            pygame.draw.polygon(self.image, (100, 150, 255), body_points)
            pygame.draw.polygon(self.image, (200, 150, 255), body_points, 2)
            # 机翼发光条
            pygame.draw.line(self.image, (255, 100, 200), (5, 30), (40, 30), 3)
            # 尾部引擎喷口（双引擎）
            pygame.draw.circle(self.image, (255, 200, 0), (15, 45), 3)
            pygame.draw.circle(self.image, (255, 200, 0), (29, 45), 3)
            # 驾驶舱
            pygame.draw.circle(self.image, (100, 255, 255), (22, 15), 3)
            self.base_speed = 4; self.hp = 40 + lvl * 15
            self.neon_color = (100, 150, 255)
            
        elif type_name == "tank":
            # 坦克：履带型装甲战车
            self.image = pygame.Surface((55, 50), pygame.SRCALPHA)
            # 主炮塔（圆形）
            pygame.draw.circle(self.image, (255, 100, 0), (27, 20), 12)
            pygame.draw.circle(self.image, (255, 150, 100), (27, 20), 12, 2)
            # 主炮口（上方）
            pygame.draw.line(self.image, (200, 100, 255), (27, 8), (27, -2), 4)
            pygame.draw.circle(self.image, (200, 100, 255), (27, 8), 3)
            # 车体（矩形）
            pygame.draw.rect(self.image, (100, 100, 150), (8, 28, 38, 18))
            pygame.draw.rect(self.image, (150, 150, 200), (8, 28, 38, 18), 2)
            # 履带（两边装甲条）
            for y in [30, 40]:
                pygame.draw.line(self.image, (100, 200, 255), (8, y), (46, y), 2)
            # 车轮（4个）
            for x in [12, 22, 32, 42]:
                pygame.draw.circle(self.image, (150, 100, 50), (x, 48), 3)
            self.base_speed = 1.5; self.hp = 65 + lvl * 18; self.radius = 25
            self.neon_color = (255, 150, 0)
            
        elif type_name == "wasp":
            # 黄蜂：细长轰炸机
            self.image = pygame.Surface((35, 55), pygame.SRCALPHA)
            # 机身（细长）
            body = [(17, 8), (25, 15), (28, 30), (25, 45), (17, 52), (9, 45), (6, 30), (9, 15)]
            pygame.draw.polygon(self.image, (255, 200, 0), body)
            pygame.draw.polygon(self.image, (255, 100, 100), body, 2)
            # 机翼（两侧）
            pygame.draw.polygon(self.image, (255, 150, 0), [(2, 25), (10, 28), (10, 32), (2, 35)])
            pygame.draw.polygon(self.image, (255, 150, 0), [(32, 25), (24, 28), (24, 32), (32, 35)])
            # 炸弹舱（下方）
            pygame.draw.rect(self.image, (200, 100, 200), (14, 35, 6, 8))
            # 驾驶舱
            pygame.draw.circle(self.image, (255, 255, 150), (17, 12), 2)
            self.base_speed = 3.5; self.hp = 35 + lvl * 11; self.radius = 17
            self.neon_color = (255, 200, 0)
            self.start_x = random.randint(0, WIDTH)
            
        elif type_name == "sniper":
            # 狙击手：细长塔楼+瞄准系统
            self.image = pygame.Surface((32, 65), pygame.SRCALPHA)
            # 基座
            pygame.draw.rect(self.image, (100, 50, 50), (4, 50, 24, 12))
            pygame.draw.rect(self.image, (200, 100, 100), (4, 50, 24, 12), 2)
            # 塔身
            pygame.draw.polygon(self.image, (100, 100, 200), [(8, 50), (24, 50), (22, 15), (10, 15)])
            pygame.draw.polygon(self.image, (150, 150, 255), [(8, 50), (24, 50), (22, 15), (10, 15)], 2)
            # 瞄准镜（顶部旋转结构）
            pygame.draw.circle(self.image, (255, 100, 100), (16, 10), 6)
            pygame.draw.circle(self.image, (255, 200, 0), (16, 10), 6, 2)
            pygame.draw.line(self.image, (0, 200, 255), (16, 4), (16, 16), 1)
            pygame.draw.line(self.image, (0, 200, 255), (10, 10), (22, 10), 1)
            self.base_speed = 3; self.hp = 45 + lvl * 11
            self.neon_color = (100, 200, 255)
            
        elif type_name == "glitch":
            # 虫群：有机触手怪
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            center = 25
            # 主体（不规则球形）
            body_points = [(25, 10), (35, 15), (40, 25), (35, 35), (25, 40), (15, 35), (10, 25), (15, 15)]
            pygame.draw.polygon(self.image, (200, 100, 200), body_points)
            pygame.draw.polygon(self.image, (150, 200, 255), body_points, 2)
            # 6条触手
            tentacle_angles = [0, 60, 120, 180, 240, 300]
            for angle in tentacle_angles:
                rad = math.radians(angle)
                x1 = center + math.cos(rad) * 12
                y1 = center + math.sin(rad) * 12
                x2 = center + math.cos(rad) * 23
                y2 = center + math.sin(rad) * 23
                pygame.draw.line(self.image, (255, 150, 100), (int(x1), int(y1)), (int(x2), int(y2)), 3)
                pygame.draw.circle(self.image, (255, 100, 200), (int(x2), int(y2)), 2)
            # 多个眼睛
            for i in range(3):
                eye_x = 18 + i * 7
                pygame.draw.circle(self.image, (100, 255, 200), (eye_x, 20), 2)
            self.base_speed = 2; self.hp = 28 + lvl * 7
            self.neon_color = (200, 100, 200)
        
        elif type_name == "sentinel":
            # 哨兵：防御炮台
            self.image = pygame.Surface((45, 55), pygame.SRCALPHA)
            # 基座（厚重）
            pygame.draw.rect(self.image, (100, 50, 50), (8, 40, 29, 12))
            pygame.draw.rect(self.image, (200, 100, 100), (8, 40, 29, 12), 2)
            # 炮塔（八边形）
            tower_points = [(22, 20), (32, 25), (35, 35), (32, 40), (22, 42), (12, 40), (9, 35), (12, 25)]
            pygame.draw.polygon(self.image, (180, 50, 50), tower_points)
            pygame.draw.polygon(self.image, (255, 100, 100), tower_points, 2)
            # 主炮（上方）
            pygame.draw.line(self.image, (255, 50, 50), (22, 20), (22, 5), 5)
            pygame.draw.circle(self.image, (255, 150, 100), (22, 5), 4)
            # 侧炮孔
            pygame.draw.circle(self.image, (200, 100, 50), (12, 30), 2)
            pygame.draw.circle(self.image, (200, 100, 50), (32, 30), 2)
            self.base_speed = 1.2; self.hp = 55 + lvl * 14; self.radius = 20
            self.neon_color = (255, 100, 100)
            self.state = "aim"
            self.timer = 0
        
        elif type_name == "phantom":
            # 幽灵：能量体设计
            self.image = pygame.Surface((45, 50), pygame.SRCALPHA)
            # 能量核心（中心）
            pygame.draw.circle(self.image, (200, 100, 255), (22, 25), 8)
            pygame.draw.circle(self.image, (255, 200, 255), (22, 25), 8, 2)
            # 围绕能量体的轨道环
            for radius in [12, 18, 24]:
                pygame.draw.circle(self.image, (150, 100, 200), (22, 25), radius, 1)
            # 3个环绕轨道点
            for i in range(3):
                angle = i * 120 + pygame.time.get_ticks() / 1000
                rad = math.radians(angle)
                x = 22 + math.cos(rad) * 18
                y = 25 + math.sin(rad) * 18
                pygame.draw.circle(self.image, (100, 255, 200), (int(x), int(y)), 2)
            self.base_speed = 3.8; self.hp = 35 + lvl * 10; self.radius = 16
            self.neon_color = (200, 100, 255)
        
        elif type_name == "spike":
            # 刺球：带刺的生物
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            center = 25
            # 主体（球形）
            pygame.draw.circle(self.image, (255, 100, 50), (center, center), 13)
            pygame.draw.circle(self.image, (255, 150, 100), (center, center), 13, 2)
            # 12个棘刺（3D效果）
            for i in range(12):
                angle = i * 30
                rad = math.radians(angle)
                x1 = center + math.cos(rad) * 13
                y1 = center + math.sin(rad) * 13
                x2 = center + math.cos(rad) * 24
                y2 = center + math.sin(rad) * 24
                pygame.draw.line(self.image, (255, 200, 0), (x1, y1), (x2, y2), 3)
                # 棘刺顶端
                pygame.draw.circle(self.image, (255, 150, 0), (int(x2), int(y2)), 2)
            # 眼睛
            pygame.draw.circle(self.image, (255, 255, 150), (20, 22), 2)
            pygame.draw.circle(self.image, (255, 255, 150), (30, 22), 2)
            self.base_speed = 2.5; self.hp = 45 + lvl * 12; self.radius = 18
            self.neon_color = (255, 150, 50)
        
        elif type_name == "orbiter":
            # 轨道体：浮游生物
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            center = 25
            # 中心核体（紫色）
            pygame.draw.circle(self.image, (200, 100, 255), (center, center), 10)
            pygame.draw.circle(self.image, (255, 150, 255), (center, center), 10, 2)
            # 3个环绕外壳
            for radius in [16, 22, 28]:
                pygame.draw.circle(self.image, (100, 200, 255), (center, center), radius, 2)
            # 12个环绕信号点
            for i in range(12):
                angle = i * 30
                rad = math.radians(angle)
                x = center + math.cos(rad) * 24
                y = center + math.sin(rad) * 24
                pygame.draw.circle(self.image, (100, 255, 200), (int(x), int(y)), 2)
            self.base_speed = 3.2; self.hp = 38 + lvl * 10; self.radius = 17
            self.neon_color = (100, 200, 255)
        
        elif type_name == "vortex":
            # 漩涡：螺旋生命体
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            center = 25
            # 3层螺旋环
            for layer, (radius, color, width) in enumerate([
                (18, (100, 255, 100), 3),
                (12, (150, 255, 150), 2),
                (6, (200, 255, 100), 1)
            ]):
                pygame.draw.circle(self.image, color, (center, center), radius, width)
            # 旋转的内部纹理
            for i in range(8):
                angle = (pygame.time.get_ticks() / 500 + i * 45) % 360
                rad = math.radians(angle)
                x = center + math.cos(rad) * 10
                y = center + math.sin(rad) * 10
                pygame.draw.circle(self.image, (200, 100, 255), (int(x), int(y)), 1)
            # 中心吸收孔
            pygame.draw.circle(self.image, (100, 100, 100), (center, center), 3)
            self.base_speed = 2.2; self.hp = 25 + lvl * 8; self.radius = 15
            self.neon_color = (100, 255, 100)
        
        # Add subtle neon glow aura for enemies
        try:
            neon = getattr(self, 'neon_color', None)
            if neon:
                w, h = self.image.get_size()
                glow_surf = pygame.Surface((w+24, h+24), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*neon, 30), (w//2+12, h//2+12), max(w, h)//2 + 6)
                # Create a new surface and blit the glow then image
                final_surf = pygame.Surface((w+24, h+24), pygame.SRCALPHA)
                final_surf.blit(glow_surf, (0, 0))
                final_surf.blit(self.image, (12, 12))
                self.image = final_surf
        except Exception:
            pass
        self.rect = self.image.get_rect()
        if type_name != "wasp":
            self.rect.x = random.randint(0, WIDTH-50)
            self.rect.y = random.randint(-100, -40)
        else:
            self.rect.x = self.start_x
            self.rect.y = random.randint(-100, -40)

        if self.is_elite:
            self.affix = random.choice(["fast", "tank", "split"])
            self.hp *= 3
            if self.affix == "fast": self.base_speed *= 1.5
            elif self.affix == "tank": 
                self.hp *= 2
                self.radius *= 1.3
                # 精英怪：重新建模，采用完全不同的设计
                self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
                center = 30
                
                # 根据原敌人类型重新建模
                if self.type == "drone":
                    # 精英六边形：多层金色结构
                    for layer, (size, color, width) in enumerate([
                        (22, (255, 200, 0), 0),
                        (20, (255, 150, 0), 2),
                        (15, (200, 150, 100), 0)
                    ]):
                        hex_points = []
                        for i in range(6):
                            angle = i * 60
                            rad = math.radians(angle)
                            x = center + size * math.cos(rad)
                            y = center + size * math.sin(rad)
                            hex_points.append((x, y))
                        pygame.draw.polygon(self.image, color, hex_points) if width == 0 else pygame.draw.polygon(self.image, color, hex_points, width)
                    # 中心星形
                    for i in range(6):
                        angle = i * 60
                        rad = math.radians(angle)
                        x = center + 10 * math.cos(rad)
                        y = center + 10 * math.sin(rad)
                        pygame.draw.circle(self.image, (255, 255, 150), (int(x), int(y)), 2)
                
                elif self.type == "tank":
                    # 精英坦克：多层棱柱结构
                    # 外层十边形
                    dec_points = []
                    for i in range(10):
                        angle = i * 36
                        rad = math.radians(angle)
                        x = center + 22 * math.cos(rad)
                        y = center + 22 * math.sin(rad)
                        dec_points.append((x, y))
                    pygame.draw.polygon(self.image, (255, 200, 0), dec_points)
                    pygame.draw.polygon(self.image, (255, 150, 0), dec_points, 2)
                    # 中层八边形
                    for i in range(8):
                        angle = i * 45
                        rad = math.radians(angle)
                        x = center + 16 * math.cos(rad)
                        y = center + 16 * math.sin(rad)
                        pygame.draw.circle(self.image, (200, 100, 255), (int(x), int(y)), 3)
                    # 中心
                    pygame.draw.circle(self.image, (255, 255, 0), (center, center), 8)
                
                else:
                    # 其他精英怪：多色分层星形
                    # 3层星形
                    for layer, (points_count, radius, color) in enumerate([
                        (8, 22, (255, 200, 0)),
                        (6, 16, (200, 100, 255)),
                        (4, 10, (100, 255, 200))
                    ]):
                        for i in range(points_count):
                            angle = (i * 360 / points_count) + (layer * 15)
                            rad = math.radians(angle)
                            x = center + radius * math.cos(rad)
                            y = center + radius * math.sin(rad)
                            pygame.draw.circle(self.image, color, (int(x), int(y)), 3 - layer)
                    # 中心发光球
                    pygame.draw.circle(self.image, (255, 255, 100), (center, center), 6)
                
        self.speed = self.base_speed
        self.max_hp = self.hp

    def update(self):
        if self.frozen_timer > 0:
            self.frozen_timer -= 1
            return # 冻结不移动
            
        t = pygame.time.get_ticks() / 1000.0
        self.timer += 1
        
        # 更新移动和攻击
        if self.type == "drone":
            # 无人机：螺旋下降轨迹
            self.rect.y += self.speed
            self.rect.x = WIDTH // 2 + math.sin(t * 2 + self.rect.y * 0.01) * 100
            # 定时散射攻击
            if self.timer % 40 == 0:
                for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
                    rad = math.radians(angle)
                    vx = math.cos(rad) * 3
                    vy = math.sin(rad) * 3
                    Bullet(self.rect.centerx, self.rect.centery, vx=vx, vy=vy, is_enemy=True, color=(255, 100, 150), b_type="needle")
        
        elif self.type == "chaser":
            # 拦截者：之字形移动 + 追踪
            self.rect.y += self.speed
            self.rect.x = WIDTH // 2 + math.sin(t * 4) * 120
            # 高频攻击
            if self.timer % 25 == 0:
                Bullet(self.rect.centerx, self.rect.bottom, is_enemy=True, color=(100, 150, 255), b_type="needle")
                Bullet(self.rect.centerx + 10, self.rect.bottom, is_enemy=True, color=(100, 150, 255), b_type="needle")
                Bullet(self.rect.centerx - 10, self.rect.bottom, is_enemy=True, color=(100, 150, 255), b_type="needle")
        
        elif self.type == "tank":
            # 坦克：缓慢直线 + 定点炮击
            self.rect.y += self.speed * 0.8
            # 每隔一段时间开火一轮
            if self.timer % 60 == 0:
                for angle in [-30, 0, 30]:
                    rad = math.radians(angle)
                    vx = math.sin(rad) * 2.5
                    vy = math.cos(rad) * 2.5 + 1
                    Bullet(self.rect.centerx, self.rect.bottom, vx=vx, vy=vy, is_enemy=True, color=(255, 100, 0), b_type="needle")
        
        elif self.type == "wasp":
            # 黄蜂：蛇形飞行轨迹 + 单点狙击
            self.rect.y += self.speed
            self.rect.x = self.start_x + math.sin(t * 3) * 150
            if self.timer % 50 == 0:
                Bullet(self.rect.centerx, self.rect.bottom, is_enemy=True, color=(255, 200, 0), b_type="needle")
        
        elif self.type == "sniper":
            # 狙击手：降落后狙击
            if self.state == "move":
                self.rect.y += self.speed
                if self.rect.y > 150: 
                    self.state = "aim"
                    self.timer = 0
            elif self.state == "aim":
                self.timer += 1
                if self.timer > 40 and self.timer % 30 == 0:
                    Bullet(self.rect.centerx, self.rect.bottom, is_enemy=True, color=(0, 200, 255), b_type="needle")
            
        elif self.type == "glitch":
            # 虫群：快速冲刺+集团攻击
            self.rect.y += self.speed
            self.rect.x = WIDTH // 2 + math.cos(t * 3) * 80
            if self.timer % 35 == 0:
                # 8向散射
                for i in range(8):
                    angle = i * 45
                    rad = math.radians(angle)
                    vx = math.cos(rad) * 2
                    vy = math.sin(rad) * 2 + 1
                    Bullet(self.rect.centerx, self.rect.centery, vx=vx, vy=vy, is_enemy=True, color=(200, 100, 200), b_type="needle")
        
        elif self.type == "sentinel":
            # 哨兵：固定位置+范围炮击
            self.rect.y += self.speed * 0.5
            if self.state == "move" and self.rect.y > 120:
                self.state = "aim"
                self.timer = 0
            elif self.state == "aim":
                # 固定位置后持续开火
                if self.timer % 30 == 0:
                    for angle in [-45, -15, 0, 15, 45]:
                        rad = math.radians(angle)
                        vx = math.sin(rad) * 3
                        vy = math.cos(rad) * 2 + 2
                        Bullet(self.rect.centerx, self.rect.bottom, vx=vx, vy=vy, is_enemy=True, color=(255, 100, 100), b_type="needle")
                self.timer += 1
        
        elif self.type == "phantom":
            # 幽灵：随机闪现轨迹 + 能量弹
            self.rect.y += self.speed
            # 随机横向移动
            if self.timer % 20 == 0:
                self.rect.x += random.choice([-60, -30, 0, 30, 60])
                self.rect.x = max(20, min(WIDTH - 20, self.rect.x))
            # 能量球攻击
            if self.timer % 45 == 0:
                for i in range(3):
                    angle = i * 120
                    rad = math.radians(angle)
                    vx = math.cos(rad) * 2.5
                    vy = math.sin(rad) * 1.5 + 2
                    Bullet(self.rect.centerx, self.rect.centery, vx=vx, vy=vy, is_enemy=True, color=(200, 100, 255), b_type="needle")
        
        elif self.type == "spike":
            # 刺球：随机弹跳 + 棘刺喷射
            self.rect.y += self.speed
            if self.timer % 40 == 0:
                self.rect.x += random.choice([-50, 50])
            # 全方位棘刺喷射
            if self.timer % 50 == 0:
                for i in range(12):
                    angle = i * 30
                    rad = math.radians(angle)
                    vx = math.cos(rad) * 2.5
                    vy = math.sin(rad) * 2.5 + 1
                    Bullet(self.rect.centerx, self.rect.centery, vx=vx, vy=vy, is_enemy=True, color=(255, 150, 50), b_type="needle")
        
        elif self.type == "orbiter":
            # 轨道体：螺旋下降 + 追踪弹
            self.rect.y += self.speed * 0.9
            self.rect.x = WIDTH // 2 + math.cos(t * 2 + self.rect.y * 0.01) * 120
            # 追踪攻击
            if self.timer % 55 == 0:
                for i in range(4):
                    angle = i * 90
                    rad = math.radians(angle)
                    vx = math.cos(rad) * 1.5
                    vy = math.sin(rad) * 1.5 + 1.5
                    Bullet(self.rect.centerx, self.rect.centery, vx=vx, vy=vy, is_enemy=True, color=(100, 200, 255), b_type="needle")
        
        elif self.type == "vortex":
            # 漩涡：缓慢螺旋+吸取
            self.rect.y += self.speed
            self.rect.x = WIDTH // 2 + math.sin(t * 1.5) * 100
            # 定时释放能量波
            if self.timer % 70 == 0:
                for i in range(6):
                    angle = i * 60
                    rad = math.radians(angle)
                    vx = math.cos(rad) * 2
                    vy = math.sin(rad) * 2 + 1.5
                    Bullet(self.rect.centerx, self.rect.centery, vx=vx, vy=vy, is_enemy=True, color=(100, 255, 100), b_type="needle")
                # 同时吸取其他敌人
                for other in mobs:
                    if other != self and isinstance(other, Enemy):
                        dist = math.hypot(other.rect.centerx - self.rect.centerx, 
                                        other.rect.centery - self.rect.centery)
                        if dist < 120:
                            dx = self.rect.centerx - other.rect.centerx
                            dy = self.rect.centery - other.rect.centery
                            other.rect.x += (dx / dist) * 0.8 if dist > 0 else 0
                            other.rect.y += (dy / dist) * 0.8 if dist > 0 else 0
        else:
            # 默认直线下移
            self.rect.y += self.speed
            
        if self.rect.top > HEIGHT: self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self, boss_type=None):
        super().__init__()
        # 确保只在 boss 不存在时添加
        boss_types = list(BOSS_DB.keys())
        self.type = boss_type if boss_type in boss_types else random.choice(boss_types)
        data = BOSS_DB[self.type]
        self.data = data
        self.name = data["name"]
        color = data["color"]
        self.visual = data.get('visual', None)
        
        # 使用 utils 中的绘图函数
        self.image = get_boss_surf(self.type, color, data.get('visual', None))
        self.rect = self.image.get_rect(midbottom=(WIDTH/2, -50))
        
        self.hp = 5000 # 基础血量
        self.max_hp = self.hp
        self.health = self.hp  # 别名兼容性
        self.speed_base = 2.0  # Boss移动基础速度
        self.fire_rate_mult = 1.0  # 射速倍数（越小越快）
        # phases: loaded from data config and sorted so higher thresholds trigger first
        raw_phases = data.get('phases', [])
        self.phase_configs = sorted(raw_phases, key=lambda p: p.get('threshold', 0), reverse=True) if raw_phases else []
        # Create (threshold, name) pairs for UI and checking. Fall back to default list if none configured.
        self.phases = [(p.get('threshold', 0), f"phase_{i}") for i, p in enumerate(self.phase_configs)] if self.phase_configs else [(0.75, 'phase_1'), (0.5, 'phase_2'), (0.25, 'phase_3')]
        self.phase_index = 0
        self._entered_phases = set()
        self.state = "enter"
        self.enraged = False
        self.shoot_timer = 0
        self.shoot_modifier = 1.0
        self.phase_change_timer = 0
        self.phase_change_magnitude = 0
        self.teleport_timer = 0
        self.angle = 0
        self.start_y = 0
        self._hit_flash_timer = 0  # 被击中时的闪白效果计时器

    def update(self):
        if not self.enraged and self.hp < self.max_hp * 0.5:
            self.enraged = True
            sound_mgr.play("warning")
            # Enrage visual: spawn aura shockwave
            if self.visual and self.visual.get('aura'):
                Particle((self.rect.centerx, self.rect.centery), self.visual.get('aura'), mode='shockwave')
            
        if self.state == "enter":
            self.rect.y += 2
            if self.rect.top > 50:
                self.state = "fight"
                self.start_y = self.rect.y
        elif self.state == "fight":
            self.shoot_timer += 1
            threshold = (30 if self.enraged else 60) * self.shoot_modifier
            
            # 丰富的攻击模式：每个Boss都有独特的多阶段弹幕
            if self.shoot_timer > threshold:
                self.shoot_timer = 0
                if self.type == "carrier":  # 毁灭者级·虚空母舰
                    if self.phase_index == 0:  # 阶段1：散射无人机群
                        for i in range(-3, 4):
                            Bullet(self.rect.centerx + i*30, self.rect.bottom, angle=i*10, is_enemy=True, b_type="drone_swarm")
                    elif self.phase_index == 1:  # 阶段2：密集扇形弹幕
                        for i in range(-4, 5):
                            Bullet(self.rect.centerx, self.rect.bottom, angle=i*12, is_enemy=True)
                    else:  # 阶段3：混合全屏弹幕
                        for i in range(0, 360, 20):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="drone_swarm")
                        
                elif self.type == "fortress":  # 不朽级·钢铁堡垒
                    if self.phase_index == 0:  # 阶段1：激光扫射
                        for i in range(2, WIDTH-50, 150):
                            Bullet(i, self.rect.bottom-20, angle=0, is_enemy=True, b_type="laser_barrage")
                    elif self.phase_index == 1:  # 阶段2：混合激光+等离子
                        for i in range(0, WIDTH, 120):
                            Bullet(i, self.rect.bottom, angle=-10 if i % 2 == 0 else 10, is_enemy=True, b_type="plasma")
                        for i in range(50, WIDTH, 180):
                            Bullet(i, self.rect.bottom-30, angle=0, is_enemy=True, b_type="laser_barrage")
                    else:  # 阶段3：全屏地毯式轰炸
                        for i in range(0, WIDTH, 80):
                            Bullet(i, self.rect.bottom, angle=random.randint(-20, 20), is_enemy=True, b_type="plasma")
                            
                elif self.type == "assassin":  # 幻影级·虚空刺客 - 快速移动 + 幻影攻击
                    if self.phase_index == 0:  # 阶段1：追踪幻影弹
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx + i*40, self.rect.centery, angle=i*15, is_enemy=True, b_type="phantom")
                    elif self.phase_index == 1:  # 阶段2：密集扇形
                        for i in range(-4, 5):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*10, is_enemy=True, b_type="phantom")
                    else:  # 阶段3：环形幻影弹幕
                        for i in range(0, 360, 30):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="phantom")
                            
                elif self.type == "seraphim":  # 审判级·炽天使 - 圣光轰炸
                    if self.phase_index == 0:  # 阶段1：散射圣光
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx + i*50, self.rect.bottom, angle=i*15, is_enemy=True, b_type="holy_light")
                    elif self.phase_index == 1:  # 阶段2：连续圣光射线
                        for i in range(-3, 4):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*12, is_enemy=True, b_type="holy_light")
                    else:  # 阶段3：神圣审判轰炸
                        for i in range(0, 360, 25):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="holy_light")
                            
                elif self.type == "leviathan":  # 深渊巨兽·利维坦 - 触手+虚空尖刺
                    if self.phase_index == 0:  # 阶段1：触手挥击
                        for i in range(-3, 4):
                            Bullet(self.rect.centerx + i*35, self.rect.bottom, angle=i*15, is_enemy=True, b_type="tentacle")
                    elif self.phase_index == 1:  # 阶段2：深渊尖刺
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*18, is_enemy=True, b_type="void_spike")
                    else:  # 阶段3：混合全屏弹幕
                        for i in range(0, 360, 22):
                            b_type = "tentacle" if i % 2 == 0 else "void_spike"
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type=b_type)
                            
                elif self.type == "overlord":  # 蜂群主宰·奥伯龙 - 蜂群弹幕
                    if self.phase_index == 0:  # 阶段1：散射群弹
                        for i in range(-3, 4):
                            Bullet(self.rect.centerx + i*30, self.rect.bottom, angle=i*12, is_enemy=True, b_type="glitch")
                    elif self.phase_index == 1:  # 阶段2：密集环形
                        for i in range(0, 360, 30):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="glitch")
                    else:  # 阶段3：超密集环形
                        for i in range(0, 360, 15):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="glitch")
                            
                elif self.type == "ragnarok":  # 终焉机神·诸神黄昏 - 火焰毁灭
                    if self.phase_index == 0:  # 阶段1：火焰喷射
                        for i in range(-4, 5):
                            Bullet(self.rect.centerx, self.rect.bottom, angle=i*10, is_enemy=True, b_type="flame_burst")
                    elif self.phase_index == 1:  # 阶段2：混合环形
                        for i in range(0, 360, 40):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="flame_burst")
                    else:  # 阶段3：全屏火焰地狱
                        for i in range(0, 360, 18):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="flame_burst")
                            
                elif self.type == "hydra":  # 九头蛇·剧毒领主 - 毒液喷射
                    if self.phase_index == 0:  # 阶段1：散射毒液
                        for i in range(-3, 4):
                            Bullet(self.rect.centerx + i*40, self.rect.bottom, angle=i*12, is_enemy=True, b_type="glitch")
                    elif self.phase_index == 1:  # 阶段2：多向毒液弹幕
                        for i in range(-4, 5):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*10, is_enemy=True, b_type="glitch")
                    else:  # 阶段3：九头混合弹幕
                        for i in range(0, 360, 20):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="glitch")
                            
                elif self.type == "chronos":  # 时之主·克洛诺斯 - 冰冷时间
                    if self.phase_index == 0:  # 阶段1：散射冰晶
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx + i*50, self.rect.bottom, angle=i*15, is_enemy=True, b_type="ice_shard")
                    elif self.phase_index == 1:  # 阶段2：环形冰晶
                        for i in range(0, 360, 36):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="ice_shard")
                    else:  # 阶段3：密集冰晶地狱
                        for i in range(0, 360, 16):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="ice_shard")
                            
                elif self.type == "gazer":  # 深渊凝视者 - 盯视射线
                    if self.phase_index == 0:  # 阶段1：散射激光
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*20, is_enemy=True, b_type="laser_barrage")
                    elif self.phase_index == 1:  # 阶段2：聚焦扇形
                        for i in range(-3, 4):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*15, is_enemy=True, b_type="laser_barrage")
                    else:  # 阶段3：环形激光地狱
                        for i in range(0, 360, 22):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="laser_barrage")
                            
                elif self.type == "lich":  # 赛博巫妖 - 诅咒能量
                    if self.phase_index == 0:  # 阶段1：散射诅咒球
                        for i in range(-3, 4):
                            Bullet(self.rect.centerx + i*35, self.rect.bottom, angle=i*12, is_enemy=True, b_type="glitch")
                    elif self.phase_index == 1:  # 阶段2：混合环形诅咒
                        for i in range(0, 360, 30):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="glitch")
                    else:  # 阶段3：诅咒风暴
                        for i in range(0, 360, 18):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="glitch")
                            
                elif self.type == "tempest":  # 风暴引擎 - 风刃切割
                    if self.phase_index == 0:  # 阶段1：散射风刃
                        for i in range(-3, 4):
                            Bullet(self.rect.centerx + i*40, self.rect.bottom, angle=i*12, is_enemy=True, b_type="blade_wind")
                    elif self.phase_index == 1:  # 阶段2：扇形风刃
                        for i in range(-4, 5):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*10, is_enemy=True, b_type="blade_wind")
                    else:  # 阶段3：暴风切割
                        for i in range(0, 360, 20):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="blade_wind")
                            
                elif self.type == "void_golem":  # 虚空魔像 - 齿轮机械
                    if self.phase_index == 0:  # 阶段1：环形齿轮弹
                        for i in range(0, 360, 30):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="gear")
                        Particle((self.rect.centerx, self.rect.centery), (120,0,180), mode="gear_spin")
                    elif self.phase_index == 1:  # 阶段2：能量波+追踪弹
                        for i in range(-3, 4):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*15, is_enemy=True, b_type="energy")
                        Particle((self.rect.centerx, self.rect.centery), (180,20,220), mode="energy_wave")
                    else:  # 阶段3：多向核心冲击
                        for i in range(0, 360, 18):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="core")
                        Particle((self.rect.centerx, self.rect.centery), (255,80,180), mode="core_burst")
                        
                elif self.type == "abyss_queen":  # 星渊女王 - 星系弹幕
                    if self.phase_index == 0:  # 阶段1：星尘弹+召唤星体
                        for i in range(0, 360, 40):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="star")
                        Particle((self.rect.centerx, self.rect.centery), (180,80,255), mode="star_dust")
                    elif self.phase_index == 1:  # 阶段2：星卫弹幕
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*25, is_enemy=True, b_type="star_guard")
                        Particle((self.rect.centerx, self.rect.centery), (120,60,200), mode="queen_invis")
                    else:  # 阶段3：星爆全屏弹幕
                        for i in range(0, 360, 15):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="star_burst")
                        Particle((self.rect.centerx, self.rect.centery), (255,180,255), mode="star_burst")
                            
                else:
                    # 默认环形弹幕
                    for i in range(0, 360, 45):
                        Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True)
                        
            # 移动逻辑
            self.rect.x = WIDTH/2 - 120 + math.sin(pygame.time.get_ticks()*0.001) * 100
            # Phase check and transition
            cur_frac = self.hp / max(1, self.max_hp)
            # If we have more phases and current HP is below next threshold, enter next phase
            if self.phase_index < len(self.phases):
                thresh, name = self.phases[self.phase_index]
                if cur_frac <= thresh:
                    self.enter_phase(self.phase_index, name)
                    self.phase_index += 1
            # Enraged visual intensification
            if self.enraged and self.visual and self.visual.get('aura'):
                if pygame.time.get_ticks() % 60 == 0:
                    Particle((self.rect.centerx + random.randint(-40, 40), self.rect.centery + random.randint(-40, 40)), self.visual.get('aura'), mode='spark')

    def enter_phase(self, idx, name):
        """Called when entering a new phase; spawn effects and change behavior."""
        if idx in self._entered_phases:
            return
        self._entered_phases.add(idx)
        # visual effect
        if self.visual and self.visual.get('aura'):
            Particle((self.rect.centerx, self.rect.centery), self.visual.get('aura'), mode='pulse')
        # set phase flash timer for UI/shake and play sound
        self.phase_change_timer = 120
        self.phase_change_magnitude = 8 + idx * 4
        try:
            sound_mgr.play('warning')
        except Exception:
            pass
        # Use sorted phase configs if present
        phase_cfg = None
        if hasattr(self, 'phase_configs') and idx < len(self.phase_configs):
            phase_cfg = self.phase_configs[idx]
        if phase_cfg:
            # spawn
            spawn_cfg = phase_cfg.get('spawn')
            if spawn_cfg:
                btype = spawn_cfg.get('type')
                cnt = spawn_cfg.get('count', 1)
                for i in range(cnt):
                    Enemy(btype)
                    Particle((self.rect.centerx + random.randint(-80, 80), self.rect.centery + random.randint(20, 80)), self.visual.get('core_color', CYAN) if self.visual else CYBER_AMBER, mode='star')
            # effect
            eff = phase_cfg.get('effect')
            if eff:
                eff_type = eff.get('type')
                eff_count = eff.get('count', 3)
                for i in range(eff_count):
                    if eff_type == 'wind_gusts':
                        Particle((self.rect.centerx + random.randint(-100, 100), self.rect.centery + random.randint(-20, 20)), WIND_BLUE, mode='pulse')
                    elif eff_type == 'storm_burst':
                        Particle((self.rect.centerx + random.randint(-80, 80), self.rect.centery + random.randint(-40, 40)), WIND_BLUE, mode='bloom')
                    elif eff_type == 'teleport_dash':
                        # small visual and reposition
                        Particle((self.rect.centerx, self.rect.centery), MAGENTA, mode='star')
                        self.rect.x = random.randint(100, WIDTH-100)
            # fire rate change
            if 'fire_rate_mult' in phase_cfg:
                # Set modifier directly (don't stack multiplicatively across phases)
                self.shoot_modifier = phase_cfg.get('fire_rate_mult', self.shoot_modifier)
        else:
            if self.type == 'carrier':
                # Spawn small drones
                for i in range(3 + idx):
                    Enemy('drone')
                    Particle((self.rect.centerx + random.randint(-80, 80), self.rect.centery + random.randint(20, 80)), CYBER_RED_ALERT, mode='star')
            elif self.type == 'fortress':
                # Turret barrage: spawn short-lived turrets (sniper type) at side
                for x in range(100, WIDTH-100, 200):
                    Enemy('sniper')
                    Particle((x, self.rect.bottom + 10), GOLD, mode='bloom')
            elif self.type == 'tempest':
                # Wind gusts: strong slow pulses
                for i in range(5 + idx*2):
                    Particle((self.rect.centerx + random.randint(-100, 100), self.rect.centery + random.randint(-20, 20)), WIND_BLUE, mode='pulse')
            else:
                # Default: slightly increase firing cadence by reducing shoot_timer
                self.shoot_timer = max(0, self.shoot_timer - 20)

class Player(pygame.sprite.Sprite):
    def __init__(self, plane_id="striker"):
        super().__init__()
        self.plane_id = plane_id
        self.plane_data = PLANES[plane_id]
        
        # 绘制机体
        self.visual = self.plane_data.get('visual', None)
        if not self.visual:
            # Provide sensible defaults
            self.visual = {
                'neon_color': self.plane_data.get('color', CYAN),
                'accent_color': WHITE,
                'trail_color': self.plane_data.get('color', CYAN),
                'ability': None
            }
        self.image = get_plane_surf(plane_id, self.visual)
        # 缩小一点适配游戏
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect(center=(WIDTH/2, HEIGHT-100))
        
        self.speed = self.plane_data["speed"]
        self.max_hp = self.plane_data["hp"]
        self.hp = self.max_hp
        self.damage = self.plane_data["damage"]
        self.shoot_delay = self.plane_data["delay"]
        
        # 属性
        self.xp = 0
        self.next_level_xp = 100
        self.level = 1
        self.bullet_count = 1
        self.piercing = 0
        self.homing_level = 0
        self.bounce_level = 0
        self.crit_chance = 0.05
        self.crit_mult = 2.0
        self.max_shield = 0
        self.shield = 0
        self.max_dash_energy = 100
        self.dash_energy = 100
        self.is_dashing = False
        self.ult_charge = 0
        self.max_ult_charge = 300
        self.ult_cooldown = 0  # 【新】大招冷却计时器
        self.ult_max_cooldown = 60  # 【新】大招冷却时间：1秒(60帧)
        self.last_shot = 0
        self.damage_reduction = 0.0
        
        self.weapon_slots = []
        for w_data in arsenal_save_data["loadout"]:
            if w_data: self.weapon_slots.append(WeaponSystem(w_data))
            else: self.weapon_slots.append(None)
        self.current_slot = 0
        self.switch_cooldown = 0
        
        # ========== 【新增】僚机编队系统 ==========
        self.wingman_squadron = None  # 将在 main.py 中延迟初始化
        self.max_wingmen = 4  # 最多僚机数量
        self.wingman_count = 0  # 当前僚机数量
        
        self.drones = [] # 保留用于兼容性
        self.skill_cd = 0
        self.max_skill_cd = 300
        self.trail_pos = []
        self.overdrive_timer = 0
        
        # ========== 肉鸽系统初始化 ==========
        # 延迟导入以避免循环引用（在 update 中或 main.py 中初始化）
        self.upgrade_manager = None
        self.exp_system = None
        self.buff_processor = None
        
        # 肉鸽相关属性初始化
        self.pickup_range = 150  # 拾取范围
        self.execute_threshold = 0.2  # 斩杀血线阈值
        self.drone_count = 0  # 僚机数量
        self.bullet_speed_mult = 1.0  # 子弹速度倍率
        self.explosion_mult = 1.0  # 爆炸倍率
        self.boss_damage_mult = 1.0  # Boss伤害倍率
        self.cooldown_reduction = 0.0  # 冷却缩减
        
        # 被动效果标志
        self.has_regen = False  # 纳米再生
        self.has_frost = False  # 冰霜新星
        self.has_lightning = False  # 雷神之锤
        self.has_corpse_explosion = False  # 裂变反应
        
        # 【新增】肉鸽增益卡牌跟踪列表
        self.buffs = []  # 存储已应用的卡牌ID列表
        self.has_vampire = False  # 吸血鬼
        self.has_area_dmg = False  # 聚能爆破
        self.has_blackhole = False  # 奇点发生器
        self.has_freeze_burn = False  # 寒冰灼烧
        self.has_energy_siphon = False  # 能量虹吸
        self.has_blood_pact = False  # 鲜血契约

    def update(self):
        # 拖尾记录
        if len(self.trail_pos) > 10: self.trail_pos.pop(0)
        self.trail_pos.append(self.rect.center)
        
        # 能量回复 - 不在冲刺时回复（更快回复）
        if not self.is_dashing:
            if self.dash_energy < self.max_dash_energy:
                self.dash_energy = min(self.max_dash_energy, self.dash_energy + 1.5)  # 提高回复速度到1.5/帧
        
        if self.skill_cd > 0: self.skill_cd -= 1
        # 【新】大招冷却更新
        if self.ult_cooldown > 0: self.ult_cooldown -= 1
        
        # 武器更新
        if self.switch_cooldown > 0: self.switch_cooldown -= 1
        for w in self.weapon_slots:
            if w: w.update()

        # 移动逻辑 (WASD + Arrows) - 改进版支持流畅对角线移动
        keys = pygame.key.get_pressed()
        dx, dy = 0.0, 0.0
        
        # 累加所有按下的移动键（支持对角线）
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += self.speed
        
        # 对角线移动标准化（避免对角线速度过快）
        if dx != 0 and dy != 0:
            move_length = math.sqrt(dx*dx + dy*dy)
            dx = dx / move_length * self.speed
            dy = dy / move_length * self.speed
        
        # 冲刺
        # Overdrive temporary buff handling
        if self.overdrive_timer > 0:
            self.overdrive_timer -= 1
            if self.overdrive_timer == 0:
                # Reset damage when overdrive ends
                self.damage = self.plane_data['damage']
        
        # 冲刺条件：需要足够的能量（>=80/100）且有移动方向
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.dash_energy >= 80 and (dx!=0 or dy!=0):
            self.is_dashing = True
            self.dash_energy = max(0, self.dash_energy - 2)  # 扣除能量
            dx *= 2.0; dy *= 2.0
        else:
            self.is_dashing = False
            
        self.rect.x += dx
        self.rect.y += dy
        
        # 边界限制
        self.rect.clamp_ip(screen_rect)

        # 切换武器
        if self.switch_cooldown <= 0:
            if keys[pygame.K_q]:
                self.current_slot = (self.current_slot - 1) % 3
                self.switch_cooldown = 60
                sound_mgr.play("select")
            elif keys[pygame.K_e]:
                self.current_slot = (self.current_slot + 1) % 3
                self.switch_cooldown = 60
                sound_mgr.play("select")

    def shoot(self):
        now = pygame.time.get_ticks()
        
        # 1. 主炮射击 (保持不变)
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self._fire_main_gun()
            sound_mgr.play("shoot")
            
        # 【改动】副武器现在由僚机使用，玩家只使用主武器
        # 副武器逻辑已转移到 wingman.py 中的 Wingman 类

    def _fire_main_gun(self):
        """根据机体ID释放不同的射击模式"""
        pid = self.plane_id
        color = self.plane_data["color"]
        b_type = self.plane_data["bullet_type"]
        cnt = self.bullet_count
        
        # ========== 1. 霓虹突击者 - 直线扇形射击 ==========
        if pid == "striker":
            # 中间直射 + 两侧略微散开
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 15
                angle = -5 + i * 5 if cnt > 1 else 0
                Bullet(self.rect.centerx + offset_x, self.rect.top, angle=angle, 
                       color=color, b_type=b_type, piercing=self.piercing, homing=self.homing_level)
        
        # ========== 2. 虚空幻影 - 快速多枚散射 ==========
        elif pid == "phantom":
            # 高射速特性：发射更多细小子弹
            for i in range(cnt * 2):
                spread = (i - cnt + 0.5) * 8
                angle = random.uniform(-15, 15)
                Bullet(self.rect.centerx + spread, self.rect.top, angle=angle,
                       color=color, b_type=b_type, piercing=self.piercing//2 if self.piercing else 0)
        
        # ========== 3. 钢铁泰坦 - 慢速但强力的集中炮火 ==========
        elif pid == "titan":
            # 低射速、高威力：发射强力火箭
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 25
                Bullet(self.rect.centerx + offset_x, self.rect.top, 
                       color=color, b_type=b_type, piercing=self.piercing + 2, homing=self.homing_level)
        
        # ========== 4. 极光女神 - 范围电浆波 ==========
        elif pid == "aurora":
            # 范围型：发射扇形波纹攻击
            for i in range(cnt + 2):
                angle = -30 + i * (60 / (cnt + 1))
                Bullet(self.rect.centerx, self.rect.top, angle=angle,
                       color=color, b_type="wave", piercing=self.piercing)
        
        # ========== 5. 幽灵收割者 - 单发极高伤害 ==========
        elif pid == "specter":
            # 射速极慢但单发超高伤害
            if cnt > 0:  # 应该是1
                Bullet(self.rect.centerx, self.rect.top,
                       color=color, b_type=b_type, piercing=self.piercing + 5, homing=self.homing_level)
        
        # ========== 6. 雷霆战鹰 - 多段连锁闪电 ==========
        elif pid == "thunderbird":
            # 发射闪电链：多个连接的闪电
            spacing = 20
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * spacing
                Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=color, b_type="lightning", piercing=self.piercing)
        
        # ========== 7. 剧毒蝰蛇 - 持续毒液喷射 ==========
        elif pid == "viper":
            # 连续喷射：在一定范围内发射多枚毒液
            for i in range(cnt + 1):
                spread = (i - cnt/2) * 12
                angle = random.uniform(-20, 20)
                Bullet(self.rect.centerx + spread, self.rect.top, angle=angle,
                       color=color, b_type="acid", piercing=self.piercing)
        
        # ========== 8. 绯红之刃 - 高频旋转飞刃 ==========
        elif pid == "crimson":
            # 高射速特性：发射旋转的飞刃
            time_factor = pygame.time.get_ticks() / 100  # 时间因子实现旋转效果
            for i in range(cnt * 2):
                angle = (time_factor + i * (360 / (cnt * 2))) % 360
                Bullet(self.rect.centerx, self.rect.top, angle=angle,
                       color=color, b_type="blade", piercing=self.piercing)
        
        # ========== 9. 星界潜行者 - 追踪星镖 ==========
        elif pid == "stalker":
            # 追踪特性：发射自动追踪的星镖
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 20
                Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=color, b_type="star", piercing=self.piercing, 
                       homing=self.homing_level + 1)  # 加强追踪
        
        # ========== 10. 大地守护者 - 散射荆棘 ==========
        elif pid == "gaia":
            # 散射特性：发射向下散开的荆棘
            for i in range(cnt + 3):
                angle = -40 + i * (80 / (cnt + 2))
                Bullet(self.rect.centerx, self.rect.top, angle=angle,
                       color=color, b_type="thorn", piercing=self.piercing)
        
        # ========== 11. 虚空编织者 - 蛛网束缚 ==========
        elif pid == "weaver":
            # 控制特性：发射粘稠的蛛网
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 20
                # 蛛网子弹速度较慢
                bullet = Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=color, b_type="web", piercing=self.piercing)
                bullet.speed = -8  # 减速
        
        # ========== 12. 日冕耀斑 - 高频火焰喷流 ==========
        elif pid == "solar":
            # 极高射速：发射连续的火焰
            for i in range(cnt * 3):  # 射速高意味着更多子弹
                spread = (i - cnt + 0.5) * 6
                angle = random.uniform(-12, 12)
                Bullet(self.rect.centerx + spread, self.rect.top, angle=angle,
                       color=color, b_type="flame", piercing=self.piercing//2 if self.piercing else 0)
        
        # ========== 13. 量子裁决者 - 分裂量子块 ==========
        elif pid == "arbiter":
            # 分裂特性：发射会分裂的量子块
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 18
                Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=color, b_type="quant", piercing=self.piercing)
        
        # ========== 14. 日食幽灵 - 双核心双线射击 ==========
        elif pid == "eclipse":
            # 双核心特性：同时从两个点发射
            left_x = self.rect.centerx - 15
            right_x = self.rect.centerx + 15
            for i in range(cnt):
                offset = (i - (cnt-1)/2) * 10
                # 左核心
                Bullet(left_x + offset, self.rect.top, 
                       color=color, b_type="shadow", piercing=self.piercing, angle=-5)
                # 右核心
                Bullet(right_x + offset, self.rect.top,
                       color=color, b_type="shadow", piercing=self.piercing, angle=5)
        
        # ========== 15. 棱镜分光 - 一发三道分裂 ==========
        elif pid == "prism":
            # 分裂特性：每发子弹发射后会分裂成三道
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 16
                # 中间直射
                Bullet(self.rect.centerx + offset_x, self.rect.top, angle=0,
                       color=(100, 180, 255), b_type="refract", piercing=self.piercing)
                # 左侧散射
                Bullet(self.rect.centerx + offset_x, self.rect.top, angle=-25,
                       color=(255, 100, 100), b_type="refract", piercing=self.piercing//2)
                # 右侧散射
                Bullet(self.rect.centerx + offset_x, self.rect.top, angle=25,
                       color=(100, 255, 100), b_type="refract", piercing=self.piercing//2)
        
        # ========== 16. 死灵骑士 - 吸血射击 ==========
        elif pid == "necro":
            # 吸血特性：普通伤害转化为吸收
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 18
                Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=color, b_type="spectral", piercing=self.piercing)
        
        # 默认情况
        else:
            cnt = self.bullet_count
            start_x = self.rect.centerx - (cnt-1)*10
            for i in range(cnt):
                Bullet(start_x + i*20, self.rect.top, color=color, b_type=b_type, 
                       piercing=self.piercing, homing=self.homing_level)

    def use_ultimate(self):
        # 【新】冷却检查
        if self.ult_cooldown > 0:
            return  # 冷却中，无法释放
        
        if self.ult_charge >= 100:
            self.ult_charge -= 100
            # 【新】设置冷却计时
            self.ult_cooldown = self.ult_max_cooldown
            
            name = self.plane_data["ult_name"]
            FloatingText(self.rect.centerx, self.rect.top - 50, f"★ {name} ★", self.plane_data["color"])
            sound_mgr.play("nuke")
            
            # 根据机体ID释放不同大招
            pid = self.plane_id
            
            # ========== 原有机体 ==========
            if pid == "striker":
                FinalBeam(self)
            elif pid == "phantom": 
                # 时空冻结：冻结所有敌人和子弹3秒
                global global_time_freeze
                global_time_freeze = 180
                for m in mobs:
                    TimeSlash(m.rect.center)
                for eb in enemy_bullets:
                    eb.frozen = True
            elif pid == "titan":
                NukeExplosion()
            elif pid == "aurora":
                AuroraCurtain()
            elif pid == "specter":
                DeathScythe(self.rect.center)
            elif pid == "void":
                BlackHole((WIDTH/2, HEIGHT/2))
            
            # ========== 新增机体大招 ==========
            elif pid == "thunderbird":
                # 雷神降世：链式闪电击中所有敌人
                for m in list(mobs):
                    for _ in range(3):
                        Bullet(m.rect.centerx, m.rect.centery, is_enemy=False, color=YELLOW, b_type="lightning")
                    m.hp -= 200
                    Particle(m.rect.center, YELLOW)
                    # 链式传导
                    for m2 in list(mobs):
                        if m != m2 and abs(m.rect.centerx - m2.rect.centerx) < 200:
                            for _ in range(2):
                                Particle(m2.rect.center, (200, 150, 50))
                            m2.hp -= 50
            
            elif pid == "viper":
                # 腐蚀毒雾：全屏毒气伤害
                for m in list(mobs):
                    m.hp -= 150
                    # 持续毒伤标记
                    m.poison_timer = 180  # 3秒持续伤害
                    Particle(m.rect.center, LIME)
            
            elif pid == "crimson":
                # 鲜血新月：释放扇形刀刃
                for angle in range(-45, 46, 15):
                    Bullet(self.rect.centerx, self.rect.centery, angle=angle, is_enemy=False, 
                          color=CRIMSON, b_type="blade", piercing=5)
            
            elif pid == "stalker":
                # 群星坠落：发射追踪星镖群
                for angle in range(0, 360, 30):
                    Bullet(self.rect.centerx, self.rect.centery, angle=angle, is_enemy=False, 
                          color=INDIGO, b_type="star", homing=3, piercing=3)
            
            elif pid == "gaia":
                # 自然之怒：释放分散荆棘
                for angle in range(0, 360, 45):
                    Bullet(self.rect.centerx, self.rect.centery, angle=angle, is_enemy=False, 
                          color=FOREST, b_type="thorn", piercing=5)
                # 伤害所有敌人
                for m in mobs:
                    m.hp -= 100
                    Particle(m.rect.center, FOREST)
            
            elif pid == "weaver":
                # 维度陷阱：放置减速蛛网
                for m in list(mobs):
                    m.hp -= 80
                    m.frozen_timer = 120  # 冻结2秒
                    Particle(m.rect.center, WEB_GRAY)
            
            elif pid == "solar":
                # 超新星爆发：范围火焰爆炸
                cx, cy = WIDTH/2, HEIGHT/2
                for angle in range(0, 360, 30):
                    rad = math.radians(angle)
                    for dist in range(50, 300, 50):
                        px = cx + math.cos(rad) * dist
                        py = cy + math.sin(rad) * dist
                        Particle((px, py), BRIGHT_ORANGE)
                # 伤害范围内敌人
                for m in list(mobs):
                    dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
                    if dist < 300:
                        m.hp -= 180
            
            elif pid == "arbiter":
                # 矩阵重置：生成爆炸量子块
                for i in range(12):
                    angle = i * 30
                    Bullet(self.rect.centerx, self.rect.centery, angle=angle, is_enemy=False, 
                          color=NEON_PURPLE, b_type="quant", piercing=3)
                # 屏幕闪烁效果
                for m in mobs:
                    m.hp -= 120
            
            elif pid == "eclipse":
                # 黑日降临：双核吸收光束
                for offset in [-20, 20]:
                    for i in range(8):
                        angle = i * 45
                        Bullet(self.rect.centerx + offset, self.rect.centery, angle=angle, is_enemy=False,
                              color=(100, 50, 180), b_type="shadow", piercing=4)
                # 吸收伤害转为护盾
                for m in list(mobs):
                    dmg = 140
                    m.hp -= dmg
                    self.shield = min(self.max_shield + 100, self.shield + dmg // 2)
                    Particle(m.rect.center, (100, 50, 180))
            
            elif pid == "prism":
                # 光谱爆裂：多向分光射线
                for angle in range(0, 360, 30):
                    for split_angle in [-15, 0, 15]:
                        Bullet(self.rect.centerx, self.rect.centery, angle=angle + split_angle, is_enemy=False,
                              color=(100, 180, 255), b_type="prism", piercing=2)
                # 范围伤害
                for m in list(mobs):
                    dist = math.hypot(m.rect.centerx - self.rect.centerx, m.rect.centery - self.rect.centery)
                    if dist < 250:
                        m.hp -= 110
                        Particle(m.rect.center, (0, 255, 200))
            
            elif pid == "necro":
                # 亡灵收割：扩散吸血光线
                for angle in range(0, 360, 45):
                    Bullet(self.rect.centerx, self.rect.centery, angle=angle, is_enemy=False,
                          color=(200, 50, 150), b_type="spectral", piercing=6, homing=2)
                # 每次伤害都转为治疗
                for m in list(mobs):
                    dmg = 130
                    m.hp -= dmg
                    self.hp = min(self.max_hp, self.hp + dmg // 3)
                    FloatingText(self.rect.centerx, self.rect.centery - 30, f"+{dmg//3} HP", LIME)
                    Particle(m.rect.center, (200, 50, 150))
            
            else:
                # 通用：全屏清弹 + 通用爆炸
                enemy_bullets.empty()
                NukeExplosion()
            
            # ========== 特殊能力触发 ==========
            if getattr(self, 'visual', None):
                ability = self.visual.get('ability')
                if ability == 'overdrive':
                    FinalBeam(self)
                    self.damage = int(self.damage * 1.3)
                    self.overdrive_timer = 600
                elif ability == 'phase_shift':
                    for i in range(3):
                        Particle(self.rect.center, self.visual.get('neon_color', MAGENTA), mode='spark')
                    self.rect.y = max(50, self.rect.y - 160)
                elif ability == 'armor_plating':
                    Particle(self.rect.center, self.visual.get('neon_color', CYBER_AMBER), mode='shockwave')
                    self.shield = self.max_shield + 50
                elif ability == 'area_field':
                    for angle in range(0, 360, 60):
                        Particle(self.rect.center, TEAL, mode='shockwave')

    def draw_trail(self, surf):
        if len(self.trail_pos) > 2:
            trail_color = self.visual.get('trail_color') if getattr(self, 'visual', None) else self.plane_data["color"]
            pygame.draw.lines(surf, trail_color, False, self.trail_pos, 2)
            
    def draw_auras(self, surf):
        # 护盾光环 - 透明效果，更大
        if self.shield > 0:
            shield_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (*SHIELD_BLUE, 100), (60, 60), 55, 2)
            surf.blit(shield_surf, (self.rect.centerx - 60, self.rect.centery - 60), special_flags=pygame.BLEND_ALPHA_SDL2)
            
        # 武器冷却条
        active_w = self.weapon_slots[self.current_slot]
        if active_w:
            bar_w = 40; bar_h = 3
            bx = self.rect.centerx - bar_w // 2; by = self.rect.bottom + 5
            pct = 0; c = WHITE
            
            if active_w.type == "cannon": pct = 1.0 - (active_w.heat / active_w.max_heat); c = RED
            elif active_w.type == "beam": pct = active_w.energy / active_w.max_energy; c = CYAN
            elif active_w.reload_timer > 0: pct = 1.0 - (active_w.reload_timer / active_w.cooldown_max); c = GRAY
            else: pct = 1.0; c = GREEN
            
            pygame.draw.rect(surf, (50,50,50), (bx, by, bar_w, bar_h))
            if pct > 0: pygame.draw.rect(surf, c, (bx, by, int(bar_w*pct), bar_h))

    def _fire_sub_weapon(self, w):
        # 从 weapon 对象获取参数
        w_type = w.type
        color = w.stats['color']
        h_lvl = self.homing_level
        x, y = self.rect.centerx, self.rect.top

        # 计算追踪等级加成
        if w_type == "missile": h_lvl += 5
        elif w_type == "arc": h_lvl += 3
        elif w_type == "swarm": h_lvl += 8

        # --- 发射逻辑移植 ---
        if w_type == "cannon":
            Bullet(x, y, color=color, b_type="needle", homing=h_lvl)
            sound_mgr.play("shoot")
        elif w_type == "beam":
            Bullet(x, y, color=color, b_type="beam", homing=h_lvl)
        elif w_type == "explosive":
            b = Bullet(x, y, color=color, b_type="plasma", homing=h_lvl)
            b.speed = -6
        elif w_type == "missile":
            Bullet(x, y, homing=h_lvl, color=color, b_type="rocket")
            sound_mgr.play("shoot")
        elif w_type == "exotic":
            for i in range(0, 360, 45): 
                Bullet(x, y, angle=i, color=color, b_type="star", homing=h_lvl)
            sound_mgr.play("zap")
        elif w_type == "scatter":
            sound_mgr.play("shoot")
            for i in range(-2, 3):
                b = Bullet(x, y, angle=i*10, color=color, b_type="shard", homing=h_lvl)
                b.speed = -10
        elif w_type == "arc":
            sound_mgr.play("zap")
            Bullet(x, y, homing=h_lvl, color=color, b_type="lightning")
        elif w_type == "sniper":
            sound_mgr.play("sniper_charge")
            b = Bullet(x, y, color=color, b_type="needle", piercing=999, homing=h_lvl)
            b.speed = -25
            # 特效需要引用 Particle，确保已导入
            Particle((x, y), color, mode="shockwave")
        elif w_type == "blade":
            sound_mgr.play("shoot")
            b = Bullet(x, y, color=color, b_type="blade", homing=h_lvl)
            b.speed = -8
            b.piercing = 5
            b.bounce = 1
        elif w_type == "railgun":
            sound_mgr.play("laser")
            Particle((x, y), color, mode="shockwave")
            b = Bullet(x, y, color=color, b_type="beam", piercing=999)
            b.speed = -40
        elif w_type == "void":
            b = Bullet(x, y, color=color, b_type="orb", piercing=10)
            b.speed = -3
            sound_mgr.play("blackhole")
        elif w_type == "frost":
            Bullet(x, y, color=color, b_type="shard", homing=h_lvl)
            sound_mgr.play("shoot")
        elif w_type == "swarm":
            sound_mgr.play("shoot")
            for i in range(8):
                angle = random.randint(-45, 45)
                b = Bullet(x, y, angle=angle, color=color, b_type="rocket", homing=h_lvl)
                b.speed = -7
    
    # ========== 肉鸽系统方法 ==========
    def init_roguelite_systems(self):
        """初始化肉鸽系统（在 main.py 中调用）"""
        try:
            from roguelite import UpgradeManager, ExperienceSystem, BuffProcessor, ItemManager, AchievementManager
            from systems import EffectManager
            
            self.upgrade_manager = UpgradeManager()
            self.exp_system = ExperienceSystem(self)
            self.buff_processor = BuffProcessor(self)
            self.item_manager = ItemManager()
            self.achievement_manager = AchievementManager()
            self.effect_manager = EffectManager()
        except ImportError as e:
            log_error(f"Failed to import roguelite module: {e}")
            # In case of import error, still try to recover gracefully
            return
        # Always set player reference in the upgrade manager
        try:
            if self.upgrade_manager:
                self.upgrade_manager.set_player_ref(self)
        except Exception:
            log_error("Failed to set player ref in upgrade_manager")
    
    def add_xp(self, amount):
        """增加经验值，可能触发升级"""
        if not self.exp_system:
            return self.level
        
        new_level = self.exp_system.add_xp(amount)
        
        # 同步 Player 的 xp 和 next_level_xp 属性
        self.xp = self.exp_system.xp_collected
        self.next_level_xp = self.exp_system.next_level_xp
        
        # 如果升级，触发升级选择 UI
        if new_level > self.level:
            self.level = new_level
            sound_mgr.play("levelup")
            return new_level
        
        return self.level
    
    def apply_buff(self, buff_id):
        """应用指定增益到玩家"""
        try:
            from roguelite import apply_buff_to_player
            return apply_buff_to_player(self, buff_id)
        except Exception as e:
            log_error(f"Failed to apply buff {buff_id}: {e}")
            return False
    
    def heal(self, amount):
        """回复生命值"""
        self.hp = min(self.hp + amount, self.max_hp)
        if amount > 0:
            FloatingText(self.rect.centerx, self.rect.centery, f"+{int(amount)}", LIME)
        return self.hp
    
    def take_damage(self, amount):
        """受到伤害，考虑护盾和装甲"""
        # 装甲减伤
        reduced = amount * (1 - self.damage_reduction)
        
        # 先扣护盾
        if self.shield > 0:
            shield_absorb = min(self.shield, reduced)
            self.shield -= shield_absorb
            reduced -= shield_absorb
        
        # 再扣生命
        self.hp -= reduced
        
        if reduced > 0:
            DamageNumber(self.rect.centerx, self.rect.centery, int(reduced), is_crit=False)
        
        return max(0, self.hp)
    
    def update_buffs(self):
        """每帧更新肉鸽系统的被动效果"""
        if self.buff_processor:
            self.buff_processor.update(dt=1)
    
    def on_kill_enemy(self, enemy):
        """击杀敌人时触发肉鸽效果"""
        if self.buff_processor:
            corpse_effect = self.buff_processor.on_kill_enemy(enemy)
            if corpse_effect and corpse_effect["type"] == "corpse_explosion":
                # 返回爆炸信息，由 main.py 处理
                return corpse_effect
        return None
    
    def on_buff_received(self, buff_id, buff_data):
        """接收增益时的钩子（可用于显示通知）"""
        color = RARITY_COLORS[buff_data["rarity"]]
        FloatingText(self.rect.centerx, self.rect.top - 30, f"✦ {buff_data['name']}", color)