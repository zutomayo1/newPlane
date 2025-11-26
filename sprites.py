import pygame
import math
import random
from config import *
from utils import sound_mgr, draw_text, get_plane_surf, get_boss_surf, draw_cyber_rect, log_error
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
        self.life = random.randint(20, 40)
        if mode == "shockwave":
            self.image = pygame.Surface((2, 2), pygame.SRCALPHA)
            self.radius = 10
            self.pos = pos
            self.rect = self.image.get_rect(center=pos)
        elif mode == "lightning":
            self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            self.rect = self.image.get_rect()
            self.points = pos
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
        
        # 创建棱形纹理
        self.image = pygame.Surface((self.size*3, self.size*3), pygame.SRCALPHA)
        self.draw_diamond()
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        
    def draw_diamond(self):
        """绘制棱形（菱形）经验球"""
        self.image.fill((0, 0, 0, 0))
        center = self.size * 1.5
        
        # 背景光晕
        for i in range(3, 0, -1):
            alpha = int(60 * (1 - i/4))
            pygame.draw.circle(self.image, self.glow_color, (int(center), int(center)), int(self.size * 1.2 + i), 1)
        
        # 棱形顶点（上下左右）
        diamond_points = [
            (center, center - self.size),      # 上
            (center + self.size, center),       # 右
            (center, center + self.size),       # 下
            (center - self.size, center)        # 左
        ]
        
        # 绘制棱形填充
        pygame.draw.polygon(self.image, self.color, diamond_points)
        
        # 棱形边框（增强轮廓）
        pygame.draw.polygon(self.image, self.glow_color, diamond_points, 1)
        
    def update(self):
        # 重力下落
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
        sound_mgr.play("laser")

    def update(self):
        self.life -= 1
        self.image.fill((0,0,0,0))
        if self.life <= 0: self.kill(); return
        
        w = 150 * math.sin(self.life / 120 * 3.14)
        center_x = self.owner.rect.centerx
        pygame.draw.rect(self.image, WHITE, (center_x - w/4, 0, w/2, HEIGHT))
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 255, 255, 100), (center_x - w/2, 0, w, HEIGHT))
        self.image.blit(s, (0,0))
        
        # 伤害判定逻辑需在 main loop 中处理，或者在这里引用全局 mobs
        # 这里仅负责视觉，碰撞由调用者或全局管理
        if self.life % 5 == 0:
            # 简单的范围判定
            for m in mobs:
                if abs(m.rect.centerx - center_x) < w/2 + m.radius:
                    m.hp -= 200
                    Particle(m.rect.center, CYAN)

class TimeSlash(pygame.sprite.Sprite):
    def __init__(self, target_pos):
        super().__init__()
        all_sprites.add(self)
        self.pos = target_pos
        self.life = 30
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=target_pos)
        self.angle = random.randint(0, 360)

    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        self.image.fill((0,0,0,0))
        l = 100 * (1 - self.life/30)
        rad = math.radians(self.angle)
        start = (50 - math.cos(rad)*l, 50 - math.sin(rad)*l)
        end = (50 + math.cos(rad)*l, 50 + math.sin(rad)*l)
        pygame.draw.line(self.image, MAGENTA, start, end, 5)
        pygame.draw.line(self.image, WHITE, start, end, 2)

class NukeExplosion(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        all_sprites.add(self)
        self.life = 60
        self.radius = 10
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("nuke")

    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        self.radius += 30 # 加快扩散
        pygame.draw.circle(self.image, (255, 100, 0, 20), (WIDTH/2, HEIGHT/2), self.radius)

class BlackHole(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        all_sprites.add(self)
        self.pos = pos
        self.life = 180
        self.radius = 10
        self.max_radius = 120
        self.image = pygame.Surface((self.max_radius*2, self.max_radius*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        self.angle = 0
        sound_mgr.play("blackhole")

    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        if self.life > 150: self.radius = min(self.max_radius, self.radius + 4)
        elif self.life < 30: self.radius = max(0, self.radius - 4)
        
        self.angle = (self.angle + 10) % 360
        self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BLACK, (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.image, (100, 0, 150), (self.radius, self.radius), self.radius, 4)
        
        for i in range(0, 360, 45):
            rad = math.radians(i + self.angle)
            end_x = self.radius + math.cos(rad) * self.radius
            end_y = self.radius + math.sin(rad) * self.radius
            pygame.draw.line(self.image, MAGENTA, (self.radius, self.radius), (end_x, end_y), 2)
            
        self.rect = self.image.get_rect(center=self.pos)
        # 吸附效果
        for m in mobs:
            dist = math.hypot(m.rect.centerx - self.pos[0], m.rect.centery - self.pos[1])
            if dist < self.radius * 2.5:
                m.rect.centerx += (self.pos[0] - m.rect.centerx) * 0.1
                m.rect.centery += (self.pos[1] - m.rect.centery) * 0.1
                m.hp -= 2

class AuroraCurtain(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        all_sprites.add(self)
        self.life = 120
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0,0))
        self.offset = 0
        self.damage_timer = 0

    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        self.offset += 0.2
        self.image.fill((0,0,0,0))
        colors = [TEAL, (0, 255, 128), (0, 100, 255)]
        
        for i, color in enumerate(colors):
            points = []
            for y in range(0, HEIGHT, 20):
                x = WIDTH/2 + math.sin(y * 0.01 + self.offset + i) * (WIDTH/2 - 50)
                points.append((x, y))
            
            if len(points) > 1:
                pygame.draw.lines(self.image, (*color, 150), False, points, 10)

        self.damage_timer += 1
        if self.damage_timer % 4 == 0:
            for m in mobs: 
                m.hp -= 100
                m.frozen_timer = 20

class DeathScythe(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        all_sprites.add(self)
        self.center = center
        self.angle = 0
        self.life = 60
        self.radius = 10
        self.max_radius = 450 # 增大范围
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self.damage_timer = 0

    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        self.angle += 15
        if self.life > 40: self.radius = min(self.max_radius, self.radius + 25)
        
        self.image.fill((0,0,0,0))
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
                pygame.draw.lines(self.image, (150, 50, 255, 200), False, points, 8)

        self.damage_timer += 1
        if self.damage_timer % 5 == 0:
            for m in mobs:
                dist = math.hypot(m.rect.centerx - self.center[0], m.rect.centery - self.center[1])
                if dist < self.radius:
                    m.hp -= 300
                    Particle(m.rect.center, (150, 50, 255))

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
        # 假设 player_level 是全局或传入参数，这里简化为 1
        lvl = 1 
        
        if type_name == "drone":
            # 赛博朋克风格：六边形无人机，红色警报色
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            center = 20
            size = 12
            # 绘制六边形
            points = [(center + size, center), (center + size//2, center + size), 
                     (center - size//2, center + size), (center - size, center),
                     (center - size//2, center - size), (center + size//2, center - size)]
            pygame.draw.polygon(self.image, CYBER_RED_ALERT, points)
            pygame.draw.polygon(self.image, CYBER_CYAN, points, 1)
            self.base_speed = 3; self.hp = 25 + lvl * 10
        elif type_name == "chaser":
            # 赛博朋克风格：菱形追踪者，警报红
            self.image = pygame.Surface((36, 40), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, CYBER_RED_ALERT, [(18, 40), (36, 0), (18, 10), (0, 0)])
            pygame.draw.polygon(self.image, CYBER_CYAN_BRIGHT, [(18, 40), (36, 0), (18, 10), (0, 0)], 1)
            self.base_speed = 4; self.hp = 40 + lvl * 15
        elif type_name == "tank":
            # 赛博朋克风格：方形坦克，橙色警告
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (255, 140, 0), (5, 5, 40, 40))
            pygame.draw.rect(self.image, CYBER_CYAN_BRIGHT, (5, 5, 40, 40), 2)
            self.base_speed = 1.5; self.hp = 80 + lvl * 20; self.radius = 25
        elif type_name == "wasp":
            # 赛博朋克风格：菱形黄蜂，琥珀黄
            self.image = pygame.Surface((34, 34), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, CYBER_AMBER, [(17, 34), (34, 20), (17, 0), (0, 20)])
            pygame.draw.polygon(self.image, CYBER_LIME, [(17, 34), (34, 20), (17, 0), (0, 20)], 1)
            self.base_speed = 3.5; self.hp = 30 + lvl * 10; self.radius = 17
            self.start_x = random.randint(0, WIDTH)
            
        elif type_name == "sniper":
            # 赛博朋克风格：竖长方形狙击手，极光青
            self.image = pygame.Surface((30, 60), pygame.SRCALPHA)
            pygame.draw.rect(self.image, CYBER_CYAN, (8, 5, 14, 50))
            pygame.draw.rect(self.image, CYBER_CYAN_BRIGHT, (8, 5, 14, 50), 2)
            self.base_speed = 3; self.hp = 50 + lvl * 12
        elif type_name == "glitch": 
            # 赛博朋克风格：闪烁的小方块，幽灵青
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.rect(self.image, CYBER_CYAN_BRIGHT, (8, 8, 14, 14))
            pygame.draw.rect(self.image, CYBER_CYAN, (8, 8, 14, 14), 1)
            self.base_speed = 2; self.hp = 20 + lvl * 5
            
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
                self.image = pygame.transform.scale(self.image, (int(self.image.get_width()*1.3), int(self.image.get_height()*1.3)))
                self.radius *= 1.3
                # 重绘精英版本，添加外圈
                original = self.image.copy()
                self.image = pygame.Surface((int(self.image.get_width()*1.2), int(self.image.get_height()*1.2)), pygame.SRCALPHA)
                self.image.blit(original, (int(self.image.get_width()*0.1), int(self.image.get_height()*0.1)))
                # 添加琥珀黄外框
                pygame.draw.rect(self.image, CYBER_AMBER, self.image.get_rect(), 2)
                
        self.speed = self.base_speed
        self.max_hp = self.hp

    def update(self):
        if self.frozen_timer > 0:
            self.frozen_timer -= 1
            return # 冻结不移动
            
        if self.type == "wasp":
            self.rect.y += self.speed
            self.rect.x = self.start_x + math.sin(pygame.time.get_ticks() * 0.005) * 80
        elif self.type == "sniper":
            if self.state == "move":
                self.rect.y += self.speed
                if self.rect.y > 100: self.state = "aim"; self.timer = 0
            elif self.state == "aim":
                self.timer += 1
                if self.timer > 60: self.state = "fire"
            elif self.state == "fire":
                Bullet(self.rect.centerx, self.rect.bottom, is_enemy=True, color=CYAN, b_type="needle")
                self.state = "leave"
            elif self.state == "leave":
                self.rect.y += self.speed * 2
        else:
            self.rect.y += self.speed
            
        if self.rect.top > HEIGHT: self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 确保只在 boss 不存在时添加
        boss_types = list(BOSS_DB.keys())
        self.type = random.choice(boss_types)
        data = BOSS_DB[self.type]
        self.name = data["name"]
        color = data["color"]
        
        # 使用 utils 中的绘图函数
        self.image = get_boss_surf(self.type, color)
        self.rect = self.image.get_rect(midbottom=(WIDTH/2, -50))
        
        self.hp = 5000 # 基础血量
        self.max_hp = self.hp
        self.state = "enter"
        self.enraged = False
        self.shoot_timer = 0
        self.teleport_timer = 0
        self.angle = 0
        self.start_y = 0

    def update(self):
        if not self.enraged and self.hp < self.max_hp * 0.5:
            self.enraged = True
            sound_mgr.play("warning")
            
        if self.state == "enter":
            self.rect.y += 2
            if self.rect.top > 50:
                self.state = "fight"
                self.start_y = self.rect.y
        elif self.state == "fight":
            self.shoot_timer += 1
            threshold = 30 if self.enraged else 60
            
            # 简单的通用射击逻辑，根据BOSS类型微调
            if self.shoot_timer > threshold:
                self.shoot_timer = 0
                if self.type == "carrier":
                    for i in range(-2, 3): 
                        Bullet(self.rect.centerx, self.rect.bottom, angle=i*15, is_enemy=True)
                elif self.type == "fortress":
                    for i in range(0, WIDTH, 100):
                        Bullet(i, self.rect.bottom, angle=0, is_enemy=True, b_type="plasma")
                else:
                    # 默认环形弹幕
                    for i in range(0, 360, 45):
                        Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True)
                        
            # 移动逻辑
            self.rect.x = WIDTH/2 - 120 + math.sin(pygame.time.get_ticks()*0.001) * 100

class Player(pygame.sprite.Sprite):
    def __init__(self, plane_id="striker"):
        super().__init__()
        self.plane_id = plane_id
        self.plane_data = PLANES[plane_id]
        
        # 绘制机体
        self.image = get_plane_surf(plane_id)
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
        self.last_shot = 0
        self.damage_reduction = 0.0
        
        self.weapon_slots = []
        for w_data in arsenal_save_data["loadout"]:
            if w_data: self.weapon_slots.append(WeaponSystem(w_data))
            else: self.weapon_slots.append(None)
        self.current_slot = 0
        self.switch_cooldown = 0
        
        self.drones = [] # Wingman 逻辑可以在 main 或此处实现
        self.skill_cd = 0
        self.max_skill_cd = 300
        self.trail_pos = []
        
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
        
        # 能量回复
        if not self.is_dashing and self.dash_energy < self.max_dash_energy:
            self.dash_energy += 0.5
        if self.skill_cd > 0: self.skill_cd -= 1
        
        # 武器更新
        if self.switch_cooldown > 0: self.switch_cooldown -= 1
        for w in self.weapon_slots:
            if w: w.update()

        # 移动逻辑 (WASD + Arrows)
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = self.speed
        
        # 冲刺
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.dash_energy > 2 and (dx!=0 or dy!=0):
            self.is_dashing = True
            self.dash_energy -= 2
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
            
        # 2. 副武器射击 (修复了子弹生成逻辑)
        active_w = self.weapon_slots[self.current_slot]
        if active_w and self.switch_cooldown <= 0:
            if active_w.can_shoot():
                # 先扣除资源 (调用 systems.py 中的逻辑)
                active_w.shoot(self.rect, mobs, self.homing_level)
                # 再生成实体 (调用本地的 _fire_sub_weapon)
                self._fire_sub_weapon(active_w)

    def _fire_main_gun(self):
        b_type = self.plane_data["bullet_type"]
        color = self.plane_data["color"]
        cnt = self.bullet_count
        start_x = self.rect.centerx - (cnt-1)*10
        for i in range(cnt):
            Bullet(start_x + i*20, self.rect.top, color=color, b_type=b_type, piercing=self.piercing, homing=self.homing_level)

    def use_ultimate(self):
        if self.ult_charge >= 100:
            self.ult_charge -= 100
            name = self.plane_data["ult_name"]
            FloatingText(self.rect.centerx, self.rect.top - 50, f"★ {name} ★", self.plane_data["color"])
            
            # 根据机体ID释放不同大招
            pid = self.plane_id
            if pid == "striker": FinalBeam(self)
            elif pid == "phantom": 
                # 这里需要 main.py 设置 global_time_freeze，暂且只生成特效
                for m in mobs: TimeSlash(m.rect.center)
            elif pid == "titan": NukeExplosion()
            elif pid == "aurora": AuroraCurtain()
            elif pid == "specter": DeathScythe(self.rect.center)
            elif pid == "void": BlackHole((WIDTH/2, HEIGHT/2))
            # 其他机体大招可在此补充
            else:
                # 通用：全屏清弹
                enemy_bullets.empty()
                sound_mgr.play("nuke")

    def draw_trail(self, surf):
        if len(self.trail_pos) > 2:
            pygame.draw.lines(surf, self.plane_data["color"], False, self.trail_pos, 2)
            
    def draw_auras(self, surf):
        # 护盾光环
        if self.shield > 0:
            pygame.draw.circle(surf, SHIELD_BLUE, self.rect.center, 35, 1)
            
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
            from roguelite import UpgradeManager, ExperienceSystem, BuffProcessor
            self.upgrade_manager = UpgradeManager()
            self.exp_system = ExperienceSystem(self)
            self.buff_processor = BuffProcessor(self)
        except ImportError as e:
            log_error(f"Failed to import roguelite module: {e}")
    
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