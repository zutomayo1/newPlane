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
        
    def draw_diamond(self, rotation=0, pulse=1.0):
        """绘制经验球 - 高级动态设计"""
        self.image.fill((0, 0, 0, 0))
        center = self.size * 1.5
        
        if self.amount >= 10:  # 精英掉落（金黄色 - 更炫）
            # 脉冲外光环（多层渐变）
            for i in range(5, 0, -1):
                alpha = int(80 * pulse / i)
                glow_surf = pygame.Surface((self.size*6, self.size*6), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 200, 0, alpha), 
                                 (self.size*3, self.size*3), 
                                 int(self.size * (1.5 + i * 0.2) * pulse))
                self.image.blit(glow_surf, (center - self.size*3, center - self.size*3))
            
            # 旋转八边形（外框）
            oct_size = self.size * pulse
            oct_points = []
            for i in range(8):
                angle = i * 45 + rotation
                rad = math.radians(angle)
                x = center + oct_size * math.cos(rad)
                y = center + oct_size * math.sin(rad)
                oct_points.append((x, y))
            
            # 渐变填充
            pygame.draw.polygon(self.image, (255, 220, 0), oct_points)
            pygame.draw.polygon(self.image, (255, 180, 0), oct_points, 3)
            pygame.draw.polygon(self.image, (255, 255, 100), oct_points, 1)
            
            # 旋转菱形（反向旋转制造动感）
            diamond_points = []
            for i in range(4):
                angle = i * 90 - rotation * 1.5
                rad = math.radians(angle)
                x = center + self.size * 0.7 * math.cos(rad) * pulse
                y = center + self.size * 0.7 * math.sin(rad) * pulse
                diamond_points.append((x, y))
            pygame.draw.polygon(self.image, (255, 200, 50), diamond_points)
            pygame.draw.polygon(self.image, (255, 150, 0), diamond_points, 2)
            
            # 旋转五角星（快速旋转）
            star_points = []
            for i in range(5):
                angle = i * 72 + rotation * 2
                rad = math.radians(angle)
                r = self.size * 0.4 * pulse
                x = center + r * math.cos(rad)
                y = center + r * math.sin(rad)
                star_points.append((x, y))
                # 星角间的小点
                angle2 = angle + 36
                rad2 = math.radians(angle2)
                r2 = self.size * 0.2 * pulse
                x2 = center + r2 * math.cos(rad2)
                y2 = center + r2 * math.sin(rad2)
                star_points.append((x2, y2))
            pygame.draw.polygon(self.image, (255, 255, 150), star_points)
            
            # 中心核心（呼吸发光）
            core_size = int(self.size * 0.3 * pulse)
            pygame.draw.circle(self.image, (255, 255, 200), (int(center), int(center)), core_size)
            pygame.draw.circle(self.image, (255, 255, 255), (int(center), int(center)), max(1, core_size // 2))
            
            # 粒子轨道
            for i in range(4):
                orbit_angle = rotation * 3 + i * 90
                rad = math.radians(orbit_angle)
                px = center + self.size * 0.9 * math.cos(rad)
                py = center + self.size * 0.9 * math.sin(rad)
                pygame.draw.circle(self.image, (255, 255, 100), (int(px), int(py)), 2)
        
        else:  # 普通掉落（翠绿色 - 也要炫）
            # 脉冲外光环
            for i in range(4, 0, -1):
                alpha = int(60 * pulse / i)
                glow_surf = pygame.Surface((self.size*6, self.size*6), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (100, 255, 150, alpha), 
                                 (self.size*3, self.size*3), 
                                 int(self.size * (1.4 + i * 0.15) * pulse))
                self.image.blit(glow_surf, (center - self.size*3, center - self.size*3))
            
            # 旋转六边形
            hex_size = self.size * pulse
            hex_points = []
            for i in range(6):
                angle = i * 60 + rotation
                rad = math.radians(angle)
                x = center + hex_size * math.cos(rad)
                y = center + hex_size * math.sin(rad)
                hex_points.append((x, y))
            pygame.draw.polygon(self.image, (100, 255, 150), hex_points)
            pygame.draw.polygon(self.image, (50, 255, 100), hex_points, 2)
            pygame.draw.polygon(self.image, (150, 255, 200), hex_points, 1)
            
            # 内菱形（反向旋转）
            diamond_points = []
            for i in range(4):
                angle = i * 90 - rotation * 1.5
                rad = math.radians(angle)
                x = center + self.size * 0.65 * math.cos(rad) * pulse
                y = center + self.size * 0.65 * math.sin(rad) * pulse
                diamond_points.append((x, y))
            pygame.draw.polygon(self.image, (150, 255, 180), diamond_points)
            pygame.draw.polygon(self.image, (100, 255, 150), diamond_points, 2)
            
            # 四角装饰点（旋转）
            corner_colors = [(100, 255, 200), (255, 150, 200), (100, 200, 255), (255, 200, 100)]
            for i, col in enumerate(corner_colors):
                angle = i * 90 + rotation * 2
                rad = math.radians(angle)
                px = center + self.size * 0.5 * math.cos(rad) * pulse
                py = center + self.size * 0.5 * math.sin(rad) * pulse
                pygame.draw.circle(self.image, col, (int(px), int(py)), 3)
                pygame.draw.circle(self.image, (255, 255, 255), (int(px), int(py)), 1)
            
            # 中心核心
            core_size = int(self.size * 0.35 * pulse)
            pygame.draw.circle(self.image, (200, 255, 220), (int(center), int(center)), core_size)
            pygame.draw.circle(self.image, (255, 255, 255), (int(center), int(center)), max(1, core_size // 2))
        
    def update(self):
        # 计算动态旋转和脉冲
        elapsed = (pygame.time.get_ticks() - self.birth_time) / 1000.0
        rotation = (elapsed * 60) % 360  # 每秒旋转60度
        pulse = 0.85 + 0.15 * math.sin(elapsed * 3)  # 呼吸效果
        
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
            
            # 重新绘制缩小的经验球（快速旋转）
            old_size = self.size
            self.size = int(old_size * fade_ratio)
            fast_rotation = (rotation * 3) % 360
            self.draw_diamond(fast_rotation, fade_ratio)
            self.size = old_size
            
            self.rect.center = (int(self.x), int(self.y))
            return
        
        # 正常状态：重新绘制（持续旋转+脉冲）
        self.draw_diamond(rotation, pulse)
        
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
        
        # 透明度闪烁效果
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
#   新大招特效类（重写版）
# ==============================================================================

class ThunderStorm(pygame.sprite.Sprite):
    """雷霆战鹰·雷神降世 - 全屏雷暴风暴，闪电从天而降"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 90
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.hit_enemies = set()
        self.strike_timer = 0
        self.lightning_bolts = []  # 存储闪电路径
        sound_mgr.play("nuke")
        
    def _generate_lightning_path(self, start, end):
        """生成锯齿状闪电路径"""
        points = [start]
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        segments = 8
        for i in range(1, segments):
            t = i / segments
            x = start[0] + dx * t + random.randint(-40, 40)
            y = start[1] + dy * t + random.randint(-20, 20)
            points.append((x, y))
        points.append(end)
        return points
    
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        self.strike_timer += 1
        
        # 每6帧生成新闪电
        if self.strike_timer % 6 == 0:
            # 随机选择目标（敌人或随机位置）
            targets = list(mobs)
            if targets:
                target = random.choice(targets)
                target_pos = target.rect.center
            else:
                target_pos = (random.randint(50, WIDTH-50), random.randint(100, HEIGHT-100))
            
            # 从天空降下闪电
            start_x = target_pos[0] + random.randint(-100, 100)
            start_pos = (start_x, -20)
            path = self._generate_lightning_path(start_pos, target_pos)
            self.lightning_bolts.append({'path': path, 'life': 15, 'width': 6})
            
            # 对目标位置周围敌人造成伤害
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - target_pos[0], m.rect.centery - target_pos[1])
                if dist < 80:
                    if m not in self.hit_enemies:
                        m.hp -= 280
                        self.hit_enemies.add(m)
                        FloatingText(m.rect.centerx, m.rect.top - 30, "⚡THUNDER!", YELLOW)
                    else:
                        m.hp -= 60
                    for _ in range(3):
                        Particle(m.rect.center, YELLOW)
        
        # 绘制所有闪电
        for bolt in self.lightning_bolts[:]:
            bolt['life'] -= 1
            if bolt['life'] <= 0:
                self.lightning_bolts.remove(bolt)
                continue
            
            alpha = int(255 * (bolt['life'] / 15))
            width = max(1, int(bolt['width'] * (bolt['life'] / 15)))
            
            # 主闪电 - 黄白色
            for i in range(len(bolt['path']) - 1):
                p1, p2 = bolt['path'][i], bolt['path'][i+1]
                pygame.draw.line(self.image, (255, 255, 200, alpha), p1, p2, width)
                pygame.draw.line(self.image, (255, 255, 0, alpha), p1, p2, max(1, width-2))
            
            # 分叉闪电
            if len(bolt['path']) > 4:
                branch_start = bolt['path'][3]
                branch_end = (branch_start[0] + random.randint(-60, 60), branch_start[1] + random.randint(20, 80))
                pygame.draw.line(self.image, (255, 255, 100, alpha//2), branch_start, branch_end, max(1, width-2))
        
        # 屏幕闪烁效果
        if self.strike_timer % 6 < 2:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 255, 200, 30))
            self.image.blit(flash, (0, 0))


class ToxicMiasma(pygame.sprite.Sprite):
    """剧毒蝰蛇·腐蚀毒雾 - 全屏毒气弥漫，持续腐蚀"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 150
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.particles = []
        self.hit_enemies = {}
        sound_mgr.play("nuke")
        
        # 生成初始毒雾粒子
        for _ in range(50):
            self.particles.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'size': random.randint(30, 80),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-0.5, 0.5),
                'alpha': random.randint(50, 100)
            })
    
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        
        # 更新和绘制毒雾粒子
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            # 边界循环
            if p['x'] < -50: p['x'] = WIDTH + 50
            if p['x'] > WIDTH + 50: p['x'] = -50
            if p['y'] < -50: p['y'] = HEIGHT + 50
            if p['y'] > HEIGHT + 50: p['y'] = -50
            
            # 脉动效果
            pulse = 1 + 0.2 * math.sin(self.life * 0.1 + p['x'] * 0.01)
            size = int(p['size'] * pulse)
            alpha = int(p['alpha'] * (self.life / 150))
            
            # 绘制毒雾圆
            surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            # 多层渐变
            for r in range(size, 0, -5):
                a = int(alpha * (r / size))
                pygame.draw.circle(surf, (50, 200, 50, a), (size, size), r)
            self.image.blit(surf, (int(p['x'] - size), int(p['y'] - size)))
        
        # 毒液滴落效果
        if self.life % 10 == 0:
            for _ in range(3):
                x = random.randint(50, WIDTH-50)
                Particle((x, random.randint(50, 150)), LIME, mode='spark')
        
        # 持续毒伤
        if self.life % 5 == 0:
            for m in list(mobs):
                if m not in self.hit_enemies:
                    self.hit_enemies[m] = 0
                    m.hp -= 150
                    FloatingText(m.rect.centerx, m.rect.top - 30, "☠TOXIC!", LIME)
                else:
                    m.hp -= 25
                    self.hit_enemies[m] += 1
                m.poison_timer = 60  # 标记中毒
                if random.random() < 0.3:
                    Particle(m.rect.center, LIME)


class BloodMoonSlash(pygame.sprite.Sprite):
    """绯红之刃·鲜血新月 - 360度旋转血刃斩击"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 60
        self.angle = 0
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.hit_enemies = set()
        self.slashes = []  # 存储刀痕
        sound_mgr.play("laser")
        
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        self.angle += 25
        
        cx, cy = self.owner.rect.center
        
        stack_ratio = self.owner.blood_stacks / max(1, getattr(self.owner, 'max_blood_stacks', 1)) if hasattr(self.owner, 'blood_stacks') else 0
        blade_color = (
            int(140 + 90 * stack_ratio),
            int(5 + 80 * stack_ratio),
            int(20 + 140 * stack_ratio)
        )
        highlight_color = (
            min(255, int(200 + 40 * stack_ratio)),
            int(60 + 120 * stack_ratio),
            int(80 + 150 * stack_ratio)
        )
        blade_length = 260 + 120 * stack_ratio
        width_base = 6 + int(3 * stack_ratio)

        # 绘制旋转的6把血刃
        for i in range(6):
            blade_angle = self.angle + i * 60
            rad = math.radians(blade_angle)
            
            # 刀刃轨迹
            tip_x = cx + math.cos(rad) * blade_length
            tip_y = cy + math.sin(rad) * blade_length
            
            # 刀身曲线（贝塞尔曲线效果）
            points = []
            for t in range(20):
                prog = t / 19
                r = blade_length * prog
                curve = math.sin(prog * math.pi) * 30
                px = cx + math.cos(rad) * r + math.cos(rad + math.pi/2) * curve
                py = cy + math.sin(rad) * r + math.sin(rad + math.pi/2) * curve
                points.append((px, py))
            
            if len(points) > 2:
                pygame.draw.lines(self.image, blade_color, False, points, width_base)
                pygame.draw.lines(self.image, highlight_color, False, points, max(2, width_base - 3))
            
            # 刀尖光效
            pygame.draw.circle(self.image, (255, 200, 200), (int(tip_x), int(tip_y)), 8 + int(4 * stack_ratio))
            
            # 伤害检测
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
                if dist < blade_length:
                    angle_to_enemy = math.degrees(math.atan2(m.rect.centery - cy, m.rect.centerx - cx))
                    angle_diff = abs((angle_to_enemy - blade_angle + 180) % 360 - 180)
                    if angle_diff < 15:
                        if m not in self.hit_enemies:
                            damage = 320 + 40 * stack_ratio
                            m.hp -= damage
                            self.hit_enemies.add(m)
                            FloatingText(m.rect.centerx, m.rect.top - 30, "🌙CRESCENT!", CRIMSON)
                            # 添加刀痕
                            self.slashes.append({'pos': m.rect.center, 'life': 20, 'angle': blade_angle})
                            if hasattr(self.owner, 'apply_crimson_blood'):
                                self.owner.apply_crimson_blood(m, damage, m.rect.center)
                        else:
                            chip_damage = 50 + 15 * stack_ratio
                            m.hp -= chip_damage
                            if hasattr(self.owner, 'apply_crimson_blood'):
                                self.owner.apply_crimson_blood(m, chip_damage, m.rect.center)
                        for _ in range(2):
                            Particle(m.rect.center, CRIMSON)
        
        # 绘制刀痕
        for slash in self.slashes[:]:
            slash['life'] -= 1
            if slash['life'] <= 0:
                self.slashes.remove(slash)
                continue
            alpha = int(255 * (slash['life'] / 20))
            rad = math.radians(slash['angle'])
            sx, sy = slash['pos']
            s_len = 40
            p1 = (sx - math.cos(rad) * s_len, sy - math.sin(rad) * s_len)
            p2 = (sx + math.cos(rad) * s_len, sy + math.sin(rad) * s_len)
            pygame.draw.line(self.image, (255, 50, 50, alpha), p1, p2, 3)
        
        # 中心血月
        moon_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        glow_alpha = int(150 + 80 * stack_ratio)
        pygame.draw.circle(moon_surf, (150, 0, 0, glow_alpha), (50, 50), 40)
        pygame.draw.circle(moon_surf, blade_color, (50, 50), 35, 3)
        self.image.blit(moon_surf, (cx - 50, cy - 50))


class StarfallBarrage(pygame.sprite.Sprite):
    """星界潜行者·群星坠落 - 星镖从四面八方射向敌人"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 80
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.stars = []
        self.hit_enemies = set()
        sound_mgr.play("nuke")
        
        # 生成初始星镖
        for _ in range(24):
            angle = random.uniform(0, 360)
            rad = math.radians(angle)
            dist = random.randint(400, 600)
            self.stars.append({
                'x': WIDTH/2 + math.cos(rad) * dist,
                'y': HEIGHT/2 + math.sin(rad) * dist,
                'size': random.randint(8, 15),
                'target': None,
                'speed': random.uniform(12, 18),
                'trail': [],
                'color': random.choice([(75, 0, 130), (138, 43, 226), (148, 0, 211)])
            })
    
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        
        for star in self.stars[:]:
            # 寻找目标
            if star['target'] is None or star['target'] not in mobs:
                targets = [m for m in mobs if m not in self.hit_enemies]
                if targets:
                    star['target'] = random.choice(targets)
                else:
                    star['target'] = None
            
            # 追踪或直线飞行
            if star['target']:
                tx, ty = star['target'].rect.center
            else:
                tx, ty = self.owner.rect.center
            
            dx = tx - star['x']
            dy = ty - star['y']
            dist = math.hypot(dx, dy)
            
            if dist > 5:
                star['x'] += (dx / dist) * star['speed']
                star['y'] += (dy / dist) * star['speed']
            
            # 记录尾迹
            star['trail'].append((star['x'], star['y']))
            if len(star['trail']) > 10:
                star['trail'].pop(0)
            
            # 绘制尾迹
            for i, pos in enumerate(star['trail']):
                alpha = int(255 * (i / len(star['trail'])))
                size = int(star['size'] * (i / len(star['trail'])))
                pygame.draw.circle(self.image, (*star['color'], alpha), (int(pos[0]), int(pos[1])), max(1, size//2))
            
            # 绘制星镖（五角星）
            self._draw_star(self.image, star['x'], star['y'], star['size'], star['color'])
            
            # 碰撞检测
            if star['target'] and dist < 30:
                m = star['target']
                if m not in self.hit_enemies:
                    m.hp -= 200
                    self.hit_enemies.add(m)
                    FloatingText(m.rect.centerx, m.rect.top - 30, "☆STAR!", INDIGO)
                for _ in range(4):
                    Particle(m.rect.center, star['color'])
                self.stars.remove(star)
    
    def _draw_star(self, surf, x, y, size, color):
        """绘制五角星"""
        points = []
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            r = size if i % 2 == 0 else size * 0.4
            px = x + math.cos(angle) * r
            py = y + math.sin(angle) * r
            points.append((px, py))
        pygame.draw.polygon(surf, color, points)
        pygame.draw.polygon(surf, (200, 150, 255), points, 2)


class NatureWrath(pygame.sprite.Sprite):
    """大地守护者·自然之怒 - 荆棘从地面涌出"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 100
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.thorns = []
        self.hit_enemies = set()
        sound_mgr.play("nuke")
        
        # 生成荆棘位置
        for _ in range(15):
            self.thorns.append({
                'x': random.randint(50, WIDTH-50),
                'y': HEIGHT,
                'target_y': random.randint(100, HEIGHT-100),
                'height': 0,
                'max_height': random.randint(150, 300),
                'width': random.randint(20, 40),
                'phase': 'grow',
                'branches': random.randint(2, 4)
            })
    
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        
        for thorn in self.thorns:
            if thorn['phase'] == 'grow':
                thorn['height'] = min(thorn['height'] + 15, thorn['max_height'])
                if thorn['height'] >= thorn['max_height']:
                    thorn['phase'] = 'hold'
            elif thorn['phase'] == 'hold' and self.life < 30:
                thorn['phase'] = 'shrink'
            elif thorn['phase'] == 'shrink':
                thorn['height'] = max(0, thorn['height'] - 10)
            
            if thorn['height'] > 0:
                # 绘制主茎
                base_x = thorn['x']
                base_y = thorn['target_y'] + thorn['max_height'] // 2
                tip_y = base_y - thorn['height']
                
                # 荆棘主体
                points = [
                    (base_x - thorn['width']//2, base_y),
                    (base_x, tip_y),
                    (base_x + thorn['width']//2, base_y)
                ]
                pygame.draw.polygon(self.image, FOREST, points)
                pygame.draw.polygon(self.image, (100, 200, 100), points, 2)
                
                # 绘制分支刺
                for i in range(thorn['branches']):
                    branch_y = base_y - (thorn['height'] * (i + 1) / (thorn['branches'] + 1))
                    side = 1 if i % 2 == 0 else -1
                    branch_len = 30 + i * 10
                    bx = base_x + side * branch_len
                    by = branch_y - 20
                    pygame.draw.line(self.image, FOREST, (base_x, branch_y), (bx, by), 4)
                    pygame.draw.circle(self.image, (100, 200, 100), (int(bx), int(by)), 5)
                
                # 伤害检测
                thorn_rect = pygame.Rect(base_x - thorn['width'], tip_y, thorn['width']*2, thorn['height'])
                for m in list(mobs):
                    if thorn_rect.colliderect(m.rect):
                        if m not in self.hit_enemies:
                            m.hp -= 250
                            self.hit_enemies.add(m)
                            FloatingText(m.rect.centerx, m.rect.top - 30, "🌿THORN!", FOREST)
                        else:
                            m.hp -= 30
                        Particle(m.rect.center, FOREST)


class DimensionTrap(pygame.sprite.Sprite):
    """虚空编织者·维度陷阱 - 蛛网维度牢笼"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 120
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.hit_enemies = set()
        self.web_angle = 0
        self.trapped = {}  # 被困敌人
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        self.web_angle += 2
        
        cx, cy = WIDTH//2, HEIGHT//2
        
        # 绘制多层蛛网
        for layer in range(5):
            radius = 100 + layer * 80
            alpha = 150 - layer * 20
            
            # 同心环
            pygame.draw.circle(self.image, (*WEB_GRAY[:3], alpha), (cx, cy), radius, 2)
            
            # 放射线
            for i in range(12):
                angle = math.radians(i * 30 + self.web_angle * (1 if layer % 2 == 0 else -1))
                x1 = cx + math.cos(angle) * (radius - 80)
                y1 = cy + math.sin(angle) * (radius - 80)
                x2 = cx + math.cos(angle) * radius
                y2 = cy + math.sin(angle) * radius
                pygame.draw.line(self.image, (*WEB_GRAY[:3], alpha), (x1, y1), (x2, y2), 2)
        
        # 中心虚空核心
        pulse = abs(math.sin(self.life * 0.1))
        core_size = int(30 + 20 * pulse)
        pygame.draw.circle(self.image, (100, 0, 150, 200), (cx, cy), core_size)
        pygame.draw.circle(self.image, MAGENTA, (cx, cy), core_size, 3)
        
        # 敌人困住效果
        for m in list(mobs):
            dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
            if dist < 400:
                m.frozen_timer = 30  # 减速
                if m not in self.hit_enemies:
                    m.hp -= 180
                    self.hit_enemies.add(m)
                    self.trapped[m] = m.rect.center
                    FloatingText(m.rect.centerx, m.rect.top - 30, "🕸TRAPPED!", WEB_GRAY)
                else:
                    m.hp -= 20
                
                # 绘制连接线
                pygame.draw.line(self.image, (*WEB_GRAY[:3], 100), (cx, cy), m.rect.center, 1)
                
                # 吸引向中心
                pull = 0.05
                m.rect.centerx += (cx - m.rect.centerx) * pull
                m.rect.centery += (cy - m.rect.centery) * pull
                
                Particle(m.rect.center, WEB_GRAY)


class SupernovaExplosion(pygame.sprite.Sprite):
    """日冕耀斑·超新星爆发 - 太阳核心爆发"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 80
        self.radius = 30
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.hit_enemies = set()
        self.flares = []
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        
        cx, cy = self.owner.rect.center
        
        # 阶段1: 能量聚集 (60-80)
        if self.life > 60:
            charge = (80 - self.life) / 20
            core_size = int(50 * charge)
            # 吸入粒子效果
            for _ in range(3):
                angle = random.uniform(0, 360)
                dist = 200 + random.randint(0, 100)
                rad = math.radians(angle)
                px = cx + math.cos(rad) * dist
                py = cy + math.sin(rad) * dist
                pygame.draw.line(self.image, BRIGHT_ORANGE, (px, py), (cx, cy), 2)
        
        # 阶段2: 爆发 (0-60)
        else:
            self.radius += 25
            
            # 太阳核心
            for r in range(5, 0, -1):
                color_intensity = int(255 - r * 30)
                pygame.draw.circle(self.image, (255, color_intensity, 0), (cx, cy), 30 + r * 5)
            
            # 放射状火焰
            num_rays = 16
            for i in range(num_rays):
                angle = (i * 360 / num_rays) + self.life * 3
                rad = math.radians(angle)
                
                # 火焰长度随机波动
                ray_len = self.radius + random.randint(-30, 30)
                end_x = cx + math.cos(rad) * ray_len
                end_y = cy + math.sin(rad) * ray_len
                
                # 火焰渐变
                for w in range(8, 0, -1):
                    alpha = int(200 * (w / 8))
                    pygame.draw.line(self.image, (255, 150, 0, alpha), (cx, cy), (end_x, end_y), w)
            
            # 外层冲击波
            wave_alpha = int(150 * (self.life / 60))
            pygame.draw.circle(self.image, (255, 200, 0, wave_alpha), (cx, cy), self.radius, 5)
            pygame.draw.circle(self.image, (255, 100, 0, wave_alpha//2), (cx, cy), self.radius + 20, 3)
            
            # 伤害判定
            if self.life % 3 == 0:
                for m in list(mobs):
                    dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
                    if dist < self.radius:
                        if m not in self.hit_enemies:
                            m.hp -= 350
                            self.hit_enemies.add(m)
                            FloatingText(m.rect.centerx, m.rect.top - 30, "☀NOVA!", BRIGHT_ORANGE)
                        else:
                            m.hp -= 60
                        for _ in range(3):
                            Particle(m.rect.center, BRIGHT_ORANGE)


class QuantumMatrix(pygame.sprite.Sprite):
    """量子裁决者·矩阵重置 - 几何量子打击"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 90
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.hit_enemies = set()
        self.shapes = []
        sound_mgr.play("nuke")
        
        # 生成几何图形
        for _ in range(12):
            self.shapes.append({
                'x': random.randint(100, WIDTH-100),
                'y': random.randint(100, HEIGHT-100),
                'size': random.randint(30, 60),
                'type': random.choice(['triangle', 'square', 'hexagon']),
                'angle': random.randint(0, 360),
                'pulse': random.uniform(0, math.pi * 2)
            })
    
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        
        # 背景网格
        grid_alpha = int(50 * (self.life / 90))
        for x in range(0, WIDTH, 40):
            pygame.draw.line(self.image, (*NEON_PURPLE[:3], grid_alpha), (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 40):
            pygame.draw.line(self.image, (*NEON_PURPLE[:3], grid_alpha), (0, y), (WIDTH, y), 1)
        
        for shape in self.shapes:
            shape['angle'] += 3
            shape['pulse'] += 0.1
            pulse_scale = 1 + 0.2 * math.sin(shape['pulse'])
            size = shape['size'] * pulse_scale
            
            # 绘制几何图形
            points = []
            if shape['type'] == 'triangle':
                sides = 3
            elif shape['type'] == 'square':
                sides = 4
            else:
                sides = 6
            
            for i in range(sides):
                angle = math.radians(shape['angle'] + i * 360 / sides)
                px = shape['x'] + math.cos(angle) * size
                py = shape['y'] + math.sin(angle) * size
                points.append((px, py))
            
            # 外框
            pygame.draw.polygon(self.image, NEON_PURPLE, points, 3)
            # 内部填充
            inner_points = [(shape['x'] + (p[0]-shape['x'])*0.6, shape['y'] + (p[1]-shape['y'])*0.6) for p in points]
            pygame.draw.polygon(self.image, (*NEON_PURPLE[:3], 100), inner_points)
            
            # 连接线到中心
            pygame.draw.line(self.image, (*NEON_PURPLE[:3], 80), (shape['x'], shape['y']), (WIDTH//2, HEIGHT//2), 1)
            
            # 伤害判定
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - shape['x'], m.rect.centery - shape['y'])
                if dist < size:
                    if m not in self.hit_enemies:
                        m.hp -= 180
                        self.hit_enemies.add(m)
                        FloatingText(m.rect.centerx, m.rect.top - 30, "⬡MATRIX!", NEON_PURPLE)
                    else:
                        m.hp -= 25
                    Particle(m.rect.center, NEON_PURPLE)


class EclipseVortex(pygame.sprite.Sprite):
    """日食幽灵·黑日降临 - 双核吸收黑洞"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 100
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.hit_enemies = set()
        self.angle = 0
        self.absorbed_hp = 0
        sound_mgr.play("blackhole")
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            # 吸收转化护盾
            if hasattr(self.owner, 'shield'):
                self.owner.shield = min(self.owner.max_shield + 100, self.owner.shield + self.absorbed_hp // 3)
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        self.angle += 5
        
        cx, cy = self.owner.rect.center
        
        # 双核黑洞
        offsets = [(-60, -30), (60, -30)]
        for ox, oy in offsets:
            hx, hy = cx + ox, cy + oy
            
            # 黑洞核心
            pygame.draw.circle(self.image, (20, 10, 40), (hx, hy), 40)
            pygame.draw.circle(self.image, (100, 50, 180), (hx, hy), 40, 3)
            
            # 旋转吸积盘
            for ring in range(3):
                ring_radius = 50 + ring * 20
                for i in range(8):
                    angle = math.radians(self.angle + i * 45 + ring * 15)
                    px = hx + math.cos(angle) * ring_radius
                    py = hy + math.sin(angle) * ring_radius
                    size = 5 - ring
                    pygame.draw.circle(self.image, (150, 80, 220), (int(px), int(py)), size)
        
        # 中央连接光束
        pygame.draw.line(self.image, (100, 50, 180, 150), (cx - 60, cy - 30), (cx + 60, cy - 30), 3)
        
        # 吸收和伤害
        for m in list(mobs):
            dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
            if dist < 200:
                # 吸引
                pull = 0.08 * (1 - dist / 200)
                m.rect.centerx += (cx - m.rect.centerx) * pull
                m.rect.centery += (cy - m.rect.centery) * pull
                
                if m not in self.hit_enemies:
                    dmg = 220
                    m.hp -= dmg
                    self.absorbed_hp += dmg
                    self.hit_enemies.add(m)
                    FloatingText(m.rect.centerx, m.rect.top - 30, "🌑ECLIPSE!", (100, 50, 180))
                else:
                    m.hp -= 30
                    self.absorbed_hp += 30
                
                Particle(m.rect.center, (100, 50, 180))


class PrismBurst(pygame.sprite.Sprite):
    """棱镜分光·光谱爆裂 - 彩虹光线分裂"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 70
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.hit_enemies = set()
        self.beams = []
        self.colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 127, 255), (75, 0, 130), (148, 0, 211)]
        sound_mgr.play("laser")
        
        # 初始光束
        for i, color in enumerate(self.colors):
            angle = i * (360 / len(self.colors))
            self.beams.append({
                'angle': angle,
                'length': 0,
                'max_length': 500,
                'color': color,
                'width': 8
            })
    
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        
        cx, cy = self.owner.rect.center
        
        # 中心棱镜
        prism_size = 30
        prism_points = []
        for i in range(6):
            angle = math.radians(i * 60 + self.life * 2)
            px = cx + math.cos(angle) * prism_size
            py = cy + math.sin(angle) * prism_size
            prism_points.append((px, py))
        pygame.draw.polygon(self.image, (200, 220, 255), prism_points)
        pygame.draw.polygon(self.image, WHITE, prism_points, 2)
        
        for beam in self.beams:
            beam['angle'] += 2  # 旋转
            beam['length'] = min(beam['length'] + 20, beam['max_length'])
            
            rad = math.radians(beam['angle'])
            end_x = cx + math.cos(rad) * beam['length']
            end_y = cy + math.sin(rad) * beam['length']
            
            # 主光束
            pygame.draw.line(self.image, beam['color'], (cx, cy), (end_x, end_y), beam['width'])
            # 光晕
            pygame.draw.line(self.image, (*beam['color'], 100), (cx, cy), (end_x, end_y), beam['width'] + 4)
            
            # 分裂效果（每条光束分出3条子光束）
            if beam['length'] > 200:
                for split in [-20, 0, 20]:
                    split_rad = math.radians(beam['angle'] + split)
                    split_start_x = cx + math.cos(rad) * 200
                    split_start_y = cy + math.sin(rad) * 200
                    split_end_x = split_start_x + math.cos(split_rad) * (beam['length'] - 200)
                    split_end_y = split_start_y + math.sin(split_rad) * (beam['length'] - 200)
                    pygame.draw.line(self.image, beam['color'], (split_start_x, split_start_y), (split_end_x, split_end_y), 3)
            
            # 伤害检测
            for m in list(mobs):
                # 检测是否在光束路径上
                mx, my = m.rect.center
                # 简化：检测距离光束端点的距离
                dist_to_beam = abs((end_y - cy) * mx - (end_x - cx) * my + end_x * cy - end_y * cx) / max(1, beam['length'])
                dist_along = math.hypot(mx - cx, my - cy)
                
                if dist_to_beam < 40 and dist_along < beam['length']:
                    if m not in self.hit_enemies:
                        m.hp -= 200
                        self.hit_enemies.add(m)
                        FloatingText(m.rect.centerx, m.rect.top - 30, "🌈PRISM!", beam['color'])
                    else:
                        m.hp -= 35
                    Particle(m.rect.center, beam['color'])


class SoulHarvest(pygame.sprite.Sprite):
    """死灵骑士·亡灵收割 - 灵魂吸取风暴"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 100
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.hit_enemies = set()
        self.souls = []
        self.total_heal = 0
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            # 最终治疗
            if hasattr(self.owner, 'hp') and hasattr(self.owner, 'max_hp'):
                heal = self.total_heal // 4
                self.owner.hp = min(self.owner.max_hp, self.owner.hp + heal)
                if heal > 0:
                    FloatingText(self.owner.rect.centerx, self.owner.rect.top - 50, f"+{heal} HP", LIME)
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        
        cx, cy = self.owner.rect.center
        
        # 死灵光环
        aura_radius = 300
        pulse = abs(math.sin(self.life * 0.1))
        for ring in range(3):
            r = aura_radius - ring * 50
            alpha = int(80 - ring * 20)
            pygame.draw.circle(self.image, (200, 50, 150, alpha), (cx, cy), int(r * (0.8 + 0.2 * pulse)), 3)
        
        # 骷髅符文
        for i in range(8):
            angle = math.radians(i * 45 + self.life * 2)
            rx = cx + math.cos(angle) * 150
            ry = cy + math.sin(angle) * 150
            # 简单骷髅图案
            pygame.draw.circle(self.image, (200, 50, 150), (int(rx), int(ry)), 15)
            pygame.draw.circle(self.image, (50, 0, 50), (int(rx) - 5, int(ry) - 3), 3)
            pygame.draw.circle(self.image, (50, 0, 50), (int(rx) + 5, int(ry) - 3), 3)
            pygame.draw.line(self.image, (50, 0, 50), (rx - 4, ry + 5), (rx + 4, ry + 5), 2)
        
        # 灵魂收集
        for m in list(mobs):
            dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
            if dist < aura_radius:
                if m not in self.hit_enemies:
                    dmg = 250
                    m.hp -= dmg
                    self.total_heal += dmg
                    self.hit_enemies.add(m)
                    FloatingText(m.rect.centerx, m.rect.top - 30, "💀HARVEST!", (200, 50, 150))
                    # 生成灵魂
                    self.souls.append({
                        'x': m.rect.centerx,
                        'y': m.rect.centery,
                        'size': 15
                    })
                else:
                    m.hp -= 30
                    self.total_heal += 30
                
                Particle(m.rect.center, (200, 50, 150))
        
        # 更新灵魂飞向玩家
        for soul in self.souls[:]:
            dx = cx - soul['x']
            dy = cy - soul['y']
            dist = math.hypot(dx, dy)
            if dist < 20:
                self.souls.remove(soul)
                continue
            
            speed = 8
            soul['x'] += (dx / dist) * speed
            soul['y'] += (dy / dist) * speed
            
            # 绘制灵魂
            pygame.draw.circle(self.image, (200, 100, 180), (int(soul['x']), int(soul['y'])), soul['size'])
            pygame.draw.circle(self.image, (255, 150, 200), (int(soul['x']), int(soul['y'])), soul['size'] - 3)


class VoidRift(pygame.sprite.Sprite):
    """虚空幻影（void）·虚空撕裂 - 维度裂隙"""
    def __init__(self, pos):
        super().__init__()
        all_sprites.add(self)
        self.pos = pos
        self.life = 150
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.hit_enemies = set()
        self.rifts = []
        self.angle = 0
        sound_mgr.play("blackhole")
        
        # 生成裂隙
        for i in range(5):
            angle = i * 72
            rad = math.radians(angle)
            self.rifts.append({
                'x': pos[0] + math.cos(rad) * 150,
                'y': pos[1] + math.sin(rad) * 150,
                'angle': angle,
                'width': 0,
                'max_width': 100
            })
    
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        self.angle += 1
        
        cx, cy = self.pos
        
        # 中心虚空核心
        core_pulse = abs(math.sin(self.life * 0.1))
        core_size = int(40 + 20 * core_pulse)
        pygame.draw.circle(self.image, (30, 0, 50), (int(cx), int(cy)), core_size)
        pygame.draw.circle(self.image, MAGENTA, (int(cx), int(cy)), core_size, 3)
        
        # 虚空粒子环
        for i in range(20):
            p_angle = math.radians(self.angle * 2 + i * 18)
            p_dist = 60 + 30 * math.sin(self.life * 0.1 + i)
            px = cx + math.cos(p_angle) * p_dist
            py = cy + math.sin(p_angle) * p_dist
            pygame.draw.circle(self.image, (150, 0, 200), (int(px), int(py)), 3)
        
        for rift in self.rifts:
            rift['angle'] += 0.5
            rift['width'] = min(rift['width'] + 3, rift['max_width'])
            
            # 绘制裂隙（椭圆形撕裂）
            rx, ry = rift['x'], rift['y']
            w = rift['width']
            h = w // 3
            
            # 裂隙主体
            rift_surf = pygame.Surface((w * 2, h * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(rift_surf, (50, 0, 80), (0, 0, w * 2, h * 2))
            pygame.draw.ellipse(rift_surf, MAGENTA, (0, 0, w * 2, h * 2), 2)
            
            # 旋转
            rotated = pygame.transform.rotate(rift_surf, rift['angle'])
            rot_rect = rotated.get_rect(center=(rx, ry))
            self.image.blit(rotated, rot_rect)
            
            # 连接到中心
            pygame.draw.line(self.image, (100, 0, 150, 100), (cx, cy), (rx, ry), 2)
            
            # 伤害检测
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - rx, m.rect.centery - ry)
                if dist < w:
                    if m not in self.hit_enemies:
                        m.hp -= 200
                        self.hit_enemies.add(m)
                        FloatingText(m.rect.centerx, m.rect.top - 30, "🌀VOID!", MAGENTA)
                    else:
                        m.hp -= 25
                    Particle(m.rect.center, MAGENTA)
        
        # 吸引效果
        for m in list(mobs):
            dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
            if dist < 250:
                pull = 0.04 * (1 - dist / 250)
                m.rect.centerx += (cx - m.rect.centerx) * pull
                m.rect.centery += (cy - m.rect.centery) * pull


# ==============================================================================
#   第二大招特效类（G键释放）
# ==============================================================================

class OmegaLaser(pygame.sprite.Sprite):
    """霓虹突击者·欧米伽激光 - 三道交叉激光扫射"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 80
        self.angle = -30
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.hit_enemies = {}
        sound_mgr.play("laser")
        
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        self.angle += 1.5  # 扫射角度
        
        cx, cy = self.owner.rect.center
        
        # 三道激光
        for i, offset in enumerate([-30, 0, 30]):
            angle = self.angle + offset
            rad = math.radians(angle - 90)
            
            # 激光端点
            end_x = cx + math.cos(rad) * HEIGHT
            end_y = cy + math.sin(rad) * HEIGHT
            
            # 多层激光效果
            for w, alpha in [(12, 80), (8, 150), (4, 255), (2, 255)]:
                color = (0, 255, 255, alpha) if w > 4 else (255, 255, 255, alpha)
                pygame.draw.line(self.image, color, (cx, cy), (end_x, end_y), w)
            
            # 伤害检测（沿激光线）
            for m in list(mobs):
                # 点到线距离
                mx, my = m.rect.center
                dist = abs((end_y - cy) * mx - (end_x - cx) * my + end_x * cy - end_y * cx) / max(1, math.hypot(end_x - cx, end_y - cy))
                if dist < 30:
                    if m not in self.hit_enemies:
                        self.hit_enemies[m] = 0
                        m.hp -= 180
                        FloatingText(m.rect.centerx, m.rect.top - 30, "ΩLASER!", CYAN)
                    elif self.hit_enemies[m] < 3:
                        m.hp -= 40
                        self.hit_enemies[m] += 1
                    Particle(m.rect.center, CYAN)


class PhantomClone(pygame.sprite.Sprite):
    """虚空幻影·分身乱舞 - 生成多个攻击分身"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 90
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.clones = []
        self.hit_enemies = set()
        sound_mgr.play("dash")
        
        # 生成4个分身
        for i in range(4):
            angle = i * 90
            rad = math.radians(angle)
            self.clones.append({
                'x': owner.rect.centerx + math.cos(rad) * 150,
                'y': owner.rect.centery + math.sin(rad) * 150,
                'angle': angle,
                'attack_timer': i * 10
            })
    
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        
        for clone in self.clones:
            clone['angle'] += 5
            rad = math.radians(clone['angle'])
            clone['x'] = self.owner.rect.centerx + math.cos(rad) * 120
            clone['y'] = self.owner.rect.centery + math.sin(rad) * 120
            
            # 绘制分身（紫色幻影）
            cx, cy = int(clone['x']), int(clone['y'])
            
            # 幻影轮廓
            pygame.draw.polygon(self.image, (200, 0, 255, 150), [
                (cx, cy - 25), (cx + 15, cy + 15), (cx, cy + 5), (cx - 15, cy + 15)
            ])
            pygame.draw.polygon(self.image, MAGENTA, [
                (cx, cy - 25), (cx + 15, cy + 15), (cx, cy + 5), (cx - 15, cy + 15)
            ], 2)
            
            # 分身攻击
            clone['attack_timer'] += 1
            if clone['attack_timer'] % 15 == 0:
                # 向最近敌人发射
                for m in list(mobs):
                    dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
                    if dist < 200:
                        if m not in self.hit_enemies:
                            m.hp -= 100
                            self.hit_enemies.add(m)
                        else:
                            m.hp -= 30
                        Particle(m.rect.center, MAGENTA)
                        pygame.draw.line(self.image, MAGENTA, (cx, cy), m.rect.center, 3)


class MeteorStrike(pygame.sprite.Sprite):
    """钢铁泰坦·陨石轰炸 - 召唤陨石群"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 100
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.meteors = []
        self.hit_enemies = set()
        sound_mgr.play("nuke")
        
        # 生成陨石
        for _ in range(8):
            self.meteors.append({
                'x': random.randint(100, WIDTH - 100),
                'y': -50 - random.randint(0, 200),
                'size': random.randint(30, 50),
                'speed': random.uniform(8, 12),
                'trail': [],
                'exploded': False
            })
    
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        
        for meteor in self.meteors:
            if meteor['exploded']:
                continue
            
            meteor['y'] += meteor['speed']
            meteor['trail'].append((meteor['x'], meteor['y']))
            if len(meteor['trail']) > 15:
                meteor['trail'].pop(0)
            
            # 绘制尾迹
            for i, pos in enumerate(meteor['trail']):
                alpha = int(200 * (i / len(meteor['trail'])))
                size = int(meteor['size'] * (i / len(meteor['trail'])) * 0.5)
                pygame.draw.circle(self.image, (255, 100, 0, alpha), (int(pos[0]), int(pos[1])), max(1, size))
            
            # 绘制陨石
            pygame.draw.circle(self.image, (200, 80, 0), (int(meteor['x']), int(meteor['y'])), meteor['size'])
            pygame.draw.circle(self.image, (255, 150, 50), (int(meteor['x']), int(meteor['y'])), meteor['size'] - 5)
            pygame.draw.circle(self.image, ORANGE, (int(meteor['x']), int(meteor['y'])), meteor['size'], 3)
            
            # 落地爆炸
            if meteor['y'] > HEIGHT - 50:
                meteor['exploded'] = True
                # 爆炸伤害
                for m in list(mobs):
                    dist = math.hypot(m.rect.centerx - meteor['x'], m.rect.centery - meteor['y'])
                    if dist < 150:
                        if m not in self.hit_enemies:
                            m.hp -= 300
                            self.hit_enemies.add(m)
                        else:
                            m.hp -= 80
                        for _ in range(5):
                            Particle(m.rect.center, ORANGE)
                # 爆炸视觉效果
                for _ in range(10):
                    Particle((meteor['x'], meteor['y']), (255, random.randint(100, 200), 0))


class ChainLightning(pygame.sprite.Sprite):
    """雷霆战鹰·连锁闪电 - 闪电在敌人间跳跃"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 60
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.chains = []
        self.hit_enemies = set()
        sound_mgr.play("zap")
        self._start_chain()
        
    def _start_chain(self):
        """从玩家开始连锁"""
        targets = list(mobs)
        if not targets:
            return
        
        current = self.owner.rect.center
        for _ in range(min(10, len(targets))):
            # 找最近未击中的敌人
            nearest = None
            min_dist = 300
            for m in targets:
                if m not in self.hit_enemies:
                    dist = math.hypot(m.rect.centerx - current[0], m.rect.centery - current[1])
                    if dist < min_dist:
                        min_dist = dist
                        nearest = m
            
            if nearest:
                self.chains.append({
                    'start': current,
                    'end': nearest.rect.center,
                    'life': 20
                })
                nearest.hp -= 150
                self.hit_enemies.add(nearest)
                FloatingText(nearest.rect.centerx, nearest.rect.top - 30, "⚡CHAIN!", YELLOW)
                current = nearest.rect.center
            else:
                break
    
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        
        for chain in self.chains[:]:
            chain['life'] -= 1
            if chain['life'] <= 0:
                self.chains.remove(chain)
                continue
            
            # 绘制锯齿闪电
            points = [chain['start']]
            dx = chain['end'][0] - chain['start'][0]
            dy = chain['end'][1] - chain['start'][1]
            for i in range(1, 6):
                t = i / 6
                px = chain['start'][0] + dx * t + random.randint(-20, 20)
                py = chain['start'][1] + dy * t + random.randint(-20, 20)
                points.append((px, py))
            points.append(chain['end'])
            
            alpha = int(255 * (chain['life'] / 20))
            for i in range(len(points) - 1):
                pygame.draw.line(self.image, (255, 255, 0, alpha), points[i], points[i+1], 4)
                pygame.draw.line(self.image, (255, 255, 255, alpha), points[i], points[i+1], 2)


class AcidRain(pygame.sprite.Sprite):
    """剧毒蝰蛇·酸雨倾盆 - 全屏毒液雨"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 120
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.drops = []
        self.pools = []
        self.hit_enemies = {}
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        
        # 生成新雨滴
        if self.life > 30 and self.life % 2 == 0:
            for _ in range(3):
                self.drops.append({
                    'x': random.randint(0, WIDTH),
                    'y': -10,
                    'speed': random.uniform(10, 15)
                })
        
        # 更新雨滴
        for drop in self.drops[:]:
            drop['y'] += drop['speed']
            
            # 绘制雨滴
            pygame.draw.line(self.image, LIME, (drop['x'], drop['y']), (drop['x'], drop['y'] + 15), 2)
            
            if drop['y'] > HEIGHT:
                self.drops.remove(drop)
                # 生成毒池
                self.pools.append({
                    'x': drop['x'],
                    'y': HEIGHT - 20,
                    'size': 30,
                    'life': 60
                })
        
        # 更新毒池
        for pool in self.pools[:]:
            pool['life'] -= 1
            if pool['life'] <= 0:
                self.pools.remove(pool)
                continue
            
            alpha = int(150 * (pool['life'] / 60))
            pygame.draw.ellipse(self.image, (*LIME[:3], alpha), 
                              (pool['x'] - pool['size'], pool['y'] - 10, pool['size'] * 2, 20))
            
            # 毒池伤害
            for m in list(mobs):
                if abs(m.rect.centerx - pool['x']) < pool['size'] and m.rect.bottom > HEIGHT - 50:
                    if m not in self.hit_enemies:
                        self.hit_enemies[m] = 0
                        m.hp -= 80
                    elif self.hit_enemies[m] < 5:
                        m.hp -= 20
                        self.hit_enemies[m] += 1
                    m.poison_timer = 30


class GhostWail(pygame.sprite.Sprite):
    """幽灵收割者·亡魂哀嚎 - 释放尖啸灵魂波"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 70
        self.radius = 0
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.hit_enemies = set()
        self.ghosts = []
        sound_mgr.play("nuke")
        
        # 生成幽灵
        for i in range(6):
            angle = i * 60
            self.ghosts.append({
                'angle': angle,
                'dist': 50,
                'size': 20
            })
    
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        self.radius += 8
        
        cx, cy = self.owner.rect.center
        
        # 音波环
        wave_alpha = int(150 * (self.life / 70))
        for i in range(3):
            r = self.radius - i * 30
            if r > 0:
                pygame.draw.circle(self.image, (150, 100, 255, wave_alpha - i * 30), (cx, cy), r, 3)
        
        # 幽灵环绕
        for ghost in self.ghosts:
            ghost['angle'] += 4
            ghost['dist'] = min(ghost['dist'] + 5, self.radius * 0.8)
            
            rad = math.radians(ghost['angle'])
            gx = cx + math.cos(rad) * ghost['dist']
            gy = cy + math.sin(rad) * ghost['dist']
            
            # 绘制幽灵
            pygame.draw.circle(self.image, (180, 150, 255, 150), (int(gx), int(gy)), ghost['size'])
            pygame.draw.circle(self.image, (150, 100, 255), (int(gx), int(gy)), ghost['size'] - 5)
            # 眼睛
            pygame.draw.circle(self.image, (50, 0, 80), (int(gx) - 5, int(gy) - 3), 3)
            pygame.draw.circle(self.image, (50, 0, 80), (int(gx) + 5, int(gy) - 3), 3)
        
        # 伤害判定
        for m in list(mobs):
            dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
            if dist < self.radius and dist > self.radius - 50:
                if m not in self.hit_enemies:
                    m.hp -= 220
                    self.hit_enemies.add(m)
                    FloatingText(m.rect.centerx, m.rect.top - 30, "👻WAIL!", (150, 100, 255))
                    m.frozen_timer = 60  # 恐惧效果
                Particle(m.rect.center, (150, 100, 255))


class AuroraWave(pygame.sprite.Sprite):
    """极光女神·极光冲击波 - 全屏极光爆发"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 60
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.waves = []
        self.hit_enemies = set()
        sound_mgr.play("nuke")
        
        # 从玩家位置发出多波
        for i in range(5):
            self.waves.append({
                'radius': 30 + i * 30,
                'max_radius': 500,
                'color': [(0, 255, 200), (0, 200, 255), (100, 255, 200), (0, 255, 150), (50, 200, 255)][i]
            })
    
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        
        cx, cy = self.owner.rect.center
        
        for wave in self.waves:
            wave['radius'] += 12
            if wave['radius'] > wave['max_radius']:
                continue
            
            # 绘制极光波
            alpha = int(200 * (1 - wave['radius'] / wave['max_radius']))
            for w in range(8, 0, -2):
                pygame.draw.circle(self.image, (*wave['color'], alpha), (cx, cy), int(wave['radius']), w)
            
            # 伤害判定
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
                if abs(dist - wave['radius']) < 30:
                    if m not in self.hit_enemies:
                        m.hp -= 180
                        self.hit_enemies.add(m)
                        FloatingText(m.rect.centerx, m.rect.top - 30, "🌊WAVE!", TEAL)
                    else:
                        m.hp -= 30
                    m.frozen_timer = 30
                    Particle(m.rect.center, wave['color'])


class BladeStorm(pygame.sprite.Sprite):
    """绯红之刃·刀刃风暴 - 环绕飞刃护盾"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 120
        self.angle = 0
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.hit_timers = {}
        self.blades = []
        sound_mgr.play("laser")
        
        # 生成12把飞刃
        for i in range(12):
            self.blades.append({
                'angle': i * 30,
                'dist': 100,
                'length': 40
            })
    
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        self.angle += 8
        
        cx, cy = self.owner.rect.center
        
        for blade in self.blades:
            blade['angle'] += 8
            rad = math.radians(blade['angle'])
            bx = cx + math.cos(rad) * blade['dist']
            by = cy + math.sin(rad) * blade['dist']
            
            # 刀刃方向
            blade_rad = rad + math.pi / 2
            tip_x = bx + math.cos(blade_rad) * blade['length']
            tip_y = by + math.sin(blade_rad) * blade['length']
            base_x = bx - math.cos(blade_rad) * blade['length'] * 0.3
            base_y = by - math.sin(blade_rad) * blade['length'] * 0.3
            
            # 绘制刀刃
            pygame.draw.line(self.image, (255, 200, 200), (base_x, base_y), (tip_x, tip_y), 6)
            pygame.draw.line(self.image, CRIMSON, (base_x, base_y), (tip_x, tip_y), 3)
            pygame.draw.circle(self.image, (255, 100, 100), (int(tip_x), int(tip_y)), 4)
            
            # 伤害检测
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - bx, m.rect.centery - by)
                if dist < 50:
                    if m not in self.hit_timers or self.hit_timers[m] <= 0:
                        m.hp -= 80
                        self.hit_timers[m] = 10
                        Particle(m.rect.center, CRIMSON)
        
        # 更新冷却
        for m in list(self.hit_timers.keys()):
            self.hit_timers[m] -= 1


class GravityWell(pygame.sprite.Sprite):
    """星界潜行者·引力陷阱 - 创建吸引力场"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 100
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.wells = []
        self.hit_enemies = {}
        sound_mgr.play("blackhole")
        
        # 生成3个引力井
        positions = [(WIDTH * 0.25, HEIGHT * 0.4), (WIDTH * 0.5, HEIGHT * 0.5), (WIDTH * 0.75, HEIGHT * 0.4)]
        for pos in positions:
            self.wells.append({
                'x': pos[0],
                'y': pos[1],
                'radius': 80,
                'angle': 0
            })
    
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        
        for well in self.wells:
            well['angle'] += 3
            wx, wy = well['x'], well['y']
            
            # 绘制引力场
            for ring in range(4):
                r = well['radius'] - ring * 15
                alpha = 100 - ring * 20
                pygame.draw.circle(self.image, (75, 0, 130, alpha), (int(wx), int(wy)), r, 2)
            
            # 旋转粒子
            for i in range(8):
                angle = math.radians(well['angle'] + i * 45)
                px = wx + math.cos(angle) * well['radius'] * 0.7
                py = wy + math.sin(angle) * well['radius'] * 0.7
                pygame.draw.circle(self.image, INDIGO, (int(px), int(py)), 4)
            
            # 吸引和伤害
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - wx, m.rect.centery - wy)
                if dist < well['radius'] * 1.5:
                    # 吸引
                    pull = 0.1 * (1 - dist / (well['radius'] * 1.5))
                    m.rect.centerx += (wx - m.rect.centerx) * pull
                    m.rect.centery += (wy - m.rect.centery) * pull
                    
                    if dist < well['radius']:
                        if m not in self.hit_enemies:
                            self.hit_enemies[m] = 0
                            m.hp -= 120
                            FloatingText(m.rect.centerx, m.rect.top - 30, "🌀GRAVITY!", INDIGO)
                        elif self.hit_enemies[m] < 8:
                            m.hp -= 25
                            self.hit_enemies[m] += 1


class EarthShield(pygame.sprite.Sprite):
    """大地守护者·岩石护盾 - 召唤岩石防御"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 150
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rocks = []
        self.hit_enemies = set()
        sound_mgr.play("nuke")
        
        # 生成岩石
        for i in range(8):
            angle = i * 45
            self.rocks.append({
                'angle': angle,
                'dist': 80,
                'size': random.randint(20, 35),
                'hp': 100
            })
    
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        
        cx, cy = self.owner.rect.center
        
        # 更新岩石位置（跟随玩家）
        for rock in self.rocks[:]:
            if rock['hp'] <= 0:
                self.rocks.remove(rock)
                continue
            
            rock['angle'] += 1.5
            rad = math.radians(rock['angle'])
            rx = cx + math.cos(rad) * rock['dist']
            ry = cy + math.sin(rad) * rock['dist']
            
            # 绘制岩石
            points = []
            for i in range(6):
                a = math.radians(i * 60 + rock['angle'])
                r = rock['size'] * (0.7 + random.uniform(0, 0.3))
                points.append((rx + math.cos(a) * r, ry + math.sin(a) * r))
            pygame.draw.polygon(self.image, (100, 80, 60), points)
            pygame.draw.polygon(self.image, (60, 50, 40), points, 3)
            pygame.draw.polygon(self.image, FOREST, points, 2)
            
            # 阻挡敌人子弹
            for eb in list(enemy_bullets):
                dist = math.hypot(eb.rect.centerx - rx, eb.rect.centery - ry)
                if dist < rock['size']:
                    rock['hp'] -= 20
                    eb.kill()
                    Particle((rx, ry), FOREST)
            
            # 撞击敌人
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - rx, m.rect.centery - ry)
                if dist < rock['size'] + 20:
                    if m not in self.hit_enemies:
                        m.hp -= 150
                        self.hit_enemies.add(m)
                        Particle(m.rect.center, FOREST)


class WebTrap(pygame.sprite.Sprite):
    """虚空编织者·蛛网陷阱 - 放置多个减速网"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 180
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.webs = []
        self.hit_enemies = {}
        sound_mgr.play("nuke")
        
        # 随机放置蛛网
        for _ in range(6):
            self.webs.append({
                'x': random.randint(100, WIDTH - 100),
                'y': random.randint(100, HEIGHT - 100),
                'size': random.randint(60, 100),
                'angle': random.randint(0, 360)
            })
    
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        
        for web in self.webs:
            web['angle'] += 0.5
            wx, wy = web['x'], web['y']
            size = web['size']
            
            # 绘制蛛网
            # 同心环
            for ring in range(4):
                r = size * (ring + 1) / 4
                alpha = 120 - ring * 20
                pygame.draw.circle(self.image, (*WEB_GRAY[:3], alpha), (int(wx), int(wy)), int(r), 1)
            
            # 放射线
            for i in range(8):
                angle = math.radians(i * 45 + web['angle'])
                ex = wx + math.cos(angle) * size
                ey = wy + math.sin(angle) * size
                pygame.draw.line(self.image, (*WEB_GRAY[:3], 100), (wx, wy), (ex, ey), 1)
            
            # 减速和伤害
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - wx, m.rect.centery - wy)
                if dist < size:
                    m.frozen_timer = 20  # 持续减速
                    if m not in self.hit_enemies:
                        self.hit_enemies[m] = 0
                        m.hp -= 60
                    elif self.hit_enemies[m] < 10:
                        m.hp -= 10
                        self.hit_enemies[m] += 1


class SolarFlare(pygame.sprite.Sprite):
    """日冕耀斑·太阳耀斑 - 持续燃烧光柱"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 80
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.flares = []
        self.hit_enemies = {}
        sound_mgr.play("laser")
        
        # 生成耀斑柱
        for i in range(5):
            self.flares.append({
                'x': 100 + i * (WIDTH - 200) / 4,
                'width': 60,
                'intensity': random.uniform(0.8, 1.2)
            })
    
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        
        for flare in self.flares:
            fx = flare['x']
            fw = flare['width']
            intensity = flare['intensity']
            
            # 闪烁效果
            pulse = abs(math.sin(self.life * 0.2)) * intensity
            
            # 绘制火焰柱
            for layer in range(5):
                w = fw - layer * 10
                alpha = int((200 - layer * 30) * pulse)
                color = (255, 200 - layer * 30, 0, alpha)
                pygame.draw.rect(self.image, color, (fx - w/2, 0, w, HEIGHT))
            
            # 顶部火焰
            for i in range(10):
                flame_x = fx + random.randint(-int(fw/2), int(fw/2))
                flame_y = random.randint(0, 100)
                flame_size = random.randint(10, 30)
                pygame.draw.circle(self.image, (255, 150, 0, 150), (int(flame_x), flame_y), flame_size)
            
            # 伤害判定
            for m in list(mobs):
                if abs(m.rect.centerx - fx) < fw:
                    if m not in self.hit_enemies:
                        self.hit_enemies[m] = 0
                        m.hp -= 100
                        FloatingText(m.rect.centerx, m.rect.top - 30, "🔥FLARE!", BRIGHT_ORANGE)
                    elif self.hit_enemies[m] < 10:
                        m.hp -= 25
                        self.hit_enemies[m] += 1
                    Particle(m.rect.center, BRIGHT_ORANGE)


class DataCorruption(pygame.sprite.Sprite):
    """量子裁决者·数据腐蚀 - 病毒式扩散攻击"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 100
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.corrupted = set()
        self.glitch_rects = []
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        
        # 生成故障方块
        if self.life % 3 == 0:
            for _ in range(5):
                self.glitch_rects.append({
                    'x': random.randint(0, WIDTH),
                    'y': random.randint(0, HEIGHT),
                    'w': random.randint(20, 80),
                    'h': random.randint(10, 40),
                    'life': 15,
                    'color': random.choice([NEON_PURPLE, (255, 0, 100), (0, 255, 200), (255, 255, 0)])
                })
        
        # 绘制故障效果
        for rect in self.glitch_rects[:]:
            rect['life'] -= 1
            if rect['life'] <= 0:
                self.glitch_rects.remove(rect)
                continue
            
            alpha = int(200 * (rect['life'] / 15))
            # 故障条纹
            pygame.draw.rect(self.image, (*rect['color'][:3], alpha), 
                           (rect['x'], rect['y'], rect['w'], rect['h']))
            # 边框
            pygame.draw.rect(self.image, (*NEON_PURPLE[:3], alpha), 
                           (rect['x'], rect['y'], rect['w'], rect['h']), 2)
        
        # 病毒感染敌人
        for m in list(mobs):
            # 检查是否在故障区域
            for rect in self.glitch_rects:
                if (rect['x'] < m.rect.centerx < rect['x'] + rect['w'] and
                    rect['y'] < m.rect.centery < rect['y'] + rect['h']):
                    if m not in self.corrupted:
                        m.hp -= 200
                        self.corrupted.add(m)
                        FloatingText(m.rect.centerx, m.rect.top - 30, "💀CORRUPT!", NEON_PURPLE)
                        # 感染扩散
                        for m2 in list(mobs):
                            if m2 != m:
                                dist = math.hypot(m2.rect.centerx - m.rect.centerx, m2.rect.centery - m.rect.centery)
                                if dist < 100 and m2 not in self.corrupted:
                                    m2.hp -= 80
                                    self.corrupted.add(m2)
                    break


class DarkMatter(pygame.sprite.Sprite):
    """日食幽灵·暗物质爆发 - 释放暗能量波"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 90
        self.radius = 0
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.hit_enemies = set()
        self.tendrils = []
        sound_mgr.play("blackhole")
        
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        self.radius += 6
        
        cx, cy = self.owner.rect.center
        
        # 暗物质核心
        core_pulse = abs(math.sin(self.life * 0.15))
        core_size = int(50 + 20 * core_pulse)
        pygame.draw.circle(self.image, (30, 10, 50), (cx, cy), core_size)
        pygame.draw.circle(self.image, (100, 50, 180), (cx, cy), core_size, 3)
        
        # 暗能量波
        if self.radius < 400:
            for i in range(3):
                r = self.radius - i * 20
                if r > 0:
                    alpha = int(150 * (1 - r / 400))
                    pygame.draw.circle(self.image, (80, 30, 120, alpha), (cx, cy), r, 4)
        
        # 暗物质触手
        if self.life % 10 == 0:
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
                if dist < self.radius:
                    self.tendrils.append({
                        'start': (cx, cy),
                        'end': m.rect.center,
                        'life': 15
                    })
        
        for tendril in self.tendrils[:]:
            tendril['life'] -= 1
            if tendril['life'] <= 0:
                self.tendrils.remove(tendril)
                continue
            alpha = int(200 * (tendril['life'] / 15))
            pygame.draw.line(self.image, (100, 50, 180, alpha), tendril['start'], tendril['end'], 3)
        
        # 伤害判定
        for m in list(mobs):
            dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
            if dist < self.radius and dist > self.radius - 40:
                if m not in self.hit_enemies:
                    m.hp -= 200
                    self.hit_enemies.add(m)
                    FloatingText(m.rect.centerx, m.rect.top - 30, "🌑DARK!", (100, 50, 180))
                Particle(m.rect.center, (100, 50, 180))


class RainbowShatter(pygame.sprite.Sprite):
    """棱镜分光·彩虹碎裂 - 爆炸式光谱分裂"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 70
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.shards = []
        self.hit_enemies = set()
        sound_mgr.play("nuke")
        
        colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 127, 255), (75, 0, 130), (148, 0, 211)]
        
        # 生成碎片
        for i in range(28):
            angle = i * (360 / 28)
            color = colors[i % len(colors)]
            self.shards.append({
                'x': owner.rect.centerx,
                'y': owner.rect.centery,
                'angle': angle,
                'speed': random.uniform(8, 12),
                'color': color,
                'size': random.randint(10, 20),
                'trail': []
            })
    
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        
        self.image.fill((0,0,0,0))
        
        for shard in self.shards:
            rad = math.radians(shard['angle'])
            shard['x'] += math.cos(rad) * shard['speed']
            shard['y'] += math.sin(rad) * shard['speed']
            
            shard['trail'].append((shard['x'], shard['y']))
            if len(shard['trail']) > 10:
                shard['trail'].pop(0)
            
            # 绘制尾迹
            for i, pos in enumerate(shard['trail']):
                alpha = int(200 * (i / len(shard['trail'])))
                size = int(shard['size'] * (i / len(shard['trail'])))
                pygame.draw.circle(self.image, (*shard['color'], alpha), (int(pos[0]), int(pos[1])), max(1, size))
            
            # 绘制碎片（菱形）
            sx, sy = int(shard['x']), int(shard['y'])
            s = shard['size']
            points = [(sx, sy - s), (sx + s//2, sy), (sx, sy + s), (sx - s//2, sy)]
            pygame.draw.polygon(self.image, shard['color'], points)
            pygame.draw.polygon(self.image, (255, 255, 255), points, 2)
            
            # 碰撞检测
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - shard['x'], m.rect.centery - shard['y'])
                if dist < 30:
                    if m not in self.hit_enemies:
                        m.hp -= 120
                        self.hit_enemies.add(m)
                        FloatingText(m.rect.centerx, m.rect.top - 30, "✨SHATTER!", shard['color'])
                    Particle(m.rect.center, shard['color'])


class LifeDrain(pygame.sprite.Sprite):
    """死灵骑士·生命汲取 - 持续吸取生命"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 120
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.drain_links = {}
        self.total_heal = 0
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            # 最终治疗
            if hasattr(self.owner, 'hp') and hasattr(self.owner, 'max_hp'):
                heal = self.total_heal // 5
                self.owner.hp = min(self.owner.max_hp, self.owner.hp + heal)
                if heal > 0:
                    FloatingText(self.owner.rect.centerx, self.owner.rect.top - 50, f"+{heal} HP", LIME)
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        
        cx, cy = self.owner.rect.center
        
        # 生命汲取光环
        pulse = abs(math.sin(self.life * 0.1))
        aura_size = int(200 + 50 * pulse)
        pygame.draw.circle(self.image, (200, 50, 150, 50), (cx, cy), aura_size)
        pygame.draw.circle(self.image, (200, 50, 150), (cx, cy), aura_size, 2)
        
        # 连接所有范围内敌人
        for m in list(mobs):
            dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
            if dist < aura_size:
                # 生命链接线
                pygame.draw.line(self.image, (200, 100, 150, 150), (cx, cy), m.rect.center, 2)
                
                # 流动的生命能量
                for i in range(5):
                    t = (self.life + i * 10) % 50 / 50
                    px = cx + (m.rect.centerx - cx) * t
                    py = cy + (m.rect.centery - cy) * t
                    pygame.draw.circle(self.image, (255, 100, 150), (int(px), int(py)), 4)
                
                # 持续伤害和治疗
                if m not in self.drain_links:
                    self.drain_links[m] = 0
                
                if self.life % 10 == 0:
                    dmg = 30
                    m.hp -= dmg
                    self.total_heal += dmg
                    self.drain_links[m] += 1
                    Particle(m.rect.center, (200, 50, 150))


# ==============================================================================
#   第三大招特效类（C键释放）
# ==============================================================================

class PlasmaVortex(pygame.sprite.Sprite):
    """先锋战机·等离子漩涡 - 释放吸引敌人的等离子漩涡"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 150
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.hit_enemies = set()
        self.vortex_angle = 0
        self.absorbed_enemies = []
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            # 最终爆炸
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - self.owner.rect.centerx, 
                                 m.rect.centery - self.owner.rect.centery)
                if dist < 250:
                    m.hp -= 200
                    FloatingText(m.rect.centerx, m.rect.top - 20, "💥IMPLODE!", CYAN)
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        cx, cy = self.owner.rect.center
        self.vortex_angle += 8
        
        # 绘制等离子漩涡
        for i in range(6):
            angle = math.radians(self.vortex_angle + i * 60)
            r = 80 + 60 * abs(math.sin(self.life * 0.05))
            for j in range(20):
                t = j / 20
                spiral_r = r * (1 - t * 0.7)
                spiral_angle = angle + t * math.pi * 3
                px = cx + spiral_r * math.cos(spiral_angle)
                py = cy + spiral_r * math.sin(spiral_angle)
                size = int(8 * (1 - t))
                alpha = int(255 * (1 - t * 0.5))
                color = (100, 200 + int(55 * t), 255, alpha)
                pygame.draw.circle(self.image, color, (int(px), int(py)), size)
        
        # 核心发光
        pygame.draw.circle(self.image, (150, 230, 255), (cx, cy), 30)
        pygame.draw.circle(self.image, WHITE, (cx, cy), 15)
        
        # 吸引并伤害敌人
        for m in list(mobs):
            dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
            if dist < 200 and dist > 30:
                # 吸引效果
                pull_strength = 3
                dx = (cx - m.rect.centerx) / dist * pull_strength
                dy = (cy - m.rect.centery) / dist * pull_strength
                m.rect.x += dx
                m.rect.y += dy
                
                # 持续伤害
                if self.life % 15 == 0:
                    m.hp -= 25
                    Particle(m.rect.center, CYAN)


class MirrorImage(pygame.sprite.Sprite):
    """幻影刺客·镜像分裂 - 创建攻击敌人的镜像"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 120
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.mirrors = []
        # 创建4个镜像
        for i in range(4):
            angle = i * 90
            self.mirrors.append({
                'angle': angle,
                'dist': 100,
                'attack_timer': 0
            })
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        cx, cy = self.owner.rect.center
        
        for mirror in self.mirrors:
            mirror['angle'] += 3
            mirror['attack_timer'] += 1
            
            # 镜像位置
            rad = math.radians(mirror['angle'])
            mx = cx + mirror['dist'] * math.cos(rad)
            my = cy + mirror['dist'] * math.sin(rad)
            
            # 绘制半透明镜像
            pygame.draw.polygon(self.image, (100, 150, 255, 150), [
                (mx, my - 25), (mx - 15, my + 15), (mx + 15, my + 15)
            ])
            pygame.draw.polygon(self.image, CYAN, [
                (mx, my - 25), (mx - 15, my + 15), (mx + 15, my + 15)
            ], 2)
            
            # 每30帧攻击
            if mirror['attack_timer'] % 30 == 0:
                targets = list(mobs)
                if targets:
                    target = min(targets, key=lambda t: math.hypot(
                        t.rect.centerx - mx, t.rect.centery - my))
                    # 绘制攻击线
                    pygame.draw.line(self.image, CYAN, (mx, my), target.rect.center, 3)
                    target.hp -= 50
                    FloatingText(target.rect.centerx, target.rect.top - 20, "👤MIRROR!", (150, 200, 255))
                    Particle(target.rect.center, CYAN)


class SeismicSlam(pygame.sprite.Sprite):
    """钢铁堡垒·地震冲击 - 制造扩散的地震波"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 90
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.waves = []
        self.wave_timer = 0
        self.hit_by_wave = {}
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        cx, cy = self.owner.rect.center
        self.wave_timer += 1
        
        # 每15帧发射新波
        if self.wave_timer % 15 == 0 and self.life > 30:
            self.waves.append({'radius': 20, 'alpha': 255})
        
        # 更新和绘制波
        for wave in self.waves[:]:
            wave['radius'] += 12
            wave['alpha'] = max(0, wave['alpha'] - 5)
            
            if wave['alpha'] <= 0:
                self.waves.remove(wave)
                continue
            
            # 绘制地震波
            color = (180, 120, 60, wave['alpha'])
            pygame.draw.circle(self.image, color, (cx, cy), int(wave['radius']), 8)
            
            # 裂缝效果
            for i in range(8):
                angle = math.radians(i * 45 + wave['radius'])
                x1 = cx + (wave['radius'] - 20) * math.cos(angle)
                y1 = cy + (wave['radius'] - 20) * math.sin(angle)
                x2 = cx + (wave['radius'] + 10) * math.cos(angle)
                y2 = cy + (wave['radius'] + 10) * math.sin(angle)
                pygame.draw.line(self.image, (139, 90, 43), (x1, y1), (x2, y2), 3)
            
            # 伤害敌人
            wave_id = id(wave)
            if wave_id not in self.hit_by_wave:
                self.hit_by_wave[wave_id] = set()
            
            for m in list(mobs):
                if m in self.hit_by_wave[wave_id]:
                    continue
                dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
                if abs(dist - wave['radius']) < 30:
                    m.hp -= 80
                    self.hit_by_wave[wave_id].add(m)
                    FloatingText(m.rect.centerx, m.rect.top - 20, "🌋QUAKE!", (180, 120, 60))
                    Particle(m.rect.center, (139, 90, 43))


class BallLightning(pygame.sprite.Sprite):
    """雷霆战鹰·球状闪电 - 释放追踪敌人的球状闪电"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 180
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.balls = []
        # 创建3个球状闪电
        for i in range(3):
            angle = random.uniform(0, math.pi * 2)
            self.balls.append({
                'x': owner.rect.centerx + math.cos(angle) * 50,
                'y': owner.rect.centery + math.sin(angle) * 50,
                'vx': 0, 'vy': 0,
                'target': None,
                'hit_count': 0
            })
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        
        for ball in self.balls:
            # 寻找目标
            targets = [m for m in mobs if m not in [b.get('last_hit') for b in self.balls]]
            if targets:
                ball['target'] = min(targets, key=lambda t: math.hypot(
                    t.rect.centerx - ball['x'], t.rect.centery - ball['y']))
            
            # 追踪移动
            if ball['target'] and ball['target'].alive():
                dx = ball['target'].rect.centerx - ball['x']
                dy = ball['target'].rect.centery - ball['y']
                dist = math.hypot(dx, dy)
                if dist > 0:
                    ball['vx'] += dx / dist * 0.8
                    ball['vy'] += dy / dist * 0.8
            
            # 限制速度
            speed = math.hypot(ball['vx'], ball['vy'])
            if speed > 8:
                ball['vx'] = ball['vx'] / speed * 8
                ball['vy'] = ball['vy'] / speed * 8
            
            ball['x'] += ball['vx']
            ball['y'] += ball['vy']
            
            # 绘制球状闪电
            bx, by = int(ball['x']), int(ball['y'])
            
            # 外层电弧
            for i in range(8):
                angle = random.uniform(0, math.pi * 2)
                r = random.randint(15, 35)
                ex = bx + math.cos(angle) * r
                ey = by + math.sin(angle) * r
                pygame.draw.line(self.image, (150, 200, 255), (bx, by), (int(ex), int(ey)), 2)
            
            # 核心
            pygame.draw.circle(self.image, (200, 230, 255), (bx, by), 20)
            pygame.draw.circle(self.image, WHITE, (bx, by), 12)
            
            # 碰撞检测
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - ball['x'], m.rect.centery - ball['y'])
                if dist < 35:
                    m.hp -= 60
                    ball['hit_count'] += 1
                    ball['last_hit'] = m
                    ball['target'] = None
                    # 反弹
                    ball['vx'] = -ball['vx'] * 0.5 + random.uniform(-3, 3)
                    ball['vy'] = -ball['vy'] * 0.5 + random.uniform(-3, 3)
                    FloatingText(m.rect.centerx, m.rect.top - 20, "⚡BALL!", (200, 230, 255))
                    Particle(m.rect.center, (150, 200, 255))
                    break


class CorrosiveCloud(pygame.sprite.Sprite):
    """毒蛇轰炸机·腐蚀云雾 - 释放扩散的腐蚀性毒云"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 180
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.clouds = [{'x': owner.rect.centerx, 'y': owner.rect.centery, 
                       'size': 50, 'growing': True}]
        self.affected = {}
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        
        # 扩散云雾
        if self.life % 40 == 0 and len(self.clouds) < 5:
            parent = random.choice(self.clouds)
            angle = random.uniform(0, math.pi * 2)
            self.clouds.append({
                'x': parent['x'] + math.cos(angle) * 80,
                'y': parent['y'] + math.sin(angle) * 80,
                'size': 30, 'growing': True
            })
        
        for cloud in self.clouds:
            if cloud['growing'] and cloud['size'] < 120:
                cloud['size'] += 1
            
            # 绘制毒云
            cx, cy = int(cloud['x']), int(cloud['y'])
            size = int(cloud['size'])
            
            # 多层云雾效果
            for i in range(3):
                layer_size = size - i * 15
                if layer_size > 0:
                    alpha = 80 - i * 20
                    color = (100, 180, 50, alpha)
                    pygame.draw.circle(self.image, color, (cx, cy), layer_size)
            
            # 毒气粒子
            for _ in range(3):
                px = cx + random.randint(-size, size)
                py = cy + random.randint(-size, size)
                if math.hypot(px - cx, py - cy) < size:
                    pygame.draw.circle(self.image, (150, 220, 80), (px, py), 3)
            
            # 伤害敌人
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
                if dist < size:
                    if m not in self.affected:
                        self.affected[m] = 0
                    self.affected[m] += 1
                    
                    if self.affected[m] % 20 == 0:
                        m.hp -= 15 + self.affected[m] // 20 * 5  # 递增伤害
                        FloatingText(m.rect.centerx, m.rect.top - 20, "☠️TOXIC!", LIME)
                        Particle(m.rect.center, (100, 180, 50))


class SoulStorm(pygame.sprite.Sprite):
    """幽灵战机·灵魂风暴 - 召唤亡魂漩涡"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 150
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.souls = []
        self.storm_angle = 0
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        cx, cy = self.owner.rect.center
        self.storm_angle += 5
        
        # 生成新灵魂
        if self.life % 10 == 0 and len(self.souls) < 20:
            angle = random.uniform(0, math.pi * 2)
            self.souls.append({
                'angle': angle,
                'dist': random.randint(50, 150),
                'speed': random.uniform(2, 4),
                'size': random.randint(8, 15),
                'phase': random.uniform(0, math.pi * 2)
            })
        
        # 绘制漩涡中心
        pygame.draw.circle(self.image, (80, 50, 120, 100), (cx, cy), 60)
        pygame.draw.circle(self.image, (120, 80, 180), (cx, cy), 60, 3)
        
        # 更新灵魂
        for soul in self.souls[:]:
            soul['angle'] += soul['speed'] * 0.05
            soul['dist'] += math.sin(self.life * 0.1 + soul['phase']) * 2
            
            # 灵魂位置
            sx = cx + soul['dist'] * math.cos(soul['angle'])
            sy = cy + soul['dist'] * math.sin(soul['angle'])
            
            # 绘制灵魂
            alpha = 150 + int(50 * math.sin(self.life * 0.2 + soul['phase']))
            color = (180, 150, 220, alpha)
            pygame.draw.circle(self.image, color, (int(sx), int(sy)), soul['size'])
            
            # 灵魂尾迹
            for i in range(3):
                trail_angle = soul['angle'] - i * 0.2
                trail_dist = soul['dist'] - i * 5
                tx = cx + trail_dist * math.cos(trail_angle)
                ty = cy + trail_dist * math.sin(trail_angle)
                trail_alpha = alpha - i * 40
                if trail_alpha > 0:
                    pygame.draw.circle(self.image, (150, 120, 200, trail_alpha), 
                                     (int(tx), int(ty)), soul['size'] - i * 2)
        
        # 伤害敌人
        for m in list(mobs):
            dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
            if dist < 180:
                if self.life % 12 == 0:
                    m.hp -= 35
                    FloatingText(m.rect.centerx, m.rect.top - 20, "👻HAUNT!", (180, 150, 220))
                    Particle(m.rect.center, (150, 120, 200))


class NorthernLights(pygame.sprite.Sprite):
    """极光之翼·北极光 - 释放治疗和伤害的极光波"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 120
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.wave_offset = 0
        self.heal_total = 0
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            if self.heal_total > 0:
                FloatingText(self.owner.rect.centerx, self.owner.rect.top - 60, 
                           f"✨+{self.heal_total} HP", CYAN)
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        self.wave_offset += 3
        
        # 绘制极光波
        colors = [(100, 255, 200), (150, 200, 255), (200, 150, 255), (100, 255, 150)]
        
        for i, color in enumerate(colors):
            points = []
            for x in range(0, WIDTH, 10):
                y_base = HEIGHT // 2
                wave1 = math.sin((x + self.wave_offset + i * 30) * 0.02) * 100
                wave2 = math.sin((x + self.wave_offset * 1.5 + i * 50) * 0.015) * 50
                y = y_base + wave1 + wave2 + i * 30
                points.append((x, int(y)))
            
            if len(points) > 2:
                # 绘制填充区域
                fill_points = points + [(WIDTH, HEIGHT), (0, HEIGHT)]
                pygame.draw.polygon(self.image, (*color, 30), fill_points)
                # 绘制线条
                pygame.draw.lines(self.image, (*color, 150), False, points, 3)
        
        # 伤害敌人 + 治疗自己
        for m in list(mobs):
            if self.life % 15 == 0:
                m.hp -= 40
                heal = 5
                self.owner.hp = min(self.owner.max_hp, self.owner.hp + heal)
                self.heal_total += heal
                Particle(m.rect.center, random.choice(colors))


class BladeWhirlwind(pygame.sprite.Sprite):
    """血色男爵·刀刃旋风 - 生成旋转的刀刃风暴"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 120
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.angle = 0
        self.blades = []
        # 创建刀刃
        for i in range(12):
            self.blades.append({
                'angle': i * 30,
                'dist': 80 + (i % 3) * 40,
                'length': 40
            })
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        cx, cy = self.owner.rect.center
        self.angle += 8
        
        # 更新和绘制刀刃
        for blade in self.blades:
            blade['angle'] += 6
            rad = math.radians(blade['angle'] + self.angle)
            
            # 刀刃中心位置
            bx = cx + blade['dist'] * math.cos(rad)
            by = cy + blade['dist'] * math.sin(rad)
            
            # 刀刃两端
            blade_rad = rad + math.pi / 2
            x1 = bx + blade['length'] * math.cos(blade_rad)
            y1 = by + blade['length'] * math.sin(blade_rad)
            x2 = bx - blade['length'] * math.cos(blade_rad)
            y2 = by - blade['length'] * math.sin(blade_rad)
            
            # 绘制刀刃
            pygame.draw.line(self.image, (255, 50, 50), (int(x1), int(y1)), (int(x2), int(y2)), 4)
            pygame.draw.line(self.image, (255, 200, 200), (int(x1), int(y1)), (int(x2), int(y2)), 2)
            
            # 刀刃轨迹
            trail_rad = math.radians(blade['angle'] + self.angle - 15)
            tx = cx + blade['dist'] * math.cos(trail_rad)
            ty = cy + blade['dist'] * math.sin(trail_rad)
            pygame.draw.line(self.image, (255, 100, 100, 100), (int(bx), int(by)), (int(tx), int(ty)), 2)
            
            # 碰撞检测
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - bx, m.rect.centery - by)
                if dist < 50:
                    if self.life % 8 == 0:
                        m.hp -= 45
                        FloatingText(m.rect.centerx, m.rect.top - 20, "🗡️SLASH!", RED)
                        Particle(m.rect.center, RED)


class GravityBomb(pygame.sprite.Sprite):
    """暗影猎手·重力炸弹 - 投掷黑洞炸弹"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 150
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.bomb_x = owner.rect.centerx
        self.bomb_y = owner.rect.centery - 100
        self.phase = 'grow'  # grow -> implode -> explode
        self.size = 10
        self.pulled_enemies = set()
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        
        if self.phase == 'grow':
            self.size = min(80, self.size + 2)
            if self.life < 80:
                self.phase = 'implode'
        elif self.phase == 'implode':
            if self.life < 30:
                self.phase = 'explode'
        
        # 绘制黑洞
        bx, by = int(self.bomb_x), int(self.bomb_y)
        
        if self.phase != 'explode':
            # 吸积盘
            for i in range(5):
                ring_size = self.size + i * 15
                alpha = 150 - i * 25
                pygame.draw.circle(self.image, (100, 50, 150, alpha), (bx, by), ring_size, 2)
            
            # 黑洞核心
            pygame.draw.circle(self.image, (20, 10, 30), (bx, by), self.size)
            pygame.draw.circle(self.image, (80, 40, 120), (bx, by), self.size, 2)
            
            # 扭曲效果
            for i in range(12):
                angle = math.radians(i * 30 + self.life * 5)
                r = self.size + 20
                ex = bx + r * math.cos(angle)
                ey = by + r * math.sin(angle)
                pygame.draw.line(self.image, (150, 100, 200), (bx, by), (int(ex), int(ey)), 1)
            
            # 吸引敌人
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - bx, m.rect.centery - by)
                if dist < 200 and dist > 20:
                    pull = 4 if self.phase == 'implode' else 2
                    dx = (bx - m.rect.centerx) / dist * pull
                    dy = (by - m.rect.centery) / dist * pull
                    m.rect.x += dx
                    m.rect.y += dy
                    self.pulled_enemies.add(m)
                    
                    if dist < 50 and self.life % 10 == 0:
                        m.hp -= 30
        
        else:
            # 爆炸阶段
            explode_size = (30 - self.life) * 15
            pygame.draw.circle(self.image, (200, 100, 255, 150), (bx, by), explode_size)
            pygame.draw.circle(self.image, (255, 200, 255), (bx, by), explode_size, 3)
            
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - bx, m.rect.centery - by)
                if dist < explode_size and m in self.pulled_enemies:
                    m.hp -= 150
                    self.pulled_enemies.discard(m)
                    FloatingText(m.rect.centerx, m.rect.top - 20, "🕳️CRUSH!", (200, 100, 255))


class CrystalBarrier(pygame.sprite.Sprite):
    """盖亚守护者·水晶屏障 - 生成反弹伤害的水晶护盾"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 180
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.crystals = []
        self.shield_hp = 500
        self.angle = 0
        # 生成水晶
        for i in range(8):
            self.crystals.append({
                'angle': i * 45,
                'size': random.randint(20, 35)
            })
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0 or self.shield_hp <= 0:
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        cx, cy = self.owner.rect.center
        self.angle += 1
        
        # 护盾圆环
        shield_radius = 100
        pygame.draw.circle(self.image, (100, 200, 200, 50), (cx, cy), shield_radius)
        pygame.draw.circle(self.image, CYAN, (cx, cy), shield_radius, 2)
        
        # 绘制水晶
        for crystal in self.crystals:
            rad = math.radians(crystal['angle'] + self.angle)
            crx = cx + shield_radius * math.cos(rad)
            cry = cy + shield_radius * math.sin(rad)
            
            # 水晶形状（六边形）
            points = []
            for i in range(6):
                a = math.radians(i * 60 + self.angle * 2)
                px = crx + crystal['size'] * math.cos(a) * (0.5 if i % 2 else 1)
                py = cry + crystal['size'] * math.sin(a) * (0.5 if i % 2 else 1)
                points.append((px, py))
            
            pygame.draw.polygon(self.image, (150, 230, 230, 180), points)
            pygame.draw.polygon(self.image, CYAN, points, 2)
            
            # 水晶光芒
            pygame.draw.circle(self.image, (200, 255, 255, 100), (int(crx), int(cry)), 5)
        
        # 检测并反弹敌人/敌方子弹
        for m in list(mobs):
            dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
            if dist < shield_radius + 30 and dist > shield_radius - 30:
                # 反弹伤害
                m.hp -= 50
                self.shield_hp -= 20
                # 推开敌人
                if dist > 0:
                    push_x = (m.rect.centerx - cx) / dist * 10
                    push_y = (m.rect.centery - cy) / dist * 10
                    m.rect.x += push_x
                    m.rect.y += push_y
                FloatingText(m.rect.centerx, m.rect.top - 20, "💎REFLECT!", CYAN)
                Particle(m.rect.center, CYAN)


class SpiderSwarm(pygame.sprite.Sprite):
    """织网者·蜘蛛群袭 - 召唤蜘蛛大军攻击敌人"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 180
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.spiders = []
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        
        # 生成蜘蛛
        if self.life % 15 == 0 and len(self.spiders) < 15:
            self.spiders.append({
                'x': self.owner.rect.centerx + random.randint(-30, 30),
                'y': self.owner.rect.centery + random.randint(-30, 30),
                'vx': 0, 'vy': 0,
                'target': None,
                'leg_phase': random.uniform(0, math.pi * 2)
            })
        
        # 更新蜘蛛
        for spider in self.spiders[:]:
            # 寻找目标
            targets = list(mobs)
            if targets:
                spider['target'] = min(targets, key=lambda t: math.hypot(
                    t.rect.centerx - spider['x'], t.rect.centery - spider['y']))
            
            # 移动向目标
            if spider['target'] and spider['target'].alive():
                dx = spider['target'].rect.centerx - spider['x']
                dy = spider['target'].rect.centery - spider['y']
                dist = math.hypot(dx, dy)
                if dist > 0:
                    spider['vx'] = dx / dist * 4
                    spider['vy'] = dy / dist * 4
            
            spider['x'] += spider['vx']
            spider['y'] += spider['vy']
            spider['leg_phase'] += 0.3
            
            sx, sy = int(spider['x']), int(spider['y'])
            
            # 绘制蜘蛛身体
            pygame.draw.circle(self.image, (60, 40, 30), (sx, sy), 8)
            pygame.draw.circle(self.image, (80, 60, 50), (sx, sy - 5), 5)
            
            # 绘制蜘蛛腿
            for i in range(8):
                leg_angle = math.radians(i * 45)
                leg_wave = math.sin(spider['leg_phase'] + i) * 3
                leg_len = 12 + leg_wave
                lx = sx + math.cos(leg_angle) * leg_len
                ly = sy + math.sin(leg_angle) * leg_len
                pygame.draw.line(self.image, (60, 40, 30), (sx, sy), (int(lx), int(ly)), 2)
            
            # 攻击
            if spider['target'] and spider['target'].alive():
                dist = math.hypot(spider['target'].rect.centerx - spider['x'],
                                spider['target'].rect.centery - spider['y'])
                if dist < 20:
                    spider['target'].hp -= 25
                    FloatingText(spider['target'].rect.centerx, spider['target'].rect.top - 20, 
                               "🕷️BITE!", (80, 60, 50))
                    Particle(spider['target'].rect.center, (60, 40, 30))
                    # 蜘蛛死亡
                    self.spiders.remove(spider)


class SolarBeam(pygame.sprite.Sprite):
    """烈日凤凰·太阳光束 - 蓄力后发射毁灭性光束"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 120
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.charge_phase = 60  # 蓄力时间
        self.beam_angle = -90  # 向上
        self.hit_enemies = set()
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        cx, cy = self.owner.rect.center
        
        if self.charge_phase > 0:
            # 蓄力阶段
            self.charge_phase -= 1
            charge_pct = 1 - self.charge_phase / 60
            
            # 能量聚集效果
            for i in range(int(20 * charge_pct)):
                angle = random.uniform(0, math.pi * 2)
                dist = random.randint(50, 150) * (1 - charge_pct * 0.5)
                px = cx + math.cos(angle) * dist
                py = cy + math.sin(angle) * dist
                
                # 能量粒子向中心移动
                pygame.draw.line(self.image, (255, 200, 50), (int(px), int(py)), (cx, cy), 2)
                pygame.draw.circle(self.image, (255, 220, 100), (int(px), int(py)), 4)
            
            # 中心蓄能球
            ball_size = int(20 + 30 * charge_pct)
            pygame.draw.circle(self.image, (255, 200, 50, 150), (cx, cy), ball_size)
            pygame.draw.circle(self.image, (255, 255, 200), (cx, cy), ball_size // 2)
            
        else:
            # 发射光束
            beam_width = 60
            
            # 光束主体
            for i in range(3):
                w = beam_width - i * 15
                alpha = 200 - i * 50
                color = (255, 220 - i * 30, 50, alpha)
                pygame.draw.rect(self.image, color, 
                               (cx - w // 2, 0, w, cy))
            
            # 光束边缘效果
            for i in range(10):
                side_x = cx + random.randint(-beam_width // 2, beam_width // 2)
                side_y = random.randint(0, cy)
                pygame.draw.circle(self.image, (255, 255, 200), (side_x, side_y), 3)
            
            # 伤害
            self.hit_enemies.clear()
            for m in list(mobs):
                if abs(m.rect.centerx - cx) < beam_width // 2 + 20 and m.rect.centery < cy:
                    m.hp -= 100
                    FloatingText(m.rect.centerx, m.rect.top - 20, "☀️SOLAR!", (255, 200, 50))
                    Particle(m.rect.center, (255, 220, 100))


class VirusInfection(pygame.sprite.Sprite):
    """仲裁者·病毒感染 - 释放传染性病毒"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 180
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.infected = {}  # 感染的敌人及其感染等级
        self.virus_particles = []
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        cx, cy = self.owner.rect.center
        
        # 初始感染
        if self.life == 179:
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
                if dist < 150:
                    self.infected[m] = 1
        
        # 病毒传播
        newly_infected = {}
        for m, level in list(self.infected.items()):
            if not m.alive():
                del self.infected[m]
                continue
            
            # 伤害
            if self.life % 20 == 0:
                dmg = 20 * level
                m.hp -= dmg
                
                # 生成病毒粒子
                for _ in range(3):
                    self.virus_particles.append({
                        'x': m.rect.centerx,
                        'y': m.rect.centery,
                        'vx': random.uniform(-3, 3),
                        'vy': random.uniform(-3, 3),
                        'life': 30
                    })
            
            # 传播到附近敌人
            for other in list(mobs):
                if other not in self.infected and other not in newly_infected:
                    dist = math.hypot(other.rect.centerx - m.rect.centerx,
                                    other.rect.centery - m.rect.centery)
                    if dist < 80:
                        newly_infected[other] = level + 1
                        FloatingText(other.rect.centerx, other.rect.top - 20, 
                                   "🦠INFECTED!", (150, 255, 100))
        
        self.infected.update(newly_infected)
        
        # 绘制病毒粒子
        for p in self.virus_particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            
            if p['life'] <= 0:
                self.virus_particles.remove(p)
                continue
            
            alpha = int(255 * p['life'] / 30)
            pygame.draw.circle(self.image, (150, 255, 100, alpha), 
                             (int(p['x']), int(p['y'])), 4)
        
        # 绘制感染标记
        for m, level in self.infected.items():
            if m.alive():
                color = (100 + level * 30, 255, 100, 150)
                pygame.draw.circle(self.image, color, m.rect.center, 15 + level * 5, 2)
                # 病毒符号
                pygame.draw.circle(self.image, (150, 255, 100), m.rect.center, 5)


class VoidCollapse(pygame.sprite.Sprite):
    """日蚀使者·虚空坍缩 - 创造吞噬一切的虚空裂隙"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 150
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rifts = []
        self.spawn_timer = 0
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        self.spawn_timer += 1
        
        # 生成裂隙
        if self.spawn_timer % 30 == 0 and len(self.rifts) < 5:
            targets = list(mobs)
            if targets:
                target = random.choice(targets)
                x, y = target.rect.center
            else:
                x = random.randint(100, WIDTH - 100)
                y = random.randint(100, HEIGHT - 100)
            
            self.rifts.append({
                'x': x, 'y': y,
                'size': 10,
                'max_size': random.randint(60, 100),
                'phase': 'grow',
                'rotation': 0
            })
        
        # 更新裂隙
        for rift in self.rifts[:]:
            rift['rotation'] += 3
            
            if rift['phase'] == 'grow':
                rift['size'] = min(rift['max_size'], rift['size'] + 3)
                if rift['size'] >= rift['max_size']:
                    rift['phase'] = 'stable'
            elif rift['phase'] == 'stable' and self.life < 30:
                rift['phase'] = 'collapse'
            elif rift['phase'] == 'collapse':
                rift['size'] -= 5
                if rift['size'] <= 0:
                    self.rifts.remove(rift)
                    continue
            
            rx, ry = int(rift['x']), int(rift['y'])
            size = int(rift['size'])
            
            # 绘制虚空裂隙
            pygame.draw.circle(self.image, (10, 5, 20), (rx, ry), size)
            
            # 扭曲边缘
            for i in range(12):
                angle = math.radians(i * 30 + rift['rotation'])
                dist = size + random.randint(-5, 10)
                ex = rx + math.cos(angle) * dist
                ey = ry + math.sin(angle) * dist
                pygame.draw.line(self.image, (80, 40, 120), (rx, ry), (int(ex), int(ey)), 2)
            
            pygame.draw.circle(self.image, (100, 50, 150), (rx, ry), size, 3)
            
            # 吸引并伤害
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - rx, m.rect.centery - ry)
                if dist < size + 50 and dist > 10:
                    # 吸引
                    pull = 3
                    dx = (rx - m.rect.centerx) / dist * pull
                    dy = (ry - m.rect.centery) / dist * pull
                    m.rect.x += dx
                    m.rect.y += dy
                
                if dist < size:
                    if self.life % 10 == 0:
                        m.hp -= 40
                        FloatingText(m.rect.centerx, m.rect.top - 20, "🌀VOID!", (100, 50, 150))


class LightPrism(pygame.sprite.Sprite):
    """棱镜守卫·光之棱镜 - 分裂成多彩光线攻击"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 120
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.prism_angle = 0
        self.beams = []
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        cx, cy = self.owner.rect.center
        self.prism_angle += 2
        
        # 绘制棱镜
        prism_size = 40
        prism_points = []
        for i in range(3):
            angle = math.radians(self.prism_angle + i * 120)
            px = cx + prism_size * math.cos(angle)
            py = cy + prism_size * math.sin(angle)
            prism_points.append((px, py))
        
        pygame.draw.polygon(self.image, (200, 200, 255, 150), prism_points)
        pygame.draw.polygon(self.image, WHITE, prism_points, 3)
        
        # 彩虹光束
        colors = [RED, (255, 165, 0), YELLOW, LIME, CYAN, (100, 100, 255), (200, 100, 255)]
        
        for i, color in enumerate(colors):
            beam_angle = math.radians(self.prism_angle + i * (360 / len(colors)))
            
            # 光束路径
            beam_length = 400
            ex = cx + math.cos(beam_angle) * beam_length
            ey = cy + math.sin(beam_angle) * beam_length
            
            # 绘制光束
            pygame.draw.line(self.image, (*color, 200), (cx, cy), (int(ex), int(ey)), 4)
            pygame.draw.line(self.image, (*color, 100), (cx, cy), (int(ex), int(ey)), 8)
            
            # 光束碰撞
            for m in list(mobs):
                # 点到线段距离
                mx, my = m.rect.center
                dx, dy = ex - cx, ey - cy
                t = max(0, min(1, ((mx - cx) * dx + (my - cy) * dy) / (dx * dx + dy * dy + 0.001)))
                closest_x = cx + t * dx
                closest_y = cy + t * dy
                dist = math.hypot(mx - closest_x, my - closest_y)
                
                if dist < 30 and self.life % 15 == 0:
                    m.hp -= 35
                    Particle(m.rect.center, color)


class SoulReap(pygame.sprite.Sprite):
    """死灵骑士·灵魂收割 - 收割敌人灵魂转化为攻击"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 150
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.souls_collected = []
        self.scythe_angle = 0
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            # 释放所有灵魂
            for soul in self.souls_collected:
                targets = list(mobs)
                if targets:
                    target = random.choice(targets)
                    target.hp -= 80
                    FloatingText(target.rect.centerx, target.rect.top - 20, "💀SOUL!", (180, 100, 200))
            self.kill()
            return
        
        self.image.fill((0,0,0,0))
        cx, cy = self.owner.rect.center
        self.scythe_angle += 6
        
        # 绘制死神镰刀
        scythe_len = 100
        scythe_rad = math.radians(self.scythe_angle)
        sx = cx + scythe_len * math.cos(scythe_rad)
        sy = cy + scythe_len * math.sin(scythe_rad)
        
        # 镰刀柄
        pygame.draw.line(self.image, (80, 60, 100), (cx, cy), (int(sx), int(sy)), 4)
        
        # 镰刀刃
        blade_angle = scythe_rad + math.pi / 2
        blade_len = 50
        bx1 = sx + blade_len * math.cos(blade_angle)
        by1 = sy + blade_len * math.sin(blade_angle)
        bx2 = sx + blade_len * 0.3 * math.cos(blade_angle + 0.5)
        by2 = sy + blade_len * 0.3 * math.sin(blade_angle + 0.5)
        
        pygame.draw.polygon(self.image, (150, 100, 180), [
            (sx, sy), (int(bx1), int(by1)), (int(bx2), int(by2))
        ])
        pygame.draw.polygon(self.image, (200, 150, 220), [
            (sx, sy), (int(bx1), int(by1)), (int(bx2), int(by2))
        ], 2)
        
        # 收割灵魂
        for m in list(mobs):
            dist = math.hypot(m.rect.centerx - sx, m.rect.centery - sy)
            if dist < 60:
                if self.life % 20 == 0:
                    dmg = 50
                    m.hp -= dmg
                    # 收集灵魂
                    self.souls_collected.append({
                        'x': m.rect.centerx,
                        'y': m.rect.centery
                    })
                    FloatingText(m.rect.centerx, m.rect.top - 20, "👻REAP!", (180, 100, 200))
        
        # 绘制收集的灵魂
        for i, soul in enumerate(self.souls_collected):
            orbit_angle = math.radians(self.scythe_angle * 2 + i * 60)
            orbit_dist = 60 + i * 10
            soul_x = cx + orbit_dist * math.cos(orbit_angle)
            soul_y = cy + orbit_dist * math.sin(orbit_angle)
            
            pygame.draw.circle(self.image, (180, 150, 220, 150), (int(soul_x), int(soul_y)), 10)
            pygame.draw.circle(self.image, (220, 200, 255), (int(soul_x), int(soul_y)), 5)
        
        # 灵魂数量显示
        if self.souls_collected:
            draw_text(self.image, f"Souls: {len(self.souls_collected)}", 14, cx, cy - 80, 
                     (200, 150, 255), align='center')


# ==============================================================================
#   防御炮塔系统
# ==============================================================================
class DefenseTurret:
    """固定位置的自动防御炮塔"""
    def __init__(self, x, y, damage, bullet_theme=None):
        self.x = x
        self.y = y
        self.damage = damage
        self.bullet_theme = bullet_theme
        self.shoot_cooldown = 0
        self.shoot_delay = 40  # 射击间隔(约0.67秒)
        self.range = 350  # 射程
        self.rotation = 0  # 炮塔旋转角度
    
    def update(self):
        """更新炮塔,自动射击范围内的敌人"""
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            return
        
        # 寻找最近的敌人
        closest_enemy = None
        min_dist = self.range
        
        for mob in mobs:
            dx = mob.rect.centerx - self.x
            dy = mob.rect.centery - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < min_dist:
                min_dist = dist
                closest_enemy = mob
        
        # 如果找到敌人,射击
        if closest_enemy:
            # 计算射击角度
            dx = closest_enemy.rect.centerx - self.x
            dy = closest_enemy.rect.centery - self.y
            self.rotation = math.degrees(math.atan2(dy, dx)) + 90  # +90因为默认向上
            
            # 发射炮塔子弹 - 增强视觉效果
            turret_bullet = Bullet(self.x, self.y, angle=self.rotation - 90,  # -90校正回来
                                  color=(255, 150, 0), b_type="basic", piercing=0,
                                  bullet_theme=self.bullet_theme)
            turret_bullet.damage = self.damage
            turret_bullet.speed = -15
            
            # 重新绘制更大更明显的炮塔子弹
            if hasattr(turret_bullet, 'image'):
                # 创建发光子弹
                bullet_size = 16
                new_img = pygame.Surface((bullet_size, bullet_size), pygame.SRCALPHA)
                
                # 外层光晕
                for r in range(bullet_size//2, 0, -1):
                    alpha = int(200 * (r / (bullet_size//2)))
                    color_val = int(255 * (r / (bullet_size//2)))
                    pygame.draw.circle(new_img, (255, color_val, 0, alpha), 
                                     (bullet_size//2, bullet_size//2), r)
                
                # 核心亮点
                pygame.draw.circle(new_img, (255, 255, 255), (bullet_size//2, bullet_size//2), 4)
                pygame.draw.circle(new_img, (255, 200, 0), (bullet_size//2, bullet_size//2), 6, 2)
                
                turret_bullet.image = new_img
                turret_bullet.rect = turret_bullet.image.get_rect(center=(self.x, self.y))
            
            self.shoot_cooldown = self.shoot_delay
            sound_mgr.play("shoot")
    
    def draw(self, screen):
        """绘制炮塔"""
        # 炮塔底座(大圆)
        pygame.draw.circle(screen, (80, 80, 80), (int(self.x), int(self.y)), 20, 0)
        pygame.draw.circle(screen, (120, 120, 120), (int(self.x), int(self.y)), 20, 2)
        
        # 炮塔主体(八边形)
        pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), 12, 0)
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), 10, 0)
        
        # 炮管(根据rotation旋转)
        if self.shoot_cooldown == self.shoot_delay:  # 刚射击时闪烁
            barrel_color = WHITE
        else:
            barrel_color = RED
        
        barrel_length = 18
        end_x = self.x + barrel_length * math.cos(math.radians(self.rotation - 90))
        end_y = self.y + barrel_length * math.sin(math.radians(self.rotation - 90))
        pygame.draw.line(screen, barrel_color, (self.x, self.y), (end_x, end_y), 4)
        
        # 射程指示圈(半透明)
        if self.shoot_cooldown <= 0:
            pygame.draw.circle(screen, (255, 100, 0, 50), (int(self.x), int(self.y)), int(self.range), 1)

# ==============================================================================
#   核心实体：Bullet, Player, Enemy, Boss
# ==============================================================================
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0, is_enemy=False, piercing=0, color=YELLOW, homing=0, bounce=0, b_type="beam", bullet_theme=None, is_split=False):
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
        self.is_split = is_split  # 【优化】分裂子弹标记，防止递归分裂
        
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
                self.speed = -22
                
            elif b_type == "shard":  # 2. Phantom - 虚空幻影（洋红菱形碎片）
                self.image = pygame.Surface((16, 30), pygame.SRCALPHA)
                pygame.draw.polygon(self.image, MAGENTA, [(8,0), (16,15), (8,30), (0,15)])
                pygame.draw.polygon(self.image, WHITE, [(8,0), (16,15), (8,30), (0,15)], 2)
                pygame.draw.polygon(self.image, CYBER_CYAN_BRIGHT, [(8,6), (12,15), (8,24), (4,15)])
                self.speed = -26
                self.piercing = max(1, self.piercing)
                
            elif b_type == "rocket":  # 3. Titan - 钢铁泰坦（橙色重型火箭）
                self.image = pygame.Surface((20, 38), pygame.SRCALPHA)
                pygame.draw.rect(self.image, ORANGE, (4, 12, 12, 22))
                pygame.draw.rect(self.image, CYBER_AMBER, (3, 12, 14, 22), 3)
                pygame.draw.polygon(self.image, CYBER_AMBER, [(4,12), (10,0), (16,12)])
                pygame.draw.rect(self.image, (255, 80, 0), (6, 34, 8, 4))
                pygame.draw.circle(self.image, WHITE, (10, 22), 4)
                self.speed = -15
                
            elif b_type == "lightning":  # 4. Thunderbird - 雷霆战鹰（黄色闪电链）
                self.image = pygame.Surface((18, 40), pygame.SRCALPHA)
                points = [(9,0), (4,14), (14,26), (9,40)]
                pygame.draw.lines(self.image, YELLOW, False, points, 4)
                pygame.draw.lines(self.image, WHITE, False, points, 2)
                pygame.draw.line(self.image, YELLOW, (4,14), (0,18), 2)
                pygame.draw.line(self.image, YELLOW, (14,26), (18,30), 2)
                self.speed = -24
                
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
                self.speed = -18
                
            elif b_type == "spectral":  # 6. Specter - 幽灵收割者（紫色幽能箭）
                self.image = pygame.Surface((18, 42), pygame.SRCALPHA)
                points = [(9,0), (5,14), (13,28), (9,42)]
                pygame.draw.lines(self.image, (150, 100, 255), False, points, 5)
                pygame.draw.lines(self.image, (200, 150, 255), False, points, 3)
                pygame.draw.circle(self.image, WHITE, (9, 8), 5)
                pygame.draw.circle(self.image, (180, 130, 255), (9, 24), 4)
                self.speed = -28
                
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
                self.speed = -19
                
            elif b_type == "blade":  # 8. Crimson - 绯红之刃（红色月牙刀光）
                self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.arc(self.image, CRIMSON, (0,0,40,40), 0, 3.14, 5)
                pygame.draw.arc(self.image, (255, 50, 80), (2,2,36,36), 0, 3.14, 4)
                pygame.draw.arc(self.image, WHITE, (6,6,28,28), 0, 3.14, 3)
                pygame.draw.line(self.image, CRIMSON, (0, 20), (40, 20), 3)
                pygame.draw.circle(self.image, WHITE, (20, 20), 5)
                self.speed = -26
                
            elif b_type == "star":  # 9. Stalker - 星界潜行者（靛蓝八芒星）
                self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
                points = [(12,0), (14,8), (24,12), (14,16), (12,24), (10,16), (0,12), (10,8)]
                pygame.draw.polygon(self.image, INDIGO, points)
                pygame.draw.polygon(self.image, (150, 100, 255), points, 2)
                pygame.draw.circle(self.image, WHITE, (12,12), 4)
                pygame.draw.circle(self.image, INDIGO, (12,12), 2)
                self.speed = -21
                
            elif b_type == "thorn":  # 10. Gaia - 大地守护者（岩石荆棘弹）
                # 基础尺寸，可被fury_scale放大
                base_size = 20
                self.image = pygame.Surface((base_size, base_size + 16), pygame.SRCALPHA)
                # 岩石主体
                pygame.draw.polygon(self.image, FOREST, [(base_size//2, 0), (base_size, base_size//2 + 4), (base_size//2, base_size + 12), (0, base_size//2 + 4)])
                pygame.draw.polygon(self.image, (100, 160, 80), [(base_size//2, 0), (base_size, base_size//2 + 4), (base_size//2, base_size + 12), (0, base_size//2 + 4)], 3)
                # 内部纹理
                pygame.draw.polygon(self.image, (80, 140, 60), [(base_size//2, 4), (base_size - 4, base_size//2 + 2), (base_size//2, base_size + 6), (4, base_size//2 + 2)])
                # 荆棘尖刺
                for i in [base_size//3, base_size//2 + 4, base_size - 4]:
                    pygame.draw.line(self.image, CYBER_LIME, (base_size//2, i), (2, i - 5), 2)
                    pygame.draw.line(self.image, CYBER_LIME, (base_size//2, i), (base_size - 2, i - 5), 2)
                # 发光点
                pygame.draw.circle(self.image, (150, 220, 120), (base_size//2, base_size//2 + 2), 3)
                self.speed = -14  # 较慢但更有威力
                
            elif b_type == "web":  # 11. Weaver - 虚空编织者（灰色蛛网十字）
                self.image = pygame.Surface((26, 26), pygame.SRCALPHA)
                pygame.draw.line(self.image, (180, 180, 180), (0,13), (26,13), 3)
                pygame.draw.line(self.image, (180, 180, 180), (13,0), (13,26), 3)
                pygame.draw.line(self.image, (220, 220, 220), (4,4), (22,22), 2)
                pygame.draw.line(self.image, (220, 220, 220), (22,4), (4,22), 2)
                pygame.draw.circle(self.image, WHITE, (13, 13), 5)
                pygame.draw.circle(self.image, CYBER_CYAN_BRIGHT, (13, 13), 4, 2)
                self.speed = -13
                
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
                self.speed = -25
                
            elif b_type == "quant":  # 13. Arbiter - 量子裁决者（紫色量子方块）
                self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.rect(self.image, NEON_PURPLE, (2,2,16,16))
                pygame.draw.rect(self.image, (180, 100, 255), (2,2,16,16), 3)
                pygame.draw.rect(self.image, WHITE, (6,6,8,8))
                pygame.draw.rect(self.image, MAGENTA, (8,8,4,4))
                pygame.draw.line(self.image, CYBER_CYAN_BRIGHT, (0, 10), (20, 10), 2)
                pygame.draw.line(self.image, CYBER_CYAN_BRIGHT, (10, 0), (10, 20), 2)
                self.speed = -19
                
            elif b_type == "shadow":  # 14. Eclipse - 日食幽灵（紫黑暗影箭）
                self.image = pygame.Surface((18, 36), pygame.SRCALPHA)
                pygame.draw.polygon(self.image, (100, 50, 180), [(9,0), (18,12), (15,36), (3,36), (0,12)])
                pygame.draw.polygon(self.image, (150, 100, 220), [(9,0), (18,12), (15,36), (3,36), (0,12)], 3)
                pygame.draw.circle(self.image, (200, 150, 255), (9, 12), 5)
                pygame.draw.circle(self.image, WHITE, (9, 12), 3)
                pygame.draw.circle(self.image, (80, 30, 120), (9, 26), 6)
                self.speed = -21
                
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
                self.speed = -22
            elif b_type == "aurora_prism":  # 极光女神专属棱镜弹幕
                self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
                center = 8
                prism_points = [(center, 2), (14, center), (center, 14), (2, center)]
                inner_points = [(center, 4), (12, center), (center, 12), (4, center)]
                pygame.draw.polygon(self.image, TEAL, prism_points)
                pygame.draw.polygon(self.image, (180, 255, 255), inner_points)
                pygame.draw.polygon(self.image, WHITE, prism_points, 2)
                # 旋转光束装饰
                for a in [0, 90, 180, 270]:
                    rad = math.radians(a)
                    x = center + int(6 * math.cos(rad))
                    y = center + int(6 * math.sin(rad))
                    pygame.draw.line(self.image, CYBER_CYAN_BRIGHT, (center, center), (x, y), 1)
                self.speed = -10
                self.wave_amplitude = 15
                self.wave_frequency = 0.2
                
            else:  # 16. Necro + 默认（紫红幽能，与Specter共用）
                self.image = pygame.Surface((18, 42), pygame.SRCALPHA)
                points = [(9,0), (5,14), (13,28), (9,42)]
                pygame.draw.lines(self.image, (200, 50, 150), False, points, 5)
                pygame.draw.lines(self.image, (255, 100, 200), False, points, 3)
                pygame.draw.circle(self.image, WHITE, (9, 8), 5)
                pygame.draw.circle(self.image, (220, 80, 180), (9, 24), 4)
                self.speed = -24
        
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
        
        # 【新增】通用子弹动态效果（不依赖effects属性）
        self._apply_bullet_dynamics()
        
        # 【优化】速度因子 - 玩家子弹更快，敌人子弹正常
        speed_factor = 0.6 if not self.is_enemy else 0.4
        
        # 特殊移动逻辑
        if not self.is_enemy and self.b_type == "flame":
            if self.timer > 25: self.kill()
            self.pos += self.vel * (1.0 - self.timer/30.0) * speed_factor
        else: 
            self.pos += self.vel * speed_factor
            
        # 追踪逻辑（优化：增强追踪效果）
        if not self.is_enemy and self.homing > 0:
            target = None
            min_dist = 9999
            for m in mobs:
                dist = self.pos.distance_to(pygame.math.Vector2(m.rect.center))
                if dist < min_dist and dist < 600:  # 增加索敌范围到600
                    min_dist = dist
                    target = m
            if target:
                target_vec = pygame.math.Vector2(target.rect.center) - self.pos
                if target_vec.length() > 0: 
                    target_vec = target_vec.normalize() * abs(self.speed)
                    # 追踪强度增强：基础强度*3，使追踪更明显
                    lerp_strength = min(self.homing * 3, 0.95)
                    self.vel = self.vel.lerp(target_vec, lerp_strength)
        
        # 极光棱镜波浪弹道
        if not self.is_enemy and self.b_type == "aurora_prism":
            wave_freq = getattr(self, 'wave_frequency', 0.2)
            wave_amp = getattr(self, 'wave_amplitude', 15)
            self.pos.x = self.start_x + math.sin(self.timer * wave_freq) * wave_amp
                    
        self.rect.center = self.pos
    
    def _apply_bullet_dynamics(self):
        """为所有子弹类型添加动态视觉效果 - 优先使用涂装主题效果"""
        # 每3帧更新一次以优化性能
        if self.timer % 3 != 0:
            return
            
        # 保存原始图像（首次调用时）
        if not hasattr(self, '_base_image'):
            self._base_image = self.image.copy()
            self._base_rect_size = self.image.get_size()
        
        # 时间参数
        t = self.timer * 0.15
        
        # 【新】如果有涂装主题，使用主题效果
        if self.bullet_theme and not self.is_enemy:
            self._apply_theme_dynamics(t)
            return
        
        # 根据子弹类型应用不同效果
        if self.is_enemy:
            # 敌方子弹：不添加额外效果
            pass
            
        else:
            # 玩家子弹：根据类型应用效果
            bt = self.b_type
            
            if bt == "beam":
                # 激光束：脉冲亮度 + 尾焰
                pulse = 0.8 + 0.2 * abs(math.sin(t * 2))
                base_w, base_h = self._base_rect_size
                
                new_image = pygame.Surface((base_w + 8, base_h + 12), pygame.SRCALPHA)
                
                # 尾焰效果
                flame_alpha = int(120 * pulse)
                for i in range(3):
                    flame_y = base_h + i * 4
                    flame_w = base_w - i * 2
                    if flame_w > 0:
                        pygame.draw.ellipse(new_image, (100, 200, 255, flame_alpha - i * 30), 
                                          (4 + i, flame_y, flame_w, 6 - i))
                
                # 原始子弹
                new_image.blit(self._base_image, (4, 0))
                
                old_center = self.rect.center
                self.image = new_image
                self.rect = self.image.get_rect(center=old_center)
                
            elif bt == "lightning":
                # 闪电：闪烁 + 电弧
                if random.random() < 0.3:  # 30%概率闪烁
                    base_w, base_h = self._base_rect_size
                    new_image = pygame.Surface((base_w + 10, base_h + 10), pygame.SRCALPHA)
                    
                    # 电弧光晕
                    glow_alpha = random.randint(100, 180)
                    pygame.draw.ellipse(new_image, (255, 255, 100, glow_alpha), (0, 0, base_w + 10, base_h + 10))
                    
                    # 随机小电弧
                    cx, cy = (base_w + 10) // 2, (base_h + 10) // 2
                    for _ in range(2):
                        angle = random.uniform(0, math.pi * 2)
                        length = random.randint(8, 15)
                        ex = cx + int(length * math.cos(angle))
                        ey = cy + int(length * math.sin(angle))
                        pygame.draw.line(new_image, (255, 255, 200), (cx, cy), (ex, ey), 1)
                    
                    new_image.blit(self._base_image, (5, 5))
                    
                    old_center = self.rect.center
                    self.image = new_image
                    self.rect = self.image.get_rect(center=old_center)
                    
            elif bt == "flame":
                # 火焰：摇曳 + 粒子
                flicker = 0.8 + 0.2 * math.sin(t * 3 + random.uniform(-0.5, 0.5))
                base_w, base_h = self._base_rect_size
                
                new_image = pygame.Surface((base_w + 10, base_h + 10), pygame.SRCALPHA)
                
                # 火焰粒子
                for _ in range(2):
                    px = random.randint(2, base_w + 8)
                    py = random.randint(base_h, base_h + 8)
                    psize = random.randint(2, 4)
                    alpha = int(150 * flicker)
                    pygame.draw.circle(new_image, (255, 200, 50, alpha), (px, py), psize)
                
                new_image.blit(self._base_image, (5, 0))
                
                old_center = self.rect.center
                self.image = new_image
                self.rect = self.image.get_rect(center=old_center)
                
            elif bt == "acid":
                # 毒液：气泡效果
                base_w, base_h = self._base_rect_size
                new_image = pygame.Surface((base_w + 8, base_h + 8), pygame.SRCALPHA)
                
                # 气泡
                for _ in range(2):
                    bx = random.randint(2, base_w + 6)
                    by = random.randint(2, base_h + 6)
                    bsize = random.randint(2, 4)
                    pygame.draw.circle(new_image, (150, 255, 150, 100), (bx, by), bsize)
                    pygame.draw.circle(new_image, (200, 255, 200), (bx, by), bsize, 1)
                
                new_image.blit(self._base_image, (4, 4))
                
                old_center = self.rect.center
                self.image = new_image
                self.rect = self.image.get_rect(center=old_center)
                
            elif bt in ["shard", "shadow", "spectral"]:
                # 幽能类：闪烁 + 拖尾
                pulse = 0.7 + 0.3 * abs(math.sin(t * 1.5))
                base_w, base_h = self._base_rect_size
                
                new_image = pygame.Surface((base_w + 6, base_h + 15), pygame.SRCALPHA)
                
                # 能量拖尾
                for i in range(4):
                    trail_alpha = int(60 * pulse * (1 - i / 4))
                    trail_y = base_h + i * 3
                    trail_w = max(2, base_w - i * 3)
                    pygame.draw.ellipse(new_image, (*self.color[:3], trail_alpha), 
                                      (3 + i, trail_y, trail_w, 4))
                
                new_image.blit(self._base_image, (3, 0))
                
                old_center = self.rect.center
                self.image = new_image
                self.rect = self.image.get_rect(center=old_center)
                
            elif bt == "blade":
                # 刀刃：旋转光效
                rotation_angle = (self.timer * 8) % 360
                base_w, base_h = self._base_rect_size
                
                # 旋转原图
                rotated = pygame.transform.rotate(self._base_image, rotation_angle)
                
                old_center = self.rect.center
                self.image = rotated
                self.rect = self.image.get_rect(center=old_center)
                
            elif bt == "prism":
                # 棱镜：彩虹闪烁（无光晕）
                pass
                
            elif bt == "rocket":
                # 火箭：推进尾焰
                base_w, base_h = self._base_rect_size
                new_image = pygame.Surface((base_w + 8, base_h + 20), pygame.SRCALPHA)
                
                # 尾焰
                flicker = 0.7 + 0.3 * random.random()
                flame_colors = [(255, 200, 50), (255, 150, 0), (255, 80, 0)]
                for i, fc in enumerate(flame_colors):
                    flame_h = int((12 - i * 3) * flicker)
                    flame_w = base_w // 2 - i * 2
                    if flame_w > 0 and flame_h > 0:
                        pygame.draw.ellipse(new_image, (*fc, 180 - i * 40), 
                                          ((base_w + 8) // 2 - flame_w // 2, base_h + i * 2, flame_w, flame_h))
                
                new_image.blit(self._base_image, (4, 0))
                
                old_center = self.rect.center
                self.image = new_image
                self.rect = self.image.get_rect(center=old_center)
                
            elif bt == "star":
                # 星形：旋转（无光晕）
                rotation_angle = (self.timer * 5) % 360
                
                # 旋转
                rotated = pygame.transform.rotate(self._base_image, rotation_angle)
                
                old_center = self.rect.center
                self.image = rotated
                self.rect = self.image.get_rect(center=old_center)
                
            elif bt == "aurora_beam":
                # 极光：波纹扩散
                pulse = abs(math.sin(t))
                base_w, base_h = self._base_rect_size
                
                expand = int(4 * pulse)
                new_w = base_w + expand * 2
                new_h = base_h + expand * 2
                
                new_image = pygame.Surface((new_w, new_h), pygame.SRCALPHA)
                
                # 外层波纹
                pygame.draw.ellipse(new_image, (100, 255, 220, int(80 * (1 - pulse))), 
                                  (0, 0, new_w, new_h), 2)
                
                # 缩放原图
                scaled = pygame.transform.scale(self._base_image, (base_w + expand, base_h + expand))
                new_image.blit(scaled, (expand // 2, expand // 2))
                
                old_center = self.rect.center
                self.image = new_image
                self.rect = self.image.get_rect(center=old_center)

    def _apply_theme_dynamics(self, t):
        """根据涂装主题应用动态效果"""
        theme = self.bullet_theme
        effects = theme.get("effects", [])
        colors = theme.get("colors", {})
        visual = theme.get("visual", {})
        animation = visual.get("animation", "")
        
        primary = colors.get("primary", self.color)
        secondary = colors.get("secondary", (255, 255, 255))
        glow = colors.get("glow", (200, 200, 255))
        
        base_w, base_h = self._base_rect_size
        
        # ========== 火花/金属类效果 ==========
        if "spark_trail" in effects or "metal_shine" in effects:
            # 火花拖尾 + 金属闪光
            pulse = 0.8 + 0.2 * abs(math.sin(t * 2.5))
            new_image = pygame.Surface((base_w + 12, base_h + 18), pygame.SRCALPHA)
            
            # 火花尾迹
            for i in range(4):
                spark_alpha = int(120 * (1 - i / 4) * pulse)
                spark_y = base_h + i * 4
                spark_w = max(4, base_w // 2 - i * 2)
                pygame.draw.ellipse(new_image, (*primary[:3], spark_alpha), 
                                  ((base_w + 12) // 2 - spark_w // 2, spark_y, spark_w, 5))
            
            # 金属高光闪烁
            if "metal_shine" in effects and self.timer % 8 < 4:
                shine_x = (base_w + 12) // 2 + int(3 * math.sin(t * 3))
                pygame.draw.circle(new_image, (255, 255, 255, 200), (shine_x, 8), 3)
            
            new_image.blit(self._base_image, (6, 0))
            self._update_bullet_image(new_image)
            
        # ========== 相位/虚空类效果 ==========
        elif "phase_flicker" in effects or "void_crack_trail" in effects:
            # 相位闪烁 + 虚空裂缝
            flicker = 0.6 + 0.4 * abs(math.sin(t * 4)) if self.timer % 6 < 3 else 1.0
            new_image = pygame.Surface((base_w + 10, base_h + 14), pygame.SRCALPHA)
            
            # 虚空裂缝拖尾
            if "void_crack_trail" in effects:
                for i in range(3):
                    crack_y = base_h + i * 4
                    crack_alpha = int(80 * (1 - i / 3))
                    pygame.draw.line(new_image, (*secondary[:3], crack_alpha),
                                   ((base_w + 10) // 2 - 4, crack_y),
                                   ((base_w + 10) // 2 + 4, crack_y + 3), 2)
            
            # 相位闪烁效果
            if flicker < 0.8:
                temp = self._base_image.copy()
                temp.set_alpha(int(255 * flicker))
                new_image.blit(temp, (5, 0))
            else:
                new_image.blit(self._base_image, (5, 0))
            
            self._update_bullet_image(new_image)
            
        # ========== 量子/时空类效果 ==========
        elif "quantum_glitch" in effects or "position_echo" in effects:
            # 量子故障 + 位置残影
            new_image = pygame.Surface((base_w + 16, base_h + 10), pygame.SRCALPHA)
            
            # 位置残影
            if "position_echo" in effects:
                for i in range(3):
                    echo_alpha = int(60 * (1 - i / 3))
                    offset_x = int(3 * math.sin(t * 2 + i))
                    temp = self._base_image.copy()
                    temp.set_alpha(echo_alpha)
                    new_image.blit(temp, (8 + offset_x - i * 2, 5))
            
            # 量子故障效果
            if "quantum_glitch" in effects and random.random() < 0.15:
                glitch_offset = random.randint(-3, 3)
                new_image.blit(self._base_image, (8 + glitch_offset, 5))
            else:
                new_image.blit(self._base_image, (8, 5))
            
            self._update_bullet_image(new_image)
            
        # ========== 圣光类效果 ==========
        elif "holy_ray" in effects or "divine_glow" in effects:
            # 圣光射线（无光晕）
            pulse = 0.7 + 0.3 * abs(math.sin(t * 1.5))
            new_image = pygame.Surface((base_w + 14, base_h + 14), pygame.SRCALPHA)
            
            # 十字光芒
            if "holy_ray" in effects:
                cx, cy = (base_w + 14) // 2, (base_h + 14) // 2
                ray_len = int(10 * pulse)
                pygame.draw.line(new_image, (*primary[:3], 150), (cx - ray_len, cy), (cx + ray_len, cy), 2)
                pygame.draw.line(new_image, (*primary[:3], 150), (cx, cy - ray_len), (cx, cy + ray_len), 2)
            
            new_image.blit(self._base_image, (7, 7))
            self._update_bullet_image(new_image)
            
        # ========== 龙息/火焰类效果 ==========
        elif "dragon_breath" in effects or "scale_shimmer" in effects:
            # 龙息火焰 + 鳞片闪烁
            flicker = 0.75 + 0.25 * random.random()
            new_image = pygame.Surface((base_w + 12, base_h + 16), pygame.SRCALPHA)
            
            # 火焰拖尾
            flame_colors = [(255, 100, 0), (255, 180, 0), (255, 220, 100)]
            for i, fc in enumerate(flame_colors):
                flame_alpha = int(150 * flicker * (1 - i / 3))
                flame_y = base_h + i * 4
                flame_w = max(4, base_w // 2 - i * 2)
                pygame.draw.ellipse(new_image, (*fc, flame_alpha),
                                  ((base_w + 12) // 2 - flame_w // 2, flame_y, flame_w, 6))
            
            # 鳞片闪光
            if "scale_shimmer" in effects and self.timer % 10 < 5:
                pygame.draw.circle(new_image, (255, 215, 0, 180), 
                                 ((base_w + 12) // 2, base_h // 3), 2)
            
            new_image.blit(self._base_image, (6, 0))
            self._update_bullet_image(new_image)
            
        # ========== 闪电/电弧类效果 ==========
        elif "lightning_arc" in effects or "blade_trail" in effects:
            # 闪电弧 + 刀刃轨迹
            new_image = pygame.Surface((base_w + 14, base_h + 12), pygame.SRCALPHA)
            
            # 电弧效果
            if "lightning_arc" in effects and random.random() < 0.4:
                cx, cy = (base_w + 14) // 2, (base_h + 12) // 2
                for _ in range(2):
                    angle = random.uniform(0, math.pi * 2)
                    length = random.randint(6, 12)
                    ex = cx + int(length * math.cos(angle))
                    ey = cy + int(length * math.sin(angle))
                    pygame.draw.line(new_image, (*primary[:3], 200), (cx, cy), (ex, ey), 1)
            
            # 刀刃轨迹
            if "blade_trail" in effects:
                for i in range(3):
                    trail_alpha = int(100 * (1 - i / 3))
                    pygame.draw.line(new_image, (*secondary[:3], trail_alpha),
                                   ((base_w + 14) // 2, base_h + i * 3),
                                   ((base_w + 14) // 2, base_h + i * 3 + 4), 2)
            
            new_image.blit(self._base_image, (7, 0))
            self._update_bullet_image(new_image)
            
        # ========== 虚空/扭曲类效果 ==========
        elif "void_distortion" in effects or "nebula_swirl" in effects:
            # 虚空扭曲 + 星云漩涡
            pulse = 0.8 + 0.2 * abs(math.sin(t * 1.2))
            new_image = pygame.Surface((base_w + 16, base_h + 16), pygame.SRCALPHA)
            
            # 星云漩涡
            if "nebula_swirl" in effects:
                cx, cy = (base_w + 16) // 2, (base_h + 16) // 2
                for i in range(4):
                    angle = (i * 90 + self.timer * 3) * math.pi / 180
                    px = cx + int(8 * math.cos(angle))
                    py = cy + int(8 * math.sin(angle))
                    pygame.draw.circle(new_image, (*secondary[:3], int(60 * pulse)), (px, py), 3)
            
            new_image.blit(self._base_image, (8, 8))
            self._update_bullet_image(new_image)
            
        # ========== 幽灵/灵魂类效果 ==========
        elif "ghost_face" in effects or "soul_wail" in effects:
            # 幽灵面孔 + 哀嚎
            flicker = 0.5 + 0.5 * abs(math.sin(t * 3)) if random.random() < 0.1 else 1.0
            new_image = pygame.Surface((base_w + 10, base_h + 12), pygame.SRCALPHA)
            
            # 飘动残影
            if "soul_wail" in effects:
                for i in range(2):
                    offset_y = int(2 * math.sin(t * 2 + i))
                    temp = self._base_image.copy()
                    temp.set_alpha(int(60 * (1 - i / 2)))
                    new_image.blit(temp, (5, 0 + offset_y))
            
            temp = self._base_image.copy()
            temp.set_alpha(int(255 * flicker))
            new_image.blit(temp, (5, 6))
            self._update_bullet_image(new_image)
            
        # ========== 水晶/棱镜类效果 ==========
        elif "crystal_prism" in effects or "light_scatter" in effects:
            # 水晶棱镜 + 光线散射
            new_image = pygame.Surface((base_w + 14, base_h + 14), pygame.SRCALPHA)
            
            # 彩虹散射
            if "light_scatter" in effects:
                rainbow = [(255, 0, 0), (255, 165, 0), (255, 255, 0), 
                          (0, 255, 0), (0, 255, 255), (0, 0, 255)]
                for i, color in enumerate(rainbow):
                    angle = (i * 60 + self.timer * 4) * math.pi / 180
                    px = (base_w + 14) // 2 + int(6 * math.cos(angle))
                    py = (base_h + 14) // 2 + int(6 * math.sin(angle))
                    pygame.draw.circle(new_image, (*color, 80), (px, py), 2)
            
            new_image.blit(self._base_image, (7, 7))
            self._update_bullet_image(new_image)
            
        # ========== 触手/生物类效果 ==========
        elif "tentacle_crawl" in effects or "bio_pulse" in effects:
            # 触手蠕动 + 生物脉冲
            pulse = 0.85 + 0.15 * abs(math.sin(t * 2.5))
            new_image = pygame.Surface((base_w + 12, base_h + 12), pygame.SRCALPHA)
            
            # 脉冲光环
            if "bio_pulse" in effects:
                pulse_alpha = int(60 * pulse)
                pygame.draw.ellipse(new_image, (*primary[:3], pulse_alpha), 
                                  (2, 2, base_w + 8, base_h + 8))
            
            new_image.blit(self._base_image, (6, 6))
            self._update_bullet_image(new_image)
            
        # ========== 极光/彗星类效果 ==========
        elif "aurora_tail" in effects or "comet_trail" in effects:
            # 极光尾迹 + 彗星轨迹
            new_image = pygame.Surface((base_w + 10, base_h + 20), pygame.SRCALPHA)
            
            # 彩色尾迹
            trail_colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]
            for i, tc in enumerate(trail_colors):
                trail_alpha = int(100 * (1 - i / 4))
                trail_y = base_h + i * 4
                pygame.draw.ellipse(new_image, (*tc, trail_alpha),
                                  ((base_w + 10) // 2 - 3, trail_y, 6, 5))
            
            new_image.blit(self._base_image, (5, 0))
            self._update_bullet_image(new_image)
            
        # ========== 时空/沙漏类效果 ==========
        elif "hourglass_flow" in effects or "time_sand" in effects:
            # 沙漏流动 + 时间沙
            new_image = pygame.Surface((base_w + 10, base_h + 10), pygame.SRCALPHA)
            
            # 流沙粒子
            if "time_sand" in effects:
                for _ in range(3):
                    px = random.randint(3, base_w + 7)
                    py = random.randint(3, base_h + 7)
                    pygame.draw.circle(new_image, (*secondary[:3], 120), (px, py), 1)
            
            new_image.blit(self._base_image, (5, 5))
            self._update_bullet_image(new_image)
            
        # ========== 熔岩/反应堆类效果 ==========
        elif "lava_crack" in effects or "reactor_pulse" in effects:
            # 熔岩裂纹（无光晕）
            new_image = pygame.Surface((base_w + 12, base_h + 12), pygame.SRCALPHA)
            
            # 能量裂纹
            if "lava_crack" in effects:
                cx, cy = (base_w + 12) // 2, (base_h + 12) // 2
                for i in range(4):
                    angle = (i * 90 + 45) * math.pi / 180
                    ex = cx + int(6 * math.cos(angle))
                    ey = cy + int(6 * math.sin(angle))
                    pygame.draw.line(new_image, (255, 200, 0, 180), (cx, cy), (ex, ey), 1)
            
            new_image.blit(self._base_image, (6, 6))
            self._update_bullet_image(new_image)
            
        # ========== 齿轮/机械类效果 ==========
        elif "gear_rotate" in effects or "piston_pump" in effects:
            # 齿轮旋转（无光晕）
            rotation_angle = (self.timer * 6) % 360
            rotated = pygame.transform.rotate(self._base_image, rotation_angle)
            
            old_center = self.rect.center
            self.image = rotated
            self.rect = self.image.get_rect(center=old_center)
            
        # ========== 灵魂/火焰类效果 ==========
        elif "soul_fire" in effects or "ghostly_fade" in effects:
            # 幽灵火焰
            flicker = 0.6 + 0.4 * abs(math.sin(t * 3))
            new_image = pygame.Surface((base_w + 12, base_h + 14), pygame.SRCALPHA)
            
            # 魂火粒子
            for i in range(3):
                fire_y = base_h - 2 + int(4 * math.sin(t * 2 + i))
                fire_alpha = int(100 * flicker * (1 - i / 3))
                pygame.draw.circle(new_image, (*secondary[:3], fire_alpha),
                                 ((base_w + 12) // 2 + i * 3 - 3, fire_y), 3)
            
            # 渐隐效果
            if "ghostly_fade" in effects and random.random() < 0.1:
                temp = self._base_image.copy()
                temp.set_alpha(int(180 * flicker))
                new_image.blit(temp, (6, 0))
            else:
                new_image.blit(self._base_image, (6, 0))
            
            self._update_bullet_image(new_image)
            
        # ========== 镜面/棱光类效果 ==========
        elif "mirror_reflect" in effects or "prism_ray" in effects:
            # 镜面反射 + 棱镜光线
            new_image = pygame.Surface((base_w + 14, base_h + 14), pygame.SRCALPHA)
            
            # 棱镜光线
            if "prism_ray" in effects:
                cx, cy = (base_w + 14) // 2, (base_h + 14) // 2
                rainbow = [(255, 0, 0), (255, 165, 0), (255, 255, 0), 
                          (0, 255, 0), (0, 255, 255), (0, 0, 255)]
                for i, color in enumerate(rainbow):
                    angle = (i * 60 + self.timer * 5) * math.pi / 180
                    ex = cx + int(8 * math.cos(angle))
                    ey = cy + int(8 * math.sin(angle))
                    pygame.draw.line(new_image, (*color, 100), (cx, cy), (ex, ey), 1)
            
            # 镜面高光
            if "mirror_reflect" in effects and self.timer % 6 < 3:
                pygame.draw.circle(new_image, (255, 255, 255, 200),
                                 ((base_w + 14) // 2, 6), 2)
            
            new_image.blit(self._base_image, (7, 7))
            self._update_bullet_image(new_image)
            
        # ========== 黑雾/恐惧类效果 ==========
        elif "dark_mist" in effects or "fear_aura" in effects:
            # 黑雾弥漫 + 恐惧光环
            pulse = 0.7 + 0.3 * abs(math.sin(t * 1.5))
            new_image = pygame.Surface((base_w + 16, base_h + 16), pygame.SRCALPHA)
            
            # 黑雾
            for i in range(3):
                mist_alpha = int(40 * (1 - i / 3))
                offset_x = int(4 * math.sin(t + i))
                pygame.draw.ellipse(new_image, (30, 0, 50, mist_alpha),
                                  (offset_x, i * 3, base_w + 10, base_h + 10))
            
            new_image.blit(self._base_image, (8, 8))
            self._update_bullet_image(new_image)
            
        # ========== 极光波/彩虹类效果 ==========
        elif "aurora_wave" in effects or "rainbow_trail" in effects:
            # 极光波动 + 彩虹拖尾
            new_image = pygame.Surface((base_w + 12, base_h + 18), pygame.SRCALPHA)
            
            # 彩虹尾迹
            rainbow = [(255, 100, 100), (255, 200, 100), (255, 255, 100),
                      (100, 255, 100), (100, 200, 255), (150, 100, 255)]
            for i, color in enumerate(rainbow):
                trail_y = base_h + i * 3
                trail_alpha = int(80 * (1 - i / 6))
                pygame.draw.ellipse(new_image, (*color, trail_alpha),
                                  ((base_w + 12) // 2 - 4, trail_y, 8, 4))
            
            new_image.blit(self._base_image, (6, 0))
            self._update_bullet_image(new_image)
            
        # ========== 时间波纹/残影类效果 ==========
        elif "time_ripple" in effects or "afterimage_trail" in effects:
            # 时间波纹 + 残影拖尾
            new_image = pygame.Surface((base_w + 12, base_h + 14), pygame.SRCALPHA)
            
            # 残影
            if "afterimage_trail" in effects:
                for i in range(3):
                    temp = self._base_image.copy()
                    temp.set_alpha(int(60 * (1 - i / 3)))
                    new_image.blit(temp, (6, i * 3))
            
            # 时间波纹
            if "time_ripple" in effects:
                pulse = abs(math.sin(t))
                ripple_alpha = int(50 * (1 - pulse))
                cx, cy = (base_w + 12) // 2, (base_h + 14) // 2
                pygame.draw.circle(new_image, (*secondary[:3], ripple_alpha),
                                 (cx, cy), int(8 + 4 * pulse), 1)
            
            new_image.blit(self._base_image, (6, 0))
            self._update_bullet_image(new_image)
            
        # ========== 矩阵/代码类效果 ==========
        elif "matrix_rain" in effects or "code_glitch" in effects:
            # 数字矩阵雨 + 代码故障
            new_image = pygame.Surface((base_w + 10, base_h + 16), pygame.SRCALPHA)
            
            # 数字雨粒子
            if "matrix_rain" in effects:
                for i in range(4):
                    py = base_h + i * 4
                    alpha = int(100 * (1 - i / 4))
                    pygame.draw.rect(new_image, (*primary[:3], alpha),
                                   ((base_w + 10) // 2 - 2, py, 4, 3))
            
            # 故障闪烁
            if "code_glitch" in effects and random.random() < 0.2:
                glitch_x = random.randint(-2, 2)
                new_image.blit(self._base_image, (5 + glitch_x, 0))
            else:
                new_image.blit(self._base_image, (5, 0))
            
            self._update_bullet_image(new_image)
            
        # ========== 烟雾/金属类效果 ==========
        elif "smoke_exhaust" in effects or "metal_texture" in effects:
            # 烟雾排放 + 金属质感
            new_image = pygame.Surface((base_w + 10, base_h + 14), pygame.SRCALPHA)
            
            # 烟雾
            if "smoke_exhaust" in effects:
                for i in range(3):
                    smoke_alpha = int(60 * (1 - i / 3))
                    smoke_y = base_h + i * 4
                    smoke_w = 6 + i * 2
                    offset_x = int(2 * math.sin(t * 2 + i))
                    pygame.draw.ellipse(new_image, (100, 100, 100, smoke_alpha),
                                      ((base_w + 10) // 2 - smoke_w // 2 + offset_x, smoke_y, smoke_w, 5))
            
            new_image.blit(self._base_image, (5, 0))
            self._update_bullet_image(new_image)
            
        # ========== 辐射/毒素类效果 ==========
        elif "radiation_wave" in effects or "toxic_glow" in effects:
            # 辐射波 + 毒素发光
            pulse = 0.7 + 0.3 * abs(math.sin(t * 2.5))
            new_image = pygame.Surface((base_w + 14, base_h + 14), pygame.SRCALPHA)
            
            # 辐射波纹
            if "radiation_wave" in effects:
                cx, cy = (base_w + 14) // 2, (base_h + 14) // 2
                for i in range(2):
                    wave_r = int(6 + 4 * ((t + i * 0.5) % 1))
                    wave_alpha = int(80 * (1 - (t + i * 0.5) % 1))
                    pygame.draw.circle(new_image, (*primary[:3], wave_alpha), (cx, cy), wave_r, 1)
            
            new_image.blit(self._base_image, (7, 7))
            self._update_bullet_image(new_image)
            
        # ========== 熔岩/火星类效果 ==========
        elif "lava_drip" in effects or "ember_burst" in effects:
            # 熔岩滴落 + 火星迸发
            new_image = pygame.Surface((base_w + 12, base_h + 16), pygame.SRCALPHA)
            
            # 熔岩滴
            if "lava_drip" in effects:
                for i in range(2):
                    drip_y = base_h + random.randint(4, 12)
                    drip_x = (base_w + 12) // 2 + random.randint(-4, 4)
                    pygame.draw.circle(new_image, (255, 100, 0, 150), (drip_x, drip_y), 2)
            
            # 火星
            if "ember_burst" in effects:
                for _ in range(2):
                    ex = random.randint(2, base_w + 10)
                    ey = random.randint(0, base_h)
                    pygame.draw.circle(new_image, (255, 200, 50, 200), (ex, ey), 1)
            
            new_image.blit(self._base_image, (6, 0))
            self._update_bullet_image(new_image)
            
        # ========== 等离子/推进类效果 ==========
        elif "plasma_thrust" in effects or "mech_exhaust" in effects:
            # 等离子推进 + 机械排气
            flicker = 0.7 + 0.3 * random.random()
            new_image = pygame.Surface((base_w + 10, base_h + 18), pygame.SRCALPHA)
            
            # 等离子尾焰
            flame_colors = [(100, 200, 255), (50, 150, 255), (0, 100, 200)]
            for i, fc in enumerate(flame_colors):
                flame_alpha = int(180 * flicker * (1 - i / 3))
                flame_y = base_h + i * 4
                flame_w = max(4, 8 - i * 2)
                pygame.draw.ellipse(new_image, (*fc, flame_alpha),
                                  ((base_w + 10) // 2 - flame_w // 2, flame_y, flame_w, 6))
            
            new_image.blit(self._base_image, (5, 0))
            self._update_bullet_image(new_image)
            
        # ========== 冰霜/水晶类效果 ==========
        elif "frost_aura" in effects or "crystal_shine" in effects:
            # 水晶闪光（无光晕）
            new_image = pygame.Surface((base_w + 12, base_h + 12), pygame.SRCALPHA)
            
            # 水晶闪光
            if "crystal_shine" in effects and self.timer % 10 < 5:
                cx, cy = (base_w + 12) // 2, (base_h + 12) // 2
                for i in range(4):
                    angle = (i * 90 + 45) * math.pi / 180
                    ex = cx + int(5 * math.cos(angle))
                    ey = cy + int(5 * math.sin(angle))
                    pygame.draw.line(new_image, (255, 255, 255, 180), (cx, cy), (ex, ey), 1)
            
            new_image.blit(self._base_image, (6, 6))
            self._update_bullet_image(new_image)
            
        # ========== 恶魔/血浆类效果 ==========
        elif "demon_aura" in effects or "blood_splatter" in effects:
            # 血浆飞溅（无光晕）
            new_image = pygame.Surface((base_w + 14, base_h + 14), pygame.SRCALPHA)
            
            # 血浆飞溅
            if "blood_splatter" in effects and random.random() < 0.15:
                for _ in range(2):
                    bx = random.randint(2, base_w + 12)
                    by = random.randint(2, base_h + 12)
                    pygame.draw.circle(new_image, (180, 0, 0, 180), (bx, by), 2)
            
            new_image.blit(self._base_image, (7, 7))
            self._update_bullet_image(new_image)
            
        # ========== 等离子柱/轨道类效果 ==========
        elif "plasma_column" in effects or "orbital_strike" in effects:
            # 等离子柱 + 轨道打击
            new_image = pygame.Surface((base_w + 14, base_h + 14), pygame.SRCALPHA)
            
            # 轨道环
            if "orbital_strike" in effects:
                cx, cy = (base_w + 14) // 2, (base_h + 14) // 2
                for i in range(3):
                    ring_angle = (self.timer * 4 + i * 120) * math.pi / 180
                    rx = cx + int(6 * math.cos(ring_angle))
                    ry = cy + int(6 * math.sin(ring_angle))
                    pygame.draw.circle(new_image, (*secondary[:3], 120), (rx, ry), 2)
            
            new_image.blit(self._base_image, (7, 7))
            self._update_bullet_image(new_image)
            
        # ========== 默认效果 ==========
        else:
            # 无额外效果
            pass
    
    def _update_bullet_image(self, new_image):
        """更新子弹图像并保持中心位置"""
        old_center = self.rect.center
        self.image = new_image
        self.rect = self.image.get_rect(center=old_center)

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
        self.time_slow_factor = 1.0  # 时间膨胀因子：1.0=正常，0.5=减速50%
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
            self.base_speed = 3; self.hp = 75 + lvl * 10
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
            self.base_speed = 4; self.hp = 90 + lvl * 15
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
            self.base_speed = 1.5; self.hp = 115 + lvl * 18; self.radius = 25
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
            self.base_speed = 3.5; self.hp = 85 + lvl * 11; self.radius = 17
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
            self.base_speed = 3; self.hp = 95 + lvl * 11
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
            self.base_speed = 2; self.hp = 78 + lvl * 7
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
            self.base_speed = 1.2; self.hp = 105 + lvl * 14; self.radius = 20
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
            self.base_speed = 3.8; self.hp = 85 + lvl * 10; self.radius = 16
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
            self.base_speed = 2.5; self.hp = 95 + lvl * 12; self.radius = 18
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
            self.base_speed = 3.2; self.hp = 88 + lvl * 10; self.radius = 17
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
            self.base_speed = 2.2; self.hp = 75 + lvl * 8; self.radius = 15
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
        
        # 应用时间膨胀效果：减缓敌人的移动和攻击
        time_slow = getattr(self, 'time_slow_factor', 1.0)
        self.speed = self.base_speed * time_slow
        
        t = pygame.time.get_ticks() / 1000.0
        # timer 按时间膨胀因子增加，导致攻击间隔被延长
        self.timer += time_slow
        
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
                        for i in range(2, WIDTH-50, 200):
                            Bullet(i, self.rect.bottom-20, angle=0, is_enemy=True, b_type="laser_barrage")
                    elif self.phase_index == 1:  # 阶段2：混合激光+等离子
                        for i in range(0, WIDTH, 180):
                            Bullet(i, self.rect.bottom, angle=-10 if i % 2 == 0 else 10, is_enemy=True, b_type="plasma")
                        for i in range(50, WIDTH, 250):
                            Bullet(i, self.rect.bottom-30, angle=0, is_enemy=True, b_type="laser_barrage")
                    else:  # 阶段3：全屏地毯式轰炸（优化：减少弹幕密度）
                        for i in range(0, WIDTH, 120):
                            Bullet(i, self.rect.bottom, angle=random.randint(-20, 20), is_enemy=True, b_type="plasma")
                            
                elif self.type == "assassin":  # 幻影级·虚空刺客 - 快速移动 + 幻影攻击
                    if self.phase_index == 0:  # 阶段1：追踪幻影弹
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx + i*40, self.rect.centery, angle=i*15, is_enemy=True, b_type="phantom")
                    elif self.phase_index == 1:  # 阶段2：密集扇形
                        for i in range(-3, 4):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*12, is_enemy=True, b_type="phantom")
                    else:  # 阶段3：环形幻影弹幕（优化）
                        for i in range(0, 360, 45):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="phantom")
                            
                elif self.type == "seraphim":  # 审判级·炽天使 - 圣光轰炸
                    if self.phase_index == 0:  # 阶段1：散射圣光
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx + i*50, self.rect.bottom, angle=i*15, is_enemy=True, b_type="holy_light")
                    elif self.phase_index == 1:  # 阶段2：连续圣光射线
                        for i in range(-3, 4):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*12, is_enemy=True, b_type="holy_light")
                    else:  # 阶段3：神圣审判轰炸（优化）
                        for i in range(0, 360, 40):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="holy_light")
                            
                elif self.type == "leviathan":  # 深渊巨兽·利维坦 - 触手+虚空尖刺
                    if self.phase_index == 0:  # 阶段1：触手挥击
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx + i*35, self.rect.bottom, angle=i*15, is_enemy=True, b_type="tentacle")
                    elif self.phase_index == 1:  # 阶段2：深渊尖刺
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*18, is_enemy=True, b_type="void_spike")
                    else:  # 阶段3：混合全屏弹幕（优化）
                        for i in range(0, 360, 40):
                            b_type = "tentacle" if i % 2 == 0 else "void_spike"
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type=b_type)
                            
                elif self.type == "overlord":  # 蜂群主宰·奥伯龙 - 蜂群弹幕
                    if self.phase_index == 0:  # 阶段1：散射群弹
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx + i*30, self.rect.bottom, angle=i*12, is_enemy=True, b_type="glitch")
                    elif self.phase_index == 1:  # 阶段2：密集环形
                        for i in range(0, 360, 45):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="glitch")
                    else:  # 阶段3：超密集环形（优化）
                        for i in range(0, 360, 30):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="glitch")
                            
                elif self.type == "ragnarok":  # 终焉机神·诸神黄昏 - 火焰毁灭
                    if self.phase_index == 0:  # 阶段1：火焰喷射
                        for i in range(-3, 4):
                            Bullet(self.rect.centerx, self.rect.bottom, angle=i*12, is_enemy=True, b_type="flame_burst")
                    elif self.phase_index == 1:  # 阶段2：混合环形
                        for i in range(0, 360, 45):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="flame_burst")
                    else:  # 阶段3：全屏火焰地狱（优化）
                        for i in range(0, 360, 36):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="flame_burst")
                            
                elif self.type == "hydra":  # 九头蛇·剧毒领主 - 毒液喷射
                    if self.phase_index == 0:  # 阶段1：散射毒液
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx + i*40, self.rect.bottom, angle=i*12, is_enemy=True, b_type="glitch")
                    elif self.phase_index == 1:  # 阶段2：多向毒液弹幕
                        for i in range(-3, 4):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*12, is_enemy=True, b_type="glitch")
                    else:  # 阶段3：九头混合弹幕（优化）
                        for i in range(0, 360, 40):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="glitch")
                            
                elif self.type == "chronos":  # 时之主·克洛诺斯 - 冰冷时间
                    if self.phase_index == 0:  # 阶段1：散射冰晶
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx + i*50, self.rect.bottom, angle=i*15, is_enemy=True, b_type="ice_shard")
                    elif self.phase_index == 1:  # 阶段2：环形冰晶
                        for i in range(0, 360, 45):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="ice_shard")
                    else:  # 阶段3：密集冰晶地狱（优化）
                        for i in range(0, 360, 30):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="ice_shard")
                            
                elif self.type == "gazer":  # 深渊凝视者 - 盯视射线
                    if self.phase_index == 0:  # 阶段1：散射激光
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*20, is_enemy=True, b_type="laser_barrage")
                    elif self.phase_index == 1:  # 阶段2：聚焦扇形
                        for i in range(-3, 4):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*15, is_enemy=True, b_type="laser_barrage")
                    else:  # 阶段3：环形激光地狱（优化）
                        for i in range(0, 360, 36):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="laser_barrage")
                            
                elif self.type == "lich":  # 赛博巫妖 - 诅咒能量
                    if self.phase_index == 0:  # 阶段1：散射诅咒球
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx + i*35, self.rect.bottom, angle=i*12, is_enemy=True, b_type="glitch")
                    elif self.phase_index == 1:  # 阶段2：混合环形诅咒
                        for i in range(0, 360, 45):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="glitch")
                    else:  # 阶段3：诅咒风暴（优化）
                        for i in range(0, 360, 36):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="glitch")
                            
                elif self.type == "tempest":  # 风暴引擎 - 风刃切割
                    if self.phase_index == 0:  # 阶段1：散射风刃
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx + i*40, self.rect.bottom, angle=i*12, is_enemy=True, b_type="blade_wind")
                    elif self.phase_index == 1:  # 阶段2：扇形风刃
                        for i in range(-3, 4):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*12, is_enemy=True, b_type="blade_wind")
                    else:  # 阶段3：暴风切割（优化）
                        for i in range(0, 360, 36):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="blade_wind")
                            
                elif self.type == "void_golem":  # 虚空魔像 - 齿轮机械
                    if self.phase_index == 0:  # 阶段1：环形齿轮弹
                        for i in range(0, 360, 45):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="gear")
                    elif self.phase_index == 1:  # 阶段2：能量波+追踪弹
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*18, is_enemy=True, b_type="energy")
                    else:  # 阶段3：多向核心冲击（优化）
                        for i in range(0, 360, 36):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="core")
                        
                elif self.type == "abyss_queen":  # 星渊女王 - 星系弹幕
                    if self.phase_index == 0:  # 阶段1：星尘弹+召唤星体
                        for i in range(0, 360, 45):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="star")
                    elif self.phase_index == 1:  # 阶段2：星卫弹幕
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*25, is_enemy=True, b_type="star_guard")
                    else:  # 阶段3：星爆全屏弹幕（优化）
                        for i in range(0, 360, 30):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, is_enemy=True, b_type="star_burst")
                            
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
        
        # 碰撞半径 - 比视觉大小小很多，方便躲避
        self.radius = 15  # 从默认的50(rect的一半)减小到15
        
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
        self.max_ult_charge = 100  # 主大招：只能储存1次
        self.ult_cooldown = 0  # 【新】大招冷却计时器
        self.ult_max_cooldown = 60  # 【新】大招冷却时间：1秒(60帧)
        
        # ========== 【新增】第二大招系统（G键） ==========
        self.ult2_charge = 0
        self.max_ult2_charge = 100  # 副大招：只能储存1次
        self.ult2_cooldown = 0
        self.ult2_max_cooldown = 90  # 冷却1.5秒
        
        # ========== 【新增】第三大招系统（C键） ==========
        self.ult3_charge = 0
        self.max_ult3_charge = 100  # 第三大招：只能储存1次
        self.ult3_cooldown = 0
        self.ult3_max_cooldown = 120  # 冷却2秒
        
        self.last_shot = 0
        self.damage_reduction = 0.0
        
        # 时间膨胀相关属性
        self.time_factor = 1.0  # 敌人速度/攻击因子：1.0=正常，0.5=减速50%
        
        # 混沌注入相关属性
        self.has_chaos = False  # 是否具有混沌效果
        self.chaos_chance = 0.0  # 混沌触发概率
        self.chaos_mult = 1.0  # 混沌伤害倍率
        
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
        
        # 【绯红之刃】鲜血狂热状态（其余机体保持空值即可）
        self.blood_stacks = 0
        self.max_blood_stacks = 25
        self.blood_grace_timer = 0
        self._blood_decay_tick = 0
        
        # 【星界潜行者】暗影标记状态
        self.shadow_marks = 0        # 当前标记的敌人数
        self.max_shadow_marks = 8    # 最大同时标记数
        self.shadow_mark_dmg_bonus = 0.0  # 根据标记数累积的伤害加成
        
        # 【大地守护者】大地之力状态
        self.earth_fury = 0          # 大地怒气
        self.max_earth_fury = 100    # 最大怒气
        self.earth_fury_decay_timer = 0
        self.earth_armor_bonus = 0.0 # 护甲加成
        self.earth_dmg_bonus = 0.0   # 伤害加成
        
        # 【钢铁泰坦】重装过载状态
        self.titan_overload = 0       # 过载能量
        self.max_titan_overload = 100 # 最大过载
        self.titan_next_shot_empowered = False  # 下一发是否强化
        self.titan_armor_stacks = 0   # 装甲层数
        self.max_armor_stacks = 5     # 最大装甲层数
        
        # 【虚空编织者】维度织网状态
        self.weaver_webbed_count = 0  # 当前被网住的敌人数
        self.weaver_web_damage_bonus = 0.0  # 网伤害加成
        
        # 【日冕耀斑】灼热核心状态
        self.solar_heat = 0           # 当前热量
        self.max_solar_heat = 100     # 最大热量
        self.solar_overheat = False   # 是否过热
        self.solar_overheat_timer = 0 # 过热冷却计时器
        self.solar_aura_damage = 0    # 灸烧光环伤害
        
        # 【量子裁决者】量子叠加态状态
        self.arbiter_quantum = 0      # 量子能量
        self.max_arbiter_quantum = 100 # 最大量子能量
        self.arbiter_collapse_ready = False  # 坡缩就绪
        
        # 【日食幽灵】光暗交替状态
        self.eclipse_phase = "light"  # 当前形态: light/dark
        self.eclipse_phase_timer = 0  # 形态切换计时器
        self.eclipse_shield = 0       # 暗影护盾
        self.max_eclipse_shield = 50  # 最大护盾
        self.eclipse_light_bonus = 0.0 # 光态伤害加成
        
        # 【棱镜分光】折射风暴状态
        self.prism_chain_count = 0    # 当前折射链计数
        self.prism_max_chain = 0      # 本局最长折射链
        self.prism_chain_damage = 0.0 # 折射链伤害加成
        
        # 【死灵骑士】亡灵军团状态
        self.necro_ghosts = []        # 亡灵列表
        self.max_necro_ghosts = 6     # 最大亡灵数
        self.necro_ghost_damage = 0   # 亡灵总伤害统计
        
        # 【霓虹突击者】超载引擎状态
        self.striker_charge = 0
        self.max_striker_charge = 100
        self.striker_overdrive = False
        self.striker_overdrive_timer = 0
        self.striker_idle_timer = 0  # 命中间隔计时，决定何时开始衰减
        self.striker_decay_delay = 90  # 约1.5秒无命中后开始衰减
        self.striker_decay_rate = 0.6  # 衰减速度（每帧）
        
        # 【虚空幻影】相位漂移状态
        self.phantom_phase = 0
        self.max_phantom_phase = 100
        self.phantom_intangible = False
        self.phantom_intangible_timer = 0
        
        # 【雷霆战鹰】雷暴连锁状态
        self.thunder_charge = 0
        self.max_thunder_charge = 100
        self.thunder_idle_timer = 0  # 命中间隔计时器
        self.thunder_decay_delay = 60
        self.thunder_decay_rate = 1.0
        
        # 【剧毒蝰蛇】剧毒累积状态
        self.viper_venom_stacks = {}  # {enemy_id: stack_count}
        self.viper_total_poison = 0
        
        # 【幽灵收割者】死神印记状态
        self.specter_focus = None
        self.specter_focus_time = 0
        self.specter_stealth = 0
        self.specter_focus_ready = False
        self.specter_focus_decay_timer = 0
        self.specter_focus_decay_delay = 120
        self.specter_focus_decay_rate = 0.8
        
        # 【极光女神】极光共鸣状态
        self.aurora_orbs = []
        self.max_aurora_orbs = 5
        self.aurora_orb_damage = 0

        # 炮塔系统(固定位置防御塔)
        self.has_turrets = False
        self.turret_count = 0
        self.turret_damage = 0.6
        self.turrets = []  # 存储炮塔对象

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
        # 【新】第二大招冷却更新
        if self.ult2_cooldown > 0: self.ult2_cooldown -= 1
        # 【新】第三大招冷却更新
        if self.ult3_cooldown > 0: self.ult3_cooldown -= 1
        
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
        
        # 【虚空幻影】移动时积累相位
        if self.plane_id == "phantom" and (dx != 0 or dy != 0):
            move_speed = math.sqrt(dx*dx + dy*dy)
            self.gain_phantom_phase(move_speed * 0.18)
        
        # 边界限制
        self.rect.clamp_ip(screen_rect)

        # 【绯红之刃】鲜血狂热状态维护
        self._update_crimson_state()
        # 【星界潜行者】暗影标记状态维护
        self._update_stalker_state()
        # 【大地守护者】大地之力状态维护
        self._update_gaia_state()
        # 【钢铁泰坦】重装过载状态维护
        self._update_titan_state()
        # 【虚空编织者】维度织网状态维护
        self._update_weaver_state()
        # 【日冕耀斑】灼热核心状态维护
        self._update_solar_state()
        # 【量子裁决者】量子叠加态状态维护
        self._update_arbiter_state()
        # 【日食幽灵】光暗交替状态维护
        self._update_eclipse_state()
        # 【棱镜分光】光谱共振状态维护
        self._update_prism_state()
        # 【死灵骑士】亡魂收割状态维护
        self._update_necro_state()
        # 【霓虹突击者】超载引擎状态维护
        self._update_striker_state()
        # 【虚空幻影】相位漂移状态维护
        self._update_phantom_state()
        # 【雷霆战鹰】雷暴连锁状态维护
        self._update_thunder_state()
        # 【剧毒蝰蛇】剧毒累积状态维护
        self._update_viper_state()
        # 【幽灵收割者】死神印记状态维护
        self._update_specter_state()
        # 【极光女神】极光共鸣状态维护
        self._update_aurora_state()

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
        
        # 计算追踪强度（如果有追踪卡牌）
        homing_value = getattr(self, 'homing_strength', 0) if getattr(self, 'has_homing', False) else 0
        
        # 【调试】追踪卡牌诊断
        if hasattr(self, 'has_homing') or hasattr(self, 'homing_strength'):
            print(f"[追踪诊断] has_homing={getattr(self, 'has_homing', False)}, homing_strength={getattr(self, 'homing_strength', 0)}, homing_value={homing_value}")
        
        # ========== 1. 霓虹突击者 - 直线扇形射击 ==========
        if pid == "striker":
            # 中间直射 + 两侧略微散开
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 15
                angle = -5 + i * 5 if cnt > 1 else 0
                Bullet(self.rect.centerx + offset_x, self.rect.top, angle=angle, 
                       color=color, b_type=b_type, piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
        
        # ========== 2. 虚空幻影 - 快速多枚散射 ==========
        elif pid == "phantom":
            # 高射速特性：发射更多细小子弹
            for i in range(cnt * 2):
                spread = (i - cnt + 0.5) * 8
                angle = random.uniform(-15, 15)
                Bullet(self.rect.centerx + spread, self.rect.top, angle=angle,
                       color=color, b_type=b_type, piercing=self.piercing//2 if self.piercing else 0, homing=homing_value, bullet_theme=self.bullet_theme)
        
        # ========== 3. 钢铁泰坦 - 重装过载火箭 ==========
        elif pid == "titan":
            # 低射速、高威力：发射强力火箭
            is_empowered = getattr(self, 'titan_next_shot_empowered', False)
            
            if is_empowered:
                # 过载弹：发射巨型爆裂火箭
                self.titan_next_shot_empowered = False
                self.titan_overload = 0
                # 发射强化弹（标记为过载弹）
                for i in range(cnt + 1):  # 额外+1发
                    offset_x = (i - cnt/2) * 30
                    bullet = Bullet(self.rect.centerx + offset_x, self.rect.top, 
                           color=(255, 100, 0), b_type=b_type, piercing=self.piercing + 5, homing=homing_value, bullet_theme=self.bullet_theme)
                    bullet.is_titan_empowered = True  # 标记为过载弹
                    bullet.speed = bullet.speed * 0.8  # 稍慢但更强
                # 过载发射视觉
                FloatingText(self.rect.centerx, self.rect.top - 30, "💥重炮齐射!", ORANGE)
                for _ in range(8):
                    Particle(self.rect.center, ORANGE)
            else:
                # 普通射击 + 积蓄过载
                for i in range(cnt):
                    offset_x = (i - (cnt-1)/2) * 25
                    Bullet(self.rect.centerx + offset_x, self.rect.top, 
                           color=color, b_type=b_type, piercing=self.piercing + 2, homing=homing_value, bullet_theme=self.bullet_theme)
                # 每次射击积蓄过载
                if hasattr(self, 'gain_titan_overload'):
                    self.gain_titan_overload(18)  # 约5-6发满过载
        
        # ========== 4. 极光女神 - 范围电浆波 ==========
        elif pid == "aurora":
            # 范围型：发射扇形波纹攻击
            for i in range(cnt + 2):
                angle = -30 + i * (60 / (cnt + 1))
                Bullet(self.rect.centerx, self.rect.top, angle=angle,
                       color=color, b_type=b_type, piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
        
        # ========== 5. 幽灵收割者 - 单发极高伤害 ==========
        elif pid == "specter":
            # 射速极慢但单发超高伤害
            if cnt > 0:  # 应该是1
                Bullet(self.rect.centerx, self.rect.top,
                       color=color, b_type=b_type, piercing=self.piercing + 5, homing=homing_value, bullet_theme=self.bullet_theme)
        
        # ========== 6. 雷霆战鹰 - 多段连锁闪电 ==========
        elif pid == "thunderbird":
            # 发射闪电链：正常数量的闪电，自带连锁效果
            spacing = 20
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * spacing
                Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=color, b_type="lightning", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
        
        # ========== 7. 剧毒蝰蛇 - 持续毒液喷射 ==========
        elif pid == "viper":
            # 连续喷射：在一定范围内发射多枚毒液
            for i in range(cnt + 1):
                spread = (i - cnt/2) * 12
                angle = random.uniform(-20, 20)
                Bullet(self.rect.centerx + spread, self.rect.top, angle=angle,
                       color=color, b_type="acid", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
        
        # ========== 8. 绯红之刃 - 高频旋转飞刃 ==========
        elif pid == "crimson":
            # 高射速特性：发射旋转的飞刃
            time_factor = pygame.time.get_ticks() / 100  # 时间因子实现旋转效果
            for i in range(cnt * 2):
                angle = (time_factor + i * (360 / (cnt * 2))) % 360
                Bullet(self.rect.centerx, self.rect.top, angle=angle,
                       color=color, b_type="blade", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
        
        # ========== 9. 星界潜行者 - 追踪星镖 ==========
        elif pid == "stalker":
            # 追踪特性：发射自动追踪的星镖
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 20
                Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=color, b_type="star", piercing=self.piercing, 
                       homing=max(homing_value, 0.2), bullet_theme=self.bullet_theme)  # 自带追踪+卡牌追踪
        
        # ========== 10. 大地守护者 - 岩石冲击 ==========
        elif pid == "gaia":
            # 防御型特性：发射较少但更强的岩石弹，怒气越高子弹越大
            fury_ratio = getattr(self, 'earth_fury', 0) / max(1, getattr(self, 'max_earth_fury', 100))
            base_count = max(1, cnt)
            # 怒气高时散射角度收窄，更精准
            spread_angle = 35 - 15 * fury_ratio  # 35°→20°
            for i in range(base_count):
                if base_count == 1:
                    angle = 0
                else:
                    angle = -spread_angle + i * (spread_angle * 2 / (base_count - 1))
                # 传递怒气比例给子弹（通过自定义属性）
                bullet = Bullet(self.rect.centerx, self.rect.top, angle=angle,
                       color=color, b_type="thorn", piercing=self.piercing + 1, homing=homing_value, bullet_theme=self.bullet_theme)
                # 怒气加成：子弹更大更慢但更强
                bullet.fury_scale = 1 + fury_ratio * 0.5  # 最大1.5倍大小
        
        # ========== 11. 虚空编织者 - 维度蛛网 ==========
        elif pid == "weaver":
            # 控制特性：发射粘稠的蛛网，根据被网敌人数量增强
            webbed = getattr(self, 'weaver_webbed_count', 0)
            extra_shots = min(2, webbed // 2)  # 每2个被网敌人额外+1发
            total_shots = cnt + extra_shots
            for i in range(total_shots):
                offset_x = (i - (total_shots-1)/2) * 18
                angle = random.uniform(-8, 8)  # 轻微散布
                bullet = Bullet(self.rect.centerx + offset_x, self.rect.top, angle=angle,
                       color=color, b_type="web", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
                bullet.speed = -10  # 稍快一点
        
        # ========== 12. 日冕耀斑 - 灼热火焰喷流 ==========
        elif pid == "solar":
            # 检查过热
            if getattr(self, 'solar_overheat', False):
                # 过热时不能射击，显示冷却中
                if random.random() < 0.1:
                    FloatingText(self.rect.centerx, self.rect.top - 10, "冷却中...", (150, 150, 150))
                return  # 不发射
            # 极高射速：发射连续的火焰
            heat_ratio = getattr(self, 'solar_heat', 0) / max(1, getattr(self, 'max_solar_heat', 100))
            flame_count = cnt * 3 + int(heat_ratio * 2)  # 热量高时火焰更密集
            for i in range(flame_count):
                spread = (i - flame_count/2 + 0.5) * 5
                angle = random.uniform(-10 - heat_ratio * 5, 10 + heat_ratio * 5)  # 热量高时扩散更大
                bullet = Bullet(self.rect.centerx + spread, self.rect.top, angle=angle,
                       color=color, b_type="flame", piercing=self.piercing//2 if self.piercing else 0, homing=homing_value, bullet_theme=self.bullet_theme)
                bullet.is_solar_flame = True
            # 每次射击积累热量
            if hasattr(self, 'gain_solar_heat'):
                self.gain_solar_heat(2)  # 约50次射击过热（约3秒持续射击）
        
        # ========== 13. 量子裁决者 - 分裂量子块 ==========
        elif pid == "arbiter":
            # 分裂特性：发射会分裂的量子块
            is_collapse = getattr(self, 'arbiter_collapse_ready', False)
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 18
                bullet = Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=NEON_PURPLE if is_collapse else color, b_type="quant", 
                       piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
                bullet.is_collapse_shot = is_collapse  # 标记坑缩弹
                if is_collapse:
                    bullet.damage_mult = 1.5  # 坑缩弹基础伤害+50%
        
        # ========== 14. 日食幽灵 - 双核心双线射击 ==========
        elif pid == "eclipse":
            # 双核心特性：同时从两个点发射
            left_x = self.rect.centerx - 15
            right_x = self.rect.centerx + 15
            is_light = getattr(self, 'eclipse_phase', 'light') == "light"
            bullet_color = (255, 220, 100) if is_light else (80, 40, 120)
            for i in range(cnt):
                offset = (i - (cnt-1)/2) * 10
                # 左核心
                b1 = Bullet(left_x + offset, self.rect.top, 
                       color=bullet_color, b_type="shadow", piercing=self.piercing, angle=-5, homing=homing_value, bullet_theme=self.bullet_theme)
                b1.is_eclipse_light = is_light
                # 右核心
                b2 = Bullet(right_x + offset, self.rect.top,
                       color=bullet_color, b_type="shadow", piercing=self.piercing, angle=5, homing=homing_value, bullet_theme=self.bullet_theme)
                b2.is_eclipse_light = is_light
        
        # ========== 15. 棱镜分光 - 一发三道分裂 ==========
        elif pid == "prism":
            # 分裂特性：每发子弹发射后会分裂成三道，命中后折射
            chain_bonus = getattr(self, 'prism_chain_damage', 0)
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 16
                # 中间直射 - 蓝色
                b1 = Bullet(self.rect.centerx + offset_x, self.rect.top, angle=0,
                       color=(100, 180, 255), b_type="refract", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
                b1.refract_count = 0
                b1.damage_mult = 1 + chain_bonus
                # 左侧散射 - 紫色
                b2 = Bullet(self.rect.centerx + offset_x, self.rect.top, angle=-25,
                       color=(180, 100, 255), b_type="refract", piercing=self.piercing//2, homing=homing_value, bullet_theme=self.bullet_theme)
                b2.refract_count = 0
                b2.damage_mult = 1 + chain_bonus
                # 右侧散射 - 青色
                b3 = Bullet(self.rect.centerx + offset_x, self.rect.top, angle=25,
                       color=(100, 255, 180), b_type="refract", piercing=self.piercing//2, homing=homing_value, bullet_theme=self.bullet_theme)
                b3.refract_count = 0
                b3.damage_mult = 1 + chain_bonus
        
        # ========== 16. 死灵骑士 - 亡灵射击 ==========
        elif pid == "necro":
            # 亡灵特性：子弹带有亡灵气息
            ghost_count = len(getattr(self, 'necro_ghosts', []))
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 18
                bullet = Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=color, b_type="spectral", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
                bullet.is_necro_bullet = True
                # 亡灵越多子弹越亮
                if ghost_count > 0:
                    brightness = min(255, 150 + ghost_count * 20)
                    bullet.color = (brightness, 50, int(100 + ghost_count * 15))
        
        # 默认情况
        else:
            cnt = self.bullet_count
            start_x = self.rect.centerx - (cnt-1)*10
            for i in range(cnt):
                Bullet(start_x + i*20, self.rect.top, color=color, b_type=b_type, 
                       piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)

    def spawn_turrets(self):
        """生成固定位置的防御炮塔"""
        if not hasattr(self, 'has_turrets') or not self.has_turrets:
            return
        
        # 清空现有炮塔
        self.turrets = []
        
        # 根据炮塔数量在屏幕固定位置生成
        turret_positions = []
        if self.turret_count == 2:
            # 2个炮塔: 左上和右上
            turret_positions = [(150, 150), (WIDTH - 150, 150)]
        elif self.turret_count == 4:
            # 4个炮塔: 四个角落
            turret_positions = [
                (150, 150), (WIDTH - 150, 150),
                (150, HEIGHT - 200), (WIDTH - 150, HEIGHT - 200)
            ]
        elif self.turret_count == 6:
            # 6个炮塔: 上中下各2个
            turret_positions = [
                (150, 150), (WIDTH - 150, 150),
                (150, HEIGHT // 2), (WIDTH - 150, HEIGHT // 2),
                (150, HEIGHT - 200), (WIDTH - 150, HEIGHT - 200)
            ]
        
        # 创建炮塔对象
        for pos in turret_positions:
            turret = DefenseTurret(pos[0], pos[1], self.damage * self.turret_damage, self.bullet_theme)
            self.turrets.append(turret)

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
            
            # ========== 重写后的机体大招 ==========
            if pid == "striker":
                # 毁灭光束：超强贯穿光柱
                FinalBeam(self)
            
            elif pid == "phantom": 
                # 时空冻结：冻结所有敌人和子弹3秒，释放时间斩击
                global global_time_freeze
                global_time_freeze = 180
                for m in mobs:
                    TimeSlash(m.rect.center)
                for eb in enemy_bullets:
                    eb.frozen = True
            
            elif pid == "titan":
                # 战术核弹：全屏核爆
                NukeExplosion()
            
            elif pid == "aurora":
                # 极光天幕：波动控场
                AuroraCurtain()
            
            elif pid == "specter":
                # 死神降临：旋转镰刀收割
                DeathScythe(self.rect.center)
            
            elif pid == "void":
                # 虚空撕裂：维度裂隙阵列
                VoidRift((WIDTH/2, HEIGHT/2))
            
            elif pid == "thunderbird":
                # 雷神降世：全屏雷暴风暴，闪电从天而降
                ThunderStorm(self)
            
            elif pid == "viper":
                # 腐蚀毒雾：全屏毒气弥漫，持续腐蚀
                ToxicMiasma(self)
            
            elif pid == "crimson":
                # 鲜血新月：360度旋转血刃斩击
                BloodMoonSlash(self)
            
            elif pid == "stalker":
                # 群星坠落：星镖从四面八方射向敌人
                StarfallBarrage(self)
            
            elif pid == "gaia":
                # 自然之怒：荆棘从地面涌出
                NatureWrath(self)
            
            elif pid == "weaver":
                # 维度陷阱：蛛网维度牢笼
                DimensionTrap(self)
            
            elif pid == "solar":
                # 超新星爆发：太阳核心爆发
                SupernovaExplosion(self)
            
            elif pid == "arbiter":
                # 矩阵重置：几何量子打击
                QuantumMatrix(self)
            
            elif pid == "eclipse":
                # 黑日降临：双核吸收黑洞
                EclipseVortex(self)
            
            elif pid == "prism":
                # 光谱爆裂：彩虹光线分裂
                PrismBurst(self)
            
            elif pid == "necro":
                # 亡灵收割：灵魂吸取风暴
                SoulHarvest(self)
            
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

    def apply_crimson_blood(self, enemy, damage, hit_pos=None):
        """绯红之刃固有：命中后吸血并引爆血浪"""
        if self.plane_id != "crimson" or enemy is None:
            return
        hit_pos = hit_pos or enemy.rect.center
        self.blood_stacks = min(self.max_blood_stacks, self.blood_stacks + 1)
        self.blood_grace_timer = 240  # 4秒宽限
        self._blood_decay_tick = 0
        stack_ratio = self.blood_stacks / max(1, self.max_blood_stacks)
        lifesteal_ratio = 0.04 + 0.12 * stack_ratio
        heal_amount = damage * lifesteal_ratio
        if heal_amount > 0:
            prev_hp = self.hp
            self.hp = min(self.max_hp, self.hp + heal_amount)
            heal_delta = self.hp - prev_hp
            if heal_delta > 0:
                FloatingText(int(hit_pos[0]), int(hit_pos[1]) - 18, f"+{int(heal_delta)}", CRIMSON)
        splash_radius = 80 + 90 * stack_ratio
        splash_damage = max(8, damage * (0.12 + 0.28 * stack_ratio))
        for mob in list(mobs):
            if mob == enemy or mob.hp <= 0:
                continue
            dist = math.hypot(mob.rect.centerx - hit_pos[0], mob.rect.centery - hit_pos[1])
            if dist <= splash_radius:
                mob.hp -= splash_damage
                FloatingText(mob.rect.centerx, mob.rect.top - 10, f"-{int(splash_damage)}", CRIMSON)
                Particle(mob.rect.center, CRIMSON)
        # 中心血雾
        for _ in range(4):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(5, 40)
            px = hit_pos[0] + math.cos(angle) * dist
            py = hit_pos[1] + math.sin(angle) * dist
            Particle((int(px), int(py)), (200, 30, 60))

    def apply_stalker_mark(self, enemy, damage, hit_pos=None):
        """星界潜行者固有：命中敌人施加暗影标记，标记目标受伤增加并吸引星镖"""
        if self.plane_id != "stalker" or enemy is None:
            return
        hit_pos = hit_pos or enemy.rect.center
        # 施加/刷新标记
        if not hasattr(enemy, 'shadow_mark'):
            enemy.shadow_mark = 0
            enemy.shadow_mark_timer = 0
        if enemy.shadow_mark == 0:
            # 新标记
            self.shadow_marks = min(self.max_shadow_marks, self.shadow_marks + 1)
        enemy.shadow_mark = min(5, enemy.shadow_mark + 1)  # 标记层数上限5
        enemy.shadow_mark_timer = 300  # 5秒持续
        # 标记视觉
        for _ in range(3):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(8, 20)
            px = hit_pos[0] + math.cos(angle) * dist
            py = hit_pos[1] + math.sin(angle) * dist
            Particle((int(px), int(py)), INDIGO)
        # 计算伤害加成
        self.shadow_mark_dmg_bonus = self.shadow_marks * 0.04  # 每个标记+4%伤害

    def _update_stalker_state(self):
        """每帧更新标记计数"""
        if self.plane_id != "stalker":
            return
        active_marks = 0
        for enemy in list(mobs):
            if hasattr(enemy, 'shadow_mark') and enemy.shadow_mark > 0:
                enemy.shadow_mark_timer -= 1
                if enemy.shadow_mark_timer <= 0:
                    enemy.shadow_mark = 0
                else:
                    active_marks += 1
                    # 标记敌人周围偶尔出现星尘粒子
                    if random.random() < 0.08:
                        Particle(enemy.rect.center, INDIGO)
        self.shadow_marks = active_marks
        self.shadow_mark_dmg_bonus = active_marks * 0.04

    def gain_earth_fury(self, amount):
        """大地守护者受伤时积蓄怒气"""
        if self.plane_id != "gaia":
            return
        self.earth_fury = min(self.max_earth_fury, self.earth_fury + amount)
        self.earth_fury_decay_timer = 360  # 6秒不受伤后开始衰减
        fury_ratio = self.earth_fury / self.max_earth_fury
        self.earth_armor_bonus = fury_ratio * 0.50  # 最高50%减伤
        self.earth_dmg_bonus = fury_ratio * 0.80    # 最高80%伤害加成
        # 怒气加速攻击：最高30%减少射击间隔
        self.shoot_delay = int(self.plane_data["delay"] * (1 - fury_ratio * 0.30))
        # 怒气视觉：绿色岩石粒子
        if self.earth_fury > 30 and random.random() < 0.4:
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(15, 30)
            px = self.rect.centerx + math.cos(angle) * dist
            py = self.rect.centery + math.sin(angle) * dist
            Particle((int(px), int(py)), FOREST)

    def apply_gaia_entangle(self, enemy, damage, hit_pos=None):
        """大地守护者固有：命中敌人有几率缠绕"""
        if self.plane_id != "gaia" or enemy is None:
            return
        hit_pos = hit_pos or enemy.rect.center
        fury_ratio = self.earth_fury / max(1, self.max_earth_fury)
        entangle_chance = 0.12 + 0.18 * fury_ratio  # 12%-30%几率
        if random.random() < entangle_chance:
            if not hasattr(enemy, 'entangle_timer'):
                enemy.entangle_timer = 0
                enemy.entangle_damage = 0
            enemy.entangle_timer = 240  # 4秒定身
            enemy.entangle_damage = max(12, damage * 0.15)  # 持续伤害增强
            # 缠绕视觉
            FloatingText(int(hit_pos[0]), int(hit_pos[1]) - 15, "🌿缠绕!", FOREST)
            for _ in range(5):
                angle = random.uniform(0, math.pi * 2)
                dist = random.uniform(10, 25)
                px = hit_pos[0] + math.cos(angle) * dist
                py = hit_pos[1] + math.sin(angle) * dist
                Particle((int(px), int(py)), FOREST)

    def _update_gaia_state(self):
        """每帧更新大地怒气"""
        if self.plane_id != "gaia":
            return
        # 衰减计时
        if self.earth_fury > 0:
            if self.earth_fury_decay_timer > 0:
                self.earth_fury_decay_timer -= 1
            else:
                # 缓慢衰减
                self.earth_fury = max(0, self.earth_fury - 0.2)
                fury_ratio = self.earth_fury / self.max_earth_fury
                self.earth_armor_bonus = fury_ratio * 0.50
                self.earth_dmg_bonus = fury_ratio * 0.80
                self.shoot_delay = int(self.plane_data["delay"] * (1 - fury_ratio * 0.30))
        # 高怒气时持续粒子（更明显）
        if self.earth_fury > 50 and random.random() < 0.15:
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(20, 35)
            px = self.rect.centerx + math.cos(angle) * dist
            py = self.rect.centery + math.sin(angle) * dist
            Particle((int(px), int(py)), (80, 140, 60))

    def gain_titan_overload(self, amount):
        """钢铁泰坦射击时积蓄过载能量"""
        if self.plane_id != "titan":
            return
        self.titan_overload = min(self.max_titan_overload, self.titan_overload + amount)
        # 过载满时触发强化
        if self.titan_overload >= self.max_titan_overload:
            self.titan_next_shot_empowered = True
            # 过载满视觉
            for _ in range(5):
                angle = random.uniform(0, math.pi * 2)
                dist = random.uniform(15, 35)
                px = self.rect.centerx + math.cos(angle) * dist
                py = self.rect.centery + math.sin(angle) * dist
                Particle((int(px), int(py)), ORANGE)
            FloatingText(self.rect.centerx, self.rect.top - 20, "⚡过载!", ORANGE)

    def gain_titan_armor(self):
        """钢铁泰坦受伤时获得装甲层数"""
        if self.plane_id != "titan":
            return
        self.titan_armor_stacks = min(self.max_armor_stacks, self.titan_armor_stacks + 1)
        # 装甲视觉
        if self.titan_armor_stacks >= 3:
            for _ in range(3):
                angle = random.uniform(0, math.pi * 2)
                dist = random.uniform(20, 30)
                px = self.rect.centerx + math.cos(angle) * dist
                py = self.rect.centery + math.sin(angle) * dist
                Particle((int(px), int(py)), CYBER_AMBER)

    def _update_titan_state(self):
        """每帧更新泰坦状态"""
        if self.plane_id != "titan":
            return
        # 过载缓慢衰减（如果没满）
        if self.titan_overload > 0 and not self.titan_next_shot_empowered:
            self.titan_overload = max(0, self.titan_overload - 0.15)
        # 装甲层数缓慢衰减（每3秒减1层）
        if self.titan_armor_stacks > 0:
            if not hasattr(self, '_armor_decay_timer'):
                self._armor_decay_timer = 0
            self._armor_decay_timer += 1
            if self._armor_decay_timer >= 180:  # 3秒
                self._armor_decay_timer = 0
                self.titan_armor_stacks = max(0, self.titan_armor_stacks - 1)
        # 高过载粒子
        if self.titan_overload > 60 and random.random() < 0.12:
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(18, 30)
            px = self.rect.centerx + math.cos(angle) * dist
            py = self.rect.centery + math.sin(angle) * dist
            Particle((int(px), int(py)), (255, 150, 50))

    def apply_weaver_web(self, enemy, damage, hit_pos=None):
        """虚空编织者固有：命中敌人施加维度网"""
        if self.plane_id != "weaver" or enemy is None:
            return
        hit_pos = hit_pos or enemy.rect.center
        # 施加网缚效果
        if not hasattr(enemy, 'weaver_web_timer'):
            enemy.weaver_web_timer = 0
            enemy.weaver_web_slow = 0.5
        enemy.weaver_web_timer = 180  # 3秒网缚
        enemy.weaver_web_slow = 0.3   # 70%减速
        enemy.weaver_web_dot = max(5, damage * 0.08)  # 持续伤害
        # 网缚视觉
        for _ in range(4):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(8, 18)
            px = hit_pos[0] + math.cos(angle) * dist
            py = hit_pos[1] + math.sin(angle) * dist
            Particle((int(px), int(py)), WEB_GRAY)

    def _update_weaver_state(self):
        """每帧更新编织者状态"""
        if self.plane_id != "weaver":
            return
        webbed_enemies = []
        for enemy in list(mobs):
            if hasattr(enemy, 'weaver_web_timer') and enemy.weaver_web_timer > 0:
                webbed_enemies.append(enemy)
                enemy.weaver_web_timer -= 1
                # 减速效果
                enemy.time_slow_factor = min(getattr(enemy, 'time_slow_factor', 1.0), 
                                            getattr(enemy, 'weaver_web_slow', 0.5))
                # 网缚视觉
                if random.random() < 0.1:
                    Particle(enemy.rect.center, (180, 180, 180))
        self.weaver_webbed_count = len(webbed_enemies)
        # 根据被网敌人数量计算伤害加成
        self.weaver_web_damage_bonus = self.weaver_webbed_count * 0.06  # 每个被网敌人+6%伤害
        # 维度连线：被网敌人之间产生伤害连线
        if len(webbed_enemies) >= 2:
            # 每30帧触发一次连线伤害
            if not hasattr(self, '_web_link_timer'):
                self._web_link_timer = 0
            self._web_link_timer += 1
            if self._web_link_timer >= 30:
                self._web_link_timer = 0
                link_damage = self.damage * 0.3 * len(webbed_enemies)
                for enemy in webbed_enemies:
                    enemy.hp -= link_damage
                    FloatingText(enemy.rect.centerx, enemy.rect.top - 10, 
                               f"-{int(link_damage)}", WEB_GRAY)

    def gain_solar_heat(self, amount):
        """日冕耀斑射击时积累热量"""
        if self.plane_id != "solar" or self.solar_overheat:
            return
        self.solar_heat = min(self.max_solar_heat, self.solar_heat + amount)
        self._solar_shoot_timer = 30  # 标记正在射击，30帧内不衰减
        heat_ratio = self.solar_heat / self.max_solar_heat
        # 热量加成伤害
        self.solar_aura_damage = self.damage * heat_ratio * 0.5
        # 过热检测
        if self.solar_heat >= self.max_solar_heat:
            self.solar_overheat = True
            self.solar_overheat_timer = 60  # 1秒冷却
            FloatingText(self.rect.centerx, self.rect.top - 20, "🔥过热!", (255, 100, 0))
            for _ in range(8):
                Particle(self.rect.center, (255, 80, 0))
        # 热量视觉
        if self.solar_heat > 50 and random.random() < 0.2:
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(12, 25)
            px = self.rect.centerx + math.cos(angle) * dist
            py = self.rect.centery + math.sin(angle) * dist
            Particle((int(px), int(py)), BRIGHT_ORANGE)

    def _update_solar_state(self):
        """每帧更新日冕状态"""
        if self.plane_id != "solar":
            return
        # 更新射击计时器
        if hasattr(self, '_solar_shoot_timer') and self._solar_shoot_timer > 0:
            self._solar_shoot_timer -= 1
        if self.solar_overheat:
            # 过热冷却中
            self.solar_overheat_timer -= 1
            if self.solar_overheat_timer <= 0:
                self.solar_overheat = False
                self.solar_heat = 0
                FloatingText(self.rect.centerx, self.rect.top - 20, "✔冷却完成", BRIGHT_ORANGE)
        else:
            # 热量自然衰减（只有停止射击后才衰减）
            shoot_timer = getattr(self, '_solar_shoot_timer', 0)
            if self.solar_heat > 0 and shoot_timer <= 0:
                self.solar_heat = max(0, self.solar_heat - 0.5)
                heat_ratio = self.solar_heat / self.max_solar_heat
                self.solar_aura_damage = self.damage * heat_ratio * 0.5
        # 灸烧光环：对近距离敌人造成伤害
        if self.solar_heat > 30 and not self.solar_overheat:
            aura_radius = 80 + 40 * (self.solar_heat / self.max_solar_heat)
            for enemy in list(mobs):
                dist = math.hypot(enemy.rect.centerx - self.rect.centerx,
                                enemy.rect.centery - self.rect.centery)
                if dist <= aura_radius:
                    # 每15帧造成一次灸烧伤害
                    if not hasattr(self, '_aura_tick'):
                        self._aura_tick = 0
                    self._aura_tick += 1
                    if self._aura_tick >= 15:
                        self._aura_tick = 0
                        aura_dmg = self.solar_aura_damage
                        if aura_dmg > 0:
                            enemy.hp -= aura_dmg
                            if random.random() < 0.3:
                                FloatingText(enemy.rect.centerx, enemy.rect.top - 8, 
                                           f"-{int(aura_dmg)}", (255, 150, 50))
                            Particle(enemy.rect.center, (255, 120, 30))

    def gain_arbiter_quantum(self, amount):
        """量子裁决者命中时积累量子能量"""
        if self.plane_id != "arbiter":
            return
        self.arbiter_quantum = min(self.max_arbiter_quantum, self.arbiter_quantum + amount)
        # 量子满载时准备坡缩
        if self.arbiter_quantum >= self.max_arbiter_quantum and not self.arbiter_collapse_ready:
            self.arbiter_collapse_ready = True
            FloatingText(self.rect.centerx, self.rect.top - 20, "⚡量子坑缩就绪!", NEON_PURPLE)
            for _ in range(6):
                Particle(self.rect.center, NEON_PURPLE)

    def trigger_quantum_collapse(self, target, hit_pos):
        """触发量子坑缩爆发"""
        if self.plane_id != "arbiter" or not self.arbiter_collapse_ready:
            return 0
        self.arbiter_collapse_ready = False
        self.arbiter_quantum = 0
        # 坑缩爆发伤害
        collapse_damage = self.damage * 3.0
        collapse_radius = 100
        FloatingText(hit_pos[0], hit_pos[1] - 20, f"☢坑缩!-{int(collapse_damage)}", NEON_PURPLE)
        # 爆炸视觉
        for _ in range(12):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(20, 50)
            px = hit_pos[0] + math.cos(angle) * dist
            py = hit_pos[1] + math.sin(angle) * dist
            Particle((int(px), int(py)), NEON_PURPLE)
        # 对范围内敌人造成伤害
        for enemy in list(mobs):
            dist = math.hypot(enemy.rect.centerx - hit_pos[0], enemy.rect.centery - hit_pos[1])
            if dist <= collapse_radius and enemy != target:
                aoe_dmg = collapse_damage * (1 - dist / collapse_radius) * 0.6
                enemy.hp -= aoe_dmg
                FloatingText(enemy.rect.centerx, enemy.rect.top - 10, f"-{int(aoe_dmg)}", (180, 100, 255))
        return collapse_damage

    def _update_arbiter_state(self):
        """每帧更新量子裁决者状态"""
        if self.plane_id != "arbiter":
            return
        # 量子能量缓慢衰减
        if self.arbiter_quantum > 0 and not self.arbiter_collapse_ready:
            self.arbiter_quantum = max(0, self.arbiter_quantum - 0.1)
        # 量子粒子效果
        if self.arbiter_quantum > 50 and random.random() < 0.15:
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(15, 28)
            px = self.rect.centerx + math.cos(angle) * dist
            py = self.rect.centery + math.sin(angle) * dist
            Particle((int(px), int(py)), NEON_PURPLE)

    def toggle_eclipse_phase(self):
        """切换日食幽灵的光/暗形态"""
        if self.plane_id != "eclipse":
            return
        if self.eclipse_phase == "light":
            self.eclipse_phase = "dark"
            self.eclipse_light_bonus = 0
            FloatingText(self.rect.centerx, self.rect.top - 20, "🌑暗影形态", (80, 50, 120))
        else:
            self.eclipse_phase = "light"
            FloatingText(self.rect.centerx, self.rect.top - 20, "☀️光耀形态", (255, 220, 100))
        for _ in range(6):
            Particle(self.rect.center, (100, 50, 180) if self.eclipse_phase == "dark" else (255, 200, 100))

    def gain_eclipse_shield(self, amount):
        """暗影形态下吸收伤害转化为护盾"""
        if self.plane_id != "eclipse" or self.eclipse_phase != "dark":
            return
        old_shield = self.eclipse_shield
        self.eclipse_shield = min(self.max_eclipse_shield, self.eclipse_shield + amount)
        if self.eclipse_shield > old_shield:
            Particle(self.rect.center, (100, 50, 180))

    def _update_eclipse_state(self):
        """每帧更新日食幽灵状态"""
        if self.plane_id != "eclipse":
            return
        # 自动切换形态计时器
        self.eclipse_phase_timer += 1
        if self.eclipse_phase_timer >= 300:  # 每5秒自动切换
            self.eclipse_phase_timer = 0
            self.toggle_eclipse_phase()
        # 光态：持续时间越长伤害越高
        if self.eclipse_phase == "light":
            phase_progress = self.eclipse_phase_timer / 300
            self.eclipse_light_bonus = phase_progress * 0.5  # 最高+50%伤害
            # 光态时护盾缓慢衰减
            if self.eclipse_shield > 0:
                self.eclipse_shield = max(0, self.eclipse_shield - 0.1)
            # 光态粒子
            if random.random() < 0.1:
                Particle(self.rect.center, (255, 220, 100))
        else:
            # 暗态：护盾不衰减，可以积累
            # 暗态粒子
            if random.random() < 0.08:
                Particle(self.rect.center, (80, 40, 120))

    def apply_prism_hit(self, enemy, bullet, hit_pos):
        """棱镜分光固有：子弹命中后折射到附近敌人"""
        if self.plane_id != "prism" or enemy is None:
            return
        # 获取子弹的折射次数
        refract_count = getattr(bullet, 'refract_count', 0)
        if refract_count >= 5:  # 最多折射5次
            return
        # 更新折射链计数
        self.prism_chain_count = refract_count + 1
        if self.prism_chain_count > self.prism_max_chain:
            self.prism_max_chain = self.prism_chain_count
        # 折射伤害加成: 每次折射+15%
        self.prism_chain_damage = self.prism_chain_count * 0.15
        # 寻找附近可折射的敌人
        refract_range = 150
        candidates = []
        for m in mobs:
            if m != enemy and m.hp > 0:
                dist = math.hypot(m.rect.centerx - hit_pos[0], m.rect.centery - hit_pos[1])
                if dist <= refract_range:
                    candidates.append((m, dist))
        if candidates:
            # 折射到最近的敌人
            candidates.sort(key=lambda x: x[1])
            target = candidates[0][0]
            # 创建折射子弹
            angle = math.degrees(math.atan2(target.rect.centery - hit_pos[1], 
                                           target.rect.centerx - hit_pos[0])) - 90
            # 折射子弹颜色随次数变化
            colors = [(100, 180, 255), (180, 100, 255), (255, 100, 180), (255, 180, 100), (100, 255, 180)]
            ref_color = colors[min(refract_count, len(colors)-1)]
            ref_bullet = Bullet(hit_pos[0], hit_pos[1], angle=angle, color=ref_color,
                               b_type="refract", piercing=0, homing=0, bullet_theme=self.bullet_theme)
            ref_bullet.refract_count = refract_count + 1
            ref_bullet.is_refracted = True
            ref_bullet.damage_mult = 1 + self.prism_chain_damage  # 折射伤害加成
            # 折射视觉 - 光线连接
            Particle(hit_pos, ref_color)
            # 完美折射链(5次)触发棱镜爆发
            if refract_count + 1 >= 5:
                FloatingText(hit_pos[0], hit_pos[1] - 25, "*棱镜爆发*", (200, 255, 255))
                # 对范围内敌人造成爆发伤害
                burst_damage = self.damage * 2.5
                for m in mobs:
                    dist = math.hypot(m.rect.centerx - hit_pos[0], m.rect.centery - hit_pos[1])
                    if dist <= 120:
                        m.hp -= burst_damage
                        FloatingText(m.rect.centerx, m.rect.top - 10, f"-{int(burst_damage)}", (150, 255, 255))
                        Particle(m.rect.center, (200, 255, 255))
                for _ in range(8):
                    Particle(hit_pos, random.choice(colors))

    def _update_prism_state(self):
        """每帧更新棱镜分光状态"""
        if self.plane_id != "prism":
            return
        # 折射链计数缓慢衰减
        if self.prism_chain_count > 0:
            if not hasattr(self, '_chain_decay_timer'):
                self._chain_decay_timer = 0
            self._chain_decay_timer += 1
            if self._chain_decay_timer >= 60:  # 1秒后重置
                self._chain_decay_timer = 0
                self.prism_chain_count = 0
                self.prism_chain_damage = 0
        # 折射粒子效果
        if self.prism_chain_count > 0 and random.random() < 0.1:
            colors = [(100, 180, 255), (180, 100, 255), (255, 100, 180)]
            Particle(self.rect.center, random.choice(colors))

    def gain_necro_soul(self, enemy_pos):
        """死灵骑士击杀时召唤亡灵"""
        if self.plane_id != "necro":
            return
        if len(self.necro_ghosts) < self.max_necro_ghosts:
            # 创建亡灵数据
            ghost = {
                'x': enemy_pos[0],
                'y': enemy_pos[1],
                'target': None,
                'attack_cd': 0,
                'lifetime': 600,  # 10秒存活
                'damage': self.damage * 0.4,  # 40%基础伤害
            }
            self.necro_ghosts.append(ghost)
            FloatingText(enemy_pos[0], enemy_pos[1] - 20, "+亡灵", (200, 50, 150))
            for _ in range(4):
                Particle(enemy_pos, (150, 50, 100))

    def _update_necro_state(self):
        """每帧更新死灵骑士状态 - 亡灵AI"""
        if self.plane_id != "necro":
            return
        ghosts_to_remove = []
        for ghost in self.necro_ghosts:
            # 生命周期
            ghost['lifetime'] -= 1
            if ghost['lifetime'] <= 0:
                ghosts_to_remove.append(ghost)
                continue
            # 寻找目标
            if ghost['target'] is None or ghost['target'] not in mobs or ghost['target'].hp <= 0:
                # 找最近的敌人
                min_dist = 300
                ghost['target'] = None
                for m in mobs:
                    dist = math.hypot(m.rect.centerx - ghost['x'], m.rect.centery - ghost['y'])
                    if dist < min_dist:
                        min_dist = dist
                        ghost['target'] = m
            # 移动向目标
            if ghost['target']:
                target = ghost['target']
                dx = target.rect.centerx - ghost['x']
                dy = target.rect.centery - ghost['y']
                dist = math.hypot(dx, dy)
                if dist > 30:
                    speed = 3.5
                    ghost['x'] += (dx / dist) * speed
                    ghost['y'] += (dy / dist) * speed
                # 攻击
                ghost['attack_cd'] -= 1
                if ghost['attack_cd'] <= 0 and dist < 50:
                    ghost['attack_cd'] = 45  # 0.75秒攻击间隔
                    target.hp -= ghost['damage']
                    self.necro_ghost_damage += ghost['damage']
                    FloatingText(target.rect.centerx, target.rect.top - 8, 
                               f"-{int(ghost['damage'])}", (180, 80, 130))
                    Particle((int(ghost['x']), int(ghost['y'])), (200, 50, 150))
            else:
                # 没有目标时围绕玩家
                angle = math.atan2(self.rect.centery - ghost['y'], self.rect.centerx - ghost['x'])
                target_x = self.rect.centerx + math.cos(angle + len(self.necro_ghosts) * 0.5) * 60
                target_y = self.rect.centery + math.sin(angle + len(self.necro_ghosts) * 0.5) * 60
                ghost['x'] += (target_x - ghost['x']) * 0.05
                ghost['y'] += (target_y - ghost['y']) * 0.05
            # 亡灵粒子效果
            if random.random() < 0.08:
                Particle((int(ghost['x']), int(ghost['y'])), (150, 50, 100))
        # 移除过期亡灵
        for ghost in ghosts_to_remove:
            self.necro_ghosts.remove(ghost)
            Particle((int(ghost['x']), int(ghost['y'])), (100, 30, 60))

    # ========== 霓虹突击者 - 超载引擎 ==========
    def gain_striker_charge(self, amount):
        """霓虹突击者命中时积累超载"""
        if self.plane_id != "striker":
            return
        if self.striker_overdrive:
            return  # 超载中不积累
        self.striker_charge = min(self.max_striker_charge, self.striker_charge + amount)
        self.striker_idle_timer = self.striker_decay_delay
        if self.striker_charge >= self.max_striker_charge:
            self.striker_overdrive = True
            self.striker_overdrive_timer = 300  # 5秒超载
            self.striker_charge = self.max_striker_charge
            FloatingText(self.rect.centerx, self.rect.top - 20, "超载启动!", CYAN)
            for _ in range(8):
                Particle(self.rect.center, CYAN)

    def _update_striker_state(self):
        """每帧更新霓虹突击者状态"""
        if self.plane_id != "striker":
            return
        if self.striker_overdrive:
            self.striker_overdrive_timer -= 1
            if self.striker_overdrive_timer <= 0:
                self.striker_overdrive = False
                self.striker_charge = 0
                FloatingText(self.rect.centerx, self.rect.top - 20, "超载结束", (100, 150, 150))
            elif random.random() < 0.15:
                Particle(self.rect.center, CYAN)
        else:
            if self.striker_charge > 0:
                if self.striker_idle_timer > 0:
                    self.striker_idle_timer -= 1
                else:
                    self.striker_charge = max(0, self.striker_charge - self.striker_decay_rate)
                    if self.striker_charge == 0:
                        FloatingText(self.rect.centerx, self.rect.top - 15, "能量耗散", (80, 160, 160))

    # ========== 虚空幻影 - 相位漂移 ==========
    def gain_phantom_phase(self, amount):
        """虚空幻影移动时积累相位"""
        if self.plane_id != "phantom":
            return
        if self.phantom_intangible:
            return
        self.phantom_phase = min(self.max_phantom_phase, self.phantom_phase + amount)
        # 自动触发：能量满自动进入相位无敌
        if self.phantom_phase >= self.max_phantom_phase:
            self.activate_phantom_intangible()

    def activate_phantom_intangible(self):
        """激活相位无敌"""
        if self.plane_id != "phantom" or self.phantom_phase < 50:
            return False
        self.phantom_intangible = True
        self.phantom_intangible_timer = 45  # 0.75秒无敌
        self.phantom_phase = 0
        FloatingText(self.rect.centerx, self.rect.top - 20, "相位!", MAGENTA)
        for _ in range(6):
            Particle(self.rect.center, MAGENTA)
        return True

    def _update_phantom_state(self):
        """每帧更新虚空幻影状态"""
        if self.plane_id != "phantom":
            return
        if self.phantom_intangible:
            self.phantom_intangible_timer -= 1
            if self.phantom_intangible_timer <= 0:
                self.phantom_intangible = False
            elif random.random() < 0.2:
                Particle(self.rect.center, (200, 100, 255))
        else:
            # 不再被动衰减，改为仅在命中或移动时蓄能
            if self.phantom_phase >= self.max_phantom_phase:
                self.activate_phantom_intangible()

    # ========== 雷霆战鹰 - 雷暴连锁 ==========
    def gain_thunder_charge(self, amount):
        """雷霆战鹰命中时积累电荷"""
        if self.plane_id != "thunderbird":
            return
        self.thunder_charge = min(self.max_thunder_charge, self.thunder_charge + amount)
        self.thunder_idle_timer = self.thunder_decay_delay

    def trigger_chain_lightning(self, hit_pos):
        """触发连锁闪电"""
        if self.plane_id != "thunderbird" or self.thunder_charge < self.max_thunder_charge:
            return []
        self.thunder_charge = 0
        lightning_paths = []
        base_color = (120, 200, 255)
        FloatingText(hit_pos[0], hit_pos[1] - 20, "雷暴!", base_color)
        # 选择最近的最多5个目标，逐个连锁
        candidates = []
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - hit_pos[0], enemy.rect.centery - hit_pos[1])
            if dist <= 240:
                candidates.append((dist, enemy))
        candidates.sort(key=lambda item: item[0])
        targets = [enemy for _, enemy in candidates[:5]]
        last_point = hit_pos
        damage = self.damage * 1.8
        for idx, enemy in enumerate(targets):
            enemy.hp -= damage
            FloatingText(enemy.rect.centerx, enemy.rect.top - 12, f"-{int(damage)}", base_color)
            Particle(enemy.rect.center, base_color)
            lightning_paths.append((last_point, enemy.rect.center))
            last_point = enemy.rect.center
            damage *= 0.85  # 每次连锁衰减
        # 中心闪电粒子
        for _ in range(14):
            Particle(hit_pos, base_color)
        return lightning_paths

    def _update_thunder_state(self):
        """每帧更新雷霆战鹰状态"""
        if self.plane_id != "thunderbird":
            return
        # 高电荷粒子
        if self.thunder_charge > 70 and random.random() < 0.12:
            Particle(self.rect.center, YELLOW)
        # 衰减机制：离战斗太久会流失
        if self.thunder_charge > 0:
            if self.thunder_idle_timer > 0:
                self.thunder_idle_timer -= 1
            else:
                self.thunder_charge = max(0, self.thunder_charge - self.thunder_decay_rate)

    # ========== 剧毒蝰蛇 - 剧毒累积 ==========
    def apply_viper_poison(self, enemy, damage):
        """蝰蛇命中时施加毒素"""
        if self.plane_id != "viper" or enemy is None:
            return
        enemy_id = id(enemy)
        if enemy_id not in self.viper_venom_stacks:
            self.viper_venom_stacks[enemy_id] = 0
        self.viper_venom_stacks[enemy_id] = min(10, self.viper_venom_stacks[enemy_id] + 1)
        # 标记敌人
        if not hasattr(enemy, 'viper_poison'):
            enemy.viper_poison = 0
        enemy.viper_poison = self.viper_venom_stacks[enemy_id]
        enemy.viper_poison_timer = 180  # 3秒持续
        enemy.viper_poison_dmg = damage * 0.1  # 每层10%伤害/秒

    def _update_viper_state(self):
        """每帧更新蝰蛇状态"""
        if self.plane_id != "viper":
            return
        # 计算总中毒层数
        self.viper_total_poison = 0
        alive_ids = set()
        for m in mobs:
            alive_ids.add(id(m))
            if hasattr(m, 'viper_poison') and m.viper_poison > 0:
                self.viper_total_poison += m.viper_poison
                # 持续毒伤
                if hasattr(m, 'viper_poison_timer'):
                    m.viper_poison_timer -= 1
                    if m.viper_poison_timer <= 0:
                        m.viper_poison = 0
                    elif random.random() < 0.1:
                        poison_dmg = getattr(m, 'viper_poison_dmg', 1) * m.viper_poison
                        m.hp -= poison_dmg
                        if random.random() < 0.3:
                            FloatingText(m.rect.centerx, m.rect.top - 8, f"-{int(poison_dmg)}", LIME)
                        Particle(m.rect.center, LIME)
        # 清理死亡敌人
        self.viper_venom_stacks = {k: v for k, v in self.viper_venom_stacks.items() if k in alive_ids}

    # ========== 幽灵收割者 - 死神印记 ==========
    def update_specter_focus(self, target):
        """更新幽灵收割者的瞄准目标"""
        if self.plane_id != "specter":
            return
        if target == self.specter_focus:
            self.specter_focus_time = min(180, self.specter_focus_time + 0.6)  # 更慢充能
            if self.specter_focus_time >= 180:
                self.specter_focus_ready = True
            self.specter_focus_decay_timer = self.specter_focus_decay_delay
        else:
            self.specter_focus = target
            self.specter_focus_time = 0
            self.specter_focus_ready = False
            self.specter_focus_decay_timer = self.specter_focus_decay_delay

    def get_specter_damage_mult(self, target):
        """获取幽灵收割者对目标的伤害倍率"""
        if self.plane_id != "specter":
            return 1.0
        if target == self.specter_focus and self.specter_focus_time > 0:
            base_mult = 1.0 + (self.specter_focus_time / 180) * 1.0  # 最高+100%
            if self.specter_focus_ready:
                base_mult += 0.5  # 满印记再+50%
                self.specter_focus_ready = False  # 触发一次后重置
            return base_mult
        return 1.0

    def trigger_specter_stealth(self):
        """击杀后触发隐身"""
        if self.plane_id != "specter":
            return
        self.specter_stealth = 90  # 1.5秒隐身
        FloatingText(self.rect.centerx, self.rect.top - 15, "隐身", (150, 100, 255))

    def _update_specter_state(self):
        """每帧更新幽灵收割者状态"""
        if self.plane_id != "specter":
            return
        # 隐身衰减
        if self.specter_stealth > 0:
            self.specter_stealth -= 1
            if random.random() < 0.1:
                Particle(self.rect.center, (150, 100, 255))
        # 焦点能量衰减：长时间未命中会慢慢流失
        if self.specter_focus_time > 0:
            if self.specter_focus_decay_timer > 0:
                self.specter_focus_decay_timer -= 1
            else:
                decay_step = self.specter_focus_decay_rate
                if self.specter_focus is None or self.specter_focus not in mobs:
                    decay_step *= 1.5
                self.specter_focus_time = max(0, self.specter_focus_time - decay_step)
                if self.specter_focus_time == 0:
                    self.specter_focus_ready = False
                    self.specter_focus_decay_timer = 0
        # 目标消失时保留蓄力，等待新目标
        if self.specter_focus is None or self.specter_focus not in mobs:
            self.specter_focus = None

    # ========== 极光女神 - 极光共鸣 ==========
    def spawn_aurora_orb(self, pos):
        """极光女神命中时生成极光球"""
        if self.plane_id != "aurora":
            return
        if len(self.aurora_orbs) >= self.max_aurora_orbs:
            return
        if random.random() > 0.25:  # 25%几率生成
            return
        orb = {
            'x': pos[0],
            'y': pos[1],
            'target': None,
            'attack_cd': 0,
            'lifetime': 300,  # 5秒存活
            'damage': self.damage * 0.3,
        }
        self.aurora_orbs.append(orb)
        for _ in range(3):
            Particle(pos, TEAL)
        # 达到上限时自动引爆所有极光球
        if len(self.aurora_orbs) >= self.max_aurora_orbs:
            self._trigger_aurora_nova()

    def _update_aurora_state(self):
        """每帧更新极光女神状态"""
        if self.plane_id != "aurora":
            return
        orbs_to_remove = []
        for orb in self.aurora_orbs:
            orb['lifetime'] -= 1
            if orb['lifetime'] <= 0:
                orbs_to_remove.append(orb)
                continue
            # 寻找目标
            if orb['target'] is None or orb['target'] not in mobs or orb['target'].hp <= 0:
                min_dist = 200
                orb['target'] = None
                for m in mobs:
                    dist = math.hypot(m.rect.centerx - orb['x'], m.rect.centery - orb['y'])
                    if dist < min_dist:
                        min_dist = dist
                        orb['target'] = m
            # 攻击
            if orb['target']:
                target = orb['target']
                orb['attack_cd'] -= 1
                if orb['attack_cd'] <= 0:
                    orb['attack_cd'] = 30  # 0.5秒攻击间隔
                    target.hp -= orb['damage']
                    self.aurora_orb_damage += orb['damage']
                    Particle((int(orb['x']), int(orb['y'])), TEAL)
                    Particle(target.rect.center, (100, 255, 200))
            # 围绕玩家缓慢移动
            angle = math.atan2(self.rect.centery - orb['y'], self.rect.centerx - orb['x'])
            idx = self.aurora_orbs.index(orb)
            target_angle = angle + idx * (math.pi * 2 / max(1, len(self.aurora_orbs)))
            target_x = self.rect.centerx + math.cos(target_angle) * 70
            target_y = self.rect.centery + math.sin(target_angle) * 70
            orb['x'] += (target_x - orb['x']) * 0.08
            orb['y'] += (target_y - orb['y']) * 0.08
            # 粒子效果
            if random.random() < 0.1:
                Particle((int(orb['x']), int(orb['y'])), (0, 200, 180))
        for orb in orbs_to_remove:
            self.aurora_orbs.remove(orb)

        # 被动光环：多球时给予轻微攻速移速加成（非持久，随球数量刷新）
        orb_count = len(self.aurora_orbs)
        if orb_count >= 3:
            bonus_ratio = 0.1 if orb_count == 3 else (0.2 if orb_count == 4 else 0.35)
            self.shoot_delay = max(5, int(self.plane_data["delay"] * (1 - bonus_ratio)))
            self.speed = self.plane_data.get("speed", self.speed) * (1 + bonus_ratio)
        else:
            # 恢复基础数值
            self.shoot_delay = self.plane_data["delay"]
            self.speed = self.plane_data.get("speed", self.speed)

    def _trigger_aurora_nova(self):
        """引爆所有极光球造成范围伤害"""
        if self.plane_id != "aurora" or not self.aurora_orbs:
            return
        center = self.rect.center
        orb_count = len(self.aurora_orbs)
        nova_damage = self.damage * 0.6 * orb_count
        radius = 180
        for enemy in list(mobs):
            dist = math.hypot(enemy.rect.centerx - center[0], enemy.rect.centery - center[1])
            if dist <= radius:
                enemy.hp -= nova_damage
                Particle(enemy.rect.center, TEAL)
                FloatingText(enemy.rect.centerx, enemy.rect.top - 12, f"-{int(nova_damage)}", (100, 255, 200))
        for _ in range(8):
            Particle(center, TEAL)
        self.aurora_orbs.clear()

    def _update_crimson_state(self):
        if self.plane_id != "crimson":
            return
        if self.blood_stacks <= 0:
            self.blood_grace_timer = 0
            self._blood_decay_tick = 0
            return
        if self.blood_grace_timer > 0:
            self.blood_grace_timer -= 1
        else:
            self._blood_decay_tick += 1
            if self._blood_decay_tick >= 30:
                self._blood_decay_tick = 0
                self.blood_stacks = max(0, self.blood_stacks - 1)
        # 小幅血光粒子
        if random.random() < min(0.25, 0.08 + self.blood_stacks / (self.max_blood_stacks * 2)):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(10, 24)
            px = self.rect.centerx + math.cos(angle) * dist
            py = self.rect.centery + math.sin(angle) * dist
            Particle((int(px), int(py)), CRIMSON)

    def use_secondary_ultimate(self):
        """第二大招（G键释放）"""
        # 冷却检查
        if self.ult2_cooldown > 0:
            return  # 冷却中，无法释放
        
        if self.ult2_charge >= 100:
            self.ult2_charge -= 100
            # 设置冷却计时
            self.ult2_cooldown = self.ult2_max_cooldown
            
            # 获取第二大招名称
            ult2_names = {
                "striker": "欧米伽激光",
                "phantom": "分身乱舞",
                "titan": "陨石轰炸",
                "thunderbird": "连锁闪电",
                "viper": "酸雨倾盆",
                "specter": "亡魂哀嚎",
                "aurora": "极光冲击波",
                "crimson": "刀刃风暴",
                "stalker": "引力陷阱",
                "gaia": "岩石护盾",
                "weaver": "蛛网陷阱",
                "solar": "太阳耀斑",
                "arbiter": "数据腐蚀",
                "eclipse": "暗物质爆发",
                "prism": "彩虹碎裂",
                "necro": "生命汲取",
                "void": "虚空撕裂"
            }
            
            pid = self.plane_id
            name = ult2_names.get(pid, "次级大招")
            
            FloatingText(self.rect.centerx, self.rect.top - 50, f"◆ {name} ◆", self.plane_data["color"])
            sound_mgr.play("nuke")
            
            # 根据机体ID释放不同的第二大招
            if pid == "striker":
                # 欧米伽激光：三道交叉激光扫射
                OmegaLaser(self)
            
            elif pid == "phantom":
                # 分身乱舞：生成多个攻击分身
                PhantomClone(self)
            
            elif pid == "titan":
                # 陨石轰炸：召唤陨石群
                MeteorStrike(self)
            
            elif pid == "thunderbird":
                # 连锁闪电：闪电在敌人间跳跃
                ChainLightning(self)
            
            elif pid == "viper":
                # 酸雨倾盆：全屏毒液雨
                AcidRain(self)
            
            elif pid == "specter":
                # 亡魂哀嚎：释放尖啸灵魂波
                GhostWail(self)
            
            elif pid == "aurora":
                # 极光冲击波：全屏极光爆发
                AuroraWave(self)
            
            elif pid == "crimson":
                # 刀刃风暴：环绕飞刃护盾
                BladeStorm(self)
            
            elif pid == "stalker":
                # 引力陷阱：创建吸引力场
                GravityWell(self)
            
            elif pid == "gaia":
                # 岩石护盾：召唤岩石防御
                EarthShield(self)
            
            elif pid == "weaver":
                # 蛛网陷阱：放置多个减速网
                WebTrap(self)
            
            elif pid == "solar":
                # 太阳耀斑：持续燃烧光柱
                SolarFlare(self)
            
            elif pid == "arbiter":
                # 数据腐蚀：病毒式扩散攻击
                DataCorruption(self)
            
            elif pid == "eclipse":
                # 暗物质爆发：释放暗能量波
                DarkMatter(self)
            
            elif pid == "prism":
                # 彩虹碎裂：爆炸式光谱分裂
                RainbowShatter(self)
            
            elif pid == "necro":
                # 生命汲取：持续吸取生命
                LifeDrain(self)
            
            elif pid == "void":
                # 虚空撕裂（与主大招相同但稍弱）
                VoidRift(self.rect.center)
            
            else:
                # 通用：清弹
                enemy_bullets.empty()
                for _ in range(8):
                    Particle(self.rect.center, self.plane_data["color"], mode='shockwave')

    def use_tertiary_ultimate(self):
        """第三大招（C键释放）"""
        # 冷却检查
        if self.ult3_cooldown > 0:
            return  # 冷却中，无法释放
        
        if self.ult3_charge >= 100:
            self.ult3_charge -= 100
            # 设置冷却计时
            self.ult3_cooldown = self.ult3_max_cooldown
            
            # 获取第三大招名称
            ult3_names = {
                "striker": "等离子漩涡",
                "phantom": "镜像分裂",
                "titan": "地震冲击",
                "thunderbird": "球状闪电",
                "viper": "腐蚀云雾",
                "specter": "灵魂风暴",
                "aurora": "北极光",
                "crimson": "刀刃旋风",
                "stalker": "重力炸弹",
                "gaia": "水晶屏障",
                "weaver": "蜘蛛群袭",
                "solar": "太阳光束",
                "arbiter": "病毒感染",
                "eclipse": "虚空坍缩",
                "prism": "光之棱镜",
                "necro": "灵魂收割",
                "void": "等离子漩涡"
            }
            
            pid = self.plane_id
            name = ult3_names.get(pid, "终极大招")
            
            FloatingText(self.rect.centerx, self.rect.top - 50, f"★ {name} ★", self.plane_data["color"])
            sound_mgr.play("nuke")
            
            # 根据机体ID释放不同的第三大招
            if pid == "striker":
                # 等离子漩涡：吸引敌人并爆炸
                PlasmaVortex(self)
            
            elif pid == "phantom":
                # 镜像分裂：创建攻击镜像
                MirrorImage(self)
            
            elif pid == "titan":
                # 地震冲击：制造地震波
                SeismicSlam(self)
            
            elif pid == "thunderbird":
                # 球状闪电：追踪电球
                BallLightning(self)
            
            elif pid == "viper":
                # 腐蚀云雾：扩散毒云
                CorrosiveCloud(self)
            
            elif pid == "specter":
                # 灵魂风暴：召唤灵魂漩涡
                SoulStorm(self)
            
            elif pid == "aurora":
                # 北极光：治疗和伤害的极光波
                NorthernLights(self)
            
            elif pid == "crimson":
                # 刀刃旋风：旋转刀刃风暴
                BladeWhirlwind(self)
            
            elif pid == "stalker":
                # 重力炸弹：黑洞炸弹
                GravityBomb(self)
            
            elif pid == "gaia":
                # 水晶屏障：反弹护盾
                CrystalBarrier(self)
            
            elif pid == "weaver":
                # 蜘蛛群袭：召唤蜘蛛大军
                SpiderSwarm(self)
            
            elif pid == "solar":
                # 太阳光束：蓄力毁灭光束
                SolarBeam(self)
            
            elif pid == "arbiter":
                # 病毒感染：传染性病毒
                VirusInfection(self)
            
            elif pid == "eclipse":
                # 虚空坍缩：虚空裂隙
                VoidCollapse(self)
            
            elif pid == "prism":
                # 光之棱镜：彩虹光线
                LightPrism(self)
            
            elif pid == "necro":
                # 灵魂收割：死神镰刀
                SoulReap(self)
            
            elif pid == "void":
                # 虚空类也用等离子漩涡
                PlasmaVortex(self)
            
            else:
                # 通用：全屏伤害
                for m in list(mobs):
                    m.hp -= 100
                    Particle(m.rect.center, self.plane_data["color"], mode='shockwave')

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
            from roguelite import UpgradeManager, ExperienceSystem, ItemManager, AchievementManager, CardEffectProcessor
            from systems import EffectManager
            
            self.upgrade_manager = UpgradeManager()
            self.exp_system = ExperienceSystem(self)
            self.item_manager = ItemManager()
            self.achievement_manager = AchievementManager()
            self.effect_manager = EffectManager()
            self.card_effect_processor = CardEffectProcessor(self)  # 卡牌效果处理器
            
            # 同步经验系统的初始值到Player属性
            if self.exp_system:
                self.xp = self.exp_system.xp_collected
                self.next_level_xp = self.exp_system.next_level_xp
                self.level = self.exp_system.level
        except Exception as e:
            log_error(f"Failed to initialize roguelite systems: {e}")
            import traceback
            traceback.print_exc()
            # In case of error, still try to recover gracefully
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
        """击杀敌人时触发肉鸽效果（吸血、裂变等）"""
        # 优先使用卡牌效果处理器
        if hasattr(self, 'card_effect_processor') and self.card_effect_processor:
            corpse_effect = self.card_effect_processor.on_kill_enemy(enemy)
            if corpse_effect and corpse_effect.get("type") == "corpse_explosion":
                return corpse_effect
        # 备用：使用buff处理器
        elif self.buff_processor:
            corpse_effect = self.buff_processor.on_kill_enemy(enemy)
            if corpse_effect and corpse_effect.get("type") == "corpse_explosion":
                return corpse_effect
        return None
    
    def on_buff_received(self, buff_id, buff_data):
        """接收增益时的钩子（可用于显示通知）"""
        color = RARITY_COLORS[buff_data["rarity"]]
        FloatingText(self.rect.centerx, self.rect.top - 30, f"✦ {buff_data['name']}", color)