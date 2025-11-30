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
    def __init__(self, x, y, angle=0, is_enemy=False, piercing=0, color=YELLOW, homing=0, bounce=0, b_type="beam", bullet_theme=None):
        super().__init__()
        self.is_enemy = is_enemy
        self.piercing = piercing
        self.homing = homing
        self.bounce = bounce
        self.color = color
        self.b_type = b_type
        self.timer = 0
        self.frozen = False  # 【新】时间冻结标记
        self.bullet_theme = bullet_theme  # 【新】子弹涂装主题
        
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
            
            # =============================================================================
            # 【子弹涂装系统】根据装备的涂装主题绘制子弹
            # =============================================================================
            
            # 如果有涂装主题，使用涂装绘制；否则使用默认绘制
            if bullet_theme and bullet_theme.get("effects"):
                self._create_themed_bullet(bullet_theme)
            elif b_type == "beam":  # 1. Striker - 霓虹突击者（青色激光束）
                self.image = pygame.Surface((14, 34), pygame.SRCALPHA)
                pygame.draw.rect(self.image, CYAN, (4, 0, 6, 34))
                pygame.draw.rect(self.image, CYBER_CYAN_BRIGHT, (3, 0, 8, 34), 2)
                pygame.draw.rect(self.image, WHITE, (5, 10, 4, 16))
                pygame.draw.circle(self.image, WHITE, (7, 6), 3)
                self.speed = -15
                
            elif b_type == "shard":  # 2. Phantom - 虚空幻影（洋红菱形碎片）
                self.image = pygame.Surface((16, 30), pygame.SRCALPHA)
                pygame.draw.polygon(self.image, MAGENTA, [(8,0), (16,15), (8,30), (0,15)])
                pygame.draw.polygon(self.image, WHITE, [(8,0), (16,15), (8,30), (0,15)], 2)
                pygame.draw.polygon(self.image, CYBER_CYAN_BRIGHT, [(8,6), (12,15), (8,24), (4,15)])
                self.speed = -18
                self.piercing = max(1, self.piercing)
                
            elif b_type == "rocket":  # 3. Titan - 钢铁泰坦（橙色重型火箭）
                self.image = pygame.Surface((20, 38), pygame.SRCALPHA)
                pygame.draw.rect(self.image, ORANGE, (4, 12, 12, 22))
                pygame.draw.rect(self.image, CYBER_AMBER, (3, 12, 14, 22), 3)
                pygame.draw.polygon(self.image, CYBER_AMBER, [(4,12), (10,0), (16,12)])
                pygame.draw.rect(self.image, (255, 80, 0), (6, 34, 8, 4))
                pygame.draw.circle(self.image, WHITE, (10, 22), 4)
                self.speed = -10
                
            elif b_type == "lightning":  # 4. Thunderbird - 雷霆战鹰（黄色闪电链）
                self.image = pygame.Surface((18, 40), pygame.SRCALPHA)
                points = [(9,0), (4,14), (14,26), (9,40)]
                pygame.draw.lines(self.image, YELLOW, False, points, 4)
                pygame.draw.lines(self.image, WHITE, False, points, 2)
                pygame.draw.line(self.image, YELLOW, (4,14), (0,18), 2)
                pygame.draw.line(self.image, YELLOW, (14,26), (18,30), 2)
                self.speed = -16
                
            elif b_type == "acid":  # 5. Viper - 剧毒蝰蛇（绿色毒液滴）
                self.image = pygame.Surface((26, 34), pygame.SRCALPHA)
                # 毒液主体（水滴形）
                pygame.draw.ellipse(self.image, (50, 255, 50), (3, 0, 20, 28))
                pygame.draw.ellipse(self.image, (100, 255, 100), (3, 0, 20, 28), 3)
                # 滴落尖端
                pygame.draw.polygon(self.image, (50, 255, 50), [(13, 28), (18, 32), (13, 34), (8, 32)])
                # 内部光泽
                pygame.draw.ellipse(self.image, (200, 255, 200), (8, 6, 10, 14))
                pygame.draw.ellipse(self.image, WHITE, (10, 8, 6, 8))
                # 气泡效果
                pygame.draw.circle(self.image, (150, 255, 150), (10, 18), 3)
                pygame.draw.circle(self.image, (150, 255, 150), (16, 15), 2)
                pygame.draw.circle(self.image, (150, 255, 150), (13, 22), 2)
                self.speed = -12
                
            elif b_type == "spectral":  # 6. Specter - 幽灵收割者（紫色幽能箭）
                self.image = pygame.Surface((18, 42), pygame.SRCALPHA)
                points = [(9,0), (5,14), (13,28), (9,42)]
                pygame.draw.lines(self.image, (150, 100, 255), False, points, 5)
                pygame.draw.lines(self.image, (200, 150, 255), False, points, 3)
                pygame.draw.circle(self.image, WHITE, (9, 8), 5)
                pygame.draw.circle(self.image, (180, 130, 255), (9, 24), 4)
                self.speed = -20
                
            elif b_type == "aurora_beam":  # 7. Aurora - 极光女神（青绿波纹光环）
                self.image = pygame.Surface((34, 34), pygame.SRCALPHA)
                # 极光同心圆波纹
                pygame.draw.circle(self.image, (0, 255, 200), (17, 17), 15)
                pygame.draw.circle(self.image, (50, 255, 220), (17, 17), 15, 3)
                pygame.draw.circle(self.image, (100, 255, 230), (17, 17), 11, 2)
                pygame.draw.circle(self.image, (150, 255, 240), (17, 17), 7, 2)
                # 波纹效果（多层同心圆）
                for r in [13, 9, 5]:
                    pygame.draw.circle(self.image, WHITE, (17, 17), r, 1)
                # 中心亮点
                pygame.draw.circle(self.image, WHITE, (17, 17), 4)
                pygame.draw.circle(self.image, (200, 255, 250), (17, 17), 2)
                self.speed = -13
                
            elif b_type == "blade":  # 8. Crimson - 绯红之刃（红色月牙刀光）
                self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.arc(self.image, CRIMSON, (0,0,40,40), 0, 3.14, 5)
                pygame.draw.arc(self.image, (255, 50, 80), (2,2,36,36), 0, 3.14, 4)
                pygame.draw.arc(self.image, WHITE, (6,6,28,28), 0, 3.14, 3)
                pygame.draw.line(self.image, CRIMSON, (0, 20), (40, 20), 3)
                pygame.draw.circle(self.image, WHITE, (20, 20), 5)
                self.speed = -18
                
            elif b_type == "star":  # 9. Stalker - 星界潜行者（靛蓝八芒星）
                self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
                points = [(12,0), (14,8), (24,12), (14,16), (12,24), (10,16), (0,12), (10,8)]
                pygame.draw.polygon(self.image, INDIGO, points)
                pygame.draw.polygon(self.image, (150, 100, 255), points, 2)
                pygame.draw.circle(self.image, WHITE, (12,12), 4)
                pygame.draw.circle(self.image, INDIGO, (12,12), 2)
                self.speed = -14
                
            elif b_type == "thorn":  # 10. Gaia - 大地守护者（绿色荆棘箭）
                self.image = pygame.Surface((16, 32), pygame.SRCALPHA)
                pygame.draw.polygon(self.image, FOREST, [(8,0), (16,14), (8,32), (0,14)])
                pygame.draw.polygon(self.image, CYBER_LIME, [(8,0), (16,14), (8,32), (0,14)], 3)
                pygame.draw.polygon(self.image, (120, 220, 100), [(8,5), (12,14), (8,28), (4,14)])
                for i in [10, 18, 26]:
                    pygame.draw.line(self.image, CYBER_LIME, (8, i), (2, i-4), 2)
                    pygame.draw.line(self.image, CYBER_LIME, (8, i), (14, i-4), 2)
                self.speed = -11
                
            elif b_type == "web":  # 11. Weaver - 虚空编织者（灰色蛛网十字）
                self.image = pygame.Surface((26, 26), pygame.SRCALPHA)
                pygame.draw.line(self.image, (180, 180, 180), (0,13), (26,13), 3)
                pygame.draw.line(self.image, (180, 180, 180), (13,0), (13,26), 3)
                pygame.draw.line(self.image, (220, 220, 220), (4,4), (22,22), 2)
                pygame.draw.line(self.image, (220, 220, 220), (22,4), (4,22), 2)
                pygame.draw.circle(self.image, WHITE, (13, 13), 5)
                pygame.draw.circle(self.image, CYBER_CYAN_BRIGHT, (13, 13), 4, 2)
                self.speed = -9
                
            elif b_type == "flame":  # 12. Solar - 日冕耀斑（橙黄火焰）
                self.image = pygame.Surface((30, 36), pygame.SRCALPHA)
                # 火焰外层（橙红色）
                pygame.draw.ellipse(self.image, (255, 100, 0), (2, 0, 26, 32))
                pygame.draw.ellipse(self.image, (255, 150, 0), (2, 0, 26, 32), 3)
                # 火焰中层（橙色）
                pygame.draw.ellipse(self.image, (255, 180, 50), (6, 4, 18, 24))
                pygame.draw.ellipse(self.image, (255, 200, 100), (6, 4, 18, 24), 2)
                # 火焰内核（黄白色）
                pygame.draw.ellipse(self.image, (255, 230, 150), (10, 8, 10, 16))
                pygame.draw.circle(self.image, WHITE, (15, 14), 4)
                # 火花效果（小火球）
                pygame.draw.circle(self.image, (255, 200, 100), (8, 26), 3)
                pygame.draw.circle(self.image, (255, 200, 100), (22, 24), 3)
                pygame.draw.circle(self.image, (255, 180, 80), (15, 30), 4)
                pygame.draw.circle(self.image, (255, 220, 120), (15, 30), 2)
                self.speed = -17
                
            elif b_type == "quant":  # 13. Arbiter - 量子裁决者（紫色量子方块）
                self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.rect(self.image, NEON_PURPLE, (2,2,16,16))
                pygame.draw.rect(self.image, (180, 100, 255), (2,2,16,16), 3)
                pygame.draw.rect(self.image, WHITE, (6,6,8,8))
                pygame.draw.rect(self.image, MAGENTA, (8,8,4,4))
                pygame.draw.line(self.image, CYBER_CYAN_BRIGHT, (0, 10), (20, 10), 2)
                pygame.draw.line(self.image, CYBER_CYAN_BRIGHT, (10, 0), (10, 20), 2)
                self.speed = -13
                
            elif b_type == "shadow":  # 14. Eclipse - 日食幽灵（紫黑暗影箭）
                self.image = pygame.Surface((18, 36), pygame.SRCALPHA)
                pygame.draw.polygon(self.image, (100, 50, 180), [(9,0), (18,12), (15,36), (3,36), (0,12)])
                pygame.draw.polygon(self.image, (150, 100, 220), [(9,0), (18,12), (15,36), (3,36), (0,12)], 3)
                pygame.draw.circle(self.image, (200, 150, 255), (9, 12), 5)
                pygame.draw.circle(self.image, WHITE, (9, 12), 3)
                pygame.draw.circle(self.image, (80, 30, 120), (9, 26), 6)
                self.speed = -14
                
            elif b_type == "prism":  # 15. Prism - 棱镜分光（彩虹三棱镜）
                self.image = pygame.Surface((22, 30), pygame.SRCALPHA)
                pygame.draw.polygon(self.image, (100, 200, 255), [(11,0), (22,30), (0,30)])
                pygame.draw.polygon(self.image, (150, 230, 255), [(11,0), (22,30), (0,30)], 3)
                pygame.draw.polygon(self.image, (180, 150, 255), [(11,8), (17,26), (5,26)])
                pygame.draw.polygon(self.image, WHITE, [(11,12), (14,22), (8,22)])
                for a in [0, 120, 240]:
                    rad = math.radians(a)
                    x = 11 + int(6 * math.cos(rad))
                    y = 20 + int(6 * math.sin(rad))
                    pygame.draw.line(self.image, (200, 255, 255), (11, 20), (x, y), 2)
                self.speed = -15
                
            else:  # 16. Necro + 默认（紫红幽能，与Specter共用）
                self.image = pygame.Surface((18, 42), pygame.SRCALPHA)
                points = [(9,0), (5,14), (13,28), (9,42)]
                pygame.draw.lines(self.image, (200, 50, 150), False, points, 5)
                pygame.draw.lines(self.image, (255, 100, 200), False, points, 3)
                pygame.draw.circle(self.image, WHITE, (9, 8), 5)
                pygame.draw.circle(self.image, (220, 80, 180), (9, 24), 4)
                self.speed = -16
        
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
    
    def _create_themed_bullet(self, theme):
        """根据涂装主题创建子弹视觉"""
        effects = theme.get("effects", [])
        color = theme.get("color", self.color)
        size = 24  # 子弹基础尺寸
        
        if "gear_rotate" in effects:
            # 机械齿轮：六边形
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            points = []
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                px = center + int(size//2 * math.cos(angle))
                py = center + int(size//2 * math.sin(angle))
                points.append((px, py))
            pygame.draw.polygon(self.image, color, points)
            pygame.draw.polygon(self.image, (255, 255, 255), points, 2)
            self.speed = -15
            
        elif "phase_flicker" in effects:
            # 幽灵：波浪形
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            points = []
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                radius = size//2
                px = center + int(radius * math.cos(angle))
                py = center + int(radius * math.sin(angle))
                points.append((px, py))
            pygame.draw.polygon(self.image, color, points)
            self.speed = -18
            
        elif "lava_crack" in effects:
            # 反应堆：方形碎片
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            pygame.draw.rect(self.image, color, (center-size//2, center-size//2, size, size))
            pygame.draw.circle(self.image, (255, 255, 0), (center, center), size//4)
            self.speed = -14
            
        elif "quantum_shift" in effects:
            # 量子：菱形
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            diamond = [
                (center, center - size//2),
                (center + size//2, center),
                (center, center + size//2),
                (center - size//2, center)
            ]
            pygame.draw.polygon(self.image, color, diamond)
            self.speed = -16
            
        elif "holy_ray" in effects:
            # 圣光：八芒星
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            for rotation in [0, 45]:
                points = []
                for i in range(4):
                    angle = (i * 90 + rotation) * 3.14159 / 180
                    px = center + int(size//2 * math.cos(angle))
                    py = center + int(size//2 * math.sin(angle))
                    points.append((px, py))
                pygame.draw.polygon(self.image, color, points)
            self.speed = -14
            
        elif "dragon_breath" in effects:
            # 龙息：尖刺球
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            pygame.draw.circle(self.image, color, (center, center), size//3)
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                x1 = center + int(size//3 * math.cos(angle))
                y1 = center + int(size//3 * math.sin(angle))
                x2 = center + int(size//1.8 * math.cos(angle))
                y2 = center + int(size//1.8 * math.sin(angle))
                pygame.draw.line(self.image, (255, 100, 0), (x1, y1), (x2, y2), 3)
            self.speed = -13
            
        elif "blade_orbit" in effects:
            # 光刃：三角形
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            tri_points = [
                (center, center - size//2),
                (center - size//3, center + size//3),
                (center + size//3, center + size//3)
            ]
            pygame.draw.polygon(self.image, color, tri_points)
            pygame.draw.polygon(self.image, (255, 255, 255), tri_points, 2)
            self.speed = -17
        
        # ========== Phantom 子弹形状 ==========
        elif "void_crack" in effects:
            # 虚空裂缝：不规则裂缝形态
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 黑洞核心
            for r in range(size//2, 0, -size//8):
                alpha = int(200 * (1 - r / (size//2)))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (center, center), r)
                self.image.blit(temp_surf, (0, 0))
            # 裂缝线条
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                x1 = center + int(size//4 * math.cos(angle))
                y1 = center + int(size//4 * math.sin(angle))
                x2 = center + int(size * math.cos(angle))
                y2 = center + int(size * math.sin(angle))
                pygame.draw.line(self.image, (150, 0, 200), (x1, y1), (x2, y2), 2)
            self.speed = -16
            
        elif "ghost_face" in effects:
            # 幽灵面孔：椭圆脸+眼睛
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 脸型
            pygame.draw.ellipse(self.image, color, (size//2, size//3, size, size*4//3))
            # 眼睛
            pygame.draw.circle(self.image, (255, 255, 255), (center-size//4, center-size//6), size//8)
            pygame.draw.circle(self.image, (255, 255, 255), (center+size//4, center-size//6), size//8)
            pygame.draw.circle(self.image, (100, 100, 255), (center-size//4, center-size//6), size//12)
            pygame.draw.circle(self.image, (100, 100, 255), (center+size//4, center-size//6), size//12)
            self.speed = -15
            
        elif "crystal_prism" in effects:
            # 水晶棱镜：多面体
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 八面体结构
            top = (center, center - size//2)
            bottom = (center, center + size//2)
            mid_points = [
                (center - size//3, center - size//6),
                (center + size//3, center - size//6),
                (center + size//3, center + size//6),
                (center - size//3, center + size//6)
            ]
            # 绘制面
            for i in range(4):
                face = [top, mid_points[i], mid_points[(i+1)%4]]
                pygame.draw.polygon(self.image, color, face)
                pygame.draw.polygon(self.image, (255, 255, 255), face, 1)
            self.speed = -17
            
        elif "tentacle_crawl" in effects:
            # 触手蠕动：中心眼球+触手
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 眼球
            pygame.draw.circle(self.image, (150, 0, 150), (center, center), size//3)
            pygame.draw.circle(self.image, (255, 0, 255), (center, center), size//5)
            pygame.draw.circle(self.image, (50, 0, 50), (center, center), size//8)
            # 4条触手
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                segments = [(center, center)]
                for j in range(3):
                    r = (j + 1) * size // 6
                    px = center + int(r * math.cos(angle))
                    py = center + int(r * math.sin(angle))
                    segments.append((px, py))
                for k in range(len(segments)-1):
                    width = max(1, 4 - k)
                    pygame.draw.line(self.image, color, segments[k], segments[k+1], width)
            self.speed = -14
            
        elif "aurora_tail" in effects:
            # 极光彗星：头部+彩色尾迹
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 彗星头
            pygame.draw.circle(self.image, (255, 255, 255), (center+size//3, center), size//4)
            pygame.draw.circle(self.image, color, (center+size//3, center), size//6)
            # 彩色尾迹
            colors = [(255, 100, 100), (255, 255, 100), (100, 255, 100), (100, 100, 255)]
            for i, trail_color in enumerate(colors):
                y_offset = (i - 1.5) * size // 8
                pygame.draw.line(self.image, trail_color, 
                               (center+size//3, center), 
                               (center-size//2, int(center+y_offset)), 3)
            self.speed = -18
            
        elif "hourglass_flow" in effects:
            # 时空沙漏：沙漏形状
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 上三角
            top_tri = [
                (center, center),
                (center - size//2, center - size//2),
                (center + size//2, center - size//2)
            ]
            pygame.draw.polygon(self.image, color, top_tri)
            # 下三角
            bottom_tri = [
                (center, center),
                (center - size//2, center + size//2),
                (center + size//2, center + size//2)
            ]
            pygame.draw.polygon(self.image, color, bottom_tri)
            # 轮廓
            pygame.draw.polygon(self.image, (255, 255, 255), top_tri, 2)
            pygame.draw.polygon(self.image, (255, 255, 255), bottom_tri, 2)
            self.speed = -15
            
        elif "matrix_rain" in effects:
            # 矩阵代码雨：方块阵列
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 绘制小方块阵列
            for row in range(4):
                for col in range(4):
                    if (row + col) % 2 == 0:  # 棋盘格模式
                        x = size//3 + col * size//3
                        y = size//3 + row * size//3
                        block_size = size//5
                        pygame.draw.rect(self.image, color, (x, y, block_size, block_size))
                        pygame.draw.rect(self.image, (0, 200, 0), (x, y, block_size, block_size), 1)
            self.speed = -16
        
        # ========== Titan 子弹形状（大型、慢速）==========
        elif "shell_massive" in effects:
            # 巨型炮弹：更大尺寸
            big_size = int(size * 1.8)  # 放大1.8倍
            self.image = pygame.Surface((big_size, big_size*2), pygame.SRCALPHA)
            center = big_size // 2
            # 弹体
            body_width = big_size // 2
            body_height = big_size
            pygame.draw.rect(self.image, color, 
                           (center - body_width//2, center, body_width, body_height),
                           border_radius=3)
            pygame.draw.rect(self.image, (180, 180, 180), 
                           (center - body_width//2, center, body_width, body_height), 2,
                           border_radius=3)
            # 弹头
            tip = [
                (center, center - big_size//4),
                (center - body_width//2, center),
                (center + body_width//2, center)
            ]
            pygame.draw.polygon(self.image, (100, 100, 100), tip)
            pygame.draw.polygon(self.image, (200, 200, 200), tip, 2)
            self.speed = -12  # 较慢速度
            
        elif "nuclear_glow" in effects:
            # 核辐射球：发光效果
            big_size = int(size * 1.6)
            self.image = pygame.Surface((big_size*2, big_size*2), pygame.SRCALPHA)
            center = big_size
            # 多层光环
            for r in range(big_size, 0, -big_size//4):
                alpha = int(180 * (1 - (big_size - r) / big_size))
                temp_surf = pygame.Surface((big_size*2, big_size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (center, center), r)
                self.image.blit(temp_surf, (0, 0))
            # 核心
            pygame.draw.circle(self.image, (255, 255, 0), (center, center), big_size//3)
            pygame.draw.circle(self.image, color, (center, center), big_size//4)
            # 辐射标志
            for i in range(3):
                angle = (i * 120) * 3.14159 / 180
                x1 = center + int(big_size//5 * math.cos(angle))
                y1 = center + int(big_size//5 * math.sin(angle))
                x2 = center + int(big_size//1.5 * math.cos(angle))
                y2 = center + int(big_size//1.5 * math.sin(angle))
                pygame.draw.line(self.image, (0, 0, 0), (x1, y1), (x2, y2), 4)
            self.speed = -13
            
        elif "magma_boulder" in effects:
            # 熔岩巨石：最大尺寸
            big_size = int(size * 2.0)
            self.image = pygame.Surface((big_size, big_size), pygame.SRCALPHA)
            center = big_size // 2
            # 不规则岩石
            import random
            random.seed(42)
            points = []
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                radius = big_size//2.5 + random.randint(-big_size//10, big_size//10)
                px = center + int(radius * math.cos(angle))
                py = center + int(radius * math.sin(angle))
                points.append((px, py))
            pygame.draw.polygon(self.image, (80, 40, 0), points)
            pygame.draw.polygon(self.image, color, points, 2)
            # 岩浆裂缝
            for i in range(3):
                x1 = center + random.randint(-big_size//6, big_size//6)
                y1 = center + random.randint(-big_size//6, big_size//6)
                x2 = x1 + random.randint(-big_size//8, big_size//8)
                y2 = y1 + random.randint(-big_size//8, big_size//8)
                pygame.draw.line(self.image, (255, 255, 0), (x1, y1), (x2, y2), 2)
            self.speed = -11
            
        elif "rocket_thruster" in effects:
            # 机械火箭
            big_size = int(size * 1.7)
            self.image = pygame.Surface((big_size, big_size*2), pygame.SRCALPHA)
            center_x = big_size // 2
            center_y = big_size
            # 火箭头
            nose = [
                (center_x, center_y - big_size),
                (center_x - big_size//4, center_y - big_size*2//3),
                (center_x + big_size//4, center_y - big_size*2//3)
            ]
            pygame.draw.polygon(self.image, (200, 200, 200), nose)
            # 火箭身
            pygame.draw.rect(self.image, color, 
                           (center_x - big_size//4, center_y - big_size*2//3, big_size//2, big_size))
            pygame.draw.rect(self.image, (255, 255, 255), 
                           (center_x - big_size//4, center_y - big_size*2//3, big_size//2, big_size), 2)
            # 窗口
            pygame.draw.circle(self.image, (100, 200, 255), (center_x, center_y - big_size//4), big_size//8)
            # 尾焰
            flame = [
                (center_x - big_size//4, center_y + big_size//3),
                (center_x, center_y + big_size),
                (center_x + big_size//4, center_y + big_size//3)
            ]
            pygame.draw.polygon(self.image, (255, 200, 0), flame)
            self.speed = -14
            
        elif "ice_spike" in effects:
            # 冰晶巨刺
            big_size = int(size * 1.6)
            self.image = pygame.Surface((big_size*2, big_size*2), pygame.SRCALPHA)
            center = big_size
            # 四棱锥
            tip = (center, center - big_size)
            base = [
                (center - big_size//3, center + big_size//3),
                (center + big_size//3, center + big_size//3),
                (center + big_size//2, center),
                (center - big_size//2, center)
            ]
            for i in range(4):
                face = [tip, base[i], base[(i+1)%4]]
                pygame.draw.polygon(self.image, (*color, 200), face)
                pygame.draw.polygon(self.image, (255, 255, 255), face, 2)
            self.speed = -13
            
        elif "demon_skull" in effects:
            # 恶魔骷髅
            big_size = int(size * 1.9)
            self.image = pygame.Surface((big_size*2, big_size*2), pygame.SRCALPHA)
            center = big_size
            # 头骨
            pygame.draw.ellipse(self.image, (120, 0, 0), 
                              (center - big_size//2, center - big_size//2, big_size, big_size))
            pygame.draw.ellipse(self.image, color, 
                              (center - big_size//2, center - big_size//2, big_size, big_size), 3)
            # 眼睛
            pygame.draw.circle(self.image, (0, 0, 0), (center - big_size//4, center - big_size//8), big_size//8)
            pygame.draw.circle(self.image, (255, 0, 0), (center - big_size//4, center - big_size//8), big_size//8, 2)
            pygame.draw.circle(self.image, (0, 0, 0), (center + big_size//4, center - big_size//8), big_size//8)
            pygame.draw.circle(self.image, (255, 0, 0), (center + big_size//4, center - big_size//8), big_size//8, 2)
            # 恶魔角
            for dx in [-big_size//2, big_size//2]:
                horn = [
                    (center + dx, center - big_size//3),
                    (center + dx + (big_size//6 if dx < 0 else -big_size//6), center - big_size),
                    (center + dx + (big_size//4 if dx < 0 else -big_size//4), center - big_size//3)
                ]
                pygame.draw.polygon(self.image, (80, 0, 0), horn)
            self.speed = -12
            
        elif "plasma_beam" in effects:
            # 轨道激光柱
            big_size = int(size * 1.5)
            self.image = pygame.Surface((big_size*2, big_size*2), pygame.SRCALPHA)
            center = big_size
            # 核心
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), big_size//3)
            pygame.draw.circle(self.image, color, (center, center), big_size//4)
            # 十字光束
            beam_width = big_size // 6
            pygame.draw.rect(self.image, (*color, 220), 
                           (center - beam_width//2, 0, beam_width, big_size*2))
            pygame.draw.rect(self.image, (*color, 220), 
                           (0, center - beam_width//2, big_size*2, beam_width))
            # 瞄准圈
            for radius in [big_size//1.5, big_size]:
                pygame.draw.circle(self.image, (255, 255, 255), (center, center), radius, 2)
            self.speed = -15
        
        # ========== Thunderbird 子弹形状 ==========
        elif "lightning_bolt" in effects:
            # 闪电箭矢：之字形
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            segments = [
                (center, center - size),
                (center + size//4, center - size//2),
                (center - size//6, center),
                (center + size//5, center + size//2),
                (center, center + size)
            ]
            pygame.draw.lines(self.image, (255, 255, 255), False, segments, 5)
            pygame.draw.lines(self.image, color, False, segments, 2)
            self.speed = -17
            
        elif "tesla_coil" in effects:
            # 特斯拉线圈：螺旋+环
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 核心
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//4)
            pygame.draw.circle(self.image, color, (center, center), size//6)
            # 电弧环
            for i in range(3):
                arc_radius = size//3 + i * size//6
                pygame.draw.circle(self.image, color, (center, center), arc_radius, 2)
            self.speed = -16
            
        elif "feather_shape" in effects:
            # 等离子羽毛
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 羽轴
            pygame.draw.line(self.image, (200, 200, 200), 
                           (center, center - size), (center, center + size), 3)
            # 羽丝
            for i in range(8):
                y = center - size + i * size//4
                width = int(size//2 * (1 - abs(i - 4) / 4))
                pygame.draw.line(self.image, color, 
                               (center, y), (center - width, y + size//8), 2)
                pygame.draw.line(self.image, color, 
                               (center, y), (center + width, y + size//8), 2)
            self.speed = -15
            
        elif "aurora_blade" in effects:
            # 极光羽刃：菱形刀刃
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            blade = [
                (center, center - size),
                (center + size//4, center),
                (center, center + size),
                (center - size//4, center)
            ]
            # 彩虹效果
            colors_gradient = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255)]
            for i, grad_color in enumerate(colors_gradient):
                offset = i * 2
                temp_blade = [(x + offset, y) for x, y in blade]
                pygame.draw.polygon(self.image, (*grad_color, 120), temp_blade)
            pygame.draw.polygon(self.image, (255, 255, 255), blade, 2)
            self.speed = -16
            
        elif "holy_spear" in effects:
            # 女武神之矛
            self.image = pygame.Surface((size, size*3), pygame.SRCALPHA)
            center_x = size // 2
            center_y = size
            # 矛杆
            shaft_width = size // 8
            pygame.draw.rect(self.image, (180, 160, 140), 
                           (center_x - shaft_width//2, center_y, shaft_width, size))
            # 矛尖
            spear_tip = [
                (center_x, center_y - size),
                (center_x - size//3, center_y),
                (center_x + size//3, center_y)
            ]
            pygame.draw.polygon(self.image, (220, 220, 240), spear_tip)
            pygame.draw.polygon(self.image, color, spear_tip, 2)
            self.speed = -14
            
        elif "phoenix_plume" in effects:
            # 凤凰火羽
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 羽轴
            pygame.draw.line(self.image, (255, 200, 0), 
                           (center, center - size), (center, center + size), 4)
            # 火焰羽丝
            for i in range(6):
                y = center - size + i * size//3
                flame_width = int(size//1.5 * (1 - abs(i - 3) / 3))
                # 左侧
                pygame.draw.line(self.image, (255, 100, 0), 
                               (center, y), (center - flame_width, y + size//6), 3)
                pygame.draw.line(self.image, (255, 200, 0), 
                               (center, y), (center - flame_width, y + size//6), 1)
                # 右侧
                pygame.draw.line(self.image, (255, 100, 0), 
                               (center, y), (center + flame_width, y + size//6), 3)
                pygame.draw.line(self.image, (255, 200, 0), 
                               (center, y), (center + flame_width, y + size//6), 1)
            self.speed = -15
            
        elif "nebula_feather" in effects:
            # 星云羽毛
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 羽轴
            pygame.draw.line(self.image, (200, 150, 255), 
                           (center, center - size), (center, center + size), 3)
            # 羽丝
            for i in range(8):
                y = center - size + i * size//4
                width = int(size//2 * (1 - abs(i - 4) / 4))
                pygame.draw.line(self.image, color, 
                               (center, y), (center - width, y + size//8), 2)
                pygame.draw.line(self.image, color, 
                               (center, y), (center + width, y + size//8), 2)
            # 星点
            import random
            random.seed(456)
            for _ in range(8):
                star_x = center + random.randint(-size//2, size//2)
                star_y = center + random.randint(-size, size)
                pygame.draw.circle(self.image, (255, 255, 255), (star_x, star_y), 2)
            self.speed = -16
        
        # ========== Viper 子弹形状 ==========
        elif "venom_fang" in effects:
            # 毒牙：三角形+毒滴
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            fang = [
                (center, center + size//2),
                (center - size//3, center - size//2),
                (center + size//3, center - size//2)
            ]
            pygame.draw.polygon(self.image, (200, 200, 200), fang)
            pygame.draw.polygon(self.image, color, fang, 2)
            # 毒液滴
            for i in range(2):
                drop_y = center + size//2 + (i + 1) * size//6
                pygame.draw.circle(self.image, color, (center, int(drop_y)), size//10)
            self.speed = -16
            
        elif "acid_drop" in effects:
            # 强酸液滴
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            pygame.draw.circle(self.image, color, (center, center), size//2)
            pygame.draw.circle(self.image, (255, 255, 100), (center, center), size//3)
            # 泪滴尖
            tip = [
                (center, center + size//2),
                (center - size//6, center + size//4),
                (center + size//6, center + size//4)
            ]
            pygame.draw.polygon(self.image, color, tip)
            self.speed = -15
            
        elif "biohazard_symbol" in effects:
            # 生化符号
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 中心圆
            pygame.draw.circle(self.image, (0, 0, 0), (center, center), size//6)
            pygame.draw.circle(self.image, color, (center, center), size//6, 2)
            # 三叶
            for i in range(3):
                angle = (i * 120) * 3.14159 / 180
                leaf_x = center + int(size//2 * math.cos(angle))
                leaf_y = center + int(size//2 * math.sin(angle))
                pygame.draw.circle(self.image, color, (leaf_x, leaf_y), size//5)
                pygame.draw.circle(self.image, (0, 0, 0), (leaf_x, leaf_y), size//8)
                # 连接线
                inner_x = center + int(size//6 * math.cos(angle))
                inner_y = center + int(size//6 * math.sin(angle))
                outer_x = center + int(size//3 * math.cos(angle))
                outer_y = center + int(size//3 * math.sin(angle))
                pygame.draw.line(self.image, color, (inner_x, inner_y), (outer_x, outer_y), 3)
            self.speed = -14
            
        elif "plasma_orb" in effects:
            # 等离子球
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 多层
            for r in range(size, size//3, -size//6):
                alpha = int(200 * (1 - (size - r) / (size*2//3)))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (center, center), r)
                self.image.blit(temp_surf, (0, 0))
            pygame.draw.circle(self.image, (255, 100, 255), (center, center), size//4)
            self.speed = -15
            
        elif "hydra_heads" in effects:
            # 九头蛇
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 身体
            pygame.draw.circle(self.image, (100, 150, 50), (center, center), size//3)
            pygame.draw.circle(self.image, color, (center, center), size//3, 2)
            # 蛇头
            for i in range(5):
                angle = (i * 72 - 90) * 3.14159 / 180
                head_x = center + int(size*2//3 * math.cos(angle))
                head_y = center + int(size*2//3 * math.sin(angle))
                head_tip = [
                    (head_x + int(size//6 * math.cos(angle)), head_y + int(size//6 * math.sin(angle))),
                    (head_x + int(size//10 * math.cos(angle + 0.5)), head_y + int(size//10 * math.sin(angle + 0.5))),
                    (head_x + int(size//10 * math.cos(angle - 0.5)), head_y + int(size//10 * math.sin(angle - 0.5)))
                ]
                pygame.draw.polygon(self.image, (150, 200, 50), head_tip)
                pygame.draw.line(self.image, color, (center, center), (head_x, head_y), 2)
            self.speed = -13
            
        elif "neon_glow" in effects:
            # 霓虹发光
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 外发光
            for r in range(size, size//4, -size//8):
                alpha = int(180 * (1 - (size - r) / (size*3//4)))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (center, center), r)
                self.image.blit(temp_surf, (0, 0))
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//4)
            pygame.draw.circle(self.image, color, (center, center), size//6)
            self.speed = -16
            
        elif "serpent_eye" in effects:
            # 蛇神之眼
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 眼轮廓
            pygame.draw.ellipse(self.image, (255, 200, 0), 
                              (center - size//2, center - size//3, size, size*2//3))
            pygame.draw.ellipse(self.image, color, 
                              (center - size//2, center - size//3, size, size*2//3), 2)
            # 竖瞳
            pupil_width = size // 8
            pupil_height = size // 2
            pygame.draw.ellipse(self.image, (0, 0, 0), 
                              (center - pupil_width//2, center - pupil_height//2, pupil_width, pupil_height))
            # 眼神光
            pygame.draw.circle(self.image, (255, 255, 200), (center - size//8, center - size//8), size//12)
            self.speed = -14
        
        # ========== Specter 子弹形状 ==========
        elif "scythe_blade" in effects:
            # 死神镰刀
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 镰刀柄
            pygame.draw.line(self.image, (80, 80, 80), (center, center + size//2), (center, center + size), 4)
            # 弯月刀刃
            blade_rect = pygame.Rect(center - size, center - size, size*2, size*2)
            pygame.draw.arc(self.image, color, blade_rect, 0, 3.14159, 4)
            # 刀尖
            tip = [
                (center - size, center),
                (center - size - size//6, center - size//10),
                (center - size, center - size//5)
            ]
            pygame.draw.polygon(self.image, color, tip)
            self.speed = -14
            
        elif "shadow_dagger" in effects:
            # 暗影匕首
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 刀刃
            blade = [
                (center, center - size),
                (center + size//6, center),
                (center, center + size//3),
                (center - size//6, center)
            ]
            pygame.draw.polygon(self.image, (100, 100, 150), blade)
            pygame.draw.polygon(self.image, color, blade, 2)
            # 刀柄
            pygame.draw.rect(self.image, (50, 50, 80), (center - size//10, center + size//3, size//5, size//3))
            self.speed = -17
            
        elif "wraith_chain" in effects:
            # 怨灵锁链
            self.image = pygame.Surface((size, size*3), pygame.SRCALPHA)
            center_x = size // 2
            # 锁链链节
            for i in range(6):
                y_pos = i * size // 3
                link_rect = (center_x - size//8, y_pos, size//4, size//6)
                pygame.draw.ellipse(self.image, color, link_rect, 2)
            self.speed = -15
            
        elif "sniper_round" in effects:
            # 狙击弹
            self.image = pygame.Surface((size, size*2), pygame.SRCALPHA)
            center_x = size // 2
            center_y = size
            # 弹头
            tip = [
                (center_x, center_y - size),
                (center_x - size//4, center_y - size//2),
                (center_x + size//4, center_y - size//2)
            ]
            pygame.draw.polygon(self.image, (200, 200, 220), tip)
            pygame.draw.polygon(self.image, color, tip, 2)
            # 弹体
            pygame.draw.rect(self.image, (180, 180, 200), (center_x - size//4, center_y - size//2, size//2, size))
            pygame.draw.rect(self.image, color, (center_x - size//4, center_y - size//2, size//2, size), 2)
            self.speed = -18
            
        elif "poltergeist_cube" in effects:
            # 灵异魔方
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            cube_size = size // 2
            # 正面
            front = [
                (center - cube_size, center - cube_size),
                (center + cube_size, center - cube_size),
                (center + cube_size, center + cube_size),
                (center - cube_size, center + cube_size)
            ]
            pygame.draw.polygon(self.image, color, front)
            pygame.draw.polygon(self.image, (255, 255, 255), front, 2)
            # 上面
            top = [
                (center - cube_size, center - cube_size),
                (center + cube_size, center - cube_size),
                (center + cube_size + cube_size//2, center - cube_size - cube_size//2),
                (center - cube_size + cube_size//2, center - cube_size - cube_size//2)
            ]
            pygame.draw.polygon(self.image, (*color, 180), top)
            self.speed = -13
            
        elif "fallen_wing" in effects:
            # 堕落天使
            self.image = pygame.Surface((size*3, size*2), pygame.SRCALPHA)
            center_x = size*3//2
            center_y = size
            # 左翼羽毛
            for i in range(4):
                fx = center_x - size//4 - i * size//6
                fy = center_y - size//3 + i * size//8
                feather = [
                    (fx, fy),
                    (fx - size//8, fy + size//5),
                    (fx + size//12, fy + size//6)
                ]
                pygame.draw.polygon(self.image, (50, 50, 80), feather)
            # 右翼羽毛
            for i in range(4):
                fx = center_x + size//4 + i * size//6
                fy = center_y - size//3 + i * size//8
                feather = [
                    (fx, fy),
                    (fx + size//8, fy + size//5),
                    (fx - size//12, fy + size//6)
                ]
                pygame.draw.polygon(self.image, (50, 50, 80), feather)
            # 中心光
            pygame.draw.circle(self.image, (150, 150, 200), (center_x, center_y), size//6)
            self.speed = -15
            
        # ========== Aurora 子弹 ==========
        elif "goddess_aura" in effects or "holy_rings" in effects:
            # 女神光辉/圣洁光环
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 神圣核心
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//4)
            pygame.draw.circle(self.image, color, (center, center), size//5)
            # 光环（3层）
            for i in range(3):
                ring_r = size//3 + i * size//5
                alpha = 200 - i * 50
                temp = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp, (*color, alpha), (center, center), ring_r, 2)
                self.image.blit(temp, (0, 0))
            self.speed = -14
            
        elif "nebula_swirl" in effects or "star_sparkle" in effects:
            # 星云之心/星辰闪烁
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 星云核心
            pygame.draw.circle(self.image, (180, 130, 255), (center, center), size//3)
            # 星云漩涡
            for arm in range(3):
                for i in range(8):
                    angle = (i * 45 + arm * 120) * 3.14159 / 180
                    r = size//4 + i * size//20
                    x = center + int(r * math.cos(angle))
                    y = center + int(r * math.sin(angle))
                    pygame.draw.circle(self.image, color, (x, y), size//15)
            self.speed = -14
            
        elif "ice_crown" in effects or "frost_spikes" in effects:
            # 冰雪王冠/冰霜尖刺
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 冰晶核心
            pygame.draw.circle(self.image, (230, 245, 255), (center, center), size//5)
            # 冰刺（6根）
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                x1 = center + int(size//5 * math.cos(angle))
                y1 = center + int(size//5 * math.sin(angle))
                x2 = center + int(size//1.5 * math.cos(angle))
                y2 = center + int(size//1.5 * math.sin(angle))
                # 冰锥
                perp = angle + 1.5708
                p1 = (x1 + int(size//12 * math.cos(perp)), y1 + int(size//12 * math.sin(perp)))
                p2 = (x1 - int(size//12 * math.cos(perp)), y1 - int(size//12 * math.sin(perp)))
                spike = [(x2, y2), p1, p2]
                temp = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.polygon(temp, (*color, 200), spike)
                self.image.blit(temp, (0, 0))
                pygame.draw.polygon(self.image, (255, 255, 255), spike, 1)
            self.speed = -14
            
        elif "rainbow_beam" in effects or "chromatic_shift" in effects:
            # 彩虹光束/彩虹折射
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 彩虹射线
            rainbow_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]
            for i, rc in enumerate(rainbow_colors):
                angle = (i * 360 / 7) * 3.14159 / 180
                x2 = center + int(size//1.5 * math.cos(angle))
                y2 = center + int(size//1.5 * math.sin(angle))
                pygame.draw.line(self.image, rc, (center, center), (x2, y2), 2)
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//5)
            self.speed = -15
            
        elif "prism_split" in effects or "light_refract" in effects:
            # 棱镜折射/光线折射
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 棱镜（菱形）
            prism = [(center, center - size), (center + size//2, center), (center, center + size), (center - size//2, center)]
            temp = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.polygon(temp, (*color, 180), prism)
            self.image.blit(temp, (0, 0))
            pygame.draw.polygon(self.image, (255, 255, 255), prism, 2)
            # 折射光
            for i, rc in enumerate([(255, 0, 0), (0, 255, 0), (0, 0, 255)]):
                angle = (30 + i * 30) * 3.14159 / 180
                x1 = center + int(size//2 * math.cos(angle))
                y1 = center + int(size//2 * math.sin(angle))
                x2 = center + int(size * math.cos(angle + 0.3))
                y2 = center + int(size * math.sin(angle + 0.3))
                pygame.draw.line(self.image, rc, (x1, y1), (x2, y2), 2)
            self.speed = -15
            
        elif "sakura_petal" in effects or "petal_spin" in effects:
            # 樱花飞舞/樱花旋转
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 花瓣（5瓣）
            for i in range(5):
                angle = (i * 72) * 3.14159 / 180
                px = center + int(size//2 * math.cos(angle))
                py = center + int(size//2 * math.sin(angle))
                # 花瓣椭圆
                petal_rect = pygame.Rect(px - size//6, py - size//4, size//3, size//2)
                temp = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.ellipse(temp, (*color, 200), petal_rect)
                self.image.blit(temp, (0, 0))
                pygame.draw.ellipse(self.image, (255, 180, 200), petal_rect, 1)
            # 花心
            pygame.draw.circle(self.image, (255, 200, 220), (center, center), size//8)
            self.speed = -13
            
        elif "celestial_ring" in effects or "divine_blessing" in effects:
            # 天界光环/神圣祝福
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 十字光芒
            pygame.draw.line(self.image, (255, 255, 240), (center, 0), (center, size*2), 4)
            pygame.draw.line(self.image, (255, 255, 240), (0, center), (size*2, center), 4)
            pygame.draw.line(self.image, color, (center, 0), (center, size*2), 2)
            pygame.draw.line(self.image, color, (0, center), (size*2, center), 2)
            # 中心光核
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//4)
            pygame.draw.circle(self.image, color, (center, center), size//6)
            self.speed = -15
            
        # ========== Crimson 子弹 ==========
        elif "blood_blade" in effects or "crimson_mist" in effects:
            # 血月之刃/血雾弥漫
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 弯刀形状
            blade_points = []
            for i in range(12):
                angle = (i * 15 - 90) * 3.14159 / 180
                r = size
                x = center + int(r * math.cos(angle))
                y = center + int(r * math.sin(angle))
                blade_points.append((x, y))
            if len(blade_points) > 1:
                pygame.draw.lines(self.image, color, False, blade_points, 4)
                pygame.draw.lines(self.image, (255, 0, 0), False, blade_points, 2)
            # 血雾
            for i in range(5):
                r = size//4 + i * size//8
                alpha = 150 - i * 25
                temp = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp, (*color, alpha), (center, center), r)
                self.image.blit(temp, (0, 0))
            self.speed = -15
            
        elif "katana_slash" in effects or "blade_flash" in effects:
            # 武士刀气/刀光闪烁
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 斜斩刀光
            x1, y1 = size//2, size*3//2
            x2, y2 = size*3//2, size//2
            for i in range(4):
                offset = i * 2
                alpha = 220 - i * 40
                temp = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.line(temp, (*color, alpha), (x1 + offset, y1 - offset), (x2 + offset, y2 - offset), 5 - i)
                self.image.blit(temp, (0, 0))
            pygame.draw.line(self.image, (255, 255, 255), (x1, y1), (x2, y2), 1)
            self.speed = -16
            
        elif "demon_claw" in effects or "blood_scratch" in effects:
            # 恶魔之爪/血色爪痕
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 爪痕（3条）
            for i in range(3):
                offset = (i - 1) * size//3
                x1 = center + offset - size//6
                y1 = size//4
                x2 = center + offset + size//6
                y2 = size*7//4
                pygame.draw.line(self.image, (80, 0, 0), (x1, y1), (x2, y2), 5)
                pygame.draw.line(self.image, color, (x1, y1), (x2, y2), 3)
            self.speed = -15
            
        elif "hellfire_burst" in effects or "inferno_wave" in effects:
            # 地狱烈焰/炼狱波动
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 火核
            pygame.draw.circle(self.image, (255, 255, 0), (center, center), size//5)
            pygame.draw.circle(self.image, color, (center, center), size//4)
            # 火焰爆发（8个火舌）
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                x1 = center + int(size//5 * math.cos(angle))
                y1 = center + int(size//5 * math.sin(angle))
                x2 = center + int(size * math.cos(angle))
                y2 = center + int(size * math.sin(angle))
                # 火焰渐变
                pygame.draw.line(self.image, (255, 200, 0), (x1, y1), (x2, y2), 4)
                pygame.draw.line(self.image, (255, 100, 0), (x1, y1), (x2, y2), 2)
            self.speed = -15
            
        elif "rose_petal" in effects or "thorn_spike" in effects:
            # 血玫瑰刺/尖刺荆棘
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 玫瑰花瓣（5瓣）
            for i in range(5):
                angle = (i * 72) * 3.14159 / 180
                px = center + int(size//2 * math.cos(angle))
                py = center + int(size//2 * math.sin(angle))
                petal_rect = pygame.Rect(px - size//6, py - size//5, size//3, size//2)
                temp = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.ellipse(temp, (*color, 200), petal_rect)
                self.image.blit(temp, (0, 0))
                pygame.draw.ellipse(self.image, (180, 30, 60), petal_rect, 1)
            # 花心
            pygame.draw.circle(self.image, (150, 0, 40), (center, center), size//8)
            # 尖刺
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                x1 = center + int(size//8 * math.cos(angle))
                y1 = center + int(size//8 * math.sin(angle))
                x2 = center + int(size//1.5 * math.cos(angle))
                y2 = center + int(size//1.5 * math.sin(angle))
                pygame.draw.line(self.image, (200, 50, 80), (x1, y1), (x2, y2), 2)
            self.speed = -14
            
        elif "dragon_breath" in effects or "blood_scale" in effects:
            # 血龙吐息/血色龙鳞
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 龙头
            head = [(center - size//3, center - size//3), (center, center - size), 
                   (center + size//3, center - size//3), (center + size//4, center), (center - size//4, center)]
            pygame.draw.polygon(self.image, (150, 0, 0), head)
            pygame.draw.polygon(self.image, color, head, 2)
            # 龙鳞纹理
            for row in range(2):
                for col in range(2):
                    sx = center + (col - 0.5) * size//3
                    sy = center + (row - 0.5) * size//3
                    scale = [(sx, sy - size//10), (sx + size//12, sy), (sx, sy + size//10), (sx - size//12, sy)]
                    temp = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                    pygame.draw.polygon(temp, (*color, 180), scale)
                    self.image.blit(temp, (0, 0))
            # 火焰吐息
            breath = [(center, center), (center - size//6, center + size//2), (center + size//8, center + size//1.5)]
            pygame.draw.lines(self.image, (255, 100, 0), False, breath, 6)
            self.speed = -16
            
        elif "bat_swarm" in effects or "vampire_drain" in effects:
            # 吸血蝠群/吸血吸取
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 蝙蝠（4只）
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                bx = center + int(size//2 * math.cos(angle))
                by = center + int(size//2 * math.sin(angle))
                # 翅膀
                wing = size // 6
                left = [(bx, by), (bx - wing, by - wing//2), (bx - wing//2, by + wing//4)]
                right = [(bx, by), (bx + wing, by - wing//2), (bx + wing//2, by + wing//4)]
                pygame.draw.polygon(self.image, color, left)
                pygame.draw.polygon(self.image, color, right)
                pygame.draw.circle(self.image, (80, 0, 40), (bx, by), size//20)
            # 中心血核
            pygame.draw.circle(self.image, (120, 0, 50), (center, center), size//5)
            self.speed = -15
        
        # ========== Stalker 子弹 ==========
        elif "plasma_disc" in effects or "heat_trail" in effects:
            # 铁血飞盘
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 飞盘主体
            pygame.draw.circle(self.image, (180, 0, 220), (center, center), size//2)
            # 锯齿边（6个）
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                x1 = center + int(size//2 * math.cos(angle))
                y1 = center + int(size//2 * math.sin(angle))
                x2 = center + int(size//1.5 * math.cos(angle))
                y2 = center + int(size//1.5 * math.sin(angle))
                perp = angle + 1.5708
                p1 = (x1 + int(size//12 * math.cos(perp)), y1 + int(size//12 * math.sin(perp)))
                p2 = (x1 - int(size//12 * math.cos(perp)), y1 - int(size//12 * math.sin(perp)))
                pygame.draw.polygon(self.image, color, [(x2, y2), p1, p2])
            # 中心
            pygame.draw.circle(self.image, (255, 0, 255), (center, center), size//5)
            self.speed = -16
            
        elif "acid_drop" in effects or "corrosive" in effects:
            # 异形酸液
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 液滴形状
            drop = [(center, center - size), (center + size//2, center), (center, center + size), (center - size//2, center)]
            temp = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.polygon(temp, (*color, 220), drop)
            self.image.blit(temp, (0, 0))
            pygame.draw.polygon(self.image, (150, 200, 0), drop, 2)
            # 腐蚀气泡
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                bubble_x = center + int(size//3 * math.cos(angle))
                bubble_y = center + int(size//3 * math.sin(angle))
                pygame.draw.circle(self.image, (200, 255, 0), (bubble_x, bubble_y), size//15)
            self.speed = -14
            
        elif "color_shift" in effects or "stealth_flicker" in effects:
            # 变色迷彩
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 多层渐变
            shift_colors = [(120, 180, 120), (80, 140, 180), (140, 120, 160)]
            for i, sc in enumerate(shift_colors):
                radius = size//1.5 - i * size//8
                alpha = 200 - i * 50
                temp = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp, (*sc, alpha), (center, center), radius)
                self.image.blit(temp, (0, 0))
            self.speed = -15
            
        elif "spore_burst" in effects or "swarm_split" in effects:
            # 虫群孢子
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 主孢子囊
            pygame.draw.circle(self.image, (100, 140, 60), (center, center), size//3)
            pygame.draw.circle(self.image, color, (center, center), size//3, 2)
            # 裂变纹理
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                x2 = center + int(size//3 * math.cos(angle))
                y2 = center + int(size//3 * math.sin(angle))
                pygame.draw.line(self.image, (60, 100, 30), (center, center), (x2, y2), 2)
            # 小孢子
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                sx = center + int(size//1.5 * math.cos(angle))
                sy = center + int(size//1.5 * math.sin(angle))
                temp = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp, (*color, 180), (sx, sy), size//12)
                self.image.blit(temp, (0, 0))
            self.speed = -14
            
        elif "drone_tracking" in effects or "scanner_lock" in effects:
            # 追踪无人机
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 十字机身
            pygame.draw.rect(self.image, (220, 170, 0), (size//2, center - size//10, size, size//5))
            pygame.draw.rect(self.image, (220, 170, 0), (center - size//10, size//2, size//5, size))
            # 中心核心
            pygame.draw.circle(self.image, (255, 200, 0), (center, center), size//5)
            # 四旋翼
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                rx = center + int(size//2 * math.cos(angle))
                ry = center + int(size//2 * math.sin(angle))
                pygame.draw.circle(self.image, (180, 140, 0), (rx, ry), size//8, 2)
            self.speed = -16
            
        elif "void_phase" in effects or "dimension_shift" in effects:
            # 虚空潜行
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 裂隙
            rift = [(center, center - size), (center - size//6, center - size//3), (center + size//8, center + size//3), (center, center + size)]
            pygame.draw.lines(self.image, (150, 0, 200), False, rift, 3)
            pygame.draw.lines(self.image, (200, 100, 255), False, rift, 1)
            # 虚空漩涡
            for i in range(3):
                radius = size//3 + i * size//6
                alpha = 180 - i * 50
                temp = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp, (*color, alpha), (center, center), radius, 2)
                self.image.blit(temp, (0, 0))
            self.speed = -15
            
        elif "xenomorph_egg" in effects or "hive_spawn" in effects:
            # 异形卵巢
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 卵体
            egg_rect = pygame.Rect(center - size//2, center - size, size, size*2)
            temp = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.ellipse(temp, (*color, 220), egg_rect)
            self.image.blit(temp, (0, 0))
            pygame.draw.ellipse(self.image, (60, 140, 60), egg_rect, 2)
            # 竖纹
            for i in range(4):
                line_x = center - size//3 + i * size//4
                pygame.draw.line(self.image, (40, 100, 40), (line_x, center - size), (line_x, center + size), 1)
            # 触手
            for i in range(4):
                angle = (i * 90 + 45) * 3.14159 / 180
                for j in range(3):
                    radius = size//2 + j * size//8
                    tx = center + int(radius * math.cos(angle))
                    ty = center + int(radius * math.sin(angle))
                    pygame.draw.circle(self.image, (60, 120, 60), (tx, ty), size//15)
            self.speed = -14
            
        # ========== Gaia 子弹 ==========
        elif "seed_spiral" in effects or "leaf_swirl" in effects:
            # 森林之种
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 种子核心
            pygame.draw.circle(self.image, (100, 200, 100), (center, center), size//5)
            pygame.draw.circle(self.image, color, (center, center), size//6)
            # 螺旋叶片（6片）
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                leaf_x = center + int(size//2 * math.cos(angle))
                leaf_y = center + int(size//2 * math.sin(angle))
                leaf_rect = pygame.Rect(leaf_x - size//10, leaf_y - size//8, size//5, size//4)
                temp = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.ellipse(temp, (*color, 200), leaf_rect)
                self.image.blit(temp, (0, 0))
                pygame.draw.ellipse(self.image, (100, 220, 100), leaf_rect, 1)
            self.speed = -13
            
        elif "crystal_facet" in effects or "gem_sparkle" in effects:
            # 水晶宝石
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 六边形晶体
            crystal = []
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                px = center + int(size//1.5 * math.cos(angle))
                py = center + int(size//1.5 * math.sin(angle))
                crystal.append((px, py))
            temp = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.polygon(temp, (*color, 200), crystal)
            self.image.blit(temp, (0, 0))
            pygame.draw.polygon(self.image, (0, 255, 220), crystal, 2)
            # 切面
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                x2 = center + int(size//1.5 * math.cos(angle))
                y2 = center + int(size//1.5 * math.sin(angle))
                pygame.draw.line(self.image, (0, 220, 200), (center, center), (x2, y2), 1)
            self.speed = -14
            
        elif "vine_coil" in effects or "thorn_barb" in effects:
            # 荆棘藤蔓
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 藤蔓螺旋
            vine = []
            for i in range(12):
                angle = (i * 30) * 3.14159 / 180
                radius = size//4 + (i / 12) * size//2
                vx = center + int(radius * math.cos(angle))
                vy = center + int(radius * math.sin(angle))
                vine.append((vx, vy))
            if len(vine) > 1:
                pygame.draw.lines(self.image, (120, 160, 60), False, vine, 3)
                pygame.draw.lines(self.image, color, False, vine, 1)
            # 荆棘
            for i in range(0, len(vine), 3):
                if i < len(vine):
                    vx, vy = vine[i]
                    thorn = [(vx, vy - size//10), (vx + size//15, vy), (vx - size//15, vy)]
                    pygame.draw.polygon(self.image, (140, 180, 70), thorn)
            self.speed = -14
            
        elif "petal_storm" in effects or "bloom_burst" in effects:
            # 花瓣风暴
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 花心
            pygame.draw.circle(self.image, (255, 200, 0), (center, center), size//8)
            # 花瓣（8片）
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                px = center + int(size//2 * math.cos(angle))
                py = center + int(size//2 * math.sin(angle))
                petal_rect = pygame.Rect(px - size//10, py - size//8, size//5, size//4)
                temp = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.ellipse(temp, (*color, 220), petal_rect)
                self.image.blit(temp, (0, 0))
                pygame.draw.ellipse(self.image, (255, 180, 220), petal_rect, 1)
            self.speed = -13
            
        elif "rock_boulder" in effects or "earth_crack" in effects:
            # 大地之石
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 岩石（不规则）
            rock = [
                (center, center - size),
                (center + size//2, center - size//3),
                (center + size//1.5, center + size//4),
                (center + size//3, center + size),
                (center - size//3, center + size),
                (center - size//1.5, center + size//4),
                (center - size//2, center - size//3)
            ]
            pygame.draw.polygon(self.image, (140, 120, 80), rock)
            pygame.draw.polygon(self.image, color, rock, 2)
            # 裂纹
            pygame.draw.line(self.image, (80, 60, 40), (center - size//4, center - size//3), (center + size//3, center + size//6), 2)
            self.speed = -15
            
        elif "mushroom_cap" in effects or "spore_cloud" in effects:
            # 魔法蘑菇
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 伞盖
            cap_rect = pygame.Rect(center - size//1.5, center - size, size*4//3, size)
            temp = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.ellipse(temp, (*color, 220), cap_rect)
            self.image.blit(temp, (0, 0))
            pygame.draw.arc(self.image, (220, 120, 255), cap_rect, 0, 3.14159, 2)
            # 柄
            pygame.draw.rect(self.image, (180, 150, 200), (center - size//10, center, size//5, size))
            # 斑点
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                spot_x = center + int(size//3 * math.cos(angle))
                spot_y = center - size//2
                pygame.draw.circle(self.image, (255, 200, 255), (spot_x, spot_y), size//15)
            self.speed = -13
            
        elif "tree_rings" in effects or "ancient_runes" in effects:
            # 古树之心
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 年轮
            for i in range(4):
                ring_r = size//4 + i * size//8
                pygame.draw.circle(self.image, (130 - i * 15, 90 - i * 10, 40), (center, center), ring_r, 2)
            # 中心
            pygame.draw.circle(self.image, (180, 120, 60), (center, center), size//6)
            # 符文（4个）
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                rune_x = center + int(size//2 * math.cos(angle))
                rune_y = center + int(size//2 * math.sin(angle))
                pygame.draw.line(self.image, (200, 150, 80), (rune_x, rune_y - size//12), (rune_x, rune_y + size//12), 2)
                pygame.draw.line(self.image, (200, 150, 80), (rune_x - size//15, rune_y - size//15), (rune_x + size//15, rune_y - size//15), 2)
            self.speed = -14
        
        # ========== Weaver 子弹 ==========
        elif "web_net" in effects or "spider_silk" in effects:
            # 蛛网陷阱
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 蛛网节点
            pygame.draw.circle(self.image, (220, 220, 220), (center, center), size//6)
            pygame.draw.circle(self.image, color, (center, center), size//8)
            # 放射线（6条）
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                x1 = center + int(size//8 * math.cos(angle))
                y1 = center + int(size//8 * math.sin(angle))
                x2 = center + int(size//1.5 * math.cos(angle))
                y2 = center + int(size//1.5 * math.sin(angle))
                pygame.draw.line(self.image, (200, 200, 200), (x1, y1), (x2, y2), 2)
            # 蛛网环（2层）
            for i in range(2):
                ring_r = size//3 + i * size//5
                web_points = []
                for j in range(6):
                    angle = (j * 60) * 3.14159 / 180
                    px = center + int(ring_r * math.cos(angle))
                    py = center + int(ring_r * math.sin(angle))
                    web_points.append((px, py))
                if len(web_points) > 1:
                    pygame.draw.lines(self.image, (180, 180, 180), True, web_points, 1)
            self.speed = -13
        
        elif "phase_shift" in effects or "dimension_warp" in effects:
            # 相位穿梭
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 多重相位（3层）
            shift_offsets = [(0, 0), (2, -2), (4, -4)]
            for i, (dx, dy) in enumerate(shift_offsets):
                alpha = 220 - i * 60
                diamond = [
                    (center + dx, center//2 + dy),
                    (center + size//2 + dx, center + dy),
                    (center + dx, center + size//2 + dy),
                    (center - size//2 + dx, center + dy)
                ]
                pygame.draw.polygon(self.image, (*color, alpha), diamond)
                if i == 0:
                    pygame.draw.polygon(self.image, (200, 200, 220), diamond, 2)
            # 相位粒子
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                px = center + int(size//4 * math.cos(angle))
                py = center + int(size//4 * math.sin(angle))
                pygame.draw.circle(self.image, (180, 180, 220), (px, py), size//25)
            self.speed = -16
        
        elif "void_cocoon" in effects or "space_lock" in effects:
            # 虚空之茧
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 茧外壳（椭圆）
            cocoon_rect = (center - size//3, center - size//2, size*2//3, size)
            pygame.draw.ellipse(self.image, (*color, 200), cocoon_rect)
            pygame.draw.ellipse(self.image, (120, 120, 180), cocoon_rect, 3)
            # 束缚线（4条）
            for i in range(4):
                line_x = center - size//4 + i * size//6
                pygame.draw.line(self.image, (80, 80, 130), (line_x, center - size//2), (line_x, center + size//2), 2)
            # 虚空核心
            pygame.draw.circle(self.image, (50, 50, 100), (center, center), size//8)
            # 扭曲环
            for i in range(2):
                wave_r = size//6 + i * size//8
                pygame.draw.circle(self.image, (*color, 150 - i * 50), (center, center), wave_r, 2)
            self.speed = -11
        
        elif "time_thread" in effects or "slow_field" in effects:
            # 时间丝线
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 时钟圆盘
            pygame.draw.circle(self.image, (200, 200, 240), (center, center), size//3, 3)
            # 时钟刻度（8个）
            for i in range(8):
                angle = (i * 45 - 90) * 3.14159 / 180
                x1 = center + int(size//4 * math.cos(angle))
                y1 = center + int(size//4 * math.sin(angle))
                x2 = center + int(size//3 * math.cos(angle))
                y2 = center + int(size//3 * math.sin(angle))
                width = 2 if i % 2 == 0 else 1
                pygame.draw.line(self.image, (160, 160, 200), (x1, y1), (x2, y2), width)
            # 时针
            time_angle = 0
            needle_x = center + int(size//4 * math.cos(time_angle))
            needle_y = center + int(size//4 * math.sin(time_angle))
            pygame.draw.line(self.image, (100, 100, 150), (center, center), (needle_x, needle_y), 3)
            # 时间波纹
            for i in range(2):
                wave_r = size//2 + i * size//6
                pygame.draw.circle(self.image, (*color, 150 - i * 50), (center, center), wave_r, 2)
            self.speed = -12
        
        elif "quantum_tangle" in effects or "entangle_web" in effects:
            # 量子纠缠
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 中心核
            pygame.draw.circle(self.image, (150, 220, 255), (center, center), size//6)
            pygame.draw.circle(self.image, color, (center, center), size//8)
            # 量子粒子（4个）
            particles = []
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                px = center + int(size//2.5 * math.cos(angle))
                py = center + int(size//2.5 * math.sin(angle))
                particles.append((px, py))
                pygame.draw.circle(self.image, (100, 180, 255), (px, py), size//12)
            # 纠缠连线
            for i in range(len(particles)):
                for j in range(i + 1, len(particles)):
                    pygame.draw.line(self.image, (*color, 150), particles[i], particles[j], 1)
            self.speed = -14
        
        elif "shadow_weave" in effects or "dark_web" in effects:
            # 暗影编织
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 暗影中心
            pygame.draw.circle(self.image, (30, 30, 60), (center, center), size//5)
            pygame.draw.circle(self.image, color, (center, center), size//6)
            # 暗影射线（8条）
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                length = size//2 + (i % 2) * size//6
                x1 = center + int(size//6 * math.cos(angle))
                y1 = center + int(size//6 * math.sin(angle))
                x2 = center + int(length * math.cos(angle))
                y2 = center + int(length * math.sin(angle))
                pygame.draw.line(self.image, (*color, 180), (x1, y1), (x2, y2), 2)
            # 暗影粒子
            import random
            random.seed(456)
            for _ in range(6):
                sx = center + random.randint(-size//2, size//2)
                sy = center + random.randint(-size//2, size//2)
                pygame.draw.circle(self.image, (30, 30, 60, 150), (sx, sy), size//20)
            self.speed = -15
        
        elif "cosmic_web" in effects or "fate_thread" in effects:
            # 宇宙丝线
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 宇宙中心
            pygame.draw.circle(self.image, (120, 170, 220), (center, center), size//6)
            pygame.draw.circle(self.image, color, (center, center), size//8)
            # 星系节点（6个）
            nodes = []
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                nx = center + int(size//2.5 * math.cos(angle))
                ny = center + int(size//2.5 * math.sin(angle))
                nodes.append((nx, ny))
                pygame.draw.circle(self.image, (80, 130, 180), (nx, ny), size//15)
                # 星光闪烁
                for j in range(4):
                    star_angle = (j * 90) * 3.14159 / 180
                    sx = nx + int(size//10 * math.cos(star_angle))
                    sy = ny + int(size//10 * math.sin(star_angle))
                    pygame.draw.line(self.image, (150, 200, 255), (nx, ny), (sx, sy), 1)
            # 命运之线连接
            for i, (nx, ny) in enumerate(nodes):
                pygame.draw.line(self.image, (100, 150, 200), (center, center), (nx, ny), 2)
                next_node = nodes[(i + 1) % len(nodes)]
                pygame.draw.line(self.image, (*color, 150), (nx, ny), next_node, 1)
            self.speed = -13
        
        # ========== Solar 子弹 ==========
        elif "solar_flare" in effects or "light_burst" in effects:
            # 太阳耀斑
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 太阳核心
            pygame.draw.circle(self.image, (255, 255, 100), (center, center), size//5)
            pygame.draw.circle(self.image, color, (center, center), size//6)
            # 耀斑射线（12条）
            for i in range(12):
                angle = (i * 30) * 3.14159 / 180
                length = size//2 if i % 2 == 0 else size//1.5
                x1 = center + int(size//6 * math.cos(angle))
                y1 = center + int(size//6 * math.sin(angle))
                x2 = center + int(length * math.cos(angle))
                y2 = center + int(length * math.sin(angle))
                pygame.draw.line(self.image, (255, 220, 0), (x1, y1), (x2, y2), 3)
            # 光晕
            for i in range(2):
                halo_r = size//4 + i * size//8
                pygame.draw.circle(self.image, (*color, 180 - i * 80), (center, center), halo_r)
            self.speed = -17
        
        elif "corona_ring" in effects or "plasma_loop" in effects:
            # 日冕光环
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 中心
            pygame.draw.circle(self.image, (255, 200, 0), (center, center), size//6)
            # 日冕环（2层）
            for i in range(2):
                ring_r = size//3 + i * size//6
                ring_color = (255, 180 - i * 30, 0)
                pygame.draw.circle(self.image, (*ring_color, 200 - i * 60), (center, center), ring_r, 4)
            # 等离子弧（3个）
            for i in range(3):
                angle = (i * 120) * 3.14159 / 180
                arc_points = []
                for a in range(8):
                    arc_angle = angle + (a - 4) * 0.1
                    px = center + int(size//2 * math.cos(arc_angle))
                    py = center + int(size//2 * math.sin(arc_angle))
                    arc_points.append((px, py))
                if len(arc_points) > 1:
                    pygame.draw.lines(self.image, (255, 150, 0), False, arc_points, 3)
            self.speed = -15
        
        elif "prominence_jet" in effects or "flame_tongue" in effects:
            # 日珥喷发
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 太阳主体
            pygame.draw.circle(self.image, (255, 120, 0), (center, center), size//4)
            # 火焰喷射（4条）
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                flame_points = []
                for j in range(6):
                    radius = size//4 + j * size//12
                    wave_offset = int(size//15 * math.sin(j * 0.5))
                    fx = center + int(radius * math.cos(angle)) + wave_offset
                    fy = center + int(radius * math.sin(angle))
                    flame_points.append((fx, fy))
                if len(flame_points) > 1:
                    pygame.draw.lines(self.image, (255, 200, 0), False, flame_points, 4)
                    pygame.draw.lines(self.image, (255, 100, 0), False, flame_points, 2)
            self.speed = -16
        
        elif "sunspot_vortex" in effects or "magnetic_storm" in effects:
            # 太阳黑子
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 黑子核心
            pygame.draw.circle(self.image, (100, 50, 0), (center, center), size//5)
            pygame.draw.circle(self.image, color, (center, center), size//6)
            # 磁力线漩涡（2条）
            for arm in range(2):
                spiral_points = []
                arm_offset = arm * 180
                for i in range(10):
                    angle = (i * 36 + arm_offset) * 3.14159 / 180
                    radius = size//8 + i * size//25
                    sx = center + int(radius * math.cos(angle))
                    sy = center + int(radius * math.sin(angle))
                    spiral_points.append((sx, sy))
                if len(spiral_points) > 1:
                    pygame.draw.lines(self.image, (255, 150, 0), False, spiral_points, 3)
            # 磁暴环
            for i in range(2):
                storm_r = size//3 + i * size//5
                pygame.draw.circle(self.image, (255, 100, 0, 160 - i * 80), (center, center), storm_r, 3)
            self.speed = -14
        
        elif "fusion_core" in effects or "nuclear_pulse" in effects:
            # 核聚变核
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 聚变核心
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//8)
            pygame.draw.circle(self.image, (255, 255, 200), (center, center), size//6)
            pygame.draw.circle(self.image, color, (center, center), size//5)
            # 能量环（3层）
            for i in range(3):
                pulse_r = size//4 + i * size//6
                pygame.draw.circle(self.image, (255, 255, 100, 200 - i * 50), (center, center), pulse_r, 3)
            # 聚变粒子
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                particle_r = size//3
                px = center + int(particle_r * math.cos(angle))
                py = center + int(particle_r * math.sin(angle))
                pygame.draw.circle(self.image, (255, 255, 150), (px, py), size//20)
            self.speed = -18
        
        elif "photon_stream" in effects or "light_particle" in effects:
            # 光子流束
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 光源核心
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//8)
            pygame.draw.circle(self.image, color, (center, center), size//10)
            # 光子粒子流（螺旋）
            for stream in range(3):
                stream_offset = stream * 120
                for i in range(10):
                    angle = (i * 36 + stream_offset) * 3.14159 / 180
                    radius = size//6 + i * size//25
                    px = center + int(radius * math.cos(angle))
                    py = center + int(radius * math.sin(angle))
                    particle_size = size//15 - i // 4
                    if particle_size > 0:
                        pygame.draw.circle(self.image, (255, 255, 220), (px, py), particle_size)
            self.speed = -16
        
        elif "supernova_burst" in effects or "stellar_explosion" in effects:
            # 超新星爆发
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 超新星核心
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//10)
            pygame.draw.circle(self.image, (255, 100, 0), (center, center), size//8)
            pygame.draw.circle(self.image, color, (center, center), size//6)
            # 爆炸波（2层）
            for i in range(2):
                blast_r = size//3 + i * size//4
                blast_color = [(255, 0, 0), (255, 150, 0)][i]
                pygame.draw.circle(self.image, (*blast_color, 220 - i * 80), (center, center), blast_r, 4)
            # 爆炸碎片（8个）
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                debris_r = size//2
                dx = center + int(debris_r * math.cos(angle))
                dy = center + int(debris_r * math.sin(angle))
                pygame.draw.circle(self.image, (255, 150, 0), (dx, dy), size//12)
            self.speed = -19
        
        # ========== Arbiter 子弹 ==========
        elif "quant_cube" in effects or "quantum_matrix" in effects:
            # 量子立方
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            cube_size = size//2
            # 主立方
            pygame.draw.rect(self.image, color, (center - cube_size//2, center - cube_size//2, cube_size, cube_size), 3)
            # 透视立方
            offset = size//6
            back_rect = (center - cube_size//2 + offset, center - cube_size//2 - offset, cube_size, cube_size)
            pygame.draw.rect(self.image, (150, 80, 200), back_rect, 2)
            # 连接线
            corners = [
                (center - cube_size//2, center - cube_size//2),
                (center + cube_size//2, center - cube_size//2),
                (center + cube_size//2, center + cube_size//2),
                (center - cube_size//2, center + cube_size//2)
            ]
            back_corners = [
                (center - cube_size//2 + offset, center - cube_size//2 - offset),
                (center + cube_size//2 + offset, center - cube_size//2 - offset),
                (center + cube_size//2 + offset, center + cube_size//2 - offset),
                (center - cube_size//2 + offset, center + cube_size//2 - offset)
            ]
            for i in range(4):
                pygame.draw.line(self.image, (120, 60, 180), corners[i], back_corners[i], 1)
            # 量子粒子
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                px = center + int(size//4 * math.cos(angle))
                py = center + int(size//4 * math.sin(angle))
                pygame.draw.circle(self.image, (200, 150, 255), (px, py), size//25)
            self.speed = -14
        
        elif "fractal_shard" in effects or "split_multiply" in effects:
            # 分形碎片
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 主三角形
            main_triangle = [
                (center, center - size//2),
                (center - size//2, center + size//2),
                (center + size//2, center + size//2)
            ]
            pygame.draw.polygon(self.image, color, main_triangle, 3)
            # 子三角形
            for i in range(3):
                angle = (i * 120) * 3.14159 / 180
                fx = center + int(size//3 * math.cos(angle))
                fy = center + int(size//3 * math.sin(angle))
                sub_triangle = [
                    (fx, fy - size//6),
                    (fx - size//6, fy + size//6),
                    (fx + size//6, fy + size//6)
                ]
                pygame.draw.polygon(self.image, (180, 100, 230), sub_triangle, 2)
            # 分裂线
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                x1 = center + int(size//8 * math.cos(angle))
                y1 = center + int(size//8 * math.sin(angle))
                x2 = center + int(size//2 * math.cos(angle))
                y2 = center + int(size//2 * math.sin(angle))
                pygame.draw.line(self.image, (*color, 150), (x1, y1), (x2, y2), 1)
            self.speed = -15
        
        elif "tesseract" in effects or "hypercube_projection" in effects:
            # 四维超立方
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 内立方
            inner_size = size//3
            inner_rect = (center - inner_size//2, center - inner_size//2, inner_size, inner_size)
            pygame.draw.rect(self.image, (150, 100, 220), inner_rect, 3)
            # 外立方
            outer_size = size//1.5
            outer_rect = (center - outer_size//2, center - outer_size//2, outer_size, outer_size)
            pygame.draw.rect(self.image, color, outer_rect, 3)
            # 连接线
            inner_corners = [
                (center - inner_size//2, center - inner_size//2),
                (center + inner_size//2, center - inner_size//2),
                (center + inner_size//2, center + inner_size//2),
                (center - inner_size//2, center + inner_size//2)
            ]
            outer_corners = [
                (center - outer_size//2, center - outer_size//2),
                (center + outer_size//2, center - outer_size//2),
                (center + outer_size//2, center + outer_size//2),
                (center - outer_size//2, center + outer_size//2)
            ]
            for i in range(4):
                pygame.draw.line(self.image, (180, 120, 240), inner_corners[i], outer_corners[i], 2)
            self.speed = -16
        
        elif "matrix_rain" in effects or "code_cascade" in effects:
            # 矩阵代码雨
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 背景
            pygame.draw.rect(self.image, (0, 50, 20, 180), (0, 0, size*2, size*2))
            # 代码流
            import random
            random.seed(789)
            for i in range(6):
                line_x = center - size//2 + i * size//3
                for j in range(5):
                    code_y = center - size//2 + j * size//5
                    brightness = 100 + (j * 30)
                    char_size = size//20
                    pygame.draw.rect(self.image, (0, brightness, 50), (line_x - char_size//2, code_y - char_size//2, char_size, char_size))
            # 矩阵光芒
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                x1 = center + int(size//6 * math.cos(angle))
                y1 = center + int(size//6 * math.sin(angle))
                x2 = center + int(size//2 * math.cos(angle))
                y2 = center + int(size//2 * math.sin(angle))
                pygame.draw.line(self.image, (0, 255, 100), (x1, y1), (x2, y2), 2)
            self.speed = -13
        
        elif "geometric_wave" in effects or "angular_ripple" in effects:
            # 几何波纹
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 六边形
            hex_points = []
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                px = center + int(size//4 * math.cos(angle))
                py = center + int(size//4 * math.sin(angle))
                hex_points.append((px, py))
            pygame.draw.polygon(self.image, color, hex_points, 3)
            # 波纹环（2层）
            for i in range(2):
                wave_r = size//3 + i * size//8
                wave_hex = []
                for j in range(6):
                    angle = (j * 60) * 3.14159 / 180
                    px = center + int(wave_r * math.cos(angle))
                    py = center + int(wave_r * math.sin(angle))
                    wave_hex.append((px, py))
                if len(wave_hex) > 1:
                    pygame.draw.lines(self.image, (*color, 200 - i * 80), True, wave_hex, 2)
            self.speed = -14
        
        elif "quantum_entangle" in effects or "spooky_action" in effects:
            # 量子纠缠网
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 中心核
            pygame.draw.circle(self.image, (255, 150, 255), (center, center), size//8)
            pygame.draw.circle(self.image, color, (center, center), size//10)
            # 纠缠粒子（6个）
            particles = []
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                px = center + int(size//2.5 * math.cos(angle))
                py = center + int(size//2.5 * math.sin(angle))
                particles.append((px, py))
                pygame.draw.circle(self.image, (200, 100, 220), (px, py), size//15)
            # 纠缠连线
            for i in range(len(particles)):
                opposite = (i + 3) % len(particles)
                pygame.draw.line(self.image, (*color, 150), particles[i], particles[opposite], 2)
            self.speed = -15
        
        elif "collapse_star" in effects or "wavefunction_collapse" in effects:
            # 波函数坍缩
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 多重态（4个重影）
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                spread = size//4
                sx = center + int(spread * math.cos(angle))
                sy = center + int(spread * math.sin(angle))
                pygame.draw.circle(self.image, (*color, 120), (sx, sy), size//12)
            # 确定态
            pygame.draw.circle(self.image, (220, 180, 255), (center, center), size//7)
            pygame.draw.circle(self.image, color, (center, center), size//8)
            # 坍缩波
            for i in range(2):
                wave_r = size//4 + i * size//8
                pygame.draw.circle(self.image, (*color, 180 - i * 80), (center, center), wave_r, 2)
            self.speed = -16
        
        # ========== Eclipse 子弹 ==========
        elif "dual_core" in effects or "sync_resonance" in effects:
            # 双核心共振
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            core_offset = size//4
            # 左核心
            left_x = center - core_offset
            pygame.draw.circle(self.image, (100, 50, 180), (left_x, center), size//6)
            pygame.draw.circle(self.image, color, (left_x, center), size//8)
            # 右核心
            right_x = center + core_offset
            pygame.draw.circle(self.image, (150, 80, 220), (right_x, center), size//6)
            pygame.draw.circle(self.image, color, (right_x, center), size//8)
            # 共振线
            pygame.draw.line(self.image, (200, 100, 255), (left_x, center), (right_x, center), 3)
            # 能量环
            for i in range(2):
                ring_r = size//3 + i * size//8
                pygame.draw.circle(self.image, (*color, 180 - i * 80), (center, center), ring_r, 2)
            self.speed = -15
        
        elif "shadow_eclipse" in effects or "lunar_devour" in effects:
            # 影蚀之月
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 月盘
            pygame.draw.circle(self.image, (180, 180, 200), (center, center), size//3)
            # 影子侵蚀
            shadow_x = center - size//6
            pygame.draw.circle(self.image, (30, 20, 50), (shadow_x, center), size//3)
            # 边缘光晕
            pygame.draw.circle(self.image, color, (center, center), size//3, 3)
            # 日冕效果
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                x1 = center + int(size//3 * math.cos(angle))
                y1 = center + int(size//3 * math.sin(angle))
                x2 = center + int(size//2 * math.cos(angle))
                y2 = center + int(size//2 * math.sin(angle))
                pygame.draw.line(self.image, (120, 80, 160), (x1, y1), (x2, y2), 2)
            self.speed = -14
        
        elif "corona_burst" in effects or "eclipse_ring" in effects:
            # 日冕爆发
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 日食主体
            pygame.draw.circle(self.image, (50, 30, 80), (center, center), size//4)
            # 日冕环（2层）
            for i in range(2):
                ring_r = size//3 + i * size//6
                ring_color = (100 + i * 40, 50 + i * 30, 180 + i * 30)
                pygame.draw.circle(self.image, (*ring_color, 200 - i * 80), (center, center), ring_r, 3)
            # 爆发射线（8条）
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                length = size//3 if i % 2 == 0 else size//2
                x1 = center + int(size//4 * math.cos(angle))
                y1 = center + int(size//4 * math.sin(angle))
                x2 = center + int(length * math.cos(angle))
                y2 = center + int(length * math.sin(angle))
                pygame.draw.line(self.image, (200, 100, 255), (x1, y1), (x2, y2), 2)
            self.speed = -16
        
        elif "void_mirror" in effects or "shadow_clone" in effects:
            # 虚空镜像
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 主体
            pygame.draw.circle(self.image, color, (center, center), size//5)
            pygame.draw.circle(self.image, (150, 100, 200), (center, center), size//6)
            # 镜像（4个）
            mirror_offsets = [(0, -size//3), (size//3, 0), (0, size//3), (-size//3, 0)]
            for i, (dx, dy) in enumerate(mirror_offsets):
                mirror_x = center + dx
                mirror_y = center + dy
                pygame.draw.circle(self.image, (*color, 150 - i * 20), (mirror_x, mirror_y), size//10)
            # 连接线
            for dx, dy in mirror_offsets:
                mirror_x = center + dx
                mirror_y = center + dy
                pygame.draw.line(self.image, (*color, 100), (center, center), (mirror_x, mirror_y), 1)
            self.speed = -13
        
        elif "twilight_zone" in effects or "dusk_dawn_edge" in effects:
            # 黄昏地带
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 渐变背景
            for i in range(15):
                gradient_y = center - size//2 + i * size//8
                brightness = 200 - i * 13
                gradient_color = (brightness, brightness//2, brightness + 55)
                pygame.draw.line(self.image, gradient_color, 
                               (center - size//2, gradient_y),
                               (center + size//2, gradient_y), size//8)
            # 边界线
            pygame.draw.line(self.image, color, (center - size//2, center), (center + size//2, center), 4)
            # 光暗粒子
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                px = center + int(size//3 * math.cos(angle))
                py = center + int(size//3 * math.sin(angle))
                particle_color = (200, 150, 250) if py < center else (50, 30, 100)
                pygame.draw.circle(self.image, particle_color, (px, py), size//18)
            self.speed = -14
        
        elif "dark_matter" in effects or "invisible_mass" in effects:
            # 暗物质弹
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 扭曲波纹
            for i in range(3):
                wave_r = size//6 + i * size//10
                pygame.draw.circle(self.image, (*color, 150 - i * 40), (center, center), wave_r, 2)
            # 暗物质核心
            pygame.draw.circle(self.image, (50, 20, 100), (center, center), size//8)
            pygame.draw.circle(self.image, (*color, 100), (center, center), size//6)
            # 引力扭曲线
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                x1 = center + int(size//4 * math.cos(angle))
                y1 = center + int(size//4 * math.sin(angle))
                x2 = center + int(size//2 * math.cos(angle + 0.3))
                y2 = center + int(size//2 * math.sin(angle + 0.3))
                pygame.draw.line(self.image, (*color, 120), (x1, y1), (x2, y2), 1)
            self.speed = -12
        
        elif "black_sun" in effects or "anti_radiance" in effects:
            # 黑日降临
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 黑色核心
            pygame.draw.circle(self.image, (20, 10, 30), (center, center), size//4)
            pygame.draw.circle(self.image, color, (center, center), size//5)
            # 反光环
            for i in range(2):
                halo_r = size//3 + i * size//8
                pygame.draw.circle(self.image, (50, 20, 80, 180 - i * 70), (center, center), halo_r, 4)
            # 反向射线（12条）
            for i in range(12):
                angle = (i * 30) * 3.14159 / 180
                x1 = center + int(size//2 * math.cos(angle))
                y1 = center + int(size//2 * math.sin(angle))
                x2 = center + int(size//4 * math.cos(angle))
                y2 = center + int(size//4 * math.sin(angle))
                pygame.draw.line(self.image, (80, 30, 120), (x1, y1), (x2, y2), 2)
            # 暗能量粒子
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                px = center + int(size//2.5 * math.cos(angle))
                py = center + int(size//2.5 * math.sin(angle))
                pygame.draw.circle(self.image, (100, 30, 150), (px, py), size//20)
            self.speed = -17
        
        # ========== Prism 子弹 ==========
        elif "rainbow_ray" in effects or "spectrum_split" in effects:
            # 彩虹射线
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            rainbow_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]
            # 彩虹射线
            for i, ray_color in enumerate(rainbow_colors):
                angle = (i * 51.4) * 3.14159 / 180
                x1 = center + int(size//8 * math.cos(angle))
                y1 = center + int(size//8 * math.sin(angle))
                x2 = center + int(size//2 * math.cos(angle))
                y2 = center + int(size//2 * math.sin(angle))
                pygame.draw.line(self.image, ray_color, (x1, y1), (x2, y2), 3)
            # 中心白光
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//8)
            pygame.draw.circle(self.image, color, (center, center), size//10)
            self.speed = -16
        
        elif "crystal_shard" in effects or "prism_fragment" in effects:
            # 水晶碎片
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 中心水晶
            crystal_points = [(center, center - size//2), (center + size//3, center), (center, center + size//2), (center - size//3, center)]
            pygame.draw.polygon(self.image, (200, 240, 255), crystal_points)
            pygame.draw.polygon(self.image, color, crystal_points, 3)
            # 碎片（4个）
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                sx = center + int(size//2.5 * math.cos(angle))
                sy = center + int(size//2.5 * math.sin(angle))
                shard_points = [(sx, sy - size//8), (sx + size//12, sy + size//12), (sx - size//12, sy + size//12)]
                pygame.draw.polygon(self.image, (150, 220, 255), shard_points)
            self.speed = -15
        
        elif "refraction_beam" in effects or "light_bend" in effects:
            # 折射光束
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 光源
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//8)
            pygame.draw.circle(self.image, color, (center, center), size//10)
            # 折射光束（3条）
            for i in range(3):
                beam_angle = (i * 120) * 3.14159 / 180
                beam_points = []
                for j in range(6):
                    radius = size//8 + j * size//15
                    curve_offset = int(size//12 * math.sin(j * 0.5))
                    bx = center + int(radius * math.cos(beam_angle)) + curve_offset
                    by = center + int(radius * math.sin(beam_angle))
                    beam_points.append((bx, by))
                if len(beam_points) > 1:
                    pygame.draw.lines(self.image, (200, 230, 255), False, beam_points, 3)
            self.speed = -14
        
        elif "laser_prism" in effects or "triangular_prism" in effects:
            # 激光棱镜
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 棱镜（三角形）
            prism_triangle = [(center, center - size//3), (center + size//3, center + size//3), (center - size//3, center + size//3)]
            pygame.draw.polygon(self.image, (180, 230, 255), prism_triangle)
            pygame.draw.polygon(self.image, color, prism_triangle, 3)
            # 入射光
            pygame.draw.line(self.image, (255, 255, 255), (center - size//2, center - size//4), (center - size//6, center), 3)
            # 分光
            spectrum_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            for i, spec_color in enumerate(spectrum_colors):
                angle = -15 + i * 15
                rad = angle * 3.14159 / 180
                x2 = center + int(size//2 * math.cos(rad))
                y2 = center + int(size//2 * math.sin(rad))
                pygame.draw.line(self.image, spec_color, (center + size//6, center), (x2, y2), 2)
            self.speed = -15
        
        elif "aurora_split" in effects or "northern_light" in effects:
            # 极光分裂
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 极光波纹（3层）
            aurora_colors = [(0, 255, 200), (100, 255, 150), (150, 255, 200)]
            for i in range(3):
                wave_y = center - size//3 + i * size//3
                wave_points = []
                for j in range(8):
                    wx = center - size//2 + j * size//7
                    wy = wave_y + int(size//10 * math.sin(j * 0.8))
                    wave_points.append((wx, wy))
                if len(wave_points) > 1:
                    pygame.draw.lines(self.image, (*aurora_colors[i], 200 - i * 50), False, wave_points, 2)
            # 中心光球
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//8)
            pygame.draw.circle(self.image, color, (center, center), size//10)
            self.speed = -16
        
        elif "hologram" in effects or "3d_projection" in effects:
            # 全息投影
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 全息网格
            for i in range(6):
                y_pos = center - size//2 + i * size//5
                pygame.draw.line(self.image, (*color, 120), (center - size//2, y_pos), (center + size//2, y_pos), 1)
                x_pos = center - size//2 + i * size//5
                pygame.draw.line(self.image, (*color, 120), (x_pos, center - size//2), (x_pos, center + size//2), 1)
            # 3D立方体
            cube_size = size//4
            pygame.draw.rect(self.image, color, (center - cube_size//2, center - cube_size//2, cube_size, cube_size), 2)
            offset = size//8
            pygame.draw.rect(self.image, (150, 200, 255), (center - cube_size//2 + offset, center - cube_size//2 - offset, cube_size, cube_size), 2)
            # 连接线
            corners = [(center - cube_size//2, center - cube_size//2), (center + cube_size//2, center - cube_size//2)]
            back_corners = [(center - cube_size//2 + offset, center - cube_size//2 - offset), (center + cube_size//2 + offset, center - cube_size//2 - offset)]
            for i in range(2):
                pygame.draw.line(self.image, (120, 180, 240), corners[i], back_corners[i], 1)
            self.speed = -14
        
        elif "lens_flare" in effects or "optical_burst" in effects:
            # 镜头光晕
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 主光源
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//6)
            pygame.draw.circle(self.image, color, (center, center), size//8)
            # 光晕环（3层）
            for i in range(3):
                flare_r = size//5 + i * size//10
                pygame.draw.circle(self.image, (255, 255, 255, 200 - i * 50), (center, center), flare_r)
            # 光斑（4个）
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                spot_x = center + int(size//2.5 * math.cos(angle))
                spot_y = center + int(size//2.5 * math.sin(angle))
                pygame.draw.circle(self.image, (*color, 180), (spot_x, spot_y), size//15)
            # 十字光芒
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                x1 = center + int(size//8 * math.cos(angle))
                y1 = center + int(size//8 * math.sin(angle))
                x2 = center + int(size//1.5 * math.cos(angle))
                y2 = center + int(size//1.5 * math.sin(angle))
                pygame.draw.line(self.image, (255, 255, 200), (x1, y1), (x2, y2), 3)
            self.speed = -17
        
        # ========== Necro 子弹 ==========
        elif "soul_reaper" in effects or "death_scythe" in effects:
            # 灵魂收割
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 镰刀刃
            scythe_blade = [(center - size//6, center - size//3), (center + size//3, center - size//6), (center + size//4, center + size//8), (center - size//4, center)]
            pygame.draw.polygon(self.image, (200, 200, 220), scythe_blade)
            pygame.draw.polygon(self.image, color, scythe_blade, 3)
            # 镰刀柄
            pygame.draw.line(self.image, (100, 50, 80), (center, center), (center - size//4, center + size//2), 4)
            # 灵魂漩涡（4个）
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                sx = center + int(size//3 * math.cos(angle))
                sy = center + int(size//3 * math.sin(angle))
                pygame.draw.circle(self.image, (*color, 200 - i * 40), (sx, sy), size//20)
            self.speed = -15
        
        elif "blood_curse" in effects or "vampire_drain" in effects:
            # 鲜血诅咒
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 血滴核心
            pygame.draw.circle(self.image, (180, 0, 80), (center, center), size//4)
            pygame.draw.circle(self.image, color, (center, center), size//5)
            # 血滴形状
            drop_points = []
            for i in range(12):
                angle = (i * 30 - 90) * 3.14159 / 180
                radius = size//3 if i < 6 else size//4
                px = center + int(radius * math.cos(angle))
                py = center + int(radius * math.sin(angle))
                drop_points.append((px, py))
            if len(drop_points) > 2:
                pygame.draw.polygon(self.image, (200, 0, 100, 180), drop_points)
                pygame.draw.lines(self.image, color, True, drop_points, 2)
            # 吸血触手（4条）
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                tendril_points = []
                for j in range(4):
                    radius = size//5 + j * size//12
                    tx = center + int(radius * math.cos(angle))
                    ty = center + int(radius * math.sin(angle))
                    tendril_points.append((tx, ty))
                if len(tendril_points) > 1:
                    pygame.draw.lines(self.image, (150, 0, 70), False, tendril_points, 2)
            self.speed = -14
        
        elif "bone_spike" in effects or "skeletal_weapon" in effects:
            # 白骨尖刺
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 骨刺主体
            spike_points = [(center, center - size//2), (center + size//8, center + size//2), (center - size//8, center + size//2)]
            pygame.draw.polygon(self.image, (220, 220, 220), spike_points)
            pygame.draw.polygon(self.image, color, spike_points, 3)
            # 骨节（3条横纹）
            for i in range(3):
                node_y = center - size//3 + i * size//4
                node_width = size//6 - i * size//30
                pygame.draw.line(self.image, (180, 180, 180), (center - node_width, node_y), (center + node_width, node_y), 2)
            # 骨刺尖端
            pygame.draw.circle(self.image, (255, 255, 255), (center, center - size//2), size//12)
            self.speed = -16
        
        elif "plague_cloud" in effects or "pestilence_mist" in effects:
            # 瘟疫之云
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 毒雾核心
            pygame.draw.circle(self.image, (100, 150, 50), (center, center), size//5)
            pygame.draw.circle(self.image, color, (center, center), size//6)
            # 毒雾扩散（8个云团）
            import random
            random.seed(567)
            for i in range(8):
                angle = (i * 45 + random.randint(-10, 10)) * 3.14159 / 180
                cloud_r = size//4 + random.randint(0, size//10)
                cx = center + int(cloud_r * math.cos(angle))
                cy = center + int(cloud_r * math.sin(angle))
                cloud_size = size//12
                pygame.draw.circle(self.image, (120, 180, 60, 150), (cx, cy), cloud_size)
            # 病毒粒子（6个）
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                px = center + int(size//3 * math.cos(angle))
                py = center + int(size//3 * math.sin(angle))
                pygame.draw.line(self.image, (80, 120, 40), (px - size//25, py), (px + size//25, py), 2)
                pygame.draw.line(self.image, (80, 120, 40), (px, py - size//25), (px, py + size//25), 2)
            self.speed = -13
        
        elif "death_mark" in effects or "doom_sigil" in effects:
            # 死亡印记
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 符文圆环
            pygame.draw.circle(self.image, color, (center, center), size//3, 3)
            pygame.draw.circle(self.image, (150, 0, 100), (center, center), size//4, 2)
            # 五角星
            star_points = []
            for i in range(5):
                angle = (i * 72 - 90) * 3.14159 / 180
                px = center + int(size//4 * math.cos(angle))
                py = center + int(size//4 * math.sin(angle))
                star_points.append((px, py))
            if len(star_points) == 5:
                pygame.draw.line(self.image, color, star_points[0], star_points[2], 3)
                pygame.draw.line(self.image, color, star_points[2], star_points[4], 3)
                pygame.draw.line(self.image, color, star_points[4], star_points[1], 3)
                pygame.draw.line(self.image, color, star_points[1], star_points[3], 3)
                pygame.draw.line(self.image, color, star_points[3], star_points[0], 3)
            self.speed = -15
        
        elif "ghost_chain" in effects or "spectral_shackle" in effects:
            # 幽灵锁链
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 锁链中心
            pygame.draw.circle(self.image, (120, 80, 150), (center, center), size//6)
            pygame.draw.circle(self.image, color, (center, center), size//8)
            # 锁链（4条）
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                chain_points = []
                for j in range(4):
                    radius = size//8 + j * size//12
                    cx = center + int(radius * math.cos(angle))
                    cy = center + int(radius * math.sin(angle))
                    chain_points.append((cx, cy))
                if len(chain_points) > 1:
                    pygame.draw.lines(self.image, (100, 70, 130), False, chain_points, 3)
                    # 锁链节点
                    for cx, cy in chain_points[::2]:
                        pygame.draw.circle(self.image, (150, 100, 180), (cx, cy), size//25)
            # 枷锁环（4个）
            for i in range(4):
                angle = (i * 90 + 45) * 3.14159 / 180
                ring_x = center + int(size//2.5 * math.cos(angle))
                ring_y = center + int(size//2.5 * math.sin(angle))
                pygame.draw.circle(self.image, (140, 90, 160), (ring_x, ring_y), size//15, 2)
            self.speed = -14
        
        elif "necrotic_burst" in effects or "undead_explosion" in effects:
            # 死灵爆发
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 死灵核心
            pygame.draw.circle(self.image, (180, 50, 120), (center, center), size//5)
            pygame.draw.circle(self.image, color, (center, center), size//6)
            # 爆发波（2层）
            for i in range(2):
                burst_r = size//4 + i * size//6
                burst_colors = [(150, 0, 100), (200, 80, 140)]
                pygame.draw.circle(self.image, (*burst_colors[i], 200 - i * 80), (center, center), burst_r, 3)
            # 死灵能量（6个骷髅简化）
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                skull_r = size//3
                sx = center + int(skull_r * math.cos(angle))
                sy = center + int(skull_r * math.sin(angle))
                skull_size = size//15
                # 简化骷髅
                pygame.draw.circle(self.image, (200, 200, 200), (sx, sy), skull_size)
                pygame.draw.circle(self.image, (0, 0, 0), (sx - skull_size//3, sy - skull_size//4), skull_size//5)
                pygame.draw.circle(self.image, (0, 0, 0), (sx + skull_size//3, sy - skull_size//4), skull_size//5)
            self.speed = -17
        
        elif "void_rift" in effects:
            # 虚空裂缝
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 裂缝
            rift = [
                (center, center - size),
                (center - size//6, center - size//4),
                (center + size//8, center + size//6),
                (center, center + size)
            ]
            pygame.draw.lines(self.image, (150, 0, 200), False, rift, 3)
            # 虚空核心
            for r in range(size//2, 0, -size//8):
                alpha = int(180 * (1 - r / (size//2)))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (center, center), r)
                self.image.blit(temp_surf, (0, 0))
            self.speed = -16
            
        else:
            # 默认子弹
            self.image = pygame.Surface((size, size*2), pygame.SRCALPHA)
            pygame.draw.rect(self.image, color, (size//4, 0, size//2, size*2))
            pygame.draw.circle(self.image, (255, 255, 255), (size//2, size//2), size//4)
            self.speed = -15

    def update(self):
        self.timer += 1
        
        # 【改进】时间冻结时跳过移动
        if self.frozen:
            return
        
        # 动态子弹效果 - 每5帧重新渲染以优化性能
        if hasattr(self, 'effects') and self.timer % 5 == 0:
            self._update_bullet_animation()
        
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
    
    def _update_bullet_animation(self):
        """更新子弹动画效果"""
        if not hasattr(self, 'effects'):
            return
            
        effects = self.effects
        color = self.bullet_color
        size = 8
        
        # 时间参数
        t = self.timer * 0.1  # 减慢动画速度
        
        # 旋转粒子效果 (用于等离子、电弧、星爆等)
        if any(e in effects for e in ["plasma_ring", "arc_storm", "starburst", "solar_flare", 
                                       "cosmic_spiral", "void_rift", "quantum_flux"]):
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            
            # 核心
            pygame.draw.circle(self.image, color, (center, center), size//4)
            
            # 旋转粒子
            for i in range(6):
                angle = (i * 60 + t * 50) * 3.14159 / 180  # 旋转动画
                px = center + int(size * 0.7 * math.cos(angle))
                py = center + int(size * 0.7 * math.sin(angle))
                particle_color = tuple(min(255, c + 50) for c in color)
                pygame.draw.circle(self.image, particle_color, (px, py), size//6)
        
        # 脉冲效果 (用于能量波、震荡波等)
        elif any(e in effects for e in ["energy_pulse", "shockwave", "resonance", "temporal_wave"]):
            pulse = abs(math.sin(t)) * 0.3 + 0.7  # 0.7 到 1.0 的脉冲
            pulse_size = int(size * pulse)
            
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            
            # 脉冲圆环
            for r in range(3):
                radius = pulse_size + r * size//4
                alpha = int(255 * (1 - r / 3))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (center, center), radius, 2)
                self.image.blit(temp_surf, (0, 0))
            
            # 核心
            pygame.draw.circle(self.image, color, (center, center), pulse_size//2)
        
        # 火焰效果 (用于烈焰、地狱火等)
        elif any(e in effects for e in ["flame_burst", "inferno", "phoenix_fire"]):
            flicker = math.sin(t * 2) * 0.2 + 0.8  # 闪烁
            
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            
            # 火焰粒子
            for i in range(8):
                angle = (i * 45 + t * 30) * 3.14159 / 180
                dist = size * 0.6 * (1 + math.sin(t + i) * 0.2)  # 摇曳
                px = center + int(dist * math.cos(angle))
                py = center + int(dist * math.sin(angle))
                
                # 渐变火焰色
                flame_color = (
                    int(255 * flicker),
                    int(color[1] * flicker),
                    int(color[2] * 0.5 * flicker)
                )
                pygame.draw.circle(self.image, flame_color, (px, py), size//5)
            
            # 火焰核心
            core_color = tuple(min(255, c + 50) for c in color)
            pygame.draw.circle(self.image, core_color, (center, center), size//3)
        
        # 闪电效果 (用于雷暴、电弧等)
        elif any(e in effects for e in ["lightning", "thunder_strike", "storm_bolt"]):
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            
            # 电弧核心
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//4)
            pygame.draw.circle(self.image, color, (center, center), size//3, 2)
            
            # 动态电弧
            for i in range(4):
                angle = (i * 90 + t * 40) * 3.14159 / 180
                arc_len = size * 0.8 * (1 + math.sin(t * 2 + i) * 0.3)
                ex = center + int(arc_len * math.cos(angle))
                ey = center + int(arc_len * math.sin(angle))
                
                # 锯齿状电弧
                points = [(center, center)]
                steps = 3
                for j in range(steps):
                    progress = (j + 1) / steps
                    px = center + int((ex - center) * progress)
                    py = center + int((ey - center) * progress)
                    offset = int(math.sin(t * 3 + j) * size//5)
                    points.append((px + offset, py))
                
                if len(points) > 1:
                    pygame.draw.lines(self.image, color, False, points, 2)
        
        # 寒冰效果 (用于冰霜、极寒等)
        elif any(e in effects for e in ["frost", "blizzard", "frozen_heart"]):
            crystal_phase = t % (2 * 3.14159)
            
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            
            # 冰晶核心
            pygame.draw.circle(self.image, (200, 230, 255), (center, center), size//3)
            pygame.draw.circle(self.image, color, (center, center), size//4)
            
            # 旋转的冰晶尖刺
            for i in range(6):
                angle = (i * 60 + math.sin(crystal_phase) * 30) * 3.14159 / 180
                spike_len = size * 0.6
                sx = center + int(spike_len * math.cos(angle))
                sy = center + int(spike_len * math.sin(angle))
                pygame.draw.line(self.image, color, (center, center), (sx, sy), 2)
                pygame.draw.circle(self.image, (150, 200, 255), (sx, sy), size//8)
        
        # 暗影效果 (用于暗影箭、死亡印记等)
        elif any(e in effects for e in ["shadow_bolt", "death_mark", "doom_sigil"]):
            shadow_pulse = abs(math.sin(t * 1.5)) * 0.4 + 0.6
            
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            
            # 暗影光晕
            for r in range(3):
                radius = int(size * shadow_pulse) + r * size//5
                alpha = int(100 * (1 - r / 3))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (center, center), radius)
                self.image.blit(temp_surf, (0, 0))
            
            # 旋转符文
            for i in range(5):
                angle = (i * 72 + t * 20) * 3.14159 / 180
                px = center + int(size//3 * math.cos(angle))
                py = center + int(size//3 * math.sin(angle))
                rune_color = tuple(min(255, c + 30) for c in color)
                pygame.draw.circle(self.image, rune_color, (px, py), size//10)
        
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
    def __init__(self, plane_id="striker", custom_visual=None):
        super().__init__()
        self.plane_id = plane_id
        self.plane_data = PLANES[plane_id]
        
        # 获取装备的子弹涂装
        self.bullet_theme = None
        try:
            from customization import customization_manager, BULLET_THEMES
            equipped_bullet_id = customization_manager.get_equipped_theme(plane_id, bullet=True)
            if equipped_bullet_id and equipped_bullet_id in BULLET_THEMES:
                self.bullet_theme = BULLET_THEMES[equipped_bullet_id]
        except:
            pass  # 如果导入失败或没有涂装，使用默认子弹
        
        # 绘制机体 - 使用涂装系统
        if custom_visual:
            self.visual = custom_visual
        else:
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
        self.image = pygame.transform.scale(self.image, (100, 100))
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
        # 更新动态飞机模型
        plane_surf = get_plane_surf(self.plane_id, self.visual, static=False)
        self.image = pygame.transform.scale(plane_surf, (100, 100))
        
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
                       color=color, b_type=b_type, piercing=self.piercing, homing=self.homing_level, bullet_theme=self.bullet_theme)
        
        # ========== 2. 虚空幻影 - 快速多枚散射 ==========
        elif pid == "phantom":
            # 高射速特性：发射更多细小子弹
            for i in range(cnt * 2):
                spread = (i - cnt + 0.5) * 8
                angle = random.uniform(-15, 15)
                Bullet(self.rect.centerx + spread, self.rect.top, angle=angle,
                       color=color, b_type=b_type, piercing=self.piercing//2 if self.piercing else 0, bullet_theme=self.bullet_theme)
        
        # ========== 3. 钢铁泰坦 - 慢速但强力的集中炮火 ==========
        elif pid == "titan":
            # 低射速、高威力：发射强力火箭
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 25
                Bullet(self.rect.centerx + offset_x, self.rect.top, 
                       color=color, b_type=b_type, piercing=self.piercing + 2, homing=self.homing_level, bullet_theme=self.bullet_theme)
        
        # ========== 4. 极光女神 - 范围电浆波 ==========
        elif pid == "aurora":
            # 范围型：发射扇形波纹攻击
            for i in range(cnt + 2):
                angle = -30 + i * (60 / (cnt + 1))
                Bullet(self.rect.centerx, self.rect.top, angle=angle,
                       color=color, b_type=b_type, piercing=self.piercing, bullet_theme=self.bullet_theme)
        
        # ========== 5. 幽灵收割者 - 单发极高伤害 ==========
        elif pid == "specter":
            # 射速极慢但单发超高伤害
            if cnt > 0:  # 应该是1
                Bullet(self.rect.centerx, self.rect.top,
                       color=color, b_type=b_type, piercing=self.piercing + 5, homing=self.homing_level, bullet_theme=self.bullet_theme)
        
        # ========== 6. 雷霆战鹰 - 多段连锁闪电 ==========
        elif pid == "thunderbird":
            # 发射闪电链：多个连接的闪电
            spacing = 20
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * spacing
                Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=color, b_type="lightning", piercing=self.piercing, bullet_theme=self.bullet_theme)
        
        # ========== 7. 剧毒蝰蛇 - 持续毒液喷射 ==========
        elif pid == "viper":
            # 连续喷射：在一定范围内发射多枚毒液
            for i in range(cnt + 1):
                spread = (i - cnt/2) * 12
                angle = random.uniform(-20, 20)
                Bullet(self.rect.centerx + spread, self.rect.top, angle=angle,
                       color=color, b_type="acid", piercing=self.piercing, bullet_theme=self.bullet_theme)
        
        # ========== 8. 绯红之刃 - 高频旋转飞刃 ==========
        elif pid == "crimson":
            # 高射速特性：发射旋转的飞刃
            time_factor = pygame.time.get_ticks() / 100  # 时间因子实现旋转效果
            for i in range(cnt * 2):
                angle = (time_factor + i * (360 / (cnt * 2))) % 360
                Bullet(self.rect.centerx, self.rect.top, angle=angle,
                       color=color, b_type="blade", piercing=self.piercing, bullet_theme=self.bullet_theme)
        
        # ========== 9. 星界潜行者 - 追踪星镖 ==========
        elif pid == "stalker":
            # 追踪特性：发射自动追踪的星镖
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 20
                Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=color, b_type="star", piercing=self.piercing, 
                       homing=self.homing_level + 1, bullet_theme=self.bullet_theme)  # 加强追踪
        
        # ========== 10. 大地守护者 - 散射荆棘 ==========
        elif pid == "gaia":
            # 散射特性：发射向下散开的荆棘
            for i in range(cnt + 3):
                angle = -40 + i * (80 / (cnt + 2))
                Bullet(self.rect.centerx, self.rect.top, angle=angle,
                       color=color, b_type="thorn", piercing=self.piercing, bullet_theme=self.bullet_theme)
        
        # ========== 11. 虚空编织者 - 蛛网束缚 ==========
        elif pid == "weaver":
            # 控制特性：发射粘稠的蛛网
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 20
                # 蛛网子弹速度较慢
                bullet = Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=color, b_type="web", piercing=self.piercing, bullet_theme=self.bullet_theme)
                bullet.speed = -8  # 减速
        
        # ========== 12. 日冕耀斑 - 高频火焰喷流 ==========
        elif pid == "solar":
            # 极高射速：发射连续的火焰
            for i in range(cnt * 3):  # 射速高意味着更多子弹
                spread = (i - cnt + 0.5) * 6
                angle = random.uniform(-12, 12)
                Bullet(self.rect.centerx + spread, self.rect.top, angle=angle,
                       color=color, b_type="flame", piercing=self.piercing//2 if self.piercing else 0, bullet_theme=self.bullet_theme)
        
        # ========== 13. 量子裁决者 - 分裂量子块 ==========
        elif pid == "arbiter":
            # 分裂特性：发射会分裂的量子块
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 18
                Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=color, b_type="quant", piercing=self.piercing, bullet_theme=self.bullet_theme)
        
        # ========== 14. 日食幽灵 - 双核心双线射击 ==========
        elif pid == "eclipse":
            # 双核心特性：同时从两个点发射
            left_x = self.rect.centerx - 15
            right_x = self.rect.centerx + 15
            for i in range(cnt):
                offset = (i - (cnt-1)/2) * 10
                # 左核心
                Bullet(left_x + offset, self.rect.top, 
                       color=color, b_type="shadow", piercing=self.piercing, angle=-5, bullet_theme=self.bullet_theme)
                # 右核心
                Bullet(right_x + offset, self.rect.top,
                       color=color, b_type="shadow", piercing=self.piercing, angle=5, bullet_theme=self.bullet_theme)
        
        # ========== 15. 棱镜分光 - 一发三道分裂 ==========
        elif pid == "prism":
            # 分裂特性：每发子弹发射后会分裂成三道
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 16
                # 中间直射
                Bullet(self.rect.centerx + offset_x, self.rect.top, angle=0,
                       color=(100, 180, 255), b_type="refract", piercing=self.piercing, bullet_theme=self.bullet_theme)
                # 左侧散射
                Bullet(self.rect.centerx + offset_x, self.rect.top, angle=-25,
                       color=(255, 100, 100), b_type="refract", piercing=self.piercing//2, bullet_theme=self.bullet_theme)
                # 右侧散射
                Bullet(self.rect.centerx + offset_x, self.rect.top, angle=25,
                       color=(100, 255, 100), b_type="refract", piercing=self.piercing//2, bullet_theme=self.bullet_theme)
        
        # ========== 16. 死灵骑士 - 吸血射击 ==========
        elif pid == "necro":
            # 吸血特性：普通伤害转化为吸收
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 18
                Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=color, b_type="spectral", piercing=self.piercing, bullet_theme=self.bullet_theme)
        
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
            # 使用增强尾迹效果（如果有涂装系统）
            try:
                from customization import EnhancedTrailEffect
                EnhancedTrailEffect.draw_trail(surf, self.trail_pos, self.visual)
            except:
                # 降级为普通尾迹
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